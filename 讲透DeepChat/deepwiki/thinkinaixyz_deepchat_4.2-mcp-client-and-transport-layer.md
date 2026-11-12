> 来源: [https://deepwiki.com/thinkinaixyz/deepchat/4.2-mcp-client-and-transport-layer](https://deepwiki.com/thinkinaixyz/deepchat/4.2-mcp-client-and-transport-layer)（Wayback 快照 2026-03-06）
> DeepWiki deepchat/4.2-mcp-client-and-transport-layer

# MCP Client and Transport Layer

  Relevant source files 
 - [electron.vite.config.ts](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/electron.vite.config.ts)
 - [package.json](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/package.json)
 - [src/main/presenter/mcpPresenter/index.ts](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/index.ts)
 - [src/main/presenter/mcpPresenter/mcpClient.ts](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/mcpClient.ts)
 - [src/main/presenter/mcpPresenter/serverManager.ts](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/serverManager.ts)
 - [src/main/presenter/mcpPresenter/toolManager.ts](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/toolManager.ts)
 - [src/renderer/src/components/markdown/MarkdownRenderer.vue](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/markdown/MarkdownRenderer.vue)
 - [src/renderer/src/composables/useArtifactCodeEditor.ts](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/composables/useArtifactCodeEditor.ts)
 - [src/renderer/src/main.ts](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/main.ts)
 - [src/renderer/src/stores/mcp.ts](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/mcp.ts)
 
  
## Purpose and Scope

 This document details the `McpClient` class and the transport layer that forms the foundation of DeepChat's MCP integration. The `McpClient` wraps the `@modelcontextprotocol/sdk` Client and manages four distinct transport types for connecting to MCP servers. This layer handles connection lifecycle, notification processing, sampling requests, session recovery, and transport-specific configuration.

 For information about server lifecycle management and tool aggregation across multiple clients, see [Server Lifecycle and Tool Management](https://deepwiki.com/thinkinaixyz/deepchat/4.3-server-lifecycle-and-tool-management). For details on the presenter layer that orchestrates multiple clients, see [MCP System Architecture](https://deepwiki.com/thinkinaixyz/deepchat/4.1-mcp-system-architecture).

 
---

 
## McpClient Class Architecture

 The `McpClient` class serves as a wrapper around the MCP SDK's `Client` class, providing connection management, caching, and error recovery capabilities for a single MCP server.

 
```

```

 **Sources**: [src/main/presenter/mcpPresenter/mcpClient.ts115-145](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/mcpClient.ts#L115-L145)

 
### Key Properties

 
| Property | Type | Purpose |
|---|---|---|
| client | Client \| null | MCP SDK client instance, null when disconnected |
| transport | Transport \| null | Active transport instance (Stdio/SSE/HTTP/InMemory) |
| serverName | string | Unique identifier for this server |
| serverConfig | Record<string, unknown> | Server configuration object (type, command, args, env, etc.) |
| isConnected | boolean | Connection status flag |
| connectionTimeout | NodeJS.Timeout \| null | 5-minute connection timeout handle |
| cachedTools | Tool[] \| null | Cached tool definitions, invalidated on ToolListChangedNotification |
| cachedPrompts | PromptListEntry[] \| null | Cached prompt list, invalidated on PromptListChangedNotification |
| cachedResources | ResourceListEntry[] \| null | Cached resource list, invalidated on ResourceListChangedNotification |
| isRecovering | boolean | Flag indicating active session recovery attempt |
| hasRestarted | boolean | Flag tracking whether server has been restarted once for session errors |

 **Sources**: [src/main/presenter/mcpPresenter/mcpClient.ts116-133](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/mcpClient.ts#L116-L133)

 
---

 
## Transport Layer Architecture

 DeepChat supports four transport types for MCP communication, each instantiated based on the `serverConfig.type` field during connection.

 
### Transport Type Selection

 
```

```

 **Sources**: [src/main/presenter/mcpPresenter/mcpClient.ts168-372](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/mcpClient.ts#L168-L372)

 
---

 
## Transport Implementations

 
### 1. Stdio Transport

 Spawns a child process for Node.js-based MCP servers using `npx` or direct Node.js execution.

 **Configuration Flow**:

 
```

```

 **Environment Variable Management**:

 The Stdio transport uses a whitelist approach for Node.js/UV commands and preserves all environment variables for other commands:

 
| Command Type | Environment Handling | Variables Included |
|---|---|---|
| Node.js/UV commands (node, npm, npx, uv, uvx) | Whitelist only | PATH, npm_config_*, NPM_CONFIG_* |
| Other commands | Full passthrough | All process.env variables |
| Custom env from serverConfig.env | Always merged | User-defined variables override |
| Runtime paths | Always prepended to PATH | UV runtime, Node runtime from bundled runtimes |

 **Sources**: [src/main/presenter/mcpPresenter/mcpClient.ts175-354](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/mcpClient.ts#L175-L354)

 **Key Implementation Details**:

 
 - **Path Expansion**: `RuntimeHelper.expandPath()` resolves `~` and environment variables in command/args [mcpClient.ts184-185](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/mcpClient.ts#L184-L185)
 - **Runtime Injection**: `RuntimeHelper.processCommandWithArgs()` injects bundled UV/Node runtimes [mcpClient.ts210-212](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/mcpClient.ts#L210-L212)
 - **PATH Construction**: System PATH + default paths + runtime paths (UV, Node) [mcpClient.ts238-267](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/mcpClient.ts#L238-L267)
 - **Registry Configuration**: `npm_config_registry` set to tested npm registry, `UV_DEFAULT_INDEX` for UV registry [mcpClient.ts336-343](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/mcpClient.ts#L336-L343)
 - **Stderr Piping**: Stderr is piped to console for debugging [mcpClient.ts350-354](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/mcpClient.ts#L350-L354)
 
 
---

 
### 2. SSE Transport

 Connects to remote MCP servers via Server-Sent Events for streaming communication.

 **Configuration**:

 
```

```

 **Authentication Handling**:

 
```

```

 The `Authorization` header is removed from `customHeaders` and converted to a `SimpleOAuthProvider` instance that the SDK uses for authentication [mcpClient.ts158-166](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/mcpClient.ts#L158-L166)

 **Sources**: [src/main/presenter/mcpPresenter/mcpClient.ts47-62](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/mcpClient.ts#L47-L62) [mcpClient.ts355-360](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/mcpClient.ts#L355-L360)

 
---

 
### 3. HTTP Transport (Streamable HTTP)

 Uses `StreamableHTTPClientTransport` for HTTP-based MCP servers with streaming support and session management.

 **Configuration**:

 
```

```

 **Session Error Detection**:

 The HTTP transport includes sophisticated session error detection to handle connection issues:

 
```

```

 **Session Error Patterns** (case-insensitive matching):

 
 - `"no valid session"`
 - `"session expired"`
 - `"session not found"`
 - `"invalid session"`
 - `"session id"`
 - `"mcp-session-id"`
 - HTTP errors (`"http 400"`, `"http 404"`) when message contains `"posting"` or `"endpoint"`
 
 **Sources**: [src/main/presenter/mcpPresenter/mcpClient.ts81-112](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/mcpClient.ts#L81-L112) [mcpClient.ts854-904](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/mcpClient.ts#L854-L904) [mcpClient.ts361-369](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/mcpClient.ts#L361-L369)

 
---

 
### 4. InMemory Transport

 Creates a linked pair of transports for built-in MCP services that run in-process without external server processes.

 
```

```

 **Server Instantiation**:

 The `getInMemoryServer()` factory function resolves the server name to a specific built-in server implementation:

 
| Server Name | Type | Purpose |
|---|---|---|
| deepchat-inmemory/artifacts-server | Artifacts | Create/display rich UI artifacts |
| deepchat-inmemory/bosearch-server | Search | BoSearch web search integration |
| deepchat-inmemory/brave-search-server | Search | Brave Search API integration |
| deepchat-inmemory/dify-knowledge-base-server | Knowledge | Dify RAG knowledge base |
| deepchat-inmemory/ragflow-knowledge-base-server | Knowledge | RAGFlow RAG knowledge base |
| deepchat-inmemory/knowledge-base-server | Knowledge | Built-in DuckDB vector search |
| deepchat-inmemory/powerpack-server | Tools | Code execution, web browsing, time |
| deepchat-inmemory/deep-research-server | Research | Multi-step research workflows |
| deepchat-inmemory/meeting-server | Meeting | Meeting transcription and analysis |
| deepchat-inmemory/custom-prompts-server | Prompts | User-defined prompt templates |
| deepchat-inmemory/apple-server | System | macOS system integration (AppleScript) |

 **Sources**: [src/main/presenter/mcpPresenter/mcpClient.ts168-174](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/mcpClient.ts#L168-L174) [mcpClient.ts23](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/mcpClient.ts#L23-L23)

 
---

 
## Connection Lifecycle

 
### Connection Sequence

 
```

```

 **Sources**: [src/main/presenter/mcpPresenter/mcpClient.ts148-453](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/mcpClient.ts#L148-L453)

 
### Disconnection and Cleanup

 
```

```

 **Sources**: [src/main/presenter/mcpPresenter/mcpClient.ts456-468](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/mcpClient.ts#L456-L468) [mcpClient.ts470-496](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/mcpClient.ts#L470-L496) [mcpClient.ts906-922](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/mcpClient.ts#L906-L922)

 
---

 
## Notification Handling System

 The `McpClient` registers handlers for five MCP SDK notification types to maintain cache consistency and provide real-time updates.

 
### Notification Handler Registration

 
```

```

 **Sources**: [src/main/presenter/mcpPresenter/mcpClient.ts499-556](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/mcpClient.ts#L499-L556)

 **Handler Behavior**:

 All handlers follow a **proactive cache invalidation + refresh** pattern:

 
 - **Clear Cache**: Set the relevant cache to `null` (e.g., `this.cachedTools = null`)
 - **Actively Refresh**: Call the corresponding list method (e.g., `await this.listTools()`)
 - **Error Tolerance**: If refresh fails, log warning but don't throw (ensures notification handler doesn't block)
 
 This ensures that when an MCP server notifies of changes, the client immediately fetches fresh data rather than waiting for the next explicit request.

 
---

 
## Caching Strategy

 Each list operation (`listTools`, `listPrompts`, `listResources`) implements a cache-first strategy:

 
```

```

 **Cache Invalidation Triggers**:

 
| Event | Cache Cleared | Refresh Behavior |
|---|---|---|
| ToolListChangedNotification | cachedTools = null | Immediate listTools() call |
| PromptListChangedNotification | cachedPrompts = null | Immediate listPrompts() call |
| ResourceListChangedNotification | cachedResources = null | Immediate listResources() call |
| ResourceUpdatedNotification | cachedResources = null | Immediate listResources() call |
| Tool call returns error | cachedTools = null | No automatic refresh |
| Session error detected | All caches cleared | Refresh after reconnection |

 **Sources**: [src/main/presenter/mcpPresenter/mcpClient.ts968-1014](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/mcpClient.ts#L968-L1014) [mcpClient.ts1017-1086](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/mcpClient.ts#L1017-L1086) [mcpClient.ts1090-1142](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/mcpClient.ts#L1090-L1142)

 
---

 
## Sampling System Integration

 The `McpClient` acts as a sampling provider, allowing MCP servers to request LLM completions from DeepChat.

 
### Sampling Request Flow

 
```

```

 **Sources**: [src/main/presenter/mcpPresenter/mcpClient.ts388-390](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/mcpClient.ts#L388-L390) [mcpClient.ts558-641](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/mcpClient.ts#L558-L641)

 
### Image Validation for Sampling

 The sampling system enforces strict validation for image content:

 **Allowed MIME Types**:

 
```

```

 **Validation Steps** in `sanitizeSamplingImageData()`:

 
 - **Type Check**: Ensure data is a string
 - **Whitespace Removal**: Strip all whitespace from base64 string
 - **Format Validation**: Check length divisible by 4, valid base64 characters only
 - **Decoding Test**: Attempt to decode to Buffer
 - **Re-encoding Verification**: Re-encode and compare to ensure data integrity
 
 If any validation fails, throws `McpError(ErrorCode.InvalidParams, 'Invalid sampling image payload received')`.

 **Sources**: [src/main/presenter/mcpPresenter/mcpClient.ts38-43](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/mcpClient.ts#L38-L43) [mcpClient.ts691-771](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/mcpClient.ts#L691-L771)

 
---

 
## Session Management and Error Recovery

 The HTTP transport includes a sophisticated session error recovery system that automatically restarts connections on transient session failures.

 
### Error Recovery State Machine

 
```

```

 **Sources**: [src/main/presenter/mcpPresenter/mcpClient.ts854-904](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/mcpClient.ts#L854-L904)

 
### Session Error Detection Logic

 The `isSessionError()` function uses pattern matching to identify session-related failures:

 
```

```

 **Recovery Behavior**:

 
| Attempt | Action | Result |
|---|---|---|
| First error | cleanupResources() + hasRestarted=true | Next connect() auto-reconnects |
| Second error | stopService() + event notification | Server marked as stopped, manual restart required |

 **Sources**: [src/main/presenter/mcpPresenter/mcpClient.ts82-112](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/mcpClient.ts#L82-L112) [mcpClient.ts854-893](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/mcpClient.ts#L854-L893)

 
---

 
## Tool Call Integration

 Tool calls flow through the client with automatic reconnection and cache invalidation:

 
```

```

 **Sources**: [src/main/presenter/mcpPresenter/mcpClient.ts925-965](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/mcpClient.ts#L925-L965)

 
---

 
## Configuration and Environment Setup

 
### Runtime Path Resolution

 The `RuntimeHelper` singleton manages bundled runtime paths and command injection:

 
```

```

 **Runtime Path Priority** (prepended to PATH in order):

 
 - **Node Runtime**: `<app>/runtime/node/bin` (non-Windows) or `<app>/runtime/node` (Windows)
 - **UV Runtime**: `<app>/runtime/uv`
 - **Default System Paths**: `/usr/local/bin`, `/usr/bin`, `/bin`, etc.
 - **Existing PATH**: From `process.env.PATH`
 
 **Sources**: [src/main/presenter/mcpPresenter/mcpClient.ts177-314](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/mcpClient.ts#L177-L314)

 
### Environment Variable Whitelist (Node.js/UV Commands)

 For security, Node.js and UV commands only receive a whitelist of environment variables:

 
```

```

 All other commands receive the full `process.env` to ensure compatibility with tools that expect standard environment variables.

 **Sources**: [src/main/presenter/mcpPresenter/mcpClient.ts189-234](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/mcpClient.ts#L189-L234) [mcpClient.ts269-314](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/mcpClient.ts#L269-L314)

 
---

 
## Summary

 The `McpClient` class and transport layer provide:

 
 - **Four Transport Types**: Stdio (process), SSE (streaming), HTTP (streamable HTTP with session recovery), InMemory (built-in services)
 - **Connection Management**: 5-minute timeout, automatic reconnection on session errors, status event broadcasting
 - **Caching Strategy**: Cache-first reads with notification-driven invalidation and proactive refresh
 - **Sampling Integration**: MCP servers can request LLM completions with image validation and approval flow
 - **Session Recovery**: Automatic restart on first session error, manual intervention on persistent failures
 - **Runtime Management**: Bundled UV/Node runtime injection, environment variable handling, registry configuration
 - **Notification System**: Real-time cache updates on tool/prompt/resource changes from MCP servers
 
 This foundation enables the higher-level `ServerManager` and `ToolManager` to orchestrate multiple clients while maintaining consistent state and providing robust error recovery.
