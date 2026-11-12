<!-- source: DeepWiki mcp.deepwiki.com · repo btriapitsyn/openchamber · page 3 Architecture · fetched 2026-10-26 -->

# Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CHANGELOG.md](CHANGELOG.md)
- [bun.lock](bun.lock)
- [package.json](package.json)
- [packages/desktop/package.json](packages/desktop/package.json)
- [packages/desktop/src-tauri/Cargo.lock](packages/desktop/src-tauri/Cargo.lock)
- [packages/desktop/src-tauri/Cargo.toml](packages/desktop/src-tauri/Cargo.toml)
- [packages/desktop/src-tauri/src/main.rs](packages/desktop/src-tauri/src/main.rs)
- [packages/desktop/src-tauri/tauri.conf.json](packages/desktop/src-tauri/tauri.conf.json)
- [packages/ui/package.json](packages/ui/package.json)
- [packages/ui/src/App.tsx](packages/ui/src/App.tsx)
- [packages/ui/src/lib/api/types.ts](packages/ui/src/lib/api/types.ts)
- [packages/vscode/CHANGELOG.md](packages/vscode/CHANGELOG.md)
- [packages/vscode/package.json](packages/vscode/package.json)
- [packages/vscode/src/bridge.ts](packages/vscode/src/bridge.ts)
- [packages/web/package.json](packages/web/package.json)
- [packages/web/server/index.js](packages/web/server/index.js)

</details>



## Overview

OpenChamber is a multi-platform AI coding assistant that runs as a native desktop application (Tauri), web application (Express + browser), and VS Code extension. All three platforms share the same React UI layer (`@openchamber/ui` package) and integrate with the OpenCode backend for AI agent orchestration.

This page covers the high-level architectural patterns and design decisions. For detailed implementation:

