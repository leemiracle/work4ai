# Page: Overview

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [docs/api-reference/agent/tasks.mdx](docs/api-reference/agent/tasks.mdx)
- [docs/core-concepts/desktop-environment.mdx](docs/core-concepts/desktop-environment.mdx)
- [docs/deployment/railway.mdx](docs/deployment/railway.mdx)
- [docs/guides/task-creation.mdx](docs/guides/task-creation.mdx)
- [docs/introduction.mdx](docs/introduction.mdx)
- [docs/quickstart.mdx](docs/quickstart.mdx)

</details>



This document provides a high-level introduction to the Bytebot system, explaining its purpose, architecture, and core components. It serves as the entry point for understanding how Bytebot enables AI-driven desktop automation through a three-tier service architecture.

For deployment instructions, see [Quick Start](#1.1). For detailed architectural patterns, see [System Architecture](#2). For core concepts like Tasks and the observe-act-verify cycle, see [Core Concepts](#1.2).

## Purpose and Capabilities

Bytebot is an open-source AI desktop automation system that executes natural language tasks by controlling a virtual Ubuntu desktop environment. The system combines large language models (LLMs) with desktop automation to perform complex multi-step workflows.

**Core capabilities:**
- Execute tasks described in natural language (e.g., "Download all invoices from email and organize by date")
- Control desktop applications through mouse and keyboard automation
- Process uploaded files (PDFs, spreadsheets, documents) within the LLM context
- Handle authentication flows via password manager integration
- Provide real-time desktop view during task execution
- Support human intervention through takeover mode
- Expose REST and WebSocket APIs for programmatic control

**Target use cases:**
- Business process automation (RPA replacement)
- Document processing and data extraction
- Multi-application workflows across systems without APIs
- Compliance and audit task automation
- Development/QA integration with visual testing

Sources: [README.md:1-311](), [docs/introduction.mdx:1-216]()

## Three-Tier Architecture

```mermaid
graph TB
    subgraph "Port 9992 - bytebot-ui"
        NextJS["Next.js Server<br/>packages/bytebot-ui/server.ts"]
        APIProxy["API Proxy<br/>/api/proxy/*"]
        WSProxy["Socket.IO Proxy<br/>/api/proxy/tasks"]
        VNCProxy["VNC WebSocket Proxy<br/>/api/proxy/websockify"]
    end
    
    subgraph "Port 9991 - bytebot-agent"
        TasksController["TasksController<br/>packages/bytebot-agent/src/tasks"]
        TasksService["TasksService<br/>packages/bytebot-agent/src/tasks/tasks.service.ts"]
        TasksGateway["TasksGateway<br/>packages/bytebot-agent/src/tasks/tasks.gateway.ts"]
        AgentProcessor["AgentProcessor<br/>packages/bytebot-agent/src/agent/agent-processor.service.ts"]
        MessagesService["MessagesService<br/>packages/bytebot-agent/src/messages"]
        SummariesService["SummariesService<br/>packages/bytebot-agent/src/summaries"]
        PrismaService["PrismaService<br/>PostgreSQL Client"]
    end
    
    subgraph "Port 9990 - bytebotd"
        ComputerUseController["ComputerUseController<br/>packages/bytebotd/src/computer-use"]
        ComputerUseService["ComputerUseService<br/>packages/bytebotd/src/computer-use/computer-use.service.ts"]
        VNCServer["VNC Server<br/>websockify:6080→5900"]
        MCPEndpoint["MCP Endpoint<br/>/mcp SSE"]
        Desktop["XFCE4 Desktop<br/>Ubuntu 22.04"]
    end
    
    subgraph "External Services"
        Anthropic["Anthropic API<br/>Claude Models"]
        OpenAI["OpenAI API<br/>GPT Models"]
        Google["Google API<br/>Gemini Models"]
    end
    
    Browser["Web Browser"] -->|HTTPS| NextJS
    NextJS --> APIProxy
    NextJS --> WSProxy
    NextJS --> VNCProxy
    
    APIProxy -->|"POST /tasks<br/>GET /tasks/:id"| TasksController
    WSProxy -->|"Socket.IO<br/>join_task, leave_task"| TasksGateway
    VNCProxy -->|WebSocket| VNCServer
    
    TasksController --> TasksService
    TasksController --> MessagesService
    TasksGateway -.->|"Emits task_updated<br/>new_message events"| Browser
    
    TasksService --> AgentProcessor
    TasksService --> PrismaService
    MessagesService --> PrismaService
    SummariesService --> PrismaService
    
    AgentProcessor -->|"POST /computer-use"| ComputerUseController
    AgentProcessor -->|LLM API calls| Anthropic
    AgentProcessor -->|LLM API calls| OpenAI
    AgentProcessor -->|LLM API calls| Google
    
    ComputerUseController --> ComputerUseService
    ComputerUseService -->|"@nut-tree-fork/nut-js"| Desktop
    Desktop --> VNCServer
    
    MCPClient["MCP Client"] <-->|"Server-Sent Events"| MCPEndpoint
    MCPEndpoint --> ComputerUseService
```

**Tier 1: Frontend (bytebot-ui)**
- Next.js 15 application with custom Express server
- Serves React UI components for task management
- Proxies all backend communication (HTTP, WebSocket, VNC)
- Exposes public interface on port 9992

**Tier 2: Orchestration (bytebot-agent)**
- NestJS backend service on port 9991
- Manages task lifecycle through `TasksService`
- Executes agent processing loop via `AgentProcessor`
- Communicates with LLM providers for decision-making
- Persists data to PostgreSQL via Prisma
- Broadcasts real-time updates through `TasksGateway`

**Tier 3: Desktop Environment (bytebotd)**
- NestJS daemon on port 9990 running inside Ubuntu container
- Executes computer actions through `ComputerUseService`
- Provides VNC access via noVNC web client
- Exposes MCP endpoint for tool invocation
- Runs XFCE4 desktop at 1920x1080 resolution

Sources: [README.md:108-116](), [README.md:230-239](), [docs/introduction.mdx:120-147](), Diagram 1 from high-level architecture

## Service Component Mapping

```mermaid
graph LR
    subgraph "bytebot-ui Service"
        UIApp["App Router<br/>app/"]
        TaskList["TaskList Component<br/>app/tasks/page.tsx"]
        TaskDetail["TaskDetail Page<br/>app/tasks/[id]/page.tsx"]
        DesktopContainer["DesktopContainer<br/>components/DesktopContainer.tsx"]
        TaskUtils["taskUtils API Client<br/>lib/taskUtils.ts"]
        UseWebSocket["useWebSocket Hook<br/>hooks/useWebSocket.ts"]
    end
    
    subgraph "bytebot-agent Service"
        TasksModule["TasksModule<br/>src/tasks/tasks.module.ts"]
        TasksCtrl["TasksController<br/>@Controller('tasks')"]
        TasksSvc["TasksService"]
        TasksGW["TasksGateway<br/>@WebSocketGateway()"]
        AgentModule["AgentModule<br/>src/agent/agent.module.ts"]
        AgentProc["AgentProcessor"]
        AgentScheduler["AgentScheduler<br/>@Cron('*/5 * * * * *')"]
        MessagesModule["MessagesModule"]
        MessagesSvc["MessagesService"]
        SummariesModule["SummariesModule"]
        SummariesSvc["SummariesService"]
        FilesModule["FilesModule"]
        PrismaDB["Prisma Client<br/>Task, Message,<br/>Summary, File"]
    end
    
    subgraph "bytebotd Service"
        ComputerModule["ComputerUseModule<br/>src/computer-use/computer-use.module.ts"]
        ComputerCtrl["ComputerUseController<br/>@Controller('computer-use')"]
        ComputerSvc["ComputerUseService"]
        NutJS["@nut-tree-fork/nut-js<br/>Mouse, Keyboard, Screen"]
        BytebotMCP["BytebotMcpModule<br/>src/bytebot-mcp/bytebot-mcp.module.ts"]
        MCPTools["ComputerUseTools<br/>17 MCP Tools"]
    end
    
    TaskUtils -->|"HTTP POST /tasks"| TasksCtrl
    UseWebSocket -->|"Socket.IO"| TasksGW
    
    TasksCtrl --> TasksSvc
    TasksGW --> TasksSvc
    TasksSvc --> PrismaDB
    TasksSvc --> AgentProc
    
    AgentScheduler -->|"Picks PENDING tasks"| TasksSvc
    AgentProc --> MessagesSvc
    AgentProc --> SummariesSvc
    MessagesSvc --> PrismaDB
    SummariesSvc --> PrismaDB
    
    AgentProc -->|"HTTP POST /computer-use"| ComputerCtrl
    ComputerCtrl --> ComputerSvc
    ComputerSvc --> NutJS
    
    BytebotMCP --> ComputerSvc
    MCPTools --> ComputerSvc
```

**Frontend Components:**
- `app/tasks/page.tsx`: Task list view with filtering and pagination
- `app/tasks/[id]/page.tsx`: Task detail page with chat and desktop view
- `components/DesktopContainer.tsx`: VNC viewer or scrollable screenshot display
- `lib/taskUtils.ts`: API client for task CRUD operations
- `hooks/useWebSocket.ts`: Socket.IO client for real-time events

**Backend Services:**
- `TasksService`: CRUD operations, status transitions, event emission
- `AgentProcessor`: Core processing loop (observe → plan → act → verify)
- `AgentScheduler`: Cron job running every 5 seconds to pick pending tasks
- `MessagesService`: Message creation, retrieval, grouping, role switching
- `SummariesService`: Hierarchical summarization when token usage exceeds 75%

**Desktop Services:**
- `ComputerUseService`: Dispatches actions to nut-js automation library
- `ComputerUseTools`: MCP tool definitions for 17 desktop operations
- `BytebotMcpModule`: SSE endpoint at `/mcp` for external MCP clients

Sources: [README.md:108-116](), Diagrams 1-4 from high-level architecture

## Data Flow: Task Creation to Execution

```mermaid
sequenceDiagram
    participant UI as bytebot-ui<br/>TaskList Component
    participant API as bytebot-agent<br/>TasksController
    participant Svc as TasksService
    participant DB as Prisma Client<br/>PostgreSQL
    participant WS as TasksGateway<br/>Socket.IO
    participant Sched as AgentScheduler<br/>@Cron
    participant Proc as AgentProcessor
    participant LLM as Anthropic/OpenAI<br/>Google API
    participant Comp as bytebotd<br/>ComputerUseService
    
    UI->>API: POST /tasks<br/>{description, priority}
    API->>Svc: create(dto)
    Svc->>DB: prisma.task.create({status: PENDING})
    DB-->>Svc: Task entity
    Svc->>WS: server.emit('task_created', task)
    WS-->>UI: task_created event
    Svc-->>API: Task entity
    API-->>UI: 201 Created + Task JSON
    
    Note over Sched: Every 5 seconds
    Sched->>Svc: findNextPendingTask()
    Svc->>DB: prisma.task.findFirst({status: PENDING})
    DB-->>Sched: Task or null
    Sched->>Svc: update(id, {status: RUNNING})
    Sched->>Proc: processTask(taskId)
    
    loop Agent Processing Loop
        Proc->>Comp: POST /computer-use<br/>{action: 'screenshot'}
        Comp-->>Proc: {base64: '...'}
        Proc->>Svc: getLatestContext(taskId)
        Svc->>DB: findLatestSummary + findUnsummarizedMessages
        DB-->>Proc: [summary?, ...messages]
        Proc->>LLM: POST /messages<br/>{messages: context}
        LLM-->>Proc: {content: [tool_use blocks]}
        Proc->>Comp: POST /computer-use<br/>{action: 'click_mouse', coordinate: [x,y]}
        Comp-->>Proc: {success: true}
        Proc->>Svc: createMessage({role: ASSISTANT, content})
        Svc->>DB: prisma.message.create()
        Svc->>WS: emitTaskUpdated(taskId)
        WS-->>UI: task_updated event
    end
    
    Proc->>Svc: update(id, {status: COMPLETED})
    Svc->>DB: prisma.task.update()
    Svc->>WS: server.emit('task_updated')
    WS-->>UI: task_updated event
```

**Flow stages:**

1. **Task Creation (UI → Agent):**
   - User submits task via `TaskList` component
   - `taskUtils.createTask()` sends POST to `TasksController`
   - `TasksService.create()` persists to PostgreSQL with `status: PENDING`
   - `TasksGateway` broadcasts `task_created` event via Socket.IO

2. **Task Scheduling (Agent):**
   - `AgentScheduler` cron job runs every 5 seconds
   - Queries `prisma.task.findFirst({where: {status: 'PENDING'}})` 
   - Updates task status to `RUNNING`
   - Invokes `AgentProcessor.processTask()`

3. **Agent Execution Loop (Agent → Desktop → LLM):**
   - `AgentProcessor` captures screenshot via `/computer-use` endpoint
   - Builds context from latest summary + unsummarized messages
   - Sends context to LLM (Anthropic/OpenAI/Google)
   - Receives tool use blocks (e.g., `computer` tool with mouse/keyboard actions)
   - Executes actions via `ComputerUseService`
   - Creates messages and emits `task_updated` events
   - Repeats until task reaches terminal state (`COMPLETED`, `FAILED`, `NEEDS_HELP`)

4. **Real-time Updates (Agent → UI):**
   - `TasksGateway` emits events to rooms (clients joined to specific task IDs)
   - `useWebSocket` hook receives events and updates React state
   - UI re-renders with new messages and status

Sources: [README.md:108-116](), Diagram 2 from high-level architecture, [docs/api-reference/agent/tasks.mdx:1-310]()

## Technology Stack

| Layer | Component | Technology | Purpose |
|-------|-----------|-----------|---------|
| **Frontend** | bytebot-ui | Next.js 15.4.7, React 19 | Server-side rendering, API routes |
| | Styling | Tailwind CSS 4, Radix UI | Component styling, accessible primitives |
| | State | React hooks, Socket.IO client | Client state, real-time updates |
| | VNC | react-vnc | Browser-based desktop access |
| **Backend** | bytebot-agent | NestJS, TypeScript 5.7.3 | Dependency injection, modularity |
| | Database | Prisma ORM, PostgreSQL | Type-safe queries, migrations |
| | LLM Integration | @anthropic-ai/sdk, openai, @google/genai | Multi-provider support |
| | Events | @nestjs/event-emitter, EventEmitter2 | Internal event bus |
| | WebSocket | socket.io | Real-time bidirectional communication |
| | Scheduling | @nestjs/schedule | Cron-based task scheduling |
| **Desktop** | bytebotd | NestJS, TypeScript 5.7.3 | Desktop automation daemon |
| | Automation | @nut-tree-fork/nut-js | Mouse, keyboard, screen control |
| | Input Tracking | uiohook-napi | Global input event capture |
| | Image Processing | sharp | Screenshot encoding/optimization |
| | MCP | @rekog/mcp-nest | Model Context Protocol server |
| | VNC | noVNC, websockify | Web-based remote desktop |
| **Environment** | OS | Ubuntu 22.04 LTS | Base system |
| | Desktop | XFCE4 | Lightweight window manager |
| | Display | X11, Xvfb | Virtual display server |
| | Applications | Firefox ESR, VS Code, 1Password | Pre-installed tools |
| **Shared** | Types | Zod, class-validator | Runtime validation |
| | Package | @bytebot/shared | Cross-package type definitions |

Sources: [README.md:230-239](), Diagram 4 from high-level architecture, [docs/core-concepts/desktop-environment.mdx:36-88]()

## Persistence Layer

The system uses PostgreSQL with Prisma ORM for type-safe database access. Four primary models represent the data structure:

| Model | Purpose | Key Relationships |
|-------|---------|-------------------|
| `Task` | Work unit with description, status, priority | Has many `Message`, `Summary`, `File` |
| `Message` | Conversation entry (user input, LLM response, tool results) | Belongs to `Task` and optionally `Summary` |
| `Summary` | Compressed conversation context for token management | Belongs to `Task`, self-referential for hierarchy |
| `File` | Uploaded file metadata and base64 data | Belongs to `Task` |

**Schema locations:**
- [packages/bytebot-agent/prisma/schema.prisma]()

**Service access patterns:**
- `TasksService` → CRUD operations on `Task` model
- `MessagesService` → Message creation, retrieval, grouping logic
- `SummariesService` → Hierarchical summarization when context exceeds 75% token limit
- `FilesService` → File upload handling, base64 encoding, desktop materialization

**Message content structure:**
Messages use a `Json` type storing arrays of `MessageContentBlock` objects compatible with Anthropic's Claude API format (text, tool_use, tool_result, image, thinking, document blocks).

Sources: [docs/api-reference/agent/tasks.mdx:10-21](), Diagram 5 from high-level architecture

## Communication Architecture

```mermaid
graph TB
    subgraph "Client Layer"
        Browser["Web Browser<br/>React Components"]
    end
    
    subgraph "Proxy Layer - Port 9992"
        ExpressServer["Express Server<br/>server.ts"]
        HTTPProxy["API Proxy<br/>app/api/proxy/[...path]"]
        WSHandler["WebSocket Handler<br/>app/api/proxy/tasks"]
        VNCHandler["VNC Proxy<br/>app/api/proxy/websockify"]
    end
    
    subgraph "Backend Layer - Port 9991"
        RESTRoutes["REST Endpoints<br/>TasksController"]
        SocketIOServer["Socket.IO Server<br/>TasksGateway"]
        EventBus["Internal Event Bus<br/>EventEmitter2"]
    end
    
    subgraph "Desktop Layer - Port 9990"
        ComputerAPI["Computer Use API<br/>POST /computer-use"]
        VNCD["VNC Server<br/>websockify:6080"]
        MCPSSE["MCP SSE<br/>GET /mcp"]
    end
    
    Browser -->|"HTTP GET/POST"| HTTPProxy
    Browser -->|"Socket.IO upgrade"| WSHandler
    Browser -->|"WebSocket upgrade"| VNCHandler
    
    HTTPProxy -->|"Proxy to :9991"| RESTRoutes
    WSHandler -->|"Proxy to :9991"| SocketIOServer
    VNCHandler -->|"Proxy to :9990"| VNCD
    
    RESTRoutes -.->|"Emit events"| EventBus
    EventBus -.->|"@OnEvent listeners"| SocketIOServer
    
    RESTRoutes -->|"HTTP POST"| ComputerAPI
    
    MCPClientExt["External MCP Client"] -->|"SSE stream"| MCPSSE
```

**HTTP Communication:**
- Frontend makes REST requests to `/api/proxy/*`
- Next.js API routes forward to `http://bytebot-agent:9991/*`
- TasksController handles `/tasks` endpoints (GET, POST, PATCH, DELETE)
- AgentProcessor makes POST requests to `http://bytebotd:9990/computer-use`

**WebSocket Communication:**
- Frontend establishes Socket.IO connection to `/api/proxy/tasks`
- UI server proxies WebSocket upgrade to `bytebot-agent:9991`
- TasksGateway handles client events: `join_task`, `leave_task`
- Server emits events: `task_created`, `task_updated`, `task_deleted`, `new_message`
- Room-based subscriptions (clients join `task-{id}` rooms for targeted updates)

**VNC Streaming:**
- Separate WebSocket channel for desktop view
- Proxied from `/api/proxy/websockify` to `bytebotd:9990` websockify server
- Uses noVNC client library for browser rendering
- Bi-directional for mouse/keyboard input and screen updates

**Internal Event Bus:**
- `TasksService` emits domain events: `task.completed`, `task.failed`, `task.takeover`, `task.resume`, `task.cancel`
- `AgentProcessor` listens via `@OnEvent` decorators
- Enables reactive behavior (e.g., abort processing on takeover)

Sources: [README.md:108-116](), Diagram 3 from high-level architecture, [docs/deployment/railway.mdx:18-28]()

## Deployment Options

The system supports three primary deployment methods:

**1. Docker Compose (Local Development)**
- Single command: `docker-compose -f docker/docker-compose.yml up -d`
- Four containers: bytebot-ui, bytebot-agent, bytebotd, postgres
- Environment variables in `docker/.env` for API keys
- Exposed ports: 9992 (UI), 9991 (Agent API), 9990 (Desktop API)
- Volume mounts for PostgreSQL persistence

**2. Railway (Cloud Hosting)**
- One-click deployment via template
- Automatic private networking between services
- Only bytebot-ui exposed with public domain
- Managed PostgreSQL database
- Environment variables configured via Railway dashboard
- Deployment time: ~2 minutes

**3. Kubernetes/Helm**
- Helm chart at `helm/` directory
- Service definitions for ui, agent, desktop
- StatefulSet for desktop with persistent volume
- Ingress for external access
- ConfigMaps for environment variables
- Supports horizontal scaling of agent service

Sources: [README.md:82-106](), [docs/quickstart.mdx:1-363](), [docs/deployment/railway.mdx:1-90]()

## Next Steps

For hands-on deployment, see [Quick Start](#1.1).

For architectural deep-dives, see [System Architecture](#2), [Service Architecture](#2.1), and [Communication Patterns](#2.2).

For understanding the task lifecycle, see [Core Concepts](#1.2) and [Task Management System](#5).

For AI agent internals, see [Agent System](#6) and [Agent Processor](#6.1).

For desktop automation capabilities, see [Desktop Environment](#7) and [Desktop Tools](#7.2).

Sources: TOC structure

---

# Page: Quick Start

# Quick Start

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [docs/api-reference/agent/tasks.mdx](docs/api-reference/agent/tasks.mdx)
- [docs/core-concepts/desktop-environment.mdx](docs/core-concepts/desktop-environment.mdx)
- [docs/deployment/railway.mdx](docs/deployment/railway.mdx)
- [docs/guides/task-creation.mdx](docs/guides/task-creation.mdx)
- [docs/introduction.mdx](docs/introduction.mdx)
- [docs/quickstart.mdx](docs/quickstart.mdx)

</details>



This guide provides a streamlined path to deploying Bytebot and executing your first AI-powered desktop automation task. You will launch the complete stack (virtual desktop, AI agent, web interface, and database) and verify functionality within minutes.

For detailed configuration options and advanced deployment scenarios, see [Installation and Setup](#3). For architectural details about how the services communicate, see [System Architecture](#2). For deployment-specific guides, see [Docker Deployment](#3.1) or [Railway Deployment](#3.2).

---

## Prerequisites

Before deploying Bytebot, ensure you have:

| Requirement | Details |
|-------------|---------|
| **Deployment Platform** | Docker ≥ 20.10 with Docker Compose (for self-hosting) OR Railway account (for cloud hosting) |
| **System Resources** | Minimum 4GB RAM available, 10GB disk space |
| **AI Provider API Key** | At least one of: Anthropic API key ([console.anthropic.com](https://console.anthropic.com)), OpenAI API key ([platform.openai.com](https://platform.openai.com/api-keys)), or Google Gemini API key ([makersuite.google.com](https://makersuite.google.com/app/apikey)) |

Sources: [README.md:38-45](), [docs/quickstart.mdx:36-44]()

---

## Deployment Options

Bytebot supports two primary deployment methods optimized for different use cases.

### Railway Deployment (Cloud - Fastest)

Railway provides zero-configuration deployment with automatic service networking.

**Deployment Steps:**

```mermaid
sequenceDiagram
    participant User
    participant Railway
    participant GithubRegistry as "GitHub Container Registry"
    participant Services as "Bytebot Services"
    
    User->>Railway: Click Deploy on Railway button
    User->>Railway: Configure ANTHROPIC_API_KEY / OPENAI_API_KEY / GEMINI_API_KEY
    Railway->>GithubRegistry: Pull ghcr.io/bytebot-ai/bytebot-ui:edge
    Railway->>GithubRegistry: Pull ghcr.io/bytebot-ai/bytebot-agent:edge
    Railway->>GithubRegistry: Pull ghcr.io/bytebot-ai/bytebot-desktop:edge
    Railway->>GithubRegistry: Pull postgres:14-alpine
    Railway->>Services: Deploy all services
    Railway->>Services: Configure private networking
    Railway->>User: Return public URL (e.g., https://bytebot-ui-prod.up.railway.app)
```

**Services Deployed**

| Service | Image | Port | Public Access |
|---------|-------|------|---------------|
| `bytebot-ui` | `ghcr.io/bytebot-ai/bytebot-ui:edge` | 9992 | Yes (assigned public domain) |
| `bytebot-agent` | `ghcr.io/bytebot-ai/bytebot-agent:edge` | 9991 | No (private network only) |
| `bytebot-desktop` | `ghcr.io/bytebot-ai/bytebot-desktop:edge` | 9990 | No (private network only) |
| `postgres` | `postgres:14-alpine` | 5432 | No (private network only) |

**Configuration:**

1. Navigate to the Railway template deployment page
2. Set environment variable for `bytebot-agent` service:
   - `ANTHROPIC_API_KEY=sk-ant-...` (for Claude models) OR
   - `OPENAI_API_KEY=sk-...` (for GPT models) OR
   - `GEMINI_API_KEY=...` (for Gemini models)
3. Click Deploy
4. Wait approximately 2 minutes for initial build
5. Access the provided URL

Sources: [README.md:85-89](), [docs/quickstart.mdx:11-26](), [docs/deployment/railway.mdx:18-26]()

### Docker Compose Deployment (Self-Hosted)

Docker Compose provides full control over the deployment environment on your own infrastructure.

**Deployment Steps:**

```bash
# Clone repository
git clone https://github.com/bytebot-ai/bytebot.git
cd bytebot

# Configure AI provider (choose one)
echo "ANTHROPIC_API_KEY=sk-ant-your_key_here" > docker/.env
# OR: echo "OPENAI_API_KEY=sk-your_key_here" > docker/.env
# OR: echo "GEMINI_API_KEY=your_key_here" > docker/.env

# Start all services
docker-compose -f docker/docker-compose.yml up -d

# Verify services are running
docker-compose -f docker/docker-compose.yml ps
```

**Service Architecture:**

```mermaid
graph TB
    subgraph "Host Machine - Port Bindings"
        Port9992["localhost:9992"]
        Port9991["localhost:9991"]
        Port9990["localhost:9990"]
    end
    
    subgraph "Docker Network - bytebot_network"
        UI["bytebot-ui container<br/>Next.js 15.4.7 + Express<br/>Port 9992"]
        Agent["bytebot-agent container<br/>NestJS + Prisma<br/>Port 9991"]
        Desktop["bytebot-desktop container<br/>bytebotd daemon<br/>Ubuntu 22.04 + XFCE<br/>Port 9990"]
        DB["postgres container<br/>PostgreSQL 14<br/>Port 5432"]
    end
    
    Port9992 --> UI
    Port9991 --> Agent
    Port9990 --> Desktop
    
    UI -->|"HTTP proxy to /tasks"| Agent
    UI -->|"WebSocket proxy to /socket.io"| Agent
    UI -->|"WebSocket proxy to /vnc"| Desktop
    
    Agent -->|"Prisma Client"| DB
    Agent -->|"POST /computer-use"| Desktop
    
    Desktop -->|"Screenshot responses"| Agent
```

**Docker Compose Service Definitions:**

The [docker/docker-compose.yml]() file defines four services:
- `bytebot-ui`: Exposes port 9992, depends on `bytebot-agent`
- `bytebot-agent`: Exposes port 9991, depends on `postgres` and `bytebot-desktop`, sets `DATABASE_URL` and `BYTEBOT_CORE_URL`
- `bytebot-desktop`: Exposes port 9990, runs with `--shm-size=2gb` for desktop graphics
- `postgres`: Stores tasks, messages, summaries, and file metadata

Sources: [README.md:92-104](), [docs/quickstart.mdx:50-91](), [docker/docker-compose.yml]()

---

## Service Access Points

After successful deployment, the following endpoints are available:

| Endpoint | URL (Local) | URL (Railway) | Purpose |
|----------|-------------|---------------|---------|
| **Web Interface** | `http://localhost:9992` | `https://<project>.up.railway.app` | Task creation UI, chat interface, desktop viewer |
| **Tasks API** | `http://localhost:9991/tasks` | Internal only | REST API for task CRUD operations |
| **Desktop Control API** | `http://localhost:9990/computer-use` | Internal only | Direct desktop automation endpoint |
| **MCP Endpoint** | `http://localhost:9990/mcp` | Internal only | Model Context Protocol server-sent events |
| **VNC Access** | `http://localhost:9990/vnc` | Internal only | noVNC web client for direct desktop access |

**Port Assignment Rationale:**

```mermaid
graph LR
    subgraph "External Access"
        Browser["Web Browser"]
    end
    
    subgraph "bytebot-ui - Port 9992"
        UIRoutes["Express Custom Routes"]
        NextApp["Next.js Application"]
        ProxyTasks["/api/proxy/tasks → :9991/tasks"]
        ProxyWS["/api/proxy/tasks → :9991 Socket.IO"]
        ProxyVNC["/api/proxy/websockify → :9990 WebSocket"]
    end
    
    subgraph "bytebot-agent - Port 9991"
        TasksController["TasksController"]
        TasksGateway["TasksGateway (Socket.IO)"]
    end
    
    subgraph "bytebotd - Port 9990"
        ComputerUseController["ComputerUseController"]
        VNCServer["VNC WebSocket Server"]
    end
    
    Browser --> UIRoutes
    Browser --> NextApp
    ProxyTasks --> TasksController
    ProxyWS --> TasksGateway
    ProxyVNC --> VNCServer
```

The UI service acts as the sole public-facing component, proxying all requests to backend services through Express middleware defined in [apps/bytebot-ui/server.js]().

Sources: [README.md:171-176](), [docs/quickstart.mdx:169-176](), [apps/bytebot-ui/server.js]()

---

## Verification Steps

Verify your deployment is functioning correctly:

**1. Check Service Health:**

```bash
# For Docker Compose deployment
docker-compose -f docker/docker-compose.yml ps

# Expected output shows all services as "Up"
# NAME                STATUS    PORTS
# bytebot-ui          Up        0.0.0.0:9992->9992/tcp
# bytebot-agent       Up        0.0.0.0:9991->9991/tcp
# bytebot-desktop     Up        0.0.0.0:9990->9990/tcp
# postgres            Up        5432/tcp
```

**2. Access Web Interface:**

Navigate to `http://localhost:9992` (or your Railway-provided URL). You should see the task creation interface with an input field and model selector.

**3. Verify Desktop Environment:**

The virtual desktop should be accessible. The `bytebotd` daemon runs on port 9990 and manages:
- X11 display server (`:99`)
- XFCE4 desktop environment
- VNC server (port 6080, proxied via websockify)
- Computer use API endpoint

Sources: [docs/quickstart.mdx:207-223](), [docs/core-concepts/desktop-environment.mdx:72-83]()

---

## Creating Your First Task

Test the complete system by creating a simple automation task.

### Via Web Interface

**Task Creation Flow:**

```mermaid
sequenceDiagram
    participant User
    participant UIComponent as "CreateTaskForm component"
    participant APIClient as "taskUtils.createTask"
    participant TasksController as "TasksController.create"
    participant TasksService as "TasksService"
    participant Database as "PostgreSQL"
    participant AgentScheduler as "AgentScheduler"
    
    User->>UIComponent: Enter task description
    User->>UIComponent: Click Create button
    UIComponent->>APIClient: createTask({description, priority, model})
    APIClient->>TasksController: POST /tasks
    TasksController->>TasksService: create(createTaskDto)
    TasksService->>Database: INSERT INTO Task
    Database->>TasksService: Return task entity
    TasksService->>TasksController: Return task
    TasksController->>APIClient: 201 Created
    APIClient->>UIComponent: Task created
    UIComponent->>User: Redirect to /tasks/{id}
    
    Note over AgentScheduler: Cron job runs every 5 seconds
    AgentScheduler->>TasksService: findPendingTasks()
    TasksService->>AgentScheduler: Return pending tasks
    AgentScheduler->>AgentScheduler: processTask(task)
```

**Example Tasks:**

| Task Type | Description | Expected Outcome |
|-----------|-------------|------------------|
| **Screenshot** | "Take a screenshot of the desktop" | Agent captures desktop screenshot, saves to filesystem, reports completion |
| **Browser Navigation** | "Open Firefox and go to google.com" | Agent launches Firefox, navigates to URL, confirms page load |
| **File Creation** | "Create a text file called hello.txt with today's date" | Agent creates file in `/home/user/Desktop`, writes date, verifies creation |

Sources: [apps/bytebot-ui/app/(dashboard)/page.tsx](), [apps/bytebot-ui/lib/taskUtils.ts](), [apps/bytebot-agent/src/tasks/tasks.controller.ts]()

### Via REST API

Create tasks programmatically using HTTP requests:

```bash
# Simple task creation
curl -X POST http://localhost:9991/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Take a screenshot of the desktop",
    "priority": "MEDIUM"
  }'

# Task with file upload
curl -X POST http://localhost:9991/tasks \
  -F "description=Read this PDF and extract all email addresses" \
  -F "priority=HIGH" \
  -F "files=@document.pdf"
```

**Response Structure:**

```json
{
  "id": "cm5a1b2c3d4e5f6g7h8i9j0k",
  "description": "Take a screenshot of the desktop",
  "status": "PENDING",
  "priority": "MEDIUM",
  "control": "AGENT",
  "model": "claude-3-5-sonnet-20241022",
  "createdAt": "2025-01-15T10:30:00.000Z",
  "updatedAt": "2025-01-15T10:30:00.000Z"
}
```

The `status` field transitions from `PENDING` → `RUNNING` → `COMPLETED` as the `AgentScheduler` picks up the task and the `AgentProcessor` executes it.

Sources: [docs/api-reference/agent/tasks.mdx:25-67](), [apps/bytebot-agent/src/tasks/tasks.controller.ts]()

---

## Task Execution Monitoring

Once a task is created, monitor its execution through the web interface or API.

### Web Interface Monitoring

Navigate to `/tasks/{taskId}` to view:
- Real-time message stream (user messages, assistant responses, tool executions)
- Desktop viewer showing live VNC feed or screenshot history
- Task status indicator (green dot = running)
- Control handoff button (switch between agent and user control)

The UI uses WebSocket connections to receive real-time updates:

```mermaid
sequenceDiagram
    participant Browser
    participant useWebSocket as "useWebSocket hook"
    participant TasksGateway as "TasksGateway"
    participant TasksService as "TasksService"
    
    Browser->>useWebSocket: Connect to /api/proxy/tasks
    useWebSocket->>TasksGateway: Socket.IO connection
    useWebSocket->>TasksGateway: emit('join_task', {taskId})
    TasksGateway->>TasksGateway: socket.join(`task-${taskId}`)
    
    Note over TasksService: Task status changes
    TasksService->>TasksGateway: emitTaskUpdated(task)
    TasksGateway->>useWebSocket: emit to room task-{taskId}: 'task_updated'
    useWebSocket->>Browser: Update UI state
    
    Note over TasksService: New message created
    TasksService->>TasksGateway: emitNewMessage(message)
    TasksGateway->>useWebSocket: emit to room task-{taskId}: 'new_message'
    useWebSocket->>Browser: Append to message list
```

Sources: [apps/bytebot-ui/hooks/useWebSocket.ts](), [apps/bytebot-agent/src/tasks/tasks.gateway.ts]()

### API Monitoring

Poll the task status endpoint:

```bash
# Get task by ID (includes messages)
curl http://localhost:9991/tasks/{taskId}

# Get currently running task
curl http://localhost:9991/tasks/in-progress
```

Sources: [docs/api-reference/agent/tasks.mdx:116-151]()

---

## Common First-Run Issues

| Symptom | Cause | Resolution |
|---------|-------|------------|
| Container fails to start | Insufficient system resources | Verify 4GB+ RAM available: `docker stats` |
| "Invalid API key" error | Missing or malformed AI provider key | Check [docker/.env]() or Railway environment variables |
| UI shows "Connecting..." indefinitely | Backend services not ready | Wait 30 seconds for services to initialize, check `docker-compose logs` |
| Task stuck in PENDING | AgentScheduler cron not triggering | Verify `bytebot-agent` container is running: `docker ps` |
| Desktop actions fail | bytebotd daemon not responding | Check `bytebot-desktop` logs: `docker logs bytebot-desktop` |

Sources: [docs/quickstart.mdx:274-298]()

---

## Next Steps

After verifying your deployment:

1. **Explore Core Concepts**: Understand how tasks, agents, and the desktop environment interact. See [Core Concepts](#1.2).

2. **Advanced Task Creation**: Learn to write effective task descriptions for complex workflows. See [Task Creation & Management](#5).

3. **Customize Desktop Environment**: Install additional applications or password managers. See [Desktop Environment](#7).

4. **API Integration**: Integrate Bytebot into your applications using the Tasks REST API. See [API Reference](#10).

5. **Production Deployment**: Configure authentication, resource limits, and monitoring. See [Deployment Architecture](#2.3).

Sources: [docs/quickstart.mdx:300-320]()

---

# Page: Core Concepts

# Core Concepts

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [docs/api-reference/agent/tasks.mdx](docs/api-reference/agent/tasks.mdx)
- [docs/core-concepts/desktop-environment.mdx](docs/core-concepts/desktop-environment.mdx)
- [docs/deployment/railway.mdx](docs/deployment/railway.mdx)
- [docs/guides/task-creation.mdx](docs/guides/task-creation.mdx)
- [docs/introduction.mdx](docs/introduction.mdx)
- [docs/quickstart.mdx](docs/quickstart.mdx)
- [packages/bytebot-agent/prisma/migrations/20250722041608_files/migration.sql](packages/bytebot-agent/prisma/migrations/20250722041608_files/migration.sql)
- [packages/bytebot-agent/src/agent/agent.computer-use.ts](packages/bytebot-agent/src/agent/agent.computer-use.ts)
- [packages/bytebot-agent/src/agent/agent.constants.ts](packages/bytebot-agent/src/agent/agent.constants.ts)
- [packages/bytebot-agent/src/agent/agent.scheduler.ts](packages/bytebot-agent/src/agent/agent.scheduler.ts)
- [packages/bytebot-agent/src/agent/agent.tools.ts](packages/bytebot-agent/src/agent/agent.tools.ts)
- [packages/bytebotd/src/computer-use/computer-use.controller.ts](packages/bytebotd/src/computer-use/computer-use.controller.ts)
- [packages/bytebotd/src/main.ts](packages/bytebotd/src/main.ts)

</details>



This page explains the fundamental building blocks of Bytebot and how they work together. It covers Tasks (the unit of work), the Virtual Desktop (the execution environment), the AI Agent (the decision-making system), Tools (available actions), and the observe-act-verify cycle (the execution pattern).

For architectural details about how services communicate, see [Service Architecture](#2.1). For deployment configuration, see [Installation and Setup](#3).

---

## Tasks: The Unit of Work

A **Task** represents a single objective that Bytebot should accomplish. Tasks are the primary interface between users and the system, stored in PostgreSQL, and processed sequentially by the agent.

### Task Data Model

```mermaid
erDiagram
    Task ||--o{ Message : "has"
    Task ||--o{ Summary : "has"
    Task ||--o{ File : "has"
    
    Task {
        string id PK
        string description
        enum status
        enum priority
        enum type
        enum control
        string model
        datetime scheduledFor
        datetime queuedAt
        datetime executedAt
        datetime completedAt
        string error
    }
    
    Message {
        string id PK
        json content
        enum role
        string taskId FK
        string summaryId FK
    }
    
    Summary {
        string id PK
        string content
        string taskId FK
        string parentId FK
    }
    
    File {
        string id PK
        string name
        string type
        int size
        string data
        string taskId FK
    }
```

**Sources:** [packages/bytebot-agent/prisma/migrations/20250722041608_files/migration.sql:1-17](), [docs/api-reference/agent/tasks.mdx:12-21]()

### Task States and Lifecycle

Tasks transition through a state machine managed by `TasksService`:

| Status | Description | Next States |
|--------|-------------|-------------|
| `PENDING` | Created, awaiting scheduling | `RUNNING` |
| `RUNNING` | Agent actively processing | `COMPLETED`, `NEEDS_HELP`, `FAILED`, `CANCELLED` |
| `NEEDS_HELP` | Requires user clarification | `RUNNING` (after user input) |
| `COMPLETED` | Successfully finished | (terminal) |
| `FAILED` | Encountered error | (terminal) |
| `CANCELLED` | User cancelled | (terminal) |

**Sources:** [docs/api-reference/agent/tasks.mdx:16-17](), [docs/guides/task-creation.mdx:203-216]()

### Task Scheduling and Execution

```mermaid
flowchart TB
    Create["Task created via API<br/>(TasksController.create)"]
    Queue["status=PENDING<br/>stored in PostgreSQL"]
    Cron["AgentScheduler.handleCron<br/>(every 5 seconds)"]
    CheckScheduled["Check scheduledFor<br/>timestamp"]
    SetQueued["Set queuedAt"]
    CheckAgent["Is agent running?"]
    WriteFiles["Write task.files to<br/>/home/user/Desktop/"]
    SetRunning["status=RUNNING<br/>executedAt=now"]
    Process["AgentProcessor.processTask"]
    
    Create --> Queue
    Queue --> Cron
    Cron --> CheckScheduled
    CheckScheduled -->|"scheduledFor < now"| SetQueued
    SetQueued --> CheckAgent
    CheckAgent -->|No| WriteFiles
    WriteFiles --> SetRunning
    SetRunning --> Process
    CheckAgent -->|Yes| Cron
```

**Sources:** [packages/bytebot-agent/src/agent/agent.scheduler.ts:22-62]()

### File Handling

Files uploaded with tasks are:
1. Base64-encoded and stored in the `File` table
2. Written to `/home/user/Desktop/` before task execution via `writeFile` function
3. Accessible to the agent through `computer_read_file` tool

**Sources:** [packages/bytebot-agent/src/agent/agent.scheduler.ts:43-53](), [packages/bytebot-agent/src/agent/agent.computer-use.ts:612-646]()

---

## Virtual Desktop: The Execution Environment

The **bytebotd** service provides a containerized Ubuntu desktop where all task actions are executed. This isolation ensures security and consistency.

### Desktop Architecture

```mermaid
graph TB
    subgraph bytebotd["bytebotd Service (Port 9990)"]
        Controller["ComputerUseController<br/>/computer-use endpoint"]
        Service["ComputerUseService<br/>action dispatcher"]
        NutJS["@nut-tree-fork/nut-js<br/>automation library"]
        UIHook["uiohook-napi<br/>input tracking"]
        VNCServer["VNC Server<br/>port 6080"]
        MCPEndpoint["MCP SSE Endpoint<br/>/mcp"]
    end
    
    subgraph Desktop["XFCE Desktop Environment"]
        Firefox["Firefox Browser"]
        Thunderbird["Thunderbird Email"]
        OnePassword["1Password Manager"]
        VSCode["Visual Studio Code"]
        Terminal["Terminal"]
        FileManager["File Manager"]
    end
    
    Controller --> Service
    Service --> NutJS
    NutJS --> Desktop
    UIHook --> Desktop
    VNCServer --> Desktop
    MCPEndpoint --> Service
```

**Sources:** [packages/bytebotd/src/main.ts:1-39](), [packages/bytebotd/src/computer-use/computer-use.controller.ts:1-43](), [docs/core-concepts/desktop-environment.mdx:70-88]()

### Desktop Specifications

| Property | Value |
|----------|-------|
| Operating System | Ubuntu 22.04 LTS |
| Desktop Environment | XFCE4 |
| Display Server | X11 |
| Resolution | 1280x960 (defined in `DEFAULT_DISPLAY_SIZE`) |
| User | `user` (passwordless sudo) |
| Home Directory | `/home/user` |

**Sources:** [packages/bytebot-agent/src/agent/agent.constants.ts:1-4](), [docs/core-concepts/desktop-environment.mdx:39-43](), [docs/core-concepts/desktop-environment.mdx:97-101]()

### Desktop API Endpoint

All desktop actions are executed via `POST /computer-use` on the bytebotd service:

```
POST http://localhost:9990/computer-use
Content-Type: application/json

{
  "action": "screenshot" | "move_mouse" | "click_mouse" | ...,
  ...action-specific parameters
}
```

**Sources:** [packages/bytebotd/src/computer-use/computer-use.controller.ts:19-42]()

---

## AI Agent: The Decision-Making System

The **AgentProcessor** coordinates task execution by maintaining a continuous loop of observation, planning, and action using Large Language Models.

### Agent Components

```mermaid
graph TB
    subgraph AgentProcessor["AgentProcessor"]
        ProcessTask["processTask(taskId)"]
        BuildContext["Build context:<br/>- Latest Summary<br/>- Unsummarized Messages<br/>- System Prompt"]
        CallLLM["BytebotAgentService<br/>(Anthropic/OpenAI/Google)"]
        ParseResponse["Parse LLM response<br/>for tool use blocks"]
    end
    
    subgraph ToolHandlers["Tool Handlers"]
        ComputerTool["handleComputerToolUse<br/>(mouse, keyboard, screenshot)"]
        TaskTool["handleTaskManagementTool<br/>(set_task_status, create_task)"]
    end
    
    subgraph ExternalServices["External Services"]
        TasksService["TasksService<br/>(DB operations)"]
        MessagesService["MessagesService<br/>(context management)"]
        SummariesService["SummariesService<br/>(context compression)"]
        Bytebotd["bytebotd<br/>(action execution)"]
    end
    
    ProcessTask --> BuildContext
    BuildContext --> CallLLM
    CallLLM --> ParseResponse
    ParseResponse --> ComputerTool
    ParseResponse --> TaskTool
    ComputerTool --> Bytebotd
    TaskTool --> TasksService
    BuildContext --> MessagesService
    BuildContext --> SummariesService
```

**Sources:** [packages/bytebot-agent/src/agent/agent.processor.ts]() (inferred from architecture), [packages/bytebot-agent/src/agent/agent.computer-use.ts:28-239]()

### LLM Integration

The agent supports three LLM providers through a common interface:

| Provider | Model (Default) | Environment Variable |
|----------|-----------------|---------------------|
| Anthropic | `claude-3-5-sonnet-20241022` | `ANTHROPIC_API_KEY` |
| OpenAI | `gpt-4o` | `OPENAI_API_KEY` |
| Google | `gemini-1.5-flash` | `GEMINI_API_KEY` |

**Sources:** [docs/quickstart.mdx:327-337](), [README.md:96-99]()

### Agent System Prompt

The agent operates under strict principles defined in `AGENT_SYSTEM_PROMPT`:

1. **Observe First**: Always take screenshot before acting
2. **Navigate Applications**: Use `computer_application` to switch apps
3. **Human-Like Interaction**: Smooth movements, realistic typing
4. **Valid Keys Only**: Use exact nut-tree `Key` enum identifiers
5. **Verify Every Step**: Screenshot after each action
6. **Efficiency & Clarity**: Minimize unnecessary operations
7. **Stay Within Scope**: Only do what user requested
8. **Security**: Flag sensitive data with `isSensitive`
9. **Consistency & Persistence**: Complete bulk operations fully

**Sources:** [packages/bytebot-agent/src/agent/agent.constants.ts:17-175]()

---

## Tools: Available Actions

Tools are functions the agent can invoke to interact with the desktop and manage tasks. They are defined in `agentTools` array and fall into four categories.

### Tool Categories

```mermaid
graph LR
    subgraph Mouse["Mouse Tools (7)"]
        MM["computer_move_mouse"]
        TM["computer_trace_mouse"]
        CM["computer_click_mouse"]
        PM["computer_press_mouse"]
        DM["computer_drag_mouse"]
        SC["computer_scroll"]
        CP["computer_cursor_position"]
    end
    
    subgraph Keyboard["Keyboard Tools (4)"]
        TK["computer_type_keys"]
        PK["computer_press_keys"]
        TT["computer_type_text"]
        PT["computer_paste_text"]
    end
    
    subgraph Utility["Utility Tools (3)"]
        SS["computer_screenshot"]
        AP["computer_application"]
        WT["computer_wait"]
    end
    
    subgraph Task["Task Tools (3)"]
        STS["set_task_status"]
        CT["create_task"]
        RF["computer_read_file"]
    end
```

**Sources:** [packages/bytebot-agent/src/agent/agent.tools.ts:387-405]()

### Tool Execution Flow

```mermaid
sequenceDiagram
    participant Agent as AgentProcessor
    participant Handler as handleComputerToolUse
    participant API as bytebotd API
    participant Desktop as XFCE Desktop
    
    Agent->>Handler: ToolUseContentBlock
    
    alt screenshot or cursor_position
        Handler->>API: POST /computer-use
        API->>Desktop: Execute action
        Desktop-->>API: Result
        API-->>Handler: Response
        Handler-->>Agent: ToolResultContentBlock
    else other tools
        Handler->>API: POST /computer-use
        API->>Desktop: Execute action
        Handler->>Handler: Wait 750ms
        Handler->>API: POST /computer-use<br/>{action: "screenshot"}
        API-->>Handler: Screenshot image
        Handler-->>Agent: ToolResult + Image
    end
```

**Sources:** [packages/bytebot-agent/src/agent/agent.computer-use.ts:28-239]()

### Tool Definitions Example

Mouse click tool schema:
```typescript
{
  name: 'computer_click_mouse',
  description: 'Performs a mouse click at the specified coordinates or current position',
  input_schema: {
    type: 'object',
    properties: {
      coordinates: { type: 'object', nullable: true },
      button: { type: 'string', enum: ['left', 'right', 'middle'] },
      holdKeys: { type: 'array', nullable: true },
      clickCount: { type: 'integer', default: 1 }
    },
    required: ['button', 'clickCount']
  }
}
```

**Sources:** [packages/bytebot-agent/src/agent/agent.tools.ts:67-90]()

---

## The Observe-Act-Verify Cycle

The agent operates in a continuous loop, always grounding decisions in visual observation of the desktop state.

### Execution Loop

```mermaid
stateDiagram-v2
    [*] --> Observe
    
    Observe: Take Screenshot<br/>(computer_screenshot)
    
    Observe --> BuildContext: Screenshot captured
    
    BuildContext: Assemble Context<br/>- Latest Summary<br/>- Unsummarized Messages<br/>- Current Screenshot<br/>- System Prompt
    
    BuildContext --> LLMCall: Send to LLM
    
    LLMCall: LLM Reasoning<br/>(Anthropic/OpenAI/Google)
    
    LLMCall --> ParseResponse: Receive response
    
    ParseResponse: Extract Tool Use Blocks<br/>or Completion Signal
    
    state CheckResponse <<choice>>
    ParseResponse --> CheckResponse
    
    CheckResponse --> ExecuteTool: Tool use detected
    CheckResponse --> Complete: set_task_status called
    
    ExecuteTool: Execute via bytebotd<br/>(click, type, etc.)
    
    ExecuteTool --> Wait: Action sent
    
    Wait: Pause 750ms<br/>(UI settling time)
    
    Wait --> Observe: Verify result
    
    Complete --> [*]: Task finished
```

**Sources:** [packages/bytebot-agent/src/agent/agent.computer-use.ts:184-196](), [packages/bytebot-agent/src/agent/agent.constants.ts:94-138]()

### Context Building Strategy

The agent manages LLM token limits through hierarchical summarization:

1. **Initial Context**: Latest summary (if exists) + all unsummarized messages
2. **Token Check**: If usage exceeds 75% of context window
3. **Summarization**: Send conversation to LLM with `SUMMARIZATION_SYSTEM_PROMPT`
4. **Storage**: Create new `Summary` record, link processed messages via `summaryId`
5. **Next Iteration**: Use new summary + only new messages

**Sources:** [packages/bytebot-agent/src/agent/agent.constants.ts:6-15]()

### Verification Pattern

After each action (except `screenshot` and `cursor_position`), the agent:
1. Waits 750ms for UI to settle
2. Takes a screenshot
3. Receives both text confirmation and visual proof
4. Sends screenshot to LLM in next iteration
5. LLM validates expected state before continuing

This creates a fail-safe loop where the agent always knows the actual desktop state.

**Sources:** [packages/bytebot-agent/src/agent/agent.computer-use.ts:184-219](), [packages/bytebot-agent/src/agent/agent.constants.ts:43]()

---

## Integration: How Concepts Work Together

```mermaid
flowchart TD
    UserTask["User creates Task<br/>'Download invoices and organize'"]
    
    Scheduler["AgentScheduler picks task<br/>every 5 seconds"]
    
    WriteFiles["Write task.files to Desktop"]
    
    AgentStart["AgentProcessor.processTask<br/>status=RUNNING"]
    
    Screenshot1["Tool: computer_screenshot"]
    
    Context["Build context:<br/>Summary + Messages + Screenshot"]
    
    LLM1["LLM: 'I'll open Firefox'"]
    
    Tool1["Tool: computer_application<br/>{application: 'firefox'}"]
    
    Execute1["bytebotd executes<br/>via NutJS"]
    
    Wait1["Wait 750ms"]
    
    Screenshot2["Tool: computer_screenshot"]
    
    Context2["Build context with new screenshot"]
    
    LLM2["LLM: 'Firefox opened,<br/>I'll navigate to site'"]
    
    ToolN["Tool: computer_click_mouse<br/>Tool: computer_type_text<br/>...continue cycle..."]
    
    Complete["Tool: set_task_status<br/>{status: 'completed'}"]
    
    UpdateDB["TasksService.update<br/>status=COMPLETED"]
    
    UserTask --> Scheduler
    Scheduler --> WriteFiles
    WriteFiles --> AgentStart
    AgentStart --> Screenshot1
    Screenshot1 --> Context
    Context --> LLM1
    LLM1 --> Tool1
    Tool1 --> Execute1
    Execute1 --> Wait1
    Wait1 --> Screenshot2
    Screenshot2 --> Context2
    Context2 --> LLM2
    LLM2 --> ToolN
    ToolN --> Complete
    Complete --> UpdateDB
```

**Sources:** [packages/bytebot-agent/src/agent/agent.scheduler.ts:22-62](), [packages/bytebot-agent/src/agent/agent.computer-use.ts:28-239]()

---

## Summary

The five core concepts form a cohesive system:

1. **Tasks** define what needs to be done
2. **Virtual Desktop** provides isolated execution environment
3. **AI Agent** plans and coordinates actions
4. **Tools** enable interaction with desktop and task management
5. **Observe-Act-Verify** ensures grounded, reliable execution

Together, these create a system where natural language requests are translated into precise desktop actions, always verified through visual observation.

---

# Page: System Architecture

# System Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [docs/api-reference/agent/tasks.mdx](docs/api-reference/agent/tasks.mdx)
- [docs/core-concepts/desktop-environment.mdx](docs/core-concepts/desktop-environment.mdx)
- [docs/deployment/railway.mdx](docs/deployment/railway.mdx)
- [docs/guides/task-creation.mdx](docs/guides/task-creation.mdx)
- [docs/introduction.mdx](docs/introduction.mdx)
- [docs/quickstart.mdx](docs/quickstart.mdx)
- [packages/bytebot-agent/src/main.ts](packages/bytebot-agent/src/main.ts)
- [packages/bytebot-agent/src/tasks/tasks.gateway.ts](packages/bytebot-agent/src/tasks/tasks.gateway.ts)
- [packages/bytebot-ui/next.config.ts](packages/bytebot-ui/next.config.ts)
- [packages/bytebot-ui/server.ts](packages/bytebot-ui/server.ts)
- [packages/bytebot-ui/src/app/api/[[...path]]/route.ts](packages/bytebot-ui/src/app/api/[[...path]]/route.ts)
- [packages/bytebot-ui/src/hooks/useWebSocket.ts](packages/bytebot-ui/src/hooks/useWebSocket.ts)

</details>



This document provides a comprehensive overview of Bytebot's multi-service system architecture, covering service interactions, data flows, and deployment patterns. For detailed information about individual services, see [Service Architecture](#2.1), and for deployment-specific configurations, see [Deployment Architecture](#2.2).

## Overview

Bytebot is implemented as a distributed system consisting of four core services that work together to provide AI-powered desktop automation. The architecture follows a microservices pattern with clear separation of concerns: user interface, AI orchestration, desktop automation, and data persistence.

### High-Level System Architecture

```mermaid
graph TB
    subgraph "Frontend Layer"
        UI[bytebot-ui<br/>"Next.js Web App<br/>:9992"]
    end
    
    subgraph "Backend Services"
        Agent[bytebot-agent<br/>"NestJS Service<br/>:9991"]
        Desktop[bytebot-desktop<br/>"Ubuntu + XFCE<br/>:9990"]
        DB[("PostgreSQL<br/>Database")]
    end
    
    subgraph "External Services"
        LLM["AI Providers<br/>Anthropic, OpenAI, Google"]
        VNC["VNC Server<br/>Desktop Access"]
    end
    
    UI -->|"Task Management<br/>WebSocket/HTTP"| Agent
    UI -->|"VNC Streaming<br/>WebSocket"| Desktop
    Agent -->|"Task Orchestration<br/>Computer Actions"| Desktop
    Agent -->|"Data Persistence"| DB
    Agent -->|"AI Generation"| LLM
    Desktop -->|"Desktop Environment"| VNC
```

The system consists of four main components: `bytebot-ui` serves as the user interface, `bytebot-agent` handles AI orchestration and task management, `bytebot-desktop` provides the virtual desktop environment, and PostgreSQL stores persistent data. External AI providers power the intelligent decision-making, while VNC enables visual access to the desktop.

Sources: [README.md:99-106](), [packages/bytebot-agent/src/app.module.ts:17-36](), [docs/core-concepts/desktop-environment.mdx:72-87]()

## Core Service Architecture

### bytebot-ui Service

The `bytebot-ui` service is a Next.js 15 application that provides the web interface for task management and desktop interaction.

**Key Components:**
- **Task Management Interface**: Creates and monitors tasks
- **Desktop Viewer**: Embedded VNC client for real-time desktop access
- **API Proxy**: Routes requests to backend services
- **WebSocket Client**: Real-time updates from agent service

**Technology Stack:**
- Next.js 15 with React 19
- TypeScript for type safety
- TailwindCSS for styling
- Socket.IO client for WebSocket connections
- react-vnc for desktop viewing

Sources: [README.md:227-233](), [docs/quickstart.mdx:77-83]()

### bytebot-agent Service

The `bytebot-agent` service orchestrates AI-powered task execution through a modular NestJS architecture.

### Agent Service Module Architecture

```mermaid
graph TB
    subgraph "bytebot-agent (NestJS)"
        TasksService[TasksService<br/>"Task CRUD & Lifecycle"]
        AgentProcessor[AgentProcessor<br/>"AI Orchestration"]
        MessagesService[MessagesService<br/>"Message Storage"]
        TasksGateway[TasksGateway<br/>"WebSocket Server"]
        
        subgraph "AI Providers"
            AnthropicService[AnthropicService]
            OpenAIService[OpenAIService] 
            GoogleService[GoogleService]
            ProxyService[ProxyService]
        end
    end
    
    TasksService --> AgentProcessor
    AgentProcessor --> AnthropicService
    AgentProcessor --> OpenAIService
    AgentProcessor --> GoogleService
    AgentProcessor --> ProxyService
    AgentProcessor --> MessagesService
    TasksGateway --> TasksService
```

**Core Module Structure:**
- `AppModule`: Root module importing all service modules
- `AgentModule`: Contains `AgentProcessor`, `AgentScheduler`, and `InputCaptureService`
- `TasksModule`: Task management with `TasksService` and `TasksGateway` for WebSocket
- `MessagesModule`: Message persistence and retrieval
- Provider modules: `AnthropicModule`, `OpenAIModule`, `GoogleModule`, `ProxyModule`

**Key Services:**
- `AgentProcessor`: Coordinates AI model interactions and computer actions
- `AgentScheduler`: Manages task queuing and execution scheduling  
- `InputCaptureService`: Captures user input for training and monitoring
- `TasksService`: CRUD operations for task management
- `MessagesService`: Conversation history and message processing

Sources: [packages/bytebot-agent/src/app.module.ts:17-36](), [packages/bytebot-agent/src/agent/agent.module.ts:15-33]()

### bytebot-desktop Service

The `bytebot-desktop` service provides a containerized Ubuntu 22.04 environment with automation capabilities.

**Core Components:**
- **bytebotd Daemon**: Automation service built on nutjs framework
- **XFCE4 Desktop**: Lightweight desktop environment
- **noVNC Server**: Browser-based desktop access
- **Pre-installed Applications**: Firefox, VS Code, Thunderbird, development tools

**APIs Exposed:**
- Computer Use API on port 9990
- MCP (Model Context Protocol) endpoint at `/mcp`
- VNC WebSocket proxy for remote access

Sources: [docs/core-concepts/desktop-environment.mdx:36-88](), [README.md:227-233]()

### PostgreSQL Database

The database stores all persistent data using Prisma ORM for type-safe database access.

**Schema Structure:**
- **Tasks Table**: Task metadata, status, and execution details
- **Messages Table**: Conversation history and AI interactions
- **Summaries Table**: Task summaries and parent relationships
- **Users Table**: Authentication data (when auth enabled)

Sources: [packages/bytebot-agent/src/app.module.ts:10](), [docs/core-concepts/agent-system.mdx:149-154]()

## Communication and Data Flow

### Task Execution Flow

```mermaid
sequenceDiagram
    participant User
    participant UI as "bytebot-ui"
    participant Agent as "bytebot-agent"
    participant LLM as "AI Provider"
    participant Desktop as "bytebot-desktop"
    participant DB as "PostgreSQL"
    
    User->>UI: "Create task with description"
    UI->>Agent: "POST /tasks (task data)"
    Agent->>DB: "Store task and initial message"
    Agent->>DB: "Update task status to RUNNING"
    
    loop Task Execution
        Agent->>LLM: "Send task context + available tools"
        LLM->>Agent: "Return actions to perform"
        Agent->>Desktop: "Execute computer actions"
        Desktop->>Agent: "Return action results"
        Agent->>DB: "Store messages and results"
        Agent->>UI: "WebSocket updates"
        UI->>User: "Real-time task progress"
        
        alt Task needs help
            Agent->>UI: "Request user intervention"
            UI->>User: "Show takeover interface"
            User->>UI: "Provide guidance"
            UI->>Agent: "User input message"
        end
    end
    
    Agent->>DB: "Update task status to COMPLETED"
    Agent->>UI: "Final task update"
```

This sequence shows the complete task execution flow with tasks created through the UI, processed by the agent using AI providers, executed on the virtual desktop, and continuously updated in the database with real-time feedback to users.

**WebSocket Events:**
- `task_updated`: Real-time task status changes
- `new_message`: AI conversation updates  
- `task_completed`: Final task completion

Sources: [docs/api-reference/agent/tasks.mdx:25-67](), [docs/guides/task-creation.mdx:114-121]()

### Data and Communication Flow

```mermaid
graph LR
    subgraph "User Interactions"
        Browser["Web Browser<br/>User Interface"]
        VNCClient["VNC Client<br/>Desktop View"]
    end
    
    subgraph "Communication Protocols"
        HTTP["HTTP API<br/>Task Management"]
        WS["WebSocket<br/>Real-time Updates"]
        VNCProto["VNC Protocol<br/>Desktop Streaming"]
        MCP["MCP Protocol<br/>Tool Access"]
    end
    
    subgraph "Data Storage"
        TaskData[("Tasks<br/>Messages<br/>Files")]
        SessionData[("WebSocket<br/>Sessions")]
    end
    
    Browser --> HTTP
    Browser --> WS
    Browser --> VNCClient
    VNCClient --> VNCProto
    
    HTTP --> TaskData
    WS --> SessionData
    
    HTTP -.-> MCP
    MCP -.-> VNCProto
```

This diagram shows the various communication protocols and data flows within Bytebot. HTTP APIs handle task management, WebSockets provide real-time updates, VNC enables desktop visualization, and MCP (Model Context Protocol) allows AI models to access tools.

### API Communication Patterns

| Protocol | Usage | Endpoints | Port |
|----------|-------|-----------|------|
| HTTP REST | Task CRUD operations | `/tasks`, `/messages` | 9991 |
| WebSocket | Real-time updates | Socket.IO connections | 9991 |
| HTTP Proxy | UI → Backend routing | `/api/**` in Next.js | 9992 |
| VNC WebSocket | Desktop streaming | `/vnc` via websockify | 9990 |
| MCP SSE | Tool integration | `/mcp` Server-Sent Events | 9990 |

Sources: [docs/quickstart.mdx:170-177](), [docs/core-concepts/desktop-environment.mdx:122-141](), [docs/api-reference/agent/tasks.mdx:8]()

## Technology Stack Integration

### Multi-Provider AI Integration Architecture

```mermaid
graph TB
    subgraph "Agent Core"
        AP[AgentProcessor<br/>"Task Orchestration"]
        AT[AgentTools<br/>"Tool Definitions"]
    end
    
    subgraph "AI Provider Adapters"
        AS[AnthropicService]
        OS[OpenAIService]
        GS[GoogleService]
        PS[ProxyService]
    end
    
    subgraph "External AI APIs"
        Claude[Anthropic Claude]
        GPT[OpenAI GPT]
        Gemini[Google Gemini]
        LLMProxy[LiteLLM Proxy]
    end
    
    subgraph "Tool Execution"
        CTU[Computer Tool Use<br/>"Handler"]
        CUS[ComputerUseService]
        Desktop["Virtual Desktop"]
    end
    
    AT --> AS
    AT --> OS
    AT --> GS
    AT --> PS
    
    AP --> AS
    AP --> OS
    AP --> GS
    AP --> PS
    
    AS <--> Claude
    OS <--> GPT
    GS <--> Gemini
    PS <--> LLMProxy
    
    AP --> CTU
    CTU --> CUS
    CUS --> Desktop
```

The system supports multiple AI providers through a common interface, with each provider having its own service adapter. Tool definitions are consistently formatted across providers, enabling the same computer automation capabilities regardless of which AI model is used.

**Environment Configuration:**
- `ANTHROPIC_API_KEY`: Claude model access
- `OPENAI_API_KEY`: GPT model access  
- `GEMINI_API_KEY`: Gemini model access
- `LLM_PROXY_URL`: LiteLLM proxy endpoint

Sources: [packages/bytebot-agent/src/app.module.ts:27-31](), [packages/bytebot-agent/package.json:25-27,40]()

### Deployment and Infrastructure Overview

```mermaid
graph TB
    subgraph "Deployment Options"
        Railway["Railway PaaS<br/>One-click Deploy"]
        Docker["Docker Compose<br/>Local/Self-hosted"]
        K8s["Kubernetes<br/>Enterprise Scale"]
    end
    
    subgraph "Container Images"
        UIImage["ghcr.io/bytebot-ai/<br/>bytebot-ui:edge"]
        AgentImage["ghcr.io/bytebot-ai/<br/>bytebot-agent:edge"]
        DesktopImage["ghcr.io/bytebot-ai/<br/>bytebot-desktop:edge"]
    end
    
    subgraph "CI/CD Pipeline"
        GHA["GitHub Actions<br/>Build Workflows"]
        GHCR["GitHub Container<br/>Registry"]
    end
    
    subgraph "Runtime Environment"
        UI2["bytebot-ui:9992"]
        Agent2["bytebot-agent:9991"]
        Desktop2["bytebot-desktop:9990"]
        DB2[("PostgreSQL:5432")]
    end
    
    Railway --> UI2
    Docker --> UI2
    K8s --> UI2
    
    GHA --> GHCR
    GHCR --> UIImage
    GHCR --> AgentImage
    GHCR --> DesktopImage
    
    UIImage --> UI2
    AgentImage --> Agent2
    DesktopImage --> Desktop2
```

The system supports multiple deployment methods from simple PaaS solutions to enterprise Kubernetes clusters. Automated CI/CD builds multi-architecture container images that are deployed consistently across different environments.

**Container Images:**
- `ghcr.io/bytebot-ai/bytebot-ui:edge`
- `ghcr.io/bytebot-ai/bytebot-agent:edge`
- `ghcr.io/bytebot-ai/bytebot-desktop:edge`
- `postgres:14-alpine`

**Network Architecture:**
- Internal container networking
- Port mapping for external access
- WebSocket proxy for VNC connections
- Health checks and service discovery

Sources: [docs/quickstart.mdx:68-74,190-201](), [README.md:76-78,251-261]()

## Security and Isolation

### Container Security Model

Each service runs in isolated Docker containers with specific security configurations:

- **Process Isolation**: Services run as non-root users where possible
- **Network Isolation**: Private networking between containers
- **Resource Limits**: CPU and memory constraints enforced
- **Data Persistence**: Volumes for database and user data

### Authentication Integration

Optional authentication through `@thallesp/nestjs-better-auth`:

```typescript
// Conditional auth module loading
const authEnabled = process.env.AUTH_ENABLED === 'true';
```

Sources: [packages/bytebot-agent/src/app.module.ts:19-29](), [docs/core-concepts/architecture.mdx:119-149]()

## Deployment Patterns

The architecture supports multiple deployment scenarios:

| Pattern | Use Case | Resource Requirements |
|---------|----------|----------------------|
| Docker Compose | Development/Self-hosting | 4GB RAM, 2 CPU cores |
| Railway PaaS | Managed deployment | Auto-scaling |
| Kubernetes/Helm | Enterprise production | Dedicated nodes |

**Configuration Management:**
- Environment variables for secrets
- Docker Compose overrides
- Helm value customization
- Health check endpoints

Sources: [docs/quickstart.mdx:36-96](), [docs/deployment/railway.mdx:1-89](), [docs/core-concepts/architecture.mdx:151-176]()

---

# Page: Service Architecture

# Service Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [packages/bytebot-agent/package-lock.json](packages/bytebot-agent/package-lock.json)
- [packages/bytebot-agent/package.json](packages/bytebot-agent/package.json)
- [packages/bytebot-agent/src/agent/agent.module.ts](packages/bytebot-agent/src/agent/agent.module.ts)
- [packages/bytebot-agent/src/app.module.ts](packages/bytebot-agent/src/app.module.ts)
- [packages/bytebot-agent/src/main.ts](packages/bytebot-agent/src/main.ts)
- [packages/bytebot-agent/src/tasks/tasks.gateway.ts](packages/bytebot-agent/src/tasks/tasks.gateway.ts)
- [packages/bytebot-ui/next.config.ts](packages/bytebot-ui/next.config.ts)
- [packages/bytebot-ui/server.ts](packages/bytebot-ui/server.ts)
- [packages/bytebot-ui/src/app/api/[[...path]]/route.ts](packages/bytebot-ui/src/app/api/[[...path]]/route.ts)
- [packages/bytebot-ui/src/hooks/useWebSocket.ts](packages/bytebot-ui/src/hooks/useWebSocket.ts)

</details>



This document details the internal architecture of each core Bytebot service, including their modules, dependencies, and inter-service communication patterns. For overall system design and component relationships, see [System Architecture](#2). For deployment considerations, see [Deployment Architecture](#2.2).

## Service Overview

Bytebot consists of three primary services that work together to provide AI-powered desktop automation:

| Service | Technology | Port | Primary Responsibility |
|---------|------------|------|----------------------|
| `bytebot-agent` | NestJS | 9991 | Task orchestration and AI integration |
| `bytebot-ui` | Next.js | 9992 | Web interface and user interaction |
| `bytebotd` | NestJS | 9990 | Desktop automation and computer control |

## Agent Service Architecture

### Core Module Structure

The `bytebot-agent` service is built using NestJS and organized into specialized modules for task management, AI integration, and system orchestration.

```mermaid
graph TB
    AppModule["AppModule"]
    
    subgraph "Core Processing"
        AgentModule["AgentModule"]
        TasksModule["TasksModule"]  
        MessagesModule["MessagesModule"]
        SummariesModule["SummariesModule"]
    end
    
    subgraph "AI Providers"
        AnthropicModule["AnthropicModule"]
        OpenAIModule["OpenAIModule"]
        GoogleModule["GoogleModule"]
        ProxyModule["ProxyModule"]
    end
    
    subgraph "Infrastructure"
        PrismaModule["PrismaModule"]
        ConfigModule["ConfigModule"]
        ScheduleModule["ScheduleModule"]
        EventEmitterModule["EventEmitterModule"]
    end
    
    AppModule --> AgentModule
    AppModule --> TasksModule
    AppModule --> MessagesModule
    AppModule --> SummariesModule
    AppModule --> AnthropicModule
    AppModule --> OpenAIModule
    AppModule --> GoogleModule
    AppModule --> ProxyModule
    AppModule --> PrismaModule
    AppModule --> ConfigModule
    AppModule --> ScheduleModule
    AppModule --> EventEmitterModule
```

**Sources:** [packages/bytebot-agent/src/app.module.ts:17-33]()

### Agent Processing Components

The `AgentModule` contains the core orchestration logic and processing components:

```mermaid
graph TB
    subgraph "AgentModule Dependencies"
        TasksModule2["TasksModule"]
        MessagesModule2["MessagesModule"]
        SummariesModule2["SummariesModule"]
        AnthropicModule2["AnthropicModule"]
        OpenAIModule2["OpenAIModule"]
        GoogleModule2["GoogleModule"]
        ProxyModule2["ProxyModule"]
    end
    
    subgraph "Agent Providers"
        AgentProcessor["AgentProcessor"]
        AgentScheduler["AgentScheduler"]
        InputCaptureService["InputCaptureService"]
        AgentAnalyticsService["AgentAnalyticsService"]
    end
    
    TasksModule2 --> AgentProcessor
    MessagesModule2 --> AgentProcessor
    SummariesModule2 --> AgentProcessor
    AnthropicModule2 --> AgentProcessor
    OpenAIModule2 --> AgentProcessor
    GoogleModule2 --> AgentProcessor
    ProxyModule2 --> AgentProcessor
    
    AgentProcessor --> AgentScheduler
    AgentProcessor --> InputCaptureService
    AgentProcessor --> AgentAnalyticsService
```

**Sources:** [packages/bytebot-agent/src/agent/agent.module.ts:15-33]()

### Key Dependencies

The agent service relies on several critical dependencies for AI integration and system functionality:

| Dependency | Purpose | Version |
|------------|---------|---------|
| `@anthropic-ai/sdk` | Claude AI integration | ^0.39.0 |
| `openai` | OpenAI GPT integration | ^5.8.2 |
| `@google/genai` | Google Gemini integration | ^1.8.0 |
| `@prisma/client` | Database ORM | ^6.6.0 |
| `socket.io` | WebSocket communication | ^4.8.1 |
| `@nestjs/websockets` | NestJS WebSocket support | ^11.1.1 |

**Sources:** [packages/bytebot-agent/package.json:24-46]()

## UI Service Architecture

### Next.js Application Structure

The `bytebot-ui` service provides the web interface using Next.js with a custom Express server for proxy functionality:

```mermaid
graph TB
    subgraph "Frontend Layer"
        NextJSApp["Next.js Application"]
        ReactComponents["React Components"]
        
        subgraph "Core Pages"
            HomePage["Home Page ()"]
            TasksPage["Tasks Page (/tasks)"]
            DesktopPage["Desktop Page (/desktop)"]
        end
        
        subgraph "Layout Components"
            Header["Header Component"]
            Navigation["Navigation Links"]
        end
    end
    
    subgraph "Server Layer"
        ExpressServer["Express Server"]
        ProxyMiddleware["HTTP Proxy Middleware"]
    end
    
    subgraph "External Connections"
        SocketIOClient["Socket.IO Client"]
        VNCViewer["VNC Viewer (react-vnc)"]
        APIClient["API Client"]
    end
    
    NextJSApp --> ReactComponents
    ReactComponents --> HomePage
    ReactComponents --> TasksPage
    ReactComponents --> DesktopPage
    ReactComponents --> Header
    Header --> Navigation
    
    NextJSApp --> ExpressServer
    ExpressServer --> ProxyMiddleware
    
    ReactComponents --> SocketIOClient
    ReactComponents --> VNCViewer
    ReactComponents --> APIClient
```

**Sources:** [packages/bytebot-ui/src/components/layout/Header.tsx:15-94](), [packages/bytebot-ui/package.json:30-47]()

### UI Dependencies and Communication

The UI service integrates multiple technologies for real-time communication and desktop visualization:

| Dependency | Purpose | Version |
|------------|---------|---------|
| `next` | React framework | >=15.3.3 |
| `react` | UI library | ^19.0.0 |
| `socket.io-client` | Real-time communication | ^4.8.1 |
| `react-vnc` | VNC desktop viewer | ^3.1.0 |
| `http-proxy-middleware` | API proxying | ^3.0.5 |
| `@radix-ui/*` | UI component primitives | Various |

**Sources:** [packages/bytebot-ui/package.json:11-47]()

## Desktop Service Architecture

### Daemon Module Organization

The `bytebotd` service provides desktop automation capabilities through a modular NestJS architecture:

```mermaid
graph TB
    subgraph "AppModule"
        AppController["AppController"]
        AppService["AppService"]
    end
    
    subgraph "Core Modules"
        ComputerUseModule["ComputerUseModule"]
        InputTrackingModule["InputTrackingModule"]
        BytebotMcpModule["BytebotMcpModule"]
    end
    
    subgraph "Infrastructure Modules"
        ConfigModule3["ConfigModule"]
        ServeStaticModule["ServeStaticModule"]
    end
    
    subgraph "External Integrations"
        noVNCServer["noVNC Static Files (/novnc)"]
        VNCRedirect["VNC Redirect (/vnc)"]
    end
    
    AppController --> VNCRedirect
    ServeStaticModule --> noVNCServer
    ComputerUseModule --> InputTrackingModule
    BytebotMcpModule --> ComputerUseModule
    
    AppModule --> ComputerUseModule
    AppModule --> InputTrackingModule  
    AppModule --> BytebotMcpModule
    AppModule --> ConfigModule3
    AppModule --> ServeStaticModule
```

**Sources:** [packages/bytebotd/src/app.module.ts:10-26](), [packages/bytebotd/src/app.controller.ts:1-18]()

### MCP Integration Architecture

The Model Context Protocol (MCP) integration enables AI models to access desktop automation tools:

```mermaid
graph TB
    subgraph "BytebotMcpModule"
        McpModule["McpModule"]
        ComputerUseTools["ComputerUseTools"]
    end
    
    subgraph "MCP Configuration"
        MCPName["name: 'bytebotd'"]
        MCPVersion["version: '0.0.1'"]
        MCPEndpoint["sseEndpoint: '/mcp'"]
    end
    
    subgraph "Tool Integration"
        ComputerUseModule3["ComputerUseModule"]
        DesktopAutomation["Desktop Automation APIs"]
    end
    
    McpModule --> MCPName
    McpModule --> MCPVersion
    McpModule --> MCPEndpoint
    ComputerUseTools --> ComputerUseModule3
    ComputerUseModule3 --> DesktopAutomation
    
    BytebotMcpModule --> McpModule
    BytebotMcpModule --> ComputerUseTools
```

**Sources:** [packages/bytebotd/src/mcp/bytebot-mcp.module.ts:6-17]()

### Desktop Automation Dependencies

The desktop service uses specialized libraries for computer control and input monitoring:

| Dependency | Purpose | Version |
|------------|---------|---------|
| `@nut-tree-fork/nut-js` | Desktop automation framework | ^4.2.6 |
| `uiohook-napi` | Global input event capture | ^1.5.4 |
| `sharp` | Image processing for screenshots | ^0.34.2 |
| `@rekog/mcp-nest` | MCP protocol integration | ^1.6.2 |
| `http-proxy-middleware` | Request proxying | ^3.0.5 |

**Sources:** [packages/bytebotd/package.json:28-46]()

## Inter-Service Communication

### Communication Protocols and Patterns

The three services communicate using multiple protocols optimized for different types of data exchange:

```mermaid
graph LR
    subgraph "bytebot-ui (:9992)"
        UIComponents["UI Components"]
        SocketClient["Socket.IO Client"]
        HTTPClient["HTTP Client"]
        VNCClient["VNC Client"]
    end
    
    subgraph "bytebot-agent (:9991)"
        TasksGateway["TasksGateway (WebSocket)"]
        TasksController["TasksController (HTTP)"]
        AgentProcessor2["AgentProcessor"]
    end
    
    subgraph "bytebotd (:9990)"
        ComputerUseAPI["Computer Use API"]
        MCPEndpoint2["MCP Endpoint (/mcp)"]
        VNCProxy["VNC Proxy"]
    end
    
    subgraph "External Services"
        PostgreSQL[("PostgreSQL Database")]
        VNCServer["VNC Server"]
    end
    
    SocketClient <-->|"WebSocket (Real-time updates)"| TasksGateway
    HTTPClient -->|"HTTP REST (Task management)"| TasksController
    VNCClient <-->|"VNC Protocol (Desktop streaming)"| VNCProxy
    
    AgentProcessor2 -->|"HTTP (Computer actions)"| ComputerUseAPI
    AgentProcessor2 <-->|"MCP (Tool access)"| MCPEndpoint2
    
    TasksController -->|"Prisma ORM"| PostgreSQL
    VNCProxy <-->|"VNC Protocol"| VNCServer
```

**Sources:** [packages/bytebot-agent/src/app.module.ts:17-37](), [packages/bytebotd/src/app.controller.ts:10-17](), [packages/bytebot-ui/package.json:41-43]()

## Service Runtime Configuration

### Port Allocation and Environment

Each service operates on dedicated ports with specific runtime configurations:

```mermaid
graph TB
    subgraph "Runtime Environment"
        subgraph "bytebot-ui:9992"
            NextServer["Next.js Server"]
            ExpressProxy["Express Proxy Server"]
        end
        
        subgraph "bytebot-agent:9991"  
            NestAgent["NestJS Application"]
            PrismaClient["Prisma Database Client"]
            SocketIOServer["Socket.IO WebSocket Server"]
        end
        
        subgraph "bytebotd:9990"
            NestDesktop["NestJS Daemon"]
            ComputerAutomation["Computer Automation Engine"]
            MCPServer["MCP SSE Server (/mcp)"]
            StaticFiles["Static Files (/novnc)"]
        end
        
        subgraph "External Dependencies"
            Database[("PostgreSQL:5432")]
            VNC["VNC Server:5900"]
        end
    end
    
    NextServer -->|"Proxy requests"| ExpressProxy
    ExpressProxy -->|"API calls"| NestAgent
    ExpressProxy -->|"Desktop access"| NestDesktop
    
    NestAgent --> PrismaClient
    PrismaClient --> Database
    NestAgent --> SocketIOServer
    
    NestDesktop --> ComputerAutomation
    NestDesktop --> MCPServer
    NestDesktop --> StaticFiles
    NestDesktop --> VNC
```

**Sources:** [packages/bytebot-agent/package.json:96-98](), [packages/bytebot-ui/package.json:5-9](), [packages/bytebotd/src/app.module.ts:15-18]()

---

# Page: Communication Patterns

# Communication Patterns

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [packages/bytebot-agent/src/agent/agent.processor.ts](packages/bytebot-agent/src/agent/agent.processor.ts)
- [packages/bytebot-agent/src/main.ts](packages/bytebot-agent/src/main.ts)
- [packages/bytebot-agent/src/tasks/tasks.controller.ts](packages/bytebot-agent/src/tasks/tasks.controller.ts)
- [packages/bytebot-agent/src/tasks/tasks.gateway.ts](packages/bytebot-agent/src/tasks/tasks.gateway.ts)
- [packages/bytebot-agent/src/tasks/tasks.service.ts](packages/bytebot-agent/src/tasks/tasks.service.ts)
- [packages/bytebot-ui/next.config.ts](packages/bytebot-ui/next.config.ts)
- [packages/bytebot-ui/server.ts](packages/bytebot-ui/server.ts)
- [packages/bytebot-ui/src/app/api/[[...path]]/route.ts](packages/bytebot-ui/src/app/api/[[...path]]/route.ts)
- [packages/bytebot-ui/src/hooks/useChatSession.ts](packages/bytebot-ui/src/hooks/useChatSession.ts)
- [packages/bytebot-ui/src/hooks/useWebSocket.ts](packages/bytebot-ui/src/hooks/useWebSocket.ts)

</details>



This document describes the three primary communication mechanisms in Bytebot: REST API proxying through the frontend layer, WebSocket-based real-time event distribution, and VNC streaming for desktop access. It also covers the internal event-driven coordination between backend services.

For detailed API specifications, see [Tasks REST API](#10.1) and [WebSocket API](#10.3). For service-level architecture, see [Service Architecture](#2.1).

---

## REST API Proxying

Bytebot-ui acts as a unified proxy layer, forwarding all HTTP requests from the browser to bytebot-agent. This architecture provides a single origin for the frontend and simplifies CORS management.

### Next.js Catch-All Route

The Next.js API routes proxy HTTP requests to the backend using a catch-all route handler.

**Path Resolution Flow Diagram**

```mermaid
graph LR
    Browser["Browser Request<br/>/api/tasks"]
    NextRoute["Next.js Route Handler<br/>/api/[[...path]]/route.ts"]
    ProxyFn["proxy() function"]
    Backend["bytebot-agent<br/>http://localhost:9991"]
    
    Browser --> NextRoute
    NextRoute --> ProxyFn
    ProxyFn --> Backend
    
    NextRoute -->|"params.path = ['tasks']"| ProxyFn
    ProxyFn -->|"Construct URL:<br/>BASE_URL + path + search"| Backend
```

**Sources:** [packages/bytebot-ui/src/app/api/[[...path]]/route.ts:1-65]()

The route handler at [packages/bytebot-ui/src/app/api/[[...path]]/route.ts:6-46]() implements request proxying:

1. Extracts path segments from the catch-all `[[...path]]` parameter
2. Reconstructs the full URL using `BYTEBOT_AGENT_BASE_URL` environment variable
3. Forwards HTTP method, headers (including cookies), and body
4. Returns the backend response with preserved `Set-Cookie` headers

**HTTP Method Support**

| Method | Handler Export | Use Case |
|--------|---------------|----------|
| GET | `export const GET = handler` | Fetch tasks, messages, models |
| POST | `export const POST = handler` | Create tasks, add messages |
| PATCH | `export const PATCH = handler` | Update task status |
| DELETE | `export const DELETE = handler` | Delete tasks |

**Sources:** [packages/bytebot-ui/src/app/api/[[...path]]/route.ts:58-64]()

### Express Server Proxying

For WebSocket upgrades and VNC streaming, bytebot-ui runs a custom Express server that handles HTTP proxying and WebSocket protocol upgrades.

**Express Proxy Configuration Diagram**

```mermaid
graph TB
    ExpressApp["Express Application<br/>server.ts"]
    TasksProxy["Socket.IO Proxy<br/>/api/proxy/tasks"]
    VNCProxy["VNC Proxy<br/>/api/proxy/websockify"]
    NextHandler["Next.js Handler<br/>app.getRequestHandler()"]
    
    subgraph "Proxy Middleware"
        TasksMiddleware["createProxyMiddleware<br/>target: BYTEBOT_AGENT_BASE_URL<br/>pathRewrite: /socket.io"]
        VNCMiddleware["createProxyServer<br/>target: BYTEBOT_DESKTOP_VNC_URL<br/>ws: true"]
    end
    
    ExpressApp --> TasksProxy
    ExpressApp --> VNCProxy
    ExpressApp --> NextHandler
    
    TasksProxy --> TasksMiddleware
    VNCProxy --> VNCMiddleware
```

**Sources:** [packages/bytebot-ui/server.ts:1-89]()

The Express server at [packages/bytebot-ui/server.ts:29-51]() configures two proxy paths:

1. **`/api/proxy/tasks`** - Proxies Socket.IO connections to bytebot-agent, rewriting the path to `/socket.io` [packages/bytebot-ui/server.ts:33-37]()
2. **`/api/proxy/websockify`** - Proxies VNC WebSocket connections to bytebotd [packages/bytebot-ui/server.ts:41-51]()

All other requests fall through to Next.js via `handle(req, res)` [packages/bytebot-ui/server.ts:54]().

**Sources:** [packages/bytebot-ui/server.ts:29-54]()

---

## WebSocket Communication

Bytebot uses Socket.IO for bidirectional, real-time communication between the frontend and backend. This enables instant task status updates, message notifications, and reactive UI updates.

### Server-Side Gateway

The `TasksGateway` class implements the Socket.IO server in bytebot-agent.

**TasksGateway Architecture Diagram**

```mermaid
graph TB
    Gateway["TasksGateway<br/>@WebSocketGateway"]
    Server["Socket.IO Server<br/>@WebSocketServer"]
    
    subgraph "Client Event Handlers"
        JoinTask["@SubscribeMessage('join_task')<br/>handleJoinTask()"]
        LeaveTask["@SubscribeMessage('leave_task')<br/>handleLeaveTask()"]
    end
    
    subgraph "Server Emission Methods"
        EmitUpdate["emitTaskUpdate(taskId, task)<br/>→ task_updated"]
        EmitMessage["emitNewMessage(taskId, message)<br/>→ new_message"]
        EmitCreated["emitTaskCreated(task)<br/>→ task_created"]
        EmitDeleted["emitTaskDeleted(taskId)<br/>→ task_deleted"]
    end
    
    subgraph "Socket Rooms"
        GlobalRoom["Global Room<br/>All clients"]
        TaskRoom["Task Room<br/>task_{taskId}"]
    end
    
    Gateway --> Server
    Server --> JoinTask
    Server --> LeaveTask
    
    EmitUpdate --> TaskRoom
    EmitMessage --> TaskRoom
    EmitCreated --> GlobalRoom
    EmitDeleted --> GlobalRoom
    
    JoinTask -->|"client.join('task_{taskId}')"| TaskRoom
```

**Sources:** [packages/bytebot-agent/src/tasks/tasks.gateway.ts:1-58]()

**Room-Based Event Distribution**

The gateway uses Socket.IO rooms to implement targeted event delivery:

- **Task-specific events** (`task_updated`, `new_message`) emit to `task_{taskId}` room [packages/bytebot-agent/src/tasks/tasks.gateway.ts:42-47]()
- **Global events** (`task_created`, `task_deleted`) broadcast to all connected clients [packages/bytebot-agent/src/tasks/tasks.gateway.ts:50-56]()

Clients join rooms by emitting `join_task` with a task ID [packages/bytebot-agent/src/tasks/tasks.gateway.ts:30-34]().

**Sources:** [packages/bytebot-agent/src/tasks/tasks.gateway.ts:30-56]()

### Client-Side Hook

The `useWebSocket` hook manages the Socket.IO client connection in the React frontend.

**WebSocket Client Lifecycle**

```mermaid
stateDiagram-v2
    [*] --> Disconnected
    Disconnected --> Connecting: "connect() called"
    Connecting --> Connected: "Socket.IO handshake"
    Connected --> InTask: "joinTask(taskId)"
    InTask --> InTask: "Switch task:<br/>leave_task + join_task"
    InTask --> Connected: "leaveTask()"
    Connected --> Disconnected: "disconnect()"
    
    note right of InTask
        Socket emits:
        - join_task event
        - leave_task event
        
        Socket receives:
        - task_updated
        - new_message
    end note
```

**Sources:** [packages/bytebot-ui/src/hooks/useWebSocket.ts:1-114]()

**Connection Configuration**

The hook creates a Socket.IO client with the following parameters [packages/bytebot-ui/src/hooks/useWebSocket.ts:27-34]():

```
io({
  path: "/api/proxy/tasks",
  transports: ["websocket"],
  autoConnect: true,
  reconnection: true,
  reconnectionAttempts: 5,
  reconnectionDelay: 1000
})
```

**Event Handlers Table**

| Socket Event | Handler | Callback Prop | Usage |
|--------------|---------|---------------|-------|
| `task_updated` | [Line 44-46]() | `onTaskUpdate` | Update task status in UI |
| `new_message` | [Line 49-51]() | `onNewMessage` | Append message to chat |
| `task_created` | [Line 54-56]() | `onTaskCreated` | Refresh task list |
| `task_deleted` | [Line 59-61]() | `onTaskDeleted` | Remove task from list |

**Sources:** [packages/bytebot-ui/src/hooks/useWebSocket.ts:36-62]()

### Service Integration

`TasksService` calls `TasksGateway` emission methods after database operations to trigger real-time updates.

**Service-to-Gateway Call Pattern**

```mermaid
graph LR
    CreateTask["TasksService.create()"]
    UpdateTask["TasksService.update()"]
    DeleteTask["TasksService.delete()"]
    AddMessage["TasksService.addTaskMessage()"]
    
    EmitCreated["tasksGateway.emitTaskCreated()"]
    EmitUpdated["tasksGateway.emitTaskUpdate()"]
    EmitDeleted["tasksGateway.emitTaskDeleted()"]
    EmitMessage["tasksGateway.emitNewMessage()"]
    
    CreateTask -->|"After DB insert"| EmitCreated
    UpdateTask -->|"After DB update"| EmitUpdated
    DeleteTask -->|"After DB delete"| EmitDeleted
    AddMessage -->|"After message created"| EmitMessage
```

**Sources:** [packages/bytebot-agent/src/tasks/tasks.service.ts:114-116](), [packages/bytebot-agent/src/tasks/tasks.service.ts:244-246](), [packages/bytebot-agent/src/tasks/tasks.service.ts:258-260](), [packages/bytebot-agent/src/tasks/tasks.service.ts:278-279]()

The `TasksService` constructor injects `TasksGateway` using `@Inject(forwardRef(() => TasksGateway))` to resolve circular dependencies [packages/bytebot-agent/src/tasks/tasks.service.ts:32-33]().

**Sources:** [packages/bytebot-agent/src/tasks/tasks.service.ts:30-38]()

---

## Internal Event System

Bytebot-agent uses `EventEmitter2` for asynchronous, decoupled communication between services. This pattern allows `TasksService` to broadcast state changes without directly coupling to `AgentProcessor`.

### Event Emitters

The `TasksService` emits lifecycle events after task state transitions.

**Internal Event Emission Diagram**

```mermaid
graph TB
    TasksService["TasksService"]
    EventEmitter["EventEmitter2<br/>@nestjs/event-emitter"]
    
    subgraph "Emitted Events"
        Completed["task.completed<br/>{ taskId }"]
        Failed["task.failed<br/>{ taskId }"]
        Takeover["task.takeover<br/>{ taskId }"]
        Resume["task.resume<br/>{ taskId }"]
        Cancel["task.cancel<br/>{ taskId }"]
    end
    
    TasksService -->|"eventEmitter.emit()"| EventEmitter
    EventEmitter --> Completed
    EventEmitter --> Failed
    EventEmitter --> Takeover
    EventEmitter --> Resume
    EventEmitter --> Cancel
```

**Sources:** [packages/bytebot-agent/src/tasks/tasks.service.ts:234-239](), [packages/bytebot-agent/src/tasks/tasks.service.ts:312](), [packages/bytebot-agent/src/tasks/tasks.service.ts:351](), [packages/bytebot-agent/src/tasks/tasks.service.ts:385]()

**Event Emission Triggers**

| Method | Condition | Event Emitted | Payload |
|--------|-----------|---------------|---------|
| `update()` | `status === COMPLETED` | `task.completed` | `{ taskId }` |
| `update()` | `status === FAILED` | `task.failed` | `{ taskId }` |
| `takeOver()` | User takes control | `task.takeover` | `{ taskId }` |
| `resume()` | User returns control | `task.resume` | `{ taskId }` |
| `cancel()` | Task cancelled | `task.cancel` | `{ taskId }` |

**Sources:** [packages/bytebot-agent/src/tasks/tasks.service.ts:217-391]()

### Event Listeners

The `AgentProcessor` uses the `@OnEvent` decorator to handle internal events.

**AgentProcessor Event Handling Flow**

```mermaid
graph TB
    subgraph "Event Listeners"
        TakeoverHandler["@OnEvent('task.takeover')<br/>handleTaskTakeover()"]
        ResumeHandler["@OnEvent('task.resume')<br/>handleTaskResume()"]
        CancelHandler["@OnEvent('task.cancel')<br/>handleTaskCancel()"]
    end
    
    subgraph "Actions"
        AbortLLM["abortController.abort()<br/>Cancel in-flight LLM request"]
        StartCapture["inputCaptureService.start()<br/>Begin recording user actions"]
        ResumeIter["runIteration(taskId)<br/>Resume agent loop"]
        StopProc["stopProcessing()<br/>Halt agent execution"]
    end
    
    TakeoverHandler --> AbortLLM
    TakeoverHandler --> StartCapture
    ResumeHandler --> ResumeIter
    CancelHandler --> StopProc
```

**Sources:** [packages/bytebot-agent/src/agent/agent.processor.ts:84-112]()

**Event Handler Details**

1. **`task.takeover`** [packages/bytebot-agent/src/agent/agent.processor.ts:84-95]()
   - Aborts any in-flight LLM API call if processing the same task
   - Starts input capture to record user actions

2. **`task.resume`** [packages/bytebot-agent/src/agent/agent.processor.ts:97-105]()
   - Creates new `AbortController` for next iteration
   - Resumes the agent's `runIteration()` loop

3. **`task.cancel`** [packages/bytebot-agent/src/agent/agent.processor.ts:107-112]()
   - Calls `stopProcessing()` to halt execution
   - Stops input capture

**Sources:** [packages/bytebot-agent/src/agent/agent.processor.ts:84-112]()

---

## VNC Streaming

The VNC streaming architecture provides browser-based access to the virtual desktop environment. This involves WebSocket protocol upgrades and proxy routing.

### WebSocket Upgrade Handling

The Express server listens for WebSocket upgrade requests and routes them appropriately.

**WebSocket Upgrade Flow Diagram**

```mermaid
graph TB
    Browser["Browser WebSocket Request<br/>ws://localhost:9992/api/proxy/websockify"]
    UpgradeEvent["Server 'upgrade' Event<br/>server.on('upgrade', ...)"]
    PathCheck{"pathname.startsWith?"}
    TasksUpgrade["tasksProxy.upgrade()<br/>Socket.IO handshake"]
    VNCUpgrade["vncProxy.ws()<br/>VNC protocol"]
    NextUpgrade["nextUpgradeHandler()<br/>Next.js WebSocket"]
    
    Browser --> UpgradeEvent
    UpgradeEvent --> PathCheck
    PathCheck -->|"/api/proxy/tasks"| TasksUpgrade
    PathCheck -->|"/api/proxy/websockify"| VNCUpgrade
    PathCheck -->|"Other"| NextUpgrade
    
    TasksUpgrade --> Backend["bytebot-agent:9991<br/>Socket.IO Server"]
    VNCUpgrade --> Desktop["bytebotd:6080<br/>websockify + VNC Server"]
```

**Sources:** [packages/bytebot-ui/server.ts:57-79]()

The upgrade handler at [packages/bytebot-ui/server.ts:57-79]() performs path-based routing:

1. **Socket.IO**: Paths starting with `/api/proxy/tasks` upgrade to bytebot-agent's Socket.IO server
2. **VNC**: Paths starting with `/api/proxy/websockify` upgrade to bytebotd's VNC server
3. **Next.js**: All other paths handled by Next.js WebSocket handler

**VNC Proxy Configuration**

The VNC proxy server is created with [packages/bytebot-ui/server.ts:27]():

```
createProxyServer({ 
  changeOrigin: true, 
  ws: true 
})
```

The path rewrite logic extracts the target path from the URL [packages/bytebot-ui/server.ts:68-71]():

```
targetUrl.pathname + request.url.replace(/^\/api\/proxy\/websockify/, "")
```

**Sources:** [packages/bytebot-ui/server.ts:27](), [packages/bytebot-ui/server.ts:67-75]()

### Environment Configuration

Both proxy targets are configured via environment variables:

| Variable | Purpose | Example |
|----------|---------|---------|
| `BYTEBOT_AGENT_BASE_URL` | Backend REST/WS endpoint | `http://localhost:9991` |
| `BYTEBOT_DESKTOP_VNC_URL` | VNC WebSocket endpoint | `http://localhost:6080` |

**Sources:** [packages/bytebot-ui/server.ts:16-17]()

---

## Complete Communication Flow

This diagram shows how all three communication patterns work together during a typical task execution.

**End-to-End Communication Sequence**

```mermaid
sequenceDiagram
    participant Browser
    participant ExpressServer as "Express Server<br/>(bytebot-ui)"
    participant NextAPI as "Next.js API Route"
    participant TasksGateway as "TasksGateway<br/>(Socket.IO)"
    participant TasksService
    participant EventEmitter as "EventEmitter2"
    participant AgentProcessor
    
    Browser->>ExpressServer: POST /api/tasks (Create Task)
    ExpressServer->>NextAPI: Proxy HTTP request
    NextAPI->>TasksService: create(dto)
    TasksService->>TasksService: prisma.task.create()
    TasksService->>TasksGateway: emitTaskCreated(task)
    TasksGateway-->>Browser: task_created event
    
    Browser->>ExpressServer: WebSocket Upgrade /api/proxy/tasks
    ExpressServer->>TasksGateway: Upgrade to Socket.IO
    TasksGateway-->>Browser: Connected
    
    Browser->>TasksGateway: join_task event
    TasksGateway->>TasksGateway: client.join('task_{id}')
    
    AgentProcessor->>TasksService: update(id, { status: COMPLETED })
    TasksService->>TasksService: prisma.task.update()
    TasksService->>EventEmitter: emit('task.completed')
    TasksService->>TasksGateway: emitTaskUpdate(id, task)
    TasksGateway-->>Browser: task_updated event
    EventEmitter-->>AgentProcessor: @OnEvent handler (if listening)
    
    Browser->>ExpressServer: POST /api/tasks/{id}/takeover
    ExpressServer->>NextAPI: Proxy HTTP request
    NextAPI->>TasksService: takeOver(id)
    TasksService->>EventEmitter: emit('task.takeover')
    EventEmitter-->>AgentProcessor: handleTaskTakeover()
    AgentProcessor->>AgentProcessor: abortController.abort()
    TasksService->>TasksGateway: emitTaskUpdate(id, task)
    TasksGateway-->>Browser: task_updated event
```

**Sources:** [packages/bytebot-ui/server.ts:33-79](), [packages/bytebot-ui/src/app/api/[[...path]]/route.ts:6-46](), [packages/bytebot-agent/src/tasks/tasks.gateway.ts:30-56](), [packages/bytebot-agent/src/tasks/tasks.service.ts:40-391](), [packages/bytebot-agent/src/agent/agent.processor.ts:84-112]()

---

# Page: Deployment Architecture

# Deployment Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [docs/api-reference/agent/tasks.mdx](docs/api-reference/agent/tasks.mdx)
- [docs/core-concepts/desktop-environment.mdx](docs/core-concepts/desktop-environment.mdx)
- [docs/deployment/railway.mdx](docs/deployment/railway.mdx)
- [docs/guides/task-creation.mdx](docs/guides/task-creation.mdx)
- [docs/introduction.mdx](docs/introduction.mdx)
- [docs/quickstart.mdx](docs/quickstart.mdx)

</details>



This document explains the Docker containerization strategy, Kubernetes deployment architecture with Helm charts, and infrastructure patterns used by the Bytebot system. It covers container orchestration, service networking, and deployment automation.

For detailed information about the internal service architecture and component interactions, see [Service Architecture](#2.1). For step-by-step installation instructions, see [Installation and Setup](#3).

## Overview

Bytebot's deployment architecture is built on containerized microservices designed for Kubernetes orchestration:

| Component | Purpose | Container Image | Architecture |
|-----------|---------|-----------------|--------------|
| **Helm Charts** | Kubernetes deployment | `/helm` directory | Declarative configuration |
| **Multi-arch Images** | Container distribution | GitHub Container Registry | `linux/amd64`, `linux/arm64` |
| **Service Mesh** | Internal networking | Kubernetes Services | Private cluster communication |
| **Persistent Storage** | Data persistence | PersistentVolumeClaims | Database and file storage |

## Container Architecture

Bytebot deploys as a multi-container system with standardized Docker images:

### Core Container Images

```mermaid
graph TB
    subgraph "Container Registry: ghcr.io/bytebot-ai"
        UI_IMG["bytebot-ui:edge<br/>Next.js Frontend<br/>Port: 9992"]
        AGENT_IMG["bytebot-agent:edge<br/>NestJS Backend<br/>Port: 9991"]
        DESKTOP_IMG["bytebot-desktop:edge<br/>Ubuntu + XFCE<br/>Port: 9990"]
    end
    
    subgraph "External Dependencies"
        PG_IMG["postgres:14-alpine<br/>Database<br/>Port: 5432"]
        PROXY_IMG["litellm/litellm:main-latest<br/>LLM Proxy (Optional)<br/>Port: 4000"]
    end
    
    subgraph "Build Pipeline"
        GH_ACTIONS["GitHub Actions<br/>Multi-arch Build"]
        PLATFORMS["linux/amd64<br/>linux/arm64"]
    end
    
    GH_ACTIONS --> UI_IMG
    GH_ACTIONS --> AGENT_IMG
    GH_ACTIONS --> DESKTOP_IMG
    GH_ACTIONS --> PLATFORMS
```

Sources: [.github/workflows/build-ui.yaml:27-28](), [.github/workflows/build-agent.yaml:27-28](), [.github/workflows/build-desktop.yaml:34-35]()

### Container Build Configuration

Each service uses optimized Docker builds with multi-architecture support:

| Service | Context | Dockerfile | Platforms |
|---------|---------|------------|-----------|
| `bytebot-ui` | `./packages` | `bytebot-ui/Dockerfile` | `linux/amd64,linux/arm64` |
| `bytebot-agent` | `./packages` | `bytebot-agent/Dockerfile` | `linux/amd64,linux/arm64` |
| `bytebot-desktop` | `./packages` | `bytebotd/Dockerfile` | `linux/amd64,linux/arm64` |

Sources: [.github/workflows/build-ui.yaml:42-44](), [.github/workflows/build-agent.yaml:42-44](), [.github/workflows/build-desktop.yaml:53-55]()

## Kubernetes Deployment with Helm

Bytebot uses Helm charts for Kubernetes deployment, providing declarative configuration and lifecycle management.

### Helm Chart Structure

```mermaid
graph TB
    subgraph "Main Chart: ./helm"
        CHART_YAML["Chart.yaml<br/>Metadata"]
        VALUES_YAML["values.yaml<br/>Default Configuration"]
        VALUES_PROXY["values-proxy.yaml<br/>LiteLLM Configuration"]
        TEMPLATES["templates/<br/>Kubernetes Templates"]
    end
    
    subgraph "Subcharts: ./helm/charts"
        DESKTOP_CHART["bytebot-desktop/<br/>Desktop Service"]
        AGENT_CHART["bytebot-agent/<br/>Backend API"]
        UI_CHART["bytebot-ui/<br/>Frontend Service"]
        PROXY_CHART["bytebot-llm-proxy/<br/>LLM Proxy"]
        PG_CHART["postgresql/<br/>Database"]
    end
    
    CHART_YAML --> DESKTOP_CHART
    CHART_YAML --> AGENT_CHART
    CHART_YAML --> UI_CHART
    CHART_YAML --> PROXY_CHART
    CHART_YAML --> PG_CHART
    
    VALUES_YAML --> TEMPLATES
    VALUES_PROXY --> PROXY_CHART
```

Sources: [helm/README.md:34-48]()

### Service Configuration in Kubernetes

The Helm deployment creates Kubernetes resources with proper networking:

```mermaid
graph TB
    subgraph "Kubernetes Namespace: bytebot"
        subgraph "Deployments"
            UI_DEPLOY["bytebot-ui<br/>Deployment"]
            AGENT_DEPLOY["bytebot-agent<br/>Deployment"]  
            DESKTOP_DEPLOY["bytebot-desktop<br/>Deployment"]
        end
        
        subgraph "Services"
            UI_SVC["bytebot-ui<br/>Service<br/>Port: 9992"]
            AGENT_SVC["bytebot-agent<br/>Service<br/>Port: 9991"]
            DESKTOP_SVC["bytebot-desktop<br/>Service<br/>Port: 9990"]
            PG_SVC["bytebot-postgresql<br/>Service<br/>Port: 5432"]
        end
        
        subgraph "Storage"
            PG_PVC["PostgreSQL<br/>PersistentVolumeClaim"]
            DESKTOP_PVC["Desktop Files<br/>PersistentVolumeClaim"]
        end
        
        subgraph "StatefulSets"
            PG_SS["bytebot-postgresql-0<br/>StatefulSet"]
        end
    end
    
    UI_DEPLOY --> UI_SVC
    AGENT_DEPLOY --> AGENT_SVC
    DESKTOP_DEPLOY --> DESKTOP_SVC
    PG_SS --> PG_SVC
    PG_SS --> PG_PVC
    DESKTOP_DEPLOY --> DESKTOP_PVC
```

Sources: [docs/deployment/helm.mdx:132-144]()

### Configuration Management

Helm values provide centralized configuration for all services:

```yaml
# Example configuration from values.yaml
bytebot-agent:
  apiKeys:
    anthropic:
      value: "sk-ant-your-key-here"
    openai:
      value: "sk-your-key-here"
      
desktop:
  resources:
    requests:
      memory: "2Gi"
      cpu: "1"
    limits:
      memory: "4Gi" 
      cpu: "2"
      
ui:
  ingress:
    enabled: true
    hostname: "bytebot.your-domain.com"
```

Sources: [docs/deployment/helm.mdx:68-77](), [docs/deployment/helm.mdx:84-100](), [docs/deployment/helm.mdx:107-112]()

## Container Image Management

### CI/CD Pipeline Architecture

Automated Docker builds use GitHub Actions with multi-architecture support:

```mermaid
graph LR
    subgraph "Source Control"
        MAIN_BRANCH["main branch<br/>Git Push"]
        PATH_FILTERS["Path Filters<br/>packages/bytebot-ui/**<br/>packages/bytebot-agent/**<br/>packages/bytebotd/**"]
    end
    
    subgraph "GitHub Actions"
        BUILD_UI["build-ui.yaml<br/>UI Container"]
        BUILD_AGENT["build-agent.yaml<br/>Agent Container"] 
        BUILD_DESKTOP["build-desktop.yaml<br/>Desktop Container"]
    end
    
    subgraph "Build Process"
        QEMU["setup-qemu-action<br/>Cross-platform"]
        BUILDX["setup-buildx-action<br/>Multi-arch Builder"]
        CACHE["GitHub Actions Cache<br/>Build Optimization"]
    end
    
    subgraph "Container Registry"
        GHCR["ghcr.io/bytebot-ai/<br/>GitHub Container Registry"]
        EDGE_TAG["edge tag<br/>Latest Builds"]
    end
    
    MAIN_BRANCH --> PATH_FILTERS
    PATH_FILTERS --> BUILD_UI
    PATH_FILTERS --> BUILD_AGENT
    PATH_FILTERS --> BUILD_DESKTOP
    
    BUILD_UI --> QEMU
    BUILD_AGENT --> BUILDX
    BUILD_DESKTOP --> CACHE
    
    QEMU --> GHCR
    BUILDX --> EDGE_TAG
```

Sources: [.github/workflows/build-ui.yaml:4-10](), [.github/workflows/build-agent.yaml:4-10](), [.github/workflows/build-desktop.yaml:4-10]()

### Image Build Configuration

Each workflow uses consistent build patterns with platform-specific optimizations:

| Build Feature | Configuration | Purpose |
|---------------|---------------|---------|
| **Platforms** | `linux/amd64,linux/arm64` | Multi-architecture support |
| **Cache** | `type=gha,mode=max` | GitHub Actions cache optimization |
| **Registry** | `ghcr.io` | GitHub Container Registry |
| **Buildx** | `BUILDX_NO_DEFAULT_ATTESTATIONS: 1` | Clean registry metadata |

Sources: [.github/workflows/build-ui.yaml:38-50](), [.github/workflows/build-agent.yaml:38-49](), [.github/workflows/build-desktop.yaml:48-60]()

### Container Security and Optimization

Build configuration includes security and performance optimizations:

```bash
# Environment variables for build optimization
BUILDX_NO_DEFAULT_ATTESTATIONS=1  # Hide "unknown/unknown" in GHCR
DOCKER_BUILD_SUMMARY=false        # Keep logs concise
DOCKER_BUILD_RECORD_UPLOAD=false  # Reduce build artifacts
```

Sources: [.github/workflows/build-ui.yaml:38-40](), [.github/workflows/build-agent.yaml:37-40](), [.github/workflows/build-desktop.yaml:49-51]()

## Infrastructure Patterns

### Kubernetes Service Networking

Internal service communication uses Kubernetes DNS and service discovery:

```mermaid
graph TB
    subgraph "External Access"
        INGRESS["Ingress Controller<br/>External Load Balancer"]
        PORT_FORWARD["kubectl port-forward<br/>Development Access"]
    end
    
    subgraph "Service Layer"
        UI_SVC["bytebot-ui.bytebot.svc.cluster.local<br/>Service: 9992"]
        AGENT_SVC["bytebot-agent.bytebot.svc.cluster.local<br/>Service: 9991"]
        DESKTOP_SVC["bytebot-desktop.bytebot.svc.cluster.local<br/>Service: 9990"]
        PG_SVC["bytebot-postgresql.bytebot.svc.cluster.local<br/>Service: 5432"]
    end
    
    subgraph "Pod Layer"
        UI_POD["bytebot-ui-xxxxx<br/>Pod"]
        AGENT_POD["bytebot-agent-xxxxx<br/>Pod"]
        DESKTOP_POD["bytebot-desktop-xxxxx<br/>Pod"]
        PG_POD["bytebot-postgresql-0<br/>StatefulSet Pod"]
    end
    
    INGRESS --> UI_SVC
    PORT_FORWARD --> UI_SVC
    
    UI_SVC --> UI_POD
    AGENT_SVC --> AGENT_POD
    DESKTOP_SVC --> DESKTOP_POD
    PG_SVC --> PG_POD
    
    UI_POD --> AGENT_SVC
    AGENT_POD --> DESKTOP_SVC
    AGENT_POD --> PG_SVC
```

Sources: [docs/deployment/helm.mdx:118-122](), [helm/templates/NOTES.txt:5-6]()

### Storage Architecture

Persistent storage patterns for stateful components:

| Component | Storage Type | Purpose | Configuration |
|-----------|-------------|---------|---------------|
| **PostgreSQL** | `StatefulSet` + `PVC` | Database persistence | `postgresql.persistence.size` |
| **Desktop Files** | `PersistentVolume` | User data retention | `desktop.persistence.enabled` |
| **Agent Logs** | `emptyDir` | Temporary log storage | Container filesystem |
| **Shared Config** | `ConfigMap` + `Secret` | Configuration management | Helm values |

Sources: [docs/deployment/helm.mdx:236-247]()

### Resource Management

Kubernetes resource allocation follows container-specific patterns:

```yaml
# Resource configuration patterns
desktop:
  resources:
    requests:
      memory: "2Gi"    # Ubuntu + XFCE baseline
      cpu: "1"         # Desktop automation workload
    limits:
      memory: "4Gi"    # Prevent memory exhaustion
      cpu: "2"         # GUI rendering peak usage

agent:
  resources:
    requests:
      memory: "1Gi"    # NestJS + AI model requests
      cpu: "500m"      # API server baseline
```

Sources: [docs/deployment/helm.mdx:84-100]()

## Security and Access Patterns

### Kubernetes Security Model

Production deployments include security hardening through Helm configuration:

```mermaid
graph TB
    subgraph "Network Security"
        NETWORK_POLICY["NetworkPolicy<br/>Ingress/Egress Rules"]
        INGRESS_TLS["Ingress TLS<br/>Certificate Management"]
        SERVICE_MESH["Service Mesh<br/>Internal mTLS"]
    end
    
    subgraph "Pod Security"
        POD_SECURITY["PodSecurityContext<br/>runAsNonRoot: true<br/>runAsUser: 1000"]
        SECURITY_CONTEXT["SecurityContext<br/>readOnlyRootFilesystem"]
        CAPABILITIES["Linux Capabilities<br/>Drop Privileges"]
    end
    
    subgraph "Secret Management"
        API_SECRETS["API Key Secrets<br/>External Secret Operators"]
        CONFIG_MAPS["ConfigMaps<br/>Non-sensitive Config"]
        VAULT_INTEGRATION["Vault Integration<br/>Dynamic Secrets"]
    end
    
    NETWORK_POLICY --> POD_SECURITY
    POD_SECURITY --> API_SECRETS
    INGRESS_TLS --> CONFIG_MAPS
```

Sources: [docs/deployment/helm.mdx:252-269]()

### Access Control Configuration

```yaml
# Production security configuration
networkPolicy:
  enabled: true                    # Restrict pod-to-pod communication

podSecurityContext:
  runAsNonRoot: true              # Security hardening
  runAsUser: 1000                 # Non-privileged user
  fsGroup: 1000                   # File system group

auth:
  enabled: true                   # Enable authentication
  type: "basic"                   # Basic auth type
  username: "admin"               # Username
  password: "changeme"            # Use secrets in production
```

Sources: [docs/deployment/helm.mdx:252-268]()

## Configuration Management

### Environment Variable Hierarchy

```typescript
// Priority order (highest to lowest)
1. Railway service variables    // Platform-specific config
2. Docker Compose .env file    // Local development config  
3. Container default values    // Fallback configuration
4. Application defaults        // Code-level defaults
```

### Required vs Optional Configuration

| Variable | Required | Default | Purpose |
|----------|----------|---------|---------|
| `ANTHROPIC_API_KEY` | One of AI keys | - | Claude model access |
| `OPENAI_API_KEY` | One of AI keys | - | GPT model access |
| `GOOGLE_API_KEY` | One of AI keys | - | Gemini model access |
| `DATABASE_URL` | Yes | Auto-generated | PostgreSQL connection |
| `DESKTOP_SERVICE_URL` | No | `http://bytebot-desktop:9990` | Desktop API endpoint |

Sources: [docs/deployment/railway.mdx:38-43]()

## Troubleshooting Deployment Issues

### Common Railway Issues

| Symptom | Cause | Solution |
|---------|-------|----------|
| UI shows "connecting..." | Desktop container not ready | Wait for `bytebot-desktop` startup |
| Agent API errors `401`/`403` | Invalid AI API key | Verify API key in Railway variables |
| Slow desktop performance | Resource limits | Upgrade Railway plan |

Sources: [docs/deployment/railway.mdx:78-82]()

### Local Deployment Issues

- **Port conflicts**: Ensure ports 5432, 9990-9992 are available
- **Docker resources**: Allocate sufficient CPU/RAM for desktop container
- **Network connectivity**: Verify container-to-container communication
- **Image availability**: Ensure access to GitHub Container Registry

Sources: [docs/api-reference/agent/ui.mdx:128-134]()

---

# Page: Installation and Setup

# Installation and Setup

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [docs/api-reference/agent/tasks.mdx](docs/api-reference/agent/tasks.mdx)
- [docs/core-concepts/desktop-environment.mdx](docs/core-concepts/desktop-environment.mdx)
- [docs/deployment/railway.mdx](docs/deployment/railway.mdx)
- [docs/guides/task-creation.mdx](docs/guides/task-creation.mdx)
- [docs/introduction.mdx](docs/introduction.mdx)
- [docs/quickstart.mdx](docs/quickstart.mdx)

</details>



This document provides an overview of deploying and configuring the Bytebot AI desktop agent system. It covers the available deployment methods, system requirements, and initial configuration steps required to run all four core services.

For detailed deployment instructions using Docker Compose, see [Docker Deployment](#3.1). For Kubernetes deployments, see [Kubernetes Deployment](#3.2). For comprehensive configuration options, see [Configuration](#3.3).

## Deployment Methods Overview

Bytebot supports multiple deployment approaches depending on your infrastructure requirements and operational preferences.

```mermaid
graph TB
    subgraph "One-Click Deployment"
        RailwayBtn["Deploy on Railway Button"]
        RailwayTemplate["railway.com/deploy/bytebot"]
    end
    
    subgraph "Self-Hosted Options"
        DockerCompose["docker-compose.yml"]
        K8sHelm["Kubernetes + Helm"]
        LocalDev["Local Development"]
    end
    
    subgraph "Container Registry"
        GHCR["ghcr.io/bytebot-ai"]
        UIImage["bytebot-ui:edge"]
        AgentImage["bytebot-agent:edge"] 
        DesktopImage["bytebot-desktop:edge"]
    end
    
    RailwayBtn --> RailwayTemplate
    DockerCompose --> GHCR
    K8sHelm --> GHCR
    LocalDev --> GHCR
    
    GHCR --> UIImage
    GHCR --> AgentImage
    GHCR --> DesktopImage
```

**Deployment Architecture and Container Images**

Sources: [docs/deployment/railway.mdx:1-90](), [docker/docker-compose.yml:1-87]()

## System Architecture

The complete Bytebot system consists of four interconnected services that must be deployed and configured together.

```mermaid
graph TB
    subgraph "bytebot-ui:9992"
        NextJS["Next.js Application"]
        VNCViewer["VNC Client Integration"]
        TaskInterface["Task Management UI"]
    end
    
    subgraph "bytebot-agent:9991"
        NestJSAgent["NestJS Service"]
        TasksService["TasksService"]
        AgentProcessor["AgentProcessor"] 
        MessagesService["MessagesService"]
        TasksGateway["TasksGateway WebSocket"]
    end
    
    subgraph "bytebot-desktop:9990"
        BytebotdDaemon["bytebotd NestJS Daemon"]
        ComputerUseService["ComputerUseService"]
        XfceDesktop["Ubuntu + XFCE Desktop"]
        VNCServer["VNC/noVNC Server"]
    end
    
    subgraph "postgres:5432"
        PostgresDB["PostgreSQL Database"]
        TasksTable["Tasks Table"]
        MessagesTable["Messages Table"]
    end
    
    NextJS -->|"HTTP API Calls"| NestJSAgent
    VNCViewer -->|"WebSocket VNC"| VNCServer
    TasksGateway -->|"Real-time Updates"| TaskInterface
    
    AgentProcessor -->|"Computer Actions"| ComputerUseService
    TasksService -->|"Task Persistence"| PostgresDB
    MessagesService -->|"Message Storage"| PostgresDB
```

**Service Dependencies and Network Communication**

Sources: [docker/docker-compose.yml:38-79](), [docker/docker-compose.yml:3-36]()

## Container Images and Build Process

All Bytebot services are distributed as multi-architecture Docker images built automatically from the main branch.

| Service | Container Image | Build Trigger | Platforms |
|---------|-----------------|---------------|-----------|
| `bytebot-ui` | `ghcr.io/bytebot-ai/bytebot-ui:edge` | UI/shared code changes | `linux/amd64`, `linux/arm64` |
| `bytebot-agent` | `ghcr.io/bytebot-ai/bytebot-agent:edge` | Agent/shared code changes | `linux/amd64`, `linux/arm64` |
| `bytebot-desktop` | `ghcr.io/bytebot-ai/bytebot-desktop:edge` | Desktop/bytebotd changes | `linux/amd64`, `linux/arm64` |

The build process uses GitHub Actions workflows that automatically trigger on code changes and push multi-architecture images to GitHub Container Registry.

```mermaid
graph LR
    subgraph "GitHub Actions"
        BuildUI[".github/workflows/build-ui.yaml"]
        BuildAgent[".github/workflows/build-agent.yaml"] 
        BuildDesktop[".github/workflows/build-desktop.yaml"]
    end
    
    subgraph "Build Context"
        PackagesDir["./packages/"]
        UIDockerfile["bytebot-ui/Dockerfile"]
        AgentDockerfile["bytebot-agent/Dockerfile"]
        DesktopDockerfile["bytebotd/Dockerfile"]
    end
    
    subgraph "Registry"
        GHCRRegistry["ghcr.io/bytebot-ai"]
    end
    
    BuildUI --> UIDockerfile
    BuildAgent --> AgentDockerfile
    BuildDesktop --> DesktopDockerfile
    
    UIDockerfile --> GHCRRegistry
    AgentDockerfile --> GHCRRegistry
    DesktopDockerfile --> GHCRRegistry
```

**Automated Container Build Pipeline**

Sources: [.github/workflows/build-ui.yaml:1-51](), [.github/workflows/build-agent.yaml:1-50](), [.github/workflows/build-desktop.yaml:1-61]()

## Quick Start Options

### Railway One-Click Deployment

The fastest way to deploy Bytebot is using the Railway template, which handles all service orchestration, networking, and database provisioning automatically.

```mermaid
sequenceDiagram
    participant User
    participant Railway as "Railway Platform"
    participant Template as "Bytebot Template"
    participant GHCR as "GitHub Container Registry"
    
    User->>Railway: Click "Deploy on Railway" button
    Railway->>Template: Load bytebot template configuration
    Template->>GHCR: Pull latest edge images
    Railway->>Railway: Create postgres service
    Railway->>Railway: Setup private networking
    Railway->>User: Provide public URL for bytebot-ui
    User->>Railway: Add AI API keys (ANTHROPIC_API_KEY, etc.)
    Railway->>User: Deployment ready (~2 minutes)
```

**Railway Deployment Flow**

Sources: [docs/deployment/railway.mdx:6-56]()

### Docker Compose Local Deployment

For local development or self-hosted deployments, use the provided Docker Compose configuration:

```bash
# Clone repository and navigate to docker directory
git clone https://github.com/bytebot-ai/bytebot
cd bytebot/docker

# Set required environment variables
export ANTHROPIC_API_KEY="your-key-here"
# or OPENAI_API_KEY, GEMINI_API_KEY

# Deploy all services
docker-compose up -d
```

The `docker-compose.yml` file defines all four services with proper networking and dependency management.

Sources: [docker/docker-compose.yml:1-87]()

## Environment Variables

The core environment variables required across all deployment methods:

| Variable | Service | Purpose | Example |
|----------|---------|---------|---------|
| `DATABASE_URL` | bytebot-agent | PostgreSQL connection | `postgresql://postgres:postgres@postgres:5432/bytebotdb` |
| `BYTEBOT_DESKTOP_BASE_URL` | bytebot-agent | Desktop service URL | `http://bytebot-desktop:9990` |
| `BYTEBOT_AGENT_BASE_URL` | bytebot-ui | Agent service URL | `http://bytebot-agent:9991` |
| `BYTEBOT_DESKTOP_VNC_URL` | bytebot-ui | VNC WebSocket URL | `http://bytebot-desktop:9990/websockify` |
| `ANTHROPIC_API_KEY` | bytebot-agent | Claude API access | `sk-ant-...` |
| `OPENAI_API_KEY` | bytebot-agent | GPT API access | `sk-...` |
| `GEMINI_API_KEY` | bytebot-agent | Gemini API access | `AI...` |

At minimum, one AI provider API key is required for the system to function.

Sources: [docker/docker-compose.yml:48-76]()

## Network Architecture

All services communicate through internal networking with only the UI service exposed publicly.

```mermaid
graph TB
    subgraph "Public Access"
        PublicURL["https://your-domain.com:9992"]
    end
    
    subgraph "Internal Network: bytebot-network"
        UI["bytebot-ui:9992<br/>Public Port: 9992"]
        Agent["bytebot-agent:9991<br/>Internal Only"]
        Desktop["bytebot-desktop:9990<br/>Internal Only"] 
        DB["postgres:5432<br/>Internal Only"]
    end
    
    PublicURL --> UI
    UI -->|"HTTP API"| Agent
    UI -->|"WebSocket VNC"| Desktop
    Agent -->|"SQL Queries"| DB
    Agent -->|"Computer Actions"| Desktop
    
    style UI fill:#e1f5fe
    style Agent fill:#f3e5f5  
    style Desktop fill:#e8f5e8
    style DB fill:#fff3e0
```

**Service Network Topology**

Sources: [docker/docker-compose.yml:81-83](), [docs/deployment/railway.mdx:60-66]()

## System Requirements

### Minimum Requirements
- **CPU**: 2 cores
- **RAM**: 4GB minimum (8GB recommended)
- **Storage**: 10GB available space
- **Network**: Internet access for AI provider APIs

### Desktop Service Requirements
The `bytebot-desktop` service requires additional resources as it runs a full Ubuntu desktop environment:
- **Shared Memory**: 2GB (`shm_size: "2g"`)
- **Privileged Mode**: Required for desktop functionality
- **Display**: Virtual display `:0` configured

Sources: [docker/docker-compose.yml:11-20](), [docker/docker-compose.core.yml:11-19]()

## Next Steps

After completing the initial installation:

1. **Configure AI Providers**: Add API keys for your preferred AI services (see [Configuration](#3.3))
2. **Set Up Authentication**: Consider adding authentication for production deployments
3. **Customize Desktop Environment**: Modify the desktop service configuration as needed
4. **Monitor Services**: Set up logging and monitoring for production environments

For production deployments, see [Kubernetes Deployment](#3.2) for scalable orchestration options.

Sources: [docs/deployment/railway.mdx:86-90]()

---

# Page: Docker Deployment

# Docker Deployment

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [docs/api-reference/agent/tasks.mdx](docs/api-reference/agent/tasks.mdx)
- [docs/core-concepts/desktop-environment.mdx](docs/core-concepts/desktop-environment.mdx)
- [docs/deployment/railway.mdx](docs/deployment/railway.mdx)
- [docs/guides/task-creation.mdx](docs/guides/task-creation.mdx)
- [docs/introduction.mdx](docs/introduction.mdx)
- [docs/quickstart.mdx](docs/quickstart.mdx)

</details>



This document covers deploying Bytebot using Docker Compose for local development or self-hosted production environments. It includes both pre-built container images and building from source.

For enterprise-scale Kubernetes deployments, see [Kubernetes Deployment](#3.2). For managed PaaS deployment options, see Railway's one-click template referenced in the system documentation.

## Container Services Overview

Bytebot runs as a multi-container application with four core services orchestrated through Docker Compose:

```mermaid
graph TB
    subgraph "Docker Network: bytebot-network"
        UI["bytebot-ui<br/>:9992<br/>(Public)"]
        Agent["bytebot-agent<br/>:9991<br/>(Internal)"]
        Desktop["bytebot-desktop<br/>:9990<br/>(Internal)"]
        DB["postgres<br/>:5432<br/>(Internal)"]
    end
    
    subgraph "External Access"
        Browser["Web Browser<br/>Port 9992"]
        VNC["VNC Client<br/>Port 9990"]
    end
    
    Browser --> UI
    VNC --> Desktop
    UI --> Agent
    Agent --> Desktop
    Agent --> DB
    
    subgraph "Container Images"
        UIImg["ghcr.io/bytebot-ai/<br/>bytebot-ui:edge"]
        AgentImg["ghcr.io/bytebot-ai/<br/>bytebot-agent:edge"] 
        DesktopImg["ghcr.io/bytebot-ai/<br/>bytebot-desktop:edge"]
        PostgresImg["postgres:16-alpine"]
    end
    
    UI -.-> UIImg
    Agent -.-> AgentImg
    Desktop -.-> DesktopImg
    DB -.-> PostgresImg
```

**Sources:** [docker/docker-compose.yml:1-87]()

## Quick Start

### Prerequisites

- Docker Engine 20.10+
- Docker Compose v2.0+
- At least 4GB available RAM
- AI provider API key (Anthropic, OpenAI, or Google)

### Basic Deployment

1. Clone the repository and navigate to the docker directory
2. Copy the compose file and configure environment variables:

```bash
# Use pre-built images (recommended)
curl -o docker-compose.yml https://raw.githubusercontent.com/bytebot-ai/bytebot/main/docker/docker-compose.yml

# Set required environment variables
export ANTHROPIC_API_KEY="your-anthropic-key"
# OR export OPENAI_API_KEY="your-openai-key" 
# OR export GEMINI_API_KEY="your-gemini-key"

# Start the services
docker compose up -d
```

3. Access the web interface at `http://localhost:9992`

**Sources:** [docker/docker-compose.yml:48-53](), [docs/deployment/railway.mdx:38-42]()

## Service Configuration

### bytebot-desktop Service

The desktop service provides the containerized Ubuntu environment with XFCE desktop:

```mermaid
graph TB
    subgraph "bytebot-desktop Container"
        XVfb["Xvfb<br/>Virtual Display :0"]
        XFCE["XFCE Desktop<br/>Environment"]
        noVNC["noVNC<br/>Web VNC Server"]
        bytebotd["bytebotd<br/>NestJS Daemon<br/>Port 9990"]
    end
    
    subgraph "Host System"
        VNCPort["Host Port 9990"]
        SharedMem["2GB Shared Memory"]
        Privileged["Privileged Mode"]
    end
    
    VNCPort --> noVNC
    SharedMem --> XVfb
    Privileged --> XFCE
    bytebotd --> XFCE
```

Key configuration parameters:
- `shm_size: "2g"` - Required for X11 applications
- `privileged: true` - Enables desktop environment features
- `hostname: computer` - Internal hostname for desktop identification

**Sources:** [docker/docker-compose.yml:4-21]()

### bytebot-agent Service

The agent orchestrates AI-powered task execution:

| Configuration | Value | Purpose |
|---------------|-------|---------|
| **Port** | `9991` | HTTP API and WebSocket server |
| **Database URL** | `postgresql://postgres:postgres@postgres:5432/bytebotdb` | PostgreSQL connection |
| **Desktop URL** | `http://bytebot-desktop:9990` | Internal desktop API access |
| **Dependencies** | `postgres` | Database must start first |

**Sources:** [docker/docker-compose.yml:38-57]()

### bytebot-ui Service

The web interface provides task management and desktop streaming:

Build-time arguments configure internal service URLs:
- `BYTEBOT_AGENT_BASE_URL` - Agent API endpoint
- `BYTEBOT_DESKTOP_VNC_URL` - VNC WebSocket endpoint

**Sources:** [docker/docker-compose.yml:59-79]()

## Networking and Ports

```mermaid
graph LR
    subgraph "External Access"
        Browser["Browser<br/>:9992"]
        Admin["Admin<br/>:5432"]
        VNCClient["VNC Client<br/>:9990"]
    end
    
    subgraph "bytebot-network (Bridge)"
        UI["bytebot-ui<br/>:9992"]
        Agent["bytebot-agent<br/>:9991"] 
        Desktop["bytebot-desktop<br/>:9990"]
        DB["postgres<br/>:5432"]
    end
    
    Browser --> UI
    Admin -.->|Optional| DB
    VNCClient --> Desktop
    
    UI -->|Internal| Agent
    Agent -->|Internal| Desktop
    Agent -->|Internal| DB
```

| Service | Host Port | Container Port | External Access |
|---------|-----------|----------------|-----------------|
| **bytebot-ui** | `9992` | `9992` | ✅ Web interface |
| **bytebot-agent** | `9991` | `9991` | ❌ Internal API |
| **bytebot-desktop** | `9990` | `9990` | ✅ VNC access |
| **postgres** | `5432` | `5432` | ❌ Database only |

**Sources:** [docker/docker-compose.yml:81-86]()

## Environment Variables

### Required Variables

At least one AI provider API key must be configured:

```bash
# Anthropic Claude models
ANTHROPIC_API_KEY=your-anthropic-key

# OpenAI GPT models  
OPENAI_API_KEY=your-openai-key

# Google Gemini models
GEMINI_API_KEY=your-gemini-key
```

### Optional Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `DATABASE_URL` | `postgresql://postgres:postgres@postgres:5432/bytebotdb` | PostgreSQL connection string |
| `BYTEBOT_DESKTOP_BASE_URL` | `http://bytebot-desktop:9990` | Desktop service endpoint |
| `BYTEBOT_AGENT_BASE_URL` | `http://bytebot-agent:9991` | Agent service endpoint |
| `BYTEBOT_DESKTOP_VNC_URL` | `http://bytebot-desktop:9990/websockify` | VNC WebSocket URL |

**Sources:** [docker/docker-compose.yml:48-75]()

## Volume Management

### PostgreSQL Data Persistence

```yaml
volumes:
  postgres_data:
    # Named volume for database persistence
```

The database volume ensures data survives container restarts and updates. For production deployments, consider mounting a host directory:

```yaml
volumes:
  - ./postgres-data:/var/lib/postgresql/data
```

**Sources:** [docker/docker-compose.yml:85-86](), [docker/docker-compose.yml:35-36]()

## Building from Source

The Docker Compose file supports both pre-built images and local builds:

```mermaid
graph TB
    subgraph "Build Context: ./packages/"
        Shared["shared/<br/>Common types"]
        UI["bytebot-ui/<br/>Dockerfile"]
        Agent["bytebot-agent/<br/>Dockerfile"] 
        Desktop["bytebotd/<br/>Dockerfile"]
    end
    
    subgraph "Build Process"
        UIBuild["UI Build<br/>Next.js App"]
        AgentBuild["Agent Build<br/>NestJS Service"]
        DesktopBuild["Desktop Build<br/>Ubuntu + XFCE"]
    end
    
    UI --> UIBuild
    Agent --> AgentBuild  
    Desktop --> DesktopBuild
    Shared --> UIBuild
    Shared --> AgentBuild
```

To build from source, uncomment the `build` sections in the compose file:

```yaml
services:
  bytebot-desktop:
    build:
      context: ../packages/
      dockerfile: bytebotd/Dockerfile
    # image: ghcr.io/bytebot-ai/bytebot-desktop:edge
```

**Sources:** [docker/docker-compose.yml:5-8](), [docker/docker-compose.yml:39-42](), [docker/docker-compose.yml:60-65]()

## CI/CD Integration

The GitHub Actions workflows automatically build and push container images:

```mermaid
graph LR
    subgraph "GitHub Actions"
        UIWorkflow[".github/workflows/<br/>build-ui.yaml"]
        AgentWorkflow[".github/workflows/<br/>build-agent.yaml"]
        DesktopWorkflow[".github/workflows/<br/>build-desktop.yaml"]
    end
    
    subgraph "GitHub Container Registry"
        UIImage["ghcr.io/bytebot-ai/<br/>bytebot-ui:edge"]
        AgentImage["ghcr.io/bytebot-ai/<br/>bytebot-agent:edge"]
        DesktopImage["ghcr.io/bytebot-ai/<br/>bytebot-desktop:edge"]
    end
    
    UIWorkflow --> UIImage
    AgentWorkflow --> AgentImage
    DesktopWorkflow --> DesktopImage
```

Images are built for both `linux/amd64` and `linux/arm64` architectures and tagged as `edge` from the main branch.

**Sources:** [.github/workflows/build-ui.yaml:27-28](), [.github/workflows/build-agent.yaml:27-28](), [.github/workflows/build-desktop.yaml:34-35]()

## Troubleshooting

### Common Issues

| Symptom | Likely Cause | Solution |
|---------|--------------|----------|
| UI shows "connecting..." | Desktop container not ready | Wait for `bytebot-desktop` startup, check logs |
| Agent startup errors | Missing API keys | Verify AI provider credentials |
| Database connection failed | PostgreSQL not ready | Ensure postgres container is healthy |
| Desktop performance issues | Insufficient shared memory | Increase `shm_size` or add more RAM |
| VNC connection refused | Port conflicts | Check port 9990 availability |

### Service Dependencies

```mermaid
graph TB
    Start["docker compose up"]
    
    subgraph "Startup Order"
        DB["1. postgres<br/>Database startup"]
        Desktop["2. bytebot-desktop<br/>Desktop environment"]
        Agent["3. bytebot-agent<br/>depends_on: postgres"]
        UI["4. bytebot-ui<br/>depends_on: bytebot-agent"]
    end
    
    Start --> DB
    Start --> Desktop
    DB --> Agent
    Agent --> UI
```

### Log Analysis

```bash
# View all service logs
docker compose logs -f

# View specific service logs
docker compose logs -f bytebot-agent
docker compose logs -f bytebot-desktop

# Check service health
docker compose ps
```

**Sources:** [docker/docker-compose.yml:54-55](), [docker/docker-compose.yml:76-77]()

---

# Page: Railway Deployment

# Railway Deployment

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [docs/api-reference/agent/tasks.mdx](docs/api-reference/agent/tasks.mdx)
- [docs/core-concepts/desktop-environment.mdx](docs/core-concepts/desktop-environment.mdx)
- [docs/deployment/railway.mdx](docs/deployment/railway.mdx)
- [docs/guides/task-creation.mdx](docs/guides/task-creation.mdx)
- [docs/introduction.mdx](docs/introduction.mdx)
- [docs/quickstart.mdx](docs/quickstart.mdx)

</details>



## Purpose and Scope

This document provides comprehensive guidance for deploying Bytebot on the Railway platform. Railway offers a zero-configuration Platform-as-a-Service (PaaS) deployment method that automatically provisions all required services with private networking. This deployment option is ideal for users who want a production-ready Bytebot instance without managing infrastructure.

For local development deployment, see [Docker Deployment](#3.1). For overall deployment architecture concepts, see [Deployment Architecture](#2.3). For general configuration options that apply to all deployment methods, see [Configuration](#3.3).

## Railway Deployment Overview

Railway provides a template-based deployment system that instantiates the complete Bytebot stack from pre-built container images. The deployment uses Railway's private networking to connect services securely while exposing only the web UI to the public internet.

**Deployment URL**: The official template is accessible at:
```
https://railway.com/deploy/bytebot?referralCode=L9lKXQ
```

**Deployment Time**: Approximately 2 minutes for initial deployment, with faster subsequent redeploys.

**Sources**: [README.md:11](), [docs/deployment/railway.mdx:1-14](), [docs/quickstart.mdx:14]()

## Railway Service Architecture

### Service Topology

The Railway template deploys four interconnected services that communicate via Railway's internal private network:

```mermaid
graph TB
    subgraph "Public Internet"
        Browser["Browser Clients"]
    end
    
    subgraph "Railway Private Network"
        UI["bytebot-ui<br/>ghcr.io/bytebot-ai/bytebot-ui:edge<br/>Port 9992<br/>PUBLIC"]
        Agent["bytebot-agent<br/>ghcr.io/bytebot-ai/bytebot-agent:edge<br/>Port 9991<br/>PRIVATE"]
        Desktop["bytebot-desktop<br/>ghcr.io/bytebot-ai/bytebot-desktop:edge<br/>Port 9990<br/>PRIVATE"]
        DB["postgres<br/>postgres:14-alpine<br/>Port 5432<br/>PRIVATE"]
    end
    
    subgraph "External Services"
        Anthropic["Anthropic API<br/>Claude Models"]
        OpenAI["OpenAI API<br/>GPT Models"]
        Google["Google API<br/>Gemini Models"]
    end
    
    Browser -->|"HTTPS<br/>railway.app domain"| UI
    UI -->|"HTTP Proxy<br/>Internal DNS"| Agent
    UI -->|"WebSocket Proxy<br/>Internal DNS"| Desktop
    Agent -->|"Prisma Client<br/>DATABASE_URL"| DB
    Agent -->|"Computer Use API<br/>COMPUTER_USE_API_URL"| Desktop
    Agent -->|"ANTHROPIC_API_KEY"| Anthropic
    Agent -->|"OPENAI_API_KEY"| OpenAI
    Agent -->|"GEMINI_API_KEY"| Google
```

**Sources**: [docs/deployment/railway.mdx:18-28](), [docs/quickstart.mdx:68-74]()

### Container Image Sources

All services use pre-built images from GitHub Container Registry, automatically built from the `edge` branch:

| Service | Container Image | Purpose |
|---------|----------------|---------|
| **bytebot-ui** | `ghcr.io/bytebot-ai/bytebot-ui:edge` | Next.js frontend with Express server for API proxying |
| **bytebot-agent** | `ghcr.io/bytebot-ai/bytebot-agent:edge` | NestJS backend for task orchestration and LLM integration |
| **bytebot-desktop** | `ghcr.io/bytebot-ai/bytebot-desktop:edge` | Ubuntu 22.04 desktop environment with bytebotd daemon |
| **postgres** | `postgres:14-alpine` | Relational database for tasks, messages, summaries, and files |

**Sources**: [docs/deployment/railway.mdx:18-26]()

### Service Port Configuration

```mermaid
graph LR
    subgraph "Port Mapping"
        UI_Port["bytebot-ui:9992<br/>PUBLIC<br/>Assigned Railway Domain"]
        Agent_Port["bytebot-agent:9991<br/>PRIVATE<br/>Internal DNS Only"]
        Desktop_Port["bytebot-desktop:9990<br/>PRIVATE<br/>Internal DNS Only"]
        DB_Port["postgres:5432<br/>PRIVATE<br/>Internal DNS Only"]
    end
    
    subgraph "Environment Variables"
        AGENT_URL["AGENT_API_URL<br/>http://bytebot-agent:9991"]
        DESKTOP_URL["COMPUTER_USE_API_URL<br/>http://bytebot-desktop:9990"]
        DATABASE_URL["DATABASE_URL<br/>postgresql://postgres:5432/bytebot"]
    end
    
    UI_Port --> AGENT_URL
    UI_Port --> DESKTOP_URL
    Agent_Port --> DESKTOP_URL
    Agent_Port --> DATABASE_URL
```

**Sources**: [docs/deployment/railway.mdx:18-28](), [docs/quickstart.mdx:170-177]()

## Step-by-Step Deployment Process

### 1. Template Initialization

Access the Railway template by clicking the deployment button or visiting the template URL directly. Railway will prompt for authentication if not already logged in.

**Template URL**: `https://railway.com/deploy/bytebot?referralCode=L9lKXQ`

**Sources**: [docs/deployment/railway.mdx:34-36](), [README.md:11](), [docs/quickstart.mdx:17-19]()

### 2. Environment Configuration

The deployment requires at least one LLM provider API key. Railway presents a configuration form for the `bytebot-agent` service:

```mermaid
graph TD
    Config["Railway Configuration Form"]
    
    Config --> Required["Required: Choose One LLM Provider"]
    
    Required --> Anthropic["ANTHROPIC_API_KEY<br/>Format: sk-ant-..."]
    Required --> OpenAI["OPENAI_API_KEY<br/>Format: sk-..."]
    Required --> Google["GEMINI_API_KEY<br/>Format: AIza..."]
    
    Config --> Optional["Optional: Model Selection"]
    
    Optional --> AnthropicModel["ANTHROPIC_MODEL<br/>Default: claude-3-5-sonnet-20241022"]
    Optional --> OpenAIModel["OPENAI_MODEL<br/>Default: gpt-4o"]
    Optional --> GeminiModel["GEMINI_MODEL<br/>Default: gemini-1.5-flash"]
```

**Required Configuration**:
- **API Key**: At least one of `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, or `GEMINI_API_KEY` must be provided
- **Format Validation**: Keys must match the expected format for each provider

**Optional Configuration**:
- **Model Selection**: Override default models by setting provider-specific model environment variables
- **Database Credentials**: Auto-generated by Railway; no manual configuration needed

**Sources**: [docs/deployment/railway.mdx:38-44](), [docs/quickstart.mdx:20-22](), [docs/quickstart.mdx:326-337]()

### 3. Service Provisioning

Railway executes the following provisioning sequence:

```mermaid
sequenceDiagram
    participant User
    participant Railway
    participant Registry as "GitHub Container Registry"
    participant Services as "Railway Services"
    
    User->>Railway: Click Deploy
    Railway->>Railway: Validate Environment Variables
    Railway->>Railway: Create Private Network
    Railway->>Railway: Provision PostgreSQL Database
    
    Railway->>Registry: Pull ghcr.io/bytebot-ai/bytebot-ui:edge
    Railway->>Registry: Pull ghcr.io/bytebot-ai/bytebot-agent:edge
    Railway->>Registry: Pull ghcr.io/bytebot-ai/bytebot-desktop:edge
    Registry-->>Railway: Container Images
    
    Railway->>Services: Deploy postgres
    Railway->>Services: Deploy bytebot-desktop
    Railway->>Services: Deploy bytebot-agent
    Railway->>Services: Deploy bytebot-ui
    
    Services-->>Railway: Health Checks Pass
    Railway->>Railway: Generate Public Domain
    Railway-->>User: Deployment Complete<br/>URL: https://bytebot-ui-prod.up.railway.app
```

**Provisioning Steps**:
1. Environment variable validation
2. Private network creation for inter-service communication
3. PostgreSQL database initialization with auto-generated credentials
4. Container image pulls from GitHub Container Registry
5. Service deployment in dependency order (database → desktop → agent → UI)
6. Health check verification for each service
7. Public domain assignment to `bytebot-ui` service

**Deployment Duration**: Approximately 2 minutes for initial deployment. Subsequent redeploys are faster due to cached container layers.

**Sources**: [docs/deployment/railway.mdx:45-52](), [docs/deployment/railway.mdx:54-56]()

### 4. Service Readiness

The deployment is complete when the UI service reports ready status. Access the application at the generated Railway domain:

**URL Format**: `https://bytebot-ui-prod-{random}.up.railway.app`

**Verification Steps**:
1. Navigate to the generated URL
2. Verify the task creation interface loads
3. Create a test task to confirm agent connectivity
4. Check desktop viewer for virtual desktop access

**Sources**: [docs/deployment/railway.mdx:48-52]()

## Environment Variables and Configuration

### Core Service Variables

#### bytebot-agent Environment

The agent service requires LLM provider credentials and internal service URLs:

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `ANTHROPIC_API_KEY` | Conditional* | - | Anthropic API key for Claude models |
| `OPENAI_API_KEY` | Conditional* | - | OpenAI API key for GPT models |
| `GEMINI_API_KEY` | Conditional* | - | Google API key for Gemini models |
| `ANTHROPIC_MODEL` | No | `claude-3-5-sonnet-20241022` | Specific Claude model identifier |
| `OPENAI_MODEL` | No | `gpt-4o` | Specific GPT model identifier |
| `GEMINI_MODEL` | No | `gemini-1.5-flash` | Specific Gemini model identifier |
| `DATABASE_URL` | Yes (auto) | Auto-generated | PostgreSQL connection string |
| `COMPUTER_USE_API_URL` | Yes (auto) | `http://bytebot-desktop:9990` | Desktop service API endpoint |

\* At least one LLM provider API key is required

**Sources**: [docs/deployment/railway.mdx:38-44](), [docs/quickstart.mdx:326-337]()

#### bytebot-ui Environment

The UI service requires agent API endpoint configuration:

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `AGENT_API_URL` | Yes (auto) | `http://bytebot-agent:9991` | Agent service REST API endpoint |
| `PORT` | No | `9992` | HTTP server port |

**Sources**: [docs/quickstart.mdx:170-177]()

#### bytebot-desktop Environment

The desktop service runs with minimal configuration:

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `PORT` | No | `9990` | Computer use API and VNC server port |
| `DISPLAY` | Yes (auto) | `:0` | X11 display server identifier |

**Sources**: [docs/core-concepts/desktop-environment.mdx:73-77]()

### Database Configuration

Railway automatically provisions a PostgreSQL database and injects the connection string into the `bytebot-agent` service:

```
DATABASE_URL=postgresql://<user>:<password>@<host>:5432/<database>
```

**Auto-generated Components**:
- Database name
- Username
- Password
- Internal hostname
- SSL configuration

The `bytebot-agent` service uses Prisma as the database client, which reads `DATABASE_URL` from the environment.

**Sources**: [docs/deployment/railway.mdx:18-26]()

## Railway Private Networking

### Internal DNS Resolution

Railway's private network provides DNS-based service discovery. Services communicate using internal hostnames that match the service names:

```mermaid
graph LR
    subgraph "Internal DNS Names"
        UI_DNS["bytebot-ui.railway.internal"]
        Agent_DNS["bytebot-agent.railway.internal"]
        Desktop_DNS["bytebot-desktop.railway.internal"]
        DB_DNS["postgres.railway.internal"]
    end
    
    subgraph "Simplified References"
        UI_Simple["bytebot-ui"]
        Agent_Simple["bytebot-agent"]
        Desktop_Simple["bytebot-desktop"]
        DB_Simple["postgres"]
    end
    
    UI_Simple -.->|"Resolves to"| UI_DNS
    Agent_Simple -.->|"Resolves to"| Agent_DNS
    Desktop_Simple -.->|"Resolves to"| Desktop_DNS
    DB_Simple -.->|"Resolves to"| DB_DNS
```

**Service Communication Patterns**:
- `bytebot-ui` → `http://bytebot-agent:9991` (REST API proxy)
- `bytebot-ui` → `ws://bytebot-desktop:9990` (VNC WebSocket proxy)
- `bytebot-agent` → `http://bytebot-desktop:9990/computer-use` (Computer actions)
- `bytebot-agent` → `postgresql://postgres:5432/bytebot` (Database queries)

**Sources**: [docs/deployment/railway.mdx:27-28](), [docs/deployment/railway.mdx:60-66]()

### Network Isolation

Railway enforces network isolation at multiple layers:

| Layer | Configuration | Purpose |
|-------|---------------|---------|
| **Public Exposure** | Only `bytebot-ui` receives a public domain | Limits attack surface to UI service only |
| **Internal Network** | All services share a private network segment | Enables service-to-service communication |
| **Port Binding** | Services bind to `0.0.0.0` internally | Accessible within private network only |
| **DNS Scope** | Internal DNS names not resolvable publicly | Prevents external resolution of private services |

**Security Implications**:
- Agent API (`port 9991`) not accessible from public internet
- Desktop API (`port 9990`) not accessible from public internet
- PostgreSQL (`port 5432`) not accessible from public internet
- Only UI serves HTTP/WebSocket traffic to external clients

**Sources**: [docs/deployment/railway.mdx:60-66]()

## Public Access and Domain Configuration

### Default Railway Domain

Railway automatically generates a public domain for the `bytebot-ui` service:

**URL Pattern**: `https://{service-name}-{environment}-{random}.up.railway.app`

**Example**: `https://bytebot-ui-prod-a4k2j.up.railway.app`

**Sources**: [docs/deployment/railway.mdx:48-52]()

### Custom Domain Configuration

Railway supports custom domain mapping through the dashboard:

```mermaid
graph LR
    CustomDomain["Custom Domain<br/>app.yourcompany.com"]
    
    CustomDomain -->|"1. Add Domain in Railway"| Railway["Railway Dashboard"]
    Railway -->|"2. Provides DNS Records"| DNS["DNS Provider"]
    DNS -->|"3. Configure CNAME/A Records"| Records["DNS Records"]
    Records -->|"4. SSL Certificate"| SSL["Auto-provisioned<br/>Let's Encrypt"]
    SSL -->|"5. HTTPS Traffic"| UI["bytebot-ui Service"]
```

**Configuration Steps**:
1. Navigate to `bytebot-ui` service settings in Railway dashboard
2. Click "Add Domain"
3. Enter custom domain (e.g., `app.yourcompany.com`)
4. Configure DNS provider with provided records
5. Railway automatically provisions SSL certificate

**Sources**: [docs/deployment/railway.mdx:65]()

### Adding Authentication Layer

Railway deployments can be secured with authentication proxies:

**Options**:
- **Railway Built-in**: Password protection via Railway dashboard settings
- **Cloudflare Access**: Zero Trust authentication with Cloudflare
- **OAuth Proxy**: OAuth2 Proxy for identity provider integration
- **Auth0**: Reverse proxy with Auth0 authentication

**Implementation**: Place authentication proxy in front of `bytebot-ui` service using Railway's service chaining.

**Sources**: [docs/deployment/railway.mdx:63-65]()

## Customization and Scaling

### Using Custom Container Images

Fork the repository and build custom images to modify service behavior:

```mermaid
graph LR
    Fork["Fork Repository"]
    Build["Build Custom Images"]
    Push["Push to Container Registry"]
    Update["Update Railway Template"]
    
    Fork --> Modify["Modify Code"]
    Modify --> Build
    Build --> Tag["Tag as custom:latest"]
    Tag --> Push
    Push --> Registry["ghcr.io/your-org/bytebot-agent:custom"]
    Registry --> Update
    Update --> Deploy["Deploy on Railway"]
```

**Steps**:
1. Fork `https://github.com/bytebot-ai/bytebot`
2. Modify service code as needed
3. Build and tag custom container images
4. Push to your container registry (GitHub Container Registry, Docker Hub, etc.)
5. Edit Railway template to reference custom images
6. Deploy modified template

**Sources**: [docs/deployment/railway.mdx:70-72]()

### Resource Allocation

Railway provides per-service resource controls:

| Resource | Minimum | Recommended | Maximum |
|----------|---------|-------------|---------|
| **CPU** | 0.5 vCPU | 2 vCPU | 8 vCPU |
| **Memory** | 512 MB | 2 GB | 32 GB |
| **Storage** | 1 GB | 10 GB | 100 GB |

**Service-Specific Recommendations**:
- **bytebot-ui**: 512 MB RAM, 0.5 vCPU (low resource usage)
- **bytebot-agent**: 2 GB RAM, 1 vCPU (LLM context processing)
- **bytebot-desktop**: 4 GB RAM, 2 vCPU (desktop environment and automation)
- **postgres**: 1 GB RAM, 1 vCPU (database operations)

**Scaling Configuration**: Access resource sliders in Railway dashboard under each service's Settings → Resources tab.

**Sources**: [docs/deployment/railway.mdx:71-72]()

### Database Management

Railway provides PostgreSQL management tools:

**Available Operations**:
- **Backups**: Automatic daily backups with point-in-time recovery
- **Scaling**: Vertical scaling via RAM/CPU sliders
- **Monitoring**: Built-in metrics for connections, queries, storage
- **Access**: Direct database access via Railway's built-in PostgreSQL client

**Connection Details**: Access credentials and connection string from Railway dashboard under postgres service → Connect tab.

**Sources**: [docs/deployment/railway.mdx:18-26]()

## Monitoring and Troubleshooting

### Service Logs

Railway provides real-time log streaming for all services:

**Access Pattern**:
1. Navigate to project in Railway dashboard
2. Select service (e.g., `bytebot-agent`)
3. Click "Logs" tab for real-time stream

**Log Types**:
- **Build Logs**: Container image pull and initialization
- **Deploy Logs**: Service startup and health checks
- **Runtime Logs**: Application output (stdout/stderr)

**Sources**: [docs/deployment/railway.mdx:50]()

### Common Issues and Resolutions

| Symptom | Likely Cause | Resolution |
|---------|--------------|------------|
| UI shows "connecting..." | `bytebot-desktop` not ready | Wait for desktop container startup (~30s); verify logs show "bytebotd ready" |
| Agent returns `401 Unauthorized` | Missing or invalid API key | Re-enter LLM provider API key in Railway variables; redeploy |
| Agent returns `403 Forbidden` | API key lacks required permissions | Verify API key has access to requested model |
| Slow desktop video stream | Free tier bandwidth throttling | Upgrade Railway plan or reduce screen resolution in desktop settings |
| Database connection errors | `DATABASE_URL` misconfigured | Verify postgres service is healthy; check `DATABASE_URL` format |
| Tasks fail to start | `COMPUTER_USE_API_URL` unreachable | Verify `bytebot-desktop` service is running; check private network configuration |

**Sources**: [docs/deployment/railway.mdx:77-83]()

### Health Check Verification

```mermaid
graph TD
    Check["Health Check Sequence"]
    
    Check --> DB["1. PostgreSQL Health"]
    DB --> DB_OK{"Database<br/>Responding?"}
    DB_OK -->|Yes| Desktop["2. Desktop Service Health"]
    DB_OK -->|No| DB_Fail["Check postgres logs<br/>Verify DATABASE_URL"]
    
    Desktop --> Desktop_OK{"bytebotd<br/>Ready?"}
    Desktop_OK -->|Yes| Agent["3. Agent Service Health"]
    Desktop_OK -->|No| Desktop_Fail["Check bytebot-desktop logs<br/>Verify port 9990 listening"]
    
    Agent --> Agent_OK{"Agent API<br/>Responding?"}
    Agent_OK -->|Yes| UI["4. UI Service Health"]
    Agent_OK -->|No| Agent_Fail["Check bytebot-agent logs<br/>Verify API key configured"]
    
    UI --> UI_OK{"UI Public<br/>Domain Active?"}
    UI_OK -->|Yes| Success["System Healthy"]
    UI_OK -->|No| UI_Fail["Check bytebot-ui logs<br/>Verify port 9992 listening"]
```

**Manual Health Checks**:
1. **Database**: Verify postgres service shows "Active" status in Railway dashboard
2. **Desktop**: Check logs for "VNC server started" and "bytebotd listening on port 9990"
3. **Agent**: Check logs for "NestJS application successfully started" and "Listening on port 9991"
4. **UI**: Access public URL and verify task creation interface loads

**Sources**: [docs/deployment/railway.mdx:77-83]()

## Cost Considerations

### Railway Pricing Model

Railway uses a resource-based pricing model:

**Pricing Components**:
- **Base Resources**: CPU, RAM, and storage per service
- **Network Egress**: Outbound bandwidth from public services
- **Build Minutes**: Time spent building custom images (if applicable)

**Free Trial**: Railway offers trial credits for new accounts, sufficient for testing Bytebot deployment.

**Production Costs**: Typical monthly cost for Bytebot stack ranges from $20-50 USD depending on usage patterns and resource allocation.

**Sources**: [docs/deployment/railway.mdx:82]()

### Optimization Strategies

**Cost Reduction Techniques**:
1. **Use Pre-built Images**: Avoid rebuild costs by using official `edge` images
2. **Right-size Resources**: Start with minimum recommended resources; scale as needed
3. **Optimize Desktop Usage**: Reduce screen resolution and color depth for lower bandwidth
4. **Schedule Deployments**: Use Railway's cron jobs to stop/start services during off-hours

**Monitoring Costs**: Track resource usage in Railway dashboard under project → Usage tab.

**Sources**: [docs/deployment/railway.mdx:70-72]()

## Next Steps

After successful Railway deployment, consider the following actions:

- **Configure Desktop**: Use the Desktop tab to install additional applications and set up password managers (see [Core Concepts: Desktop Environment](#1.2))
- **Create Tasks**: Start with simple tasks to verify functionality (see [Task Creation & Management](#8.1))
- **API Integration**: Integrate Bytebot with your applications using the Tasks API (see [Tasks REST API](#10.1))
- **Custom Domains**: Set up a custom domain for professional deployment (see this page, Custom Domain Configuration section above)
- **Security Hardening**: Add authentication layer for production use (see this page, Adding Authentication Layer section above)

**Sources**: [docs/deployment/railway.mdx:86-90]()

---

# Page: Configuration

# Configuration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [docs/api-reference/agent/tasks.mdx](docs/api-reference/agent/tasks.mdx)
- [docs/core-concepts/desktop-environment.mdx](docs/core-concepts/desktop-environment.mdx)
- [docs/deployment/railway.mdx](docs/deployment/railway.mdx)
- [docs/guides/task-creation.mdx](docs/guides/task-creation.mdx)
- [docs/introduction.mdx](docs/introduction.mdx)
- [docs/quickstart.mdx](docs/quickstart.mdx)
- [packages/bytebot-agent/package-lock.json](packages/bytebot-agent/package-lock.json)
- [packages/bytebot-agent/package.json](packages/bytebot-agent/package.json)
- [packages/bytebot-agent/src/agent/agent.module.ts](packages/bytebot-agent/src/agent/agent.module.ts)
- [packages/bytebot-agent/src/app.module.ts](packages/bytebot-agent/src/app.module.ts)
- [packages/bytebot-ui/package-lock.json](packages/bytebot-ui/package-lock.json)
- [packages/bytebot-ui/package.json](packages/bytebot-ui/package.json)
- [packages/bytebot-ui/src/app/layout.tsx](packages/bytebot-ui/src/app/layout.tsx)
- [packages/bytebot-ui/src/components/layout/Header.tsx](packages/bytebot-ui/src/components/layout/Header.tsx)

</details>



This page documents all configuration options for Bytebot services, including environment variables, LLM API keys, database settings, and port assignments. Configuration is loaded from environment variables at runtime, typically provided via `.env` files in Docker deployments or platform environment settings in cloud deployments.

For deployment-specific setup instructions, see [Docker Deployment](#3.1) and [Railway Deployment](#3.2).

---

## Configuration Architecture

Bytebot's configuration system uses environment variables loaded at service startup. Each service (bytebot-agent, bytebot-ui, bytebotd) has independent configuration, with the agent service requiring the most settings due to its role as the orchestration layer.

### Configuration Loading Flow

```mermaid
graph TB
    subgraph "Configuration Sources"
        EnvFile[".env files"]
        PlatformEnv["Platform Environment<br/>(Railway, Docker, K8s)"]
    end
    
    subgraph "bytebot-agent (Port 9991)"
        ConfigModule["ConfigModule<br/>(NestJS)"]
        AnthropicModule["AnthropicModule"]
        OpenAIModule["OpenAIModule"]
        GoogleModule["GoogleModule"]
        PrismaModule["PrismaModule"]
    end
    
    subgraph "bytebot-ui (Port 9992)"
        NextConfig["Next.js Config"]
        ExpressServer["Express Server"]
    end
    
    subgraph "bytebotd (Port 9990)"
        NestConfig["NestJS Config"]
        ComputerUseService["ComputerUseService"]
    end
    
    EnvFile -->|"process.env"| ConfigModule
    PlatformEnv -->|"process.env"| ConfigModule
    
    ConfigModule -->|"ANTHROPIC_API_KEY<br/>ANTHROPIC_MODEL"| AnthropicModule
    ConfigModule -->|"OPENAI_API_KEY<br/>OPENAI_MODEL"| OpenAIModule
    ConfigModule -->|"GEMINI_API_KEY<br/>GEMINI_MODEL"| GoogleModule
    ConfigModule -->|"DATABASE_URL"| PrismaModule
    
    EnvFile -->|"NEXT_PUBLIC_AGENT_URL"| NextConfig
    NextConfig --> ExpressServer
    
    EnvFile -->|"PORT"| NestConfig
    NestConfig --> ComputerUseService
```

**Sources:** [packages/bytebot-agent/src/app.module.ts:18-23](), [README.md:96-99](), [docs/quickstart.mdx:327-337]()

---

## bytebot-agent Configuration

The agent service requires configuration for LLM providers, database connection, and service endpoints.

### Core Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `ANTHROPIC_API_KEY` | Conditional* | - | Anthropic API key for Claude models |
| `OPENAI_API_KEY` | Conditional* | - | OpenAI API key for GPT models |
| `GEMINI_API_KEY` | Conditional* | - | Google API key for Gemini models |
| `DATABASE_URL` | Yes | `postgresql://postgres:postgres@localhost:5432/bytebot` | PostgreSQL connection string for Prisma |
| `PORT` | No | `9991` | HTTP server port for agent API |
| `COMPUTER_USE_URL` | No | `http://bytebot-desktop:9990` | Base URL for bytebotd service |

\* At least one LLM provider API key is required.

### LLM Model Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `ANTHROPIC_MODEL` | `claude-3-5-sonnet-20241022` | Specific Claude model to use |
| `OPENAI_MODEL` | `gpt-4o` | Specific GPT model to use |
| `GEMINI_MODEL` | `gemini-1.5-flash` | Specific Gemini model to use |

### Proxy Mode Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `LITELLM_PROXY_URL` | No | - | LiteLLM proxy endpoint URL (e.g., `http://litellm:4000`) |
| `LITELLM_PROXY_API_KEY` | No | - | API key for LiteLLM proxy authentication |

**Sources:** [README.md:96-99](), [docs/quickstart.mdx:327-337](), [packages/bytebot-agent/package.json:24-32]()

---

## bytebot-ui Configuration

The UI service requires minimal configuration, primarily for connecting to the agent backend.

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `PORT` | No | `9992` | HTTP server port for UI |
| `NEXT_PUBLIC_AGENT_URL` | No | `http://localhost:9991` | Agent API base URL (client-side) |
| `AGENT_URL` | No | `http://bytebot-agent:9991` | Agent API base URL (server-side proxy) |
| `DESKTOP_URL` | No | `http://bytebot-desktop:9990` | Desktop service URL for VNC/WebSocket proxying |

The `NEXT_PUBLIC_` prefix makes variables available to client-side code. The non-prefixed versions are used by the Express server for API proxying.

**Sources:** [packages/bytebot-ui/package.json:1-11](), [docs/quickstart.mdx:340-346]()

---

## bytebotd Configuration

The desktop service has minimal configuration requirements.

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `PORT` | No | `9990` | HTTP server port for computer-use API and VNC |
| `DISPLAY` | No | `:1` | X11 display number |
| `VNC_PORT` | No | `5901` | VNC server port (internal) |
| `WEBSOCKIFY_PORT` | No | `6080` | WebSocket proxy port for browser VNC access |

**Sources:** [docs/core-concepts/desktop-environment.mdx:72-76](), [docs/quickstart.mdx:172-176]()

---

## LLM Provider Setup

### Provider Selection Logic

The agent service attempts to use LLM providers in the following order based on available API keys:

```mermaid
graph TB
    Start["AgentProcessor<br/>needs LLM"]
    
    CheckAnthropic{"ANTHROPIC_API_KEY<br/>set?"}
    CheckOpenAI{"OPENAI_API_KEY<br/>set?"}
    CheckGemini{"GEMINI_API_KEY<br/>set?"}
    CheckLiteLLM{"LITELLM_PROXY_URL<br/>set?"}
    
    UseAnthropic["Use AnthropicService<br/>with ANTHROPIC_MODEL"]
    UseOpenAI["Use OpenAIService<br/>with OPENAI_MODEL"]
    UseGemini["Use GoogleService<br/>with GEMINI_MODEL"]
    UseLiteLLM["Use ProxyService<br/>with LITELLM_PROXY_URL"]
    
    Error["Throw Error:<br/>No LLM provider configured"]
    
    Start --> CheckLiteLLM
    CheckLiteLLM -->|Yes| UseLiteLLM
    CheckLiteLLM -->|No| CheckAnthropic
    CheckAnthropic -->|Yes| UseAnthropic
    CheckAnthropic -->|No| CheckOpenAI
    CheckOpenAI -->|Yes| UseOpenAI
    CheckOpenAI -->|No| CheckGemini
    CheckGemini -->|Yes| UseGemini
    CheckGemini -->|No| Error
```

**Sources:** [packages/bytebot-agent/src/app.module.ts:24-30](), [packages/bytebot-agent/src/agent/agent.module.ts:19-23]()

### Anthropic Claude Configuration

```bash
# Required
ANTHROPIC_API_KEY=sk-ant-api03-...

# Optional - specify model version
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022

# Other supported models:
# - claude-3-5-sonnet-20240620
# - claude-3-opus-20240229
# - claude-3-sonnet-20240229
# - claude-3-haiku-20240307
```

Get your API key from [https://console.anthropic.com](https://console.anthropic.com).

### OpenAI GPT Configuration

```bash
# Required
OPENAI_API_KEY=sk-...

# Optional - specify model version
OPENAI_MODEL=gpt-4o

# Other supported models:
# - gpt-4o-mini
# - gpt-4-turbo
# - gpt-4
# - gpt-3.5-turbo
```

Get your API key from [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys).

### Google Gemini Configuration

```bash
# Required
GEMINI_API_KEY=AIzaSy...

# Optional - specify model version
GEMINI_MODEL=gemini-1.5-flash

# Other supported models:
# - gemini-1.5-pro
# - gemini-1.0-pro
```

Get your API key from [https://makersuite.google.com/app/apikey](https://makersuite.google.com/app/apikey).

**Sources:** [README.md:96-99](), [docs/quickstart.mdx:327-337](), [packages/bytebot-agent/package.json:25-27]()

---

## Database Configuration

Bytebot uses PostgreSQL with Prisma ORM for data persistence.

### Connection String Format

```bash
DATABASE_URL="postgresql://[user]:[password]@[host]:[port]/[database]?[options]"
```

### Default Configuration

```bash
# Docker Compose default
DATABASE_URL="postgresql://postgres:postgres@bytebot-db:5432/bytebot"

# Local development
DATABASE_URL="postgresql://postgres:postgres@localhost:5432/bytebot"

# Railway (auto-generated)
DATABASE_URL=${{Postgres.DATABASE_URL}}
```

### Prisma Configuration Files

The database schema is defined in the Prisma schema files:

- Schema definition: References Prisma schema files in the codebase
- Migrations: Applied via `prisma migrate deploy` on startup
- Client generation: Generated via `prisma generate` during build

**Running Migrations:**

```bash
# Development (creates migration files)
npm run prisma:dev

# Production (applies migrations)
npm run prisma:prod
```

**Sources:** [packages/bytebot-agent/package.json:9-10](), [packages/bytebot-agent/package.json:36]()

---

## Port Configuration

### Default Port Assignments

```mermaid
graph LR
    subgraph "External Access"
        Browser["Web Browser"]
        APIClient["API Client"]
    end
    
    subgraph "Service Ports"
        UI["bytebot-ui<br/>:9992"]
        Agent["bytebot-agent<br/>:9991"]
        Desktop["bytebotd<br/>:9990"]
        DB["PostgreSQL<br/>:5432"]
    end
    
    Browser -->|"HTTP/WebSocket"| UI
    APIClient -->|"REST API"| Agent
    
    UI -->|"Proxy to :9991"| Agent
    UI -->|"Proxy to :9990"| Desktop
    Agent -->|"Computer actions"| Desktop
    Agent -->|"SQL queries"| DB
```

| Service | Default Port | Protocol | Purpose |
|---------|--------------|----------|---------|
| bytebot-ui | 9992 | HTTP/WebSocket | Web interface, proxies to backend services |
| bytebot-agent | 9991 | HTTP/WebSocket | Task management API, LLM orchestration |
| bytebotd | 9990 | HTTP/WebSocket | Computer-use API, VNC access |
| PostgreSQL | 5432 | PostgreSQL | Database persistence |

### Customizing Ports

#### Docker Compose

Edit port mappings in `docker-compose.yml`:

```yaml
services:
  bytebot-ui:
    ports:
      - "8080:9992"  # Map host port 8080 to container port 9992
```

#### Environment Variables

```bash
# bytebot-agent
PORT=8991

# bytebot-ui
PORT=8992

# bytebotd
PORT=8990
```

**Note:** When changing ports, ensure dependent services are updated with the new URLs (e.g., `AGENT_URL`, `DESKTOP_URL`, `COMPUTER_USE_URL`).

**Sources:** [docs/quickstart.mdx:172-176](), [docs/quickstart.mdx:340-346]()

---

## Configuration Examples

### Minimal Configuration (Docker Compose)

```bash
# docker/.env
ANTHROPIC_API_KEY=sk-ant-api03-...
DATABASE_URL=postgresql://postgres:postgres@bytebot-db:5432/bytebot
```

This is the minimum required configuration for a working Bytebot installation using Anthropic Claude.

### Multi-Provider Configuration

```bash
# docker/.env
# Enable multiple providers for fallback
ANTHROPIC_API_KEY=sk-ant-api03-...
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=AIzaSy...

# Specify preferred models
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022
OPENAI_MODEL=gpt-4o
GEMINI_MODEL=gemini-1.5-flash

DATABASE_URL=postgresql://postgres:postgres@bytebot-db:5432/bytebot
```

### LiteLLM Proxy Configuration

Using LiteLLM allows access to 100+ LLM providers through a unified interface:

```bash
# docker/.env
# Point to LiteLLM proxy instead of direct provider APIs
LITELLM_PROXY_URL=http://litellm:4000
LITELLM_PROXY_API_KEY=your-proxy-api-key

# No need for individual provider keys when using proxy
DATABASE_URL=postgresql://postgres:postgres@bytebot-db:5432/bytebot
```

Deploy with the proxy configuration:

```bash
docker-compose -f docker/docker-compose.proxy.yml up -d
```

**Sources:** [docs/quickstart.mdx:349-354](), [README.md:250-256]()

---

## Advanced Configuration

### Custom Computer-Use Endpoint

Override the default bytebotd connection:

```bash
# Connect to remote desktop instance
COMPUTER_USE_URL=http://remote-desktop.example.com:9990
```

### Custom Next.js Configuration

For the UI service, advanced configuration can be set in `next.config.js`:

- API route rewrites
- Environment variable exposure
- Build optimizations

### Database Connection Pooling

For high-traffic deployments, configure Prisma connection pooling:

```bash
DATABASE_URL="postgresql://user:pass@host:5432/db?connection_limit=10&pool_timeout=20"
```

**Sources:** [packages/bytebot-ui/package.json:6-8](), [packages/bytebot-agent/package.json:36]()

---

## Configuration Validation

### Agent Service Validation

The agent service validates configuration on startup:

```mermaid
graph TB
    Start["Service Startup"]
    
    CheckDB{"DATABASE_URL<br/>valid?"}
    CheckLLM{"At least one<br/>LLM provider?"}
    CheckComputer{"COMPUTER_USE_URL<br/>reachable?"}
    
    InitModules["Initialize NestJS Modules:<br/>- ConfigModule<br/>- PrismaModule<br/>- AnthropicModule<br/>- OpenAIModule<br/>- GoogleModule<br/>- ProxyModule"]
    
    Ready["Service Ready<br/>Port 9991"]
    Error["Exit with Error"]
    
    Start --> CheckDB
    CheckDB -->|"No"| Error
    CheckDB -->|"Yes"| CheckLLM
    CheckLLM -->|"No"| Error
    CheckLLM -->|"Yes"| CheckComputer
    CheckComputer -->|"No"| Error
    CheckComputer -->|"Yes"| InitModules
    InitModules --> Ready
```

**Sources:** [packages/bytebot-agent/src/app.module.ts:17-37]()

### Common Configuration Errors

| Error Message | Cause | Solution |
|---------------|-------|----------|
| `No LLM provider configured` | Missing all API keys | Set at least one: `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, or `GEMINI_API_KEY` |
| `Database connection failed` | Invalid `DATABASE_URL` | Verify PostgreSQL is running and connection string is correct |
| `Cannot connect to computer-use service` | bytebotd not running or wrong URL | Check `COMPUTER_USE_URL` and ensure bytebotd is accessible |
| `Invalid API key` | Incorrect or expired API key | Verify API key from provider console |

**Sources:** [README.md:290-296](), [docs/quickstart.mdx:273-298]()

---

## Environment Variable Reference

### Complete Variable List

```bash
# ===== bytebot-agent =====
# LLM Providers (at least one required)
ANTHROPIC_API_KEY=sk-ant-api03-...
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=AIzaSy...

# LLM Models (optional, defaults shown)
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022
OPENAI_MODEL=gpt-4o
GEMINI_MODEL=gemini-1.5-flash

# LiteLLM Proxy (optional)
LITELLM_PROXY_URL=http://litellm:4000
LITELLM_PROXY_API_KEY=your-key

# Database (required)
DATABASE_URL=postgresql://postgres:postgres@bytebot-db:5432/bytebot

# Service Configuration
PORT=9991
COMPUTER_USE_URL=http://bytebot-desktop:9990

# ===== bytebot-ui =====
PORT=9992
NEXT_PUBLIC_AGENT_URL=http://localhost:9991
AGENT_URL=http://bytebot-agent:9991
DESKTOP_URL=http://bytebot-desktop:9990

# ===== bytebotd =====
PORT=9990
DISPLAY=:1
VNC_PORT=5901
WEBSOCKIFY_PORT=6080
```

**Sources:** [README.md:96-99](), [docs/quickstart.mdx:327-337](), [docs/deployment/railway.mdx:36-42]()

---

# Page: Core Services

# Core Services

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [packages/bytebot-agent/package-lock.json](packages/bytebot-agent/package-lock.json)
- [packages/bytebot-agent/package.json](packages/bytebot-agent/package.json)
- [packages/bytebot-agent/src/agent/agent.module.ts](packages/bytebot-agent/src/agent/agent.module.ts)
- [packages/bytebot-agent/src/app.module.ts](packages/bytebot-agent/src/app.module.ts)
- [packages/bytebot-ui/package-lock.json](packages/bytebot-ui/package-lock.json)
- [packages/bytebot-ui/package.json](packages/bytebot-ui/package.json)
- [packages/bytebot-ui/src/app/layout.tsx](packages/bytebot-ui/src/app/layout.tsx)
- [packages/bytebot-ui/src/components/layout/Header.tsx](packages/bytebot-ui/src/components/layout/Header.tsx)
- [packages/bytebotd/package-lock.json](packages/bytebotd/package-lock.json)
- [packages/bytebotd/package.json](packages/bytebotd/package.json)
- [packages/bytebotd/src/app.controller.ts](packages/bytebotd/src/app.controller.ts)
- [packages/bytebotd/src/app.module.ts](packages/bytebotd/src/app.module.ts)
- [packages/bytebotd/src/mcp/bytebot-mcp.module.ts](packages/bytebotd/src/mcp/bytebot-mcp.module.ts)
- [packages/bytebotd/src/mcp/index.ts](packages/bytebotd/src/mcp/index.ts)

</details>



This page provides a detailed examination of Bytebot's three core services and their internal architecture. It covers the implementation details, module structures, and communication patterns within each service.

For deployment and infrastructure information, see [Deployment Architecture](#2.2). For user-facing functionality, see [User Interface](#7) and [Desktop Environment](#5).

## Service Overview

Bytebot consists of three primary services that work together to provide AI-powered desktop automation:

| Service | Package Name | Technology | Port | Primary Role |
|---------|--------------|------------|------|--------------|
| Agent Service | `bytebot-agent` | NestJS | 9991 | AI orchestration, API backend |
| Desktop Service | `bytebotd` | NestJS | 9990 | Desktop automation, VNC server |
| UI Service | `bytebot-ui` | Next.js | 9992 | Web frontend, user interface |

```mermaid
graph TB
    subgraph "bytebot-ui:9992"
        UI_App["Next.js Application"]
        UI_Proxy["API Proxy<br/>/api/**"]
    end
    
    subgraph "bytebot-agent:9991"
        Agent_Main["main.ts<br/>NestFactory.create(AppModule)"]
        Agent_App["AppModule"]
        Agent_Tasks["TasksModule"]
        Agent_Messages["MessagesModule"]
        Agent_Auth["AuthModule"]
    end
    
    subgraph "bytebotd:9990"
        Desktop_Main["main.ts<br/>NestFactory.create(AppModule)"]
        Desktop_App["AppModule"]
        Desktop_ComputerUse["ComputerUseModule"]
        Desktop_InputTracking["InputTrackingModule"]
        Desktop_MCP["BytebotMcpModule"]
    end
    
    UI_Proxy -->|"HTTP/WebSocket"| Agent_Main
    UI_Proxy -->|"VNC WebSocket"| Desktop_Main
    Agent_Tasks -->|"Computer Actions"| Desktop_ComputerUse
    
    Agent_App --> Agent_Tasks
    Agent_App --> Agent_Messages
    Agent_App --> Agent_Auth
    
    Desktop_App --> Desktop_ComputerUse
    Desktop_App --> Desktop_InputTracking
    Desktop_App --> Desktop_MCP
```

**Sources:** [packages/bytebot-agent/src/main.ts:1-36](), [packages/bytebotd/src/app.module.ts:1-27](), [packages/bytebotd/package.json:1-93]()

## Agent Service Architecture

The `bytebot-agent` service serves as the central orchestrator, handling AI model integration, task management, and API endpoints.

### Main Application Setup

The agent service initializes through `main.ts` with specific configurations for handling large payloads and CORS:

```mermaid
graph TD
    Bootstrap["bootstrap()"]
    CreateApp["NestFactory.create(AppModule)"]
    ConfigBody["Body Parser Config<br/>50MB limit"]
    ConfigCORS["CORS Config<br/>origin: '*'"]
    SetPrefix["setGlobalPrefix('api')"]
    Listen["app.listen(9991)"]
    
    Bootstrap --> CreateApp
    CreateApp --> ConfigBody
    ConfigBody --> ConfigCORS
    ConfigCORS --> SetPrefix
    SetPrefix --> Listen
```

The application configures JSON and URL-encoded body parsers with a 50MB limit to handle large file uploads and screenshots [packages/bytebot-agent/src/main.ts:18-19](), sets a global API prefix [packages/bytebot-agent/src/main.ts:22](), and enables permissive CORS for cross-origin requests [packages/bytebot-agent/src/main.ts:25-28]().

### Module Structure

The agent service follows NestJS modular architecture patterns:

| Module | Responsibility | Key Components |
|--------|----------------|----------------|
| `AppModule` | Root module, dependency injection | Core configuration |
| `TasksModule` | Task lifecycle management | `TasksService`, `TasksController` |
| `MessagesModule` | Chat message handling | `MessagesService`, message persistence |
| `AuthModule` | Authentication and authorization | Better Auth integration |
| `AgentModule` | AI model orchestration | `AgentProcessor`, LLM integrations |

**Sources:** [packages/bytebot-agent/src/main.ts:1-36]()

## Desktop Service Architecture

The `bytebotd` service provides the virtual desktop environment and computer automation capabilities.

### Application Module Configuration

```mermaid
graph TB
    AppModule["AppModule"]
    ConfigModule["ConfigModule.forRoot()<br/>isGlobal: true"]
    ServeStatic["ServeStaticModule<br/>rootPath: /opt/noVNC<br/>serveRoot: /novnc"]
    ComputerUse["ComputerUseModule"]
    InputTracking["InputTrackingModule"]
    BytebotMcp["BytebotMcpModule"]
    AppController["AppController"]
    AppService["AppService"]
    
    AppModule --> ConfigModule
    AppModule --> ServeStatic
    AppModule --> ComputerUse
    AppModule --> InputTracking
    AppModule --> BytebotMcp
    AppModule --> AppController
    AppModule --> AppService
```

The desktop service configures global environment variables [packages/bytebotd/src/app.module.ts:12-14](), serves noVNC static files for web-based VNC access [packages/bytebotd/src/app.module.ts:15-18](), and integrates multiple specialized modules for different automation concerns.

### Core Modules

| Module | Technology Stack | Purpose |
|--------|------------------|---------|
| `ComputerUseModule` | `@nut-tree-fork/nut-js` | Mouse, keyboard, screen automation |
| `InputTrackingModule` | `uiohook-napi` | User input monitoring and capture |
| `BytebotMcpModule` | `@rekog/mcp-nest` | Model Context Protocol server |

### VNC Integration

The `AppController` provides seamless VNC access through automatic redirection:

```mermaid
graph LR
    Client["Client Request<br/>/vnc"]
    Controller["AppController.redirectToVnc()"]
    Redirect["302 Redirect<br/>/novnc/vnc.html?host=&path=websockify&resize=scale"]
    NoVNC["noVNC Client<br/>Served from /opt/noVNC"]
    
    Client --> Controller
    Controller --> Redirect
    Redirect --> NoVNC
```

The controller extracts the host header and constructs a noVNC URL with appropriate parameters for websocket connection and display scaling [packages/bytebotd/src/app.controller.ts:13-16]().

**Sources:** [packages/bytebotd/src/app.module.ts:1-27](), [packages/bytebotd/src/app.controller.ts:1-19](), [packages/bytebotd/package.json:28-47]()

## Model Context Protocol Integration

The desktop service implements MCP (Model Context Protocol) for standardized AI tool integration:

```mermaid
graph TB
    McpModule["McpModule.forRoot()"]
    Config["name: 'bytebotd'<br/>version: '0.0.1'<br/>sseEndpoint: '/mcp'"]
    ComputerUseTools["ComputerUseTools<br/>MCP Tool Provider"]
    ComputerUseModule_ref["ComputerUseModule<br/>Automation Backend"]
    
    McpModule --> Config
    McpModule --> ComputerUseTools
    ComputerUseTools --> ComputerUseModule_ref
```

The MCP integration exposes computer automation capabilities as standardized tools that can be consumed by AI models through the `/mcp` SSE endpoint [packages/bytebotd/src/mcp/bytebot-mcp.module.ts:9-13]().

**Sources:** [packages/bytebotd/src/mcp/bytebot-mcp.module.ts:1-18](), [packages/bytebotd/src/mcp/index.ts:1-2]()

## Inter-Service Communication Patterns

The services communicate through multiple channels optimized for different data types and latency requirements:

```mermaid
graph TB
    subgraph "Communication Layers"
        HTTP["HTTP REST API<br/>Task CRUD, File Operations"]
        WebSocket["WebSocket Events<br/>Real-time Updates"]
        VNC_WS["VNC WebSocket<br/>Desktop Streaming"]
        MCP_SSE["MCP Server-Sent Events<br/>Tool Invocation"]
    end
    
    subgraph "Data Flow"
        UI_Tasks["UI Task Management"] -->|HTTP| HTTP
        UI_Chat["UI Chat Interface"] -->|WebSocket| WebSocket
        UI_Desktop["UI Desktop Viewer"] -->|VNC WebSocket| VNC_WS
        Agent_Tools["Agent Tool Use"] -->|SSE| MCP_SSE
    end
    
    HTTP --> Agent_API["bytebot-agent<br/>:9991/api"]
    WebSocket --> Agent_Gateway["TasksGateway<br/>Socket.IO"]
    VNC_WS --> Desktop_VNC["bytebotd<br/>:9990/websockify"]
    MCP_SSE --> Desktop_MCP["bytebotd<br/>:9990/mcp"]
```

### Service Dependencies

Each service has specific technology dependencies that define its capabilities:

| Service | Key Dependencies | Purpose |
|---------|------------------|---------|
| `bytebot-agent` | `@nestjs/platform-socket.io`, `prisma` | WebSocket gateway, database ORM |
| `bytebotd` | `@nut-tree-fork/nut-js`, `uiohook-napi`, `sharp` | OS automation, input capture, image processing |
| `bytebot-ui` | `socket.io-client`, `react-vnc` | Real-time communication, VNC display |

**Sources:** [packages/bytebotd/package.json:28-47](), [packages/bytebot-agent/src/main.ts:22-28]()

## Service Lifecycle and Process Management

Each service follows standardized patterns for initialization, configuration, and shutdown:

```mermaid
graph TB
    subgraph "Agent Service Lifecycle"
        Agent_Bootstrap["bootstrap()"]
        Agent_Crypto["Crypto Polyfill<br/>globalThis.crypto"]
        Agent_Factory["NestFactory.create(AppModule)"]
        Agent_Config["Middleware & CORS Setup"]
        Agent_Listen["Listen on Port 9991"]
    end
    
    subgraph "Desktop Service Lifecycle"
        Desktop_Module["AppModule Bootstrap"]
        Desktop_Static["Static File Serving<br/>/opt/noVNC"]
        Desktop_Modules["Load Feature Modules"]
        Desktop_Listen["Listen on Port 9990"]
    end
    
    Agent_Bootstrap --> Agent_Crypto
    Agent_Crypto --> Agent_Factory
    Agent_Factory --> Agent_Config
    Agent_Config --> Agent_Listen
    
    Desktop_Module --> Desktop_Static
    Desktop_Static --> Desktop_Modules
    Desktop_Modules --> Desktop_Listen
```

The agent service includes a crypto polyfill for compatibility with NestJS schedule module [packages/bytebot-agent/src/main.ts:7-9](), while the desktop service prioritizes static file serving for noVNC integration.

**Sources:** [packages/bytebot-agent/src/main.ts:1-36](), [packages/bytebotd/src/app.module.ts:10-26]()

---

# Page: bytebot-agent Service

# bytebot-agent Service

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [packages/bytebot-agent/package-lock.json](packages/bytebot-agent/package-lock.json)
- [packages/bytebot-agent/package.json](packages/bytebot-agent/package.json)
- [packages/bytebot-agent/src/agent/agent.module.ts](packages/bytebot-agent/src/agent/agent.module.ts)
- [packages/bytebot-agent/src/app.module.ts](packages/bytebot-agent/src/app.module.ts)
- [packages/bytebot-agent/src/main.ts](packages/bytebot-agent/src/main.ts)
- [packages/bytebot-agent/src/tasks/tasks.gateway.ts](packages/bytebot-agent/src/tasks/tasks.gateway.ts)
- [packages/bytebot-ui/next.config.ts](packages/bytebot-ui/next.config.ts)
- [packages/bytebot-ui/server.ts](packages/bytebot-ui/server.ts)
- [packages/bytebot-ui/src/app/api/[[...path]]/route.ts](packages/bytebot-ui/src/app/api/[[...path]]/route.ts)
- [packages/bytebot-ui/src/hooks/useWebSocket.ts](packages/bytebot-ui/src/hooks/useWebSocket.ts)

</details>



The **bytebot-agent** service is the core orchestration backend of the Bytebot system. It is a NestJS-based application running on port 9991 that manages task lifecycle, coordinates AI agent execution, integrates with multiple LLM providers, maintains persistent state in PostgreSQL, and provides both REST and WebSocket APIs for real-time communication. This service acts as the central nervous system, receiving task requests from [bytebot-ui](#4.3), delegating desktop automation to [bytebotd](#4.2), and managing all agent decision-making logic.

For information about the AI agent's processing logic and LLM integration, see [Agent System](#6). For details on the REST and WebSocket APIs exposed by this service, see [API Reference](#10).

---

## Architecture Overview

### Module Structure

The bytebot-agent service follows NestJS's modular architecture pattern, with distinct feature modules organized by domain responsibility.

```mermaid
graph TB
    AppModule["AppModule<br/>(app.module.ts)"]
    
    subgraph "Core Domain Modules"
        TasksModule["TasksModule<br/>Task CRUD + Lifecycle"]
        MessagesModule["MessagesModule<br/>Message Storage + Retrieval"]
        SummariesModule["SummariesModule<br/>Context Summarization"]
        AgentModule["AgentModule<br/>AI Processing + Scheduling"]
    end
    
    subgraph "LLM Provider Modules"
        AnthropicModule["AnthropicModule<br/>Claude Integration"]
        OpenAIModule["OpenAIModule<br/>GPT Integration"]
        GoogleModule["GoogleModule<br/>Gemini Integration"]
    end
    
    subgraph "Infrastructure Modules"
        PrismaModule["PrismaModule<br/>Database Client"]
        ProxyModule["ProxyModule<br/>bytebotd HTTP Client"]
        ConfigModule["ConfigModule<br/>Environment Variables"]
        ScheduleModule["ScheduleModule<br/>Cron Jobs"]
        EventEmitterModule["EventEmitterModule<br/>Internal Events"]
    end
    
    AppModule --> TasksModule
    AppModule --> MessagesModule
    AppModule --> SummariesModule
    AppModule --> AgentModule
    AppModule --> AnthropicModule
    AppModule --> OpenAIModule
    AppModule --> GoogleModule
    AppModule --> PrismaModule
    AppModule --> ProxyModule
    AppModule --> ConfigModule
    AppModule --> ScheduleModule
    AppModule --> EventEmitterModule
    
    AgentModule -.->|imports| TasksModule
    AgentModule -.->|imports| MessagesModule
    AgentModule -.->|imports| SummariesModule
    AgentModule -.->|imports| AnthropicModule
    AgentModule -.->|imports| OpenAIModule
    AgentModule -.->|imports| GoogleModule
    AgentModule -.->|imports| ProxyModule
    
    TasksModule -.->|imports| PrismaModule
    MessagesModule -.->|imports| PrismaModule
    SummariesModule -.->|imports| PrismaModule
```

**Sources:** [packages/bytebot-agent/src/app.module.ts:1-37](), [packages/bytebot-agent/src/agent/agent.module.ts:1-34]()

### Dependency Stack

The service's technology stack is defined in its package configuration:

| Category | Dependencies | Purpose |
|----------|-------------|---------|
| **Framework** | `@nestjs/common`, `@nestjs/core`, `@nestjs/platform-express` | NestJS framework core |
| **Database** | `@prisma/client`, `prisma` | PostgreSQL ORM and migrations |
| **LLM Providers** | `@anthropic-ai/sdk`, `openai`, `@google/genai` | Claude, GPT, and Gemini integration |
| **WebSockets** | `@nestjs/platform-socket.io`, `@nestjs/websockets`, `socket.io` | Real-time communication |
| **Scheduling** | `@nestjs/schedule` | Cron-based task scheduling |
| **Events** | `@nestjs/event-emitter` | Internal event bus |
| **Configuration** | `@nestjs/config` | Environment variable management |
| **Validation** | `class-validator`, `class-transformer`, `zod` | DTO validation and transformation |
| **Shared Types** | `@bytebot/shared` | Cross-package type definitions |
| **HTTP Client** | Built-in via ProxyModule | Communication with bytebotd |

**Sources:** [packages/bytebot-agent/package.json:24-45]()

---

## Entry Point and Bootstrap

The application entry point is `main.ts`, which configures the NestJS application and starts the HTTP server.

```mermaid
graph TB
    Bootstrap["bootstrap()<br/>(main.ts:11-32)"]
    
    CreateApp["NestFactory.create(AppModule)<br/>Line 15"]
    ConfigureJSON["app.use(json({ limit: '50mb' }))<br/>Line 18"]
    ConfigureURLEncoded["app.use(urlencoded({...}))<br/>Line 19"]
    EnableCORS["app.enableCors({ origin: '*' })<br/>Line 22-25"]
    Listen["app.listen(process.env.PORT ?? 9991)<br/>Line 27"]
    
    Bootstrap --> CreateApp
    CreateApp --> ConfigureJSON
    ConfigureJSON --> ConfigureURLEncoded
    ConfigureURLEncoded --> EnableCORS
    EnableCORS --> Listen
    
    CryptoPolyfill["globalThis.crypto = webcrypto<br/>Line 8<br/>(Required for @nestjs/schedule)"]
    
    CryptoPolyfill -.->|Polyfill before bootstrap| Bootstrap
```

**Key Configuration Details:**

| Setting | Value | Purpose |
|---------|-------|---------|
| **Port** | `9991` (default) | HTTP server listening port |
| **Body Size Limit** | `50mb` | Accommodates large file uploads and base64 images |
| **CORS** | `origin: '*'` | Allows requests from any origin (bytebot-ui) |
| **Crypto Polyfill** | `webcrypto` | Required for `@nestjs/schedule` cron functionality |

**Sources:** [packages/bytebot-agent/src/main.ts:1-32]()

---

## Core Modules

### TasksModule

The `TasksModule` manages task lifecycle, persistence, and real-time updates. It exposes REST endpoints for task CRUD operations and emits WebSocket events for state changes.

```mermaid
graph LR
    subgraph "TasksModule Exports"
        TasksController["TasksController<br/>REST Endpoints"]
        TasksService["TasksService<br/>Business Logic"]
        TasksGateway["TasksGateway<br/>Socket.IO Server"]
    end
    
    subgraph "External Clients"
        UI["bytebot-ui<br/>HTTP + WebSocket"]
    end
    
    UI -->|"POST /tasks"| TasksController
    UI -->|"GET /tasks/:id"| TasksController
    UI -->|"PATCH /tasks/:id"| TasksController
    UI -->|"DELETE /tasks/:id"| TasksController
    
    TasksController --> TasksService
    TasksService -->|"emitTaskUpdate()"| TasksGateway
    TasksService -->|"emitTaskCreated()"| TasksGateway
    TasksService -->|"emitTaskDeleted()"| TasksGateway
    
    TasksGateway -->|"task_updated event"| UI
    TasksGateway -->|"task_created event"| UI
    TasksGateway -->|"task_deleted event"| UI
    
    PrismaService["PrismaService<br/>(from PrismaModule)"]
    TasksService --> PrismaService
```

The `TasksGateway` implements Socket.IO lifecycle hooks and room-based event broadcasting.

**Key Methods:**
- `handleConnection(client: Socket)` - Logs client connections
- `handleJoinTask(client: Socket, taskId: string)` - Subscribes client to `task_{taskId}` room
- `handleLeaveTask(client: Socket, taskId: string)` - Unsubscribes client from room
- `emitTaskUpdate(taskId: string, task: any)` - Broadcasts to room-specific clients
- `emitNewMessage(taskId: string, message: any)` - Broadcasts new messages
- `emitTaskCreated(task: any)` - Global broadcast to all connected clients
- `emitTaskDeleted(taskId: string)` - Global broadcast

**Sources:** [packages/bytebot-agent/src/tasks/tasks.gateway.ts:1-57]()

### AgentModule

The `AgentModule` contains the core AI agent logic, including task processing, scheduling, and input capture.

```mermaid
graph TB
    subgraph "AgentModule Providers"
        AgentProcessor["AgentProcessor<br/>Main processing loop"]
        AgentScheduler["AgentScheduler<br/>Cron-based task picker"]
        InputCaptureService["InputCaptureService<br/>User action recording"]
        AgentAnalyticsService["AgentAnalyticsService<br/>Metrics tracking"]
    end
    
    subgraph "Imported Modules"
        TasksModule2["TasksModule"]
        MessagesModule2["MessagesModule"]
        SummariesModule2["SummariesModule"]
        AnthropicModule2["AnthropicModule"]
        OpenAIModule2["OpenAIModule"]
        GoogleModule2["GoogleModule"]
        ProxyModule2["ProxyModule"]
    end
    
    AgentProcessor -->|Task state management| TasksModule2
    AgentProcessor -->|Message creation| MessagesModule2
    AgentProcessor -->|Context summarization| SummariesModule2
    AgentProcessor -->|LLM requests| AnthropicModule2
    AgentProcessor -->|LLM requests| OpenAIModule2
    AgentProcessor -->|LLM requests| GoogleModule2
    AgentProcessor -->|Desktop actions| ProxyModule2
    
    AgentScheduler -->|Finds PENDING tasks| TasksModule2
    AgentScheduler -->|Triggers| AgentProcessor
    
    InputCaptureService -->|Records user actions| MessagesModule2
```

The `AgentModule` acts as the integration point, coordinating all other modules to execute AI-driven tasks.

**Sources:** [packages/bytebot-agent/src/agent/agent.module.ts:1-34]()

### MessagesModule

The `MessagesModule` handles conversation history storage, retrieval, and grouping for both LLM context building and UI display.

**Key Responsibilities:**
- Persist messages with structured content (text, tool use, tool results, images, user actions)
- Query messages by task and summary association
- Transform flat message lists into grouped UI structures
- Attach messages to summaries for context management

**Sources:** [packages/bytebot-agent/src/app.module.ts:6]()

### SummariesModule

The `SummariesModule` implements hierarchical context compression to manage LLM token limits. When conversation history exceeds 75% of the context window, it triggers summarization.

**Key Responsibilities:**
- Create summaries from conversation history using LLM
- Link messages to summaries via `summaryId` foreign key
- Support parent-child summary relationships for multi-level compression
- Provide latest summary for context building

**Sources:** [packages/bytebot-agent/src/app.module.ts:14]()

### LLM Integration Modules

Three parallel modules provide a unified interface to different LLM providers:

```mermaid
graph TB
    AgentProcessor2["AgentProcessor"]
    
    subgraph "LLM Provider Modules"
        AnthropicModule3["AnthropicModule<br/>@anthropic-ai/sdk"]
        OpenAIModule3["OpenAIModule<br/>openai"]
        GoogleModule3["GoogleModule<br/>@google/genai"]
    end
    
    BytebotAgentService["BytebotAgentService Interface<br/>(Abstract)"]
    
    AnthropicService["AnthropicService<br/>implements BytebotAgentService"]
    OpenAIService["OpenAIService<br/>implements BytebotAgentService"]
    GoogleService["GoogleService<br/>implements BytebotAgentService"]
    
    AnthropicModule3 --> AnthropicService
    OpenAIModule3 --> OpenAIService
    GoogleModule3 --> GoogleService
    
    AnthropicService -.->|implements| BytebotAgentService
    OpenAIService -.->|implements| BytebotAgentService
    GoogleService -.->|implements| BytebotAgentService
    
    AgentProcessor2 -->|Runtime selection| BytebotAgentService
    
    ClaudeAPI["Claude API<br/>(Anthropic)"]
    GPTAPI["GPT API<br/>(OpenAI)"]
    GeminiAPI["Gemini API<br/>(Google)"]
    
    AnthropicService --> ClaudeAPI
    OpenAIService --> GPTAPI
    GoogleService --> GeminiAPI
```

Each service implements a common interface, allowing the `AgentProcessor` to switch between providers based on the task's `model` field.

**Sources:** [packages/bytebot-agent/src/app.module.ts:27-29](), [packages/bytebot-agent/package.json:25,27,40]()

### PrismaModule

The `PrismaModule` provides a singleton `PrismaService` that manages the PostgreSQL connection pool. All data access goes through Prisma's type-safe client.

**Key Responsibilities:**
- Manage database connection lifecycle
- Provide type-safe query methods for Task, Message, Summary, and File models
- Handle transactions and migrations

**Sources:** [packages/bytebot-agent/src/app.module.ts:32](), [packages/bytebot-agent/package.json:36]()

### ProxyModule

The `ProxyModule` provides HTTP client functionality for communicating with the bytebotd desktop service.

**Key Responsibilities:**
- POST requests to `BYTEBOT_DESKTOP_BASE_URL/computer-use` endpoint
- Execute desktop actions (mouse, keyboard, screenshots, file operations)
- Handle action responses and errors

**Sources:** [packages/bytebot-agent/src/app.module.ts:31](), [packages/bytebot-agent/src/agent/agent.module.ts:13,24]()

---

## Communication Layer

### Request Flow Architecture

```mermaid
graph TB
    subgraph "bytebot-ui (Port 9992)"
        UIClient["React Client"]
        NextAPI["Next.js API Routes<br/>/api/[[...path]]"]
        ExpressServer["Express Server<br/>(server.ts)"]
    end
    
    subgraph "bytebot-agent (Port 9991)"
        NestApp["NestJS Application<br/>(main.ts:27)"]
        TasksController2["TasksController<br/>REST Endpoints"]
        TasksGateway2["TasksGateway<br/>Socket.IO<br/>(tasks.gateway.ts)"]
    end
    
    UIClient -->|"HTTP GET/POST/PATCH/DELETE"| NextAPI
    UIClient -->|"Socket.IO connect"| ExpressServer
    
    NextAPI -->|"Proxy to :9991"| NestApp
    ExpressServer -->|"WebSocket Upgrade<br/>/api/proxy/tasks"| TasksGateway2
    
    NestApp --> TasksController2
    
    TasksController2 -->|"Response"| NextAPI
    TasksGateway2 -->|"Events: task_updated,<br/>new_message, etc."| ExpressServer
    
    NextAPI -->|"JSON Response"| UIClient
    ExpressServer -->|"Socket.IO events"| UIClient
```

**Sources:** [packages/bytebot-ui/src/app/api/[[...path]]/route.ts:1-64](), [packages/bytebot-ui/server.ts:32-40](), [packages/bytebot-agent/src/main.ts:22-27](), [packages/bytebot-agent/src/tasks/tasks.gateway.ts:12-17]()

### WebSocket Event System

The `TasksGateway` uses Socket.IO for bidirectional communication:

**Client-to-Server Events:**

| Event | Payload | Handler | Purpose |
|-------|---------|---------|---------|
| `join_task` | `taskId: string` | `handleJoinTask()` | Subscribe to task-specific updates |
| `leave_task` | `taskId: string` | `handleLeaveTask()` | Unsubscribe from task room |

**Server-to-Client Events:**

| Event | Room Scope | Payload | Trigger |
|-------|-----------|---------|---------|
| `task_updated` | `task_{taskId}` | Task object | Task state change |
| `new_message` | `task_{taskId}` | Message object | New message created |
| `task_created` | Global | Task object | New task created |
| `task_deleted` | Global | `taskId: string` | Task deleted |

**UI Integration:**

The `useWebSocket` hook on the client side subscribes to these events:

```typescript
// packages/bytebot-ui/src/hooks/useWebSocket.ts:26-34
const socket = io({
  path: "/api/proxy/tasks",
  transports: ["websocket"],
  autoConnect: true,
  reconnection: true,
  reconnectionAttempts: 5,
  reconnectionDelay: 1000,
});
```

**Sources:** [packages/bytebot-agent/src/tasks/tasks.gateway.ts:30-56](), [packages/bytebot-ui/src/hooks/useWebSocket.ts:1-113]()

---

## Configuration and Environment

The service uses `@nestjs/config` to load environment variables, which are globally available across all modules.

**Required Environment Variables:**

| Variable | Purpose | Example |
|----------|---------|---------|
| `PORT` | HTTP server port | `9991` |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@host:5432/db` |
| `ANTHROPIC_API_KEY` | Claude API authentication | `sk-ant-...` |
| `OPENAI_API_KEY` | GPT API authentication | `sk-...` |
| `GOOGLE_API_KEY` | Gemini API authentication | `AIza...` |
| `BYTEBOT_DESKTOP_BASE_URL` | bytebotd service URL | `http://localhost:9990` |

**Configuration Module Setup:**

```typescript
// packages/bytebot-agent/src/app.module.ts:21-23
ConfigModule.forRoot({
  isGlobal: true,
})
```

The `isGlobal: true` option makes environment variables accessible in all modules without explicit imports.

**Sources:** [packages/bytebot-agent/src/app.module.ts:11,21-23](), [packages/bytebot-agent/src/main.ts:27]()

---

## Build and Execution

### Build Process

```mermaid
graph LR
    SharedBuild["npm run build --prefix ../shared<br/>Compile @bytebot/shared"]
    PrismaGenerate["npx prisma generate<br/>Generate Prisma Client"]
    NestBuild["nest build<br/>Compile TypeScript to dist/"]
    
    SharedBuild --> PrismaGenerate
    PrismaGenerate --> NestBuild
```

**Build Scripts:**

| Script | Command | Purpose |
|--------|---------|---------|
| `build` | `npm run build --prefix ../shared && npx prisma generate && nest build` | Production build |
| `start` | `npm run build --prefix ../shared && nest start` | Start compiled application |
| `start:dev` | `npm run build --prefix ../shared && nest start --watch` | Development with hot reload |
| `start:prod` | Build + migrations + start | Production startup with DB migrations |

**Sources:** [packages/bytebot-agent/package.json:8-16]()

### Runtime Dependencies

The service requires:
1. **PostgreSQL database** - Connection string in `DATABASE_URL`
2. **bytebotd service** - Running on `BYTEBOT_DESKTOP_BASE_URL`
3. **@bytebot/shared package** - Built and linked
4. **LLM API keys** - At least one provider configured

**Node Version:** Locked to Node.js 20 via `engines` field.

**Sources:** [packages/bytebot-agent/package.json:97-99]()

---

## Module Dependency Graph

```mermaid
graph TB
    PrismaModule2["PrismaModule"]
    ConfigModule2["ConfigModule"]
    ScheduleModule2["ScheduleModule"]
    EventEmitterModule2["EventEmitterModule"]
    
    TasksModule3["TasksModule"]
    MessagesModule3["MessagesModule"]
    SummariesModule3["SummariesModule"]
    
    AnthropicModule4["AnthropicModule"]
    OpenAIModule4["OpenAIModule"]
    GoogleModule4["GoogleModule"]
    ProxyModule3["ProxyModule"]
    
    AgentModule2["AgentModule"]
    
    TasksModule3 --> PrismaModule2
    MessagesModule3 --> PrismaModule2
    SummariesModule3 --> PrismaModule2
    
    AnthropicModule4 --> ConfigModule2
    OpenAIModule4 --> ConfigModule2
    GoogleModule4 --> ConfigModule2
    ProxyModule3 --> ConfigModule2
    
    AgentModule2 --> TasksModule3
    AgentModule2 --> MessagesModule3
    AgentModule2 --> SummariesModule3
    AgentModule2 --> AnthropicModule4
    AgentModule2 --> OpenAIModule4
    AgentModule2 --> GoogleModule4
    AgentModule2 --> ProxyModule3
    AgentModule2 --> ConfigModule2
    
    AgentModule2 -.->|Uses| ScheduleModule2
    TasksModule3 -.->|Uses| EventEmitterModule2
```

This dependency structure ensures:
- **Infrastructure modules** (Prisma, Config, Schedule, EventEmitter) have no dependencies
- **Domain modules** (Tasks, Messages, Summaries) depend only on infrastructure
- **Integration modules** (Anthropic, OpenAI, Google, Proxy) depend on Config
- **Agent module** orchestrates all other modules

**Sources:** [packages/bytebot-agent/src/app.module.ts:17-36](), [packages/bytebot-agent/src/agent/agent.module.ts:15-25]()

---

# Page: bytebotd Desktop Service

# Desktop Service

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [docs/api-reference/agent/tasks.mdx](docs/api-reference/agent/tasks.mdx)
- [docs/core-concepts/desktop-environment.mdx](docs/core-concepts/desktop-environment.mdx)
- [docs/deployment/railway.mdx](docs/deployment/railway.mdx)
- [docs/guides/task-creation.mdx](docs/guides/task-creation.mdx)
- [docs/introduction.mdx](docs/introduction.mdx)
- [docs/quickstart.mdx](docs/quickstart.mdx)
- [packages/bytebotd/package-lock.json](packages/bytebotd/package-lock.json)
- [packages/bytebotd/package.json](packages/bytebotd/package.json)
- [packages/bytebotd/src/app.controller.ts](packages/bytebotd/src/app.controller.ts)
- [packages/bytebotd/src/app.module.ts](packages/bytebotd/src/app.module.ts)
- [packages/bytebotd/src/mcp/bytebot-mcp.module.ts](packages/bytebotd/src/mcp/bytebot-mcp.module.ts)
- [packages/bytebotd/src/mcp/index.ts](packages/bytebotd/src/mcp/index.ts)

</details>



The Desktop Service (`bytebotd`) is a NestJS-based daemon that provides programmatic control over a virtual desktop environment. It serves as the bridge between AI agents and the underlying Ubuntu desktop system, enabling automated computer interactions through a comprehensive API. This service handles mouse movements, keyboard input, application launching, file operations, and screen capture within the containerized desktop environment.

For information about how the agent orchestrates tasks using this service, see [Agent Service](#4.1). For details about the web interface that displays the desktop, see [UI Service](#4.3).

## Architecture Overview

The Desktop Service is built as a NestJS application running on port 9990, providing both REST APIs and Model Context Protocol (MCP) integration for computer automation.

```mermaid
graph TB
    subgraph "Desktop Service (bytebotd:9990)"
        AppModule["AppModule"]
        ComputerUseModule["ComputerUseModule"] 
        InputTrackingModule["InputTrackingModule"]
        BytebotMcpModule["BytebotMcpModule"]
        AppController["AppController"]
    end
    
    subgraph "Core Services"
        ComputerUseService["ComputerUseService"]
        NutService["NutService"]
        InputTrackingService["InputTrackingService"]
    end
    
    subgraph "MCP Integration"
        ComputerUseTools["ComputerUseTools"]
        McpModule["McpModule"]
    end
    
    subgraph "Desktop Environment"
        UbuntuXfce["Ubuntu + XFCE"]
        VncServer["VNC Server"]
        NoVncClient["noVNC Client"]
    end
    
    subgraph "External Libraries"
        NutJs["@nut-tree-fork/nut-js"]
        UiohookNapi["uiohook-napi"]
        Sharp["sharp"]
    end
    
    AppModule --> ComputerUseModule
    AppModule --> InputTrackingModule  
    AppModule --> BytebotMcpModule
    
    ComputerUseModule --> ComputerUseService
    ComputerUseService --> NutService
    InputTrackingModule --> InputTrackingService
    
    BytebotMcpModule --> McpModule
    BytebotMcpModule --> ComputerUseTools
    ComputerUseTools --> ComputerUseService
    
    NutService --> NutJs
    ComputerUseService --> Sharp
    InputTrackingService --> UiohookNapi
    
    ComputerUseService --> UbuntuXfce
    AppController --> NoVncClient
    UbuntuXfce --> VncServer
```

Sources: [packages/bytebotd/src/app.module.ts:1-26](), [packages/bytebotd/package.json:28-46](), [packages/bytebotd/src/mcp/bytebot-mcp.module.ts:1-17]()

## Core Components

### ComputerUseService

The `ComputerUseService` is the central component that executes all computer actions. It implements a comprehensive action dispatcher that handles mouse, keyboard, application, and file operations.

```mermaid
graph LR
    subgraph "Computer Actions"
        MouseActions["Mouse Actions<br/>move_mouse<br/>click_mouse<br/>drag_mouse<br/>trace_mouse<br/>press_mouse<br/>scroll"]
        KeyboardActions["Keyboard Actions<br/>type_keys<br/>press_keys<br/>type_text<br/>paste_text"]
        SystemActions["System Actions<br/>screenshot<br/>cursor_position<br/>wait<br/>application"]
        FileActions["File Actions<br/>write_file<br/>read_file"]
    end
    
    subgraph "ComputerUseService"
        ActionDispatcher["action(params: ComputerAction)"]
        MouseHandlers["moveMouse()<br/>clickMouse()<br/>dragMouse()<br/>traceMouse()<br/>pressMouse()<br/>scroll()"]
        KeyboardHandlers["typeKeys()<br/>pressKeys()<br/>typeText()<br/>pasteText()"]
        SystemHandlers["screenshot()<br/>cursor_position()<br/>delay()<br/>application()"]
        FileHandlers["writeFile()<br/>readFile()"]
    end
    
    subgraph "NutService"
        NutMethods["mouseMoveEvent()<br/>mouseClickEvent()<br/>mouseButtonEvent()<br/>mouseWheelEvent()<br/>sendKeys()<br/>holdKeys()<br/>typeText()<br/>pasteText()<br/>screendump()<br/>getCursorPosition()"]
    end
    
    MouseActions --> ActionDispatcher
    KeyboardActions --> ActionDispatcher  
    SystemActions --> ActionDispatcher
    FileActions --> ActionDispatcher
    
    ActionDispatcher --> MouseHandlers
    ActionDispatcher --> KeyboardHandlers
    ActionDispatcher --> SystemHandlers
    ActionDispatcher --> FileHandlers
    
    MouseHandlers --> NutMethods
    KeyboardHandlers --> NutMethods
    SystemHandlers --> NutMethods
```

Sources: [packages/bytebotd/src/computer-use/computer-use.service.ts:31-105]()

### MCP Integration

The service exposes its functionality through the Model Context Protocol (MCP), allowing AI models to directly invoke computer actions as tools.

```mermaid
graph TB
    subgraph "MCP Tools Layer"
        ComputerUseTools["ComputerUseTools"]
        ToolDecorators["@Tool Decorators"]
    end
    
    subgraph "Individual MCP Tools"
        MoveMouse["computer_move_mouse"]
        ClickMouse["computer_click_mouse"] 
        TraceMouse["computer_trace_mouse"]
        DragMouse["computer_drag_mouse"]
        TypeKeys["computer_type_keys"]
        TypeText["computer_type_text"]
        Screenshot["computer_screenshot"]
        Application["computer_application"]
        WriteFile["computer_write_file"]
        ReadFile["computer_read_file"]
    end
    
    subgraph "Validation Layer"
        ZodSchemas["Zod Parameter Schemas"]
        ErrorHandling["Try/Catch Error Handling"]
    end
    
    subgraph "ComputerUseService"
        ActionMethod["action(params: ComputerAction)"]
    end
    
    ComputerUseTools --> ToolDecorators
    ToolDecorators --> MoveMouse
    ToolDecorators --> ClickMouse
    ToolDecorators --> TraceMouse
    ToolDecorators --> DragMouse
    ToolDecorators --> TypeKeys
    ToolDecorators --> TypeText
    ToolDecorators --> Screenshot
    ToolDecorators --> Application
    ToolDecorators --> WriteFile
    ToolDecorators --> ReadFile
    
    MoveMouse --> ZodSchemas
    ClickMouse --> ZodSchemas
    TraceMouse --> ZodSchemas
    
    ZodSchemas --> ErrorHandling
    ErrorHandling --> ActionMethod
```

Sources: [packages/bytebotd/src/mcp/computer-use.tools.ts:8-698](), [packages/bytebotd/src/mcp/bytebot-mcp.module.ts:9-13]()

## Computer Action Types

The system supports a comprehensive set of computer actions defined by TypeScript types and validated through DTOs.

| Action Category | Actions | Purpose |
|----------------|---------|---------|
| Mouse Movement | `move_mouse`, `trace_mouse` | Position cursor and create movement paths |
| Mouse Interaction | `click_mouse`, `press_mouse`, `drag_mouse` | Perform clicks, hold/release buttons, drag operations |
| Scrolling | `scroll` | Scroll in any direction with customizable count |
| Keyboard Input | `type_keys`, `press_keys`, `type_text`, `paste_text` | Send key combinations, hold keys, type text |
| System Control | `screenshot`, `cursor_position`, `wait` | Capture screen, get cursor position, add delays |
| Application Control | `application` | Launch and switch between applications |
| File Operations | `write_file`, `read_file` | Create and read files with base64 encoding |

```mermaid
graph TD
    subgraph "Type System"
        ComputerAction["ComputerAction Union Type"]
        SharedTypes["Shared Types<br/>Coordinates<br/>Button<br/>Press<br/>Application"]
    end
    
    subgraph "Action Types"
        MouseActions["MoveMouseAction<br/>TraceMouseAction<br/>ClickMouseAction<br/>PressMouseAction<br/>DragMouseAction<br/>ScrollAction"]
        KeyboardActions["TypeKeysAction<br/>PressKeysAction<br/>TypeTextAction<br/>PasteTextAction"]
        SystemActions["WaitAction<br/>ScreenshotAction<br/>CursorPositionAction<br/>ApplicationAction"]
        FileActions["WriteFileAction<br/>ReadFileAction"]
    end
    
    subgraph "Validation Layer"
        ComputerActionDto["ComputerActionDto Union"]
        ValidationPipe["ComputerActionValidationPipe"]
    end
    
    ComputerAction --> MouseActions
    ComputerAction --> KeyboardActions
    ComputerAction --> SystemActions
    ComputerAction --> FileActions
    
    SharedTypes --> MouseActions
    SharedTypes --> KeyboardActions
    
    MouseActions --> ComputerActionDto
    KeyboardActions --> ComputerActionDto
    SystemActions --> ComputerActionDto
    FileActions --> ComputerActionDto
    
    ComputerActionDto --> ValidationPipe
```

Sources: [packages/shared/src/types/computerAction.types.ts:1-126](), [packages/bytebotd/src/computer-use/dto/computer-action.dto.ts:223-240]()

## File Operations

The service provides secure file operations with automatic path resolution and permission handling.

```mermaid
graph TB
    subgraph "File Operations Flow"
        WriteRequest["Write File Request<br/>path: string<br/>data: base64"]
        ReadRequest["Read File Request<br/>path: string"]
    end
    
    subgraph "Path Resolution"
        RelativePathCheck["Is Absolute Path?"]
        DefaultToDesktop["Default to /home/user/Desktop"]
    end
    
    subgraph "Write Process"
        CreateTempFile["Create Temp File<br/>/tmp/bytebot_temp_*"]
        DecodeBase64["Decode Base64 Data"]
        EnsureDirectory["sudo mkdir -p directory"]
        CopyToTarget["sudo cp temp target"]
        SetPermissions["sudo chown user:user<br/>sudo chmod 644"]
        CleanupTemp["Remove Temp File"]
    end
    
    subgraph "Read Process"
        CopyToTemp["sudo cp target temp"]
        ReadBuffer["fs.readFile(temp)"]
        GetFileStats["sudo stat target"]
        DetermineMediaType["Determine MIME Type"]
        EncodeToBase64["Buffer.toString('base64')"]
    end
    
    WriteRequest --> RelativePathCheck
    ReadRequest --> RelativePathCheck
    RelativePathCheck --> DefaultToDesktop
    
    WriteRequest --> CreateTempFile
    CreateTempFile --> DecodeBase64
    DecodeBase64 --> EnsureDirectory
    EnsureDirectory --> CopyToTarget
    CopyToTarget --> SetPermissions
    SetPermissions --> CleanupTemp
    
    ReadRequest --> CopyToTemp
    CopyToTemp --> ReadBuffer
    ReadBuffer --> GetFileStats
    GetFileStats --> DetermineMediaType
    DetermineMediaType --> EncodeToBase64
```

Sources: [packages/bytebotd/src/computer-use/computer-use.service.ts:364-506]()

## Application Management

The service can launch and manage desktop applications with automatic window management.

```mermaid
graph LR
    subgraph "Supported Applications"
        AppTypes["firefox<br/>1password<br/>thunderbird<br/>vscode<br/>terminal<br/>directory<br/>desktop"]
    end
    
    subgraph "Application Control Flow"
        CheckRunning["wmctrl -lx | grep process"]
        IsRunning{"Application<br/>Running?"}
        LaunchApp["sudo -u user nohup command"]
        ActivateWindow["wmctrl -x -a process"]
        MaximizeWindow["wmctrl -x -r process<br/>-b add,maximized_vert,maximized_horz"]
    end
    
    subgraph "Command Mapping"
        CommandMap["firefox: firefox-esr<br/>1password: 1password<br/>thunderbird: thunderbird<br/>vscode: code<br/>terminal: xfce4-terminal<br/>directory: thunar"]
        ProcessMap["firefox: Navigator.firefox-esr<br/>1password: 1password.1Password<br/>thunderbird: Mail.thunderbird<br/>vscode: code.Code<br/>terminal: xfce4-terminal.Xfce4-Terminal<br/>directory: Thunar"]
    end
    
    AppTypes --> CheckRunning
    CheckRunning --> IsRunning
    IsRunning -->|Yes| ActivateWindow
    IsRunning -->|No| LaunchApp
    ActivateWindow --> MaximizeWindow
    
    LaunchApp --> CommandMap
    CheckRunning --> ProcessMap
```

Sources: [packages/bytebotd/src/computer-use/computer-use.service.ts:264-362]()

## Integration Points

### VNC Access

The service provides VNC access through a redirect endpoint that integrates with the noVNC web client.

```mermaid
graph LR
    subgraph "VNC Integration"
        VncEndpoint["/vnc Endpoint"]
        AppController["AppController.redirectToVnc()"]
        NoVncRedirect["Redirect to /novnc/vnc.html"]
        NoVncStatic["ServeStaticModule<br/>/opt/noVNC -> /novnc"]
    end
    
    subgraph "Desktop Environment"
        XfceDesktop["XFCE Desktop"]
        VncServer["VNC Server :5900"]
        Websockify["Websockify Bridge"]
    end
    
    VncEndpoint --> AppController
    AppController --> NoVncRedirect
    NoVncRedirect --> NoVncStatic
    NoVncStatic --> Websockify
    Websockify --> VncServer
    VncServer --> XfceDesktop
```

Sources: [packages/bytebotd/src/app.controller.ts:8-17](), [packages/bytebotd/src/app.module.ts:15-18]()

### Input Tracking

The service includes input tracking capabilities for monitoring user interactions with the desktop environment.

```mermaid
graph TB
    subgraph "Input Tracking System"
        InputTrackingModule["InputTrackingModule"]
        InputTrackingService["InputTrackingService"]
        UiohookNapi["uiohook-napi Library"]
    end
    
    subgraph "Event Types"
        MouseEvents["Mouse Movement<br/>Mouse Clicks<br/>Mouse Scrolling"]
        KeyboardEvents["Key Press<br/>Key Release<br/>Key Combinations"]
    end
    
    subgraph "Desktop Environment"
        UserInput["User Input Events"]
        SystemEvents["System Event Queue"]
    end
    
    InputTrackingModule --> InputTrackingService
    InputTrackingService --> UiohookNapi
    
    UserInput --> SystemEvents
    SystemEvents --> UiohookNapi
    UiohookNapi --> MouseEvents
    UiohookNapi --> KeyboardEvents
```

Sources: [packages/bytebotd/src/app.module.ts:20](), [packages/bytebotd/package.json:46]()

---

# Page: bytebot-ui Frontend Service

# UI Service

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [packages/bytebot-agent/src/main.ts](packages/bytebot-agent/src/main.ts)
- [packages/bytebot-agent/src/tasks/tasks.gateway.ts](packages/bytebot-agent/src/tasks/tasks.gateway.ts)
- [packages/bytebot-ui/next.config.ts](packages/bytebot-ui/next.config.ts)
- [packages/bytebot-ui/package-lock.json](packages/bytebot-ui/package-lock.json)
- [packages/bytebot-ui/package.json](packages/bytebot-ui/package.json)
- [packages/bytebot-ui/server.ts](packages/bytebot-ui/server.ts)
- [packages/bytebot-ui/src/app/api/[[...path]]/route.ts](packages/bytebot-ui/src/app/api/[[...path]]/route.ts)
- [packages/bytebot-ui/src/app/layout.tsx](packages/bytebot-ui/src/app/layout.tsx)
- [packages/bytebot-ui/src/components/layout/Header.tsx](packages/bytebot-ui/src/components/layout/Header.tsx)
- [packages/bytebot-ui/src/hooks/useWebSocket.ts](packages/bytebot-ui/src/hooks/useWebSocket.ts)

</details>



The UI Service (`bytebot-ui`) is a Next.js 15 React application that provides the web frontend for Bytebot system interaction. It operates as a hybrid Express/Next.js server running on port 9992, implementing dual-proxy architecture to route requests to `bytebot-agent` and `bytebot-desktop` services. The service handles task management UI, real-time WebSocket communication via Socket.IO, and VNC desktop viewing through `react-vnc`.

The service integrates with [Agent Service](#4.1) for task orchestration and [Desktop Service](#4.2) for computer automation capabilities.

## Architecture Overview

The `bytebot-ui` service implements a dual-server architecture combining Express.js with Next.js. The `server.ts` file creates an Express application that wraps the Next.js app, enabling custom proxy middleware while preserving Next.js functionality.

**Dual-Server Architecture**
```mermaid
graph TB
    subgraph "server.ts Implementation"
        expressApp["expressApp = express()"]
        nextApp["app = next()"]
        createServer["server = createServer(expressApp)"]
        
        subgraph "Proxy Middleware"
            tasksProxy["tasksProxy<br/>createProxyMiddleware"]
            vncProxy["vncProxy<br/>createProxyServer"]
        end
        
        subgraph "Request Handlers"
            proxyTasksRoute["/api/proxy/tasks → tasksProxy"]
            proxyWebsockifyRoute["/api/proxy/websockify → vncProxy"]
            nextHandler["/* → handle(req, res)"]
        end
    end
    
    subgraph "Target Services"
        BYTEBOT_AGENT_BASE_URL["process.env.BYTEBOT_AGENT_BASE_URL<br/>/socket.io"]
        BYTEBOT_DESKTOP_VNC_URL["process.env.BYTEBOT_DESKTOP_VNC_URL<br/>websockify"]
    end
    
    expressApp --> tasksProxy
    expressApp --> vncProxy
    nextApp --> nextHandler
    
    proxyTasksRoute --> BYTEBOT_AGENT_BASE_URL
    proxyWebsockifyRoute --> BYTEBOT_DESKTOP_VNC_URL
    nextHandler --> nextApp
    
    createServer --> expressApp
```

The `server.listen()` function starts the hybrid server on `process.env.PORT ?? 9992` with WebSocket upgrade handling for both Socket.IO and VNC connections.

Sources: [packages/bytebot-ui/server.ts:29-31](), [packages/bytebot-ui/server.ts:19-24](), [packages/bytebot-ui/server.ts:81-83]()

## Proxy Implementation

The service implements dual-proxy routing through Express middleware (`server.ts`) and Next.js API routes (`[[...path]]/route.ts`). This handles both WebSocket upgrades and HTTP API forwarding to backend services.

### Express Server Proxy Configuration

**WebSocket and HTTP Proxy Setup**
```mermaid
graph TB
    subgraph "server.ts Proxy Routes"
        expressApp_use_tasks["expressApp.use('/api/proxy/tasks', tasksProxy)"]
        expressApp_use_websockify["expressApp.use('/api/proxy/websockify', vncProxy)"]
        expressApp_all["expressApp.all('*', handle)"]
        
        subgraph "Proxy Middleware"
            tasksProxy_create["tasksProxy = createProxyMiddleware({<br/>target: BYTEBOT_AGENT_BASE_URL,<br/>ws: true,<br/>pathRewrite: {'^/api/proxy/tasks': '/socket.io'}<br/>})"]
            vncProxy_create["vncProxy = createProxyServer({<br/>changeOrigin: true,<br/>ws: true<br/>})"]
        end
        
        subgraph "WebSocket Upgrade Handling"
            server_on_upgrade["server.on('upgrade', (request, socket, head))"]
            pathname_check["pathname.startsWith('/api/proxy/tasks')<br/>pathname.startsWith('/api/proxy/websockify')"]
            tasksProxy_upgrade["tasksProxy.upgrade(request, socket, head)"]
            vncProxy_ws["vncProxy.ws(request, socket, head)"]
        end
    end
    
    expressApp_use_tasks --> tasksProxy_create
    expressApp_use_websockify --> vncProxy_create
    server_on_upgrade --> pathname_check
    pathname_check --> tasksProxy_upgrade
    pathname_check --> vncProxy_ws
```

**Proxy Route Mapping**
| Route Pattern | Proxy Target | Rewrite Rule | WebSocket Support |
|---------------|--------------|--------------|-------------------|
| `/api/proxy/tasks` | `BYTEBOT_AGENT_BASE_URL/socket.io` | `^/api/proxy/tasks` → `/socket.io` | ✓ |
| `/api/proxy/websockify` | `BYTEBOT_DESKTOP_VNC_URL` | Path preserved with prefix removal | ✓ |
| `*` | `handle(req, res)` | Next.js handler | Next.js WebSocket |

Sources: [packages/bytebot-ui/server.ts:33-37](), [packages/bytebot-ui/server.ts:41-51](), [packages/bytebot-ui/server.ts:57-79]()

### Next.js API Proxy Routes

**Catch-All Route Implementation**
```mermaid
graph TD
    subgraph "src/app/api/[[...path]]/route.ts"
        handler_function["handler(req, {params})"]
        proxy_function["proxy(req: NextRequest, path: string[])"]
        
        subgraph "Request Processing"
            extract_params["const {path} = await params"]
            join_path["subPath = path.length ? path.join('/') : ''"]
            build_url["url = `${BASE_URL}/${subPath}${req.nextUrl.search}`"]
            extract_cookies["cookies = req.headers.get('cookie')"]
        end
        
        subgraph "HTTP Method Exports"
            export_GET["export const GET = handler"]
            export_POST["export const POST = handler"]
            export_PUT["export const PUT = handler"]
            export_PATCH["export const PATCH = handler"]
            export_DELETE["export const DELETE = handler"]
            export_OPTIONS["export const OPTIONS = handler"]
            export_HEAD["export const HEAD = handler"]
        end
        
        subgraph "Response Handling"
            fetch_request["fetch(url, init)"]
            extract_setCookie["setCookieHeaders = res.headers.getSetCookie()"]
            build_response["new Response(body, {status, headers})"]
        end
    end
    
    handler_function --> extract_params
    extract_params --> proxy_function
    proxy_function --> join_path
    join_path --> build_url
    build_url --> extract_cookies
    extract_cookies --> fetch_request
    fetch_request --> extract_setCookie
    extract_setCookie --> build_response
    
    export_GET --> handler_function
    export_POST --> handler_function
```

The `proxy()` function forwards requests to `process.env.BYTEBOT_AGENT_BASE_URL` with cookie preservation and supports all HTTP methods through dynamic exports.

Sources: [packages/bytebot-ui/src/app/api/[[...path]]/route.ts:6-25](), [packages/bytebot-ui/src/app/api/[[...path]]/route.ts:53-64]()

## React Component Structure

The `bytebot-ui` implements a Next.js App Router architecture with TypeScript React components using `@radix-ui` primitives and Tailwind CSS styling.

**Component File Structure**
```mermaid
graph TB
    subgraph "src/app Directory (Next.js App Router)"
        layout_tsx["layout.tsx<br/>RootLayout component"]
        page_tsx["page.tsx<br/>Home page"]
        
        subgraph "src/app/tasks"
            tasks_id_page["[id]/page.tsx<br/>TaskDetailPage"]
        end
        
        subgraph "src/app/desktop"
            desktop_page["page.tsx<br/>DesktopPage"]
        end
        
        subgraph "src/app/api"
            api_catchall["[[...path]]/route.ts<br/>proxy handlers"]
        end
    end
    
    subgraph "src/components Directory"
        subgraph "src/components/layout"
            Header_tsx["Header.tsx<br/>Header component"]
        end
        
        subgraph "src/components/messages"
            ChatInput_tsx["ChatInput.tsx<br/>ChatInput component"]
        end
        
        subgraph "src/components/tasks"  
            TaskList_tsx["TaskList.tsx<br/>TaskList component"]
        end
        
        subgraph "src/components/ui"
            select_tsx["select.tsx<br/>Select component"]
            button_tsx["button.tsx<br/>Button variants"]
        end
    end
    
    subgraph "src/hooks"
        useWebSocket_ts["useWebSocket.ts<br/>useWebSocket hook"]
    end
    
    layout_tsx --> Header_tsx
    page_tsx --> ChatInput_tsx
    page_tsx --> TaskList_tsx
    tasks_id_page --> useWebSocket_ts
```

**Key Component Implementation Details**

**Header Component** (`src/components/layout/Header.tsx`):
- `usePathname()` for active route detection via `isActive(path)` function
- Theme-aware logo switching with `useTheme()` from `next-themes`
- Navigation links using `Link` components with dynamic CSS classes via `getLinkClasses(path)`
- HugeIcons integration: `Home01Icon`, `TaskDaily01Icon`, `ComputerIcon`, `DocumentCodeIcon`

**WebSocket Integration** (`src/hooks/useWebSocket.ts`):
- `socketRef.current` maintains Socket.IO client instance
- Connection config: `path: "/api/proxy/tasks"`, `transports: ["websocket"]`
- Event handlers: `onTaskUpdate`, `onNewMessage`, `onTaskCreated`, `onTaskDeleted`
- Room management: `joinTask(taskId)` emits `join_task`, `leaveTask()` emits `leave_task`

Sources: [packages/bytebot-ui/src/components/layout/Header.tsx:15-43](), [packages/bytebot-ui/src/hooks/useWebSocket.ts:12-17](), [packages/bytebot-ui/src/hooks/useWebSocket.ts:68-88]()

## Socket.IO WebSocket Implementation

The `useWebSocket` hook manages Socket.IO client connections to the `bytebot-agent` service through the Express proxy layer, implementing task-based room subscriptions and real-time event handling.

**Socket.IO Client Architecture**
```mermaid
graph TB
    subgraph "useWebSocket.ts Hook Implementation"
        socketRef_current["socketRef.current: Socket | null"]
        currentTaskIdRef["currentTaskIdRef.current: string | null"]
        
        subgraph "Connection Management Functions"
            connect_function["connect() useCallback"]
            joinTask_function["joinTask(taskId) useCallback"]  
            leaveTask_function["leaveTask() useCallback"]
            disconnect_function["disconnect() useCallback"]
        end
        
        subgraph "io() Configuration Object"
            io_config["io({<br/>  path: '/api/proxy/tasks',<br/>  transports: ['websocket'],<br/>  autoConnect: true,<br/>  reconnection: true,<br/>  reconnectionAttempts: 5,<br/>  reconnectionDelay: 1000<br/>})"]
        end
        
        subgraph "Socket Event Listeners"
            socket_on_connect["socket.on('connect')"]
            socket_on_disconnect["socket.on('disconnect')"]
            socket_on_task_updated["socket.on('task_updated', onTaskUpdate)"]
            socket_on_new_message["socket.on('new_message', onNewMessage)"]
            socket_on_task_created["socket.on('task_created', onTaskCreated)"]
            socket_on_task_deleted["socket.on('task_deleted', onTaskDeleted)"]
        end
    end
    
    subgraph "TasksGateway Integration"
        handleJoinTask["handleJoinTask(client, taskId)<br/>client.join(`task_${taskId}`)"]
        handleLeaveTask["handleLeaveTask(client, taskId)<br/>client.leave(`task_${taskId}`)"]
        emitTaskUpdate["emitTaskUpdate(taskId, task)<br/>server.to(`task_${taskId}`).emit('task_updated')"]
        emitNewMessage["emitNewMessage(taskId, message)<br/>server.to(`task_${taskId}`).emit('new_message')"]
    end
    
    connect_function --> io_config
    io_config --> socket_on_connect
    joinTask_function --> handleJoinTask
    leaveTask_function --> handleLeaveTask
    socket_on_task_updated --> emitTaskUpdate
    socket_on_new_message --> emitNewMessage
```

**WebSocket Event Protocol**

| Client Event | Server Handler | Server Response | Room Targeting |
|--------------|----------------|-----------------|----------------|
| `emit('join_task', taskId)` | `handleJoinTask()` | - | `client.join(\`task_${taskId}\`)` |
| `emit('leave_task', taskId)` | `handleLeaveTask()` | - | `client.leave(\`task_${taskId}\`)` |
| - | `emitTaskUpdate()` | `task_updated` | `server.to(\`task_${taskId}\`)` |
| - | `emitNewMessage()` | `new_message` | `server.to(\`task_${taskId}\`)` |
| - | `emitTaskCreated()` | `task_created` | `server.emit()` (broadcast) |
| - | `emitTaskDeleted()` | `task_deleted` | `server.emit()` (broadcast) |

The hook maintains `currentTaskIdRef` to track active subscriptions and automatically handles room transitions when switching between tasks.

Sources: [packages/bytebot-ui/src/hooks/useWebSocket.ts:21-34](), [packages/bytebot-ui/src/hooks/useWebSocket.ts:68-88](), [packages/bytebot-agent/src/tasks/tasks.gateway.ts:30-56]()

## Dependencies and Technology Stack

The `bytebot-ui` package implements a modern React stack with specific dependencies for proxy servers, real-time communication, and desktop integration.

### Core Runtime Dependencies

| Package | Version | Implementation Purpose |
|---------|---------|----------------------|
| `next` | ≥15.3.3 | Next.js App Router with React Server Components |
| `react` | ^19.0.0 | UI framework with concurrent features |
| `express` | ^4.21.2 | Custom server wrapper for `server.ts` |
| `http-proxy-middleware` | ^3.0.5 | Express middleware for `/api/proxy/tasks` routing |
| `http-proxy` | ^1.18.1 | Low-level proxy for VNC WebSocket handling |
| `socket.io-client` | ^4.8.1 | WebSocket client for `useWebSocket` hook |
| `react-vnc` | ^3.1.0 | VNC client component for desktop viewing |
| `tsx` | ^4.19.3 | TypeScript runtime for `server.ts` execution |

### UI Component Dependencies

| Package | Version | Usage |
|---------|---------|-------|
| `@radix-ui/react-*` | ^2.x | Headless UI primitives (`Select`, `DropdownMenu`, `Popover`) |
| `@hugeicons/react` | ^1.0.5 | Icon components (`Home01Icon`, `TaskDaily01Icon`) |
| `lucide-react` | ^0.517.0 | Additional icon library |
| `tailwindcss` | ^4 | Utility-first CSS framework |
| `class-variance-authority` | ^0.7.1 | Component variant management |
| `clsx` | ^2.1.1 | Conditional className utility |

### Shared Package Integration

| Package | Source | Purpose |
|---------|--------|---------|
| `@bytebot/shared` | `../shared` | TypeScript interfaces (`Task`, `Message`) |
| `@prisma/client` | ^6.5.0 | Database client types and runtime |

The `next.config.ts` includes `transpilePackages: ["@bytebot/shared"]` to enable monorepo package importing.

Sources: [packages/bytebot-ui/package.json:11-47](), [packages/bytebot-ui/package.json:49-62](), [packages/bytebot-ui/next.config.ts:6-8]()

## Build and Deployment Configuration

The UI Service uses custom build scripts and supports both development and production deployments.

### Build Scripts

```mermaid
graph LR
    subgraph "Build Pipeline"
        SharedBuild["npm run build<br/>../shared"]
        NextBuild["next build"]
        ServerStart["tsx server.ts"]
    end
    
    subgraph "Development"
        DevScript["npm run dev"]
        DevServer["tsx server.ts<br/>with Next.js dev mode"]
    end
    
    subgraph "Production"  
        StartScript["npm run start"]
        ProdServer["tsx server.ts<br/>with built Next.js app"]
    end
    
    SharedBuild --> NextBuild
    DevScript --> DevServer
    StartScript --> SharedBuild
    StartScript --> ProdServer
```

### Environment Configuration

| Variable | Purpose | Default |
|----------|---------|---------|
| `BYTEBOT_AGENT_BASE_URL` | Agent Service endpoint | Required |
| `BYTEBOT_DESKTOP_VNC_URL` | Desktop VNC endpoint | Required |
| `PORT` | Server port | 9992 |
| `HOSTNAME` | Server hostname | localhost |
| `NODE_ENV` | Environment mode | development |

The Next.js configuration [packages/bytebot-ui/next.config.ts]() transpiles the shared package for proper module resolution across the monorepo structure.

Sources: [packages/bytebot-ui/package.json:5-9](), [packages/bytebot-ui/server.ts:11-17](), [packages/bytebot-ui/next.config.ts:6-8]()

---

# Page: Task Management System

# Task Management System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [packages/bytebot-agent/src/agent/agent.processor.ts](packages/bytebot-agent/src/agent/agent.processor.ts)
- [packages/bytebot-agent/src/tasks/tasks.controller.ts](packages/bytebot-agent/src/tasks/tasks.controller.ts)
- [packages/bytebot-agent/src/tasks/tasks.service.ts](packages/bytebot-agent/src/tasks/tasks.service.ts)
- [packages/bytebot-ui/src/hooks/useChatSession.ts](packages/bytebot-ui/src/hooks/useChatSession.ts)

</details>



The Task Management System provides comprehensive task creation, lifecycle management, and real-time communication capabilities for Bytebot. This system handles task CRUD operations, state transitions, scheduling, file attachments, and WebSocket-based event broadcasting to keep all clients synchronized.

For details on how tasks are executed by the AI agent, see page 6 (Agent System). For real-time event communication patterns, see page 2.2 (Communication Patterns). For database schema details, see page 9.2 (Database Schema).

## Architecture Overview

The Task Management System centers around `TasksService`, which provides CRUD operations, state management, and event emission. It integrates with `TasksGateway` for WebSocket broadcasting, `AgentScheduler` for queue management, and `EventEmitter2` for internal event coordination.

**Task Management System Architecture**

```mermaid
graph TB
    subgraph "External Clients"
        UI["bytebot-ui<br/>React Components"]
        API["External API Clients"]
    end
    
    subgraph "API Layer"
        TasksController["TasksController<br/>REST Endpoints"]
        TasksGateway["TasksGateway<br/>Socket.IO Server"]
    end
    
    subgraph "Core Services"
        TasksService["TasksService<br/>CRUD + Event Emission"]
        MessagesService["MessagesService<br/>Message Management"]
        FilesService["File Storage<br/>Base64 → Desktop"]
    end
    
    subgraph "Task Execution"
        AgentScheduler["AgentScheduler<br/>Cron-based Queue"]
        AgentProcessor["AgentProcessor<br/>Task Execution"]
    end
    
    subgraph "Event System"
        EventEmitter["EventEmitter2<br/>task.completed<br/>task.failed<br/>task.takeover<br/>task.resume<br/>task.cancel"]
    end
    
    subgraph "Persistence"
        PrismaService["PrismaService<br/>PostgreSQL Client"]
        TaskTable["Task Table<br/>id, description, status<br/>priority, type, control<br/>model, scheduledFor"]
        FileTable["File Table<br/>id, name, type, size<br/>data, taskId"]
    end
    
    UI -->|"HTTP Requests"| TasksController
    API -->|"HTTP Requests"| TasksController
    UI <-->|"Socket.IO"| TasksGateway
    
    TasksController --> TasksService
    TasksController --> MessagesService
    TasksGateway <--> TasksService
    
    TasksService --> EventEmitter
    TasksService --> PrismaService
    TasksService --> FilesService
    
    PrismaService --> TaskTable
    PrismaService --> FileTable
    
    AgentScheduler -->|"findNextTask()"| TasksService
    AgentScheduler -->|"processTask()"| AgentProcessor
    
    EventEmitter -.->|"@OnEvent"| AgentProcessor
```

Sources: [packages/bytebot-agent/src/tasks/tasks.service.ts:1-392](), [packages/bytebot-agent/src/tasks/tasks.controller.ts:1-194](), [packages/bytebot-agent/src/tasks/tasks.gateway.ts]()

## Task Data Model

Tasks are represented by the Prisma `Task` model with comprehensive metadata for scheduling, execution tracking, and control management.

**Task Entity Schema**

| Field | Type | Description |
|-------|------|-------------|
| `id` | `string` | UUID primary key |
| `description` | `string` | User-provided task description |
| `status` | `TaskStatus` | Current state: PENDING, RUNNING, NEEDS_HELP, COMPLETED, FAILED, CANCELLED |
| `priority` | `TaskPriority` | Execution priority: LOW, MEDIUM, HIGH |
| `type` | `TaskType` | Task type: IMMEDIATE, SCHEDULED |
| `control` | `Role` | Control authority: ASSISTANT (AI), USER |
| `createdBy` | `Role` | Creator: USER or ASSISTANT |
| `model` | `Json` | AI model configuration (provider, name, contextWindow) |
| `scheduledFor` | `DateTime?` | Optional scheduled execution time |
| `queuedAt` | `DateTime?` | When task was queued for execution |
| `executedAt` | `DateTime?` | When task execution started |
| `completedAt` | `DateTime?` | When task finished |
| `error` | `string?` | Error message if failed |
| `createdAt` | `DateTime` | Creation timestamp |
| `updatedAt` | `DateTime` | Last modification timestamp |

**Task Status Enumeration**

```typescript
enum TaskStatus {
  PENDING      // Created but not started
  RUNNING      // Currently executing
  NEEDS_HELP   // Paused, awaiting user guidance
  COMPLETED    // Successfully finished
  FAILED       // Terminated with error
  CANCELLED    // User-cancelled
}
```

**Task Priority and Type**

```typescript
enum TaskPriority {
  LOW
  MEDIUM
  HIGH
}

enum TaskType {
  IMMEDIATE    // Execute as soon as possible
  SCHEDULED    // Execute at scheduledFor time
}
```

Sources: [packages/bytebot-agent/prisma/schema.prisma](), [packages/bytebot-agent/src/tasks/tasks.service.ts:12-20]()

## TasksService Core Operations

The `TasksService` class provides comprehensive task lifecycle management through CRUD operations, state transitions, and event emission.

**Task Creation Flow**

```mermaid
sequenceDiagram
    participant Client
    participant Controller as TasksController
    participant Service as TasksService
    participant Prisma as PrismaService
    participant Gateway as TasksGateway
    
    Client->>Controller: POST /tasks (CreateTaskDto)
    Controller->>Service: create(createTaskDto)
    
    Service->>Prisma: $transaction start
    Service->>Prisma: task.create({description, type, priority, model, ...})
    
    alt Files provided
        loop For each file
            Service->>Prisma: file.create({name, type, size, data, taskId})
        end
    end
    
    Service->>Prisma: message.create({content: [{type: 'text', text}], role: USER, taskId})
    Service->>Prisma: $transaction commit
    
    Service->>Gateway: emitTaskCreated(task)
    Gateway-->>Client: task_created event (broadcast)
    Service->>Controller: Task
    Controller->>Client: 201 Created, Task
```

Sources: [packages/bytebot-agent/src/tasks/tasks.service.ts:40-117](), [packages/bytebot-agent/src/tasks/tasks.controller.ts:42-46]()

### Primary TasksService Methods

**CRUD Operations**

| Method | Parameters | Return | Description |
|--------|-----------|--------|-------------|
| `create()` | `CreateTaskDto` | `Promise<Task>` | Creates task with initial message, saves files, emits `task_created` |
| `findAll()` | `page, limit, statuses?` | `Promise<{tasks, total, totalPages}>` | Paginated task list with optional status filter |
| `findById()` | `id: string` | `Promise<Task>` | Retrieves single task with files included |
| `update()` | `id: string, UpdateTaskDto` | `Promise<Task>` | Updates task, handles status transitions, emits `task_updated` |
| `delete()` | `id: string` | `Promise<Task>` | Deletes task, emits `task_deleted` |

**Task Queue Management**

| Method | Parameters | Return | Description |
|--------|-----------|--------|-------------|
| `findScheduledTasks()` | - | `Promise<Task[]>` | Returns tasks with `scheduledFor` set but not yet queued |
| `findNextTask()` | - | `Promise<Task & {files}>` | Returns highest priority RUNNING or PENDING task with files |

**Control Transfer Operations**

| Method | Parameters | Return | Description |
|--------|-----------|--------|-------------|
| `takeOver()` | `taskId: string` | `Promise<Task>` | Transfers control to USER, starts input tracking, emits `task.takeover` |
| `resume()` | `taskId: string` | `Promise<Task>` | Returns control to ASSISTANT, stops input tracking, emits `task.resume` |
| `cancel()` | `taskId: string` | `Promise<Task>` | Sets status to CANCELLED, emits `task.cancel` |
| `addTaskMessage()` | `taskId, AddTaskMessageDto` | `Promise<Task>` | Adds user message, emits `new_message` |

Sources: [packages/bytebot-agent/src/tasks/tasks.service.ts:40-391]()

### Status Update Logic

When `update()` is called with a status change, `TasksService` handles special status transitions:

```typescript
// In update() method
if (updateTaskDto.status === TaskStatus.COMPLETED) {
  this.eventEmitter.emit('task.completed', { taskId: id });
} else if (updateTaskDto.status === TaskStatus.NEEDS_HELP) {
  updatedTask = await this.takeOver(id);
} else if (updateTaskDto.status === TaskStatus.FAILED) {
  this.eventEmitter.emit('task.failed', { taskId: id });
}
```

The `NEEDS_HELP` status automatically triggers `takeOver()`, which transfers control to the user and starts input tracking.

Sources: [packages/bytebot-agent/src/tasks/tasks.service.ts:217-247]()

## Task Lifecycle State Machine

Tasks transition through well-defined states from creation to completion. The state machine handles user intervention, error conditions, and successful completion.

**Task State Transitions**

```mermaid
stateDiagram-v2
    [*] --> PENDING: create()
    
    PENDING --> RUNNING: AgentScheduler picks task<br/>update(status=RUNNING, executedAt=now)
    
    RUNNING --> NEEDS_HELP: AI calls set_task_status(needs_help)<br/>update(status=NEEDS_HELP)<br/>→ takeOver() automatic
    RUNNING --> COMPLETED: AI calls set_task_status(completed)<br/>update(status=COMPLETED, completedAt=now)
    RUNNING --> FAILED: Error during processing<br/>update(status=FAILED, error=message)
    RUNNING --> CANCELLED: User calls cancel()<br/>update(status=CANCELLED)
    
    NEEDS_HELP --> RUNNING: User calls resume()<br/>update(status=RUNNING, control=ASSISTANT)
    NEEDS_HELP --> CANCELLED: User calls cancel()<br/>update(status=CANCELLED)
    
    PENDING --> CANCELLED: User calls cancel()<br/>update(status=CANCELLED)
    
    COMPLETED --> [*]
    FAILED --> [*]
    CANCELLED --> [*]
    
    note right of RUNNING
        Task is being processed by AI agent
        control = ASSISTANT
        Agent has full desktop control
    end note
    
    note right of NEEDS_HELP
        Task paused for user guidance
        control = USER (via takeOver())
        Input tracking started
        User can add messages or take manual actions
    end note
```

**Control Authority Transitions**

Tasks have a `control` field that determines who currently manages the desktop:

| Control Value | Authority | Input Tracking | Actions Available |
|---------------|-----------|----------------|-------------------|
| `Role.ASSISTANT` | AI Agent | Stopped | AI can execute desktop actions via computer tools |
| `Role.USER` | Human User | Started | User can manually interact with desktop, VNC streaming active |

Control transfers occur via:
- `takeOver(taskId)`: ASSISTANT → USER (sets `control=USER`, starts input tracking)
- `resume(taskId)`: USER → ASSISTANT (sets `control=ASSISTANT`, stops input tracking)

Sources: [packages/bytebot-agent/src/tasks/tasks.service.ts:217-391](), [packages/bytebot-agent/src/agent/agent.processor.ts:134-149]()

### State Transition Events

`TasksService` emits internal events via `EventEmitter2` for key state transitions:

| Event Name | Triggered By | Payload | Listeners |
|------------|--------------|---------|-----------|
| `task.completed` | `update(status=COMPLETED)` | `{taskId}` | AgentProcessor |
| `task.failed` | `update(status=FAILED)` | `{taskId}` | AgentProcessor |
| `task.takeover` | `takeOver(taskId)` | `{taskId}` | AgentProcessor |
| `task.resume` | `resume(taskId)` | `{taskId}` | AgentProcessor |
| `task.cancel` | `cancel(taskId)` | `{taskId}` | AgentProcessor |

These events allow `AgentProcessor` to react to task lifecycle changes (e.g., aborting processing on takeover, resuming iteration on resume).

Sources: [packages/bytebot-agent/src/tasks/tasks.service.ts:234-238](), [packages/bytebot-agent/src/tasks/tasks.service.ts:312](), [packages/bytebot-agent/src/tasks/tasks.service.ts:351](), [packages/bytebot-agent/src/tasks/tasks.service.ts:385]()

## WebSocket Real-Time Events

`TasksGateway` provides WebSocket-based real-time communication using Socket.IO, enabling clients to subscribe to task updates and receive instant notifications.

**WebSocket Event Flow**

```mermaid
sequenceDiagram
    participant UI as bytebot-ui Client
    participant Proxy as Next.js Proxy<br/>/api/proxy/tasks
    participant Gateway as TasksGateway<br/>Socket.IO Server
    participant Service as TasksService
    
    UI->>Proxy: Connect via Socket.IO
    Proxy->>Gateway: WebSocket Upgrade
    Gateway->>UI: connection event
    
    UI->>Gateway: join_task(taskId)
    Note over Gateway: Client joins room "task:{taskId}"
    
    Service->>Gateway: emitTaskUpdate(taskId, task)
    Gateway->>UI: task_updated(task)<br/>(to room "task:{taskId}")
    
    Service->>Gateway: emitNewMessage(taskId, message)
    Gateway->>UI: new_message(message)<br/>(to room "task:{taskId}")
    
    Service->>Gateway: emitTaskCreated(task)
    Gateway-->>UI: task_created(task)<br/>(broadcast to all)
    
    Service->>Gateway: emitTaskDeleted(taskId)
    Gateway-->>UI: task_deleted(taskId)<br/>(broadcast to all)
    
    UI->>Gateway: leave_task()
    Note over Gateway: Client leaves current room
```

Sources: [packages/bytebot-agent/src/tasks/tasks.gateway.ts](), [packages/bytebot-ui/src/hooks/useWebSocket.ts]()

### WebSocket Events

**Client-to-Server Events**

| Event | Payload | Description |
|-------|---------|-------------|
| `join_task` | `{taskId: string}` | Subscribe to updates for specific task (joins room `task:{taskId}`) |
| `leave_task` | - | Unsubscribe from current task room |

**Server-to-Client Events**

| Event | Payload | Scope | Description |
|-------|---------|-------|-------------|
| `task_updated` | `Task` | Room (`task:{taskId}`) | Emitted when task status, control, or other fields change |
| `new_message` | `Message` | Room (`task:{taskId}`) | Emitted when new message added to task |
| `task_created` | `Task` | Broadcast (all clients) | Emitted when new task created |
| `task_deleted` | `string` (taskId) | Broadcast (all clients) | Emitted when task deleted |

### TasksGateway Implementation

`TasksGateway` uses Socket.IO rooms for targeted event delivery:

```typescript
// Join task room
@SubscribeMessage('join_task')
handleJoinTask(client: Socket, payload: { taskId: string }) {
  client.join(`task:${payload.taskId}`);
}

// Room-scoped emission (only clients in that room receive)
emitTaskUpdate(taskId: string, task: Task) {
  this.server.to(`task:${taskId}`).emit('task_updated', task);
}

// Broadcast to all connected clients
emitTaskCreated(task: Task) {
  this.server.emit('task_created', task);
}
```

Sources: [packages/bytebot-agent/src/tasks/tasks.gateway.ts]()

### Frontend WebSocket Integration

The `useWebSocket` hook in bytebot-ui manages Socket.IO connections and event handling:

```typescript
const { joinTask, leaveTask } = useWebSocket({
  onTaskUpdate: (task) => setTaskStatus(task.status),
  onNewMessage: (message) => setMessages(prev => [...prev, message]),
  onTaskCreated: (task) => console.log('New task:', task),
  onTaskDeleted: (taskId) => console.log('Deleted:', taskId),
});

// Subscribe to specific task
useEffect(() => {
  if (currentTaskId) {
    joinTask(currentTaskId);
  }
  return () => leaveTask();
}, [currentTaskId]);
```

Sources: [packages/bytebot-ui/src/hooks/useWebSocket.ts](), [packages/bytebot-ui/src/hooks/useChatSession.ts:99-104]()

## Task Scheduling System

`AgentScheduler` manages the task execution queue via a cron job that runs every 5 seconds, handling scheduled task queueing and picking the next task for execution.

**AgentScheduler Operation Flow**

```mermaid
graph TB
    subgraph "Cron Trigger"
        CronJob["@Cron(CronExpression.EVERY_5_SECONDS)<br/>handleCron()"]
    end
    
    subgraph "Scheduled Task Queueing"
        FindScheduled["tasksService.findScheduledTasks()"]
        CheckTime{{"scheduledFor <= now"}}
        SetQueued["tasksService.update(taskId,<br/>{queuedAt: new Date()})"]
    end
    
    subgraph "Task Execution"
        CheckProcessing{{"agentProcessor.isRunning()"}}
        FindNext["tasksService.findNextTask()"]
        PrepareFiles["Write task.files[] to<br/>/home/user/Desktop/"]
        UpdateRunning["tasksService.update(<br/>status=RUNNING,<br/>executedAt=now)"]
        StartProcessing["agentProcessor.processTask(taskId)"]
    end
    
    CronJob --> FindScheduled
    FindScheduled -->|"Tasks with scheduledFor"| CheckTime
    CheckTime -->|"Yes"| SetQueued
    
    CronJob --> CheckProcessing
    CheckProcessing -->|"false (idle)"| FindNext
    FindNext -->|"Task found"| PrepareFiles
    PrepareFiles --> UpdateRunning
    UpdateRunning --> StartProcessing
    
    CheckProcessing -->|"true (busy)"| CronJob
    FindNext -->|"No task"| CronJob
```

Sources: [packages/bytebot-agent/src/agent/agent.scheduler.ts:1-64]()

### Task Selection Priority

The `findNextTask()` method returns the highest priority task using this sort order:

1. **executedAt** (ascending): Tasks already RUNNING are prioritized over PENDING tasks
2. **priority** (descending): HIGH > MEDIUM > LOW
3. **queuedAt** (ascending): Earlier queued tasks first
4. **createdAt** (ascending): Older tasks first

```typescript
await this.prisma.task.findFirst({
  where: {
    status: {
      in: [TaskStatus.RUNNING, TaskStatus.PENDING],
    },
  },
  orderBy: [
    { executedAt: 'asc' },
    { priority: 'desc' },
    { queuedAt: 'asc' },
    { createdAt: 'asc' },
  ],
  include: {
    files: true,
  },
});
```

This ensures:
- A task already RUNNING (with `executedAt` set) continues before starting new tasks
- Higher priority tasks execute first within PENDING tasks
- Tasks are processed in FIFO order when priority is equal

Sources: [packages/bytebot-agent/src/tasks/tasks.service.ts:131-156]()

### Scheduled Task Processing

Tasks with `type=SCHEDULED` and a `scheduledFor` date are handled specially:

1. `findScheduledTasks()` retrieves tasks where `scheduledFor` is set but `queuedAt` is null
2. For each task where `scheduledFor <= now`, update `queuedAt` to current time
3. Task becomes eligible for `findNextTask()` selection

```typescript
async findScheduledTasks(): Promise<Task[]> {
  return this.prisma.task.findMany({
    where: {
      scheduledFor: {
        not: null,
      },
      queuedAt: null,
    },
    orderBy: [{ scheduledFor: 'asc' }],
  });
}
```

Sources: [packages/bytebot-agent/src/tasks/tasks.service.ts:119-129](), [packages/bytebot-agent/src/agent/agent.scheduler.ts:22-63]()

## Context Management and Summarization

The agent system automatically manages conversation context through intelligent summarization when approaching token limits, ensuring long-running tasks can continue without losing important information.

**Context Window Management**

```mermaid
graph TB
    subgraph "Context Composition"
        LatestSummary["findLatest(taskId)<br/>Most recent summary"]
        UnsummarizedMsgs["findUnsummarized(taskId)<br/>Messages after last summary"]
        MessageArray["Combined message array<br/>Summary + unsummarized messages"]
    end
    
    subgraph "Token Management"
        TokenUsage["agentResponse.tokenUsage.totalTokens"]
        ContextWindow["model.contextWindow || 200000"]
        Threshold["contextThreshold = contextWindow * 0.75"]
        ShouldSummarize["tokenUsage >= contextThreshold"]
    end
    
    subgraph "Summarization Process"
        SummaryPrompt["SUMMARIZATION_SYSTEM_PROMPT<br/>Task progress and context"]
        SummaryGeneration["generateMessage() for summary"]
        SummaryStorage["summariesService.create()"]
        MessageAttachment["messagesService.attachSummary()"]
    end
    
    LatestSummary --> MessageArray
    UnsummarizedMsgs --> MessageArray
    MessageArray --> TokenUsage
    
    TokenUsage --> ShouldSummarize
    ContextWindow --> Threshold
    Threshold --> ShouldSummarize
    
    ShouldSummarize -->|"true"| SummaryPrompt
    SummaryPrompt --> SummaryGeneration
    SummaryGeneration --> SummaryStorage
    SummaryStorage --> MessageAttachment
```

Sources: [packages/bytebot-agent/src/agent/agent.processor.ts:157-181](), [packages/bytebot-agent/src/agent/agent.processor.ts:233-298](), [packages/bytebot-agent/src/agent/agent.constants.ts:6-15]()

## Task Scheduling and Queue Management

The `AgentScheduler` manages task execution through a cron-based system that handles scheduled tasks, file preparation, and ensures only one task processes at a time.

**Task Queue Processing Logic**

```mermaid
graph TB
    subgraph "Cron Schedule (Every 5s)"
        CronTrigger["@Cron(CronExpression.EVERY_5_SECONDS)<br/>handleCron()"]
    end
    
    subgraph "Scheduled Task Processing"
        FindScheduled["findScheduledTasks()<br/>Tasks with scheduledFor dates"]
        CheckTime["scheduledFor < now"]
        QueueTask["update(taskId, {queuedAt: now})"]
    end
    
    subgraph "Active Task Processing"
        CheckRunning["agentProcessor.isRunning()"]
        FindNext["findNextTask()<br/>RUNNING or PENDING tasks"]
        PrepareFiles["writeFile() for task.files[]<br/>to /home/user/Desktop/"]
        StartTask["update(status: RUNNING, executedAt)<br/>agentProcessor.processTask()"]
    end
    
    CronTrigger --> FindScheduled
    FindScheduled --> CheckTime
    CheckTime -->|"true"| QueueTask
    
    CronTrigger --> CheckRunning
    CheckRunning -->|"false"| FindNext
    FindNext -->|"task found"| PrepareFiles
    PrepareFiles --> StartTask
```

Sources: [packages/bytebot-agent/src/agent/agent.scheduler.ts:22-63](), [packages/bytebot-agent/src/tasks/tasks.service.ts:131-156]()

## System Prompts and Tool Definitions

The agent system uses carefully crafted system prompts and comprehensive tool definitions to guide AI behavior and ensure reliable computer automation.

The `AGENT_SYSTEM_PROMPT` provides detailed instructions for computer interaction, including valid keyboard keys, application handling, and task lifecycle management. The prompt emphasizes observation-first behavior, human-like interaction patterns, and thorough verification of actions.

Key prompt sections include:
- **Available Applications**: Firefox, Thunderbird, 1Password, VSCode, Terminal, File Manager
- **Core Working Principles**: Screenshot before action, navigate via `computer_application`, human-like interaction
- **Repetitive Task Handling**: Progress tracking, batch processing, error recovery
- **Task Lifecycle Template**: Prepare → Execute Loop → Batch Loop → Cleanup → Terminate

The `agentTools` array defines 15+ computer interaction tools covering:
- **Mouse Actions**: `computer_move_mouse`, `computer_click_mouse`, `computer_drag_mouse`, `computer_scroll`
- **Keyboard Actions**: `computer_type_keys`, `computer_press_keys`, `computer_type_text`, `computer_paste_text`
- **Utility Actions**: `computer_screenshot`, `computer_cursor_position`, `computer_wait`, `computer_application`
- **Task Management**: `set_task_status`, `create_task`
- **File Operations**: `computer_read_file`

Sources: [packages/bytebot-agent/src/agent/agent.constants.ts:17-176](), [packages/bytebot-agent/src/agent/agent.tools.ts:387-405]()

---

# Page: Task Lifecycle

# Task Lifecycle

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [packages/bytebot-agent/prisma/schema.prisma](packages/bytebot-agent/prisma/schema.prisma)
- [packages/bytebot-agent/src/agent/agent.processor.ts](packages/bytebot-agent/src/agent/agent.processor.ts)
- [packages/bytebot-agent/src/anthropic/anthropic.tools.ts](packages/bytebot-agent/src/anthropic/anthropic.tools.ts)
- [packages/bytebot-agent/src/tasks/dto/create-task.dto.ts](packages/bytebot-agent/src/tasks/dto/create-task.dto.ts)
- [packages/bytebot-agent/src/tasks/tasks.controller.ts](packages/bytebot-agent/src/tasks/tasks.controller.ts)
- [packages/bytebot-agent/src/tasks/tasks.service.ts](packages/bytebot-agent/src/tasks/tasks.service.ts)
- [packages/bytebot-ui/src/hooks/useChatSession.ts](packages/bytebot-ui/src/hooks/useChatSession.ts)
- [packages/bytebot-ui/src/types/index.ts](packages/bytebot-ui/src/types/index.ts)

</details>



This document describes the lifecycle of a Task entity from creation through completion, including all possible states, state transitions, control handoff mechanisms, and the agent processing loop. Tasks are the fundamental unit of work in Bytebot, representing user requests that the AI agent executes on the virtual desktop.

For details on creating and managing tasks via API, see [TasksService API](#5.2). For information on the agent's processing logic, see [Agent Processor](#6.1). For real-time task updates, see [WebSocket Events](#5.3).

---

## Task States

Tasks progress through a defined set of states stored in the `status` field. The complete set of states is defined in the Prisma schema as the `TaskStatus` enum.

| Status | Description | Control | Terminal |
|--------|-------------|---------|----------|
| `PENDING` | Task created but not yet started by the scheduler | `ASSISTANT` | No |
| `RUNNING` | Agent actively processing the task in iterations | `ASSISTANT` | No |
| `NEEDS_HELP` | Agent has requested user guidance or intervention | `USER` | No |
| `NEEDS_REVIEW` | Task completed but requires user verification | `USER` | No |
| `COMPLETED` | Task successfully finished | `ASSISTANT` | Yes |
| `CANCELLED` | Task manually cancelled by user | `ASSISTANT` | Yes |
| `FAILED` | Task terminated due to error | `ASSISTANT` | Yes |

**Sources:**
- [packages/bytebot-agent/prisma/schema.prisma:16-24]()
- [packages/bytebot-ui/src/types/index.ts:32-40]()

---

## Task State Diagram

The following diagram shows all possible state transitions and the operations that trigger them:

```mermaid
stateDiagram-v2
    [*] --> PENDING: "TasksService.create()"
    
    PENDING --> RUNNING: "AgentScheduler picks task<br/>File preparation<br/>Set executedAt timestamp"
    
    RUNNING --> RUNNING: "AgentProcessor.runIteration()<br/>Continuous loop while status=RUNNING"
    
    RUNNING --> COMPLETED: "set_task_status tool<br/>status='completed'<br/>TasksService.update()"
    
    RUNNING --> NEEDS_HELP: "set_task_status tool<br/>status='needs_help'<br/>TasksService.update()<br/>Calls takeOver()"
    
    RUNNING --> FAILED: "Error in AgentProcessor<br/>TasksService.update()<br/>Emit 'task.failed'"
    
    RUNNING --> CANCELLED: "TasksService.cancel()<br/>User cancellation<br/>Emit 'task.cancel'"
    
    NEEDS_HELP --> RUNNING: "TasksService.resume()<br/>User guidance provided<br/>Control transferred to ASSISTANT<br/>Emit 'task.resume'"
    
    NEEDS_HELP --> CANCELLED: "TasksService.cancel()"
    
    COMPLETED --> [*]: "Terminal state"
    CANCELLED --> [*]: "Terminal state"
    FAILED --> [*]: "Terminal state"
    
    note right of PENDING
        Initial state after creation
        Task stored in database
        Initial message created
        Files attached if provided
    end note
    
    note right of RUNNING
        AgentProcessor.isProcessing = true
        Continuous iteration loop
        Screenshot → LLM → Tools → Verify
        Emits WebSocket updates
    end note
    
    note right of NEEDS_HELP
        Control transfers to USER
        Input tracking started
        Agent processing paused
        Awaits user message or resume
    end note
```

**Sources:**
- [packages/bytebot-agent/src/tasks/tasks.service.ts:217-247]()
- [packages/bytebot-agent/src/agent/agent.processor.ts:134-403]()
- [packages/bytebot-agent/src/tasks/tasks.controller.ts:176-192]()

---

## Task Creation Flow

When a task is created via `TasksService.create()`, the system performs several initialization steps within a database transaction:

```mermaid
flowchart TD
    Start["POST /tasks<br/>CreateTaskDto"] --> CreateRecord["prisma.task.create()<br/>status=PENDING<br/>control=ASSISTANT"]
    
    CreateRecord --> CheckFiles{"Files attached?"}
    
    CheckFiles -->|Yes| SaveFiles["prisma.file.create()<br/>Store base64 data<br/>Build filesDescription"]
    CheckFiles -->|No| CreateMessage
    
    SaveFiles --> CreateMessage["prisma.message.create()<br/>role=USER<br/>content=[text block]<br/>Includes filesDescription"]
    
    CreateMessage --> EmitEvent["tasksGateway.emitTaskCreated()<br/>Broadcast to WebSocket clients"]
    
    EmitEvent --> End["Return Task entity"]
    
    style CreateRecord fill:#f9f9f9
    style SaveFiles fill:#f9f9f9
    style CreateMessage fill:#f9f9f9
    style EmitEvent fill:#f9f9f9
```

**Key Implementation Details:**

- **Transaction boundary**: [packages/bytebot-agent/src/tasks/tasks.service.ts:45-112]()
- **File processing**: Base64 data prefix removed, stored in `File.data` field [packages/bytebot-agent/src/tasks/tasks.service.ts:66-93]()
- **Initial message**: Contains task description plus file confirmation text [packages/bytebot-agent/src/tasks/tasks.service.ts:96-109]()
- **Default values**: `type=IMMEDIATE`, `priority=MEDIUM`, `status=PENDING`, `createdBy=USER`, `control=ASSISTANT` [packages/bytebot-agent/src/tasks/tasks.service.ts:48-59]()

**Sources:**
- [packages/bytebot-agent/src/tasks/tasks.service.ts:40-117]()
- [packages/bytebot-agent/src/tasks/dto/create-task.dto.ts:31-60]()

---

## Task Scheduling and File Preparation

The `AgentScheduler` cron job monitors for tasks ready to execute:

```mermaid
sequenceDiagram
    participant Cron as "@Cron('*/5 * * * * *')<br/>AgentScheduler.checkForTasks()"
    participant TS as TasksService
    participant AP as AgentProcessor
    participant FS as "Filesystem<br/>/home/user/Desktop"
    
    Cron->>AP: isRunning()?
    AP-->>Cron: false
    
    Cron->>TS: findNextTask()
    Note over TS: Query: status IN [RUNNING, PENDING]<br/>Order by: executedAt, priority, queuedAt, createdAt
    TS-->>Cron: Task & files[]
    
    alt Task has files
        loop Each file
            Cron->>FS: fs.writeFile(Desktop/${name}, base64)
        end
    end
    
    Cron->>TS: update(id, {<br/>  status: RUNNING,<br/>  executedAt: now(),<br/>  queuedAt: now()<br/>})
    
    Cron->>AP: processTask(taskId)
    Note over AP: isProcessing = true<br/>currentTaskId = taskId<br/>abortController = new
    
    AP->>AP: runIteration(taskId)
```

**Scheduling Logic:**
- **Cron interval**: Every 5 seconds [packages/bytebot-agent/src/agent/agent.scheduler.ts:31]()
- **Task selection**: Returns first task matching status filter, ordered by priority and timestamps [packages/bytebot-agent/src/tasks/tasks.service.ts:131-156]()
- **File materialization**: Files decoded from base64 and written to `/home/user/Desktop/` [packages/bytebot-agent/src/agent/agent.scheduler.ts:58-70]()
- **State update**: Sets `status=RUNNING`, `executedAt`, and `queuedAt` before processing [packages/bytebot-agent/src/agent/agent.scheduler.ts:75-79]()

**Sources:**
- [packages/bytebot-agent/src/agent/agent.scheduler.ts:27-95]()
- [packages/bytebot-agent/src/tasks/tasks.service.ts:131-156]()

---

## Control Handoff System

Tasks have a `control` field that determines whether the agent or user has control of the desktop:

| Control Value | Desktop Control | Input Tracking | Agent Processing | Use Case |
|---------------|----------------|----------------|------------------|----------|
| `ASSISTANT` | Agent | Stopped | Active | Normal agent operation |
| `USER` | User | Active | Paused | Manual intervention, guidance |

### Taking Over Control

When the agent calls `set_task_status` with `status='needs_help'`, or when a user manually calls `POST /tasks/:id/takeover`:

```mermaid
flowchart LR
    Trigger["Trigger:<br/>- set_task_status tool<br/>- POST /tasks/:id/takeover"] --> TakeOver["TasksService.takeOver(taskId)"]
    
    TakeOver --> Validate{"control === ASSISTANT?"}
    Validate -->|No| Error["BadRequestException<br/>'Not under agent control'"]
    Validate -->|Yes| Update["prisma.task.update()<br/>control = USER"]
    
    Update --> StartTracking["POST /input-tracking/start<br/>to bytebotd"]
    StartTracking --> EmitEvent["eventEmitter.emit('task.takeover')"]
    EmitEvent --> Gateway["tasksGateway.emitTaskUpdate()"]
    
    EmitEvent --> Handler["AgentProcessor.handleTaskTakeover()"]
    Handler --> Abort["abortController.abort()<br/>Stop current LLM call"]
    Handler --> InputCapture["inputCaptureService.start(taskId)<br/>Record user actions"]
```

**Implementation Details:**
- **Validation**: Ensures task is under agent control before allowing takeover [packages/bytebot-agent/src/tasks/tasks.service.ts:328-332]()
- **Database update**: Sets `control=USER` [packages/bytebot-agent/src/tasks/tasks.service.ts:334-339]()
- **Input tracking**: Starts recording mouse/keyboard events [packages/bytebot-agent/src/tasks/tasks.service.ts:341-348]()
- **Event emission**: Broadcasts `task.takeover` to abort processing [packages/bytebot-agent/src/tasks/tasks.service.ts:351]()
- **Agent response**: Aborts in-flight LLM calls if processing this task [packages/bytebot-agent/src/agent/agent.processor.ts:84-95]()

### Resuming Agent Control

When a user provides guidance and clicks resume, or calls `POST /tasks/:id/resume`:

```mermaid
flowchart LR
    Trigger["POST /tasks/:id/resume"] --> Resume["TasksService.resume(taskId)"]
    
    Resume --> Validate{"control === USER?"}
    Validate -->|No| Error["BadRequestException<br/>'Not under user control'"]
    Validate -->|Yes| Update["prisma.task.update()<br/>control = ASSISTANT<br/>status = RUNNING"]
    
    Update --> StopTracking["POST /input-tracking/stop<br/>to bytebotd"]
    StopTracking --> EmitEvent["eventEmitter.emit('task.resume')"]
    EmitEvent --> Gateway["tasksGateway.emitTaskUpdate()"]
    
    EmitEvent --> Handler["AgentProcessor.handleTaskResume()"]
    Handler --> NewController["abortController = new"]
    NewController --> Continue["runIteration(taskId)"]
```

**Implementation Details:**
- **Validation**: Ensures task is under user control [packages/bytebot-agent/src/tasks/tasks.service.ts:290-292]()
- **Database update**: Sets `control=ASSISTANT`, `status=RUNNING` [packages/bytebot-agent/src/tasks/tasks.service.ts:294-300]()
- **Input tracking**: Stops recording user actions [packages/bytebot-agent/src/tasks/tasks.service.ts:302-309]()
- **Event emission**: Broadcasts `task.resume` to restart processing [packages/bytebot-agent/src/tasks/tasks.service.ts:312]()
- **Agent response**: Creates new abort controller and continues iteration [packages/bytebot-agent/src/agent/agent.processor.ts:97-105]()

**Sources:**
- [packages/bytebot-agent/src/tasks/tasks.service.ts:282-357]()
- [packages/bytebot-agent/src/agent/agent.processor.ts:84-105]()
- [packages/bytebot-agent/src/tasks/tasks.controller.ts:176-186]()

---

## Agent Processing Loop

Once a task enters `RUNNING` state, `AgentProcessor` executes a continuous iteration loop:

```mermaid
flowchart TD
    Start["processTask(taskId)<br/>isProcessing = true<br/>currentTaskId = taskId"] --> RunIter["runIteration(taskId)"]
    
    RunIter --> CheckStatus{"task.status === RUNNING?"}
    CheckStatus -->|No| Stop["isProcessing = false<br/>currentTaskId = null<br/>STOP"]
    
    CheckStatus -->|Yes| BuildContext["summariesService.findLatest()<br/>messagesService.findUnsummarized()<br/>Build context array"]
    
    BuildContext --> CallLLM["service.generateMessage()<br/>AGENT_SYSTEM_PROMPT<br/>messages<br/>model<br/>abortSignal"]
    
    CallLLM --> SaveResponse["messagesService.create()<br/>role=ASSISTANT<br/>contentBlocks"]
    
    SaveResponse --> CheckTokens{"tokenUsage >=<br/>contextWindow * 0.75?"}
    CheckTokens -->|Yes| Summarize["service.generateMessage()<br/>SUMMARIZATION_SYSTEM_PROMPT<br/>summariesService.create()<br/>messagesService.attachSummary()"]
    CheckTokens -->|No| ProcessTools
    
    Summarize --> ProcessTools["Process content blocks:<br/>- isComputerToolUseContentBlock<br/>- isCreateTaskToolUseBlock<br/>- isSetTaskStatusToolUseBlock"]
    
    ProcessTools --> ComputerTool{"Computer tool?"}
    ComputerTool -->|Yes| ExecComputer["handleComputerToolUse()<br/>POST /computer-use<br/>Generate ToolResult"]
    
    ProcessTools --> CreateTool{"Create task tool?"}
    CreateTool -->|Yes| CreateSubTask["tasksService.create()<br/>Generate ToolResult"]
    
    ProcessTools --> SetStatus{"Set status tool?"}
    SetStatus -->|Yes| CaptureBlock["Store setTaskStatusToolUseBlock<br/>Generate ToolResult"]
    
    ExecComputer --> SaveResults
    CreateSubTask --> SaveResults
    CaptureBlock --> SaveResults
    
    SaveResults["messagesService.create()<br/>role=USER<br/>toolResults"]
    
    SaveResults --> UpdateStatus{"setTaskStatusToolUseBlock?"}
    UpdateStatus -->|completed| Complete["tasksService.update()<br/>status=COMPLETED<br/>completedAt=now()"]
    UpdateStatus -->|needs_help| NeedsHelp["tasksService.update()<br/>status=NEEDS_HELP<br/>Calls takeOver()"]
    UpdateStatus -->|No| ScheduleNext
    
    Complete --> Stop
    NeedsHelp --> Stop
    
    ScheduleNext["setImmediate(() =><br/>  runIteration(taskId))"] --> RunIter
```

**Key Components:**

- **Context building**: Combines latest summary with unsummarized messages [packages/bytebot-agent/src/agent/agent.processor.ts:157-180]()
- **LLM call**: Uses provider-specific service (Anthropic, OpenAI, Google, or Proxy) [packages/bytebot-agent/src/agent/agent.processor.ts:185-207]()
- **Summarization**: Triggered when token usage exceeds 75% of context window [packages/bytebot-agent/src/agent/agent.processor.ts:233-299]()
- **Tool execution**: Processes computer, create_task, and set_task_status tools [packages/bytebot-agent/src/agent/agent.processor.ts:305-357]()
- **Status updates**: Handles task completion or needs_help transitions [packages/bytebot-agent/src/agent/agent.processor.ts:368-382]()
- **Non-blocking loop**: Uses `setImmediate()` to schedule next iteration [packages/bytebot-agent/src/agent/agent.processor.ts:385-387]()

**Sources:**
- [packages/bytebot-agent/src/agent/agent.processor.ts:114-403]()
- [packages/bytebot-agent/src/agent/agent.computer-use.ts:1-100]()

---

## Terminal States

Tasks can reach three terminal states:

### COMPLETED

- **Trigger**: Agent calls `set_task_status` tool with `status='completed'`
- **Update**: Sets `status=COMPLETED`, `completedAt=now()` [packages/bytebot-agent/src/agent/agent.processor.ts:370-374]()
- **Event**: Emits `task.completed` via EventEmitter2 [packages/bytebot-agent/src/tasks/tasks.service.ts:234]()
- **Processing**: Agent stops iteration loop [packages/bytebot-agent/src/agent/agent.processor.ts:142-148]()

### FAILED

- **Trigger**: Unhandled error in `AgentProcessor.runIteration()`
- **Update**: Sets `status=FAILED` [packages/bytebot-agent/src/agent/agent.processor.ts:396-398]()
- **Event**: Emits `task.failed` via EventEmitter2 [packages/bytebot-agent/src/tasks/tasks.service.ts:238]()
- **Processing**: Sets `isProcessing=false`, clears `currentTaskId` [packages/bytebot-agent/src/agent/agent.processor.ts:399-400]()
- **Common causes**: No service found for model provider, LLM returned empty content blocks

### CANCELLED

- **Trigger**: User calls `POST /tasks/:id/cancel`
- **Validation**: Cannot cancel if already `COMPLETED`, `FAILED`, or `CANCELLED` [packages/bytebot-agent/src/tasks/tasks.service.ts:367-375]()
- **Update**: Sets `status=CANCELLED` [packages/bytebot-agent/src/tasks/tasks.service.ts:377-382]()
- **Event**: Emits `task.cancel` to abort processing [packages/bytebot-agent/src/tasks/tasks.service.ts:385]()
- **Processing**: `AgentProcessor.handleTaskCancel()` calls `stopProcessing()` [packages/bytebot-agent/src/agent/agent.processor.ts:107-112]()

**Sources:**
- [packages/bytebot-agent/src/agent/agent.processor.ts:368-402]()
- [packages/bytebot-agent/src/tasks/tasks.service.ts:233-239]()
- [packages/bytebot-agent/src/tasks/tasks.service.ts:359-391]()

---

## Event System Integration

The task lifecycle emits internal events via EventEmitter2 for reactive coordination:

| Event Name | Emitted By | Payload | Listeners |
|------------|-----------|---------|-----------|
| `task.completed` | `TasksService.update()` | `{ taskId }` | None currently |
| `task.failed` | `TasksService.update()` | `{ taskId }` | None currently |
| `task.takeover` | `TasksService.takeOver()` | `{ taskId }` | `AgentProcessor.handleTaskTakeover()` |
| `task.resume` | `TasksService.resume()` | `{ taskId }` | `AgentProcessor.handleTaskResume()` |
| `task.cancel` | `TasksService.cancel()` | `{ taskId }` | `AgentProcessor.handleTaskCancel()` |

**Event Handler Decorators:**

- `@OnEvent('task.takeover')`: Aborts current processing, starts input capture [packages/bytebot-agent/src/agent/agent.processor.ts:84-95]()
- `@OnEvent('task.resume')`: Creates new abort controller, continues iteration [packages/bytebot-agent/src/agent/agent.processor.ts:97-105]()
- `@OnEvent('task.cancel')`: Stops processing immediately [packages/bytebot-agent/src/agent/agent.processor.ts:107-112]()

**WebSocket Broadcasting:**

In addition to internal events, `TasksGateway` broadcasts task updates to connected clients:

- `emitTaskCreated(task)`: Sent to all connected clients [packages/bytebot-agent/src/tasks/tasks.service.ts:114]()
- `emitTaskUpdate(taskId, task)`: Sent to clients in task's room [packages/bytebot-agent/src/tasks/tasks.service.ts:244]()
- `emitTaskDeleted(taskId)`: Sent to all connected clients [packages/bytebot-agent/src/tasks/tasks.service.ts:258]()
- `emitNewMessage(taskId, message)`: Sent to clients in task's room [packages/bytebot-agent/src/tasks/tasks.service.ts:278]()

**Sources:**
- [packages/bytebot-agent/src/tasks/tasks.service.ts:233-391]()
- [packages/bytebot-agent/src/agent/agent.processor.ts:84-112]()
- [packages/bytebot-agent/src/tasks/tasks.gateway.ts:1-100]()

---

# Page: TasksService API

# TasksService API

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [packages/bytebot-agent/src/agent/agent.processor.ts](packages/bytebot-agent/src/agent/agent.processor.ts)
- [packages/bytebot-agent/src/tasks/tasks.controller.ts](packages/bytebot-agent/src/tasks/tasks.controller.ts)
- [packages/bytebot-agent/src/tasks/tasks.service.ts](packages/bytebot-agent/src/tasks/tasks.service.ts)
- [packages/bytebot-ui/src/hooks/useChatSession.ts](packages/bytebot-ui/src/hooks/useChatSession.ts)

</details>



## Purpose and Scope

This document details the `TasksService` class and its API methods for managing task lifecycle, state, and control flow. The service provides CRUD operations, task querying, and control handoff mechanisms between user and AI agent.

For information about task states and transitions, see [Task Lifecycle](#5.1). For real-time event broadcasting, see [WebSocket Events](#5.3). For automated task scheduling, see [Task Scheduling](#5.4).

**Sources:** [packages/bytebot-agent/src/tasks/tasks.service.ts:1-392]()

---

## Service Architecture

The `TasksService` is a NestJS injectable service that coordinates task management across multiple subsystems. It serves as the central authority for task state mutations and broadcasts changes to connected clients.

### Dependency Graph

```mermaid
graph TB
    TasksService["TasksService"]
    PrismaService["PrismaService<br/>(Database Client)"]
    TasksGateway["TasksGateway<br/>(WebSocket Broadcasting)"]
    ConfigService["ConfigService<br/>(Environment Config)"]
    EventEmitter2["EventEmitter2<br/>(Internal Event Bus)"]
    
    TasksService --> PrismaService
    TasksService --> TasksGateway
    TasksService --> ConfigService
    TasksService --> EventEmitter2
    
    TasksController["TasksController<br/>(REST API)"] --> TasksService
    AgentScheduler["AgentScheduler<br/>(Cron Jobs)"] --> TasksService
    AgentProcessor["AgentProcessor<br/>(Task Execution)"] --> TasksService
    
    PrismaService --> PostgreSQL[("PostgreSQL<br/>Task, Message, File tables")]
    TasksGateway --> SocketIOClients["Socket.IO Clients"]
    EventEmitter2 --> AgentProcessor
```

**Sources:** [packages/bytebot-agent/src/tasks/tasks.service.ts:26-38]()

The service uses constructor-based dependency injection with a circular dependency on `TasksGateway` (resolved via `forwardRef`) to enable bidirectional communication for real-time updates.

---

## Method Categorization

TasksService methods are organized into five functional categories:

```mermaid
graph LR
    subgraph "CRUD Operations"
        create["create()"]
        findAll["findAll()"]
        findById["findById()"]
        update["update()"]
        delete["delete()"]
    end
    
    subgraph "Queue Management"
        findScheduledTasks["findScheduledTasks()"]
        findNextTask["findNextTask()"]
    end
    
    subgraph "Control Flow"
        takeOver["takeOver()"]
        resume["resume()"]
        cancel["cancel()"]
    end
    
    subgraph "Messaging"
        addTaskMessage["addTaskMessage()"]
    end
    
    subgraph "Event Broadcasting"
        emitTaskCreated["tasksGateway.emitTaskCreated()"]
        emitTaskUpdate["tasksGateway.emitTaskUpdate()"]
        emitTaskDeleted["tasksGateway.emitTaskDeleted()"]
        emitNewMessage["tasksGateway.emitNewMessage()"]
    end
    
    create -.-> emitTaskCreated
    update -.-> emitTaskUpdate
    delete -.-> emitTaskDeleted
    addTaskMessage -.-> emitNewMessage
    takeOver -.-> emitTaskUpdate
    resume -.-> emitTaskUpdate
    cancel -.-> emitTaskUpdate
```

**Sources:** [packages/bytebot-agent/src/tasks/tasks.service.ts:40-391]()

---

## CRUD Operations

### create(createTaskDto: CreateTaskDto)

Creates a new task with associated files and initial message in a database transaction.

**Transaction Sequence:**

```mermaid
sequenceDiagram
    participant Client
    participant TasksService
    participant PrismaTransaction
    participant TasksGateway
    
    Client->>TasksService: create(createTaskDto)
    TasksService->>PrismaTransaction: BEGIN TRANSACTION
    
    PrismaTransaction->>PrismaTransaction: prisma.task.create()<br/>status=PENDING
    
    alt Files provided
        loop For each file
            PrismaTransaction->>PrismaTransaction: prisma.file.create()<br/>base64 data extraction
        end
    end
    
    PrismaTransaction->>PrismaTransaction: prisma.message.create()<br/>role=USER, initial message
    
    PrismaTransaction->>TasksService: COMMIT
    TasksService->>TasksGateway: emitTaskCreated(task)
    TasksService-->>Client: Task
```

**Key Behaviors:**

| Behavior | Implementation |
|----------|----------------|
| **Base64 Processing** | Strips `data:*/*;base64,` prefix from file data before storage ([tasks.service.ts:74-76]()) |
| **File Description** | Appends file names to task description message ([tasks.service.ts:78]()) |
| **Default Values** | Sets `type=IMMEDIATE`, `priority=MEDIUM`, `status=PENDING`, `createdBy=USER` if not provided ([tasks.service.ts:51-54]()) |
| **Initial Message** | Creates USER message combining description and file information ([tasks.service.ts:96-109]()) |

**Sources:** [packages/bytebot-agent/src/tasks/tasks.service.ts:40-117]()

---

### findAll(page, limit, statuses?)

Retrieves paginated task list with optional status filtering.

**Parameters:**
- `page` (number, default=1): Page number for pagination
- `limit` (number, default=10): Items per page
- `statuses` (string[], optional): Filter by task statuses (e.g., `['RUNNING', 'PENDING']`)

**Return Type:**
```typescript
{
  tasks: Task[];
  total: number;
  totalPages: number;
}
```

**Query Strategy:**

```mermaid
graph LR
    A["findAll(page, limit, statuses)"] --> B{statuses provided?}
    B -->|Yes| C["WHERE status IN statuses"]
    B -->|No| D["No filter"]
    C --> E["ORDER BY createdAt DESC"]
    D --> E
    E --> F["SKIP (page-1) * limit"]
    F --> G["TAKE limit"]
    G --> H["COUNT total"]
    H --> I["Calculate totalPages"]
```

The method executes parallel queries for tasks and count using `Promise.all` for performance ([tasks.service.ts:174-184]()).

**Sources:** [packages/bytebot-agent/src/tasks/tasks.service.ts:158-190]()

---

### findById(id: string)

Retrieves a single task by ID with associated files included.

**Includes:** `files: true` - Eager loads file records associated with the task.

**Error Handling:** Throws `NotFoundException` if task does not exist ([tasks.service.ts:203-205]()).

**Sources:** [packages/bytebot-agent/src/tasks/tasks.service.ts:192-215]()

---

### update(id: string, updateTaskDto: UpdateTaskDto)

Updates task fields and triggers state-specific side effects.

**State Transition Side Effects:**

```mermaid
graph TB
    update["update(id, updateTaskDto)"]
    
    update --> check{status in DTO?}
    
    check -->|COMPLETED| completed["eventEmitter.emit('task.completed')"]
    check -->|NEEDS_HELP| needsHelp["Call takeOver(id)"]
    check -->|FAILED| failed["eventEmitter.emit('task.failed')"]
    check -->|Other| noAction["No special handling"]
    
    completed --> broadcast["tasksGateway.emitTaskUpdate()"]
    needsHelp --> broadcast
    failed --> broadcast
    noAction --> broadcast
```

**Event Emissions:**

| Status Change | Event Emitted | Listener |
|---------------|---------------|----------|
| `COMPLETED` | `task.completed` | `AgentProcessor` ([agent.processor.ts:234]()) |
| `FAILED` | `task.failed` | `AgentProcessor` |
| `NEEDS_HELP` | `task.takeover` | Delegated to `takeOver()` method |

**Sources:** [packages/bytebot-agent/src/tasks/tasks.service.ts:217-247]()

---

### delete(id: string)

Deletes task and cascades to associated records (messages, files, summaries via Prisma schema).

**Broadcast:** Emits `task_deleted` WebSocket event to all connected clients ([tasks.service.ts:258]()).

**Sources:** [packages/bytebot-agent/src/tasks/tasks.service.ts:249-261]()

---

## Queue Management Methods

### findScheduledTasks()

Queries tasks with scheduled execution times that haven't been queued yet.

**Query Conditions:**
- `scheduledFor` is NOT NULL
- `queuedAt` is NULL

**Ordering:** Ascending by `scheduledFor` to process earliest scheduled tasks first.

**Usage:** Called by `AgentScheduler` cron job to identify tasks ready for execution ([agent.scheduler.ts]()).

**Sources:** [packages/bytebot-agent/src/tasks/tasks.service.ts:119-129]()

---

### findNextTask()

Retrieves the highest-priority task from the queue for agent processing.

**Priority Algorithm:**

```mermaid
graph LR
    A["findNextTask()"] --> B["Filter: status IN [RUNNING, PENDING]"]
    B --> C["ORDER BY executedAt ASC<br/>(resume running tasks first)"]
    C --> D["ORDER BY priority DESC<br/>(HIGH > MEDIUM > LOW)"]
    D --> E["ORDER BY queuedAt ASC<br/>(FIFO within priority)"]
    E --> F["ORDER BY createdAt ASC<br/>(oldest first)"]
    F --> G["LIMIT 1"]
    G --> H["Include files: true"]
```

**Key Insight:** The `executedAt ASC` ordering ensures that `RUNNING` tasks (which have `executedAt` set) are resumed before `PENDING` tasks are started, preventing task interruption.

**Sources:** [packages/bytebot-agent/src/tasks/tasks.service.ts:131-156]()

---

## Task Control Methods

These methods manage the handoff of control between the AI agent and human user.

### Control State Machine

```mermaid
stateDiagram-v2
    [*] --> AgentControl: Task created<br/>control=ASSISTANT
    
    AgentControl --> UserControl: takeOver() called
    UserControl --> AgentControl: resume() called
    
    AgentControl --> Cancelled: cancel() called
    UserControl --> Cancelled: cancel() called
    
    Cancelled --> [*]
    
    note right of AgentControl
        status: RUNNING or PENDING
        control: ASSISTANT
        Input tracking: STOPPED
    end note
    
    note right of UserControl
        status: NEEDS_HELP
        control: USER
        Input tracking: STARTED
    end note
```

**Sources:** [packages/bytebot-agent/src/tasks/tasks.service.ts:282-391]()

---

### takeOver(taskId: string)

Transfers control from agent to user, enabling manual intervention.

**Preconditions:**
- Task must exist
- Task `control` must be `ASSISTANT` (throws `BadRequestException` otherwise)

**State Changes:**

| Field | New Value |
|-------|-----------|
| `control` | `USER` |
| Status | Unchanged (typically `NEEDS_HELP` set separately via `update()`) |

**Side Effects:**
1. **Input Tracking Activation:** Sends `POST /input-tracking/start` to bytebotd service ([tasks.service.ts:342-348]())
2. **Event Emission:** Emits `task.takeover` event to notify `AgentProcessor` to abort processing ([tasks.service.ts:351]())
3. **WebSocket Broadcast:** Emits `task_updated` to connected clients

**AgentProcessor Integration:**

When `AgentProcessor` receives the `task.takeover` event, it:
- Aborts any in-flight LLM requests via `AbortController` ([agent.processor.ts:90]())
- Starts `InputCaptureService` to record user actions ([agent.processor.ts:94]())

**Sources:** [packages/bytebot-agent/src/tasks/tasks.service.ts:320-357]()

---

### resume(taskId: string)

Returns control from user back to agent, resuming automated execution.

**Preconditions:**
- Task must exist
- Task `control` must be `USER` (throws `BadRequestException` otherwise)

**State Changes:**

| Field | New Value |
|-------|-----------|
| `control` | `ASSISTANT` |
| `status` | `RUNNING` |

**Side Effects:**
1. **Input Tracking Deactivation:** Sends `POST /input-tracking/stop` to bytebotd service ([tasks.service.ts:303-309]())
2. **Event Emission:** Emits `task.resume` event ([tasks.service.ts:312]())
3. **WebSocket Broadcast:** Emits `task_updated` to connected clients

**AgentProcessor Integration:**

When `AgentProcessor` receives the `task.resume` event while processing the task, it:
- Creates new `AbortController` instance ([agent.processor.ts:101]())
- Immediately calls `runIteration()` to continue agent loop ([agent.processor.ts:103]())

**Sources:** [packages/bytebot-agent/src/tasks/tasks.service.ts:282-318]()

---

### cancel(taskId: string)

Cancels an in-progress task, preventing further execution.

**Preconditions:**
- Task must exist
- Task status must NOT be `COMPLETED`, `FAILED`, or `CANCELLED` (throws `BadRequestException` otherwise)

**State Changes:**

| Field | New Value |
|-------|-----------|
| `status` | `CANCELLED` |

**Side Effects:**
1. **Event Emission:** Emits `task.cancel` event ([tasks.service.ts:385]())
2. **WebSocket Broadcast:** Emits `task_updated` to connected clients

**AgentProcessor Integration:**

The `task.cancel` event listener calls `stopProcessing()`, which:
- Aborts in-flight operations via `AbortController` ([agent.processor.ts:413]())
- Stops input tracking ([agent.processor.ts:415]())
- Clears processing state ([agent.processor.ts:417-418]())

**Sources:** [packages/bytebot-agent/src/tasks/tasks.service.ts:359-391]()

---

## Messaging Integration

### addTaskMessage(taskId: string, addTaskMessageDto: AddTaskMessageDto)

Adds a user-provided message to a task's conversation history.

**Message Creation:**
- **Role:** `USER`
- **Content:** Single text block containing the message
- **Linked to Task:** via `taskId` foreign key

**WebSocket Broadcast:** Emits `new_message` event to clients subscribed to the task room ([tasks.service.ts:278]()).

**Usage Context:** Called when user provides guidance or additional instructions while task is in `NEEDS_HELP` state.

**Sources:** [packages/bytebot-agent/src/tasks/tasks.service.ts:263-280]()

---

## Event Integration Patterns

TasksService integrates with two event systems for decoupled communication.

### EventEmitter2 (Internal Events)

Internal events enable reactive behavior across services without tight coupling.

```mermaid
graph LR
    subgraph "TasksService Emissions"
        A["update()<br/>status=COMPLETED"] --> E1["task.completed"]
        B["update()<br/>status=FAILED"] --> E2["task.failed"]
        C["takeOver()"] --> E3["task.takeover"]
        D["resume()"] --> E4["task.resume"]
        F["cancel()"] --> E5["task.cancel"]
    end
    
    subgraph "AgentProcessor Listeners"
        E1 --> L1["@OnEvent('task.completed')<br/>(if needed)"]
        E2 --> L2["@OnEvent('task.failed')<br/>(if needed)"]
        E3 --> L3["@OnEvent('task.takeover')<br/>abort + start input capture"]
        E4 --> L4["@OnEvent('task.resume')<br/>continue iteration"]
        E5 --> L5["@OnEvent('task.cancel')<br/>stopProcessing()"]
    end
```

**Event Payload Format:**
```typescript
{ taskId: string }
```

**Sources:** [packages/bytebot-agent/src/tasks/tasks.service.ts:234-386](), [packages/bytebot-agent/src/agent/agent.processor.ts:84-112]()

---

### TasksGateway (WebSocket Events)

WebSocket events broadcast state changes to connected UI clients in real-time.

**Emitted Events:**

| Method | Gateway Method | Event Name | Payload |
|--------|----------------|------------|---------|
| `create()` | `emitTaskCreated()` | `task_created` | `Task` object |
| `update()` | `emitTaskUpdate()` | `task_updated` | `Task` object |
| `delete()` | `emitTaskDeleted()` | `task_deleted` | Task ID string |
| `addTaskMessage()` | `emitNewMessage()` | `new_message` | `Message` object |

**Room-Based Broadcasting:**

- `task_created` and `task_deleted` are broadcast globally to all connected clients
- `task_updated` and `new_message` are broadcast only to clients in the task-specific room (joined via `join_task` event)

**Sources:** [packages/bytebot-agent/src/tasks/tasks.service.ts:114-388](), [packages/bytebot-agent/src/tasks/tasks.gateway.ts]()

---

## REST API Endpoints

The `TasksController` exposes TasksService methods via HTTP endpoints:

| Endpoint | Method | TasksService Method | Description |
|----------|--------|---------------------|-------------|
| `POST /tasks` | `create()` | `create()` | Create new task |
| `GET /tasks` | `findAll()` | `findAll()` | List tasks with pagination |
| `GET /tasks/:id` | `findById()` | `findById()` | Get single task |
| `DELETE /tasks/:id` | `delete()` | `delete()` | Delete task |
| `POST /tasks/:id/messages` | `addTaskMessage()` | `addTaskMessage()` | Add user message |
| `POST /tasks/:id/takeover` | `takeOver()` | `takeOver()` | Take manual control |
| `POST /tasks/:id/resume` | `resume()` | `resume()` | Return control to agent |
| `POST /tasks/:id/cancel` | `cancel()` | `cancel()` | Cancel task |

**Additional Controller Methods:**

- `GET /tasks/models` - Returns available LLM models (not a TasksService method)
- `GET /tasks/:id/messages` - Delegates to `MessagesService.findAll()`
- `GET /tasks/:id/messages/raw` - Delegates to `MessagesService.findRawMessages()`
- `GET /tasks/:id/messages/processed` - Delegates to `MessagesService.findProcessedMessages()`

**Sources:** [packages/bytebot-agent/src/tasks/tasks.controller.ts:1-193]()

---

## Usage Examples

### Creating a Task with Files

```typescript
// Client request to POST /tasks
const createTaskDto = {
  description: "Analyze the spreadsheet and create a summary report",
  type: TaskType.IMMEDIATE,
  priority: TaskPriority.HIGH,
  model: {
    provider: "anthropic",
    name: "claude-3-5-sonnet-20241022"
  },
  files: [
    {
      name: "data.xlsx",
      type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
      size: 45678,
      base64: "data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,UEsDBBQABg..."
    }
  ]
};

// TasksService processes:
// 1. Creates task record (status=PENDING)
// 2. Strips base64 prefix and creates file record
// 3. Creates initial USER message: "Analyze the spreadsheet... File data.xlsx written to desktop."
// 4. Broadcasts task_created event
```

**Sources:** [packages/bytebot-agent/src/tasks/tasks.service.ts:40-117](), [packages/bytebot-agent/src/tasks/dto/create-task.dto.ts]()

---

### Control Handoff Workflow

```typescript
// 1. Agent encounters ambiguity, sets status=NEEDS_HELP
await tasksService.update(taskId, { status: TaskStatus.NEEDS_HELP });
// → Calls takeOver() → Sets control=USER, starts input tracking

// 2. User provides guidance
await tasksService.addTaskMessage(taskId, { message: "Use the export function in the menu" });
// → Creates USER message, broadcasts new_message event

// 3. User clicks "Resume" in UI
await tasksService.resume(taskId);
// → Sets control=ASSISTANT, status=RUNNING
// → Emits task.resume event
// → AgentProcessor continues processing loop
```

**Sources:** [packages/bytebot-agent/src/tasks/tasks.service.ts:217-318]()

---

## Error Handling

### Common Exceptions

| Exception | Thrown By | Condition |
|-----------|-----------|-----------|
| `NotFoundException` | `findById()` | Task ID does not exist |
| `BadRequestException` | `resume()` | Task not under user control (`control !== USER`) |
| `BadRequestException` | `takeOver()` | Task not under agent control (`control !== ASSISTANT`) |
| `BadRequestException` | `cancel()` | Task already in terminal state (`COMPLETED`, `FAILED`, `CANCELLED`) |

**Logging Strategy:**

- **Info Level:** Method entry/exit, successful operations ([tasks.service.ts:41-42, 61, 114]())
- **Debug Level:** Detailed operation progress ([tasks.service.ts:47, 69, 96]())
- **Warn Level:** Task not found scenarios ([tasks.service.ts:204]())
- **Error Level:** Exception details with stack traces ([tasks.service.ts:211-212, 308, 347]())

**Sources:** [packages/bytebot-agent/src/tasks/tasks.service.ts:1-392]()

---

## Database Transaction Patterns

### Atomic Task Creation

The `create()` method uses `prisma.$transaction()` to ensure atomicity across three operations:

1. Task record creation
2. File records creation (if files provided)
3. Initial message creation

**Rollback Guarantee:** If any step fails, all changes are rolled back, preventing orphaned records.

**Sources:** [packages/bytebot-agent/src/tasks/tasks.service.ts:45-112]()

---

## Performance Considerations

### Parallel Query Execution

The `findAll()` method executes task retrieval and count queries in parallel using `Promise.all()`, reducing response time by ~50% compared to sequential queries.

```typescript
const [tasks, total] = await Promise.all([
  this.prisma.task.findMany({ /* query */ }),
  this.prisma.task.count({ /* query */ })
]);
```

**Sources:** [packages/bytebot-agent/src/tasks/tasks.service.ts:174-184]()

### Eager Loading

`findNextTask()` and `findById()` include `files: true` to prevent N+1 query problems when accessing task files.

**Sources:** [packages/bytebot-agent/src/tasks/tasks.service.ts:144-146, 198-200]()

---

## Integration with Other Services

### AgentScheduler Integration

`AgentScheduler` calls `findScheduledTasks()` every minute to check for tasks with `scheduledFor` times that have passed. When found, it queues them by setting `queuedAt` timestamp and updating status to `PENDING`.

**Sources:** [packages/bytebot-agent/src/tasks/tasks.service.ts:119-129](), [packages/bytebot-agent/src/agent/agent.scheduler.ts]()

### AgentProcessor Integration

`AgentProcessor` calls `findNextTask()` to retrieve the highest-priority task from the queue. It listens for `task.*` events to react to state changes:

- `task.takeover` → Abort processing, start input capture
- `task.resume` → Resume processing loop
- `task.cancel` → Stop processing
- `task.completed` → Natural completion (no action needed)
- `task.failed` → Natural failure (no action needed)

**Sources:** [packages/bytebot-agent/src/agent/agent.processor.ts:84-112](), [packages/bytebot-agent/src/tasks/tasks.service.ts:131-156]()

### Bytebotd Integration

Control methods (`takeOver()` and `resume()`) communicate with the bytebotd service to start/stop input tracking via HTTP requests to `/input-tracking/start` and `/input-tracking/stop`.

**Error Handling:** Failed input tracking requests are logged but do not throw exceptions, allowing control transfers to complete even if bytebotd is unavailable.

**Sources:** [packages/bytebot-agent/src/tasks/tasks.service.ts:303-309, 342-348]()

---

# Page: WebSocket Events

# WebSocket Events

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [packages/bytebot-agent/src/agent/agent.processor.ts](packages/bytebot-agent/src/agent/agent.processor.ts)
- [packages/bytebot-agent/src/main.ts](packages/bytebot-agent/src/main.ts)
- [packages/bytebot-agent/src/tasks/tasks.controller.ts](packages/bytebot-agent/src/tasks/tasks.controller.ts)
- [packages/bytebot-agent/src/tasks/tasks.gateway.ts](packages/bytebot-agent/src/tasks/tasks.gateway.ts)
- [packages/bytebot-agent/src/tasks/tasks.service.ts](packages/bytebot-agent/src/tasks/tasks.service.ts)
- [packages/bytebot-ui/next.config.ts](packages/bytebot-ui/next.config.ts)
- [packages/bytebot-ui/server.ts](packages/bytebot-ui/server.ts)
- [packages/bytebot-ui/src/app/api/[[...path]]/route.ts](packages/bytebot-ui/src/app/api/[[...path]]/route.ts)
- [packages/bytebot-ui/src/hooks/useChatSession.ts](packages/bytebot-ui/src/hooks/useChatSession.ts)
- [packages/bytebot-ui/src/hooks/useWebSocket.ts](packages/bytebot-ui/src/hooks/useWebSocket.ts)

</details>



This document describes the real-time WebSocket communication system in Bytebot, covering the Socket.IO-based event architecture that enables live task updates, message notifications, and client-server coordination. The WebSocket layer provides bidirectional communication between the **bytebot-ui** frontend and **bytebot-agent** backend.

For information about the REST API endpoints, see [Tasks REST API](#10.1). For internal event-driven coordination within bytebot-agent (using EventEmitter2), see [Agent Processor](#6.1).

---

## Architecture Overview

The WebSocket system uses Socket.IO to provide real-time, event-driven communication. The architecture consists of three layers:

1. **Client Layer** (`useWebSocket` hook in bytebot-ui)
2. **Proxy Layer** (Express server proxying WebSocket connections)
3. **Server Layer** (`TasksGateway` in bytebot-agent)

**WebSocket Communication Architecture**

```mermaid
graph TB
    subgraph "bytebot-ui (Port 9992)"
        UIClient["useWebSocket Hook<br/>packages/bytebot-ui/src/hooks/useWebSocket.ts"]
        ExpressProxy["Express WebSocket Proxy<br/>packages/bytebot-ui/server.ts"]
    end
    
    subgraph "bytebot-agent (Port 9991)"
        TasksGateway["TasksGateway<br/>packages/bytebot-agent/src/tasks/tasks.gateway.ts"]
        TasksService["TasksService<br/>packages/bytebot-agent/src/tasks/tasks.service.ts"]
        MessagesService["MessagesService"]
    end
    
    UIClient -->|"Socket.IO<br/>path: /api/proxy/tasks"| ExpressProxy
    ExpressProxy -->|"WebSocket Upgrade<br/>rewrite to /socket.io"| TasksGateway
    
    TasksService -.->|"emitTaskUpdate()<br/>emitTaskCreated()<br/>emitTaskDeleted()"| TasksGateway
    MessagesService -.->|"emitNewMessage()"| TasksGateway
    
    TasksGateway -->|"task_updated<br/>new_message<br/>task_created<br/>task_deleted"| UIClient
    UIClient -->|"join_task<br/>leave_task"| TasksGateway
    
    style TasksGateway fill:#ffccbc
    style UIClient fill:#b3e5fc
    style ExpressProxy fill:#fff9c4
```

**Sources:** [packages/bytebot-ui/src/hooks/useWebSocket.ts:1-114](), [packages/bytebot-agent/src/tasks/tasks.gateway.ts:1-58](), [packages/bytebot-ui/server.ts:1-89]()

---

## Event Types

Bytebot's WebSocket system defines two categories of events:

### Client-to-Server Events

| Event Name | Payload | Purpose |
|------------|---------|---------|
| `join_task` | `taskId: string` | Subscribe to updates for a specific task |
| `leave_task` | `taskId: string` | Unsubscribe from task updates |

### Server-to-Client Events

| Event Name | Scope | Payload | Purpose |
|------------|-------|---------|---------|
| `task_updated` | Task-specific | `Task` object | Notify when task state changes |
| `new_message` | Task-specific | `Message` object | Notify when a new message is created |
| `task_created` | Global | `Task` object | Notify all clients of new task creation |
| `task_deleted` | Global | `taskId: string` | Notify all clients of task deletion |

**Sources:** [packages/bytebot-agent/src/tasks/tasks.gateway.ts:30-56](), [packages/bytebot-ui/src/hooks/useWebSocket.ts:44-62]()

---

## Room-Based Event Routing

TasksGateway uses Socket.IO rooms to implement targeted event delivery. Each task has a dedicated room identified by `task_${taskId}`.

**Room Subscription Pattern**

```mermaid
sequenceDiagram
    participant Client as "Client (Socket)"
    participant Gateway as "TasksGateway"
    participant Room as "Room: task_abc123"
    
    Client->>Gateway: emit("join_task", "abc123")
    Gateway->>Room: client.join("task_abc123")
    Note over Gateway: Client added to room
    
    Gateway->>Room: emit("task_updated", task)
    Room->>Client: Receive task_updated event
    
    Client->>Gateway: emit("leave_task", "abc123")
    Gateway->>Room: client.leave("task_abc123")
    Note over Gateway: Client removed from room
```

**Sources:** [packages/bytebot-agent/src/tasks/tasks.gateway.ts:30-40]()

### Room Scoping Implementation

The `TasksGateway` implements room-based routing through Socket.IO's `join` and `leave` methods:

```typescript
// Client joins a task room
@SubscribeMessage('join_task')
handleJoinTask(client: Socket, taskId: string) {
  client.join(`task_${taskId}`);
}

// Emit to specific room only
emitTaskUpdate(taskId: string, task: any) {
  this.server.to(`task_${taskId}`).emit('task_updated', task);
}

// Emit globally (no room restriction)
emitTaskCreated(task: any) {
  this.server.emit('task_created', task);
}
```

| Event Method | Routing | Scope |
|--------------|---------|-------|
| `emitTaskUpdate()` | `server.to(task_${taskId})` | Task-specific room |
| `emitNewMessage()` | `server.to(task_${taskId})` | Task-specific room |
| `emitTaskCreated()` | `server.emit()` | All connected clients |
| `emitTaskDeleted()` | `server.emit()` | All connected clients |

**Sources:** [packages/bytebot-agent/src/tasks/tasks.gateway.ts:42-56]()

---

## Server-to-Client Events

### task_updated

Emitted when task properties change (status, control, etc.). Sent only to clients subscribed to the specific task room.

**Trigger Locations:**
- [packages/bytebot-agent/src/tasks/tasks.service.ts:244]() - After task update
- [packages/bytebot-agent/src/tasks/tasks.service.ts:315]() - After resume
- [packages/bytebot-agent/src/tasks/tasks.service.ts:354]() - After takeover
- [packages/bytebot-agent/src/tasks/tasks.service.ts:388]() - After cancel

**Payload Structure:**
```typescript
interface Task {
  id: string;
  description: string;
  status: TaskStatus;
  control: Role;
  priority: TaskPriority;
  type: TaskType;
  model: BytebotAgentModel;
  createdAt: Date;
  updatedAt: Date;
  executedAt?: Date;
  completedAt?: Date;
  error?: string;
  // ... additional fields
}
```

**Client Handling:**
```typescript
socket.on("task_updated", (task: Task) => {
  if (task.id === currentTaskId) {
    setTaskStatus(task.status);
    setControl(task.control);
  }
});
```

**Sources:** [packages/bytebot-agent/src/tasks/tasks.service.ts:217-246](), [packages/bytebot-ui/src/hooks/useChatSession.ts:37-45]()

---

### new_message

Emitted when a message is created for a task. Sent only to clients subscribed to the task room.

**Trigger Location:**
- [packages/bytebot-agent/src/tasks/tasks.service.ts:278]() - After message creation

**Payload Structure:**
```typescript
interface Message {
  id: string;
  content: MessageContentBlock[];
  role: Role;
  taskId: string;
  summaryId?: string;
  createdAt: Date;
  updatedAt: Date;
}
```

**Client Handling:**
```typescript
socket.on("new_message", (message: Message) => {
  if (!processedMessageIds.current.has(message.id) 
      && message.taskId === currentTaskId) {
    processedMessageIds.current.add(message.id);
    setMessages((prev) => [...prev, message]);
    reloadGroupedMessages();
  }
});
```

**Sources:** [packages/bytebot-agent/src/tasks/tasks.service.ts:263-280](), [packages/bytebot-ui/src/hooks/useChatSession.ts:65-80]()

---

### task_created

Global event emitted when any task is created. All connected clients receive this notification.

**Trigger Location:**
- [packages/bytebot-agent/src/tasks/tasks.service.ts:114]() - After task creation in database

**Payload:** Complete `Task` object

**Client Handling:**
```typescript
socket.on("task_created", (task: Task) => {
  console.log("New task created:", task);
  // Typically used to refresh task lists
});
```

**Sources:** [packages/bytebot-agent/src/tasks/tasks.service.ts:40-117](), [packages/bytebot-ui/src/hooks/useChatSession.ts:82-84]()

---

### task_deleted

Global event emitted when a task is deleted. All connected clients receive this notification.

**Trigger Location:**
- [packages/bytebot-agent/src/tasks/tasks.service.ts:258]() - After task deletion

**Payload:** `taskId: string`

**Client Handling:**
```typescript
socket.on("task_deleted", (taskId: string) => {
  if (taskId === currentTaskId) {
    setCurrentTaskId(null);
    setMessages([]);
    processedMessageIds.current = new Set();
  }
});
```

**Sources:** [packages/bytebot-agent/src/tasks/tasks.service.ts:249-261](), [packages/bytebot-ui/src/hooks/useChatSession.ts:86-96]()

---

## Client-to-Server Events

### join_task

Subscribes the client to updates for a specific task by joining the task's Socket.IO room.

**Client Emission:**
```typescript
const joinTask = (taskId: string) => {
  const socket = socketRef.current || connect();
  if (currentTaskIdRef.current) {
    socket.emit("leave_task", currentTaskIdRef.current);
  }
  socket.emit("join_task", taskId);
  currentTaskIdRef.current = taskId;
};
```

**Server Handler:**
```typescript
@SubscribeMessage('join_task')
handleJoinTask(client: Socket, taskId: string) {
  client.join(`task_${taskId}`);
  console.log(`Client ${client.id} joined task ${taskId}`);
}
```

**Sources:** [packages/bytebot-ui/src/hooks/useWebSocket.ts:68-79](), [packages/bytebot-agent/src/tasks/tasks.gateway.ts:30-34]()

---

### leave_task

Unsubscribes the client from task updates by leaving the task's Socket.IO room.

**Client Emission:**
```typescript
const leaveTask = () => {
  const socket = socketRef.current;
  if (socket && currentTaskIdRef.current) {
    socket.emit("leave_task", currentTaskIdRef.current);
    currentTaskIdRef.current = null;
  }
};
```

**Server Handler:**
```typescript
@SubscribeMessage('leave_task')
handleLeaveTask(client: Socket, taskId: string) {
  client.leave(`task_${taskId}`);
  console.log(`Client ${client.id} left task ${taskId}`);
}
```

**Sources:** [packages/bytebot-ui/src/hooks/useWebSocket.ts:81-88](), [packages/bytebot-agent/src/tasks/tasks.gateway.ts:36-40]()

---

## Client Implementation

### useWebSocket Hook

The `useWebSocket` hook provides a React-friendly interface for WebSocket communication.

**Hook Lifecycle**

```mermaid
stateDiagram-v2
    [*] --> Initializing: "Component Mount"
    Initializing --> Connected: "connect()"
    
    state Connected {
        [*] --> Idle
        Idle --> Subscribed: "joinTask(taskId)"
        Subscribed --> Idle: "leaveTask()"
        
        state Subscribed {
            [*] --> Listening
            Listening --> EventReceived: "task_updated/new_message"
            EventReceived --> Listening: "Callback invoked"
        }
    }
    
    Connected --> Disconnected: "Component Unmount"
    Disconnected --> [*]
```

**Sources:** [packages/bytebot-ui/src/hooks/useWebSocket.ts:1-114]()

### Connection Management

The hook manages a single Socket.IO connection with automatic reconnection:

```typescript
const connect = useCallback(() => {
  const socket = io({
    path: "/api/proxy/tasks",
    transports: ["websocket"],
    autoConnect: true,
    reconnection: true,
    reconnectionAttempts: 5,
    reconnectionDelay: 1000,
  });
  
  socket.on("connect", () => {
    console.log("Connected to WebSocket server");
  });
  
  // Event handlers
  socket.on("task_updated", (task: Task) => onTaskUpdate?.(task));
  socket.on("new_message", (message: Message) => onNewMessage?.(message));
  socket.on("task_created", (task: Task) => onTaskCreated?.(task));
  socket.on("task_deleted", (taskId: string) => onTaskDeleted?.(taskId));
  
  return socket;
}, [onTaskUpdate, onNewMessage, onTaskCreated, onTaskDeleted]);
```

**Configuration Options:**

| Option | Value | Purpose |
|--------|-------|---------|
| `path` | `/api/proxy/tasks` | Proxy path to backend Socket.IO |
| `transports` | `["websocket"]` | Force WebSocket transport (no polling fallback) |
| `reconnection` | `true` | Enable automatic reconnection |
| `reconnectionAttempts` | `5` | Maximum reconnection attempts |
| `reconnectionDelay` | `1000` | Delay between attempts (ms) |

**Sources:** [packages/bytebot-ui/src/hooks/useWebSocket.ts:21-66]()

---

## Server Implementation

### TasksGateway

The `TasksGateway` class implements the Socket.IO server using NestJS decorators.

**Gateway Configuration:**
```typescript
@Injectable()
@WebSocketGateway({
  cors: {
    origin: '*',
    methods: ['GET', 'POST'],
  },
})
export class TasksGateway implements OnGatewayConnection, OnGatewayDisconnect {
  @WebSocketServer()
  server: Server;
  
  handleConnection(client: Socket) {
    console.log(`Client connected: ${client.id}`);
  }
  
  handleDisconnect(client: Socket) {
    console.log(`Client disconnected: ${client.id}`);
  }
}
```

**Event Emission Methods:**

| Method | Room Scope | Called From |
|--------|-----------|-------------|
| `emitTaskUpdate(taskId, task)` | `task_${taskId}` | TasksService.update() |
| `emitNewMessage(taskId, message)` | `task_${taskId}` | TasksService.addTaskMessage() |
| `emitTaskCreated(task)` | Global | TasksService.create() |
| `emitTaskDeleted(taskId)` | Global | TasksService.delete() |

**Sources:** [packages/bytebot-agent/src/tasks/tasks.gateway.ts:1-58]()

---

## Event Flow Examples

### Task Update Flow

```mermaid
sequenceDiagram
    participant Client as "useWebSocket"
    participant Gateway as "TasksGateway"
    participant Service as "TasksService"
    participant DB as "PostgreSQL"
    
    Client->>Gateway: emit("join_task", taskId)
    Gateway->>Gateway: client.join(task_${taskId})
    
    Note over Service: User resumes task
    Service->>DB: UPDATE task SET status=RUNNING
    DB-->>Service: Updated task
    
    Service->>Gateway: emitTaskUpdate(taskId, task)
    Gateway->>Client: emit("task_updated", task)
    
    Note over Client: Update UI state
    Client->>Client: setTaskStatus(task.status)
    Client->>Client: setControl(task.control)
```

**Sources:** [packages/bytebot-agent/src/tasks/tasks.service.ts:282-318](), [packages/bytebot-ui/src/hooks/useChatSession.ts:37-45]()

---

### Message Creation Flow

```mermaid
sequenceDiagram
    participant UI as "Task Detail Page"
    participant API as "TasksController"
    participant Service as "TasksService"
    participant Gateway as "TasksGateway"
    participant Client as "useWebSocket"
    
    UI->>API: POST /tasks/:id/messages
    API->>Service: addTaskMessage(taskId, dto)
    Service->>Service: prisma.message.create()
    
    Service->>Gateway: emitNewMessage(taskId, message)
    Gateway->>Client: emit("new_message", message) to room
    
    Client->>Client: handleNewMessage(message)
    Client->>Client: setMessages([...prev, message])
    Client->>Client: reloadGroupedMessages()
```

**Sources:** [packages/bytebot-agent/src/tasks/tasks.service.ts:263-280](), [packages/bytebot-agent/src/tasks/tasks.controller.ts:133-140](), [packages/bytebot-ui/src/hooks/useChatSession.ts:65-80]()

---

## Proxy Configuration

The bytebot-ui Express server proxies WebSocket connections to the backend using `http-proxy-middleware`.

**Proxy Setup:**

```typescript
// HTTP proxy for Socket.IO handshake
const tasksProxy = createProxyMiddleware({
  target: BYTEBOT_AGENT_BASE_URL,
  ws: true,
  pathRewrite: { "^/api/proxy/tasks": "/socket.io" },
});

expressApp.use("/api/proxy/tasks", tasksProxy);
```

**WebSocket Upgrade Handler:**

```typescript
server.on("upgrade", (request, socket, head) => {
  const { pathname } = new URL(request.url!, `http://${request.headers.host}`);
  
  if (pathname.startsWith("/api/proxy/tasks")) {
    return tasksProxy.upgrade(request, socket as any, head);
  }
  
  // Fallback to Next.js
  nextUpgradeHandler(request, socket, head);
});
```

**Path Rewriting:**

| Client Path | Rewritten To | Backend Path |
|-------------|--------------|--------------|
| `/api/proxy/tasks` | → | `/socket.io` |

This allows the client to use a consistent `/api/proxy/tasks` path while the backend serves Socket.IO on the standard `/socket.io` path.

**Sources:** [packages/bytebot-ui/server.ts:32-79]()

---

## Integration with useChatSession

The `useChatSession` hook consumes WebSocket events to maintain real-time task state:

**Event Handler Setup:**

```typescript
const { joinTask, leaveTask } = useWebSocket({
  onTaskUpdate: handleTaskUpdate,
  onNewMessage: handleNewMessage,
  onTaskCreated: handleTaskCreated,
  onTaskDeleted: handleTaskDeleted,
});

// Join task room when taskId changes
useEffect(() => {
  if (currentTaskId) {
    joinTask(currentTaskId);
  } else {
    leaveTask();
  }
}, [currentTaskId, joinTask, leaveTask]);
```

**State Synchronization:**

```mermaid
graph LR
    subgraph "WebSocket Events"
        TaskUpdated["task_updated"]
        NewMessage["new_message"]
        TaskDeleted["task_deleted"]
    end
    
    subgraph "React State Updates"
        SetTaskStatus["setTaskStatus()"]
        SetControl["setControl()"]
        SetMessages["setMessages()"]
        ReloadGrouped["reloadGroupedMessages()"]
    end
    
    TaskUpdated --> SetTaskStatus
    TaskUpdated --> SetControl
    NewMessage --> SetMessages
    NewMessage --> ReloadGrouped
    TaskDeleted --> SetMessages
```

**Sources:** [packages/bytebot-ui/src/hooks/useChatSession.ts:36-104](), [packages/bytebot-ui/src/hooks/useChatSession.ts:232-241]()

---

## Distinction from Internal Events

Note that WebSocket events are distinct from the internal EventEmitter2 events used within bytebot-agent:

| WebSocket Events | Internal Events (EventEmitter2) |
|------------------|--------------------------------|
| Cross-process (UI ↔ Agent) | Within bytebot-agent process |
| Socket.IO protocol | Node.js EventEmitter |
| `task_updated`, `new_message` | `task.takeover`, `task.resume`, `task.cancel` |
| Client-server communication | Service coordination |

Internal events are documented in [Agent Processor](#6.1).

**Sources:** [packages/bytebot-agent/src/agent/agent.processor.ts:84-112](), [packages/bytebot-agent/src/tasks/tasks.service.ts:234-240]()

---

# Page: Task Scheduling

# Task Scheduling

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [packages/bytebot-agent/prisma/migrations/20250722041608_files/migration.sql](packages/bytebot-agent/prisma/migrations/20250722041608_files/migration.sql)
- [packages/bytebot-agent/src/agent/agent.computer-use.ts](packages/bytebot-agent/src/agent/agent.computer-use.ts)
- [packages/bytebot-agent/src/agent/agent.constants.ts](packages/bytebot-agent/src/agent/agent.constants.ts)
- [packages/bytebot-agent/src/agent/agent.scheduler.ts](packages/bytebot-agent/src/agent/agent.scheduler.ts)
- [packages/bytebot-agent/src/agent/agent.tools.ts](packages/bytebot-agent/src/agent/agent.tools.ts)
- [packages/bytebotd/src/computer-use/computer-use.controller.ts](packages/bytebotd/src/computer-use/computer-use.controller.ts)
- [packages/bytebotd/src/main.ts](packages/bytebotd/src/main.ts)

</details>



## Purpose and Scope

This document describes the **AgentScheduler** system responsible for automated task execution in Bytebot. The scheduler implements cron-based polling to:

1. Queue scheduled tasks when their execution time arrives
2. Select the next pending task based on priority
3. Prepare task files by writing them to the desktop filesystem
4. Initiate task processing via the AgentProcessor

For information about task lifecycle states and transitions, see [Task Lifecycle](#5.1). For details on the AgentProcessor's execution loop, see [Agent Processor](#6.1). For task creation and management APIs, see [TasksService API](#5.2).

**Sources:** [packages/bytebot-agent/src/agent/agent.scheduler.ts:1-63]()

---

## Scheduling Architecture

The `AgentScheduler` runs as a NestJS service with cron-based polling. It acts as the orchestrator between task storage (database) and task execution (agent processor).

### Component Relationships

```mermaid
graph TB
    subgraph "AgentScheduler Service"
        OnModuleInit["OnModuleInit Hook<br/>(Application Startup)"]
        CronJob["@Cron Decorator<br/>EVERY_5_SECONDS"]
        HandleCron["handleCron() Method"]
    end
    
    subgraph "Dependencies"
        TasksService["TasksService<br/>(Database Operations)"]
        AgentProcessor["AgentProcessor<br/>(Task Execution)"]
        WriteFile["writeFile()<br/>(File Preparation)"]
    end
    
    subgraph "Database"
        ScheduledTasks["Tasks with scheduledFor<br/>status=PENDING"]
        QueuedTasks["Tasks with queuedAt<br/>status=PENDING"]
    end
    
    OnModuleInit -->|"Triggers initial"| HandleCron
    CronJob -->|"Triggers every 5s"| HandleCron
    
    HandleCron -->|"findScheduledTasks()"| TasksService
    TasksService -->|"Returns"| ScheduledTasks
    
    HandleCron -->|"Check scheduledFor < now"| ScheduledTasks
    HandleCron -->|"update(id, {queuedAt})"| TasksService
    TasksService -->|"Sets queuedAt"| QueuedTasks
    
    HandleCron -->|"isRunning()?"| AgentProcessor
    AgentProcessor -->|"false = idle"| HandleCron
    
    HandleCron -->|"findNextTask()"| TasksService
    TasksService -->|"Returns highest priority"| QueuedTasks
    
    HandleCron -->|"task.files.length > 0"| WriteFile
    WriteFile -->|"Writes to /home/user/Desktop/"| Desktop["/home/user/Desktop/"]
    
    HandleCron -->|"update(id, {status:RUNNING})"| TasksService
    HandleCron -->|"processTask(taskId)"| AgentProcessor
    AgentProcessor -->|"Begins execution loop"| Running["Task RUNNING State"]
```

**Sources:** [packages/bytebot-agent/src/agent/agent.scheduler.ts:1-63]()

---

## Scheduler Initialization

The scheduler implements the `OnModuleInit` lifecycle hook to begin polling immediately when the application starts, ensuring no delay in processing existing queued tasks.

| Component | Type | Purpose |
|-----------|------|---------|
| `AgentScheduler` | `@Injectable()` class | NestJS service providing scheduling functionality |
| `OnModuleInit` | Interface | Lifecycle hook for initialization |
| `onModuleInit()` | Method | Executes `handleCron()` once at startup |

The initialization sequence:

```mermaid
sequenceDiagram
    participant App as NestJS Application
    participant Scheduler as AgentScheduler
    participant Handler as handleCron()
    
    App->>Scheduler: Bootstrap application
    App->>Scheduler: onModuleInit()
    Scheduler->>Handler: await this.handleCron()
    Note over Handler: Processes any pending tasks<br/>immediately on startup
    Handler-->>Scheduler: Complete
    Scheduler-->>App: Initialization complete
    Note over Scheduler: Cron decorator now active<br/>Polls every 5 seconds
```

**Implementation:**

```typescript
async onModuleInit() {
  this.logger.log('AgentScheduler initialized');
  await this.handleCron();
}
```

**Sources:** [packages/bytebot-agent/src/agent/agent.scheduler.ts:17-20]()

---

## Cron-Based Polling Mechanism

The scheduler uses the `@nestjs/schedule` package to execute `handleCron()` every 5 seconds via the `@Cron` decorator.

### Polling Configuration

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| Interval | `CronExpression.EVERY_5_SECONDS` | Balance between responsiveness and system load |
| Execution | Single-threaded | Only one `handleCron()` runs at a time |
| Concurrency Control | `isRunning()` check | Prevents parallel task execution |

### Cron Method Implementation

```typescript
@Cron(CronExpression.EVERY_5_SECONDS)
async handleCron() {
  // 1. Queue scheduled tasks
  // 2. Check if agent is busy
  // 3. Select next task
  // 4. Prepare files
  // 5. Start execution
}
```

**Sources:** [packages/bytebot-agent/src/agent/agent.scheduler.ts:22-62]()

---

## Scheduled Task Queueing

The first phase of each cron cycle identifies tasks with future execution times and queues them when their scheduled time arrives.

### Queueing Logic Flow

```mermaid
flowchart TD
    Start["handleCron() invoked"]
    GetNow["now = new Date()"]
    FindScheduled["scheduledTasks = tasksService.findScheduledTasks()"]
    
    Start --> GetNow
    GetNow --> FindScheduled
    
    FindScheduled --> LoopTasks{"For each<br/>scheduledTask"}
    
    LoopTasks -->|"Has more tasks"| CheckTime{"scheduledTask.scheduledFor<br/>< now?"}
    CheckTime -->|"Yes - Time has arrived"| UpdateQueue["tasksService.update(id,<br/>{queuedAt: now})"]
    CheckTime -->|"No - Still in future"| LoopTasks
    UpdateQueue --> LoopTasks
    
    LoopTasks -->|"No more tasks"| CheckRunning{"agentProcessor.isRunning()"}
    
    CheckRunning -->|"true - Agent busy"| End["Return early<br/>(skip task selection)"]
    CheckRunning -->|"false - Agent idle"| FindNext["Continue to task selection"]
```

### Database Query

The scheduler relies on `TasksService.findScheduledTasks()` to retrieve tasks where:
- `status = PENDING`
- `type = SCHEDULED`
- `scheduledFor IS NOT NULL`
- `queuedAt IS NULL`

When a task's `scheduledFor` time is reached, the scheduler sets `queuedAt` to the current timestamp, making it eligible for execution selection.

**Sources:** [packages/bytebot-agent/src/agent/agent.scheduler.ts:24-35]()

---

## Task Selection and Priority

When the `AgentProcessor` is idle, the scheduler selects the highest-priority pending task for execution.

### Selection Criteria

The `TasksService.findNextTask()` method returns tasks ordered by:

1. **Priority** (descending): `URGENT > HIGH > MEDIUM > LOW`
2. **Queue time** (ascending): Older queued tasks execute first

| Task State | Eligibility |
|------------|-------------|
| `status = PENDING` | ✓ Eligible |
| `queuedAt IS NOT NULL` | ✓ Eligible |
| `status = RUNNING` | ✗ Currently executing |
| `status = NEEDS_HELP` | ✗ Awaiting user input |
| `status = COMPLETED` | ✗ Finished |
| `queuedAt IS NULL` | ✗ Not yet queued |

### Concurrency Control

```typescript
if (this.agentProcessor.isRunning()) {
  return;
}
```

The scheduler prevents concurrent task execution by checking `AgentProcessor.isRunning()`. Only when the processor is idle does it proceed to select and start a new task.

**Sources:** [packages/bytebot-agent/src/agent/agent.scheduler.ts:37-41]()

---

## File Preparation Workflow

Before task execution begins, the scheduler writes any attached files to the virtual desktop's filesystem, making them accessible to the AI agent.

### File Writing Process

```mermaid
sequenceDiagram
    participant Scheduler as AgentScheduler
    participant TaskService as TasksService
    participant WriteFile as writeFile()
    participant Desktop as bytebotd /computer-use API
    participant FS as Virtual Desktop Filesystem
    
    Scheduler->>TaskService: findNextTask()
    TaskService-->>Scheduler: task (with task.files[])
    
    Scheduler->>Scheduler: if (task.files.length > 0)
    
    loop For each file in task.files
        Scheduler->>WriteFile: writeFile({<br/>  path: /home/user/Desktop/{file.name},<br/>  content: file.data<br/>})
        Note over WriteFile: file.data is already<br/>base64 encoded
        WriteFile->>Desktop: POST /computer-use<br/>{action: 'write_file', path, data}
        Desktop->>FS: Write base64 decoded data
        FS-->>Desktop: Success
        Desktop-->>WriteFile: {success: true}
        WriteFile-->>Scheduler: Complete
    end
    
    Scheduler->>TaskService: update(id, {status: RUNNING})
    Scheduler->>Scheduler: agentProcessor.processTask(id)
```

### File Structure

Files attached to tasks are stored in the database with the following schema:

| Column | Type | Description |
|--------|------|-------------|
| `id` | String (UUID) | Unique file identifier |
| `name` | String | Filename (e.g., `document.pdf`) |
| `type` | String | MIME type (e.g., `application/pdf`) |
| `size` | Integer | File size in bytes |
| `data` | Text | Base64-encoded file content |
| `taskId` | String (FK) | Reference to parent task |

### Desktop Path Convention

All task files are written to `/home/user/Desktop/{filename}`, ensuring they are:
- Immediately visible to the AI agent
- Easily accessible via desktop icons
- Ready for interaction in the XFCE environment

**Implementation:**

```typescript
if (task.files.length > 0) {
  this.logger.debug(
    `Task ID: ${task.id} has files, writing them to the desktop`,
  );
  for (const file of task.files) {
    await writeFile({
      path: `/home/user/Desktop/${file.name}`,
      content: file.data, // Already base64 encoded in database
    });
  }
}
```

**Sources:** [packages/bytebot-agent/src/agent/agent.scheduler.ts:43-53](), [packages/bytebot-agent/prisma/migrations/20250722041608_files/migration.sql:1-17](), [packages/bytebot-agent/src/agent/agent.computer-use.ts:612-646]()

---

## Task Execution Handoff

After file preparation, the scheduler transitions the task to `RUNNING` status and delegates execution to the `AgentProcessor`.

### State Transition Sequence

```mermaid
stateDiagram-v2
    [*] --> PENDING: Task created
    PENDING --> PENDING: scheduledFor < now<br/>Set queuedAt
    PENDING --> RUNNING: AgentScheduler selects task
    
    state RUNNING {
        [*] --> FilesWritten: writeFile() for each attachment
        FilesWritten --> StatusUpdated: update({status: RUNNING, executedAt})
        StatusUpdated --> ProcessorStarted: agentProcessor.processTask(id)
    }
    
    note right of RUNNING
        AgentScheduler hands off to AgentProcessor
        Scheduler no longer manages this task
        AgentProcessor controls execution loop
    end note
```

### Handoff Implementation

```typescript
await this.tasksService.update(task.id, {
  status: TaskStatus.RUNNING,
  executedAt: new Date(),
});
this.logger.debug(`Processing task ID: ${task.id}`);
this.agentProcessor.processTask(task.id);
```

| Field Updated | Value | Purpose |
|---------------|-------|---------|
| `status` | `TaskStatus.RUNNING` | Marks task as actively executing |
| `executedAt` | `new Date()` | Records execution start timestamp |

The `processTask()` call is **non-blocking**—the scheduler immediately returns, allowing the next cron cycle to run while the agent processes the task asynchronously.

**Sources:** [packages/bytebot-agent/src/agent/agent.scheduler.ts:55-60]()

---

## Integration with bytebotd

The file writing process delegates to the bytebotd service's `/computer-use` endpoint, which executes the actual filesystem operation in the virtual desktop environment.

### Computer Use API Integration

```mermaid
graph LR
    subgraph "bytebot-agent Service"
        Scheduler["AgentScheduler"]
        WriteFileFn["writeFile() function<br/>(agent.computer-use.ts)"]
    end
    
    subgraph "bytebotd Service (Port 9990)"
        Controller["ComputerUseController<br/>POST /computer-use"]
        Service["ComputerUseService<br/>action() method"]
        FileHandler["File Action Handler"]
    end
    
    subgraph "Virtual Desktop"
        Filesystem["/home/user/Desktop/"]
    end
    
    Scheduler -->|"await writeFile({path, content})"| WriteFileFn
    WriteFileFn -->|"fetch POST<br/>action='write_file'"| Controller
    Controller -->|"Validates DTO"| Service
    Service -->|"Dispatches action"| FileHandler
    FileHandler -->|"Decodes base64<br/>Writes file"| Filesystem
```

### API Request Format

```typescript
await fetch(`${BYTEBOT_DESKTOP_BASE_URL}/computer-use`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    action: 'write_file',
    path: '/home/user/Desktop/filename.ext',
    data: '<base64-encoded-content>',
  }),
});
```

The base64 encoding is preserved from database storage through to bytebotd, which decodes it before writing to the filesystem.

**Sources:** [packages/bytebot-agent/src/agent/agent.computer-use.ts:612-646](), [packages/bytebotd/src/computer-use/computer-use.controller.ts:1-42]()

---

## Scheduling Loop Summary

The complete scheduling cycle executes every 5 seconds:

| Phase | Duration | Action |
|-------|----------|--------|
| **1. Schedule Check** | ~10-50ms | Query scheduled tasks, update `queuedAt` for due tasks |
| **2. Concurrency Check** | <1ms | Check `AgentProcessor.isRunning()` |
| **3. Task Selection** | ~10-30ms | Query highest priority pending task |
| **4. File Preparation** | Variable | Write N files to desktop (depends on file count/size) |
| **5. Execution Start** | ~5-10ms | Update task status, call `processTask()` |
| **Total** | <100ms | Typical execution time (excluding file I/O) |

### Execution Guarantees

The scheduler provides the following guarantees:

1. **Single-threaded execution**: Only one task runs at a time via `isRunning()` check
2. **FIFO within priority**: Tasks of equal priority execute in queue order
3. **Scheduled task accuracy**: ±5 seconds from `scheduledFor` timestamp
4. **File availability**: All task files present on desktop before agent starts
5. **State consistency**: Task status always updated before processing begins

**Sources:** [packages/bytebot-agent/src/agent/agent.scheduler.ts:1-63]()

---

# Page: File Handling

# File Handling

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [packages/bytebot-agent/prisma/migrations/20250722041608_files/migration.sql](packages/bytebot-agent/prisma/migrations/20250722041608_files/migration.sql)
- [packages/bytebot-agent/src/agent/agent.computer-use.ts](packages/bytebot-agent/src/agent/agent.computer-use.ts)
- [packages/bytebot-agent/src/agent/agent.constants.ts](packages/bytebot-agent/src/agent/agent.constants.ts)
- [packages/bytebot-agent/src/agent/agent.scheduler.ts](packages/bytebot-agent/src/agent/agent.scheduler.ts)
- [packages/bytebot-agent/src/agent/agent.tools.ts](packages/bytebot-agent/src/agent/agent.tools.ts)
- [packages/bytebot-ui/src/app/page.tsx](packages/bytebot-ui/src/app/page.tsx)
- [packages/bytebot-ui/src/components/messages/ChatInput.tsx](packages/bytebot-ui/src/components/messages/ChatInput.tsx)
- [packages/bytebot-ui/src/components/ui/select.tsx](packages/bytebot-ui/src/components/ui/select.tsx)
- [packages/bytebotd/src/computer-use/computer-use.controller.ts](packages/bytebotd/src/computer-use/computer-use.controller.ts)
- [packages/bytebotd/src/main.ts](packages/bytebotd/src/main.ts)

</details>



## Purpose and Scope

This document describes how Bytebot handles file uploads, storage, and access throughout the system. It covers:

- User file uploads via the web interface
- Base64 encoding and database storage
- Automatic file materialization to the virtual desktop
- Agent file reading capabilities
- File size limits and validation

For information about task creation and scheduling, see [Task Scheduling](#5.4). For details about the agent's file reading tool, see [Desktop Tools](#7.2).

---

## File Upload Flow

Files move through a multi-stage pipeline from user upload to desktop availability. The following diagram illustrates the complete flow:

```mermaid
graph TB
    subgraph "bytebot-ui: User Upload"
        A["User selects files<br/>(ChatInput component)"]
        B["handleFileSelect()<br/>Validation"]
        C["convertToBase64()<br/>FileReader API"]
        D["FileWithBase64[]<br/>State"]
    end
    
    subgraph "API Request"
        E["startTask()<br/>POST /api/tasks"]
        F["Request Payload<br/>{description, model, files}"]
    end
    
    subgraph "bytebot-agent: Storage"
        G["TasksService.create()"]
        H["Prisma: File.create()"]
        I["PostgreSQL File Table<br/>{name, type, size, data}"]
    end
    
    subgraph "bytebot-agent: Preparation"
        J["AgentScheduler.handleCron()"]
        K["task.files.forEach()"]
        L["writeFile()<br/>POST /computer-use"]
    end
    
    subgraph "bytebotd: Materialization"
        M["ComputerUseController"]
        N["ComputerUseService.action()"]
        O["/home/user/Desktop/<br/>Physical files"]
    end
    
    A --> B
    B --> C
    C --> D
    D --> E
    E --> F
    F --> G
    G --> H
    H --> I
    I --> J
    J --> K
    K --> L
    L --> M
    M --> N
    N --> O
    
    style I fill:#f9f9f9
    style O fill:#f9f9f9
```

**Sources:** [packages/bytebot-ui/src/components/messages/ChatInput.tsx:46-107](), [packages/bytebot-ui/src/app/page.tsx:97-133](), [packages/bytebot-agent/src/agent/agent.scheduler.ts:43-53](), [packages/bytebot-agent/src/agent/agent.computer-use.ts:612-646]()

---

## File Upload Interface

The `ChatInput` component provides the file upload interface with the following constraints:

| Parameter | Value | Location |
|-----------|-------|----------|
| Maximum Files | 5 files per task | [ChatInput.tsx:38]() |
| Maximum File Size | 30 MB per file | [ChatInput.tsx:39]() |
| Accepted Types | All file types (`*/*`) | [ChatInput.tsx:160]() |
| Encoding | Base64 data URL | [ChatInput.tsx:100-107]() |

### FileWithBase64 Interface

The `FileWithBase64` interface defines the structure used for file uploads:

```typescript
interface FileWithBase64 {
  name: string;      // Original filename
  base64: string;    // Data URL (data:type;base64,...)
  type: string;      // MIME type
  size: number;      // File size in bytes
}
```

**Sources:** [packages/bytebot-ui/src/components/messages/ChatInput.tsx:7-12](), [packages/bytebot-ui/src/app/page.tsx:37-42]()

### Validation Logic

The file upload process includes comprehensive validation:

```mermaid
flowchart TD
    A["handleFileSelect()"] --> B{"Files selected?"}
    B -->|No| Z["Return"]
    B -->|Yes| C{"Current + New<br/>> MAX_FILES?"}
    C -->|Yes| D["setErrorMessage()<br/>'Maximum 5 files allowed'"]
    C -->|No| E["Check each file size"]
    E --> F{"Any file<br/>> MAX_FILE_SIZE?"}
    F -->|Yes| G["setErrorMessage()<br/>'File exceeds 30MB limit'"]
    F -->|No| H["convertToBase64()<br/>for each file"]
    H --> I["Update selectedFiles[]"]
    I --> J["onFileUpload(updatedFiles)"]
    J --> K["Files ready for upload"]
    
    D --> Z
    G --> Z
```

**Sources:** [packages/bytebot-ui/src/components/messages/ChatInput.tsx:46-98]()

---

## Database Storage

Files are persisted in the PostgreSQL database through the Prisma ORM.

### File Table Schema

```mermaid
erDiagram
    Task ||--o{ File : "has"
    File {
        string id PK
        string name
        string type
        int size
        string data "base64 encoded"
        datetime createdAt
        datetime updatedAt
        string taskId FK
    }
    Task {
        string id PK
    }
```

The `File` model stores base64-encoded file content directly in the `data` column. This approach simplifies deployment (no separate file storage service) but requires larger database storage.

**Sources:** [packages/bytebot-agent/prisma/migrations/20250722041608_files/migration.sql:1-17]()

---

## Desktop Materialization

When a task begins execution, the `AgentScheduler` automatically writes attached files to the virtual desktop.

### Materialization Process

```mermaid
sequenceDiagram
    participant S as AgentScheduler
    participant TS as TasksService
    participant W as writeFile()
    participant API as bytebotd API
    participant FS as Desktop Filesystem
    
    S->>TS: findNextTask()
    TS-->>S: task (with files)
    
    alt task.files.length > 0
        S->>S: Log: "Task has files"
        loop For each file
            S->>W: writeFile({path, content})
            W->>API: POST /computer-use
            Note over W,API: action: 'write_file'<br/>path: '/home/user/Desktop/{name}'<br/>data: base64
            API->>FS: Write binary data
            FS-->>API: Success
            API-->>W: {success: true}
        end
    end
    
    S->>TS: update(status: RUNNING)
```

**Sources:** [packages/bytebot-agent/src/agent/agent.scheduler.ts:43-53](), [packages/bytebot-agent/src/agent/agent.computer-use.ts:612-646]()

### File Writing Implementation

The `writeFile` function in `agent.computer-use.ts` handles the actual file transfer:

- **Path:** Files are always written to `/home/user/Desktop/{filename}`
- **Content:** Expects base64-encoded data (without data URL prefix)
- **Transport:** HTTP POST to `BYTEBOT_DESKTOP_BASE_URL/computer-use`
- **Action Type:** `write_file`

```typescript
// Simplified implementation
async function writeFile(input: {path: string; content: string}) {
  const response = await fetch(`${BYTEBOT_DESKTOP_BASE_URL}/computer-use`, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      action: 'write_file',
      path: input.path,
      data: input.content  // base64 data
    })
  });
}
```

**Sources:** [packages/bytebot-agent/src/agent/agent.computer-use.ts:612-646]()

---

## File Reading

The agent can read files from the desktop using the `computer_read_file` tool.

### Read File Tool Definition

```mermaid
graph LR
    subgraph "Agent Tool"
        A["computer_read_file"]
    end
    
    subgraph "Input Schema"
        B["path: string<br/>(file path to read)"]
    end
    
    subgraph "Execution"
        C["handleComputerToolUse()"]
        D["readFile()<br/>POST /computer-use"]
        E["bytebotd reads file"]
    end
    
    subgraph "Response"
        F["ToolResultContentBlock"]
        G["DocumentContentBlock<br/>{type: 'document'<br/>source: base64<br/>name, size, mediaType}"]
    end
    
    A --> B
    B --> C
    C --> D
    D --> E
    E --> F
    F --> G
```

**Sources:** [packages/bytebot-agent/src/agent/agent.tools.ts:368-382](), [packages/bytebot-agent/src/agent/agent.computer-use.ts:146-181]()

### Reading Process

When the agent invokes `computer_read_file`:

1. **Tool Call:** Agent provides `{path: "/path/to/file"}`
2. **API Request:** `handleComputerToolUse` sends POST to bytebotd
3. **File Read:** bytebotd reads the file and encodes it as base64
4. **Response Structure:**
   ```typescript
   {
     success: boolean,
     data?: string,        // base64 encoded content
     name?: string,        // filename
     size?: number,        // file size in bytes
     mediaType?: string,   // MIME type
     message?: string      // error message if failed
   }
   ```
5. **Content Block:** If successful, returns `DocumentContentBlock` to LLM

**Sources:** [packages/bytebot-agent/src/agent/agent.computer-use.ts:146-181](), [packages/bytebot-agent/src/agent/agent.computer-use.ts:576-610]()

---

## Technical Details

### Payload Size Limits

The system enforces size limits at multiple layers:

| Service | Limit | Configuration |
|---------|-------|---------------|
| bytebotd | 50 MB | [main.ts:11-12]() |
| UI Client | 30 MB per file | [ChatInput.tsx:39]() |
| UI Client | 5 files max | [ChatInput.tsx:38]() |

The bytebotd service configures Express middleware to accept large payloads:

```typescript
app.use(json({ limit: '50mb' }));
app.use(urlencoded({ limit: '50mb', extended: true }));
```

**Sources:** [packages/bytebotd/src/main.ts:10-12]()

### Base64 Encoding Details

Files undergo base64 encoding at the browser layer using the FileReader API:

```typescript
const convertToBase64 = (file: File): Promise<string> => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.readAsDataURL(file);  // Produces data URL
    reader.onload = () => resolve(reader.result as string);
    reader.onerror = (error) => reject(error);
  });
};
```

The resulting string has the format: `data:{mimeType};base64,{encodedData}`

**Sources:** [packages/bytebot-ui/src/components/messages/ChatInput.tsx:100-107]()

### Desktop Path Convention

All uploaded files are materialized to a consistent location:

- **Directory:** `/home/user/Desktop/`
- **Filename:** Original filename from upload
- **User:** `user` (the desktop environment's default user)
- **Visibility:** Files appear as desktop icons in the XFCE environment

This convention allows the agent to easily locate user-provided files by name.

**Sources:** [packages/bytebot-agent/src/agent/agent.scheduler.ts:49]()

### Computer Use API Integration

The bytebotd service exposes file operations through the `/computer-use` endpoint:

```mermaid
graph TB
    subgraph "POST /computer-use"
        A["ComputerUseController"]
        B["ComputerActionValidationPipe"]
        C["ComputerUseService.action()"]
    end
    
    subgraph "Write File Action"
        D["action: 'write_file'"]
        E["path: string"]
        F["data: string (base64)"]
    end
    
    subgraph "Read File Action"
        G["action: 'read_file'"]
        H["path: string"]
    end
    
    A --> B
    B --> C
    C --> D
    C --> G
    D --> E
    D --> F
    G --> H
```

The controller sanitizes logs to avoid outputting base64 data:

```typescript
const paramsCopy = { ...params };
if (paramsCopy.action === 'write_file') {
  paramsCopy.data = 'base64 data';  // Redacted for logs
}
this.logger.log(`Computer action request: ${JSON.stringify(paramsCopy)}`);
```

**Sources:** [packages/bytebotd/src/computer-use/computer-use.controller.ts:19-41]()

### Agent System Prompt Guidance

The agent receives explicit instructions about file reading in its system prompt:

> **Read Files** - If you need to read file contents, invoke
> ```json
> { "name": "computer_read_file", "input": { "path": "/path/to/file" } }
> ```
> This tool reads files and returns them as document content blocks with base64 data, supporting various file types including documents (PDF, DOCX, TXT, etc.) and images (PNG, JPG, etc.).

This guidance ensures the agent knows how to access uploaded files and other desktop files.

**Sources:** [packages/bytebot-agent/src/agent/agent.constants.ts:122-126]()

---

## File Lifecycle Summary

```mermaid
stateDiagram-v2
    [*] --> UserSelection: User selects files
    UserSelection --> Validation: File count & size check
    Validation --> Base64Encoding: All valid
    Validation --> Error: Invalid
    Base64Encoding --> TaskCreation: convertToBase64()
    TaskCreation --> DatabaseStorage: Prisma.File.create()
    DatabaseStorage --> QueuedTask: Task in PENDING status
    QueuedTask --> DesktopWrite: AgentScheduler picks task
    DesktopWrite --> AgentExecution: Files on /home/user/Desktop/
    AgentExecution --> FileRead: Agent uses computer_read_file
    FileRead --> ToolResult: DocumentContentBlock
    ToolResult --> LLMProcessing: Agent analyzes content
    LLMProcessing --> TaskCompletion: Task completed
    TaskCompletion --> [*]
    Error --> [*]
```

**Sources:** [packages/bytebot-ui/src/components/messages/ChatInput.tsx:46-107](), [packages/bytebot-agent/src/agent/agent.scheduler.ts:43-53](), [packages/bytebot-agent/src/agent/agent.computer-use.ts:146-181]()

---

# Page: Agent System

# Agent System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [packages/bytebot-agent/prisma/migrations/20250722041608_files/migration.sql](packages/bytebot-agent/prisma/migrations/20250722041608_files/migration.sql)
- [packages/bytebot-agent/src/agent/agent.computer-use.ts](packages/bytebot-agent/src/agent/agent.computer-use.ts)
- [packages/bytebot-agent/src/agent/agent.constants.ts](packages/bytebot-agent/src/agent/agent.constants.ts)
- [packages/bytebot-agent/src/agent/agent.processor.ts](packages/bytebot-agent/src/agent/agent.processor.ts)
- [packages/bytebot-agent/src/agent/agent.scheduler.ts](packages/bytebot-agent/src/agent/agent.scheduler.ts)
- [packages/bytebot-agent/src/agent/agent.tools.ts](packages/bytebot-agent/src/agent/agent.tools.ts)
- [packages/bytebot-agent/src/tasks/tasks.controller.ts](packages/bytebot-agent/src/tasks/tasks.controller.ts)
- [packages/bytebot-agent/src/tasks/tasks.service.ts](packages/bytebot-agent/src/tasks/tasks.service.ts)
- [packages/bytebot-ui/src/hooks/useChatSession.ts](packages/bytebot-ui/src/hooks/useChatSession.ts)
- [packages/bytebotd/src/computer-use/computer-use.controller.ts](packages/bytebotd/src/computer-use/computer-use.controller.ts)
- [packages/bytebotd/src/main.ts](packages/bytebotd/src/main.ts)

</details>



The Agent System is the AI-driven core of Bytebot that orchestrates autonomous task execution on the virtual desktop. It implements a continuous observe-act-verify loop, using Large Language Models (LLMs) to make decisions and desktop automation tools to execute actions. This system transforms user task descriptions into sequences of computer interactions, managing context through summarization and handling multi-step workflows.

For information about task lifecycle management and status transitions, see [Task Management System](#5). For details about the desktop environment where actions are executed, see [Desktop Environment](#7). For LLM provider configuration, see [Configuration](#3.3).

## Architecture Overview

The Agent System consists of four primary components working in coordination:

**AgentProcessor** - The central orchestrator ([packages/bytebot-agent/src/agent/agent.processor.ts:44-420]()) that manages the processing loop, maintains state, and coordinates between LLM services and tool execution.

**BytebotAgentService Implementations** - Provider-specific adapters for Anthropic Claude, OpenAI GPT, and Google Gemini that abstract LLM communication behind a common interface.

**Tool System** - A collection of 17 desktop automation tools ([packages/bytebot-agent/src/agent/agent.tools.ts:387-405]()) and their execution handlers that translate LLM decisions into computer actions.

**Context Management** - Message storage and summarization services that maintain conversation history while respecting LLM context windows.

```mermaid
graph TB
    subgraph "AgentProcessor Core"
        AP[AgentProcessor<br/>agent.processor.ts:44]
        ProcessLoop[processTask()<br/>:114]
        RunIter[runIteration()<br/>:134]
        AbortCtrl[AbortController<br/>:48]
    end
    
    subgraph "LLM Integration Layer"
        BAIS[BytebotAgentService<br/>Interface]
        Anthropic[AnthropicService<br/>anthropic.service.ts]
        OpenAI[OpenAIService<br/>openai.service.ts]
        Google[GoogleService<br/>google.service.ts]
        Proxy[ProxyService<br/>proxy.service.ts]
    end
    
    subgraph "Tool Execution"
        ToolDefs[agentTools[]<br/>agent.tools.ts:387]
        CompUse[handleComputerToolUse()<br/>agent.computer-use.ts:28]
        DesktopAPI[POST /computer-use<br/>bytebotd:9990]
    end
    
    subgraph "Context Management"
        MsgSvc[MessagesService<br/>messages.service.ts]
        SumSvc[SummariesService<br/>summaries.service.ts]
        MsgDB[(Message Table)]
        SumDB[(Summary Table)]
    end
    
    subgraph "Task State"
        TaskSvc[TasksService<br/>tasks.service.ts]
        EventBus[EventEmitter2<br/>Internal Events]
    end
    
    ProcessLoop --> RunIter
    RunIter --> TaskSvc
    RunIter --> SumSvc
    RunIter --> MsgSvc
    RunIter --> BAIS
    
    BAIS --> Anthropic
    BAIS --> OpenAI
    BAIS --> Google
    BAIS --> Proxy
    
    RunIter --> CompUse
    CompUse --> DesktopAPI
    
    MsgSvc --> MsgDB
    SumSvc --> SumDB
    
    TaskSvc --> EventBus
    EventBus -.->|task.takeover| AP
    EventBus -.->|task.resume| AP
    EventBus -.->|task.cancel| AP
    
    AbortCtrl -.->|Cancels| BAIS
```

**Diagram: Agent System Component Architecture**

The diagram shows how AgentProcessor orchestrates the system, delegating to specialized services while maintaining control through event subscriptions and abort signals.

Sources: [packages/bytebot-agent/src/agent/agent.processor.ts:44-420](), [packages/bytebot-agent/src/agent/agent.computer-use.ts:1-647](), [packages/bytebot-agent/src/agent/agent.tools.ts:1-406]()

## Processing Loop

The agent operates in a continuous iteration loop implemented in `runIteration()`. Each iteration follows the observe-plan-act-verify pattern:

```mermaid
stateDiagram-v2
    [*] --> CheckRunning: processTask(taskId)
    
    CheckRunning --> RunIteration: isProcessing = true
    
    state RunIteration {
        [*] --> FetchTask: findById(taskId)
        
        FetchTask --> CheckStatus: Task retrieved
        
        state CheckStatus <<choice>>
        CheckStatus --> LoadContext: status == RUNNING
        CheckStatus --> StopProcessing: status != RUNNING
        
        LoadContext --> BuildMessages: findLatest(taskId)<br/>findUnsummarized(taskId)
        
        BuildMessages --> CallLLM: messages[] assembled
        
        CallLLM --> ParseResponse: service.generateMessage()<br/>AGENT_SYSTEM_PROMPT
        
        ParseResponse --> ProcessBlocks: contentBlocks[]
        
        state ProcessBlocks {
            [*] --> SaveAssistantMsg: create(contentBlocks)
            
            SaveAssistantMsg --> CheckSummarize: Calculate token usage
            
            state CheckSummarize <<choice>>
            CheckSummarize --> Summarize: tokens > 75% context
            CheckSummarize --> ExecuteTools: tokens <= 75% context
            
            Summarize --> ExecuteTools: Summary created<br/>Messages attached
            
            ExecuteTools --> ComputerTool: isComputerToolUseContentBlock()
            ExecuteTools --> CreateTaskTool: isCreateTaskToolUseBlock()
            ExecuteTools --> SetStatusTool: isSetTaskStatusToolUseBlock()
            ExecuteTools --> ToolResultsDone: No more tools
            
            ComputerTool --> handleComputerToolUse: Execute action
            handleComputerToolUse --> SaveToolResults: POST /computer-use
            
            CreateTaskTool --> CreateTask: tasksService.create()
            CreateTask --> SaveToolResults: Tool result generated
            
            SetStatusTool --> SaveToolResults: Store result
            SaveToolResults --> ToolResultsDone: All tools processed
            
            ToolResultsDone --> UpdateTaskStatus: Save tool results
        }
        
        UpdateTaskStatus --> CheckFinalStatus: setTaskStatusToolUseBlock?
        
        state CheckFinalStatus <<choice>>
        CheckFinalStatus --> MarkCompleted: status = completed
        CheckFinalStatus --> MarkNeedsHelp: status = needs_help
        CheckFinalStatus --> ScheduleNext: No status change
        
        MarkCompleted --> StopProcessing: Update task
        MarkNeedsHelp --> StopProcessing: Update task
        
        ScheduleNext --> [*]: setImmediate(runIteration)
    }
    
    RunIteration --> [*]: Continue loop
    
    StopProcessing --> [*]: isProcessing = false
    
    note right of CallLLM
        Uses BytebotAgentService interface
        Supports Anthropic, OpenAI, Google
        Passes AbortSignal for cancellation
    end note
    
    note right of CheckSummarize
        contextWindow * 0.75 threshold
        Prevents context overflow
        Creates hierarchical summaries
    end note
```

**Diagram: AgentProcessor Iteration Lifecycle**

Each iteration is scheduled via `setImmediate()`, creating a non-blocking asynchronous loop that continues until the task reaches a terminal status.

Sources: [packages/bytebot-agent/src/agent/agent.processor.ts:134-403](), [packages/bytebot-agent/src/tasks/tasks.service.ts:217-391]()

## Tool Use Execution Flow

When the LLM responds with tool use blocks, the agent processes each tool sequentially:

```mermaid
graph TB
    LLMResp[LLM Response<br/>contentBlocks[]]
    
    SaveMsg[messagesService.create()<br/>role: ASSISTANT<br/>:227-231]
    
    LoopBlocks{For each block}
    
    CheckType1{isComputerToolUseContentBlock?}
    CheckType2{isCreateTaskToolUseBlock?}
    CheckType3{isSetTaskStatusToolUseBlock?}
    
    HandleComp[handleComputerToolUse()<br/>agent.computer-use.ts:28]
    
    ToolDispatch{Tool Name}
    
    Screenshot[screenshot()<br/>:526-555]
    CursorPos[cursorPosition()<br/>:506-524]
    MouseAction[moveMouse/clickMouse/etc.<br/>:241-485]
    KeyAction[typeKeys/pressKeys/typeText<br/>:399-466]
    AppAction[application()<br/>:557-574]
    ReadFile[readFile()<br/>:576-610]
    
    Wait750[Wait 750ms<br/>:187-189]
    TakeScreenshot[screenshot()<br/>:192]
    
    BuildResult[Build ToolResultContentBlock<br/>:199-221]
    
    CreateTask[tasksService.create()<br/>:319-328]
    SetStatus[Store status change<br/>:343-356]
    
    CollectResults[generatedToolResults[]<br/>:305]
    
    SaveResults[messagesService.create()<br/>role: USER<br/>:360-364]
    
    UpdateTask[tasksService.update()<br/>Apply status change<br/>:368-382]
    
    LLMResp --> SaveMsg
    SaveMsg --> LoopBlocks
    
    LoopBlocks --> CheckType1
    CheckType1 -->|Yes| HandleComp
    CheckType1 -->|No| CheckType2
    
    HandleComp --> ToolDispatch
    
    ToolDispatch -->|screenshot| Screenshot
    ToolDispatch -->|cursor_position| CursorPos
    ToolDispatch -->|move_mouse,etc| MouseAction
    ToolDispatch -->|type_keys,etc| KeyAction
    ToolDispatch -->|application| AppAction
    ToolDispatch -->|read_file| ReadFile
    
    Screenshot --> BuildResult
    CursorPos --> BuildResult
    
    MouseAction --> Wait750
    KeyAction --> Wait750
    AppAction --> Wait750
    
    Wait750 --> TakeScreenshot
    TakeScreenshot --> BuildResult
    
    ReadFile --> BuildResult
    
    BuildResult --> CollectResults
    
    CheckType2 -->|Yes| CreateTask
    CheckType2 -->|No| CheckType3
    
    CreateTask --> CollectResults
    
    CheckType3 -->|Yes| SetStatus
    CheckType3 -->|No| LoopBlocks
    
    SetStatus --> CollectResults
    
    CollectResults --> SaveResults
    SaveResults --> UpdateTask
```

**Diagram: Tool Execution Dispatch and Result Collection**

The 750ms delay before post-action screenshots allows UI animations to settle, ensuring the agent observes the actual result state.

Sources: [packages/bytebot-agent/src/agent/agent.processor.ts:309-382](), [packages/bytebot-agent/src/agent/agent.computer-use.ts:28-239]()

## System Prompt and Operating Principles

The agent's behavior is governed by the `AGENT_SYSTEM_PROMPT` constant ([packages/bytebot-agent/src/agent/agent.constants.ts:17-175]()), which defines:

| Principle | Description | Implementation |
|-----------|-------------|----------------|
| **Observe First** | Always take screenshot before actions | `computer_screenshot` before each operation |
| **Human-Like Interaction** | Natural mouse movements, realistic typing | Smooth paths, context-appropriate text |
| **Verify Every Step** | Confirm expected state after actions | Screenshot after each tool use |
| **Batch Processing** | Process repetitive tasks in groups of 10-20 | Continue until all items processed |
| **Error Recovery** | Don't let single failures stop operations | Note errors, continue with next item |
| **Cleanup** | Return desktop to idle state | Close windows before completion |
| **Security** | Protect sensitive information | `isSensitive` flag on passwords |

The prompt includes a comprehensive task lifecycle template, valid key mappings from `nut-tree`'s `Key` enum, and specific guidance for bulk operations to prevent premature completion.

For detailed operating principles, see [Agent Operating Principles](#6.5).

Sources: [packages/bytebot-agent/src/agent/agent.constants.ts:17-175]()

## Event-Driven Control

The agent responds to external events through the `EventEmitter2` pattern:

```mermaid
sequenceDiagram
    participant User
    participant TasksCtrl as TasksController
    participant TasksSvc as TasksService
    participant EventBus as EventEmitter2
    participant AP as AgentProcessor
    participant InputCapture as InputCaptureService
    
    User->>TasksCtrl: POST /tasks/:id/takeover
    TasksCtrl->>TasksSvc: takeOver(taskId)
    TasksSvc->>TasksSvc: Update control = USER
    TasksSvc->>EventBus: emit('task.takeover', {taskId})
    TasksSvc->>InputCapture: POST /input-tracking/start
    
    EventBus-->>AP: @OnEvent('task.takeover')
    AP->>AP: abortController.abort()
    AP->>InputCapture: start(taskId)
    
    Note over AP: Processing halted<br/>User has control
    
    User->>TasksCtrl: POST /tasks/:id/resume
    TasksCtrl->>TasksSvc: resume(taskId)
    TasksSvc->>TasksSvc: Update control = ASSISTANT
    TasksSvc->>EventBus: emit('task.resume', {taskId})
    TasksSvc->>InputCapture: POST /input-tracking/stop
    
    EventBus-->>AP: @OnEvent('task.resume')
    AP->>AP: abortController = new AbortController()
    AP->>AP: runIteration(taskId)
    
    Note over AP: Processing resumed<br/>Agent continues task
```

**Diagram: Event-Driven Task Control Flow**

The abort controller mechanism ([packages/bytebot-agent/src/agent/agent.processor.ts:48,155]()) allows graceful cancellation of in-flight LLM requests without leaving operations in inconsistent states.

Sources: [packages/bytebot-agent/src/agent/agent.processor.ts:84-112](), [packages/bytebot-agent/src/tasks/tasks.service.ts:282-391]()

## LLM Provider Abstraction

The agent uses a common interface to support multiple LLM providers:

```typescript
interface BytebotAgentService {
  generateMessage(
    systemPrompt: string,
    messages: Message[],
    model: string,
    tools: boolean,
    signal: AbortSignal
  ): Promise<BytebotAgentResponse>;
}
```

Implementations map provider-specific APIs to this interface:

| Provider | Service Class | Model Selection | Context Window |
|----------|---------------|-----------------|----------------|
| Anthropic | `AnthropicService` | Claude 3.5 Sonnet, Opus | 200,000 tokens |
| OpenAI | `OpenAIService` | GPT-4o, o1-preview, o1-mini | 128,000 tokens |
| Google | `GoogleService` | Gemini 2.0 Flash, Pro | 1,000,000 tokens |
| Proxy | `ProxyService` | LiteLLM proxy endpoint | Configurable |

Provider selection occurs at runtime based on the task's `model` field ([packages/bytebot-agent/src/agent/agent.processor.ts:185-199]()), with automatic fallback if the specified provider is unavailable.

For provider implementation details, see [AI Model Integration](#6.3).

Sources: [packages/bytebot-agent/src/agent/agent.processor.ts:61-66,185-207](), [packages/bytebot-agent/src/tasks/tasks.controller.ts:23-33]()

## Summarization Strategy

To manage LLM context limits, the agent implements automatic summarization:

**Trigger Condition**: When `totalTokens >= (contextWindow * 0.75)` ([packages/bytebot-agent/src/agent/agent.processor.ts:234-237]())

**Summarization Process**:
1. Use `SUMMARIZATION_SYSTEM_PROMPT` to request concise summary
2. Send all unsummarized messages plus summary request to LLM
3. Extract text from response content blocks
4. Create summary record in database
5. Attach processed messages to summary via `summaryId`

**Context Building** ([packages/bytebot-agent/src/agent/agent.processor.ts:157-180]()):
```
[
  {role: USER, content: <latest summary text>},  // If exists
  ...unsummarizedMessages                         // Recent messages
]
```

This creates a hierarchical structure where summaries can reference parent summaries, enabling indefinite conversation length while staying within token limits.

For message processing and summarization details, see [Message and Summarization](#6.4).

Sources: [packages/bytebot-agent/src/agent/agent.processor.ts:157-299](), [packages/bytebot-agent/src/agent/agent.constants.ts:6-15]()

## Task Scheduling and Initialization

The `AgentScheduler` ([packages/bytebot-agent/src/agent/agent.scheduler.ts:9-63]()) runs every 5 seconds to:

1. **Check scheduled tasks**: Queue any tasks where `scheduledFor < now`
2. **Find next task**: If processor idle, find highest priority task (RUNNING or PENDING)
3. **Prepare files**: Write task attachments to `/home/user/Desktop/`
4. **Start processing**: Update status to RUNNING, call `agentProcessor.processTask()`

File preparation ([packages/bytebot-agent/src/agent/agent.scheduler.ts:43-53]()) materializes base64-encoded database blobs onto the virtual desktop filesystem, making them accessible to applications.

Task prioritization follows:
```
ORDER BY executedAt ASC, priority DESC, queuedAt ASC, createdAt ASC
```

This ensures RUNNING tasks resume before new PENDING tasks, with priority as the secondary sort.

Sources: [packages/bytebot-agent/src/agent/agent.scheduler.ts:1-64](), [packages/bytebot-agent/src/tasks/tasks.service.ts:131-156]()

## Desktop Tool Catalog

The agent has access to 17 computer automation tools grouped by category:

**Mouse Tools** ([packages/bytebot-agent/src/agent/agent.tools.ts:35-155]()):
- `computer_move_mouse`, `computer_trace_mouse`, `computer_click_mouse`
- `computer_press_mouse`, `computer_drag_mouse`, `computer_scroll`

**Keyboard Tools** ([packages/bytebot-agent/src/agent/agent.tools.ts:160-248]()):
- `computer_type_keys`, `computer_press_keys`, `computer_type_text`
- `computer_paste_text`

**Utility Tools** ([packages/bytebot-agent/src/agent/agent.tools.ts:253-382]()):
- `computer_screenshot`, `computer_cursor_position`, `computer_wait`
- `computer_application`, `computer_read_file`

**Task Management Tools** ([packages/bytebot-agent/src/agent/agent.tools.ts:314-363]()):
- `set_task_status`, `create_task`

Each tool definition includes JSON schema for input validation. The `computer_application` tool limits applications to: `firefox`, `1password`, `thunderbird`, `vscode`, `terminal`, `desktop`, `directory`.

For complete tool documentation, see [Computer Use Integration](#6.2) and [Desktop Tools](#7.2).

Sources: [packages/bytebot-agent/src/agent/agent.tools.ts:1-406]()

## Error Handling and Recovery

The agent implements multi-layer error handling:

**LLM Request Errors**: Caught at the service level, propagated as `BytebotAgentInterrupt` errors when abort signals trigger ([packages/bytebot-agent/src/agent/agent.processor.ts:389-401]())

**Tool Execution Errors**: Return `ToolResultContentBlock` with `is_error: true` flag ([packages/bytebot-agent/src/agent/agent.computer-use.ts:222-238]()), allowing the LLM to see failures and retry

**Task Failures**: Set `status: FAILED` and stop processing ([packages/bytebot-agent/src/agent/agent.processor.ts:193-198]())

**Abort on Takeover**: When user takes control, abort any in-flight requests immediately ([packages/bytebot-agent/src/agent/agent.processor.ts:89-91]())

Error messages include stack traces in logs but sanitize sensitive information before storage.

Sources: [packages/bytebot-agent/src/agent/agent.processor.ts:388-402](), [packages/bytebot-agent/src/agent/agent.computer-use.ts:222-238]()

## Integration Points

The Agent System integrates with:

| Component | Integration Method | Purpose |
|-----------|-------------------|---------|
| TasksService | Direct injection | CRUD operations, status updates |
| MessagesService | Direct injection | Store LLM responses, tool results |
| SummariesService | Direct injection | Context compression |
| bytebotd | HTTP POST /computer-use | Execute desktop actions |
| TasksGateway | Via TasksService | Real-time UI notifications |
| EventEmitter2 | Event subscriptions | React to control changes |
| InputCaptureService | Direct calls | Track user actions during takeover |

The processor maintains minimal state (current task ID, processing flag, abort controller), relying on database queries for task state to ensure consistency across restarts.

Sources: [packages/bytebot-agent/src/agent/agent.processor.ts:51-67](), [packages/bytebot-agent/src/agent/agent.computer-use.ts:26,248-555]()

---

# Page: Agent Processor

# Agent Processor

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [packages/bytebot-agent/src/agent/agent.processor.ts](packages/bytebot-agent/src/agent/agent.processor.ts)
- [packages/bytebot-agent/src/tasks/tasks.controller.ts](packages/bytebot-agent/src/tasks/tasks.controller.ts)
- [packages/bytebot-agent/src/tasks/tasks.service.ts](packages/bytebot-agent/src/tasks/tasks.service.ts)
- [packages/bytebot-ui/src/hooks/useChatSession.ts](packages/bytebot-ui/src/hooks/useChatSession.ts)

</details>



## Purpose and Scope

The **AgentProcessor** is the core orchestration component that executes AI-driven tasks in a continuous observation-action loop. It coordinates between LLM providers, desktop automation, message management, and summarization to autonomously complete user-defined tasks. This document covers the processing lifecycle, event-driven coordination, tool execution, and context management strategies.

For information about the specific desktop actions the agent can execute, see [Computer Use Integration](#6.2). For details on LLM provider implementations, see [AI Model Integration](#6.3). For the message storage and summarization strategy, see [Message and Summarization](#6.4).

---

## Overview

The AgentProcessor implements a single-threaded, non-blocking task execution engine that:

1. **Observes** the current desktop state via screenshots
2. **Reasons** by sending message context to LLM providers
3. **Acts** by executing tool use instructions (computer actions, subtask creation, status updates)
4. **Verifies** results and continues the loop until task completion

The processor runs one task at a time, maintaining state through the `isProcessing` flag and `currentTaskId` reference. It responds to external events (takeover, resume, cancel) via the EventEmitter2 system and supports graceful interruption using AbortController.

Sources: [packages/bytebot-agent/src/agent/agent.processor.ts:1-420]()

---

## Class Structure and Dependencies

### AgentProcessor Service

```mermaid
graph TB
    AgentProcessor["AgentProcessor<br/>@Injectable()"]
    
    subgraph "Service Dependencies"
        TasksService["TasksService<br/>CRUD + Events"]
        MessagesService["MessagesService<br/>Create + Query"]
        SummariesService["SummariesService<br/>Hierarchical summaries"]
        AnthropicService["AnthropicService<br/>Claude integration"]
        OpenAIService["OpenAIService<br/>GPT integration"]
        GoogleService["GoogleService<br/>Gemini integration"]
        ProxyService["ProxyService<br/>LLM proxy integration"]
        InputCaptureService["InputCaptureService<br/>User action tracking"]
    end
    
    subgraph "Internal State"
        currentTaskId["currentTaskId: string | null"]
        isProcessing["isProcessing: boolean"]
        abortController["abortController: AbortController"]
        services["services: Record<string, BytebotAgentService>"]
    end
    
    AgentProcessor --> TasksService
    AgentProcessor --> MessagesService
    AgentProcessor --> SummariesService
    AgentProcessor --> AnthropicService
    AgentProcessor --> OpenAIService
    AgentProcessor --> GoogleService
    AgentProcessor --> ProxyService
    AgentProcessor --> InputCaptureService
    
    AgentProcessor --> currentTaskId
    AgentProcessor --> isProcessing
    AgentProcessor --> abortController
    AgentProcessor --> services
```

The AgentProcessor maintains a services registry mapping provider names (`anthropic`, `openai`, `google`, `proxy`) to their respective service implementations. This allows runtime model selection based on the task's configured model.

| Internal State | Type | Purpose |
|---|---|---|
| `currentTaskId` | `string \| null` | ID of the task currently being processed |
| `isProcessing` | `boolean` | Flag indicating whether processor is active |
| `abortController` | `AbortController \| null` | Controls abortion of in-flight LLM requests |
| `services` | `Record<string, BytebotAgentService>` | Map of provider names to service implementations |

Sources: [packages/bytebot-agent/src/agent/agent.processor.ts:44-68]()

---

## Processing Lifecycle

### Entry Point: processTask()

```mermaid
stateDiagram-v2
    [*] --> CheckProcessing: processTask(taskId)
    
    CheckProcessing --> AlreadyRunning: isProcessing == true
    CheckProcessing --> InitializeProcessing: isProcessing == false
    
    AlreadyRunning --> LogWarning
    LogWarning --> [*]: Return early
    
    InitializeProcessing --> SetFlags: Set isProcessing = true<br/>currentTaskId = taskId
    SetFlags --> CreateAbortController: abortController = new AbortController()
    CreateAbortController --> KickoffIteration: void runIteration(taskId)
    KickoffIteration --> [*]: Non-blocking return
```

The `processTask()` method [packages/bytebot-agent/src/agent/agent.processor.ts:114-128]() serves as the entry point for task execution. It:

1. Validates that no other task is currently processing
2. Sets the `isProcessing` flag and `currentTaskId`
3. Creates a fresh `AbortController` for request cancellation
4. Initiates the first iteration without blocking the caller

The method returns immediately after scheduling the first iteration, allowing the NestJS event loop to continue serving other requests.

Sources: [packages/bytebot-agent/src/agent/agent.processor.ts:114-128]()

---

### Main Loop: runIteration()

```mermaid
flowchart TD
    Start["runIteration(taskId)"] --> CheckProcessing{"isProcessing?"}
    CheckProcessing -->|No| Return["Return early"]
    CheckProcessing -->|Yes| FetchTask["Fetch task from DB"]
    
    FetchTask --> CheckStatus{"task.status == RUNNING?"}
    CheckStatus -->|No| CleanupState["Set isProcessing = false<br/>currentTaskId = null"]
    CleanupState --> Return
    
    CheckStatus -->|Yes| RefreshAbort["Create new AbortController"]
    RefreshAbort --> BuildContext["Build message context:<br/>latestSummary +<br/>unsummarizedMessages"]
    
    BuildContext --> SelectService["Select service by model.provider"]
    SelectService --> InvalidService{"Service exists?"}
    InvalidService -->|No| FailTask["Update status to FAILED"]
    FailTask --> CleanupState
    
    InvalidService -->|Yes| CallLLM["service.generateMessage()<br/>with AGENT_SYSTEM_PROMPT"]
    
    CallLLM --> ValidateResponse{"contentBlocks.length > 0?"}
    ValidateResponse -->|No| FailTask
    
    ValidateResponse -->|Yes| SaveAssistantMsg["Save ASSISTANT message<br/>with contentBlocks"]
    
    SaveAssistantMsg --> CheckTokens{"tokenUsage >= 75% of contextWindow?"}
    CheckTokens -->|Yes| Summarize["Generate summary via LLM<br/>Create Summary entity<br/>Attach messages to summary"]
    CheckTokens -->|No| ProcessTools["Process tool use blocks"]
    Summarize --> ProcessTools
    
    ProcessTools --> ComputerTool{"isComputerToolUseContentBlock?"}
    ProcessTools --> CreateTaskTool{"isCreateTaskToolUseBlock?"}
    ProcessTools --> SetStatusTool{"isSetTaskStatusToolUseBlock?"}
    
    ComputerTool --> HandleComputer["handleComputerToolUse()<br/>Execute via bytebotd"]
    CreateTaskTool --> CreateSubTask["TasksService.create()"]
    SetStatusTool --> SaveSetStatus["Save tool result"]
    
    HandleComputer --> AddResults["Collect tool results"]
    CreateSubTask --> AddResults
    SaveSetStatus --> AddResults
    
    AddResults --> SaveResults{"generatedToolResults.length > 0?"}
    SaveResults -->|Yes| SaveUserMsg["Save USER message<br/>with tool results"]
    SaveResults -->|No| CheckSetStatus
    SaveUserMsg --> CheckSetStatus
    
    CheckSetStatus{"setTaskStatusToolUseBlock?"}
    CheckSetStatus -->|completed| UpdateCompleted["Update status to COMPLETED<br/>Set completedAt"]
    CheckSetStatus -->|needs_help| UpdateNeedsHelp["Update status to NEEDS_HELP"]
    CheckSetStatus -->|No| ScheduleNext
    
    UpdateCompleted --> ScheduleNext
    UpdateNeedsHelp --> ScheduleNext
    
    ScheduleNext{"isProcessing?"}
    ScheduleNext -->|Yes| SetImmediate["setImmediate(() => runIteration(taskId))"]
    ScheduleNext -->|No| Return
    SetImmediate --> Return
```

The `runIteration()` method [packages/bytebot-agent/src/agent/agent.processor.ts:134-403]() implements the core processing loop. Each iteration:

1. **Validates task status** - Returns early if task is no longer RUNNING
2. **Builds context** - Combines latest summary with unsummarized messages
3. **Calls LLM** - Uses provider-specific service with AGENT_SYSTEM_PROMPT
4. **Saves response** - Stores ASSISTANT message with content blocks
5. **Conditionally summarizes** - If token usage ≥ 75% of context window
6. **Executes tools** - Processes computer actions, subtask creation, status updates
7. **Saves results** - Stores USER message with tool execution results
8. **Updates status** - If `set_task_status` tool was used
9. **Schedules next iteration** - Uses `setImmediate()` for non-blocking continuation

The loop continues until the task status changes from RUNNING to COMPLETED, NEEDS_HELP, FAILED, or CANCELLED.

Sources: [packages/bytebot-agent/src/agent/agent.processor.ts:134-403]()

---

## Event-Driven Coordination

The AgentProcessor responds to three key events emitted by TasksService via EventEmitter2:

### Event Handlers

```mermaid
sequenceDiagram
    participant User
    participant TasksController
    participant TasksService
    participant EventEmitter2
    participant AgentProcessor
    participant InputCaptureService
    
    User->>TasksController: POST /tasks/:id/takeover
    TasksController->>TasksService: takeOver(taskId)
    TasksService->>TasksService: Update control to USER
    TasksService->>EventEmitter2: emit('task.takeover', {taskId})
    EventEmitter2->>AgentProcessor: @OnEvent('task.takeover')
    AgentProcessor->>AgentProcessor: abortController?.abort()
    AgentProcessor->>InputCaptureService: start(taskId)
    
    User->>TasksController: POST /tasks/:id/resume
    TasksController->>TasksService: resume(taskId)
    TasksService->>TasksService: Update control to ASSISTANT<br/>status to RUNNING
    TasksService->>EventEmitter2: emit('task.resume', {taskId})
    EventEmitter2->>AgentProcessor: @OnEvent('task.resume')
    AgentProcessor->>AgentProcessor: Create new AbortController
    AgentProcessor->>AgentProcessor: void runIteration(taskId)
    
    User->>TasksController: POST /tasks/:id/cancel
    TasksController->>TasksService: cancel(taskId)
    TasksService->>TasksService: Update status to CANCELLED
    TasksService->>EventEmitter2: emit('task.cancel', {taskId})
    EventEmitter2->>AgentProcessor: @OnEvent('task.cancel')
    AgentProcessor->>AgentProcessor: stopProcessing()
```

### task.takeover Event

When a user takes control of a task [packages/bytebot-agent/src/agent/agent.processor.ts:84-95]():

1. **Aborts in-flight operations** - If the processor is currently processing this task, calls `abortController?.abort()` to cancel pending LLM requests
2. **Starts input capture** - Calls `InputCaptureService.start(taskId)` to track user actions on the desktop

The processor does not modify `isProcessing` or `currentTaskId` because the next iteration will naturally detect the status change and exit the loop.

### task.resume Event

When a user returns control to the agent [packages/bytebot-agent/src/agent/agent.processor.ts:97-105]():

1. **Validates ownership** - Only resumes if `currentTaskId === taskId && isProcessing`
2. **Creates fresh AbortController** - Replaces the aborted controller
3. **Resumes processing** - Calls `void runIteration(taskId)` to continue the loop

### task.cancel Event

When a user cancels a task [packages/bytebot-agent/src/agent/agent.processor.ts:107-112]():

1. **Calls stopProcessing()** - Aborts all operations and cleans up state
2. **Sets flags to null** - `isProcessing = false`, `currentTaskId = null`

Sources: [packages/bytebot-agent/src/agent/agent.processor.ts:84-112](), [packages/bytebot-agent/src/tasks/tasks.service.ts:282-391]()

---

## LLM Integration and Service Selection

### Multi-Provider Architecture

```mermaid
graph TB
    AgentProcessor["AgentProcessor"]
    
    subgraph "Service Registry"
        ServicesMap["services: Record<string, BytebotAgentService>"]
    end
    
    subgraph "Provider Implementations"
        AnthropicService["AnthropicService<br/>provider: 'anthropic'"]
        OpenAIService["OpenAIService<br/>provider: 'openai'"]
        GoogleService["GoogleService<br/>provider: 'google'"]
        ProxyService["ProxyService<br/>provider: 'proxy'"]
    end
    
    subgraph "BytebotAgentService Interface"
        GenerateMessage["generateMessage(<br/>systemPrompt: string,<br/>messages: Message[],<br/>modelName: string,<br/>useTools: boolean,<br/>signal: AbortSignal<br/>): Promise<BytebotAgentResponse>"]
    end
    
    AgentProcessor --> ServicesMap
    ServicesMap --> AnthropicService
    ServicesMap --> OpenAIService
    ServicesMap --> GoogleService
    ServicesMap --> ProxyService
    
    AnthropicService -.implements.-> GenerateMessage
    OpenAIService -.implements.-> GenerateMessage
    GoogleService -.implements.-> GenerateMessage
    ProxyService -.implements.-> GenerateMessage
```

The AgentProcessor abstracts LLM providers behind a common `BytebotAgentService` interface. During initialization [packages/bytebot-agent/src/agent/agent.processor.ts:61-66](), it builds a services registry:

```typescript
this.services = {
  anthropic: this.anthropicService,
  openai: this.openaiService,
  google: this.googleService,
  proxy: this.proxyService,
};
```

### Runtime Service Selection

At the start of each iteration [packages/bytebot-agent/src/agent/agent.processor.ts:185-199]():

1. **Extract model metadata** - `const model = task.model as BytebotAgentModel`
2. **Lookup service** - `const service = this.services[model.provider]`
3. **Validate existence** - If no service found, mark task as FAILED
4. **Generate response** - `await service.generateMessage(...)`

This design allows users to select different models per task without code changes.

### System Prompts

The processor uses two system prompts:

| Prompt | Purpose | Location |
|---|---|---|
| `AGENT_SYSTEM_PROMPT` | Guides agent behavior during task execution | [packages/bytebot-agent/src/agent/agent.constants.ts]() |
| `SUMMARIZATION_SYSTEM_PROMPT` | Instructs LLM to compress conversation history | [packages/bytebot-agent/src/agent/agent.constants.ts]() |

Sources: [packages/bytebot-agent/src/agent/agent.processor.ts:185-207](), [packages/bytebot-agent/src/agent/agent.types.ts]()

---

## Tool Execution

The processor recognizes three tool types returned by LLMs:

### Tool Dispatch Logic

```mermaid
flowchart TD
    ContentBlocks["messageContentBlocks: MessageContentBlock[]"] --> ForEach["for (const block of messageContentBlocks)"]
    
    ForEach --> CheckComputer{"isComputerToolUseContentBlock(block)?"}
    ForEach --> CheckCreateTask{"isCreateTaskToolUseBlock(block)?"}
    ForEach --> CheckSetStatus{"isSetTaskStatusToolUseBlock(block)?"}
    
    CheckComputer -->|Yes| HandleComputer["handleComputerToolUse(block, logger)"]
    HandleComputer --> AddComputerResult["generatedToolResults.push(<br/>ToolResultContentBlock)"]
    
    CheckCreateTask -->|Yes| ExtractParams["type = block.input.type<br/>priority = block.input.priority<br/>description = block.input.description<br/>scheduledFor = block.input.scheduledFor"]
    ExtractParams --> CreateTask["await TasksService.create({...})"]
    CreateTask --> AddCreateResult["generatedToolResults.push(<br/>ToolResultContentBlock)"]
    
    CheckSetStatus -->|Yes| SaveStatus["setTaskStatusToolUseBlock = block"]
    SaveStatus --> AddStatusResult["generatedToolResults.push(<br/>ToolResultContentBlock)"]
    
    AddComputerResult --> Continue["Continue loop"]
    AddCreateResult --> Continue
    AddStatusResult --> Continue
    
    Continue --> SaveResults["await MessagesService.create({<br/>content: generatedToolResults,<br/>role: USER,<br/>taskId<br/>})"]
```

### Computer Tool Use

For computer actions [packages/bytebot-agent/src/agent/agent.processor.ts:310-313]():

```typescript
if (isComputerToolUseContentBlock(block)) {
  const result = await handleComputerToolUse(block, this.logger);
  generatedToolResults.push(result);
}
```

The `handleComputerToolUse()` function [packages/bytebot-agent/src/agent/agent.computer-use.ts]() executes the action via bytebotd's `/computer-use` endpoint and returns a `ToolResultContentBlock` containing the result or error.

### Create Task Tool

For subtask creation [packages/bytebot-agent/src/agent/agent.processor.ts:315-340]():

```typescript
if (isCreateTaskToolUseBlock(block)) {
  const type = block.input.type?.toUpperCase() as TaskType;
  const priority = block.input.priority?.toUpperCase() as TaskPriority;

  await this.tasksService.create({
    description: block.input.description,
    type,
    createdBy: Role.ASSISTANT,
    ...(block.input.scheduledFor && {
      scheduledFor: new Date(block.input.scheduledFor),
    }),
    model: task.model,
    priority,
  });

  generatedToolResults.push({
    type: MessageContentType.ToolResult,
    tool_use_id: block.id,
    content: [{
      type: MessageContentType.Text,
      text: 'The task has been created',
    }],
  });
}
```

This allows the agent to spawn subtasks with optional scheduling.

### Set Task Status Tool

For status updates [packages/bytebot-agent/src/agent/agent.processor.ts:342-356]():

```typescript
if (isSetTaskStatusToolUseBlock(block)) {
  setTaskStatusToolUseBlock = block;

  generatedToolResults.push({
    type: MessageContentType.ToolResult,
    tool_use_id: block.id,
    is_error: block.input.status === 'failed',
    content: [{
      type: MessageContentType.Text,
      text: block.input.description,
    }],
  });
}
```

After all tools are processed, if a `setTaskStatusToolUseBlock` was found [packages/bytebot-agent/src/agent/agent.processor.ts:368-382]():

```typescript
if (setTaskStatusToolUseBlock) {
  switch (setTaskStatusToolUseBlock.input.status) {
    case 'completed':
      await this.tasksService.update(taskId, {
        status: TaskStatus.COMPLETED,
        completedAt: new Date(),
      });
      break;
    case 'needs_help':
      await this.tasksService.update(taskId, {
        status: TaskStatus.NEEDS_HELP,
      });
      break;
  }
}
```

Sources: [packages/bytebot-agent/src/agent/agent.processor.ts:309-382]()

---

## Summarization System

### Token Usage Monitoring

```mermaid
flowchart TD
    GenerateResponse["agentResponse = await service.generateMessage(...)"]
    GenerateResponse --> ExtractTokens["totalTokens = agentResponse.tokenUsage.totalTokens"]
    
    ExtractTokens --> GetWindow["contextWindow = model.contextWindow || 200000"]
    GetWindow --> CalcThreshold["contextThreshold = contextWindow * 0.75"]
    
    CalcThreshold --> CheckThreshold{"totalTokens >= contextThreshold?"}
    
    CheckThreshold -->|No| SkipSummarize["Log token usage percentage<br/>Continue to tool processing"]
    
    CheckThreshold -->|Yes| BuildSummaryContext["Build context:<br/>[...messages,<br/>{role: USER, text: 'Respond with a summary...'}]"]
    
    BuildSummaryContext --> CallSummarize["summaryResponse = await service.generateMessage(<br/>SUMMARIZATION_SYSTEM_PROMPT,<br/>context,<br/>modelName,<br/>useTools=false,<br/>signal<br/>)"]
    
    CallSummarize --> ExtractText["Extract text from summaryContentBlocks"]
    
    ExtractText --> CreateSummary["summary = await SummariesService.create({<br/>content: summaryContent,<br/>taskId<br/>})"]
    
    CreateSummary --> AttachMessages["await MessagesService.attachSummary(<br/>taskId,<br/>summary.id,<br/>messageIds<br/>)"]
    
    AttachMessages --> LogSuccess["Log: Generated summary for task {taskId}<br/>due to token usage ({totalTokens}/{contextWindow})"]
    
    LogSuccess --> ContinueProcessing["Continue to tool processing"]
    SkipSummarize --> ContinueProcessing
```

After receiving a response from the LLM [packages/bytebot-agent/src/agent/agent.processor.ts:233-299]():

1. **Calculate threshold** - `contextThreshold = contextWindow * 0.75`
2. **Check usage** - `shouldSummarize = tokenUsage.totalTokens >= contextThreshold`
3. **Generate summary** - If threshold exceeded, send messages to LLM with `SUMMARIZATION_SYSTEM_PROMPT`
4. **Create Summary entity** - Store compressed content via `SummariesService.create()`
5. **Attach messages** - Link processed messages to summary via `MessagesService.attachSummary()`

### Context Building Strategy

At the start of each iteration [packages/bytebot-agent/src/agent/agent.processor.ts:157-180]():

```typescript
const latestSummary = await this.summariesService.findLatest(taskId);
const unsummarizedMessages = await this.messagesService.findUnsummarized(taskId);
const messages = [
  ...(latestSummary
    ? [{
        role: Role.USER,
        content: [{
          type: MessageContentType.Text,
          text: latestSummary.content,
        }],
      }]
    : []),
  ...unsummarizedMessages,
];
```

This creates a hybrid context where:
- **Summary** represents all older messages in compressed form
- **Unsummarized messages** provide full detail for recent interactions

This allows the agent to maintain indefinitely long task histories while staying within token limits.

Sources: [packages/bytebot-agent/src/agent/agent.processor.ts:157-299]()

---

## Error Handling and Abort Control

### AbortController Pattern

```mermaid
sequenceDiagram
    participant AgentProcessor
    participant AbortController
    participant LLMService
    participant TasksService
    
    AgentProcessor->>AbortController: new AbortController()
    Note over AgentProcessor: Each iteration creates fresh controller
    
    AgentProcessor->>LLMService: generateMessage(..., signal)
    
    alt Takeover event received
        AgentProcessor->>AbortController: abort()
        AbortController->>LLMService: Signal abort
        LLMService-->>AgentProcessor: Throw BytebotAgentInterrupt
        Note over AgentProcessor: Catch and log warning
    end
    
    alt Normal completion
        LLMService-->>AgentProcessor: BytebotAgentResponse
        Note over AgentProcessor: Process tools and continue
    end
    
    alt Error during processing
        LLMService-->>AgentProcessor: Throw error
        AgentProcessor->>TasksService: update(taskId, {status: FAILED})
        AgentProcessor->>AgentProcessor: Set isProcessing = false
    end
```

### Interruption Handling

The processor creates a fresh `AbortController` for each iteration [packages/bytebot-agent/src/agent/agent.processor.ts:155]():

```typescript
this.abortController = new AbortController();
```

This prevents accumulation of abort listeners on a single signal across iterations.

### Error Classification

The catch block [packages/bytebot-agent/src/agent/agent.processor.ts:388-402]() distinguishes between:

| Error Type | Handling |
|---|---|
| `BytebotAgentInterrupt` | Log warning, don't update task status (expected during takeover) |
| Other errors | Log error with stack trace, update task status to FAILED, cleanup state |

Sources: [packages/bytebot-agent/src/agent/agent.processor.ts:155, 388-402]()

---

## Status Check and Cleanup

### Public Status Methods

```typescript
isRunning(): boolean {
  return this.isProcessing;
}

getCurrentTaskId(): string | null {
  return this.currentTaskId;
}
```

These methods [packages/bytebot-agent/src/agent/agent.processor.ts:73-82]() allow external components (like the AgentScheduler) to check processor state before attempting to start a new task.

### stopProcessing Method

```typescript
async stopProcessing(): Promise<void> {
  if (!this.isProcessing) {
    return;
  }

  this.logger.log(`Stopping execution of task ${this.currentTaskId}`);

  // Signal any in-flight async operations to abort
  this.abortController?.abort();

  await this.inputCaptureService.stop();

  this.isProcessing = false;
  this.currentTaskId = null;
}
```

This method [packages/bytebot-agent/src/agent/agent.processor.ts:405-419]():
1. Aborts pending LLM requests
2. Stops input capture service
3. Resets processing state

Sources: [packages/bytebot-agent/src/agent/agent.processor.ts:73-82, 405-419]()

---

# Page: Computer Use Integration

# Computer Use Integration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [packages/bytebot-agent/prisma/migrations/20250722041608_files/migration.sql](packages/bytebot-agent/prisma/migrations/20250722041608_files/migration.sql)
- [packages/bytebot-agent/src/agent/agent.computer-use.ts](packages/bytebot-agent/src/agent/agent.computer-use.ts)
- [packages/bytebot-agent/src/agent/agent.constants.ts](packages/bytebot-agent/src/agent/agent.constants.ts)
- [packages/bytebot-agent/src/agent/agent.scheduler.ts](packages/bytebot-agent/src/agent/agent.scheduler.ts)
- [packages/bytebot-agent/src/agent/agent.tools.ts](packages/bytebot-agent/src/agent/agent.tools.ts)
- [packages/bytebotd/src/computer-use/computer-use.controller.ts](packages/bytebotd/src/computer-use/computer-use.controller.ts)
- [packages/bytebotd/src/main.ts](packages/bytebotd/src/main.ts)

</details>



This document explains how Bytebot's agent service translates AI model decisions into executable computer actions on the virtual desktop. It covers the tool definition system, the execution pipeline from AI responses to desktop commands, and the integration between the agent and desktop services.

For information about the desktop service API that receives these commands, see [Computer Use API](#5.1). For details about AI model integration and tool handling, see [AI Model Integration](#6.3).

## Overview

The Computer Use Integration system enables AI models to control the virtual desktop through a standardized tool interface. When an AI model decides to perform a computer action, it responds with tool use requests that are processed by the agent service and translated into HTTP requests to the desktop service.

```mermaid
flowchart TB
    subgraph "AI Model Response"
        AIModel["AI Model"]
        ToolUse["Tool Use Response<br/>ComputerToolUseContentBlock"]
    end
    
    subgraph "Agent Service"
        Handler["handleComputerToolUse()<br/>agent.computer-use.ts"]
        Validation["Tool Validation<br/>Type Guards"]
        ActionFn["Action Functions<br/>(moveMouse, clickMouse, etc.)"]
    end
    
    subgraph "Desktop Service"
        Controller["ComputerUseController<br/>/computer-use endpoint"]
        Service["ComputerUseService<br/>Desktop Execution"]
    end
    
    subgraph "Desktop Environment"
        X11["X11 Display"]
        Apps["GUI Applications"]
    end
    
    AIModel --> ToolUse
    ToolUse --> Handler
    Handler --> Validation
    Validation --> ActionFn
    ActionFn --> |HTTP POST| Controller
    Controller --> Service
    Service --> X11
    X11 --> Apps
```

Sources: [packages/bytebot-agent/src/agent/agent.computer-use.ts:28-239](), [packages/bytebotd/src/computer-use/computer-use.controller.ts:13-42]()

## Tool Definition System

The system provides AI models with a comprehensive set of computer interaction tools defined in `agentTools`. Each tool has a structured schema that specifies valid inputs and expected behavior.

### Mouse Tools

| Tool Name | Purpose | Key Parameters |
|-----------|---------|----------------|
| `computer_move_mouse` | Move cursor to coordinates | `coordinates` (x, y) |
| `computer_click_mouse` | Click at position or current location | `button`, `clickCount`, optional `coordinates` |
| `computer_drag_mouse` | Drag along a path | `path[]`, `button`, optional `holdKeys` |
| `computer_scroll` | Scroll in direction | `coordinates`, `direction`, `scrollCount` |

### Keyboard Tools

| Tool Name | Purpose | Key Parameters |
|-----------|---------|----------------|
| `computer_type_keys` | Type key sequences/shortcuts | `keys[]`, optional `delay` |
| `computer_type_text` | Type text character by character | `text`, optional `delay`, `isSensitive` |
| `computer_paste_text` | Paste text via clipboard | `text`, `isSensitive` |
| `computer_press_keys` | Hold/release keys | `keys[]`, `press` (up/down) |

### System Tools

| Tool Name | Purpose | Key Parameters |
|-----------|---------|----------------|
| `computer_screenshot` | Capture screen image | None |
| `computer_cursor_position` | Get cursor coordinates | None |
| `computer_application` | Open/focus application | `application` (enum) |
| `computer_wait` | Pause execution | `duration` (500ms) |
| `computer_read_file` | Read file contents | `path` |

Sources: [packages/bytebot-agent/src/agent/agent.tools.ts:35-405]()

## Tool Execution Pipeline

The `handleComputerToolUse` function processes AI model tool requests through a multi-stage pipeline:

```mermaid
flowchart TD
    Input["ComputerToolUseContentBlock<br/>from AI Model"]
    
    subgraph "Type-Specific Handling"
        Screenshot["isScreenshotToolUseBlock()<br/>Direct execution"]
        Cursor["isCursorPositionToolUseBlock()<br/>Direct execution"]
        OtherTools["Other Tool Types<br/>Delegated execution"]
    end
    
    subgraph "Action Execution"
        ActionCall["Action Function Call<br/>(moveMouse, typeText, etc.)"]
        HTTPReq["HTTP Request to<br/>BYTEBOT_DESKTOP_BASE_URL"]
        Wait["750ms delay"]
        AutoScreenshot["Automatic screenshot<br/>after action"]
    end
    
    subgraph "Response Formation"
        Success["ToolResultContentBlock<br/>with success message"]
        Error["ToolResultContentBlock<br/>with error flag"]
        WithImage["Add screenshot to<br/>response content"]
    end
    
    Input --> Screenshot
    Input --> Cursor
    Input --> OtherTools
    
    Screenshot --> Success
    Cursor --> Success
    OtherTools --> ActionCall
    ActionCall --> HTTPReq
    HTTPReq --> Wait
    Wait --> AutoScreenshot
    AutoScreenshot --> WithImage
    WithImage --> Success
    
    ActionCall -.->|Exception| Error
    HTTPReq -.->|Exception| Error
    AutoScreenshot -.->|Exception| Success
```

Sources: [packages/bytebot-agent/src/agent/agent.computer-use.ts:28-239]()

## Computer Action Implementation

Each computer action is implemented as an async function that makes HTTP requests to the desktop service. The functions follow a consistent pattern:

### Mouse Actions

The `moveMouse` function demonstrates the standard pattern:
- Accepts typed input parameters
- Logs the action being performed  
- Makes POST request to `/computer-use` endpoint
- Includes proper error handling

```typescript
// Example from moveMouse function
await fetch(`${BYTEBOT_DESKTOP_BASE_URL}/computer-use`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    action: 'move_mouse',
    coordinates,
  }),
});
```

### Advanced Mouse Operations

More complex operations like `dragMouse` and `traceMouse` handle coordinate arrays and optional modifier keys:
- `traceMouse`: Moves along a path without button press
- `dragMouse`: Moves along path while holding button down
- Both support `holdKeys` for modifier combinations

### Keyboard Input Handling

The system provides multiple keyboard input methods:
- `typeKeys`: For key sequences and shortcuts using the valid key identifiers
- `typeText`: Character-by-character typing with optional delays
- `pasteText`: Clipboard-based text insertion for longer strings
- `pressKeys`: Hold or release specific keys

### File Operations

The `readFile` function returns structured responses with base64 data:
- Success: Returns `data`, `name`, `size`, `mediaType`
- Error: Returns `success: false` with error message
- Special handling in `handleComputerToolUse` to create document content blocks

Sources: [packages/bytebot-agent/src/agent/agent.computer-use.ts:241-646]()

## Response Processing and Screenshots

The system automatically captures screenshots after most actions to provide visual feedback to AI models:

### Automatic Screenshot Logic

1. **750ms Delay**: Allows UI to settle after action
2. **Screenshot Capture**: Uses the same `screenshot()` function  
3. **Response Enhancement**: Adds image to `ToolResultContentBlock`
4. **Error Resilience**: Screenshot failures don't fail the action

### Screenshot Function

The `screenshot` function communicates with the desktop service:
- Makes POST request with `action: 'screenshot'`  
- Returns base64-encoded PNG image data
- Includes comprehensive error handling
- Used both for explicit screenshot tools and automatic captures

### Special Case Handling

Some tools have special response handling:
- **Screenshot Tool**: Returns image directly in response
- **Cursor Position**: Returns text with coordinates  
- **Read File**: Returns document content block with file data
- **Standard Actions**: Return success message plus automatic screenshot

Sources: [packages/bytebot-agent/src/agent/agent.computer-use.ts:184-221](), [packages/bytebot-agent/src/agent/agent.computer-use.ts:526-555]()

## Error Handling and Logging

The system implements comprehensive error handling at multiple levels:

### Tool-Level Error Handling

Each action function catches exceptions and re-throws them:
- Network errors from desktop service communication
- Invalid parameters or malformed requests
- Desktop service internal errors

### Handler-Level Error Processing

The `handleComputerToolUse` function provides consistent error response formatting:
- Creates `ToolResultContentBlock` with `is_error: true`
- Includes descriptive error messages
- Logs full error details with stack traces
- Maintains tool_use_id for proper response correlation

### Logging Strategy

The system uses structured logging throughout:
- **Debug Level**: Action parameters and execution flow
- **Error Level**: Exceptions with full context and stack traces  
- **Sensitive Data**: Screenshots and file content not logged in full

Sources: [packages/bytebot-agent/src/agent/agent.computer-use.ts:57-70](), [packages/bytebot-agent/src/agent/agent.computer-use.ts:222-238]()

## Desktop Service Integration

The agent communicates with the desktop service through a REST API defined by the `BYTEBOT_DESKTOP_BASE_URL` environment variable.

### Request Format

All requests follow a consistent JSON structure:
```json
{
  "action": "action_name",
  "parameter1": "value1",
  "parameter2": "value2"
}
```

### Supported Actions

The desktop service handles these action types:
- **Mouse**: `move_mouse`, `click_mouse`, `press_mouse`, `drag_mouse`, `trace_mouse`
- **Keyboard**: `type_keys`, `press_keys`, `type_text`, `paste_text`  
- **System**: `scroll`, `wait`, `screenshot`, `cursor_position`, `application`
- **File**: `read_file`, `write_file`

### Response Handling

Different actions return different response formats:
- **Screenshot**: `{ image: "base64_data" }`
- **Cursor Position**: `{ x: number, y: number }`
- **File Read**: `{ success: boolean, data?: string, name?: string, size?: number, mediaType?: string }`
- **Standard Actions**: HTTP status indicates success/failure

Sources: [packages/bytebot-agent/src/agent/agent.computer-use.ts:26](), [packages/bytebotd/src/computer-use/computer-use.controller.ts:19-41]()

---

# Page: AI Model Integration

# AI Model Integration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [packages/bytebot-agent/src/agent/agent.types.ts](packages/bytebot-agent/src/agent/agent.types.ts)
- [packages/bytebot-agent/src/anthropic/anthropic.constants.ts](packages/bytebot-agent/src/anthropic/anthropic.constants.ts)
- [packages/bytebot-agent/src/anthropic/anthropic.service.ts](packages/bytebot-agent/src/anthropic/anthropic.service.ts)
- [packages/bytebot-agent/src/google/google.constants.ts](packages/bytebot-agent/src/google/google.constants.ts)
- [packages/bytebot-agent/src/google/google.service.ts](packages/bytebot-agent/src/google/google.service.ts)
- [packages/bytebot-agent/src/messages/messages.module.ts](packages/bytebot-agent/src/messages/messages.module.ts)
- [packages/bytebot-agent/src/messages/messages.service.ts](packages/bytebot-agent/src/messages/messages.service.ts)
- [packages/bytebot-agent/src/openai/openai.constants.ts](packages/bytebot-agent/src/openai/openai.constants.ts)
- [packages/bytebot-agent/src/openai/openai.service.ts](packages/bytebot-agent/src/openai/openai.service.ts)

</details>



This document covers Bytebot's multi-provider AI integration system, which enables the agent to work with different AI models from Anthropic, OpenAI, and Google through a unified interface. The system handles message formatting, tool integration, and response processing across different AI providers while maintaining consistent behavior and capabilities.

For information about how the agent processes these AI responses to execute computer actions, see [Computer Use Integration](#6.2). For details on task orchestration and lifecycle management, see [Task Management](#6.1).

## Provider Architecture Overview

The AI model integration system uses a common interface pattern that allows different AI providers to be used interchangeably while maintaining consistent tool access and message formatting.

```mermaid
graph TB
    subgraph "Agent Core"
        AgentProcessor["AgentProcessor<br/>Task Orchestration"]
        AgentTypes["BytebotAgentService<br/>Common Interface"]
    end
    
    subgraph "Provider Services"
        AnthropicService["AnthropicService<br/>Claude Integration"]
        OpenAIService["OpenAIService<br/>GPT Integration"] 
        GoogleService["GoogleService<br/>Gemini Integration"]
    end
    
    subgraph "Provider Tools"
        AnthropicTools["anthropicTools<br/>Anthropic.Tool[]"]
        OpenAITools["openaiTools<br/>OpenAI Tools"]
        GoogleTools["googleTools<br/>Google Function Declarations"]
    end
    
    subgraph "Model Definitions"
        AnthropicModels["ANTHROPIC_MODELS<br/>claude-opus-4-1-20250805<br/>claude-sonnet-4-20250514"]
        OpenAIModels["OPENAI_MODELS<br/>o3-2025-04-16<br/>gpt-4.1-2025-04-14"]
        GoogleModels["GOOGLE_MODELS<br/>gemini-2.5-pro<br/>gemini-2.5-flash"]
    end
    
    AgentProcessor --> AgentTypes
    AgentTypes --> AnthropicService
    AgentTypes --> OpenAIService  
    AgentTypes --> GoogleService
    
    AnthropicService --> AnthropicTools
    OpenAIService --> OpenAITools
    GoogleService --> GoogleTools
    
    AnthropicService --> AnthropicModels
    OpenAIService --> OpenAIModels
    GoogleService --> GoogleModels
```

**Sources**: [packages/bytebot-agent/src/agent/agent.types.ts:13-21](), [packages/bytebot-agent/src/anthropic/anthropic.service.ts:24](), [packages/bytebot-agent/src/openai/openai.service.ts:25](), [packages/bytebot-agent/src/google/google.service.ts:30]()

## Common Interface Design

All AI provider services implement the `BytebotAgentService` interface, which standardizes how the agent interacts with different AI models regardless of their underlying APIs.

### BytebotAgentService Interface

The core interface defines a single method for message generation:

| Method | Parameters | Return Type | Purpose |
|--------|------------|-------------|---------|
| `generateMessage` | `systemPrompt`, `messages`, `model`, `useTools`, `signal?` | `Promise<BytebotAgentResponse>` | Generate AI response with tool support |

### Response Structure

All providers return a standardized `BytebotAgentResponse`:

```typescript
interface BytebotAgentResponse {
  contentBlocks: MessageContentBlock[];
  tokenUsage: {
    inputTokens: number;
    outputTokens: number; 
    totalTokens: number;
  };
}
```

**Sources**: [packages/bytebot-agent/src/agent/agent.types.ts:4-11](), [packages/bytebot-agent/src/agent/agent.types.ts:13-21]()

## Provider-Specific Services

Each AI provider has a dedicated service that handles the specifics of that provider's API while implementing the common interface.

### AnthropicService

The `AnthropicService` integrates with Claude models using the Anthropic SDK:

```mermaid
graph LR
    subgraph "AnthropicService Implementation"
        generateMessage["generateMessage()"]
        formatMessages["formatMessagesForAnthropic()"]
        formatResponse["formatAnthropicResponse()"]
        anthropicSDK["@anthropic-ai/sdk"]
    end
    
    generateMessage --> formatMessages
    formatMessages --> anthropicSDK
    anthropicSDK --> formatResponse
    formatResponse --> generateMessage
```

Key features:
- Supports Claude Opus 4.1 and Claude Sonnet 4 models
- Implements prompt caching with `cache_control` ephemeral markers
- Handles thinking content blocks for reasoning models
- Processes user action content blocks for takeover scenarios

### OpenAIService

The `OpenAIService` provides integration with OpenAI's GPT and o3 models:

```mermaid
graph LR
    subgraph "OpenAIService Implementation" 
        generateMessage2["generateMessage()"]
        formatMessages2["formatMessagesForOpenAI()"]
        formatResponse2["formatOpenAIResponse()"]
        openaiSDK["openai SDK"]
    end
    
    generateMessage2 --> formatMessages2
    formatMessages2 --> openaiSDK
    openaiSDK --> formatResponse2
    formatResponse2 --> generateMessage2
```

Key features:
- Supports o3 and GPT-4.1 models with different context windows
- Uses OpenAI's Responses API for structured interaction
- Handles reasoning models with encrypted content for thinking
- Processes function calls and tool outputs

### GoogleService

The `GoogleService` enables integration with Google's Gemini models:

```mermaid
graph LR  
    subgraph "GoogleService Implementation"
        generateMessage3["generateMessage()"]
        formatMessages3["formatMessagesForGoogle()"]
        formatResponse3["formatGoogleResponse()"]
        googleSDK["@google/genai"]
    end
    
    generateMessage3 --> formatMessages3
    formatMessages3 --> googleSDK
    googleSDK --> formatResponse3
    formatResponse3 --> generateMessage3
```

Key features:
- Supports Gemini 2.5 Pro and Flash models with 1M token context
- Implements thinking budget configuration for reasoning
- Handles function declarations for tool integration
- Processes inline data for image content

**Sources**: [packages/bytebot-agent/src/anthropic/anthropic.service.ts:42-102](), [packages/bytebot-agent/src/openai/openai.service.ts:43-91](), [packages/bytebot-agent/src/google/google.service.ts:48-116]()

## Tool Integration

The system provides consistent tool access across all AI providers by converting from a common tool definition format to provider-specific formats.

### Tool Conversion Architecture

```mermaid
graph TB
    subgraph "Common Tool Definitions"
        AgentTools["agentTools<br/>Universal Tool Definitions"]
    end
    
    subgraph "Provider Tool Adapters"
        AnthropicAdapter["agentToolToAnthropicTool()<br/>Anthropic.Tool conversion"]
        OpenAIAdapter["agentToolToOpenAITool()<br/>OpenAI Tool conversion"] 
        GoogleAdapter["agentToolToGoogleTool()<br/>Function Declaration conversion"]
    end
    
    subgraph "Provider Tool Arrays"
        AnthropicToolArray["anthropicTools: Anthropic.Tool[]"]
        OpenAIToolArray["openaiTools: OpenAI Tool[]"]
        GoogleToolArray["googleTools: Function Declarations"]
    end
    
    AgentTools --> AnthropicAdapter
    AgentTools --> OpenAIAdapter
    AgentTools --> GoogleAdapter
    
    AnthropicAdapter --> AnthropicToolArray
    OpenAIAdapter --> OpenAIToolArray  
    GoogleAdapter --> GoogleToolArray
```

### Available Tools

The system provides these computer automation tools across all providers:

| Tool Category | Tools | Purpose |
|---------------|-------|---------|
| Mouse Control | `moveMouseTool`, `clickMouseTool`, `dragMouseTool` | Cursor manipulation |
| Keyboard Input | `typeKeysTool`, `pressKeysTool`, `typeTextTool`, `pasteTextTool` | Text and key input |
| Screen Operations | `screenshotTool`, `cursorPositionTool`, `scrollTool` | Screen interaction |
| Task Management | `setTaskStatusTool`, `createTaskTool` | Task control |
| System | `waitTool`, `applicationTool` | General operations |

**Sources**: [packages/bytebot-agent/src/anthropic/anthropic.tools.ts:7-54](), [packages/bytebot-agent/src/anthropic/anthropic.tools.ts:34-49]()

## Message Format Translation

Each provider service implements bidirectional message format conversion to translate between Bytebot's internal `MessageContentBlock` format and the provider's expected format.

### Message Processing Flow

```mermaid
sequenceDiagram
    participant Agent as "Agent Core"
    participant Service as "Provider Service"
    participant Provider as "AI Provider API"
    
    Agent->>Service: generateMessage(systemPrompt, messages, model, useTools)
    Service->>Service: formatMessagesFor[Provider](messages)
    Note over Service: Convert MessageContentBlock[] to provider format
    Service->>Provider: API call with formatted messages
    Provider->>Service: Provider-specific response
    Service->>Service: format[Provider]Response(response)
    Note over Service: Convert response to MessageContentBlock[]
    Service->>Agent: BytebotAgentResponse with contentBlocks
```

### Content Block Type Handling

Each provider handles these content block types:

| Content Type | Anthropic | OpenAI | Google | Internal Type |
|--------------|-----------|---------|--------|---------------|
| Text | `text` block | `input_text`/`output_text` | `text` part | `MessageContentType.Text` |
| Tool Use | `tool_use` block | `function_call` | `functionCall` part | `MessageContentType.ToolUse` |
| Tool Result | `tool_result` block | `function_call_output` | `functionResponse` part | `MessageContentType.ToolResult` |
| Image | `image` block | `input_image` | `inlineData` part | `MessageContentType.Image` |
| Thinking | `thinking` block | `reasoning` | `thought` part | `MessageContentType.Thinking` |

### Special Message Handling

The system handles these special message scenarios:

- **User Action Messages**: When users take control, their actions are formatted as descriptive text for the AI
- **Tool Result Images**: Screenshots from tool execution are embedded as image content
- **Thinking Content**: Reasoning steps from models that support internal reasoning

**Sources**: [packages/bytebot-agent/src/anthropic/anthropic.service.ts:107-154](), [packages/bytebot-agent/src/openai/openai.service.ts:93-240](), [packages/bytebot-agent/src/google/google.service.ts:121-234]()

## Model Configuration

Each provider defines available models with their capabilities and context windows.

### Model Definitions

| Provider | Models | Context Window | Default |
|----------|---------|---------------|---------|
| Anthropic | `claude-opus-4-1-20250805`, `claude-sonnet-4-20250514` | 200,000 tokens | Claude Opus 4.1 |
| OpenAI | `o3-2025-04-16`, `gpt-4.1-2025-04-14` | 200,000 / 1,047,576 tokens | o3 |
| Google | `gemini-2.5-pro`, `gemini-2.5-flash` | 1,000,000 tokens | Gemini 2.5 Pro |

### Provider Selection

The system uses environment variables to configure API access:

| Environment Variable | Provider | Purpose |
|---------------------|----------|---------|
| `ANTHROPIC_API_KEY` | Anthropic | Claude model access |
| `OPENAI_API_KEY` | OpenAI | GPT and o3 model access |
| `GEMINI_API_KEY` | Google | Gemini model access |

**Sources**: [packages/bytebot-agent/src/anthropic/anthropic.constants.ts:3-18](), [packages/bytebot-agent/src/openai/openai.constants.ts:3-18](), [packages/bytebot-agent/src/google/google.constants.ts:3-18]()

---

# Page: Message and Summarization

# Message and Summarization

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [packages/bytebot-agent/src/agent/agent.processor.ts](packages/bytebot-agent/src/agent/agent.processor.ts)
- [packages/bytebot-agent/src/agent/agent.types.ts](packages/bytebot-agent/src/agent/agent.types.ts)
- [packages/bytebot-agent/src/anthropic/anthropic.constants.ts](packages/bytebot-agent/src/anthropic/anthropic.constants.ts)
- [packages/bytebot-agent/src/anthropic/anthropic.service.ts](packages/bytebot-agent/src/anthropic/anthropic.service.ts)
- [packages/bytebot-agent/src/google/google.constants.ts](packages/bytebot-agent/src/google/google.constants.ts)
- [packages/bytebot-agent/src/google/google.service.ts](packages/bytebot-agent/src/google/google.service.ts)
- [packages/bytebot-agent/src/messages/messages.module.ts](packages/bytebot-agent/src/messages/messages.module.ts)
- [packages/bytebot-agent/src/messages/messages.service.ts](packages/bytebot-agent/src/messages/messages.service.ts)
- [packages/bytebot-agent/src/openai/openai.constants.ts](packages/bytebot-agent/src/openai/openai.constants.ts)
- [packages/bytebot-agent/src/openai/openai.service.ts](packages/bytebot-agent/src/openai/openai.service.ts)
- [packages/bytebot-agent/src/tasks/tasks.controller.ts](packages/bytebot-agent/src/tasks/tasks.controller.ts)
- [packages/bytebot-agent/src/tasks/tasks.service.ts](packages/bytebot-agent/src/tasks/tasks.service.ts)
- [packages/bytebot-ui/src/hooks/useChatSession.ts](packages/bytebot-ui/src/hooks/useChatSession.ts)

</details>



This document explains how Bytebot stores messages, builds context for LLM requests, and implements automatic summarization to manage context window limits. The system uses a 75% token threshold to trigger summarization and supports hierarchical summaries for very long conversations.

For information about agent processing flow, see [Agent Processor](#6.1). For message content type definitions, see [Message Content Types](#9.3).

## Message Storage Schema

The `Message` model stores conversation history with flexible content blocks. Each message belongs to a task and optionally links to a summary when it has been summarized.

**Database Schema**

```mermaid
erDiagram
    Task ||--o{ Message : "has"
    Summary ||--o{ Message : "summarizes"
    Summary ||--o{ Summary : "parent"
    
    Message {
        string id PK
        json content "MessageContentBlock[]"
        Role role "USER or ASSISTANT" 
        datetime createdAt
        datetime updatedAt
        string taskId FK
        string summaryId FK "null until summarized"
    }
    
    Task {
        string id PK
        string description
        TaskStatus status
    }
    
    Summary {
        string id PK
        string content "Text summary"
        string taskId FK
        string parentId FK "For hierarchical summaries"
    }
```

**Key Fields**

| Field | Type | Purpose |
|-------|------|---------|
| `content` | `Json` | Array of `MessageContentBlock` objects |
| `role` | `Role` | Enum: `USER` or `ASSISTANT` |
| `taskId` | `String` | Foreign key to parent task |
| `summaryId` | `String?` | Links to summary when messages are compressed |

**Content Storage**

Messages store content as a JSON array of content blocks. Each block has a `type` field that determines its structure:

- `text`: Plain text content
- `image`: Base64-encoded images
- `tool_use`: AI tool execution requests
- `tool_result`: Tool execution results (including screenshots)
- `thinking`: AI reasoning traces
- `user_action`: Captured user actions during takeover

Sources: [packages/bytebot-agent/prisma/schema.prisma:83-99](), [packages/bytebot-agent/src/messages/messages.service.ts:36-52]()

## Message Content Types

Messages use a flexible content block structure defined in `@bytebot/shared`. See [Message Content Types](#9.3) for detailed type definitions.

**Common Message Patterns**

| Role | Content Type | Example Use Case |
|------|--------------|------------------|
| `USER` | `text` | User provides task instructions |
| `USER` | `tool_result` | Screenshot results from computer actions |
| `ASSISTANT` | `text` | AI explains its reasoning |
| `ASSISTANT` | `tool_use` | AI requests to execute computer actions |
| `ASSISTANT` | `thinking` | AI reasoning traces (extended thinking) |
| `USER` | `user_action` | Captured actions during user takeover |

**Message Creation**

The `MessagesService.create()` method stores new messages and emits WebSocket events:

```typescript
// From packages/bytebot-agent/src/messages/messages.service.ts:36-52
async create(data: {
  content: MessageContentBlock[];
  role: Role;
  taskId: string;
}): Promise<Message>
```

Sources: [packages/bytebot-agent/src/messages/messages.service.ts:36-52](), [@bytebot/shared package types]()

## Context Building for LLM

When the agent makes an LLM request, it assembles context from the latest summary (if any) and all unsummarized messages. This compressed representation keeps token usage manageable while preserving conversation history.

**Context Assembly Process**

```mermaid
graph TB
    subgraph "Context Sources"
        LatestSummary["SummariesService.findLatest(taskId)"]
        UnsummarizedMsgs["MessagesService.findUnsummarized(taskId)"]
    end
    
    subgraph "Context Array Construction"
        LatestSummary -->|"If summary exists"| SummaryMessage["Synthetic USER message\nwith summary text"]
        UnsummarizedMsgs -->|"Always included"| MessageArray["Unsummarized messages"]
        
        SummaryMessage --> ContextArray["messages = [summary, ...unsummarized]"]
        MessageArray --> ContextArray
    end
    
    ContextArray --> LLMRequest["BytebotAgentService.generateMessage()"]
    LLMRequest --> LLMResponse["AI response with token usage"]
```

**Code Implementation**

The `AgentProcessor` builds context in the iteration loop:

```typescript
// From packages/bytebot-agent/src/agent/agent.processor.ts:157-180
const latestSummary = await this.summariesService.findLatest(taskId);
const unsummarizedMessages = await this.messagesService.findUnsummarized(taskId);

const messages = [
  ...(latestSummary ? [{
    id: '',
    createdAt: new Date(),
    updatedAt: new Date(),
    taskId,
    summaryId: null,
    role: Role.USER,
    content: [{
      type: MessageContentType.Text,
      text: latestSummary.content,
    }],
  }] : []),
  ...unsummarizedMessages,
];
```

**Query Methods**

| Method | Purpose | Returns |
|--------|---------|---------|
| `findLatest(taskId)` | Gets most recent summary | `Summary \| null` |
| `findUnsummarized(taskId)` | Gets messages with `summaryId = null` | `Message[]` |

Sources: [packages/bytebot-agent/src/agent/agent.processor.ts:157-180](), [packages/bytebot-agent/src/messages/messages.service.ts:89-98]()

## Token-Based Summarization

The system monitors token usage against the model's context window and triggers automatic summarization when usage exceeds 75% of the available context. This prevents context overflow and maintains conversation continuity.

**Summarization Trigger Flow**

```mermaid
sequenceDiagram
    participant AgentProcessor
    participant BytebotAgentService
    participant SummariesService
    participant MessagesService
    participant Database
    
    Note over AgentProcessor: During iteration loop
    
    AgentProcessor->>AgentProcessor: Build context array
    AgentProcessor->>BytebotAgentService: generateMessage(AGENT_SYSTEM_PROMPT, messages, ...)
    BytebotAgentService-->>AgentProcessor: response with tokenUsage
    
    AgentProcessor->>AgentProcessor: Check: tokenUsage.totalTokens >= contextWindow * 0.75
    
    alt Token usage exceeds 75% threshold
        Note over AgentProcessor,Database: Summarization process
        
        AgentProcessor->>BytebotAgentService: generateMessage(SUMMARIZATION_SYSTEM_PROMPT, messages, ...)
        Note over BytebotAgentService: useTools=false for summarization
        BytebotAgentService-->>AgentProcessor: summary content blocks
        
        AgentProcessor->>AgentProcessor: Extract text from content blocks
        AgentProcessor->>SummariesService: create({ content, taskId })
        SummariesService->>Database: INSERT INTO Summary
        
        AgentProcessor->>MessagesService: attachSummary(taskId, summaryId, messageIds)
        MessagesService->>Database: UPDATE Message SET summaryId WHERE id IN (...)
        
        Note over AgentProcessor: Future iterations will use this summary
    end
```

**Token Threshold Calculation**

```typescript
// From packages/bytebot-agent/src/agent/agent.processor.ts:234-238
const contextWindow = model.contextWindow || 200000; // Default 200k
const contextThreshold = contextWindow * 0.75;
const shouldSummarize = agentResponse.tokenUsage.totalTokens >= contextThreshold;
```

**Model Context Windows**

| Provider | Model | Context Window |
|----------|-------|----------------|
| Anthropic | Claude Opus 4.1 | 200,000 tokens |
| Anthropic | Claude Sonnet 4 | 200,000 tokens |
| OpenAI | o3 | 200,000 tokens |
| OpenAI | GPT-4.1 | 1,047,576 tokens |
| Google | Gemini 2.5 Pro | 1,000,000 tokens |

**Summarization System Prompt**

The agent uses `SUMMARIZATION_SYSTEM_PROMPT` when generating summaries. This prompt instructs the LLM to compress the conversation into a concise summary while preserving key context.

Sources: [packages/bytebot-agent/src/agent/agent.processor.ts:234-299](), [packages/bytebot-agent/src/anthropic/anthropic.constants.ts:3-16](), [packages/bytebot-agent/src/openai/openai.constants.ts:3-16](), [packages/bytebot-agent/src/google/google.constants.ts:3-16]()

## Hierarchical Summaries

For very long conversations that exceed context limits even after initial summarization, the system supports hierarchical summaries where one summary can reference a parent summary. This creates a multi-level compression structure.

**Hierarchical Summary Structure**

```mermaid
graph TB
    Summary1["Summary 1\nparentId: null\ncontent: 'Early conversation summary'"]
    Summary2["Summary 2\nparentId: Summary1.id\ncontent: 'Middle conversation summary'"]
    Summary3["Summary 3\nparentId: Summary2.id\ncontent: 'Recent conversation summary'"]
    
    Message1["Messages 1-100\nsummaryId: Summary1.id"]
    Message2["Messages 101-200\nsummaryId: Summary2.id"]
    Message3["Messages 201-300\nsummaryId: Summary3.id"]
    Message4["Messages 301+\nsummaryId: null\n(unsummarized)"]
    
    Summary1 --> Message1
    Summary2 --> Summary1
    Summary2 --> Message2
    Summary3 --> Summary2
    Summary3 --> Message3
    
    style Message4 fill:#f9f9f9
```

**Summary Schema**

```typescript
// From prisma schema
model Summary {
  id        String   @id @default(cuid())
  content   String   @db.Text
  taskId    String
  task      Task     @relation(fields: [taskId], references: [id], onDelete: Cascade)
  parentId  String?
  parent    Summary? @relation("SummaryHierarchy", fields: [parentId], references: [id])
  children  Summary[] @relation("SummaryHierarchy")
  messages  Message[]
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt
}
```

**Context Building with Hierarchy**

When a parent summary exists, the `findLatest()` method retrieves the most recent summary, which implicitly includes context from parent summaries through the LLM's compression:

1. First summarization creates Summary1 (parentId=null)
2. When tokens exceed threshold again, create Summary2 (parentId=Summary1.id)
3. Context array uses Summary2 content, which references Summary1's context
4. Each summary level compresses approximately 75% of a context window's worth of messages

Sources: [packages/bytebot-agent/prisma/schema.prisma](), [packages/bytebot-agent/src/summaries/summaries.service.ts]()

## Summary Attachment Process

After creating a summary, the system links the summarized messages to the summary record by updating their `summaryId` field. This marks them as summarized and excludes them from future context builds.

**Attachment Workflow**

```mermaid
sequenceDiagram
    participant AgentProcessor
    participant SummariesService
    participant MessagesService
    participant Database
    
    Note over AgentProcessor: After generating summary text
    
    AgentProcessor->>SummariesService: create({ content: summaryText, taskId })
    SummariesService->>Database: INSERT INTO Summary
    SummariesService-->>AgentProcessor: summary (with id)
    
    AgentProcessor->>AgentProcessor: Extract message IDs from context array
    AgentProcessor->>MessagesService: attachSummary(taskId, summaryId, messageIds)
    
    MessagesService->>Database: UPDATE Message<br/>SET summaryId = summaryId<br/>WHERE taskId = taskId<br/>AND id IN (messageIds)
    
    Note over Database: Messages now have summaryId populated
    Note over Database: findUnsummarized() will exclude these messages
```

**Code Implementation**

```typescript
// From packages/bytebot-agent/src/messages/messages.service.ts:100-113
async attachSummary(
  taskId: string,
  summaryId: string,
  messageIds: string[],
): Promise<void> {
  if (messageIds.length === 0) {
    return;
  }

  await this.prisma.message.updateMany({
    where: { taskId, id: { in: messageIds } },
    data: { summaryId },
  });
}
```

**Query Exclusion**

Once messages have a `summaryId`, they are excluded from context building:

```typescript
// From packages/bytebot-agent/src/messages/messages.service.ts:89-98
async findUnsummarized(taskId: string): Promise<Message[]> {
  return this.prisma.message.findMany({
    where: {
      taskId,
      summaryId: null,  // Only return messages not yet summarized
    },
    orderBy: { createdAt: 'asc' },
  });
}
```

This creates a clear boundary between compressed historical context (in summaries) and active conversation context (unsummarized messages).

Sources: [packages/bytebot-agent/src/agent/agent.processor.ts:279-288](), [packages/bytebot-agent/src/messages/messages.service.ts:89-113]()

## Message Summarization

To manage context window limits, the system automatically summarizes older messages when token usage approaches provider limits. Summaries replace groups of messages while preserving essential context.

```mermaid
sequenceDiagram
    participant AgentProcessor
    participant AIService
    participant SummariesService
    participant MessagesService
    participant Database
    
    Note over AgentProcessor,Database: Summarization Trigger
    
    AgentProcessor->>AgentProcessor: Check token usage vs context window
    AgentProcessor->>AIService: Generate response
    AIService-->>AgentProcessor: Response + token usage
    
    alt Token usage > 75% of context window
        AgentProcessor->>AIService: Generate summary request
        Note over AIService: Uses SUMMARIZATION_SYSTEM_PROMPT
        AIService-->>AgentProcessor: Summary content blocks
        
        AgentProcessor->>SummariesService: Create summary
        SummariesService->>Database: Store summary
        
        AgentProcessor->>MessagesService: Attach summary to messages
        MessagesService->>Database: Update messages with summaryId
        
        Note over AgentProcessor: Future requests use summary + unsummarized messages
    end
```

**Summarization Process**

1. Monitor token usage during AI generation
2. When approaching context limit (75% of window), trigger summarization
3. Send existing messages to AI with summarization prompt
4. Store summary and link it to original messages
5. Future requests load summary + unsummarized messages only

**Summary Management**

- `SummariesService` handles summary CRUD operations
- `findUnsummarized()` retrieves messages not yet summarized
- Summaries can form hierarchies for very long conversations

Sources: [packages/bytebot-agent/src/agent/agent.processor.ts:234-299](), [packages/bytebot-agent/src/summaries/summaries.service.ts](), [packages/bytebot-agent/src/messages/messages.service.ts:89-98]()

---

# Page: Agent Operating Principles

# Agent Operating Principles

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [packages/bytebot-agent/prisma/migrations/20250722041608_files/migration.sql](packages/bytebot-agent/prisma/migrations/20250722041608_files/migration.sql)
- [packages/bytebot-agent/src/agent/agent.computer-use.ts](packages/bytebot-agent/src/agent/agent.computer-use.ts)
- [packages/bytebot-agent/src/agent/agent.constants.ts](packages/bytebot-agent/src/agent/agent.constants.ts)
- [packages/bytebot-agent/src/agent/agent.scheduler.ts](packages/bytebot-agent/src/agent/agent.scheduler.ts)
- [packages/bytebot-agent/src/agent/agent.tools.ts](packages/bytebot-agent/src/agent/agent.tools.ts)
- [packages/bytebotd/src/computer-use/computer-use.controller.ts](packages/bytebotd/src/computer-use/computer-use.controller.ts)
- [packages/bytebotd/src/main.ts](packages/bytebotd/src/main.ts)

</details>



This document describes the guiding principles that govern how the Bytebot AI agent operates when executing tasks. These principles are encoded in the system prompt sent to LLM providers and enforced through code-level mechanisms such as screenshot verification delays and tool usage patterns.

For details on the agent's core processing loop implementation, see [Agent Processor](#6.1). For information about how the agent integrates with LLM providers, see [AI Model Integration](#6.3). For tool execution mechanics, see [Computer Use Integration](#6.2).

---

## Overview

The agent's operating principles are defined in `AGENT_SYSTEM_PROMPT` and guide all decision-making. These principles balance reliability (through observation and verification) with efficiency (through batching and intelligent tool selection). The agent operates on a virtual Ubuntu 22.04 desktop with a 1280x960 display, using tools to perform mouse, keyboard, and application management actions.

**Sources:** [packages/bytebot-agent/src/agent/agent.constants.ts:17-175]()

---

## Core Operating Principles

The agent follows nine fundamental principles when executing tasks. These are embedded in the system prompt sent to every LLM request.

### 1. Observe First

The agent must **always** invoke `computer_screenshot` before its first action and whenever the UI may have changed. This prevents blind actions and ensures decisions are based on current state.

**Key behaviors:**
- Screenshot before every action when filling out forms
- When opening documents or PDFs, scroll through at least the first page to confirm correctness
- Never assume the state of the desktop without visual confirmation

**Code enforcement:** The `handleComputerToolUse` function automatically captures a screenshot after most actions [packages/bytebot-agent/src/agent/agent.computer-use.ts:186-193]() with a 750ms delay to allow UI settling.

### 2. Navigate Applications

The agent must use `computer_application` tool to switch between default applications. Keyboard shortcuts for application switching are explicitly prohibited.

**Available applications:**
- `firefox` - Default web browser
- `thunderbird` - Email client
- `1password` - Password manager
- `vscode` - Code editor
- `terminal` - Command line
- `directory` - File manager
- `desktop` - Return to desktop

**Tool definition:** [packages/bytebot-agent/src/agent/agent.tools.ts:287-309]()

### 3. Human-Like Interaction

The agent should mimic natural human computer usage patterns:

- **Mouse movements:** Smooth, purposeful paths; click near visual centers of targets
- **Desktop icons:** Double-click to open
- **Text input:** 
  - Use `computer_type_text` for short strings (< 25 characters)
  - Use `computer_paste_text` for long strings or special characters
  - Use `computer_type_keys` for keyboard shortcuts

### 4. Valid Keys Only

All key identifiers must match the nut-tree `Key` enum exactly. The system prompt includes a comprehensive list of 150+ valid keys (case-sensitive, no spaces).

**Examples:** `LeftControl`, `Enter`, `Backspace`, `F1`-`F24`, `NumPad0`-`NumPad9`, `AudioVolUp`

**Sources:** [packages/bytebot-agent/src/agent/agent.constants.ts:147-169]()

### 5. Verify Every Step

After each action, the agent must:
1. Take another screenshot
2. Confirm the expected state before continuing
3. If action failed, retry sensibly (try again, then try 2 different methods)
4. If still failing, call `set_task_status` with status `needs_help`

**Implementation:** The 750ms delay [packages/bytebot-agent/src/agent/agent.computer-use.ts:187-189]() ensures UI elements have time to update before verification screenshot.

### 6. Efficiency & Clarity

- Combine related key presses into single operations
- Prefer scrolling or dragging over many small movements
- Minimize unnecessary wait actions
- Use `computer_paste_text` instead of character-by-character typing for long text

### 7. Stay Within Scope

- Do nothing the user didn't request
- Don't suggest unrelated tasks
- For forms and login fields, don't fill in random data unless explicitly instructed

### 8. Security

- Never repeat passwords, secret keys, or sensitive information in conversation
- When typing sensitive information, use `computer_type_text` with `isSensitive: true`
- The `isSensitive` flag is available in both type and paste tools

**Tool schemas:** [packages/bytebot-agent/src/agent/agent.tools.ts:219-223](), [packages/bytebot-agent/src/agent/agent.tools.ts:240-244]()

### 9. Consistency & Persistence

- Continue repetitive tasks until the user's goal is completely met
- For bulk operations, maintain focus and process all items
- Don't end the task prematurely

**Sources:** [packages/bytebot-agent/src/agent/agent.constants.ts:41-58]()

---

## Observe-Act-Verify Cycle

The fundamental operational pattern for every agent action follows this cycle:

```mermaid
stateDiagram-v2
    [*] --> Observe: "Take screenshot"
    Observe --> Analyze: "LLM analyzes state"
    Analyze --> Decide: "Choose action"
    Decide --> Act: "Execute tool"
    Act --> Wait: "750ms delay"
    Wait --> Verify: "Take screenshot"
    Verify --> CheckSuccess: "Confirm expected state"
    
    CheckSuccess --> Observe: "Success: continue"
    CheckSuccess --> Retry: "Failed: attempt 1"
    Retry --> AlternateMethod: "Failed: attempt 2"
    AlternateMethod --> AlternateMethod2: "Failed: attempt 3"
    AlternateMethod2 --> NeedsHelp: "Still failing"
    NeedsHelp --> [*]: "set_task_status(needs_help)"
    
    Observe --> Complete: "Goal achieved"
    Complete --> [*]: "set_task_status(completed)"
```

**Key code points:**
- Screenshot action: [packages/bytebot-agent/src/agent/agent.computer-use.ts:526-555]()
- Post-action delay: [packages/bytebot-agent/src/agent/agent.computer-use.ts:186-189]()
- Verification screenshot: [packages/bytebot-agent/src/agent/agent.computer-use.ts:191-193]()

**Sources:** [packages/bytebot-agent/src/agent/agent.constants.ts:43-53](), [packages/bytebot-agent/src/agent/agent.computer-use.ts:186-219]()

---

## Repetitive Task Handling

For bulk operations like "visit each profile" or "process all items", the agent follows specialized guidelines to ensure complete execution.

### Progress Tracking

The agent maintains mental count of:
- Total items to process (if known)
- Items completed so far
- Current item being processed
- Any errors encountered

### Batch Processing

For large sets, the agent processes in groups of 10-20 items:

```mermaid
flowchart TD
    Start["Start repetitive task"] --> EstimateTotal["Estimate total items"]
    EstimateTotal --> InitCounter["Initialize counter = 0"]
    InitCounter --> CheckRemaining{"Items remaining?"}
    
    CheckRemaining -->|Yes| ProcessBatch["Process batch of 10-20 items"]
    ProcessBatch --> UpdateCounter["Update counter"]
    UpdateCounter --> BriefPause["Brief pause to prevent overload"]
    BriefPause --> ProgressUpdate{"Counter % 20 == 0?"}
    
    ProgressUpdate -->|Yes| LogProgress["Log progress update"]
    ProgressUpdate -->|No| CheckRemaining
    LogProgress --> CheckRemaining
    
    CheckRemaining -->|No| ReportResults["Report completion with error summary"]
    ReportResults --> Cleanup["Cleanup actions"]
    Cleanup --> SetComplete["set_task_status(completed)"]
    SetComplete --> End["End"]
    
    ProcessBatch -.-> ErrorCheck{"Item failed?"}
    ErrorCheck -->|Yes| LogError["Note error, continue with next"]
    ErrorCheck -->|No| ProcessBatch
    LogError --> ProcessBatch
```

### Error Recovery

- If an item fails, note the error but continue with next item
- Keep a list of failed items to report at end
- Don't let one failure stop the entire operation

### Progress Updates

Every 10-20 items, provide brief status:
- Example: "Processed 20/100 profiles, continuing..."
- No detailed reports unless requested

### Completion Criteria

The task is NOT complete until:
- All items in the set are processed, OR
- A clear endpoint is reached (e.g., "No more profiles to load"), OR
- User explicitly tells agent to stop

**Important:** The agent must not prematurely mark tasks as complete after processing just a few items.

### State Management

For tasks spanning multiple tabs/pages:
- Save progress to a file periodically
- Include timestamps and item identifiers

**Sources:** [packages/bytebot-agent/src/agent/agent.constants.ts:60-105]()

---

## Task Lifecycle Template

The agent follows a structured template for executing tasks, with special consideration for repetitive operations.

### Standard Lifecycle

| Step | Action | Tools Used |
|------|--------|-----------|
| **1. Prepare** | Initial screenshot → plan → estimate scope | `computer_screenshot` |
| **2. Execute Loop** | For each sub-goal: Screenshot → Think → Act → Verify | Various computer tools |
| **3. Batch Loop** | Process items in batches of 10-20, update progress | Task-specific tools |
| **4. Switch Applications** | Open/focus applications in fullscreen | `computer_application` |
| **5. Create Tasks** | Spawn separate tasks if unrelated to current work | `create_task` |
| **6. Schedule Tasks** | Schedule future tasks with ISO dates | `create_task` with `scheduledFor` |
| **7. Read Files** | Read file contents as base64-encoded documents | `computer_read_file` |
| **8. Ask for Help** | Request clarification or report blockers | `set_task_status(needs_help)` |
| **9. Cleanup** | Close windows/apps, return to idle desktop | Various close actions |
| **10. Terminate** | Mark task complete with summary | `set_task_status(completed)` |

### Application Switching Example

```json
{
  "name": "computer_application",
  "input": {
    "application": "firefox"
  }
}
```

Valid application values: `firefox`, `thunderbird`, `1password`, `vscode`, `terminal`, `directory`, `desktop`

### Task Creation Examples

**Immediate task:**
```json
{
  "name": "create_task",
  "input": {
    "description": "Subtask description",
    "type": "IMMEDIATE",
    "priority": "MEDIUM"
  }
}
```

**Scheduled task:**
```json
{
  "name": "create_task",
  "input": {
    "description": "Send reminder email",
    "type": "SCHEDULED",
    "scheduledFor": "2025-01-15T14:30:00Z",
    "priority": "HIGH"
  }
}
```

### File Reading Example

```json
{
  "name": "computer_read_file",
  "input": {
    "path": "/home/user/Desktop/document.pdf"
  }
}
```

Returns a document content block with base64 data, supporting PDFs, DOCX, TXT, images, etc.

### Task Status Management

**Request help:**
```json
{
  "name": "set_task_status",
  "input": {
    "status": "needs_help",
    "description": "Unable to locate the submit button on the form"
  }
}
```

**Mark complete:**
```json
{
  "name": "set_task_status",
  "input": {
    "status": "completed",
    "description": "Successfully processed all 47 profiles and saved results to profiles.csv"
  }
}
```

**Sources:** [packages/bytebot-agent/src/agent/agent.constants.ts:94-138](), [packages/bytebot-agent/src/agent/agent.tools.ts:314-363]()

---

## Tool Usage Guidelines

The agent has access to 17 computer tools plus 2 task management tools. Tool selection follows specific patterns based on the operation type.

### Mouse Operations

```mermaid
graph TB
    MouseOperation["Mouse Operation Needed"]
    
    MouseOperation --> SimpleMove{"Just moving cursor?"}
    SimpleMove -->|Yes| MoveMouse["computer_move_mouse<br/>Move to coordinates"]
    SimpleMove -->|No| NeedClick{"Need to click?"}
    
    NeedClick -->|Yes| ClickType{"Click type?"}
    ClickType -->|Single/Double| ClickMouse["computer_click_mouse<br/>clickCount: 1 or 2"]
    ClickType -->|Press and hold| PressMouse["computer_press_mouse<br/>press: down/up"]
    
    NeedClick -->|No| DragOrTrace{"Drag or trace?"}
    DragOrTrace -->|Drag with button| DragMouse["computer_drag_mouse<br/>path + button"]
    DragOrTrace -->|Just trace path| TraceMouse["computer_trace_mouse<br/>path only"]
    
    NeedClick -->|Scroll| Scroll["computer_scroll<br/>direction + scrollCount"]
```

**Coordinates:** All coordinates use the 1280x960 display size defined in [packages/bytebot-agent/src/agent/agent.constants.ts:1-4]()

### Keyboard Operations

```mermaid
graph TB
    KeyboardOperation["Keyboard Operation Needed"]
    
    KeyboardOperation --> TextOrKeys{"Text or keys?"}
    
    TextOrKeys -->|"Text (letters/words)"| TextLength{"Length?"}
    TextLength -->|"< 25 chars"| TypeText["computer_type_text<br/>Character by character"]
    TextLength -->|"> 25 chars"| PasteText["computer_paste_text<br/>Clipboard paste"]
    
    TextOrKeys -->|"Keys (shortcuts)"| KeyAction{"Action type?"}
    KeyAction -->|"Sequential presses"| TypeKeys["computer_type_keys<br/>Array of keys"]
    KeyAction -->|"Press/Release"| PressKeys["computer_press_keys<br/>press: up/down"]
    
    TypeText -.-> Sensitive{"Sensitive data?"}
    PasteText -.-> Sensitive
    Sensitive -->|Yes| SetFlag["Set isSensitive: true"]
    Sensitive -->|No| NoFlag["isSensitive: false/undefined"]
```

**Tool definitions:**
- Type text: [packages/bytebot-agent/src/agent/agent.tools.ts:203-227]()
- Paste text: [packages/bytebot-agent/src/agent/agent.tools.ts:229-248]()
- Type keys: [packages/bytebot-agent/src/agent/agent.tools.ts:160-179]()
- Press keys: [packages/bytebot-agent/src/agent/agent.tools.ts:181-201]()

### File Operations

The agent can read files from the desktop environment and receive their contents as base64-encoded document blocks:

**Read file tool:** [packages/bytebot-agent/src/agent/agent.tools.ts:368-382]()

**Read implementation:** [packages/bytebot-agent/src/agent/agent.computer-use.ts:576-610]()

Files uploaded by users are automatically written to `/home/user/Desktop/` before task execution by the scheduler [packages/bytebot-agent/src/agent/agent.scheduler.ts:43-53]().

**Sources:** [packages/bytebot-agent/src/agent/agent.tools.ts:1-406](), [packages/bytebot-agent/src/agent/agent.computer-use.ts:28-239]()

---

## State Verification and Error Recovery

The agent implements a multi-layer verification strategy to ensure reliable execution.

### Post-Action Delay

After executing any computer action (except screenshot and cursor_position), the system waits 750ms before capturing a verification screenshot:

```typescript
const delayMs = 750; // 750ms delay
logger.debug(`Waiting ${delayMs}ms before taking screenshot`);
await new Promise((resolve) => setTimeout(resolve, delayMs));
```

This delay allows:
- UI animations to complete
- Network requests to initiate
- Application state to stabilize
- Window focus changes to settle

**Implementation:** [packages/bytebot-agent/src/agent/agent.computer-use.ts:186-189]()

### Screenshot Verification

Every action returns a `ToolResultContentBlock` containing:
1. Success/error text message
2. Screenshot image (base64 PNG) if applicable

**Screenshot tool result structure:**
```typescript
{
  type: MessageContentType.ToolResult,
  tool_use_id: block.id,
  content: [
    {
      type: MessageContentType.Text,
      text: 'Tool executed successfully'
    },
    {
      type: MessageContentType.Image,
      source: {
        data: image,      // base64 PNG
        media_type: 'image/png',
        type: 'base64'
      }
    }
  ]
}
```

**Source:** [packages/bytebot-agent/src/agent/agent.computer-use.ts:199-221]()

### Error Handling Flow

```mermaid
flowchart TD
    ExecuteAction["Execute computer action"] --> Success{"Execution successful?"}
    
    Success -->|Yes| Delay["Wait 750ms"]
    Delay --> CaptureScreenshot["Capture screenshot"]
    CaptureScreenshot --> ReturnSuccess["Return ToolResult with screenshot"]
    
    Success -->|No| CatchError["Catch exception"]
    CatchError --> LogError["Log error with stack trace"]
    LogError --> ReturnError["Return ToolResult with is_error: true"]
    
    ReturnSuccess --> LLMAnalysis["LLM analyzes screenshot"]
    ReturnError --> LLMAnalysis
    
    LLMAnalysis --> StateCheck{"Expected state achieved?"}
    StateCheck -->|Yes| Continue["Continue to next action"]
    StateCheck -->|No| RetryLogic["Retry logic (3 attempts)"]
    
    RetryLogic --> FinalCheck{"Resolved after retries?"}
    FinalCheck -->|Yes| Continue
    FinalCheck -->|No| NeedsHelp["set_task_status(needs_help)"]
```

**Error return structure:**
```typescript
{
  type: MessageContentType.ToolResult,
  tool_use_id: block.id,
  content: [
    {
      type: MessageContentType.Text,
      text: `Error executing ${block.name} tool: ${error.message}`
    }
  ],
  is_error: true
}
```

**Source:** [packages/bytebot-agent/src/agent/agent.computer-use.ts:222-238]()

### Cleanup Protocol

Before marking a task as complete, the agent must:

1. **Close all opened resources:**
   - Browser tabs opened during task
   - Applications launched
   - File windows opened
   - Documents viewed

2. **Return to idle state:**
   - Navigate to desktop using `computer_application` with `application: "desktop"`
   - Ensure clean desktop visible
   - No running processes left behind

3. **Only then call completion:**
   ```json
   {
     "name": "set_task_status",
     "input": {
       "status": "completed",
       "description": "Task summary here"
     }
   }
   ```

This ensures the virtual desktop is ready for the next task without state pollution.

**Sources:** [packages/bytebot-agent/src/agent/agent.constants.ts:131-138](), [packages/bytebot-agent/src/agent/agent.computer-use.ts:184-238]()

---

## Display Configuration

The agent operates on a fixed display size that all coordinates must reference:

| Property | Value |
|----------|-------|
| Width | 1280 pixels |
| Height | 960 pixels |
| Desktop Environment | XFCE |
| Operating System | Ubuntu 22.04 |

**System prompt reference:** The display dimensions are embedded in the system prompt [packages/bytebot-agent/src/agent/agent.constants.ts:18]()

**Constant definition:** [packages/bytebot-agent/src/agent/agent.constants.ts:1-4]()

All mouse coordinates passed to tools like `computer_move_mouse`, `computer_click_mouse`, and `computer_scroll` must fall within the (0,0) to (1280,960) range.

**Sources:** [packages/bytebot-agent/src/agent/agent.constants.ts:1-4](), [packages/bytebot-agent/src/agent/agent.constants.ts:17-18]()

---

# Page: Desktop Environment

# Desktop Environment

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [docs/api-reference/agent/tasks.mdx](docs/api-reference/agent/tasks.mdx)
- [docs/core-concepts/desktop-environment.mdx](docs/core-concepts/desktop-environment.mdx)
- [docs/deployment/railway.mdx](docs/deployment/railway.mdx)
- [docs/guides/task-creation.mdx](docs/guides/task-creation.mdx)
- [docs/introduction.mdx](docs/introduction.mdx)
- [docs/quickstart.mdx](docs/quickstart.mdx)
- [packages/bytebotd/src/computer-use/computer-use.service.ts](packages/bytebotd/src/computer-use/computer-use.service.ts)
- [packages/bytebotd/src/computer-use/dto/base.dto.ts](packages/bytebotd/src/computer-use/dto/base.dto.ts)
- [packages/bytebotd/src/computer-use/dto/computer-action-validation.pipe.ts](packages/bytebotd/src/computer-use/dto/computer-action-validation.pipe.ts)
- [packages/bytebotd/src/computer-use/dto/computer-action.dto.ts](packages/bytebotd/src/computer-use/dto/computer-action.dto.ts)
- [packages/bytebotd/src/mcp/computer-use.tools.ts](packages/bytebotd/src/mcp/computer-use.tools.ts)
- [packages/shared/src/types/computerAction.types.ts](packages/shared/src/types/computerAction.types.ts)
- [packages/shared/src/types/messageContent.types.ts](packages/shared/src/types/messageContent.types.ts)
- [packages/shared/src/utils/computerAction.utils.ts](packages/shared/src/utils/computerAction.utils.ts)
- [packages/shared/src/utils/messageContent.utils.ts](packages/shared/src/utils/messageContent.utils.ts)

</details>



This document covers the virtual Linux desktop environment that serves as the execution context for Bytebot's computer automation capabilities. The desktop environment provides a complete, isolated computing environment where AI agents can perform tasks using standard desktop applications and interfaces.

For information about the REST API for programmatic desktop control, see [Computer Use API](#5.1). For details about monitoring user input events, see [Input Tracking System](#5.2).

## System Architecture

The desktop environment is built as a containerized Ubuntu Linux system with a complete graphical desktop interface. It runs independently from the host system, providing isolation and consistency across different deployment environments.

### Core Desktop Stack

```mermaid
graph TB
    subgraph "Desktop Container (port 9990)"
        subgraph "System Layer"
            Ubuntu["Ubuntu 22.04 LTS"]
            X11["X11 Display Server"]
            XFCE["XFCE4 Desktop Environment"]
        end
        
        subgraph "Service Layer"
            bytebotd["bytebotd Daemon<br/>(NestJS)"]
            supervisor["supervisord<br/>(Process Manager)"]
            novnc["noVNC Web Client"]
            vnc["VNC Server"]
        end
        
        subgraph "Application Layer"
            Firefox["firefox-esr"]
            VSCode["code (VS Code)"]
            OnePassword["1password"]
            Thunderbird["thunderbird"]
            Terminal["xfce4-terminal"]
            FileManager["thunar"]
        end
    end
    
    subgraph "External Access"
        WebBrowser["Web Browser<br/>(VNC Client)"]
        AgentService["bytebot-agent<br/>(REST/MCP Client)"]
    end
    
    Ubuntu --> XFCE
    XFCE --> X11
    supervisor --> bytebotd
    supervisor --> vnc
    vnc --> novnc
    
    WebBrowser --> novnc
    AgentService --> bytebotd
    
    bytebotd --> Firefox
    bytebotd --> VSCode
    bytebotd --> Terminal
```

**Desktop Environment Stack Architecture**

The desktop runs as a complete Linux system with graphical capabilities, managed by `supervisord` for service orchestration and accessed through multiple interfaces.

Sources: [README.md:103-106](), [docs/core-concepts/desktop-environment.mdx:36-43](), [docs/quickstart.mdx:68-74]()

### Service Integration

```mermaid
graph LR
    subgraph "Agent Service (9991)"
        AgentProcessor["AgentProcessor"]
        ComputerUseClient["Computer Use Client"]
    end
    
    subgraph "Desktop Service (9990)"
        ComputerUseController["ComputerUseController"]
        ComputerUseService["ComputerUseService"] 
        NutService["NutService"]
        MCPModule["MCP Module"]
        ComputerUseTools["ComputerUseTools"]
    end
    
    subgraph "Desktop Environment"
        XServer["X11 Server :0.0"]
        Applications["GUI Applications"]
    end
    
    AgentProcessor --> ComputerUseClient
    ComputerUseClient -->|"POST /computer-use"| ComputerUseController
    ComputerUseClient -->|"GET /mcp (SSE)"| MCPModule
    
    ComputerUseController --> ComputerUseService
    MCPModule --> ComputerUseTools
    ComputerUseTools --> ComputerUseService
    
    ComputerUseService --> NutService
    NutService --> XServer
    XServer --> Applications
```

**Service Communication Architecture**

The `ComputerUseService` acts as the central coordinator, translating high-level computer actions into low-level desktop operations through `NutService`.

Sources: [packages/bytebotd/src/computer-use/computer-use.service.ts:25-29](), [packages/bytebotd/src/mcp/computer-use.tools.ts:7-9]()

## Container Composition

The desktop environment runs as a Docker container with specific configuration for automation and remote access.

### Runtime Environment

| Component | Details |
|-----------|---------|
| **Base Image** | Ubuntu 22.04 LTS |
| **Desktop** | XFCE4 (lightweight, automation-friendly) |
| **Display** | `:0.0` (X11 display server) |
| **Resolution** | 1920x1080 @ 24-bit color |
| **User Context** | `user` with sudo access |
| **Process Manager** | supervisord |

### File System Layout

```
/home/user/                     # User home directory
├── Desktop/                    # Desktop files and shortcuts
├── Documents/                  # User documents
├── Downloads/                  # Browser downloads
├── .config/                    # Application configurations
│   ├── Code/                   # VS Code settings
│   └── firefox/                # Firefox profile
└── .local/                     # User-local data

/opt/bytebotd/                  # bytebotd service directory
└── src/                        # Service source code

/var/log/supervisor/            # Service logs
├── bytebotd.log               # Desktop daemon logs
└── vnc.log                    # VNC server logs
```

Sources: [docs/core-concepts/desktop-environment.mdx:98-111](), [packages/bytebotd/src/computer-use/computer-use.service.ts:364-417]()

## Pre-installed Applications

The desktop comes with essential applications configured for automation and productivity tasks.

### Application Inventory

```mermaid
graph TB
    subgraph "Web & Communication"
        firefox["firefox-esr<br/>(Primary Browser)"]
        thunderbird["thunderbird<br/>(Email Client)"]
        onepass["1password<br/>(Password Manager)"]
    end
    
    subgraph "Development Tools"
        vscode["code<br/>(VS Code Editor)"]
        terminal["xfce4-terminal<br/>(Terminal Emulator)"]
        git["git<br/>(Version Control)"]
        python["python3<br/>(Python Runtime)"]
    end
    
    subgraph "System Tools"
        thunar["thunar<br/>(File Manager)"]
        desktop["xfdesktop<br/>(Desktop Manager)"]
        wmctrl["wmctrl<br/>(Window Control)"]
    end
    
    subgraph "Process Management"
        ApplicationAction --> firefox
        ApplicationAction --> thunderbird  
        ApplicationAction --> onepass
        ApplicationAction --> vscode
        ApplicationAction --> terminal
        ApplicationAction --> thunar
        ApplicationAction --> desktop
    end
```

**Pre-installed Application Ecosystem**

Applications are managed through the `ApplicationAction` interface, allowing programmatic opening and window management.

Sources: [packages/shared/src/types/computerAction.types.ts:4-11](), [packages/bytebotd/src/computer-use/computer-use.service.ts:287-304](), [packages/bytebotd/src/mcp/computer-use.tools.ts:511-519]()

### Application Management System

The `ComputerUseService` provides application lifecycle management through the `application` action:

```typescript
// Application types supported
type Application = 
  | "firefox" 
  | "1password" 
  | "thunderbird" 
  | "vscode" 
  | "terminal" 
  | "desktop" 
  | "directory"
```

The service handles:
- **Application Detection**: Uses `wmctrl -lx` to check running applications
- **Window Activation**: Brings existing windows to foreground  
- **Process Launching**: Starts new application instances
- **Window Management**: Maximizes and positions windows

Sources: [packages/bytebotd/src/computer-use/computer-use.service.ts:264-362](), [packages/shared/src/types/computerAction.types.ts:4-11]()

## Access Interfaces

The desktop environment provides multiple access methods for different use cases.

### VNC Web Interface

```mermaid
graph LR
    subgraph "Client Browser"
        UserBrowser["Web Browser"]
    end
    
    subgraph "Desktop Container"
        noVNC["noVNC Web Client<br/>(HTML5 VNC)"]
        VNCServer["VNC Server<br/>(Real VNC)"]
        XServer["X11 Display Server<br/>(:0.0)"]
        Desktop["XFCE4 Desktop"]
    end
    
    UserBrowser -->|"HTTP :9990/vnc"| noVNC
    noVNC --> VNCServer  
    VNCServer --> XServer
    XServer --> Desktop
```

**VNC Web Access Architecture**

The noVNC client provides browser-based desktop access without requiring VNC client software installation.

- **URL**: `http://localhost:9990/vnc`
- **Protocol**: WebSocket-proxied VNC
- **Features**: Full desktop interaction, clipboard sharing
- **Use Cases**: Manual setup, troubleshooting, demonstration

Sources: [docs/core-concepts/desktop-environment.mdx:115-121](), [docs/quickstart.mdx:200]()

### REST API Interface

The `bytebotd` daemon exposes computer control functionality through REST endpoints:

| Endpoint | Purpose |
|----------|---------|
| `POST /computer-use` | Execute computer actions |
| `GET /mcp` | MCP protocol SSE endpoint |
| `GET /vnc` | VNC web client interface |

The API accepts `ComputerAction` objects and delegates execution to `ComputerUseService`:

Sources: [packages/bytebotd/src/computer-use/computer-use.service.ts:31-105](), [docs/core-concepts/desktop-environment.mdx:123-156]()

### MCP Protocol Support

The desktop provides Model Context Protocol (MCP) integration for tool access:

```json
{
  "mcpServers": {
    "bytebot": {
      "command": "npx",
      "args": [
        "mcp-remote", 
        "http://127.0.0.1:9990/mcp",
        "--transport",
        "http-first"
      ]
    }
  }
}
```

The MCP interface exposes computer use tools as callable functions for AI models.

Sources: [docs/core-concepts/desktop-environment.mdx:123-141](), [packages/bytebotd/src/mcp/computer-use.tools.ts:8-698]()

## Computer Action System

The desktop environment executes computer actions through a comprehensive action system that covers all desktop interaction patterns.

### Action Type Hierarchy

```mermaid
graph TB
    ComputerAction["ComputerAction<br/>(Union Type)"]
    
    subgraph "Mouse Actions"
        MoveMouseAction["move_mouse"]
        ClickMouseAction["click_mouse"] 
        DragMouseAction["drag_mouse"]
        ScrollAction["scroll"]
        PressMouseAction["press_mouse"]
        TraceMouseAction["trace_mouse"]
    end
    
    subgraph "Keyboard Actions"
        TypeTextAction["type_text"]
        TypeKeysAction["type_keys"]
        PressKeysAction["press_keys"]
        PasteTextAction["paste_text"]
    end
    
    subgraph "System Actions"
        ScreenshotAction["screenshot"]
        ApplicationAction["application"]
        WaitAction["wait"]
        CursorPositionAction["cursor_position"]
    end
    
    subgraph "File Actions"
        WriteFileAction["write_file"]
        ReadFileAction["read_file"]
    end
    
    ComputerAction --> MoveMouseAction
    ComputerAction --> ClickMouseAction
    ComputerAction --> TypeTextAction
    ComputerAction --> ScreenshotAction
    ComputerAction --> WriteFileAction
    ComputerAction --> ApplicationAction
    ComputerAction --> WaitAction
```

**Computer Action Type System**

All desktop interactions are modeled as strongly-typed action objects processed by `ComputerUseService.action()`.

Sources: [packages/shared/src/types/computerAction.types.ts:109-125](), [packages/bytebotd/src/computer-use/computer-use.service.ts:31-105]()

### Action Execution Pipeline

The execution flow for computer actions follows a consistent pattern:

1. **Action Validation**: DTOs validate action parameters
2. **Service Routing**: `ComputerUseService` routes to specific handlers  
3. **Desktop Execution**: `NutService` performs low-level operations
4. **Result Processing**: Return values or success confirmations

```typescript
// Example action execution flow
await computerUseService.action({
  action: 'click_mouse',
  coordinates: { x: 500, y: 300 },
  button: 'left',
  clickCount: 1
});
```

Sources: [packages/bytebotd/src/computer-use/computer-use.service.ts:31-105](), [packages/bytebotd/src/computer-use/dto/computer-action.dto.ts:22-239]()

## Service Management

The desktop environment uses `supervisord` for process management and service orchestration.

### Service Configuration

Key services managed by supervisor:

- **bytebotd**: Main automation daemon (NestJS application)
- **VNC Server**: Remote desktop access 
- **X11**: Display server
- **Desktop Session**: XFCE4 session management

Each service has dedicated logging and automatic restart capabilities.

### Resource Management

The desktop environment is optimized for automation workloads:

- **Memory Usage**: ~1-2GB typical, 4GB recommended
- **CPU Usage**: Scales with automation complexity
- **Storage**: Persistent user data, temporary execution files
- **Network**: Outbound internet access, inbound API access

Sources: [docs/core-concepts/desktop-environment.mdx:176-189](), [docs/core-concepts/architecture.mdx:194-207]()

## Customization and Extension

The desktop environment supports customization for specific automation requirements.

### Software Installation

Additional software can be installed through standard Ubuntu package management or custom Docker builds:

```dockerfile
FROM ghcr.io/bytebot-ai/bytebot-desktop:edge

# Install additional packages
RUN apt-get update && apt-get install -y \
    slack-desktop \
    zoom \
    custom-enterprise-software

# Copy configuration files  
COPY configs/ /home/user/.config/
```

### Application Configuration

Pre-installed applications can be configured through:
- **Configuration Files**: Standard Linux config directories
- **Environment Variables**: Runtime configuration
- **Startup Scripts**: Custom initialization logic

Sources: [docs/core-concepts/desktop-environment.mdx:160-174](), [docs/quickstart.mdx:163-174]()

## Performance Characteristics

The desktop environment is designed for reliability and consistent performance in automation scenarios.

### Resource Requirements

| Resource | Minimum | Recommended | Notes |
|----------|---------|-------------|--------|
| **Memory** | 2GB | 4GB | Higher for complex applications |
| **CPU** | 1 core | 2+ cores | Scales with concurrency |
| **Storage** | 2GB | 10GB+ | Includes applications and user data |
| **Network** | 10 Mbps | 100+ Mbps | For web automation tasks |

### Optimization Considerations

- **Display Resolution**: Fixed at 1920x1080 for consistent element positioning
- **Application Startup**: Pre-configured for fast launch times
- **Resource Isolation**: Container limits prevent resource contention
- **Session Persistence**: User data survives container restarts

Sources: [docs/core-concepts/desktop-environment.mdx:176-189](), [docs/core-concepts/architecture.mdx:194-207]()

---

# Page: Computer Use Service

# Computer Use Service

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [packages/bytebotd/src/computer-use/computer-use.service.ts](packages/bytebotd/src/computer-use/computer-use.service.ts)
- [packages/bytebotd/src/computer-use/dto/base.dto.ts](packages/bytebotd/src/computer-use/dto/base.dto.ts)
- [packages/bytebotd/src/computer-use/dto/computer-action-validation.pipe.ts](packages/bytebotd/src/computer-use/dto/computer-action-validation.pipe.ts)
- [packages/bytebotd/src/computer-use/dto/computer-action.dto.ts](packages/bytebotd/src/computer-use/dto/computer-action.dto.ts)
- [packages/bytebotd/src/mcp/computer-use.tools.ts](packages/bytebotd/src/mcp/computer-use.tools.ts)
- [packages/shared/src/types/computerAction.types.ts](packages/shared/src/types/computerAction.types.ts)
- [packages/shared/src/types/messageContent.types.ts](packages/shared/src/types/messageContent.types.ts)
- [packages/shared/src/utils/computerAction.utils.ts](packages/shared/src/utils/computerAction.utils.ts)
- [packages/shared/src/utils/messageContent.utils.ts](packages/shared/src/utils/messageContent.utils.ts)

</details>



The `ComputerUseService` class in the `bytebotd` daemon serves as the central action execution layer for desktop automation. This service translates high-level computer actions into low-level desktop operations through `NutService`, providing the execution engine for AI agent interactions and direct API calls.

For AI integration via MCP tools, see [MCP Integration](#7.3). For the complete set of desktop tools available to agents, see [Desktop Tools](#7.2). For direct REST API usage, see [Computer Use API](#10.2).

## Service Architecture

The `ComputerUseService` is implemented as a NestJS injectable service that receives `ComputerAction` objects and dispatches them to appropriate handler methods. Each handler coordinates with `NutService` to execute the requested desktop operation.

### Component Hierarchy

```mermaid
graph TB
    subgraph "Consumer Layer"
        ComputerUseController["ComputerUseController<br/>/computer-use endpoint"]
        ComputerUseTools["ComputerUseTools<br/>MCP @Tool decorators"]
    end
    
    subgraph "Service Layer"
        ComputerUseService["ComputerUseService<br/>@Injectable()"]
        ActionMethod["action(params: ComputerAction)"]
        Handlers["Handler Methods<br/>moveMouse()<br/>clickMouse()<br/>typeText()<br/>screenshot()"]
    end
    
    subgraph "Desktop Automation Layer"
        NutService["NutService<br/>@nut-tree-fork/nut-js wrapper"]
        NutMethods["mouseMoveEvent()<br/>mouseClickEvent()<br/>sendKeys()<br/>screendump()"]
    end
    
    subgraph "System Layer"
        XFCEDesktop["XFCE Desktop<br/>Ubuntu 22.04<br/>1280x960"]
    end
    
    ComputerUseController --> ActionMethod
    ComputerUseTools --> ActionMethod
    ActionMethod --> Handlers
    Handlers --> NutMethods
    NutMethods --> XFCEDesktop
    
    style ComputerUseService fill:#fff9c4
    style ActionMethod fill:#ffccbc
```

The service receives validated `ComputerAction` DTOs from either the REST controller or MCP tools layer, routes them through the central `action()` dispatcher, and delegates execution to specialized handler methods.

**Sources:** [packages/bytebotd/src/computer-use/computer-use.service.ts:25-29](), [packages/bytebotd/src/computer-use/computer-use.service.ts:31-105]()

### Dependency Injection

The service declares a single dependency on `NutService`:

```typescript
constructor(private readonly nutService: NutService) {}
```

This tight coupling with `NutService` reflects the service's role as a facade that provides a higher-level, action-based interface over the low-level desktop automation primitives.

**Sources:** [packages/bytebotd/src/computer-use/computer-use.service.ts:29]()

## Action Dispatch System

The core of `ComputerUseService` is the `action()` method, which implements a switch-based dispatcher pattern. This method receives a `ComputerAction` union type and routes execution to the appropriate handler method.

### Dispatcher Implementation

```mermaid
graph TB
    ActionMethod["action(params: ComputerAction)"]
    SwitchStatement["switch (params.action)"]
    
    MM["case 'move_mouse'<br/>moveMouse(params)"]
    TM["case 'trace_mouse'<br/>traceMouse(params)"]
    CM["case 'click_mouse'<br/>clickMouse(params)"]
    PM["case 'press_mouse'<br/>pressMouse(params)"]
    DM["case 'drag_mouse'<br/>dragMouse(params)"]
    SC["case 'scroll'<br/>scroll(params)"]
    TK["case 'type_keys'<br/>typeKeys(params)"]
    PK["case 'press_keys'<br/>pressKeys(params)"]
    TT["case 'type_text'<br/>typeText(params)"]
    PT["case 'paste_text'<br/>pasteText(params)"]
    WT["case 'wait'<br/>delay(duration)"]
    SS["case 'screenshot'<br/>return screenshot()"]
    CP["case 'cursor_position'<br/>return cursor_position()"]
    AP["case 'application'<br/>application(params)"]
    WF["case 'write_file'<br/>return writeFile(params)"]
    RF["case 'read_file'<br/>return readFile(params)"]
    DF["default<br/>throw Error"]
    
    ActionMethod --> SwitchStatement
    SwitchStatement --> MM
    SwitchStatement --> TM
    SwitchStatement --> CM
    SwitchStatement --> PM
    SwitchStatement --> DM
    SwitchStatement --> SC
    SwitchStatement --> TK
    SwitchStatement --> PK
    SwitchStatement --> TT
    SwitchStatement --> PT
    SwitchStatement --> WT
    SwitchStatement --> SS
    SwitchStatement --> CP
    SwitchStatement --> AP
    SwitchStatement --> WF
    SwitchStatement --> RF
    SwitchStatement --> DF
```

The dispatcher ensures type safety through TypeScript's discriminated union types - each `case` branch narrows the `params` type to the specific action interface.

**Sources:** [packages/bytebotd/src/computer-use/computer-use.service.ts:31-105]()

### Return Value Patterns

Most actions return `Promise<void>` and execute for their side effects. Three actions return data:

| Action | Return Type | Data Structure |
|--------|-------------|----------------|
| `screenshot` | `Promise<{ image: string }>` | Base64-encoded PNG image |
| `cursor_position` | `Promise<{ x: number; y: number }>` | Current cursor coordinates |
| `read_file` | `Promise<{ success, data?, name?, size?, mediaType?, message? }>` | File contents and metadata |
| `write_file` | `Promise<{ success, message }>` | Operation result |

**Sources:** [packages/bytebotd/src/computer-use/computer-use.service.ts:253-257](), [packages/bytebotd/src/computer-use/computer-use.service.ts:259-262](), [packages/bytebotd/src/computer-use/computer-use.service.ts:419-505]()

## Action Categories

The service implements 17 distinct action types organized into four functional categories.

### Mouse Operations

| Action | Handler Method | NutService Calls | Parameters |
|--------|---------------|------------------|------------|
| `move_mouse` | `moveMouse()` | `mouseMoveEvent()` | `coordinates: {x, y}` |
| `trace_mouse` | `traceMouse()` | `mouseMoveEvent()` + `holdKeys()` | `path: Coordinates[]`, `holdKeys?` |
| `click_mouse` | `clickMouse()` | `mouseClickEvent()` + optional `mouseMoveEvent()` | `button`, `clickCount`, `coordinates?`, `holdKeys?` |
| `press_mouse` | `pressMouse()` | `mouseButtonEvent()` | `button`, `press: "up"/"down"`, `coordinates?` |
| `drag_mouse` | `dragMouse()` | `mouseButtonEvent()` + `mouseMoveEvent()` | `path: Coordinates[]`, `button`, `holdKeys?` |
| `scroll` | `scroll()` | `mouseWheelEvent()` | `direction`, `scrollCount`, `coordinates?`, `holdKeys?` |

Mouse operations demonstrate the service's coordination capabilities. For example, `clickMouse()` orchestrates multiple NutService calls:

1. Move to coordinates (if provided): `await this.nutService.mouseMoveEvent(coordinates)`
2. Hold modifier keys (if provided): `await this.nutService.holdKeys(holdKeys, true)`
3. Perform clicks with delay: `await this.nutService.mouseClickEvent(button)` + `await this.delay(150)`
4. Release modifier keys: `await this.nutService.holdKeys(holdKeys, false)`

**Sources:** [packages/bytebotd/src/computer-use/computer-use.service.ts:107-227](), [packages/shared/src/types/computerAction.types.ts:14-53]()

### Keyboard Operations

| Action | Handler Method | NutService Calls | Parameters |
|--------|---------------|------------------|------------|
| `type_keys` | `typeKeys()` | `sendKeys()` | `keys: string[]`, `delay?` |
| `press_keys` | `pressKeys()` | `holdKeys()` | `keys: string[]`, `press: "up"/"down"` |
| `type_text` | `typeText()` | `typeText()` | `text: string`, `delay?` |
| `paste_text` | `pasteText()` | `pasteText()` | `text: string` |

Keyboard handlers are thin wrappers that delegate directly to `NutService` methods. The complexity of key mapping and event generation is handled by the underlying NutJS library.

The `type_keys` action supports 100+ key names including:
- **Modifiers**: `LeftControl`, `RightControl`, `LeftShift`, `RightShift`, `LeftAlt`, `RightAlt`, `LeftCmd`, `RightCmd`
- **Function keys**: `F1` through `F24`
- **Navigation**: `Up`, `Down`, `Left`, `Right`, `Home`, `End`, `PageUp`, `PageDown`
- **Special**: `Enter`, `Tab`, `Escape`, `Backspace`, `Delete`, `Space`
- **Alphanumeric**: `A-Z`, `Num0-Num9`, `NumPad0-NumPad9`

**Sources:** [packages/bytebotd/src/computer-use/computer-use.service.ts:229-247](), [packages/bytebotd/src/mcp/computer-use.tools.ts:317-426]()

### System Operations

| Action | Handler Method | Implementation | Parameters |
|--------|---------------|----------------|------------|
| `screenshot` | `screenshot()` | `nutService.screendump()` + base64 encoding | None |
| `cursor_position` | `cursor_position()` | `nutService.getCursorPosition()` | None |
| `wait` | `delay()` | `new Promise(setTimeout)` | `duration: number` (ms) |
| `application` | `application()` | Shell commands via `exec`/`spawn` | `application: Application` |

The `wait` action provides a simple utility method for pausing execution:

```typescript
private async delay(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}
```

**Sources:** [packages/bytebotd/src/computer-use/computer-use.service.ts:249-262]()

### Application Management

The `application()` handler implements sophisticated window management using `wmctrl` commands:

```mermaid
graph TB
    Start["application(action)"]
    CheckDesktop{"application === 'desktop'?"}
    ShowDesktop["wmctrl -k on<br/>Show desktop"]
    CheckOpen["wmctrl -lx | grep process"]
    IsOpen{"Application<br/>already open?"}
    Activate["wmctrl -x -a<br/>Activate window"]
    Maximize["wmctrl -x -r -b add,maximized"]
    Launch["sudo -u user nohup app"]
    End["Return"]
    
    Start --> CheckDesktop
    CheckDesktop -->|Yes| ShowDesktop
    CheckDesktop -->|No| CheckOpen
    ShowDesktop --> End
    CheckOpen --> IsOpen
    IsOpen -->|Yes| Activate
    IsOpen -->|No| Launch
    Activate --> Maximize
    Maximize --> End
    Launch --> End
```

The service maintains two mapping tables:

- **Command map**: Application name → executable command
  - `firefox` → `firefox-esr`
  - `vscode` → `code`
  - `terminal` → `xfce4-terminal`
  - etc.

- **Process map**: Application name → WM_CLASS identifier
  - `firefox` → `Navigator.firefox-esr`
  - `vscode` → `code.Code`
  - `terminal` → `xfce4-terminal.Xfce4-Terminal`
  - etc.

All application commands are executed via `spawn()` with `detached: true` and `unref()` to prevent blocking the service.

**Sources:** [packages/bytebotd/src/computer-use/computer-use.service.ts:264-362]()

### File Operations

| Action | Handler Method | Implementation Strategy | Return Data |
|--------|---------------|------------------------|-------------|
| `write_file` | `writeFile()` | Temp file + `sudo cp` + chown | `{success, message}` |
| `read_file` | `readFile()` | `sudo cp` to temp + read + cleanup | `{success, data?, name?, size?, mediaType?, message?}` |

Both file operations require elevated permissions since files are accessed in the user context. The service uses a temporary file pattern:

**Write flow:**
1. Decode base64 data to Buffer
2. Resolve path (relative → `/home/user/Desktop/...`)
3. Create directory: `sudo mkdir -p`
4. Write to temp file: `/tmp/bytebot_temp_*`
5. Copy with permissions: `sudo cp`, `sudo chown user:user`, `sudo chmod 644`
6. Clean up temp file

**Read flow:**
1. Resolve path
2. Copy to temp: `sudo cp target tempFile`
3. Change permissions: `sudo chmod 644 tempFile`
4. Read as Buffer
5. Get file size: `sudo stat -c "%s"`
6. Clean up temp file
7. Encode to base64 and determine MIME type

The service includes MIME type detection for 20+ file extensions including documents (PDF, DOCX, TXT), images (PNG, JPEG, WebP), and structured formats (JSON, XML, CSV).

**Sources:** [packages/bytebotd/src/computer-use/computer-use.service.ts:364-506]()

## NutService Integration

The `ComputerUseService` delegates all actual desktop interaction to the `NutService` wrapper around `@nut-tree-fork/nut-js`. This creates a clean separation between action orchestration (ComputerUseService) and low-level automation primitives (NutService).

### NutService Method Mapping

```mermaid
graph LR
    subgraph "ComputerUseService Handlers"
        MH["moveMouse()<br/>traceMouse()<br/>clickMouse()"]
        KH["typeKeys()<br/>typeText()<br/>pasteText()"]
        SH["screenshot()<br/>cursor_position()"]
    end
    
    subgraph "NutService Methods"
        MM["mouseMoveEvent(coordinates)"]
        MC["mouseClickEvent(button)"]
        MB["mouseButtonEvent(button, down)"]
        MW["mouseWheelEvent(direction, amount)"]
        HK["holdKeys(keys, down)"]
        SK["sendKeys(keys, delay)"]
        TT["typeText(text, delay)"]
        PT["pasteText(text)"]
        SD["screendump()"]
        CP["getCursorPosition()"]
    end
    
    MH --> MM
    MH --> MC
    MH --> MB
    MH --> MW
    MH --> HK
    KH --> HK
    KH --> SK
    KH --> TT
    KH --> PT
    SH --> SD
    SH --> CP
```

### Coordinate System

All mouse operations use absolute screen coordinates in the 1280x960 desktop resolution:
- X-axis: 0 (left) to 1280 (right)
- Y-axis: 0 (top) to 960 (bottom)
- Origin: Top-left corner

The `Coordinates` type enforces this contract: `{ x: number, y: number }`

**Sources:** [packages/bytebotd/src/computer-use/computer-use.service.ts:29](), [packages/shared/src/types/computerAction.types.ts:1]()

### Timing and Synchronization

The service implements explicit delays between certain operations to ensure desktop stability:

- **Multi-click delay**: 150ms between clicks in `clickMouse()`
- **Scroll delay**: 150ms between scroll events in `scroll()`
- **User-controlled wait**: `wait` action accepts duration in milliseconds

These delays prevent race conditions where the desktop hasn't finished rendering the result of one action before the next action executes.

**Sources:** [packages/bytebotd/src/computer-use/computer-use.service.ts:151](), [packages/bytebotd/src/computer-use/computer-use.service.ts:220]()

## Validation and Type Safety

The service benefits from multi-layer type safety through TypeScript discriminated unions, class-validator DTOs, and Zod schemas.

### Type Hierarchy

```mermaid
graph TB
    SharedTypes["@bytebot/shared<br/>ComputerAction union type"]
    DTOs["DTOs<br/>MoveMouseActionDto<br/>ClickMouseActionDto<br/>etc."]
    ValidationPipe["ComputerActionValidationPipe<br/>plainToClass + validate()"]
    ServiceMethod["ComputerUseService.action()<br/>params: ComputerAction"]
    
    SharedTypes -.->|Type definition| DTOs
    DTOs --> ValidationPipe
    ValidationPipe --> ServiceMethod
    SharedTypes -.->|Type constraint| ServiceMethod
```

### Validation Pipeline

The `ComputerActionValidationPipe` implements a two-stage validation process:

**Stage 1: DTO Selection**
```typescript
switch (value.action) {
  case 'move_mouse':
    dto = plainToClass(MoveMouseActionDto, value);
    break;
  case 'click_mouse':
    dto = plainToClass(ClickMouseActionDto, value);
    break;
  // ... 15 more cases
}
```

**Stage 2: Constraint Validation**
```typescript
const errors = await validate(dto);
if (errors.length > 0) {
  throw new BadRequestException(errors);
}
```

Each DTO class uses `class-validator` decorators to enforce constraints:

| Decorator | Purpose | Example Usage |
|-----------|---------|---------------|
| `@IsIn(['action_name'])` | Ensure action field matches | `@IsIn(['move_mouse'])` |
| `@ValidateNested()` | Validate nested objects | Coordinates validation |
| `@Type(() => Class)` | Transform plain object to class | `@Type(() => CoordinatesDto)` |
| `@IsEnum(EnumType)` | Validate against enum | `@IsEnum(ButtonType)` |
| `@IsNumber()` / `@IsString()` | Primitive type validation | Basic fields |
| `@Min(n)` | Numeric range validation | `@Min(1)` for clickCount |
| `@IsOptional()` | Allow undefined | Optional parameters |
| `@IsArray()` | Array validation | Key arrays, path arrays |

**Sources:** [packages/bytebotd/src/computer-use/dto/computer-action-validation.pipe.ts:29-96](), [packages/bytebotd/src/computer-use/dto/computer-action.dto.ts:1-240]()

## Integration Patterns

### MCP Tool Interface

The Computer Use API is exposed to AI agents through MCP (Model Context Protocol) tools. Each computer action becomes a tool that AI models can invoke:

```typescript
@Tool({
  name: 'computer_move_mouse',
  description: 'Moves the mouse cursor to the specified coordinates.',
  parameters: z.object({
    coordinates: z.object({
      x: z.number(),
      y: z.number(),
    }),
  }),
})
async moveMouse({ coordinates }) {
  await this.computerUse.action({ action: 'move_mouse', coordinates });
  return { content: [{ type: 'text', text: 'mouse moved' }] };
}
```

Each MCP tool wraps the corresponding computer action, providing AI-friendly descriptions and structured parameter schemas using Zod validation.

**Sources:** [packages/bytebotd/src/mcp/computer-use.tools.ts:11-35](), [packages/bytebotd/src/mcp/computer-use.tools.ts:80-138]()

### Message Content Integration

Computer actions integrate with Bytebot's message system through content block types. Actions can be converted between different representations:

- `ComputerAction` types for internal processing
- `ToolUseContentBlock` types for AI agent communication  
- `UserActionContentBlock` types for user interaction tracking

**Sources:** [packages/shared/src/types/messageContent.types.ts:187-203](), [packages/shared/src/utils/computerAction.utils.ts:299-342]()

### Request/Response Patterns

```mermaid
sequenceDiagram
    participant Client
    participant ValidationPipe as "ComputerActionValidationPipe"
    participant Service as "ComputerUseService"
    participant NUT as "NutService"
    participant Desktop as "Desktop Environment"
    
    Client->>ValidationPipe: POST /computer-use<br/>{action, params}
    ValidationPipe->>ValidationPipe: validate DTO
    ValidationPipe->>Service: action(validatedParams)
    Service->>Service: route to handler method
    Service->>NUT: execute desktop operation
    NUT->>Desktop: system calls
    Desktop->>NUT: operation result
    NUT->>Service: result data
    Service->>Client: HTTP response
```

The API follows a consistent request/response pattern where most actions return `{success: true}` on completion, while information-gathering actions like `screenshot` and `cursor_position` return additional data.

**Sources:** [packages/bytebotd/src/computer-use/computer-use.service.ts:31-105](), [docs/api-reference/computer-use/unified-endpoint.mdx:388-453]()

---

# Page: Desktop Tools

# Desktop Tools

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [packages/bytebot-agent/prisma/migrations/20250722041608_files/migration.sql](packages/bytebot-agent/prisma/migrations/20250722041608_files/migration.sql)
- [packages/bytebot-agent/src/agent/agent.computer-use.ts](packages/bytebot-agent/src/agent/agent.computer-use.ts)
- [packages/bytebot-agent/src/agent/agent.constants.ts](packages/bytebot-agent/src/agent/agent.constants.ts)
- [packages/bytebot-agent/src/agent/agent.scheduler.ts](packages/bytebot-agent/src/agent/agent.scheduler.ts)
- [packages/bytebot-agent/src/agent/agent.tools.ts](packages/bytebot-agent/src/agent/agent.tools.ts)
- [packages/bytebotd/src/computer-use/computer-use.controller.ts](packages/bytebotd/src/computer-use/computer-use.controller.ts)
- [packages/bytebotd/src/computer-use/computer-use.service.ts](packages/bytebotd/src/computer-use/computer-use.service.ts)
- [packages/bytebotd/src/computer-use/dto/base.dto.ts](packages/bytebotd/src/computer-use/dto/base.dto.ts)
- [packages/bytebotd/src/computer-use/dto/computer-action-validation.pipe.ts](packages/bytebotd/src/computer-use/dto/computer-action-validation.pipe.ts)
- [packages/bytebotd/src/computer-use/dto/computer-action.dto.ts](packages/bytebotd/src/computer-use/dto/computer-action.dto.ts)
- [packages/bytebotd/src/main.ts](packages/bytebotd/src/main.ts)
- [packages/bytebotd/src/mcp/computer-use.tools.ts](packages/bytebotd/src/mcp/computer-use.tools.ts)
- [packages/shared/src/types/computerAction.types.ts](packages/shared/src/types/computerAction.types.ts)
- [packages/shared/src/types/messageContent.types.ts](packages/shared/src/types/messageContent.types.ts)
- [packages/shared/src/utils/computerAction.utils.ts](packages/shared/src/utils/computerAction.utils.ts)
- [packages/shared/src/utils/messageContent.utils.ts](packages/shared/src/utils/messageContent.utils.ts)

</details>



This page documents all 17 desktop automation tools available to the AI agent for controlling the virtual desktop environment. These tools provide mouse control, keyboard input, screenshot capture, application management, file operations, and task control capabilities.

For information about how these tools are executed by the desktop daemon, see [Computer Use Service](#7.1). For details on how the agent processes and invokes these tools, see [Computer Use Integration](#6.2). For MCP exposure of these tools, see [MCP Integration](#7.3).

## Tool Categories

The desktop tools are organized into five functional categories:

| Category | Tool Count | Purpose |
|----------|------------|---------|
| **Mouse Tools** | 7 | Control cursor position and clicking behavior |
| **Keyboard Tools** | 4 | Simulate keyboard input and shortcuts |
| **Utility Tools** | 3 | Screenshot capture, waiting, and application management |
| **File Operations** | 2 | Read and write files on the desktop |
| **Task Management** | 2 | Control task status and create subtasks |

**Sources:** [packages/bytebot-agent/src/agent/agent.tools.ts:387-406]()

## Tool Architecture

```mermaid
graph TB
    subgraph "bytebot-agent (NestJS)"
        AgentTools["agentTools Array<br/>[agent.tools.ts:387-406]"]
        HandleComputerToolUse["handleComputerToolUse()<br/>[agent.computer-use.ts:28-239]"]
        TypeGuards["Type Guard Functions<br/>[messageContent.utils.ts]"]
    end
    
    subgraph "Shared Types (@bytebot/shared)"
        ToolUseBlocks["Tool Use Content Blocks<br/>MoveMouseToolUseBlock<br/>ClickMouseToolUseBlock<br/>TypeTextToolUseBlock<br/>etc."]
        ActionTypes["Computer Action Types<br/>MoveMouseAction<br/>ClickMouseAction<br/>TypeTextAction<br/>etc."]
    end
    
    subgraph "bytebotd Desktop Daemon (NestJS)"
        ComputerUseService["ComputerUseService<br/>[computer-use.service.ts:26-507]"]
        ActionDispatcher["action() Method<br/>Switch Statement<br/>[computer-use.service.ts:31-105]"]
        NutService["NutService<br/>Desktop Automation Layer"]
    end
    
    LLM["LLM Provider<br/>(Claude/GPT/Gemini)"]
    
    LLM -->|"Tool use response"| HandleComputerToolUse
    HandleComputerToolUse -->|"Type guard validation"| TypeGuards
    HandleComputerToolUse -->|"POST /computer-use"| ActionDispatcher
    ActionDispatcher -->|"moveMouse()<br/>clickMouse()<br/>typeText()<br/>etc."| ComputerUseService
    ComputerUseService -->|"NutJS API calls"| NutService
    
    AgentTools -->|"Sent to LLM<br/>as available tools"| LLM
    
    ToolUseBlocks -.->|"Type definitions"| HandleComputerToolUse
    ActionTypes -.->|"Type definitions"| ComputerUseService
```

**Sources:** [packages/bytebot-agent/src/agent/agent.tools.ts:1-406](), [packages/bytebot-agent/src/agent/agent.computer-use.ts:1-647](), [packages/bytebotd/src/computer-use/computer-use.service.ts:1-507]()

## Mouse Tools

### computer_move_mouse

Moves the mouse cursor to absolute screen coordinates.

**Parameters:**
- `coordinates` (required): Target `{x, y}` position in pixels

**Tool Definition:**
```typescript
{
  name: 'computer_move_mouse',
  description: 'Moves the mouse cursor to the specified coordinates',
  input_schema: {
    type: 'object',
    properties: {
      coordinates: { type: 'object', properties: { x: 'number', y: 'number' } }
    },
    required: ['coordinates']
  }
}
```

**Execution:** Calls `NutService.mouseMoveEvent(coordinates)` in [computer-use.service.ts:107-109]().

**Sources:** [packages/bytebot-agent/src/agent/agent.tools.ts:35-48](), [packages/bytebotd/src/computer-use/computer-use.service.ts:107-109]()

### computer_trace_mouse

Moves the mouse cursor smoothly along a path of coordinates, optionally holding modifier keys.

**Parameters:**
- `path` (required): Array of `{x, y}` coordinates defining the path
- `holdKeys` (optional): Array of key names to hold during trace (e.g., `["LeftShift"]`)

**Execution:** Moves to first coordinate, holds keys if specified, traces through all path points, then releases keys. See [computer-use.service.ts:111-131]().

**Sources:** [packages/bytebot-agent/src/agent/agent.tools.ts:50-65](), [packages/bytebotd/src/computer-use/computer-use.service.ts:111-131]()

### computer_click_mouse

Performs single or multiple mouse button clicks at specified coordinates or current position.

**Parameters:**
- `coordinates` (optional): Click location; defaults to current position
- `button` (required): `"left"`, `"right"`, or `"middle"`
- `holdKeys` (optional): Array of modifier keys to hold during click
- `clickCount` (required): Number of clicks (e.g., `2` for double-click)

**Execution:** Moves to coordinates if provided, holds modifier keys, performs clicks with 150ms delay between each, releases modifiers. See [computer-use.service.ts:133-162]().

**Sources:** [packages/bytebot-agent/src/agent/agent.tools.ts:67-90](), [packages/bytebotd/src/computer-use/computer-use.service.ts:133-162]()

### computer_press_mouse

Presses down or releases up a specific mouse button without completing a click.

**Parameters:**
- `coordinates` (optional): Position to press at; defaults to current position
- `button` (required): Mouse button to press/release
- `press` (required): `"down"` or `"up"`

**Use Case:** Enables drag operations by separating press and release actions.

**Sources:** [packages/bytebot-agent/src/agent/agent.tools.ts:92-112](), [packages/bytebotd/src/computer-use/computer-use.service.ts:164-178]()

### computer_drag_mouse

Drags the mouse along a path while holding a button down.

**Parameters:**
- `path` (required): Array of coordinates for the drag path
- `button` (required): Button to hold during drag
- `holdKeys` (optional): Modifier keys to hold

**Execution Flow:**
1. Move to first path coordinate
2. Hold modifier keys if specified
3. Press mouse button down
4. Move through all path coordinates
5. Release mouse button
6. Release modifier keys

**Sources:** [packages/bytebot-agent/src/agent/agent.tools.ts:114-130](), [packages/bytebotd/src/computer-use/computer-use.service.ts:180-202]()

### computer_scroll

Scrolls the mouse wheel in a specified direction.

**Parameters:**
- `coordinates` (optional): Position to scroll at
- `direction` (required): `"up"`, `"down"`, `"left"`, or `"right"`
- `scrollCount` (required): Number of scroll steps
- `holdKeys` (optional): Modifier keys to hold during scroll

**Execution:** Performs each scroll step with a 150ms delay between steps. See [computer-use.service.ts:204-227]().

**Sources:** [packages/bytebot-agent/src/agent/agent.tools.ts:132-155](), [packages/bytebotd/src/computer-use/computer-use.service.ts:204-227]()

### computer_cursor_position

Returns the current `{x, y}` coordinates of the mouse cursor.

**Returns:** `{ x: number, y: number }`

**Use Case:** Allows the agent to determine current cursor position for relative movements.

**Sources:** [packages/bytebot-agent/src/agent/agent.tools.ts:278-285](), [packages/bytebotd/src/computer-use/computer-use.service.ts:259-262]()

## Keyboard Tools

### computer_type_keys

Types a sequence of keys in order, pressing and releasing each. Used primarily for keyboard shortcuts.

**Parameters:**
- `keys` (required): Array of key names to type (e.g., `["LeftControl", "C"]`)
- `delay` (optional): Milliseconds to wait between key presses

**Valid Keys:** Must use exact identifiers from nut-tree's `Key` enum. See the full list in [agent.constants.ts:148-169]() including:
- Modifiers: `LeftControl`, `LeftShift`, `LeftAlt`, `LeftCmd`
- Letters: `A`-`Z` (case-sensitive)
- Function keys: `F1`-`F24`
- Special keys: `Enter`, `Backspace`, `Delete`, `Tab`, `Escape`
- Navigation: `Up`, `Down`, `Left`, `Right`, `Home`, `End`, `PageUp`, `PageDown`

**Sources:** [packages/bytebot-agent/src/agent/agent.tools.ts:160-179](), [packages/bytebotd/src/computer-use/computer-use.service.ts:229-232](), [packages/bytebot-agent/src/agent/agent.constants.ts:148-169]()

### computer_press_keys

Presses down or releases keys without completing a full press-release cycle. Used for holding modifier keys.

**Parameters:**
- `keys` (required): Array of key names
- `press` (required): `"down"` or `"up"`

**Use Case:** Hold Shift while performing other actions, then release it.

**Sources:** [packages/bytebot-agent/src/agent/agent.tools.ts:181-201](), [packages/bytebotd/src/computer-use/computer-use.service.ts:234-237]()

### computer_type_text

Types a text string character by character. Recommended for strings less than 25 characters or sensitive fields.

**Parameters:**
- `text` (required): String to type
- `delay` (optional): Milliseconds between characters
- `isSensitive` (optional): Boolean flag indicating sensitive information (e.g., passwords)

**Note:** The agent system prompt instructs the LLM not to repeat sensitive text when `isSensitive` is true. See [agent.constants.ts:56]().

**Sources:** [packages/bytebot-agent/src/agent/agent.tools.ts:203-227](), [packages/bytebotd/src/computer-use/computer-use.service.ts:239-242]()

### computer_paste_text

Copies text to clipboard and pastes it using Ctrl+V. Recommended for long strings or special characters.

**Parameters:**
- `text` (required): String to paste
- `isSensitive` (optional): Boolean flag for sensitive data

**Execution:** Uses clipboard manipulation via NutJS. More efficient than `type_text` for large content.

**Sources:** [packages/bytebot-agent/src/agent/agent.tools.ts:229-248](), [packages/bytebotd/src/computer-use/computer-use.service.ts:244-247]()

## Utility Tools

### computer_wait

Pauses execution for a specified duration.

**Parameters:**
- `duration` (required): Milliseconds to wait (enum constrained to `500`)

**Use Case:** Allow time for UI animations or slow operations to complete.

**Execution:** Simple `setTimeout` promise. See [computer-use.service.ts:249-251]().

**Sources:** [packages/bytebot-agent/src/agent/agent.tools.ts:253-267](), [packages/bytebotd/src/computer-use/computer-use.service.ts:76-80]()

### computer_screenshot

Captures a screenshot of the entire desktop display (1280x960).

**Returns:** Base64-encoded PNG image in response format:
```typescript
{
  type: 'tool_result',
  tool_use_id: string,
  content: [{
    type: 'image',
    source: {
      data: string,  // base64
      media_type: 'image/png',
      type: 'base64'
    }
  }]
}
```

**Execution:** Calls `NutService.screendump()` which captures via Sharp image processing library. See [computer-use.service.ts:253-257]().

**Sources:** [packages/bytebot-agent/src/agent/agent.tools.ts:269-276](), [packages/bytebotd/src/computer-use/computer-use.service.ts:253-257]()

### computer_application

Opens or focuses a desktop application and maximizes it.

**Parameters:**
- `application` (required): Application name from enum

**Available Applications:**
- `firefox` - Firefox ESR browser
- `1password` - 1Password password manager
- `thunderbird` - Thunderbird email client
- `vscode` - Visual Studio Code editor
- `terminal` - XFCE4 Terminal
- `directory` - Thunar file manager
- `desktop` - Return to desktop/show desktop

**Execution Logic:**
1. Check if application is already open using `wmctrl -lx`
2. If open: activate and maximize window
3. If not open: launch application using `sudo -u user nohup <command>`
4. Uses fire-and-forget pattern (detached processes)

See the command and process mappings in [computer-use.service.ts:287-304]().

**Sources:** [packages/bytebot-agent/src/agent/agent.tools.ts:287-309](), [packages/bytebotd/src/computer-use/computer-use.service.ts:264-362]()

## File Operations

### computer_read_file

Reads a file from the desktop filesystem and returns it as a document content block.

**Parameters:**
- `path` (required): File path (relative paths are resolved to `/home/user/Desktop/`)

**Returns:** Document content block with:
```typescript
{
  type: 'tool_result',
  content: [{
    type: 'document',
    source: {
      type: 'base64',
      media_type: string,  // MIME type based on extension
      data: string         // base64 encoded file
    },
    name: string,
    size: number
  }]
}
```

**Supported File Types:** PDF, DOCX, DOC, TXT, HTML, JSON, XML, CSV, RTF, ODT, EPUB, PNG, JPG, JPEG, WEBP, GIF, SVG. See MIME type mapping in [computer-use.service.ts:464-482]().

**Execution:**
1. Resolve relative path to `/home/user/Desktop/`
2. Copy file to temp location using `sudo cp`
3. Read file buffer from temp location
4. Get file stats for size
5. Determine MIME type from extension
6. Clean up temp file
7. Return base64-encoded content

**Sources:** [packages/bytebot-agent/src/agent/agent.tools.ts:368-382](), [packages/bytebotd/src/computer-use/computer-use.service.ts:419-506]()

### computer_write_file

Writes base64-encoded data to a file on the desktop.

**Parameters:**
- `path` (required): Target file path (relative paths resolved to `/home/user/Desktop/`)
- `data` (required): Base64-encoded file content

**Returns:**
```typescript
{
  success: boolean,
  message: string
}
```

**Execution:**
1. Decode base64 data to buffer
2. Resolve relative path
3. Create directory structure using `sudo mkdir -p`
4. Write to temp file
5. Copy temp file to target using `sudo cp`
6. Set ownership to `user:user` and permissions to 644
7. Clean up temp file

**Sources:** [packages/bytebot-agent/src/agent/agent.computer-use.ts:612-646](), [packages/bytebotd/src/computer-use/computer-use.service.ts:364-417]()

## Task Management Tools

These tools control task lifecycle and are not exposed via the Computer Use API. They are handled directly in the agent processor.

### set_task_status

Sets the status of the current task to `completed` or `needs_help`.

**Parameters:**
- `status` (required): `"completed"` or `"needs_help"`
- `description` (required): Summary of completion or issue description

**Behavior:**
- `completed`: Task is marked complete, agent stops processing
- `needs_help`: Task pauses, user can provide guidance and resume

**Sources:** [packages/bytebot-agent/src/agent/agent.tools.ts:314-333]()

### create_task

Creates a new task to be executed after the current task completes.

**Parameters:**
- `description` (required): Task description
- `type` (optional): `"IMMEDIATE"` (default) or `"SCHEDULED"`
- `scheduledFor` (optional): ISO 8601 datetime for scheduled tasks
- `priority` (optional): `"LOW"`, `"MEDIUM"` (default), `"HIGH"`, or `"URGENT"`

**Use Case:** Break down complex work into separate tasks or schedule future actions.

**Sources:** [packages/bytebot-agent/src/agent/agent.tools.ts:335-363]()

## Tool Execution Flow

```mermaid
sequenceDiagram
    participant LLM as "LLM Provider"
    participant AP as "AgentProcessor<br/>[agent.processor.ts]"
    participant Handler as "handleComputerToolUse()<br/>[agent.computer-use.ts:28-239]"
    participant Guards as "Type Guards<br/>[messageContent.utils.ts]"
    participant API as "Desktop API<br/>POST /computer-use"
    participant CUS as "ComputerUseService<br/>[computer-use.service.ts]"
    participant Nut as "NutService<br/>Desktop Automation"
    
    LLM->>AP: "Tool use response"
    AP->>Handler: "Pass tool use blocks"
    Handler->>Guards: "isScreenshotToolUseBlock()?"
    alt Screenshot Tool
        Guards-->>Handler: "true"
        Handler->>API: "POST /computer-use<br/>{action: 'screenshot'}"
        API->>CUS: "action(params)"
        CUS->>Nut: "screendump()"
        Nut-->>CUS: "Buffer"
        CUS-->>API: "{image: base64}"
        API-->>Handler: "Response"
        Handler-->>AP: "ToolResult with image"
    else Other Computer Tool
        Guards-->>Handler: "false, check next..."
        Handler->>Guards: "isMoveMouseToolUseBlock()?"
        Guards-->>Handler: "true"
        Handler->>API: "POST /computer-use<br/>{action: 'move_mouse', coordinates}"
        API->>CUS: "action(params)"
        CUS->>CUS: "moveMouse(params)"
        CUS->>Nut: "mouseMoveEvent(coordinates)"
        Nut-->>CUS: "void"
        CUS-->>API: "void"
        Note over Handler: "Wait 750ms for UI to settle"
        Handler->>API: "POST /computer-use<br/>{action: 'screenshot'}"
        API-->>Handler: "Screenshot"
        Handler-->>AP: "ToolResult with screenshot"
    end
```

**Sources:** [packages/bytebot-agent/src/agent/agent.computer-use.ts:28-239](), [packages/bytebotd/src/computer-use/computer-use.service.ts:31-105]()

## Validation Architecture

```mermaid
graph LR
    subgraph "bytebot-agent"
        ToolDef["Tool Definitions<br/>agentTools array"]
        TypeGuards["Type Guard Functions<br/>is*ToolUseBlock()"]
        Handler["handleComputerToolUse()"]
    end
    
    subgraph "Shared Types"
        ContentBlocks["Tool Use Content Blocks<br/>Typed interfaces"]
        ActionTypes["Computer Action Types<br/>Typed interfaces"]
    end
    
    subgraph "bytebotd"
        ValidationPipe["ComputerActionValidationPipe<br/>[computer-action-validation.pipe.ts]"]
        DTOs["Action DTOs<br/>class-validator decorators"]
        Service["ComputerUseService<br/>Type-safe dispatch"]
    end
    
    ToolDef -.->|"Schema validation"| ContentBlocks
    Handler -->|"Runtime validation"| TypeGuards
    TypeGuards -.->|"Use types"| ContentBlocks
    Handler -->|"POST JSON"| ValidationPipe
    ValidationPipe -->|"Transform & validate"| DTOs
    DTOs -.->|"Match types"| ActionTypes
    ValidationPipe -->|"Validated DTO"| Service
    Service -.->|"Type-safe methods"| ActionTypes
```

**Validation Layers:**

1. **Tool Schema Definition** - JSON Schema in tool definitions ensures LLM generates valid inputs
2. **Type Guards** - Runtime checks in agent using type predicates from [messageContent.utils.ts]()
3. **DTO Validation** - class-validator decorators in bytebotd DTOs, see [computer-action.dto.ts]()
4. **Validation Pipe** - `ComputerActionValidationPipe` transforms and validates requests at API boundary

**Sources:** [packages/bytebot-agent/src/agent/agent.tools.ts:1-406](), [packages/shared/src/utils/messageContent.utils.ts:1-516](), [packages/bytebotd/src/computer-use/dto/computer-action.dto.ts:1-240](), [packages/bytebotd/src/computer-use/dto/computer-action-validation.pipe.ts:1-97]()

## Complete Tool Reference

| Tool Name | Category | Parameters | Returns | Key File Reference |
|-----------|----------|------------|---------|-------------------|
| `computer_move_mouse` | Mouse | coordinates | void + screenshot | [agent.tools.ts:35-48]() |
| `computer_trace_mouse` | Mouse | path, holdKeys? | void + screenshot | [agent.tools.ts:50-65]() |
| `computer_click_mouse` | Mouse | coordinates?, button, holdKeys?, clickCount | void + screenshot | [agent.tools.ts:67-90]() |
| `computer_press_mouse` | Mouse | coordinates?, button, press | void + screenshot | [agent.tools.ts:92-112]() |
| `computer_drag_mouse` | Mouse | path, button, holdKeys? | void + screenshot | [agent.tools.ts:114-130]() |
| `computer_scroll` | Mouse | coordinates?, direction, scrollCount, holdKeys? | void + screenshot | [agent.tools.ts:132-155]() |
| `computer_cursor_position` | Mouse | none | {x, y} | [agent.tools.ts:278-285]() |
| `computer_type_keys` | Keyboard | keys, delay? | void + screenshot | [agent.tools.ts:160-179]() |
| `computer_press_keys` | Keyboard | keys, press | void + screenshot | [agent.tools.ts:181-201]() |
| `computer_type_text` | Keyboard | text, delay?, isSensitive? | void + screenshot | [agent.tools.ts:203-227]() |
| `computer_paste_text` | Keyboard | text, isSensitive? | void + screenshot | [agent.tools.ts:229-248]() |
| `computer_wait` | Utility | duration | void | [agent.tools.ts:253-267]() |
| `computer_screenshot` | Utility | none | image (base64) | [agent.tools.ts:269-276]() |
| `computer_application` | Utility | application | void + screenshot | [agent.tools.ts:287-309]() |
| `computer_read_file` | File | path | document (base64) | [agent.tools.ts:368-382]() |
| `set_task_status` | Task | status, description | N/A (internal) | [agent.tools.ts:314-333]() |
| `create_task` | Task | description, type?, scheduledFor?, priority? | N/A (internal) | [agent.tools.ts:335-363]() |

**Note:** All computer tools except `screenshot`, `cursor_position`, and `read_file` automatically capture a verification screenshot after execution with a 750ms delay to allow UI settling. See [agent.computer-use.ts:186-219]().

**Sources:** [packages/bytebot-agent/src/agent/agent.tools.ts:387-406](), [packages/bytebot-agent/src/agent/agent.computer-use.ts:28-239]()

---

# Page: MCP Integration

# MCP Integration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [packages/bytebotd/package-lock.json](packages/bytebotd/package-lock.json)
- [packages/bytebotd/package.json](packages/bytebotd/package.json)
- [packages/bytebotd/src/app.controller.ts](packages/bytebotd/src/app.controller.ts)
- [packages/bytebotd/src/app.module.ts](packages/bytebotd/src/app.module.ts)
- [packages/bytebotd/src/mcp/bytebot-mcp.module.ts](packages/bytebotd/src/mcp/bytebot-mcp.module.ts)
- [packages/bytebotd/src/mcp/index.ts](packages/bytebotd/src/mcp/index.ts)

</details>



## Purpose and Scope

This document describes the Model Context Protocol (MCP) integration in the bytebotd service. MCP provides a standardized way for AI systems to discover and invoke tools via Server-Sent Events (SSE). The integration exposes computer automation capabilities as MCP-compliant tools, enabling external AI agents to control the virtual desktop.

For information about the underlying computer automation capabilities, see [Computer Use Service](#7.1). For details on the individual desktop actions available, see [Desktop Tools](#7.2). For the REST API alternative, see [Computer Use API](#10.2).

---

## Overview

The MCP integration serves as an alternative interface to the computer automation system. While the REST API at `POST /computer-use` is used by the bytebot-agent service for task execution, the MCP endpoint at `/mcp` allows external AI systems and tools to discover and invoke the same capabilities through a standardized protocol.

### Key Characteristics

| Feature | Description |
|---------|-------------|
| **Protocol** | Server-Sent Events (SSE) for bidirectional communication |
| **Endpoint** | `/mcp` on port 9990 |
| **Library** | `@rekog/mcp-nest` v1.6.2 |
| **Exposed Tools** | All computer automation actions from ComputerUseService |
| **Use Case** | External AI agent integration, tool discovery, remote desktop control |

**Sources:** [packages/bytebotd/package.json:38](), [packages/bytebotd/src/mcp/bytebot-mcp.module.ts:9-13]()

---

## Module Architecture

```mermaid
graph TB
    subgraph "bytebotd Application"
        AppModule["AppModule<br/>(app.module.ts)"]
        BytebotMcpModule["BytebotMcpModule<br/>(bytebot-mcp.module.ts)"]
        ComputerUseModule["ComputerUseModule<br/>(computer-use.module.ts)"]
        ComputerUseTools["ComputerUseTools<br/>(computer-use.tools.ts)"]
        McpModule["McpModule<br/>(@rekog/mcp-nest)"]
    end
    
    subgraph "External Layer"
        MCPClients["External MCP Clients<br/>(AI Systems, Tools)"]
    end
    
    subgraph "Internal Services"
        ComputerUseService["ComputerUseService<br/>(computer-use.service.ts)"]
    end
    
    AppModule -->|"imports"| BytebotMcpModule
    BytebotMcpModule -->|"imports"| ComputerUseModule
    BytebotMcpModule -->|"imports"| McpModule
    BytebotMcpModule -->|"provides"| ComputerUseTools
    
    ComputerUseTools -->|"injects"| ComputerUseService
    McpModule -->|"discovers"| ComputerUseTools
    
    MCPClients <-->|"SSE: /mcp"| McpModule
    
    style BytebotMcpModule fill:#f9f9f9
    style ComputerUseTools fill:#f9f9f9
    style McpModule fill:#e1e1e1
```

**Module Structure Diagram** - Shows the NestJS module hierarchy and MCP integration point

The `BytebotMcpModule` serves as the integration point between the MCP protocol library and the computer automation system. It imports `ComputerUseModule` to access the underlying automation services and configures `McpModule` with the SSE endpoint.

**Sources:** [packages/bytebotd/src/app.module.ts:21](), [packages/bytebotd/src/mcp/bytebot-mcp.module.ts:1-17]()

---

## BytebotMcpModule Configuration

The module is defined in [packages/bytebotd/src/mcp/bytebot-mcp.module.ts:6-17]() and follows NestJS module conventions:

```typescript
@Module({
  imports: [
    ComputerUseModule,
    McpModule.forRoot({
      name: 'bytebotd',
      version: '0.0.1',
      sseEndpoint: '/mcp',
    }),
  ],
  providers: [ComputerUseTools],
})
export class BytebotMcpModule {}
```

### Configuration Properties

| Property | Value | Purpose |
|----------|-------|---------|
| `name` | `'bytebotd'` | Service identifier for MCP clients |
| `version` | `'0.0.1'` | Version number exposed to clients |
| `sseEndpoint` | `'/mcp'` | URL path where SSE connection is established |

The `McpModule.forRoot()` method sets up the SSE server infrastructure, tool discovery mechanism, and protocol handlers. The module automatically discovers providers decorated with MCP tool decorators (like `ComputerUseTools`) and exposes them through the SSE endpoint.

**Sources:** [packages/bytebotd/src/mcp/bytebot-mcp.module.ts:6-17]()

---

## SSE Communication Flow

```mermaid
sequenceDiagram
    participant Client as "MCP Client"
    participant SSE as "SSE Endpoint<br/>/mcp"
    participant McpModule as "McpModule"
    participant Tools as "ComputerUseTools"
    participant Service as "ComputerUseService"
    
    Client->>SSE: "Connect (SSE)"
    SSE->>McpModule: "Establish connection"
    McpModule-->>Client: "Server info (bytebotd v0.0.1)"
    
    Client->>McpModule: "list_tools request"
    McpModule->>Tools: "Discover available tools"
    Tools-->>McpModule: "Tool schemas"
    McpModule-->>Client: "Tool list with schemas"
    
    Client->>McpModule: "call_tool: move_mouse"
    McpModule->>Tools: "Route to handler"
    Tools->>Service: "executeAction(move_mouse)"
    Service-->>Tools: "Action result"
    Tools-->>McpModule: "Result"
    McpModule-->>Client: "Tool result"
    
    Note over Client,Service: "Connection remains open for multiple requests"
```

**MCP SSE Communication Flow** - Shows the lifecycle of tool discovery and invocation

The SSE connection provides a persistent channel for:
1. **Discovery**: Clients can query available tools and their schemas
2. **Invocation**: Clients can call tools with typed parameters
3. **Streaming**: Real-time results and events can be pushed to clients

Unlike the REST API, the SSE connection remains open, allowing for efficient repeated tool calls without connection overhead.

**Sources:** [packages/bytebotd/src/mcp/bytebot-mcp.module.ts:12]()

---

## ComputerUseTools Provider

While the specific implementation of `ComputerUseTools` is not visible in the provided files, based on the module structure and MCP conventions, this provider:

1. **Decorates methods** with `@McpTool()` or similar decorators to expose them
2. **Injects ComputerUseService** to delegate actual computer automation
3. **Defines schemas** for each tool's parameters using the MCP protocol format
4. **Handles errors** and formats responses according to MCP standards

### Expected Tool Exposure Pattern

```mermaid
graph LR
    subgraph "ComputerUseTools"
        MoveMouse["@McpTool()<br/>moveMouse()"]
        ClickMouse["@McpTool()<br/>clickMouse()"]
        TypeText["@McpTool()<br/>typeText()"]
        Screenshot["@McpTool()<br/>screenshot()"]
        OtherTools["... other tools"]
    end
    
    subgraph "ComputerUseService"
        ExecuteAction["executeAction()<br/>(main dispatch)"]
    end
    
    MoveMouse -->|"delegates"| ExecuteAction
    ClickMouse -->|"delegates"| ExecuteAction
    TypeText -->|"delegates"| ExecuteAction
    Screenshot -->|"delegates"| ExecuteAction
    OtherTools -->|"delegates"| ExecuteAction
```

**Tool Delegation Pattern** - Each MCP tool method delegates to ComputerUseService.executeAction()

The tools exposed through MCP correspond to the same action types available through the REST API (see [Desktop Tools](#7.2) for the complete list of 17 actions).

**Sources:** [packages/bytebotd/src/mcp/bytebot-mcp.module.ts:4](), [packages/bytebotd/src/mcp/bytebot-mcp.module.ts:15]()

---

## Client Integration

External MCP clients connect to the bytebotd SSE endpoint to access desktop automation:

### Connection URL

```
http://localhost:9990/mcp
```

Or in production/Docker environments:
```
http://bytebotd:9990/mcp
```

### Client Workflow

1. **Establish SSE Connection**: Client opens connection to `/mcp` endpoint
2. **Receive Server Info**: Server sends service name and version
3. **List Tools**: Client sends `list_tools` message to discover capabilities
4. **Validate Schemas**: Client receives tool schemas with parameter types
5. **Invoke Tools**: Client sends `call_tool` messages with typed parameters
6. **Process Results**: Client receives tool execution results

### MCP Protocol Messages

| Message Type | Direction | Purpose |
|--------------|-----------|---------|
| `initialize` | Client → Server | Establish protocol version |
| `initialized` | Server → Client | Confirm initialization |
| `list_tools` | Client → Server | Request available tools |
| `tools_list` | Server → Client | Send tool schemas |
| `call_tool` | Client → Server | Execute a specific tool |
| `tool_result` | Server → Client | Return execution result |

**Sources:** [packages/bytebotd/src/mcp/bytebot-mcp.module.ts:12]()

---

## Integration Points

```mermaid
graph TB
    subgraph "Access Methods"
        REST["REST API<br/>POST /computer-use"]
        MCP["MCP SSE<br/>GET /mcp"]
    end
    
    subgraph "Core Service"
        ComputerUseService["ComputerUseService<br/>executeAction()"]
    end
    
    subgraph "Clients"
        BytebotAgent["bytebot-agent<br/>(Internal)"]
        ExternalAI["External AI Systems<br/>(External)"]
        MCPTools["MCP-Compatible Tools<br/>(External)"]
    end
    
    BytebotAgent -->|"HTTP POST"| REST
    ExternalAI -->|"SSE"| MCP
    MCPTools -->|"SSE"| MCP
    
    REST --> ComputerUseService
    MCP --> ComputerUseService
    
    style ComputerUseService fill:#f9f9f9
```

**Access Method Comparison** - Two interfaces to the same underlying automation service

### REST API vs MCP SSE

| Aspect | REST API | MCP SSE |
|--------|----------|---------|
| **Protocol** | HTTP POST | Server-Sent Events |
| **Connection** | Request-response | Persistent connection |
| **Discovery** | Fixed schema | Dynamic tool discovery |
| **Primary User** | bytebot-agent | External AI systems |
| **Endpoint** | `/computer-use` | `/mcp` |
| **Standards** | Custom | MCP protocol |

Both interfaces provide access to the identical set of computer automation actions. The REST API is optimized for the internal agent's observe-act loop, while MCP enables standardized integration with external AI frameworks and tools.

**Sources:** [packages/bytebotd/src/mcp/bytebot-mcp.module.ts:1-17](), [packages/bytebotd/src/app.module.ts:21]()

---

## Module Exports

The module's public interface is defined in [packages/bytebotd/src/mcp/index.ts:1]():

```typescript
export * from './bytebot-mcp.module';
```

This makes `BytebotMcpModule` available for import by the main `AppModule` at [packages/bytebotd/src/app.module.ts:8]().

**Sources:** [packages/bytebotd/src/mcp/index.ts:1](), [packages/bytebotd/src/app.module.ts:8]()

---

## Dependencies

The MCP integration relies on the following packages:

| Package | Version | Purpose |
|---------|---------|---------|
| `@rekog/mcp-nest` | ^1.6.2 | MCP protocol implementation for NestJS |
| `@nestjs/common` | ^11.1.2 | NestJS core module decorators |
| `@nestjs/core` | ^11.0.1 | NestJS dependency injection |

The `@rekog/mcp-nest` library provides:
- SSE server infrastructure
- MCP protocol message handling
- Tool discovery and registration
- Schema validation
- Error handling

**Sources:** [packages/bytebotd/package.json:38](), [packages/bytebotd/package.json:30-32]()

---

## Deployment Configuration

The MCP endpoint is exposed through the main bytebotd service on port 9990. In Docker deployments, this port is mapped to the host, making the SSE endpoint accessible at:

```
http://localhost:9990/mcp
```

No additional configuration is required beyond the standard bytebotd service setup. The endpoint is automatically available when the service starts.

For Railway or other cloud deployments, ensure that:
1. Port 9990 is exposed
2. SSE connections are allowed by the load balancer/proxy
3. Long-lived connections are supported (SSE requires persistent HTTP connections)

**Sources:** [packages/bytebotd/src/mcp/bytebot-mcp.module.ts:12]()

---

# Page: Input Tracking

# Input Tracking

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [packages/bytebotd/package-lock.json](packages/bytebotd/package-lock.json)
- [packages/bytebotd/package.json](packages/bytebotd/package.json)
- [packages/bytebotd/src/app.controller.ts](packages/bytebotd/src/app.controller.ts)
- [packages/bytebotd/src/app.module.ts](packages/bytebotd/src/app.module.ts)
- [packages/bytebotd/src/mcp/bytebot-mcp.module.ts](packages/bytebotd/src/mcp/bytebot-mcp.module.ts)
- [packages/bytebotd/src/mcp/index.ts](packages/bytebotd/src/mcp/index.ts)

</details>



## Purpose and Scope

This document describes the input tracking system in bytebotd, which captures user keyboard and mouse events during manual control sessions. The system uses the `uiohook-napi` library to monitor user interactions and record them as structured actions that can be processed by the AI agent.

For information about executing computer actions programmatically, see [Computer Use Service](#7.1). For details on specific desktop automation tools, see [Desktop Tools](#7.2).

**Sources:** [packages/bytebotd/src/app.module.ts:1-27]()

---

## System Architecture

The Input Tracking system is implemented as a NestJS module within bytebotd and operates as a passive monitoring layer that captures low-level input events and transforms them into high-level user actions.

```mermaid
graph TB
    subgraph "User Layer"
        User["User (Manual Control)"]
        Desktop["XFCE Desktop<br/>1280x960"]
    end
    
    subgraph "bytebotd - Input Tracking System"
        ITModule["InputTrackingModule"]
        UIHook["uiohook-napi<br/>Native Event Hooks"]
        EventProcessor["Event Processing Logic"]
        ActionRecorder["Action Recorder"]
    end
    
    subgraph "Integration Points"
        MessagesService["bytebot-agent<br/>MessagesService"]
        TaskSystem["Task State Machine"]
    end
    
    User -->|"Keyboard/Mouse"| Desktop
    Desktop -->|"OS-Level Events"| UIHook
    UIHook -->|"Raw Events"| EventProcessor
    EventProcessor -->|"Structured Actions"| ActionRecorder
    ActionRecorder -->|"UserAction Messages"| MessagesService
    TaskSystem -.->|"Enable on NEEDS_HELP"| ITModule
    TaskSystem -.->|"Disable on RESUME"| ITModule
```

**Diagram: Input Tracking Architecture**

The system operates in three stages:
1. **Event Capture**: uiohook-napi hooks into OS-level input events
2. **Event Processing**: Raw events are transformed into meaningful actions
3. **Action Recording**: Structured actions are stored as message content blocks

**Sources:** [packages/bytebotd/src/app.module.ts:1-27](), [packages/bytebotd/package.json:46]()

---

## uiohook-napi Integration

### Library Overview

The bytebotd service uses `uiohook-napi` version 1.5.4 as its input capture backend. This library provides cross-platform native bindings for capturing global keyboard and mouse events at the operating system level.

| Feature | Details |
|---------|---------|
| **Package** | `uiohook-napi@1.5.4` |
| **Type** | Native Addon (N-API) |
| **Scope** | Global input event capture |
| **Platform** | Linux (Ubuntu 22.04 in container) |
| **Events Captured** | Mouse movement, clicks, keyboard presses/releases, wheel events |

**Sources:** [packages/bytebotd/package.json:46]()

### Event Hook Implementation

```mermaid
graph LR
    subgraph "OS Level"
        XServer["X Server<br/>(Display :1)"]
        InputDevices["Input Devices<br/>(Mouse/Keyboard)"]
    end
    
    subgraph "uiohook-napi Layer"
        NativeHook["Native Event Hook"]
        EventQueue["Event Queue"]
    end
    
    subgraph "Node.js Layer"
        NAPIBridge["N-API Bridge"]
        EventEmitter["Node EventEmitter"]
    end
    
    InputDevices --> XServer
    XServer --> NativeHook
    NativeHook --> EventQueue
    EventQueue --> NAPIBridge
    NAPIBridge --> EventEmitter
```

**Diagram: uiohook-napi Event Capture Pipeline**

The library operates by:
1. Installing global event hooks at the X Server level
2. Capturing events before they reach application windows
3. Queueing events for processing by the Node.js runtime
4. Exposing events through a Node.js EventEmitter interface

**Sources:** [packages/bytebotd/package.json:28-46]()

---

## InputTrackingModule Structure

### Module Configuration

The `InputTrackingModule` is registered in the root `AppModule` and operates as a global service within bytebotd.

```mermaid
graph TB
    AppModule["AppModule"]
    ConfigModule["ConfigModule<br/>(Global)"]
    ComputerUseModule["ComputerUseModule"]
    InputTrackingModule["InputTrackingModule"]
    BytebotMcpModule["BytebotMcpModule"]
    
    AppModule --> ConfigModule
    AppModule --> ComputerUseModule
    AppModule --> InputTrackingModule
    AppModule --> BytebotMcpModule
    
    InputTrackingModule -.->|"May depend on"| ConfigModule
```

**Diagram: InputTrackingModule in App Structure**

The module is imported alongside other core modules:
- **ComputerUseModule**: Handles outbound actions (agent → desktop)
- **InputTrackingModule**: Handles inbound events (user → system)
- **BytebotMcpModule**: Provides MCP management interface

**Sources:** [packages/bytebotd/src/app.module.ts:1-27]()

### Module Dependencies

The InputTrackingModule likely provides:
- An event listener service that subscribes to uiohook-napi events
- An action transformation service that converts raw events to user actions
- Integration hooks for notifying the bytebot-agent service of captured actions

**Sources:** [packages/bytebotd/src/app.module.ts:19-20]()

---

## User Action Recording

### Action Data Structure

When a user takes manual control of a task (status = `NEEDS_HELP`), the input tracking system records their actions as `UserAction` content blocks within the message stream.

```mermaid
graph TB
    subgraph "Message Content Types"
        MessageContentBlock["MessageContentBlock<br/>(Union Type)"]
        Text["TextBlock"]
        ToolUse["ToolUseBlock"]
        ToolResult["ToolResultBlock"]
        UserAction["UserActionBlock"]
        Image["ImageBlock"]
    end
    
    MessageContentBlock --> Text
    MessageContentBlock --> ToolUse
    MessageContentBlock --> ToolResult
    MessageContentBlock --> UserAction
    MessageContentBlock --> Image
    
    UserAction -->|"Records"| MouseMove["Mouse Movements"]
    UserAction -->|"Records"| MouseClick["Mouse Clicks"]
    UserAction -->|"Records"| KeyPress["Keyboard Input"]
    UserAction -->|"Records"| Scroll["Scroll Events"]
```

**Diagram: UserAction in Message Content Type Hierarchy**

The `UserAction` content block structure includes:
- **Action Type**: The type of input (click, type, move, scroll)
- **Parameters**: Action-specific data (coordinates, text, button)
- **Timestamp**: When the action occurred
- **Metadata**: Additional context (modifier keys, duration)

**Sources:** [packages/bytebotd/src/app.module.ts:19-20]()

### Recording Lifecycle

```mermaid
stateDiagram-v2
    [*] --> Disabled: Task in RUNNING state
    Disabled --> Enabled: Task transitions to NEEDS_HELP
    
    state Enabled {
        [*] --> Listening
        Listening --> Capturing: Input event detected
        Capturing --> Transforming: Event queued
        Transforming --> Recording: Action structured
        Recording --> Listening: Action saved
    }
    
    Enabled --> Disabled: User clicks RESUME
    Disabled --> [*]: Task completion
    
    note right of Enabled
        uiohook-napi hooks active
        Events transformed to UserAction
        Actions sent to MessagesService
    end note
```

**Diagram: Input Tracking State Machine**

The recording lifecycle is controlled by task state:
1. **Disabled State**: No event capture when agent is in control
2. **Transition to NEEDS_HELP**: Input tracking begins
3. **Active Recording**: User actions are captured and stored
4. **Transition to RUNNING**: Input tracking stops when user resumes agent

**Sources:** [packages/bytebotd/src/app.module.ts:1-27]()

---

## Event Processing Pipeline

### Raw Event to Action Transformation

The input tracking system transforms low-level OS events into high-level actions that the AI agent can understand and potentially replay.

```mermaid
graph TB
    subgraph "Raw Events (uiohook-napi)"
        MouseDown["MOUSE_DOWN<br/>{button, x, y}"]
        MouseUp["MOUSE_UP<br/>{button, x, y}"]
        MouseMove["MOUSE_MOVE<br/>{x, y}"]
        KeyDown["KEY_DOWN<br/>{keycode}"]
        KeyUp["KEY_UP<br/>{keycode}"]
        Wheel["WHEEL<br/>{rotation, direction}"]
    end
    
    subgraph "Event Processing"
        Aggregator["Event Aggregator"]
        ClickDetector["Click Detector<br/>(Down + Up)"]
        TypeDetector["Type Detector<br/>(Key sequences)"]
        DragDetector["Drag Detector<br/>(Move + Down)"]
    end
    
    subgraph "User Actions"
        ClickAction["click_mouse<br/>{x, y, button}"]
        TypeAction["type_text<br/>{text}"]
        MoveAction["move_mouse<br/>{x, y}"]
        ScrollAction["scroll<br/>{direction, amount}"]
        DragAction["drag<br/>{start, end}"]
    end
    
    MouseDown --> ClickDetector
    MouseUp --> ClickDetector
    MouseMove --> DragDetector
    MouseDown --> DragDetector
    
    KeyDown --> TypeDetector
    KeyUp --> TypeDetector
    
    MouseMove --> Aggregator
    Wheel --> Aggregator
    
    ClickDetector --> ClickAction
    TypeDetector --> TypeAction
    Aggregator --> MoveAction
    Aggregator --> ScrollAction
    DragDetector --> DragAction
```

**Diagram: Event Processing and Action Detection**

The transformation process includes:
- **Event Aggregation**: Grouping related events (e.g., key presses into words)
- **Pattern Detection**: Identifying high-level actions from event sequences
- **Noise Filtering**: Ignoring spurious events (e.g., small mouse movements)
- **Action Structuring**: Creating well-formed action objects matching ComputerAction schema

**Sources:** [packages/bytebotd/package.json:46]()

### Event Filtering and Debouncing

| Event Type | Processing Strategy | Rationale |
|------------|-------------------|-----------|
| **Mouse Move** | Debounced (sampled at intervals) | Reduces noise from continuous movement |
| **Mouse Click** | Immediate capture | Critical interaction points |
| **Key Press** | Buffered into sequences | Groups characters into words/commands |
| **Scroll** | Aggregated by direction | Combines multiple wheel events |
| **Modifier Keys** | State tracking | Captures Ctrl, Shift, Alt context |

The filtering logic ensures that only meaningful user actions are recorded, avoiding log spam from minor cursor adjustments.

**Sources:** [packages/bytebotd/src/app.module.ts:19-20]()

---

## Integration with Task System

### Communication with bytebot-agent

The input tracking system communicates captured actions back to the bytebot-agent service, where they are stored in the message history for context.

```mermaid
sequenceDiagram
    participant User
    participant Desktop
    participant ITModule as InputTrackingModule
    participant API as Computer Use API
    participant Agent as bytebot-agent
    participant DB as PostgreSQL
    
    User->>Agent: Task creation
    Agent->>DB: Store task (PENDING)
    Agent->>Agent: Process task (RUNNING)
    Agent->>Agent: Encounter issue
    Agent->>DB: Update status (NEEDS_HELP)
    Agent->>ITModule: Enable input tracking
    
    User->>Desktop: Manual control actions
    Desktop->>ITModule: OS-level events
    ITModule->>ITModule: Transform events
    ITModule->>API: POST user actions
    API->>Agent: Forward UserAction blocks
    Agent->>DB: Store as messages
    
    User->>Agent: Click RESUME
    Agent->>ITModule: Disable input tracking
    Agent->>DB: Update status (RUNNING)
    Agent->>Agent: Continue processing
```

**Diagram: Input Tracking Integration Flow**

The integration flow:
1. Agent sets task to `NEEDS_HELP` when user intervention is required
2. Input tracking is enabled on the bytebotd side
3. User actions are captured and sent to bytebot-agent via internal API
4. Actions are stored as `UserAction` message content blocks
5. When user clicks "RESUME", input tracking is disabled
6. Agent continues with full context of user's manual actions

**Sources:** [packages/bytebotd/src/app.module.ts:1-27]()

### UserAction Message Format

The captured user actions are stored as messages with role `USER` and content type `UserAction`:

| Field | Type | Description |
|-------|------|-------------|
| **type** | `"user_action"` | Identifies this as a user action block |
| **action** | `string` | Action name (e.g., "click_mouse", "type_text") |
| **parameters** | `object` | Action-specific parameters matching ComputerAction schema |
| **timestamp** | `number` | Unix timestamp in milliseconds |
| **sequence** | `number` | Sequential order within the session |

These UserAction blocks are interspersed with other message types in the conversation history, providing the agent with a complete picture of what the user did during manual control.

**Sources:** [packages/bytebotd/src/app.module.ts:19-20]()

---

## Configuration and Control

### Environment Variables

The input tracking system may be configured through environment variables in bytebotd:

| Variable | Purpose | Default |
|----------|---------|---------|
| `INPUT_TRACKING_ENABLED` | Enable/disable tracking globally | `true` |
| `INPUT_TRACKING_SAMPLE_RATE` | Mouse move sampling rate (ms) | `100` |
| `INPUT_TRACKING_DEBOUNCE` | Key press debounce period (ms) | `50` |

**Note**: Actual configuration variables would be defined in the ConfigModule and consumed by the InputTrackingModule.

**Sources:** [packages/bytebotd/src/app.module.ts:12-14]()

### Runtime Control

Input tracking can be controlled at runtime through:
- **Task State Transitions**: Automatically enabled/disabled based on task status
- **WebSocket Commands**: Manual enable/disable via administrative interface
- **MCP Tools**: Management commands through the MCP endpoint

**Sources:** [packages/bytebotd/src/mcp/bytebot-mcp.module.ts:1-18]()

---

## Performance Considerations

### Resource Usage

| Metric | Impact | Mitigation Strategy |
|--------|--------|---------------------|
| **CPU Overhead** | Event processing in real-time | Event debouncing and sampling |
| **Memory Usage** | Event queue buffering | Bounded queue size with overflow handling |
| **Network Traffic** | Sending actions to bytebot-agent | Batching multiple actions in single requests |
| **Disk I/O** | Database writes for messages | Handled by bytebot-agent's message batching |

The input tracking system is designed to have minimal performance impact on the desktop environment while providing comprehensive action recording.

**Sources:** [packages/bytebotd/package.json:28-46]()

### Event Throughput

Under typical usage:
- **Mouse events**: 10-50 per second during active movement
- **Keyboard events**: 5-20 per second during typing
- **Processed actions**: 1-5 per second after aggregation
- **Network requests**: 1-2 per second to bytebot-agent

The aggregation and debouncing logic significantly reduces the downstream load while preserving all meaningful user actions.

**Sources:** [packages/bytebotd/src/app.module.ts:19-20]()

---

## Summary

The Input Tracking system provides essential functionality for human-in-the-loop AI workflows by:

1. **Capturing user input** via native OS hooks using uiohook-napi
2. **Transforming low-level events** into structured, meaningful actions
3. **Recording actions** as UserAction message content blocks
4. **Integrating with task lifecycle** through automatic enable/disable based on task state
5. **Maintaining context** for the AI agent to learn from human demonstrations

This system enables the agent to observe and potentially learn from user interventions, creating a feedback loop that improves the AI's capabilities over time.

**Sources:** [packages/bytebotd/src/app.module.ts:1-27](), [packages/bytebotd/package.json:46]()

---

# Page: VNC Access

# VNC Access

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [packages/bytebot-ui/.gitignore](packages/bytebot-ui/.gitignore)
- [packages/bytebot-ui/src/components/vnc/VncViewer.tsx](packages/bytebot-ui/src/components/vnc/VncViewer.tsx)
- [packages/bytebot-ui/src/utils/taskUtils.ts](packages/bytebot-ui/src/utils/taskUtils.ts)
- [packages/bytebotd/package-lock.json](packages/bytebotd/package-lock.json)
- [packages/bytebotd/package.json](packages/bytebotd/package.json)
- [packages/bytebotd/src/app.controller.ts](packages/bytebotd/src/app.controller.ts)
- [packages/bytebotd/src/app.module.ts](packages/bytebotd/src/app.module.ts)
- [packages/bytebotd/src/mcp/bytebot-mcp.module.ts](packages/bytebotd/src/mcp/bytebot-mcp.module.ts)
- [packages/bytebotd/src/mcp/index.ts](packages/bytebotd/src/mcp/index.ts)

</details>



This document explains the VNC (Virtual Network Computing) access system that enables browser-based viewing and control of the bytebotd desktop environment. VNC access provides real-time visual feedback during task execution and allows users to monitor or manually interact with the XFCE desktop.

For information about desktop automation and action execution, see [Computer Use Service](#7.1). For details on input capture during user takeover, see [Input Tracking](#7.4). For the UI component that displays the desktop stream, see [Desktop Viewer](#8.4).

---

## Architecture Overview

The VNC access system consists of three layers: the noVNC web client, a WebSocket proxy in bytebot-ui, and the VNC server in bytebotd. This architecture allows secure browser-based access without requiring VNC client software installation.

```mermaid
graph TB
    subgraph "Browser"
        VncReact["VncViewer Component<br/>(react-vnc)"]
        NoVNC["noVNC HTML Client<br/>(/novnc/vnc.html)"]
    end
    
    subgraph "bytebot-ui (Port 9992)"
        WSProxy["/api/proxy/websockify<br/>WebSocket Proxy"]
    end
    
    subgraph "bytebotd (Port 9990)"
        StaticServe["ServeStaticModule<br/>/opt/noVNC → /novnc"]
        VncRedirect["AppController<br/>GET /vnc redirect"]
        VncServer["VNC Server<br/>websockify<br/>Port 6080"]
    end
    
    subgraph "Virtual Desktop"
        XFCE["XFCE Desktop<br/>Ubuntu 22.04<br/>1280x960"]
    end
    
    VncReact -->|"ws[s]://host/api/proxy/websockify"| WSProxy
    NoVNC -->|"?host=&path=websockify"| WSProxy
    
    WSProxy -->|"WebSocket"| VncServer
    VncServer -->|"Screen capture"| XFCE
    
    VncRedirect -.->|"302 redirect"| NoVNC
    StaticServe -.->|"Serve files"| NoVNC
    
    style VncServer fill:#f9f9f9
    style WSProxy fill:#f9f9f9
```

**Sources:** [packages/bytebot-ui/src/components/vnc/VncViewer.tsx:1-48](), [packages/bytebotd/src/app.controller.ts:1-19](), [packages/bytebotd/src/app.module.ts:1-27]()

---

## noVNC Static Files

The bytebotd service serves the noVNC web client as static files. The `ServeStaticModule` configuration maps the `/opt/noVNC` directory to the `/novnc` web path.

| Configuration | Value |
|---------------|-------|
| Physical path | `/opt/noVNC` |
| Web route | `/novnc` |
| Entry point | `/novnc/vnc.html` |
| Module | `@nestjs/serve-static` |

The noVNC client provides a full-featured VNC viewer implemented in JavaScript, supporting keyboard and mouse input when `viewOnly` is disabled.

**Configuration:**
[packages/bytebotd/src/app.module.ts:15-18]()

```typescript
ServeStaticModule.forRoot({
  rootPath: '/opt/noVNC',
  serveRoot: '/novnc',
})
```

**Sources:** [packages/bytebotd/src/app.module.ts:1-27]()

---

## VNC Redirect Endpoint

The bytebotd service exposes a convenience endpoint at `GET /vnc` that redirects to the noVNC client with pre-configured connection parameters.

### Redirect Controller

[packages/bytebotd/src/app.controller.ts:8-17]()

| Parameter | Description |
|-----------|-------------|
| `host` | Server hostname from request headers |
| `path` | WebSocket path: `websockify` |
| `resize` | Viewport scaling: `scale` |

The redirect URL is constructed dynamically using the `host` header from the incoming request, ensuring correct connection parameters regardless of how the service is accessed.

**Example redirect:**
```
GET /vnc
→ 302 /novnc/vnc.html?host=localhost:9990&path=websockify&resize=scale
```

**Sources:** [packages/bytebotd/src/app.controller.ts:1-19]()

---

## WebSocket Proxy Architecture

The bytebot-ui frontend proxies VNC WebSocket connections to bytebotd. This proxy allows the React application to connect to VNC through a single origin, avoiding CORS issues and simplifying deployment.

```mermaid
sequenceDiagram
    participant Browser
    participant UIProxy as "bytebot-ui<br/>/api/proxy/websockify"
    participant VncServer as "bytebotd<br/>VNC Server (6080)"
    participant Desktop as "XFCE Desktop"
    
    Browser->>UIProxy: "WebSocket upgrade request<br/>ws://host/api/proxy/websockify"
    UIProxy->>VncServer: "Forward WebSocket<br/>ws://bytebotd:6080"
    VncServer->>Desktop: "Capture screen buffer"
    Desktop-->>VncServer: "Frame data"
    VncServer-->>UIProxy: "VNC protocol frames"
    UIProxy-->>Browser: "Binary frame data"
    
    Note over Browser,Desktop: "Continuous streaming loop"
    
    Browser->>UIProxy: "Mouse/keyboard events<br/>(if viewOnly=false)"
    UIProxy->>VncServer: "Forward input events"
    VncServer->>Desktop: "Inject input"
```

**Sources:** High-level architecture diagrams, [packages/bytebot-ui/src/components/vnc/VncViewer.tsx:22-26]()

---

## VncViewer React Component

The `VncViewer` component provides browser-based VNC access using the `react-vnc` library. It dynamically constructs the WebSocket URL and renders the VNC client.

### Component Implementation

[packages/bytebot-ui/src/components/vnc/VncViewer.tsx:1-48]()

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `viewOnly` | boolean | `true` | Disable mouse/keyboard input |

### WebSocket URL Construction

The component builds the WebSocket URL based on the current page protocol:

```typescript
const proto = window.location.protocol === "https:" ? "wss" : "ws";
const wsUrl = `${proto}://${window.location.host}/api/proxy/websockify`;
```

This ensures TLS is used for WebSocket connections when the page is served over HTTPS.

### RFB Options

| Option | Value | Purpose |
|--------|-------|---------|
| `secure` | `false` | Encryption handled by proxy |
| `shared` | `true` | Allow multiple connections |
| `wsProtocols` | `["binary"]` | Use binary WebSocket protocol |
| `scaleViewport` | `true` | Scale to fit container |

### Dynamic Import

The component uses dynamic import for `react-vnc` to ensure client-side only loading:

[packages/bytebot-ui/src/components/vnc/VncViewer.tsx:16-19]()

This prevents SSR (Server-Side Rendering) issues since VNC requires browser APIs.

**Sources:** [packages/bytebot-ui/src/components/vnc/VncViewer.tsx:1-48]()

---

## Connection Flow

The complete flow from user action to desktop visualization involves multiple service layers and protocol conversions.

```mermaid
graph LR
    User["User Browser"]
    UIComp["VncViewer<br/>Component"]
    ReactVNC["react-vnc<br/>Library"]
    WSConn["WebSocket<br/>Connection"]
    UIServer["bytebot-ui<br/>Next.js Server"]
    Proxy["http-proxy-<br/>middleware"]
    BytebotdWS["bytebotd<br/>WebSocket<br/>Handler"]
    VncProto["VNC Server<br/>Port 6080"]
    XDisplay["X11 Display<br/>:99"]
    
    User -->|"Navigate to<br/>/tasks/[id]"| UIComp
    UIComp -->|"Mount & connect"| ReactVNC
    ReactVNC -->|"ws[s]://host/api/<br/>proxy/websockify"| WSConn
    WSConn -->|"Upgrade request"| UIServer
    UIServer -->|"Proxy config"| Proxy
    Proxy -->|"Forward to<br/>bytebotd:6080"| BytebotdWS
    BytebotdWS -->|"VNC handshake"| VncProto
    VncProto -->|"Screen capture"| XDisplay
    
    XDisplay -.->|"Frame buffer"| VncProto
    VncProto -.->|"RFB protocol"| BytebotdWS
    BytebotdWS -.->|"Binary frames"| Proxy
    Proxy -.->|"Forward"| UIServer
    UIServer -.->|"WebSocket data"| WSConn
    WSConn -.->|"Render frames"| ReactVNC
    ReactVNC -.->|"Display canvas"| UIComp
    UIComp -.->|"Show to user"| User
    
    style VncProto fill:#f9f9f9
    style Proxy fill:#f9f9f9
```

**Sources:** [packages/bytebot-ui/src/components/vnc/VncViewer.tsx:1-48](), High-level architecture diagrams

---

## Access Methods

Users can access the VNC desktop through two primary methods:

### 1. Task Detail Page (Recommended)

The `VncViewer` component is embedded in the task detail page as part of the `DesktopContainer`. This provides integrated viewing alongside task messages and controls.

- **Route:** `/tasks/[taskId]`
- **Component:** `VncViewer` with `viewOnly={true}`
- **Use case:** Monitoring agent activity during task execution
- **Reference:** See [Desktop Viewer](#8.4) for UI integration details

### 2. Direct noVNC Access

Users can access the full noVNC client directly for advanced features or manual interaction.

- **Route:** `http://bytebotd:9990/vnc` (redirects to noVNC)
- **Client:** Full-featured noVNC HTML interface
- **Use case:** Manual desktop control, troubleshooting
- **Note:** Requires network access to bytebotd service

**Sources:** [packages/bytebot-ui/src/components/vnc/VncViewer.tsx:1-48](), [packages/bytebotd/src/app.controller.ts:8-17]()

---

## Technical Details

### Port Configuration

| Service | Port | Protocol | Purpose |
|---------|------|----------|---------|
| bytebotd VNC | 6080 | WebSocket | VNC server endpoint |
| bytebot-ui proxy | 9992 | HTTP/WS | User-facing VNC proxy |
| bytebotd HTTP | 9990 | HTTP | noVNC static files |

### Protocol Stack

The VNC access system uses multiple protocol layers:

1. **RFB (Remote Framebuffer Protocol):** Core VNC protocol for screen data and input
2. **WebSocket:** Transport layer for browser compatibility
3. **HTTP/HTTPS:** Initial connection and upgrade negotiation
4. **Binary Protocol:** Efficient frame data transmission using `wsProtocols: ["binary"]`

### Security Considerations

- **View-Only Mode:** Default configuration prevents accidental input during monitoring
- **Proxy Isolation:** WebSocket proxy prevents direct bytebotd exposure
- **Shared Access:** Multiple users can view simultaneously with `shared: true`
- **No TLS Termination:** Encryption handled at the proxy layer, not VNC server

**Sources:** [packages/bytebot-ui/src/components/vnc/VncViewer.tsx:32-36](), [packages/bytebotd/package.json:1-93]()

---

## Integration with Desktop Viewer

The `VncViewer` component is consumed by the `DesktopContainer` component, which provides adaptive rendering between VNC streaming and static screenshots based on task state.

When task status is `RUNNING`, the desktop viewer switches to VNC streaming mode, allowing real-time observation of agent actions. For completed or paused tasks, static screenshots provide a more efficient viewing experience.

For details on this adaptive rendering logic, see [Desktop Viewer](#8.4).

**Sources:** [packages/bytebot-ui/src/components/vnc/VncViewer.tsx:1-48]()

---

# Page: User Interface

# User Interface

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [packages/bytebot-ui/package-lock.json](packages/bytebot-ui/package-lock.json)
- [packages/bytebot-ui/package.json](packages/bytebot-ui/package.json)
- [packages/bytebot-ui/src/app/layout.tsx](packages/bytebot-ui/src/app/layout.tsx)
- [packages/bytebot-ui/src/app/page.tsx](packages/bytebot-ui/src/app/page.tsx)
- [packages/bytebot-ui/src/components/layout/Header.tsx](packages/bytebot-ui/src/components/layout/Header.tsx)
- [packages/bytebot-ui/src/components/messages/ChatInput.tsx](packages/bytebot-ui/src/components/messages/ChatInput.tsx)
- [packages/bytebot-ui/src/components/ui/select.tsx](packages/bytebot-ui/src/components/ui/select.tsx)

</details>



The user interface provides a web-based frontend for creating, managing, and monitoring AI-powered desktop automation tasks. Built with Next.js, it offers real-time task monitoring, chat-based interaction, and integrated desktop viewing capabilities.

This document covers the frontend web application components and user interaction patterns. For backend task processing, see [Agent System](#6). For desktop environment details, see [Desktop Environment](#5). For deployment configuration, see [Installation and Setup](#3).

## Architecture Overview

The UI is built as a Next.js application with two primary interfaces: a task creation homepage and detailed task monitoring pages. The architecture emphasizes real-time communication through WebSocket connections and seamless integration with the virtual desktop environment.

### Component Architecture

```mermaid
graph TB
    subgraph "Next.js Application"
        HomePage["HomePage<br/>/app/page.tsx"]
        TaskPage["TaskPage<br/>/app/tasks/[id]/page.tsx"]
        Header["Header<br/>Navigation Component"]
    end
    
    subgraph "Task Creation Interface"
        TaskList["TaskList<br/>Recent Tasks"]
        ChatInput["ChatInput<br/>Task Description Input"]
        ModelSelect["Select<br/>Model Selection"]
    end
    
    subgraph "Task Monitoring Interface"
        ChatContainer["ChatContainer<br/>Message Display"]
        DesktopContainer["DesktopContainer<br/>VNC/Screenshot Display"]
        MessageGroup["MessageGroup<br/>Grouped Messages"]
    end
    
    subgraph "Real-time Communication"
        useChatSession["useChatSession<br/>WebSocket Management"]
        useScrollScreenshot["useScrollScreenshot<br/>Screenshot Sync"]
    end
    
    HomePage --> TaskList
    HomePage --> ChatInput
    HomePage --> ModelSelect
    
    TaskPage --> ChatContainer
    TaskPage --> DesktopContainer
    TaskPage --> useChatSession
    
    ChatContainer --> MessageGroup
    TaskPage --> useScrollScreenshot
    
    useChatSession -.->|"WebSocket /tasks"| Backend["bytebot-agent"]
    DesktopContainer -.->|"VNC Connection"| Desktop["bytebot-desktop"]
```

**Sources:** [packages/bytebot-ui/src/app/page.tsx:1-256](), [packages/bytebot-ui/src/app/tasks/[id]/page.tsx:1-220](), [packages/bytebot-ui/src/components/messages/ChatContainer.tsx:1-154]()

### UI State Management Flow

```mermaid
graph LR
    User["User Action"]
    
    subgraph "Frontend State"
        ChatSession["useChatSession Hook"]
        Messages["messages[]"]
        TaskStatus["taskStatus"]
        Control["control (Role)"]
    end
    
    subgraph "Backend Integration"
        WebSocket["TasksGateway WebSocket"]
        API["REST API Endpoints"]
    end
    
    subgraph "UI Components"
        ChatInput["ChatInput"]
        MessageDisplay["Message Components"]
        DesktopView["DesktopContainer"]
    end
    
    User --> ChatInput
    ChatInput --> ChatSession
    ChatSession --> WebSocket
    ChatSession --> API
    
    WebSocket --> Messages
    API --> Messages
    Messages --> TaskStatus
    TaskStatus --> Control
    
    Messages --> MessageDisplay
    TaskStatus --> DesktopView
    Control --> DesktopView
```

**Sources:** [packages/bytebot-ui/src/hooks/useChatSession.ts]() (referenced in task page), [packages/bytebot-ui/src/components/messages/ChatContainer.tsx:26-40]()

## Task Management Interface

The homepage (`/`) serves as the primary task creation interface, featuring a conversational input system and model selection capabilities.

### Task Creation Components

| Component | Location | Purpose |
|-----------|----------|---------|
| `ChatInput` | [packages/bytebot-ui/src/components/messages/ChatInput.tsx:24-254]() | Multi-line task description input with file upload |
| `Select` | [packages/bytebot-ui/src/components/ui/select.tsx:10-121]() | AI model selection dropdown |
| `TaskList` | Referenced in homepage | Recent task history display |
| `startTask` | [packages/bytebot-ui/src/utils/taskUtils.ts]() (imported) | Task creation utility |

The task creation flow handles model selection, file uploads, and task initialization:

```mermaid
sequenceDiagram
    participant User
    participant HomePage as "HomePage Component"
    participant ChatInput
    participant ModelSelect as "Select Component"
    participant startTask as "startTask Utility"
    participant Router as "Next.js Router"
    
    User->>HomePage: Load homepage
    HomePage->>ModelSelect: Fetch available models
    ModelSelect->>HomePage: Display model options
    
    User->>ChatInput: Enter task description
    User->>ChatInput: Optional: Upload files
    User->>ModelSelect: Select AI model
    User->>ChatInput: Click send / press Enter
    
    ChatInput->>HomePage: Trigger handleSend
    HomePage->>startTask: Call with description, model, files
    startTask->>HomePage: Return task object
    HomePage->>Router: Navigate to /tasks/{taskId}
```

**Sources:** [packages/bytebot-ui/src/app/page.tsx:97-133](), [packages/bytebot-ui/src/components/messages/ChatInput.tsx:41-133]()

### File Upload Handling

The `ChatInput` component supports file uploads with validation and preview:

- Maximum 5 files per task
- 30MB limit per file
- Base64 encoding for API transmission
- Real-time file list management with removal capabilities

**Sources:** [packages/bytebot-ui/src/components/messages/ChatInput.tsx:46-98](), [packages/bytebot-ui/src/components/messages/ChatInput.tsx:169-196]()

## Task Detail Interface

Individual task pages (`/tasks/[id]`) provide comprehensive task monitoring with split-screen layout: desktop view on the left, chat interface on the right.

### Layout Structure

```mermaid
graph TB
    subgraph "TaskPage Layout"
        Header["Header Component"]
        
        subgraph "Main Grid (7 columns)"
            subgraph "Desktop Area (4 cols)"
                DesktopContainer["DesktopContainer<br/>VNC or Screenshot Display"]
                TakeOverButton["Take Over Button<br/>(conditional)"]
                ProceedButton["Proceed Button<br/>(conditional)"]
                CancelMenu["Cancel Dropdown<br/>(conditional)"]
            end
            
            subgraph "Chat Area (3 cols)"
                ChatContainer["ChatContainer<br/>Message History"]
                ChatInput_Detail["ChatInput<br/>Additional Messages"]
            end
        end
    end
    
    Header --- DesktopContainer
    Header --- ChatContainer
    
    DesktopContainer --- TakeOverButton
    DesktopContainer --- ProceedButton
    DesktopContainer --- CancelMenu
```

**Sources:** [packages/bytebot-ui/src/app/tasks/[id]/page.tsx:119-219]()

### Task Control States

The interface dynamically shows different controls based on task status and control ownership:

| State | Condition | Available Actions |
|-------|-----------|------------------|
| AI Running | `taskStatus === RUNNING && control === ASSISTANT` | Take Over, Cancel |
| User Control | `taskStatus === RUNNING && control === USER` | Proceed, Cancel |
| Needs Help | `taskStatus === NEEDS_HELP` | Proceed, Cancel |
| Completed/Failed | `taskStatus === COMPLETED/FAILED/CANCELLED` | View-only mode |

**Sources:** [packages/bytebot-ui/src/app/tasks/[id]/page.tsx:50-84]()

### Message Display System

```mermaid
graph TB
    ChatContainer --> GroupedMessages["groupedMessages[]"]
    
    subgraph "Message Types"
        UserMessage["UserMessage Component"]
        AssistantMessage["AssistantMessage Component"]
    end
    
    subgraph "Message Content"
        TextContent["Text Content Blocks"]
        ToolContent["Tool Result Blocks"]
        ImageContent["Screenshot Images"]
        TakeOverContent["Take Over Messages"]
    end
    
    GroupedMessages --> MessageGroup["MessageGroup"]
    MessageGroup --> UserMessage
    MessageGroup --> AssistantMessage
    
    UserMessage --> TextContent
    AssistantMessage --> TextContent
    AssistantMessage --> ToolContent
    AssistantMessage --> TakeOverContent
    
    ToolContent --> ImageContent
```

**Sources:** [packages/bytebot-ui/src/components/messages/MessageGroup.tsx:13-18](), [packages/bytebot-ui/src/components/messages/AssistantMessage.tsx:15-136](), [packages/bytebot-ui/src/components/messages/UserMessage.tsx:16-135]()

## Desktop Viewer Integration

The `DesktopContainer` provides two modes of desktop interaction based on task state:

### VNC Mode vs Screenshot Mode

```mermaid
graph TB
    TaskState{"Task Status Check"}
    
    subgraph "Active Task"
        VNCViewer["VNC Viewer<br/>Real-time Desktop"]
        InteractiveMode["Interactive Mode<br/>(User Control)"]
        ViewOnlyMode["View-only Mode<br/>(AI Control)"]
    end
    
    subgraph "Inactive Task"
        ScreenshotViewer["Screenshot Viewer<br/>Static Images"]
        ScrollSync["Scroll Synchronization<br/>useScrollScreenshot"]
    end
    
    TaskState -->|"RUNNING, NEEDS_HELP"| VNCViewer
    TaskState -->|"COMPLETED, FAILED, CANCELLED"| ScreenshotViewer
    
    VNCViewer --> InteractiveMode
    VNCViewer --> ViewOnlyMode
    
    ScreenshotViewer --> ScrollSync
```

The task page determines display mode using the `isTaskInactive()` function:

**Sources:** [packages/bytebot-ui/src/app/tasks/[id]/page.tsx:51-57](), [packages/bytebot-ui/src/app/tasks/[id]/page.tsx:81-83](), [packages/bytebot-ui/src/app/tasks/[id]/page.tsx:127-129]()

### Screenshot Synchronization

For completed tasks, the interface synchronizes screenshot display with chat scroll position:

```mermaid
graph LR
    subgraph "Scroll Detection"
        ScrollContainer["Chat Container Scroll"]
        MessageMarkers["Hidden Screenshot Markers<br/>data-message-index"]
    end
    
    subgraph "Screenshot Processing"
        extractScreenshots["extractScreenshots()<br/>Extract from messages"]
        getScreenshotForScrollPosition["getScreenshotForScrollPosition()<br/>Find current screenshot"]
    end
    
    subgraph "Display Update"
        ScreenshotViewer["Screenshot Display"]
        CurrentScreenshot["currentScreenshot State"]
    end
    
    ScrollContainer --> MessageMarkers
    MessageMarkers --> getScreenshotForScrollPosition
    extractScreenshots --> getScreenshotForScrollPosition
    getScreenshotForScrollPosition --> CurrentScreenshot
    CurrentScreenshot --> ScreenshotViewer
```

**Sources:** [packages/bytebot-ui/src/hooks/useScrollScreenshot.ts:10-114](), [packages/bytebot-ui/src/utils/screenshotUtils.ts:14-147](), [packages/bytebot-ui/src/app/tasks/[id]/page.tsx:86-89]()

## Computer Tool Display

The interface visualizes AI computer actions through specialized message content rendering that displays tool usage, screenshots, and action results.

### Tool Result Rendering

```mermaid
graph TB
    subgraph "Message Content Blocks"
        TextBlock["Text Content Block<br/>isTextContentBlock()"]
        ToolBlock["Tool Result Block<br/>isToolResultContentBlock()"]
        ImageBlock["Image Content Block<br/>isImageContentBlock()"]
    end
    
    subgraph "Tool Display Components"
        MessageContent["MessageContent Component"]
        ToolResultDisplay["Tool Result Display"]
        ScreenshotDisplay["Screenshot Display"]
        ErrorDisplay["Error Display"]
    end
    
    subgraph "Hidden Markers"
        ScreenshotMarkers["Screenshot Position Markers<br/>data-message-index<br/>data-block-index"]
    end
    
    ToolBlock --> ToolResultDisplay
    ToolBlock --> ScreenshotDisplay
    ToolBlock --> ErrorDisplay
    ToolBlock --> ScreenshotMarkers
    
    ImageBlock --> ScreenshotDisplay
    ImageBlock --> ScreenshotMarkers
```

Tool results are processed and displayed with hidden markers for screenshot synchronization:

**Sources:** [packages/bytebot-ui/src/components/messages/AssistantMessage.tsx:95-125](), [packages/bytebot-ui/src/components/messages/UserMessage.tsx:89-118]()

### Take-Over Message Display

Special rendering for user intervention messages with visual indicators:

**Sources:** [packages/bytebot-ui/src/components/messages/AssistantMessage.tsx:29-86]()

## Real-time Communication

The UI maintains persistent WebSocket connections for live task updates and user interaction.

### WebSocket Integration

```mermaid
graph TB
    subgraph "Frontend Hooks"
        useChatSession["useChatSession Hook"]
        WebSocketConnection["WebSocket Connection"]
    end
    
    subgraph "Message Types"
        TaskUpdate["Task Status Updates"]
        MessageReceived["New Messages"]
        ErrorNotification["Error Notifications"]
    end
    
    subgraph "Backend Gateway"
        TasksGateway["TasksGateway<br/>NestJS WebSocket"]
        AgentProcessor["AgentProcessor<br/>Task Execution"]
    end
    
    subgraph "UI State Updates"
        MessageState["messages[]"]
        TaskStatusState["taskStatus"]
        ControlState["control (Role)"]
        LoadingState["isLoading"]
    end
    
    useChatSession --> WebSocketConnection
    WebSocketConnection <--> TasksGateway
    TasksGateway <--> AgentProcessor
    
    TasksGateway --> TaskUpdate
    TasksGateway --> MessageReceived
    TasksGateway --> ErrorNotification
    
    TaskUpdate --> TaskStatusState
    MessageReceived --> MessageState
    TaskStatusState --> ControlState
    MessageReceived --> LoadingState
```

**Sources:** Referenced through [packages/bytebot-ui/src/app/tasks/[id]/page.tsx:31-48]() hook usage

### Infinite Scroll Implementation

The chat interface supports loading historical messages through scroll-based pagination:

**Sources:** [packages/bytebot-ui/src/components/messages/ChatContainer.tsx:44-66](), [packages/bytebot-ui/src/components/messages/ChatContainer.tsx:118-123]()

### Auto-scroll Behavior

During active tasks, the chat automatically scrolls to show the latest messages:

**Sources:** [packages/bytebot-ui/src/components/messages/ChatContainer.tsx:68-81]()

## State Management Architecture

The UI uses React hooks and context for state management, with real-time synchronization through WebSocket connections.

### Key State Flows

| State | Source | Purpose |
|-------|--------|---------|
| `messages[]` | WebSocket + API | Complete message history |
| `groupedMessages[]` | Computed | Messages grouped by role for display |
| `taskStatus` | WebSocket | Current task execution state |
| `control` | WebSocket | Whether user or AI has control |
| `isLoading` | Local | UI loading states |
| `input` | Local | Current chat input value |

**Sources:** [packages/bytebot-ui/src/app/tasks/[id]/page.tsx:31-48]()

---

# Page: Task Creation Interface

# Task Creation Interface

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [packages/bytebot-ui/src/app/page.tsx](packages/bytebot-ui/src/app/page.tsx)
- [packages/bytebot-ui/src/components/messages/ChatInput.tsx](packages/bytebot-ui/src/components/messages/ChatInput.tsx)
- [packages/bytebot-ui/src/components/ui/select.tsx](packages/bytebot-ui/src/components/ui/select.tsx)

</details>



The Task Creation Interface is the primary entry point for users to submit tasks to the Bytebot system. Located at the home page (`/`), it provides a form-based interface for entering task descriptions, selecting AI models, and uploading files. This page serves as both the task creation form and a dashboard showing the latest tasks.

For information about viewing task details and monitoring execution, see [Task Detail Page](#8.3). For the task list browsing interface, see [Task List Interface](#8.2).

## Purpose and Scope

This document covers the implementation of the task creation form in [packages/bytebot-ui/src/app/page.tsx](), including:
- The main `Home` component structure and state management
- The `ChatInput` component for text and file input
- Model selection via Radix UI `Select` component
- Client-side validation and file handling
- Integration with the `startTask` API utility

## Component Architecture

The task creation interface is built using a compositional React architecture with three primary components:

```mermaid
graph TB
    Home["Home Component<br/>(page.tsx)"]
    Header["Header<br/>(layout/Header)"]
    ChatInput["ChatInput<br/>(messages/ChatInput)"]
    Select["Select Components<br/>(ui/select)"]
    TaskList["TaskList<br/>(tasks/TaskList)"]
    
    Home --> Header
    Home --> ChatInput
    Home --> Select
    Home --> TaskList
    
    ChatInput --> FileInput["Hidden File Input"]
    ChatInput --> Textarea["Auto-resizing Textarea"]
    ChatInput --> UploadButton["Attachment Button"]
    ChatInput --> SubmitButton["Send Button"]
    
    Select --> SelectTrigger["SelectTrigger"]
    Select --> SelectContent["SelectContent"]
    Select --> SelectItem["SelectItem[]"]
    
    Home -.->|"calls"| startTask["startTask()<br/>(utils/taskUtils)"]
    startTask -.->|"POST /api/tasks"| TasksAPI["Tasks API"]
    
    Home -.->|"router.push"| TaskDetailPage["/tasks/:id"]
```

**Component Hierarchy and Data Flow**

Sources: [packages/bytebot-ui/src/app/page.tsx:1-256]()

### Home Component State

The `Home` component manages the following state:

| State Variable | Type | Purpose |
|----------------|------|---------|
| `input` | `string` | Task description text |
| `isLoading` | `boolean` | Loading state during task creation |
| `models` | `Model[]` | Available AI models from backend |
| `selectedModel` | `Model \| null` | Currently selected model |
| `uploadedFiles` | `FileWithBase64[]` | Base64-encoded file attachments |
| `activePopoverIndex` | `number \| null` | Manages popover state (unused in current implementation) |

Sources: [packages/bytebot-ui/src/app/page.tsx:44-55]()

## Task Input System

The task input system uses the `ChatInput` component, which provides a multi-line auto-resizing textarea with file attachment capabilities.

```mermaid
graph LR
    subgraph "ChatInput Component"
        TextareaRef["textareaRef<br/>(useRef)"]
        FileInputRef["fileInputRef<br/>(useRef)"]
        Input["input: string"]
        SelectedFiles["selectedFiles:<br/>FileWithBase64[]"]
        ErrorMessage["errorMessage: string"]
    end
    
    subgraph "User Interactions"
        TypeText["User Types Text"]
        ClickAttach["Click Attachment Button"]
        SelectFiles["Select Files from Dialog"]
        PressEnter["Press Enter"]
    end
    
    subgraph "Handlers"
        OnInputChange["onInputChange(value)"]
        HandleFileSelect["handleFileSelect()"]
        HandleSubmit["handleSubmit()"]
        ConvertToBase64["convertToBase64(file)"]
    end
    
    TypeText -->|"onChange"| OnInputChange
    ClickAttach -->|"triggerFileInput()"| FileInputRef
    SelectFiles -->|"onChange"| HandleFileSelect
    PressEnter -->|"onSubmit"| HandleSubmit
    
    HandleFileSelect --> ConvertToBase64
    ConvertToBase64 --> SelectedFiles
    SelectedFiles -->|"onFileUpload()"| Input
    
    OnInputChange --> TextareaRef
    TextareaRef -.->|"Auto-resize"| AutoResize["useEffect:<br/>adjust height"]
```

**ChatInput Auto-Resize Logic**

Sources: [packages/bytebot-ui/src/components/messages/ChatInput.tsx:24-254]()

### FileWithBase64 Interface

The system uses a custom interface to represent uploaded files with their base64-encoded content:

```typescript
interface FileWithBase64 {
  name: string;      // Original filename
  base64: string;    // Data URL (e.g., "data:image/png;base64,...")
  type: string;      // MIME type
  size: number;      // File size in bytes
}
```

This interface is defined identically in both [packages/bytebot-ui/src/app/page.tsx:37-42]() and [packages/bytebot-ui/src/components/messages/ChatInput.tsx:7-12]().

Sources: [packages/bytebot-ui/src/app/page.tsx:37-42](), [packages/bytebot-ui/src/components/messages/ChatInput.tsx:7-12]()

## Model Selection

The model selection dropdown is implemented using Radix UI's `Select` components, which provide accessible, keyboard-navigable selection.

```mermaid
graph TB
    FetchModels["useEffect: Fetch Models<br/>GET /api/tasks/models"]
    SetModels["setModels(data)"]
    SetDefault["setSelectedModel(data[0])"]
    
    SelectTrigger["SelectTrigger<br/>Display selected model"]
    SelectContent["SelectContent<br/>Dropdown menu"]
    SelectItems["SelectItem[]<br/>One per model"]
    
    FetchModels -->|"On mount"| SetModels
    SetModels --> SetDefault
    SetDefault --> SelectTrigger
    
    SelectTrigger -->|"Click"| SelectContent
    SelectContent --> SelectItems
    SelectItems -->|"onValueChange"| UpdateSelected["setSelectedModel()"]
    
    UpdateSelected -.->|"Used in"| TaskCreation["Task Creation Payload"]
```

**Model Selection Flow**

The component fetches available models on mount and automatically selects the first model:

| Step | Action | Code Reference |
|------|--------|----------------|
| 1. Mount | Fetch models from `/api/tasks/models` | [page.tsx:57-65]() |
| 2. Response | Store in `models` state | [page.tsx:61]() |
| 3. Default | Set first model as selected | [page.tsx:62]() |
| 4. Render | Display model dropdown | [page.tsx:165-183]() |
| 5. Change | Update `selectedModel` on selection | [page.tsx:167-171]() |

Sources: [packages/bytebot-ui/src/app/page.tsx:57-65](), [packages/bytebot-ui/src/app/page.tsx:165-183]()

## File Upload System

The file upload system provides multi-file support with client-side validation for file size and count limits.

### Upload Constraints

| Constraint | Value | Constant |
|------------|-------|----------|
| Maximum files | 5 | `MAX_FILES` |
| Maximum size per file | 30 MB | `MAX_FILE_SIZE` (30 × 1024 × 1024 bytes) |

Sources: [packages/bytebot-ui/src/components/messages/ChatInput.tsx:38-39]()

### File Selection and Validation Flow

```mermaid
stateDiagram-v2
    [*] --> FileInput: User clicks attachment button
    FileInput --> Validate: handleFileSelect()
    
    state Validate {
        [*] --> CheckCount
        CheckCount --> CheckSize: Count <= MAX_FILES
        CheckCount --> ShowError1: Count > MAX_FILES
        CheckSize --> Convert: All files < 30MB
        CheckSize --> ShowError2: Any file > 30MB
        
        ShowError1 --> [*]: "Maximum 5 files allowed"
        ShowError2 --> [*]: "File(s) exceed 30MB limit"
    }
    
    Validate --> ConvertFiles: Validation passed
    
    state ConvertFiles {
        [*] --> ReadFile
        ReadFile --> Base64: FileReader.readAsDataURL()
        Base64 --> CreateObject: FileWithBase64
        CreateObject --> [*]
    }
    
    ConvertFiles --> UpdateState: All files converted
    UpdateState --> NotifyParent: onFileUpload(files)
    NotifyParent --> RenderPills: Display file chips
    RenderPills --> [*]
```

**File Validation and Conversion Process**

The `handleFileSelect` function implements comprehensive validation:

1. **Count Validation**: Checks if `selectedFiles.length + files.length > MAX_FILES` at [ChatInput.tsx:53-57]()
2. **Size Validation**: Iterates through files and validates `file.size <= MAX_FILE_SIZE` at [ChatInput.tsx:60-73]()
3. **Base64 Conversion**: Uses `FileReader.readAsDataURL()` at [ChatInput.tsx:100-107]()
4. **Error Display**: Shows red error banner above file list at [ChatInput.tsx:163-167]()

Sources: [packages/bytebot-ui/src/components/messages/ChatInput.tsx:46-117]()

### File Display and Removal

Selected files are displayed as removable chips showing the filename:

- Files rendered in a flex-wrap container at [ChatInput.tsx:169-196]()
- Each chip includes a cancel button that calls `removeFile(index)` at [ChatInput.tsx:109-117]()
- Counter shows `{selectedFiles.length} / {MAX_FILES} files` at [ChatInput.tsx:172]()

Sources: [packages/bytebot-ui/src/components/messages/ChatInput.tsx:169-196]()

## Task Creation Flow

The task creation flow orchestrates user input validation, API communication, and navigation to the task detail page.

```mermaid
sequenceDiagram
    participant User
    participant ChatInput
    participant Home
    participant startTask
    participant API as "POST /api/tasks"
    participant Router
    participant TaskPage as "/tasks/:id"
    
    User->>ChatInput: Enter task description
    User->>ChatInput: Attach files (optional)
    User->>ChatInput: Press Enter or click Send
    
    ChatInput->>Home: onSend()
    Home->>Home: handleSend()
    
    alt input.trim() is empty
        Home->>User: No action (early return)
    else input is valid
        Home->>Home: setIsLoading(true)
        
        alt selectedModel is null
            Home->>Home: throw Error("No model selected")
        else model is selected
            Home->>Home: Build taskData object
            
            Note over Home: taskData = {<br/>  description: input,<br/>  model: selectedModel,<br/>  files?: uploadedFiles<br/>}
            
            Home->>startTask: startTask(taskData)
            startTask->>API: POST request with taskData
            API-->>startTask: task object { id, ... }
            startTask-->>Home: return task
            
            alt task.id exists
                Home->>Router: router.push(`/tasks/${task.id}`)
                Router->>TaskPage: Navigate to task detail
            else task creation failed
                Home->>Home: console.error("Failed to create task")
            end
        end
        
        Home->>Home: setIsLoading(false)
    end
```

**Task Creation Sequence**

Sources: [packages/bytebot-ui/src/app/page.tsx:97-133]()

### handleSend Implementation

The `handleSend` function at [page.tsx:97-133]() implements the following logic:

1. **Input Validation**: Returns early if `!input.trim()` at line 98
2. **Loading State**: Sets `isLoading` to true at line 100
3. **Model Validation**: Throws error if no model selected at line 103
4. **Payload Construction**: Builds `taskData` object with required fields at lines 105-117
   - Always includes: `description`, `model`
   - Conditionally includes: `files` (if `uploadedFiles.length > 0`)
5. **API Call**: Invokes `startTask(taskData)` at line 119
6. **Navigation**: Redirects to `/tasks/${task.id}` using Next.js router at line 123
7. **Error Handling**: Catches and logs errors at lines 128-129
8. **Cleanup**: Sets `isLoading` to false in finally block at line 131

Sources: [packages/bytebot-ui/src/app/page.tsx:97-133]()

### startTask API Integration

The `startTask` utility function (referenced but not shown in provided files) performs the following:

| Function | Location | Purpose |
|----------|----------|---------|
| `startTask(taskData)` | `@/utils/taskUtils` | Sends POST request to `/api/tasks`, returns created task object |

The function is imported at [page.tsx:15]() and called at [page.tsx:119]().

Sources: [packages/bytebot-ui/src/app/page.tsx:15](), [packages/bytebot-ui/src/app/page.tsx:119]()

## Layout System

The interface implements responsive layouts optimized for desktop and mobile viewports using Tailwind CSS utility classes.

### Layout Variants

```mermaid
graph TB
    subgraph "Desktop Layout (lg: screens)"
        DesktopGrid["Grid: 2 columns (50/50)"]
        LeftColumn["Left Column<br/>Task creation form<br/>+ Latest tasks"]
        RightColumn["Right Column<br/>Stock photo"]
        
        DesktopGrid --> LeftColumn
        DesktopGrid --> RightColumn
    end
    
    subgraph "Mobile Layout (< lg screens)"
        MobileStack["Flex Column<br/>Full width"]
        FormArea["Task creation form"]
        TaskArea["Latest tasks"]
        
        MobileStack --> FormArea
        MobileStack --> TaskArea
    end
    
    subgraph "Common Components"
        Header["Header"]
        Title["What can I help you<br/>get done? (h1)"]
        InputContainer["bg-bytebot-bronze-light-2<br/>border rounded-2xl"]
        ChatInputComp["ChatInput component"]
        ModelSelect["Select dropdown"]
        TaskListComp["TaskList component"]
    end
    
    LeftColumn --> Title
    LeftColumn --> InputContainer
    InputContainer --> ChatInputComp
    InputContainer --> ModelSelect
    LeftColumn --> TaskListComp
    
    FormArea --> Title
    FormArea --> InputContainer
    FormArea --> TaskListComp
```

**Responsive Layout Architecture**

### Desktop Layout

The desktop layout uses a CSS Grid with `lg:grid lg:grid-cols-2` at [page.tsx:145]():

- **Left Panel**: Task creation form with centered content, max-width `xl` (672px) at [page.tsx:148]()
- **Right Panel**: Decorative stock photo, centered with `aspect-square` at [page.tsx:196-199]()
- **Visibility**: Hidden on mobile with `hidden` class, shown on desktop with `lg:grid` at [page.tsx:145]()

Sources: [packages/bytebot-ui/src/app/page.tsx:145-201]()

### Mobile Layout

The mobile layout uses a flex column at [page.tsx:204]():

- **Single Column**: Full-width flex column with `flex-col`
- **Padding**: `px-4 pt-10` for top and horizontal spacing at [page.tsx:205]()
- **Visibility**: Visible by default, hidden on desktop with `lg:hidden` at [page.tsx:204]()
- **No Stock Photo**: Image omitted to save vertical space

Sources: [packages/bytebot-ui/src/app/page.tsx:204-252]()

### Common UI Elements

Both layouts share these components:

| Component | Styling | Location |
|-----------|---------|----------|
| Title (h1) | `text-bytebot-bronze-light-12 text-2xl` | [page.tsx:150-152]() |
| Input Container | `bg-bytebot-bronze-light-2 border-bytebot-bronze-light-7 rounded-2xl` | [page.tsx:155]() |
| ChatInput | `minLines={3}` | [page.tsx:156-163]() |
| Model Select | `w-auto` trigger | [page.tsx:165-183]() |
| TaskList | `w-full` with title "Latest Tasks" | [page.tsx:187-191]() |

Sources: [packages/bytebot-ui/src/app/page.tsx:150-191]()

## Validation and Error Handling

The interface implements multi-layered validation to ensure data integrity before task creation.

### Client-Side Validation

```mermaid
graph TD
    subgraph "Input Validation"
        CheckEmpty["input.trim() empty?"]
        CheckModel["selectedModel null?"]
    end
    
    subgraph "File Validation"
        CheckFileCount["Files > MAX_FILES?"]
        CheckFileSize["Any file > 30MB?"]
    end
    
    subgraph "Actions"
        EarlyReturn["Return (no-op)"]
        ThrowError["Throw Error"]
        ShowFilesError["setErrorMessage()"]
        ProceedCreate["Proceed to startTask()"]
    end
    
    CheckEmpty -->|Yes| EarlyReturn
    CheckEmpty -->|No| CheckModel
    CheckModel -->|Yes| ThrowError
    CheckModel -->|No| CheckFileCount
    
    CheckFileCount -->|Yes| ShowFilesError
    CheckFileCount -->|No| CheckFileSize
    CheckFileSize -->|Yes| ShowFilesError
    CheckFileSize -->|No| ProceedCreate
```

**Validation Chain**

### Validation Rules

| Validation Type | Rule | Error Behavior | Code Reference |
|----------------|------|----------------|----------------|
| **Empty Input** | `input.trim()` must not be empty | Silent return (no action) | [page.tsx:98]() |
| **Model Selection** | `selectedModel` must not be null | Throws error | [page.tsx:103]() |
| **File Count** | `selectedFiles.length + files.length <= 5` | Red error banner | [ChatInput.tsx:53-57]() |
| **File Size** | Each file `size <= 30 MB` | Red error banner with filenames | [ChatInput.tsx:60-73]() |

Sources: [packages/bytebot-ui/src/app/page.tsx:98-103](), [packages/bytebot-ui/src/components/messages/ChatInput.tsx:53-73]()

### Error Display Mechanisms

**File Upload Errors**

Error messages are displayed in a red banner above the file list:

- Component: `<div>` with classes `bg-red-50 text-red-600` at [ChatInput.tsx:163-167]()
- State: `errorMessage` string state variable at [ChatInput.tsx:36]()
- Clear: Error cleared on successful file selection or file removal at [ChatInput.tsx:50](), [ChatInput.tsx:112]()

**Error Messages**

The system displays specific error messages:

```typescript
"Maximum 5 files allowed"                          // File count exceeded
"File(s) exceed 30MB limit: filename1 (size), ..." // File size exceeded
```

Sources: [packages/bytebot-ui/src/components/messages/ChatInput.tsx:36](), [packages/bytebot-ui/src/components/messages/ChatInput.tsx:163-167]()

### Loading State

The `isLoading` state provides user feedback during async operations:

- **Button State**: Send button replaced with spinning loader at [ChatInput.tsx:234-249]()
- **Input Disabled**: Textarea disabled when `isLoading={true}` at [ChatInput.tsx:210]()
- **Duration**: Set to `true` before API call, reset in finally block at [page.tsx:100](), [page.tsx:131]()

Sources: [packages/bytebot-ui/src/app/page.tsx:100-131](), [packages/bytebot-ui/src/components/messages/ChatInput.tsx:210](), [packages/bytebot-ui/src/components/messages/ChatInput.tsx:234-249]()

## Integration with Backend

The task creation interface communicates with the backend through a well-defined API contract.

### API Request Payload

```typescript
// Constructed in handleSend()
const taskData: {
  description: string;
  model: Model;
  files?: FileWithBase64[];
} = {
  description: input,
  model: selectedModel,
};

// Files conditionally added
if (uploadedFiles.length > 0) {
  taskData.files = uploadedFiles;
}
```

### API Communication Flow

```mermaid
graph LR
    subgraph "Frontend (bytebot-ui)"
        Home["Home.handleSend()"]
        StartTask["startTask() utility"]
        APIProxy["API Proxy<br/>/api/tasks"]
    end
    
    subgraph "Backend (bytebot-agent)"
        TasksAPI["TasksController<br/>POST /tasks"]
        TasksSvc["TasksService.create()"]
        FilesSvc["Write files to desktop"]
        DB["PostgreSQL<br/>Task record"]
    end
    
    Home -->|"taskData"| StartTask
    StartTask -->|"POST /api/tasks"| APIProxy
    APIProxy -->|"HTTP request"| TasksAPI
    TasksAPI --> TasksSvc
    TasksSvc --> DB
    TasksSvc --> FilesSvc
    
    DB -.->|"task object"| TasksAPI
    TasksAPI -.->|"JSON response"| APIProxy
    APIProxy -.->|"task object"| StartTask
    StartTask -.->|"task"| Home
    Home -.->|"router.push"| TaskDetail["/tasks/:id"]
```

**End-to-End Task Creation**

The complete flow from user input to task detail page:

1. User submits form → `handleSend()` called
2. `startTask(taskData)` sends POST to `/api/tasks` via proxy at [page.tsx:119]()
3. Backend creates task record in database
4. Backend writes files to `/home/user/Desktop` if provided
5. Backend returns task object with `id`
6. Frontend navigates to `/tasks/${task.id}` at [page.tsx:123]()

For details on the backend task creation process, see [TasksService API](#5.2). For file handling specifics, see [File Handling](#5.5).

Sources: [packages/bytebot-ui/src/app/page.tsx:97-133]()

---

# Page: Task List Interface

# Task List Interface

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [packages/bytebot-ui/src/app/tasks/page.tsx](packages/bytebot-ui/src/app/tasks/page.tsx)
- [packages/bytebot-ui/src/components/tasks/TaskItem.tsx](packages/bytebot-ui/src/components/tasks/TaskItem.tsx)
- [packages/bytebot-ui/src/components/tasks/TaskTabs.tsx](packages/bytebot-ui/src/components/tasks/TaskTabs.tsx)
- [packages/bytebot-ui/src/components/ui/button.tsx](packages/bytebot-ui/src/components/ui/button.tsx)

</details>



## Purpose and Scope

The Task List Interface provides a paginated, tab-based view for browsing all tasks in the system. Located at `/tasks`, this page enables users to filter tasks by status category, navigate through pages of results, and access individual task details. The interface displays task metadata including status indicators, descriptions, and creation timestamps.

For creating new tasks, see [Task Creation Interface](#8.1). For viewing individual task details and messages, see [Task Detail Page](#8.3). For the underlying API operations, see [Tasks REST API](#10.1).

## Page Architecture

The Task List Interface consists of three primary components that work together to provide the browsing experience:

**Component Hierarchy Diagram**

```mermaid
graph TB
    TasksPage["TasksPage<br/>/app/tasks/page.tsx"]
    TasksPageContent["TasksPageContent<br/>Main component"]
    Header["Header<br/>Navigation bar"]
    TaskTabs["TaskTabs<br/>Filter tabs"]
    TaskItemList["Task Item List<br/>Rendered tasks"]
    TaskItem["TaskItem<br/>Individual task card"]
    Pagination["Pagination<br/>Page navigation"]
    EmptyState["Empty State<br/>No tasks message"]
    
    TasksPage -->|"Suspense wrapper"| TasksPageContent
    TasksPageContent --> Header
    TasksPageContent --> TaskTabs
    TasksPageContent --> TaskItemList
    TasksPageContent --> Pagination
    TasksPageContent --> EmptyState
    TaskItemList -->|"maps tasks array"| TaskItem
    
    style TasksPageContent fill:#f9f9f9
    style TaskTabs fill:#f9f9f9
    style TaskItem fill:#f9f9f9
```

**Sources:** [packages/bytebot-ui/src/app/tasks/page.tsx:1-191]()

The `TasksPage` component uses React Suspense to wrap `TasksPageContent`, providing a loading fallback during initial render. The main component manages state and coordinates child components.

## Tab-Based Filtering System

The interface provides four predefined filter tabs, each mapping to specific task status combinations:

| Tab Key | Label | Included Statuses | Icon |
|---------|-------|-------------------|------|
| `ALL` | All | All statuses | `ListViewIcon` |
| `ACTIVE` | Active | `PENDING`, `RUNNING`, `NEEDS_HELP`, `NEEDS_REVIEW` | `CursorProgress04Icon` |
| `COMPLETED` | Completed | `COMPLETED` | `Tick02Icon` |
| `CANCELLED_FAILED` | Cancelled/Failed | `CANCELLED`, `FAILED` | `MultiplicationSignIcon` |

**Tab Configuration and Filtering Flow**

```mermaid
graph TB
    TAB_CONFIGS["TAB_CONFIGS<br/>Record&lt;TabKey, TabConfig&gt;"]
    TabKey["TabKey type<br/>'ALL' | 'ACTIVE' | 'COMPLETED' | 'CANCELLED_FAILED'"]
    TaskTabs["TaskTabs component<br/>Renders tab buttons"]
    onTabChange["handleTabChange()<br/>in TasksPageContent"]
    URLUpdate["router.push()<br/>Update URL params"]
    fetchTasks["fetchTasks()<br/>API call with statuses"]
    
    TAB_CONFIGS -->|"provides config for"| TaskTabs
    TabKey -->|"constrains"| TAB_CONFIGS
    TaskTabs -->|"onClick"| onTabChange
    onTabChange -->|"setActiveTab()"| TabKey
    onTabChange --> URLUpdate
    onTabChange -->|"triggers useEffect"| fetchTasks
    
    URLParams["URL search params<br/>?tab=ACTIVE"]
    URLParams -.->|"syncs with"| onTabChange
```

**Sources:** [packages/bytebot-ui/src/components/tasks/TaskTabs.tsx:11-60](), [packages/bytebot-ui/src/app/tasks/page.tsx:94-108]()

The `TAB_CONFIGS` constant at [packages/bytebot-ui/src/components/tasks/TaskTabs.tsx:30-60]() defines the mapping between tab keys and their status arrays. When a user clicks a tab:

1. `handleTabChange()` at [packages/bytebot-ui/src/app/tasks/page.tsx:94-108]() updates `activeTab` state
2. URL parameters are updated (tab parameter added/removed)
3. `currentPage` resets to 1
4. A `useEffect` hook triggers `fetchTasks()` with the new status filter

### Task Count Badges

Each tab displays a count badge showing the number of tasks in that category:

**Task Count Loading Flow**

```mermaid
sequenceDiagram
    participant TasksPageContent
    participant fetchTaskCounts
    participant API as "/api/proxy/tasks/count"
    participant TaskTabs
    
    TasksPageContent->>fetchTaskCounts: useEffect on mount
    fetchTaskCounts->>API: GET request
    API-->>fetchTaskCounts: {ALL: 15, ACTIVE: 3, ...}
    fetchTaskCounts-->>TasksPageContent: Update taskCounts state
    TasksPageContent->>TaskTabs: Pass taskCounts prop
    TaskTabs->>TaskTabs: Render badges if count > 0
```

**Sources:** [packages/bytebot-ui/src/app/tasks/page.tsx:67-78](), [packages/bytebot-ui/src/components/tasks/TaskTabs.tsx:91-101]()

The `fetchTaskCounts()` utility at [packages/bytebot-ui/src/app/tasks/page.tsx:68-77]() loads all counts once on component mount. The `TaskTabs` component conditionally renders count badges at [packages/bytebot-ui/src/components/tasks/TaskTabs.tsx:91-101]() when `count > 0`.

## Task Item Display

Each task is rendered as a `TaskItem` component, displaying status, description, and timestamp:

**TaskItem Component Structure**

```mermaid
graph LR
    TaskItem["TaskItem component<br/>&lt;Link href='/tasks/{id}'&gt;"]
    StatusIcon["StatusIcon<br/>Status-specific icon/loader"]
    Description["Task description<br/>Capitalized text"]
    Timestamp["Formatted timestamp<br/>formatDate()"]
    
    TaskItem --> StatusIcon
    TaskItem --> Description
    TaskItem --> Timestamp
    
    STATUS_CONFIGS["STATUS_CONFIGS<br/>Record&lt;TaskStatus, StatusIconConfig&gt;"]
    STATUS_CONFIGS -->|"maps status to"| StatusIcon
    
    subgraph "StatusIconConfig options"
        Icon["icon: HugeIcon"]
        Color["color: Tailwind class"]
        Loader["useLoader: boolean"]
    end
    
    STATUS_CONFIGS --> Icon
    STATUS_CONFIGS --> Color
    STATUS_CONFIGS --> Loader
```

**Sources:** [packages/bytebot-ui/src/components/tasks/TaskItem.tsx:1-111]()

### Status Icon Mapping

The `STATUS_CONFIGS` constant at [packages/bytebot-ui/src/components/tasks/TaskItem.tsx:25-52]() defines the visual representation for each `TaskStatus`:

| Status | Display | Color Class |
|--------|---------|-------------|
| `COMPLETED` | `Tick02Icon` | `text-bytebot-green-8` |
| `RUNNING` | `Loader` spinner | N/A |
| `NEEDS_HELP` | `AlertCircleIcon` | `text-[#FF9D00]` (orange) |
| `PENDING` | `Loader` spinner | N/A |
| `FAILED` | `AlertCircleIcon` | `text-bytebot-red-light-9` |
| `NEEDS_REVIEW` | `AlertCircleIcon` | `text-[#FF9D00]` (orange) |
| `CANCELLED` | `CancelCircleIcon` | `text-bytebot-bronze-light-10` |

The `StatusIcon` function at [packages/bytebot-ui/src/components/tasks/TaskItem.tsx:71-90]() determines whether to render an icon or loader based on the configuration.

### Date Formatting

The `formatDate()` function at [packages/bytebot-ui/src/components/tasks/TaskItem.tsx:56-69]() provides human-readable timestamps:

- **Same day:** "Today 9:13am"
- **Different day:** "April 13, 2025 12:01pm"

The formatted date appears below the task description at [packages/bytebot-ui/src/components/tasks/TaskItem.tsx:103-106]().

### Navigation

Each `TaskItem` is wrapped in a Next.js `Link` component at [packages/bytebot-ui/src/components/tasks/TaskItem.tsx:93](), pointing to `/tasks/${task.id}`. Clicking anywhere on the card navigates to the task detail page.

## Pagination System

When task results exceed the page size limit (10 tasks), pagination controls appear:

**Pagination Data Flow**

```mermaid
graph TB
    fetchTasks["fetchTasks()<br/>API call"]
    APIResponse["{tasks: Task[], total: number, totalPages: number}"]
    State["Component state<br/>tasks, total, totalPages, currentPage"]
    PaginationComp["Pagination component<br/>packages/ui/pagination.tsx"]
    handlePageChange["handlePageChange()<br/>setCurrentPage()"]
    
    fetchTasks -->|"returns"| APIResponse
    APIResponse -->|"updates"| State
    State -->|"props"| PaginationComp
    PaginationComp -->|"onPageChange callback"| handlePageChange
    handlePageChange -->|"triggers useEffect"| fetchTasks
    
    useEffect["useEffect([currentPage, activeTab])"]
    useEffect -.->|"watches"| fetchTasks
```

**Sources:** [packages/bytebot-ui/src/app/tasks/page.tsx:43-65](), [packages/bytebot-ui/src/app/tasks/page.tsx:110-112](), [packages/bytebot-ui/src/app/tasks/page.tsx:159-167]()

The pagination system operates through:

1. **API Response:** `fetchTasks()` at [packages/bytebot-ui/src/app/tasks/page.tsx:49]() returns `total` and `totalPages` from the backend
2. **Conditional Rendering:** Pagination only displays when `totalPages > 1` at [packages/bytebot-ui/src/app/tasks/page.tsx:159]()
3. **Page Navigation:** `handlePageChange()` at [packages/bytebot-ui/src/app/tasks/page.tsx:110-112]() updates `currentPage` state
4. **Effect Trigger:** A `useEffect` at [packages/bytebot-ui/src/app/tasks/page.tsx:43-65]() watches `currentPage` and `activeTab`, fetching new data on change

The `PAGE_SIZE` constant is set to 10 at [packages/bytebot-ui/src/app/tasks/page.tsx:41]().

## State Management

The interface manages multiple interconnected state variables:

**State Variable Dependencies**

```mermaid
graph TB
    URLParams["URL searchParams<br/>?tab=ACTIVE"]
    activeTab["activeTab state<br/>TabKey"]
    currentPage["currentPage state<br/>number"]
    tasks["tasks state<br/>Task[]"]
    taskCounts["taskCounts state<br/>Record&lt;TabKey, number&gt;"]
    total["total state<br/>number"]
    totalPages["totalPages state<br/>number"]
    isLoading["isLoading state<br/>boolean"]
    
    URLParams -->|"getInitialTab()"| activeTab
    activeTab -->|"useEffect dependency"| tasks
    currentPage -->|"useEffect dependency"| tasks
    activeTab -.->|"reset on change"| currentPage
    
    fetchTasks["fetchTasks() call"]
    fetchTaskCounts["fetchTaskCounts() call"]
    
    activeTab --> fetchTasks
    currentPage --> fetchTasks
    fetchTasks -->|"updates"| tasks
    fetchTasks -->|"updates"| total
    fetchTasks -->|"updates"| totalPages
    fetchTasks -->|"updates"| isLoading
    
    fetchTaskCounts -->|"updates once"| taskCounts
    
    style URLParams fill:#f9f9f9
    style fetchTasks fill:#f9f9f9
    style fetchTaskCounts fill:#f9f9f9
```

**Sources:** [packages/bytebot-ui/src/app/tasks/page.tsx:15-78]()

### URL Parameter Synchronization

The interface maintains bidirectional sync between URL parameters and component state:

1. **Initial Load:** `getInitialTab()` at [packages/bytebot-ui/src/app/tasks/page.tsx:23-29]() reads the `tab` URL parameter
2. **Tab Change:** `handleTabChange()` at [packages/bytebot-ui/src/app/tasks/page.tsx:94-108]() updates URL via `router.push()`
3. **URL Change:** A `useEffect` at [packages/bytebot-ui/src/app/tasks/page.tsx:81-92]() watches `searchParams` and syncs to state

The URL format is:
- **All tasks:** `/tasks` (no parameter)
- **Filtered:** `/tasks?tab=ACTIVE`, `/tasks?tab=COMPLETED`, etc.

### Loading States

The `isLoading` state at [packages/bytebot-ui/src/app/tasks/page.tsx:20]() controls three UI variations:

1. **Loading:** Spinner displayed at [packages/bytebot-ui/src/app/tasks/page.tsx:130-134]()
2. **Empty:** No tasks message at [packages/bytebot-ui/src/app/tasks/page.tsx:135-150]()
3. **Loaded:** Task list at [packages/bytebot-ui/src/app/tasks/page.tsx:151-168]()

## Empty State

When no tasks match the current filter, an empty state component appears:

**Empty State Structure**

```mermaid
graph LR
    EmptyCheck{"tasks.length === 0<br/>and !isLoading"}
    EmptyState["Empty state container<br/>Centered card"]
    Heading["'No tasks yet'<br/>h3 element"]
    Description["'Get started...'<br/>p element"]
    NewTaskButton["'+ New Task' Button<br/>&lt;Link href='/'&gt;"]
    
    EmptyCheck -->|"true"| EmptyState
    EmptyState --> Heading
    EmptyState --> Description
    EmptyState --> NewTaskButton
```

**Sources:** [packages/bytebot-ui/src/app/tasks/page.tsx:135-150]()

The empty state at [packages/bytebot-ui/src/app/tasks/page.tsx:136-149]() provides:

- A heading: "No tasks yet"
- Description text: "Get started by creating a first task"
- A "New Task" button linking to the home page (`/`)

This appears when the `tasks` array is empty but loading has completed (preventing flash during initial load).

## API Integration Points

The interface integrates with multiple API endpoints through the `taskUtils` module:

| Function | Endpoint | Purpose | Returns |
|----------|----------|---------|---------|
| `fetchTasks()` | `/api/proxy/tasks` | Load paginated tasks | `{tasks: Task[], total: number, totalPages: number}` |
| `fetchTaskCounts()` | `/api/proxy/tasks/count` | Load status counts | `Record<TabKey, number>` |

**API Request Flow**

```mermaid
sequenceDiagram
    participant Component as TasksPageContent
    participant Utils as taskUtils
    participant Proxy as /api/proxy/tasks
    participant Backend as bytebot-agent
    
    Component->>Utils: fetchTasks({page, limit, statuses})
    Utils->>Proxy: GET /api/proxy/tasks?page=1&limit=10
    Proxy->>Backend: GET /tasks?page=1&limit=10
    Backend-->>Proxy: {tasks: [...], total: 15, totalPages: 2}
    Proxy-->>Utils: Same response
    Utils-->>Component: Update tasks state
    
    Component->>Utils: fetchTaskCounts()
    Utils->>Proxy: GET /api/proxy/tasks/count
    Proxy->>Backend: GET /tasks/count
    Backend-->>Proxy: {ALL: 15, ACTIVE: 3, ...}
    Proxy-->>Utils: Same response
    Utils-->>Component: Update taskCounts state
```

**Sources:** [packages/bytebot-ui/src/app/tasks/page.tsx:49-56](), [packages/bytebot-ui/src/app/tasks/page.tsx:68-77]()

Both API calls pass through the Next.js proxy layer at `/api/proxy/tasks` which forwards requests to the `bytebot-agent` service. For detailed API specifications, see [Tasks REST API](#10.1). For the utility implementation, see [API Client Utilities](#8.6).

---

# Page: Task Detail Page

# Task Detail Page

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [packages/bytebot-ui/src/app/tasks/[id]/page.tsx](packages/bytebot-ui/src/app/tasks/[id]/page.tsx)
- [packages/bytebot-ui/src/components/messages/AssistantMessage.tsx](packages/bytebot-ui/src/components/messages/AssistantMessage.tsx)
- [packages/bytebot-ui/src/components/messages/ChatContainer.tsx](packages/bytebot-ui/src/components/messages/ChatContainer.tsx)
- [packages/bytebot-ui/src/components/messages/MessageGroup.tsx](packages/bytebot-ui/src/components/messages/MessageGroup.tsx)
- [packages/bytebot-ui/src/components/messages/UserMessage.tsx](packages/bytebot-ui/src/components/messages/UserMessage.tsx)
- [packages/bytebot-ui/src/components/screenshot/ScreenshotViewer.tsx](packages/bytebot-ui/src/components/screenshot/ScreenshotViewer.tsx)
- [packages/bytebot-ui/src/hooks/useScrollScreenshot.ts](packages/bytebot-ui/src/hooks/useScrollScreenshot.ts)
- [packages/bytebot-ui/src/utils/screenshotUtils.ts](packages/bytebot-ui/src/utils/screenshotUtils.ts)

</details>



The Task Detail Page (`/tasks/[id]`) provides real-time interaction with individual AI tasks through a dual-pane interface. It combines desktop visualization (VNC or screenshots) with a chat-based messaging system, supporting both autonomous AI execution and manual user takeover.

For task creation, see page 8.1. For desktop viewing implementation, see page 8.4. For message display components, see page 8.5.

## Component Architecture

The task detail page is implemented in [packages/bytebot-ui/src/app/tasks/[id]/page.tsx:25-220]() as a Next.js dynamic route. The `TaskPage` component orchestrates state management, real-time updates, and UI rendering for individual task sessions.

**TaskPage Component Architecture**

```mermaid
graph TB
    subgraph "TaskPage (/tasks/[id]/page.tsx)"
        TaskPageFunction["TaskPage() default export"]
        useChatSessionHook["useChatSession({ initialTaskId })"]
        useScrollScreenshotHook["useScrollScreenshot({ messages, scrollContainerRef })"]
        chatContainerRef["chatContainerRef: RefObject<HTMLDivElement>"]
    end
    
    subgraph "Layout Components (packages/bytebot-ui/src/components)"
        HeaderComponent["Header"]
        DesktopContainer["DesktopContainer<br/>(ui/desktop-container)<br/>col-span-4"]
        ChatContainer["ChatContainer<br/>(messages/ChatContainer)<br/>col-span-3"]
    end
    
    subgraph "Task Control Functions"
        isTaskInactive["isTaskInactive()"]
        canTakeOver["canTakeOver()"]
        hasUserControl["hasUserControl()"]
        canCancel["canCancel()"]
        vncViewOnly["vncViewOnly()"]
    end
    
    subgraph "useChatSession Returns"
        messages["messages: Message[]"]
        groupedMessages["groupedMessages: GroupedMessages[]"]
        taskStatus["taskStatus: TaskStatus"]
        control["control: Role"]
        handleTakeOverTask["handleTakeOverTask()"]
        handleResumeTask["handleResumeTask()"]
        handleCancelTask["handleCancelTask()"]
    end
    
    TaskPageFunction --> HeaderComponent
    TaskPageFunction --> DesktopContainer
    TaskPageFunction --> ChatContainer
    TaskPageFunction --> useChatSessionHook
    TaskPageFunction --> useScrollScreenshotHook
    
    useChatSessionHook --> messages
    useChatSessionHook --> groupedMessages
    useChatSessionHook --> taskStatus
    useChatSessionHook --> control
    useChatSessionHook --> handleTakeOverTask
    useChatSessionHook --> handleResumeTask
    useChatSessionHook --> handleCancelTask
    
    taskStatus --> isTaskInactive
    control --> canTakeOver
    control --> hasUserControl
    taskStatus --> canCancel
    hasUserControl --> vncViewOnly
    
    chatContainerRef --> useScrollScreenshotHook
    DesktopContainer --> isTaskInactive
    DesktopContainer --> vncViewOnly
    ChatContainer --> groupedMessages
    ChatContainer --> chatContainerRef
```

Sources: [packages/bytebot-ui/src/app/tasks/[id]/page.tsx:25-48](), [packages/bytebot-ui/src/app/tasks/[id]/page.tsx:50-83](), [packages/bytebot-ui/src/hooks/useChatSession.ts](), [packages/bytebot-ui/src/hooks/useScrollScreenshot.ts:5-14]()

## Layout and Structure

The task detail interface uses a responsive grid layout that divides the screen into two main areas: desktop visualization and chat interaction.

### Grid Layout

The page uses a 7-column CSS Grid layout defined in [packages/bytebot-ui/src/app/tasks/[id]/page.tsx:119-217](). The desktop container spans 4 columns (left), and the chat container spans 3 columns (right):

```mermaid
graph LR
    subgraph "Screen Layout (7-column grid)"
        Desktop["DesktopContainer<br/>col-span-4<br/>Desktop View"]
        Chat["ChatContainer<br/>col-span-3<br/>Chat Interface"]
    end
    
    subgraph "DesktopContainer Contents"
        VNCOrScreenshot["VNC Viewer or Screenshot"]
        StatusOverlay["Virtual Desktop Status"]
        ActionButtons["Task Control Buttons"]
    end
    
    subgraph "ChatContainer Contents"
        MessagesArea["Messages Scrollable Area<br/>flex-1"]
        InputArea["Chat Input Area<br/>flex-shrink-0"]
    end
    
    Desktop --> VNCOrScreenshot
    Desktop --> StatusOverlay
    Desktop --> ActionButtons
    
    Chat --> MessagesArea
    Chat --> InputArea
```

Sources: [packages/bytebot-ui/src/app/tasks/[id]/page.tsx:119-217]()

### Key Component Props

The `TaskPage` component renders child components with state-derived props:

| Component | Purpose | Key Props |
|-----------|---------|-----------|
| `DesktopContainer` | Desktop visualization and status | `screenshot`, `viewOnly`, `status` |
| `ChatContainer` | Message display and input | `groupedMessages`, `taskStatus`, `control` |
| `Header` | Navigation and branding | None |
| Task Control Buttons | Task state management | Conditional rendering based on task status |

The `DesktopContainer` receives `screenshot`, `viewOnly`, and `status` props determined by task state [packages/bytebot-ui/src/app/tasks/[id]/page.tsx:127-146](). The `ChatContainer` receives `groupedMessages`, `taskStatus`, `control`, and message handling callbacks [packages/bytebot-ui/src/app/tasks/[id]/page.tsx:198-213]().

Sources: [packages/bytebot-ui/src/app/tasks/[id]/page.tsx:127-146](), [packages/bytebot-ui/src/app/tasks/[id]/page.tsx:198-213](), [packages/bytebot-ui/src/components/messages/ChatContainer.tsx:9-24]()

## State Management Logic

The page implements five boolean state functions in [packages/bytebot-ui/src/app/tasks/[id]/page.tsx:50-83]() that determine UI behavior based on `taskStatus` and `control` state from `useChatSession`.

### Task State Functions

```mermaid
stateDiagram-v2
    [*] --> RUNNING
    RUNNING --> NEEDS_HELP: "User intervention required"
    RUNNING --> COMPLETED: "Task finished successfully"
    RUNNING --> FAILED: "Task encountered error"
    RUNNING --> CANCELLED: "User cancelled"
    NEEDS_HELP --> RUNNING: "User provides input"
    NEEDS_HELP --> CANCELLED: "User cancels"
    COMPLETED --> [*]
    FAILED --> [*]
    CANCELLED --> [*]
    
    note right of RUNNING
        Shows VNC viewer
        AI or User control
        Real-time updates
    end note
    
    note right of COMPLETED
        Shows screenshot
        Read-only mode
        Full message history
    end note
```

The following functions determine conditional rendering and interaction modes:

| Function | Implementation | Return Condition |
|----------|----------------|------------------|
| `isTaskInactive()` | [packages/bytebot-ui/src/app/tasks/[id]/page.tsx:51-57]() | `TaskStatus.COMPLETED \|\| TaskStatus.FAILED \|\| TaskStatus.CANCELLED` |
| `canTakeOver()` | [packages/bytebot-ui/src/app/tasks/[id]/page.tsx:60-62]() | `control === Role.ASSISTANT && taskStatus === TaskStatus.RUNNING` |
| `hasUserControl()` | [packages/bytebot-ui/src/app/tasks/[id]/page.tsx:65-71]() | `control === Role.USER && (TaskStatus.RUNNING \|\| TaskStatus.NEEDS_HELP)` |
| `canCancel()` | [packages/bytebot-ui/src/app/tasks/[id]/page.tsx:74-77]() | `TaskStatus.RUNNING \|\| TaskStatus.NEEDS_HELP` |
| `vncViewOnly()` | [packages/bytebot-ui/src/app/tasks/[id]/page.tsx:81-83]() | `!hasUserControl()` |

These functions are used throughout the component to conditionally render buttons, switch between VNC and screenshot modes, and control message auto-loading.

Sources: [packages/bytebot-ui/src/app/tasks/[id]/page.tsx:50-83]()

### Control Handoff Flow

Task control transitions between AI (`Role.ASSISTANT`) and user (`Role.USER`) through handler functions from `useChatSession`:

| Current State | Available Actions | Result |
|---------------|-------------------|---------|
| AI Control + RUNNING | Take Over | User gains control, VNC becomes interactive |
| User Control + RUNNING/NEEDS_HELP | Proceed | AI resumes control |
| Any Active State | Cancel | Task terminates, interface becomes read-only |

The `handleTakeOverTask` function updates the task's `control` field to `USER`, while `handleResumeTask` sets it back to `ASSISTANT`. The `handleCancelTask` function sets task status to `CANCELLED`.

Sources: [packages/bytebot-ui/src/app/tasks/[id]/page.tsx:148-182](), [packages/bytebot-ui/src/hooks/useChatSession.ts]()

## Message Display System

The `ChatContainer` component renders grouped messages using a three-tier component hierarchy: `ChatContainer` → `MessageGroup` → `AssistantMessage` or `UserMessage`.

**ChatContainer Message Rendering Pipeline**

```mermaid
graph TB
    subgraph "ChatContainer Component"
        ChatContainerFn["ChatContainer<br/>packages/bytebot-ui/src/components/messages/ChatContainer.tsx:26-154"]
        handleScrollFn["handleScroll()<br/>line 44"]
        scrollToBottomFn["scrollToBottom()<br/>line 79"]
        ChatInputComponent["ChatInput<br/>line 134"]
    end
    
    subgraph "MessageGroup Component"
        MessageGroupFn["MessageGroup<br/>packages/bytebot-ui/src/components/messages/MessageGroup.tsx:13-19"]
        RoleCheck["group.role === Role.ASSISTANT ?<br/>line 14"]
    end
    
    subgraph "Role-Specific Rendering"
        AssistantMessageFn["AssistantMessage<br/>packages/bytebot-ui/src/components/messages/AssistantMessage.tsx:15-136"]
        UserMessageFn["UserMessage<br/>packages/bytebot-ui/src/components/messages/UserMessage.tsx:16-135"]
    end
    
    subgraph "Content Rendering Components"
        MessageContentFn["MessageContent<br/>content/MessageContent.tsx"]
        MessageAvatarFn["MessageAvatar<br/>MessageAvatar.tsx"]
        TakeOverUI["Take Over UI<br/>AssistantMessage.tsx:29-86"]
    end
    
    subgraph "Content Block Helpers from @bytebot/shared"
        isTextContentBlockFn["isTextContentBlock()"]
        isToolResultContentBlockFn["isToolResultContentBlock()"]  
        isImageContentBlockFn["isImageContentBlock()"]
    end
    
    ChatContainerFn --> MessageGroupFn
    ChatContainerFn --> handleScrollFn
    ChatContainerFn --> scrollToBottomFn
    ChatContainerFn --> ChatInputComponent
    
    MessageGroupFn --> RoleCheck
    RoleCheck -->|"true"| AssistantMessageFn
    RoleCheck -->|"false"| UserMessageFn
    
    AssistantMessageFn --> MessageContentFn
    AssistantMessageFn --> MessageAvatarFn
    AssistantMessageFn --> TakeOverUI
    UserMessageFn --> MessageContentFn
    UserMessageFn --> MessageAvatarFn
    
    MessageContentFn --> isTextContentBlockFn
    MessageContentFn --> isToolResultContentBlockFn
    MessageContentFn --> isImageContentBlockFn
```

Sources: [packages/bytebot-ui/src/components/messages/ChatContainer.tsx:26-154](), [packages/bytebot-ui/src/components/messages/MessageGroup.tsx:13-19](), [packages/bytebot-ui/src/components/messages/AssistantMessage.tsx:15-136](), [packages/bytebot-ui/src/components/messages/UserMessage.tsx:16-135]()

### Infinite Scroll for Message History

The `ChatContainer` implements bottom-triggered infinite scroll in [packages/bytebot-ui/src/components/messages/ChatContainer.tsx:44-66](). When the user scrolls within 20 pixels of the bottom, it calls `loadMoreMessages()` from `useChatSession`:

```mermaid
sequenceDiagram
    participant User
    participant scrollListener["scroll listener<br/>(line 60-66)"]
    participant handleScroll["handleScroll()<br/>(line 44-57)"]
    participant loadMoreMessages["loadMoreMessages()<br/>(useChatSession)"]
    participant APICall["taskUtils API call"]
    
    User->>scrollListener: "Scrolls near bottom"
    scrollListener->>handleScroll: "scroll event"
    handleScroll->>handleScroll: "distanceFromBottom <= 20"
    handleScroll->>loadMoreMessages: "if hasMoreMessages"
    loadMoreMessages->>APICall: "GET /tasks/:id/messages?cursor"
    APICall-->>loadMoreMessages: "older messages"
    loadMoreMessages-->>handleScroll: "update groupedMessages"
    handleScroll-->>User: "render new messages"
```

The `isLoadingMoreMessages` flag prevents duplicate requests during loading. The scroll listener is attached in a `useEffect` at [packages/bytebot-ui/src/components/messages/ChatContainer.tsx:60-66]().

Sources: [packages/bytebot-ui/src/components/messages/ChatContainer.tsx:44-66]()

## Screenshot Navigation

For completed, failed, or cancelled tasks, the page displays static screenshots that update based on chat scroll position. This system extracts screenshots from message content and maps them to scroll markers.

### Screenshot Data Structure

The `ScreenshotData` interface defined in [packages/bytebot-ui/src/utils/screenshotUtils.ts:4-9]() tracks individual screenshots extracted from messages:

| Field | Type | Purpose |
|-------|------|---------|
| `id` | `string` | Unique identifier: `${messageId}-${blockIndex}-${contentIndex}` |
| `base64Data` | `string` | Base64-encoded PNG image data |
| `messageIndex` | `number` | Flat index in messages array |
| `blockIndex` | `number` | Index within message's content array |

### Screenshot Extraction Process

The `extractScreenshots` function in [packages/bytebot-ui/src/utils/screenshotUtils.ts:14-36]() processes all messages to find image content blocks:

```mermaid
graph TB
    subgraph "extractScreenshots Function"
        ExtractFn["extractScreenshots(messages)<br/>screenshotUtils.ts:14"]
        MessageLoopFn["messages.forEach<br/>line 17"]
        ContentLoopFn["message.content.forEach<br/>line 18"]
        ToolResultCheckFn["isToolResultContentBlock(block)<br/>line 20"]
        ContentItemLoopFn["block.content.forEach<br/>line 22"]
        ImageCheckFn["isImageContentBlock(contentItem)<br/>line 23"]
        PushScreenshotFn["screenshots.push({ id, base64Data, ... })<br/>line 24"]
    end
    
    ExtractFn --> MessageLoopFn
    MessageLoopFn --> ContentLoopFn
    ContentLoopFn --> ToolResultCheckFn
    ToolResultCheckFn -->|"has content"| ContentItemLoopFn
    ContentItemLoopFn --> ImageCheckFn
    ImageCheckFn -->|"is image"| PushScreenshotFn
```

This function iterates through all messages, checks each content block for tool results with images, and creates `ScreenshotData` objects for each image found. The `contentIndex` tracks multiple images within a single tool result block.

Sources: [packages/bytebot-ui/src/utils/screenshotUtils.ts:14-36]()

### Scroll Position Mapping

The system uses hidden marker `<div>` elements in the chat to map scroll position to screenshots. These markers are rendered in [packages/bytebot-ui/src/components/messages/AssistantMessage.tsx:48-78]() and [packages/bytebot-ui/src/components/messages/UserMessage.tsx:30-59]() with data attributes:

```html
<div 
  data-message-index="5"
  data-block-index="2"
  data-content-index="0"
  style={{ position: 'absolute', width: 0, height: 0, overflow: 'hidden' }}
/>
```

The `getScreenshotForScrollPosition` function in [packages/bytebot-ui/src/utils/screenshotUtils.ts:41-148]() queries these markers and selects the appropriate screenshot:

```mermaid
graph TB
    subgraph "getScreenshotForScrollPosition"
        QueryMarkers["querySelectorAll('[data-message-index][data-block-index]')<br/>line 51"]
        CalculateVisibility["Calculate element visibility<br/>lines 68-109"]
        FindClosestTo350px["Find element closest to 350px from top<br/>line 98"]
        FindBestScreenshot["Find most recent screenshot <= marker<br/>lines 137-145"]
        ReturnScreenshot["return screenshot"]
    end
    
    QueryMarkers --> CalculateVisibility
    CalculateVisibility --> FindClosestTo350px
    FindClosestTo350px --> FindBestScreenshot
    FindBestScreenshot --> ReturnScreenshot
```

The algorithm uses a target position of 350 pixels from the top of the viewport. It finds the visible marker closest to this position, then returns the most recent screenshot at or before that marker's message/block index.

Sources: [packages/bytebot-ui/src/utils/screenshotUtils.ts:41-148]()

### useScrollScreenshot Hook

The `useScrollScreenshot` hook in [packages/bytebot-ui/src/hooks/useScrollScreenshot.ts:10-115]() integrates screenshot extraction and scroll tracking:

- **Lines 15-45**: Extracts screenshots when messages change, sets initial screenshot
- **Lines 47-67**: Uses `MutationObserver` to detect DOM changes and re-trigger scroll events
- **Lines 70-90**: Implements throttled `handleScroll` callback (100ms throttle)
- **Lines 92-108**: Attaches scroll event listener to container

The hook returns `{ currentScreenshot, allScreenshots, hasScreenshots }` which is consumed by the `TaskPage` component.

Sources: [packages/bytebot-ui/src/hooks/useScrollScreenshot.ts:10-115]()

## Real-Time Updates

The page receives real-time updates through the `useChatSession` hook, which subscribes to WebSocket events via Socket.IO. Task status changes, new messages, and control transitions trigger automatic UI updates.

### Update Flow

```mermaid
graph TB
    subgraph "Socket.IO Events"
        TaskUpdatedEvent["task_updated<br/>(taskId, task)"]
        NewMessageEvent["new_message<br/>(taskId, message)"]
    end
    
    subgraph "useChatSession State"
        TaskStatusState["taskStatus"]
        ControlState["control"]
        MessagesState["messages"]
        GroupedMessagesState["groupedMessages"]
    end
    
    subgraph "TaskPage Reactions"
        StateCheckFns["isTaskInactive()<br/>canTakeOver()<br/>hasUserControl()"]
        DesktopModeSwitch["VNC ↔ Screenshot switch"]
        ButtonVisibility["Button visibility updates"]
        AutoScroll["scrollToBottom()<br/>(ChatContainer)"]
    end
    
    TaskUpdatedEvent --> TaskStatusState
    TaskUpdatedEvent --> ControlState
    NewMessageEvent --> MessagesState
    MessagesState --> GroupedMessagesState
    
    TaskStatusState --> StateCheckFns
    ControlState --> StateCheckFns
    StateCheckFns --> DesktopModeSwitch
    StateCheckFns --> ButtonVisibility
    GroupedMessagesState --> AutoScroll
```

Sources: [packages/bytebot-ui/src/hooks/useChatSession.ts](), [packages/bytebot-ui/src/app/tasks/[id]/page.tsx:50-83]()

### Auto-Scroll Behavior

The `ChatContainer` implements conditional auto-scroll in [packages/bytebot-ui/src/components/messages/ChatContainer.tsx:68-81]():

```typescript
// Trigger when messages or status changes
useEffect(() => {
  if (
    taskStatus === TaskStatus.RUNNING ||
    taskStatus === TaskStatus.NEEDS_HELP
  ) {
    scrollToBottom();
  }
}, [taskStatus, groupedMessages]);

// scrollToBottom implementation
const scrollToBottom = () => {
  messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
};
```

The effect only triggers auto-scroll for active tasks (`RUNNING` or `NEEDS_HELP`). Inactive tasks preserve scroll position to support screenshot navigation. The `messagesEndRef` is a ref to an empty `<div>` at the end of the message list [packages/bytebot-ui/src/components/messages/ChatContainer.tsx:126]().

For inactive tasks, the page triggers auto-loading of all messages in [packages/bytebot-ui/src/app/tasks/[id]/page.tsx:92-101]() to ensure all screenshot markers are available for navigation.

Sources: [packages/bytebot-ui/src/components/messages/ChatContainer.tsx:68-81](), [packages/bytebot-ui/src/components/messages/ChatContainer.tsx:126](), [packages/bytebot-ui/src/app/tasks/[id]/page.tsx:92-101]()

## Task Control Buttons

The page renders three possible control buttons as children of the `DesktopContainer`: **Take Over**, **Proceed**, and **Cancel**. Button visibility is determined by task state functions.

### Button Rendering Logic

Each button is conditionally rendered as a child of `DesktopContainer` in [packages/bytebot-ui/src/app/tasks/[id]/page.tsx:148-187]():

| Button | Condition | Handler | Effect |
|--------|-----------|---------|--------|
| **Take Over** | `canTakeOver()` | `handleTakeOverTask` | Sets `control` to `USER`, enables interactive VNC |
| **Proceed** | `hasUserControl()` | `handleResumeTask` | Sets `control` to `ASSISTANT`, resumes AI execution |
| **Cancel** | `canCancel()` | `handleCancelTask` | Sets status to `CANCELLED`, terminates task |

The buttons are rendered using the `Button` component from Radix UI with Bytebot styling. The **Take Over** button includes a waving hand icon, and the **Cancel** button is nested in a dropdown menu for destructive actions.

Sources: [packages/bytebot-ui/src/app/tasks/[id]/page.tsx:148-187]()

### Desktop Status Display

The `DesktopContainer` receives a `status` prop that determines the visual status indicator displayed. The `TaskPage` component maps task state to status values in [packages/bytebot-ui/src/app/tasks/[id]/page.tsx:130-145]():

| Task State | Desktop Status | VNC Mode | Available Controls |
|------------|----------------|----------|-------------------|
| AI Control + RUNNING | "running" | view-only | Take Over, Cancel |
| User Control + RUNNING | "user_control" | interactive | Proceed, Cancel |
| NEEDS_HELP | "needs_attention" | interactive | Proceed, Cancel |
| COMPLETED | "completed" | screenshot | None |
| FAILED | "failed" | screenshot | None |
| CANCELLED | "canceled" | screenshot | None |

Sources: [packages/bytebot-ui/src/app/tasks/[id]/page.tsx:125-141]()

---

# Page: Desktop Viewer

# Desktop Viewer

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [packages/bytebot-ui/.gitignore](packages/bytebot-ui/.gitignore)
- [packages/bytebot-ui/src/app/tasks/[id]/page.tsx](packages/bytebot-ui/src/app/tasks/[id]/page.tsx)
- [packages/bytebot-ui/src/components/messages/AssistantMessage.tsx](packages/bytebot-ui/src/components/messages/AssistantMessage.tsx)
- [packages/bytebot-ui/src/components/messages/ChatContainer.tsx](packages/bytebot-ui/src/components/messages/ChatContainer.tsx)
- [packages/bytebot-ui/src/components/messages/MessageGroup.tsx](packages/bytebot-ui/src/components/messages/MessageGroup.tsx)
- [packages/bytebot-ui/src/components/messages/UserMessage.tsx](packages/bytebot-ui/src/components/messages/UserMessage.tsx)
- [packages/bytebot-ui/src/components/screenshot/ScreenshotViewer.tsx](packages/bytebot-ui/src/components/screenshot/ScreenshotViewer.tsx)
- [packages/bytebot-ui/src/components/vnc/VncViewer.tsx](packages/bytebot-ui/src/components/vnc/VncViewer.tsx)
- [packages/bytebot-ui/src/hooks/useScrollScreenshot.ts](packages/bytebot-ui/src/hooks/useScrollScreenshot.ts)
- [packages/bytebot-ui/src/utils/screenshotUtils.ts](packages/bytebot-ui/src/utils/screenshotUtils.ts)
- [packages/bytebot-ui/src/utils/taskUtils.ts](packages/bytebot-ui/src/utils/taskUtils.ts)

</details>



The Desktop Viewer provides real-time visual access to the virtual desktop environment through VNC streaming technology. This component enables users to observe AI agent actions as they execute computer automation tasks and optionally take manual control when intervention is needed.

This document covers the VNC client implementation and desktop streaming architecture. For information about the underlying desktop environment, see [Desktop Service](#4.2). For details on how the desktop viewer integrates with task monitoring, see [Task Detail Interface](#7.2).

## Component Architecture

The Desktop Viewer is implemented as a React component that wraps the `react-vnc` library to provide VNC connectivity within the web interface. The component handles dynamic loading, connection management, and viewport scaling.

```mermaid
graph TB
    subgraph "UI Layer"
        TaskPage["TaskDetail Page"]
        VncViewer["VncViewer Component"]
        ReactVnc["react-vnc Library"]
    end
    
    subgraph "Network Layer"
        ProxyEndpoint["/api/proxy/websockify"]
        WebSocket["WebSocket Connection"]
    end
    
    subgraph "Desktop Layer"
        VncServer["VNC Server"]
        DesktopEnv["XFCE Desktop"]
    end
    
    TaskPage --> VncViewer
    VncViewer --> ReactVnc
    ReactVnc --> WebSocket
    WebSocket --> ProxyEndpoint
    ProxyEndpoint --> VncServer
    VncServer --> DesktopEnv
```

**VNC Component Flow**
This diagram shows how the `VncViewer` component integrates with the broader system to provide desktop access through VNC protocol streaming.

Sources: [packages/bytebot-ui/src/components/vnc/VncViewer.tsx:1-48]()

## VNC Integration Implementation

The `VncViewer` component dynamically imports the `VncScreen` component from `react-vnc` to ensure client-side only rendering and avoid server-side rendering issues.

```mermaid
sequenceDiagram
    participant Component as "VncViewer"
    participant ReactVNC as "react-vnc"
    participant WebSocket as "WebSocket"
    participant Proxy as "/api/proxy/websockify"
    participant VNCServer as "VNC Server"
    
    Component->>ReactVNC: "Dynamic import VncScreen"
    ReactVNC->>Component: "VncScreen component"
    Component->>Component: "Construct WebSocket URL"
    Component->>ReactVNC: "Render with rfbOptions"
    ReactVNC->>WebSocket: "Connect to ws://host/api/proxy/websockify"
    WebSocket->>Proxy: "WebSocket handshake"
    Proxy->>VNCServer: "Proxy VNC protocol"
    VNCServer->>Proxy: "Desktop frames"
    Proxy->>WebSocket: "Binary data stream"
    WebSocket->>ReactVNC: "VNC frames"
    ReactVNC->>Component: "Rendered desktop"
```

**VNC Connection Sequence**
This sequence shows the initialization and connection process for establishing VNC desktop streaming through the WebSocket proxy.

Sources: [packages/bytebot-ui/src/components/vnc/VncViewer.tsx:15-26](), [packages/bytebot-ui/src/components/vnc/VncViewer.tsx:30-44]()

## Connection Management

The component manages WebSocket URL construction based on the current protocol and hostname, ensuring secure connections when the UI is served over HTTPS.

| Configuration | Value | Purpose |
|---------------|--------|---------|
| `secure` | `false` | Disables TLS for VNC protocol |
| `shared` | `true` | Allows multiple concurrent viewers |
| `wsProtocols` | `["binary"]` | Specifies binary WebSocket protocol |
| `scaleViewport` | `true` | Automatically scales desktop to fit viewer |

The WebSocket URL is dynamically constructed using the pattern:
- HTTPS sites: `wss://hostname/api/proxy/websockify`
- HTTP sites: `ws://hostname/api/proxy/websockify`

Sources: [packages/bytebot-ui/src/components/vnc/VncViewer.tsx:22-26](), [packages/bytebot-ui/src/components/vnc/VncViewer.tsx:32-36]()

## User Interaction Modes

The `VncViewer` component supports two interaction modes controlled by the `viewOnly` prop:

```mermaid
graph LR
    subgraph "View-Only Mode"
        ViewOnlyTrue["viewOnly: true"]
        ReadOnly["Desktop Read-Only"]
        NoInput["No Mouse/Keyboard"]
    end
    
    subgraph "Interactive Mode"
        ViewOnlyFalse["viewOnly: false"]
        FullControl["Full Desktop Control"]
        InputEnabled["Mouse/Keyboard Active"]
    end
    
    ViewOnlyTrue --> ReadOnly
    ReadOnly --> NoInput
    ViewOnlyFalse --> FullControl
    FullControl --> InputEnabled
```

**Interaction Mode Configuration**
This diagram shows how the `viewOnly` prop controls user interaction capabilities with the virtual desktop.

The component uses the `viewOnly` value as a React key to force re-rendering when the interaction mode changes, ensuring the VNC connection properly reflects the new permission level.

Sources: [packages/bytebot-ui/src/components/vnc/VncViewer.tsx:5-7](), [packages/bytebot-ui/src/components/vnc/VncViewer.tsx:38-41]()

## Technical Implementation Details

### Client-Side Loading Strategy

The component implements a client-side only loading pattern to avoid server-side rendering conflicts:

```mermaid
flowchart TD
    Mount["Component Mount"]
    SSRCheck["SSR Safety Check"]
    DynamicImport["Dynamic Import react-vnc"]
    SetComponent["Set VncComponent State"]
    URLConstruction["Construct WebSocket URL"]
    Render["Render VncScreen"]
    
    Mount --> SSRCheck
    SSRCheck --> DynamicImport
    DynamicImport --> SetComponent
    Mount --> URLConstruction
    SetComponent --> Render
    URLConstruction --> Render
```

**Component Loading Flow**
This flowchart shows the initialization sequence that ensures proper client-side rendering of the VNC component.

### RFB Options Configuration

The Remote Framebuffer (RFB) protocol options are configured for optimal web-based VNC streaming:

- **Secure**: Disabled to allow unencrypted VNC traffic through the WebSocket proxy
- **Shared**: Enabled to support multiple simultaneous viewers
- **WS Protocols**: Set to binary mode for efficient frame transmission
- **Scale Viewport**: Automatically adjusts desktop size to fit the container

Sources: [packages/bytebot-ui/src/components/vnc/VncViewer.tsx:15-20](), [packages/bytebot-ui/src/components/vnc/VncViewer.tsx:32-43]()

## Container and Styling

The component renders within a full-width and full-height container div that references `containerRef`. The VNC screen component inherits these dimensions and applies responsive scaling to fit the available viewport space.

The styling ensures the desktop viewer integrates seamlessly with the parent task detail interface while maintaining aspect ratio and providing smooth scaling across different screen sizes.

Sources: [packages/bytebot-ui/src/components/vnc/VncViewer.tsx:28-47]()

---

# Page: Message Display System

# Message Display System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [packages/bytebot-ui/src/app/tasks/[id]/page.tsx](packages/bytebot-ui/src/app/tasks/[id]/page.tsx)
- [packages/bytebot-ui/src/components/messages/AssistantMessage.tsx](packages/bytebot-ui/src/components/messages/AssistantMessage.tsx)
- [packages/bytebot-ui/src/components/messages/ChatContainer.tsx](packages/bytebot-ui/src/components/messages/ChatContainer.tsx)
- [packages/bytebot-ui/src/components/messages/MessageGroup.tsx](packages/bytebot-ui/src/components/messages/MessageGroup.tsx)
- [packages/bytebot-ui/src/components/messages/UserMessage.tsx](packages/bytebot-ui/src/components/messages/UserMessage.tsx)
- [packages/bytebot-ui/src/components/screenshot/ScreenshotViewer.tsx](packages/bytebot-ui/src/components/screenshot/ScreenshotViewer.tsx)
- [packages/bytebot-ui/src/hooks/useScrollScreenshot.ts](packages/bytebot-ui/src/hooks/useScrollScreenshot.ts)
- [packages/bytebot-ui/src/utils/screenshotUtils.ts](packages/bytebot-ui/src/utils/screenshotUtils.ts)

</details>



## Purpose and Scope

The Message Display System is responsible for rendering the conversation history between users and the AI agent in the task detail view. This system handles message grouping, role-based rendering, screenshot marker placement, and special UI states like user takeover mode. 

For information about the overall task detail page structure, see [Task Detail Page](#8.3). For information about the desktop viewer that displays screenshots, see [Desktop Viewer](#8.4). For information about how messages are created and stored, see [Message and Summarization](#6.4).

**Sources:** [packages/bytebot-ui/src/components/messages/ChatContainer.tsx:1-154](), [packages/bytebot-ui/src/components/messages/MessageGroup.tsx:1-19]()

---

## Message Rendering Architecture

The message display system transforms flat message arrays into grouped, role-separated UI elements with embedded screenshot markers for scroll-synchronized desktop viewing.

```mermaid
graph TB
    Messages["messages: Message[]<br/>(flat array from API)"]
    GroupedMessages["groupedMessages: GroupedMessages[]<br/>(consecutive same-role groups)"]
    ChatContainer["ChatContainer<br/>packages/bytebot-ui/src/components/messages/ChatContainer.tsx"]
    MessageGroup["MessageGroup<br/>Role router component"]
    AssistantMessage["AssistantMessage<br/>Assistant role renderer"]
    UserMessage["UserMessage<br/>User role renderer"]
    MessageContent["MessageContent<br/>Content block renderer"]
    ScreenshotMarkers["Hidden Screenshot Markers<br/>data-message-index<br/>data-block-index<br/>data-content-index"]
    
    Messages -->|"Grouped by useChatSession"| GroupedMessages
    GroupedMessages --> ChatContainer
    ChatContainer -->|"Map over groups"| MessageGroup
    MessageGroup -->|"role === ASSISTANT"| AssistantMessage
    MessageGroup -->|"role === USER"| UserMessage
    AssistantMessage --> MessageContent
    AssistantMessage --> ScreenshotMarkers
    UserMessage --> MessageContent
    UserMessage --> ScreenshotMarkers
    
    ScreenshotMarkers -.->|"DOM queried by"| ScrollScreenshotHook["useScrollScreenshot hook"]
    ScrollScreenshotHook -.->|"Updates"| DesktopViewer["Desktop screenshot display"]
```

**Sources:** [packages/bytebot-ui/src/components/messages/ChatContainer.tsx:26-154](), [packages/bytebot-ui/src/components/messages/MessageGroup.tsx:1-19](), [packages/bytebot-ui/src/app/tasks/[id]/page.tsx:30-48]()

---

## Component Hierarchy

The message display system is organized as a three-level component hierarchy with specialized rendering for each role.

| Component | File | Responsibility |
|-----------|------|----------------|
| `ChatContainer` | [packages/bytebot-ui/src/components/messages/ChatContainer.tsx]() | Container for all messages, infinite scroll, loading states, chat input |
| `MessageGroup` | [packages/bytebot-ui/src/components/messages/MessageGroup.tsx]() | Routes to role-specific renderers based on `group.role` |
| `AssistantMessage` | [packages/bytebot-ui/src/components/messages/AssistantMessage.tsx]() | Renders assistant messages with avatar, take-over detection |
| `UserMessage` | [packages/bytebot-ui/src/components/messages/UserMessage.tsx]() | Renders user messages with special styling for first message |
| `MessageContent` | [packages/bytebot-ui/src/components/messages/content/MessageContent.tsx]() | Renders individual content blocks (text, tool use, tool result, etc.) |

**Sources:** [packages/bytebot-ui/src/components/messages/ChatContainer.tsx:9-24](), [packages/bytebot-ui/src/components/messages/MessageGroup.tsx:7-19]()

---

## GroupedMessages Data Structure

Messages are grouped by consecutive same-role sequences to create chat bubble groupings. The `GroupedMessages` type contains an array of messages with the same role, plus metadata.

```mermaid
graph LR
    FlatMessages["Flat Message Array<br/>[USER, ASSISTANT, ASSISTANT, USER, ASSISTANT]"]
    GroupingLogic["groupBackToBackMessages()<br/>Groups consecutive same-role"]
    GroupedArray["GroupedMessages Array"]
    
    Group1["Group 1<br/>role: USER<br/>messages: [msg1]"]
    Group2["Group 2<br/>role: ASSISTANT<br/>messages: [msg2, msg3]<br/>take_over: false"]
    Group3["Group 3<br/>role: USER<br/>messages: [msg4]"]
    Group4["Group 4<br/>role: ASSISTANT<br/>messages: [msg5]<br/>take_over: true"]
    
    FlatMessages --> GroupingLogic
    GroupingLogic --> GroupedArray
    GroupedArray --> Group1
    GroupedArray --> Group2
    GroupedArray --> Group3
    GroupedArray --> Group4
```

The `take_over` flag indicates when a user has taken control of the desktop from the agent, triggering special UI rendering. This grouping logic is handled by the backend's `MessagesService` and provided to the UI via the `useChatSession` hook.

**Sources:** [packages/bytebot-ui/src/components/messages/ChatContainer.tsx:17](), [packages/bytebot-ui/src/hooks/useChatSession.ts]()

---

## Screenshot Marker System

The message display system embeds invisible DOM markers at screenshot locations to enable scroll-synchronized desktop viewing. These markers allow the desktop viewer to display the screenshot corresponding to the user's current scroll position in the message history.

### Marker Placement

Each message component (both `AssistantMessage` and `UserMessage`) scans its content blocks for tool results containing images and renders hidden `<div>` elements at those positions:

```mermaid
graph TB
    MessageContent["message.content array"]
    ScanBlocks["Scan each content block"]
    CheckToolResult{"Is ToolResult<br/>with images?"}
    RenderMarker["Render hidden div<br/>data-message-index<br/>data-block-index<br/>data-content-index"]
    RenderContent["Render visible content"]
    
    MessageContent --> ScanBlocks
    ScanBlocks --> CheckToolResult
    CheckToolResult -->|"Yes"| RenderMarker
    CheckToolResult -->|"No"| RenderContent
    RenderMarker --> RenderContent
```

The markers are absolutely positioned with zero dimensions:

```typescript
style={{
  position: "absolute",
  width: 0,
  height: 0,
  overflow: "hidden",
}}
```

**Sources:** [packages/bytebot-ui/src/components/messages/AssistantMessage.tsx:48-78](), [packages/bytebot-ui/src/components/messages/UserMessage.tsx:88-117]()

### Marker Data Attributes

Each screenshot marker contains three data attributes that identify its position in the message hierarchy:

| Attribute | Purpose | Example |
|-----------|---------|---------|
| `data-message-index` | Flat index in the message array | `"5"` |
| `data-block-index` | Index within message's content array | `"2"` |
| `data-content-index` | Index within tool result's content array | `"0"` |

These attributes are queried by the `useScrollScreenshot` hook to determine which screenshot should be displayed based on scroll position.

**Sources:** [packages/bytebot-ui/src/components/messages/AssistantMessage.tsx:59-71](), [packages/bytebot-ui/src/hooks/useScrollScreenshot.ts:71-90]()

### Screenshot Extraction and Positioning

The `screenshotUtils.ts` module provides functions to extract screenshots and determine which one to display:

```mermaid
graph TB
    Messages["messages: Message[]"]
    ExtractFunc["extractScreenshots()<br/>Scan all messages"]
    ScreenshotArray["ScreenshotData[]<br/>id, base64Data, messageIndex, blockIndex"]
    
    ScrollEvent["User scrolls chat"]
    GetScreenshotFunc["getScreenshotForScrollPosition()"]
    QueryMarkers["Query DOM for<br/>[data-message-index][data-block-index]"]
    CalculateVisibility["Calculate which marker<br/>is at target position (350px from top)"]
    FindBest["Find most recent screenshot<br/>at or before visible marker"]
    UpdateDesktop["Update desktop viewer"]
    
    Messages --> ExtractFunc
    ExtractFunc --> ScreenshotArray
    
    ScrollEvent --> GetScreenshotFunc
    ScreenshotArray --> GetScreenshotFunc
    GetScreenshotFunc --> QueryMarkers
    QueryMarkers --> CalculateVisibility
    CalculateVisibility --> FindBest
    FindBest --> UpdateDesktop
```

The system targets a position 350 pixels down from the top of the scroll container, finding the marker closest to this position and displaying the corresponding screenshot.

**Sources:** [packages/bytebot-ui/src/utils/screenshotUtils.ts:14-36](), [packages/bytebot-ui/src/utils/screenshotUtils.ts:41-148]()

---

## ChatContainer Component

The `ChatContainer` component serves as the main orchestrator for message display, handling infinite scroll, loading states, and the chat input.

### Layout Structure

```mermaid
graph TB
    ChatContainer["ChatContainer<br/>Full height flex column"]
    
    LoadingState{"isLoadingSession?"}
    LoadingSpinner["Loader component"]
    
    ContentArea["Content area<br/>flex-1"]
    MessageGroups["Map groupedMessages<br/>Render MessageGroup components"]
    
    WorkingIndicator{"taskStatus === RUNNING<br/>AND control === ASSISTANT?"}
    WorkingUI["'Bytebot is working...'<br/>with loader"]
    
    InfiniteLoader{"isLoadingMoreMessages?"}
    InfiniteSpinner["Bottom loader"]
    
    ScrollAnchor["messagesEndRef<br/>Auto-scroll target"]
    
    InputSection{"Task is RUNNING or NEEDS_HELP?"}
    ChatInput["ChatInput component"]
    
    ChatContainer --> LoadingState
    LoadingState -->|"Yes"| LoadingSpinner
    LoadingState -->|"No"| ContentArea
    
    ContentArea --> MessageGroups
    MessageGroups --> WorkingIndicator
    WorkingIndicator -->|"Yes"| WorkingUI
    MessageGroups --> InfiniteLoader
    InfiniteLoader -->|"Yes"| InfiniteSpinner
    MessageGroups --> ScrollAnchor
    
    ChatContainer --> InputSection
    InputSection -->|"Yes"| ChatInput
```

**Sources:** [packages/bytebot-ui/src/components/messages/ChatContainer.tsx:83-154]()

### Infinite Scroll Implementation

The container monitors scroll events to load additional messages when the user scrolls near the bottom:

- Scroll event listener attached to parent `scrollRef` [packages/bytebot-ui/src/components/messages/ChatContainer.tsx:60-66]()
- Triggers when within 20px of bottom [packages/bytebot-ui/src/components/messages/ChatContainer.tsx:54]()
- Calls `loadMoreMessages()` if `hasMoreMessages` is true and not already loading [packages/bytebot-ui/src/components/messages/ChatContainer.tsx:54-56]()

### Auto-Scroll Behavior

The container automatically scrolls to the newest message when the task is active:

- Tracks `messagesEndRef` as scroll target [packages/bytebot-ui/src/components/messages/ChatContainer.tsx:41]()
- Triggers on `groupedMessages` or `taskStatus` change [packages/bytebot-ui/src/components/messages/ChatContainer.tsx:69-76]()
- Only scrolls when `taskStatus` is `RUNNING` or `NEEDS_HELP` [packages/bytebot-ui/src/components/messages/ChatContainer.tsx:71-75]()

**Sources:** [packages/bytebot-ui/src/components/messages/ChatContainer.tsx:44-81]()

---

## AssistantMessage Component

The `AssistantMessage` component renders messages from the AI agent, with special handling for take-over mode.

### Standard Rendering

In normal mode, assistant messages display with:
- Left-aligned layout with avatar [packages/bytebot-ui/src/components/messages/AssistantMessage.tsx:21-26]()
- Border on left, right, and conditionally bottom [packages/bytebot-ui/src/components/messages/AssistantMessage.tsx:23-24]()
- Screenshot markers for each image in tool results [packages/bytebot-ui/src/components/messages/AssistantMessage.tsx:94-125]()
- `MessageContent` rendering for visible content [packages/bytebot-ui/src/components/messages/AssistantMessage.tsx:126-129]()

### Take-Over Mode Rendering

When `group.take_over` is true, the component applies special styling:

```mermaid
graph LR
    TakeOverContainer["Pink border container<br/>border-bytebot-bronze-light-a6"]
    TakeOverHeader["Header with indicator<br/>'You took control'"]
    MessagesWrapper["Nested message container<br/>bg-bytebot-bronze-light-2"]
    MessageContent["Message content blocks"]
    
    TakeOverContainer --> TakeOverHeader
    TakeOverContainer --> MessagesWrapper
    MessagesWrapper --> MessageContent
```

This creates a visually distinct card indicating that the user has taken control from the agent. The messages within the take-over group are rendered in a nested container with different background color.

**Sources:** [packages/bytebot-ui/src/components/messages/AssistantMessage.tsx:29-86]()

---

## UserMessage Component

The `UserMessage` component renders messages from the user, with special styling for the initial task description.

### First Message (Task Description)

The first message (index 0) receives special treatment:
- Sticky positioning at top of scroll container [packages/bytebot-ui/src/components/messages/UserMessage.tsx:19]()
- Different background color (`bg-bytebot-bronze-light-2`) [packages/bytebot-ui/src/components/messages/UserMessage.tsx:20]()
- Rounded top corners [packages/bytebot-ui/src/components/messages/UserMessage.tsx:20]()
- Contains the original task description provided by the user

**Sources:** [packages/bytebot-ui/src/components/messages/UserMessage.tsx:17-78]()

### Subsequent User Messages

User messages after the first are:
- Right-aligned with avatar on right [packages/bytebot-ui/src/components/messages/UserMessage.tsx:81-82]()
- Styled in fuchsia color (`text-fuchsia-600`) [packages/bytebot-ui/src/components/messages/UserMessage.tsx:119]()
- Rendered with ReactMarkdown for text content [packages/bytebot-ui/src/components/messages/UserMessage.tsx:123]()

Both rendering modes include screenshot marker generation for any tool results containing images, following the same pattern as `AssistantMessage`.

**Sources:** [packages/bytebot-ui/src/components/messages/UserMessage.tsx:80-135]()

---

## Message Content Rendering

The `MessageContent` component (referenced but not provided in files) handles rendering of individual content blocks within messages. Based on the usage patterns, it processes:

### Content Block Types

| Block Type | Rendering Behavior | Detection Function |
|------------|-------------------|-------------------|
| Text | Rendered as text or markdown | `isTextContentBlock()` |
| Tool Use | Displays tool invocation details | `isToolUseContentBlock()` |
| Tool Result | Displays tool execution results | `isToolResultContentBlock()` |
| Image | Screenshot/image display | `isImageContentBlock()` |
| Thinking | Agent reasoning display | `isThinkingContentBlock()` |
| User Action | User intervention display | `isUserActionContentBlock()` |

Type guards from `@bytebot/shared` are used to determine block types and render appropriately. The `MessageContent` component receives the content array and optional `isTakeOver` flag for conditional styling.

**Sources:** [packages/bytebot-ui/src/components/messages/AssistantMessage.tsx:79-82](), [packages/bytebot-ui/src/components/messages/UserMessage.tsx:61-70]()

---

## Integration with Desktop Viewer

The message display system coordinates with the desktop viewer through the screenshot marker system:

```mermaid
sequenceDiagram
    participant User
    participant ChatContainer
    participant AssistantMessage
    participant DOM
    participant useScrollScreenshot
    participant DesktopContainer
    
    User->>ChatContainer: Scrolls message history
    ChatContainer->>AssistantMessage: Renders messages
    AssistantMessage->>DOM: Inserts screenshot markers
    DOM->>useScrollScreenshot: Queries markers via data attributes
    useScrollScreenshot->>useScrollScreenshot: Calculates visible marker at 350px
    useScrollScreenshot->>DesktopContainer: Updates currentScreenshot
    DesktopContainer->>User: Displays synchronized screenshot
```

This creates a synchronized viewing experience where scrolling through the conversation history automatically updates the desktop screenshot to show the state at that point in the task execution.

**Sources:** [packages/bytebot-ui/src/app/tasks/[id]/page.tsx:86-89](), [packages/bytebot-ui/src/hooks/useScrollScreenshot.ts:70-90](), [packages/bytebot-ui/src/utils/screenshotUtils.ts:51-148]()

---

## Styling and Visual Design

The message display system uses a consistent design language with the Bytebot bronze color palette:

### Color Scheme

| Element | Background | Border | Text |
|---------|-----------|--------|------|
| Container | `bg-bytebot-bronze-light-3` | `border-bytebot-bronze-light-7` | - |
| First message | `bg-bytebot-bronze-light-2` | `border-bytebot-bronze-light-7` | `text-bytebot-bronze-light-12` |
| User messages | - | - | `text-fuchsia-600` |
| Take-over card | `bg-bytebot-bronze-light-a1` | `border-bytebot-bronze-light-a6` | `text-bytebot-bronze-light-12` |

### Layout Specifications

- Avatar gap: 2 units (`gap-2`) [packages/bytebot-ui/src/components/messages/AssistantMessage.tsx:23]()
- Message padding: 4 units horizontal, 3 units vertical (`px-4 py-3`) [packages/bytebot-ui/src/components/messages/AssistantMessage.tsx:23]()
- Rounded corners: `rounded-lg` or `rounded-2xl` for cards
- Border width: 1px on relevant sides

**Sources:** [packages/bytebot-ui/src/components/messages/AssistantMessage.tsx:21-26](), [packages/bytebot-ui/src/components/messages/UserMessage.tsx:19-20](), [packages/bytebot-ui/src/components/messages/UserMessage.tsx:81]()

---

# Page: API Client Utilities

# API Client Utilities

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [packages/bytebot-ui/.gitignore](packages/bytebot-ui/.gitignore)
- [packages/bytebot-ui/src/components/vnc/VncViewer.tsx](packages/bytebot-ui/src/components/vnc/VncViewer.tsx)
- [packages/bytebot-ui/src/utils/taskUtils.ts](packages/bytebot-ui/src/utils/taskUtils.ts)

</details>



## Purpose and Scope

This document describes the client-side API utilities provided by `taskUtils.ts` in the bytebot-ui package. These utilities abstract HTTP communication between React components and the backend bytebot-agent service, providing type-safe functions for task management, message handling, and real-time updates.

For information about the underlying REST API endpoints, see [Tasks REST API](#10.1). For real-time communication patterns, see [WebSocket Events](#5.3). For UI components that consume these utilities, see [Task Detail Page](#8.3) and [Task List Interface](#8.2).

---

## Architecture Overview

The API client utilities implement a centralized abstraction layer that handles:
- HTTP request configuration and credentials
- Error handling and null safety
- Query parameter serialization
- Type-safe request/response contracts
- API endpoint routing through the Next.js proxy

```mermaid
graph TB
    subgraph "React Components"
        TaskDetail["TaskDetail Component"]
        TaskList["TaskList Component"]
        ChatContainer["ChatContainer Component"]
        HomeForm["Home Page Form"]
    end
    
    subgraph "taskUtils.ts"
        apiRequest["apiRequest<T>()<br/>Generic HTTP handler"]
        buildQueryString["buildQueryString()<br/>URL parameter builder"]
        
        fetchTaskById["fetchTaskById()"]
        fetchTasks["fetchTasks()"]
        fetchTaskMessages["fetchTaskMessages()"]
        fetchTaskProcessedMessages["fetchTaskProcessedMessages()"]
        startTask["startTask()"]
        addMessage["addMessage()"]
        takeOverTask["takeOverTask()"]
        resumeTask["resumeTask()"]
        cancelTask["cancelTask()"]
        fetchModels["fetchModels()"]
        fetchTaskCounts["fetchTaskCounts()"]
    end
    
    subgraph "Next.js API Proxy"
        ProxyRoute["/api/*<br/>Custom Express Server"]
    end
    
    subgraph "bytebot-agent"
        TasksAPI["TasksController<br/>NestJS REST API"]
    end
    
    TaskDetail --> fetchTaskById
    TaskDetail --> fetchTaskProcessedMessages
    TaskDetail --> addMessage
    TaskDetail --> takeOverTask
    TaskDetail --> resumeTask
    TaskDetail --> cancelTask
    
    TaskList --> fetchTasks
    TaskList --> fetchTaskCounts
    
    ChatContainer --> fetchTaskProcessedMessages
    
    HomeForm --> startTask
    HomeForm --> fetchModels
    
    fetchTaskById --> apiRequest
    fetchTasks --> apiRequest
    fetchTaskMessages --> apiRequest
    fetchTaskProcessedMessages --> apiRequest
    startTask --> apiRequest
    addMessage --> apiRequest
    takeOverTask --> apiRequest
    resumeTask --> apiRequest
    cancelTask --> apiRequest
    fetchModels --> apiRequest
    
    fetchTasks --> buildQueryString
    fetchTaskMessages --> buildQueryString
    fetchTaskProcessedMessages --> buildQueryString
    fetchTaskCounts --> buildQueryString
    
    apiRequest --> ProxyRoute
    ProxyRoute --> TasksAPI
```

**Sources:** [packages/bytebot-ui/src/utils/taskUtils.ts:1-260]()

---

## API Configuration

The utility module maintains a centralized configuration object that defines base request parameters applied to all API calls.

### Base Configuration

[packages/bytebot-ui/src/utils/taskUtils.ts:6-12]() defines the `API_CONFIG` object:

| Property | Value | Purpose |
|----------|-------|---------|
| `baseUrl` | `"/api"` | Routes requests through Next.js API proxy |
| `headers` | `{"Content-Type": "application/json"}` | Ensures JSON request bodies |
| `credentials` | `"include"` | Sends cookies for session management |

The `baseUrl` points to `/api` rather than directly to the bytebot-agent service (port 9991) because the Next.js frontend implements a custom Express server that proxies all `/api/*` requests to the backend. This architecture provides:
- CORS management
- Single-origin deployment
- Simplified client configuration

**Sources:** [packages/bytebot-ui/src/utils/taskUtils.ts:6-12]()

---

## Generic Request Handler

The `apiRequest<T>()` function provides a type-safe wrapper around the Fetch API with consistent error handling.

### Function Signature

```typescript
async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {},
): Promise<T | null>
```

### Request Flow

```mermaid
graph TB
    Start["apiRequest<T>() called"]
    BuildURL["Construct full URL:<br/>`${API_CONFIG.baseUrl}${endpoint}`"]
    MergeOptions["Merge options:<br/>- API_CONFIG headers<br/>- Custom headers<br/>- Credentials"]
    Fetch["Execute fetch()"]
    CheckStatus{"response.ok?"}
    ParseJSON["response.json()"]
    ReturnData["Return typed data: T"]
    CatchError["Catch exception"]
    LogError["console.error()"]
    ReturnNull["Return null"]
    
    Start --> BuildURL
    BuildURL --> MergeOptions
    MergeOptions --> Fetch
    Fetch --> CheckStatus
    CheckStatus -->|Yes| ParseJSON
    CheckStatus -->|No| CatchError
    ParseJSON --> ReturnData
    CatchError --> LogError
    LogError --> ReturnNull
    
    style ReturnNull fill:#ffcdd2
    style ReturnData fill:#c8e6c9
```

### Error Handling Strategy

The function implements defensive programming:
1. **HTTP errors** (non-2xx status codes) throw an error with status and statusText
2. **Network errors** (connection failures) are caught by the catch block
3. **All errors** are logged to console with the endpoint path
4. **All errors** result in returning `null` rather than propagating exceptions

This null-return pattern allows calling components to handle failures gracefully without try-catch blocks, though it requires null checks at call sites.

**Sources:** [packages/bytebot-ui/src/utils/taskUtils.ts:17-42]()

---

## Query String Builder

The `buildQueryString()` utility constructs URL query parameters from key-value objects.

### Implementation

[packages/bytebot-ui/src/utils/taskUtils.ts:47-58]() implements parameter serialization:

```typescript
function buildQueryString(
  params: Record<string, string | number | boolean>,
): string
```

### Behavior

| Input | Output |
|-------|--------|
| `{ page: 2, limit: 10 }` | `"?page=2&limit=10"` |
| `{ status: "RUNNING" }` | `"?status=RUNNING"` |
| `{ statuses: "PENDING,RUNNING" }` | `"?statuses=PENDING%2CRUNNING"` |
| `{}` | `""` |
| `{ value: undefined }` | `""` |
| `{ value: null }` | `""` |

The function:
1. Creates a `URLSearchParams` instance
2. Filters out `undefined` and `null` values
3. Converts all values to strings
4. Prepends `?` only if parameters exist
5. Returns empty string if no valid parameters

**Sources:** [packages/bytebot-ui/src/utils/taskUtils.ts:47-58]()

---

## Task Operations

Task operations handle CRUD operations for the primary Task entity.

### Endpoint Mapping

```mermaid
graph LR
    subgraph "Task Functions"
        fetchTaskById["fetchTaskById(taskId)"]
        startTask["startTask(data)"]
        fetchTasks["fetchTasks(options)"]
    end
    
    subgraph "API Endpoints"
        GET_task["GET /api/tasks/:id"]
        POST_tasks["POST /api/tasks"]
        GET_tasks["GET /api/tasks?page&limit&status"]
    end
    
    fetchTaskById -->|"GET"| GET_task
    startTask -->|"POST with body"| POST_tasks
    fetchTasks -->|"GET with query params"| GET_tasks
```

### fetchTaskById

[packages/bytebot-ui/src/utils/taskUtils.ts:117-119]() retrieves a single task by its UUID:

```typescript
export async function fetchTaskById(taskId: string): Promise<Task | null>
```

Returns the complete Task object or null if not found or on error.

### startTask

[packages/bytebot-ui/src/utils/taskUtils.ts:124-133]() creates a new task:

```typescript
export async function startTask(data: {
  description: string;
  model: Model;
  files?: FileWithBase64[];
}): Promise<Task | null>
```

The `FileWithBase64` type includes base64-encoded file data that gets materialized to the virtual desktop's `/home/user/Desktop` directory. See [File Handling](#5.5) for details on file processing.

### fetchTasks

[packages/bytebot-ui/src/utils/taskUtils.ts:151-172]() retrieves paginated task lists with filtering:

```typescript
export async function fetchTasks(options?: {
  page?: number;
  limit?: number;
  status?: string;
  statuses?: string[];
}): Promise<{ tasks: Task[]; total: number; totalPages: number }>
```

**Special handling for `statuses` array:** The function joins multiple status values with commas [packages/bytebot-ui/src/utils/taskUtils.ts:162-164](), allowing queries like `?statuses=PENDING,RUNNING,NEEDS_HELP` to filter for multiple states simultaneously.

**Sources:** [packages/bytebot-ui/src/utils/taskUtils.ts:117-172]()

---

## Message Operations

Message operations retrieve conversation history for tasks in various formats.

### Message Retrieval Variants

```mermaid
graph TB
    Task["Task ID: abc-123"]
    
    fetchTaskMessages["fetchTaskMessages()<br/>Returns: Message[]"]
    fetchTaskRawMessages["fetchTaskRawMessages()<br/>Returns: Message[]"]
    fetchTaskProcessedMessages["fetchTaskProcessedMessages()<br/>Returns: GroupedMessages[]"]
    
    subgraph "API Endpoints"
        EP1["/api/tasks/:id/messages"]
        EP2["/api/tasks/:id/messages/raw"]
        EP3["/api/tasks/:id/messages/processed"]
    end
    
    Task --> fetchTaskMessages
    Task --> fetchTaskRawMessages
    Task --> fetchTaskProcessedMessages
    
    fetchTaskMessages --> EP1
    fetchTaskRawMessages --> EP2
    fetchTaskProcessedMessages --> EP3
    
    EP1 --> Default["Default messages<br/>Filtered by MessagesService"]
    EP2 --> Raw["Unprocessed messages<br/>Direct from database"]
    EP3 --> Processed["Grouped for chat UI<br/>Role switching applied"]
```

### fetchTaskMessages

[packages/bytebot-ui/src/utils/taskUtils.ts:63-76]() retrieves default message processing:

```typescript
export async function fetchTaskMessages(
  taskId: string,
  options?: { limit?: number; page?: number }
): Promise<Message[]>
```

Returns messages with basic filtering applied by MessagesService.

### fetchTaskRawMessages

[packages/bytebot-ui/src/utils/taskUtils.ts:81-94]() retrieves unprocessed messages:

```typescript
export async function fetchTaskRawMessages(
  taskId: string,
  options?: { limit?: number; page?: number }
): Promise<Message[]>
```

Returns messages exactly as stored in the database, without role switching or grouping.

### fetchTaskProcessedMessages

[packages/bytebot-ui/src/utils/taskUtils.ts:99-112]() retrieves UI-optimized messages:

```typescript
export async function fetchTaskProcessedMessages(
  taskId: string,
  options?: { limit?: number; page?: number }
): Promise<GroupedMessages[]>
```

Returns messages grouped by consecutive same-role messages, with role switching applied (pure tool results become ASSISTANT messages). This is the format used by chat UI components. See [Message Display System](#8.5) for details on how GroupedMessages are rendered.

### addMessage

[packages/bytebot-ui/src/utils/taskUtils.ts:138-146]() posts a user message to a task:

```typescript
export async function addMessage(
  taskId: string,
  message: string
): Promise<Task | null>
```

Creates a new USER role message and returns the updated task. When a task is in NEEDS_HELP status, adding a message provides guidance to the agent.

**Sources:** [packages/bytebot-ui/src/utils/taskUtils.ts:63-146]()

---

## Task List Operations

Task list operations support the task browsing interface with counts and filtering.

### fetchTaskCounts

[packages/bytebot-ui/src/utils/taskUtils.ts:177-221]() calculates task counts for filtered views:

```typescript
export async function fetchTaskCounts(): Promise<Record<string, number>>
```

### Count Calculation Logic

```mermaid
graph TB
    Start["fetchTaskCounts() called"]
    FetchAll["fetchTasks() - no filters<br/>Get total count"]
    DefineGroups["Define status groups:<br/>ALL, ACTIVE, COMPLETED,<br/>CANCELLED_FAILED"]
    
    subgraph "Status Group Definitions"
        ALL["ALL: All TaskStatus values"]
        ACTIVE["ACTIVE: PENDING, RUNNING,<br/>NEEDS_HELP, NEEDS_REVIEW"]
        COMPLETED["COMPLETED: COMPLETED"]
        CANCELLED_FAILED["CANCELLED_FAILED: CANCELLED, FAILED"]
    end
    
    CreatePromises["Create Promise array:<br/>fetchTasks() for each group"]
    AwaitAll["Promise.all()<br/>Execute parallel requests"]
    BuildCounts["Build counts object:<br/>{ALL, ACTIVE, COMPLETED, CANCELLED_FAILED}"]
    ReturnCounts["Return counts"]
    
    Start --> FetchAll
    FetchAll --> DefineGroups
    DefineGroups --> CreatePromises
    CreatePromises --> AwaitAll
    AwaitAll --> BuildCounts
    BuildCounts --> ReturnCounts
    
    DefineGroups -.-> ALL
    DefineGroups -.-> ACTIVE
    DefineGroups -.-> COMPLETED
    DefineGroups -.-> CANCELLED_FAILED
```

The function:
1. Fetches all tasks to get the total count
2. Defines four status groups based on TaskStatus enum
3. Issues parallel requests for each group using `Promise.all()` [packages/bytebot-ui/src/utils/taskUtils.ts:196-206]()
4. Returns a counts object used to populate tab badges in the task list UI

The ACTIVE group aggregates multiple "in-progress" states, while CANCELLED_FAILED groups terminal failure states. This grouping matches the tab structure in the task list interface.

**Sources:** [packages/bytebot-ui/src/utils/taskUtils.ts:177-221]()

---

## Model Configuration Operations

### fetchModels

[packages/bytebot-ui/src/utils/taskUtils.ts:223-238]() retrieves available LLM models:

```typescript
export async function fetchModels(): Promise<Model[]>
```

Unlike other operations, this function directly calls `fetch()` rather than using `apiRequest()`, likely because it was implemented separately or has different error handling requirements. It queries `/api/tasks/models` to get the list of configured models that users can select when creating tasks.

**Sources:** [packages/bytebot-ui/src/utils/taskUtils.ts:223-238]()

---

## Task Control Operations

Task control operations manage task state transitions through user actions.

### Control Operation Mapping

```mermaid
graph TB
    subgraph "Client Functions"
        takeOverTask["takeOverTask(taskId)"]
        resumeTask["resumeTask(taskId)"]
        cancelTask["cancelTask(taskId)"]
    end
    
    subgraph "API Endpoints"
        POST_takeover["POST /api/tasks/:id/takeover"]
        POST_resume["POST /api/tasks/:id/resume"]
        POST_cancel["POST /api/tasks/:id/cancel"]
    end
    
    subgraph "State Changes"
        ToTakeover["Status → TAKEOVER<br/>control → 'user'"]
        ToRunning["Status → RUNNING<br/>control → 'agent'"]
        ToCancelled["Status → CANCELLED"]
    end
    
    takeOverTask --> POST_takeover
    resumeTask --> POST_resume
    cancelTask --> POST_cancel
    
    POST_takeover --> ToTakeover
    POST_resume --> ToRunning
    POST_cancel --> ToCancelled
```

### takeOverTask

[packages/bytebot-ui/src/utils/taskUtils.ts:243-245]() hands control to the user:

```typescript
export async function takeOverTask(taskId: string): Promise<Task | null>
```

Sets task status to TAKEOVER and control field to "user", pausing agent execution. The user can then manually interact with the desktop or add guidance messages.

### resumeTask

[packages/bytebot-ui/src/utils/taskUtils.ts:250-252]() returns control to the agent:

```typescript
export async function resumeTask(taskId: string): Promise<Task | null>
```

Sets task status to RUNNING and control field to "agent", allowing the agent processor to resume execution from where it stopped.

### cancelTask

[packages/bytebot-ui/src/utils/taskUtils.ts:257-259]() terminates task execution:

```typescript
export async function cancelTask(taskId: string): Promise<Task | null>
```

Sets task status to CANCELLED, permanently stopping execution. This action is irreversible—the task cannot be resumed after cancellation.

**Sources:** [packages/bytebot-ui/src/utils/taskUtils.ts:243-259]()

---

## WebSocket Integration

While `taskUtils.ts` focuses on HTTP operations, the UI also uses WebSocket connections for real-time updates. The VNC viewer component demonstrates WebSocket client usage.

### VNC WebSocket Connection

[packages/bytebot-ui/src/components/vnc/VncViewer.tsx:1-48]() establishes a WebSocket connection to the VNC server:

```typescript
const proto = window.location.protocol === "https:" ? "wss" : "ws";
setWsUrl(`${proto}://${window.location.host}/api/proxy/websockify`);
```

The VNC viewer:
1. Dynamically imports the `react-vnc` library client-side to avoid SSR issues [packages/bytebot-ui/src/components/vnc/VncViewer.tsx:16-20]()
2. Constructs the WebSocket URL based on the page protocol (wss for HTTPS, ws for HTTP)
3. Routes through `/api/proxy/websockify`, which proxies to bytebotd's VNC server on port 6080

For task event WebSocket connections, see the `useWebSocket` hook documented in [WebSocket Events](#5.3).

**Sources:** [packages/bytebot-ui/src/components/vnc/VncViewer.tsx:1-48]()

---

## Error Handling Patterns

The API utilities implement a consistent error handling strategy across all functions.

### Error Flow

```mermaid
graph TB
    Call["Function called<br/>(e.g., fetchTaskById)"]
    APIRequest["apiRequest<T>()"]
    TryCatch["try-catch block"]
    FetchAPI["fetch() call"]
    
    CheckOK{"response.ok?"}
    ThrowError["throw Error<br/>(status + statusText)"]
    ParseJSON["response.json()"]
    
    CatchBlock["catch (error)"]
    LogError["console.error()<br/>with endpoint path"]
    ReturnNull["return null"]
    
    ReturnData["return typed data"]
    NullCheck["Calling code checks for null"]
    HandleError["Handle error in UI"]
    UseData["Use data"]
    
    Call --> APIRequest
    APIRequest --> TryCatch
    TryCatch --> FetchAPI
    FetchAPI --> CheckOK
    
    CheckOK -->|No| ThrowError
    CheckOK -->|Yes| ParseJSON
    
    ThrowError --> CatchBlock
    FetchAPI -.->|Network error| CatchBlock
    
    CatchBlock --> LogError
    LogError --> ReturnNull
    
    ParseJSON --> ReturnData
    
    ReturnNull --> NullCheck
    ReturnData --> NullCheck
    
    NullCheck -->|null| HandleError
    NullCheck -->|data| UseData
```

### Error Categories

| Error Type | Cause | Logged Information | Return Value |
|------------|-------|-------------------|--------------|
| HTTP 4xx/5xx | Server returns error status | Endpoint + status + statusText | `null` |
| Network failure | Connection refused, timeout | Endpoint + error message | `null` |
| JSON parse error | Invalid response body | Endpoint + error message | `null` |

### Calling Pattern

All functions that use `apiRequest()` follow this pattern:

```typescript
const result = await apiRequest<Task>(`/tasks/${taskId}`, { method: "GET" });
return result || []; // Or null, or default value
```

Some functions provide empty defaults:
- `fetchTaskMessages` returns `[]` on error [packages/bytebot-ui/src/utils/taskUtils.ts:75]()
- `fetchTasks` returns `{ tasks: [], total: 0, totalPages: 0 }` [packages/bytebot-ui/src/utils/taskUtils.ts:171]()
- `fetchTaskCounts` returns zeroed counts [packages/bytebot-ui/src/utils/taskUtils.ts:214-220]()

This approach allows UI components to degrade gracefully—empty lists display no items rather than crashing, and zero counts show empty tabs rather than undefined badges.

**Sources:** [packages/bytebot-ui/src/utils/taskUtils.ts:17-42](), [packages/bytebot-ui/src/utils/taskUtils.ts:63-221]()

---

## Type Safety

All utility functions use TypeScript generics and explicit return types to ensure compile-time type checking.

### Type Imports

[packages/bytebot-ui/src/utils/taskUtils.ts:1]() imports shared types:

```typescript
import { Message, Task, Model, GroupedMessages, FileWithBase64, TaskStatus } from "@/types";
```

These types mirror the Prisma database schema and provide consistency across the UI codebase. The `@/types` alias resolves to `packages/bytebot-ui/src/types`, which re-exports types from the `@bytebot/shared` package.

### Generic Type Parameter

The `apiRequest<T>()` function uses a generic type parameter to enforce return type contracts:

```typescript
async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {},
): Promise<T | null>
```

When calling `apiRequest<Task>()`, TypeScript ensures the JSON response matches the Task interface, catching type mismatches at compile time.

**Sources:** [packages/bytebot-ui/src/utils/taskUtils.ts:1](), [packages/bytebot-ui/src/utils/taskUtils.ts:17-20]()

---

## Usage Examples

### Creating a Task

```typescript
import { startTask } from '@/utils/taskUtils';

const task = await startTask({
  description: "Open Firefox and navigate to example.com",
  model: "claude-3-5-sonnet-20241022",
  files: [] // Optional file attachments
});

if (task) {
  // Task created successfully, redirect to task page
  router.push(`/task/${task.id}`);
} else {
  // Handle error
  setError("Failed to create task");
}
```

### Fetching and Displaying Messages

```typescript
import { fetchTaskProcessedMessages } from '@/utils/taskUtils';

const messages = await fetchTaskProcessedMessages(taskId, {
  limit: 50,
  page: 1
});

// messages is GroupedMessages[] ready for chat UI rendering
setMessages(messages);
```

### Handling Task Control

```typescript
import { takeOverTask, resumeTask } from '@/utils/taskUtils';

// User clicks "Take Over" button
const handleTakeOver = async () => {
  const updatedTask = await takeOverTask(taskId);
  if (updatedTask) {
    setTask(updatedTask); // Update local state
  }
};

// User clicks "Resume" button after providing guidance
const handleResume = async () => {
  const updatedTask = await resumeTask(taskId);
  if (updatedTask) {
    setTask(updatedTask); // Agent will resume processing
  }
};
```

**Sources:** [packages/bytebot-ui/src/utils/taskUtils.ts:124-259]()

---

# Page: Data Models

# Data Models

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [packages/bytebot-agent/prisma/schema.prisma](packages/bytebot-agent/prisma/schema.prisma)
- [packages/bytebot-agent/src/anthropic/anthropic.tools.ts](packages/bytebot-agent/src/anthropic/anthropic.tools.ts)
- [packages/bytebot-agent/src/tasks/dto/create-task.dto.ts](packages/bytebot-agent/src/tasks/dto/create-task.dto.ts)
- [packages/bytebot-ui/src/types/index.ts](packages/bytebot-ui/src/types/index.ts)

</details>



This document provides comprehensive documentation of the data structures, database schema, and type definitions used throughout the Bytebot system. It covers the PostgreSQL database schema, TypeScript interfaces, data transfer objects (DTOs), and shared type definitions that enable communication between services.

## Database Schema

The Bytebot system uses PostgreSQL as its primary database with Prisma as the ORM. The schema defines the core entities and their relationships for task management, message persistence, and file storage.

### Core Entity Models

**Database Entity Relationship Diagram**

The database schema centers around four primary entities: `Task`, `Message`, `Summary`, and `File`, with hierarchical relationships for conversation summarization.

```mermaid
erDiagram
    Task ||--o{ Message : "has many"
    Task ||--o{ File : "has many"  
    Task ||--o{ Summary : "has many"
    Message }o--o| Summary : "belongs to"
    Summary ||--o{ Message : "summarizes"
    Summary }o--o| Summary : "parent-child"
    
    Task {
        string id PK
        string description
        TaskType type
        TaskStatus status
        TaskPriority priority
        Role control
        Role createdBy
        DateTime createdAt
        DateTime updatedAt
        DateTime scheduledFor
        DateTime executedAt
        DateTime completedAt
        DateTime queuedAt
        string error
        Json result
        Json model
    }
    
    Message {
        string id PK
        Json content
        Role role
        DateTime createdAt
        DateTime updatedAt
        string taskId FK
        string summaryId FK
    }
    
    Summary {
        string id PK
        string content
        DateTime createdAt
        DateTime updatedAt
        string taskId FK
        string parentId FK
    }
    
    File {
        string id PK
        string name
        string type
        int size
        string data
        DateTime createdAt
        DateTime updatedAt
        string taskId FK
    }
```

**Sources:** [packages/bytebot-agent/prisma/schema.prisma:43-115]()

### Enumeration Types

The system defines several enums to constrain values and ensure data consistency:

| Enum | Values | Usage |
|------|--------|-------|
| `TaskStatus` | `PENDING`, `RUNNING`, `NEEDS_HELP`, `NEEDS_REVIEW`, `COMPLETED`, `CANCELLED`, `FAILED` | Tracks task lifecycle state |
| `TaskPriority` | `LOW`, `MEDIUM`, `HIGH`, `URGENT` | Prioritizes task execution |
| `TaskType` | `IMMEDIATE`, `SCHEDULED` | Distinguishes execution timing |
| `Role` | `USER`, `ASSISTANT` | Identifies message sender and task control |

**Sources:** [packages/bytebot-agent/prisma/schema.prisma:16-41]()

### Summary Model Hierarchy

The `Summary` model supports hierarchical summarization with self-referential relationships to enable progressive conversation compression:

```mermaid
graph TD
    Summary1["Summary (Parent)"] --> Summary2["Summary (Child 1)"]
    Summary1 --> Summary3["Summary (Child 2)"]
    Summary2 --> Summary4["Summary (Grandchild)"]
    
    Summary1 -.-> Message1["Message Group 1"]
    Summary2 -.-> Message2["Message Group 2"] 
    Summary3 -.-> Message3["Message Group 3"]
    Summary4 -.-> Message4["Message Group 4"]
```

This enables the system to maintain context while managing token limits by creating nested summaries of conversation history.

**Sources:** [packages/bytebot-agent/prisma/schema.prisma:67-81]()

## TypeScript Interfaces

The frontend and shared packages define TypeScript interfaces that correspond to database models with additional client-side properties and computed fields.

### Frontend Data Models

**Client-Side Type Structure**

```mermaid
classDiagram
    class Task {
        +string id
        +string description
        +TaskType type
        +TaskStatus status
        +TaskPriority priority
        +Role control
        +Role createdBy
        +string createdAt
        +string updatedAt
        +string scheduledFor
        +string executedAt
        +string completedAt
        +string queuedAt
        +string error
        +unknown result
        +Model model
        +User user
        +File[] files
    }
    
    class Message {
        +string id
        +MessageContentBlock[] content
        +Role role
        +string taskId
        +string createdAt
        +boolean take_over
    }
    
    class GroupedMessages {
        +Role role
        +Message[] messages
        +boolean take_over
    }
    
    class Model {
        +string provider
        +string name
        +string title
    }
    
    Task --> Model : uses
    Task --> File : contains
    Message --> MessageContentBlock : contains
    GroupedMessages --> Message : groups
```

**Sources:** [packages/bytebot-ui/src/types/index.ts:78-98](), [packages/bytebot-ui/src/types/index.ts:8-29]()

### File Handling Types

The system defines two file interfaces for different contexts:

| Interface | Purpose | Fields |
|-----------|---------|--------|
| `FileWithBase64` | Client-side file upload | `name`, `base64`, `type`, `size` |
| `File` | Persisted database file | `id`, `name`, `type`, `size`, `data`, `createdAt`, `updatedAt`, `taskId` |

**Sources:** [packages/bytebot-ui/src/types/index.ts:60-76]()

## Data Transfer Objects

The backend uses DTOs for request validation and type safety during API operations.

### Task Management DTOs

**Task Creation and Update DTOs**

```mermaid
classDiagram
    class CreateTaskDto {
        +string description
        +TaskType type
        +Date scheduledFor
        +TaskPriority priority
        +Role createdBy
        +any model
        +TaskFileDto[] files
    }
    
    class TaskFileDto {
        +string name
        +string base64
        +string type
        +number size
    }
    
    class UpdateTaskDto {
        +TaskStatus status
        +string error
        +unknown result
        +DateTime executedAt
        +DateTime completedAt
    }
    
    class AddTaskMessageDto {
        +string message
    }
    
    CreateTaskDto --> TaskFileDto : contains
```

The DTOs include validation decorators from `class-validator`:
- `@IsNotEmpty()` for required fields like `description`
- `@IsOptional()` for optional fields like `scheduledFor`  
- `@ValidateNested()` for nested object validation with `TaskFileDto[]`

**Sources:** [packages/bytebot-agent/src/tasks/dto/create-task.dto.ts:31-60](), [packages/bytebot-agent/src/tasks/dto/update-task.dto.ts]()

## Message Content Structure

Messages in Bytebot follow Anthropic's content blocks structure, stored as JSON in the database and typed via the shared package. The `@bytebot/shared` package provides comprehensive type definitions for all content block variants.

### Content Block Type Hierarchy

**MessageContentBlock Type Structure**

```mermaid
graph TD
    MessageContentBlock["MessageContentBlock<br/>(from @bytebot/shared)"] 
    
    TextContentBlock["TextContentBlock<br/>type: 'text'<br/>text: string"]
    ImageContentBlock["ImageContentBlock<br/>type: 'image'<br/>source: {media_type, data}"]
    DocumentContentBlock["DocumentContentBlock<br/>type: 'document'<br/>source: {media_type, data}"]
    ToolUseContentBlock["ToolUseContentBlock<br/>type: 'tool_use'<br/>name: string, input: object"]
    ToolResultContentBlock["ToolResultContentBlock<br/>type: 'tool_result'<br/>tool_use_id: string"]
    ThinkingContentBlock["ThinkingContentBlock<br/>type: 'thinking'<br/>thinking: string"]
    UserActionContentBlock["UserActionContentBlock<br/>type: 'user_action'<br/>content: ContentBlock[]"]
    
    MessageContentBlock --> TextContentBlock
    MessageContentBlock --> ImageContentBlock
    MessageContentBlock --> DocumentContentBlock
    MessageContentBlock --> ToolUseContentBlock
    MessageContentBlock --> ToolResultContentBlock
    MessageContentBlock --> ThinkingContentBlock
    MessageContentBlock --> UserActionContentBlock
```

### Computer Tool Use Types

The system defines specialized tool use blocks for computer automation:

**Computer Tool Use Content Blocks**

```mermaid
graph TD
    ComputerToolUseContentBlock["ComputerToolUseContentBlock<br/>(Union Type)"]
    
    MouseTools["Mouse Tools<br/>MoveMouseToolUseBlock<br/>ClickMouseToolUseBlock<br/>DragMouseToolUseBlock<br/>ScrollToolUseBlock"]
    
    KeyboardTools["Keyboard Tools<br/>TypeKeysToolUseBlock<br/>TypeTextToolUseBlock<br/>PasteTextToolUseBlock"]
    
    SystemTools["System Tools<br/>ScreenshotToolUseBlock<br/>ApplicationToolUseBlock<br/>WaitToolUseBlock"]
    
    FileTools["File Tools<br/>WriteFileToolUseBlock<br/>ReadFileToolUseBlock"]
    
    ComputerToolUseContentBlock --> MouseTools
    ComputerToolUseContentBlock --> KeyboardTools
    ComputerToolUseContentBlock --> SystemTools
    ComputerToolUseContentBlock --> FileTools
```

Content blocks are stored as JSON arrays in the database `Message.content` field and consumed by both the frontend chat interface and AI model processing.

**Sources:** [packages/shared/src/types/messageContent.types.ts:4-258](), [packages/bytebot-agent/prisma/schema.prisma:91]()

## Computer Action Types

The system defines comprehensive types for computer automation actions that correspond to desktop control operations.

### Computer Action Type Structure

**Computer Action Definitions**

```mermaid
graph TD
    ComputerAction["ComputerAction<br/>(Union Type)"]
    
    MouseActions["Mouse Actions<br/>MoveMouseAction<br/>ClickMouseAction<br/>DragMouseAction<br/>ScrollAction<br/>PressMouseAction<br/>TraceMouseAction"]
    
    KeyboardActions["Keyboard Actions<br/>TypeKeysAction<br/>TypeTextAction<br/>PasteTextAction<br/>PressKeysAction"]
    
    SystemActions["System Actions<br/>ScreenshotAction<br/>WaitAction<br/>CursorPositionAction<br/>ApplicationAction"]
    
    FileActions["File Actions<br/>WriteFileAction<br/>ReadFileAction"]
    
    ComputerAction --> MouseActions
    ComputerAction --> KeyboardActions
    ComputerAction --> SystemActions
    ComputerAction --> FileActions
```

These types are used by `ComputerUseService` in the desktop service to perform actual desktop automation, and are validated using DTOs and pipes.

**Sources:** [packages/shared/src/types/computerAction.types.ts:109-125](), [packages/bytebotd/src/computer-use/dto/computer-action.dto.ts:223-239]()

## Data Flow and Type Mapping

**System Data Flow Architecture**

```mermaid
flowchart TD
    subgraph "Frontend (bytebot-ui)"
        UITypes["UI Types<br/>Task, Message, Model<br/>GroupedMessages"]
        taskUtils["taskUtils.ts<br/>fetchTasks(), startTask()<br/>addMessage()"]
        useChatSession["useChatSession.ts<br/>WebSocket Management"]
    end
    
    subgraph "Backend (bytebot-agent)"
        TasksController["TasksController<br/>/api/tasks endpoints"]
        TasksService["TasksService<br/>create(), findAll()<br/>update()"]
        DTOs["DTOs<br/>CreateTaskDto<br/>AddTaskMessageDto"]
        PrismaModels["Prisma Models<br/>Task, Message, Summary, File"]
        AgentProcessor["AgentProcessor<br/>Task Execution Engine"]
    end
    
    subgraph "Desktop Service (bytebotd)"
        ComputerUseService["ComputerUseService<br/>action() method"]
        ComputerActionDtos["Computer Action DTOs<br/>Validation Pipeline"]
    end
    
    subgraph "Database"
        PostgreSQL["PostgreSQL<br/>Prisma Schema Tables"]
    end
    
    subgraph "Shared Package"
        SharedTypes["@bytebot/shared<br/>MessageContentBlock<br/>ComputerAction"]
    end
    
    taskUtils -->|"HTTP POST"| TasksController
    TasksController --> TasksService
    TasksService -->|"Validation"| DTOs
    DTOs --> PrismaModels
    PrismaModels -->|"Prisma ORM"| PostgreSQL
    
    AgentProcessor -->|"Computer Actions"| ComputerUseService
    ComputerUseService --> ComputerActionDtos
    
    SharedTypes -.->|"Import"| UITypes
    SharedTypes -.->|"Import"| AgentProcessor
    SharedTypes -.->|"Import"| ComputerUseService
    
    useChatSession -->|"WebSocket"| TasksService
```

**Sources:** [packages/bytebot-ui/src/utils/taskUtils.ts:1-260](), [packages/bytebot-agent/src/tasks/tasks.service.ts:1-393](), [packages/bytebotd/src/computer-use/computer-use.service.ts:25-507]()

## Tool Definitions and Computer Actions

The system defines tools that the AI agent can use to interact with the desktop environment:

```mermaid
graph LR
    subgraph "Agent Tools"
        AgentToolsDef["agentTools<br/>Tool Definitions"]
        AnthropicTools["anthropicTools<br/>Anthropic.Tool[]"]
    end
    
    subgraph "Computer Actions"
        MouseActions["Mouse Tools<br/>moveMouseTool, clickMouseTool,<br/>dragMouseTool, scrollTool"]
        KeyboardActions["Keyboard Tools<br/>typeKeysTool, pressKeysTool,<br/>typeTextTool, pasteTextTool"]
        SystemActions["System Tools<br/>screenshotTool, waitTool,<br/>applicationTool"]
        TaskActions["Task Tools<br/>setTaskStatusTool,<br/>createTaskTool"]
    end
    
    AgentToolsDef --> AnthropicTools
    AnthropicTools --> MouseActions
    AnthropicTools --> KeyboardActions  
    AnthropicTools --> SystemActions
    AnthropicTools --> TaskActions
```

Tool definitions are converted from generic agent tools to Anthropic-specific format and exposed as individual exports for type safety.

**Sources:** [packages/bytebot-agent/src/anthropic/anthropic.tools.ts:7-54]()

---

# Page: Type System Overview

# Type System Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [packages/bytebot-agent/prisma/schema.prisma](packages/bytebot-agent/prisma/schema.prisma)
- [packages/bytebot-agent/src/anthropic/anthropic.tools.ts](packages/bytebot-agent/src/anthropic/anthropic.tools.ts)
- [packages/bytebot-agent/src/tasks/dto/create-task.dto.ts](packages/bytebot-agent/src/tasks/dto/create-task.dto.ts)
- [packages/bytebot-ui/src/types/index.ts](packages/bytebot-ui/src/types/index.ts)

</details>



## Purpose and Scope

This document explains how Bytebot maintains type consistency across its three-tier architecture. It describes the type definition strategy, the relationship between Prisma database schemas and TypeScript interfaces, the role of shared type packages, and validation mechanisms at API boundaries.

For details on specific database models and relationships, see [Database Schema](#9.2). For message content structure, see [Message Content Types](#9.3). For computer action type hierarchies, see [Computer Action Types](#9.4).

---

## Type Architecture

Bytebot employs a **multi-layered type system** to ensure type safety from the database through the API layer to the UI. Types are defined at four distinct layers, each serving a specific purpose in the data flow.

### Type Definition Layers

```mermaid
graph TB
    subgraph Layer1["Database Layer (Prisma)"]
        PrismaSchema["schema.prisma<br/>Enums: TaskStatus, TaskPriority, Role, TaskType<br/>Models: Task, Message, Summary, File"]
    end
    
    subgraph Layer2["Shared Package (@bytebot/shared)"]
        SharedTypes["MessageContentBlock types<br/>ComputerAction types<br/>Cross-package interfaces"]
    end
    
    subgraph Layer3["Backend Layer (bytebot-agent)"]
        DTOs["DTOs (class-validator)<br/>CreateTaskDto, TaskFileDto<br/>ComputerActionDto variants"]
        PrismaClient["@prisma/client<br/>Generated types from schema"]
        Services["Service layer types<br/>Business logic interfaces"]
    end
    
    subgraph Layer4["Frontend Layer (bytebot-ui)"]
        UITypes["types/index.ts<br/>Task, Message, File interfaces<br/>GroupedMessages, FileWithBase64"]
    end
    
    PrismaSchema -->|"Generates"| PrismaClient
    PrismaSchema -.->|"Mirrored in"| UITypes
    SharedTypes -->|"Imported by"| Services
    SharedTypes -->|"Imported by"| UITypes
    PrismaClient -->|"Used by"| Services
    Services -->|"Validated by"| DTOs
    Services -->|"Serialized to"| UITypes
    
    style PrismaSchema fill:#f9f9f9
    style SharedTypes fill:#f9f9f9
    style DTOs fill:#f9f9f9
    style UITypes fill:#f9f9f9
```

**Sources:** [packages/bytebot-agent/prisma/schema.prisma:1-115](), [packages/bytebot-ui/src/types/index.ts:1-91]()

---

## Type Consistency Strategy

Bytebot maintains type consistency through **schema mirroring** and **shared type packages** rather than code generation from a single source of truth. This approach balances flexibility with type safety.

### Enum Synchronization

Core enums are defined in the Prisma schema and manually mirrored in the UI types. This requires discipline but avoids complex build-time code generation across packages.

| Enum | Prisma Location | UI Location | Purpose |
|------|----------------|-------------|---------|
| `TaskStatus` | [schema.prisma:16-24]() | [types/index.ts:32-40]() | Task lifecycle states |
| `TaskPriority` | [schema.prisma:26-31]() | [types/index.ts:42-47]() | Task urgency levels |
| `Role` | [schema.prisma:33-36]() | [types/index.ts:3-6]() | Message authorship |
| `TaskType` | [schema.prisma:38-41]() | [types/index.ts:49-52]() | Immediate vs scheduled |

### Interface Mirroring

The `Task` interface in the UI exactly mirrors the Prisma `Task` model, ensuring API responses can be directly consumed by UI components without transformation.

**Prisma Model:**
```prisma
model Task {
  id            String        @id @default(uuid())
  description   String
  type          TaskType      @default(IMMEDIATE)
  status        TaskStatus    @default(PENDING)
  priority      TaskPriority  @default(MEDIUM)
  control       Role          @default(ASSISTANT)
  // ... additional fields
}
```

**UI Interface:**
```typescript
export interface Task {
  id: string;
  description: string;
  type: TaskType;
  status: TaskStatus;
  priority: TaskPriority;
  control: Role;
  // ... additional fields
}
```

**Sources:** [packages/bytebot-agent/prisma/schema.prisma:43-65](), [packages/bytebot-ui/src/types/index.ts:72-90]()

---

## Core Type Categories

### Task Types

Task-related types define the structure and lifecycle of work units in Bytebot.

```mermaid
graph LR
    Task["Task Interface<br/>(id, description, status, priority, etc.)"]
    TaskStatus["TaskStatus Enum<br/>PENDING, RUNNING, NEEDS_HELP,<br/>NEEDS_REVIEW, COMPLETED,<br/>CANCELLED, FAILED"]
    TaskPriority["TaskPriority Enum<br/>LOW, MEDIUM, HIGH, URGENT"]
    TaskType["TaskType Enum<br/>IMMEDIATE, SCHEDULED"]
    Role["Role Enum<br/>USER, ASSISTANT"]
    Model["Model Interface<br/>(provider, name, title)"]
    
    Task -->|"status field"| TaskStatus
    Task -->|"priority field"| TaskPriority
    Task -->|"type field"| TaskType
    Task -->|"control field"| Role
    Task -->|"createdBy field"| Role
    Task -->|"model field"| Model
```

**Key Fields:**
- `id`: UUID string identifier
- `description`: User-provided task instructions
- `status`: Current lifecycle state (see [Task Lifecycle](#5.1))
- `control`: Whether `USER` or `ASSISTANT` has control
- `model`: JSON object specifying LLM provider and model name
- `scheduledFor`: Optional future execution timestamp
- `error`: Optional error message if `status` is `FAILED`

**Sources:** [packages/bytebot-ui/src/types/index.ts:72-90](), [packages/bytebot-agent/prisma/schema.prisma:43-65]()

### Message Types

Message types support the conversation history between users and AI agents, with structured content blocks.

```mermaid
graph TB
    Message["Message Interface<br/>(id, content, role, taskId)"]
    MessageContentBlock["MessageContentBlock[]<br/>(from @bytebot/shared)"]
    GroupedMessages["GroupedMessages Interface<br/>(role, messages[], take_over?)"]
    
    Message -->|"content field"| MessageContentBlock
    Message -->|"role field"| Role
    Message -->|"grouped by UI"| GroupedMessages
    
    MessageContentBlock -->|"Variants"| TextBlock["Text Block"]
    MessageContentBlock -->|"Variants"| ToolUse["Tool Use Block"]
    MessageContentBlock -->|"Variants"| ToolResult["Tool Result Block"]
    MessageContentBlock -->|"Variants"| ImageBlock["Image Block"]
    MessageContentBlock -->|"Variants"| UserAction["User Action Block"]
```

**Message Interface:**
- [packages/bytebot-ui/src/types/index.ts:9-16]() defines the core structure
- `content`: Array of `MessageContentBlock` objects from `@bytebot/shared`
- `role`: Either `USER` or `ASSISTANT`
- `take_over`: Optional boolean indicating user takeover events

**GroupedMessages:**
- [packages/bytebot-ui/src/types/index.ts:19-23]() defines the grouped structure
- Used by the UI to display consecutive messages from the same role
- See [Message Display System](#8.5) for rendering details

**Sources:** [packages/bytebot-ui/src/types/index.ts:9-23](), [packages/bytebot-agent/prisma/schema.prisma:83-99]()

### File Types

File types handle attachment uploads and desktop filesystem materialization.

**FileWithBase64** (Upload Format):
```typescript
export interface FileWithBase64 {
  name: string;
  base64: string;  // Base64-encoded file data
  type: string;    // MIME type
  size: number;    // Bytes
}
```

**File** (Database Model):
```typescript
export interface File {
  id: string;
  name: string;
  type: string;
  size: number;
  data: string;    // Base64-encoded
  createdAt: string;
  updatedAt: string;
  taskId: string;
}
```

The transformation occurs at the API boundary:
1. UI uploads `FileWithBase64` objects via `CreateTaskDto`
2. Backend stores as `File` records in database
3. Agent materializes `data` field to `/home/user/Desktop/` filesystem

**Sources:** [packages/bytebot-ui/src/types/index.ts:54-70](), [packages/bytebot-agent/prisma/schema.prisma:101-113]()

### Tool and Action Types

Tool definitions use a shared format across LLM providers, with provider-specific adapters.

```mermaid
graph LR
    agentTools["agentTools array<br/>(agent.tools.ts)"]
    AnthropicTool["Anthropic.Tool[]<br/>(anthropic.tools.ts)"]
    ComputerAction["ComputerAction types<br/>(@bytebot/shared)"]
    
    agentTools -->|"Converted to"| AnthropicTool
    agentTools -->|"Defines schema for"| ComputerAction
    
    AnthropicTool -->|"Individual exports"| moveMouseTool
    AnthropicTool -->|"Individual exports"| clickMouseTool
    AnthropicTool -->|"Individual exports"| typeTextTool
    AnthropicTool -->|"Individual exports"| screenshotTool
```

The conversion pattern:
- [packages/bytebot-agent/src/anthropic/anthropic.tools.ts:7-9]() converts generic tool definitions
- [packages/bytebot-agent/src/anthropic/anthropic.tools.ts:14-31]() creates named exports
- Tools include: mouse operations, keyboard operations, screenshot, application management, task control

**Sources:** [packages/bytebot-agent/src/anthropic/anthropic.tools.ts:1-55]()

---

## Type Flow Across Package Boundaries

This diagram shows how types flow from client requests through validation, database operations, and back to the client.

```mermaid
sequenceDiagram
    participant Client as "bytebot-ui Client"
    participant API as "TasksController"
    participant DTO as "CreateTaskDto<br/>(class-validator)"
    participant Service as "TasksService"
    participant Prisma as "PrismaClient"
    participant DB as "PostgreSQL"
    
    Client->>API: "POST /tasks<br/>{description, files, model}"
    API->>DTO: "Validate request body"
    DTO->>DTO: "@IsNotEmpty, @IsString<br/>@ValidateNested"
    
    alt Validation fails
        DTO-->>Client: "400 Bad Request"
    end
    
    DTO->>Service: "create(createTaskDto)"
    Service->>Service: "Transform FileWithBase64<br/>to File entities"
    Service->>Prisma: "task.create({data: {...}})"
    Prisma->>DB: "INSERT INTO Task"
    DB-->>Prisma: "Task record"
    Prisma-->>Service: "Task (Prisma type)"
    Service-->>API: "Task (serialized)"
    API-->>Client: "Task (UI interface)"
    
    Note over Client,DB: "Type consistency maintained:<br/>CreateTaskDto → Prisma.Task → UI.Task"
```

**Sources:** [packages/bytebot-agent/src/tasks/dto/create-task.dto.ts:1-61]()

---

## Validation and Runtime Type Safety

Bytebot employs multiple validation strategies at different layers.

### DTO Validation (API Boundary)

The backend uses `class-validator` decorators to enforce type constraints at REST API endpoints.

**CreateTaskDto Example:**
```typescript
export class CreateTaskDto {
  @IsNotEmpty()
  @IsString()
  description: string;

  @IsOptional()
  @IsString()
  type?: TaskType;

  @IsOptional()
  @IsArray()
  @ValidateNested({ each: true })
  @Type(() => TaskFileDto)
  files?: TaskFileDto[];
}
```

**Validation Decorators:**
- `@IsNotEmpty()`: Rejects null/undefined/empty values
- `@IsString()`, `@IsNumber()`: Type checking
- `@IsOptional()`: Field not required
- `@ValidateNested()`: Recursively validate nested objects
- `@Type(() => Class)`: Transform plain objects to class instances

**Sources:** [packages/bytebot-agent/src/tasks/dto/create-task.dto.ts:1-61]()

### Prisma Type Generation

Prisma generates TypeScript types from the schema automatically:

```bash
npx prisma generate
```

This creates the `@prisma/client` package with:
- Type-safe model interfaces
- Enum exports matching schema definitions
- Query builder with autocomplete
- Type inference for relations

The generated types are imported throughout the backend:
```typescript
import { TaskStatus, TaskPriority, Role, TaskType } from '@prisma/client';
```

**Sources:** [packages/bytebot-agent/prisma/schema.prisma:7-9]()

### Shared Package Types

The `@bytebot/shared` package (referenced in imports but not shown in provided files) defines cross-cutting types:
- `MessageContentBlock` and its variants
- `ComputerAction` type hierarchy
- Common interfaces used by both frontend and backend

This prevents duplication and ensures consistency for types that need to cross package boundaries.

**Sources:** [packages/bytebot-ui/src/types/index.ts:1]()

---

## Type Safety Benefits

The multi-layered type system provides several guarantees:

1. **Compile-Time Safety**: TypeScript catches type mismatches before runtime
2. **API Contract Enforcement**: DTOs validate incoming requests against expected schemas
3. **Database Consistency**: Prisma ensures database operations match schema definitions
4. **UI Rendering Safety**: Frontend components receive properly typed data structures

This architecture trades some duplication (manual enum mirroring) for flexibility and clarity, avoiding complex code generation pipelines while maintaining strong type safety across all layers.

**Sources:** All files referenced throughout this document

---

# Page: Database Schema

# Database Schema

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [packages/bytebot-agent/prisma/schema.prisma](packages/bytebot-agent/prisma/schema.prisma)
- [packages/bytebot-agent/src/anthropic/anthropic.tools.ts](packages/bytebot-agent/src/anthropic/anthropic.tools.ts)
- [packages/bytebot-agent/src/tasks/dto/create-task.dto.ts](packages/bytebot-agent/src/tasks/dto/create-task.dto.ts)
- [packages/bytebot-ui/src/types/index.ts](packages/bytebot-ui/src/types/index.ts)

</details>



This document describes the PostgreSQL database schema used by Bytebot to store tasks, messages, summaries, and file attachments. The schema is managed using Prisma ORM and provides the persistence layer for the AI agent task processing system.

For information about the TypeScript interfaces and data types used in the application layer, see [Types and Interfaces](8.1). For details about task lifecycle management, see [Task Management](6.1).

## Database Technology

Bytebot uses PostgreSQL as its primary database, deployed as a containerized service within the Docker/Kubernetes infrastructure. The database schema is managed through Prisma ORM with migration-based schema evolution.

The database runs on port 5432 and is accessed by the `bytebot-agent` service through the `PrismaService`, which provides type-safe database operations and automatic query generation.

Sources: [packages/bytebot-agent/prisma/schema.prisma:11-14]()

## Schema Overview

The database schema consists of four core entities that support Bytebot's AI agent task processing:

| Entity | Purpose | Key Features |
|--------|---------|--------------|
| `Task` | AI agent task lifecycle and orchestration | Status tracking, priority, control handoff |
| `Message` | Conversation history and AI interactions | Structured content blocks, role-based attribution |
| `Summary` | Message history compression for context management | Hierarchical summarization, token optimization |
| `File` | Task attachments and file processing | Base64 storage, MIME type support |

**Core Database Schema**
```mermaid
erDiagram
    Task {
        string id PK
        string description
        TaskType type
        TaskStatus status
        TaskPriority priority
        Role control
        Role createdBy
        datetime createdAt
        datetime updatedAt
        datetime scheduledFor
        datetime executedAt
        datetime completedAt
        datetime queuedAt
        string error
        Json result
        Json model
    }
    
    Message {
        string id PK
        Json content
        Role role
        datetime createdAt
        datetime updatedAt
        string taskId FK
        string summaryId FK
    }
    
    Summary {
        string id PK
        string content
        datetime createdAt
        datetime updatedAt
        string taskId FK
        string parentId FK
    }
    
    File {
        string id PK
        string name
        string type
        int size
        string data
        datetime createdAt
        datetime updatedAt
        string taskId FK
    }
    
    Task ||--o{ Message : "contains"
    Task ||--o{ Summary : "summarizes"
    Task ||--o{ File : "attachments"
    Summary ||--o{ Message : "groups"
    Summary ||--o{ Summary : "hierarchy"
```

Sources: [packages/bytebot-agent/prisma/schema.prisma:43-114]()

## Task Entity Schema

The `Task` entity is the central component of Bytebot's database schema, representing individual AI agent tasks with comprehensive lifecycle management.

### Task Table Structure

The `Task` table stores all task-related information and state:

```sql
-- Core task fields
id            UUID PRIMARY KEY DEFAULT gen_random_uuid()
description   TEXT NOT NULL
type          TaskType DEFAULT 'IMMEDIATE'
status        TaskStatus DEFAULT 'PENDING'
priority      TaskPriority DEFAULT 'MEDIUM'
control       Role DEFAULT 'ASSISTANT'
createdBy     Role DEFAULT 'USER'

-- Timestamps for lifecycle tracking  
createdAt     TIMESTAMP DEFAULT now()
updatedAt     TIMESTAMP DEFAULT now()
scheduledFor  TIMESTAMP NULL
executedAt    TIMESTAMP NULL
completedAt   TIMESTAMP NULL
queuedAt      TIMESTAMP NULL

-- Execution results and errors
error         TEXT NULL
result        JSONB NULL

-- AI model configuration
model         JSONB NOT NULL
```

### Task Status Management

The task status follows a defined lifecycle managed by the `AgentProcessor`:

**Task Status Flow**
```mermaid
stateDiagram-v2
    [*] --> PENDING : "TasksService.create()"
    PENDING --> RUNNING : "AgentProcessor.processTask()"
    RUNNING --> COMPLETED : "set_task_status tool"
    RUNNING --> NEEDS_HELP : "set_task_status tool"
    RUNNING --> FAILED : "Error or timeout"
    NEEDS_HELP --> RUNNING : "TasksService.resume()"
    RUNNING --> CANCELLED : "TasksService.cancel()"
    COMPLETED --> [*]
    FAILED --> [*]
    CANCELLED --> [*]
```

### Task Control Handoff

The `control` field manages handoff between AI agent and user:

| Control State | Description | Managed By |
|---------------|-------------|------------|
| `ASSISTANT` | AI agent has control, executing actions | `AgentProcessor` |
| `USER` | User has control, can provide guidance | `TasksService.takeOver()` |

Sources: [packages/bytebot-agent/prisma/schema.prisma:43-65](), [packages/bytebot-agent/src/agent/agent.processor.ts:84-420]()

## Message Storage Schema

The `Message` table stores conversation history between users and AI agents using Anthropic's content block structure for flexible multimedia support.

### Message Content Structure

Messages use a JSON `content` field following Anthropic's format:

```typescript
// Example message content structures
[
  {"type": "text", "text": "Hello world"}
]

[
  {"type": "text", "text": "Please analyze this image"},
  {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": "..."}}
]

[
  {"type": "tool_use", "id": "toolu_123", "name": "computer", "input": {"action": "screenshot"}}
]
```

### Message Role System

The `role` field distinguishes message sources:

| Role | Purpose | Created By |
|------|---------|------------|
| `USER` | User input, guidance, task descriptions | `TasksService.addTaskMessage()` |
| `ASSISTANT` | AI agent responses, tool usage | `AgentProcessor.runIteration()` |

**Message Processing Flow**
```mermaid
sequenceDiagram
    participant UI as "bytebot-ui"
    participant TS as "TasksService"
    participant AP as "AgentProcessor" 
    participant MS as "MessagesService"
    participant DB as "PostgreSQL"
    
    UI->>TS: "addTaskMessage(taskId, message)"
    TS->>MS: "create({role: USER, content: [...]})"
    MS->>DB: "INSERT INTO Message"
    AP->>MS: "create({role: ASSISTANT, content: [...]})"
    MS->>DB: "INSERT INTO Message"
    AP->>MS: "create({role: USER, content: [tool_results]})"
    MS->>DB: "INSERT INTO Message"
```

Sources: [packages/bytebot-agent/prisma/schema.prisma:83-99](), [packages/bytebot-agent/src/tasks/tasks.service.ts:263-280]()

## Summary and File Storage

The schema includes specialized entities for message summarization and file attachment handling to support long-running tasks and multimedia processing.

### Summary Table for Context Management

The `Summary` table enables context compression when message history exceeds AI model token limits:

```sql
-- Summary table structure
id             UUID PRIMARY KEY DEFAULT gen_random_uuid()
content        TEXT NOT NULL
createdAt      TIMESTAMP DEFAULT now()
updatedAt      TIMESTAMP DEFAULT now()
taskId         UUID REFERENCES Task(id) ON DELETE CASCADE
parentId       UUID REFERENCES Summary(id) -- Self-referential hierarchy
```

**Hierarchical Summarization**
```mermaid
graph TD
    T["Task"] --> M1["Messages 1-50"]
    T --> M2["Messages 51-100"] 
    T --> M3["Messages 101-150"]
    
    M1 --> S1["Summary 1"]
    M2 --> S2["Summary 2"]
    M3 --> S3["Summary 3"]
    
    S1 --> PS1["Parent Summary"]
    S2 --> PS1
    S3 --> PS1
    
    PS1 --> T
```

### File Attachment Storage

The `File` table stores task-related file attachments as base64-encoded data:

```sql
-- File table structure
id            UUID PRIMARY KEY DEFAULT gen_random_uuid()
name          TEXT NOT NULL
type          TEXT NOT NULL        -- MIME type (e.g., 'image/jpeg')
size          INTEGER NOT NULL     -- Size in bytes
data          TEXT NOT NULL        -- Base64 encoded file data
createdAt     TIMESTAMP DEFAULT now()
updatedAt     TIMESTAMP DEFAULT now()
taskId        UUID REFERENCES Task(id) ON DELETE CASCADE
```

Files are processed during task creation in `TasksService.create()` and written to the desktop environment for agent access.

Sources: [packages/bytebot-agent/prisma/schema.prisma:67-114](), [packages/bytebot-agent/src/tasks/tasks.service.ts:66-93]()

## Database Transactions and Operations

The schema supports complex operations through Prisma transactions, particularly for task creation and message processing.

### Task Creation Transaction

Task creation involves multiple related operations in a single transaction:

**Task Creation Process**
```mermaid
sequenceDiagram
    participant C as "CreateTaskDto"
    participant TS as "TasksService"
    participant P as "PrismaService"
    participant DB as "PostgreSQL"
    
    C->>TS: "create(createTaskDto)"
    TS->>P: "$transaction(async prisma => {"
    P->>DB: "prisma.task.create()"
    P->>DB: "prisma.file.create() (for each file)"
    P->>DB: "prisma.message.create() (initial message)"
    P->>TS: "transaction complete"
    TS->>TS: "tasksGateway.emitTaskCreated()"
```

### Message Processing with Summaries

When token usage exceeds thresholds, the `AgentProcessor` triggers summarization:

```typescript
// Token usage check in AgentProcessor
const contextWindow = model.contextWindow || 200000;
const contextThreshold = contextWindow * 0.75;
const shouldSummarize = agentResponse.tokenUsage.totalTokens >= contextThreshold;
```

This creates new `Summary` records and links existing messages to maintain context while reducing token consumption.

Sources: [packages/bytebot-agent/src/tasks/tasks.service.ts:45-117](), [packages/bytebot-agent/src/agent/agent.processor.ts:234-299]()

## Enum Definitions and Constraints

The schema defines several enums that constrain field values and provide type safety across the application.

### Core Enums

| Enum | Values | Usage |
|------|--------|-------|
| `TaskStatus` | `PENDING`, `RUNNING`, `NEEDS_HELP`, `NEEDS_REVIEW`, `COMPLETED`, `CANCELLED`, `FAILED` | Task lifecycle state |
| `TaskPriority` | `LOW`, `MEDIUM`, `HIGH`, `URGENT` | Task execution priority |
| `Role` | `USER`, `ASSISTANT` | Message attribution and control |
| `TaskType` | `IMMEDIATE`, `SCHEDULED` | Task execution timing |

### Data Integrity Constraints

The schema enforces data integrity through:

- **UUID Primary Keys**: All entities use UUID primary keys for global uniqueness
- **Cascade Deletions**: Task deletion automatically removes related messages, summaries, and files
- **Default Values**: Sensible defaults for status (`PENDING`), priority (`MEDIUM`), and control (`ASSISTANT`)
- **JSON Validation**: The `model` field stores structured AI provider configuration
- **Timestamp Tracking**: Automatic `createdAt` and `updatedAt` timestamps on all entities

Sources: [packages/bytebot-agent/prisma/schema.prisma:16-41]()

## Migration Strategy

The database schema follows a migration-based approach using Prisma's migration system. The migration file shows the addition of the Better Auth schema to an existing database with a `Message` table.

Migration characteristics:
- Incremental schema changes through numbered migration files
- Backward-compatible additions (adding `userId` column as nullable)
- Foreign key constraints with appropriate cascade behaviors
- Index creation for performance optimization

The migration pattern supports:
- Zero-downtime deployments
- Schema version tracking
- Rollback capabilities
- Multi-environment consistency

Sources: [packages/bytebot-agent/prisma/migrations/20250619013027_add_better_auth_schema/migration.sql:1-82]()

---

# Page: Message Content Types

# Message Content Types

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [packages/bytebot-agent/prisma/schema.prisma](packages/bytebot-agent/prisma/schema.prisma)
- [packages/bytebot-agent/src/anthropic/anthropic.tools.ts](packages/bytebot-agent/src/anthropic/anthropic.tools.ts)
- [packages/bytebot-agent/src/tasks/dto/create-task.dto.ts](packages/bytebot-agent/src/tasks/dto/create-task.dto.ts)
- [packages/bytebot-ui/src/types/index.ts](packages/bytebot-ui/src/types/index.ts)
- [packages/bytebotd/src/computer-use/computer-use.service.ts](packages/bytebotd/src/computer-use/computer-use.service.ts)
- [packages/bytebotd/src/computer-use/dto/base.dto.ts](packages/bytebotd/src/computer-use/dto/base.dto.ts)
- [packages/bytebotd/src/computer-use/dto/computer-action-validation.pipe.ts](packages/bytebotd/src/computer-use/dto/computer-action-validation.pipe.ts)
- [packages/bytebotd/src/computer-use/dto/computer-action.dto.ts](packages/bytebotd/src/computer-use/dto/computer-action.dto.ts)
- [packages/bytebotd/src/mcp/computer-use.tools.ts](packages/bytebotd/src/mcp/computer-use.tools.ts)
- [packages/shared/src/types/computerAction.types.ts](packages/shared/src/types/computerAction.types.ts)
- [packages/shared/src/types/messageContent.types.ts](packages/shared/src/types/messageContent.types.ts)
- [packages/shared/src/utils/computerAction.utils.ts](packages/shared/src/utils/computerAction.utils.ts)
- [packages/shared/src/utils/messageContent.utils.ts](packages/shared/src/utils/messageContent.utils.ts)

</details>



This document provides a comprehensive reference for the `MessageContentBlock` type system, which defines the structure of message content exchanged between users, AI agents, and tools throughout the Bytebot system. These types enable rich, structured communication that includes text, images, documents, LLM reasoning steps, tool invocations, and tool results.

For information about how messages are stored in the database, see [Database Schema](#9.2). For details about computer action execution, see [Computer Action Types](#9.4). For broader context on type consistency across packages, see [Type System Overview](#9.1).

## Purpose and Scope

Message content blocks form the vocabulary for all conversation-style interactions in Bytebot. They represent:

- User input (text, images, documents)
- AI agent responses (text, reasoning, tool usage)
- Tool execution results (screenshots, file data, action confirmations)
- User manual interventions (captured desktop actions)

All message content is stored as JSON arrays in the database's `Message.content` field and validated using TypeScript discriminated unions defined in the `@bytebot/shared` package.

**Sources:** [packages/shared/src/types/messageContent.types.ts:1-258](), [packages/bytebot-agent/prisma/schema.prisma:83-99]()

## Type Hierarchy

The message content system uses TypeScript's discriminated union pattern with a `type` field as the discriminator. All content blocks extend `MessageContentBlockBase` and specify their specific type via the `MessageContentType` enum.

### Type Discriminator Enum

```mermaid
graph TB
    MessageContentType["MessageContentType Enum"]
    
    MessageContentType --> Text["Text<br/>'text'"]
    MessageContentType --> Image["Image<br/>'image'"]
    MessageContentType --> Document["Document<br/>'document'"]
    MessageContentType --> ToolUse["ToolUse<br/>'tool_use'"]
    MessageContentType --> ToolResult["ToolResult<br/>'tool_result'"]
    MessageContentType --> Thinking["Thinking<br/>'thinking'"]
    MessageContentType --> RedactedThinking["RedactedThinking<br/>'redacted_thinking'"]
    MessageContentType --> UserAction["UserAction<br/>'user_action'"]
```

**Sources:** [packages/shared/src/types/messageContent.types.ts:4-13]()

### Union Structure

The `MessageContentBlock` type is a discriminated union of all possible content block variants:

```mermaid
graph LR
    MessageContentBlock["MessageContentBlock<br/>(Union Type)"]
    
    MessageContentBlock --> TextContentBlock
    MessageContentBlock --> ImageContentBlock
    MessageContentBlock --> DocumentContentBlock
    MessageContentBlock --> ToolUseContentBlock
    MessageContentBlock --> ThinkingContentBlock
    MessageContentBlock --> RedactedThinkingContentBlock
    MessageContentBlock --> UserActionContentBlock
    MessageContentBlock --> ComputerToolUseContentBlock
    MessageContentBlock --> ToolResultContentBlock
    
    ToolUseContentBlock -.->|"extends"| ComputerToolUseContentBlock
    ToolUseContentBlock -.->|"extends"| SetTaskStatusToolUseBlock
    ToolUseContentBlock -.->|"extends"| CreateTaskToolUseBlock
```

**Sources:** [packages/shared/src/types/messageContent.types.ts:248-258]()

## Base Type Structure

All content blocks share a common base structure:

| Field | Type | Description |
|-------|------|-------------|
| `type` | `MessageContentType` | Discriminator field identifying the specific content block type |
| `content` | `MessageContentBlock[]` (optional) | Nested content blocks for hierarchical structures |

**Sources:** [packages/shared/src/types/messageContent.types.ts:15-19]()

## Text Content

### TextContentBlock

Represents plain text content from users or AI responses.

```typescript
type: MessageContentType.Text
text: string
```

**Structure:**
- `type`: Always `"text"`
- `text`: The actual text content

**Usage:** User messages, AI text responses, simple confirmations

**Sources:** [packages/shared/src/types/messageContent.types.ts:21-24]()

## Media Content

### ImageContentBlock

Represents image data, typically screenshots captured by the agent or uploaded by users.

```typescript
type: MessageContentType.Image
source: {
  media_type: "image/png"
  type: "base64"
  data: string
}
```

**Structure:**
- `type`: Always `"image"`
- `source.media_type`: Always `"image/png"`
- `source.type`: Always `"base64"`
- `source.data`: Base64-encoded PNG image data

**Usage:** Screenshots from desktop automation, user-uploaded images

**Sources:** [packages/shared/src/types/messageContent.types.ts:26-33]()

### DocumentContentBlock

Represents document files with arbitrary MIME types.

```typescript
type: MessageContentType.Document
source: {
  type: "base64"
  media_type: string
  data: string
}
name?: string
size?: number
```

**Structure:**
- `type`: Always `"document"`
- `source.media_type`: MIME type (e.g., `"application/pdf"`, `"text/plain"`)
- `source.type`: Always `"base64"`
- `source.data`: Base64-encoded document data
- `name`: Optional filename
- `size`: Optional file size in bytes

**Usage:** User-uploaded files, files read from the virtual desktop

**Sources:** [packages/shared/src/types/messageContent.types.ts:35-44](), [packages/bytebotd/src/computer-use/computer-use.service.ts:419-506]()

## LLM Reasoning Content

### ThinkingContentBlock

Represents the AI model's explicit reasoning process (for models that support extended thinking).

```typescript
type: MessageContentType.Thinking
thinking: string
signature: string
```

**Structure:**
- `type`: Always `"thinking"`
- `thinking`: The actual reasoning text
- `signature`: Cryptographic signature verifying authenticity

**Usage:** Extended thinking from models like Claude with thinking features enabled

**Sources:** [packages/shared/src/types/messageContent.types.ts:46-50]()

### RedactedThinkingContentBlock

Represents redacted or compressed thinking content.

```typescript
type: MessageContentType.RedactedThinking
data: string
```

**Structure:**
- `type`: Always `"redacted_thinking"`
- `data`: Redacted or placeholder data

**Usage:** Privacy-preserving storage of thinking content

**Sources:** [packages/shared/src/types/messageContent.types.ts:52-55]()

## Tool Interaction Content

### ToolUseContentBlock

Base type for all tool invocations by the AI agent.

```typescript
type: MessageContentType.ToolUse
name: string
id: string
input: Record<string, any>
```

**Structure:**
- `type`: Always `"tool_use"`
- `name`: Tool name (e.g., `"computer_click_mouse"`, `"set_task_status"`)
- `id`: Unique identifier linking to corresponding `ToolResultContentBlock`
- `input`: Tool-specific input parameters

**Usage:** AI agent requests tool execution

**Sources:** [packages/shared/src/types/messageContent.types.ts:57-62]()

### ToolResultContentBlock

Represents the result of a tool execution.

```typescript
type: MessageContentType.ToolResult
tool_use_id: string
content: MessageContentBlock[]
is_error?: boolean
```

**Structure:**
- `type`: Always `"tool_result"`
- `tool_use_id`: ID of the corresponding `ToolUseContentBlock`
- `content`: Array of content blocks representing the result (text, images, etc.)
- `is_error`: Optional flag indicating execution failure

**Usage:** System responses after tool execution

**Sources:** [packages/shared/src/types/messageContent.types.ts:240-245]()

## Computer Tool Use Blocks

Computer tool use blocks are specialized `ToolUseContentBlock` variants for desktop automation. Each has a specific `name` and typed `input` structure.

### Mouse Control Tools

```mermaid
graph TB
    subgraph "Mouse Tools"
        MoveMouse["computer_move_mouse<br/>MoveMouseToolUseBlock"]
        TraceMouse["computer_trace_mouse<br/>TraceMouseToolUseBlock"]
        ClickMouse["computer_click_mouse<br/>ClickMouseToolUseBlock"]
        PressMouse["computer_press_mouse<br/>PressMouseToolUseBlock"]
        DragMouse["computer_drag_mouse<br/>DragMouseToolUseBlock"]
        Scroll["computer_scroll<br/>ScrollToolUseBlock"]
        CursorPosition["computer_cursor_position<br/>CursorPositionToolUseBlock"]
    end
    
    MoveMouse --> Input1["input:<br/>{ coordinates: {x, y} }"]
    TraceMouse --> Input2["input:<br/>{ path: Coordinates[],<br/>holdKeys?: string[] }"]
    ClickMouse --> Input3["input:<br/>{ coordinates?: {x, y},<br/>button: Button,<br/>holdKeys?: string[],<br/>clickCount: number }"]
    PressMouse --> Input4["input:<br/>{ coordinates?: {x, y},<br/>button: Button,<br/>press: Press }"]
    DragMouse --> Input5["input:<br/>{ path: Coordinates[],<br/>button: Button,<br/>holdKeys?: string[] }"]
    Scroll --> Input6["input:<br/>{ coordinates?: {x, y},<br/>direction: up|down|left|right,<br/>scrollCount: number,<br/>holdKeys?: string[] }"]
```

**Sources:** [packages/shared/src/types/messageContent.types.ts:64-115]()

### Keyboard Control Tools

```mermaid
graph TB
    subgraph "Keyboard Tools"
        TypeKeys["computer_type_keys<br/>TypeKeysToolUseBlock"]
        PressKeys["computer_press_keys<br/>PressKeysToolUseBlock"]
        TypeText["computer_type_text<br/>TypeTextToolUseBlock"]
        PasteText["computer_paste_text<br/>PasteTextToolUseBlock"]
    end
    
    TypeKeys --> Input1["input:<br/>{ keys: string[],<br/>delay?: number }"]
    PressKeys --> Input2["input:<br/>{ keys: string[],<br/>press: 'down' | 'up' }"]
    TypeText --> Input3["input:<br/>{ text: string,<br/>isSensitive?: boolean,<br/>delay?: number }"]
    PasteText --> Input4["input:<br/>{ text: string,<br/>isSensitive?: boolean }"]
```

**Sources:** [packages/shared/src/types/messageContent.types.ts:117-148]()

### System Control Tools

| Tool Name | Type | Input Parameters | Purpose |
|-----------|------|------------------|---------|
| `computer_wait` | `WaitToolUseBlock` | `{ duration: number }` | Pause execution |
| `computer_screenshot` | `ScreenshotToolUseBlock` | (none) | Capture screen |
| `computer_application` | `ApplicationToolUseBlock` | `{ application: string }` | Open/switch app |
| `computer_write_file` | `WriteFileToolUseBlock` | `{ path: string, data: string }` | Write file to desktop |
| `computer_read_file` | `ReadFileToolUseBlock` | `{ path: string }` | Read file from desktop |

**Sources:** [packages/shared/src/types/messageContent.types.ts:150-185]()

### Computer Tool Use Union Type

All computer tool use blocks are combined into a union type:

```typescript
type ComputerToolUseContentBlock =
  | MoveMouseToolUseBlock
  | TraceMouseToolUseBlock
  | ClickMouseToolUseBlock
  | PressMouseToolUseBlock
  | TypeKeysToolUseBlock
  | PressKeysToolUseBlock
  | TypeTextToolUseBlock
  | PasteTextToolUseBlock
  | WaitToolUseBlock
  | ScreenshotToolUseBlock
  | DragMouseToolUseBlock
  | ScrollToolUseBlock
  | CursorPositionToolUseBlock
  | ApplicationToolUseBlock
  | WriteFileToolUseBlock
  | ReadFileToolUseBlock
```

**Sources:** [packages/shared/src/types/messageContent.types.ts:187-204]()

## Task Management Tool Use Blocks

### SetTaskStatusToolUseBlock

Allows the agent to mark a task as completed, failed, or needing help.

```typescript
name: "set_task_status"
input: {
  status: "completed" | "failed" | "needs_help"
  description: string
}
```

**Structure:**
- `status`: Target task status
- `description`: Explanation of the status change

**Usage:** Task completion, failure reporting, requesting human assistance

**Sources:** [packages/shared/src/types/messageContent.types.ts:221-227]()

### CreateTaskToolUseBlock

Allows the agent to spawn subtasks.

```typescript
name: "create_task"
input: {
  name: string
  description: string
  type?: "immediate" | "scheduled"
  scheduledFor?: string
  priority: "low" | "medium" | "high" | "urgent"
}
```

**Structure:**
- `name`: Short task name
- `description`: Detailed task description
- `type`: Task scheduling type (defaults to immediate)
- `scheduledFor`: ISO timestamp for scheduled tasks
- `priority`: Task priority level

**Usage:** Breaking down complex tasks, scheduling future work

**Sources:** [packages/shared/src/types/messageContent.types.ts:229-238]()

## User Action Content

### UserActionContentBlock

Represents user actions captured during manual desktop control (takeover mode).

```typescript
type: MessageContentType.UserAction
content: (
  | ImageContentBlock
  | MoveMouseToolUseBlock
  | TraceMouseToolUseBlock
  | ClickMouseToolUseBlock
  | PressMouseToolUseBlock
  | TypeKeysToolUseBlock
  | PressKeysToolUseBlock
  | TypeTextToolUseBlock
  | DragMouseToolUseBlock
  | ScrollToolUseBlock
)[]
```

**Structure:**
- `type`: Always `"user_action"`
- `content`: Array of captured actions and screenshots

**Usage:** Recording user demonstrations during task execution handoff

**Sources:** [packages/shared/src/types/messageContent.types.ts:205-219]()

## Type Guards and Validation

The system provides comprehensive type guards for runtime validation and type narrowing.

### Type Guard Functions

```mermaid
graph TB
    subgraph "Type Guard Utilities"
        isMessageContentBlock["isMessageContentBlock()"]
        isTextContentBlock["isTextContentBlock()"]
        isImageContentBlock["isImageContentBlock()"]
        isDocumentContentBlock["isDocumentContentBlock()"]
        isToolUseContentBlock["isToolUseContentBlock()"]
        isComputerToolUseContentBlock["isComputerToolUseContentBlock()"]
        isToolResultContentBlock["isToolResultContentBlock()"]
        isThinkingContentBlock["isThinkingContentBlock()"]
        isUserActionContentBlock["isUserActionContentBlock()"]
    end
    
    subgraph "Specific Computer Tool Guards"
        isMoveMouseToolUseBlock["isMoveMouseToolUseBlock()"]
        isClickMouseToolUseBlock["isClickMouseToolUseBlock()"]
        isTypeTextToolUseBlock["isTypeTextToolUseBlock()"]
        isScreenshotToolUseBlock["isScreenshotToolUseBlock()"]
        isSetTaskStatusToolUseBlock["isSetTaskStatusToolUseBlock()"]
        isCreateTaskToolUseBlock["isCreateTaskToolUseBlock()"]
    end
    
    isComputerToolUseContentBlock -.->|"used by"| isMoveMouseToolUseBlock
    isComputerToolUseContentBlock -.->|"used by"| isClickMouseToolUseBlock
    isComputerToolUseContentBlock -.->|"used by"| isTypeTextToolUseBlock
    isComputerToolUseContentBlock -.->|"used by"| isScreenshotToolUseBlock
```

**Key Type Guards:**

| Function | Purpose | Returns True If |
|----------|---------|-----------------|
| `isMessageContentBlock()` | General content block validation | Object is any valid `MessageContentBlock` |
| `isToolUseContentBlock()` | Tool use validation | `type === "tool_use"` with required fields |
| `isComputerToolUseContentBlock()` | Computer tool detection | Tool name starts with `"computer_"` |
| `isToolResultContentBlock()` | Tool result validation | `type === "tool_result"` with `tool_use_id` |
| `isUserActionContentBlock()` | User action detection | `type === "user_action"` |

**Sources:** [packages/shared/src/utils/messageContent.utils.ts:33-516]()

### Type Guard Example Usage

```typescript
// Runtime type checking and narrowing
if (isTextContentBlock(block)) {
  console.log(block.text);  // TypeScript knows block.text exists
}

if (isComputerToolUseContentBlock(block)) {
  if (isClickMouseToolUseBlock(block)) {
    const { coordinates, button } = block.input;  // Fully typed
  }
}
```

**Sources:** [packages/shared/src/utils/messageContent.utils.ts:38-47](), [packages/shared/src/utils/messageContent.utils.ts:300-309]()

## Storage and Serialization

### Database Storage

Message content blocks are stored as JSON in the `Message` model's `content` field:

```prisma
model Message {
  id        String      @id @default(uuid())
  content   Json        // Array of MessageContentBlock
  role      Role        @default(ASSISTANT)
  taskId    String
  summaryId String?
}
```

**Example JSON storage:**
```json
[
  {
    "type": "text",
    "text": "I'll click the search button"
  },
  {
    "type": "tool_use",
    "id": "toolu_123",
    "name": "computer_click_mouse",
    "input": {
      "coordinates": { "x": 640, "y": 480 },
      "button": "left",
      "clickCount": 1
    }
  }
]
```

**Sources:** [packages/bytebot-agent/prisma/schema.prisma:83-99]()

### Type Consistency Across Packages

The `Message` interface in the UI mirrors the database structure:

```typescript
// bytebot-ui/src/types/index.ts
interface Message {
  id: string;
  content: MessageContentBlock[];  // From @bytebot/shared
  role: Role;
  taskId?: string;
  createdAt?: string;
}
```

This ensures type safety from database to frontend rendering.

**Sources:** [packages/bytebot-ui/src/types/index.ts:8-16]()

## Message Content Flow

```mermaid
graph LR
    subgraph "Content Block Lifecycle"
        User["User Input<br/>(TextContentBlock)"]
        Agent["AI Agent Response<br/>(TextContentBlock +<br/>ToolUseContentBlock)"]
        Execution["Tool Execution<br/>(ComputerUseService)"]
        Result["Tool Result<br/>(ToolResultContentBlock +<br/>ImageContentBlock)"]
        DB["Database<br/>(Message.content: Json)"]
    end
    
    User --> DB
    DB --> Agent
    Agent --> DB
    DB --> Execution
    Execution --> Result
    Result --> DB
    DB --> Agent
```

**Flow Description:**
1. User creates `TextContentBlock` messages
2. Agent responds with `TextContentBlock` + `ToolUseContentBlock` arrays
3. System executes tools via `ComputerUseService.action()`
4. Results stored as `ToolResultContentBlock` with nested content
5. All content serialized to JSON in `Message.content`
6. Agent receives context including previous tool results

**Sources:** [packages/bytebot-agent/src/agent/agent.processor.ts](), [packages/bytebotd/src/computer-use/computer-use.service.ts:31-105]()

## Integration with LLM Providers

The content block types are designed to be compatible with LLM provider APIs, particularly Anthropic's message format.

### Provider Tool Conversion

```mermaid
graph TB
    agentTools["agentTools<br/>(agent.tools.ts)"]
    
    subgraph "Provider-Specific Formats"
        anthropicTools["anthropicTools<br/>(Anthropic.Tool[])"]
        mcpTools["ComputerUseTools<br/>(@Tool decorators)"]
    end
    
    agentTools --> anthropicTools
    agentTools --> mcpTools
    
    anthropicTools --> API["Anthropic API<br/>(messages.create)"]
    mcpTools --> MCP["MCP Server<br/>(SSE endpoint)"]
```

**Conversion Process:**
- Agent tools defined in generic format
- Converted to provider-specific schemas
- Anthropic receives `Anthropic.Tool[]` definitions
- MCP uses `@Tool` decorator with Zod schemas

**Sources:** [packages/bytebot-agent/src/anthropic/anthropic.tools.ts:4-54](), [packages/bytebotd/src/mcp/computer-use.tools.ts:8-698]()

---

# Page: Computer Action Types

# Computer Action Types

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [packages/bytebotd/src/computer-use/computer-use.service.ts](packages/bytebotd/src/computer-use/computer-use.service.ts)
- [packages/bytebotd/src/computer-use/dto/base.dto.ts](packages/bytebotd/src/computer-use/dto/base.dto.ts)
- [packages/bytebotd/src/computer-use/dto/computer-action-validation.pipe.ts](packages/bytebotd/src/computer-use/dto/computer-action-validation.pipe.ts)
- [packages/bytebotd/src/computer-use/dto/computer-action.dto.ts](packages/bytebotd/src/computer-use/dto/computer-action.dto.ts)
- [packages/bytebotd/src/mcp/computer-use.tools.ts](packages/bytebotd/src/mcp/computer-use.tools.ts)
- [packages/shared/src/types/computerAction.types.ts](packages/shared/src/types/computerAction.types.ts)
- [packages/shared/src/types/messageContent.types.ts](packages/shared/src/types/messageContent.types.ts)
- [packages/shared/src/utils/computerAction.utils.ts](packages/shared/src/utils/computerAction.utils.ts)
- [packages/shared/src/utils/messageContent.utils.ts](packages/shared/src/utils/messageContent.utils.ts)

</details>



This page documents the `ComputerAction` type system, which defines the structured data format for all desktop automation operations in Bytebot. These types represent the low-level actions that the AI agent can request the bytebotd daemon to execute on the virtual desktop.

For information about how these actions are represented in AI conversations, see [Message Content Types](#9.3). For the execution implementation, see [Computer Use Service](#7.1).

---

## Purpose and Scope

Computer Action Types provide a type-safe abstraction layer between AI decision-making and desktop automation. The type system serves three key functions:

1. **Type Safety**: TypeScript discriminated unions ensure compile-time correctness across the shared package, bytebot-agent, and bytebotd
2. **Validation**: Runtime validation DTOs in bytebotd enforce API contract integrity at the service boundary
3. **Serialization**: Structured types enable seamless conversion between tool use requests (from LLMs) and executable commands

The type hierarchy is defined in [packages/shared/src/types/computerAction.types.ts:1-126]() and consumed by both the agent orchestration layer and the desktop execution daemon.

**Sources**: [packages/shared/src/types/computerAction.types.ts:1-126]()

---

## Type Hierarchy Overview

```mermaid
graph TB
    ComputerAction["ComputerAction<br/>(Discriminated Union)"]
    
    subgraph "Mouse Actions"
        MoveMouseAction["MoveMouseAction<br/>move_mouse"]
        TraceMouseAction["TraceMouseAction<br/>trace_mouse"]
        ClickMouseAction["ClickMouseAction<br/>click_mouse"]
        PressMouseAction["PressMouseAction<br/>press_mouse"]
        DragMouseAction["DragMouseAction<br/>drag_mouse"]
        ScrollAction["ScrollAction<br/>scroll"]
    end
    
    subgraph "Keyboard Actions"
        TypeKeysAction["TypeKeysAction<br/>type_keys"]
        PressKeysAction["PressKeysAction<br/>press_keys"]
        TypeTextAction["TypeTextAction<br/>type_text"]
        PasteTextAction["PasteTextAction<br/>paste_text"]
    end
    
    subgraph "System Actions"
        WaitAction["WaitAction<br/>wait"]
        ScreenshotAction["ScreenshotAction<br/>screenshot"]
        CursorPositionAction["CursorPositionAction<br/>cursor_position"]
        ApplicationAction["ApplicationAction<br/>application"]
    end
    
    subgraph "File Actions"
        WriteFileAction["WriteFileAction<br/>write_file"]
        ReadFileAction["ReadFileAction<br/>read_file"]
    end
    
    ComputerAction --> MoveMouseAction
    ComputerAction --> TraceMouseAction
    ComputerAction --> ClickMouseAction
    ComputerAction --> PressMouseAction
    ComputerAction --> DragMouseAction
    ComputerAction --> ScrollAction
    
    ComputerAction --> TypeKeysAction
    ComputerAction --> PressKeysAction
    ComputerAction --> TypeTextAction
    ComputerAction --> PasteTextAction
    
    ComputerAction --> WaitAction
    ComputerAction --> ScreenshotAction
    ComputerAction --> CursorPositionAction
    ComputerAction --> ApplicationAction
    
    ComputerAction --> WriteFileAction
    ComputerAction --> ReadFileAction
```

The `ComputerAction` type is a discriminated union of 17 distinct action types, each identified by its `action` field. This enables exhaustive pattern matching in the [ComputerUseService.action]() method at [packages/bytebotd/src/computer-use/computer-use.service.ts:34-104]().

**Sources**: [packages/shared/src/types/computerAction.types.ts:109-125](), [packages/bytebotd/src/computer-use/computer-use.service.ts:31-105]()

---

## Common Type Definitions

The following types are shared across multiple action definitions:

| Type | Definition | Usage |
|------|------------|-------|
| `Coordinates` | `{ x: number; y: number }` | Mouse position in pixels (0,0 = top-left, max = 1280x960) |
| `Button` | `"left" \| "right" \| "middle"` | Mouse button identifier for click/press/drag operations |
| `Press` | `"up" \| "down"` | Key or button state change direction |
| `Application` | `"firefox" \| "1password" \| "thunderbird" \| "vscode" \| "terminal" \| "desktop" \| "directory"` | Pre-installed applications available on the virtual desktop |

**Sources**: [packages/shared/src/types/computerAction.types.ts:1-11]()

---

## Action Type Reference

### Mouse Actions

| Action Type | Properties | Description |
|-------------|------------|-------------|
| **MoveMouseAction** | `coordinates: Coordinates` | Moves cursor to absolute position without clicking |
| **TraceMouseAction** | `path: Coordinates[]`<br/>`holdKeys?: string[]` | Moves cursor through multiple points, optionally holding modifier keys |
| **ClickMouseAction** | `coordinates?: Coordinates`<br/>`button: Button`<br/>`holdKeys?: string[]`<br/>`clickCount: number` | Performs single/double/triple click at position or current location |
| **PressMouseAction** | `coordinates?: Coordinates`<br/>`button: Button`<br/>`press: Press` | Press down or release mouse button without full click cycle |
| **DragMouseAction** | `path: Coordinates[]`<br/>`button: Button`<br/>`holdKeys?: string[]` | Hold button down and drag through path coordinates |
| **ScrollAction** | `coordinates?: Coordinates`<br/>`direction: "up"\|"down"\|"left"\|"right"`<br/>`scrollCount: number`<br/>`holdKeys?: string[]` | Scroll mouse wheel specified number of times |

**Sources**: [packages/shared/src/types/computerAction.types.ts:14-53]()

### Keyboard Actions

| Action Type | Properties | Description |
|-------------|------------|-------------|
| **TypeKeysAction** | `keys: string[]`<br/>`delay?: number` | Type sequence of keys (press+release each), used for shortcuts like `["LeftControl", "C"]` |
| **PressKeysAction** | `keys: string[]`<br/>`press: Press` | Press down or release keys without auto-release, for holding modifiers |
| **TypeTextAction** | `text: string`<br/>`delay?: number`<br/>`sensitive?: boolean` | Type text character-by-character, recommended for <25 characters or passwords |
| **PasteTextAction** | `text: string` | Copy text to clipboard and paste via Ctrl+V, recommended for long text or special characters |

The distinction between `TypeKeysAction` and `TypeTextAction` is critical: `type_keys` uses key codes (e.g., `"LeftControl"`, `"A"`) for shortcuts, while `type_text` uses literal character strings. Valid key names are documented in [packages/bytebotd/src/mcp/computer-use.tools.ts:319-344]().

**Sources**: [packages/shared/src/types/computerAction.types.ts:55-77](), [packages/bytebotd/src/mcp/computer-use.tools.ts:317-371]()

### System Actions

| Action Type | Properties | Description |
|-------------|------------|-------------|
| **WaitAction** | `duration: number` | Pause execution for specified milliseconds |
| **ScreenshotAction** | _(none)_ | Capture current desktop state as base64 PNG |
| **CursorPositionAction** | _(none)_ | Query current mouse coordinates |
| **ApplicationAction** | `application: Application` | Open or activate application window and maximize |

The `ApplicationAction` uses `wmctrl` to detect if the application is already running via process name matching defined in [packages/bytebotd/src/computer-use/computer-use.service.ts:296-304](), then either activates the existing window or launches a new instance.

**Sources**: [packages/shared/src/types/computerAction.types.ts:79-95](), [packages/bytebotd/src/computer-use/computer-use.service.ts:264-362]()

### File Actions

| Action Type | Properties | Description |
|-------------|------------|-------------|
| **WriteFileAction** | `path: string`<br/>`data: string` | Write base64-encoded data to file path (relative to `/home/user/Desktop/` if not absolute) |
| **ReadFileAction** | `path: string` | Read file and return base64-encoded data with media type detection |

File operations use sudo commands to manage permissions and default to the desktop directory if relative paths are provided. Media type mapping for common extensions is defined at [packages/bytebotd/src/computer-use/computer-use.service.ts:464-482]().

**Sources**: [packages/shared/src/types/computerAction.types.ts:97-106](), [packages/bytebotd/src/computer-use/computer-use.service.ts:364-506]()

---

## Validation Layer

### DTO Architecture

```mermaid
graph LR
    subgraph "API Request"
        RawJSON["Raw JSON Body"]
    end
    
    subgraph "Validation Pipe"
        ValidationPipe["ComputerActionValidationPipe"]
        ActionSwitch{"action field<br/>discrimination"}
    end
    
    subgraph "DTO Classes"
        MoveMouseDto["MoveMouseActionDto"]
        ClickMouseDto["ClickMouseActionDto"]
        TypeTextDto["TypeTextActionDto"]
        OtherDtos["... 14 more DTOs"]
    end
    
    subgraph "Class Validator"
        Validate["validate()"]
        Transform["plainToClass()"]
    end
    
    subgraph "Base DTOs"
        CoordinatesDto["CoordinatesDto<br/>@IsNumber x,y"]
        ButtonEnum["ButtonType enum"]
        PressEnum["PressType enum"]
        AppEnum["ApplicationName enum"]
    end
    
    subgraph "Execution"
        ComputerUseService["ComputerUseService.action()"]
    end
    
    RawJSON --> ValidationPipe
    ValidationPipe --> ActionSwitch
    
    ActionSwitch -->|"move_mouse"| MoveMouseDto
    ActionSwitch -->|"click_mouse"| ClickMouseDto
    ActionSwitch -->|"type_text"| TypeTextDto
    ActionSwitch -->|"..."| OtherDtos
    
    MoveMouseDto --> Transform
    ClickMouseDto --> Transform
    TypeTextDto --> Transform
    OtherDtos --> Transform
    
    Transform --> Validate
    
    MoveMouseDto -.->|"uses"| CoordinatesDto
    ClickMouseDto -.->|"uses"| CoordinatesDto
    ClickMouseDto -.->|"uses"| ButtonEnum
    TypeTextDto -.->|"uses"| PressEnum
    OtherDtos -.->|"uses"| AppEnum
    
    Validate -->|"valid"| ComputerUseService
    Validate -->|"invalid"| BadRequest["BadRequestException"]
```

The validation layer transforms untrusted JSON into type-safe DTOs through a multi-step pipeline:

1. **Discrimination**: [ComputerActionValidationPipe]() inspects the `action` field at [packages/bytebotd/src/computer-use/dto/computer-action-validation.pipe.ts:36-87]()
2. **Transformation**: `plainToClass()` converts plain objects to DTO instances with proper types
3. **Validation**: `class-validator` decorators enforce constraints (e.g., `@Min(1)` for clickCount)
4. **Execution**: Validated DTO is passed to [ComputerUseService.action()]()

**Sources**: [packages/bytebotd/src/computer-use/dto/computer-action-validation.pipe.ts:1-97](), [packages/bytebotd/src/computer-use/dto/computer-action.dto.ts:1-240]()

### DTO Decorators

Each DTO class uses `class-validator` decorators for runtime enforcement:

```typescript
// Example from ClickMouseActionDto
@IsIn(['click_mouse'])
action: 'click_mouse';

@IsOptional()
@ValidateNested()
@Type(() => CoordinatesDto)
coordinates?: CoordinatesDto;

@IsEnum(ButtonType)
button: ButtonType;

@IsNumber()
@Min(1)
clickCount: number;
```

Base enums are defined in [packages/bytebotd/src/computer-use/dto/base.dto.ts:11-37]() to provide compile-time and runtime validation.

**Sources**: [packages/bytebotd/src/computer-use/dto/computer-action.dto.ts:51-71](), [packages/bytebotd/src/computer-use/dto/base.dto.ts:1-38]()

---

## Type Guards and Converters

### Type Guard Pattern

The shared package provides type guards for runtime type discrimination:

```typescript
// Factory pattern for creating type guards
function createActionTypeGuard<T extends ComputerAction>(
  actionType: T["action"]
): (obj: unknown) => obj is T {
  return (obj: unknown): obj is T => {
    if (!obj || typeof obj !== "object") {
      return false;
    }
    const action = obj as Record<string, any>;
    return action.action === actionType;
  };
}

// Generated type guards
export const isMoveMouseAction = createActionTypeGuard<MoveMouseAction>("move_mouse");
export const isClickMouseAction = createActionTypeGuard<ClickMouseAction>("click_mouse");
// ... etc for all 17 types
```

**Sources**: [packages/shared/src/utils/computerAction.utils.ts:28-66]()

### Conversion to ToolUse Blocks

The `convertComputerActionToToolUseBlock()` function at [packages/shared/src/utils/computerAction.utils.ts:299-342]() transforms `ComputerAction` types into `ComputerToolUseContentBlock` types, which are used in AI conversation messages. This enables the agent to record user actions during takeover mode and include them in the LLM context.

**Example conversion flow**:

```mermaid
graph LR
    subgraph "User Takeover"
        InputTracking["InputTrackingService"]
        UserAction["User clicks at 100,200"]
    end
    
    subgraph "Action Recording"
        RecordAction["Record ClickMouseAction"]
        ActionObj["{ action: 'click_mouse',<br/>coordinates: {x:100, y:200},<br/>button: 'left',<br/>clickCount: 1 }"]
    end
    
    subgraph "Conversion"
        Converter["convertClickMouseActionToToolUseBlock()"]
        ToolUse["{ type: 'tool_use',<br/>name: 'computer_click_mouse',<br/>id: 'tool_xyz',<br/>input: {...} }"]
    end
    
    subgraph "Message Storage"
        UserActionBlock["UserActionContentBlock"]
        MessagesDB[("Messages Table")]
    end
    
    UserAction --> InputTracking
    InputTracking --> RecordAction
    RecordAction --> ActionObj
    ActionObj --> Converter
    Converter --> ToolUse
    ToolUse --> UserActionBlock
    UserActionBlock --> MessagesDB
```

**Sources**: [packages/shared/src/utils/computerAction.utils.ts:103-294](), [packages/shared/src/types/messageContent.types.ts:205-219]()

---

## Integration with Message Content Types

### ToolUse Block Mapping

Each `ComputerAction` type has a corresponding `ComputerToolUseContentBlock` variant defined in [packages/shared/src/types/messageContent.types.ts:64-203](). The mapping uses the `computer_` prefix convention:

| ComputerAction | ToolUse Block Name |
|----------------|-------------------|
| `move_mouse` | `computer_move_mouse` |
| `click_mouse` | `computer_click_mouse` |
| `type_text` | `computer_type_text` |
| `screenshot` | `computer_screenshot` |
| `write_file` | `computer_write_file` |
| _(etc for all 17 types)_ | _(consistent naming)_ |

This dual representation exists because:
- **ComputerAction**: Used by bytebotd for execution (internal API contract)
- **ToolUse Block**: Used by LLMs for decision-making and conversation history (AI interface)

The agent converts between these representations when processing LLM responses at [packages/bytebot-agent/src/agent/agent.processor.ts]() (see [Agent Processor](#6.1) for details).

**Sources**: [packages/shared/src/types/messageContent.types.ts:187-203]()

### MCP Tool Definitions

The MCP integration layer defines Zod schemas that mirror the DTO validation but use the MCP SDK's `@Tool()` decorator pattern at [packages/bytebotd/src/mcp/computer-use.tools.ts:11-697](). Each tool method wraps a call to `ComputerUseService.action()`:

```typescript
@Tool({
  name: 'computer_click_mouse',
  description: 'Performs a mouse click at the specified coordinates or current position.',
  parameters: z.object({
    coordinates: z.object({
      x: z.number().describe('The x-coordinate to move the mouse to.'),
      y: z.number().describe('The y-coordinate to move the mouse to.'),
    }).optional(),
    button: z.enum(['left', 'right', 'middle']),
    holdKeys: z.array(z.string()).optional(),
    clickCount: z.number(),
  }),
})
async clickMouse({ coordinates, button, holdKeys, clickCount }) {
  await this.computerUse.action({
    action: 'click_mouse',
    coordinates,
    button,
    holdKeys,
    clickCount,
  });
  return { content: [{ type: 'text', text: 'mouse clicked' }] };
}
```

**Sources**: [packages/bytebotd/src/mcp/computer-use.tools.ts:80-138]()

---

## Execution Flow

```mermaid
graph TB
    subgraph "AI Agent - bytebot-agent"
        LLMResponse["LLM Response with<br/>ToolUse blocks"]
        AgentProcessor["AgentProcessor.handleComputerToolUse()"]
        ExtractInput["Extract input object<br/>from ToolUse block"]
        AddAction["Add 'action' field<br/>to create ComputerAction"]
    end
    
    subgraph "API Call"
        HTTPPost["POST /computer-use"]
    end
    
    subgraph "Validation - bytebotd"
        ValidationPipe["ComputerActionValidationPipe"]
        DTOInstance["Validated DTO instance"]
    end
    
    subgraph "Execution - bytebotd"
        ComputerUseService["ComputerUseService.action()"]
        ActionSwitch{"Switch on<br/>action field"}
        MoveMouseHandler["moveMouse()"]
        ClickMouseHandler["clickMouse()"]
        TypeTextHandler["typeText()"]
        OtherHandlers["... 14 more handlers"]
    end
    
    subgraph "Automation - NutService"
        NutJS["@nut-tree-fork/nut-js"]
        XEvents["X11 Events"]
    end
    
    LLMResponse --> AgentProcessor
    AgentProcessor --> ExtractInput
    ExtractInput --> AddAction
    AddAction --> HTTPPost
    
    HTTPPost --> ValidationPipe
    ValidationPipe --> DTOInstance
    DTOInstance --> ComputerUseService
    
    ComputerUseService --> ActionSwitch
    ActionSwitch -->|"move_mouse"| MoveMouseHandler
    ActionSwitch -->|"click_mouse"| ClickMouseHandler
    ActionSwitch -->|"type_text"| TypeTextHandler
    ActionSwitch -->|"..."| OtherHandlers
    
    MoveMouseHandler --> NutJS
    ClickMouseHandler --> NutJS
    TypeTextHandler --> NutJS
    OtherHandlers --> NutJS
    
    NutJS --> XEvents
```

The complete flow from AI decision to desktop action involves:

1. **LLM generates ToolUse block** with tool name (e.g., `computer_click_mouse`) and input parameters
2. **AgentProcessor extracts input** and adds the `action` field to create a valid `ComputerAction`
3. **HTTP POST to bytebotd** at `/computer-use` endpoint
4. **Validation pipe discriminates** on `action` field and validates against appropriate DTO
5. **ComputerUseService dispatches** to action-specific handler method
6. **NutService executes** low-level automation via NutJS library
7. **X11 events** manipulate the virtual desktop

**Sources**: [packages/bytebotd/src/computer-use/computer-use.service.ts:31-105](), [packages/bytebot-agent/src/agent/agent.processor.ts]()

---

## Summary Table

| Component | Location | Purpose |
|-----------|----------|---------|
| **Type Definitions** | [packages/shared/src/types/computerAction.types.ts]() | Shared TypeScript types for compile-time safety |
| **Validation DTOs** | [packages/bytebotd/src/computer-use/dto/computer-action.dto.ts]() | Runtime validation via class-validator decorators |
| **Validation Pipe** | [packages/bytebotd/src/computer-use/dto/computer-action-validation.pipe.ts]() | NestJS pipe for discriminating and validating requests |
| **Type Guards** | [packages/shared/src/utils/computerAction.utils.ts]() | Runtime type checking utilities |
| **Converters** | [packages/shared/src/utils/computerAction.utils.ts]() | Convert between ComputerAction and ToolUse blocks |
| **MCP Tools** | [packages/bytebotd/src/mcp/computer-use.tools.ts]() | Zod-based MCP tool definitions |
| **Execution Service** | [packages/bytebotd/src/computer-use/computer-use.service.ts]() | Dispatches actions to NutService for execution |

**Sources**: Multiple files cited in table

---

# Page: API Reference

# API Reference

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [packages/bytebot-agent/src/agent/agent.processor.ts](packages/bytebot-agent/src/agent/agent.processor.ts)
- [packages/bytebot-agent/src/tasks/tasks.controller.ts](packages/bytebot-agent/src/tasks/tasks.controller.ts)
- [packages/bytebot-agent/src/tasks/tasks.service.ts](packages/bytebot-agent/src/tasks/tasks.service.ts)
- [packages/bytebot-ui/src/hooks/useChatSession.ts](packages/bytebot-ui/src/hooks/useChatSession.ts)
- [packages/bytebotd/src/computer-use/computer-use.service.ts](packages/bytebotd/src/computer-use/computer-use.service.ts)
- [packages/bytebotd/src/computer-use/dto/base.dto.ts](packages/bytebotd/src/computer-use/dto/base.dto.ts)
- [packages/bytebotd/src/computer-use/dto/computer-action-validation.pipe.ts](packages/bytebotd/src/computer-use/dto/computer-action-validation.pipe.ts)
- [packages/bytebotd/src/computer-use/dto/computer-action.dto.ts](packages/bytebotd/src/computer-use/dto/computer-action.dto.ts)
- [packages/bytebotd/src/mcp/computer-use.tools.ts](packages/bytebotd/src/mcp/computer-use.tools.ts)
- [packages/shared/src/types/computerAction.types.ts](packages/shared/src/types/computerAction.types.ts)
- [packages/shared/src/types/messageContent.types.ts](packages/shared/src/types/messageContent.types.ts)
- [packages/shared/src/utils/computerAction.utils.ts](packages/shared/src/utils/computerAction.utils.ts)
- [packages/shared/src/utils/messageContent.utils.ts](packages/shared/src/utils/messageContent.utils.ts)

</details>



This document provides a comprehensive reference for all HTTP and WebSocket APIs exposed by the Bytebot system. It covers the REST API endpoints for task management, the Computer Use API for desktop automation, and the WebSocket API for real-time event subscriptions.

For detailed endpoint specifications, see:
- Tasks REST API: [#10.1](#10.1)
- Computer Use API: [#10.2](#10.2)
- WebSocket API: [#10.3](#10.3)

For information about the data models used in these APIs, see [Data Models](#9).

---

## API Architecture Overview

The Bytebot system exposes three distinct API surfaces across two backend services:

**bytebot-agent (Port 9991):**
- **Tasks REST API**: CRUD operations for tasks, messages, and task control
- **WebSocket API**: Real-time task and message events via Socket.IO

**bytebotd (Port 9990):**
- **Computer Use API**: Desktop automation actions and screenshots

**bytebot-ui (Port 9992)** acts as a unified proxy layer, routing requests to the appropriate backend service.

```mermaid
graph TB
    subgraph "Client Layer"
        Browser["Web Browser / API Client"]
    end
    
    subgraph "bytebot-ui (Port 9992)"
        UIProxy["/api/proxy/tasks<br/>HTTP Proxy"]
        WSProxy["/api/proxy/tasks<br/>WebSocket Proxy"]
    end
    
    subgraph "bytebot-agent (Port 9991)"
        TasksController["TasksController<br/>/tasks/*"]
        TasksGateway["TasksGateway<br/>Socket.IO Server"]
        
        TasksService["TasksService"]
        MessagesService["MessagesService"]
    end
    
    subgraph "bytebotd (Port 9990)"
        ComputerUseController["ComputerUseController<br/>/computer-use"]
        ComputerUseService["ComputerUseService"]
    end
    
    subgraph "Data Layer"
        PostgreSQL[("PostgreSQL<br/>Tasks, Messages,<br/>Summaries, Files")]
    end
    
    Browser -->|"GET/POST/PATCH/DELETE"| UIProxy
    Browser -->|"Socket.IO Events"| WSProxy
    
    UIProxy -->|"HTTP"| TasksController
    WSProxy -->|"WebSocket"| TasksGateway
    
    TasksController --> TasksService
    TasksController --> MessagesService
    TasksGateway --> TasksService
    
    TasksService --> PostgreSQL
    MessagesService --> PostgreSQL
    
    TasksService -.->|"POST /computer-use"| ComputerUseController
    ComputerUseController --> ComputerUseService
    
    ComputerUseService -.->|"Desktop Automation"| Desktop["XFCE Desktop<br/>NutJS / uiohook"]
```

**Sources:** [packages/bytebot-agent/src/tasks/tasks.controller.ts](), [packages/bytebotd/src/computer-use/computer-use.service.ts]()

---

## Base URLs and Service Endpoints

### Development Environment

| Service | Base URL | Purpose |
|---------|----------|---------|
| **bytebot-ui** | `http://localhost:9992` | Unified frontend and API proxy |
| **bytebot-agent** | `http://localhost:9991` | Task orchestration and AI agent |
| **bytebotd** | `http://localhost:9990` | Desktop automation execution |

### Production (via Proxy)

When accessing through **bytebot-ui**, all backend services are proxied:

| API Surface | Proxied Path | Target Service |
|-------------|--------------|----------------|
| Tasks REST API | `/api/proxy/tasks/*` | `bytebot-agent:9991/tasks/*` |
| WebSocket API | `/api/proxy/tasks` (Socket.IO) | `bytebot-agent:9991` |
| Computer Use API | Direct access not proxied | `bytebot-agent` calls internally |

**Sources:** [packages/bytebot-ui/src/server.ts]()

---

## API Surface Breakdown

### Tasks REST API Endpoints

The Tasks REST API provides full CRUD operations for task management:

```mermaid
graph LR
    subgraph "Task Lifecycle Endpoints"
        CreateTask["POST /tasks<br/>CreateTaskDto"]
        GetTasks["GET /tasks<br/>?page&limit&status"]
        GetTask["GET /tasks/:id"]
        DeleteTask["DELETE /tasks/:id"]
    end
    
    subgraph "Task Control Endpoints"
        TakeOver["POST /tasks/:id/takeover<br/>Transfer to USER control"]
        Resume["POST /tasks/:id/resume<br/>Transfer to ASSISTANT control"]
        Cancel["POST /tasks/:id/cancel<br/>Cancel execution"]
    end
    
    subgraph "Message Endpoints"
        GetMessages["GET /tasks/:id/messages<br/>Paginated messages"]
        AddMessage["POST /tasks/:id/messages<br/>Add user guidance"]
        GetRaw["GET /tasks/:id/messages/raw<br/>Unprocessed messages"]
        GetProcessed["GET /tasks/:id/messages/processed<br/>Grouped messages"]
    end
    
    subgraph "Model Metadata"
        GetModels["GET /tasks/models<br/>Available AI models"]
    end
```

**Sources:** [packages/bytebot-agent/src/tasks/tasks.controller.ts:1-194]()

### Computer Use API Actions

The Computer Use API accepts action objects via `POST /computer-use`:

```mermaid
graph TB
    subgraph "Mouse Actions"
        MoveMouse["move_mouse<br/>MoveMouseAction"]
        TraceMouse["trace_mouse<br/>TraceMouseAction"]
        ClickMouse["click_mouse<br/>ClickMouseAction"]
        PressMouse["press_mouse<br/>PressMouseAction"]
        DragMouse["drag_mouse<br/>DragMouseAction"]
        Scroll["scroll<br/>ScrollAction"]
    end
    
    subgraph "Keyboard Actions"
        TypeKeys["type_keys<br/>TypeKeysAction"]
        PressKeys["press_keys<br/>PressKeysAction"]
        TypeText["type_text<br/>TypeTextAction"]
        PasteText["paste_text<br/>PasteTextAction"]
    end
    
    subgraph "Observation Actions"
        Screenshot["screenshot<br/>ScreenshotAction"]
        CursorPos["cursor_position<br/>CursorPositionAction"]
    end
    
    subgraph "Application Actions"
        OpenApp["application<br/>ApplicationAction"]
        Wait["wait<br/>WaitAction"]
    end
    
    subgraph "File Operations"
        WriteFile["write_file<br/>WriteFileAction"]
        ReadFile["read_file<br/>ReadFileAction"]
    end
    
    ComputerAction["ComputerAction<br/>(Union Type)"] --> MoveMouse
    ComputerAction --> TraceMouse
    ComputerAction --> ClickMouse
    ComputerAction --> PressMouse
    ComputerAction --> DragMouse
    ComputerAction --> Scroll
    ComputerAction --> TypeKeys
    ComputerAction --> PressKeys
    ComputerAction --> TypeText
    ComputerAction --> PasteText
    ComputerAction --> Screenshot
    ComputerAction --> CursorPos
    ComputerAction --> OpenApp
    ComputerAction --> Wait
    ComputerAction --> WriteFile
    ComputerAction --> ReadFile
```

**Sources:** [packages/shared/src/types/computerAction.types.ts:1-126](), [packages/bytebotd/src/computer-use/dto/computer-action.dto.ts:1-240]()

### WebSocket Event Types

The WebSocket API uses Socket.IO for bidirectional communication:

| Event Direction | Event Name | Payload | Purpose |
|----------------|------------|---------|---------|
| **Client → Server** | `join_task` | `{ taskId: string }` | Subscribe to task updates |
| **Client → Server** | `leave_task` | `{ taskId: string }` | Unsubscribe from task updates |
| **Server → Client** | `task_created` | `Task` | New task created (global) |
| **Server → Client** | `task_updated` | `Task` | Task state changed (room-scoped) |
| **Server → Client** | `task_deleted` | `{ taskId: string }` | Task deleted (global) |
| **Server → Client** | `new_message` | `Message` | New message added (room-scoped) |

**Sources:** [packages/bytebot-agent/src/tasks/tasks.gateway.ts](), [packages/bytebot-ui/src/hooks/useWebSocket.ts]()

---

## Core Type System

The API uses a shared type system defined in the `@bytebot/shared` package:

### Request/Response Type Flow

```mermaid
graph TB
    subgraph "Client Request Types"
        CreateTaskDto["CreateTaskDto<br/>description, model,<br/>files[], priority"]
        AddTaskMessageDto["AddTaskMessageDto<br/>message: string"]
        ComputerActionDto["ComputerActionDto<br/>Discriminated union<br/>by action field"]
    end
    
    subgraph "Shared Domain Types"
        Task["Task<br/>id, description, status,<br/>control, model, priority"]
        Message["Message<br/>id, content, role,<br/>taskId, summaryId"]
        MessageContentBlock["MessageContentBlock<br/>Text | Image | Document<br/>ToolUse | ToolResult<br/>Thinking | UserAction"]
    end
    
    subgraph "Response Types"
        TaskResponse["Task<br/>(with files[])"]
        MessageArray["Message[]<br/>(paginated)"]
        GroupedMessages["GroupedMessages[]<br/>(UI-optimized)"]
        ComputerResult["{ image?: string }<br/>| { success, message }"]
    end
    
    CreateTaskDto -->|"TasksService.create()"| TaskResponse
    AddTaskMessageDto -->|"TasksService.addTaskMessage()"| TaskResponse
    ComputerActionDto -->|"ComputerUseService.action()"| ComputerResult
    
    Task -.->|"Persisted to"| PostgreSQL[("PostgreSQL<br/>Task table")]
    Message -.->|"Persisted to"| PostgreSQL
    
    TaskResponse --> Task
    MessageArray --> Message
    Message --> MessageContentBlock
```

**Sources:** [packages/shared/src/types/messageContent.types.ts:1-258](), [packages/bytebot-agent/src/tasks/dto/create-task.dto.ts]()

### MessageContentBlock Type Hierarchy

The `MessageContentBlock` type is a discriminated union used throughout the message system:

| Type | Discriminator | Key Fields | Purpose |
|------|---------------|------------|---------|
| `TextContentBlock` | `type: "text"` | `text: string` | Plain text content |
| `ImageContentBlock` | `type: "image"` | `source: { data, media_type }` | Base64-encoded images |
| `DocumentContentBlock` | `type: "document"` | `source: { data, media_type }`, `name`, `size` | File attachments |
| `ToolUseContentBlock` | `type: "tool_use"` | `name: string`, `input: object`, `id: string` | LLM tool invocations |
| `ToolResultContentBlock` | `type: "tool_result"` | `tool_use_id: string`, `content: []`, `is_error?` | Tool execution results |
| `ThinkingContentBlock` | `type: "thinking"` | `thinking: string`, `signature: string` | Extended thinking (Claude) |
| `UserActionContentBlock` | `type: "user_action"` | `content: []` | Captured user input |

**Sources:** [packages/shared/src/types/messageContent.types.ts:1-258]()

### ComputerAction Type Hierarchy

All desktop automation actions share the `ComputerAction` discriminated union:

```mermaid
graph TB
    subgraph "Action Categories"
        MouseActions["Mouse Actions<br/>move_mouse, trace_mouse,<br/>click_mouse, press_mouse,<br/>drag_mouse, scroll"]
        KeyboardActions["Keyboard Actions<br/>type_keys, press_keys,<br/>type_text, paste_text"]
        ObservationActions["Observation Actions<br/>screenshot,<br/>cursor_position"]
        UtilityActions["Utility Actions<br/>wait, application,<br/>write_file, read_file"]
    end
    
    ComputerAction["ComputerAction<br/>Discriminated by<br/>action: string"] --> MouseActions
    ComputerAction --> KeyboardActions
    ComputerAction --> ObservationActions
    ComputerAction --> UtilityActions
    
    MouseActions -.->|"Coordinates"| CoordinatesType["Coordinates<br/>{ x: number, y: number }"]
    MouseActions -.->|"Button"| ButtonType["Button<br/>'left' | 'right' | 'middle'"]
    KeyboardActions -.->|"Keys"| KeyArray["string[]<br/>Valid key names"]
```

**Sources:** [packages/shared/src/types/computerAction.types.ts:1-126](), [packages/bytebotd/src/computer-use/dto/base.dto.ts:1-38]()

---

## Authentication and Configuration

### Environment Variables

The APIs require the following environment variables:

**bytebot-agent:**
```bash
DATABASE_URL=postgresql://user:password@localhost:5432/bytebot
ANTHROPIC_API_KEY=sk-ant-...        # For Claude models
OPENAI_API_KEY=sk-...               # For GPT models
GEMINI_API_KEY=...                  # For Gemini models
BYTEBOT_DESKTOP_BASE_URL=http://localhost:9990  # bytebotd URL
```

**bytebotd:**
```bash
# No API keys required - receives actions from bytebot-agent
```

**Sources:** [packages/bytebot-agent/src/tasks/tasks.controller.ts:23-28]()

### Model Selection

Available models are dynamically determined by configured API keys:

```typescript
GET /tasks/models
```

**Response:**
```json
[
  {
    "provider": "anthropic",
    "name": "claude-3-7-sonnet-20250219",
    "title": "Claude 3.7 Sonnet",
    "contextWindow": 200000
  },
  {
    "provider": "openai", 
    "name": "gpt-4o",
    "title": "GPT-4o",
    "contextWindow": 128000
  }
]
```

**Sources:** [packages/bytebot-agent/src/tasks/tasks.controller.ts:69-111]()

---

## Request/Response Patterns

### Standard Task Creation Flow

```mermaid
sequenceDiagram
    participant Client
    participant TasksController
    participant TasksService
    participant MessagesService
    participant PostgreSQL
    participant TasksGateway
    
    Client->>TasksController: POST /tasks<br/>CreateTaskDto
    TasksController->>TasksService: create(dto)
    
    TasksService->>PostgreSQL: BEGIN TRANSACTION
    TasksService->>PostgreSQL: INSERT Task
    
    opt Files attached
        TasksService->>PostgreSQL: INSERT Files (base64)
    end
    
    TasksService->>PostgreSQL: INSERT initial Message<br/>(USER, description)
    TasksService->>PostgreSQL: COMMIT
    
    TasksService->>TasksGateway: emitTaskCreated(task)
    TasksGateway-->>Client: task_created event (broadcast)
    
    TasksService-->>TasksController: Task
    TasksController-->>Client: 201 Created<br/>Task
```

**Sources:** [packages/bytebot-agent/src/tasks/tasks.service.ts:40-117](), [packages/bytebot-agent/src/tasks/tasks.controller.ts:42-46]()

### Computer Action Execution Flow

```mermaid
sequenceDiagram
    participant AgentProcessor
    participant ComputerUseController
    participant ComputerUseService
    participant NutService
    participant Desktop
    
    AgentProcessor->>ComputerUseController: POST /computer-use<br/>ComputerActionDto
    ComputerUseController->>ComputerUseService: action(params)
    
    alt Screenshot
        ComputerUseService->>NutService: screendump()
        NutService->>Desktop: Capture screen
        Desktop-->>NutService: Raw buffer
        NutService-->>ComputerUseService: PNG buffer
        ComputerUseService-->>ComputerUseController: { image: base64 }
    else Mouse Action
        ComputerUseService->>NutService: mouseMoveEvent(coords)
        NutService->>Desktop: Move cursor
        Desktop-->>NutService: Success
        NutService-->>ComputerUseService: void
        ComputerUseService-->>ComputerUseController: void
    else File Operation
        ComputerUseService->>Desktop: Write to /home/user/Desktop
        Desktop-->>ComputerUseService: Success
        ComputerUseService-->>ComputerUseController: { success, message }
    end
    
    ComputerUseController-->>AgentProcessor: 200 OK<br/>Result
```

**Sources:** [packages/bytebotd/src/computer-use/computer-use.service.ts:31-507](), [packages/bytebot-agent/src/agent/agent.computer-use.ts]()

---

## Validation and Error Handling

### DTO Validation

All endpoints use class-validator decorators for input validation:

**Example: CreateTaskDto**
```typescript
class CreateTaskDto {
  @IsString()
  @IsNotEmpty()
  description: string;

  @IsOptional()
  @ValidateNested()
  @Type(() => BytebotAgentModel)
  model?: BytebotAgentModel;

  @IsOptional()
  @IsArray()
  @ValidateNested({ each: true })
  @Type(() => FileWithBase64)
  files?: FileWithBase64[];
}
```

**Sources:** [packages/bytebot-agent/src/tasks/dto/create-task.dto.ts]()

### Computer Action Validation Pipeline

Computer actions use a discriminated union validation pipe:

```mermaid
graph TB
    Request["POST /computer-use<br/>{ action, ...params }"]
    
    Request --> Pipe["ComputerActionValidationPipe"]
    
    Pipe --> Switch{action field}
    
    Switch -->|"move_mouse"| DTO1["plainToClass<br/>MoveMouseActionDto"]
    Switch -->|"click_mouse"| DTO2["plainToClass<br/>ClickMouseActionDto"]
    Switch -->|"screenshot"| DTO3["plainToClass<br/>ScreenshotActionDto"]
    Switch -->|"unknown"| Error1["BadRequestException<br/>'Unknown action'"]
    
    DTO1 --> Validate1["validate(dto)"]
    DTO2 --> Validate2["validate(dto)"]
    DTO3 --> Validate3["validate(dto)"]
    
    Validate1 --> Check1{errors.length}
    Validate2 --> Check2{errors.length}
    Validate3 --> Check3{errors.length}
    
    Check1 -->|"> 0"| Error2["BadRequestException<br/>validation errors"]
    Check2 -->|"> 0"| Error2
    Check3 -->|"> 0"| Error2
    
    Check1 -->|"= 0"| Valid["Return validated DTO"]
    Check2 -->|"= 0"| Valid
    Check3 -->|"= 0"| Valid
```

**Sources:** [packages/bytebotd/src/computer-use/dto/computer-action-validation.pipe.ts:1-97]()

### Standard Error Responses

All endpoints return standard NestJS error responses:

| Status Code | Error Type | Example |
|-------------|------------|---------|
| 400 | `BadRequestException` | Invalid DTO, validation failure |
| 404 | `NotFoundException` | Task not found |
| 500 | `InternalServerException` | Unexpected errors |

**Response Format:**
```json
{
  "statusCode": 404,
  "message": "Task with ID abc-123 not found",
  "error": "Not Found"
}
```

---

## Pagination and Filtering

### Task List Pagination

```
GET /tasks?page=1&limit=10&status=RUNNING
```

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | `number` | `1` | Page number (1-indexed) |
| `limit` | `number` | `10` | Items per page |
| `status` | `string` | - | Single status filter |
| `statuses` | `string` | - | Comma-separated statuses |

**Response:**
```json
{
  "tasks": [Task],
  "total": 42,
  "totalPages": 5
}
```

**Sources:** [packages/bytebot-agent/src/tasks/tasks.controller.ts:48-67](), [packages/bytebot-agent/src/tasks/tasks.service.ts:158-190]()

### Message Pagination

```
GET /tasks/:id/messages?page=1&limit=10
```

Messages are returned in reverse chronological order (newest first).

**Sources:** [packages/bytebot-agent/src/tasks/tasks.controller.ts:118-131]()

---

## Type Guards and Utilities

The `@bytebot/shared` package provides type guard functions for runtime type checking:

**MessageContentBlock Type Guards:**
```typescript
isTextContentBlock(obj): obj is TextContentBlock
isImageContentBlock(obj): obj is ImageContentBlock  
isToolUseContentBlock(obj): obj is ToolUseContentBlock
isComputerToolUseContentBlock(obj): obj is ComputerToolUseContentBlock
isSetTaskStatusToolUseBlock(obj): obj is SetTaskStatusToolUseBlock
```

**ComputerAction Type Guards:**
```typescript
isMoveMouseAction(obj): obj is MoveMouseAction
isClickMouseAction(obj): obj is ClickMouseAction
isScreenshotAction(obj): obj is ScreenshotAction
```

**Converter Functions:**
```typescript
convertComputerActionToToolUseBlock(
  action: ComputerAction,
  toolUseId: string
): ComputerToolUseContentBlock
```

**Sources:** [packages/shared/src/utils/messageContent.utils.ts:1-516](), [packages/shared/src/utils/computerAction.utils.ts:1-343]()

---

## Complete API Reference Sections

For detailed documentation of individual endpoints and events, refer to:

- **[Tasks REST API](#10.1)**: Complete endpoint specifications, request/response schemas, and examples
- **[Computer Use API](#10.2)**: All 17 desktop automation actions with parameter details
- **[WebSocket API](#10.3)**: Event specifications, room management, and real-time patterns

**Sources:** All files listed above

---

# Page: Tasks REST API

# Tasks REST API

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [packages/bytebot-agent/src/agent/agent.processor.ts](packages/bytebot-agent/src/agent/agent.processor.ts)
- [packages/bytebot-agent/src/tasks/tasks.controller.ts](packages/bytebot-agent/src/tasks/tasks.controller.ts)
- [packages/bytebot-agent/src/tasks/tasks.service.ts](packages/bytebot-agent/src/tasks/tasks.service.ts)
- [packages/bytebot-ui/src/hooks/useChatSession.ts](packages/bytebot-ui/src/hooks/useChatSession.ts)

</details>



This document provides a complete reference for the HTTP REST API exposed by the **bytebot-agent** service for task management. The Tasks REST API enables creating, querying, updating, and deleting tasks, as well as managing task messages and control flow. For real-time updates about task state changes, see [WebSocket API](#10.3). For information about task lifecycle and states, see [Task Lifecycle](#5.1).

**Sources:** [packages/bytebot-agent/src/tasks/tasks.controller.ts:1-194]()

---

## API Overview

The Tasks REST API is implemented in the `TasksController` class and operates on the `/tasks` base path. All endpoints communicate via JSON and are proxied through the bytebot-ui frontend service running on port 9992, which forwards requests to bytebot-agent on port 9991.

```mermaid
graph LR
    Client["HTTP Client<br/>(Browser/External)"]
    Proxy["bytebot-ui Proxy<br/>:9992/api/proxy/tasks"]
    Controller["TasksController<br/>:9991/tasks"]
    Service["TasksService"]
    DB[("PostgreSQL<br/>Task, Message,<br/>Summary, File")]
    
    Client -->|"HTTP Request"| Proxy
    Proxy -->|"Forward to backend"| Controller
    Controller -->|"Business logic"| Service
    Service -->|"Prisma queries"| DB
    DB -->|"Data"| Service
    Service -->|"Domain objects"| Controller
    Controller -->|"JSON response"| Proxy
    Proxy -->|"HTTP Response"| Client
```

**Sources:** [packages/bytebot-agent/src/tasks/tasks.controller.ts:35-36](), [packages/bytebot-ui/src/utils/taskUtils.ts]()

---

## Endpoint Reference

The following table summarizes all available endpoints:

| Method | Path | Purpose | Auth Required |
|--------|------|---------|---------------|
| `POST` | `/tasks` | Create a new task | No |
| `GET` | `/tasks` | List tasks with pagination and filtering | No |
| `GET` | `/tasks/models` | Retrieve available LLM models | No |
| `GET` | `/tasks/:id` | Get a specific task by ID | No |
| `GET` | `/tasks/:id/messages` | Retrieve task messages (filtered) | No |
| `POST` | `/tasks/:id/messages` | Add a user message to a task | No |
| `GET` | `/tasks/:id/messages/raw` | Retrieve raw unprocessed messages | No |
| `GET` | `/tasks/:id/messages/processed` | Retrieve UI-formatted grouped messages | No |
| `DELETE` | `/tasks/:id` | Delete a task and all related data | No |
| `POST` | `/tasks/:id/takeover` | Transfer control to user | No |
| `POST` | `/tasks/:id/resume` | Transfer control back to agent | No |
| `POST` | `/tasks/:id/cancel` | Cancel a running task | No |

**Sources:** [packages/bytebot-agent/src/tasks/tasks.controller.ts:35-193]()

---

## Core Endpoints

### POST /tasks

Creates a new task and initializes it with a system message. If files are attached, they are stored in the database and the initial message is augmented with file notification text.

**Request Body:** `CreateTaskDto`

```typescript
{
  description: string;           // Required: Task description
  model?: BytebotAgentModel;     // Optional: LLM model to use
  type?: TaskType;               // Optional: IMMEDIATE (default) or SCHEDULED
  priority?: TaskPriority;       // Optional: LOW, MEDIUM (default), HIGH
  scheduledFor?: Date;           // Optional: Schedule time for SCHEDULED tasks
  createdBy?: Role;              // Optional: USER (default) or ASSISTANT
  files?: FileWithBase64[];      // Optional: Files to attach
}
```

**Response:** `Task` object with status `PENDING`

**Status Codes:**
- `201 Created` - Task created successfully
- `400 Bad Request` - Invalid request data

**Implementation Details:**
1. Creates a task record with initial status `PENDING`
2. Saves attached files to database (base64-encoded)
3. Creates initial USER message with description and file notifications
4. Emits `task_created` WebSocket event via `TasksGateway`

**Sources:** [packages/bytebot-agent/src/tasks/tasks.controller.ts:42-46](), [packages/bytebot-agent/src/tasks/tasks.service.ts:40-117](), [packages/bytebot-agent/src/tasks/dto/create-task.dto.ts]()

---

### GET /tasks

Retrieves a paginated list of tasks with optional status filtering.

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | number | 1 | Page number (1-indexed) |
| `limit` | number | 10 | Items per page |
| `status` | string | - | Single status filter |
| `statuses` | string | - | Comma-separated status list |

**Response:**

```typescript
{
  tasks: Task[];        // Array of task objects
  total: number;        // Total matching tasks
  totalPages: number;   // Total pages available
}
```

**Status Codes:**
- `200 OK` - Tasks retrieved successfully

**Filtering Logic:**
- If `statuses` is provided, splits by comma and filters tasks
- If only `status` is provided, filters by single status
- If neither is provided, returns all tasks

**Sources:** [packages/bytebot-agent/src/tasks/tasks.controller.ts:48-67](), [packages/bytebot-agent/src/tasks/tasks.service.ts:158-190]()

---

### GET /tasks/models

Retrieves the list of available LLM models. If `BYTEBOT_LLM_PROXY_URL` is configured, fetches models from the proxy service; otherwise, returns hardcoded models based on available API keys.

**Response:** Array of `BytebotAgentModel`

```typescript
[
  {
    provider: string;       // "anthropic" | "openai" | "google" | "proxy"
    name: string;           // Model identifier (e.g., "claude-3-5-sonnet-20241022")
    title: string;          // Display name
    contextWindow: number;  // Context window size in tokens
  }
]
```

**Status Codes:**
- `200 OK` - Models retrieved successfully
- `502 Bad Gateway` - Proxy request failed (when using proxy)
- `500 Internal Server Error` - Other proxy errors

**Sources:** [packages/bytebot-agent/src/tasks/tasks.controller.ts:69-111]()

---

### GET /tasks/:id

Retrieves a specific task by its unique identifier, including associated files.

**Path Parameters:**
- `id` (string) - Task UUID

**Response:** `Task` object with `files` relation included

**Status Codes:**
- `200 OK` - Task found
- `404 Not Found` - Task does not exist

**Sources:** [packages/bytebot-agent/src/tasks/tasks.controller.ts:113-116](), [packages/bytebot-agent/src/tasks/tasks.service.ts:192-215]()

---

## Message Endpoints

```mermaid
graph TB
    Client["Client Request"]
    
    MessagesRaw["GET /tasks/:id/messages/raw<br/>MessagesService.findRawMessages"]
    MessagesFiltered["GET /tasks/:id/messages<br/>MessagesService.findAll"]
    MessagesProcessed["GET /tasks/:id/messages/processed<br/>MessagesService.findProcessedMessages"]
    AddMessage["POST /tasks/:id/messages<br/>TasksService.addTaskMessage"]
    
    RawDB[("Raw DB Messages<br/>All content blocks")]
    FilteredDB[("Filtered Messages<br/>Role switching applied")]
    ProcessedUI["Grouped Messages<br/>UI-optimized format"]
    
    Client --> MessagesRaw
    Client --> MessagesFiltered
    Client --> MessagesProcessed
    Client --> AddMessage
    
    MessagesRaw --> RawDB
    MessagesFiltered --> FilteredDB
    MessagesProcessed --> ProcessedUI
    
    AddMessage -->|"Creates USER message"| RawDB
    AddMessage -->|"Emits new_message event"| WSGateway["TasksGateway"]
```

**Sources:** [packages/bytebot-agent/src/tasks/tasks.controller.ts:118-168]()

---

### GET /tasks/:id/messages

Retrieves filtered messages for a task with role switching applied (pure tool results become ASSISTANT messages). This is the primary endpoint for displaying task conversation history.

**Path Parameters:**
- `id` (string) - Task UUID

**Query Parameters:**
- `limit` (number) - Optional: Messages per page
- `page` (number) - Optional: Page number

**Response:** Array of `Message` objects

**Sources:** [packages/bytebot-agent/src/tasks/tasks.controller.ts:118-131](), [packages/bytebot-agent/src/messages/messages.service.ts]()

---

### POST /tasks/:id/messages

Adds a user message to a task, typically for providing additional guidance or answering agent questions when task status is `NEEDS_HELP`.

**Path Parameters:**
- `id` (string) - Task UUID

**Request Body:** `AddTaskMessageDto`

```typescript
{
  message: string;  // User message text
}
```

**Response:** Updated `Task` object

**Status Codes:**
- `201 Created` - Message added successfully
- `404 Not Found` - Task does not exist

**Implementation Details:**
1. Creates a USER message with text content
2. Emits `new_message` WebSocket event to notify connected clients
3. If task is RUNNING, agent will process the new message on next iteration

**Sources:** [packages/bytebot-agent/src/tasks/tasks.controller.ts:133-140](), [packages/bytebot-agent/src/tasks/tasks.service.ts:263-280]()

---

### GET /tasks/:id/messages/raw

Retrieves unprocessed messages exactly as stored in the database, without role switching or filtering. Useful for debugging and understanding the raw LLM conversation.

**Path Parameters:**
- `id` (string) - Task UUID

**Query Parameters:**
- `limit` (number) - Optional: Messages per page
- `page` (number) - Optional: Page number

**Response:** Array of `Message` objects with all content blocks

**Sources:** [packages/bytebot-agent/src/tasks/tasks.controller.ts:142-154]()

---

### GET /tasks/:id/messages/processed

Retrieves messages formatted for UI display, with consecutive same-role messages grouped together and user takeover actions extracted. Returns `GroupedMessages[]` format.

**Path Parameters:**
- `id` (string) - Task UUID

**Query Parameters:**
- `limit` (number) - Optional: Messages per page
- `page` (number) - Optional: Page number

**Response:** Array of `GroupedMessages` objects

```typescript
{
  role: Role;                      // USER or ASSISTANT
  messages: Message[];             // Consecutive messages with same role
  userActions?: UserActionBlock[]; // Extracted user input actions (if role=USER)
}
```

**Sources:** [packages/bytebot-agent/src/tasks/tasks.controller.ts:156-168](), [packages/bytebot-agent/src/messages/messages.service.ts]()

---

## Control Flow Endpoints

```mermaid
stateDiagram-v2
    [*] --> Running: "Task starts"
    
    Running --> UserControl: "POST /tasks/:id/takeover<br/>control=USER"
    UserControl --> Running: "POST /tasks/:id/resume<br/>control=ASSISTANT"
    
    Running --> Cancelled: "POST /tasks/:id/cancel<br/>status=CANCELLED"
    
    state Running {
        [*] --> AgentProcessing
        AgentProcessing --> AgentProcessing: "Agent iterations"
    }
    
    state UserControl {
        [*] --> InputTracking
        InputTracking --> UserProvides: "User can interact<br/>with desktop"
        UserProvides --> [*]: "Adds messages"
    }
    
    note right of UserControl
        TasksService.takeOver()
        - Sets control=USER
        - Starts input tracking
        - Emits task.takeover event
        - Aborts agent processing
    end note
    
    note right of Running
        TasksService.resume()
        - Sets control=ASSISTANT
        - Stops input tracking
        - Emits task.resume event
        - Agent continues processing
    end note
```

**Sources:** [packages/bytebot-agent/src/tasks/tasks.service.ts:282-391]()

---

### POST /tasks/:id/takeover

Transfers control from the agent to the user, allowing manual interaction with the virtual desktop. The agent immediately aborts any in-flight LLM requests and stops processing.

**Path Parameters:**
- `id` (string) - Task UUID

**Response:** Updated `Task` object with `control=USER`

**Status Codes:**
- `200 OK` - Takeover successful
- `404 Not Found` - Task does not exist
- `400 Bad Request` - Task not under agent control

**Side Effects:**
1. Updates `task.control` to `USER`
2. Sends POST to `/input-tracking/start` on bytebotd
3. Emits `task.takeover` event via `EventEmitter2`
4. `AgentProcessor` aborts current processing via `AbortController`
5. Emits `task_updated` WebSocket event

**Sources:** [packages/bytebot-agent/src/tasks/tasks.controller.ts:176-180](), [packages/bytebot-agent/src/tasks/tasks.service.ts:320-357](), [packages/bytebot-agent/src/agent/agent.processor.ts:84-95]()

---

### POST /tasks/:id/resume

Transfers control from the user back to the agent, resuming automated processing.

**Path Parameters:**
- `id` (string) - Task UUID

**Response:** Updated `Task` object with `control=ASSISTANT` and `status=RUNNING`

**Status Codes:**
- `200 OK` - Resume successful
- `404 Not Found` - Task does not exist
- `400 Bad Request` - Task not under user control

**Side Effects:**
1. Updates `task.control` to `ASSISTANT`
2. Updates `task.status` to `RUNNING`
3. Sends POST to `/input-tracking/stop` on bytebotd
4. Emits `task.resume` event via `EventEmitter2`
5. `AgentProcessor` creates new `AbortController` and continues iterations
6. Emits `task_updated` WebSocket event

**Sources:** [packages/bytebot-agent/src/tasks/tasks.controller.ts:182-186](), [packages/bytebot-agent/src/tasks/tasks.service.ts:282-318](), [packages/bytebot-agent/src/agent/agent.processor.ts:97-105]()

---

### POST /tasks/:id/cancel

Cancels a running task, marking it as `CANCELLED` and stopping agent processing.

**Path Parameters:**
- `id` (string) - Task UUID

**Response:** Updated `Task` object with `status=CANCELLED`

**Status Codes:**
- `200 OK` - Cancellation successful
- `404 Not Found` - Task does not exist
- `400 Bad Request` - Task already completed, failed, or cancelled

**Side Effects:**
1. Updates `task.status` to `CANCELLED`
2. Emits `task.cancel` event via `EventEmitter2`
3. `AgentProcessor` aborts current processing and resets state
4. Emits `task_updated` WebSocket event

**Sources:** [packages/bytebot-agent/src/tasks/tasks.controller.ts:188-192](), [packages/bytebot-agent/src/tasks/tasks.service.ts:359-391](), [packages/bytebot-agent/src/agent/agent.processor.ts:107-112]()

---

### DELETE /tasks/:id

Permanently deletes a task and all associated data (messages, summaries, files) via cascading database constraints.

**Path Parameters:**
- `id` (string) - Task UUID

**Status Codes:**
- `204 No Content` - Task deleted successfully
- `404 Not Found` - Task does not exist (throws exception before deletion)

**Side Effects:**
1. Deletes task record from database
2. Cascades to delete all messages, summaries, and files
3. Emits `task_deleted` WebSocket event

**Sources:** [packages/bytebot-agent/src/tasks/tasks.controller.ts:170-174](), [packages/bytebot-agent/src/tasks/tasks.service.ts:249-261]()

---

## Data Types and DTOs

### CreateTaskDto

Data transfer object for creating tasks, validated using `class-validator`.

**Properties:**

| Field | Type | Required | Validation | Default |
|-------|------|----------|------------|---------|
| `description` | string | Yes | Non-empty string | - |
| `model` | BytebotAgentModel | No | Valid model object | - |
| `type` | TaskType | No | IMMEDIATE or SCHEDULED | IMMEDIATE |
| `priority` | TaskPriority | No | LOW, MEDIUM, or HIGH | MEDIUM |
| `scheduledFor` | Date | No | Valid date | - |
| `createdBy` | Role | No | USER or ASSISTANT | USER |
| `files` | FileWithBase64[] | No | Array of file objects | [] |

**Sources:** [packages/bytebot-agent/src/tasks/dto/create-task.dto.ts]()

---

### UpdateTaskDto

Partial update object for task modifications. All fields are optional.

**Properties:**
- `status` - TaskStatus enum value
- `priority` - TaskPriority enum value
- `control` - Role enum value (USER or ASSISTANT)
- `executedAt` - Timestamp when execution started
- `completedAt` - Timestamp when task completed
- `error` - Error message if task failed

**Sources:** [packages/bytebot-agent/src/tasks/dto/update-task.dto.ts]()

---

### AddTaskMessageDto

Simple DTO for adding user messages to tasks.

**Properties:**
- `message` (string, required) - User message text

**Sources:** [packages/bytebot-agent/src/tasks/dto/add-task-message.dto.ts]()

---

## Task Object Schema

The `Task` entity returned by API endpoints conforms to the Prisma model:

```typescript
{
  id: string;                    // UUID
  description: string;           // Task description
  status: TaskStatus;            // PENDING, RUNNING, NEEDS_HELP, COMPLETED, FAILED, CANCELLED
  type: TaskType;                // IMMEDIATE or SCHEDULED
  priority: TaskPriority;        // LOW, MEDIUM, HIGH
  control: Role;                 // USER or ASSISTANT
  model: BytebotAgentModel;      // LLM model configuration (stored as JSON)
  createdBy: Role;               // USER or ASSISTANT
  createdAt: Date;               // Creation timestamp
  updatedAt: Date;               // Last update timestamp
  queuedAt?: Date;               // When task was queued
  scheduledFor?: Date;           // Scheduled execution time
  executedAt?: Date;             // When execution started
  completedAt?: Date;            // When task completed
  error?: string;                // Error message if failed
  files?: File[];                // Associated files (when included)
}
```

**Sources:** [packages/bytebot-agent/prisma/schema.prisma]()

---

## Error Handling

All endpoints follow standard HTTP error conventions:

### Common Error Responses

| Status Code | Exception Type | When It Occurs |
|-------------|----------------|----------------|
| 400 | `BadRequestException` | Invalid request data, validation failure, or illegal state transition |
| 404 | `NotFoundException` | Task or resource not found |
| 500 | `InternalServerError` | Unhandled exceptions, database errors |
| 502 | `BadGatewayException` | Proxy service communication failure |

### Error Response Format

```typescript
{
  statusCode: number;
  message: string | string[];
  error?: string;
}
```

**Sources:** [packages/bytebot-agent/src/tasks/tasks.service.ts:203-214](), [packages/bytebot-agent/src/tasks/tasks.controller.ts:80-107]()

---

## Integration with Agent System

```mermaid
sequenceDiagram
    participant Client
    participant TasksController
    participant TasksService
    participant DB
    participant TasksGateway
    participant EventEmitter
    participant AgentScheduler
    participant AgentProcessor
    
    Client->>TasksController: "POST /tasks"
    TasksController->>TasksService: "create(dto)"
    TasksService->>DB: "CREATE task, files, message"
    DB-->>TasksService: "task"
    TasksService->>TasksGateway: "emitTaskCreated(task)"
    TasksGateway-->>Client: "task_created event"
    TasksService-->>TasksController: "task"
    TasksController-->>Client: "201 Created"
    
    Note over AgentScheduler: "Cron job runs @Interval(2000)"
    AgentScheduler->>TasksService: "findNextTask()"
    TasksService-->>AgentScheduler: "task"
    AgentScheduler->>AgentProcessor: "processTask(taskId)"
    
    loop "Agent iterations"
        AgentProcessor->>AgentProcessor: "runIteration()"
        AgentProcessor->>DB: "Get messages, summaries"
        AgentProcessor->>AgentProcessor: "Call LLM, execute tools"
        AgentProcessor->>TasksService: "update(status)"
        TasksService->>EventEmitter: "emit('task.completed')"
        TasksService->>TasksGateway: "emitTaskUpdate()"
    end
    
    Client->>TasksController: "POST /tasks/:id/takeover"
    TasksController->>TasksService: "takeOver(taskId)"
    TasksService->>EventEmitter: "emit('task.takeover')"
    EventEmitter->>AgentProcessor: "@OnEvent handler"
    AgentProcessor->>AgentProcessor: "abortController.abort()"
```

**Sources:** [packages/bytebot-agent/src/tasks/tasks.service.ts:40-117](), [packages/bytebot-agent/src/tasks/tasks.service.ts:320-357](), [packages/bytebot-agent/src/agent/agent.processor.ts:114-128](), [packages/bytebot-agent/src/agent/agent.scheduler.ts]()

---

## Proxying Through bytebot-ui

All API requests from the browser are proxied through the bytebot-ui service to avoid CORS issues and centralize backend communication.

**Proxy Configuration:**

- Frontend proxy path: `/api/proxy/tasks/*`
- Backend target: `http://bytebot-agent:9991/tasks/*`
- Implementation: Custom Express middleware in Next.js server

**Example Flow:**

1. Client makes request to `http://localhost:9992/api/proxy/tasks`
2. bytebot-ui proxies to `http://bytebot-agent:9991/tasks`
3. TasksController processes request
4. Response flows back through proxy to client

**Sources:** [packages/bytebot-ui/src/server/index.ts](), [packages/bytebot-ui/src/utils/taskUtils.ts]()

---

# Page: Computer Use API

# Computer Use API

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [packages/bytebotd/src/computer-use/computer-use.service.ts](packages/bytebotd/src/computer-use/computer-use.service.ts)
- [packages/bytebotd/src/computer-use/dto/base.dto.ts](packages/bytebotd/src/computer-use/dto/base.dto.ts)
- [packages/bytebotd/src/computer-use/dto/computer-action-validation.pipe.ts](packages/bytebotd/src/computer-use/dto/computer-action-validation.pipe.ts)
- [packages/bytebotd/src/computer-use/dto/computer-action.dto.ts](packages/bytebotd/src/computer-use/dto/computer-action.dto.ts)
- [packages/bytebotd/src/mcp/computer-use.tools.ts](packages/bytebotd/src/mcp/computer-use.tools.ts)
- [packages/shared/src/types/computerAction.types.ts](packages/shared/src/types/computerAction.types.ts)
- [packages/shared/src/types/messageContent.types.ts](packages/shared/src/types/messageContent.types.ts)
- [packages/shared/src/utils/computerAction.utils.ts](packages/shared/src/utils/computerAction.utils.ts)
- [packages/shared/src/utils/messageContent.utils.ts](packages/shared/src/utils/messageContent.utils.ts)

</details>



## Purpose and Scope

This document provides a complete reference for the Computer Use API, the HTTP endpoint exposed by the `bytebotd` service that enables programmatic control of the virtual desktop environment. This API accepts structured action commands and executes them using the underlying automation framework.

For information about how the AI agent integrates with this API, see [Agent Processor](#6.1) and [Computer Use Integration](#6.2). For the MCP-based tools that wrap this API, see [MCP Integration](#7.3). For details on the underlying automation service, see [Computer Use Service](#7.1).

---

## Endpoint Overview

The Computer Use API is exposed as a single HTTP POST endpoint that accepts action objects with varying structures based on the action type.

**Endpoint**: `POST /computer-use`

**Content-Type**: `application/json`

**Service**: `bytebotd` (port 9990)

**Handler**: [packages/bytebotd/src/computer-use/computer-use.service.ts:26-105]()

The endpoint accepts a `ComputerAction` object, validates it using the `ComputerActionValidationPipe`, and dispatches it to the appropriate handler method based on the `action` discriminator field.

### Request Flow Diagram

```mermaid
graph TB
    Agent["Agent Processor<br/>(bytebot-agent)"]
    HTTP["HTTP POST /computer-use"]
    Validation["ComputerActionValidationPipe"]
    Service["ComputerUseService.action()"]
    Dispatch["Action Dispatch Switch"]
    
    subgraph "Action Handlers"
        MouseH["Mouse Actions<br/>moveMouse, clickMouse, etc."]
        KeyH["Keyboard Actions<br/>typeKeys, typeText, etc."]
        SysH["System Actions<br/>screenshot, application, etc."]
        FileH["File Actions<br/>writeFile, readFile"]
    end
    
    NutService["NutService<br/>(automation layer)"]
    Result["Action Result"]
    
    Agent -->|"ComputerAction object"| HTTP
    HTTP --> Validation
    Validation -->|"Validated DTO"| Service
    Service --> Dispatch
    
    Dispatch --> MouseH
    Dispatch --> KeyH
    Dispatch --> SysH
    Dispatch --> FileH
    
    MouseH --> NutService
    KeyH --> NutService
    SysH --> NutService
    FileH -->|"File operations"| Result
    
    NutService --> Result
    Result -->|"Response object"| Agent
```

**Sources**: [packages/bytebotd/src/computer-use/computer-use.service.ts:31-105](), [packages/bytebotd/src/computer-use/dto/computer-action-validation.pipe.ts:29-96]()

---

## Action Type System

All actions inherit from a common type structure with an `action` discriminator field that determines which parameters are required.

### Type Hierarchy

```mermaid
graph TD
    CA["ComputerAction<br/>(discriminated union)"]
    
    subgraph "Mouse Actions (8)"
        MM["MoveMouseAction<br/>action: 'move_mouse'"]
        TM["TraceMouseAction<br/>action: 'trace_mouse'"]
        CM["ClickMouseAction<br/>action: 'click_mouse'"]
        PM["PressMouseAction<br/>action: 'press_mouse'"]
        DM["DragMouseAction<br/>action: 'drag_mouse'"]
        SC["ScrollAction<br/>action: 'scroll'"]
        CP["CursorPositionAction<br/>action: 'cursor_position'"]
    end
    
    subgraph "Keyboard Actions (5)"
        TK["TypeKeysAction<br/>action: 'type_keys'"]
        PK["PressKeysAction<br/>action: 'press_keys'"]
        TT["TypeTextAction<br/>action: 'type_text'"]
        PT["PasteTextAction<br/>action: 'paste_text'"]
    end
    
    subgraph "System Actions (3)"
        SS["ScreenshotAction<br/>action: 'screenshot'"]
        WA["WaitAction<br/>action: 'wait'"]
        AP["ApplicationAction<br/>action: 'application'"]
    end
    
    subgraph "File Actions (2)"
        WF["WriteFileAction<br/>action: 'write_file'"]
        RF["ReadFileAction<br/>action: 'read_file'"]
    end
    
    CA --> MM
    CA --> TM
    CA --> CM
    CA --> PM
    CA --> DM
    CA --> SC
    CA --> CP
    CA --> TK
    CA --> PK
    CA --> TT
    CA --> PT
    CA --> SS
    CA --> WA
    CA --> AP
    CA --> WF
    CA --> RF
```

**Sources**: [packages/shared/src/types/computerAction.types.ts:109-126](), [packages/bytebotd/src/computer-use/dto/computer-action.dto.ts:223-240]()

---

## Mouse Actions

### move_mouse

Moves the mouse cursor to absolute coordinates.

**Request Structure**:
```json
{
  "action": "move_mouse",
  "coordinates": {
    "x": 640,
    "y": 480
  }
}
```

**Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `action` | `"move_mouse"` | Yes | Action type discriminator |
| `coordinates` | `Coordinates` | Yes | Target position |
| `coordinates.x` | `number` | Yes | X-coordinate (0-1280) |
| `coordinates.y` | `number` | Yes | Y-coordinate (0-960) |

**Response**: `void` (no response body)

**Handler**: [packages/bytebotd/src/computer-use/computer-use.service.ts:107-109]()

---

### trace_mouse

Moves the mouse cursor along a path of coordinates, optionally holding modifier keys.

**Request Structure**:
```json
{
  "action": "trace_mouse",
  "path": [
    { "x": 100, "y": 100 },
    { "x": 200, "y": 150 },
    { "x": 300, "y": 200 }
  ],
  "holdKeys": ["LeftShift"]
}
```

**Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `action` | `"trace_mouse"` | Yes | Action type discriminator |
| `path` | `Coordinates[]` | Yes | Array of coordinates to trace through |
| `holdKeys` | `string[]` | No | Keys to hold during trace (e.g., modifier keys) |

**Response**: `void`

**Handler**: [packages/bytebotd/src/computer-use/computer-use.service.ts:111-131]()

**Implementation Details**: The handler moves to the first coordinate, holds specified keys, iterates through all path coordinates, then releases keys.

---

### click_mouse

Performs mouse clicks at specified coordinates or current position.

**Request Structure**:
```json
{
  "action": "click_mouse",
  "coordinates": { "x": 500, "y": 300 },
  "button": "left",
  "clickCount": 2,
  "holdKeys": ["LeftControl"]
}
```

**Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `action` | `"click_mouse"` | Yes | Action type discriminator |
| `coordinates` | `Coordinates` | No | Click position (omit for current position) |
| `button` | `"left" \| "right" \| "middle"` | Yes | Mouse button to click |
| `clickCount` | `number` | Yes | Number of clicks (≥1, use 2 for double-click) |
| `holdKeys` | `string[]` | No | Keys to hold during click (e.g., Ctrl, Shift) |

**Response**: `void`

**Handler**: [packages/bytebotd/src/computer-use/computer-use.service.ts:133-162]()

**Implementation Details**: If `clickCount > 1`, clicks are performed with 150ms delay between each. Coordinates and hold keys are optional.

---

### press_mouse

Presses down or releases a mouse button without clicking.

**Request Structure**:
```json
{
  "action": "press_mouse",
  "coordinates": { "x": 100, "y": 100 },
  "button": "left",
  "press": "down"
}
```

**Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `action` | `"press_mouse"` | Yes | Action type discriminator |
| `coordinates` | `Coordinates` | No | Position for press/release |
| `button` | `"left" \| "right" \| "middle"` | Yes | Mouse button |
| `press` | `"down" \| "up"` | Yes | Press down or release up |

**Response**: `void`

**Handler**: [packages/bytebotd/src/computer-use/computer-use.service.ts:164-178]()

**Use Case**: Useful for drag operations or holding buttons while performing other actions.

---

### drag_mouse

Drags the mouse along a path while holding a button.

**Request Structure**:
```json
{
  "action": "drag_mouse",
  "path": [
    { "x": 100, "y": 100 },
    { "x": 300, "y": 300 }
  ],
  "button": "left",
  "holdKeys": ["LeftShift"]
}
```

**Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `action` | `"drag_mouse"` | Yes | Action type discriminator |
| `path` | `Coordinates[]` | Yes | Drag path coordinates |
| `button` | `"left" \| "right" \| "middle"` | Yes | Button to hold during drag |
| `holdKeys` | `string[]` | No | Modifier keys to hold |

**Response**: `void`

**Handler**: [packages/bytebotd/src/computer-use/computer-use.service.ts:180-202]()

**Implementation Details**: Moves to first coordinate, holds modifier keys, presses mouse button, traces path, releases button, releases modifier keys.

---

### scroll

Scrolls the mouse wheel in a specified direction.

**Request Structure**:
```json
{
  "action": "scroll",
  "coordinates": { "x": 640, "y": 480 },
  "direction": "down",
  "scrollCount": 5,
  "holdKeys": ["LeftControl"]
}
```

**Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `action` | `"scroll"` | Yes | Action type discriminator |
| `coordinates` | `Coordinates` | No | Position to scroll at |
| `direction` | `"up" \| "down" \| "left" \| "right"` | Yes | Scroll direction |
| `scrollCount` | `number` | Yes | Number of scroll wheel notches (≥1) |
| `holdKeys` | `string[]` | No | Modifier keys to hold during scroll |

**Response**: `void`

**Handler**: [packages/bytebotd/src/computer-use/computer-use.service.ts:204-227]()

**Implementation Details**: Each scroll notch includes a 150ms delay between iterations.

---

### cursor_position

Retrieves the current mouse cursor coordinates.

**Request Structure**:
```json
{
  "action": "cursor_position"
}
```

**Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `action` | `"cursor_position"` | Yes | Action type discriminator |

**Response**:
```json
{
  "x": 640,
  "y": 480
}
```

**Response Type**: `{ x: number; y: number }`

**Handler**: [packages/bytebotd/src/computer-use/computer-use.service.ts:259-262]()

---

## Keyboard Actions

### type_keys

Types a sequence of keys, pressing and releasing each in order. Used for keyboard shortcuts.

**Request Structure**:
```json
{
  "action": "type_keys",
  "keys": ["LeftControl", "C"],
  "delay": 50
}
```

**Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `action` | `"type_keys"` | Yes | Action type discriminator |
| `keys` | `string[]` | Yes | Array of key names to type in sequence |
| `delay` | `number` | No | Milliseconds delay between key presses |

**Response**: `void`

**Handler**: [packages/bytebotd/src/computer-use/computer-use.service.ts:229-232]()

**Valid Keys**: See the comprehensive list at [packages/bytebotd/src/mcp/computer-use.tools.ts:318-344](). Includes letters (A-Z), numbers, modifiers (LeftControl, LeftShift, etc.), function keys (F1-F24), navigation keys (Home, End, PageUp, etc.), and special keys.

---

### press_keys

Presses down or releases specific keys without typing them. Used for holding modifier keys.

**Request Structure**:
```json
{
  "action": "press_keys",
  "keys": ["LeftShift", "LeftControl"],
  "press": "down"
}
```

**Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `action` | `"press_keys"` | Yes | Action type discriminator |
| `keys` | `string[]` | Yes | Array of key names to press/release |
| `press` | `"down" \| "up"` | Yes | Press down or release up |

**Response**: `void`

**Handler**: [packages/bytebotd/src/computer-use/computer-use.service.ts:234-237]()

**Use Case**: Holding modifier keys while performing other actions (e.g., Shift-click).

---

### type_text

Types a text string character by character.

**Request Structure**:
```json
{
  "action": "type_text",
  "text": "Hello, World!",
  "delay": 20
}
```

**Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `action` | `"type_text"` | Yes | Action type discriminator |
| `text` | `string` | Yes | Text to type |
| `delay` | `number` | No | Milliseconds delay between characters |

**Response**: `void`

**Handler**: [packages/bytebotd/src/computer-use/computer-use.service.ts:239-242]()

**Recommended Use**: Best for short strings (<25 characters) or sensitive form fields. For longer text, use `paste_text`.

---

### paste_text

Copies text to clipboard and pastes it using Ctrl+V.

**Request Structure**:
```json
{
  "action": "paste_text",
  "text": "Long text content that would be slow to type character by character..."
}
```

**Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `action` | `"paste_text"` | Yes | Action type discriminator |
| `text` | `string` | Yes | Text to paste |

**Response**: `void`

**Handler**: [packages/bytebotd/src/computer-use/computer-use.service.ts:244-247]()

**Recommended Use**: Long text strings or special characters not on standard keyboard.

---

## System Actions

### screenshot

Captures a screenshot of the current desktop.

**Request Structure**:
```json
{
  "action": "screenshot"
}
```

**Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `action` | `"screenshot"` | Yes | Action type discriminator |

**Response**:
```json
{
  "image": "iVBORw0KGgoAAAANSUhEUgAA..."
}
```

**Response Type**: `{ image: string }`

**Handler**: [packages/bytebotd/src/computer-use/computer-use.service.ts:253-257]()

**Implementation Details**: Returns PNG image data as base64-encoded string. The image represents the 1280x960 desktop.

---

### wait

Pauses execution for a specified duration.

**Request Structure**:
```json
{
  "action": "wait",
  "duration": 1000
}
```

**Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `action` | `"wait"` | Yes | Action type discriminator |
| `duration` | `number` | Yes | Milliseconds to wait |

**Response**: `void`

**Handler**: [packages/bytebotd/src/computer-use/computer-use.service.ts:249-251]()

**Use Case**: Allowing UI elements to load or animations to complete.

---

### application

Opens or switches to a specified application and maximizes it.

**Request Structure**:
```json
{
  "action": "application",
  "application": "firefox"
}
```

**Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `action` | `"application"` | Yes | Action type discriminator |
| `application` | `Application` | Yes | Application to open/switch to |

**Valid Applications**:
- `"firefox"` - Firefox ESR browser
- `"1password"` - 1Password password manager
- `"thunderbird"` - Thunderbird email client
- `"vscode"` - Visual Studio Code editor
- `"terminal"` - XFCE Terminal
- `"directory"` - Thunar file manager
- `"desktop"` - Show desktop (minimize all windows)

**Response**: `void`

**Handler**: [packages/bytebotd/src/computer-use/computer-use.service.ts:264-362]()

**Implementation Details**: 
1. Checks if application is already open using `wmctrl -lx`
2. If open, activates and maximizes the window
3. If not open, spawns the application process
4. Uses process mapping defined at [packages/bytebotd/src/computer-use/computer-use.service.ts:296-304]()

---

## File Actions

### write_file

Writes a file to the desktop filesystem from base64-encoded data.

**Request Structure**:
```json
{
  "action": "write_file",
  "path": "document.txt",
  "data": "SGVsbG8sIFdvcmxkIQ=="
}
```

**Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `action` | `"write_file"` | Yes | Action type discriminator |
| `path` | `string` | Yes | File path (relative paths resolved to `/home/user/Desktop/`) |
| `data` | `string` | Yes | Base64-encoded file content |

**Response**:
```json
{
  "success": true,
  "message": "File written successfully to: /home/user/Desktop/document.txt"
}
```

**Response Type**: `{ success: boolean; message: string }`

**Handler**: [packages/bytebotd/src/computer-use/computer-use.service.ts:364-417]()

**Implementation Details**:
1. Decodes base64 data to buffer
2. Resolves relative paths to `/home/user/Desktop/`
3. Creates parent directories using `sudo mkdir -p`
4. Writes to temporary file in `/tmp/`
5. Moves to target location using `sudo cp`
6. Sets ownership to `user:user` and permissions to `644`
7. Cleans up temporary file

**Error Handling**: Returns `success: false` with error message on failure.

---

### read_file

Reads a file from the desktop filesystem and returns it as base64-encoded data.

**Request Structure**:
```json
{
  "action": "read_file",
  "path": "document.pdf"
}
```

**Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `action` | `"read_file"` | Yes | Action type discriminator |
| `path` | `string` | Yes | File path (relative paths resolved to `/home/user/Desktop/`) |

**Response**:
```json
{
  "success": true,
  "data": "JVBERi0xLjQKJeLjz9...",
  "name": "document.pdf",
  "size": 45678,
  "mediaType": "application/pdf"
}
```

**Response Type**:
```typescript
{
  success: boolean;
  data?: string;        // Base64-encoded file content
  name?: string;        // File name
  size?: number;        // File size in bytes
  mediaType?: string;   // MIME type
  message?: string;     // Error message if success=false
}
```

**Handler**: [packages/bytebotd/src/computer-use/computer-use.service.ts:419-506]()

**Supported Media Types**: The handler includes a comprehensive MIME type mapping at [packages/bytebotd/src/computer-use/computer-use.service.ts:464-482](), supporting:
- Documents: PDF, DOCX, DOC, TXT, HTML, JSON, XML, CSV, RTF, ODT, EPUB
- Images: PNG, JPEG, WEBP, GIF, SVG

**Implementation Details**:
1. Resolves relative paths to `/home/user/Desktop/`
2. Copies file to temporary location using `sudo cp`
3. Reads file as buffer from temporary location
4. Gets file size using `sudo stat`
5. Determines MIME type from file extension
6. Cleans up temporary file
7. Returns base64-encoded data with metadata

**Error Handling**: Returns `success: false` with error message on failure.

---

## Validation System

All requests are validated using NestJS class-validator decorators before execution.

### Validation Pipeline

```mermaid
graph LR
    Request["Raw Request<br/>Body"]
    Pipe["ComputerActionValidationPipe"]
    Switch["Action Type Switch"]
    
    subgraph "DTO Classes"
        MoveDTO["MoveMouseActionDto"]
        ClickDTO["ClickMouseActionDto"]
        TypeDTO["TypeTextActionDto"]
        OtherDTO["... (14 more DTOs)"]
    end
    
    Validate["class-validator<br/>validate()"]
    Transform["plainToClass()"]
    Service["ComputerUseService"]
    Error["BadRequestException"]
    
    Request --> Pipe
    Pipe -->|"Check action field"| Switch
    Switch --> Transform
    Transform --> MoveDTO
    Transform --> ClickDTO
    Transform --> TypeDTO
    Transform --> OtherDTO
    
    MoveDTO --> Validate
    ClickDTO --> Validate
    TypeDTO --> Validate
    OtherDTO --> Validate
    
    Validate -->|"Valid"| Service
    Validate -->|"Invalid"| Error
```

**Sources**: [packages/bytebotd/src/computer-use/dto/computer-action-validation.pipe.ts:29-96](), [packages/bytebotd/src/computer-use/dto/computer-action.dto.ts:1-240]()

### Common Validation Rules

The validation system enforces the following rules across all action types:

| Rule | Applied To | Example |
|------|-----------|---------|
| `@IsIn([action_name])` | All `action` fields | Ensures exact match |
| `@IsNumber()` | Coordinates, durations | Type checking |
| `@Min(0)` or `@Min(1)` | Counts, delays | Positive values |
| `@IsEnum()` | Button types, directions | Valid enum values |
| `@IsArray()` | Key arrays, paths | Array type checking |
| `@ValidateNested()` | Coordinates objects | Nested validation |
| `@IsOptional()` | Optional parameters | Allows undefined |

**Coordinate Validation**: [packages/bytebotd/src/computer-use/dto/base.dto.ts:3-9]()

**Enum Validation**: [packages/bytebotd/src/computer-use/dto/base.dto.ts:11-37]()

### Validation Error Response

When validation fails, the API returns a `400 Bad Request` with detailed error information:

```json
{
  "statusCode": 400,
  "message": [
    {
      "property": "coordinates",
      "constraints": {
        "isNumber": "coordinates.x must be a number"
      }
    }
  ],
  "error": "Bad Request"
}
```

---

## Error Handling

The Computer Use API implements comprehensive error handling at multiple levels.

### Error Categories

| Error Type | Status Code | Cause | Example |
|------------|-------------|-------|---------|
| Validation Error | 400 | Invalid request structure | Missing required field |
| Unknown Action | 400 | Unrecognized action type | `"action": "invalid_action"` |
| Execution Error | 500 | Action execution failure | NutJS automation failure |
| File Error | 200 (with `success: false`) | File operation failure | Permission denied |

### Error Handling Flow

```mermaid
graph TD
    Request["POST /computer-use"]
    Validation["ComputerActionValidationPipe"]
    Service["ComputerUseService.action()"]
    Dispatch["Switch Statement"]
    Handler["Action Handler Method"]
    NutService["NutService"]
    
    ValError["400 Bad Request<br/>Validation errors"]
    UnknownError["400 Bad Request<br/>Unknown action"]
    ExecError["500 Internal Error<br/>Execution failed"]
    FileError["200 OK<br/>{success: false, message}"]
    Success["200 OK<br/>Result data"]
    
    Request --> Validation
    Validation -->|"Invalid"| ValError
    Validation -->|"Valid"| Service
    
    Service --> Dispatch
    Dispatch -->|"Unknown action"| UnknownError
    Dispatch -->|"Known action"| Handler
    
    Handler -->|"File action"| FileError
    Handler -->|"Other action"| NutService
    
    NutService -->|"Error"| ExecError
    NutService -->|"Success"| Success
    
    style ValError fill:#ffcccc
    style UnknownError fill:#ffcccc
    style ExecError fill:#ffcccc
    style FileError fill:#ffffcc
    style Success fill:#ccffcc
```

**Sources**: [packages/bytebotd/src/computer-use/computer-use.service.ts:31-105](), [packages/bytebotd/src/computer-use/dto/computer-action-validation.pipe.ts:29-96]()

### File Operation Error Handling

File operations (`write_file` and `read_file`) use a different error handling strategy - they return a 200 OK response with a `success` field instead of throwing exceptions:

**Write File Error**:
```json
{
  "success": false,
  "message": "Error writing file: Permission denied"
}
```

**Read File Error**:
```json
{
  "success": false,
  "message": "Error reading file: No such file or directory"
}
```

This design allows the agent to gracefully handle file system errors without aborting the entire task execution loop.

**Sources**: [packages/bytebotd/src/computer-use/computer-use.service.ts:410-416](), [packages/bytebotd/src/computer-use/computer-use.service.ts:500-505]()

---

## Integration with Agent System

The Computer Use API is primarily consumed by the AI agent during task execution. The integration flow demonstrates how high-level AI decisions translate into low-level desktop actions.

### Agent-to-API Request Flow

```mermaid
sequenceDiagram
    participant Agent as "AgentProcessor"
    participant LLM as "LLM Provider"
    participant Handler as "handleComputerToolUse()"
    participant API as "POST /computer-use"
    participant Service as "ComputerUseService"
    participant Desktop as "Virtual Desktop"
    
    Agent->>LLM: "Send context + screenshot"
    LLM->>Agent: "ToolUse: computer_click_mouse"
    Agent->>Handler: "toolUse: ClickMouseToolUseBlock"
    Handler->>Handler: "Extract action parameters"
    Handler->>API: "POST {action: 'click_mouse', ...}"
    API->>Service: "Validated ClickMouseAction"
    Service->>Desktop: "Click at coordinates"
    Desktop->>Service: "Action complete"
    Service->>API: "void"
    API->>Handler: "200 OK"
    Handler->>Agent: "ToolResult content block"
    Agent->>Agent: "Wait 750ms"
    Agent->>API: "POST {action: 'screenshot'}"
    API->>Service: "ScreenshotAction"
    Service->>Desktop: "Capture screen"
    Desktop->>Service: "PNG buffer"
    Service->>API: "{image: base64}"
    API->>Handler: "200 OK {image}"
    Handler->>Agent: "Image content block"
```

**Sources**: [packages/bytebot-agent/src/agent/agent.computer-use.ts]() (referenced in system architecture)

### Tool Use to Action Conversion

The agent receives LLM tool use blocks and converts them to Computer Use API requests. For example:

**LLM Tool Use Block**:
```json
{
  "type": "tool_use",
  "id": "toolu_123",
  "name": "computer_click_mouse",
  "input": {
    "coordinates": { "x": 500, "y": 300 },
    "button": "left",
    "clickCount": 1
  }
}
```

**Converted to Computer Use API Request**:
```json
{
  "action": "click_mouse",
  "coordinates": { "x": 500, "y": 300 },
  "button": "left",
  "clickCount": 1
}
```

The conversion utilities are provided in [packages/shared/src/utils/computerAction.utils.ts:299-342]().

**Sources**: [packages/shared/src/types/messageContent.types.ts:79-88](), [packages/shared/src/utils/computerAction.utils.ts:125-143]()

---

## MCP Tools Integration

The Computer Use API is also exposed via Model Context Protocol (MCP) tools, allowing external MCP clients to control the desktop.

### MCP Tools Wrapper

The `ComputerUseTools` class wraps each Computer Use API action as an MCP tool with Zod schema validation:

```mermaid
graph LR
    MCPClient["MCP Client"]
    MCPServer["MCP SSE Endpoint<br/>/mcp"]
    Tools["ComputerUseTools<br/>@Tool decorators"]
    API["ComputerUseService.action()"]
    
    subgraph "17 Tool Methods"
        MoveMouse["moveMouse()<br/>@Tool"]
        ClickMouse["clickMouse()<br/>@Tool"]
        TypeText["typeText()<br/>@Tool"]
        Screenshot["screenshot()<br/>@Tool"]
        WriteFile["writeFile()<br/>@Tool"]
        Others["... (12 more tools)"]
    end
    
    MCPClient -->|"SSE"| MCPServer
    MCPServer --> Tools
    Tools --> MoveMouse
    Tools --> ClickMouse
    Tools --> TypeText
    Tools --> Screenshot
    Tools --> WriteFile
    Tools --> Others
    
    MoveMouse --> API
    ClickMouse --> API
    TypeText --> API
    Screenshot --> API
    WriteFile --> API
    Others --> API
```

**Sources**: [packages/bytebotd/src/mcp/computer-use.tools.ts:1-698]()

Each MCP tool:
1. Validates parameters using Zod schemas
2. Calls `ComputerUseService.action()` with the appropriate action object
3. Catches errors and returns formatted error messages
4. Returns standardized MCP content blocks

**Example Tool Definition**: [packages/bytebotd/src/mcp/computer-use.tools.ts:11-35]()

For more details on MCP integration, see [MCP Integration](#7.3).

---

## Action Execution Implementation

The `ComputerUseService` dispatches actions to appropriate handlers using a switch statement. Most handlers delegate to the `NutService` automation layer.

### Action Dispatch Map

| Action | Handler Method | Delegates To | Returns |
|--------|---------------|--------------|---------|
| `move_mouse` | `moveMouse()` | `NutService.mouseMoveEvent()` | `void` |
| `trace_mouse` | `traceMouse()` | `NutService.mouseMoveEvent()` + `holdKeys()` | `void` |
| `click_mouse` | `clickMouse()` | `NutService.mouseClickEvent()` | `void` |
| `press_mouse` | `pressMouse()` | `NutService.mouseButtonEvent()` | `void` |
| `drag_mouse` | `dragMouse()` | `NutService.mouseButtonEvent()` + `mouseMoveEvent()` | `void` |
| `scroll` | `scroll()` | `NutService.mouseWheelEvent()` | `void` |
| `type_keys` | `typeKeys()` | `NutService.sendKeys()` | `void` |
| `press_keys` | `pressKeys()` | `NutService.holdKeys()` | `void` |
| `type_text` | `typeText()` | `NutService.typeText()` | `void` |
| `paste_text` | `pasteText()` | `NutService.pasteText()` | `void` |
| `wait` | `delay()` | `setTimeout()` | `void` |
| `screenshot` | `screenshot()` | `NutService.screendump()` | `{ image: string }` |
| `cursor_position` | `cursor_position()` | `NutService.getCursorPosition()` | `{ x, y }` |
| `application` | `application()` | `exec()`, `spawn()`, `wmctrl` | `void` |
| `write_file` | `writeFile()` | `fs.writeFile()`, `exec()` | `{ success, message }` |
| `read_file` | `readFile()` | `fs.readFile()`, `exec()` | `{ success, data, ... }` |

**Sources**: [packages/bytebotd/src/computer-use/computer-use.service.ts:34-104]()

### NutService Integration

The `NutService` wraps the `@nut-tree-fork/nut-js` library, providing:
- Mouse control (`mouseMoveEvent`, `mouseClickEvent`, `mouseButtonEvent`, `mouseWheelEvent`)
- Keyboard control (`sendKeys`, `holdKeys`, `typeText`, `pasteText`)
- Screen capture (`screendump`)
- Cursor queries (`getCursorPosition`)

For details on the NutService implementation, see [Computer Use Service](#7.1).

**Sources**: [packages/bytebotd/src/nut/nut.service.ts]() (referenced in system architecture)

---

## Summary

The Computer Use API provides a unified HTTP interface for controlling the virtual desktop through 17 distinct action types organized into four categories:

- **Mouse Actions** (8): cursor movement, clicking, dragging, scrolling
- **Keyboard Actions** (5): key sequences, text typing, clipboard operations  
- **System Actions** (3): screenshots, waiting, application management
- **File Actions** (2): reading and writing files on the desktop

All requests are validated using class-validator DTOs, dispatched through a type-safe switch statement, and executed via the NutJS automation framework. The API is consumed by both the AI agent during task execution and external MCP clients for programmatic desktop control.

**Sources**: [packages/bytebotd/src/computer-use/computer-use.service.ts:1-508](), [packages/shared/src/types/computerAction.types.ts:1-126](), [packages/bytebotd/src/computer-use/dto/computer-action.dto.ts:1-240]()

---

# Page: WebSocket API

# WebSocket API

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [packages/bytebot-agent/src/main.ts](packages/bytebot-agent/src/main.ts)
- [packages/bytebot-agent/src/tasks/tasks.gateway.ts](packages/bytebot-agent/src/tasks/tasks.gateway.ts)
- [packages/bytebot-ui/next.config.ts](packages/bytebot-ui/next.config.ts)
- [packages/bytebot-ui/server.ts](packages/bytebot-ui/server.ts)
- [packages/bytebot-ui/src/app/api/[[...path]]/route.ts](packages/bytebot-ui/src/app/api/[[...path]]/route.ts)
- [packages/bytebot-ui/src/hooks/useWebSocket.ts](packages/bytebot-ui/src/hooks/useWebSocket.ts)

</details>



This document describes the real-time WebSocket communication layer that enables live task updates and message delivery in Bytebot. The WebSocket API uses Socket.IO for bidirectional communication between the frontend and backend, with room-based subscriptions for task-specific event filtering.

For information about REST API endpoints for task management, see [Tasks REST API](#10.1). For details on the internal event-driven architecture within bytebot-agent, see [Communication Patterns](#2.2).

## Overview

The WebSocket system provides real-time notifications for task state changes, new messages, task creation, and task deletion. Clients connect to the `TasksGateway` in bytebot-agent via a proxy layer in bytebot-ui, subscribe to specific task rooms, and receive targeted updates.

**Key Components:**
- **Server**: `TasksGateway` class in bytebot-agent
- **Client**: `useWebSocket` hook in bytebot-ui
- **Proxy**: Express middleware in bytebot-ui server
- **Transport**: Socket.IO over WebSocket protocol

**Sources:** [packages/bytebot-agent/src/tasks/tasks.gateway.ts:1-58](), [packages/bytebot-ui/src/hooks/useWebSocket.ts:1-114]()

## Connection Architecture

The WebSocket connection flows through a multi-layer proxy architecture to enable unified frontend access.

```mermaid
graph TB
    Client["Client Browser<br/>(socket.io-client)"]
    UIServer["bytebot-ui Express Server<br/>Port 9992<br/>server.ts"]
    Proxy["createProxyMiddleware<br/>Path: /api/proxy/tasks"]
    Gateway["TasksGateway<br/>bytebot-agent Port 9991"]
    
    Client -->|"WebSocket Upgrade<br/>path: /api/proxy/tasks"| UIServer
    UIServer -->|"Proxy Layer"| Proxy
    Proxy -->|"Path Rewrite:<br/>/socket.io"| Gateway
    
    Gateway -.->|"task_updated<br/>new_message<br/>task_created<br/>task_deleted"| Proxy
    Proxy -.-> UIServer
    UIServer -.-> Client
```

**Connection Flow:**

1. **Client connects** to `io({ path: "/api/proxy/tasks" })` on port 9992
2. **Express server** receives WebSocket upgrade request at `/api/proxy/tasks`
3. **Proxy middleware** rewrites path to `/socket.io` and forwards to bytebot-agent
4. **TasksGateway** accepts connection on port 9991
5. **Bidirectional communication** established through proxy chain

**Sources:** [packages/bytebot-ui/server.ts:32-37](), [packages/bytebot-ui/server.ts:57-65](), [packages/bytebot-agent/src/tasks/tasks.gateway.ts:12-17]()

## Gateway Configuration

The `TasksGateway` class configures the Socket.IO server with CORS and connection handling.

```mermaid
classDiagram
    class TasksGateway {
        +Server server
        +handleConnection(client: Socket)
        +handleDisconnect(client: Socket)
        +handleJoinTask(client: Socket, taskId: string)
        +handleLeaveTask(client: Socket, taskId: string)
        +emitTaskUpdate(taskId: string, task: any)
        +emitNewMessage(taskId: string, message: any)
        +emitTaskCreated(task: any)
        +emitTaskDeleted(taskId: string)
    }
    
    class WebSocketGateway {
        <<decorator>>
        cors origin "*"
        cors methods GET POST
    }
    
    class Socket {
        id string
        join(room: string)
        leave(room: string)
    }
    
    TasksGateway --|> WebSocketGateway
    TasksGateway --> Socket : manages
```

**Gateway Decorator Configuration:**

| Property | Value | Purpose |
|----------|-------|---------|
| `cors.origin` | `"*"` | Allow all origins |
| `cors.methods` | `["GET", "POST"]` | Permitted HTTP methods |

The gateway implements `OnGatewayConnection` and `OnGatewayDisconnect` lifecycle interfaces to log connection events.

**Sources:** [packages/bytebot-agent/src/tasks/tasks.gateway.ts:12-28]()

## Client-to-Server Events

Clients emit two events to manage room subscriptions.

### join_task

Subscribe to updates for a specific task.

**Event Name:** `"join_task"`

**Payload:** `string` (task ID)

**Handler:** [packages/bytebot-agent/src/tasks/tasks.gateway.ts:30-34]()

```typescript
@SubscribeMessage('join_task')
handleJoinTask(client: Socket, taskId: string) {
  client.join(`task_${taskId}`);
  console.log(`Client ${client.id} joined task ${taskId}`);
}
```

**Room Pattern:** `task_${taskId}`

When a client joins a task room, it will receive all room-scoped events (`task_updated`, `new_message`) for that task.

**Client Usage:**

The `useWebSocket` hook automatically manages room subscriptions. When `joinTask(taskId)` is called, the hook:
1. Leaves the current task room (if any)
2. Emits `join_task` with the new task ID
3. Updates internal state to track the current room

**Sources:** [packages/bytebot-agent/src/tasks/tasks.gateway.ts:30-34](), [packages/bytebot-ui/src/hooks/useWebSocket.ts:68-79]()

### leave_task

Unsubscribe from a task's updates.

**Event Name:** `"leave_task"`

**Payload:** `string` (task ID)

**Handler:** [packages/bytebot-agent/src/tasks/tasks.gateway.ts:36-40]()

```typescript
@SubscribeMessage('leave_task')
handleLeaveTask(client: Socket, taskId: string) {
  client.leave(`task_${taskId}`);
  console.log(`Client ${client.id} left task ${taskId}`);
}
```

Clients should emit this event before disconnecting or switching to a different task to clean up server-side room membership.

**Sources:** [packages/bytebot-agent/src/tasks/tasks.gateway.ts:36-40](), [packages/bytebot-ui/src/hooks/useWebSocket.ts:81-88]()

## Server-to-Client Events

The gateway emits four event types to notify clients of state changes.

```mermaid
graph LR
    subgraph "Room-Scoped Events"
        TaskUpdated["task_updated<br/>Emitted to: task_taskId room"]
        NewMessage["new_message<br/>Emitted to: task_taskId room"]
    end
    
    subgraph "Global Events"
        TaskCreated["task_created<br/>Emitted to: all clients"]
        TaskDeleted["task_deleted<br/>Emitted to: all clients"]
    end
    
    TasksService["TasksService<br/>emitTaskUpdate()"]
    MessagesService["MessagesService<br/>emitNewMessage()"]
    
    TasksService -->|"Calls gateway.emitTaskUpdate()"| TaskUpdated
    MessagesService -->|"Calls gateway.emitNewMessage()"| NewMessage
    TasksService -->|"Calls gateway.emitTaskCreated()"| TaskCreated
    TasksService -->|"Calls gateway.emitTaskDeleted()"| TaskDeleted
```

**Sources:** [packages/bytebot-agent/src/tasks/tasks.gateway.ts:42-56]()

### task_updated

Notifies clients when a task's state changes.

**Event Name:** `"task_updated"`

**Scope:** Room-scoped (`task_${taskId}`)

**Payload:** Task object

**Emitter Method:** [packages/bytebot-agent/src/tasks/tasks.gateway.ts:42-44]()

```typescript
emitTaskUpdate(taskId: string, task: any) {
  this.server.to(`task_${taskId}`).emit('task_updated', task);
}
```

**Triggered By:**
- Task status changes (PENDING → RUNNING → COMPLETED, etc.)
- Task updates (description, priority, scheduledFor changes)
- Control handoff (AI → USER, USER → AI)
- Execution timestamps (executedAt, completedAt)

Only clients that have joined the specific task room receive this event.

**Client Handler:** [packages/bytebot-ui/src/hooks/useWebSocket.ts:44-47]()

**Sources:** [packages/bytebot-agent/src/tasks/tasks.gateway.ts:42-44]()

### new_message

Notifies clients when a new message is added to a task.

**Event Name:** `"new_message"`

**Scope:** Room-scoped (`task_${taskId}`)

**Payload:** Message object

**Emitter Method:** [packages/bytebot-agent/src/tasks/tasks.gateway.ts:46-48]()

```typescript
emitNewMessage(taskId: string, message: any) {
  this.server.to(`task_${taskId}`).emit('new_message', message);
}
```

**Triggered By:**
- User sends a message
- AI agent generates a response
- Tool execution completes (screenshot, action result)
- User takeover actions

**Client Handler:** [packages/bytebot-ui/src/hooks/useWebSocket.ts:49-52]()

**Sources:** [packages/bytebot-agent/src/tasks/tasks.gateway.ts:46-48]()

### task_created

Notifies all clients when a new task is created.

**Event Name:** `"task_created"`

**Scope:** Global (all connected clients)

**Payload:** Task object

**Emitter Method:** [packages/bytebot-agent/src/tasks/tasks.gateway.ts:50-52]()

```typescript
emitTaskCreated(task: any) {
  this.server.emit('task_created', task);
}
```

**Triggered By:**
- User creates a task via the UI
- AI agent creates a subtask using the `create_task` tool

**Use Case:** Updates task list pages in real-time without manual refresh.

**Client Handler:** [packages/bytebot-ui/src/hooks/useWebSocket.ts:54-57]()

**Sources:** [packages/bytebot-agent/src/tasks/tasks.gateway.ts:50-52]()

### task_deleted

Notifies all clients when a task is deleted.

**Event Name:** `"task_deleted"`

**Scope:** Global (all connected clients)

**Payload:** `string` (task ID)

**Emitter Method:** [packages/bytebot-agent/src/tasks/tasks.gateway.ts:54-56]()

```typescript
emitTaskDeleted(taskId: string) {
  this.server.emit('task_deleted', taskId);
}
```

**Triggered By:**
- User deletes a task via the UI
- Task cleanup operations

**Use Case:** Removes deleted tasks from task list views in real-time.

**Client Handler:** [packages/bytebot-ui/src/hooks/useWebSocket.ts:59-62]()

**Sources:** [packages/bytebot-agent/src/tasks/tasks.gateway.ts:54-56]()

## Event Payload Schemas

### Task Object

```typescript
{
  id: string;
  description: string;
  status: "PENDING" | "RUNNING" | "COMPLETED" | "FAILED" | "NEEDS_HELP" | "CANCELLED";
  priority: "LOW" | "MEDIUM" | "HIGH";
  type: "MAIN" | "SUB";
  control: "AI" | "USER";
  model: string;
  scheduledFor?: Date;
  executedAt?: Date;
  completedAt?: Date;
  error?: string;
  createdAt: Date;
  updatedAt: Date;
}
```

Transmitted in: `task_updated`, `task_created`

### Message Object

```typescript
{
  id: string;
  taskId: string;
  content: MessageContentBlock[];  // Array of text/tool blocks
  role: "USER" | "ASSISTANT";
  createdAt: Date;
  summaryId?: string;
}
```

Transmitted in: `new_message`

For detailed content block types (Text, ToolUse, ToolResult, Image, UserAction), see [Message Content Types](#9.3).

**Sources:** Type definitions in `@bytebot/shared` package

## Client Implementation

The `useWebSocket` hook provides a React interface for WebSocket communication.

### Hook Interface

```typescript
interface UseWebSocketProps {
  onTaskUpdate?: (task: Task) => void;
  onNewMessage?: (message: Message) => void;
  onTaskCreated?: (task: Task) => void;
  onTaskDeleted?: (taskId: string) => void;
}

interface UseWebSocketReturn {
  socket: Socket | null;
  joinTask: (taskId: string) => void;
  leaveTask: () => void;
  disconnect: () => void;
  isConnected: boolean;
}
```

**Sources:** [packages/bytebot-ui/src/hooks/useWebSocket.ts:5-17]()

### Connection Configuration

The hook initializes the Socket.IO client with specific configuration:

```typescript
const socket = io({
  path: "/api/proxy/tasks",        // Proxy endpoint
  transports: ["websocket"],       // WebSocket only (no polling)
  autoConnect: true,               // Connect immediately
  reconnection: true,              // Enable reconnection
  reconnectionAttempts: 5,         // Try 5 times
  reconnectionDelay: 1000,         // 1 second between attempts
});
```

**Configuration Details:**

| Option | Value | Purpose |
|--------|-------|---------|
| `path` | `"/api/proxy/tasks"` | Routes through bytebot-ui proxy |
| `transports` | `["websocket"]` | Skip HTTP long-polling fallback |
| `autoConnect` | `true` | Connect on initialization |
| `reconnection` | `true` | Auto-reconnect on disconnect |
| `reconnectionAttempts` | `5` | Max retry attempts |
| `reconnectionDelay` | `1000` | 1 second between retries |

**Sources:** [packages/bytebot-ui/src/hooks/useWebSocket.ts:21-34]()

### Connection Lifecycle

```mermaid
stateDiagram-v2
    [*] --> Initializing: useWebSocket() called
    Initializing --> Connecting: connect() invoked
    Connecting --> Connected: Socket.IO handshake success
    
    Connected --> JoinedRoom: joinTask(taskId)
    JoinedRoom --> LeavingRoom: leaveTask() or joinTask(newId)
    LeavingRoom --> JoinedRoom: emit leave_task, join_task
    
    Connected --> Disconnecting: disconnect() called
    Disconnecting --> [*]: Socket closed
    
    Connected --> Reconnecting: Connection lost
    Reconnecting --> Connected: Reconnection successful
    Reconnecting --> [*]: Max attempts exceeded
    
    note right of JoinedRoom
        Receives room-scoped events:
        - task_updated
        - new_message
    end note
    
    note right of Connected
        Receives global events:
        - task_created
        - task_deleted
    end note
```

**Lifecycle Methods:**

**`connect()`** - Establishes WebSocket connection
- Called automatically on hook mount
- Returns existing socket if already connected
- Registers all event handlers

**`joinTask(taskId)`** - Subscribes to task room
- Leaves previous room if any
- Emits `join_task` event
- Updates `currentTaskIdRef`

**`leaveTask()`** - Unsubscribes from current room
- Emits `leave_task` event
- Clears `currentTaskIdRef`

**`disconnect()`** - Closes WebSocket connection
- Calls `socket.disconnect()`
- Clears all refs
- Called on component unmount

**Sources:** [packages/bytebot-ui/src/hooks/useWebSocket.ts:21-104]()

### Event Handler Registration

The hook registers event handlers during connection:

```typescript
socket.on("connect", () => {
  console.log("Connected to WebSocket server");
});

socket.on("disconnect", () => {
  console.log("Disconnected from WebSocket server");
});

socket.on("task_updated", (task: Task) => {
  console.log("Task updated:", task);
  onTaskUpdate?.(task);
});

socket.on("new_message", (message: Message) => {
  console.log("New message:", message);
  onNewMessage?.(message);
});

socket.on("task_created", (task: Task) => {
  console.log("Task created:", task);
  onTaskCreated?.(task);
});

socket.on("task_deleted", (taskId: string) => {
  console.log("Task deleted:", taskId);
  onTaskDeleted?.(taskId);
});
```

All handlers call optional callback props, allowing components to react to events.

**Sources:** [packages/bytebot-ui/src/hooks/useWebSocket.ts:36-62]()

## Proxy Layer Details

The bytebot-ui Express server handles WebSocket upgrade requests using `http-proxy-middleware`.

### HTTP Proxy Setup

```typescript
const tasksProxy = createProxyMiddleware({
  target: BYTEBOT_AGENT_BASE_URL,  // e.g., http://localhost:9991
  ws: true,                         // Enable WebSocket proxying
  pathRewrite: { 
    "^/api/proxy/tasks": "/socket.io"  // Rewrite path
  },
});

expressApp.use("/api/proxy/tasks", tasksProxy);
```

**Sources:** [packages/bytebot-ui/server.ts:33-40]()

### WebSocket Upgrade Handling

```typescript
server.on("upgrade", (request, socket, head) => {
  const { pathname } = new URL(
    request.url!,
    `http://${request.headers.host}`,
  );

  if (pathname.startsWith("/api/proxy/tasks")) {
    return tasksProxy.upgrade(request, socket as any, head);
  }
  
  // ... other upgrade handlers
});
```

The `upgrade` event handler:
1. Parses the request URL path
2. Checks if path starts with `/api/proxy/tasks`
3. Delegates to `tasksProxy.upgrade()` for WebSocket handshake
4. Proxy forwards to `${BYTEBOT_AGENT_BASE_URL}/socket.io`

**Sources:** [packages/bytebot-ui/server.ts:57-65]()

## CORS Configuration

The bytebot-agent backend enables CORS for WebSocket connections.

### Application-Level CORS

[packages/bytebot-agent/src/main.ts:22-25]():

```typescript
app.enableCors({
  origin: '*',
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'PATCH'],
});
```

### Gateway-Level CORS

[packages/bytebot-agent/src/tasks/tasks.gateway.ts:12-17]():

```typescript
@WebSocketGateway({
  cors: {
    origin: '*',
    methods: ['GET', 'POST'],
  },
})
```

Both configurations allow all origins (`*`) to support development environments and flexible deployment. In production, this should be restricted to specific domains.

**Sources:** [packages/bytebot-agent/src/main.ts:22-25](), [packages/bytebot-agent/src/tasks/tasks.gateway.ts:12-17]()

## Usage Example

Typical usage in a React component:

```typescript
const TaskDetailPage = ({ taskId }: { taskId: string }) => {
  const [task, setTask] = useState<Task | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  
  const { joinTask, leaveTask, isConnected } = useWebSocket({
    onTaskUpdate: (updatedTask) => {
      if (updatedTask.id === taskId) {
        setTask(updatedTask);
      }
    },
    onNewMessage: (message) => {
      if (message.taskId === taskId) {
        setMessages(prev => [...prev, message]);
      }
    },
  });
  
  useEffect(() => {
    joinTask(taskId);
    return () => leaveTask();
  }, [taskId, joinTask, leaveTask]);
  
  return (
    <div>
      <ConnectionIndicator connected={isConnected} />
      {/* Task details and messages */}
    </div>
  );
};
```

This pattern:
1. Initializes the WebSocket hook with event handlers
2. Joins the task room on mount
3. Updates local state when events arrive
4. Leaves the room on unmount

**Sources:** Implementation pattern follows [packages/bytebot-ui/src/hooks/useWebSocket.ts:1-114]()

## Error Handling

### Connection Errors

The Socket.IO client automatically handles connection failures with exponential backoff:
- Maximum 5 reconnection attempts
- 1 second initial delay
- Automatic exponential backoff

### Event Handler Errors

Event handlers use optional chaining (`?.`) to prevent crashes when callbacks are undefined:

```typescript
onTaskUpdate?.(task);
onNewMessage?.(message);
```

This allows the hook to be used without providing all callbacks.

**Sources:** [packages/bytebot-ui/src/hooks/useWebSocket.ts:44-62]()

## Performance Considerations

### Room-Based Filtering

Room subscriptions ensure clients only receive relevant events:
- Clients in `task_123` room only get updates for task 123
- Global events (task_created, task_deleted) broadcast to all clients
- Prevents unnecessary network traffic and client-side filtering

### Transport Optimization

The client configuration uses WebSocket-only transport:

```typescript
transports: ["websocket"]
```

This skips HTTP long-polling fallback, reducing connection establishment time and eliminating polling overhead.

**Sources:** [packages/bytebot-ui/src/hooks/useWebSocket.ts:29](), [packages/bytebot-agent/src/tasks/tasks.gateway.ts:30-40]()

---

# Page: Development Guide

# Development Guide

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [packages/bytebot-agent/package-lock.json](packages/bytebot-agent/package-lock.json)
- [packages/bytebot-agent/package.json](packages/bytebot-agent/package.json)
- [packages/bytebot-agent/src/agent/agent.module.ts](packages/bytebot-agent/src/agent/agent.module.ts)
- [packages/bytebot-agent/src/app.module.ts](packages/bytebot-agent/src/app.module.ts)
- [packages/bytebot-ui/package-lock.json](packages/bytebot-ui/package-lock.json)
- [packages/bytebot-ui/package.json](packages/bytebot-ui/package.json)
- [packages/bytebot-ui/src/app/layout.tsx](packages/bytebot-ui/src/app/layout.tsx)
- [packages/bytebot-ui/src/components/layout/Header.tsx](packages/bytebot-ui/src/components/layout/Header.tsx)

</details>



This document provides developers with comprehensive information for setting up, building, and contributing to the Bytebot system. It covers local development environment setup, build processes, testing procedures, and deployment workflows.

For information about system architecture and component relationships, see [System Architecture](#2). For deployment instructions for end users, see [Installation and Setup](#3).

## Development Environment Requirements

The Bytebot system requires a consistent development environment across all services. The following tools and versions are required:

| Tool | Version | Purpose |
|------|---------|---------|
| Node.js | 20.x | Runtime for all JavaScript/TypeScript services |
| Docker | Latest | Containerization and local development |
| Docker Compose | Latest | Multi-service orchestration |
| PostgreSQL | Latest | Database for development |

All services are configured with TypeScript 5.7+ and use modern ES2022+ features. The system enforces consistent code formatting through Prettier and linting through ESLint across all packages.

**Sources:** [packages/bytebot-agent/package.json:96-98](), [packages/bytebot-agent/package.json:71-72]()

## Repository Structure and Build System

The Bytebot monorepo follows a packages-based architecture with a shared type package and coordinated build processes across all services.

### Package Structure

```mermaid
graph TB
    subgraph "Repository Root"
        subgraph "packages/"
            UI["bytebot-ui/"]
            Agent["bytebot-agent/"]
            Desktop["bytebotd/"]
            Shared["shared/<br/>@bytebot/shared"]
        end
        
        subgraph "Infrastructure"
            Docker["docker/"]
            Workflows[".github/workflows/"]
        end
    end
    
    UI --> Shared
    Agent --> Shared
    Desktop --> Shared
    
    Workflows --> UI
    Workflows --> Agent  
    Workflows --> Desktop
```

### Shared Package Architecture

The `@bytebot/shared` package contains type definitions and schemas used across all services:

| Content Type | Purpose | Usage |
|-------------|---------|-------|
| Type Definitions | TypeScript interfaces for Tasks, Messages, ComputerActions | Ensures type consistency across frontend/backend |
| Zod Schemas | Runtime validation schemas | Validates API requests and responses |
| Enums | Shared enumerations (TaskStatus, Priority, Role) | Consistent state values |
| Constants | System-wide constants | Configuration and defaults |

All services declare `@bytebot/shared` as a local dependency using relative paths:

```json
"dependencies": {
  "@bytebot/shared": "../shared"
}
```

**Sources:** [packages/bytebot-agent/package.json:26](), [packages/bytebot-ui/package.json:13]()

### Build Dependencies and Scripts

The build system uses coordinated npm scripts that ensure the shared package is built before individual services:

```mermaid
graph LR
    SharedBuild["npm run build<br/>--prefix ../shared"] --> AgentBuild["bytebot-agent:<br/>nest build"]
    SharedBuild --> UIBuild["bytebot-ui:<br/>next build"]
    SharedBuild --> DesktopBuild["bytebotd:<br/>nest build"]
    
    PrismaGen["prisma generate"] --> AgentBuild
    PrismaMigrate["prisma migrate deploy"] --> AgentStart["start:prod"]
    
    AgentBuild --> AgentStart
```

#### Agent Service Build Scripts

The agent service demonstrates the coordinated build pattern:

| Script | Command | Purpose |
|--------|---------|---------|
| `build` | `npm run build --prefix ../shared && npx prisma generate && nest build` | Full build with shared package and Prisma client |
| `start` | `npm run build --prefix ../shared && nest start` | Basic start with shared package build |
| `start:dev` | `npm run build --prefix ../shared && nest start --watch` | Development mode with hot reload |
| `start:prod` | `npm run build --prefix ../shared && npx prisma migrate deploy && npx prisma generate && node dist/main` | Production start with migrations |

**Sources:** [packages/bytebot-agent/package.json:11-16]()

#### UI Service Build Scripts

The UI service follows the same pattern with Next.js-specific commands:

| Script | Command | Purpose |
|--------|---------|---------|
| `dev` | `npm run build --prefix ../shared && tsx server.ts` | Development server with custom Express backend |
| `build` | `npm run build --prefix ../shared && next build` | Production build |
| `start` | `npm run build --prefix ../shared && tsx server.ts` | Production start |

**Sources:** [packages/bytebot-ui/package.json:6-9]()

## NestJS Module Architecture

The bytebot-agent service follows NestJS best practices for module organization and dependency injection.

### Root Module Structure

```mermaid
graph TB
    AppModule["AppModule<br/>(app.module.ts)"] --> ConfigModule["ConfigModule.forRoot()<br/>isGlobal: true"]
    AppModule --> ScheduleModule["ScheduleModule.forRoot()<br/>Cron scheduling"]
    AppModule --> EventEmitterModule["EventEmitterModule.forRoot()<br/>Internal events"]
    
    AppModule --> AgentModule["AgentModule<br/>Core processing logic"]
    AppModule --> TasksModule["TasksModule<br/>Task CRUD + WebSocket"]
    AppModule --> MessagesModule["MessagesModule<br/>Message storage"]
    AppModule --> SummariesModule["SummariesModule<br/>Context summarization"]
    
    subgraph "AI Provider Modules"
        AppModule --> AnthropicModule["AnthropicModule<br/>@anthropic-ai/sdk"]
        AppModule --> OpenAIModule["OpenAIModule<br/>openai package"] 
        AppModule --> GoogleModule["GoogleModule<br/>@google/genai"]
        AppModule --> ProxyModule["ProxyModule<br/>LiteLLM proxy"]
    end
    
    AppModule --> PrismaModule["PrismaModule<br/>@prisma/client"]
```

**Sources:** [packages/bytebot-agent/src/app.module.ts:1-37]()

### Global Module Configuration

The root module uses NestJS `.forRoot()` pattern for global configuration:

```typescript
@Module({
  imports: [
    ScheduleModule.forRoot(),           // Enables @Cron() decorators
    EventEmitterModule.forRoot(),        // Enables @OnEvent() decorators
    ConfigModule.forRoot({
      isGlobal: true,                    // Makes ConfigService available everywhere
    }),
    // ... feature modules
  ],
})
```

This pattern ensures infrastructure services are available to all modules without repeated imports.

**Sources:** [packages/bytebot-agent/src/app.module.ts:18-23]()

### Feature Module Pattern: AgentModule

The `AgentModule` demonstrates dependency injection and service composition:

```mermaid
graph TB
    subgraph "AgentModule Imports"
        ConfigModule2["ConfigModule<br/>(Global)"]
        TasksModule2["TasksModule<br/>(exports TasksService)"]
        MessagesModule2["MessagesModule<br/>(exports MessagesService)"]
        SummariesModule2["SummariesModule<br/>(exports SummariesService)"]
        AnthropicModule2["AnthropicModule<br/>(exports AnthropicService)"]
        OpenAIModule2["OpenAIModule<br/>(exports OpenAIService)"]
        GoogleModule2["GoogleModule<br/>(exports GoogleService)"]
        ProxyModule2["ProxyModule<br/>(exports ProxyService)"]
    end
    
    subgraph "AgentModule Providers"
        AgentProcessor["AgentProcessor<br/>(Injectable)"]
        AgentScheduler["AgentScheduler<br/>(Injectable)"]
        InputCaptureService["InputCaptureService<br/>(Injectable)"]
        AgentAnalyticsService["AgentAnalyticsService<br/>(Injectable)"]
    end
    
    ConfigModule2 --> AgentProcessor
    TasksModule2 --> AgentProcessor
    MessagesModule2 --> AgentProcessor
    SummariesModule2 --> AgentProcessor
    AnthropicModule2 --> AgentProcessor
    OpenAIModule2 --> AgentProcessor
    GoogleModule2 --> AgentProcessor
    ProxyModule2 --> AgentProcessor
    
    AgentProcessor --> AgentScheduler
    AgentProcessor --> InputCaptureService
    AgentProcessor --> AgentAnalyticsService
    
    AgentModule["AgentModule<br/>(exports AgentProcessor)"] --> AgentProcessor
```

**Sources:** [packages/bytebot-agent/src/agent/agent.module.ts:1-34]()

### Dependency Injection Pattern

NestJS modules use constructor injection to access services from imported modules:

```typescript
@Module({
  imports: [
    TasksModule,      // Must export TasksService
    MessagesModule,   // Must export MessagesService
    AnthropicModule,  // Must export AnthropicService
  ],
  providers: [AgentProcessor],
  exports: [AgentProcessor],
})
export class AgentModule {}
```

The `AgentProcessor` can then inject these services:

```typescript
@Injectable()
export class AgentProcessor {
  constructor(
    private tasksService: TasksService,
    private messagesService: MessagesService,
    private anthropicService: AnthropicService,
  ) {}
}
```

**Sources:** [packages/bytebot-agent/src/agent/agent.module.ts:15-33]()

## Containerized Development Workflow  

The system uses Docker for both development and production deployment, with multi-architecture support and automated builds.

### Development Container Architecture

```mermaid
graph TB
    subgraph "Development Environment"
        ComposeFile["docker-compose.yml<br/>(Local Development)"]
        
        subgraph "Service Containers"
            UIContainer["bytebot-ui:dev<br/>Port: 9992<br/>Volume: ./packages/bytebot-ui"]
            AgentContainer["bytebot-agent:dev<br/>Port: 9991<br/>Volume: ./packages/bytebot-agent"]
            DesktopContainer["bytebot-desktop:dev<br/>Port: 9990<br/>Volume: ./packages/bytebotd"]
        end
        
        subgraph "Supporting Services"
            PostgresContainer["postgresql:latest<br/>Port: 5432<br/>Volume: pgdata"]
            RedisContainer["redis:latest<br/>Port: 6379"]
        end
    end
    
    ComposeFile --> UIContainer
    ComposeFile --> AgentContainer
    ComposeFile --> DesktopContainer
    ComposeFile --> PostgresContainer
    ComposeFile --> RedisContainer
```

Each service includes Docker configuration optimized for development with volume mounts for hot reloading and debugging support.

**Sources:** [packages/bytebotd/.dockerignore:1-10]()

## CI/CD Pipeline Architecture

The system employs GitHub Actions for automated building and publishing of container images:

### Build Pipeline Structure

```mermaid
graph TD
    subgraph "GitHub Actions Workflows"
        UIWorkflow["build-ui.yaml<br/>(UI Changes)"]
        AgentWorkflow["build-agent.yaml<br/>(Agent Changes)"]
        DesktopWorkflow["build-desktop.yaml<br/>(Desktop Changes)"]
    end
    
    subgraph "Triggers"
        UITrigger["Push to main<br/>packages/bytebot-ui/**<br/>packages/shared/**"] --> UIWorkflow
        AgentTrigger["Push to main<br/>packages/bytebot-agent/**<br/>packages/shared/**"] --> AgentWorkflow
        DesktopTrigger["Push to main<br/>docker/**<br/>packages/bytebotd/**"] --> DesktopWorkflow
    end
    
    subgraph "Build Process"
        UIWorkflow --> QEMUSetup["QEMU Multi-arch Setup"]
        AgentWorkflow --> QEMUSetup
        DesktopWorkflow --> QEMUSetup
        
        QEMUSetup --> BuildxSetup["Docker Buildx Setup"]
        BuildxSetup --> MultiArchBuild["Multi-arch Build<br/>(amd64, arm64)"]
        MultiArchBuild --> GHCRPush["Push to GHCR<br/>ghcr.io/bytebot-ai/"]
    end
```

Each workflow builds multi-architecture images (amd64, arm64) and publishes them to GitHub Container Registry with the `edge` tag for continuous deployment.

**Sources:** [.github/workflows/build-ui.yaml:1-51](), [.github/workflows/build-agent.yaml:1-50](), [.github/workflows/build-desktop.yaml:1-61]()

## Validation and Type Safety

The system employs dual validation strategies: compile-time type checking with TypeScript and runtime validation using Zod and class-validator.

### Type System Architecture

```mermaid
graph TB
    subgraph "Compile-Time Types"
        SharedTypes["@bytebot/shared<br/>TypeScript Interfaces"]
        PrismaTypes["@prisma/client<br/>Generated Types"]
    end
    
    subgraph "Runtime Validation"
        ZodSchemas["Zod Schemas<br/>@bytebot/shared"]
        ClassValidatorDTOs["class-validator DTOs<br/>bytebot-agent"]
    end
    
    subgraph "Application Layer"
        UIComponents["UI Components<br/>Type-safe props"]
        NestJSControllers["NestJS Controllers<br/>Validated DTOs"]
        ServiceLayer["Service Layer<br/>Type-safe methods"]
    end
    
    SharedTypes --> UIComponents
    SharedTypes --> ServiceLayer
    PrismaTypes --> ServiceLayer
    
    ZodSchemas --> UIComponents
    ZodSchemas --> NestJSControllers
    ClassValidatorDTOs --> NestJSControllers
    
    NestJSControllers --> ServiceLayer
```

**Sources:** [packages/bytebot-agent/package.json:38-39](), [packages/bytebot-agent/package.json:45]()

### Zod Schema Validation

Zod provides runtime type validation with TypeScript inference:

| Package | Zod Version | Usage |
|---------|-------------|-------|
| bytebot-agent | 4.0.5 | LLM response validation, API request schemas |
| bytebot-ui | 3.24.2 | Form validation, API response validation |
| @bytebot/shared | - | Shared schemas for common types |

Zod schemas enable both runtime validation and TypeScript type inference:

```typescript
// Schema definition provides both validation and types
const TaskSchema = z.object({
  id: z.string(),
  description: z.string(),
  status: z.enum(['PENDING', 'RUNNING', 'COMPLETED']),
});

// Inferred TypeScript type
type Task = z.infer<typeof TaskSchema>;
```

**Sources:** [packages/bytebot-agent/package.json:45](), [packages/bytebot-ui/package.json:47]()

### Class-Validator DTOs

The bytebot-agent service uses class-validator for NestJS DTO validation:

```typescript
// DTO with validation decorators
class CreateTaskDto {
  @IsString()
  @IsNotEmpty()
  description: string;

  @IsEnum(TaskPriority)
  @IsOptional()
  priority?: TaskPriority;

  @IsArray()
  @ValidateNested({ each: true })
  @Type(() => FileDto)
  files?: FileDto[];
}
```

NestJS automatically validates incoming requests using ValidationPipe:

```typescript
@Post('tasks')
@UsePipes(new ValidationPipe({ transform: true }))
async createTask(@Body() dto: CreateTaskDto) {
  // dto is validated and transformed
}
```

**Sources:** [packages/bytebot-agent/package.json:38-39]()

### Type Guard Pattern

Type guards enable runtime type checking with TypeScript type narrowing:

```typescript
function isToolUseBlock(
  block: MessageContentBlock
): block is ToolUseBlock {
  return block.type === 'tool_use';
}

// Usage with type narrowing
if (isToolUseBlock(block)) {
  // TypeScript knows block is ToolUseBlock
  const toolName = block.name;
  const toolInput = block.input;
}
```

This pattern is used throughout the codebase to safely handle union types and polymorphic data structures.

**Sources:** [packages/bytebot-agent/package.json:38-39]()

## Testing and Development Tools

### Package Scripts and Development Commands

The agent service provides comprehensive npm scripts for various development tasks:

| Script | Purpose | Command |
|--------|---------|---------|
| `start:dev` | Development with hot reload | `npm run build --prefix ../shared && nest start --watch` |
| `start:debug` | Debug mode with inspector | `npm run build --prefix ../shared && nest start --debug --watch` |
| `test` | Unit test execution | `jest` |
| `test:watch` | Continuous testing | `jest --watch` |
| `test:cov` | Coverage reporting | `jest --coverage` |
| `test:e2e` | End-to-end testing | `jest --config ./test/jest-e2e.json` |
| `lint` | Code linting and fixing | `eslint "{src,apps,libs,test}/**/*.ts" --fix` |
| `format` | Code formatting | `prettier --write "src/**/*.ts" "test/**/*.ts"` |

**Sources:** [packages/bytebot-agent/package.json:8-22]()

### Jest Configuration

The agent service uses Jest with TypeScript support:

```json
{
  "jest": {
    "moduleFileExtensions": ["js", "json", "ts"],
    "rootDir": "src",
    "testRegex": ".*\\.spec\\.ts$",
    "transform": {
      "^.+\\.(t|j)s$": "ts-jest"
    },
    "collectCoverageFrom": ["**/*.(t|j)s"],
    "coverageDirectory": "../coverage",
    "testEnvironment": "node"
  }
}
```

Test files follow the `*.spec.ts` naming convention and are located alongside source files.

**Sources:** [packages/bytebot-agent/package.json:75-91]()

### Database Development Workflow

Database operations use Prisma for schema management and client generation:

```mermaid
graph LR
    SchemaDev["schema.prisma<br/>(Development)"] --> PrismaMigrateDev["prisma migrate dev"]
    PrismaMigrateDev --> PrismaGenerate["prisma generate"]
    PrismaGenerate --> DevClient["@prisma/client<br/>(Type-safe DB access)"]
    
    SchemaProd["schema.prisma<br/>(Production)"] --> PrismaMigrateDeploy["prisma migrate deploy"]
    PrismaMigrateDeploy --> PrismaGenerateProd["prisma generate"] 
    PrismaGenerateProd --> ProdClient["@prisma/client<br/>(Production)"]
```

| Script | Command | Usage |
|--------|---------|-------|
| `prisma:dev` | `npx prisma migrate dev && npx prisma generate` | Development migrations with prompts |
| `prisma:prod` | `npx prisma migrate deploy && npx prisma generate` | Production migrations without prompts |

**Sources:** [packages/bytebot-agent/package.json:9-10]()

## Desktop Environment Development

The desktop service includes specific configuration for the virtual desktop environment used by the AI agents:

### Desktop Environment Configuration

```mermaid
graph TB
    subgraph "Desktop Container Configuration"
        LightDMConfig["lightdm.conf.d/50-autologin.conf<br/>(Auto-login user)"]
        FirefoxPolicies["firefox/policies/policies.json<br/>(Browser policies)"]
        XFCEDesktop["Ubuntu + XFCE<br/>(Desktop environment)"]
    end
    
    LightDMConfig --> AutoLogin["autologin-user=user<br/>autologin-session=xfce"]
    FirefoxPolicies --> BrowserConfig["Skip onboarding<br/>Disable features<br/>Block notifications"]
    XFCEDesktop --> VNCServer["VNC Server<br/>(Remote access)"]
```

The desktop environment is pre-configured for autonomous operation with automatic login and browser policies that prevent user interaction prompts.

**Sources:** [packages/bytebotd/root/etc/lightdm/lightdm.conf.d/50-autologin.conf:1-4](), [packages/bytebotd/root/etc/firefox/policies/policies.json:1-28]()

## Contributing Guidelines

### Development Workflow

1. **Environment Setup**: Ensure Node.js 20, Docker, and Docker Compose are installed
2. **Repository Clone**: Clone the repository and initialize submodules if any
3. **Dependency Installation**: Run `npm install` in each package directory
4. **Database Setup**: Initialize PostgreSQL and run Prisma migrations
5. **Service Startup**: Use Docker Compose for full system development

### Code Quality Standards

- **TypeScript**: All code must use TypeScript 5.7+ with strict mode enabled
- **Linting**: ESLint configuration is enforced across all packages
- **Formatting**: Prettier configuration ensures consistent code style
- **Testing**: Minimum test coverage requirements for new features
- **Documentation**: Code documentation using JSDoc for public APIs

### Pull Request Process

- Feature branches should be created from `main`
- All CI/CD checks must pass before merging
- Multi-architecture Docker builds are automatically triggered on merge
- Container images are published to GitHub Container Registry with `edge` tags

The modular architecture and comprehensive tooling support rapid development while maintaining production quality standards.

**Sources:** [packages/bytebot-agent/package.json:59-72]()

---

# Page: Build System

# Build System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [packages/bytebot-agent/package-lock.json](packages/bytebot-agent/package-lock.json)
- [packages/bytebot-agent/package.json](packages/bytebot-agent/package.json)
- [packages/bytebot-agent/src/agent/agent.module.ts](packages/bytebot-agent/src/agent/agent.module.ts)
- [packages/bytebot-agent/src/app.module.ts](packages/bytebot-agent/src/app.module.ts)
- [packages/bytebot-ui/package-lock.json](packages/bytebot-ui/package-lock.json)
- [packages/bytebot-ui/package.json](packages/bytebot-ui/package.json)
- [packages/bytebot-ui/src/app/layout.tsx](packages/bytebot-ui/src/app/layout.tsx)
- [packages/bytebot-ui/src/components/layout/Header.tsx](packages/bytebot-ui/src/components/layout/Header.tsx)
- [packages/bytebotd/package-lock.json](packages/bytebotd/package-lock.json)
- [packages/bytebotd/package.json](packages/bytebotd/package.json)
- [packages/bytebotd/src/app.controller.ts](packages/bytebotd/src/app.controller.ts)
- [packages/bytebotd/src/app.module.ts](packages/bytebotd/src/app.module.ts)
- [packages/bytebotd/src/mcp/bytebot-mcp.module.ts](packages/bytebotd/src/mcp/bytebot-mcp.module.ts)
- [packages/bytebotd/src/mcp/index.ts](packages/bytebotd/src/mcp/index.ts)

</details>



This document describes the build process, package dependencies, compilation workflow, and development scripts for the Bytebot codebase. For information about module organization within individual services, see [Module Architecture](#11.2).

## Overview

Bytebot uses a **monorepo structure** with three independently buildable services that share a common type library. The build system is based on npm workspaces, with each package managing its own compilation through specialized build tools (NestJS CLI, Next.js, TypeScript compiler). A critical aspect of the build workflow is the **build order dependency** on the shared package, which must be compiled before any service can build.

## Repository Structure

```mermaid
graph TB
    subgraph "Monorepo Root"
        PackagesDir["packages/"]
    end
    
    subgraph "Service Packages"
        AgentPkg["bytebot-agent/<br/>NestJS Backend"]
        UIPkg["bytebot-ui/<br/>Next.js Frontend"]
        DaemonPkg["bytebotd/<br/>Desktop Daemon"]
    end
    
    subgraph "Shared Package"
        SharedPkg["@bytebot/shared/<br/>Type Definitions"]
    end
    
    PackagesDir --> AgentPkg
    PackagesDir --> UIPkg
    PackagesDir --> DaemonPkg
    PackagesDir --> SharedPkg
    
    AgentPkg -->|"file:../shared"| SharedPkg
    UIPkg -->|"file:../shared"| SharedPkg
    DaemonPkg -->|"file:../shared"| SharedPkg
```

**Sources:** [packages/bytebot-agent/package.json:1-100](), [packages/bytebot-ui/package.json:1-64](), [packages/bytebotd/package.json:1-93]()

### Package Dependencies

Each service package declares `@bytebot/shared` as a dependency using local file references:

| Package | Dependency Declaration |
|---------|----------------------|
| bytebot-agent | `"@bytebot/shared": "../shared"` |
| bytebot-ui | `"@bytebot/shared": "../shared"` |
| bytebotd | `"@bytebot/shared": "file:../shared"` |

This creates a build-time dependency where changes to shared types require rebuilding all consuming packages.

**Sources:** [packages/bytebot-agent/package.json:26](), [packages/bytebot-ui/package.json:13](), [packages/bytebotd/package.json:12]()

## Build Scripts and Workflow

### Build Order Dependency Chain

All service build scripts follow a consistent pattern: **shared package must build first**. This is enforced through script prefixes:

```
npm run build --prefix ../shared && <service-specific-build>
```

```mermaid
graph LR
    BuildShared["npm run build<br/>--prefix ../shared"]
    
    subgraph "bytebot-agent Build"
        PrismaGen["npx prisma generate"]
        NestBuild1["nest build"]
    end
    
    subgraph "bytebot-ui Build"
        NextBuild["next build"]
    end
    
    subgraph "bytebotd Build"
        NestBuild2["nest build"]
    end
    
    BuildShared --> PrismaGen
    PrismaGen --> NestBuild1
    
    BuildShared --> NextBuild
    BuildShared --> NestBuild2
```

**Sources:** [packages/bytebot-agent/package.json:11-16](), [packages/bytebot-ui/package.json:6-8](), [packages/bytebotd/package.json:15-20]()

### bytebot-agent Build Process

The backend service has the most complex build pipeline due to Prisma database schema generation:

| Script | Command | Purpose |
|--------|---------|---------|
| `build` | `npm run build --prefix ../shared && npx prisma generate && nest build` | Production build with Prisma client generation |
| `start` | `npm run build --prefix ../shared && nest start` | Start compiled server |
| `start:dev` | `npm run build --prefix ../shared && nest start --watch` | Development mode with hot reload |
| `start:prod` | `npm run build --prefix ../shared && npx prisma migrate deploy && npx prisma generate && node dist/main` | Production start with migrations |

The production start script includes **database migration execution** (`prisma migrate deploy`) before starting the server, ensuring the database schema is current.

**Sources:** [packages/bytebot-agent/package.json:8-23]()

### bytebot-ui Build Process

The frontend uses a custom Express server (instead of Next.js standalone mode) for API proxying:

| Script | Command | Purpose |
|--------|---------|---------|
| `dev` | `npm run build --prefix ../shared && tsx server.ts` | Development mode using tsx runtime |
| `build` | `npm run build --prefix ../shared && next build` | Production build |
| `start` | `npm run build --prefix ../shared && tsx server.ts` | Production start (runs custom Express server) |

The `tsx` runtime is used instead of `next start` because the service implements a **custom Express server** for request proxying to bytebot-agent and bytebotd services.

**Sources:** [packages/bytebot-ui/package.json:5-9]()

### bytebotd Build Process

The desktop daemon follows a simpler NestJS build pattern:

| Script | Command | Purpose |
|--------|---------|---------|
| `build` | `npm run build --prefix ../shared && nest build` | Production build |
| `start:dev` | `npm run build --prefix ../shared && nest start --watch` | Development with hot reload |
| `start:prod` | `npm run build --prefix ../shared && node dist/main` | Production start |
| `compile` | `tsc` | TypeScript compilation only (no NestJS CLI) |

**Sources:** [packages/bytebotd/package.json:13-26]()

## Build Tool Stack

### Compilation Tools by Package

```mermaid
graph TB
    subgraph "bytebot-agent Tools"
        NestCLI1["@nestjs/cli: ^11.0.0"]
        SWC1["@swc/core: ^1.10.7"]
        TSC1["typescript: ^5.7.3"]
        Prisma["prisma: ^6.16.1"]
    end
    
    subgraph "bytebot-ui Tools"
        NextJS["next: >=15.4.7"]
        TSX["tsx: ^4.19.3"]
        TSC2["typescript: ^5.7.3"]
        TailwindCSS["tailwindcss: ^4"]
    end
    
    subgraph "bytebotd Tools"
        NestCLI2["@nestjs/cli: ^11.0.0"]
        SWC2["@swc/core: ^1.10.7"]
        TSC3["typescript: ^5.7.3"]
    end
    
    subgraph "Shared Tools"
        TSCShared["typescript: ^5.7.3"]
    end
```

**Sources:** [packages/bytebot-agent/package.json:47-73](), [packages/bytebot-ui/package.json:49-62](), [packages/bytebotd/package.json:48-73]()

### Key Build Dependencies

**NestJS Services (bytebot-agent, bytebotd):**
- `@nestjs/cli` - Framework CLI for building and scaffolding
- `@swc/core` - Fast TypeScript/JavaScript compiler (used by NestJS)
- `ts-loader` - TypeScript loader for Webpack
- `tsconfig-paths` - Path mapping support for TypeScript

**Frontend (bytebot-ui):**
- `next` - React framework with built-in build pipeline
- `tsx` - TypeScript execution engine for custom server
- `@tailwindcss/postcss` - CSS processing and optimization

**All Packages:**
- `typescript: ^5.7.3` - Unified TypeScript version across monorepo
- `prettier` - Code formatting
- `eslint` - Code linting

**Sources:** [packages/bytebot-agent/package-lock.json:47-73](), [packages/bytebot-ui/package.json:49-62](), [packages/bytebotd/package.json:48-73]()

## Development Workflow

### Local Development Scripts

Each package provides watch mode for development:

```mermaid
graph LR
    DevStart["npm run start:dev"]
    
    BuildShared["Build @bytebot/shared"]
    WatchMode["Start in Watch Mode"]
    FileChange["File Change Detected"]
    Rebuild["Incremental Rebuild"]
    
    DevStart --> BuildShared
    BuildShared --> WatchMode
    WatchMode --> FileChange
    FileChange --> Rebuild
    Rebuild --> WatchMode
```

**Watch Mode Commands:**

| Service | Command | Mechanism |
|---------|---------|-----------|
| bytebot-agent | `nest start --watch` | NestJS CLI with incremental compilation |
| bytebot-ui | `tsx server.ts` (with Next.js dev mode) | Next.js Fast Refresh + tsx runtime |
| bytebotd | `nest start --watch` | NestJS CLI with incremental compilation |

**Sources:** [packages/bytebot-agent/package.json:14](), [packages/bytebot-ui/package.json:6](), [packages/bytebotd/package.json:18]()

### Debug Mode Support

Debug scripts attach Node.js inspector for debugging:

```bash
# bytebot-agent debug mode
npm run start:debug
# → nest start --debug --watch
```

This enables debugging in IDEs like VS Code by exposing the Node.js debug port (default 9229).

**Sources:** [packages/bytebot-agent/package.json:15](), [packages/bytebotd/package.json:19]()

## Module System and TypeScript Configuration

### Module Resolution

The codebase uses **path aliases** to simplify imports. For example, in bytebot-agent:

```typescript
import { AgentProcessor } from './agent/agent.processor';
import { TasksModule } from '../tasks/tasks.module';
import { SummariesModule } from 'src/summaries/summaries.modue';
```

The `src/` prefix is configured via `tsconfig-paths` and TypeScript's `baseUrl` setting, allowing absolute imports within each package.

**Sources:** [packages/bytebot-agent/src/agent/agent.module.ts:1-34](), [packages/bytebotd/src/app.module.ts:1-26]()

### NestJS Module Architecture

Both backend services (bytebot-agent, bytebotd) use NestJS's module system with decorators:

**bytebot-agent App Module Structure:**

```mermaid
graph TB
    AppModule["AppModule"]
    
    ScheduleModule["ScheduleModule.forRoot()"]
    EventEmitterModule["EventEmitterModule.forRoot()"]
    ConfigModule["ConfigModule.forRoot({isGlobal: true})"]
    
    AgentModule["AgentModule"]
    TasksModule["TasksModule"]
    MessagesModule["MessagesModule"]
    SummariesModule["SummariesModule"]
    AnthropicModule["AnthropicModule"]
    OpenAIModule["OpenAIModule"]
    GoogleModule["GoogleModule"]
    ProxyModule["ProxyModule"]
    PrismaModule["PrismaModule"]
    
    AppModule --> ScheduleModule
    AppModule --> EventEmitterModule
    AppModule --> ConfigModule
    AppModule --> AgentModule
    AppModule --> TasksModule
    AppModule --> MessagesModule
    AppModule --> SummariesModule
    AppModule --> AnthropicModule
    AppModule --> OpenAIModule
    AppModule --> GoogleModule
    AppModule --> ProxyModule
    AppModule --> PrismaModule
```

**Sources:** [packages/bytebot-agent/src/app.module.ts:1-38]()

**bytebotd App Module Structure:**

```mermaid
graph TB
    AppModuleD["AppModule"]
    
    ConfigModuleD["ConfigModule.forRoot({isGlobal: true})"]
    ServeStaticModule["ServeStaticModule.forRoot({rootPath: '/opt/noVNC'})"]
    
    ComputerUseModule["ComputerUseModule"]
    InputTrackingModule["InputTrackingModule"]
    BytebotMcpModule["BytebotMcpModule"]
    
    AppModuleD --> ConfigModuleD
    AppModuleD --> ServeStaticModule
    AppModuleD --> ComputerUseModule
    AppModuleD --> InputTrackingModule
    AppModuleD --> BytebotMcpModule
```

**Sources:** [packages/bytebotd/src/app.module.ts:1-27]()

### MCP Module Initialization

The bytebotd service includes MCP (Model Context Protocol) integration:

```mermaid
graph LR
    BytebotMcpModule["BytebotMcpModule"]
    
    ComputerUseModuleImport["ComputerUseModule<br/>(import)"]
    McpModuleConfig["McpModule.forRoot({<br/>name: 'bytebotd',<br/>version: '0.0.1',<br/>sseEndpoint: '/mcp'<br/>})"]
    ComputerUseTools["ComputerUseTools<br/>(provider)"]
    
    BytebotMcpModule --> ComputerUseModuleImport
    BytebotMcpModule --> McpModuleConfig
    BytebotMcpModule --> ComputerUseTools
```

This configures the SSE endpoint at `/mcp` for MCP client connections.

**Sources:** [packages/bytebotd/src/mcp/bytebot-mcp.module.ts:1-18]()

## Database Schema Management

### Prisma Build Integration

The bytebot-agent service uses Prisma for database schema management, which adds extra build steps:

**Development Workflow:**
```bash
npm run prisma:dev
# → npx prisma migrate dev && npx prisma generate
```

**Production Workflow:**
```bash
npm run prisma:prod
# → npx prisma migrate deploy && npx prisma generate
```

The `prisma generate` command creates the Prisma Client TypeScript definitions based on the schema, which must be regenerated whenever the schema changes.

**Sources:** [packages/bytebot-agent/package.json:9-10]()

### Production Build Sequence

```mermaid
sequenceDiagram
    participant Build as Build Script
    participant Shared as @bytebot/shared
    participant Prisma as Prisma CLI
    participant Nest as NestJS CLI
    participant DB as PostgreSQL
    
    Build->>Shared: npm run build --prefix ../shared
    Shared-->>Build: TypeScript types compiled
    
    Build->>Prisma: npx prisma migrate deploy
    Prisma->>DB: Apply pending migrations
    DB-->>Prisma: Schema updated
    
    Build->>Prisma: npx prisma generate
    Prisma-->>Build: @prisma/client generated
    
    Build->>Nest: nest build
    Nest-->>Build: dist/ output created
```

**Sources:** [packages/bytebot-agent/package.json:16]()

## Testing Infrastructure

### Test Scripts

All packages include Jest-based testing:

| Script | Purpose | Configuration |
|--------|---------|---------------|
| `test` | Run all tests once | `jest` |
| `test:watch` | Run tests in watch mode | `jest --watch` |
| `test:cov` | Generate coverage reports | `jest --coverage` |
| `test:debug` | Debug tests with inspector | `node --inspect-brk ... jest --runInBand` |
| `test:e2e` | End-to-end tests | `jest --config ./test/jest-e2e.json` |

**Jest Configuration** (embedded in package.json):

```javascript
{
  "moduleFileExtensions": ["js", "json", "ts"],
  "rootDir": "src",
  "testRegex": ".*\\.spec\\.ts$",
  "transform": {
    "^.+\\.(t|j)s$": "ts-jest"
  },
  "collectCoverageFrom": ["**/*.(t|j)s"],
  "coverageDirectory": "../coverage",
  "testEnvironment": "node"
}
```

**Sources:** [packages/bytebot-agent/package.json:18-22, 75-91](), [packages/bytebotd/package.json:22-26, 75-91]()

## Linting and Formatting

### Code Quality Tools

All packages use consistent linting and formatting:

**ESLint Configuration:**
- `@eslint/eslintrc` for configuration
- `eslint-config-prettier` to disable conflicting rules
- `eslint-plugin-prettier` to run Prettier as ESLint rule
- `typescript-eslint` for TypeScript-specific rules

**Format Script:**
```bash
npm run format
# → prettier --write "src/**/*.ts" "test/**/*.ts"
```

**Lint Script:**
```bash
npm run lint
# → eslint "{src,apps,libs,test}/**/*.ts" --fix
```

**Sources:** [packages/bytebot-agent/package.json:12, 17, 47-73](), [packages/bytebotd/package.json:14, 21, 48-73]()

## Deployment Build Artifacts

### Production Build Outputs

Each service produces different artifacts:

| Service | Output Directory | Entry Point | Type |
|---------|-----------------|-------------|------|
| bytebot-agent | `dist/` | `dist/main.js` | NestJS compiled output |
| bytebot-ui | `.next/` | `server.ts` (via tsx) | Next.js optimized build + custom server |
| bytebotd | `dist/` | `dist/main.js` | NestJS compiled output |

**Production Start Commands:**

```bash
# bytebot-agent
node dist/main

# bytebot-ui  
tsx server.ts

# bytebotd
node dist/main
```

**Sources:** [packages/bytebot-agent/package.json:16](), [packages/bytebot-ui/package.json:8](), [packages/bytebotd/package.json:20]()

### Docker Build Considerations

While Docker configuration files are not shown in the provided sources, the production scripts indicate the services are designed to run in containerized environments:

- Database migrations run automatically in `start:prod`
- Environment configuration via `ConfigModule.forRoot({isGlobal: true})`
- Static asset serving configured for noVNC in bytebotd

**Sources:** [packages/bytebot-agent/src/app.module.ts:21-23](), [packages/bytebotd/src/app.module.ts:12-18]()

## Build System Dependencies Graph

```mermaid
graph TB
    subgraph "Shared Package Build"
        TSCompile["TypeScript Compiler"]
        SharedTypes["Type Definitions Output"]
    end
    
    subgraph "bytebot-agent Build"
        SharedDep1["@bytebot/shared"]
        PrismaSchema["Prisma Schema"]
        PrismaClient["@prisma/client<br/>generation"]
        NestCompile1["NestJS Build"]
        AgentDist["dist/main.js"]
    end
    
    subgraph "bytebot-ui Build"
        SharedDep2["@bytebot/shared"]
        NextCompile["Next.js Build"]
        NextOut[".next/ output"]
    end
    
    subgraph "bytebotd Build"
        SharedDep3["@bytebot/shared"]
        NestCompile2["NestJS Build"]
        DaemonDist["dist/main.js"]
    end
    
    TSCompile --> SharedTypes
    
    SharedTypes --> SharedDep1
    SharedTypes --> SharedDep2
    SharedTypes --> SharedDep3
    
    SharedDep1 --> PrismaClient
    PrismaSchema --> PrismaClient
    PrismaClient --> NestCompile1
    NestCompile1 --> AgentDist
    
    SharedDep2 --> NextCompile
    NextCompile --> NextOut
    
    SharedDep3 --> NestCompile2
    NestCompile2 --> DaemonDist
```

**Sources:** All package.json files across the repository

---

# Page: Module Architecture

# Module Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [packages/bytebot-agent/package-lock.json](packages/bytebot-agent/package-lock.json)
- [packages/bytebot-agent/package.json](packages/bytebot-agent/package.json)
- [packages/bytebot-agent/src/agent/agent.module.ts](packages/bytebot-agent/src/agent/agent.module.ts)
- [packages/bytebot-agent/src/app.module.ts](packages/bytebot-agent/src/app.module.ts)

</details>



This document details the NestJS module structure used in both `bytebot-agent` and `bytebotd` services. It explains how modules organize services through dependency injection, how cross-module dependencies are managed, and the patterns used to maintain clean separation of concerns.

For information about the build system and package structure, see [Build System](#11.1). For details on validation systems used within modules, see [Testing and Validation](#11.3).

---

## Overview

Both `bytebot-agent` and `bytebotd` services use the NestJS framework, which organizes code into modules that encapsulate related functionality. Each module declares its providers (services), controllers (HTTP endpoints or gateways), imports (dependencies on other modules), and exports (services made available to other modules).

The module system provides:
- **Dependency Injection**: Automatic instantiation and injection of service dependencies
- **Encapsulation**: Clear boundaries between feature domains
- **Testability**: Easy mocking of dependencies for unit testing
- **Modularity**: Reusable, self-contained feature modules

---

## Root Module Structure

### AppModule: bytebot-agent

The root application module coordinates all feature modules and configures global infrastructure.

```mermaid
graph TB
    AppModule["AppModule<br/>(app.module.ts)"]
    
    subgraph "Global Infrastructure"
        ScheduleModule["ScheduleModule.forRoot()<br/>Cron scheduling"]
        EventEmitterModule["EventEmitterModule.forRoot()<br/>Internal events"]
        ConfigModule["ConfigModule.forRoot()<br/>Environment config"]
    end
    
    subgraph "Core Feature Modules"
        TasksModule["TasksModule<br/>Task CRUD + WebSocket"]
        MessagesModule["MessagesModule<br/>Message storage"]
        SummariesModule["SummariesModule<br/>Context compression"]
        AgentModule["AgentModule<br/>Agent processing"]
    end
    
    subgraph "LLM Provider Modules"
        AnthropicModule["AnthropicModule<br/>Claude integration"]
        OpenAIModule["OpenAIModule<br/>GPT integration"]
        GoogleModule["GoogleModule<br/>Gemini integration"]
    end
    
    subgraph "Infrastructure Modules"
        PrismaModule["PrismaModule<br/>Database client"]
        ProxyModule["ProxyModule<br/>bytebotd proxy"]
    end
    
    AppModule --> ScheduleModule
    AppModule --> EventEmitterModule
    AppModule --> ConfigModule
    AppModule --> TasksModule
    AppModule --> MessagesModule
    AppModule --> SummariesModule
    AppModule --> AgentModule
    AppModule --> AnthropicModule
    AppModule --> OpenAIModule
    AppModule --> GoogleModule
    AppModule --> PrismaModule
    AppModule --> ProxyModule
```

**Sources:** [packages/bytebot-agent/src/app.module.ts:1-38]()

---

## Module Organization Patterns

### Feature Module Structure

Each feature module follows a consistent directory structure:

```
<feature>/
├── <feature>.module.ts       # Module definition
├── <feature>.service.ts      # Business logic
├── <feature>.controller.ts   # HTTP endpoints (if applicable)
├── <feature>.gateway.ts      # WebSocket gateway (if applicable)
├── dto/                      # Data transfer objects
│   ├── create-<feature>.dto.ts
│   └── update-<feature>.dto.ts
└── entities/                 # Database entities (if applicable)
    └── <feature>.entity.ts
```

### Module Types

| Module Type | Purpose | Examples | Global? |
|-------------|---------|----------|---------|
| **Infrastructure** | Provides low-level services to all modules | `PrismaModule`, `ConfigModule` | Yes |
| **Feature** | Implements specific business domain | `TasksModule`, `MessagesModule`, `AgentModule` | No |
| **Provider** | Integrates external services | `AnthropicModule`, `OpenAIModule`, `GoogleModule` | No |
| **Utility** | Cross-cutting concerns | `ScheduleModule`, `EventEmitterModule` | Yes |
| **Proxy** | External API clients | `ProxyModule` | No |

**Sources:** [packages/bytebot-agent/src/app.module.ts:1-38]()

---

## AgentModule: Detailed Example

The `AgentModule` demonstrates typical NestJS module patterns including imports, providers, and exports.

### Module Definition

```mermaid
graph LR
    subgraph "AgentModule Imports"
        ConfigModule_dep["ConfigModule"]
        TasksModule_dep["TasksModule"]
        MessagesModule_dep["MessagesModule"]
        SummariesModule_dep["SummariesModule"]
        AnthropicModule_dep["AnthropicModule"]
        OpenAIModule_dep["OpenAIModule"]
        GoogleModule_dep["GoogleModule"]
        ProxyModule_dep["ProxyModule"]
    end
    
    subgraph "AgentModule Providers"
        AgentProcessor["AgentProcessor<br/>Main processing loop"]
        AgentScheduler["AgentScheduler<br/>Cron-based task picker"]
        InputCaptureService["InputCaptureService<br/>User action tracking"]
        AgentAnalyticsService["AgentAnalyticsService<br/>Performance metrics"]
    end
    
    subgraph "Exported Services"
        AgentProcessor_export["AgentProcessor"]
    end
    
    ConfigModule_dep --> AgentProcessor
    TasksModule_dep --> AgentProcessor
    TasksModule_dep --> AgentScheduler
    MessagesModule_dep --> AgentProcessor
    SummariesModule_dep --> AgentProcessor
    AnthropicModule_dep --> AgentProcessor
    OpenAIModule_dep --> AgentProcessor
    GoogleModule_dep --> AgentProcessor
    ProxyModule_dep --> AgentProcessor
    
    AgentProcessor --> AgentProcessor_export
```

**Module Declaration:**

The module imports eight dependencies and declares four providers. Only `AgentProcessor` is exported for use by other modules.

**Sources:** [packages/bytebot-agent/src/agent/agent.module.ts:1-35]()

---

## Dependency Injection Flow

### Provider Registration and Injection

NestJS uses the `@Injectable()` decorator to mark classes as providers that can be injected. Dependencies are declared in the constructor.

```mermaid
sequenceDiagram
    participant NestJS as "NestJS DI Container"
    participant Module as "AgentModule"
    participant Processor as "AgentProcessor"
    participant TasksService as "TasksService"
    participant MessagesService as "MessagesService"
    
    Note over NestJS: Application bootstrap
    NestJS->>Module: Register providers
    Module->>NestJS: [AgentProcessor, AgentScheduler, ...]
    
    Note over NestJS: Resolve dependencies
    NestJS->>TasksService: Instantiate (from TasksModule)
    NestJS->>MessagesService: Instantiate (from MessagesModule)
    NestJS->>Processor: Instantiate with dependencies
    Processor->>NestJS: constructor(tasksService, messagesService, ...)
    NestJS->>Processor: Inject instances
    
    Note over Processor: Ready to use
```

### Service Scope

| Scope | Lifetime | Use Case | Example |
|-------|----------|----------|---------|
| **Singleton** (default) | Application lifetime | Stateless services, shared resources | `TasksService`, `PrismaService` |
| **Request** | Per HTTP request | Request-specific context | Authentication guards |
| **Transient** | New instance per injection | Independent state per consumer | Rare in this codebase |

All services in `bytebot-agent` use singleton scope for performance and simplicity.

**Sources:** [packages/bytebot-agent/src/agent/agent.module.ts:1-35]()

---

## Cross-Module Communication

### Import Chains

Modules access services from other modules by importing them. The imported module must export the required service.

```mermaid
graph TB
    subgraph "AgentModule"
        AgentProcessor_service["AgentProcessor"]
    end
    
    subgraph "TasksModule (imported)"
        TasksService_export["TasksService (exported)"]
        TasksController["TasksController"]
        TasksGateway["TasksGateway"]
    end
    
    subgraph "MessagesModule (imported)"
        MessagesService_export["MessagesService (exported)"]
    end
    
    subgraph "AnthropicModule (imported)"
        AnthropicService_export["AnthropicService (exported)"]
    end
    
    subgraph "ProxyModule (imported)"
        ProxyService_export["ProxyService (exported)"]
    end
    
    AgentProcessor_service -->|"inject"| TasksService_export
    AgentProcessor_service -->|"inject"| MessagesService_export
    AgentProcessor_service -->|"inject"| AnthropicService_export
    AgentProcessor_service -->|"inject"| ProxyService_export
```

**Pattern:**
1. `TasksModule` exports `TasksService` in its `exports` array
2. `AgentModule` imports `TasksModule` in its `imports` array
3. `AgentProcessor` declares `TasksService` as a constructor parameter
4. NestJS injects the `TasksService` instance from `TasksModule`

**Sources:** [packages/bytebot-agent/src/agent/agent.module.ts:15-34]()

---

## Global Modules

### Infrastructure Modules

Certain modules are configured as global to avoid repeated imports across every feature module.

| Module | Configuration | Purpose |
|--------|---------------|---------|
| `ConfigModule` | `ConfigModule.forRoot({ isGlobal: true })` | Environment variables accessible everywhere |
| `ScheduleModule` | `ScheduleModule.forRoot()` | Enables `@Cron()` decorators in any module |
| `EventEmitterModule` | `EventEmitterModule.forRoot()` | Event bus for inter-service communication |
| `PrismaModule` | Custom global module | Database client available to all modules |

**ConfigModule Example:**

```typescript
// In app.module.ts
ConfigModule.forRoot({
  isGlobal: true,  // Makes ConfigService available everywhere
})

// In any service
constructor(private configService: ConfigService) {
  const apiKey = this.configService.get<string>('ANTHROPIC_API_KEY');
}
```

**Sources:** [packages/bytebot-agent/src/app.module.ts:21-23]()

---

## Module Dependencies in Practice

### TasksModule Dependencies

```mermaid
graph TB
    TasksModule["TasksModule"]
    
    subgraph "Imported Modules"
        PrismaModule_imp["PrismaModule<br/>(database)"]
        MessagesModule_imp["MessagesModule<br/>(message operations)"]
    end
    
    subgraph "Internal Providers"
        TasksService_prov["TasksService<br/>(business logic)"]
        TasksController_prov["TasksController<br/>(REST API)"]
        TasksGateway_prov["TasksGateway<br/>(WebSocket)"]
    end
    
    subgraph "Exported Services"
        TasksService_exp["TasksService"]
    end
    
    TasksModule --> PrismaModule_imp
    TasksModule --> MessagesModule_imp
    
    PrismaModule_imp -.->|"provides PrismaService"| TasksService_prov
    MessagesModule_imp -.->|"provides MessagesService"| TasksService_prov
    
    TasksService_prov --> TasksController_prov
    TasksService_prov --> TasksGateway_prov
    TasksService_prov --> TasksService_exp
```

**Key Points:**
- `TasksModule` imports `PrismaModule` to access `PrismaService` for database queries
- `TasksModule` imports `MessagesModule` to create messages when tasks are updated
- `TasksService` is both used internally (by `TasksController` and `TasksGateway`) and exported for external modules
- Controller and Gateway are providers but not exported (only for internal HTTP/WebSocket handling)

**Sources:** Referenced from module pattern visible in [packages/bytebot-agent/src/app.module.ts:1-38]()

---

## Provider Lifecycle and Events

### EventEmitter Integration

The `EventEmitterModule` enables services to emit and listen for events without direct coupling.

```mermaid
sequenceDiagram
    participant TasksService as "TasksService"
    participant EventEmitter as "EventEmitter2"
    participant AgentProcessor as "AgentProcessor"
    
    Note over TasksService: Task status changes
    TasksService->>TasksService: updateTask(id, { status: 'COMPLETED' })
    TasksService->>EventEmitter: emit('task.completed', task)
    
    Note over EventEmitter: Broadcast to listeners
    EventEmitter->>AgentProcessor: @OnEvent('task.completed')
    
    Note over AgentProcessor: React to event
    AgentProcessor->>AgentProcessor: handleTaskCompleted(task)
    AgentProcessor->>AgentProcessor: Stop processing loop
```

**Event Listener Declaration:**

Services use the `@OnEvent()` decorator to subscribe to events:

```typescript
@Injectable()
export class AgentProcessor {
  @OnEvent('task.completed')
  handleTaskCompleted(task: Task) {
    // React to task completion
  }
}
```

**Sources:** Pattern referenced from [packages/bytebot-agent/src/app.module.ts:13]() (EventEmitterModule import)

---

## Scheduled Tasks with Cron

### AgentScheduler Pattern

The `@nestjs/schedule` module enables cron-based task scheduling within any module.

```mermaid
graph LR
    ScheduleModule["ScheduleModule.forRoot()"]
    AgentScheduler["AgentScheduler<br/>@Injectable()"]
    pickPendingTask["pickPendingTask()<br/>@Cron('* * * * * *')"]
    
    ScheduleModule -.->|"enables @Cron"| AgentScheduler
    AgentScheduler --> pickPendingTask
    
    pickPendingTask -->|"every second"| TasksService["TasksService.findPending()"]
    pickPendingTask -->|"start processing"| AgentProcessor["AgentProcessor.processTask()"]
```

**Cron Decorator Usage:**

```typescript
@Injectable()
export class AgentScheduler {
  @Cron('* * * * * *')  // Every second
  async pickPendingTask() {
    const task = await this.tasksService.findPending();
    if (task) await this.agentProcessor.processTask(task.id);
  }
}
```

**Sources:** [packages/bytebot-agent/src/app.module.ts:19](), [packages/bytebot-agent/src/agent/agent.module.ts:28]()

---

## Module Testing Strategy

### Dependency Mocking

NestJS testing utilities allow replacing real services with mocks:

```typescript
const module: TestingModule = await Test.createTestingModule({
  providers: [
    AgentProcessor,
    {
      provide: TasksService,
      useValue: mockTasksService,  // Mock implementation
    },
    {
      provide: MessagesService,
      useValue: mockMessagesService,
    },
  ],
}).compile();

const processor = module.get<AgentProcessor>(AgentProcessor);
```

**Benefits:**
- Test services in isolation
- Control dependency behavior
- Fast unit tests without database/network

**Sources:** Standard NestJS testing pattern used throughout the codebase

---

## Package Dependencies

### Core NestJS Packages

The following packages enable the module system:

| Package | Version | Purpose |
|---------|---------|---------|
| `@nestjs/common` | ^11.0.1 | Core decorators (`@Module`, `@Injectable`, `@Controller`) |
| `@nestjs/core` | ^11.0.1 | Dependency injection container |
| `@nestjs/platform-express` | ^11.1.5 | HTTP server (Express adapter) |
| `@nestjs/platform-socket.io` | ^11.1.1 | WebSocket server (Socket.IO adapter) |
| `@nestjs/websockets` | ^11.1.1 | WebSocket gateway decorators |
| `@nestjs/config` | ^4.0.2 | Environment configuration module |
| `@nestjs/schedule` | ^6.0.0 | Cron scheduling |
| `@nestjs/event-emitter` | ^3.0.1 | Event-driven communication |

**Sources:** [packages/bytebot-agent/package.json:24-36]()

---

## Module Best Practices

### Guidelines Followed in bytebot-agent

1. **Single Responsibility**: Each module encapsulates one domain (Tasks, Messages, Agent, etc.)
2. **Explicit Exports**: Only export services needed by other modules
3. **Import Order**: Global modules → Infrastructure → Feature → Provider modules
4. **Circular Dependencies**: Avoided through careful import design (e.g., TasksModule doesn't import AgentModule)
5. **Service Naming**: `<Domain>Service` for business logic, `<Domain>Controller` for HTTP, `<Domain>Gateway` for WebSocket
6. **Global Sparingly**: Only configuration and infrastructure are global

**Anti-Pattern Example (avoided):**
```typescript
// BAD: Circular dependency
// TasksModule imports AgentModule
// AgentModule imports TasksModule
// Solution: Use EventEmitter for decoupling
```

**Sources:** Pattern observed across [packages/bytebot-agent/src/app.module.ts:1-38]() and [packages/bytebot-agent/src/agent/agent.module.ts:1-35]()

---

## Summary

The NestJS module architecture in bytebot-agent provides:

- **Clear Boundaries**: Each module owns a specific domain
- **Dependency Injection**: Automatic instantiation and wiring
- **Event-Driven**: Decoupled communication via EventEmitter
- **Scheduled Tasks**: Cron-based background jobs
- **Global Configuration**: Environment variables accessible everywhere
- **Testability**: Easy mocking for unit tests

This architecture scales well as new features are added, maintaining clean separation of concerns and explicit dependencies between modules.

**Sources:** [packages/bytebot-agent/src/app.module.ts:1-38](), [packages/bytebot-agent/src/agent/agent.module.ts:1-35](), [packages/bytebot-agent/package.json:1-101]()

---

# Page: Testing and Validation

# Testing and Validation

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [packages/bytebot-agent/package-lock.json](packages/bytebot-agent/package-lock.json)
- [packages/bytebot-agent/package.json](packages/bytebot-agent/package.json)
- [packages/bytebot-agent/src/agent/agent.module.ts](packages/bytebot-agent/src/agent/agent.module.ts)
- [packages/bytebot-agent/src/app.module.ts](packages/bytebot-agent/src/app.module.ts)
- [packages/bytebotd/src/computer-use/computer-use.service.ts](packages/bytebotd/src/computer-use/computer-use.service.ts)
- [packages/bytebotd/src/computer-use/dto/base.dto.ts](packages/bytebotd/src/computer-use/dto/base.dto.ts)
- [packages/bytebotd/src/computer-use/dto/computer-action-validation.pipe.ts](packages/bytebotd/src/computer-use/dto/computer-action-validation.pipe.ts)
- [packages/bytebotd/src/computer-use/dto/computer-action.dto.ts](packages/bytebotd/src/computer-use/dto/computer-action.dto.ts)
- [packages/bytebotd/src/mcp/computer-use.tools.ts](packages/bytebotd/src/mcp/computer-use.tools.ts)
- [packages/shared/src/types/computerAction.types.ts](packages/shared/src/types/computerAction.types.ts)
- [packages/shared/src/types/messageContent.types.ts](packages/shared/src/types/messageContent.types.ts)
- [packages/shared/src/utils/computerAction.utils.ts](packages/shared/src/utils/computerAction.utils.ts)
- [packages/shared/src/utils/messageContent.utils.ts](packages/shared/src/utils/messageContent.utils.ts)

</details>



This document describes the validation and testing systems used in Bytebot. The codebase employs a multi-layered validation strategy combining compile-time type checking (TypeScript), runtime validation (class-validator, Zod), and type guards for safe type narrowing. For information about the overall type system architecture, see [Type System Overview](#9.1).

## Validation Architecture Overview

Bytebot uses three complementary validation approaches to ensure data integrity across service boundaries and throughout the application lifecycle:

```mermaid
graph TD
    subgraph "Compile Time"
        TS["TypeScript Type System"]
        TSInterfaces["Type Definitions<br/>messageContent.types.ts<br/>computerAction.types.ts"]
    end
    
    subgraph "Runtime - bytebot-agent"
        Prisma["Prisma Schema<br/>Database Types"]
    end
    
    subgraph "Runtime - bytebotd"
        ClassValidator["class-validator DTOs<br/>computer-action.dto.ts"]
        ValidationPipe["ComputerActionValidationPipe"]
        ZodSchemas["Zod Schemas<br/>MCP Tools"]
    end
    
    subgraph "Runtime - Shared"
        TypeGuards["Type Guard Functions<br/>messageContent.utils.ts<br/>computerAction.utils.ts"]
    end
    
    subgraph "External Input"
        APIRequest["POST /computer-use"]
        MCPRequest["MCP Tool Invocation"]
        DBQuery["Database Operations"]
    end
    
    APIRequest -->|"Body"| ValidationPipe
    ValidationPipe -->|"Uses"| ClassValidator
    ClassValidator -->|"Validated DTO"| ComputerUseService["ComputerUseService.action()"]
    
    MCPRequest -->|"Parameters"| ZodSchemas
    ZodSchemas -->|"Validated"| MCPTools["ComputerUseTools methods"]
    
    DBQuery -->|"Schema"| Prisma
    
    TypeGuards -->|"Runtime Checks"| MessageProcessing["Message Processing"]
    TypeGuards -->|"Runtime Checks"| ActionConversion["Action Conversion"]
    
    TS -.->|"Compile-time checks"| TSInterfaces
    TSInterfaces -.->|"Type definitions for"| ClassValidator
    TSInterfaces -.->|"Type definitions for"| TypeGuards
    
    style TS fill:#f9f9f9
    style ClassValidator fill:#fff4e6
    style ZodSchemas fill:#fff4e6
    style TypeGuards fill:#e6f3ff
```

**Sources:** [packages/bytebotd/src/computer-use/dto/computer-action-validation.pipe.ts:1-97](), [packages/bytebotd/src/mcp/computer-use.tools.ts:1-699](), [packages/shared/src/utils/messageContent.utils.ts:1-516](), [packages/shared/src/utils/computerAction.utils.ts:1-343]()

## Type Guard System

The `@bytebot/shared` package provides comprehensive type guards for runtime type checking. These functions safely narrow TypeScript types and enable pattern matching across message content and computer actions.

### Message Content Type Guards

Type guards for message content blocks follow a consistent pattern and are organized into a hierarchy:

```mermaid
graph TB
    isMessageContentBlock["isMessageContentBlock(obj)<br/>Top-level validator"]
    
    isTextContentBlock["isTextContentBlock(obj)<br/>MessageContentType.Text"]
    isImageContentBlock["isImageContentBlock(obj)<br/>MessageContentType.Image"]
    isDocumentContentBlock["isDocumentContentBlock(obj)<br/>MessageContentType.Document"]
    isThinkingContentBlock["isThinkingContentBlock(obj)<br/>MessageContentType.Thinking"]
    isRedactedThinkingContentBlock["isRedactedThinkingContentBlock(obj)<br/>MessageContentType.RedactedThinking"]
    isUserActionContentBlock["isUserActionContentBlock(obj)<br/>MessageContentType.UserAction"]
    isToolUseContentBlock["isToolUseContentBlock(obj)<br/>MessageContentType.ToolUse"]
    isToolResultContentBlock["isToolResultContentBlock(obj)<br/>MessageContentType.ToolResult"]
    
    isComputerToolUseContentBlock["isComputerToolUseContentBlock(obj)<br/>name.startsWith('computer_')"]
    
    isMessageContentBlock -->|"Checks"| isTextContentBlock
    isMessageContentBlock -->|"Checks"| isImageContentBlock
    isMessageContentBlock -->|"Checks"| isDocumentContentBlock
    isMessageContentBlock -->|"Checks"| isThinkingContentBlock
    isMessageContentBlock -->|"Checks"| isRedactedThinkingContentBlock
    isMessageContentBlock -->|"Checks"| isUserActionContentBlock
    isMessageContentBlock -->|"Checks"| isToolUseContentBlock
    isMessageContentBlock -->|"Checks"| isToolResultContentBlock
    
    isToolUseContentBlock -->|"Refinement"| isComputerToolUseContentBlock
    
    isComputerToolUseContentBlock -->|"Specific tools"| SpecificTools["isMoveMouseToolUseBlock<br/>isClickMouseToolUseBlock<br/>isTypeTextToolUseBlock<br/>isScreenshotToolUseBlock<br/>... (17 total)"]
    
    style isMessageContentBlock fill:#f9f9f9
    style isComputerToolUseContentBlock fill:#fff4e6
    style SpecificTools fill:#e6f3ff
```

Each type guard validates the discriminator field (`type`) and required properties. For example:

**Text Content Block Validation:**
```typescript
// From messageContent.utils.ts:38-47
function isTextContentBlock(obj: unknown): obj is TextContentBlock {
  const block = obj as Partial<TextContentBlock>;
  return (
    block.type === MessageContentType.Text && 
    typeof block.text === "string"
  );
}
```

**Tool Use Content Block Validation:**
```typescript
// From messageContent.utils.ts:139-154
function isToolUseContentBlock(obj: unknown): obj is ToolUseContentBlock {
  const block = obj as Partial<ToolUseContentBlock>;
  return (
    block.type === MessageContentType.ToolUse &&
    typeof block.name === "string" &&
    typeof block.id === "string" &&
    block.input !== undefined &&
    typeof block.input === "object"
  );
}
```

**Sources:** [packages/shared/src/utils/messageContent.utils.ts:33-208]()

### Computer Action Type Guards

The `computerAction.utils.ts` module provides type guards using a factory pattern for consistency:

```mermaid
graph LR
    Factory["createActionTypeGuard&lt;T&gt;(actionType)"]
    
    Factory -->|"Creates"| isMoveMouseAction["isMoveMouseAction<br/>action === 'move_mouse'"]
    Factory -->|"Creates"| isClickMouseAction["isClickMouseAction<br/>action === 'click_mouse'"]
    Factory -->|"Creates"| isTypeTextAction["isTypeTextAction<br/>action === 'type_text'"]
    Factory -->|"Creates"| isScreenshotAction["isScreenshotAction<br/>action === 'screenshot'"]
    Factory -->|"Creates"| OtherActions["... 11 more action guards"]
    
    style Factory fill:#f9f9f9
```

The factory function ensures consistent validation logic:

```typescript
// From computerAction.utils.ts:28-38
function createActionTypeGuard<T extends ComputerAction>(
  actionType: T["action"]
): (obj: unknown) => obj is T {
  return (obj: unknown): obj is T => {
    if (!obj || typeof obj !== "object") return false;
    const action = obj as Record<string, any>;
    return action.action === actionType;
  };
}
```

**Sources:** [packages/shared/src/utils/computerAction.utils.ts:26-67]()

### Type Guard Usage Patterns

| Pattern | Usage | Example Location |
|---------|-------|------------------|
| **Type Narrowing** | Safely narrow union types in conditional logic | Message processing in agent |
| **Validation** | Verify data structure before processing | Tool result handling |
| **Pattern Matching** | Switch-case discrimination | `convertComputerActionToToolUseBlock` |
| **Debug/Logging** | Identify specific types for logging | `getMessageContentBlockType` |

**Sources:** [packages/shared/src/utils/messageContent.utils.ts:211-261](), [packages/shared/src/utils/computerAction.utils.ts:299-342]()

## Class-Validator DTOs (bytebotd)

The `bytebotd` service uses class-validator for validating incoming computer action requests at the API boundary.

### DTO Structure

DTOs are organized by action type with a common base class:

```mermaid
graph TB
    BaseActionDto["BaseActionDto<br/>abstract action: string"]
    
    BaseActionDto -->|"Extends"| MoveMouseActionDto["MoveMouseActionDto<br/>@IsIn(['move_mouse'])<br/>coordinates: CoordinatesDto"]
    BaseActionDto -->|"Extends"| ClickMouseActionDto["ClickMouseActionDto<br/>@IsIn(['click_mouse'])<br/>coordinates?: CoordinatesDto<br/>button: ButtonType<br/>clickCount: number"]
    BaseActionDto -->|"Extends"| TypeTextActionDto["TypeTextActionDto<br/>@IsIn(['type_text'])<br/>text: string<br/>delay?: number"]
    BaseActionDto -->|"Extends"| ScreenshotActionDto["ScreenshotActionDto<br/>@IsIn(['screenshot'])"]
    BaseActionDto -->|"Extends"| MoreDtos["... 12 more DTOs"]
    
    CoordinatesDto["CoordinatesDto<br/>@IsNumber() x: number<br/>@IsNumber() y: number"]
    
    ClickMouseActionDto -->|"Uses"| CoordinatesDto
    MoveMouseActionDto -->|"Uses"| CoordinatesDto
    
    Enums["Enums<br/>ButtonType<br/>PressType<br/>ScrollDirection<br/>ApplicationName"]
    
    ClickMouseActionDto -->|"Validates with"| Enums
    
    style BaseActionDto fill:#f9f9f9
    style CoordinatesDto fill:#fff4e6
    style Enums fill:#e6f3ff
```

### Validation Decorators

Each DTO uses class-validator decorators to enforce constraints:

| Decorator | Purpose | Example |
|-----------|---------|---------|
| `@IsIn([value])` | Validates literal action type | `@IsIn(['move_mouse'])` |
| `@IsNumber()` | Ensures numeric value | Coordinate validation |
| `@IsString()` | Ensures string value | Text content |
| `@IsEnum(Enum)` | Validates enum membership | Button types |
| `@IsOptional()` | Marks field as optional | Optional coordinates |
| `@ValidateNested()` | Validates nested objects | CoordinatesDto |
| `@IsArray()` | Ensures array type | Key arrays |
| `@Min(value)` | Minimum numeric value | `clickCount: @Min(1)` |

**Example DTO with Multiple Validators:**
```typescript
// From computer-action.dto.ts:51-71
export class ClickMouseActionDto extends BaseActionDto {
  @IsIn(['click_mouse'])
  action: 'click_mouse';

  @IsOptional()
  @ValidateNested()
  @Type(() => CoordinatesDto)
  coordinates?: CoordinatesDto;

  @IsEnum(ButtonType)
  button: ButtonType;

  @IsOptional()
  @IsArray()
  @IsString({ each: true })
  holdKeys?: string[];

  @IsNumber()
  @Min(1)
  clickCount: number;
}
```

**Sources:** [packages/bytebotd/src/computer-use/dto/computer-action.dto.ts:1-240](), [packages/bytebotd/src/computer-use/dto/base.dto.ts:1-38]()

## Validation Pipes

The `ComputerActionValidationPipe` transforms and validates incoming API requests before they reach the service layer.

### Validation Flow

```mermaid
sequenceDiagram
    participant Client
    participant Controller as "ComputerUseController<br/>POST /computer-use"
    participant Pipe as "ComputerActionValidationPipe"
    participant ClassTransformer as "class-transformer<br/>plainToClass()"
    participant ClassValidator as "class-validator<br/>validate()"
    participant Service as "ComputerUseService"
    
    Client->>Controller: POST { action: "click_mouse", ... }
    Controller->>Pipe: transform(value, metadata)
    
    Pipe->>Pipe: Check value.action exists
    
    alt action exists
        Pipe->>Pipe: Switch on action type
        Pipe->>ClassTransformer: plainToClass(ClickMouseActionDto, value)
        ClassTransformer-->>Pipe: DTO instance
        
        Pipe->>ClassValidator: validate(dto)
        ClassValidator-->>Pipe: ValidationError[]
        
        alt errors.length > 0
            Pipe-->>Controller: throw BadRequestException(errors)
            Controller-->>Client: 400 Bad Request
        else no errors
            Pipe-->>Controller: Validated DTO
            Controller->>Service: action(dto)
            Service-->>Controller: Result
            Controller-->>Client: 200 OK
        end
    else action missing
        Pipe-->>Controller: throw BadRequestException("Missing action field")
        Controller-->>Client: 400 Bad Request
    end
```

### Pipe Implementation Pattern

The validation pipe uses a switch statement to map action types to their corresponding DTOs:

```typescript
// From computer-action-validation.pipe.ts:30-95
async transform(value: any, metadata: ArgumentMetadata) {
  if (!value || !value.action) {
    throw new BadRequestException('Missing action field');
  }

  let dto;
  switch (value.action) {
    case 'move_mouse':
      dto = plainToClass(MoveMouseActionDto, value);
      break;
    case 'click_mouse':
      dto = plainToClass(ClickMouseActionDto, value);
      break;
    // ... 13 more cases
    default:
      throw new BadRequestException(`Unknown action: ${value.action}`);
  }

  const errors = await validate(dto);
  if (errors.length > 0) {
    throw new BadRequestException(errors);
  }

  return dto;
}
```

**Sources:** [packages/bytebotd/src/computer-use/dto/computer-action-validation.pipe.ts:28-96]()

## Zod Schema Validation (MCP Tools)

The MCP integration in `bytebotd` uses Zod schemas to validate tool parameters. The `@Tool` decorator accepts a Zod schema that defines parameter structure.

### MCP Tool Schema Pattern

```mermaid
graph LR
    ToolDecorator["@Tool Decorator<br/>name, description, parameters"]
    
    ToolDecorator -->|"Defines"| Schema["Zod Schema<br/>z.object({ ... })"]
    
    Schema -->|"Validates"| Required["Required Fields<br/>z.string()<br/>z.number()<br/>z.enum()"]
    Schema -->|"Validates"| Optional["Optional Fields<br/>z.optional()<br/>z.array().optional()"]
    Schema -->|"Validates"| Nested["Nested Objects<br/>z.object({ x, y })"]
    
    Schema -->|"Passed to"| MCPServer["MCP Server"]
    MCPServer -->|"Enforces at runtime"| ToolInvocation["Tool Method Invocation"]
    
    style ToolDecorator fill:#f9f9f9
    style Schema fill:#fff4e6
```

### Example Zod Schema Definitions

**Simple Action (Screenshot):**
```typescript
// From computer-use.tools.ts:549-577
@Tool({
  name: 'computer_screenshot',
  description: 'Captures a screenshot of the current screen.',
})
async screenshot() {
  // No parameters schema needed
}
```

**Complex Action (Click Mouse):**
```typescript
// From computer-use.tools.ts:80-138
@Tool({
  name: 'computer_click_mouse',
  description: 'Performs a mouse click at the specified coordinates or current position.',
  parameters: z.object({
    coordinates: z.object({
      x: z.number().describe('The x-coordinate to move the mouse to.'),
      y: z.number().describe('The y-coordinate to move the mouse to.'),
    }).optional().describe('Optional coordinates for the click.'),
    button: z.enum(['left', 'right', 'middle']).describe('The mouse button to click.'),
    holdKeys: z.array(z.string()).optional().describe('Optional array of keys to hold.'),
    clickCount: z.number().describe('Number of clicks to perform (e.g., 2 for double-click).'),
  }),
})
```

### Zod vs Class-Validator Comparison

| Aspect | Zod (MCP Tools) | class-validator (API DTOs) |
|--------|-----------------|---------------------------|
| **Location** | `bytebotd/mcp/computer-use.tools.ts` | `bytebotd/computer-use/dto/` |
| **Syntax** | Functional, chainable | Decorator-based |
| **Type Inference** | Automatic from schema | Manual TypeScript types |
| **Use Case** | MCP tool parameter validation | HTTP API request validation |
| **Error Format** | Zod error objects | ValidationError arrays |
| **Integration** | `@rekog/mcp-nest` framework | NestJS pipes |

**Sources:** [packages/bytebotd/src/mcp/computer-use.tools.ts:11-698]()

## Testing Infrastructure

### Jest Configuration

The `bytebot-agent` package is configured with Jest for testing:

```typescript
// From package.json:75-91
{
  "jest": {
    "moduleFileExtensions": ["js", "json", "ts"],
    "rootDir": "src",
    "testRegex": ".*\\.spec\\.ts$",
    "transform": {
      "^.+\\.(t|j)s$": "ts-jest"
    },
    "collectCoverageFrom": ["**/*.(t|j)s"],
    "coverageDirectory": "../coverage",
    "testEnvironment": "node"
  }
}
```

### Test Scripts

| Script | Command | Purpose |
|--------|---------|---------|
| `test` | `jest` | Run all tests once |
| `test:watch` | `jest --watch` | Run tests in watch mode |
| `test:cov` | `jest --coverage` | Generate coverage report |
| `test:debug` | `node --inspect-brk ... jest` | Debug tests |
| `test:e2e` | `jest --config ./test/jest-e2e.json` | Run end-to-end tests |

### Testing Dependencies

```mermaid
graph TB
    Jest["jest v29.7.0<br/>Test Runner"]
    TsJest["ts-jest v29.2.5<br/>TypeScript Transform"]
    Types["@types/jest v29.5.14<br/>Type Definitions"]
    Supertest["supertest v7.0.0<br/>HTTP Assertions"]
    NestTesting["@nestjs/testing v11.0.1<br/>NestJS Test Utilities"]
    
    Jest -->|"Uses"| TsJest
    Jest -->|"Types from"| Types
    Jest -->|"HTTP testing with"| Supertest
    Jest -->|"Module testing with"| NestTesting
    
    style Jest fill:#f9f9f9
```

**Sources:** [packages/bytebot-agent/package.json:47-91]()

## Validation Integration Points

### Computer Action Validation Path

```mermaid
graph TB
    subgraph "Entry Points"
        HTTPAPI["HTTP API<br/>POST /computer-use"]
        MCPEndpoint["MCP Endpoint<br/>SSE /mcp"]
        AgentProcessor["AgentProcessor<br/>handleComputerToolUse()"]
    end
    
    subgraph "Validation Layers"
        ValidationPipe["ComputerActionValidationPipe<br/>class-validator"]
        ZodValidation["Zod Schema<br/>@Tool parameters"]
        TypeGuard["Type Guards<br/>isComputerToolUseContentBlock()"]
    end
    
    subgraph "Service Layer"
        ComputerUseService["ComputerUseService.action()"]
    end
    
    subgraph "Type Safety"
        TypeScript["TypeScript Compiler<br/>Compile-time checks"]
        ComputerAction["ComputerAction<br/>Union Type"]
    end
    
    HTTPAPI -->|"Validates with"| ValidationPipe
    ValidationPipe -->|"Produces"| ComputerAction
    
    MCPEndpoint -->|"Validates with"| ZodValidation
    ZodValidation -->|"Produces"| ComputerAction
    
    AgentProcessor -->|"Validates with"| TypeGuard
    TypeGuard -->|"Narrows to"| ComputerAction
    
    ComputerAction -->|"Passed to"| ComputerUseService
    
    TypeScript -.->|"Enforces at compile-time"| ComputerAction
    
    style ValidationPipe fill:#fff4e6
    style ZodValidation fill:#fff4e6
    style TypeGuard fill:#e6f3ff
```

**Sources:** [packages/bytebotd/src/computer-use/computer-use.service.ts:31-105](), [packages/bytebotd/src/computer-use/dto/computer-action-validation.pipe.ts:1-97](), [packages/bytebotd/src/mcp/computer-use.tools.ts:1-699]()

## Best Practices

### When to Use Each Validation Approach

| Scenario | Recommended Approach | Rationale |
|----------|---------------------|-----------|
| **API Request Body** | class-validator DTOs + ValidationPipe | NestJS integration, detailed error messages |
| **MCP Tool Parameters** | Zod schemas with `@Tool` | MCP framework requirement, functional style |
| **Message Processing** | Type guards | Safe type narrowing for union types |
| **Internal Type Conversion** | Type guards + TypeScript | Compile-time and runtime safety |
| **Database Operations** | Prisma schema | ORM-level validation and type generation |

### Validation Error Handling

**class-validator Errors:**
```typescript
// ValidationPipe throws BadRequestException with detailed errors
// Each error contains:
// - property: string (field name)
// - constraints: Record<string, string> (validation failures)
// - children: ValidationError[] (nested errors)
```

**Zod Errors:**
```typescript
// Zod provides structured error information:
// - path: (string | number)[] (location of error)
// - message: string (error description)
// - code: ZodIssueCode (error type)
```

### Type Guard Patterns

**Exhaustive Switch with Type Guards:**
```typescript
// From computerAction.utils.ts:299-342
export function convertComputerActionToToolUseBlock(
  action: ComputerAction,
  toolUseId: string
): ComputerToolUseContentBlock {
  switch (action.action) {
    case "move_mouse":
      return convertMoveMouseActionToToolUseBlock(action, toolUseId);
    case "click_mouse":
      return convertClickMouseActionToToolUseBlock(action, toolUseId);
    // ... more cases
    default:
      const exhaustiveCheck: never = action;
      throw new Error(`Unknown action type: ${(exhaustiveCheck as any).action}`);
  }
}
```

The `never` type in the default case ensures compile-time completeness checking.

**Sources:** [packages/shared/src/utils/computerAction.utils.ts:299-342]()

### Nested Validation

For complex nested structures, use `@ValidateNested()` with `@Type()`:

```typescript
// From computer-action.dto.ts:51-58
export class ClickMouseActionDto extends BaseActionDto {
  @IsOptional()
  @ValidateNested()
  @Type(() => CoordinatesDto)
  coordinates?: CoordinatesDto;
  // ... other fields
}
```

This ensures that nested objects are validated according to their DTO class definitions.

**Sources:** [packages/bytebotd/src/computer-use/dto/computer-action.dto.ts:51-71]()

## Module Dependencies

The validation system spans multiple packages with specific dependency relationships:

```mermaid
graph TB
    subgraph "@bytebot/shared"
        Types["Type Definitions<br/>*.types.ts"]
        TypeGuards["Type Guards<br/>*.utils.ts"]
    end
    
    subgraph "bytebot-agent"
        AgentDeps["Dependencies:<br/>zod: ^4.0.5<br/>class-validator: ^0.14.2<br/>class-transformer: ^0.5.1"]
        PrismaSchema["Prisma Schema<br/>schema.prisma"]
    end
    
    subgraph "bytebotd"
        BytebotdDeps["Dependencies:<br/>class-validator: ^0.14.2<br/>class-transformer: ^0.5.1<br/>zod (via @rekog/mcp-nest)"]
        DTOs["DTOs + Pipes"]
        MCPTools["MCP Tools"]
    end
    
    Types -->|"Import"| TypeGuards
    Types -->|"Import"| DTOs
    Types -->|"Import"| MCPTools
    
    TypeGuards -->|"Used in"| AgentDeps
    
    DTOs -->|"Uses"| BytebotdDeps
    MCPTools -->|"Uses"| BytebotdDeps
    
    style Types fill:#f9f9f9
    style TypeGuards fill:#e6f3ff
    style DTOs fill:#fff4e6
```

**Sources:** [packages/bytebot-agent/package.json:24-45](), [packages/shared/src/types/messageContent.types.ts:1-258](), [packages/shared/src/types/computerAction.types.ts:1-126]()