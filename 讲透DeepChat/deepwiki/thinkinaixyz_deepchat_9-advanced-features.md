> 来源: [https://deepwiki.com/thinkinaixyz/deepchat/9-advanced-features](https://deepwiki.com/thinkinaixyz/deepchat/9-advanced-features)（Wayback 快照 2026-01-18）
> DeepWiki deepchat/9-advanced-features

# Advanced Features

  Relevant source files 
 - [electron.vite.config.ts](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/electron.vite.config.ts)
 - [src/main/presenter/deeplinkPresenter/index.ts](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/main/presenter/deeplinkPresenter/index.ts)
 - [src/main/presenter/llmProviderPresenter/providers/dashscopeProvider.ts](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/main/presenter/llmProviderPresenter/providers/dashscopeProvider.ts)
 - [src/main/presenter/llmProviderPresenter/providers/zhipuProvider.ts](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/main/presenter/llmProviderPresenter/providers/zhipuProvider.ts)
 - [src/main/presenter/tabPresenter.ts](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/main/presenter/tabPresenter.ts)
 - [src/main/presenter/windowPresenter/index.ts](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/main/presenter/windowPresenter/index.ts)
 - [src/renderer/shell/App.vue](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/renderer/shell/App.vue)
 - [src/renderer/shell/components/AppBar.vue](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/renderer/shell/components/AppBar.vue)
 - [src/renderer/shell/components/app-bar/AppBarTabItem.vue](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/renderer/shell/components/app-bar/AppBarTabItem.vue)
 - [src/renderer/src/components/ChatConfig.vue](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/renderer/src/components/ChatConfig.vue)
 - [src/renderer/src/components/ModelSelect.vue](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/renderer/src/components/ModelSelect.vue)
 - [src/renderer/src/components/NewThread.vue](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/renderer/src/components/NewThread.vue)
 - [src/renderer/src/components/TitleView.vue](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/renderer/src/components/TitleView.vue)
 - [src/renderer/src/components/settings/ModelConfigDialog.vue](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/renderer/src/components/settings/ModelConfigDialog.vue)
 - [src/renderer/src/views/SettingsTabView.vue](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/renderer/src/views/SettingsTabView.vue)
 
  This document covers specialized features and advanced functionality in DeepChat that extend beyond core chat and model management capabilities. These features enable external integration, data management, sandboxed browsing, network configuration, and security hardening.

 For basic configuration and settings, see [Configuration and Settings System](https://deepwiki.com/thinkinaixyz/deepchat/3-configuration-and-settings-system). For MCP tool integration, see [Model Context Protocol (MCP)](https://deepwiki.com/thinkinaixyz/deepchat/6-model-context-protocol-(mcp)). For ACP agent integration details, see the ACP subsection in settings.

 
---

 
## Purpose and Scope

 Advanced features documented here include:

 
 - **DeepLink Protocol** ([9.1](https://deepwiki.com/thinkinaixyz/deepchat/9.1-deeplink-protocol)): External application integration via `deepchat://` URLs
 - **Data Synchronization and Backup** ([9.2](https://deepwiki.com/thinkinaixyz/deepchat/9.2-data-synchronization-and-backup)): Data export, import, and incremental sync
 - **Proxy Configuration** ([9.3](https://deepwiki.com/thinkinaixyz/deepchat/9.3-proxy-configuration)): Network proxy settings and custom proxy support
 
 These features enable external tool integration, data portability across devices, and network configuration for restrictive environments.

 
---

 
## 9.1 DeepLink Protocol

 DeepChat implements a custom URL protocol handler (`deepchat://`) through `DeeplinkPresenter` to enable external applications to trigger actions. This allows browser extensions, CLI tools, and other applications to initiate chats or install MCP servers programmatically.

 
### Protocol Registration and Lifecycle

 **DeepLink Processing Flow**

 
```

```

 **Implementation Details**

 The `DeeplinkPresenter` handles three launch scenarios:

 
 - **Cold Start**: DeepLink URL passed as command-line argument 
 - Parsed from `process.argv` or `process.env.STARTUP_DEEPLINK`
 - Stored in `startupUrl` until window is ready
 - **Warm Start**: DeepLink received while app is running 
 - macOS: `app.on('open-url')` event
 - Windows/Linux: `app.on('second-instance')` event
 - **Pending Processing**: DeepLinks requiring subsystem initialization 
 - Start actions wait for `WINDOW_EVENTS.FIRST_CONTENT_LOADED`
 - MCP install waits for `MCP_EVENTS.INITIALIZED`
 
 Sources: [src/main/presenter/deeplinkPresenter/index.ts33-118](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/main/presenter/deeplinkPresenter/index.ts#L33-L118) [src/main/events.ts149-153](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/main/events.ts#L149-L153)

 
### Start Command

 **URL Format**: `deepchat://start?msg={encodedText}&model={modelId}&system={systemPrompt}&mentions={mention1,mention2}`

 **Parameters**:

 
| Parameter | Type | Required | Description |
|---|---|---|---|
| msg | string | Yes | URL-encoded message content |
| model | string | No | Model ID or name for fuzzy matching |
| system | string | No | System prompt override |
| mentions | string | No | Comma-separated mention IDs |

 **Processing Flow**:

 
```

```

 **Security Measures**:

 The `handleStart` method implements multiple sanitization layers:

 
 - `sanitizeMessageContent()`: Removes dangerous HTML/JS patterns
 - `sanitizeStringParameter()`: Strips protocol handlers and event attributes
 - Auto-send disabled: `yolo` parameter removed for security
 - Content length limit: 50KB maximum
 
 Rejected patterns include `<script>`, `javascript:`, event handlers (`on*=`), and other XSS vectors.

 Sources: [src/main/presenter/deeplinkPresenter/index.ts215-277](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/main/presenter/deeplinkPresenter/index.ts#L215-L277) [src/main/presenter/deeplinkPresenter/index.ts567-664](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/main/presenter/deeplinkPresenter/index.ts#L567-L664)

 
### MCP Install Command

 **URL Format**: `deepchat://mcp/install?code={base64JSON}`

 **Parameters**:

 
| Parameter | Type | Required | Description |
|---|---|---|---|
| code | string | Yes | Base64-encoded JSON containing mcpServers object |

 **Configuration Schema**:

 
```

```

 **Type Inference Logic**:

 
 - Explicit `type` field takes precedence
 - If `type` missing: 
 - Has `command` → infer `stdio`
 - Has `url` → infer `sse`
 - Both present → error (must specify type)
 - Neither present → error (must provide command or url)
 
 **Processing Flow**:

 The `handleMcpInstall` method:

 
 - Decodes base64 `code` parameter
 - Validates server configurations
 - Determines transport type (stdio vs SSE)
 - Merges with default configuration (icons, autoApprove, etc.)
 - Stores complete config in Settings window localStorage as `pending-mcp-install`
 - Settings UI detects stored config and displays installation dialog
 
 For cold start scenarios (no windows open), config is stored in the first shell window's localStorage.

 Sources: [src/main/presenter/deeplinkPresenter/index.ts338-500](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/main/presenter/deeplinkPresenter/index.ts#L338-L500) [src/main/presenter/deeplinkPresenter/index.ts506-565](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/main/presenter/deeplinkPresenter/index.ts#L506-L565)

 
### Tab Management for DeepLinks

 The `ensureChatTabActive()` method ensures DeepLink actions target an active chat tab:

 
 - Searches for existing chat tab (`url === 'local://chat'`)
 - Switches to chat tab if found but inactive
 - Creates new chat tab if none exists
 - Waits for tab renderer ready via `TAB_EVENTS.RENDERER_TAB_READY`
 
 This prevents DeepLinks from being lost when chat tab is not currently visible.

 Sources: [src/main/presenter/deeplinkPresenter/index.ts279-336](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/main/presenter/deeplinkPresenter/index.ts#L279-L336)

 
---

 
## 9.2 Data Synchronization and Backup

 DeepChat provides data management features for backup snapshots, import/export, and cross-device synchronization through the Settings interface.

 
### Backup Architecture

 **Backup Data Flow**

 
```

```

 **Backup Components**

 Backups include:

 
 - **conversations.db**: SQLite database containing all messages, threads, and conversation metadata
 - **app-settings.json**: ElectronStore configuration including provider credentials, model settings, and UI preferences
 - **Knowledge Base Files**: DuckDB vector stores with embedded document chunks
 - **Cache Files**: Optional inclusion of temporary data and runtime caches
 
 Sources: Settings UI implementation

 
### Backup Operations

 **Creating Backups**

 Backups are initiated through Settings → Data Management → Backup. The system creates a timestamped folder containing snapshots of all data sources.

 
| Setting | Description |
|---|---|
| startBackup | Trigger manual backup creation |
| syncFolder | Configure target directory for backups |
| openSyncFolder | Open backup location in file manager |
| backingUp | Progress indicator during backup operation |

 **Importing Backups**

 Two import modes control how backup data is merged:

 
 - **Incremental Import** (`incrementImport`): Merges backup data with existing data, preserving records not in the backup
 - **Overwrite Import** (`overwriteImport`): Replaces all current data with backup snapshot
 
 Import flow:

 
 - Select backup from `backupSelectLabel` dropdown (lists timestamped snapshots)
 - Choose import mode
 - Confirm via `importConfirmTitle` dialog
 - Application restarts to load imported data
 
 Sources: Settings UI backup section

 
### Data Reset Operations

 Selective reset options allow targeted data deletion:

 
| Reset Type | Scope | Restart Required |
|---|---|---|
| resetChatData | Delete all conversations and message history | Yes |
| resetKnowledgeData | Delete knowledge base vector stores and files | Yes |
| resetConfig | Reset app settings, model configs, system prompts | Yes |
| resetAll | Complete data deletion including cache | Yes |

 All reset operations trigger automatic application restart to ensure clean state initialization and prevent stale data references.

 Sources: Settings UI data management section

 
### Sync Folder Configuration

 The sync folder enables cross-device synchronization by storing backups in a cloud-synced directory (Dropbox, OneDrive, iCloud Drive, etc.).

 Configuration:

 
 - **Location**: User-selectable folder path
 - **Automatic Sync**: Optional (`syncEnable` toggle)
 - **Last Sync Time**: Displays timestamp of most recent backup (`lastSyncTime`)
 
 Backup snapshots are organized by timestamp, allowing version history and rollback capabilities.

 Sources: Settings UI sync configuration

 
## 9.3 Proxy Configuration

 DeepChat implements a global proxy system through the `ProxyConfig` class that supports three modes: system proxy detection, no proxy, and custom proxy URLs. Proxy settings apply to all HTTP/HTTPS network requests including LLM API calls, MCP server communications, and web content fetching.

 
### ProxyConfig Architecture

 **Proxy System Components**

 
```

```

 **Proxy Mode Enum**

 The `ProxyMode` enum defines three operational modes:

 
```

```

 Sources: [src/main/presenter/proxyConfig.ts7-11](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/main/presenter/proxyConfig.ts#L7-L11)

 
### Proxy Mode Implementation

 **SYSTEM Mode**

 When `ProxyMode.SYSTEM` is active:

 
 - `session.defaultSession.setProxy({ mode: 'system' })` enables OS proxy detection
 - `resolveProxy('https://www.google.com')` tests proxy resolution
 - Detected proxy URL is stored in `process.env.http_proxy`, `process.env.https_proxy`, etc.
 - `EnvHttpProxyAgent` from `undici` applies environment variable settings globally
 
 Sources: [src/main/presenter/proxyConfig.ts71-94](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/main/presenter/proxyConfig.ts#L71-L94)

 **NONE Mode**

 When `ProxyMode.NONE` is active:

 
 - `clearProxy()` deletes all `process.env` proxy variables
 - `session.defaultSession.setProxy({ mode: 'direct' })` bypasses proxy
 - `setGlobalDispatcher(new Agent())` configures undici for direct connections
 
 Sources: [src/main/presenter/proxyConfig.ts102-114](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/main/presenter/proxyConfig.ts#L102-L114)

 **CUSTOM Mode**

 When `ProxyMode.CUSTOM` is active:

 
 - User-provided proxy URL is validated via `isValidProxyUrl()`
 - Valid URL is stored in `process.env` variables
 - `session.defaultSession.setProxy({ proxyRules: proxyUrl })` applies to Electron
 - `EnvHttpProxyAgent` configured with custom URL
 
 Sources: [src/main/presenter/proxyConfig.ts116-135](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/main/presenter/proxyConfig.ts#L116-L135)

 
### Custom Proxy URL Validation

 The `isValidProxyUrl()` method enforces URL format requirements:

 **Valid Formats**

 
 - `http://hostname:port`
 - `https://hostname:port`
 - `http://username:password@hostname:port`
 
 **Validation Rules**

 
 - Must start with `http://` or `https://`
 - Hostname must be valid domain or IP address
 - Port number must be numeric if specified
 - URL must be parseable by `new URL()`
 
 Invalid URLs are rejected with fallback to `ProxyMode.SYSTEM`.

 Sources: [src/main/presenter/proxyConfig.ts142-167](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/main/presenter/proxyConfig.ts#L142-L167)

 
### No-Proxy Configuration

 The `NO_PROXY` constant defines hosts that bypass proxy:

 
```

```

 The `mergeNoProxy()` function combines this default list with system-level `no_proxy` environment variables, ensuring local development servers and internal network hosts are never proxied.

 Sources: [src/main/presenter/proxyConfig.ts12-32](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/main/presenter/proxyConfig.ts#L12-L32)

 
### Event-Driven Proxy Updates

 Proxy configuration changes trigger event-based updates:

 **Configuration Change Flow**

 
```

```

 Event listeners are registered in the `ProxyConfig` constructor:

 
 - `CONFIG_EVENTS.PROXY_MODE_CHANGED`: Updates proxy mode and re-resolves
 - `CONFIG_EVENTS.CUSTOM_PROXY_URL_CHANGED`: Updates custom URL and re-applies if in custom mode
 
 Sources: [src/main/presenter/proxyConfig.ts42-54](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/main/presenter/proxyConfig.ts#L42-L54)

 
### Proxy Application Scope

 Proxy settings affect all network operations:

 
| Component | Affected Operations |
|---|---|
| LLMProviderPresenter | API calls to OpenAI, Anthropic, Gemini, Ollama, etc. |
| McpPresenter | HTTP/SSE transport MCP server connections, NPM registry access |
| FilePresenter | Remote file downloads, URL content fetching |
| Electron Updater | Application update checks and downloads |
| Web Scraping | PowerPack web scraper tool HTTP requests |

 Proxy configuration is applied through:

 
 - **Node.js native modules**: `process.env.http_proxy` / `process.env.https_proxy`
 - **undici**: `EnvHttpProxyAgent` global dispatcher
 - **Electron**: `session.defaultSession.setProxy()`
 
 Sources: [src/main/presenter/proxyConfig.ts1-209](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/main/presenter/proxyConfig.ts#L1-L209)

 
### Initialization and Defaults

 The `ProxyConfig` instance is initialized at application startup:

 
```

```

 Default mode is `ProxyMode.SYSTEM`. The `initFromConfig()` method loads persisted settings from ElectronStore and applies them:

 
```

```

 Sources: [src/main/presenter/proxyConfig.ts195-207](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/main/presenter/proxyConfig.ts#L195-L207) [src/main/presenter/proxyConfig.ts209](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/main/presenter/proxyConfig.ts#L209-L209)

 
---

 
## Security Features

 DeepChat implements several security features to protect user privacy and control data collection.

 
### Security Architecture

 
```

```

 **Security Feature Categories**

 Sources: [src/renderer/src/i18n/en-US/settings.json39-65](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/renderer/src/i18n/en-US/settings.json#L39-L65)

 
### Content Protection

 **Screen Capture Prevention**: Prevents screen sharing software from capturing the DeepChat main window.

 Settings:

 
 - `contentProtection`: Toggle screen capture protection
 - `contentProtectionEnableDesc`: Description of protection behavior
 - `contentProtectionRestartNotice`: Warning that app will restart
 
 Limitations:

 
 - Not all screen sharing applications honor this setting
 - Some environments may leave a black window artifact
 - Platform-dependent implementation
 
 When enabled, DeepChat sets window flags to prevent capture by recording software, protecting sensitive conversation data from inadvertent sharing during screen recordings or presentations.

 Sources: [src/renderer/src/i18n/en-US/settings.json39-42](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/renderer/src/i18n/en-US/settings.json#L39-L42)

 
### Logging Controls

 DeepChat provides configurable logging to balance diagnostics with privacy:

 Settings:

 
 - `loggingEnabled`: Toggle application logging
 - `loggingEnableDesc`: Warning that logs may contain sensitive information
 - `loggingDisableDesc`: Explanation that logging stops data collection
 - `loggingRestartNotice`: App restart required
 - `openLogFolder`: Open log directory in file manager
 
 Logging considerations:

 
 - Log files may contain API keys, conversation content, or personal data
 - Useful for debugging but should be disabled for maximum privacy
 - Changing setting triggers application restart
 
 Sources: [src/renderer/src/i18n/en-US/settings.json46-55](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/renderer/src/i18n/en-US/settings.json#L46-L55)

 
### MCP Tool Permission System

 MCP tools can request file system access, shell execution, or network operations. DeepChat implements a permission system to control these capabilities:

 **Auto-Approve Options** (from MCP server configuration):

 
 - `autoApproveAll`: Automatically approve all tool operations
 - `autoApproveRead`: Automatically approve read-only operations
 - `autoApproveWrite`: Automatically approve write operations
 - Manual approval: Prompt user for each operation
 
 The `PowerpackServer` demonstrates security-conscious tool implementation:

 
 - Shell execution tools default to requiring approval
 - File system access can be restricted to specific folders
 - Web scraping respects content length limits
 
 Sources: [src/renderer/src/i18n/en-US/settings.json39-65](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/renderer/src/i18n/en-US/settings.json#L39-L65) [src/main/presenter/mcpPresenter/inMemoryServers/powerpackServer.ts1-50](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/main/presenter/mcpPresenter/inMemoryServers/powerpackServer.ts#L1-L50)

 
### File Upload and Content Limits

 DeepChat enforces resource limits to prevent abuse and manage memory:

 **File Upload Limits**:

 
 - `fileMaxSize`: Maximum upload size per file
 - `fileMaxSizeHint`: Description of limit purpose
 
 **Web Content Limits**:

 
 - `webContentLengthLimit`: Maximum characters extracted from web pages (range: 0-50000)
 - `webContentLengthLimitHint`: Set to 0 for unlimited
 - `webContentLengthLimitTooltip`: Explanation of trade-offs (completeness vs. token cost)
 
 These limits apply to:

 
 - File attachments in chat messages
 - Web scraping operations via PowerPack `web_scraper` tool
 - Content enrichment for URLs shared in conversations
 
 Sources: [src/renderer/src/i18n/en-US/settings.json50-65](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/renderer/src/i18n/en-US/settings.json#L50-L65)

 
---

 
## Additional Advanced Features

 
### Trace Debug Mode

 Settings:

 
 - `traceDebugEnabled`: Toggle trace call debugging
 
 Enables detailed debugging output for diagnosing complex issues in LLM provider integrations, MCP server communications, and agent protocol operations.

 
### Sound Effects

 Settings:

 
 - `soundEnabled`: Toggle audio feedback
 
 Provides auditory notification when AI responses complete, useful when DeepChat is in background.

 
### COT Information Copying

 Settings:

 
 - `copyWithCotEnabled`: Include Chain-of-Thought details when copying
 
 When enabled, copying AI responses includes reasoning traces and intermediate thinking steps (for models that support native reasoning like o1 series).

 Sources: [src/renderer/src/i18n/en-US/settings.json43-46](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/renderer/src/i18n/en-US/settings.json#L43-L46)

 
---

 
## Summary

 DeepChat's advanced features enable:

 
 - **External Integration**: DeepLink protocol for browser extensions and CLI tools
 - **Data Portability**: Backup, import, and sync capabilities for cross-device workflows
 - **Secure Browsing**: YoBrowser sandbox for isolated web operations
 - **Network Flexibility**: Configurable proxy support for restrictive networks
 - **Privacy Controls**: Content protection, logging management, and permission systems
 
 These features transform DeepChat from a simple chat client into a comprehensive AI agent platform with enterprise-grade security and flexibility.
