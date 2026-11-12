> 来源: [https://deepwiki.com/thinkinaixyz/deepchat/2-core-architecture](https://deepwiki.com/thinkinaixyz/deepchat/2-core-architecture)（Wayback 快照 2025-10-07）
> DeepWiki deepchat/2-core-architecture

# Core Architecture

  Relevant source files 
 - [src/main/events.ts](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/src/main/events.ts)
 - [src/main/presenter/configPresenter/index.ts](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/src/main/presenter/configPresenter/index.ts)
 - [src/main/presenter/index.ts](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/src/main/presenter/index.ts)
 - [src/renderer/src/App.vue](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/src/renderer/src/App.vue)
 - [src/renderer/src/events.ts](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/src/renderer/src/events.ts)
 - [src/renderer/src/stores/language.ts](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/src/renderer/src/stores/language.ts)
 - [src/renderer/src/stores/settings.ts](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/src/renderer/src/stores/settings.ts)
 - [src/shared/presenter.d.ts](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/src/shared/presenter.d.ts)
 
  This document describes the fundamental architectural patterns, communication mechanisms, and core system components that form the foundation of DeepChat. It covers the Electron multi-process design, the Presenter pattern for business logic, IPC communication, event-driven architecture, and state management strategies.

 For detailed information about specific subsystems, see:

 
 - IPC and Presenter pattern details: [Presenter Pattern and IPC](https://deepwiki.com/thinkinaixyz/deepchat/2.1-presenter-pattern-and-ipc)
 - Application initialization and state stores: [Application Lifecycle and State Management](https://deepwiki.com/thinkinaixyz/deepchat/2.2-application-lifecycle-and-state-management)
 - Event system implementation: [Event System Architecture](https://deepwiki.com/thinkinaixyz/deepchat/2.3-event-system-architecture)
 - Window and tab coordination: [Window and Tab Management](https://deepwiki.com/thinkinaixyz/deepchat/2.4-window-and-tab-management)
 
 
## Electron Multi-Process Architecture

 DeepChat follows Electron's recommended security architecture with strict separation between the main process (Node.js) and renderer process (Chromium). The main process handles all privileged operations including file system access, database operations, and external API calls, while the renderer process is sandboxed to only display UI and manage user interactions.

 
### Process Responsibilities

 **Main Process (Node.js)**

 
 - Business logic encapsulated in Presenters
 - Database operations (SQLite, DuckDB)
 - File system access
 - External API communication (LLM providers, MCP servers)
 - Window lifecycle management
 - Configuration persistence via ElectronStore
 
 **Renderer Process (Chromium)**

 
 - Vue.js application rendering
 - User input handling
 - Local UI state management via Pinia stores
 - IPC requests to main process
 - Event subscription for state updates
 
 **Preload Scripts**

 
 - Context Bridge for secure IPC exposure
 - Type-safe API surface
 - No direct Node.js access from renderer
 
 
### Security Model

 The architecture enforces that the renderer process cannot directly access Node.js APIs. All privileged operations must go through the Context Bridge, which exposes only the `presenter:call` IPC mechanism [src/main/presenter/index.ts239-295](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/src/main/presenter/index.ts#L239-L295)

 **Diagram: Process Boundary and Communication Flow**

 
```

```

 Sources: [src/main/presenter/index.ts239-295](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/src/main/presenter/index.ts#L239-L295) [src/renderer/src/composables/usePresenter.ts](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/src/renderer/src/composables/usePresenter.ts)

 
## Presenter Pattern

 The Presenter pattern is the core architectural pattern for main process business logic. Each Presenter class encapsulates a specific domain of functionality and is managed by a central `Presenter` singleton that acts as a service locator and dependency injection container.

 
### Presenter Singleton

 The `Presenter` class [src/main/presenter/index.ts58-220](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/src/main/presenter/index.ts#L58-L220) is instantiated once during application lifecycle and manages all sub-presenters:

 **Key Properties:**

 
 - `configPresenter: IConfigPresenter` - Configuration and settings management
 - `sqlitePresenter: ISQLitePresenter` - Database operations
 - `llmproviderPresenter: ILlmProviderPresenter` - LLM provider coordination
 - `threadPresenter: IThreadPresenter` - Conversation and message lifecycle
 - `windowPresenter: IWindowPresenter` - Window lifecycle management
 - `tabPresenter: ITabPresenter` - Tab coordination
 - `mcpPresenter: IMCPPresenter` - Model Context Protocol integration
 - `knowledgePresenter: IKnowledgePresenter` - Knowledge base management
 - `filePresenter: IFilePresenter` - File processing
 - `upgradePresenter: IUpgradePresenter` - Application updates
 - `syncPresenter: ISyncPresenter` - Data synchronization
 - `shortcutPresenter: IShortcutPresenter` - Keyboard shortcuts
 
 
### Presenter Instance Creation

 The `Presenter` singleton is created during application initialization [src/main/presenter/index.ts126-132](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/src/main/presenter/index.ts#L126-L132):

 
```

```

 Dependencies are injected during construction. For example, `ThreadPresenter` receives three dependencies [src/main/presenter/index.ts97-101](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/src/main/presenter/index.ts#L97-L101):

 
```

```

 **Diagram: Presenter Dependency Graph**

 
```

```

 Sources: [src/main/presenter/index.ts58-220](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/src/main/presenter/index.ts#L58-L220)

 
### Presenter Lifecycle

 Presenters are initialized in phases:

 
 - **Construction Phase**: Core presenters instantiated [src/main/presenter/index.ts84-122](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/src/main/presenter/index.ts#L84-L122)
 - **Setup Phase**: Event bus configured [src/main/presenter/index.ts123](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/src/main/presenter/index.ts#L123-L123)
 - **Initialization Phase**: Presenters initialized after main window ready [src/main/presenter/index.ts166-176](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/src/main/presenter/index.ts#L166-L176)
 - **Destruction Phase**: Resources cleaned up on app quit [src/main/presenter/index.ts209-219](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/src/main/presenter/index.ts#L209-L219)
 
 
## IPC Communication Layer

 All communication from renderer to main process goes through a single IPC handler `presenter:call` [src/main/presenter/index.ts239-295](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/src/main/presenter/index.ts#L239-L295) This provides a unified, type-safe interface for invoking presenter methods.

 
### IPC Call Mechanism

 The handler signature:

 
```

```

 **Parameters:**

 
 - `name`: Presenter name (e.g., `"configPresenter"`, `"threadPresenter"`)
 - `method`: Method name to invoke (e.g., `"getSetting"`, `"sendMessage"`)
 - `payloads`: Variable arguments passed to the method
 
 
### Context Passing

 Each IPC call extracts context from the `IpcMainInvokeEvent` [src/main/presenter/index.ts244-256](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/src/main/presenter/index.ts#L244-L256):

 
```

```

 The `tabId` and `windowId` are resolved using `TabPresenter`:

 
```

```

 
### Dynamic Method Invocation

 The handler dynamically invokes methods using reflection [src/main/presenter/index.ts266-282](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/src/main/presenter/index.ts#L266-L282):

 
```

```

 
### Renderer-Side Abstraction

 The renderer uses the `usePresenter` composable to create type-safe presenter proxies:

 
```

```

 This abstracts away the IPC call details and provides autocomplete for available methods.

 **Diagram: IPC Call Flow**

 
```

```

 Sources: [src/main/presenter/index.ts239-295](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/src/main/presenter/index.ts#L239-L295) [src/renderer/src/composables/usePresenter.ts](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/src/renderer/src/composables/usePresenter.ts)

 
## Event-Driven Communication

 While IPC provides request-response communication from renderer to main, the Event Bus provides broadcast-style communication in all directions: main-to-renderer, main-to-main, and main-to-all-windows.

 
### Event Bus Implementation

 The `eventBus` singleton [src/main/eventbus/index.ts](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/src/main/eventbus/index.ts) manages event distribution:

 **Key Methods:**

 
 - `send(event, target, ...args)` - Send to specific target
 - `sendToRenderer(event, target, ...args)` - Send to renderer process(es)
 - `sendToMain(event, ...args)` - Send to main process listeners
 - `on(event, handler)` - Register main process listener
 
 **Send Targets:**

 
 - `SendTarget.ACTIVE_WINDOW` - Only currently focused window
 - `SendTarget.ALL_WINDOWS` - All open windows
 - `SendTarget.SPECIFIC_WINDOW` - Specific window by ID
 - `SendTarget.ACTIVE_TAB` - Currently active tab in active window
 
 
### Event Categories

 Events are organized by domain using namespace prefixes [src/main/events.ts1-217](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/src/main/events.ts#L1-L217):

 
| Category | Prefix | Example Events |
|---|---|---|
| Configuration | config: | config:provider-changed, config:model-status-changed |
| Conversation | conversation: | conversation:activated, conversation:message-edited |
| Streaming | stream: | stream:response, stream:end, stream:error |
| Window | window: | window:maximized, window:closed |
| MCP | mcp: | mcp:server-started, mcp:tool-call-result |
| Tab | tab: | tab:title-updated, tab:visibility-changed |
| Update | update: | update:progress, update:will-restart |

 
### Event Flow Patterns

 **Configuration Changes:** When a setting is updated in `ConfigPresenter` [src/main/presenter/configPresenter/index.ts350-363](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/src/main/presenter/configPresenter/index.ts#L350-L363):

 
```

```

 **Streaming Updates:** During message generation, `ThreadPresenter` emits stream events that are automatically broadcast to the active tab:

 
```

```

 **Provider Updates:** Atomic provider updates trigger precise change events [src/main/presenter/configPresenter/index.ts403-429](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/src/main/presenter/configPresenter/index.ts#L403-L429):

 
```

```

 **Diagram: Event Flow Topology**

 
```

```

 Sources: [src/main/events.ts1-217](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/src/main/events.ts#L1-L217) [src/main/eventbus/index.ts](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/src/main/eventbus/index.ts) [src/main/presenter/configPresenter/index.ts350-363](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/src/main/presenter/configPresenter/index.ts#L350-L363)

 
## State Management

 DeepChat uses a dual-layer state management architecture: persistent storage in the main process and reactive stores in the renderer process.

 
### Main Process Storage

 **ElectronStore** [src/main/presenter/configPresenter/index.ts92-134](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/src/main/presenter/configPresenter/index.ts#L92-L134):

 
 - Application settings (language, theme, proxy)
 - Provider configurations
 - Custom models
 - System prompts
 - MCP server configurations
 
 **Configuration Structure:**

 
```

```

 **SQLite Database** (via `SQLitePresenter`):

 
 - Conversation records
 - Message history with content blocks
 - File attachments
 - Message metadata (tokens, costs)
 
 **DuckDB Databases** (via `KnowledgePresenter`):

 
 - Vector embeddings for knowledge bases
 - HNSW indices for similarity search
 - Document metadata and chunks
 
 
### Renderer Process Stores

 **Pinia Store Architecture:**

 
| Store | Purpose | Key State |
|---|---|---|
| useChatStore | Active conversations, messages | threads, messages, activeThreadId, generatingThreadIds |
| useSettingsStore | Providers, models, settings | providers, enabledModels, searchEngines |
| useMcpStore | MCP servers, tools | servers, tools, mcpEnabled |
| useThemeStore | Theme management | themeMode, isDark |
| useLanguageStore | Localization | language, dir (for RTL) |
| useArtifactStore | Code artifacts | artifacts, isOpen |

 
### State Synchronization Strategy

 **Initial Load:** When a store is created, it loads initial state via IPC [src/renderer/src/stores/settings.ts295-380](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/src/renderer/src/stores/settings.ts#L295-L380):

 
```

```

 **Event-Driven Updates:** Stores subscribe to relevant events to stay synchronized [src/renderer/src/stores/settings.ts655-746](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/src/renderer/src/stores/settings.ts#L655-L746):

 
```

```

 **Optimistic Updates:** Some operations update local state immediately before IPC completes:

 
```

```

 
### Cache Strategies

 **Memory Caching:** `ConfigPresenter` maintains an in-memory cache for high-frequency reads [src/main/presenter/configPresenter/index.ts101-104](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/src/main/presenter/configPresenter/index.ts#L101-L104):

 
```

```

 **Transient State:** Streaming message state is kept in memory only during generation [src/main/presenter/threadPresenter/index.ts](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/src/main/presenter/threadPresenter/index.ts):

 
```

```

 **Diagram: State Synchronization Flow**

 
```

```

 Sources: [src/main/presenter/configPresenter/index.ts92-578](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/src/main/presenter/configPresenter/index.ts#L92-L578) [src/renderer/src/stores/settings.ts1-1395](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/src/renderer/src/stores/settings.ts#L1-L1395)

 
## Key System Components

 
### ConfigPresenter

 Central configuration management [src/main/presenter/configPresenter/index.ts91-1426](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/src/main/presenter/configPresenter/index.ts#L91-L1426):

 **Responsibilities:**

 
 - ElectronStore persistence (`app-settings`, `custom_prompts`, `system_prompts`)
 - Provider CRUD operations with atomic updates
 - Model configuration and status management
 - Settings accessors with type safety
 - Event broadcasting for configuration changes
 
 **Key Methods:**

 
 - `getSetting<T>(key)` / `setSetting<T>(key, value)` - Generic settings access
 - `getProviders()` / `setProviders()` - Provider list management
 - `updateProviderAtomic()` - Atomic provider updates with rebuild detection
 - `getModelStatus()` / `setModelStatus()` - Model enable/disable state
 - `getBatchModelStatus()` - Optimized batch model status retrieval
 
 **Storage Locations:**

 
 - Main settings: `userData/app-settings.json`
 - Provider models: `userData/provider_models/models_{providerId}.json`
 - Custom prompts: `userData/custom_prompts.json`
 - System prompts: `userData/system_prompts.json`
 
 
### SQLitePresenter

 Conversation and message persistence [src/main/presenter/sqlitePresenter/index.ts](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/src/main/presenter/sqlitePresenter/index.ts):

 **Schema:**

 
 - `conversations` - Thread metadata (title, model, created_at)
 - `messages` - Individual messages with role, content blocks, status
 - `message_files` - File attachments linked to messages
 
 **Query Patterns:**

 
 - Conversations sorted by last update time
 - Messages filtered by conversation_id with pagination
 - Efficient updates for streaming content
 
 
### LLMProviderPresenter

 LLM provider orchestration [src/main/presenter/llmProviderPresenter/index.ts](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/src/main/presenter/llmProviderPresenter/index.ts):

 **Responsibilities:**

 
 - Provider instance management (lazy initialization)
 - Model list retrieval and caching
 - Rate limiting and queue management
 - Stream processing coordination
 - Custom model registration
 
 **Provider Registry:**

 
 - OpenAI-compatible providers (OpenAI, DeepSeek, Minimax, etc.)
 - Anthropic Claude
 - Google Gemini
 - Alibaba Dashscope (Qwen)
 - Local Ollama
 
 
### WindowPresenter & TabPresenter

 Window and tab lifecycle management:

 **WindowPresenter** [src/main/presenter/windowPresenter/index.ts](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/src/main/presenter/windowPresenter/index.ts):

 
 - Creates and manages BrowserWindow instances
 - Handles window state (maximize, minimize, close)
 - Manages window-conversation binding
 
 **TabPresenter** [src/main/presenter/tabPresenter/index.ts](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/src/main/presenter/tabPresenter/index.ts):

 
 - Tracks tab-to-webContentsId mapping
 - Coordinates multi-tab state
 - Provides context for IPC calls
 - Manages tab-conversation associations
 
 **Tab Context Resolution:**

 
```

```

 This enables IPC handlers to identify which tab and window initiated a request.

 Sources: [src/main/presenter/configPresenter/index.ts91-1426](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/src/main/presenter/configPresenter/index.ts#L91-L1426) [src/main/presenter/index.ts58-220](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/src/main/presenter/index.ts#L58-L220) [src/main/presenter/windowPresenter/index.ts](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/src/main/presenter/windowPresenter/index.ts) [src/main/presenter/tabPresenter/index.ts](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/src/main/presenter/tabPresenter/index.ts)

 
## Summary

 DeepChat's core architecture demonstrates production-grade patterns:

 **Architectural Patterns:**

 
 - **Presenter Pattern**: Business logic encapsulation with dependency injection
 - **Service Locator**: Central `Presenter` singleton managing all sub-presenters
 - **Event-Driven**: Decoupled communication via EventBus broadcasts
 - **IPC Abstraction**: Unified `presenter:call` interface for type-safe cross-process communication
 
 **Security:**

 
 - Strict process separation with Context Bridge
 - No direct Node.js access from renderer
 - Controlled API surface
 
 **State Management:**

 
 - Dual-layer: ElectronStore (main) + Pinia (renderer)
 - Memory caching for high-frequency reads
 - Event-driven synchronization across windows
 - Optimistic updates for responsive UI
 
 **Scalability:**

 
 - Lazy initialization of providers
 - Batch operations for model status
 - Transient state for streaming operations
 - Atomic configuration updates to minimize event churn
 
 This architecture provides a solid foundation for the application's feature set while maintaining security, performance, and maintainability.
