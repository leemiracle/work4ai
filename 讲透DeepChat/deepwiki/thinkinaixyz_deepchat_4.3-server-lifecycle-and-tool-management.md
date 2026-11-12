> 来源: [https://deepwiki.com/thinkinaixyz/deepchat/4.3-server-lifecycle-and-tool-management](https://deepwiki.com/thinkinaixyz/deepchat/4.3-server-lifecycle-and-tool-management)（Wayback 快照 2026-03-06）
> DeepWiki deepchat/4.3-server-lifecycle-and-tool-management

# Server Lifecycle and Tool Management

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
 
  This document describes how MCP servers are started, stopped, and managed throughout their lifecycle, as well as how tools are discovered, cached, and resolved when conflicts occur. This includes NPM registry speed testing, default server handling, and the tool conflict resolution system.

 For information about MCP client connections and transport protocols, see [4.2](https://deepwiki.com/thinkinaixyz/deepchat/4.2-mcp-client-and-transport-layer). For tool execution and permission handling, see [4.4](https://deepwiki.com/thinkinaixyz/deepchat/4.4-tool-execution-and-permission-system). For MCP configuration management, see [4.7](https://deepwiki.com/thinkinaixyz/deepchat/4.7-mcp-configuration-management).

 
## Overview

 The server lifecycle and tool management system is implemented across three primary classes:

 
 - `ServerManager` - Manages server instances, startup/shutdown, and NPM registry testing
 - `McpClient` - Handles individual server connections and lifecycle
 - `ToolManager` - Discovers tools from running servers and resolves naming conflicts
 
 These components work together to ensure MCP servers start reliably, tools are discovered efficiently, and naming conflicts are handled transparently.

 
## Server Lifecycle Management

 
### Server State Model

 
```

```

 **Server State Transitions**

 
| State | Description | Managed By |
|---|---|---|
| NotCreated | No client instance exists | ServerManager |
| Starting | Client instance created, connecting | ServerManager + McpClient |
| Connected | Transport connected, handshake complete | McpClient |
| Running | Server operational, accepting requests | McpClient |
| Stopping | Disconnect initiated | McpClient |
| Failed | Connection or session error occurred | McpClient |

 Sources: [src/main/presenter/mcpPresenter/serverManager.ts235-280](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/serverManager.ts#L235-L280) [src/main/presenter/mcpPresenter/mcpClient.ts148-453](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/mcpClient.ts#L148-L453)

 
### Server Startup Flow

 
```

```

 **Key Steps in Server Startup:**

 
 - **Pre-startup Checks** - [src/main/presenter/mcpPresenter/serverManager.ts236-244](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/serverManager.ts#L236-L244)

 
 - Verify server not already running
 - Retrieve server configuration from `ConfigPresenter`
 - **Client Instantiation** - [src/main/presenter/mcpPresenter/serverManager.ts254-263](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/serverManager.ts#L254-L263)

 
 - Create `McpClient` instance with server name, config, and registry settings
 - Store in `ServerManager.clients` Map
 - **Transport Setup** - [src/main/presenter/mcpPresenter/mcpClient.ts168-372](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/mcpClient.ts#L168-L372)

 
 - Select transport based on `serverConfig.type` (stdio, SSE, HTTP, inmemory)
 - For stdio: process command/args expansion with `RuntimeHelper`
 - Configure environment variables with allowlist for Node.js/UV commands
 - Apply npm and uv registry settings
 - **Connection Establishment** - [src/main/presenter/mcpPresenter/mcpClient.ts374-432](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/mcpClient.ts#L374-L432)

 
 - Create MCP Client with DeepChat capabilities (including `sampling`)
 - Register notification handlers for tool/prompt/resource list changes
 - Connect with 5-minute timeout using `Promise.race`
 - Set `isConnected = true` on success
 - **Event Emission** - [src/main/presenter/mcpPresenter/serverManager.ts278](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/serverManager.ts#L278-L278)

 
 - Broadcast `MCP_EVENTS.CLIENT_LIST_UPDATED` to all windows
 - Trigger `MCP_EVENTS.SERVER_STARTED` from McpPresenter
 
 Sources: [src/main/presenter/mcpPresenter/serverManager.ts235-280](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/serverManager.ts#L235-L280) [src/main/presenter/mcpPresenter/mcpClient.ts148-453](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/mcpClient.ts#L148-L453)

 
### Server Shutdown Flow

 
```

```

 **Cleanup Process:**

 The `cleanupResources()` method [src/main/presenter/mcpPresenter/mcpClient.ts471-496](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/mcpClient.ts#L471-L496) performs:

 
 - Clear connection timeout if pending
 - Close transport connection
 - Reset `client` and `transport` to null
 - Set `isConnected = false`
 - Clear cached tools, prompts, and resources
 
 Sources: [src/main/presenter/mcpPresenter/serverManager.ts307-327](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/serverManager.ts#L307-L327) [src/main/presenter/mcpPresenter/mcpClient.ts456-468](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/mcpClient.ts#L456-L468) [src/main/presenter/mcpPresenter/mcpClient.ts471-496](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/mcpClient.ts#L471-L496)

 
### Session Error Recovery

 The `McpClient` includes automatic session error detection and recovery for Streamable HTTP transport:

 
```

```

 **Session Error Detection Patterns** - [src/main/presenter/mcpPresenter/mcpClient.ts82-112](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/mcpClient.ts#L82-L112):

 
 - "no valid session", "session expired", "session not found"
 - "invalid session", "session id", "mcp-session-id"
 - HTTP 400/404 errors related to session endpoints
 
 **Recovery Logic** - [src/main/presenter/mcpPresenter/mcpClient.ts854-904](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/mcpClient.ts#L854-L904):

 
 - First error: Clean up and allow reconnection (`hasRestarted = true`)
 - Second consecutive error: Permanently stop service
 - Clear all caches to ensure fresh data after recovery
 
 Sources: [src/main/presenter/mcpPresenter/mcpClient.ts82-112](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/mcpClient.ts#L82-L112) [src/main/presenter/mcpPresenter/mcpClient.ts854-904](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/mcpClient.ts#L854-L904)

 
## NPM Registry Speed Testing

 To ensure fast package installation for stdio-based MCP servers, `ServerManager` automatically tests and selects the fastest npm registry.

 
### Registry Test Algorithm

 
```

```

 **Registry List** - [src/main/presenter/mcpPresenter/serverManager.ts10-14](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/serverManager.ts#L10-L14):

 
```

```

 **Test Parameters** - [src/main/presenter/mcpPresenter/serverManager.ts71-73](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/serverManager.ts#L71-L73):

 
 - Timeout: 10 seconds per registry
 - Test package: `tiny-runtime-injector`
 - Proxy configuration applied if configured
 
 **Cache Management** - [src/main/presenter/mcpPresenter/serverManager.ts139-145](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/serverManager.ts#L139-L145):

 
 - Cache stored in ConfigPresenter via `setNpmRegistryCache()`
 - Cache includes: `registry`, `lastChecked`, `isAutoDetect`
 - Cache validity checked via `isNpmRegistryCacheValid()`
 
 **Background Updates** - [src/main/presenter/mcpPresenter/serverManager.ts159-172](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/serverManager.ts#L159-L172):

 
 - Triggered 5 seconds after initialization
 - Only runs if cache is expired
 - Updates cache without blocking operations
 
 Sources: [src/main/presenter/mcpPresenter/serverManager.ts44-147](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/serverManager.ts#L44-L147) [src/main/presenter/mcpPresenter/serverManager.ts159-172](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/serverManager.ts#L159-L172)

 
## Default Server Management

 Default servers are automatically started when MCP is enabled. The system supports up to 30 default servers.

 
### Default Server Operations

 
| Operation | Method | Description |
|---|---|---|
| Get list | getMcpDefaultServers() | Returns array of default server names |
| Add | addMcpDefaultServer(name) | Adds server to defaults (max 30) |
| Remove | removeMcpDefaultServer(name) | Removes from defaults |
| Toggle | toggleMcpDefaultServer(name) | Adds or removes based on current state |
| Reset | resetToDefaultServers() | Restores original default set |

 **Auto-Start Flow** - [src/main/presenter/mcpPresenter/index.ts158-174](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/index.ts#L158-L174):

 
```

```

 **Renderer-Side Default Management** - [src/renderer/src/stores/mcp.ts602-622](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/mcp.ts#L602-L622):

 
 - `toggleDefaultServer()` checks `hasMaxDefaultServers` (30 limit)
 - Returns error if limit reached
 - Mutations automatically invalidate config cache
 
 **Custom Prompts Server Priority** - [src/main/presenter/mcpPresenter/index.ts138-155](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/index.ts#L138-L155):

 
 - `deepchat-inmemory/custom-prompts-server` always started first if configured
 - Ensures custom prompts are available immediately
 
 Sources: [src/main/presenter/mcpPresenter/index.ts114-188](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/index.ts#L114-L188) [src/main/presenter/mcpPresenter/serverManager.ts179-222](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/serverManager.ts#L179-L222) [src/renderer/src/stores/mcp.ts602-635](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/mcp.ts#L602-L635)

 
## Tool Discovery and Caching

 The `ToolManager` discovers tools from all running servers and maintains a unified cache with conflict resolution.

 
### Tool Discovery Flow

 
```

```

 **Two-Pass Algorithm** - [src/main/presenter/mcpPresenter/toolManager.ts80-224](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/toolManager.ts#L80-L224):

 **Pass 1: Conflict Detection**

 
 - Build `toolNameToServerMap` tracking which server owns each tool name
 - Detect conflicts when same tool name appears from multiple servers
 - Mark all conflicting tools in `toolsToRename` Map per server
 
 **Pass 2: Build Results with Renaming**

 
 - Process each server's tools
 - If tool name in `toolsToRename`, prefix with `{serverName}_`
 - Validate against pattern `/^[a-zA-Z0-9_-]+$/`
 - Build `MCPToolDefinition` with function parameters
 - Update `toolNameToTargetMap` with final name → {client, originalName}
 
 **Tool Definition Structure** - [src/main/presenter/mcpPresenter/toolManager.ts173-189](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/toolManager.ts#L173-L189):

 
```

```

 Sources: [src/main/presenter/mcpPresenter/toolManager.ts50-224](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/toolManager.ts#L50-L224)

 
### Tool Cache Management

 **Cache Invalidation Events:**

 
| Event | Trigger | Action |
|---|---|---|
| MCP_EVENTS.CLIENT_LIST_UPDATED | Server start/stop | Clear cachedToolDefinitions and toolNameToTargetMap |
| MCP_EVENTS.CONFIG_CHANGED | Configuration update | Clear caches |
| ToolListChangedNotificationSchema | Server notification | Clear cachedTools in McpClient, refresh |

 **Client-Level Caching** - [src/main/presenter/mcpPresenter/mcpClient.ts130-133](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/mcpClient.ts#L130-L133):

 
 - Each `McpClient` maintains `cachedTools`, `cachedPrompts`, `cachedResources`
 - Cleared on list change notifications
 - Actively refreshes after clearing
 
 **Manager-Level Caching** - [src/main/presenter/mcpPresenter/toolManager.ts21-23](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/toolManager.ts#L21-L23):

 
 - `cachedToolDefinitions`: Array of all tool definitions after conflict resolution
 - `toolNameToTargetMap`: Maps final tool name to {client, originalName}
 - Both cleared together to maintain consistency
 
 Sources: [src/main/presenter/mcpPresenter/toolManager.ts30-44](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/toolManager.ts#L30-L44) [src/main/presenter/mcpPresenter/mcpClient.ts505-556](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/mcpClient.ts#L505-L556)

 
## Tool Name Conflict Resolution

 When multiple servers provide tools with the same name, the system automatically renames them to prevent collisions.

 
### Conflict Resolution Strategy

 
```

```

 **Conflict Detection Logic** - [src/main/presenter/mcpPresenter/toolManager.ts91-108](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/toolManager.ts#L91-L108):

 
```

```

 **Renaming Implementation** - [src/main/presenter/mcpPresenter/toolManager.ts151-154](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/toolManager.ts#L151-L154):

 
```

```

 **Name Validation** - [src/main/presenter/mcpPresenter/toolManager.ts157-163](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/toolManager.ts#L157-L163):

 
 - Pattern: `/^[a-zA-Z0-9_-]+$/`
 - Invalid names are skipped and logged
 - Ensures compatibility with all LLM provider tool name requirements
 
 **Tool Call Routing** - [src/main/presenter/mcpPresenter/toolManager.ts407-421](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/toolManager.ts#L407-L421):

 
 - When tool is called with renamed name, `toolNameToTargetMap` provides original name
 - `McpClient.callTool()` invoked with original tool name
 - Transparent to LLM - sees renamed tool, server receives original name
 
 Sources: [src/main/presenter/mcpPresenter/toolManager.ts80-224](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/toolManager.ts#L80-L224) [src/main/presenter/mcpPresenter/toolManager.ts384-567](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/toolManager.ts#L384-L567)

 
## Integration with Renderer Process

 The renderer process tracks server status and tool availability through the `useMcpStore`.

 
### State Synchronization Architecture

 
```

```

 **Server Status Tracking** - [src/renderer/src/stores/mcp.ts508-557](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/mcp.ts#L508-L557):

 
 - `serverStatuses` ref tracks running state per server
 - `updateServerStatus()` queries `mcpPresenter.isServerRunning()`
 - After status change, refreshes tools and clients with `{ force: true }`
 - Automatically enables/disables tools in `chatStore.chatConfig.enabledMcpTools`
 
 **Query Invalidation Strategy** - [src/renderer/src/stores/mcp.ts362-418](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/mcp.ts#L362-L418):

 
| Mutation | Invalidates |
|---|---|
| addServerMutation | config, tools, clients, resources |
| updateServerMutation | config, tools, clients, resources |
| removeServerMutation | config, tools, clients, resources |
| addDefaultServerMutation | config |
| removeDefaultServerMutation | config |
| setMcpEnabledMutation | config |

 **Optimistic Updates** - [src/renderer/src/stores/mcp.ts638-669](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/mcp.ts#L638-L669):

 
 - `toggleServer()` immediately updates `serverStatuses[serverName]`
 - Shows loading state via `serverLoadingStates[serverName]`
 - Rolls back on error
 - Syncs actual state after operation completes
 
 Sources: [src/renderer/src/stores/mcp.ts422-557](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/mcp.ts#L422-L557) [src/renderer/src/stores/mcp.ts638-669](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/mcp.ts#L638-L669)

 
### MCP Enabled State Management

 Enabling/disabling MCP involves coordinating server startup, tool loading, and cache management.

 
```

```

 **Enable Flow** - [src/renderer/src/stores/mcp.ts452-504](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/mcp.ts#L452-L504):

 
 - Optimistically set `mcpEnabled = true` and `ready = true`
 - Call mutation to persist state
 - Force refresh config query
 - Start all default servers via `startDefaultServers()`
 - Update server statuses
 - Wait 300ms for servers to register tools
 - Force refresh tools, clients, prompts
 - Schedule another refresh after 1 second to catch any delayed registrations
 
 **Disable Flow** - [src/renderer/src/stores/mcp.ts484-495](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/mcp.ts#L484-L495):

 
 - Clear `serverStatuses`, `toolInputs`, `toolResults`
 - Force refetch all queries to get empty results
 - Config queries remain enabled but return disabled state
 
 Sources: [src/renderer/src/stores/mcp.ts438-505](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/mcp.ts#L438-L505) [src/renderer/src/stores/mcp.ts206-268](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/mcp.ts#L206-L268)

 
## Error Handling and Notifications

 Errors during server lifecycle operations are captured and displayed to users.

 
### Error Notification Flow

 
```

```

 **Error Types and Messages:**

 
| Error Context | Title Key | Message Format |
|---|---|---|
| Server connection failed | mcpConnectionErrorTitle | {serverName}: {errorMessage} |
| Tool list fetch failed | getMcpToolListErrorTitle | Server and error details |
| Server toggle failed | toggleServerFailed | {serverName} with error |
| Add server duplicate | addMcpServerErrorTitle | {serverName} already exists |

 **Implementation** - [src/main/presenter/mcpPresenter/serverManager.ts283-305](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/serverManager.ts#L283-L305):

 
 - Extract locale from `ConfigPresenter.getLanguage()`
 - Load i18n labels via `getErrorMessageLabels(locale)`
 - Generate unique notification ID: `mcp-error-{serverName}-{timestamp}`
 - Send to all windows via `NOTIFICATION_EVENTS.SHOW_ERROR`
 
 **Pass 1/Pass 2 Error Handling** - [src/main/presenter/mcpPresenter/toolManager.ts112-135](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/toolManager.ts#L112-L135):

 
 - Pass 1 errors logged and notified, but conflict detection continues
 - Pass 2 errors logged, but results from other clients still included
 - Ensures partial functionality if some servers fail
 
 Sources: [src/main/presenter/mcpPresenter/serverManager.ts283-305](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/serverManager.ts#L283-L305) [src/main/presenter/mcpPresenter/toolManager.ts112-135](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/toolManager.ts#L112-L135) [src/main/presenter/mcpPresenter/toolManager.ts196-207](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/toolManager.ts#L196-L207)
