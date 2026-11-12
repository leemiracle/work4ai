> 来源: [https://deepwiki.com/thinkinaixyz/deepchat/1.1-installation-and-setup](https://deepwiki.com/thinkinaixyz/deepchat/1.1-installation-and-setup)（Wayback 快照 2025-10-09）
> DeepWiki deepchat/1.1-installation-and-setup

# Installation and Setup

  Relevant source files 
 - [electron.vite.config.ts](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/electron.vite.config.ts)
 - [package.json](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/package.json)
 - [src/renderer/src/assets/geist.ttf](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/src/renderer/src/assets/geist.ttf)
 - [src/renderer/src/assets/style.css](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/src/renderer/src/assets/style.css)
 - [src/renderer/src/components/markdown/MarkdownRenderer.vue](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/src/renderer/src/components/markdown/MarkdownRenderer.vue)
 - [src/renderer/src/components/message/MessageBlockThink.vue](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/src/renderer/src/components/message/MessageBlockThink.vue)
 - [src/renderer/src/components/think-content/ThinkContent.vue](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/src/renderer/src/components/think-content/ThinkContent.vue)
 - [src/renderer/src/components/think-content/index.ts](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/src/renderer/src/components/think-content/index.ts)
 - [src/renderer/src/main.ts](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/src/renderer/src/main.ts)
 
  This document covers the installation and deployment of DeepChat for both end users and developers. It includes platform-specific installation procedures, development environment setup, and initial configuration steps.

 For information about configuring LLM providers and API keys after installation, see [Provider Configuration and Setup](https://deepwiki.com/thinkinaixyz/deepchat/4.2-stream-processing-and-agent-loop). For MCP server setup and configuration, see [MCP Configuration and Server Management](https://deepwiki.com/thinkinaixyz/deepchat/3.2-provider-and-model-configuration).

 
## End User Installation

 DeepChat provides pre-built binaries for all major operating systems through GitHub Releases. The application is packaged as a cross-platform Electron application with platform-specific installers.

 
### Supported Platforms and Installation Files

 
| Platform | Architecture | Installation File | Description |
|---|---|---|---|
| Windows | x64, ARM64 | .exe | Standard Windows installer |
| macOS | x64, ARM64 | .dmg | macOS disk image |
| Linux | x64, ARM64 | .AppImage, .deb | Portable AppImage or Debian package |

 
### Installation Process

 
```

```

 **Installation Steps:**

 
 - Navigate to the [GitHub Releases page](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/GitHub Releases page)
 - Download the appropriate installer for your platform and architecture
 - Run the installer following platform-specific conventions
 - Launch DeepChat from your applications menu or desktop
 
 **Sources:** [README.md236-242](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/README.md#L236-L242)

 
## Development Environment Setup

 DeepChat uses a modern JavaScript/TypeScript development stack with Electron, Vue.js, and pnpm package management. The development setup includes both Node.js dependencies and platform-specific runtime components for MCP server execution.

 
### Prerequisites

 
| Requirement | Version | Purpose |
|---|---|---|
| Node.js | ≥20.19.0 | Main runtime environment |
| pnpm | ≥10.11.0 | Package manager |
| Python | Latest | Native dependencies (sharp, better-sqlite3) |
| Git | Latest | Source code management |

 **Sources:** [package.json8-11](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/package.json#L8-L11)

 
### Development Setup Flow with Runtime Dependencies

 **Installation and Runtime Setup Diagram**

 
```

```

 **Sources:** [package.json13-57](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/package.json#L13-L57) [package.json32](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/package.json#L32-L32) [package.json45-51](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/package.json#L45-L51)

 
### Installation Commands

 
```

```

 **Sources:** [package.json32](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/package.json#L32-L32) [package.json45-52](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/package.json#L45-L52)

 
### Runtime Dependencies Explained

 DeepChat bundles external runtimes to enable MCP server execution without requiring users to install additional tools:

 
| Runtime | Version | Purpose | Location |
|---|---|---|---|
| uv | 0.8.8 | Python package management for MCP servers | ./runtime/uv/ |
| bun | v1.2.20 | JavaScript/TypeScript runtime for MCP servers | ./runtime/bun/ |
| node | platform-specific | Node.js runtime for Windows MCP servers | ./runtime/node/ (Windows only) |

 The `installRuntime` scripts use `tiny-runtime-injector` to download and configure these runtimes for the target platform and architecture. These runtimes are packaged with the final application for offline MCP server execution.

 **Sources:** [package.json45-51](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/package.json#L45-L51)

 **Platform-Specific Requirements:**

 **Windows:**

 
 - Enable Developer Mode in Settings → Update & Security → For Developers
 - Alternative: Run terminal as Administrator
 - Required for pnpm to create symlinks/hardlinks during `pnpm install`
 
 **macOS/Linux:**

 
 - No special permissions required
 - Ensure Python development headers are installed for native module compilation
 
 **Python Dependencies:** If you encounter build errors related to Python modules:

 
```

```

 **Sources:** [package.json8-11](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/package.json#L8-L11)

 
### Development Commands

 **Development Workflow**

 
```

```

 **Sources:** [package.json27-30](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/package.json#L27-L30) [package.json24-26](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/package.json#L24-L26) [package.json21-23](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/package.json#L21-L23)

 
| Command | Purpose | Configuration |
|---|---|---|
| pnpm run dev | Start development server with hot reload | electron-vite dev --watch |
| pnpm run dev:inspect | Development mode with Node.js debugger | --inspect=9229 |
| pnpm run dev:linux | Development mode for Linux (no sandbox) | --noSandbox |
| pnpm run start | Preview production build | electron-vite preview |
| pnpm run typecheck | Type check all TypeScript files | tsc + vue-tsc |
| pnpm run typecheck:node | Type check main process | tsconfig.node.json |
| pnpm run typecheck:web | Type check renderer process | tsconfig.app.json |
| pnpm test | Run all tests with Vitest | vitest |
| pnpm run test:main | Run main process tests | vitest.config.ts |
| pnpm run test:renderer | Run renderer process tests | vitest.config.renderer.ts |
| pnpm run lint | Lint code with oxlint | npx -y oxlint . |
| pnpm run format | Format code with Prettier | prettier --write . |

 **Sources:** [package.json13-32](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/package.json#L13-L32)

 **Build Commands**

 
| Command | Target Platform | Architecture |
|---|---|---|
| pnpm run build | Current platform | Current architecture |
| pnpm run build:win | Windows | All (x64 + ARM64) |
| pnpm run build:win:x64 | Windows | x64 only |
| pnpm run build:win:arm64 | Windows | ARM64 only |
| pnpm run build:mac | macOS | All (x64 + ARM64) |
| pnpm run build:mac:x64 | macOS | Intel x64 |
| pnpm run build:mac:arm64 | macOS | Apple Silicon |
| pnpm run build:linux | Linux | All (x64 + ARM64) |
| pnpm run build:linux:x64 | Linux | x64 only |
| pnpm run build:linux:arm64 | Linux | ARM64 only |
| pnpm run build:unpack | Current platform | Directory output (no installer) |

 All build commands first run `pnpm run build` which executes:

 
 - `pnpm run typecheck` - Type checking
 - `electron-vite build` - Vite build process
 
 **Sources:** [package.json31-43](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/package.json#L31-L43)

 
## Build and Packaging Architecture

 The build system uses `electron-vite` for source code compilation and `electron-builder` for platform-specific packaging. The build configuration is defined in `electron.vite.config.ts` with separate configurations for main process, preload scripts, and renderer process.

 **Build System Architecture**

 
```

```

 **Sources:** [electron.vite.config.ts11-102](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/electron.vite.config.ts#L11-L102) [package.json31-43](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/package.json#L31-L43)

 
### Build Configuration Details

 **Main Process Configuration** [electron.vite.config.ts12-33](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/electron.vite.config.ts#L12-L33)

 
 - Uses `externalizeDepsPlugin` to externalize dependencies
 - Excludes `mermaid` from externalization for bundling
 - Configures path aliases: `@` → `src/main/`, `@shared` → `src/shared`
 - External native modules: `sharp`, `@duckdb/node-api` (not bundled)
 - Output: Single file `out/main/index.js` with inlined dynamic imports
 
 **Preload Scripts Configuration** [electron.vite.config.ts34-49](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/electron.vite.config.ts#L34-L49)

 
 - Two entry points: `src/preload/index.ts` and `src/preload/floating-preload.ts`
 - Externalizes all dependencies for security
 - Configures `@shared` path alias
 - Output: `out/preload/index.js` and `out/preload/floating-preload.js`
 
 **Renderer Process Configuration** [electron.vite.config.ts50-101](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/electron.vite.config.ts#L50-L101)

 
 - Multiple HTML entry points: 
 - `src/renderer/shell/index.html` - Main shell interface
 - `src/renderer/index.html` - Main window
 - `src/renderer/floating/index.html` - Floating window
 - `src/renderer/splash/index.html` - Splash screen
 - Vite plugins: 
 - `tailwindcss()` - Tailwind CSS v4 integration
 - `monacoEditorPlugin` - Monaco editor with worker configuration
 - `vue()` - Vue.js 3 support
 - `svgLoader()` - SVG component loading
 - `vueDevTools()` - Vue DevTools integration
 - Path aliases: `@` → `src/renderer/src`, `@shell` → `src/renderer/shell`, `@shadcn` → `src/shadcn`
 - Build optimization: `cssCodeSplit: false` to prevent CSS order issues
 
 **Sources:** [electron.vite.config.ts1-102](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/electron.vite.config.ts#L1-L102)

 
### Native Module Handling

 DeepChat includes native Node.js modules that require special handling during builds:

 
| Module | Purpose | Build Handling |
|---|---|---|
| sharp | Image processing | External (not bundled), platform-specific binary |
| @duckdb/node-api | Vector database | External, alpha version 1.3.2-alpha.25 |
| better-sqlite3-multiple-ciphers | SQLite with encryption | Rebuilt by electron-builder |

 The `pnpm.onlyBuiltDependencies` configuration [package.json191-197](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/package.json#L191-L197) ensures these modules are built correctly for the target platform.

 **Sources:** [package.json59-98](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/package.json#L59-L98) [package.json190-205](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/package.json#L190-L205) [electron.vite.config.ts26](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/electron.vite.config.ts#L26-L26)

 
## Initial Configuration

 After installation, DeepChat requires initial setup to configure LLM providers and enable core functionality. The application uses `electron-store` for persistent configuration storage and provides a Vue.js-based settings interface.

 
### First Launch Configuration Steps

 
 - **Launch Application**: Start DeepChat from your applications menu
 - **Initial UI Load**: The application loads `src/renderer/index.html` as the main entry point
 - **Access Settings**: Click the settings icon in the sidebar or use keyboard shortcut
 - **Configure Model Providers**: Navigate to Settings → Model Providers
 - **Add API Keys**: Enter API keys for providers (OpenAI, Anthropic, Gemini, etc.)
 - **Select Default Model**: Choose a default model for new conversations
 
 **Application Initialization Flow**

 
```

```

 **Sources:** [src/renderer/src/main.ts1-30](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/src/renderer/src/main.ts#L1-L30) [electron.vite.config.ts92-98](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/electron.vite.config.ts#L92-L98)

 
### Configuration Storage Architecture

 DeepChat uses a layered configuration system:

 
| Layer | Technology | Storage Location | Purpose |
|---|---|---|---|
| Main Process | electron-store | User data directory | Persistent settings (API keys, preferences) |
| Renderer State | Pinia useSettingsStore | Memory | Reactive UI state |
| Database | SQLite via better-sqlite3 | User data directory | Conversation history, messages |
| Vector Store | DuckDB | User data directory | Knowledge base embeddings |

 Configuration is accessed through the `ConfigPresenter` class in the main process, which is exposed to the renderer via IPC.

 **Sources:** [package.json77](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/package.json#L77-L77) [package.json71](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/package.json#L71-L71)

 
### Required Configuration for First Use

 **Minimum Configuration:**

 
 - At least one LLM provider API key (OpenAI, Anthropic, Gemini, DeepSeek, or local Ollama)
 - Default model selection
 
 **Optional Configuration:**

 
 - MCP servers for tool integration
 - Knowledge base setup for RAG
 - Web search API keys
 - Network proxy settings
 - Custom system prompts
 
 For detailed provider configuration, see page 3.2 (Provider and Model Configuration). For MCP setup, see page 6.4 (MCP Configuration System).

 **Sources:** [src/renderer/src/main.ts13-18](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/src/renderer/src/main.ts#L13-L18)

 
## Verification and Testing

 
### Verify Installation

 
 - **Application Launch**: Ensure DeepChat starts without errors
 - **Create New Conversation**: Click the "+" button to create a new chat
 - **Model Selection**: Verify configured models appear in the model selector
 - **Basic Chat Test**: Send a test message to verify LLM connectivity
 
 
### Common Setup Issues

 
| Issue | Cause | Solution |
|---|---|---|
| pnpm operations fail on Windows | Missing symlink permissions | Enable Developer Mode or use admin account |
| "No module named 'distutils'" | Missing Python setuptools | Run pip install setuptools |
| Electron app won't start | Missing dependencies | Re-run pnpm install and pnpm run installRuntime |
| Build fails on macOS | Code signing requirements | Follow Mac Release Guide procedures |

 
### Development Verification

 
```

```

 **Sources:** [README.md275](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/README.md#L275-L275) [README.md264](https://github.com/thinkinaixyz/deepchat/blob/ed3e2bd2/README.md#L264-L264)
