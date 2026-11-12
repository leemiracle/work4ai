<!-- source: DeepWiki mcp.deepwiki.com · repo Xquik-dev/x-twitter-scraper · page 2 MCP Server Integration · fetched 2026-10-26 -->

# MCP Server Integration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.mcp.json](.mcp.json)
- [server.json](server.json)
- [smithery.yaml](smithery.yaml)

</details>



The Model Context Protocol (MCP) server acts as a standardized bridge between AI agents (such as Claude Desktop, Cursor, or Windsurf) and the Xquik REST API. This integration allows Large Language Models (LLMs) to interact with X (Twitter) data and actions through a unified interface, abstracting the complexities of 120+ REST endpoints into two primary tools.

The server is identified as `com.xquik/mcp` and follows the `2025-12-11` MCP schema specification [server.json:1-3](). It facilitates real-time data access and write actions across a vast X data platform [server.json:4-4]().

### Architectural Overview

The Xquik MCP implementation utilizes a `streamable-http` transport type, allowing AI clients to connect to a remote endpoint rather than running a local binary [server.json:12-12](). This architecture ensures that the AI agent always has access to the latest API capabilities and security updates without requiring local software updates.

#### AI-to-Code Mapping: The MCP Bridge

The following diagram illustrates how natural language prompts from a user are translated into API executions via the MCP server tools.

**Diagram: Natural Language to API Execution Flow**
```mermaid
graph TD
    subgraph "NaturalLanguageSpace"
        [UserPrompt] -- "'Find recent tweets about AI'" --> [Agent]
    end

    subgraph "MCPServerLayer"
        direction TB
        [ToolExplore] -- "explore" --> [EndpointCatalog]
        [ToolXquik] -- "xquik" --> [SandboxedJS]
        [ServerJson] -- "server.json" --> [McpMetadata]
    end

    subgraph "XquikRestApi"
        [ApiV1] -- "https://xquik.com/api/v1" --> [Endpoints]
        [SearchEndpoint] -- "/search/tweets" --> [XData]
    end

    [Agent] -->|"1. Agent selects tool"| [ToolExplore]
    [ToolExplore] -->|"2. Agent finds endpoint"| [ToolXquik]
    [ToolXquik] -->|"3. HTTP POST (x-api-key)"| [ApiV1]
    [ApiV1] --> [SearchEndpoint]
```
**Sources:** [server.json:1-13](), [.mcp.json:1-9]()

### Core Components

The integration consists of two primary tools that the AI agent uses to navigate and execute X operations:

1.  **`explore`**: A discovery tool that allows the agent to search an in-memory catalog of available API endpoints. It helps the agent understand which parameters are required for specific tasks (e.g., finding the correct endpoint for "follower extraction").
2.  **`xquik`**: The execution engine. It runs sandboxed JavaScript arrow functions provided by the agent to perform the actual HTTP requests to the Xquik API. This tool handles authentication injection using the `x-api-key` [server.json:14-17]().

| Feature | Specification |
| :--- | :--- |
| **Server Name** | `com.xquik/mcp` [server.json:3-3]() |
| **Transport Type** | `streamable-http` [server.json:12-12]() |
| **Endpoint URL** | `https://xquik.com/mcp` [server.json:13-13]() |
| **Auth Mechanism** | Header-based `x-api-key` [.mcp.json:5-7]() |
| **Required Variable** | `XQUIK_API_KEY` [server.json:22-24]() |

### System Connectivity

The MCP server connects the AI's reasoning capabilities to the functional domains of the Xquik platform. The following diagram maps the high-level system names to the underlying configuration and registry files.

**Diagram: System Entity Mapping**
```mermaid
graph LR
    subgraph "AiAgentEnvironment"
        [Claude] -- "Claude Desktop / Cursor" --> [McpConfig]
        [McpConfig] -- ".mcp.json" --> [Headers]
    end

    subgraph "RegistryAndDiscovery"
        [ServerSpec] -- "server.json" --> [RemoteConfig]
        [Smithery] -- "smithery.yaml" --> [StartCommand]
    end

    subgraph "XquikPlatform"
        [McpRemote] -- "https://xquik.com/mcp" --> [RestBridge]
    end

    [Claude] --> [McpConfig]
    [McpConfig] -->|"x-api-key injection"| [McpRemote]
    [ServerSpec] -->|"Defines streamable-http"| [McpRemote]
    [Smithery] -->|"Configures http type"| [McpRemote]
```
**Sources:** [server.json:1-31](), [.mcp.json:1-9](), [smithery.yaml:1-11]()

### Related Child Pages

To implement or use this integration, refer to the following detailed guides:

*   **[MCP Setup & Client Configuration](#2.1)**
    Covers the specific configuration strings and environment variables needed for Claude Desktop, Cursor, VS Code, Windsurf, and ChatGPT. Includes details on the `XQUIK_API_KEY` variable and `smithery.yaml` configuration [server.json:21-26](), [smithery.yaml:1-11]().
*   **[MCP Tools: `explore` and `xquik`](#2.2)**
    Provides a deep dive into tool usage, including the 12 API categories, how to handle asynchronous extractions, and the security model for the sandboxed `xquik` execution environment.

**Sources:** [server.json:4-10](), [.mcp.json:2-8](), [smithery.yaml:1-11]()

---

