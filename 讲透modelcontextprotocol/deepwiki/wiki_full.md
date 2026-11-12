# Page: Overview

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitattributes](.gitattributes)
- [.github/dependabot.yml](.github/dependabot.yml)
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [README.md](README.md)
- [SECURITY.md](SECURITY.md)
- [blog/archetypes/default.md](blog/archetypes/default.md)
- [blog/content/posts/2025-07-29-prompts-for-automation.md](blog/content/posts/2025-07-29-prompts-for-automation.md)
- [blog/content/posts/2025-07-31-governance-for-mcp.md](blog/content/posts/2025-07-31-governance-for-mcp.md)
- [blog/content/posts/2025-09-05-php-sdk.md](blog/content/posts/2025-09-05-php-sdk.md)
- [blog/content/posts/2025-09-08-mcp-registry-preview.md](blog/content/posts/2025-09-08-mcp-registry-preview.md)
- [blog/content/posts/2025-09-26-mcp-next-version-update.md](blog/content/posts/2025-09-26-mcp-next-version-update.md)
- [blog/content/posts/2025-11-03-using-server-instructions.md](blog/content/posts/2025-11-03-using-server-instructions.md)
- [blog/content/posts/2025-11-20-adopting-mcpb.md](blog/content/posts/2025-11-20-adopting-mcpb.md)
- [blog/content/posts/2025-11-21-mcp-apps.md](blog/content/posts/2025-11-21-mcp-apps.md)
- [blog/content/posts/2025-11-25-first-mcp-anniversary.md](blog/content/posts/2025-11-25-first-mcp-anniversary.md)
- [blog/content/posts/2025-11-28-sep-process-update.md](blog/content/posts/2025-11-28-sep-process-update.md)
- [blog/content/posts/welcome-to-mcp-blog.md](blog/content/posts/welcome-to-mcp-blog.md)
- [docs/community/security.mdx](docs/community/security.mdx)
- [docs/docs/develop/build-client.mdx](docs/docs/develop/build-client.mdx)
- [docs/docs/develop/build-server.mdx](docs/docs/develop/build-server.mdx)
- [docs/docs/develop/build-with-agent-skills.mdx](docs/docs/develop/build-with-agent-skills.mdx)
- [docs/docs/learn/architecture.mdx](docs/docs/learn/architecture.mdx)
- [docs/docs/learn/client-concepts.mdx](docs/docs/learn/client-concepts.mdx)
- [docs/docs/learn/server-concepts.mdx](docs/docs/learn/server-concepts.mdx)
- [docs/docs/sdk.mdx](docs/docs/sdk.mdx)
- [docs/images/mcp-simple-diagram.png](docs/images/mcp-simple-diagram.png)
- [package-lock.json](package-lock.json)
- [package.json](package.json)

</details>



## Purpose and Scope

This document provides an overview of the `modelcontextprotocol/modelcontextprotocol` repository, which serves as the **authoritative source** for the Model Context Protocol (MCP) specification, schema definitions, protocol documentation, and community governance structures. The repository functions as a multi-purpose system that:

- Defines the MCP specification through versioned releases [README.md:5-9]().
- Maintains the TypeScript schema as the single source of truth for JSON-RPC message types [README.md:11-13]().
- Publishes comprehensive documentation to [modelcontextprotocol.io](https://modelcontextprotocol.io) [README.md:15-17]().
- Coordinates a massive ecosystem of servers and clients [blog/content/posts/2025-11-25-first-mcp-anniversary.md:25-35]().
- Establishes governance processes for protocol evolution through Specification Enhancement Proposals (SEPs) [blog/content/posts/2025-11-25-first-mcp-anniversary.md:57-65]().

The protocol has achieved significant adoption since its launch, with the **MCP Registry** growing to nearly 2,000 entries—a 407% increase since its announcement in September 2025 [blog/content/posts/2025-11-25-first-mcp-anniversary.md:17-35]().

Sources: [README.md:1-29](), [blog/content/posts/2025-11-25-first-mcp-anniversary.md:1-65]()

## Repository Architecture

The repository is organized into distinct functional areas, separating the formal specification from user-facing documentation and community guidelines.

### Repository Structure

```mermaid
graph TB
    subgraph "Specification_Sources"
        [SCHEMA_TS] -- "schema/2025-11-25/schema.ts<br/>TypeScript definitions"
        [SCHEMA_JSON] -- "schema/2025-11-25/schema.json<br/>Generated JSON Schema"
    end
    
    subgraph "Documentation"
        [DOCS] -- "docs/docs/**/*.mdx<br/>Tutorials and guides"
        [BLOG] -- "blog/content/posts/<br/>Hugo-formatted posts"
    end
    
    subgraph "Community_Governance"
        [MAINTAINERS] -- "MAINTAINERS.md"
        [CONTRIB] -- "CONTRIBUTING.md"
        [SECURITY] -- "SECURITY.md"
        [AI_POLICY] -- "AI_POLICY.md"
    end
    
    subgraph "Build_System"
        [PACKAGE_JSON] -- "package.json<br/>npm scripts"
        [GIT_ATTRS] -- ".gitattributes<br/>Merge strategies"
    end
    
    [SCHEMA_TS] -->|"npm run generate:schema"| [SCHEMA_JSON]
    [PACKAGE_JSON] -->|"npm run prep"| [DOCS]
    [GIT_ATTRS] -->|"Prevents merge conflicts"| [SCHEMA_JSON]
```

Sources: [README.md:5-13](), [CONTRIBUTING.md:42-54](), [.gitattributes:1-11](), [package.json:23-46]()

### Key Directory Functions

| Directory | Purpose | Key Files |
|-----------|---------|-----------|
| `schema/` | Canonical protocol types | `schema.ts`, `schema.json` [README.md:11-13]() |
| `docs/docs/` | MDX-based documentation | `develop/`, `learn/`, `sdk.mdx` [CONTRIBUTING.md:71]() |
| `blog/` | Community updates and news | Hugo markdown posts [CONTRIBUTING.md:92]() |
| `.github/` | CI/CD automation | Workflows for validation [CONTRIBUTING.md:109]() |

Sources: [CONTRIBUTING.md:1-149](), [README.md:1-29]()

## Schema System

The TypeScript schema (e.g., `schema/draft/schema.ts`) is the **single source of truth** for all MCP protocol definitions [CONTRIBUTING.md:42-44](). All other artifacts, including the JSON Schema and documentation fragments, derive from this source via the `generate` scripts.

### Schema Generation Pipeline

```mermaid
graph LR
    [SCHEMA_TS] -- "schema/draft/schema.ts<br/>TypeScript Source"
    
    [SCHEMA_JSON] -- "schema/draft/schema.json<br/>JSON Schema"
    
    [SPEC_MDX] -- "docs/specification/draft/schema.mdx<br/>MDX Documentation"
    
    [NPM_GEN] -- "npm run generate:schema"
    [NPM_CHECK] -- "npm run check:schema:ts"
    
    [SCHEMA_TS] --> [NPM_GEN]
    [NPM_GEN] --> [SCHEMA_JSON]
    [NPM_GEN] --> [SPEC_MDX]
    [SCHEMA_TS] --> [NPM_CHECK]
```

Sources: [CONTRIBUTING.md:42-54](), [package.json:23-37]()

## Protocol Implementation Logic

MCP follows a client-server architecture where an **MCP Host** (e.g., Claude Desktop or VS Code) manages **MCP Clients** that connect to dedicated **MCP Servers** [docs/docs/learn/architecture.mdx:31-40]().

### Connection Lifecycle

The protocol is stateful and requires a formal handshake:
1. **Initialize**: The client calls `initialize` to perform capability negotiation and version matching [docs/docs/learn/architecture.mdx:111-115](), [docs/docs/develop/build-client.mdx:150]().
2. **Operation**: Bidirectional exchange of JSON-RPC 2.0 messages (requests, responses, and notifications) [docs/docs/learn/architecture.mdx:107-108]().
3. **Shutdown**: Graceful termination of the session [docs/docs/learn/architecture.mdx:87]().

### Core Primitives

Servers provide context through three main primitives:
- **Resources**: File-like data that can be read by clients (e.g., API responses or file contents) [docs/docs/develop/build-server.mdx:26]().
- **Tools**: Functions that can be called by the LLM (with user approval) [docs/docs/develop/build-server.mdx:27]().
- **Prompts**: Pre-written templates that help users accomplish specific tasks [docs/docs/develop/build-server.mdx:28]().

Sources: [docs/docs/learn/architecture.mdx:1-115](), [docs/docs/develop/build-server.mdx:22-30](), [docs/docs/develop/build-client.mdx:148-156]()

## Trust Model and Security

The MCP security model relies on explicit user consent and trust boundaries between local and remote environments [SECURITY.md:31-40]().

### Data Flow and Security Boundaries

```mermaid
graph TD
    subgraph "MCP_Host_Application"
        [MCPClient] -- "mcp.ClientSession"
    end

    subgraph "Local_Environment"
        [STDIO_SERVER] -- "StdioServerParameters"
        [FS] -- "Local Filesystem"
    end

    subgraph "Remote_Environment"
        [HTTP_SERVER] -- "Streamable HTTP / SSE"
        [CLOUD_API] -- "Upstream Cloud API"
    end

    [MCPClient] -- "spawn()" --> [STDIO_SERVER]
    [STDIO_SERVER] -- "read/write" --> [FS]
    [MCPClient] -- "HTTP POST" --> [HTTP_SERVER]
    [HTTP_SERVER] -- "OAuth/Bearer" --> [CLOUD_API]

    style [STDIO_SERVER] stroke-dasharray: 5 5
    style [HTTP_SERVER] stroke-dasharray: 5 5
```

**Key Security Principles:**
- **Local Trust**: Local servers run with the same privileges as the client [SECURITY.md:67-70](). The SDK does not sandbox the STDIO transport [SECURITY.md:89-90]().
- **Explicit Approval**: Every tool execution typically requires user consent at the host level [docs/docs/develop/build-server.mdx:27]().
- **Transport Security**: Remote servers are recommended to use OAuth to obtain authentication tokens [docs/docs/learn/architecture.mdx:99]().

Sources: [SECURITY.md:23-118](), [docs/docs/learn/architecture.mdx:96-101](), [docs/docs/develop/build-client.mdx:106-149]()

## SDK Ecosystem

Official SDKs are classified into tiers based on feature completeness, protocol support, and maintenance commitment [docs/docs/sdk.mdx:6]().

| Tier | Status | Languages |
| :--- | :--- | :--- |
| **Tier 1** | Production Ready | TypeScript, Python, C#, Go [docs/docs/sdk.mdx:12-15]() |
| **Tier 2** | Stable | Java, Rust [docs/docs/sdk.mdx:16-17]() |
| **Tier 3** | Experimental/Community | Swift, Ruby, PHP, Kotlin [docs/docs/sdk.mdx:18-21]() |

Sources: [docs/docs/sdk.mdx:1-35]()

## Contributing and Governance

Changes to the protocol follow the **Specification Enhancement Process (SEP)** [CONTRIBUTING.md:118]().

- **AI Policy**: AI-assisted contributions must be disclosed per `AI_POLICY.md` [CONTRIBUTING.md:133-137]().
- **Governance**: Managed by a mix of community leaders and maintainers from Anthropic [blog/content/posts/2025-11-25-first-mcp-anniversary.md:57-61]().
- **Working Groups**: Formalized under SEP-1302 to handle specific domains like Transports, SDKs, or Security [blog/content/posts/2025-11-25-first-mcp-anniversary.md:61]().

Sources: [CONTRIBUTING.md:1-149](), [blog/content/posts/2025-11-25-first-mcp-anniversary.md:39-65]()

---

# Page: Protocol Specification

# Protocol Specification

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.prettierignore](.prettierignore)
- [docs/specification/2024-11-05/basic/index.mdx](docs/specification/2024-11-05/basic/index.mdx)
- [docs/specification/2024-11-05/index.mdx](docs/specification/2024-11-05/index.mdx)
- [docs/specification/2024-11-05/server/index.mdx](docs/specification/2024-11-05/server/index.mdx)
- [docs/specification/2025-03-26/basic/index.mdx](docs/specification/2025-03-26/basic/index.mdx)
- [docs/specification/2025-03-26/changelog.mdx](docs/specification/2025-03-26/changelog.mdx)
- [docs/specification/2025-03-26/index.mdx](docs/specification/2025-03-26/index.mdx)
- [docs/specification/2025-03-26/server/index.mdx](docs/specification/2025-03-26/server/index.mdx)
- [docs/specification/2025-06-18/schema.mdx](docs/specification/2025-06-18/schema.mdx)
- [docs/specification/2025-11-25/schema.mdx](docs/specification/2025-11-25/schema.mdx)
- [docs/specification/draft/basic/index.mdx](docs/specification/draft/basic/index.mdx)
- [docs/specification/draft/changelog.mdx](docs/specification/draft/changelog.mdx)
- [docs/specification/draft/client/elicitation.mdx](docs/specification/draft/client/elicitation.mdx)
- [docs/specification/draft/index.mdx](docs/specification/draft/index.mdx)
- [docs/specification/draft/schema.mdx](docs/specification/draft/schema.mdx)
- [docs/specification/draft/server/index.mdx](docs/specification/draft/server/index.mdx)
- [docs/style.css](docs/style.css)
- [schema/2025-11-25/schema.json](schema/2025-11-25/schema.json)
- [schema/2025-11-25/schema.ts](schema/2025-11-25/schema.ts)
- [schema/draft/schema.json](schema/draft/schema.json)
- [schema/draft/schema.ts](schema/draft/schema.ts)
- [scripts/pull-registry-docs.sh](scripts/pull-registry-docs.sh)
- [typedoc.config.mjs](typedoc.config.mjs)
- [typedoc.plugin.mjs](typedoc.plugin.mjs)

</details>



## Purpose and Scope

This page documents the Model Context Protocol (MCP) specification—the authoritative definition of how clients and servers communicate. It covers the core messaging system, transport mechanisms, connection lifecycle, and protocol features that enable bidirectional interaction between MCP clients and servers.

This page focuses on the **protocol layer itself**: message types, encoding, transport, and capability negotiation. For information about implementing servers, see [Server Development](#5). For information about client implementations, see [Client Ecosystem](#4). For authorization and security mechanisms, see [Authorization and Security](#3).

## Overview: Protocol Architecture

MCP is built on three foundational layers:

1.  **JSON-RPC 2.0 Message System**: All communication uses JSON-RPC 2.0 for encoding requests, responses, and notifications.
2.  **Transport Layer**: Messages are transmitted via stdio (subprocess) or Streamable HTTP (remote).
3.  **Stateless Connection Model**: In the latest specification (`2026-07-28`), the protocol has shifted to a stateless architecture where capabilities and versioning are declared per-request.

The protocol is **bidirectional**—both clients and servers can initiate requests and send notifications. This enables servers to request user input via elicitation and access filesystem roots.

Sources: [schema/draft/schema.ts:26-32](), [docs/specification/draft/basic/index.mdx:7-24](), [docs/specification/draft/changelog.mdx:14-16]()

## JSON-RPC Message System

### Message Types

MCP defines three JSON-RPC message types, all encoded as UTF-8 JSON:

| Message Type | Direction | Expects Response | Structure |
| :--- | :--- | :--- | :--- |
| **Request** | Either direction | Yes | `{jsonrpc: "2.0", id, method, params?}` |
| **Response** | Either direction | No | `{jsonrpc: "2.0", id, result or error}` |
| **Notification** | Either direction | No | `{jsonrpc: "2.0", method, params?}` |

Key constraints:
*   Request IDs **MUST** be string or number (never `null`) [docs/specification/draft/basic/index.mdx:46-47]().
*   Result responses **MUST** include a `resultType` (e.g., `"complete"` or `"input_required"`) [docs/specification/draft/basic/index.mdx:73-82]().
*   Notifications **MUST NOT** include an ID.

Sources: [schema/draft/schema.ts:26-27](), [docs/specification/draft/basic/index.mdx:31-106]()

### Error Handling

MCP defines standard JSON-RPC error codes plus implementation-specific codes in the range `-32020` to `-32099`:

| Error Code | Name | Usage |
| :--- | :--- | :--- |
| `-32700` | `ParseError` | Invalid JSON received |
| `-32600` | `InvalidRequest` | Request structure invalid |
| `-32601` | `MethodNotFound` | Method not supported or capability not declared |
| `-32020` | `HeaderMismatch` | HTTP header and `_meta` version mismatch |
| `-32021` | `MissingRequiredClientCapability` | Client lacks capability for the request |
| `-32022` | `UnsupportedProtocolVersion` | Server doesn't support requested version |

Sources: [schema/draft/schema.ts:203-247](), [docs/specification/draft/basic/index.mdx:107-154]()

### Metadata System (`_meta`)

All messages **MAY** include a `_meta` field. In the latest stateless spec, `_meta` is **REQUIRED** for requests to carry protocol version and capabilities.

**Reserved Prefix System**:
*   Any prefix where the second label is `modelcontextprotocol` or `mcp` is **reserved** (e.g., `io.modelcontextprotocol/`) [schema/draft/schema.ts:45-46]().

**Stateless Request Metadata** [schema/draft/schema.ts:63-104]():
*   `io.modelcontextprotocol/protocolVersion`: Required protocol version.
*   `io.modelcontextprotocol/clientInfo`: Required client identification.
*   `io.modelcontextprotocol/clientCapabilities`: Required per-request capabilities.

Sources: [schema/draft/schema.ts:34-104](), [docs/specification/draft/changelog.mdx:14-16]()

## Transport Layer

### stdio Transport

The client launches the MCP server as a subprocess. Messages are framed using single-line JSON objects delimited by newlines.

Sources: [docs/specification/draft/changelog.mdx:16-18]()

### Streamable HTTP Transport

Standardized via SEP, this transport removes protocol-level sessions in favor of stateless requests.

**Key Changes in Draft Spec**:
*   **Stateless**: Endpoints like `tools/list` no longer vary per-connection [docs/specification/draft/changelog.mdx:12-13]().
*   **Subscriptions**: Replaces SSE resumability with `subscriptions/listen`, a single long-lived POST-response stream for change notifications [docs/specification/draft/changelog.mdx:18-19]().
*   **Headers**: Requires `Mcp-Method` and `Mcp-Name` on POST requests [docs/specification/draft/changelog.mdx:35-36]().

Sources: [docs/specification/draft/changelog.mdx:12-30]()

## Connection Lifecycle and Capabilities

### Stateless Lifecycle

The `initialize` handshake and `notifications/initialized` are **removed** in the latest draft specification.

**Sequence Diagram: Stateless Protocol Lifecycle**
```mermaid
sequenceDiagram
    participant Host
    participant Client
    participant Server
    
    Note over Client,Server: Stateless Interaction (Draft Spec)
    Client->>Server: tools/list request<br/>(_meta: {protocolVersion, clientCapabilities})
    Server-->>Client: tools/list response<br/>(resultType: "complete", tools: [...])
    
    Note over Client,Server: Feature Discovery
    Client->>Server: server/discover request
    Server-->>Client: discover response<br/>(versions, capabilities, serverInfo)
```

**server/discover**: Servers **MUST** implement this to advertise supported versions and capabilities for up-front selection [docs/specification/draft/changelog.mdx:16-17]().

Sources: [docs/specification/draft/changelog.mdx:14-21]()

### Capability Negotiation

Capabilities are now declared **per-request** in the `_meta` field.

**Client Capabilities** [schema/draft/schema.ts:474-573]():
*   `elicitation`: Supports user input requests.
*   `roots`: Supports filesystem boundary lists (deprecated in draft).
*   `sampling`: Supports LLM access (deprecated in draft).

**Server Capabilities** [schema/draft/schema.ts:580-690]():
*   `prompts`, `resources`, `tools`: Core primitives.
*   `logging`: Supports emitting logs.

Sources: [schema/draft/schema.ts:85-91](), [docs/specification/draft/changelog.mdx:14-16]()

## Server Features

### Tools, Resources, and Prompts

Servers expose functional and data primitives to the model.

| Feature | Control | Description |
| :--- | :--- | :--- |
| **Tools** | Model | Executable functions (e.g., `tools/call`). |
| **Resources** | Application | Data sources (e.g., `resources/read`). |
| **Prompts** | User | Template instructions (e.g., `prompts/get`). |

**Annotations and Caching**:
*   **Annotations**: `audience`, `priority`, and `lastModified` inform client display [schema/draft/schema.json:4-26]().
*   **Caching**: `CacheableResult` provides `ttlMs` and `cacheScope` (`public`/`private`) hints [schema/draft/schema.json:122-146]().

Sources: [docs/specification/draft/server/index.mdx:15-22](), [schema/draft/schema.json:122-146](), [docs/specification/draft/changelog.mdx:36-37]()

## Multi Round-Trip Requests (MRTR)

MRTR replaces server-initiated requests (like `sampling/createMessage`) with a pattern where the server indicates that more input is required to finish a request.

**Sequence Diagram: Multi Round-Trip Requests (MRTR)**
```mermaid
sequenceDiagram
    participant Client
    participant Server
    
    Client->>Server: "tools/call" (Request A)
    Server-->>Client: "JSONRPCResultResponse" (resultType: "input_required",<br/>inputRequests: [elicitation/create])
    Note over Client: Client performs elicitation
    Client->>Server: "tools/call" (Retry Request A,<br/>inputResponses: [...])
    Server-->>Client: "JSONRPCResultResponse" (resultType: "complete", content: [...])
```

*   **InputRequiredResult**: Used when a request is incomplete [schema/draft/schema.ts:178-185]().
*   **inputRequests**: Carries the nested request (e.g., `elicitation/create`) [schema/draft/schema.ts:1085-1090]().

Sources: [docs/specification/draft/changelog.mdx:24-27](), [schema/draft/schema.ts:1071-1100]()

## Task System (Extension)

Long-running operations are moved to an official extension `io.modelcontextprotocol/tasks`.

*   **Polling**: Uses `tasks/get` to check status [docs/specification/draft/changelog.mdx:22-23]().
*   **Input**: Uses `tasks/update` for mid-flight client-to-server input.
*   **States**: `working`, `input_required`, `completed`, `failed`, `cancelled`.

Sources: [docs/specification/draft/changelog.mdx:22-23](), [schema/draft/schema.ts:1212-1244]()

## Protocol Versioning

MCP uses date-based versioning (e.g., `2026-07-28`).

*   **LATEST_PROTOCOL_VERSION**: `2026-07-28` [schema/draft/schema.ts:30]().
*   **Negotiation**: Handled per-request via `_meta` or up-front via `server/discover`.
*   **Deprecation**: Features remain in spec for at least 12 months in the deprecated features registry [schema/draft/schema.ts:99-102]().

Sources: [schema/draft/schema.ts:30-32](), [docs/specification/draft/changelog.mdx:14-17]()

---

# Page: Architecture and Core Concepts

# Architecture and Core Concepts

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/docs/develop/build-client.mdx](docs/docs/develop/build-client.mdx)
- [docs/docs/develop/build-server.mdx](docs/docs/develop/build-server.mdx)
- [docs/docs/develop/build-with-agent-skills.mdx](docs/docs/develop/build-with-agent-skills.mdx)
- [docs/docs/learn/architecture.mdx](docs/docs/learn/architecture.mdx)
- [docs/docs/learn/client-concepts.mdx](docs/docs/learn/client-concepts.mdx)
- [docs/docs/learn/server-concepts.mdx](docs/docs/learn/server-concepts.mdx)
- [docs/docs/sdk.mdx](docs/docs/sdk.mdx)
- [docs/specification/2024-11-05/architecture/index.mdx](docs/specification/2024-11-05/architecture/index.mdx)
- [docs/specification/2025-03-26/architecture/index.mdx](docs/specification/2025-03-26/architecture/index.mdx)
- [docs/specification/2025-06-18/architecture/index.mdx](docs/specification/2025-06-18/architecture/index.mdx)
- [docs/specification/2025-11-25/architecture/index.mdx](docs/specification/2025-11-25/architecture/index.mdx)
- [docs/specification/draft/architecture/index.mdx](docs/specification/draft/architecture/index.mdx)
- [docs/specification/draft/basic/patterns/mrtr.mdx](docs/specification/draft/basic/patterns/mrtr.mdx)
- [docs/specification/draft/basic/transports/index.mdx](docs/specification/draft/basic/transports/index.mdx)
- [docs/specification/draft/basic/transports/stdio.mdx](docs/specification/draft/basic/transports/stdio.mdx)

</details>



This document provides a technical overview of the Model Context Protocol (MCP) architecture, covering its JSON-RPC foundation, client-server model, and the transition to a stateless architecture in the latest specification.

## Overview

MCP is a schema-driven protocol that enables AI applications (hosts) to integrate with external data sources and tools (servers). The architecture is designed for modularity, separating the data layer (semantics) from the transport layer (communication). The protocol uses [JSON-RPC 2.0](https://www.jsonrpc.org/specification) as its messaging foundation [docs/docs/learn/architecture.mdx:82-85]().

The protocol focuses solely on the exchange of context; it does not dictate how AI applications manage that context or interact with LLMs [docs/docs/learn/architecture.mdx:22-25]().

## Client-Server Topology

MCP follows a client-server architecture where an **MCP Host** (e.g., Claude Desktop, Claude Code, or an IDE) coordinates one or more **MCP Clients**. Each client maintains a dedicated, one-to-one connection to a specific **MCP Server** [docs/docs/learn/architecture.mdx:28-40]().

### Participant Roles

| Participant | Role | Responsibility |
|-------------|------|----------------|
| **MCP Host** | AI Application | Acts as the container; manages multiple client instances, enforces security policies, and handles user authorization [docs/specification/draft/architecture/index.mdx:50-60](). |
| **MCP Client** | Protocol Component | Maintains a connection to exactly one server, attaches protocol metadata to requests, and routes messages bidirectionally [docs/specification/draft/architecture/index.mdx:61-72](). |
| **MCP Server** | Context Provider | Program that exposes Tools, Resources, and Prompts. Can be local (stdio) or remote (HTTP) [docs/specification/draft/architecture/index.mdx:74-83](). |

**Client-Server Entity Mapping**

```mermaid
graph TB
    subgraph HostApp["MCP Host (e.g. Visual Studio Code)"]
        direction TB
        C1["ClientSession (Instance 1)"]
        C2["ClientSession (Instance 2)"]
    end
    
    subgraph LocalSrv["Local Server Process"]
        direction LR
        Transport1["StdioServerTransport"]
        Handler1["FastMCP / McpServer"]
    end
    
    subgraph RemoteSrv["Remote Service"]
        direction LR
        Transport2["StreamableHTTPTransport"]
        Handler2["Sentry / External API"]
    end
    
    C1 ---|"JSON-RPC (stdio)"| Transport1
    C2 ---|"JSON-RPC (HTTP)"| Transport2
    Transport1 --- Handler1
    Transport2 --- Handler2
```
Sources: [docs/docs/learn/architecture.mdx:44-61](), [docs/docs/develop/build-client.mdx:114-122](), [docs/specification/draft/architecture/index.mdx:17-48]()

## Stateless Architecture (Draft Spec)

The latest protocol revision introduces a shift toward a **stateless architecture**. In this model, every request is self-contained and carries its own protocol version and capabilities [docs/specification/draft/architecture/index.mdx:7-9]().

### Key Architectural Shifts
1.  **Handshake Removal**: Legacy versions used an `initialize` handshake. Modern MCP uses `server/discover` for up-front capability discovery, but every subsequent request must still include metadata [docs/specification/draft/architecture/index.mdx:118-123]().
2.  **Request-Scoped Capabilities**: Capabilities are declared per-request via the `_meta` field, allowing for dynamic feature negotiation [docs/specification/draft/architecture/index.mdx:118-123]().
3.  **Sessionless HTTP**: Streamable HTTP no longer relies on a long-lived session ID for basic requests; the protocol is designed to work without stateful load balancing [docs/specification/draft/basic/patterns/mrtr.mdx:29-32]().

### The `_meta` Field
Metadata is attached to interactions using the `_meta` field. Reserved keys use the `io.modelcontextprotocol/` prefix.

| Meta Key | Purpose |
|----------|---------|
| `protocolVersion` | The protocol version for this specific request [docs/specification/draft/architecture/index.mdx:144-144](). |
| `clientCapabilities` | Declares supported features (e.g., sampling, elicitation) for this request [docs/specification/draft/architecture/index.mdx:118-123](). |

Sources: [docs/specification/draft/architecture/index.mdx:116-130](), [docs/specification/draft/basic/transports/stdio.mdx:65-72]()

## Protocol Layers

### Data Layer
The data layer implements a JSON-RPC 2.0 based exchange protocol that defines the message structure and semantics [docs/docs/learn/architecture.mdx:82-85](). It handles primitives like tools, resources, and prompts [docs/docs/learn/architecture.mdx:87-90]().

**Data Layer Message Structure**

```mermaid
graph TD
    subgraph JSONRPC["JSON-RPC 2.0 Types"]
        Msg["JSONRPCMessage"]
        Req["JSONRPCRequest<br/>id: RequestId<br/>method: string<br/>params: RequestParams"]
        Res["JSONRPCResponse<br/>id: RequestId<br/>result: Result"]
        Notif["JSONRPCNotification<br/>method: string<br/>params: NotificationParams"]
    end

    subgraph Meta["Request Metadata (_meta)"]
        direction TB
        Ver["io.modelcontextprotocol/protocolVersion"]
        Caps["io.modelcontextprotocol/clientCapabilities"]
    end

    Msg --> Req
    Msg --> Res
    Msg --> Notif
    Req -.-> Meta
```
Sources: [docs/docs/learn/architecture.mdx:103-108](), [docs/specification/draft/architecture/index.mdx:116-130](), [docs/specification/draft/basic/transports/stdio.mdx:65-72]()

### Transport Layer
The transport layer manages communication channels and message framing. MCP supports two primary mechanisms [docs/docs/learn/architecture.mdx:92-95]():

1.  **Stdio Transport**: Uses standard input/output streams for direct process communication. Servers read from `stdin` and write to `stdout`. Messages are newline-delimited [docs/specification/draft/basic/transports/stdio.mdx:7-13]().
2.  **Streamable HTTP Transport**: Uses HTTP POST for messages with optional Server-Sent Events (SSE) for streaming [docs/docs/learn/architecture.mdx:99-101]().

## Core Communication Patterns

### Multi Round-Trip Requests (MRTR)
MRTR replaces the legacy pattern of server-initiated requests. It allows a server to request additional information from the client as part of a single logical operation [docs/specification/draft/basic/patterns/mrtr.mdx:7-14]().

1.  **Request**: Client sends a request (e.g., `tools/call`) [docs/specification/draft/basic/patterns/mrtr.mdx:44-44]().
2.  **Input Required**: Server determines more info is needed and returns an `InputRequiredResult` [docs/specification/draft/basic/patterns/mrtr.mdx:46-46]().
3.  **Gathering**: Client gathers input (via Elicitation, Sampling, etc.) [docs/specification/draft/basic/patterns/mrtr.mdx:48-48]().
4.  **Retry**: Client retries the original request with the new input included [docs/specification/draft/basic/patterns/mrtr.mdx:49-49]().

### Subscriptions
Clients can monitor changes by opening a subscription stream using `subscriptions/listen`. The server then sends notifications (e.g., `notifications/resources/updated`) tagged with a `subscriptionId` [docs/specification/draft/architecture/index.mdx:155-161]().

Sources: [docs/specification/draft/basic/patterns/mrtr.mdx:25-52](), [docs/specification/draft/architecture/index.mdx:131-162](), [docs/specification/draft/basic/transports/stdio.mdx:41-54]()

---

# Page: JSON-RPC Message System

# JSON-RPC Message System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.prettierignore](.prettierignore)
- [docs/specification/2025-06-18/schema.mdx](docs/specification/2025-06-18/schema.mdx)
- [docs/specification/2025-11-25/schema.mdx](docs/specification/2025-11-25/schema.mdx)
- [docs/specification/draft/basic/index.mdx](docs/specification/draft/basic/index.mdx)
- [docs/specification/draft/changelog.mdx](docs/specification/draft/changelog.mdx)
- [docs/specification/draft/client/elicitation.mdx](docs/specification/draft/client/elicitation.mdx)
- [docs/specification/draft/schema.mdx](docs/specification/draft/schema.mdx)
- [docs/style.css](docs/style.css)
- [schema/2025-11-25/schema.json](schema/2025-11-25/schema.json)
- [schema/2025-11-25/schema.ts](schema/2025-11-25/schema.ts)
- [schema/draft/examples/CallToolResultResponse/call-tool-result-response.json](schema/draft/examples/CallToolResultResponse/call-tool-result-response.json)
- [schema/draft/examples/CompleteResultResponse/completion-result-response.json](schema/draft/examples/CompleteResultResponse/completion-result-response.json)
- [schema/draft/examples/GetPromptResultResponse/get-prompt-result-response.json](schema/draft/examples/GetPromptResultResponse/get-prompt-result-response.json)
- [schema/draft/examples/ReadResourceResultResponse/read-resource-result-response.json](schema/draft/examples/ReadResourceResultResponse/read-resource-result-response.json)
- [schema/draft/schema.json](schema/draft/schema.json)
- [schema/draft/schema.ts](schema/draft/schema.ts)
- [scripts/pull-registry-docs.sh](scripts/pull-registry-docs.sh)
- [seps/414-request-meta.md](seps/414-request-meta.md)
- [typedoc.config.mjs](typedoc.config.mjs)
- [typedoc.plugin.mjs](typedoc.plugin.mjs)

</details>



## Purpose and Scope

This page documents the JSON-RPC 2.0 message system that forms the foundation of the Model Context Protocol (MCP). It details the structure and semantics of the three core message types—requests, responses, and notifications—along with error handling, the metadata system, and the ID requirements that enable bidirectional communication.

The protocol has transitioned to a **stateless architecture** as of version `2026-07-28`. Every request now carries protocol versioning, client identity, and capability negotiation within its metadata, removing the need for an initialization handshake [docs/specification/draft/changelog.mdx:14-15]().

## Core Message Types

MCP uses JSON-RPC 2.0 as specified in [https://www.jsonrpc.org/specification](https://www.jsonrpc.org/specification). All messages exchanged between clients and servers **MUST** follow this specification [docs/specification/draft/basic/index.mdx:27-29]().

The protocol defines three message types, represented by the union type `JSONRPCMessage` [schema/draft/schema.ts:26-27]():

```typescript
type JSONRPCMessage = JSONRPCRequest | JSONRPCNotification | JSONRPCResponse;
```

### Requests

A **request** is a message that expects a response. Both clients and servers can send requests to each other, enabling bidirectional communication [docs/specification/draft/basic/index.mdx:33-33]().

**Structure** [schema/draft/schema.ts:129-132]():

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `jsonrpc` | string | Yes | **MUST** be `"2.0"` [schema/draft/schema.ts:32]() |
| `id` | `RequestId` | Yes | Unique identifier (string or number) [schema/draft/schema.ts:122]() |
| `method` | string | Yes | The name of the method to invoke |
| `params` | object | No | Parameters for the method, typically including `_meta` |

**Key requirements:**
- The `id` field **MUST NOT** be `null` [docs/specification/draft/basic/index.mdx:47-47]().
- The `id` **MUST NOT** match the ID of any other request the sender has issued and not yet received a response for [docs/specification/draft/basic/index.mdx:48-49]().

Sources: [schema/draft/schema.ts:129-132](), [docs/specification/draft/basic/index.mdx:33-50]()

### Responses

A **response** is sent in reply to a request. It contains either a successful result or an error.

**Structure** [docs/specification/draft/basic/index.mdx:57-101]():

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `jsonrpc` | string | Yes | **MUST** be `"2.0"` |
| `id` | `RequestId` | Yes | **MUST** match the ID of the request being answered |
| `result` | `Result` | Conditional | Present on success; **MUST** include `resultType` [docs/specification/draft/basic/index.mdx:73-73]() |
| `error` | `Error` | Conditional | Present on failure; **MUST** include `code` and `message` |

**Result Types:**
MCP supports polymorphic results. The `resultType` field allows the client to determine how to parse the object [docs/specification/draft/basic/index.mdx:77-79]():
- `"complete"`: The request completed successfully [docs/specification/draft/basic/index.mdx:81-81]().
- `"input_required"`: The request requires additional input via the Multi Round-Trip Request (MRTR) pattern [docs/specification/draft/basic/index.mdx:82-82]().

Sources: [docs/specification/draft/basic/index.mdx:53-86](), [schema/draft/schema.ts:148-152](), [schema/draft/schema.ts:159-163]()

### Notifications

A **notification** is a one-way message that does not expect a response.

**Structure** [schema/draft/schema.ts:139-141]():

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `jsonrpc` | string | Yes | **MUST** be `"2.0"` |
| `method` | string | Yes | The name of the notification |
| `params` | `NotificationParams` | No | Parameters for the notification |

**Key requirements:**
- **MUST NOT** include an `id` field [docs/specification/draft/basic/index.mdx:158-158]().
- The receiver **MUST NOT** send a response [docs/specification/draft/basic/index.mdx:159-159]().

Sources: [schema/draft/schema.ts:139-141](), [docs/specification/draft/basic/index.mdx:155-163]()

## Error Handling

MCP uses standard JSON-RPC error codes and defines specific ranges for protocol-level errors.

### Error Codes and Allocation Policy

The specification partitions the implementation-defined range (`-32000` to `-32099`) as follows [docs/specification/draft/basic/index.mdx:112-125]():

| Range | Usage |
|-------|-------|
| `-32700`, `-32600` to `-32603` | Standard JSON-RPC 2.0 errors (Parse error, Invalid request, etc.) |
| `-32000` to `-32019` | **Legacy.** Allocated before the current policy. New codes MUST NOT be added here. |
| `-32020` to `-32099` | **Reserved for MCP Specification.** Defined exclusively in the schema. |

**Defined MCP Error Codes:**
- `-32020`: `HeaderMismatch` [docs/specification/draft/basic/index.mdx:131]()
- `-32021`: `MissingRequiredClientCapability` [docs/specification/draft/basic/index.mdx:132]()
- `-32022`: `UnsupportedProtocolVersion` [docs/specification/draft/basic/index.mdx:133]()

Sources: [docs/specification/draft/basic/index.mdx:107-153]()

## Metadata System (`_meta`)

The `_meta` field allows clients and servers to attach additional metadata to interactions without modifying the core parameter schemas.

### Key Naming and Reserved Prefixes
Metadata keys follow a strict `[prefix/]name` structure [schema/draft/schema.ts:39-40]():
- **Prefix:** Optional series of labels separated by dots (`.`), followed by a slash (`/`).
- **Reserved:** Any prefix where the second label is `modelcontextprotocol` or `mcp` is reserved (e.g., `io.modelcontextprotocol/`) [schema/draft/schema.ts:45-45]().

### Request Metadata (`RequestMetaObject`)
In the stateless protocol version (`2026-07-28`), the `_meta` field on requests is **required** and must include the following fields [schema/draft/schema.ts:63-111]():

| Field | Type | Description |
|-------|------|-------------|
| `io.modelcontextprotocol/protocolVersion` | string | The version being used (e.g., `2026-07-28`) |
| `io.modelcontextprotocol/clientInfo` | `Implementation` | Identifies the client software (name and version) |
| `io.modelcontextprotocol/clientCapabilities` | `ClientCapabilities` | Declares capabilities for this specific request |
| `progressToken` | `ProgressToken` | Optional token for out-of-band progress notifications |
| `io.modelcontextprotocol/logLevel` | `LoggingLevel` | Optional desired log level (deprecated) |

Sources: [schema/draft/schema.ts:35-158](), [docs/specification/draft/changelog.mdx:14-15]()

## Message Flow Patterns

### Multi Round-Trip Requests (MRTR)
MRTR replaces server-initiated requests (like sampling or elicitation) with a polling/retry pattern to maintain statelessness [docs/specification/draft/changelog.mdx:24-24]().

```mermaid
sequenceDiagram
    participant C as "Client"
    participant S as "Server"
    
    C->>S: Request (method: "tools/call", _meta: { capabilities... })
    Note over S: Needs user input
    S-->>C: Response (resultType: "input_required", inputRequests: ["elicitation/create"])
    Note over C: Collects user input
    C->>S: Request (method: "tools/call", inputResponses: [...], _meta: { capabilities... })
    S-->>C: Response (resultType: "complete", result: { ... })
```

### Notification Correlation
Notifications delivered via a subscription stream include a subscription ID in their metadata to allow client correlation [schema/draft/schema.ts:120-134]().

```mermaid
graph TB
    subgraph "Message Entity Mapping"
        REQ["JSONRPCRequest<br/>(schema.ts:129)"]
        RESP["JSONRPCResponse<br/>(schema.ts:170)"]
        NOTIF["JSONRPCNotification<br/>(schema.ts:139)"]
    end

    subgraph "Code Components"
        META["RequestMetaObject<br/>(schema.ts:63)"]
        RES_TYPE["ResultType<br/>(basic/index.mdx:75)"]
        ERR["JSONRPCErrorResponse<br/>(schema.mdx:11)"]
    end

    REQ --> META
    RESP --> RES_TYPE
    RESP --> ERR
```

Sources: [schema/draft/schema.ts:120-134](), [docs/specification/draft/changelog.mdx:24-27](), [docs/specification/draft/schema.mdx:11-36]()

## Pagination and Progress

### Pagination
List operations use `PaginatedRequestParams` and return `PaginatedResult`.
- `cursor`: An opaque token used to represent a cursor for pagination [schema/draft/schema.ts:172]().
- `nextCursor`: If present in the result, indicates more data is available [schema/draft/schema.ts:1075]().

### Progress Notifications
If a request includes a `progressToken` in `_meta`, the server may emit `notifications/progress` [schema/draft/schema.ts:64-67](). These notifications are delivered on the **response stream** of the request they relate to, not the general subscription stream [docs/specification/draft/changelog.mdx:18-18]().

Sources: [schema/draft/schema.ts:165-172](), [docs/specification/draft/changelog.mdx:18-18]()

---

# Page: Transport Layer

# Transport Layer

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [blog/content/posts/2025-12-19-mcp-transport-future.md](blog/content/posts/2025-12-19-mcp-transport-future.md)
- [docs/seps/2243-http-standardization.mdx](docs/seps/2243-http-standardization.mdx)
- [docs/seps/2549-TTL-for-list-results.mdx](docs/seps/2549-TTL-for-list-results.mdx)
- [docs/seps/2567-sessionless-mcp.mdx](docs/seps/2567-sessionless-mcp.mdx)
- [docs/specification/draft/basic/transports/streamable-http.mdx](docs/specification/draft/basic/transports/streamable-http.mdx)
- [docs/specification/draft/basic/versioning.mdx](docs/specification/draft/basic/versioning.mdx)
- [schema/draft/examples/HeaderMismatchError/header-mismatch.json](schema/draft/examples/HeaderMismatchError/header-mismatch.json)
- [schema/draft/examples/MissingRequiredClientCapabilityError/missing-elicitation-capability.json](schema/draft/examples/MissingRequiredClientCapabilityError/missing-elicitation-capability.json)
- [schema/draft/examples/ReadResourceResultResponse/read-resource-result-response-with-ttl.json](schema/draft/examples/ReadResourceResultResponse/read-resource-result-response-with-ttl.json)
- [schema/draft/examples/UnsupportedProtocolVersionError/unsupported-version.json](schema/draft/examples/UnsupportedProtocolVersionError/unsupported-version.json)
- [scripts/render-seps.ts](scripts/render-seps.ts)
- [seps/2243-http-standardization.md](seps/2243-http-standardization.md)
- [seps/2549-TTL-for-list-results.md](seps/2549-TTL-for-list-results.md)
- [seps/2567-sessionless-mcp.md](seps/2567-sessionless-mcp.md)

</details>



## Purpose and Scope

The transport layer defines how JSON-RPC messages are physically transmitted between MCP clients and servers. This page covers the two standard transport mechanisms (stdio and Streamable HTTP), their message framing, SSE streaming, session management, and connection patterns. It also covers the HTTP standardization (SEP-2243), the introduction of TTL-based caching (SEP-2549), and the removal of protocol-level sessions (SEP-2567) in the 2026-07-28 protocol revision.

**Sources:** [docs/specification/draft/basic/transports/index.mdx:7-25](), [docs/specification/draft/architecture/index.mdx:7-13]()

## Transport Mechanisms

MCP defines two standard transports for carrying UTF-8 encoded JSON-RPC messages:

| Transport | Use Case | Connection Model | Message Framing |
|-----------|----------|------------------|-----------------|
| **stdio** | Local servers as subprocesses | Client launches server process | Newline-delimited JSON |
| **Streamable HTTP** | Remote/Distributed servers | Server runs independently | HTTP POST + SSE |

Protocol semantics are identical on every transport; the binding defines how messages are framed, how metadata is carried, and how cancellation is signaled.

**Sources:** [docs/specification/draft/basic/transports/index.mdx:10-22](), [docs/specification/draft/basic/transports/stdio.mdx:7-22]()

## stdio Transport

### Architecture

In the stdio transport, the client launches the MCP server as a subprocess. The two ends communicate over the subprocess's standard streams.

```mermaid
graph TB
    subgraph "ApplicationHostProcess"
        Client["Client"]
    end
    
    subgraph "ServerSubprocess"
        Server["Server"]
        stdin["stdin<br/>(read JSONRPCMessage)"]
        stdout["stdout<br/>(write JSONRPCMessage)"]
        stderr["stderr<br/>(UTF-8 logging)"]
    end
    
    Client -->|"Launch"| Server
    Client -->|"Write JSON-RPC<br/>(newline-delimited)"| stdin
    stdout -->|"Read JSON-RPC<br/>(newline-delimited)"| Client
    stderr -.->|"Optional logs"| Client
    
    stdin --> Server
    Server --> stdout
    Server -.-> stderr
```

**Sources:** [docs/specification/draft/basic/transports/stdio.mdx:7-22]()

### Message Framing and Constraints

**Message Format:**
- Each message **MUST** be a complete JSON-RPC request, notification, or response [docs/specification/draft/basic/transports/stdio.mdx:12-12]().
- Messages are delimited by newlines and **MUST NOT** contain embedded newlines [docs/specification/draft/basic/transports/stdio.mdx:13-13]().
- The server **MUST NOT** write non-MCP messages to `stdout` [docs/specification/draft/basic/transports/stdio.mdx:18-19]().

**Stream Usage:**
- **stdin**: Client writes requests and notifications to the server [docs/specification/draft/basic/transports/stdio.mdx:35-37]().
- **stdout**: Server writes responses and notifications to the client [docs/specification/draft/basic/transports/stdio.mdx:41-44]().
- **stderr**: Used for logging purposes only. Clients **SHOULD NOT** assume `stderr` output indicates error conditions [docs/specification/draft/basic/transports/stdio.mdx:14-17]().

### Cancellation and Shutdown

- **Cancellation**: To cancel an in-flight request, the client sends a `notifications/cancelled` notification referencing the request ID [docs/specification/draft/basic/transports/stdio.mdx:78-83]().
- **Graceful Shutdown**: Initiated by the client closing the server's `stdin`. Servers **SHOULD** exit promptly when `stdin` is closed [docs/specification/draft/basic/transports/stdio.mdx:89-104]().
- **Unexpected Termination**: If the server exits, the client **SHOULD** restart it. Because the protocol is stateless (in modern versions), in-flight requests can be retried against the fresh process [docs/specification/draft/basic/transports/stdio.mdx:111-115]().

**Sources:** [docs/specification/draft/basic/transports/stdio.mdx:78-115]()

## Streamable HTTP Transport

### Architecture (Modern/Stateless)

The 2026-07-28 revision of Streamable HTTP moved toward a stateless model. The server exposes a single **MCP endpoint** that accepts POST requests. Protocol-level sessions and the `GET` stream endpoint have been removed [docs/specification/draft/basic/transports/streamable-http.mdx:16-20]().

```mermaid
graph TB
    subgraph "Client"
        C["Client"]
        SSER["SSEReader"]
    end
    
    subgraph "MCPServerIndependentProcess"
        Endpoint["MCPEndpoint<br/>POST /mcp"]
        Auth["Auth & Origin<br/>Validation"]
        Logic["JSONRPCProcessor"]
    end
    
    C -->|"POST (Request/Notification)"| Endpoint
    Endpoint --> Auth
    Auth --> Logic
    Logic -->|"200 OK (JSON Response)"| C
    Logic -->|"200 OK (SSE Stream)"| SSER
    Logic -->|"202 Accepted (Notification)"| C
```

**Sources:** [docs/specification/draft/basic/transports/streamable-http.mdx:16-45](), [docs/specification/draft/architecture/index.mdx:7-13]()

### HTTP Message Flow

1. **Client to Server**: Every JSON-RPC message is a new HTTP POST request [docs/specification/draft/basic/transports/streamable-http.mdx:72-73]().
2. **Notifications**: If the body is a notification, the server returns `202 Accepted` with no body [docs/specification/draft/basic/transports/streamable-http.mdx:82-84]().
3. **Requests**: The server returns either `application/json` (single response) or `text/event-stream` (SSE stream for progress/messages followed by final response) [docs/specification/draft/basic/transports/streamable-http.mdx:88-91]().
4. **Cancellation**: Closing the SSE response stream acts as the cancellation signal; no `notifications/cancelled` message is used on HTTP [docs/specification/draft/basic/transports/streamable-http.mdx:98-100]().

### SSE Response Streams

When returning `Content-Type: text/event-stream`:
- The server **MAY** send JSON-RPC notifications (e.g., `notifications/progress`) before the final response [docs/specification/draft/basic/transports/streamable-http.mdx:112-116]().
- The final JSON-RPC response **SHOULD** terminate the stream [docs/specification/draft/basic/transports/streamable-http.mdx:125-125]().
- Servers **SHOULD** include `X-Accel-Buffering: no` to prevent proxy buffering [docs/specification/draft/basic/transports/streamable-http.mdx:136-138]().
- **Keep-alive**: Servers should emit SSE comment lines (lines starting with `:`) to prevent idle timeouts [docs/specification/draft/basic/transports/streamable-http.mdx:146-153]().

**Sources:** [docs/specification/draft/basic/transports/streamable-http.mdx:109-153]()

## HTTP Header Standardization (SEP-2243)

To enable network intermediaries (load balancers, WAFs) to route traffic without deep packet inspection, critical metadata is mirrored into HTTP headers.

| Header Name | Source Field | Required For |
|-------------|--------------|--------------|
| `Mcp-Method` | `method` | All requests and notifications |
| `Mcp-Name` | `params.name` or `params.uri` | `tools/call`, `resources/read`, `prompts/get` |

### Security and Validation
- **Mismatches**: Servers MUST reject requests where header values do not match the JSON body [docs/seps/2243-http-standardization.mdx:57-59]().
- **Error Code**: A mismatch results in a `-32020` error [schema/draft/examples/HeaderMismatchError/header-mismatch.json:5-7]().

### Custom Headers (`x-mcp-header`)
Servers can designate tool parameters to be mirrored into headers using the `x-mcp-header` extension in the tool's `inputSchema`.
- Construct header as `Mcp-Param-{name}` [docs/seps/2243-http-standardization.mdx:176-176]().
- Restricted to primitive types (integer, string, boolean) [docs/seps/2243-http-standardization.mdx:168-168]().

**Sources:** [docs/seps/2243-http-standardization.mdx:46-63](), [seps/2243-http-standardization.md:30-60]()

## Caching and TTL (SEP-2549)

To reduce reliance on long-lived SSE streams for notifications, MCP supports time-based caching for list results.

### `CacheableResult` Interface
Results from `tools/list`, `prompts/list`, `resources/list`, and `resources/read` can include caching hints [seps/2549-TTL-for-list-results.md:85-86]():

- `ttlMs`: Number of milliseconds the client may cache the response [seps/2549-TTL-for-list-results.md:52-63]().
- `cacheScope`: Either `"public"` (shared cacheable) or `"private"` (user-specific) [seps/2549-TTL-for-list-results.md:65-78]().

**Sources:** [seps/2549-TTL-for-list-results.md:38-79](), [docs/seps/2549-TTL-for-list-results.mdx:59-98]()

## Connection Patterns and Evolution

### Stateless Architecture
Modern MCP (2026-07-28+) is stateless. Every request is self-contained and carries its own:
- Protocol Version [docs/specification/draft/basic/versioning.mdx:41-43]()
- Client Identity [docs/specification/draft/architecture/index.mdx:8-9]()
- Capabilities [docs/specification/draft/architecture/index.mdx:118-120]()

This removes the need for the `initialize` handshake and protocol-level sessions [docs/specification/draft/basic/transports/streamable-http.mdx:16-20](). SEP-2567 formally removed the `Mcp-Session-Id` header and protocol-level session concept in favor of explicit state handles [seps/2567-sessionless-mcp.md:11-15]().

### Subscriptions
Long-lived notifications (e.g., `notifications/tools/list_changed`) are delivered via a `subscriptions/listen` request. The response is an SSE stream that stays open for the duration of the subscription [docs/specification/draft/basic/patterns/index.mdx:62-67]().

```mermaid
sequenceDiagram
    participant Client
    participant Server
    
    Client->>Server: POST /mcp (subscriptions/listen)
    Server-->>Client: HTTP 200 (text/event-stream)
    Server-->>Client: event: message<br/>data: notifications/subscriptions/acknowledged
    loop ActiveSubscription
        Server-->>Client: event: message<br/>data: notifications/resources/updated
    end
    Note over Client, Server: Stream remains open for notifications
```

**Sources:** [docs/specification/draft/basic/patterns/index.mdx:62-78](), [docs/specification/draft/basic/transports/streamable-http.mdx:127-134]()

## Backward Compatibility

Implementations must handle "Legacy" (handshake-based) vs "Modern" (stateless) counterparts.

- **Terminology**: "Modern" refers to revision `2026-07-28` and later; "Legacy" refers to `2025-11-25` and earlier [docs/specification/draft/basic/versioning.mdx:34-37]().
- **stdio Detection**: Probe with `server/discover`. If the server returns a modern error (e.g., `UnsupportedProtocolVersionError`) or a result, it is modern. Otherwise, fall back to `initialize` [docs/specification/draft/basic/transports/stdio.mdx:123-137]().
- **HTTP Detection**: Attempt a modern request. Inspect the body of a `400 Bad Request` before falling back [docs/specification/draft/basic/versioning.mdx:139-141]().

**Sources:** [docs/specification/draft/basic/versioning.mdx:126-153](), [docs/specification/draft/basic/transports/stdio.mdx:121-150]()

---

# Page: Connection Lifecycle and Capabilities

# Connection Lifecycle and Capabilities

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/specification/2024-11-05/basic/index.mdx](docs/specification/2024-11-05/basic/index.mdx)
- [docs/specification/2024-11-05/basic/lifecycle.mdx](docs/specification/2024-11-05/basic/lifecycle.mdx)
- [docs/specification/2024-11-05/basic/transports.mdx](docs/specification/2024-11-05/basic/transports.mdx)
- [docs/specification/2024-11-05/basic/utilities/cancellation.mdx](docs/specification/2024-11-05/basic/utilities/cancellation.mdx)
- [docs/specification/2024-11-05/basic/utilities/ping.mdx](docs/specification/2024-11-05/basic/utilities/ping.mdx)
- [docs/specification/2024-11-05/client/sampling.mdx](docs/specification/2024-11-05/client/sampling.mdx)
- [docs/specification/2024-11-05/index.mdx](docs/specification/2024-11-05/index.mdx)
- [docs/specification/2024-11-05/server/index.mdx](docs/specification/2024-11-05/server/index.mdx)
- [docs/specification/2025-03-26/basic/index.mdx](docs/specification/2025-03-26/basic/index.mdx)
- [docs/specification/2025-03-26/basic/lifecycle.mdx](docs/specification/2025-03-26/basic/lifecycle.mdx)
- [docs/specification/2025-03-26/basic/transports.mdx](docs/specification/2025-03-26/basic/transports.mdx)
- [docs/specification/2025-03-26/changelog.mdx](docs/specification/2025-03-26/changelog.mdx)
- [docs/specification/2025-03-26/client/sampling.mdx](docs/specification/2025-03-26/client/sampling.mdx)
- [docs/specification/2025-03-26/index.mdx](docs/specification/2025-03-26/index.mdx)
- [docs/specification/2025-03-26/server/index.mdx](docs/specification/2025-03-26/server/index.mdx)
- [docs/specification/draft/basic/transports/streamable-http.mdx](docs/specification/draft/basic/transports/streamable-http.mdx)
- [docs/specification/draft/basic/versioning.mdx](docs/specification/draft/basic/versioning.mdx)
- [docs/specification/draft/index.mdx](docs/specification/draft/index.mdx)
- [docs/specification/draft/server/discover.mdx](docs/specification/draft/server/discover.mdx)
- [docs/specification/draft/server/index.mdx](docs/specification/draft/server/index.mdx)
- [schema/draft/examples/DiscoverResult/server-capabilities-discovery.json](schema/draft/examples/DiscoverResult/server-capabilities-discovery.json)
- [schema/draft/examples/DiscoverResultResponse/discover-result-response.json](schema/draft/examples/DiscoverResultResponse/discover-result-response.json)
- [schema/draft/examples/HeaderMismatchError/header-mismatch.json](schema/draft/examples/HeaderMismatchError/header-mismatch.json)
- [schema/draft/examples/MissingRequiredClientCapabilityError/missing-elicitation-capability.json](schema/draft/examples/MissingRequiredClientCapabilityError/missing-elicitation-capability.json)
- [schema/draft/examples/UnsupportedProtocolVersionError/unsupported-version.json](schema/draft/examples/UnsupportedProtocolVersionError/unsupported-version.json)

</details>



This document details the Model Context Protocol (MCP) connection lifecycle, including the shift toward stateless interactions in recent protocol revisions, capability negotiation, protocol version negotiation, and connection termination.

## Lifecycle Evolution

The MCP connection lifecycle has evolved from a stateful, session-based model to a stateless, per-request model in modern protocol versions (revision `2026-07-28` and later).

| Era | Protocol Versions | Lifecycle Pattern | Key Mechanism |
| :--- | :--- | :--- | :--- |
| **Modern** | `2026-07-28`+ | Stateless | Per-request `_meta` and `server/discover` |
| **Legacy** | `2025-11-25` and earlier | Session-based | `initialize` handshake |

Sources: [docs/specification/draft/basic/versioning.mdx:34-37](), [docs/specification/draft/basic/transports/streamable-http.mdx:16-20]()

### Modern Lifecycle (Stateless)

In modern MCP, there is no mandatory initialization handshake. Every request is independent and carries its own version, identity, and capability information in the `_meta` field [docs/specification/draft/index.mdx:53-54](). This shift eliminates the need for protocol-level sessions [docs/specification/draft/basic/transports/streamable-http.mdx:20-20]().

```mermaid
sequenceDiagram
    participant Client as "MCP Client"
    participant Server as "MCP Server"

    Note over Client, Server: "Optional Discovery"
    Client->>+Server: "server/discover (method)"
    Server-->>-Client: "DiscoverResult (versions, capabilities, info)"

    Note over Client, Server: "Independent Requests"
    Client->>+Server: "Any RPC Request (with _meta)"
    alt "version supported"
        Server-->>Client: "RPC Result"
    else "version unsupported"
        Server-->>-Client: "UnsupportedProtocolVersionError"
        Note over Client: "Retry with supported version"
    end
```

Sources: [docs/specification/draft/basic/versioning.mdx:15-27](), [docs/specification/draft/server/discover.mdx:7-10](), [docs/specification/draft/index.mdx:53-54]()

### Legacy Lifecycle (Session-based)

Legacy versions require a formal three-step handshake to establish a session before any other operations (except pings/logging) can occur.

```mermaid
sequenceDiagram
    participant Client as "Legacy Client"
    participant Server as "Legacy Server"

    Note over Client,Server: "Initialization Phase"
    activate Client
    Client->>+Server: "initialize (request)"
    Server-->>Client: "initialize (response)"
    Client--)Server: "notifications/initialized"

    Note over Client,Server: "Operation Phase"
    rect rgb(240, 240, 240)
        Note over Client,Server: "Normal protocol operations"
    end

    Note over Client,Server: "Shutdown"
    Client--)-Server: "Disconnect / Close Transport"
    deactivate Server
```

Sources: [docs/specification/2025-03-26/basic/lifecycle.mdx:12-32]()

## Server Discovery

The `server/discover` method allows a client to query a server's supported protocol versions, capabilities, and identity [docs/specification/draft/server/discover.mdx:7-9](). Servers **MUST** implement this method [docs/specification/draft/server/discover.mdx:9-9]().

### Discovery Request
The request carries no body parameters but uses the standard `_meta` to convey client information [docs/specification/draft/server/discover.mdx:13-14]().

```json
{
  "jsonrpc": "2.0",
  "id": "discover-1",
  "method": "server/discover",
  "params": {
    "_meta": {
      "io.modelcontextprotocol/protocolVersion": "2026-07-28",
      "io.modelcontextprotocol/clientInfo": {
        "name": "ExampleClient",
        "version": "1.0.0"
      },
      "io.modelcontextprotocol/clientCapabilities": {}
    }
  }
}
```

Sources: [docs/specification/draft/server/discover.mdx:15-31]()

### Discovery Response
The server provides a `DiscoverResult` containing its supported versions and available features. This response supports caching via `ttlMs` and `cacheScope` [docs/specification/draft/server/discover.mdx:33-36]().

```json
{
  "jsonrpc": "2.0",
  "id": "discover-1",
  "result": {
    "resultType": "complete",
    "supportedVersions": ["2026-07-28"],
    "capabilities": {
      "tools": {},
      "resources": {}
    },
    "_meta": {
      "io.modelcontextprotocol/serverInfo": {
        "name": "ExampleServer",
        "version": "1.0.0"
      }
    },
    "instructions": "This server provides weather and resource utilities.",
    "ttlMs": 3600000,
    "cacheScope": "public"
  }
}
```

Sources: [docs/specification/draft/server/discover.mdx:38-60](), [schema/draft/examples/DiscoverResultResponse/discover-result-response.json:1-20]()

## Protocol Version Negotiation

Every modern request declares its protocol version in the `_meta` field [docs/specification/draft/basic/versioning.mdx:43-44](). On HTTP transports, this is also carried in the `MCP-Protocol-Version` header [docs/specification/draft/basic/versioning.mdx:44-46]().

If a server does not support the requested version, it **MUST** respond with an `UnsupportedProtocolVersionError` (code `-32022`) [docs/specification/draft/basic/versioning.mdx:48-52](). The error data includes the `supported` versions, enabling the client to retry with a mutually supported version [docs/specification/draft/basic/versioning.mdx:61-71]().

Sources: [docs/specification/draft/basic/versioning.mdx:43-71](), [schema/draft/examples/UnsupportedProtocolVersionError/unsupported-version.json:1-15]()

## Capability Negotiation

Capabilities establish which optional features are available. In the modern stateless model, negotiation occurs per-request via `_meta` [docs/specification/draft/index.mdx:54-54]().

### Key Capabilities

| Category | Capability | Description |
| :--- | :--- | :--- |
| **Server** | `tools` | Exposes callable functions for models [docs/specification/draft/index.mdx:62-62](). |
| **Server** | `resources` | Provides context and data for the model [docs/specification/draft/index.mdx:60-60](). |
| **Server** | `prompts` | Offers templated messages for users [docs/specification/draft/index.mdx:61-61](). |
| **Client** | `elicitation` | Support for server-initiated user input requests [docs/specification/draft/index.mdx:66-66](). |
| **Client** | `sampling` | (Legacy) Support for LLM access requests [docs/specification/2025-03-26/basic/lifecycle.mdx:148-148](). |

Sources: [docs/specification/draft/index.mdx:58-66](), [docs/specification/2025-03-26/basic/lifecycle.mdx:145-155]()

### Extension Negotiation
Support for optional extensions (e.g., `io.modelcontextprotocol/tasks`) is advertised in the `extensions` field of capabilities [docs/specification/draft/basic/versioning.mdx:82-85](). Extension identifiers must follow mandatory prefix rules [docs/specification/draft/basic/versioning.mdx:85-87]().

Sources: [docs/specification/draft/basic/versioning.mdx:80-116]()

## Connection Termination

Termination behavior is transport-specific:

*   **stdio**: The client closes the input stream to the server process [docs/specification/2025-03-26/basic/lifecycle.mdx:181-183](). The server should exit, or the client may escalate to `SIGTERM` and `SIGKILL` [docs/specification/2025-03-26/basic/lifecycle.mdx:184-187]().
*   **Streamable HTTP**: Interactions are generally discrete POST requests [docs/specification/draft/basic/transports/streamable-http.mdx:32-33](). For long-lived notification streams, closing the SSE response stream acts as the cancellation signal [docs/specification/draft/basic/transports/streamable-http.mdx:98-100]().

Sources: [docs/specification/2025-03-26/basic/lifecycle.mdx:181-196](), [docs/specification/draft/basic/transports/streamable-http.mdx:30-42](), [docs/specification/draft/basic/transports/streamable-http.mdx:98-101]()

## Backward Compatibility Rules

"Dual-era" implementations support both modern (stateless) and legacy (handshake) behaviors [docs/specification/draft/basic/versioning.mdx:38-39]().

1.  **stdio**: Clients probe with `server/discover` [docs/specification/draft/basic/versioning.mdx:136-138](). A recognized modern JSON-RPC error identifies a modern server; otherwise, the client falls back to `initialize` [docs/specification/draft/basic/versioning.mdx:143-147]().
2.  **Streamable HTTP**: Clients attempt a modern request and inspect the response of a `400 Bad Request` to determine if legacy fallback is necessary [docs/specification/draft/basic/versioning.mdx:139-141]().

Sources: [docs/specification/draft/basic/versioning.mdx:127-153]()

---

# Page: Server Features

# Server Features

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [blog/content/posts/2026-03-16-tool-annotations.md](blog/content/posts/2026-03-16-tool-annotations.md)
- [docs/seps/2106-json-schema-2020-12.mdx](docs/seps/2106-json-schema-2020-12.mdx)
- [docs/specification/draft/server/prompts.mdx](docs/specification/draft/server/prompts.mdx)
- [docs/specification/draft/server/resources.mdx](docs/specification/draft/server/resources.mdx)
- [docs/specification/draft/server/tools.mdx](docs/specification/draft/server/tools.mdx)
- [docs/specification/draft/server/utilities/caching.mdx](docs/specification/draft/server/utilities/caching.mdx)
- [docs/specification/draft/server/utilities/completion.mdx](docs/specification/draft/server/utilities/completion.mdx)
- [docs/specification/draft/server/utilities/pagination.mdx](docs/specification/draft/server/utilities/pagination.mdx)
- [schema/draft/examples/CallToolResult/result-with-array-structured-content.json](schema/draft/examples/CallToolResult/result-with-array-structured-content.json)
- [schema/draft/examples/ListPromptsResult/prompts-list-with-cursor-and-ttl.json](schema/draft/examples/ListPromptsResult/prompts-list-with-cursor-and-ttl.json)
- [schema/draft/examples/ListPromptsResultResponse/list-prompts-result-response.json](schema/draft/examples/ListPromptsResultResponse/list-prompts-result-response.json)
- [schema/draft/examples/ListResourceTemplatesResult/resource-templates-list-with-cursor-and-ttl.json](schema/draft/examples/ListResourceTemplatesResult/resource-templates-list-with-cursor-and-ttl.json)
- [schema/draft/examples/ListResourceTemplatesResultResponse/list-resource-templates-result-response.json](schema/draft/examples/ListResourceTemplatesResultResponse/list-resource-templates-result-response.json)
- [schema/draft/examples/ListResourcesResult/resources-list-with-cursor-and-ttl.json](schema/draft/examples/ListResourcesResult/resources-list-with-cursor-and-ttl.json)
- [schema/draft/examples/ListResourcesResultResponse/list-resources-result-response.json](schema/draft/examples/ListResourcesResultResponse/list-resources-result-response.json)
- [schema/draft/examples/ListToolsResult/tools-list-with-cursor-and-ttl.json](schema/draft/examples/ListToolsResult/tools-list-with-cursor-and-ttl.json)
- [schema/draft/examples/ListToolsResultResponse/list-tools-result-response.json](schema/draft/examples/ListToolsResultResponse/list-tools-result-response.json)
- [schema/draft/examples/Tool/tool-with-array-output-schema.json](schema/draft/examples/Tool/tool-with-array-output-schema.json)
- [schema/draft/examples/Tool/tool-with-composition-input-schema.json](schema/draft/examples/Tool/tool-with-composition-input-schema.json)
- [seps/2106-json-schema-2020-12.md](seps/2106-json-schema-2020-12.md)

</details>



This document details the various features and capabilities that Model Context Protocol (MCP) servers can implement. These features enable servers to provide rich contextual information and interactive functionalities to MCP clients. For information on client-side capabilities, see [Client Features](#2.6). For an overview of the core protocol, see [Architecture and Core Concepts](#2.1).

## Overview of Server Capabilities

MCP servers declare their supported features during the [Connection Lifecycle and Capabilities](#2.4) initialization phase. This negotiation ensures that both the client and server operate within a mutually understood set of functionalities.

The primary server features include:

*   **Tools**: Model-controlled executable functions.
*   **Resources**: Application-driven URI-addressable data.
*   **Prompts**: User-controlled structured message templates.
*   **Logging**: Structured observability and debugging.
*   **Completion**: Interactive argument autocompletion.
*   **Caching**: Performance optimization via TTL and scope hints.

The following diagram illustrates the relationship between these server features and the core protocol layer:

### MCP Server Architecture Diagram
```mermaid
graph TD
    subgraph "MCP_Protocol_Layer"
        LIFECYCLE["Connection Lifecycle (initialize, initialized)"]
        JSONRPC["JSON-RPC 2.0 Message System"]
    end

    subgraph "Server_Features"
        TOOLS["Tools System (tools/list, tools/call)"]
        RESOURCES["Resources System (resources/list, resources/read, resources/templates/list)"]
        PROMPTS["Prompts System (prompts/list, prompts/get)"]
        LOGGING["Logging (notifications/message)"]
        COMPLETION["Completion (completion/complete)"]
        CACHING["Caching (ttlMs, cacheScope)"]
    end

    LIFECYCLE --> JSONRPC
    JSONRPC --> TOOLS
    JSONRPC --> RESOURCES
    JSONRPC --> PROMPTS
    JSONRPC --> LOGGING
    JSONRPC --> COMPLETION
    JSONRPC --> CACHING
```
Sources: [docs/specification/draft/server/tools.mdx:7-10](), [docs/specification/draft/server/resources.mdx:7-11](), [docs/specification/draft/server/prompts.mdx:7-10](), [docs/specification/draft/server/utilities/caching.mdx:7-9]()

## Tools System

The Tools system allows MCP servers to expose executable functions that can be invoked by language models. Each tool is uniquely identified by a name and includes metadata describing its schema.

### User Interaction Model
Tools are designed to be **model-controlled**, meaning the LLM discovers and invokes them automatically based on context [docs/specification/draft/server/tools.mdx:22-24](). For security, applications **SHOULD** provide a human-in-the-loop interface to confirm tool invocations [docs/specification/draft/server/tools.mdx:32-40]().

### Capabilities
Servers supporting tools **MUST** declare the `tools` capability [docs/specification/draft/server/tools.mdx:46-51]().
*   `listChanged`: Indicates the server will emit `notifications/tools/list_changed` when tools change [docs/specification/draft/server/tools.mdx:58-59]().

### Protocol Messages
*   **Listing Tools**: Clients send `tools/list` to discover tools [docs/specification/draft/server/tools.mdx:79-81]().
*   **Calling Tools**: Clients send `tools/call` with `name` and `arguments` [docs/specification/draft/server/tools.mdx:136-152]().
*   **Input Required**: Servers may respond with `InputRequiredResult` if more info is needed before completion [docs/specification/draft/server/tools.mdx:173-175](). This follows the Multi Round-Trip Request (MRTR) pattern [docs/specification/draft/server/tools.mdx:176-180]().

### Tool Annotations (Risk Vocabulary)
Tool annotations provide hints about operational risk [blog/content/posts/2026-03-16-tool-annotations.md:11-15]():
*   `readOnlyHint`: Does the tool modify the environment? [blog/content/posts/2026-03-16-tool-annotations.md:31]()
*   `destructiveHint`: Is the modification destructive? [blog/content/posts/2026-03-16-tool-annotations.md:32]()
*   `idempotentHint`: Can it be safely called again with the same args? [blog/content/posts/2026-03-16-tool-annotations.md:33]()
*   `openWorldHint`: Does it interact with external entities? [blog/content/posts/2026-03-16-tool-annotations.md:34]()

Sources: [docs/specification/draft/server/tools.mdx:7-60](), [blog/content/posts/2026-03-16-tool-annotations.md:15-35]()

## Resources System

Resources allow servers to share data like files or database schemas via URIs [docs/specification/draft/server/resources.mdx:7-11]().

### User Interaction Model
Resources are **application-driven**. The host application determines how to present them (e.g., a resource picker) [docs/specification/draft/server/resources.mdx:23-32]().

### Capabilities
Servers **MUST** declare the `resources` capability [docs/specification/draft/server/resources.mdx:40-51]().
*   `subscribe`: Supports resource-specific update notifications [docs/specification/draft/server/resources.mdx:57-59]().
*   `listChanged`: Emits notifications when the set of available resources changes [docs/specification/draft/server/resources.mdx:55-57]().

### Protocol Messages
*   **Listing**: `resources/list` returns available resources [docs/specification/draft/server/resources.mdx:86-103]().
*   **Reading**: `resources/read` retrieves contents [docs/specification/draft/server/resources.mdx:135-152]().
*   **Templates**: `resources/templates/list` allows parameterized URI templates [docs/specification/draft/server/resources.mdx:180-185]().

Sources: [docs/specification/draft/server/resources.mdx:7-71]()

## Prompts System

Prompts provide structured templates for LLM instructions [docs/specification/draft/server/prompts.mdx:7-10]().

### User Interaction Model
Prompts are **user-controlled**, typically triggered by user-initiated commands like slash commands in a UI [docs/specification/draft/server/prompts.mdx:22-32]().

### Capabilities
Servers **MUST** declare the `prompts` capability [docs/specification/draft/server/prompts.mdx:40-51]().

### Protocol Messages
*   **Listing**: `prompts/list` retrieves available templates [docs/specification/draft/server/prompts.mdx:69-83]().
*   **Getting**: `prompts/get` resolves a template with provided arguments [docs/specification/draft/server/prompts.mdx:123-140]().

Sources: [docs/specification/draft/server/prompts.mdx:7-162]()

## Caching and Performance

MCP supports time-based caching for list operations and resource reads to reduce re-fetching [docs/specification/draft/server/utilities/caching.mdx:7-9]().

### Cacheable Model
Servers include caching hints in results with `resultType: "complete"` [docs/specification/draft/server/utilities/caching.mdx:13-14]():
*   `ttlMs`: Milliseconds the result is considered fresh (analogous to HTTP `max-age`) [docs/specification/draft/server/utilities/caching.mdx:48-50]().
*   `cacheScope`: Either `"public"` (sharable) or `"private"` (user-specific/auth-bound) [docs/specification/draft/server/utilities/caching.mdx:95-102]().

### Caching Logic Flow
```mermaid
sequenceDiagram
    participant C["Client (CacheManager)"]
    participant S["Server"]

    C->>S: tools/list
    S-->>C: { tools: [...], ttlMs: 300000, cacheScope: "public" }
    Note over C: Store in Cache (t_received)
    
    Note over C: 2 mins later: now < t_received + ttlMs
    C->>C: Use Cached Data
    
    Note over S: Tools Change
    S->>C: notifications/tools/list_changed
    Note over C: Invalidate Cache Immediately
```
Sources: [docs/specification/draft/server/utilities/caching.mdx:124-145]()

## Utilities: Logging and Completion

### Logging
The logging feature allows servers to send structured logs to the client for observability [docs/specification/draft/server/utilities/logging.mdx:20-23]().
*   **Note**: In the latest draft, standard output streams (stderr) are often preferred for simple logging, while the protocol supports structured `notifications/message` [docs/specification/draft/server/utilities/logging.mdx:25-30]().
*   **Levels**: Follows syslog severity (debug, info, error, etc.) [docs/specification/draft/server/utilities/logging.mdx:44-56]().

### Completion
Servers provide autocompletion for prompt and resource template arguments [docs/specification/draft/server/utilities/completion.mdx:7-10]().
*   **Method**: `completion/complete` [docs/specification/draft/server/utilities/completion.mdx:48-57]().
*   **Ref Types**: `ref/prompt` or `ref/resource` [docs/specification/draft/server/utilities/completion.mdx:134-140]().

Sources: [docs/specification/draft/server/utilities/completion.mdx:7-140]()

## Pagination

Large result sets are handled via opaque cursor-based pagination [docs/specification/draft/server/utilities/pagination.mdx:7-9]().

### Pagination Flow
1.  **Initial Request**: Client calls a list method without a cursor [docs/specification/draft/server/utilities/pagination.mdx:76]().
2.  **Response**: Server returns a page and a `nextCursor` [docs/specification/draft/server/utilities/pagination.mdx:33-37]().
3.  **Continuation**: Client requests again with the `cursor` parameter [docs/specification/draft/server/utilities/pagination.mdx:54-66]().

Sources: [docs/specification/draft/server/utilities/pagination.mdx:7-107]()

---

# Page: Client Features

# Client Features

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/specification/draft/client/roots.mdx](docs/specification/draft/client/roots.mdx)
- [docs/specification/draft/client/sampling.mdx](docs/specification/draft/client/sampling.mdx)
- [docs/specification/draft/server/utilities/logging.mdx](docs/specification/draft/server/utilities/logging.mdx)
- [schema/draft/examples/ClientCapabilities/sampling-minimum-baseline-support.json](schema/draft/examples/ClientCapabilities/sampling-minimum-baseline-support.json)
- [schema/draft/examples/ClientCapabilities/sampling-tool-use-support.json](schema/draft/examples/ClientCapabilities/sampling-tool-use-support.json)
- [schema/draft/examples/CreateMessageRequest/sampling-request.json](schema/draft/examples/CreateMessageRequest/sampling-request.json)
- [schema/draft/examples/CreateMessageRequestParams/basic-request.json](schema/draft/examples/CreateMessageRequestParams/basic-request.json)
- [schema/draft/examples/CreateMessageRequestParams/follow-up-with-tool-results.json](schema/draft/examples/CreateMessageRequestParams/follow-up-with-tool-results.json)
- [schema/draft/examples/CreateMessageRequestParams/request-with-tools.json](schema/draft/examples/CreateMessageRequestParams/request-with-tools.json)
- [schema/draft/examples/CreateMessageResult/final-response.json](schema/draft/examples/CreateMessageResult/final-response.json)
- [schema/draft/examples/CreateMessageResult/text-response.json](schema/draft/examples/CreateMessageResult/text-response.json)
- [schema/draft/examples/CreateMessageResult/tool-use-response.json](schema/draft/examples/CreateMessageResult/tool-use-response.json)
- [schema/draft/examples/ElicitRequest/elicitation-request.json](schema/draft/examples/ElicitRequest/elicitation-request.json)
- [schema/draft/examples/InputRequests/elicitation-and-sampling-input-requests.json](schema/draft/examples/InputRequests/elicitation-and-sampling-input-requests.json)
- [schema/draft/examples/InputResponses/elicitation-and-sampling-input-responses.json](schema/draft/examples/InputResponses/elicitation-and-sampling-input-responses.json)
- [schema/draft/examples/ModelPreferences/with-hints-and-priorities.json](schema/draft/examples/ModelPreferences/with-hints-and-priorities.json)
- [seps/1577--sampling-with-tools.md](seps/1577--sampling-with-tools.md)

</details>



## Purpose and Scope

This document covers the capabilities that MCP **clients** expose to **servers**, enabling servers to request operations that require client resources or user interaction. These features are distinct from server features ([Server Features](#2.5)), which servers expose to clients.

Client features include:
- **Sampling**: LLM completions/generations requested by servers (Deprecated in 2026-07-28).
- **Elicitation**: User input collection through forms or external URLs.
- **Roots**: Filesystem boundary declarations for context scoping (Deprecated in 2026-07-28).
- **Logging**: Server log message routing to client handlers (Deprecated in 2026-07-28).

In the protocol version `2026-07-28`, the interaction model has shifted from server-initiated requests to the **Multi Round-Trip Requests (MRTR)** pattern.

Sources: [docs/specification/draft/client/sampling.mdx:1-37](), [docs/specification/draft/client/roots.mdx:1-24](), [docs/specification/draft/server/utilities/logging.mdx:20-24]()

## Client Capability Declaration

In the stateless `2026-07-28` protocol, clients no longer declare capabilities once during initialization. Instead, capabilities are declared **per-request** within the `_meta` object. Servers MUST NOT infer capabilities from prior requests.

### ClientCapabilities Structure

```mermaid
graph TB
    RequestMeta["RequestMetaObject (_meta)"]
    ClientCaps["io.modelcontextprotocol/clientCapabilities"]
    
    Sampling["sampling<br/>{context?, tools?}"]
    Elicitation["elicitation<br/>{form?, url?}"]
    Roots["roots"]
    
    RequestMeta --> ClientCaps
    ClientCaps --> Sampling
    ClientCaps --> Elicitation
    ClientCaps --> Roots
    
    SamplingContext["context: {}<br/>(Deprecated)"]
    SamplingTools["tools: {}<br/>Supports tool use in sampling"]
    
    Sampling --> SamplingContext
    Sampling --> SamplingTools
    
    ElicitForm["form: {}<br/>Supports form-based elicitation"]
    ElicitURL["url: {}<br/>Supports URL-based elicitation"]
    
    Elicitation --> ElicitForm
    Elicitation --> ElicitURL
```

Sources: [docs/specification/draft/client/sampling.mdx:54-97](), [docs/specification/draft/client/roots.mdx:38-51](), [schema/draft/examples/ClientCapabilities/sampling-minimum-baseline-support.json:1-3]()

## Multi Round-Trip Requests (MRTR) Pattern

The MRTR pattern replaces server-initiated requests for client features. Instead of a server calling a client method like `sampling/createMessage`, the server returns an `InputRequiredResult`.

### MRTR Data Flow

```mermaid
sequenceDiagram
    participant Client
    participant Server
    participant User

    Client->>Server: Request (e.g., tools/call)
    Note over Server: Server needs user input
    Server-->>Client: Response (resultType: "input_required")<br/>{ inputRequests: [elicitation/create] }
    
    Note over Client,User: Client processes inputRequests
    Client->>User: Show Form/Prompt
    User-->>Client: Provide Input
    
    Client->>Server: Retry original Request<br/>{ inputResponses: [...], requestState: "..." }
    Server-->>Client: Final Response (resultType: "complete")
```

Sources: [docs/specification/draft/client/sampling.mdx:113-117](), [docs/specification/draft/client/roots.mdx:55-60](), [docs/specification/draft/client/sampling.mdx:168-207]()

## Sampling (Deprecated)

Sampling allows servers to request LLM generations via the client. It is **deprecated** as of version `2026-07-28`. Existing implementations should migrate to direct LLM provider integrations.

### Sampling with Tools Flow (MRTR)

Servers include a `sampling/createMessage` request inside the `inputRequests` field of an `InputRequiredResult`.

```mermaid
sequenceDiagram
    participant Server
    participant Client
    participant LLM

    Client->>Server: tools/call
    Server-->>Client: InputRequiredResult(sampling/createMessage)
    
    Note over Client: User Approval
    Client->>LLM: Generate
    LLM-->>Client: Tool Use Request (stopReason: "toolUse")
    
    Client->>Server: Retry tools/call (inputResponses: [tool_use])
    Note over Server: Execute Tool
    Server-->>Client: InputRequiredResult(sampling/createMessage + tool_results)
    
    Client->>LLM: Generate final
    LLM-->>Client: Text Response (stopReason: "endTurn")
    Client->>Server: Retry tools/call (inputResponses: [final_text])
    Server-->>Client: Result("complete")
```

Sources: [docs/specification/draft/client/sampling.mdx:7-17](), [docs/specification/draft/client/sampling.mdx:168-207](), [seps/1577--sampling-with-tools.md:58-71]()

### Key Data Structures

| Type | Description | File |
| :--- | :--- | :--- |
| `SamplingMessage` | Represents a message in the conversation history (role: user/assistant). | [docs/specification/draft/client/sampling.mdx:123-131]() |
| `ModelPreferences` | Hints for model selection (intelligence vs. speed vs. cost). | [docs/specification/draft/client/sampling.mdx:132-141]() |
| `CreateMessageResult` | The LLM response including `content`, `model`, and `stopReason`. | [docs/specification/draft/client/sampling.mdx:152-162]() |

## Elicitation

Elicitation allows servers to gather data from users. It is the primary mechanism for interactive workflows.

### Form Mode
Used for non-sensitive structured data. The client renders a UI based on a provided JSON schema.

**Example Request:**
```json
{
  "method": "elicitation/create",
  "params": {
    "mode": "form",
    "message": "Please provide your GitHub username",
    "requestedSchema": {
      "type": "object",
      "properties": {
        "name": { "type": "string" }
      },
      "required": ["name"]
    }
  }
}
```

Sources: [schema/draft/examples/ElicitRequest/elicitation-request.json:1-19](), [schema/draft/examples/InputRequests/elicitation-and-sampling-input-requests.json:1-17]()

## Roots (Deprecated)

Roots provide informational guidance to servers about relevant filesystem directories. This feature is **deprecated** as of version `2026-07-28`.

**Migration Path:** Servers should receive directory paths via tool parameters or server configuration instead of querying `roots/list`.

### Data Structure: Root
- `uri`: Must be a `file://` URI.
- `name`: Optional human-readable name.

Sources: [docs/specification/draft/client/roots.mdx:7-17](), [docs/specification/draft/client/roots.mdx:96-102]()

## Logging (Deprecated)

The global `logging/setLevel` method is **deprecated**.

**New Pattern:**
- Log levels are set **per-request** via `_meta["io.modelcontextprotocol/logLevel"]`.
- Servers MUST NOT emit `notifications/message` unless the request opted in via `_meta`.
- Notifications are request-scoped and delivered on the response stream of the associated request.

Sources: [docs/specification/draft/server/utilities/logging.mdx:7-18](), [docs/specification/draft/server/utilities/logging.mdx:60-73]()

## Security and Approval

1. **Human-in-the-Loop**: Clients SHOULD always require user approval for sampling and elicitation requests. [docs/specification/draft/client/sampling.mdx:35-46]()
2. **Permission Scoping**: Roots are informational guidance, not an access-control mechanism. [docs/specification/draft/client/roots.mdx:22-24]()
3. **Sensitive Data**: Log messages MUST NOT contain credentials or PII. [docs/specification/draft/server/utilities/logging.mdx:123-127]()

Sources: [docs/specification/draft/client/sampling.mdx:35-46](), [docs/specification/draft/client/roots.mdx:22-24](), [docs/specification/draft/server/utilities/logging.mdx:123-127]()

---

# Page: Task System and Async Operations

# Task System and Async Operations

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [blog/content/posts/2026-01-26-mcp-apps.md](blog/content/posts/2026-01-26-mcp-apps.md)
- [docs/community/sdk-tiers.mdx](docs/community/sdk-tiers.mdx)
- [docs/docs.json](docs/docs.json)
- [docs/docs/getting-started/intro.mdx](docs/docs/getting-started/intro.mdx)
- [docs/docs/tools/debugging.mdx](docs/docs/tools/debugging.mdx)
- [docs/extensions/apps/build.mdx](docs/extensions/apps/build.mdx)
- [docs/extensions/apps/overview.mdx](docs/extensions/apps/overview.mdx)
- [docs/extensions/auth/oauth-client-credentials.mdx](docs/extensions/auth/oauth-client-credentials.mdx)
- [docs/extensions/auth/overview.mdx](docs/extensions/auth/overview.mdx)
- [docs/extensions/client-matrix.mdx](docs/extensions/client-matrix.mdx)
- [docs/extensions/overview.mdx](docs/extensions/overview.mdx)
- [docs/extensions/tasks/overview.mdx](docs/extensions/tasks/overview.mdx)
- [docs/seps/2260-Require-Server-requests-to-be-associated-with-Client-requests.mdx](docs/seps/2260-Require-Server-requests-to-be-associated-with-Client-requests.mdx)
- [docs/seps/2322-MRTR.mdx](docs/seps/2322-MRTR.mdx)
- [docs/seps/2663-tasks-extension.mdx](docs/seps/2663-tasks-extension.mdx)
- [docs/seps/index.mdx](docs/seps/index.mdx)
- [docs/specification/draft/basic/patterns/cancellation.mdx](docs/specification/draft/basic/patterns/cancellation.mdx)
- [docs/specification/draft/basic/patterns/progress.mdx](docs/specification/draft/basic/patterns/progress.mdx)
- [docs/specification/draft/basic/patterns/subscriptions.mdx](docs/specification/draft/basic/patterns/subscriptions.mdx)
- [seps/1024-mcp-client-security-requirements-for-local-server-.md](seps/1024-mcp-client-security-requirements-for-local-server-.md)
- [seps/1034--support-default-values-for-all-primitive-types-in.md](seps/1034--support-default-values-for-all-primitive-types-in.md)
- [seps/1036-url-mode-elicitation-for-secure-out-of-band-intera.md](seps/1036-url-mode-elicitation-for-secure-out-of-band-intera.md)
- [seps/1303-input-validation-errors-as-tool-execution-errors.md](seps/1303-input-validation-errors-as-tool-execution-errors.md)
- [seps/1613-establish-json-schema-2020-12-as-default-dialect-f.md](seps/1613-establish-json-schema-2020-12-as-default-dialect-f.md)
- [seps/1686-tasks.md](seps/1686-tasks.md)
- [seps/1699-support-sse-polling-via-server-side-disconnect.md](seps/1699-support-sse-polling-via-server-side-disconnect.md)
- [seps/1730-sdks-tiering-system.md](seps/1730-sdks-tiering-system.md)
- [seps/2260-Require-Server-requests-to-be-associated-with-Client-requests.md](seps/2260-Require-Server-requests-to-be-associated-with-Client-requests.md)
- [seps/2322-MRTR.md](seps/2322-MRTR.md)
- [seps/2663-tasks-extension.md](seps/2663-tasks-extension.md)
- [seps/991-enable-url-based-client-registration-using-oauth-c.md](seps/991-enable-url-based-client-registration-using-oauth-c.md)

</details>



This page documents the MCP task system, which enables asynchronous, long-running operations through a polling-based workflow model. Tasks were originally introduced as an experimental feature in version 2025-11-25 and have been redesigned as an official extension in **SEP-2663** (`io.modelcontextprotocol/tasks`) to improve handshake reliability and remove blocking connection traps.

For information about synchronous request/response patterns, see the JSON-RPC message system documentation ([2.2]()). For multi-round-trip interactions that don't require durable polling, see the **MRTR (SEP-2322)** pattern ([2.7.4](#multi-round-trip-requests-mrtr)).

## Overview

The task system provides a standardized mechanism for representing expensive computations, batch processing, and operations that require user interaction mid-execution. Unlike standard JSON-RPC requests that block until completion, task-augmented requests allow the receiver to immediately return a **task handle** (a durable state machine), which the requestor then uses to poll for progress or retrieve final results.

Key improvements in the Task Extension (SEP-2663) include:
- **Stateless Handshake**: Moves from complex tool-level negotiation to a single extension capability declaration.
- **Non-Blocking Lifecycle**: Replaces the blocking `tasks/result` with a polling-based `tasks/get` and `tasks/update` flow.
- **Server-Directed Creation**: Servers can decide to return a task even if the client didn't explicitly request one, provided the client supports the extension.

**Sources:** [seps/2663-tasks-extension.md:11-37](), [docs/seps/2663-tasks-extension.mdx:29-54]()

## Architecture

### Task State Machine

```mermaid
stateDiagram-v2
    [*] --> "working" : "Request Received"
    
    "working" --> "input_required" : "Server needs info"
    "working" --> "completed" : "Success"
    "working" --> "failed" : "Error"
    "working" --> "cancelled" : "tasks/cancel"
    
    "input_required" --> "working" : "tasks/update (Result)"
    "input_required" --> "completed" : "Success"
    "input_required" --> "failed" : "Error"
    "input_required" --> "cancelled" : "tasks/cancel"
    
    "completed" --> [*]
    "failed" --> [*]
    "cancelled" --> [*]

    note right of "input_required"
        "Client retrieves nested request"
        "via tasks/get and provides"
        "response via tasks/update"
    end note
```

Tasks are durable state machines identified by a server-generated `taskId`. The `Task` object tracks the lifecycle and carries any pending server-to-client requests (like elicitation or sampling).

**Sources:** [seps/2663-tasks-extension.md:41-44](), [seps/2663-tasks-extension.md:402-431]()

## Capability Negotiation

Support for tasks is negotiated during the initialization handshake using the extension identifier `io.modelcontextprotocol/tasks`.

### Client Capability
The client signals support in its per-request capabilities:
```jsonc
{
  "method": "initialize",
  "params": {
    "capabilities": {
      "extensions": {
        "io.modelcontextprotocol/tasks": {}
      }
    }
  }
}
```

### Server Capability
The server declares support for specific task methods:
```jsonc
{
  "capabilities": {
    "extensions": {
      "io.modelcontextprotocol/tasks": {
        "methods": ["tasks/get", "tasks/update", "tasks/cancel"]
      }
    }
  }
}
```

**Sources:** [seps/2663-tasks-extension.md:51-80](), [docs/extensions/client-matrix.mdx:26-31]()

## Task Lifecycle Operations

### 1. Task Creation
When a client calls a tool (e.g., `tools/call`), a task-supporting server may return a `task` result type instead of a final result.

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "resultType": "task",
    "task": {
      "taskId": "task-uuid-123",
      "status": "working",
      "pollInterval": 5000
    }
  }
}
```

### 2. Polling and Retrieval (`tasks/get`)
The client polls the server to check status. The response contains the `Task` object. If the task is `completed`, the `result` field contains the final tool output.

```mermaid
sequenceDiagram
    participant "C" as "Client"
    participant "S" as "Server"
    
    "C"->>"S": "tools/call"
    "S"->>"C": "{ resultType: 'task', taskId: '123' }"
    
    loop "Polling"
        "C"->>"S": "tasks/get (taskId: '123')"
        "S"->>"C": "{ status: 'working' }"
    end
    
    "C"->>"S": "tasks/get (taskId: '123')"
    "S"->>"C": "{ status: 'completed', result: { content: [...] } }"
```

**Sources:** [seps/2663-tasks-extension.md:184-228](), [seps/2663-tasks-extension.md:463-476]()

### 3. Handling Input (`input_required`)
If a task reaches the `input_required` state, the `Task` object includes a `request` field containing a server-to-client request (e.g., `sampling/createMessage`). The client resolves this and sends the result back via `tasks/update`.

```mermaid
sequenceDiagram
    participant "C" as "Client"
    participant "S" as "Server"
    
    "C"->>"S": "tasks/get (taskId: '123')"
    "S"->>"C": "{ status: 'input_required', request: { method: 'sampling/createMessage', ... } }"
    
    Note over "C": "Client processes sampling"
    
    "C"->>"S": "tasks/update (taskId: '123', result: { ... })"
    "S"->>"C": "{ status: 'working' }"
```

**Sources:** [seps/2663-tasks-extension.md:434-453](), [seps/2663-tasks-extension.md:470-476]()

### 4. Cancellation (`tasks/cancel`)
Clients can explicitly terminate a task. Terminal tasks (completed/failed) cannot be cancelled.

**Sources:** [seps/2663-tasks-extension.md:354-386]()

## Multi Round-Trip Requests (MRTR)

**SEP-2322** introduces the MRTR pattern to handle server-initiated requests (Elicitation, Sampling) without requiring persistent SSE streams or complex server-side state shared across instances.

### MRTR vs. Tasks
- **Tasks**: For durable, long-running background jobs that survive connection drops. Requires polling.
- **MRTR**: For interactive, nested requests (like "I need a password to run this tool"). The server returns an intermediate "request" response, and the client "continues" the original call by sending the answer.

### MRTR Flow
```mermaid
sequenceDiagram
    participant "C" as "Client"
    participant "S" as "Server Instance A"
    participant "S2" as "Server Instance B"
    
    "C"->>"S": "tools/call (Initial)"
    "S"-->>"C": "elicitation/create (As intermediate response)"
    
    Note over "C": "User provides input"
    
    "C"->>"S2": "tools/call (Continue with state handle)"
    "S2"->>"C": "Final Tool Result"
```

MRTR enables **stateless scaling** by allowing any server instance to resume a request if the client provides the necessary state handle returned in the intermediate step.

**Sources:** [seps/2322-MRTR.md:13-27](), [seps/2322-MRTR.md:77-100](), [docs/seps/2322-MRTR.mdx:29-46]()

## Implementation Requirements

### Request Association
Per **SEP-2260**, all server-to-client requests (Sampling, Elicitation, Roots) **MUST** be associated with an originating client request. In the task system, this is enforced by embedding these requests within the `Task` object retrieved via `tasks/get`.

**Sources:** [seps/2260-Require-Server-requests-to-be-associated-with-Client-requests.md:12-21](), [seps/2663-tasks-extension.md:19-23]()

### Error Handling
| Code | Meaning |
|------|---------|
| `-32602` | Invalid Params: Attempting to cancel a terminal task. |
| `-32001` | Task Not Found: The provided `taskId` does not exist or has expired. |

**Sources:** [seps/2663-tasks-extension.md:494-501]()

### Time-To-Live (TTL)
Servers should implement TTL for task results to prevent memory exhaustion. The `Task` object includes `createdAt` and `lastUpdatedAt` timestamps to allow clients to track expiration.

**Sources:** [seps/2663-tasks-extension.md:454-462]()

---

# Page: Extensions Framework

# Extensions Framework

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [blog/content/posts/2026-01-26-mcp-apps.md](blog/content/posts/2026-01-26-mcp-apps.md)
- [blog/content/posts/2026-03-11-understanding-mcp-extensions.md](blog/content/posts/2026-03-11-understanding-mcp-extensions.md)
- [docs/community/sdk-tiers.mdx](docs/community/sdk-tiers.mdx)
- [docs/docs/getting-started/intro.mdx](docs/docs/getting-started/intro.mdx)
- [docs/docs/tools/debugging.mdx](docs/docs/tools/debugging.mdx)
- [docs/extensions/apps/build.mdx](docs/extensions/apps/build.mdx)
- [docs/extensions/apps/overview.mdx](docs/extensions/apps/overview.mdx)
- [docs/extensions/auth/oauth-client-credentials.mdx](docs/extensions/auth/oauth-client-credentials.mdx)
- [docs/extensions/auth/overview.mdx](docs/extensions/auth/overview.mdx)
- [docs/extensions/client-matrix.mdx](docs/extensions/client-matrix.mdx)
- [docs/extensions/overview.mdx](docs/extensions/overview.mdx)
- [docs/extensions/tasks/overview.mdx](docs/extensions/tasks/overview.mdx)
- [schema/draft/examples/ClientCapabilities/extensions-ui-mime-types.json](schema/draft/examples/ClientCapabilities/extensions-ui-mime-types.json)
- [schema/draft/examples/ClientCapabilities/sampling-context-inclusion-support-deprecated.json](schema/draft/examples/ClientCapabilities/sampling-context-inclusion-support-deprecated.json)
- [seps/2133-extensions.md](seps/2133-extensions.md)

</details>



## Purpose and Scope

The Extensions Framework (SEP-2133) provides a standardized mechanism for extending the Model Context Protocol (MCP) with optional, composable capabilities beyond the core protocol [seps/2133-extensions.md:1-12](). This framework enables the ecosystem to evolve and experiment—through features like interactive UIs or specialized authorization—without forcing adoption across all implementations or compromising core protocol stability [seps/2133-extensions.md:12-15]().

## Extension Identification and Naming

Extensions are identified by a unique **Extension Identifier** using the format `{vendor-prefix}/{extension-name}` [seps/2133-extensions.md:23-27]().

*   **Vendor Prefixes**: To prevent collisions, prefixes SHOULD be a reversed domain name owned by the author (e.g., `com.example/`) [seps/2133-extensions.md:28-29]().
*   **Official Prefix**: Official extensions maintained by the MCP organization use the `io.modelcontextprotocol/` prefix [seps/2133-extensions.md:38-39]().
*   **Breaking Changes**: Any modification that causes existing implementations to fail (removing fields, changing types, altering semantics) MUST use a new identifier, such as `io.modelcontextprotocol/auth-v2` [seps/2133-extensions.md:30-31]().

Sources: [seps/2133-extensions.md:23-31]()

## Extension Types and Governance

The framework classifies extensions into three categories based on their maturity and maintenance [seps/2133-extensions.md:34-35]().

| Type | Prefix | Repository Pattern | Governance |
| :--- | :--- | :--- | :--- |
| **Official** | `io.modelcontextprotocol/` | `ext-{category}` | MCP Core Maintainers & Appointed Repository Maintainers [seps/2133-extensions.md:38-43]() |
| **Experimental** | `io.modelcontextprotocol/` | `experimental-ext-{name}` | Working Groups (WGs) or Interest Groups (IGs) [seps/2133-extensions.md:56-59]() |
| **Unofficial** | `vendor-specific/` | External | Independent developers [seps/2133-extensions.md:34-35]() |

### Incubation and Graduation
Experimental extensions serve as an incubation pathway for WGs/IGs to prototype ideas before formal SEP submission [seps/2133-extensions.md:53-55](). To graduate to **Official** status, an extension must pass through the **Extensions Track** of the SEP process, requiring at least one reference implementation in an official SDK [docs/extensions/overview.mdx:72-84]().

Sources: [seps/2133-extensions.md:34-64](), [docs/extensions/overview.mdx:60-75]()

## Capability Negotiation

Extensions are opt-in and negotiated during the `initialize` handshake [docs/extensions/client-matrix.mdx:16-17](). Clients and servers advertise support via the `extensions` field within their respective capabilities [docs/extensions/overview.mdx:114-116]().

### Negotiation Flow
The following diagram illustrates how the `initialize` method facilitates extension discovery between `McpClient` and `McpServer`.

```mermaid
sequenceDiagram
    participant C as "McpClient"
    participant S as "McpServer"
    
    Note over C,S: "Initialization Handshake"
    C->>S: "initialize(capabilities: { extensions: { 'io.modelcontextprotocol/ui': {} } })"
    Note right of S: "Server checks if it supports requested extensions"
    S-->>C: "result(capabilities: { extensions: { 'io.modelcontextprotocol/ui': { 'mimeTypes': [...] } } })"
    
    alt "Both Support Extension"
        Note over C,S: "Extension Enabled"
        C->>S: "ui/initialize (Extension-specific method)"
    else "Missing Support"
        Note over C,S: "Graceful Degradation"
        C->>S: "tools/call (Standard MCP method)"
    end
```
Sources: [docs/extensions/overview.mdx:114-135](), [docs/extensions/apps/overview.mdx:71-76]()

## Official Extensions

### 1. MCP Apps (`io.modelcontextprotocol/ui`)
MCP Apps allow servers to return interactive HTML interfaces (dashboards, forms) that render in sandboxed iframes within the client [blog/content/posts/2026-01-26-mcp-apps.md:15-18]().
*   **Mechanism**: Tools include a `_meta.ui.resourceUri` pointing to a `ui://` scheme resource [blog/content/posts/2026-01-26-mcp-apps.md:62-68]().
*   **Communication**: The app communicates with the host via JSON-RPC over `postMessage` [blog/content/posts/2026-01-26-mcp-apps.md:83-84]().
*   **Library**: Developers use `@modelcontextprotocol/ext-apps` which provides the `App` class [blog/content/posts/2026-01-26-mcp-apps.md:104-111]().

### 2. MCP Tasks (`io.modelcontextprotocol/tasks`)
Designed for long-running operations (CI pipelines, human approvals) that exceed standard timeout limits [docs/extensions/tasks/overview.mdx:17-21]().
*   **Durable Handles**: Servers return a `taskId` with status `working` instead of blocking [docs/extensions/tasks/overview.mdx:54-57]().
*   **Polling & Updates**: Clients use `tasks/get` to check status and `tasks/update` to provide mid-flight input when status is `input_required` [docs/extensions/tasks/overview.mdx:59-65]().

### 3. Authorization Extensions
Managed in the `ext-auth` repository, these supplement core OAuth 2.1 features [docs/extensions/overview.mdx:24-31]().
*   **OAuth Client Credentials**: For machine-to-machine (M2M) auth without user login [docs/extensions/client-matrix.mdx:29]().
*   **Enterprise-Managed Authorization**: Centralized access control via enterprise Identity Providers (IdP) [docs/extensions/client-matrix.mdx:30]().

Sources: [blog/content/posts/2026-01-26-mcp-apps.md:15-111](), [docs/extensions/tasks/overview.mdx:17-65](), [docs/extensions/client-matrix.mdx:26-31]()

## Technical Implementation and Data Flow

The following diagram maps the Natural Language concepts of "UI Resources" and "Task Polling" to the code entities and URI schemes used in the implementation.

```mermaid
graph TD
    subgraph "Extension_Resource_Space"
        UI_URI["ui:// URI Scheme"]
        TASK_ID["taskId (Durable Handle)"]
    end

    subgraph "Code_Entities"
        APP_CLASS["App Class (@modelcontextprotocol/ext-apps)"]
        UI_META["_meta.ui.resourceUri"]
        CREATE_TASK["CreateTaskResult"]
        TASK_GET["tasks/get method"]
    end

    subgraph "Transport_and_Security"
        POST_MSG["postMessage (JSON-RPC)"]
        IFRAME["Sandboxed Iframe"]
    end

    UI_URI -->|referenced_by| UI_META
    UI_META -->|loads_into| IFRAME
    APP_CLASS -->|communicates_via| POST_MSG
    POST_MSG -->|inside| IFRAME

    TASK_ID -->|returned_in| CREATE_TASK
    CREATE_TASK -->|queried_by| TASK_GET
```
Sources: [blog/content/posts/2026-01-26-mcp-apps.md:62-84](), [docs/extensions/tasks/overview.mdx:54-65](), [docs/extensions/apps/overview.mdx:39-49]()

## Graceful Degradation
Extensions are optional. Servers SHOULD provide text-only fallbacks for UI-enabled tools so they can serve hosts that do not support the `io.modelcontextprotocol/ui` extension [blog/content/posts/2026-03-11-understanding-mcp-extensions.md:30-31](). If a client receives an extension-specific result type (like `CreateTaskResult`) for an extension it did not negotiate, it must treat it as an error or handle it via standard protocol fallbacks [docs/extensions/tasks/overview.mdx:40-42]().

Sources: [blog/content/posts/2026-03-11-understanding-mcp-extensions.md:30-31](), [docs/extensions/tasks/overview.mdx:40-42]()

---

# Page: Protocol Versioning and Changelog

# Protocol Versioning and Changelog

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/community/feature-lifecycle.mdx](docs/community/feature-lifecycle.mdx)
- [docs/docs/learn/versioning.mdx](docs/docs/learn/versioning.mdx)
- [docs/seps/1024-mcp-client-security-requirements-for-local-server-.mdx](docs/seps/1024-mcp-client-security-requirements-for-local-server-.mdx)
- [docs/seps/1034--support-default-values-for-all-primitive-types-in.mdx](docs/seps/1034--support-default-values-for-all-primitive-types-in.mdx)
- [docs/seps/1036-url-mode-elicitation-for-secure-out-of-band-intera.mdx](docs/seps/1036-url-mode-elicitation-for-secure-out-of-band-intera.mdx)
- [docs/seps/1046-support-oauth-client-credentials-flow-in-authoriza.mdx](docs/seps/1046-support-oauth-client-credentials-flow-in-authoriza.mdx)
- [docs/seps/1302-formalize-working-groups-and-interest-groups-in-mc.mdx](docs/seps/1302-formalize-working-groups-and-interest-groups-in-mc.mdx)
- [docs/seps/1303-input-validation-errors-as-tool-execution-errors.mdx](docs/seps/1303-input-validation-errors-as-tool-execution-errors.mdx)
- [docs/seps/1319-decouple-request-payload-from-rpc-methods-definiti.mdx](docs/seps/1319-decouple-request-payload-from-rpc-methods-definiti.mdx)
- [docs/seps/1330-elicitation-enum-schema-improvements-and-standards.mdx](docs/seps/1330-elicitation-enum-schema-improvements-and-standards.mdx)
- [docs/seps/1577--sampling-with-tools.mdx](docs/seps/1577--sampling-with-tools.mdx)
- [docs/seps/2596-spec-feature-lifecycle-and-deprecation.mdx](docs/seps/2596-spec-feature-lifecycle-and-deprecation.mdx)
- [docs/seps/991-enable-url-based-client-registration-using-oauth-c.mdx](docs/seps/991-enable-url-based-client-registration-using-oauth-c.mdx)
- [docs/spec-version-warning.js](docs/spec-version-warning.js)
- [docs/specification/draft/basic/transports/streamable-http.mdx](docs/specification/draft/basic/transports/streamable-http.mdx)
- [docs/specification/draft/basic/versioning.mdx](docs/specification/draft/basic/versioning.mdx)
- [docs/specification/draft/deprecated.mdx](docs/specification/draft/deprecated.mdx)
- [schema/2024-11-05/schema.json](schema/2024-11-05/schema.json)
- [schema/2024-11-05/schema.ts](schema/2024-11-05/schema.ts)
- [schema/2025-03-26/schema.json](schema/2025-03-26/schema.json)
- [schema/2025-03-26/schema.ts](schema/2025-03-26/schema.ts)
- [schema/2025-06-18/schema.json](schema/2025-06-18/schema.json)
- [schema/2025-06-18/schema.ts](schema/2025-06-18/schema.ts)
- [schema/draft/examples/HeaderMismatchError/header-mismatch.json](schema/draft/examples/HeaderMismatchError/header-mismatch.json)
- [schema/draft/examples/MissingRequiredClientCapabilityError/missing-elicitation-capability.json](schema/draft/examples/MissingRequiredClientCapabilityError/missing-elicitation-capability.json)
- [schema/draft/examples/UnsupportedProtocolVersionError/unsupported-version.json](schema/draft/examples/UnsupportedProtocolVersionError/unsupported-version.json)
- [seps/2596-spec-feature-lifecycle-and-deprecation.md](seps/2596-spec-feature-lifecycle-and-deprecation.md)

</details>



This document describes the Model Context Protocol's date-based versioning scheme, the transition from session-based (Legacy) to per-request (Modern) versioning, the feature lifecycle policy (Active, Deprecated, Removed), and the tracking of specification changes.

## Versioning Scheme

MCP uses string-based version identifiers in the format `YYYY-MM-DD`. This identifier indicates the last date on which **backwards-incompatible** changes were made to the protocol [docs/docs/learn/versioning.mdx:7-9]().

### Backwards Compatibility
The protocol version is **not** incremented when the specification is updated with backwards-compatible improvements [docs/docs/learn/versioning.mdx:12-14](). This allows for incremental growth—such as adding optional fields or new capabilities—while preserving interoperability between existing clients and servers [docs/docs/learn/versioning.mdx:13-15]().

### Revision States
Specification revisions exist in one of three states [docs/docs/learn/versioning.mdx:18-25]():
| State | Meaning |
| :--- | :--- |
| **Draft** | In-progress specifications; not yet ready for production consumption [docs/docs/learn/versioning.mdx:22-22](). |
| **Current** | The authoritative protocol version ready for use. It may receive compatible updates [docs/docs/learn/versioning.mdx:23-24](). |
| **Final** | Past, complete specifications that are frozen and will not be changed [docs/docs/learn/versioning.mdx:25-25](). |

The **current** protocol version is `2025-11-25` [docs/docs/learn/versioning.mdx:27-27]().

Sources: [docs/docs/learn/versioning.mdx:7-27]()

## Version Negotiation

MCP has evolved from a handshake-based negotiation to a per-request metadata-based model.

### Terminology
*   **Modern**: Versions `2026-07-28` and later. These convey version, identity, and capabilities as per-request metadata in the `_meta` field [docs/specification/draft/versioning.mdx:34-35]().
*   **Legacy**: Versions `2025-11-25` and earlier. These establish a session with an `initialize` handshake [docs/specification/draft/versioning.mdx:36-37]().
*   **Dual-era**: Implementations supporting both models [docs/specification/draft/versioning.mdx:38-39]().

### Modern Negotiation Flow (Per-Request)
In modern versions, there is no negotiation handshake. Every request declares its protocol version in its `_meta` field (or `MCP-Protocol-Version` HTTP header) [docs/specification/draft/versioning.mdx:12-13](), [docs/specification/draft/versioning.mdx:43-46]().

1.  **Client Request**: Client sends a JSON-RPC request containing `_meta.protocolVersion`.
2.  **Server Validation**: If the server does not support the version, it **MUST** respond with an `UnsupportedProtocolVersionError` (code `-32022`) [docs/specification/draft/versioning.mdx:48-52]().
3.  **Client Retry**: The error response includes a `supported` list of versions. The client should select a mutually supported version and retry [docs/specification/draft/versioning.mdx:61-71]().

### Code Entity Mapping: Modern Negotiation
The following diagram maps the per-request negotiation process to specific code entities.

```mermaid
sequenceDiagram
    participant C ["Client SDK"]
    participant S ["Server Implementation"]

    Note over C,S: Modern Per-Request Versioning

    C->>S: JSONRPCRequest { params: { _meta: { protocolVersion: "2026-07-28" } } }
    Note right of C: protocolVersion in _meta [docs/specification/draft/versioning.mdx:43-44]

    alt Server supports version
        S-->>C: JSONRPCResponse { result: ... }
    else Server mismatch
        S-->>C: UnsupportedProtocolVersionError { code: -32022, data: { supported: [...] } }
        Note left of S: Defined in [docs/specification/draft/versioning.mdx:54-67]
        C->>S: Retry with supported version
    end
```

Sources: [docs/specification/draft/versioning.mdx:7-78](), [docs/docs/learn/versioning.mdx:47-55]()

## Feature Lifecycle (SEP-2596)

Individual features (messages, capabilities, transports) follow a structured lifecycle to ensure predictable evolution and removal [docs/community/feature-lifecycle.mdx:6-10]().

### Lifecycle States
Features move through three primary states [docs/community/feature-lifecycle.mdx:24-30]():
1.  **Active**: Part of the Current specification revision.
2.  **Deprecated**: Scheduled for removal. Remained in the spec with a documented migration path [docs/community/feature-lifecycle.mdx:29-29]().
3.  **Removed**: Deleted from the `draft` specification [docs/community/feature-lifecycle.mdx:30-30]().

### Deprecation Requirements
A feature is marked as Deprecated via a **Specification Enhancement Process (SEP)** [docs/community/feature-lifecycle.mdx:55-56](). The deprecation must include:
*   **Minimum Deprecation Window**: At least **twelve months** before the feature is eligible for removal [docs/community/feature-lifecycle.mdx:65-66]().
*   **Migration Path**: Instructions on how to achieve the same functionality using active features [docs/community/feature-lifecycle.mdx:61-64]().

### Deprecated Features Registry
The file `docs/specification/draft/deprecated.mdx` is the canonical registry for features in a Deprecated or Removed state [docs/specification/draft/deprecated.mdx:7-10]().

| Feature | Deprecated In | Migration Path | Earliest Removal |
| :--- | :--- | :--- | :--- |
| **Roots** | `2026-07-28` | Pass paths via tool parameters/resource URIs [docs/specification/draft/deprecated.mdx:26-26]() | 2027-07-28 |
| **Sampling** | `2026-07-28` | Integrate directly with LLM provider APIs [docs/specification/draft/deprecated.mdx:27-27]() | 2027-07-28 |
| **Logging** | `2026-07-28` | Log to `stderr` or use OpenTelemetry [docs/specification/draft/deprecated.mdx:28-28]() | 2027-07-28 |
| **HTTP+SSE** | `2025-03-26` | Use Streamable HTTP [docs/specification/draft/deprecated.mdx:31-31]() | ~SEP-2596 + 3mo |

Sources: [docs/community/feature-lifecycle.mdx:24-72](), [docs/specification/draft/deprecated.mdx:22-31]()

## Protocol Evolution and Changelog

The repository tracks changes across releases via `changelog.mdx` files and date-versioned schema snapshots.

### Major Specification Milestones
*   **2024-11-05**: Initial foundation. Introduced basic JSON-RPC 2.0 structure, Resources, Prompts, and Tools [schema/2024-11-05/schema.ts:5-6]().
*   **2025-03-26**: Introduced `JSONRPCBatchRequest` and `JSONRPCBatchResponse` types [schema/2025-03-26/schema.ts:17-22](). Introduced **Streamable HTTP** as a replacement for HTTP+SSE [docs/specification/draft/basic/transports/streamable-http.mdx:9-10]().
*   **2025-06-18**: Refined sampling with `tools` and `toolChoice` via SEP-1577 [docs/seps/1577--sampling-with-tools.mdx:31-32]().
*   **2025-11-25 (Current)**: Added **Tasks** (SEP-1686) and established the `_meta` field standard.
*   **2026-07-28 (Draft)**: Shifted to stateless transport, removed protocol-level sessions in Streamable HTTP, and initiated major feature deprecations (Roots, Sampling, Logging) [docs/specification/draft/basic/transports/streamable-http.mdx:16-20](), [docs/specification/draft/deprecated.mdx:26-28]().

### Code Entity Mapping: Feature Evolution
The diagram below illustrates how features move from proposal to the Deprecated Registry.

```mermaid
graph TD
    subgraph "Natural Language Space"
        SEP["SEP (Proposal)<br/>docs/seps/"]
        Policy["Lifecycle Policy<br/>docs/community/feature-lifecycle.mdx"]
    end

    subgraph "Code Entity Space"
        TS["TypeScript Schema<br/>schema/draft/schema.ts"]
        JSDoc["@deprecated JSDoc Tag<br/>[docs/community/feature-lifecycle.mdx:75-77]"]
        SDK["Tier 1 SDK Warning<br/>[docs/community/feature-lifecycle.mdx:110-113]"]
    end

    subgraph "Tracking Space"
        Registry["Deprecated Registry<br/>docs/specification/draft/deprecated.mdx"]
        Changelog["changelog.mdx<br/>[docs/community/feature-lifecycle.mdx:80-82]"]
    end

    Policy --> SEP
    SEP --> TS
    TS --> JSDoc
    JSDoc --> Registry
    JSDoc --> Changelog
    JSDoc --> SDK
```

Sources: [docs/community/feature-lifecycle.mdx:73-113](), [docs/specification/draft/deprecated.mdx:7-21](), [docs/specification/draft/basic/transports/streamable-http.mdx:9-25]()

---

# Page: Authorization and Security

# Authorization and Security

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [MAINTAINERS.md](MAINTAINERS.md)
- [blog/content/posts/2026-04-08-maintainer-update.md](blog/content/posts/2026-04-08-maintainer-update.md)
- [blog/static/posts/images/maintainer-update-2026-04/clare.webp](blog/static/posts/images/maintainer-update-2026-04/clare.webp)
- [blog/static/posts/images/maintainer-update-2026-04/den.jpeg](blog/static/posts/images/maintainer-update-2026-04/den.jpeg)
- [docs/community/communication.mdx](docs/community/communication.mdx)
- [docs/community/governance.mdx](docs/community/governance.mdx)
- [docs/community/sep-guidelines.mdx](docs/community/sep-guidelines.mdx)
- [docs/docs/tutorials/security/authorization.mdx](docs/docs/tutorials/security/authorization.mdx)
- [docs/specification/draft/basic/authorization/authorization-server-discovery.mdx](docs/specification/draft/basic/authorization/authorization-server-discovery.mdx)
- [docs/specification/draft/basic/authorization/client-registration.mdx](docs/specification/draft/basic/authorization/client-registration.mdx)
- [docs/specification/draft/basic/authorization/index.mdx](docs/specification/draft/basic/authorization/index.mdx)
- [docs/specification/draft/basic/authorization/security-considerations.mdx](docs/specification/draft/basic/authorization/security-considerations.mdx)

</details>



## Purpose and Scope

This section provides comprehensive coverage of the Model Context Protocol's authorization system and security architecture. MCP uses an **OAuth 2.1-based framework** to secure access to sensitive resources and operations exposed by MCP servers. While authorization is **optional**, it is the standard mechanism for HTTP-based transports to protect user data and ensure administrative actions are performed by permitted users.

Authorization is specifically designed for remote, HTTP-hosted servers. Local servers using the **stdio transport** should not follow this specification and should instead rely on environment-based credentials or local security contexts.

Sources: [docs/docs/tutorials/security/authorization.mdx:6-9](), [docs/docs/tutorials/security/authorization.mdx:21-27](), [docs/specification/draft/basic/authorization/index.mdx:12-25]()

## Core Security Architecture

The MCP security model bridges "Natural Language Space" (user intent and model reasoning) with "Code Entity Space" (authenticated protocol messages and resource access).

### System Roles and Code Entities

The following diagram maps the logical OAuth roles to specific code-level responsibilities and discovery endpoints defined in the specification.

```mermaid
graph TD
    subgraph "Client Space"
        Client["MCP Client<br/>(OAuth 2.1 Client)"]
        PKCE["PKCE Handler<br/>S256 code_challenge"]
    end

    subgraph "Server Space (Resource)"
        Server["MCP Server<br/>(Resource Server)"]
        PRM["Protected Resource Metadata<br/>/.well-known/oauth-protected-resource"]
        AuthHeader["WWW-Authenticate Header<br/>401 response with resource_metadata"]
    end

    subgraph "Identity Space"
        AuthServer["Authorization Server"]
        ASMetadata["AS Metadata<br/>/.well-known/oauth-authorization-server"]
        RegEndpoint["registration_endpoint<br/>(CIMD/DCR)"]
        TokenEndpoint["token_endpoint<br/>(Token exchange)"]
    end

    Client -- "1. Unauthenticated Request" --> Server
    Server -- "2. HTTP 401 Unauthorized" --> Client
    Client -- "3. Fetch Metadata" --> PRM
    PRM -- "4. Provides authorization_servers" --> Client
    Client -- "5. Discover Endpoints" --> ASMetadata
    Client -- "6. Authenticate & Token Exchange" --> TokenEndpoint
    Client -- "7. Bearer Token Request" --> Server
```
**Diagram: Mapping Protocol Roles to Code Entities**

Sources: [docs/docs/tutorials/security/authorization.mdx:34-45](), [docs/specification/draft/basic/authorization/index.mdx:47-59](), [docs/specification/draft/basic/authorization/authorization-server-discovery.mdx:7-19](), [docs/specification/draft/basic/authorization/authorization-server-discovery.mdx:100-125]()

## Key Authorization Components

MCP's security framework is modular, with detailed documentation available for each sub-system:

### [OAuth 2.1 Authorization Framework](#3.1)
MCP adopts the **OAuth 2.1** draft specification as its core authorization lifecycle. This includes:
- **Discovery**: Using Protected Resource Metadata ([RFC 9728]()) and Authorization Server Metadata ([RFC 8414]()).
- **PKCE Requirements**: Mandatory use of Proof Key for Code Exchange (PKCE) with the `S256` method to prevent code interception.
- **Resource Binding**: Mandatory use of the `resource` parameter ([RFC 8707]()) to bind tokens to specific server audiences.

For details, see [OAuth 2.1 Authorization Framework](#3.1).

Sources: [docs/specification/draft/basic/authorization/index.mdx:27-46](), [docs/specification/draft/basic/authorization/security-considerations.mdx:11-13](), [docs/specification/draft/basic/authorization/security-considerations.mdx:50-54]()

### [Client Registration Methods](#3.2)
Before a client can authorize, it must be known to the Authorization Server. MCP supports three methods:
1. **Client ID Metadata Documents (CIMD)**: The primary method (SEP-991) where clients use HTTPS URLs as identifiers pointing to a JSON document.
2. **Dynamic Client Registration (DCR)**: A legacy fallback ([RFC 7591]()) for servers that do not yet support CIMD.
3. **Pre-registration**: For established relationships between specific clients and servers.

For details, see [Client Registration Methods](#3.2).

Sources: [docs/specification/draft/basic/authorization/client-registration.mdx:7-19](), [docs/specification/draft/basic/authorization/client-registration.mdx:20-29](), [docs/specification/draft/basic/authorization/client-registration.mdx:140-145]()

### [Token Management and Validation](#3.3)
This covers the operational lifecycle of credentials:
- **Validation**: Servers **MUST** validate the `aud` (audience) claim to ensure the token was specifically issued for their use.
- **Scope Strategy**: MCP uses a "principle of least privilege" approach, where servers suggest required scopes in the `WWW-Authenticate` challenge.
- **Step-up Flow**: Handling `insufficient_scope` errors by requesting additional permissions from the resource owner.

For details, see [Token Management and Validation](#3.3).

Sources: [docs/specification/draft/basic/authorization/index.mdx:97-114](), [docs/specification/draft/basic/authorization/security-considerations.mdx:14-24]()

### [Security Best Practices and Threat Models](#3.4)
Comprehensive documentation on mitigating common vulnerabilities:
- **Confused Deputy**: Preventing servers from being tricked into using their authority on behalf of a malicious client.
- **Token Passthrough**: Explicitly forbidden; servers must never forward tokens received from clients to other services.
- **Mix-Up Attacks**: Mitigation via `iss` (issuer) identification in authorization responses ([RFC 9207]()).
- **Local Server Security**: Specific requirements for servers running on `localhost` (SEP-1024).

For details, see [Security Best Practices and Threat Models](#3.4).

Sources: [docs/specification/draft/basic/authorization/security-considerations.mdx:22-23](), [docs/specification/draft/basic/authorization/security-considerations.mdx:63-68](), [blog/content/posts/2026-04-08-maintainer-update.md:39-39]()

## Standards Compliance Matrix

MCP implements a selected subset of industry standards to balance security with developer ergonomics.

| Standard | Role | Requirement |
| :--- | :--- | :--- |
| **OAuth 2.1** | Core Framework | **MUST** (for HTTP) |
| **RFC 9728** | Resource Metadata | **MUST** (for discovery) |
| **RFC 8414** | AS Metadata | **MUST** (for clients) |
| **RFC 8707** | Resource Indicators | **MUST** (for audience binding) |
| **PKCE** | Code Protection | **MUST** (S256 method) |
| **CIMD** | Client Identity | **SHOULD** (recommended registration) |

Sources: [docs/specification/draft/basic/authorization/index.mdx:27-46](), [docs/specification/draft/basic/authorization/security-considerations.mdx:50-54](), [docs/specification/draft/basic/authorization/client-registration.mdx:22-24]()

## Security Governance

The security and authorization specifications are managed by dedicated Interest Groups (IGs) within the MCP governance structure, overseen by the Steering Group.

- **Security Interest Group**: Facilitated by [Den Delimarsky](https://github.com/localden), [Paul Carleton](https://github.com/pcarleton), and [Jenn Newton](https://github.com/jenn-newton).
- **Authorization Interest Group**: Facilitated by [Aaron Parecki](https://github.com/aaronpk), [Darin McAdams](https://github.com/D-McAdams), and [Paul Carleton](https://github.com/pcarleton).

Sources: [MAINTAINERS.md:160-171](), [docs/community/governance.mdx:68-75](), [blog/content/posts/2026-04-08-maintainer-update.md:39-40]()

---

# Page: OAuth 2.1 Authorization Framework

# OAuth 2.1 Authorization Framework

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [MAINTAINERS.md](MAINTAINERS.md)
- [blog/content/posts/2026-04-08-maintainer-update.md](blog/content/posts/2026-04-08-maintainer-update.md)
- [blog/static/posts/images/maintainer-update-2026-04/clare.webp](blog/static/posts/images/maintainer-update-2026-04/clare.webp)
- [blog/static/posts/images/maintainer-update-2026-04/den.jpeg](blog/static/posts/images/maintainer-update-2026-04/den.jpeg)
- [docs/community/communication.mdx](docs/community/communication.mdx)
- [docs/community/governance.mdx](docs/community/governance.mdx)
- [docs/community/sep-guidelines.mdx](docs/community/sep-guidelines.mdx)
- [docs/docs/tutorials/security/authorization.mdx](docs/docs/tutorials/security/authorization.mdx)
- [docs/specification/2025-06-18/basic/authorization.mdx](docs/specification/2025-06-18/basic/authorization.mdx)
- [docs/specification/2025-06-18/basic/index.mdx](docs/specification/2025-06-18/basic/index.mdx)
- [docs/specification/2025-06-18/basic/transports.mdx](docs/specification/2025-06-18/basic/transports.mdx)
- [docs/specification/2025-06-18/basic/utilities/cancellation.mdx](docs/specification/2025-06-18/basic/utilities/cancellation.mdx)
- [docs/specification/2025-06-18/basic/utilities/ping.mdx](docs/specification/2025-06-18/basic/utilities/ping.mdx)
- [docs/specification/2025-06-18/client/sampling.mdx](docs/specification/2025-06-18/client/sampling.mdx)
- [docs/specification/draft/basic/authorization/authorization-server-discovery.mdx](docs/specification/draft/basic/authorization/authorization-server-discovery.mdx)
- [docs/specification/draft/basic/authorization/client-registration.mdx](docs/specification/draft/basic/authorization/client-registration.mdx)
- [docs/specification/draft/basic/authorization/index.mdx](docs/specification/draft/basic/authorization/index.mdx)
- [docs/specification/draft/basic/authorization/security-considerations.mdx](docs/specification/draft/basic/authorization/security-considerations.mdx)

</details>



## Purpose and Scope

This document describes MCP's OAuth 2.1-based authorization framework for HTTP-based transports. It covers authorization server discovery, client registration methods, token management, and security requirements for implementing protected MCP servers and clients.

Authorization is **OPTIONAL** for MCP implementations. When implemented, this specification applies **ONLY** to HTTP-based transports. For STDIO transports, implementations **SHOULD NOT** follow this specification and instead retrieve credentials from the environment or use third-party libraries embedded directly in the server. For alternative transports, follow established security best practices for that protocol.

**Sources:** [docs/specification/draft/basic/authorization/index.mdx:8-25](), [docs/docs/tutorials/security/authorization.mdx:6-27](), [docs/specification/2025-06-18/basic/authorization.mdx:7-24]()

## Standards and Specifications

MCP's authorization framework implements a selected subset of OAuth 2.1 and related specifications to ensure security while maintaining simplicity:

| Specification | RFC/Draft | Purpose |
|---------------|-----------|---------|
| OAuth 2.1 | draft-ietf-oauth-v2-1-13 | Core authorization protocol framework |
| Authorization Server Metadata | RFC8414 | Discovery of authorization server capabilities |
| Dynamic Client Registration | RFC7591 | Automatic client registration (deprecated in favor of CIMD) |
| Protected Resource Metadata | RFC9728 | Discovery of resource server authorization requirements |
| Resource Indicators | RFC8707 | Token audience binding to prevent misuse |
| Bearer Token Usage | RFC6750 | Access token transmission in HTTP requests |
| Client ID Metadata Documents | draft-ietf-oauth-client-id-metadata-document-00 | URL-based client identification (CIMD) |
| OIDC Discovery 1.0 | OpenID Connect | Alternative discovery mechanism for auth servers |

**Sources:** [docs/specification/draft/basic/authorization/index.mdx:26-46](), [docs/docs/tutorials/security/authorization.mdx:34-44](), [docs/specification/2025-06-18/basic/authorization.mdx:25-37]()

## Roles and Architecture

### OAuth 2.1 Role Mapping

```mermaid
graph TB
    subgraph "OAuth 2.1 Roles in MCP Context"
        RC["Resource Owner<br/>(End User)"]
        
        subgraph "MCP Client Role"
            MC["MCP Client<br/>OAuth 2.1 Client<br/>Makes protected requests"]
        end
        
        subgraph "MCP Server Role"
            MS["MCP Server<br/>OAuth 2.1 Resource Server<br/>Validates access tokens"]
        end
        
        subgraph "Authorization Server Role"
            AS["Authorization Server<br/>Issues access tokens<br/>May be separate service"]
        end
    end
    
    RC -->|"Authorizes"| AS
    MC -->|"1. Requests without token"| MS
    MS -->|"2. HTTP 401 + WWW-Authenticate"| MC
    MC -->|"3. Discovery & OAuth flow"| AS
    AS -->|"4. Returns access token"| MC
    MC -->|"5. Protected requests with Bearer token"| MS
    MS -->|"6. Validates token audience"| AS
```

**Roles:**
- **MCP Server**: Acts as an OAuth 2.1 resource server, capable of accepting and responding to protected resource requests using access tokens.
- **MCP Client**: Acts as an OAuth 2.1 client, making protected resource requests on behalf of a resource owner.
- **Authorization Server**: Responsible for interacting with the user and issuing access tokens. It may be hosted with the resource server or as a separate entity.

**Sources:** [docs/specification/draft/basic/authorization/index.mdx:47-59](), [docs/docs/tutorials/security/authorization.mdx:122-133](), [docs/specification/2025-06-18/basic/authorization.mdx:40-52]()

### Implementation Requirements Matrix

| Component | MUST | SHOULD | MAY |
|-----------|------|--------|-----|
| **Authorization Servers** | Implement OAuth 2.1, support PKCE, provide RFC8414 or OIDC Discovery | Support Client ID Metadata Documents (CIMD) | Support Dynamic Client Registration (RFC7591) |
| **MCP Servers** | Implement RFC9728 Protected Resource Metadata, validate token audience | Include `scope` in 401 responses | Provide metadata at root well-known URI |
| **MCP Clients** | Support AS discovery (RFC8414/OIDC), use PKCE (S256), include `resource` parameter | Support CIMD for registration | Support Dynamic Client Registration |

**Sources:** [docs/specification/draft/basic/authorization/index.mdx:60-81](), [docs/specification/draft/basic/authorization/security-considerations.mdx:50-54](), [docs/specification/2025-06-18/basic/authorization.mdx:53-67]()

## Authorization Server Discovery

### Discovery Mechanisms

MCP provides a two-stage discovery process: first locating the Protected Resource Metadata (PRM) on the MCP server, then using that to find the Authorization Server (AS) metadata.

```mermaid
sequenceDiagram
    participant C as "MCP Client"
    participant M as "MCP Server"
    participant A as "Authorization Server"
    
    Note over C: "Attempt unauthenticated request"
    C->>M: "MCP request without token"
    M->>C: "HTTP 401 Unauthorized<br/>WWW-Authenticate: Bearer resource_metadata=..., scope=..."
    
    alt "WWW-Authenticate includes resource_metadata"
        C->>M: "GET resource_metadata URI"
        M->>C: "PRM Document (RFC9728)<br/>{authorization_servers: [...]}"
    else "No resource_metadata in header"
        Note over C: "Fallback to well-known URI probing"
        C->>M: "GET /.well-known/oauth-protected-resource/mcp"
        M->>C: "PRM Document"
    end
    
    Note over C: "Extract AS URL and fetch AS Metadata"
    C->>A: "GET /.well-known/oauth-authorization-server"
    A->>C: "AS Metadata (RFC8414)"
```

**Sources:** [docs/specification/draft/basic/authorization/authorization-server-discovery.mdx:7-55](), [docs/docs/tutorials/security/authorization.mdx:34-77](), [docs/specification/2025-06-18/basic/authorization.mdx:97-126]()

### Protected Resource Metadata (PRM) Discovery

MCP servers **MUST** implement one of the following to provide AS location information:

1. **WWW-Authenticate Header**: Include the URL in the `resource_metadata` parameter of the `WWW-Authenticate` header in a 401 response.
2. **Well-Known URI**: Serve metadata at `/.well-known/oauth-protected-resource` or a sub-path corresponding to the MCP endpoint.

MCP clients **MUST** support both and prioritize the header value if present.

**Sources:** [docs/specification/draft/basic/authorization/authorization-server-discovery.mdx:37-50](), [docs/docs/tutorials/security/authorization.mdx:34-60](), [docs/specification/2025-06-18/basic/authorization.mdx:74-92]()

### Authorization Server Metadata Discovery

To handle different issuer URL formats, MCP clients **MUST** attempt multiple well-known endpoints:

**For issuer URLs with path components** (e.g., `https://auth.example.com/tenant1`):
1. OAuth 2.0 AS Metadata: `https://auth.example.com/.well-known/oauth-authorization-server/tenant1`
2. OIDC Discovery: `https://auth.example.com/.well-known/openid-configuration/tenant1`
3. OIDC Discovery (path appending): `https://auth.example.com/tenant1/.well-known/openid-configuration`

**Validation:** MCP clients **MUST** validate that the `issuer` value in the retrieved document is identical to the issuer identifier used to construct the URL.

**Sources:** [docs/specification/draft/basic/authorization/authorization-server-discovery.mdx:56-95](), [docs/docs/tutorials/security/authorization.mdx:62-77](), [docs/specification/2025-06-18/basic/authorization.mdx:93-96]()

## Client Registration Methods

### Selection Priority

Clients supporting all options **SHOULD** use the following priority order:
1. **Pre-registration**: Use existing credentials if available.
2. **Client ID Metadata Documents (CIMD)**: Use if AS metadata indicates `client_id_metadata_document_supported`.
3. **Dynamic Client Registration (DCR)**: Use as fallback if `registration_endpoint` is present.
4. **Manual Prompt**: Prompt the user to enter information.

**Sources:** [docs/specification/draft/basic/authorization/client-registration.mdx:7-19]()

### Client ID Metadata Documents (CIMD)

This approach enables clients to use HTTPS URLs as client identifiers, pointing to a JSON document containing client metadata. This is the recommended approach for the unbounded MCP ecosystem.

**Client Requirements:**
- Host metadata at an HTTPS URL.
- The `client_id` URL MUST match the document URL exactly.
- Required properties: `client_id`, `client_name`, `redirect_uris`.

**Server Requirements:**
- SHOULD fetch metadata when encountering URL-formatted `client_ids`.
- MUST validate document structure and `client_id` match.
- SHOULD cache metadata respecting HTTP headers.

**Sources:** [docs/specification/draft/basic/authorization/client-registration.mdx:20-71]()

### Dynamic Client Registration (DCR)

**Warning:** DCR is deprecated in the MCP specification. New implementations should use CIMD. It remains for backwards compatibility with older authorization servers.

**Sources:** [docs/specification/draft/basic/authorization/client-registration.mdx:140-145](), [docs/docs/tutorials/security/authorization.mdx:83-95](), [docs/specification/2025-06-18/basic/authorization.mdx:128-146]()

## Authorization Lifecycle

### PKCE Requirements

**Proof Key for Code Exchange (PKCE)** is mandatory for all MCP clients to mitigate authorization code interception.

- Clients **MUST** use the `S256` code challenge method.
- Clients **MUST** verify PKCE support in AS metadata (`code_challenge_methods_supported`) before proceeding.
- If the field is absent, the client **MUST** refuse to proceed.

**Sources:** [docs/specification/draft/basic/authorization/security-considerations.mdx:45-62](), [docs/docs/tutorials/security/authorization.mdx:106-119]()

### Resource Parameter Usage

MCP clients **MUST** include the `resource` parameter (RFC8707) in authorization and token requests to bind tokens to their intended audiences.

- The `resource` parameter identifies the canonical URI of the MCP server.
- MCP servers **MUST** validate that tokens presented were specifically issued for their use.

**Sources:** [docs/specification/draft/basic/authorization/security-considerations.mdx:14-24](), [docs/specification/draft/basic/authorization/index.mdx:39-40]()

### Scope Selection and Challenges

1. **Initial Handshake**: MCP servers SHOULD include a `scope` parameter in the `WWW-Authenticate` header to guide clients on required permissions.
2. **Least Privilege**: Clients SHOULD treat these scopes as authoritative for the current operation.
3. **Step-up Authorization**: If a client attempts an operation requiring more permissions, the server returns a `403 Forbidden` with `error="insufficient_scope"` and the required `scope` list. The client then re-authorizes to upgrade the token.

**Sources:** [docs/specification/draft/basic/authorization/index.mdx:98-123](), [docs/specification/draft/basic/authorization/index.mdx:504-559]()

## Security Requirements

### Token Validation

MCP servers **MUST** validate tokens on every request:
- **Audience Binding**: Verify the token was issued for the server's specific URI.
- **Issuer Validation**: Verify the token was issued by a trusted AS.
- **Scope Verification**: Ensure the token possesses the scopes required for the specific MCP method or resource.

**Sources:** [docs/specification/draft/basic/authorization/security-considerations.mdx:14-24](), [docs/docs/tutorials/security/authorization.mdx:122-133]()

### Threat Mitigations

- **Token Passthrough**: Explicitly forbidden. Servers must never forward a client's token to upstream services.
- **Mix-Up Attacks**: Mitigated by validating the `iss` (issuer) parameter in the authorization response.
- **SSRF**: Authorization servers fetching CIMD documents MUST implement SSRF protections against malicious client URLs.
- **Token Theft**: AS SHOULD issue short-lived access tokens and MUST rotate refresh tokens for public clients.

**Sources:** [docs/specification/draft/basic/authorization/security-considerations.mdx:25-35](), [docs/specification/draft/basic/authorization/security-considerations.mdx:63-68](), [docs/specification/draft/basic/authorization/security-considerations.mdx:90-97]()

---

# Page: Client Registration Methods

# Client Registration Methods

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [blog/content/archives.md](blog/content/archives.md)
- [blog/content/posts/client_registration/index.md](blog/content/posts/client_registration/index.md)
- [blog/content/posts/client_registration/mitigation-attack-cost.png](blog/content/posts/client_registration/mitigation-attack-cost.png)
- [blog/content/search.md](blog/content/search.md)
- [blog/layouts/_markup/render-codeblock-mermaid.html](blog/layouts/_markup/render-codeblock-mermaid.html)
- [blog/layouts/baseof.html](blog/layouts/baseof.html)
- [docs/seps/1024-mcp-client-security-requirements-for-local-server-.mdx](docs/seps/1024-mcp-client-security-requirements-for-local-server-.mdx)
- [docs/seps/1034--support-default-values-for-all-primitive-types-in.mdx](docs/seps/1034--support-default-values-for-all-primitive-types-in.mdx)
- [docs/seps/1036-url-mode-elicitation-for-secure-out-of-band-intera.mdx](docs/seps/1036-url-mode-elicitation-for-secure-out-of-band-intera.mdx)
- [docs/seps/1046-support-oauth-client-credentials-flow-in-authoriza.mdx](docs/seps/1046-support-oauth-client-credentials-flow-in-authoriza.mdx)
- [docs/seps/1302-formalize-working-groups-and-interest-groups-in-mc.mdx](docs/seps/1302-formalize-working-groups-and-interest-groups-in-mc.mdx)
- [docs/seps/1303-input-validation-errors-as-tool-execution-errors.mdx](docs/seps/1303-input-validation-errors-as-tool-execution-errors.mdx)
- [docs/seps/1319-decouple-request-payload-from-rpc-methods-definiti.mdx](docs/seps/1319-decouple-request-payload-from-rpc-methods-definiti.mdx)
- [docs/seps/991-enable-url-based-client-registration-using-oauth-c.mdx](docs/seps/991-enable-url-based-client-registration-using-oauth-c.mdx)
- [docs/spec-version-warning.js](docs/spec-version-warning.js)

</details>



## Purpose and Scope

This document explains the three client registration approaches supported by the Model Context Protocol (MCP) for HTTP-based transports: **Client ID Metadata Documents (CIMD)**, **Dynamic Client Registration (DCR)**, and **Pre-registration**. Client registration is the prerequisite step where an MCP client obtains or provides a `client_id` to identify itself to an authorization server before initiating an OAuth 2.1 flow [docs/seps/991-enable-url-based-client-registration-using-oauth-c.mdx:35-39]().

## The Registration Challenge in MCP

MCP's architecture often involves clients and servers with no prior relationship. Unlike traditional OAuth where a client developer registers their app with a specific provider (e.g., "Login with Google"), an MCP client must be able to connect to any remote MCP server the user specifies [blog/content/posts/client_registration/index.md:61-65]().

This creates two primary challenges:
1. **Operational Scale**: It is impossible for every client to be pre-registered with every possible authorization server [blog/content/posts/client_registration/index.md:65-66]().
2. **Trust and Identity**: Authorization servers need a way to verify client metadata (like names and redirect URIs) to prevent impersonation and phishing [blog/content/posts/client_registration/index.md:55-58]().

**Sources:** [blog/content/posts/client_registration/index.md:55-66](), [docs/seps/991-enable-url-based-client-registration-using-oauth-c.mdx:46-55]()

## Registration Approach Priority

The MCP specification adopts OAuth 2.1 as its foundation [blog/content/posts/client_registration/index.md:9-9](). While multiple methods exist, SEP-991 establishes a clear preference for URL-based metadata discovery in open ecosystems.

| Priority | Method | Description |
| :--- | :--- | :--- |
| 1 | **Pre-registration** | Optimal for established relationships where credentials already exist [docs/seps/991-enable-url-based-client-registration-using-oauth-c.mdx:54-55](). |
| 2 | **Client ID Metadata Documents** | **SHOULD** be supported as the primary method for open connections [docs/seps/991-enable-url-based-client-registration-using-oauth-c.mdx:77-79](). |
| 3 | **Dynamic Client Registration** | **MAY** be supported for backwards compatibility [docs/seps/991-enable-url-based-client-registration-using-oauth-c.mdx:77-79](). |

**Sources:** [docs/seps/991-enable-url-based-client-registration-using-oauth-c.mdx:77-79](), [blog/content/posts/client_registration/index.md:77-78]()

## Client ID Metadata Documents (CIMD)

CIMD (based on `draft-parecki-oauth-client-id-metadata-document`) allows an OAuth client to use an HTTPS URL as its `client_id` [docs/seps/991-enable-url-based-client-registration-using-oauth-c.mdx:29-31](). This URL points to a JSON document containing the client's metadata, enabling trust without pre-coordination [docs/seps/991-enable-url-based-client-registration-using-oauth-c.mdx:59-61]().

### Metadata Document Requirements
Clients MUST host a valid JSON document at an HTTPS URL containing at minimum [docs/seps/991-enable-url-based-client-registration-using-oauth-c.mdx:121-125]():
*   `client_id`: MUST exactly match the document URL.
*   `client_name`: Human-readable name for the consent screen.
*   `redirect_uris`: Array of allowed redirection endpoints.

### CIMD Implementation Data Flow
This diagram illustrates the interaction between the `Authorization Server` and the `Metadata Endpoint` (the client's URL).

**Diagram: CIMD Metadata Retrieval and Validation**
```mermaid
sequenceDiagram
    participant User ["User"]
    participant Client ["MCP Client"]
    participant AS ["Authorization Server"]
    participant Meta ["Metadata Endpoint (HTTPS URL)"]
    participant Resource ["MCP Server (Resource)"]

    Note over Client,Meta: "Client hosts metadata at https://app.example.com/oauth/metadata.json"
    
    User->>Client: "Initiate connection to MCP Server"
    Client->>AS: "Authorization Request (client_id=HTTPS_URL)"
    
    Note over AS: "Detect URL-formatted client_id"
    AS->>Meta: "GET https://app.example.com/oauth/metadata.json"
    Meta-->>AS: "JSON Metadata Document"
    
    Note over AS: "Validation: Check client_id matches URL & redirect_uri is allowed"
    
    AS->>User: "Display consent page with client_name"
    User->>AS: "Approve access"
    AS->>Client: "Authorization code via redirect_uri"
    Client->>AS: "Exchange code for token"
    AS-->>Client: "Access token"
    Client->>Resource: "MCP requests with access token"
```
**Sources:** [docs/seps/991-enable-url-based-client-registration-using-oauth-c.mdx:83-119]()

### Security Implications of CIMD
*   **Trust Model**: Servers can trust clients based on the HTTPS domain hosting the metadata and domain reputation [docs/seps/991-enable-url-based-client-registration-using-oauth-c.mdx:63-66]().
*   **Policy Control**: Authorization servers can be "Open" (accepting any HTTPS `client_id`) or "Protected" (restricting to specific domains) [docs/seps/991-enable-url-based-client-registration-using-oauth-c.mdx:68-71]().
*   **Caching**: Servers should cache metadata document results while respecting HTTP cache headers to improve performance [docs/seps/991-enable-url-based-client-registration-using-oauth-c.mdx:118-119]().

## Dynamic Client Registration (DCR)

DCR (RFC 7591) provides an API for just-in-time registration by sending client metadata to a registration endpoint [docs/seps/991-enable-url-based-client-registration-using-oauth-c.mdx:38-38]().

### Operational Limitations
DCR presents several challenges in the open MCP ecosystem:
*   **Unbounded Database Growth**: Every user instance of a client (e.g., Claude Desktop on two different machines) typically creates distinct registrations, leading to database bloat for the authorization server [blog/content/posts/client_registration/index.md:94-96]().
*   **Client Expiry**: There is no standard mechanism to notify a client that its ID is invalid, often leading to "black hole" registrations [blog/content/posts/client_registration/index.md:97-98]().
*   **Impersonation Risk**: Open DCR endpoints are vulnerable to clients claiming false identities (e.g., a malicious app claiming to be "Claude Desktop") unless strict vetting is applied [blog/content/posts/client_registration/index.md:57-58]().

**Sources:** [blog/content/posts/client_registration/index.md:88-105](), [docs/seps/991-enable-url-based-client-registration-using-oauth-c.mdx:38-45]()

## Pre-registration

Pre-registration is the traditional OAuth pattern where a `client_id` is issued manually by the server administrator to the client developer [docs/seps/991-enable-url-based-client-registration-using-oauth-c.mdx:37-37]().

### Machine-to-Machine (M2M) Scenarios
For scenarios where an end-user is unavailable for interactive authorization, SEP-1046 recommends the **OAuth client credentials flow** [docs/seps/1046-support-oauth-client-credentials-flow-in-authoriza.mdx:31-31](). 
*   **JWT Assertions**: The RECOMMENDED method using asymmetric keys (RFC 7523) [docs/seps/1046-support-oauth-client-credentials-flow-in-authoriza.mdx:39-40]().
*   **Client Secrets**: Allowed for maximum compatibility with existing systems via HTTP Basic authentication [docs/seps/1046-support-oauth-client-credentials-flow-in-authoriza.mdx:48-49]().

**Sources:** [docs/seps/991-enable-url-based-client-registration-using-oauth-c.mdx:37-37](), [docs/seps/1046-support-oauth-client-credentials-flow-in-authoriza.mdx:31-52]()

## Summary of Registration Flow Logic

This diagram maps the decision logic a client or server might use when determining which registration entity to use.

**Diagram: Registration Method Selection Logic**
```mermaid
graph TD
    Start["Start Connection"] --> HasCreds{"Pre-existing relationship?"}
    HasCreds -- "Yes" --> PreReg["Use Pre-registered client_id"]
    HasCreds -- "No" --> CheckAS{"Check AS Metadata"}
    
    CheckAS --> CIMDSupport{"client_id_metadata_document_supported?"}
    CIMDSupport -- "Yes" --> UseCIMD["Use HTTPS URL as client_id (SEP-991)"]
    CIMDSupport -- "No" --> DCRSupport{"registration_endpoint present?"}
    
    DCRSupport -- "Yes" --> UseDCR["POST to Registration Endpoint (RFC 7591)"]
    DCRSupport -- "No" --> Manual["Manual Client ID Entry (Fallback)"]

    subgraph "Entities in Code"
        UseCIMD -.-> CIMD_Doc["JSON Metadata Document"]
        UseDCR -.-> DCR_Req["Dynamic Registration Request"]
        PreReg -.-> ClientID["Static Client ID"]
    end
```
**Sources:** [docs/seps/991-enable-url-based-client-registration-using-oauth-c.mdx:77-81](), [blog/content/posts/client_registration/index.md:65-78]()

---

# Page: Token Management and Validation

# Token Management and Validation

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [MAINTAINERS.md](MAINTAINERS.md)
- [blog/content/posts/2026-04-08-maintainer-update.md](blog/content/posts/2026-04-08-maintainer-update.md)
- [blog/static/posts/images/maintainer-update-2026-04/clare.webp](blog/static/posts/images/maintainer-update-2026-04/clare.webp)
- [blog/static/posts/images/maintainer-update-2026-04/den.jpeg](blog/static/posts/images/maintainer-update-2026-04/den.jpeg)
- [docs/community/communication.mdx](docs/community/communication.mdx)
- [docs/community/governance.mdx](docs/community/governance.mdx)
- [docs/community/sep-guidelines.mdx](docs/community/sep-guidelines.mdx)
- [docs/docs/tutorials/security/authorization.mdx](docs/docs/tutorials/security/authorization.mdx)
- [docs/seps/2164-resource-not-found-error.mdx](docs/seps/2164-resource-not-found-error.mdx)
- [docs/seps/2207-oidc-refresh-token-guidance.mdx](docs/seps/2207-oidc-refresh-token-guidance.mdx)
- [docs/seps/2468-recommend-issuer-claim-for-auth.mdx](docs/seps/2468-recommend-issuer-claim-for-auth.mdx)
- [docs/seps/2484-conformance-tests-required-for-final-seps.mdx](docs/seps/2484-conformance-tests-required-for-final-seps.mdx)
- [docs/specification/2025-03-26/basic/authorization.mdx](docs/specification/2025-03-26/basic/authorization.mdx)
- [seps/2164-resource-not-found-error.md](seps/2164-resource-not-found-error.md)
- [seps/2207-oidc-refresh-token-guidance.md](seps/2207-oidc-refresh-token-guidance.md)
- [seps/2468-recommend-issuer-claim-for-auth.md](seps/2468-recommend-issuer-claim-for-auth.md)
- [seps/2484-conformance-tests-required-for-final-seps.md](seps/2484-conformance-tests-required-for-final-seps.md)

</details>



## Purpose and Scope

This page documents how MCP handles access tokens throughout their lifecycle: from initial acquisition during the OAuth 2.1 authorization flow, through validation and usage in requests, to refresh and expiration handling. It covers the mechanisms by which MCP clients obtain tokens, how MCP servers validate them, and the security requirements that govern token handling, including issuer validation and OIDC compatibility.

For information about the complete OAuth 2.1 authorization framework and client registration, see **3.1 OAuth 2.1 Authorization Framework**. For client registration methods specifically, see **3.2 Client Registration Methods**. For security threats and mitigations related to tokens, see **3.4 Security Best Practices and Threat Models**.

## Token Lifecycle Overview

Access tokens in MCP follow a standard OAuth 2.1 lifecycle with several key phases.

Title: Token Lifecycle Data Flow
```mermaid
graph LR
    A["Client Requests<br/>Authorization"] --> B["Authorization Server<br/>Issues Token"]
    B --> C["Client Stores<br/>Token"]
    C --> D["Client Includes Token<br/>in Requests"]
    D --> E["Server Validates<br/>Token"]
    E --> F{"Token Valid?"}
    F -->|Yes| G["Process Request"]
    F -->|No| H["Return 401"]
    G --> I{"Token Expired?"}
    I -->|Yes| J["Client Refreshes<br/>Token"]
    I -->|No| K["Continue Using<br/>Token"]
    J --> C
    K --> D
    H --> J
```

**Sources:** [docs/specification/2025-03-26/basic/authorization.mdx:85-103](), [docs/tutorials/security/authorization.mdx:29-134]()

## Token Acquisition

### Authorization Flow Token Request

After the user completes authorization, the MCP client exchanges an authorization code for tokens at the authorization server's token endpoint. This exchange includes the `resource` parameter to bind the token to the specific MCP server.

**Token Request Parameters:**

| Parameter | Required | Purpose |
|-----------|----------|---------|
| `grant_type` | Yes | Must be `authorization_code` |
| `code` | Yes | Authorization code from authorization endpoint |
| `code_verifier` | Yes | PKCE verifier matching the `code_challenge` |
| `resource` | Yes | Canonical URI of the MCP server (RFC 8707) |
| `client_id` | Yes | Client identifier |
| `redirect_uri` | Yes | Must match registered redirect URI |

**Token Response:**

```json
{
  "access_token": "eyJhbGciOiJSUzI1NiIs...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "refresh_token": "def502...",
  "scope": "mcp:tools mcp:resources"
}
```

The `access_token` is an opaque string (or JWT) that the client includes in subsequent requests. The `refresh_token` (if present) allows obtaining new access tokens without user interaction.

**Sources:** [docs/specification/2025-03-26/basic/authorization.mdx:91-103](), [docs/tutorials/security/authorization.mdx:106-120]()

## Token Storage and Security

### Client-Side Token Storage

MCP clients **MUST** implement secure token storage following OAuth 2.1 best practices. Storage mechanisms vary by platform:

- **Desktop/Native Applications**: Use OS-provided credential storage (keychain, credential manager).
- **Web Applications**: Use secure, HTTP-only cookies or encrypted local storage.
- **Server Applications**: Use encrypted configuration or secrets management systems.

For local MCP servers using the **STDIO transport**, environment-based credentials or third-party libraries are recommended instead of OAuth flows.

**Sources:** [docs/tutorials/security/authorization.mdx:20-27]()

## Token Validation

### Server-Side Validation Requirements

MCP servers acting as OAuth 2.1 resource servers **MUST** validate access tokens before processing requests. Validation occurs in two phases:

#### Phase 1: Token Introspection or JWT Verification

Servers can validate tokens using either:

*   **Token Introspection (RFC 7662):** The server sends the token to the authorization server's introspection endpoint.
*   **JWT Verification:** The server validates the JWT signature using the authorization server's public keys and verifies standard claims (`exp`, `iat`, `iss`).

#### Phase 2: Audience Validation

After confirming token validity, servers **MUST** validate that the token was issued specifically for them as the intended audience. This prevents token reuse across different services.

**Audience Validation Methods:**
1.  **JWT `aud` Claim**: Verify the `aud` claim contains the server's canonical URI.
2.  **Resource Parameter Binding**: Verify the token was issued with the `resource` parameter matching the server's URI.

**Sources:** [docs/specification/2025-03-26/basic/authorization.mdx:9-12](), [docs/tutorials/security/authorization.mdx:122-133]()

### Validation Implementation Patterns

The following diagram maps high-level validation logic to code entities often found in SDK implementations.

Title: Validation Code Entity Map
```mermaid
graph TD
    subgraph "Natural Language Space"
        AuthHeader["Authorization Header"]
        Verify["Token Verification"]
        AudCheck["Audience Validation"]
    end

    subgraph "Code Entity Space"
        ReqBearer["McpServer.handleRequest"]
        Verifier["validateToken"]
        AudVal["verifyAudience"]
    end

    AuthHeader --- ReqBearer
    Verify --- Verifier
    AudCheck --- AudVal
```

**Sources:** [docs/tutorials/security/authorization.mdx:122-133]()

## Token Usage in Requests

### Bearer Token Header Format

MCP clients **MUST** include access tokens in the `Authorization` header using the Bearer scheme:

```http
GET /mcp HTTP/1.1
Host: your-server.com
Authorization: Bearer eyJhbGciOiJSUzI1NiIs...
```

### Error Responses for Invalid Tokens

When a client sends an invalid or expired token, the server **MUST** respond with `HTTP 401 Unauthorized`. The response includes the `WWW-Authenticate` header with a `resource_metadata` parameter pointing to the Protected Resource Metadata (PRM) document.

**Sources:** [docs/tutorials/security/authorization.mdx:34-43](), [docs/specification/2025-03-26/basic/authorization.mdx:76-82]()

## Token Refresh and OIDC Guidance

### Refresh Token Grant

When an access token expires, clients can obtain a new one using the refresh token via the `refresh_token` grant type.

**OIDC Refresh Token Guidance (SEP-2207):**
Specific guidance is provided for OpenID Connect refresh tokens to ensure compatibility across diverse identity providers in the MCP ecosystem.

**Sources:** [seps/2207-oidc-refresh-token-guidance.md:1-20]()

## Issuer Validation (SEP-2468)

To mitigate authorization mix-up attacks in multi-IdP environments, MCP requires explicit issuer validation.

**Requirements:**
*   **Servers**: **SHOULD** include an `iss` parameter in authorization responses and **MUST** advertise support by setting `authorization_response_iss_parameter_supported: true` in metadata.
*   **Clients**: **MUST** validate the `iss` parameter in authorization responses by comparing it against the expected issuer identifier discovered during the initial metadata fetch.

Title: Issuer Validation Flow
```mermaid
sequenceDiagram
    participant C as "MCP Client"
    participant A as "Authorization Server"
    
    C->>A: Authorization Request
    A-->>C: Redirect with code & iss
    Note over C: Client compares iss to expected issuer
    alt Match
        C->>A: Token Request
    else Mismatch
        C->>C: Abort Flow (Invalid Response)
    end
```

**Sources:** [seps/2468-recommend-issuer-claim-for-auth.md:24-60](), [docs/seps/2468-recommend-issuer-claim-for-auth.mdx:43-61]()

## Token Validation Sequence

Title: Token Validation and Refresh Sequence
```mermaid
sequenceDiagram
    participant C as "MCP Client"
    participant S as "MCP Server"
    participant A as "Authorization Server"
    
    C->>S: Request + Authorization: Bearer token
    
    alt Token Validation
        S->>A: Token Introspection (RFC 7662)
        A-->>S: {active: true, aud: "server_uri"}
    end
    
    S->>S: Validate aud claim
    
    alt Valid
        S-->>C: 200 OK + Resource Data
    else Invalid/Expired
        S-->>C: 401 Unauthorized
        C->>A: Refresh Token Request
        A-->>C: New Access Token
    end
```

**Sources:** [docs/specification/2025-03-26/basic/authorization.mdx:85-103](), [docs/tutorials/security/authorization.mdx:122-133]()

---

# Page: Security Best Practices and Threat Models

# Security Best Practices and Threat Models

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitattributes](.gitattributes)
- [.github/dependabot.yml](.github/dependabot.yml)
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [README.md](README.md)
- [SECURITY.md](SECURITY.md)
- [blog/content/posts/enterprise-managed-auth/ema-comparison.png](blog/content/posts/enterprise-managed-auth/ema-comparison.png)
- [blog/content/posts/enterprise-managed-auth/index.md](blog/content/posts/enterprise-managed-auth/index.md)
- [docs/community/security.mdx](docs/community/security.mdx)
- [docs/docs/tutorials/security/security_best_practices.mdx](docs/docs/tutorials/security/security_best_practices.mdx)
- [docs/extensions/auth/enterprise-managed-authorization.mdx](docs/extensions/auth/enterprise-managed-authorization.mdx)
- [docs/specification/draft/basic/authorization/authorization-server-discovery.mdx](docs/specification/draft/basic/authorization/authorization-server-discovery.mdx)
- [docs/specification/draft/basic/authorization/client-registration.mdx](docs/specification/draft/basic/authorization/client-registration.mdx)
- [docs/specification/draft/basic/authorization/index.mdx](docs/specification/draft/basic/authorization/index.mdx)
- [docs/specification/draft/basic/authorization/security-considerations.mdx](docs/specification/draft/basic/authorization/security-considerations.mdx)
- [package-lock.json](package-lock.json)
- [package.json](package.json)

</details>



## Purpose and Scope

This document identifies security threats, attack vectors, and best practices specific to the Model Context Protocol (MCP). It provides technical implementation details for mitigating risks such as the Confused Deputy problem, token passthrough, session hijacking, and Server-Side Request Forgery (SSRF). This page complements the [OAuth 2.1 Authorization Framework](/specification/draft/basic/authorization) and [Enterprise-Managed Authorization](/extensions/auth/enterprise-managed-authorization) specifications.

**Sources:** [docs/specification/draft/basic/authorization/index.mdx:8-15](), [docs/docs/tutorials/security/security_best_practices.mdx:6-20]()

## Security Architecture and Code Entities

The following diagram bridges protocol concepts to specific implementation requirements for MCP clients and servers.

```mermaid
graph TB
    subgraph "MCP Client (OAuth 2.1 Client)"
        Client["MCP Client Core"]
        CIMD["Client ID Metadata Document<br/>(draft-ietf-oauth-client-id-metadata-document-00)"]
        PKCE["PKCE: code_challenge (S256)"]
        TokenStore["Secure Token Storage"]
        
        Client --> CIMD
        Client --> PKCE
        Client --> TokenStore
    end
    
    subgraph "MCP Server (Resource Server)"
        ResourceServer["MCP Resource Server"]
        Metadata["RFC 9728: Protected Resource Metadata"]
        AudienceBinding["RFC 8707: Resource Indicators"]
        WwwAuth["WWW-Authenticate Header<br/>(Scope Guidance)"]
        
        ResourceServer --> Metadata
        ResourceServer --> AudienceBinding
        ResourceServer --> WwwAuth
    end
    
    subgraph "Authorization Server (AS)"
        AuthServer["OAuth 2.1 Auth Server"]
        AS_Metadata["RFC 8414: AS Metadata"]
        IDJAG["ID-JAG: Identity Assertion<br/>JWT Authorization Grant"]
        
        AuthServer --> AS_Metadata
        AuthServer --> IDJAG
    end

    Client -->|"GET /.well-known/oauth-protected-resource"| Metadata
    ResourceServer -->|"401 Unauthorized + scope"| WwwAuth
    Client -->|"Token Request + resource param"| AuthServer
    AuthServer -->|"Access Token (aud-bound)"| TokenStore
    TokenStore -->|"Bearer Token"| ResourceServer
```

**Sources:** [docs/specification/draft/basic/authorization/index.mdx:47-59](), [docs/specification/draft/basic/authorization/security-considerations.mdx:14-24](), [docs/specification/draft/basic/authorization/authorization-server-discovery.mdx:11-19]()

## Threat Models and Mitigations

### 1. Confused Deputy Problem (Proxy Servers)

This vulnerability occurs when an MCP proxy server connects to a third-party API using a static Client ID while allowing dynamic registration for its own clients. Attackers can exploit existing user consent cookies on the third-party Authorization Server to bypass human-in-the-loop approval.

| Code Entity / Role | Mitigation Responsibility |
|:---|:---|
| **MCP Proxy Server** | **MUST** implement per-client consent before forwarding to third-party auth. |
| **MCP Proxy Server** | **MUST** store consent decisions in a registry keyed by `client_id` and `user_id`. |
| **MCP Proxy Server** | **MUST** validate that `redirect_uri` exactly matches the registered URI. |

```mermaid
sequenceDiagram
    participant UA as "User-Agent (Browser)"
    participant MC as "Malicious MCP Client"
    participant M as "MCP Proxy Server"
    participant TAS as "Third-Party Auth Server"

    MC->>M: "Dynamic Registration (redirect_uri: attacker.com)"
    M-->>MC: "client_id: evil-123"
    MC->>UA: "Send malicious link"
    UA->>M: "GET /authorize?client_id=evil-123"
    
    rect rgb(240, 240, 240)
    Note over M: "MITIGATION: Check per-client consent"
    M->>UA: "Display MCP-level Consent UI"
    UA->>M: "User Approves evil-123"
    end

    M->>UA: "Redirect to TAS (static-proxy-id)"
    UA->>TAS: "Auth Request + Cookie"
    TAS-->>UA: "Code + Redirect to M"
    UA->>M: "Auth Code"
    M->>UA: "Redirect to attacker.com with MCP Code"
```

**Sources:** [docs/docs/tutorials/security/security_best_practices.mdx:27-73](), [docs/docs/tutorials/security/security_best_practices.mdx:160-182]()

### 2. Token Passthrough Anti-Pattern

Token passthrough is strictly forbidden. MCP servers must never forward a token received from a client directly to a downstream API.

*   **Vulnerability:** Replaying tokens across different trust boundaries.
*   **Mitigation:** 
    *   MCP clients **MUST** include the `resource` parameter ([RFC 8707](https://www.rfc-editor.org/rfc/rfc8707.html)) in requests to bind the token to a specific server [docs/specification/draft/basic/authorization/security-considerations.mdx:14-24]().
    *   MCP servers **MUST** validate the `aud` (audience) claim to ensure the token was issued specifically for them [docs/docs/tutorials/security/security_best_practices.mdx:242-244]().
    *   Servers needing upstream access **MUST** act as a separate OAuth client and obtain their own tokens [docs/docs/tutorials/security/security_best_practices.mdx:222-241]().

### 3. Server-Side Request Forgery (SSRF)

SSRF risks are prominent during **Client ID Metadata Document (CIMD)** fetching and **Authorization Server Discovery**.

*   **Threat:** A malicious client provides a `client_id` URL pointing to an internal network resource (e.g., `http://169.254.169.254/latest/meta-data/`).
*   **Mitigation:**
    *   Authorization servers **MUST** validate that `client_id` URLs use the `https` scheme [docs/specification/draft/basic/authorization/client-registration.mdx:38-42]().
    *   Authorization servers **SHOULD** implement network-level egress filtering to prevent fetching metadata from private IP ranges [docs/specification/draft/basic/authorization/security-considerations.mdx:96-100]().
    *   Fetched `client_id` values inside the document **MUST** match the request URL exactly [docs/specification/draft/basic/authorization/client-registration.mdx:47]().

**Sources:** [docs/specification/draft/basic/authorization/security-considerations.mdx:84-100](), [docs/specification/draft/basic/authorization/client-registration.mdx:38-52]()

### 4. Session Hijacking and Async Events

In Streamable HTTP transports, session IDs are used to route async events.

*   **Threat:** Predicting or stealing a `session_id` to inject malicious payloads into another user's event stream.
*   **Mitigation:**
    *   Servers **MUST NOT** use session IDs for authentication; every request must carry a Bearer token [docs/docs/tutorials/security/security_best_practices.mdx:318-322]().
    *   Session IDs **MUST** be cryptographically secure non-deterministic values (e.g., UUIDv4) [docs/docs/tutorials/security/security_best_practices.mdx:324-326]().
    *   Servers **SHOULD** bind sessions to the user identity by keying storage as `<user_id>:<session_id>` [docs/docs/tutorials/security/security_best_practices.mdx:327-331]().

**Sources:** [docs/docs/tutorials/security/security_best_practices.mdx:246-331]()

## Local Server Security

Local MCP servers (running via `stdio`) operate with the same privileges as the MCP client (e.g., the user's IDE or Desktop app).

*   **Trust Model:** Local MCP servers are trusted like any other software installed on the system [SECURITY.md:41-45]().
*   **Command Execution:** MCP clients launch servers by executing commands. This is intended behavior and not a vulnerability [SECURITY.md:62-75]().
*   **Pre-Configuration Consent:** Clients **MUST** display the full command line (no truncation) before executing a local server [docs/docs/tutorials/security/security_best_practices.mdx:365-375]().
*   **Command Sanitization:** Clients **SHOULD** warn users about dangerous patterns like `sudo`, `rm -rf`, or pipes [docs/docs/tutorials/security/security_best_practices.mdx:377-385]().
*   **Transport Boundary:** The SDK does not defend peers against a malicious counterpart across `stdio`; a malicious server already has code execution by virtue of being run [SECURITY.md:76-84]().

**Sources:** [docs/docs/tutorials/security/security_best_practices.mdx:333-392](), [SECURITY.md:31-84]()

## Enterprise and Machine-to-Machine (M2M) Security

### Enterprise-Managed Authorization (EMA)
EMA centralizes access control via an Identity Provider (IdP). It uses the **Identity Assertion JWT Authorization Grant (ID-JAG)** to eliminate per-server consent prompts.

```mermaid
sequenceDiagram
    participant C as "MCP Client"
    participant IdP as "Enterprise IdP"
    participant MAS as "MCP Auth Server"
    
    C->>IdP: "Exchange ID Token for ID-JAG"
    Note over IdP: "Evaluates Organizational Policy"
    IdP-->>C: "ID-JAG (JWT)"
    C->>MAS: "Token Request (grant_type: identity_assertion, assertion: ID-JAG)"
    MAS->>MAS: "Validate ID-JAG signature/aud/iss"
    MAS-->>C: "MCP Access Token"
```

**Sources:** [docs/extensions/auth/enterprise-managed-authorization.mdx:42-74](), [blog/content/posts/enterprise-managed-auth/index.md:62-74]()

### M2M with Client Credentials
For non-interactive scenarios (e.g., one MCP server calling another), the OAuth 2.1 **Client Credentials Grant** is used.
*   Clients **MAY** use `private_key_jwt` for authentication at the token endpoint to avoid sharing static secrets [docs/specification/draft/basic/authorization/client-registration.mdx:42]().

**Sources:** [docs/specification/draft/basic/authorization/client-registration.mdx:42](), [docs/specification/draft/basic/authorization/index.mdx:62-63]()

---

# Page: Client Ecosystem

# Client Ecosystem

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [blog/content/posts/2026-01-26-mcp-apps.md](blog/content/posts/2026-01-26-mcp-apps.md)
- [docs/community/sdk-tiers.mdx](docs/community/sdk-tiers.mdx)
- [docs/docs/develop/build-client.mdx](docs/docs/develop/build-client.mdx)
- [docs/docs/develop/build-server.mdx](docs/docs/develop/build-server.mdx)
- [docs/docs/develop/build-with-agent-skills.mdx](docs/docs/develop/build-with-agent-skills.mdx)
- [docs/docs/getting-started/intro.mdx](docs/docs/getting-started/intro.mdx)
- [docs/docs/learn/architecture.mdx](docs/docs/learn/architecture.mdx)
- [docs/docs/learn/client-concepts.mdx](docs/docs/learn/client-concepts.mdx)
- [docs/docs/learn/server-concepts.mdx](docs/docs/learn/server-concepts.mdx)
- [docs/docs/sdk.mdx](docs/docs/sdk.mdx)
- [docs/docs/tools/debugging.mdx](docs/docs/tools/debugging.mdx)
- [docs/extensions/apps/build.mdx](docs/extensions/apps/build.mdx)
- [docs/extensions/apps/overview.mdx](docs/extensions/apps/overview.mdx)
- [docs/extensions/auth/oauth-client-credentials.mdx](docs/extensions/auth/oauth-client-credentials.mdx)
- [docs/extensions/auth/overview.mdx](docs/extensions/auth/overview.mdx)
- [docs/extensions/client-matrix.mdx](docs/extensions/client-matrix.mdx)
- [docs/extensions/overview.mdx](docs/extensions/overview.mdx)
- [docs/extensions/tasks/overview.mdx](docs/extensions/tasks/overview.mdx)

</details>



This page documents the MCP client ecosystem: the applications that integrate with MCP servers to expose tools, resources, prompts, and other capabilities to users and AI models. The ecosystem includes desktop applications, IDE extensions, web platforms, CLI tools, and specialized frameworks. For details about the MCP protocol features themselves, see [Protocol Specification](#2).

## Core Client Concepts

MCP clients are instantiated by **host applications** to communicate with particular MCP servers. The host application (e.g., Claude.ai or an IDE) manages the overall user experience and coordinates multiple clients. Each client handles one direct communication with one server.

[docs/docs/learn/client-concepts.mdx:6-9]()

### Client-Server Participants
The MCP architecture involves three key participants:
- **MCP Host**: The AI application that coordinates and manages one or multiple MCP clients.
- **MCP Client**: A component that maintains a connection to an MCP server and obtains context for the host.
- **MCP Server**: A program that provides context (tools, resources, prompts) to clients.

[docs/docs/learn/architecture.mdx:35-40]()

### Participant Interaction
```mermaid
graph TB
    subgraph "MCP Host (AI Application)"
        [Client1] -- "Dedicated connection" --- [ServerA]
        [Client2] -- "Dedicated connection" --- [ServerB]
        [Client3] -- "Dedicated connection" --- [ServerC]
        [Client4] -- "Dedicated connection" --- [ServerC]
    end

    [ServerA] ["MCP Server A - Local (stdio)"]
    [ServerB] ["MCP Server B - Local (stdio)"]
    [ServerC] ["MCP Server C - Remote (Streamable HTTP)"]
```
Sources: [docs/docs/learn/architecture.mdx:44-61]()

## Client Feature Support

The MCP client ecosystem exhibits a power law distribution in feature adoption. While `Tools` represent the baseline value proposition, advanced features and extensions allow for richer interactions.

| Feature | Explanation | Example |
| :--- | :--- | :--- |
| **Elicitation** | Servers request specific information from users during interactions. | A travel server asking for seat preferences. |
| **Roots** | Clients specify filesystem boundaries for server focus. | Giving a server access to a specific workspace directory. |
| **Sampling** | Servers request LLM completions through the client (agentic workflow). | A server asking the LLM to pick the best flight from a list. |
| **Apps** | Interactive HTML interfaces rendered inline in the conversation. | A dashboard or interactive chart returned by a tool. |
| **Tasks** | Asynchronous execution for long-running operations. | A CI pipeline or batch process returning a durable handle. |

For details, see [Client Directory and Feature Matrix](#4.1).

Sources: [docs/docs/learn/client-concepts.mdx:14-18](), [docs/extensions/client-matrix.mdx:26-31](), [docs/extensions/tasks/overview.mdx:17-21]()

## Client SDK Ecosystem

Official SDKs are classified into tiers based on feature completeness, protocol support, and maintenance commitment. This system helps developers choose the right SDK for building clients.

| Tier | Status | Requirement |
| :--- | :--- | :--- |
| **Tier 1** | Fully Supported | 100% conformance test pass rate, comprehensive documentation. |
| **Tier 2** | Actively Maintained | 80% conformance test pass rate, basic documentation. |
| **Tier 3** | Experimental | No minimum conformance requirement, partially implemented. |

### SDK Availability
- **Tier 1**: TypeScript, Python, C#, Go.
- **Tier 2**: Java, Rust.
- **Tier 3**: Swift, Ruby, PHP, Kotlin.

Sources: [docs/docs/sdk.mdx:10-21](), [docs/community/sdk-tiers.mdx:33-42]()

## Notable Client Implementations

### Desktop Applications
- **Claude Desktop**: Supports local MCP servers via `stdio` transport. [docs/docs/develop/build-server.mdx:6-7]()
- **Goose**: An open-source AI agent with built-in support for MCP Apps. [blog/content/posts/2026-01-26-mcp-apps.md:166-166]()

### IDE Extensions
- **Visual Studio Code**: Supports MCP Apps in Insiders builds and integrates MCP servers via GitHub Copilot. [docs/extensions/client-matrix.mdx:38-38]()
- **Cursor**: Supports MCP tools in Cursor Composer and interactive extensions. [docs/extensions/client-matrix.mdx:44-44]()

### Web Platforms
- **Claude.ai**: Supports remote MCP servers via Streamable HTTP and renders MCP Apps. [blog/content/posts/2026-01-26-mcp-apps.md:165-165]()
- **ChatGPT**: Supports remote MCP servers and interactive UI components. [blog/content/posts/2026-01-26-mcp-apps.md:169-169]()
- **Microsoft 365 Copilot**: Supports MCP Apps for interactive conversation interfaces. [docs/extensions/client-matrix.mdx:39-39]()

## Client Integration Patterns

Clients typically connect to servers using one of two transport layers:
1. **Stdio Transport**: Used for local processes. The client spawns the server as a child process and communicates via standard input/output. [docs/docs/learn/architecture.mdx:97-98]()
2. **Streamable HTTP Transport**: Used for remote servers. The client communicates via HTTP POST for requests and receives updates via Server-Sent Events (SSE). [docs/docs/learn/architecture.mdx:99-99]()

### Code Entity Bridge: Python Client Implementation
This diagram maps the natural language "Connect to Server" flow to the specific classes and methods used in the `mcp-python-sdk`.

```mermaid
sequenceDiagram
    participant App as "MCPClient (client.py)"
    participant SDK as "mcp.client.stdio"
    participant Session as "ClientSession (mcp.session)"

    App->>SDK: calls stdio_client(StdioServerParameters)
    SDK-->>App: returns (read_stream, write_stream)
    App->>Session: initializes ClientSession(read_stream, write_stream)
    App->>Session: session.initialize()
    Session-->>App: returns InitializeResult
    App->>Session: session.list_tools()
    Session-->>App: returns ListToolsResult
```
Sources: [docs/docs/develop/build-client.mdx:114-156]()

### Extension Negotiation
Clients and servers negotiate capabilities during the initialization handshake. Extensions like `io.modelcontextprotocol/ui` (Apps) or `io.modelcontextprotocol/tasks` (Tasks) are opt-in.

```mermaid
sequenceDiagram
    participant Client as "MCP Client"
    participant Server as "MCP Server"

    Client->>Server: initialize (capabilities: { extensions: { "io.modelcontextprotocol/ui": {} } })
    Server-->>Client: initialize response (capabilities: { extensions: { "io.modelcontextprotocol/ui": {} } })
    Note over Client,Server: Extension enabled for session
```
Sources: [docs/extensions/client-matrix.mdx:16-17](), [docs/extensions/tasks/overview.mdx:50-52]()

For details on configuration and environment setup, see [Client Integration Patterns](#4.2).

---

# Page: Client Directory and Feature Matrix

# Client Directory and Feature Matrix

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [blog/content/posts/2026-01-26-mcp-apps.md](blog/content/posts/2026-01-26-mcp-apps.md)
- [docs/community/sdk-tiers.mdx](docs/community/sdk-tiers.mdx)
- [docs/docs/getting-started/intro.mdx](docs/docs/getting-started/intro.mdx)
- [docs/docs/tools/debugging.mdx](docs/docs/tools/debugging.mdx)
- [docs/extensions/apps/build.mdx](docs/extensions/apps/build.mdx)
- [docs/extensions/apps/overview.mdx](docs/extensions/apps/overview.mdx)
- [docs/extensions/auth/oauth-client-credentials.mdx](docs/extensions/auth/oauth-client-credentials.mdx)
- [docs/extensions/auth/overview.mdx](docs/extensions/auth/overview.mdx)
- [docs/extensions/client-matrix.mdx](docs/extensions/client-matrix.mdx)
- [docs/extensions/overview.mdx](docs/extensions/overview.mdx)
- [docs/extensions/tasks/overview.mdx](docs/extensions/tasks/overview.mdx)

</details>



## Purpose and Scope

This page catalogs known MCP client implementations and documents their supported features through a standardized feature matrix. It serves as a technical reference for understanding which MCP capabilities (Resources, Prompts, Tools, Sampling, Tasks, etc.) each client supports. This directory enables users to identify compatible clients for their specific infrastructure and allows developers to understand the implementation landscape of the Model Context Protocol.

For integration guides, see [Client Integration Patterns](4.2). For protocol message details, see [Protocol Specification](2).

## Feature Categories and Badge System

The MCP ecosystem uses a standardized badge system to categorize client support levels. These features are defined in the documentation and implemented via capability negotiation during the protocol handshake [docs/community/sdk-tiers.mdx:23-26]().

| Feature Category | Features | Color | Purpose |
|:---|:---|:---|:---|
| **Server Features** | Resources, Prompts, Tools | Blue | Core server-provided primitives consumed by the client. |
| **Client Features** | Sampling, Roots, Elicitation | Green | Capabilities provided by the client that servers can request. |
| **Discovery** | Discovery, Instructions | Purple | Dynamic capability updates and LLM guidance. |
| **Authorization** | CIMD, DCR | Yellow | Identity and registration mechanisms (OAuth 2.1). |
| **Advanced** | Tasks, Apps | Orange | Long-running operations and interactive UI extensions. |

### Feature Definitions in Code
*   **Sampling**: Allows servers to request LLM completions through the client, placing the client in control of security [docs/community/sdk-tiers.mdx:23-24]().
*   **Roots**: Defines filesystem boundaries (using `file://` URIs) for server operations.
*   **Elicitation**: Enables servers to request specific information from users via structured JSON schemas [docs/community/sdk-tiers.mdx:23-24]().
*   **MCP Apps**: An official extension (`io.modelcontextprotocol/ui`) allowing tools to return interactive HTML interfaces [docs/extensions/client-matrix.mdx:28-28]().
*   **Tasks**: An experimental extension (`io.modelcontextprotocol/tasks`) for long-running operations with polling and mid-flight input [docs/extensions/tasks/overview.mdx:50-58]().

## Client Capability Negotiation

When an MCP client connects to a server, it must perform an initialization handshake. The client declares its supported features within the `ClientCapabilities` object. For extensions, both client and server must declare support in the `extensions` field during this handshake [docs/extensions/overview.mdx:116-118]().

### Handshake Data Flow
The following diagram maps the natural language "Capability Negotiation" to the specific code entities and message flow used during connection establishment.

**Handshake and Capability Mapping**
```mermaid
sequenceDiagram
    participant Host as "MCP Host (App)"
    participant Client as "ClientSession / Client"
    participant Server as "Server (JSON-RPC)"

    Note over Host,Client: Client instantiation
    Host->>Client: new Client({name, version}, {capabilities})
    
    Note over Client,Server: ClientCapabilities (JSON-RPC)
    Client->>Server: initialize request { capabilities: { extensions: { "io.modelcontextprotocol/tasks": {} } } }
    
    Note over Server,Client: ServerCapabilities
    Server-->>Client: initialize response { capabilities: { tools, resources, prompts } }
    
    Note over Client,Host: Connection Ready
    Client->>Host: client.connect(transport)
```
Sources: [docs/extensions/overview.mdx:116-133](), [docs/extensions/tasks/overview.mdx:158-170](), [docs/extensions/auth/oauth-client-credentials.mdx:195-217]()

## Support Matrix: Official Extensions

Beyond core protocol features, clients are increasingly adopting official extensions. Support is tracked for `MCP Apps` and `OAuth` variations. Extensions are always opt-in [docs/extensions/client-matrix.mdx:16-16]().

| Client | [MCP Apps](https://apps.extensions.modelcontextprotocol.io) (`ui`) | [OAuth Client Credentials](https://github.com/modelcontextprotocol/ext-auth) | [Enterprise Auth](https://github.com/modelcontextprotocol/ext-auth) |
|:---|:---:|:---:|:---:|
| Claude (Web & Desktop) | ✅ | | |
| VS Code GitHub Copilot | ✅ | | |
| Microsoft 365 Copilot | ✅ | | |
| ChatGPT | ✅ | | |
| Cursor | ✅ | | |
| Goose | ✅ | | |
| Postman | ✅ | | |
| MCPJam | ✅ | | |
| Archestra.AI | ✅ | | ✅ |
| PostHog Code | ✅ | | |

Sources: [docs/extensions/client-matrix.mdx:34-47](), [blog/content/posts/2026-01-26-mcp-apps.md:163-170]()

## Notable Client Implementations

### AI Assistants and IDEs
*   **Claude Desktop**: A primary host for local MCP servers. It supports Tools, Resources, Prompts, and the `MCP Apps` extension [blog/content/posts/2026-01-26-mcp-apps.md:165-165](). It uses the `stdio` transport for local servers [docs/docs/tools/debugging.mdx:92-94]().
*   **VS Code**: Supports `MCP Apps` in Insiders builds [blog/content/posts/2026-01-26-mcp-apps.md:167-168]().
*   **Goose**: An open-source agent supporting `MCP Apps` and providing tutorials for building them [blog/content/posts/2026-01-26-mcp-apps.md:166-166]().

### Frameworks as Clients
*   **SDK-based Clients**: Developers can build custom clients using Tier 1 SDKs. For example, the TypeScript SDK provides `ClientCredentialsProvider` for automated auth [docs/extensions/auth/oauth-client-credentials.mdx:202-205]().

## Technical Implementation: MCP Apps

The `MCP Apps` feature is the first official extension to move beyond text-based interaction. It utilizes the `ui://` URI scheme and a `_meta.ui.resourceUri` field in tool descriptions [blog/content/posts/2026-01-26-mcp-apps.md:62-68]().

### App Communication Flow
This diagram associates the UI interaction with the underlying protocol methods and classes.

**MCP App Interaction Model**
```mermaid
graph TD
    subgraph "Client Space (Host)"
        A["App (@modelcontextprotocol/ext-apps)"]
        H["ClientSession / Host"]
    end

    subgraph "Server Space"
        S["MCP Server"]
    end

    A -- "app.callServerTool()" --> H
    H -- "tools/call" --> S
    S -- "_meta.ui.resourceUri (ui://...)" --> H
    H -- "postMessage (JSON-RPC)" --> A
    A -- "app.updateModelContext()" --> H
```
Sources: [blog/content/posts/2026-01-26-mcp-apps.md:64-84](), [blog/content/posts/2026-01-26-mcp-apps.md:109-129](), [docs/extensions/apps/overview.mdx:77-96]()

## SDK Tiers and Feature Completeness

The level of feature support in a client often depends on the underlying SDK tier. Tier 1 SDKs are fully supported with complete protocol implementation [docs/community/sdk-tiers.mdx:23-24]().

| Tier | Conformance Requirement | Feature Support |
|:---|:---|:---|
| **Tier 1** | 100% Pass Rate | Full protocol including optional capabilities like Sampling and Elicitation. |
| **Tier 2** | 80% Pass Rate | Actively maintained, working toward full specification support. |
| **Tier 3** | No Minimum | Experimental, partially implemented, or specialized. |

Sources: [docs/community/sdk-tiers.mdx:33-42](), [docs/community/sdk-tiers.mdx:65-67]()

## Summary of Client Transports

Clients connect to servers using two primary transport layers:

1.  **Stdio Transport**: Standard for local desktop integrations (Claude Desktop, IDEs). Logs to `stderr` are captured for debugging [docs/docs/tools/debugging.mdx:31-34]().
2.  **Streamable HTTP Transport**: Used for remote/web integrations. Supports `Mcp-Session-Id` headers and Server-Sent Events (SSE) [docs/docs/tools/debugging.mdx:43-49]().

Sources: [docs/docs/tools/debugging.mdx:20-22](), [docs/docs/tools/debugging.mdx:43-49]()

---

# Page: Client Integration Patterns

# Client Integration Patterns

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/docs/develop/build-client.mdx](docs/docs/develop/build-client.mdx)
- [docs/docs/develop/build-server.mdx](docs/docs/develop/build-server.mdx)
- [docs/docs/develop/build-with-agent-skills.mdx](docs/docs/develop/build-with-agent-skills.mdx)
- [docs/docs/develop/clients/client-best-practices.mdx](docs/docs/develop/clients/client-best-practices.mdx)
- [docs/docs/develop/connect-local-servers.mdx](docs/docs/develop/connect-local-servers.mdx)
- [docs/docs/develop/connect-remote-servers.mdx](docs/docs/develop/connect-remote-servers.mdx)
- [docs/docs/learn/architecture.mdx](docs/docs/learn/architecture.mdx)
- [docs/docs/learn/client-concepts.mdx](docs/docs/learn/client-concepts.mdx)
- [docs/docs/learn/server-concepts.mdx](docs/docs/learn/server-concepts.mdx)
- [docs/docs/sdk.mdx](docs/docs/sdk.mdx)
- [docs/images/claude-add-files-connectors-and-more.png](docs/images/claude-add-files-connectors-and-more.png)
- [docs/images/claude-desktop-hamburger-menu-icon.png](docs/images/claude-desktop-hamburger-menu-icon.png)
- [docs/images/programmatic-tool-calling.svg](docs/images/programmatic-tool-calling.svg)
- [docs/images/progressive-discovery.svg](docs/images/progressive-discovery.svg)
- [docs/images/quickstart-remote/4-select-resources-menu.png](docs/images/quickstart-remote/4-select-resources-menu.png)
- [docs/images/quickstart-remote/5-select-prompts-resources.png](docs/images/quickstart-remote/5-select-prompts-resources.png)
- [docs/images/quickstart-remote/6-configure-tools.png](docs/images/quickstart-remote/6-configure-tools.png)
- [docs/images/quickstart-tools.png](docs/images/quickstart-tools.png)

</details>



## Purpose and Scope

This page documents how MCP servers integrate with various client applications. It covers configuration patterns, transport selection, capability negotiation, and client-specific setup procedures. This material focuses on the practical integration of MCP servers into existing client applications like Claude Desktop, IDEs, and custom implementations.

For information about the MCP client implementations themselves, see [Available SDKs and Language Support](#6.2). For details about building MCP servers, see [Building MCP Servers](#5.1).

## Overview of Client Integration

MCP clients are instantiated by host applications (like Claude Desktop or an IDE) to communicate with particular MCP servers [docs/docs/learn/client-concepts.mdx:6-9](). The host application manages the user experience, while the client handles protocol-level communication [docs/docs/learn/client-concepts.mdx:8-9]().

### Bridging Natural Language to Code Entities: Client Architecture
The following diagram illustrates how the conceptual "MCP Host" maps to specific code entities and transport implementations within the SDKs.

```mermaid
graph TB
    subgraph "MCP Host (AI Application)"
        direction TB
        Host["Host (e.g., Visual Studio Code)"]
        Client1["ClientSession (Client 1)"]
        Client2["ClientSession (Client 2)"]
    end
    
    subgraph "Transport Implementations"
        direction LR
        StdioTransport["stdio_client / StdioServerParameters"]
        HttpTransport["Streamable HTTP / SSE"]
    end
    
    subgraph "MCP Servers"
        ServerA["Local Server (Process)"]
        ServerC["Remote Server (Network)"]
    end
    
    Host -->|"instantiates"| Client1
    Host -->|"instantiates"| Client2
    
    Client1 -->|"uses"| StdioTransport
    Client2 -->|"uses"| HttpTransport
    
    StdioTransport ---|"STDIO Stream"| ServerA
    HttpTransport ---|"POST + SSE"| ServerC
```
Sources: [docs/docs/learn/architecture.mdx:31-61](), [docs/docs/develop/build-client.mdx:106-148]()

## Configuration Patterns

### Local Server Configuration (STDIO)
Most desktop clients use a JSON configuration file to define local MCP servers. The configuration typically includes a friendly name, a command to execute, and an array of arguments [docs/docs/develop/connect-local-servers.mdx:130-139]().

**Example: `claude_desktop_config.json`**
```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "/Users/username/Desktop"
      ],
      "env": {
        "CUSTOM_VAR": "value"
      }
    }
  }
}
```
Sources: [docs/docs/develop/connect-local-servers.mdx:94-108](), [docs/docs/tools/debugging.mdx:132-146]()

### Remote Server Configuration (HTTP)
Remote servers are connected via URLs. In clients like Claude.ai, these are added as "Custom Connectors" [docs/docs/develop/connect-remote-servers.mdx:16-18](). The URL must include the protocol (https://) and any necessary path components [docs/docs/develop/connect-remote-servers.mdx:54-55]().

## Transport Selection and Setup

### STDIO Transport (Local)
Used for direct process communication on the same machine [docs/docs/learn/architecture.mdx:97-99](). 
- **Implementation**: In the Python SDK, this is handled via `stdio_client` using `StdioServerParameters` to define the command and arguments [docs/docs/develop/build-client.mdx:140-146]().
- **Best Practice**: Servers must never write to `stdout` for logging, as it corrupts JSON-RPC messages. Use `stderr` or a logging library [docs/docs/develop/build-server.mdx:48-55]().

### Streamable HTTP Transport (Remote)
Used for internet-hosted services, enabling access to cloud APIs and multi-user deployments [docs/docs/develop/build-with-agent-skills.mdx:62-66]().
- **Implementation**: Uses HTTP POST for client-to-server messages and Server-Sent Events (SSE) for server-to-client streaming [docs/docs/learn/architecture.mdx:98-101]().
- **Authentication**: Remote servers commonly use OAuth, API keys, or username/password combinations [docs/docs/develop/connect-remote-servers.mdx:68-69]().

## Capability Negotiation

During the `initialize` request, the client and server exchange "Capabilities" to determine supported features [docs/docs/learn/architecture.mdx:111-115]().

### Bridging Capabilities to Code Primitives
The following diagram maps protocol capabilities to the underlying SDK methods and UI concepts.

```mermaid
graph LR
    subgraph "Client Features (ClientSession)"
        Sampling["sampling (Sampling)"]
        Roots["roots (Roots)"]
        Elicit["elicitation (elicitation/create)"]
    end

    subgraph "Initialization Handshake"
        InitReq["initialize() Request"]
        InitRes["initialize() Response"]
    end

    subgraph "Server Features (FastMCP / McpServer)"
        Tools["tools (tools/list, tools/call)"]
        Resources["resources (resources/list, resources/read)"]
        Prompts["prompts (prompts/list, prompts/get)"]
    end

    Sampling --> InitReq
    Roots --> InitReq
    Elicit --> InitReq
    
    InitReq --> InitRes
    
    Tools --> InitRes
    Resources --> InitRes
    Prompts --> InitRes
```
Sources: [docs/docs/learn/client-concepts.mdx:14-18](), [docs/docs/learn/server-concepts.mdx:14-18](), [docs/docs/develop/build-client.mdx:150-156]()

### Progressive Discovery
Clients implement progressive discovery by showing visual indicators only after a successful connection [docs/docs/develop/connect-local-servers.mdx:152-168]().
- **Tool Browsing**: Users can view available tools in a "Manage connectors" or "Add files" menu [docs/docs/develop/connect-local-servers.mdx:161-168]().
- **Dynamic Updates**: Roots can be updated dynamically with `roots/list_changed` notifications [docs/docs/learn/client-concepts.mdx:122-123]().

## Client-Specific Integration Patterns

### Claude Desktop
- **Config Location (macOS)**: `~/Library/Application Support/Claude/claude_desktop_config.json` [docs/docs/develop/connect-local-servers.mdx:84]()
- **Config Location (Windows)**: `%APPDATA%\Claude\claude_desktop_config.json` [docs/docs/develop/connect-local-servers.mdx:85]()
- **Usage**: Claude requires explicit approval for each tool execution [docs/docs/develop/connect-local-servers.mdx:46-47]().

### Web Clients (Claude.ai)
- **Mechanism**: Connect via "Custom Connectors" in the browser settings [docs/docs/develop/connect-remote-servers.mdx:34-36]().
- **Auth Flow**: Users follow authentication prompts provided by the server, which may redirect to third-party providers [docs/docs/develop/connect-remote-servers.mdx:77-78]().

## Debugging and Testing Tools

### MCP Inspector
The Inspector is the primary tool for testing servers before integrating them with a full host application [docs/docs/tools/inspector.mdx:6-7]().
- **Usage**: `npx @modelcontextprotocol/inspector <command> <args>` [docs/docs/tools/inspector.mdx:15-16]().
- **Features**: Supports testing `tools/call`, `resources/read`, and `prompts/get` interactively [docs/docs/tools/inspector.mdx:91-110]().

### Common Integration Issues
1. **Working Directory**: Clients may launch servers with an undefined working directory; always use absolute paths in configs [docs/docs/tools/debugging.mdx:98-107]().
2. **STDIO Corruption**: Writing to `stdout` (e.g., via `print()`) breaks the JSON-RPC stream [docs/docs/develop/build-server.mdx:48-50]().
3. **Environment Variables**: Servers launched via stdio inherit a limited environment; explicit `env` configuration is often required for API keys or custom paths [docs/docs/tools/debugging.mdx:129-146]().

Sources: [docs/docs/tools/debugging.mdx:90-185](), [docs/docs/tools/inspector.mdx:8-20](), [docs/docs/develop/build-server.mdx:48-55]()

---

# Page: Server Development

# Server Development

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/docs/develop/build-client.mdx](docs/docs/develop/build-client.mdx)
- [docs/docs/develop/build-server.mdx](docs/docs/develop/build-server.mdx)
- [docs/docs/develop/build-with-agent-skills.mdx](docs/docs/develop/build-with-agent-skills.mdx)
- [docs/docs/learn/architecture.mdx](docs/docs/learn/architecture.mdx)
- [docs/docs/learn/client-concepts.mdx](docs/docs/learn/client-concepts.mdx)
- [docs/docs/learn/server-concepts.mdx](docs/docs/learn/server-concepts.mdx)
- [docs/docs/sdk.mdx](docs/docs/sdk.mdx)
- [docs/examples.mdx](docs/examples.mdx)

</details>



MCP servers are lightweight, domain-focused programs that expose specific capabilities—tools, resources, and prompts—to AI applications through a standardized protocol. This page introduces the server development ecosystem, the philosophy of composable servers, and guides you to detailed implementation resources.

The MCP server ecosystem has grown significantly, with thousands of servers available in the community alongside official integrations from companies like Notion, Stripe, GitHub, Hugging Face, and Postman.

For client-side development, see [Client Ecosystem](#4).

## Server Development Philosophy

MCP servers follow a **domain-focused, composable** design philosophy:

*   **Domain-Focused**: Each server specializes in a specific domain or service rather than attempting to provide general-purpose functionality. For example, a weather server focuses solely on weather data [docs/docs/develop/build-server.mdx:10-10](), while a filesystem server provides file operations within specified boundaries [docs/docs/develop/build-server.mdx:26-26]().
*   **Composable**: Servers are designed to work together, allowing AI applications to combine multiple specialized servers to accomplish complex tasks. A host application coordinates multiple clients, each handling one direct communication with one server [docs/docs/learn/client-concepts.mdx:6-8]().

This approach reduces complexity, improves maintainability, and enables rapid ecosystem growth through specialization.

## The MCP Server Ecosystem

The server ecosystem consists of reference implementations, official integrations, and community servers.

**Server Ecosystem Structure:**

```mermaid
graph TB
    subgraph "Reference Servers"
        REF_EVERYTHING["Everything Server<br/>src/everything"]
        REF_FILESYSTEM["Filesystem Server<br/>src/filesystem"]
        REF_GIT["Git Server<br/>src/git"]
        REF_MEMORY["Memory Server<br/>src/memory"]
    end
    
    subgraph "Official Integrations"
        OFF_NOTION["Notion MCP Server"]
        OFF_STRIPE["Stripe MCP Server"]
        OFF_GITHUB["GitHub MCP Server"]
        OFF_HF["Hugging Face MCP"]
    end
    
    subgraph "SDK Layer"
        SDK_PYTHON["Python SDK<br/>FastMCP class<br/>mcp.server.fastmcp"]
        SDK_TS["TypeScript SDK<br/>McpServer class"]
        SDK_JAVA["Java SDK<br/>Spring Boot"]
        SDK_OTHER["Go, Kotlin, Swift<br/>C#, Ruby, Rust, PHP"]
    end
    
    REF_EVERYTHING --> SDK_TS
    REF_FILESYSTEM --> SDK_TS
    REF_GIT --> SDK_TS
    REF_MEMORY --> SDK_TS
    
    OFF_NOTION --> SDK_TS
    OFF_GITHUB --> SDK_TS
    OFF_HF --> SDK_PYTHON
    
    SDK_PYTHON --- SDK_TS
    SDK_TS --- SDK_JAVA
```

**Sources:** [docs/examples.mdx:8-34](), [docs/docs/sdk.mdx:10-21](), [docs/docs/develop/build-server.mdx:145-148]()

### Reference Servers

Official examples demonstrating protocol features and best practices. These servers serve as learning resources and SDK usage examples:

| Server | Purpose | SDK |
|--------|---------|-----|
| **Everything** | Reference server with prompts, resources, and tools | TypeScript |
| **Fetch** | Web content fetching and markdown conversion | TypeScript |
| **Filesystem** | Secure file operations with configurable access controls | TypeScript |
| **Git** | Tools to read, search, and manipulate Git repositories | TypeScript |
| **Memory** | Knowledge graph-based persistent memory system | TypeScript |
| **Sequential Thinking** | Dynamic problem-solving through thought sequences | TypeScript |
| **Time** | Time and timezone conversion capabilities | TypeScript |

See [Reference Server Implementations](#5.2) for detailed documentation.

**Sources:** [docs/examples.mdx:10-21]()

## Server Capabilities Overview

MCP servers provide functionality through three main building blocks [docs/docs/learn/server-concepts.mdx:12-18]():

| Feature | Control | Explanation | Example |
| :--- | :--- | :--- | :--- |
| **Tools** | Model | Functions the LLM can actively call to perform actions. | `searchFlights`, `sendEmail` |
| **Resources** | Application | Passive data sources providing read-only context. | `file:///docs/api.md`, `calendar://events` |
| **Prompts** | User | Pre-built instruction templates for specific tasks. | "Plan a vacation", "Summarize meetings" |

**Capability Decision Flow:**

```mermaid
graph TD
    START["Need to Expose Functionality"]
    
    Q1{"Does it<br/>perform actions<br/>or read data?"}
    Q2{"Should AI model<br/>decide when to use it?"}
    Q3{"Is it a<br/>parameterized<br/>template?"}
    
    TOOL["Implement as TOOL<br/>@mcp.tool() (Python)<br/>server.tool() (TS)"]
    RESOURCE["Implement as RESOURCE<br/>resources/read handler"]
    PROMPT["Implement as PROMPT<br/>prompts/get handler"]
    
    START --> Q1
    Q1 -->|"Performs actions"| Q2
    Q1 -->|"Reads data"| RESOURCE
    Q2 -->|"Yes"| TOOL
    Q2 -->|"No, user controls"| Q3
    Q3 -->|"Yes"| PROMPT
    Q3 -->|"No"| RESOURCE
```

For detailed capability implementation, see [Server Capabilities Deep Dive](#5.3).

**Sources:** [docs/docs/learn/server-concepts.mdx:12-18](), [docs/docs/develop/build-server.mdx:191-191]()

## Building Your First Server

### SDK Selection

MCP provides official SDKs in multiple languages, classified into tiers based on feature completeness [docs/docs/sdk.mdx:6-6]():

*   **Tier 1 (Core)**: TypeScript, Python, C#, Go [docs/docs/sdk.mdx:12-15]()
*   **Tier 2**: Java, Rust [docs/docs/sdk.mdx:16-17]()
*   **Tier 3**: Swift, Ruby, PHP, Kotlin [docs/docs/sdk.mdx:18-21]()

### Development Workflow

The typical server development process involves initializing the project, defining capabilities, and implementing handlers. Modern tools like **Agent Skills** (e.g., `build-mcp-server`) can guide AI coding assistants through design and implementation [docs/docs/develop/build-with-agent-skills.mdx:13-21]().

**Example: Weather Server Implementation (Python FastMCP)**

```python
# Initialize FastMCP server
from mcp.server.fastmcp import FastMCP
mcp = FastMCP("weather")

@mcp.tool()
async def get_forecast(latitude: float, longitude: float) -> str:
    """Get weather forecast for a location."""
    # Implementation logic here...
    return "Sunny"
```
[docs/docs/develop/build-server.mdx:145-212]()

See [Building MCP Servers](#5.1) for complete quickstart tutorials.

## Server Execution and Deployment

### Deployment Paths

Based on the use case, several deployment models are available:

| Path | Transport | Best For |
| :--- | :--- | :--- |
| **Local stdio** | `stdio` | Prototyping and local-only access (files, local processes) [docs/docs/develop/build-with-agent-skills.mdx:80-82](). |
| **MCP Bundles (MCPB)** | `stdio` | Distributing local servers with runtimes as single archives [docs/docs/develop/build-with-agent-skills.mdx:74-79](). |
| **Remote HTTP** | `Streamable HTTP` | Cloud APIs, OAuth flows, and multi-user deployments [docs/docs/develop/build-with-agent-skills.mdx:62-66](). |
| **MCP Apps** | `Streamable HTTP` | Servers requiring rich UI widgets in chat [docs/docs/develop/build-with-agent-skills.mdx:68-72](). |

### Critical Rule for STDIO
STDIO-based servers must **never** write to `stdout` for logging, as this corrupts JSON-RPC messages. Use `stderr` instead [docs/docs/develop/build-server.mdx:48-49]().

**Configuration Example (`claude_desktop_config.json`):**
```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/data"]
    }
  }
}
```
[docs/examples.mdx:61-85]()

## Testing and Debugging

### MCP Inspector

The [MCP Inspector](https://github.com/modelcontextprotocol/inspector) is the primary interactive tool for testing servers [docs/docs/learn/architecture.mdx:19-19]().

**Usage:**
```bash
npx @modelcontextprotocol/inspector <command> <args>
```

### Debugging in Claude Desktop

Claude Desktop provides logs for troubleshooting MCP connections:
*   **macOS**: `~/Library/Logs/Claude/mcp*.log`
*   **Windows**: `%APPDATA%\Claude\logs\mcp*.log`

Common issues include incorrect working directories, missing environment variables, and protocol version mismatches.

## Child Pages

*   [Building MCP Servers](#5.1) — Step-by-step guide to creating MCP servers, including quickstart tutorials and transport selection.
*   [Reference Server Implementations](#5.2) — Documentation of official reference servers as implementation examples.
*   [Server Capabilities Deep Dive](#5.3) — Detailed patterns for implementing Tools, Resources, Prompts, and Logging.
*   [Server Registry and Discovery](#5.4) — How to publish and discover servers in the MCP ecosystem.

**Sources:** [docs/docs/develop/build-server.mdx:1-400](), [docs/docs/learn/architecture.mdx:1-115](), [docs/docs/develop/build-with-agent-skills.mdx:6-83](), [docs/docs/sdk.mdx:1-51](), [docs/examples.mdx:1-92]()

---

# Page: Building MCP Servers

# Building MCP Servers

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/docs/develop/build-client.mdx](docs/docs/develop/build-client.mdx)
- [docs/docs/develop/build-server.mdx](docs/docs/develop/build-server.mdx)
- [docs/docs/develop/build-with-agent-skills.mdx](docs/docs/develop/build-with-agent-skills.mdx)
- [docs/docs/develop/connect-local-servers.mdx](docs/docs/develop/connect-local-servers.mdx)
- [docs/docs/develop/connect-remote-servers.mdx](docs/docs/develop/connect-remote-servers.mdx)
- [docs/docs/learn/architecture.mdx](docs/docs/learn/architecture.mdx)
- [docs/docs/learn/client-concepts.mdx](docs/docs/learn/client-concepts.mdx)
- [docs/docs/learn/server-concepts.mdx](docs/docs/learn/server-concepts.mdx)
- [docs/docs/sdk.mdx](docs/docs/sdk.mdx)
- [docs/images/claude-add-files-connectors-and-more.png](docs/images/claude-add-files-connectors-and-more.png)
- [docs/images/claude-desktop-hamburger-menu-icon.png](docs/images/claude-desktop-hamburger-menu-icon.png)
- [docs/images/quickstart-remote/4-select-resources-menu.png](docs/images/quickstart-remote/4-select-resources-menu.png)
- [docs/images/quickstart-remote/5-select-prompts-resources.png](docs/images/quickstart-remote/5-select-prompts-resources.png)
- [docs/images/quickstart-remote/6-configure-tools.png](docs/images/quickstart-remote/6-configure-tools.png)
- [docs/images/quickstart-tools.png](docs/images/quickstart-tools.png)

</details>



This guide covers the practical implementation patterns for building MCP servers. It demonstrates how to register tools, expose resources, define prompts, and handle client feature requests like sampling and elicitation.

For a complete tutorial building a weather server from scratch, see [Build an MCP Server](docs/docs/develop/build-server.mdx:1-4). For conceptual understanding of server capabilities, see [Understanding MCP Servers](docs/docs/learn/server-concepts.mdx:1-9). For SDK-specific APIs, see [SDK Reference](docs/docs/sdk.mdx:1-34).

## Server Implementation Overview

Building an MCP server involves implementing handlers for three core server capabilities and optionally supporting client features. The implementation pattern varies by SDK but follows the same conceptual flow.

### Implementation Flow Diagram

Title: MCP Server Lifecycle and Registration Flow
```mermaid
graph TB
    [START]("Initialize Server Instance")
    [REGISTER]("Register Capabilities")
    [TRANSPORT]("Configure Transport")
    [RUN]("Start Server")
    [HANDLE]("Handle Client Requests")
    
    [START] --> [REGISTER]
    [REGISTER] --> [TOOLS]("Register Tools<br/>@mcp.tool() or server.tool()")
    [REGISTER] --> [RESOURCES]("Register Resources<br/>server.resource() or handlers")
    [REGISTER] --> [PROMPTS]("Register Prompts<br/>server.prompt() or handlers")
    [TOOLS] --> [TRANSPORT]
    [RESOURCES] --> [TRANSPORT]
    [PROMPTS] --> [TRANSPORT]
    [TRANSPORT] --> [STDIO]("stdio transport<br/>StdioServerTransport")
    [TRANSPORT] --> [HTTP]("HTTP transport<br/>Streamable HTTP")
    [STDIO] --> [RUN]
    [HTTP] --> [RUN]
    [RUN] --> [HANDLE]
    [HANDLE] --> [TOOLCALL]("tools/call")
    [HANDLE] --> [RESREAD]("resources/read")
    [HANDLE] --> [PROMPTGET]("prompts/get")
```

**Code Entity Mapping:**

| Concept | TypeScript SDK | Python SDK | Java SDK |
|---------|---------------|------------|----------|
| Server Instance | `McpServer` or `Server` | `FastMCP` [docs/docs/develop/build-server.mdx:145-148]() | `McpServer` |
| Tool Registration | `server.tool()` | `@mcp.tool()` [docs/docs/develop/build-server.mdx:191-192]() | `McpServer.addTool()` |
| Resource Registration | `server.resource()` | `server.add_resource()` | `McpServer.addResource()` |
| Prompt Registration | `server.prompt()` | `server.add_prompt()` | `McpServer.addPrompt()` |
| stdio Transport | `StdioServerTransport` | `stdio_client` [docs/docs/develop/build-client.mdx:107-107]() | `StdioServerTransport` |

Sources: [docs/docs/develop/build-server.mdx:138-156](), [docs/docs/develop/build-client.mdx:101-121](), [docs/docs/sdk.mdx:8-21]()

## Registering Tools

Tools are the primary mechanism for MCP servers to expose executable functionality to clients. Tool registration involves defining the tool's input schema and implementing its execution logic.

### Python Tool Registration Pattern

The Python SDK provides the `FastMCP` class which uses Python type hints and docstrings to automatically generate tool definitions [docs/docs/develop/build-server.mdx:155-156]().

```python
# Using FastMCP decorator pattern
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("weather")

@mcp.tool()
async def get_forecast(latitude: float, longitude: float) -> str:
    """Get weather forecast for a location.
    
    Args:
        latitude: Latitude of the location
        longitude: Longitude of the location
    """
    # Tool implementation
    return forecast_data
```

The `@mcp.tool()` decorator automatically:
- Extracts the input schema from type hints [docs/docs/develop/build-server.mdx:155-156]().
- Uses the docstring for tool description [docs/docs/develop/build-server.mdx:155-156]().
- Registers the tool with the server [docs/docs/develop/build-server.mdx:191-192]().

Sources: [docs/docs/develop/build-server.mdx:145-156](), [docs/docs/develop/build-server.mdx:191-197]()

### Tool Result Format

Tools enable AI models to perform actions. Each tool defines a specific operation with typed inputs and outputs [docs/docs/learn/server-concepts.mdx:24-25](). MCP uses JSON Schema for validation [docs/docs/learn/server-concepts.mdx:28-29]().

**Protocol operations:**

| Method | Purpose | Returns |
| :--- | :--- | :--- |
| `tools/list` | Discover available tools | Array of tool definitions with schemas [docs/docs/learn/server-concepts.mdx:34-34]() |
| `tools/call` | Execute a specific tool | Tool execution result [docs/docs/learn/server-concepts.mdx:35-35]() |

Sources: [docs/docs/learn/server-concepts.mdx:32-35]()

## Exposing Resources

Resources provide read-only access to data sources. Applications can access this information directly and decide how to use it [docs/docs/learn/server-concepts.mdx:99-101]().

### Resource Interaction and Data Flow

Title: Resource Interaction and Data Flow
```mermaid
sequenceDiagram
    participant Client
    participant Server
    participant DataSource["Data Source<br/>(File, DB, API)"]
    
    Note over Client,Server: Resource Discovery
    Client->>Server: "resources/list"
    Server-->>Client: "List of resource URIs"
    
    Note over Client,Server: Resource Access
    Client->>Server: "resources/read {uri}"
    Server->>DataSource: "Fetch data"
    DataSource-->>Server: "Raw data"
    Server->>Server: "Format with MIME type"
    Server-->>Client: "Resource content + metadata"
    
    Note over Client,Server: Change Notifications (Optional)
    Client->>Server: "resources/subscribe {uri}"
    Server-->>Client: "Subscription confirmed"
    DataSource-->>Server: "Data changed"
    Server->>Client: "resources/updated notification"
```

### Resource Discovery Patterns

Resources support two discovery patterns [docs/docs/learn/server-concepts.mdx:104-105]():
- **Direct Resources**: Fixed URIs pointing to specific data (e.g., `calendar://events/2024`) [docs/docs/learn/server-concepts.mdx:106-106]().
- **Resource Templates**: Dynamic URIs with parameters for flexible queries (e.g., `travel://activities/{city}/{category}`) [docs/docs/learn/server-concepts.mdx:107-108]().

Sources: [docs/docs/learn/server-concepts.mdx:104-110](), [docs/docs/learn/server-concepts.mdx:115-120]()

## Defining Prompts

Prompts are pre-built instruction templates that tell the model to work with specific tools and resources [docs/docs/learn/server-concepts.mdx:18-18]().

### Prompt Structure and Generation

Title: Prompt Template Resolution
```mermaid
graph TB
    [DEFINE]("Define Prompt Template")
    [ARGS]("Specify Arguments<br/>(name, type, description)")
    [REGISTER]("Register with Server<br/>server.prompt()")
    
    [CLIENT_REQUEST]("Client: prompts/get")
    [VALIDATE]("Validate Arguments")
    [GENERATE]("Generate Messages")
    [RETURN]("Return Message Array")
    
    [DEFINE] --> [ARGS]
    [ARGS] --> [REGISTER]
    
    [CLIENT_REQUEST] --> [VALIDATE]
    [VALIDATE] --> [GENERATE]
    [GENERATE] --> [RETURN]
```

Sources: [docs/docs/learn/server-concepts.mdx:18-18](), [docs/docs/learn/architecture.mdx:87-90]()

## Handling Client Features

MCP clients can provide features to servers to build richer interactions [docs/docs/learn/client-concepts.mdx:10-12]().

### Sampling: Requesting LLM Completions

Sampling allows servers to request LLM completions through the client, enabling an agentic workflow [docs/docs/learn/client-concepts.mdx:18-18]().

Title: Sampling Request and Approval Flow
```mermaid
sequenceDiagram
    participant Server
    participant Client  
    participant LLM
    participant User
    
    Note over Server,Client: Server initiates sampling
    Server->>Client: "sampling/createMessage"
    
    Note over Client,User: Human interaction
    Client->>User: Present request for approval
    User-->>Client: Approve/Modify/Decline
    
    Note over Client,LLM: Execute sampling
    Client->>LLM: Generate completion
    LLM-->>Client: Return response
    
    Note over Server,Client: Return to server
    Client-->>Server: Return LLM response
```

Sources: [docs/docs/learn/client-concepts.mdx:18-18](), [docs/docs/learn/architecture.mdx:89-89]()

### Elicitation: Requesting User Input

Elicitation enables servers to request specific information from users during interactions [docs/docs/learn/client-concepts.mdx:16-16]().

Title: Elicitation Information Gathering
```mermaid
sequenceDiagram
    participant User
    participant Client
    participant Server

    Note over Server,Client: Server initiates elicitation
    Server->>Client: "elicitation/create"

    Note over Client,User: Human interaction
    Client->>User: Present elicitation UI
    User-->>Client: Provide requested information

    Note over Server,Client: Complete request
    Client-->>Server: Return user response
```

Sources: [docs/docs/learn/client-concepts.mdx:30-47]()

## Transport Layer Selection

MCP supports two transport mechanisms [docs/docs/learn/architecture.mdx:96-97]():

| Transport | Use Case | Characteristics |
| :--- | :--- | :--- |
| **Stdio** | Local processes | Direct process communication via stdin/stdout [docs/docs/learn/architecture.mdx:98-98](). |
| **Streamable HTTP** | Remote servers | Uses HTTP POST for messages and SSE for streaming [docs/docs/learn/architecture.mdx:99-99](). |

### Critical Stdio Logging Rule
When implementing Stdio-based servers, **never write to stdout**. Writing to stdout will corrupt the JSON-RPC messages and break your server [docs/docs/develop/build-server.mdx:48-49](). Use `sys.stderr` or a logging library [docs/docs/develop/build-server.mdx:49-54]().

Sources: [docs/docs/learn/architecture.mdx:96-101](), [docs/docs/develop/build-server.mdx:45-70]()

## Deployment and Connectivity

### Local vs. Remote Deployment
Servers can be deployed locally or remotely. Local servers typically use the `stdio` transport and are launched by the host application [docs/docs/learn/architecture.mdx:63-68](). Remote servers use `Streamable HTTP` and allow multiple clients to connect over the internet [docs/docs/learn/architecture.mdx:33-33]().

### Connecting to Clients
- **Claude Desktop**: Configuration is handled via `claude_desktop_config.json` [docs/docs/develop/connect-local-servers.mdx:82-86]().
- **Custom Connectors**: Used to bridge Claude to remote MCP servers via a URL [docs/docs/develop/connect-remote-servers.mdx:16-18]().
- **MCP Bundles (MCPB)**: A method to package local servers with their runtime for easier installation [docs/docs/develop/build-with-agent-skills.mdx:74-78]().

Sources: [docs/docs/learn/architecture.mdx:33-71](), [docs/docs/develop/connect-local-servers.mdx:82-90](), [docs/docs/develop/connect-remote-servers.mdx:16-29](), [docs/docs/develop/build-with-agent-skills.mdx:74-78]()

---

# Page: Reference Server Implementations

# Reference Server Implementations

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/docs/develop/build-client.mdx](docs/docs/develop/build-client.mdx)
- [docs/docs/develop/build-server.mdx](docs/docs/develop/build-server.mdx)
- [docs/docs/develop/build-with-agent-skills.mdx](docs/docs/develop/build-with-agent-skills.mdx)
- [docs/docs/learn/architecture.mdx](docs/docs/learn/architecture.mdx)
- [docs/docs/learn/client-concepts.mdx](docs/docs/learn/client-concepts.mdx)
- [docs/docs/learn/server-concepts.mdx](docs/docs/learn/server-concepts.mdx)
- [docs/docs/sdk.mdx](docs/docs/sdk.mdx)
- [docs/examples.mdx](docs/examples.mdx)

</details>



## Purpose and Scope

This document provides comprehensive documentation of the official reference MCP server implementations maintained in the `modelcontextprotocol/servers` repository. These servers demonstrate core MCP features, SDK usage patterns, and best practices for building production-ready servers. Each reference server showcases different aspects of the protocol: tools, resources, prompts, and various integration patterns.

For information about building custom MCP servers, see [Building MCP Servers](#5.1). For initial setup and execution, see [Overview](#1).

**Sources:** [docs/examples.mdx:1-24](), [docs/docs/learn/architecture.mdx:13-21]()

## Reference Server Architecture

The reference servers follow a consistent architectural pattern across TypeScript and Python implementations. Each server provides a focused set of capabilities demonstrating specific MCP features.

**Repository Structure and Package Distribution**

```mermaid
graph TB
    subgraph "modelcontextprotocol/servers Repository"
        REPO["github.com/modelcontextprotocol/servers"]
        
        subgraph "src/ Directory - TypeScript Servers"
            EVERYTHING["src/everything/<br/>Package: @modelcontextprotocol/server-everything<br/>Test all protocol features"]
            FETCH["src/fetch/<br/>Package: @modelcontextprotocol/server-fetch<br/>Web content retrieval"]
            FILESYSTEM["src/filesystem/<br/>Package: @modelcontextprotocol/server-filesystem<br/>File operations with access control"]
            MEMORY["src/memory/<br/>Package: @modelcontextprotocol/server-memory<br/>Knowledge graph storage"]
            SEQUENTIAL["src/sequentialthinking/<br/>Package: @modelcontextprotocol/server-sequentialthinking<br/>Thought sequences"]
            TIME["src/time/<br/>Package: @modelcontextprotocol/server-time<br/>Time/timezone operations"]
        end
        
        subgraph "src/ Directory - Python Servers"
            GIT["src/git/<br/>Package: mcp-server-git<br/>Repository operations"]
        end
        
        REPO --> EVERYTHING
        REPO --> FETCH
        REPO --> FILESYSTEM
        REPO --> MEMORY
        REPO --> SEQUENTIAL
        REPO --> TIME
        REPO --> GIT
    end
    
    subgraph "Execution via Package Managers"
        NPX["npx -y<br/>Downloads and runs TypeScript servers<br/>No installation required"]
        UVX["uvx<br/>Downloads and runs Python servers<br/>Isolated environments"]
        PIP["pip install + python -m<br/>Traditional Python installation"]
    end
    
    subgraph "Client Integration Points"
        CLAUDE_CONFIG["claude_desktop_config.json<br/>mcpServers section"]
        STDIO["stdio transport<br/>stdin/stdout communication"]
    end
    
    EVERYTHING --> NPX
    FETCH --> NPX
    FILESYSTEM --> NPX
    MEMORY --> NPX
    SEQUENTIAL --> NPX
    TIME --> NPX
    
    GIT --> UVX
    GIT --> PIP
    
    NPX --> CLAUDE_CONFIG
    UVX --> CLAUDE_CONFIG
    PIP --> CLAUDE_CONFIG
    CLAUDE_CONFIG --> STDIO
```

**Sources:** [docs/examples.mdx:8-21](), [docs/examples.mdx:40-55]()

## Server Capability Matrix

The following table summarizes the capabilities exposed by each reference server:

| Server | Tools | Resources | Prompts | Primary Purpose |
|--------|-------|-----------|---------|-----------------|
| Everything | ✅ | ✅ | ✅ | Complete protocol test bed demonstrating all MCP features |
| Fetch | ✅ | ✅ | ❌ | Web content retrieval and conversion for LLM consumption |
| Filesystem | ✅ | ✅ | ❌ | Secure file operations with access control boundaries |
| Git | ✅ | ❌ | ❌ | Repository reading, searching, and manipulation |
| Memory | ✅ | ✅ | ❌ | Knowledge graph-based persistent storage system |
| Sequential Thinking | ✅ | ❌ | ❌ | Dynamic problem-solving through thought sequences |
| Time | ✅ | ❌ | ❌ | Time and timezone conversion operations |

**Sources:** [docs/examples.mdx:12-20](), [docs/docs/learn/server-concepts.mdx:10-18]()

## Everything Server

### Purpose
The Everything server serves as the comprehensive reference implementation and test bed for the MCP protocol. It demonstrates the complete feature set: tools, resources, and prompts in a single server implementation. This server is specifically designed for testing and validation rather than production use.

### Package Information
- **Package:** `@modelcontextprotocol/server-everything`
- **Execution:** `npx -y @modelcontextprotocol/server-everything`

### Capabilities Demonstrated
| Feature Type | What It Demonstrates |
|--------------|---------------------|
| **Tools** | Complete tool registration and execution patterns including input validation |
| **Resources** | Both direct resources and resource templates with URI-based access |
| **Prompts** | Prompt definition with parameter handling and completion |
| **Notifications** | Real-time notification patterns for capability changes |

**Sources:** [docs/examples.mdx:14]()

## Fetch Server

### Purpose
The Fetch server provides web content retrieval and conversion capabilities optimized for LLM consumption. It fetches web pages and converts HTML content into clean, LLM-friendly formats that maximize information density while minimizing token usage.

### Package Information
- **Package:** `@modelcontextprotocol/server-fetch`
- **Execution:** `npx -y @modelcontextprotocol/server-fetch`

### Capabilities
- **Web Fetching Tool**: Retrieves web page content via HTTP/HTTPS.
- **Content Conversion**: Converts HTML to clean markdown or plain text.
- **LLM Optimization**: Strips unnecessary HTML/CSS/JS while preserving semantic content.

**Sources:** [docs/examples.mdx:15]()

## Filesystem Server

### Purpose
The Filesystem server provides secure file operations with configurable access controls. It implements filesystem boundaries (roots) to prevent unauthorized access outside specified directories. This server demonstrates the MCP roots concept and secure file handling patterns.

### Package Information
- **Package:** `@modelcontextprotocol/server-filesystem`
- **Execution:** `npx -y @modelcontextprotocol/server-filesystem /path/to/allowed/files`

### Capabilities
| Tool | Purpose |
|------|---------|
| `read_file` | Read file contents |
| `write_file` | Write content to file |
| `list_directory` | List directory contents |
| `move_file` | Move/rename files |
| `search_files` | Search for files by pattern |
| `get_file_info` | Get file metadata |

### Security Model
The server enforces boundaries by only allowing operations within paths specified during startup. It uses the `file://` URI scheme for resource access.

**Sources:** [docs/examples.mdx:16](), [docs/docs/learn/client-concepts.mdx:106-121]()

## Git Server

### Purpose
The Git server provides comprehensive tools for reading, searching, and manipulating Git repositories. It enables LLMs to inspect repository structure, search commit history, and analyze code changes.

### Package Information
- **Package:** `mcp-server-git`
- **Execution:** `uvx mcp-server-git` or `pip install mcp-server-git`

### Capabilities
- **Repository Reading**: Clone repository, read file contents at specific commits.
- **Commit Analysis**: View commit history, show commit details, generate diffs.
- **Search Functions**: Search commits by message, author, or file changes.

**Sources:** [docs/examples.mdx:17](), [docs/examples.mdx:48-55]()

## Memory Server

### Purpose
The Memory server implements a knowledge graph-based persistent memory system. It allows LLMs to store and retrieve information across sessions, maintaining context and learned facts.

### Package Information
- **Package:** `@modelcontextprotocol/server-memory`
- **Execution:** `npx -y @modelcontextprotocol/server-memory`

### Knowledge Graph Architecture

```mermaid
graph TB
    subgraph "Memory Server Knowledge Graph"
        ENTITIES["Entities<br/>Nodes representing concepts"]
        RELATIONS["Relations<br/>Edges connecting entities"]
        OBSERVATIONS["Observations<br/>Facts about entities"]
        
        ENTITIES --> RELATIONS
        ENTITIES --> OBSERVATIONS
    end
    
    subgraph "Storage Operations"
        CREATE["create_entities tool"]
        RELATE["create_relations tool"]
        OBSERVE["add_observations tool"]
        SEARCH["search_nodes tool"]
    end
    
    subgraph "Persistence"
        STORAGE["Local filesystem storage<br/>JSON-based"]
    end
    
    CREATE --> ENTITIES
    RELATE --> RELATIONS
    OBSERVE --> OBSERVATIONS
    ENTITIES --> STORAGE
```

**Sources:** [docs/examples.mdx:18](), [docs/examples.mdx:43-44]()

## Sequential Thinking Server

### Purpose
The Sequential Thinking server provides dynamic and reflective problem-solving capabilities through structured thought sequences. It enables LLMs to break down complex problems into explicit reasoning steps.

### Package Information
- **Package:** `@modelcontextprotocol/server-sequentialthinking`
- **Execution:** `npx -y @modelcontextprotocol/server-sequentialthinking`

**Sources:** [docs/examples.mdx:19]()

## Time Server

### Purpose
The Time server provides time and timezone conversion capabilities, enabling LLMs to perform temporal calculations and timezone conversions accurately.

### Package Information
- **Package:** `@modelcontextprotocol/server-time`
- **Execution:** `npx -y @modelcontextprotocol/server-time`

**Sources:** [docs/examples.mdx:20]()

## Server Implementation Patterns

**TypeScript Server Implementation Pattern**

The TypeScript SDK provides a high-level `McpServer` class for registering capabilities.

```mermaid
graph TB
    subgraph "TypeScript Server Code Structure"
        TS_SERVER["new McpServer({<br/>  name: 'server-name',<br/>  version: '1.0.0'<br/>})"]
        TS_TOOLS["server.registerTool(<br/>  'tool_name',<br/>  { description, inputSchema },<br/>  async (params) => {...}<br/>)"]
        TS_RESOURCES["server.registerResource(<br/>  { uri, name, mimeType },<br/>  async () => {...}<br/>)"]
        TS_TRANSPORT["new StdioServerTransport()"]
        TS_CONNECT["await server.connect(transport)"]
        
        TS_SERVER --> TS_TOOLS
        TS_SERVER --> TS_RESOURCES
        TS_SERVER --> TS_CONNECT
        TS_TRANSPORT --> TS_CONNECT
    end
```

**Python Server Implementation Pattern (FastMCP)**

The Python SDK uses the `FastMCP` class which leverages decorators for capability registration.

```mermaid
graph TB
    subgraph "Python Server Code Structure"
        PY_MCP["mcp = FastMCP('server-name')"]
        PY_TOOLS["@mcp.tool()<br/>async def tool_name(param: str) -> str:<br/>    '''Tool docstring'''<br/>    return result"]
        PY_RESOURCES["@mcp.resource('uri://path')<br/>async def resource_name() -> str:<br/>    return content"]
        PY_RUN["mcp.run(transport='stdio')"]
        
        PY_MCP --> PY_TOOLS
        PY_MCP --> PY_RESOURCES
        PY_MCP --> PY_RUN
    end
```

**Sources:** [docs/docs/develop/build-server.mdx:144-159](), [docs/docs/develop/build-server.mdx:191-212]()

## Configuration with MCP Clients

### Claude Desktop Integration
Reference servers are configured through the `claude_desktop_config.json` file.

**Configuration file locations:**
- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

#### Multi-Server Example
```json
{
  "mcpServers": {
    "memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"]
    },
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "/Users/username/Desktop"
      ]
    },
    "git": {
      "command": "uvx",
      "args": ["mcp-server-git"]
    }
  }
}
```

**Sources:** [docs/examples.mdx:58-85]()

## Development and Testing

### Testing with MCP Inspector
The MCP Inspector provides interactive testing of server implementations by establishing a direct connection to the server process.

```bash
# Test a TypeScript server
npx @modelcontextprotocol/inspector node build/index.js

# Test a Python server
npx @modelcontextprotocol/inspector uvx mcp-server-git
```

**Sources:** [docs/docs/learn/architecture.mdx:19](), [docs/docs/develop/build-with-agent-skills.mdx:90-96]()

### Debugging Reference Servers
- **Logging**: When implementing STDIO-based servers, never write to `stdout` directly (e.g., using `print()` in Python without `file=sys.stderr`). Writing to `stdout` will corrupt the JSON-RPC message stream and break the server connection [docs/docs/develop/build-server.mdx:46-70]().
- **Environment Variables**: For servers requiring authentication (like GitHub or Git), ensure environment variables are correctly passed in the client configuration [docs/examples.mdx:76-82]().

**Sources:** [docs/docs/develop/build-server.mdx:44-70](), [docs/examples.mdx:76-82]()

---

# Page: Server Capabilities Deep Dive

# Server Capabilities Deep Dive

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/specification/draft/server/prompts.mdx](docs/specification/draft/server/prompts.mdx)
- [docs/specification/draft/server/resources.mdx](docs/specification/draft/server/resources.mdx)
- [docs/specification/draft/server/tools.mdx](docs/specification/draft/server/tools.mdx)
- [docs/specification/draft/server/utilities/caching.mdx](docs/specification/draft/server/utilities/caching.mdx)
- [docs/specification/draft/server/utilities/completion.mdx](docs/specification/draft/server/utilities/completion.mdx)
- [docs/specification/draft/server/utilities/pagination.mdx](docs/specification/draft/server/utilities/pagination.mdx)
- [schema/draft/examples/AudioContent/audio-wav-content.json](schema/draft/examples/AudioContent/audio-wav-content.json)
- [schema/draft/examples/CallToolRequestParams/get-weather-tool-call-params.json](schema/draft/examples/CallToolRequestParams/get-weather-tool-call-params.json)
- [schema/draft/examples/CallToolResult/invalid-tool-input-error.json](schema/draft/examples/CallToolResult/invalid-tool-input-error.json)
- [schema/draft/examples/CallToolResult/result-with-structured-content.json](schema/draft/examples/CallToolResult/result-with-structured-content.json)
- [schema/draft/examples/CallToolResult/result-with-unstructured-text.json](schema/draft/examples/CallToolResult/result-with-unstructured-text.json)
- [schema/draft/examples/CompleteResult/multiple-completion-values-with-more-available.json](schema/draft/examples/CompleteResult/multiple-completion-values-with-more-available.json)
- [schema/draft/examples/CompleteResult/single-completion-value.json](schema/draft/examples/CompleteResult/single-completion-value.json)
- [schema/draft/examples/EmbeddedResource/embedded-file-resource-with-annotations.json](schema/draft/examples/EmbeddedResource/embedded-file-resource-with-annotations.json)
- [schema/draft/examples/GetPromptResult/code-review-prompt.json](schema/draft/examples/GetPromptResult/code-review-prompt.json)
- [schema/draft/examples/ImageContent/image-png-content-with-annotations.json](schema/draft/examples/ImageContent/image-png-content-with-annotations.json)
- [schema/draft/examples/ResourceLink/file-resource-link.json](schema/draft/examples/ResourceLink/file-resource-link.json)
- [schema/draft/examples/ServerCapabilities/tools-list-changed-notifications.json](schema/draft/examples/ServerCapabilities/tools-list-changed-notifications.json)

</details>



This document provides detailed technical guidance for implementing MCP server capabilities. It covers the protocol message structures, data types, and implementation requirements for exposing tools, resources, prompts, and supporting features.

## Capability Negotiation

Servers declare their supported capabilities during the handshake. In the latest specification, this is managed via the `server/discover` method or the initial capability exchange, determining which protocol features the server can support during the session.

### ServerCapabilities Structure

The complete capability structure includes:

```typescript
interface ServerCapabilities {
  experimental?: { [key: string]: object };
  logging?: object;
  completions?: object;
  prompts?: {
    listChanged?: boolean;
  };
  resources?: {
    subscribe?: boolean;
    listChanged?: boolean;
  };
  tools?: {
    listChanged?: boolean;
  };
}
```

**Capability Declaration Flow:**

```mermaid
sequenceDiagram
    participant Client
    participant Server
    
    Client->>Server: "server/discover" request
    Note over Server: "Determine supported features"
    Server->>Client: "DiscoverResult" (capabilities: ServerCapabilities)
    Note over Client: "Client now knows which features<br/>to use for this session"
```

Sources: [docs/specification/draft/server/tools.mdx:46-57](), [docs/specification/draft/server/resources.mdx:40-72](), [docs/specification/draft/server/prompts.mdx:40-52](), [docs/specification/draft/server/utilities/caching.mdx:16-16]()

## Tools Capability

Tools enable servers to expose executable functions that can be invoked by language models. Tools are **model-controlled**, meaning the LLM decides when to call them based on the `inputSchema` provided by the server.

### Tool Discovery and Invocation

**Protocol Message Flow:**

```mermaid
sequenceDiagram
    participant LLM
    participant Client
    participant Server
    
    Note over Client,Server: Discovery
    Client->>Server: tools/list
    Server-->>Client: List of tools (name, inputSchema, title, description)
    
    Note over LLM,Server: Invocation
    LLM->>Client: Suggest tool_call(get_weather, {location: "New York"})
    Client->>Server: tools/call(name: "get_weather", arguments: {location: "New York"})
    Server-->>Client: CallToolResult (content: [...], isError: boolean)
    Client->>LLM: Forward result content
```

Sources: [docs/specification/draft/server/tools.mdx:7-10](), [docs/specification/draft/server/tools.mdx:79-172](), [docs/specification/draft/server/tools.mdx:251-275]()

### Tool Results and Content

Tool calls return a `CallToolResult` which can include multiple content blocks and optional structured data for programmatic use.

| Field | Type | Description |
|-------|------|-------------|
| `content` | `ContentBlock[]` | Array of text, image, or resource content. |
| `isError` | `boolean` | Indicates if the tool execution failed. |
| `structuredContent` | `object` | (Optional) Raw data for client processing. |

Sources: [docs/specification/draft/server/tools.mdx:156-172](), [schema/draft/examples/CallToolResult/result-with-structured-content.json:1-15]()

### Multi Round-Trip Tool Calls (MRTR)

If a tool requires additional user input (e.g., authentication or missing parameters), it returns an `InputRequiredResult`. The client then retries the call with `inputResponses`.

```mermaid
sequenceDiagram
    participant Client
    participant Server
    
    Client->>Server: tools/call (ID: 2, name: "get_weather")
    Note over Server: Needs GitHub Login
    Server-->>Client: InputRequiredResult (elicitation/create request)
    Note over Client: User provides "octocat"
    Client->>Server: tools/call (ID: 3, inputResponses: {github_login: ...}, requestState: "...")
    Server-->>Client: Final Tool Result (resultType: "complete")
```

Sources: [docs/specification/draft/server/tools.mdx:174-235]()

## Resources Capability

Resources allow servers to share data (files, DB schemas, etc.) that provide context. Resources are **application-driven**, meaning the host application decides when to include them based on user selection or heuristics.

### Resource Types and Discovery

Servers can expose static resources or dynamic **Resource Templates** using URI templates ([RFC 6570](https://datatracker.ietf.org/doc/html/rfc6570)).

| Method | Description |
|--------|-------------|
| `resources/list` | Returns a list of available URIs with metadata (mimeType, icons). |
| `resources/templates/list` | Returns parameterized URI templates like `file:///{path}`. |
| `resources/read` | Retrieves the content for a specific URI. |

Sources: [docs/specification/draft/server/resources.mdx:85-179](), [docs/specification/draft/server/resources.mdx:181-231]()

### Resource Subscriptions

If a server declares the `subscribe` capability, clients can listen for updates to specific URIs using the `subscriptions/listen` mechanism.

```mermaid
sequenceDiagram
    participant Client
    participant Server
    
    Client->>Server: subscriptions/listen (resourceSubscriptions filter)
    Server-->>Client: notifications/subscriptions/acknowledged
    Note over Server: Data at URI changes
    Server->>Client: notifications/resources/updated (uri)
    Client->>Server: resources/read (uri)
```

Sources: [docs/specification/draft/server/resources.mdx:232-261]()

## Prompts Capability

Prompts are structured message templates designed to be **user-controlled**, typically triggered via UI elements like slash commands.

### Prompt Content Composition

A `prompts/get` request returns a list of `PromptMessage` objects. Each message has a `role` ("user" or "assistant") and a `content` block.

**Content Block Hierarchy:**

```mermaid
graph TD
    ContentBlock["ContentBlock"]
    
    ContentBlock --> TextContent["TextContent<br/>{type: 'text', text: string}"]
    ContentBlock --> ImageContent["ImageContent<br/>{type: 'image', data: string, mimeType: string}"]
    ContentBlock --> ResourceLink["ResourceLink<br/>{type: 'resource_link', uri: string}"]
    ContentBlock --> EmbeddedResource["EmbeddedResource<br/>{type: 'resource', resource: ResourceContents}"]
```

Sources: [docs/specification/draft/server/prompts.mdx:207-250](), [schema/draft/examples/EmbeddedResource/embedded-file-resource-with-annotations.json:1-13]()

## Common Utilities

### Caching and Freshness

Servers provide caching hints to reduce redundant network traffic for list operations and resource reads.

- `ttlMs`: Hint specifying how long the client may consider the result fresh (analogous to HTTP `max-age`).
- `cacheScope`: `"public"` (shared across users) or `"private"` (specific to an authorization context).

**Cache Invalidation:** Notifications like `notifications/tools/list_changed` immediately **invalidate** cached entries regardless of the remaining TTL.

Sources: [docs/specification/draft/server/utilities/caching.mdx:11-26](), [docs/specification/draft/server/utilities/caching.mdx:41-109](), [docs/specification/draft/server/utilities/caching.mdx:123-145]()

### Completion API

The completion API provides suggestions for prompt arguments or resource template variables, enabling interactive user experiences like dropdowns.

```mermaid
sequenceDiagram
    participant Client
    participant Server
    
    Note over Client: User types 'py' for 'language' arg
    Client->>Server: completion/complete (ref: ref/prompt, argument: {name: 'language', value: 'py'})
    Server-->>Client: {values: ['python', 'pytorch', 'pyside'], hasMore: true}
```

Sources: [docs/specification/draft/server/utilities/completion.mdx:7-11](), [docs/specification/draft/server/utilities/completion.mdx:46-87](), [docs/specification/draft/server/utilities/completion.mdx:133-149]()

### Pagination

For large result sets, MCP uses an opaque cursor-based pagination model. Clients must not attempt to parse these cursors.

| Request Param | Response Field | Description |
|---------------|----------------|-------------|
| `cursor` | `nextCursor` | Opaque token used to fetch the next chunk of data. |

Sources: [docs/specification/draft/server/utilities/pagination.mdx:24-68](), [docs/specification/draft/server/utilities/pagination.mdx:83-91]()

---

# Page: Server Registry and Discovery

# Server Registry and Discovery

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [blog/archetypes/default.md](blog/archetypes/default.md)
- [blog/content/posts/2025-07-29-prompts-for-automation.md](blog/content/posts/2025-07-29-prompts-for-automation.md)
- [blog/content/posts/2025-07-31-governance-for-mcp.md](blog/content/posts/2025-07-31-governance-for-mcp.md)
- [blog/content/posts/2025-09-05-php-sdk.md](blog/content/posts/2025-09-05-php-sdk.md)
- [blog/content/posts/2025-09-08-mcp-registry-preview.md](blog/content/posts/2025-09-08-mcp-registry-preview.md)
- [blog/content/posts/2025-09-26-mcp-next-version-update.md](blog/content/posts/2025-09-26-mcp-next-version-update.md)
- [blog/content/posts/2025-11-03-using-server-instructions.md](blog/content/posts/2025-11-03-using-server-instructions.md)
- [blog/content/posts/2025-11-20-adopting-mcpb.md](blog/content/posts/2025-11-20-adopting-mcpb.md)
- [blog/content/posts/2025-11-21-mcp-apps.md](blog/content/posts/2025-11-21-mcp-apps.md)
- [blog/content/posts/2025-11-25-first-mcp-anniversary.md](blog/content/posts/2025-11-25-first-mcp-anniversary.md)
- [blog/content/posts/2025-11-28-sep-process-update.md](blog/content/posts/2025-11-28-sep-process-update.md)
- [blog/content/posts/welcome-to-mcp-blog.md](blog/content/posts/welcome-to-mcp-blog.md)
- [docs/registry/about.mdx](docs/registry/about.mdx)
- [docs/registry/github-actions.mdx](docs/registry/github-actions.mdx)
- [docs/registry/quickstart.mdx](docs/registry/quickstart.mdx)
- [docs/registry/registry-aggregators.mdx](docs/registry/registry-aggregators.mdx)

</details>



The MCP Registry is the authoritative centralized index for discovering and publishing Model Context Protocol servers. Launched in September 2024, the registry has scaled to nearly 2,000 entries, providing a standardized mechanism for server distribution, namespace management, and discovery across the ecosystem [blog/content/posts/2025-11-25-first-mcp-anniversary.md:35-36]().

This system allows developers to publish metadata about their servers—including installation commands, environment variables, and capabilities—enabling clients and aggregators to automatically configure and integrate them.

## The Registry Ecosystem

The MCP Registry operates as a "source of truth" metadata repository, distinct from the package registries (like npm or PyPI) that host the actual server binaries [docs/registry/about.mdx:34-38]().

```mermaid
graph TD
    subgraph "Registry Providers"
        REG["MCP Registry<br/>registry.modelcontextprotocol.io"]
        SUB["Private Sub-registries<br/>Enterprise-internal"]
        MARKET["Downstream Aggregators<br/>Marketplaces / Curation"]
    end

    subgraph "Data Consumers"
        CLIENT["MCP Host Applications<br/>Claude Desktop, IDEs"]
        CLI["CLI Tooling<br/>mcpb, npx, uvx"]
    end

    subgraph "Code Providers"
        NPM["npm / PyPI / Docker Hub<br/>Binary & Code Hosting"]
    end

    REG -->|"OpenAPI Spec"| MARKET
    REG -->|"OpenAPI Spec"| SUB
    MARKET --> CLIENT
    SUB --> CLIENT
    CLIENT -->|"Fetch & Run"| NPM
```
**Diagram: The MCP Registry Data Flow and Ecosystem Relationships**

### Key Roles
*   **Official Registry**: Hosted at `https://registry.modelcontextprotocol.io`, this unopinionated metadata store is maintained by the Registry Working Group [docs/registry/about.mdx:10-15]().
*   **Sub-registries**: Organizations can implement the Registry OpenAPI spec to host private or specialized server lists [docs/registry/about.mdx:56-60]().
*   **Aggregators**: Downstream consumers (like marketplaces) that ingest registry data and add opinionated metadata like ratings or security scans [docs/registry/about.mdx:50-54]().

**Sources**: [docs/registry/about.mdx:10-60](), [blog/content/posts/2025-09-08-mcp-registry-preview.md:25-37]()

## Server Metadata and Namespaces

The registry uses a standardized `server.json` schema to describe server instances. This schema ensures that clients know exactly how to execute a server and what environment it requires [docs/registry/about.mdx:19-20]().

### Namespace Authentication
To prevent name squatting and impersonation, the registry enforces **Namespace Authentication**. Server names must follow a reverse DNS format (e.g., `io.github.username/server-name`) [docs/registry/about.mdx:21-25]().
*   **GitHub Verification**: Users verify ownership of their GitHub namespace [docs/registry/about.mdx:72-73]().
*   **DNS/HTTP Verification**: Domain owners verify via DNS records or HTTP challenges [docs/registry/about.mdx:89-90]().

### The `server.json` Structure
The core entity in the registry is the `server.json` file.

| Field | Description | Example |
| :--- | :--- | :--- |
| `name` | Unique reverse-DNS identifier | `io.github.user/weather-server` |
| `packages` | List of distribution methods | `npm`, `pypi`, `docker` |
| `transport` | Communication mechanism | `stdio` or `sse` |
| `args` | Execution arguments | `["--port", "8080"]` |
| `capabilities` | Declared server features | Tools, Resources, Prompts |

**Sources**: [docs/registry/about.mdx:19-25](), [blog/content/posts/2025-09-08-mcp-registry-preview.md:25-27]()

## Discovery Mechanisms

Discovery occurs through a versioned REST API that allows clients to query server metadata.

### API Implementation (v0.1)
The registry provides unauthenticated read-only endpoints for discovery [docs/registry/about.mdx:16-17]():

1.  **List Servers**: `GET /v0.1/servers`
2.  **Get Versions**: `GET /v0.1/servers/{serverName}/versions`
3.  **Get Latest**: `GET /v0.1/servers/{serverName}/versions/latest`

```mermaid
sequenceDiagram
    participant Client as MCP Host/Aggregator
    participant Registry as MCP Registry API
    
    Client->>Registry: GET /v0.1/servers
    Registry-->>Client: 200 OK (List of server metadata)
    
    Note over Client, Registry: Fetching details for a specific server
    
    Client->>Registry: GET /v0.1/servers/io.github.user%2Fmy-server/versions/latest
    Registry-->>Client: 200 OK (server.json content)
```
**Diagram: API Interaction Flow for Server Discovery**

**Sources**: [docs/registry/about.mdx:16-25](), [blog/content/posts/2025-09-08-mcp-registry-preview.md:25-27]()

## Publishing and Integration

### GitHub Actions Integration
The recommended path for publishing is using the official GitHub Action. This automates the validation of `server.json` and submission to the registry during a repository's release cycle [blog/content/posts/2025-09-08-mcp-registry-preview.md:20-21]().

### MCP Bundles (.mcpb)
For local, portable servers, the ecosystem supports the **MCP Bundle** format. These are ZIP archives containing [blog/content/posts/2025-11-20-adopting-mcpb.md:19-21]():
*   `manifest.json`: Metadata and capabilities description [blog/content/posts/2025-11-20-adopting-mcpb.md:25]().
*   `server/`: Implementation code (Node.js, Python, or binary) [blog/content/posts/2025-11-20-adopting-mcpb.md:26]().
*   `node_modules/`: Bundled dependencies [blog/content/posts/2025-11-20-adopting-mcpb.md:28]().

This format enables "one-click" installation in compatible clients like Claude Desktop [blog/content/posts/2025-11-20-adopting-mcpb.md:15-16]().

### Server Identity and .well-known
Modern MCP servers (RC 2025-11-14) can advertise their capabilities via `.well-known` URLs. This allows the registry and clients to discover a server's "business card" without establishing a full stateful connection [blog/content/posts/2025-09-26-mcp-next-version-update.md:67-72]().

**Sources**: [blog/content/posts/2025-11-20-adopting-mcpb.md:15-32](), [blog/content/posts/2025-09-26-mcp-next-version-update.md:67-72](), [docs/registry/about.mdx:19-25]()

## Moderation and Security

The registry delegates code-level security scanning to the underlying package managers (npm, PyPI) and downstream aggregators [docs/registry/about.mdx:78-83](). However, it maintains a **Moderation Policy** to handle:
*   **Spam/Malware**: Publishers must verify namespaces, preventing arbitrary spam [docs/registry/about.mdx:88-90]().
*   **Impersonation**: Handled via namespace verification through DNS or GitHub [docs/registry/about.mdx:70-75]().
*   **Takedowns**: Maintainers can manually remove entries that violate guidelines, such as malicious code or impersonation [docs/registry/about.mdx:91-92](), [blog/content/posts/2025-09-08-mcp-registry-preview.md:39-42]().

**Sources**: [docs/registry/about.mdx:70-94](), [blog/content/posts/2025-09-08-mcp-registry-preview.md:39-42]()

---

# Page: SDK Ecosystem

# SDK Ecosystem

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [blog/content/posts/2026-01-26-mcp-apps.md](blog/content/posts/2026-01-26-mcp-apps.md)
- [blog/content/posts/2026-06-29-sdk-betas-for-2026-07-28.md](blog/content/posts/2026-06-29-sdk-betas-for-2026-07-28.md)
- [blog/static/posts/images/sdk-betas/stack.svg](blog/static/posts/images/sdk-betas/stack.svg)
- [docs/community/sdk-tiers.mdx](docs/community/sdk-tiers.mdx)
- [docs/docs/getting-started/intro.mdx](docs/docs/getting-started/intro.mdx)
- [docs/docs/tools/debugging.mdx](docs/docs/tools/debugging.mdx)
- [docs/extensions/apps/build.mdx](docs/extensions/apps/build.mdx)
- [docs/extensions/apps/overview.mdx](docs/extensions/apps/overview.mdx)
- [docs/extensions/auth/oauth-client-credentials.mdx](docs/extensions/auth/oauth-client-credentials.mdx)
- [docs/extensions/auth/overview.mdx](docs/extensions/auth/overview.mdx)
- [docs/extensions/client-matrix.mdx](docs/extensions/client-matrix.mdx)
- [docs/extensions/overview.mdx](docs/extensions/overview.mdx)
- [docs/extensions/tasks/overview.mdx](docs/extensions/tasks/overview.mdx)

</details>



## Purpose and Scope

This document describes the MCP SDK ecosystem: the collection of official language-specific SDKs that enable developers to build MCP clients and servers. It covers the tier classification system that establishes quality and maintenance expectations, the available SDKs across 10+ languages, conformance testing mechanisms, and the development guidelines for SDK maintainers.

For details on the specific classification levels, see [SDK Tier System](#6.1). For a catalog of current implementations, see [Available SDKs and Language Support](#6.2). For details on the automated validation process, see [Conformance Testing and Quality Metrics](#6.3).

## Overview

The MCP SDK ecosystem provides standardized implementations of the Model Context Protocol across multiple programming languages. Each SDK enables developers to:

- Create MCP servers that expose tools, resources, and prompts.
- Build MCP clients that connect to any MCP server.
- Support local (stdio) and remote (HTTP/SSE) transport protocols.
- Maintain protocol compliance with type safety.

The ecosystem is organized into three tiers based on feature completeness, maintenance commitment, and documentation quality [docs/community/sdk-tiers.mdx:19-29](). This tiering system helps developers choose the right SDK for their needs and provides SDK maintainers with a clear path to improving adoption expectations.

## SDK Tier System

The MCP SDK Tiering System establishes clear expectations for feature completeness and maintenance commitments [docs/community/sdk-tiers.mdx:6-17]().

- **Tier 1: Fully Supported**: Complete protocol implementation, including optional capabilities like sampling and elicitation. Requires a 100% conformance pass rate and issue triage within 2 business days [docs/community/sdk-tiers.mdx:33-40]().
- **Tier 2: Commitment to Full Support**: Actively-maintained SDKs working toward full protocol specification support. Requires an 80% conformance pass rate and issue triage within a month [docs/community/sdk-tiers.mdx:33-40]().
- **Tier 3: Experimental**: Partially implemented, specialized, or experimental SDKs with no minimum conformance or triage requirements [docs/community/sdk-tiers.mdx:26-27](), [docs/community/sdk-tiers.mdx:33-40]().

For details, see [SDK Tier System](#6.1).

Sources: [docs/community/sdk-tiers.mdx:1-43]()

## Conformance Testing

All SDKs are evaluated using automated conformance tests that validate protocol support against the published specifications [docs/community/sdk-tiers.mdx:61-63]().

### Conformance Scoring
Scores are calculated against **applicable required tests** only, excluding experimental features, pending tests, legacy backward-compatibility tests, or disputed scenarios [docs/community/sdk-tiers.mdx:69-75]().

### Tier Advancement and Relegation
Maintainers can request advancement by self-assessing against requirements and passing automated tests reviewed by the SDK Working Group [docs/community/sdk-tiers.mdx:83-90](). Conversely, an SDK may be relegated if tests fail continuously for 4 weeks on the latest stable release (e.g., Tier 1 to Tier 2 if any test fails) [docs/community/sdk-tiers.mdx:94-99]().

For details, see [Conformance Testing and Quality Metrics](#6.3).

Sources: [docs/community/sdk-tiers.mdx:59-101]()

## Available SDKs and Language Support

The ecosystem currently includes SDKs for TypeScript, Python, Java, C#, Go, Kotlin, Swift, Rust, Ruby, and PHP.

### The 2026-07-28 Specification Update
In June 2026, beta releases for the Tier 1 SDKs (TypeScript, Python, Go, and C#) were launched to support the "stateless core" of the 2026-07-28 specification [blog/content/posts/2026-06-29-sdk-betas-for-2026-07-28.md:31-38](). These updates include support for:
- **Stateless Core**: Every request is self-describing; capabilities come from `server/discover` [blog/content/posts/2026-06-29-sdk-betas-for-2026-07-28.md:88-92]().
- **Multi Round-Trip Requests (MRTR)**: Tools returning `InputRequiredResult` for mid-call user interaction [blog/content/posts/2026-06-29-sdk-betas-for-2026-07-28.md:93-97]().
- **Routable Headers**: `Mcp-Method` and `Mcp-Name` on every request for gateway and rate limiter routing [blog/content/posts/2026-06-29-sdk-betas-for-2026-07-28.md:98-102]().

For details, see [Available SDKs and Language Support](#6.2).

Sources: [blog/content/posts/2026-06-29-sdk-betas-for-2026-07-28.md:1-125]()

## SDK Architecture and Components

All official SDKs follow a consistent layered architecture that bridges high-level application logic with the low-level JSON-RPC protocol.

### Layered Architecture

```mermaid
graph TB
    subgraph "Application Layer"
        APP["Application Code<br/>(e.g., McpServer implementation)"]
    end
    
    subgraph "SDK Layer"
        subgraph "Client/Server Layer"
            MCPCLIENT["McpClient<br/>(Client-side protocol operations)"]
            MCPSERVER["McpServer<br/>(Server-side protocol operations)"]
        end
        
        subgraph "Session Layer"
            SESSION["McpSession<br/>(Request/Response correlation)"]
        end
        
        subgraph "Transport Layer"
            STDIO["StdioTransport<br/>(stdin/stdout)"]
            HTTP["StreamableHttpTransport<br/>(HTTP + SSE)"]
        end
    end
    
    APP --> MCPSERVER
    APP --> MCPCLIENT
    MCPSERVER --> SESSION
    MCPCLIENT --> SESSION
    SESSION --> STDIO
    SESSION --> HTTP
```

**Diagram: SDK Layered Architecture bridging Code Entities**

Sources: [blog/static/posts/images/sdk-betas/stack.svg:1-70](), [docs/extensions/apps/overview.mdx:77-96]()

### Core Components
1. **Client/Server Classes**: The primary entry points for developers, such as `McpServer` in TypeScript or `FastMCP` in Python [blog/content/posts/2026-06-29-sdk-betas-for-2026-07-28.md:31-38](), [docs/extensions/apps/build.mdx:12-13]().
2. **Transports**: Standardized handlers for `stdio` (stdin/stdout) and `Streamable HTTP` (SSE) [blog/content/posts/2026-06-29-sdk-betas-for-2026-07-28.md:63-68](), [docs/docs/tools/debugging.mdx:31-49]().
3. **Extension Support**: Mechanisms to opt-in to optional features like `io.modelcontextprotocol/ui` (MCP Apps) or `io.modelcontextprotocol/tasks` [docs/extensions/overview.mdx:114-117]().

## Extension Ecosystem

SDKs provide the foundation for official MCP extensions. These are optional and require explicit opt-in via the `extensions` field during the `initialize` handshake or `server/discover` [docs/extensions/overview.mdx:114-117]().

| Extension | Identifier | SDK Role |
| :--- | :--- | :--- |
| **MCP Apps** | `io.modelcontextprotocol/ui` | Provides the `App` class for UI-to-host communication over `postMessage` [blog/content/posts/2026-01-26-mcp-apps.md:103-112](). |
| **Tasks** | `io.modelcontextprotocol/tasks` | Handles `CreateTaskResult` (identified by `resultType: "task"`) and polling via `tasks/get` [docs/extensions/tasks/overview.mdx:50-62](). |
| **OAuth** | `io.modelcontextprotocol/oauth-client-credentials` | Supplementary auth for machine-to-machine scenarios [docs/extensions/auth/overview.mdx:33-39](). |

### Extension Interaction Flow

```mermaid
sequenceDiagram
    participant SDK as SDK (McpClient)
    participant App as MCP App (iframe)
    participant Srv as MCP Server
    
    SDK->>Srv: initialize (with extensions: { "io.modelcontextprotocol/ui": {} })
    Srv-->>SDK: initialize response (confirmed)
    Note over SDK,App: SDK renders App iframe
    App->>SDK: postMessage(ui/initialize)
    App->>SDK: postMessage(tools/call)
    SDK->>Srv: tools/call (forwarded)
    Srv-->>SDK: tool result
    SDK->>App: postMessage(tool result)
```

**Diagram: SDK Extension Negotiation and UI Communication**

Sources: [docs/extensions/apps/overview.mdx:77-96](), [blog/content/posts/2026-01-26-mcp-apps.md:103-129](), [docs/extensions/overview.mdx:114-117]()

## Issue Triage and Quality Metrics

To maintain Tier 1 and Tier 2 status, SDK repositories must use standardized labels to track triage and resolution metrics [docs/community/sdk-tiers.mdx:104-107]().

### Priority Definitions
- **P0 (Critical)**: Security vulnerabilities (CVSS ≥ 7.0), data corruption, or core functionality failures (e.g., transport connection failure) [docs/community/sdk-tiers.mdx:134-142]().
- **P1-P3**: Significant bugs with workarounds, moderate issues, and "nice-to-have" enhancements respectively [docs/community/sdk-tiers.mdx:128-132]().

### Response Requirements
Tier 1 SDKs must triage issues within 2 business days and resolve P0 bugs within 7 days [docs/community/sdk-tiers.mdx:33-38]().

Sources: [docs/community/sdk-tiers.mdx:102-142]()

---

# Page: SDK Tier System

# SDK Tier System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [blog/content/posts/2026-01-26-mcp-apps.md](blog/content/posts/2026-01-26-mcp-apps.md)
- [docs/community/sdk-tiers.mdx](docs/community/sdk-tiers.mdx)
- [docs/docs/getting-started/intro.mdx](docs/docs/getting-started/intro.mdx)
- [docs/docs/tools/debugging.mdx](docs/docs/tools/debugging.mdx)
- [docs/extensions/apps/build.mdx](docs/extensions/apps/build.mdx)
- [docs/extensions/apps/overview.mdx](docs/extensions/apps/overview.mdx)
- [docs/extensions/auth/oauth-client-credentials.mdx](docs/extensions/auth/oauth-client-credentials.mdx)
- [docs/extensions/auth/overview.mdx](docs/extensions/auth/overview.mdx)
- [docs/extensions/client-matrix.mdx](docs/extensions/client-matrix.mdx)
- [docs/extensions/overview.mdx](docs/extensions/overview.mdx)
- [docs/extensions/tasks/overview.mdx](docs/extensions/tasks/overview.mdx)

</details>



## Purpose and Scope

This document explains the MCP SDK Tier System, which classifies official SDKs into three tiers based on feature completeness, protocol support, and maintenance commitments. The tier system provides clear expectations for SDK users and maintainers, establishes advancement criteria, and defines quality metrics through conformance testing.

For information about available SDKs and their current tier assignments, see [Available SDKs and Language Support](#6.2). For details on conformance testing methodology and quality metrics, see [Conformance Testing and Quality Metrics](#6.3).

## Overview

The SDK Tier System establishes three classification levels that reflect the maturity and completeness of MCP implementations across different programming languages:

- **Tier 1**: Fully supported SDKs with complete protocol implementation, including all non-experimental features and optional capabilities like sampling and elicitation.
- **Tier 2**: Actively-maintained SDKs working toward full protocol specification support.
- **Tier 3**: Experimental, partially implemented, or specialized SDKs.

Experimental features (such as Tasks) and protocol extensions (such as MCP Apps) are not required for any tier.

Sources: [docs/community/sdk-tiers.mdx:19-29]()

## Tier Requirements

The following table defines the specific requirements for each tier across multiple dimensions:

| Requirement | Tier 1: Fully Supported | Tier 2: Commitment to Full Support | Tier 3: Experimental |
| :--- | :--- | :--- | :--- |
| **Conformance Tests** | 100% pass rate | 80% pass rate | No minimum |
| **New Protocol Features** | Before new spec version release, timeline agreed per release based on feature complexity | Within 6 months | No timeline commitment |
| **Issue Triage** | Within 2 business days | Within a month | No requirement |
| **Critical Bug Resolution** | Within 7 days | Within two weeks | No requirement |
| **Stable Release** | Required with clear versioning | At least one stable release | Not required |
| **Documentation** | Comprehensive with examples for all features | Basic documentation covering core features | No minimum |
| **Dependency Policy** | Published update policy | Published update policy | Not required |
| **Roadmap** | Published roadmap | Published plan toward Tier 1 or explanation for remaining Tier 2 | Not required |

### Key Definitions

**Issue Triage** means labeling and determining whether an issue is valid (e.g., using `bug`, `enhancement`, or `question` labels), not necessarily resolving the issue itself. [docs/community/sdk-tiers.mdx:44-44](), [docs/community/sdk-tiers.mdx:108-115]()

**Critical Bug** refers to P0 issues, which are defined as:
- **Security vulnerabilities** with CVSS score ≥ 7.0 (High or Critical severity). [docs/community/sdk-tiers.mdx:143-144]()
- **Core functionality failures** that prevent basic MCP operations: connection establishment, message exchange, or use of core primitives (tools, resources, prompts). [docs/community/sdk-tiers.mdx:145-147]()

**Stable Release** is a published version explicitly marked as production-ready (e.g., version `1.0.0` or higher without pre-release identifiers like `-alpha`, `-beta`, or `-rc`). [docs/community/sdk-tiers.mdx:49-50]()

**Clear Versioning** means following idiomatic versioning patterns with documented breaking change policies. [docs/community/sdk-tiers.mdx:52-53]()

**Roadmap** outlines concrete steps and work items that track implementation of required MCP specification components. [docs/community/sdk-tiers.mdx:55-57]()

Sources: [docs/community/sdk-tiers.mdx:31-57](), [docs/community/sdk-tiers.mdx:143-147]()

## Conformance Testing

All SDKs are evaluated using [automated conformance tests](https://github.com/modelcontextprotocol/conformance) that validate protocol support against published specifications.

### Conformance Scoring

SDKs receive a conformance score based on test results:
- **Tier 1**: 100% conformance required. [docs/community/sdk-tiers.mdx:65-65]()
- **Tier 2**: 80% conformance required. [docs/community/sdk-tiers.mdx:66-66]()
- **Tier 3**: No minimum requirement. [docs/community/sdk-tiers.mdx:67-67]()

Conformance scores are calculated against **applicable required tests** only, excluding tests for experimental features, pending/skipped tests, and disputed tests. [docs/community/sdk-tiers.mdx:69-76]()

Sources: [docs/community/sdk-tiers.mdx:59-78]()

## Tier Advancement

SDK maintainers can request tier advancement by following this process:

1. **Self-assess** against tier requirements.
2. **Open an issue** in the `modelcontextprotocol/modelcontextprotocol` repository with supporting evidence.
3. **Pass automated conformance testing** with the required pass rate for the target tier.
4. **Receive approval** from SDK Working Group maintainers.

Sources: [docs/community/sdk-tiers.mdx:81-90]()

## Tier Relegation

An SDK may be moved to a lower tier if existing conformance tests on the latest stable release fail continuously for 4 weeks:

- **Tier 1 → Tier 2**: Any conformance test fails. [docs/community/sdk-tiers.mdx:97-97]()
- **Tier 2 → Tier 3**: More than 20% of conformance tests fail. [docs/community/sdk-tiers.mdx:98-98]()

An SDK may also be relegated if issues remain unaddressed for two months. [docs/community/sdk-tiers.mdx:100-100]()

Sources: [docs/community/sdk-tiers.mdx:92-101]()

## Issue Triage Labels

SDK repositories must use consistent labels to enable automated reporting on issue handling metrics.

### Status Labels (pick one)

| Label | Description |
| :--- | :--- |
| `needs confirmation` | Unclear if still relevant. |
| `needs repro` | Insufficient information to reproduce. |
| `ready for work` | Has enough information to start. |
| `good first issue` | Good for newcomers. |
| `help wanted` | Contributions welcome from those familiar with codebase. |

### Priority Labels (only if actionable)

| Label | Description |
| :--- | :--- |
| `P0` | Critical: core functionality failures or high-severity security. |
| `P1` | Significant bug affecting many users. |
| `P2` | Moderate issues, valuable feature requests. |
| `P3` | Nice to haves, rare edge cases. |

Sources: [docs/community/sdk-tiers.mdx:119-142]()

## SDK Advancement and Maintenance Flow

The following diagram bridges the Natural Language requirements for tiers to the operational entities in the codebase and GitHub ecosystem.

```mermaid
graph TD
    subgraph "GitHub Operations"
        ISSUE["GitHub Issue (Type/Status/Priority Labels)"]
        CONFORM["modelcontextprotocol/conformance Tests"]
        RELEASES["Stable Releases (SemVer)"]
    end

    subgraph "SDK Working Group Process"
        SELF["Self-Assessment"]
        ADVANCE["Tier Advancement Request"]
        WG_REVIEW["Working Group Approval"]
    end

    subgraph "Tier Status"
        T1["Tier 1: 100% Pass, 2d Triage"]
        T2["Tier 2: 80% Pass, 1mo Triage"]
        T3["Tier 3: Experimental"]
    end

    SELF --> ADVANCE
    ADVANCE --> ISSUE
    ADVANCE --> CONFORM
    CONFORM --> WG_REVIEW
    ISSUE --> WG_REVIEW
    WG_REVIEW --> T1
    WG_REVIEW --> T2
    
    T1 -- "Fail > 4 weeks" --> T2
    T2 -- "Fail > 20% > 4 weeks" --> T3
    T1 -- "P0 Issue > 7 days" --> T2
```

Sources: [docs/community/sdk-tiers.mdx:31-42](), [docs/community/sdk-tiers.mdx:81-101]()

## Protocol Conformance Mapping

This diagram maps specific protocol entities and extensions to the conformance requirements of the Tier system.

```mermaid
graph LR
    subgraph "Required for Tier 1 & 2"
        direction TB
        LIFECYCLE["Connection Lifecycle (initialize/initialized)"]
        TOOLS["Tools (list_tools/call_tool)"]
        RESOURCES["Resources (list_resources/read_resource)"]
        PROMPTS["Prompts (list_prompts/get_prompt)"]
        SAMPLING["Sampling (sampling/createMessage)"]
        ELICITATION["Elicitation (elicitation/request)"]
    end

    subgraph "Optional / Experimental (Exempt)"
        TASKS["Tasks Extension (io.modelcontextprotocol/tasks)"]
        APPS["MCP Apps Extension (io.modelcontextprotocol/ui)"]
        AUTH["Auth Extensions (oauth-client-credentials)"]
    end

    LIFECYCLE -- "100% for T1" --> CONFORMANCE["Conformance Score"]
    TOOLS -- "80% for T2" --> CONFORMANCE
    TASKS -- "Excluded" --> CONFORMANCE
    APPS -- "Excluded" --> CONFORMANCE
```

Sources: [docs/community/sdk-tiers.mdx:23-29](), [docs/community/sdk-tiers.mdx:69-76](), [docs/extensions/tasks/overview.mdx:50-52](), [docs/extensions/apps/overview.mdx:53-56]()

## Tier System Timeline

- **January 23, 2026**: Conformance tests available. [docs/community/sdk-tiers.mdx:10-10]()
- **February 23, 2026**: Official SDK tiering published. [docs/community/sdk-tiers.mdx:11-11]()

Sources: [docs/community/sdk-tiers.mdx:8-17]()

---

# Page: Available SDKs and Language Support

# Available SDKs and Language Support

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [blog/archetypes/default.md](blog/archetypes/default.md)
- [blog/content/posts/2025-07-29-prompts-for-automation.md](blog/content/posts/2025-07-29-prompts-for-automation.md)
- [blog/content/posts/2025-07-31-governance-for-mcp.md](blog/content/posts/2025-07-31-governance-for-mcp.md)
- [blog/content/posts/2025-09-05-php-sdk.md](blog/content/posts/2025-09-05-php-sdk.md)
- [blog/content/posts/2025-09-08-mcp-registry-preview.md](blog/content/posts/2025-09-08-mcp-registry-preview.md)
- [blog/content/posts/2025-09-26-mcp-next-version-update.md](blog/content/posts/2025-09-26-mcp-next-version-update.md)
- [blog/content/posts/2025-11-03-using-server-instructions.md](blog/content/posts/2025-11-03-using-server-instructions.md)
- [blog/content/posts/2025-11-20-adopting-mcpb.md](blog/content/posts/2025-11-20-adopting-mcpb.md)
- [blog/content/posts/2025-11-21-mcp-apps.md](blog/content/posts/2025-11-21-mcp-apps.md)
- [blog/content/posts/2025-11-25-first-mcp-anniversary.md](blog/content/posts/2025-11-25-first-mcp-anniversary.md)
- [blog/content/posts/2025-11-28-sep-process-update.md](blog/content/posts/2025-11-28-sep-process-update.md)
- [blog/content/posts/2026-06-29-sdk-betas-for-2026-07-28.md](blog/content/posts/2026-06-29-sdk-betas-for-2026-07-28.md)
- [blog/content/posts/welcome-to-mcp-blog.md](blog/content/posts/welcome-to-mcp-blog.md)
- [blog/static/posts/images/sdk-betas/stack.svg](blog/static/posts/images/sdk-betas/stack.svg)

</details>



## Purpose and Scope

This page catalogs the official Model Context Protocol (MCP) SDKs across multiple programming languages, their tier classifications, and documentation links. It highlights the SDK beta releases supporting the **2026-07-28 specification** release candidate, which introduces a stateless architecture and Multi Round-Trip Requests (MRTR).

## SDK Overview

The MCP ecosystem provides official SDKs in 10 programming languages. As of June 2026, four "Tier 1" SDKs have released beta versions to support the major protocol revision scheduled for July 28, 2026 [blog/content/posts/2026-06-29-sdk-betas-for-2026-07-28.md:1-38]().

| Language | Repository | Tier Status | 2026-07-28 Beta |
| :--- | :--- | :--- | :--- |
| **TypeScript** | [modelcontextprotocol/typescript-sdk](https://github.com/modelcontextprotocol/typescript-sdk) | Tier 1 | v2.0.0-beta [blog/content/posts/2026-06-29-sdk-betas-for-2026-07-28.md:31-34]() |
| **Python** | [modelcontextprotocol/python-sdk](https://github.com/modelcontextprotocol/python-sdk) | Tier 1 | v2.0.0-beta [blog/content/posts/2026-06-29-sdk-betas-for-2026-07-28.md:31-34]() |
| **Go** | [modelcontextprotocol/go-sdk](https://github.com/modelcontextprotocol/go-sdk) | Tier 1 | Available [blog/content/posts/2026-06-29-sdk-betas-for-2026-07-28.md:35-36]() |
| **C#** | [modelcontextprotocol/csharp-sdk](https://github.com/modelcontextprotocol/csharp-sdk) | Tier 1 | Available [blog/content/posts/2026-06-29-sdk-betas-for-2026-07-28.md:35-36]() |
| **Java** | [modelcontextprotocol/java-sdk](https://github.com/modelcontextprotocol/java-sdk) | Tier 2 | TBD |
| **PHP** | [modelcontextprotocol/php-sdk](https://github.com/modelcontextprotocol/php-sdk) | Tier 3 | Supported [blog/content/posts/2025-09-05-php-sdk.md:14-20]() |
| **Kotlin** | [modelcontextprotocol/kotlin-sdk](https://github.com/modelcontextprotocol/kotlin-sdk) | Tier 3 | TBD |
| **Swift** | [modelcontextprotocol/swift-sdk](https://github.com/modelcontextprotocol/swift-sdk) | Tier 3 | TBD [blog/content/posts/2025-09-26-mcp-next-version-update.md:92-92]() |
| **Rust** | [modelcontextprotocol/rust-sdk](https://github.com/modelcontextprotocol/rust-sdk) | Tier 3 | TBD |
| **Ruby** | [modelcontextprotocol/ruby-sdk](https://github.com/modelcontextprotocol/ruby-sdk) | Tier 3 | TBD |

Sources: [blog/content/posts/2026-06-29-sdk-betas-for-2026-07-28.md:31-38](), [blog/content/posts/2025-09-05-php-sdk.md:14-20](), [blog/content/posts/2025-09-26-mcp-next-version-update.md:89-94]()

## Tier 1 SDKs and the 2026-07-28 Spec

The Tier 1 SDKs (TypeScript, Python, Go, C#) are the first to implement the core changes from the 2026-07-28 release candidate [blog/content/posts/2026-06-29-sdk-betas-for-2026-07-28.md:81-83]().

### Key 2026-07-28 Features Supported
*   **Stateless Core**: Removal of the `initialize` handshake; every request is self-describing via `server/discover` [blog/content/posts/2026-06-29-sdk-betas-for-2026-07-28.md:88-92]().
*   **Multi Round-Trip Requests (MRTR)**: Support for `InputRequiredResult`, allowing tools to pause for user input mid-call [blog/content/posts/2026-06-29-sdk-betas-for-2026-07-28.md:93-97]().
*   **Routable Headers**: Inclusion of `Mcp-Method` and `Mcp-Name` in transport headers for gateway routing [blog/content/posts/2026-06-29-sdk-betas-for-2026-07-28.md:98-102]().
*   **Authorization Hardening**: Implementation of `iss` validation (RFC 9207) and `application_type` for Dynamic Client Registration (DCR) [blog/content/posts/2026-06-29-sdk-betas-for-2026-07-28.md:103-111]().
*   **Standard Error Codes**: Transition to standard JSON-RPC error codes (e.g., `-32602` for missing resources) [blog/content/posts/2026-06-29-sdk-betas-for-2026-07-28.md:115-119]().

### Migration and Interoperability
Upgrading to the v2 SDKs is an opt-in breaking change [blog/content/posts/2026-06-29-sdk-betas-for-2026-07-28.md:53-55](). New clients speaking the 2026-07-28 protocol are designed to fall back to the `initialize` handshake when connecting to legacy servers (2025-11-25 or earlier) [blog/content/posts/2026-06-29-sdk-betas-for-2026-07-28.md:69-71]().

## Extension Support

Official extensions allow servers to provide interactive UIs and advanced automation.

| Extension | Identifier | Status |
| :--- | :--- | :--- |
| **MCP Apps** | `ui://` | Proposed in SEP-1865 for interactive UIs via iframes [blog/content/posts/2025-11-21-mcp-apps.md:22-28]() |
| **Server Instructions** | `initializeResult.instructions` | Injected into system prompts to guide LLM tool usage [blog/content/posts/2025-11-03-using-server-instructions.md:47-48]() |
| **MCP Bundles** | `.mcpb` | Standardized format for portable local server distribution [blog/content/posts/2025-11-20-adopting-mcpb.md:15-19]() |

Sources: [blog/content/posts/2025-11-21-mcp-apps.md:54-64](), [blog/content/posts/2025-11-03-using-server-instructions.md:47-48](), [blog/content/posts/2025-11-20-adopting-mcpb.md:21-30]()

## SDK Architecture: Bridging Space

The following diagrams illustrate how the SDKs bridge high-level application logic with low-level protocol entities.

### From Natural Language to Tool Execution (MRTR Pattern)

```mermaid
graph TD
    subgraph "Natural Language Space"
        User["User: 'Show me analytics'"]
    end

    subgraph "Code Entity Space (SDK Layer)"
        McpClient["McpClient Class"]
        CallTool["tools/call Method"]
        InputReq["InputRequiredResult Entity"]
        RetryCall["Retry with Answer"]
    end

    subgraph "Transport Layer"
        JSONRPC["JSON-RPC Message"]
        Headers["Mcp-Method: tools/call"]
    end

    User --> McpClient
    McpClient --> CallTool
    CallTool --> Headers
    Headers --> JSONRPC
    JSONRPC -- "Server asks for input" --> InputReq
    InputReq -- "User provides input" --> RetryCall
```
Sources: [blog/content/posts/2026-06-29-sdk-betas-for-2026-07-28.md:93-102](), [blog/content/posts/2025-11-03-using-server-instructions.md:77-80]()

### MCP Apps: UI-to-Host Communication

```mermaid
graph LR
    subgraph "Application Space (Iframe)"
        UIRes["ui:// Resource Template"]
        McpSDK["@modelcontextprotocol/sdk"]
        PostMessage["postMessage (JSON-RPC)"]
    end

    subgraph "Host Space (Client SDK)"
        HostApp["Host Application"]
        Sandbox["Sandboxed Iframe"]
    end

    UIRes --> McpSDK
    McpSDK -- "JSON-RPC over postMessage" --> PostMessage
    PostMessage --> HostApp
    HostApp -- "Render UI" --> Sandbox
```
Sources: [blog/content/posts/2025-11-21-mcp-apps.md:84-91](), [blog/content/posts/2025-11-21-mcp-apps.md:105-112]()

## SDK-Specific Technical Details

### TypeScript (Reference)
The TypeScript SDK remains the primary reference.
*   **Version 2 Beta**: Introduces stateless transport wiring [blog/content/posts/2026-06-29-sdk-betas-for-2026-07-28.md:63-65]().
*   **UI Support**: Developers can use the standard SDK to build UI components communicating via `postMessage` [blog/content/posts/2025-11-21-mcp-apps.md:86-88]().

### Python
*   **Version 2 Beta**: A single endpoint can answer both `2026-07-28` and legacy protocol revisions [blog/content/posts/2026-06-29-sdk-betas-for-2026-07-28.md:65-68]().
*   **Package Management**: Users are encouraged to pin `mcp>=1.27,<2` for stable workloads [blog/content/posts/2026-06-29-sdk-betas-for-2026-07-28.md:75-77]().

### PHP
*   **Announcement**: Released Sept 2025 in collaboration with the PHP Foundation and Symfony [blog/content/posts/2025-09-05-php-sdk.md:1-12]().
*   **Capabilities**: Supports exposing tools, prompts, and resources [blog/content/posts/2025-09-05-php-sdk.md:16-18]().

### C#
*   **Stateless Default**: The C# preview's HTTP transport defaults to the new stateless mode [blog/content/posts/2026-06-29-sdk-betas-for-2026-07-28.md:67-68]().

Sources: [blog/content/posts/2026-06-29-sdk-betas-for-2026-07-28.md:1-125](), [blog/content/posts/2025-11-21-mcp-apps.md:84-91](), [blog/content/posts/2025-09-05-php-sdk.md:1-36]()

---

# Page: Conformance Testing and Quality Metrics

# Conformance Testing and Quality Metrics

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [blog/content/posts/2026-01-26-mcp-apps.md](blog/content/posts/2026-01-26-mcp-apps.md)
- [docs/community/sdk-tiers.mdx](docs/community/sdk-tiers.mdx)
- [docs/docs/getting-started/intro.mdx](docs/docs/getting-started/intro.mdx)
- [docs/docs/tools/debugging.mdx](docs/docs/tools/debugging.mdx)
- [docs/extensions/apps/build.mdx](docs/extensions/apps/build.mdx)
- [docs/extensions/apps/overview.mdx](docs/extensions/apps/overview.mdx)
- [docs/extensions/auth/oauth-client-credentials.mdx](docs/extensions/auth/oauth-client-credentials.mdx)
- [docs/extensions/auth/overview.mdx](docs/extensions/auth/overview.mdx)
- [docs/extensions/client-matrix.mdx](docs/extensions/client-matrix.mdx)
- [docs/extensions/overview.mdx](docs/extensions/overview.mdx)
- [docs/extensions/tasks/overview.mdx](docs/extensions/tasks/overview.mdx)

</details>



## Purpose and Scope

This page documents the conformance testing framework used to evaluate Model Context Protocol (MCP) SDK implementations against the protocol specification. It covers the automated test suite, pass rate requirements for SDK tier classification, issue triage labeling standards, and quality metrics used to assess SDK maintenance and feature completeness.

For information about the SDK tier system itself and advancement/relegation criteria, see [SDK Tier System](6.1). For details on available SDKs and their current tier status, see [Available SDKs and Language Support](6.2).

## Overview

Conformance testing is the primary mechanism for objectively measuring whether an SDK correctly implements the MCP protocol. The test suite validates protocol compliance by running standardized scenarios and checking message exchanges against the specification. SDKs receive a conformance score based on test results, which directly influences tier classification and maintenance expectations.

**Key principles:**

- Tests are specification-driven and version-specific [docs/community/sdk-tiers.mdx:69-71]().
- Scores exclude experimental features and pending tests [docs/community/sdk-tiers.mdx:72-75]().
- Tier requirements: Tier 1 requires 100% pass rate, Tier 2 requires 80% [docs/community/sdk-tiers.mdx:33-35]().
- Conformance testing is automated and reproducible across all SDKs [docs/community/sdk-tiers.mdx:61-63]().

Sources: [docs/community/sdk-tiers.mdx:59-78]()

## Conformance Test Suite

### Test Repository and Structure

The conformance test suite is maintained in the `modelcontextprotocol/conformance` repository [docs/community/sdk-tiers.mdx:61-62](). Tests are organized by protocol version and feature area, allowing SDKs to target specific specification versions while maintaining backward compatibility validation.

**Test organization:**
- Tests grouped by specification version [docs/community/sdk-tiers.mdx:71]().
- Feature-specific test suites (core protocol, tools, resources, prompts, sampling, etc.).
- Markers for test status: `pending`, `skipped`, `experimental` [docs/community/sdk-tiers.mdx:72-73]().
- Legacy backward-compatibility tests (optional for SDKs claiming legacy support) [docs/community/sdk-tiers.mdx:74]().

### Applicable Test Calculation

Conformance scores are calculated against **applicable required tests only**, excluding:
- Tests for specification versions the SDK does not target [docs/community/sdk-tiers.mdx:71]().
- Tests marked as `pending` or `skipped` [docs/community/sdk-tiers.mdx:72]().
- Tests for experimental features such as **Tasks** or **MCP Apps** [docs/community/sdk-tiers.mdx:28-29](), [docs/community/sdk-tiers.mdx:73]().
- Legacy backward-compatibility tests (unless the SDK explicitly claims legacy support) [docs/community/sdk-tiers.mdx:74]().
- Tests labeled `disputed` in the conformance repository until resolved [docs/community/sdk-tiers.mdx:75]().

Sources: [docs/community/sdk-tiers.mdx:69-75]()

## Pass Rate Requirements by Tier

| Requirement | Tier 1: Fully Supported | Tier 2: Commitment to Full Support | Tier 3: Experimental |
| :--- | :--- | :--- | :--- |
| **Conformance Tests** | 100% pass rate | 80% pass rate | No minimum |
| **New Protocol Features** | Before new spec version release | Within 6 months | No timeline commitment |
| **Issue Triage** | Within 2 business days | Within a month | No requirement |
| **Critical Bug Resolution** | Within 7 days | Within two weeks | No requirement |
| **Stable Release** | Required with clear versioning | At least one stable release | Not required |
| **Documentation** | Comprehensive with examples | Basic documentation | No minimum |

Sources: [docs/community/sdk-tiers.mdx:33-42]()

## Issue Triage Labels

SDK repositories must use consistent labels to enable automated reporting on issue handling metrics [docs/community/sdk-tiers.mdx:102-104](). These labels track triage response times (creation to first label) and critical bug resolution times (P0 label to close) [docs/community/sdk-tiers.mdx:105-107]().

### Type Labels (pick one)

| Label | Description |
| :--- | :--- |
| `bug` | Something isn't working |
| `enhancement` | Request for new feature |
| `question` | Further information requested |

Repositories using GitHub's native issue types satisfy this requirement without needing explicit type labels [docs/community/sdk-tiers.mdx:116-117]().

### Status Labels (pick one)

These labels must use exact names across all repositories to enable consistent automated reporting [docs/community/sdk-tiers.mdx:121-122]().

| Label | Description |
| :--- | :--- |
| `needs confirmation` | Unclear if still relevant |
| `needs repro` | Insufficient information to reproduce |
| `ready for work` | Has enough information to start |
| `good first issue` | Good for newcomers |
| `help wanted` | Contributions welcome from those familiar with codebase |

### Priority Labels (only if actionable)

| Label | Description |
| :--- | :--- |
| `P0` | Critical: core functionality failures or high-severity security |
| `P1` | Significant bug affecting many users |
| `P2` | Moderate issues, valuable feature requests |
| `P3` | Nice to haves, rare edge cases |

**P0 (Critical) issues** are defined as:
- **Security vulnerabilities** with CVSS score ≥ 7.0 (High or Critical severity).
- **Core functionality failures** that prevent basic MCP operations: connection establishment, message exchange, or use of core primitives (tools, resources, prompts).

Sources: [docs/community/sdk-tiers.mdx:102-142]()

## Tier Advancement and Relegation

### Advancement Process
SDK maintainers can request tier advancement by:
1. Self-assessing against tier requirements [docs/community/sdk-tiers.mdx:85]().
2. Opening an issue in the `modelcontextprotocol/modelcontextprotocol` repository with supporting evidence [docs/community/sdk-tiers.mdx:86]().
3. Passing automated conformance testing [docs/community/sdk-tiers.mdx:87]().
4. Receiving approval from SDK Working Group maintainers [docs/community/sdk-tiers.mdx:88]().

### Relegation Criteria
An SDK may be moved to a lower tier if existing conformance tests on the latest stable release fail continuously for 4 weeks [docs/community/sdk-tiers.mdx:94-95]():
- **Tier 1 → Tier 2**: Any conformance test fails [docs/community/sdk-tiers.mdx:97]().
- **Tier 2 → Tier 3**: More than 20% of conformance tests fail [docs/community/sdk-tiers.mdx:98]().
- Relegation may also occur if issues remain unaddressed for two months [docs/community/sdk-tiers.mdx:100]().

Sources: [docs/community/sdk-tiers.mdx:81-100]()

## Conformance Testing Workflow

The following diagram illustrates how conformance testing integrates with the SDK tier system and quality evaluation.

### Conformance to Tier Evaluation
```mermaid
graph TB
    subgraph "SDK_Source_Code"
        [SDK_Implementation] --> [Feature_Set]
    end
    
    subgraph "Conformance_Suite"
        [modelcontextprotocol/conformance] --> [Test_Runner]
        [Test_Runner] --> [Filter_Applicable_Tests]
    end

    subgraph "Quality_Metrics"
        [Issue_Labels] --> [Triage_Response_Time]
        [P0_Label] --> [Critical_Bug_Resolution_Time]
    end

    [Feature_Set] --> [Test_Runner]
    [Filter_Applicable_Tests] --> [Conformance_Score]
    [Conformance_Score] --> [Tier_Classification]
    [Triage_Response_Time] --> [Tier_Classification]
    [Critical_Bug_Resolution_Time] --> [Tier_Classification]

    subgraph "Tier_Classification"
        direction TB
        [Tier_1_100pct]
        [Tier_2_80pct]
        [Tier_3_No_Min]
    end
```
Sources: [docs/community/sdk-tiers.mdx:33-75]()

## Extension Support and Quality Metrics

While core protocol features are required for conformance, official extensions like **MCP Apps** (`io.modelcontextprotocol/ui`) and **Tasks** (`io.modelcontextprotocol/tasks`) are currently considered opt-in and are not required for any tier [docs/community/sdk-tiers.mdx:28-29](). However, they are tracked via an Extension Support Matrix to help developers evaluate SDK and client capabilities [docs/extensions/client-matrix.mdx:32-34]().

### Extension Negotiation and Verification
Extensions are negotiated during the initialization handshake. A client only uses an extension if both client and server declare support [docs/extensions/client-matrix.mdx:16-17]().

```mermaid
sequenceDiagram
    participant SDK as "SDK / Client"
    participant Conf as "Conformance Test"
    participant Ext as "Extension Spec"

    Note over SDK,Ext: Extension Negotiation (initialize)
    SDK->>Conf: initialize(capabilities: { extensions: { "io.modelcontextprotocol/ui": {} } })
    Conf->>Ext: Check identifier in docs/extensions/overview.mdx
    Ext-->>Conf: Valid Extension (e.g., MCP Apps)
    Conf->>SDK: Verify implementation (e.g., ui/initialize)
    Note right of SDK: Supported but not required for Tier 1
```
Sources: [docs/extensions/overview.mdx:114-117](), [docs/community/sdk-tiers.mdx:28-29](), [docs/extensions/client-matrix.mdx:16-17]()

### Quality Metrics for SDK Evaluation
Beyond conformance tests, SDKs are evaluated on maintenance health using GitHub labels:
- **Triage Latency**: Measured as time from issue creation to the application of a Status label like `ready for work` [docs/community/sdk-tiers.mdx:105-107]().
- **Resolution Latency**: Specifically for `P0` issues, measuring time to close [docs/community/sdk-tiers.mdx:106-107]().
- **Release Stability**: Verified by checking for stable version strings (e.g., `1.0.0`) without pre-release tags like `-beta` [docs/community/sdk-tiers.mdx:49-50]().

Sources: [docs/community/sdk-tiers.mdx:44-53](), [docs/community/sdk-tiers.mdx:102-107]()

## Related Resources

- [SDK Tier System](6.1) - Detailed tier requirements and advancement process.
- [Available SDKs and Language Support](6.2) - Current SDK catalog and tier status.
- [Protocol Specification](2) - Complete MCP protocol documentation.
- [Contributing to MCP](7.1) - How to contribute to the specification repository.

---

# Page: Development Guide

# Development Guide

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitattributes](.gitattributes)
- [.github/ISSUE_TEMPLATE/bug_report.yml](.github/ISSUE_TEMPLATE/bug_report.yml)
- [.github/ISSUE_TEMPLATE/config.yml](.github/ISSUE_TEMPLATE/config.yml)
- [.github/ISSUE_TEMPLATE/work_tracking.yml](.github/ISSUE_TEMPLATE/work_tracking.yml)
- [.github/dependabot.yml](.github/dependabot.yml)
- [.prototools](.prototools)
- [AGENTS.md](AGENTS.md)
- [CLAUDE.md](CLAUDE.md)
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [README.md](README.md)
- [SECURITY.md](SECURITY.md)
- [docs/community/security.mdx](docs/community/security.mdx)
- [package-lock.json](package-lock.json)
- [package.json](package.json)

</details>



This guide provides a comprehensive overview for developers contributing to the Model Context Protocol (MCP) specification repository. It covers environment setup, build orchestration, schema development, and automated maintenance tools.

For detailed information on specific contribution areas:
- **Contributing to MCP**: Prerequisites, repository structure, and AI-assisted contribution policies. See [Contributing to MCP](#7.1).
- **Specification Enhancement Process (SEP)**: Proposing protocol changes and navigating the SEP lifecycle. See [Specification Enhancement Process (SEP)](#7.2).
- **Schema Development and Generation**: Working with the TypeScript source-of-truth and generating JSON schemas. See [Schema Development and Generation](#7.3).
- **Build System and Automation**: npm scripts, CI/CD workflows, and release management. See [Build System and Automation](#7.4).
- **Documentation Generation System**: TypeDoc plugins, Mintlify integration, and the Hugo blog. See [Documentation Generation System](#7.5).
- **SEP Lifecycle Automation Tool**: The `sep-automation` tool for managing GitHub issues and Discord notifications. See [SEP Lifecycle Automation Tool](#7.6).

## Repository Overview

The repository acts as the authoritative source for the MCP specification, housing protocol definitions, documentation, and the blog [README.md:5-9]().

### System Architecture: Source to Artifacts

The following diagram illustrates how source files in the "Natural Language Space" (documentation and SEPs) and "Code Entity Space" (TypeScript schemas) are transformed into published artifacts.

**Source-to-Artifact Pipeline**
```mermaid
graph TD
    subgraph "Natural Language Space"
        SEP_MD["seps/*.md<br/>(SEP Proposals)"]
        DOCS_MDX["docs/**/*.mdx<br/>(Hand-written Docs)"]
        BLOG_MD["blog/content/**/*.md<br/>(Hugo Posts)"]
    end

    subgraph "Code Entity Space"
        SCHEMA_TS["schema/*/schema.ts<br/>(TS Source of Truth)"]
        GEN_SCRIPT["scripts/generate-schemas.ts<br/>(Generator)"]
        SEP_RENDER["scripts/render-seps.ts<br/>(SEP Renderer)"]
        EXAMPLES["schema/*/examples/**/*.json<br/>(Validation Samples)"]
    end

    subgraph "Published Artifacts"
        SCHEMA_JSON["schema/*/schema.json<br/>(JSON Schema)"]
        SCHEMA_MDX["docs/specification/*/schema.mdx<br/>(Generated Reference)"]
        MINTLIFY_SITE["modelcontextprotocol.io<br/>(Mintlify)"]
        HUGO_SITE["blog.modelcontextprotocol.io<br/>(Hugo)"]
    end

    SCHEMA_TS -- "input" --> GEN_SCRIPT
    EXAMPLES -- "referenced in TS" --> SCHEMA_TS
    GEN_SCRIPT -- "writes" --> SCHEMA_JSON
    GEN_SCRIPT -- "writes" --> SCHEMA_MDX
    
    SEP_MD -- "input" --> SEP_RENDER
    SEP_RENDER -- "writes" --> MINTLIFY_SITE
    
    DOCS_MDX --> MINTLIFY_SITE
    SCHEMA_MDX --> MINTLIFY_SITE
    BLOG_MD --> HUGO_SITE
```
Sources: [package.json:23-28](), [CONTRIBUTING.md:42-54](), [README.md:5-17](), [AGENTS.md:58-65]()

## Development Environment

### Prerequisites
- **Node.js**: Version 20 or above is required [package.json:10-12]().
- **Package Manager**: `npm` is used for dependency management and task execution.
- **Tools**: Hugo (for blog development) and Mintlify (for documentation preview) [CONTRIBUTING.md:12-17]().

### Core npm Scripts
The build system is orchestrated via `package.json` scripts.

| Script | Purpose |
|:-------|:--------|
| `npm run generate` | Top-level command to regenerate schemas and SEPs [package.json:24](). |
| `npm run check` | Runs full suite of validation (TS, JSON, Examples, MDX, Links) [package.json:32](). |
| `npm run prep` | Comprehensive script for local development: check, generate, and format [package.json:45](). |
| `npm run serve:docs` | Starts local Mintlify preview for documentation [package.json:43](). |
| `npm run serve:blog` | Starts local Hugo server for the blog [package.json:44](). |

Sources: [package.json:23-46](), [CONTRIBUTING.md:8-17]()

## Build and Automation Workflows

The repository employs several automated workflows to maintain specification integrity and facilitate the release process.

### Automation Tooling: SEP Lifecycle
The `tools/sep-automation` utility (referenced in child page 7.6) manages the state of Specification Enhancement Proposals. It interacts with GitHub to transition SEPs between states and pings maintainers for review.

**SEP Automation Interaction**
```mermaid
graph LR
    subgraph "GitHub Actions"
        SEP_WORKFLOW[".github/workflows/sep-lifecycle.yml"]
    end

    subgraph "sep-automation tool"
        SEP_PROC["SEPProcessor"]
        TRANS_HAND["TransitionHandler"]
        MAINT_RES["MaintainerResolver"]
    end

    subgraph "External Integration"
        GH_API["GitHub API"]
        DISCORD["Discord Webhook"]
    end

    SEP_WORKFLOW -- "triggers" --> SEP_PROC
    SEP_PROC -- "evaluates" --> MAINT_RES
    SEP_PROC -- "executes" --> TRANS_HAND
    TRANS_HAND -- "updates" --> GH_API
    SEP_PROC -- "notifies" --> DISCORD
```
Sources: [package.json:28](), [AGENTS.md:77-81]()

### CI/CD Pipelines
Validation is enforced through GitHub Actions to ensure that manual edits to source files are reflected in generated artifacts.

- **Main Validation**: Checks TypeScript definitions, JSON schema consistency, and MDX reference files via `npm run check` [package.json:32]().
- **Merge Handling**: Generated files (`.json`, `.mdx`) use a special merge strategy defined in `.gitattributes` to prevent manual conflict resolution [ .gitattributes:3-10]().
- **Blog Deployment**: Automatically builds and deploys the Hugo site [package.json:44]().

Sources: [package.json:23-46](), [.gitattributes:1-11](), [CONTRIBUTING.md:56-67]()

## Documentation System

The documentation is a hybrid of hand-written MDX and generated API references.

### Schema Reference Generation
TypeScript files are the source of truth for the protocol schema [AGENTS.md:50-55](). The generation pipeline uses `typedoc` to transform `schema.ts` into MDX files suitable for Mintlify [package.json:27]().

- **TypeScript Source**: Located in `schema/[version]/schema.ts` [AGENTS.md:52]().
- **JSON Schema Output**: Generated at `schema/[version]/schema.json` [AGENTS.md:54]().
- **MDX Reference**: Generated at `docs/specification/[version]/schema.mdx` [AGENTS.md:54]().

### Blog System
The blog uses Hugo and is located in the `blog/` directory [CONTRIBUTING.md:92](). It is separate from the main documentation site and can be previewed locally using `npm run serve:blog` [package.json:44]().

Sources: [package.json:23-46](), [CONTRIBUTING.md:90-98](), [AGENTS.md:48-57]()

---

# Page: Contributing to MCP

# Contributing to MCP

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitattributes](.gitattributes)
- [.github/ISSUE_TEMPLATE/bug_report.yml](.github/ISSUE_TEMPLATE/bug_report.yml)
- [.github/ISSUE_TEMPLATE/config.yml](.github/ISSUE_TEMPLATE/config.yml)
- [.github/ISSUE_TEMPLATE/work_tracking.yml](.github/ISSUE_TEMPLATE/work_tracking.yml)
- [.github/dependabot.yml](.github/dependabot.yml)
- [.prototools](.prototools)
- [AGENTS.md](AGENTS.md)
- [AI_POLICY.md](AI_POLICY.md)
- [ANTITRUST.md](ANTITRUST.md)
- [CLAUDE.md](CLAUDE.md)
- [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [LICENSE](LICENSE)
- [README.md](README.md)
- [SECURITY.md](SECURITY.md)
- [docs/community/antitrust.mdx](docs/community/antitrust.mdx)
- [docs/community/contributing.mdx](docs/community/contributing.mdx)
- [docs/community/security.mdx](docs/community/security.mdx)
- [package-lock.json](package-lock.json)
- [package.json](package.json)

</details>



This page explains how to contribute to the Model Context Protocol project, including prerequisites, repository structure, contribution workflows, and the tools and processes used by maintainers and contributors.

**Scope:** This document covers contributions to the core MCP project—the specification, official SDKs, documentation, and governance processes. For information about building MCP servers and clients (rather than contributing to MCP itself), see the [Server Development](#5) and [Client Ecosystem](#4) sections.

---

## Prerequisites and Setup

### Required Tools

Before contributing, ensure you have the following installed:

| Tool | Version | Purpose |
|------|---------|---------|
| **Git** | Any recent version | Cloning repositories and submitting changes |
| **Node.js** | 20+ (24+ recommended) | Building, testing, and schema generation |
| **npm** | 11+ | Dependency management (comes with Node.js) |
| **GitHub account** | — | Submitting pull requests and issues |
| **TypeScript** | 6.0.3+ | Language for schema source-of-truth |
| **Hugo** | — | For previewing blog changes |

Sources: [package.json:11-12](), [CONTRIBUTING.md:8-17](), [docs/community/contributing.mdx:13-28]()

### Repository Structure

MCP spans multiple repositories in the [`modelcontextprotocol`](https://github.com/modelcontextprotocol) GitHub organization:

| Repository | Contents |
|------------|----------|
| `modelcontextprotocol/modelcontextprotocol` | Specification, documentation, SEPs, schema, blog |
| `modelcontextprotocol/typescript-sdk` | TypeScript/JavaScript SDK |
| `modelcontextprotocol/python-sdk` | Python SDK |
| `modelcontextprotocol/go-sdk` | Go SDK |
| `modelcontextprotocol/java-sdk` | Java SDK |
| `modelcontextprotocol/kotlin-sdk` | Kotlin SDK |
| `modelcontextprotocol/csharp-sdk` | C# SDK |
| `modelcontextprotocol/swift-sdk` | Swift SDK |
| `modelcontextprotocol/rust-sdk` | Rust SDK |
| `modelcontextprotocol/ruby-sdk` | Ruby SDK |
| `modelcontextprotocol/php-sdk` | PHP SDK |

The **specification repository** (`modelcontextprotocol/modelcontextprotocol`) is the primary repository for protocol changes, documentation, and SEPs.

Sources: [docs/community/contributing.mdx:35-57](), [README.md:5-17]()

---

## Project Roles and Governance

MCP follows a hierarchical governance model with different levels of responsibility:

### Governance Hierarchy
```mermaid
graph TD
    A["Lead Maintainers<br/>(David Soria Parra & Justin Spahr-Summers)<br/>Final decision authority"]
    B["Core Maintainers<br/>Overall project direction<br/>Review SEPs"]
    C["Maintainers<br/>SDKs, Working Groups,<br/>Components"]
    D["Contributors<br/>Issues, PRs,<br/>Discussions"]
    
    A --> B
    B --> C
    C --> D
```

**Contributor** - Anyone who files issues, submits PRs, or participates in discussions.
**Maintainer** - Stewards specific areas like SDKs, documentation, or Working Groups.
**Core Maintainer** - Guides overall project direction, reviews SEPs, and oversees the specification.

Sources: [docs/community/contributing.mdx:59-71](), [README.md:18-20]()

---

## Your First Contribution

### Step 1: Set Up Your Environment

1. **Fork the repository** on GitHub.
2. **Clone your fork**:
   ```bash
   git clone https://github.com/YOUR-USERNAME/modelcontextprotocol.git
   cd modelcontextprotocol
   ```
3. **Install dependencies**:
   ```bash
   nvm install  # install correct Node version [CONTRIBUTING.md:32]
   npm install
   ```
4. **Verify everything works**:
   ```bash
   npm run check
   ```

Sources: [CONTRIBUTING.md:18-34](), [docs/community/contributing.mdx:85-125]()

### Step 2: Make Your Change

1. **Create a branch**: `git checkout -b fix/your-description`.
2. **Edit files**:
   - Schema changes go in `schema/draft/schema.ts` [CONTRIBUTING.md:44]().
   - Documentation is in `docs/` (MDX format) [CONTRIBUTING.md:71]().
   - Blog posts are in `blog/` (Hugo format) [CONTRIBUTING.md:92]().
3. **Regenerate if needed**: If you change the schema, run `npm run generate:schema` [CONTRIBUTING.md:53]().
4. **Run prep**: Use `npm run prep` to run all checks, generation, and formatting at once [CONTRIBUTING.md:88]().

### Step 3: Submit

1. **Push your branch** to your fork.
2. **Open a Pull Request** to the main repository.
3. **Follow the template**: Fill out the PR template, disclosing any AI assistance [CONTRIBUTING.md:126-137]().

---

## Contribution Policies

### AI Contribution Policy
If you use AI assistance (e.g., Claude, ChatGPT), you **must disclose it** in the PR or issue [CONTRIBUTING.md:133-137]().
- **Disclosure requirements**: See `AI_POLICY.md` for full disclosure expectations.
- **Human in the loop**: You must personally understand the changes and provide a clear rationale.

### AI Agent Policy (AGENTS.md)
Autonomous AI agents (Claude, Copilot) are restricted from creating issues or PRs unless:
- The user is a listed maintainer [AGENTS.md:11-13]().
- The user has >3 merged PRs [AGENTS.md:14-14]().
- If bypassing these rules, a `disclosure.txt` file with specific text must be included: `"This change was submitted despite me reading the rules and understanding AI contribution guidelines."` [AGENTS.md:19-25]().

### Security Reporting
**Do not report security issues through public PRs or issues.**
- Use the **GitHub Security Advisory process** [SECURITY.md:7-9]().
- Report vulnerabilities like auth bypasses, injection, or sandbox escapes.
- **Out of scope**: Stdio transport attacks where one peer crashes another (expected trust boundary) [SECURITY.md:76-90]().

### Code of Conduct
The project follows the Contributor Covenant. Unacceptable behavior includes harassment, trolling, and sexualized language [CODE_OF_CONDUCT.md:26-34](). Reports can be sent to `mcp-coc@anthropic.com` [CODE_OF_CONDUCT.md:55-57]().

---

## Technical Workflow: Schema and Docs Generation

The TypeScript definition is the source of truth for the protocol. The build system uses `tsx` to run generation scripts and `typedoc` to render documentation.

### Data Flow for Specification Changes
```mermaid
graph LR
    subgraph "Natural Language Space"
        A["Protocol Feature Request"]
    end

    subgraph "Code Entity Space"
        B["schema/draft/schema.ts"]
        C["schema/draft/schema.json"]
        D["docs/specification/draft/schema.mdx"]
        E["scripts/generate-schemas.ts"]
        F["scripts/render-seps.ts"]
    end

    A -->|"SEP Process"| B
    B -->|"npm run generate:schema"| E
    E --> C
    E --> D
    F -->|"npm run generate:seps"| G["docs/seps/"]
```

**Key Files & Scripts:**
- **Source of Truth**: `schema/draft/schema.ts` [CONTRIBUTING.md:44]()
- **JSON Schema Generator**: `scripts/generate-schemas.ts` [package.json:26]()
- **Documentation Renderer**: `typedoc` with `--schemaPageTemplate` [package.json:27]()
- **SEP Renderer**: `scripts/render-seps.ts` [package.json:28]()
- **Conflict Resolution**: Generated files use `-merge` in `.gitattributes` to prevent textual merge markers; developers must regenerate instead of manual resolution [CONTRIBUTING.md:56-67](), [.gitattributes:6-10]().

Sources: [package.json:23-46](), [CONTRIBUTING.md:42-55](), [AGENTS.md:48-57]()

---

## Build System Commands

The following `npm` scripts are used for the development workflow defined in `package.json`:

| Command | Description |
|---------|-------------|
| `npm run prep` | Full prep before committing: `check:schema:ts`, `generate`, `check:docs`, `check:seps`, and `format` [package.json:45]() |
| `npm run generate` | Regenerates all schemas and SEP documents [package.json:24]() |
| `npm run check` | Runs all schema, doc, and SEP validations [package.json:32]() |
| `npm run serve:docs` | Starts a local Mintlify server for documentation preview [package.json:43]() |
| `npm run serve:blog` | Starts a local Hugo server for blog preview [package.json:44]() |
| `npm run check:docs:links` | Validates internal documentation links using `mint broken-links` [package.json:41]() |
| `npm run format` | Auto-formats code and documentation via Prettier [package.json:29]() |

Sources: [package.json:23-46](), [CONTRIBUTING.md:60-88](), [AGENTS.md:72-95]()

---

# Page: Specification Enhancement Process (SEP)

# Specification Enhancement Process (SEP)

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [MAINTAINERS.md](MAINTAINERS.md)
- [blog/content/posts/2026-04-08-maintainer-update.md](blog/content/posts/2026-04-08-maintainer-update.md)
- [blog/static/posts/images/maintainer-update-2026-04/clare.webp](blog/static/posts/images/maintainer-update-2026-04/clare.webp)
- [blog/static/posts/images/maintainer-update-2026-04/den.jpeg](blog/static/posts/images/maintainer-update-2026-04/den.jpeg)
- [docs/community/communication.mdx](docs/community/communication.mdx)
- [docs/community/governance.mdx](docs/community/governance.mdx)
- [docs/community/sep-guidelines.mdx](docs/community/sep-guidelines.mdx)
- [docs/docs/tutorials/security/authorization.mdx](docs/docs/tutorials/security/authorization.mdx)
- [docs/seps/2575-stateless-mcp.mdx](docs/seps/2575-stateless-mcp.mdx)
- [seps/1850-pr-based-sep-workflow.md](seps/1850-pr-based-sep-workflow.md)
- [seps/2575-stateless-mcp.md](seps/2575-stateless-mcp.md)
- [seps/README.md](seps/README.md)

</details>



The Specification Enhancement Process (SEP) is the formal mechanism for proposing, discussing, and documenting changes to the Model Context Protocol. SEPs are design documents stored as markdown files in the [`seps/` directory](https://github.com/modelcontextprotocol/modelcontextprotocol/tree/main/seps) and managed through pull requests. This page describes the complete workflow for creating, sponsoring, reviewing, and finalizing SEPs, including automated tooling available for authors.

Sources: [docs/community/sep-guidelines.mdx:8-15](), [seps/1850-pr-based-sep-workflow.md:12-15]()

## What is a SEP?

A SEP (Specification Enhancement Proposal) is a design document that provides information to the MCP community or describes a new feature for the Model Context Protocol. SEPs serve three primary functions:

1.  **Proposing major new features** with detailed technical specifications.
2.  **Collecting community input** on protocol design decisions.
3.  **Documenting the rationale** behind decisions that shape the protocol.

The SEP author is responsible for building consensus within the community and documenting dissenting opinions. The revision history in Git serves as the historical record of the feature proposal.

Sources: [docs/community/sep-guidelines.mdx:8-10](), [seps/1850-pr-based-sep-workflow.md:12-15]()

## When to Use a SEP

Not all changes require a SEP. Regular pull requests are more appropriate for smaller, direct changes. The SEP process is reserved for changes substantial enough to require broad community discussion and a formal historical record.

| Scenario | Requires SEP | Example |
| :--- | :--- | :--- |
| New protocol feature or API | Yes | Adding new message types, capabilities, or server features |
| Breaking change | Yes | Non-backwards-compatible modifications to existing behavior |
| Governance/process change | Yes | Altering contribution guidelines or decision-making processes |
| Complex/controversial topic | Yes | Changes with multiple valid solutions requiring community consensus |
| Bug fix | No | Straightforward corrections to existing functionality |
| Documentation improvement | No | Clarifications or examples without semantic changes |
| Minor enhancement | No | Small improvements that don't alter core protocol behavior |

Sources: [docs/community/sep-guidelines.mdx:20-33]()

## SEP Types

SEPs are categorized into four types:

1.  **Standards Track**: Describes a new feature or implementation for the Model Context Protocol, or an interoperability standard supported outside the core protocol specification.
2.  **Extensions Track**: Describes a protocol extension. These follow the same review process as Standards Track SEPs.
3.  **Informational**: Describes a design issue or provides general guidelines to the MCP community without proposing a new feature.
4.  **Process**: Describes a process surrounding MCP or proposes changes to project processes (e.g., [SEP-1850: PR-Based SEP Workflow](seps/1850-pr-based-sep-workflow.md)).

Sources: [docs/community/sep-guidelines.mdx:38-43](), [seps/1850-pr-based-sep-workflow.md:4-4]()

## The PR-Based Workflow (SEP-1850)

As of [SEP-1850](seps/1850-pr-based-sep-workflow.md), all SEPs are submitted as pull requests containing markdown files. This workflow ensures that every SEP is versioned alongside the specification itself and uses standard GitHub review tooling.

### Workflow Diagram: Natural Language to Code Entity

This diagram bridges the conceptual "Idea" to the concrete file entities and PR states used in the repository.

```mermaid
graph TD
    subgraph "Natural Language Space"
        Idea["Feature Idea"]
        Discuss["Discord/Discussion Thread"]
    end

    subgraph "Code Entity Space"
        Template["seps/0000-slug.md (Placeholder)"]
        FinalFile["seps/{PR_NUMBER}-slug.md"]
        PR["GitHub Pull Request"]
        Maintainers["MAINTAINERS.md"]
    end

    Idea --> Discuss
    Discuss -->|Authoring| Template
    Template -->|git push| PR
    PR -->|Rename File| FinalFile
    Maintainers -->|Assign Sponsor| PR
    FinalFile -->|Maintainer Approval| Accepted["Status: Accepted"]
```

Sources: [seps/1850-pr-based-sep-workflow.md:34-46](), [docs/community/sep-guidelines.mdx:48-69]()

## SEP States and Lifecycle

SEPs progress through a defined set of states. Status changes are reflected both in the file's preamble and via GitHub PR labels.

| State | Meaning |
| :--- | :--- |
| `draft` | Has a sponsor, undergoing informal review. |
| `in-review` | Ready for formal Core Maintainer review. |
| `accepted` | Approved, awaiting implementation + conformance tests. |
| `rejected` | Declined by Core Maintainers. |
| `withdrawn` | Author withdrew the proposal. |
| `final` | Complete with implementation and conformance tests. |
| `superseded` | Replaced by a newer SEP. |
| `dormant` | No sponsor found within 6 months; can be revived. |

Sources: [docs/community/sep-guidelines.mdx:103-113](), [seps/1850-pr-based-sep-workflow.md:64-72]()

## Authoring and AI Assistance

### The Claude Plugin Skill
Authors can use the `/draft-sep` skill (documented in `plugins/mcp-spec`) to assist in creating high-quality proposals. This tool facilitates an interview process to ensure alignment with [MCP design principles](docs/community/sep-guidelines.mdx:12-12).

```mermaid
sequenceDiagram
    participant User
    participant Skill as /draft-sep Skill
    participant Repo as seps/ directory
    participant GH as GitHub PR

    User->>Skill: /draft-sep "Stateless Protocol"
    Skill->>User: Interview (Type, Breaking Change?, etc.)
    Skill->>Repo: Generate 0000-stateless-mcp.md
    Skill->>GH: Create Pull Request
    Note over GH: PR #2575 assigned
    User->>Repo: Rename to 2575-stateless-mcp.md
```

Sources: [docs/community/sep-guidelines.mdx:82-86](), [seps/1850-pr-based-sep-workflow.md:42-45]()

### Manual Process
If not using the automated tool, authors must:
1.  Draft the proposal as a markdown file named `0000-your-feature-title.md`.
2.  Create a pull request adding the file to the `seps/` directory.
3.  Once the PR number is known, rename the file (e.g., `1850-your-feature-title.md`) and update the header.

Sources: [docs/community/sep-guidelines.mdx:82-86](), [seps/1850-pr-based-sep-workflow.md:42-45]()

## Sponsorship Requirements

A SEP cannot enter the `draft` state without a **Sponsor**. A sponsor must be a Core Maintainer or Maintainer listed in `MAINTAINERS.md`.

**Sponsor Responsibilities:**
*   **Reviewing the proposal** and providing constructive feedback.
*   **Managing status transitions** (updating the markdown file and PR labels).
*   **Initiating formal review** by presenting the SEP at Core Maintainer meetings.
*   **Tracking implementation** to ensure reference implementations and conformance tests are complete.

Sources: [seps/1850-pr-based-sep-workflow.md:48-62](), [MAINTAINERS.md:7-108]()

## Governance and Decisions

Technical governance is led by the **MCP Steering Group**, comprising Lead Maintainers, Core Maintainers, and Maintainers.

*   **Lead Maintainers (BDFL)**: Final decision authority (e.g., David Soria Parra, Den Delimarsky).
*   **Core Maintainers**: Drive overall project direction and vote on SEPs (e.g., Clare Liguori, Kurtis Van Gent).
*   **Maintainers**: Steward specific areas like SDKs or Working Groups.

Sources: [docs/community/governance.mdx:24-36](), [MAINTAINERS.md:7-21](), [blog/content/posts/2026-04-08-maintainer-update.md:15-15]()

## Conformance and Finalization

For Standards Track SEPs that introduce observable protocol behavior, a **conformance test** must be merged before the SEP reaches `final` status. A reference implementation must also be completed.

Sources: [docs/community/sep-guidelines.mdx:101-102](), [seps/1850-pr-based-sep-workflow.md:71-71]()

---

# Page: Schema Development and Generation

# Schema Development and Generation

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitattributes](.gitattributes)
- [.github/dependabot.yml](.github/dependabot.yml)
- [.prettierignore](.prettierignore)
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [README.md](README.md)
- [SECURITY.md](SECURITY.md)
- [docs/community/security.mdx](docs/community/security.mdx)
- [docs/specification/2025-06-18/schema.mdx](docs/specification/2025-06-18/schema.mdx)
- [docs/specification/2025-11-25/schema.mdx](docs/specification/2025-11-25/schema.mdx)
- [docs/style.css](docs/style.css)
- [package-lock.json](package-lock.json)
- [package.json](package.json)
- [schema/2025-11-25/schema.json](schema/2025-11-25/schema.json)
- [schema/2025-11-25/schema.ts](schema/2025-11-25/schema.ts)
- [schema/draft/schema.mdx](schema/draft/schema.mdx)
- [scripts/generate-schemas.ts](scripts/generate-schemas.ts)
- [scripts/pull-registry-docs.sh](scripts/pull-registry-docs.sh)
- [tsconfig.json](tsconfig.json)
- [typedoc.config.mjs](typedoc.config.mjs)
- [typedoc.plugin.mjs](typedoc.plugin.mjs)

</details>



This document covers the technical workflow for developing and maintaining the MCP protocol schemas. It explains how to edit TypeScript schema definitions, generate derived artifacts (JSON Schema and MDX documentation), and validate changes through the pipeline.

The schema system manages the transformation of canonical TypeScript schemas into multiple generated artifacts:
- **TypeScript schemas** (`schema/*/schema.ts`) are the single source of truth. [schema/2025-11-25/schema.ts:8-9]()
- **JSON schemas** (`schema/*/schema.json`) are generated for machine consumption. [schema/2025-11-25/schema.json:1-3]()
- **MDX documentation** (`docs/specification/*/schema.mdx`) is generated for human-readable API reference. [docs/specification/2025-11-25/schema.mdx:1-13]()

## Schema Generation Pipeline

The generation pipeline transforms TypeScript source files into artifacts using two parallel paths.

```mermaid
graph TB
    subgraph "Source of Truth"
        DraftTS["schema/draft/schema.ts<br/>TypeScript Definitions"]
        V20251125TS["schema/2025-11-25/schema.ts"]
    end
    
    subgraph "Generation Tools"
        GenScript["tsx scripts/generate-schemas.ts<br/>JSON Schema Generator"]
        TypeDocTool["typedoc + typedoc.plugin.mjs<br/>MDX Generator"]
    end
    
    subgraph "Generated Artifacts"
        DraftJSON["schema/draft/schema.json"]
        V20251125JSON["schema/2025-11-25/schema.json"]
        
        DraftMDX["docs/specification/draft/schema.mdx"]
        V20251125MDX["docs/specification/2025-11-25/schema.mdx"]
    end
    
    DraftTS -->|typescript-json-schema| GenScript
    V20251125TS -->|typescript-json-schema| GenScript
    
    GenScript -->|writes| DraftJSON
    GenScript -->|writes| V20251125JSON
    
    DraftTS -->|typedoc --schemaPageTemplate| TypeDocTool
    V20251125TS -->|typedoc --schemaPageTemplate| TypeDocTool
    
    TypeDocTool -->|writes| DraftMDX
    TypeDocTool -->|writes| V20251125MDX
```
**Title: Schema Generation Pipeline Architecture**

Sources: [package.json:23-28](), [scripts/generate-schemas.ts:1-35](), [typedoc.config.mjs:21]()

## Source-of-Truth (TypeScript)

The protocol is defined using TypeScript interfaces and type aliases. This provides type safety for SDKs and clear documentation through TSDoc comments.

| Entity | Role | File Example |
|--------|------|--------------|
| `JSONRPCMessage` | Discriminated union of all valid messages | [schema/2025-11-25/schema.ts:8-9]() |
| `InitializeRequest` | Definition for the handshake start | [schema/2025-11-25/schema.ts:251-260]() |
| `ServerCapabilities` | Registry of supported features | [schema/2025-11-25/schema.ts:340-343]() |
| `@category` | Metadata for documentation grouping | [schema/2025-11-25/schema.ts:6-7]() |
| `LATEST_PROTOCOL_VERSION` | Internal constant for versioning | [schema/2025-11-25/schema.ts:12]() |

Sources: [schema/2025-11-25/schema.ts:1-343]()

## JSON Schema Generation

The project uses `typescript-json-schema` to extract JSON Schema definitions from the TypeScript source. [package.json:62]()

### Generation Logic
The script `scripts/generate-schemas.ts` orchestrates the extraction. For modern schemas, it applies transformations to align with specific JSON Schema dialects. [package.json:26]()

### Validation
The project includes a validation step for examples to ensure they match the generated schemas. [package.json:36]()
- **Script**: `scripts/validate-examples.ts`
- **Tool**: `ajv` (Another JSON Schema Validator) is used for schema validation. [package.json:49]()
- **Formats**: `ajv-formats` provides validation for standard string formats. [package.json:50]()

Sources: [package.json:26](), [package.json:35-36](), [package.json:49-50]()

## Documentation Generation (TypeDoc)

Human-readable documentation is generated using TypeDoc with a custom plugin located at `typedoc.plugin.mjs`. [typedoc.config.mjs:21]()

### Documentation Flow

```mermaid
graph LR
    subgraph "Code Entity Space"
        TS["schema.ts"]
        Decl["DeclarationReflection"]
        Context["DefaultThemeRenderContext"]
    end

    subgraph "Natural Language Space"
        Plugin["typedoc.plugin.mjs"]
        MDX_Temp["schema.mdx Template"]
        Final_MDX["Final Documentation"]
    end

    TS -->|Parse| Decl
    Decl -->|Process| Plugin
    Plugin -->|renderReflection| Context
    Plugin -->|renderTemplate| Final_MDX
    MDX_Temp -->|Inject| Final_MDX
```
**Title: Bridge from TypeScript Entities to MDX Documentation**

### Plugin Implementation
The plugin implements a custom `SchemaPageRouter` to handle Mintlify-compatible URL anchoring. [typedoc.plugin.mjs:47-64]()
- **`renderTemplate`**: Replaces category placeholders (e.g., `{/* @category JSON-RPC */}`) in the MDX template with rendered type information. [typedoc.plugin.mjs:93-121]()
- **`renderReflection`**: Converts TypeScript declarations (Interfaces, Type Aliases) into HTML/JSX blocks by calling `context.reflectionPreview` and `context.commentSummary`. [typedoc.plugin.mjs:195-215]()
- **Markdown Escaping**: `MARKDOWN_SPECIAL_CHARS` (like `[`, `_`, `{`) are converted to HTML entities to prevent JSX parsing errors in the output MDX. [typedoc.plugin.mjs:7-13]()

Sources: [typedoc.plugin.mjs:1-215](), [typedoc.config.mjs:1-24](), [package.json:27]()

## Build and Check Commands

The following `npm` scripts are used to manage the schema lifecycle:

| Command | Action | Implementation |
|---------|--------|----------------|
| `npm run generate:schema:json` | Generates JSON schemas | [package.json:26]() |
| `npm run generate:schema:md` | Generates MDX docs via `typedoc` | [package.json:27]() |
| `npm run check:schema:ts` | Validates TS source with `tsc` and `eslint` | [package.json:34]() |
| `npm run check:schema:json` | Checks if JSON schemas are up-to-date | [package.json:35]() |
| `npm run check:schema:examples` | Validates example blocks with `ajv` | [package.json:36]() |
| `npm run check:schema:md` | Compares generated MDX with existing docs | [package.json:37]() |
| `npm run prep` | Runs full generate and check suite | [package.json:45]() |

### Development Workflow
Developers modify `schema/draft/schema.ts` [CONTRIBUTING.md:44]() and run `npm run generate:schema` to update the corresponding JSON and MDX files. [CONTRIBUTING.md:50-53]() Manual editing of generated files is prohibited; merge conflicts are resolved by regenerating artifacts after fixing the source TypeScript. [CONTRIBUTING.md:56-65]()

Sources: [package.json:23-45](), [CONTRIBUTING.md:42-67]()

---

# Page: Build System and Automation

# Build System and Automation

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitattributes](.gitattributes)
- [.github/dependabot.yml](.github/dependabot.yml)
- [.github/workflows/blog-preview.yml](.github/workflows/blog-preview.yml)
- [.github/workflows/cut-release.yml](.github/workflows/cut-release.yml)
- [.github/workflows/deploy-blog.yml](.github/workflows/deploy-blog.yml)
- [.github/workflows/main.yml](.github/workflows/main.yml)
- [.github/workflows/markdown-format.yml](.github/workflows/markdown-format.yml)
- [.github/workflows/publish-release.yml](.github/workflows/publish-release.yml)
- [.github/workflows/render-seps.yml](.github/workflows/render-seps.yml)
- [.github/workflows/sep-lifecycle-manual.yml](.github/workflows/sep-lifecycle-manual.yml)
- [.github/workflows/sep-lifecycle.yml](.github/workflows/sep-lifecycle.yml)
- [.github/workflows/sep-reminder.yml](.github/workflows/sep-reminder.yml)
- [.github/workflows/slash-commands.yml](.github/workflows/slash-commands.yml)
- [.github/workflows/stage-blog.yml](.github/workflows/stage-blog.yml)
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [README.md](README.md)
- [SECURITY.md](SECURITY.md)
- [docs/community/security.mdx](docs/community/security.mdx)
- [package-lock.json](package-lock.json)
- [package.json](package.json)

</details>



This document describes the automated build system, npm scripts, and GitHub Actions workflows for the Model Context Protocol (MCP) specification repository. The system manages the lifecycle of the protocol through automated schema generation, documentation rendering, and rigorous validation of all artifacts.

## npm Scripts Overview

The build system is orchestrated through npm scripts defined in `package.json`. These scripts handle generation, formatting, and validation of both the machine-readable protocol and human-readable documentation.

### Generation Scripts

| Script | Command | Purpose |
|--------|---------|---------|
| `npm run generate` | `npm run generate:schema && npm run generate:seps` | Entry point for all generation tasks. [package.json:24]() |
| `npm run generate:schema` | `npm run generate:schema:json & npm run generate:schema:md & wait` | Generates JSON schemas and MDX documentation in parallel. [package.json:25]() |
| `npm run generate:schema:json` | `tsx scripts/generate-schemas.ts` | Transforms TypeScript definitions into JSON schemas. [package.json:26]() |
| `npm run generate:schema:md` | `find schema/*/schema.mdx ... xargs typedoc` | Uses TypeDoc with a custom template to generate schema reference docs. [package.json:27]() |
| `npm run generate:seps` | `tsx scripts/render-seps.ts` | Renders Specification Enhancement Proposals (SEPs). [package.json:28]() |

### Validation and Quality Scripts

| Script | Command | Purpose |
|--------|---------|---------|
| `npm run check` | `check:schema && check:docs && check:seps` | Comprehensive validation suite. [package.json:32]() |
| `npm run check:schema:ts` | `tsc --noEmit && eslint schema/ && prettier --check` | Validates TypeScript correctness, linting, and formatting. [package.json:34]() |
| `npm run check:schema:json` | `tsx scripts/generate-schemas.ts --check` | Verifies committed JSON schemas match TypeScript sources. [package.json:35]() |
| `npm run check:schema:examples` | `tsx scripts/validate-examples.ts` | Validates example payloads against generated schemas. [package.json:36]() |
| `npm run check:schema:md` | `typedoc ... | cmp docs/specification/...` | Verifies MDX documentation is up to date. [package.json:37]() |
| `npm run check:docs:links` | `cd docs && npx mint broken-links` | Checks for broken internal links in documentation. [package.json:41]() |
| `npm run prep` | Sequential run of checks, generation, and formatting | Standard pre-commit workflow for developers. [package.json:45]() |

**Sources:** [package.json:23-46]()

## Build System Architecture

The build system bridges the gap between TypeScript-defined protocol entities and the generated artifacts consumed by the ecosystem.

### Data Flow and Entity Mapping

The following diagram illustrates how "Natural Language Space" requirements (like protocol features) are processed through "Code Entity Space" tools into final artifacts.

**Build Pipeline and Entity Association:**

```mermaid
graph TB
    subgraph "Natural Language Space (Requirements)"
        ReqSpec["Protocol Features"]
        ReqDocs["Human Documentation"]
        ReqSEPs["Evolution Proposals"]
    end

    subgraph "Code Entity Space (Implementation)"
        SchemaTS["schema/*/schema.ts<br/>(Source of Truth)"]
        TemplateMDX["schema/*/schema.mdx<br/>(Documentation Template)"]
        SEPFiles["seps/*.md<br/>(Raw Proposals)"]
        
        GenScript["scripts/generate-schemas.ts<br/>(JSON Generator)"]
        DocTool["typedoc<br/>(Documentation Engine)"]
        SEPRenderer["scripts/render-seps.ts<br/>(SEP Generator)"]
    end

    subgraph "Artifact Space (Output)"
        SchemaJSON["schema/*/schema.json<br/>(Machine Readable)"]
        RefMDX["docs/specification/*/schema.mdx<br/>(Web Documentation)"]
        FinalSEPs["docs/seps/*.mdx<br/>(Rendered Proposals)"]
    end

    ReqSpec --> SchemaTS
    ReqDocs --> TemplateMDX
    ReqSEPs --> SEPFiles

    SchemaTS --> GenScript
    GenScript --> SchemaJSON

    SchemaTS --> DocTool
    TemplateMDX --> DocTool
    DocTool --> RefMDX

    SEPFiles --> SEPRenderer
    SEPRenderer --> FinalSEPs
```

**Sources:** [package.json:23-45](), [CONTRIBUTING.md:42-55](), [README.md:11-13]()

## Documentation Generation System

The repository uses a documentation pipeline that transforms TypeScript source-of-truth definitions into MDX pages compatible with Mintlify.

### Generation Logic

The `generate:schema:md` script utilizes `typedoc` with a specific template to create documentation. It targets TypeScript files in the `schema/` directory and outputs rendered MDX to `docs/specification/`.

**Documentation Transformation Flow:**

```mermaid
graph LR
    subgraph "Source Definitions"
        SchemaTS["schema/*/schema.ts<br/>(TypeScript Source)"]
        TemplateMDX["schema/*/schema.mdx<br/>(Template)"]
    end

    subgraph "Processing"
        TypeDoc["typedoc --entryPoints ... --schemaPageTemplate"]
    end

    subgraph "Mintlify Output"
        FinalMDX["docs/specification/*/schema.mdx"]
    end

    SchemaTS --> TypeDoc
    TemplateMDX --> TypeDoc
    TypeDoc --> FinalMDX
```

**Sources:** [package.json:27](), [CONTRIBUTING.md:50-54]()

## CI/CD Workflows

The repository uses GitHub Actions for continuous validation, release management, and automated maintenance.

### Validation Workflow (`main.yml`)
Runs on every push to `main` and all pull requests. It ensures that the generated `schema.json` and `schema.mdx` files are perfectly synchronized with the TypeScript source code.
- **Steps**: `npm run check:schema:ts` → `npm run check:schema:json` → `npm run check:schema:md`.
- **Sources:** [.github/workflows/main.yml:1-32]()

### Release Management Workflows
The release process is split into two phases:
1. **Cut Release (`cut-release.yml`)**: A manual workflow (`workflow_dispatch`) that can cut a Release Candidate (RC) or a Final release. 
   - **RC Mode**: Creates a `<version>-RC` tag and a prerelease on GitHub [.github/workflows/cut-release.yml:36-72]().
   - **Final Mode**: Promotes the `draft/` specification to a versioned directory (e.g., `docs/specification/YYYY-MM-DD/`), patches `docs/docs.json` for Mintlify versioning, and opens a release PR [.github/workflows/cut-release.yml:78-163]().
2. **Publish Release**: While not shown in full, this companion job handles tagging the GA release after the PR created by `cut-release.yml` is merged [.github/workflows/cut-release.yml:7-8]().

### SEP Lifecycle Automation (`sep-lifecycle.yml`)
This workflow automates the management of Specification Enhancement Proposals.
- **Triggers**: On labeling, unlabeling, assigning, or opening of issues/PRs, and on a weekly schedule (Monday 9 AM UTC) [.github/workflows/sep-lifecycle.yml:3-12]().
- **Functions**: Executes the automation tool located in `tools/sep-automation` to process transitions and optionally post to Discord [.github/workflows/sep-lifecycle.yml:84-105]().

### Blog and Site Deployment
- **Deploy Blog (`deploy-blog.yml`)**: Builds the Hugo-based blog from the `blog/` directory using a custom `hugo-build` action and deploys it to GitHub Pages [.github/workflows/deploy-blog.yml:1-59]().
- **Slash Commands (`slash-commands.yml`)**: Processes maintainer commands (like `/lgtm`, `/hold`, `/stageblog`) and handles auto-approval for narrowly-scoped Dependabot PRs [.github/workflows/slash-commands.yml:1-49]().

**Sources:** [.github/workflows/main.yml:1-32](), [.github/workflows/cut-release.yml:1-170](), [.github/workflows/sep-lifecycle.yml:1-113](), [.github/workflows/deploy-blog.yml:1-59](), [.github/workflows/slash-commands.yml:1-49]()

---

# Page: Documentation Generation System

# Documentation Generation System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.prettierignore](.prettierignore)
- [blog/assets/css/extended/custom.css](blog/assets/css/extended/custom.css)
- [blog/hugo.toml](blog/hugo.toml)
- [blog/layouts/_default/archives.html](blog/layouts/_default/archives.html)
- [blog/layouts/_default/list.html](blog/layouts/_default/list.html)
- [blog/layouts/_default/search.html](blog/layouts/_default/search.html)
- [blog/layouts/_default/terms.html](blog/layouts/_default/terms.html)
- [blog/layouts/index.html](blog/layouts/index.html)
- [blog/layouts/partials/footer.html](blog/layouts/partials/footer.html)
- [blog/layouts/partials/header.html](blog/layouts/partials/header.html)
- [blog/layouts/partials/post_meta.html](blog/layouts/partials/post_meta.html)
- [blog/layouts/partials/post_nav_links.html](blog/layouts/partials/post_nav_links.html)
- [blog/layouts/partials/templates/schema_json.html](blog/layouts/partials/templates/schema_json.html)
- [docs/seps/1024-mcp-client-security-requirements-for-local-server-.mdx](docs/seps/1024-mcp-client-security-requirements-for-local-server-.mdx)
- [docs/seps/1034--support-default-values-for-all-primitive-types-in.mdx](docs/seps/1034--support-default-values-for-all-primitive-types-in.mdx)
- [docs/seps/1036-url-mode-elicitation-for-secure-out-of-band-intera.mdx](docs/seps/1036-url-mode-elicitation-for-secure-out-of-band-intera.mdx)
- [docs/seps/1046-support-oauth-client-credentials-flow-in-authoriza.mdx](docs/seps/1046-support-oauth-client-credentials-flow-in-authoriza.mdx)
- [docs/seps/1302-formalize-working-groups-and-interest-groups-in-mc.mdx](docs/seps/1302-formalize-working-groups-and-interest-groups-in-mc.mdx)
- [docs/seps/1303-input-validation-errors-as-tool-execution-errors.mdx](docs/seps/1303-input-validation-errors-as-tool-execution-errors.mdx)
- [docs/seps/1319-decouple-request-payload-from-rpc-methods-definiti.mdx](docs/seps/1319-decouple-request-payload-from-rpc-methods-definiti.mdx)
- [docs/seps/991-enable-url-based-client-registration-using-oauth-c.mdx](docs/seps/991-enable-url-based-client-registration-using-oauth-c.mdx)
- [docs/spec-version-warning.js](docs/spec-version-warning.js)
- [docs/specification/2025-06-18/schema.mdx](docs/specification/2025-06-18/schema.mdx)
- [docs/specification/2025-11-25/schema.mdx](docs/specification/2025-11-25/schema.mdx)
- [docs/style.css](docs/style.css)
- [schema/2025-11-25/schema.json](schema/2025-11-25/schema.json)
- [schema/2025-11-25/schema.ts](schema/2025-11-25/schema.ts)
- [scripts/pull-registry-docs.sh](scripts/pull-registry-docs.sh)
- [typedoc.config.mjs](typedoc.config.mjs)
- [typedoc.plugin.mjs](typedoc.plugin.mjs)

</details>



## Purpose and Scope

The documentation system implements a dual-track publishing architecture that serves both technical reference documentation and community blog content. Mintlify powers the main documentation site at `modelcontextprotocol.io`, while Hugo with the PaperMod theme hosts the blog at `blog.modelcontextprotocol.io`. This page covers the TypeDoc configuration for schema generation, the custom plugin for Mintlify compatibility, the Hugo-based blog system, and the dynamic version warning system.

For information about the build system and CI/CD workflows that validate and generate documentation artifacts, see [Build System and Automation](#7.4). For details on the schema generation process itself, see [Schema Development and Generation](#7.3).

## Architecture Overview

The documentation system consists of two independent publishing tracks with distinct toolchains and content types:

```mermaid
graph TB
    subgraph "Content_Sources"
        HandWritten["Hand-Written MDX<br/>docs/**/*.mdx"]
        SchemaTS["Schema TypeScript<br/>schema/*/schema.ts"]
        BlogMD["Blog Markdown<br/>blog/content/**/*.md"]
    end
    
    subgraph "Generation_Pipeline"
        TypeDocPlugin["TypeDoc Plugin<br/>typedoc.plugin.mjs<br/>schema-page output"]
    end
    
    subgraph "Configuration"
        HugoTOML["hugo.toml<br/>Hugo Config"]
        StyleCSS["style.css<br/>Custom Styling"]
        SpecWarning["spec-version-warning.js<br/>Version Banner"]
    end
    
    subgraph "Published_Sites"
        Mintlify["Mintlify<br/>modelcontextprotocol.io<br/>Main Documentation"]
        HugoBlog["Hugo Site<br/>blog.modelcontextprotocol.io<br/>Community Blog"]
    end
    
    SchemaTS -->|"typedoc"| TypeDocPlugin
    TypeDocPlugin -->|"generates"| SchemaMDX["schema.mdx<br/>Generated API Docs"]
    
    HandWritten --> Mintlify
    SchemaMDX --> Mintlify
    StyleCSS --> Mintlify
    SpecWarning --> Mintlify
    
    BlogMD --> HugoTOML
    HugoTOML --> HugoBlog
```

**Sources:** [typedoc.plugin.mjs:23-44](), [blog/hugo.toml:1-106](), [docs/style.css:1-207]()

## TypeDoc Schema Generation

The documentation for the MCP specification is generated directly from the TypeScript source-of-truth in the `schema/` directory (e.g., `schema/2025-11-25/schema.ts`).

### Configuration

The TypeDoc configuration is managed in `typedoc.config.mjs`. It filters internal symbols and JSON-Schema specific tags that are not relevant for protocol consumers.

| Property | Value | Purpose |
|----------|-------|---------|
| `out` | `"tmp"` | Temporary output directory (actual output via plugin) |
| `excludeInternal` | `true` | Hides symbols marked as internal implementation details [typedoc.config.mjs:7-7]() |
| `excludeTags` | `["@format", "@maximum", ...]` | Filters JSON Schema metadata from documentation [typedoc.config.mjs:8-15]() |
| `plugin` | `["./typedoc.plugin.mjs"]` | Loads the custom Mintlify-compatibility plugin [typedoc.config.mjs:21-21]() |

**Sources:** [typedoc.config.mjs:1-24](), [schema/2025-11-25/schema.ts:1-12]()

### Custom TypeDoc Plugin Architecture

The custom plugin `typedoc.plugin.mjs` transforms TypeDoc's internal reflection model into Mintlify-compatible MDX. It bypasses the standard HTML renderer to produce Markdown that preserves Mintlify's specific component syntax and CSS hooks.

```mermaid
graph TD
    "typedoc-run"["TypeDoc Run"] --> "load-fn"["load(app)"]
    "load-fn" --> "add-output"["app.outputs.addOutput('schema-page')"]
    "add-output" --> "SchemaPageRouter"["SchemaPageRouter"]
    "SchemaPageRouter" --> "buildPageEvents"["buildPageEvents()"]
    "buildPageEvents" --> "renderTemplate"["renderTemplate()"]
    "renderTemplate" --> "renderCategory"["renderCategory()"]
    "renderCategory" --> "renderReflection"["renderReflection()"]
    "renderReflection" --> "output-mdx"["stdout -> schema.mdx"]
```

**Key Implementation Details:**
- **SchemaPageRouter**: Overrides default URL generation to create Mintlify-compatible lowercase anchor IDs by replacing dots, slashes, and hashes with dashes [typedoc.plugin.mjs:47-64]().
- **renderCategory**: Groups reflections based on the `@category` JSDoc tag found in the schema source [typedoc.plugin.mjs:177-188](), [schema/2025-11-25/schema.ts:6-7]().
- **getReflectionOrder**: Implements a protocol-specific sorting logic where `Request` types appear before `Result` or `Notification` types [typedoc.plugin.mjs:137-152]().

**Sources:** [typedoc.plugin.mjs:1-243](), [schema/2025-11-25/schema.ts:6-9]()

### Mintlify Compatibility and Styling

Because Mintlify uses a custom Markdown parser, the plugin performs extensive character escaping and tag transformations to prevent rendering errors.

- **Character Escaping**: Brackets, underscores, and braces are converted to HTML entities (e.g., `[` to `&#x5B;`) using `MARKDOWN_SPECIAL_CHARS_HTML_ENTITIES` to prevent them from being interpreted as MDX/JSX components [typedoc.plugin.mjs:7-13]().
- **Heading Transformation**: HTML headings (`<hN>`) are converted to `<div>` elements with `data-typedoc-h` attributes to avoid interfering with Mintlify's auto-generated Table of Contents [typedoc.plugin.mjs:213-216]().
- **CSS Hooks**: The `docs/style.css` file uses the `body:has(#schema-reference)` selector to apply specialized styling to these generated pages, including custom syntax highlighting for `tsd-signature` and `tsd-comment` elements [docs/style.css:102-189]().

**Sources:** [typedoc.plugin.mjs:213-238](), [docs/style.css:102-189]()

## Hugo Blog System

The blog at `blog.modelcontextprotocol.io` is built using Hugo and the PaperMod theme. It serves as the primary channel for protocol updates and ecosystem news.

### Theme Customization

The system applies significant customizations to PaperMod via `blog/assets/css/extended/custom.css` and template overrides.

- **Color Tokens**: Defines indigo-based brand accents (`--link: #4f46e5` for light, `#818cf8` for dark) [blog/assets/css/extended/custom.css:1-14]().
- **Accessibility**: Enhances `:focus-visible` indicators and adds a skip-link for keyboard navigation [blog/assets/css/extended/custom.css:26-41](), [blog/assets/css/extended/custom.css:81-95]().
- **Search Integration**: Configures PaperMod's Fuse.js client-side search via `blog/hugo.toml` and custom CSS to match the visual style of the main documentation site [blog/hugo.toml:11-13](), [blog/assets/css/extended/custom.css:49-78]().

**Sources:** [blog/hugo.toml:7-13](), [blog/assets/css/extended/custom.css:1-243]()

### Paginator and Layout Overrides

The `blog/layouts/_default/list.html` override modifies standard PaperMod behavior:
1. **Home Info Persistence**: The intro card (title and blurb defined in `params.homeInfoParams`) appears on every paginated page, not just the first [blog/layouts/_default/list.html:7-9](), [blog/hugo.toml:40-42]().
2. **Page Counter**: Adds an absolutely-positioned "Page N of M" counter between the "Prev" and "Next" buttons [blog/layouts/_default/list.html:110-128]().

**Sources:** [blog/layouts/_default/list.html:1-133](), [blog/hugo.toml:40-42]()

## Spec Version Warning System

The `docs/spec-version-warning.js` script provides a dynamic banner system that alerts users when they are viewing an older or draft version of the specification.

### Dynamic Resolution

Instead of hardcoding the "latest" version, the script performs a `HEAD` request to `/specification/latest` and parses the redirect destination to determine the current stable version [docs/spec-version-warning.js:60-72]().

```mermaid
sequenceDiagram
    participant User as Browser
    participant Script as spec-version-warning.js
    participant Server as Mintlify Edge
    
    User->>Script: Loads page /specification/2025-06-18/schema
    Script->>Server: HEAD /specification/latest
    Server-->>Script: 302 Redirect to /specification/2025-11-25
    Script->>Script: resolveLatestVersion() -> 2025-11-25
    Script->>Script: parseSpecPath() -> current: 2025-06-18
    Script->>User: createBanner() -> Inject Warning
```

**Sources:** [docs/spec-version-warning.js:54-72](), [docs/spec-version-warning.js:107-156]()

### Banner Implementation

The script uses a `MutationObserver` to ensure the banner persists across SPA (Single Page Application) transitions within the Mintlify site [docs/spec-version-warning.js:165-173](). It differentiates between "draft" pages (Info style) and "older version" pages (Warning style) by checking if the version string matches `DRAFT_VERSION` ("draft") [docs/spec-version-warning.js:10-12](), [docs/spec-version-warning.js:135-140]().

**Sources:** [docs/spec-version-warning.js:74-103](), [docs/spec-version-warning.js:165-173]()

---

# Page: SEP Lifecycle Automation Tool

# SEP Lifecycle Automation Tool

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/blog-preview.yml](.github/workflows/blog-preview.yml)
- [.github/workflows/cut-release.yml](.github/workflows/cut-release.yml)
- [.github/workflows/deploy-blog.yml](.github/workflows/deploy-blog.yml)
- [.github/workflows/main.yml](.github/workflows/main.yml)
- [.github/workflows/markdown-format.yml](.github/workflows/markdown-format.yml)
- [.github/workflows/publish-release.yml](.github/workflows/publish-release.yml)
- [.github/workflows/render-seps.yml](.github/workflows/render-seps.yml)
- [.github/workflows/sep-lifecycle-manual.yml](.github/workflows/sep-lifecycle-manual.yml)
- [.github/workflows/sep-lifecycle.yml](.github/workflows/sep-lifecycle.yml)
- [.github/workflows/slash-commands.yml](.github/workflows/slash-commands.yml)
- [.github/workflows/stage-blog.yml](.github/workflows/stage-blog.yml)
- [tools/sep-automation/package-lock.json](tools/sep-automation/package-lock.json)
- [tools/sep-automation/package.json](tools/sep-automation/package.json)
- [tools/sep-automation/src/config.ts](tools/sep-automation/src/config.ts)
- [tools/sep-automation/src/github/client.ts](tools/sep-automation/src/github/client.ts)
- [tools/sep-automation/src/github/types.ts](tools/sep-automation/src/github/types.ts)
- [tools/sep-automation/src/index.ts](tools/sep-automation/src/index.ts)
- [tools/sep-automation/src/maintainers/resolver.ts](tools/sep-automation/src/maintainers/resolver.ts)
- [tools/sep-automation/src/processor.ts](tools/sep-automation/src/processor.ts)
- [tools/sep-automation/src/sep/analyzer.ts](tools/sep-automation/src/sep/analyzer.ts)
- [tools/sep-automation/test/unit/config.test.ts](tools/sep-automation/test/unit/config.test.ts)

</details>



The `tools/sep-automation` utility is a TypeScript-based application designed to manage the Specification Enhancement Process (SEP) lifecycle automatically. It enforces governance rules, manages GitHub labels and assignments, and provides community notifications via Discord [tools/sep-automation/package.json:1-11]().

## Overview

The tool operates by scanning GitHub Issues and Pull Requests for SEP-related labels and content. It ensures that every SEP has a valid sponsor from the steering committee, manages state transitions (e.g., from `proposal` to `draft`), and pings inactive participants to maintain momentum in the protocol evolution [tools/sep-automation/src/processor.ts:1-15]().

### Key Responsibilities
- **Sponsorship Enforcement**: Verifies that SEPs are assigned to members of the `steering-committee` or its descendant teams [.github/workflows/sep-lifecycle.yml:95-101](), [tools/sep-automation/src/maintainers/resolver.ts:9-12]().
- **Lifecycle State Management**: Automates transitions between `proposal`, `draft`, `in-review`, and `accepted` based on repository activity and labeling [.github/workflows/slash-commands.yml:34-41]().
- **Notification & Reporting**: Sends summaries of SEP activity to Discord and generates logs for maintainer review [.github/workflows/sep-lifecycle.yml:103-112]().
- **Staleness Tracking**: Identifies SEPs that have lacked activity and pings the relevant stakeholders [tools/sep-automation/src/processor.ts:1-15]().

## System Architecture

The automation tool is structured into functional handlers managed by a central `SEPProcessor`.

### Code Entity Space to Logic Mapping

The following diagram maps the high-level automation logic to the specific TypeScript classes and GitHub Actions that implement them.

**SEP Automation Component Map**
```mermaid
graph TD
    subgraph "GitHub Actions Layer"
        GHA_Sched["sep-lifecycle.yml (Cron)"]
        GHA_Event["sep-lifecycle.yml (Labeled/Opened)"]
        GHA_Manual["sep-lifecycle-manual.yml"]
    end

    subgraph "Logic Layer (tools/sep-automation/src/)"
        Processor["SEPProcessor (processor.ts)"]
        Resolver["MaintainerResolver (maintainers/resolver.ts)"]
        GHClient["GitHubClient (github/client.ts)"]
        Discord["DiscordHook"]
    end

    GHA_Sched -->|"npm start"| Processor
    GHA_Event -->|"npm start --issue N"| Processor
    GHA_Manual --> Processor

    Processor --> Resolver
    Processor --> GHClient
    Processor --> Discord

    Resolver -->|"getAllDescendantTeams"| GHClient
```
**Sources:** [.github/workflows/sep-lifecycle.yml:1-13](), [.github/workflows/sep-lifecycle-manual.yml:3-9](), [tools/sep-automation/src/processor.ts:1-15](), [tools/sep-automation/src/maintainers/resolver.ts:14-25]().

## Implementation Details

### MaintainerResolver
The `MaintainerResolver` class is responsible for determining who is authorized to sponsor a SEP. It defines the `steering-committee` as the `SPONSOR_ROOT_TEAM` [tools/sep-automation/src/maintainers/resolver.ts:12]().

- **Dynamic Team Discovery**: It uses `github.getAllDescendantTeams` to find all sub-teams under the steering committee [tools/sep-automation/src/maintainers/resolver.ts:46-49]().
- **Membership Caching**: To avoid hitting GitHub API rate limits, it caches the set of valid sponsors in `sponsorSet` [tools/sep-automation/src/maintainers/resolver.ts:31-35]().
- **Sponsorship Validation**: The `canSponsor` method checks if a specific GitHub username belongs to the discovered sponsor teams [tools/sep-automation/src/maintainers/resolver.ts:101-104]().

### SEPProcessor
The `SEPProcessor` acts as the orchestrator. When executed, it:
1.  Loads the configuration (e.g., target repository, Discord webhook URL) [.github/workflows/sep-lifecycle.yml:95-103]().
2.  Fetches issues or PRs labeled with `SEP` [.github/workflows/sep-lifecycle.yml:18-33]().
3.  Delegates state-specific logic to sub-handlers (TransitionHandler, PingHandler).
4.  Reports outcomes via `DiscordHook`.

### Data Flow: SEP Event Processing

The diagram below illustrates how a labeling event on GitHub triggers the automation tool to validate sponsorship.

**Sponsorship Validation Flow**
```mermaid
sequenceDiagram
    participant GH as "GitHub (Event)"
    participant Workflow as "sep-lifecycle.yml"
    participant Tool as "SEPProcessor"
    participant Resolver as "MaintainerResolver"
    participant Client as "GitHubClient"

    GH->>Workflow: "Label 'SEP' added to PR #123"
    Workflow->>Tool: "npm start --issue 123"
    Tool->>Client: "getIssue(123)"
    Client-->>Tool: "PR Data (Assignees: ['userA'])"
    Tool->>Resolver: "canSponsor('userA')"
    Resolver->>Client: "getAllDescendantTeams('steering-committee')"
    Client-->>Resolver: "['lead-maintainers', 'core-maintainers']"
    Resolver->>Client: "getTeamMembers('core-maintainers')"
    Client-->>Resolver: "['userA', 'userB']"
    Resolver-->>Tool: "true"
    Tool->>GH: "Add label 'proposal'"
```
**Sources:** [.github/workflows/sep-lifecycle.yml:84-95](), [tools/sep-automation/src/maintainers/resolver.ts:43-67](), [tools/sep-automation/src/maintainers/resolver.ts:101-104]().

## GitHub Actions Integration

The automation is integrated via three primary workflows:

| Workflow | Trigger | Purpose |
| :--- | :--- | :--- |
| `sep-lifecycle.yml` | `schedule` (Weekly), `labeled`, `opened` | Primary automation runner for state transitions and pings [.github/workflows/sep-lifecycle.yml:3-12](). |
| `sep-lifecycle-manual.yml` | `workflow_dispatch` | Allows maintainers to manually trigger a full sweep or process a specific issue with a `dry_run` option [.github/workflows/sep-lifecycle-manual.yml:4-14](). |
| `slash-commands.yml` | `issue_comment` | Handles `/lgtm`, `/hold`, and label cleanup (removing `in-review`, `draft`, `proposal` on acceptance) [.github/workflows/slash-commands.yml:17-41](). |

### Execution Modes
- **Single Issue Mode**: Triggered by event-driven GHA. The tool is invoked with `--issue <number>` to process only the affected item [.github/workflows/sep-lifecycle.yml:88-91]().
- **Full Sweep Mode**: Triggered by the weekly cron job. The tool scans all open SEPs to identify staleness or missing sponsors [.github/workflows/sep-lifecycle.yml:92-94]().

## Configuration and Environment

The tool requires several environment variables and secrets to function within GitHub Actions:

- `APP_ID` / `APP_PRIVATE_KEY`: Used for GitHub App authentication, providing `read:org` permissions to check team memberships [.github/workflows/sep-lifecycle.yml:96-98]().
- `MAINTAINERS_TEAM`: Set to `core-maintainers` [.github/workflows/sep-lifecycle.yml:101]().
- `DISCORD_WEBHOOK_URL`: Destination for weekly summaries and urgent alerts [.github/workflows/sep-lifecycle.yml:103]().
- `DRY_RUN`: When set to `true`, the tool logs intended actions without making API writes [.github/workflows/sep-lifecycle-manual.yml:50-54]().

**Sources:** [.github/workflows/sep-lifecycle.yml:1-113](), [.github/workflows/sep-lifecycle-manual.yml:1-81](), [tools/sep-automation/src/maintainers/resolver.ts:1-126](), [tools/sep-automation/src/processor.ts:1-15]().

---

# Page: Governance and Community

# Governance and Community

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [MAINTAINERS.md](MAINTAINERS.md)
- [blog/content/posts/2026-04-08-maintainer-update.md](blog/content/posts/2026-04-08-maintainer-update.md)
- [blog/static/posts/images/maintainer-update-2026-04/clare.webp](blog/static/posts/images/maintainer-update-2026-04/clare.webp)
- [blog/static/posts/images/maintainer-update-2026-04/den.jpeg](blog/static/posts/images/maintainer-update-2026-04/den.jpeg)
- [docs/community/charter-template.mdx](docs/community/charter-template.mdx)
- [docs/community/communication.mdx](docs/community/communication.mdx)
- [docs/community/contributor-ladder.mdx](docs/community/contributor-ladder.mdx)
- [docs/community/governance.mdx](docs/community/governance.mdx)
- [docs/community/sep-guidelines.mdx](docs/community/sep-guidelines.mdx)
- [docs/community/working-interest-groups.mdx](docs/community/working-interest-groups.mdx)
- [docs/docs/tutorials/security/authorization.mdx](docs/docs/tutorials/security/authorization.mdx)
- [docs/seps/2149-working-group-charter-template.mdx](docs/seps/2149-working-group-charter-template.mdx)
- [seps/2149-working-group-charter-template.md](seps/2149-working-group-charter-template.md)

</details>



This page documents the Model Context Protocol's governance structure, community organization, and the processes for proposing and implementing changes to the specification. It covers the maintainer hierarchy, the Specification Enhancement Proposal (SEP) workflow, Working Groups and Interest Groups, communication channels, and the project's release history.

For technical contribution guidelines including schema development and build processes, see [Development Guide](#7).

## Governance Structure

MCP adopts a hierarchical governance model to ensure transparent decision-making and community participation. The structure is established as **Model Context Protocol a Series of LF Projects, LLC** [docs/community/governance.mdx:8-10]().

### Hierarchy Overview

```mermaid
graph TB
    Lead["Lead Maintainers (2)<br/>Ultimate Authority<br/>(BDFL Model)"]
    Core["Core Maintainers (7)<br/>Overall Direction<br/>Specification Steering"]
    Maintainers["Maintainers<br/>Domain Stewards<br/>SDKs, WGs, Components"]
    Contributors["Contributors<br/>Community<br/>Issues, PRs, Discussions"]
    
    Lead -->|"appoints/removes"| Core
    Core -->|"appoints/removes"| Maintainers
    Lead -->|"veto power"| Core
    Core -->|"veto power (majority)"| Maintainers
    
    Contributors -->|"propose"| Maintainers
    Contributors -->|"propose"| Core
    Maintainers -->|"sponsor"| Core
```

**Sources:** [docs/community/governance.mdx:20-38](), [docs/community/governance.mdx:44-53](), [MAINTAINERS.md:1-110]()

### Lead Maintainers (BDFLs)
The Lead Maintainers hold final authority and serve as the project's Benevolent Dictators for Life (BDFL). They are administrators on all project infrastructure [docs/community/governance.mdx:51-53]().
- **David Soria Parra** (`@dsp-ant`)
- **Den Delimarsky** (`@localden`)

**Sources:** [MAINTAINERS.md:7-10](), [docs/community/governance.mdx:51-53]()

### Core Maintainers
Core Maintainers steer the specification and project direction. They meet bi-weekly to vote on proposals and resolve technical disputes [docs/community/governance.mdx:49-50]().
- **Caitie McCaffrey** (`@CaitieM20`)
- **Clare Liguori** (`@clareliguori`)
- **Kurtis Van Gent** (`@kurtisvg`)
- **Nick Aldridge** (`@000-000-000-000-000`)
- **Nick Cooper** (`@nickcoai`)
- **Paul Carleton** (`@pcarleton`)
- **Peter Alexander** (`@pja-ant`)

**Sources:** [MAINTAINERS.md:12-21](), [docs/community/governance.mdx:49-50]()

### Maintainers and Roles
Maintainers steward specific components. For a detailed catalog of current maintainers and their SDK/project ownership, see [Maintainers and Roles](#8.2).
- **SDK Maintainers**: Ownership of specific language SDKs such as Java, Python, TypeScript, Go, C#, Kotlin, Swift, Rust, and PHP [MAINTAINERS.md:28-108]().
- **Project Maintainers**: Stewards for tools like the **Inspector**, **Registry**, **use-mcp**, and **Reference Servers** [MAINTAINERS.md:109-146]().
- **Group Facilitators**: Leadership for Working and Interest Groups [MAINTAINERS.md:156-211]().

**Sources:** [MAINTAINERS.md:28-155](), [docs/community/governance.mdx:47-48]()

## Contributor Ladder
The project defines a formal advancement path based on earned trust and sustained engagement.

| Role | Requirement | Privileges |
| :--- | :--- | :--- |
| **Contributor** | Any contribution | Submit PRs, participate in discussions |
| **Member** | 2-3 months active | GitHub org membership, triage rights |
| **Maintainer** | 6+ months as Member | Merge rights for specific area |
| **Core Maintainer** | Invitation only | Final decision authority |

For details on requirements and advancement, see [Maintainers and Roles](#8.2).

**Sources:** [docs/community/contributor-ladder.mdx:17-26](), [docs/community/contributor-ladder.mdx:52-132]()

## Specification Enhancement Proposal (SEP) Process
The SEP process is the primary mechanism for proposing substantial protocol changes [docs/community/sep-guidelines.mdx:6-15]().

### SEP Workflow
```mermaid
stateDiagram-v2
    [*] --> Idea
    Idea --> AwaitingSponsor: Submit PR to seps/
    AwaitingSponsor --> Draft: Maintainer sponsors
    Draft --> InReview: Informal review complete
    InReview --> Accepted: Core Maintainer vote
    InReview --> Rejected: Core Maintainer vote
    Accepted --> Final: Implementation + Conformance
    AwaitingSponsor --> Dormant: No sponsor (6 months)
```

### SEP Types
1.  **Standards Track**: New features or implementation changes [docs/community/sep-guidelines.mdx:40]().
2.  **Informational**: Guidelines or design issues [docs/community/sep-guidelines.mdx:41]().
3.  **Process**: Changes to governance or processes (e.g., SEP-2149) [docs/community/sep-guidelines.mdx:42]().
4.  **Extensions Track**: Protocol extensions [docs/community/sep-guidelines.mdx:43]().

For the full process and status definitions, see [Governance Structure](#8.1).

**Sources:** [docs/community/sep-guidelines.mdx:6-69](), [docs/community/sep-guidelines.mdx:103-112]()

## Working Groups and Interest Groups
Collaboration is organized into two group types defined by SEP-2149 [seps/2149-working-group-charter-template.md:1-15]().

| Group Type | Purpose | Deliverables |
| :--- | :--- | :--- |
| **Interest Group (IG)** | Problem identification | Use cases, recommendations |
| **Working Group (WG)** | Solution development | SEPs, code, implementations |

### Active Groups
- **Transports Interest Group**: Evolution of communication mechanisms [MAINTAINERS.md:189-194]().
- **Security Interest Group**: Protocol security and threat modeling [MAINTAINERS.md:160-164]().
- **Authorization Interest Group**: OAuth 2.1 and identity integration [MAINTAINERS.md:166-170]().
- **Agents Working Group**: Agent-to-agent communication models [MAINTAINERS.md:202-206]().
- **Registry Working Group**: Management of the MCP server ecosystem [MAINTAINERS.md:122-126]().

For a full list and charters, see [Working Groups and Interest Groups](#8.3).

**Sources:** [docs/community/working-interest-groups.mdx:8-18](), [seps/2149-working-group-charter-template.md:36-40](), [MAINTAINERS.md:156-211]()

## Communication Channels
- **Discord**: Real-time coordination for contributors. Not for general support [docs/community/communication.mdx:20-22]().
- **GitHub Discussions**: Long-form debate, proposals, and roadmap planning [docs/community/communication.mdx:60-70]().
- **GitHub Issues**: Bug reports and actionable development tasks [docs/community/communication.mdx:72-83]().
- **Live Calls**: Sync sessions for WG/IG presentations [docs/community/communication.mdx:13]().

For platform links and usage guidelines, see [Communication Channels](#8.4).

**Sources:** [docs/community/communication.mdx:8-16](), [docs/community/communication.mdx:19-23]()

## Release History and Roadmap
MCP tracks its evolution through major releases and adoption milestones. Recent focus areas include the standardization of OAuth 2.1 authorization [docs/docs/tutorials/security/authorization.mdx:8-9]() and the expansion of the multi-language SDK ecosystem [MAINTAINERS.md:28-108]().

For the detailed evolution of the protocol and future priorities, see [Release History and Roadmap](#8.5).

**Sources:** [docs/docs/tutorials/security/authorization.mdx:8-9](), [MAINTAINERS.md:1-108]()

---

# Page: Governance Structure

# Governance Structure

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [MAINTAINERS.md](MAINTAINERS.md)
- [blog/content/posts/2026-04-08-maintainer-update.md](blog/content/posts/2026-04-08-maintainer-update.md)
- [blog/static/posts/images/maintainer-update-2026-04/clare.webp](blog/static/posts/images/maintainer-update-2026-04/clare.webp)
- [blog/static/posts/images/maintainer-update-2026-04/den.jpeg](blog/static/posts/images/maintainer-update-2026-04/den.jpeg)
- [docs/community/communication.mdx](docs/community/communication.mdx)
- [docs/community/governance.mdx](docs/community/governance.mdx)
- [docs/community/sep-guidelines.mdx](docs/community/sep-guidelines.mdx)
- [docs/docs/tutorials/security/authorization.mdx](docs/docs/tutorials/security/authorization.mdx)
- [seps/2085-governance-succession-and-amendment.md](seps/2085-governance-succession-and-amendment.md)

</details>



This document describes the hierarchical governance model for the Model Context Protocol project, including the roles, responsibilities, authority relationships, and succession procedures. For the complete list of current maintainers, see [Maintainers and Roles](#8.2). For information about Working Groups and Interest Groups, see [Working Groups and Interest Groups](#8.3). For SEP procedures, see [Specification Enhancement Process (SEP)](#7.2).

## Purpose and Scope

The MCP project adopts a three-tier hierarchical governance structure similar to Python, PyTorch, and other major open source projects [docs/community/governance.mdx:22-30](). This structure ensures clear decision-making authority while enabling distributed maintenance across multiple domains (SDKs, projects, working groups). The governance model balances the need for decisive leadership with community participation and transparent processes.

## Hierarchical Authority Model

The governance structure consists of three levels of maintainership, each with distinct responsibilities and authority. Together, these roles form the **MCP Steering Group** [docs/community/governance.mdx:36-37]().

### Governance Hierarchy Diagram

```mermaid
graph TB
    subgraph "Authority Hierarchy"
        Lead["Lead Maintainers (BDFL)<br/>David Soria Parra<br/>Den Delimarsky"]
        Core["Core Maintainers<br/>Specification Oversight"]
        Maint["Maintainers<br/>Domain Specialists"]
        
        Lead -->|"appoint/remove"| Core
        Core -->|"appoint/remove"| Maint
        Lead -->|"veto power"| Core
        Core -->|"veto by majority"| Maint
    end
    
    subgraph "Maintained Domains"
        SDK["SDK Maintainers<br/>Language-specific SDKs"]
        Proj["Project Maintainers<br/>Inspector, Registry, etc."]
        Groups["WG/IG Maintainers<br/>Security, Auth, Agents, etc."]
        CommunityMod["Community Moderators<br/>Discord Management"]
    end
    
    Maint -->|"steward"| SDK
    Maint -->|"steward"| Proj
    Maint -->|"steward"| Groups
    Maint -->|"some overlap"| CommunityMod
    
    subgraph "Decision Authority"
        Steering["MCP Steering Group<br/>Lead + Core + Maintainers"]
    end
    
    Lead -.member of.-> Steering
    Core -.member of.-> Steering
    Maint -.member of.-> Steering
```

**Sources:** [docs/community/governance.mdx:20-38](), [MAINTAINERS.md:7-155]()

The governance hierarchy implements a clear chain of authority with explicit veto powers. Lead Maintainers can veto any decision by Core Maintainers or Maintainers [docs/community/governance.mdx:52-53](). Core Maintainers can veto decisions by Maintainers through majority vote [docs/community/governance.mdx:50-51](). This structure is often referred to as "Benevolent Dictator for Life" (BDFL) in open source governance [docs/community/governance.mdx:34-34]().

## Governance Roles and Responsibilities

### Lead Maintainers (BDFL)

The Lead Maintainers serve as the ultimate decision-makers for the MCP project.

| Current Lead Maintainers | Status | GitHub |
|-------------------------|--------|--------|
| David Soria Parra | Active | [dsp-ant](https://github.com/dsp-ant) |
| Den Delimarsky | Active | [localden](https://github.com/localden) |
| Justin Spahr-Summers | Emeritus | [jspahrsummers](https://github.com/jspahrsummers) |

**Authority:**
- Final decision authority and veto power over any decision by Core Maintainers or Maintainers [docs/community/governance.mdx:52-53]().
- Appointment and removal of Core Maintainers [docs/community/governance.mdx:52-53]().
- Administrator access to all project infrastructure [docs/community/governance.mdx:52-53]().

**Sources:** [MAINTAINERS.md:7-11](), [MAINTAINERS.md:24-24](), [docs/community/governance.mdx:52-53](), [blog/content/posts/2026-04-08-maintainer-update.md:35-35]()

### Core Maintainers

Core Maintainers steer the MCP specification and overall project direction.

**Key Responsibilities:**
- Drive overall project direction and oversee contributors and maintainers [docs/community/governance.mdx:33-33]().
- Veto Maintainer decisions by majority vote and resolve disputes [docs/community/governance.mdx:50-51]().
- Appoint or remove Maintainers [docs/community/governance.mdx:50-51]().
- Admin access to all MCP repositories while using the standard PR workflow [docs/community/governance.mdx:50-51]().

**Current Core Maintainers (Partial List):**
- Caitie McCaffrey [MAINTAINERS.md:14-14]()
- Clare Liguori [MAINTAINERS.md:15-15]()
- Kurtis Van Gent [MAINTAINERS.md:16-16]()
- Nick Aldridge [MAINTAINERS.md:17-17]()
- Nick Cooper [MAINTAINERS.md:18-18]()
- Paul Carleton [MAINTAINERS.md:19-19]()
- Peter Alexander [MAINTAINERS.md:20-20]()

**Sources:** [MAINTAINERS.md:12-21](), [docs/community/governance.mdx:50-51](), [blog/content/posts/2026-04-08-maintainer-update.md:15-15]()

### Maintainers

Maintainers steward specific areas such as SDKs, documentation, or Working Groups. They make decisions for their area independently and escalate to Core Maintainers when needed [docs/community/governance.mdx:48-49]().

**Maintainer Categories:**
- **SDK Maintainers**: Responsible for specific language implementations (e.g., Python, TypeScript, Java, Go) [MAINTAINERS.md:28-108]().
- **Project Maintainers**: Oversee specific tools like the MCP Inspector, Registry, and Reference Servers [MAINTAINERS.md:109-146]().
- **WG/IG Maintainers**: Facilitate specific interest and working groups [MAINTAINERS.md:156-211]().

**Sources:** [MAINTAINERS.md:28-211](), [docs/community/governance.mdx:48-49]()

## Governance Succession and Amendment (SEP-2085)

Formal procedures exist for leadership transitions and governance changes to ensure project continuity, as established in SEP-2085.

### Succession Process
- **Lead Maintainer Departure**: Triggered by written notice or determination of inability to serve [seps/2085-governance-succession-and-amendment.md:30-31]().
- **Successor Appointment**: If one Lead Maintainer remains, they appoint a successor. If no Lead Maintainers remain, Core Maintainers appoint a successor by majority vote within 30 days [seps/2085-governance-succession-and-amendment.md:32-34]().
- **Interim Governance**: During a complete Lead Maintainer vacancy, the project operates by a two-thirds (2/3) vote of Core Maintainers [seps/2085-governance-succession-and-amendment.md:34-35]().

### Amendment Process
- **Proposal Authority**: Amendments to the governance structure may only be proposed by Lead Maintainers [seps/2085-governance-succession-and-amendment.md:38-38]().
- **Approval Requirement**: Amendments must be approved by a two-thirds (2/3) majority of all Core Maintainers [seps/2085-governance-succession-and-amendment.md:38-38]().
- **Procedure**: Proposals must be in writing, include specific rationale and language, and allow for a minimum 5-day comment period before a recorded vote [seps/2085-governance-succession-and-amendment.md:40-46]().

**Sources:** [seps/2085-governance-succession-and-amendment.md:28-46]()

## Decision-Making Process

### Decision Venues
| Venue | Purpose | Frequency |
|-------|---------|-----------|
| **Core Maintainer Meetings** | Discuss and vote on proposals | Bi-weekly [docs/community/governance.mdx:58-58]() |
| **Maintainer Discord** | Small proposals and technical coordination | Ongoing [docs/community/governance.mdx:58-58]() |
| **Steering Group Meetings** | High-level alignment and in-person sync | Every 3-6 months [docs/community/governance.mdx:60-60]() |

### Decision Recording
To ensure transparency, all significant decisions are documented in public channels:
- **Technical/Governance Decisions**: Recorded in GitHub Issues and SEPs [docs/community/communication.mdx:99-102]().
- **Specification Changes**: Tracked in the Protocol Changelog [docs/community/communication.mdx:100-100]().
- **Transparency Rule**: All technical decisions affecting the community discussed in private channels must be moved to GitHub and labeled with `notes` [docs/community/communication.mdx:52-54]().

**Sources:** [docs/community/governance.mdx:58-60](), [docs/community/communication.mdx:93-102]()

## Communication and Data Flow

The following diagram illustrates how governance discussions translate from informal spaces into formal protocol artifacts.

```mermaid
graph LR
    subgraph "Natural Language Space (Communication)"
        Discord["Discord Channels<br/>#general, #auth-wg<br/>Private Maintainer Space"]
        Meetings["Core Maintainer Meetings<br/>Bi-weekly Syncs"]
        Discussions["GitHub Discussions<br/>Consensus Building"]
    end
    
    subgraph "Code & Specification Space (Entity)"
        SEP["seps/ Directory<br/>Markdown Design Documents"]
        Governance["docs/community/governance.mdx<br/>Rules of the Road"]
        Changelog["docs/specification/changelog.md<br/>Protocol History"]
    end
    
    Discord -->|"Informal Idea"| Discussions
    Discussions -->|"Formal Proposal"| SEP
    Meetings -->|"Vote/Decision"| SEP
    SEP -->|"Approved Change"| Governance
    SEP -->|"Protocol Update"| Changelog
```

**Sources:** [docs/community/communication.mdx:8-58](), [docs/community/governance.mdx:42-43](), [docs/community/sep-guidelines.mdx:47-69]()

## Legal and Policy Framework

The Model Context Protocol is established as **Model Context Protocol a Series of LF Projects, LLC** [docs/community/governance.mdx:10-10]().

| Aspect | Policy |
|--------|--------|
| **Entity** | LF Projects, LLC [docs/community/governance.mdx:10-10]() |
| **Code License** | Apache License, Version 2.0 [docs/community/governance.mdx:14-14]() |
| **Docs License** | Creative Commons Attribution 4.0 [docs/community/governance.mdx:18-18]() |
| **Copyright** | Retained by contributors as independent works [docs/community/governance.mdx:12-12]() |

**Sources:** [docs/community/governance.mdx:8-18]()

---

# Page: Maintainers and Roles

# Maintainers and Roles

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [MAINTAINERS.md](MAINTAINERS.md)
- [blog/content/posts/2026-01-22-core-maintainer-update.md](blog/content/posts/2026-01-22-core-maintainer-update.md)
- [blog/content/posts/2026-04-08-maintainer-update.md](blog/content/posts/2026-04-08-maintainer-update.md)
- [blog/static/posts/images/maintainer-update-2026-04/clare.webp](blog/static/posts/images/maintainer-update-2026-04/clare.webp)
- [blog/static/posts/images/maintainer-update-2026-04/den.jpeg](blog/static/posts/images/maintainer-update-2026-04/den.jpeg)
- [docs/community/communication.mdx](docs/community/communication.mdx)
- [docs/community/governance.mdx](docs/community/governance.mdx)
- [docs/community/sep-guidelines.mdx](docs/community/sep-guidelines.mdx)
- [docs/docs/tutorials/security/authorization.mdx](docs/docs/tutorials/security/authorization.mdx)

</details>



This page catalogs the current maintainers of the Model Context Protocol (MCP) project, their specific responsibilities, SDK ownership, and working group facilitation. The MCP project operates under a formal governance model with a hierarchical structure designed to ensure protocol stability and community growth.

**Note:** This roster is maintained in [MAINTAINERS.md:1-211]() and was last updated May 1, 2026.

## Governance Roles and Hierarchy

The MCP project adopts a hierarchical structure similar to major open-source projects like Python and PyTorch [docs/community/governance.mdx:22-23](). The **MCP Steering Group** is composed of Lead, Core, and specialized Maintainers [docs/community/governance.mdx:36-36]().

### Technical Governance Hierarchy

```mermaid
graph TB
    subgraph "Lead Maintainers (BDFL)"
        LEAD1["David Soria Parra<br/>@dsp-ant"]
        LEAD2["Den Delimarsky<br/>@localden"]
    end
    
    subgraph "Core Maintainers"
        CORE1["Caitie McCaffrey<br/>@CaitieM20"]
        CORE2["Clare Liguori<br/>@clareliguori"]
        CORE3["Kurtis Van Gent<br/>@kurtisvg"]
        CORE4["Nick Aldridge<br/>@000-000-000-000-000"]
        CORE5["Nick Cooper<br/>@nickcoai"]
        CORE6["Paul Carleton<br/>@pcarleton"]
        CORE7["Peter Alexander<br/>@pja-ant"]
    end
    
    subgraph "Maintainers"
        SDK["SDK Maintainers<br/>(Language Specific)"]
        PROJ["Project Maintainers<br/>(Tools/Infrastructure)"]
        WGIG["WG/IG Maintainers<br/>(Facilitators)"]
    end
    
    LEAD1 & LEAD2 -->|"Final decision authority"| CORE1 & CORE2 & CORE3 & CORE4 & CORE5 & CORE6 & CORE7
    CORE1 & CORE2 & CORE3 & CORE4 & CORE5 & CORE6 & CORE7 -->|"Drive project direction"| SDK & PROJ & WGIG
    
    subgraph "Contributors"
        CONTRIB["Issues, PRs, Discussions"]
    end
    
    SDK & PROJ & WGIG -->|"Steward specific areas"| CONTRIB
```

**Sources:** [MAINTAINERS.md:7-21](), [docs/community/governance.mdx:22-54](), [blog/content/posts/2026-04-08-maintainer-update.md:14-41]()

### Role Definitions

| Role | Scope | Authority |
| :--- | :--- | :--- |
| **Lead Maintainers** | Entire MCP Ecosystem | Final decision authority (BDFL); appoint and remove Core Maintainers [docs/community/governance.mdx:52-53](). |
| **Core Maintainers** | Spec & Project Direction | Steer the MCP specification; veto Maintainer decisions by majority vote; appoint/remove Maintainers [docs/community/governance.mdx:50-51](). |
| **Maintainers** | Specific Components | Steward SDKs, documentation, or Working Groups; make decisions for their area independently [docs/community/governance.mdx:48-49](). |
| **Contributors** | Code & Feedback | File issues and submit pull requests using the standard contribution process [docs/community/governance.mdx:31-31](). |

**Sources:** [docs/community/governance.mdx:24-54]()

## SDK Maintainers

SDK maintainers are responsible for language-specific implementations of the MCP protocol. They ensure conformance with the specification and manage release cycles for their respective libraries [docs/community/governance.mdx:48-49]().

### SDK Ownership Matrix

| SDK | Maintainers |
| :--- | :--- |
| **TypeScript** | Inna Harper, Felix Weinberger, Olivier Chafik, Konstantin Konstantinov, Matt Carey [MAINTAINERS.md:84-91]() |
| **Python** | Inna Harper, Jerome Swannack, Marcelo Trylesinski, Max Isbey, Felix Weinberger [MAINTAINERS.md:76-83]() |
| **Java** | Christian Tzolov, Dariusz Jędrzejczyk, Daniel Garnier-Moiroux, Mark Pollack [MAINTAINERS.md:30-36]() |
| **Go** | Maciej Kisiel, Yaroslav Shevchuk, Guglielmo Colombo, Jonathan Amsterdam [MAINTAINERS.md:51-57]() |
| **C#** | Stephan Halter, Mike Kistler, Den Delimarsky, Eirik Tsarpalis, Stephen Toub [MAINTAINERS.md:59-65]() |
| **Rust** | Alex Hancock, Michael Bolin, Bradley Axen, Jack Amadeo, Michael Neale [MAINTAINERS.md:92-99]() |
| **Swift** | Matt Zmuda, Carl Peaslee, Maksym Mova, Stephen Tallent [MAINTAINERS.md:44-50]() |
| **Kotlin** | Leonid Stashevsky, Sergey Ignatov, Konstantin Pavlov, Pavel Gorgulov, Briliantov Vadim, Sergei Dubov, Maria Tigina [MAINTAINERS.md:66-75]() |
| **Ruby** | Topher Bullock, Koichi Ito, Ateş Göral, Jonathan Hefner [MAINTAINERS.md:37-43]() |
| **PHP** | Kyrian Obikwelu, Christopher Hertel, Fabien Potencier, Nicolas Grekas, Tobias Nyholm, Roman Pronskiy [MAINTAINERS.md:100-108]() |

**Sources:** [MAINTAINERS.md:30-108]()

## Project Maintainers

These maintainers oversee core tools, infrastructure, and reference implementations that support the MCP ecosystem [MAINTAINERS.md:109-146]().

| Project | Maintainers |
| :--- | :--- |
| **Inspector** | Cliff Hall, Konstantin Konstantinov, Ola Hungerford, Bob Dickinson [MAINTAINERS.md:115-121]() |
| **Registry** | Tadas Antanavicius, Radoslav (Rado) Dimitrov, Bob Dickinson [MAINTAINERS.md:122-127]() |
| **Reference Servers** | Ola Hungerford, Cliff Hall, Tadas Antanavicius, Shaun Smith, Jonathan Hefner [MAINTAINERS.md:139-146]() |
| **use-mcp** | Glen Maddern [MAINTAINERS.md:111-114]() |
| **MCPB (Bundle)** | Alexander Sklar, Adam Jones, Joan Xie [MAINTAINERS.md:133-138]() |

**Sources:** [MAINTAINERS.md:111-146]()

## Working Group (WG) & Interest Group (IG) Facilitation

Collaboration is organized around Interest Groups (problem identification) and Working Groups (solution delivery) [docs/community/governance.mdx:70-75]().

### Group Organization

```mermaid
graph LR
    subgraph "Interest Groups (Problem Identification)"
        SEC_IG["Security IG<br/>Den Delimarsky, Paul Carleton"]
        AUTH_IG["Authorization IG<br/>Aaron Parecki, Paul Carleton"]
        TRANS_IG["Transports IG<br/>Kurtis Van Gent, Jonathan Hefner"]
        FIN_IG["Financial Services IG<br/>Sambhav Kothari, Peder HP"]
    end
    
    subgraph "Working Groups (Solution Delivery)"
        AGENTS_WG["Agents WG<br/>Peter Alexander, Inna Harper"]
        APPS_WG["MCP Apps WG<br/>Liad Yosef, Ido Salomon"]
        CARD_WG["Server Card WG<br/>Tadas Antanavicius, David Soria Parra"]
    end
    
    subgraph "Client Implementation"
        CLIENT_IG["Client Implementor IG<br/>Goose, Zed, VS Code, Cursor,<br/>Codex, GitHub Copilot"]
    end
```

**Sources:** [MAINTAINERS.md:156-211](), [docs/community/governance.mdx:68-75]()

### Group Maintainer Details

*   **Security IG:** Den Delimarsky, Paul Carleton, Jenn Newton [MAINTAINERS.md:160-165](). Focuses on protocol security and vulnerability management.
*   **Authorization IG:** Aaron Parecki, Darin McAdams, Paul Carleton [MAINTAINERS.md:166-171](). Stewards the OAuth 2.1-based authorization specification [docs/docs/tutorials/security/authorization.mdx:8-9]().
*   **Transports IG:** Kurtis Van Gent, Jonathan Hefner, Shaun Smith, Harvey Tuch [MAINTAINERS.md:189-195](). Oversees evolution of stdio and HTTP transports.
*   **Agents WG:** Peter Alexander, Luca Chang, Inna Harper [MAINTAINERS.md:202-207](). Focuses on agentic execution models and unsolicited tasks.
*   **Server Card WG:** Tadas Antanavicius, David Soria Parra, Sam Morrow [MAINTAINERS.md:196-201](). Develops standards for server discovery and metadata.
*   **Client Implementor IG:** Representatives from Goose (Alex Hancock), Zed (Ben Brandt), VS Code (Connor Peet, Tyler Leonhardt), Codex (Gabriel Peal), GitHub Copilot (Jun Han), and Cursor (Michael Feldstein) [MAINTAINERS.md:172-183]().

**Sources:** [MAINTAINERS.md:156-211]()

## Contact and Communication

Technical governance and coordination are primarily facilitated through the shared Discord server and GitHub [docs/community/communication.mdx:8-17]().

*   **Discord:** [MCP Contributor Discord](https://discord.gg/6CSzBmMkjX). Used for real-time discussion, WG/IG coordination, and maintainer availability [docs/community/communication.mdx:12-22]().
*   **GitHub Discussions:** Used for structured, long-form debate on project direction and roadmap planning [docs/community/communication.mdx:60-71]().
*   **Security Reporting:** Security issues should **never** be posted publicly. Use the private reporting process in `SECURITY.md` or contact Lead/Core Maintainers directly [docs/community/communication.mdx:85-92]().

**Sources:** [docs/community/communication.mdx:8-92](), [docs/community/governance.mdx:40-43]()

---

# Page: Working Groups and Interest Groups

# Working Groups and Interest Groups

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/CODEOWNERS](.github/CODEOWNERS)
- [docs/community/charter-template.mdx](docs/community/charter-template.mdx)
- [docs/community/contributor-ladder.mdx](docs/community/contributor-ladder.mdx)
- [docs/community/interest-groups/auth.mdx](docs/community/interest-groups/auth.mdx)
- [docs/community/interest-groups/enterprise-managed-authorization.mdx](docs/community/interest-groups/enterprise-managed-authorization.mdx)
- [docs/community/interest-groups/financial-services.mdx](docs/community/interest-groups/financial-services.mdx)
- [docs/community/interest-groups/primitive-grouping.mdx](docs/community/interest-groups/primitive-grouping.mdx)
- [docs/community/interest-groups/security.mdx](docs/community/interest-groups/security.mdx)
- [docs/community/interest-groups/tool-annotations.mdx](docs/community/interest-groups/tool-annotations.mdx)
- [docs/community/working-groups/file-uploads.mdx](docs/community/working-groups/file-uploads.mdx)
- [docs/community/working-groups/inspector-v2.mdx](docs/community/working-groups/inspector-v2.mdx)
- [docs/community/working-groups/interceptors.mdx](docs/community/working-groups/interceptors.mdx)
- [docs/community/working-groups/registry.mdx](docs/community/working-groups/registry.mdx)
- [docs/community/working-groups/sdk.mdx](docs/community/working-groups/sdk.mdx)
- [docs/community/working-groups/server-card.mdx](docs/community/working-groups/server-card.mdx)
- [docs/community/working-interest-groups.mdx](docs/community/working-interest-groups.mdx)
- [docs/seps/2149-working-group-charter-template.mdx](docs/seps/2149-working-group-charter-template.mdx)
- [seps/2149-working-group-charter-template.md](seps/2149-working-group-charter-template.md)

</details>



This document describes the collaborative group structures within the Model Context Protocol's governance: **Working Groups** (WGs) and **Interest Groups** (IGs). These groups facilitate focused discussions, problem identification, and deliverable production within specific areas of the MCP ecosystem.

For information about the overall governance structure and maintainer hierarchy, see [Governance Structure](#8.1). For the process of proposing specification changes, see [Specification Enhancement Process (SEP)](#7.2).

## Purpose and Scope

Working Groups and Interest Groups are established to address community feedback regarding unclear authority delegation and inconsistent processes. They provide:
- Standardized governance rules defined in **SEP-2149** [seps/2149-working-group-charter-template.md:12-15]().
- Clear expectations for leadership and participation levels [docs/community/working-interest-groups.mdx:113-123]().
- Explicitly defined boundaries through mandatory charters [docs/community/charter-template.mdx:6-8]().

Sources: [docs/community/working-interest-groups.mdx:1-19](), [seps/2149-working-group-charter-template.md:10-32]()

## Interest Groups vs Working Groups

| Feature | Interest Group (IG) | Working Group (WG) |
| :--- | :--- | :--- |
| **Purpose** | Identify and discuss problems | Build concrete solutions |
| **Output** | Problem statements, use cases, recommendations | SEPs, implementations, code |
| **Commitment** | Active contribution expected | Active contribution expected |
| **Leadership** | Facilitator(s) | Lead(s) |
| **Decisions** | Rough consensus, non-binding | Binding (Lazy consensus → Vote → Escalation) |
| **Duration** | Ongoing as long as topic is relevant | Until deliverables complete |

Sources: [docs/community/working-interest-groups.mdx:8-19](), [seps/2149-working-group-charter-template.md:36-40]()

### Typical Flow
Contributors typically discuss a problem in an IG to validate community support, then form or join a WG to build the solution, eventually submitting a SEP for implementation [docs/community/working-interest-groups.mdx:36]().

## Group Governance and Leadership

### Leadership Requirements
Each group is led by **Leads** (WGs) or **Facilitators** (IGs). They must:
- Hold at least **Member** status on the [Contributor Ladder](./contributor-ladder) [docs/community/working-interest-groups.mdx:85]().
- Be sponsored by at least two Core Maintainers or one Lead Maintainer [docs/community/working-interest-groups.mdx:89]().
- WG Leads additionally commit to 2-3 hours/week for group activities [docs/community/working-interest-groups.mdx:91-94]().

### Participation Tiers
Participation is organized into four levels to ensure clear pathways for involvement:

| Level | Description | Privileges |
| :--- | :--- | :--- |
| **Observer** | Anyone following the work | Read access, attend meetings |
| **Participant** | Active contributor | Propose agenda items, async votes |
| **WG Member** | Sustained contributor (3+ months) | Counted for quorum (WGs only) |
| **Lead/Facilitator** | Operational leadership | Sets agenda, facilitates, escalates |

Sources: [docs/community/working-interest-groups.mdx:113-132](), [seps/2149-working-group-charter-template.md:92-98]()

### Group Decision-Making (WG Only)
Working Groups follow a formal decision-making hierarchy to prevent bottlenecks:
1. **Lazy Consensus**: Proposals are assumed accepted if no objections are raised within 72 hours [docs/community/working-interest-groups.mdx:143-152]().
2. **Formal Vote**: If consensus fails, WG Members vote (simple majority) [docs/community/working-interest-groups.mdx:154-162]().
3. **Escalation**: Blocked decisions are escalated to Core Maintainers [docs/community/working-interest-groups.mdx:164-168]().

## Group Chartering (SEP-2149)

Every group must maintain a charter at `docs/community/working-groups/<name>.mdx` or `docs/community/interest-groups/<name>.mdx` [docs/community/charter-template.mdx:6-7]().

### Charter Template Structure
Charters follow a standardized format to ensure consistency across the ecosystem:
- **Mission Statement**: 2-3 sentence summary of purpose [docs/community/charter-template.mdx:30-38]().
- **Scope**: Explicit "In Scope" and "Out of Scope" sections to prevent mission creep [docs/community/charter-template.mdx:40-59]().
- **Authority & Decision Rights (WG only)**: Matrix defining what the WG can decide autonomously vs. what requires Core Maintainer approval [docs/community/charter-template.mdx:75-94]().
- **Deliverables & Success Metrics (WG only)**: Tracking active work items and target dates [docs/community/charter-template.mdx:121-137]().

Sources: [docs/community/charter-template.mdx:18-143](), [seps/2149-working-group-charter-template.md:205-274]()

## Active Groups

### Interest Groups (IGs)

| Group | Facilitators | Focus |
| :--- | :--- | :--- |
| **Auth IG** | Aaron Parecki, Darin McAdams, Paul Carleton | OAuth 2.1 gaps, enterprise identity, agentic access [docs/community/interest-groups/auth.mdx:46-51](). |
| **Security IG** | TBD | Threat modeling, best practices, and protocol security [docs/community/interest-groups/security.mdx:1-5](). |
| **Enterprise-Managed Auth IG** | Paul Carleton, Aaron Parecki | Interop for the ID-JAG flow and enterprise IdP integration [docs/community/interest-groups/enterprise-managed-authorization.mdx:39-44](). |
| **Financial Services IG** | Sambhav Kothari, Peder H. Pedersen | Compliance, auditability, and risk-controlled deployment [docs/community/interest-groups/financial-services.mdx:75-79](). |
| **Tool Annotations IG** | Sam Morrow, Robert Reichel | Metadata for tool discovery and selection [docs/community/interest-groups/tool-annotations.mdx:38-42](). |
| **Primitive Grouping IG** | Tapan Chugh, Sam Morrow | Organizing Tools/Resources beyond flat lists [docs/community/interest-groups/primitive-grouping.mdx:67-71](). |

### Working Groups (WGs)

| Group | Leads | Deliverables |
| :--- | :--- | :--- |
| **Transports WG** | TBD | Evolution of stdio and HTTP transports [docs/community/charter-template.mdx:151-153](). |
| **Registry WG** | Tadas Antanavicius, Radoslav Dimitrov | `registry.modelcontextprotocol.io`, `server.json` schema [docs/community/working-groups/registry.mdx:38-44](). |
| **Inspector v2 WG** | TBD | Next generation of the MCP Inspector tool [docs/community/working-groups/inspector-v2.mdx:1-5](). |
| **File Uploads WG** | TBD | Standardizing binary and file transfers [docs/community/working-groups/file-uploads.mdx:1-5](). |
| **SDK WG** | TBD | Multi-language SDK tiering and conformance [docs/community/working-groups/sdk.mdx:1-5](). |
| **Server Card WG** | TBD | Standardized metadata for server discovery [docs/community/working-groups/server-card.mdx:1-5](). |
| **Interceptors WG** | Sambhav Kothari, Peder H. Pedersen, et al. | SEP-1763, context validation/mutation primitives [docs/community/working-groups/interceptors.mdx:34-42](). |

## Lifecycle Management

### Creation Workflow
Groups are proposed via the `#wg-ig-group-creation` channel on Discord. Proposals are reviewed by Community Moderators and require sponsorship from Core Maintainers [docs/community/interest-groups/auth.mdx:68-69]().

### Group Entity Relationship
The following diagram illustrates how Group Charters (Natural Language Space) map to Governance and Code Entities (Code Space).

**Title: Group Governance and Code Mapping**
```mermaid
graph TD
    subgraph "Natural Language (Charters)"
        CHARTER["Group Charter<br/>(docs/community/working-groups/*.mdx)"]
        MISSION["Mission Statement"]
        SCOPE["Scope Boundaries"]
    end

    subgraph "Governance Entities"
        LEAD["Group Lead / Facilitator<br/>(Must be Member status)"]
        CORE_M["Core Maintainer<br/>(Sponsor/Approver)"]
        SEP_PROC["SEP Process<br/>(docs/seps/1850-sep-process.md)"]
    end

    subgraph "Code & Automation"
        ACCESS_REPO["access repo<br/>(github.com/modelcontextprotocol/access)"]
        CODEOWNERS[".github/CODEOWNERS"]
        DOCS_JSON["docs/docs.json"]
    end

    CHARTER --> MISSION
    CHARTER --> SCOPE
    LEAD -->|Maintains| ACCESS_REPO
    CORE_M -->|Approves Charter| CODEOWNERS
    CHARTER -->|Registered in| DOCS_JSON
    LEAD -->|Drives| SEP_PROC
```

Sources: [docs/community/charter-template.mdx:6-10](), [.github/CODEOWNERS:13-20](), [docs/community/working-interest-groups.mdx:101](), [seps/2149-working-group-charter-template.md:14-15]()

### Operations and Communication
- **Meetings**: Agendas must be published in advance, and notes posted within 48 hours [docs/community/working-interest-groups.mdx:98-99]().
- **Discord**: Primary communication happens in dedicated `#<group-name>` channels on the MCP Contributors Discord [docs/community/interest-groups/auth.mdx:56-64]().
- **Membership**: Managed via the [access repository](https://github.com/modelcontextprotocol/access) [docs/community/working-interest-groups.mdx:101]().

**Title: Communication and Deliverable Flow**
```mermaid
graph LR
    subgraph "Communication"
        DISCORD["Discord Channels<br/>(#auth-ig, #interceptors)"]
        MEETINGS["Biweekly Calls<br/>(Group Sessions)"]
    end

    subgraph "Deliverables"
        GH_DISC["GitHub Discussions<br/>(Meeting Notes)"]
        SEPS["seps/ Directory<br/>(Spec Enhancements)"]
        REPOS["Project Repos<br/>(e.g., ext-auth, experimental-ext-interceptors)"]
    end

    DISCORD -->|Sync| MEETINGS
    MEETINGS -->|Notes| GH_DISC
    DISCORD -->|Async Discussion| GH_DISC
    GH_DISC -->|Problem Validation| SEPS
    SEPS -->|Implementation| REPOS
```

Sources: [docs/community/working-interest-groups.mdx:95-112](), [docs/community/interest-groups/auth.mdx:56-64](), [docs/community/working-groups/interceptors.mdx:57-65]()

---

# Page: Communication Channels

# Communication Channels

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [MAINTAINERS.md](MAINTAINERS.md)
- [blog/content/posts/2026-04-08-maintainer-update.md](blog/content/posts/2026-04-08-maintainer-update.md)
- [blog/static/posts/images/maintainer-update-2026-04/clare.webp](blog/static/posts/images/maintainer-update-2026-04/clare.webp)
- [blog/static/posts/images/maintainer-update-2026-04/den.jpeg](blog/static/posts/images/maintainer-update-2026-04/den.jpeg)
- [docs/community/communication.mdx](docs/community/communication.mdx)
- [docs/community/governance.mdx](docs/community/governance.mdx)
- [docs/community/sep-guidelines.mdx](docs/community/sep-guidelines.mdx)
- [docs/docs/tutorials/security/authorization.mdx](docs/docs/tutorials/security/authorization.mdx)

</details>



This document describes the communication infrastructure for the Model Context Protocol (MCP) project, including where community discussions happen, how decisions are documented, and the policies governing transparency. For governance structure and decision-making processes, see [Governance Structure](#8.1). For the SEP proposal process, see [Specification Enhancement Process (SEP)](#7.2).

## Overview

The MCP project maintains several primary communication channels, each serving distinct purposes in the project lifecycle. These channels are designed to support a distributed, multi-language ecosystem of SDKs and server implementations.

| Channel | Purpose | Formality | Persistence |
| :--- | :--- | :--- | :--- |
| **Discord** | Real-time contributor discussions, coordination | Informal | Transient |
| **Live Calls** | Synchronous WG/IG presentations, reports | Semi-formal | Recorded/Notes |
| **GitHub Discussions** | Long-form proposals, roadmap planning | Semi-formal | Permanent |
| **GitHub Issues** | Actionable tasks, bug reports, tracking | Formal | Permanent |
| **Security Reporting** | Private vulnerability disclosure | Formal | Private |

**Sources:** [docs/community/communication.mdx:8-17]()

## Communication to Code Entity Mapping

The following diagram bridges the natural language space of community interaction with the code and documentation entities that persist those interactions.

**Interaction Flow and Data Persistence**
```mermaid
graph TB
    subgraph "Natural Language Space (Communication)"
        Discord["Discord Server<br/>discord.gg/6CSzBmMkjX"]
        Meetings["Live Calls<br/>meet.modelcontextprotocol.io"]
        
        subgraph "Public Discord Channels"
            PublicSDK["#typescript-sdk-dev<br/>#python-sdk-dev"]
            PublicWG["WG/IG Channels<br/>e.g., #auth-wg, #security-ig"]
        end
        
        subgraph "Private Discord Channels"
            PrivateSec["Security Incident Rooms"]
            PrivatePeople["Maintainer Discussions"]
        end
    end
    
    subgraph "Code & Documentation Space (Entities)"
        GHIssues["GitHub Issues<br/>(Actionable Tasks)"]
        GHDiscussions["GitHub Discussions<br/>(Structured Debate)"]
        SEPs["seps/ directory<br/>(Spec Proposals)"]
        SecurityMD["SECURITY.md<br/>(Private Reporting)"]
        Changelog["specification/draft/changelog<br/>(Protocol History)"]
    end
    
    Discord --> PublicSDK
    Discord --> PublicWG
    Discord --> PrivateSec
    
    PublicWG -. "notes" .-> GHIssues
    PublicSDK -. "proposals" .-> GHDiscussions
    GHDiscussions --> SEPs
    SEPs --> Changelog
    PrivateSec -. "formal report" .-> SecurityMD
    
    style Discord stroke-dasharray: 5 5
    style Meetings stroke-dasharray: 5 5
```

**Sources:** [docs/community/communication.mdx:8-107](), [docs/community/governance.mdx:40-43](), [docs/community/sep-guidelines.mdx:14-15]()

## Discord Server Structure

### Access and Membership
The [MCP Contributor Discord](https://discord.gg/6CSzBmMkjX) is specifically designed for **MCP contributors** and is not intended for general user support [docs/community/communication.mdx:20-22]().

### Public Channel Categories
Public channels follow a default-open policy for transparency:
*   **SDK and Tooling Development:** Channels like `#typescript-sdk-dev`, `#python-sdk-dev`, and `#inspector-dev` host real-time coordination for core components [docs/community/communication.mdx:30-34]().
*   **WG and IG Discussions:** Channels such as `#auth-wg` and `#security-ig` support the collaborative groups [docs/community/communication.mdx:31-31]().
*   **Public Office Hours:** Maintainers use Discord to coordinate availability and community onboarding [docs/community/communication.mdx:34-35]().

### Private Channel Policies
Private channels are exceptions used for confidential coordination [docs/community/communication.mdx:41-43]().
*   **Criteria:** Security incidents (CVEs), people matters (maintainer discussions, CoC issues), or immediate coordination requiring a limited audience [docs/community/communication.mdx:45-51]().
*   **Transparency Requirements:** Any significant technical or governance discussion on Discord that leads to a potential decision must be moved to GitHub Discussions or Issues for a persistent record [docs/community/communication.mdx:58-59](). Decisions must be documented and labeled with `notes` [docs/community/communication.mdx:52-54]().

**Sources:** [docs/community/communication.mdx:19-59](), [docs/community/governance.mdx:40-43]()

## GitHub Discussions and Issues

### Structured Discussion
GitHub Discussions are the primary tool for structured, long-form debate on project direction [docs/community/communication.mdx:60-62]().
*   **Use cases:** Roadmap planning, announcements, community polls, and feature requests with rationale [docs/community/communication.mdx:64-70]().
*   **Fallback:** If a repository doesn't have Discussions enabled, GitHub Issues are used instead [docs/community/communication.mdx:70-71]().

### Actionable Tasks
GitHub Issues are reserved for actionable development tasks [docs/community/communication.mdx:72-74]().
*   **Use cases:** Bug reports with reproducible steps, documentation improvements, and CI/CD or infrastructure problems [docs/community/communication.mdx:76-81]().

### SEP Relationship
Proposed changes to the specification are submitted as pull requests to the `seps/` directory, not as GitHub Issues [docs/community/communication.mdx:83-84](). The PR-based workflow (e.g., SEP-1850) serves as the historical record of feature proposals [docs/community/sep-guidelines.mdx:14-15]().

**Sources:** [docs/community/communication.mdx:60-84](), [docs/community/sep-guidelines.mdx:14-15]()

## Security and Decision Records

### Security Reporting
Vulnerabilities must **never** be posted publicly [docs/community/communication.mdx:87-88]().
1.  Follow the private security reporting process in `SECURITY.md` [docs/community/communication.mdx:89-89]().
2.  Contact Lead or Core Maintainers directly [docs/community/communication.mdx:90-90]().

### Decision Record System
All MCP decisions follow a documentation hierarchy to ensure context is retained for onboarding engineers.

| Type | Location |
| :--- | :--- |
| **Technical Decisions** | [GitHub Issues](https://github.com/modelcontextprotocol/modelcontextprotocol/issues) and SEPs |
| **Specification Changes** | [Changelog](https://modelcontextprotocol.io/specification/draft/changelog) |
| **Process Changes** | [Community Governance Docs](https://modelcontextprotocol.io/community/governance) |
| **Governance Decisions** | [GitHub Issues](https://github.com/modelcontextprotocol/modelcontextprotocol/issues) and SEPs |

**Sources:** [docs/community/communication.mdx:85-103]()

## Community Events and Meetings

### Working and Interest Groups
Collaboration is organized around Interest Groups (IGs) and Working Groups (WGs) [docs/community/governance.mdx:68-70]().
*   **IGs:** Identify and articulate problems through open discussions [docs/community/governance.mdx:72-72]().
*   **WGs:** Develop concrete solutions and deliverables like SEPs [docs/community/governance.mdx:73-73]().
*   **Live Calls:** Synchronous presentations and progress reports are hosted at `meet.modelcontextprotocol.io` [docs/community/communication.mdx:13-13]().

### Core Maintainer Meetings
The Core Maintainer group meets bi-weekly to discuss and vote on proposals [docs/community/governance.mdx:56-58](). The Steering Group (Lead, Core, and Maintainers) attempts to meet in person every three to six months [docs/community/governance.mdx:60-61]().

**Sources:** [docs/community/governance.mdx:56-75](), [docs/community/communication.mdx:10-15]()

## Moderation and Code of Conduct

All communication is governed by the [Code of Conduct](https://github.com/modelcontextprotocol/modelcontextprotocol/blob/main/CODE_OF_CONDUCT.md) [docs/community/communication.mdx:17-18]().

### Community Moderators
The project designates Community Moderators to ensure respectful interactions [MAINTAINERS.md:147-148]().
*   **Moderator Team:** Includes Ola Hungerford, Cliff Hall, Shaun Smith, Jonathan Hefner, Tadas Antanavicius, and Peder Holdgaard Pedersen [MAINTAINERS.md:149-154]().

### Usage Guidelines
*   **Avoid Marketing:** Keep discussions vendor-neutral; mentions of brands are discouraged except as technical examples [docs/community/communication.mdx:39-40]().
*   **No General Support:** Discord is for contributors. Users should use official documentation or GitHub Discussions for support [docs/community/communication.mdx:38-38]().

**Sources:** [docs/community/communication.mdx:17-40](), [MAINTAINERS.md:147-154]()

---

# Page: Release History and Roadmap

# Release History and Roadmap

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [blog/archetypes/default.md](blog/archetypes/default.md)
- [blog/content/posts/2025-07-29-prompts-for-automation.md](blog/content/posts/2025-07-29-prompts-for-automation.md)
- [blog/content/posts/2025-07-31-governance-for-mcp.md](blog/content/posts/2025-07-31-governance-for-mcp.md)
- [blog/content/posts/2025-09-05-php-sdk.md](blog/content/posts/2025-09-05-php-sdk.md)
- [blog/content/posts/2025-09-08-mcp-registry-preview.md](blog/content/posts/2025-09-08-mcp-registry-preview.md)
- [blog/content/posts/2025-09-26-mcp-next-version-update.md](blog/content/posts/2025-09-26-mcp-next-version-update.md)
- [blog/content/posts/2025-11-03-using-server-instructions.md](blog/content/posts/2025-11-03-using-server-instructions.md)
- [blog/content/posts/2025-11-20-adopting-mcpb.md](blog/content/posts/2025-11-20-adopting-mcpb.md)
- [blog/content/posts/2025-11-21-mcp-apps.md](blog/content/posts/2025-11-21-mcp-apps.md)
- [blog/content/posts/2025-11-25-first-mcp-anniversary.md](blog/content/posts/2025-11-25-first-mcp-anniversary.md)
- [blog/content/posts/2025-11-28-sep-process-update.md](blog/content/posts/2025-11-28-sep-process-update.md)
- [blog/content/posts/2025-12-09-mcp-joins-agentic-ai-foundation.md](blog/content/posts/2025-12-09-mcp-joins-agentic-ai-foundation.md)
- [blog/content/posts/2026-05-21-mcp-2026-07-28-rc.md](blog/content/posts/2026-05-21-mcp-2026-07-28-rc.md)
- [blog/content/posts/welcome-to-mcp-blog.md](blog/content/posts/welcome-to-mcp-blog.md)
- [blog/static/posts/images/2026-07-28-rc/handle-pattern.svg](blog/static/posts/images/2026-07-28-rc/handle-pattern.svg)
- [blog/static/posts/images/2026-07-28-rc/stateless-topology.svg](blog/static/posts/images/2026-07-28-rc/stateless-topology.svg)
- [docs/development/roadmap.mdx](docs/development/roadmap.mdx)
- [docs/specification/2025-06-18/basic/lifecycle.mdx](docs/specification/2025-06-18/basic/lifecycle.mdx)
- [docs/specification/2025-06-18/changelog.mdx](docs/specification/2025-06-18/changelog.mdx)
- [docs/specification/2025-06-18/index.mdx](docs/specification/2025-06-18/index.mdx)
- [docs/specification/2025-06-18/server/index.mdx](docs/specification/2025-06-18/server/index.mdx)

</details>



This document chronicles the evolution of the Model Context Protocol through its major releases, documenting the key features and Specification Enhancement Proposals (SEPs) introduced in each version. It also outlines the protocol's versioning scheme, release cadence, and future roadmap based on active working group priorities.

## Versioning Scheme

MCP uses a **date-based versioning scheme** in YYYY-MM-DD format. Each version identifier represents the date of the last breaking change to the protocol.

- **Legacy versions** (2024-11-05 through 2025-06-18): Use JSON Schema draft-07.
- **Modern versions** (2025-11-25 onward): Use JSON Schema 2020-12 with updated terminology (e.g., `$defs` instead of `definitions`).
- **Draft Version**: The special identifier `draft` represents active development and may change without notice.

**Sources:** [blog/content/posts/2025-11-25-first-mcp-anniversary.md:1-20](), [blog/content/posts/2025-09-26-mcp-next-version-update.md:15-22]()

## Release Timeline and Milestones

MCP followed an accelerated early release cycle, maturing into a quarterly cadence overseen by the Linux Foundation.

Title: MCP Evolution and Roadmap
```mermaid
gantt
    title MCP Evolution and Roadmap
    dateFormat YYYY-MM-DD
    axisFormat %Y-%m
    section Protocol Releases
    "2024-11-05 (Genesis)"     :milestone, 2024-11-05, 0d
    "2025-03-26"               :milestone, 2025-03-26, 0d
    "2025-06-18"               :milestone, 2025-06-18, 0d
    "2025-11-25 (1st Anniv)"   :milestone, 2025-11-25, 0d
    "2026-07-28 (RC)"          :active, 2026-05-21, 2026-07-28
    section Adoption
    "Registry Launch"          :crit, 2025-09-08, 1d
    "Agentic AI Foundation"    :crit, 2025-12-09, 1d
    "~2,000 Servers"           :2025-11-25, 1d
```

**Sources:** [blog/content/posts/2025-11-25-first-mcp-anniversary.md:17-35](), [blog/content/posts/2025-09-26-mcp-next-version-update.md:15-25](), [blog/content/posts/2025-12-09-mcp-joins-agentic-ai-foundation.md:1-10]()

## Release History

### Version 2024-11-05 (Genesis)
The initial release established the core JSON-RPC 2.0 foundation.
- **Transports**: Introduced `stdio` and initial HTTP+SSE patterns.
- **Primitives**: Tools, Resources, and Prompts.
- **Lifecycle**: Initial `initialize` handshake. [docs/specification/2025-06-18/basic/lifecycle.mdx:38-74]()

### Version 2025-06-18
Focused on transport standardization and security.
- **Streamable HTTP**: Standardized the HTTP transport mechanism. [blog/content/posts/2025-09-26-mcp-next-version-update.md:64-65]()
- **Structured Tool Output**: Added support for complex tool results. [blog/content/posts/2025-09-26-mcp-next-version-update.md:23-26]()
- **OAuth-based Authorization**: Integrated OAuth 2.1 for secure resource access. [blog/content/posts/2025-09-26-mcp-next-version-update.md:23-26]()
- **Elicitation**: Support for server-initiated user interactions. [blog/content/posts/2025-09-26-mcp-next-version-update.md:23-26]()

### Version 2025-11-25 (First Anniversary)
Major leap in agentic capabilities and ecosystem maturation.
- **Asynchronous Operations (SEP-1391)**: Support for long-running tasks. [blog/content/posts/2025-09-26-mcp-next-version-update.md:55-60]()
- **Statelessness and Scalability**: Improvements to Streamable HTTP for enterprise-scale deployments. [blog/content/posts/2025-09-26-mcp-next-version-update.md:61-66]()
- **Server Identity**: Introduction of `.well-known` URLs for server discovery. [blog/content/posts/2025-09-26-mcp-next-version-update.md:67-72]()
- **Official Extensions**: Standardization of common industry patterns (e.g., MCP Apps/SEP-1865). [blog/content/posts/2025-11-21-mcp-apps.md:22-24](), [blog/content/posts/2025-09-26-mcp-next-version-update.md:73-78]()
- **SDK Tiering**: Clear classification system for SDK support and compliance. [blog/content/posts/2025-09-26-mcp-next-version-update.md:79-84]()
- **MCP Bundles (.mcpb)**: Standardized distribution format for local servers. [blog/content/posts/2025-11-20-adopting-mcpb.md:15-30]()

### Draft Release Candidate (2026-07-28)
A fundamental shift toward stateless, horizontally scalable architecture.
- **Stateless Capability Negotiation**: Moving from the `initialize` handshake to per-request capability headers.
- **Server Discover**: New `server/discover` method to replace the monolithic `initialize` result.
- **MRTR Pattern**: Model-Request-Tool-Response pattern for cleaner agentic loops.
- **Handle Pattern**: Stateful tool handles for managing resources across requests in a stateless transport.

**Sources:** [blog/content/posts/2025-11-25-first-mcp-anniversary.md:19-65](), [blog/content/posts/2025-09-26-mcp-next-version-update.md:51-84](), [blog/content/posts/2025-11-20-adopting-mcpb.md:15-30]()

## Strategic Roadmap (2026+)

The roadmap is driven by Working Groups (WGs) addressing production scaling and enterprise requirements.

### 1. Transport Evolution and Scalability
The **Transports WG** is evolving Streamable HTTP to support stateless operation across multiple server instances behind load balancers.
- **Session Resumption**: Protocols for migrating sessions across server restarts. [docs/development/roadmap.mdx:30-31]()
- **MCP Server Cards**: `.well-known` metadata for capability discovery without connection. [docs/development/roadmap.mdx:32-33]()

### 2. Agent Communication
The **Agents WG** is refining the Tasks primitive and agentic patterns.
- **Retry Semantics**: Defining failure handling for transient task errors. [docs/development/roadmap.mdx:45-46]()
- **Expiry Policies**: Standardizing result retention and expiration notifications. [docs/development/roadmap.mdx:46-47]()

### 3. Enterprise Readiness
The **Enterprise WG** (proposed) focuses on high-compliance environments.
- **Audit Trails**: End-to-end visibility for logging and compliance pipelines. [docs/development/roadmap.mdx:66-67]()
- **Managed Auth**: SSO-integrated flows to replace static client secrets. [docs/development/roadmap.mdx:68-69]()
- **Gateway Patterns**: Standardizing behavior for intermediaries and proxies. [docs/development/roadmap.mdx:70-71]()

### 4. Governance Maturation
The **Governance WG** is formalizing the community leadership path.
- **Contributor Ladder**: Defined progression from participant to Core Maintainer. [docs/development/roadmap.mdx:56-57]()
- **Delegation Model**: Allowing WGs to accept SEPs within their domain autonomously. [docs/development/roadmap.mdx:58-59]()

**Sources:** [docs/development/roadmap.mdx:16-72]()

## Code Entity Mapping: Release Infrastructure

This diagram maps release and roadmap concepts to the code entities that manage them.

Title: Release and Roadmap Infrastructure
```mermaid
classDiagram
    class SEP_Automation {
        +SEPProcessor
        +TransitionHandler
        +MaintainerResolver
    }
    class Schema_Generation {
        +TypeScriptSource
        +JsonSchemaGenerator
        +VersionedSnapshot
    }
    class Roadmap_Priorities {
        <<Interface>>
        +TransportEvolution
        +AgentCommunication
        +EnterpriseReadiness
    }

    SEP_Automation ..> Roadmap_Priorities : "Automates lifecycle of"
    Schema_Generation ..> Roadmap_Priorities : "Implements protocol for"
    
    note for SEP_Automation "tools/sep-automation/src/SEPProcessor.ts"
    note for Schema_Generation "scripts/generate-schemas.ts"
```

**Sources:** [docs/development/roadmap.mdx:16-72](), [blog/content/posts/2025-11-28-sep-process-update.md:14-46]()

## Protocol Adoption Trajectory

MCP's growth from a "small experiment" to an industry standard.

Title: Evolution from Experiment to Standard
```mermaid
graph TD
    subgraph "Natural Language (Adoption Milestones)"
        A["Initial Announcement (Nov 2024)"]
        B["Registry Preview (Sept 2025)"]
        C["Agentic AI Foundation (Dec 2025)"]
    end

    subgraph "Code Entities (Implementation)"
        D["@modelcontextprotocol/sdk"]
        E["modelcontextprotocol/registry"]
        F["seps/1850-your-feature.md"]
    end

    A --> D
    B --> E
    C --> F
```

**Sources:** [blog/content/posts/2025-11-25-first-mcp-anniversary.md:17-35](), [blog/content/posts/2025-12-09-mcp-joins-agentic-ai-foundation.md:1-10](), [blog/content/posts/2025-11-28-sep-process-update.md:30-41]()

---

# Page: Tools and Debugging

# Tools and Debugging

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [blog/content/posts/2026-01-26-mcp-apps.md](blog/content/posts/2026-01-26-mcp-apps.md)
- [docs/community/sdk-tiers.mdx](docs/community/sdk-tiers.mdx)
- [docs/docs/getting-started/intro.mdx](docs/docs/getting-started/intro.mdx)
- [docs/docs/tools/debugging.mdx](docs/docs/tools/debugging.mdx)
- [docs/docs/tools/inspector.mdx](docs/docs/tools/inspector.mdx)
- [docs/extensions/apps/build.mdx](docs/extensions/apps/build.mdx)
- [docs/extensions/apps/overview.mdx](docs/extensions/apps/overview.mdx)
- [docs/extensions/auth/oauth-client-credentials.mdx](docs/extensions/auth/oauth-client-credentials.mdx)
- [docs/extensions/auth/overview.mdx](docs/extensions/auth/overview.mdx)
- [docs/extensions/client-matrix.mdx](docs/extensions/client-matrix.mdx)
- [docs/extensions/overview.mdx](docs/extensions/overview.mdx)
- [docs/extensions/tasks/overview.mdx](docs/extensions/tasks/overview.mdx)

</details>



This page provides a high-level overview of the development tools, debugging techniques, and AI-assisted utilities available for working with the Model Context Protocol (MCP). The ecosystem includes the **MCP Inspector** for interactive server testing, a comprehensive suite of **Debugging Techniques** for troubleshooting integrations, and a specialized **Claude Plugin** for researching and drafting protocol enhancements.

## Overview

Developing for MCP requires visibility into the JSON-RPC message exchange and the execution environment of servers. Because many MCP servers run as subprocesses (STDIO transport), standard debugging patterns like `print()` can interfere with protocol operations [docs/docs/tools/debugging.mdx:36-41](). The tooling ecosystem is designed to provide this visibility without disrupting the communication flow.

For detailed documentation on specific tools, see the child pages:
- **[MCP Inspector](#9.1)**: Interactive testing UI for servers.
- **[Development Tools and Debugging](#9.2)**: Log analysis, environment handling, and troubleshooting.
- **[Claude Plugin for MCP Spec](#9.3)**: AI skills for SEP drafting and GitHub research.

## MCP Inspector

The **MCP Inspector** is a command-line utility that provides a web-based interface for testing MCP servers in isolation [docs/docs/tools/inspector.mdx:6-7](). It acts as a reference client, allowing developers to discover and execute tools, resources, and prompts without needing to configure a full host application like Claude Desktop [docs/docs/tools/inspector.mdx:84-112]().

### Execution and Interface
The Inspector is typically invoked via `npx` and launches the target server as a subprocess using the `stdio` transport [docs/docs/tools/inspector.mdx:12-16]().

```bash
npx @modelcontextprotocol/inspector <command> <args>
```

The interface allows for:
- **Tool Testing**: Validating input schemas and viewing execution results [docs/docs/tools/inspector.mdx:105-110]().
- **Resource Inspection**: Reading contents and monitoring MIME types [docs/docs/tools/inspector.mdx:91-96]().
- **Notification Tracking**: Real-time monitoring of server-sent events and logs [docs/docs/tools/inspector.mdx:112-115]().

For details, see [MCP Inspector](#9.1).

**Sources**: [docs/docs/tools/inspector.mdx:6-115](), [docs/docs/tools/debugging.mdx:14-19]()

## Debugging Techniques

Debugging MCP integrations involves monitoring the "outer" transport layer and the "inner" data layer. A critical pitfall in MCP development is **STDIO stream corruption**: writing directly to `stdout` in a local server will break the JSON-RPC framing [docs/docs/tools/debugging.mdx:36-41]().

### Key Debugging Strategies
- **Logging to Stderr**: Servers must use `stderr` for traditional logging to avoid corrupting the protocol stream [docs/docs/tools/debugging.mdx:31-34]().
- **Log Message Notifications**: Using the `notifications/message` method to send structured logs to the client [docs/docs/tools/debugging.mdx:51-73]().
- **Client Logs**: Accessing host-specific logs (e.g., `~/Library/Logs/Claude` on macOS) to see connection events and raw message exchanges [docs/docs/tools/debugging.mdx:203-225]().
- **Environment Handling**: Ensuring servers have the correct absolute paths and environment variables, as subprocesses often inherit a restricted environment [docs/docs/tools/debugging.mdx:98-107]().

For details, see [Development Tools and Debugging](#9.2).

**Sources**: [docs/docs/tools/debugging.mdx:31-107](), [docs/docs/tools/debugging.mdx:203-225]()

## Claude Plugin for MCP Spec

The `plugins/mcp-spec` directory contains a specialized plugin for Claude that assists in the evolution of the protocol. It provides "Agent Skills" that encode the governance and research processes of the MCP project.

### Available Skills
- **`/search-mcp-github`**: Performs deep-dive research across the `modelcontextprotocol` GitHub organization, including issues, PRs, and Discussions, to find historical design rationale.
- **`/draft-sep`**: An interactive workflow that interviews an author, checks current specification coverage, and generates a Specification Enhancement Proposal (SEP) following the official template.

For details, see [Claude Plugin for MCP Spec](#9.3).

**Sources**: [plugins/mcp-spec/skills/draft-sep/SKILL.md:1-13](), [plugins/mcp-spec/skills/search-mcp-github/SKILL.md:1-10]()

## Tooling and Debugging Architecture

The following diagram illustrates how debugging tools sit between the "Natural Language Space" (where the developer or AI operates) and the "Code Entity Space" (the protocol implementation).

### Debugging Data Flow
```mermaid
graph TD
    subgraph "Natural Language Space"
        User["Developer / AI Agent"]
        ClaudePlugin["Claude Plugin (/draft-sep)"]
    end

    subgraph "Code Entity Space"
        subgraph "Testing Tools"
            Inspector["@modelcontextprotocol/inspector"]
            DevTools["Chrome DevTools (allowDevTools)"]
        end

        subgraph "Server Implementation"
            McpServer["McpServer / FastMCP Instance"]
            StdioTransport["StdioServerTransport / StdioClientTransport"]
        end

        subgraph "Persistence & Logs"
            LogFiles["mcp*.log (Claude Desktop Logs)"]
            Config["claude_desktop_config.json"]
        end
    end

    User -->|"/draft-sep"| ClaudePlugin
    User -->|"npx"| Inspector
    Inspector -->|"JSON-RPC over"| StdioTransport
    StdioTransport --> McpServer
    McpServer -->|"stderr"| LogFiles
    Config -->|"env / args"| StdioTransport
    DevTools -->|"inspect"| McpServer
```
**Sources**: [docs/docs/tools/debugging.mdx:14-25](), [docs/docs/tools/debugging.mdx:232-237](), [docs/docs/tools/inspector.mdx:84-89]()

### AI-Assisted Development Workflow
This diagram shows how Agent Skills bridge the gap between high-level ideas and concrete codebase entities like the SEP templates.

```mermaid
graph LR
    subgraph "Natural Language Space"
        Idea["'Add WebSocket Transport'"]
        Research["Prior Art Research"]
    end

    subgraph "Code Entity Space"
        Skill["plugins/mcp-spec/skills/draft-sep"]
        Template["seps/TEMPLATE.md"]
        Schema["specification/schema.ts"]
        SEP["seps/0000-new-feature.md"]
    end

    Idea --> Skill
    Skill -->| "reads" | Template
    Skill -->| "references" | Schema
    Research -->| "GitHub API" | Skill
    Skill -->| "writes" | SEP
```
**Sources**: [plugins/mcp-spec/skills/draft-sep/SKILL.md:1-13](), [docs/community/sdk-tiers.mdx:83-90]()

## Related Pages
- **[MCP Inspector](#9.1)**: Detailed usage of the inspector tool.
- **[Development Tools and Debugging](#9.2)**: Comprehensive troubleshooting guide.
- **[Claude Plugin for MCP Spec](#9.3)**: Documentation for spec-contribution skills.
- **[Specification Enhancement Process (SEP)](#7.2)**: The process the Claude Plugin helps automate.

---

# Page: MCP Inspector

# MCP Inspector

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [blog/content/posts/2026-01-26-mcp-apps.md](blog/content/posts/2026-01-26-mcp-apps.md)
- [docs/community/sdk-tiers.mdx](docs/community/sdk-tiers.mdx)
- [docs/docs/getting-started/intro.mdx](docs/docs/getting-started/intro.mdx)
- [docs/docs/tools/debugging.mdx](docs/docs/tools/debugging.mdx)
- [docs/docs/tools/inspector.mdx](docs/docs/tools/inspector.mdx)
- [docs/extensions/apps/build.mdx](docs/extensions/apps/build.mdx)
- [docs/extensions/apps/overview.mdx](docs/extensions/apps/overview.mdx)
- [docs/extensions/auth/oauth-client-credentials.mdx](docs/extensions/auth/oauth-client-credentials.mdx)
- [docs/extensions/auth/overview.mdx](docs/extensions/auth/overview.mdx)
- [docs/extensions/client-matrix.mdx](docs/extensions/client-matrix.mdx)
- [docs/extensions/overview.mdx](docs/extensions/overview.mdx)
- [docs/extensions/tasks/overview.mdx](docs/extensions/tasks/overview.mdx)

</details>



The MCP Inspector is an interactive developer tool for testing and debugging MCP servers during development. It provides a graphical interface for discovering server capabilities, executing tools, reading resources, testing prompts, and monitoring server behavior without requiring integration with a production MCP client.

For information about broader debugging strategies and using the Inspector as part of a complete debugging workflow, see [Development Tools and Debugging](#9.2).

## Purpose and Scope

The Inspector serves as a standalone MCP client implementation with developer-focused features. Its primary purposes are:

- **Server validation**: Verify that an MCP server correctly implements the protocol specification [docs/docs/tools/inspector.mdx:1-7]().
- **Interactive testing**: Manually test tools, resources, and prompts before client integration [docs/docs/tools/inspector.mdx:84-111]().
- **Development iteration**: Rapidly test changes during server development without restarting a full client application [docs/docs/tools/inspector.mdx:120-132]().
- **Protocol debugging**: Inspect message exchanges and server behavior at the protocol level [docs/docs/tools/debugging.mdx:14-19]().

The Inspector is not intended for production use or end-user interactions. It is exclusively a development and testing tool for server authors.

## Architecture and Design

### Inspector as MCP Client

The Inspector functions as a host environment that instantiates an MCP client to communicate with a target server. It supports both local (stdio) and remote (SSE) transport mechanisms.

Inspector Architecture Overview:
```mermaid
graph TB
    subgraph "MCP_Inspector_Process"
        UI["Web_UI<br/>(Browser_Interface)"]
        Client["MCP_Client_Session<br/>(ClientSession)"]
        TransportMgr["Transport_Manager"]
    end
    
    subgraph "Server_Process"
        Server["MCP_Server<br/>(FastMCP/McpServer)"]
    end
    
    subgraph "Transport_Implementations"
        StdioTransport["StdioClientTransport<br/>(Local_Servers)"]
        HTTPTransport["SSEClientTransport<br/>(Remote_Servers)"]
    end
    
    UI -->|"User_Actions"| Client
    Client -->|"JSON-RPC_Messages"| TransportMgr
    TransportMgr -->|"stdio"| StdioTransport
    TransportMgr -->|"HTTP/SSE"| HTTPTransport
    StdioTransport -->|"stdin/stdout"| Server
    HTTPTransport -->|"HTTP_POST/SSE"| Server
    Server -->|"JSON-RPC_Responses"| TransportMgr
    TransportMgr -->|"Protocol_Messages"| Client
    Client -->|"State_Updates"| UI
```
Sources: [docs/docs/tools/inspector.mdx:84-90](), [docs/docs/tools/debugging.mdx:14-19]()

### Protocol Message Flow

The Inspector follows the standard MCP lifecycle, beginning with an initialization handshake before enabling feature discovery. It negotiates capabilities such as logging and support for experimental extensions like Tasks or Apps if the server advertises them.

Inspector Protocol Interaction Sequence:
```mermaid
sequenceDiagram
    participant User
    participant Inspector["MCP_Inspector<br/>(ClientSession)"]
    participant Server["MCP_Server"]
    
    Note over User,Server: Connection Phase
    User->>Inspector: npx @modelcontextprotocol/inspector <command>
    Inspector->>Server: Launch process (stdio) or Connect (SSE)
    Inspector->>Server: initialize request (capabilities)
    Server-->>Inspector: initialize response (capabilities)
    Inspector->>Server: initialized notification
    
    Note over User,Server: Discovery Phase
    Inspector->>Server: tools/list
    Server-->>Inspector: ListToolsResult
    Inspector->>Server: resources/list
    Server-->>Inspector: ListResourcesResult
    Inspector->>Server: prompts/list
    Server-->>Inspector: ListPromptsResult
    
    Note over User,Server: Interactive Testing Phase
    User->>Inspector: Input tool arguments
    Inspector->>Server: tools/call (name, arguments)
    Server-->>Inspector: CallToolResult
    Inspector->>User: Render Result
```
Sources: [docs/docs/tools/inspector.mdx:120-132](), [docs/extensions/tasks/overview.mdx:76-101](), [docs/extensions/apps/overview.mdx:78-96]()

## Installation and Execution

The Inspector is designed to be run without permanent installation using `npx` [docs/docs/tools/inspector.mdx:12-16]().

### Execution Patterns by Server Type

| Server Type | Command Pattern | Example |
| :--- | :--- | :--- |
| **npm package** | `npx -y @modelcontextprotocol/inspector npx <package> <args>` | `npx -y @modelcontextprotocol/inspector npx @modelcontextprotocol/server-filesystem /Users/Desktop` |
| **PyPI package** | `npx @modelcontextprotocol/inspector uvx <package> <args>` | `npx @modelcontextprotocol/inspector uvx mcp-server-git --repository ~/repo` |
| **Local TS/JS** | `npx @modelcontextprotocol/inspector node <path/to/index.js>` | `npx @modelcontextprotocol/inspector node ./dist/index.js` |
| **Local Python** | `npx @modelcontextprotocol/inspector uv --directory <dir> run <package>` | `npx @modelcontextprotocol/inspector uv --directory ./server run weather.py` |

Sources: [docs/docs/tools/inspector.mdx:22-74]()

## Feature Overview

### Server Connection Pane
The connection pane allows developers to select the transport (stdio or HTTP) and configure environment variables or command-line arguments [docs/docs/tools/inspector.mdx:86-90]().

### Resources Tab
*   **Discovery**: Lists all available resources and resource templates [docs/docs/tools/inspector.mdx:93-94]().
*   **Inspection**: Allows reading resource contents via `resources/read` [docs/docs/tools/inspector.mdx:95]().
*   **Subscriptions**: Supports testing resource subscription updates [docs/docs/tools/inspector.mdx:96]().

### Prompts Tab
*   **Templates**: Lists available prompt templates [docs/docs/tools/inspector.mdx:99]().
*   **Arguments**: Provides a UI to fill in required arguments defined in the prompt's schema [docs/docs/tools/inspector.mdx:100-102]().
*   **Preview**: Shows the generated message array [docs/docs/tools/inspector.mdx:103]().

### Tools Tab
*   **Schema Validation**: Displays the JSON Schema for tool inputs [docs/docs/tools/inspector.mdx:108]().
*   **Interactive Call**: Allows users to input JSON arguments and execute `tools/call` [docs/docs/tools/inspector.mdx:109]().
*   **Output Visualization**: Renders the result returned by the server [docs/docs/tools/inspector.mdx:110]().

### Notifications Pane
Captures all asynchronous communication from the server:
*   **Logs**: Displays `notifications/message` events at various severity levels [docs/docs/tools/debugging.mdx:20-22]().
*   **Updates**: Shows notifications received from the server, such as `list_changed` [docs/docs/tools/inspector.mdx:115]().

Sources: [docs/docs/tools/inspector.mdx:84-116]()

## Extension Support in Inspector

The Inspector acts as a testing ground for protocol extensions. While primarily used for core protocol features, it is a key tool for validating extension implementations:

*   **MCP Tasks**: The Inspector can be used to monitor `CreateTaskResult` and poll for task status via `tasks/get` [docs/extensions/tasks/overview.mdx:44-74]().
*   **MCP Apps**: Developers can verify if a tool correctly returns `_meta.ui.resourceUri` metadata which would trigger UI rendering in a production client [blog/content/posts/2026-01-26-mcp-apps.md:69-81]().

Sources: [docs/extensions/tasks/overview.mdx:44-74](), [blog/content/posts/2026-01-26-mcp-apps.md:69-81]()

## Development Workflow Integration

### Iterative Testing Pattern
The Inspector is optimized for a tight feedback loop:
1.  **Launch**: Start the Inspector with the server command [docs/docs/tools/inspector.mdx:122]().
2.  **Verify**: Check that capabilities are correctly negotiated in the initialization phase [docs/docs/tools/inspector.mdx:124]().
3.  **Test**: Execute tools with edge-case inputs (e.g., invalid types, missing fields) [docs/docs/tools/inspector.mdx:133-137]().
4.  **Debug**: Monitor the Notifications pane for stderr output or protocol errors [docs/docs/tools/inspector.mdx:113-116]().
5.  **Refine**: Modify server code, rebuild, and reconnect the Inspector [docs/docs/tools/inspector.mdx:127-130]().

### Best Practices for Logging
When testing with the Inspector:
*   **STDIO Servers**: Ensure the server logs to `stderr` and not `stdout`. `stdout` is reserved for JSON-RPC messages; writing logs there will corrupt the transport [docs/docs/tools/debugging.mdx:36-41]().
*   **Severity Levels**: Use appropriate RFC 5424 levels (debug, info, error) so they can be filtered in the Inspector UI [docs/docs/tools/debugging.mdx:75-81]().

Sources: [docs/docs/tools/inspector.mdx:119-138](), [docs/docs/tools/debugging.mdx:27-73]()

---

# Page: Development Tools and Debugging

# Development Tools and Debugging

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [blog/content/posts/2026-01-26-mcp-apps.md](blog/content/posts/2026-01-26-mcp-apps.md)
- [docs/community/sdk-tiers.mdx](docs/community/sdk-tiers.mdx)
- [docs/docs/develop/build-client.mdx](docs/docs/develop/build-client.mdx)
- [docs/docs/develop/build-server.mdx](docs/docs/develop/build-server.mdx)
- [docs/docs/develop/build-with-agent-skills.mdx](docs/docs/develop/build-with-agent-skills.mdx)
- [docs/docs/getting-started/intro.mdx](docs/docs/getting-started/intro.mdx)
- [docs/docs/learn/architecture.mdx](docs/docs/learn/architecture.mdx)
- [docs/docs/learn/client-concepts.mdx](docs/docs/learn/client-concepts.mdx)
- [docs/docs/learn/server-concepts.mdx](docs/docs/learn/server-concepts.mdx)
- [docs/docs/sdk.mdx](docs/docs/sdk.mdx)
- [docs/docs/tools/debugging.mdx](docs/docs/tools/debugging.mdx)
- [docs/extensions/apps/build.mdx](docs/extensions/apps/build.mdx)
- [docs/extensions/apps/overview.mdx](docs/extensions/apps/overview.mdx)
- [docs/extensions/auth/oauth-client-credentials.mdx](docs/extensions/auth/oauth-client-credentials.mdx)
- [docs/extensions/auth/overview.mdx](docs/extensions/auth/overview.mdx)
- [docs/extensions/client-matrix.mdx](docs/extensions/client-matrix.mdx)
- [docs/extensions/overview.mdx](docs/extensions/overview.mdx)
- [docs/extensions/tasks/overview.mdx](docs/extensions/tasks/overview.mdx)

</details>



This document provides a technical deep dive into the debugging techniques, tools, and utilities available for the Model Context Protocol (MCP). It covers implementation details for logging, interactive testing via the MCP Inspector, client-side debugging, and common pitfalls related to execution environments and stream corruption.

## Debugging Architecture

MCP debugging spans the entire stack, from low-level transport stream monitoring to high-level UI inspection in host applications. Because MCP SDKs abstract away many concerns [docs/docs/learn/architecture.mdx:9-11](), understanding the data flow between these layers is essential for troubleshooting.

### Tooling and Data Flow

The following diagram illustrates how debugging information flows from the server to various developer tools, bridging the "Natural Language Space" of user logs to the "Code Entity Space" of the protocol.

**Figure 1: MCP Debugging Data Flow and Entity Mapping**
```mermaid
graph TD
    subgraph "MCP_Server_Process"
        ServerCode["Server Implementation<br/>(FastMCP / McpServer)"]
        StdErr["stderr Stream<br/>(System.err / sys.stderr)"]
        StdOut["stdout Stream<br/>(JSON-RPC Framing)"]
    end

    subgraph "Transport_Layer"
        Stdio["stdio_client / stdio_server<br/>(Transport Layer)"]
        HTTP["Streamable HTTP<br/>(SSE / POST)"]
    end

    subgraph "Developer_Tools"
        Inspector["MCP Inspector<br/>(npx @modelcontextprotocol/inspector)"]
        ClientLogs["Client Log Files<br/>(mcp.log / mcp-server-*.log)"]
        DevTools["Chrome DevTools<br/>(Console/Network)"]
    end

    ServerCode -- "logging.info() / console.error()" --> StdErr
    ServerCode -- "sendLoggingMessage()" --> StdOut
    
    StdErr -- "Captured by Host" --> ClientLogs
    StdOut -- "JSON-RPC Notifications" --> Inspector
    StdOut -- "JSON-RPC Notifications" --> DevTools
    
    Stdio -- "Pipe stderr" --> ClientLogs
    HTTP -- "SSE Events" --> DevTools
```
**Sources:** [docs/docs/develop/build-server.mdx:44-70](), [docs/docs/learn/architecture.mdx:75-102](), [docs/docs/develop/build-client.mdx:102-107]()

## MCP Inspector

The **MCP Inspector** is the primary tool for isolated server testing [docs/docs/learn/architecture.mdx:19](). It acts as a generic MCP client, allowing developers to manually trigger server capabilities without a full AI host like Claude.

### Execution Patterns
The Inspector is typically invoked via `npx` and can wrap various runtimes to initiate the `stdio` transport connection:

| Runtime | Command Example |
| :--- | :--- |
| **npm** | `npx -y @modelcontextprotocol/inspector npx @modelcontextprotocol/server-filesystem /path` |
| **Python (uv)** | `npx @modelcontextprotocol/inspector uvx mcp-server-git --repository ~/repo` |
| **Node.js** | `npx @modelcontextprotocol/inspector node path/to/server/index.js` |

**Sources:** [docs/docs/develop/build-server.mdx:109-110](), [docs/docs/develop/build-client.mdx:140-146]()

### Feature Testing via Protocol Primitives
The Inspector interface allows direct interaction with the `Data Layer` primitives defined in the specification [docs/docs/learn/architecture.mdx:77-81]():

*   **Resources**: Tests `resources/list` and `resources/read` methods. It can also monitor `resources/subscribe` for real-time data updates [docs/docs/learn/server-concepts.mdx:115-120]().
*   **Prompts**: Tests `prompts/list` and `prompts/get`, allowing developers to verify how arguments are injected into templates [docs/docs/learn/server-concepts.mdx:14-18]().
*   **Tools**: Tests `tools/list` and `tools/call`. It validates the `arguments` object against the server's `inputSchema` (JSON Schema) before execution [docs/docs/learn/server-concepts.mdx:32-35]().

## Logging and Stream Integrity

Proper logging is critical in MCP, especially for the **STDIO transport**, where the communication channel is shared with standard output.

### The STDIO Corruption Pitfall
In STDIO-based servers, `stdout` is reserved strictly for JSON-RPC 2.0 messages [docs/docs/learn/architecture.mdx:84-85](). Writing arbitrary text to `stdout` (e.g., using `print()` in Python or `console.log()` in JS) will corrupt the message framing and break the server [docs/docs/develop/build-server.mdx:48-50]().

**Figure 2: Stream Handling Logic**
```mermaid
graph LR
    subgraph "Application_Logic"
        LogCall["logging.error('Init')"]
        ResultCall["return ToolResult"]
    end

    subgraph "SDK_Transport_Handling"
        McpServer["FastMCP / McpServer"]
        StdErr["Process stderr"]
        StdOut["Process stdout"]
    end

    LogCall --> StdErr
    ResultCall --> McpServer
    McpServer -- "JSON-RPC 2.0 Wrapping" --> StdOut
    
    style StdOut stroke-width:4px
    style StdErr stroke-dasharray: 5 5
```
**Sources:** [docs/docs/develop/build-server.mdx:62-70](), [docs/docs/learn/architecture.mdx:98-99]()

### Implementation Examples
*   **Python (FastMCP)**: Use `logging.info()` or `print("...", file=sys.stderr)` to avoid stream corruption [docs/docs/develop/build-server.mdx:58-70]().
*   **TypeScript**: Use `console.error()` for internal logs or the SDK's `sendLoggingMessage` for protocol-level logs.

## Troubleshooting Common Issues

### Working Directory and Path Pitfalls
When launched by a host application, the server's working directory (`cwd`) may not match the developer's expectations.
*   **Issue**: Relative paths for resources or configuration files fail to resolve.
*   **Solution**: Always use **absolute paths** when configuring servers in the host (e.g., in `Claude Desktop` configuration) [docs/docs/develop/build-server.mdx:101-102]().

### Environment Variable Handling
MCP servers do not automatically inherit the user's full shell environment (e.g., `PATH` or custom aliases).
*   **Behavior**: Servers receive a minimal environment defined by the host [docs/docs/develop/build-client.mdx:140-144]().
*   **Mitigation**: Explicitly define required variables like `API_KEYS` in the `env` property of the `StdioServerParameters` or the host's configuration file [docs/docs/develop/build-client.mdx:112-114]().

### Conformance and SDK Tiers
If a server behaves inconsistently across different clients, it may be due to varying levels of protocol support in the SDKs.
*   **Tier 1 SDKs**: (TypeScript, Python, C#, Go) have 100% conformance and support all non-experimental features [docs/community/sdk-tiers.mdx:23-24](), [docs/docs/sdk.mdx:12-15]().
*   **Tier 2/3 SDKs**: May lack support for advanced features like `Sampling` or `Elicitation` [docs/community/sdk-tiers.mdx:25-26]().
*   **Validation**: Use the official [automated conformance tests](https://github.com/modelcontextprotocol/conformance) to validate SDK behavior against the spec [docs/community/sdk-tiers.mdx:61-63]().

## Advanced Debugging Tools

### Agent-Assisted Debugging
The `mcp-server-dev` plugin provides agent skills to help scaffold and debug servers [docs/docs/develop/build-with-agent-skills.mdx:13-15]():
*   `build-mcp-server`: Interrogates the use case to pick the right deployment model (e.g., Streamable HTTP vs Stdio) [docs/docs/develop/build-with-agent-skills.mdx:19]().
*   `build-mcp-app`: Scaffolds interactive UI widgets for the [MCP Apps](/extensions/apps/overview) extension [docs/docs/develop/build-with-agent-skills.mdx:20]().

### Extension Debugging (MCP Apps & Tasks)
*   **MCP Apps**: Debugged via Chrome DevTools within the host's sandboxed `iframe` [blog/content/posts/2026-01-26-mcp-apps.md:83-85](). Communication is handled via `postMessage` using a JSON-RPC dialect [docs/extensions/apps/overview.mdx:70-76]().
*   **Tasks**: Debugged by monitoring the `tasks/get` polling loop and checking for `input_required` status in the terminal [docs/extensions/tasks/overview.mdx:59-66]().

**Sources:** [docs/community/sdk-tiers.mdx:33-42](), [docs/docs/develop/build-with-agent-skills.mdx:6-21](), [docs/extensions/apps/overview.mdx:39-44](), [docs/extensions/tasks/overview.mdx:75-101]()

---

# Page: Claude Plugin for MCP Spec

# Claude Plugin for MCP Spec

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.claude-plugin/marketplace.json](.claude-plugin/marketplace.json)
- [.github/ISSUE_TEMPLATE/bug_report.yml](.github/ISSUE_TEMPLATE/bug_report.yml)
- [.github/ISSUE_TEMPLATE/config.yml](.github/ISSUE_TEMPLATE/config.yml)
- [.github/ISSUE_TEMPLATE/work_tracking.yml](.github/ISSUE_TEMPLATE/work_tracking.yml)
- [.prototools](.prototools)
- [AGENTS.md](AGENTS.md)
- [CLAUDE.md](CLAUDE.md)
- [plugins/mcp-spec/.claude-plugin/plugin.json](plugins/mcp-spec/.claude-plugin/plugin.json)
- [plugins/mcp-spec/README.md](plugins/mcp-spec/README.md)
- [plugins/mcp-spec/skills/draft-sep/SKILL.md](plugins/mcp-spec/skills/draft-sep/SKILL.md)
- [plugins/mcp-spec/skills/search-mcp-github/SKILL.md](plugins/mcp-spec/skills/search-mcp-github/SKILL.md)
- [seps/TEMPLATE.md](seps/TEMPLATE.md)

</details>



The `plugins/mcp-spec` directory contains the official Claude plugin designed to assist developers and maintainers in researching and contributing to the Model Context Protocol (MCP) specification [plugins/mcp-spec/README.md:1-3](). This plugin provides AI-assisted skills that automate the complex workflows involved in protocol governance, specifically around the Specification Enhancement Proposal (SEP) process and cross-repository research on GitHub [plugins/mcp-spec/README.md:17-41]().

## Plugin Architecture and Skills

The plugin is structured as a set of skills that leverage the GitHub CLI (`gh`), local git commands, and the MCP documentation server to perform deep analysis of the protocol's history and current state [plugins/mcp-spec/skills/draft-sep/SKILL.md:15-19](), [plugins/mcp-spec/skills/search-mcp-github/SKILL.md:14-19](). It is integrated into the Claude ecosystem via the marketplace configuration [ .claude-plugin/marketplace.json:1-17]().

### Data Flow: AI-Assisted Research and Authoring

The following diagram illustrates how the plugin's skills bridge natural language requests to specific codebase entities and external data sources.

**MCP Spec Plugin Integration Map**
```mermaid
graph TD
    subgraph "NaturalLanguageSpace"["Natural Language Space"]
        User["User Intent (e.g., 'Draft a SEP for WebSockets')"]
    end

    subgraph "ClaudePluginSpace"["Claude Plugin Space (plugins/mcp-spec)"]
        DraftSkill["Skill: draft-sep"]
        SearchSkill["Skill: search-mcp-github"]
    end

    subgraph "CodeEntitySpace"["Code Entity Space"]
        Template["seps/TEMPLATE.md"]
        SchemaSource["schema/draft/schema.ts"]
        Maintainers["MAINTAINERS.md"]
        DocsServer["mcp-docs (MCP Server)"]
        GHTool["gh CLI / GraphQL API"]
    end

    User -->|Invocable| DraftSkill
    User -->|Invocable| SearchSkill
    
    DraftSkill -->|Reads| Template
    DraftSkill -->|Inspects| Maintainers
    DraftSkill -->|Validates| SchemaSource
    
    SearchSkill -->|Queries| DocsServer
    SearchSkill -->|Executes| GHTool
    
    DraftSkill -.->|Calls| SearchSkill
```
Sources: [plugins/mcp-spec/skills/draft-sep/SKILL.md:11-103](), [plugins/mcp-spec/skills/search-mcp-github/SKILL.md:14-33](), [plugins/mcp-spec/.claude-plugin/plugin.json:11-16](), [AGENTS.md:66-69]()

---

## Skill: `/search-mcp-github`

This skill provides a unified interface for searching across the entire `modelcontextprotocol` GitHub organization, including PRs, issues, and discussions [plugins/mcp-spec/skills/search-mcp-github/SKILL.md:1-10]().

### Key Functions
1.  **Multi-Source Search**: It prioritizes the `mcp-docs` server's `SearchModelContextProtocol` tool for authoritative spec content before falling back to GitHub searches [plugins/mcp-spec/skills/search-mcp-github/SKILL.md:14-19]().
2.  **Discussion Retrieval**: Since the GitHub CLI lacks a native `search discussions` command, the skill uses the GraphQL API to query repository and organization-level discussions [plugins/mcp-spec/skills/search-mcp-github/SKILL.md:25-33]().
3.  **Variant Expansion**: The skill automatically handles tokenization differences between `camelCase` (used in `schema.ts`) and space-separated text (used in natural language discussions) [plugins/mcp-spec/skills/search-mcp-github/SKILL.md:35-43]().
4.  **Maintainer Attribution**: It identifies comments from users with `MEMBER` or `OWNER` associations to highlight design intent and historical rationale [plugins/mcp-spec/skills/search-mcp-github/SKILL.md:79-94]().

Sources: [plugins/mcp-spec/skills/search-mcp-github/SKILL.md:1-119]()

---

## Skill: `/draft-sep`

The `/draft-sep` skill automates the lifecycle of creating a Specification Enhancement Proposal [plugins/mcp-spec/skills/draft-sep/SKILL.md:1-9](). It enforces the governance rules defined in `docs/community/sep-guidelines.mdx` through a multi-phase workflow [plugins/mcp-spec/skills/draft-sep/SKILL.md:11-13]().

### The SEP Authoring Pipeline

The skill executes six distinct phases to move from an idea to a pull request.

**SEP Drafting Workflow**
```mermaid
sequenceDiagram
    participant U as "User"
    participant S as "/draft-sep Skill"
    participant FS as "Filesystem (seps/)"
    participant GH as "GitHub API"

    U->>S: "/draft-sep {idea}"
    Note over S: Phase 1: Gate
    S->>S: "Check if SEP-worthy"
    Note over S: Phase 2: Interview
    S->>U: "Ask 6 Questions"
    U-->>S: "Type, Breaking, Prototype, Sponsor, etc."
    Note over S: Phase 3: Research
    S->>S: "Search GitHub & schema/draft/schema.ts"
    Note over S: Phase 4: Draft
    S->>FS: "Fill seps/TEMPLATE.md"
    Note over S: Phase 5: Post-processing
    S->>FS: "npm run generate:seps"
    Note over S: Phase 6: Submit
    S->>GH: "gh pr create --draft"
```
Sources: [plugins/mcp-spec/skills/draft-sep/SKILL.md:27-103](), [plugins/mcp-spec/README.md:38-51](), [AGENTS.md:78-81]()

### Phase Implementation Details

| Phase | Responsibility | Key Code Entities / Actions |
| :--- | :--- | :--- |
| **1. Gate** | Filter out non-SEP changes | Redirects bug fixes or typos to regular PRs [plugins/mcp-spec/skills/draft-sep/SKILL.md:27-39](). |
| **2. Interview** | Collect metadata | Captures `Author`, `Sponsor`, and `Security Implications` [plugins/mcp-spec/skills/draft-sep/SKILL.md:49-60](). |
| **3. Research** | Contextual analysis | Searches `schema/draft/schema.ts` for touch-points and checks prior art via `/search-mcp-github` [plugins/mcp-spec/skills/draft-sep/SKILL.md:61-98](). |
| **4. Draft** | Template population | Fills `seps/TEMPLATE.md` to create `seps/0000-{slug}.md` [plugins/mcp-spec/skills/draft-sep/SKILL.md:106-113](). |
| **5. Process** | Build validation | Runs `npm run generate:seps` and `npm run format:docs` [plugins/mcp-spec/skills/draft-sep/SKILL.md:115-122](). |
| **6. Submit** | PR Creation | Executes `gh pr create --draft` and backfills the SEP number [plugins/mcp-spec/skills/draft-sep/SKILL.md:124-142](). |

Sources: [plugins/mcp-spec/skills/draft-sep/SKILL.md:27-142](), [seps/TEMPLATE.md:1-11](), [AGENTS.md:78-85]()

---

## AI Agent Contribution Policy

The plugin and its skills are subject to the repository's strict AI agent policy [AGENTS.md:5-18](). 

- **Authorization**: Agents may only open PRs if the user is a listed maintainer in `MAINTAINERS.md` or has >3 merged PRs [AGENTS.md:9-15]().
- **Disclosure**: If an agent bypasses these rules under user instruction, it must include a `disclosure.txt` file or a specific HTML comment in the PR body [AGENTS.md:19-26](), [CLAUDE.md:19-26]().
- **Validation**: Before pushing or creating PRs, the agent is expected to ensure that `npm run prep` is free of warnings and errors [AGENTS.md:39-40](), [CLAUDE.md:39-40]().
- **Issue Templates**: Blank issues are disabled; the plugin must use forms in `.github/ISSUE_TEMPLATE/` when interacting with the API [AGENTS.md:98-101](), [.github/ISSUE_TEMPLATE/config.yml:1]()

Sources: [AGENTS.md:1-26](), [CLAUDE.md:1-26](), [.github/ISSUE_TEMPLATE/bug_report.yml:1-18]()

---

# Page: Glossary

# Glossary

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitattributes](.gitattributes)
- [.github/dependabot.yml](.github/dependabot.yml)
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [MAINTAINERS.md](MAINTAINERS.md)
- [README.md](README.md)
- [SECURITY.md](SECURITY.md)
- [blog/content/posts/2026-01-26-mcp-apps.md](blog/content/posts/2026-01-26-mcp-apps.md)
- [blog/content/posts/2026-04-08-maintainer-update.md](blog/content/posts/2026-04-08-maintainer-update.md)
- [blog/static/posts/images/maintainer-update-2026-04/clare.webp](blog/static/posts/images/maintainer-update-2026-04/clare.webp)
- [blog/static/posts/images/maintainer-update-2026-04/den.jpeg](blog/static/posts/images/maintainer-update-2026-04/den.jpeg)
- [docs/community/communication.mdx](docs/community/communication.mdx)
- [docs/community/governance.mdx](docs/community/governance.mdx)
- [docs/community/sdk-tiers.mdx](docs/community/sdk-tiers.mdx)
- [docs/community/security.mdx](docs/community/security.mdx)
- [docs/community/sep-guidelines.mdx](docs/community/sep-guidelines.mdx)
- [docs/docs.json](docs/docs.json)
- [docs/docs/getting-started/intro.mdx](docs/docs/getting-started/intro.mdx)
- [docs/docs/tools/debugging.mdx](docs/docs/tools/debugging.mdx)
- [docs/docs/tutorials/security/authorization.mdx](docs/docs/tutorials/security/authorization.mdx)
- [docs/extensions/apps/build.mdx](docs/extensions/apps/build.mdx)
- [docs/extensions/apps/overview.mdx](docs/extensions/apps/overview.mdx)
- [docs/extensions/auth/oauth-client-credentials.mdx](docs/extensions/auth/oauth-client-credentials.mdx)
- [docs/extensions/auth/overview.mdx](docs/extensions/auth/overview.mdx)
- [docs/extensions/client-matrix.mdx](docs/extensions/client-matrix.mdx)
- [docs/extensions/overview.mdx](docs/extensions/overview.mdx)
- [docs/extensions/tasks/overview.mdx](docs/extensions/tasks/overview.mdx)
- [docs/seps/2260-Require-Server-requests-to-be-associated-with-Client-requests.mdx](docs/seps/2260-Require-Server-requests-to-be-associated-with-Client-requests.mdx)
- [docs/seps/2322-MRTR.mdx](docs/seps/2322-MRTR.mdx)
- [docs/seps/2663-tasks-extension.mdx](docs/seps/2663-tasks-extension.mdx)
- [docs/seps/index.mdx](docs/seps/index.mdx)
- [docs/specification/draft/basic/index.mdx](docs/specification/draft/basic/index.mdx)
- [docs/specification/draft/changelog.mdx](docs/specification/draft/changelog.mdx)
- [docs/specification/draft/client/elicitation.mdx](docs/specification/draft/client/elicitation.mdx)
- [docs/specification/draft/schema.mdx](docs/specification/draft/schema.mdx)
- [package-lock.json](package-lock.json)
- [package.json](package.json)
- [schema/draft/schema.json](schema/draft/schema.json)
- [schema/draft/schema.ts](schema/draft/schema.ts)
- [seps/2260-Require-Server-requests-to-be-associated-with-Client-requests.md](seps/2260-Require-Server-requests-to-be-associated-with-Client-requests.md)
- [seps/2322-MRTR.md](seps/2322-MRTR.md)
- [seps/2663-tasks-extension.md](seps/2663-tasks-extension.md)
- [tools/sep-automation/package-lock.json](tools/sep-automation/package-lock.json)
- [tools/sep-automation/package.json](tools/sep-automation/package.json)
- [tools/sep-automation/src/config.ts](tools/sep-automation/src/config.ts)
- [tools/sep-automation/src/github/client.ts](tools/sep-automation/src/github/client.ts)
- [tools/sep-automation/src/github/types.ts](tools/sep-automation/src/github/types.ts)
- [tools/sep-automation/src/index.ts](tools/sep-automation/src/index.ts)
- [tools/sep-automation/src/maintainers/resolver.ts](tools/sep-automation/src/maintainers/resolver.ts)
- [tools/sep-automation/src/processor.ts](tools/sep-automation/src/processor.ts)
- [tools/sep-automation/src/sep/analyzer.ts](tools/sep-automation/src/sep/analyzer.ts)
- [tools/sep-automation/test/unit/config.test.ts](tools/sep-automation/test/unit/config.test.ts)

</details>



This glossary defines technical terms, protocol concepts, and codebase-specific jargon used within the Model Context Protocol (MCP) repository. It serves as a reference for onboarding engineers to understand the relationship between the specification and its implementation.

## Core Protocol Concepts

### JSON-RPC
The foundational messaging protocol for MCP. All communications follow the JSON-RPC 2.0 specification, using `Requests`, `Responses`, and `Notifications` [schema/draft/schema.ts:26-27]().

*   **Request**: A message that expects a response, identified by a unique `id`. In MCP, the ID MUST NOT be `null` [docs/specification/draft/basic/index.mdx:33-47]().
*   **Response**: A message sent in reply to a request, containing a `result` (Success) or an `error` (Failure) [docs/specification/draft/basic/index.mdx:53-101]().
*   **Notification**: A one-way message which does not expect a response [docs/specification/draft/schema.mdx:27-29]().

### ResultType
A mandatory discriminator field in every `Result` object (as of version 2026-07-28) that allows the client to determine how to parse the response [docs/specification/draft/basic/index.mdx:75-86]().
*   `complete`: The operation finished successfully and contains final content [docs/specification/draft/basic/index.mdx:81]().
*   `input_required`: The operation is paused and requires additional user information via MRTR [docs/specification/draft/basic/index.mdx:82]().

### _meta
A reserved field in `JSONRPCMessage` types used for protocol-level metadata [schema/draft/schema.ts:35-55](). MCP-specific keys are prefixed with `io.modelcontextprotocol/` [schema/draft/schema.ts:45](). Key metadata includes:
*   `protocolVersion`: The version being used for the request [schema/draft/schema.ts:76]().
*   `clientCapabilities`: The capabilities for the specific request [schema/draft/schema.ts:98]().

### MRTR (Multi Round-Trip Requests)
A pattern introduced in [SEP-2322] where a server responds with `resultType: "input_required"` to request more information before completing the original request [docs/specification/draft/changelog.mdx:24-26](). The client retries the original request providing the requested information in `inputResponses` [docs/specification/draft/changelog.mdx:24-26]().

### Transport
The mechanism for moving JSON-RPC messages between peers.
*   **STDIO**: Communication via standard input/output streams, typically for local processes [docs/docs/tutorials/security/authorization.mdx:21-23]().
*   **Streamable HTTP**: A stateless transport using HTTP POST for requests and a single `subscriptions/listen` stream for server-to-client notifications [docs/specification/draft/changelog.mdx:18-19]().

## System Architecture and Data Flow

The following diagram bridges the natural language concepts of a tool call to the specific code entities and types defined in the schema.

### Tool Call Flow: Natural Language to Code Entities

```mermaid
sequenceDiagram
    participant C as "Client (JSONRPCRequest)"
    participant S as "Server (JSONRPCResponse)"

    Note over C,S: Discovery Phase
    C->>S: "method: 'tools/list'" [schema/draft/schema.ts:34]()
    S-->>C: "result: { tools: Tool[] }" [schema/draft/schema.json:66]()

    Note over C,S: Execution Phase
    C->>S: "method: 'tools/call', _meta: { io.modelcontextprotocol/protocolVersion: '2026-07-28' }" [schema/draft/schema.ts:76]()
    alt "Success"
        S-->>C: "result: { resultType: 'complete', content: TextContent[] }" [docs/specification/draft/basic/index.mdx:81]()
    else "MRTR (Input Required)"
        S-->>C: "result: { resultType: 'input_required', inputRequests: ElicitationRequest }" [docs/specification/draft/basic/index.mdx:82]()
        C->>S: "Retry 'tools/call' with inputResponses" [docs/specification/draft/changelog.mdx:24-26]()
    end
```
**Sources:** [schema/draft/schema.ts:69-111](), [docs/specification/draft/basic/index.mdx:75-86](), [docs/specification/draft/changelog.mdx:24-26]().

## Domain Specific Terms

| Term | Definition | Code Pointer |
| :--- | :--- | :--- |
| **Elicitation** | A capability allowing servers to request data (Form mode) or URL navigation (URL mode) from users. | [docs/specification/draft/client/elicitation.mdx:7-15]() |
| **Sampling** | A client capability allowing a server to request a completion from the LLM hosted by the client. | [docs/docs.json:141]() |
| **Resource** | Application-driven data (like files) that a server exposes for reading. | [docs/docs.json:150]() |
| **Prompt** | Server-provided templates that help users interact with LLMs. | [docs/docs.json:149]() |
| **Tool** | Model-controlled functions that a server exposes for execution. | [schema/draft/schema.json:66]() |
| **Task** | An asynchronous operation handle (`io.modelcontextprotocol/tasks`) for long-running requests. | [seps/2663-tasks-extension.md:13-15]() |
| **Root** | A filesystem boundary provided by the client (Deprecated in draft). | [docs/docs.json:140]() |

## Governance and Tooling

### SEP (Specification Enhancement Process)
The formal process for proposing changes to the MCP specification [package.json:28]().
*   **SEP Lifecycle Automation**: A tool that manages SEP states and GitHub integration [tools/sep-automation/src/index.ts:1-10]().

### Implementation Tiers
A classification system for SDKs based on their priority and completeness.
*   **Lead Maintainers**: David Soria Parra and Den Delimarsky [MAINTAINERS.md:7-11]().
*   **SDK Maintainers**: Specialized maintainers for Java, Ruby, Swift, Go, C#, Kotlin, Python, TypeScript, Rust, and PHP [MAINTAINERS.md:28-108]().

### Code Entity Mapping: Governance and Extensions

```mermaid
graph TD
    subgraph "Governance Entities"
        LM["Lead Maintainers (MAINTAINERS.md)"] -- "Approve" --> SEP["SEP (Specification Enhancement Process)"]
        SEP -- "Status: Final" --> Spec["MCP Specification (schema/draft/schema.ts)"]
    end

    subgraph "Extension System"
        Spec -- "Capability" --> Ext["Extension (io.modelcontextprotocol/*)"]
        Ext -- "Identifier" --> Tasks["Tasks Extension (SEP-2663)"]
        Ext -- "Identifier" --> Apps["MCP Apps Extension"]
    end

    subgraph "Protocol Implementation"
        Tasks -- "Method" --> TGet["tasks/get"]
        Tasks -- "Method" --> TUpdate["tasks/update"]
        Spec -- "Transport" --> SHTTP["Streamable HTTP"]
    end
```
**Sources:** [MAINTAINERS.md:7-11](), [seps/2663-tasks-extension.md:1-15](), [docs/specification/draft/changelog.mdx:12-28]().

## Schema and Types

### Annotations
Optional metadata for the client to inform UI display, including `audience`, `priority`, and `lastModified` [schema/draft/schema.json:4-26]().

### Implementation
A structure identifying software metadata (`name`, `version`) used in `clientInfo` and `serverInfo` [schema/draft/schema.ts:80-90]().

### Cursor
An opaque token used to represent a position in a paginated result set [schema/draft/schema.ts:168]().

### MetaObject
A dictionary of metadata attached to messages, following specific segment naming rules (Prefix/Name) [schema/draft/schema.ts:35-54]().

**Sources:**
- [schema/draft/schema.ts:1-182]()
- [schema/draft/schema.json:1-150]()
- [docs/specification/draft/changelog.mdx:1-60]()
- [docs/specification/draft/basic/index.mdx:1-152]()
- [seps/2663-tasks-extension.md:1-54]()
- [MAINTAINERS.md:1-215]()