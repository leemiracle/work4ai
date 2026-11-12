> 来源: [https://deepwiki.com/thinkinaixyz/deepchat/4.7-mcp-configuration-management](https://deepwiki.com/thinkinaixyz/deepchat/4.7-mcp-configuration-management)（Wayback 快照 2026-03-06）
> DeepWiki deepchat/4.7-mcp-configuration-management

# MCP Configuration Management

  Relevant source files 
 - [src/main/presenter/configPresenter/mcpConfHelper.ts](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/configPresenter/mcpConfHelper.ts)
 - [src/main/presenter/mcpPresenter/inMemoryServers/builder.ts](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/inMemoryServers/builder.ts)
 - [src/renderer/src/components/mcp-config/mcpServerForm.vue](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/mcp-config/mcpServerForm.vue)
 - [src/renderer/src/i18n/en-US/mcp.json](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/i18n/en-US/mcp.json)
 - [src/renderer/src/i18n/fa-IR/mcp.json](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/i18n/fa-IR/mcp.json)
 - [src/renderer/src/i18n/fr-FR/mcp.json](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/i18n/fr-FR/mcp.json)
 - [src/renderer/src/i18n/ja-JP/mcp.json](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/i18n/ja-JP/mcp.json)
 - [src/renderer/src/i18n/ko-KR/mcp.json](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/i18n/ko-KR/mcp.json)
 - [src/renderer/src/i18n/ru-RU/mcp.json](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/i18n/ru-RU/mcp.json)
 - [src/renderer/src/i18n/zh-CN/mcp.json](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/i18n/zh-CN/mcp.json)
 - [src/renderer/src/i18n/zh-HK/mcp.json](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/i18n/zh-HK/mcp.json)
 - [src/renderer/src/i18n/zh-TW/mcp.json](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/i18n/zh-TW/mcp.json)
 
  This document details the MCP configuration management system, which is responsible for persisting, validating, and managing MCP server configurations through the `McpConfHelper` class. This includes handling built-in servers, user-defined servers, default server lists, NPM registry settings, platform-specific servers, and configuration migrations.

 For information about the MCP system architecture and server lifecycle, see [MCP System Architecture](https://deepwiki.com/thinkinaixyz/deepchat/4.1-mcp-system-architecture). For details about the MCP configuration UI components, see [MCP Configuration UI](https://deepwiki.com/thinkinaixyz/deepchat/4.8-mcp-configuration-ui). For information about built-in MCP servers, see [Built-in MCP Servers](https://deepwiki.com/thinkinaixyz/deepchat/4.6-built-in-mcp-servers).

 
## System Overview

 The `McpConfHelper` class serves as the central configuration manager for all MCP servers in DeepChat. It bridges the gap between persistent storage (ElectronStore), the `ConfigPresenter`, and the `McpPresenter`, ensuring that server configurations are consistently stored, validated, and synchronized across the application.

 **Core Architecture: McpConfHelper in Context**

 
```

```

 Sources: [src/main/presenter/configPresenter/mcpConfHelper.ts1-997](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/configPresenter/mcpConfHelper.ts#L1-L997) [src/main/presenter/mcpPresenter/inMemoryServers/builder.ts1-97](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/inMemoryServers/builder.ts#L1-L97)

 
## ElectronStore Data Structure

 `McpConfHelper` uses ElectronStore to persist configuration in `mcp-settings.json`. The store maintains a structured schema for all MCP-related settings.

 **MCP Settings Schema**

 
| Field | Type | Description |
|---|---|---|
| mcpServers | Record<string, MCPServerConfig> | Dictionary of all server configurations keyed by server name |
| defaultServers | string[] | Array of server names to start automatically |
| mcpEnabled | boolean | Global enable/disable flag for MCP functionality |
| customNpmRegistry | string? | User-specified NPM registry URL |
| autoDetectNpmRegistry | boolean? | Whether to auto-detect fastest NPM registry |
| npmRegistryCache | INpmRegistryCache? | Cached NPM registry URL with timestamp |
| removedBuiltInServers | string[] | List of built-in servers explicitly removed by user |

 The `MCPServerConfig` interface includes:

 
| Field | Type | Description |
|---|---|---|
| command | string | Executable command (for stdio servers) |
| args | string[] | Command arguments |
| env | Record<string, string> | Environment variables |
| descriptions | string | Human-readable description |
| icons | string | Emoji icon for UI display |
| autoApprove | string[] | Auto-approved tool permissions ('all', 'read', 'write') |
| type | MCPServerType | Server type: 'stdio', 'sse', 'http', 'inmemory' |
| disable | boolean? | Whether server is disabled |
| baseUrl | string? | Base URL for SSE/HTTP servers |
| customHeaders | Record<string, string>? | Custom HTTP headers |
| customNpmRegistry | string? | Server-specific NPM registry override |

 Sources: [src/main/presenter/configPresenter/mcpConfHelper.ts11-46](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/configPresenter/mcpConfHelper.ts#L11-L46)

 
## Built-in Server Management

 The system defines three categories of built-in servers that are automatically provisioned and managed:

 **Built-in Server Hierarchy**

 
```

```

 
### Built-in Server Categories

 
 - **DEFAULT_INMEMORY_SERVERS** - Core built-in servers available on all platforms:

 
 - `Artifacts` - Rich artifact rendering
 - `bochaSearch` / `braveSearch` - Web search services
 - `imageServer` - Image understanding/generation proxy
 - `powerpack` - Enhanced capabilities (time, web, code execution)
 - Knowledge servers (`difyKnowledge`, `ragflowKnowledge`, `fastGptKnowledge`, `builtinKnowledge`)
 - `deepchat-inmemory/deep-research-server` - Deep research with web search
 - `deepchat-inmemory/auto-prompting-server` - Automatic prompt selection
 - `deepchat-inmemory/conversation-search-server` - Conversation history search
 - `deepchat-inmemory/meeting-server` - Multi-agent discussions
 - **PLATFORM_SPECIFIC_SERVERS** - Servers available only on specific platforms:

 
 - `deepchat/apple-server` - macOS system integration (Calendar, Contacts, Mail, etc.) - only on macOS
 - **DEFAULT_MCP_SERVERS** - Combines all built-in servers plus default third-party servers:

 
 - Includes all `DEFAULT_INMEMORY_SERVERS`
 - Includes applicable `PLATFORM_SPECIFIC_SERVERS` based on runtime platform
 - Example third-party: `nowledge-mem` (HTTP-based memory service)
 
 Sources: [src/main/presenter/configPresenter/mcpConfHelper.ts62-316](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/configPresenter/mcpConfHelper.ts#L62-L316)

 
### Built-in Server Tracking

 The `removedBuiltInServers` mechanism allows users to remove built-in servers while preserving this choice across version upgrades. When a built-in server is deleted by the user, its name is added to this list, preventing it from being re-added during `getMcpServers()`.

 **Built-in Server Removal Flow**

 
```

```

 Key methods:

 
 - `markBuiltInServerRemoved(name)` - Adds server name to persistent removal list [mcpConfHelper.ts353-358](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/mcpConfHelper.ts#L353-L358)
 - `unmarkBuiltInServerRemoved(name)` - Removes server from removal list (when re-added) [mcpConfHelper.ts360-364](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/mcpConfHelper.ts#L360-L364)
 - `isBuiltInServer(name)` - Checks if name exists in `BUILT_IN_SERVER_NAMES` set [mcpConfHelper.ts349-351](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/mcpConfHelper.ts#L349-L351)
 
 Sources: [src/main/presenter/configPresenter/mcpConfHelper.ts337-364](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/configPresenter/mcpConfHelper.ts#L337-L364) [src/main/presenter/configPresenter/mcpConfHelper.ts381-451](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/configPresenter/mcpConfHelper.ts#L381-L451)

 
## Server Configuration CRUD Operations

 `McpConfHelper` provides a complete set of operations for managing server configurations:

 **Configuration Operations Table**

 
| Operation | Method | Description |
|---|---|---|
| Read | getMcpServers() | Returns all server configs with automatic built-in server补充 and platform filtering |
| Create | addMcpServer(name, config) | Adds new server, unmarking if previously removed built-in |
| Update | updateMcpServer(name, config) | Partially updates existing server configuration |
| Delete | removeMcpServer(name) | Removes server, marking if built-in, also removes from default list |
| Reset | resetToDefaultServers() | Restores all built-in servers, removes all inmemory types |

 
### getMcpServers() Logic Flow

 The `getMcpServers()` method implements sophisticated logic to ensure consistency:

 
```

```

 Sources: [src/main/presenter/configPresenter/mcpConfHelper.ts381-451](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/configPresenter/mcpConfHelper.ts#L381-L451)

 
### Server Removal and Default List Management

 When removing a server, the system automatically cleans up the default server list:

 
```

```

 Sources: [src/main/presenter/configPresenter/mcpConfHelper.ts637-651](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/configPresenter/mcpConfHelper.ts#L637-L651)

 
## Default Server Management

 The `defaultServers` array specifies which servers should be started automatically when MCP is enabled. The system enforces a maximum of 30 default servers.

 **Default Server Operations**

 
| Method | Purpose | Max Limit |
|---|---|---|
| getMcpDefaultServers() | Returns array of default server names | N/A |
| addMcpDefaultServer(name) | Adds server to default list with validation | 30 |
| removeMcpDefaultServer(name) | Removes server from default list | N/A |
| toggleMcpDefaultServer(name) | Toggles server's default status | 30 |

 
### Default Server Validation

 When adding a server to the default list, `addMcpDefaultServer()` performs validation:

 
```

```

 Sources: [src/main/presenter/configPresenter/mcpConfHelper.ts469-507](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/configPresenter/mcpConfHelper.ts#L469-L507)

 
## NPM Registry Configuration

 For stdio-based MCP servers that use `npx` or `node` commands, `McpConfHelper` supports custom NPM registry configuration to optimize package installation speed and bypass network restrictions.

 **NPM Registry Resolution Priority**

 
```

```

 **NPM Registry Cache Structure**

 
```

```

 
### Registry Configuration Methods

 
| Method | Purpose |
|---|---|
| getCustomNpmRegistry() | Returns user-specified NPM registry URL |
| setCustomNpmRegistry(url) | Sets custom NPM registry (normalized with trailing slash) |
| getAutoDetectNpmRegistry() | Returns whether auto-detection is enabled |
| setAutoDetectNpmRegistry(enabled) | Toggles auto-detection |
| getNpmRegistryCache() | Returns cached registry info |
| setNpmRegistryCache(cache) | Updates registry cache |
| isNpmRegistryCacheValid() | Checks if cache is < 24 hours old |
| getEffectiveNpmRegistry() | Returns resolved registry URL based on priority |
| clearNpmRegistryCache() | Invalidates cache |

 The `ServerManager` uses `getEffectiveNpmRegistry()` when spawning stdio servers to determine which NPM registry to use for package installation.

 Sources: [src/main/presenter/configPresenter/mcpConfHelper.ts558-635](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/configPresenter/mcpConfHelper.ts#L558-L635)

 
## Platform-Specific Server Management

 The system automatically filters servers based on the runtime platform, ensuring that platform-specific servers (like `deepchat/apple-server`) are only available on supported operating systems.

 **Platform Detection and Filtering**

 
```

```

 Platform filtering occurs in multiple places:

 
 - **Definition time** - `PLATFORM_SPECIFIC_SERVERS` object only includes servers for the current platform [mcpConfHelper.ts62-110](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/mcpConfHelper.ts#L62-L110)
 - **Load time** - `getMcpServers()` removes servers not compatible with current platform [mcpConfHelper.ts409-431](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/mcpConfHelper.ts#L409-L431)
 - **Upgrade time** - `onUpgrade()` removes unsupported platform servers and adds newly supported ones [mcpConfHelper.ts948-996](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/mcpConfHelper.ts#L948-L996)
 
 Example: The `deepchat/apple-server` provides macOS system integration (Calendar, Contacts, Mail, Maps, Notes, Reminders) and is only available when `process.platform === 'darwin'`.

 Sources: [src/main/presenter/configPresenter/mcpConfHelper.ts48-110](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/configPresenter/mcpConfHelper.ts#L48-L110) [src/main/presenter/configPresenter/mcpConfHelper.ts409-431](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/configPresenter/mcpConfHelper.ts#L409-L431)

 
## Batch Import Functionality

 The `batchImportMcpServers()` method enables importing multiple MCP servers from external sources (like ModelScope marketplace) with conflict resolution and validation.

 **Batch Import Flow**

 
```

```

 **Import Options**

 
| Option | Type | Default | Description |
|---|---|---|---|
| skipExisting | boolean | true | Skip servers that already exist |
| enableByDefault | boolean | false | Add imported servers to default list |
| overwriteExisting | boolean | false | Overwrite existing servers with same package |

 **ExtendedMCPServerConfig** includes additional marketplace metadata:

 
```

```

 The `generateUniqueServerName()` helper creates collision-free names by sanitizing package names and appending numeric suffixes if needed.

 Sources: [src/main/presenter/configPresenter/mcpConfHelper.ts702-853](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/configPresenter/mcpConfHelper.ts#L702-L853)

 
## Version Migrations and Upgrades

 The `onUpgrade(oldVersion)` method handles configuration migrations when the application version changes. It uses `compare-versions` for semantic version comparison.

 **Migration Timeline**

 
```

```

 
### Key Migrations

 
 - **Version ≤ 0.0.12** - Migrate single `defaultServer` string to `defaultServers` array [mcpConfHelper.ts856-869](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/mcpConfHelper.ts#L856-L869)
 - **Version < 0.6.0** - Remove deprecated filesystem servers:

 
 - `filesystem` - Old filesystem MCP server
 - `buildInFileSystem` - Built-in filesystem server
 - Reason: Filesystem capabilities now provided via Agent tools
 - Mark as removed to prevent re-addition [mcpConfHelper.ts873-918](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/mcpConfHelper.ts#L873-L918)
 - **Version < 0.3.5** - Remove `deepchat-inmemory/custom-prompts-server`:

 
 - Custom prompts now provided via config data source
 - Remove from both `mcpServers` and `defaultServers` [mcpConfHelper.ts921-946](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/mcpConfHelper.ts#L921-L946)
 - **All upgrades** - Platform-specific server management:

 
 - Add platform-specific servers if missing (e.g., `deepchat/apple-server` on macOS)
 - Remove servers not supported on current platform
 - Update `defaultServers` list accordingly [mcpConfHelper.ts948-996](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/mcpConfHelper.ts#L948-L996)
 
 Sources: [src/main/presenter/configPresenter/mcpConfHelper.ts854-996](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/configPresenter/mcpConfHelper.ts#L854-L996)

 
## UI Integration

 The configuration UI is implemented in `mcpServerForm.vue`, which provides a comprehensive form for adding and editing MCP server configurations.

 **UI Configuration Flow**

 
```

```

 The form handles server-specific configurations:

 
 - **stdio servers** - Command, args, environment variables, optional custom NPM registry
 - **SSE/HTTP servers** - Base URL, custom headers (Key=Value format)
 - **inmemory servers** - Special handling per server type: 
 - `imageServer` - Model selection via `ModelSelect` component
 - `buildInFileSystem` - Folder selection with path list
 - `powerpack` - E2B configuration (API key, enable/disable)
 
 The form supports both JSON import and manual configuration workflows, with validation for each field type.

 Sources: [src/renderer/src/components/mcp-config/mcpServerForm.vue1-1556](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/mcp-config/mcpServerForm.vue#L1-L1556) [src/renderer/src/i18n/en-US/mcp.json84-137](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/i18n/en-US/mcp.json#L84-L137)

 
## Event Synchronization

 Configuration changes are propagated throughout the application via the `EventBus` using `MCP_EVENTS.CONFIG_CHANGED`:

 
```

```

 The event payload includes:

 
```

```

 This ensures that all parts of the application stay synchronized when configuration changes occur, including:

 
 - The settings UI updates to reflect new state
 - Running MCP servers reload their configurations
 - The MCP enabled/disabled state propagates to UI controls
 - Default server badges update in the server list
 
 Sources: [src/main/presenter/configPresenter/mcpConfHelper.ts456-461](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/configPresenter/mcpConfHelper.ts#L456-L461) [src/main/presenter/configPresenter/mcpConfHelper.ts501-506](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/configPresenter/mcpConfHelper.ts#L501-L506)
