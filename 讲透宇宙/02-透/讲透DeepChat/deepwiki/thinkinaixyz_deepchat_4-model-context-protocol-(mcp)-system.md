> 来源: [https://deepwiki.com/thinkinaixyz/deepchat/4-model-context-protocol-(mcp)-system](https://deepwiki.com/thinkinaixyz/deepchat/4-model-context-protocol-(mcp)-system)（Wayback 快照 2026-03-06）
> DeepWiki deepchat/4-model-context-protocol-(mcp)-system

# Model Context Protocol (MCP) System

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

 The Model Context Protocol (MCP) System is DeepChat's primary mechanism for extending agent capabilities through tool calling. This system implements the MCP specification, enabling DeepChat to connect to external MCP servers (via stdio, SSE, or HTTP) and built-in in-memory services. The MCP system provides tool discovery, execution, permission management, and LLM sampling capabilities.

 This document covers:

 
 - MCP client architecture and transport mechanisms
 - Server lifecycle management and NPM registry optimization
 - Tool aggregation, conflict resolution, and permission checking
 - Sampling feature (where MCP servers request LLM completions)
 - Configuration storage and UI integration
 
 For LLM provider integration that consumes MCP tools, see [LLM Provider Integration](https://deepwiki.com/thinkinaixyz/deepchat/5-llm-provider-integration). For built-in MCP server implementations, see [Built-in MCP Servers](https://deepwiki.com/thinkinaixyz/deepchat/4.6-built-in-mcp-servers).

 **Sources:** [src/main/presenter/mcpPresenter/index.ts1-112](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/index.ts#L1-L112) [package.json72](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/package.json#L72-L72)

 
---

 
## System Architecture Overview

 The MCP system implements a three-tier architecture separating concerns across presenter orchestration, server/tool management, and client connections.

 
### Architecture Layers

 
```

```

 **Sources:** [src/main/presenter/mcpPresenter/index.ts83-112](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/index.ts#L83-L112) [src/main/presenter/mcpPresenter/serverManager.ts16-25](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/serverManager.ts#L16-L25) [src/main/presenter/mcpPresenter/toolManager.ts18-32](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/toolManager.ts#L18-L32)

 
### Component Responsibilities

 
| Component | File | Primary Responsibilities |
|---|---|---|
| McpPresenter | src/main/presenter/mcpPresenter/index.ts | Orchestrates MCP system initialization, delegates to managers, handles IPC calls from renderer, manages sampling requests |
| ServerManager | src/main/presenter/mcpPresenter/serverManager.ts | Server lifecycle (start/stop), NPM registry speed testing and caching, client instance management |
| ToolManager | src/main/presenter/mcpPresenter/toolManager.ts | Tool list aggregation, name conflict resolution, permission checking, tool execution delegation |
| McpClient | src/main/presenter/mcpPresenter/mcpClient.ts | Single server connection, transport management, notification handlers, tool/prompt/resource listing |
| useMcpStore | src/renderer/src/stores/mcp.ts | Renderer state management, query caching with Pinia Colada, UI state synchronization |

 **Sources:** [src/main/presenter/mcpPresenter/index.ts83-112](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/index.ts#L83-L112) [src/main/presenter/mcpPresenter/serverManager.ts16-43](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/serverManager.ts#L16-L43) [src/main/presenter/mcpPresenter/toolManager.ts18-32](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/toolManager.ts#L18-L32) [src/main/presenter/mcpPresenter/mcpClient.ts115-145](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/mcpClient.ts#L115-L145) [src/renderer/src/stores/mcp.ts25-40](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/mcp.ts#L25-L40)

 
---

 
## MCP Client and Transport Layer

 Each `McpClient` instance represents a connection to a single MCP server. The client supports four transport types, selected based on server configuration.

 
### Transport Types and Configuration

 
```

```

 **Sources:** [src/main/presenter/mcpPresenter/mcpClient.ts148-373](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/mcpClient.ts#L148-L373)

 
### Transport Implementation Details

 
#### Stdio Transport Configuration

 The stdio transport spawns a child process and communicates via standard input/output. The system includes sophisticated environment variable management:

 
| Environment Handling | Description |
|---|---|
| Runtime path injection | Prepends bundled Node.js and UV runtime paths to PATH |
| Whitelist filtering (Node/UV) | For Node/npm/npx/uv/uvx commands, only passes whitelisted env vars |
| Full passthrough (other) | For other commands, passes all system env vars |
| Custom env merging | Merges user-provided env vars with processed environment |
| NPM registry injection | Sets npm_config_registry if configured |
| UV registry injection | Sets UV_DEFAULT_INDEX and PIP_INDEX_URL for Python servers |

 **Sources:** [src/main/presenter/mcpPresenter/mcpClient.ts175-354](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/mcpClient.ts#L175-L354)

 
#### SSE and HTTP Transports

 Remote transports support OAuth Bearer token authentication through `SimpleOAuthProvider`:

 
```

```

 Custom headers are processed to extract `Authorization` headers for the auth provider, then removed from the headers object to avoid duplication.

 **Sources:** [src/main/presenter/mcpPresenter/mcpClient.ts47-62](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/mcpClient.ts#L47-L62) [src/main/presenter/mcpPresenter/mcpClient.ts158-169](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/mcpClient.ts#L158-L169) [src/main/presenter/mcpPresenter/mcpClient.ts355-370](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/mcpClient.ts#L355-L370)

 
#### InMemory Transport

 In-memory servers use `InMemoryTransport.createLinkedPair()` which creates bidirectional communication channels without IPC overhead. The server instance is obtained from `getInMemoryServer()` which maps server names to built-in implementations.

 **Sources:** [src/main/presenter/mcpPresenter/mcpClient.ts168-174](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/mcpClient.ts#L168-L174)

 
### Notification Handlers

 `McpClient` registers handlers for five MCP notification types:

 
| Notification | Schema | Handler Behavior |
|---|---|---|
| Tool list changed | ToolListChangedNotificationSchema | Clears cachedTools, actively refreshes via listTools() |
| Prompt list changed | PromptListChangedNotificationSchema | Clears cachedPrompts, actively refreshes via listPrompts() |
| Resource list changed | ResourceListChangedNotificationSchema | Clears cachedResources, actively refreshes via listResources() |
| Resource updated | ResourceUpdatedNotificationSchema | Clears cachedResources, actively refreshes via listResources() |
| Logging message | LoggingMessageNotificationSchema | Logs message to console |

 **Sources:** [src/main/presenter/mcpPresenter/mcpClient.ts498-556](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/mcpClient.ts#L498-L556)

 
### Client Lifecycle and Session Management

 The client implements session error detection and recovery:

 
```

```

 **Sources:** [src/main/presenter/mcpPresenter/mcpClient.ts82-112](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/mcpClient.ts#L82-L112) [src/main/presenter/mcpPresenter/mcpClient.ts854-904](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/mcpClient.ts#L854-L904)

 
---

 
## Server Lifecycle Management

 `ServerManager` handles MCP server startup, shutdown, and NPM registry optimization.

 
### NPM Registry Speed Testing

 To optimize package installation for stdio-based MCP servers, the system tests multiple NPM registries and caches the fastest:

 
```

```

 **Sources:** [src/main/presenter/mcpPresenter/serverManager.ts44-147](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/serverManager.ts#L44-L147)

 
### Server Start Sequence

 
```

```

 **Sources:** [src/main/presenter/mcpPresenter/serverManager.ts235-280](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/serverManager.ts#L235-L280)

 The connection timeout is set to 5 minutes to accommodate slow server initialization or package installation.

 **Sources:** [src/main/presenter/mcpPresenter/mcpClient.ts393-432](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/mcpClient.ts#L393-L432)

 
### Background Registry Updates

 The system schedules background NPM registry updates after initialization:

 
 - Initial registry detection happens during `McpPresenter` initialization
 - Background update scheduled after 5 seconds via `scheduleBackgroundRegistryUpdate()`
 - Update only runs if cache expired (`isNpmRegistryCacheValid()` returns false)
 - Registry cache has a TTL managed by `ConfigPresenter`
 
 **Sources:** [src/main/presenter/mcpPresenter/index.ts181-182](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/index.ts#L181-L182) [src/main/presenter/mcpPresenter/index.ts262-270](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/index.ts#L262-L270) [src/main/presenter/mcpPresenter/serverManager.ts159-172](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/serverManager.ts#L159-L172)

 
---

 
## Tool Management and Execution

 `ToolManager` aggregates tools from all running clients, resolves name conflicts, and enforces permissions.

 
### Tool Aggregation with Conflict Resolution

 When multiple servers expose tools with the same name, the system renames conflicting tools by prefixing the server name:

 
```

```

 **Sources:** [src/main/presenter/mcpPresenter/toolManager.ts49-224](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/toolManager.ts#L49-L224)

 
### Tool Name Mapping Structure

 The `toolNameToTargetMap` maintains bidirectional mapping for tool execution:

 
| Map Entry | Key | Value |
|---|---|---|
| Final name → Client + Original | finalName: string | { client: McpClient, originalName: string } |

 This enables:

 
 - Tool execution to route to correct client using original name
 - Enabled tool filtering (checking both final and original names)
 - Reverse lookup for permission checks
 
 **Sources:** [src/main/presenter/mcpPresenter/toolManager.ts21-23](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/toolManager.ts#L21-L23) [src/main/presenter/mcpPresenter/toolManager.ts192-194](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/toolManager.ts#L192-L194)

 
### Tool Execution Flow

 
```

```

 **Sources:** [src/main/presenter/mcpPresenter/toolManager.ts384-567](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/toolManager.ts#L384-L567)

 
---

 
## Permission System

 The MCP permission system implements a three-level hierarchy (all/write/read) with both persistent and session-scoped permissions.

 
### Permission Levels and Determination

 
```

```

 **Sources:** [src/main/presenter/mcpPresenter/toolManager.ts226-271](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/toolManager.ts#L226-L271)

 
### Permission Checking Hierarchy

 Permission checks follow a priority order:

 
```

```

 **Sources:** [src/main/presenter/mcpPresenter/toolManager.ts273-315](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/toolManager.ts#L273-L315)

 
### Session Permission Management

 Session permissions are stored in memory and scoped to conversations:

 
| Data Structure | Type | Scope |
|---|---|---|
| sessionPermissions | Map<string, Set<string>> | Per-conversation temporary permissions |
| Map key | conversationId | Identifies conversation |
| Set entries | "serverName:permissionType" | Permission grants for this conversation |

 **Hierarchy Rules:**

 
 - `all` permission covers `write` and `read`
 - `write` permission covers `read`
 - `read` permission only covers read operations
 
 **Sources:** [src/main/presenter/mcpPresenter/toolManager.ts24-26](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/toolManager.ts#L24-L26) [src/main/presenter/mcpPresenter/toolManager.ts619-686](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/toolManager.ts#L619-L686)

 
### Pre-check Permission (Without Execution)

 The system supports checking permissions before tool execution via `preCheckToolPermission()`:

 
```

```

 This enables UI to show permission dialogs before executing tools, improving UX by avoiding failed executions.

 **Sources:** [src/main/presenter/mcpPresenter/toolManager.ts317-382](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/toolManager.ts#L317-L382) [src/main/presenter/mcpPresenter/index.ts589-610](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/index.ts#L589-L610)

 
### ACP Agent Access Control

 For ACP (Agent Client Protocol) agents, an additional access control layer restricts which MCP servers an agent can use:

 
 - Check if chat mode is `'acp agent'`
 - Resolve `agentId` from conversation settings
 - Load `agentMcpSelections` from config
 - Deny if server not in allowed list
 
 **Sources:** [src/main/presenter/mcpPresenter/toolManager.ts422-448](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/toolManager.ts#L422-L448)

 
---

 
## Sampling System

 MCP servers can request LLM completions from the DeepChat client via the sampling feature.

 
### Sampling Request Flow

 
```

```

 **Sources:** [src/main/presenter/mcpPresenter/mcpClient.ts558-641](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/mcpClient.ts#L558-L641) [src/main/presenter/mcpPresenter/index.ts612-664](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/index.ts#L612-L664)

 
### Image Validation for Sampling

 Sampling requests support images with strict validation:

 
| Validation Step | Implementation |
|---|---|
| Allowed MIME types | image/png, image/jpeg, image/gif, image/webp |
| Base64 validation | Check valid base64 charset, proper padding, length divisible by 4 |
| Re-encoding check | Decode to Buffer, re-encode, compare with original |
| Data URL generation | data:{mimeType};base64,{sanitizedData} |

 **Sources:** [src/main/presenter/mcpPresenter/mcpClient.ts38-43](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/mcpClient.ts#L38-L43) [src/main/presenter/mcpPresenter/mcpClient.ts691-771](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/mcpClient.ts#L691-L771)

 
### Model Preferences Normalization

 Sampling requests can include model preferences for intelligent model selection:

 
```

```

 **Sources:** [src/main/presenter/mcpPresenter/mcpClient.ts773-808](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/mcpClient.ts#L773-L808)

 
---

 
## Configuration Management

 MCP configuration is managed through `McpConfHelper` and stored in ElectronStore.

 
### Configuration Schema

 
```

```

 **Sources:** [src/renderer/src/stores/mcp.ts35-40](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/mcp.ts#L35-L40)

 
### Default Server Management

 The system supports marking up to 30 servers as "default" servers that auto-start when MCP is enabled:

 
| Operation | Method | Behavior |
|---|---|---|
| Add default | addMcpDefaultServer(name) | Adds to defaultServers array if under limit |
| Remove default | removeMcpDefaultServer(name) | Removes from defaultServers array |
| Toggle default | toggleMcpDefaultServer(name) | Adds or removes based on current state |
| Check limit | hasMaxDefaultServers computed | Returns true if 30+ servers |

 **Sources:** [src/renderer/src/stores/mcp.ts351-356](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/mcp.ts#L351-L356) [src/renderer/src/stores/mcp.ts602-622](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/mcp.ts#L602-L622)

 
### Auto-start Sequence

 When MCP is enabled:

 
 - `setMcpEnabled(true)` called
 - Config updated optimistically in renderer
 - `startDefaultServers()` invoked
 - For each server in `defaultServers`: 
 - Check if already running via `isServerRunning(name)`
 - If not running, call `startServer(name)`
 - `updateAllServerStatuses()` refreshes status map
 - Queries refreshed after 300ms delay
 - Second refresh after 1000ms to ensure all tools loaded
 
 **Sources:** [src/renderer/src/stores/mcp.ts438-450](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/mcp.ts#L438-L450) [src/renderer/src/stores/mcp.ts452-505](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/mcp.ts#L452-L505)

 
---

 
## UI Integration

 The renderer integrates with the MCP system through `useMcpStore` which uses Pinia Colada for query management.

 
### Query Architecture

 
```

```

 **Sources:** [src/renderer/src/stores/mcp.ts71-155](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/mcp.ts#L71-L155)

 
### Query Invalidation Strategy

 Mutations automatically invalidate related queries using `invalidateQueries` option:

 
| Mutation | Invalidates |
|---|---|
| addMcpServer | ['mcp', 'config'], ['mcp', 'tools'], ['mcp', 'clients'], ['mcp', 'resources'] |
| updateMcpServer | Same as addMcpServer |
| removeMcpServer | Same as addMcpServer |
| addMcpDefaultServer | ['mcp', 'config'] |
| removeMcpDefaultServer | ['mcp', 'config'] |
| setMcpEnabled | ['mcp', 'config'] |

 **Sources:** [src/renderer/src/stores/mcp.ts363-418](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/mcp.ts#L363-L418)

 
### Conditional Query Execution

 Tools, clients, and resources queries are conditionally enabled:

 
```

```

 This prevents queries from executing when:

 
 - MCP system hasn't finished initialization (`ready = false`)
 - MCP is globally disabled (`mcpEnabled = false`)
 
 The `ready` flag is set to `true` after `McpPresenter.initialize()` completes and emits `MCP_EVENTS.INITIALIZED`.

 **Sources:** [src/renderer/src/stores/mcp.ts94](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/mcp.ts#L94-L94) [src/renderer/src/stores/mcp.ts177-179](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/mcp.ts#L177-L179) [src/main/presenter/mcpPresenter/index.ts177-187](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/index.ts#L177-L187)

 
### Tool List Synchronization

 The store maintains enabled tool state in `useChatStore`:

 
```

```

 **Sources:** [src/renderer/src/stores/mcp.ts522-557](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/mcp.ts#L522-L557)

 
### Empty Enabled Tools Default

 When `enabledMcpTools` is empty or undefined, the system defaults to enabling all available tools:

 
```

```

 This prevents a scenario where restarting DeepChat results in zero enabled tools.

 **Sources:** [src/renderer/src/stores/mcp.ts693-702](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/mcp.ts#L693-L702)

 
---

 
## Summary

 The MCP system architecture achieves:

 
 - **Modularity**: Clean separation between presenter orchestration, lifecycle management, tool aggregation, and client connections
 - **Extensibility**: Four transport types support diverse server implementations (local processes, remote HTTP, built-in services)
 - **Reliability**: Session error recovery, connection timeouts, NPM registry optimization, notification-driven cache invalidation
 - **Security**: Three-level permission system with persistent and session-scoped grants, pre-execution permission checks, ACP agent access control
 - **Performance**: Query caching with automatic invalidation, background registry updates, tool definition caching with conflict resolution
 - **User Experience**: Sampling requests enable servers to leverage client's LLM capabilities, permission dialogs prevent unexpected operations
 
 The system integrates tightly with other DeepChat subsystems: LLM providers consume MCP tools for function calling, configuration helpers manage persistence, the event bus coordinates state updates, and the renderer provides reactive UI state management through Pinia Colada queries.

 **Sources:** [src/main/presenter/mcpPresenter/index.ts](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/index.ts) [src/main/presenter/mcpPresenter/mcpClient.ts](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/mcpClient.ts) [src/main/presenter/mcpPresenter/serverManager.ts](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/serverManager.ts) [src/main/presenter/mcpPresenter/toolManager.ts](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/toolManager.ts) [src/renderer/src/stores/mcp.ts](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/mcp.ts)
