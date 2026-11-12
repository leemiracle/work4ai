> 来源: [https://deepwiki.com/thinkinaixyz/deepchat/4.4-tool-execution-and-permission-system](https://deepwiki.com/thinkinaixyz/deepchat/4.4-tool-execution-and-permission-system)（Wayback 快照 2026-03-06）
> DeepWiki deepchat/4.4-tool-execution-and-permission-system

# Tool Execution and Permission System

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
 
  This document describes the tool execution pipeline and two-level permission system in DeepChat's MCP integration. It covers how tools are called by LLMs, how permissions are checked and granted, and how tool results are formatted and returned.

 For information about MCP server lifecycle and tool discovery, see [Server Lifecycle and Tool Management](https://deepwiki.com/thinkinaixyz/deepchat/4.3-server-lifecycle-and-tool-management). For tool format conversion between providers, see MCP Tool Format Conversion.

 
---

 
## Overview

 The tool execution system orchestrates the following flow:

 
 - **Pre-execution permission check** - Optional pre-flight check without executing the tool
 - **Permission validation** - Two-level system (session-scoped + persistent configuration)
 - **Tool invocation** - Routing to appropriate MCP server and calling the tool
 - **Result formatting** - Converting MCP responses to LLM-friendly format
 - **Error handling** - Graceful degradation with permission requests
 
 The permission system uses a **two-level hierarchy**:

 
 - **Session-level permissions** (temporary, memory-only, per-conversation)
 - **Persistent permissions** (stored in server configuration, cross-session)
 
 
---

 
## Tool Execution Architecture

 
### Component Interaction

 
```

```

 **Sources:** [src/main/presenter/mcpPresenter/toolManager.ts1-700](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/toolManager.ts#L1-L700) [src/main/presenter/mcpPresenter/mcpClient.ts924-965](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/mcpClient.ts#L924-L965)

 
---

 
## Permission Types and Detection

 
### Permission Type Classification

 The system automatically determines permission requirements based on tool name patterns:

 
| Permission Type | Tool Name Patterns | Examples |
|---|---|---|
| read | read, list, get, show, view, fetch, search, find, query, tree | read_file, list_directory, search_code |
| write | write, create, update, delete, modify, edit, remove, add, insert, save, execute, run, call, move, copy, mkdir, rmdir | write_file, create_directory, execute_command |
| all | Explicit configuration | User grants all permissions to server |

 **Default behavior:** Unknown operations default to `write` for safety.

 
```

```

 **Sources:** [src/main/presenter/mcpPresenter/toolManager.ts226-271](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/toolManager.ts#L226-L271)

 
---

 
## Two-Level Permission System

 
### Architecture

 
```

```

 **Sources:** [src/main/presenter/mcpPresenter/toolManager.ts24-26](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/toolManager.ts#L24-L26) [src/main/presenter/mcpPresenter/toolManager.ts273-315](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/toolManager.ts#L273-L315) [src/main/presenter/mcpPresenter/toolManager.ts649-685](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/toolManager.ts#L649-L685)

 
### Session Permission Hierarchy

 Session permissions follow a hierarchical model where higher-level permissions automatically grant lower-level access:

 
```
all > write > read
```

 **Example:** Granting `write` permission implicitly grants `read` permission for the same server in that conversation.

 **Sources:** [src/main/presenter/mcpPresenter/toolManager.ts650-685](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/toolManager.ts#L650-L685)

 
---

 
## Tool Call Process

 
### Complete Execution Flow

 
```

```

 **Sources:** [src/main/presenter/mcpPresenter/toolManager.ts384-567](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/toolManager.ts#L384-L567) [src/main/presenter/mcpPresenter/mcpClient.ts924-965](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/mcpClient.ts#L924-L965)

 
### Key Steps in `callTool()`

 
 - **Tool Resolution** ([toolManager.ts386-421](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/toolManager.ts#L386-L421))

 
 - Look up `finalName` in `toolNameToTargetMap`
 - Extract `originalName` and target `McpClient`
 - Handle tool not found errors
 - **ACP Agent Access Control** ([toolManager.ts423-448](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/toolManager.ts#L423-L448))

 
 - Only active in "acp agent" chat mode
 - Check if server is in agent's MCP selections
 - Reject if not allowed
 - **Permission Check** ([toolManager.ts477-522](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/toolManager.ts#L477-L522))

 
 - Load server config with `autoApprove` settings
 - Call `checkToolPermission()` with session and persistent checks
 - Return permission request if denied
 - **Argument Parsing** ([toolManager.ts458-475](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/toolManager.ts#L458-L475))

 
 - Parse JSON arguments string
 - Fallback to `jsonrepair()` on parse errors
 - Use empty object `{}` if all parsing fails
 - **Tool Execution** ([toolManager.ts524-526](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/toolManager.ts#L524-L526))

 
 - Call `targetClient.callTool(originalName, args)`
 - Use original tool name (not renamed version)
 - **Result Formatting** ([toolManager.ts528-553](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/toolManager.ts#L528-L553))

 
 - Handle string content directly
 - Convert content arrays to `MCPContentItem[]`
 - Format image, resource, and text types
 - Add error marker if `isError` flag set
 
 **Sources:** [src/main/presenter/mcpPresenter/toolManager.ts384-567](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/toolManager.ts#L384-L567)

 
---

 
## Permission Request Flow

 
### Permission Request Object

 When a tool requires permission, `callTool()` returns an `MCPToolResponse` with `requiresPermission: true`:

 
```

```

 **Sources:** [src/main/presenter/mcpPresenter/toolManager.ts508-522](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/toolManager.ts#L508-L522)

 
### Granting Permissions

 
```

```

 **Sources:** [src/main/presenter/mcpPresenter/toolManager.ts619-647](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/toolManager.ts#L619-L647)

 
### `grantPermission()` Method

 
```

```

 **Parameters:**

 
 - `serverName` - MCP server identifier
 - `permissionType` - Level of access to grant
 - `remember` - `true` = persistent, `false` = session-only
 - `conversationId` - Required for session-level grants
 
 **Behavior:**

 
 - **Persistent (`remember: true`)**: Calls `updateServerPermissions()` which modifies `autoApprove` array in server config
 - **Session (`remember: false`)**: Adds `"serverName:permissionType"` key to `sessionPermissions.get(conversationId)` Set
 
 **Sources:** [src/main/presenter/mcpPresenter/toolManager.ts619-647](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/toolManager.ts#L619-L647)

 
---

 
## Pre-Check Permission API

 The `preCheckToolPermission()` method allows checking permissions **before** executing a tool:

 
```

```

 **Returns:**

 
 - `null` if permission already granted
 - Permission requirement object if permission needed
 
 **Use Case:** Display permission prompt to user before LLM generates the tool call, allowing for better UX in multi-turn tool scenarios.

 **Sources:** [src/main/presenter/mcpPresenter/toolManager.ts317-382](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/toolManager.ts#L317-L382) [src/main/presenter/mcpPresenter/index.ts593-610](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/index.ts#L593-L610)

 
---

 
## Tool Result Formatting

 
### Content Type Handling

 The `callTool()` method in `McpPresenter` formats raw MCP results into LLM-friendly strings:

 
```

```

 **Example Formatted Output:**

 
```

```

 **Sources:** [src/main/presenter/mcpPresenter/index.ts543-587](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/index.ts#L543-L587)

 
### Split Merged Content Handling

 MCP servers can return multiple content items in a single response. The system preserves this structure:

 
 - **Text content** - Extracted directly
 - **Image content** - Represented as placeholder with MIME type
 - **Resource content** - Formatted based on resource type (text, blob, or URI-only)
 
 Each content type is joined with double newlines (`\n\n`) for readability.

 **Sources:** [src/main/presenter/mcpPresenter/index.ts556-579](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/index.ts#L556-L579)

 
---

 
## ACP Agent-Level Access Control

 In **ACP agent mode**, an additional permission layer restricts which MCP servers an agent can access:

 
```

```

 **Configuration:**

 
 - ACP agent MCP selections are stored in config with `getAgentMcpSelections(agentId)`
 - Returns `string[]` of allowed server names
 - Empty or missing array denies all MCP access for that agent
 
 **Error Message:**

 
```
MCP server '{serverName}' is not allowed for ACP agent '{agentId}'. 
Configure MCP access in ACP settings.
```

 **Sources:** [src/main/presenter/mcpPresenter/toolManager.ts423-448](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/toolManager.ts#L423-L448)

 
---

 
## Permission Check Implementation

 
### `checkToolPermission()` Method

 
```

```

 **Check Order:**

 
 - **Session permissions** (if `conversationId` provided)

 
 - Call `checkSessionPermission(conversationId, serverName, permissionType)`
 - Uses hierarchical permission model
 - Returns `true` if found in session cache
 - **Persistent 'all' permission**

 
 - Check if `autoApprove.includes('all')`
 - Grants all operations for this server
 - **Persistent specific permission**

 
 - Check if `autoApprove.includes(permissionType)`
 - Grants only operations of specified type
 - **Default: Deny**

 
 - Returns `false`, triggering permission request
 
 **Sources:** [src/main/presenter/mcpPresenter/toolManager.ts273-315](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/toolManager.ts#L273-L315)

 
### `checkSessionPermission()` Implementation

 
```

```

 **Permission Hierarchy Logic:**

 
```

```

 **Example:** If session has `"myserver:write"` permission, it automatically grants `"myserver:read"` requests.

 **Sources:** [src/main/presenter/mcpPresenter/toolManager.ts649-685](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/toolManager.ts#L649-L685)

 
---

 
## Error Handling

 
### Common Error Scenarios

 
| Error Type | Detection | Response |
|---|---|---|
| Tool not found | !toolNameToTargetMap.get(finalName) | Return error: "Tool '{name}' not found or server not running" |
| Server config missing | !servers[toolServerName] | Return error: "Configuration missing for server '{name}'" |
| ACP access denied | !selections.includes(toolServerName) | Return error with agent/server details |
| Permission denied | !hasPermission | Return requiresPermission: true with permission request object |
| Argument parse error | JSON.parse() fails | Fallback to jsonrepair(), then empty object {} |
| Tool execution error | result.isError flag | Prefix content with "Error: " |

 **Sources:** [src/main/presenter/mcpPresenter/toolManager.ts384-567](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/toolManager.ts#L384-L567)

 
### Graceful Degradation

 The system prioritizes non-blocking behavior:

 
 - **Argument parsing failures** → Continue with empty object rather than failing
 - **Permission denials** → Return permission request rather than throwing error
 - **Tool execution errors** → Return formatted error rather than crashing
 
 **Sources:** [src/main/presenter/mcpPresenter/toolManager.ts459-475](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/toolManager.ts#L459-L475)

 
---

 
## Integration with LLM Agent Loop

 The tool execution system integrates with the agent loop (see [Streaming and Agent Loop](https://deepwiki.com/thinkinaixyz/deepchat/5.3-streaming-and-agent-loop)) through these events:

 
 - **Tool call initiated** - LLM provider returns tool call in streaming response
 - **Permission check** - Agent presenter calls `preCheckToolPermission()` (optional) or `callTool()`
 - **User approval** (if needed) - UI displays permission request, waits for user decision
 - **Tool execution** - Approved calls execute via `callTool()`
 - **Result return** - Formatted result sent back to LLM for next turn
 
 **Event Flow:**

 
```
LLM_STREAM_EVENT → TOOL_CALL_INITIATED → PERMISSION_REQUEST? → TOOL_CALL_RESULT
```

 **Sources:** [src/main/presenter/mcpPresenter/toolManager.ts555](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/toolManager.ts#L555-L555)

 
---

 
## Configuration Schema

 
### Server Auto-Approve Configuration

 
```

```

 **Example:**

 
```

```

 **Storage:** Persisted in `mcp-settings.json` via `ElectronStore`.

 **Sources:** [src/main/presenter/mcpPresenter/toolManager.ts477-488](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/toolManager.ts#L477-L488)

 
---

 
## Summary

 The tool execution and permission system provides:

 
 - **Two-level permission architecture** balancing security and UX
 - **Automatic permission type detection** based on tool name patterns
 - **Session-scoped temporary permissions** for conversation-specific grants
 - **Persistent configuration** for trusted tool auto-approval
 - **ACP agent-level access control** for multi-agent security
 - **Graceful error handling** with non-blocking permission requests
 - **Flexible result formatting** supporting text, images, and resources
 
 This design enables secure, user-controlled tool execution while minimizing friction for trusted operations and repeat tool usage within a conversation.

 **Sources:** [src/main/presenter/mcpPresenter/toolManager.ts](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/toolManager.ts) [src/main/presenter/mcpPresenter/index.ts543-610](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/index.ts#L543-L610) [src/main/presenter/mcpPresenter/mcpClient.ts924-965](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/mcpClient.ts#L924-L965)
