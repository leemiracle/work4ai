<!-- source: DeepWiki mcp.deepwiki.com · repo bytedance/UI-TARS-desktop · page 6 Agent Infrastructure Layer · fetched 2026-10-30 -->

# Agent Infrastructure Layer

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitignore](.gitignore)
- [.lintstagedrc.mjs](.lintstagedrc.mjs)
- [.secretlintignore](.secretlintignore)
- [package.json](package.json)
- [packages/agent-infra/browser-use/src/dom/views.test.ts](packages/agent-infra/browser-use/src/dom/views.test.ts)
- [packages/agent-infra/browser-use/src/dom/views.ts](packages/agent-infra/browser-use/src/dom/views.ts)
- [packages/agent-infra/browser-use/vitest.config.ts](packages/agent-infra/browser-use/vitest.config.ts)
- [packages/agent-infra/mcp-client/CHANGELOG.md](packages/agent-infra/mcp-client/CHANGELOG.md)
- [packages/agent-infra/mcp-client/package.json](packages/agent-infra/mcp-client/package.json)
- [packages/agent-infra/mcp-servers/browser/CHANGELOG.md](packages/agent-infra/mcp-servers/browser/CHANGELOG.md)
- [packages/agent-infra/mcp-servers/browser/package.json](packages/agent-infra/mcp-servers/browser/package.json)
- [packages/agent-infra/mcp-servers/browser/tests/utils/utils.test.ts](packages/agent-infra/mcp-servers/browser/tests/utils/utils.test.ts)
- [packages/agent-infra/mcp-servers/commands/CHANGELOG.md](packages/agent-infra/mcp-servers/commands/CHANGELOG.md)
- [packages/agent-infra/mcp-servers/commands/package.json](packages/agent-infra/mcp-servers/commands/package.json)
- [packages/agent-infra/mcp-servers/filesystem/CHANGELOG.md](packages/agent-infra/mcp-servers/filesystem/CHANGELOG.md)
- [packages/agent-infra/mcp-servers/filesystem/package.json](packages/agent-infra/mcp-servers/filesystem/package.json)
- [packages/agent-infra/mcp-servers/search/CHANGELOG.md](packages/agent-infra/mcp-servers/search/CHANGELOG.md)
- [packages/agent-infra/mcp-servers/search/package.json](packages/agent-infra/mcp-servers/search/package.json)
- [packages/agent-infra/mcp-shared/CHANGELOG.md](packages/agent-infra/mcp-shared/CHANGELOG.md)
- [packages/agent-infra/mcp-shared/package.json](packages/agent-infra/mcp-shared/package.json)
- [packages/common/configs/package.json](packages/common/configs/package.json)
- [pnpm-lock.yaml](pnpm-lock.yaml)

</details>



