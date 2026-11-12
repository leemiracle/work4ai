> 来源: [https://deepwiki.com/thinkinaixyz/deepchat/4.1-mcp-system-architecture](https://deepwiki.com/thinkinaixyz/deepchat/4.1-mcp-system-architecture)（Wayback 快照 2026-03-06）
> DeepWiki deepchat/4.1-mcp-system-architecture

# MCP System Architecture

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

 This document describes the Model Context Protocol (MCP) system architecture in DeepChat, the highest-priority system (importance 412.77) that enables tool calling and agent capabilities. It covers the three-tier architecture (Presenter/Manager/Client layers), transport mechanisms, tool aggregation with conflict resolution, and the permission system.

 For MCP configuration management and storage, see [MCP Configuration Management](https://deepwiki.com/thinkinaixyz/deepchat/4.7-mcp-configuration-management). For built-in MCP servers, see [Built-in MCP Servers](https://deepwiki.com/thinkinaixyz/deepchat/4.6-built-in-mcp-servers). For tool execution flow and permission UI, see [Tool Execution and Permission System](https://deepwiki.com/thinkinaixyz/deepchat/4.4-tool-execution-and-permission-system). For the MCP sampling feature, see [MCP Sampling System](https://deepwiki.com/thinkinaixyz/deepchat/4.5-mcp-sampling-system).

 
---

 
## Three-Tier Architecture Overview

 The MCP system implements a layered architecture separating concerns across three tiers:

 
```

```

 **Sources:** [src/main/presenter/mcpPresenter/index.ts83-112](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/index.ts#L83-L112) [src/main/presenter/mcpPresenter/serverManager.ts16-25](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/serverManager.ts#L16-L25) [src/main/presenter/mcpPresenter/toolManager.ts18-32](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/toolManager.ts#L18-L32) [src/main/presenter/mcpPresenter/mcpClient.ts115-145](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/mcpClient.ts#L115-L145)

 
| Layer | Components | Responsibilities |
|---|---|---|
| Configuration | McpConfHelper, useMcpStore | Persist server configs, manage UI state |
| Presenter | McpPresenter | Orchestrate operations, convert tool formats |
| Manager | ServerManager, ToolManager | Server lifecycle, tool aggregation, permissions |
| Client | McpClient instances | Individual server connections |
| Transport | Transport implementations | Communication protocols |

 
---

 
## Transport Layer

 Each `McpClient` supports four transport types based on server configuration:

 
```

```

 **Sources:** [src/main/presenter/mcpPresenter/mcpClient.ts147-373](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/mcpClient.ts#L147-L373)

 
### Transport Configuration

 
| Transport | Type Value | Required Config | Use Case |
|---|---|---|---|
| Stdio | 'stdio' | command, args, env | Local Node.js/Python servers via npx/uvx |
| SSE | 'sse' | baseUrl, customHeaders | Remote server-sent event endpoints |
| HTTP | 'http' | baseUrl, customHeaders | Remote HTTP streaming with session management |
| InMemory | 'inmemory' | args, env | Built-in DeepChat services (no external process) |

 The transport is selected in `McpClient.connect()` at [src/main/presenter/mcpPresenter/mcpClient.ts168-372](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/mcpClient.ts#L168-L372) based on `serverConfig.type`.

 
### Stdio Transport Details

 For `type: 'stdio'`, the system spawns external processes with environment management:

 
```

```

 **Sources:** [src/main/presenter/mcpPresenter/mcpClient.ts175-351](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/mcpClient.ts#L175-L351)

 Key environment handling logic:

 
 - **Node.js/UV commands** (npx, uv, uvx): Whitelist-only environment ([lines 219-267](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/lines 219-267))
 - **Other commands**: Preserve all system env vars, supplement PATH ([lines 269-314](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/lines 269-314))
 - **Custom env vars**: Merged into final environment ([lines 317-334](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/lines 317-334))
 - **NPM/UV registry**: Injected from `ServerManager` ([lines 336-343](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/lines 336-343))
 
 
---

 
## Client Layer: McpClient

 
### McpClient Class Structure

 
```

```

 **Sources:** [src/main/presenter/mcpPresenter/mcpClient.ts115-145](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/mcpClient.ts#L115-L145) [src/main/presenter/mcpPresenter/mcpClient.ts147-453](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/mcpClient.ts#L147-L453) [src/main/presenter/mcpPresenter/mcpClient.ts924-1014](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/mcpClient.ts#L924-L1014)

 
### Connection Lifecycle

 
```

```

 **Sources:** [src/main/presenter/mcpPresenter/mcpClient.ts147-453](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/mcpClient.ts#L147-L453)

 
### Notification Handlers

 The client registers handlers for server-initiated notifications:

 
| Notification Schema | Handler Behavior |
|---|---|
| ToolListChangedNotificationSchema | Clear cachedTools, refresh via listTools() |
| PromptListChangedNotificationSchema | Clear cachedPrompts, refresh via listPrompts() |
| ResourceListChangedNotificationSchema | Clear cachedResources, refresh via listResources() |
| ResourceUpdatedNotificationSchema | Clear cachedResources, refresh via listResources() |
| LoggingMessageNotificationSchema | Log message to console |

 **Sources:** [src/main/presenter/mcpPresenter/mcpClient.ts498-556](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/mcpClient.ts#L498-L556)

 
### Session Error Recovery

 For `StreamableHTTPClientTransport`, the client implements automatic session error recovery:

 
```

```

 **Sources:** [src/main/presenter/mcpPresenter/mcpClient.ts81-112](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/mcpClient.ts#L81-L112) [src/main/presenter/mcpPresenter/mcpClient.ts854-904](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/mcpClient.ts#L854-L904)

 Session error patterns detected ([lines 82-111](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/lines 82-111)):

 
 - "no valid session", "session expired", "session not found", "invalid session"
 - "http 400", "http 404", "bad request", "not found" (when combined with HTTP keywords)
 
 
---

 
## Manager Layer: ServerManager

 
### ServerManager Responsibilities

 
```

```

 **Sources:** [src/main/presenter/mcpPresenter/serverManager.ts16-343](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/serverManager.ts#L16-L343)

 
### NPM Registry Speed Testing

 The system tests multiple NPM registries on initialization to select the fastest:

 
| Registry URL | Purpose |
|---|---|
| https://registry.npmmirror.com/ | Alibaba mirror (China) |
| https://registry.npmjs.org/ | Official NPM registry |
| https://r.cnpmjs.org/ | CNPM mirror (China) |

 **Sources:** [src/main/presenter/mcpPresenter/serverManager.ts10-14](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/serverManager.ts#L10-L14)

 Test algorithm at [src/main/presenter/mcpPresenter/serverManager.ts44-147](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/serverManager.ts#L44-L147):

 
 - Test all registries in parallel with 10s timeout
 - Filter successful responses (status 200-299)
 - Sort by response time (lowest first)
 - Select fastest registry, cache result for 24 hours
 - Set UV registry to Aliyun mirror if NPM mirror is Alibaba
 
 The cache is stored in `ConfigPresenter` via `setNpmRegistryCache()` with structure:

 
```

```

 
### Server Start Flow

 
```

```

 **Sources:** [src/main/presenter/mcpPresenter/serverManager.ts235-280](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/serverManager.ts#L235-L280)

 
---

 
## Manager Layer: ToolManager

 
### ToolManager Responsibilities

 
```

```

 **Sources:** [src/main/presenter/mcpPresenter/toolManager.ts18-700](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/toolManager.ts#L18-L700)

 
### Tool Name Conflict Resolution

 When multiple servers expose tools with identical names, `ToolManager` implements two-pass conflict resolution:

 **Pass 1: Conflict Detection** ([lines 84-136](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/lines 84-136)):

 
```

```

 **Sources:** [src/main/presenter/mcpPresenter/toolManager.ts84-136](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/toolManager.ts#L84-L136)

 **Pass 2: Rename & Build Results** ([lines 139-209](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/lines 139-209)):

 
 - For tools marked in Pass 1: Rename to `{serverName}_{toolName}`
 - Update description to `[{serverName}] {originalDescription}`
 - Populate `toolNameToTargetMap` with mapping: `finalName -> {client, originalName}`
 - Validate renamed tools match pattern `/^[a-zA-Z0-9_-]+$/`
 
 Example conflict resolution:

 
 - Server A: `read_file` → `serverA_read_file`
 - Server B: `read_file` → `serverB_read_file`
 - Server C: `list_files` → `list_files` (no conflict)
 
 
### Tool Call Routing

 
```

```

 **Sources:** [src/main/presenter/mcpPresenter/toolManager.ts384-567](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/toolManager.ts#L384-L567)

 **Critical Detail**: The system calls tools using the **original name** from the server, not the potentially renamed final name. The `toolNameToTargetMap` resolves the LLM-facing name back to the original server name.

 
---

 
## Presenter Layer: McpPresenter

 
### McpPresenter as Orchestrator

 
```

```

 **Sources:** [src/main/presenter/mcpPresenter/index.ts83-665](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/index.ts#L83-L665)

 
### Tool Format Conversion

 `McpPresenter` provides methods to convert between MCP tool definitions and LLM-specific formats:

 **OpenAI Format** ([lines 792-849](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/lines 792-849)):

 
```

```

 **Anthropic Format** ([lines 857-900](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/lines 857-900)):

 
```

```

 **Gemini Format** ([lines 908-978](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/lines 908-978)):

 
```

```

 The conversion methods filter tool properties to supported JSON Schema attributes ([lines 688-783](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/lines 688-783)):

 
 - `type`, `nullable`, `description`, `properties`, `items`, `enum`, `anyOf`, `$def`
 
 
---

 
## Configuration Layer

 
### State Management Flow

 
```

```

 **Sources:** [src/renderer/src/stores/mcp.ts25-850](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/mcp.ts#L25-L850)

 
### useMcpStore Queries

 The store uses Pinia Colada for reactive query management:

 
| Query | Key | Enabled Condition | Stale Time |
|---|---|---|---|
| configQuery | ['mcp', 'config'] | Always | 30s |
| toolsQuery | ['mcp', 'tools'] | config.ready && config.mcpEnabled | 30s |
| clientsQuery | ['mcp', 'clients'] | config.ready && config.mcpEnabled | 30s |
| resourcesQuery | ['mcp', 'resources'] | config.ready && config.mcpEnabled | 30s |
| promptsQuery | ['mcp', 'prompts'] | Always | 60s |

 **Sources:** [src/renderer/src/stores/mcp.ts71-155](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/mcp.ts#L71-L155)

 
### MCP Enable/Disable Flow

 
```

```

 **Sources:** [src/renderer/src/stores/mcp.ts452-505](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/mcp.ts#L452-L505)

 Key behaviors:

 
 - **Optimistic update**: UI toggles immediately
 - **Default server auto-start**: When enabling, start all servers in `defaultServers` array
 - **Delayed refresh**: Additional tool refresh after 1s to catch late-registering tools
 - **State clearing**: When disabling, clear all server/tool state
 
 
---

 
## Data Flow: Tool Call Execution

 
### End-to-End Tool Call Flow

 
```

```

 **Sources:** [src/main/presenter/mcpPresenter/index.ts543-587](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/index.ts#L543-L587) [src/main/presenter/mcpPresenter/toolManager.ts384-567](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/toolManager.ts#L384-L567) [src/main/presenter/mcpPresenter/mcpClient.ts924-965](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/mcpClient.ts#L924-L965)

 
### Permission Check Details

 Permission checking in `ToolManager.callTool()` at [lines 478-522](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/lines 478-522):

 
 - Get server config from `ConfigPresenter.getMcpServers()`
 - Extract `autoApprove` array from config (e.g., `['read', 'write', 'all']`)
 - Determine permission type by analyzing tool name ([lines 226-271](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/lines 226-271)): 
 - **Read**: `read`, `list`, `get`, `show`, `view`, `fetch`, `search`, `find`, `query`, `tree`
 - **Write**: `write`, `create`, `update`, `delete`, `modify`, `edit`, `remove`, `add`, `insert`, `save`, `execute`, `run`, `call`, `move`, `copy`, `mkdir`, `rmdir`
 - **Default**: `write` (for safety)
 - Check permission hierarchy: 
 - Session-level permission (in-memory, conversation-scoped)
 - Persistent `'all'` permission
 - Persistent specific permission type
 - If no permission: Return `requiresPermission: true` with `permissionRequest` object
 
 
---

 
## Data Flow: MCP Sampling

 MCP servers can request LLM completions from DeepChat through the sampling mechanism:

 
```

```

 **Sources:** [src/main/presenter/mcpPresenter/mcpClient.ts558-641](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/mcpClient.ts#L558-L641) [src/main/presenter/mcpPresenter/index.ts612-664](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/index.ts#L612-L664)

 
### Sampling Request Payload

 The `McpSamplingRequestPayload` structure ([lines 656-665](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/lines 656-665)):

 
```

```

 
### Image Validation

 For sampling requests with images, the client validates:

 
 - MIME type in allowed set: `image/png`, `image/jpeg`, `image/gif`, `image/webp` ([lines 38-43](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/lines 38-43))
 - Base64 data format validation ([lines 737-771](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/lines 737-771))
 - Decode and re-encode to verify integrity
 
 
---

 
## Permission System

 
### Permission Levels

 
| Level | Description | Tool Name Patterns |
|---|---|---|
| read | Read-only operations | read_*, list_*, get_*, show_*, view_*, fetch_*, search_*, find_*, query_*, tree_* |
| write | Modify operations | write_*, create_*, update_*, delete_*, modify_*, edit_*, remove_*, add_*, insert_*, save_*, execute_*, run_*, call_*, move_*, copy_*, mkdir_*, rmdir_* |
| all | All operations | Grants both read and write |

 **Sources:** [src/main/presenter/mcpPresenter/toolManager.ts226-271](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/toolManager.ts#L226-L271)

 
### Permission Storage

 
```

```

 **Sources:** [src/main/presenter/mcpPresenter/toolManager.ts619-647](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/toolManager.ts#L619-L647) [src/main/presenter/mcpPresenter/toolManager.ts651-677](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/toolManager.ts#L651-L677)

 
### Grant Permission Flow

 
```

```

 **Sources:** [src/main/presenter/mcpPresenter/toolManager.ts619-647](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/toolManager.ts#L619-L647)

 
### ACP Agent MCP Access Control

 When in `'acp agent'` chat mode, an additional permission layer restricts which MCP servers an agent can access:

 
```

```

 **Sources:** [src/main/presenter/mcpPresenter/toolManager.ts423-448](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/toolManager.ts#L423-L448)

 This allows configuration of which MCP servers each ACP agent can use, providing agent-level tool isolation.

 
---

 
## Summary

 The MCP system architecture achieves:

 
 - **Clean separation**: Three tiers (Presenter/Manager/Client) with clear responsibilities
 - **Transport flexibility**: Four transport types (Stdio/SSE/HTTP/InMemory) for different server types
 - **Tool aggregation**: Automatic conflict resolution with server-prefixed renaming
 - **Permission control**: Three-level system (read/write/all) with session and persistent storage
 - **LLM integration**: Format converters for OpenAI, Anthropic, Gemini tool schemas
 - **Sampling support**: Bidirectional LLM requests from servers to client
 - **Session recovery**: Automatic reconnection for HTTP transport session errors
 - **Registry optimization**: NPM registry speed testing with 24-hour caching
 
 The system enables DeepChat to function as a universal MCP client, connecting to external tool servers while maintaining security through fine-grained permissions and agent-level access control.