- Multi-platform deployment strategies → [Multi-Platform Deployment](#3.1)
- OpenCode SDK integration and process management → [OpenCode Backend Integration](#3.2)
- SSE streaming and HTTP communication → [Real-Time Communication](#3.3)
- Zustand stores and state persistence → [State Management](#3.4)
- Platform-specific details: [Desktop Application](#4), [Web Application](#5), [VS Code Extension](#6)

## Monorepo Structure

OpenChamber is organized as a Bun workspace with four packages:

```mermaid
graph TB
    Root["openchamber-monorepo<br/>package.json"]
    
    subgraph Packages["packages/"]
        UI["ui/<br/>@openchamber/ui<br/>Shared React components<br/>Zustand stores"]
        Web["web/<br/>@openchamber/web<br/>Express server<br/>npm CLI package"]
        Desktop["desktop/<br/>@openchamber/desktop<br/>Tauri application<br/>src-tauri/Cargo.toml"]
        VSCode["vscode/<br/>openchamber<br/>VS Code extension<br/>VSIX package"]
    end
    
    Root --> UI
    Root --> Web
    Root --> Desktop
    Root --> VSCode
    
    Web -.->|"imports"| UI
    Desktop -.->|"bundles"| Web
    VSCode -.->|"imports"| UI
```

**Package responsibilities:**

| Package | Type | Main Entry | Exports |
|---------|------|------------|---------|
| `@openchamber/ui` | Library | `src/main.tsx` | React components, hooks, stores |
| `@openchamber/web` | Application + CLI | `server/index.js` | Express server, `openchamber` CLI |
| `@openchamber/desktop` | Application | `src-tauri/src/main.rs` | Native installers (.dmg, .app) |
| `openchamber` (vscode) | Extension | `src/extension.ts` | VS Code extension (.vsix) |

**Sources:** [package.json:1-10](), [packages/ui/package.json:1-12](), [packages/web/package.json:1-12](), [packages/desktop/package.json:1-11](), [packages/vscode/package.json:1-40]()

---

## Core Architecture Layers

OpenChamber's architecture consists of three primary layers:

### Layer 1: Platform Runtime

Each platform provides a runtime environment with platform-specific capabilities:

```mermaid
graph LR
    subgraph Platform["Platform Layer"]
        DesktopRuntime["Desktop Runtime<br/>Tauri backend<br/>src-tauri/src/main.rs"]
        WebRuntime["Web Runtime<br/>Express server<br/>server/index.js"]
        VSCodeRuntime["VS Code Runtime<br/>Extension host<br/>src/extension.ts"]
    end
    
    subgraph Capabilities["RuntimeAPIs Implementation"]
        SettingsAPI["SettingsAPI<br/>load() / save()"]
        TerminalAPI["TerminalAPI<br/>createSession() / connect()"]
        GitAPI["GitAPI<br/>getGitStatus() / createGitCommit()"]
        GitHubAPI["GitHubAPI<br/>createPullRequest()"]
    end
    
    DesktopRuntime -->|"implements"| SettingsAPI
    DesktopRuntime -->|"implements"| TerminalAPI
    DesktopRuntime -->|"implements"| GitAPI
    
    WebRuntime -->|"implements"| SettingsAPI
    WebRuntime -->|"implements"| TerminalAPI
    WebRuntime -->|"implements"| GitAPI
    WebRuntime -->|"implements"| GitHubAPI
    
    VSCodeRuntime -->|"implements"| SettingsAPI
    VSCodeRuntime -->|"implements"| GitAPI
    VSCodeRuntime -->|"implements"| GitHubAPI
```

The `RuntimeAPIs` interface defines the contract between the UI and platform-specific functionality. Each platform implements this interface differently based on its capabilities.

**Sources:** [packages/ui/src/lib/api/types.ts:1-50](), [packages/desktop/src-tauri/src/main.rs:378-437](), [packages/web/server/index.js:1-100](), [packages/vscode/src/bridge.ts:1-100]()

### Layer 2: Shared UI Layer

The `@openchamber/ui` package contains all React components and state management logic:

```mermaid
graph TB
    subgraph UI["@openchamber/ui"]
        App["App.tsx<br/>Main application entry"]
        
        subgraph Layouts["Layout Components"]
            MainLayout["MainLayout<br/>Desktop/Web layout"]
            VSCodeLayout["VSCodeLayout<br/>Extension layout"]
        end
        
        subgraph Stores["Zustand Stores"]
            SessionStore["useSessionStore<br/>sessions, activeSessionId"]
            MessageStore["useMessageStore<br/>messages by session"]
            ConfigStore["useConfigStore<br/>providers, models, agents"]
            UIStore["useUIStore<br/>theme, sidebar state"]
        end
        
        subgraph Hooks["Core Hooks"]
            EventStream["useEventStream<br/>SSE event processing"]
            Router["useRouter<br/>URL state sync"]
        end
    end
    
    App --> MainLayout
    App --> VSCodeLayout
    
    MainLayout --> Stores
    VSCodeLayout --> Stores
    
    Stores --> EventStream
    EventStream --> Router
```

**Key files:**
- Entry point: [packages/ui/src/App.tsx:1-328]()
- Store definitions: `packages/ui/src/stores/`
- Layout components: `packages/ui/src/components/layout/`

**Sources:** [packages/ui/src/App.tsx:1-70](), [packages/ui/package.json:1-30]()

### Layer 3: OpenCode Backend

Each platform spawns and manages its own OpenCode CLI process:

```mermaid
graph TB
    subgraph Platforms["Platform Runtimes"]
        Desktop["Desktop<br/>OpenCodeManager struct"]
        Web["Web<br/>createOpencodeServer()"]
        VSCode["VS Code<br/>OpenCodeManager class"]
    end
    
    subgraph OpenCode["OpenCode Process (Per Platform)"]
        CLI["opencode CLI<br/>Dynamic port assignment"]
        HTTPServer["HTTP Server<br/>/config, /session, /agent"]
        SSEEndpoint["/event Endpoint<br/>Server-Sent Events"]
    end
    
    subgraph External["External Services"]
        Providers["AI Providers<br/>OpenAI, Anthropic, Google"]
    end
    
    Desktop -->|"spawn process"| CLI
    Web -->|"@opencode-ai/sdk/server"| CLI
    VSCode -->|"@opencode-ai/sdk/server"| CLI
    
    CLI --> HTTPServer
    CLI --> SSEEndpoint
    
    HTTPServer -->|"agent execution"| Providers
```

**Sources:** [packages/web/server/index.js:1424-1476](), [packages/desktop/src-tauri/src/main.rs:1-100](), [packages/vscode/src/opencode.ts]() (referenced in extension.ts)

---

## Request Flow Example

Here's how a typical user action flows through the system:

### Example: Send Chat Message

```mermaid
sequenceDiagram
    participant User
    participant ChatInput["ChatInput.tsx"]
    participant SessionStore["useSessionStore"]
    participant RuntimeAPI["RuntimeAPIs"]
    participant OpenCode["OpenCode HTTP API"]
    participant EventStream["useEventStream"]
    
    User->>ChatInput: Type message + press Enter
    ChatInput->>SessionStore: sendMessage(content)
    SessionStore->>SessionStore: Add optimistic message
    SessionStore->>RuntimeAPI: opencodeClient.sendMessage()
    RuntimeAPI->>OpenCode: POST /session/:id/prompt_async
    OpenCode-->>RuntimeAPI: 200 OK (non-blocking)
    
    Note over OpenCode,EventStream: AI processes request
    
    OpenCode->>EventStream: SSE: message.part.created
    EventStream->>SessionStore: addStreamingPart()
    SessionStore->>ChatInput: Re-render with streaming part
    
    OpenCode->>EventStream: SSE: message.part.updated (chunk)
    EventStream->>SessionStore: updateStreamingPart()
    SessionStore->>ChatInput: Re-render with new chunk
    
    OpenCode->>EventStream: SSE: message.updated (complete)
    EventStream->>SessionStore: completeStreamingMessage()
    SessionStore->>ChatInput: Final render
```

**Key code entities:**
- User interaction: `packages/ui/src/components/chat/ChatInput.tsx`
- Message sending: `useSessionStore.sendMessage()` in stores
- OpenCode client: `packages/ui/src/lib/opencode/client.ts`
- Event processing: [packages/ui/src/hooks/useEventStream.ts]()

**Sources:** [packages/web/server/index.js:1125-1203](), [packages/ui/src/lib/api/types.ts:21-24]()

## Platform Deployment Strategies

OpenChamber runs on three platforms with different deployment and runtime characteristics. See [Multi-Platform Deployment](#3.1) for detailed implementation.

### Platform Comparison

| Platform | Runtime | UI Rendering | OpenCode Integration | Distribution |
|----------|---------|--------------|---------------------|--------------|
| **Desktop** | Tauri + Rust | WebView (WKWebView) | Process spawn via Rust | .dmg / .app bundles |
| **Web** | Node.js/Bun + Express | Browser | `createOpencodeServer()` from SDK | npm package |
| **VS Code** | Extension Host | Webview panel | `createOpencodeServer()` from SDK | .vsix package |

### Runtime Detection

The UI layer detects which platform it's running on using the `RuntimeDescriptor` interface:

```typescript
interface RuntimeDescriptor {
  platform: 'web' | 'desktop' | 'vscode';
  isDesktop: boolean;
  isVSCode: boolean;
  label?: string;
}
```

**Platform-specific code paths:**
- Desktop: [packages/ui/src/App.tsx:58-64]() checks `apis.runtime.isVSCode` and `isDesktopShell()`
- VS Code: [packages/ui/src/App.tsx:271-302]() renders `VSCodeLayout` instead of `MainLayout`
- Web: Default rendering path when neither desktop nor VS Code

**Sources:** [packages/ui/src/lib/api/types.ts:3-13](), [packages/ui/src/App.tsx:46-70]()

## OpenCode Integration Pattern

Each platform spawns its own OpenCode CLI process and manages its lifecycle independently. See [OpenCode Backend Integration](#3.2) for detailed implementation.

### Process Management

```mermaid
graph TB
    subgraph Desktop["Desktop Platform"]
        DesktopMain["main.rs"]
        OpenCodeManager["OpenCodeManager struct"]
        HealthWatchdog["Health watchdog<br/>(15s interval)"]
    end
    
    subgraph Web["Web Platform"]
        WebServer["server/index.js"]
        SDK["createOpencodeServer()<br/>@opencode-ai/sdk"]
        RestartLogic["Restart logic<br/>with grace period"]
    end
    
    subgraph VSCode["VS Code Platform"]
        Extension["extension.ts"]
        OpenCodeMgr["OpenCodeManager class"]
        BridgeLogic["Bridge to webview"]
    end
    
    subgraph OpenCodeProcess["OpenCode CLI (Per Platform)"]
        Process["opencode process<br/>Dynamic port"]
        HTTPApi["HTTP API<br/>/config /session /event"]
    end
    
    OpenCodeManager -->|"spawn"| Process
    SDK -->|"spawn"| Process
    OpenCodeMgr -->|"spawn"| Process
    
    HealthWatchdog -->|"monitor"| HTTPApi
    RestartLogic -->|"respawn on failure"| Process
    BridgeLogic -->|"proxy requests"| HTTPApi
```

**Key responsibilities per platform:**
- **Desktop**: Direct process management in Rust, no intermediate SDK
- **Web/VS Code**: Use `@opencode-ai/sdk/server` for process spawning and lifecycle
- **All platforms**: Dynamic port detection, health monitoring, automatic restart on crash

**Sources:** [packages/web/server/index.js:1424-1476](), [packages/desktop/src-tauri/src/main.rs:766-820](), [packages/vscode/src/opencode.ts]() (referenced)

## Communication Patterns

OpenChamber uses a dual-channel model: HTTP for commands and SSE for streaming. See [Real-Time Communication](#3.3) for detailed protocol implementation.

### HTTP Request Proxying

Each platform proxies HTTP requests from the UI to OpenCode's HTTP API:

```mermaid
graph LR
    UI["React UI<br/>opencodeClient"]
    
    subgraph Proxies["Platform Proxies"]
        DesktopProxy["Desktop: Axum server<br/>127.0.0.1:dynamic"]
        WebProxy["Web: http-proxy-middleware<br/>Express"]
        VSCodeBridge["VS Code: postMessage bridge<br/>extension host"]
    end
    
    subgraph OpenCodeAPI["OpenCode HTTP API"]
        Config["/config<br/>GET providers/models"]
        Session["/session/:id/prompt_async<br/>POST message"]
        Event["/event<br/>SSE stream"]
    end
    
    UI -->|"fetch()"| DesktopProxy
    UI -->|"fetch()"| WebProxy
    UI -->|"postMessage()"| VSCodeBridge
    
    DesktopProxy --> Config
    WebProxy --> Config
    VSCodeBridge --> Config
    
    DesktopProxy --> Session
    WebProxy --> Session
    VSCodeBridge --> Session
```

**Key API endpoints:**
- `/config` - Provider and model metadata
- `/session/:id/prompt_async` - Non-blocking message send
- `/session/:id/message` - Message history retrieval
- `/event` - SSE stream for real-time updates

**Sources:** [packages/desktop/src-tauri/src/main.rs:1073-1101](), [packages/web/server/index.js:1760-1868](), [packages/vscode/src/bridge.ts:49-96]()

### SSE Event Processing

The `useEventStream` hook processes SSE events and routes them to appropriate Zustand stores:

```mermaid
graph TB
    OpenCodeEvent["OpenCode /event endpoint"]
    
    subgraph EventProcessing["Event Processing"]
        EventSource["EventSource connection<br/>or platform bridge"]
        useEventStream["useEventStream hook"]
        EventRouter["Event type router"]
    end
    
    subgraph StoreUpdates["Store Updates"]
        MessageStore["useMessageStore<br/>addStreamingPart()<br/>completeStreamingMessage()"]
        SessionStore["useSessionStore<br/>addPermission()<br/>updateSessionStatus()"]
        ConfigStore["useConfigStore<br/>updateProviders()"]
    end
    
    OpenCodeEvent -->|"SSE stream"| EventSource
    EventSource -->|"parse JSON"| useEventStream
    useEventStream --> EventRouter
    
    EventRouter -->|"message.part.*"| MessageStore
    EventRouter -->|"permission.asked"| SessionStore
    EventRouter -->|"session.status"| SessionStore
    EventRouter -->|"mcp.tools.changed"| ConfigStore
```

**Event types and handlers:**
- `message.part.created` / `message.part.updated` → Stream message chunks
- `message.updated` → Mark message complete
- `permission.asked` → Show permission dialog
- `session.status` → Update session running/idle state

**Sources:** [packages/web/server/index.js:1125-1203](), [packages/ui/src/hooks/useEventStream.ts]() (referenced)

## State Management Architecture

OpenChamber uses Zustand for state management with domain-specific stores. See [State Management](#3.4) for detailed implementation.

### Store Organization

```mermaid
graph TB
    subgraph Stores["Zustand Stores (packages/ui/src/stores/)"]
        SessionStore["useSessionStore<br/>sessions[], activeSessionId<br/>permissions[]"]
        MessageStore["useMessageStore<br/>messagesBySession<br/>streamingParts"]
        ConfigStore["useConfigStore<br/>providers[], models[]<br/>agents[], defaults"]
        UIStore["useUIStore<br/>theme, sidebarVisible<br/>activeTab"]
        DirectoryStore["useDirectoryStore<br/>currentDirectory<br/>projects[]"]
        GitStore["useGitStore<br/>status, branches<br/>remotes[]"]
    end
    
    subgraph Hooks["Core Hooks"]
        EventStream["useEventStream<br/>SSE event routing"]
        Router["useRouter<br/>URL synchronization"]
    end
    
    subgraph Persistence["Persistence"]
        SettingsAPI["RuntimeAPIs.settings<br/>load() / save()"]
    end
    
    EventStream -->|"update"| SessionStore
    EventStream -->|"update"| MessageStore
    EventStream -->|"update"| ConfigStore
    
    Router -->|"sync URL"| SessionStore
    Router -->|"sync URL"| UIStore
    
    SessionStore -->|"persist"| SettingsAPI
    UIStore -->|"persist"| SettingsAPI
    DirectoryStore -->|"persist"| SettingsAPI
```

**Key stores:**
- `useSessionStore` - Session list, active session, permissions
- `useMessageStore` - Message history, streaming chunks
- `useConfigStore` - Providers, models, agents, MCP tools
- `useUIStore` - Theme, sidebar, dialog state
- `useDirectoryStore` - Active project, workspace switching
- `useGitStore` - Git status, branches, commit history

**Sources:** [packages/ui/src/lib/api/types.ts:353-384](), [packages/ui/src/App.tsx:10-18]()

### State Update Flow

```mermaid
sequenceDiagram
    participant SSE["SSE /event stream"]
    participant Hook["useEventStream"]
    participant Store["Zustand Store"]
    participant Component["React Component"]
    
    SSE->>Hook: Event: message.part.updated
    Hook->>Hook: Parse event type + payload
    Hook->>Store: addStreamingPart(sessionId, part)
    Store->>Store: Update state (immutable)
    Store-->>Component: Trigger re-render
    Component-->>Component: Display new chunk
```

Store updates are immutable and trigger React re-renders via Zustand's subscription mechanism. Components subscribe to specific store slices to minimize unnecessary renders.

**Sources:** [packages/web/server/index.js:1125-1203]()

## Cross-Cutting Concerns

### Configuration Hierarchy

OpenCode backend configuration (agents, models) has a three-tier override system:

1. **Built-in** - Bundled with `opencode` CLI
2. **User-level** - `~/.config/opencode/agents/`, `~/.config/opencode/commands/`
3. **Project-level** - `.opencode/agents/`, `.opencode/commands/`

Application settings (theme, projects, defaults) are persisted per platform via `RuntimeAPIs.settings`:

- **Desktop**: Tauri store plugin
- **Web**: `~/.config/openchamber/settings.json`
- **VS Code**: Extension `globalState`

**Sources:** [packages/ui/src/lib/api/types.ts:353-384](), [packages/web/server/index.js:1054-1079]()

### OpenCode API Prefix Detection

OpenCode can serve its API at different prefixes (`/api`, `/`, etc.). Each platform detects the prefix on startup:

1. Fetch `/doc` and extract `__OPENCODE_API_BASE__` from HTML
2. Fallback: Try `/config`, then `/api/config`
3. Environment override: `OPENCODE_API_PREFIX` env var

**Implementation:**
- Desktop: Rust-based detection in `OpenCodeManager`
- Web: [packages/web/server/index.js:1226-1368]()

**Sources:** [packages/web/server/index.js:940-948](), [packages/web/server/index.js:1059-1079]()

### Health Monitoring

Platforms monitor OpenCode process health and emit status updates:

- **Desktop**: 15s polling interval, emits `openchamber:health-changed` events
- **Web**: HTTP 503 during restart, grace period before marking unhealthy
- **VS Code**: Health checks during API initialization

**Sources:** [packages/desktop/src-tauri/src/main.rs:766-820](), [packages/web/server/index.js:1549-1639]()

---

## Summary

OpenChamber's architecture achieves multi-platform deployment through:

1. **Shared UI Layer**: `@openchamber/ui` package with React components and Zustand stores
2. **Platform Adapters**: Each platform implements `RuntimeAPIs` interface with platform-specific capabilities
3. **Unified Backend**: All platforms integrate with OpenCode via HTTP + SSE
4. **Independent Instances**: Each platform spawns and manages its own OpenCode process
5. **Dynamic Configuration**: API prefix detection and health monitoring for resilient operation

This architecture allows OpenChamber to run natively on macOS (Desktop), in any browser (Web), and integrated into VS Code (Extension), while maintaining a consistent user experience and feature set across all platforms.

---