The Agent Infrastructure Layer provides foundational services that enable agent capabilities through standardized interfaces. This layer consists of three primary subsystems: the Model Context Protocol (MCP) ecosystem for tool integration, browser automation infrastructure for web interaction, and multi-provider search abstraction. These components are implemented as packages under `packages/agent-infra/` and are consumed by higher-level agent implementations in the Multimodal Agent Stack ([Multimodal Agent Stack (Agent TARS / OmniTARS)](#3)) and UI-TARS Desktop application ([UI-TARS Desktop Application](#5)).

For details on how agents consume these infrastructure services, see the MCP Agent Plugin ([MCP Agent Integration](#3.5)) and GUI Agent Plugin ([GUI Agent Plugin and Screenshot Processing](#3.3)). For the Tarko framework that orchestrates agent execution, see [Tarko Framework](#4).

## Infrastructure Package Organization

The `@agent-infra` namespace contains specialized packages organized by capability domain:

| Package | Purpose | Key Exports / Binaries |
|---------|---------|-------------|
| `@agent-infra/mcp-client` | MCP protocol client | `MCPClient`, connection management |
| `@agent-infra/mcp-shared` | Common MCP utilities | Zod schemas, client/server types |
| `mcp-http-server` | HTTP/SSE transport layer | `MCPHTTPServer` integration |
| `@agent-infra/mcp-server-browser` | Browser automation server | `mcp-server-browser` (CLI) |
| `@agent-infra/mcp-server-filesystem` | File operations server | `mcp-server-filesystem` (CLI) |
| `@agent-infra/mcp-server-commands` | Shell execution server | `mcp-server-commands` (CLI) |
| `@agent-infra/mcp-server-search` | Web search server | `mcp-server-search` (CLI) |
| `@agent-infra/browser` | Browser control primitives | `LocalBrowser`, `RemoteBrowser` |
| `@agent-infra/browser-use` | AI-driven browser control | LangChain-based interaction |

**Sources:** [packages/agent-infra/mcp-client/package.json:1-54](), [packages/agent-infra/mcp-servers/browser/package.json:1-17](), [packages/agent-infra/mcp-servers/filesystem/package.json:1-26](), [packages/agent-infra/mcp-servers/commands/package.json:1-18](), [packages/agent-infra/mcp-shared/package.json:1-33]()

## Infrastructure Layer Architecture

```mermaid
graph TB
    subgraph "Agent Layer Consumers"
        ["MCPAgentPlugin"]
        ["GuiAgentPlugin"]
    end
    
    subgraph "MCP Client Layer"
        ["MCPClient"]
        ["@agent-infra/mcp-shared"]
    end
    
    subgraph "MCP Transport Layer"
        ["mcp-http-server"]
        ["@modelcontextprotocol/sdk"]
    end
    
    subgraph "MCP Server Implementations"
        ["@agent-infra/mcp-server-browser"]
        ["@agent-infra/mcp-server-filesystem"]
        ["@agent-infra/mcp-server-commands"]
    end
    
    subgraph "Automation Infrastructure"
        ["@agent-infra/browser"]
        ["@agent-infra/search"]
    end
    
    subgraph "External Resources"
        ["puppeteer-core"]
        ["SearchProviders"]
    end
    
    ["MCPAgentPlugin"] --> ["MCPClient"]
    ["MCPClient"] --> ["@agent-infra/mcp-shared"]
    
    ["MCPClient"] --> ["@agent-infra/mcp-server-browser"]
    ["MCPClient"] --> ["@agent-infra/mcp-server-filesystem"]
    
    ["@agent-infra/mcp-server-browser"] --> ["mcp-http-server"]
    ["@agent-infra/mcp-server-filesystem"] --> ["mcp-http-server"]
    
    ["mcp-http-server"] --> ["@modelcontextprotocol/sdk"]
    ["@agent-infra/mcp-server-browser"] --> ["@agent-infra/browser"]
    
    ["@agent-infra/browser"] --> ["puppeteer-core"]
```

**Diagram: Agent Infrastructure Layer Component Architecture**

This diagram illustrates the layered architecture. The MCP Client connects to multiple MCP servers through a common transport layer. Each server implementation delegates to specialized automation infrastructure (browser control, search) that interfaces with external resources like `puppeteer-core` [packages/agent-infra/mcp-servers/browser/package.json:55-55]().

**Sources:** [packages/agent-infra/mcp-client/package.json:35-42](), [packages/agent-infra/mcp-servers/browser/package.json:49-56](), [packages/agent-infra/mcp-servers/filesystem/package.json:37-40]()

## MCP Protocol Stack

The Model Context Protocol implementation consists of three layers that work together to provide standardized tool integration:

```mermaid
graph TB
    subgraph "Protocol Specification"
        ["@modelcontextprotocol/sdk"]
    end
    
    subgraph "Client Implementation"
        ["MCPClient"]
        ["minimatch Tool Filtering"]
        ["Configurable Timeout"]
    end
    
    subgraph "Server Framework"
        ["ServerCore"]
        ["RequestContext"]
        ["mcp-http-server"]
    end
    
    ["@modelcontextprotocol/sdk"] --> ["MCPClient"]
    ["@modelcontextprotocol/sdk"] --> ["ServerCore"]
    
    ["MCPClient"] --> ["minimatch Tool Filtering"]
    ["MCPClient"] --> ["Configurable Timeout"]
    
    ["ServerCore"] --> ["RequestContext"]
    ["ServerCore"] --> ["mcp-http-server"]
```

**Diagram: MCP Protocol Stack Layers**

The MCP system implements the Model Context Protocol specification using `@modelcontextprotocol/sdk` version `~1.15.1` [packages/agent-infra/mcp-shared/package.json:43-43](). The client layer adds tool discovery and filtering using `minimatch` [packages/agent-infra/mcp-client/package.json:39-39](), along with configurable timeouts [packages/agent-infra/mcp-client/CHANGELOG.md:55-55](). The server framework provides `RequestContext` for session tracking [packages/agent-infra/mcp-servers/browser/package.json:30-33]() and supports high-performance SSE via `mcp-http-server` [packages/agent-infra/mcp-servers/browser/package.json:54-54]().

**Sources:** [packages/agent-infra/mcp-client/package.json:35-42](), [packages/agent-infra/mcp-client/CHANGELOG.md:55-63](), [packages/agent-infra/mcp-servers/browser/package.json:30-34](), [packages/agent-infra/mcp-shared/package.json:43-45]()

## Infrastructure Integration Interfaces

The infrastructure layer exposes primary integration interfaces for higher-level agent components:

### MCP Client Integration

Agents integrate with MCP servers through the `@agent-infra/mcp-client` package. It supports tool and prompt filtering using glob patterns and configurable timeouts for robust operation.

- **Tool Filtering**: Uses `minimatch` patterns to restrict available tools [packages/agent-infra/mcp-client/CHANGELOG.md:62-63]().
- **Timeouts**: Configurable request timeouts for network-resilient tool calls [packages/agent-infra/mcp-client/CHANGELOG.md:55-56]().

**Sources:** [packages/agent-infra/mcp-client/CHANGELOG.md:55-63](), [packages/agent-infra/mcp-client/package.json:35-42]()

### Browser Automation Integration

Direct browser control is provided by `@agent-infra/mcp-server-browser` and its underlying dependencies.

- **Vision Mode**: Supports `browser_vision_screen_capture` using WebP format for optimized performance [packages/agent-infra/mcp-servers/browser/CHANGELOG.md:124-127]().
- **Tooling**: Includes tools for markdown extraction (`browser_get_markdown`), keyboard interaction, and form filling [packages/agent-infra/mcp-servers/browser/CHANGELOG.md:79-81]().
- **Puppeteer Integration**: Built on `puppeteer-core` version 24.7.2 for reliable element selection and page manipulation [packages/agent-infra/mcp-servers/browser/package.json:55-55]().

**Sources:** [packages/agent-infra/mcp-servers/browser/package.json:49-56](), [packages/agent-infra/mcp-servers/browser/CHANGELOG.md:31-33]()

### Filesystem and Command Execution

- **Filesystem MCP**: Provides controlled access to the local filesystem, enabling agents to read, write, and list files within specific directories [packages/agent-infra/mcp-servers/filesystem/package.json:4-5]().
- **Commands MCP**: Allows agents to run arbitrary shell commands, supporting features like custom working directories (CWD) [packages/agent-infra/mcp-servers/commands/CHANGELOG.md:39-40]().

**Sources:** [packages/agent-infra/mcp-servers/filesystem/package.json:1-10](), [packages/agent-infra/mcp-servers/commands/package.json:1-10]()

## Subsystem Documentation

The infrastructure layer is documented in detail across three subsections:

- **[Model Context Protocol (MCP) System](#6.1)**: Overview of the MCP integration, client-server architecture, and tool/prompt/resource access. For details, see [Model Context Protocol (MCP) System](#6.1).
- **[Browser Automation Infrastructure](#6.2)**: Document the browser automation stack: `@agent-infra/browser`, puppeteer integration, and browser-use for AI-driven control. For details, see [Browser Automation Infrastructure](#6.2).
- **[Search System Architecture](#6.3)**: Detail the unified search system, SearchProvider enum, SearchClient, and provider implementations (Bing, Tavily, DuckDuckGo, etc.). For details, see [Search System Architecture](#6.3).

---

