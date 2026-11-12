> 来源: [https://deepwiki.com/thinkinaixyz/deepchat/1.2-application-architecture-overview](https://deepwiki.com/thinkinaixyz/deepchat/1.2-application-architecture-overview)（Wayback 快照 2026-01-20）
> DeepWiki deepchat/1.2-application-architecture-overview

# Application Architecture Overview

  Relevant source files 
 - [electron.vite.config.ts](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/electron.vite.config.ts)
 - [package.json](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/package.json)
 - [src/main/events.ts](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/main/events.ts)
 - [src/main/presenter/configPresenter/index.ts](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/main/presenter/configPresenter/index.ts)
 - [src/main/presenter/index.ts](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/main/presenter/index.ts)
 - [src/main/presenter/mcpPresenter/index.ts](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/main/presenter/mcpPresenter/index.ts)
 - [src/main/presenter/mcpPresenter/mcpClient.ts](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/main/presenter/mcpPresenter/mcpClient.ts)
 - [src/main/presenter/mcpPresenter/serverManager.ts](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/main/presenter/mcpPresenter/serverManager.ts)
 - [src/main/presenter/mcpPresenter/toolManager.ts](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/main/presenter/mcpPresenter/toolManager.ts)
 - [src/main/presenter/tabPresenter.ts](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/main/presenter/tabPresenter.ts)
 - [src/main/presenter/windowPresenter/index.ts](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/main/presenter/windowPresenter/index.ts)
 - [src/renderer/shell/App.vue](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/renderer/shell/App.vue)
 - [src/renderer/shell/components/AppBar.vue](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/renderer/shell/components/AppBar.vue)
 - [src/renderer/shell/components/app-bar/AppBarTabItem.vue](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/renderer/shell/components/app-bar/AppBarTabItem.vue)
 - [src/renderer/src/events.ts](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/renderer/src/events.ts)
 - [src/renderer/src/main.ts](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/renderer/src/main.ts)
 - [src/renderer/src/stores/mcp.ts](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/renderer/src/stores/mcp.ts)
 - [src/renderer/src/views/SettingsTabView.vue](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/renderer/src/views/SettingsTabView.vue)
 - [src/shared/presenter.d.ts](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/shared/presenter.d.ts)
 
  
## Purpose and Scope

 This document provides a high-level overview of DeepChat's application architecture, explaining how the Electron framework structures the codebase into separate processes, how components communicate, and where major subsystems reside. For installation instructions, see [Installation and Setup](https://deepwiki.com/thinkinaixyz/deepchat/1.1-installation-and-setup). For details on the build system and dependencies, see [Build System and Dependencies](https://deepwiki.com/thinkinaixyz/deepchat/1.3-build-system-and-dependencies). For deep dives into specific architectural patterns like the Presenter pattern and IPC communication, see [Presenter Pattern and IPC Communication](https://deepwiki.com/thinkinaixyz/deepchat/2.1-presenter-pattern-and-ipc-communication).

 
---

 
## Electron Multi-Process Architecture

 DeepChat is built on Electron, which separates application logic into two distinct process types: a **Main Process** running in Node.js and one or more **Renderer Processes** running Chromium-based web views. This architecture provides security isolation and enables native OS integration while maintaining a modern web-based UI.

 
### Process Separation

 
```

```

 **Sources:** [src/main/index.ts](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/main/index.ts) [src/main/presenter/index.ts70-294](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/main/presenter/index.ts#L70-L294) [src/renderer/src/main.ts1-76](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/renderer/src/main.ts#L1-L76) [src/preload/index.ts](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/preload/index.ts) [electron.vite.config.ts1-120](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/electron.vite.config.ts#L1-L120)

 
### Main Process Responsibilities

 The Main Process serves as the application's backend, handling:

 
| Responsibility | Implementation |
|---|---|
| Application Lifecycle | app.on() event handlers in main/index.ts |
| Window Management | WindowPresenter manages BrowserWindow instances |
| Tab Management | TabPresenter manages WebContentsView instances |
| Native OS Integration | File system, dialogs, notifications, system tray |
| Database Operations | SQLite connections via SQLitePresenter |
| External API Calls | LLM provider integrations, MCP server connections |
| Business Logic | Coordinated by 15+ specialized Presenter classes |

 The Main Process runs continuously from application start to quit and has full access to Node.js APIs and native modules.

 **Sources:** [src/main/index.ts](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/main/index.ts) [src/main/presenter/windowPresenter](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/main/presenter/windowPresenter) [src/main/presenter/tabPresenter](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/main/presenter/tabPresenter)

 
### Renderer Process Responsibilities

 Each Renderer Process runs an isolated Vue.js application responsible for:

 
| Responsibility | Implementation |
|---|---|
| User Interface | Vue 3 Single File Components |
| Client-Side State | Pinia stores (chatStore, modelStore, etc.) |
| Routing | Vue Router for navigation |
| User Input | Forms, chat input, file uploads |
| Real-time Updates | Event listeners for IPC messages |
| Markdown Rendering | MarkdownRenderer.vue with custom nodes |

 Each window in DeepChat (main window, settings window, floating button) runs its own Renderer Process with a separate JavaScript context.

 **Sources:** [src/renderer/src/main.ts1-76](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/renderer/src/main.ts#L1-L76) [src/renderer/src/App.vue](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/renderer/src/App.vue) [src/renderer/src/components/markdown/MarkdownRenderer.vue1-220](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/renderer/src/components/markdown/MarkdownRenderer.vue#L1-L220)

 
---

 
## Main Process Architecture

 
### Presenter Coordination Pattern

 The Main Process uses a **Presenter pattern** where a root `Presenter` class (defined in `src/main/presenter/index.ts`) coordinates specialized presenter instances. The singleton is exported as `presenter` and accessed throughout the Main Process via `import { presenter } from '@/presenter'`.

 **Presenter Instance Map**

 
```

```

 The `Presenter` class constructor instantiates all presenters in a specific order to handle dependencies. For example, `WindowPresenter` requires `ConfigPresenter`, so configuration is initialized first. The lifecycle is managed by `LifecycleManager`, which ensures database and configuration are ready before presenter initialization.

 **Sources:** [src/main/presenter/index.ts75-194](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/main/presenter/index.ts#L75-L194) [src/main/index.ts](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/main/index.ts)

 
### Key Presenter Responsibilities

 
| Presenter Instance | Class | File Path | Primary Responsibility |
|---|---|---|---|
| presenter.configPresenter | ConfigPresenter | presenter/configPresenter/index.ts | Settings persistence via ElectronStore, provider configuration, model metadata |
| presenter.windowPresenter | WindowPresenter | presenter/windowPresenter/index.ts | BrowserWindow creation, lifecycle, and multi-window management |
| presenter.tabPresenter | TabPresenter | presenter/tabPresenter.ts | WebContentsView tab management within windows, drag-and-drop reordering |
| presenter.llmproviderPresenter | LLMProviderPresenter | presenter/llmProviderPresenter/index.ts | LLM provider instance management (40+ providers), streaming response coordination |
| presenter.sessionPresenter | SessionPresenter | presenter/sessionPresenter/index.ts | Thread/conversation CRUD, message persistence to SQLite |
| presenter.mcpPresenter | McpPresenter | presenter/mcpPresenter/index.ts | MCP server lifecycle, tool discovery via ToolManager, resource/prompt access |
| presenter.knowledgePresenter | KnowledgePresenter | presenter/knowledgePresenter/index.ts | Multi-KB orchestration, DuckDB vector storage, embedding task queue |
| presenter.filePresenter | FilePresenter | presenter/filePresenter/FilePresenter.ts | File adapter pattern by MIME type, thumbnail generation, content extraction |
| presenter.agentPresenter | AgentPresenter | presenter/agentPresenter/index.ts | ACP agent message generation, session mode management via SessionManager |
| presenter.workspacePresenter | WorkspacePresenter | presenter/workspacePresenter/index.ts | Workspace state (plan entries, file tree, terminal output) for agent workflows |
| presenter.toolPresenter | ToolPresenter | presenter/toolPresenter/index.ts | Unified tool routing between MCP tools and agent tools, permission handling |

 **Sources:** [src/main/presenter/index.ts79-193](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/main/presenter/index.ts#L79-L193) [src/main/presenter/configPresenter/index.ts101-250](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/main/presenter/configPresenter/index.ts#L101-L250) [src/main/presenter/windowPresenter/index.ts21-47](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/main/presenter/windowPresenter/index.ts#L21-L47) [src/main/presenter/tabPresenter.ts16-45](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/main/presenter/tabPresenter.ts#L16-L45)

 
### Configuration Management

 `ConfigPresenter` delegates domain-specific configuration to helper classes, each managing a subset of the `ElectronStore` or separate storage:

 **Configuration Helper Architecture**

 
```

```

 
| Helper Class | Responsibility | Key Methods |
|---|---|---|
| ProviderHelper | LLM provider CRUD operations | getProviders(), updateProviderAtomic(), updateProvidersBatch() |
| ModelConfigHelper | Per-model parameter overrides | getModelConfig(), setModelConfig(), migration logic |
| ModelStatusHelper | Model enable/disable state | getModelStatus(), batchSetModelStatus(), caching |
| ProviderModelHelper | Provider model list management | getProviderModels(), addCustomModel() |
| McpConfHelper | MCP server configuration | getMcpServers(), addMcpServer(), getMcpDefaultServers() |
| AcpConfHelper | ACP agent configuration | getAcpAgents(), syncAcpProviderEnabled() |
| KnowledgeConfHelper | Knowledge base settings | getKnowledgeBases(), addKnowledgeBase() |
| UiSettingsHelper | UI preferences | getSearchPreviewEnabled(), setFontFamily() |
| SystemPromptHelper | System prompt management | getSystemPrompts(), getDefaultSystemPrompt() |

 All helpers trigger `CONFIG_EVENTS.*` events via `eventBus.sendToMain()` or `eventBus.send()` when configuration changes, enabling reactive updates across the application.

 **Sources:** [src/main/presenter/configPresenter/index.ts101-250](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/main/presenter/configPresenter/index.ts#L101-L250) [src/main/presenter/configPresenter/providerHelper.ts](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/main/presenter/configPresenter/providerHelper.ts) [src/main/presenter/configPresenter/modelConfig.ts](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/main/presenter/configPresenter/modelConfig.ts) [src/main/presenter/configPresenter/mcpConfHelper.ts](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/main/presenter/configPresenter/mcpConfHelper.ts)

 
---

 
## Renderer Process Architecture

 
### Vue Application Structure

 The Renderer Process uses Vue 3 with Composition API, organized into:

 
```

```

 **Sources:** [src/renderer/src/main.ts1-76](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/renderer/src/main.ts#L1-L76) [src/renderer/src/App.vue](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/renderer/src/App.vue) [src/renderer/src/router/index.ts](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/renderer/src/router/index.ts)

 
### Pinia Store Architecture

 Pinia stores coordinate renderer state and IPC calls to Main Process presenters. Store definitions use `defineStore()` from Pinia with composition API style.

 **Store-to-Presenter Communication**

 
```

```

 
| Store Function | File Path | Key State | IPC Target Presenter | Example Methods |
|---|---|---|---|---|
| useChatStore() | stores/chat.ts | activeThread, messages, streaming | sessionPresenter, agentPresenter | sendMessage(), retryMessage(), loadMessages() |
| useModelStore() | stores/model.ts | providers, models, enabledModels | configPresenter | fetchModels(), setModelStatus() |
| useMcpStore() | stores/mcp.ts | config.mcpServers, tools, clients, prompts | mcpPresenter, configPresenter | startServer(), callTool(), loadPrompts() |
| useWorkspaceStore() | stores/workspace.ts | planEntries, files, terminalOutput | workspacePresenter | updatePlan(), updateFiles() |
| useArtifactStore() | stores/artifact.ts | artifacts, activeArtifactId | N/A (renderer-only) | showArtifact(), closeArtifact() |
| useThemeStore() | stores/theme.ts | theme, systemTheme | N/A (renderer-only) | setTheme(), toggleTheme() |

 The `usePresenter()` composable returns a reactive proxy that wraps `window.api.presenter.call()`, providing typed access to Main Process methods. The `@pinia/colada` plugin provides `useQuery` and `useMutation` for managing async IPC calls with caching and loading states.

 **Sources:** [src/renderer/src/stores/chat.ts](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/renderer/src/stores/chat.ts) [src/renderer/src/stores/model.ts](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/renderer/src/stores/model.ts) [src/renderer/src/stores/mcp.ts25-310](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/renderer/src/stores/mcp.ts#L25-L310) [src/renderer/src/composables/usePresenter.ts](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/renderer/src/composables/usePresenter.ts)

 
---

 
## Communication Patterns

 
### IPC Communication Flow

 The `presenter:call` IPC channel provides a unified interface for Renderer-to-Main communication:

 
```

```

 The handler dynamically dispatches to the appropriate presenter method based on string names:

 
```

```

 **Sources:** [src/main/presenter/index.ts313-371](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/main/presenter/index.ts#L313-L371) [src/preload/index.ts](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/preload/index.ts) [src/renderer/src/composables/usePresenter.ts](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/renderer/src/composables/usePresenter.ts)

 
### Event System

 The `EventBus` singleton (exported from `src/main/eventbus/index.ts`) provides pub/sub across Main and Renderer processes. Presenters emit events using `eventBus.send()` or `eventBus.sendToMain()`, and the bus routes them to subscribed listeners based on `SendTarget`.

 **EventBus Message Routing**

 
```

```

 **Event Domain Constants**

 All events are defined as constant objects in `src/main/events.ts` (Main) and `src/renderer/src/events.ts` (Renderer):

 
| Event Domain | Constant Object | Example Events | Emitted By |
|---|---|---|---|
| Configuration | CONFIG_EVENTS | PROVIDER_CHANGED, MODEL_STATUS_CHANGED, LANGUAGE_CHANGED | ConfigPresenter, helpers |
| Conversations | CONVERSATION_EVENTS | LIST_UPDATED, ACTIVATED, MESSAGE_EDITED | SessionPresenter |
| Streaming | STREAM_EVENTS | RESPONSE, END, ERROR | LLMProviderPresenter, AgentPresenter |
| MCP Servers | MCP_EVENTS | SERVER_STARTED, SERVER_STOPPED, TOOL_CALL_RESULT, SAMPLING_REQUEST | McpPresenter |
| Windows | WINDOW_EVENTS | READY_TO_SHOW, WINDOW_CLOSED, WINDOW_FOCUSED | WindowPresenter |
| Tabs | TAB_EVENTS | TITLE_UPDATED, STATE_CHANGED, RENDERER_TAB_READY | TabPresenter |
| Workspace | WORKSPACE_EVENTS | PLAN_UPDATED, TERMINAL_OUTPUT, FILES_CHANGED | WorkspacePresenter |
| Knowledge Base | RAG_EVENTS | FILE_UPDATED, FILE_PROGRESS | KnowledgePresenter |

 Example event emission:

 
```

```

 **Sources:** [src/main/events.ts1-286](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/main/events.ts#L1-L286) [src/renderer/src/events.ts1-215](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/renderer/src/events.ts#L1-L215) [src/main/eventbus/index.ts](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/main/eventbus/index.ts) [src/main/presenter/mcpPresenter/index.ts143-148](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/main/presenter/mcpPresenter/index.ts#L143-L148)

 
---

 
## Build System and Entry Points

 
### Build Configuration

 The build system uses `electron-vite` (version `^4.0.1`) configured in `electron.vite.config.ts` with process-specific settings:

 **Build Target Configuration**

 
| Target | Entry Point | Output Directory | Build Config Section | Key Plugins |
|---|---|---|---|---|
| Main | src/main/index.ts | out/main/ | main: { ... } | externalizeDepsPlugin (excludes mermaid) |
| Preload | src/preload/index.ts, src/preload/floating-preload.ts | out/preload/ | preload: { ... } | externalizeDepsPlugin |
| Renderer | Multiple HTML files (see below) | out/renderer/ | renderer: { ... } | @vitejs/plugin-vue, vite-plugin-monaco-editor-esm, @tailwindcss/vite |

 **Renderer Entry Points** (configured in `rollupOptions.input`):

 
```

```

 **External Dependencies**: The Main Process build externalizes native modules (`sharp`, `@duckdb/node-api`) to avoid bundling binary dependencies. Renderer uses `optimizeDeps` to pre-bundle `monaco-editor` and `axios`.

 **Path Aliases**:

 
 - Main: `@` → `src/main/`, `@shared` → `src/shared`
 - Renderer: `@` → `src/renderer/src`, `@shell` → `src/renderer/shell`, `@shared` → `src/shared`, `@shadcn` → `src/shadcn`
 
 **Sources:** [electron.vite.config.ts1-120](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/electron.vite.config.ts#L1-L120) [package.json1-60](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/package.json#L1-L60)

 
### Application Startup Sequence

 The initialization sequence follows a phased approach managed by `LifecycleManager` to ensure dependencies are ready before dependent systems start.

 **Startup Sequence Diagram**

 
```

```

 **Key Lifecycle Phases**:

 
 - **Database Setup** (`lifecycle/hooks/database.ts`): Opens SQLite connection, runs schema migrations
 - **Configuration Load** (`lifecycle/hooks/config.ts`): Initializes `ConfigPresenter`, loads settings from `ElectronStore`
 - **Presenter Initialization** (`presenter/index.ts:110-194`): Constructs all presenter instances with dependency injection
 - **Window Creation** (`main/index.ts`): Creates shell window with `BrowserWindow`
 - **Renderer Ready** (`WINDOW_EVENTS.READY_TO_SHOW`): Triggers `presenter.init()` which syncs models and initializes auxiliary systems
 
 The lifecycle ensures that database connections are open before `SQLitePresenter` is used, and that configuration is loaded before providers are instantiated.

 **Sources:** [src/main/index.ts](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/main/index.ts) [src/main/lifecycle/index.ts](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/main/lifecycle/index.ts) [src/main/presenter/index.ts110-194](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/main/presenter/index.ts#L110-L194) [src/main/presenter/index.ts241-258](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/main/presenter/index.ts#L241-L258)

 
---

 
## Project Structure

 
### Directory Organization

 
```
deepchat/
├── src/
│   ├── main/               # Main Process (Node.js)
│   │   ├── presenter/      # Business logic layer
│   │   ├── eventbus/       # Event coordination
│   │   ├── lifecycle/      # Startup orchestration
│   │   └── index.ts        # Application entry point
│   │
│   ├── renderer/           # Renderer Process (Vue.js)
│   │   ├── src/            # Main window application
│   │   │   ├── components/ # Vue components
│   │   │   ├── stores/     # Pinia stores
│   │   │   ├── composables/# Vue composables
│   │   │   ├── router/     # Vue Router config
│   │   │   └── main.ts     # Vue entry point
│   │   ├── settings/       # Settings window
│   │   ├── floating/       # Floating button window
│   │   └── shell/          # Shell/terminal views
│   │
│   ├── preload/            # Preload Scripts
│   │   └── index.ts        # IPC bridge setup
│   │
│   └── shared/             # Shared TypeScript types
│       └── types/          # Interface definitions
│
├── electron.vite.config.ts # Build configuration
└── package.json            # Dependencies and scripts
```

 The `shared/` directory contains TypeScript interfaces that define contracts between Main and Renderer processes, ensuring type safety across the IPC boundary.

 **Sources:** [electron.vite.config.ts1-120](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/electron.vite.config.ts#L1-L120) [src/shared/presenter.d.ts1-3](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/shared/presenter.d.ts#L1-L3) Project directory structure

 
---

 
## Summary

 DeepChat's architecture leverages Electron's multi-process model to separate concerns:

 
 - **Main Process**: Node.js backend with Presenter-based business logic, native OS integration, and external API management
 - **Renderer Process**: Vue.js frontend with Pinia state management, reactive UI components, and real-time updates
 - **IPC Bridge**: Unified `presenter:call` mechanism with dynamic method dispatch
 - **Event System**: Domain-organized events coordinated by `EventBus` for cross-process communication
 
 This separation enables secure, performant operation while maintaining a clean architecture where the Main Process handles privileged operations and the Renderer Process focuses on user experience.

 For deeper exploration of specific subsystems:

 
 - [Presenter Pattern and IPC Communication](https://deepwiki.com/thinkinaixyz/deepchat/2.1-presenter-pattern-and-ipc-communication)
 - [Event System Architecture](https://deepwiki.com/thinkinaixyz/deepchat/2.2-event-system-architecture)
 - [Window and Tab Management](https://deepwiki.com/thinkinaixyz/deepchat/2.4-window-and-tab-management)
 - [State Management and Pinia Stores](https://deepwiki.com/thinkinaixyz/deepchat/2.5-state-management-and-pinia-stores)
