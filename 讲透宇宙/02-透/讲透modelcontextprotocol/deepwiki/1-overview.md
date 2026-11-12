<!-- source: DeepWiki mcp.deepwiki.com · repo modelcontextprotocol/modelcontextprotocol · page 1 Overview · fetched 2026-10-21 -->

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

