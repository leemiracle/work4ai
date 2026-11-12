# Page: Overview

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.dockerignore](.dockerignore)
- [Dockerfile](Dockerfile)
- [README.md](README.md)
- [package.json](package.json)
- [packages/app/package.json](packages/app/package.json)
- [packages/app/vite.config.ts](packages/app/vite.config.ts)
- [packages/mcp/package.json](packages/mcp/package.json)
- [packages/mcp/src/duplicate-space.ts](packages/mcp/src/duplicate-space.ts)
- [packages/mcp/src/error-messages.ts](packages/mcp/src/error-messages.ts)
- [packages/mcp/src/index.ts](packages/mcp/src/index.ts)
- [packages/mcp/src/tool-ids.ts](packages/mcp/src/tool-ids.ts)
- [pnpm-lock.yaml](pnpm-lock.yaml)
- [start.sh](start.sh)

</details>



The Hugging Face MCP Server is an implementation of the Model Context Protocol (MCP) that enables AI assistants and development tools to interact with the Hugging Face ecosystem. It provides 15 built-in tools for searching and managing models, datasets, spaces, and documentation, plus dynamic integration with thousands of Gradio applications hosted on Hugging Face Spaces.

This page describes the system architecture, core components, and deployment options. For detailed installation instructions, see [Getting Started](#2). For information about the available tools and their usage, see [Tools and Prompts](#4). For transport layer details, see [Transport Layer](#7).

## System Purpose and Scope

The server acts as a bridge between MCP-compatible clients (Claude Desktop, VS Code, Cursor, Gemini CLI, etc.) and Hugging Face services. It exposes functionality through three main interfaces:

- **Tools**: Executable functions for searching, retrieving details, managing spaces, and invoking Gradio apps
- **Prompts**: Pre-configured prompt templates for common tasks (model/dataset summaries, paper analysis)
- **Resources**: Static resources like HTML widgets for embedding Gradio interfaces

The system supports four transport protocols (`STDIO`, `SSE`, `StreamableHTTP`, `StatelessHTTPJson`) and can run as a CLI tool, web service, or Docker container.

Sources: [README.md:1-13](), [packages/app/package.json:1-11](), [packages/mcp/src/index.ts:1-30]()

## System Architecture

```mermaid
graph TB
    subgraph "Client Layer"
        ClaudeDesktop["Claude Desktop"]
        ClaudeCode["Claude Code (CLI)"]
        VSCode["VS Code"]
        Cursor["Cursor"]
        GeminiCLI["Gemini CLI"]
        WebBrowser["Web Browser"]
    end
    
    subgraph "packages/app - Application Layer"
        WebServer["WebServer<br/>Express server<br/>src/server/web-server.ts"]
        Application["Application<br/>Lifecycle orchestrator<br/>src/server/application.ts"]
        
        subgraph "Transport Implementations"
            STDIOTransport["STDIOTransport<br/>src/server/transports/stdio-transport.ts"]
            SSETransport["SSETransport<br/>src/server/transports/sse-transport.ts"]
            StreamableHTTP["StreamableHTTPTransport<br/>src/server/transports/streamable-http-transport.ts"]
            StatelessHTTP["StatelessHTTPTransport<br/>stateless mode"]
        end
        
        McpApiClient["McpApiClient<br/>Tool state management<br/>src/server/mcp-api-client.ts"]
        ToolSelection["ToolSelectionStrategy<br/>selectTools()<br/>src/server/tool-selection.ts"]
        SettingsService["settingsService<br/>User config storage<br/>src/server/settings-service.ts"]
    end
    
    subgraph "MCP Server Factory"
        ServerFactory["createServerFactory()<br/>src/server/server-factory.ts"]
        ProxyFactory["createProxyServerFactory()<br/>Gradio wrapper<br/>src/server/gradio-proxy-server.ts"]
        McpServer["McpServer<br/>@modelcontextprotocol/sdk"]
    end
    
    subgraph "packages/mcp - Library Layer"
        ToolRegistry["TOOL_ID_GROUPS<br/>src/tool-ids.ts"]
        
        subgraph "Built-in Tools (15)"
            ModelTools["ModelSearchTool<br/>ModelDetailTool"]
            DatasetTools["DatasetSearchTool<br/>DatasetDetailTool"]
            SpaceTools["DuplicateSpaceTool<br/>SpaceInfoTool<br/>SpaceFilesTool"]
            DocTools["DocSearchTool<br/>DocFetchTool"]
        end
        
        subgraph "Gradio Integration"
            GradioConnector["fetchGradioToolSchemas()<br/>src/server/gradio-utils.ts"]
            GradioHandler["createToolHandler()<br/>gradio-files.ts"]
            UseSpace["USE_SPACE_TOOL_CONFIG<br/>use-space.ts"]
        end
    end
    
    subgraph "External Services"
        HuggingFaceAPI["Hugging Face API<br/>huggingface.co/api"]
        GradioApps["Gradio Spaces<br/>*.hf.space"]
        DocsAPI["Documentation API<br/>huggingface.co/docs"]
    end
    
    ClaudeCode -->|stdin/stdout| STDIOTransport
    ClaudeDesktop -->|HTTP| StreamableHTTP
    VSCode -->|HTTP| StreamableHTTP
    Cursor -->|HTTP| StreamableHTTP
    GeminiCLI -->|HTTP| StreamableHTTP
    WebBrowser -->|HTTP| WebServer
    
    Application --> WebServer
    Application --> McpApiClient
    WebServer --> STDIOTransport
    WebServer --> SSETransport
    WebServer --> StreamableHTTP
    WebServer --> StatelessHTTP
    
    STDIOTransport --> ServerFactory
    SSETransport --> ServerFactory
    StreamableHTTP --> ServerFactory
    StatelessHTTP --> ServerFactory
    
    ServerFactory --> ToolSelection
    ServerFactory --> ProxyFactory
    ProxyFactory --> McpServer
    ProxyFactory --> GradioConnector
    
    McpApiClient --> SettingsService
    ToolSelection --> SettingsService
    ToolSelection --> ToolRegistry
    
    McpServer --> ModelTools
    McpServer --> DatasetTools
    McpServer --> SpaceTools
    McpServer --> DocTools
    McpServer --> UseSpace
    
    ModelTools --> HuggingFaceAPI
    DatasetTools --> HuggingFaceAPI
    SpaceTools --> HuggingFaceAPI
    DocTools --> DocsAPI
    GradioHandler --> GradioApps
```

This diagram shows how client connections flow through the transport layer to the MCP server factory, which uses `ToolSelectionStrategy` to determine available tools based on configuration, then creates an `McpServer` instance with registered tools from the `packages/mcp` library.

Sources: [packages/app/src/server/application.ts](), [packages/app/src/server/server-factory.ts](), [packages/app/src/server/tool-selection.ts](), [packages/mcp/src/tool-ids.ts:1-105]()

## Monorepo Structure

The project is organized as a monorepo with two main packages:

| Package | Path | Purpose | Key Exports |
|---------|------|---------|-------------|
| `@llmindset/hf-mcp` | `packages/mcp/` | MCP tool implementations and utilities | Tool classes, schemas, handlers, `TOOL_ID_GROUPS` |
| `@llmindset/hf-mcp-server` | `packages/app/` | Application server and web interface | Executables: `hf-mcp-server`, `hf-mcp-server-http`, `hf-mcp-server-http-json` |

The `packages/mcp` library is a pure implementation layer that exports tool configurations and handler functions. The `packages/app` layer consumes this library and adds:

- Transport protocol implementations
- Web server and dashboard UI
- Server factory pattern with tool selection
- Session management and metrics
- Docker containerization

Sources: [package.json:1-38](), [packages/mcp/package.json:1-54](), [packages/app/package.json:1-111]()

## Core Components and Data Flow

```mermaid
graph LR
    subgraph "Request Lifecycle"
        ClientRequest["Client<br/>JSON-RPC Request"]
        
        Transport["Transport Handler<br/>BaseTransport.handleRequest()"]
        
        SessionValidation["Session Validation<br/>validateAuthToken()"]
        
        ServerInstance["MCP Server Instance<br/>tools + prompts + resources"]
        
        ToolRouter["Tool Router<br/>server.setRequestHandler()"]
        
        BuiltInHandler["Built-in Tool<br/>HfApiCall.execute()"]
        GradioTool["Gradio Tool<br/>createToolHandler()"]
        
        HFAPI["Hugging Face API<br/>fetch() calls"]
        GradioSSE["Gradio Space<br/>SSE connection"]
        
        PostProcess["Post-processing<br/>applyResultPostProcessing()"]
        
        Response["JSON-RPC Response<br/>to client"]
    end
    
    ClientRequest --> Transport
    Transport --> SessionValidation
    SessionValidation --> ServerInstance
    ServerInstance --> ToolRouter
    
    ToolRouter -->|built-in tool| BuiltInHandler
    ToolRouter -->|gradio tool| GradioTool
    
    BuiltInHandler --> HFAPI
    GradioTool --> GradioSSE
    
    HFAPI --> PostProcess
    GradioSSE --> PostProcess
    
    PostProcess --> Response
```

Each request follows this path:

1. **Transport Layer** receives and validates the JSON-RPC request
2. **Session Validation** checks authentication token and session state (for stateful transports)
3. **MCP Server** routes to appropriate tool handler based on method name
4. **Tool Execution** invokes either a built-in tool (direct HF API call) or Gradio tool (SSE streaming)
5. **Post-processing** applies transformations (image filtering, OpenAI format conversion)
6. **Response** returns formatted result to client

Sources: [packages/app/src/server/transports/base-transport.ts](), [packages/app/src/server/server-factory.ts](), [packages/mcp/src/hf-api-call.ts]()

## Built-in Tools Catalog

The system provides 15 built-in tools organized by category in `TOOL_ID_GROUPS`:

```mermaid
graph TB
    subgraph "Tool Categories - TOOL_ID_GROUPS"
        SearchGroup["search bouquet<br/>5 tools"]
        SpacesGroup["spaces bouquet<br/>5 tools"]
        DetailGroup["detail group<br/>3 tools"]
        DocsGroup["docs bouquet<br/>2 tools"]
        APIGroup["hf_api bouquet<br/>7 tools"]
    end
    
    subgraph "Search Tools"
        ModelSearch["model_search<br/>MODEL_SEARCH_TOOL_CONFIG"]
        DatasetSearch["dataset_search<br/>DATASET_SEARCH_TOOL_CONFIG"]
        PaperSearch["paper_search<br/>PAPER_SEARCH_TOOL_CONFIG"]
        SpaceSearch["space_semantic_search<br/>SEMANTIC_SEARCH_TOOL_CONFIG"]
        DocSearch["hf_doc_search<br/>DOCS_SEMANTIC_SEARCH_CONFIG"]
    end
    
    subgraph "Space Management"
        DuplicateSpace["duplicate_space<br/>DUPLICATE_SPACE_TOOL_CONFIG"]
        SpaceInfo["space_info<br/>SPACE_INFO_TOOL_CONFIG"]
        SpaceFiles["space_files<br/>SPACE_FILES_TOOL_CONFIG"]
        UseSpace["use_space<br/>USE_SPACE_TOOL_CONFIG"]
    end
    
    subgraph "Detail Retrieval"
        ModelDetail["model_detail<br/>MODEL_DETAIL_TOOL_CONFIG"]
        DatasetDetail["dataset_detail<br/>DATASET_DETAIL_TOOL_CONFIG"]
        HubInspect["hub_repo_details<br/>HUB_INSPECT_TOOL_CONFIG"]
    end
    
    subgraph "Documentation"
        DocFetch["hf_doc_fetch<br/>DOC_FETCH_CONFIG"]
    end
    
    SearchGroup --> ModelSearch
    SearchGroup --> DatasetSearch
    SearchGroup --> PaperSearch
    SearchGroup --> SpaceSearch
    SearchGroup --> DocSearch
    
    SpacesGroup --> SpaceSearch
    SpacesGroup --> DuplicateSpace
    SpacesGroup --> SpaceInfo
    SpacesGroup --> SpaceFiles
    SpacesGroup --> UseSpace
    
    DetailGroup --> ModelDetail
    DetailGroup --> DatasetDetail
    DetailGroup --> HubInspect
    
    DocsGroup --> DocSearch
    DocsGroup --> DocFetch
    
    APIGroup --> ModelSearch
    APIGroup --> DatasetSearch
    APIGroup --> PaperSearch
    APIGroup --> SpaceSearch
    APIGroup --> DocSearch
    APIGroup --> HubInspect
```

Each tool is exported from `packages/mcp` with a configuration object (schema, description, annotations) and an implementation class. The `TOOL_ID_GROUPS` constant in [packages/mcp/src/tool-ids.ts:68-96]() defines bouquet presets that group related tools.

Sources: [packages/mcp/src/tool-ids.ts:1-105](), [packages/mcp/src/index.ts:1-30]()

## Dynamic Gradio Tool Integration

Beyond the 15 built-in tools, the system dynamically discovers and registers Gradio application endpoints as MCP tools:

```mermaid
graph TD
    subgraph "Discovery Phase"
        UserConfig["User Settings<br/>spaceTools array"]
        HeaderConfig["x-mcp-gradio header<br/>space1,space2"]
        
        ParseSpaces["parseGradioSpaceIds()<br/>gradio-utils.ts:112"]
        
        FetchMetadata["fetchGradioSubdomains()<br/>gradio-utils.ts:170"]
        
        GetSchema["GET /{space}/--replicate/api/gradio_api/run/predict/info"]
        
        ParseSchema["parseSchemaResponse()<br/>gradio-files.ts:227"]
        
        ConvertZod["Zod Schema<br/>z.object()"]
    end
    
    subgraph "Registration Phase"
        ProxyFactory["createProxyServerFactory()<br/>gradio-proxy-server.ts"]
        
        RegisterTool["server.addTool()<br/>dynamic tool registration"]
        
        ToolHandler["createToolHandler()<br/>gradio-files.ts:124"]
    end
    
    subgraph "Execution Phase"
        ClientCall["Client calls gradio tool"]
        
        SSEConnect["SSE connection to space"]
        
        StreamResults["Stream JSON events"]
        
        PostProcess["applyResultPostProcessing()<br/>gradio-post-processing.ts"]
        
        ImageFilter["filterImageContent()<br/>optional image removal"]
        
        OpenAITransform["toOpenAIContent()<br/>apps-openai-transformer.ts"]
    end
    
    UserConfig --> ParseSpaces
    HeaderConfig --> ParseSpaces
    ParseSpaces --> FetchMetadata
    FetchMetadata --> GetSchema
    GetSchema --> ParseSchema
    ParseSchema --> ConvertZod
    
    ConvertZod --> ProxyFactory
    ProxyFactory --> RegisterTool
    RegisterTool --> ToolHandler
    
    ToolHandler --> ClientCall
    ClientCall --> SSEConnect
    SSEConnect --> StreamResults
    StreamResults --> PostProcess
    PostProcess --> ImageFilter
    ImageFilter --> OpenAITransform
```

The `createProxyServerFactory()` function wraps the base server factory to inject Gradio tool discovery before server initialization. Each discovered endpoint becomes a tool with a generated schema based on the Gradio API contract.

Sources: [packages/app/src/server/gradio-proxy-server.ts](), [packages/app/src/server/gradio-utils.ts:112-200](), [packages/mcp/src/gradio-files.ts:124-240]()

## Transport Protocol Support

The server implements four transport protocols as defined by the MCP specification:

| Transport | Entry Point | Use Case | Session Model | Endpoints |
|-----------|-------------|----------|---------------|-----------|
| `STDIO` | `dist/server/stdio.js` | CLI integration (Claude Code, Gemini) | Single long-lived session | stdin/stdout pipes |
| `SSE` | `dist/server/sse.js` | Legacy web clients | Stateful (session map) | `GET /sse`, `POST /message` |
| `StreamableHTTP` | `dist/server/streamableHttp.js` | Modern web clients (VS Code, Cursor) | Stateful (session map) | `POST/GET/DELETE /mcp` |
| `StatelessHTTPJson` | `dist/server/streamableHttp.js --json` | Analytics/stateless mode | Stateless (per-request server) | `POST /mcp` |

All HTTP transports run on port 3000 by default and include a web dashboard at `/`. The `--json` flag enables stateless mode with optional analytics tracking.

**Session Management** (for stateful transports):

```typescript
// Default environment variables
MCP_CLIENT_HEARTBEAT_INTERVAL=30000    // Check SSE connection health
MCP_CLIENT_CONNECTION_CHECK=90000      // Check for stale sessions
MCP_CLIENT_CONNECTION_TIMEOUT=300000   // Remove inactive sessions
MCP_PING_ENABLED=true                  // Enable ping keep-alive
MCP_PING_INTERVAL=30000                // Ping frequency
```

Sources: [packages/app/package.json:6-11](), [README.md:226-235](), [start.sh:1-58]()

## Deployment Options

The server supports three deployment modes:

### 1. NPX (No Installation)

```bash
npx @llmindset/hf-mcp-server       # STDIO mode
npx @llmindset/hf-mcp-server-http  # HTTP mode
npx @llmindset/hf-mcp-server-json  # JSON mode
```

Sources: [README.md:144-146]()

### 2. Docker Container

```bash
docker pull ghcr.io/evalstate/hf-mcp-server:latest
docker run --rm -p 3000:3000 ghcr.io/evalstate/hf-mcp-server:latest
```

The `Dockerfile` builds both packages and defaults to `streamableHttpJson` transport. The `start.sh` script handles transport selection via the `TRANSPORT` environment variable.

Sources: [Dockerfile:1-67](), [start.sh:1-58]()

### 3. Development Mode

```bash
pnpm install
pnpm build
pnpm dev              # Concurrent watch mode
pnpm dev:stdio        # STDIO transport
pnpm dev:json         # JSON transport
```

The `concurrently` tool runs TypeScript compilation (`tsc --watch`), Vite bundling (`vite build --watch`), and server restart (`nodemon`) simultaneously.

Sources: [package.json:7-12](), [packages/app/package.json:40-46]()

## Configuration System

The server behavior is controlled through three mechanisms:

1. **Environment Variables**: Authentication, timeouts, API endpoints
   - `DEFAULT_HF_TOKEN`: Default token for unauthenticated requests (development only)
   - `HF_API_TIMEOUT`: API request timeout (default: 12500ms)
   - `USER_CONFIG_API`: External settings API URL
   - `SEARCH_ENABLES_FETCH`: Auto-enable `hf_doc_fetch` when `hf_doc_search` is enabled

2. **HTTP Headers**: Per-request tool selection
   - `x-mcp-bouquet`: Override tool selection with preset (`hf_api`, `search`, `spaces`, `docs`, `all`)
   - `x-mcp-mix`: Additive tool selection combined with user settings
   - `x-mcp-gradio`: Comma-separated Gradio space IDs to include
   - `Authorization: Bearer <token>`: User authentication

3. **User Settings**: Persistent configuration via web dashboard or external API
   - `builtInTools`: Array of enabled tool IDs
   - `spaceTools`: Array of Gradio space configurations
   - Storage: In-memory `settingsService` or external API via `USER_CONFIG_API`

The precedence order is: `x-mcp-bouquet` (override) > `x-mcp-mix` (additive) > user settings > fallback (all tools).

Sources: [README.md:238-248](), [packages/app/src/server/tool-selection.ts](), [packages/app/src/server/settings-service.ts]()

## Key Design Patterns

**Server Factory Pattern**: The `createServerFactory()` function returns a factory that creates per-session `McpServer` instances with selected tools. This enables different clients to have different tool sets based on their configuration.

**Proxy Factory Pattern**: The `createProxyServerFactory()` wraps the base factory to inject Gradio tool discovery, maintaining separation between built-in and dynamic tools.

**Tool Configuration Pattern**: Each tool exports a `*_TOOL_CONFIG` constant with `name`, `schema` (Zod), `description`, and `annotations`, ensuring consistent registration.

**Base Class Pattern**: `HfApiCall<TParams, TResult>` provides shared functionality for API requests, error handling, and token management across all built-in tools.

Sources: [packages/app/src/server/server-factory.ts](), [packages/app/src/server/gradio-proxy-server.ts](), [packages/mcp/src/hf-api-call.ts](), [packages/mcp/src/duplicate-space.ts:42-64]()

---

# Page: Getting Started

# Getting Started

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.dockerignore](.dockerignore)
- [Dockerfile](Dockerfile)
- [README.md](README.md)
- [package.json](package.json)
- [packages/app/package.json](packages/app/package.json)
- [packages/app/vite.config.ts](packages/app/vite.config.ts)
- [packages/mcp/package.json](packages/mcp/package.json)
- [packages/mcp/src/duplicate-space.ts](packages/mcp/src/duplicate-space.ts)
- [packages/mcp/src/error-messages.ts](packages/mcp/src/error-messages.ts)
- [pnpm-lock.yaml](pnpm-lock.yaml)
- [start.sh](start.sh)

</details>



This page provides an overview of how to install, configure, and connect clients to the Hugging Face MCP Server. For detailed installation instructions, see [Installation and Setup](#2.1). For step-by-step client connection guides, see [Client Integration](#2.2).

The Hugging Face MCP Server enables AI clients (such as Claude Desktop, VS Code, Cursor, and Gemini CLI) to interact with the Hugging Face ecosystem through the Model Context Protocol (MCP). The server exposes tools for searching models/datasets/papers, managing Spaces, accessing documentation, and invoking Gradio applications.

---

## Prerequisites

Before installing the server, ensure you have:

| Requirement | Purpose | Notes |
|------------|---------|-------|
| **Node.js** (≥18) | Runtime environment | Required for all installation methods |
| **Hugging Face Token** | API authentication | Obtain from https://huggingface.co/settings/tokens |
| **pnpm** (10.15.1) | Package manager | Only for building from source; managed via Corepack |
| **Docker** (optional) | Containerized deployment | Alternative to Node.js installation |

**Sources:** [README.md:176-179](), [package.json:6]()

---

## Server Transport Modes

The server supports four transport mechanisms for client communication. Understanding these modes is essential for proper configuration:

```mermaid
graph TB
    Client["MCP Client"]
    
    subgraph TransportLayer["Transport Layer"]
        STDIO["STDIO Transport<br/>packages/app/src/server/stdio.ts"]
        SSE["SSE Transport<br/>packages/app/src/server/sse.ts"]
        HTTP["StreamableHTTP<br/>packages/app/src/server/streamableHttp.ts"]
        JSONMode["StreamableHTTPJson<br/>--json flag"]
    end
    
    subgraph Characteristics["Transport Characteristics"]
        C1["stdin/stdout pipes<br/>Single process<br/>Environment token"]
        C2["GET /sse + POST /message<br/>Stateful sessions<br/>Real-time updates"]
        C3["POST/GET/DELETE /mcp<br/>Stateful sessions<br/>Session tracking"]
        C4["POST /mcp only<br/>Stateless requests<br/>Per-request servers"]
    end
    
    Client -->|"CLI Clients"| STDIO
    Client -->|"Desktop Apps"| SSE
    Client -->|"IDEs"| HTTP
    Client -->|"Web Dashboard"| JSONMode
    
    STDIO -.-> C1
    SSE -.-> C2
    HTTP -.-> C3
    JSONMode -.-> C4
```

**Transport Mode Comparison**

| Mode | Entry Point | Use Case | Session State | Authentication |
|------|------------|----------|---------------|----------------|
| **STDIO** | `stdio.js` | CLI tools (Claude Code, Gemini) | Single long-lived session | `HF_TOKEN` environment variable |
| **SSE** | `sse.js` | Desktop applications | Stateful with heartbeat | `Authorization` header |
| **StreamableHTTP** | `streamableHttp.js` | IDEs (VS Code, Cursor) | Stateful with tracking | `Authorization` header |
| **StreamableHTTPJson** | `streamableHttp.js --json` | Web clients, Analytics | Stateless or optional analytics | `Authorization` header |

**Sources:** [packages/app/package.json:8-10](), [README.md:125-135](), [start.sh:33-58]()

---

## Installation Methods

### Quick Start with npx

The fastest way to run the server without installation:

```bash
# STDIO mode (for CLI clients)
npx @llmindset/hf-mcp-server

# HTTP mode (for web-based clients)
npx @llmindset/hf-mcp-server-http

# JSON mode (stateless)
npx @llmindset/hf-mcp-server-json
```

Each command starts the server in a different transport mode. HTTP and JSON modes also launch a web dashboard on `http://localhost:3000/`.

**Sources:** [README.md:141-147](), [packages/app/package.json:8-10]()

### Docker Deployment

Pull and run the pre-built container:

```bash
# Pull image
docker pull ghcr.io/evalstate/hf-mcp-server:latest

# Run with default settings (StreamableHTTPJson mode)
docker run --rm -p 3000:3000 \
  -e DEFAULT_HF_TOKEN=hf_xxx \
  ghcr.io/evalstate/hf-mcp-server:latest

# Run in STDIO mode
docker run -i --rm \
  -e TRANSPORT=stdio \
  -e DEFAULT_HF_TOKEN=hf_xxx \
  ghcr.io/evalstate/hf-mcp-server:latest
```

The Docker image defaults to `streamableHttpJson` mode and exposes port 3000 for the web dashboard.

**Sources:** [README.md:149-157](), [Dockerfile:1-66](), [start.sh:3-14]()

### Building from Source

For development or customization:

```bash
# Clone repository
git clone https://github.com/huggingface/hf-mcp-server
cd hf-mcp-server

# Install dependencies (uses pnpm via Corepack)
pnpm install

# Build all packages
pnpm build

# Start server
pnpm start
```

The monorepo contains two packages:
- **`packages/mcp`**: Core MCP tool implementations and API integrations
- **`packages/app`**: Server application, transports, and web UI

**Sources:** [README.md:176-195](), [package.json:1-38](), [README.md:116-122]()

---

## Configuration via Environment Variables

The server behavior is controlled through environment variables:

```mermaid
graph LR
    subgraph EnvVars["Environment Variables"]
        TRANSPORT["TRANSPORT<br/>stdio|sse|streamableHttp|streamableHttpJson"]
        TOKEN["DEFAULT_HF_TOKEN<br/>⚠️ Use only for development"]
        HFTOKEN["HF_TOKEN<br/>Standard authentication"]
        PORT["PORT<br/>Default: 3000"]
        TIMEOUT["HF_API_TIMEOUT<br/>Default: 12500ms"]
        CONFIG["USER_CONFIG_API<br/>External settings URL"]
        STRICT["MCP_STRICT_COMPLIANCE<br/>GET 405 in JSON mode"]
        SEARCH["SEARCH_ENABLES_FETCH<br/>Auto-enable doc_fetch"]
    end
    
    subgraph ServerBehavior["Server Behavior"]
        TransportMode["Transport Selection"]
        Auth["Authentication"]
        Timeouts["API Timeouts"]
        Settings["User Settings"]
        Compliance["Protocol Compliance"]
        Features["Feature Flags"]
    end
    
    TRANSPORT --> TransportMode
    TOKEN --> Auth
    HFTOKEN --> Auth
    PORT --> TransportMode
    TIMEOUT --> Timeouts
    CONFIG --> Settings
    STRICT --> Compliance
    SEARCH --> Features
```

**Key Environment Variables**

| Variable | Default | Description |
|----------|---------|-------------|
| `TRANSPORT` | `streamableHttpJson` | Transport type (stdio, sse, streamableHttp, streamableHttpJson) |
| `PORT` | `3000` | HTTP server port |
| `HF_TOKEN` | - | Standard Hugging Face authentication (used in Authorization header) |
| `DEFAULT_HF_TOKEN` | - | ⚠️ Fallback token when no header provided (dev/test only) |
| `HF_API_TIMEOUT` | `12500` | API request timeout in milliseconds |
| `USER_CONFIG_API` | - | External API for user settings (default: internal storage) |
| `MCP_STRICT_COMPLIANCE` | `false` | Reject GET requests with 405 in JSON mode |
| `SEARCH_ENABLES_FETCH` | `false` | Auto-enable `hf_doc_fetch` when `hf_doc_search` is enabled |

For stateful transports (SSE, StreamableHTTP), additional session management variables are available (see [Transport Layer](#7) for details).

**Sources:** [README.md:237-248](), [start.sh:3-27]()

---

## Authentication Flow

```mermaid
sequenceDiagram
    participant Client
    participant Transport
    participant ServerFactory["createServerFactory<br/>packages/app/src/server/factory.ts"]
    participant McpServer["McpServer<br/>@mcp-ui/server"]
    participant HfApi["Hugging Face API"]
    
    rect rgb(245, 245, 245)
        Note over Client,McpServer: Connection Phase
        Client->>Transport: Connect with Auth header
        Transport->>Transport: validateAuthAndTrackMetrics()
        alt Has Authorization header
            Transport->>ServerFactory: Create with token from header
        else No Authorization header
            Transport->>ServerFactory: Use DEFAULT_HF_TOKEN if set
        end
        ServerFactory->>McpServer: Instantiate with credentials
        McpServer-->>Client: Connection established
    end
    
    rect rgb(245, 245, 245)
        Note over Client,HfApi: Tool Invocation Phase
        Client->>McpServer: Call tool (e.g., model_search)
        McpServer->>HfApi: Request with token
        HfApi-->>McpServer: Response
        McpServer-->>Client: Tool result
    end
```

**Authentication Methods by Transport:**

- **STDIO**: Uses `HF_TOKEN` or `DEFAULT_HF_TOKEN` from environment variables
- **SSE/HTTP/JSON**: Uses `Authorization: Bearer <token>` header from client request
- **Docker**: Can set `DEFAULT_HF_TOKEN` for testing (not recommended for production)

**Sources:** [start.sh:12-27](), [README.md:241-242]()

---

## Client Connection Overview

The server is designed for integration with multiple MCP-compatible clients. Each client type uses a different transport:

**Supported Client Integrations**

| Client | Transport | Configuration Method |
|--------|-----------|---------------------|
| **Claude Desktop** | SSE/HTTP | Web connector gallery at claude.ai/settings/connectors |
| **Claude Code** | HTTP | CLI command: `claude mcp add` |
| **Gemini CLI** | HTTP | CLI command: `gemini mcp add` |
| **VS Code** | HTTP | Gallery at code.visualstudio.com/mcp or `mcp.json` |
| **Cursor** | HTTP | One-click install link or manual `mcp.json` |
| **Web Dashboard** | HTTPJson | Direct access at `http://localhost:3000/` |

For detailed setup instructions for each client, see [Client Integration](#2.2).

**Sources:** [README.md:11-108]()

---

## Server Architecture Overview

```mermaid
graph TB
    subgraph Clients["Client Layer"]
        CLI["CLI Clients<br/>(Claude Code, Gemini)"]
        IDE["IDE Clients<br/>(VS Code, Cursor)"]
        Desktop["Desktop Apps<br/>(Claude Desktop)"]
        Browser["Web Browser"]
    end
    
    subgraph AppLayer["packages/app<br/>Application Layer"]
        WebServer["WebServer<br/>src/server/web-server.ts<br/>Express + API Routes"]
        Application["Application<br/>src/server/application.ts<br/>Lifecycle Management"]
        
        StdioT["STDIOTransport<br/>src/server/stdio.ts"]
        SseT["SSETransport<br/>src/server/sse.ts"]
        HttpT["StreamableHTTPTransport<br/>src/server/streamableHttp.ts"]
        
        ServerFactory["createServerFactory<br/>src/server/factory.ts"]
        McpApiClient["McpApiClient<br/>src/mcp-api-client.ts<br/>Tool State Management"]
    end
    
    subgraph McpLayer["packages/mcp<br/>Library Layer"]
        ToolRegistry["Tool Registry<br/>src/tool-ids.ts"]
        HfTools["HF API Tools<br/>model-search.ts<br/>dataset-search.ts<br/>paper-search.ts"]
        DocTools["Documentation<br/>doc-search.ts<br/>doc-fetch.ts"]
        GradioIntegration["Gradio Integration<br/>gradio-endpoint.ts<br/>use-space.ts"]
    end
    
    CLI --> StdioT
    IDE --> HttpT
    Desktop --> SseT
    Browser --> WebServer
    
    StdioT --> Application
    SseT --> Application
    HttpT --> Application
    WebServer --> Application
    
    Application --> ServerFactory
    Application --> McpApiClient
    
    ServerFactory --> ToolRegistry
    ServerFactory --> HfTools
    ServerFactory --> DocTools
    ServerFactory --> GradioIntegration
```

The system is organized as a monorepo with two main packages:
- **packages/app**: Contains the server application, transport implementations, and web UI
- **packages/mcp**: Contains the tool implementations and Hugging Face API integrations

**Sources:** [README.md:116-122](), [package.json:1-38](), [packages/app/package.json:1-111](), [packages/mcp/package.json:1-53]()

---

## Web Dashboard

When running in HTTP or JSON mode, the server provides a web interface at `http://localhost:3000/`:

**Dashboard Features:**
- **Settings Copy Page**: Pre-configured connection snippets for different clients
- **Tool Configuration**: Enable/disable built-in tools using bouquets or custom selections
- **Gradio Endpoints**: Add/remove Gradio Space tools dynamically
- **Monitoring**: Real-time metrics for connections, tool calls, and sessions
- **Transport Stats**: Connection health, session tracking, and performance metrics

The web interface is built with React and Vite, using Server-Sent Events to display real-time updates.

**Sources:** [README.md:156-157](), [packages/app/vite.config.ts:1-47]()

---

## Development Mode

For contributors and developers extending the server:

```bash
# Start both packages in watch mode with hot module reload
pnpm dev

# Development commands by transport
pnpm dev:stdio        # STDIO transport
pnpm dev:sse          # SSE transport  
pnpm dev:json         # JSON mode
pnpm dev:watch        # Watch mode with nodemon

# Build commands
pnpm build            # Build all packages
pnpm clean            # Clean build artifacts
pnpm buildrun         # Clean, build, lint, test, and start
```

The development workflow uses:
- **TypeScript compiler** in watch mode for server code (`tsc --watch`)
- **Vite** in watch mode for web UI (`vite build --watch`)
- **Concurrently** to run multiple watch processes
- **Nodemon** for automatic server restarts

**Sources:** [package.json:7-24](), [packages/app/package.json:33-56](), [README.md:173-196]()

---

## Next Steps

After understanding the basic installation and configuration options:

1. **[Installation and Setup](#2.1)**: Follow detailed instructions for your preferred installation method
2. **[Client Integration](#2.2)**: Connect your specific client (Claude, VS Code, etc.)
3. **[Tool Selection System](#5)**: Learn how to configure which tools are available
4. **[Architecture](#3)**: Understand the system components and their interactions
5. **[Development Guide](#9)**: Contribute to or extend the server

For production deployments, review the [Transport Layer](#7) documentation to understand session management and stateful vs. stateless modes.

**Sources:** [README.md:1-248]()

---

# Page: Installation and Setup

# Installation and Setup

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.dockerignore](.dockerignore)
- [Dockerfile](Dockerfile)
- [README.md](README.md)
- [package.json](package.json)
- [packages/app/package.json](packages/app/package.json)
- [packages/app/vite.config.ts](packages/app/vite.config.ts)
- [packages/mcp/package.json](packages/mcp/package.json)
- [packages/mcp/src/duplicate-space.ts](packages/mcp/src/duplicate-space.ts)
- [packages/mcp/src/error-messages.ts](packages/mcp/src/error-messages.ts)
- [pnpm-lock.yaml](pnpm-lock.yaml)
- [start.sh](start.sh)

</details>



This page provides detailed instructions for installing dependencies, building the project, and running the HF MCP Server in different operational modes. The installation process supports multiple deployment strategies including quick execution via `npx`, containerized deployment with Docker, and development from source.

For instructions on connecting specific MCP clients (Claude, VS Code, Cursor, Gemini) to a running server instance, see [Client Integration](#2.2).

---

## Prerequisites

The HF MCP Server requires Node.js 18 or higher and uses `pnpm` as its package manager.

| Requirement | Minimum Version | Notes |
|-------------|----------------|-------|
| Node.js | 18.0.0 | Specified in [packages/mcp/package.json:458]() |
| pnpm | 10.15.1 | Managed via Corepack in [package.json:6]() |

The project uses Corepack to ensure consistent `pnpm` versions across all environments. Corepack is included with Node.js 16.9+ and can be enabled with:

```bash
corepack enable pnpm
```

**Sources:** [package.json:6](), [packages/mcp/package.json:458](), [Dockerfile:4]()

---

## Installation Methods

### Diagram: Installation Entry Points and Executables

```mermaid
graph TB
    subgraph "NPX Installation"
        NPX1["npx @llmindset/hf-mcp-server"]
        NPX2["npx @llmindset/hf-mcp-server-http"]
        NPX3["npx @llmindset/hf-mcp-server-http-json"]
    end
    
    subgraph "Docker Installation"
        DOCKER["docker pull ghcr.io/evalstate/hf-mcp-server:latest"]
        DOCKERRUN["docker run -p 3000:3000"]
    end
    
    subgraph "Source Installation"
        CLONE["git clone"]
        INSTALL["pnpm install"]
        BUILD["pnpm build"]
    end
    
    subgraph "Package Bin Mappings"
        BIN1["dist/server/stdio.js"]
        BIN2["dist/server/streamableHttp.js"]
        BIN3["dist/server/streamableHttpJson.js"]
    end
    
    subgraph "Start Script"
        STARTSH["start.sh"]
        TRANSPORT["TRANSPORT env var"]
    end
    
    NPX1 --> BIN1
    NPX2 --> BIN2
    NPX3 --> BIN3
    
    DOCKERRUN --> STARTSH
    STARTSH --> TRANSPORT
    TRANSPORT --> BIN1
    TRANSPORT --> BIN2
    TRANSPORT --> BIN3
    
    BUILD --> BIN1
    BUILD --> BIN2
    BUILD --> BIN3
    
    style NPX1 fill:#f9f9f9
    style NPX2 fill:#f9f9f9
    style NPX3 fill:#f9f9f9
    style DOCKER fill:#e8f4f8
```

**Sources:** [packages/app/package.json:7-11](), [start.sh:4-6](), [README.md:144-147]()

---

## Quick Installation with NPX

The fastest method to run the server is using `npx`, which downloads and executes the package without manual installation:

```bash
# STDIO mode (for CLI clients like Claude Code)
npx @llmindset/hf-mcp-server

# StreamableHTTP mode (stateful, for web-based clients)
npx @llmindset/hf-mcp-server-http

# StreamableHTTPJson mode (stateless, recommended for production)
npx @llmindset/hf-mcp-server-http-json
```

These commands map to the `bin` entries defined in [packages/app/package.json:7-11]():

| NPX Command | Binary Path | Transport Mode |
|-------------|-------------|----------------|
| `@llmindset/hf-mcp-server` | `dist/server/stdio.js` | STDIO |
| `@llmindset/hf-mcp-server-http` | `dist/server/streamableHttp.js` | StreamableHTTP |
| `@llmindset/hf-mcp-server-http-json` | `dist/server/streamableHttpJson.js` | StreamableHTTPJson |

The HTTP-based transports start a web server on port 3000 by default, serving the management dashboard at `http://localhost:3000/` and the MCP endpoint at `http://localhost:3000/mcp`.

**Sources:** [packages/app/package.json:7-11](), [README.md:144-147]()

---

## Docker Installation

The Docker image provides a self-contained deployment with all dependencies included.

### Pull the Image

```bash
docker pull ghcr.io/evalstate/hf-mcp-server:latest
```

### Run with Default Settings

```bash
docker run --rm -p 3000:3000 ghcr.io/evalstate/hf-mcp-server:latest
```

This starts the server in **StreamableHTTPJson** mode (the default for Docker deployments) as specified in [Dockerfile:59]().

### Run with Custom Transport

```bash
# STDIO mode
docker run -i --rm -e TRANSPORT=stdio -p 3000:3000 ghcr.io/evalstate/hf-mcp-server:latest

# SSE mode
docker run --rm -e TRANSPORT=sse -p 3000:3000 ghcr.io/evalstate/hf-mcp-server:latest

# StreamableHTTP mode
docker run --rm -e TRANSPORT=streamableHttp -p 3000:3000 ghcr.io/evalstate/hf-mcp-server:latest
```

The `TRANSPORT` environment variable is processed by [start.sh:4-7]() and converted to lowercase for case-insensitive matching.

### Run with Authentication Token

```bash
docker run --rm -p 3000:3000 -e DEFAULT_HF_TOKEN=hf_xxx ghcr.io/evalstate/hf-mcp-server:latest
```

⚠️ **Security Warning:** The `DEFAULT_HF_TOKEN` environment variable should only be used in development/test environments or for local STDIO deployments. For HTTP transports, authentication should be provided via the `Authorization: Bearer` header on a per-request basis.

**Sources:** [Dockerfile:1-67](), [start.sh:1-58](), [README.md:150-154]()

---

## Source Installation

Installing from source provides access to development scripts and allows customization.

### Clone and Install

```bash
# Clone the repository
git clone https://github.com/huggingface/hf-mcp-server.git
cd hf-mcp-server

# Install dependencies
pnpm install
```

The `pnpm install` command respects the workspace configuration defined in [pnpm-workspace.yaml]() and installs dependencies for both packages:
- `packages/mcp` - The core MCP library
- `packages/app` - The application layer with transports and web UI

### Build the Project

```bash
pnpm build
```

This executes the `build` script from [package.json:21](), which runs `pnpm -r build` to build all workspace packages recursively.

**Sources:** [package.json:2-38](), [README.md:177-183]()

---

## Build System

### Diagram: Build Process and Artifacts

```mermaid
graph LR
    subgraph "Source Files"
        MCP_SRC["packages/mcp/src/*.ts"]
        APP_SRC["packages/app/src/server/*.ts"]
        WEB_SRC["packages/app/src/web/*.tsx"]
    end
    
    subgraph "Build Commands"
        ROOT_BUILD["pnpm build"]
        MCP_BUILD["tsc --declaration"]
        APP_SERVER["tsc -p tsconfig.server.json"]
        APP_WEB["vite build"]
        SINGLEFILES["build:singlefiles"]
    end
    
    subgraph "Build Artifacts"
        MCP_DIST["packages/mcp/dist/*.js"]
        SERVER_DIST["packages/app/dist/server/*.js"]
        WEB_DIST["packages/app/dist/web/"]
        WELCOME["mcp-welcome.html"]
        WIDGET["gradio-widget.html"]
    end
    
    MCP_SRC --> MCP_BUILD
    APP_SRC --> APP_SERVER
    WEB_SRC --> APP_WEB
    
    ROOT_BUILD --> MCP_BUILD
    ROOT_BUILD --> APP_SERVER
    ROOT_BUILD --> APP_WEB
    ROOT_BUILD --> SINGLEFILES
    
    MCP_BUILD --> MCP_DIST
    APP_SERVER --> SERVER_DIST
    APP_WEB --> WEB_DIST
    SINGLEFILES --> WELCOME
    SINGLEFILES --> WIDGET
    
    style MCP_BUILD fill:#f9f9f9
    style APP_SERVER fill:#f9f9f9
    style APP_WEB fill:#f9f9f9
```

### Build Scripts

The monorepo uses a hierarchical build system with scripts at both root and package levels:

| Script | Location | Command | Purpose |
|--------|----------|---------|---------|
| `build` | [package.json:21]() | `pnpm -r build` | Build all packages recursively |
| `build:server` | [packages/app/package.json:35]() | `tsc -p tsconfig.server.json` | Compile server TypeScript |
| `build:web` | [packages/app/package.json:36]() | `vite build` | Bundle web UI with Vite |
| `build:singlefiles` | [packages/app/package.json:37]() | Build standalone HTML | Create self-contained HTML files |
| `build` | [packages/mcp/package.json:26]() | `tsc --declaration` | Compile library with type definitions |

### Build Order and Dependencies

The build process follows this sequence:

1. **Library Build (`packages/mcp`)**: Compiles TypeScript sources to JavaScript with type definitions, outputs to `packages/mcp/dist/`
2. **Server Build**: Compiles server entry points (`stdio.js`, `streamableHttp.js`, `sse.js`) using [packages/app/tsconfig.server.json]()
3. **Web Build**: Bundles React dashboard using Vite configuration from [packages/app/vite.config.ts:8-47]()
4. **Single-File Builds**: Creates standalone HTML files (`mcp-welcome.html`, `gradio-widget.html`) using `vite-plugin-singlefile` from [packages/app/vite.config.ts:19]()

The Vite configuration uses conditional logic based on `VITE_BUILD_TARGET` environment variable to determine which HTML file to build as a single-file bundle.

### Clean Build

```bash
pnpm clean  # Remove all dist/ directories
pnpm build  # Full rebuild
```

The `clean` script is defined in [package.json:22]() and [packages/app/package.json:55]().

**Sources:** [package.json:21-24](), [packages/app/package.json:34-39](), [packages/app/vite.config.ts:1-48](), [packages/mcp/package.json:26]()

---

## Running the Server

### Transport Modes

The server supports four transport implementations, each optimized for different use cases:

| Transport | Entry Point | Use Case | Statefulness |
|-----------|-------------|----------|--------------|
| **STDIO** | [packages/app/package.json:8]() | CLI clients (Claude Code, Gemini CLI) | Single session |
| **SSE** | [packages/app/package.json:50]() | Legacy real-time updates | Stateful |
| **StreamableHTTP** | [packages/app/package.json:9]() | Web clients with session persistence | Stateful |
| **StreamableHTTPJson** | [packages/app/package.json:10]() | Stateless production deployments | Stateless |

### Development Scripts

```bash
# Start in StreamableHTTP mode with dashboard
pnpm dev

# Start in STDIO mode
pnpm dev:stdio

# Start in SSE mode
pnpm dev:sse

# Start in StreamableHTTPJson mode
pnpm dev:json

# Watch mode with auto-rebuild
pnpm dev:watch
```

These scripts are defined in [package.json:8-12]() and use `concurrently` to run both library and application builds simultaneously.

### Production Scripts

```bash
# Start production server (StreamableHTTP)
pnpm start

# Start in StreamableHTTPJson mode
pnpm start:json

# Start in STDIO mode
pnpm start:stdio

# Start in SSE mode
pnpm start:sse
```

Production scripts set `NODE_ENV=production` as seen in [packages/app/package.json:47-50]().

### Diagram: Transport Selection Flow

```mermaid
graph TD
    START["start.sh"]
    GETENV["Read TRANSPORT env var"]
    LOWER["Convert to lowercase"]
    CHECKSTDIO{"TRANSPORT == 'stdio'?"}
    CHECKSSE{"TRANSPORT == 'sse'?"}
    CHECKHTTP{"TRANSPORT == 'streamablehttp'?"}
    CHECKJSON{"TRANSPORT == 'streamablehttpjson'?"}
    
    STDIO_BIN["node dist/server/stdio.js"]
    SSE_BIN["node dist/server/sse.js"]
    HTTP_BIN["node dist/server/streamableHttp.js"]
    JSON_BIN["node dist/server/streamableHttp.js --json"]
    ERROR["Exit with error"]
    
    START --> GETENV
    GETENV --> LOWER
    LOWER --> CHECKSTDIO
    
    CHECKSTDIO -->|Yes| STDIO_BIN
    CHECKSTDIO -->|No| CHECKSSE
    
    CHECKSSE -->|Yes| SSE_BIN
    CHECKSSE -->|No| CHECKHTTP
    
    CHECKHTTP -->|Yes| HTTP_BIN
    CHECKHTTP -->|No| CHECKJSON
    
    CHECKJSON -->|Yes| JSON_BIN
    CHECKJSON -->|No| ERROR
    
    style STDIO_BIN fill:#f9f9f9
    style SSE_BIN fill:#f9f9f9
    style HTTP_BIN fill:#f9f9f9
    style JSON_BIN fill:#f9f9f9
```

The transport selection logic is implemented in [start.sh:34-58](), which converts the `TRANSPORT` environment variable to lowercase and routes to the appropriate server entry point.

**Sources:** [start.sh:34-58](), [package.json:8-14](), [packages/app/package.json:40-50]()

---

## Environment Variables

### Core Configuration

| Variable | Default | Description | Reference |
|----------|---------|-------------|-----------|
| `TRANSPORT` | `streamableHttpJson` (Docker) | Transport type: `stdio`, `sse`, `streamableHttp`, `streamableHttpJson` | [start.sh:4](), [Dockerfile:59]() |
| `PORT` | `3000` | HTTP server port for web dashboard and MCP endpoints | [start.sh:8]() |
| `NODE_ENV` | `production` | Node environment mode | [Dockerfile:58]() |

### Authentication

| Variable | Purpose | Security Notes | Reference |
|----------|---------|----------------|-----------|
| `DEFAULT_HF_TOKEN` | Fallback token when no Authorization header provided | ⚠️ Use only in dev/test or local STDIO | [README.md:241]() |
| `HF_TOKEN` | Used as `DEFAULT_HF_TOKEN` in STDIO mode if not set | Auto-converted for STDIO transport | [start.sh:13-15]() |

The token fallback logic in [start.sh:13-15]() specifically handles STDIO mode by setting `DEFAULT_HF_TOKEN` from `HF_TOKEN` if the latter is present.

### API Configuration

| Variable | Default | Description | Reference |
|----------|---------|-------------|-----------|
| `HF_API_TIMEOUT` | `12500` | Hugging Face API timeout in milliseconds | [README.md:243]() |
| `USER_CONFIG_API` | Local frontend | URL for external user settings storage | [README.md:244]() |

### Tool Behavior

| Variable | Default | Description | Reference |
|----------|---------|-------------|-----------|
| `SEARCH_ENABLES_FETCH` | `false` | Auto-enable `hf_doc_fetch` when `hf_doc_search` is enabled | [README.md:247]() |
| `AUTHENTICATE_TOOL` | `false` | Include OAuth challenge tool | [README.md:246]() |
| `MCP_STRICT_COMPLIANCE` | `false` | Return 405 for GET requests in JSON mode (vs. welcome page) | [README.md:245]() |

### Session Management (Stateful Transports)

These variables apply to SSE and StreamableHTTP transports only:

| Variable | Default | Description | Reference |
|----------|---------|-------------|-----------|
| `MCP_CLIENT_HEARTBEAT_INTERVAL` | `30000` | SSE connection health check interval (ms) | [README.md:230]() |
| `MCP_CLIENT_CONNECTION_CHECK` | `90000` | Stale session check interval (ms) | [README.md:231]() |
| `MCP_CLIENT_CONNECTION_TIMEOUT` | `300000` | Remove sessions inactive for this duration (ms) | [README.md:232]() |
| `MCP_PING_ENABLED` | `true` | Enable ping keep-alive for sessions | [README.md:233]() |
| `MCP_PING_INTERVAL` | `30000` | Interval between ping cycles (ms) | [README.md:234]() |

**Sources:** [README.md:237-247](), [start.sh:4-15](), [Dockerfile:58-60]()

---

## Verification

### HTTP Transports (SSE, StreamableHTTP, StreamableHTTPJson)

After starting an HTTP-based transport, verify the server is running:

1. **Access the Web Dashboard:**
   ```
   http://localhost:3000/
   ```
   This serves the management interface built from [packages/app/src/web/index.html]().

2. **Check the MCP Endpoint:**
   - StreamableHTTP/HTTPJson: `http://localhost:3000/mcp`
   - SSE: `http://localhost:3000/sse` (with message endpoint at `/message`)

3. **Test with curl:**
   ```bash
   # StreamableHTTPJson mode
   curl -X POST http://localhost:3000/mcp \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer YOUR_HF_TOKEN" \
     -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}'
   ```

The endpoint paths are documented in [README.md:217-222]().

### STDIO Transport

STDIO transport communicates via stdin/stdout and does not start an HTTP server. Verify by:

1. Piping JSON-RPC messages to stdin
2. Checking stdout for responses
3. Monitoring stderr for error messages

**Sources:** [README.md:134-157](), [README.md:217-222]()

---

## Docker Build from Source

To build the Docker image locally:

```bash
docker build -t hf-mcp-server .
```

The Dockerfile uses a multi-stage approach:

1. **Dependency Installation:** [Dockerfile:8-13]() copies package files and runs `pnpm install --frozen-lockfile`
2. **Source Copy:** [Dockerfile:16]() copies all source files
3. **Build Process:** [Dockerfile:24-26]() runs `pnpm run build` to compile all packages
4. **Single-File Build:** [Dockerfile:29-35]() rebuilds `mcp-welcome.html` as standalone (~252KB self-contained file)

The build process includes verification steps in [Dockerfile:37-47]() that list directory structures and file sizes to confirm successful compilation.

**Sources:** [Dockerfile:1-67](), [.dockerignore:1-18]()

---

## Troubleshooting

### Build Failures

If the build fails with TypeScript errors:

```bash
pnpm clean
pnpm install
pnpm build
```

### Port Already in Use

If port 3000 is occupied, specify a different port:

```bash
PORT=3001 pnpm dev
```

Or for Docker:

```bash
docker run --rm -p 3001:3000 -e PORT=3001 ghcr.io/evalstate/hf-mcp-server:latest
```

Note: The internal container port remains 3000, only the host mapping changes.

### Module Resolution Errors

If you encounter module resolution errors after pulling updates:

```bash
pnpm install --force
pnpm build
```

**Sources:** [packages/app/package.json:55](), [start.sh:8]()

---

# Page: Client Integration

# Client Integration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.dockerignore](.dockerignore)
- [Dockerfile](Dockerfile)
- [README.md](README.md)
- [packages/app/src/server/utils/tool-selection-strategy.ts](packages/app/src/server/utils/tool-selection-strategy.ts)
- [packages/app/src/shared/bouquet-presets.ts](packages/app/src/shared/bouquet-presets.ts)
- [packages/app/src/web/components/SettingsCopyPage.tsx](packages/app/src/web/components/SettingsCopyPage.tsx)
- [packages/app/src/web/components/bouquets/ToolPresetsCard.tsx](packages/app/src/web/components/bouquets/ToolPresetsCard.tsx)
- [packages/app/test/server/utils/tool-selection-strategy.test.ts](packages/app/test/server/utils/tool-selection-strategy.test.ts)
- [packages/app/vite.config.ts](packages/app/vite.config.ts)
- [packages/mcp/src/duplicate-space.ts](packages/mcp/src/duplicate-space.ts)
- [packages/mcp/src/error-messages.ts](packages/mcp/src/error-messages.ts)
- [start.sh](start.sh)

</details>



This page provides step-by-step instructions for connecting various MCP clients to the Hugging Face MCP Server. It covers authentication methods, transport selection, client-specific configuration, and URL parameters for customizing tool availability.

For information about the underlying transport implementations and session management, see [Transport Layer Architecture](#7). For details on tool selection and configuration, see [Tool Selection System](#5).

---

## Connection Architecture Overview

The HF MCP Server supports multiple MCP clients through different transport mechanisms. Each client type connects using a specific transport protocol based on its capabilities and deployment environment.

```mermaid
graph TB
    subgraph "Client Categories"
        WebClients["Web-Based Clients<br/>(Claude.ai)"]
        DesktopClients["Desktop Clients<br/>(Claude Desktop, VS Code, Cursor)"]
        CLIClients["CLI Clients<br/>(Claude Code, Gemini CLI)"]
        LocalClients["Local/Self-Hosted<br/>(LM Studio, Codex CLI)"]
    end
    
    subgraph "Authentication Methods"
        OAuth["OAuth Flow<br/>?login parameter"]
        TokenAuth["Token-Based<br/>Authorization: Bearer <token>"]
        EnvAuth["Environment Variable<br/>HF_TOKEN or DEFAULT_HF_TOKEN"]
    end
    
    subgraph "Transport Layer"
        HTTPTransport["StreamableHTTPTransport<br/>POST/GET/DELETE /mcp"]
        STDIOTransport["STDIOTransport<br/>stdin/stdout pipes"]
        SSETransport["SSETransport<br/>GET /sse + POST /message"]
    end
    
    subgraph "Server Entry Points"
        ServerFactory["createServerFactory()<br/>packages/app/src/server/mcp/server-factory.ts"]
        Application["Application<br/>packages/app/src/server/application.ts"]
    end
    
    WebClients --> OAuth
    DesktopClients --> OAuth
    DesktopClients --> TokenAuth
    CLIClients --> OAuth
    CLIClients --> TokenAuth
    LocalClients --> TokenAuth
    LocalClients --> EnvAuth
    
    OAuth --> HTTPTransport
    TokenAuth --> HTTPTransport
    TokenAuth --> STDIOTransport
    EnvAuth --> STDIOTransport
    
    HTTPTransport --> ServerFactory
    STDIOTransport --> ServerFactory
    SSETransport --> ServerFactory
    ServerFactory --> Application
```

**Sources:** [README.md:11-158](), [packages/app/src/web/components/SettingsCopyPage.tsx:49-833](), [start.sh:1-58]()

---

## Authentication Methods

The server supports two primary authentication methods, selected based on the client configuration and transport type.

### OAuth Flow

The OAuth flow is the recommended method for most clients. It provides a secure authentication experience without exposing tokens in configuration files.

**URL Pattern:**
```
https://huggingface.co/mcp?login
```

When a client connects with the `?login` parameter, the server initiates an OAuth flow that:
1. Redirects the user to Hugging Face for authentication
2. Requests appropriate permissions for the user's account
3. Returns an access token that is securely stored by the client

The OAuth flow is handled by the server's authentication middleware and is transparent to the MCP client implementation.

**Supported Clients:**
- Claude Desktop and Claude.ai
- Claude Code
- VS Code
- Cursor
- Gemini CLI

**Sources:** [README.md:12-42](), [packages/app/src/web/components/SettingsCopyPage.tsx:75-121]()

### Token-Based Authentication

Token-based authentication uses a Hugging Face API token passed via the `Authorization` header.

**Header Format:**
```
Authorization: Bearer hf_xxxxxxxxxxxxxxxxxxxxx
```

This method is used for:
- Manual configuration of clients
- Self-hosted deployments
- STDIO transport (via environment variables)
- Automation and CI/CD pipelines

**Token Retrieval:**
Users can generate tokens at https://huggingface.co/settings/tokens. The token should have READ permissions for most operations, and WRITE permissions if using tools like `duplicate_space`.

**Sources:** [README.md:77-105](), [packages/app/src/server/utils/auth-utils.ts]()

### Environment Variable Authentication

For STDIO transport, authentication can be configured via environment variables:

| Variable | Purpose | Transport |
|----------|---------|-----------|
| `HF_TOKEN` | Token for STDIO mode | STDIO only |
| `DEFAULT_HF_TOKEN` | Fallback token when no Authorization header present | All transports |

**Warning:** `DEFAULT_HF_TOKEN` should only be used in development, testing, or local STDIO deployments. Setting this in production HTTP deployments exposes the token to all users.

**Sources:** [README.md:237-248](), [start.sh:12-15]()

---

## Transport Selection by Client

Different clients connect using different transport protocols based on their architecture and capabilities.

```mermaid
graph LR
    subgraph "Client Type"
        Desktop["Desktop Apps<br/>Claude Desktop<br/>VS Code<br/>Cursor<br/>LM Studio"]
        CLI["CLI Tools<br/>Claude Code<br/>Gemini CLI<br/>Codex CLI"]
        Web["Web Apps<br/>Claude.ai"]
    end
    
    subgraph "Transport Implementation"
        HTTP["StreamableHTTPTransport<br/>Stateful HTTP with SSE"]
        STDIO["STDIOTransport<br/>Process stdin/stdout"]
    end
    
    subgraph "Server Files"
        HTTPServer["streamableHttp.ts:46-85<br/>createStreamableHttpTransport()"]
        STDIOServer["stdio.ts:18-42<br/>createStdioTransport()"]
    end
    
    Desktop --> HTTP
    Web --> HTTP
    CLI --> HTTP
    CLI --> STDIO
    
    HTTP --> HTTPServer
    STDIO --> STDIOServer
```

**Transport Characteristics:**

| Transport | Stateful | Endpoints | Session Management | Use Case |
|-----------|----------|-----------|-------------------|----------|
| StreamableHTTP | Yes | POST/GET/DELETE /mcp | Session tracking with heartbeat | Desktop clients, web apps |
| STDIO | No | stdin/stdout | Single long-lived process | CLI tools running locally |
| SSE | Yes | GET /sse, POST /message | Session tracking with heartbeat | Legacy clients (deprecated) |

**Sources:** [README.md:123-157](), [start.sh:34-53](), [packages/app/src/server/transports/]()

---

## Client-Specific Setup Guides

### Claude Desktop and Claude.ai

**Method 1: Connector Gallery (Recommended)**

1. Navigate to https://claude.ai/settings/connectors
2. Click "Browse Connectors"
3. Select "Hugging Face" from the gallery
4. Click "Add"

The connector will automatically configure OAuth authentication and tool availability.

**Method 2: Direct Link**

Click this link to add the connector: [claude.ai/redirect/website.v1.67274164-23df-4883-8166-3c93ced276be/directory/37ed56d5-9d61-4fd4-ad00-b9134c694296](https://claude.ai/redirect/website.v1.67274164-23df-4883-8166-3c93ced276be/directory/37ed56d5-9d61-4fd4-ad00-b9134c694296)

**Sources:** [README.md:11-21](), [packages/app/src/web/components/SettingsCopyPage.tsx:49-122]()

---

### Claude Code

Claude Code supports both OAuth and token-based authentication via HTTP transport.

**OAuth Setup (Recommended):**
```bash
claude mcp add hf-mcp-server -t http https://huggingface.co/mcp?login
```

After running this command:
1. Start Claude: `claude`
2. Follow the OAuth authentication prompts in the browser
3. Grant permissions to the HF MCP Server

**Token-Based Setup:**
```bash
claude mcp add hf-mcp-server \
  -t http https://huggingface.co/mcp \
  -H "Authorization: Bearer <YOUR_HF_TOKEN>"
```

Replace `<YOUR_HF_TOKEN>` with your Hugging Face token from https://huggingface.co/settings/tokens.

**Sources:** [README.md:23-42](), [packages/app/src/web/components/SettingsCopyPage.tsx:697-771]()

---

### Visual Studio Code

VS Code connects via the MCP extension using HTTP transport.

**One-Click Installation:**

Click this link to install: `vscode:mcp/install?%7B%22name%22%3A%22huggingface%22%2C%22gallery%22%3Atrue%2C%22url%22%3A%22https%3A%2F%2Fhuggingface.co%2Fmcp%3Flogin%22%7D`

Alternatively, visit https://code.visualstudio.com/mcp and install "Hugging Face" from the gallery.

**Manual Configuration:**

Add to your VS Code `settings.json`:
```json
{
  "servers": {
    "huggingface": {
      "url": "https://huggingface.co/mcp",
      "headers": {
        "Authorization": "Bearer <HF_TOKEN>"
      }
    }
  }
}
```

**Configuration File Location:**
- Windows: `%APPDATA%\Code\User\settings.json`
- macOS: `~/Library/Application Support/Code/User/settings.json`
- Linux: `~/.config/Code/User/settings.json`

**Sources:** [README.md:68-88](), [packages/app/src/web/components/SettingsCopyPage.tsx:123-397]()

---

### Cursor

Cursor uses the same HTTP transport configuration as VS Code.

**One-Click Installation:**

Visit: https://cursor.com/en/install-mcp?name=Hugging%20Face&config=eyJ1cmwiOiJodHRwczovL2h1Z2dpbmdmYWNlLmNvL21jcD9sb2dpbiJ9

**Manual Configuration:**

Edit your Cursor `mcp.json` file:
```json
{
  "mcpServers": {
    "huggingface": {
      "url": "https://huggingface.co/mcp",
      "headers": {
        "Authorization": "Bearer <HF_TOKEN>"
      }
    }
  }
}
```

**Configuration File Location:**
- Windows: `%APPDATA%\Cursor\User\mcp.json`
- macOS: `~/Library/Application Support/Cursor/User/mcp.json`
- Linux: `~/.config/Cursor/User/mcp.json`

**Sources:** [README.md:90-105](), [packages/app/src/web/components/SettingsCopyPage.tsx:398-526]()

---

### Gemini CLI

Gemini CLI offers two setup methods: direct MCP connection or the HuggingFace extension.

**Method 1: Direct MCP Connection**
```bash
gemini mcp add -t http huggingface https://huggingface.co/mcp?login
```

Then start Gemini and follow the OAuth authentication prompts:
```bash
gemini
```

**Method 2: HuggingFace Extension (Recommended)**

The extension bundles the MCP server with context files and custom commands for better tool usage:

```bash
gemini extensions install https://github.com/huggingface/hf-mcp-server
```

Authenticate the extension:
```bash
gemini
/mcp auth huggingface
```

The extension provides enhanced prompts that teach Gemini how to effectively use HF MCP tools.

**Sources:** [README.md:44-66](), [packages/app/src/web/components/SettingsCopyPage.tsx:599-696]()

---

### LM Studio

LM Studio requires manual token configuration for authentication.

**Installation Link:**

Visit: https://lmstudio.ai/install-mcp?name=huggingface&config=eyJ1cmwiOiJodHRwczovL2h1Z2dpbmdmYWNlLmNvL21jcCIsImhlYWRlcnMiOnsiQXV0aG9yaXphdGlvbiI6IkJlYXJlciA8WU9VUl9IRl9UT0tFTj4ifX0%3D

After clicking the link, replace `<YOUR_HF_TOKEN>` with your Hugging Face API token.

**Sources:** [packages/app/src/web/components/SettingsCopyPage.tsx:527-598]()

---

### Codex CLI

Codex CLI uses STDIO transport via the `mcp-remote` proxy.

**Configuration:**

Edit `~/.codex/config.toml`:
```toml
[mcp_servers.huggingface]
command = "npx"
args = ["-y", "mcp-remote@latest", "https://huggingface.co/mcp?login"]
```

The `mcp-remote` tool acts as a bridge between STDIO and HTTP transports, enabling Codex to connect to the HTTP-based HF MCP Server.

**Sources:** [packages/app/src/web/components/SettingsCopyPage.tsx:772-833]()

---

## Configuration Parameters

### URL Structure and Query Parameters

The server URL supports several query parameters for customizing tool availability and behavior:

**Base URL:**
```
https://huggingface.co/mcp
```

**Common Parameters:**

| Parameter | Values | Description | Example |
|-----------|--------|-------------|---------|
| `login` | (flag) | Initiates OAuth flow | `?login` |
| `bouquet` | Preset name | Overrides tool selection with a preset | `?bouquet=search` |
| `mix` | Preset name | Adds preset tools to user settings | `?mix=docs` |
| `gradio` | Space IDs (comma-separated) | Adds Gradio space endpoints | `?gradio=victor/websearch` |
| `no_image_content` | `true` | Disables Gradio image downloads | `?no_image_content=true` |

**Parameter Combination Examples:**

```
# OAuth with search bouquet
https://huggingface.co/mcp?login&bouquet=search

# OAuth with docs mix added to user settings
https://huggingface.co/mcp?login&mix=docs

# OAuth with custom Gradio space
https://huggingface.co/mcp?login&gradio=victor/websearch

# OAuth with multiple Gradio spaces
https://huggingface.co/mcp?login&gradio=victor/websearch,microsoft/Florence-2-large

# Disable Gradio images
https://huggingface.co/mcp?login&no_image_content=true
```

**Sources:** [packages/app/src/shared/bouquet-presets.ts:13-59](), [packages/app/src/web/components/bouquets/ToolPresetsCard.tsx:9-32](), [packages/app/src/server/utils/tool-selection-strategy.ts:129-147]()

---

### HTTP Headers

Query parameters can also be specified via HTTP headers for programmatic configuration:

```mermaid
graph TB
    subgraph "Request Headers"
        AuthHeader["Authorization: Bearer <token>"]
        BouquetHeader["x-mcp-bouquet: <preset>"]
        MixHeader["x-mcp-mix: <preset>"]
        GradioHeader["x-mcp-gradio: <space-ids>"]
    end
    
    subgraph "Processing"
        AuthUtil["extractAuthBouquetAndMix()<br/>packages/app/src/server/utils/auth-utils.ts"]
        ToolStrategy["ToolSelectionStrategy<br/>packages/app/src/server/utils/tool-selection-strategy.ts"]
    end
    
    subgraph "Result"
        EnabledTools["enabledToolIds: string[]"]
        GradioTools["gradioSpaceTools: SpaceTool[]"]
        Mode["ToolSelectionMode"]
    end
    
    AuthHeader --> AuthUtil
    BouquetHeader --> AuthUtil
    MixHeader --> AuthUtil
    GradioHeader --> AuthUtil
    
    AuthUtil --> ToolStrategy
    ToolStrategy --> EnabledTools
    ToolStrategy --> GradioTools
    ToolStrategy --> Mode
```

**Header Mapping:**

| Query Parameter | HTTP Header | Values |
|-----------------|-------------|--------|
| `bouquet=search` | `x-mcp-bouquet` | `search`, `hf_api`, `spaces`, `docs`, `all` |
| `mix=docs` | `x-mcp-mix` | Same as bouquet values |
| `gradio=foo/bar` | `x-mcp-gradio` | Comma-separated space IDs |

**Example HTTP Request:**
```http
POST /mcp HTTP/1.1
Host: huggingface.co
Authorization: Bearer hf_xxxxxxxxxxxxxxxxxxxxx
x-mcp-bouquet: search
x-mcp-gradio: victor/websearch
Content-Type: application/json

{
  "jsonrpc": "2.0",
  "method": "tools/list",
  "id": 1
}
```

**Sources:** [packages/app/src/server/utils/auth-utils.ts](), [packages/app/src/server/utils/tool-selection-strategy.ts:129-147]()

---

### Bouquet Presets

Bouquets are predefined tool sets that can be activated via the `bouquet` parameter. For detailed information on bouquet configuration and precedence rules, see [Bouquet System](#5.1).

**Available Bouquets:**

| Bouquet | Tools | Description |
|---------|-------|-------------|
| `search` | 5 search tools | Semantic search across models, datasets, papers, and docs |
| `hf_api` | 7 API tools | Balanced search and repository details |
| `spaces` | 5 space tools | Space management and inspection |
| `docs` | 2 doc tools | Documentation search and fetch |
| `all` | 15+ tools | All built-in tools |

**URL Examples:**
```
https://huggingface.co/mcp?login&bouquet=search
https://huggingface.co/mcp?login&bouquet=hf_api
https://huggingface.co/mcp?login&bouquet=spaces
```

**Sources:** [packages/app/src/shared/bouquet-presets.ts:13-59](), [packages/app/src/web/components/bouquets/ToolPresetsCard.tsx:34-139]()

---

### Mix Mode

Mix mode adds bouquet tools to your existing saved settings rather than replacing them. This allows dynamic tool expansion without losing your configured preferences.

**Examples:**

```
# Add docs tools to your saved settings
https://huggingface.co/mcp?login&mix=docs

# Add search tools to your saved settings
https://huggingface.co/mcp?login&mix=search
```

**Precedence:** Mix mode has lower precedence than bouquet override. If both are specified, bouquet takes priority. For detailed precedence rules, see [Tool Selection Strategy](#5.2).

**Sources:** [packages/app/src/server/utils/tool-selection-strategy.ts:154-178]()

---

### Gradio Space Configuration

The `gradio` parameter allows adding custom Gradio spaces as dynamic MCP tools.

**Syntax:**
```
gradio=<username>/<space-name>[,<username>/<space-name>,...]
```

**Examples:**

```
# Single space
https://huggingface.co/mcp?login&gradio=victor/websearch

# Multiple spaces
https://huggingface.co/mcp?login&gradio=victor/websearch,microsoft/Florence-2-large

# Disable all Gradio spaces
https://huggingface.co/mcp?login&gradio=none
```

**Special Value:** `gradio=none` disables all Gradio endpoints, including those from user settings. This is useful when combining with bouquets to get a minimal tool set.

For details on how Gradio spaces are discovered and converted to MCP tools, see [Gradio Integration](#6).

**Sources:** [packages/app/src/server/utils/tool-selection-strategy.ts:84-102](), [packages/app/src/server/utils/gradio-utils.ts]()

---

## Configuration Management Interface

After connecting a client, users can manage their tool configuration at https://huggingface.co/settings/mcp.

```mermaid
graph TB
    subgraph "Web UI Components"
        SettingsPage["SettingsCopyPage<br/>packages/app/src/web/components/SettingsCopyPage.tsx"]
        PresetsCard["ToolPresetsCard<br/>packages/app/src/web/components/bouquets/ToolPresetsCard.tsx"]
    end
    
    subgraph "API Endpoints"
        GetSettings["GET /api/settings"]
        PostSettings["POST /api/settings"]
        GetGradio["GET /api/gradio-endpoints"]
        PostGradio["POST /api/gradio-endpoints"]
    end
    
    subgraph "Backend Services"
        SettingsService["settingsService<br/>packages/app/src/server/utils/settings-service.ts"]
        ApiClient["McpApiClient<br/>packages/app/src/server/utils/mcp-api-client.ts"]
    end
    
    subgraph "State Storage"
        InternalStore["In-Memory Map"]
        ExternalAPI["USER_CONFIG_API<br/>Remote Endpoint"]
    end
    
    SettingsPage --> GetSettings
    SettingsPage --> PostSettings
    PresetsCard --> GetSettings
    
    GetSettings --> SettingsService
    PostSettings --> SettingsService
    GetGradio --> ApiClient
    PostGradio --> ApiClient
    
    SettingsService --> InternalStore
    SettingsService --> ExternalAPI
    ApiClient --> InternalStore
```

**Features:**

1. **Client Setup Instructions**: Copy-paste configuration for each client type
2. **Tool Selection**: Enable/disable built-in tools via web interface
3. **Gradio Space Management**: Add/remove custom Gradio spaces
4. **Bouquet Presets**: View and copy URLs for different tool configurations
5. **Real-Time Updates**: Changes propagate to active MCP sessions via `toolListChanged` notifications

**Sources:** [packages/app/src/web/components/SettingsCopyPage.tsx:835-1439](), [packages/app/src/web/components/bouquets/ToolPresetsCard.tsx:141-226]()

---

## Connection Verification

After configuring a client, verify the connection is working:

### For HTTP-Based Clients

1. Check that the client shows "Connected" or similar status
2. List available tools (method varies by client):
   - Claude: Type a message asking "what tools do you have?"
   - VS Code: Open the MCP panel and view tools list
   - Cursor: Same as VS Code

3. Test a simple tool call:
   ```
   Can you search for models related to "sentiment analysis"?
   ```

### For STDIO-Based Clients

STDIO clients establish the connection when they start. If the process starts without errors, the connection is established.

**Verify with a test query:**
```bash
# For Claude Code
claude

# Then in the Claude prompt:
"Search for models related to sentiment analysis"
```

---

## Troubleshooting Common Issues

### Authentication Failures

**Symptom:** Client reports "401 Unauthorized" or similar error

**Solutions:**
1. Verify your token is valid at https://huggingface.co/settings/tokens
2. Check token has READ permissions (WRITE for `duplicate_space`)
3. For OAuth flow, try re-authenticating by removing and re-adding the connector
4. Verify the `Authorization` header format: `Bearer <token>` (note the space)

**Sources:** [packages/mcp/src/error-messages.ts:10-21]()

---

### Tool List Empty

**Symptom:** Client connects but shows no tools available

**Solutions:**
1. Check your user settings at https://huggingface.co/settings/mcp
2. Verify at least some tools are enabled
3. Try using `bouquet=all` parameter to enable all tools
4. Check server logs for tool selection errors

**Sources:** [packages/app/src/server/utils/tool-selection-strategy.ts:210-221]()

---

### Gradio Spaces Not Appearing

**Symptom:** Custom Gradio spaces configured but not showing as tools

**Solutions:**
1. Verify space IDs are formatted correctly: `username/space-name`
2. Check spaces are public (private spaces may require authentication)
3. Try the `gradio` parameter to explicitly add spaces
4. Wait for space metadata to be fetched (can take 10-30 seconds on first connection)

**Sources:** [packages/app/src/server/utils/gradio-utils.ts]()

---

### Connection Timeout

**Symptom:** Client fails to connect or times out during initial handshake

**Solutions:**
1. Check network connectivity to huggingface.co
2. Verify no firewall is blocking the connection
3. For self-hosted deployments, check server is running and port is accessible
4. Try increasing client timeout settings if available

---

### STDIO Mode Not Starting

**Symptom:** STDIO-based client fails to start the server process

**Solutions:**
1. Verify `npx` is installed and in PATH
2. Check Node.js version (requires Node 18+)
3. Try running the command manually to see error messages
4. For Docker deployments, verify `TRANSPORT=stdio` environment variable

**Sources:** [start.sh:1-58](), [Dockerfile:1-67]()

---

## Advanced Configuration

### Self-Hosted Deployment

For self-hosted deployments, clients connect to your own server instance:

```json
{
  "huggingface": {
    "url": "http://localhost:3000/mcp",
    "headers": {
      "Authorization": "Bearer <HF_TOKEN>"
    }
  }
}
```

**Environment Variables:**
```bash
export PORT=3000
export TRANSPORT=streamableHttpJson
export DEFAULT_HF_TOKEN=hf_xxxxxxxxxxxxx  # Optional, for local use only
```

**Sources:** [README.md:137-157](), [start.sh:1-58]()

---

### Docker Deployment

```bash
# Pull image
docker pull ghcr.io/evalstate/hf-mcp-server:latest

# Run with HTTP transport
docker run --rm -p 3000:3000 \
  -e TRANSPORT=streamableHttpJson \
  -e DEFAULT_HF_TOKEN=hf_xxx \
  ghcr.io/evalstate/hf-mcp-server:latest

# Run with STDIO transport
docker run -i --rm \
  -e TRANSPORT=stdio \
  -e DEFAULT_HF_TOKEN=hf_xxx \
  ghcr.io/evalstate/hf-mcp-server:latest
```

**Client Configuration for Docker:**
```json
{
  "huggingface": {
    "url": "http://localhost:3000/mcp"
  }
}
```

**Sources:** [README.md:199-223](), [Dockerfile:1-67]()

---

### External Settings API

For enterprise deployments, the server can fetch user settings from an external API:

```bash
export USER_CONFIG_API=https://api.example.com/mcp-settings
```

The external API should implement:
- `GET /settings?hfToken=<token>` - Returns user settings
- `POST /settings` - Updates user settings

**Response Format:**
```json
{
  "builtInTools": ["model_search", "dataset_search"],
  "spaceTools": [
    {
      "name": "websearch",
      "subdomain": "victor-websearch",
      "_id": "custom-1",
      "emoji": "🔍"
    }
  ]
}
```

**Sources:** [README.md:244](), [packages/app/src/server/utils/mcp-api-client.ts]()

---

# Page: Architecture

# Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [package.json](package.json)
- [packages/app/package.json](packages/app/package.json)
- [packages/app/src/server/application.ts](packages/app/src/server/application.ts)
- [packages/app/src/server/mcp-server.ts](packages/app/src/server/mcp-server.ts)
- [packages/app/src/server/web-server.ts](packages/app/src/server/web-server.ts)
- [packages/app/src/shared/settings.ts](packages/app/src/shared/settings.ts)
- [packages/app/src/web/App.tsx](packages/app/src/web/App.tsx)
- [packages/mcp/package.json](packages/mcp/package.json)
- [pnpm-lock.yaml](pnpm-lock.yaml)

</details>



This document describes the overall system architecture of the Hugging Face MCP Server, including its package structure, core components, design patterns, and how they interact to serve MCP requests from AI clients.

For detailed information about specific subsystems, see:
- System component details: [System Components](#3.1)
- Package organization: [Package Structure](#3.2)
- MCP Server implementation: [MCP Server Core](#3.3)
- Transport layer design: [Transport Layer Architecture](#3.4)

## System Overview

The Hugging Face MCP Server is organized as a multi-layered application that bridges AI clients to the Hugging Face ecosystem through the Model Context Protocol. The system consists of three primary layers:

1. **Application Layer** (`packages/app`) - Manages server lifecycle, client connections, and web interface
2. **Library Layer** (`packages/mcp`) - Provides tool implementations and shared utilities
3. **External Services** - Hugging Face API, Gradio applications, and documentation services

```mermaid
graph TB
    subgraph Clients["AI Clients"]
        Claude["Claude Desktop/Code"]
        VSCode["VS Code / Cursor"]
        Browser["Web Browser"]
    end
    
    subgraph AppLayer["Application Layer (packages/app)"]
        Application["Application<br/>application.ts"]
        WebServer["WebServer<br/>web-server.ts"]
        
        subgraph Transports["Transport Implementations"]
            STDIO["STDIOTransport<br/>stdio-transport.ts"]
            SSE["SSETransport<br/>sse-transport.ts"]
            HTTP["StreamableHTTPTransport<br/>streamable-http-transport.ts"]
            JSON["StatelessHTTPTransport<br/>stateless-http-transport.ts"]
        end
        
        ServerFactory["createServerFactory()<br/>mcp-server.ts"]
        ProxyFactory["createProxyServerFactory()<br/>mcp-proxy.ts"]
        McpApiClient["McpApiClient<br/>mcp-api-client.ts"]
    end
    
    subgraph LibLayer["Library Layer (packages/mcp)"]
        ToolConfigs["Tool Configurations<br/>tool-ids.ts"]
        ToolImpls["Tool Implementations<br/>ModelSearchTool, etc."]
        GradioUtils["Gradio Utilities<br/>gradio-*.ts"]
    end
    
    subgraph External["External Services"]
        HFAPI["Hugging Face API"]
        GradioSpaces["Gradio Spaces"]
    end
    
    Claude --> STDIO
    VSCode --> HTTP
    Browser --> WebServer
    
    Application --> WebServer
    Application --> McpApiClient
    
    STDIO --> ServerFactory
    SSE --> ServerFactory
    HTTP --> ServerFactory
    JSON --> ServerFactory
    
    ServerFactory --> ProxyFactory
    ProxyFactory --> ToolConfigs
    ServerFactory --> ToolConfigs
    
    ToolConfigs --> ToolImpls
    ProxyFactory --> GradioUtils
    
    ToolImpls --> HFAPI
    GradioUtils --> GradioSpaces
```

**Sources:** [packages/app/src/server/application.ts:1-198](), [packages/app/src/server/web-server.ts:1-491](), [packages/app/src/server/mcp-server.ts:1-897](), [packages/app/package.json:1-112](), [packages/mcp/package.json:1-54]()

## Package Organization

The system is structured as a pnpm monorepo with workspace dependencies:

| Package | Path | Purpose | Main Exports |
|---------|------|---------|-------------|
| `@llmindset/hf-mcp-server` | `packages/app` | Application runtime, transports, web server | Binary executables, server implementations |
| `@llmindset/hf-mcp` | `packages/mcp` | Tool implementations, shared utilities | Tool classes, configuration objects |

**Dependency Flow:**
```
packages/app (application)
    ├─> packages/mcp (library)
    ├─> @modelcontextprotocol/sdk
    ├─> express (web server)
    └─> react (web UI)

packages/mcp (library)
    ├─> @modelcontextprotocol/sdk
    ├─> @huggingface/hub
    └─> zod (schema validation)
```

The `packages/app` package declares a workspace dependency on `packages/mcp` via `"@llmindset/hf-mcp": "workspace:^"` in [packages/app/package.json:59]().

**Binary Entrypoints:**

The application package exposes three binary commands in [packages/app/package.json:7-11]():

| Binary | File | Transport Type |
|--------|------|----------------|
| `hf-mcp-server` | `dist/server/stdio.js` | STDIO (CLI) |
| `hf-mcp-server-http` | `dist/server/streamableHttp.js` | Stateful HTTP |
| `hf-mcp-server-http-json` | `dist/server/streamableHttpJson.js` | Stateless HTTP |

**Sources:** [package.json:1-39](), [packages/app/package.json:1-112](), [packages/mcp/package.json:1-54]()

## Core Components and Responsibilities

### Application Orchestrator

The `Application` class in [packages/app/src/server/application.ts:23-198]() coordinates the entire server lifecycle:

**Key Responsibilities:**
- Initializes `WebServer` instance
- Creates `McpApiClient` for global tool state management
- Constructs server factory pipeline: `createServerFactory()` → `createProxyServerFactory()`
- Initializes appropriate transport based on `TransportType`
- Manages startup/shutdown sequences

**Constructor Dependencies:**
```typescript
interface ApplicationOptions {
    transportType: TransportType;
    webAppPort: number;
    webServerInstance: WebServer;
    apiClientConfig?: ApiClientConfig;
}
```

The application ensures proper ordering: web server starts first, then transport initializes, then static files are configured. This prevents route conflicts between transport endpoints and static assets.

**Sources:** [packages/app/src/server/application.ts:1-198]()

### WebServer

The `WebServer` class in [packages/app/src/server/web-server.ts:21-491]() provides the HTTP foundation:

**Core Functions:**
1. Express application setup with security middleware
2. CORS configuration with origin allowlist
3. API route management (`/api/transport`, `/api/settings`, `/api/transport-metrics`, etc.)
4. Static file serving (production) or Vite middleware integration (development)
5. Session and transport info aggregation

**Important Methods:**

| Method | Purpose | Line Reference |
|--------|---------|----------------|
| `setupMiddleware()` | Configure CORS, body parsing, security headers | [39-115]() |
| `setupApiRoutes()` | Register all `/api/*` endpoints | [223-489]() |
| `setupStaticFiles()` | Configure static assets or Vite dev server | [182-221]() |
| `setTransportInfo()` | Update transport metadata | [121-123]() |
| `setTransport()` | Inject transport instance for metrics | [138-140]() |

The WebServer maintains global tool state in `localSharedToolStates` [packages/app/src/server/web-server.ts:30]() and emits `toolStateChange` events via `McpApiClient` when settings are updated.

**Sources:** [packages/app/src/server/web-server.ts:1-491]()

### MCP Server Factory

The factory pattern is implemented in two stages:

**Stage 1: Base Factory** (`createServerFactory` in [packages/app/src/server/mcp-server.ts:96-896]())

Returns a `ServerFactory` function that:
1. Authenticates via `extractAuthBouquetAndMix()` to extract `hfToken`
2. Invokes `ToolSelectionStrategy.selectTools()` to determine enabled tools
3. Creates a new `McpServer` instance from `@modelcontextprotocol/sdk`
4. Registers all built-in tools (15+ tools) and prompts (4 prompts)
5. Registers dynamic tools conditionally based on tool selection
6. Sets up event listeners for `toolStateChange` events

**Stage 2: Proxy Factory** (`createProxyServerFactory` in [packages/app/src/server/mcp-proxy.ts]())

Wraps the base factory to inject Gradio tool discovery:
1. Calls original factory to get base `McpServer`
2. Parses Gradio space IDs from headers and settings
3. Fetches Gradio schemas via `fetchGradioSubdomains()`
4. Registers dynamic Gradio tools as `gr1_*`, `gr2_*`, etc.
5. Returns enhanced server instance

**Tool Registration Pattern:**

```typescript
toolInstances[TOOL_NAME] = server.tool(
    TOOL_CONFIG.name,           // Tool identifier
    TOOL_CONFIG.description,    // Human description
    TOOL_CONFIG.schema.shape,   // Zod schema
    TOOL_CONFIG.annotations,    // Metadata (title, hints)
    async (params) => { ... }   // Handler function
);
```

Each registered tool returns an object with `enable()` and `disable()` methods that control tool visibility to clients.

**Sources:** [packages/app/src/server/mcp-server.ts:1-897]()

### Transport Layer Hierarchy

The transport layer uses an inheritance hierarchy defined in [packages/app/src/server/transport/base-transport.ts]():

```mermaid
graph TB
    BaseTransport["BaseTransport<br/>(abstract)<br/>base-transport.ts"]
    StatefulTransport["StatefulTransport<br/>(abstract)<br/>stateful-transport.ts"]
    
    STDIO["STDIOTransport<br/>stdio-transport.ts"]
    SSE["SSETransport<br/>sse-transport.ts"]
    HTTP["StreamableHTTPTransport<br/>streamable-http-transport.ts"]
    Stateless["StatelessHTTPTransport<br/>stateless-http-transport.ts"]
    
    BaseTransport --> StatefulTransport
    BaseTransport --> Stateless
    StatefulTransport --> STDIO
    StatefulTransport --> SSE
    StatefulTransport --> HTTP
    
    BaseTransport -.provides.-> Metrics["validateAuthAndTrackMetrics()"]
    StatefulTransport -.provides.-> Sessions["Session Management<br/>Heartbeat/Stale Detection"]
```

**BaseTransport** (abstract class) provides:
- `validateAuthAndTrackMetrics()` - Token validation and request tracking
- `ServerFactory` integration
- Metrics collection interface

**StatefulTransport** (abstract class, extends BaseTransport) adds:
- Session map management (`sessions: Map<string, SessionInfo>`)
- Heartbeat mechanism (30s interval)
- Stale session detection (10min timeout)
- Ping/pong support for connection health

**Concrete Implementations:**

| Transport | Base Class | Session Model | Use Case |
|-----------|------------|---------------|----------|
| `STDIOTransport` | `StatefulTransport` | Single persistent session | CLI clients (Claude Code, Gemini) |
| `SSETransport` | `StatefulTransport` | Multiple sessions via session map | Real-time web clients |
| `StreamableHTTPTransport` | `StatefulTransport` | Multiple sessions via session map | Stateful HTTP clients |
| `StatelessHTTPTransport` | `BaseTransport` | Per-request server creation | Stateless HTTP clients, analytics mode |

**Sources:** For detailed transport implementations, see [Transport Layer Architecture](#3.4)

### McpApiClient

The `McpApiClient` class in [packages/app/src/server/utils/mcp-api-client.ts]() provides centralized tool state management:

**Operating Modes:**

1. **Polling Mode** - Polls `/api/settings` at regular intervals (default 5s)
2. **External API Mode** - Fetches settings from external `USER_CONFIG_API` endpoint

**Key Methods:**

| Method | Purpose |
|--------|---------|
| `startPolling()` | Begin periodic settings fetch |
| `stopPolling()` | Stop polling |
| `getGradioEndpoints()` | Return current Gradio space tools |
| `emit('toolStateChange', ...)` | Notify all MCP server instances of state changes |

The client extends `EventEmitter` to broadcast `toolStateChange` events. Each MCP server instance listens for these events and calls `enable()`/`disable()` on the corresponding tool instance.

**Sources:** [packages/app/src/server/application.ts:87-93](), [packages/app/src/server/web-server.ts:403-410]()

## Request Processing Flow

The following diagram illustrates a complete request lifecycle from client to tool execution:

```mermaid
sequenceDiagram
    participant Client
    participant Transport
    participant Factory["Server Factory"]
    participant Strategy["ToolSelectionStrategy"]
    participant Server["McpServer Instance"]
    participant Tool["Tool Implementation"]
    participant HFAPI["HF API"]
    
    rect rgb(245, 245, 245)
        Note over Client,Server: Connection Phase
        Client->>Transport: Connect (HTTP/STDIO/SSE)
        Transport->>Transport: validateAuthAndTrackMetrics()
        Transport->>Factory: Call ServerFactory(headers, settings)
        Factory->>Strategy: selectTools(context)
        Strategy-->>Factory: ToolSelectionResult
        Factory->>Server: new McpServer()
        Factory->>Server: Register tools via server.tool()
        Server-->>Transport: Server instance ready
        Transport-->>Client: Connection established
    end
    
    rect rgb(245, 245, 245)
        Note over Client,HFAPI: Tool Invocation Phase
        Client->>Transport: tools/call model_search
        Transport->>Server: Route to tool handler
        Server->>Tool: ModelSearchTool.searchWithParams()
        Tool->>HFAPI: API call with token
        HFAPI-->>Tool: Search results
        Tool->>Tool: Format as ToolResult
        Tool-->>Server: Formatted response
        Server-->>Transport: JSON-RPC response
        Transport->>Transport: Log metrics
        Transport-->>Client: Return result
    end
```

**Key Stages:**

1. **Connection Phase** ([packages/app/src/server/mcp-server.ts:96-172]()):
   - Transport calls `validateAuthAndTrackMetrics()` to extract token
   - Factory invokes `ToolSelectionStrategy` to determine enabled tools
   - New `McpServer` instance created with all tools registered
   - Tools start in enabled or disabled state based on selection result

2. **Tool Invocation Phase** ([packages/app/src/server/mcp-server.ts:383-406]()):
   - Client sends `tools/call` JSON-RPC request
   - Transport routes to appropriate server instance
   - Server invokes tool handler function
   - Tool calls Hugging Face API with authenticated token
   - Result formatted and returned via JSON-RPC

**Sources:** [packages/app/src/server/mcp-server.ts:96-406](), [packages/app/src/server/transport/base-transport.ts]()

## Design Patterns

### Factory Pattern

The system employs a two-stage factory pattern:

**Primary Factory** (`createServerFactory`):
```typescript
type ServerFactory = (
    headers: Record<string, string> | null,
    userSettings?: AppSettings,
    skipGradio?: boolean,
    sessionInfo?: SessionInfo
) => Promise<ServerFactoryResult>;
```

This function is invoked by transports to create fresh MCP server instances. Each invocation:
- Performs authentication
- Applies tool selection strategy
- Registers all tools
- Sets up event listeners

**Proxy Factory** (`createProxyServerFactory`):
Wraps the primary factory to intercept and enhance with Gradio tools. Uses the decorator pattern to transparently add functionality without modifying the base factory.

**Sources:** [packages/app/src/server/mcp-server.ts:96](), [packages/app/src/server/transport/base-transport.ts:66-75]()

### Strategy Pattern

The `ToolSelectionStrategy` class in [packages/app/src/server/utils/tool-selection-strategy.ts]() encapsulates tool selection logic:

**Precedence Rules:**
1. `x-mcp-bouquet` header (highest priority)
2. `x-mcp-mix` header + user settings
3. User settings only
4. Fallback to all tools

**Key Method:**
```typescript
async selectTools(context: ToolSelectionContext): Promise<ToolSelectionResult>
```

Returns:
- `enabledToolIds: string[]` - Tools to enable
- `gradioSpaceTools: SpaceTool[]` - Gradio endpoints to register
- `mode: ToolSelectionMode` - How selection was determined
- `reason: string` - Explanation for logging

The strategy is invoked during server factory execution in [packages/app/src/server/mcp-server.ts:115-185]().

**Sources:** [packages/app/src/server/utils/tool-selection-strategy.ts](), [packages/app/src/server/mcp-server.ts:115-185]()

### Observer Pattern

Tool state changes propagate via the observer pattern:

```mermaid
graph LR
    WebUI["Web UI<br/>/api/settings POST"]
    WebServer["WebServer<br/>API Handler"]
    ApiClient["McpApiClient<br/>EventEmitter"]
    Server1["McpServer Instance 1"]
    Server2["McpServer Instance 2"]
    Server3["McpServer Instance N"]
    
    WebUI -->|Update settings| WebServer
    WebServer -->|"emit('toolStateChange')"| ApiClient
    ApiClient -->|Event| Server1
    ApiClient -->|Event| Server2
    ApiClient -->|Event| Server3
    Server1 -->|"toolInstance.enable()"| Server1
    Server2 -->|"toolInstance.disable()"| Server2
```

Each MCP server instance registers a `toolStateChange` listener in [packages/app/src/server/mcp-server.ts:873-891](). When the web UI updates settings via `/api/settings`, the `WebServer` emits events to all listening servers, which immediately update tool visibility.

**Sources:** [packages/app/src/server/web-server.ts:395-410](), [packages/app/src/server/mcp-server.ts:873-891]()

## Component Communication

### Application to WebServer

The `Application` class coordinates with `WebServer` through method calls:

```typescript
// In application.ts constructor
this.webServerInstance = options.webServerInstance;

// Setup sequence
this.webServerInstance.setTransportInfo(transportInfo);
this.webServerInstance.setupApiRoutes();
await this.webServerInstance.start(port);
```

**Sources:** [packages/app/src/server/application.ts:36-123]()

### WebServer to Transport

`WebServer` receives transport instance to access session data and metrics:

```typescript
// In application.ts
this.webServerInstance.setTransport(this.transport);

// In web-server.ts API routes
const sessions = this.transport.getSessions();
const metrics = this.transport.getMetrics();
```

This allows the web API to expose real-time transport status at `/api/sessions` and `/api/transport-metrics`.

**Sources:** [packages/app/src/server/web-server.ts:232-251](), [packages/app/src/server/application.ts:140]()

### Transport to Server Factory

Transports invoke the `ServerFactory` function to create MCP server instances:

**STDIO Transport** (single long-lived server):
```typescript
// In stdio-transport.ts
const { server } = await this.serverFactory(headers, undefined, false, sessionInfo);
this.mcpServer = server;
```

**Stateful HTTP Transports** (per-session servers):
```typescript
// Session creation
const { server } = await this.serverFactory(headers, userSettings, false, sessionInfo);
sessionInfo.mcpServer = server;
this.sessions.set(sessionId, sessionInfo);
```

**Stateless Transport** (per-request servers):
```typescript
// Each request creates new server
const { server } = await this.serverFactory(headers, userSettings, skipGradio, sessionInfo);
// Server used for single request then discarded
```

**Sources:** [packages/app/src/server/transport/base-transport.ts:66-75]()

### Server to Tools

The `McpServer` instance routes tool calls to registered handlers:

```typescript
// Tool registration in mcp-server.ts
server.tool(
    MODEL_SEARCH_TOOL_CONFIG.name,
    MODEL_SEARCH_TOOL_CONFIG.description,
    MODEL_SEARCH_TOOL_CONFIG.schema.shape,
    MODEL_SEARCH_TOOL_CONFIG.annotations,
    async (params: ModelSearchParams) => {
        const modelSearch = new ModelSearchTool(hfToken);
        const result = await modelSearch.searchWithParams(params);
        return { content: [{ type: 'text', text: result.formatted }] };
    }
);
```

Each tool handler instantiates the appropriate tool class from `packages/mcp` with the user's authentication token and invokes its methods.

**Sources:** [packages/app/src/server/mcp-server.ts:383-406]()

## Configuration and Environment

The system reads configuration from environment variables and settings:

| Variable | Purpose | Used By |
|----------|---------|---------|
| `DEFAULT_HF_TOKEN` | Default authentication token | `Application`, all transports |
| `USER_CONFIG_API` | External settings API URL | `Application`, `McpApiClient` |
| `NODE_ENV` | Development vs production mode | `WebServer`, `Application` |
| `CORS_ALLOWED_ORIGINS` | CORS origin allowlist override | `WebServer` |
| `HSTS` | Enable HTTP Strict Transport Security | `WebServer` |

**Runtime Configuration Flow:**
1. `Application` constructor reads `DEFAULT_HF_TOKEN` and `USER_CONFIG_API`
2. Creates `TransportInfo` object with configuration in [packages/app/src/server/application.ts:41-49]()
3. Passes to `McpApiClient` constructor
4. `McpApiClient` determines polling vs external mode in [packages/app/src/server/application.ts:66-86]()

**Sources:** [packages/app/src/server/application.ts:41-86](), [packages/app/src/server/web-server.ts:39-115]()

## State Management

### Local Settings Service

The `settingsService` in [packages/app/src/shared/settings.ts:50-96]() provides in-memory settings storage:

```typescript
interface AppSettings {
    builtInTools: string[];      // Enabled built-in tool IDs
    spaceTools: SpaceTool[];     // Gradio space configurations
}
```

**Key Operations:**
- `getSettings()` - Returns current settings
- `updateBuiltInTools()` - Updates enabled tools array
- `updateSpaceTools()` - Updates Gradio endpoints
- `isToolEnabled()` - Checks individual tool state

Used only in non-external-API mode (when `USER_CONFIG_API` is not set).

**Sources:** [packages/app/src/shared/settings.ts:1-96]()

### Session Management

Stateful transports maintain session state:

```typescript
interface SessionInfo {
    id: string;
    connectedAt: Date;
    lastActivity: Date;
    requestCount: number;
    mcpServer?: McpServer;
    clientInfo?: { name: string; version: string };
}
```

The session map is checked periodically by stale detection routines. Sessions with `lastActivity` older than 10 minutes are cleaned up.

**Sources:** For transport-specific session management, see [Transport Layer Architecture](#3.4)

### Tool State Synchronization

Tool states synchronize across all MCP server instances through the event system:

1. User updates settings in web UI
2. `/api/settings` endpoint receives POST request
3. `WebServer` updates `settingsService` and local state map
4. `WebServer` emits `toolStateChange` events via `McpApiClient`
5. All listening MCP servers receive events
6. Each server calls `enable()` or `disable()` on affected tools

This ensures immediate propagation without requiring reconnection.

**Sources:** [packages/app/src/server/web-server.ts:381-413](), [packages/app/src/server/mcp-server.ts:873-891]()

---

# Page: System Components

# System Components

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [packages/app/src/server/application.ts](packages/app/src/server/application.ts)
- [packages/app/src/server/mcp-server.ts](packages/app/src/server/mcp-server.ts)
- [packages/app/src/server/web-server.ts](packages/app/src/server/web-server.ts)
- [packages/app/src/shared/settings.ts](packages/app/src/shared/settings.ts)
- [packages/app/src/web/App.tsx](packages/app/src/web/App.tsx)

</details>



## Purpose and Scope

This document describes the five major components of the Hugging Face MCP Server architecture and their interactions. These components work together to provide a complete Model Context Protocol implementation that connects AI clients to Hugging Face services.

The components covered here are:
- **Application**: Lifecycle orchestration and component coordination
- **WebServer**: HTTP API and static file serving
- **MCP Server**: Tool and prompt registration with the MCP SDK
- **Transport Layer**: Client communication abstractions (detailed in [Transport Layer Architecture](#3.4))
- **McpApiClient**: Global tool state management

For information about the specific transport implementations, see [Transport Layer Architecture](#3.4). For package organization, see [Package Structure](#3.2).

---

## Component Architecture Overview

The system uses a layered architecture where the `Application` class coordinates all other components. Each component has distinct responsibilities and communicates through well-defined interfaces.

**Component Dependency Graph**

```mermaid
graph TB
    Application["Application<br/>(application.ts)"]
    WebServer["WebServer<br/>(web-server.ts)"]
    ServerFactory["createServerFactory()<br/>(mcp-server.ts)"]
    ProxyFactory["createProxyServerFactory()<br/>(mcp-proxy.ts)"]
    McpServer["McpServer instances<br/>(from @modelcontextprotocol/sdk)"]
    Transport["BaseTransport<br/>(base-transport.ts)"]
    ApiClient["McpApiClient<br/>(mcp-api-client.ts)"]
    Express["Express app"]
    
    Application -->|"constructs"| WebServer
    Application -->|"constructs"| ApiClient
    Application -->|"creates"| ServerFactory
    Application -->|"wraps"| ProxyFactory
    Application -->|"creates via factory"| Transport
    
    WebServer -->|"provides"| Express
    WebServer -->|"references"| Transport
    WebServer -->|"references"| ApiClient
    
    ServerFactory -->|"creates"| McpServer
    ProxyFactory -->|"wraps"| ServerFactory
    ProxyFactory -->|"enhances"| McpServer
    
    Transport -->|"uses"| ServerFactory
    Transport -->|"mounts routes on"| Express
    
    ApiClient -->|"emits events to"| McpServer
    
    style Application fill:#f9f9f9
    style WebServer fill:#f9f9f9
    style ServerFactory fill:#f9f9f9
    style ApiClient fill:#f9f9f9
```

**Sources**: [packages/app/src/server/application.ts:1-198](), [packages/app/src/server/web-server.ts:1-491](), [packages/app/src/server/mcp-server.ts:1-897]()

---

## Application Component

The `Application` class ([packages/app/src/server/application.ts:23-192]()) serves as the main orchestrator that coordinates all other components. It manages the startup sequence, dependency injection, and graceful shutdown.

### Responsibilities

| Responsibility | Implementation |
|---|---|
| Component initialization order | [application.ts:99-123]() |
| Server factory creation | [application.ts:90-93]() |
| Transport lifecycle | [application.ts:133-149]() |
| Tool state management setup | [application.ts:125-131]() |
| Graceful shutdown coordination | [application.ts:172-187]() |

### Construction and Configuration

The `Application` constructor accepts an `ApplicationOptions` interface ([application.ts:13-18]()):

```typescript
interface ApplicationOptions {
  transportType: TransportType;
  webAppPort: number;
  webServerInstance: WebServer;
  apiClientConfig?: ApiClientConfig; // Optional - defaults to polling mode
}
```

The constructor performs these initialization steps:
1. Creates `TransportInfo` object with environment configuration ([application.ts:40-49]())
2. Configures `McpApiClient` based on `USER_CONFIG_API` environment variable ([application.ts:66-86]())
3. Creates base server factory via `createServerFactory()` ([application.ts:90]())
4. Wraps it with Gradio proxy via `createProxyServerFactory()` ([application.ts:93]())

### Startup Sequence

The `start()` method ([application.ts:99-123]()) orchestrates component initialization in this precise order:

```mermaid
sequenceDiagram
    participant Main
    participant App as Application
    participant WS as WebServer
    participant Transport
    participant ApiClient
    
    Main->>App: new Application(options)
    Main->>App: start()
    
    App->>WS: setTransportInfo()
    App->>App: setupToolManagement()
    App->>WS: setupApiRoutes()
    App->>WS: start(port)
    Note over WS: Web server listening
    
    App->>Transport: createTransport()
    App->>WS: setTransport()
    App->>Transport: initialize()
    Note over Transport: Transport routes mounted
    
    App->>WS: setupStaticFiles()
    Note over WS: Static/Vite middleware added
    
    App->>ApiClient: startPolling()
    Note over ApiClient: Tool state sync begins
```

**Sources**: [packages/app/src/server/application.ts:23-192]()

---

## WebServer Component

The `WebServer` class ([packages/app/src/server/web-server.ts:21-490]()) manages the Express HTTP server, API endpoints, static file serving, and acts as the central point for accessing transport and client information.

### Core Responsibilities

```mermaid
graph LR
    WebServer["WebServer"]
    
    subgraph "HTTP Layer"
        Express["Express app"]
        CORS["CORS middleware"]
        Security["Security headers"]
    end
    
    subgraph "API Routes"
        Transport["/api/transport"]
        Sessions["/api/sessions"]
        Metrics["/api/transport-metrics"]
        Settings["/api/settings"]
        Gradio["/api/gradio-endpoints"]
    end
    
    subgraph "Static Serving"
        Vite["Vite dev server<br/>(development)"]
        Static["Static files<br/>(production)"]
    end
    
    WebServer --> Express
    WebServer --> Transport
    WebServer --> Sessions
    WebServer --> Metrics
    WebServer --> Settings
    WebServer --> Gradio
    WebServer --> Vite
    WebServer --> Static
    
    Express --> CORS
    Express --> Security
```

### API Endpoints

The `setupApiRoutes()` method ([web-server.ts:223-489]()) registers these endpoints:

| Endpoint | Method | Purpose | Implementation |
|---|---|---|---|
| `/api/transport` | GET | Returns current `TransportInfo` | [web-server.ts:226-228]() |
| `/api/sessions` | GET | Lists active MCP sessions | [web-server.ts:231-251]() |
| `/api/transport-metrics` | GET | Real-time metrics with optional temp logging | [web-server.ts:254-373]() |
| `/api/settings` | GET | Returns current `AppSettings` | [web-server.ts:376-378]() |
| `/api/settings` | POST | Updates tool/space settings and emits events | [web-server.ts:381-413]() |
| `/api/gradio-endpoints` | GET | Lists Gradio endpoint configuration | [web-server.ts:416-422]() |
| `/api/gradio-endpoints/:index` | POST | Toggles Gradio endpoint enabled state | [web-server.ts:425-454]() |
| `/api/gradio-endpoints/:index` | PUT | Updates Gradio endpoint configuration | [web-server.ts:457-488]() |

### CORS Configuration

CORS is configured globally ([web-server.ts:57-114]()) with support for:
- Exact origin matching from `CORS_ALLOWED_ORIGINS` constant
- Environment variable override via `CORS_ALLOWED_ORIGINS` env var
- Wildcard subdomain patterns (e.g., `*.use-mcp.dev`)
- Exposed headers defined in `CORS_EXPOSED_HEADERS` ([web-server.ts:109]())

### Static File Serving

The `setupStaticFiles()` method ([web-server.ts:182-221]()) configures different serving strategies:

**Development Mode** ([web-server.ts:184-208]()):
- Creates Vite dev server with HMR enabled
- Uses `middlewareMode: true` for integration
- Serves from `packages/app/src/web` directory

**Production Mode** ([web-server.ts:209-220]()):
- Serves pre-built static files from `dist/web`
- Fallback to `index.html` for SPA routing (non-API paths)

### Tool State Management

The `WebServer` maintains local tool state ([web-server.ts:30]()) and coordinates tool state changes:

1. Initializes states via `initializeToolStates()` ([web-server.ts:129-136]())
2. Tracks changes in `POST /api/settings` handler ([web-server.ts:395-410]())
3. Emits `toolStateChange` events through `McpApiClient` ([web-server.ts:405]())

**Sources**: [packages/app/src/server/web-server.ts:1-491]()

---

## MCP Server Component

The MCP Server component consists of factory functions that create `McpServer` instances from the `@modelcontextprotocol/sdk` package. Each instance has tools, prompts, and resources registered.

### Server Factory Pattern

**Server Factory Creation Flow**

```mermaid
graph TB
    createServerFactory["createServerFactory()<br/>(mcp-server.ts:96)"]
    createProxyServerFactory["createProxyServerFactory()<br/>(mcp-proxy.ts)"]
    ServerFactory["ServerFactory function"]
    McpServer["McpServer instance"]
    
    subgraph "Registration"
        Tools["15+ built-in tools<br/>(model_search, etc.)"]
        Prompts["4 prompts<br/>(user_summary, etc.)"]
        Resources["Gradio widget resource<br/>(for OpenAI client)"]
        GradioTools["Dynamic Gradio tools<br/>(discovered at runtime)"]
    end
    
    createServerFactory -->|"returns"| ServerFactory
    createProxyServerFactory -->|"wraps"| ServerFactory
    createProxyServerFactory -->|"adds Gradio discovery"| ServerFactory
    
    ServerFactory -->|"called by transport"| McpServer
    
    McpServer --> Tools
    McpServer --> Prompts
    McpServer --> Resources
    McpServer --> GradioTools
```

### createServerFactory Implementation

The `createServerFactory()` function ([mcp-server.ts:96-896]()) returns a `ServerFactory` that:

1. **Authenticates user** via `whoAmI()` from `@huggingface/hub` ([mcp-server.ts:124-133]())
2. **Selects tools** using `ToolSelectionStrategy` ([mcp-server.ts:115-185]())
3. **Creates `McpServer`** with metadata ([mcp-server.ts:151-172]())
4. **Registers all tools** (15+ built-in tools) ([mcp-server.ts:198-815]())
5. **Registers prompts** (4 prompts) ([mcp-server.ts:221-355]())
6. **Registers resources** (Gradio widget for OpenAI) ([mcp-server.ts:818-831]())
7. **Applies tool states** based on selection strategy ([mcp-server.ts:839-859]())
8. **Sets up event listeners** for dynamic tool state changes ([mcp-server.ts:872-891]())

### Tool Registration Examples

Tools are registered using the `server.tool()` method:

**Authentication Tool** ([mcp-server.ts:198-206]()):
```typescript
server.tool('hf_whoami', whoDescription, {}, 
  { readOnlyHint: true, openWorldHint: false, title: 'Hugging Face User Info' },
  () => { return { content: [{ type: 'text', text: response }] }; }
);
```

**Search Tool** ([mcp-server.ts:357-381]()):
```typescript
toolInstances[SEMANTIC_SEARCH_TOOL_CONFIG.name] = server.tool(
  SEMANTIC_SEARCH_TOOL_CONFIG.name,
  SEMANTIC_SEARCH_TOOL_CONFIG.description,
  SEMANTIC_SEARCH_TOOL_CONFIG.schema.shape,
  SEMANTIC_SEARCH_TOOL_CONFIG.annotations,
  async (params: SearchParams) => {
    const semanticSearch = new SpaceSearchTool(hfToken);
    const searchResult = await semanticSearch.search(params.query, params.limit, params.mcp);
    // ... logging and formatting
    return { content: [{ type: 'text', text: result.formatted }] };
  }
);
```

### Tool Instance Management

All tool registrations return a tool instance with `enable()` and `disable()` methods ([mcp-server.ts:174-177]()). These instances are stored in `toolInstances` map ([mcp-server.ts:191]()) for dynamic state control.

The `applyToolStates()` function ([mcp-server.ts:839-859]()) enables/disables tools based on `ToolSelectionStrategy` results:

```typescript
for (const [toolName, toolInstance] of Object.entries(toolInstances)) {
  if (toolSelection.enabledToolIds.includes(toolName)) {
    toolInstance.enable();
  } else {
    toolInstance.disable();
  }
}
```

### Prompt Registration

Four prompts are registered ([mcp-server.ts:221-355]()) using similar pattern:

| Prompt | Config | Handler Class |
|---|---|---|
| `user_summary` | `USER_SUMMARY_PROMPT_CONFIG` | `UserSummaryPrompt` |
| `paper_summary` | `PAPER_SUMMARY_PROMPT_CONFIG` | `PaperSummaryPrompt` |
| `model_detail_prompt` | `MODEL_DETAIL_PROMPT_CONFIG` | `ModelDetailTool` |
| `dataset_detail_prompt` | `DATASET_DETAIL_PROMPT_CONFIG` | `DatasetDetailTool` |

### Resource Registration

For OpenAI MCP clients (identified by `clientInfo.name === 'openai-mcp'`), a Gradio widget resource is registered ([mcp-server.ts:818-831]()):

```typescript
if (sessionInfo?.clientInfo?.name === 'openai-mcp') {
  const widgetConfig = createGradioWidgetResourceConfig(version);
  server.registerResource(widgetConfig.name, widgetConfig.uri, {}, async () => ({
    contents: [{ uri: widgetConfig.uri, mimeType: widgetConfig.mimeType, 
                 text: widgetConfig.htmlContent, _meta: widgetConfig.metadata }]
  }));
}
```

### Event-Driven Tool State Changes

The server factory sets up listeners for `toolStateChange` events ([mcp-server.ts:873-891]()) in non-JSON, non-external API modes:

```typescript
const toolStateChangeHandler = (toolId: string, enabled: boolean) => {
  const toolInstance = toolInstances[toolId];
  if (toolInstance) {
    if (enabled) { toolInstance.enable(); } 
    else { toolInstance.disable(); }
  }
};
sharedApiClient.on('toolStateChange', toolStateChangeHandler);
```

**Sources**: [packages/app/src/server/mcp-server.ts:1-897]()

---

## Transport Layer Overview

The Transport Layer provides abstraction over different client communication mechanisms. Four implementations exist:

| Transport | Class | Use Case | File |
|---|---|---|---|
| STDIO | `STDIOTransport` | CLI clients (Claude Code) | `stdio-transport.ts` |
| SSE | `SSETransport` | Browser-based clients | `sse-transport.ts` |
| Stateful HTTP | `StreamableHTTPTransport` | IDE clients (VS Code) | `streamable-http-transport.ts` |
| Stateless HTTP | `StatelessHTTPTransport` | Per-request isolation | `stateless-http-transport.ts` |

All transports extend `BaseTransport` ([base-transport.ts]()) which provides common functionality. For detailed information about transport implementations, see [Transport Layer Architecture](#3.4).

### BaseTransport Interface

The `BaseTransport` abstract class defines this interface:

**Key Methods**:
- `initialize(config)`: Mount routes and start services
- `getSessions()`: Return active session information
- `getMetrics()`: Return transport-specific metrics
- `getConfiguration()`: Return transport configuration
- `cleanup()`: Clean up resources on shutdown

**ServerFactory Type** ([base-transport.ts]()):
```typescript
type ServerFactory = (
  headers: Record<string, string> | null,
  userSettings?: AppSettings,
  skipGradio?: boolean,
  sessionInfo?: {
    clientSessionId?: string;
    isAuthenticated?: boolean;
    clientInfo?: { name: string; version: string };
  }
) => Promise<ServerFactoryResult>;
```

Each transport calls the `ServerFactory` to create `McpServer` instances per session or per request.

**Sources**: Referenced in [packages/app/src/server/application.ts:133-149]()

---

## McpApiClient Component

The `McpApiClient` class manages global tool state and provides event-driven coordination between the web UI, MCP server instances, and external configuration sources.

### Architecture

**McpApiClient in System Context**

```mermaid
graph TB
    WebUI["Web UI<br/>(App.tsx)"]
    WebServer["WebServer"]
    ApiClient["McpApiClient<br/>(mcp-api-client.ts)"]
    
    subgraph "State Sources"
        InternalSettings["settingsService<br/>(in-memory)"]
        ExternalAPI["USER_CONFIG_API<br/>(external endpoint)"]
    end
    
    subgraph "MCP Servers"
        Server1["McpServer instance 1"]
        Server2["McpServer instance 2"]
        ServerN["McpServer instance N"]
    end
    
    WebUI -->|"POST /api/settings"| WebServer
    WebServer -->|"emit('toolStateChange')"| ApiClient
    
    ApiClient -->|"poll() or fetch()"| InternalSettings
    ApiClient -->|"poll() or fetch()"| ExternalAPI
    
    ApiClient -.->|"toolStateChange event"| Server1
    ApiClient -.->|"toolStateChange event"| Server2
    ApiClient -.->|"toolStateChange event"| ServerN
```

### Configuration Modes

The `McpApiClient` supports two configuration modes via `ApiClientConfig` type:

**Polling Mode** (default):
```typescript
{
  type: 'polling',
  baseUrl: 'http://localhost:3000',
  pollInterval: 5000,
  staticGradioEndpoints: GradioEndpoint[]
}
```
- Polls `GET /api/settings` endpoint
- Uses local `settingsService`
- Suitable for standalone deployment

**External Mode**:
```typescript
{
  type: 'external',
  externalUrl: 'https://api.example.com/config',
  hfToken?: string
}
```
- Fetches from external API (configured via `USER_CONFIG_API` env var)
- Authenticates using `hfToken` as bearer token
- Suitable for managed/hosted deployments

### Event System

The `McpApiClient` extends `EventEmitter` and emits these events:

| Event | Arguments | Triggered When |
|---|---|---|
| `toolStateChange` | `toolId: string, enabled: boolean` | Tool state changes in settings |

MCP server instances listen for these events ([mcp-server.ts:873-891]()) to dynamically enable/disable tools without requiring client reconnection.

### Polling Mechanism

The `startPolling()` method ([mcp-api-client.ts]()) implements periodic state synchronization:

1. Fetch current settings (internal or external)
2. Compare with previous state
3. Emit `toolStateChange` events for changes
4. Repeat at `pollInterval` (default 5000ms)

### Gradio Endpoint Management

The `McpApiClient` also manages Gradio endpoint configuration:

**Methods**:
- `getGradioEndpoints()`: Returns current Gradio endpoint list
- `updateGradioEndpointState(index, enabled)`: Toggle endpoint enabled state
- `updateGradioEndpoint(index, endpoint)`: Update endpoint configuration

These methods are called by `WebServer` API handlers ([web-server.ts:425-488]()).

**Sources**: Referenced in [packages/app/src/server/application.ts:87](), [packages/app/src/server/web-server.ts:144](), [packages/app/src/server/mcp-server.ts:873-891]()

---

## Component Interaction Flow

This sequence diagram shows how components interact during a typical tool call:

**Complete Request Flow**

```mermaid
sequenceDiagram
    participant Client
    participant Transport as BaseTransport
    participant Factory as ServerFactory
    participant Strategy as ToolSelectionStrategy
    participant Server as McpServer
    participant Tool as Tool Implementation
    participant HFAPI as Hugging Face API
    participant Logger as Query Logger
    
    Note over Client,Logger: Connection Establishment Phase
    Client->>Transport: Connect (HTTP/SSE/STDIO)
    Transport->>Transport: validateAuth()
    Transport->>Factory: createServerFactory(headers, settings)
    Factory->>Strategy: selectTools(context)
    Strategy-->>Factory: ToolSelectionResult
    Factory->>Server: new McpServer()
    Factory->>Server: server.tool() x 15+
    Factory->>Server: server.prompt() x 4
    Factory->>Factory: applyToolStates()
    Server-->>Transport: McpServer instance
    Transport-->>Client: Connection established
    
    Note over Client,Logger: Tool Call Phase
    Client->>Transport: tools/call model_search
    Transport->>Server: route to handler
    Server->>Tool: ModelSearchTool.searchWithParams()
    Tool->>HFAPI: API request
    HFAPI-->>Tool: Search results
    Tool->>Tool: Format as ToolResult
    Tool->>Logger: logSearchQuery()
    Tool-->>Server: Formatted response
    Server-->>Transport: JSON-RPC result
    Transport-->>Client: Tool result
    
    Note over Client,Logger: Dynamic Tool State Change
    Client->>Transport: POST /api/settings
    Transport->>WebServer: Handle settings update
    WebServer->>ApiClient: emit('toolStateChange', toolId, enabled)
    ApiClient-->>Server: toolStateChange event
    Server->>Server: toolInstance.enable/disable()
```

### Key Interaction Points

**Application Startup** ([application.ts:99-123]()):
1. `Application` creates `McpApiClient` in constructor
2. `Application.start()` calls `WebServer.start()`
3. `Application` creates transport via `createTransport()`
4. Transport's `initialize()` mounts routes on Express app
5. `Application` starts API client polling

**Settings Update Flow** ([web-server.ts:381-413]()):
1. Web UI sends `POST /api/settings` with new tool states
2. `WebServer` updates `settingsService`
3. `WebServer` emits events via `ApiClient.emit('toolStateChange')`
4. All `McpServer` instances receive events and update tool states
5. No client reconnection required

**Per-Request Server Creation**:
1. Client sends MCP request to transport endpoint
2. Transport extracts headers and calls `ServerFactory`
3. `ServerFactory` creates new `McpServer` instance
4. Tools execute and return results
5. For stateful transports, same instance is reused per session

**Sources**: [packages/app/src/server/application.ts:99-123](), [packages/app/src/server/web-server.ts:381-413](), [packages/app/src/server/mcp-server.ts:96-896]()

---

# Page: Package Structure

# Package Structure

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [package.json](package.json)
- [packages/app/package.json](packages/app/package.json)
- [packages/mcp/package.json](packages/mcp/package.json)
- [packages/mcp/src/index.ts](packages/mcp/src/index.ts)
- [packages/mcp/src/tool-ids.ts](packages/mcp/src/tool-ids.ts)
- [pnpm-lock.yaml](pnpm-lock.yaml)

</details>



This document explains the monorepo organization of the HF MCP Server codebase, detailing the two primary packages, their responsibilities, dependency relationships, and build outputs. For information about the internal architecture of the MCP server implementation, see [MCP Server Core](#3.3). For build system specifics and development workflows, see [Build System](#9.1).

---

## Monorepo Organization

The HF MCP Server is organized as a **pnpm workspace monorepo** with two distinct packages that separate library functionality from application concerns.

```mermaid
graph TB
    subgraph "Repository Root"
        Root["hf-mcp/<br/>package.json<br/>pnpm-workspace"]
        
        subgraph "Library Package"
            McpPkg["packages/mcp/<br/>@llmindset/hf-mcp<br/>Core tool implementations"]
        end
        
        subgraph "Application Package"
            AppPkg["packages/app/<br/>@llmindset/hf-mcp-server<br/>Server & UI orchestration"]
        end
    end
    
    Root --> McpPkg
    Root --> AppPkg
    AppPkg -->|"workspace:^ dependency"| McpPkg
    
    style McpPkg fill:#f9f9f9
    style AppPkg fill:#f9f9f9
```

**Monorepo Structure**

Sources: [package.json:1-38](), [pnpm-lock.yaml:1-241]()

---

## Package Overview

| Package | Name | Version | Purpose | Published |
|---------|------|---------|---------|-----------|
| Library | `@llmindset/hf-mcp` | 0.2.43 | Tool implementations, schemas, API clients | Yes |
| Application | `@llmindset/hf-mcp-server` | 0.2.43 | MCP server, transports, web UI | Yes (main package) |

The **library package** (`packages/mcp`) contains pure tool logic and can be consumed independently, while the **application package** (`packages/app`) orchestrates the server runtime, transport layers, and user interfaces.

Sources: [packages/app/package.json:2-4](), [packages/mcp/package.json:2-4]()

---

## Library Package: `@llmindset/hf-mcp`

### Package Configuration

The library package is located at `packages/mcp/` and exports reusable tool implementations, utilities, and type definitions.

```mermaid
graph TB
    subgraph "packages/mcp/"
        PkgJson["package.json<br/>Type: module<br/>Main: dist/index.js"]
        
        subgraph "Source Structure"
            Index["src/index.ts<br/>Central export hub"]
            ToolIds["src/tool-ids.ts<br/>Tool ID registry"]
            Tools["src/*-tool.ts<br/>15+ tool implementations"]
            Types["src/types/<br/>Shared types"]
            Gradio["src/gradio-files.js<br/>Gradio integration"]
            Docs["src/docs-search/<br/>Documentation tools"]
        end
        
        subgraph "Build Output"
            DistIndex["dist/index.js<br/>dist/index.d.ts"]
            DistTools["dist/*-tool.js<br/>dist/*-tool.d.ts"]
        end
    end
    
    PkgJson --> Index
    Index --> ToolIds
    Index --> Tools
    Index --> Types
    Index --> Gradio
    Index --> Docs
    
    Index -.compiles to.-> DistIndex
    Tools -.compiles to.-> DistTools
```

**Library Package Structure**

Sources: [packages/mcp/package.json:1-53](), [packages/mcp/src/index.ts:1-30]()

### Export Structure

The library package provides multiple export paths for optimized imports:

| Export Path | File | Purpose |
|------------|------|---------|
| `.` | `dist/index.js` | Default export - all tools and utilities |
| `./semantic` | `dist/semantic-search.js` | Space semantic search tool |
| `./model` | `dist/model-search.js` | Model search tool |
| `./paper` | `dist/paper-search.js` | Paper search tool |

**Named Exports from Main Entry Point**

The main `index.ts` exports all tool implementations, utility functions, and shared types:

```mermaid
graph LR
    Index["src/index.ts"]
    
    subgraph "Tool Exports"
        ApiCall["hf-api-call.js"]
        ModelSearch["model-search.js"]
        DatasetSearch["dataset-search.js"]
        SpaceSearch["space-search.js"]
        PaperSearch["paper-search.js"]
        DocSearch["docs-search/"]
        Gradio["gradio-files.js"]
        UseSpace["use-space.js"]
    end
    
    subgraph "Core Exports"
        ToolIds["tool-ids.ts"]
        Types["types/tool-result.js"]
        Utils["utilities.js"]
    end
    
    Index --> ApiCall
    Index --> ModelSearch
    Index --> DatasetSearch
    Index --> SpaceSearch
    Index --> PaperSearch
    Index --> DocSearch
    Index --> Gradio
    Index --> UseSpace
    Index --> ToolIds
    Index --> Types
    Index --> Utils
```

**Index Export Structure**

Sources: [packages/mcp/src/index.ts:1-30](), [packages/mcp/package.json:7-23]()

### Tool ID Registry

The `tool-ids.ts` file serves as the canonical source of truth for all built-in tool identifiers, exporting constants extracted from tool configurations:

**Tool ID Constants** (examples):
- `SPACE_SEARCH_TOOL_ID` - "space_semantic_search"
- `MODEL_SEARCH_TOOL_ID` - "model_search"
- `MODEL_DETAIL_TOOL_ID` - "model_detail"
- `DATASET_SEARCH_TOOL_ID` - "dataset_search"
- `DOC_FETCH_TOOL_ID` - "hf_doc_fetch"

**Tool ID Groups** - Pre-defined collections for bouquet configurations:
- `TOOL_ID_GROUPS.search` - All search tools (5 tools)
- `TOOL_ID_GROUPS.spaces` - Space management tools (5 tools)
- `TOOL_ID_GROUPS.docs` - Documentation tools (2 tools)
- `TOOL_ID_GROUPS.hf_api` - HF API operation tools (7 tools)
- `TOOL_ID_GROUPS.all` - All built-in tools (15 tools)

Sources: [packages/mcp/src/tool-ids.ts:1-105]()

### Dependencies

The library package has minimal external dependencies:

**Core Dependencies**:
- `@huggingface/hub` (^2.6.12) - HF API client
- `@mcp-ui/server` (^5.12.0) - MCP protocol utilities
- `@modelcontextprotocol/sdk` (^1.20.0) - MCP SDK
- `zod` (^3.24.4) - Schema validation
- `turndown` (^7.2.0) - HTML to Markdown conversion
- `shell-quote` (^1.8.3) - Shell command escaping

Sources: [packages/mcp/package.json:34-41]()

---

## Application Package: `@llmindset/hf-mcp-server`

### Package Configuration

The application package is located at `packages/app/` and serves as the primary distribution package containing server implementations, transport layers, and the web dashboard.

```mermaid
graph TB
    subgraph "packages/app/"
        PkgJson["package.json<br/>Type: module<br/>Main: dist/server/streamableHttp.js"]
        
        subgraph "Server Entry Points"
            Stdio["src/server/stdio.ts<br/>STDIO transport"]
            Http["src/server/streamableHttp.ts<br/>HTTP transport"]
            HttpJson["src/server/streamableHttpJson.ts<br/>JSON-only HTTP"]
            Sse["src/server/sse.ts<br/>SSE transport"]
        end
        
        subgraph "Core Application"
            App["src/application.ts<br/>Application orchestrator"]
            WebServer["src/web-server.ts<br/>Express server"]
            Factory["src/server-factory.ts<br/>MCP server creation"]
            Transport["src/transport/<br/>Transport implementations"]
        end
        
        subgraph "Web Interface"
            UI["src/web/<br/>React dashboard"]
            Vite["vite.config.ts<br/>Frontend build"]
        end
    end
    
    PkgJson --> Stdio
    PkgJson --> Http
    PkgJson --> HttpJson
    PkgJson --> Sse
    
    Stdio --> App
    Http --> App
    HttpJson --> App
    Sse --> App
    
    App --> WebServer
    App --> Factory
    App --> Transport
    WebServer --> UI
```

**Application Package Structure**

Sources: [packages/app/package.json:1-111]()

### Binary Executables

The application package exposes three command-line entry points:

| Binary | File | Transport | Use Case |
|--------|------|-----------|----------|
| `hf-mcp-server` | `dist/server/stdio.js` | STDIO | CLI clients (Claude Code, Gemini) |
| `hf-mcp-server-http` | `dist/server/streamableHttp.js` | HTTP/SSE | Web clients, IDEs (default) |
| `hf-mcp-server-http-json` | `dist/server/streamableHttpJson.js` | HTTP (stateless) | Analytics, single-shot requests |

These binaries are automatically registered in `node_modules/.bin/` when the package is installed.

Sources: [packages/app/package.json:7-10]()

### Build Targets

The application package produces multiple build artifacts:

**Server Builds** (TypeScript → JavaScript):
- `dist/server/*.js` - Server entry points
- `dist/transport/*.js` - Transport implementations
- `dist/*.js` - Core application modules

**Web UI Builds** (Vite bundling):
- `dist/web/` - Production React dashboard
- `dist/mcp-welcome.html` - Single-file welcome page
- `dist/gradio-widget.html` - Gradio iframe widget

**Build Script Execution**:

```mermaid
graph LR
    Build["pnpm run build"]
    
    subgraph "Build Steps"
        Web["build:web<br/>vite build"]
        Single["build:singlefiles<br/>Vite single-file mode"]
        Server["build:server<br/>tsc -p tsconfig.server.json"]
    end
    
    Build --> Web
    Build --> Single
    Build --> Server
    
    Web --> WebDist["dist/web/"]
    Single --> Welcome["dist/mcp-welcome.html"]
    Single --> Widget["dist/gradio-widget.html"]
    Server --> ServerDist["dist/server/<br/>dist/transport/<br/>dist/*.js"]
```

**Build Pipeline**

Sources: [packages/app/package.json:34-39]()

### Application Dependencies

The application package has extensive dependencies for server runtime and UI:

**Server Dependencies**:
- `@llmindset/hf-mcp` (workspace:^) - **Library package dependency**
- `express` (^4.18.3) - HTTP server framework
- `@modelcontextprotocol/sdk` (^1.20.0) - MCP protocol
- `pino` (^9.7.0) - Structured logging
- `cors` (^2.8.5) - CORS middleware

**UI Dependencies**:
- `react` (^19.1.0) / `react-dom` (^19.1.0) - UI framework
- `@radix-ui/*` - UI component primitives
- `tailwindcss` (^4.1.5) - CSS framework
- `@tanstack/react-table` (^8.21.3) - Data tables
- `swr` (^2.3.3) - Data fetching

Sources: [packages/app/package.json:58-87]()

---

## Workspace Dependency Graph

The workspace configuration establishes a one-way dependency relationship from application to library:

```mermaid
graph TB
    subgraph "External Dependencies"
        Npm["npm registry"]
        HfHub["@huggingface/hub"]
        McpSdk["@modelcontextprotocol/sdk"]
        Express["express"]
        React["react/react-dom"]
        Zod["zod"]
    end
    
    subgraph "Workspace Packages"
        McpLib["@llmindset/hf-mcp<br/>packages/mcp"]
        AppPkg["@llmindset/hf-mcp-server<br/>packages/app"]
    end
    
    Npm --> HfHub
    Npm --> McpSdk
    Npm --> Express
    Npm --> React
    Npm --> Zod
    
    HfHub --> McpLib
    McpSdk --> McpLib
    Zod --> McpLib
    
    HfHub --> AppPkg
    McpSdk --> AppPkg
    Express --> AppPkg
    React --> AppPkg
    
    McpLib -->|"workspace:^"| AppPkg
    
    style McpLib fill:#f0f0f0
    style AppPkg fill:#f0f0f0
```

**Package Dependency Relationships**

The `workspace:^` protocol ensures the application package always uses the local version of the library package during development, while npm resolves it to the published version in production.

Sources: [packages/app/package.json:59](), [pnpm-lock.yaml:42-49]()

### Shared Dependencies

Both packages share several core dependencies to maintain compatibility:

| Dependency | Library Version | App Version | Purpose |
|------------|----------------|-------------|---------|
| `@huggingface/hub` | ^2.6.12 | ^2.6.12 | HF API client |
| `@modelcontextprotocol/sdk` | ^1.20.0 | ^1.20.0 | MCP protocol |
| `@mcp-ui/server` | ^5.12.0 | ^5.12.0 | MCP utilities |
| `zod` | ^3.24.4 | ^3.24.4 | Schema validation |
| `typescript` | 5.9.2 | 5.9.2 | Type checking |

Sources: [packages/mcp/package.json:34-40](), [packages/app/package.json:58-86]()

---

## Build System Integration

### TypeScript Compilation

Both packages use TypeScript with declaration file generation:

**Library Package Compilation**:
- Command: `tsc --declaration`
- Output: `dist/` with `.js` and `.d.ts` files
- Entry: `src/index.ts` → `dist/index.js` + `dist/index.d.ts`

**Application Package Compilation**:
- Command: `tsc -p tsconfig.server.json`
- Output: `dist/server/`, `dist/transport/`, `dist/*.js`
- No declaration files (not consumed as library)

Sources: [packages/mcp/package.json:26](), [packages/app/package.json:35]()

### Development Scripts

The root `package.json` provides convenience scripts for concurrent development:

| Script | Command | Purpose |
|--------|---------|---------|
| `dev` | `concurrently "pnpm run --filter=@llmindset/hf-mcp dev" "pnpm run --filter=@llmindset/hf-mcp-server dev"` | Watch both packages |
| `dev:watch` | Similar with watch mode | Full hot-reload development |
| `build` | `pnpm -r build` | Build all packages recursively |
| `test` | `pnpm run -r test` | Run all tests |

The `--filter` flag leverages pnpm's workspace filtering to target specific packages.

Sources: [package.json:7-24]()

---

## Distribution and Publishing

### Published Artifacts

**Primary Package** (`@llmindset/hf-mcp-server`):
- Main entry: `dist/server/streamableHttp.js`
- Binary executables: 3 command-line tools
- Bundled assets: Web UI, welcome page, Gradio widget
- Files published: `dist/**/*`, `components.json`

**Library Package** (`@llmindset/hf-mcp`):
- Main entry: `dist/index.js`
- Type definitions: `dist/index.d.ts`
- Additional exports: `./semantic`, `./model`, `./paper`
- All compiled `.js` and `.d.ts` files

Both packages maintain synchronized version numbers (0.2.43) and use MIT licensing.

Sources: [packages/app/package.json:6-32](), [packages/mcp/package.json:5-23]()

### Repository Configuration

```mermaid
graph TB
    Repo["GitHub Repository<br/>evalstate/hf-mcp-server"]
    
    subgraph "Package Registry"
        NpmApp["npm: @llmindset/hf-mcp-server"]
        NpmLib["npm: @llmindset/hf-mcp"]
    end
    
    subgraph "Package Directories"
        AppDir["packages/app/<br/>directory: packages/app"]
        McpDir["packages/mcp/<br/>directory: (none - root)"]
    end
    
    Repo --> NpmApp
    Repo --> NpmLib
    
    NpmApp --> AppDir
    NpmLib --> McpDir
```

**Repository to Package Mapping**

The `repository.directory` field in `package.json` helps tools like npm and GitHub correctly associate source code locations with published packages.

Sources: [packages/app/package.json:24-28](), [package.json:1-38]()

---

## Key Takeaways

1. **Clean Separation**: Library package (`@llmindset/hf-mcp`) provides reusable tool implementations; application package (`@llmindset/hf-mcp-server`) orchestrates server runtime and UI.

2. **Workspace Protocol**: The application package consumes the library via `workspace:^` dependency, ensuring local development uses the working directory version.

3. **Multiple Entry Points**: The application package exposes three binary executables for different transport modes, while the library provides specialized export paths for tree-shaking optimization.

4. **Independent Publishing**: Both packages are published to npm with synchronized versions, allowing the library to be consumed independently by other projects.

5. **Monorepo Tooling**: Uses pnpm workspaces for efficient dependency management and concurrent development workflows.

Sources: [package.json:1-38](), [packages/app/package.json:1-111](), [packages/mcp/package.json:1-53]()

---

# Page: MCP Server Core

# MCP Server Core

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [packages/app/src/server/gradio-endpoint-connector.ts](packages/app/src/server/gradio-endpoint-connector.ts)
- [packages/app/src/server/mcp-proxy.ts](packages/app/src/server/mcp-proxy.ts)
- [packages/app/src/server/mcp-server.ts](packages/app/src/server/mcp-server.ts)
- [packages/app/src/shared/settings.ts](packages/app/src/shared/settings.ts)
- [packages/app/src/web/App.tsx](packages/app/src/web/App.tsx)

</details>



The MCP Server Core is responsible for creating and configuring individual `McpServer` instances that expose tools, prompts, and resources to MCP clients. This page documents the server factory pattern, tool/prompt registration mechanisms, authentication handling, and dynamic tool state management.

For information about how tools are selected and filtered before registration, see [Tool Selection System](#5). For details about the transport layer that invokes the server factory, see [Transport Layer Architecture](#3.4). For information about Gradio tool discovery and registration, see [Gradio Integration](#6).

---

## Server Factory Pattern

The server factory is the primary abstraction for creating MCP server instances. Each transport implementation calls the factory to create a fresh or cached server instance based on the transport's session model.

**ServerFactory Type Definition**

```mermaid
graph TB
    subgraph "Factory Function Signature"
        Input["ServerFactory Function"]
        Input --> Param1["headers: Record&lt;string, string&gt; | null"]
        Input --> Param2["userSettings?: AppSettings"]
        Input --> Param3["skipGradio?: boolean"]
        Input --> Param4["sessionInfo?: SessionInfo"]
        
        Input --> Output["Promise&lt;ServerFactoryResult&gt;"]
        Output --> Server["server: McpServer"]
        Output --> User["userDetails?: WhoAmI"]
    end
    
    subgraph "Factory Creation"
        Create["createServerFactory()"]
        Create --> WebServer["webServerInstance: WebServer"]
        Create --> ApiClient["sharedApiClient: McpApiClient"]
        Create --> Returns["Returns ServerFactory"]
    end
    
    subgraph "Usage Pattern"
        Transport["Transport Layer"]
        Transport --> Calls["Calls factory(headers, settings, skipGradio, sessionInfo)"]
        Calls --> Creates["Creates McpServer instance"]
        Creates --> Registers["Registers tools/prompts/resources"]
        Registers --> Final["Returns configured server"]
    end
```

The `createServerFactory` function at [packages/app/src/server/mcp-server.ts:96-896]() is the entry point. It accepts a `WebServer` instance and `McpApiClient` and returns a factory function that produces `McpServer` instances.

Sources: [packages/app/src/server/mcp-server.ts:96-109]()

---

## Server Initialization and Metadata

Each server instance is initialized with metadata that identifies it to MCP clients.

**Server Metadata Structure**

| Property | Value | Purpose |
|----------|-------|---------|
| `name` | `@huggingface/mcp-services` | Package identifier |
| `version` | From package.json | Semantic version |
| `title` | `Hugging Face` | Display name |
| `websiteUrl` | `https://huggingface.co/mcp` | Documentation URL |
| `icons` | Hugging Face favicon | Client UI icon |
| `instructions` | Dynamic user context | Initial guidance for AI |

The instructions field dynamically includes authentication status, informing the AI whether the user is authenticated or anonymous with rate limits.

```mermaid
graph LR
    subgraph "Server Creation Flow"
        Factory["createServerFactory()"]
        Factory --> Extract["extractAuthBouquetAndMix()"]
        Extract --> Token["hfToken?"]
        
        Token -->|Present| Auth["whoAmI() API call"]
        Token -->|Absent| Anon["Anonymous mode"]
        
        Auth --> UserInfo["userInfo = 'authenticated as {name}'"]
        Anon --> AnonInfo["userInfo = 'anonymous + rate limits'"]
        
        UserInfo --> Create["new McpServer(metadata, instructions)"]
        AnonInfo --> Create
    end
```

The server is instantiated at [packages/app/src/server/mcp-server.ts:151-172]() using the MCP SDK's `McpServer` class. Authentication is performed at [packages/app/src/server/mcp-server.ts:124-133]() using `@huggingface/hub`'s `whoAmI` function.

Sources: [packages/app/src/server/mcp-server.ts:96-172](), [packages/app/src/server/utils/auth-utils.ts]()

---

## Tool Registration System

Tools are registered using the MCP SDK's `.tool()` method, which accepts a name, description, schema, annotations, and handler function. All built-in tools are registered immediately, but only enabled tools are made available to clients based on the tool selection strategy.

**Tool Registration Pattern**

```mermaid
graph TB
    subgraph "Registration Process"
        Server["McpServer instance"]
        Server --> Method["server.tool(name, description, schema, annotations, handler)"]
        
        Method --> Name["name: string<br/>(unique identifier)"]
        Method --> Desc["description: string<br/>(shown to AI)"]
        Method --> Schema["schema: ZodObject<br/>(parameter validation)"]
        Method --> Annot["annotations: object<br/>(readOnlyHint, openWorldHint, title)"]
        Method --> Handler["handler: async function<br/>(execution logic)"]
        
        Method --> Returns["Returns Tool instance<br/>(with enable/disable methods)"]
    end
    
    subgraph "Storage and Control"
        Returns --> Store["toolInstances[name] = toolInstance"]
        Store --> Enable["toolInstance.enable()"]
        Store --> Disable["toolInstance.disable()"]
    end
```

Each tool registration call returns a `Tool` object with `enable()` and `disable()` methods. These instances are stored in the `toolInstances` map at [packages/app/src/server/mcp-server.ts:191]() for dynamic state management.

**Built-in Tool Registration Examples**

The registration pattern is consistent across all tools:

1. **Search Tools** - e.g., `model_search` at [packages/app/src/server/mcp-server.ts:383-406]()
   - Uses `MODEL_SEARCH_TOOL_CONFIG` imported from `@llmindset/hf-mcp`
   - Instantiates `ModelSearchTool` with `hfToken`
   - Logs query metrics via `logSearchQuery()`
   - Returns formatted text response

2. **Detail Tools** - e.g., `model_detail` at [packages/app/src/server/mcp-server.ts:408-431]()
   - Uses `MODEL_DETAIL_TOOL_CONFIG`
   - Instantiates `ModelDetailTool` with `hfToken`
   - Fetches comprehensive model metadata
   - Returns structured markdown response

3. **Space Management Tools** - e.g., `duplicate_space` at [packages/app/src/server/mcp-server.ts:602-615]()
   - Uses dynamic config via `DuplicateSpaceTool.createToolConfig(username)`
   - Requires authentication (uses `username`)
   - Performs space duplication operation
   - Returns operation status

4. **Documentation Tools** - e.g., `hf_doc_search` at [packages/app/src/server/mcp-server.ts:563-586]()
   - Uses `DOCS_SEMANTIC_SEARCH_CONFIG`
   - Searches Hugging Face documentation
   - Returns ranked documentation results

5. **Dynamic Tools** - `use_space` at [packages/app/src/server/mcp-server.ts:699-815]()
   - Allows invoking any Gradio space by name
   - Supports `view_parameters` and `invoke` operations
   - Applies post-processing for images and OpenAI compatibility
   - Respects `gradio=none` header to disable invoke

**Special Tool: hub_repo_details**

The `hub_repo_details` tool has runtime-configurable schema based on the `README_INCLUDE` flag:

```mermaid
graph TB
    subgraph "hub_repo_details Schema Adaptation"
        Selection["Tool Selection Result"]
        Selection --> Check["hasReadmeFlag(enabledToolIds)"]
        
        Check -->|True| AllowReadme["Include 'include_readme' parameter in schema"]
        Check -->|False| OmitReadme["Omit 'include_readme' parameter from schema"]
        
        AllowReadme --> Dynamic["At execution time:<br/>Re-evaluate flag for current state"]
        OmitReadme --> Register["Register tool with adjusted schema"]
        
        Dynamic --> Handler["Handler checks allowReadme && wantReadme"]
    end
```

This adaptation occurs at [packages/app/src/server/mcp-server.ts:512-561](). The tool re-evaluates the flag at runtime to support UI-driven configuration changes without server restart.

Sources: [packages/app/src/server/mcp-server.ts:357-697](), [packages/mcp/src/tools/]()

---

## Prompt Registration

Prompts provide pre-configured conversation starters that bundle context and instructions for the AI. The server registers four built-in prompts.

**Prompt Registration Pattern**

```mermaid
graph LR
    subgraph "Prompt Structure"
        Config["PROMPT_CONFIG"]
        Config --> Name["name: string"]
        Config --> Desc["description: string"]
        Config --> Schema["schema: ZodObject"]
    end
    
    subgraph "Registration"
        Server["server.prompt()"]
        Server --> Args["name, description, schema.shape, handler"]
        Handler["async handler(params)"]
        Handler --> Generate["Generate prompt text"]
        Generate --> Return["Return GetPromptResult<br/>{description, messages}"]
    end
```

**Registered Prompts**

| Prompt Name | Purpose | Implementation |
|-------------|---------|----------------|
| `user_summary` | Summarize HF user profile | [packages/app/src/server/mcp-server.ts:221-253]() |
| `paper_summary` | Summarize research paper | [packages/app/src/server/mcp-server.ts:255-287]() |
| `model_detail_prompt` | Format model details | [packages/app/src/server/mcp-server.ts:289-321]() |
| `dataset_detail_prompt` | Format dataset details | [packages/app/src/server/mcp-server.ts:323-355]() |

Each prompt instantiates the appropriate tool class (e.g., `UserSummaryPrompt`, `ModelDetailTool`) and returns formatted content as messages with the `user` role. Prompts are logged via `logPromptQuery()` for analytics.

Sources: [packages/app/src/server/mcp-server.ts:221-355]()

---

## Resource Registration

Resources provide static or dynamic content referenced by URI. The server conditionally registers the Gradio widget resource for OpenAI MCP clients.

```mermaid
graph TB
    subgraph "Resource Registration Logic"
        Check["sessionInfo?.clientInfo?.name === 'openai-mcp'"]
        Check -->|True| Create["createGradioWidgetResourceConfig(version)"]
        Check -->|False| Skip["Skip resource registration"]
        
        Create --> Config["widgetConfig<br/>{name, uri, mimeType, htmlContent, metadata}"]
        Config --> Register["server.registerResource()"]
        
        Register --> URI["uri: 'ui://huggingface-mcp/gradio-widget'"]
        Register --> Handler["async handler() => HTMLContent"]
    end
```

The widget provides an HTML template for rendering Gradio outputs in the OpenAI MCP client interface. Registration occurs at [packages/app/src/server/mcp-server.ts:818-831]().

Sources: [packages/app/src/server/mcp-server.ts:818-831](), [packages/app/src/server/resources/gradio-widget-resource.ts]()

---

## Authentication and User Context

Authentication is handled via Hugging Face API tokens passed in headers or environment variables.

**Authentication Flow**

```mermaid
sequenceDiagram
    participant Factory as createServerFactory
    participant Extract as extractAuthBouquetAndMix
    participant HF as @huggingface/hub
    participant Server as McpServer
    
    Factory->>Extract: extractAuthBouquetAndMix(headers)
    Extract-->>Factory: {hfToken, bouquet, gradio, mix}
    
    alt hfToken present
        Factory->>HF: whoAmI({credentials: {accessToken: hfToken}})
        HF-->>Factory: WhoAmI {name, ...}
        Factory->>Factory: Set userInfo = "authenticated as {name}"
    else no token
        Factory->>Factory: Set userInfo = "anonymous + rate limits"
    end
    
    Factory->>Server: new McpServer(metadata, {instructions: userInfo})
    Server-->>Factory: McpServer instance
```

The `hf_whoami` tool is always registered at [packages/app/src/server/mcp-server.ts:198-206]() to provide authentication guidance. It returns either the username or configuration instructions for setting up authentication.

Sources: [packages/app/src/server/mcp-server.ts:111-133](), [packages/app/src/server/mcp-server.ts:198-206](), [packages/app/src/server/utils/auth-utils.ts]()

---

## Dynamic Tool State Management

Tools can be enabled or disabled dynamically without restarting the server, allowing the web UI and API to control tool availability.

**Tool State Control Architecture**

```mermaid
graph TB
    subgraph "Initial State Application"
        Selection["ToolSelectionStrategy.selectTools()"]
        Selection --> Result["ToolSelectionResult<br/>{enabledToolIds: string[]}"]
        Result --> Apply["applyToolStates()"]
        
        Apply --> Loop["for each tool in toolInstances"]
        Loop --> IsEnabled{"toolId in enabledToolIds?"}
        IsEnabled -->|Yes| Enable["toolInstance.enable()"]
        IsEnabled -->|No| Disable["toolInstance.disable()"]
    end
    
    subgraph "Runtime State Changes"
        Event["sharedApiClient.on('toolStateChange')"]
        Event --> Handler["toolStateChangeHandler(toolId, enabled)"]
        Handler --> Lookup["toolInstance = toolInstances[toolId]"]
        Lookup --> Toggle{"enabled?"}
        Toggle -->|True| EnableRT["toolInstance.enable()"]
        Toggle -->|False| DisableRT["toolInstance.disable()"]
    end
```

Initial tool states are applied at [packages/app/src/server/mcp-server.ts:839-859](). For stateful transports in internal API mode, an event listener is registered at [packages/app/src/server/mcp-server.ts:872-891]() to handle real-time tool state changes broadcasted by `McpApiClient`.

The event listener is cleaned up when the server closes via the `server.server.onclose` callback.

**Tool State Application Conditions**

```mermaid
graph TB
    SkipGradio{"skipGradio?"}
    SkipGradio -->|True| NoApply["Skip tool state application<br/>(initialize or tools/call request)"]
    SkipGradio -->|False| Apply["Apply tool states"]
    
    Apply --> Transport{"transportInfo.jsonResponseEnabled<br/>|| transportInfo.externalApiMode?"}
    Transport -->|True| NoListener["Apply states but skip event listener<br/>(stateless mode)"]
    Transport -->|False| WithListener["Apply states and register event listener<br/>(stateful + internal mode)"]
```

This logic ensures tool states are only applied when needed and event listeners are only registered for transports that support dynamic updates.

Sources: [packages/app/src/server/mcp-server.ts:839-892](), [packages/app/src/server/utils/mcp-api-client.ts]()

---

## Capability Declaration

The server declares its capabilities to inform clients about supported MCP features.

```mermaid
graph LR
    subgraph "Capability Registration"
        Register["registerCapabilities()"]
        Register --> Server["server: McpServer"]
        Register --> Client["sharedApiClient: McpApiClient"]
        Register --> Options["options: {hasResources: boolean}"]
        
        Options --> Check{"hasResources?"}
        Check -->|True| Resources["capabilities.resources = {listChanged: false}"]
        Check -->|False| NoResources["Do not register resources capability"]
        
        Server --> Tools["capabilities.tools = {listChanged: true}"]
        Server --> Prompts["capabilities.prompts = {}"]
    end
```

Capabilities are registered at [packages/app/src/server/mcp-server.ts:864-866]() using the `registerCapabilities` utility. The `listChanged: true` flag for tools indicates that the tool list can change dynamically during the session, which is essential for the dynamic Gradio tool registration system.

Resources are only declared if the client is OpenAI MCP (`sessionInfo?.clientInfo?.name === 'openai-mcp'`), as determined by the `hasResources` option.

Sources: [packages/app/src/server/mcp-server.ts:862-866](), [packages/app/src/server/utils/capability-utils.ts]()

---

## Integration with Proxy Factory

The server factory is wrapped by the proxy factory to inject Gradio tool discovery and registration.

**Factory Wrapping Pattern**

```mermaid
graph TB
    subgraph "Factory Creation Chain"
        CreateServer["createServerFactory(webServer, apiClient)"]
        CreateServer --> OriginalFactory["originalServerFactory: ServerFactory"]
        
        OriginalFactory --> Wrap["createProxyServerFactory(webServer, apiClient, originalServerFactory)"]
        Wrap --> ProxyFactory["proxyServerFactory: ServerFactory"]
    end
    
    subgraph "Proxy Invocation Flow"
        Transport["Transport calls proxyFactory()"]
        Transport --> Proxy["createProxyServerFactory execution"]
        
        Proxy --> CallOriginal["result = originalServerFactory(headers, settings, skipGradio, sessionInfo)"]
        CallOriginal --> OrigServer["Returns {server, userDetails}"]
        
        OrigServer --> CheckSkip{"skipGradio?"}
        CheckSkip -->|True| Return1["Return result immediately"]
        CheckSkip -->|False| Gradio["Discover and register Gradio tools"]
        
        Gradio --> Register["registerRemoteTools(server, ...)"]
        Register --> Return2["Return enhanced result"]
    end
```

The original server factory creates the base `McpServer` with all built-in tools registered. The proxy factory at [packages/app/src/server/mcp-proxy.ts:83-276]() then:

1. Calls the original factory to get a server instance
2. Checks if Gradio discovery should be skipped
3. If not skipped:
   - Parses Gradio space IDs from headers and settings
   - Fetches Gradio schemas via `getGradioSpaces()`
   - Registers remote tools via `registerRemoteTools()`
   - Conditionally registers special prompts (e.g., Qwen Image enhancer)

This separation allows the core server factory to focus on built-in tool registration while the proxy handles the dynamic, network-dependent Gradio integration.

Sources: [packages/app/src/server/mcp-server.ts:96-896](), [packages/app/src/server/mcp-proxy.ts:83-276](), [packages/app/src/server/gradio-endpoint-connector.ts]()

---

## Factory Return Value and Session Management

The factory returns a `ServerFactoryResult` containing the configured server and optional user details.

```mermaid
graph LR
    subgraph "ServerFactoryResult Structure"
        Result["ServerFactoryResult"]
        Result --> Server["server: McpServer<br/>(configured instance)"]
        Result --> User["userDetails?: WhoAmI<br/>(authenticated user info)"]
    end
    
    subgraph "Usage by Transport Layer"
        Transport["Transport receives result"]
        Transport --> Session{"Session model?"}
        Session -->|Stateful| Cache["Cache server in session map"]
        Session -->|Stateless| Discard["Use once and discard"]
        
        Cache --> Reuse["Reuse server for subsequent requests"]
        Discard --> Fresh["Create fresh server each request"]
    end
```

The `userDetails` object is returned at [packages/app/src/server/mcp-server.ts:894]() to provide the transport layer with authenticated user information for logging and session tracking purposes. Different transports use this information differently based on their session models (see [Transport Layer Architecture](#3.4)).

Sources: [packages/app/src/server/mcp-server.ts:894-896](), [packages/app/src/server/transport/base-transport.ts]()

---

# Page: Transport Layer Architecture

# Transport Layer Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.dockerignore](.dockerignore)
- [Dockerfile](Dockerfile)
- [README.md](README.md)
- [packages/app/src/server/transport/base-transport.ts](packages/app/src/server/transport/base-transport.ts)
- [packages/app/src/server/transport/sse-transport.ts](packages/app/src/server/transport/sse-transport.ts)
- [packages/app/src/server/transport/stateless-http-transport.ts](packages/app/src/server/transport/stateless-http-transport.ts)
- [packages/app/src/server/transport/streamable-http-transport.ts](packages/app/src/server/transport/streamable-http-transport.ts)
- [packages/app/vite.config.ts](packages/app/vite.config.ts)
- [packages/mcp/src/duplicate-space.ts](packages/mcp/src/duplicate-space.ts)
- [packages/mcp/src/error-messages.ts](packages/mcp/src/error-messages.ts)
- [start.sh](start.sh)

</details>



## Purpose and Scope

The Transport Layer provides an abstraction over different communication mechanisms between MCP clients and the server. This page describes the overall architecture, base classes, and the four transport implementations at a conceptual level.

For detailed implementation specifics of each transport, see [Transport Layer](#7). For information about how the Application orchestrates transport initialization, see [System Components](#3.1).

**Sources**: [README.md:123-131](), [packages/app/src/server/transport/base-transport.ts:1-100]()

## Overview

The HF MCP Server supports four distinct transport implementations, each optimized for different client integration patterns:

| Transport | Mode | Primary Use Case | Endpoint |
|-----------|------|------------------|----------|
| **STDIO** | Stateful | CLI tools (Claude Code, Gemini CLI) | stdin/stdout |
| **SSE** | Stateful | Legacy web clients | `/sse` + `/message` |
| **StreamableHTTP** | Stateful | Modern IDE integrations | `/mcp` |
| **StreamableHTTPJson** | Stateless | High-scale web apps, analytics | `/mcp` |

All transports share common responsibilities: authentication validation, metrics tracking, request routing, and server lifecycle management. The key architectural distinction is between **stateful transports** (which maintain persistent sessions) and **stateless transports** (which create fresh server instances per request).

**Sources**: [README.md:123-131](), [packages/app/src/server/transport/base-transport.ts:39-79]()

## Class Hierarchy

```mermaid
classDiagram
    class BaseTransport {
        <<abstract>>
        +ServerFactory serverFactory
        +Express app
        +MetricsCounter metrics
        +initialize(options)* Promise~void~
        +cleanup()* Promise~void~
        +getActiveConnectionCount()* number
        +getSessions() SessionMetadata[]
        +getMetrics() TransportMetrics
        #validateAuthAndTrackMetrics()
        #trackRequest()
        #trackError()
        #extractMethodForTracking()
    }
    
    class StatefulTransport {
        <<abstract>>
        +Map~string,TSession~ sessions
        +boolean isShuttingDown
        #STALE_CHECK_INTERVAL
        #STALE_TIMEOUT
        #HEARTBEAT_INTERVAL
        #PING_ENABLED
        #PING_INTERVAL
        #startStaleConnectionCheck()
        #startPingKeepAlive()
        #updateSessionActivity()
        #removeStaleSession()* Promise~void~
        #cleanupSession()
        #setupSseEventHandlers()
    }
    
    class SseTransport {
        -Map~string,SSEConnection~ sessions
        +initialize() Promise~void~
        -handleSseConnection()
        -handleSseMessage()
        -createSession()
        #removeStaleSession()
    }
    
    class StreamableHttpTransport {
        -Map~string,StreamableHttpConnection~ sessions
        +initialize() Promise~void~
        -handlePostRequest()
        -handleGetRequest()
        -handleDeleteRequest()
        -createSession()
        #removeStaleSession()
    }
    
    class StatelessHttpTransport {
        -boolean analyticsMode
        -Map~string,AnalyticsSession~ analyticsSessions
        +initialize() Promise~void~
        -handleJsonRpcRequest()
        -shouldHandle()
        -createAnalyticsSession()
    }
    
    BaseTransport <|-- StatefulTransport
    BaseTransport <|-- StatelessHttpTransport
    StatefulTransport <|-- SseTransport
    StatefulTransport <|-- StreamableHttpTransport
```

The transport layer uses a two-tier inheritance model. `BaseTransport` provides core functionality shared by all transports (metrics, authentication, method tracking). `StatefulTransport` extends this with session management capabilities (stale detection, ping keep-alive, activity tracking) required by SSE and StreamableHTTP. The stateless transport directly extends `BaseTransport` since it doesn't maintain persistent sessions.

**Sources**: [packages/app/src/server/transport/base-transport.ts:83-346](), [packages/app/src/server/transport/base-transport.ts:352-806](), [packages/app/src/server/transport/sse-transport.ts:14-20](), [packages/app/src/server/transport/streamable-http-transport.ts:12-18](), [packages/app/src/server/transport/stateless-http-transport.ts:39-59]()

## Base Transport Infrastructure

### BaseTransport Abstract Class

`BaseTransport` provides the foundation for all transport implementations:

```mermaid
graph TB
    subgraph "Core Responsibilities"
        A["ServerFactory<br/>createServerFactory()"]
        B["MetricsCounter<br/>Request/Error/Method tracking"]
        C["Authentication<br/>validateAuthAndTrackMetrics()"]
        D["Request Parsing<br/>extractMethodForTracking()"]
    end
    
    subgraph "Abstract Methods"
        E["initialize(options)"]
        F["cleanup()"]
        G["getActiveConnectionCount()"]
    end
    
    subgraph "Optional Methods"
        H["shutdown()<br/>Mark as shutting down"]
        I["getSessions()<br/>Return session metadata"]
    end
    
    A --> BaseTransport
    B --> BaseTransport
    C --> BaseTransport
    D --> BaseTransport
    E --> BaseTransport
    F --> BaseTransport
    G --> BaseTransport
    H --> BaseTransport
    I --> BaseTransport
    
    BaseTransport["BaseTransport<br/>Abstract Class"]
```

**Key Components:**

- **ServerFactory**: A function type that creates `McpServer` instances with optional authentication and settings. Signature: `(headers, userSettings?, skipGradio?, sessionInfo?) => Promise<ServerFactoryResult>`
- **MetricsCounter**: Tracks requests, errors, method calls, connections, and authentication state
- **Authentication Validation**: Uses `whoAmI()` from `@huggingface/hub` to validate HF tokens, tracks authenticated/anonymous/unauthorized connections
- **Method Extraction**: Parses JSON-RPC request bodies to extract method names for metrics (e.g., `tools/call:model_search`)

**Sources**: [packages/app/src/server/transport/base-transport.ts:83-346]()

### StatefulTransport Abstract Class

`StatefulTransport` extends `BaseTransport` with session management capabilities:

| Feature | Configuration Variable | Default | Purpose |
|---------|----------------------|---------|---------|
| Stale Check Interval | `MCP_CLIENT_CONNECTION_CHECK` | 90000ms | How often to scan for stale sessions |
| Stale Timeout | `MCP_CLIENT_CONNECTION_TIMEOUT` | 600000ms (10min) | Inactivity threshold for removal |
| Heartbeat Interval | `MCP_CLIENT_HEARTBEAT_INTERVAL` | 30000ms | SSE connection health check frequency |
| Ping Enabled | `MCP_PING_ENABLED` | true | Enable ping keep-alive mechanism |
| Ping Interval | `MCP_PING_INTERVAL` | 30000ms | Frequency of ping requests |
| Ping Failure Threshold | `MCP_PING_FAILURE_THRESHOLD` | 1 | Failed pings before session considered distressed |

**Session Management Features:**

1. **Activity Tracking**: Updates `lastActivity` timestamp on every request via `updateSessionActivity()`
2. **Stale Detection**: Periodic timer checks `lastActivity` against `STALE_TIMEOUT`, removes inactive sessions
3. **Ping Keep-Alive**: Fire-and-forget ping requests to validate client connectivity, increment `pingFailures` on errors
4. **Heartbeat Monitoring**: For SSE connections, checks if response stream is destroyed/ended
5. **Client Info Capture**: Associates sessions with client identity (`name`, `version`) from initialize request

**Sources**: [packages/app/src/server/transport/base-transport.ts:352-806](), [README.md:224-235]()

## Session Metadata Structure

All transports use a standardized `SessionMetadata` interface for consistency:

```mermaid
classDiagram
    class SessionMetadata {
        +string id
        +Date connectedAt
        +Date lastActivity
        +number requestCount
        +boolean isAuthenticated
        +ClientInfo? clientInfo
        +Capabilities capabilities
        +number? pingFailures
        +Date? lastPingAttempt
    }
    
    class ClientInfo {
        +string name
        +string version
    }
    
    class Capabilities {
        +boolean? sampling
        +boolean? roots
    }
    
    SessionMetadata --> ClientInfo
    SessionMetadata --> Capabilities
```

This metadata is:
- Stored in session maps for stateful transports (`Map<string, TSession>`)
- Returned by `getSessions()` for monitoring dashboards
- Used for metrics tracking and client-specific behavior
- Logged in system events for analytics

**Sources**: [packages/app/src/server/transport/base-transport.ts:43-61](), [packages/app/src/server/transport/base-transport.ts:63-73]()

## Transport Implementations

### STDIO Transport

**Architecture**: Single long-lived session using stdin/stdout pipes. No HTTP server required.

**Key Characteristics:**
- Environment-based authentication (`HF_TOKEN` or `DEFAULT_HF_TOKEN`)
- Process-level lifecycle (one server instance per process)
- No session management or cleanup required
- Direct pipe communication with client

**Use Case**: CLI tools like Claude Code and Gemini CLI that spawn child processes.

**Sources**: [README.md:126-127](), [start.sh:35-36]()

### SSE Transport (Legacy)

**Architecture**: Stateful sessions with Server-Sent Events for server-to-client streaming.

**Endpoints:**
- `GET /sse?sessionId=<uuid>` - Establish SSE connection
- `POST /message?sessionId=<uuid>` - Send client messages

**Key Characteristics:**
- First client to connect creates session via `GET /sse`
- Separate POST endpoint for client-to-server messages
- Full session lifecycle management (stale detection, ping, heartbeat)
- Supports reconnection attempts but recreates session

**Use Case**: Legacy web clients, being phased out in favor of StreamableHTTP.

**Sources**: [README.md:128-129](), [packages/app/src/server/transport/sse-transport.ts:14-284]()

### StreamableHTTP Transport (Stateful)

**Architecture**: Stateful sessions using modern StreamableHTTP protocol with SSE-like streaming.

**Endpoints:**
- `POST /mcp` - Initialize new session or send requests
- `GET /mcp` - Establish SSE stream for existing session
- `DELETE /mcp` - Terminate session

**Key Characteristics:**
- Single endpoint (`/mcp`) for all operations
- Session ID passed via `Mcp-Session-Id` header
- Initialization detected via `isInitializeRequest()` check
- Full session management with heartbeat and ping
- Graceful shutdown support (503 during `isShuttingDown`)

**Use Case**: Modern IDE integrations (VS Code, Cursor), desktop apps (Claude Desktop).

**Sources**: [README.md:129-130](), [packages/app/src/server/transport/streamable-http-transport.ts:18-313]()

### StreamableHTTPJson Transport (Stateless)

**Architecture**: Stateless request-response model with optional analytics session tracking.

**Endpoint:**
- `POST /mcp` - Handle all JSON-RPC requests

**Key Characteristics:**
- Creates fresh `McpServer` + `StreamableHTTPServerTransport` per request
- Immediate cleanup after response (no persistent state)
- Optional analytics mode tracks sessions without maintaining server state
- Stub responder for simple requests (capabilities, ping) to avoid full server creation
- Static welcome page served on `GET /mcp` (or 405 if `MCP_STRICT_COMPLIANCE=true`)

**Analytics Mode** (`ANALYTICS_MODE=true`):
- Tracks sessions in `Map<string, AnalyticsSession>` where `server: null`
- Session ID returned in `Mcp-Session-Id` response header on initialize
- Client must send session ID in subsequent requests
- 404 error if session not found (tracks failed resumptions)
- Supports `DELETE /mcp` to explicitly delete analytics session

**Use Case**: High-scale web applications, serverless deployments, analytics tracking.

**Sources**: [README.md:130-131](), [packages/app/src/server/transport/stateless-http-transport.ts:39-555]()

## Request Flow Comparison

```mermaid
sequenceDiagram
    participant C as Client
    participant T as Transport
    participant F as ServerFactory
    participant S as McpServer
    
    rect rgb(245, 245, 245)
        Note over C,S: Stateful Flow (SSE/StreamableHTTP)
        C->>T: Initialize request
        T->>T: validateAuthAndTrackMetrics()
        T->>F: serverFactory(headers)
        F->>S: new McpServer + register tools
        S-->>F: server instance
        F-->>T: ServerFactoryResult
        T->>T: Store in sessions Map
        T->>S: server.connect(transport)
        S-->>C: Initialize response
        
        C->>T: Subsequent request (with session ID)
        T->>T: sessions.get(sessionId)
        T->>T: updateSessionActivity()
        T->>S: Route to existing server
        S-->>C: Response
    end
    
    rect rgb(240, 240, 240)
        Note over C,S: Stateless Flow (StreamableHTTPJson)
        C->>T: Initialize request
        T->>T: validateAuthAndTrackMetrics()
        T->>F: serverFactory(headers)
        F->>S: new McpServer
        S-->>F: server instance
        F-->>T: ServerFactoryResult
        T->>S: server.connect(new transport)
        S-->>C: Response + session ID
        T->>T: cleanup() - close server
        
        C->>T: Subsequent request (with session ID)
        T->>T: Check analytics session exists
        T->>F: serverFactory(headers) - NEW SERVER
        F->>S: new McpServer
        T->>S: server.connect(new transport)
        S-->>C: Response
        T->>T: cleanup() - close server
    end
```

**Key Differences:**

1. **Server Lifecycle**: Stateful transports create one server per session that persists; stateless creates and destroys a server for each request
2. **Session Storage**: Stateful stores full `{ transport, server, metadata }` objects; stateless (analytics mode) stores only `{ transport: null, server: null, metadata }`
3. **Activity Tracking**: Stateful updates `lastActivity` on existing session; stateless validates session existence in analytics map
4. **Cleanup Timing**: Stateful cleanup on stale timeout or explicit close; stateless cleanup immediately after response

**Sources**: [packages/app/src/server/transport/streamable-http-transport.ts:92-170](), [packages/app/src/server/transport/stateless-http-transport.ts:141-408]()

## Server Factory Pattern

The `ServerFactory` type is the bridge between transports and MCP server creation:

```mermaid
graph LR
    subgraph "ServerFactory Signature"
        Inputs["headers: Record~string,string~<br/>userSettings?: AppSettings<br/>skipGradio?: boolean<br/>sessionInfo?: SessionInfo"]
        Factory["serverFactory()<br/>Async Function"]
        Output["ServerFactoryResult<br/>{server, userDetails}"]
    end
    
    Inputs --> Factory
    Factory --> Output
    
    subgraph "Factory Responsibilities"
        A["Extract auth/bouquet from headers"]
        B["Select tools via ToolSelectionStrategy"]
        C["Create McpServer instance"]
        D["Register tools and prompts"]
        E["Optionally setup Gradio proxy"]
    end
    
    Factory -.implements.- A
    Factory -.implements.- B
    Factory -.implements.- C
    Factory -.implements.- D
    Factory -.implements.- E
```

**Factory Implementation Details:**

The factory is created by the Application layer (see [MCP Server Core](#3.3)) and passed to transport constructors. It encapsulates:

1. **Authentication Extraction**: Parses `Authorization` header or `HF_TOKEN` environment variable
2. **Tool Selection**: Uses bouquet system (`x-mcp-bouquet`, `x-mcp-mix` headers) or user settings
3. **Server Instantiation**: Creates `new McpServer()` with selected tool configurations
4. **Gradio Discovery**: Conditionally fetches and registers Gradio space tools (skipped for initialize requests)
5. **Session Logging**: Logs initialize events with session info for analytics

**Sources**: [packages/app/src/server/transport/base-transport.ts:14-35](), [packages/app/src/server/transport/streamable-http-transport.ts:223-227](), [packages/app/src/server/transport/stateless-http-transport.ts:294-309]()

## Authentication Flow

```mermaid
flowchart TD
    Start["Request Received"] --> Extract["extractAuthBouquetAndMix(headers)"]
    Extract --> HasToken{"hfToken<br/>present?"}
    
    HasToken -->|No| CheckForce{"x-mcp-force-auth<br/>header?"}
    CheckForce -->|Yes| RejectAnon["Return 401<br/>trackUnauthorizedConnection()"]
    CheckForce -->|No| AllowAnon["Continue<br/>trackAnonymousConnection()"]
    
    HasToken -->|Yes| Validate["whoAmI({accessToken})"]
    Validate --> ValidResult{"Valid?"}
    
    ValidResult -->|Yes| Accept["Continue<br/>trackAuthenticatedConnection()"]
    ValidResult -->|401 Error| Reject["Return 401<br/>trackUnauthorizedConnection()"]
    ValidResult -->|Other Error| ContinueNoAuth["Continue without auth tracking<br/>Network/500 errors"]
    
    RejectAnon --> End["End Request"]
    AllowAnon --> Process["Process Request"]
    Accept --> Process
    Reject --> End
    ContinueNoAuth --> Process
    Process --> End
```

All transports use the shared `validateAuthAndTrackMetrics()` method which:

1. Extracts token from `Authorization: Bearer <token>` header or HF-specific headers
2. Calls `whoAmI()` API to validate token
3. Returns `{ shouldContinue: boolean, statusCode?: number, userIdentified: boolean }`
4. Tracks authentication state in metrics (authenticated/anonymous/unauthorized)

**Special Cases:**
- STDIO mode uses environment variable `HF_TOKEN` or `DEFAULT_HF_TOKEN`
- `x-mcp-force-auth` header forces authentication even if token is missing
- Non-401 errors (network, 500) continue processing without auth tracking

**Sources**: [packages/app/src/server/transport/base-transport.ts:301-345]()

## Stateful vs Stateless Trade-offs

| Aspect | Stateful Transports | Stateless Transport |
|--------|-------------------|-------------------|
| **Memory Usage** | One server instance per session | No persistent servers |
| **Startup Cost** | Per-session (less frequent) | Per-request (more frequent) |
| **State Management** | Complex (stale detection, ping) | Simple (no state) |
| **Session Resume** | Native support | Analytics mode only |
| **Scaling** | Limited by memory (sessions × server size) | Unlimited (no persistent state) |
| **Tool State Changes** | Notification via `tools/list` changed | Reflected on next request |
| **Analytics** | Full session tracking | Optional lightweight tracking |
| **Cleanup Complexity** | High (heartbeat, ping, timers) | Low (close after request) |

**When to Use Stateful:**
- Long-lived client connections (IDEs, desktop apps)
- Clients that benefit from persistent tool caching
- Need for real-time notifications (tool list changes)
- Moderate concurrent user count

**When to Use Stateless:**
- High-scale web applications
- Serverless deployments
- Analytics/telemetry collection
- Stateless client architecture

**Sources**: [packages/app/src/server/transport/base-transport.ts:76-78](), [packages/app/src/server/transport/stateless-http-transport.ts:32-58]()

## Transport Initialization

The Application layer selects and initializes the appropriate transport based on configuration:

```mermaid
flowchart TD
    Start["Application.start()"] --> CheckTransport{"TRANSPORT<br/>environment variable"}
    
    CheckTransport -->|stdio| CreateStdio["new StdioTransport"]
    CheckTransport -->|sse| CreateSSE["new SseTransport"]
    CheckTransport -->|streamableHttp| CheckJson{"JSON_MODE?"}
    CheckJson -->|Yes| CreateStateless["new StatelessHttpTransport"]
    CheckJson -->|No| CreateStreamable["new StreamableHttpTransport"]
    
    CreateStdio --> InitStdio["transport.initialize({port})"]
    CreateSSE --> InitSSE["transport.initialize({port})"]
    CreateStreamable --> InitStreamable["transport.initialize({port})"]
    CreateStateless --> InitStateless["transport.initialize({port})"]
    
    InitStdio --> StdioReady["Listens on stdin/stdout<br/>No HTTP server"]
    InitSSE --> SSEReady["Registers /sse and /message routes"]
    InitStreamable --> StreamableReady["Registers /mcp routes (POST/GET/DELETE)<br/>Starts stale checker + ping"]
    InitStateless --> StatelessReady["Registers /mcp route (POST only)<br/>Optional GET for welcome page"]
    
    StdioReady --> Running["Transport Running"]
    SSEReady --> Running
    StreamableReady --> Running
    StatelessReady --> Running
```

**Configuration Sources:**
1. `TRANSPORT` environment variable: `stdio`, `sse`, `streamableHttp`, `streamableHttpJson`
2. `JSON_MODE=true` with `streamableHttp` enables stateless mode
3. Docker defaults to `streamableHttpJson` mode
4. CLI tools use `stdio` mode

**Sources**: [start.sh:34-57](), [README.md:239-240](), [Dockerfile:59]()

## Method Tracking and Metrics

All transports track method calls for observability:

```mermaid
graph TB
    subgraph "Method Extraction"
        Request["JSON-RPC Request Body"] --> Extract["extractMethodForTracking()"]
        Extract --> Check{"Method type?"}
        Check -->|initialize| Name1["'initialize'"]
        Check -->|tools/call| GetTool["Extract tool name<br/>from params.name"]
        GetTool --> SafeName["getMetricsSafeName()<br/>Handle Gradio prefixes"]
        SafeName --> Name2["'tools/call:model_search'"]
        Check -->|prompts/get| GetPrompt["Extract prompt name"]
        GetPrompt --> Name3["'prompts/get:user_summary'"]
        Check -->|Other| Name4["method name as-is"]
    end
    
    subgraph "Metrics Tracking"
        Name1 --> Track["metrics.trackMethod()"]
        Name2 --> Track
        Name3 --> Track
        Name4 --> Track
        
        Track --> Record["Record in TransportMetrics"]
        Record --> Store1["methodCalls: Map~string,number~"]
        Record --> Store2["methodErrors: Map~string,number~"]
        Record --> Store3["methodDurations: Map~string,number[]~"]
        Record --> Store4["clientMethods: Map~string,Map~string,number~~"]
    end
```

**Metric Dimensions:**
- **Method Name**: Extracted method (e.g., `tools/call:model_search`)
- **Duration**: Time from request start to completion (stateless only)
- **Error Status**: Success or failure boolean
- **Client Info**: Associated client name/version if available

**Special Handling:**
- Gradio tools get sanitized names via `getMetricsSafeName()` to handle special characters
- Responses (JSON-RPC with `id` but no `method`) are not tracked
- Notifications are tracked but marked differently

**Sources**: [packages/app/src/server/transport/base-transport.ts:188-223](), [packages/app/src/server/transport/base-transport.ts:269-280]()

## Gradio Setup Optimization

Transports optimize Gradio endpoint discovery by conditionally skipping it:

```mermaid
flowchart TD
    Start["Request arrives"] --> ExtractMethod["Extract method from body"]
    ExtractMethod --> CheckMethod{"Method type?"}
    
    CheckMethod -->|initialize| Skip1["skipGradio = true<br/>Don't fetch Gradio schemas"]
    CheckMethod -->|resources/*| Skip2["skipGradio = true<br/>Only for openai-mcp client"]
    CheckMethod -->|tools/call| CheckToolName{"Tool name<br/>starts with 'gr'?"}
    
    CheckToolName -->|Yes| NoSkip["skipGradio = false<br/>Fetch Gradio schemas"]
    CheckToolName -->|No| Skip3["skipGradio = true<br/>Not a Gradio tool"]
    
    CheckMethod -->|Other| NoSkip
    
    Skip1 --> Factory["serverFactory(headers, settings, skipGradio)"]
    Skip2 --> Factory
    Skip3 --> Factory
    NoSkip --> Factory
    
    Factory --> Decision{"skipGradio?"}
    Decision -->|true| CreateFast["Create server without Gradio discovery<br/>Faster initialization"]
    Decision -->|false| CreateFull["Create server with Gradio discovery<br/>Full tool set"]
```

This optimization significantly improves initialization performance by avoiding unnecessary Gradio API calls when:
- Client is establishing initial connection (initialize request)
- Client is only using built-in tools (non-Gradio tool calls)
- Client is requesting resources (for OpenAI MCP client only)

**Sources**: [packages/app/src/server/transport/base-transport.ts:228-267](), [packages/app/src/server/transport/stateless-http-transport.ts:290-299]()

## Error Handling and JSON-RPC Errors

All transports use standardized JSON-RPC error responses:

| Error Type | Method | Status Code | Use Case |
|-----------|---------|-------------|----------|
| Invalid Request | `JsonRpcErrors.invalidRequest()` | 400 | Malformed request body |
| Invalid Params | `JsonRpcErrors.invalidParams()` | 400 | Missing required parameter |
| Session Not Found | `JsonRpcErrors.sessionNotFound()` | 404 | Invalid session ID |
| Method Not Allowed | `JsonRpcErrors.methodNotAllowed()` | 405 | Wrong HTTP verb |
| Internal Error | `JsonRpcErrors.internalError()` | 500 | Unexpected error |
| Server Shutting Down | `JsonRpcErrors.serverShuttingDown()` | 503 | Graceful shutdown |

All error responses include:
- `jsonrpc: "2.0"` field
- `error` object with `code`, `message`, and optional `data`
- Request `id` for correlation (extracted via `extractJsonRpcId()`)

**Error Tracking:**
Each transport calls `trackError(statusCode?, error?)` which records:
- Total error count
- Errors by status code
- Error details in metrics

**Sources**: [packages/app/src/server/transport/json-rpc-errors.ts:1-100]() (not provided but referenced), [packages/app/src/server/transport/streamable-http-transport.ts:86-88](), [packages/app/src/server/transport/stateless-http-transport.ts:404-406]()

## Session Cleanup and Lifecycle

Stateful transports implement comprehensive cleanup:

```mermaid
flowchart TD
    Start["Session Created"] --> Active["Active State<br/>Handling requests"]
    
    Active --> Trigger{"Cleanup trigger?"}
    
    Trigger -->|Stale timeout| Stale["staleCheckInterval timer<br/>lastActivity > STALE_TIMEOUT"]
    Trigger -->|Client disconnect| Disconnect["SSE 'close' event<br/>or heartbeat detects destroyed"]
    Trigger -->|Explicit close| Explicit["DELETE request"]
    Trigger -->|Server shutdown| Shutdown["Application.stop()"]
    
    Stale --> CheckFlag{"cleaningUp flag?"}
    Disconnect --> CheckFlag
    Explicit --> CheckFlag
    Shutdown --> CheckFlag
    
    CheckFlag -->|true| Skip["Skip cleanup<br/>Already in progress"]
    CheckFlag -->|false| SetFlag["Set cleaningUp = true"]
    
    SetFlag --> StopHeart["Stop heartbeat timer<br/>clearInterval()"]
    StopHeart --> CloseTransport["transport.close()<br/>Close SSE stream"]
    CloseTransport --> CloseServer["server.close()<br/>Disconnect MCP"]
    CloseServer --> RemoveMap["sessions.delete(sessionId)"]
    RemoveMap --> TrackMetrics["trackSessionCleaned()<br/>trackSessionDeleted()"]
    TrackMetrics --> DisconnectClient["metrics.disconnectClient()"]
    DisconnectClient --> Complete["Cleanup Complete"]
    
    Skip --> Complete
```

**Cleanup Sources:**
1. **Stale Timeout**: `startStaleConnectionCheck()` timer scans sessions every `STALE_CHECK_INTERVAL`
2. **Heartbeat Detection**: SSE response stream monitoring detects destroyed/ended connections
3. **Client Disconnect**: SSE 'close' event or transport.onclose callback
4. **Explicit Close**: DELETE request from client
5. **Graceful Shutdown**: Application calls `transport.cleanup()` which cleans all sessions

**Cleanup Guarantees:**
- `cleaningUp` flag prevents recursive cleanup
- Errors during cleanup are caught and logged but don't prevent removal from map
- Metrics are always updated even if transport/server close fails
- Client info is disconnected from metrics to update active client counts

**Sources**: [packages/app/src/server/transport/base-transport.ts:681-724](), [packages/app/src/server/transport/base-transport.ts:726-740](), [packages/app/src/server/transport/streamable-http-transport.ts:290-303]()

---

# Page: Tools and Prompts

# Tools and Prompts

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [packages/app/src/server/mcp-server.ts](packages/app/src/server/mcp-server.ts)
- [packages/app/src/shared/settings.ts](packages/app/src/shared/settings.ts)
- [packages/app/src/web/App.tsx](packages/app/src/web/App.tsx)
- [packages/mcp/src/index.ts](packages/mcp/src/index.ts)
- [packages/mcp/src/tool-ids.ts](packages/mcp/src/tool-ids.ts)

</details>



This document describes the tools and prompts available in the Hugging Face MCP Server. It covers the tool architecture, configuration patterns, registration process, and the complete catalog of built-in tools and prompts.

For information about how tools are selected and filtered for clients, see [Tool Selection System](#5). For details about dynamically-discovered Gradio tools, see [Gradio Integration](#6).

## Overview

The HF MCP Server provides two types of capabilities to connected clients:

**Tools** are callable functions that perform operations against the Hugging Face ecosystem. The server includes 15 built-in tools covering search, detail retrieval, space management, documentation access, and job management. Additionally, Gradio-based tools can be dynamically registered (covered in [Gradio Integration](#6)).

**Prompts** are pre-configured message templates that fetch and format data for insertion into AI assistant conversations. The server includes 4 prompts for summarizing users, papers, models, and datasets.

All tools and prompts follow a consistent configuration pattern using Zod schemas for parameter validation and type safety.

Sources: [packages/app/src/server/mcp-server.ts:1-896](), [packages/mcp/src/tool-ids.ts:1-105]()

## Tool Architecture

### Tool Configuration Structure

Every tool in the system follows a standardized configuration pattern. Each tool has a configuration object (`*_TOOL_CONFIG`) that defines its metadata and behavior.

```mermaid
graph TB
    subgraph "Tool Configuration Object"
        Config["TOOL_CONFIG"]
        Name["name: string<br/>(Tool ID)"]
        Desc["description: string<br/>(Tool Purpose)"]
        Schema["schema: ZodObject<br/>(Parameter Schema)"]
        Annotations["annotations: object<br/>(MCP Metadata)"]
    end
    
    subgraph "Zod Schema (Validation)"
        ZodSchema["z.object({...})"]
        Params["Parameter Definitions"]
        Validation["Runtime Validation"]
    end
    
    subgraph "Annotations (MCP Protocol)"
        Title["title: string"]
        ReadOnly["readOnlyHint: boolean"]
        OpenWorld["openWorldHint: boolean"]
    end
    
    subgraph "Tool Implementation"
        ToolClass["Tool Class<br/>(e.g., ModelSearchTool)"]
        Handler["Handler Function<br/>(async execution)"]
        Result["ToolResult<br/>(formatted response)"]
    end
    
    Config --> Name
    Config --> Desc
    Config --> Schema
    Config --> Annotations
    
    Schema --> ZodSchema
    ZodSchema --> Params
    ZodSchema --> Validation
    
    Annotations --> Title
    Annotations --> ReadOnly
    Annotations --> OpenWorld
    
    Config -.."used by"..- ToolClass
    ToolClass --> Handler
    Handler --> Result
```

**Tool Configuration Example Structure**

| Component | Purpose | Example |
|-----------|---------|---------|
| `name` | Unique tool identifier | `"model_search"` |
| `description` | Human-readable tool purpose | `"Search for models on Hugging Face Hub"` |
| `schema` | Zod schema for parameter validation | `z.object({ query: z.string() })` |
| `annotations.title` | Display name for UIs | `"Model Search"` |
| `annotations.readOnlyHint` | Whether tool modifies state | `true` |
| `annotations.openWorldHint` | Whether results are comprehensive | `false` |

Sources: [packages/app/src/server/mcp-server.ts:6-63](), [packages/mcp/src/tool-ids.ts:6-26]()

### Tool Registration Flow

Tools are registered with the MCP server during server instantiation using the `server.tool()` method from the `@modelcontextprotocol/sdk`.

```mermaid
sequenceDiagram
    participant Factory as createServerFactory
    participant Server as McpServer
    participant ToolInstance as Tool Instance
    participant ToolImpl as Tool Implementation
    
    Factory->>Server: new McpServer(info, instructions)
    
    rect rgb(250, 250, 250)
        Note over Factory,ToolImpl: Registration Phase
        
        Factory->>Server: server.tool(name, desc, schema, annotations, handler)
        Server->>ToolInstance: Create tool instance with enable/disable methods
        Server-->>Factory: Return tool instance
        Factory->>Factory: Store in toolInstances map
        
        Factory->>Server: server.tool(...) [repeat for all tools]
        Server->>ToolInstance: Create tool instances
        Server-->>Factory: Return instances
    end
    
    rect rgb(250, 250, 250)
        Note over Factory,ToolImpl: Invocation Phase
        
        Server->>ToolInstance: Client calls tool
        ToolInstance->>ToolImpl: Execute handler function
        ToolImpl->>ToolImpl: Validate params with Zod schema
        ToolImpl->>ToolImpl: Perform operation (API call, etc.)
        ToolImpl-->>ToolInstance: Return ToolResult
        ToolInstance-->>Server: Format as CallToolResult
        Server-->>Factory: Return to client
    end
```

The registration creates a `toolInstances` map that stores references to each registered tool, allowing dynamic enable/disable control:

```typescript
const toolInstances: { [name: string]: Tool } = {};

toolInstances[MODEL_SEARCH_TOOL_CONFIG.name] = server.tool(
  MODEL_SEARCH_TOOL_CONFIG.name,
  MODEL_SEARCH_TOOL_CONFIG.description,
  MODEL_SEARCH_TOOL_CONFIG.schema.shape,
  MODEL_SEARCH_TOOL_CONFIG.annotations,
  async (params: ModelSearchParams) => { /* handler */ }
);
```

Sources: [packages/app/src/server/mcp-server.ts:151-896](), [packages/app/src/server/mcp-server.ts:383-406]()

## Built-in Tools

The server provides 15 built-in tools organized into functional categories. Each tool is implemented as a class in `packages/mcp/src/` and registered in the server factory.

### Tool Categories and Groups

Tools are organized into logical groups defined in `TOOL_ID_GROUPS`:

```mermaid
graph TB
    subgraph "TOOL_ID_GROUPS"
        All["all<br/>(15 tools)"]
        
        Search["search<br/>(5 tools)"]
        Spaces["spaces<br/>(5 tools)"]
        Detail["detail<br/>(3 tools)"]
        Docs["docs<br/>(2 tools)"]
        HfApi["hf_api<br/>(7 tools)"]
    end
    
    subgraph "Search Tools"
        SpaceSearch["space_semantic_search"]
        ModelSearch["model_search"]
        DatasetSearch["dataset_search"]
        PaperSearch["paper_search"]
        DocSearch["hf_doc_search"]
    end
    
    subgraph "Space Management Tools"
        SpaceSearchDup["space_semantic_search"]
        DuplicateSpace["duplicate_space"]
        SpaceInfo["space_info"]
        SpaceFiles["space_files"]
        UseSpace["use_space"]
    end
    
    subgraph "Detail Tools"
        ModelDetail["model_detail"]
        DatasetDetail["dataset_detail"]
        HubInspect["hub_repo_details"]
    end
    
    subgraph "Documentation Tools"
        DocSearchDup["hf_doc_search"]
        DocFetch["hf_doc_fetch"]
    end
    
    Search --> SpaceSearch
    Search --> ModelSearch
    Search --> DatasetSearch
    Search --> PaperSearch
    Search --> DocSearch
    
    Spaces --> SpaceSearchDup
    Spaces --> DuplicateSpace
    Spaces --> SpaceInfo
    Spaces --> SpaceFiles
    Spaces --> UseSpace
    
    Detail --> ModelDetail
    Detail --> DatasetDetail
    Detail --> HubInspect
    
    Docs --> DocSearchDup
    Docs --> DocFetch
    
    HfApi --> SpaceSearch
    HfApi --> ModelSearch
    HfApi --> DatasetSearch
    HfApi --> PaperSearch
    HfApi --> HubInspect
    HfApi --> DocSearch
    
    All --> Search
    All --> Spaces
    All --> Detail
    All --> Docs
```

Sources: [packages/mcp/src/tool-ids.ts:67-96]()

### Complete Tool Catalog

| Tool ID | Tool Class | Config | Registration | Purpose |
|---------|-----------|--------|--------------|---------|
| `hf_whoami` | N/A (inline) | N/A | [mcp-server.ts:198-206]() | Display authentication status |
| `space_semantic_search` | `SpaceSearchTool` | `SEMANTIC_SEARCH_TOOL_CONFIG` | [mcp-server.ts:357-381]() | Semantic search across HF Spaces |
| `model_search` | `ModelSearchTool` | `MODEL_SEARCH_TOOL_CONFIG` | [mcp-server.ts:383-406]() | Search models with filters |
| `model_detail` | `ModelDetailTool` | `MODEL_DETAIL_TOOL_CONFIG` | [mcp-server.ts:408-431]() | Get comprehensive model information |
| `paper_search` | `PaperSearchTool` | `PAPER_SEARCH_TOOL_CONFIG` | [mcp-server.ts:433-459]() | Search academic papers on HF Hub |
| `dataset_search` | `DatasetSearchTool` | `DATASET_SEARCH_TOOL_CONFIG` | [mcp-server.ts:461-484]() | Search datasets with filters |
| `dataset_detail` | `DatasetDetailTool` | `DATASET_DETAIL_TOOL_CONFIG` | [mcp-server.ts:486-509]() | Get comprehensive dataset information |
| `hub_repo_details` | `HubInspectTool` | `HUB_INSPECT_TOOL_CONFIG` | [mcp-server.ts:524-561]() | Inspect repository structure and files |
| `hf_doc_search` | `DocSearchTool` | `DOCS_SEMANTIC_SEARCH_CONFIG` | [mcp-server.ts:563-586]() | Semantic search HF documentation |
| `hf_doc_fetch` | `DocFetchTool` | `DOC_FETCH_CONFIG` | [mcp-server.ts:588-600]() | Fetch and convert documentation pages |
| `duplicate_space` | `DuplicateSpaceTool` | `DUPLICATE_SPACE_TOOL_CONFIG` | [mcp-server.ts:602-615]() | Duplicate a Space to user's account |
| `space_info` | `SpaceInfoTool` | `SPACE_INFO_TOOL_CONFIG` | [mcp-server.ts:617-630]() | Get Space metadata and runtime info |
| `space_files` | `SpaceFilesTool` | `SPACE_FILES_TOOL_CONFIG` | [mcp-server.ts:632-645]() | List files in a Space repository |
| `use_space` | `UseSpaceTool` | `USE_SPACE_TOOL_CONFIG` | [mcp-server.ts:647-670]() | View or invoke Gradio Space endpoints |
| `hf_jobs` | `HfJobsTool` | `HF_JOBS_TOOL_CONFIG` | [mcp-server.ts:672-697]() | Manage training/inference jobs |
| `use-space` (dynamic) | `SpaceTool` | `DYNAMIC_SPACE_TOOL_CONFIG` | [mcp-server.ts:699-815]() | Dynamic Space invocation with operations |

Sources: [packages/app/src/server/mcp-server.ts:198-815](), [packages/mcp/src/tool-ids.ts:28-47]()

### Authentication Tool

The `hf_whoami` tool is always enabled and provides authentication guidance:

- **Authenticated users**: Displays username
- **Unauthenticated users**: Returns configuration guidance from `CONFIG_GUIDANCE`

An optional `Authenticate` tool can be enabled via `AUTHENTICATE_TOOL=true` environment variable for certain client workflows.

Sources: [packages/app/src/server/mcp-server.ts:193-219]()

### Tool Implementation Pattern

Most tools follow a consistent implementation pattern:

```mermaid
graph LR
    subgraph "Tool Implementation Classes"
        HfApiCall["HfApiCall<br/>(Base Class)"]
        ModelSearchTool["ModelSearchTool"]
        DatasetSearchTool["DatasetSearchTool"]
        ModelDetailTool["ModelDetailTool"]
        DocSearchTool["DocSearchTool"]
    end
    
    subgraph "Shared Functionality"
        Auth["credentials<br/>(HF token)"]
        ErrorHandling["handleError()"]
        Formatting["Format utilities"]
    end
    
    subgraph "External APIs"
        HubAPI["@huggingface/hub API"]
        DocsAPI["HF Docs API"]
    end
    
    HfApiCall --> Auth
    HfApiCall --> ErrorHandling
    HfApiCall --> Formatting
    
    ModelSearchTool -.inherits.- HfApiCall
    DatasetSearchTool -.inherits.- HfApiCall
    ModelDetailTool -.inherits.- HfApiCall
    DocSearchTool -.inherits.- HfApiCall
    
    ModelSearchTool --> HubAPI
    DatasetSearchTool --> HubAPI
    ModelDetailTool --> HubAPI
    DocSearchTool --> DocsAPI
```

Each tool class:
1. Extends `HfApiCall` base class (for most tools)
2. Accepts `hfToken` for authentication
3. Implements a main execution method (e.g., `search()`, `getDetails()`)
4. Returns a `ToolResult` object with `{ formatted, totalResults, resultsShared }`

Sources: [packages/mcp/src/hf-api-call.ts:1-100]() (inferred), [packages/app/src/server/mcp-server.ts:383-509]()

## Prompts

The server provides 4 prompts that fetch and format data for AI assistant conversations. Prompts are registered using `server.prompt()` and return message objects with pre-formatted content.

### Prompt Catalog

| Prompt ID | Prompt Class | Config | Registration | Purpose |
|-----------|-------------|--------|--------------|---------|
| `user_summary` | `UserSummaryPrompt` | `USER_SUMMARY_PROMPT_CONFIG` | [mcp-server.ts:221-253]() | Summarize user's HF contributions |
| `paper_summary` | `PaperSummaryPrompt` | `PAPER_SUMMARY_PROMPT_CONFIG` | [mcp-server.ts:255-287]() | Summarize academic paper details |
| `model_detail_prompt` | `ModelDetailTool` | `MODEL_DETAIL_PROMPT_CONFIG` | [mcp-server.ts:289-321]() | Model details formatted for prompts |
| `dataset_detail_prompt` | `DatasetDetailTool` | `DATASET_DETAIL_PROMPT_CONFIG` | [mcp-server.ts:323-355]() | Dataset details formatted for prompts |

### Prompt Structure

Prompts follow the MCP protocol's message format:

```typescript
{
  description: "User summary for username",
  messages: [
    {
      role: "user",
      content: {
        type: "text",
        text: "formatted summary content"
      }
    }
  ]
}
```

Prompts differ from tools in that they:
- Return pre-formatted messages ready for conversation insertion
- Always use `role: "user"` to inject context into the conversation
- Typically aggregate multiple API calls into a single coherent summary
- Have logging that tracks `responseCharCount` instead of raw API metrics

Sources: [packages/app/src/server/mcp-server.ts:221-355](), [packages/mcp/src/user-summary.ts:1-100]() (inferred)

## Tool Configuration Pattern

### Configuration Object Structure

Each tool exports a configuration object with the following structure:

```mermaid
graph TB
    subgraph "Example: MODEL_SEARCH_TOOL_CONFIG"
        Config["Configuration Object"]
        
        NameField["name: 'model_search'"]
        DescField["description: 'Search for models...'"]
        SchemaField["schema: z.object({...})"]
        AnnotField["annotations: {...}"]
    end
    
    subgraph "schema (Zod Validation)"
        ZodObj["z.object({"])
        QueryParam["query: z.string().optional()"]
        LimitParam["limit: z.number().optional()"]
        SortParam["sort: z.enum([...]).optional()"]
        TagsParam["tags: z.array(...).optional()"]
        ZodClose["})"]
    end
    
    subgraph "annotations (MCP Metadata)"
        TitleAnn["title: 'Model Search'"]
        ReadOnlyAnn["readOnlyHint: true"]
        OpenWorldAnn["openWorldHint: false"]
    end
    
    Config --> NameField
    Config --> DescField
    Config --> SchemaField
    Config --> AnnotField
    
    SchemaField --> ZodObj
    ZodObj --> QueryParam
    ZodObj --> LimitParam
    ZodObj --> SortParam
    ZodObj --> TagsParam
    ZodObj --> ZodClose
    
    AnnotField --> TitleAnn
    AnnotField --> ReadOnlyAnn
    AnnotField --> OpenWorldAnn
```

### Parameter Schema Validation

All tool parameters are validated using Zod schemas. When a tool is invoked:

1. The MCP SDK automatically validates parameters against `schema.shape`
2. Invalid parameters result in immediate error responses
3. Valid parameters are passed to the handler function with TypeScript type safety

Example parameter types:

```typescript
// ModelSearchParams (inferred from schema)
type ModelSearchParams = {
  query?: string;
  limit?: number;
  sort?: "trendingScore" | "downloads" | "likes";
  tags?: string[];
  // ... additional parameters
}
```

Sources: [packages/app/src/server/mcp-server.ts:12-13](), [packages/mcp/src/model-search.ts:1-100]() (inferred)

### Annotations and Hints

The `annotations` field provides MCP protocol metadata:

| Annotation | Type | Purpose |
|------------|------|---------|
| `title` | `string` | Human-readable display name |
| `readOnlyHint` | `boolean` | Indicates if tool modifies state (false = writes data) |
| `openWorldHint` | `boolean` | Indicates if results are comprehensive (false = filtered/limited) |

These hints allow MCP clients to make informed decisions about tool usage and caching.

Sources: [packages/app/src/server/mcp-server.ts:202](), [packages/app/src/server/mcp-server.ts:360-361]()

## Tool Registration Process

### Server Factory Pattern

The `createServerFactory` function returns a factory that creates configured `McpServer` instances:

```mermaid
graph TB
    subgraph "createServerFactory"
        Factory["Factory Function"]
        Params["Parameters:<br/>headers, userSettings,<br/>skipGradio, sessionInfo"]
    end
    
    subgraph "Server Creation"
        ExtractAuth["extractAuthBouquetAndMix()<br/>(Get HF token)"]
        Authenticate["whoAmI()<br/>(Validate token)"]
        NewServer["new McpServer()<br/>(Create instance)"]
    end
    
    subgraph "Tool Registration Loop"
        RegisterTool1["server.tool(hf_whoami, ...)"]
        RegisterTool2["server.tool(space_semantic_search, ...)"]
        RegisterToolN["server.tool(...) x 15"]
        StoreInstance["Store in toolInstances map"]
    end
    
    subgraph "Prompt Registration Loop"
        RegisterPrompt1["server.prompt(user_summary, ...)"]
        RegisterPrompt2["server.prompt(paper_summary, ...)"]
        RegisterPromptN["server.prompt(...) x 4"]
    end
    
    subgraph "Tool State Management"
        ApplyState["applyToolStates()<br/>(Enable/disable based on selection)"]
        EventListener["Set up toolStateChange listener"]
    end
    
    subgraph "Result"
        ServerResult["Return { server, userDetails }"]
    end
    
    Factory --> Params
    Params --> ExtractAuth
    ExtractAuth --> Authenticate
    Authenticate --> NewServer
    NewServer --> RegisterTool1
    RegisterTool1 --> RegisterTool2
    RegisterTool2 --> RegisterToolN
    RegisterToolN --> StoreInstance
    StoreInstance --> RegisterPrompt1
    RegisterPrompt1 --> RegisterPrompt2
    RegisterPrompt2 --> RegisterPromptN
    RegisterPromptN --> ApplyState
    ApplyState --> EventListener
    EventListener --> ServerResult
```

The factory is invoked by transport implementations whenever a new server instance is needed:
- **STDIO transport**: Once at startup
- **Stateful transports (SSE, HTTP)**: Once per session
- **Stateless transport**: Once per request

Sources: [packages/app/src/server/mcp-server.ts:96-896]()

### Tool Instance Storage

The `toolInstances` map stores references to all registered tools:

```typescript
const toolInstances: { [name: string]: Tool } = {};
```

Each entry has `enable()` and `disable()` methods that control tool visibility. This allows dynamic tool management based on:
- Tool selection strategy results
- User settings changes (via `toolStateChange` events)
- Runtime configuration flags

Sources: [packages/app/src/server/mcp-server.ts:174-191](), [packages/app/src/server/mcp-server.ts:839-893]()

### Dynamic Tool State Management

After registration, tool states are applied:

```typescript
const applyToolStates = async () => {
  // Apply the desired state to each tool
  for (const [toolName, toolInstance] of Object.entries(toolInstances)) {
    if (toolSelection.enabledToolIds.includes(toolName)) {
      toolInstance.enable();
    } else {
      toolInstance.disable();
    }
  }
};
```

For stateful transports, an event listener updates tool states dynamically:

```typescript
sharedApiClient.on('toolStateChange', (toolId: string, enabled: boolean) => {
  const toolInstance = toolInstances[toolId];
  if (toolInstance) {
    if (enabled) {
      toolInstance.enable();
    } else {
      toolInstance.disable();
    }
  }
});
```

This allows the web UI to toggle tools without requiring client reconnection.

Sources: [packages/app/src/server/mcp-server.ts:839-893]()

## Tool Invocation Lifecycle

When a client calls a tool, the following sequence occurs:

```mermaid
sequenceDiagram
    participant Client
    participant Transport
    participant McpServer
    participant Handler
    participant ToolImpl
    participant HfAPI
    
    Client->>Transport: tools/call request<br/>{name: "model_search", arguments: {...}}
    Transport->>McpServer: Route to tool handler
    McpServer->>McpServer: Validate params with Zod schema
    
    alt Validation Fails
        McpServer-->>Transport: Error response
        Transport-->>Client: Validation error
    else Validation Succeeds
        McpServer->>Handler: Call handler function<br/>(params: ModelSearchParams)
        Handler->>ToolImpl: new ModelSearchTool(hfToken)
        Handler->>ToolImpl: searchWithParams(params)
        ToolImpl->>HfAPI: API call (listModels, etc.)
        HfAPI-->>ToolImpl: Raw API response
        ToolImpl->>ToolImpl: Format as ToolResult<br/>{formatted, totalResults, resultsShared}
        ToolImpl-->>Handler: Return ToolResult
        Handler->>Handler: logSearchQuery()<br/>(Record metrics)
        Handler->>Handler: Wrap as CallToolResult<br/>{content: [{type: "text", text: ...}]}
        Handler-->>McpServer: Return result
        McpServer-->>Transport: JSON-RPC response
        Transport-->>Client: Tool result
    end
```

### Handler Function Pattern

Each tool handler follows this pattern:

1. **Instantiate tool class** with authentication token
2. **Execute operation** (search, fetch, etc.)
3. **Format result** as `ToolResult`
4. **Log query** with metrics
5. **Return** as `CallToolResult` with text content

Example handler structure:

```typescript
async (params: ModelSearchParams) => {
  const modelSearch = new ModelSearchTool(hfToken);
  const result = await modelSearch.searchWithParams(params);
  
  logSearchQuery(
    MODEL_SEARCH_TOOL_CONFIG.name,
    params.query || `sort:${params.sort}`,
    params,
    { ...loggingOptions, ...result }
  );
  
  return {
    content: [{ type: 'text', text: result.formatted }]
  };
}
```

Sources: [packages/app/src/server/mcp-server.ts:383-406]()

### Result Format

Tools return `CallToolResult` objects with:

```typescript
{
  content: [
    {
      type: "text",
      text: "formatted result string"
    }
  ],
  isError?: boolean  // Optional error flag
}
```

The `formatted` text is typically a human-readable markdown string summarizing the operation results.

Sources: [packages/app/src/server/mcp-server.ts:378-379](), [packages/app/src/server/mcp-server.ts:402-405]()

## Special Tool Behaviors

### Dynamic Schema Modification

The `hub_repo_details` tool conditionally modifies its schema based on the `README_INCLUDE_FLAG`:

```typescript
const hubInspectReadmeAllowed = hasReadmeFlag(toolSelection.enabledToolIds);
const hubInspectDescription = hubInspectReadmeAllowed
  ? `${HUB_INSPECT_TOOL_CONFIG.description} README file may be requested...`
  : HUB_INSPECT_TOOL_CONFIG.description;

const hubInspectSchemaShape = hubInspectReadmeAllowed
  ? hubInspectBaseShape
  : omitReadmeParameter(hubInspectBaseShape);
```

When the flag is disabled, the `include_readme` parameter is removed from the schema, preventing clients from requesting README content.

Sources: [packages/app/src/server/mcp-server.ts:512-523]()

### Runtime Feature Flags

The `use-space` dynamic tool checks the `gradio=none` header to disable invoke operations:

```typescript
if (params.operation === 'invoke' && gradio === 'none') {
  return {
    content: [{ type: 'text', text: 'The invoke operation is disabled...' }],
    isError: true,
  };
}
```

This allows fine-grained control over Gradio functionality without changing tool registration.

Sources: [packages/app/src/server/mcp-server.ts:706-716]()

### Logging and Metrics

All tool invocations are logged with:
- Tool name and query/operation
- Input parameters (sanitized)
- Session information (client ID, auth status, client name/version)
- Result metrics (total results, results shared, response character count)

Different logging functions are used based on tool type:
- `logSearchQuery()` for search tools
- `logPromptQuery()` for prompts and detail tools
- `logGradioEvent()` for Gradio tool invocations

Sources: [packages/app/src/server/mcp-server.ts:69](), [packages/app/src/server/mcp-server.ts:366-376]()

---

# Page: Tool System Overview

# Tool System Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [packages/app/src/server/mcp-server.ts](packages/app/src/server/mcp-server.ts)
- [packages/app/src/shared/settings.ts](packages/app/src/shared/settings.ts)
- [packages/app/src/web/App.tsx](packages/app/src/web/App.tsx)
- [packages/mcp/src/index.ts](packages/mcp/src/index.ts)
- [packages/mcp/src/tool-ids.ts](packages/mcp/src/tool-ids.ts)

</details>



## Purpose and Scope

This page explains the tool system architecture in the Hugging Face MCP Server, covering how tools are defined, registered, validated, and invoked. It focuses on the configuration pattern, schema validation with Zod, and the tool execution lifecycle.

For information about specific built-in tools and their functionality, see [Built-in Tools](#4.2). For details on how tools are selected and filtered for clients, see [Tool Selection System](#5). For Gradio-specific tool mechanics, see [Gradio Integration](#6).

---

## Tool Configuration Pattern

Tools in this system follow a standardized configuration pattern where each tool is defined by a configuration object containing metadata and behavior specifications. This pattern ensures consistency across all tool implementations and provides the MCP Server with the information needed to register and expose tools to clients.

### Configuration Structure

Each tool configuration object includes four key components:

| Component | Type | Purpose |
|-----------|------|---------|
| `name` | `string` | Unique identifier for the tool (e.g., `"model_search"`) |
| `description` | `string` | Human-readable explanation of the tool's purpose |
| `schema` | `z.ZodObject` | Zod schema defining input parameters and validation rules |
| `annotations` | `object` | Metadata including `title`, `readOnlyHint`, `openWorldHint` |

**Example Tool Configuration Structure**

```mermaid
graph TB
    subgraph "Tool Configuration Object"
        Config["ToolConfig"]
        Name["name: string<br/>'model_search'"]
        Desc["description: string<br/>'Search models on HF Hub...'"]
        Schema["schema: z.ZodObject<br/>Parameter definitions"]
        Annot["annotations: object<br/>title, hints, etc."]
    end
    
    Config --> Name
    Config --> Desc
    Config --> Schema
    Config --> Annot
    
    subgraph "Zod Schema Shape"
        SchemaShape["schema.shape"]
        Param1["query: z.string().optional()"]
        Param2["limit: z.number().default(10)"]
        Param3["sort: z.enum([...])"]
    end
    
    Schema --> SchemaShape
    SchemaShape --> Param1
    SchemaShape --> Param2
    SchemaShape --> Param3
```

**Sources:** [packages/mcp/src/model-search.ts](), [packages/mcp/src/tool-ids.ts:6-26](), [packages/app/src/server/mcp-server.ts:383-406]()

### Configuration Constants

Tool configurations are exported as constants from the `@llmindset/hf-mcp` package, providing a single source of truth for tool definitions. These constants are imported and used during server initialization.

Examples from the codebase:
- `MODEL_SEARCH_TOOL_CONFIG` - Configuration for model search tool
- `DATASET_SEARCH_TOOL_CONFIG` - Configuration for dataset search tool
- `SEMANTIC_SEARCH_TOOL_CONFIG` - Configuration for space semantic search
- `DOC_FETCH_CONFIG` - Configuration for documentation fetch tool

**Sources:** [packages/app/src/server/mcp-server.ts:6-63](), [packages/mcp/src/tool-ids.ts:6-26]()

---

## Schema Validation with Zod

The system uses [Zod](https://github.com/colinhacks/zod) for runtime schema validation and TypeScript type inference. Each tool's input parameters are validated against a Zod schema before execution, ensuring type safety and providing automatic error messages for invalid inputs.

### Schema Definition Pattern

Tools define their schemas using Zod's schema builders, which provide both validation logic and TypeScript type information:

```typescript
// Example pattern (not actual code, for illustration)
const schema = z.object({
  query: z.string().describe("Search query text"),
  limit: z.number().min(1).max(100).default(10),
  sort: z.enum(["trending", "likes", "downloads"]).optional()
})
```

### Type Inference

Zod schemas enable automatic TypeScript type inference for tool parameters. The `z.infer<typeof schema>` utility extracts the TypeScript type from the schema, ensuring that tool handlers receive correctly typed parameters.

**Tool Parameter Type Flow**

```mermaid
graph LR
    subgraph "Schema Definition"
        ZodSchema["z.object({ ... })<br/>Zod Schema"]
    end
    
    subgraph "Type Inference"
        InferType["z.infer<typeof schema><br/>TypeScript Type"]
    end
    
    subgraph "Tool Handler"
        Params["params: ModelSearchParams"]
        Handler["async (params) => {...}"]
    end
    
    subgraph "Runtime Validation"
        Validate["MCP SDK validates<br/>against schema.shape"]
        Error["ValidationError<br/>if invalid"]
    end
    
    ZodSchema --> InferType
    InferType --> Params
    Params --> Handler
    ZodSchema --> Validate
    Validate --> Handler
    Validate --> Error
```

**Sources:** [packages/app/src/server/mcp-server.ts:383-406](), [packages/mcp/src/model-search.ts]()

### Schema Shape for Registration

During tool registration, the MCP SDK requires the schema's `shape` property rather than the full Zod schema object. The shape is accessed via `schema.shape` and contains the raw Zod type definitions:

```typescript
// Registration pattern used in mcp-server.ts
server.tool(
  MODEL_SEARCH_TOOL_CONFIG.name,
  MODEL_SEARCH_TOOL_CONFIG.description,
  MODEL_SEARCH_TOOL_CONFIG.schema.shape,  // ← .shape property
  MODEL_SEARCH_TOOL_CONFIG.annotations,
  async (params: ModelSearchParams) => { /* ... */ }
)
```

**Sources:** [packages/app/src/server/mcp-server.ts:383-387]()

---

## Tool Registration and State Management

Tools are registered to `McpServer` instances during server creation. Each tool can be dynamically enabled or disabled without server restart, allowing runtime control over tool availability.

### Registration Process

The `createServerFactory` function creates new `McpServer` instances and registers all tools. Registration happens in [packages/app/src/server/mcp-server.ts:96-896]() and follows this pattern:

1. Create `McpServer` instance with server metadata
2. For each tool, call `server.tool()` with configuration and handler
3. Store returned tool instance in `toolInstances` map
4. Apply tool selection strategy to enable/disable tools

**Tool Registration Flow**

```mermaid
sequenceDiagram
    participant Factory as createServerFactory
    participant Strategy as ToolSelectionStrategy
    participant Server as McpServer
    participant Registry as toolInstances
    
    Factory->>Server: new McpServer(metadata)
    
    loop For each tool config
        Factory->>Server: server.tool(name, desc, schema, handler)
        Server-->>Factory: Tool instance with enable/disable
        Factory->>Registry: toolInstances[name] = instance
    end
    
    Factory->>Strategy: selectTools(context)
    Strategy-->>Factory: enabledToolIds[]
    
    loop For each tool instance
        alt Tool in enabledToolIds
            Factory->>Registry: toolInstance.enable()
        else Tool not enabled
            Factory->>Registry: toolInstance.disable()
        end
    end
    
    Factory-->>Factory: Return { server, userDetails }
```

**Sources:** [packages/app/src/server/mcp-server.ts:96-896](), [packages/app/src/server/mcp-server.ts:839-893]()

### Tool Instances and State Management

Each call to `server.tool()` returns an object with `enable()` and `disable()` methods. These instances are stored in a map for dynamic state control:

```typescript
// From mcp-server.ts
const toolInstances: { [name: string]: Tool } = {};

interface Tool {
  enable(): void;
  disable(): void;
}

// Registration stores instance
toolInstances[MODEL_SEARCH_TOOL_CONFIG.name] = server.tool(
  /* ... config ... */
);

// Later, state can be changed
toolInstances["model_search"].disable();
toolInstances["model_search"].enable();
```

**Tool State Management Architecture**

```mermaid
graph TB
    subgraph "Tool Registration"
        ServerTool["server.tool(...)"]
        Instance["Tool Instance<br/>{enable(), disable()}"]
    end
    
    subgraph "Storage"
        Map["toolInstances Map<br/>{[name]: instance}"]
    end
    
    subgraph "State Control"
        Selection["ToolSelectionStrategy<br/>Determines enabled tools"]
        Apply["applyToolStates()<br/>Calls enable/disable"]
    end
    
    subgraph "Dynamic Updates"
        Event["toolStateChange Event<br/>From McpApiClient"]
        Handler["Event Handler<br/>Toggles individual tool"]
    end
    
    ServerTool --> Instance
    Instance --> Map
    Selection --> Apply
    Apply --> Map
    Event --> Handler
    Handler --> Map
```

**Sources:** [packages/app/src/server/mcp-server.ts:174-177](), [packages/app/src/server/mcp-server.ts:839-859](), [packages/app/src/server/mcp-server.ts:873-891]()

### Dynamic State Changes via Events

For stateful transport modes (non-JSON, non-external API), the server listens for `toolStateChange` events from `McpApiClient`. When a tool is toggled in the web UI, all connected server instances receive the event and update their state:

**Sources:** [packages/app/src/server/mcp-server.ts:873-891]()

---

## Tool Invocation Lifecycle

When a client invokes a tool, the request flows through multiple layers of validation, routing, and execution before returning results.

### Request Flow

```mermaid
graph TB
    Client["MCP Client<br/>(Claude, VS Code, etc.)"]
    Transport["Transport Layer<br/>(STDIO, HTTP, SSE)"]
    Server["McpServer Instance"]
    Router["Tool Router<br/>(MCP SDK)"]
    Handler["Tool Handler Function<br/>async (params) => result"]
    
    subgraph "Validation & Parsing"
        Validate["Parameter Validation<br/>(Zod schema)"]
        Parse["JSON-RPC Parsing"]
    end
    
    subgraph "Tool Implementation"
        ToolImpl["Tool Class<br/>(e.g., ModelSearchTool)"]
        BaseClass["HfApiCall Base<br/>(Common API logic)"]
        HFAPI["Hugging Face API"]
    end
    
    subgraph "Result Processing"
        Format["formatSearchResults()<br/>Text formatting"]
        Result["ToolResult<br/>{content, formatted}"]
    end
    
    Client -->|"tools/call request"| Transport
    Transport --> Parse
    Parse --> Server
    Server --> Router
    Router --> Validate
    Validate -->|"Valid params"| Handler
    Handler --> ToolImpl
    ToolImpl --> BaseClass
    BaseClass --> HFAPI
    HFAPI --> ToolImpl
    ToolImpl --> Format
    Format --> Result
    Result --> Handler
    Handler --> Server
    Server --> Transport
    Transport --> Client
```

**Sources:** [packages/app/src/server/mcp-server.ts:383-406](), [packages/mcp/src/model-search.ts](), [packages/mcp/src/hf-api-call.ts]()

### Handler Function Signature

Tool handlers are async functions that receive validated parameters and return MCP-compatible results. The return format follows the `CallToolResultSchema` from the MCP SDK:

```typescript
// Handler pattern
async (params: ToolParamsType) => {
  // 1. Create tool instance
  const tool = new ToolClass(hfToken, username);
  
  // 2. Execute tool logic
  const result = await tool.execute(params);
  
  // 3. Return MCP result format
  return {
    content: [{ type: 'text', text: result.formatted }],
    ...(result.isError && { isError: true })
  };
}
```

**Sources:** [packages/app/src/server/mcp-server.ts:388-405](), [packages/app/src/server/mcp-server.ts:461-484]()

### Parameter Extraction and Validation

The MCP SDK automatically validates incoming parameters against the registered schema before invoking the handler. If validation fails, an error is returned to the client without calling the handler function. This ensures handlers always receive well-typed, validated data.

**Sources:** [packages/app/src/server/mcp-server.ts:383-406]()

---

## Tool Categories

The system distinguishes between different types of tools based on their implementation and registration timing.

### Built-in Tools

Built-in tools are statically registered during server initialization. There are 15 core built-in tools:

| Category | Tools | Count |
|----------|-------|-------|
| Search | `model_search`, `dataset_search`, `paper_search`, `space_semantic_search`, `hf_doc_search` | 5 |
| Detail | `model_detail`, `dataset_detail`, `hub_repo_details` | 3 |
| Space Management | `duplicate_space`, `space_info`, `space_files`, `use_space` | 4 |
| Documentation | `hf_doc_fetch` | 1 |
| Jobs | `hf_jobs` | 1 |
| Dynamic Space | `hf_space` | 1 |

Plus the `hf_whoami` authentication/info tool.

**Tool Registry Structure**

```mermaid
graph TB
    subgraph "Tool ID Registry"
        ToolIds["tool-ids.ts<br/>Canonical IDs"]
        Groups["TOOL_ID_GROUPS<br/>Grouped by category"]
    end
    
    subgraph "Built-in Tools (15)"
        SearchGroup["search Group<br/>5 tools"]
        SpacesGroup["spaces Group<br/>4 tools"]
        DetailGroup["detail Group<br/>3 tools"]
        DocsGroup["docs Group<br/>2 tools"]
        JobsGroup["jobs Group<br/>1 tool"]
    end
    
    subgraph "Tool Configurations"
        Configs["*_TOOL_CONFIG<br/>Exported constants"]
        Schema["Zod Schemas"]
        Handlers["Tool Classes"]
    end
    
    subgraph "Registration"
        McpServer["McpServer.tool()<br/>Registration"]
        Instances["toolInstances Map<br/>State control"]
    end
    
    ToolIds --> Groups
    Groups --> SearchGroup
    Groups --> SpacesGroup
    Groups --> DetailGroup
    Groups --> DocsGroup
    Groups --> JobsGroup
    
    Configs --> Schema
    Configs --> Handlers
    Configs --> McpServer
    McpServer --> Instances
```

**Sources:** [packages/mcp/src/tool-ids.ts:49-96](), [packages/app/src/server/mcp-server.ts:357-815]()

### Dynamic Gradio Tools

Dynamic Gradio tools are discovered and registered at runtime based on user configuration or header parameters. These are not included in the built-in tool count but are registered through the proxy factory pattern. See [Gradio Integration](#6) for details.

**Sources:** [packages/app/src/server/mcp-server.ts:699-815]()

### Prompts vs Tools

The MCP protocol distinguishes between tools and prompts:

- **Tools** (`server.tool()`): Execute actions and return results (e.g., search, fetch data)
- **Prompts** (`server.prompt()`): Return pre-formatted messages for the LLM context (e.g., summaries)

Prompts are registered using `server.prompt()` with a similar configuration pattern but return message arrays instead of tool results. The system includes 4 built-in prompts: `user_summary`, `paper_summary`, `model_detail_prompt`, and `dataset_detail_prompt`.

**Sources:** [packages/app/src/server/mcp-server.ts:221-355]()

---

## Tool Configuration Code Mapping

The following table maps natural language tool concepts to their code entities:

| Concept | Code Entity | File Location |
|---------|-------------|---------------|
| Tool configuration object | `*_TOOL_CONFIG` constants | `packages/mcp/src/` (various files) |
| Tool ID registry | `TOOL_ID_GROUPS` export | `packages/mcp/src/tool-ids.ts` |
| Tool registration | `server.tool()` calls | `packages/app/src/server/mcp-server.ts:357-815` |
| Tool state manager | `toolInstances: { [name: string]: Tool }` | `packages/app/src/server/mcp-server.ts:191` |
| Server factory | `createServerFactory()` | `packages/app/src/server/mcp-server.ts:96-896` |
| Tool selection logic | `ToolSelectionStrategy.selectTools()` | `packages/app/src/server/utils/tool-selection-strategy.ts` |
| State application | `applyToolStates()` | `packages/app/src/server/mcp-server.ts:839-859` |
| Settings service | `settingsService` | `packages/app/src/shared/settings.ts:50-95` |

**Sources:** [packages/app/src/server/mcp-server.ts:96-896](), [packages/mcp/src/tool-ids.ts:1-105](), [packages/app/src/shared/settings.ts:1-96]()

---

# Page: Built-in Tools

# Built-in Tools

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.dockerignore](.dockerignore)
- [Dockerfile](Dockerfile)
- [README.md](README.md)
- [packages/app/src/shared/constants.ts](packages/app/src/shared/constants.ts)
- [packages/app/vite.config.ts](packages/app/vite.config.ts)
- [packages/e2e-python/prompts.py](packages/e2e-python/prompts.py)
- [packages/mcp/src/dataset-detail.ts](packages/mcp/src/dataset-detail.ts)
- [packages/mcp/src/docs-search/doc-fetch.test.ts](packages/mcp/src/docs-search/doc-fetch.test.ts)
- [packages/mcp/src/docs-search/doc-fetch.ts](packages/mcp/src/docs-search/doc-fetch.ts)
- [packages/mcp/src/docs-search/docs-semantic-search.test.ts](packages/mcp/src/docs-search/docs-semantic-search.test.ts)
- [packages/mcp/src/docs-search/docs-semantic-search.ts](packages/mcp/src/docs-search/docs-semantic-search.ts)
- [packages/mcp/src/duplicate-space.ts](packages/mcp/src/duplicate-space.ts)
- [packages/mcp/src/error-messages.ts](packages/mcp/src/error-messages.ts)
- [packages/mcp/src/index.ts](packages/mcp/src/index.ts)
- [packages/mcp/src/model-detail.ts](packages/mcp/src/model-detail.ts)
- [packages/mcp/src/tool-ids.ts](packages/mcp/src/tool-ids.ts)
- [start.sh](start.sh)

</details>



## Purpose and Scope

This page provides a comprehensive reference for all built-in tools in the Hugging Face MCP Server. Built-in tools are statically defined MCP tools that provide access to Hugging Face Hub APIs, documentation, and space management capabilities. These tools are distinct from dynamically-discovered Gradio tools (covered in [Gradio Integration](#6)).

For information about how tools are selected and enabled, see [Tool Selection System](#5). For details about the tool configuration pattern, schema validation, and invocation lifecycle, see [Tool System Overview](#4.1).

**Scope**: This page documents the 15 built-in tools, their organization into functional categories, registration patterns, and the tool ID system. Detailed documentation for each tool category is provided in subsections [4.2.1](#4.2.1) through [4.2.4](#4.2.4).

## Tool Architecture Overview

Built-in tools follow a consistent configuration and registration pattern. Each tool is defined by a `TOOL_CONFIG` object containing metadata, a Zod schema for parameters, and optional annotations. The tool IDs serve as canonical identifiers throughout the system.

```mermaid
graph TB
    subgraph "Tool Definition Layer"
        Config["TOOL_CONFIG Object<br/>• name (tool ID)<br/>• description<br/>• schema (Zod)<br/>• annotations"]
        Implementation["Tool Implementation<br/>Class or Function"]
    end
    
    subgraph "Tool Registry (tool-ids.ts)"
        ToolIds["Exported Tool ID Constants<br/>MODEL_SEARCH_TOOL_ID<br/>DATASET_DETAIL_TOOL_ID<br/>DOC_FETCH_TOOL_ID..."]
        Groups["TOOL_ID_GROUPS<br/>• search<br/>• detail<br/>• spaces<br/>• docs<br/>• hf_api"]
        AllBuiltin["ALL_BUILTIN_TOOL_IDS<br/>(15 tools)"]
    end
    
    subgraph "MCP Server Registration"
        ServerFactory["createServerFactory()"]
        ToolSelection["ToolSelectionStrategy"]
        McpServer["McpServer Instance"]
        RegisteredTools["server.setRequestHandler<br/>('tools/list')<br/>('tools/call')"]
    end
    
    Config -->|"exports"| ToolIds
    Implementation -->|"uses"| Config
    ToolIds --> Groups
    ToolIds --> AllBuiltin
    Groups --> ToolSelection
    ToolSelection --> ServerFactory
    ServerFactory --> McpServer
    McpServer --> RegisteredTools
    Implementation -->|"invoked via"| RegisteredTools
```

**Diagram**: Tool configuration and registration architecture

Sources: [packages/mcp/src/tool-ids.ts:1-105](), [packages/mcp/src/index.ts:1-30]()

## Complete Tool Registry

The following table lists all 15 built-in tools with their canonical IDs, primary categories, and descriptions:

| Tool ID | Category | Description | Auth Required |
|---------|----------|-------------|---------------|
| `space_semantic_search` | Search, Spaces | Semantic search for Spaces on Hugging Face | No |
| `model_search` | Search | Search for models on the Hub | No |
| `dataset_search` | Search | Search for datasets on the Hub | No |
| `paper_search` | Search | Search for papers on Hugging Face Papers | No |
| `hf_doc_search` | Search, Docs | Semantic search in HF documentation | No |
| `model_details` | Detail | Get detailed model information | No* |
| `dataset_details` | Detail | Get detailed dataset information | No* |
| `hub_repo_details` | Detail | Get repository metadata and file lists | No* |
| `duplicate_space` | Spaces | Duplicate a Space to user's namespace | Yes |
| `space_info` | Spaces | Get Space runtime and configuration info | No* |
| `space_files` | Spaces | List files in a Space repository | No* |
| `use_space` | Spaces | Dynamically invoke any Gradio Space | No* |
| `hf_doc_fetch` | Docs | Fetch and convert documentation to Markdown | No |
| `hf_jobs` | HF API | Query Hugging Face compute jobs | Yes |
| `dynamic_space` | Dynamic | Runtime-generated Space endpoint tools | No* |

\* Authentication may be required for private or gated resources

Sources: [packages/mcp/src/tool-ids.ts:49-66](), [packages/mcp/src/index.ts:1-30]()

## Tool ID System

Tool IDs are the canonical identifiers used throughout the codebase. They are exported from individual tool configuration objects and centralized in `tool-ids.ts` for reference by other components.

```mermaid
graph LR
    subgraph "Tool Definition Files"
        ModelDetail["model-detail.ts<br/>MODEL_DETAIL_TOOL_CONFIG<br/>name: 'model_details'"]
        DocFetch["doc-fetch.ts<br/>DOC_FETCH_CONFIG<br/>name: 'hf_doc_fetch'"]
        DuplicateSpace["duplicate-space.ts<br/>DUPLICATE_SPACE_TOOL_CONFIG<br/>name: 'duplicate_space'"]
    end
    
    subgraph "Centralized Registry (tool-ids.ts)"
        Exports["Export Tool ID Constants:<br/>MODEL_DETAIL_TOOL_ID = MODEL_DETAIL_TOOL_CONFIG.name<br/>DOC_FETCH_TOOL_ID = DOC_FETCH_CONFIG.name<br/>DUPLICATE_SPACE_TOOL_ID = DUPLICATE_SPACE_TOOL_CONFIG.name"]
    end
    
    subgraph "Consumers"
        ToolSelection["Tool Selection Strategy<br/>Uses tool IDs for filtering"]
        Bouquets["Bouquet Configurations<br/>Reference tool IDs"]
        TypeChecking["Type Guards<br/>isValidBuiltinToolId()"]
    end
    
    ModelDetail -->|"config exported"| Exports
    DocFetch -->|"config exported"| Exports
    DuplicateSpace -->|"config exported"| Exports
    Exports --> ToolSelection
    Exports --> Bouquets
    Exports --> TypeChecking
```

**Diagram**: Tool ID centralization and usage pattern

The `tool-ids.ts` module provides:
- **Exported constants**: One for each tool (e.g., `MODEL_SEARCH_TOOL_ID`)
- **`ALL_BUILTIN_TOOL_IDS`**: Array of all 15 tool IDs
- **`TOOL_ID_GROUPS`**: Predefined groupings for bouquet configurations
- **`isValidBuiltinToolId()`**: Type guard function for validation

Sources: [packages/mcp/src/tool-ids.ts:1-105]()

## Tool Categories

Built-in tools are organized into five functional categories, each serving a distinct purpose within the Hugging Face ecosystem:

### 1. Search Tools (5 tools)

Tools for discovering content across the Hugging Face Hub and documentation. See [Search Tools](#4.2.1) for detailed documentation.

| Tool ID | Purpose |
|---------|---------|
| `space_semantic_search` | Find Spaces using semantic queries |
| `model_search` | Find models by name, tags, or metadata |
| `dataset_search` | Find datasets by name, tags, or task |
| `paper_search` | Search academic papers on HF Papers |
| `hf_doc_search` | Search HF product documentation |

### 2. Detail Tools (3 tools)

Tools for retrieving comprehensive information about Hub entities. See [Detail Tools](#4.2.2) for detailed documentation.

| Tool ID | Purpose |
|---------|---------|
| `model_details` | Full model card, stats, and metadata |
| `dataset_details` | Full dataset card, stats, and metadata |
| `hub_repo_details` | Repository metadata and file listings |

### 3. Space Management Tools (5 tools)

Tools for managing and interacting with Hugging Face Spaces. See [Space Management Tools](#4.2.3) for detailed documentation.

| Tool ID | Purpose |
|---------|---------|
| `duplicate_space` | Clone a Space to user's account |
| `space_info` | Get Space runtime configuration |
| `space_files` | List files in Space repository |
| `use_space` | Invoke any Gradio Space dynamically |
| `dynamic_space` | Runtime-generated Space endpoint |

### 4. Documentation Tools (2 tools)

Tools for discovering and retrieving Hugging Face documentation. See [Documentation Tools](#4.2.4) for detailed documentation.

| Tool ID | Purpose |
|---------|---------|
| `hf_doc_search` | Semantic documentation search |
| `hf_doc_fetch` | Fetch and convert docs to Markdown |

### 5. Additional Tools

| Tool ID | Category | Purpose |
|---------|----------|---------|
| `hf_jobs` | HF API | Query user's compute jobs |
| `hf_whoami` | Auth | Get authenticated user info |

Sources: [packages/mcp/src/tool-ids.ts:67-96]()

## Tool Configuration Pattern

Each built-in tool is defined using a consistent configuration object pattern. This pattern is detailed in [Tool System Overview](#4.1), but is summarized here for reference.

### Configuration Structure

```typescript
export const TOOL_CONFIG = {
    name: string,              // Tool ID (canonical identifier)
    description: string,       // User-facing description
    schema: ZodSchema,        // Parameter validation schema
    annotations: {            // MCP annotations
        title?: string,
        destructiveHint?: boolean,
        readOnlyHint?: boolean,
        openWorldHint?: boolean,
    },
} as const;
```

### Example: Documentation Fetch Tool

The `hf_doc_fetch` tool demonstrates this pattern:

```typescript
// Configuration object
export const DOC_FETCH_CONFIG = {
    name: 'hf_doc_fetch',
    description: 'Fetch a document from the Hugging Face or Gradio documentation library...',
    schema: z.object({
        doc_url: z.string().max(200).describe('Documentation URL'),
        offset: z.number().min(0).optional().describe('Token offset for large documents'),
    }),
    annotations: {
        title: 'Fetch a document from the Hugging Face documentation library',
        destructiveHint: false,
        readOnlyHint: true,
        openWorldHint: true,
    },
}

// Implementation class
export class DocFetchTool {
    async fetch(params: DocFetchParams): Promise<string> {
        // ... implementation
    }
}
```

Sources: [packages/mcp/src/docs-search/doc-fetch.ts:5-23](), [packages/mcp/src/docs-search/doc-fetch.ts:27-217]()

## Tool Implementation Patterns

Built-in tools follow two primary implementation patterns:

### Pattern 1: HfApiCall Base Class

Most tools that interact with Hugging Face APIs extend the `HfApiCall` base class, which provides:
- HTTP request handling with authentication
- Error handling and retry logic
- Timeout management
- Response parsing

```mermaid
graph TB
    HfApiCall["HfApiCall<TParams, TResponse><br/>Base Class"]
    
    DocSearchTool["DocSearchTool<br/>extends HfApiCall"]
    ModelDetailTool["ModelDetailTool<br/>Direct HF.js library"]
    DatasetDetailTool["DatasetDetailTool<br/>Direct HF.js library"]
    DuplicateSpaceTool["DuplicateSpaceTool<br/>extends HfApiCall"]
    
    HfApiCall -->|"provides API utilities"| DocSearchTool
    HfApiCall -->|"provides API utilities"| DuplicateSpaceTool
    
    HFLibrary["@huggingface/hub<br/>Official JS Library"]
    ModelDetailTool -.->|"uses modelInfo()"| HFLibrary
    DatasetDetailTool -.->|"uses datasetInfo()"| HFLibrary
    
    style HfApiCall fill:#f9f9f9
    style HFLibrary fill:#f9f9f9
```

**Diagram**: Tool implementation inheritance patterns

### Pattern 2: Direct Library Usage

Some tools (particularly detail tools) use the official `@huggingface/hub` JavaScript library directly:
- `ModelDetailTool` uses `modelInfo()`
- `DatasetDetailTool` uses `datasetInfo()`

This approach provides type-safe access to Hub APIs with proper error handling built-in.

Sources: [packages/mcp/src/hf-api-call.ts]() (referenced), [packages/mcp/src/model-detail.ts:1-6](), [packages/mcp/src/dataset-detail.ts:1-6]()

## Tool Registration Flow

Tools are registered with the MCP Server during server initialization. The process involves tool selection, instantiation, and handler registration.

```mermaid
sequenceDiagram
    participant Factory as createServerFactory()
    participant Selection as ToolSelectionStrategy
    participant Server as McpServer
    participant Handlers as Tool Handlers
    
    Factory->>Selection: selectTools(context)
    Selection->>Selection: Apply bouquet/user settings
    Selection-->>Factory: enabledToolIds[]
    
    Factory->>Server: new McpServer()
    
    loop For each enabled tool ID
        Factory->>Server: Register tool config
        Factory->>Handlers: Create tool instance
        Server->>Server: setRequestHandler('tools/call', toolId)
    end
    
    Server-->>Factory: Configured McpServer
    
    Note over Server: Server ready to handle:<br/>- tools/list<br/>- tools/call
```

**Diagram**: Tool registration sequence during server startup

The registration process:

1. **Tool Selection**: `ToolSelectionStrategy` determines which tools to enable based on bouquets, user settings, or defaults (see [Tool Selection System](#5))

2. **Tool Instantiation**: Tool implementation classes are instantiated with appropriate configuration (HF token, API URLs, etc.)

3. **Handler Registration**: Each tool's configuration and handler are registered with the `McpServer` instance

4. **Request Routing**: When clients call `tools/call`, the server routes to the appropriate tool handler based on tool ID

Sources: [packages/app/src/server/mcp-server-factory.ts]() (referenced from diagrams)

## Tool Groupings for Bouquets

Tool groupings defined in `TOOL_ID_GROUPS` are used by the bouquet system to enable predefined sets of tools. These groupings allow clients to request specific capabilities without listing individual tools.

| Bouquet | Tools Included | Use Case |
|---------|----------------|----------|
| `search` | 5 search tools | Discovery-focused workflows |
| `detail` | 3 detail tools | Information retrieval |
| `spaces` | 5 space tools | Space management and usage |
| `docs` | 2 documentation tools | Documentation lookup |
| `hf_api` | 7 core API tools | General Hub operations |
| `all` | All 15 tools | Full capability access |

Note: Some tools appear in multiple groupings (e.g., `space_semantic_search` is in both `search` and `spaces`).

For more information on how bouquets work and how to use them, see [Bouquet System](#5.1).

Sources: [packages/mcp/src/tool-ids.ts:67-96]()

## Tool Discovery and Listing

Clients discover available tools through the MCP `tools/list` request. The server returns tool configurations for all enabled tools based on the current tool selection strategy.

### Tool List Response Structure

Each tool in the response includes:
- **name**: The tool ID
- **description**: User-facing description (may be dynamically generated with user context)
- **inputSchema**: JSON Schema representation of the Zod validation schema
- **annotations**: MCP-specific metadata (destructive hints, read-only indicators, etc.)

### Dynamic Tool Descriptions

Some tools (e.g., `duplicate_space`) generate descriptions dynamically to include user-specific information:

```typescript
static createToolConfig(username?: string) {
    const description = username
        ? `Duplicate a Hugging Face Space. Target space will be created as ${username}/<new-space-name>.`
        : NO_TOKEN_INSTRUCTIONS;
    return {
        ...DUPLICATE_SPACE_TOOL_CONFIG,
        description,
    };
}
```

This allows the tool to provide context-aware guidance based on the authenticated user.

Sources: [packages/mcp/src/duplicate-space.ts:82-92]()

## Authentication Requirements

Most built-in tools operate without authentication, but some require or benefit from a Hugging Face token:

### Requires Authentication
- `duplicate_space`: Must have valid token to create Spaces
- `hf_jobs`: Must have token to query user's jobs

### Benefits from Authentication
- `model_details`, `dataset_details`: Required for private/gated content
- `space_info`, `space_files`: Required for private Spaces
- `hub_repo_details`: Required for private repositories

### No Authentication Needed
- Search tools: `model_search`, `dataset_search`, `paper_search`, `space_semantic_search`
- Documentation tools: `hf_doc_search`, `hf_doc_fetch`

Authentication is handled via the `Authorization: Bearer <token>` header on HTTP transports, or via the `HF_TOKEN` environment variable for STDIO transport.

Sources: [packages/mcp/src/duplicate-space.ts:124-129](), [packages/mcp/src/utilities.ts]() (referenced for NO_TOKEN_INSTRUCTIONS)

## Tool Result Format

All built-in tools return results in a consistent format defined by the `ToolResult` interface:

```typescript
interface ToolResult {
    formatted: string;      // Markdown-formatted output
    totalResults: number;   // Total items found/processed
    resultsShared: number;  // Items included in response
}
```

This structure allows tools to:
- Return human-readable Markdown output
- Indicate pagination or truncation (when `resultsShared < totalResults`)
- Provide metadata about the operation

### Markdown Formatting

Tools format their output as Markdown for optimal readability in LLM contexts:
- Headers for sections
- Lists for multiple items
- Tables for structured data
- Links to relevant Hub pages
- Code blocks for technical details

Example output structure from `model_details`:

```markdown
# model-name

## Overview
- **Author:** author-name
- **Task:** text-generation
- **Downloads:** 1.2M | **Likes:** 500

## Technical Details
- **Parameters:** 7B
- **Architecture:** transformer

**Link:** [https://hf.co/model-name](...)
```

Sources: [packages/mcp/src/types/tool-result.ts]() (referenced), [packages/mcp/src/model-detail.ts:304-462]()

## Special Features

### Document Chunking

The `hf_doc_fetch` tool implements automatic chunking for large documents:
- Maximum chunk size: 7,500 tokens
- Returns truncation message with offset for next chunk
- Allows progressive retrieval of long documents

```typescript
private applyChunking(markdownContent: string, offset: number): string {
    const totalTokens = estimateTokens(markdownContent);
    const maxTokensPerChunk = 7500;
    // ... chunking logic
    if (hasMore) {
        result += `\n\n=== DOCUMENT TRUNCATED. CALL ${DOC_FETCH_CONFIG.name} WITH AN OFFSET OF ${nextOffset} FOR THE NEXT CHUNK ===`;
    }
    return result;
}
```

Sources: [packages/mcp/src/docs-search/doc-fetch.ts:181-216]()

### HTML to Markdown Conversion

Documentation tools use TurndownService to convert HTML to Markdown:
- Removes navigation, scripts, SVG images
- Preserves code blocks and formatting
- Strips anchor-only links and decorative elements

Sources: [packages/mcp/src/docs-search/doc-fetch.ts:27-116]()

### README Inclusion

Detail tools can optionally include README content from repositories:

```typescript
async getDetails(modelId: string, includeReadme: boolean = false): Promise<ToolResult> {
    // ... fetch model data
    
    if (includeReadme) {
        const readmeContent = await fetchReadmeContent(modelDetails.name, 'models', false);
        if (readmeContent) {
            result.formatted += '\n\n## README\n<modelcard-readme>\n' + readmeContent.trim() + '\n</modelcard-readme>';
        }
    }
    
    return result;
}
```

This is particularly useful for the prompt-based invocations where full context is desired.

Sources: [packages/mcp/src/model-detail.ts:261-268](), [packages/mcp/src/dataset-detail.ts:164-173]()

## Next Steps

For detailed information about specific tool categories:
- [Search Tools](#4.2.1) - Comprehensive guide to the 5 search tools
- [Detail Tools](#4.2.2) - Model, dataset, and repository detail retrieval
- [Space Management Tools](#4.2.3) - Space duplication, info, and usage
- [Documentation Tools](#4.2.4) - Documentation search and retrieval

For information about how tools are selected and configured:
- [Tool Selection System](#5) - Bouquets, mixes, and user settings
- [Tool System Overview](#4.1) - Configuration patterns and schemas

---

# Page: Search Tools

# Search Tools

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [packages/app/src/shared/constants.ts](packages/app/src/shared/constants.ts)
- [packages/e2e-python/prompts.py](packages/e2e-python/prompts.py)
- [packages/mcp/src/dataset-detail.ts](packages/mcp/src/dataset-detail.ts)
- [packages/mcp/src/docs-search/doc-fetch.test.ts](packages/mcp/src/docs-search/doc-fetch.test.ts)
- [packages/mcp/src/docs-search/doc-fetch.ts](packages/mcp/src/docs-search/doc-fetch.ts)
- [packages/mcp/src/docs-search/docs-semantic-search.test.ts](packages/mcp/src/docs-search/docs-semantic-search.test.ts)
- [packages/mcp/src/docs-search/docs-semantic-search.ts](packages/mcp/src/docs-search/docs-semantic-search.ts)
- [packages/mcp/src/model-detail.ts](packages/mcp/src/model-detail.ts)

</details>



## Purpose and Scope

This page documents the five search tools that enable discovery of resources on the Hugging Face Hub and within the documentation library. These tools provide semantic search capabilities for models, datasets, papers, spaces, and documentation.

For tools that retrieve detailed information about specific entities, see [Detail Tools](#4.2.2). For space-specific operations beyond search, see [Space Management Tools](#4.2.3). For documentation retrieval after search, see [Documentation Tools](#4.2.4).

**Sources:** [packages/mcp/src/docs-search/docs-semantic-search.ts:1-380]()

## Available Search Tools

| Tool Name | Purpose | Primary Use Case |
|-----------|---------|------------------|
| `model_search` | Search for models on Hugging Face Hub | Finding models by keywords, tags, or capabilities |
| `dataset_search` | Search for datasets on Hugging Face Hub | Discovering datasets by task, domain, or features |
| `paper_search` | Search for papers on Hugging Face Hub | Finding research papers and associated artifacts |
| `space_semantic_search` | Semantic search for Spaces | Discovering Gradio/Streamlit applications |
| `hf_doc_search` | Search Hugging Face documentation | Finding documentation pages and code examples |

**Sources:** [packages/mcp/src/docs-search/docs-semantic-search.ts:10-45]()

## Search Tool Architecture

### Tool Configuration Pattern

All search tools follow a consistent configuration pattern using Zod schemas for input validation and MCP tool annotations.

```mermaid
graph TB
    subgraph "Tool Configuration Structure"
        Config["TOOL_CONFIG Object"]
        Config --> Name["name: string"]
        Config --> Desc["description: string"]
        Config --> Schema["schema: ZodObject"]
        Config --> Annotations["annotations: object"]
        
        Schema --> QueryParam["query: z.string()"]
        Schema --> Filters["filter params (optional)"]
        
        Annotations --> Title["title: string"]
        Annotations --> Hints["readOnlyHint: true<br/>destructiveHint: false<br/>openWorldHint: true"]
    end
    
    subgraph "Implementation Classes"
        ToolClass["SearchTool Class"]
        HfApiCall["HfApiCall<TParams, TResponse>"]
        
        ToolClass -.extends.- HfApiCall
        ToolClass --> SearchMethod["search(params): Promise<ToolResult>"]
    end
    
    subgraph "Result Structure"
        ToolResult["ToolResult"]
        ToolResult --> Formatted["formatted: string<br/>(Markdown)"]
        ToolResult --> TotalResults["totalResults: number"]
        ToolResult --> ResultsShared["resultsShared: number"]
    end
    
    Config -.used by.- ToolClass
    SearchMethod -.returns.- ToolResult
```

**Diagram: Search Tool Configuration and Implementation Pattern**

**Sources:** [packages/mcp/src/docs-search/docs-semantic-search.ts:10-45](), [packages/mcp/src/types/tool-result.ts]()

### HfApiCall Base Class

Search tools that interact with the Hugging Face API extend the `HfApiCall` base class, which provides common functionality for HTTP requests, error handling, and authentication.

```mermaid
graph LR
    subgraph "Base Class"
        HfApiCall["HfApiCall&lt;TParams, TResponse&gt;"]
        HfApiCall --> Constructor["constructor(apiUrl, hfToken?)"]
        HfApiCall --> CallApi["callApi(params): Promise&lt;TResponse&gt;"]
        HfApiCall --> FetchFromApi["fetchFromApi&lt;T&gt;(url): Promise&lt;T&gt;"]
    end
    
    subgraph "Concrete Implementations"
        DocSearchTool["DocSearchTool"]
        ModelSearchTool["ModelSearchTool"]
        DatasetSearchTool["DatasetSearchTool"]
        PaperSearchTool["PaperSearchTool"]
    end
    
    HfApiCall -.inherited by.- DocSearchTool
    HfApiCall -.inherited by.- ModelSearchTool
    HfApiCall -.inherited by.- DatasetSearchTool
    HfApiCall -.inherited by.- PaperSearchTool
    
    DocSearchTool --> DocSearch["search(params):<br/>Promise&lt;ToolResult&gt;"]
    ModelSearchTool --> ModelSearch["search(params):<br/>Promise&lt;ToolResult&gt;"]
    DatasetSearchTool --> DatasetSearch["search(params):<br/>Promise&lt;ToolResult&gt;"]
    PaperSearchTool --> PaperSearch["search(params):<br/>Promise&lt;ToolResult&gt;"]
```

**Diagram: HfApiCall Base Class Inheritance Hierarchy**

**Sources:** [packages/mcp/src/docs-search/docs-semantic-search.ts:77-88](), [packages/mcp/src/hf-api-call.ts]()

## Documentation Search Tool (hf_doc_search)

### Tool Configuration

The `hf_doc_search` tool provides semantic search over the Hugging Face documentation library with support for product filtering and empty-query discovery.

```typescript
// Tool identifier and schema
name: 'hf_doc_search'

// Input parameters
query: string (0-200 chars)  // Empty query returns docs index
product?: string             // Optional filter (e.g., 'hub', 'transformers')

// Annotations
readOnlyHint: true           // Read-only operation
openWorldHint: true          // Can discover new information
```

**Sources:** [packages/mcp/src/docs-search/docs-semantic-search.ts:10-45]()

### Empty Query Behavior

When invoked with an empty query string, `hf_doc_search` returns the documentation index, providing a structured overview of available products and navigation guidance.

```mermaid
sequenceDiagram
    participant Client
    participant DocSearchTool
    participant DocsAPI["HF Docs API<br/>/api/docs"]
    
    Client->>DocSearchTool: "search({ query: '' })"
    DocSearchTool->>DocSearchTool: "query.trim().length === 0"
    DocSearchTool->>DocsAPI: "fetchFromApi(DOCS_INDEX_URL)"
    DocsAPI-->>DocSearchTool: "DocsIndexEntry[]"
    DocSearchTool->>DocSearchTool: "formatDocsIndex()"
    DocSearchTool-->>Client: "Markdown table of products"
    
    Note over Client,DocSearchTool: Returns structure, categories,<br/>and llms.txt endpoints
```

**Diagram: Empty Query Discovery Flow**

The response includes a markdown table with columns for Product ID, Category, and Documentation URL, plus information about `llms.txt` endpoints for each documentation root.

**Sources:** [packages/mcp/src/docs-search/docs-semantic-search.ts:94-100](), [packages/mcp/src/docs-search/docs-semantic-search.ts:162-190]()

### Semantic Search Flow

For non-empty queries, the tool performs semantic search against the documentation API and formats results with grouping and token budget management.

```mermaid
graph TB
    subgraph "Search Execution"
        Input["DocSearchParams<br/>{query, product?}"]
        Input --> Validate["Validate query length<br/>(3-200 chars)"]
        Validate --> BuildParams["Build API params<br/>{q: query.toLowerCase()}"]
        BuildParams --> AddFilter{product<br/>provided?}
        AddFilter -->|yes| WithFilter["Add product filter"]
        AddFilter -->|no| NoFilter["No filter"]
        WithFilter --> APICall
        NoFilter --> APICall
        APICall["callApi()<br/>→ DocSearchResult[]"]
    end
    
    subgraph "Result Processing"
        APICall --> CheckEmpty{results.length<br/>=== 0?}
        CheckEmpty -->|yes| EmptyMsg["Return 'No documentation found'"]
        CheckEmpty -->|no| Format["formatSearchResults()"]
        
        Format --> Group["groupResults()<br/>by product & page"]
        Group --> Sort["Sort by hit count"]
        Sort --> BuildOutput["Build markdown output"]
        BuildOutput --> TokenCheck["Token budget check"]
        TokenCheck --> Truncate["Truncate excerpts<br/>or use links"]
    end
    
    BuildOutput --> Result["ToolResult"]
    EmptyMsg --> Result
    Truncate --> Result
```

**Diagram: Semantic Search Processing Pipeline**

**Sources:** [packages/mcp/src/docs-search/docs-semantic-search.ts:94-127](), [packages/mcp/src/docs-search/docs-semantic-search.ts:265-379]()

### Result Grouping and Formatting

Search results are grouped hierarchically by product, then by source page URL (with anchors stripped), then by section heading.

```mermaid
graph TB
    subgraph "Grouping Hierarchy"
        Results["DocSearchResult[]"]
        Results --> GroupByProduct["Group by product field"]
        GroupByProduct --> Product1["Product: 'hub'"]
        GroupByProduct --> Product2["Product: 'transformers'"]
        GroupByProduct --> Product3["Product: 'dataset-viewer'"]
        
        Product1 --> Page1["Page: /docs/hub/analytics<br/>(strip #anchors)"]
        Product1 --> Page2["Page: /docs/hub/spaces"]
        
        Page1 --> Section1["Section: heading2 = 'Export'"]
        Page1 --> Section2["Section: heading2 = 'View'"]
        
        Section1 --> Excerpt1["text excerpts"]
        Section2 --> Excerpt2["text excerpts"]
    end
    
    subgraph "Markdown Output Structure"
        Header["# Search Results<br/>Found N results"]
        Header --> ProdHeader1["## Results for Product: hub (5 results)"]
        ProdHeader1 --> PageHeader1["### Results from [Analytics](url) (3 results)"]
        PageHeader1 --> SectionHeader1["#### Excerpts from 'Export' section"]
        SectionHeader1 --> ExcerptText["Plain text excerpt..."]
    end
```

**Diagram: Result Grouping and Output Structure**

**Sources:** [packages/mcp/src/docs-search/docs-semantic-search.ts:132-157](), [packages/mcp/src/docs-search/docs-semantic-search.ts:194-210]()

### Token Budget Management

The tool implements a token budget system (default 12,500 tokens) to prevent overwhelming responses. When approaching the budget, the tool switches strategies:

| Phase | Token Usage | Behavior |
|-------|-------------|----------|
| Early results | < 70% of budget | Full excerpts included |
| Approaching limit | > 70% of budget | Excerpts truncated to 400 chars with message |
| Over budget | > 100% of budget | Pages converted to link-only references |

```mermaid
graph LR
    subgraph "Budget Checking Logic"
        Start["For each product/page"]
        Start --> EstimateTokens["estimateTokens(currentText)"]
        EstimateTokens --> CheckBudget{tokens ><br/>budget?}
        
        CheckBudget -->|under| CheckPhase{tokens ><br/>70% budget?}
        CheckBudget -->|over| LinkOnly["Add to linkOnlyResults[]"]
        
        CheckPhase -->|yes| Truncate["Truncate excerpts<br/>to 400 chars<br/>+ show message"]
        CheckPhase -->|no| Full["Include full excerpt"]
        
        Full --> AddToOutput["Add to output"]
        Truncate --> AddToOutput
        LinkOnly --> DeferredLinks["Added to<br/>'Further results' section"]
    end
```

**Diagram: Token Budget Management Strategy**

**Sources:** [packages/mcp/src/docs-search/docs-semantic-search.ts:69-72](), [packages/mcp/src/docs-search/docs-semantic-search.ts:296-370](), [packages/mcp/src/docs-search/docs-semantic-search.ts:242-248]()

### Integration with Doc Fetch Tool

Search results include a footer message directing users to the `hf_doc_fetch` tool for retrieving full document content. The constant `DOC_FETCH_CONFIG.name` is referenced to maintain consistency.

```typescript
// Footer added to all search results
lines.push(`Use the "${DOC_FETCH_CONFIG.name}" tool to fetch a document from the library.`);
```

This integration pattern enables a two-step workflow: discover relevant documentation with `hf_doc_search`, then retrieve full content with `hf_doc_fetch`.

**Sources:** [packages/mcp/src/docs-search/docs-semantic-search.ts:4](), [packages/mcp/src/docs-search/docs-semantic-search.ts:372]()

## Model, Dataset, and Paper Search Tools

While the implementation files for `model_search`, `dataset_search`, and `paper_search` are not included in the provided sources, these tools follow similar patterns to the documentation search tool:

### Common Characteristics

- Extend `HfApiCall` base class for API interactions
- Accept query strings and optional filter parameters
- Return `ToolResult` with formatted markdown
- Support sorting and filtering by various attributes
- Integrate with corresponding detail tools (see [Detail Tools](#4.2.2))

### Typical Parameters

| Tool | Key Parameters | Example Filters |
|------|---------------|-----------------|
| `model_search` | query, sort, direction, limit | task, language, library, tags |
| `dataset_search` | query, sort, direction, limit | task_categories, languages, size_categories |
| `paper_search` | query, sort, limit | published date, topics |

**Sources:** Inferred from [packages/mcp/src/model-detail.ts](), [packages/mcp/src/dataset-detail.ts]()

## Space Semantic Search

The `space_semantic_search` tool enables discovery of Gradio and Streamlit applications hosted on Hugging Face Spaces using semantic queries.

### Integration with Gradio System

Space search results can be used in conjunction with the Gradio integration system (see [Gradio Integration](#6)) to dynamically load and invoke Space tools.

```mermaid
graph LR
    subgraph "Discovery to Execution Flow"
        SpaceSearch["space_semantic_search<br/>query='image generation'"]
        SpaceSearch --> Results["List of matching<br/>Space IDs"]
        Results --> UseSpace["use_space tool<br/>with Space ID"]
        UseSpace --> GradioProxy["Gradio Proxy Factory"]
        GradioProxy --> Execution["Dynamic tool execution"]
    end
```

**Diagram: Space Search to Execution Pipeline**

**Sources:** Referenced in tool selection system documentation

## Search Results Structure

All search tools return a consistent `ToolResult` structure with three key fields:

```typescript
interface ToolResult {
  formatted: string;      // Markdown-formatted results for display
  totalResults: number;   // Total number of results found
  resultsShared: number;  // Number of results included in formatted output
}
```

The distinction between `totalResults` and `resultsShared` allows tools to report when results have been truncated or limited for token budget reasons.

**Sources:** [packages/mcp/src/types/tool-result.ts](), [packages/mcp/src/docs-search/docs-semantic-search.ts:374-378]()

## Search-Fetch Integration Pattern

The documentation search tool demonstrates a key integration pattern where search tools reference complementary fetch/detail tools:

```mermaid
graph LR
    subgraph "Two-Step Workflow"
        Client["MCP Client"]
        Client -->|1| SearchTool["hf_doc_search<br/>query='transformers'"]
        SearchTool --> SearchResults["Formatted results<br/>+ URLs"]
        SearchResults -->|User reviews| Client
        Client -->|2| FetchTool["hf_doc_fetch<br/>doc_url='...'"]
        FetchTool --> FullContent["Full document<br/>content"]
    end
    
    SearchResults -.footer message.-> FetchTool
```

**Diagram: Search-to-Fetch Workflow Pattern**

This pattern is also utilized by the tool selection strategy through the `SEARCH_ENABLES_FETCH` feature flag (see [Tool Selection Strategy](#5.2)), which automatically enables `hf_doc_fetch` when `hf_doc_search` is selected in a bouquet.

**Sources:** [packages/mcp/src/docs-search/docs-semantic-search.ts:372](), [packages/mcp/src/docs-search/doc-fetch.ts:5-23]()

## Test Coverage

The documentation search tool includes comprehensive test coverage demonstrating expected behaviors:

### Key Test Scenarios

- URL validation for HF and Gradio documentation
- Empty query returns documentation index
- Product filtering in search requests
- Result grouping by product and page
- Token budget enforcement with truncation
- Link-only mode for over-budget results
- Markdown escaping for special characters
- HTML tag removal from excerpts
- Proper sorting by result count

**Sources:** [packages/mcp/src/docs-search/docs-semantic-search.test.ts:1-429]()

## Usage Example

From the end-to-end test suite:

```python
# Discover documentation structure
await agent.anon("***CALL_TOOL hf_doc_search {\"query\": \"\"}")

# Search for specific topic
await agent.anon("***CALL_TOOL hf_doc_search {\"query\": \"rate limits\", \"product\": \"hub\"}")

# Fetch full document after search
await agent.anon("***CALL_TOOL hf_doc_fetch {\"doc_url\": \"https://huggingface.co/docs/hub/...\"}")
```

**Sources:** [packages/e2e-python/prompts.py:1-30]() (pattern inferred)

---

# Page: Detail Tools

# Detail Tools

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [packages/e2e-python/prompts.py](packages/e2e-python/prompts.py)
- [packages/mcp/src/dataset-detail.ts](packages/mcp/src/dataset-detail.ts)
- [packages/mcp/src/model-detail.ts](packages/mcp/src/model-detail.ts)

</details>



This document describes the detail tools in the HF MCP Server that retrieve comprehensive information about specific entities on the Hugging Face Hub. These tools provide in-depth metadata, statistics, and technical specifications for models and datasets.

For information about searching across entities, see [Search Tools](#4.2.1). For information about managing and discovering Spaces, see [Space Management Tools](#4.2.3).

## Overview

The detail tools provide rich, structured information about individual Hugging Face Hub entities. The system currently includes two primary detail tools:

| Tool Name | Entity Type | Primary Class | Configuration |
|-----------|-------------|---------------|---------------|
| `model_details` | Models | `ModelDetailTool` | `MODEL_DETAIL_TOOL_CONFIG` |
| `dataset_details` | Datasets | `DatasetDetailTool` | `DATASET_DETAIL_TOOL_CONFIG` |

These tools integrate with the `@huggingface/hub` library to fetch comprehensive metadata and format it as structured markdown responses. Both tools support optional README content inclusion and provide both tool and prompt configurations for different use cases.

**Sources:** [packages/mcp/src/model-detail.ts:9-26](), [packages/mcp/src/dataset-detail.ts:8-20]()

## Tool Configuration Pattern

Each detail tool follows a consistent configuration pattern with Zod schema validation and MCP annotations:

```typescript
// Model Details Tool Configuration
{
  name: 'model_details',
  description: 'Get detailed information about a model from the Hugging Face Hub...',
  schema: z.object({
    model_id: z.string().min(1).describe('The Model ID in author/model format')
  }),
  annotations: {
    title: 'Model Details',
    destructiveHint: false,
    readOnlyHint: true,
    openWorldHint: false
  }
}
```

### Prompt Configurations

Both tools also provide prompt configurations that include README content by default. These are registered as MCP prompts and can be invoked using the `apply_prompt` method:

```mermaid
graph LR
    ToolConfig["MODEL_DETAIL_TOOL_CONFIG"]
    PromptConfig["MODEL_DETAIL_PROMPT_CONFIG"]
    
    ToolConfig -->|"name: model_details"| ToolInvocation["Direct tool call"]
    PromptConfig -->|"name: Model Details"| PromptInvocation["apply_prompt call"]
    
    ToolInvocation -->|"includeReadme: false"| Result["Basic details only"]
    PromptInvocation -->|"includeReadme: true"| ResultWithReadme["Details + README"]
```

**Sources:** [packages/mcp/src/model-detail.ts:9-40](), [packages/mcp/src/dataset-detail.ts:8-34](), [packages/e2e-python/prompts.py:20-21]()

## Data Extraction Architecture

### ModelDetailTool Architecture

The `ModelDetailTool` class implements a layered data extraction approach that safely handles optional fields from the Hugging Face API:

```mermaid
graph TB
    subgraph "API Layer"
        modelInfo["modelInfo() from @huggingface/hub"]
        additionalFields["additionalFields array:<br/>author, downloadsAllTime, library_name,<br/>tags, config, transformersInfo,<br/>safetensors, cardData, spaces,<br/>inferenceProviderMapping"]
    end
    
    subgraph "ModelDetailTool Class"
        constructor["constructor(hfToken?, hubUrl?)"]
        getDetails["getDetails(modelId, includeReadme)"]
    end
    
    subgraph "Data Structures"
        ModelBasicInfo["ModelBasicInfo<br/>Required: id, name, downloads,<br/>likes, private, gated, updatedAt"]
        ModelExtendedInfo["ModelExtendedInfo<br/>Optional: author, library_name,<br/>pipeline_tag, downloadsAllTime, tags"]
        ModelTechnicalDetails["ModelTechnicalDetails<br/>Optional: modelType, vocabSize,<br/>parameters, modelClass"]
        ModelMetadata["ModelMetadata<br/>Optional: language, license,<br/>datasets, fineTunedFrom"]
        InferenceProvider["InferenceProvider[]<br/>provider, status, providerId, task"]
    end
    
    subgraph "Output"
        ModelInformation["ModelInformation interface<br/>Combines all data layers"]
        formatModelDetails["formatModelDetails()<br/>Markdown formatter"]
        ToolResult["ToolResult<br/>formatted, totalResults, resultsShared"]
    end
    
    constructor --> getDetails
    getDetails --> modelInfo
    modelInfo --> additionalFields
    additionalFields --> ModelBasicInfo
    additionalFields --> ModelExtendedInfo
    additionalFields --> ModelTechnicalDetails
    additionalFields --> ModelMetadata
    additionalFields --> InferenceProvider
    
    ModelBasicInfo --> ModelInformation
    ModelExtendedInfo --> ModelInformation
    ModelTechnicalDetails --> ModelInformation
    ModelMetadata --> ModelInformation
    InferenceProvider --> ModelInformation
    
    ModelInformation --> formatModelDetails
    formatModelDetails --> ToolResult
```

The class extracts data through carefully validated type assertions:

**Technical Details Extraction:**
```typescript
// Safe extraction from config
if (modelData.config && typeof modelData.config === 'object') {
  const config = modelData.config as Record<string, unknown>;
  if ('model_type' in config && typeof config.model_type === 'string') {
    technical.modelType = config.model_type;
  }
  // vocab_size, etc.
}
```

**Inference Provider Extraction:**
```typescript
const inferenceProviders = (modelData.inferenceProviderMapping ?? [])
  .map((entry) => ({
    provider: entry.provider,
    status: entry.status,
    providerId: entry.providerId,
    task: entry.task,
  }))
  .filter((el) => !!el);
```

**Sources:** [packages/mcp/src/model-detail.ts:106-301](), [packages/mcp/src/model-detail.ts:44-101]()

### DatasetDetailTool Architecture

The `DatasetDetailTool` follows a similar pattern but focuses on dataset-specific metadata:

```mermaid
graph TB
    subgraph "API Layer"
        datasetInfo["datasetInfo() from @huggingface/hub"]
        additionalFields["additionalFields array:<br/>author, downloadsAllTime,<br/>tags, description, cardData"]
    end
    
    subgraph "DatasetDetailTool Class"
        constructor["constructor(hfToken?, hubUrl?)"]
        getDetails["getDetails(datasetId, includeReadme)"]
    end
    
    subgraph "Data Structures"
        DatasetBasicInfo["DatasetBasicInfo<br/>Required: id, name, downloads,<br/>likes, private, gated, updatedAt"]
        DatasetExtendedInfo["DatasetExtendedInfo<br/>Optional: author, downloadsAllTime,<br/>tags, description"]
        DatasetMetadata["DatasetMetadata<br/>Optional: language, license,<br/>task_categories, size_categories,<br/>dataset_info"]
    end
    
    subgraph "Output"
        DatasetInformation["DatasetInformation interface<br/>Combines all data layers"]
        formatDatasetDetails["formatDatasetDetails()<br/>Markdown formatter"]
        ToolResult["ToolResult<br/>formatted, totalResults, resultsShared"]
    end
    
    constructor --> getDetails
    getDetails --> datasetInfo
    datasetInfo --> additionalFields
    additionalFields --> DatasetBasicInfo
    additionalFields --> DatasetExtendedInfo
    additionalFields --> DatasetMetadata
    
    DatasetBasicInfo --> DatasetInformation
    DatasetExtendedInfo --> DatasetInformation
    DatasetMetadata --> DatasetInformation
    
    DatasetInformation --> formatDatasetDetails
    formatDatasetDetails --> ToolResult
```

**Sources:** [packages/mcp/src/dataset-detail.ts:77-206](), [packages/mcp/src/dataset-detail.ts:38-72]()

## Output Format Structure

### Model Details Output

The `formatModelDetails` function generates structured markdown with the following sections:

| Section | Condition | Content |
|---------|-----------|---------|
| Title | Always | Model name as H1 |
| Overview | Always | Author, task, library, downloads, likes, updated date, status |
| Technical Details | If available | Model class, parameters, architecture, vocab size |
| Tags | If available | Comma-separated tags in code blocks |
| Metadata | If available | Language, license, datasets, fine-tuned from |
| Demo Spaces | If available | Up to 12 spaces with links (limited by `SPACES_TO_INCLUDE`) |
| Inference Providers | If available | Provider names with status, playground link |
| Link | Always | Direct link to model on hf.co |

**Example Output Structure:**
```markdown
# author/model-name

## Overview
- **Author:** author-name
- **Task:** text-generation
- **Library:** transformers
- **Downloads:** 1,234,567 | **Likes:** 42
- **Updated:** Jan 15, 2024
- **Status:** 🔒 Gated

## Technical Details
- **Model Class:** AutoModelForCausalLM
- **Parameters:** 7,000,000,000
- **Architecture:** llama
- **Vocab Size:** 32,000

## Inference Providers
- **serverless** (ready)
Try this model in the playground...

**Link:** [https://hf.co/author/model-name]
```

**Sources:** [packages/mcp/src/model-detail.ts:304-462]()

### Dataset Details Output

The `formatDatasetDetails` function generates a similar structure tailored to datasets:

| Section | Condition | Content |
|---------|-----------|---------|
| Title | Always | Dataset name as H1 |
| Description | If available | Full description text |
| Overview | Always | Author, downloads, likes, updated date, status |
| Tags | If available | Comma-separated tags |
| Metadata | If available | Language, license, task categories, size categories |
| Link | Always | Direct link to dataset on hf.co |

**Sources:** [packages/mcp/src/dataset-detail.ts:209-310]()

## README Integration

Both tools support including README content from the repository's model card or dataset card. This is controlled by the `includeReadme` parameter:

```mermaid
graph LR
    getDetails["getDetails(id, includeReadme)"]
    fetchAPI["Fetch entity details<br/>from Hub API"]
    formatResult["formatDetails()<br/>Generate markdown"]
    
    checkReadme{"includeReadme<br/>== true?"}
    fetchReadme["fetchReadmeContent()<br/>from readme-utils.ts"]
    appendReadme["Append README section<br/>with XML-style tags"]
    
    getDetails --> fetchAPI
    fetchAPI --> formatResult
    formatResult --> checkReadme
    checkReadme -->|No| returnBasic["Return basic formatted result"]
    checkReadme -->|Yes| fetchReadme
    fetchReadme --> appendReadme
    appendReadme --> returnWithReadme["Return result + README"]
```

The README content is wrapped in XML-style tags for clear delineation:

```markdown
## README
<modelcard-readme>
[README content converted from HTML to Markdown]
</modelcard-readme>
```

or

```markdown
## README
<datasetcard-readme>
[README content converted from HTML to Markdown]
</datasetcard-readme>
```

**Sources:** [packages/mcp/src/model-detail.ts:261-268](), [packages/mcp/src/dataset-detail.ts:165-172]()

## Error Handling

Both tools implement comprehensive error handling with user-friendly messages:

```mermaid
graph TD
    apiCall["API call to modelInfo/datasetInfo"]
    catchError["Catch error"]
    
    checkType{"error instanceof<br/>Error?"}
    checkNotFound{"404 or<br/>Not Found?"}
    checkUnauthorized{"401/403 or<br/>Auth keywords?"}
    
    notFoundMsg["Throw: 'Model/Dataset not found.<br/>Please check the ID.'"]
    authMsg["Throw: 'Authentication required or<br/>insufficient permissions...'"]
    genericMsg["Throw: 'Failed to get details: {msg}'"]
    rethrow["Re-throw error"]
    
    apiCall --> catchError
    catchError --> checkType
    checkType -->|Yes| checkNotFound
    checkType -->|No| rethrow
    checkNotFound -->|Yes| notFoundMsg
    checkNotFound -->|No| checkUnauthorized
    checkUnauthorized -->|Yes| authMsg
    checkUnauthorized -->|No| genericMsg
```

**Error Detection Patterns:**

| Error Type | Detection Logic | User Message |
|------------|-----------------|--------------|
| Not Found | `HubApiError.statusCode === 404` OR message contains "404", "Not Found", "Repository not found" | `Model/Dataset '{id}' not found. Please check the ID.` |
| Unauthorized | `statusCode === 401/403` OR message contains "401", "403", "username", "password", "access token" | `Authentication required or insufficient permissions to access '{id}'.` |
| Generic | Any other error | `Failed to get model/dataset details: {message}` |

**Sources:** [packages/mcp/src/model-detail.ts:271-300](), [packages/mcp/src/dataset-detail.ts:176-205]()

## Tool Instantiation and Invocation

The detail tools are instantiated with optional authentication and custom hub URL:

```mermaid
graph LR
    subgraph "Tool Creation"
        params["Constructor Parameters"]
        hfToken["hfToken?: string"]
        hubUrl["hubUrl?: string"]
        
        params --> hfToken
        params --> hubUrl
    end
    
    subgraph "Tool Instance"
        ModelDetailTool["new ModelDetailTool(hfToken, hubUrl)"]
        accessToken["this.accessToken"]
        hubUrlField["this.hubUrl"]
    end
    
    subgraph "API Call Configuration"
        credentials["credentials: { accessToken }"]
        hubUrlOption["hubUrl: string"]
        modelInfoCall["modelInfo({<br/>name, additionalFields,<br/>credentials?, hubUrl?<br/>})"]
    end
    
    hfToken --> accessToken
    hubUrl --> hubUrlField
    
    accessToken -->|If present| credentials
    hubUrlField -->|If present| hubUrlOption
    
    credentials --> modelInfoCall
    hubUrlOption --> modelInfoCall
```

**Invocation Flow:**

1. MCP client calls tool with entity ID parameter
2. Tool extracts `model_id` or `dataset_id` from request
3. `getDetails()` method called with ID and optional `includeReadme` flag
4. API call made with configured authentication
5. Response data extracted into typed interfaces
6. Markdown formatted via `formatModelDetails()` or `formatDatasetDetails()`
7. `ToolResult` returned with `formatted` string, `totalResults: 1`, `resultsShared: 1`

**Sources:** [packages/mcp/src/model-detail.ts:106-118](), [packages/mcp/src/dataset-detail.ts:77-89]()

## Usage Examples

### Tool Invocation

Direct tool calls request basic details without README:

```python
# Direct tool call - basic details only
await agent.call_tool("model_details", {"model_id": "microsoft/DialoGPT-large"})
await agent.call_tool("dataset_details", {"dataset_id": "squad"})
```

### Prompt Application

Prompt invocation includes README content automatically:

```python
# Prompt application - includes README
await agent.apply_prompt("Model Details", {"model_id": "openai/gpt-oss-120b"})
await agent.apply_prompt("Dataset Details", {"dataset_id": "Anthropic/hh-rlhf"})
```

**Sources:** [packages/e2e-python/prompts.py:20-21]()

## Field Extraction Details

### Model-Specific Fields

The `ModelDetailTool` extracts specialized fields not available for datasets:

| Field Path | Interface | Extraction Method | Example Value |
|------------|-----------|-------------------|---------------|
| `config.model_type` | `ModelTechnicalDetails.modelType` | Type check and cast | `"llama"` |
| `config.vocab_size` | `ModelTechnicalDetails.vocabSize` | Type check and cast | `32000` |
| `safetensors.total` | `ModelTechnicalDetails.parameters` | Direct numeric access | `7000000000` |
| `transformersInfo.auto_model` | `ModelTechnicalDetails.modelClass` | Direct string access | `"AutoModelForCausalLM"` |
| `inferenceProviderMapping` | `inferenceProviders[]` | Array mapping | `[{provider: "serverless", status: "ready"}]` |
| `spaces` | `spaces[]` | Array mapping with ID parsing | `[{id: "user/space", name: "space"}]` |

### Dataset-Specific Fields

The `DatasetDetailTool` extracts fields relevant to datasets:

| Field Path | Interface | Extraction Method | Example Value |
|------------|-----------|-------------------|---------------|
| `description` | `DatasetExtendedInfo.description` | Direct string access | `"A reading comprehension dataset..."` |
| `cardData.task_categories` | `DatasetMetadata.task_categories` | Cast to string or array | `["question-answering"]` |
| `cardData.size_categories` | `DatasetMetadata.size_categories` | Cast to string or array | `["10K<n<100K"]` |
| `cardData.dataset_info` | `DatasetMetadata.dataset_info` | Cast to Record | `{features: [...], splits: [...]}` |

**Sources:** [packages/mcp/src/model-detail.ts:184-258](), [packages/mcp/src/dataset-detail.ts:130-159]()

## Integration with Tool Selection

Detail tools are included in multiple bouquets:

- **`hf_api` bouquet:** Both `model_details` and `dataset_details`
- **`search` bouquet:** Both tools (paired with search capabilities)
- **`all` bouquet:** All tools including detail tools

When selected via the Tool Selection Strategy (see [Tool Selection Strategy](#5.2)), these tools become available for invocation by MCP clients. The README inclusion behavior differs between tool and prompt invocations, allowing clients to choose between compact responses and comprehensive documentation.

**Sources:** Based on tool configuration and bouquet system described in architecture diagrams

---

# Page: Space Management Tools

# Space Management Tools

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.dockerignore](.dockerignore)
- [Dockerfile](Dockerfile)
- [README.md](README.md)
- [packages/app/src/server/mcp-server.ts](packages/app/src/server/mcp-server.ts)
- [packages/app/src/shared/settings.ts](packages/app/src/shared/settings.ts)
- [packages/app/src/web/App.tsx](packages/app/src/web/App.tsx)
- [packages/app/vite.config.ts](packages/app/vite.config.ts)
- [packages/mcp/src/duplicate-space.ts](packages/mcp/src/duplicate-space.ts)
- [packages/mcp/src/error-messages.ts](packages/mcp/src/error-messages.ts)
- [start.sh](start.sh)

</details>



## Purpose and Scope

This document describes the space management tools provided by the HF MCP Server. These tools enable AI clients to interact with Hugging Face Spaces - both static operations (duplicating, inspecting, listing files) and dynamic invocation of Gradio applications. This page covers four built-in tools: `duplicate_space`, `space_info`, `space_files`, and `use_space`.

For information about searching for spaces, see [Search Tools](#4.2.1). For dynamic Gradio tool discovery and proxied execution, see [Gradio Integration](#6).

---

## Overview

Space management tools allow clients to:

1. **Duplicate existing spaces** to the authenticated user's account
2. **Inspect space metadata** including runtime configuration and hardware
3. **List files** in static spaces with download URLs
4. **Dynamically invoke Gradio spaces** without pre-registration

All space management tools except `duplicate_space` and `space_files` work for both authenticated and anonymous users. The `duplicate_space` tool requires authentication since it creates resources in the user's account. The `space_files` tool requires authentication to access the space's file tree.

Sources: [packages/app/src/server/mcp-server.ts:602-670](), [packages/mcp/src/duplicate-space.ts:1-264]()

---

## Tool Registration Architecture

### Registration Flow

```mermaid
graph TB
    ServerFactory["createServerFactory()<br/>mcp-server.ts:96"]
    McpServer["McpServer instance<br/>SDK McpServer"]
    
    subgraph "Tool Configuration"
        DupConfig["DUPLICATE_SPACE_TOOL_CONFIG<br/>duplicate-space.ts:42"]
        InfoConfig["SpaceInfoTool.createToolConfig()<br/>Dynamic config with username"]
        FilesConfig["SpaceFilesTool.createToolConfig()<br/>Dynamic config with username"]
        UseConfig["USE_SPACE_TOOL_CONFIG<br/>mcp-server.ts:39"]
    end
    
    subgraph "Tool Implementation"
        DupTool["DuplicateSpaceTool<br/>duplicate-space.ts:74"]
        InfoTool["SpaceInfoTool<br/>From @llmindset/hf-mcp"]
        FilesTool["SpaceFilesTool<br/>From @llmindset/hf-mcp"]
        UseTool["UseSpaceTool<br/>From @llmindset/hf-mcp"]
    end
    
    subgraph "Tool State Management"
        ToolInstances["toolInstances map<br/>mcp-server.ts:191"]
        ApplyStates["applyToolStates()<br/>mcp-server.ts:839"]
        Selection["ToolSelectionStrategy<br/>Determines enabled tools"]
    end
    
    ServerFactory -->|"Creates with auth"| McpServer
    ServerFactory -->|"Checks token"| DupConfig
    ServerFactory -->|"username from whoAmI"| InfoConfig
    ServerFactory -->|"username from whoAmI"| FilesConfig
    
    DupConfig -->|"server.tool()"| McpServer
    InfoConfig -->|"server.tool()"| McpServer
    FilesConfig -->|"server.tool()"| McpServer
    UseConfig -->|"server.tool()"| McpServer
    
    McpServer -->|"Instantiates on call"| DupTool
    McpServer -->|"Instantiates on call"| InfoTool
    McpServer -->|"Instantiates on call"| FilesTool
    McpServer -->|"Instantiates on call"| UseTool
    
    McpServer -->|"Stores Tool refs"| ToolInstances
    Selection -->|"Determines enabled"| ApplyStates
    ApplyStates -->|"enable/disable"| ToolInstances
```

**Diagram: Space Tool Registration and State Management**

The space management tools follow the standard MCP tool registration pattern. The `duplicate_space`, `space_info`, and `space_files` tools generate their descriptions dynamically based on whether the user is authenticated. If a valid `hfToken` is present and `whoAmI` succeeds, the tool configurations include the username in their descriptions.

Sources: [packages/app/src/server/mcp-server.ts:96-220](), [packages/app/src/server/mcp-server.ts:602-670](), [packages/mcp/src/duplicate-space.ts:82-92]()

---

## duplicate_space Tool

### Purpose

The `duplicate_space` tool creates a copy of an existing Hugging Face Space in the authenticated user's account. This is useful for:

- Forking community spaces for customization
- Creating private versions of public spaces
- Testing modified configurations
- Migrating spaces between hardware tiers

### Configuration and Schema

The tool is defined by `DUPLICATE_SPACE_TOOL_CONFIG` with the following schema:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `sourceSpaceId` | string | Yes | Space ID to copy (e.g., 'username/space-name') |
| `newSpaceId` | string | No | Name for new space (defaults to source space name) |
| `hardware` | enum | No | Either "freecpu" or "zerogpu" (auto-detects from source) |
| `private` | boolean | No | Visibility (defaults to true) |

The tool schema is defined at [packages/mcp/src/duplicate-space.ts:42-64]() and includes annotations:

```typescript
annotations: {
  title: 'Duplicate Hugging Face Space',
  destructiveHint: false,
  readOnlyHint: false,
  openWorldHint: true,
}
```

The `openWorldHint: true` indicates the tool creates new resources, alerting clients that this is a write operation.

Sources: [packages/mcp/src/duplicate-space.ts:42-64]()

### Implementation: DuplicateSpaceTool Class

```mermaid
graph TB
    DupTool["DuplicateSpaceTool<br/>extends HfApiCall"]
    
    subgraph "Constructor"
        Init["constructor(hfToken, username)<br/>duplicate-space.ts:77"]
    end
    
    subgraph "Validation Methods"
        Normalize["normalizeSpaceName()<br/>duplicate-space.ts:94"]
        GetInfo["getSpaceInfo()<br/>duplicate-space.ts:109"]
        GetVars["getSpaceVariables()<br/>duplicate-space.ts:114"]
    end
    
    subgraph "Main Operation"
        Duplicate["duplicate()<br/>duplicate-space.ts:124"]
    end
    
    subgraph "Hardware Logic"
        HardwareMap["HARDWARE_MAP<br/>freecpu → cpu-basic<br/>zerogpu → zero-a10g"]
        FreeCheck["FREE_HARDWARE array<br/>duplicate-space.ts:72"]
    end
    
    subgraph "API Interactions"
        GetSpaceAPI["GET /api/spaces/{id}"]
        GetVarsAPI["GET /api/spaces/{id}/variables"]
        PostDupAPI["POST /api/spaces/{id}/duplicate"]
    end
    
    DupTool -->|"Uses"| Init
    Init -->|"Stores"| HfApiCall["HfApiCall base class"]
    
    Duplicate -->|"Step 1"| GetInfo
    Duplicate -->|"Step 2"| GetVars
    Duplicate -->|"Step 3"| HardwareMap
    Duplicate -->|"Step 4"| Normalize
    Duplicate -->|"Step 6"| PostDupAPI
    
    GetInfo -->|"Fetches"| GetSpaceAPI
    GetVars -->|"Fetches"| GetVarsAPI
    
    HardwareMap -->|"Checks against"| FreeCheck
```

**Diagram: DuplicateSpaceTool Implementation Flow**

The `DuplicateSpaceTool` class at [packages/mcp/src/duplicate-space.ts:74-259]() extends `HfApiCall` to inherit authentication and error handling. The duplication process follows these steps:

1. **Fetch source space info** via `getSpaceInfo()` to access runtime configuration
2. **Retrieve space variables** via `getSpaceVariables()` to copy environment settings
3. **Determine hardware tier** using `HARDWARE_MAP` and source space configuration
4. **Normalize target space ID** to ensure proper namespace (`username/space-name`)
5. **Check for warnings** regarding paid hardware or gated models
6. **Execute duplication** via POST to `/api/spaces/{id}/duplicate`

Sources: [packages/mcp/src/duplicate-space.ts:74-236]()

### Hardware Selection Logic

```mermaid
graph LR
    Start["Hardware selection"]
    UserSpecified{"User specified<br/>hardware param?"}
    UseUserChoice["Use user's choice<br/>freecpu or zerogpu"]
    
    CheckSource{"Source hardware?"}
    IsZeroGPU{"Is zero-a10g?"}
    IsCPU{"Is cpu-basic<br/>or undefined?"}
    
    UseZeroGPU["Select: zerogpu<br/>(zero-a10g)"]
    UseCPU["Select: freecpu<br/>(cpu-basic)"]
    DefaultZeroGPU["Default: zerogpu<br/>(paid hardware detected)"]
    
    CheckPaid{"Source is<br/>paid hardware?"}
    AddWarning["Add hardware<br/>warning to result"]
    
    Start --> UserSpecified
    UserSpecified -->|Yes| UseUserChoice
    UserSpecified -->|No| CheckSource
    
    CheckSource --> IsZeroGPU
    IsZeroGPU -->|Yes| UseZeroGPU
    IsZeroGPU -->|No| IsCPU
    
    IsCPU -->|Yes| UseCPU
    IsCPU -->|No| DefaultZeroGPU
    
    UseUserChoice --> CheckPaid
    UseZeroGPU --> CheckPaid
    UseCPU --> CheckPaid
    DefaultZeroGPU --> CheckPaid
    
    CheckPaid -->|Yes| AddWarning
    CheckPaid -->|No| Done["Complete"]
    AddWarning --> Done
```

**Diagram: Hardware Tier Selection Algorithm**

The hardware selection logic at [packages/mcp/src/duplicate-space.ts:156-192]() handles three cases:

1. **User-specified hardware**: Direct mapping via `HARDWARE_MAP` constant
2. **Auto-detection from source**: Preserves `zero-a10g` or `cpu-basic`
3. **Paid hardware fallback**: Defaults to `zerogpu` with warning

The `FREE_HARDWARE` array at [packages/mcp/src/duplicate-space.ts:72]() defines which hardware tiers are in the free tier. If the source uses paid hardware, a warning is included in the result instructing the user to upgrade if needed.

Sources: [packages/mcp/src/duplicate-space.ts:156-192](), [packages/mcp/src/duplicate-space.ts:66-72]()

### Response Format

The tool returns a `DuplicateSpaceResult` object that is formatted by `formatDuplicateResult()` at [packages/mcp/src/duplicate-space.ts:261-263](). The formatted response includes:

- **URL**: Direct link to the new space
- **Configuration summary**: Hardware tier and visibility
- **Variable count**: Number of environment variables copied
- **Setup instructions**: Step-by-step guide to configure the space
- **Warnings**: Hardware compatibility or gated model notices

Example response structure:
```
✅ 🤗 Space successfully duplicated! 

🔗 Your new space: https://huggingface.co/spaces/username/space-name

⚙️ To configure your space:
1. Go to https://huggingface.co/spaces/username/space-name
2. Click on 'Settings' in the top right
3. Configure any additional settings as needed

Hardware: zerogpu | Visibility: Private

⚠️ Warnings:
- Note: The source space uses 'a10g-large' which is paid hardware...
```

Sources: [packages/mcp/src/duplicate-space.ts:218-258](), [packages/mcp/src/duplicate-space.ts:261-263]()

### Error Handling

The tool uses the `explain()` function from [packages/mcp/src/error-messages.ts:48-57]() to enhance error messages. Common error scenarios:

| Status | Explanation |
|--------|-------------|
| 400 | Invalid request - check token permissions or space quota |
| 401 | Authentication failed - invalid token |
| 403 | Permission denied - check token scopes |
| 404 | Source space does not exist |
| 409 | Space with target name already exists |
| 429 | Rate limit exceeded |

The `FRIENDLY_ERROR_EXPLANATIONS` at [packages/mcp/src/error-messages.ts:10-21]() provides user-friendly messages for each status code.

Sources: [packages/mcp/src/error-messages.ts:10-57](), [packages/mcp/src/duplicate-space.ts:129-235]()

---

## space_info Tool

### Purpose

The `space_info` tool retrieves comprehensive metadata about a Hugging Face Space, including runtime configuration, hardware allocation, and operational status. This tool is read-only and works for both authenticated and anonymous users.

### Configuration

The tool configuration is generated dynamically by `SpaceInfoTool.createToolConfig()` based on authentication status. When authenticated, the description includes the username to clarify which account's spaces can be managed.

Tool registration occurs at [packages/app/src/server/mcp-server.ts:617-630]() with these annotations:

```typescript
annotations: {
  title: 'Space Info',
  readOnlyHint: true,
  openWorldHint: false,
}
```

Sources: [packages/app/src/server/mcp-server.ts:617-630]()

### Implementation

The `SpaceInfoTool` class is imported from `@llmindset/hf-mcp` package. The tool:

1. Accepts a `space_id` parameter (e.g., `username/space-name`)
2. Calls the Hugging Face API to retrieve space metadata
3. Formats the result using `formatSpaceInfoResult()` helper
4. Returns structured information about the space

The tool handler at [packages/app/src/server/mcp-server.ts:624-628]() instantiates `SpaceInfoTool` with the user's token and username, then delegates to the formatting function.

Sources: [packages/app/src/server/mcp-server.ts:617-630]()

---

## space_files Tool

### Purpose

The `space_files` tool lists all files in a static Hugging Face Space with their download URLs. This is useful for:

- Inspecting space contents before duplication
- Downloading specific assets from a space
- Understanding space structure and dependencies
- Programmatic access to space artifacts

### Configuration and Schema

The tool schema requires:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `space_id` | string | Yes | Space ID to inspect (e.g., 'username/space-name') |

Like `space_info`, this tool's configuration is generated dynamically by `SpaceFilesTool.createToolConfig()` and includes authentication-aware descriptions.

Tool annotations:
```typescript
annotations: {
  title: 'Space Files',
  readOnlyHint: true,
  openWorldHint: false,
}
```

Sources: [packages/app/src/server/mcp-server.ts:632-645]()

### Implementation

The tool is registered at [packages/app/src/server/mcp-server.ts:632-645]() and follows this flow:

1. Instantiate `SpaceFilesTool` with token and username
2. Call `listFiles()` method with the space ID parameter
3. Return formatted list of files with download URLs

The `SpaceFilesTool` class handles API interaction and response formatting internally.

Sources: [packages/app/src/server/mcp-server.ts:632-645]()

---

## use_space Tool (Dynamic Invocation)

### Purpose

The `use_space` tool is a special dynamic tool that allows invocation of Gradio spaces without pre-registration. Unlike the proxied Gradio tools (e.g., `gr1_tool`, `gr2_tool`) which are discovered and registered at server startup, `use_space` enables on-demand invocation of any Gradio space.

This tool supports two operations:
1. **view_parameters**: Inspect the tool schema for a Gradio space
2. **invoke**: Execute a Gradio endpoint with provided arguments

For comprehensive Gradio integration architecture, see [Gradio Integration](#6).

Sources: [packages/app/src/server/mcp-server.ts:647-815]()

### Configuration and Schema

```mermaid
graph TB
    Config["USE_SPACE_TOOL_CONFIG<br/>mcp-server.ts:39"]
    Schema["Zod Schema<br/>Dynamic based on operation"]
    
    subgraph "Schema Fields"
        SpaceName["space_name: string<br/>Required"]
        Operation["operation: enum<br/>'view_parameters' | 'invoke'"]
        ApiName["api_name?: string<br/>Optional endpoint"]
        Args["args?: Record<br/>Dynamic arguments"]
    end
    
    subgraph "Annotations"
        Title["title: 'Use Space'"]
        Hints["destructiveHint: false<br/>readOnlyHint: false<br/>openWorldHint: true"]
    end
    
    Config --> Schema
    Schema --> SpaceName
    Schema --> Operation
    Schema --> ApiName
    Schema --> Args
    
    Config --> Title
    Config --> Hints
```

**Diagram: use_space Tool Configuration Structure**

The tool is registered at [packages/app/src/server/mcp-server.ts:647-815]() with `DYNAMIC_SPACE_TOOL_CONFIG` (also referenced as `USE_SPACE_TOOL_CONFIG`). The schema allows both parameter inspection and invocation operations.

Sources: [packages/app/src/server/mcp-server.ts:38-40](), [packages/app/src/server/mcp-server.ts:647-670]()

### Operation Flow

```mermaid
sequenceDiagram
    participant Client
    participant Handler["use_space handler<br/>mcp-server.ts:704"]
    participant SpaceTool["SpaceTool instance<br/>From @llmindset/hf-mcp"]
    participant GradioCheck["gradio header check<br/>mcp-server.ts:706"]
    participant PostProcess["applyResultPostProcessing<br/>gradio-tool-caller.ts"]
    participant Logger["logGradioEvent"]
    
    Client->>Handler: tools/call use_space
    Handler->>GradioCheck: Check if gradio=none
    
    alt gradio=none and operation=invoke
        GradioCheck-->>Client: Error: invoke disabled
    else gradio allowed
        Handler->>SpaceTool: execute(params)
        
        alt operation=view_parameters
            SpaceTool-->>Handler: ToolResult (formatted schema)
            Handler->>Logger: logSearchQuery (view operation)
            Handler-->>Client: Text response
        else operation=invoke
            SpaceTool-->>Handler: InvokeResult (raw MCP content)
            Handler->>PostProcess: Strip images if needed
            PostProcess->>PostProcess: Apply OpenAI transforms
            PostProcess-->>Handler: Processed content
            Handler->>Logger: logGradioEvent (with metrics)
            Handler-->>Client: Content array with images/text
        end
    end
```

**Diagram: use_space Execution Flow**

The tool handler at [packages/app/src/server/mcp-server.ts:704-814]() implements a sophisticated flow:

1. **Check gradio header**: If `gradio=none`, reject invoke operations
2. **Execute via SpaceTool**: Delegate to `@llmindset/hf-mcp` implementation
3. **Branch on result type**:
   - `InvokeResult`: Raw MCP content from Gradio (needs post-processing)
   - `ToolResult`: Formatted text (for view_parameters)
4. **Post-process invoke results**: Apply image filtering and OpenAI transforms
5. **Log metrics**: Track invocation performance and success

Sources: [packages/app/src/server/mcp-server.ts:704-814]()

### Post-Processing Pipeline

The invoke operation applies `applyResultPostProcessing()` from [packages/app/src/server/utils/gradio-tool-caller.ts]() with these options:

```typescript
const postProcessOptions: GradioToolCallOptions = {
  stripImageContent: noImageContentHeaderEnabled || 
                     toolSelection.enabledToolIds.includes('NO_GRADIO_IMAGE_CONTENT'),
  toolName: DYNAMIC_SPACE_TOOL_CONFIG.name,
  outwardFacingName: DYNAMIC_SPACE_TOOL_CONFIG.name,
  sessionInfo,
  spaceName: params.space_name,
};
```

This unified post-processing at [packages/app/src/server/mcp-server.ts:731-745]() handles:

- **Image filtering**: Removes image content if `x-mcp-no-image-content: true` header or `NO_GRADIO_IMAGE_CONTENT` flag is set
- **OpenAI transformations**: Converts MCP content format to OpenAI-compatible structured content (for skybridge clients)
- **Warning prepending**: Adds any warnings from the invocation to the response

Sources: [packages/app/src/server/mcp-server.ts:731-759](), [packages/app/src/server/utils/gradio-tool-caller.ts:76]()

### Gradio Header Control

The tool respects the `gradio` header value for access control:

| Header Value | Behavior |
|--------------|----------|
| Not set | Invoke allowed |
| Space IDs | Invoke allowed |
| `none` | **Invoke blocked**, view_parameters still allowed |

The check at [packages/app/src/server/mcp-server.ts:706-716]() prevents invocation when `gradio=none` is set:

```typescript
if (params.operation === 'invoke' && gradio === 'none') {
  return {
    content: [{ type: 'text', text: errorMessage }],
    isError: true,
  };
}
```

This allows users to disable Gradio invocations while still enabling parameter inspection.

Sources: [packages/app/src/server/mcp-server.ts:706-716](), [packages/app/src/server/utils/auth-utils.ts:1-50]()

### Metrics and Logging

The tool uses different logging approaches based on operation:

**For invoke operations** (line [packages/app/src/server/mcp-server.ts:762-773]()):
- Logs via `logGradioEvent()` with timing metrics
- Tracks duration, authentication status, client info
- Records response size and success/failure
- Marks as `isDynamic: true` to distinguish from proxied tools

**For view_parameters operations** (line [packages/app/src/server/mcp-server.ts:785-791]()):
- Logs via `logSearchQuery()` for consistency with other inspection tools
- Records operation type and parameter details

Sources: [packages/app/src/server/mcp-server.ts:762-791](), [packages/app/src/server/utils/query-logger.ts:69](), [packages/app/src/server/utils/gradio-tool-caller.ts:1-200]()

### Error Handling

The tool has two error handling paths:

1. **Operation-level errors** (try-catch at [packages/app/src/server/mcp-server.ts:797-813]()):
   - Logs Gradio event for invoke failures
   - Includes error details in metrics
   - Re-throws for MCP protocol error handling

2. **Validation errors** (inline at [packages/app/src/server/mcp-server.ts:706-716]()):
   - Returns error content with `isError: true`
   - Provides user-facing guidance

Sources: [packages/app/src/server/mcp-server.ts:706-813]()

---

## UI Configuration

### Web Dashboard Integration

The space management tools appear in the web dashboard's "Spaces" tab. The configuration is defined at [packages/app/src/web/App.tsx:289-311]():

```typescript
const spaceTools = {
  duplicate_space: {
    id: DUPLICATE_SPACE_TOOL_ID,
    label: DUPLICATE_SPACE_TOOL_CONFIG.annotations.title,
    description: DUPLICATE_SPACE_TOOL_CONFIG.description,
    settings: { enabled: settings?.builtInTools?.includes(DUPLICATE_SPACE_TOOL_ID) ?? true },
  },
  space_files: {
    id: SPACE_FILES_TOOL_ID,
    label: SPACE_FILES_TOOL_CONFIG.annotations.title,
    description: SPACE_FILES_TOOL_CONFIG.description,
    settings: { enabled: settings?.builtInTools?.includes(SPACE_FILES_TOOL_ID) ?? true },
  },
  no_gradio_images: {
    id: GRADIO_IMAGE_FILTER_FLAG,
    label: 'Disable Gradio Images (flag)',
    description: 'Strips image responses from Gradio spaces...',
    settings: { enabled: gradioImageFilterEnabled },
  },
};
```

Users can toggle these tools on/off, triggering API calls to update settings and sending `toolStateChange` events to all connected MCP server instances.

Sources: [packages/app/src/web/App.tsx:289-367]()

### Tool Selection and Bouquets

Space management tools are included in specific bouquet presets:

| Bouquet | Includes |
|---------|----------|
| `spaces` | `duplicate_space`, `space_info`, `space_files`, `use_space`, `space_semantic_search` |
| `hf_api` | `duplicate_space`, `space_info`, `space_files` |
| `all` | All space tools |

The bouquet system is documented in [Tool Selection System](#5).

Sources: [packages/app/src/server/utils/tool-selection-strategy.ts:1-300]()

---

## Authentication Requirements

### Tool-by-Tool Requirements

| Tool | Requires Auth | Reason |
|------|---------------|--------|
| `duplicate_space` | ✅ Yes | Creates resources in user's account |
| `space_info` | ❌ No | Read-only inspection |
| `space_files` | ✅ Yes | Accesses file tree (may include private info) |
| `use_space` | ❌ No* | *May be required by individual Gradio spaces |

The `duplicate_space` tool checks for authentication at initialization ([packages/mcp/src/duplicate-space.ts:127]()) and returns a clear error message if no token is present:

```typescript
if (!this.username) throw new Error(NO_TOKEN_INSTRUCTIONS);
```

The `NO_TOKEN_INSTRUCTIONS` constant provides user-facing guidance on setting up authentication.

Sources: [packages/mcp/src/duplicate-space.ts:77-127](), [packages/mcp/src/utilities.ts:1-50]()

### Dynamic Description Updates

The tool descriptions adapt based on authentication:

```mermaid
graph LR
    whoAmI["whoAmI(hfToken)<br/>mcp-server.ts:126"]
    Success["Username extracted"]
    Failure["Anonymous user"]
    
    CreateConfig["createToolConfig(username)<br/>duplicate-space.ts:82"]
    
    AuthDesc["Description includes:<br/>'Target space will be<br/>created as {username}/...'"]
    AnonDesc["Description is:<br/>NO_TOKEN_INSTRUCTIONS"]
    
    whoAmI -->|200 OK| Success
    whoAmI -->|Error| Failure
    
    Success -->|username param| CreateConfig
    Failure -->|undefined| CreateConfig
    
    CreateConfig -->|Has username| AuthDesc
    CreateConfig -->|No username| AnonDesc
```

**Diagram: Dynamic Tool Description Generation**

This pattern appears in all username-aware space tools (`duplicate_space`, `space_info`, `space_files`) at their respective `createToolConfig()` methods.

Sources: [packages/app/src/server/mcp-server.ts:124-133](), [packages/mcp/src/duplicate-space.ts:82-92]()

---

## Relationship to Gradio Integration

The space management tools complement but differ from the Gradio integration system:

| Aspect | Space Management Tools | Gradio Integration |
|--------|----------------------|-------------------|
| Registration | Static, always available | Dynamic, discovered at runtime |
| Purpose | Manage space lifecycle | Invoke Gradio endpoints |
| Examples | `duplicate_space`, `space_info` | `gr1_flux_schnell`, `gr2_tool` |
| Authentication | Per-tool requirements | Inherited from space |
| Configuration | Via tool selection | Via `x-mcp-gradio` header or user settings |

The `use_space` tool bridges these systems by providing dynamic invocation without requiring pre-registration. For detailed Gradio tool discovery and proxying, see [Gradio Integration](#6).

Sources: [packages/app/src/server/mcp-server.ts:602-815]()

---

# Page: Documentation Tools

# Documentation Tools

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [packages/app/src/shared/constants.ts](packages/app/src/shared/constants.ts)
- [packages/mcp/src/docs-search/doc-fetch.test.ts](packages/mcp/src/docs-search/doc-fetch.test.ts)
- [packages/mcp/src/docs-search/doc-fetch.ts](packages/mcp/src/docs-search/doc-fetch.ts)
- [packages/mcp/src/docs-search/docs-semantic-search.test.ts](packages/mcp/src/docs-search/docs-semantic-search.test.ts)
- [packages/mcp/src/docs-search/docs-semantic-search.ts](packages/mcp/src/docs-search/docs-semantic-search.ts)

</details>



This page describes the two built-in documentation tools that enable AI clients to discover and retrieve content from Hugging Face and Gradio documentation. These tools provide semantic search capabilities and HTML-to-Markdown conversion for documentation consumption.

For information about other tool categories, see [Search Tools](#4.2.1), [Detail Tools](#4.2.2), and [Space Management Tools](#4.2.3). For the overall tool system architecture, see [Tool System Overview](#4.1).

---

## Overview

The documentation tools consist of two complementary MCP tools:

1. **`hf_doc_search`** - Semantic search over Hugging Face documentation libraries
2. **`hf_doc_fetch`** - Fetch and convert documentation pages to Markdown

These tools work together in a discovery-then-retrieval pattern. The search tool identifies relevant documentation pages, and the fetch tool retrieves their full content with clean Markdown formatting.

### Supported Documentation Sources

Both tools support:
- Hugging Face documentation (`huggingface.co/docs/*`)
- Gradio documentation (`gradio.app` and `www.gradio.app`)

Sources: [packages/mcp/src/docs-search/doc-fetch.ts:1-243](), [packages/mcp/src/docs-search/docs-semantic-search.ts:1-379]()

---

## Tool Architecture

```mermaid
graph TB
    subgraph "Documentation Tools"
        Search["DocSearchTool"]
        Fetch["DocFetchTool"]
        
        SearchConfig["DOCS_SEMANTIC_SEARCH_CONFIG<br/>name: hf_doc_search<br/>schema: query, product"]
        FetchConfig["DOC_FETCH_CONFIG<br/>name: hf_doc_fetch<br/>schema: doc_url, offset"]
    end
    
    subgraph "Base Classes"
        HfApiCall["HfApiCall&lt;ApiParams, ApiResult&gt;<br/>Base HTTP client"]
        TurndownService["TurndownService<br/>HTML to Markdown converter"]
    end
    
    subgraph "External Services"
        DocsAPI["https://hf.co/api/docs/search<br/>Semantic search endpoint"]
        DocsIndex["https://huggingface.co/api/docs<br/>Documentation index"]
        DocPages["Documentation Pages<br/>HTML content"]
    end
    
    subgraph "Utilities"
        estimateTokens["estimateTokens()<br/>Token counting"]
        escapeMarkdown["escapeMarkdown()<br/>String escaping"]
        normalizeDocUrl["normalizeDocUrl()<br/>URL normalization"]
    end
    
    SearchConfig -.defines.- Search
    FetchConfig -.defines.- Fetch
    
    Search --> HfApiCall
    Search --> DocsAPI
    Search --> DocsIndex
    Search --> estimateTokens
    Search --> escapeMarkdown
    
    Fetch --> TurndownService
    Fetch --> DocPages
    Fetch --> normalizeDocUrl
    Fetch --> estimateTokens
    
    Search -.suggests URLs.- Fetch
```

**Tool Discovery and Retrieval Flow**

The tools implement a two-phase workflow where search results include URLs that can be passed to the fetch tool.

Sources: [packages/mcp/src/docs-search/doc-fetch.ts:5-23](), [packages/mcp/src/docs-search/docs-semantic-search.ts:10-45]()

---

## Documentation Search Tool

The `DocSearchTool` class implements the `hf_doc_search` tool, providing semantic search over Hugging Face and Gradio documentation libraries.

### Configuration

| Property | Type | Description |
|----------|------|-------------|
| `name` | string | `hf_doc_search` |
| `query` | string | Search query (0-200 chars). Empty string returns documentation index |
| `product` | string (optional) | Filter by product name (e.g. "transformers", "hub") |
| Token budget | number | Default: 12,500 tokens |

The tool schema enforces a minimum query length of 3 characters for searches, but allows empty queries for discovering the documentation structure.

Sources: [packages/mcp/src/docs-search/docs-semantic-search.ts:10-45](), [packages/mcp/src/docs-search/docs-semantic-search.ts:69-71]()

### Search Behavior

```mermaid
sequenceDiagram
    participant Client
    participant DocSearchTool
    participant DocsIndex as "Documentation Index API"
    participant SearchAPI as "Search API"
    participant Formatter as "Result Formatter"
    
    alt Empty Query
        Client->>DocSearchTool: search({query: ""})
        DocSearchTool->>DocsIndex: GET /api/docs
        DocsIndex-->>DocSearchTool: DocsIndexEntry[]
        DocSearchTool->>Formatter: formatDocsIndex()
        Formatter-->>Client: Product table + llms.txt note
    else Semantic Query
        Client->>DocSearchTool: search({query: "rate limits", product: "hub"})
        DocSearchTool->>SearchAPI: GET /api/docs/search?q=rate+limits&product=hub
        SearchAPI-->>DocSearchTool: DocSearchResult[]
        DocSearchTool->>Formatter: formatSearchResults()
        Formatter->>Formatter: groupResults()<br/>Sort by product and page
        Formatter->>Formatter: groupBySection()<br/>Group by heading2
        Formatter->>Formatter: Check token budget<br/>Truncate or link-only
        Formatter-->>Client: Formatted markdown results
    end
```

**Empty Query Response**

When the query is empty, the tool returns a table of available documentation products:

```markdown
### Hugging Face Documentation Products
| Product | Category | Documentation |
| --- | --- | --- |
| `transformers` | Machine Learning | https://huggingface.co/docs/transformers |
| `datasets` | Machine Learning | https://huggingface.co/docs/datasets |
...
```

This response includes a note about `llms.txt` endpoints for each documentation root.

Sources: [packages/mcp/src/docs-search/docs-semantic-search.ts:94-127](), [packages/mcp/src/docs-search/docs-semantic-search.ts:162-190]()

### Result Grouping and Formatting

The tool implements a sophisticated multi-level grouping system:

```mermaid
graph TD
    Results["Raw Search Results<br/>DocSearchResult[]"]
    
    Results --> GroupByProduct["groupResults()<br/>Group by product"]
    
    GroupByProduct --> SortProducts["Sort Products<br/>By total result count"]
    
    SortProducts --> GroupByPage["Group by Page URL<br/>Strip anchors"]
    
    GroupByPage --> SortPages["Sort Pages<br/>By result count per page"]
    
    SortPages --> GroupBySection["groupBySection()<br/>Group by heading2"]
    
    GroupBySection --> FormatExcerpts["formatSectionExcerpts()<br/>Clean HTML, check budget"]
    
    FormatExcerpts --> CheckBudget{Token<br/>Budget?}
    
    CheckBudget -->|Under 70%| FullExcerpts["Full Excerpts"]
    CheckBudget -->|Over 70%| TruncateExcerpts["Truncate to 400 chars<br/>Add truncation message"]
    CheckBudget -->|Exceeded| LinksOnly["Move to 'Further results' section"]
    
    FullExcerpts --> Output
    TruncateExcerpts --> Output
    LinksOnly --> Output
    
    Output["Formatted Markdown"]
```

**Grouping Rules**

1. Results group by `product` field (e.g., "hub", "transformers")
2. Within products, group by base URL (anchors stripped: `#section` removed)
3. Within pages, group by `heading2` field (section within page)
4. Products and pages sort by descending result count

Sources: [packages/mcp/src/docs-search/docs-semantic-search.ts:132-157](), [packages/mcp/src/docs-search/docs-semantic-search.ts:195-210](), [packages/mcp/src/docs-search/docs-semantic-search.ts:265-378]()

### Result Structure

The formatted output follows this structure:

```
# Documentation Library Search Results for "{query}" (filtered by product: {product})

Found {count} results

## Results for Product: {product} ({count} results)

### Results from [{page_title}]({url}) ({count} results)

#### Excerpts from the "{section}" section

{cleaned_text}

#### Excerpt from the "{section}" section

{cleaned_text}

## Further results were found in:
- [Page Title](url) (count results) *(product)*

---

Use the "hf_doc_fetch" tool to fetch a document from the library.
```

The tool includes a footer directing users to `hf_doc_fetch` for retrieving full documents.

Sources: [packages/mcp/src/docs-search/docs-semantic-search.ts:265-378]()

### Token Budget Management

The `DocSearchTool` implements three-tier budget management:

| State | Token Usage | Behavior |
|-------|-------------|----------|
| Under 70% budget | < 8,750 tokens | Full excerpts with HTML stripped |
| 70-100% budget | 8,750-12,500 tokens | Truncate excerpts to 400 chars, add message once |
| Over budget | > 12,500 tokens | Move remaining products/pages to "Further results" links section |

The truncation message references `hf_doc_fetch`:

```
*[Content truncated - use hf_doc_fetch for full text or narrow search terms]*
```

Token estimation uses the `estimateTokens()` utility function, which calculates approximately 3.3 characters per token.

Sources: [packages/mcp/src/docs-search/docs-semantic-search.ts:69-88](), [packages/mcp/src/docs-search/docs-semantic-search.ts:215-260](), [packages/mcp/src/docs-search/docs-semantic-search.ts:296-376]()

### Text Cleaning

The tool cleans search result excerpts before display:

1. Remove HTML tags: `<div>`, `<img>`, etc. → stripped via regex
2. Collapse multiple newlines: `\n\n\n` → `\n`
3. Trim whitespace
4. Escape markdown special characters in headings and product names

Sources: [packages/mcp/src/docs-search/docs-semantic-search.ts:237-252]()

---

## Documentation Fetch Tool

The `DocFetchTool` class implements the `hf_doc_fetch` tool, which retrieves documentation pages and converts them to clean Markdown.

### Configuration

| Property | Type | Description |
|----------|------|-------------|
| `name` | string | `hf_doc_fetch` |
| `doc_url` | string | Documentation URL (max 200 chars) |
| `offset` | number (optional) | Token offset for chunked documents (min 0) |

Sources: [packages/mcp/src/docs-search/doc-fetch.ts:5-23]()

### URL Validation and Normalization

```mermaid
graph TB
    Input["Input URL"]
    
    Input --> Normalize["normalizeDocUrl()"]
    
    Normalize --> CheckPrefix{Prefix?}
    
    CheckPrefix -->|"/docs"| AddHFHost["Prepend https://huggingface.co"]
    CheckPrefix -->|"./docs"| AddHFHost2["Prepend https://huggingface.co<br/>Strip ./ prefix"]
    CheckPrefix -->|"gradio.app"| RewriteGradio["Rewrite to www.gradio.app"]
    CheckPrefix -->|Other| PassThrough["Pass through"]
    
    AddHFHost --> Validate
    AddHFHost2 --> Validate
    RewriteGradio --> Validate
    PassThrough --> Validate
    
    Validate["validateUrl()"]
    
    Validate --> CheckProtocol{HTTPS?}
    CheckProtocol -->|No| Error["Throw Error:<br/>'That was not a valid documentation URL'"]
    CheckProtocol -->|Yes| CheckHost{Host?}
    
    CheckHost -->|huggingface.co/docs/*| Valid
    CheckHost -->|www.huggingface.co/docs/*| Valid
    CheckHost -->|gradio.app or www.gradio.app| Valid
    CheckHost -->|Other| Error
    
    Valid["Valid URL"]
```

**Normalization Examples**

| Input | Output |
|-------|--------|
| `/docs/diffusers/index` | `https://huggingface.co/docs/diffusers/index` |
| `./docs/diffusers/index` | `https://huggingface.co/docs/diffusers/index` |
| `https://gradio.app/guides/x` | `https://www.gradio.app/guides/x` |
| `https://huggingface.co/docs/transformers` | (unchanged) |

The `gradio.app` to `www.gradio.app` normalization is necessary for correct page resolution.

Sources: [packages/mcp/src/docs-search/doc-fetch.ts:119-139](), [packages/mcp/src/docs-search/doc-fetch.ts:219-243]()

### HTML to Markdown Conversion

The tool uses `TurndownService` with extensive customization to produce clean Markdown output.

#### Conversion Configuration

```typescript
// Configuration applied in constructor
headingStyle: 'atx'        // Use ### style headings
codeBlockStyle: 'fenced'   // Use ``` code blocks
```

#### Content Filtering Rules

The `DocFetchTool` constructor configures removal rules for noisy elements:

| Rule | Elements Removed | Rationale |
|------|------------------|-----------|
| Structural | `<head>`, `<script>`, `<style>`, `<noscript>` | Non-content elements |
| Navigation | `<header>`, `<nav>`, `<footer>`, `<aside>` | UI chrome, not documentation |
| Interactive | `<form>`, `<button>`, `<iframe>` | Non-textual elements |
| SVG images | `<svg>`, `<img src="*.svg">`, data URIs | Visual elements, noisy in text |
| Heading anchors | `<a href="#...">` with icons/encoded SVGs | Navigation artifacts |

Sources: [packages/mcp/src/docs-search/doc-fetch.ts:30-116]()

#### Post-Processing

After Turndown conversion, the tool applies regex cleanup:

```typescript
// Strip remaining SVG markdown images
.replace(/!\[[^\]]*\]\(\s*(?:data:image\/svg\+xml[^)]*|[^)]*\.svg(?:\?[^)]*)?)\s*\)/gi, '')

// Remove empty links: [](...) 
.replace(/\[\s*\]\(\s*[^)]*\s*\)/g, '')

// Remove links with encoded SVG payloads
.replace(/\[[^\]]*(?:data:image\/svg\+xml|%3csvg|svg%2bxml)[^\]]*\]\([^)]*\)/gi, '')
```

This ensures clean text even if DOM filters miss edge cases.

Sources: [packages/mcp/src/docs-search/doc-fetch.ts:156-169]()

### Document Chunking System

Large documents automatically chunk to stay within token limits.

```mermaid
graph TB
    Fetch["fetch(params)"]
    
    Fetch --> GetContent["Fetch HTML/Markdown<br/>from URL"]
    
    GetContent --> CheckContentType{Content<br/>Type?}
    
    CheckContentType -->|text/markdown or text/plain| UseAsIs["Use content as-is"]
    CheckContentType -->|Other HTML| Convert["TurndownService.turndown()<br/>Post-process SVGs"]
    
    UseAsIs --> ApplyChunking
    Convert --> ApplyChunking
    
    ApplyChunking["applyChunking(content, offset)"]
    
    ApplyChunking --> EstimateTotal["estimateTokens(full content)<br/>totalTokens"]
    
    EstimateTotal --> CheckSize{Size?}
    
    CheckSize -->|"≤ 7500 tokens<br/>offset = 0"| ReturnFull["Return full content"]
    CheckSize -->|"> 7500 tokens<br/>or offset > 0"| CalculateChunk["Calculate chunk boundaries"]
    
    CalculateChunk --> CharMath["charsPerToken = totalChars / totalTokens<br/>startChar = offset * charsPerToken<br/>endChar = startChar + 7500 * charsPerToken"]
    
    CharMath --> CheckOffset{Offset beyond<br/>document?}
    
    CheckOffset -->|Yes| ErrorMsg["Return error:<br/>'Offset N is beyond document length'"]
    CheckOffset -->|No| ExtractChunk["Extract chunk:<br/>content.slice(startChar, endChar)"]
    
    ExtractChunk --> CalcNext["nextOffset = offset + estimateTokens(chunk)"]
    
    CalcNext --> CheckMore{More<br/>content?}
    
    CheckMore -->|Yes| AddTruncation["Append truncation message:<br/>'CALL hf_doc_fetch WITH AN OFFSET OF {nextOffset}'"]
    CheckMore -->|No| NoMessage["No message needed"]
    
    AddTruncation --> ReturnChunk
    NoMessage --> ReturnChunk
    
    ReturnChunk["Return chunk"]
    ReturnFull --> End
    ErrorMsg --> End
    ReturnChunk --> End
```

**Chunking Parameters**

| Parameter | Value | Notes |
|-----------|-------|-------|
| Max tokens per chunk | 7,500 | Configured in `applyChunking()` |
| Offset unit | Tokens | Not characters |
| Truncation message | `=== DOCUMENT TRUNCATED. CALL hf_doc_fetch WITH AN OFFSET OF {nextOffset} FOR THE NEXT CHUNK ===` | Added if more content exists |

**Token-to-Character Mapping**

The chunking system estimates character positions from token offsets:

```typescript
const charsPerToken = totalChars / totalTokens;
const startChar = Math.floor(offset * charsPerToken);
const maxCharsPerChunk = Math.floor(7500 * charsPerToken);
const endChar = Math.min(startChar + maxCharsPerChunk, totalChars);
```

This approach avoids re-tokenizing the entire document for each chunk request.

Sources: [packages/mcp/src/docs-search/doc-fetch.ts:144-176](), [packages/mcp/src/docs-search/doc-fetch.ts:178-216]()

### Fetch Workflow

```mermaid
sequenceDiagram
    participant Client
    participant DocFetchTool
    participant normalizeDocUrl
    participant validateUrl
    participant fetch as "HTTP Fetch"
    participant TurndownService
    participant applyChunking
    
    Client->>DocFetchTool: fetch({doc_url, offset?})
    DocFetchTool->>normalizeDocUrl: Normalize URL
    normalizeDocUrl-->>DocFetchTool: Normalized URL
    DocFetchTool->>validateUrl: Validate URL
    
    alt Invalid URL
        validateUrl-->>Client: Error: "That was not a valid documentation URL"
    end
    
    DocFetchTool->>fetch: GET url<br/>headers: {accept: "text/markdown"}
    fetch-->>DocFetchTool: Response (HTML or Markdown)
    
    alt Content-Type: text/markdown or text/plain
        DocFetchTool->>DocFetchTool: Use content as-is
    else Other content type
        DocFetchTool->>TurndownService: turndown(html)
        TurndownService-->>DocFetchTool: Markdown
        DocFetchTool->>DocFetchTool: Post-process:<br/>Remove SVG images, empty links
    end
    
    DocFetchTool->>applyChunking: applyChunking(content, offset)
    
    alt Document fits in budget
        applyChunking-->>Client: Full content
    else Document exceeds budget
        applyChunking-->>Client: Chunk + truncation message
    end
    
    Note over Client: If truncated, call again<br/>with offset from message
```

Sources: [packages/mcp/src/docs-search/doc-fetch.ts:144-176]()

---

## Integration and Usage Patterns

### Discovery-Retrieval Pattern

The typical workflow combines both tools:

1. **Discover**: Use `hf_doc_search` with semantic query
2. **Select**: Identify relevant page URLs from results
3. **Retrieve**: Use `hf_doc_fetch` with selected URL
4. **Continue**: If truncated, use offset for next chunk

### Example: Multi-Chunk Retrieval

```
1. hf_doc_search({query: "rate limits"})
   → Returns: URL https://huggingface.co/docs/hub/rate-limits

2. hf_doc_fetch({doc_url: "https://huggingface.co/docs/hub/rate-limits"})
   → Returns: First 7500 tokens + "CALL hf_doc_fetch WITH AN OFFSET OF 7234"

3. hf_doc_fetch({doc_url: "https://huggingface.co/docs/hub/rate-limits", offset: 7234})
   → Returns: Next chunk or full remainder
```

### Cross-Tool References

The tools reference each other in their output:

- `hf_doc_search` truncation message: `*[Content truncated - use hf_doc_fetch for full text...]*`
- `hf_doc_search` footer: `Use the "hf_doc_fetch" tool to fetch a document from the library.`
- `hf_doc_fetch` truncation message: `=== DOCUMENT TRUNCATED. CALL hf_doc_fetch WITH AN OFFSET OF...`

These references are implemented using the exported `DOC_FETCH_CONFIG.name` constant to ensure consistency.

Sources: [packages/mcp/src/docs-search/docs-semantic-search.ts:4](), [packages/mcp/src/docs-search/docs-semantic-search.ts:246](), [packages/mcp/src/docs-search/docs-semantic-search.ts:372](), [packages/mcp/src/docs-search/doc-fetch.ts:212]()

### Tool Registration

Both tools are registered in the MCP server with their respective configurations:

- Tool config objects: `DOCS_SEMANTIC_SEARCH_CONFIG`, `DOC_FETCH_CONFIG`
- Tool classes: `DocSearchTool`, `DocFetchTool`
- Base class: `DocSearchTool extends HfApiCall`

The search tool inherits from `HfApiCall` for consistent API interaction patterns, while the fetch tool directly implements HTTP fetching with Turndown conversion.

Sources: [packages/mcp/src/docs-search/docs-semantic-search.ts:10-45](), [packages/mcp/src/docs-search/docs-semantic-search.ts:77-88](), [packages/mcp/src/docs-search/doc-fetch.ts:5-23](), [packages/mcp/src/docs-search/doc-fetch.ts:27-116]()

---

# Page: Prompts

# Prompts

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [packages/app/src/server/mcp-server.ts](packages/app/src/server/mcp-server.ts)
- [packages/app/src/shared/settings.ts](packages/app/src/shared/settings.ts)
- [packages/app/src/web/App.tsx](packages/app/src/web/App.tsx)
- [packages/e2e-python/prompts.py](packages/e2e-python/prompts.py)
- [packages/mcp/src/dataset-detail.ts](packages/mcp/src/dataset-detail.ts)
- [packages/mcp/src/model-detail.ts](packages/mcp/src/model-detail.ts)

</details>



## Purpose and Scope

This document explains the MCP prompt system and describes the four built-in prompts provided by the Hugging Face MCP Server. Prompts in the Model Context Protocol are pre-configured message templates that AI assistants can use to quickly access formatted information. This page covers prompt registration, parameter schemas, and the specific functionality of each prompt.

For information about tools (which perform actions and searches), see [Built-in Tools](#4.2). For the general tool and prompt architecture, see [Tool System Overview](#4.1).

---

## Prompts vs Tools

In the Model Context Protocol, **prompts** and **tools** serve different purposes:

| Aspect | Tools | Prompts |
|--------|-------|---------|
| **Purpose** | Perform actions, searches, or operations | Provide pre-formatted information as conversation context |
| **Return Type** | `ToolResult` with content array | `GetPromptResult` with messages array |
| **Invocation** | `tools/call` JSON-RPC method | `prompts/get` JSON-RPC method |
| **Client Experience** | Listed as available actions | Listed as template options for context injection |
| **Use Case** | Interactive operations by AI | Injecting rich context into conversations |

The key distinction is that prompts are designed to inject large amounts of formatted information directly into the conversation context, while tools are for executing discrete operations.

**Sources:** [packages/app/src/server/mcp-server.ts:221-355]()

---

## Prompt System Architecture

```mermaid
graph TB
    subgraph "Prompt Configuration Layer (packages/mcp)"
        UserConfig["USER_SUMMARY_PROMPT_CONFIG<br/>name, description, schema"]
        PaperConfig["PAPER_SUMMARY_PROMPT_CONFIG<br/>name, description, schema"]
        ModelConfig["MODEL_DETAIL_PROMPT_CONFIG<br/>name, description, schema"]
        DatasetConfig["DATASET_DETAIL_PROMPT_CONFIG<br/>name, description, schema"]
    end
    
    subgraph "Prompt Implementation Layer (packages/mcp)"
        UserImpl["UserSummaryPrompt<br/>generateSummary()"]
        PaperImpl["PaperSummaryPrompt<br/>generateSummary()"]
        ModelImpl["ModelDetailTool<br/>getDetails(includeReadme=true)"]
        DatasetImpl["DatasetDetailTool<br/>getDetails(includeReadme=true)"]
    end
    
    subgraph "Registration Layer (packages/app)"
        ServerReg["McpServer.prompt()<br/>Registration Method"]
        
        UserHandler["User Summary Handler<br/>lines 221-253"]
        PaperHandler["Paper Summary Handler<br/>lines 255-287"]
        ModelHandler["Model Details Handler<br/>lines 289-321"]
        DatasetHandler["Dataset Details Handler<br/>lines 323-355"]
    end
    
    subgraph "Logging & Metrics"
        LogPrompt["logPromptQuery()<br/>Track usage metrics"]
    end
    
    UserConfig --> UserHandler
    PaperConfig --> PaperHandler
    ModelConfig --> ModelHandler
    DatasetConfig --> DatasetHandler
    
    UserHandler --> UserImpl
    PaperHandler --> PaperImpl
    ModelHandler --> ModelImpl
    DatasetHandler --> DatasetImpl
    
    ServerReg --> UserHandler
    ServerReg --> PaperHandler
    ServerReg --> ModelHandler
    ServerReg --> DatasetHandler
    
    UserHandler --> LogPrompt
    PaperHandler --> LogPrompt
    ModelHandler --> LogPrompt
    DatasetHandler --> LogPrompt
```

**Diagram: Prompt Architecture Components**

Each prompt follows a three-layer pattern:

1. **Configuration Layer**: Defines the prompt's name, description, and Zod parameter schema
2. **Implementation Layer**: Contains the business logic for fetching and formatting data
3. **Registration Layer**: Registers the prompt with the MCP server and wires up handlers

**Sources:** [packages/app/src/server/mcp-server.ts:42-47, 221-355](), [packages/mcp/src/model-detail.ts:28-40](), [packages/mcp/src/dataset-detail.ts:22-34]()

---

## Built-in Prompts Overview

The Hugging Face MCP Server provides four built-in prompts:

| Prompt Name | Purpose | Primary Parameter | Implementation Class |
|-------------|---------|-------------------|---------------------|
| `user_summary` | User Summary | `user_id` | `UserSummaryPrompt` |
| `paper_summary` | Paper Summary | `paper_id` | `PaperSummaryPrompt` |
| `Model Details` | Model Details with README | `model_id` | `ModelDetailTool` |
| `Dataset Details` | Dataset Details with README | `dataset_id` | `DatasetDetailTool` |

All prompts return formatted markdown text suitable for injection into AI conversation context. Unlike their tool counterparts (which return concise information), prompts include comprehensive details like README content.

**Sources:** [packages/app/src/server/mcp-server.ts:221-355]()

---

## Prompt Invocation Flow

```mermaid
sequenceDiagram
    participant Client as "AI Client"
    participant Server as "McpServer"
    participant Handler as "Prompt Handler"
    participant Impl as "Implementation Class"
    participant HF as "Hugging Face API"
    participant Logger as "logPromptQuery()"
    
    Client->>Server: prompts/get request<br/>name: "Model Details"<br/>params: {model_id: "..."}
    Server->>Handler: Route to registered handler
    Handler->>Impl: new ModelDetailTool(hfToken)
    Handler->>Impl: getDetails(model_id, includeReadme=true)
    Impl->>HF: modelInfo() API call
    HF-->>Impl: Model data
    Impl->>HF: fetchReadmeContent()
    HF-->>Impl: README markdown
    Impl-->>Handler: Formatted result + README
    Handler->>Logger: Log query with metrics<br/>(totalResults, responseCharCount)
    Handler-->>Server: GetPromptResult<br/>messages: [{role: "user", content}]
    Server-->>Client: Formatted prompt response
```

**Diagram: Prompt Execution Sequence**

The flow differs from tools in the final return format: prompts return a `GetPromptResult` with a `messages` array suitable for conversation injection, rather than a `ToolResult` with a `content` array.

**Sources:** [packages/app/src/server/mcp-server.ts:221-355]()

---

## User Summary Prompt

**Prompt Name:** `user_summary`  
**Configuration:** `USER_SUMMARY_PROMPT_CONFIG`

### Purpose

Generates a comprehensive summary of a Hugging Face user's profile, including their public repositories, contributions, and activity.

### Parameters

```typescript
{
  user_id: string  // Hugging Face user ID (e.g., "microsoft", "openai")
}
```

**Schema:** [packages/app/src/server/mcp-server.ts:43, 224]()

### Implementation

The prompt is handled by the `UserSummaryPrompt` class, which:

1. Fetches user profile information from Hugging Face
2. Retrieves user's models, datasets, and spaces
3. Formats the data into a comprehensive markdown summary
4. Returns as a conversation message

### Registration

```typescript
server.prompt(
  USER_SUMMARY_PROMPT_CONFIG.name,
  USER_SUMMARY_PROMPT_CONFIG.description,
  USER_SUMMARY_PROMPT_CONFIG.schema.shape,
  async (params: UserSummaryParams) => {
    const userSummary = new UserSummaryPrompt(hfToken);
    const summaryText = await userSummary.generateSummary(params);
    // Log metrics and return as message
    return {
      description: `User summary for ${params.user_id}`,
      messages: [{
        role: 'user' as const,
        content: { type: 'text' as const, text: summaryText }
      }]
    };
  }
);
```

### Logging

Logs include:
- Query parameters (`user_id`)
- Client session metadata
- Response character count
- Total results and results shared (always 1 for successful summary)

**Sources:** [packages/app/src/server/mcp-server.ts:221-253]()

---

## Paper Summary Prompt

**Prompt Name:** `paper_summary`  
**Configuration:** `PAPER_SUMMARY_PROMPT_CONFIG`

### Purpose

Provides a detailed summary of an academic paper from arXiv or other sources, including metadata and abstract information.

### Parameters

```typescript
{
  paper_id: string  // Paper identifier (e.g., "arxiv:2502.16161")
}
```

**Schema:** [packages/app/src/server/mcp-server.ts:46, 258]()

### Implementation

The prompt is handled by the `PaperSummaryPrompt` class, which:

1. Parses the paper identifier
2. Fetches paper metadata from Hugging Face Hub
3. Retrieves abstract and related information
4. Formats into a structured markdown summary
5. Returns as a conversation message

### Registration

```typescript
server.prompt(
  PAPER_SUMMARY_PROMPT_CONFIG.name,
  PAPER_SUMMARY_PROMPT_CONFIG.description,
  PAPER_SUMMARY_PROMPT_CONFIG.schema.shape,
  async (params: PaperSummaryParams) => {
    const paperSummary = new PaperSummaryPrompt(hfToken);
    const summaryText = await paperSummary.generateSummary(params);
    // Log metrics and return as message
    return {
      description: `Paper summary for ${params.paper_id}`,
      messages: [{
        role: 'user' as const,
        content: { type: 'text' as const, text: summaryText }
      }]
    };
  }
);
```

### Example Usage (Python)

```python
await agent.anon.apply_prompt("Paper Summary", {"paper_id": "arxiv:2502.16161"})
```

**Sources:** [packages/app/src/server/mcp-server.ts:255-287](), [packages/e2e-python/prompts.py:25]()

---

## Model Details Prompt

**Prompt Name:** `Model Details`  
**Configuration:** `MODEL_DETAIL_PROMPT_CONFIG`

### Purpose

Provides comprehensive model information **including the full README content** from the model repository. This differs from the `model_details` tool, which returns only metadata without the README.

### Parameters

```typescript
{
  model_id: string  // Model ID in author/model format (e.g., "openai/gpt-oss-120b")
}
```

**Schema Constraints:**
- Minimum length: 5 characters
- Maximum length: 50 characters

**Sources:** [packages/mcp/src/model-detail.ts:28-40]()

### Implementation

The prompt reuses the `ModelDetailTool` class but calls `getDetails()` with `includeReadme=true`:

```typescript
const modelDetail = new ModelDetailTool(hfToken, undefined);
const result = await modelDetail.getDetails(params.model_id, true);
```

This triggers:

1. Fetching model metadata via `modelInfo()` from `@huggingface/hub`
2. Fetching README content via `fetchReadmeContent()`
3. Appending README in XML tags: `<modelcard-readme>...</modelcard-readme>`

### README Inclusion

The README is appended to the formatted model details:

```typescript
result.formatted += '\n\n## README\n<modelcard-readme>\n\n' 
  + readmeContent.trim() 
  + '\n</modelcard-readme>';
```

The XML-style tags help AI clients parse and distinguish the README section from metadata.

**Sources:** [packages/app/src/server/mcp-server.ts:289-321](), [packages/mcp/src/model-detail.ts:127, 261-268]()

### Comparison with model_details Tool

| Aspect | `Model Details` (Prompt) | `model_details` (Tool) |
|--------|-------------------------|------------------------|
| README Included | ✅ Yes | ❌ No |
| Response Type | Message (prompt context) | Tool result |
| Use Case | Rich context injection | Quick metadata lookup |
| Character Count | Typically 5000-50000+ | Typically 500-2000 |

### Example Usage (Python)

```python
await agent.anon.apply_prompt("Model Details", {"model_id": "openai/gpt-oss-120b"})
```

**Sources:** [packages/e2e-python/prompts.py:20]()

---

## Dataset Details Prompt

**Prompt Name:** `Dataset Details`  
**Configuration:** `DATASET_DETAIL_PROMPT_CONFIG`

### Purpose

Provides comprehensive dataset information **including the full README content** from the dataset repository. This differs from the `dataset_details` tool, which returns only metadata without the README.

### Parameters

```typescript
{
  dataset_id: string  // Dataset ID (e.g., "Anthropic/hh-rlhf", "squad")
}
```

**Schema Constraints:**
- Minimum length: 3 characters
- Maximum length: 100 characters

**Sources:** [packages/mcp/src/dataset-detail.ts:22-34]()

### Implementation

The prompt reuses the `DatasetDetailTool` class but calls `getDetails()` with `includeReadme=true`:

```typescript
const datasetDetail = new DatasetDetailTool(hfToken, undefined);
const result = await datasetDetail.getDetails(params.dataset_id, true);
```

This triggers:

1. Fetching dataset metadata via `datasetInfo()` from `@huggingface/hub`
2. Fetching README content via `fetchReadmeContent()`
3. Appending README in XML tags: `<datasetcard-readme>...</datasetcard-readme>`

### README Inclusion

The README is appended to the formatted dataset details:

```typescript
result.formatted += '\n\n## README\n<datasetcard-readme>\n' 
  + readmeContent.trim() 
  + '\n</datasetcard-readme>';
```

**Sources:** [packages/app/src/server/mcp-server.ts:323-355](), [packages/mcp/src/dataset-detail.ts:98, 165-172]()

### Comparison with dataset_details Tool

| Aspect | `Dataset Details` (Prompt) | `dataset_details` (Tool) |
|--------|---------------------------|--------------------------|
| README Included | ✅ Yes | ❌ No |
| Response Type | Message (prompt context) | Tool result |
| Use Case | Rich context injection | Quick metadata lookup |
| Character Count | Typically 3000-30000+ | Typically 400-1500 |

### Example Usage (Python)

```python
await agent.anon.apply_prompt("Dataset Details", {"dataset_id": "Anthropic/hh-rlhf"})
```

**Sources:** [packages/e2e-python/prompts.py:21]()

---

## Prompt Metrics and Logging

All prompts use the `logPromptQuery()` function to record usage metrics:

```mermaid
graph LR
    Handler["Prompt Handler"] --> LogCall["logPromptQuery()"]
    LogCall --> Metrics["Recorded Metrics"]
    
    subgraph "Metrics Captured"
        PromptName["promptName"]
        Query["queryString"]
        Params["parameters"]
        Session["clientSessionId"]
        Auth["isAuthenticated"]
        Client["clientName/Version"]
        Results["totalResults"]
        ResultsShared["resultsShared"]
        CharCount["responseCharCount"]
    end
    
    Metrics --> PromptName
    Metrics --> Query
    Metrics --> Params
    Metrics --> Session
    Metrics --> Auth
    Metrics --> Client
    Metrics --> Results
    Metrics --> ResultsShared
    Metrics --> CharCount
```

**Diagram: Prompt Metrics Collection**

### Logged Information

Each prompt invocation logs:

```typescript
logPromptQuery(
  PROMPT_CONFIG.name,           // e.g., "Model Details"
  params.model_id,              // Primary identifier
  { model_id: params.model_id }, // Full parameters
  {
    clientSessionId: sessionInfo?.clientSessionId,
    isAuthenticated: sessionInfo?.isAuthenticated ?? !!hfToken,
    clientName: sessionInfo?.clientInfo?.name,
    clientVersion: sessionInfo?.clientInfo?.version,
    totalResults: result.totalResults,
    resultsShared: result.resultsShared,
    responseCharCount: summaryText.length
  }
);
```

The `responseCharCount` is particularly important for prompts, as they typically return much larger text payloads than tools (often 10-100x larger due to README inclusion).

**Sources:** [packages/app/src/server/mcp-server.ts:69, 228-238, 262-272, 296-306, 330-340]()

---

## Prompt Registration Pattern

All prompts follow a consistent registration pattern in `createServerFactory`:

```mermaid
graph TB
    subgraph "Common Pattern"
        Config["Import CONFIG from @llmindset/hf-mcp"]
        Class["Import Implementation Class"]
        Register["server.prompt()"]
        Handler["Async Handler Function"]
        Instance["new ImplementationClass(hfToken)"]
        Execute["Call generate/getDetails method"]
        Log["logPromptQuery()"]
        Return["Return GetPromptResult"]
    end
    
    Config --> Register
    Class --> Handler
    Register --> Handler
    Handler --> Instance
    Instance --> Execute
    Execute --> Log
    Log --> Return
```

**Diagram: Standard Prompt Registration Flow**

### Code Pattern

Each prompt follows this structure in [packages/app/src/server/mcp-server.ts]():

```typescript
server.prompt(
  PROMPT_CONFIG.name,                    // Prompt name from config
  PROMPT_CONFIG.description,             // Description from config
  PROMPT_CONFIG.schema.shape,            // Zod schema shape
  async (params: PromptParams) => {
    // 1. Create implementation instance
    const implementation = new ImplementationClass(hfToken);
    
    // 2. Execute the prompt logic
    const summaryText = await implementation.generateMethod(params);
    
    // 3. Log metrics
    logPromptQuery(PROMPT_CONFIG.name, identifier, params, metrics);
    
    // 4. Return as message
    return {
      description: `Description for ${identifier}`,
      messages: [{
        role: 'user' as const,
        content: { type: 'text' as const, text: summaryText }
      }]
    };
  }
);
```

This consistent pattern ensures all prompts:
- Accept validated parameters via Zod schemas
- Log comprehensive usage metrics
- Return properly formatted messages
- Support authentication when available

**Sources:** [packages/app/src/server/mcp-server.ts:221-355]()

---

## Prompt Selection and Availability

Unlike tools, prompts are **always enabled** and do not participate in the tool selection system (bouquets, mixes, or user settings). All four prompts are available to every client regardless of configuration.

This design decision reflects that prompts provide read-only context injection rather than performing actions, making them safe to expose universally.

**Sources:** [packages/app/src/server/mcp-server.ts:221-355]()

---

# Page: Tool Selection System

# Tool Selection System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [packages/app/src/server/mcp-server.ts](packages/app/src/server/mcp-server.ts)
- [packages/app/src/server/utils/tool-selection-strategy.ts](packages/app/src/server/utils/tool-selection-strategy.ts)
- [packages/app/src/shared/bouquet-presets.ts](packages/app/src/shared/bouquet-presets.ts)
- [packages/app/src/shared/settings.ts](packages/app/src/shared/settings.ts)
- [packages/app/src/web/App.tsx](packages/app/src/web/App.tsx)
- [packages/app/src/web/components/SettingsCopyPage.tsx](packages/app/src/web/components/SettingsCopyPage.tsx)
- [packages/app/src/web/components/bouquets/ToolPresetsCard.tsx](packages/app/src/web/components/bouquets/ToolPresetsCard.tsx)
- [packages/app/test/server/utils/tool-selection-strategy.test.ts](packages/app/test/server/utils/tool-selection-strategy.test.ts)

</details>



The Tool Selection System determines which MCP tools are available to a client based on configuration headers, URL parameters, and user settings. It implements a clear precedence hierarchy to resolve conflicts between multiple configuration sources, enabling flexible tool management through bouquets (predefined tool groups), mixes (additive tool sets), and user-specific settings.

This system handles only built-in tool selection. For information about Gradio endpoint registration, see [Gradio Integration](#6). For details on how individual tools are implemented, see [Built-in Tools](#4.2).

## Overview

The Tool Selection System operates through the `ToolSelectionStrategy` class, which evaluates configuration sources in priority order and returns a `ToolSelectionResult` containing the list of enabled tool IDs. The system is invoked during MCP server instantiation by the `createServerFactory` function.

**Key Responsibilities:**
- Parse configuration from HTTP headers or URL parameters
- Resolve tool selection based on precedence rules
- Apply special features like `SEARCH_ENABLES_FETCH`
- Normalize and deduplicate tool lists
- Provide metadata about the selection mode and reasoning

**Architecture Position:**

```mermaid
graph TB
    Client["Client Request"]
    Headers["Headers/Parameters<br/>x-mcp-bouquet<br/>x-mcp-mix"]
    Factory["createServerFactory"]
    Strategy["ToolSelectionStrategy"]
    Result["ToolSelectionResult<br/>mode + enabledToolIds"]
    Server["McpServer Instance"]
    ToolInstances["Tool Registration"]
    
    Client --> Headers
    Headers --> Factory
    Factory --> Strategy
    Strategy --> Result
    Result --> Factory
    Factory --> Server
    Server --> ToolInstances
    
    style Strategy fill:#ffe1e1
    style Result fill:#e1ffe1
```

Sources: [packages/app/src/server/utils/tool-selection-strategy.ts:1-260](), [packages/app/src/server/mcp-server.ts:96-186]()

## Precedence Rules

The system evaluates configuration sources in strict priority order, with higher-precedence sources completely overriding lower ones (except for Mix mode, which is additive).

| Priority | Mode | Header/Parameter | Behavior |
|----------|------|------------------|----------|
| 1 (Highest) | `BOUQUET_OVERRIDE` | `x-mcp-bouquet` | Completely replaces tool selection with predefined set |
| 2 | `MIX` | `x-mcp-mix` | Adds mix bouquet tools to user settings (additive) |
| 3 | `EXTERNAL_API` | (none) | Uses settings from external API endpoint |
| 3 | `INTERNAL_API` | (none) | Uses settings from internal settings service |
| 4 (Lowest) | `FALLBACK` | (none) | Enables all tools when no configuration available |

**Precedence Flow:**

```mermaid
graph TD
    Start["selectTools()"]
    CheckBouquet{"Bouquet header<br/>present?"}
    CheckMix{"Mix header present<br/>+ user settings<br/>available?"}
    CheckSettings{"User settings<br/>available?"}
    
    BouquetMode["BOUQUET_OVERRIDE<br/>Use bouquet tools only"]
    MixMode["MIX<br/>User tools + mix tools"]
    SettingsMode["EXTERNAL_API or<br/>INTERNAL_API<br/>Use user settings"]
    FallbackMode["FALLBACK<br/>Enable all tools"]
    
    Start --> CheckBouquet
    CheckBouquet -->|Yes| BouquetMode
    CheckBouquet -->|No| CheckMix
    CheckMix -->|Yes| MixMode
    CheckMix -->|No| CheckSettings
    CheckSettings -->|Yes| SettingsMode
    CheckSettings -->|No| FallbackMode
    
    BouquetMode --> Return["Return ToolSelectionResult"]
    MixMode --> Return
    SettingsMode --> Return
    FallbackMode --> Return
```

Sources: [packages/app/src/server/utils/tool-selection-strategy.ts:119-221](), [packages/app/test/server/utils/tool-selection-strategy.test.ts:118-396]()

## Configuration Sources

### Bouquet Override

Bouquets are predefined tool groups that provide complete, curated tool sets for specific use cases. When a bouquet is specified via the `x-mcp-bouquet` header or `bouquet` URL parameter, it takes absolute precedence and replaces any other tool configuration.

**Code Flow:**

```mermaid
graph LR
    Header["x-mcp-bouquet: search"]
    Extract["extractAuthBouquetAndMix()"]
    Lookup["BOUQUETS['search']"]
    Normalize["normalizeBuiltInTools()"]
    Apply["applySearchEnablesFetch()"]
    Result["enabledToolIds"]
    
    Header --> Extract
    Extract --> Lookup
    Lookup --> Normalize
    Normalize --> Apply
    Apply --> Result
```

**Implementation:**

The bouquet system is implemented through:
- `BOUQUETS` constant defining available presets [packages/app/src/shared/bouquet-presets.ts:13-59]()
- `extractAuthBouquetAndMix()` parsing headers [packages/app/src/server/utils/auth-utils.ts]()
- `selectTools()` checking bouquet first [packages/app/src/server/utils/tool-selection-strategy.ts:136-148]()

**Example:**

```
x-mcp-bouquet: search
```

Results in:
- Mode: `BOUQUET_OVERRIDE`
- Tools: `['hf_semantic_search', 'hf_model_search', 'hf_dataset_search', 'hf_paper_search', 'hf_doc_search']`
- User settings are ignored

Sources: [packages/app/src/server/utils/tool-selection-strategy.ts:136-148](), [packages/app/src/shared/bouquet-presets.ts:13-59](), [packages/app/test/server/utils/tool-selection-strategy.test.ts:118-207]()

### Mix Mode

Mix mode provides additive tool selection, allowing clients to layer additional tools on top of their existing user settings or base configuration. The mix operates by combining the tools from a specified bouquet with the current user settings.

**Additive Behavior:**

```mermaid
graph LR
    UserSettings["User Settings<br/>['hf_whoami',<br/>'hf_duplicate_space']"]
    MixBouquet["Mix Bouquet: 'search'<br/>['hf_semantic_search',<br/>'hf_model_search',<br/>'hf_dataset_search',<br/>'hf_paper_search',<br/>'hf_doc_search']"]
    Combine["Combine + Deduplicate"]
    Result["Final Tools<br/>[...user tools,<br/>...search tools]"]
    
    UserSettings --> Combine
    MixBouquet --> Combine
    Combine --> Result
```

**Implementation Logic:**

The mix logic is implemented in [packages/app/src/server/utils/tool-selection-strategy.ts:154-178]():

1. Check if mix header is present and valid bouquet name
2. Verify user settings are available (mix requires base settings)
3. Combine arrays: `[...baseSettings.builtInTools, ...BOUQUETS[mix].builtInTools]`
4. Deduplicate using `Set` and normalize
5. Apply `SEARCH_ENABLES_FETCH` if enabled

**Example:**

```
x-mcp-mix: hf_api
User Settings: ['hf_semantic_search', 'hf_dataset_search']
```

Results in:
- Mode: `MIX`
- Tools: User tools + all tools from `hf_api` bouquet (deduplicated)
- Reason: `"User settings + mix(hf_api)"`

Sources: [packages/app/src/server/utils/tool-selection-strategy.ts:154-178](), [packages/app/test/server/utils/tool-selection-strategy.test.ts:209-308]()

### User Settings

When no bouquet or mix is specified, the system falls back to user-specific settings. These settings can come from two sources: an external API endpoint or the internal settings service.

**Settings Sources:**

```mermaid
graph TD
    StrategyCheck{"API client mode?"}
    ExternalAPI["EXTERNAL_API<br/>USER_CONFIG_API endpoint"]
    InternalAPI["INTERNAL_API<br/>settingsService in-memory"]
    FetchExternal["apiClient.getToolStates()"]
    FetchInternal["settingsService.getSettings()"]
    Result["User Settings<br/>builtInTools + spaceTools"]
    
    StrategyCheck -->|externalApiMode=true| ExternalAPI
    StrategyCheck -->|externalApiMode=false| InternalAPI
    ExternalAPI --> FetchExternal
    InternalAPI --> FetchInternal
    FetchExternal --> Result
    FetchInternal --> Result
```

**External API Mode:**

When `externalApiMode` is enabled in the transport configuration, user settings are fetched from a remote endpoint specified by `USER_CONFIG_API` environment variable. This allows centralized user preference management.

Configuration:
- Environment: `USER_CONFIG_API=https://api.example.com/user/settings`
- Transport info: `externalApiMode: true`
- Mode: `EXTERNAL_API`

**Internal API Mode:**

The default mode uses the `settingsService` singleton, which maintains an in-memory map of user settings. Settings can be modified through the web dashboard.

Configuration:
- No external API configured
- Transport info: `externalApiMode: false`
- Mode: `INTERNAL_API`

**Code Integration:**

The user settings retrieval is implemented in [packages/app/src/server/utils/tool-selection-strategy.ts:226-258]():

```typescript
private async getUserSettings(context: ToolSelectionContext): Promise<AppSettings | null> {
    // Use provided user settings (from proxy mode)
    if (context.userSettings) {
        return context.userSettings;
    }
    
    // Fetch from API client
    const toolStates = await this.apiClient.getToolStates(context.hfToken);
    if (toolStates) {
        const builtInTools = Object.keys(toolStates).filter(id => toolStates[id]);
        const spaceTools = this.apiClient.getGradioEndpoints().map(...);
        return { builtInTools, spaceTools };
    }
    
    return null;
}
```

Sources: [packages/app/src/server/utils/tool-selection-strategy.ts:181-208](), [packages/app/src/server/utils/tool-selection-strategy.ts:226-258](), [packages/app/src/shared/settings.ts:50-95]()

### Fallback Mode

When no configuration is available from any source (no bouquet, no mix, no user settings), the system enters fallback mode and enables all built-in tools. This ensures the server remains functional even with missing configuration.

**Fallback Trigger Conditions:**

| Condition | Result |
|-----------|--------|
| Headers are `null` or empty | Fallback |
| No user settings available | Fallback |
| Invalid bouquet name with no settings | Fallback |
| API fetch failure | Fallback |

**Implementation:**

```mermaid
graph TD
    NoConfig["No valid configuration<br/>found"]
    WarnLog["logger.warn()<br/>'No settings available'"]
    AllTools["ALL_BUILTIN_TOOL_IDS<br/>(15+ tools)"]
    Normalize["normalizeBuiltInTools()"]
    Result["FALLBACK mode<br/>All tools enabled"]
    
    NoConfig --> WarnLog
    WarnLog --> AllTools
    AllTools --> Normalize
    Normalize --> Result
```

The fallback is implemented at [packages/app/src/server/utils/tool-selection-strategy.ts:210-221]():

```typescript
// Fallback - all tools enabled
logger.warn('No settings available, using fallback (all tools enabled)');
const enabledToolIds = normalizeBuiltInTools(
    this.applySearchEnablesFetch([...ALL_BUILTIN_TOOL_IDS])
);
return {
    mode: ToolSelectionMode.FALLBACK,
    enabledToolIds,
    reason: 'Fallback - no settings available',
};
```

**Fallback Constants:**

The system uses `BOUQUET_FALLBACK` and `BOUQUET_ANON_DEFAULT` constants for consistent fallback behavior [packages/app/src/server/mcp-server.ts:78-88]():

- `BOUQUET_FALLBACK`: Used when settings API fails
- `BOUQUET_ANON_DEFAULT`: Used for unauthenticated users with external API

Both enable the `hf_api` tool group by default.

Sources: [packages/app/src/server/utils/tool-selection-strategy.ts:210-221](), [packages/app/src/server/mcp-server.ts:78-88](), [packages/app/test/server/utils/tool-selection-strategy.test.ts:370-396]()

## Bouquet Presets

Bouquets are predefined tool collections designed for specific use cases. Each bouquet is defined in `BOUQUETS` and includes a list of tool IDs and (optionally) Gradio space tools.

### Available Bouquets

| Bouquet Key | Description | Tool Count | Category |
|-------------|-------------|------------|----------|
| `hf_api` | Balanced search plus repository details | 7 | Core |
| `search` | Semantic search across all content types | 5 | Core |
| `spaces` | Space management and interaction tools | 5 | Core |
| `docs` | Documentation search and fetch | 2 | Core |
| `all` | Every built-in tool | 15+ | Core |
| `hub_repo_details_readme` | Repository inspection with README | 2 | Advanced |
| `hub_repo_details` | Repository inspection without README | 1 | Advanced |
| `no_gradio_images` | Image filtering behavior flag | 1 | Advanced |
| `mcp_ui` | MCP UI preview tool | 1 | Advanced |
| `jobs` | Job management tools | 1 | Advanced |
| `dynamic_space` | Dynamic space discovery and invocation | 2 | Advanced |

### Bouquet Structure

**Data Model:**

```mermaid
classDiagram
    class AppSettings {
        +string[] builtInTools
        +SpaceTool[] spaceTools
    }
    
    class SpaceTool {
        +string _id
        +string name
        +string subdomain
        +string emoji
    }
    
    class BOUQUETS {
        +Record~string, AppSettings~
    }
    
    class BouquetPreset {
        +BouquetKey key
        +string label
        +string description
        +string category
        +boolean supportsBouquet
        +boolean supportsMix
        +readonly string[] builtInTools
        +DirectParamOption[] directParams
    }
    
    BOUQUETS --> AppSettings
    AppSettings --> SpaceTool
    BouquetPreset --> BOUQUETS
```

**Definition Example:**

From [packages/app/src/shared/bouquet-presets.ts:13-33]():

```typescript
export const BOUQUETS: Record<string, AppSettings> = {
    hf_api: {
        builtInTools: [...TOOL_ID_GROUPS.hf_api],
        spaceTools: [],
    },
    search: {
        builtInTools: [...TOOL_ID_GROUPS.search],
        spaceTools: [],
    },
    spaces: {
        builtInTools: [...TOOL_ID_GROUPS.spaces],
        spaceTools: [],
    },
    // ... more bouquets
};
```

### Core Bouquets

#### hf_api Bouquet

The default balanced tool set, optimized for general Hugging Face Hub interaction.

**Tools Included:**
- `hf_semantic_search` - Semantic search across Spaces
- `hf_model_search` - Model repository search
- `hf_model_detail` - Model metadata and details
- `hf_dataset_search` - Dataset repository search
- `hf_dataset_detail` - Dataset metadata and details
- `hf_paper_search` - Research paper search
- `hub_repo_details` - Generic repository inspection

**Tool ID Group Definition:**

From [packages/mcp/src/tool-ids.ts]():

```typescript
export const TOOL_ID_GROUPS = {
    hf_api: [
        SEMANTIC_SEARCH_TOOL_ID,
        MODEL_SEARCH_TOOL_ID,
        MODEL_DETAIL_TOOL_ID,
        DATASET_SEARCH_TOOL_ID,
        DATASET_DETAIL_TOOL_ID,
        PAPER_SEARCH_TOOL_ID,
        HUB_INSPECT_TOOL_ID,
    ],
    // ...
};
```

#### search Bouquet

Focused on discovery and semantic search capabilities across all Hub content types.

**Tools Included:**
- `hf_semantic_search` - Space semantic search
- `hf_model_search` - Model search
- `hf_dataset_search` - Dataset search
- `hf_paper_search` - Paper search
- `hf_doc_search` - Documentation search

#### spaces Bouquet

Tools for managing and interacting with Hugging Face Spaces.

**Tools Included:**
- `duplicate_space` - Clone Spaces to user namespace
- `space_info` - List Spaces for users/orgs
- `space_files` - Browse Space repository files
- `hf_semantic_search` - Find Spaces by semantic query
- `use_space` - Interact with Gradio Spaces

#### docs Bouquet

Documentation-focused tools for searching and retrieving HF documentation.

**Tools Included:**
- `hf_doc_search` - Semantic search across documentation
- `hf_doc_fetch` - Retrieve full documentation pages

Sources: [packages/app/src/shared/bouquet-presets.ts:13-59](), [packages/app/src/shared/bouquet-presets.ts:80-179](), [packages/app/test/server/utils/tool-selection-strategy.test.ts:54-90]()

### Advanced Bouquets

Advanced bouquets enable specialized features, behavior flags, or experimental tools.

#### hub_repo_details_readme

Enables README content inclusion in repository inspection results. The README flag modifies the `hub_repo_details` tool schema and behavior.

**Tools Included:**
- `hub_repo_details` - Repository inspection tool
- `README_INCLUDE_FLAG` - Behavior flag allowing README access

**Flag Behavior:**

The README flag is checked at runtime in [packages/app/src/server/mcp-server.ts:512-534]():

```typescript
const hubInspectReadmeAllowed = hasReadmeFlag(toolSelection.enabledToolIds);
const hubInspectDescription = hubInspectReadmeAllowed
    ? `${HUB_INSPECT_TOOL_CONFIG.description} README file may be requested...`
    : HUB_INSPECT_TOOL_CONFIG.description;
```

#### no_gradio_images

Behavior flag that strips image content from Gradio tool responses, useful for reducing bandwidth or avoiding image processing.

**Implementation:**

The flag is checked during Gradio tool execution [packages/app/src/server/mcp-server.ts:731-732]():

```typescript
const stripImageContent = 
    noImageContentHeaderEnabled || 
    toolSelection.enabledToolIds.includes('NO_GRADIO_IMAGE_CONTENT');
```

#### jobs Bouquet

Enables job management tools for running, monitoring, and scheduling jobs on Hugging Face infrastructure.

**Tools Included:**
- `hf_jobs` - Job management tool with operations: create, list, status, cancel

#### dynamic_space Bouquet

Enables dynamic Space discovery and invocation without pre-registration.

**Tools Included:**
- `hf_semantic_search` - Find Spaces
- `dynamic_space_tool` - Invoke any Space dynamically

Sources: [packages/app/src/shared/bouquet-presets.ts:34-58](), [packages/app/src/shared/behavior-flags.ts](), [packages/app/src/server/mcp-server.ts:512-534]()

## Integration with MCP Server

The Tool Selection System integrates with the MCP server creation process through the `createServerFactory` function, which uses `ToolSelectionStrategy` to determine tool availability before registering tool instances.

### Server Factory Flow

```mermaid
sequenceDiagram
    participant Client
    participant Transport
    participant Factory as createServerFactory
    participant Strategy as ToolSelectionStrategy
    participant ApiClient as McpApiClient
    participant Server as McpServer
    participant Tools as Tool Instances
    
    Client->>Transport: Connect with headers
    Transport->>Factory: Invoke factory(headers, settings)
    Factory->>Strategy: new ToolSelectionStrategy(apiClient)
    Factory->>Strategy: selectTools(context)
    Strategy->>ApiClient: getToolStates(hfToken)
    ApiClient-->>Strategy: User settings or null
    Strategy->>Strategy: Apply precedence rules
    Strategy-->>Factory: ToolSelectionResult
    
    Factory->>Server: new McpServer()
    Factory->>Tools: Register all tool instances
    
    loop For each tool
        Factory->>Tools: server.tool(name, desc, schema, handler)
        Tools-->>Factory: Tool instance with enable/disable
    end
    
    Factory->>Factory: applyToolStates()
    
    loop For each tool
        Factory->>Tools: Check enabledToolIds
        alt Tool enabled
            Factory->>Tools: toolInstance.enable()
        else Tool disabled
            Factory->>Tools: toolInstance.disable()
        end
    end
    
    Factory-->>Transport: ServerFactoryResult
```

### Registration and State Management

All tools are registered with the MCP server regardless of selection state. The system then enables or disables tools based on the `ToolSelectionResult`.

**Tool Instance Storage:**

From [packages/app/src/server/mcp-server.ts:190-191]():

```typescript
// Always register all tools and store instances for dynamic control
const toolInstances: { [name: string]: Tool } = {};
```

**Tool Registration Pattern:**

Each tool is registered and its instance is stored in the `toolInstances` map [packages/app/src/server/mcp-server.ts:357-381]():

```typescript
toolInstances[SEMANTIC_SEARCH_TOOL_CONFIG.name] = server.tool(
    SEMANTIC_SEARCH_TOOL_CONFIG.name,
    SEMANTIC_SEARCH_TOOL_CONFIG.description,
    SEMANTIC_SEARCH_TOOL_CONFIG.schema.shape,
    SEMANTIC_SEARCH_TOOL_CONFIG.annotations,
    async (params: SearchParams) => {
        // Tool implementation
    }
);
```

**State Application:**

After all tools are registered, the system applies the selection state [packages/app/src/server/mcp-server.ts:839-859]():

```typescript
const applyToolStates = async () => {
    logger.info({
        mode: toolSelection.mode,
        reason: toolSelection.reason,
        enabledCount: toolSelection.enabledToolIds.length,
        totalTools: Object.keys(toolInstances).length,
    }, 'Tool selection strategy applied');
    
    // Apply the desired state to each tool
    for (const [toolName, toolInstance] of Object.entries(toolInstances)) {
        if (toolSelection.enabledToolIds.includes(toolName)) {
            toolInstance.enable();
        } else {
            toolInstance.disable();
        }
    }
};
```

### Dynamic State Changes

In non-JSON response mode and non-external API mode, the system supports dynamic tool state changes via the `toolStateChange` event.

**Event Listener Setup:**

From [packages/app/src/server/mcp-server.ts:873-891]():

```typescript
const toolStateChangeHandler = (toolId: string, enabled: boolean) => {
    const toolInstance = toolInstances[toolId];
    if (toolInstance) {
        if (enabled) {
            toolInstance.enable();
        } else {
            toolInstance.disable();
        }
        logger.debug({ toolId, enabled }, 'Applied single tool state change');
    }
};

sharedApiClient.on('toolStateChange', toolStateChangeHandler);

// Clean up event listener when server closes
server.server.onclose = () => {
    sharedApiClient.removeListener('toolStateChange', toolStateChangeHandler);
};
```

This allows the web dashboard to toggle tools on/off for all active server instances without requiring reconnection.

Sources: [packages/app/src/server/mcp-server.ts:96-186](), [packages/app/src/server/mcp-server.ts:190-859](), [packages/app/src/server/mcp-server.ts:873-891]()

## Special Features

### SEARCH_ENABLES_FETCH

The `SEARCH_ENABLES_FETCH` feature automatically enables the `hf_doc_fetch` tool when `hf_doc_search` is enabled, creating a logical pairing of search and retrieval capabilities.

**Environment Variable:**
```
SEARCH_ENABLES_FETCH=true
```

**Implementation:**

The feature is implemented in [packages/app/src/server/utils/tool-selection-strategy.ts:108-116]():

```typescript
private applySearchEnablesFetch(enabledToolIds: string[]): string[] {
    if (process.env.SEARCH_ENABLES_FETCH === 'true') {
        if (enabledToolIds.includes('hf_doc_search') && 
            !enabledToolIds.includes('hf_doc_fetch')) {
            logger.debug('SEARCH_ENABLES_FETCH: Auto-enabling hf_doc_fetch...');
            return [...enabledToolIds, 'hf_doc_fetch'];
        }
    }
    return enabledToolIds;
}
```

**Application Points:**

The function is called at every tool selection decision point:
1. Bouquet override [line 139]()
2. Mix mode [line 157]()
3. User settings [lines 187, 213]()

**Behavior:**

| Scenario | Result |
|----------|--------|
| `hf_doc_search` enabled, `SEARCH_ENABLES_FETCH=true` | Both tools enabled |
| `hf_doc_search` disabled | No effect |
| `SEARCH_ENABLES_FETCH=false` or unset | No effect |
| `hf_doc_fetch` already in list | No duplication |

Sources: [packages/app/src/server/utils/tool-selection-strategy.ts:108-116](), [packages/app/test/server/utils/tool-selection-strategy.test.ts:516-683]()

### Behavior Flags

Behavior flags are special pseudo-tool IDs that modify system behavior rather than providing tools. They are included in tool lists but don't correspond to actual MCP tools.

#### README_INCLUDE_FLAG

**Constant:** `"README_INCLUDE"` [packages/app/src/shared/behavior-flags.ts]()

**Purpose:** Allows the `hub_repo_details` tool to include README content when explicitly requested by the client.

**Runtime Check:**

From [packages/app/src/server/mcp-server.ts:512-534]():

```typescript
const hubInspectReadmeAllowed = hasReadmeFlag(toolSelection.enabledToolIds);
// ...
const currentSelection = await toolSelectionStrategy.selectTools(toolSelectionContext);
const allowReadme = hasReadmeFlag(currentSelection.enabledToolIds);
const wantReadme = (params as { include_readme?: boolean }).include_readme === true;
const includeReadme = allowReadme && wantReadme;
```

The tool schema is modified to include or exclude the `include_readme` parameter based on this flag.

#### GRADIO_IMAGE_FILTER_FLAG

**Constant:** `"NO_GRADIO_IMAGE_CONTENT"` [packages/app/src/shared/behavior-flags.ts]()

**Purpose:** Strips image content from Gradio tool responses to reduce bandwidth.

**Runtime Check:**

From [packages/app/src/server/mcp-server.ts:731-738]():

```typescript
const stripImageContent = 
    noImageContentHeaderEnabled || 
    toolSelection.enabledToolIds.includes('NO_GRADIO_IMAGE_CONTENT');

const postProcessOptions: GradioToolCallOptions = {
    stripImageContent,
    // ...
};
```

This affects all Gradio tool invocations and applies the image filtering during result post-processing.

Sources: [packages/app/src/shared/behavior-flags.ts](), [packages/app/src/server/mcp-server.ts:512-534](), [packages/app/src/server/mcp-server.ts:731-738]()

### Tool Normalization

The `normalizeBuiltInTools` function ensures consistent tool lists by deduplicating and validating tool IDs.

**Function Signature:**

From [packages/app/src/shared/tool-normalizer.ts]():

```typescript
export function normalizeBuiltInTools(toolIds: string[]): string[]
```

**Normalization Steps:**

1. Deduplicate using `Set` conversion
2. Filter out invalid/unknown tool IDs (optional, based on implementation)
3. Return sorted array for consistent ordering

**Usage Points:**

The function is called at every tool selection result:
- Bouquet override results [line 138]()
- Mix mode results [line 157]()
- User settings results [line 186]()
- Fallback results [line 212]()

This ensures that regardless of the configuration source, the final tool list is consistent and deduplicated.

Sources: [packages/app/src/shared/tool-normalizer.ts](), [packages/app/src/server/utils/tool-selection-strategy.ts:108-221]()

## Header and Parameter Configuration

The Tool Selection System accepts configuration through HTTP headers and URL query parameters, with headers taking precedence when both are present.

### Configuration Headers

| Header Name | Parameter Name | Purpose | Example Value |
|-------------|----------------|---------|---------------|
| `x-mcp-bouquet` | `bouquet` | Override tool selection with bouquet | `search`, `hf_api`, `all` |
| `x-mcp-mix` | `mix` | Add bouquet tools to user settings | `docs`, `spaces` |
| `x-mcp-gradio` | `gradio` | Specify Gradio Space endpoints | `microsoft/Florence-2-large` |
| `x-mcp-no-image-content` | `no_image_content` | Disable Gradio images | `true` |

### Header Extraction

**Code Flow:**

```mermaid
graph LR
    Request["HTTP Request"]
    ExtractFn["extractAuthBouquetAndMix()"]
    Headers["headers object"]
    Result["{ bouquet, mix, gradio }"]
    Context["ToolSelectionContext"]
    
    Request --> Headers
    Headers --> ExtractFn
    ExtractFn --> Result
    Result --> Context
```

**Implementation:**

From [packages/app/src/server/utils/auth-utils.ts]():

```typescript
export function extractAuthBouquetAndMix(headers: Record<string, string> | null): {
    hfToken?: string;
    bouquet?: string;
    mix?: string;
    gradio?: string;
} {
    if (!headers) return {};
    
    return {
        hfToken: headers['authorization']?.replace('Bearer ', ''),
        bouquet: headers['x-mcp-bouquet'],
        mix: headers['x-mcp-mix'],
        gradio: headers['x-mcp-gradio'],
    };
}
```

### URL Parameter Examples

**Basic Bouquet:**
```
https://huggingface.co/mcp?bouquet=search
```

**Mix with Bouquet:**
```
https://huggingface.co/mcp?bouquet=hf_api&mix=docs
```

**Gradio Spaces:**
```
https://huggingface.co/mcp?bouquet=search&gradio=microsoft/Florence-2-large,meta-llama/Llama-2-7b
```

**Disable Gradio Images:**
```
https://huggingface.co/mcp?bouquet=all&no_image_content=true
```

### Web Dashboard Integration

The web dashboard provides a UI for managing tool selection through the internal settings service. Changes made through the dashboard update the settings and trigger `toolStateChange` events for active server instances.

**Settings API Endpoints:**

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/settings` | Retrieve current settings |
| POST | `/api/settings` | Update built-in tools and space tools |

**UI Component Flow:**

```mermaid
graph TD
    UI["Web Dashboard<br/>ToolsCard component"]
    Checkbox["Tool checkbox toggle"]
    OptimisticUpdate["mutate() - Optimistic"]
    APICall["POST /api/settings"]
    Revalidate["mutate() - Revalidate"]
    Event["toolStateChange event"]
    Servers["Active MCP Servers"]
    
    UI --> Checkbox
    Checkbox --> OptimisticUpdate
    OptimisticUpdate --> APICall
    APICall --> Revalidate
    Revalidate --> Event
    Event --> Servers
```

**Implementation:**

From [packages/app/src/web/App.tsx:111-153]():

```typescript
const handleToolToggle = async (toolId: string, checked: boolean) => {
    try {
        // Optimistic update
        const currentSettings = settings || { builtInTools: [] };
        const currentTools = normalizeBuiltInTools(currentSettings.builtInTools);
        const updatedTools = checked
            ? [...currentTools.filter(id => id !== toolId), toolId]
            : currentTools.filter(id => id !== toolId);
        
        mutate('/api/settings', optimisticSettings, false);
        
        // Make the API call
        const response = await fetch('/api/settings', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ builtInTools: newTools }),
        });
        
        // Revalidate
        mutate('/api/settings');
    } catch (err) {
        // Revert on error
        mutate('/api/settings');
    }
};
```

Sources: [packages/app/src/server/utils/auth-utils.ts](), [packages/app/src/web/App.tsx:111-153](), [packages/app/src/web/components/SettingsCopyPage.tsx:1-227]()

## ToolSelectionResult Structure

The `ToolSelectionResult` interface encapsulates the outcome of the tool selection process, providing both the enabled tool list and metadata about how the selection was made.

**Interface Definition:**

From [packages/app/src/server/utils/tool-selection-strategy.ts:24-31]():

```typescript
export interface ToolSelectionResult {
    mode: ToolSelectionMode;
    enabledToolIds: string[];
    reason: string;
    baseSettings?: AppSettings;
    mixedBouquet?: string;
    gradioSpaceTools?: SpaceTool[];
}
```

**Field Descriptions:**

| Field | Type | Purpose | Example |
|-------|------|---------|---------|
| `mode` | `ToolSelectionMode` | Indicates which precedence rule was applied | `BOUQUET_OVERRIDE` |
| `enabledToolIds` | `string[]` | List of enabled built-in tool IDs | `['hf_model_search', 'hf_dataset_search']` |
| `reason` | `string` | Human-readable explanation of selection | `"Bouquet override: search"` |
| `baseSettings` | `AppSettings?` | Original user settings (when applicable) | `{ builtInTools: [...], spaceTools: [...] }` |
| `mixedBouquet` | `string?` | Name of mix bouquet (in MIX mode) | `"docs"` |
| `gradioSpaceTools` | `SpaceTool[]?` | Gradio endpoints from header/parameter | `[{ name: "microsoft/Florence-2-large", ... }]` |

**Result Examples:**

**Bouquet Override:**
```typescript
{
    mode: ToolSelectionMode.BOUQUET_OVERRIDE,
    enabledToolIds: ['hf_semantic_search', 'hf_model_search', ...],
    reason: "Bouquet override: search",
    gradioSpaceTools: undefined
}
```

**Mix Mode:**
```typescript
{
    mode: ToolSelectionMode.MIX,
    enabledToolIds: ['hf_whoami', 'hf_model_search', 'hf_dataset_search', ...],
    reason: "User settings + mix(hf_api)",
    baseSettings: { builtInTools: ['hf_whoami'], spaceTools: [] },
    mixedBouquet: "hf_api"
}
```

**Gradio Included:**
```typescript
{
    mode: ToolSelectionMode.BOUQUET_OVERRIDE,
    enabledToolIds: ['hf_semantic_search', ...],
    reason: "Bouquet override: search + 2 gradio endpoints",
    gradioSpaceTools: [
        { _id: "gradio_metadata_microsoft-Florence-2-large", 
          name: "microsoft/Florence-2-large", ... },
        { _id: "gradio_metadata_meta-llama-Llama-2-7b-chat-hf",
          name: "meta-llama/Llama-2-7b-chat-hf", ... }
    ]
}
```

**Logging:**

The result is logged at server creation time [packages/app/src/server/mcp-server.ts:840-849]():

```typescript
logger.info({
    mode: toolSelection.mode,
    reason: toolSelection.reason,
    enabledCount: toolSelection.enabledToolIds.length,
    totalTools: Object.keys(toolInstances).length,
    mixedBouquet: toolSelection.mixedBouquet,
}, 'Tool selection strategy applied');
```

Sources: [packages/app/src/server/utils/tool-selection-strategy.ts:24-31](), [packages/app/src/server/mcp-server.ts:840-849]()

---

# Page: Bouquet System

# Bouquet System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [packages/app/src/server/utils/tool-selection-strategy.ts](packages/app/src/server/utils/tool-selection-strategy.ts)
- [packages/app/src/shared/bouquet-presets.ts](packages/app/src/shared/bouquet-presets.ts)
- [packages/app/src/web/components/SettingsCopyPage.tsx](packages/app/src/web/components/SettingsCopyPage.tsx)
- [packages/app/src/web/components/bouquets/ToolPresetsCard.tsx](packages/app/src/web/components/bouquets/ToolPresetsCard.tsx)
- [packages/app/test/server/utils/tool-selection-strategy.test.ts](packages/app/test/server/utils/tool-selection-strategy.test.ts)

</details>



## Purpose and Scope

This document describes the **bouquet system**, which provides predefined tool groups (called "bouquets") that allow clients to quickly configure which MCP tools are available. Bouquets are static configurations defined in code that map friendly names (like `"search"` or `"spaces"`) to specific sets of built-in tools.

For information about how bouquets are used in the tool selection precedence system, see [Tool Selection Strategy](#5.2). For information about user-configurable tool settings, see [User Settings](#5.3).

---

## What are Bouquets?

A **bouquet** is a predefined, named configuration of tools stored in the `BOUQUETS` constant. Each bouquet consists of:
- A **key** (e.g., `"search"`, `"hf_api"`)
- A list of **built-in tool IDs** to enable
- An optional list of **space tools** (Gradio endpoints)

Bouquets serve two primary purposes:
1. **Override mode**: Replace user settings entirely with a specific tool set
2. **Mix mode**: Augment user settings by adding tools from a bouquet

The bouquet system is implemented as an `AppSettings` configuration, making it structurally identical to user settings but with predefined values that cannot be modified at runtime.

Sources: [packages/app/src/shared/bouquet-presets.ts:13-59]()

---

## Bouquet Definition Structure

```mermaid
graph TB
    subgraph "Core Type Definition"
        AppSettings["AppSettings<br/>────────<br/>builtInTools: string[]<br/>spaceTools: SpaceTool[]"]
    end
    
    subgraph "Bouquet Registry"
        BOUQUETS["BOUQUETS: Record&lt;string, AppSettings&gt;<br/>────────<br/>Constant mapping of bouquet names to configurations"]
        
        CoreBouquets["Core Bouquets<br/>────────<br/>hf_api<br/>search<br/>spaces<br/>docs<br/>all"]
        
        AdvancedBouquets["Advanced Bouquets<br/>────────<br/>hub_repo_details_readme<br/>hub_repo_details<br/>no_gradio_images<br/>mcp_ui<br/>jobs<br/>dynamic_space"]
    end
    
    subgraph "Tool ID Groups"
        TOOL_ID_GROUPS["TOOL_ID_GROUPS<br/>────────<br/>from @llmindset/hf-mcp<br/>Predefined tool collections"]
        
        ALL_BUILTIN_TOOL_IDS["ALL_BUILTIN_TOOL_IDS<br/>────────<br/>Complete list of 15+ tools"]
    end
    
    subgraph "Metadata System"
        PRESET_META["PRESET_META<br/>────────<br/>Display labels<br/>Descriptions<br/>Category<br/>Support flags"]
        
        BouquetPreset["BouquetPreset Interface<br/>────────<br/>key: BouquetKey<br/>label: string<br/>description: string<br/>category: 'core' | 'advanced'<br/>supportsBouquet: boolean<br/>supportsMix: boolean<br/>builtInTools: readonly string[]"]
        
        BOUQUET_PRESETS["BOUQUET_PRESETS: BouquetPreset[]<br/>────────<br/>Public API for UI components"]
    end
    
    AppSettings --> BOUQUETS
    TOOL_ID_GROUPS --> BOUQUETS
    ALL_BUILTIN_TOOL_IDS --> BOUQUETS
    BOUQUETS --> CoreBouquets
    BOUQUETS --> AdvancedBouquets
    PRESET_META --> BouquetPreset
    BOUQUETS --> BouquetPreset
    BouquetPreset --> BOUQUET_PRESETS
```

**Diagram: Bouquet Definition Structure**

The `BOUQUETS` constant maps string keys to `AppSettings` configurations. Tool definitions come from `TOOL_ID_GROUPS` (predefined collections) or `ALL_BUILTIN_TOOL_IDS` (the complete set). The metadata system (`PRESET_META`, `BouquetPreset`) provides display information for UI components without modifying the core configuration.

Sources: [packages/app/src/shared/bouquet-presets.ts:1-12](), [packages/app/src/shared/bouquet-presets.ts:13-59](), [packages/app/src/shared/bouquet-presets.ts:69-78](), [packages/app/src/shared/bouquet-presets.ts:80-170]()

---

## Core Bouquets

The system defines five **core bouquets** intended for general use:

| Bouquet Key | Label | Tool Count | Tool IDs | Description |
|------------|-------|------------|----------|-------------|
| `hf_api` | Hugging Face MCP Defaults | 7 | `TOOL_ID_GROUPS.hf_api` | Balanced search plus repository details for models, datasets, and Spaces |
| `search` | Search Tools | 5 | `TOOL_ID_GROUPS.search` | Semantic search across models, datasets, papers, and docs |
| `spaces` | Spaces Toolkit | 5 | `TOOL_ID_GROUPS.spaces` | Launch, inspect, and manage Spaces |
| `docs` | Hugging Face Documentation | 2 | `TOOL_ID_GROUPS.docs` | Documentation search and fetch tools |
| `all` | All Built-in Tools | 15+ | `ALL_BUILTIN_TOOL_IDS` | Every MCP tool shipped with the server |

### Tool Group Composition

The `TOOL_ID_GROUPS` constant (imported from `@llmindset/hf-mcp`) defines predefined collections:

```typescript
// Example from packages/mcp
TOOL_ID_GROUPS.hf_api = [
  'hf_whoami',
  'hf_model_search', 
  'hf_model_detail',
  'hf_dataset_search',
  'hf_dataset_detail',
  'hf_hub_repo_details',
  'hf_paper_search'
]

TOOL_ID_GROUPS.search = [
  'hf_model_search',
  'hf_dataset_search', 
  'hf_paper_search',
  'hf_semantic_search',
  'hf_doc_search'
]

TOOL_ID_GROUPS.spaces = [
  'hf_semantic_search',
  'hf_duplicate_space',
  'hf_space_info',
  'hf_space_files',
  'hf_use_space'
]

TOOL_ID_GROUPS.docs = [
  'hf_doc_search',
  'hf_doc_fetch'
]
```

Sources: [packages/app/src/shared/bouquet-presets.ts:14-33](), [packages/app/src/shared/bouquet-presets.ts:80-121]()

---

## Advanced Bouquets

The system includes six **advanced bouquets** for specialized use cases:

| Bouquet Key | Label | Purpose | Tools/Flags |
|------------|-------|---------|-------------|
| `hub_repo_details_readme` | Hub Repo + README | Include README sections in responses | `HUB_INSPECT_TOOL_ID`, `README_INCLUDE_FLAG` |
| `hub_repo_details` | Hub Repo Details Only | Repository inspection without README | `HUB_INSPECT_TOOL_ID` |
| `no_gradio_images` | No Gradio Images | Disable image fetching from Gradio | `GRADIO_IMAGE_FILTER_FLAG` |
| `mcp_ui` | MCP UI Preview | Enable MCP-UI compatible tools | `USE_SPACE_TOOL_ID` |
| `jobs` | Run and Manage Jobs | Job scheduling and monitoring | `HF_JOBS_TOOL_ID` |
| `dynamic_space` | Dynamic Space Tools | Runtime Space invocation | `SPACE_SEARCH_TOOL_ID`, `DYNAMIC_SPACE_TOOL_ID` |

### Behavior Flags

Some advanced bouquets include **behavior flags** rather than tool IDs. These flags modify system behavior:

- **`README_INCLUDE_FLAG`** (`"_readme_include"`): Signals that README content should be included in `hub_repo_details` responses
- **`GRADIO_IMAGE_FILTER_FLAG`** (`"_no_gradio_images"`): Prevents image downloads from Gradio endpoints

Behavior flags are processed differently from tool IDs in the normalization pipeline (see `normalizeBuiltInTools` in [Tool Selection Strategy](#5.2)).

Sources: [packages/app/src/shared/bouquet-presets.ts:35-58](), [packages/app/src/shared/bouquet-presets.ts:138-170](), [packages/app/src/shared/behavior-flags.ts]()

---

## Bouquet Metadata System

```mermaid
graph LR
    subgraph "Metadata Definition"
        PRESET_META["PRESET_META<br/>Array&lt;Omit&lt;BouquetPreset, 'builtInTools'&gt;&gt;<br/>────────<br/>Static metadata for each bouquet"]
    end
    
    subgraph "Metadata Properties"
        Key["key: BouquetKey<br/>────────<br/>Lookup identifier"]
        Label["label: string<br/>────────<br/>Display name"]
        Description["description: string<br/>────────<br/>Purpose explanation"]
        Category["category: 'core' | 'advanced'<br/>────────<br/>UI grouping"]
        SupportFlags["supportsBouquet: boolean<br/>supportsMix: boolean<br/>────────<br/>Usage mode flags"]
        DirectParams["directParams?: DirectParamOption[]<br/>────────<br/>Query parameter alternatives"]
    end
    
    subgraph "Merged Output"
        BOUQUET_PRESETS["BOUQUET_PRESETS: BouquetPreset[]<br/>────────<br/>Metadata + actual tool IDs<br/>Used by UI components"]
    end
    
    PRESET_META --> Key
    PRESET_META --> Label
    PRESET_META --> Description
    PRESET_META --> Category
    PRESET_META --> SupportFlags
    PRESET_META --> DirectParams
    
    PRESET_META --> BOUQUET_PRESETS
    BOUQUETS --> BOUQUET_PRESETS
```

**Diagram: Bouquet Metadata System**

The `PRESET_META` array defines display properties for each bouquet. The `BOUQUET_PRESETS` array merges metadata with actual tool configurations from `BOUQUETS`, creating a public API for UI components.

### BouquetPreset Interface

```typescript
interface BouquetPreset {
  key: BouquetKey;
  label: string;
  description: string;
  category: 'core' | 'advanced';
  supportsBouquet: boolean;  // Can be used with x-mcp-bouquet
  supportsMix: boolean;       // Can be used with x-mcp-mix
  builtInTools: readonly string[];
  directParams?: DirectParamOption[];
}
```

- **`supportsBouquet`**: If `true`, bouquet can be used in override mode via `x-mcp-bouquet` header
- **`supportsMix`**: If `true`, bouquet can be used in additive mode via `x-mcp-mix` header
- **`directParams`**: Alternative query parameters (e.g., `no_image_content=true` for `no_gradio_images`)

Sources: [packages/app/src/shared/bouquet-presets.ts:69-78](), [packages/app/src/shared/bouquet-presets.ts:80-170](), [packages/app/src/shared/bouquet-presets.ts:172-179]()

---

## Usage Patterns

```mermaid
sequenceDiagram
    participant Client
    participant Headers as "Request Headers"
    participant extractAuthBouquetAndMix
    participant ToolSelectionStrategy
    participant BOUQUETS
    participant McpServer
    
    rect rgb(250, 250, 250)
        Note over Client,BOUQUETS: Bouquet Override Mode
        Client->>Headers: x-mcp-bouquet: search
        Headers->>extractAuthBouquetAndMix: Parse headers
        extractAuthBouquetAndMix->>ToolSelectionStrategy: bouquet="search"
        ToolSelectionStrategy->>BOUQUETS: Lookup BOUQUETS["search"]
        BOUQUETS-->>ToolSelectionStrategy: builtInTools: [...TOOL_ID_GROUPS.search]
        ToolSelectionStrategy-->>McpServer: enabledToolIds (overrides user settings)
    end
    
    rect rgb(250, 250, 250)
        Note over Client,BOUQUETS: Mix Mode
        Client->>Headers: x-mcp-mix: docs
        Headers->>extractAuthBouquetAndMix: Parse headers
        extractAuthBouquetAndMix->>ToolSelectionStrategy: mix="docs"
        ToolSelectionStrategy->>BOUQUETS: Lookup BOUQUETS["docs"]
        BOUQUETS-->>ToolSelectionStrategy: builtInTools: ["hf_doc_search", "hf_doc_fetch"]
        Note over ToolSelectionStrategy: Merge with user settings
        ToolSelectionStrategy-->>McpServer: enabledToolIds (user + mix)
    end
```

**Diagram: Bouquet Usage Flow**

### Via HTTP Headers

Clients specify bouquets through custom headers:

```http
# Override mode - replaces user settings entirely
x-mcp-bouquet: search

# Mix mode - adds to user settings
x-mcp-mix: docs

# Both can be combined (bouquet takes precedence)
x-mcp-bouquet: hf_api
x-mcp-mix: spaces
```

The `extractAuthBouquetAndMix` function (in [packages/app/src/server/utils/auth-utils.ts]()) parses these headers:

```typescript
interface BouquetAndMixResult {
  bouquet?: string;
  mix?: string;
  gradio?: string;
}

function extractAuthBouquetAndMix(
  headers: Record<string, string> | null
): BouquetAndMixResult
```

### Via Query Parameters

Bouquets can also be specified as URL query parameters:

```
https://huggingface.co/mcp?login&bouquet=search
https://huggingface.co/mcp?login&mix=docs
https://huggingface.co/mcp?login&bouquet=hf_api&mix=spaces
```

Query parameters are converted to headers by the web server layer before reaching `ToolSelectionStrategy`.

### Direct Parameters

Some bouquets (like `no_gradio_images`) use alternative query parameters instead of bouquet/mix syntax:

```
https://huggingface.co/mcp?login&no_image_content=true
```

These are defined in `directParams` and do not use the standard bouquet resolution logic.

Sources: [packages/app/src/server/utils/auth-utils.ts](), [packages/app/src/server/utils/tool-selection-strategy.ts:129-148](), [packages/app/src/web/components/bouquets/ToolPresetsCard.tsx:9-32]()

---

## Bouquet Resolution in Tool Selection

```mermaid
graph TB
    subgraph "ToolSelectionStrategy.selectTools()"
        ExtractHeaders["extractAuthBouquetAndMix(headers)<br/>────────<br/>Extract bouquet, mix, gradio"]
        
        CheckBouquet{"bouquet && BOUQUETS[bouquet]?"}
        CheckMix{"mix && BOUQUETS[mix] && baseSettings?"}
        CheckSettings{"baseSettings?"}
        
        BouquetMode["Mode: BOUQUET_OVERRIDE<br/>────────<br/>enabledToolIds = BOUQUETS[bouquet].builtInTools<br/>Ignores user settings"]
        
        MixMode["Mode: MIX<br/>────────<br/>enabledToolIds = baseSettings.builtInTools + BOUQUETS[mix].builtInTools<br/>Deduplicated"]
        
        SettingsMode["Mode: EXTERNAL_API or INTERNAL_API<br/>────────<br/>enabledToolIds = baseSettings.builtInTools<br/>Uses user settings"]
        
        FallbackMode["Mode: FALLBACK<br/>────────<br/>enabledToolIds = ALL_BUILTIN_TOOL_IDS<br/>All tools enabled"]
        
        Normalize["normalizeBuiltInTools()<br/>────────<br/>Remove duplicates<br/>Filter behavior flags"]
        
        ApplySEF["applySearchEnablesFetch()<br/>────────<br/>Auto-enable hf_doc_fetch if SEARCH_ENABLES_FETCH=true"]
    end
    
    ExtractHeaders --> CheckBouquet
    CheckBouquet -->|Yes| BouquetMode
    CheckBouquet -->|No| CheckMix
    
    CheckMix -->|Yes| MixMode
    CheckMix -->|No| CheckSettings
    
    CheckSettings -->|Yes| SettingsMode
    CheckSettings -->|No| FallbackMode
    
    BouquetMode --> ApplySEF
    MixMode --> ApplySEF
    SettingsMode --> ApplySEF
    FallbackMode --> ApplySEF
    
    ApplySEF --> Normalize
```

**Diagram: Bouquet Resolution Flow in ToolSelectionStrategy**

The `ToolSelectionStrategy.selectTools()` method implements a clear precedence hierarchy:

1. **BOUQUET_OVERRIDE** (highest): If `x-mcp-bouquet` header specifies a valid bouquet, use its tools exclusively
2. **MIX**: If `x-mcp-mix` header specifies a valid bouquet AND user settings exist, merge the bouquet's tools with user settings
3. **USER_SETTINGS**: Use user settings from external or internal API
4. **FALLBACK** (lowest): Enable all tools if no configuration is available

### Precedence Example

```typescript
// Test case showing precedence
const context: ToolSelectionContext = {
  headers: {
    'x-mcp-bouquet': 'search',  // This wins
    'x-mcp-mix': 'hf_api'       // This is ignored
  },
  userSettings: {
    builtInTools: ['hf_whoami'] // This is ignored
  }
};

const result = await strategy.selectTools(context);
// result.mode === ToolSelectionMode.BOUQUET_OVERRIDE
// result.enabledToolIds === TOOL_ID_GROUPS.search
```

The complete precedence rules are documented in [Tool Selection Strategy](#5.2).

Sources: [packages/app/src/server/utils/tool-selection-strategy.ts:129-221](), [packages/app/test/server/utils/tool-selection-strategy.test.ts:118-206]()

---

## Configuration Entry Descriptions

The `describeConfigEntry()` function provides human-readable metadata for tool IDs and behavior flags:

```typescript
interface ConfigEntryDescription {
  id: string;
  label: string;
  description?: string;
  kind: 'tool' | 'behavior-flag';
}

function describeConfigEntry(id: string): ConfigEntryDescription;
```

### Tool Descriptions

```typescript
const TOOL_DESCRIPTIONS: Record<string, Omit<ConfigEntryDescription, 'id' | 'kind'>> = {
  space_search: {
    label: 'Space Search',
    description: 'Semantic search across public Spaces on the Hugging Face Hub.'
  },
  model_search: {
    label: 'Model Search',
    description: 'Find models on the Hub by keyword or capability.'
  },
  // ... additional tool descriptions
};
```

### Behavior Flag Descriptions

```typescript
const BEHAVIOR_FLAG_DESCRIPTIONS: Record<string, ...> = {
  [README_INCLUDE_FLAG]: {
    label: 'Allow README Include',
    description: 'Permit README sections to be returned in responses (advanced).'
  },
  [GRADIO_IMAGE_FILTER_FLAG]: {
    label: 'Skip Gradio Images',
    description: 'Prevent image downloads from Gradio endpoints (advanced).'
  }
};
```

These descriptions are used by UI components (like `ToolPresetsCard`) to display user-friendly information about each tool or flag in a bouquet.

Sources: [packages/app/src/shared/bouquet-presets.ts:181-282](), [packages/app/src/web/components/bouquets/ToolPresetsCard.tsx:34-139]()

---

## UI Integration

```mermaid
graph TB
    subgraph "React Components"
        ToolPresetsCard["ToolPresetsCard<br/>────────<br/>Displays all bouquet presets<br/>Categorized by core/advanced"]
        
        PresetCard["PresetCard<br/>────────<br/>Individual bouquet display<br/>Shows tools, params, copy buttons"]
        
        SettingsCopyPage["SettingsCopyPage<br/>────────<br/>Main settings/setup page<br/>Includes ToolPresetsCard"]
    end
    
    subgraph "Data Layer"
        BOUQUET_PRESETS_Import["import { BOUQUET_PRESETS }<br/>────────<br/>from shared/bouquet-presets"]
        
        describeConfigEntry_Import["import { describeConfigEntry }<br/>────────<br/>from shared/bouquet-presets"]
        
        CoreFilter["CORE_PRESETS = BOUQUET_PRESETS.filter<br/>category === 'core'"]
        
        AdvancedFilter["ADVANCED_PRESETS = BOUQUET_PRESETS.filter<br/>category === 'advanced'"]
    end
    
    subgraph "URL Generation"
        BaseURL["BASE_URL = https://huggingface.co/mcp?login&"]
        
        BouquetURL["bouquet={preset.key}"]
        MixURL["mix={preset.key}"]
        DirectParamURL["no_image_content=true"]
        
        CopyButton["CopyButton<br/>────────<br/>Copy full URL to clipboard"]
    end
    
    SettingsCopyPage --> ToolPresetsCard
    ToolPresetsCard --> PresetCard
    
    ToolPresetsCard --> BOUQUET_PRESETS_Import
    PresetCard --> describeConfigEntry_Import
    
    BOUQUET_PRESETS_Import --> CoreFilter
    BOUQUET_PRESETS_Import --> AdvancedFilter
    
    CoreFilter --> PresetCard
    AdvancedFilter --> PresetCard
    
    PresetCard --> BaseURL
    BaseURL --> BouquetURL
    BaseURL --> MixURL
    BaseURL --> DirectParamURL
    
    BouquetURL --> CopyButton
    MixURL --> CopyButton
    DirectParamURL --> CopyButton
```

**Diagram: Bouquet System UI Integration**

The `ToolPresetsCard` component displays all available bouquets with copy-to-clipboard functionality for URLs. Each bouquet is rendered as a `PresetCard` showing:

1. **Metadata**: Label, description, key, category
2. **Usage modes**: Bouquet and/or mix parameters with color-coded badges
3. **Tool list**: Expanded view of included tools with descriptions
4. **Copy buttons**: One-click copying of pre-configured URLs

### Example URLs Generated

```
Core Preset - Spaces Toolkit:
  Bouquet: https://huggingface.co/mcp?login&bouquet=spaces
  Mix:     https://huggingface.co/mcp?login&mix=spaces

Advanced Preset - No Gradio Images:
  Query:   https://huggingface.co/mcp?login&no_image_content=true
```

Sources: [packages/app/src/web/components/bouquets/ToolPresetsCard.tsx:1-226](), [packages/app/src/web/components/SettingsCopyPage.tsx:1044]()

---

## Testing

The test suite verifies bouquet behavior across all precedence scenarios:

### Test Coverage

| Test Category | Test Cases | File |
|--------------|-----------|------|
| Bouquet Override | 6 tests (search, hf_api, spaces, all, invalid, precedence) | [test/server/utils/tool-selection-strategy.test.ts:118-206]() |
| Mix Mode | 6 tests (hf_api mix, search mix, deduplication, no settings, invalid) | [test/server/utils/tool-selection-strategy.test.ts:209-308]() |
| Gradio Endpoints | 8 tests (bouquet + gradio, mix + gradio, multiple formats) | [test/server/utils/tool-selection-strategy.test.ts:685-799]() |
| SEARCH_ENABLES_FETCH | 7 tests (feature flag behavior with bouquets) | [test/server/utils/tool-selection-strategy.test.ts:516-683]() |

### Example Test Case

```typescript
it('should use bouquet override for search bouquet', async () => {
  const context: ToolSelectionContext = {
    headers: { 'x-mcp-bouquet': 'search' },
    hfToken: 'test-token',
  };

  const result = await strategy.selectTools(context);

  expect(result.mode).toBe(ToolSelectionMode.BOUQUET_OVERRIDE);
  expect(result.enabledToolIds).toEqual(TOOL_ID_GROUPS.search);
  expect(result.reason).toBe('Bouquet override: search');
  expect(result.baseSettings).toBeUndefined();
  expect(result.mixedBouquet).toBeUndefined();
});
```

Sources: [packages/app/test/server/utils/tool-selection-strategy.test.ts:54-90](), [packages/app/test/server/utils/tool-selection-strategy.test.ts:92-514]()

---

# Page: Tool Selection Strategy

# Tool Selection Strategy

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [packages/app/src/server/mcp-server.ts](packages/app/src/server/mcp-server.ts)
- [packages/app/src/server/utils/tool-selection-strategy.ts](packages/app/src/server/utils/tool-selection-strategy.ts)
- [packages/app/src/shared/bouquet-presets.ts](packages/app/src/shared/bouquet-presets.ts)
- [packages/app/src/shared/settings.ts](packages/app/src/shared/settings.ts)
- [packages/app/src/web/App.tsx](packages/app/src/web/App.tsx)
- [packages/app/src/web/components/SettingsCopyPage.tsx](packages/app/src/web/components/SettingsCopyPage.tsx)
- [packages/app/src/web/components/bouquets/ToolPresetsCard.tsx](packages/app/src/web/components/bouquets/ToolPresetsCard.tsx)
- [packages/app/test/server/utils/tool-selection-strategy.test.ts](packages/app/test/server/utils/tool-selection-strategy.test.ts)

</details>



## Purpose and Scope

This document explains the tool selection system that determines which MCP tools are available to a client connection. The `ToolSelectionStrategy` class implements a precedence-based system for selecting built-in tools using bouquets, mixes, and user settings.

For information about:
- Predefined bouquet configurations, see [Bouquet System](#5.1)
- User-configurable settings storage, see [User Settings](#5.3)
- Tool registration and invocation, see [Tool System Overview](#4.1)

## Overview

When a client connects to the MCP server, the system must determine which of the 15+ built-in tools should be available. The `ToolSelectionStrategy` class resolves this by evaluating multiple configuration sources in a strict precedence order, ultimately producing a list of enabled tool IDs.

The strategy is invoked during server instantiation in [packages/app/src/server/mcp-server.ts:114-185]() and returns a `ToolSelectionResult` containing the enabled tools and metadata about how they were selected.

**Sources:** [packages/app/src/server/utils/tool-selection-strategy.ts:1-260](), [packages/app/src/server/mcp-server.ts:96-186]()

## Precedence System

```mermaid
flowchart TD
    Start["Client Connection Request"] --> CheckBouquet{"x-mcp-bouquet<br/>header present?"}
    
    CheckBouquet -->|Yes| ValidBouquet{"Valid<br/>bouquet name?"}
    ValidBouquet -->|Yes| BouquetMode["BOUQUET_OVERRIDE<br/>(Highest Precedence)<br/>Replace entire tool list"]
    ValidBouquet -->|No| CheckMix
    
    CheckBouquet -->|No| CheckMix{"x-mcp-mix<br/>header present?"}
    CheckMix -->|Yes| HasSettings{"User settings<br/>available?"}
    HasSettings -->|Yes| ValidMix{"Valid<br/>mix name?"}
    ValidMix -->|Yes| MixMode["MIX<br/>(Second Precedence)<br/>Add to user settings"]
    ValidMix -->|No| SettingsMode
    
    HasSettings -->|No| FallbackMode
    CheckMix -->|No| CheckUserSettings{"User settings<br/>available?"}
    
    CheckUserSettings -->|Yes| SettingsMode["EXTERNAL_API or INTERNAL_API<br/>(Third Precedence)<br/>Use saved tool list"]
    CheckUserSettings -->|No| FallbackMode["FALLBACK<br/>(Lowest Precedence)<br/>All tools enabled"]
    
    BouquetMode --> ApplyFeatures["Apply SEARCH_ENABLES_FETCH<br/>if enabled"]
    MixMode --> ApplyFeatures
    SettingsMode --> ApplyFeatures
    FallbackMode --> ApplyFeatures
    
    ApplyFeatures --> Normalize["normalizeBuiltInTools<br/>Deduplicate and validate"]
    Normalize --> Result["ToolSelectionResult<br/>enabledToolIds: string[]<br/>mode: ToolSelectionMode<br/>reason: string"]
```

**Precedence Order (highest to lowest):**

| Priority | Mode | Header/Source | Behavior |
|----------|------|---------------|----------|
| 1 | `BOUQUET_OVERRIDE` | `x-mcp-bouquet` | Completely replaces tool list with predefined bouquet |
| 2 | `MIX` | `x-mcp-mix` + user settings | Adds mix bouquet tools to existing user settings |
| 3 | `EXTERNAL_API` / `INTERNAL_API` | User settings from API | Uses saved tool preferences |
| 4 | `FALLBACK` | None | Enables all built-in tools |

The implementation enforces this precedence in [packages/app/src/server/utils/tool-selection-strategy.ts:129-221]() where each level is checked sequentially.

**Sources:** [packages/app/src/server/utils/tool-selection-strategy.ts:34-69](), [packages/app/test/server/utils/tool-selection-strategy.test.ts:92-459]()

## Core Data Structures

```mermaid
classDiagram
    class ToolSelectionContext {
        +headers: Record~string, string~ | null
        +userSettings?: AppSettings
        +hfToken?: string
    }
    
    class ToolSelectionResult {
        +mode: ToolSelectionMode
        +enabledToolIds: string[]
        +reason: string
        +baseSettings?: AppSettings
        +mixedBouquet?: string
        +gradioSpaceTools?: SpaceTool[]
    }
    
    class ToolSelectionMode {
        <<enumeration>>
        BOUQUET_OVERRIDE
        MIX
        EXTERNAL_API
        INTERNAL_API
        FALLBACK
    }
    
    class AppSettings {
        +builtInTools: string[]
        +spaceTools: SpaceTool[]
    }
    
    class ToolSelectionStrategy {
        -apiClient: McpApiClient
        +constructor(apiClient: McpApiClient)
        +selectTools(context: ToolSelectionContext): Promise~ToolSelectionResult~
        -getUserSettings(context: ToolSelectionContext): Promise~AppSettings | null~
        -applySearchEnablesFetch(enabledToolIds: string[]): string[]
        -parseGradioEndpoints(gradioParam: string): SpaceTool[]
    }
    
    ToolSelectionStrategy --> ToolSelectionContext: accepts
    ToolSelectionStrategy --> ToolSelectionResult: returns
    ToolSelectionResult --> ToolSelectionMode: uses
    ToolSelectionResult --> AppSettings: references
    ToolSelectionContext --> AppSettings: contains
```

The `ToolSelectionStrategy` class is instantiated in [packages/app/src/server/mcp-server.ts:115]() and invoked immediately after with the `ToolSelectionContext` at [packages/app/src/server/mcp-server.ts:180-185]().

**Sources:** [packages/app/src/server/utils/tool-selection-strategy.ts:10-31](), [packages/app/src/shared/settings.ts:9-20]()

## The ToolSelectionStrategy Class

### Initialization

```typescript
// Instantiated once per server instance
const toolSelectionStrategy = new ToolSelectionStrategy(sharedApiClient);
```

The strategy requires a `McpApiClient` instance ([packages/app/src/server/utils/tool-selection-strategy.ts:73-75]()) which provides:
- Access to transport information (`externalApiMode` flag)
- Tool state fetching capabilities
- Gradio endpoint information

### selectTools Method

The core method signature:

```typescript
async selectTools(context: ToolSelectionContext): Promise<ToolSelectionResult>
```

**Execution flow:**

```mermaid
sequenceDiagram
    participant SF as ServerFactory
    participant TS as ToolSelectionStrategy
    participant Auth as extractAuthBouquetAndMix
    participant BP as BOUQUETS
    participant API as McpApiClient
    participant Norm as normalizeBuiltInTools
    
    SF->>TS: selectTools(context)
    TS->>Auth: Extract headers
    Auth-->>TS: {bouquet, mix, gradio}
    
    alt Bouquet Override
        TS->>BP: BOUQUETS[bouquet]
        BP-->>TS: AppSettings
        TS->>TS: applySearchEnablesFetch
        TS->>Norm: Deduplicate and validate
        Norm-->>TS: Final tool IDs
        TS-->>SF: ToolSelectionResult<br/>(mode: BOUQUET_OVERRIDE)
    else Mix Mode
        TS->>TS: getUserSettings(context)
        TS->>BP: BOUQUETS[mix]
        TS->>TS: Merge + deduplicate
        TS->>TS: applySearchEnablesFetch
        TS->>Norm: Validate
        TS-->>SF: ToolSelectionResult<br/>(mode: MIX)
    else User Settings
        TS->>TS: getUserSettings(context)
        TS->>API: Check externalApiMode
        TS->>TS: applySearchEnablesFetch
        TS->>Norm: Validate
        TS-->>SF: ToolSelectionResult<br/>(mode: EXTERNAL_API/INTERNAL_API)
    else Fallback
        TS->>TS: Use ALL_BUILTIN_TOOL_IDS
        TS->>TS: applySearchEnablesFetch
        TS->>Norm: Validate
        TS-->>SF: ToolSelectionResult<br/>(mode: FALLBACK)
    end
```

**Sources:** [packages/app/src/server/utils/tool-selection-strategy.ts:129-221](), [packages/app/src/server/mcp-server.ts:180-186]()

## Bouquet Override Mode

### Detection and Application

Bouquets are detected via the `x-mcp-bouquet` header, extracted using `extractAuthBouquetAndMix` utility ([packages/app/src/server/utils/auth-utils.ts]()).

```mermaid
graph LR
    Header["x-mcp-bouquet: search"] --> Extract["extractAuthBouquetAndMix"]
    Extract --> Lookup["BOUQUETS['search']"]
    
    Lookup --> BouquetDef["AppSettings:<br/>builtInTools: [<br/>  'hf_semantic_search',<br/>  'hf_model_search',<br/>  'hf_paper_search',<br/>  'hf_dataset_search',<br/>  'hf_doc_search'<br/>]"]
    
    BouquetDef --> Apply["Replace entire tool list<br/>Ignore user settings"]
    Apply --> Features["applySearchEnablesFetch"]
    Features --> Normalize["normalizeBuiltInTools"]
    Normalize --> Result["enabledToolIds"]
```

The bouquet lookup occurs at [packages/app/src/server/utils/tool-selection-strategy.ts:136-147]() where it checks if `BOUQUETS[bouquet]` exists. Valid bouquet names are defined in [packages/app/src/shared/bouquet-presets.ts:13-59]().

**Key behavior:** Bouquet override completely ignores user settings, providing a deterministic tool set. This is useful for:
- URL-based tool configuration
- Testing specific tool combinations
- Overriding user preferences temporarily

**Sources:** [packages/app/src/server/utils/tool-selection-strategy.ts:136-148](), [packages/app/src/shared/bouquet-presets.ts:13-59]()

## Mix Mode

### Additive Tool Selection

Mix mode combines a bouquet's tools with existing user settings:

```typescript
// Implementation from tool-selection-strategy.ts:154-177
if (mix && BOUQUETS[mix] && baseSettings) {
    const mixedTools = [...baseSettings.builtInTools, ...BOUQUETS[mix].builtInTools];
    const enabledToolIds = normalizeBuiltInTools(
        applySearchEnablesFetch([...new Set(mixedTools)])
    );
    // ...
}
```

**Mix operation visualization:**

```mermaid
graph TD
    UserSettings["User Settings<br/>builtInTools: [<br/>  'hf_whoami',<br/>  'hf_duplicate_space'<br/>]"] --> Merge
    
    MixBouquet["Mix: 'hf_api'<br/>BOUQUETS['hf_api'].builtInTools: [<br/>  'hf_model_search',<br/>  'hf_model_detail',<br/>  'hf_dataset_search',<br/>  'hf_dataset_detail',<br/>  ...<br/>]"] --> Merge
    
    Merge["Concatenate Arrays<br/>[...baseSettings.builtInTools,<br/>...BOUQUETS[mix].builtInTools]"] --> Dedupe["Deduplicate<br/>[...new Set(mixedTools)]"]
    
    Dedupe --> Features["applySearchEnablesFetch"]
    Features --> Normalize["normalizeBuiltInTools"]
    Normalize --> Final["Final Enabled Tools:<br/>'hf_whoami',<br/>'hf_duplicate_space',<br/>'hf_model_search',<br/>'hf_model_detail',<br/>..."]
```

**Requirements:** Mix mode requires user settings to be available. If no settings exist, it falls through to fallback mode ([packages/app/src/server/utils/tool-selection-strategy.ts:280-288]()).

**Sources:** [packages/app/src/server/utils/tool-selection-strategy.ts:154-177](), [packages/app/test/server/utils/tool-selection-strategy.test.ts:209-308]()

## User Settings Mode

### Internal vs External API

The mode determination depends on the `McpApiClient` configuration:

| Mode | Trigger | Settings Source |
|------|---------|----------------|
| `INTERNAL_API` | `externalApiMode=false` | In-memory `settingsService` |
| `EXTERNAL_API` | `externalApiMode=true` | External HTTP endpoint |

Detection occurs at [packages/app/src/server/utils/tool-selection-strategy.ts:182-184]():

```typescript
const mode = this.apiClient.getTransportInfo()?.externalApiMode
    ? ToolSelectionMode.EXTERNAL_API
    : ToolSelectionMode.INTERNAL_API;
```

### getUserSettings Implementation

```mermaid
flowchart TD
    Start["getUserSettings(context)"] --> CheckProvided{"context.userSettings<br/>provided?"}
    
    CheckProvided -->|Yes| ReturnProvided["Return provided settings<br/>(from proxy mode)"]
    
    CheckProvided -->|No| CheckEnv{"Test environment?<br/>(NODE_ENV='test')"}
    CheckEnv -->|Yes| ReturnNull["Return null"]
    
    CheckEnv -->|No| FetchAPI["apiClient.getToolStates(hfToken)"]
    FetchAPI --> CheckResult{"toolStates<br/>received?"}
    
    CheckResult -->|Yes| BuildSettings["Build AppSettings:<br/>- builtInTools: enabled tool IDs<br/>- spaceTools: from gradio endpoints"]
    BuildSettings --> ReturnSettings["Return AppSettings"]
    
    CheckResult -->|No| CatchError["Catch error<br/>Log warning"]
    CatchError --> ReturnNull
    
    ReturnProvided --> End
    ReturnSettings --> End
    ReturnNull --> End
```

The implementation at [packages/app/src/server/utils/tool-selection-strategy.ts:226-258]() handles three cases:
1. Pre-provided settings (from stateless proxy mode)
2. Test environment (skip API call)
3. Normal operation (fetch from API client)

**Sources:** [packages/app/src/server/utils/tool-selection-strategy.ts:180-208](), [packages/app/src/server/utils/tool-selection-strategy.ts:226-258]()

## Fallback Mode

### All Tools Enabled

Fallback mode activates when no configuration is available:

```typescript
// From tool-selection-strategy.ts:210-220
logger.warn('No settings available, using fallback (all tools enabled)');
const enabledToolIds = normalizeBuiltInTools(
    applySearchEnablesFetch([...ALL_BUILTIN_TOOL_IDS])
);
return {
    mode: ToolSelectionMode.FALLBACK,
    enabledToolIds,
    reason: `Fallback - no settings available...`,
    gradioSpaceTools: gradioSpaceTools.length > 0 ? gradioSpaceTools : undefined,
};
```

**When fallback occurs:**
- No bouquet header specified
- No mix header specified
- No user settings available (API call failed or not configured)
- Invalid bouquet/mix names provided

The `ALL_BUILTIN_TOOL_IDS` constant is imported from `@llmindset/hf-mcp` package and contains all 15+ built-in tool IDs.

**Sources:** [packages/app/src/server/utils/tool-selection-strategy.ts:210-220](), [packages/app/test/server/utils/tool-selection-strategy.test.ts:370-396]()

## SEARCH_ENABLES_FETCH Feature

### Automatic Tool Enhancement

The `SEARCH_ENABLES_FETCH` environment variable enables automatic addition of `hf_doc_fetch` when `hf_doc_search` is enabled:

```mermaid
graph TD
    ToolList["enabledToolIds:<br/>[..., 'hf_doc_search', ...]"] --> CheckEnv{"process.env<br/>SEARCH_ENABLES_FETCH<br/>== 'true'?"}
    
    CheckEnv -->|No| Return["Return unchanged"]
    
    CheckEnv -->|Yes| CheckSearch{"'hf_doc_search'<br/>in enabledToolIds?"}
    CheckSearch -->|No| Return
    
    CheckSearch -->|Yes| CheckFetch{"'hf_doc_fetch'<br/>already present?"}
    CheckFetch -->|Yes| Return
    
    CheckFetch -->|No| Add["Add 'hf_doc_fetch'<br/>to array"]
    Add --> Log["logger.debug:<br/>'Auto-enabling hf_doc_fetch...'"]
    Log --> Return
```

**Implementation:**

The logic is contained in [packages/app/src/server/utils/tool-selection-strategy.ts:108-116]():

```typescript
private applySearchEnablesFetch(enabledToolIds: string[]): string[] {
    if (process.env.SEARCH_ENABLES_FETCH === 'true') {
        if (enabledToolIds.includes('hf_doc_search') && !enabledToolIds.includes('hf_doc_fetch')) {
            logger.debug('SEARCH_ENABLES_FETCH: Auto-enabling hf_doc_fetch because hf_doc_search is enabled');
            return [...enabledToolIds, 'hf_doc_fetch'];
        }
    }
    return enabledToolIds;
}
```

This method is called in every precedence mode before returning the result:
- Bouquet override: [packages/app/src/server/utils/tool-selection-strategy.ts:139]()
- Mix mode: [packages/app/src/server/utils/tool-selection-strategy.ts:157]()
- User settings: [packages/app/src/server/utils/tool-selection-strategy.ts:187]()
- Fallback: [packages/app/src/server/utils/tool-selection-strategy.ts:213]()

**Sources:** [packages/app/src/server/utils/tool-selection-strategy.ts:104-116](), [packages/app/test/server/utils/tool-selection-strategy.test.ts:516-683]()

## Gradio Endpoint Handling

### Independent from Built-in Tool Selection

The `gradio` parameter is parsed independently and included in all selection modes:

```mermaid
sequenceDiagram
    participant Strategy as ToolSelectionStrategy
    participant Extract as extractAuthBouquetAndMix
    participant Parse as parseGradioEndpoints
    
    Strategy->>Extract: Parse headers
    Extract-->>Strategy: {bouquet, mix, gradio}
    
    alt gradio parameter exists
        Strategy->>Parse: parseGradioEndpoints(gradio)
        Parse->>Parse: parseGradioSpaceIds(gradioParam)
        Parse->>Parse: Convert to SpaceTool format<br/>(placeholder subdomains)
        Parse-->>Strategy: SpaceTool[]
    else No gradio parameter
        Strategy->>Strategy: gradioSpaceTools = []
    end
    
    Note over Strategy: Built-in tool selection<br/>(bouquet/mix/settings/fallback)
    
    Strategy->>Strategy: Append gradioSpaceTools<br/>to ToolSelectionResult
```

**Important distinction:** The `parseGradioEndpoints` method at [packages/app/src/server/utils/tool-selection-strategy.ts:85-102]() only creates **metadata** with placeholder subdomains. Actual Gradio endpoint registration with real subdomains happens separately in the proxy factory.

From the class documentation ([packages/app/src/server/utils/tool-selection-strategy.ts:36-68]()):

```
## Two Independent Systems

1. **Built-in Tool Selection** (handled by this class):
   - Controlled by: bouquet, mix, and user settings
   - Affects: Built-in HuggingFace MCP tools only
   - Returns: enabledToolIds array

2. **Gradio Endpoint Registration** (handled by mcp-proxy.ts):
   - Controlled by: gradio parameter + user settings spaceTools
   - Affects: Dynamic Gradio Space endpoints
   - Works with any bouquet when explicitly specified via gradio=
   - Special: gradio="none" disables all Gradio endpoints
```

**Sources:** [packages/app/src/server/utils/tool-selection-strategy.ts:36-68](), [packages/app/src/server/utils/tool-selection-strategy.ts:78-102](), [packages/app/test/server/utils/tool-selection-strategy.test.ts:685-799]()

## Integration with MCP Server

### Server Factory Usage

The `ToolSelectionStrategy` is integrated into the server creation flow:

```mermaid
sequenceDiagram
    participant Client
    participant Transport
    participant Factory as createServerFactory
    participant Strategy as ToolSelectionStrategy
    participant Server as McpServer
    participant Tools as Tool Instances
    
    Client->>Transport: Connect
    Transport->>Factory: createServerFactory(headers, settings)
    
    Factory->>Strategy: new ToolSelectionStrategy(apiClient)
    Factory->>Strategy: selectTools(context)
    Strategy-->>Factory: ToolSelectionResult
    
    Factory->>Server: new McpServer(...)
    Factory->>Factory: Register all 15+ tools
    
    loop For each tool
        Factory->>Tools: server.tool(name, desc, schema, handler)
        Tools-->>Factory: Tool instance
        Factory->>Factory: Store in toolInstances[name]
    end
    
    Factory->>Factory: applyToolStates()
    
    loop For each tool
        alt Tool in enabledToolIds
            Factory->>Tools: toolInstance.enable()
        else Tool not in enabledToolIds
            Factory->>Tools: toolInstance.disable()
        end
    end
    
    Factory-->>Transport: {server, userDetails}
```

**Key implementation points:**

1. Strategy creation at [packages/app/src/server/mcp-server.ts:115]()
2. Tool selection at [packages/app/src/server/mcp-server.ts:180-185]()
3. All tools are registered regardless of selection ([packages/app/src/server/mcp-server.ts:191]())
4. Tool states are applied at [packages/app/src/server/mcp-server.ts:839-859]()

This approach allows dynamic enabling/disabling of tools without recreating the server instance.

**Sources:** [packages/app/src/server/mcp-server.ts:96-186](), [packages/app/src/server/mcp-server.ts:839-894]()

## Normalization and Validation

### normalizeBuiltInTools Function

Every tool selection result passes through `normalizeBuiltInTools` for consistency:

```mermaid
graph TD
    Input["Tool IDs array<br/>(may contain duplicates,<br/>flags, or invalid IDs)"] --> Dedupe["[...new Set(tools)]<br/>Remove duplicates"]
    
    Dedupe --> Filter["Filter out behavior flags:<br/>- README_INCLUDE_FLAG<br/>- GRADIO_IMAGE_FILTER_FLAG<br/>- NO_GRADIO_IMAGE_CONTENT"]
    
    Filter --> Validate["Validate against<br/>ALL_BUILTIN_TOOL_IDS"]
    
    Validate --> Result["Normalized tool IDs"]
    
    style Filter fill:#f9f9f9
    style Validate fill:#f9f9f9
```

The normalization function is imported from [packages/app/src/shared/tool-normalizer.ts]() and called in every precedence mode:
- Bouquet: [packages/app/src/server/utils/tool-selection-strategy.ts:138-140]()
- Mix: [packages/app/src/server/utils/tool-selection-strategy.ts:156-158]()
- Settings: [packages/app/src/server/utils/tool-selection-strategy.ts:186-188]()
- Fallback: [packages/app/src/server/utils/tool-selection-strategy.ts:212-214]()

**Sources:** [packages/app/src/shared/tool-normalizer.ts](), [packages/app/src/server/utils/tool-selection-strategy.ts:138-214]()

## Testing Strategy

### Comprehensive Test Coverage

The test suite at [packages/app/test/server/utils/tool-selection-strategy.test.ts]() validates all precedence modes:

| Test Category | Coverage |
|--------------|----------|
| Bouquet Override | Valid/invalid bouquets, all bouquet types, precedence over mix |
| Mix Mode | Additive behavior, deduplication, invalid mix handling |
| User Settings | Internal/external API modes, empty settings |
| Fallback Mode | No config, null headers, failed API calls |
| SEARCH_ENABLES_FETCH | Enabled/disabled states, all modes |
| Gradio Endpoints | Independent parsing, all modes |

**Example test structure:**

```typescript
describe('Bouquet Override (Highest Precedence)', () => {
    it('should use bouquet override for search bouquet', async () => {
        const context: ToolSelectionContext = {
            headers: { 'x-mcp-bouquet': 'search' },
            hfToken: 'test-token',
        };
        const result = await strategy.selectTools(context);
        expect(result.mode).toBe(ToolSelectionMode.BOUQUET_OVERRIDE);
        expect(result.enabledToolIds).toEqual(TOOL_ID_GROUPS.search);
    });
});
```

**Sources:** [packages/app/test/server/utils/tool-selection-strategy.test.ts:1-801]()

---

# Page: User Settings

# User Settings

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [packages/app/src/server/application.ts](packages/app/src/server/application.ts)
- [packages/app/src/server/utils/tool-selection-strategy.ts](packages/app/src/server/utils/tool-selection-strategy.ts)
- [packages/app/src/server/web-server.ts](packages/app/src/server/web-server.ts)
- [packages/app/src/shared/bouquet-presets.ts](packages/app/src/shared/bouquet-presets.ts)
- [packages/app/src/web/components/SettingsCopyPage.tsx](packages/app/src/web/components/SettingsCopyPage.tsx)
- [packages/app/src/web/components/bouquets/ToolPresetsCard.tsx](packages/app/src/web/components/bouquets/ToolPresetsCard.tsx)
- [packages/app/test/server/utils/tool-selection-strategy.test.ts](packages/app/test/server/utils/tool-selection-strategy.test.ts)

</details>



User settings define which built-in tools and Gradio Space endpoints are available to clients connecting to the MCP server. Settings can be stored internally (in-memory) or fetched from an external API, providing flexibility for different deployment scenarios. This page covers settings structure, storage modes, management interfaces, and integration with the tool selection system.

For information about how user settings interact with bouquets and mix parameters in the tool selection precedence hierarchy, see [Tool Selection Strategy](#5.2). For details on available tool presets, see [Bouquet System](#5.1).

---

## Settings Storage Modes

The MCP server supports two storage modes for user settings, controlled by the `USER_CONFIG_API` environment variable.

### Internal Storage Mode

When `USER_CONFIG_API` is not set, settings are stored in-memory using `settingsService`. This mode provides a simple local storage solution suitable for single-instance deployments.

```mermaid
graph TB
    subgraph "Internal Storage Mode"
        Client["Client Request"]
        WebAPI["/api/settings<br/>Express Endpoints"]
        SettingsService["settingsService<br/>In-Memory Map"]
        McpApiClient["McpApiClient"]
        ToolSelection["ToolSelectionStrategy"]
        
        Client -->|"GET/POST"| WebAPI
        WebAPI -->|"getSettings()<br/>updateBuiltInTools()<br/>updateSpaceTools()"| SettingsService
        ToolSelection -->|"fetch settings"| McpApiClient
        McpApiClient -->|"polls every 5s"| WebAPI
        WebAPI -->|"reads"| SettingsService
    end
    
    note1["• No persistence across restarts<br/>• Single server instance<br/>• No external dependencies"]
```

**Sources:** [packages/app/src/server/web-server.ts:375-413](), [packages/app/src/server/application.ts:67-86]()

### External API Mode

When `USER_CONFIG_API` is set to a remote endpoint URL, the server fetches settings from that external API. This enables centralized configuration management across multiple server instances.

```mermaid
graph TB
    subgraph "External API Mode"
        Client["Client Request"]
        McpApiClient["McpApiClient<br/>External Mode"]
        ExternalAPI["USER_CONFIG_API<br/>Remote Endpoint"]
        ToolSelection["ToolSelectionStrategy"]
        
        Client -->|"connects"| ToolSelection
        ToolSelection -->|"getUserSettings()"| McpApiClient
        McpApiClient -->|"HTTP GET<br/>with HF_TOKEN"| ExternalAPI
        ExternalAPI -->|"returns AppSettings"| McpApiClient
    end
    
    note2["• Settings persist externally<br/>• Multi-instance support<br/>• Centralized management"]
```

**Sources:** [packages/app/src/server/application.ts:67-77](), [packages/app/src/server/utils/tool-selection-strategy.ts:226-258]()

---

## Settings Structure

User settings conform to the `AppSettings` interface with two primary configuration arrays.

### Built-in Tools Configuration

The `builtInTools` array contains tool IDs for standard MCP tools. Valid tool IDs are defined in `ALL_BUILTIN_TOOL_IDS` from the `@llmindset/hf-mcp` package.

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `builtInTools` | `string[]` | Array of enabled tool IDs | `["hf_model_search", "hf_dataset_search"]` |

**Common Tool ID Groups:**
- **Search Tools**: `hf_model_search`, `hf_dataset_search`, `hf_paper_search`, `hf_doc_search`, `hf_semantic_search`
- **Detail Tools**: `model_details`, `dataset_details`, `hub_repo_details`
- **Space Tools**: `duplicate_space`, `space_info`, `space_files`, `use_space`
- **Documentation**: `hf_doc_search`, `hf_doc_fetch`

**Sources:** [packages/app/src/shared/settings.ts]() (referenced), [packages/app/src/server/web-server.ts:382-393]()

### Space Tools Configuration

The `spaceTools` array defines custom Gradio Space endpoints that will be dynamically registered as MCP tools.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | `string` | Yes | Display name for the Space tool |
| `subdomain` | `string` | Yes | HuggingFace subdomain (e.g., `user-space-name`) |
| `_id` | `string` | Yes | Unique identifier for this endpoint |
| `emoji` | `string` | No | Optional emoji for UI display |

**Example SpaceTool:**
```typescript
{
  name: "Florence-2 Vision",
  subdomain: "microsoft-Florence-2-large",
  _id: "gradio_florence2",
  emoji: "👁️"
}
```

**Sources:** [packages/app/src/shared/settings.ts:8]() (type reference), [packages/app/src/server/application.ts:52-60]()

---

## Managing Settings

Settings can be managed through the web dashboard UI or directly via API endpoints.

### Web Dashboard

The web dashboard provides two primary interfaces for settings management:

```mermaid
graph LR
    subgraph "Web Dashboard Components"
        SettingsCopyPage["SettingsCopyPage<br/>Client Setup Instructions"]
        ToolPresetsCard["ToolPresetsCard<br/>Bouquet Configuration"]
        
        SettingsCopyPage -->|"fetches"| SettingsAPI["/api/settings"]
        ToolPresetsCard -->|"displays"| BouquetConfig["Bouquet Presets<br/>BOUQUETS constant"]
    end
    
    SettingsAPI -->|"GET/POST"| SettingsService["settingsService"]
```

- **SettingsCopyPage**: Displays setup instructions for connecting various clients (Claude, VS Code, Cursor, Gemini CLI, etc.) with pre-configured URLs and authentication options
- **ToolPresetsCard**: Shows available bouquet presets with copy buttons for quick URL generation

**Sources:** [packages/app/src/web/components/SettingsCopyPage.tsx:1-835](), [packages/app/src/web/components/bouquets/ToolPresetsCard.tsx:1-227]()

### API Endpoints

The server exposes REST endpoints for programmatic settings management:

#### GET /api/settings

Returns current user settings.

**Response:**
```json
{
  "builtInTools": ["hf_model_search", "hf_dataset_search"],
  "spaceTools": [
    {
      "name": "WebSearch",
      "subdomain": "victor-websearch",
      "_id": "websearch",
      "emoji": "🔍"
    }
  ]
}
```

#### POST /api/settings

Updates user settings. Supports partial updates - only specify fields to change.

**Request Body:**
```json
{
  "builtInTools": ["hf_model_search", "hf_doc_search"],
  "spaceTools": []
}
```

**Response:** Returns updated settings (same format as GET).

**Sources:** [packages/app/src/server/web-server.ts:375-413]()

### Gradio Endpoints Management

Separate endpoints manage Gradio Space tool configurations:

#### GET /api/gradio-endpoints

Returns list of registered Gradio endpoints with current state.

#### POST /api/gradio-endpoints/:index

Updates enabled state for a specific endpoint.

**Request Body:**
```json
{
  "enabled": true
}
```

#### PUT /api/gradio-endpoints/:index

Updates endpoint metadata (name, subdomain, id, emoji).

**Sources:** [packages/app/src/server/web-server.ts:415-488]()

---

## Event System

Settings changes trigger events that propagate to all active MCP server instances, enabling dynamic tool availability updates without requiring client reconnection.

```mermaid
sequenceDiagram
    participant WebUI as Web Dashboard
    participant API as POST /api/settings
    participant WS as WebServer
    participant Store as settingsService
    participant Client as McpApiClient
    participant MCP as MCP Server Instances
    
    WebUI->>API: Update builtInTools
    API->>Store: updateBuiltInTools(toolIds)
    Store-->>API: Updated settings
    
    loop For each changed tool
        API->>API: Compare old vs new state
        alt Tool state changed
            API->>Client: emit('toolStateChange', toolId, enabled)
            Client->>MCP: Notify all instances
            MCP->>MCP: Update tool availability
        end
    end
    
    API-->>WebUI: Return updated settings
```

**Key Implementation Details:**

1. **State Tracking**: WebServer maintains `localSharedToolStates` map to track previous tool states
2. **Change Detection**: Only tools whose enabled state actually changed trigger events
3. **Event Broadcasting**: `McpApiClient.emit('toolStateChange')` notifies all server instances
4. **No Disruption**: Active client connections continue working with updated tool sets

**Sources:** [packages/app/src/server/web-server.ts:129-136](), [packages/app/src/server/web-server.ts:395-410]()

---

## Integration with Tool Selection

User settings integrate into the tool selection precedence hierarchy as the third-priority source, after bouquet overrides and mix operations.

```mermaid
graph TB
    subgraph "Tool Selection Precedence"
        Headers["x-mcp-bouquet<br/>x-mcp-mix<br/>x-mcp-gradio"]
        
        Check1{"Bouquet<br/>Override?"}
        Check2{"Mix<br/>Operation?"}
        Check3{"User<br/>Settings?"}
        
        Bouquet["BOUQUET_OVERRIDE<br/>Replace tool list"]
        Mix["MIX<br/>Add to user settings"]
        Internal["INTERNAL_API<br/>Use settingsService"]
        External["EXTERNAL_API<br/>Fetch from USER_CONFIG_API"]
        Fallback["FALLBACK<br/>All tools enabled"]
        
        Headers --> Check1
        Check1 -->|"Yes"| Bouquet
        Check1 -->|"No"| Check2
        Check2 -->|"Yes + have settings"| Mix
        Check2 -->|"No"| Check3
        Check3 -->|"External mode"| External
        Check3 -->|"Internal mode"| Internal
        Check3 -->|"None available"| Fallback
    end
```

### Mode Determination

The `ToolSelectionStrategy` determines which mode to use based on configuration and context:

| Mode | Trigger | Tool Source |
|------|---------|-------------|
| `BOUQUET_OVERRIDE` | `x-mcp-bouquet` header present | Predefined bouquet from `BOUQUETS` |
| `MIX` | `x-mcp-mix` header + user settings | User settings + bouquet tools (deduplicated) |
| `EXTERNAL_API` | `USER_CONFIG_API` set, no override/mix | External API endpoint |
| `INTERNAL_API` | No `USER_CONFIG_API`, no override/mix | `settingsService` in-memory storage |
| `FALLBACK` | No settings available | All built-in tools enabled |

**Sources:** [packages/app/src/server/utils/tool-selection-strategy.ts:10-31](), [packages/app/src/server/utils/tool-selection-strategy.ts:129-221]()

### getUserSettings Flow

The `ToolSelectionStrategy.getUserSettings()` method resolves settings from multiple sources:

```mermaid
graph TB
    Context["ToolSelectionContext"]
    
    Check1{"userSettings<br/>provided?"}
    Check2{"Test<br/>environment?"}
    Check3{"API fetch<br/>succeeds?"}
    
    ProvidedSettings["Use provided<br/>userSettings"]
    SkipFetch["Return null<br/>(test mode)"]
    FetchAPI["apiClient.getToolStates()"]
    ConvertSettings["Convert to<br/>AppSettings"]
    ReturnNull["Return null"]
    
    Context --> Check1
    Check1 -->|"Yes"| ProvidedSettings
    Check1 -->|"No"| Check2
    Check2 -->|"Yes"| SkipFetch
    Check2 -->|"No"| FetchAPI
    FetchAPI --> Check3
    Check3 -->|"Yes"| ConvertSettings
    Check3 -->|"No"| ReturnNull
```

**Sources:** [packages/app/src/server/utils/tool-selection-strategy.ts:226-258]()

---

## Default Space Tools

The system provides a shared set of default Space tools when external settings are unavailable.

```mermaid
graph LR
    subgraph "Default Space Tools Initialization"
        DEFAULT_SPACE_TOOLS["DEFAULT_SPACE_TOOLS<br/>Shared Constant"]
        
        AppConfig["Application Constructor"]
        ApiClient["McpApiClient<br/>Polling Mode"]
        
        DEFAULT_SPACE_TOOLS -->|"converts to"| GradioEndpoints["GradioEndpoint[]"]
        GradioEndpoints -->|"staticGradioEndpoints"| ApiClient
        AppConfig -->|"creates"| ApiClient
    end
```

**Conversion Logic:**
- SpaceTool `_id` → GradioEndpoint `id`
- SpaceTool `subdomain` → GradioEndpoint `subdomain`
- SpaceTool `name` → GradioEndpoint `name`
- SpaceTool `emoji` → GradioEndpoint `emoji`

**Sources:** [packages/app/src/server/application.ts:52-64]()

---

## Practical Examples

### Example 1: Internal Mode with Custom Tools

Configure a minimal set of search tools for focused workflows:

```typescript
// POST /api/settings
{
  "builtInTools": [
    "hf_model_search",
    "hf_dataset_search"
  ],
  "spaceTools": []
}
```

### Example 2: External API Mode Setup

```bash
# Set environment variable
export USER_CONFIG_API="https://config.example.com/api/mcp-settings"
export DEFAULT_HF_TOKEN="hf_..."

# Server fetches settings from external API on each request
# Settings persist across server restarts
```

### Example 3: Adding Custom Gradio Spaces

```typescript
// POST /api/settings
{
  "spaceTools": [
    {
      "name": "Custom GPT Assistant",
      "subdomain": "myorg-custom-gpt",
      "_id": "custom_gpt_1",
      "emoji": "🤖"
    },
    {
      "name": "Document Analyzer",
      "subdomain": "myteam-doc-analyzer",
      "_id": "doc_analyzer",
      "emoji": "📄"
    }
  ]
}
```

### Example 4: Mix Mode with User Settings

User has minimal settings saved but wants to temporarily add search tools:

```
# User settings stored: ["hf_whoami", "duplicate_space"]
# Request URL: https://huggingface.co/mcp?login&mix=search

# Result: User tools + search bouquet tools (deduplicated)
# Final tools: ["hf_whoami", "duplicate_space", "hf_model_search", 
#               "hf_dataset_search", "hf_paper_search", "hf_doc_search", 
#               "hf_semantic_search"]
```

**Sources:** [packages/app/test/server/utils/tool-selection-strategy.test.ts:210-253](), [packages/app/test/server/utils/tool-selection-strategy.test.ts:461-513]()

---

## Testing User Settings

The test suite validates all settings modes and precedence rules:

### Key Test Scenarios

| Test Case | Location | Purpose |
|-----------|----------|---------|
| Provided user settings | [test file:311-329]() | Verifies INTERNAL_API mode with explicit settings |
| External API mode | [test file:331-367]() | Validates EXTERNAL_API mode configuration |
| Empty user settings | [test file:399-416]() | Confirms empty arrays are preserved |
| Mix with empty settings | [test file:418-435]() | Tests additive mix on empty base |
| Gradio endpoint preservation | [test file:461-513]() | Ensures spaceTools survive mix operations |
| SEARCH_ENABLES_FETCH | [test file:516-683]() | Auto-enable doc_fetch with doc_search |

**Sources:** [packages/app/test/server/utils/tool-selection-strategy.test.ts:92-683]()

---

# Page: Gradio Integration

# Gradio Integration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [packages/app/src/server/gradio-endpoint-connector.ts](packages/app/src/server/gradio-endpoint-connector.ts)
- [packages/app/src/server/mcp-proxy.ts](packages/app/src/server/mcp-proxy.ts)
- [packages/app/src/server/utils/gradio-utils.ts](packages/app/src/server/utils/gradio-utils.ts)
- [packages/app/test/server/utils/gradio-utils.test.ts](packages/app/test/server/utils/gradio-utils.test.ts)

</details>



The Gradio Integration system enables the HuggingFace MCP Server to dynamically discover, register, and execute tools from Gradio applications hosted on HuggingFace Spaces. This allows AI clients to access thousands of AI models and tools without pre-registration, expanding the MCP server's capabilities at runtime.

**Scope**: This page covers the complete Gradio integration lifecycle from space ID parsing through tool execution and post-processing. For information about the overall tool system, see [Tool System Overview](#4.1). For details on transport-level execution, see [Transport Layer](#7).

---

## System Overview

The Gradio integration follows a **lazy connection pattern** where tool schemas are fetched eagerly but SSE connections are established only when tools are invoked. This reduces overhead and enables parallel schema discovery.

```mermaid
graph TB
    subgraph "Configuration Sources"
        HeaderParam["x-mcp-gradio Header<br/>(comma-separated space IDs)"]
        UserSettings["User Settings<br/>spaceTools array"]
    end
    
    subgraph "Discovery Phase"
        ParseSpaceIds["parseGradioSpaceIds()<br/>Validate format"]
        GetGradioSpaces["getGradioSpaces()<br/>Fetch metadata + schemas"]
        SpaceCache["spaceMetadataCache<br/>In-memory cache"]
    end
    
    subgraph "Registration Phase"
        ProxyFactory["createProxyServerFactory()<br/>Inject Gradio tools"]
        ConnectEndpoints["connectToGradioEndpoints()<br/>Parallel schema fetch"]
        ParseSchema["parseSchemaResponse()<br/>Handle array/object formats"]
        RegisterTools["registerRemoteTools()<br/>Register on MCP server"]
        ConvertSchema["convertToolSchemaToZod()<br/>JSON Schema → Zod"]
        CreateToolName["createGradioToolName()<br/>Generate gr/grp prefix"]
    end
    
    subgraph "Execution Phase"
        ToolHandler["createToolHandler()<br/>Per-tool handler"]
        CallGradioTool["callGradioTool()<br/>SSE connection"]
        PostProcess["applyResultPostProcessing()<br/>Transform results"]
    end
    
    HeaderParam --> ParseSpaceIds
    UserSettings --> ParseSpaceIds
    ParseSpaceIds --> GetGradioSpaces
    GetGradioSpaces --> SpaceCache
    SpaceCache --> ConnectEndpoints
    
    ProxyFactory --> ConnectEndpoints
    ConnectEndpoints --> ParseSchema
    ParseSchema --> RegisterTools
    RegisterTools --> ConvertSchema
    RegisterTools --> CreateToolName
    RegisterTools --> ToolHandler
    
    ToolHandler --> CallGradioTool
    CallGradioTool --> PostProcess
    
    style ProxyFactory fill:#f0f0f0
    style ConnectEndpoints fill:#f0f0f0
    style ToolHandler fill:#f0f0f0
```

**Sources**: [packages/app/src/server/mcp-proxy.ts:1-277](), [packages/app/src/server/gradio-endpoint-connector.ts:1-755](), [packages/app/src/server/utils/gradio-utils.ts:1-212]()

---

## Proxy Factory Pattern

The Gradio integration uses a **proxy factory pattern** to inject dynamic tools into the MCP server without modifying the core server creation logic. The `createProxyServerFactory` function wraps the original `ServerFactory` and adds Gradio tools after the base server is created.

```mermaid
graph LR
    subgraph "Server Creation Flow"
        Transport["Transport Layer<br/>(STDIO/SSE/HTTP)"]
        OriginalFactory["originalServerFactory()<br/>Create base server"]
        ProxyFactory["createProxyServerFactory()<br/>Wrap original factory"]
        BaseServer["McpServer<br/>Built-in tools registered"]
        EnhancedServer["McpServer<br/>+ Gradio tools"]
    end
    
    Transport --> ProxyFactory
    ProxyFactory --> OriginalFactory
    OriginalFactory --> BaseServer
    ProxyFactory --> EnhancedServer
    BaseServer -.upgraded to.- EnhancedServer
    
    style ProxyFactory fill:#f0f0f0
```

The proxy factory executes the following sequence:

1. Extract authentication token and Gradio parameter from headers
2. Fetch user settings if not provided and no bouquet specified
3. Call original server factory to create base MCP server with built-in tools
4. Skip Gradio integration if `skipGradio=true` or `gradio="none"`
5. Parse space IDs from header parameter and user settings
6. Discover Gradio spaces and fetch schemas in parallel
7. Register remote tools on the existing server instance

**Key Implementation Details**:

| Aspect | Implementation | Location |
|--------|---------------|----------|
| Factory signature | `ServerFactory = (headers, userSettings?, skipGradio?, sessionInfo?) => Promise<ServerFactoryResult>` | [packages/app/src/server/transport/base-transport.ts:30-40]() |
| Proxy creation | `createProxyServerFactory(webServer, apiClient, originalFactory)` | [packages/app/src/server/mcp-proxy.ts:83-87]() |
| Gradio skipping | Checked for `initialize` calls and bouquet overrides | [packages/app/src/server/mcp-proxy.ts:124-143]() |
| Settings merge | Combines header param and user settings, deduplicates | [packages/app/src/server/mcp-proxy.ts:150-165]() |

**Sources**: [packages/app/src/server/mcp-proxy.ts:83-276](), [packages/app/src/server/transport/base-transport.ts:30-40]()

---

## Endpoint Discovery

Gradio endpoint discovery converts space IDs (e.g., `microsoft/Florence-2-large`) into fully-qualified endpoints with schemas. The process validates space ID format, fetches metadata from the HuggingFace API, and retrieves tool schemas from each space's `/gradio_api/mcp/schema` endpoint.

### Space ID Parsing

The `parseGradioSpaceIds` function validates space IDs and returns parsed structures. It enforces the `username/space-name` format with exactly one slash:

```mermaid
graph TB
    Input["gradio parameter<br/>comma-separated string"]
    Split["Split by comma,<br/>trim whitespace"]
    CheckNone{"Is 'none'<br/>(case-insensitive)?"}
    ValidateFormat{"Exactly one '/'<br/>with content on both sides?"}
    CreateParsed["Create ParsedGradioSpace<br/>{name: string}"]
    Skip["Skip entry<br/>(log warning)"]
    Return["Return ParsedGradioSpace[]"]
    
    Input --> Split
    Split --> CheckNone
    CheckNone -->|Yes| Return
    CheckNone -->|No| ValidateFormat
    ValidateFormat -->|Yes| CreateParsed
    ValidateFormat -->|No| Skip
    CreateParsed --> Return
    Skip --> Return
    
    style ValidateFormat fill:#f0f0f0
```

**Format Validation Rules**:

| Rule | Valid Examples | Invalid Examples |
|------|---------------|------------------|
| Exactly one slash | `microsoft/Florence-2-large` | `microsoft-Florence`, `a/b/c` |
| Content on both sides | `user/space`, `org/model-v2` | `/space`, `user/`, `/` |
| Special sentinel | Returns `[]` for `none` (case-insensitive) | N/A |
| Character preservation | Preserves dots, dashes, underscores | N/A |

**Sources**: [packages/app/src/server/utils/gradio-utils.ts:107-144](), [packages/app/test/server/utils/gradio-utils.test.ts:268-449]()

### Schema Fetching

The `connectToGradioEndpoints` function fetches schemas from multiple spaces in parallel with timeout protection:

```mermaid
sequenceDiagram
    participant Proxy as createProxyServerFactory
    participant Discovery as getGradioSpaces
    participant Connector as connectToGradioEndpoints
    participant Fetch as fetchEndpointSchema
    participant API as HF Space /mcp/schema
    participant Cache as spaceMetadataCache
    
    Proxy->>Discovery: getGradioSpaces(spaceNames, token)
    Discovery->>Cache: Check cache
    Cache-->>Discovery: Cached metadata + schemas
    Discovery->>Connector: For uncached spaces
    
    par Parallel schema fetch
        Connector->>Fetch: fetchEndpointSchema(endpoint1)
        Connector->>Fetch: fetchEndpointSchema(endpoint2)
        Connector->>Fetch: fetchEndpointSchema(endpoint3)
    end
    
    Fetch->>API: GET /gradio_api/mcp/schema
    Note over Fetch,API: X-HF-Authorization: Bearer token<br/>(for private spaces)
    API-->>Fetch: JSON schema response
    Fetch->>Fetch: parseSchemaResponse()
    Fetch-->>Connector: EndpointConnection
    
    Connector-->>Discovery: EndpointConnectionResult[]
    Discovery->>Cache: Cache public space metadata
    Discovery-->>Proxy: GradioSpace[] with tools
```

**Connection Details**:

| Parameter | Value | Description |
|-----------|-------|-------------|
| Timeout | `12000ms` (12 seconds) | Per-space connection timeout |
| Max concurrent | Unlimited | All spaces fetched in parallel |
| Auth header | `X-HF-Authorization: Bearer {token}` | Only sent for private spaces |
| Schema URL | `https://{subdomain}.hf.space/gradio_api/mcp/schema` | Standard Gradio MCP endpoint |
| Retry logic | None | Failures are logged and skipped |

The `fetchEndpointSchema` function performs the following steps:

1. Check if space is private using `isSpacePrivate()` with cache
2. Build schema URL: `https://{subdomain}.hf.space/gradio_api/mcp/schema`
3. Add `X-HF-Authorization` header for private spaces
4. Fetch with `AbortController` timeout (12.5 seconds)
5. Parse response with `parseSchemaResponse()`
6. Filter out tools containing `<lambda>` in name
7. Store SSE URL for lazy connection: `https://{subdomain}.hf.space/gradio_api/mcp/sse`

**Sources**: [packages/app/src/server/gradio-endpoint-connector.ts:200-267](), [packages/app/src/server/gradio-endpoint-connector.ts:273-337]()

### Schema Response Formats

The `parseSchemaResponse` function handles two schema formats returned by Gradio spaces:

**Array Format** (preferred):
```typescript
[
  {
    name: "toolName",
    description: "Tool description",
    inputSchema: {
      type: "object",
      properties: { ... },
      required: [ ... ]
    }
  }
]
```

**Object Format** (legacy):
```typescript
{
  "toolName": {
    type: "object",
    properties: { ... },
    required: [ ... ],
    description: "Tool description"
  }
}
```

Both formats are converted to a normalized structure: `Array<{ name: string; description?: string; inputSchema: JsonSchema }>`.

**Sources**: [packages/app/src/server/gradio-endpoint-connector.ts:84-137]()

---

## Tool Naming Conventions

Gradio tools use a standardized naming convention to ensure uniqueness and identify their source. The naming system distinguishes between public and private spaces and enforces a 49-character limit.

### Naming Pattern

```mermaid
graph LR
    subgraph "Tool Name Components"
        Prefix["Prefix<br/>gr or grp"]
        Index["Index<br/>1-based position"]
        Underscore1["_"]
        ToolName["Sanitized tool name"]
    end
    
    subgraph "Prefix Selection"
        IsPrivate{"Is private<br/>space?"}
        PublicPrefix["gr (public)"]
        PrivatePrefix["grp (private)"]
    end
    
    subgraph "Name Sanitization"
        Original["Original name"]
        ReplaceChars["Replace [-\\s.] with _"]
        Lowercase["Convert to lowercase"]
        CheckLength{"Length > limit?"}
        Truncate["Middle truncation<br/>Keep first 20 + last N"]
        KeepAsIs["Keep as-is"]
    end
    
    IsPrivate -->|Yes| PrivatePrefix
    IsPrivate -->|No| PublicPrefix
    
    Original --> ReplaceChars
    ReplaceChars --> Lowercase
    Lowercase --> CheckLength
    CheckLength -->|Yes| Truncate
    CheckLength -->|No| KeepAsIs
    
    PublicPrefix --> Prefix
    PrivatePrefix --> Prefix
    Prefix --> Index
    Index --> Underscore1
    Underscore1 --> ToolName
    
    style IsPrivate fill:#f0f0f0
    style CheckLength fill:#f0f0f0
```

**Function**: `createGradioToolName(toolName, index, isPrivate, toolIndex?)`

**Parameters**:

| Parameter | Type | Description |
|-----------|------|-------------|
| `toolName` | `string` | Original tool name from schema |
| `index` | `number` | Zero-based space index (converted to 1-based) |
| `isPrivate` | `boolean \| undefined` | Whether space is private |
| `toolIndex` | `number` (optional) | Tool index within space for collision resolution |

**Naming Rules**:

1. **Prefix Selection**: `gr` for public spaces, `grp` for private spaces
2. **Index**: Zero-based index + 1 (first space = 1, second space = 2, etc.)
3. **Sanitization**: Replace `-`, `.`, and spaces with `_`, then lowercase
4. **Length Limit**: Maximum 49 characters total
5. **Truncation**: If over limit, keep first 20 chars + `_` + last N chars to fill
6. **Collision Resolution**: If `toolIndex` provided and truncating, prepend `{toolIndex}_` to name

**Examples**:

| Input | Index | Private | Tool Index | Output | Notes |
|-------|-------|---------|------------|--------|-------|
| `flux1_schnell` | 0 | false | - | `gr1_flux1_schnell` | Basic public tool |
| `EasyGhibli` | 1 | false | - | `gr2_easyghibli` | Lowercase conversion |
| `private-model` | 2 | true | - | `grp3_private_model` | Private prefix |
| `very_long_tool_name_that_exceeds_forty_nine_characters_total` | 0 | false | - | `gr1_very_long_tool_name__haracters_total_and_more` | Middle truncation |
| `image_utilities_mcp_update_text_image________` | 29 | false | 0 | `gr30_0_image_utilities_mcp__te_text_image________` | With tool index |

**Sources**: [packages/app/src/server/utils/gradio-utils.ts:45-86](), [packages/app/test/server/utils/gradio-utils.test.ts:113-266]()

---

## Schema Conversion

The schema conversion system transforms JSON Schema definitions from Gradio spaces into Zod schemas compatible with the MCP protocol. This enables type validation and documentation for dynamically-discovered tools.

### Conversion Flow

```mermaid
graph TB
    subgraph "Input: Tool from parseSchemaResponse"
        ToolObj["Tool object<br/>{name, description, inputSchema}"]
        InputSchema["inputSchema<br/>JSON Schema object"]
        Properties["properties: Record<string, JsonSchemaProperty>"]
        Required["required: string[]"]
    end
    
    subgraph "Conversion Process"
        ConvertFunc["convertToolSchemaToZod(tool)"]
        IterateProps["For each property"]
        ConvertProp["convertJsonSchemaToZod(prop, isRequired)"]
        MakeOptional{"Is required?"}
        ZodProp["Zod schema for property"]
        ZodOptional["zodSchema.optional()"]
    end
    
    subgraph "Property Type Handling"
        CheckType["Check JSON Schema type"]
        FileData["FileData special case"]
        EnumType["Enum handling"]
        BasicType["string/number/boolean/array/object"]
    end
    
    subgraph "Output"
        SchemaShape["Record<string, ZodTypeAny>"]
    end
    
    ToolObj --> InputSchema
    InputSchema --> Properties
    InputSchema --> Required
    Properties --> ConvertFunc
    Required --> ConvertFunc
    
    ConvertFunc --> IterateProps
    IterateProps --> ConvertProp
    ConvertProp --> CheckType
    CheckType --> FileData
    CheckType --> EnumType
    CheckType --> BasicType
    FileData --> ZodProp
    EnumType --> ZodProp
    BasicType --> ZodProp
    
    ZodProp --> MakeOptional
    MakeOptional -->|No| ZodOptional
    MakeOptional -->|Yes| SchemaShape
    ZodOptional --> SchemaShape
    
    style ConvertFunc fill:#f0f0f0
    style ConvertProp fill:#f0f0f0
```

### Type Mapping Table

The `convertJsonSchemaToZod` function maps JSON Schema types to Zod types with special handling for common patterns:

| JSON Schema Type | Conditions | Zod Schema | Notes |
|-----------------|------------|------------|-------|
| FileData object | `title === 'FileData'` or special format | `z.object({path, url?, size?, ...})` | Gradio file upload schema |
| Enum | `enum: [...]` with all strings | `z.enum([...])` | String enum |
| Enum | `enum: [...]` with mixed types | `z.union([z.literal(...), ...])` | Union of literals |
| `string` | - | `z.string()` | Basic string |
| `number` | - | `z.number()` | Basic number |
| `boolean` | - | `z.boolean()` | Basic boolean |
| `array` | - | `z.array(z.any())` | Simplified array |
| `object` | - | `z.object({})` | Simplified object |
| Unknown | - | `z.any()` | Fallback |

**FileData Detection**: A property is considered FileData if:
- `jsonSchemaProperty.title === 'FileData'`, OR
- `jsonSchemaProperty.format === 'a http or https url to a file'` AND `default` is an object

**Default Value Handling**:

1. Required fields: Defaults are **skipped** (`skipDefault=true`) to force users to provide values
2. Optional fields: Defaults are **applied** via `zodSchema.default(value)`
3. String fields with object defaults: Extract `url` property unless FileData type
4. FileData fields: Keep full object as default

**Description Enhancement**:

File input fields get enhanced descriptions:
```typescript
description = description 
  ? `${description} (File input: provide URL or file path)` 
  : 'a http or https url to a file'
```

**Sources**: [packages/app/src/server/gradio-endpoint-connector.ts:615-754]()

---

## Tool Registration

The `registerRemoteTools` function registers Gradio tools on an existing MCP server instance. Each tool from each space gets registered with a unique name, converted schema, and execution handler.

### Registration Process

```mermaid
graph TB
    subgraph "Input: EndpointConnection"
        Connection["EndpointConnection"]
        Tools["tools: Tool[]"]
        Metadata["name, emoji, sseUrl, isPrivate"]
        OriginalIndex["originalIndex: number"]
    end
    
    subgraph "Per-Tool Registration"
        ForEach["For each tool"]
        CreateName["createGradioToolName()<br/>Generate unique name"]
        CreateDisplay["createToolDisplayInfo()<br/>Title + description"]
        ConvertSchema["convertToolSchemaToZod()<br/>JSON Schema → Zod"]
        CreateHandler["createToolHandler()<br/>Execution function"]
    end
    
    subgraph "Server Registration"
        ServerTool["server.tool(<br/>name,<br/>description,<br/>schemaShape,<br/>annotations,<br/>handler)"]
        Annotations["openWorldHint: true<br/>title: display title"]
        OpenAIMeta["_meta for openai-mcp<br/>outputTemplate, etc."]
    end
    
    Connection --> Tools
    Connection --> Metadata
    Connection --> OriginalIndex
    
    Tools --> ForEach
    Metadata --> CreateName
    OriginalIndex --> CreateName
    ForEach --> CreateName
    ForEach --> CreateDisplay
    ForEach --> ConvertSchema
    ForEach --> CreateHandler
    
    CreateName --> ServerTool
    CreateDisplay --> ServerTool
    ConvertSchema --> ServerTool
    CreateHandler --> ServerTool
    ServerTool --> Annotations
    Annotations --> OpenAIMeta
    
    style ServerTool fill:#f0f0f0
```

### Display Information

The `createToolDisplayInfo` function generates human-readable titles and descriptions:

**Title Format**: `{Space Name} - {Tool Name} {Emoji}`
- Example: `microsoft/Florence-2-large - image_caption 🔧`

**Description Format**: `{Tool Description} (from {Space Name})`
- Example: `Generate image captions (from microsoft/Florence-2-large)`
- Fallback if no description: `{Tool Name} tool from {Space Name}`

### Registration Annotations

Registered tools include these MCP annotations:

| Annotation | Value | Purpose |
|------------|-------|---------|
| `openWorldHint` | `true` | Indicates tool can be used with unknown future inputs |
| `title` | Display title string | Human-readable tool identification |

**OpenAI MCP Client Metadata** (`sessionInfo?.clientInfo?.name === 'openai-mcp'`):

```typescript
tool._meta = {
  'openai/outputTemplate': gradioWidgetUri,
  'openai/toolInvocation/invoking': `Calling the Hugging Face Space ${spaceName}`,
  'openai/toolInvocation/invoked': `Your content is being generated`
}
```

This enables custom UI rendering for OpenAI clients when displaying Gradio tool results.

**Sources**: [packages/app/src/server/gradio-endpoint-connector.ts:544-613](), [packages/app/src/server/gradio-endpoint-connector.ts:342-349]()

---

## Tool Execution

Tool execution establishes an SSE connection to the Gradio space, invokes the remote tool, and relays progress notifications back to the MCP client. The `createToolHandler` function creates an async handler for each registered tool.

### Execution Flow

```mermaid
sequenceDiagram
    participant Client as MCP Client
    participant Handler as createToolHandler
    participant Caller as callGradioTool
    participant SSE as SSE Connection
    participant Space as Gradio Space
    participant PostProc as applyResultPostProcessing
    
    Client->>Handler: tools/call with params
    Handler->>Handler: Validate sseUrl exists
    Handler->>Caller: callGradioTool(sseUrl, toolName, params)
    
    Caller->>SSE: Connect to SSE endpoint
    Note over Caller,SSE: X-HF-Authorization for private spaces
    SSE-->>Space: POST tools/call
    
    loop Progress Updates
        Space-->>SSE: Progress notification
        SSE-->>Caller: Relay notification
        Caller->>Client: Forward as MCP notification
    end
    
    Space-->>SSE: Final result
    SSE-->>Caller: Tool result
    Caller-->>Handler: ToolResult
    
    Handler->>Handler: Check for _mcpui suffix
    alt _mcpui audio tool
        Handler->>Handler: Fetch audio URL
        Handler->>Handler: Create audio player UI resource
    end
    
    Handler->>PostProc: Apply post-processing
    PostProc->>PostProc: Strip images (if enabled)
    PostProc->>PostProc: OpenAI transformation (if openai-mcp)
    PostProc-->>Handler: Processed result
    
    Handler->>Handler: Record metrics
    Handler->>Handler: Log Gradio event
    Handler-->>Client: Final MCP result
```

### Handler Components

The `createToolHandler` function captures the following in its closure:

| Captured Variable | Type | Source | Purpose |
|------------------|------|--------|---------|
| `connection` | `EndpointConnection` | Registration | Space metadata and SSE URL |
| `tool` | `Tool` | Registration | Tool name and schema |
| `outwardFacingName` | `string` | Registration | Generated `gr1_*` name |
| `hfToken` | `string \| undefined` | Headers | HF authentication |
| `sessionInfo` | `object` | Transport | Client details for logging |
| `options` | `RegisterRemoteToolsOptions` | Registration | Post-processing config |

**SSE Connection Details**:

- URL: `connection.sseUrl` (e.g., `https://{subdomain}.hf.space/gradio_api/mcp/sse`)
- Authentication: `X-HF-Authorization: Bearer {token}` for private spaces
- Protocol: Established by `@modelcontextprotocol/sdk/client/sse.js`
- Call method: `tools/call` with tool name and parameters

**Error Handling**:

1. Missing SSE URL → Throw error immediately
2. Remote tool errors → Extract error message from MCP content
3. Connection failures → Log and throw with meaningful message
4. All errors → Record in `gradioMetrics.recordFailure()`

**Metrics Tracking**:

```typescript
// Captured for each invocation:
- startTime: Date.now()
- success: !result.isError
- error: Extracted error message
- responseSizeBytes: JSON.stringify(result).length
- notificationCount: Progress updates relayed
- durationMs: endTime - startTime
```

Metrics are logged via `logGradioEvent()` in the `finally` block, ensuring all invocations are tracked regardless of success or failure.

**Sources**: [packages/app/src/server/gradio-endpoint-connector.ts:354-539]()

### MCP UI Audio Transform

Tools with names containing `_mcpui` receive special handling when they return a single text URL:

1. Check if result is single text item matching `https?://` pattern
2. Attempt to fetch audio from URL
3. Base64-encode audio if fetch succeeds
4. Create audio player UI resource with `createAudioPlayerUIResource()`
5. Append UI resource to result content array
6. Apply standard post-processing to decorated result

**Generated UI URI**: `ui://huggingface-mcp/{sanitizedSpaceName}/{timestamp}`

This enables rich audio playback in MCP clients that support UI resources.

**Sources**: [packages/app/src/server/gradio-endpoint-connector.ts:447-496]()

---

## Post-Processing

Result post-processing transforms raw Gradio outputs into client-appropriate formats. The `applyResultPostProcessing` function applies two optional transformations based on configuration.

### Processing Pipeline

```mermaid
graph TB
    RawResult["Raw ToolResult<br/>from Gradio space"]
    CheckError{"result.isError?"}
    ReturnError["Return unchanged<br/>(errors not processed)"]
    
    subgraph "Image Filtering"
        CheckStripImages{"stripImageContent<br/>enabled?"}
        FilterImages["Filter out image content<br/>Keep text/resource only"]
        KeepImages["Keep all content"]
    end
    
    subgraph "OpenAI Transformation"
        CheckOpenAI{"Client is<br/>openai-mcp?"}
        TransformOpenAI["Transform to structured output<br/>Add widget resource"]
        KeepStandard["Keep MCP format"]
    end
    
    FinalResult["Processed ToolResult"]
    
    RawResult --> CheckError
    CheckError -->|Yes| ReturnError
    CheckError -->|No| CheckStripImages
    
    CheckStripImages -->|Yes| FilterImages
    CheckStripImages -->|No| KeepImages
    FilterImages --> CheckOpenAI
    KeepImages --> CheckOpenAI
    
    CheckOpenAI -->|Yes| TransformOpenAI
    CheckOpenAI -->|No| KeepStandard
    TransformOpenAI --> FinalResult
    KeepStandard --> FinalResult
    
    style CheckStripImages fill:#f0f0f0
    style CheckOpenAI fill:#f0f0f0
```

### Image Content Filtering

When `stripImageContent` is enabled (via `x-mcp-no-image-content` header or `GRADIO_IMAGE_FILTER_FLAG` in settings), image content items are removed from results.

**Filtering Logic**:

```typescript
// Keep only if:
content.filter(item => {
  if (typeof item !== 'object' || !item) return true;
  if (item.type === 'image') return false;  // Filter images
  if (item.type === 'text') return true;     // Keep text
  if (item.type === 'resource') return true; // Keep resources
  return true; // Keep unknown types
})
```

**Use Cases**:
- Clients with limited image support
- Reducing response size for bandwidth-constrained connections
- Text-only processing workflows
- Cost optimization for token-based billing

### OpenAI Structured Output

When `sessionInfo.clientInfo.name === 'openai-mcp'`, results are transformed into OpenAI's structured output format with embedded widget resources.

**Transformation Structure**:

```typescript
{
  content: [
    {
      type: "text",
      text: JSON.stringify({
        result: <original result content>,
        widget: <widget resource URI>
      }, null, 2)
    }
  ]
}
```

**Widget Resource**: References the Gradio widget HTML resource registered on the MCP server. URI format: `ui://huggingface-mcp/gradio-widget/{version}`

**Purpose**: Enables OpenAI clients to:
1. Parse structured JSON output
2. Render custom UI via widget HTML
3. Display Gradio results with interactive elements

**Fallback**: If `gradioWidgetUri` is not provided in options, transformation is skipped.

**Sources**: [packages/app/src/server/utils/gradio-tool-caller.ts:1-150]() (referenced), [packages/app/src/server/gradio-endpoint-connector.ts:435-443]()

---

## Configuration and Caching

### Header Parameters

Gradio integration respects multiple HTTP headers for configuration:

| Header | Format | Purpose | Example |
|--------|--------|---------|---------|
| `x-mcp-gradio` | Comma-separated space IDs | Specify Gradio spaces to load | `microsoft/Florence-2-large,user/model` |
| `x-mcp-no-image-content` | `"true"` or `"false"` | Enable image filtering | `true` |
| `Authorization` | `Bearer {token}` | HF authentication (standard) | `Bearer hf_...` |

**Special Values**:
- `x-mcp-gradio: none` → Explicitly disable Gradio integration
- Empty/missing `x-mcp-gradio` → Use user settings only

### User Settings Integration

User settings provide persistent Gradio space configuration via `AppSettings.spaceTools`:

```typescript
interface SpaceTool {
  _id: string;        // Unique identifier
  name: string;       // Space ID (e.g., 'microsoft/Florence-2-large')
  subdomain: string;  // Subdomain for API access
  emoji?: string;     // Display emoji
}
```

**Settings Priority**:
1. Header `x-mcp-gradio` parameter
2. User settings `spaceTools` array
3. Both are merged and deduplicated

**Emoji Override**: If a space appears in both header and settings, the emoji from settings is used.

### Metadata Caching

The `spaceMetadataCache` stores space metadata to reduce API calls:

**Cache Configuration** (`CACHE_CONFIG`):

| Setting | Value | Purpose |
|---------|-------|---------|
| `METADATA_TTL` | 5 minutes | How long cached entries are valid |
| `SCHEMA_TTL` | 5 minutes | How long schemas are cached |
| `SPACE_INFO_TIMEOUT` | 10 seconds | Timeout for `spaceInfo()` API calls |

**Cache Structure**:

```typescript
interface CachedSpaceMetadata {
  _id: string;
  name: string;
  subdomain: string;
  emoji: string;
  private: boolean;
  sdk: string;
  fetchedAt: number;  // Timestamp for TTL calculation
}
```

**Cache Behavior**:

- **Public spaces**: Cached for full TTL
- **Private spaces**: **Never cached** (always fresh to respect auth changes)
- **Cache miss**: Falls back to `spaceInfo()` API call with timeout
- **API timeout**: Assumed private for safety

**Cache Benefits**:

1. Reduces latency for repeated space access
2. Minimizes HF API rate limit impact
3. Improves parallel discovery performance
4. Decreases server load

**Sources**: [packages/app/src/server/utils/gradio-cache.ts:1-50]() (referenced), [packages/app/src/server/gradio-endpoint-connector.ts:142-196]()

---

## Integration with Other Systems

### Tool Selection Strategy

Gradio tools interact with the tool selection system (see [Tool Selection Strategy](#5.2)):

- **Bouquet precedence**: When `bouquet` is specified (except `"all"`), Gradio tools from settings are skipped unless explicit `gradio` parameter is provided
- **Mix mode**: Gradio tools are additive and not affected by built-in tool filtering
- **Settings mode**: Gradio spaces from `spaceTools` are loaded automatically

### Dynamic Space Tool

The `use_space` tool (see [Space Management Tools](#4.2.3)) provides an alternative way to invoke Gradio spaces without pre-registration. This complements the pre-registered Gradio tools by allowing ad-hoc space invocation.

### Metrics and Logging

Gradio operations are tracked through multiple systems:

1. **Gradio Metrics** (`gradioMetrics`): Success/failure rates per tool
2. **Query Logger** (`logGradioEvent`): Detailed invocation logs with session info
3. **Transport Metrics**: Connection-level statistics

**Sources**: [packages/app/src/server/utils/gradio-metrics.ts:1-100]() (referenced), [packages/app/src/server/utils/query-logger.ts:1-150]() (referenced)

---

# Page: Gradio Overview

# Gradio Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [packages/app/src/server/gradio-endpoint-connector.ts](packages/app/src/server/gradio-endpoint-connector.ts)
- [packages/app/src/server/mcp-proxy.ts](packages/app/src/server/mcp-proxy.ts)

</details>



This document introduces the Gradio integration system, which enables dynamic discovery and registration of Gradio applications as MCP tools. It explains the proxy factory pattern used to inject Gradio tools into the server, the lazy connection model, and how Gradio spaces are configured and registered.

For details on the endpoint discovery process, see [Endpoint Discovery](#6.2). For schema conversion specifics, see [Schema Conversion](#6.3). For tool execution mechanics, see [Tool Execution and Post-Processing](#6.4).

## What Gradio Integration Enables

The Gradio integration system allows any Gradio application hosted on Hugging Face Spaces to be dynamically discovered and exposed as an MCP tool. This enables:

- **Dynamic tool expansion**: Tools are not hardcoded but discovered at runtime from Space metadata
- **Zero-configuration tool creation**: Any Gradio Space that exposes an MCP schema endpoint becomes available as a tool
- **Private space support**: Authenticated users can access tools from their private Spaces
- **Unified interface**: Gradio applications appear as regular MCP tools alongside built-in tools

The key differentiator is that Gradio tools are not statically defined in the codebase but are registered dynamically based on Space configuration and schema endpoints.

**Sources:** [packages/app/src/server/gradio-endpoint-connector.ts:1-755](), [packages/app/src/server/mcp-proxy.ts:1-277]()

## Architecture: The Proxy Factory Pattern

The Gradio integration uses a **proxy factory pattern** to intercept server creation and augment it with dynamically discovered tools.

### Proxy Factory Flow

```mermaid
sequenceDiagram
    participant Transport as "Transport Layer"
    participant ProxyFactory as "createProxyServerFactory"
    participant OriginalFactory as "originalServerFactory"
    participant Discovery as "getGradioSpaces"
    participant Connector as "gradio-endpoint-connector"
    participant Server as "McpServer"

    Transport->>ProxyFactory: "createServer(headers, settings)"
    
    Note over ProxyFactory: "Extract gradio param<br/>and space names"
    
    ProxyFactory->>OriginalFactory: "Create base server"
    OriginalFactory-->>ProxyFactory: "ServerFactoryResult"
    
    alt skipGradio or no spaces configured
        ProxyFactory-->>Transport: "Return base server"
    else Gradio enabled
        ProxyFactory->>Discovery: "getGradioSpaces(spaceNames, token)"
        Discovery-->>ProxyFactory: "GradioEndpoint[]"
        
        loop For each space
            ProxyFactory->>Connector: "registerRemoteTools(server, connection)"
            Connector->>Server: "server.tool(name, description, schema, handler)"
        end
        
        ProxyFactory-->>Transport: "Return augmented server"
    end
```

The `createProxyServerFactory` function wraps the original `ServerFactory` and adds Gradio tool registration after the base server is created. This separation allows the core MCP server logic to remain unchanged while adding dynamic tool discovery as a layer.

**Sources:** [packages/app/src/server/mcp-proxy.ts:83-276]()

### Key Components

| Component | Location | Purpose |
|-----------|----------|---------|
| `createProxyServerFactory` | [mcp-proxy.ts:83-276]() | Wraps original factory, orchestrates Gradio discovery |
| `connectToGradioEndpoints` | [gradio-endpoint-connector.ts:273-337]() | Fetches schemas from multiple endpoints in parallel |
| `registerRemoteTools` | [gradio-endpoint-connector.ts:544-613]() | Registers discovered tools on MCP server |
| `parseSchemaResponse` | [gradio-endpoint-connector.ts:84-137]() | Parses schema formats (array or object) |
| `createToolHandler` | [gradio-endpoint-connector.ts:354-539]() | Creates tool execution handler with SSE connection |

**Sources:** [packages/app/src/server/mcp-proxy.ts:83-276](), [packages/app/src/server/gradio-endpoint-connector.ts:1-755]()

## Endpoint Connection Model

The Gradio integration uses a **lazy connection model** that separates schema discovery from tool execution.

### EndpointConnection Interface

```typescript
interface EndpointConnection {
    endpointId: string;           // Unique identifier for logging
    originalIndex: number;         // Position in original space list
    client: Client | null;         // Always null in lazy model
    tools: Tool[];                 // Discovered tool schemas
    name?: string;                 // Space name (e.g., "user/space-name")
    emoji?: string;                // Display emoji from settings
    sseUrl?: string;               // SSE endpoint for lazy connection
    isPrivate?: boolean;           // Private space flag
}
```

This interface is defined at [gradio-endpoint-connector.ts:40-49]() and represents a connection to a Gradio space.

### Lazy Connection Pattern

```mermaid
graph TB
    subgraph "Schema Discovery Phase"
        FetchSchema["fetchEndpointSchema()<br/>/gradio_api/mcp/schema"]
        ParseSchema["parseSchemaResponse()"]
        CreateConnection["Build EndpointConnection<br/>client: null<br/>sseUrl: stored"]
    end
    
    subgraph "Registration Phase"
        RegisterTools["registerRemoteTools()"]
        CreateHandler["createToolHandler()<br/>Closure with sseUrl"]
        ServerTool["server.tool()<br/>Tool registered"]
    end
    
    subgraph "Execution Phase - Later"
        ToolCall["Client calls tool"]
        HandlerInvoked["Handler invoked"]
        LazyConnect["callGradioTool()<br/>Establishes SSE connection<br/>to stored sseUrl"]
        ExecuteCall["Execute MCP call"]
    end
    
    FetchSchema --> ParseSchema
    ParseSchema --> CreateConnection
    CreateConnection --> RegisterTools
    RegisterTools --> CreateHandler
    CreateHandler --> ServerTool
    
    ToolCall --> HandlerInvoked
    HandlerInvoked --> LazyConnect
    LazyConnect --> ExecuteCall
    
    style CreateConnection fill:#f9f9f9
    style LazyConnect fill:#f9f9f9
```

The key insight is that the `EndpointConnection` stores the `sseUrl` but doesn't establish the SSE connection until a tool is actually invoked. This reduces startup time and avoids keeping connections open for unused tools.

**Sources:** [packages/app/src/server/gradio-endpoint-connector.ts:40-49](), [packages/app/src/server/gradio-endpoint-connector.ts:201-267](), [packages/app/src/server/gradio-endpoint-connector.ts:354-539]()

## Schema Discovery and Parsing

### Schema Endpoint Format

Gradio spaces expose their available tools via the `/gradio_api/mcp/schema` endpoint. This endpoint returns either an **array format** or **object format**:

**Array Format** (newer):
```json
[
  {
    "name": "generate_image",
    "description": "Generates an image from a prompt",
    "inputSchema": {
      "type": "object",
      "properties": { "prompt": { "type": "string" } },
      "required": ["prompt"]
    }
  }
]
```

**Object Format** (legacy):
```json
{
  "generate_image": {
    "type": "object",
    "properties": { "prompt": { "type": "string" } },
    "required": ["prompt"],
    "description": "Generates an image from a prompt"
  }
}
```

The `parseSchemaResponse` function at [gradio-endpoint-connector.ts:84-137]() handles both formats transparently.

### Parallel Schema Fetching

```mermaid
graph LR
    subgraph "Input"
        SpaceNames["Space names<br/>[sp1, sp2, sp3]"]
    end
    
    subgraph "Parallel Fetch - connectToGradioEndpoints"
        Task1["Promise.race<br/>fetchEndpointSchema(sp1)<br/>vs createTimeout(12s)"]
        Task2["Promise.race<br/>fetchEndpointSchema(sp2)<br/>vs createTimeout(12s)"]
        Task3["Promise.race<br/>fetchEndpointSchema(sp3)<br/>vs createTimeout(12s)"]
    end
    
    subgraph "Results"
        Success["EndpointConnectionResult[]<br/>success: true/false"]
    end
    
    SpaceNames --> Task1
    SpaceNames --> Task2
    SpaceNames --> Task3
    
    Task1 --> Success
    Task2 --> Success
    Task3 --> Success
    
    style Task1 fill:#f9f9f9
    style Task2 fill:#f9f9f9
    style Task3 fill:#f9f9f9
```

The `connectToGradioEndpoints` function at [gradio-endpoint-connector.ts:273-337]() fetches schemas from multiple spaces in parallel using `Promise.all()`. Each fetch is wrapped in a `Promise.race()` with a 12-second timeout (defined by `CONNECTION_TIMEOUT_MS` at [gradio-endpoint-connector.ts:68]()).

Failed fetches are logged but don't block other spaces from being registered.

**Sources:** [packages/app/src/server/gradio-endpoint-connector.ts:84-137](), [packages/app/src/server/gradio-endpoint-connector.ts:273-337](), [packages/app/src/server/gradio-endpoint-connector.ts:201-267]()

## Private Space Support

The system detects and handles private Gradio spaces by checking the space's privacy status and forwarding authentication.

### Privacy Detection Flow

```mermaid
flowchart TD
    Start["fetchEndpointSchema()"]
    CheckCache{"spaceMetadataCache.get()"}
    CacheHit["Use cached private flag"]
    CacheMiss["Call spaceInfo() API"]
    CheckPrivate{"space.private?"}
    CachePublic["Cache metadata<br/>fetchedAt: timestamp"]
    SkipCache["Don't cache<br/>(auth-sensitive)"]
    AddHeader["Add X-HF-Authorization header"]
    FetchSchema["Fetch schema with headers"]
    
    Start --> CheckCache
    CheckCache -->|Hit| CacheHit
    CheckCache -->|Miss| CacheMiss
    CacheMiss --> CheckPrivate
    CheckPrivate -->|Public| CachePublic
    CheckPrivate -->|Private| SkipCache
    CacheHit --> CheckPrivate
    CachePublic --> CheckPrivate
    SkipCache --> CheckPrivate
    CheckPrivate -->|If private & token| AddHeader
    CheckPrivate -->|If public| FetchSchema
    AddHeader --> FetchSchema
```

The `isSpacePrivate` function at [gradio-endpoint-connector.ts:142-196]() implements this logic with intelligent caching:
- **Public spaces** are cached indefinitely (metadata won't change)
- **Private spaces** are never cached (auth-sensitive, always fetched fresh)
- Cache misses trigger a `spaceInfo()` API call with timeout

When a space is private and an HF token is available, the `X-HF-Authorization` header is added at [gradio-endpoint-connector.ts:219]() for both schema fetching and tool execution.

**Sources:** [packages/app/src/server/gradio-endpoint-connector.ts:142-196](), [packages/app/src/server/gradio-endpoint-connector.ts:201-267](), [packages/app/src/server/gradio-endpoint-connector.ts:214-221]()

## Tool Registration Flow

Once schemas are fetched, the `registerRemoteTools` function registers each discovered tool on the MCP server.

### Registration Process

```mermaid
sequenceDiagram
    participant Proxy as "createProxyServerFactory"
    participant Register as "registerRemoteTools"
    participant Naming as "createGradioToolName"
    participant Convert as "convertToolSchemaToZod"
    participant Handler as "createToolHandler"
    participant Server as "McpServer"

    Proxy->>Register: "registerRemoteTools(server, connection, token)"
    
    loop For each tool in connection.tools
        Register->>Naming: "createGradioToolName(name, index, isPrivate)"
        Naming-->>Register: "outwardFacingName"
        
        Register->>Register: "createToolDisplayInfo()<br/>title, description"
        
        Register->>Convert: "convertToolSchemaToZod(tool)"
        Convert-->>Register: "Zod schema shape"
        
        Register->>Handler: "createToolHandler(connection, tool)"
        Handler-->>Register: "Handler function"
        
        Register->>Server: "server.tool(name, desc, schema, handler)"
        
        Note over Register,Server: "Special handling for openai-mcp<br/>client: add _meta fields"
    end
```

The process involves:

1. **Tool Naming**: [gradio-endpoint-connector.ts:557-562]() - Uses `createGradioToolName` to generate unique names
2. **Display Info**: [gradio-endpoint-connector.ts:342-349]() - Creates human-readable title and description
3. **Schema Conversion**: [gradio-endpoint-connector.ts:615-639]() - Converts JSON Schema to Zod validation
4. **Handler Creation**: [gradio-endpoint-connector.ts:354-539]() - Creates closure with SSE URL and connection info
5. **Server Registration**: [gradio-endpoint-connector.ts:594-603]() - Registers tool with MCP server

**Sources:** [packages/app/src/server/gradio-endpoint-connector.ts:544-613]()

## Configuration Sources

Gradio tools can be configured through multiple sources, with specific precedence rules.

### Configuration Hierarchy

| Priority | Source | Format | Example |
|----------|--------|--------|---------|
| 1 | `x-mcp-gradio` header | Comma-separated space IDs | `user/space1,org/space2` |
| 2 | User settings | `spaceTools` array | `[{name: "user/space", emoji: "🎨"}]` |
| 3 | Fallback | Empty list | No Gradio tools |

The configuration logic at [mcp-proxy.ts:150-154]() merges both sources and deduplicates:

```typescript
const gradioSpaceNames = gradio ? parseGradioSpaceIds(gradio).map(s => s.name) : [];
const settingsSpaceNames = settings?.spaceTools?.map(s => s.name) || [];
const allSpaceNames = [...new Set([...gradioSpaceNames, ...settingsSpaceNames])];
```

### Conditional Skipping

Gradio discovery can be skipped under several conditions:

```mermaid
flowchart TD
    Start["createProxyServerFactory called"]
    CheckSkip{"skipGradio flag?"}
    CheckNone{"gradio='none'?"}
    CheckBouquet{"bouquet set &<br/>bouquet != 'all' &<br/>!gradio param?"}
    CheckSpaces{"Any spaces configured?"}
    Discover["Discover Gradio spaces<br/>getGradioSpaces()"]
    Return["Return server<br/>without Gradio tools"]
    
    Start --> CheckSkip
    CheckSkip -->|Yes| Return
    CheckSkip -->|No| CheckNone
    CheckNone -->|Yes| Return
    CheckNone -->|No| CheckBouquet
    CheckBouquet -->|Yes| Return
    CheckBouquet -->|No| CheckSpaces
    CheckSpaces -->|No| Return
    CheckSpaces -->|Yes| Discover
```

Key skip conditions:
- **`skipGradio=true`**: At [mcp-proxy.ts:124-127](), used for initialization and non-Gradio tool calls
- **`gradio="none"`**: At [mcp-proxy.ts:133-136](), explicitly disables Gradio
- **Bouquet without gradio param**: At [mcp-proxy.ts:140-143](), when a bouquet is specified (not "all") and no explicit gradio parameter is given

This optimization reduces latency for requests that don't need Gradio tools.

**Sources:** [packages/app/src/server/mcp-proxy.ts:98-143](), [packages/app/src/server/mcp-proxy.ts:150-165]()

## Integration with Built-in Tools

Gradio tools are registered alongside built-in tools and appear in the same tool list. The proxy factory ensures both sets of tools coexist:

```mermaid
graph TB
    subgraph "originalServerFactory"
        BuiltIn["Register built-in tools<br/>model_search, dataset_detail, etc."]
    end
    
    subgraph "createProxyServerFactory"
        Original["Call originalServerFactory"]
        Discover["Discover Gradio spaces"]
        Register["registerRemoteTools"]
        Augmented["Augmented server<br/>Built-in + Gradio tools"]
    end
    
    BuiltIn --> Original
    Original --> Discover
    Discover --> Register
    Register --> Augmented
    
    style Original fill:#f9f9f9
    style Augmented fill:#f9f9f9
```

The proxy pattern ensures:
- Built-in tools are always available (registered first)
- Gradio tools are added without modifying base server logic
- Tool selection strategy applies to built-in tools; Gradio tools are additive
- Both tool types use the same `McpServer.tool()` registration API

**Sources:** [packages/app/src/server/mcp-proxy.ts:83-276]()

## Post-Processing Options

The registration phase configures post-processing options that will be applied during tool execution:

| Option | Source | Purpose |
|--------|--------|---------|
| `stripImageContent` | `x-mcp-no-image-content` header or settings flag | Removes image content from results (see [Tool Execution](#6.4)) |
| `gradioWidgetUri` | OpenAI MCP client detection | Adds UI resource for embedded widgets |
| `sessionInfo` | Transport layer | Client identification and auth status |

These options are passed to `registerRemoteTools` at [mcp-proxy.ts:204-207]() and captured in the tool handler closure at [gradio-endpoint-connector.ts:364-444]().

**Sources:** [packages/app/src/server/mcp-proxy.ts:100-131](), [packages/app/src/server/mcp-proxy.ts:204-207](), [packages/app/src/server/gradio-endpoint-connector.ts:354-539]()

---

# Page: Endpoint Discovery

# Endpoint Discovery

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [packages/app/src/server/gradio-endpoint-connector.ts](packages/app/src/server/gradio-endpoint-connector.ts)
- [packages/app/src/server/mcp-proxy.ts](packages/app/src/server/mcp-proxy.ts)
- [packages/app/src/server/utils/gradio-utils.ts](packages/app/src/server/utils/gradio-utils.ts)
- [packages/app/test/server/utils/gradio-utils.test.ts](packages/app/test/server/utils/gradio-utils.test.ts)

</details>



## Purpose and Scope

This document describes how the HF MCP Server discovers and prepares Gradio spaces for use as dynamic tools. Endpoint discovery is the first phase of Gradio integration, responsible for identifying which Gradio spaces should be available, fetching their metadata and subdomains from the HuggingFace API, and retrieving their tool schemas. 

For information about converting these schemas into MCP tools, see [Schema Conversion](#6.3). For details on executing tools once discovered, see [Tool Execution and Post-Processing](#6.4). For the overall Gradio integration architecture, see [Gradio Overview](#6.1).

---

## Discovery Trigger Points

Endpoint discovery occurs during MCP server initialization in the proxy factory pattern. The `createProxyServerFactory` function intercepts server creation to inject Gradio tool discovery before the server becomes available to clients.

**Discovery Flow Sequence**

```mermaid
sequenceDiagram
    participant Client
    participant Transport as "Transport Layer"
    participant ProxyFactory as "createProxyServerFactory"
    participant GradioUtils as "gradio-utils.ts"
    participant Discovery as "getGradioSpaces"
    participant Connector as "gradio-endpoint-connector"
    participant HFAPI as "HuggingFace API"
    
    Client->>Transport: "Connect/Initialize"
    Transport->>ProxyFactory: "createServer(headers, settings)"
    
    ProxyFactory->>ProxyFactory: "extractAuthBouquetAndMix"
    ProxyFactory->>ProxyFactory: "Check skipGradio flag"
    
    alt skipGradio is true
        ProxyFactory-->>Transport: "Return without Gradio tools"
    else
        ProxyFactory->>ProxyFactory: "Collect space names from<br/>gradio header + settings"
        ProxyFactory->>GradioUtils: "parseGradioSpaceIds(gradioParam)"
        GradioUtils-->>ProxyFactory: "ParsedGradioSpace[]"
        
        ProxyFactory->>Discovery: "getGradioSpaces(spaceNames, hfToken)"
        Discovery->>HFAPI: "Fetch space metadata<br/>(parallel requests)"
        HFAPI-->>Discovery: "Space metadata with subdomains"
        Discovery->>Connector: "fetchEndpointSchema for each space"
        Connector->>HFAPI: "GET /gradio_api/mcp/schema"
        HFAPI-->>Connector: "Tool schemas"
        Discovery-->>ProxyFactory: "GradioSpace[] with tools"
        
        ProxyFactory->>Connector: "registerRemoteTools(server, spaces)"
        Connector-->>ProxyFactory: "Tools registered"
        ProxyFactory-->>Transport: "Server with Gradio tools"
    end
```

**Sources:** [packages/app/src/server/mcp-proxy.ts:83-276](), [packages/app/src/server/gradio-endpoint-connector.ts:273-337]()

---

## Discovery Sources

Gradio spaces can be specified through two channels, which are merged and deduplicated during discovery:

| Source | Format | Priority | Example |
|--------|--------|----------|---------|
| `x-mcp-gradio` Header | Comma-separated space IDs | Takes precedence when both exist | `microsoft/Florence-2-large,acme/foo` |
| User Settings (`spaceTools`) | Array of `SpaceTool` objects | Used if header not provided | `[{name: "user/space", emoji: "🔧"}]` |

The system collects space names from both sources and deduplicates them to avoid redundant API calls:

```mermaid
flowchart TB
    Headers["HTTP Headers"]
    Settings["User Settings"]
    
    Headers --> GradioHeader["x-mcp-gradio header"]
    Settings --> SpaceTools["settings.spaceTools array"]
    
    GradioHeader --> Parse["parseGradioSpaceIds()"]
    SpaceTools --> Extract["Extract .name fields"]
    
    Parse --> SpaceNames["gradioSpaceNames[]"]
    Extract --> SettingsNames["settingsSpaceNames[]"]
    
    SpaceNames --> Merge["Merge and Deduplicate"]
    SettingsNames --> Merge
    
    Merge --> AllSpaces["allSpaceNames[]<br/>(unique space IDs)"]
    
    AllSpaces --> Discovery["getGradioSpaces()<br/>Parallel Discovery"]
```

**Sources:** [packages/app/src/server/mcp-proxy.ts:150-164]()

---

## Space ID Parsing

The `parseGradioSpaceIds` function converts the comma-separated `x-mcp-gradio` header value into structured space identifiers. This function performs validation and handles special cases.

### Parsing Logic

```mermaid
flowchart TD
    Input["gradioParam string<br/>e.g., 'user/space1,org/space2'"]
    
    Input --> Split["Split by comma"]
    Split --> Trim["Trim whitespace from each entry"]
    
    Trim --> CheckNone{Entry equals<br/>'none'?}
    CheckNone -->|Yes| Skip["Skip entry"]
    CheckNone -->|No| Validate
    
    Validate{Valid format?<br/>username/space-name}
    Validate -->|Yes| Add["Add to ParsedGradioSpace[]"]
    Validate -->|No| Warn["Log warning, skip entry"]
    
    Skip --> NextEntry{More entries?}
    Add --> NextEntry
    Warn --> NextEntry
    
    NextEntry -->|Yes| CheckNone
    NextEntry -->|No| Return["Return ParsedGradioSpace[]"]
```

### Validation Rules

The parser enforces strict formatting rules on each space ID:

| Rule | Description | Valid Example | Invalid Example |
|------|-------------|---------------|-----------------|
| Exactly one slash | Must contain `/` separating username and space name | `user/space` | `user/space/extra` or `noslash` |
| Non-empty parts | Content required on both sides of slash | `user/space` | `user/` or `/space` |
| Case preservation | Original casing is maintained | `Microsoft/Florence-2-Large` | N/A |
| Special chars allowed | Dots, dashes, underscores preserved | `user/model-v2.1_test` | N/A |

**Sources:** [packages/app/src/server/utils/gradio-utils.ts:107-144](), [packages/app/test/server/utils/gradio-utils.test.ts:268-449]()

### Parsed Output

The function returns an array of `ParsedGradioSpace` objects:

```typescript
interface ParsedGradioSpace {
  name: string; // e.g., "microsoft/Florence-2-large"
}
```

Note that at this stage, **no subdomain is constructed**. The subdomain must be fetched from the HuggingFace API to ensure accuracy, as it cannot be reliably derived from the space name alone.

**Sources:** [packages/app/src/server/utils/gradio-utils.ts:89-93]()

---

## Metadata Fetching and Caching

After parsing space IDs, the system fetches metadata from the HuggingFace API, including the actual subdomain (which cannot be reliably constructed client-side) and privacy status.

### Discovery API Integration

**getGradioSpaces Flow**

```mermaid
flowchart TD
    Input["spaceNames: string[]<br/>hfToken: string?"]
    
    Input --> Cache{Check<br/>spaceMetadataCache}
    
    Cache -->|Cached| UseCached["Use cached metadata"]
    Cache -->|Not cached| FetchAPI["Fetch from HuggingFace API"]
    
    FetchAPI --> SpaceInfo["spaceInfo({<br/>name: spaceName,<br/>credentials: { accessToken: hfToken }<br/>})"]
    
    SpaceInfo --> CheckPrivacy{Is private<br/>space?}
    
    CheckPrivacy -->|Yes| SkipCache["Do not cache<br/>(auth-sensitive)"]
    CheckPrivacy -->|No| StoreCache["Store in spaceMetadataCache"]
    
    UseCached --> BuildResult
    SkipCache --> BuildResult
    StoreCache --> BuildResult
    
    BuildResult["Construct GradioSpace objects<br/>with _id, name, subdomain, emoji"]
    
    BuildResult --> FetchSchema["fetchEndpointSchema()<br/>for each space"]
    
    FetchSchema --> Return["Return GradioSpace[]<br/>with tools populated"]
```

**Sources:** [packages/app/src/server/utils/gradio-discovery.ts]() (referenced but not in provided files), [packages/app/src/server/gradio-endpoint-connector.ts:142-196]()

### Cache Configuration

The `spaceMetadataCache` stores public space metadata to reduce API calls:

| Configuration | Value | Purpose |
|---------------|-------|---------|
| Cache Target | Public spaces only | Private spaces require fresh auth checks |
| Cache Duration | Based on `CACHE_CONFIG.SPACE_INFO_TIMEOUT` | Balances freshness vs. performance |
| Cache Key | Space name (e.g., `microsoft/Florence-2-large`) | Direct lookup by space ID |
| Stored Fields | `_id`, `name`, `subdomain`, `emoji`, `private`, `sdk`, `fetchedAt` | Complete metadata for reconstruction |

**Privacy-Aware Caching Strategy:**
- Public spaces are cached after first fetch
- Private spaces are **never cached** to ensure auth tokens are validated on every request
- Cache miss triggers immediate API call with timeout protection

**Sources:** [packages/app/src/server/utils/gradio-cache.ts:14]() (referenced), [packages/app/src/server/gradio-endpoint-connector.ts:142-196]()

---

## Schema Fetching

Once space metadata is retrieved, the system fetches tool schemas from each Gradio space's `/gradio_api/mcp/schema` endpoint.

### Schema Fetch Architecture

**fetchEndpointSchema Function**

```mermaid
flowchart TD
    Input["GradioEndpoint<br/>(name, subdomain)"]
    
    Input --> CheckPrivacy["isSpacePrivate()<br/>Check cache then API"]
    CheckPrivacy --> PrepareAuth{Is private<br/>space?}
    
    PrepareAuth -->|Yes| AddAuth["Add X-HF-Authorization header<br/>with hfToken"]
    PrepareAuth -->|No| NoAuth["No auth header needed"]
    
    AddAuth --> BuildURL
    NoAuth --> BuildURL
    
    BuildURL["schemaUrl =<br/>https://{subdomain}.hf.space/<br/>gradio_api/mcp/schema"]
    
    BuildURL --> Timeout["Create AbortController<br/>timeout = HF_API_TIMEOUT (12.5s)"]
    
    Timeout --> Fetch["fetch(schemaUrl, {<br/>method: 'GET',<br/>headers,<br/>signal: controller.signal<br/>})"]
    
    Fetch --> CheckStatus{Response<br/>OK?}
    
    CheckStatus -->|No| Error["Throw error with status"]
    CheckStatus -->|Yes| ParseJSON["Parse JSON response"]
    
    ParseJSON --> ParseSchema["parseSchemaResponse()<br/>Extract tools"]
    
    ParseSchema --> FilterLambda["Filter out tools with<br/>'<lambda' in name"]
    
    FilterLambda --> BuildTools["Convert to Tool[] format<br/>with inputSchema"]
    
    BuildTools --> Return["Return EndpointConnection<br/>{endpointId, tools, sseUrl, isPrivate}"]
```

**Sources:** [packages/app/src/server/gradio-endpoint-connector.ts:201-267]()

### Schema Response Formats

The system handles two different schema formats returned by Gradio endpoints:

**Format 1: Array Format (Newer)**
```typescript
[
  {
    name: "toolName",
    description: "Tool description",
    inputSchema: {
      type: "object",
      properties: { /* ... */ },
      required: []
    }
  },
  // ... more tools
]
```

**Format 2: Object Format (Legacy)**
```typescript
{
  "toolName": {
    type: "object",
    description: "Tool description",
    properties: { /* ... */ },
    required: []
  },
  // ... more tools
}
```

The `parseSchemaResponse` function detects which format is used and normalizes both into a common structure:

**Sources:** [packages/app/src/server/gradio-endpoint-connector.ts:84-137]()

### Parallel Schema Fetching

The system fetches schemas from multiple endpoints concurrently with timeout protection:

```mermaid
flowchart LR
    Endpoints["gradioEndpoints[]"]
    
    Endpoints --> Task1["Promise.race([<br/>fetchEndpointSchema(ep1),<br/>createTimeout(12s)<br/>])"]
    
    Endpoints --> Task2["Promise.race([<br/>fetchEndpointSchema(ep2),<br/>createTimeout(12s)<br/>])"]
    
    Endpoints --> Task3["Promise.race([<br/>fetchEndpointSchema(ep3),<br/>createTimeout(12s)<br/>])"]
    
    Task1 --> Result1["EndpointConnectionResult"]
    Task2 --> Result2["EndpointConnectionResult"]
    Task3 --> Result3["EndpointConnectionResult"]
    
    Result1 --> AllResults["Promise.all([...])"]
    Result2 --> AllResults
    Result3 --> AllResults
    
    AllResults --> Results["EndpointConnectionResult[]<br/>(success + failed)"]
```

Each fetch operation races against a timeout, ensuring no single slow endpoint blocks the entire discovery process. Results include both successful connections and failures for logging.

**Sources:** [packages/app/src/server/gradio-endpoint-connector.ts:273-337]()

---

## Connection Results and Error Handling

### Result Structure

The `connectToGradioEndpoints` function returns an array of `EndpointConnectionResult`, where each result can be either successful or failed:

```typescript
type EndpointConnectionResult =
  | {
      success: true;
      endpointId: string;
      connection: EndpointConnection;
    }
  | {
      success: false;
      endpointId: string;
      error: Error;
    };
```

**EndpointConnection Structure:**

| Field | Type | Description |
|-------|------|-------------|
| `endpointId` | `string` | Unique identifier (e.g., `endpoint1`, `endpoint2`) |
| `originalIndex` | `number` | Zero-based position in request list |
| `client` | `Client \| null` | Always `null` in schema-only approach (lazy connection) |
| `tools` | `Tool[]` | Parsed tool schemas from endpoint |
| `name` | `string?` | Space name (e.g., `microsoft/Florence-2-large`) |
| `emoji` | `string?` | Optional emoji for tool display |
| `sseUrl` | `string?` | SSE endpoint URL for tool execution (stored for lazy connection) |
| `isPrivate` | `boolean?` | Whether the space requires authentication |

**Sources:** [packages/app/src/server/gradio-endpoint-connector.ts:40-49](), [packages/app/src/server/gradio-endpoint-connector.ts:56-66]()

### Error Handling Strategy

**Graceful Degradation with Metrics**

```mermaid
flowchart TD
    FetchAttempt["Attempt schema fetch"]
    
    FetchAttempt --> Success{Success?}
    
    Success -->|Yes| LogSuccess["Log successful fetch<br/>Return connection"]
    
    Success -->|No| CheckFirst["gradioMetrics.schemaFetchError()<br/>Check if first error for this space"]
    
    CheckFirst --> IsFirst{First error<br/>for space?}
    
    IsFirst -->|Yes| WarnLog["Log at 'warn' level<br/>(visible in logs)"]
    IsFirst -->|No| TraceLog["Log at 'trace' level<br/>(reduce noise)"]
    
    WarnLog --> ReturnFailed["Return {success: false,<br/>endpointId, error}"]
    TraceLog --> ReturnFailed
    
    LogSuccess --> Continue["Continue with<br/>successful endpoints"]
    ReturnFailed --> Continue
    
    Continue --> RegisterTools["Register tools from<br/>successful endpoints only"]
```

The system uses **progressive log level reduction** to avoid log spam from repeatedly failing endpoints while still capturing the first error for each space. This approach allows the server to start successfully even if some Gradio endpoints are unavailable.

**Sources:** [packages/app/src/server/gradio-endpoint-connector.ts:288-318]()

### Lazy Connection Model

The endpoint discovery phase **does not establish live SSE connections**. Instead, it:

1. Fetches only the schema via HTTP GET
2. Stores the SSE URL for later use
3. Sets `client: null` in the connection object

This "lazy connection" approach improves startup performance and reduces resource usage. The actual SSE connection is established only when a tool is invoked, as detailed in [Tool Execution and Post-Processing](#6.4).

**Sources:** [packages/app/src/server/gradio-endpoint-connector.ts:257-266]()

---

## Integration with Server Registration

After successful discovery, the proxy factory merges emoji data from user settings and registers all discovered tools with the MCP server:

**Registration Flow**

```mermaid
flowchart TD
    Discovery["getGradioSpaces()<br/>Returns GradioSpace[]"]
    
    Discovery --> Merge["Merge emoji from<br/>settings.spaceTools<br/>if available"]
    
    Merge --> Loop["For each discovered space"]
    
    Loop --> CreateConn["Create connection object:<br/>{endpointId, tools, name,<br/>emoji, sseUrl, isPrivate}"]
    
    CreateConn --> Register["registerRemoteTools(<br/>server, connection,<br/>hfToken, sessionInfo,<br/>{stripImageContent, gradioWidgetUri}<br/>)"]
    
    Register --> ToolCreation["Create MCP tools with<br/>gr<N>_<name> pattern"]
    
    ToolCreation --> NextSpace{More spaces?}
    
    NextSpace -->|Yes| Loop
    NextSpace -->|No| Complete["Discovery complete<br/>Server ready with Gradio tools"]
```

**Sources:** [packages/app/src/server/mcp-proxy.ts:168-213](), [packages/app/src/server/gradio-endpoint-connector.ts:544-613]()

---

# Page: Schema Conversion

# Schema Conversion

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [packages/app/src/server/gradio-endpoint-connector.ts](packages/app/src/server/gradio-endpoint-connector.ts)
- [packages/app/src/server/mcp-proxy.ts](packages/app/src/server/mcp-proxy.ts)

</details>



## Purpose and Scope

This page explains how Gradio JSON schemas are converted to Zod schemas and registered as MCP tools. This conversion process is the bridge between Gradio's tool definitions and the MCP protocol's tool invocation system. For information about discovering and fetching these schemas from Gradio endpoints, see [Endpoint Discovery](#6.2). For details on how these tools are executed after registration, see [Tool Execution and Post-Processing](#6.4).

The conversion process handles multiple schema formats, complex type mappings, and special cases like file inputs and enumerations, ensuring that Gradio tools can be seamlessly invoked through the MCP protocol.

---

## Schema Response Formats

Gradio endpoints expose their tool schemas via a `/gradio_api/mcp/schema` endpoint. The response can be in two different formats, and the system handles both.

### Array Format

The array format provides a structured list of tools with explicit names, descriptions, and input schemas:

```json
[
  {
    "name": "generate_image",
    "description": "Generate an image from a text prompt",
    "inputSchema": {
      "type": "object",
      "properties": {
        "prompt": { "type": "string", "description": "The text prompt" }
      },
      "required": ["prompt"]
    }
  }
]
```

This format is detected when the response is an array, and each element must have `name` and `inputSchema` properties. Lambda functions (tools with names containing `"<lambda"`) are filtered out as they represent internal Gradio operations.

Sources: [packages/app/src/server/gradio-endpoint-connector.ts:92-109]()

### Object Format

The object format uses tool names as keys with schemas as values:

```json
{
  "generate_image": {
    "type": "object",
    "properties": {
      "prompt": { "type": "string", "description": "The text prompt" }
    },
    "required": ["prompt"],
    "description": "Generate an image from a text prompt"
  }
}
```

The system detects this format when the response is an object (not an array) and maps each key-value pair to a tool definition.

Sources: [packages/app/src/server/gradio-endpoint-connector.ts:110-125]()

### Schema Parsing Function

```mermaid
flowchart TD
    Start["parseSchemaResponse()"] --> CheckType{"schemaResponse<br/>type?"}
    
    CheckType -->|"Array"| ArrayPath["Filter valid tools:<br/>- has 'name' property<br/>- has 'inputSchema' property"]
    CheckType -->|"Object"| ObjectPath["Map entries:<br/>Object.entries(schema)"]
    CheckType -->|"Other"| ErrorPath["Throw Error:<br/>'Invalid schema format'"]
    
    ArrayPath --> FilterLambda["Filter out tools with<br/>'&lt;lambda' in name"]
    ObjectPath --> MapToTools["Create tool objects:<br/>{name, description, inputSchema}"]
    
    FilterLambda --> ValidateCount{"tools.length<br/>&gt; 0?"}
    MapToTools --> ValidateCount
    
    ValidateCount -->|"Yes"| LogSuccess["Log debug:<br/>Retrieved schema"]
    ValidateCount -->|"No"| ErrorNoTools["Throw Error:<br/>'No tools found in schema'"]
    
    LogSuccess --> Return["Return tool array"]
    
    style Start fill:#f9f9f9
    style Return fill:#f9f9f9
    style ErrorPath fill:#ffe6e6
    style ErrorNoTools fill:#ffe6e6
```

**Diagram: Schema Response Parsing Flow**

The `parseSchemaResponse` function normalizes both formats into a consistent array of tool definitions, validates their structure, and filters out invalid entries.

Sources: [packages/app/src/server/gradio-endpoint-connector.ts:84-137]()

---

## JSON Schema to Zod Conversion

The core conversion process transforms JSON Schema definitions into Zod schemas that can be used for runtime validation and type inference in the MCP server.

### Type Mapping Table

| JSON Schema Type | Zod Schema | Notes |
|-----------------|------------|-------|
| `"string"` | `z.string()` | Basic string validation |
| `"number"` | `z.number()` | Numeric values |
| `"boolean"` | `z.boolean()` | Boolean values |
| `"array"` | `z.array(z.any())` | Arrays with any element type |
| `"object"` | `z.object({})` | Empty object schema |
| `undefined` or other | `z.any()` | Fallback for unknown types |

Sources: [packages/app/src/server/gradio-endpoint-connector.ts:696-716]()

### Special Type Handling

#### FileData Type

Gradio uses a special `FileData` type for file inputs. The system detects this type through either:
- `jsonSchemaProperty.title === 'FileData'`
- `jsonSchemaProperty.format === 'a http or https url to a file'` with an object default value

When detected, it creates a structured Zod schema:

```typescript
z.object({
  path: z.string(),
  url: z.string().optional(),
  size: z.number().nullable().optional(),
  orig_name: z.string().optional(),
  mime_type: z.string().nullable().optional(),
  is_stream: z.boolean().optional(),
  meta: z.object({
    _type: z.string().optional(),
  }).optional(),
})
```

This allows clients to pass file references with metadata that Gradio can resolve.

Sources: [packages/app/src/server/gradio-endpoint-connector.ts:649-669]()

#### Enum Types

Enumeration types are handled based on their value types:

- **String enums**: Converted to `z.enum()` with type-safe string literal types
- **Mixed enums**: Converted to a union of `z.literal()` values for each enum member
- **Single-value enums**: Simplified to a single literal

```mermaid
flowchart TD
    Start["Check enum property"] --> HasEnum{"Has 'enum'<br/>array?"}
    
    HasEnum -->|"No"| TypeSwitch["Switch on<br/>'type' property"]
    HasEnum -->|"Yes"| CheckAllStrings{"All values<br/>are strings?"}
    
    CheckAllStrings -->|"Yes"| ZEnum["z.enum(values)"]
    CheckAllStrings -->|"No"| MapLiterals["Map to z.literal()<br/>for each value"]
    
    MapLiterals --> CountLiterals{"literals.length"}
    CountLiterals -->|"1"| SingleLiteral["Return literals[0]"]
    CountLiterals -->|"≥2"| UnionLiterals["z.union(literals)"]
    CountLiterals -->|"0"| FallbackAny["z.any()"]
    
    ZEnum --> AddDescription
    SingleLiteral --> AddDescription
    UnionLiterals --> AddDescription
    FallbackAny --> AddDescription
    
    TypeSwitch -->|"string"| ZString["z.string()"]
    TypeSwitch -->|"number"| ZNumber["z.number()"]
    TypeSwitch -->|"boolean"| ZBoolean["z.boolean()"]
    TypeSwitch -->|"array"| ZArray["z.array(z.any())"]
    TypeSwitch -->|"object"| ZObject["z.object({})"]
    TypeSwitch -->|"other"| ZAnyType["z.any()"]
    
    ZString --> AddDescription["Add description<br/>if present"]
    ZNumber --> AddDescription
    ZBoolean --> AddDescription
    ZArray --> AddDescription
    ZObject --> AddDescription
    ZAnyType --> AddDescription
    
    AddDescription --> CheckDefault{"Has default<br/>value?"}
    CheckDefault -->|"Yes"| ApplyDefault["zodSchema.default(value)"]
    CheckDefault -->|"No"| Return["Return zodSchema"]
    ApplyDefault --> Return
    
    style Start fill:#f9f9f9
    style Return fill:#f9f9f9
```

**Diagram: JSON Schema Property to Zod Conversion Logic**

Sources: [packages/app/src/server/gradio-endpoint-connector.ts:670-695]()

### Default Values and Descriptions

The conversion process enhances schemas with default values and descriptions:

1. **Descriptions**: Copied from the JSON Schema's `description` property. For file inputs, a helpful hint is appended: `"(File input: provide URL or file path)"`

2. **Default values**: Applied using `.default()` unless the field is required. For string types with object defaults containing a `url` property, the URL is extracted as the default value instead of the full object (except for `FileData` types which keep the full object).

3. **File input enhancement**: Properties with `format === "a http or https url to a file"` get special description text to guide users.

Sources: [packages/app/src/server/gradio-endpoint-connector.ts:719-751]()

### Required vs Optional Fields

The conversion process respects the `required` array from JSON Schema:

```mermaid
flowchart LR
    Schema["JSON Schema<br/>{properties, required}"] --> Iterate["For each property"]
    
    Iterate --> Convert["convertJsonSchemaToZod()"]
    Convert --> CheckRequired{"In 'required'<br/>array?"}
    
    CheckRequired -->|"Yes"| SkipDefault["skipDefault = true<br/>(no default applied)"]
    CheckRequired -->|"No"| MakeOptional["zodSchema.optional()"]
    
    SkipDefault --> AddToShape["Add to schemaShape"]
    MakeOptional --> AddToShape
    
    AddToShape --> Complete["Return schemaShape"]
    
    style Schema fill:#f9f9f9
    style Complete fill:#f9f9f9
```

**Diagram: Required Field Handling**

Required fields don't get the `.optional()` modifier and skip default value application to ensure clients must provide them explicitly.

Sources: [packages/app/src/server/gradio-endpoint-connector.ts:615-639]()

---

## Tool Registration Process

After schema conversion, tools are registered with the MCP server through a multi-step process that creates callable tools with proper metadata and handlers.

### Tool Name Generation

Each Gradio tool receives a unique outward-facing name using `createGradioToolName()`:

```
gr{originalIndex + 1}_{privacyMarker}_{toolName}_{toolIndex}
```

- `originalIndex`: Position in the Gradio endpoints list
- `privacyMarker`: `"private"` for private spaces, omitted for public
- `toolName`: Original tool name from Gradio
- `toolIndex`: Index within the endpoint's tools (only if multiple tools exist)

Examples:
- `gr1_generate_image` - First endpoint, public space, single tool
- `gr2_private_upscale_0` - Second endpoint, private space, first of multiple tools

Sources: [packages/app/src/server/gradio-endpoint-connector.ts:557-562](), [packages/app/src/server/utils/gradio-utils.ts]()

### Registration Flow

```mermaid
flowchart TD
    Start["registerRemoteTools()"] --> ForEach["For each tool in<br/>connection.tools"]
    
    ForEach --> GenerateName["createGradioToolName():<br/>gr{N}_{private}_name_{idx}"]
    GenerateName --> CreateDisplay["createToolDisplayInfo():<br/>title & description"]
    CreateDisplay --> ConvertSchema["convertToolSchemaToZod():<br/>JSON Schema → Zod"]
    ConvertSchema --> CreateHandler["createToolHandler():<br/>Async function"]
    
    CreateHandler --> LogTrace["logger.trace():<br/>Registration details"]
    LogTrace --> RegisterTool["server.tool():<br/>name, desc, schema, handler"]
    
    RegisterTool --> CheckClient{"sessionInfo.clientInfo.name<br/>== 'openai-mcp'?"}
    CheckClient -->|"Yes"| AddMeta["Add _meta with:<br/>- outputTemplate<br/>- invoking/invoked messages"]
    CheckClient -->|"No"| NextTool["Next tool"]
    
    AddMeta --> NextTool
    NextTool --> MoreTools{"More tools?"}
    MoreTools -->|"Yes"| ForEach
    MoreTools -->|"No"| Complete["All tools registered"]
    
    style Start fill:#f9f9f9
    style Complete fill:#f9f9f9
```

**Diagram: Tool Registration Pipeline**

Sources: [packages/app/src/server/gradio-endpoint-connector.ts:544-613]()

### Tool Handler Creation

The `createToolHandler()` function creates an async handler that:

1. **Validates parameters** against the Zod schema
2. **Establishes SSE connection** to the Gradio space (lazy connection)
3. **Invokes the tool** via `callGradioTool()`
4. **Applies post-processing** (image filtering, OpenAI transformations)
5. **Tracks metrics** (duration, success/failure, response size)
6. **Logs events** for monitoring and debugging

The handler has access to:
- `connection.sseUrl`: SSE endpoint for the Gradio space
- `tool.name`: Original Gradio tool name
- `hfToken`: For authenticated requests to private spaces
- `sessionInfo`: Client session metadata
- `options`: Post-processing options (image stripping, widget URI)

Sources: [packages/app/src/server/gradio-endpoint-connector.ts:354-539]()

### OpenAI MCP Client Enhancements

When the client is identified as `'openai-mcp'`, additional metadata is attached to the tool:

```typescript
theTool._meta = {
  'openai/outputTemplate': gradioWidgetUri || '',
  'openai/toolInvocation/invoking': `Calling the Hugging Face Space ${spaceName}`,
  'openai/toolInvocation/invoked': `Your content is being generated`,
}
```

This provides OpenAI-specific UI enhancements including:
- Custom output templates via resource URIs
- User-friendly invocation status messages
- Integration with OpenAI's structured content system

Sources: [packages/app/src/server/gradio-endpoint-connector.ts:605-611](), [packages/app/src/server/mcp-proxy.ts:103-106]()

---

## Complete Conversion Pipeline

```mermaid
flowchart TD
    FetchSchema["fetchEndpointSchema()<br/>GET /gradio_api/mcp/schema"] --> ParseResponse["parseSchemaResponse()<br/>Handle array/object format"]
    
    ParseResponse --> CreateConnection["Create EndpointConnection:<br/>{endpointId, tools, sseUrl, ...}"]
    CreateConnection --> RegisterCall["registerRemoteTools(server,<br/>connection, hfToken, options)"]
    
    RegisterCall --> LoopTools["For each tool"]
    LoopTools --> NameTool["createGradioToolName()"]
    NameTool --> DisplayInfo["createToolDisplayInfo()"]
    DisplayInfo --> SchemaConversion["convertToolSchemaToZod()"]
    
    SchemaConversion --> IterateProps["For each property<br/>in inputSchema"]
    IterateProps --> ConvertProp["convertJsonSchemaToZod()"]
    ConvertProp --> CheckType{"Property type?"}
    
    CheckType -->|"FileData"| FileDataSchema["z.object({path, url, ...})"]
    CheckType -->|"Enum"| EnumSchema["z.enum() or z.union()"]
    CheckType -->|"Primitive"| PrimitiveSchema["z.string/number/boolean()"]
    CheckType -->|"Complex"| ComplexSchema["z.array/object()"]
    
    FileDataSchema --> AddDesc["Add description"]
    EnumSchema --> AddDesc
    PrimitiveSchema --> AddDesc
    ComplexSchema --> AddDesc
    
    AddDesc --> CheckReq{"Required?"}
    CheckReq -->|"Yes"| KeepRequired["Keep as-is"]
    CheckReq -->|"No"| MakeOpt["Add .optional()"]
    
    KeepRequired --> BuildShape["Add to schemaShape"]
    MakeOpt --> BuildShape
    
    BuildShape --> MoreProps{"More properties?"}
    MoreProps -->|"Yes"| IterateProps
    MoreProps -->|"No"| CreateHandler["createToolHandler()"]
    
    CreateHandler --> ServerTool["server.tool(name,<br/>desc, schema, handler)"]
    ServerTool --> CheckOpenAI{"OpenAI MCP<br/>client?"}
    CheckOpenAI -->|"Yes"| AddOpenAIMeta["Add _meta with<br/>OpenAI annotations"]
    CheckOpenAI -->|"No"| Done["Tool registered"]
    AddOpenAIMeta --> Done
    
    Done --> MoreTools{"More tools?"}
    MoreTools -->|"Yes"| LoopTools
    MoreTools -->|"No"| Complete["All tools registered<br/>and ready to invoke"]
    
    style FetchSchema fill:#f9f9f9
    style Complete fill:#f9f9f9
```

**Diagram: End-to-End Schema Conversion and Registration**

This diagram shows the complete flow from fetching a schema to having fully registered, invokable MCP tools. The process ensures type safety through Zod validation, proper error handling, and client-specific enhancements.

Sources: [packages/app/src/server/gradio-endpoint-connector.ts:201-267](), [packages/app/src/server/gradio-endpoint-connector.ts:544-613](), [packages/app/src/server/mcp-proxy.ts:191-213]()

---

## Type Definitions

The schema conversion process uses several TypeScript interfaces to maintain type safety:

| Interface | Purpose | Key Properties |
|-----------|---------|----------------|
| `JsonSchemaProperty` | Represents a single property in JSON Schema | `type`, `description`, `default`, `enum` |
| `JsonSchema` | Complete JSON Schema definition | `type`, `properties`, `required` |
| `ArrayFormatTool` | Tool definition in array format | `name`, `description`, `inputSchema` |
| `EndpointConnection` | Connection metadata for a Gradio endpoint | `endpointId`, `tools`, `sseUrl`, `isPrivate` |

Sources: [packages/app/src/server/gradio-endpoint-connector.ts:18-49]()

---

## Error Handling

The conversion process includes robust error handling:

1. **Invalid schema format**: Throws error if response is neither array nor object
2. **Empty schemas**: Throws error if no valid tools are found after parsing
3. **Type conversion failures**: Falls back to `z.any()` for unrecognized types
4. **Lambda filtering**: Automatically excludes internal Gradio lambda functions

All errors are logged with context (endpoint ID, subdomain, schema type) to aid debugging.

Sources: [packages/app/src/server/gradio-endpoint-connector.ts:126-134]()

---

# Page: Tool Execution and Post-Processing

# Tool Execution and Post-Processing

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [packages/app/src/server/gradio-endpoint-connector.ts](packages/app/src/server/gradio-endpoint-connector.ts)
- [packages/app/src/server/mcp-proxy.ts](packages/app/src/server/mcp-proxy.ts)

</details>



This page describes how dynamically-discovered Gradio tools are invoked at runtime and how their results are processed before being returned to the client. It covers the SSE connection mechanism, result post-processing pipeline, image filtering capabilities, and client-specific transformations for OpenAI compatibility.

For information about discovering Gradio spaces and fetching schemas, see [Endpoint Discovery](#6.2). For information about converting JSON schemas to Zod schemas during registration, see [Schema Conversion](#6.3).

## Overview

When a Gradio tool is registered (via `registerRemoteTools`), the system creates a handler function that establishes an SSE connection to the Gradio space only when the tool is actually invoked. This lazy connection approach avoids unnecessary overhead during server initialization. The handler function coordinates tool execution, progress relay, result post-processing, and error handling.

**Sources:** [packages/app/src/server/gradio-endpoint-connector.ts:354-539]()

## Tool Handler Creation

The `createToolHandler` function creates the execution handler for each Gradio tool. This handler is registered with the MCP server and invoked when a client calls the tool.

### Handler Configuration

```mermaid
graph TB
    createToolHandler["createToolHandler()"]
    
    subgraph "Input Parameters"
        connection["EndpointConnection"]
        tool["Tool (name, schema)"]
        outwardFacingName["outwardFacingName"]
        hfToken["hfToken (optional)"]
        sessionInfo["sessionInfo (optional)"]
        options["RegisterRemoteToolsOptions"]
    end
    
    subgraph "Options Object"
        stripImageContent["stripImageContent: boolean"]
        gradioWidgetUri["gradioWidgetUri: string"]
    end
    
    subgraph "Handler Function"
        handler["async (params, extra) => CallToolResult"]
    end
    
    connection --> createToolHandler
    tool --> createToolHandler
    outwardFacingName --> createToolHandler
    hfToken --> createToolHandler
    sessionInfo --> createToolHandler
    options --> createToolHandler
    
    stripImageContent --> options
    gradioWidgetUri --> options
    
    createToolHandler --> handler
```

The `createToolHandler` function accepts:
- **connection**: `EndpointConnection` containing `sseUrl`, `name`, `isPrivate`, etc.
- **tool**: The `Tool` object with `name` and `inputSchema`
- **outwardFacingName**: The prefixed tool name (e.g., `gradio_1_image_gen`)
- **hfToken**: Hugging Face authentication token (forwarded to private spaces)
- **sessionInfo**: Client session metadata (session ID, client name/version)
- **options**: `RegisterRemoteToolsOptions` containing `stripImageContent` and `gradioWidgetUri`

**Sources:** [packages/app/src/server/gradio-endpoint-connector.ts:354-368]()

## Tool Execution Flow

When a client invokes a Gradio tool, the handler follows this execution sequence:

```mermaid
sequenceDiagram
    participant Client
    participant Handler as "Tool Handler"
    participant Caller as "callGradioTool()"
    participant SSE as "SSE Connection"
    participant Space as "Gradio Space"
    participant PostProcess as "applyResultPostProcessing()"
    
    Client->>Handler: "Call tool with params"
    Handler->>Handler: "Validate sseUrl exists"
    Handler->>Caller: "callGradioTool(sseUrl, toolName, params, token, extra)"
    
    Caller->>SSE: "Establish SSE connection"
    SSE->>Space: "Connect to /gradio_api/mcp/sse"
    Space-->>SSE: "SSE stream established"
    
    Caller->>Space: "Send MCP tools/call request"
    
    loop Progress Updates
        Space-->>SSE: "Progress notifications"
        SSE-->>Caller: "Relay progress"
        Caller-->>Handler: "Forward via extra.sendProgress()"
        Handler-->>Client: "Progress notifications"
    end
    
    Space-->>SSE: "Final result"
    SSE-->>Caller: "CallToolResult"
    Caller-->>Handler: "Return result"
    
    Handler->>Handler: "Check for _mcpui suffix"
    
    alt Tool has _mcpui suffix and returns URL
        Handler->>Handler: "Fetch audio file"
        Handler->>Handler: "Create audio player UI resource"
    end
    
    Handler->>PostProcess: "applyResultPostProcessing(result, options)"
    PostProcess-->>Handler: "Processed result"
    Handler-->>Client: "Final CallToolResult"
```

### SSE Connection and Tool Invocation

The actual SSE connection and MCP protocol communication is delegated to `callGradioTool` from `gradio-tool-caller.ts`. This function:
1. Establishes an SSE connection to the space's `/gradio_api/mcp/sse` endpoint
2. Sends the `tools/call` MCP request with the tool name and parameters
3. Relays progress notifications back to the client via `extra.sendProgress()`
4. Returns the final `CallToolResult`

**Sources:** [packages/app/src/server/gradio-endpoint-connector.ts:386](), [packages/app/src/server/utils/gradio-tool-caller.ts:15]()

### Error Handling During Execution

If the tool execution fails, the handler:
1. Extracts a meaningful error message from the result's content array
2. Records the failure in `gradioMetrics`
3. Logs the Gradio event with error details
4. Re-throws the error for upstream handling

**Sources:** [packages/app/src/server/gradio-endpoint-connector.ts:396-427](), [packages/app/src/server/gradio-endpoint-connector.ts:500-523]()

## Special UI Resource Handling

Before applying standard post-processing, the handler checks for special UI resource transformations.

### Audio Player UI Resource

If a tool name contains `_mcpui` and returns a single text URL, the handler wraps it as an embedded audio player UI resource:

```mermaid
graph LR
    Check["Check: tool.name includes '_mcpui'"]
    Result["Result: single text item"]
    URLCheck["Text matches /^https?:\/\//"]
    
    subgraph "Transform Process"
        Fetch["Fetch audio from URL"]
        Encode["Base64 encode audio"]
        Create["createAudioPlayerUIResource()"]
    end
    
    Resource["UI Resource with embedded audio"]
    Fallback["Use URL as fallback source"]
    Decorated["Decorated result with UI resource"]
    
    Check --> Result
    Result --> URLCheck
    URLCheck -->|"Yes"| Fetch
    Fetch -->|"Success"| Encode
    Fetch -->|"Failure"| Fallback
    Encode --> Create
    Fallback --> Create
    Create --> Resource
    Resource --> Decorated
```

The audio player resource is created with:
- **uri**: Generated as `ui://huggingface-mcp/{space-name}/{timestamp}`
- **title**: Space name
- **base64Audio**: Inlined audio data (if fetch succeeds)
- **srcUrl**: Original URL (if fetch fails)
- **mimeType**: Set to `audio/wav`

The decorated result includes both the original text content and the UI resource.

**Sources:** [packages/app/src/server/gradio-endpoint-connector.ts:447-496](), [packages/app/src/server/utils/ui/audio-player.ts:13]()

## Result Post-Processing Pipeline

After special UI handling, all results pass through `applyResultPostProcessing`, which applies transformations based on configuration options.

### Post-Processing Options

The `GradioToolCallOptions` object passed to post-processing contains:

| Option | Type | Source | Purpose |
|--------|------|--------|---------|
| `stripImageContent` | `boolean` | Header or user settings | Whether to remove image content from results |
| `toolName` | `string` | Tool metadata | Original tool name (not prefixed) |
| `outwardFacingName` | `string` | Tool metadata | Prefixed tool name for logging |
| `sessionInfo` | `object` | Session context | Client session metadata |
| `gradioWidgetUri` | `string` | Widget resource | URI for OpenAI widget embedding |
| `spaceName` | `string` | Space metadata | Name of the Gradio space |

**Sources:** [packages/app/src/server/gradio-endpoint-connector.ts:436-443](), [packages/app/src/server/utils/gradio-tool-caller.ts:19-26]()

### Post-Processing Flow

```mermaid
graph TB
    Input["CallToolResult"]
    
    CheckError{"isError?"}
    
    subgraph "Image Filtering"
        CheckStrip{"stripImageContent?"}
        RemoveImages["Remove all image content items"]
        CountImages["Count removed images"]
        LogImages["Log image removal"]
    end
    
    subgraph "OpenAI Transformation"
        CheckOpenAI{"Client is openai-mcp?"}
        HasWidget{"Has gradioWidgetUri?"}
        Transform["Transform to structured content"]
        EmbedWidget["Embed widget with srcUrl"]
    end
    
    Output["Processed CallToolResult"]
    
    Input --> CheckError
    CheckError -->|"Yes"| Output
    CheckError -->|"No"| CheckStrip
    
    CheckStrip -->|"Yes"| RemoveImages
    RemoveImages --> CountImages
    CountImages --> LogImages
    LogImages --> CheckOpenAI
    
    CheckStrip -->|"No"| CheckOpenAI
    
    CheckOpenAI -->|"Yes"| HasWidget
    HasWidget -->|"Yes"| Transform
    Transform --> EmbedWidget
    EmbedWidget --> Output
    
    HasWidget -->|"No"| Output
    CheckOpenAI -->|"No"| Output
```

**Sources:** [packages/app/src/server/utils/gradio-tool-caller.ts:90-181]()

## Image Content Filtering

When `stripImageContent` is enabled (via `x-mcp-no-image-content: true` header or `GRADIO_IMAGE_FILTER` in user settings), the post-processor removes all image content items from the result.

### Image Removal Process

1. Iterate through `result.content` array
2. Identify items with `type: "image"`
3. Remove these items from the array
4. Track count of removed images
5. Log removal if any images were filtered

```mermaid
graph LR
    Content["result.content[]"]
    
    subgraph "Filter Logic"
        Iterate["For each content item"]
        CheckType{"type === 'image'?"}
        Keep["Keep item"]
        Remove["Remove item"]
        Count["Increment removedCount"]
    end
    
    Filtered["Filtered content array"]
    Log["Log: 'Stripped N image(s)'"]
    
    Content --> Iterate
    Iterate --> CheckType
    CheckType -->|"No"| Keep
    CheckType -->|"Yes"| Remove
    Remove --> Count
    Keep --> Filtered
    Count --> Filtered
    Filtered --> Log
```

This filtering is useful for:
- Reducing response payload size
- Clients that cannot display images
- Analytics/monitoring scenarios where images are unnecessary

**Sources:** [packages/app/src/server/utils/gradio-tool-caller.ts:104-119]()

## OpenAI-Specific Transformations

When the client is identified as `openai-mcp` (via `sessionInfo.clientInfo.name`), results are transformed into OpenAI's structured content format.

### Structured Content Format

Standard MCP content items are transformed as follows:

| MCP Type | OpenAI Structured Type | Additional Fields |
|----------|------------------------|-------------------|
| `text` | `text` | `title`, `description` |
| `image` | `image` | `srcUrl` (from `data` or `url`) |

### Widget Embedding

If a `gradioWidgetUri` is provided, the post-processor embeds it in the result by adding a `widgetElement` field to each content item:

```json
{
  "type": "text",
  "text": "...",
  "widgetElement": {
    "srcUrl": "resource://huggingface-mcp-gradio-widget/v1.2.3"
  }
}
```

This allows the OpenAI client to render an interactive Gradio widget alongside the result.

**Sources:** [packages/app/src/server/utils/gradio-tool-caller.ts:124-181]()

### OpenAI Metadata Registration

During tool registration, if the client is `openai-mcp`, the tool is annotated with OpenAI-specific metadata:

```typescript
theTool._meta = {
  'openai/outputTemplate': gradioWidgetUri || '',
  'openai/toolInvocation/invoking': `Calling the Hugging Face Space ${spaceName}`,
  'openai/toolInvocation/invoked': `Your content is being generated`
};
```

This metadata provides progress messages that the OpenAI client displays during tool execution.

**Sources:** [packages/app/src/server/gradio-endpoint-connector.ts:605-611]()

## Metrics and Logging

### Metrics Tracking

The handler tracks metrics at multiple stages:

1. **Start time**: Captured before tool execution
2. **Success/Failure**: Recorded in `gradioMetrics` after execution
3. **Response size**: Estimated from JSON serialization
4. **Duration**: Calculated as `endTime - startTime`

```mermaid
graph TB
    Start["Start: Record startTime"]
    
    Execute["Execute callGradioTool()"]
    
    Success{"Success?"}
    RecordSuccess["gradioMetrics.recordSuccess()"]
    RecordFailure["gradioMetrics.recordFailure()"]
    
    CalcSize["Calculate responseSizeBytes"]
    CalcDuration["Calculate duration"]
    
    LogEvent["logGradioEvent()"]
    
    Start --> Execute
    Execute --> Success
    
    Success -->|"Yes"| RecordSuccess
    Success -->|"No"| RecordFailure
    
    RecordSuccess --> CalcSize
    RecordFailure --> CalcSize
    
    CalcSize --> CalcDuration
    CalcDuration --> LogEvent
```

**Sources:** [packages/app/src/server/gradio-endpoint-connector.ts:373-378](), [packages/app/src/server/gradio-endpoint-connector.ts:430-433](), [packages/app/src/server/gradio-endpoint-connector.ts:517-518]()

### Event Logging

All tool executions are logged via `logGradioEvent` with the following data:

| Field | Description |
|-------|-------------|
| `spaceName` | Name of the Gradio space |
| `sessionId` | Client session identifier |
| `durationMs` | Execution duration in milliseconds |
| `isAuthenticated` | Whether request had HF token |
| `clientName` | Client application name (e.g., "Claude") |
| `clientVersion` | Client version string |
| `success` | Whether execution succeeded |
| `error` | Error message (if failed) |
| `responseSizeBytes` | Estimated response payload size |
| `notificationCount` | Number of progress notifications sent |

This logging supports analytics, debugging, and monitoring of Gradio tool usage.

**Sources:** [packages/app/src/server/gradio-endpoint-connector.ts:524-537]()

## Error Handling

The handler implements comprehensive error handling at multiple levels:

### Error Message Extraction

When a tool returns `isError: true`, the handler extracts a meaningful error message by traversing the content array:

```mermaid
graph TB
    ErrorResult["result.isError === true"]
    
    GetFirst["Get first content item"]
    
    CheckString{"Is string?"}
    UseString["Use string directly"]
    
    CheckObject{"Is object?"}
    CheckText{"Has .text?"}
    CheckMessage{"Has .message?"}
    CheckError{"Has .error?"}
    Stringify["JSON.stringify()"]
    
    FallbackString["String() conversion"]
    
    ErrorMessage["Error message extracted"]
    
    ErrorResult --> GetFirst
    GetFirst --> CheckString
    
    CheckString -->|"Yes"| UseString
    CheckString -->|"No"| CheckObject
    
    CheckObject -->|"Yes"| CheckText
    CheckObject -->|"No"| FallbackString
    
    CheckText -->|"Yes"| UseString
    CheckText -->|"No"| CheckMessage
    
    CheckMessage -->|"Yes"| UseString
    CheckMessage -->|"No"| CheckError
    
    CheckError -->|"Yes"| UseString
    CheckError -->|"No"| Stringify
    
    UseString --> ErrorMessage
    Stringify --> ErrorMessage
    FallbackString --> ErrorMessage
```

**Sources:** [packages/app/src/server/gradio-endpoint-connector.ts:396-424]()

### Exception Handling

All exceptions during execution are caught and processed:

1. Convert to `Error` object if not already
2. Log with full error details
3. Record failure in metrics
4. Set error message for event logging
5. Re-throw for upstream handling

This ensures that even unexpected failures are properly tracked and reported.

**Sources:** [packages/app/src/server/gradio-endpoint-connector.ts:500-523]()

## Configuration Sources

The post-processing behavior is configured from multiple sources, resolved via the proxy factory:

```mermaid
graph TB
    subgraph "Configuration Sources"
        Header["x-mcp-no-image-content header"]
        Settings["User settings (GRADIO_IMAGE_FILTER)"]
        ClientInfo["sessionInfo.clientInfo.name"]
        Version["package.json version"]
    end
    
    subgraph "Proxy Factory"
        ExtractHeader["Extract noImageFromHeader"]
        ExtractSettings["Extract noImageFromSettings"]
        CheckClient["Check if openai-mcp"]
        BuildWidget["Build gradioWidgetUri"]
    end
    
    subgraph "Registration Options"
        StripImage["stripImageContent"]
        WidgetUri["gradioWidgetUri"]
    end
    
    Handler["createToolHandler with options"]
    
    Header --> ExtractHeader
    Settings --> ExtractSettings
    
    ExtractHeader --> StripImage
    ExtractSettings --> StripImage
    
    ClientInfo --> CheckClient
    Version --> BuildWidget
    CheckClient --> BuildWidget
    BuildWidget --> WidgetUri
    
    StripImage --> Handler
    WidgetUri --> Handler
```

**Sources:** [packages/app/src/server/mcp-proxy.ts:109-110](), [packages/app/src/server/mcp-proxy.ts:129-130](), [packages/app/src/server/mcp-proxy.ts:101-105](), [packages/app/src/server/mcp-proxy.ts:204-207]()

---

# Page: Transport Layer

# Transport Layer

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.dockerignore](.dockerignore)
- [Dockerfile](Dockerfile)
- [README.md](README.md)
- [packages/app/src/server/transport/base-transport.ts](packages/app/src/server/transport/base-transport.ts)
- [packages/app/src/server/transport/sse-transport.ts](packages/app/src/server/transport/sse-transport.ts)
- [packages/app/src/server/transport/stateless-http-transport.ts](packages/app/src/server/transport/stateless-http-transport.ts)
- [packages/app/src/server/transport/streamable-http-transport.ts](packages/app/src/server/transport/streamable-http-transport.ts)
- [packages/app/vite.config.ts](packages/app/vite.config.ts)
- [packages/mcp/src/duplicate-space.ts](packages/mcp/src/duplicate-space.ts)
- [packages/mcp/src/error-messages.ts](packages/mcp/src/error-messages.ts)
- [start.sh](start.sh)

</details>



The Transport Layer provides multiple mechanisms for MCP clients to connect to and communicate with the server. It abstracts the low-level communication protocols (STDIO, Server-Sent Events, HTTP) while providing consistent session management, authentication, metrics tracking, and error handling.

This page covers the transport implementations, session management, and request handling. For information about the MCP Server instances created by these transports, see [MCP Server Core](#3.3). For client integration instructions, see [Client Integration](#2.2).

---

## Transport Architecture

The transport layer is organized into a class hierarchy with shared functionality in base classes and protocol-specific implementations in concrete classes. All transports use a `ServerFactory` to create MCP server instances either per-session (stateful) or per-request (stateless).

### Class Hierarchy

```mermaid
classDiagram
    class BaseTransport {
        <<abstract>>
        #serverFactory: ServerFactory
        #app: Express
        #metrics: MetricsCounter
        +initialize(options)* Promise~void~
        +cleanup()* Promise~void~
        +getActiveConnectionCount()* number
        +getSessions() SessionMetadata[]
        +getMetrics() TransportMetrics
        #validateAuthAndTrackMetrics() Promise
        #trackRequest()
        #trackError()
        #trackMethodCall()
        #extractMethodForTracking() string
    }
    
    class StatefulTransport {
        <<abstract>>
        #sessions: Map~string, Session~
        #isShuttingDown: boolean
        #staleCheckInterval: Timeout
        #pingInterval: Timeout
        #STALE_CHECK_INTERVAL: number
        #STALE_TIMEOUT: number
        #HEARTBEAT_INTERVAL: number
        #PING_ENABLED: boolean
        #updateSessionActivity()
        #createClientInfoCapture()
        #pingSingleSession()
        #startStaleConnectionCheck()
        #startPingKeepAlive()
        #removeStaleSession()* Promise~void~
        #cleanupSession()
        #cleanupAllSessions()
    }
    
    class SseTransport {
        -handleSseConnection()
        -handleSseMessage()
        -connectWithCleanup()
        +closeConnection()
    }
    
    class StreamableHttpTransport {
        -setupRoutes()
        -handleRequest()
        -handlePostRequest()
        -handleGetRequest()
        -handleDeleteRequest()
        -createSession()
        -removeSession()
    }
    
    class StatelessHttpTransport {
        -analyticsMode: boolean
        -analyticsSessions: Map
        -handleJsonRpcRequest()
        -handleDeleteRequest()
        -shouldHandle()
        -createAnalyticsSession()
        +activateTempLogging()
    }
    
    BaseTransport <|-- StatefulTransport
    StatefulTransport <|-- SseTransport
    StatefulTransport <|-- StreamableHttpTransport
    BaseTransport <|-- StatelessHttpTransport
```

**Sources:** [packages/app/src/server/transport/base-transport.ts:83-346](), [packages/app/src/server/transport/base-transport.ts:348-806](), [packages/app/src/server/transport/sse-transport.ts:14](), [packages/app/src/server/transport/streamable-http-transport.ts:18](), [packages/app/src/server/transport/stateless-http-transport.ts:39]()

### Transport Selection by Client Type

Different clients use different transport mechanisms based on their execution environment and capabilities:

| Transport | Endpoints | Client Types | Session Model | Use Case |
|-----------|-----------|--------------|---------------|----------|
| **STDIO** | stdin/stdout | CLI tools (Claude Code, Gemini CLI) | Single long-lived | Local development, command-line tools |
| **SSE** | `GET /sse`, `POST /message` | Legacy web clients | Stateful sessions | Real-time updates, older implementations |
| **StreamableHTTP** | `POST /GET /DELETE /mcp` | Modern web clients (Claude Desktop, VSCode, Cursor) | Stateful sessions | Modern web-based clients |
| **StatelessHTTP** | `POST /mcp` | Serverless/analytics | Stateless (optional analytics tracking) | Serverless deployments, high-scale scenarios |

**Sources:** [README.md:126-131](), [README.md:217-223](), [start.sh:34-58]()

---

## Base Transport Classes

### BaseTransport

`BaseTransport` provides functionality shared by all transports: metrics tracking, authentication validation, and method call extraction.

#### Core Interfaces

```mermaid
graph TB
    subgraph "ServerFactory Interface"
        SF["ServerFactory<br/>(headers, settings?, skipGradio?, sessionInfo?)"]
        SF --> SFR["ServerFactoryResult<br/>{server, userDetails}"]
    end
    
    subgraph "Session Metadata"
        SM["SessionMetadata"]
        SM --> SM1["id, connectedAt, lastActivity"]
        SM --> SM2["requestCount, isAuthenticated"]
        SM --> SM3["clientInfo: {name, version}"]
        SM --> SM4["capabilities: {sampling, roots}"]
    end
    
    subgraph "BaseSession"
        BS["BaseSession&lt;T&gt;"]
        BS --> BS1["transport: T"]
        BS --> BS2["server: McpServer"]
        BS --> BS3["metadata: SessionMetadata"]
        BS --> BS4["heartbeatInterval?: Timeout"]
    end
```

**Sources:** [packages/app/src/server/transport/base-transport.ts:13-35](), [packages/app/src/server/transport/base-transport.ts:42-61](), [packages/app/src/server/transport/base-transport.ts:63-73]()

#### Key Methods

The `BaseTransport` class provides several protected methods for common transport operations:

**Authentication and Metrics**

- `validateAuthAndTrackMetrics(headers)` - Validates HF token using `whoAmI` API call, tracks authenticated/anonymous/unauthorized connection metrics [packages/app/src/server/transport/base-transport.ts:305-345]()

**Request Tracking**

- `extractMethodForTracking(requestBody)` - Extracts method name from JSON-RPC request, handles special cases for `tools/call:toolName` and `prompts/get:promptName` patterns [packages/app/src/server/transport/base-transport.ts:192-223]()
- `trackMethodCall(methodName, startTime, isError, clientInfo)` - Records method call duration and success/failure status [packages/app/src/server/transport/base-transport.ts:272-280]()

**Gradio Tool Detection**

- `isGradioToolCall(requestBody)` - Checks if a `tools/call` request targets a Gradio tool [packages/app/src/server/transport/base-transport.ts:234-247]()
- `skipGradioSetup(requestBody)` - Determines whether to skip Gradio endpoint discovery for initialization or non-Gradio requests [packages/app/src/server/transport/base-transport.ts:249-267]()

**Sources:** [packages/app/src/server/transport/base-transport.ts:83-346]()

### StatefulTransport

`StatefulTransport` extends `BaseTransport` to add session management, stale connection detection, and ping keep-alive functionality for transports that maintain persistent connections.

#### Session Management Features

```mermaid
graph LR
    subgraph "Session Lifecycle"
        SC["Session Created"] --> SA["Session Active"]
        SA --> |"No activity > STALE_TIMEOUT"| SS["Session Stale"]
        SA --> |"Ping failures > threshold"| SD["Session Distressed"]
        SS --> SR["Session Removed"]
        SD --> SR
        SA --> |"Client disconnect"| SR
        SA --> |"DELETE request"| SR
    end
    
    subgraph "Background Processes"
        PC["Ping Cycle<br/>(PING_INTERVAL: 30s)"]
        PC --> |"pingSingleSession()"| PA["Update lastActivity"]
        PC --> |"Failure"| PF["Increment pingFailures"]
        
        SCC["Stale Check Cycle<br/>(STALE_CHECK_INTERVAL: 90s)"]
        SCC --> |"lastActivity > STALE_TIMEOUT"| RSS["removeStaleSession()"]
    end
```

**Configuration Environment Variables:**

| Variable | Default | Description |
|----------|---------|-------------|
| `MCP_CLIENT_HEARTBEAT_INTERVAL` | 30000ms | How often to check SSE connection health |
| `MCP_CLIENT_CONNECTION_CHECK` | 90000ms | How often to check for stale sessions |
| `MCP_CLIENT_CONNECTION_TIMEOUT` | 600000ms | Remove sessions inactive for this duration (10 min) |
| `MCP_PING_ENABLED` | true | Enable ping keep-alive for sessions |
| `MCP_PING_INTERVAL` | 30000ms | Interval between ping cycles |
| `MCP_PING_FAILURE_THRESHOLD` | 1 | Number of consecutive ping failures before marking session distressed |

**Sources:** [packages/app/src/server/transport/base-transport.ts:359-366](), [README.md:224-235]()

#### Session Management Methods

**Activity Tracking**
- `updateSessionActivity(sessionId)` - Updates `lastActivity` timestamp and client activity metrics [packages/app/src/server/transport/base-transport.ts:370-377]()

**Ping Keep-Alive**
- `pingSingleSession(sessionId)` - Sends fire-and-forget ping, updates activity on success or increments failure count [packages/app/src/server/transport/base-transport.ts:429-467]()
- `startPingKeepAlive()` / `stopPingKeepAlive()` - Manages periodic ping cycle [packages/app/src/server/transport/base-transport.ts:472-501]()

**Stale Detection**
- `startStaleConnectionCheck()` - Starts interval that removes sessions inactive beyond `STALE_TIMEOUT` [packages/app/src/server/transport/base-transport.ts:506-533]()
- `isSessionDistressed(session)` - Checks if ping failures exceed threshold [packages/app/src/server/transport/base-transport.ts:382-384]()

**Cleanup**
- `cleanupSession(sessionId)` - Stops heartbeat, closes transport/server, removes from map [packages/app/src/server/transport/base-transport.ts:685-724]()
- `cleanupAllSessions()` - Cleans up all sessions in parallel [packages/app/src/server/transport/base-transport.ts:729-740]()

**Sources:** [packages/app/src/server/transport/base-transport.ts:348-806]()

---

## STDIO Transport

The STDIO transport uses standard input/output streams for communication with CLI-based clients. It creates a single long-lived server instance and does not use HTTP endpoints.

### Characteristics

- **Protocol:** Standard input/output pipes
- **Server Instance:** Single server created at startup
- **Authentication:** Uses `HF_TOKEN` or `DEFAULT_HF_TOKEN` environment variable
- **Session Model:** Single session for the process lifetime
- **HTTP Server:** Not started (no web dashboard)

### Usage

```bash
# Start in STDIO mode
npx @llmindset/hf-mcp-server

# Or with Docker
docker run -i --rm -e TRANSPORT=stdio -e DEFAULT_HF_TOKEN=hf_xxx hf-mcp-server
```

### Implementation Notes

The STDIO transport is implemented in the `stdio.js` entry point and does not use the `BaseTransport` class hierarchy since it operates outside the HTTP request/response model.

**Sources:** [README.md:144](), [start.sh:35-37](), [README.md:210-213]()

---

## SSE Transport

The SSE (Server-Sent Events) transport provides real-time bidirectional communication using an SSE connection for server-to-client messages and HTTP POST for client-to-server messages.

### Endpoints

- `GET /sse` - Establishes SSE connection, accepts optional `?sessionId=` query parameter for reconnection
- `POST /message?sessionId=<id>` - Sends messages from client to server

### Request Flow

```mermaid
sequenceDiagram
    participant Client
    participant SseTransport
    participant ServerFactory
    participant McpServer
    participant SSEServerTransport
    
    Note over Client,SSEServerTransport: Connection Establishment
    Client->>SseTransport: GET /sse
    SseTransport->>SseTransport: validateAuthAndTrackMetrics(headers)
    SseTransport->>ServerFactory: serverFactory(headers)
    ServerFactory-->>SseTransport: {server, userDetails}
    SseTransport->>SSEServerTransport: new SSEServerTransport("/message", res)
    SseTransport->>SseTransport: sessions.set(sessionId, connection)
    SseTransport->>SseTransport: startHeartbeat(sessionId, res)
    SseTransport->>McpServer: server.connect(transport)
    McpServer-->>Client: SSE connection established
    
    Note over Client,SSEServerTransport: Message Exchange
    Client->>SseTransport: POST /message?sessionId=<id>
    SseTransport->>SseTransport: updateSessionActivity(sessionId)
    SseTransport->>SSEServerTransport: transport.handlePostMessage(req, res, body)
    SSEServerTransport->>McpServer: Route to tool/prompt handler
    McpServer-->>SSEServerTransport: Response
    SSEServerTransport-->>Client: HTTP 200 + SSE events
    
    Note over Client,SSEServerTransport: Cleanup
    Client->>Client: Connection close
    SseTransport->>SseTransport: cleanupSession(sessionId)
    SseTransport->>SSEServerTransport: transport.close()
    SseTransport->>McpServer: server.close()
```

**Sources:** [packages/app/src/server/transport/sse-transport.ts:44-152](), [packages/app/src/server/transport/sse-transport.ts:154-208]()

### Key Implementation Details

**Session Creation** [packages/app/src/server/transport/sse-transport.ts:44-152]()
1. Validates authentication via `validateAuthAndTrackMetrics()`
2. Creates new `SSEServerTransport` instance with `/message` endpoint
3. Calls `serverFactory()` to create MCP server instance
4. Stores connection in `sessions` Map with metadata
5. Starts heartbeat monitoring and SSE event handlers
6. Connects server to transport with cleanup error handling

**Reconnection Handling** [packages/app/src/server/transport/sse-transport.ts:54-75]()
- If client provides `?sessionId=`, checks if session exists
- Cleans up old session before creating new one (no session resumption)
- Tracks failed resumption metric if session not found

**Message Handling** [packages/app/src/server/transport/sse-transport.ts:154-208]()
- Requires `sessionId` query parameter
- Updates session activity timestamp
- Increments request count for method calls (not responses/pings)
- Delegates to `transport.handlePostMessage()`

**Sources:** [packages/app/src/server/transport/sse-transport.ts]()

---

## StreamableHTTP Transport

The StreamableHTTP transport implements a modern stateful HTTP protocol where all communication (initialization, method calls, SSE streaming, and termination) happens on a single endpoint using different HTTP methods.

### Endpoints

- `POST /mcp` - Initialize session or send messages
- `GET /mcp` - Establish SSE stream for existing session
- `DELETE /mcp` - Terminate session

All requests include `Mcp-Session-Id` header (except initial POST for initialization).

### Request Flow

```mermaid
sequenceDiagram
    participant Client
    participant StreamableHttpTransport as StreamableHTTP
    participant ServerFactory
    participant McpServer
    participant StreamableHTTPServerTransport
    
    Note over Client,StreamableHTTPServerTransport: Initialization
    Client->>StreamableHttpTransport: POST /mcp (initialize request)
    StreamableHttpTransport->>StreamableHttpTransport: isInitializeRequest(body)?
    StreamableHttpTransport->>StreamableHttpTransport: validateAuthAndTrackMetrics(headers)
    StreamableHttpTransport->>StreamableHttpTransport: createSession(headers)
    StreamableHttpTransport->>ServerFactory: serverFactory(headers)
    ServerFactory-->>StreamableHttpTransport: {server, userDetails}
    StreamableHttpTransport->>StreamableHTTPServerTransport: new StreamableHTTPServerTransport<br/>{sessionIdGenerator: randomUUID}
    StreamableHTTPServerTransport-->>StreamableHttpTransport: onsessioninitialized(sessionId)
    StreamableHttpTransport->>StreamableHttpTransport: sessions.set(sessionId, session)
    StreamableHttpTransport->>McpServer: server.connect(transport)
    StreamableHTTPServerTransport->>Client: Response with Mcp-Session-Id header
    
    Note over Client,StreamableHTTPServerTransport: Subsequent Requests
    Client->>StreamableHttpTransport: POST /mcp<br/>Mcp-Session-Id: <id>
    StreamableHttpTransport->>StreamableHttpTransport: sessions.has(sessionId)?
    StreamableHttpTransport->>StreamableHttpTransport: updateSessionActivity(sessionId)
    StreamableHttpTransport->>StreamableHTTPServerTransport: transport.handleRequest(req, res, body)
    StreamableHTTPServerTransport-->>Client: Response
    
    Note over Client,StreamableHTTPServerTransport: SSE Stream
    Client->>StreamableHttpTransport: GET /mcp<br/>Mcp-Session-Id: <id>
    StreamableHttpTransport->>StreamableHttpTransport: startHeartbeat(sessionId, res)
    StreamableHttpTransport->>StreamableHttpTransport: setupSseEventHandlers(sessionId, res)
    StreamableHttpTransport->>StreamableHTTPServerTransport: transport.handleRequest(req, res)
    StreamableHTTPServerTransport-->>Client: SSE events
    
    Note over Client,StreamableHTTPServerTransport: Termination
    Client->>StreamableHttpTransport: DELETE /mcp<br/>Mcp-Session-Id: <id>
    StreamableHttpTransport->>StreamableHttpTransport: removeSession(sessionId)
    StreamableHttpTransport->>StreamableHTTPServerTransport: transport.handleRequest(req, res, body)
    StreamableHttpTransport->>StreamableHttpTransport: cleanupSession(sessionId)
```

**Sources:** [packages/app/src/server/transport/streamable-http-transport.ts:63-221]()

### Session Lifecycle

**Creation** [packages/app/src/server/transport/streamable-http-transport.ts:223-288]()
- Only accepts `initialize` requests without session ID
- Creates `StreamableHTTPServerTransport` with `sessionIdGenerator: randomUUID`
- Uses `onsessioninitialized` callback to store session in map
- Sets up `onclose` handler and error tracking
- Configures client info capture via `oninitialized` hook

**Validation** [packages/app/src/server/transport/streamable-http-transport.ts:92-169]()
- Rejects new connections during shutdown (503)
- Non-initialization requests require valid `mcp-session-id` header
- Returns 404 if session not found
- Updates activity timestamp for all valid requests

**Termination** [packages/app/src/server/transport/streamable-http-transport.ts:203-221]()
- Accepts DELETE requests with session ID
- Calls `transport.handleRequest()` for graceful shutdown
- Removes session via `removeSession()` which calls `cleanupSession()`

**Sources:** [packages/app/src/server/transport/streamable-http-transport.ts]()

---

## Stateless HTTP Transport

The StatelessHTTP transport creates a new server and transport instance for each request, ensuring complete isolation between requests. It operates in pure stateless mode or optional analytics mode where session tracking is maintained for metrics without affecting request isolation.

### Characteristics

- **Server Instance:** New server created per request (or per request type)
- **Transport Instance:** New transport created per request  
- **Session Persistence:** None (optional analytics tracking only)
- **Cleanup:** Automatic after response completion
- **Scalability:** Suitable for serverless/high-scale deployments

### Endpoint

- `POST /mcp` - JSON-RPC requests
- `GET /mcp` - Serves MCP welcome page (or 405 if `MCP_STRICT_COMPLIANCE=true`)
- `DELETE /mcp` - Deletes analytics session (only in analytics mode)

### Request Flow

```mermaid
sequenceDiagram
    participant Client
    participant StatelessHttpTransport
    participant ServerFactory
    participant McpServer
    participant StreamableHTTPServerTransport
    
    Note over Client,StreamableHTTPServerTransport: Per-Request Lifecycle
    Client->>StatelessHttpTransport: POST /mcp (JSON-RPC request)
    StatelessHttpTransport->>StatelessHttpTransport: validateAuthAndTrackMetrics(headers)
    StatelessHttpTransport->>StatelessHttpTransport: shouldHandle(requestBody)?
    
    alt Full Server Needed
        StatelessHttpTransport->>ServerFactory: serverFactory(headers, skipGradio)
        ServerFactory-->>StatelessHttpTransport: {server, userDetails}
        StatelessHttpTransport->>StreamableHTTPServerTransport: new StreamableHTTPServerTransport<br/>{enableJsonResponse: !isGradioToolCall}
    else Stub Server
        StatelessHttpTransport->>McpServer: new McpServer("@huggingface/internal-responder")
        StatelessHttpTransport->>StreamableHTTPServerTransport: new StreamableHTTPServerTransport<br/>{enableJsonResponse: true}
    end
    
    StatelessHttpTransport->>McpServer: server.connect(transport)
    StatelessHttpTransport->>StreamableHTTPServerTransport: transport.handleRequest(req, res, body)
    StreamableHTTPServerTransport-->>Client: Response
    
    Note over Client,StreamableHTTPServerTransport: Cleanup
    StatelessHttpTransport->>StreamableHTTPServerTransport: transport.close()
    StatelessHttpTransport->>McpServer: server.close()
```

**Sources:** [packages/app/src/server/transport/stateless-http-transport.ts:141-408]()

### Request Optimization

The transport uses `shouldHandle()` to determine whether to create a full server instance or a minimal stub responder:

**Methods Requiring Full Server** [packages/app/src/server/transport/stateless-http-transport.ts:64-89]()
- `tools/list`
- `tools/call`
- `prompts/list`
- `prompts/get`
- `initialize`
- `resources/*` (only for `openai-mcp` client)

**Stub Responder** [packages/app/src/server/transport/stateless-http-transport.ts:313-315]()
- All other methods use minimal `McpServer` instance without tools/prompts
- Handles protocol-level methods like `ping`, `notifications`, etc.

### Analytics Mode

When `ANALYTICS_MODE=true`, the transport maintains a session map for analytics without affecting statelessness:

**Session Management** [packages/app/src/server/transport/stateless-http-transport.ts:165-244]()
- `initialize` request generates new session ID, returns it in `Mcp-Session-Id` header
- Subsequent requests must include `Mcp-Session-Id` header
- Session stores metadata but no server/transport instances
- `DELETE /mcp` removes analytics session
- Failed session resumption returns 404

**Temporary Logging** [packages/app/src/server/transport/stateless-http-transport.ts:535-554]()
- `activateTempLogging(count)` enables detailed logging for session resume failures
- Controlled by `TEMPLOG_MAX` environment variable
- Logs session ID, headers (with redacted token), client info
- Auto-disables after count is reached

**Sources:** [packages/app/src/server/transport/stateless-http-transport.ts:39-555]()

---

## Authentication and Authorization

All transports validate authentication using the `validateAuthAndTrackMetrics()` method inherited from `BaseTransport`.

### Authentication Flow

```mermaid
graph TD
    A["Request with Headers"] --> B["extractAuthBouquetAndMix()"]
    B --> C{"HF Token Present?"}
    
    C -->|Yes| D["whoAmI API Call"]
    C -->|No| E{"x-mcp-force-auth<br/>Header Present?"}
    
    D --> F{"Validation Result"}
    F -->|"401 Error"| G["Track Unauthorized<br/>Return 401"]
    F -->|"Other Error"| H["Continue Without<br/>Auth Tracking"]
    F -->|"Success"| I["Track Authenticated<br/>Continue"]
    
    E -->|Yes| G
    E -->|No| J["Track Anonymous<br/>Continue"]
    
    I --> K["shouldContinue: true<br/>userIdentified: true"]
    J --> K2["shouldContinue: true<br/>userIdentified: false"]
    G --> L["shouldContinue: false<br/>statusCode: 401"]
    H --> K2
```

**Sources:** [packages/app/src/server/transport/base-transport.ts:305-345]()

### Token Sources

The authentication flow extracts tokens from multiple header sources via `extractAuthBouquetAndMix()`:

1. `Authorization: Bearer <token>` (standard)
2. `hf-token: <token>` (custom header)
3. `x-hf-token: <token>` (alternative custom header)
4. Query parameters converted to headers (via `extractQueryParamsToHeaders()`)

For STDIO transport, if no token is provided in headers, `DEFAULT_HF_TOKEN` or `HF_TOKEN` environment variables are used.

**Sources:** [packages/app/src/server/utils/auth-utils.ts](), [start.sh:12-15]()

### OAuth Challenge Response

When authentication fails (401), transports set the `WWW-Authenticate` header with an OAuth resource challenge:

```typescript
res.set('WWW-Authenticate', buildOAuthResourceHeader(req));
res.status(401).send('Unauthorized');
```

This allows compatible clients to initiate OAuth flows for authentication.

**Sources:** [packages/app/src/server/transport/stateless-http-transport.ts:159-161](), [packages/app/src/server/transport/streamable-http-transport.ts:134-136]()

---

## Metrics and Monitoring

All transports track detailed metrics through the `MetricsCounter` class, providing visibility into connection health, request performance, and error patterns.

### Metrics Categories

```mermaid
graph TB
    subgraph "Connection Metrics"
        CM1["totalConnections<br/>(lifetime counter)"]
        CM2["activeConnections<br/>(current count)"]
        CM3["authenticatedConnections"]
        CM4["anonymousConnections"]
        CM5["unauthorizedConnections"]
    end
    
    subgraph "Session Metrics"
        SM1["sessionsCreated"]
        SM2["sessionsDeleted"]
        SM3["sessionsCleaned"]
        SM4["sessionResumeFailed"]
    end
    
    subgraph "Request Metrics"
        RM1["totalRequests"]
        RM2["errorsByStatus: Map&lt;number&gt;"]
        RM3["methodStats: Map&lt;methodName&gt;"]
    end
    
    subgraph "Ping Metrics"
        PM1["pingsSent"]
        PM2["pingsSucceeded"]
        PM3["pingsFailed"]
    end
    
    subgraph "Method Stats"
        MS1["totalCalls"]
        MS2["successfulCalls"]
        MS3["failedCalls"]
        MS4["avgDurationMs"]
        MS5["minDurationMs"]
        MS6["maxDurationMs"]
    end
    
    RM3 --> MS1
    RM3 --> MS2
    RM3 --> MS3
    RM3 --> MS4
    RM3 --> MS5
    RM3 --> MS6
```

**Sources:** [packages/app/src/shared/transport-metrics.ts]()

### Method Tracking

Method calls are tracked with granular detail including tool names and prompt names:

**Method Name Extraction** [packages/app/src/server/transport/base-transport.ts:192-223]()
- `tools/call` → `tools/call:toolName` (e.g., `tools/call:model_search`, `tools/call:gr_image_gen`)
- `prompts/get` → `prompts/get:promptName` (e.g., `prompts/get:user_summary`)
- Other methods → method name only (e.g., `initialize`, `tools/list`)
- JSON-RPC responses (have `id` but no `method`) → not tracked

**Timing** [packages/app/src/server/transport/base-transport.ts:272-280]()
- **Stateless mode:** Measures full request-to-response time including server creation
- **Stateful mode:** Tracks HTTP dispatch time without timing (duration set to `undefined`)

**Per-Client Tracking**
When client info is available, metrics are also tracked per `clientInfo.name` for client-specific analysis.

**Sources:** [packages/app/src/shared/transport-metrics.ts](), [packages/app/src/server/transport/base-transport.ts:192-223]()

### Accessing Metrics

Metrics are exposed via the web dashboard and API endpoints:

- `GET /api/transport` - Transport type and basic configuration
- `GET /api/transport-metrics` - Detailed metrics with 3-second polling
- `GET /api/sessions` - Active session list with metadata

The web dashboard displays:
- **TransportMetricsCard** - Connection counts, error distribution, client breakdown
- **McpMethodsCard** - Per-method performance statistics, call counts, avg/min/max duration
- **StdioTransportMetrics** - Session details table for STDIO/SSE/StreamableHTTP

**Sources:** [packages/app/src/web/components/monitoring/TransportMetricsCard.tsx](), [packages/app/src/web/components/monitoring/McpMethodsCard.tsx](), [packages/app/src/web/components/monitoring/StdioTransportMetrics.tsx]()

---

## Configuration

### Transport Selection

The transport type is selected via the `TRANSPORT` environment variable:

```bash
# STDIO (default for npx)
TRANSPORT=stdio node dist/server/stdio.js

# SSE (legacy)
TRANSPORT=sse node dist/server/sse.js

# StreamableHTTP (stateful)
TRANSPORT=streamableHttp node dist/server/streamableHttp.js

# StreamableHTTPJson (stateless)
TRANSPORT=streamableHttpJson node dist/server/streamableHttp.js --json
```

**Sources:** [start.sh:4-58](), [README.md:238-246]()

### Environment Variables

#### Common Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `TRANSPORT` | `stdio` | Transport type: `stdio`, `sse`, `streamableHttp`, `streamableHttpJson` |
| `PORT` | 3000 | HTTP server port (not used for STDIO) |
| `DEFAULT_HF_TOKEN` | - | ⚠️ Default token if no Authorization header provided (dev/test only) |
| `HF_TOKEN` | - | For STDIO mode, used as `DEFAULT_HF_TOKEN` if not set |
| `HF_API_TIMEOUT` | 12500 | Timeout for HF API requests in milliseconds |
| `MCP_STRICT_COMPLIANCE` | false | Return 405 for GET /mcp in stateless mode (vs. serving welcome page) |

**Sources:** [README.md:238-246](), [start.sh:4-27]()

#### Stateful Transport Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `MCP_CLIENT_HEARTBEAT_INTERVAL` | 30000 | How often to check SSE connection health (ms) |
| `MCP_CLIENT_CONNECTION_CHECK` | 90000 | How often to check for stale sessions (ms) |
| `MCP_CLIENT_CONNECTION_TIMEOUT` | 600000 | Remove sessions inactive for this duration (ms, 10 min) |
| `MCP_PING_ENABLED` | true | Enable ping keep-alive for sessions |
| `MCP_PING_INTERVAL` | 30000 | Interval between ping cycles (ms) |
| `MCP_PING_FAILURE_THRESHOLD` | 1 | Consecutive ping failures before marking session distressed |

**Sources:** [README.md:224-235](), [packages/app/src/server/transport/base-transport.ts:359-366]()

#### Stateless Transport Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `ANALYTICS_MODE` | false | Enable session tracking in stateless mode for analytics |
| `TEMPLOG_MAX` | 0 | Maximum number of session resume failures to log with full detail |

**Sources:** [packages/app/src/server/transport/stateless-http-transport.ts:48-58]()

### Docker Configuration

The Docker container defaults to `streamableHttpJson` mode and requires explicit transport override:

```bash
# Default (stateless JSON)
docker run --rm -p 3000:3000 ghcr.io/evalstate/hf-mcp-server:latest

# STDIO mode
docker run -i --rm -e TRANSPORT=stdio -e DEFAULT_HF_TOKEN=hf_xxx hf-mcp-server

# SSE mode
docker run --rm -p 3000:3000 -e TRANSPORT=sse hf-mcp-server

# StreamableHTTP mode (stateful)
docker run --rm -p 3000:3000 -e TRANSPORT=streamableHttp hf-mcp-server
```

**Sources:** [Dockerfile:58-60](), [README.md:199-216]()

---

## Transport Comparison Table

| Feature | STDIO | SSE | StreamableHTTP | StatelessHTTP |
|---------|-------|-----|----------------|---------------|
| **HTTP Endpoints** | None | `/sse`, `/message` | `/mcp` (all methods) | `/mcp` (POST only) |
| **Session Model** | Single process | Stateful | Stateful | Stateless (optional analytics) |
| **Server Instances** | 1 per process | 1 per session | 1 per session | 1 per request |
| **Stale Detection** | N/A | Yes | Yes | N/A |
| **Ping Keep-Alive** | N/A | Yes | Yes | N/A |
| **Dashboard** | No | Yes | Yes | Yes |
| **Reconnection** | N/A | Cleanup + new | Session resumption | Session resumption (analytics mode) |
| **Shutdown Behavior** | Process exit | Reject new, cleanup existing | Reject new, cleanup existing | Accept all (no state) |
| **Best For** | CLI tools | Legacy clients | Modern web clients | Serverless, high-scale |
| **Streaming Support** | Yes (native) | Yes (SSE) | Yes (SSE) | Yes (SSE, per-request) |

**Sources:** [README.md:126-131](), All transport implementation files

---

# Page: Base Transport Classes

# Base Transport Classes

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [packages/app/src/server/transport/base-transport.ts](packages/app/src/server/transport/base-transport.ts)
- [packages/app/src/server/transport/sse-transport.ts](packages/app/src/server/transport/sse-transport.ts)
- [packages/app/src/server/transport/stateless-http-transport.ts](packages/app/src/server/transport/stateless-http-transport.ts)
- [packages/app/src/server/transport/streamable-http-transport.ts](packages/app/src/server/transport/streamable-http-transport.ts)

</details>



## Purpose and Scope

This document describes the abstract base classes that provide common functionality for all transport implementations in the HF MCP Server. The `BaseTransport` and `StatefulTransport` classes define the core architecture for handling client connections, managing sessions, tracking metrics, and coordinating with the MCP server factory.

For information about specific transport implementations, see:
- [STDIO Transport](#7.2) - command-line integration
- [SSE Transport](#7.3) - Server-Sent Events transport
- [HTTP Transports](#7.4) - stateful and stateless HTTP implementations

For the overall transport layer architecture, see [Transport Layer Architecture](#3.4).

---

## Architecture Overview

The transport layer uses a two-tier inheritance hierarchy to share functionality while allowing customization:

**Class Hierarchy Diagram**

```mermaid
graph TB
    BaseTransport["BaseTransport<br/>(abstract class)"]
    StatefulTransport["StatefulTransport&lt;TSession&gt;<br/>(abstract class)"]
    STDIOTransport["STDIOTransport"]
    SseTransport["SseTransport"]
    StreamableHttpTransport["StreamableHttpTransport"]
    StatelessHttpTransport["StatelessHttpTransport"]
    
    BaseTransport --> StatefulTransport
    BaseTransport --> StatelessHttpTransport
    StatefulTransport --> STDIOTransport
    StatefulTransport --> SseTransport
    StatefulTransport --> StreamableHttpTransport
    
    BaseTransport:::abstract
    StatefulTransport:::abstract
    STDIOTransport:::concrete
    SseTransport:::concrete
    StreamableHttpTransport:::concrete
    StatelessHttpTransport:::concrete
    
    classDef abstract stroke-width:3px,stroke-dasharray: 5 5
    classDef concrete stroke-width:2px
```

**Sources:** [packages/app/src/server/transport/base-transport.ts:82-346](), [packages/app/src/server/transport/base-transport.ts:352-806]()

---

## BaseTransport Abstract Class

The `BaseTransport` class provides core functionality shared by all transport implementations, regardless of whether they maintain session state.

### Core Responsibilities

| Responsibility | Description |
|---------------|-------------|
| **Server Factory Management** | Stores and invokes the `ServerFactory` to create MCP server instances |
| **Metrics Tracking** | Maintains `MetricsCounter` for requests, errors, connections, and method calls |
| **Authentication Validation** | Validates Hugging Face tokens and tracks authentication metrics |
| **Request Analysis** | Extracts method names, client info, and determines request types |
| **Express Integration** | Stores reference to Express app for route registration |

### Key Properties and Methods

```typescript
// Core properties (from base-transport.ts)
protected serverFactory: ServerFactory
protected app: Express
protected metrics: MetricsCounter

// Abstract methods - must be implemented by subclasses
abstract initialize(options: TransportOptions): Promise<void>
abstract cleanup(): Promise<void>
abstract getActiveConnectionCount(): number

// Optional shutdown method
shutdown?(): void
```

**Sources:** [packages/app/src/server/transport/base-transport.ts:83-108]()

### Authentication Flow

The `validateAuthAndTrackMetrics` method handles token validation and metrics tracking:

**Authentication Validation Flow**

```mermaid
sequenceDiagram
    participant Transport as "BaseTransport"
    participant Auth as "extractAuthBouquetAndMix"
    participant HF as "whoAmI (HF API)"
    participant Metrics as "MetricsCounter"
    
    Transport->>Auth: "Extract HF token from headers"
    Auth-->>Transport: "hfToken (or undefined)"
    
    alt "Token Present"
        Transport->>HF: "whoAmI({ accessToken })"
        alt "Token Valid (200 OK)"
            HF-->>Transport: "WhoAmI data"
            Transport->>Metrics: "trackAuthenticatedConnection()"
            Transport-->>Transport: "Return { shouldContinue: true, userIdentified: true }"
        else "Token Invalid (401)"
            HF-->>Transport: "401 Unauthorized"
            Transport->>Metrics: "trackUnauthorizedConnection()"
            Transport-->>Transport: "Return { shouldContinue: false, statusCode: 401 }"
        else "Other Error (500, network)"
            HF-->>Transport: "Error (non-401)"
            Transport-->>Transport: "Return { shouldContinue: true, userIdentified: false }"
        end
    else "No Token"
        Transport->>Metrics: "trackAnonymousConnection()"
        Transport->>Transport: "Check x-mcp-force-auth header"
        alt "Force Auth Enabled"
            Transport-->>Transport: "Return { shouldContinue: false }"
        else "Allow Anonymous"
            Transport-->>Transport: "Return { shouldContinue: true, userIdentified: false }"
        end
    end
```

**Sources:** [packages/app/src/server/transport/base-transport.ts:305-345]()

### Method Tracking

The `extractMethodForTracking` method converts JSON-RPC requests into trackable method names:

| Request Type | Tracking Name Format |
|-------------|---------------------|
| `tools/call` with `params.name="model_search"` | `tools/call:model_search` |
| `tools/call` with Gradio tool | `tools/call:gr1_toolname` (sanitized) |
| `prompts/get` with `params.name="user_summary"` | `prompts/get:user_summary` |
| `initialize` | `initialize` |
| JSON-RPC response (has `result` or `error` but no `method`) | `null` (not tracked) |

**Sources:** [packages/app/src/server/transport/base-transport.ts:192-223]()

### Gradio Detection

The base class provides methods to identify Gradio-related requests:

```typescript
// Check if a request is a Gradio tool call
protected isGradioToolCall(requestBody): boolean

// Determine if Gradio setup should be skipped
// Returns true for: initialize, resources/*, non-Gradio tools/call
protected skipGradioSetup(requestBody): boolean
```

**Sources:** [packages/app/src/server/transport/base-transport.ts:234-267]()

---

## StatefulTransport Abstract Class

The `StatefulTransport` class extends `BaseTransport` to provide session management capabilities for transports that maintain persistent connections.

### Session Management Architecture

**Session Lifecycle Components**

```mermaid
graph TB
    subgraph "Session Storage"
        SessionsMap["sessions: Map&lt;string, TSession&gt;"]
        SessionMetadata["SessionMetadata<br/>• id<br/>• connectedAt<br/>• lastActivity<br/>• requestCount<br/>• isAuthenticated<br/>• clientInfo<br/>• capabilities"]
    end
    
    subgraph "Monitoring Processes"
        StaleChecker["Stale Connection Checker<br/>Interval: STALE_CHECK_INTERVAL"]
        PingKeepAlive["Ping Keep-Alive<br/>Interval: PING_INTERVAL"]
        Heartbeat["Heartbeat Monitor<br/>Per-session, SSE only"]
    end
    
    subgraph "Configuration"
        EnvVars["Environment Variables<br/>• MCP_CLIENT_CONNECTION_CHECK<br/>• MCP_CLIENT_CONNECTION_TIMEOUT<br/>• MCP_CLIENT_HEARTBEAT_INTERVAL<br/>• MCP_PING_ENABLED<br/>• MCP_PING_INTERVAL<br/>• MCP_PING_FAILURE_THRESHOLD"]
    end
    
    SessionsMap --> SessionMetadata
    StaleChecker --> SessionsMap
    PingKeepAlive --> SessionsMap
    Heartbeat --> SessionsMap
    EnvVars --> StaleChecker
    EnvVars --> PingKeepAlive
    EnvVars --> Heartbeat
```

**Sources:** [packages/app/src/server/transport/base-transport.ts:352-366](), [packages/app/src/server/transport/base-transport.ts:506-533]()

### Session State Properties

```typescript
// Session management
protected sessions: Map<string, TSession>
protected isShuttingDown: boolean
protected staleCheckInterval?: NodeJS.Timeout
protected pingInterval?: NodeJS.Timeout
protected pingsInFlight: Set<string>

// Configuration from environment variables
protected readonly STALE_CHECK_INTERVAL: number    // Default: 90000ms (90s)
protected readonly STALE_TIMEOUT: number           // Default: 600000ms (10min)
protected readonly HEARTBEAT_INTERVAL: number      // Default: 30000ms (30s)
protected readonly PING_ENABLED: boolean           // Default: true
protected readonly PING_INTERVAL: number           // Default: 30000ms (30s)
protected readonly PING_FAILURE_THRESHOLD: number  // Default: 1
```

**Sources:** [packages/app/src/server/transport/base-transport.ts:353-365]()

### Stale Connection Detection

The stale checker runs periodically to identify and remove inactive sessions:

**Stale Connection Detection Flow**

```mermaid
sequenceDiagram
    participant Interval as "Stale Check Interval"
    participant StatefulTransport as "StatefulTransport"
    participant Session as "Session Map"
    participant Cleanup as "removeStaleSession"
    
    loop "Every STALE_CHECK_INTERVAL (90s)"
        Interval->>StatefulTransport: "Check for stale sessions"
        StatefulTransport->>StatefulTransport: "Skip if isShuttingDown"
        
        loop "For each session"
            StatefulTransport->>Session: "Get lastActivity timestamp"
            Session-->>StatefulTransport: "lastActivity: Date"
            StatefulTransport->>StatefulTransport: "Calculate time since activity"
            
            alt "timeSinceActivity > STALE_TIMEOUT (10min)"
                StatefulTransport->>StatefulTransport: "Add to staleSessionIds[]"
            end
        end
        
        loop "For each stale session"
            StatefulTransport->>Cleanup: "removeStaleSession(sessionId)"
            Note over Cleanup: "Implemented by concrete transport"
        end
    end
```

**Sources:** [packages/app/src/server/transport/base-transport.ts:506-533]()

### Ping Keep-Alive System

The ping system actively probes session health using MCP's `ping` method:

**Ping Keep-Alive Architecture**

```mermaid
sequenceDiagram
    participant Interval as "Ping Interval"
    participant Transport as "StatefulTransport"
    participant PingsInFlight as "pingsInFlight: Set"
    participant Server as "McpServer"
    participant Metadata as "SessionMetadata"
    
    loop "Every PING_INTERVAL (30s)"
        Interval->>Transport: "Ping all sessions"
        
        loop "For each session"
            Transport->>PingsInFlight: "Check if sessionId in set"
            
            alt "Ping already in flight"
                PingsInFlight-->>Transport: "Skip this session"
            else "No ping in flight"
                Transport->>PingsInFlight: "Add sessionId to set"
                Transport->>Metadata: "Update lastPingAttempt"
                Transport->>Server: "server.ping() [fire-and-forget]"
                
                par "Async ping result"
                    alt "Ping Success"
                        Server-->>Transport: "Promise resolves"
                        Transport->>Transport: "updateSessionActivity()"
                        Transport->>Metadata: "Reset pingFailures to 0"
                        Transport->>PingsInFlight: "Remove sessionId from set"
                    else "Ping Failure"
                        Server-->>Transport: "Promise rejects"
                        Transport->>Metadata: "Increment pingFailures"
                        Transport->>PingsInFlight: "Remove sessionId from set"
                        
                        alt "pingFailures >= PING_FAILURE_THRESHOLD"
                            Transport->>Transport: "Mark session as distressed"
                            Note over Transport: "Stale checker will remove it"
                        end
                    end
                end
            end
        end
    end
```

**Sources:** [packages/app/src/server/transport/base-transport.ts:429-467](), [packages/app/src/server/transport/base-transport.ts:472-500]()

### Client Information Capture

The `createClientInfoCapture` method creates a callback to extract client details after initialization:

```typescript
protected createClientInfoCapture(sessionId: string): () => void {
  return () => {
    const session = this.sessions.get(sessionId);
    // Extract from server.getClientVersion() and server.getClientCapabilities()
    // Update session metadata
    // Track metrics for client association
  };
}
```

This callback is typically registered as `server.server.oninitialized` to capture client info when the `initialize` method completes.

**Sources:** [packages/app/src/server/transport/base-transport.ts:389-423]()

### Session Cleanup

The base class provides standardized cleanup methods:

| Method | Purpose |
|--------|---------|
| `cleanupSession(sessionId)` | Clean up a single session: stop heartbeat, close transport, close server, remove from map |
| `cleanupAllSessions()` | Clean up all sessions in parallel during shutdown |
| `removeStaleSession(sessionId)` | Abstract method - concrete transports implement this to remove stale sessions |

**Cleanup Sequence**

```mermaid
sequenceDiagram
    participant Caller as "Caller"
    participant Transport as "StatefulTransport"
    participant Session as "Session Object"
    participant Heartbeat as "Heartbeat Interval"
    participant SDK as "SDK Transport"
    participant Server as "McpServer"
    participant Map as "sessions Map"
    participant Metrics as "MetricsCounter"
    
    Caller->>Transport: "cleanupSession(sessionId)"
    Transport->>Session: "Check cleaningUp flag"
    
    alt "Already cleaning up"
        Session-->>Transport: "cleaningUp = true"
        Transport-->>Caller: "Return early (skip)"
    else "Not yet cleaning up"
        Transport->>Session: "Set cleaningUp = true"
        Transport->>Heartbeat: "stopHeartbeat(sessionId)"
        Heartbeat-->>Transport: "Interval cleared"
        
        Transport->>SDK: "transport.close()"
        SDK-->>Transport: "Promise resolves/rejects"
        
        Transport->>Server: "server.close()"
        Server-->>Transport: "Promise resolves/rejects"
        
        Transport->>Map: "sessions.delete(sessionId)"
        Transport->>Metrics: "trackSessionCleaned()"
        Transport->>Metrics: "trackSessionDeleted()"
        Transport->>Metrics: "updateActiveConnections()"
        Transport->>Metrics: "disconnectClient(clientInfo)"
        
        Transport-->>Caller: "Cleanup complete"
    end
```

**Sources:** [packages/app/src/server/transport/base-transport.ts:685-740]()

---

## Key Interfaces and Types

### ServerFactory and ServerFactoryResult

The `ServerFactory` type defines the function signature for creating MCP server instances:

```typescript
// Factory function signature
export type ServerFactory = (
  headers: Record<string, string> | null,
  userSettings?: AppSettings,
  skipGradio?: boolean,
  sessionInfo?: {
    clientSessionId?: string;
    isAuthenticated?: boolean;
    clientInfo?: { name: string; version: string };
  }
) => Promise<ServerFactoryResult>;

// Return type
export interface ServerFactoryResult {
  server: McpServer;
  userDetails?: WhoAmI;
}
```

The factory is called during session creation to instantiate a new MCP server with the appropriate tool selection and configuration.

**Sources:** [packages/app/src/server/transport/base-transport.ts:16-35]()

### SessionMetadata

The `SessionMetadata` interface provides a standardized structure for tracking session information across all transport types:

```typescript
export interface SessionMetadata {
  id: string;                    // Unique session identifier
  connectedAt: Date;             // When session was created
  lastActivity: Date;            // Last request or successful ping
  requestCount: number;          // Number of requests processed
  isAuthenticated: boolean;      // Whether HF token is present
  clientInfo?: {                 // Client identity (after initialization)
    name: string;                // e.g., "claude-desktop", "vscode"
    version: string;             // Client version string
  };
  capabilities: {                // MCP capabilities
    sampling?: boolean;
    roots?: boolean;
  };
  pingFailures?: number;         // Consecutive ping failures
  lastPingAttempt?: Date;        // Last time ping was sent
}
```

**Sources:** [packages/app/src/server/transport/base-transport.ts:45-61]()

### BaseSession

The `BaseSession` interface is the generic session container that all stateful transports extend:

```typescript
export interface BaseSession<T = unknown> {
  transport: T;                  // SDK transport instance (type varies)
  server: McpServer;             // MCP server instance
  metadata: SessionMetadata;     // Session tracking data
  heartbeatInterval?: NodeJS.Timeout;  // Heartbeat timer (SSE/StreamableHTTP)
  cleaningUp?: boolean;          // Cleanup guard flag
}
```

Concrete implementations extend this with transport-specific fields (e.g., `activeResponse` for StreamableHTTP, `cleanup` function for SSE).

**Sources:** [packages/app/src/server/transport/base-transport.ts:67-73]()

### TransportOptions

The `TransportOptions` interface defines initialization parameters:

```typescript
export interface TransportOptions {
  port?: number;
  onClientInfoUpdate?: (clientInfo: { name: string; version: string }) => void;
}
```

**Sources:** [packages/app/src/server/transport/base-transport.ts:37-40]()

### STATELESS_MODE Constant

The `STATELESS_MODE` constant (`-1`) is returned by `getActiveConnectionCount()` for stateless transports to distinguish them from transports with zero active connections:

```typescript
export const STATELESS_MODE = -1;
```

**Sources:** [packages/app/src/server/transport/base-transport.ts:78]()

---

## Metrics Tracking System

The base transport classes integrate tightly with the `MetricsCounter` to provide comprehensive tracking:

### Metrics Categories

| Metric Category | Tracked By | Examples |
|----------------|-----------|----------|
| **Requests** | `BaseTransport` | Total requests received, errors by status code |
| **Connections** | `BaseTransport` | Total connections, authenticated/anonymous/unauthorized counts |
| **Sessions** | `StatefulTransport` | Active sessions, session creation/deletion, resume failures |
| **Methods** | `BaseTransport` | Method call counts, durations, error rates per method |
| **Client Activity** | `StatefulTransport` | Per-client session counts, activity tracking, disconnections |
| **Ping Status** | `StatefulTransport` | Pings sent/succeeded/failed |

### Metrics Methods in BaseTransport

```typescript
// Request tracking
protected trackRequest(): void
protected trackError(statusCode?: number, error?: Error): void
protected trackNewConnection(): void

// Method tracking
protected trackMethodCall(methodName: string | null, startTime: number, 
                         isError: boolean, clientInfo?: ClientInfo): void

// Auth tracking (via validateAuthAndTrackMetrics)
metrics.trackAuthenticatedConnection()
metrics.trackAnonymousConnection()
metrics.trackUnauthorizedConnection()
```

**Sources:** [packages/app/src/server/transport/base-transport.ts:148-280]()

### Metrics Methods in StatefulTransport

```typescript
// Session lifecycle
protected trackSessionCreated(sessionId: string): void
protected trackSessionCleaned(session?: TSession): void

// Client tracking
protected associateSessionWithClient(clientInfo: ClientInfo): void
protected updateClientActivity(clientInfo?: ClientInfo): void
protected disconnectClient(clientInfo?: ClientInfo): void

// Ping tracking
metrics.trackPingSent()
metrics.trackPingSuccess()
metrics.trackPingFailed()
```

**Sources:** [packages/app/src/server/transport/base-transport.ts:576-601]()

---

## Configuration System

### Environment Variables

Stateful transports read configuration from environment variables with sensible defaults:

| Environment Variable | Default | Purpose |
|---------------------|---------|---------|
| `MCP_CLIENT_CONNECTION_CHECK` | `90000` (90s) | How often to check for stale connections |
| `MCP_CLIENT_CONNECTION_TIMEOUT` | `600000` (10min) | How long before connection is considered stale |
| `MCP_CLIENT_HEARTBEAT_INTERVAL` | `30000` (30s) | SSE heartbeat frequency |
| `MCP_PING_ENABLED` | `true` | Whether to enable ping keep-alive |
| `MCP_PING_INTERVAL` | `30000` (30s) | How often to send pings |
| `MCP_PING_FAILURE_THRESHOLD` | `1` | Consecutive failures before session is distressed |

### Configuration Access

The `getConfiguration()` method exposes these settings:

```typescript
getConfiguration(): {
  heartbeatInterval: number;
  staleCheckInterval: number;
  staleTimeout: number;
  pingEnabled: boolean;
  pingInterval: number;
  pingFailureThreshold: number;
}
```

This is used by the web dashboard to display current transport settings.

**Sources:** [packages/app/src/server/transport/base-transport.ts:360-365](), [packages/app/src/server/transport/base-transport.ts:613-629]()

---

## Abstract Methods Contract

Concrete transport implementations must provide:

### Required Methods

| Method | BaseTransport | StatefulTransport | Purpose |
|--------|---------------|-------------------|---------|
| `initialize(options)` | ✓ Required | Inherited | Set up routes, start intervals |
| `cleanup()` | ✓ Required | Inherited | Clean up resources on shutdown |
| `getActiveConnectionCount()` | ✓ Required | Implemented | Return session count or `STATELESS_MODE` |
| `removeStaleSession(sessionId)` | - | ✓ Required | Handle removal of stale session |

### Optional Methods

| Method | Purpose |
|--------|---------|
| `shutdown()` | Mark transport as shutting down (reject new connections) |
| `getSessions()` | Return array of `SessionMetadata` for dashboard |
| `getConfiguration()` | Return configuration settings |

**Sources:** [packages/app/src/server/transport/base-transport.ts:97-143](), [packages/app/src/server/transport/base-transport.ts:538-629]()

---

## Implementation Patterns

### Typical StatefulTransport Implementation

Concrete stateful transports follow this pattern:

```typescript
class ConcreteTransport extends StatefulTransport<ConcreteSession> {
  async initialize(options: TransportOptions): Promise<void> {
    // 1. Set up Express routes
    this.app.post('/endpoint', (req, res) => { ... });
    
    // 2. Start monitoring processes
    this.startStaleConnectionCheck();
    this.startPingKeepAlive();
    
    // 3. Log initialization
    logger.info({ config }, 'Transport initialized');
  }
  
  protected async removeStaleSession(sessionId: string): Promise<void> {
    // Use base class cleanupSession() method
    await this.cleanupSession(sessionId);
    
    // Add any transport-specific cleanup
    // ...
  }
  
  async cleanup(): Promise<void> {
    // 1. Stop monitoring processes
    this.stopStaleConnectionCheck();
    
    // 2. Clean up all sessions
    await this.cleanupAllSessions();
    
    // 3. Log completion
    logger.info('Cleanup complete');
  }
}
```

**Sources:** [packages/app/src/server/transport/sse-transport.ts:14-261](), [packages/app/src/server/transport/streamable-http-transport.ts:18-313]()

### Typical BaseTransport Implementation (Stateless)

Stateless transports directly extend `BaseTransport`:

```typescript
class StatelessTransport extends BaseTransport {
  async initialize(options: TransportOptions): Promise<void> {
    // Set up routes for request handling
    this.app.post('/endpoint', (req, res) => {
      this.trackRequest();
      void this.handleRequest(req, res);
    });
  }
  
  getActiveConnectionCount(): number {
    // Return STATELESS_MODE or analytics session count
    return this.analyticsMode ? this.analyticsSessions.size : STATELESS_MODE;
  }
  
  async cleanup(): Promise<void> {
    // Minimal cleanup - no persistent sessions
    logger.info('Cleanup complete');
  }
}
```

**Sources:** [packages/app/src/server/transport/stateless-http-transport.ts:39-555]()

---

## Summary

The base transport classes provide a robust foundation for MCP server connectivity:

- **`BaseTransport`** handles metrics, authentication, and request analysis for all transports
- **`StatefulTransport`** adds session management, health monitoring, and automatic cleanup
- **Standardized interfaces** (`SessionMetadata`, `BaseSession`) ensure consistency across implementations
- **Environment-driven configuration** allows tuning of timeouts and intervals
- **Comprehensive metrics** track every aspect of transport operation
- **Abstract method contract** enforces implementation requirements while maximizing code reuse

Concrete transport implementations (STDIO, SSE, StreamableHTTP, StatelessHTTP) build on these classes to provide specific connection mechanisms while inheriting all common functionality.

**Sources:** [packages/app/src/server/transport/base-transport.ts:1-807]()

---

# Page: STDIO Transport

# STDIO Transport

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.dockerignore](.dockerignore)
- [Dockerfile](Dockerfile)
- [README.md](README.md)
- [packages/app/src/server/transport/base-transport.ts](packages/app/src/server/transport/base-transport.ts)
- [packages/app/src/server/transport/stateless-http-transport.ts](packages/app/src/server/transport/stateless-http-transport.ts)
- [packages/app/vite.config.ts](packages/app/vite.config.ts)
- [packages/mcp/src/duplicate-space.ts](packages/mcp/src/duplicate-space.ts)
- [packages/mcp/src/error-messages.ts](packages/mcp/src/error-messages.ts)
- [start.sh](start.sh)

</details>



## Purpose and Scope

This document covers the STDIO (Standard Input/Output) transport implementation, which enables CLI-based clients to communicate with the MCP server through stdin/stdout pipes. This is one of four transport mechanisms supported by the system. For information about HTTP-based transports, see [HTTP Transports](#7.4). For information about SSE transport, see [SSE Transport](#7.3). For the base transport architecture, see [Base Transport Classes](#7.1).

## Overview

The STDIO transport implements the MCP protocol over standard input and output streams, making it suitable for command-line integration scenarios where the MCP server runs as a subprocess. Unlike HTTP-based transports, STDIO operates without a web server, communicating directly through process pipes.

**Key Characteristics:**

| Property | Value |
|----------|-------|
| **Communication** | stdin/stdout pipes |
| **Server Lifecycle** | Single long-lived instance |
| **Authentication** | Environment variables (`HF_TOKEN` or `DEFAULT_HF_TOKEN`) |
| **HTTP Server** | None |
| **Session Model** | Single persistent session |
| **Primary Clients** | Claude Code, Gemini CLI, other CLI tools |

The STDIO transport is particularly important for local development workflows and CLI-based AI assistants that spawn the MCP server as a child process.

**Sources:** [README.md:127-128](), [README.md:144](), [packages/app/src/server/transport/base-transport.ts:1-346]()

## Architecture Position

```mermaid
graph TB
    subgraph "CLI Clients"
        Claude["Claude Code<br/>claude mcp add"]
        Gemini["Gemini CLI<br/>gemini mcp add"]
        CustomCLI["Custom CLI Tools"]
    end
    
    subgraph "STDIO Transport Layer"
        StdioTransport["STDIOTransport<br/>packages/app/src/server/transport/stdio-transport.ts"]
        StdioEntry["stdio.js Entry Point<br/>packages/app/src/server/stdio.ts"]
    end
    
    subgraph "Base Classes"
        BaseTransport["BaseTransport<br/>Abstract class with metrics,<br/>auth validation, logging"]
    end
    
    subgraph "Core MCP"
        ServerFactory["ServerFactory Function<br/>createServerFactory()"]
        McpServer["McpServer Instance<br/>Tools + Prompts"]
        SDKTransport["StdioServerTransport<br/>@modelcontextprotocol/sdk"]
    end
    
    subgraph "Process Environment"
        EnvVars["Environment Variables<br/>HF_TOKEN or<br/>DEFAULT_HF_TOKEN"]
        StdStreams["Process Streams<br/>process.stdin<br/>process.stdout"]
    end
    
    Claude -->|spawn subprocess| StdioEntry
    Gemini -->|spawn subprocess| StdioEntry
    CustomCLI -->|spawn subprocess| StdioEntry
    
    StdioEntry --> StdioTransport
    StdioTransport -.extends.- BaseTransport
    
    StdioTransport -->|reads| EnvVars
    StdioTransport -->|creates via| ServerFactory
    ServerFactory --> McpServer
    StdioTransport -->|connects to| SDKTransport
    SDKTransport -->|reads/writes| StdStreams
    SDKTransport --> McpServer
    
    StdStreams -->|pipes to| Claude
    StdStreams -->|pipes to| Gemini
    StdStreams -->|pipes to| CustomCLI
```

The STDIO transport sits at the CLI integration boundary, bridging subprocess communication with the MCP server core. Unlike stateful HTTP transports that extend `StatefulTransport`, STDIO extends `BaseTransport` directly since it doesn't require session management infrastructure.

**Sources:** [README.md:127-130](), [README.md:217-222](), [start.sh:34-37]()

## Initialization and Lifecycle

### Startup Sequence

```mermaid
sequenceDiagram
    participant Launcher as CLI Launcher<br/>(e.g., claude)
    participant Entry as stdio.js<br/>Entry Point
    participant Transport as STDIOTransport
    participant Factory as ServerFactory
    participant Server as McpServer
    participant SDK as StdioServerTransport
    
    Launcher->>Entry: spawn process
    Entry->>Entry: Read HF_TOKEN or<br/>DEFAULT_HF_TOKEN from env
    Entry->>Transport: new STDIOTransport(serverFactory, app)
    Entry->>Transport: initialize(options)
    
    Transport->>Transport: validateAuthAndTrackMetrics()
    Transport->>Factory: serverFactory(headers, settings)
    Factory->>Server: Create McpServer with tools
    Factory-->>Transport: ServerFactoryResult
    
    Transport->>SDK: new StdioServerTransport()
    Transport->>Server: server.connect(sdkTransport)
    SDK->>SDK: Attach to process.stdin/stdout
    
    SDK-->>Launcher: Connection established
    
    loop Request Processing
        Launcher->>SDK: JSON-RPC message via stdin
        SDK->>Server: Route to method handler
        Server->>Server: Process (tool/prompt/resource)
        Server-->>SDK: JSON-RPC response
        SDK-->>Launcher: Response via stdout
    end
    
    Launcher->>Entry: SIGTERM or process.exit()
    Entry->>Transport: cleanup()
    Transport->>Server: server.close()
    Transport->>SDK: transport.close()
```

The STDIO transport has a simpler lifecycle than HTTP transports because it manages only a single server instance for the lifetime of the process. The server is created during initialization and persists until the process terminates.

**Sources:** [start.sh:34-37](), [packages/app/src/server/transport/base-transport.ts:97-129]()

### Entry Point

The STDIO transport is launched via the `stdio.js` entry point, which is built from the source TypeScript:

```
packages/app/src/server/stdio.ts  →  compile  →  packages/app/dist/server/stdio.js
```

The entry point is invoked by the startup script:

[start.sh:35-37]()

**Sources:** [start.sh:1-58](), [README.md:144-146]()

## Authentication Model

### Environment-Based Token Resolution

```mermaid
graph LR
    subgraph "Environment Variables (Priority Order)"
        DEFAULT_HF["DEFAULT_HF_TOKEN<br/>(Explicit override)"]
        HF_TOKEN["HF_TOKEN<br/>(Standard token)"]
    end
    
    subgraph "Startup Logic"
        StartScript["start.sh<br/>Line 12-15"]
    end
    
    subgraph "Transport Layer"
        ValidateAuth["validateAuthAndTrackMetrics()<br/>base-transport.ts:305-345"]
        ExtractAuth["extractAuthBouquetAndMix()<br/>auth-utils.ts"]
    end
    
    subgraph "API Calls"
        WhoAmI["whoAmI() validation<br/>@huggingface/hub"]
        HFApi["Hugging Face API"]
    end
    
    subgraph "Metrics Tracking"
        AuthMetrics["Authentication Metrics<br/>- trackAuthenticatedConnection()<br/>- trackAnonymousConnection()<br/>- trackUnauthorizedConnection()"]
    end
    
    DEFAULT_HF -->|"Priority 1:<br/>If set"| StartScript
    HF_TOKEN -->|"Priority 2:<br/>If DEFAULT_HF_TOKEN not set<br/>in stdio mode"| StartScript
    
    StartScript -->|"Export DEFAULT_HF_TOKEN"| ValidateAuth
    ValidateAuth --> ExtractAuth
    ExtractAuth -->|"If token present"| WhoAmI
    WhoAmI --> HFApi
    HFApi -->|"200: Valid"| AuthMetrics
    HFApi -->|"401: Invalid"| AuthMetrics
    ExtractAuth -->|"No token"| AuthMetrics
```

The STDIO transport uses environment variables for authentication rather than HTTP headers. The startup script [start.sh:12-15]() implements special logic: if running in STDIO mode and `DEFAULT_HF_TOKEN` is not set, it copies `HF_TOKEN` to `DEFAULT_HF_TOKEN`.

**Token Validation:**

The `validateAuthAndTrackMetrics()` method [packages/app/src/server/transport/base-transport.ts:305-345]() validates tokens by calling the Hugging Face API's `whoAmI()` endpoint. This validation happens once at startup for STDIO, versus per-request for stateless HTTP.

**Metrics Tracked:**

| Condition | Metric Method |
|-----------|---------------|
| Valid token (200 from whoAmI) | `trackAuthenticatedConnection()` |
| Invalid token (401 from whoAmI) | `trackUnauthorizedConnection()` |
| No token provided | `trackAnonymousConnection()` |

**Security Note:**

The `DEFAULT_HF_TOKEN` environment variable should only be used in development/test environments or for local STDIO deployments, as stated in [README.md:241-242](). For production HTTP deployments, tokens should be provided via Authorization headers.

**Sources:** [start.sh:12-15](), [packages/app/src/server/transport/base-transport.ts:305-345](), [README.md:237-242]()

## Connection Model

### Single-Session Architecture

Unlike stateful HTTP transports that maintain a `Map<string, Session>` for multiple concurrent connections, the STDIO transport operates with a single, persistent server instance:

```mermaid
graph TB
    subgraph "HTTP Transports (Multi-Session)"
        HTTPMap["sessions: Map<string, Session><br/>Multiple concurrent clients"]
        Session1["Session 1<br/>transport + server"]
        Session2["Session 2<br/>transport + server"]
        Session3["Session 3<br/>transport + server"]
        
        HTTPMap --> Session1
        HTTPMap --> Session2
        HTTPMap --> Session3
    end
    
    subgraph "STDIO Transport (Single Session)"
        STDIOServer["Single McpServer Instance<br/>Created at startup<br/>Lives until process exit"]
        STDIOTransport["Single StdioServerTransport<br/>Connected to stdin/stdout"]
        
        STDIOServer --- STDIOTransport
    end
    
    style HTTPMap fill:#f9f9f9
    style STDIOServer fill:#f9f9f9
```

**No Session Management:**

The STDIO transport does not implement:
- Session ID generation
- Session maps or tracking
- Stale connection detection
- Heartbeat intervals
- Ping keep-alive mechanisms

These are handled by the `StatefulTransport` class [packages/app/src/server/transport/base-transport.ts:352-806](), which STDIO does not extend.

**`getActiveConnectionCount()` Implementation:**

For STDIO, this method returns either:
- `1` (if the server is running)
- `0` (if the server has been cleaned up)

This differs from HTTP transports which return the size of their session maps, or `STATELESS_MODE` (-1) for stateless HTTP [packages/app/src/server/transport/base-transport.ts:77-78]().

**Sources:** [packages/app/src/server/transport/base-transport.ts:352-806](), [packages/app/src/server/transport/base-transport.ts:113-122]()

## Request/Response Flow

### Message Processing Pipeline

```mermaid
sequenceDiagram
    participant Client as CLI Client<br/>(stdin/stdout)
    participant SDK as StdioServerTransport<br/>@modelcontextprotocol/sdk
    participant Server as McpServer
    participant ToolImpl as Tool Implementation<br/>(e.g., ModelSearchTool)
    participant HFAPI as Hugging Face API
    
    Client->>SDK: JSON-RPC request via stdin<br/>{"jsonrpc":"2.0","method":"tools/call",...}
    SDK->>SDK: Parse JSON message
    SDK->>Server: Route to method handler
    
    alt Built-in Tool Call
        Server->>ToolImpl: Execute tool handler
        ToolImpl->>HFAPI: API request
        HFAPI-->>ToolImpl: API response
        ToolImpl->>ToolImpl: Format as ToolResult
        ToolImpl-->>Server: Formatted result
    else Gradio Tool Call
        Server->>Server: Gradio tool handler
        Server->>HFAPI: SSE connection to Space
        HFAPI-->>Server: Streaming results
        Server->>Server: applyResultPostProcessing()
        Server-->>Server: Processed result
    else Prompt Request
        Server->>Server: Retrieve prompt template
        Server->>Server: Fill prompt with data
        Server-->>Server: Prompt result
    end
    
    Server-->>SDK: JSON-RPC response
    SDK->>SDK: Serialize to JSON
    SDK-->>Client: Write to stdout
```

**JSON-RPC Protocol:**

All communication follows the JSON-RPC 2.0 specification. Messages are newline-delimited JSON objects written to streams.

**Synchronous Processing:**

Unlike HTTP transports where multiple requests can be processed concurrently across sessions, STDIO processes requests sequentially on a single server instance. The MCP SDK's `StdioServerTransport` handles the stream reading/writing and message framing.

**No Session Context:**

Request handlers in STDIO mode cannot access:
- Session IDs
- Per-session state
- Client connection metadata (until after `initialize` is called)

This information is available in stateful HTTP transports via the session map [packages/app/src/server/transport/base-transport.ts:353]().

**Sources:** [packages/app/src/server/transport/base-transport.ts:192-223]()

## Configuration

### Environment Variables

The STDIO transport respects the following environment variables:

| Variable | Default | Description | Source |
|----------|---------|-------------|--------|
| `HF_TOKEN` | (none) | Standard Hugging Face authentication token | [README.md:242]() |
| `DEFAULT_HF_TOKEN` | (none) | Override token (inherits from `HF_TOKEN` in STDIO mode) | [start.sh:12-15]() |
| `PORT` | 3000 | Port for web dashboard (STDIO still launches dashboard) | [start.sh:8]() |
| `HF_API_TIMEOUT` | 12500 | Timeout for HF API requests (milliseconds) | [README.md:243]() |
| `USER_CONFIG_API` | (local) | URL for user settings service | [README.md:244]() |
| `SEARCH_ENABLES_FETCH` | false | Auto-enable `hf_doc_fetch` when `hf_doc_search` is enabled | [README.md:247]() |
| `AUTHENTICATE_TOOL` | (unset) | Include OAuth authentication tool | [README.md:246]() |

**STDIO-Specific Behavior:**

The startup script [start.sh:12-15]() implements special handling for STDIO:

```sh
if [ "$TRANSPORT" = "stdio" ] && [ -z "$DEFAULT_HF_TOKEN" ] && [ -n "$HF_TOKEN" ]; then
  export DEFAULT_HF_TOKEN="$HF_TOKEN"
fi
```

This ensures that the standard `HF_TOKEN` environment variable works correctly in STDIO mode.

**No Connection Management Variables:**

The following variables from [README.md:228-235]() do NOT apply to STDIO:
- `MCP_CLIENT_HEARTBEAT_INTERVAL`
- `MCP_CLIENT_CONNECTION_CHECK`
- `MCP_CLIENT_CONNECTION_TIMEOUT`
- `MCP_PING_ENABLED`
- `MCP_PING_INTERVAL`

These are only relevant for stateful transports (SSE and StreamableHTTP) that maintain session maps.

**Sources:** [README.md:237-248](), [start.sh:12-15](), [README.md:228-235]()

### Tool Selection

STDIO supports all tool selection mechanisms:

```mermaid
graph TB
    subgraph "Tool Selection Headers"
        Bouquet["x-mcp-bouquet<br/>(Bouquet override)"]
        Mix["x-mcp-mix<br/>(Additive selection)"]
        Gradio["x-mcp-gradio<br/>(Space IDs)"]
    end
    
    subgraph "Environment Simulation"
        Note["Note: In STDIO mode,<br/>headers are simulated from<br/>environment variables<br/>during server creation"]
    end
    
    subgraph "Tool Selection Strategy"
        Strategy["ToolSelectionStrategy<br/>Precedence:<br/>1. Bouquet override<br/>2. Mix mode<br/>3. User settings<br/>4. Default (all tools)"]
    end
    
    subgraph "Result"
        EnabledTools["Enabled Built-in Tools"]
        GradioTools["Enabled Gradio Tools"]
    end
    
    Bouquet --> Note
    Mix --> Note
    Gradio --> Note
    Note --> Strategy
    Strategy --> EnabledTools
    Strategy --> GradioTools
```

Since STDIO doesn't use HTTP requests, the "headers" for tool selection are constructed from environment variables or configuration files at startup. The tool selection logic is the same as HTTP transports (documented in [Tool Selection Strategy](#5.2)), but the input source differs.

**Sources:** [packages/app/src/server/transport/base-transport.ts:26-35]()

## Use Cases and Client Integration

### Claude Code Integration

Claude Code uses the STDIO transport to integrate with MCP servers. The installation command:

```bash
claude mcp add hf-mcp-server -t http https://huggingface.co/mcp?login
```

For authenticated access:

```bash
claude mcp add hf-mcp-server \
  -t http https://huggingface.co/mcp \
  -H "Authorization: Bearer <YOUR_HF_TOKEN>"
```

**Configuration Location:**

Claude Code stores MCP server configurations in its configuration file, which specifies how to spawn the subprocess and what environment variables to provide.

**Sources:** [README.md:24-40]()

### Gemini CLI Integration

Gemini CLI also supports STDIO transport:

```bash
gemini mcp add -t http huggingface https://huggingface.co/mcp?login
```

The Gemini CLI includes an extension system that bundles the MCP server with custom commands:

```bash
gemini extensions install https://github.com/huggingface/hf-mcp-server
gemini  # then run: /mcp auth huggingface
```

**Sources:** [README.md:45-65]()

### Local Development

For local testing and development, the STDIO transport can be started directly:

```bash
npx @llmindset/hf-mcp-server
```

This spawns the server in STDIO mode, reading JSON-RPC messages from stdin and writing responses to stdout. Developers can pipe input/output to test the protocol:

```bash
echo '{"jsonrpc":"2.0","method":"initialize",...}' | npx @llmindset/hf-mcp-server
```

**Sources:** [README.md:144]()

### Docker STDIO Deployment

STDIO mode can be run in Docker with interactive mode:

```bash
docker run -i --rm \
  -e TRANSPORT=stdio \
  -e DEFAULT_HF_TOKEN=hf_xxx \
  ghcr.io/evalstate/hf-mcp-server:latest
```

The `-i` flag is required to keep stdin open for the container. The `start.sh` script detects `TRANSPORT=stdio` and launches the appropriate entry point [start.sh:35-37]().

**Sources:** [README.md:210-213](), [start.sh:34-37]()

## Comparison with Other Transports

### Transport Comparison Matrix

| Feature | STDIO | SSE | StreamableHTTP | StatelessHTTP |
|---------|-------|-----|----------------|---------------|
| **Base Class** | `BaseTransport` | `StatefulTransport` | `StatefulTransport` | `BaseTransport` |
| **Server Instances** | Single | Per-session | Per-session | Per-request |
| **Communication** | stdin/stdout | HTTP SSE | HTTP streaming | HTTP POST |
| **Session Tracking** | None | Map-based | Map-based | Optional (analytics) |
| **Authentication** | Environment vars | HTTP headers | HTTP headers | HTTP headers |
| **Heartbeat** | No | Yes | Yes | No |
| **Stale Detection** | No | Yes | Yes | No |
| **Primary Use Case** | CLI tools | Legacy web clients | Modern web clients | Stateless/serverless |
| **Implementation** | `stdio-transport.ts` | `sse-transport.ts` | `streamable-http-transport.ts` | `stateless-http-transport.ts` |

**Key Architectural Differences:**

1. **Lifecycle Management:**
   - STDIO: Single server for process lifetime
   - Stateful (SSE/HTTP): Per-connection servers in session map
   - Stateless: New server for each request

2. **Connection Monitoring:**
   - STDIO: Relies on process signals
   - Stateful: Active monitoring via heartbeat/ping
   - Stateless: No monitoring needed

3. **Cleanup Strategy:**
   - STDIO: Process termination cleans up automatically
   - Stateful: Must track and clean up stale sessions [base-transport.ts:506-533]()
   - Stateless: Cleanup after each request [stateless-http-transport.ts:324-341]()

**Sources:** [packages/app/src/server/transport/base-transport.ts:82-346](), [packages/app/src/server/transport/base-transport.ts:352-806](), [packages/app/src/server/transport/stateless-http-transport.ts:39-555]()

### When to Use STDIO

**Choose STDIO when:**
- Building CLI tools or extensions
- Running MCP server as a subprocess
- Deploying locally on developer machines
- Integrating with tools that spawn child processes (Claude Code, Gemini CLI)
- Want simplest possible deployment (no HTTP server configuration)

**Choose HTTP transports when:**
- Multiple concurrent clients need to connect
- Running as a web service
- Need RESTful API access
- Want browser-based dashboard access
- Deploying to cloud environments
- Need stateless request handling for serverless

**Sources:** [README.md:123-136]()

## Metrics and Monitoring

### Metrics Collection

Despite operating without HTTP, the STDIO transport still collects metrics through the `MetricsCounter` class inherited from `BaseTransport`:

```mermaid
graph LR
    subgraph "STDIO Transport"
        Transport["STDIOTransport"]
    end
    
    subgraph "Base Transport Metrics"
        MetricsCounter["MetricsCounter Instance<br/>this.metrics"]
    end
    
    subgraph "Tracked Metrics"
        TotalReq["totalRequests"]
        TotalConn["totalConnections"]
        ActiveConn["activeConnections"]
        Methods["methodStats Map<br/>Per-method timing"]
        Errors["errorStats<br/>By status code"]
        Auth["authStats<br/>authenticated/anonymous/<br/>unauthorized"]
    end
    
    Transport --> MetricsCounter
    MetricsCounter --> TotalReq
    MetricsCounter --> TotalConn
    MetricsCounter --> ActiveConn
    MetricsCounter --> Methods
    MetricsCounter --> Errors
    MetricsCounter --> Auth
```

**Available Metrics Methods:**

From [packages/app/src/server/transport/base-transport.ts:148-280]():

- `trackRequest()` - Increment request counter
- `trackError(statusCode?, error?)` - Track errors by status code
- `trackNewConnection()` - Increment total connections
- `trackMethodCall(methodName, startTime, isError, clientInfo)` - Track method timing and success/failure
- `trackAuthenticatedConnection()` - Track authenticated requests
- `trackAnonymousConnection()` - Track requests without token
- `trackUnauthorizedConnection()` - Track invalid tokens

**Accessing Metrics:**

Even in STDIO mode, the web dashboard is available (by default on port 3000) and can display metrics:

```bash
npx @llmindset/hf-mcp-server  # STDIO server running
# In another terminal:
curl http://localhost:3000/api/transport-metrics
```

The dashboard polls `/api/transport-metrics` to display real-time statistics about the STDIO transport.

**Sources:** [packages/app/src/server/transport/base-transport.ts:83-130](), [packages/app/src/server/transport/base-transport.ts:148-280]()

---

# Page: SSE Transport

# SSE Transport

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.dockerignore](.dockerignore)
- [Dockerfile](Dockerfile)
- [README.md](README.md)
- [packages/app/src/server/transport/sse-transport.ts](packages/app/src/server/transport/sse-transport.ts)
- [packages/app/src/server/transport/streamable-http-transport.ts](packages/app/src/server/transport/streamable-http-transport.ts)
- [packages/app/vite.config.ts](packages/app/vite.config.ts)
- [packages/mcp/src/duplicate-space.ts](packages/mcp/src/duplicate-space.ts)
- [packages/mcp/src/error-messages.ts](packages/mcp/src/error-messages.ts)
- [start.sh](start.sh)

</details>



## Purpose and Scope

This document describes the Server-Sent Events (SSE) transport implementation used by the Hugging Face MCP Server for real-time, stateful client connections. The SSE transport maintains persistent sessions with clients through HTTP-based event streams and handles bidirectional communication via separate endpoints.

For information about the base transport abstractions that SSE extends, see [Base Transport Classes](#7.1). For comparison with other transport options, see [STDIO Transport](#7.2) and [HTTP Transports](#7.4).

**Note**: SSE transport is being deprecated in favor of StreamableHTTP but remains commonly deployed in production environments.

Sources: [packages/app/src/server/transport/sse-transport.ts:1-284](), [README.md:128-129]()

## Overview

The `SseTransport` class implements a stateful, session-based transport mechanism using Server-Sent Events for server-to-client communication and HTTP POST for client-to-server messages. It extends `StatefulTransport` to inherit session management, heartbeat monitoring, and stale connection detection capabilities.

### Key Characteristics

| Characteristic | Value |
|---------------|-------|
| Base Class | `StatefulTransport<SSEConnection>` |
| Session Model | Stateful with session ID tracking |
| Endpoints | `GET /sse` (event stream), `POST /message` (client messages) |
| Authentication | Per-session, validated on connection |
| Heartbeat | Enabled by default (30s interval) |
| Stale Detection | 90s check interval, 5min timeout |
| Use Cases | Desktop apps, persistent connections |

Sources: [packages/app/src/server/transport/sse-transport.ts:14-42](), [README.md:227-235]()

## Architecture and Data Flow

```mermaid
graph TB
    subgraph "Client"
        ClientSSE["SSE Connection<br/>(GET /sse)"]
        ClientPost["Message Sender<br/>(POST /message)"]
    end
    
    subgraph "SseTransport Class"
        HandleSSE["handleSseConnection()<br/>Line 44-152"]
        HandleMsg["handleSseMessage()<br/>Line 154-208"]
        CreateSession["Session Creation<br/>+ SSEServerTransport"]
        Cleanup["cleanupSession()<br/>inherited"]
    end
    
    subgraph "Session Management"
        SessionMap["sessions: Map<string, SSEConnection>"]
        SessionMeta["metadata:<br/>- id<br/>- connectedAt<br/>- lastActivity<br/>- requestCount<br/>- isAuthenticated"]
    end
    
    subgraph "Background Tasks"
        Heartbeat["startHeartbeat()<br/>Write to res"]
        StaleCheck["startStaleConnectionCheck()<br/>90s interval"]
        PingKeepAlive["startPingKeepAlive()<br/>30s interval"]
    end
    
    subgraph "MCP Server"
        ServerFactory["serverFactory()"]
        McpServer["McpServer instance"]
        Transport["SSEServerTransport"]
    end
    
    ClientSSE -->|"GET /sse?sessionId=..."| HandleSSE
    ClientPost -->|"POST /message?sessionId=..."| HandleMsg
    
    HandleSSE --> CreateSession
    CreateSession --> ServerFactory
    ServerFactory --> McpServer
    CreateSession --> Transport
    McpServer -.connect.- Transport
    
    HandleSSE --> SessionMap
    HandleMsg --> SessionMap
    SessionMap --> SessionMeta
    
    HandleSSE --> Heartbeat
    HandleSSE --> StaleCheck
    HandleSSE --> PingKeepAlive
    
    HandleMsg --> Transport
    Transport --> McpServer
    
    StaleCheck --> Cleanup
    Cleanup --> SessionMap
```

**SSE Transport Request Flow and Session Lifecycle**

This diagram maps the complete flow from client connection through message handling to session cleanup, showing how `SseTransport` coordinates between HTTP endpoints, session storage, and the underlying MCP server instance.

Sources: [packages/app/src/server/transport/sse-transport.ts:14-284]()

## Endpoints and Routing

The SSE transport exposes two HTTP endpoints that work together to enable bidirectional communication:

### Route Registration

The transport registers its routes during initialization:

```typescript
// GET /sse - Establishes SSE event stream
this.app.get('/sse', (req: Request, res: Response) => {
    this.trackRequest();
    void this.handleSseConnection(req, res);
});

// POST /message - Receives client messages
this.app.post('/message', (req: Request, res: Response) => {
    this.trackRequest();
    void this.handleSseMessage(req, res);
});
```

Sources: [packages/app/src/server/transport/sse-transport.ts:15-27]()

### Endpoint Details

| Endpoint | Method | Purpose | Headers/Query Params |
|----------|--------|---------|---------------------|
| `/sse` | GET | Establish SSE event stream | Query: `sessionId` (optional, for reconnect) |
| `/message` | POST | Send JSON-RPC messages to server | Query: `sessionId` (required) |

The `/sse` endpoint returns a persistent HTTP connection with `Content-Type: text/event-stream`, while `/message` accepts JSON-RPC payloads and returns JSON responses.

Sources: [packages/app/src/server/transport/sse-transport.ts:17-26](), [README.md:220]()

## Session Lifecycle

```mermaid
sequenceDiagram
    participant C as Client
    participant SSE as SseTransport
    participant Auth as validateAuthAndTrackMetrics
    participant Factory as serverFactory
    participant Transport as SSEServerTransport
    participant Server as McpServer
    participant Map as sessions Map
    
    rect rgb(245, 245, 245)
        Note over C,Map: Connection Establishment
        C->>SSE: GET /sse
        SSE->>Auth: Validate HF token
        alt Token invalid
            Auth-->>C: 401 Unauthorized
        end
        Auth->>Factory: Create server with headers
        Factory-->>SSE: {server, proxyFactory}
        SSE->>Transport: new SSEServerTransport('/message', res)
        Note over Transport: Generates sessionId
        SSE->>Map: Store SSEConnection<br/>{transport, server, metadata, cleanup}
        SSE->>Server: server.connect(transport)
        SSE->>SSE: startHeartbeat(sessionId, res)
        SSE->>SSE: setupSseEventHandlers(sessionId, res)
        SSE-->>C: SSE stream established
    end
    
    rect rgb(245, 245, 245)
        Note over C,Map: Message Exchange
        C->>SSE: POST /message?sessionId=abc
        SSE->>Map: Get session by sessionId
        SSE->>SSE: updateSessionActivity(sessionId)
        SSE->>SSE: metadata.requestCount++
        SSE->>Transport: handlePostMessage(req, res, body)
        Transport->>Server: Route to MCP handler
        Server-->>Transport: JSON-RPC response
        Transport-->>SSE: Response
        SSE-->>C: 200 OK + JSON response
    end
    
    rect rgb(245, 245, 245)
        Note over C,Map: Session Cleanup
        alt Client disconnect
            C->>SSE: Connection closed
            SSE->>SSE: res 'close' event
        else Stale detection
            SSE->>SSE: removeStaleSession(sessionId)
        end
        SSE->>SSE: cleanupSession(sessionId)
        SSE->>Server: Close server
        SSE->>Map: Delete session
        SSE->>SSE: logSystemEvent('session_delete')
    end
```

**SSE Session Lifecycle: Connection, Communication, and Cleanup**

This sequence diagram shows the three phases of an SSE session: establishing the connection with authentication and server creation, exchanging messages through the `/message` endpoint, and cleaning up when the connection ends or becomes stale.

Sources: [packages/app/src/server/transport/sse-transport.ts:44-152](), [packages/app/src/server/transport/sse-transport.ts:154-208](), [packages/app/src/server/transport/sse-transport.ts:236-244]()

## Connection Management

### Session Creation

When a client connects to `/sse`, the transport performs the following steps:

1. **Shutdown Check**: Rejects new connections if `isShuttingDown` is true
2. **Reconnection Handling**: If `sessionId` query parameter exists, cleans up old connection
3. **Authentication**: Validates HF token via `validateAuthAndTrackMetrics()`
4. **Server Creation**: Calls `serverFactory()` with request headers and session info
5. **Transport Instantiation**: Creates `SSEServerTransport` with `/message` endpoint
6. **Session Storage**: Stores `SSEConnection` object in `sessions` Map
7. **Connection Setup**: Establishes heartbeat, event handlers, and connects server to transport

Sources: [packages/app/src/server/transport/sse-transport.ts:44-152]()

### SSEConnection Interface

The session object stored in the `sessions` Map has the following structure:

```typescript
interface SSEConnection extends BaseSession<SSEServerTransport> {
    cleanup: () => Promise<void>;
}

// Where BaseSession includes:
interface BaseSession<T> {
    transport: T;                    // SSEServerTransport instance
    server: McpServer;               // MCP server instance
    metadata: {
        id: string;                  // Session ID
        connectedAt: Date;           // Connection timestamp
        lastActivity: Date;          // Last message timestamp
        requestCount: number;        // Total requests processed
        isAuthenticated: boolean;    // Has valid HF token
        capabilities: object;        // Client capabilities
    };
    cleaningUp: boolean;            // Cleanup in progress flag
}
```

Sources: [packages/app/src/server/transport/sse-transport.ts:10-12](), [packages/app/src/server/transport/base-transport.ts:44-66]()

### Reconnection Behavior

When a client attempts to reconnect with an existing `sessionId`:

1. The transport checks if the session still exists in `sessions` Map
2. If found, it logs a warning with session age and cleans up the old connection
3. If not found, it tracks a failed resume metric
4. A new session is always created for the reconnection attempt

This prevents duplicate sessions while allowing graceful reconnection after temporary network issues.

Sources: [packages/app/src/server/transport/sse-transport.ts:54-75]()

## Message Handling

### POST /message Endpoint

The `/message` endpoint handles all client-to-server communication after the SSE connection is established:

```mermaid
graph TB
    Request["POST /message<br/>?sessionId=abc<br/>Body: JSON-RPC"]
    
    ExtractSession["Extract sessionId<br/>from query params"]
    ValidateSession["Lookup in sessions Map"]
    
    UpdateActivity["updateSessionActivity()<br/>Update lastActivity"]
    IncrementCount["metadata.requestCount++<br/>(if actual method call)"]
    
    HandlePost["transport.handlePostMessage()<br/>(req, res, body)"]
    
    McpProcess["MCP Server processes<br/>JSON-RPC request"]
    
    TrackMetrics["metrics.trackMethod()<br/>(name, undefined, error)"]
    
    Response["JSON-RPC response<br/>to client"]
    
    Request --> ExtractSession
    ExtractSession --> ValidateSession
    
    ValidateSession -->|Not found| Error404["404: session_not_found"]
    ValidateSession -->|Found| UpdateActivity
    
    UpdateActivity --> IncrementCount
    IncrementCount --> HandlePost
    HandlePost --> McpProcess
    McpProcess --> TrackMetrics
    TrackMetrics --> Response
    
    Error404 --> TrackMetrics
```

**Message Handling Flow in POST /message Endpoint**

The flow shows how each message updates session state before being processed by the MCP server through the `SSEServerTransport`.

Sources: [packages/app/src/server/transport/sse-transport.ts:154-208]()

### Request Tracking

The transport tracks method calls without timing information (unlike stateless mode) because stateful transports measure HTTP dispatch time rather than MCP processing time:

```typescript
// Track method call without timing
this.metrics.trackMethod(trackingName, undefined, false);
```

This is consistent across both SSE and StreamableHTTP transports.

Sources: [packages/app/src/server/transport/sse-transport.ts:193-194]()

### Error Handling

The message handler provides specific error responses for common failure cases:

| Error Code | Condition | Response |
|-----------|-----------|----------|
| 400 | Missing `sessionId` query parameter | `JsonRpcErrors.invalidParams()` |
| 404 | Session ID not found in Map | `JsonRpcErrors.sessionNotFound()` |
| 500 | Exception during message processing | `JsonRpcErrors.internalError()` |

Sources: [packages/app/src/server/transport/sse-transport.ts:160-177](), [packages/app/src/server/transport/sse-transport.ts:197-206]()

## Heartbeat and Stale Detection

The SSE transport inherits stateful connection management from `StatefulTransport` and configures three monitoring mechanisms:

### Configuration Parameters

The following environment variables control SSE connection health:

| Environment Variable | Default | Purpose |
|---------------------|---------|---------|
| `MCP_CLIENT_HEARTBEAT_INTERVAL` | 30000ms | Heartbeat write frequency |
| `MCP_CLIENT_CONNECTION_CHECK` | 90000ms | Stale session check interval |
| `MCP_CLIENT_CONNECTION_TIMEOUT` | 300000ms (5min) | Session inactivity timeout |
| `MCP_PING_ENABLED` | true | Enable ping keep-alive |
| `MCP_PING_INTERVAL` | 30000ms | Ping cycle interval |

These are logged at initialization time.

Sources: [packages/app/src/server/transport/sse-transport.ts:28-40](), [README.md:227-235]()

### Monitoring Mechanisms

```mermaid
graph TB
    subgraph "Heartbeat System"
        HBTimer["setInterval<br/>(HEARTBEAT_INTERVAL)"]
        HBCheck["Check res.writable"]
        HBWrite["Write ':heartbeat' to stream"]
        HBFail["Connection dead:<br/>cleanupSession()"]
        
        HBTimer --> HBCheck
        HBCheck -->|writable| HBWrite
        HBCheck -->|not writable| HBFail
    end
    
    subgraph "Stale Detection"
        SCTimer["setInterval<br/>(STALE_CHECK_INTERVAL)"]
        SCIterate["Iterate all sessions"]
        SCCompare["Compare lastActivity<br/>to STALE_TIMEOUT"]
        SCRemove["removeStaleSession()"]
        
        SCTimer --> SCIterate
        SCIterate --> SCCompare
        SCCompare -->|stale| SCRemove
    end
    
    subgraph "Ping Keep-Alive"
        PTimer["setInterval<br/>(PING_INTERVAL)"]
        PIterate["Iterate all sessions"]
        PSend["server.sendPing()"]
        
        PTimer --> PIterate
        PIterate -->|if PING_ENABLED| PSend
    end
    
    subgraph "Event Handlers"
        CloseEvent["res 'close' event"]
        ErrorEvent["res 'error' event"]
        FinishEvent["res 'finish' event"]
        CleanupCall["cleanupSession(sessionId)"]
        
        CloseEvent --> CleanupCall
        ErrorEvent --> CleanupCall
        FinishEvent --> CleanupCall
    end
    
    HBFail --> CleanupCall
    SCRemove --> CleanupCall
```

**Three-Layer Connection Monitoring System**

This diagram shows how SSE transport monitors connection health through heartbeats (detect dead connections), stale detection (timeout inactive sessions), and ping keep-alive (maintain session state), along with event-driven cleanup.

Sources: [packages/app/src/server/transport/sse-transport.ts:28-42](), [packages/app/src/server/transport/base-transport.ts:325-368](), [packages/app/src/server/transport/base-transport.ts:370-407]()

### Heartbeat Implementation

The heartbeat is started per-session when the SSE connection is established:

```typescript
this.startHeartbeat(sessionId, res);
```

The `startHeartbeat()` method (inherited from `StatefulTransport`) writes a comment to the SSE stream periodically and checks if the response is still writable. If not, it triggers session cleanup.

Sources: [packages/app/src/server/transport/sse-transport.ts:137](), [packages/app/src/server/transport/base-transport.ts:325-368]()

### Stale Session Removal

The `removeStaleSession()` method is called by the background stale checker when a session exceeds the timeout:

```typescript
protected async removeStaleSession(sessionId: string): Promise<void> {
    logger.info({ sessionId }, 'Removing stale SSE connection');
    await this.cleanupSession(sessionId);
    
    logSystemEvent('session_delete', sessionId, {
        clientSessionId: sessionId,
    });
}
```

This ensures sessions that have stopped sending messages (but haven't closed the connection) are eventually cleaned up.

Sources: [packages/app/src/server/transport/sse-transport.ts:236-244]()

## Cleanup and Shutdown

### Session Cleanup

Session cleanup is triggered by multiple events:

1. **Client Disconnect**: SSE response `close`, `error`, or `finish` events
2. **Stale Detection**: Session inactive beyond `MCP_CLIENT_CONNECTION_TIMEOUT`
3. **Manual Closure**: `closeConnection()` method call
4. **Shutdown**: `cleanup()` method during server shutdown

The cleanup process:

```typescript
// Inherited cleanupSession() performs:
// 1. Check if already cleaning up (prevents double cleanup)
// 2. Mark session as cleaningUp = true
// 3. Clear heartbeat timer
// 4. Close MCP server
// 5. Close transport
// 6. Delete from sessions Map
// 7. Track session removal metrics
```

Sources: [packages/app/src/server/transport/sse-transport.ts:236-244](), [packages/app/src/server/transport/sse-transport.ts:265-283](), [packages/app/src/server/transport/base-transport.ts:417-475]()

### Global Cleanup

During server shutdown, the `cleanup()` method:

1. Stops the stale connection checker using `stopStaleConnectionCheck()`
2. Calls `cleanupAllSessions()` to close all active sessions
3. Logs completion

```typescript
async cleanup(): Promise<void> {
    logger.info(
        {
            activeConnections: this.sessions.size,
        },
        'Starting SSE transport cleanup'
    );

    this.stopStaleConnectionCheck();
    await this.cleanupAllSessions();

    logger.info('SSE transport cleanup completed');
}
```

Sources: [packages/app/src/server/transport/sse-transport.ts:246-261]()

### Force Close API

The `closeConnection()` method provides a programmatic way to terminate a specific session:

```typescript
async closeConnection(sessionId: string): Promise<boolean> {
    const session = this.sessions.get(sessionId);
    if (!session) {
        return false;
    }

    try {
        await this.cleanupSession(sessionId);
        logSystemEvent('session_delete', sessionId, {
            clientSessionId: sessionId,
        });
        return true;
    } catch (error) {
        logger.error({ error, sessionId }, 'Error closing connection');
        return false;
    }
}
```

This is used during reconnection attempts to clean up old sessions before establishing new ones.

Sources: [packages/app/src/server/transport/sse-transport.ts:266-283]()

## Integration with Base Classes

The SSE transport leverages significant functionality from its parent classes:

### From StatefulTransport

- `sessions: Map<string, SSEConnection>` - Session storage
- `startStaleConnectionCheck()` / `stopStaleConnectionCheck()` - Background monitoring
- `startPingKeepAlive()` - Session ping support
- `cleanupSession(sessionId)` - Individual session cleanup
- `cleanupAllSessions()` - Bulk cleanup during shutdown
- `updateSessionActivity(sessionId)` - Activity timestamp updates
- `setupSseEventHandlers(sessionId, res)` - Response event listeners
- `startHeartbeat(sessionId, res)` - Heartbeat monitoring

Sources: [packages/app/src/server/transport/base-transport.ts:73-475]()

### From BaseTransport

- `trackRequest()` - Request counting
- `trackError(statusCode?, error?)` - Error metrics
- `trackSessionCreated(sessionId)` - Session creation metrics
- `validateAuthAndTrackMetrics(headers)` - Authentication with metrics
- `extractMethodForTracking(body)` - Extract method name from JSON-RPC
- `serverFactory()` - Create MCP server instances
- `metrics` - Metrics collector instance
- `createClientInfoCapture(sessionId)` - Client info tracking

Sources: [packages/app/src/server/transport/base-transport.ts:109-311]()

## Comparison with Other Transports

| Feature | SSE | StreamableHTTP | STDIO |
|---------|-----|----------------|-------|
| Statefulness | Stateful | Stateful | Single session |
| Endpoints | `/sse` + `/message` | `/mcp` (POST/GET/DELETE) | stdin/stdout |
| Session tracking | Query param `sessionId` | Header `mcp-session-id` | N/A |
| Heartbeat | Yes | Yes | No |
| Use case | Legacy support | Modern web clients | CLI tools |
| Deprecation | Being deprecated | Recommended | Active |

The SSE transport is functionally similar to StreamableHTTP but uses separate endpoints for the event stream and messages, whereas StreamableHTTP unifies everything under `/mcp` with different HTTP methods.

Sources: [packages/app/src/server/transport/sse-transport.ts:1-284](), [packages/app/src/server/transport/streamable-http-transport.ts:1-314](), [README.md:127-134]()

---

# Page: HTTP Transports

# HTTP Transports

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [packages/app/src/server/transport/base-transport.ts](packages/app/src/server/transport/base-transport.ts)
- [packages/app/src/server/transport/sse-transport.ts](packages/app/src/server/transport/sse-transport.ts)
- [packages/app/src/server/transport/stateless-http-transport.ts](packages/app/src/server/transport/stateless-http-transport.ts)
- [packages/app/src/server/transport/streamable-http-transport.ts](packages/app/src/server/transport/streamable-http-transport.ts)

</details>



This document covers the two HTTP transport implementations in the HF MCP Server: `StreamableHttpTransport` and `StatelessHttpTransport`. These transports enable web-based clients to connect to the MCP server using standard HTTP protocols. For information about the base transport classes and shared functionality, see [Base Transport Classes](#7.1). For information about the SSE transport which uses a different protocol pattern, see [SSE Transport](#7.3).

## Overview

The HF MCP Server provides two distinct HTTP transport implementations that serve different use cases:

- **StreamableHttpTransport** ([packages/app/src/server/transport/streamable-http-transport.ts]()): A stateful transport that maintains persistent sessions across multiple HTTP requests, suitable for interactive clients
- **StatelessHttpTransport** ([packages/app/src/server/transport/stateless-http-transport.ts]()): A stateless transport that creates fresh server instances per request, with optional analytics session tracking

Both transports use the MCP SDK's `StreamableHTTPServerTransport` internally but differ in their session management strategy and lifecycle.

Sources: [packages/app/src/server/transport/streamable-http-transport.ts:1-18](), [packages/app/src/server/transport/stateless-http-transport.ts:1-39]()

## Transport Comparison

### Feature Matrix

| Feature | StreamableHttpTransport | StatelessHttpTransport |
|---------|------------------------|------------------------|
| **Base Class** | `StatefulTransport` | `BaseTransport` |
| **Session Persistence** | Yes, across requests | No (per-request) |
| **Server Instance** | One per session | One per request |
| **HTTP Methods** | POST, GET, DELETE | POST, DELETE (analytics only) |
| **GET Endpoint** | SSE streaming | Static welcome page |
| **Session Tracking** | Always enabled | Optional (analytics mode) |
| **Memory Footprint** | Higher (persistent servers) | Lower (ephemeral servers) |
| **Stale Detection** | Active monitoring | None |
| **Ping Keep-Alive** | Supported | Not applicable |
| **Best For** | IDEs, interactive clients | Stateless integrations, high volume |

Sources: [packages/app/src/server/transport/streamable-http-transport.ts:18](), [packages/app/src/server/transport/stateless-http-transport.ts:39]()

## StreamableHttpTransport (Stateful)

### Architecture

```mermaid
graph TB
    subgraph "Client Session Lifecycle"
        C1["Client: POST /mcp<br/>(initialize request)"]
        C2["Client: GET /mcp<br/>(open SSE stream)"]
        C3["Client: POST /mcp<br/>(subsequent requests)"]
        C4["Client: DELETE /mcp<br/>(terminate session)"]
    end
    
    subgraph "StreamableHttpTransport"
        Router["setupRoutes()<br/>POST/GET/DELETE /mcp"]
        Handler["handleRequest()"]
        PostHandler["handlePostRequest()"]
        GetHandler["handleGetRequest()"]
        DeleteHandler["handleDeleteRequest()"]
        SessionMap["sessions: Map<string, Session>"]
        CreateSession["createSession()"]
    end
    
    subgraph "Session Management"
        StaleCheck["startStaleConnectionCheck()<br/>every 90s"]
        Heartbeat["startHeartbeat()<br/>every 30s"]
        PingKeepAlive["startPingKeepAlive()<br/>every 30s"]
        CleanupFn["removeSession()<br/>cleanupSession()"]
    end
    
    subgraph "Per-Session Resources"
        Transport["StreamableHTTPServerTransport"]
        Server["McpServer instance"]
        Metadata["SessionMetadata"]
    end
    
    C1 --> Router
    C2 --> Router
    C3 --> Router
    C4 --> Router
    
    Router --> Handler
    Handler --> PostHandler
    Handler --> GetHandler
    Handler --> DeleteHandler
    
    PostHandler --> CreateSession
    CreateSession --> Transport
    CreateSession --> Server
    CreateSession --> Metadata
    CreateSession --> SessionMap
    
    GetHandler --> SessionMap
    GetHandler --> Heartbeat
    
    PostHandler --> SessionMap
    DeleteHandler --> SessionMap
    DeleteHandler --> CleanupFn
    
    StaleCheck --> CleanupFn
    PingKeepAlive --> Server
    
    Transport --> SessionMap
    Server --> SessionMap
    Metadata --> SessionMap
```

Sources: [packages/app/src/server/transport/streamable-http-transport.ts:18-61](), [packages/app/src/server/transport/streamable-http-transport.ts:223-288]()

### Route Structure

The `StreamableHttpTransport` registers three routes on the `/mcp` endpoint:

**POST /mcp** - Request handling
- Creates new sessions (on initialize request with no session ID)
- Routes requests to existing sessions
- Validates session ID presence for non-initialize requests
- Rejects new connections during shutdown

**GET /mcp** - SSE streaming
- Opens Server-Sent Events stream for an existing session
- Requires `mcp-session-id` header
- Sets up heartbeat monitoring to detect stale connections
- Handles connection close/error events

**DELETE /mcp** - Session termination
- Explicitly terminates a session
- Cleans up transport and server resources
- Returns 404 if session not found

Sources: [packages/app/src/server/transport/streamable-http-transport.ts:37-61](), [packages/app/src/server/transport/streamable-http-transport.ts:63-90]()

### Session Creation Flow

```mermaid
sequenceDiagram
    participant Client
    participant PostHandler as "handlePostRequest()"
    participant CreateSession as "createSession()"
    participant Factory as "serverFactory()"
    participant SDK as "StreamableHTTPServerTransport"
    participant Map as "sessions Map"
    
    Client->>PostHandler: POST /mcp (initialize)
    PostHandler->>PostHandler: validateAuthAndTrackMetrics()
    PostHandler->>CreateSession: Create session
    CreateSession->>Factory: serverFactory(headers)
    Factory-->>CreateSession: ServerFactoryResult
    CreateSession->>SDK: new StreamableHTTPServerTransport()
    SDK->>SDK: Generate session ID
    SDK-->>CreateSession: transport with sessionId
    
    CreateSession->>CreateSession: Setup onsessioninitialized callback
    CreateSession->>CreateSession: Setup onclose handler
    CreateSession->>CreateSession: Setup onerror handler
    CreateSession->>CreateSession: Setup oninitialized handler
    CreateSession->>CreateSession: Connect server to transport
    
    SDK->>CreateSession: Trigger onsessioninitialized
    CreateSession->>Map: Store Session object
    CreateSession->>CreateSession: trackSessionCreated()
    
    CreateSession-->>PostHandler: transport
    PostHandler->>SDK: transport.handleRequest()
    SDK-->>Client: Response with Mcp-Session-Id header
```

Sources: [packages/app/src/server/transport/streamable-http-transport.ts:92-170](), [packages/app/src/server/transport/streamable-http-transport.ts:223-288]()

### Session Structure

The `StreamableHttpConnection` interface extends `BaseSession`:

```typescript
interface StreamableHttpConnection extends BaseSession<StreamableHTTPServerTransport> {
    activeResponse?: Response;
}
```

Each session contains:
- `transport`: `StreamableHTTPServerTransport` instance for this session
- `server`: `McpServer` instance with registered tools
- `metadata`: `SessionMetadata` with connection info, activity timestamps, request count
- `heartbeatInterval`: Timer for detecting stale SSE connections
- `activeResponse`: Current SSE response object (when GET endpoint is active)

Sources: [packages/app/src/server/transport/streamable-http-transport.ts:12-16]()

### Stale Connection Management

The stateful transport inherits comprehensive session health monitoring from `StatefulTransport`:

**Stale Checker** (every 90 seconds by default):
- Scans all sessions for inactivity
- Removes sessions with no activity for 10 minutes (default)
- Configurable via `MCP_CLIENT_CONNECTION_CHECK` and `MCP_CLIENT_CONNECTION_TIMEOUT`

**Heartbeat Monitor** (every 30 seconds):
- Checks if SSE response stream is still writable
- Detects client disconnects via `response.destroyed` or `response.writableEnded`
- Automatically cleans up abandoned connections

**Ping Keep-Alive** (every 30 seconds):
- Sends MCP ping messages to all sessions
- Updates `lastActivity` on successful ping
- Increments `pingFailures` counter on failure
- Removes sessions exceeding failure threshold

Sources: [packages/app/src/server/transport/base-transport.ts:360-533](), [packages/app/src/server/transport/streamable-http-transport.ts:19-35]()

## StatelessHttpTransport

### Architecture

```mermaid
graph TB
    subgraph "Client Request Flow"
        Req["POST /mcp<br/>(any JSON-RPC request)"]
        GetReq["GET /mcp<br/>(browser only)"]
        DelReq["DELETE /mcp<br/>(analytics mode)"]
    end
    
    subgraph "StatelessHttpTransport"
        Router["initialize()<br/>POST/GET/DELETE /mcp"]
        PostHandler["handleJsonRpcRequest()"]
        GetHandler["Serve mcp-welcome.html"]
        DeleteHandler["handleDeleteRequest()"]
        AnalyticsMap["analyticsSessions: Map<br/>(analytics mode only)"]
    end
    
    subgraph "Per-Request Processing"
        ValidateAuth["validateAuthAndTrackMetrics()"]
        ShouldHandle["shouldHandle()<br/>Full server vs stub"]
        CreateServer["serverFactory(headers)"]
        CreateTransport["new StreamableHTTPServerTransport"]
        Connect["server.connect(transport)"]
        HandleReq["transport.handleRequest()"]
        Cleanup["Immediate cleanup"]
    end
    
    subgraph "Analytics Mode Optional"
        SessionCheck{"Analytics<br/>enabled?"}
        CreateAnalytics["createAnalyticsSession()"]
        UpdateAnalytics["updateAnalyticsSessionActivity()"]
        TrackMetrics["Track without server"]
    end
    
    Req --> Router
    GetReq --> Router
    DelReq --> Router
    
    Router --> PostHandler
    Router --> GetHandler
    Router --> DeleteHandler
    
    PostHandler --> ValidateAuth
    PostHandler --> SessionCheck
    
    SessionCheck -->|Yes| CreateAnalytics
    SessionCheck -->|Yes| UpdateAnalytics
    SessionCheck -->|No| ShouldHandle
    CreateAnalytics --> AnalyticsMap
    UpdateAnalytics --> AnalyticsMap
    
    ValidateAuth --> ShouldHandle
    ShouldHandle -->|Full server| CreateServer
    ShouldHandle -->|Stub responder| CreateServer
    CreateServer --> CreateTransport
    CreateTransport --> Connect
    Connect --> HandleReq
    HandleReq --> Cleanup
    
    DeleteHandler --> AnalyticsMap
    AnalyticsMap --> TrackMetrics
```

Sources: [packages/app/src/server/transport/stateless-http-transport.ts:91-139](), [packages/app/src/server/transport/stateless-http-transport.ts:141-408]()

### Request Routing

The stateless transport provides three endpoints:

**POST /mcp** - JSON-RPC request handling
- Creates fresh server and transport for each request
- Validates auth with `validateAuthAndTrackMetrics()`
- Determines if full server is needed via `shouldHandle()`
- Supports analytics session tracking (optional)
- Immediate cleanup after response

**GET /mcp** - Static welcome page
- Serves `mcp-welcome.html` for browser clients only
- Returns 405 Method Not Allowed for non-browser clients or when `MCP_STRICT_COMPLIANCE=true`
- Redirects HTTP to HTTPS (except localhost)
- Not part of MCP protocol - UX enhancement

**DELETE /mcp** - Analytics session deletion
- Only available when `ANALYTICS_MODE=true`
- Removes session from analytics tracking
- Returns 404 if session not found
- Returns 405 if analytics disabled

Sources: [packages/app/src/server/transport/stateless-http-transport.ts:91-139](), [packages/app/src/server/transport/stateless-http-transport.ts:410-452]()

### Full Server vs Stub Responder

The `shouldHandle()` method optimizes resource usage by determining which requests need full MCP server initialization:

```mermaid
graph LR
    Request["JSON-RPC Request"]
    Check{"shouldHandle()<br/>check"}
    FullServer["Create Full Server<br/>with all tools"]
    StubServer["Create Stub Server<br/>@huggingface/internal-responder"]
    
    Request --> Check
    Check -->|"tools/list<br/>tools/call<br/>prompts/list<br/>prompts/get<br/>initialize<br/>resources/* (openai-mcp)"| FullServer
    Check -->|"All other methods"| StubServer
```

Methods requiring full server:
- `tools/list`, `tools/call`
- `prompts/list`, `prompts/get`
- `initialize`
- `resources/list`, `resources/read`, `resources/templates/list` (only for `openai-mcp` client)

All other requests (ping, completion, etc.) use a minimal stub responder created with `new McpServer({ name: '@huggingface/internal-responder', version: '0.0.1' })`.

Sources: [packages/app/src/server/transport/stateless-http-transport.ts:64-89](), [packages/app/src/server/transport/stateless-http-transport.ts:290-315]()

### Request Lifecycle

```mermaid
sequenceDiagram
    participant Client
    participant Handler as "handleJsonRpcRequest()"
    participant Auth as "validateAuthAndTrackMetrics()"
    participant Analytics as "Analytics Tracking"
    participant Factory as "serverFactory()"
    participant Transport as "StreamableHTTPServerTransport"
    participant Server as "McpServer"
    participant Cleanup as "Cleanup Logic"
    
    Client->>Handler: POST /mcp
    Handler->>Auth: Validate HF token
    Auth-->>Handler: authResult
    
    alt Analytics Mode
        Handler->>Analytics: Create/update session
        Analytics-->>Handler: sessionId in header
    end
    
    Handler->>Handler: shouldHandle(requestBody)
    
    alt Full Server Needed
        Handler->>Factory: serverFactory(headers)
        Factory-->>Handler: { server, userDetails }
    else Stub Responder
        Handler->>Handler: new McpServer (stub)
    end
    
    Handler->>Transport: new StreamableHTTPServerTransport<br/>(enableJsonResponse=true)
    Handler->>Server: server.connect(transport)
    Handler->>Transport: transport.handleRequest(req, res)
    Transport-->>Client: JSON-RPC response
    
    Handler->>Cleanup: Close transport
    Handler->>Cleanup: Close server
    
    Note over Handler,Cleanup: Resources freed immediately
```

Sources: [packages/app/src/server/transport/stateless-http-transport.ts:141-408]()

### Analytics Mode

When `ANALYTICS_MODE=true`, the stateless transport maintains lightweight session tracking for metrics without persistent server instances:

**Session Initialization**:
- Client sends `initialize` request without `mcp-session-id` header
- Server generates new session ID and returns in `Mcp-Session-Id` response header
- Creates `AnalyticsSession` object: `{ transport: null, server: null, metadata }`

**Session Resumption**:
- Client includes `mcp-session-id` header in subsequent requests
- Server validates session exists and updates activity timestamp
- Returns 404 if session not found (client must reinitialize)

**Session Deletion**:
- Explicit: Client sends `DELETE /mcp` with session ID
- Implicit: No automatic cleanup (sessions persist indefinitely in map)

**Analytics Session Structure**:

```typescript
interface AnalyticsSession {
    transport: null;
    server: null;
    metadata: SessionMetadata;
}
```

The `transport` and `server` fields are always `null` because stateless mode doesn't maintain persistent connections. Only metadata is tracked for analytics purposes.

Sources: [packages/app/src/server/transport/stateless-http-transport.ts:25-30](), [packages/app/src/server/transport/stateless-http-transport.ts:46-59](), [packages/app/src/server/transport/stateless-http-transport.ts:165-245](), [packages/app/src/server/transport/stateless-http-transport.ts:410-452](), [packages/app/src/server/transport/stateless-http-transport.ts:495-528]()

### Temporary Session Resume Logging

The stateless transport includes a diagnostic feature for debugging session resume failures:

**Configuration**:
- `TEMPLOG_MAX`: Maximum number of failures to log (default: 0, disabled)
- Activated via `activateTempLogging(count)` method

**What Gets Logged**:
- Session ID that failed to resume
- Request headers (user-agent, origin, x-forwarded-for, etc.)
- HF token presence (last 5 characters only for security)
- Method being called
- Active session count

**Auto-Disable**:
- Counter decrements with each logged failure
- Automatically disables when counter reaches zero

This feature helps diagnose production issues where clients are failing to resume sessions, without the overhead of always-on verbose logging.

Sources: [packages/app/src/server/transport/stateless-http-transport.ts:42-59](), [packages/app/src/server/transport/stateless-http-transport.ts:196-232](), [packages/app/src/server/transport/stateless-http-transport.ts:535-554]()

## Transport Selection and Configuration

### Environment Variables

Both HTTP transports respect common configuration:

| Variable | Default | Description |
|----------|---------|-------------|
| `ANALYTICS_MODE` | `false` | Enable session tracking in stateless mode |
| `MCP_STRICT_COMPLIANCE` | `false` | Reject GET requests to /mcp (return 405) |
| `TEMPLOG_MAX` | `0` | Max session resume failures to log (stateless only) |

**Stateful Transport Only**:

| Variable | Default | Description |
|----------|---------|-------------|
| `MCP_CLIENT_CONNECTION_CHECK` | `90000` | Stale check interval (ms) |
| `MCP_CLIENT_CONNECTION_TIMEOUT` | `600000` | Session timeout (ms) |
| `MCP_CLIENT_HEARTBEAT_INTERVAL` | `30000` | SSE heartbeat interval (ms) |
| `MCP_PING_ENABLED` | `true` | Enable ping keep-alive |
| `MCP_PING_INTERVAL` | `30000` | Ping interval (ms) |
| `MCP_PING_FAILURE_THRESHOLD` | `1` | Max ping failures before cleanup |

Sources: [packages/app/src/server/transport/base-transport.ts:360-365](), [packages/app/src/server/transport/stateless-http-transport.ts:48-49]()

### Use Cases

**StreamableHttpTransport** is ideal for:
- IDE integrations (VS Code, Cursor) that maintain long-lived connections
- Desktop applications that need persistent state
- Clients that benefit from SSE streaming for real-time updates
- Scenarios where session reuse reduces server initialization overhead

**StatelessHttpTransport** is ideal for:
- Web-based clients that don't maintain WebSocket connections
- Serverless deployments where persistent state is problematic
- High-volume scenarios where per-request isolation prevents resource leaks
- Analytics tracking without the overhead of persistent servers
- When strict HTTP statelessness is required for scaling/load balancing

Sources: [packages/app/src/server/transport/streamable-http-transport.ts:1-35](), [packages/app/src/server/transport/stateless-http-transport.ts:32-39]()

## Implementation Details

### Transport Creation in Stateless Mode

The `StreamableHTTPServerTransport` is configured differently for stateless mode:

```typescript
transport = new StreamableHTTPServerTransport({
    sessionIdGenerator: undefined,  // No session ID generation needed
    enableJsonResponse: directResponse  // true for built-in tools, false for Gradio streaming
});
```

The `directResponse` flag controls whether the transport buffers and returns a single JSON response or streams partial results. For Gradio tool calls (detected via `isGradioToolCall()`), direct response is disabled to allow progress notifications.

Sources: [packages/app/src/server/transport/stateless-http-transport.ts:311-322]()

### Transport Creation in Stateful Mode

The `StreamableHTTPServerTransport` is configured with session callbacks:

```typescript
transport = new StreamableHTTPServerTransport({
    sessionIdGenerator: () => randomUUID(),
    onsessioninitialized: (sessionId: string) => {
        // Create and store Session object
        // Track session creation
        // Log initialize event
    }
});
```

The `onsessioninitialized` callback is triggered by the SDK when the client's initialize request is processed, allowing the transport to create the session entry in its map.

Sources: [packages/app/src/server/transport/streamable-http-transport.ts:229-259]()

### Cleanup Patterns

**Stateful**: Cleanup is deferred and managed by lifecycle hooks
- Heartbeat intervals detect stale SSE connections
- Stale checker removes inactive sessions periodically
- Explicit DELETE request triggers immediate cleanup
- Transport `onclose` handler triggers session removal

**Stateless**: Cleanup is immediate after response
- Resources freed synchronously after `transport.handleRequest()` completes
- Exception: early client disconnect triggers cleanup via `res.on('close')` handler
- No background processes or timers
- In analytics mode, sessions persist in map but don't hold resources

Sources: [packages/app/src/server/transport/streamable-http-transport.ts:261-295](), [packages/app/src/server/transport/stateless-http-transport.ts:324-341]()

### Error Handling

Both transports implement comprehensive error tracking:

**Authentication Errors**:
- 401: Invalid HF token
- WWW-Authenticate header includes OAuth resource hint

**Session Errors**:
- 404: Session not found (stateful mode or analytics resume failure)
- 400: Missing session ID for non-initialize request

**Server Errors**:
- 500: Internal error during request processing
- 503: Server shutting down (stateful mode only)
- 405: Method not allowed (GET on stateless when MCP_STRICT_COMPLIANCE enabled)

All errors are tracked via `this.trackError(statusCode, error)` and returned as JSON-RPC error responses using utilities from `json-rpc-errors.ts`.

Sources: [packages/app/src/server/transport/streamable-http-transport.ts:83-90](), [packages/app/src/server/transport/stateless-http-transport.ts:157-162](), [packages/app/src/server/transport/stateless-http-transport.ts:365-407]()

### Metrics Integration

Both transports inherit metrics tracking from `BaseTransport`:

**Request Metrics**:
- `trackRequest()`: Count total requests received
- `trackNewConnection()`: Count new connections established
- `trackMethodCall()`: Track method execution time and errors

**Session Metrics** (stateful only):
- `trackSessionCreated()`: New session added to map
- `trackSessionDeleted()`: Session removed from map
- `trackSessionCleaned()`: Session cleanup completed
- `updateActiveConnections()`: Current session count

**Authentication Metrics**:
- `trackAuthenticatedConnection()`: Valid HF token provided
- `trackAnonymousConnection()`: No token provided
- `trackUnauthorizedConnection()`: Invalid token provided

The stateless transport also tracks `trackSessionResumeFailed()` when analytics mode is enabled and a client attempts to resume a non-existent session.

Sources: [packages/app/src/server/transport/base-transport.ts:148-185](), [packages/app/src/server/transport/base-transport.ts:576-601](), [packages/app/src/server/transport/stateless-http-transport.ts:192-196]()

---

# Page: Web Interface

# Web Interface

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [packages/app/src/server/application.ts](packages/app/src/server/application.ts)
- [packages/app/src/server/utils/tool-selection-strategy.ts](packages/app/src/server/utils/tool-selection-strategy.ts)
- [packages/app/src/server/web-server.ts](packages/app/src/server/web-server.ts)
- [packages/app/src/shared/bouquet-presets.ts](packages/app/src/shared/bouquet-presets.ts)
- [packages/app/src/web/components/McpMethodsCard.tsx](packages/app/src/web/components/McpMethodsCard.tsx)
- [packages/app/src/web/components/SettingsCopyPage.tsx](packages/app/src/web/components/SettingsCopyPage.tsx)
- [packages/app/src/web/components/StdioTransportMetrics.tsx](packages/app/src/web/components/StdioTransportMetrics.tsx)
- [packages/app/src/web/components/TransportMetricsCard.tsx](packages/app/src/web/components/TransportMetricsCard.tsx)
- [packages/app/src/web/components/bouquets/ToolPresetsCard.tsx](packages/app/src/web/components/bouquets/ToolPresetsCard.tsx)
- [packages/app/src/web/components/data-table-utils.tsx](packages/app/src/web/components/data-table-utils.tsx)
- [packages/app/src/web/components/data-table.tsx](packages/app/src/web/components/data-table.tsx)
- [packages/app/src/web/hooks/useSessionCache.ts](packages/app/src/web/hooks/useSessionCache.ts)
- [packages/app/test/server/utils/tool-selection-strategy.test.ts](packages/app/test/server/utils/tool-selection-strategy.test.ts)

</details>



The Web Interface provides a browser-based dashboard for configuring the MCP server, setting up client connections, and monitoring real-time server metrics. It serves as the primary management interface for both configuration tasks (selecting tools, configuring Gradio endpoints) and operational visibility (viewing active sessions, tracking method call statistics).

For detailed information about API route implementation, see [Web Server and API Endpoints](#8.1). For client setup and tool configuration features, see [Configuration UI](#8.2). For metrics visualization and monitoring features, see [Monitoring Dashboard](#8.3).

---

## Purpose and Scope

The web interface serves three primary functions:

1. **Client Setup**: Provides platform-specific instructions and configuration examples for connecting Claude, VS Code, Cursor, Gemini CLI, and other MCP clients
2. **Tool Configuration**: Enables selection of built-in tools and Gradio Space endpoints through bouquet presets and custom configuration
3. **Real-time Monitoring**: Displays transport metrics, session status, method call statistics, and Gradio endpoint performance

The dashboard is accessible at `http://localhost:<port>` when the server is running and uses hot module replacement (HMR) in development mode for rapid iteration.

Sources: [packages/app/src/web/components/SettingsCopyPage.tsx:1-1143](), [packages/app/src/server/web-server.ts:1-491]()

---

## System Architecture

### Component Structure

```mermaid
graph TB
    subgraph "Browser"
        SettingsCopyPage["SettingsCopyPage<br/>Client Setup Instructions"]
        ToolPresetsCard["ToolPresetsCard<br/>Bouquet Configuration"]
        TransportMetricsCard["TransportMetricsCard<br/>Connection Metrics"]
        McpMethodsCard["McpMethodsCard<br/>Method Call Stats"]
        StdioTransportMetrics["StdioTransportMetrics<br/>STDIO Session Details"]
        StatefulTransportMetrics["StatefulTransportMetrics<br/>Stateful Session Details"]
        StatelessTransportMetrics["StatelessTransportMetrics<br/>Stateless Analytics"]
    end
    
    subgraph "Frontend Data Layer"
        SWR["SWR Hooks<br/>3s Auto-Refresh"]
        useSessionCache["useSessionCache<br/>5min Retention"]
    end
    
    subgraph "Express Backend"
        WebServer["WebServer<br/>Express App"]
        
        subgraph "API Routes"
            TransportRoute["/api/transport<br/>Transport Info"]
            SessionsRoute["/api/sessions<br/>Active Sessions"]
            MetricsRoute["/api/transport-metrics<br/>Method Stats"]
            SettingsRoute["/api/settings<br/>Tool Configuration"]
            GradioRoute["/api/gradio-endpoints<br/>Space Tools"]
        end
        
        StaticFiles["Static File Server<br/>Vite Dev / Prod Build"]
    end
    
    subgraph "State Management"
        Transport["BaseTransport<br/>Session Tracking"]
        McpApiClient["McpApiClient<br/>Tool State Manager"]
        settingsService["settingsService<br/>User Settings"]
        Metrics["apiMetrics<br/>gradioMetrics"]
    end
    
    SettingsCopyPage --> SWR
    ToolPresetsCard --> SWR
    TransportMetricsCard --> SWR
    McpMethodsCard --> SWR
    
    SWR --> TransportRoute
    SWR --> SessionsRoute
    SWR --> MetricsRoute
    SWR --> SettingsRoute
    SWR --> GradioRoute
    
    StdioTransportMetrics --> useSessionCache
    StatefulTransportMetrics --> useSessionCache
    
    TransportRoute --> WebServer
    SessionsRoute --> WebServer
    MetricsRoute --> WebServer
    SettingsRoute --> WebServer
    GradioRoute --> WebServer
    
    WebServer --> Transport
    WebServer --> McpApiClient
    WebServer --> settingsService
    WebServer --> Metrics
    
    StaticFiles --> WebServer
```

**Diagram: Web Interface Component Architecture**

The web interface follows a traditional client-server architecture with React components on the frontend communicating with Express API routes on the backend. The `SWR` library handles data fetching with automatic 3-second refresh intervals, while the backend `WebServer` class coordinates access to transport state, settings, and metrics collectors.

Sources: [packages/app/src/web/components/SettingsCopyPage.tsx:1-50](), [packages/app/src/web/components/TransportMetricsCard.tsx:1-72](), [packages/app/src/web/components/McpMethodsCard.tsx:1-298](), [packages/app/src/server/web-server.ts:21-149]()

---

### Request Flow and Data Refresh

```mermaid
sequenceDiagram
    participant Browser
    participant SWR as SWR Cache
    participant API as Express Routes
    participant State as Backend State
    
    rect rgb(240, 248, 255)
        Note over Browser,State: Initial Load
        Browser->>SWR: Component mount
        SWR->>API: GET /api/transport-metrics
        API->>State: transport.getMetrics()
        State-->>API: TransportMetrics
        API-->>SWR: JSON Response
        SWR-->>Browser: Display metrics
    end
    
    rect rgb(255, 250, 240)
        Note over Browser,State: Auto-Refresh (Every 3s)
        loop Every 3 seconds
            SWR->>API: GET /api/transport-metrics
            API->>State: transport.getMetrics()
            State-->>API: Updated metrics
            API-->>SWR: JSON Response
            SWR-->>Browser: Update UI
        end
    end
    
    rect rgb(240, 255, 240)
        Note over Browser,State: Configuration Change
        Browser->>API: POST /api/settings
        API->>State: settingsService.updateBuiltInTools()
        State->>State: emit('toolStateChange')
        State-->>API: Updated settings
        API-->>Browser: Confirmation
        Browser->>SWR: Revalidate cache
    end
```

**Diagram: Data Flow and Refresh Cycle**

The frontend uses `useSWR` hooks with a 3-second refresh interval to poll API endpoints. Configuration changes trigger immediate updates via POST requests, followed by cache revalidation to reflect the new state. The `useSessionCache` hook retains disconnected session information for 5 minutes to provide visibility into recently terminated connections.

Sources: [packages/app/src/web/components/McpMethodsCard.tsx:36-40](), [packages/app/src/web/components/TransportMetricsCard.tsx:20-26](), [packages/app/src/web/hooks/useSessionCache.ts:23-111](), [packages/app/src/server/web-server.ts:381-413]()

---

## Web Server Implementation

### WebServer Class Structure

The `WebServer` class in [packages/app/src/server/web-server.ts:21-491]() manages the Express application lifecycle and coordinates access to backend state.

| Property | Type | Purpose |
|----------|------|---------|
| `app` | `Express` | Express application instance |
| `server` | `Server \| null` | HTTP server instance |
| `transportInfo` | `TransportInfo` | Transport configuration and status |
| `transport` | `BaseTransport` | Active transport for session access |
| `apiClient` | `McpApiClient` | Tool state management client |
| `localSharedToolStates` | `Map<string, boolean>` | Tool enable/disable tracking |

**Key Methods:**

- `setupMiddleware()` - Configures CORS, security headers, body parsing
- `setupApiRoutes()` - Registers API endpoints
- `setupStaticFiles()` - Configures Vite dev server or static file serving
- `start(port)` - Starts the HTTP server
- `initializeToolStates()` - Initializes tool state tracking

Sources: [packages/app/src/server/web-server.ts:21-149]()

---

### API Endpoint Mapping

```mermaid
graph LR
    subgraph "Configuration Endpoints"
        GET_transport["/api/transport<br/>GET"]
        GET_settings["/api/settings<br/>GET"]
        POST_settings["/api/settings<br/>POST"]
        GET_gradio["/api/gradio-endpoints<br/>GET"]
        POST_gradio["/api/gradio-endpoints/:index<br/>POST"]
        PUT_gradio["/api/gradio-endpoints/:index<br/>PUT"]
    end
    
    subgraph "Monitoring Endpoints"
        GET_sessions["/api/sessions<br/>GET"]
        GET_metrics["/api/transport-metrics<br/>GET"]
    end
    
    subgraph "Backend State"
        transportInfo["transportInfo<br/>TransportInfo"]
        transport["transport<br/>BaseTransport"]
        settingsService["settingsService"]
        apiClient["apiClient<br/>McpApiClient"]
        metrics["apiMetrics<br/>gradioMetrics"]
    end
    
    GET_transport --> transportInfo
    GET_sessions --> transport
    GET_metrics --> transport
    GET_metrics --> metrics
    
    GET_settings --> settingsService
    POST_settings --> settingsService
    POST_settings --> apiClient
    
    GET_gradio --> apiClient
    POST_gradio --> apiClient
    PUT_gradio --> apiClient
```

**Diagram: API Route to Backend State Mapping**

Each API endpoint is implemented as an Express route handler in `setupApiRoutes()` and accesses specific backend state objects. Configuration endpoints modify state and emit events, while monitoring endpoints provide read-only access to current metrics.

Sources: [packages/app/src/server/web-server.ts:223-489]()

---

### API Endpoint Details

| Endpoint | Method | Purpose | Response Type |
|----------|--------|---------|---------------|
| `/api/transport` | GET | Returns transport type, port, token status | `TransportInfo` |
| `/api/sessions` | GET | Lists active and recent sessions | `SessionData[]` |
| `/api/transport-metrics` | GET | Method statistics, session details, Gradio metrics | `TransportMetricsResponse` |
| `/api/settings` | GET | Current built-in tools and space tools | `AppSettings` |
| `/api/settings` | POST | Updates tool configuration, emits events | `AppSettings` |
| `/api/gradio-endpoints` | GET | Lists configured Gradio Space endpoints | `GradioEndpoint[]` |
| `/api/gradio-endpoints/:index` | POST | Enables/disables a Gradio endpoint | `GradioEndpoint` |
| `/api/gradio-endpoints/:index` | PUT | Updates Gradio endpoint metadata | `GradioEndpoint` |

**Query Parameters:**

The `/api/transport-metrics` endpoint accepts an optional `?templog=<count>` parameter for stateless transports to temporarily enable session logging for debugging.

Sources: [packages/app/src/server/web-server.ts:225-489]()

---

## Frontend Components

### Component Hierarchy

```mermaid
graph TB
    App["App.tsx<br/>Root Component"]
    
    SettingsCopyPage["SettingsCopyPage<br/>Main Configuration Page"]
    ToolPresetsCard["ToolPresetsCard<br/>Bouquet Selection"]
    
    TransportMetricsCard["TransportMetricsCard<br/>Metrics Router"]
    StdioMetrics["StdioTransportMetrics<br/>STDIO Sessions"]
    StatefulMetrics["StatefulTransportMetrics<br/>Stateful Sessions"]
    StatelessMetrics["StatelessTransportMetrics<br/>Stateless Stats"]
    
    McpMethodsCard["McpMethodsCard<br/>Method Call Table"]
    DataTable["DataTable<br/>Sortable Grid"]
    
    App --> SettingsCopyPage
    SettingsCopyPage --> ToolPresetsCard
    
    App --> TransportMetricsCard
    TransportMetricsCard --> StdioMetrics
    TransportMetricsCard --> StatefulMetrics
    TransportMetricsCard --> StatelessMetrics
    
    App --> McpMethodsCard
    McpMethodsCard --> DataTable
    
    StdioMetrics --> DataTable
    StatefulMetrics --> DataTable
```

**Diagram: React Component Hierarchy**

The UI is organized into three main sections: client setup instructions (`SettingsCopyPage`), transport metrics visualization (`TransportMetricsCard` with transport-specific child components), and method call statistics (`McpMethodsCard`). The `DataTable` component provides reusable sortable, filterable tables.

Sources: [packages/app/src/web/components/SettingsCopyPage.tsx:835-1143](), [packages/app/src/web/components/TransportMetricsCard.tsx:19-72](), [packages/app/src/web/components/McpMethodsCard.tsx:31-298]()

---

### Client Configuration Display

The `SettingsCopyPage` component [packages/app/src/web/components/SettingsCopyPage.tsx:835-1143]() provides client-specific setup instructions with collapsible configuration sections.

**Client Configurations:**

| Client ID | Name | Integration Method | Manual Config |
|-----------|------|-------------------|---------------|
| `claude` | Claude Desktop and Claude.ai | OAuth via connectors | N/A |
| `vscode` | Visual Studio Code | Deep link / settings.json | Bearer token in headers |
| `cursor` | Cursor | Deep link / mcp.json | Bearer token in headers |
| `lm-studio` | LM Studio | Deep link | Bearer token in headers |
| `gemini-cli` | Gemini CLI | CLI command | Extension install |
| `claude-code` | Claude Code | CLI command | Bearer token in headers |
| `codex-cli` | Codex CLI | config.toml | npx mcp-remote |

**Instruction Step Types:**

The `InstructionStep` interface [packages/app/src/web/components/SettingsCopyPage.tsx:28-33]() supports multiple step types:
- `text` - Plain text instructions
- `code` - Copyable code blocks
- `button` - Action buttons (copy, download, external link)
- `warning` - Warning messages with AlertTriangle icon
- `info` - Info messages with Info icon

Sources: [packages/app/src/web/components/SettingsCopyPage.tsx:28-833]()

---

### Tool Preset Configuration

The `ToolPresetsCard` component [packages/app/src/web/components/bouquets/ToolPresetsCard.tsx:141-226]() displays available bouquet presets organized by category.

**Bouquet Preset Structure:**

```typescript
interface BouquetPreset {
    key: BouquetKey;              // "search", "hf_api", "spaces", etc.
    label: string;                // Display name
    description: string;          // Purpose description
    category: 'core' | 'advanced';
    supportsBouquet: boolean;     // Can use ?bouquet= parameter
    supportsMix: boolean;         // Can use ?mix= parameter
    builtInTools: readonly string[];
    directParams?: DirectParamOption[];
}
```

**URL Generation:**

Each preset generates URLs with appropriate query parameters:
- **Bouquet Override**: `https://huggingface.co/mcp?login&bouquet=search`
- **Mix Mode**: `https://huggingface.co/mcp?login&mix=docs`
- **Direct Parameters**: `https://huggingface.co/mcp?login&no_image_content=true`

The component uses `describeConfigEntry()` [packages/app/src/shared/bouquet-presets.ts:260-282]() to map tool IDs to human-readable descriptions and distinguish between tools and behavior flags.

Sources: [packages/app/src/web/components/bouquets/ToolPresetsCard.tsx:1-227](), [packages/app/src/shared/bouquet-presets.ts:69-283]()

---

### Metrics Visualization

The metrics display system routes to transport-specific components based on the active transport type.

**Routing Logic:**

[packages/app/src/web/components/TransportMetricsCard.tsx:61-70]() implements conditional rendering:

```typescript
if (metrics.transport === 'stdio') {
    return <StdioTransportMetrics metrics={metrics} />;
}
if (metrics.isStateless) {
    return <StatelessTransportMetrics metrics={metrics} />;
}
return <StatefulTransportMetrics metrics={metrics} />;
```

**Session Display Features:**

The `useSessionCache` hook [packages/app/src/web/hooks/useSessionCache.ts:30-111]() maintains a 5-minute retention window for disconnected sessions:

1. **Active sessions** are updated continuously from API responses
2. **Disconnected sessions** are marked with `disconnectedAt` timestamp
3. **Expired sessions** (disconnected > 5 minutes) are removed via cleanup interval
4. **Connection status** is determined by recent activity and ping failures

| Status | Criteria |
|--------|----------|
| Connected | Activity within 5 minutes, no ping failures |
| Distressed | Recent activity but ≥1 ping failures |
| Disconnected | No activity within 5 minutes |

Sources: [packages/app/src/web/components/TransportMetricsCard.tsx:19-72](), [packages/app/src/web/hooks/useSessionCache.ts:1-112](), [packages/app/src/web/components/StdioTransportMetrics.tsx:1-181]()

---

### Method Call Statistics

The `McpMethodsCard` component [packages/app/src/web/components/McpMethodsCard.tsx:31-298]() displays detailed method call statistics with Gradio-specific enrichment.

**Data Processing Pipeline:**

1. **Fetch metrics** from `/api/transport-metrics` with SWR auto-refresh
2. **Enrich with Gradio data** by matching tool names to `gradioMetrics.byTool`
3. **Calculate combined error rates** including both transport and Gradio failures
4. **Filter optionally** to show only `tools/call` and `prompts/get` methods

**Column Definitions:**

| Column | Display | Sort Key |
|--------|---------|----------|
| Method | Colored syntax highlighting for tool/prompt calls | `method` |
| Calls | Total invocation count | `count` |
| Errors | Combined transport + Gradio errors in red | `errors` |
| Success/Failure | Gradio-specific success/failure breakdown | `gradioMetrics` |
| Error Rate | Percentage with red highlighting | `errorRate` |
| Avg Response | Milliseconds (stateless only) | `averageResponseTime` |
| Last Called | Relative time | `lastCalled` |

**Gradio Metrics Integration:**

[packages/app/src/web/components/McpMethodsCard.tsx:46-82]() merges Gradio metrics by extracting the tool name from `tools/call:toolName` and looking up corresponding success/failure counts in `metrics.gradioMetrics.byTool`.

Sources: [packages/app/src/web/components/McpMethodsCard.tsx:1-298]()

---

## Development and Production Modes

### Static File Serving

The `setupStaticFiles()` method [packages/app/src/server/web-server.ts:182-221]() configures different behaviors for development and production:

**Development Mode** (`NODE_ENV=development`):
- Creates Vite dev server with middleware mode
- Enables HMR (Hot Module Replacement)
- Serves from `packages/app/src/web` source directory
- Auto-rebuilds on file changes

**Production Mode**:
- Serves pre-built static files from `dist/web`
- Implements SPA fallback routing to `index.html`
- Skips fallback for `/api/*` routes

```typescript
if (isDevelopment) {
    const vite = await createViteServer({
        configFile: path.resolve(__dirname, '..', '..', '..', 'app', 'vite.config.ts'),
        server: { middlewareMode: true, hmr: true },
        appType: 'spa',
        root: rootDir,
    });
    this.app.use(vite.middlewares);
} else {
    const staticPath = path.join(__dirname, '..', 'web');
    this.app.use(express.static(staticPath));
    this.app.get('*', (req, res) => {
        if (!req.path.startsWith('/api/')) {
            res.sendFile(path.join(staticPath, 'index.html'));
        }
    });
}
```

Sources: [packages/app/src/server/web-server.ts:182-221]()

---

### CORS Configuration

CORS is configured in `setupMiddleware()` [packages/app/src/server/web-server.ts:39-115]() with support for exact-match allowlists and wildcard patterns:

**Supported Origin Formats:**
- **Exact match**: `https://huggingface.co`
- **Wildcard**: `*` (allows all origins)
- **Subdomain wildcard**: `https://*.use-mcp.dev` or `*.use-mcp.dev`

**Environment Override:**

The `CORS_ALLOWED_ORIGINS` environment variable accepts comma-separated origins:
```bash
CORS_ALLOWED_ORIGINS=https://example.com,https://*.custom-domain.com
```

**Exposed Headers:**

The `CORS_EXPOSED_HEADERS` constant [packages/app/src/shared/constants.ts]() defines which headers are accessible to client code. This includes custom MCP headers like `x-mcp-bouquet` and `x-mcp-gradio`.

Sources: [packages/app/src/server/web-server.ts:39-115]()

---

## Integration with Backend State

### Tool State Management

Tool state changes flow through the `WebServer` to all active MCP server instances via the `McpApiClient` event system.

**State Change Flow:**

```mermaid
sequenceDiagram
    participant UI as Web UI
    participant API as POST /api/settings
    participant WebServer
    participant apiClient as McpApiClient
    participant McpServers as MCP Server Instances
    
    UI->>API: Update builtInTools
    API->>WebServer: settingsService.updateBuiltInTools()
    WebServer->>WebServer: localSharedToolStates.set(toolId, enabled)
    WebServer->>apiClient: emit('toolStateChange', toolId, enabled)
    apiClient->>McpServers: toolStateChange event
    McpServers->>McpServers: Update tool availability
```

**Diagram: Tool State Propagation**

When a user modifies tool settings through the web UI, the change is persisted to `settingsService` and broadcast to all connected MCP clients via the `toolStateChange` event. The `localSharedToolStates` map tracks previous states to avoid redundant event emissions.

Sources: [packages/app/src/server/web-server.ts:381-413]()

---

### Session Tracking Integration

Session data flows from the transport layer through the `WebServer` to the frontend via the `/api/sessions` endpoint.

**For STDIO Transport:**

[packages/app/src/server/web-server.ts:230-251]() includes special logic to update `stdioClient` info from session data:

```typescript
if (this.transportInfo.transport === 'stdio' && sessions.length > 0) {
    const stdioSession = sessions[0];
    if (stdioSession?.clientInfo && !this.transportInfo.stdioClient) {
        this.transportInfo.stdioClient = {
            name: stdioSession.clientInfo.name,
            version: stdioSession.clientInfo.version,
        };
    }
}
```

This ensures that client information is displayed in the UI even though STDIO doesn't maintain persistent HTTP sessions.

**For HTTP Transports:**

The `/api/sessions` endpoint calls `transport.getSessions()` which returns an array of session objects with:
- Session ID
- Connection timestamp
- Last activity timestamp
- Request count
- Client info (name, version)
- Connection status (Connected/Distressed/Disconnected)
- Ping statistics

Sources: [packages/app/src/server/web-server.ts:230-251]()

---

### Metrics Collection

The `/api/transport-metrics` endpoint [packages/app/src/server/web-server.ts:254-373]() aggregates data from multiple sources:

**Metrics Sources:**

| Source | Data Type | Purpose |
|--------|-----------|---------|
| `transport.getMetrics()` | Method call stats, session data | Transport-level metrics |
| `apiMetrics.getMetrics()` | External API call performance | API client metrics (external mode only) |
| `gradioMetrics.getMetrics()` | Gradio endpoint success/failure | Space tool execution metrics |
| `formatCacheMetricsForAPI()` | Cache hit rates, invalidations | Gradio subdomain cache performance |

**Response Structure:**

```typescript
interface TransportMetricsResponse {
    transport: TransportType;
    isStateless: boolean;
    uptimeSeconds: number;
    startupTime: string;
    sessions: SessionData[];
    methods: MethodMetric[];
    configuration?: TransportConfiguration;
    apiMetrics?: ApiMetricsData;
    gradioMetrics: GradioMetricsData;
    gradioCacheMetrics: CacheMetricsData;
    tempLogStatus?: TempLogStatus;  // Stateless only
}
```

The response is formatted by `formatMetricsForAPI()` [packages/app/src/shared/transport-metrics.ts]() which normalizes the structure across different transport types.

Sources: [packages/app/src/server/web-server.ts:254-373]()

---

## DataTable Component

The `DataTable` component [packages/app/src/web/components/data-table.tsx:35-163]() provides reusable table functionality with sorting, filtering, pagination, and column visibility controls.

**Props Interface:**

```typescript
interface DataTableProps<TData, TValue> {
    columns: ColumnDef<TData, TValue>[];
    data: TData[];
    searchColumn?: string;
    searchPlaceholder?: string;
    defaultColumnVisibility?: VisibilityState;
    pageSize?: number;
    defaultSorting?: SortingState;
}
```

**Features:**
- **TanStack Table**: Uses `@tanstack/react-table` for table state management
- **Column filtering**: Search box filters specified column
- **Column visibility**: Dropdown menu to show/hide columns
- **Sorting**: Click headers to toggle sort direction
- **Pagination**: Previous/Next buttons with configurable page size
- **Responsive**: Displays row count and page controls

**Sortable Headers:**

The `createSortableHeader()` utility [packages/app/src/web/components/data-table-utils.tsx:6-26]() generates header components with sort indicators:

```typescript
createSortableHeader(title: string, align?: 'left' | 'right' | 'center')
```

This displays chevron icons (▲/▼) to indicate current sort direction and allows click-to-sort functionality.

Sources: [packages/app/src/web/components/data-table.tsx:1-164](), [packages/app/src/web/components/data-table-utils.tsx:6-26]()

---

## Summary

The Web Interface provides a comprehensive dashboard for managing and monitoring the HF MCP Server through a React-based frontend and Express backend. Key capabilities include:

1. **Client Setup**: Platform-specific configuration instructions with copy-paste examples
2. **Tool Configuration**: Bouquet presets and direct URL parameter builders
3. **Real-time Monitoring**: Auto-refreshing metrics with 3-second polling intervals
4. **Session Tracking**: 5-minute retention window for disconnected sessions
5. **Gradio Integration**: Success/failure metrics merged into method call statistics

The architecture separates concerns cleanly with `WebServer` managing state access, React components handling presentation, and SWR providing efficient data fetching with automatic cache management. Development mode supports HMR for rapid iteration while production mode serves optimized static builds.

Sources: [packages/app/src/server/web-server.ts:1-491](), [packages/app/src/server/application.ts:99-170]()

---

# Page: Web Server and API Endpoints

# Web Server and API Endpoints

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [packages/app/src/server/application.ts](packages/app/src/server/application.ts)
- [packages/app/src/server/web-server.ts](packages/app/src/server/web-server.ts)

</details>



## Purpose and Scope

This document describes the `WebServer` class and its Express-based HTTP server infrastructure, which serves three primary functions:

1. **API endpoints** for monitoring and configuration (transport metrics, sessions, settings)
2. **Static file serving** for the web dashboard UI
3. **Transport route registration** for MCP protocol communication

For information about the web UI components that consume these APIs, see [Configuration UI](#8.2) and [Monitoring Dashboard](#8.3). For details on the transport implementations that register routes on this server, see [Transport Layer Architecture](#3.4).

---

## WebServer Class Architecture

The `WebServer` class ([packages/app/src/server/web-server.ts:21-490]()) is the central HTTP server component that provides Express infrastructure for both the MCP protocol transports and the web dashboard.

### Core Responsibilities

| Responsibility | Description | Key Methods |
|----------------|-------------|-------------|
| **HTTP Server Management** | Creates and manages the Express app and HTTP server lifecycle | `start()`, `stop()`, `getApp()` |
| **Middleware Setup** | Configures CORS, security headers, body parsing | `setupMiddleware()` |
| **API Route Registration** | Exposes REST endpoints for monitoring and configuration | `setupApiRoutes()` |
| **Static File Serving** | Serves web UI in production, integrates Vite in development | `setupStaticFiles()` |
| **State Management** | Tracks transport info, tool states, and coordinates with ApiClient | `setTransportInfo()`, `setTransport()`, `setApiClient()` |

### Integration with Application Layer

```mermaid
graph TB
    Application["Application"]
    WebServer["WebServer"]
    Express["Express App"]
    Transport["BaseTransport"]
    ApiClient["McpApiClient"]
    settingsService["settingsService"]
    
    Application -->|"creates"| WebServer
    Application -->|"calls setupApiRoutes()"| WebServer
    Application -->|"calls setupStaticFiles()"| WebServer
    Application -->|"calls start()"| WebServer
    Application -->|"setTransport()"| WebServer
    Application -->|"setApiClient()"| WebServer
    
    WebServer -->|"manages"| Express
    WebServer -->|"stores reference"| Transport
    WebServer -->|"stores reference"| ApiClient
    WebServer -->|"reads/writes"| settingsService
    
    Transport -->|"registers routes on"| Express
    ApiClient -->|"provides Gradio endpoints"| WebServer
    ApiClient -->|"receives toolStateChange events"| WebServer
```

**Sources:** [packages/app/src/server/web-server.ts:21-37](), [packages/app/src/server/application.ts:23-31]()

---

## Middleware Stack

The middleware is configured in the constructor via `setupMiddleware()` and processes all incoming requests before they reach route handlers.

### Middleware Execution Order

```mermaid
flowchart TD
    Request["HTTP Request"]
    PoweredBy["Disable x-powered-by"]
    TrustProxy["Trust Proxy Headers"]
    BodyParser["Body Parser<br/>1MB limit"]
    SecurityHeaders["Security Headers<br/>X-Content-Type-Options<br/>Referrer-Policy<br/>HSTS optional"]
    CORS["CORS Handler<br/>Origin validation<br/>Exposed headers"]
    PreflightOptions["OPTIONS Preflight<br/>Wildcard handler"]
    RouteHandler["Route Handler<br/>API or Transport"]
    
    Request --> PoweredBy
    PoweredBy --> TrustProxy
    TrustProxy --> BodyParser
    BodyParser --> SecurityHeaders
    SecurityHeaders --> CORS
    CORS --> PreflightOptions
    PreflightOptions --> RouteHandler
```

**Sources:** [packages/app/src/server/web-server.ts:39-115]()

### CORS Configuration

The CORS middleware supports three modes of origin validation:

| Mode | Configuration | Use Case |
|------|---------------|----------|
| **Wildcard** | `CORS_ALLOWED_ORIGINS="*"` | Development or public APIs |
| **Subdomain Wildcards** | `https://*.use-mcp.dev` | Multi-tenant deployments |
| **Exact Match** | `https://app.example.com` | Production with known origins |

The origin validation logic ([packages/app/src/server/web-server.ts:59-105]()):

1. Reads `CORS_ALLOWED_ORIGINS` environment variable (comma-separated)
2. Falls back to `CORS_ALLOWED_ORIGINS` constant from [packages/app/src/shared/constants.ts]()
3. Normalizes origins by removing trailing slashes
4. For patterns containing `*`, implements custom validation function
   - Supports leading wildcard: `*.domain.tld`
   - Validates scheme (http/https) if specified in pattern
   - Checks if request origin's hostname ends with the wildcard suffix

Example wildcard validation:
```
Pattern: "https://*.use-mcp.dev"
Matches: "https://demo.use-mcp.dev" ✓
Matches: "https://staging.use-mcp.dev" ✓
Rejects: "https://use-mcp.dev" ✗ (no subdomain)
Rejects: "http://demo.use-mcp.dev" ✗ (scheme mismatch)
```

Exposed headers are configured via `CORS_EXPOSED_HEADERS` constant ([packages/app/src/server/web-server.ts:14](), [packages/app/src/server/web-server.ts:109]()).

**Sources:** [packages/app/src/server/web-server.ts:57-115]()

### Security Headers

Basic security headers are applied to all responses ([packages/app/src/server/web-server.ts:46-53]()):

```
X-Content-Type-Options: nosniff
Referrer-Policy: no-referrer
Strict-Transport-Security: max-age=31536000; includeSubDomains (if HSTS=true)
```

The HSTS header is only added when `HSTS=true` environment variable is set, allowing deployment behind reverse proxies that handle TLS termination.

**Sources:** [packages/app/src/server/web-server.ts:46-53]()

### Body Parsing

JSON body parsing is configured with a 1MB limit to prevent abuse ([packages/app/src/server/web-server.ts:43]()):

```typescript
this.app.use(express.json({ limit: '1mb' }));
```

This limit applies to all POST/PUT requests to API and transport endpoints.

**Sources:** [packages/app/src/server/web-server.ts:43]()

---

## API Endpoints

All API endpoints are registered in `setupApiRoutes()` ([packages/app/src/server/web-server.ts:223-489]()) and use the `/api/` prefix to distinguish them from transport routes and static files.

### API Route Map

```mermaid
graph LR
    subgraph "Read-Only Endpoints"
        GET_transport["/api/transport<br/>GET"]
        GET_sessions["/api/sessions<br/>GET"]
        GET_metrics["/api/transport-metrics<br/>GET"]
        GET_settings["/api/settings<br/>GET"]
        GET_gradio["/api/gradio-endpoints<br/>GET"]
    end
    
    subgraph "Write Endpoints"
        POST_settings["/api/settings<br/>POST"]
        POST_gradio_status["/api/gradio-endpoints/:index<br/>POST"]
        PUT_gradio["/api/gradio-endpoints/:index<br/>PUT"]
    end
    
    subgraph "Data Sources"
        transportInfo["transportInfo<br/>TransportInfo"]
        transport["transport<br/>BaseTransport"]
        settingsService["settingsService"]
        apiClient["apiClient<br/>McpApiClient"]
    end
    
    GET_transport -->|"reads"| transportInfo
    GET_sessions -->|"getSessions()"| transport
    GET_metrics -->|"getMetrics()<br/>getConfiguration()"| transport
    GET_settings -->|"getSettings()"| settingsService
    GET_gradio -->|"getGradioEndpoints()"| apiClient
    
    POST_settings -->|"updateBuiltInTools()<br/>updateSpaceTools()"| settingsService
    POST_settings -->|"emit toolStateChange"| apiClient
    POST_gradio_status -->|"updateGradioEndpointState()"| apiClient
    PUT_gradio -->|"updateGradioEndpoint()"| apiClient
```

**Sources:** [packages/app/src/server/web-server.ts:223-489]()

### Transport Info Endpoint

**Route:** `GET /api/transport`

Returns the current transport configuration and server state.

**Response Schema:**
```typescript
{
  transport: 'stdio' | 'sse' | 'streamableHttp' | 'streamableHttpJson' | 'unknown',
  port?: number,
  defaultHfTokenSet: boolean,
  hfTokenMasked?: string,
  jsonResponseEnabled?: boolean,
  externalApiMode: boolean,
  stdioClient?: { name: string, version: string } | null
}
```

The `transportInfo` object is updated by the `Application` class during initialization and can be modified via `setTransportInfo()` and `setClientInfo()` methods.

**Sources:** [packages/app/src/server/web-server.ts:226-228](), [packages/app/src/server/web-server.ts:121-127](), [packages/app/src/server/web-server.ts:146-148]()

### Sessions Endpoint

**Route:** `GET /api/sessions`

Returns active MCP sessions from the transport layer. For STDIO transport, also updates `stdioClient` info in `transportInfo` if available.

**Response:** Array of session objects from `transport.getSessions()`

**Special Behavior for STDIO:** If a STDIO session exists and contains `clientInfo`, it's copied to `transportInfo.stdioClient` ([packages/app/src/server/web-server.ts:240-248]()).

**Sources:** [packages/app/src/server/web-server.ts:231-251]()

### Transport Metrics Endpoint

**Route:** `GET /api/transport-metrics?templog=<count>`

The most complex API endpoint, providing comprehensive metrics about transport performance, active sessions, and Gradio operations.

#### Query Parameters

| Parameter | Type | Description | Transport |
|-----------|------|-------------|-----------|
| `templog` | number | Activates temporary session logging for N requests | `streamableHttpJson` only |

#### Response Structure

```mermaid
graph TB
    Response["API Response"]
    
    subgraph "Core Metrics"
        CoreMetrics["Core Metrics<br/>from transport.getMetrics()"]
        Formatted["formatMetricsForAPI()"]
    end
    
    subgraph "Session Data"
        Sessions["sessions[]<br/>Active connections"]
        SessionStatus["connectionStatus<br/>Connected/Distressed/Disconnected"]
    end
    
    subgraph "Configuration"
        Config["configuration<br/>heartbeat/stale/ping settings"]
    end
    
    subgraph "Additional Metrics"
        APIMetrics["apiMetrics<br/>if externalApiMode"]
        GradioMetrics["gradioMetrics"]
        CacheMetrics["gradioCacheMetrics"]
        TempLog["tempLogStatus<br/>if streamableHttpJson"]
    end
    
    Response --> CoreMetrics
    CoreMetrics --> Formatted
    Response --> Sessions
    Sessions --> SessionStatus
    Response --> Config
    Response --> APIMetrics
    Response --> GradioMetrics
    Response --> CacheMetrics
    Response --> TempLog
```

#### Session Status Determination

Each session includes a `connectionStatus` field calculated based on activity and health ([packages/app/src/server/web-server.ts:296-322]()):

```
if (!hasRecentActivity within 5 minutes):
  status = "Disconnected"
else if (pingFailures >= 1):
  status = "Distressed"
else:
  status = "Connected"
```

#### Metrics Aggregation Flow

```mermaid
sequenceDiagram
    participant Client
    participant Endpoint as "/api/transport-metrics"
    participant Transport
    participant apiMetrics
    participant gradioMetrics
    participant gradioCache
    participant Formatter as "formatMetricsForAPI()"
    
    Client->>Endpoint: GET with optional ?templog=N
    
    opt Temporary Logging Activation
        Endpoint->>Transport: activateTempLogging(N)
        Transport-->>Endpoint: remaining count
    end
    
    Endpoint->>Transport: getMetrics()
    Transport-->>Endpoint: raw metrics
    
    Endpoint->>Transport: getConfiguration()
    Transport-->>Endpoint: config
    
    Endpoint->>Transport: getSessions()
    Transport-->>Endpoint: session array
    
    Endpoint->>Formatter: formatMetricsForAPI(metrics, transport, isStateless, sessions)
    Formatter-->>Endpoint: formatted metrics
    
    opt External API Mode
        Endpoint->>apiMetrics: getMetrics()
        apiMetrics-->>Endpoint: API call stats
    end
    
    Endpoint->>gradioMetrics: getMetrics()
    gradioMetrics-->>Endpoint: Gradio stats
    
    Endpoint->>gradioCache: formatCacheMetricsForAPI()
    gradioCache-->>Endpoint: cache stats
    
    Endpoint-->>Client: Complete metrics JSON
```

**Sources:** [packages/app/src/server/web-server.ts:254-373]()

### Settings Endpoints

#### Get Settings

**Route:** `GET /api/settings`

Returns current user settings from `settingsService.getSettings()`.

**Response Schema:**
```typescript
{
  builtInTools: string[],  // Array of enabled built-in tool IDs
  spaceTools: SpaceTool[]  // Array of Gradio space configurations
}
```

**Sources:** [packages/app/src/server/web-server.ts:376-378]()

#### Update Settings

**Route:** `POST /api/settings`

Updates tool configuration and emits `toolStateChange` events for modified tools.

**Request Body:**
```typescript
{
  builtInTools?: string[],
  spaceTools?: SpaceTool[]
}
```

**Tool State Change Detection:** The endpoint maintains `localSharedToolStates` map ([packages/app/src/server/web-server.ts:30]()) to track which tools are currently enabled. When settings are updated, it compares the new state with the current state and only emits events for tools that actually changed ([packages/app/src/server/web-server.ts:395-410]()):

```typescript
for (const toolId of ALL_BUILTIN_TOOL_IDS) {
  const shouldBeEnabled = builtInTools.includes(toolId);
  const currentlyEnabled = this.localSharedToolStates.get(toolId) ?? false;
  
  if (currentlyEnabled !== shouldBeEnabled) {
    this.localSharedToolStates.set(toolId, shouldBeEnabled);
    this.apiClient.emit('toolStateChange', toolId, shouldBeEnabled);
  }
}
```

This prevents redundant events and ensures MCP server instances only react to actual state transitions.

**Sources:** [packages/app/src/server/web-server.ts:381-413]()

### Gradio Endpoints

These endpoints manage dynamically-discovered Gradio space tools. The data is stored and managed by the `McpApiClient` instance.

#### List Gradio Endpoints

**Route:** `GET /api/gradio-endpoints`

Returns array of Gradio endpoints from `apiClient.getGradioEndpoints()`.

**Response Schema:**
```typescript
Array<{
  name: string,
  subdomain: string,
  id?: string,
  emoji?: string,
  enabled?: boolean
}>
```

**Sources:** [packages/app/src/server/web-server.ts:416-422]()

#### Update Endpoint Status

**Route:** `POST /api/gradio-endpoints/:index`

Enables or disables a Gradio endpoint at the specified index.

**Request Body:**
```typescript
{
  enabled: boolean
}
```

**Behavior:**
1. Validates index bounds against `apiClient.getGradioEndpoints()` array
2. Calls `apiClient.updateGradioEndpointState(index, enabled)`
3. Emits `toolStateChange` event with tool ID `gradio_{subdomain}`
4. Returns updated endpoint object

**Sources:** [packages/app/src/server/web-server.ts:425-454]()

#### Update Endpoint Configuration

**Route:** `PUT /api/gradio-endpoints/:index`

Updates the metadata for a Gradio endpoint.

**Request Body:**
```typescript
{
  name: string,       // Required
  subdomain: string,  // Required
  id?: string,
  emoji?: string
}
```

**Validation:** Returns 400 if `name` or `subdomain` is missing.

**Sources:** [packages/app/src/server/web-server.ts:457-488]()

---

## Static File Serving

The `setupStaticFiles()` method configures different serving strategies for development and production modes.

### Development Mode: Vite Middleware

In development (`NODE_ENV=development`), the server integrates Vite's dev server with Hot Module Replacement (HMR):

```mermaid
graph TB
    Request["HTTP Request"]
    ViteMiddleware["Vite Middleware"]
    ViteServer["Vite Dev Server"]
    HMR["HMR WebSocket"]
    Browser["Browser"]
    
    Request -->|"non-API routes"| ViteMiddleware
    ViteMiddleware --> ViteServer
    ViteServer -->|"transformed code"| Browser
    HMR -.->|"update notifications"| Browser
```

**Configuration ([packages/app/src/server/web-server.ts:185-207]()):**

```typescript
const vite = await createViteServer({
  configFile: path.resolve(__dirname, '..', '..', '..', 'app', 'vite.config.ts'),
  server: {
    middlewareMode: true,
    hmr: true
  },
  appType: 'spa',
  root: rootDir
});

this.app.use(vite.middlewares);
```

**Root Directory:** Resolves to `packages/app/src/web` ([packages/app/src/server/web-server.ts:187]())

**Benefits:**
- Instant hot reload of React components
- Source maps for debugging
- Fast TypeScript transpilation
- CSS hot reload without page refresh

**Sources:** [packages/app/src/server/web-server.ts:182-208]()

### Production Mode: Static Files

In production, pre-built files are served from the compiled `web` directory:

**Static Path:** `<dist>/web` ([packages/app/src/server/web-server.ts:211]())

**SPA Fallback:** All non-API routes are redirected to `index.html` for client-side routing ([packages/app/src/server/web-server.ts:214-219]()):

```typescript
this.app.get('*', (req, res) => {
  if (!req.path.startsWith('/api/')) {
    res.sendFile(path.join(staticPath, 'index.html'));
  }
});
```

This ensures URLs like `/settings` or `/monitoring` work correctly when accessed directly or after page refresh.

**Sources:** [packages/app/src/server/web-server.ts:210-220]()

### Route Priority

The order of route registration is critical to prevent conflicts:

```mermaid
flowchart TD
    Start["Application.start()"]
    APIRoutes["setupApiRoutes()<br/>/api/* handlers"]
    Transport["initializeTransport()<br/>Transport routes:/sse, /mcp"]
    StaticFiles["setupStaticFiles()<br/>Vite or static + SPA fallback"]
    
    Start --> APIRoutes
    APIRoutes --> Transport
    Transport --> StaticFiles
    
    Note1["Priority 1:<br/>API routes match first"]
    Note2["Priority 2:<br/>Transport routes"]
    Note3["Priority 3:<br/>Static files and fallback"]
    
    APIRoutes -.-> Note1
    Transport -.-> Note2
    StaticFiles -.-> Note3
```

This ordering ensures:
1. API endpoints (`/api/*`) are handled first
2. Transport routes (`/sse`, `/mcp`) are registered next
3. Static file serving and SPA fallback are last (catch-all)

**Sources:** [packages/app/src/server/application.ts:109-119]()

---

## Lifecycle Management

### Server Initialization Flow

```mermaid
sequenceDiagram
    participant App as Application
    participant WS as WebServer
    participant Express
    participant HTTP as Node HTTP Server
    
    App->>WS: new WebServer()
    WS->>Express: create Express app
    WS->>WS: setupMiddleware()
    
    App->>WS: setTransportInfo(info)
    App->>WS: setupApiRoutes()
    App->>WS: start(port)
    
    WS->>HTTP: app.listen(port)
    HTTP-->>WS: server instance
    WS->>WS: this.server = server
    WS-->>App: Promise<void> resolves
    
    Note over WS: Server is now accepting connections
```

**Sources:** [packages/app/src/server/web-server.ts:150-163](), [packages/app/src/server/application.ts:99-123]()

### Start Method

**Signature:** `async start(port: number): Promise<void>`

**Behavior:**
1. Validates server is not already running ([packages/app/src/server/web-server.ts:151-153]())
2. Calls `app.listen(port)` and wraps in Promise
3. Stores server instance in `this.server`
4. Updates `transportInfo.port` on successful start
5. Rejects promise on error

**Sources:** [packages/app/src/server/web-server.ts:150-163]()

### Stop Method

**Signature:** `async stop(): Promise<void>`

**Behavior:**
1. Returns immediately if server is not running
2. Calls `server.close()` to stop accepting new connections
3. Waits for existing connections to complete
4. Sets `this.server = null`
5. Rejects promise on error

**Note:** This is a graceful shutdown that allows in-flight requests to complete. The `Application` class coordinates this with transport shutdown ([packages/app/src/server/application.ts:172-187]()).

**Sources:** [packages/app/src/server/web-server.ts:165-180]()

### Shutdown Sequence

```mermaid
sequenceDiagram
    participant Signal as OS Signal
    participant App as Application
    participant API as McpApiClient
    participant Transport
    participant WS as WebServer
    
    Signal->>App: SIGINT/SIGTERM
    App->>App: stop()
    
    App->>API: stopPolling()
    Note over API: Stop tool state polling
    
    opt Transport initialized
        App->>Transport: shutdown()
        Note over Transport: Stop accepting new connections
    end
    
    App->>WS: stop()
    WS->>WS: server.close()
    Note over WS: Wait for in-flight requests
    WS-->>App: Promise resolves
    
    opt Transport cleanup
        App->>Transport: cleanup()
        Note over Transport: Close sessions, release resources
    end
    
    Note over App: Shutdown complete
```

**Sources:** [packages/app/src/server/application.ts:172-187]()

---

## Integration Points

### Application Class Coordination

The `Application` class ([packages/app/src/server/application.ts]()) orchestrates the `WebServer` and other components:

| Phase | Method | WebServer Interaction |
|-------|--------|----------------------|
| **Construction** | `constructor()` | Creates `WebServer` instance |
| **Configuration** | `start()` | Calls `setTransportInfo()`, `setApiClient()` |
| **API Setup** | `start()` | Calls `setupApiRoutes()` |
| **Server Start** | `startWebServer()` | Calls `start(port)` |
| **Transport Init** | `initializeTransport()` | Calls `setTransport()` |
| **Static Files** | `start()` | Calls `setupStaticFiles()` |
| **Shutdown** | `stop()` | Calls `stop()` |

**Sources:** [packages/app/src/server/application.ts:99-187]()

### Transport Integration

Transports access the Express app via `getApp()` to register their protocol-specific routes:

```typescript
const app = webServerInstance.getApp();

// Example: SSE Transport registers /sse and /message routes
app.get('/sse', handleSSE);
app.post('/message', handleMessage);
```

The `WebServer` stores a reference to the active transport via `setTransport()` ([packages/app/src/server/web-server.ts:138-140]()) to enable session and metrics queries.

**Sources:** [packages/app/src/server/web-server.ts:117-119](), [packages/app/src/server/web-server.ts:138-140]()

### ApiClient Integration

The `McpApiClient` is injected via `setApiClient()` ([packages/app/src/server/web-server.ts:142-144]()) and used for:

1. **Gradio Endpoint Management:** Reading/updating Gradio space configurations
2. **Event Emission:** Broadcasting `toolStateChange` events to MCP server instances
3. **Tool State Coordination:** Ensuring consistent tool availability across all sessions

**Sources:** [packages/app/src/server/web-server.ts:142-144](), [packages/app/src/server/web-server.ts:404-406](), [packages/app/src/server/web-server.ts:417-421]()

---

# Page: Configuration UI

# Configuration UI

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [packages/app/src/server/utils/tool-selection-strategy.ts](packages/app/src/server/utils/tool-selection-strategy.ts)
- [packages/app/src/shared/bouquet-presets.ts](packages/app/src/shared/bouquet-presets.ts)
- [packages/app/src/web/components/SettingsCopyPage.tsx](packages/app/src/web/components/SettingsCopyPage.tsx)
- [packages/app/src/web/components/bouquets/ToolPresetsCard.tsx](packages/app/src/web/components/bouquets/ToolPresetsCard.tsx)
- [packages/app/test/server/utils/tool-selection-strategy.test.ts](packages/app/test/server/utils/tool-selection-strategy.test.ts)

</details>



## Overview

The Configuration UI provides a web-based interface for setting up MCP clients and understanding tool configuration options. This page documents the React components and user workflows that guide users through connecting AI clients (Claude, VS Code, Cursor, etc.) and selecting tool presets via URL parameters.

For the backend API endpoints that serve this UI, see [Web Server and API Endpoints](#8.1). For runtime metrics and monitoring interfaces, see [Monitoring Dashboard](#8.3). For the underlying tool selection logic, see [Tool Selection Strategy](#5.2).

---

## Component Architecture

The Configuration UI consists of two primary React components that work together to provide setup instructions and configuration options.

```mermaid
graph TB
    subgraph "SettingsCopyPage Component"
        Hero["Hero Section<br/>HF Logo + Welcome"]
        GetStarted["Get Started Card<br/>2-Step Setup"]
        Step1["Step 1: Copy MCP URL<br/>https://huggingface.co/mcp?login"]
        Step2["Step 2: Link to Settings<br/>https://huggingface.co/settings/mcp"]
        ToolPresets["ToolPresetsCard<br/>Collapsible Presets"]
        ClientSetup["Client Setup Section<br/>Expandable Cards"]
    end
    
    subgraph "Client Configuration Cards"
        Claude["Claude Desktop & Claude.ai<br/>Deep Link to Connectors"]
        VSCode["VS Code<br/>vscode:mcp/install Deep Link"]
        Cursor["Cursor<br/>Install MCP Image Link"]
        LMStudio["LM Studio<br/>lmstudio.ai Deep Link"]
        GeminiCLI["Gemini CLI<br/>CLI Commands"]
        ClaudeCode["Claude Code<br/>CLI Commands"]
        CodexCLI["Codex CLI<br/>TOML Configuration"]
    end
    
    subgraph "ToolPresetsCard Details"
        ExampleLinks["Example Links Section<br/>4 URL Patterns"]
        CorePresets["Core Presets Grid<br/>spaces, search, docs, hf_api"]
        AdvancedPresets["Advanced Presets Grid<br/>no_gradio_images, mcp_ui, jobs"]
        PresetCard["PresetCard Component<br/>Per-Preset Details"]
    end
    
    Hero --> GetStarted
    GetStarted --> Step1
    GetStarted --> Step2
    GetStarted --> ToolPresets
    ToolPresets --> ExampleLinks
    ToolPresets --> CorePresets
    ToolPresets --> AdvancedPresets
    CorePresets --> PresetCard
    AdvancedPresets --> PresetCard
    
    ClientSetup --> Claude
    ClientSetup --> VSCode
    ClientSetup --> Cursor
    ClientSetup --> LMStudio
    ClientSetup --> GeminiCLI
    ClientSetup --> ClaudeCode
    ClientSetup --> CodexCLI
```

**Sources:** [packages/app/src/web/components/SettingsCopyPage.tsx:1-1095](), [packages/app/src/web/components/bouquets/ToolPresetsCard.tsx:1-227]()

---

## SettingsCopyPage Component

### Purpose and Layout

The `SettingsCopyPage` component serves as the primary entry point for users configuring MCP clients. It provides a two-step setup process followed by detailed client-specific instructions.

```mermaid
graph LR
    subgraph "Setup Workflow"
        A["1. Copy Base URL<br/>handleCopyMcpUrl()"]
        B["2. Configure Tools<br/>handleGoToSettings()"]
        C["3. Select Client<br/>toggleClientExpansion()"]
        D["4. Follow Instructions<br/>renderInstructionStep()"]
    end
    
    subgraph "Actions"
        Copy["CopyButton<br/>navigator.clipboard.writeText()"]
        External["ExternalLink<br/>window.open()"]
        Download["Download Handler<br/>document.createElement('a')"]
    end
    
    A --> B
    B --> C
    C --> D
    D --> Copy
    D --> External
    D --> Download
```

**Sources:** [packages/app/src/web/components/SettingsCopyPage.tsx:835-961]()

### Client Configuration Data Structure

Each client is defined by a `ClientConfig` interface that specifies the setup workflow:

| Field | Type | Purpose |
|-------|------|---------|
| `id` | `string` | Unique identifier (e.g., "claude", "vscode") |
| `name` | `string` | Display name shown in UI |
| `icon` | `React.ReactNode` | SVG icon component |
| `description` | `string` (optional) | Brief client description |
| `instructions` | `(string \| InstructionStep)[]` | Ordered setup steps |
| `actionButtons` | `ActionButton[]` (optional) | External documentation links |
| `manualConfig` | `object` (optional) | Alternative configuration method |

**Sources:** [packages/app/src/web/components/SettingsCopyPage.tsx:35-47]()

### Instruction Step Types

The `renderInstructionStep` function handles five step types:

```mermaid
graph TB
    subgraph "InstructionStep Types"
        Text["type: 'text'<br/>Plain text or ReactNode"]
        Code["type: 'code'<br/>Syntax-highlighted block"]
        Button["type: 'button'<br/>Actionable element"]
        Warning["type: 'warning'<br/>Yellow alert box"]
        Info["type: 'info'<br/>Blue info box"]
    end
    
    subgraph "Rendering Logic"
        Render["renderInstructionStep()"]
        CopyBtn["CopyButton<br/>copyable: true"]
        ActionBtn["Button<br/>handleActionButton()"]
    end
    
    Text --> Render
    Code --> Render
    Button --> Render
    Warning --> Render
    Info --> Render
    
    Code --> CopyBtn
    Button --> ActionBtn
```

**Sources:** [packages/app/src/web/components/SettingsCopyPage.tsx:28-33, 898-959]()

### Client Setup Examples

#### VS Code Configuration

The VS Code setup uses a deep link protocol to trigger automatic installation:

```
vscode:mcp/install?%7B%22name%22%3A%22huggingface%22%2C%22type%22%3A%22http%22%2C%22url%22%3A%22https%3A%2F%2Fhuggingface.co%2Fmcp%3Flogin%22%7D
```

Manual configuration provides an alternative using `settings.json`:

```json
{
  "servers": {
    "huggingface": {
      "url": "https://huggingface.co/mcp",
      "headers": {
        "Authorization": "Bearer <HF_TOKEN>"
      }
    }
  }
}
```

**Sources:** [packages/app/src/web/components/SettingsCopyPage.tsx:237-396]()

#### Cursor Configuration

Cursor uses an external service endpoint to handle installation:

```
https://cursor.com/en/install-mcp?name=huggingface&config=eyJ1cmwiOiJodHRwczovL2h1Z2dpbmdmYWNlLmNvL21jcD9sb2dpbiJ9
```

**Sources:** [packages/app/src/web/components/SettingsCopyPage.tsx:470-525]()

#### CLI-Based Clients

Gemini CLI and Claude Code use command-line installation:

```bash
# Gemini CLI
gemini mcp add -t http huggingface https://huggingface.co/mcp?login

# Claude Code
claude mcp add hf-mcp-server -t http https://huggingface.co/mcp?login
```

**Sources:** [packages/app/src/web/components/SettingsCopyPage.tsx:650-658, 730-736]()

---

## ToolPresetsCard Component

### Purpose

The `ToolPresetsCard` component displays collapsible documentation for bouquet presets and URL customization options. It serves as a reference for users who want to override their saved settings via URL parameters.

```mermaid
graph TB
    subgraph "ToolPresetsCard State"
        Collapsed["Collapsed State<br/>expanded: false"]
        Expanded["Expanded State<br/>expanded: true"]
    end
    
    subgraph "Expanded Content"
        Examples["Example Links Section<br/>EXAMPLE_LINKS[4]"]
        CoreGrid["Core Presets<br/>CORE_PRESETS.map()"]
        AdvancedGrid["Advanced Presets<br/>ADVANCED_PRESETS.map()"]
    end
    
    subgraph "PresetCard Rendering"
        Metadata["Preset Metadata<br/>label, description, key"]
        ParamOptions["Parameter Options<br/>bouquet/mix URLs"]
        DirectParams["Direct Query Params<br/>directParams[]"]
        Tools["Included Tools<br/>describeConfigEntry()"]
    end
    
    Collapsed -->|onClick toggle| Expanded
    Expanded --> Examples
    Expanded --> CoreGrid
    Expanded --> AdvancedGrid
    
    CoreGrid --> PresetCard
    AdvancedGrid --> PresetCard
    
    PresetCard --> Metadata
    PresetCard --> ParamOptions
    PresetCard --> DirectParams
    PresetCard --> Tools
```

**Sources:** [packages/app/src/web/components/bouquets/ToolPresetsCard.tsx:141-226]()

### Bouquet Preset Display

Each preset is rendered by the `PresetCard` component, which reads from `BOUQUET_PRESETS`:

| Field | Source | Purpose |
|-------|--------|---------|
| `key` | `BouquetKey` | URL parameter value (e.g., "search") |
| `label` | `string` | Human-readable name |
| `description` | `string` | Preset purpose explanation |
| `category` | `'core' \| 'advanced'` | Grouping for UI organization |
| `supportsBouquet` | `boolean` | Can be used with `bouquet=` param |
| `supportsMix` | `boolean` | Can be used with `mix=` param |
| `builtInTools` | `readonly string[]` | Tool IDs included in preset |
| `directParams` | `DirectParamOption[]` (optional) | Alternative query parameters |

**Sources:** [packages/app/src/shared/bouquet-presets.ts:69-78]()

### URL Generation Logic

The `PresetCard` component generates copyable URLs based on preset configuration:

```mermaid
graph LR
    subgraph "URL Generation Flow"
        Preset["BouquetPreset<br/>input"]
        CheckBouquet{supportsBouquet?}
        CheckMix{supportsMix?}
        CheckDirect{directParams?}
        
        BouquetURL["BASE_URL + bouquet=key"]
        MixURL["BASE_URL + mix=key"]
        DirectURL["BASE_URL + directParam"]
        
        ParamOptions["paramOptions[]<br/>Array of URLs"]
    end
    
    Preset --> CheckBouquet
    Preset --> CheckMix
    Preset --> CheckDirect
    
    CheckBouquet -->|true| BouquetURL
    CheckMix -->|true| MixURL
    CheckDirect -->|true| DirectURL
    
    BouquetURL --> ParamOptions
    MixURL --> ParamOptions
    DirectURL --> ParamOptions
```

**Sources:** [packages/app/src/web/components/bouquets/ToolPresetsCard.tsx:34-54]()

### Example Links Section

The component displays four example URL patterns to illustrate common use cases:

| Example | URL Pattern | Description |
|---------|-------------|-------------|
| Bouquet override | `?login&bouquet=search` | Overrides saved tool list |
| Mix with saved tools | `?login&mix=docs` | Adds tools to saved settings |
| Add Gradio Spaces | `?login&gradio=victor/websearch` | Includes dynamic Space tools |
| Customise Options | `?login&no_image_content=true` | Disables image downloads |

**Sources:** [packages/app/src/web/components/bouquets/ToolPresetsCard.tsx:11-32]()

---

## Bouquet Configuration System

### Preset Definitions

The `BOUQUETS` object maps preset keys to `AppSettings` configurations:

```mermaid
graph TB
    subgraph "BOUQUETS Object"
        HfApi["hf_api<br/>TOOL_ID_GROUPS.hf_api"]
        Spaces["spaces<br/>TOOL_ID_GROUPS.spaces"]
        Search["search<br/>TOOL_ID_GROUPS.search"]
        Docs["docs<br/>TOOL_ID_GROUPS.docs"]
        All["all<br/>ALL_BUILTIN_TOOL_IDS"]
    end
    
    subgraph "Advanced Bouquets"
        HubReadme["hub_repo_details_readme<br/>+ README_INCLUDE_FLAG"]
        NoImages["no_gradio_images<br/>+ GRADIO_IMAGE_FILTER_FLAG"]
        McpUi["mcp_ui<br/>USE_SPACE_TOOL_ID"]
        Jobs["jobs<br/>HF_JOBS_TOOL_ID"]
        Dynamic["dynamic_space<br/>SPACE_SEARCH + DYNAMIC_SPACE"]
    end
    
    subgraph "AppSettings Structure"
        BuiltIn["builtInTools: string[]"]
        SpaceTools["spaceTools: SpaceTool[]"]
    end
    
    HfApi --> BuiltIn
    Spaces --> BuiltIn
    Search --> BuiltIn
    Docs --> BuiltIn
    All --> BuiltIn
    
    HubReadme --> BuiltIn
    NoImages --> BuiltIn
    McpUi --> BuiltIn
    Jobs --> BuiltIn
    Dynamic --> BuiltIn
    
    BuiltIn --> SpaceTools
```

**Sources:** [packages/app/src/shared/bouquet-presets.ts:13-59]()

### Tool Descriptions

The `describeConfigEntry` function maps tool IDs to human-readable descriptions:

```mermaid
graph LR
    subgraph "Tool Description Lookup"
        ToolId["Input: tool ID string"]
        CheckTool{In TOOL_DESCRIPTIONS?}
        CheckFlag{In BEHAVIOR_FLAG_DESCRIPTIONS?}
        
        ToolDesc["Return ConfigEntryDescription<br/>kind: 'tool'"]
        FlagDesc["Return ConfigEntryDescription<br/>kind: 'behavior-flag'"]
        Default["Return default description"]
    end
    
    ToolId --> CheckTool
    CheckTool -->|Yes| ToolDesc
    CheckTool -->|No| CheckFlag
    CheckFlag -->|Yes| FlagDesc
    CheckFlag -->|No| Default
```

**Tool Descriptions** (lines 190-247):
- `space_search`, `model_search`, `dataset_search`, `paper_search`
- `model_details`, `dataset_details`, `hub_repo_details`
- `duplicate_space`, `space_info`, `space_files`, `use_space`
- `hf_doc_search`, `hf_doc_fetch`, `hf_jobs`

**Behavior Flag Descriptions** (lines 249-258):
- `README_INCLUDE_FLAG`: Permits README sections in responses
- `GRADIO_IMAGE_FILTER_FLAG`: Prevents image downloads

**Sources:** [packages/app/src/shared/bouquet-presets.ts:190-282]()

---

## URL Parameter System

### Parameter to Backend Flow

The Configuration UI generates URLs with query parameters that are processed by the backend tool selection system:

```mermaid
sequenceDiagram
    participant UI as "ToolPresetsCard<br/>Component"
    participant Browser as "Browser<br/>navigator.clipboard"
    participant Server as "WebServer<br/>Express"
    participant Extract as "extractAuthBouquetAndMix()"
    participant Strategy as "ToolSelectionStrategy<br/>.selectTools()"
    participant Result as "ToolSelectionResult"
    
    UI->>Browser: Copy URL with parameters
    Note over UI,Browser: https://huggingface.co/mcp?login&bouquet=search
    
    Browser->>Server: HTTP request with query params
    Server->>Extract: Parse x-mcp-bouquet header
    Extract->>Strategy: headers: { 'x-mcp-bouquet': 'search' }
    
    Strategy->>Strategy: Check precedence:<br/>1. bouquet override<br/>2. mix<br/>3. user settings<br/>4. fallback
    
    Strategy->>Result: mode: BOUQUET_OVERRIDE<br/>enabledToolIds: TOOL_ID_GROUPS.search
    Result-->>Server: Return tool configuration
```

**Sources:** [packages/app/src/web/components/bouquets/ToolPresetsCard.tsx:9-44](), [packages/app/src/server/utils/tool-selection-strategy.ts:129-148]()

### Query Parameter to Header Mapping

URL query parameters are converted to HTTP headers by the backend:

| Query Parameter | HTTP Header | Purpose |
|-----------------|-------------|---------|
| `bouquet=search` | `x-mcp-bouquet: search` | Overrides tool list completely |
| `mix=docs` | `x-mcp-mix: docs` | Adds tools to saved settings |
| `gradio=foo/bar` | `x-mcp-gradio: foo/bar` | Specifies dynamic Gradio endpoints |
| `no_image_content=true` | (processed directly) | Disables Gradio image downloads |

**Sources:** [packages/app/src/server/utils/tool-selection-strategy.ts:130](), [packages/app/src/web/components/bouquets/ToolPresetsCard.tsx:173]()

### Tool Selection Precedence

The backend implements a four-level precedence system described in `ToolSelectionStrategy`:

```mermaid
graph TB
    Start["Client Request<br/>with headers"]
    
    P1{x-mcp-bouquet<br/>present?}
    P2{x-mcp-mix<br/>present?}
    P3{User settings<br/>available?}
    
    B1["BOUQUET_OVERRIDE<br/>Use bouquet tools only"]
    B2["MIX<br/>User tools + bouquet"]
    B3["EXTERNAL_API / INTERNAL_API<br/>Use user settings"]
    B4["FALLBACK<br/>ALL_BUILTIN_TOOL_IDS"]
    
    Start --> P1
    P1 -->|Yes| B1
    P1 -->|No| P2
    P2 -->|Yes + settings| B2
    P2 -->|No| P3
    P3 -->|Yes| B3
    P3 -->|No| B4
```

**Sources:** [packages/app/src/server/utils/tool-selection-strategy.ts:33-69, 129-221]()

---

## Copy Button Integration

### CopyButton Component Usage

The UI extensively uses the `CopyButton` component for one-click URL copying:

```mermaid
graph LR
    subgraph "CopyButton Props"
        Content["content: string<br/>Text to copy"]
        Variant["variant: 'default' | 'outline'<br/>Button style"]
        Size["size: 'sm' | 'default'<br/>Button size"]
        IconOnly["iconOnly: boolean<br/>Hide label"]
        Label["label: string<br/>Accessibility text"]
    end
    
    subgraph "Copy Locations"
        URL["MCP Base URL<br/>https://huggingface.co/mcp?login"]
        Bouquet["Bouquet URL<br/>?login&bouquet=search"]
        Mix["Mix URL<br/>?login&mix=docs"]
        Code["Code Blocks<br/>JSON, TOML, CLI commands"]
    end
    
    Content --> URL
    Content --> Bouquet
    Content --> Mix
    Content --> Code
```

**Usage Examples:**

1. **Inline URL copy** (SettingsCopyPage:1003-1008):
```tsx
<CopyButton
  content="https://huggingface.co/mcp?login"
  variant="secondary"
  size="sm"
  iconOnly
  className="absolute right-2 top-1/2 transform -translate-y-1/2 h-8 px-2"
/>
```

2. **Preset URL copy** (ToolPresetsCard:80-87):
```tsx
<CopyButton
  content={option.url}
  iconOnly
  variant="ghost"
  size="sm"
  label={`Copy ${option.param}`}
  className="h-6 w-6 shrink-0"
/>
```

**Sources:** [packages/app/src/web/components/SettingsCopyPage.tsx:1003-1008](), [packages/app/src/web/components/bouquets/ToolPresetsCard.tsx:80-87]()

---

## State Management

### Component-Level State

Both major components use minimal local state:

**SettingsCopyPage** maintains expanded client sections:
```typescript
const [expandedClients, setExpandedClients] = useState<Set<string>>(new Set());

const toggleClientExpansion = (clientId: string) => {
  setExpandedClients((prev) => {
    const newSet = new Set(prev);
    if (newSet.has(clientId)) {
      newSet.delete(clientId);
    } else {
      newSet.add(clientId);
    }
    return newSet;
  });
};
```

**ToolPresetsCard** maintains collapse/expand state:
```typescript
const [expanded, setExpanded] = useState(false);
```

**Sources:** [packages/app/src/web/components/SettingsCopyPage.tsx:836-864](), [packages/app/src/web/components/bouquets/ToolPresetsCard.tsx:142]()

---

## Configuration Workflow Summary

```mermaid
graph TB
    subgraph "User Journey"
        Land["User lands on<br/>SettingsCopyPage"]
        Copy["Copy base URL<br/>https://huggingface.co/mcp?login"]
        Settings["Navigate to<br/>/settings/mcp"]
        Select["Select tools in settings UI"]
        Return["Return to choose client"]
        Expand["Expand client card"]
        Follow["Follow setup instructions"]
    end
    
    subgraph "Alternative: URL Override"
        Preset["Expand ToolPresetsCard"]
        Choose["Choose preset"]
        CopyURL["Copy bouquet/mix URL"]
        UseURL["Use URL in client config"]
    end
    
    Land --> Copy
    Copy --> Settings
    Settings --> Select
    Select --> Return
    Return --> Expand
    Expand --> Follow
    
    Land --> Preset
    Preset --> Choose
    Choose --> CopyURL
    CopyURL --> UseURL
```

**Sources:** [packages/app/src/web/components/SettingsCopyPage.tsx:976-1042](), [packages/app/src/web/components/bouquets/ToolPresetsCard.tsx:141-226]()

---

# Page: Monitoring Dashboard

# Monitoring Dashboard

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [packages/app/src/server/application.ts](packages/app/src/server/application.ts)
- [packages/app/src/server/web-server.ts](packages/app/src/server/web-server.ts)
- [packages/app/src/web/components/McpMethodsCard.tsx](packages/app/src/web/components/McpMethodsCard.tsx)
- [packages/app/src/web/components/StdioTransportMetrics.tsx](packages/app/src/web/components/StdioTransportMetrics.tsx)
- [packages/app/src/web/components/TransportMetricsCard.tsx](packages/app/src/web/components/TransportMetricsCard.tsx)
- [packages/app/src/web/components/data-table-utils.tsx](packages/app/src/web/components/data-table-utils.tsx)
- [packages/app/src/web/components/data-table.tsx](packages/app/src/web/components/data-table.tsx)
- [packages/app/src/web/hooks/useSessionCache.ts](packages/app/src/web/hooks/useSessionCache.ts)

</details>



The Monitoring Dashboard provides real-time visibility into MCP server operations, displaying connection statistics, method call performance, session tracking, and Gradio integration metrics. The dashboard automatically refreshes every 3 seconds to provide up-to-date information about client connections, tool invocations, and system health.

For information about configuring tools and server settings, see [Configuration UI](#8.2). For details about the API endpoints that power this dashboard, see [Web Server and API Endpoints](#8.1).

---

## Overview

The monitoring dashboard consists of two primary metric cards displayed in the web interface:

1. **TransportMetricsCard** - Displays transport-specific connection metrics, session information, configuration parameters, and uptime statistics
2. **McpMethodsCard** - Shows aggregated statistics for MCP method calls including tool invocations, prompt requests, error rates, and performance metrics

Both cards use SWR (stale-while-revalidate) for data fetching with 3-second polling intervals, ensuring the dashboard displays near-real-time data without manual refreshing.

**Sources:** [packages/app/src/web/components/TransportMetricsCard.tsx:1-72](), [packages/app/src/web/components/McpMethodsCard.tsx:1-298]()

---

## Dashboard Component Architecture

The dashboard follows a component hierarchy where `TransportMetricsCard` acts as a router, delegating to transport-specific components based on the active transport type.

```mermaid
graph TB
    subgraph "Dashboard UI Layer"
        Dashboard["Web Dashboard Page"]
        TMC["TransportMetricsCard<br/>(Router Component)"]
        MMC["McpMethodsCard<br/>(Method Statistics)"]
    end
    
    subgraph "Transport-Specific Components"
        STDIO["StdioTransportMetrics<br/>(STDIO Mode)"]
        Stateful["StatefulTransportMetrics<br/>(SSE/StreamableHTTP)"]
        Stateless["StatelessTransportMetrics<br/>(StreamableHTTPJson)"]
    end
    
    subgraph "Shared UI Components"
        DT["DataTable<br/>(TanStack Table)"]
        USC["useSessionCache Hook<br/>(5-minute retention)"]
        DTU["data-table-utils<br/>(createSortableHeader)"]
    end
    
    subgraph "Data Fetching"
        SWR["SWR<br/>(3-second polling)"]
        API["API Endpoints<br/>/api/transport-metrics<br/>/api/sessions"]
    end
    
    Dashboard --> TMC
    Dashboard --> MMC
    
    TMC --> STDIO
    TMC --> Stateful
    TMC --> Stateless
    
    STDIO --> DT
    STDIO --> USC
    Stateful --> DT
    Stateful --> USC
    Stateless --> DT
    
    DT --> DTU
    
    TMC --> SWR
    MMC --> SWR
    SWR --> API
```

**Sources:** [packages/app/src/web/components/TransportMetricsCard.tsx:19-71](), [packages/app/src/web/components/McpMethodsCard.tsx:31-43](), [packages/app/src/web/components/StdioTransportMetrics.tsx:1-180]()

---

## API Endpoints for Metrics

The dashboard retrieves data from several API endpoints provided by the `WebServer` class. The primary endpoint is `/api/transport-metrics`, which returns comprehensive metrics data.

### Metrics API Endpoint

The `/api/transport-metrics` endpoint is the main data source for the monitoring dashboard.

| Endpoint | Method | Response Interval | Purpose |
|----------|--------|-------------------|---------|
| `/api/transport-metrics` | GET | Polled every 3s | Returns complete metrics including methods, sessions, configuration, API metrics, and Gradio metrics |
| `/api/sessions` | GET | On-demand | Returns current active sessions (used by STDIO mode) |
| `/api/transport` | GET | Initial load | Returns transport configuration and type information |

The `/api/transport-metrics` endpoint performs these operations:

1. Retrieves raw metrics from the active transport via `transport.getMetrics()`
2. Determines if the transport is stateless (`streamableHttpJson` mode)
3. Fetches session data and calculates connection status for each session
4. Formats metrics using `formatMetricsForAPI()` from the transport-metrics module
5. Conditionally includes `apiMetrics` if in external API mode
6. Always includes `gradioMetrics` and `gradioCacheMetrics`
7. Optionally activates temporary logging for stateless transports via the `templog` query parameter

**Sources:** [packages/app/src/server/web-server.ts:254-373]()

### Session Status Calculation

Sessions are classified into three connection states based on activity timestamps and ping failures:

```mermaid
graph LR
    Session["Session Data"]
    
    RecentCheck{"Last activity<br/>within 5 minutes?"}
    PingCheck{"Ping failures<br/>>= 1?"}
    
    Connected["Connected"]
    Distressed["Distressed"]
    Disconnected["Disconnected"]
    
    Session --> RecentCheck
    RecentCheck -->|Yes| PingCheck
    RecentCheck -->|No| Disconnected
    PingCheck -->|No| Connected
    PingCheck -->|Yes| Distressed
```

The status calculation logic is implemented in the metrics endpoint handler:

- **Connected**: Recent activity (within 5 minutes) and no ping failures
- **Distressed**: Recent activity but has ping failures
- **Disconnected**: No activity within 5 minutes

**Sources:** [packages/app/src/server/web-server.ts:295-323]()

---

## TransportMetricsCard Component

The `TransportMetricsCard` serves as a router component that displays the appropriate transport-specific metrics component based on the current transport type. It handles loading states, error states, and delegates rendering to specialized components.

### Transport Type Routing

```mermaid
graph TB
    TMC["TransportMetricsCard"]
    SWR["useSWR hook<br/>/api/transport-metrics<br/>refreshInterval: 3000"]
    
    Loading["Loading State<br/>(Skeleton UI)"]
    Error["Error State<br/>(Alert Component)"]
    
    TransportCheck{"Check<br/>metrics.transport"}
    
    STDIO["StdioTransportMetrics"]
    StatelessCheck{"Check<br/>metrics.isStateless"}
    Stateful["StatefulTransportMetrics"]
    Stateless["StatelessTransportMetrics"]
    
    TMC --> SWR
    SWR -->|No data & no error| Loading
    SWR -->|Error| Error
    SWR -->|Success| TransportCheck
    
    TransportCheck -->|"stdio"| STDIO
    TransportCheck -->|Other| StatelessCheck
    StatelessCheck -->|true| Stateless
    StatelessCheck -->|false| Stateful
```

**Sources:** [packages/app/src/web/components/TransportMetricsCard.tsx:19-71]()

---

## McpMethodsCard Component

The `McpMethodsCard` displays aggregated statistics for all MCP method calls, with special focus on tool and prompt invocations. It enriches method data with Gradio-specific metrics when available.

### Method Data Structure

Each method tracked by the system includes the following metrics:

| Field | Type | Description |
|-------|------|-------------|
| `method` | string | Method name (e.g., `tools/call:model_search`, `prompts/get`) |
| `count` | number | Total invocation count |
| `errors` | number | Total error count (includes Gradio failures) |
| `errorRate` | number | Percentage of calls that resulted in errors |
| `averageResponseTime` | number? | Average response time in milliseconds (stateless mode only) |
| `lastCalled` | string | ISO timestamp of last invocation |
| `gradioSuccess` | number? | Successful Gradio invocations (for Gradio tools) |
| `gradioFailure` | number? | Failed Gradio invocations (for Gradio tools) |

**Sources:** [packages/app/src/web/components/McpMethodsCard.tsx:19-29]()

### Gradio Metrics Enrichment

The component enriches tool call data with Gradio-specific success/failure counts by matching tool names against `gradioMetrics.byTool` data:

```mermaid
graph TB
    Methods["Methods Array<br/>from metrics"]
    
    Process["Process Each Method"]
    ToolCheck{"Method starts with<br/>'tools/call:'?"}
    
    ExtractName["Extract tool name<br/>from 'tools/call:toolName'"]
    GradioCheck{"Gradio metrics exist<br/>for this tool?"}
    
    Enrich["Add gradioSuccess<br/>and gradioFailure<br/>Update total errors"]
    
    Output["Enriched MethodData"]
    
    Methods --> Process
    Process --> ToolCheck
    ToolCheck -->|Yes| ExtractName
    ToolCheck -->|No| Output
    ExtractName --> GradioCheck
    GradioCheck -->|Yes| Enrich
    GradioCheck -->|No| Output
    Enrich --> Output
```

The enrichment process adds Gradio failure counts to the total error count and recalculates the error rate:

```typescript
// Extract from McpMethodsCard.tsx:52-68
if (method.method.startsWith('tools/call:') && metrics?.gradioMetrics) {
    const toolName = method.method.replace('tools/call:', '');
    const gradioByTool = metrics.gradioMetrics.byTool;
    
    if (gradioByTool[toolName]) {
        gradioSuccess = gradioByTool[toolName].success;
        gradioFailure = gradioByTool[toolName].failure;
        totalErrors += gradioFailure;
    }
}
```

**Sources:** [packages/app/src/web/components/McpMethodsCard.tsx:46-82]()

### Filtering and Summary Statistics

The card provides a checkbox filter to show only tool and prompt calls, and displays summary statistics at the top:

| Statistic | Calculation |
|-----------|-------------|
| Total MCP Calls | Sum of all method counts |
| Tool Calls | Sum of counts for methods starting with `tools/call` |
| Prompt Calls | Sum of counts for methods starting with `prompts/get` |

**Sources:** [packages/app/src/web/components/McpMethodsCard.tsx:84-97]()

---

## Session Caching and Retention

The `useSessionCache` hook provides a 5-minute retention mechanism for disconnected sessions, allowing the dashboard to display recently disconnected sessions for forensic analysis.

### Session Cache Lifecycle

```mermaid
stateDiagram-v2
    [*] --> ActiveSession: Session connects
    
    ActiveSession --> ActiveSession: Activity updates<br/>(lastSeenAt updated)
    
    ActiveSession --> RecentlyDisconnected: No longer in<br/>active sessions list
    
    RecentlyDisconnected --> RecentlyDisconnected: Waiting<br/>(up to 5 minutes)
    
    RecentlyDisconnected --> [*]: 5 minutes elapsed<br/>(cleanup interval)
    
    note right of RecentlyDisconnected
        disconnectedAt timestamp set
        connectionStatus = "Disconnected"
        isConnected = false
    end note
```

The hook maintains a `Map<string, CachedSession>` where each cached session includes:

- All original session data
- `lastSeenAt`: Timestamp of last update (ISO string)
- `disconnectedAt`: Timestamp when session was marked disconnected (optional)

**Sources:** [packages/app/src/web/hooks/useSessionCache.ts:1-111]()

### Cleanup Process

The cache automatically removes stale disconnected sessions using a cleanup interval:

```typescript
// Cleanup old disconnected sessions every 30 seconds
const cleanup = () => {
    const now = Date.now();
    setCachedSessions((prevCache) => {
        const newCache = new Map(prevCache);
        newCache.forEach((session, sessionId) => {
            if (session.disconnectedAt) {
                const disconnectedTime = new Date(session.disconnectedAt).getTime();
                if (now - disconnectedTime > RETENTION_TIME) {  // 5 minutes
                    newCache.delete(sessionId);
                }
            }
        });
        return newCache;
    });
};
```

**Sources:** [packages/app/src/web/hooks/useSessionCache.ts:68-97]()

---

## DataTable Component

The `DataTable` component is a reusable table implementation built on TanStack Table that provides sorting, filtering, pagination, and column visibility controls. It is used extensively throughout the monitoring dashboard.

### DataTable Features

| Feature | Implementation | Usage in Dashboard |
|---------|----------------|-------------------|
| Sorting | `getSortedRowModel()` with `createSortableHeader()` | Sort methods by count, error rate, response time |
| Filtering | `getFilteredRowModel()` with search input | Filter by method name, session ID |
| Pagination | `getPaginationRowModel()` with configurable page size | Manage large method lists (50 rows/page) and sessions (10 rows/page) |
| Column Visibility | `DropdownMenu` with checkbox items | Show/hide columns like errors, Gradio metrics, response times |
| Default Sorting | `defaultSorting` prop | Sort by count descending or last activity |

The `createSortableHeader` utility function generates column headers with click-to-sort behavior and visual sort indicators (chevron icons):

```typescript
// Alignment options: 'left', 'right', 'center'
createSortableHeader('Method')  // Left-aligned
createSortableHeader('Calls', 'right')  // Right-aligned numeric column
```

**Sources:** [packages/app/src/web/components/data-table.tsx:1-163](), [packages/app/src/web/components/data-table-utils.tsx:1-27]()

---

## STDIO Transport Metrics Display

The `StdioTransportMetrics` component displays metrics specific to STDIO mode, which typically has a single long-lived session. It uses the session cache hook to retain disconnected session history.

### STDIO Metrics Layout

The component displays:

1. **Transport Info Section** - Transport type and uptime
2. **Sessions Table** - Active and recently disconnected sessions with client information

### Session Table Columns

```mermaid
graph LR
    subgraph "Session Table Columns"
        Client["Client<br/>(name@version)"]
        SessionID["Session ID<br/>(truncated)"]
        Status["Status Badge<br/>(Connected/Disconnected)"]
        Connected["Connected<br/>(relative time)"]
        Requests["Request Count"]
        LastActivity["Last Activity<br/>(relative time)"]
    end
```

**Client name truncation**: Names longer than 42 characters are truncated to show the first 35 and last 5 characters with ellipsis in between (e.g., `very-long-client-name-with-many-w.....ters`).

**Session ID truncation**: IDs longer than 12 characters show the first 5 and last 5 characters with ellipsis (e.g., `abc12...xyz89`).

**Sources:** [packages/app/src/web/components/StdioTransportMetrics.tsx:1-180]()

### Relative Time Formatting

The component uses helper functions to format timestamps in a human-readable way:

| Duration | Format | Example |
|----------|--------|---------|
| < 60 seconds | "just now" | just now |
| < 60 minutes | "Nm ago" | 5m ago |
| < 24 hours | "Nh ago" | 2h ago |
| ≥ 24 hours | "Nd ago" | 3d ago |

**Sources:** [packages/app/src/web/components/StdioTransportMetrics.tsx:26-42]()

---

## Data Flow: Dashboard to API

The complete data flow from user viewing the dashboard to displaying metrics involves SWR's automatic polling mechanism and React's rendering pipeline.

```mermaid
sequenceDiagram
    participant User as "User Browser"
    participant TMC as "TransportMetricsCard"
    participant MMC as "McpMethodsCard"
    participant SWR as "SWR Hook"
    participant API as "/api/transport-metrics"
    participant WS as "WebServer"
    participant Transport as "BaseTransport"
    
    User->>TMC: View dashboard
    User->>MMC: View dashboard
    
    TMC->>SWR: useSWR('/api/transport-metrics', { refreshInterval: 3000 })
    MMC->>SWR: useSWR('/api/transport-metrics', { refreshInterval: 3000 })
    
    loop Every 3 seconds
        SWR->>API: GET /api/transport-metrics
        API->>WS: Request handler
        WS->>Transport: getMetrics()
        Transport-->>WS: Raw metrics
        WS->>Transport: getSessions()
        Transport-->>WS: Session array
        WS->>WS: Calculate connection status
        WS->>WS: Format with formatMetricsForAPI()
        WS->>WS: Add apiMetrics, gradioMetrics
        WS-->>API: TransportMetricsResponse
        API-->>SWR: JSON response
        SWR-->>TMC: Updated metrics
        SWR-->>MMC: Updated metrics
        TMC->>TMC: Route to transport component
        MMC->>MMC: Enrich with Gradio metrics
    end
    
    TMC-->>User: Rendered metrics UI
    MMC-->>User: Rendered methods table
```

**Sources:** [packages/app/src/web/components/TransportMetricsCard.tsx:19-25](), [packages/app/src/web/components/McpMethodsCard.tsx:36-40](), [packages/app/src/server/web-server.ts:254-373]()

---

## Metrics Data Structure

The `TransportMetricsResponse` type returned by `/api/transport-metrics` contains comprehensive data about server operation:

### Core Metrics Fields

| Field | Type | Description |
|-------|------|-------------|
| `transport` | string | Transport type: `stdio`, `sse`, `streamableHttp`, `streamableHttpJson` |
| `isStateless` | boolean | Whether transport is stateless (creates per-request servers) |
| `startupTime` | string | ISO timestamp when server started |
| `uptimeSeconds` | number | Server uptime in seconds |
| `sessions` | SessionData[] | Array of active and cached sessions |
| `methods` | MethodMetrics[] | Array of method call statistics |
| `configuration` | TransportConfig? | Heartbeat/ping configuration (stateful only) |
| `apiMetrics` | object? | External API call metrics (external mode only) |
| `gradioMetrics` | object | Gradio tool invocation metrics |
| `gradioCacheMetrics` | object | Gradio schema cache statistics |

### Stateful Transport Configuration

For stateful transports (SSE, StreamableHTTP), the configuration object includes:

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `heartbeatInterval` | number | 30000 | Heartbeat ping interval (ms) |
| `staleCheckInterval` | number | 90000 | Stale session check interval (ms) |
| `staleTimeout` | number | 600000 | Session timeout threshold (ms) |
| `pingEnabled` | boolean | true | Whether ping mechanism is enabled |
| `pingInterval` | number | 30000 | Ping attempt interval (ms) |
| `pingFailureThreshold` | number | 1 | Consecutive ping failures before marking distressed |

**Sources:** [packages/app/src/server/web-server.ts:329-338](), [packages/app/src/shared/transport-metrics.ts]()

---

## Gradio Metrics Integration

The dashboard displays Gradio-specific metrics to track the health and performance of dynamic Gradio tool integrations.

### Gradio Metrics Structure

The `gradioMetrics` object includes:

- `byTool`: Map of tool names to success/failure counts
- `totalSuccess`: Total successful Gradio invocations across all tools
- `totalFailure`: Total failed Gradio invocations across all tools

The `gradioCacheMetrics` object tracks schema caching performance:

- `size`: Number of cached schemas
- `hits`: Cache hit count
- `misses`: Cache miss count
- `hitRate`: Percentage of requests served from cache

These metrics are displayed in the `McpMethodsCard` as additional columns showing success/failure counts for Gradio tools.

**Sources:** [packages/app/src/server/web-server.ts:346-349](), [packages/app/src/web/components/McpMethodsCard.tsx:146-161]()

---

## Summary

The Monitoring Dashboard provides comprehensive real-time visibility into MCP server operations through:

1. **Automatic polling** - SWR fetches fresh data every 3 seconds
2. **Transport-specific displays** - Different UI components for STDIO, stateful, and stateless modes
3. **Session retention** - 5-minute cache for disconnected sessions enables forensic analysis
4. **Method statistics** - Detailed tracking of tool calls, prompts, errors, and performance
5. **Gradio integration metrics** - Success/failure tracking for dynamic Gradio tools
6. **Sortable, filterable tables** - TanStack Table provides powerful data exploration capabilities

All dashboard components share the same `/api/transport-metrics` endpoint, ensuring consistent data across the UI with minimal server overhead. The dashboard automatically adapts its display based on the active transport type and available metrics.

---

# Page: Development Guide

# Development Guide

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.dockerignore](.dockerignore)
- [Dockerfile](Dockerfile)
- [README.md](README.md)
- [package.json](package.json)
- [packages/app/package.json](packages/app/package.json)
- [packages/app/vite.config.ts](packages/app/vite.config.ts)
- [packages/mcp/package.json](packages/mcp/package.json)
- [packages/mcp/src/duplicate-space.ts](packages/mcp/src/duplicate-space.ts)
- [packages/mcp/src/error-messages.ts](packages/mcp/src/error-messages.ts)
- [pnpm-lock.yaml](pnpm-lock.yaml)
- [start.sh](start.sh)

</details>



This guide is for developers who want to contribute to or extend the Hugging Face MCP Server. It covers the development environment setup, build system, testing infrastructure, and project organization.

For information about deploying and running the server, see [Getting Started](#2). For architectural details about the system components, see [Architecture](#3). For guidance on creating new tools, see [Tool System Overview](#4.1).

**Scope**: This document covers the development toolchain (pnpm, TypeScript, Vite), build pipeline, hot-reload workflows, testing with Vitest, and the monorepo structure. It does not cover tool implementation details or runtime architecture.

---

## Build System

The project uses a monorepo structure managed by pnpm workspaces with two main packages: `@llmindset/hf-mcp` (core library) and `@llmindset/hf-mcp-server` (application layer). The build system coordinates TypeScript compilation, Vite-based web bundling, and specialized single-file builds.

### Monorepo Architecture

```mermaid
graph TB
    subgraph "Root Workspace"
        RootPackage["package.json<br/>packageManager: pnpm@10.15.1"]
        Workspace["pnpm-workspace.yaml<br/>packages: packages/*"]
        Lock["pnpm-lock.yaml<br/>Frozen Dependencies"]
    end
    
    subgraph "packages/mcp"
        McpPkg["@llmindset/hf-mcp<br/>package.json"]
        McpSrc["src/**/*.ts<br/>Tool Implementations"]
        McpDist["dist/**/*.js<br/>Compiled Library"]
        McpTsc["tsc --declaration<br/>TypeScript Compiler"]
    end
    
    subgraph "packages/app"
        AppPkg["@llmindset/hf-mcp-server<br/>package.json"]
        
        subgraph "Server Code"
            ServerSrc["src/server/**/*.ts<br/>Transport Implementations"]
            ServerDist["dist/server/**/*.js<br/>Compiled Server"]
            ServerTsc["tsc -p tsconfig.server.json"]
        end
        
        subgraph "Web UI"
            WebSrc["src/web/**/*<br/>React Components"]
            WebDist["dist/web/**/*<br/>Bundled Assets"]
            ViteBuild["vite build<br/>React + Tailwind"]
        end
        
        subgraph "Single-File Builds"
            Welcome["mcp-welcome.html<br/>~252KB Self-Contained"]
            Widget["gradio-widget.html<br/>Inline Components"]
            SingleFile["vite-plugin-singlefile<br/>Inline CSS/JS"]
        end
    end
    
    RootPackage --> Workspace
    Workspace --> McpPkg
    Workspace --> AppPkg
    
    McpSrc --> McpTsc
    McpTsc --> McpDist
    AppPkg -.depends on.- McpPkg
    
    ServerSrc --> ServerTsc
    ServerTsc --> ServerDist
    
    WebSrc --> ViteBuild
    ViteBuild --> WebDist
    
    WebSrc --> SingleFile
    SingleFile --> Welcome
    SingleFile --> Widget
```

**Sources**: [package.json:1-38](), [pnpm-lock.yaml:1-10](), [packages/app/package.json:1-111](), [packages/mcp/package.json:1-53]()

### Build Pipeline Stages

The build system operates in distinct stages with specific responsibilities:

| Stage | Command | Outputs | Purpose |
|-------|---------|---------|---------|
| **Clean** | `pnpm clean` | Removes `dist/` directories | Ensures fresh builds |
| **Library Build** | `pnpm --filter=@llmindset/hf-mcp build` | `packages/mcp/dist/*.js` + `.d.ts` | Compiles tool implementations |
| **Server Build** | `pnpm --filter=@llmindset/hf-mcp-server build:server` | `packages/app/dist/server/*.js` | Compiles transport layer |
| **Web Build** | `pnpm --filter=@llmindset/hf-mcp-server build:web` | `packages/app/dist/web/*` | Bundles React dashboard |
| **Single-File Builds** | `pnpm --filter=@llmindset/hf-mcp-server build:singlefiles` | `mcp-welcome.html`, `gradio-widget.html` | Creates standalone pages |

**Sources**: [packages/app/package.json:33-39](), [packages/mcp/package.json:25-26]()

### TypeScript Compilation

The project uses two separate TypeScript configurations:

**Library Configuration** (`packages/mcp/tsconfig.json`):
- Compiles `src/**/*.ts` to `dist/`
- Generates `.d.ts` declaration files for consumers
- Target: ES modules with Node.js compatibility
- Command: `tsc --declaration`

**Server Configuration** (`packages/app/tsconfig.server.json`):
- Compiles `src/server/**/*.ts` to `dist/server/`
- Excludes web UI code from server compilation
- Target: Node.js runtime
- Command: `tsc -p tsconfig.server.json`

The separation ensures server code doesn't bundle unnecessary web dependencies.

**Sources**: [packages/app/package.json:35](), [packages/mcp/package.json:26]()

### Vite Build Configuration

The web UI uses Vite with conditional plugin application based on the `VITE_BUILD_TARGET` environment variable:

```mermaid
graph LR
    ViteConfig["vite.config.ts"]
    Plugins["Base Plugins<br/>react()<br/>tailwindcss()"]
    
    EnvCheck{"VITE_BUILD_TARGET?"}
    
    MainBuild["Main Build<br/>index.html<br/>gradio-widget-dev.html"]
    WelcomeBuild["mcp-welcome Build<br/>viteSingleFile()<br/>Inline Everything"]
    WidgetBuild["gradio-widget Build<br/>viteSingleFile()<br/>For OpenAI SDK"]
    
    MainOut["dist/web/assets/*<br/>Separate CSS/JS"]
    WelcomeOut["dist/web/mcp-welcome.html<br/>~252KB Standalone"]
    WidgetOut["dist/web/gradio-widget.html<br/>Embedded Widget"]
    
    ViteConfig --> Plugins
    Plugins --> EnvCheck
    
    EnvCheck -->|"undefined"| MainBuild
    EnvCheck -->|"'mcp-welcome'"| WelcomeBuild
    EnvCheck -->|"'gradio-widget'"| WidgetBuild
    
    MainBuild --> MainOut
    WelcomeBuild --> WelcomeOut
    WidgetBuild --> WidgetOut
```

The `viteSingleFile()` plugin inlines all CSS and JavaScript into a single HTML file, which is required for:
- **mcp-welcome.html**: A self-contained welcome page served at `/` when no `Accept: application/json` header is present
- **gradio-widget.html**: Embedded in MCP responses for OpenAI Apps SDK compatibility

**Sources**: [packages/app/vite.config.ts:1-47](), [packages/app/package.json:37-39]()

### Docker Build Process

The Dockerfile demonstrates the complete build pipeline in a containerized environment:

```mermaid
sequenceDiagram
    participant Docker
    participant PNPM
    participant Build
    participant Verify
    
    Docker->>PNPM: corepack enable pnpm
    Docker->>PNPM: COPY workspace files
    Docker->>PNPM: pnpm install --frozen-lockfile
    
    Docker->>Build: rm -rf dist/ (clean)
    Docker->>Build: pnpm run build
    Note over Build: 1. Build mcp library<br/>2. Build server<br/>3. Build web
    
    Docker->>Build: pnpm run build:mcp-welcome
    Note over Build: Rebuild to ensure<br/>self-contained
    
    Docker->>Verify: wc -c mcp-welcome.html
    Verify-->>Docker: Should be ~252KB
    
    Docker->>Verify: ls -la dist/
    Note over Verify: Verify all artifacts<br/>present
```

The Docker build explicitly rebuilds `mcp-welcome.html` as a final step to ensure it's self-contained with all assets inlined. The verification step checks that the file is approximately 252KB, indicating successful asset inlining.

**Sources**: [Dockerfile:1-67](), [packages/app/package.json:37-39]()

---

## Development Workflow

The project provides multiple development modes optimized for different workflows. Each mode supports hot-reload capabilities through TypeScript watch mode or Vite HMR.

### Setting Up the Development Environment

```bash
# 1. Enable Corepack (ensures correct pnpm version)
corepack enable

# 2. Install dependencies
pnpm install

# 3. Initial build (required before dev mode)
pnpm build

# 4. Start development mode
pnpm dev
```

The `corepack enable` command respects the `packageManager` field in `package.json` (pnpm@10.15.1), ensuring consistent tooling across developers.

**Sources**: [package.json:6](), [README.md:173-196]()

### Development Scripts and Watch Modes

The root workspace provides concurrent development scripts that watch both packages simultaneously:

| Command | Description | Transport | Hot Reload |
|---------|-------------|-----------|------------|
| `pnpm dev` | Default HTTP server + HMR | StreamableHTTP | ✓ Web UI + Server |
| `pnpm dev:watch` | Full watch mode | StreamableHTTP | ✓ Library + Server + Web |
| `pnpm dev:stdio` | STDIO transport | STDIO | ✓ Library + Server |
| `pnpm dev:sse` | SSE transport | SSE | ✓ Library + Server |
| `pnpm dev:json` | JSON mode | StreamableHTTPJson | ✓ Library + Server |

The `dev:watch` mode provides the most comprehensive hot-reload experience:

```bash
pnpm dev:watch
# Runs concurrently:
# 1. tsc -p tsconfig.server.json --watch
# 2. vite build --watch
# 3. nodemon dist/server/streamableHttp.js --json
```

**Sources**: [package.json:7-12](), [packages/app/package.json:46]()

### Hot Reload Architecture

```mermaid
graph TB
    subgraph "Developer Changes"
        LibEdit["Edit packages/mcp/src/*.ts"]
        ServerEdit["Edit packages/app/src/server/*.ts"]
        WebEdit["Edit packages/app/src/web/*.tsx"]
    end
    
    subgraph "Watch Processes"
        LibWatch["tsc --watch<br/>packages/mcp"]
        ServerWatch["tsc --watch<br/>tsconfig.server.json"]
        ViteWatch["vite build --watch<br/>Web Assets"]
    end
    
    subgraph "Reload Mechanisms"
        Nodemon["nodemon<br/>Restart on .js changes"]
        ViteHMR["Vite HMR<br/>React Fast Refresh"]
    end
    
    subgraph "Running Processes"
        McpServer["MCP Server Process<br/>dist/server/*.js"]
        Browser["Browser<br/>localhost:3000"]
    end
    
    LibEdit --> LibWatch
    ServerEdit --> ServerWatch
    WebEdit --> ViteWatch
    
    LibWatch -.triggers.- Nodemon
    ServerWatch -.triggers.- Nodemon
    ViteWatch --> ViteHMR
    
    Nodemon --> McpServer
    ViteHMR --> Browser
    
    McpServer --> Browser
```

**Key behaviors**:
- **TypeScript changes** (`.ts` files): Trigger recompilation → nodemon detects `.js` changes → server restarts
- **React component changes** (`.tsx` files): Vite HMR updates browser without full reload
- **Gradio widget changes**: Requires `pnpm dev:widget` for isolated HMR

**Sources**: [packages/app/package.json:40-46](), [README.md:159-171]()

### Isolated Widget Development

For developing Gradio widget components used in OpenAI Apps SDK integration:

```bash
cd packages/app
pnpm dev:widget
# Opens http://localhost:5173/gradio-widget-dev.html
```

This mode serves `gradio-widget-dev.html` with full Vite HMR, allowing rapid iteration on the widget UI. The development page includes test harnesses for sending structured content to components.

**Sources**: [packages/app/package.json:42](), [README.md:159-171](), [packages/app/vite.config.ts:41]()

### Running Specific Transports

Each transport can be run independently in development mode:

**STDIO Transport** (single process, stdin/stdout):
```bash
pnpm dev:stdio
# or directly:
cd packages/app
pnpm dev:stdio
```

**SSE Transport** (stateful, GET /sse + POST /message):
```bash
pnpm dev:sse
```

**HTTP Transport** (stateful, POST/GET/DELETE /mcp):
```bash
pnpm dev
```

**Stateless JSON Mode** (per-request isolation):
```bash
pnpm dev:json
```

The transport selection determines which `dist/server/*.js` file is executed. All transports serve the web dashboard on port 3000 except STDIO.

**Sources**: [packages/app/package.json:40-46](), [start.sh:33-58]()

---

## Testing

The project uses Vitest for unit and integration testing. Tests are located alongside source files and run in Node.js environment with TypeScript support.

### Test Infrastructure

**Vitest Configuration**:
- Runs in Node.js environment (not browser)
- TypeScript support via `tsx`
- ESM module resolution
- Test files: `**/*.test.ts` or `**/*.spec.ts`

**Running Tests**:

```bash
# Run all tests (both packages)
pnpm test

# Run tests in specific package
pnpm --filter=@llmindset/hf-mcp test
pnpm --filter=@llmindset/hf-mcp-server test

# Watch mode (auto-rerun on changes)
cd packages/mcp
pnpm test --watch
```

**Sources**: [package.json:15](), [packages/app/package.json:51](), [packages/mcp/package.json:27]()

### Test Patterns

```mermaid
graph TB
    subgraph "Test Categories"
        ToolTests["Tool Implementation Tests<br/>packages/mcp/src/*.test.ts"]
        ApiTests["API Call Tests<br/>Mock HF API responses"]
        SchemaTests["Schema Validation Tests<br/>Zod schema edge cases"]
        TransportTests["Transport Layer Tests<br/>packages/app/src/server/*.test.ts"]
    end
    
    subgraph "Test Utilities"
        MockHF["Mock HfApiCall<br/>Stub API responses"]
        TestHelpers["Test Helpers<br/>Factory functions"]
        Fixtures["Test Fixtures<br/>Sample data"]
    end
    
    ToolTests --> MockHF
    ApiTests --> MockHF
    SchemaTests --> Fixtures
    TransportTests --> TestHelpers
```

**Common patterns observed**:
- **Tool tests**: Mock `HfApiCall` base class to test tool logic without network calls
- **Error handling**: Verify friendly error messages via `explain()` function
- **Schema validation**: Test Zod schemas with valid and invalid inputs
- **Integration tests**: Test full request/response cycles with mock transports

**Example test structure** (inferred from codebase patterns):
```typescript
// Tool test pattern
describe('DuplicateSpaceTool', () => {
  it('normalizes space names correctly', () => {
    const tool = new DuplicateSpaceTool(token, 'username');
    expect(tool.normalizeSpaceName('space-name'))
      .toBe('username/space-name');
  });
});
```

**Sources**: [packages/mcp/src/duplicate-space.ts:74-259](), [packages/mcp/src/error-messages.ts:1-58]()

### Linting and Type Checking

```bash
# Lint all packages (with auto-fix)
pnpm lint

# Check linting without changes
pnpm lint:check

# Type check all packages
pnpm typecheck

# Format code
pnpm format
pnpm format:check
```

The linting setup uses:
- **ESLint** with TypeScript support
- **Prettier** for code formatting
- **typescript-eslint** for TypeScript-specific rules

**Sources**: [package.json:16-20](), [packages/app/package.json:52-54]()

---

## Project Structure

The monorepo is organized into two main packages with clear separation of concerns:

### Directory Layout

```
hf-mcp-server/
├── package.json                    # Root workspace config
├── pnpm-workspace.yaml             # Workspace definition
├── pnpm-lock.yaml                  # Locked dependencies
├── Dockerfile                      # Production container
├── start.sh                        # Container entrypoint
│
├── packages/mcp/                   # Core library (@llmindset/hf-mcp)
│   ├── package.json                # Library package config
│   ├── tsconfig.json               # TypeScript config
│   ├── src/
│   │   ├── index.ts                # Main export
│   │   ├── hf-api-call.ts          # Base class for API calls
│   │   ├── error-messages.ts       # Friendly error handling
│   │   ├── tool-ids.ts             # Tool registry
│   │   ├── utilities.ts            # Shared utilities
│   │   ├── model-search.ts         # Model search tool
│   │   ├── dataset-search.ts       # Dataset search tool
│   │   ├── paper-search.ts         # Paper search tool
│   │   ├── duplicate-space.ts      # Space duplication tool
│   │   ├── semantic-search.ts      # Space semantic search
│   │   ├── doc-search.ts           # Documentation search
│   │   ├── doc-fetch.ts            # Doc fetch & convert
│   │   ├── gradio-*.ts             # Gradio integration
│   │   └── *.test.ts               # Unit tests
│   └── dist/                       # Compiled outputs
│
└── packages/app/                   # Application layer
    ├── package.json                # App package config
    ├── tsconfig.json               # General TypeScript config
    ├── tsconfig.server.json        # Server-specific config
    ├── vite.config.ts              # Vite bundler config
    ├── components.json             # UI component config
    ├── src/
    │   ├── server/                 # Server entrypoints
    │   │   ├── stdio.ts            # STDIO transport entry
    │   │   ├── sse.ts              # SSE transport entry
    │   │   ├── streamableHttp.ts   # HTTP transport entry
    │   │   ├── streamableHttpJson.ts # JSON mode entry
    │   │   ├── lib/                # Server libraries
    │   │   │   ├── application.ts  # Application orchestrator
    │   │   │   ├── webserver.ts    # Express server
    │   │   │   ├── transports/     # Transport implementations
    │   │   │   ├── mcp/            # MCP server factory
    │   │   │   ├── tools/          # Tool selection
    │   │   │   └── settings/       # Settings service
    │   │   └── *.test.ts           # Server tests
    │   │
    │   └── web/                    # Web UI
    │       ├── index.html          # Main dashboard entry
    │       ├── mcp-welcome.html    # Welcome page entry
    │       ├── gradio-widget.html  # Widget entry
    │       ├── gradio-widget-dev.html # Widget dev harness
    │       ├── main.tsx            # React app entry
    │       ├── components/         # React components
    │       │   ├── ui/             # Base UI components
    │       │   ├── metrics/        # Metrics cards
    │       │   └── settings/       # Settings UI
    │       ├── hooks/              # React hooks
    │       └── lib/                # Web utilities
    │
    └── dist/                       # Build outputs
        ├── server/                 # Compiled server code
        │   ├── stdio.js
        │   ├── sse.js
        │   └── streamableHttp.js
        └── web/                    # Bundled web assets
            ├── index.html
            ├── mcp-welcome.html    # ~252KB self-contained
            ├── gradio-widget.html  # Embedded widget
            └── assets/             # CSS/JS chunks
```

**Sources**: [packages/app/package.json:6-14](), [packages/mcp/package.json:7-23](), [Dockerfile:1-67]()

### Component Location Map

This diagram maps high-level system concepts to their actual file locations:

```mermaid
graph TB
    subgraph "Architectural Concepts"
        Transport["Transport Layer<br/>STDIO, SSE, HTTP"]
        McpCore["MCP Server Core<br/>Server Factory"]
        ToolSel["Tool Selection<br/>Bouquet System"]
        BuiltInTools["Built-in Tools<br/>15+ Tools"]
        GradioInt["Gradio Integration<br/>Dynamic Tools"]
        WebUI["Web Dashboard<br/>React UI"]
        Settings["Settings Service<br/>User Config"]
    end
    
    subgraph "File Locations"
        TransportFiles["packages/app/src/server/lib/transports/<br/>- BaseTransport.ts<br/>- StatefulTransport.ts<br/>- STDIOTransport.ts<br/>- SSETransport.ts<br/>- StreamableHTTPTransport.ts<br/>- StatelessHTTPTransport.ts"]
        
        McpFiles["packages/app/src/server/lib/mcp/<br/>- createServerFactory.ts<br/>- createProxyServerFactory.ts<br/>- McpApiClient.ts"]
        
        ToolSelFiles["packages/app/src/server/lib/tools/<br/>- ToolSelectionStrategy.ts<br/>- bouquets.ts"]
        
        ToolFiles["packages/mcp/src/<br/>- model-search.ts<br/>- dataset-search.ts<br/>- paper-search.ts<br/>- duplicate-space.ts<br/>- semantic-search.ts<br/>- doc-search.ts<br/>- doc-fetch.ts<br/>+ tool-ids.ts (registry)"]
        
        GradioFiles["packages/mcp/src/<br/>- gradio-endpoint-connector.ts<br/>- gradio-utils.ts<br/>- use-space-tool.ts"]
        
        WebFiles["packages/app/src/web/<br/>- components/metrics/<br/>- components/settings/<br/>- components/ui/<br/>- hooks/"]
        
        SettingsFiles["packages/app/src/server/lib/settings/<br/>- settingsService.ts"]
    end
    
    Transport --> TransportFiles
    McpCore --> McpFiles
    ToolSel --> ToolSelFiles
    BuiltInTools --> ToolFiles
    GradioInt --> GradioFiles
    WebUI --> WebFiles
    Settings --> SettingsFiles
```

**Sources**: [packages/app/package.json:1-111](), [packages/mcp/package.json:1-53]()

### Package Responsibilities

**`@llmindset/hf-mcp` (packages/mcp)**:
- Tool implementations (search, detail, space management, docs)
- Gradio integration logic (schema parsing, endpoint connectors)
- API call abstractions (`HfApiCall` base class)
- Error handling utilities (`explain()`, friendly messages)
- Type definitions and Zod schemas
- Exports: Library API for external consumers

**`@llmindset/hf-mcp-server` (packages/app)**:
- Transport layer implementations (STDIO, SSE, HTTP)
- MCP server factory pattern (`createServerFactory`, `createProxyServerFactory`)
- Tool selection strategy and bouquet system
- Settings service (internal and external storage)
- Web dashboard (React + TailwindCSS)
- Single-file builds (mcp-welcome, gradio-widget)
- Express server and API routes
- Application orchestrator (`Application` class)

The dependency flow is unidirectional: `packages/app` depends on `packages/mcp`, but not vice versa. This allows `packages/mcp` to be consumed independently by other MCP server implementations.

**Sources**: [packages/app/package.json:59](), [packages/mcp/package.json:7-23]()

### Configuration Files

| File | Purpose | Key Settings |
|------|---------|--------------|
| `package.json` (root) | Workspace config | `packageManager: pnpm@10.15.1`, workspace scripts |
| `pnpm-workspace.yaml` | Package discovery | `packages/*` |
| `packages/app/tsconfig.json` | Web UI TypeScript | React JSX, strict mode |
| `packages/app/tsconfig.server.json` | Server TypeScript | Node.js target, excludes web |
| `packages/mcp/tsconfig.json` | Library TypeScript | ES modules, declaration files |
| `vite.config.ts` | Vite bundler | React, Tailwind, singleFile plugin |
| `components.json` | shadcn/ui config | Component path aliases |
| `.dockerignore` | Docker exclusions | `node_modules`, `dist`, `.git` |

**Sources**: [package.json:1-38](), [packages/app/package.json:1-111](), [packages/app/vite.config.ts:1-47](), [.dockerignore:1-18]()

---

## Advanced Build Scenarios

### Clean Build

For a completely clean build from scratch:

```bash
pnpm clean    # Remove all dist/ directories
pnpm build    # Full rebuild
```

This is recommended after:
- Switching branches with significant changes
- Updating dependencies (`pnpm install`)
- Resolving build errors

**Sources**: [package.json:22]()

### Single Package Builds

Build individual packages without building dependencies:

```bash
# Build only the mcp library
pnpm --filter=@llmindset/hf-mcp build

# Build only the app
pnpm --filter=@llmindset/hf-mcp-server build

# Build specific app components
cd packages/app
pnpm build:server      # Server only
pnpm build:web         # Web UI only
pnpm build:singlefiles # Self-contained pages only
```

**Sources**: [packages/app/package.json:34-39]()

### Production Build Verification

The Docker build includes verification steps to ensure artifacts are correct:

```bash
# Check mcp-welcome.html is self-contained
wc -c packages/app/dist/web/mcp-welcome.html
# Should output ~252000 (252KB)

# Verify all expected outputs exist
ls -la packages/app/dist/server/
ls -la packages/app/dist/web/
```

If `mcp-welcome.html` is significantly smaller (e.g., <50KB), assets were not inlined correctly and the build should be re-run.

**Sources**: [Dockerfile:32-36]()

---

# Page: Build System

# Build System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.dockerignore](.dockerignore)
- [Dockerfile](Dockerfile)
- [README.md](README.md)
- [package.json](package.json)
- [packages/app/package.json](packages/app/package.json)
- [packages/app/vite.config.ts](packages/app/vite.config.ts)
- [packages/mcp/package.json](packages/mcp/package.json)
- [packages/mcp/src/duplicate-space.ts](packages/mcp/src/duplicate-space.ts)
- [packages/mcp/src/error-messages.ts](packages/mcp/src/error-messages.ts)
- [pnpm-lock.yaml](pnpm-lock.yaml)
- [start.sh](start.sh)

</details>



This document describes the monorepo build pipeline, compilation processes, and artifact generation for the HF MCP Server project. The build system orchestrates TypeScript compilation, Vite bundling, and multiple specialized build targets to produce server binaries, web assets, and self-contained HTML files.

For information about development workflows and watch modes, see [Development Workflow](#9.2). For the overall project structure, see [Project Structure](#9.4).

---

## Build Architecture Overview

The HF MCP Server uses a multi-stage build pipeline that separates library compilation from application bundling. The build system produces three categories of artifacts: TypeScript-compiled server code, Vite-bundled web assets, and self-contained single-file HTML applications.

```mermaid
graph TB
    subgraph "Source Code"
        McpSrc["packages/mcp/src/**/*.ts<br/>Library Code"]
        AppServerSrc["packages/app/src/server/**/*.ts<br/>Server Code"]
        AppWebSrc["packages/app/src/web/**/*<br/>React Components"]
    end
    
    subgraph "Build Tools"
        TSC["tsc<br/>TypeScript Compiler"]
        Vite["vite build<br/>Bundler"]
        SingleFile["vite-plugin-singlefile<br/>Inliner"]
    end
    
    subgraph "Build Targets"
        McpLib["packages/mcp/dist/**/*.js<br/>Compiled Library"]
        ServerBin["packages/app/dist/server/*.js<br/>Server Binaries"]
        WebAssets["packages/app/dist/web/**/*<br/>Static Assets"]
        McpWelcome["packages/app/dist/web/mcp-welcome.html<br/>Self-contained ~252KB"]
        GradioWidget["packages/app/dist/web/gradio-widget.html<br/>Self-contained"]
    end
    
    McpSrc --> TSC
    TSC --> McpLib
    
    AppServerSrc --> TSC
    TSC --> ServerBin
    
    AppWebSrc --> Vite
    Vite --> WebAssets
    
    AppWebSrc --> Vite
    Vite --> SingleFile
    SingleFile --> McpWelcome
    SingleFile --> GradioWidget
    
    ServerBin -.depends on.- McpLib
```

**Sources:** [package.json:7-24](), [packages/app/package.json:33-39](), [packages/mcp/package.json:25-32]()

---

## Monorepo Structure

The project uses pnpm workspaces with two packages. The workspace configuration enforces proper dependency resolution and enables cross-package builds.

| Package | Purpose | Build Tool | Output |
|---------|---------|------------|--------|
| `@llmindset/hf-mcp` | Core MCP tool implementations | `tsc` | `packages/mcp/dist/` |
| `@llmindset/hf-mcp-server` | Application layer, transports, web UI | `tsc` + `vite` | `packages/app/dist/server/` and `packages/app/dist/web/` |

```mermaid
graph LR
    subgraph "Root Workspace"
        PnpmWorkspace["pnpm-workspace.yaml<br/>Package Manager Config"]
        RootPkg["package.json<br/>Workspace Scripts"]
    end
    
    subgraph "packages/mcp"
        McpPkg["package.json<br/>@llmindset/hf-mcp"]
        McpTsConfig["tsconfig.json<br/>Library Config"]
        McpDist["dist/<br/>Compiled Output"]
    end
    
    subgraph "packages/app"
        AppPkg["package.json<br/>@llmindset/hf-mcp-server"]
        AppTsConfig["tsconfig.server.json<br/>Server Config"]
        ViteConfig["vite.config.ts<br/>Web Config"]
        AppDist["dist/server/<br/>Server Binaries"]
        AppWeb["dist/web/<br/>Web Assets"]
    end
    
    RootPkg -->|"pnpm -r build"| McpPkg
    RootPkg -->|"pnpm -r build"| AppPkg
    
    McpPkg -->|"tsc --declaration"| McpDist
    AppPkg -->|"tsc -p tsconfig.server.json"| AppDist
    AppPkg -->|"vite build"| AppWeb
    
    AppPkg -.workspace dependency.- McpPkg
```

The workspace configuration uses pnpm's `workspace:^` protocol to link `@llmindset/hf-mcp` into `@llmindset/hf-mcp-server`, ensuring the application always builds against the local library version.

**Sources:** [package.json:1-38](), [packages/app/package.json:59](), [packages/mcp/package.json:2-3](), [pnpm-lock.yaml:47-49]()

---

## Build Scripts Hierarchy

Build commands cascade from the root workspace down to individual packages. The root `build` command orchestrates all package builds in dependency order.

```mermaid
graph TB
    subgraph "Root Scripts<br/>(package.json)"
        RootBuild["pnpm build"]
        RootClean["pnpm clean"]
        RootTest["pnpm test"]
    end
    
    subgraph "MCP Package Scripts<br/>(packages/mcp/package.json)"
        McpBuild["pnpm build<br/>→ tsc --declaration"]
        McpClean["pnpm clean<br/>→ rimraf dist"]
        McpTest["pnpm test<br/>→ vitest run"]
    end
    
    subgraph "App Package Scripts<br/>(packages/app/package.json)"
        AppBuild["pnpm build"]
        AppBuildServer["pnpm build:server<br/>→ tsc -p tsconfig.server.json"]
        AppBuildWeb["pnpm build:web<br/>→ vite build"]
        AppBuildSingle["pnpm build:singlefiles"]
        AppBuildWelcome["pnpm build:mcp-welcome<br/>→ VITE_BUILD_TARGET=mcp-welcome vite build"]
        AppBuildWidget["pnpm build:gradio-widget<br/>→ VITE_BUILD_TARGET=gradio-widget vite build<br/>→ node scripts/html-to-ts.js"]
        AppClean["pnpm clean<br/>→ rimraf dist"]
    end
    
    RootBuild -->|"pnpm -r build"| McpBuild
    RootBuild -->|"pnpm -r build"| AppBuild
    RootClean -->|"pnpm run -r clean"| McpClean
    RootClean -->|"pnpm run -r clean"| AppClean
    RootTest -->|"pnpm run -r test"| McpTest
    
    AppBuild --> AppBuildWeb
    AppBuild --> AppBuildSingle
    AppBuild --> AppBuildServer
    
    AppBuildSingle --> AppBuildWelcome
    AppBuildSingle --> AppBuildWidget
```

The `-r` flag in root scripts executes commands recursively in all workspace packages. Build order respects workspace dependencies automatically.

**Sources:** [package.json:21-24](), [packages/app/package.json:33-39](), [packages/mcp/package.json:25-32]()

---

## TypeScript Compilation Pipeline

Both packages use the TypeScript compiler directly without intermediate bundlers for server-side code. Each package has distinct `tsconfig.json` configurations.

### Library Compilation (packages/mcp)

The `@llmindset/hf-mcp` package compiles with declaration files for type exports:

```mermaid
graph LR
    TsSrc["src/**/*.ts<br/>Tool Implementations"]
    TscLib["tsc --declaration"]
    DistJs["dist/**/*.js<br/>CommonJS Output"]
    DistDts["dist/**/*.d.ts<br/>Type Declarations"]
    
    TsSrc --> TscLib
    TscLib --> DistJs
    TscLib --> DistDts
```

The package exports multiple entry points via the `exports` field, enabling selective imports:

- **Main entry**: `dist/index.js` with types `dist/index.d.ts`
- **Semantic search**: `dist/semantic-search.js` 
- **Model tools**: `dist/model-search.js`
- **Paper tools**: `dist/paper-search.js`

**Sources:** [packages/mcp/package.json:5-23](), [packages/mcp/package.json:26]()

### Server Compilation (packages/app)

The application server code compiles using `tsconfig.server.json` which targets Node.js:

```mermaid
graph LR
    ServerSrc["src/server/**/*.ts<br/>Transport Implementations"]
    McpLib["packages/mcp/dist/**/*.js<br/>Imported Tools"]
    TscApp["tsc -p tsconfig.server.json"]
    ServerDist["dist/server/**/*.js<br/>Entry Points"]
    
    ServerSrc --> TscApp
    McpLib -.imported by.- ServerSrc
    TscApp --> ServerDist
    
    ServerDist --> Stdio["stdio.js"]
    ServerDist --> Sse["sse.js"] 
    ServerDist --> StreamHttp["streamableHttp.js"]
    ServerDist --> StreamHttpJson["streamableHttpJson.js"]
```

The compilation produces four distinct entry point binaries exposed via the `bin` field in `package.json`:

- `hf-mcp-server` → `dist/server/stdio.js`
- `hf-mcp-server-http` → `dist/server/streamableHttp.js`
- `hf-mcp-server-http-json` → `dist/server/streamableHttpJson.js`

**Sources:** [packages/app/package.json:6-10](), [packages/app/package.json:35]()

---

## Vite Build Pipeline

Vite handles all web asset bundling, including the React dashboard and specialized single-file builds. The configuration uses conditional plugin loading based on `VITE_BUILD_TARGET` environment variables.

### Standard Web Build

The default build produces the monitoring dashboard with code splitting:

```mermaid
graph TB
    subgraph "Source Files"
        IndexHtml["src/web/index.html<br/>Entry Point"]
        ReactApp["src/web/main.tsx<br/>React Root"]
        Components["src/web/components/**/*<br/>UI Components"]
        DevHtml["src/web/gradio-widget-dev.html<br/>Dev Harness"]
    end
    
    subgraph "Vite Pipeline"
        ViteConfig["vite.config.ts<br/>Build Configuration"]
        ReactPlugin["@vitejs/plugin-react-swc<br/>JSX Transform"]
        TailwindPlugin["@tailwindcss/vite<br/>CSS Processing"]
        RollupOpts["rollupOptions<br/>Multi-entry Config"]
    end
    
    subgraph "Output Assets"
        DistIndex["dist/web/index.html"]
        DistJs["dist/web/assets/**/*.js<br/>Code-split Bundles"]
        DistCss["dist/web/assets/**/*.css<br/>Processed Styles"]
        DistDevHtml["dist/web/gradio-widget-dev.html"]
    end
    
    IndexHtml --> ViteConfig
    ReactApp --> ViteConfig
    Components --> ViteConfig
    DevHtml --> ViteConfig
    
    ViteConfig --> ReactPlugin
    ViteConfig --> TailwindPlugin
    ViteConfig --> RollupOpts
    
    ReactPlugin --> DistJs
    TailwindPlugin --> DistCss
    RollupOpts --> DistIndex
    RollupOpts --> DistDevHtml
```

The `vite.config.ts` excludes `mcp-welcome.html` and `gradio-widget.html` from the main build to prevent interference with single-file builds.

**Sources:** [packages/app/vite.config.ts:1-47](), [packages/app/package.json:36]()

### Single-File Builds

Two specialized builds produce self-contained HTML files with all assets inlined. These use the `vite-plugin-singlefile` plugin to embed JavaScript, CSS, and images directly into the HTML.

```mermaid
graph TB
    subgraph "Build Targets"
        McpWelcomeBuild["VITE_BUILD_TARGET=mcp-welcome<br/>vite build"]
        GradioWidgetBuild["VITE_BUILD_TARGET=gradio-widget<br/>vite build"]
    end
    
    subgraph "Source Entry Points"
        WelcomeHtml["src/web/mcp-welcome.html"]
        WidgetHtml["src/web/gradio-widget.html"]
    end
    
    subgraph "Vite Plugins"
        SingleFilePlugin["viteSingleFile()<br/>Inline All Assets"]
    end
    
    subgraph "Outputs"
        WelcomeDist["dist/web/mcp-welcome.html<br/>~252KB Self-contained"]
        WidgetDist["dist/web/gradio-widget.html<br/>Self-contained"]
        WidgetTs["src/web/gradio-widget-html.ts<br/>TypeScript Constant"]
    end
    
    McpWelcomeBuild --> WelcomeHtml
    GradioWidgetBuild --> WidgetHtml
    
    WelcomeHtml --> SingleFilePlugin
    WidgetHtml --> SingleFilePlugin
    
    SingleFilePlugin --> WelcomeDist
    SingleFilePlugin --> WidgetDist
    
    WidgetDist -->|"node scripts/html-to-ts.js"| WidgetTs
```

The `vite.config.ts` file conditionally applies the `viteSingleFile()` plugin based on the `VITE_BUILD_TARGET` environment variable:

- **mcp-welcome**: Standalone landing page served to HTTP clients in stateless mode
- **gradio-widget**: OpenAI Apps SDK component for rendering Gradio structured content

After building `gradio-widget.html`, a post-processing script converts it to a TypeScript constant exported from `src/web/gradio-widget-html.ts` for embedding in server responses.

**Sources:** [packages/app/vite.config.ts:8-20](), [packages/app/vite.config.ts:29-42](), [packages/app/package.json:37-39](), [Dockerfile:29-35]()

---

## Build Output Structure

The build process generates artifacts in distinct directories with strict separation between server and web outputs:

```
packages/
├── mcp/
│   └── dist/                      # Library compilation output
│       ├── index.js               # Main export
│       ├── index.d.ts             # Type declarations
│       ├── semantic-search.js     # Sub-entry point
│       ├── model-search.js        # Sub-entry point
│       └── ...                    # Other tool implementations
│
└── app/
    └── dist/
        ├── server/                # Server binary output
        │   ├── stdio.js           # STDIO transport entry
        │   ├── sse.js             # SSE transport entry
        │   ├── streamableHttp.js  # HTTP transport entry
        │   └── ...                # Supporting modules
        │
        └── web/                   # Web asset output
            ├── index.html         # Main dashboard
            ├── assets/            # Code-split bundles
            │   ├── index-*.js
            │   └── index-*.css
            ├── mcp-welcome.html   # Self-contained landing
            ├── gradio-widget.html # Self-contained widget
            └── gradio-widget-dev.html  # Dev harness
```

The `emptyOutDir: false` setting in Vite configuration prevents deletion of the `server/` directory during web builds, allowing both outputs to coexist.

**Sources:** [packages/app/vite.config.ts:30-31](), [packages/app/package.json:6-10](), [packages/app/package.json:12-15]()

---

## Docker Build Process

The Dockerfile orchestrates a complete monorepo build in a containerized environment. The build process includes artifact verification steps to ensure single-file builds are self-contained.

```mermaid
graph TB
    subgraph "Dockerfile Stages"
        BaseImage["FROM node:22-alpine<br/>Corepack + pnpm enabled"]
        
        CopyPkg["COPY package files<br/>pnpm-workspace.yaml<br/>pnpm-lock.yaml<br/>package.json (all levels)"]
        
        Install["RUN pnpm install --frozen-lockfile"]
        
        CopySrc["COPY source code<br/>COPY . ."]
        
        CleanBuild["RUN rm -rf ./packages/*/dist"]
        
        BuildAll["RUN pnpm run build<br/>(builds both packages)"]
        
        RebuildWelcome["RUN cd packages/app<br/>pnpm run build:mcp-welcome"]
        
        Verify["RUN wc -c dist/web/mcp-welcome.html<br/>Should be ~252KB"]
        
        ListFiles["RUN find/ls debugging<br/>Verify output structure"]
        
        SetEnv["ENV NODE_ENV=production<br/>ENV TRANSPORT=streamableHttpJson"]
        
        StartCmd["CMD /bin/sh ./start.sh"]
    end
    
    BaseImage --> CopyPkg
    CopyPkg --> Install
    Install --> CopySrc
    CopySrc --> CleanBuild
    CleanBuild --> BuildAll
    BuildAll --> RebuildWelcome
    RebuildWelcome --> Verify
    Verify --> ListFiles
    ListFiles --> SetEnv
    SetEnv --> StartCmd
```

The Docker build includes explicit verification that `mcp-welcome.html` reaches approximately 252KB, confirming all assets are properly inlined. The rebuild step ensures the self-contained page is generated last, after all other builds complete.

**Sources:** [Dockerfile:1-67](), [start.sh:1-58]()

### Docker Build Commands

Key build phases from the Dockerfile:

1. **Install dependencies** (line 13): `pnpm install --frozen-lockfile`
2. **Clean artifacts** (line 20-21): `rm -rf ./packages/*/dist`
3. **Full build** (line 24-26): `pnpm run build`
4. **Rebuild welcome page** (line 29-31): `pnpm run build:mcp-welcome`
5. **Verify size** (line 33-35): `wc -c dist/web/mcp-welcome.html`

The startup script `start.sh` determines which server binary to execute based on the `TRANSPORT` environment variable, defaulting to `streamableHttpJson` in Docker deployments.

**Sources:** [Dockerfile:13-47](), [start.sh:1-58]()

---

## Build Validation

The build system includes file size verification for single-file builds to ensure assets are properly embedded:

| Target | Expected Size | Validation |
|--------|---------------|------------|
| `mcp-welcome.html` | ~252KB | Docker build checks file size with `wc -c` |
| `gradio-widget.html` | Variable | Post-processed to TypeScript constant |

The size verification in the Docker build serves as a canary for detecting issues with the `vite-plugin-singlefile` inlining process. If the file is significantly smaller, it likely indicates external asset references that weren't inlined.

**Sources:** [Dockerfile:33-35](), [README.md:29-35]()

---

## Published Artifacts

The `@llmindset/hf-mcp-server` package publishes specific files defined in the `files` field:

```json
"files": [
  "dist/**/*",
  "components.json"
]
```

This includes:
- All compiled server code (`dist/server/**/*.js`)
- All web assets (`dist/web/**/*`)
- Component configuration for UI library

The `main` field points to `dist/server/streamableHttp.js` as the default entry point when imported as a library, though the primary usage is via the `bin` executables.

**Sources:** [packages/app/package.json:6](), [packages/app/package.json:12-15]()

---

# Page: Development Workflow

# Development Workflow

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [package.json](package.json)
- [packages/app/package.json](packages/app/package.json)
- [packages/mcp/package.json](packages/mcp/package.json)
- [pnpm-lock.yaml](pnpm-lock.yaml)

</details>



This document describes the development workflow for the HF MCP Server codebase, including hot reload setup, concurrent watch modes, development scripts, and debugging patterns. For information about the build system and production compilation, see [Build System](#9.1). For testing infrastructure, see [Testing](#9.3).

## Overview

The HF MCP Server uses a monorepo structure with two packages that require different compilation strategies. The development workflow is designed to support rapid iteration through:

- **TypeScript watch mode** for server-side code compilation
- **Vite HMR** (Hot Module Replacement) for web UI development
- **Nodemon** for automatic server restarts
- **Concurrent execution** of multiple watch processes
- **Transport-specific dev modes** for testing different client connection types

---

## Development Scripts Reference

The project provides multiple development entry points through npm scripts defined across three `package.json` files. The scripts are organized hierarchically from root to package-specific commands.

### Root-Level Development Scripts

The root [package.json:7-12]() defines monorepo-wide development commands:

| Script | Purpose | Packages Involved |
|--------|---------|-------------------|
| `pnpm dev` | Default development mode (HTTP transport) | `@llmindset/hf-mcp`, `@llmindset/hf-mcp-server` |
| `pnpm dev:sse` | SSE transport development | Both packages |
| `pnpm dev:json` | Stateless JSON transport development | Both packages |
| `pnpm dev:watch` | Full hot-reload watch mode | Both packages |
| `pnpm dev:stdio` | STDIO transport development | Both packages |

Each root script executes corresponding scripts in both packages concurrently using the `concurrently` utility.

### Application Package Scripts

The [packages/app/package.json:40-46]() defines application-specific development commands:

| Script | Command | Description |
|--------|---------|-------------|
| `dev` | `build:server && node dist/server/streamableHttp.js` | Build then run HTTP server |
| `dev:vite` | `vite dev` | Run Vite dev server only (port 5173) |
| `dev:widget` | `vite dev` | Run widget dev server |
| `dev:stdio` | `build:server && node dist/server/stdio.js` | Build then run STDIO transport |
| `dev:sse` | `build:server && node dist/server/sse.js` | Build then run SSE transport |
| `dev:json` | `build:server && node dist/server/streamableHttp.js --json` | Build then run stateless JSON mode |
| `dev:watch` | `concurrently "tsc -p tsconfig.server.json --watch" "vite build --watch" "nodemon dist/server/streamableHttp.js --json"` | Full hot-reload mode |

### Library Package Scripts

The [packages/mcp/package.json:28]() defines the library development command:

| Script | Command | Description |
|--------|---------|-------------|
| `dev` | `tsc --watch` | TypeScript watch mode for library compilation |

**Development Script Hierarchy**

```mermaid
graph TB
    subgraph "Root Commands"
        RootDev["pnpm dev<br/>(from root)"]
        RootWatch["pnpm dev:watch<br/>(from root)"]
        RootSSE["pnpm dev:sse"]
        RootJSON["pnpm dev:json"]
        RootStdio["pnpm dev:stdio"]
    end
    
    subgraph "Library Package (@llmindset/hf-mcp)"
        LibDev["pnpm dev<br/>(tsc --watch)"]
    end
    
    subgraph "App Package (@llmindset/hf-mcp-server)"
        AppDev["pnpm dev<br/>(build + run HTTP)"]
        AppWatch["pnpm dev:watch<br/>(tsc + vite + nodemon)"]
        AppSSE["pnpm dev:sse"]
        AppJSON["pnpm dev:json"]
        AppStdio["pnpm dev:stdio"]
    end
    
    RootDev -->|"concurrently"| LibDev
    RootDev -->|"concurrently"| AppDev
    RootWatch -->|"concurrently"| LibDev
    RootWatch -->|"concurrently"| AppWatch
    RootSSE -->|"concurrently"| LibDev
    RootSSE -->|"concurrently"| AppSSE
    RootJSON -->|"concurrently"| LibDev
    RootJSON -->|"concurrently"| AppJSON
    RootStdio -->|"concurrently"| LibDev
    RootStdio -->|"concurrently"| AppStdio
```

Sources: [package.json:7-12](), [packages/app/package.json:40-46](), [packages/mcp/package.json:28]()

---

## Watch Mode Architecture

Watch mode enables continuous development by automatically recompiling and restarting components when source files change. The system uses three concurrent watch processes that operate independently.

### Concurrent Watch Processes

The `dev:watch` script ([packages/app/package.json:46]()) runs three processes simultaneously using `concurrently`:

1. **TypeScript Watch**: `tsc -p tsconfig.server.json --watch`
2. **Vite Watch**: `vite build --watch`
3. **Nodemon**: `nodemon dist/server/streamableHttp.js --json`

**Watch Mode Process Architecture**

```mermaid
graph TB
    subgraph "Source Files"
        ServerTS["Server TypeScript<br/>src/server/*.ts"]
        WebTS["Web TypeScript<br/>src/web/**/*.tsx"]
        SharedTS["Shared Code<br/>src/shared/**/*.ts"]
        LibTS["Library TypeScript<br/>packages/mcp/src/**/*.ts"]
    end
    
    subgraph "Watch Process 1: TypeScript Compiler"
        TSCWatch["tsc --watch<br/>(tsconfig.server.json)"]
        TSCOutput["dist/server/*.js"]
    end
    
    subgraph "Watch Process 2: Vite Bundler"
        ViteWatch["vite build --watch"]
        ViteOutput["dist/web/index.html<br/>dist/web/assets/*.js"]
    end
    
    subgraph "Watch Process 3: Library TypeScript"
        LibTSCWatch["tsc --watch<br/>(in packages/mcp)"]
        LibOutput["packages/mcp/dist/**/*.js"]
    end
    
    subgraph "Process Monitor"
        Nodemon["nodemon<br/>watches: dist/server/**"]
        ServerProcess["Node.js Process<br/>streamableHttp.js"]
    end
    
    ServerTS --> TSCWatch
    SharedTS --> TSCWatch
    TSCWatch --> TSCOutput
    
    WebTS --> ViteWatch
    SharedTS --> ViteWatch
    ViteWatch --> ViteOutput
    
    LibTS --> LibTSCWatch
    LibTSCWatch --> LibOutput
    
    TSCOutput --> Nodemon
    Nodemon -->|"restart on change"| ServerProcess
    ServerProcess -->|"serves"| ViteOutput
```

### File Change Detection Flow

When a developer modifies source files, the following sequence occurs:

```mermaid
sequenceDiagram
    participant Dev as "Developer"
    participant FS as "File System"
    participant TSC as "TypeScript Compiler"
    participant Vite as "Vite Bundler"
    participant Nodemon as "Nodemon Monitor"
    participant Server as "HTTP Server Process"
    participant Browser as "Browser"
    
    Dev->>FS: "Edit src/server/application.ts"
    FS->>TSC: "File change detected"
    TSC->>TSC: "Incremental compilation"
    TSC->>FS: "Write dist/server/application.js"
    FS->>Nodemon: "File change detected"
    Nodemon->>Server: "Kill existing process"
    Nodemon->>Server: "Spawn new process"
    Server->>Server: "Initialize WebServer"
    Server->>Server: "Load static files from dist/web"
    
    Note over Dev,Browser: "Separate: Web UI Changes"
    Dev->>FS: "Edit src/web/App.tsx"
    FS->>Vite: "File change detected"
    Vite->>Vite: "HMR compilation"
    Vite->>FS: "Write dist/web/assets/*.js"
    Vite->>Browser: "HMR update (if dev server running)"
    
    Note over Dev,Browser: "Separate: Library Changes"
    Dev->>FS: "Edit packages/mcp/src/tools/model-search.ts"
    FS->>TSC: "File change in library"
    TSC->>FS: "Write packages/mcp/dist/model-search.js"
    Note over FS,Nodemon: "Nodemon NOT triggered (different directory)"
    Note over Dev,Browser: "Must manually restart server<br/>for library changes"
```

Sources: [packages/app/package.json:46](), [package.json:11]()

---

## Hot Reload Mechanisms

The development environment provides two distinct hot reload mechanisms for different parts of the codebase.

### Server-Side Hot Reload (Nodemon)

Server-side code uses **Nodemon** for automatic process restarts. Nodemon watches the `dist/server` directory and restarts the Node.js process when changes are detected.

**Nodemon Configuration** (inferred from [packages/app/package.json:46]()):

- **Watched directory**: `dist/server/**` (implicit)
- **Entry point**: `dist/server/streamableHttp.js`
- **Restart delay**: Default (usually 1 second)
- **Ignored patterns**: None specified (watches all changes)

**Restart Behavior**:

1. TypeScript compiler writes to `dist/server/*.js`
2. Nodemon detects file change
3. Current server process receives `SIGTERM`
4. New process spawns with fresh module imports
5. WebServer reinitializes (port binding, transport setup)

**Limitations**:

- Full process restart required (no in-place module replacement)
- Active client connections are dropped
- Server state is lost (sessions, metrics)
- Restart time typically 1-3 seconds

### Client-Side Hot Reload (Vite HMR)

Web UI code uses **Vite's Hot Module Replacement** for instant updates without page refresh.

**Vite Dev Server Configuration**:

- **Dev server**: `vite dev` ([packages/app/package.json:41]())
- **Port**: 5173 (default)
- **HMR protocol**: WebSocket
- **Build target**: Modern browsers (ESM)

**HMR Process**:

```mermaid
graph LR
    subgraph "Development Environment"
        Source["React Component<br/>src/web/App.tsx"]
        ViteServer["Vite Dev Server<br/>Port 5173"]
        Browser["Browser<br/>localhost:5173"]
    end
    
    subgraph "HMR Update Flow"
        Change["File Change"]
        Transform["ESBuild Transform"]
        HMRModule["HMR Module"]
        Update["DOM Update"]
    end
    
    Source -->|"edited"| Change
    Change --> Transform
    Transform --> HMRModule
    ViteServer -->|"WebSocket"| Browser
    HMRModule -->|"push update"| Browser
    Browser --> Update
    Update -->|"preserve state"| Browser
```

**React Fast Refresh**:

Vite uses the `@vitejs/plugin-react-swc` plugin ([packages/app/package.json:95]()) which enables React Fast Refresh. This preserves component state during hot updates.

**HMR-Safe Components**:

- Components must be default exports or named exports
- No class components (use function components)
- Hooks must follow React rules
- State preservation works for local component state

Sources: [packages/app/package.json:41](), [packages/app/package.json:95]()

---

## Development Workflow Patterns

### Standard Development Workflow

The typical development workflow for working on both server and web code:

**Step 1: Start Watch Mode**

```bash
# From repository root
pnpm dev:watch
```

This starts three concurrent processes:
- TypeScript compiler watching `packages/mcp/src` and `packages/app/src/server`
- Vite bundler watching `packages/app/src/web`
- Nodemon monitoring `packages/app/dist/server`

**Step 2: Access Development Server**

- **Web UI**: http://localhost:3000
- **API endpoints**: http://localhost:3000/api/*
- **MCP endpoint**: http://localhost:3000/mcp

**Step 3: Make Changes**

- Edit server code → automatic restart via Nodemon
- Edit web code → instant HMR update (if using Vite dev server)
- Edit library code → automatic recompilation, manual server restart required

### Transport-Specific Development

Different MCP clients use different transport mechanisms. Test specific transports during development:

**HTTP Transport Development** ([packages/app/package.json:40]()):

```bash
pnpm dev  # Uses StreamableHTTP transport
```

Access via: `http://localhost:3000/mcp`

**SSE Transport Development** ([packages/app/package.json:44]()):

```bash
pnpm dev:sse
```

Endpoints:
- GET `/sse` - Establish SSE connection
- POST `/message` - Send messages

**STDIO Transport Development** ([packages/app/package.json:43]()):

```bash
pnpm dev:stdio
```

Uses stdin/stdout, suitable for Claude Code integration testing.

**Stateless JSON Mode** ([packages/app/package.json:45]()):

```bash
pnpm dev:json
```

Uses `StatelessHTTPTransport` with no persistent sessions.

### Vite-Only Development

For rapid web UI development without running the full MCP server:

```bash
cd packages/app
pnpm dev:vite
```

This runs only the Vite dev server on port 5173. Use this when:
- Working exclusively on UI components
- Testing visual changes
- Need fastest HMR performance

**Limitation**: API endpoints won't work (mock them or proxy to running server).

**Development Mode Comparison**

```mermaid
graph TB
    subgraph "dev:watch Mode"
        DW1["TypeScript Compiler<br/>(server code)"]
        DW2["Vite Bundler<br/>(web code)"]
        DW3["Library Compiler<br/>(mcp package)"]
        DW4["Nodemon<br/>(auto-restart)"]
        DW5["HTTP Server<br/>(serves static web)"]
    end
    
    subgraph "dev Mode (default)"
        D1["One-time Build<br/>(tsc)"]
        D2["HTTP Server<br/>(serves pre-built web)"]
    end
    
    subgraph "dev:vite Mode"
        DV1["Vite Dev Server<br/>(HMR)"]
        DV2["No backend<br/>(or proxy)"]
    end
    
    DW1 --> DW4
    DW2 --> DW5
    DW3 -.->|"indirect"| DW4
    DW4 --> DW5
    
    D1 --> D2
    
    DV1 --> DV2
```

Sources: [packages/app/package.json:40-46]()

---

## Environment Configuration

Development mode respects environment variables for configuration. Set these before running dev scripts:

**Development Environment Variables**:

| Variable | Purpose | Default (dev) |
|----------|---------|---------------|
| `NODE_ENV` | Runtime environment | `development` |
| `PORT` | HTTP server port | `3000` |
| `HF_TOKEN` | Hugging Face API token | (from client or env) |
| `USER_CONFIG_API` | External settings API URL | (none) |
| `LOG_LEVEL` | Pino logging level | `info` |

**Setting Variables**:

```bash
# Cross-platform approach using cross-env
pnpm dev  # NODE_ENV=development set automatically

# Custom port
PORT=8080 pnpm dev

# With HF token for testing auth-required endpoints
HF_TOKEN=hf_xxxxx pnpm dev
```

The [packages/app/package.json:40]() scripts use `cross-env` to ensure consistent behavior across platforms (Windows, macOS, Linux).

Sources: [packages/app/package.json:40-48]()

---

## Debugging Setup

### Node.js Debugging

Debug the server process using Node.js built-in inspector:

**Step 1: Modify the dev script** (temporary change):

```bash
# In packages/app
node --inspect dist/server/streamableHttp.js
```

**Step 2: Attach debugger**:

- **VS Code**: Use "Attach to Node Process" configuration
- **Chrome DevTools**: Navigate to `chrome://inspect`
- **Command line**: Use `node inspect`

**Breakpoint Locations**:

- `src/server/application.ts` - Server initialization
- `src/server/transports/*.ts` - Request handling
- `packages/mcp/src/tools/**/*.ts` - Tool implementations

### TypeScript Source Maps

Both TypeScript compilations ([packages/app/package.json:35](), [packages/mcp/package.json:26]()) generate source maps by default. This enables:

- Debugging TypeScript source instead of compiled JavaScript
- Accurate stack traces pointing to `.ts` files
- Breakpoints in original source files

Source maps are written adjacent to compiled files:
- `dist/server/**/*.js.map`
- `packages/mcp/dist/**/*.js.map`

### Browser Debugging

Debug the web UI using browser DevTools:

**React DevTools**:

Install React DevTools browser extension for:
- Component tree inspection
- Props and state examination
- Performance profiling

**Vite Dev Tools**:

Vite provides source maps automatically in dev mode. View original TypeScript/TSX source in browser DevTools Sources panel.

Sources: [packages/app/package.json:35](), [packages/mcp/package.json:26]()

---

## Build vs. Development Mode

Understanding the differences between build and development modes:

**Development Mode Characteristics**:

- Source maps enabled
- No minification
- Fast incremental compilation
- `NODE_ENV=development`
- Verbose logging
- Hot reload enabled
- Development dependencies available

**Production Build Characteristics** (see [Build System](#9.1) for details):

- No source maps (or separate files)
- Code minification
- `NODE_ENV=production`
- Optimized bundle sizes
- No hot reload
- Only production dependencies

**Key Files**:

| Aspect | Development | Production |
|--------|-------------|------------|
| TypeScript config | `tsconfig.server.json` | `tsconfig.server.json` |
| Vite config | `vite.config.ts` (dev mode) | `vite.config.ts` (build mode) |
| Output location | `dist/` (watched) | `dist/` (final) |
| Server startup | Via nodemon | Via `node` directly |

Sources: [packages/app/package.json:34-50]()

---

## Common Development Tasks

### Adding a New Tool

**Step 1**: Create tool implementation in `packages/mcp/src/tools/`

**Step 2**: Export from `packages/mcp/src/index.ts`

**Step 3**: Register in `packages/app/src/server/createServerFactory.ts`

**Step 4**: Watch compilation automatically picks up changes:
- Library: `tsc --watch` compiles new tool
- Server: Nodemon restarts to register tool

### Modifying Web UI

**Step 1**: Edit React components in `packages/app/src/web/`

**Step 2**: Changes automatically apply via HMR (if using `dev:vite`)

**Step 3**: Test in browser at http://localhost:5173 (Vite) or http://localhost:3000 (built)

### Testing Transport Changes

**Step 1**: Modify transport implementation in `packages/app/src/server/transports/`

**Step 2**: TypeScript watch recompiles

**Step 3**: Nodemon restarts server

**Step 4**: Test with appropriate client:
- STDIO: Claude Code CLI
- HTTP/SSE: Browser-based clients
- Test in isolation: `pnpm dev:stdio` or `pnpm dev:sse`

### Dependency Updates

**Step 1**: Update dependencies in appropriate `package.json`

**Step 2**: Run `pnpm install` from root

**Step 3**: Restart dev processes:

```bash
# Kill existing processes (Ctrl+C)
pnpm dev:watch
```

TypeScript and Vite will recompile with new dependencies.

Sources: [packages/app/package.json:58-110](), [packages/mcp/package.json:34-52]()

---

## Troubleshooting Development Issues

### Common Issues and Solutions

**Issue: Port Already in Use**

```
Error: listen EADDRINUSE: address already in use :::3000
```

**Solution**:
- Kill existing process: `lsof -ti:3000 | xargs kill -9` (Unix) or `taskkill /F /IM node.exe` (Windows)
- Change port: `PORT=3001 pnpm dev`

**Issue: TypeScript Compilation Errors**

**Solution**:
- Check [packages/app/package.json:54](): `pnpm typecheck` to see all errors
- Ensure `packages/mcp` is compiled: `cd packages/mcp && pnpm build`
- Clean and rebuild: `pnpm clean && pnpm build`

**Issue: Web UI Not Updating**

**Solution**:
- If using `dev` (not `dev:vite`): Vite runs in build mode, need full rebuild
- Switch to `pnpm dev:vite` for HMR
- Hard refresh browser: Ctrl+Shift+R
- Check console for HMR errors

**Issue: Nodemon Not Restarting**

**Solution**:
- Verify TypeScript is compiling: Check console output
- Ensure file changes in `dist/server/` directory
- Check nodemon is running: Look for "watching for file changes" message
- Manual restart: Kill and run `pnpm dev:watch` again

**Issue: Library Changes Not Reflecting**

**Solution**:
- Library watch only recompiles, doesn't restart server
- After library changes, restart server manually
- Or use full `pnpm dev:watch` from root which restarts on any change

Sources: [packages/app/package.json:34-56]()

---

# Page: Testing

# Testing

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [package.json](package.json)
- [packages/app/package.json](packages/app/package.json)
- [packages/app/src/server/transport/base-transport.ts](packages/app/src/server/transport/base-transport.ts)
- [packages/app/src/server/transport/stateless-http-transport.ts](packages/app/src/server/transport/stateless-http-transport.ts)
- [packages/app/src/server/utils/gradio-utils.ts](packages/app/src/server/utils/gradio-utils.ts)
- [packages/app/test/server/utils/gradio-utils.test.ts](packages/app/test/server/utils/gradio-utils.test.ts)
- [packages/mcp/package.json](packages/mcp/package.json)
- [pnpm-lock.yaml](pnpm-lock.yaml)

</details>



This page documents the test infrastructure and testing practices for the Hugging Face MCP Server. It covers the test framework setup, how to run tests, test organization patterns, and examples of test implementation.

For information about the build system that compiles code before testing, see [Build System](#9.1). For development workflows including hot reload and watch modes, see [Development Workflow](#9.2).

---

## Test Infrastructure

The project uses **Vitest** as its testing framework across both packages in the monorepo. Vitest provides fast unit testing with native TypeScript support and ESM compatibility.

### Framework Configuration

Both `packages/app` and `packages/mcp` include Vitest as a dev dependency and define test scripts in their respective `package.json` files:

| Package | Test Command | Configuration |
|---------|-------------|---------------|
| Root | `pnpm run -r test` | Runs tests recursively across all packages |
| `packages/app` | `vitest run` | Executes app package tests |
| `packages/mcp` | `vitest run` | Executes mcp library tests |

The test command `vitest run` executes tests in non-watch mode, suitable for CI/CD pipelines and pre-commit checks.

**Sources:** [package.json:15](), [packages/app/package.json:51](), [packages/mcp/package.json:27]()

---

## Test Organization

### Directory Structure

Tests are organized in a parallel structure to the source code, following the convention of placing test files in a `test/` directory within each package:

```mermaid
graph TB
    subgraph "Monorepo Structure"
        Root["hf-mcp (root)"]
        
        subgraph "packages/app"
            AppSrc["src/"]
            AppTest["test/"]
            AppTest --> ServerTests["server/"]
            ServerTests --> UtilsTests["utils/"]
            UtilsTests --> GradioTest["gradio-utils.test.ts"]
        end
        
        subgraph "packages/mcp"
            McpSrc["src/"]
            McpTest["test/ (if exists)"]
        end
        
        Root --> AppSrc
        Root --> AppTest
        Root --> McpSrc
        Root --> McpTest
    end
    
    style Root fill:#f9f9f9
    style AppTest fill:#e1f5ff
    style McpTest fill:#e1f5ff
```

**Test Directory Mirroring Source Structure**

The test directory structure mirrors the source directory organization. For example, tests for [packages/app/src/server/utils/gradio-utils.ts]() are located at [packages/app/test/server/utils/gradio-utils.test.ts]().

**Sources:** [packages/app/test/server/utils/gradio-utils.test.ts:1-450]()

---

## Running Tests

### Command Reference

| Command | Purpose | Scope |
|---------|---------|-------|
| `pnpm test` | Run all tests across packages | Monorepo |
| `pnpm run --filter=@llmindset/hf-mcp-server test` | Run app package tests | `packages/app` |
| `pnpm run --filter=@llmindset/hf-mcp test` | Run mcp package tests | `packages/mcp` |
| `vitest` | Run tests in watch mode | Current package |
| `vitest run` | Run tests once (CI mode) | Current package |

### Pre-Test Build Requirements

Tests execute against compiled TypeScript code. The build pipeline must complete successfully before running tests:

```mermaid
sequenceDiagram
    participant Dev as Developer
    participant Build as Build System
    participant Tests as Vitest
    participant Results as Test Results
    
    Dev->>Build: pnpm build
    Build->>Build: tsc compile TypeScript
    Build->>Build: Vite bundle web assets
    Build-->>Dev: Build complete
    
    Dev->>Tests: pnpm test
    Tests->>Tests: Load compiled .js files
    Tests->>Tests: Execute test suites
    Tests->>Results: Generate report
    Results-->>Dev: Test results + coverage
```

**Test Execution Flow**

1. TypeScript compilation via `tsc` produces JavaScript output in `dist/` directories
2. Vitest loads compiled code from `dist/` or directly via TypeScript loader
3. Test files import from compiled or source depending on configuration
4. Vitest executes test suites and reports results

**Sources:** [package.json:15-23](), [packages/app/package.json:34-36](), [packages/mcp/package.json:26]()

---

## Test Patterns and Structure

### Test File Organization

Test files follow a consistent structure using Vitest's `describe` and `it` functions for organizing test cases into logical groups.

#### Example Test Structure

The [gradio-utils.test.ts]() file demonstrates the standard test organization pattern:

```mermaid
graph TB
    TestFile["gradio-utils.test.ts"]
    
    subgraph "isGradioTool Tests"
        Describe1["describe('isGradioTool')"]
        Valid["describe('valid Gradio tools')"]
        Invalid["describe('non-Gradio tools')"]
        Edge["describe('edge cases')"]
        
        Describe1 --> Valid
        Describe1 --> Invalid
        Describe1 --> Edge
        
        Valid --> Test1["it('should detect basic gr tools')"]
        Valid --> Test2["it('should detect grp tools')"]
        Valid --> Test3["it('should detect dynamic_space')"]
        
        Invalid --> Test4["it('should reject standard HF tools')"]
        Invalid --> Test5["it('should reject missing number')"]
    end
    
    subgraph "createGradioToolName Tests"
        Describe2["describe('createGradioToolName')"]
        Generate["describe('correct generation')"]
        Truncate["describe('49-char limit')"]
        
        Describe2 --> Generate
        Describe2 --> Truncate
        
        Generate --> Test6["it('should create public names')"]
        Generate --> Test7["it('should sanitize names')"]
        
        Truncate --> Test8["it('should enforce limit with truncation')"]
        Truncate --> Test9["it('should preserve unique endings')"]
    end
    
    TestFile --> Describe1
    TestFile --> Describe2
    
    style TestFile fill:#e1f5ff
    style Describe1 fill:#ffe1e1
    style Describe2 fill:#ffe1e1
```

**Three-Level Hierarchy:**
1. **Top Level**: `describe` blocks for each function being tested
2. **Second Level**: `describe` blocks for test categories (valid inputs, invalid inputs, edge cases)
3. **Third Level**: `it` blocks for individual test cases with specific assertions

**Sources:** [packages/app/test/server/utils/gradio-utils.test.ts:8-266]()

---

### Test Case Implementation

Tests use Vitest's `expect` API for assertions. The test file shows several common patterns:

#### Pattern 1: Basic Assertions

Testing boolean return values with straightforward expectations:

```typescript
it('should detect basic gr tools', () => {
    expect(isGradioTool('gr1_tool')).toBe(true);
    expect(isGradioTool('gr2_another_tool')).toBe(true);
    expect(isGradioTool('gr999_test')).toBe(true);
});
```

**Sources:** [packages/app/test/server/utils/gradio-utils.test.ts:10-14]()

#### Pattern 2: Object Equality Testing

Testing functions that return structured data using deep equality:

```typescript
it('should parse single space ID', () => {
    const result = parseGradioSpaceIds('microsoft/Florence-2-large');
    expect(result).toEqual([{ name: 'microsoft/Florence-2-large' }]);
});
```

**Sources:** [packages/app/test/server/utils/gradio-utils.test.ts:270-273]()

#### Pattern 3: Property Validation

Testing specific properties or characteristics of returned values:

```typescript
it('should enforce 49-character limit with middle truncation', () => {
    const longName = 'very_long_tool_name_that_exceeds_forty_nine_characters_total_and_more';
    const result1 = createGradioToolName(longName, 0, false);
    expect(result1.length).toBe(49);
    expect(result1).toBe('gr1_very_long_tool_name__haracters_total_and_more');
});
```

**Sources:** [packages/app/test/server/utils/gradio-utils.test.ts:145-150]()

---

### Test Coverage Categories

The test suite demonstrates comprehensive coverage across multiple dimensions:

```mermaid
graph LR
    Coverage["Test Coverage"]
    
    Coverage --> Valid["Valid Inputs"]
    Coverage --> Invalid["Invalid Inputs"]
    Coverage --> Edge["Edge Cases"]
    Coverage --> Integration["Integration Scenarios"]
    
    Valid --> BasicCases["Basic functionality"]
    Valid --> RealWorld["Real-world examples"]
    
    Invalid --> Missing["Missing components"]
    Invalid --> Malformed["Malformed data"]
    Invalid --> WrongType["Wrong types"]
    
    Edge --> Empty["Empty strings"]
    Edge --> Limits["Boundary values"]
    Edge --> Special["Special characters"]
    
    Integration --> CrossFunction["Cross-function tests"]
    Integration --> EndToEnd["End-to-end paths"]
    
    style Coverage fill:#e1f5ff
    style Valid fill:#e1ffe1
    style Invalid fill:#ffe1e1
    style Edge fill:#fff5e1
    style Integration fill:#f3e5f5
```

**Coverage Dimensions:**

| Dimension | Example from Tests | Purpose |
|-----------|-------------------|---------|
| **Valid Inputs** | Testing `gr1_tool`, `grp2_tool` patterns | Verify correct behavior on expected inputs |
| **Invalid Inputs** | Testing `hf_doc_search`, missing underscores | Ensure proper rejection of non-conforming data |
| **Edge Cases** | Empty strings, boundary lengths, special characters | Test robustness at limits |
| **Integration** | Tools generated by `createGradioToolName` tested with `isGradioTool` | Verify compatibility between functions |

**Sources:** [packages/app/test/server/utils/gradio-utils.test.ts:8-449]()

---

## Test Execution Details

### Import Resolution

Test files import from the compiled source using relative paths with `.js` extensions (TypeScript convention for ESM):

```typescript
import {
    isGradioTool,
    createGradioToolName,
    parseGradioSpaceIds,
} from '../../../src/server/utils/gradio-utils.js';
```

The `.js` extension is required even though the source is TypeScript because the compiled output produces `.js` files.

**Sources:** [packages/app/test/server/utils/gradio-utils.test.ts:2-6]()

---

### Test Module Structure

```mermaid
graph TB
    TestModule["Test Module (.test.ts)"]
    
    TestModule --> Imports["Import statements"]
    TestModule --> Describes["describe() blocks"]
    
    Imports --> Vitest["Vitest: describe, it, expect"]
    Imports --> SUT["System Under Test functions"]
    
    Describes --> MainDescribe1["Top-level describe (function 1)"]
    Describes --> MainDescribe2["Top-level describe (function 2)"]
    
    MainDescribe1 --> Nested1["Nested describe (category 1)"]
    MainDescribe1 --> Nested2["Nested describe (category 2)"]
    
    Nested1 --> Test1["it (test case 1)"]
    Nested1 --> Test2["it (test case 2)"]
    Nested2 --> Test3["it (test case 3)"]
    
    Test1 --> Arrange["// Arrange: Setup data"]
    Test1 --> Act["// Act: Execute function"]
    Test1 --> Assert["// Assert: expect() calls"]
    
    style TestModule fill:#e1f5ff
    style Imports fill:#ffe1e1
    style Describes fill:#e1ffe1
```

**Mapping Test Structure to Code Entities:**

- **Test File**: [packages/app/test/server/utils/gradio-utils.test.ts]()
- **System Under Test**: [packages/app/src/server/utils/gradio-utils.ts]()
- **Test Framework**: `vitest` (imported via `describe`, `it`, `expect`)
- **Functions Tested**: `isGradioTool`, `createGradioToolName`, `parseGradioSpaceIds`

**Sources:** [packages/app/test/server/utils/gradio-utils.test.ts:1-7]()

---

## Test-Driven Validation

### Regression Prevention

Tests document and prevent known bugs from reoccurring. The test suite includes specific cases derived from bug reports:

```typescript
it('should handle real-world example from bug report', () => {
    // This was the actual failing case: microsoft/Florence-2-large
    const result = parseGradioSpaceIds('microsoft/Florence-2-large');
    expect(result).toEqual([{ name: 'microsoft/Florence-2-large' }]);
    // Verify we're NOT converting the slash to a dash here
    expect(result[0].name).not.toContain('-Florence-');
    expect(result[0].name).toContain('/Florence-');
});
```

This test explicitly documents:
- The original bug scenario (slash being converted to dash)
- The expected correct behavior (preserving the slash)
- Validation that prevents regression (explicit checks for both conditions)

**Sources:** [packages/app/test/server/utils/gradio-utils.test.ts:306-313]()

---

### Cross-Function Integration Tests

Tests verify that outputs from one function are valid inputs to another, ensuring API compatibility:

```typescript
it('should detect tool names generated by createGradioToolName', () => {
    // Generate examples using the actual tool creation logic
    const publicTool1 = createGradioToolName('flux1_schnell', 0, false);
    const publicTool2 = createGradioToolName('EasyGhibli', 1, false);
    const privateTool = createGradioToolName('private-model', 2, true);
    
    expect(isGradioTool(publicTool1)).toBe(true);
    expect(isGradioTool(publicTool2)).toBe(true);
    expect(isGradioTool(privateTool)).toBe(true);
});
```

This validates the integration between `createGradioToolName` (tool name generator) and `isGradioTool` (tool name detector).

**Sources:** [packages/app/test/server/utils/gradio-utils.test.ts:32-42]()

---

## Test Execution Environment

### CI/CD Integration

The test command structure supports continuous integration workflows:

```mermaid
sequenceDiagram
    participant CI as CI Pipeline
    participant Root as Root Package
    participant App as App Package
    participant Mcp as MCP Package
    participant Report as Test Report
    
    CI->>Root: pnpm test
    Root->>Root: pnpm run -r test
    
    par Parallel Test Execution
        Root->>App: vitest run
        Root->>Mcp: vitest run
    end
    
    App->>App: Execute test suites
    Mcp->>Mcp: Execute test suites
    
    App-->>Root: Test results
    Mcp-->>Root: Test results
    
    Root->>Report: Aggregate results
    Report-->>CI: Exit code + coverage
    
    alt Tests Pass
        CI->>CI: Continue pipeline
    else Tests Fail
        CI->>CI: Abort pipeline
    end
```

**Test Execution Characteristics:**

- **Parallel Execution**: Tests in `packages/app` and `packages/mcp` run independently
- **Fast Feedback**: Vitest's speed enables rapid test-driven development
- **Exit Codes**: Non-zero exit code on test failure enables CI gating
- **Deterministic**: Tests run in consistent order without side effects

**Sources:** [package.json:15](), [packages/app/package.json:51](), [packages/mcp/package.json:27]()

---

## Writing New Tests

### Test File Creation

When adding tests for a new module, follow these conventions:

1. **Location**: Create test file in `test/` directory mirroring source structure
2. **Naming**: Use `.test.ts` suffix (e.g., `new-module.test.ts` for `new-module.ts`)
3. **Imports**: Import test functions from Vitest and module under test
4. **Organization**: Use nested `describe` blocks for logical grouping

### Example Template

```typescript
import { describe, it, expect } from 'vitest';
import { functionToTest } from '../../../src/path/to/module.js';

describe('functionToTest', () => {
    describe('valid inputs', () => {
        it('should handle basic case', () => {
            const result = functionToTest('input');
            expect(result).toBe('expected');
        });
    });
    
    describe('invalid inputs', () => {
        it('should reject null', () => {
            expect(() => functionToTest(null)).toThrow();
        });
    });
    
    describe('edge cases', () => {
        it('should handle empty input', () => {
            const result = functionToTest('');
            expect(result).toBe('default');
        });
    });
});
```

---

## Coverage and Quality Metrics

While specific coverage tools are not explicitly configured in the package.json files, Vitest supports coverage reporting through the `@vitest/coverage-*` packages. Coverage can be added by:

1. Installing a coverage provider (e.g., `@vitest/coverage-v8`)
2. Running `vitest run --coverage`
3. Viewing HTML coverage reports in the generated `coverage/` directory

### Target Coverage Areas

Priority areas for test coverage based on system architecture:

| Component | Test Priority | Rationale |
|-----------|--------------|-----------|
| **Utility Functions** | High | Pure functions, easy to test, high reuse |
| **Transport Layer** | High | Critical for client communication |
| **Tool Implementations** | Medium | Complex integration, may need mocking |
| **Server Factory** | Medium | Central orchestration point |
| **UI Components** | Low | Visual testing complexity |

**Sources:** [packages/app/package.json:109](), [packages/mcp/package.json:51]()

---

# Page: Project Structure

# Project Structure

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [package.json](package.json)
- [packages/app/package.json](packages/app/package.json)
- [packages/mcp/package.json](packages/mcp/package.json)
- [packages/mcp/src/index.ts](packages/mcp/src/index.ts)
- [packages/mcp/src/tool-ids.ts](packages/mcp/src/tool-ids.ts)
- [pnpm-lock.yaml](pnpm-lock.yaml)

</details>



This page provides a detailed walkthrough of the directory structure, file organization conventions, and key file locations in the HF MCP Server codebase. It serves as a map for developers navigating the repository structure.

For information about the build system and compilation process, see [Build System](#9.1). For development workflow and hot reload setup, see [Development Workflow](#9.2).

---

## Monorepo Organization

The project uses a **pnpm workspace-based monorepo** with two primary packages:

| Package | Location | Purpose | Published |
|---------|----------|---------|-----------|
| `@llmindset/hf-mcp` | `packages/mcp/` | Library layer with tool implementations | No |
| `@llmindset/hf-mcp-server` | `packages/app/` | Application layer with server and web UI | Yes (npm) |

**Root-Level Files**

```
├── package.json              # Workspace root with dev scripts
├── pnpm-workspace.yaml       # Workspace configuration
├── pnpm-lock.yaml           # Dependency lock file
├── tsconfig.json            # Shared TypeScript config
└── .eslintrc.json           # Shared linting rules
```

The root `package.json` provides workspace-level scripts that orchestrate both packages:

[package.json:7-24]()

**Sources:** [package.json:1-38](), [pnpm-lock.yaml:1-100]()

---

## Monorepo Dependency Graph

```mermaid
graph TB
    Root["Root Workspace<br/>package.json"]
    
    subgraph "Published Package"
        App["@llmindset/hf-mcp-server<br/>packages/app/"]
        AppDist["dist/<br/>Compiled output"]
    end
    
    subgraph "Internal Library"
        Mcp["@llmindset/hf-mcp<br/>packages/mcp/"]
        McpDist["dist/<br/>Tool implementations"]
    end
    
    Root -->|"pnpm workspace"| App
    Root -->|"pnpm workspace"| Mcp
    App -->|"workspace:^"| Mcp
    App --> AppDist
    Mcp --> McpDist
    
    style App fill:#f9f9f9
    style Mcp fill:#f9f9f9
```

The application package (`@llmindset/hf-mcp-server`) depends on the library package (`@llmindset/hf-mcp`) using pnpm's workspace protocol, ensuring the local version is always used during development.

**Sources:** [packages/app/package.json:59](), [pnpm-lock.yaml:42-49]()

---

## packages/app/ Structure

The `packages/app/` directory contains the **application layer** — everything needed to run MCP servers and the web dashboard.

### Directory Layout

```
packages/app/
├── package.json                      # Main package metadata and scripts
├── tsconfig.json                     # TypeScript config (server code)
├── tsconfig.server.json             # Server-specific TS config
├── vite.config.ts                   # Vite config (web UI builds)
├── components.json                  # shadcn/ui config
│
├── src/                             # Source code
│   ├── server/                      # Server entrypoints
│   │   ├── stdio.ts                # STDIO transport entrypoint
│   │   ├── sse.ts                  # SSE transport entrypoint
│   │   ├── streamableHttp.ts       # HTTP transport entrypoint
│   │   └── streamableHttpJson.ts   # Stateless HTTP entrypoint
│   │
│   ├── lib/                         # Server-side libraries
│   │   ├── application/            # Application orchestrator
│   │   ├── transports/             # Transport implementations
│   │   ├── auth/                   # Authentication utilities
│   │   ├── gradio/                 # Gradio integration
│   │   ├── settings/               # Settings service
│   │   └── mcp-server/             # MCP server factory
│   │
│   ├── api/                         # Web API routes
│   │   ├── transport.ts            # Transport metrics endpoint
│   │   ├── sessions.ts             # Session management endpoint
│   │   └── settings.ts             # Settings CRUD endpoint
│   │
│   └── ui/                          # React web UI
│       ├── pages/                  # UI pages
│       ├── components/             # Reusable components
│       └── hooks/                  # Custom React hooks
│
├── dist/                            # Build output
│   ├── server/                     # Compiled server code
│   │   ├── stdio.js               # STDIO entrypoint
│   │   ├── streamableHttp.js      # HTTP entrypoint
│   │   └── ...                    # Other compiled server files
│   │
│   ├── ui/                         # Bundled web UI
│   │   ├── index.html             # Dashboard HTML
│   │   └── assets/                # JS/CSS bundles
│   │
│   └── singlefiles/                # Standalone HTML files
│       ├── gradio-widget.html     # Gradio widget for OpenAI
│       └── mcp-welcome.html       # Welcome page
│
└── scripts/                        # Build utilities
    └── html-to-ts.js              # Convert HTML to TS string
```

**Sources:** [packages/app/package.json:1-111]()

---

## packages/app/ File Path Mappings

This diagram maps logical components to their actual file locations:

```mermaid
graph LR
    subgraph "Server Entrypoints"
        StdioEntry["stdio.ts<br/>STDIO mode"]
        SseEntry["sse.ts<br/>SSE mode"]
        HttpEntry["streamableHttp.ts<br/>Stateful HTTP"]
        JsonEntry["streamableHttpJson.ts<br/>Stateless HTTP"]
    end
    
    subgraph "Core Libraries"
        App["application/index.ts<br/>Application"]
        WebSrv["web-server.ts<br/>WebServer"]
        
        subgraph "Transports"
            TBase["transports/base-transport.ts<br/>BaseTransport"]
            TStateful["transports/stateful-transport.ts<br/>StatefulTransport"]
            TStdio["transports/stdio-transport.ts<br/>STDIOTransport"]
            TSse["transports/sse-transport.ts<br/>SSETransport"]
            THttp["transports/streamable-http-transport.ts<br/>StreamableHTTPTransport"]
            TJson["transports/streamable-http-json-transport.ts<br/>StatelessHTTPTransport"]
        end
        
        McpFact["mcp-server/create-server-factory.ts<br/>createServerFactory"]
        ProxyFact["mcp-server/create-proxy-server.ts<br/>createProxyServerFactory"]
        
        Settings["settings/settings-service.ts<br/>settingsService"]
        ApiClient["mcp-api-client.ts<br/>McpApiClient"]
    end
    
    subgraph "Web UI"
        UiPages["ui/pages/*.tsx<br/>React pages"]
        UiComps["ui/components/*.tsx<br/>UI components"]
    end
    
    StdioEntry -->|"uses"| TStdio
    SseEntry -->|"uses"| TSse
    HttpEntry -->|"uses"| THttp
    JsonEntry -->|"uses"| TJson
    
    TStdio --> TBase
    TSse --> TStateful
    THttp --> TStateful
    TJson --> TBase
    TStateful --> TBase
    
    App --> WebSrv
    WebSrv --> McpFact
    McpFact --> ProxyFact
    
    App --> ApiClient
    ApiClient --> Settings
```

**Key Directories Explained:**

- **`src/server/`** — Contains the four main entrypoints ([stdio.ts](), [sse.ts](), [streamableHttp.ts](), [streamableHttpJson.ts]()), each instantiating a different transport implementation
- **`src/lib/transports/`** — Transport layer implementations with inheritance hierarchy
- **`src/lib/mcp-server/`** — Server factory logic and Gradio proxy factory
- **`src/lib/settings/`** — User settings persistence (internal or external API)
- **`src/lib/gradio/`** — Gradio discovery, schema parsing, and tool handler creation
- **`src/ui/`** — Complete React web dashboard with pages and components

**Sources:** [packages/app/package.json:6-11]()

---

## packages/app/ Build Configuration

The package uses **dual build systems**:

| Build Target | Tool | Config | Output |
|--------------|------|--------|--------|
| Server code | TypeScript | `tsconfig.server.json` | `dist/server/` |
| Web UI | Vite | `vite.config.ts` | `dist/ui/` |
| Single-file HTML | Vite + plugin | `vite.config.ts` | `dist/singlefiles/` |

**Build Scripts:**

[packages/app/package.json:34-39]()

The `build` script chains together:
1. `build:web` — Vite bundles the React UI into `dist/ui/`
2. `build:singlefiles` — Vite creates standalone HTML files for Gradio widgets
3. `build:server` — TypeScript compiles server code to `dist/server/`

**Published Files:**

[packages/app/package.json:12-15]()

Only `dist/` and `components.json` are included in the npm package, keeping the published size minimal.

**Sources:** [packages/app/package.json:34-56]()

---

## packages/app/ Entrypoint Mapping

```mermaid
graph TB
    subgraph "npm bin Commands"
        BinStdio["hf-mcp-server"]
        BinHttp["hf-mcp-server-http"]
        BinJson["hf-mcp-server-http-json"]
    end
    
    subgraph "Source Files"
        SrcStdio["src/server/stdio.ts"]
        SrcHttp["src/server/streamableHttp.ts"]
        SrcJson["src/server/streamableHttpJson.ts"]
    end
    
    subgraph "Compiled Output"
        DistStdio["dist/server/stdio.js"]
        DistHttp["dist/server/streamableHttp.js"]
        DistJson["dist/server/streamableHttpJson.js"]
    end
    
    subgraph "package.json"
        Main["main: dist/server/streamableHttp.js"]
        Bin["bin: { ... }"]
    end
    
    BinStdio -->|"maps to"| DistStdio
    BinHttp -->|"maps to"| DistHttp
    BinJson -->|"maps to"| DistJson
    
    SrcStdio -->|"tsc compiles"| DistStdio
    SrcHttp -->|"tsc compiles"| DistHttp
    SrcJson -->|"tsc compiles"| DistJson
    
    Bin -->|"defines"| BinStdio
    Bin -->|"defines"| BinHttp
    Bin -->|"defines"| BinJson
    
    Main -->|"default export"| DistHttp
```

Users can invoke the server via:
- **`npx hf-mcp-server`** — Runs STDIO transport
- **`npx hf-mcp-server-http`** — Runs stateful HTTP transport
- **`npx hf-mcp-server-http-json`** — Runs stateless HTTP transport
- **`import "@llmindset/hf-mcp-server"`** — Imports stateful HTTP transport (main entry)

**Sources:** [packages/app/package.json:6-11]()

---

## packages/mcp/ Structure

The `packages/mcp/` directory contains the **library layer** — all tool implementations and shared utilities.

### Directory Layout

```
packages/mcp/
├── package.json                 # Library package metadata
├── tsconfig.json               # TypeScript config
│
├── src/                        # Source code
│   ├── index.ts               # Main export file
│   ├── tool-ids.ts            # Canonical tool ID registry
│   │
│   ├── hf-api-call.ts         # Base class for HF API tools
│   ├── error-messages.ts      # Error handling utilities
│   ├── utilities.ts           # Shared utilities
│   ├── readme-utils.ts        # README processing
│   │
│   ├── model-search.ts        # Model search tool
│   ├── model-detail.ts        # Model detail tool
│   ├── dataset-search.ts      # Dataset search tool
│   ├── dataset-detail.ts      # Dataset detail tool
│   ├── paper-search.ts        # Paper search tool
│   ├── space-search.ts        # Space semantic search
│   ├── hub-inspect.ts         # Hub repo details tool
│   │
│   ├── duplicate-space.ts     # Space duplication tool
│   ├── space-info.ts          # Space info tool
│   ├── space-files.ts         # Space files tool
│   ├── use-space.ts           # Dynamic space invocation
│   │
│   ├── user-summary.ts        # User summary prompt
│   ├── paper-summary.ts       # Paper summary prompt
│   │
│   ├── docs-search/           # Documentation tools
│   │   ├── docs-semantic-search.ts
│   │   └── doc-fetch.ts
│   │
│   ├── gradio-files.ts        # Gradio utilities
│   │
│   ├── jobs/                  # Jobs-related tools
│   │   └── jobs-tool.ts
│   │
│   ├── space/                 # Dynamic space tools
│   │   └── space-tool.ts
│   │
│   └── types/                 # Shared TypeScript types
│       └── tool-result.ts
│
└── dist/                      # Compiled JavaScript + declarations
    ├── index.js
    ├── index.d.ts
    ├── tool-ids.js
    ├── tool-ids.d.ts
    └── ...                    # All other compiled files
```

**Sources:** [packages/mcp/package.json:1-53](), [packages/mcp/src/index.ts:1-30]()

---

## packages/mcp/ Export Structure

The library uses a **flat export pattern** — all modules are re-exported from `index.ts`:

[packages/mcp/src/index.ts:1-30]()

**Package Exports:**

[packages/mcp/package.json:7-24]()

The package provides **subpath exports** for selective imports:
- `@llmindset/hf-mcp` — Full library (all tools)
- `@llmindset/hf-mcp/semantic` — Just semantic search
- `@llmindset/hf-mcp/model` — Just model search
- `@llmindset/hf-mcp/paper` — Just paper search

**Sources:** [packages/mcp/package.json:7-24](), [packages/mcp/src/index.ts:1-30]()

---

## Tool ID Registry

The `tool-ids.ts` file serves as the **canonical source of truth** for all tool identifiers:

```mermaid
graph TB
    subgraph "Tool Configs"
        Cfg1["MODEL_SEARCH_TOOL_CONFIG.name"]
        Cfg2["DATASET_SEARCH_TOOL_CONFIG.name"]
        Cfg3["SPACE_INFO_TOOL_CONFIG.name"]
        CfgN["...other configs"]
    end
    
    subgraph "tool-ids.ts"
        Registry["Exported Tool IDs"]
        Groups["TOOL_ID_GROUPS"]
    end
    
    subgraph "Consumers"
        App["packages/app/<br/>Server factory"]
        Selection["ToolSelectionStrategy"]
        Tests["Test suites"]
    end
    
    Cfg1 -->|"extracted from"| Registry
    Cfg2 -->|"extracted from"| Registry
    Cfg3 -->|"extracted from"| Registry
    CfgN -->|"extracted from"| Registry
    
    Registry -->|"groups into"| Groups
    
    Registry --> App
    Registry --> Selection
    Registry --> Tests
    Groups --> Selection
```

**Key Exports:**

[packages/mcp/src/tool-ids.ts:28-48]()

**Grouped Tool IDs for Bouquets:**

[packages/mcp/src/tool-ids.ts:68-96]()

This structure enables the **bouquet system** where clients can request predefined sets of tools by referencing a group key (e.g., `"search"`, `"spaces"`, `"hf_api"`).

**Sources:** [packages/mcp/src/tool-ids.ts:1-105]()

---

## Tool Implementation Pattern

All built-in tools follow a consistent pattern:

```mermaid
graph LR
    subgraph "Tool File Structure"
        Schema["Zod Schema<br/>Input validation"]
        Config["TOOL_CONFIG<br/>Name, description, schema"]
        Handler["Tool Handler Function<br/>Async implementation"]
        Types["TypeScript Types<br/>Inferred from Zod"]
    end
    
    subgraph "Base Classes"
        HfApiCall["HfApiCall<br/>API interaction helpers"]
    end
    
    subgraph "Exports"
        AllExports["All exported from index.ts"]
    end
    
    Schema -->|"used in"| Config
    Schema -->|"infers"| Types
    Handler -->|"validates with"| Schema
    Handler -.->|"may extend"| HfApiCall
    
    Config --> AllExports
    Handler --> AllExports
    Types --> AllExports
```

**Example from model-search.ts:**

```typescript
// 1. Zod schema for validation
const modelSearchArgsSchema = z.object({
  query: z.string(),
  limit: z.number().optional(),
  // ...
});

// 2. Config object (single source of truth)
export const MODEL_SEARCH_TOOL_CONFIG = {
  name: "model_search",
  description: "Search for models on Hugging Face",
  schema: zodToJsonSchema(modelSearchArgsSchema),
};

// 3. Handler function
export async function handleModelSearch(
  args: z.infer<typeof modelSearchArgsSchema>
): Promise<ToolResult> {
  // Implementation
}
```

This pattern ensures:
- **Type safety** — TypeScript types inferred from Zod schemas
- **Runtime validation** — All inputs validated before execution
- **Single source of truth** — Config object contains canonical tool metadata
- **Consistent structure** — All tools follow the same pattern

**Sources:** [packages/mcp/src/index.ts:2-24](), [packages/mcp/src/tool-ids.ts:6-26]()

---

## File Naming Conventions

The project follows consistent naming patterns:

| Pattern | Example | Purpose |
|---------|---------|---------|
| `*-search.ts` | `model-search.ts` | Search/query tools |
| `*-detail.ts` | `dataset-detail.ts` | Detail/info retrieval tools |
| `*-info.ts` | `space-info.ts` | Info/metadata tools |
| `*-summary.ts` | `user-summary.ts` | Prompt templates |
| `*-tool.ts` | `jobs-tool.ts` | Generic tool suffix |
| `*-utils.ts` | `readme-utils.ts` | Utility modules |
| `*-transport.ts` | `stdio-transport.ts` | Transport implementations |
| `*-service.ts` | `settings-service.ts` | Service classes |

**Directory Naming:**
- **Kebab-case** for directories: `docs-search/`, `mcp-server/`
- **Singular nouns** for single-concept directories: `auth/`, `gradio/`
- **Plural nouns** for collections: `transports/`, `jobs/`

**Sources:** [packages/mcp/src/index.ts:1-30]()

---

## Configuration Files

```mermaid
graph TB
    subgraph "Root Level"
        RootPkg["package.json<br/>Workspace root"]
        RootTS["tsconfig.json<br/>Shared TS config"]
        PnpmWS["pnpm-workspace.yaml<br/>Package list"]
        PnpmLock["pnpm-lock.yaml<br/>Lock file"]
    end
    
    subgraph "packages/app/"
        AppPkg["package.json<br/>Published package"]
        AppTS["tsconfig.json<br/>Base config"]
        AppTSSrv["tsconfig.server.json<br/>Server-specific"]
        Vite["vite.config.ts<br/>Web UI builds"]
        CompJson["components.json<br/>shadcn/ui"]
    end
    
    subgraph "packages/mcp/"
        McpPkg["package.json<br/>Library package"]
        McpTS["tsconfig.json<br/>Library config"]
    end
    
    RootPkg -->|"references"| AppPkg
    RootPkg -->|"references"| McpPkg
    RootTS -->|"extended by"| AppTS
    RootTS -->|"extended by"| McpTS
    AppTS -->|"extended by"| AppTSSrv
    
    style RootPkg fill:#f9f9f9
    style AppPkg fill:#f9f9f9
    style McpPkg fill:#f9f9f9
```

**TypeScript Configuration Hierarchy:**

1. **Root `tsconfig.json`** — Shared compiler options (target, module, strict mode)
2. **`packages/app/tsconfig.json`** — Extends root, adds React JSX support
3. **`packages/app/tsconfig.server.json`** — Extends app config, server-only includes
4. **`packages/mcp/tsconfig.json`** — Extends root, library-specific settings

**Build Configuration:**

- **`vite.config.ts`** — Configures Vite for web UI builds, React plugin, HTML generation
- **`components.json`** — shadcn/ui configuration for component generation

**Sources:** [package.json:1-38](), [packages/app/package.json:1-111](), [packages/mcp/package.json:1-53]()

---

## Build Output Structure

After running `pnpm build`, the directory structure becomes:

```
packages/app/dist/
├── server/                    # Compiled server code (CommonJS)
│   ├── stdio.js              # Entrypoint scripts
│   ├── streamableHttp.js
│   ├── streamableHttpJson.js
│   ├── sse.js
│   │
│   ├── lib/                  # Library modules
│   │   ├── application/
│   │   ├── transports/
│   │   ├── mcp-server/
│   │   └── ...
│   │
│   └── [all source files mirrored]
│
├── ui/                        # Bundled web UI (static site)
│   ├── index.html            # Entry HTML
│   └── assets/               # Hashed JS/CSS bundles
│       ├── index-abc123.js
│       └── index-xyz789.css
│
└── singlefiles/               # Standalone HTML files
    ├── gradio-widget.html    # Single-file Gradio widget
    └── mcp-welcome.html      # Welcome page

packages/mcp/dist/
├── index.js                   # Main export
├── index.d.ts                # Type declarations
├── tool-ids.js               # Tool ID registry
├── tool-ids.d.ts
├── model-search.js           # Individual tool modules
├── model-search.d.ts
└── [all source files compiled]
```

**Distribution Strategy:**

- **Server code** — Not tree-shakeable; entire `dist/server/` included
- **Web UI** — Optimized bundle with code splitting
- **Library** — Each tool is a separate module for selective imports
- **Type definitions** — `.d.ts` files alongside every `.js` file

**Sources:** [packages/app/package.json:34-56](), [packages/mcp/package.json:25-32]()

---

## Import Path Conventions

**Within packages/app/:**

```typescript
// Relative imports for intra-package references
import { Application } from '../lib/application/index.js';
import { WebServer } from '../lib/web-server.js';
import { STDIOTransport } from '../lib/transports/stdio-transport.js';

// Library imports use package name
import { MODEL_SEARCH_TOOL_ID } from '@llmindset/hf-mcp';
```

**Within packages/mcp/:**

```typescript
// Always use relative imports with .js extension
import { HfApiCall } from './hf-api-call.js';
import { MODEL_SEARCH_TOOL_CONFIG } from './model-search.js';
```

**From external consumers:**

```typescript
// Import from published package
import { MODEL_SEARCH_TOOL_ID } from '@llmindset/hf-mcp';
import { createServerFactory } from '@llmindset/hf-mcp-server';

// Or use subpath exports
import { handleModelSearch } from '@llmindset/hf-mcp/model';
```

All imports use **`.js` extensions** even in TypeScript source files, following Node.js ESM conventions.

**Sources:** [packages/mcp/src/index.ts:1-30](), [packages/mcp/package.json:7-24]()

---

## Key File Locations Reference

This table provides quick lookup for commonly-referenced files:

| Component | File Path |
|-----------|-----------|
| **Entrypoints** | |
| STDIO server | `packages/app/src/server/stdio.ts` |
| HTTP server | `packages/app/src/server/streamableHttp.ts` |
| **Application Core** | |
| Application orchestrator | `packages/app/src/lib/application/index.ts` |
| Web server | `packages/app/src/lib/web-server.ts` |
| MCP server factory | `packages/app/src/lib/mcp-server/create-server-factory.ts` |
| **Transports** | |
| Base transport | `packages/app/src/lib/transports/base-transport.ts` |
| STDIO transport | `packages/app/src/lib/transports/stdio-transport.ts` |
| SSE transport | `packages/app/src/lib/transports/sse-transport.ts` |
| **Settings & State** | |
| Settings service | `packages/app/src/lib/settings/settings-service.ts` |
| MCP API client | `packages/app/src/lib/mcp-api-client.ts` |
| Tool selection strategy | `packages/app/src/lib/mcp-server/tool-selection-strategy.ts` |
| **Gradio Integration** | |
| Gradio connector | `packages/app/src/lib/gradio/gradio-endpoint-connector.ts` |
| Gradio utilities | `packages/app/src/lib/gradio/gradio-utils.ts` |
| **Library Tools** | |
| Tool ID registry | `packages/mcp/src/tool-ids.ts` |
| Library main export | `packages/mcp/src/index.ts` |
| HF API base class | `packages/mcp/src/hf-api-call.ts` |
| Model search | `packages/mcp/src/model-search.ts` |
| Dataset detail | `packages/mcp/src/dataset-detail.ts` |
| Doc search | `packages/mcp/src/docs-search/docs-semantic-search.ts` |

**Sources:** [packages/app/package.json:1-111](), [packages/mcp/src/index.ts:1-30](), [packages/mcp/src/tool-ids.ts:1-105]()