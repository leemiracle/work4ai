<!-- source: DeepWiki mcp.deepwiki.com · repo voltagent/voltagent · page 6 Protocols and Integrations · fetched 2026-10-27 -->

# Protocols and Integrations

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CHANGELOG.md](CHANGELOG.md)
- [changelog.sh](changelog.sh)
- [examples/base/src/index.ts](examples/base/src/index.ts)
- [examples/with-google-ai/package.json](examples/with-google-ai/package.json)
- [examples/with-google-vertex-ai/package.json](examples/with-google-vertex-ai/package.json)
- [examples/with-groq-ai/package.json](examples/with-groq-ai/package.json)
- [examples/with-mcp/package.json](examples/with-mcp/package.json)
- [examples/with-nextjs/package.json](examples/with-nextjs/package.json)
- [packages/cli/package.json](packages/cli/package.json)
- [packages/core/package.json](packages/core/package.json)
- [packages/create-voltagent-app/CHANGELOG.md](packages/create-voltagent-app/CHANGELOG.md)
- [packages/create-voltagent-app/package.json](packages/create-voltagent-app/package.json)
- [packages/voice/package.json](packages/voice/package.json)
- [pnpm-lock.yaml](pnpm-lock.yaml)

</details>



This document covers the external protocol integrations and specialized capabilities in VoltAgent. VoltAgent implements two primary protocols for agent interoperability: Model Context Protocol (MCP) for tool access and Agent-to-Agent (A2A) for inter-agent communication. Additional integrations include voice capabilities, vector databases, and web frameworks.

