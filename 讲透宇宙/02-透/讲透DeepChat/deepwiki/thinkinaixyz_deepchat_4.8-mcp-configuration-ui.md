> 来源: [https://deepwiki.com/thinkinaixyz/deepchat/4.8-mcp-configuration-ui](https://deepwiki.com/thinkinaixyz/deepchat/4.8-mcp-configuration-ui)（Wayback 快照 2026-03-06）
> DeepWiki deepchat/4.8-mcp-configuration-ui

# MCP Configuration UI

  Relevant source files 
 - [src/main/presenter/configPresenter/mcpConfHelper.ts](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/configPresenter/mcpConfHelper.ts)
 - [src/main/presenter/mcpPresenter/inMemoryServers/builder.ts](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/inMemoryServers/builder.ts)
 - [src/renderer/src/components/mcp-config/mcpServerForm.vue](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/mcp-config/mcpServerForm.vue)
 - [src/renderer/src/i18n/da-DK/settings.json](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/i18n/da-DK/settings.json)
 - [src/renderer/src/i18n/en-US/mcp.json](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/i18n/en-US/mcp.json)
 - [src/renderer/src/i18n/en-US/settings.json](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/i18n/en-US/settings.json)
 - [src/renderer/src/i18n/fa-IR/mcp.json](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/i18n/fa-IR/mcp.json)
 - [src/renderer/src/i18n/fa-IR/settings.json](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/i18n/fa-IR/settings.json)
 - [src/renderer/src/i18n/fr-FR/mcp.json](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/i18n/fr-FR/mcp.json)
 - [src/renderer/src/i18n/fr-FR/settings.json](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/i18n/fr-FR/settings.json)
 - [src/renderer/src/i18n/ja-JP/mcp.json](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/i18n/ja-JP/mcp.json)
 - [src/renderer/src/i18n/ja-JP/settings.json](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/i18n/ja-JP/settings.json)
 - [src/renderer/src/i18n/ko-KR/mcp.json](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/i18n/ko-KR/mcp.json)
 - [src/renderer/src/i18n/ko-KR/settings.json](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/i18n/ko-KR/settings.json)
 - [src/renderer/src/i18n/pt-BR/settings.json](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/i18n/pt-BR/settings.json)
 - [src/renderer/src/i18n/ru-RU/mcp.json](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/i18n/ru-RU/mcp.json)
 - [src/renderer/src/i18n/ru-RU/settings.json](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/i18n/ru-RU/settings.json)
 - [src/renderer/src/i18n/zh-CN/mcp.json](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/i18n/zh-CN/mcp.json)
 - [src/renderer/src/i18n/zh-CN/settings.json](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/i18n/zh-CN/settings.json)
 - [src/renderer/src/i18n/zh-HK/mcp.json](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/i18n/zh-HK/mcp.json)
 - [src/renderer/src/i18n/zh-HK/settings.json](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/i18n/zh-HK/settings.json)
 - [src/renderer/src/i18n/zh-TW/mcp.json](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/i18n/zh-TW/mcp.json)
 - [src/renderer/src/i18n/zh-TW/settings.json](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/i18n/zh-TW/settings.json)
 
  This document describes the MCP configuration user interface components that allow users to manage MCP server configurations through the DeepChat settings interface. The primary components are `mcpConfig.vue` (the settings tab page) and `mcpServerForm.vue` (the server configuration form dialog).

 The MCP settings UI integrates with `McpConfHelper` for configuration persistence and `McpPresenter` for server lifecycle management. For backend implementation details, see [MCP Configuration Management](https://deepwiki.com/thinkinaixyz/deepchat/4.7-mcp-configuration-management). For overall MCP architecture, see [MCP System Architecture](https://deepwiki.com/thinkinaixyz/deepchat/4.1-mcp-system-architecture).

 
---

 
## Settings Tab Structure

 The MCP configuration UI is accessed through the DeepChat settings interface under the "MCP" tab. The UI hierarchy follows the pattern established in the Settings System (see [Settings User Interface](https://deepwiki.com/thinkinaixyz/deepchat/3.4-settings-user-interface)).

 **MCP Settings Page Structure**

 
```

```

 **Sources:** [src/renderer/src/components/mcp-config/mcpServerForm.vue1-50](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/mcp-config/mcpServerForm.vue#L1-L50) [src/renderer/src/i18n/en-US/settings.json716-894](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/i18n/en-US/settings.json#L716-L894)

 
---

 
## Purpose and Features

 The MCP Configuration UI enables users to:

 
 - Enable/disable the MCP system globally
 - Add and edit MCP server configurations through a form-based interface
 - Import server configurations from JSON (single or batch)
 - Configure server-specific parameters based on transport type (stdio, SSE, HTTP, in-memory)
 - Set auto-approval permissions for tool execution
 - Manage environment variables and custom headers
 - Select vision models for image processing servers
 - Configure NPM registry for faster package installation
 - Browse MCP marketplaces for server discovery
 
 The form component validates all inputs before submission and interfaces with `McpConfHelper` for persistence and `McpPresenter` for server management.

 **Sources:** [src/renderer/src/components/mcp-config/mcpServerForm.vue1-100](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/mcp-config/mcpServerForm.vue#L1-L100) [src/main/presenter/configPresenter/mcpConfHelper.ts1-50](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/configPresenter/mcpConfHelper.ts#L1-L50)

 
---

 
## Component Architecture

 The MCP configuration UI consists of two main Vue 3 components using the Composition API: the settings tab page and the server configuration form dialog.

 **Component Hierarchy and Data Flow**

 
```

```

 **Key Components:**

 
 - **mcpConfig.vue**: Settings tab page displaying server list and actions
 - **mcpServerForm.vue**: Dialog form for adding/editing server configurations
 - **ConfigPresenter**: Main process presenter coordinating configuration operations
 - **McpConfHelper**: Helper class managing ElectronStore persistence
 
 **Sources:** [src/renderer/src/components/mcp-config/mcpServerForm.vue1-100](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/mcp-config/mcpServerForm.vue#L1-L100) [src/main/presenter/configPresenter/mcpConfHelper.ts1-100](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/configPresenter/mcpConfHelper.ts#L1-L100)

 
---

 
## Form Fields and Configuration

 The form adapts its fields based on the selected server type. Each MCP server type has different required and optional fields.

 **Server Type Configuration Matrix**

 
| Field | stdio | sse | http | inmemory |
|---|---|---|---|---|
| Name | ✓ Required | ✓ Required | ✓ Required | ✓ Required |
| Command | ✓ Required | ✗ | ✗ | ✓ Required |
| Base URL | ✗ | ✓ Required | ✓ Required | ✗ |
| Arguments | ✓ Optional | ✗ | ✗ | ✓ Optional |
| Environment | ✓ Optional | ✓ Optional | ✓ Optional | ✓ Optional |
| Custom Headers | ✗ | ✗ | ✓ Optional | ✗ |
| Auto-Approve | ✓ Optional | ✓ Optional | ✓ Optional | ✓ Optional |
| NPM Registry | ✓ Optional | ✗ | ✗ | ✗ |

 **Type-Specific Field Visibility Logic**

 
```

```

 **Sources:** [src/renderer/src/components/mcp-config/mcpServerForm.vue200-350](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/mcp-config/mcpServerForm.vue#L200-L350) [src/renderer/src/components/mcp-config/mcpServerForm.vue500-700](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/mcp-config/mcpServerForm.vue#L500-L700)

 
---

 
## JSON Configuration Import System

 The form supports importing server configurations from JSON, either single server or batch import of multiple servers.

 **JSON Import Flow Diagram**

 
```

```

 **Batch Import Conflict Handling**

 The batch import system detects naming conflicts and provides three resolution strategies:

 
 - **Overwrite**: Replace existing server configuration
 - **Skip**: Skip the conflicting server, keep existing
 - **Rename**: Auto-generate unique name with suffix (e.g., `server-name-2`)
 
 **Sources:** [src/renderer/src/components/mcp-config/mcpServerForm.vue170-250](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/mcp-config/mcpServerForm.vue#L170-L250) [src/renderer/src/components/mcp-config/mcpServerForm.vue750-850](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/mcp-config/mcpServerForm.vue#L750-L850)

 
---

 
## Validation Logic

 The form implements client-side validation for all fields before submission.

 **Validation Rules Implementation**

 
```

```

 **Validation Error Messages**

 The validation system displays localized error messages through the toast notification system:

 
 - `settings.mcp.serverForm.nameRequired`: Server name cannot be empty
 - `settings.mcp.serverForm.commandRequired`: Command field is required for stdio servers
 - `settings.mcp.serverForm.argsRequired`: Arguments must be valid array format
 - `settings.mcp.serverForm.envInvalid`: Environment variables must be valid JSON
 - `settings.mcp.serverForm.customHeadersParseError`: Custom headers must be valid JSON
 
 **Sources:** [src/renderer/src/components/mcp-config/mcpServerForm.vue900-1000](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/mcp-config/mcpServerForm.vue#L900-L1000) [src/renderer/src/i18n/en-US/settings.json751-820](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/i18n/en-US/settings.json#L751-L820)

 
---

 
## Type-Specific Field Visibility

 The form dynamically shows/hides fields based on the selected server type and special configurations.

 **Field Visibility Logic**

 
```

```

 **Computed Visibility Properties**

 The component uses computed properties to determine field visibility:

 
 - `isStdioType`: `computed(() => serverType.value === 'stdio')`
 - `isSseOrHttpType`: `computed(() => ['sse', 'http'].includes(serverType.value))`
 - `isHttpType`: `computed(() => serverType.value === 'http')`
 - `isInMemoryType`: `computed(() => serverType.value === 'inmemory')`
 - `isImageServer`: `computed(() => isInMemoryType.value && command.value === 'imageServer')`
 - `isPowerpack`: `computed(() => isInMemoryType.value && command.value === 'powerpack')`
 
 **Sources:** [src/renderer/src/components/mcp-config/mcpServerForm.vue100-200](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/mcp-config/mcpServerForm.vue#L100-L200) [src/renderer/src/components/mcp-config/mcpServerForm.vue350-500](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/mcp-config/mcpServerForm.vue#L350-L500)

 
---

 
## Special Configuration Features

 The form includes specialized configuration options for specific MCP server types.

 
### Vision Model Selection

 For `imageServer` (in-memory type), the form provides model selection for vision capabilities:

 
```

```

 **Sources:** [src/renderer/src/components/mcp-config/mcpServerForm.vue450-500](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/mcp-config/mcpServerForm.vue#L450-L500) [src/renderer/src/components/ModelSelect.vue1-100](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/ModelSelect.vue#L1-L100)

 
### E2B Sandbox Configuration

 For `powerpack` server, users can enable E2B sandbox for Python code execution:

 **E2B Configuration Fields:**

 
 - `useE2B`: Checkbox to enable E2B sandbox
 - `e2bApiKey`: Required API key field (shown when `useE2B` is checked)
 
 Validation ensures the API key is provided when E2B is enabled.

 **Sources:** [src/renderer/src/components/mcp-config/mcpServerForm.vue550-600](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/mcp-config/mcpServerForm.vue#L550-L600)

 
### Folder Access Configuration

 For filesystem servers, users can specify allowed directories:

 **Folder Configuration:**

 
 - `allowedFolders`: Array of folder paths
 - Add/Remove folder buttons
 - Native folder picker integration via `devicePresenter.selectFolder()`
 
 **Sources:** [src/renderer/src/components/mcp-config/mcpServerForm.vue600-650](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/mcp-config/mcpServerForm.vue#L600-L650)

 
### Auto-Approve Permissions

 All server types support auto-approve settings to bypass user confirmation for tool execution:

 **Auto-Approve Options:**

 
 - `all`: Auto-approve all tool operations
 - `read`: Auto-approve read-only operations
 - `write`: Auto-approve write operations
 - Multiple selections allowed via checkbox group
 
 **Sources:** [src/renderer/src/components/mcp-config/mcpServerForm.vue700-750](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/mcp-config/mcpServerForm.vue#L700-L750)

 
---

 
## Backend Integration

 The MCP configuration UI integrates with the main process through the ConfigPresenter and McpPresenter architecture established in [ConfigPresenter and Helper Architecture](https://deepwiki.com/thinkinaixyz/deepchat/3.1-configpresenter-and-helper-architecture).

 **Backend Integration Flow**

 
```

```

 **IPC Communication Flow:**

 The renderer process communicates with the main process using the presenter pattern:

 
 - **Renderer invokes**: `configPresenter.mcpConfHelper.addMcpServer(serverName, config)`
 - **IPC layer**: `ipcRenderer.invoke('config:mcpConfHelper:addMcpServer', serverName, config)`
 - **Main process handles**: `Presenter` routes to `ConfigPresenter.mcpConfHelper.addMcpServer()`
 - **Persistence**: `McpConfHelper` writes to `ElectronStore` with key `'mcp-settings'`
 - **Event broadcast**: `eventBus.emit(MCP_EVENTS.CONFIG_UPDATED, { serverName })`
 - **Server restart**: `McpPresenter` listens to event and restarts server if needed
 
 **Key Backend Methods in McpConfHelper:**

 
| Method | Purpose | Parameters |
|---|---|---|
| getMcpServers() | Get all server configurations | None |
| addMcpServer(name, config) | Add new server | name: string, config: MCPServerConfig |
| updateMcpServer(name, config) | Update existing server | name: string, config: MCPServerConfig |
| deleteMcpServer(name) | Delete server | name: string |
| setMcpEnabled(enabled) | Enable/disable MCP | enabled: boolean |
| setDefaultServers(servers) | Set default servers | servers: string[] |
| getNpmRegistryCache() | Get NPM registry cache | None |
| updateNpmRegistryCache(cache) | Update NPM registry | cache: INpmRegistryCache |

 **Sources:** [src/renderer/src/components/mcp-config/mcpServerForm.vue1000-1050](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/mcp-config/mcpServerForm.vue#L1000-L1050) [src/main/presenter/configPresenter/mcpConfHelper.ts200-600](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/configPresenter/mcpConfHelper.ts#L200-L600) [src/main/presenter/index.ts1-100](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/index.ts#L1-L100)

 
---

 
## Marketplace Integration

 The form provides quick access to MCP server marketplaces for discovering and installing servers.

 **Marketplace Links:**

 
 - **Official MCP Marketplace**: `https://github.com/modelcontextprotocol/servers`
 - **Higress MCP Marketplace**: Platform-specific MCP servers
 
 Users can browse these marketplaces, copy server JSON configurations, and paste them directly into the JSON import field for quick setup.

 **Marketplace Constants:**

 
 - `MCP_MARKETPLACE_URL`: `'https://github.com/modelcontextprotocol/servers'`
 - `HIGRESS_MCP_MARKETPLACE_URL`: Platform-specific Higress marketplace URL
 
 **Sources:** [src/renderer/src/components/mcp-config/mcpServerForm.vue24](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/mcp-config/mcpServerForm.vue#L24-L24) [src/renderer/src/components/mcp-config/const.ts1-10](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/mcp-config/const.ts#L1-L10)

 
---

 
## Internationalization

 The MCP configuration UI supports 11 languages with complete translations for all form fields, validation messages, and tooltips.

 **Supported Languages:**

 
 - English (`en-US`)
 - Simplified Chinese (`zh-CN`)
 - Traditional Chinese (`zh-TW`, `zh-HK`)
 - Japanese (`ja-JP`)
 - Korean (`ko-KR`)
 - French (`fr-FR`)
 - Russian (`ru-RU`)
 - Portuguese (`pt-BR`)
 - Persian (`fa-IR`)
 
 All UI strings are loaded from language-specific JSON files under the `settings.mcp.serverForm` namespace.

 **Sources:** [src/renderer/src/i18n/en-US/settings.json711-888](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/i18n/en-US/settings.json#L711-L888) [src/renderer/src/i18n/zh-CN/settings.json711-888](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/i18n/zh-CN/settings.json#L711-L888) [src/renderer/src/i18n/ja-JP/settings.json711-888](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/i18n/ja-JP/settings.json#L711-L888)
