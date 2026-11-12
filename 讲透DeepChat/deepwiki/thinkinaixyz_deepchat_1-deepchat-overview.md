> 来源: [https://deepwiki.com/thinkinaixyz/deepchat/1-deepchat-overview](https://deepwiki.com/thinkinaixyz/deepchat/1-deepchat-overview)（Wayback 快照 2025-10-08）
> DeepWiki deepchat/1-deepchat-overview

# DeepChat Overview

  Relevant source files 
 - [electron.vite.config.ts](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/electron.vite.config.ts)
 - [package.json](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/package.json)
 - [src/renderer/src/App.vue](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/src/renderer/src/App.vue)
 - [src/renderer/src/assets/geist.ttf](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/src/renderer/src/assets/geist.ttf)
 - [src/renderer/src/assets/style.css](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/src/renderer/src/assets/style.css)
 - [src/renderer/src/components/markdown/MarkdownRenderer.vue](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/src/renderer/src/components/markdown/MarkdownRenderer.vue)
 - [src/renderer/src/components/message/MessageBlockThink.vue](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/src/renderer/src/components/message/MessageBlockThink.vue)
 - [src/renderer/src/components/think-content/ThinkContent.vue](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/src/renderer/src/components/think-content/ThinkContent.vue)
 - [src/renderer/src/components/think-content/index.ts](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/src/renderer/src/components/think-content/index.ts)
 - [src/renderer/src/main.ts](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/src/renderer/src/main.ts)
 - [src/renderer/src/stores/language.ts](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/src/renderer/src/stores/language.ts)
 
  
## Purpose and Scope

 This document provides a high-level introduction to DeepChat, an Electron-based AI chat application that supports multiple LLM providers, extensible tools via Model Context Protocol (MCP), and built-in knowledge base capabilities. This overview covers the application's purpose, technology stack, core architecture, and major system components.

 For detailed information about specific subsystems:

 
 - Installation and build process: see [Installation and Setup](https://deepwiki.com/thinkinaixyz/deepchat/1.1-installation-and-setup)
 - Electron architecture details: see [Application Architecture](https://deepwiki.com/thinkinaixyz/deepchat/1.2-application-architecture)
 - Presenter pattern and IPC: see [Presenter Pattern and IPC](https://deepwiki.com/thinkinaixyz/deepchat/2.1-presenter-pattern-and-ipc)
 - LLM provider implementations: see [LLM Provider Integration](https://deepwiki.com/thinkinaixyz/deepchat/4-llm-provider-integration)
 - MCP system: see [Model Context Protocol (MCP)](https://deepwiki.com/thinkinaixyz/deepchat/6-model-context-protocol-(mcp))
 - Knowledge base functionality: see [Knowledge Base System](https://deepwiki.com/thinkinaixyz/deepchat/7-knowledge-base-system)
 
 
---

 
## What is DeepChat

 DeepChat is a desktop AI chat client built with Electron, Vue 3, and TypeScript. It provides a unified interface for interacting with multiple Large Language Model (LLM) providers while offering advanced features such as streaming responses, tool calling via MCP servers, web search integration, and document-based retrieval-augmented generation (RAG) through built-in vector databases.

 **Core Design Principles:**

 
 - **Multi-Provider Support**: Single interface for OpenAI, Anthropic, Google Gemini, DeepSeek, Ollama, and other providers
 - **Security-First Architecture**: Strict process isolation between main (Node.js) and renderer (Chromium) processes
 - **Extensibility**: MCP protocol integration for adding tools, resources, and prompts from external servers
 - **Cross-Platform**: Native builds for Windows (x64, ARM64), macOS (x64, Apple Silicon), and Linux (x64, ARM64)
 - **Internationalization**: Native support for 9 languages including RTL languages (Persian, Arabic)
 
 **Sources:** [package.json1-206](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/package.json#L1-L206) [src/renderer/src/App.vue1-335](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/src/renderer/src/App.vue#L1-L335)

 
---

 
## Technology Stack

 
### Core Framework

 
| Component | Technology | Purpose |
|---|---|---|
| Application Framework | Electron 37.6.0 | Desktop application shell with Node.js + Chromium |
| Frontend Framework | Vue 3.5.21 | Reactive UI components |
| State Management | Pinia 3.0.3 | Global state management |
| Router | Vue Router 4 | Application routing |
| Build System | electron-vite 4.0.0 | Vite-based Electron build tooling |
| UI Components | Shadcn UI + Radix Vue | Accessible component library |
| Rich Text Editor | Tiptap 2.11.7 | Message input with mentions and file uploads |
| Markdown Rendering | vue-renderer-markdown | Custom markdown parser with code execution preview |

 
### Data Persistence

 
| Component | Technology | Purpose |
|---|---|---|
| Configuration | electron-store 8.2.0 | Key-value settings storage |
| Conversations | better-sqlite3-multiple-ciphers | SQLite database for messages and threads |
| Vector Database | @duckdb/node-api 1.3.2 | DuckDB with HNSW for semantic search |

 
### LLM Provider SDKs

 
| Provider | SDK | Version |
|---|---|---|
| OpenAI | openai | 5.18.0 |
| Anthropic | @anthropic-ai/sdk | 0.53.0 |
| Google Gemini | @google/genai | 1.16.0 |
| AWS Bedrock | @aws-sdk/client-bedrock-runtime | 3.879.0 |
| Ollama | ollama | 0.5.17 |
| Together AI | together-ai | 0.16.0 |

 
### Extension Systems

 
| System | Technology | Purpose |
|---|---|---|
| MCP Protocol | @modelcontextprotocol/sdk 1.17.5 | Tool and resource integration |
| Apple Integration | @jxa/run, run-applescript | macOS system automation |
| Code Execution | @e2b/code-interpreter | Sandboxed code execution |

 **Sources:** [package.json59-99](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/package.json#L59-L99) [package.json100-177](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/package.json#L100-L177)

 
---

 
## Electron Multi-Process Architecture

 DeepChat follows Electron's security best practices with strict process separation and controlled IPC communication:

 
```

```

 
### Key Architectural Components

 **Main Process (`src/main/`):**

 
 - `Presenter` singleton: Central dependency injection container managing all presenters
 - Presenter classes: Business logic layer exposing methods via IPC
 - No direct DOM access; all UI updates via events
 
 **Preload Scripts (`src/preload/`):**

 
 - `contextBridge` API: Whitelisted functions exposed to renderer
 - Security layer preventing arbitrary Node.js access from renderer
 - Two preload bundles: `index.ts` (main window), `floating-preload.ts` (floating window)
 
 **Renderer Process (`src/renderer/`):**

 
 - Vue 3 application with reactive UI components
 - Pinia stores as single source of truth for UI state
 - `usePresenter()` composable for type-safe IPC calls
 - Event listeners for reactive updates from main process
 
 **Sources:** [electron.vite.config.ts1-103](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/electron.vite.config.ts#L1-L103) [src/renderer/src/App.vue1-60](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/src/renderer/src/App.vue#L1-L60) [src/renderer/src/main.ts1-30](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/src/renderer/src/main.ts#L1-L30)

 
---

 
## Core Communication Pattern: Presenter System

 DeepChat uses a presenter pattern to bridge the main and renderer processes:

 
```

```

 **Presenter Methods Exposed:**

 
 - `configPresenter`: Settings CRUD, provider configuration, language management
 - `threadPresenter`: Message sending, conversation management, streaming completions
 - `llmProviderPresenter`: Provider instantiation, rate limiting, model metadata
 - `mcpPresenter`: MCP server lifecycle, tool execution, resource access
 - `knowledgePresenter`: Knowledge base CRUD, file upload, semantic search
 - `windowPresenter`: Window creation, tab management, floating window control
 - `devicePresenter`: System information, platform detection
 
 **Event Categories:**

 
 - `CONFIG_EVENTS`: Configuration changes (language, theme, provider updates)
 - `STREAM_EVENTS`: Real-time streaming updates (token chunks, tool calls)
 - `MCP_EVENTS`: MCP server status changes (connected, disconnected, error)
 - `NOTIFICATION_EVENTS`: User notifications (errors, system messages)
 - `SHORTCUT_EVENTS`: Keyboard shortcut triggers (zoom, new conversation)
 
 **Sources:** [src/renderer/src/App.vue179-246](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/src/renderer/src/App.vue#L179-L246)

 
---

 
## Application Entry Points

 DeepChat has multiple entry points for different window types:

 
```

```

 **Build Configuration:**

 The application uses `electron-vite` with separate build targets for main, preload, and renderer processes:

 
| Target | Entry Point | Output | Purpose |
|---|---|---|---|
| Main | src/main/index.ts | out/main/index.js | Node.js process managing application lifecycle |
| Preload (main) | src/preload/index.ts | out/preload/index.js | Context bridge for main/chat windows |
| Preload (floating) | src/preload/floating-preload.ts | out/preload/floating.js | Context bridge for floating window |
| Renderer (shell) | src/renderer/shell/index.html | out/renderer/shell/ | Main application shell |
| Renderer (index) | src/renderer/index.html | out/renderer/index.html | Primary chat interface |
| Renderer (floating) | src/renderer/floating/index.html | out/renderer/floating.html | Compact floating chat |
| Renderer (splash) | src/renderer/splash/index.html | out/renderer/splash.html | Loading screen |

 **Sources:** [electron.vite.config.ts11-102](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/electron.vite.config.ts#L11-L102)

 
---

 
## Key System Components

 
### Main Process Presenters

 DeepChat's business logic resides in presenter classes in the main process:

 
| Presenter | File | Responsibilities |
|---|---|---|
| Presenter | src/main/presenter.ts | Singleton DI container, manages all presenters |
| ConfigPresenter | src/main/presenters/configPresenter.ts | Settings persistence via ElectronStore |
| ThreadPresenter | src/main/presenters/threadPresenter.ts | Message lifecycle, streaming coordination |
| LLMProviderPresenter | src/main/presenters/llmProviderPresenter.ts | Provider routing, rate limiting, model metadata |
| McpPresenter | src/main/presenters/mcpPresenter.ts | MCP server management, tool execution |
| KnowledgePresenter | src/main/presenters/knowledgePresenter.ts | Knowledge base orchestration |
| KnowledgeStorePresenter | src/main/presenters/knowledgeStorePresenter.ts | Per-KB instance, file processing |
| WindowPresenter | src/main/presenters/windowPresenter.ts | Window lifecycle, multi-window sync |
| TabPresenter | src/main/presenters/tabPresenter.ts | Tab management, conversation-tab binding |
| FilePresenter | src/main/presenters/filePresenter.ts | File upload, MIME detection, content extraction |
| SQLitePresenter | src/main/presenters/sqlitePresenter.ts | Conversation database interface |
| DuckDBPresenter | src/main/presenters/duckdbPresenter.ts | Vector database with HNSW indexing |
| DevicePresenter | src/main/presenters/devicePresenter.ts | System info (platform, memory, CPU) |

 
---

 
### Renderer Process Stores

 State management uses Pinia stores with reactive synchronization to main process:

 
| Store | File | Purpose |
|---|---|---|
| useChatStore | src/renderer/src/stores/chat.ts | Conversations, messages, active thread tracking |
| useSettingsStore | src/renderer/src/stores/settings.ts | Provider configs, model parameters, UI settings |
| useMcpStore | src/renderer/src/stores/mcp.ts | MCP server state, tool metadata |
| useThemeStore | src/renderer/src/stores/theme.ts | Dark/light mode, system theme detection |
| useLanguageStore | src/renderer/src/stores/language.ts | i18n locale, RTL layout support |
| useArtifactStore | src/renderer/src/stores/artifact.ts | Code artifact preview state |
| useModelCheckStore | src/renderer/src/stores/modelCheck.ts | Model availability checking |
| useReferenceStore | src/renderer/src/stores/reference.ts | Web search reference preview |

 **Sources:** [src/renderer/src/App.vue6-30](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/src/renderer/src/App.vue#L6-L30) [src/renderer/src/stores/language.ts1-62](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/src/renderer/src/stores/language.ts#L1-L62)

 
---

 
## UI Architecture

 
### Component Hierarchy

 
```

```

 **Core UI Components:**

 
 - `App.vue`: Root component handling global events, theme, and error notifications
 - `ChatInput.vue`: Tiptap-based rich text editor with file uploads and mentions
 - `MarkdownRenderer.vue`: Custom markdown renderer with code execution preview
 - `MessageBlockThink.vue`: Collapsible thinking/reasoning content display
 - `ThinkContent.vue`: Styled container for model reasoning traces
 
 **Sources:** [src/renderer/src/App.vue308-335](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/src/renderer/src/App.vue#L308-L335) [src/renderer/src/components/markdown/MarkdownRenderer.vue1-124](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/src/renderer/src/components/markdown/MarkdownRenderer.vue#L1-L124) [src/renderer/src/components/message/MessageBlockThink.vue1-61](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/src/renderer/src/components/message/MessageBlockThink.vue#L1-L61) [src/renderer/src/components/think-content/ThinkContent.vue1-107](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/src/renderer/src/components/think-content/ThinkContent.vue#L1-L107)

 
---

 
## Styling and Theming

 DeepChat uses Tailwind CSS 4 with a custom design system:

 
```

```

 **Theme Variables:**

 The application defines comprehensive color palettes in CSS variables:

 
 - **Primary colors**: `--primary-50` through `--primary-1000` (blue palette)
 - **Base colors**: `--base-50` through `--base-1000` (neutral palette)
 - **Semantic tokens**: `--background`, `--foreground`, `--card`, `--border`, etc.
 - **Usage indicators**: `--usage-low`, `--usage-mid`, `--usage-high` (for token usage visualization)
 
 **RTL Support:**

 The `useLanguageStore` detects RTL languages and sets `dir="rtl"` on the root element:

 
```

```

 **Sources:** [src/renderer/src/assets/style.css1-368](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/src/renderer/src/assets/style.css#L1-L368) [src/renderer/src/stores/language.ts8-25](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/src/renderer/src/stores/language.ts#L8-L25)

 
---

 
## Build and Distribution

 
### Build Scripts

 
| Script | Command | Purpose |
|---|---|---|
| Development | pnpm dev | Start dev server with hot reload |
| Development (inspect) | pnpm dev:inspect | Enable Chrome DevTools debugging on port 9229 |
| Type Check | pnpm typecheck | Validate TypeScript for Node.js and web code |
| Build | pnpm build | Production build (all processes) |
| Build Windows x64 | pnpm build:win:x64 | Windows installer (Intel/AMD) |
| Build Windows ARM64 | pnpm build:win:arm64 | Windows installer (ARM) |
| Build macOS ARM64 | pnpm build:mac:arm64 | macOS DMG (Apple Silicon) |
| Build macOS x64 | pnpm build:mac:x64 | macOS DMG (Intel) |
| Build Linux x64 | pnpm build:linux:x64 | Linux AppImage/deb (x64) |
| Build Linux ARM64 | pnpm build:linux:arm64 | Linux AppImage/deb (ARM64) |

 
### Runtime Installation

 DeepChat bundles alternative runtimes for MCP servers:

 
```

```

 **Supported Runtimes:**

 
 - **UV**: Python package manager (0.8.8)
 - **Bun**: JavaScript runtime (v1.2.20)
 - **Node.js**: Bundled for Windows builds
 
 **Sources:** [package.json13-58](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/package.json#L13-L58)

 
---

 
## Internationalization

 DeepChat supports 9 languages with full RTL layout support:

 
| Language Code | Language | RTL Support |
|---|---|---|
| en-US | English (US) | No |
| zh-CN | Simplified Chinese | No |
| zh-TW | Traditional Chinese | No |
| ja-JP | Japanese | No |
| ko-KR | Korean | No |
| es-ES | Spanish | No |
| de-DE | German | No |
| fr-FR | French | No |
| fa-IR | Persian | Yes |

 **i18n Architecture:**

 
```

```

 **Translation Management:**

 The project uses `@lingual/i18n-check` for translation validation:

 
```

```

 **Sources:** [src/renderer/src/main.ts9-18](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/src/renderer/src/main.ts#L9-L18) [src/renderer/src/stores/language.ts1-62](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/src/renderer/src/stores/language.ts#L1-L62) [package.json53-56](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/package.json#L53-L56)

 
---

 
## Summary

 DeepChat is a production-grade AI chat client that demonstrates modern Electron best practices:

 
 - **Security**: Strict process isolation with context bridge API
 - **Scalability**: Presenter pattern for clean business logic separation
 - **Extensibility**: MCP protocol for third-party tool integration
 - **Performance**: Adaptive buffering for large content streams, DuckDB for fast vector search
 - **User Experience**: Real-time streaming, multi-window sync, native platform integrations
 - **Developer Experience**: TypeScript throughout, comprehensive type safety, modular architecture
 
 The application serves as both a functional AI chat client and a reference implementation for complex Electron applications requiring secure IPC, real-time data streaming, and extensible plugin architectures.

 **Sources:** All files referenced throughout this document
