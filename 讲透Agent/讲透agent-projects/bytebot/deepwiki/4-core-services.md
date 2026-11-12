<!-- source: DeepWiki mcp.deepwiki.com · repo bytebot-ai/bytebot · page 4 Core Services · fetched 2026-10-29 -->

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