For core framework functionality, see [Core Framework](#2). For AI provider integrations, see [AI Provider Integration](#3). For memory and storage systems, see [Memory and Storage](#5).
</thinking>

## Overview

VoltAgent extends agent capabilities through standardized protocols and service integrations:

| Integration Type | Package | Protocol/Standard | Purpose |
|-----------------|---------|-------------------|---------|
| MCP Server | `@voltagent/mcp-server` | Model Context Protocol | Expose agents/tools to IDEs |
| A2A Server | `@voltagent/a2a-server` | JSON-RPC over HTTP | Inter-agent communication |
| Voice | `@voltagent/voice` | Provider APIs | Speech synthesis/transcription |
| Vector DBs | Examples | Vendor SDKs | Semantic search for RAG |
| Web Frameworks | Examples | Framework-specific | Next.js, Nuxt integration |

**Sources:** [packages/core/package.json:6](), [CHANGELOG.md:91-196](), [pnpm-lock.yaml:1-2500]()

## Protocol and Integration Architecture

**Title:** VoltAgent Protocol and Integration Layer Architecture

```mermaid
graph TB
    subgraph "VoltAgent Core"
        AGENT["Agent"]
        TOOLS["ToolManager"]
        VOLTAGENT["VoltAgent"]
    end
    
    subgraph "Protocol Layer"
        MCP_SERVER["MCPServer<br/>@voltagent/mcp-server"]
        A2A_SERVER["A2AServer<br/>@voltagent/a2a-server"]
    end
    
    subgraph "MCP Transports"
        MCP_STDIO["stdio transport"]
        MCP_HTTP["HTTP/SSE transport"]
        MCP_ROUTES["/mcp/* routes"]
    end
    
    subgraph "A2A Endpoints"
        A2A_DISCOVERY["/.well-known/<br/>discovery"]
        A2A_RPC["/a2a/:serverId<br/>JSON-RPC"]
    end
    
    subgraph "Voice Integration"
        VOICE_PKG["@voltagent/voice"]
        OPENAI_VOICE["OpenAI API"]
        ELEVEN_VOICE["ElevenLabs API"]
        XSAI_VOICE["@xsai packages"]
    end
    
    subgraph "Server Layer"
        SERVER_HONO["honoServer<br/>@voltagent/server-hono"]
        SWAGGER["OpenAPI/Swagger"]
    end
    
    subgraph "External Clients"
        IDE["IDEs (Cursor, VSCode)"]
        EXTERNAL_AGENT["External Agents"]
        APP_CLIENT["Application Client"]
    end
    
    VOLTAGENT --> MCP_SERVER
    VOLTAGENT --> A2A_SERVER
    AGENT --> TOOLS
    
    MCP_SERVER --> MCP_STDIO
    MCP_SERVER --> MCP_HTTP
    MCP_HTTP --> MCP_ROUTES
    
    A2A_SERVER --> A2A_DISCOVERY
    A2A_SERVER --> A2A_RPC
    
    AGENT -.uses.-> VOICE_PKG
    VOICE_PKG --> OPENAI_VOICE
    VOICE_PKG --> ELEVEN_VOICE
    VOICE_PKG --> XSAI_VOICE
    
    SERVER_HONO --> MCP_ROUTES
    SERVER_HONO --> A2A_RPC
    SERVER_HONO --> SWAGGER
    
    IDE --> MCP_STDIO
    IDE --> MCP_HTTP
    EXTERNAL_AGENT --> A2A_RPC
    APP_CLIENT --> VOICE_PKG
```

**Sources:** [CHANGELOG.md:91-196](), [packages/core/package.json:6](), [packages/voice/package.json:1-51]()

## Model Context Protocol (MCP)

The Model Context Protocol provides standardized access to VoltAgent agents, tools, and resources from external clients like IDEs and other MCP-compatible applications.

### MCP Server Architecture

**Title:** MCP Server Component Architecture

```mermaid
graph TB
    subgraph "MCPServer Configuration"
        MCP_CONFIG["MCPServer<br/>{name, version}"]
        AGENTS_REG["agents: {}<br/>Agent instances"]
        TOOLS_REG["tools: {}<br/>Tool instances"]
        PROTOCOLS["protocols:<br/>{stdio, http, sse}"]
        FILTERS["filterTools()<br/>filterAgents()"]
    end
    
    subgraph "Transport Layer"
        STDIO_TRANSPORT["StdioServerTransport<br/>Process communication"]
        HTTP_TRANSPORT["SSEServerTransport<br/>HTTP/SSE"]
    end
    
    subgraph "MCP Protocol Operations"
        LIST_TOOLS["tools/list"]
        CALL_TOOL["tools/call"]
        LIST_PROMPTS["prompts/list"]
        GET_PROMPT["prompts/get"]
    end
    
    subgraph "VoltAgent Integration"
        VOLTAGENT_INST["VoltAgent instance"]
        AUTO_ROUTES["Auto-registered<br/>/mcp/* routes"]
        HONO_SERVER["honoServer"]
    end
    
    MCP_CONFIG --> AGENTS_REG
    MCP_CONFIG --> TOOLS_REG
    MCP_CONFIG --> PROTOCOLS
    MCP_CONFIG --> FILTERS
    
    PROTOCOLS --> STDIO_TRANSPORT
    PROTOCOLS --> HTTP_TRANSPORT
    
    STDIO_TRANSPORT --> LIST_TOOLS
    STDIO_TRANSPORT --> CALL_TOOL
    HTTP_TRANSPORT --> LIST_PROMPTS
    HTTP_TRANSPORT --> GET_PROMPT
    
    MCP_CONFIG -.registered in.-> VOLTAGENT_INST
    VOLTAGENT_INST --> HONO_SERVER
    HONO_SERVER --> AUTO_ROUTES
```

**Sources:** [CHANGELOG.md:122-196](), [examples/with-mcp-server/package.json:1-29]()

### MCP Server Registration

VoltAgent auto-registers MCP servers when configured in the `VoltAgent` constructor:

**Configuration:** [examples/with-mcp-server/src/index.ts:1-50]() (example pattern)
**Server Setup:** `MCPServer` class from `@voltagent/mcp-server`
**Route Registration:** `honoServer` automatically exposes `/mcp/*` endpoints when `mcpServers` is configured

### MCP Transport Protocols

| Transport | Use Case | Configuration |
|-----------|----------|---------------|
| stdio | IDE integration (Cursor, VSCode) | `protocols: { stdio: true }` |
| HTTP | Remote client access | `protocols: { http: true }` |
| SSE | Streaming updates | `protocols: { sse: true }` |

**Example MCP Configuration:**

```typescript
// Register MCP server in VoltAgent
const mcpServer = new MCPServer({
  name: "support-mcp",
  version: "1.0.0",
  agents: { assistant },
  tools: { status },
  protocols: { stdio: true, http: true, sse: true }
});

export const voltAgent = new VoltAgent({
  agents: { assistant },
  mcpServers: { primary: mcpServer },
  server: honoServer({ port: 3141 })
});
```

**Sources:** [CHANGELOG.md:165-196](), [examples/with-mcp-server/package.json:5-12]()

### MCP Tool and Agent Filtering

The MCP server supports filtering exposed tools and agents:

**Filtering Pattern:**
- `filterTools({ items })` - Filter tools before exposing via MCP
- `filterAgents({ items })` - Filter agents before exposing via MCP
- Sub-agents are automatically filtered from listings

**Sources:** [CHANGELOG.md:159-162]()

### MCP Discovery and OpenAPI

When MCP is enabled with HTTP transport:
- Endpoints appear in OpenAPI/Swagger documentation
- Routes are listed in the server startup banner
- Discovery endpoints follow MCP specification

**Sources:** [CHANGELOG.md:169-170]()

## Agent-to-Agent (A2A) Protocol

The A2A protocol enables HTTP-based inter-agent communication using JSON-RPC. External agents can discover and invoke VoltAgent agents over HTTP/SSE.

### A2A Server Architecture

**Title:** Agent-to-Agent Protocol Architecture

```mermaid
graph TB
    subgraph "A2AServer Configuration"
        A2A_CONFIG["A2AServer<br/>{name, version}"]
        A2A_AGENTS["Registered agents"]
        A2A_FILTERS["filterAgents()<br/>augmentAgent()"]
        A2A_HOOKS["Task management<br/>hooks"]
    end
    
    subgraph "Discovery Mechanism"
        WELL_KNOWN["/.well-known/<br/>agent-discovery"]
        MANIFEST["Server manifest<br/>{agents, capabilities}"]
    end
    
    subgraph "JSON-RPC Endpoints"
        RPC_ENDPOINT["/a2a/:serverId"]
        INVOKE_METHOD["agents/invoke"]
        LIST_METHOD["agents/list"]
        DESCRIBE_METHOD["agents/describe"]
    end
    
    subgraph "Request Context"
        USER_ID["userId"]
        SESSION_ID["sessionId"]
        METADATA["Custom metadata"]
        TASK_STORE["Task tracking"]
    end
    
    subgraph "Server Integration"
        HONO_ROUTES["Auto-registered<br/>A2A routes"]
        SWAGGER_DOCS["OpenAPI docs"]
        STARTUP_BANNER["Startup banner"]
    end
    
    A2A_CONFIG --> A2A_AGENTS
    A2A_CONFIG --> A2A_FILTERS
    A2A_CONFIG --> A2A_HOOKS
    
    A2A_CONFIG --> WELL_KNOWN
    WELL_KNOWN --> MANIFEST
    
    A2A_CONFIG --> RPC_ENDPOINT
    RPC_ENDPOINT --> INVOKE_METHOD
    RPC_ENDPOINT --> LIST_METHOD
    RPC_ENDPOINT --> DESCRIBE_METHOD
    
    INVOKE_METHOD --> USER_ID
    INVOKE_METHOD --> SESSION_ID
    INVOKE_METHOD --> METADATA
    A2A_HOOKS --> TASK_STORE
    
    A2A_CONFIG -.registered in.-> HONO_ROUTES
    HONO_ROUTES --> SWAGGER_DOCS
    HONO_ROUTES --> STARTUP_BANNER
```

**Sources:** [CHANGELOG.md:91-120](), [examples/with-a2a-server/package.json:1-20]()

### A2A Server Registration

Register A2A servers in the `VoltAgent` constructor:

```typescript
// Define A2A server
const a2aServer = new A2AServer({
  name: "support-agent",
  version: "0.1.0"
});

// Register with VoltAgent
export const voltAgent = new VoltAgent({
  agents: { assistant },
  a2aServers: { a2aServer },
  server: honoServer({ port: 3141 })
});
```

**Configuration:** [examples/with-a2a-server/src/index.ts:1-50]() (example pattern)
**Package:** `@voltagent/a2a-server`
**Auto-registration:** Routes automatically exposed when `a2aServers` configured

**Sources:** [CHANGELOG.md:97-120](), [examples/with-a2a-server/package.json:6-7]()

### A2A Discovery Mechanism

External agents discover available agents via the discovery endpoint:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/.well-known/agent-discovery` | GET | Server manifest with agent list |
| `/a2a/:serverId` | POST | JSON-RPC agent invocation |

**Discovery Response:**
- Server name and version
- List of available agents
- Agent capabilities and descriptions
- Protocol version information

**Sources:** [CHANGELOG.md:95]()

### A2A Request Context

A2A requests forward context to agent invocations:

**Context Fields:**
- `userId` - User identifier for memory isolation
- `sessionId` - Session tracking
- `metadata` - Custom key-value pairs
- Task management hooks for long-running operations

**Sources:** [CHANGELOG.md:93-94]()

### A2A Task Management

The A2A server supports custom task stores for tracking long-running agent operations. Task management hooks allow filtering and augmenting agent invocations.

**Sources:** [CHANGELOG.md:94]()

## Extension Development Guidelines

Extensions in the VoltAgent ecosystem follow these patterns:

### Package Structure
- Follow `@voltagent/extension-name` naming convention
- Implement standard TypeScript exports with ESM/CJS dual publishing
- Include comprehensive peer dependencies for core framework compatibility
- Provide TypeScript definitions and proper module resolution

### Interface Implementation
- Extend core interfaces rather than replacing them
- Use dependency injection for configurable components
- Provide sensible defaults while allowing customization
- Follow established error handling patterns

### Example Integration Patterns
The codebase includes over 20 example integrations demonstrating various extension patterns:

| Example Type | Package Dependencies | Key Integration |
|-------------|---------------------|-----------------|
| Voice Integration | `@voltagent/voice`, `openai` | TTS/STT services |
| RAG Chatbot | `@voltagent/libsql`, vector embeddings | Semantic search |
| Supabase Integration | `@voltagent/supabase`, `@supabase/supabase-js` | Cloud database |
| Multi-agent Systems | `@voltagent/core` SubAgent classes | Agent delegation |

**Sources:** [examples/with-voice-openai/package.json:1-38](), [examples/with-rag-chatbot/package.json:1-31](), [examples/with-supabase/package.json:1-34](), [examples/with-subagents/package.json:1-34]()

For detailed information on specific extensions:
- Voice capabilities: [Voice Capabilities](#8.1)
- Web framework integration: [Web Framework Integration](#8.2)  
- IDE connectivity: [MCP Integration](#8.3)
- Vector databases: [Vector Databases](#8.4)

---

