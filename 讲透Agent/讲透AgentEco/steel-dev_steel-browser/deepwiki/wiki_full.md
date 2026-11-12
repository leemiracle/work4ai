# Page: Overview

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Dockerfile](Dockerfile)
- [README.md](README.md)
- [api/package.json](api/package.json)
- [images/star_img.png](images/star_img.png)
- [package-lock.json](package-lock.json)
- [package.json](package.json)
- [render.yaml](render.yaml)

</details>



This document provides a high-level introduction to the steel-browser system, explaining its purpose, core architecture, and major components. For detailed information on specific subsystems, refer to the corresponding sections: [System Architecture](#1.1) for architectural details, [Key Features](#1.2) for capability descriptions, and [Monorepo Structure](#1.3) for workspace organization.

## Purpose and Scope

Steel-browser is an open-source browser API designed to enable AI agents and applications to interact with the web programmatically [README.md:10-14](). It manages the complexity of browser infrastructure, including sessions, processes, and anti-detection, allowing developers to focus on application logic [README.md:47-49]().

**Sources:** [README.md:1-70](), [package.json:1-40]()

## What is Steel Browser

Steel-browser is a comprehensive browser automation infrastructure built on Chrome DevTools Protocol (CDP) and Puppeteer [README.md:50-50](). It provides a REST API and WebSocket interface for controlling Chrome browser instances, maintaining state across requests, and performing common web automation tasks.

### Core Capabilities

| Capability | Description | Implementation |
|------------|-------------|----------------|
| **Full Browser Control** | Complete control via Puppeteer and CDP; compatible with Playwright and Selenium | `puppeteer-core`, `CDPService` |
| **Session Management** | Maintains cookies, local storage, and state across requests | `SessionService` |
| **Proxy Support** | Built-in proxy chain management for IP rotation | `proxy-chain`, `ProxyFactory` |
| **Anti-Detection** | Includes stealth plugins and fingerprint management | `fingerprint-generator`, `fingerprint-injector` |
| **Browser Tools** | APIs to convert pages to Markdown, Readability, screenshots, or PDFs | Action route handlers |
| **Debugging Tools** | Built-in request logging and a UI for session debugging | `BrowserLogger`, `ui` workspace |

**Sources:** [README.md:45-58](), [api/package.json:66-113]()

## System Architecture

The steel-browser system is organized as a Node.js monorepo consisting of an API server, a management UI, and a REPL for testing [package.json:8-12]().

### High-Level Component Architecture

```mermaid
graph TB
    subgraph "External Clients"
        HTTPClient["HTTP/REST Clients"]
        WSClient["WebSocket Clients"]
        PuppeteerClient["Puppeteer/Playwright<br/>Direct CDP Clients"]
    end
    
    subgraph "steel-browser Monorepo"
        subgraph "API Workspace (api/)"
            FastifyApp["Fastify Application<br/>api/src/index.ts"]
            
            subgraph "Route Layer (api/src/routes/)"
                SessionRoutes["sessions.ts<br/>/v1/sessions/*"]
                ActionRoutes["actions.ts<br/>/v1/scrape, screenshot, pdf"]
                FileRoutes["files.ts<br/>/v1/sessions/:id/files"]
            end
            
            subgraph "Service Layer (api/src/services/)"
                SessionService["SessionService<br/>session/session-service.ts"]
                CDPService["CDPService<br/>cdp/cdp-service.ts"]
            end
            
            subgraph "Infrastructure (api/src/)"
                PluginManager["PluginManager<br/>services/cdp/plugins/core/plugin-manager.ts"]
                WSServer["WebSocket Server<br/>plugins/browser-socket.ts"]
                BrowserLogger["BrowserLogger<br/>plugins/logging/browser-logger.ts"]
            end
        end
        
        subgraph "UI Workspace (ui/)"
            ReactApp["React Application<br/>ui/src/"]
        end
        
        subgraph "REPL Workspace (repl/)"
            REPLScript["Interactive Script<br/>repl/src/script.ts"]
        end
    end
    
    subgraph "External Dependencies"
        ChromeBrowser["Chrome/Chromium<br/>CDP Port 9222/9223"]
        DuckDB["DuckDB<br/>browser-logs.duckdb"]
    end
    
    HTTPClient -->|"HTTP"| FastifyApp
    WSClient -->|"WebSocket"| WSServer
    PuppeteerClient -->|"CDP"| ChromeBrowser
    
    ReactApp -->|"HTTP/WS"| FastifyApp
    REPLScript -->|"Puppeteer"| ChromeBrowser
    
    FastifyApp --> SessionRoutes
    FastifyApp --> ActionRoutes
    FastifyApp --> FileRoutes
    
    SessionRoutes --> SessionService
    ActionRoutes --> SessionService
    
    SessionService --> CDPService
    CDPService -->|"Controls"| ChromeBrowser
    CDPService --> PluginManager
    CDPService --> BrowserLogger
    
    BrowserLogger --> DuckDB
```

**Sources:** [api/package.json:8-39](), [package.json:8-12](), [README.md:109-156]()

### Technology Stack

```mermaid
graph LR
    subgraph "Runtime"
        NodeJS["Node.js >=22"]
        Chrome["Chrome/Chromium"]
    end
    
    subgraph "Core Dependencies"
        Fastify["fastify ^5.2.1"]
        Puppeteer["puppeteer-core 23.6.0"]
        Zod["zod ^3.24.2"]
    end
    
    subgraph "Storage"
        DuckDBAsync["duckdb-async ^1.1.3"]
        Level["level ^9.0.0"]
    end
    
    NodeJS --> Fastify
    NodeJS --> Puppeteer
    Puppeteer --> Chrome
    Fastify --> Zod
    
    CDPService["CDPService"] --> Puppeteer
    BrowserLogger["BrowserLogger"] --> DuckDBAsync
```

**Sources:** [package.json:27-36](), [api/package.json:72-113]()

## Core Service Layer

The service layer implements the logic for browser orchestration and lifecycle management. For details, see [System Architecture](#1.1).

*   **`SessionService`**: Orchestrates browser sessions, manages proxies, and handles high-level session lifecycle [api/package.json:11-13]().
*   **`CDPService`**: Manages the low-level Chrome DevTools Protocol connection, browser launches, and page instrumentation [api/package.json:15-19]().
*   **`BrowserLogger`**: Captures browser events and persists them to DuckDB for debugging and monitoring [api/package.json:21-25]().

**Sources:** [api/package.json:8-39]()

## Monorepo Structure

The codebase is organized into three primary workspaces to separate concerns. For details, see [Monorepo Structure](#1.3).

*   **`api/`**: The core Fastify server. It contains the browser automation logic, CDP integration, and the REST/WebSocket endpoints [api/package.json:1-7]().
*   **`ui/`**: A React-based dashboard for viewing and debugging live browser sessions [README.md:94-94]().
*   **`repl/`**: A workspace for interactive script development and testing [package.json:11-11]().

**Sources:** [package.json:8-12](), [README.md:109-115]()

## Key Features

Steel-browser includes several advanced features for modern web automation. For details, see [Key Features](#1.2).

*   **Anti-Detection**: Uses `fingerprint-generator` and `fingerprint-injector` to avoid bot detection [api/package.json:93-94]().
*   **Proxy Chaining**: Supports complex proxy configurations via `proxy-chain` [api/package.json:107-107]().
*   **Content Conversion**: Built-in support for converting web pages to Markdown (via Turndown) and PDF [api/package.json:81-83](), [api/package.json:104-104]().
*   **Extension Support**: Ability to load custom Chrome extensions into sessions [README.md:53-53]().

**Sources:** [README.md:45-58](), [api/package.json:72-113]()

## Deployment

Steel-browser is distributed as a Docker image that bundles the API, UI, and necessary system dependencies like Chromium and Xvfb [Dockerfile:72-108]().

*   **Docker**: The primary deployment method, supporting both combined and separate API/UI containers [README.md:87-101]().
*   **Cloud**: Support for 1-click deployments to Railway and Render [README.md:76-81](), [render.yaml:1-6]().

**Sources:** [Dockerfile:1-126](), [README.md:70-108](), [render.yaml:1-18]()

---

# Page: System Architecture

# System Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [api/src/services/cdp/cdp.service.ts](api/src/services/cdp/cdp.service.ts)
- [api/src/services/cdp/plugins/core/base-plugin.ts](api/src/services/cdp/plugins/core/base-plugin.ts)
- [api/src/services/cdp/plugins/core/plugin-manager.ts](api/src/services/cdp/plugins/core/plugin-manager.ts)
- [api/src/services/session.service.ts](api/src/services/session.service.ts)
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- [docs/DEVELOPMENT_SETUP.md](docs/DEVELOPMENT_SETUP.md)
- [docs/README.md](docs/README.md)
- [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)

</details>



Steel Browser is a containerized browser automation platform built as a TypeScript monorepo. The system provides programmatic browser control through RESTful APIs, WebSocket streaming, and direct CDP/Selenium interfaces. The architecture follows a layered service design with plugin extensibility, event-driven instrumentation, and comprehensive session management.

## Overview

The steel-browser repository is organized as a monorepo with three workspaces:

- **API Workspace** (`api/`) - Fastify server exposing REST/WebSocket APIs and managing browser sessions [api/src/server.ts:1-50]()
- **UI Workspace** (`ui/`) - React application for visual session management and monitoring [ui/src/main.tsx:1-20]()
- **REPL Workspace** (`repl/`) - Interactive scripts for direct browser automation [repl/src/index.ts:1-30]()

The API workspace contains the core system: route handlers, service layer (`CDPService`, `SessionService`), plugin architecture, and browser instrumentation.

### Monorepo Architecture

```mermaid
graph TB
    subgraph "External Clients"
        DirectHTTP["HTTP/REST Clients"]
        SDKClients["Node/Python SDKs"]
        BrowserUI["Web Browser"]
        AutomationTools["Puppeteer/Playwright<br/>Direct Automation"]
    end
    
    subgraph "steel-browser Monorepo"
        subgraph "UI Workspace (Port 5173)"
            ReactApp["React Application"]
            UIClient["Generated API Client<br/>(openapi-typescript)"]
        end
        
        subgraph "API Workspace (Port 3000)"
            FastifyServer["Fastify Server<br/>(api/src/server.ts)"]
            
            subgraph "Route Layer"
                sessionsRoutes["/v1/sessions"]
                actionsRoutes["/v1/scrape, /screenshot, /pdf"]
                filesRoutes["/v1/sessions/:id/files"]
                logsRoutes["/v1/logs"]
            end
            
            subgraph "Service Layer"
                SessionService["SessionService<br/>(session.service.ts)"]
                CDPService["CDPService<br/>(cdp/cdp.service.ts)"]
                FileService["FileService<br/>(file.service.ts)"]
                SeleniumService["SeleniumService<br/>(selenium.service.ts)"]
            end
            
            subgraph "Infrastructure"
                PluginManager["PluginManager<br/>(plugins/core/plugin-manager.ts)"]
                ProxyServer["ProxyServer<br/>(utils/proxy.ts)"]
                WebSocketRegistry["WebSocketRegistryService<br/>(websocket-registry.service.ts)"]
            end
        end
        
        subgraph "REPL Workspace"
            REPLScripts["Interactive Scripts<br/>(repl/src/index.ts)"]
        end
    end
    
    subgraph "External Systems"
        ChromeBrowser["Chrome/Chromium<br/>CDP Port 9222/9223"]
        ProxyServers["Upstream Proxy Servers"]
        Storage["DuckDB Logs<br/>File Storage<br/>Session Context"]
    end
    
    DirectHTTP --> FastifyServer
    SDKClients --> FastifyServer
    BrowserUI --> ReactApp
    AutomationTools --> ChromeBrowser
    
    ReactApp --> UIClient
    UIClient --> FastifyServer
    
    FastifyServer --> sessionsRoutes
    FastifyServer --> actionsRoutes
    FastifyServer --> filesRoutes
    FastifyServer --> logsRoutes
    
    sessionsRoutes --> SessionService
    actionsRoutes --> SessionService
    filesRoutes --> FileService
    logsRoutes --> CDPService
    
    SessionService --> CDPService
    SessionService --> SeleniumService
    SessionService --> ProxyServer
    
    CDPService --> PluginManager
    CDPService --> ChromeBrowser
    CDPService --> Storage
    
    ProxyServer --> ProxyServers
    FileService --> Storage
    
    REPLScripts --> ChromeBrowser
```

Sources: [api/src/server.ts:1-50](), [api/src/services/session.service.ts:58-91](), [api/src/services/cdp/cdp.service.ts:83-185](), [docs/ARCHITECTURE.md:5-24]()

## Core Service Layer

The API workspace implements a three-tier architecture: HTTP routes → controllers → service layer. The service layer contains core business logic and orchestrates browser automation through `CDPService` and `SessionService`.

### Service Layer Architecture

```mermaid
graph TB
    subgraph "Fastify Plugin Layer"
        steelBrowserPlugin["steelBrowserPlugin<br/>(steel-browser-plugin.ts)"]
        browserInstancePlugin["browserInstancePlugin<br/>(plugins/browser.ts)"]
    end
    
    subgraph "Core Services"
        SessionService["SessionService<br/>(session.service.ts:58)"]
        CDPService["CDPService<br/>(cdp/cdp.service.ts:83)"]
        SeleniumService["SeleniumService<br/>(selenium.service.ts)"]
        FileService["FileService<br/>(file.service.ts)"]
    end
    
    subgraph "CDPService Components"
        PluginManager["PluginManager<br/>(plugins/core/plugin-manager.ts:7)"]
        TargetInstrumentationManager["TargetInstrumentationManager<br/>(instrumentation/target-manager.ts)"]
        BrowserLogger["BrowserLogger<br/>(instrumentation/browser-logger.ts)"]
        ChromeContextService["ChromeContextService<br/>(context/chrome-context.service.ts)"]
    end
    
    subgraph "Support Services"
        ProxyServer["ProxyServer<br/>(utils/proxy.ts)"]
        TimezoneFetcher["TimezoneFetcher<br/>(timezone-fetcher.service.ts)"]
    end
    
    SessionService --> CDPService
    SessionService --> SeleniumService
    SessionService --> FileService
    SessionService --> ProxyServer
    SessionService --> TimezoneFetcher
    
    CDPService --> PluginManager
    CDPService --> TargetInstrumentationManager
    CDPService --> ChromeContextService
    TargetInstrumentationManager --> BrowserLogger
```

**Service Responsibilities:**

| Service | File | Primary Role |
|---------|------|-------------|
| `SessionService` | [api/src/services/session.service.ts:58]() | Manages session lifecycle, proxy setup, coordinates between CDP and Selenium modes. |
| `CDPService` | [api/src/services/cdp/cdp.service.ts:83]() | Controls Chrome via CDP, manages browser instances, handles page instrumentation. |
| `SeleniumService` | [api/src/services/selenium.service.ts]() | Provides WebDriver compatibility for Selenium clients. |
| `FileService` | [api/src/services/file.service.ts]() | Manages session file uploads/downloads and storage. |
| `PluginManager` | [api/src/services/cdp/plugins/core/plugin-manager.ts:7]() | Coordinates plugin lifecycle and ensure error isolation. |

Sources: [api/src/services/session.service.ts:58-80](), [api/src/services/cdp/cdp.service.ts:83-105](), [docs/ARCHITECTURE.md:28-115]()

## CDPService: Browser Orchestration Engine

The `CDPService` class [api/src/services/cdp/cdp.service.ts:83]() is the heart of Steel Browser. It manages the Puppeteer browser instance, handles fingerprinting, and coordinates the plugin system.

### CDPService Internal Architecture

```mermaid
graph TB
    subgraph "CDPService Class (cdp.service.ts)"
        InternalState["Internal State"]
        Managers["Component Managers"]
    end
    
    subgraph "Internal State Properties"
        browserInstance["browserInstance: Browser | null<br/>(line 87)"]
        wsEndpoint["wsEndpoint: string | null<br/>(line 88)"]
        primaryPage["primaryPage: Page | null<br/>(line 93)"]
        fingerprintData["fingerprintData: BrowserFingerprintWithHeaders | null<br/>(line 89)"]
        currentSessionConfig["currentSessionConfig: BrowserLauncherOptions | null<br/>(line 96)"]
    end
    
    subgraph "Managed Components"
        pluginManager["pluginManager: PluginManager<br/>(line 99)"]
        targetInstrumentationManager["targetInstrumentationManager:<br/>TargetInstrumentationManager<br/>(line 103)"]
        chromeSessionService["chromeSessionService:<br/>ChromeContextService<br/>(line 101)"]
        instrumentationLogger["instrumentationLogger: BrowserLogger<br/>(line 104)"]
    end
    
    CDPService --> pluginManager
    CDPService --> targetInstrumentationManager
    CDPService --> chromeSessionService
```

**Key Features:**
- **Lifecycle Management**: Handles `launch()`, `shutdown()`, and `refreshPrimaryPage()` [docs/ARCHITECTURE.md:44-46]().
- **Context Isolation**: Uses `ChromeContextService` to manage cookies, localStorage, and sessionStorage [api/src/services/cdp/cdp.service.ts:101]().
- **Instrumentation**: Uses `TargetInstrumentationManager` to capture browser events [api/src/services/cdp/cdp.service.ts:177-180]().

Sources: [api/src/services/cdp/cdp.service.ts:83-185](), [docs/ARCHITECTURE.md:28-56]()

## SessionService: Session Lifecycle Management

The `SessionService` [api/src/services/session.service.ts:58]() manages browser sessions with isolated contexts. It is responsible for creating sessions with custom configurations like proxies, user agents, and fingerprints.

### Session Lifecycle and State

The service maintains an `activeSession` [api/src/services/session.service.ts:67]() and a list of `pastSessions` [api/src/services/session.service.ts:66]().

```mermaid
stateDiagram-v2
    [*] --> idle: "Default State"
    idle --> live: "startSession()"
    live --> released: "endSession()"
    released --> [*]

    note right of live
        Session includes:
        - proxyServer (IProxyServer)
        - dimensions (width, height)
        - userAgent
        - fingerprint
    end note
```

**Session Creation Flow:**
1. **Timezone Resolution**: Fetches timezone early via `TimezoneFetcher` [api/src/services/session.service.ts:143-151]().
2. **Proxy Setup**: Initializes `ProxyServer` if a `proxyUrl` is provided [api/src/services/session.service.ts:208-211]().
3. **Configuration Merging**: Merges user preferences and browser options [api/src/services/session.service.ts:182-191]().
4. **Browser Launch**: Delegates to `CDPService` or `SeleniumService` [api/src/services/session.service.ts:213-235]().

Sources: [api/src/services/session.service.ts:58-243](), [docs/ARCHITECTURE.md:86-105]()

## Plugin System Architecture

Steel Browser's plugin architecture allows for extensible functionality (e.g., ad blocking, captcha solving) without modifying core code.

### Plugin Lifecycle Hooks

The `BasePlugin` [api/src/services/cdp/plugins/core/base-plugin.ts:27]() defines hooks that the `PluginManager` [api/src/services/cdp/plugins/core/plugin-manager.ts:7]() triggers during browser events:

| Hook | Trigger Point |
|------|---------------|
| `onBrowserLaunch` | When the browser process starts [api/src/services/cdp/plugins/core/plugin-manager.ts:96](). |
| `onBrowserReady` | After the browser is fully configured [api/src/services/cdp/plugins/core/plugin-manager.ts:107](). |
| `onPageCreated` | When a new page or tab is opened [api/src/services/cdp/plugins/core/plugin-manager.ts:123](). |
| `onPageNavigate` | Before a page navigates to a new URL [api/src/services/cdp/plugins/core/plugin-manager.ts:151](). |
| `onShutdown` | When the system is shutting down with a specific `ShutdownReason` [api/src/services/cdp/plugins/core/plugin-manager.ts:193](). |

### Plugin Manager Coordination

The `PluginManager` handles:
- **Registration**: Ensures plugins are uniquely named and injected with the `CDPService` [api/src/services/cdp/plugins/core/plugin-manager.ts:21-29]().
- **Error Isolation**: Wraps plugin calls in try-catch blocks to prevent a single plugin failure from crashing the browser session [api/src/services/cdp/plugins/core/plugin-manager.ts:59, 100, 128]().

Sources: [api/src/services/cdp/plugins/core/base-plugin.ts:9-55](), [api/src/services/cdp/plugins/core/plugin-manager.ts:7-217](), [docs/ARCHITECTURE.md:58-84]()

## API & Communication Layer

The backend uses **Fastify** for its REST and WebSocket API. Routes are organized by functionality:
- **Sessions** (`/v1/sessions/*`): Lifecycle management.
- **Actions** (`/v1/*`): High-level automation like `scrape`, `screenshot`, and `pdf`.
- **Files** (`/v1/files/*`): Session-scoped storage operations.

All API endpoints use **Zod** schemas for strict request and response validation [docs/ARCHITECTURE.md:202-212]().

Sources: [docs/ARCHITECTURE.md:172-212]()

---

# Page: Key Features

# Key Features

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Dockerfile](Dockerfile)
- [README.md](README.md)
- [api/src/modules/actions/actions.controller.ts](api/src/modules/actions/actions.controller.ts)
- [api/src/modules/actions/actions.routes.ts](api/src/modules/actions/actions.routes.ts)
- [api/src/modules/actions/actions.schema.ts](api/src/modules/actions/actions.schema.ts)
- [api/src/services/cdp/cdp.service.ts](api/src/services/cdp/cdp.service.ts)
- [api/src/services/cdp/plugins/core/base-plugin.ts](api/src/services/cdp/plugins/core/base-plugin.ts)
- [api/src/services/cdp/plugins/core/plugin-manager.ts](api/src/services/cdp/plugins/core/plugin-manager.ts)
- [api/src/services/selenium.service.ts](api/src/services/selenium.service.ts)
- [api/src/utils/passthough-proxy.ts](api/src/utils/passthough-proxy.ts)
- [api/src/utils/proxy.ts](api/src/utils/proxy.ts)
- [images/star_img.png](images/star_img.png)
- [render.yaml](render.yaml)

</details>



This page provides a comprehensive overview of steel-browser's capabilities, organized by functional area. Each feature is mapped to the underlying services and code components that implement it.

---

## Core Browser Automation

steel-browser provides full programmatic control over Chrome/Chromium instances through two protocol options:

### Chrome DevTools Protocol (CDP)

The primary automation interface uses Puppeteer-core and CDP for complete browser control. The `CDPService` class [api/src/services/cdp/cdp.service.ts:83-185]() manages the entire browser lifecycle.

**Key capabilities:**

| Feature | Implementation | Configuration |
|---------|---------------|---------------|
| Browser Launch | `CDPService.launch()` [api/src/services/cdp/cdp.service.ts:517-545]() | `BrowserLauncherOptions` |
| Page Management | `CDPService.createPage()` [api/src/services/cdp/cdp.service.ts:441-446]() | Automatic |
| Target Control | `TargetInstrumentationManager` [api/src/services/cdp/cdp.service.ts:177-180]() | Event-driven |
| Connection Management | WebSocket endpoint [api/src/services/cdp/cdp.service.ts:979-987]() | Auto-configured |

The system supports multiple connection methods [README.md:50-50]():
- **Puppeteer**: Native integration via `puppeteer-core` [api/src/services/cdp/cdp.service.ts:15-24]()
- **Playwright**: Via CDP endpoint with custom connection strings.
- **Direct CDP**: Raw DevTools Protocol via WebSocket.

**Browser Control Flow**
```mermaid
graph TB
    subgraph "ExternalClients"
        ["PuppeteerClient"]
        ["PlaywrightClient"]
        ["DirectCDPClient"]
    end
    
    subgraph "CDPServiceLayer"
        ["CDPService.launch()"]
        ["BrowserInstance"]
        ["WSEndpoint"]
        ["PageManager"]
    end
    
    subgraph "ChromeProcess"
        ["ChromeInstance"]
        ["CDPProtocol"]
    end
    
    ["PuppeteerClient"] -->|"puppeteer.connect()"| ["WSEndpoint"]
    ["PlaywrightClient"] -->|"chromium.connectOverCDP()"| ["WSEndpoint"]
    ["DirectCDPClient"] -->|"Raw WebSocket"| ["WSEndpoint"]
    
    ["CDPService.launch()"] --> ["BrowserInstance"]
    ["BrowserInstance"] -->|"controls"| ["ChromeInstance"]
    ["WSEndpoint"] -->|"proxies to"| ["CDPProtocol"]
    ["ChromeInstance"] -->|"exposes"| ["CDPProtocol"]
    ["PageManager"] -->|"manages"| ["ChromeInstance"]
```

**Sources:** [api/src/services/cdp/cdp.service.ts:83-185](), [api/src/services/cdp/cdp.service.ts:517-1024](), [README.md:50-50]()

### Selenium WebDriver Support

For teams with existing Selenium workflows, `SeleniumService` [api/src/services/selenium.service.ts]() provides WebDriver protocol compatibility:

- Launch sessions with `isSelenium: true` flag [api/src/services/session.service.ts:212-227]().
- Compatible with standard Selenium clients (Python, Java, Node.js).
- Maintains session state and proxy support.

**Sources:** [api/src/services/session.service.ts:212-227](), [api/src/services/selenium.service.ts]()

---

## Session & State Management

The `SessionService` [api/src/services/session.service.ts:50-300]() orchestrates session lifecycle and coordinates between CDP and Selenium modes.

### Session Lifecycle

```mermaid
graph LR
    ["POST /v1/sessions"] -->|"SessionService.startSession()"| ["ActiveSession"]
    ["ActiveSession"] -->|"status: 'live'"| ["POST /v1/sessions/:id/release"]
    ["POST /v1/sessions/:id/release"] -->|"SessionService.endSession()"| ["IdleState"]
    ["IdleState"] -->|"Cleanup & reset"| ["NewSession"]
```

**Session Creation Flow:**

1. **ID Generation**: UUID v4 assigned [api/src/services/session.service.ts:145-151]().
2. **Proxy Setup**: Optional `ProxyServer` instantiation [api/src/services/session.service.ts:159-162]().
3. **Browser Launch**: `CDPService.launch()` or `SeleniumService.launch()` [api/src/services/session.service.ts:212-242]().
4. **State Tracking**: Session details stored in `activeSession` [api/src/services/session.service.ts:59]().

**Sources:** [api/src/services/session.service.ts:85-243]()

### State Persistence

Sessions maintain persistent state (cookies, local storage) across requests [README.md:51-51](). Context injection occurs during session initialization [api/src/services/cdp/cdp.service.ts:932-950]() using the `sessionContext` parameter.

**Sources:** [api/src/services/cdp/cdp.service.ts:932-950](), [README.md:51-51]()

---

## Anti-Detection & Stealth Features

steel-browser implements multi-layered anti-detection to make automated browsers appear as regular user browsers [README.md:55-55]().

### Browser Fingerprinting

The fingerprinting system uses `fingerprint-generator` and `fingerprint-injector` [api/src/services/cdp/cdp.service.ts:3-9]() to create realistic browser fingerprints.

**Fingerprint Generation:** [api/src/services/cdp/cdp.service.ts:659-698]()
- Device type selection (desktop/mobile) via `deviceConfig`.
- Chrome version matching and realistic user agent strings.
- Screen dimensions matching session configuration.

**Fingerprint Injection:** [api/src/services/cdp/cdp.service.ts:356-364]()
- Executes before page load via `evaluateOnNewDocument()`.
- Overrides navigator properties (vendor, platform, hardware).
- Modifies WebGL renderer information.

**Sources:** [api/src/services/cdp/cdp.service.ts:659-698](), [api/src/services/cdp/cdp.service.ts:356-364](), [api/src/scripts/index.js]()

### Request Header Manipulation

The system filters and modifies HTTP headers to avoid detection [api/src/utils/browser.ts]():

**Header Filtering:** [api/src/services/cdp/cdp.service.ts:385-388]()
- Filters `accept-encoding`, `sec-fetch-*` headers via `filterHeaders()`.
- Injects custom headers via `customHeaders` configuration [api/src/services/cdp/cdp.service.ts:346-353]().

**Chrome Launch Arguments:** [api/src/services/cdp/cdp.service.ts:776-854]()
- `--disable-blink-features=AutomationControlled` removes automation flags.
- `--webrtc-ip-handling-policy=disable_non_proxied_udp` prevents IP leaks.

**Sources:** [api/src/services/cdp/cdp.service.ts:385-388](), [api/src/services/cdp/cdp.service.ts:776-854](), [api/src/utils/browser.ts]()

---

## Network & Proxy Features

### Proxy Chain Management

The `ProxyServer` class [api/src/utils/proxy.ts:15-69]() provides transparent proxy chaining with internal bypass:

**Key Features:**
- **Internal Bypass**: Automatically bypasses proxy for local hosts (0.0.0.0, localhost) [api/src/utils/proxy.ts:29-37]().
- **Bandwidth Tracking**: Tracks `txBytes` and `rxBytes` for the session [api/src/utils/proxy.ts:53-59]().
- **Upstream Rotation**: Built-in support for upstream proxy rotation [README.md:52-52]().

**Sources:** [api/src/utils/proxy.ts:15-69](), [README.md:52-52]()

### Request Interception & Filtering

Request interception [api/src/services/cdp/cdp.service.ts:385-439]() provides granular control over network traffic:

| Option | Resource Types | Implementation |
|--------|---------------|----------------|
| `blockAds` | Ad domains | `isAdRequest()` pattern matching [api/src/services/cdp/cdp.service.ts:393-397]() |
| `blockImages` | `image` | `isImageRequest()` matching [api/src/services/cdp/cdp.service.ts:401-404]() |
| `blockMedia` | `media` | `isHeavyMediaRequest()` matching [api/src/services/cdp/cdp.service.ts:408-411]() |
| `blockHosts` | Custom domains | `isHostBlocked()` check [api/src/services/cdp/cdp.service.ts:423-426]() |

**Sources:** [api/src/services/cdp/cdp.service.ts:385-439](), [api/src/utils/requests.ts]()

---

## Quick Actions API

Stateless, single-request operations for common browser tasks [README.md:57-57]().

### Scrape Endpoint

**Endpoint:** `POST /v1/scrape` [api/src/modules/actions/actions.routes.ts:7-23]()

**Output Formats (`ScrapeFormat`):** [api/src/modules/actions/actions.schema.ts:7]()
- `html`: Raw page HTML.
- `markdown`: Cleaned markdown conversion via `htmlToMarkdown`.
- `readability`: Extraction via `getDefuddleContent`.

### Screenshot & PDF

**Screenshot:** `POST /v1/screenshot` [api/src/modules/actions/actions.routes.ts:25-41]()
- Full-page or viewport capture [api/src/modules/actions/actions.schema.ts:69]().

**PDF:** `POST /v1/pdf` [api/src/modules/actions/actions.routes.ts:43-59]()
- Generates PDF content of a page.

**Sources:** [api/src/modules/actions/actions.controller.ts:25-243](), [api/src/modules/actions/actions.routes.ts](), [api/src/modules/actions/actions.schema.ts]()

---

## Extensibility & Plugin System

### Plugin Architecture

The `PluginManager` [api/src/services/cdp/plugins/core/plugin-manager.ts]() implements lifecycle hooks for custom extensions:

**Lifecycle Events:**
- `onBrowserLaunch(browser)` [api/src/services/cdp/plugins/core/plugin-manager.ts:96-105]()
- `onPageCreated(page)` [api/src/services/cdp/plugins/core/plugin-manager.ts:123-132]()
- `onPageNavigate(page)` [api/src/services/cdp/plugins/core/plugin-manager.ts:151-160]()
- `onShutdown(reason)` [api/src/services/cdp/plugins/core/plugin-manager.ts:193-202]()

**Sources:** [api/src/services/cdp/plugins/core/base-plugin.ts](), [api/src/services/cdp/plugins/core/plugin-manager.ts]()

### Chrome Extension Support

Custom Chrome extensions loaded via `--load-extension` argument [api/src/services/cdp/cdp.service.ts:709-741]().

**Extension Management**
```mermaid
graph TB
    subgraph "ExtensionSources"
        ["BuiltInExtensions"]
        ["CustomExtensions"]
        ["RecorderExtension"]
    end
    
    subgraph "Processing"
        ["getExtensionPaths()"]
        ["CDPService.launch()"]
    end
    
    subgraph "Runtime"
        ["ChromeInstance"]
    end
    
    ["BuiltInExtensions"] --> ["getExtensionPaths()"]
    ["CustomExtensions"] --> ["CDPService.launch()"]
    ["RecorderExtension"] --> ["CDPService.launch()"]
    ["getExtensionPaths()"] --> ["CDPService.launch()"]
    ["CDPService.launch()"] -->|"load-extension arg"| ["ChromeInstance"]
```

**Sources:** [api/src/services/cdp/cdp.service.ts:709-741](), [api/src/utils/extensions.ts]()

---

## Deployment & Operations

### Docker Support

Multi-stage build [Dockerfile:1-126]() with optimized layers:
- **api-build**: Compiles the API and recorder extension [Dockerfile:36-70]().
- **ui-build**: Builds the React dashboard [Dockerfile:23-34]().
- **production**: Final image containing Chromium, Node.js, and Nginx [Dockerfile:72-126]().

**Sources:** [Dockerfile:1-126](), [render.yaml:1-18](), [README.md:73-81]()

---

# Page: Monorepo Structure

# Monorepo Structure

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [api/package.json](api/package.json)
- [package-lock.json](package-lock.json)
- [package.json](package.json)
- [repl/README.md](repl/README.md)
- [repl/src/script.ts](repl/src/script.ts)

</details>



This document explains the workspace organization, package dependencies, build system, and how the three main packages (api, ui, repl) are structured and relate to each other within the Steel Browser monorepo. For deployment architecture and containerization, see page 2.3.

## Overview

Steel Browser uses npm workspaces to organize three distinct packages within a single repository at version `0.5.2`. The monorepo structure enables shared dependencies, coordinated builds, and consistent versioning across the Fastify-based API server (port 3000), React UI dashboard (port 5173), and development REPL.

**Sources:** [package.json:1-12](), [package-lock.json:1-15]()

## Workspace Organization

The monorepo defines three workspaces at the root level:

```mermaid
graph TB
    Root["steel-browser<br/>(root package)<br/>v0.5.2"]
    
    API["api<br/>@steel-browser/api<br/>v0.5.2"]
    UI["ui<br/>@steel-browser/ui"]
    REPL["repl<br/>@steel-browser/repl"]
    
    Root --> API
    Root --> UI
    Root --> REPL
    
    subgraph "Workspace Packages"
        API
        UI
        REPL
    end
    
    subgraph "Shared Root Dependencies"
        SharedDeps["- fastify@5.2.1<br/>- lodash-es@4.17.21<br/>- @joplin/turndown-plugin-gfm@1.0.62<br/>- husky@9.1.7"]
    end
    
    subgraph "Build Tools"
        BuildTools["- typescript@5.7.3<br/>- tsx@4.19.2<br/>- concurrently@8.2.0<br/>- @commitlint/cli@19.7.1"]
    end
    
    Root -.->|provides| SharedDeps
    Root -.->|provides| BuildTools
```

**Sources:** [package.json:1-12](), [package.json:30-36](), [api/package.json:2-3](), [package-lock.json:1-15]()

| Workspace | Package Name | Description | Type |
|-----------|-------------|-------------|------|
| `api` | `@steel-browser/api` | Core browser automation API server, CDPService, SessionService, and plugin system | Private |
| `ui` | `@steel-browser/ui` | React-based dashboard for session management and monitoring | Private |
| `repl` | `@steel-browser/repl` | Development REPL for testing Puppeteer scripts | Private |

**Sources:** [api/package.json:1-7](), [package.json:8-12]()

## API Package Structure

The API package (`@steel-browser/api`) is the most complex workspace, providing multiple export paths for different integration scenarios. It contains the core `CDPService`, `SessionService`, `FileService`, and plugin system.

**Workspace Structure Diagram**

```mermaid
graph TB
    subgraph "API Workspace Directory"
        SrcDir["src/<br/>(TypeScript source)"]
        BuildDir["build/<br/>(Compiled output)"]
        ExtensionsDir["extensions/recorder"]
        
        SrcDir --> Index["src/index.ts<br/>(Server entry point)"]
        SrcDir --> Services["src/services/<br/>cdp/, session/, file/"]
        SrcDir --> Routes["src/routes/"]
        SrcDir --> Plugins["src/plugins/logging/"]
        SrcDir --> Scripts["src/scripts/fingerprint.js"]
        SrcDir --> Templates["src/templates/"]
    end
    
    subgraph "Build Process"
        TSC["tsc<br/>(TypeScript compiler)"]
        CopyTemplates["copy:templates script"]
        CopyFingerprint["copy:fingerprint script"]
        
        SrcDir --> TSC
        TSC --> BuildDir
        Templates --> CopyTemplates
        CopyTemplates --> BuildTemplates["build/templates/"]
        Scripts --> CopyFingerprint
        CopyFingerprint --> BuildScripts["build/scripts/fingerprint.js"]
    end
    
    subgraph "Package Exports"
        MainExport["main: index.js"]
        PluginExport["./plugin"]
        CDPPluginExport["./cdp-plugin"]
        LoggerExport["./logger"]
        StorageExport["./storage"]
        BrowserExport["./browser"]
    end
```

**Sources:** [api/package.json:5-39](), [api/package.json:41-45]()

**API Package Export Paths**

```mermaid
graph LR
    subgraph "Package Exports Configuration"
        PluginPath["./plugin"]
        CDPPluginPath["./cdp-plugin"]
        LoggerPath["./logger"]
        StoragePath["./storage"]
        BrowserPath["./browser"]
    end
    
    subgraph "Build Output Files"
        PluginJS["build/steel-browser-plugin.js"]
        CDPPluginJS["build/services/cdp/plugins/core/base-plugin.js"]
        LoggerJS["build/plugins/logging/browser-logger.js"]
        StorageJS["build/services/cdp/instrumentation/storage/log-storage.interface.js"]
        BrowserJS["build/types/browser.js"]
    end
    
    subgraph "Consumer Use Cases"
        FastifyIntegration["Fastify Plugin Integration<br/>('@steel-browser/api/plugin')"]
        CustomCDPPlugins["Custom CDP Plugins<br/>('@steel-browser/api/cdp-plugin')"]
        CustomLogging["Custom Event Logging<br/>('@steel-browser/api/logger')"]
        CustomStorage["Custom Storage Backend<br/>('@steel-browser/api/storage')"]
        BrowserTypes["Browser Type Definitions<br/>('@steel-browser/api/browser')"]
    end
    
    PluginPath --> PluginJS
    PluginJS --> FastifyIntegration
    
    CDPPluginPath --> CDPPluginJS
    CDPPluginJS --> CustomCDPPlugins
    
    LoggerPath --> LoggerJS
    LoggerJS --> CustomLogging
    
    StoragePath --> StorageJS
    StorageJS --> CustomStorage

    BrowserPath --> BrowserJS
    BrowserJS --> BrowserTypes
```

**Sources:** [api/package.json:8-39]()

### Export Paths

The API package defines five distinct export paths for consumers:

| Export Path | Type Definition | JavaScript Module | Purpose |
|-------------|----------------|-------------------|---------|
| `./plugin` | `build/steel-browser-plugin.d.ts` | `build/steel-browser-plugin.js` | Main Fastify plugin for integrating Steel into existing applications |
| `./cdp-plugin` | `build/services/cdp/plugins/core/base-plugin.d.ts` | `build/services/cdp/plugins/core/base-plugin.js` | Base class for creating browser lifecycle plugins |
| `./logger` | `build/plugins/logging/browser-logger.d.ts` | `build/plugins/logging/browser-logger.js` | Browser event logging infrastructure |
| `./storage` | `build/services/cdp/instrumentation/storage/log-storage.interface.d.ts` | `build/services/cdp/instrumentation/storage/log-storage.interface.js` | Log storage interface for custom backends |
| `./browser` | `build/types/browser.d.ts` | `build/types/browser.js` | Core browser type definitions |

**Sources:** [api/package.json:8-39]()

## Dependency Architecture

**Dependency Distribution Across Workspaces**

```mermaid
graph TB
    subgraph "Root Level Dependencies"
        RootProd["Production:<br/>fastify@5.2.1<br/>lodash-es@4.17.21<br/>@joplin/turndown-plugin-gfm@1.0.62"]
        RootDev["Development:<br/>typescript@5.7.3<br/>tsx@4.19.2<br/>concurrently@8.2.0"]
    end
    
    subgraph "API Dependencies"
        APIProd["Core Browser Control:<br/>puppeteer-core@23.6.0<br/>zod@3.24.2<br/>fingerprint-generator@2.1.72"]
        APIFastify["Fastify Ecosystem:<br/>@fastify/cors@10.0.2<br/>@fastify/multipart@9.0.3<br/>@fastify/swagger@9.4.2"]
        APIStorage["Storage & Logs:<br/>duckdb-async@1.1.3<br/>level@9.0.0<br/>archiver@7.0.1"]
        APIPeer["Peer Dependencies:<br/>fastify@^5.0.0 (required)<br/>@opentelemetry/api@1.9.0 (optional)"]
    end
    
    subgraph "REPL Dependencies"
        REPLDeps["Puppeteer Connection:<br/>puppeteer-core"]
    end
    
    RootProd -.->|shared| APIProd
    RootDev -.->|shared| APIProd
    
    Note1["Note: API uses puppeteer-core@23.6.0<br/>for stable automation"]
```

**Sources:** [package.json:30-36](), [api/package.json:72-113](), [repl/src/script.ts:1]()

### API Package Peer Dependencies

The API package uses peer dependencies to avoid version conflicts when integrated into other applications:

```json
{
  "peerDependencies": {
    "@opentelemetry/api": "1.9.0",
    "fastify": "^5.0.0"
  },
  "peerDependenciesMeta": {
    "fastify": {
      "optional": false
    },
    "@opentelemetry/api": {
      "optional": true
    }
  }
}
```

**Sources:** [api/package.json:118-129]()

## Build System

**Root and Workspace Build Flow**

```mermaid
graph TB
    subgraph "Root Package Scripts"
        RootBuild["npm run build<br/>(package.json:14)"]
        RootDev["npm run dev<br/>(package.json:15)"]
    end
    
    subgraph "API Build Process"
        APIBuild["npm run build -w api"]
        TSC_API["tsc"]
        CopyTemplates["npm run copy:templates"]
        CopyFingerprint["npm run copy:fingerprint"]
        PrepareRecorder["npm run prepare:recorder"]
        
        APIBuild --> TSC_API
        TSC_API --> CopyTemplates
        CopyTemplates --> CopyFingerprint
        APIBuild --> PrepareRecorder
    end
    
    subgraph "Development Mode (Concurrent)"
        RootDevConcurrent["concurrently<br/>(package.json:15)"]
        APIDevWatch["tsx watch src/index.ts<br/>(api/package.json:47)"]
        UIDev["npm run dev -w ui"]
        
        RootDev --> RootDevConcurrent
        RootDevConcurrent --> APIDevWatch
        RootDevConcurrent --> UIDev
    end
```

**Sources:** [package.json:13-17](), [api/package.json:40-51]()

### Build Scripts

#### API Workspace Scripts

| Command | Script | Output/Action |
|---------|--------|---------------|
| `npm run start` | `node ./build/index.js` | Run compiled API server |
| `npm run build` | `tsc && npm run copy:templates && npm run copy:fingerprint` | Production build |
| `npm run dev` | `npm run prepare:recorder && tsx watch src/index.ts` | Dev mode with hot reload |
| `npm run copy:templates` | `mkdir -p build/templates && cp -r src/templates/* build/templates/` | Copy EJS templates |
| `npm run copy:fingerprint` | `cp src/scripts/fingerprint.js build/scripts/fingerprint.js` | Copy fingerprint script |
| `npm run prepare:recorder` | `cd extensions/recorder && npm install && npm run build` | Build recorder extension |

**Sources:** [api/package.json:40-51]()

## REPL Integration

The REPL workspace provides a standalone script to interact with the API's managed browser instances via the Chrome DevTools Protocol (CDP).

```mermaid
graph LR
    subgraph "REPL Environment"
        REPLScript["repl/src/script.ts"]
        Puppeteer["puppeteer.connect()"]
    end
    
    subgraph "API Environment"
        CDPServer["CDP WebSocket Server<br/>ws://0.0.0.0:3000"]
        Browser["Managed Chromium Instance"]
    end
    
    REPLScript --> Puppeteer
    Puppeteer -->|WebSocket| CDPServer
    CDPServer --> Browser
```

**Sources:** [repl/src/script.ts:1-23](), [repl/README.md:1-15]()

### REPL Script Logic
The REPL connects to the API's WebSocket endpoint using `puppeteer.connect` ([repl/src/script.ts:6]()). It navigates to a target URL, performs actions, and performs cleanup by closing pages and disconnecting ([repl/src/script.ts:12-18]()).

## Dependency Overrides

The monorepo enforces specific versions of transitive dependencies to ensure security and compatibility.

```json
{
  "overrides": {
    "tar-fs": ">=3.1.1",
    "cross-spawn": "^7.0.6"
  }
}
```

- `tar-fs`: Overridden to `>=3.1.1` across the monorepo to address security vulnerabilities.
- `cross-spawn`: Overridden to `^7.0.6` in the API workspace.

**Sources:** [package.json:37-39](), [api/package.json:114-117]()

---

# Page: Getting Started

# Getting Started

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Dockerfile](Dockerfile)
- [README.md](README.md)
- [api/Dockerfile](api/Dockerfile)
- [api/entrypoint.sh](api/entrypoint.sh)
- [docker-compose.dev.yml](docker-compose.dev.yml)
- [docker-compose.yml](docker-compose.yml)
- [images/star_img.png](images/star_img.png)
- [render.yaml](render.yaml)
- [ui/Dockerfile](ui/Dockerfile)

</details>



This document guides you through the initial setup and deployment of Steel Browser. It covers the available installation methods, basic configuration, and how to verify your installation is working correctly. 

For detailed environment configuration options, see [Environment Configuration](#2.2). For production deployment details, see [Docker Deployment](#2.3). For advanced deployment and operations topics, see [Deployment & Operations](#13).

## Installation Overview

Steel Browser supports multiple deployment methods depending on your requirements:

| Method | Best For | Complexity | Prerequisites |
|--------|----------|------------|---------------|
| **Pre-built Docker Image** | Quick testing, production | Low | Docker |
| **Docker Compose** | Development, self-hosted | Low | Docker Compose |
| **Local Node.js** | Development, debugging | Medium | Node.js 22+, Chrome/Chromium |
| **Cloud Platforms** | Production hosting | Low | Railway/Render account |
| **Steel Cloud** | Managed service | Very Low | Steel account |

The system exposes three network interfaces once deployed:

```mermaid
graph LR
    subgraph "Network Interfaces"
        RestAPI["REST API<br/>Port 3000<br/>routes: /v1/*"]
        CDP["Chrome DevTools Protocol<br/>Port 9223<br/>env: CDP_REDIRECT_PORT"]
        WebUI["React UI<br/>Port 5173 or /ui<br/>env: VITE_API_URL"]
    end
    
    subgraph "Backend Services"
        FastifyServer["Fastify Server<br/>api/src/index.ts"]
        ChromeBrowser["Chromium Browser<br/>env: CHROME_EXECUTABLE_PATH"]
        StaticFiles["Static UI Files<br/>ui/dist"]
    end
    
    RestAPI --> FastifyServer
    CDP --> ChromeBrowser
    WebUI --> StaticFiles
    
    FastifyServer --> ChromeBrowser
    StaticFiles -.->|"API calls"| RestAPI
```

**Interface Details:**
- **REST API**: Fastify server with route handlers defined in `api/src/routes.ts`.
- **CDP Port**: Configured via `CDP_REDIRECT_PORT` environment variable, defaulting to 9223 [api/entrypoint.sh:109]().
- **UI Path**: Vite build output served at `/ui` (combined mode) or port 5173 (separate).

Sources: [README.md:70-155](), [api/entrypoint.sh:109](), [Dockerfile:33]()

## Installation Methods

### Pre-built Docker Image

The fastest deployment method uses the pre-built image from GitHub Container Registry:

```bash
docker run -p 3000:3000 -p 9223:9223 ghcr.io/steel-dev/steel-browser
```

This command pulls a combined container that includes the API, the UI, and the browser binaries.

| Component | Location | Description |
|-----------|----------|-------------|
| Fastify API | `node api/build/index.js` | Compiled TypeScript entrypoint [api/entrypoint.sh:124]() |
| Static UI | `/app/ui/dist` | React build artifacts [Dockerfile:115]() |
| Chromium | `/usr/bin/chromium` | Browser binary [Dockerfile:103]() |
| ChromeDriver | `/usr/bin/chromedriver` | Selenium WebDriver binary [Dockerfile:103]() |

**Default Environment:**
- `NODE_ENV=production` [Dockerfile:7]()
- `CDP_REDIRECT_PORT=9223` [api/entrypoint.sh:109]()
- `DISPLAY=:10` [Dockerfile:9]() (Xvfb virtual display)
- `PUPPETEER_CACHE_DIR=/app/.cache` [Dockerfile:8]()

Sources: [README.md:86-94](), [Dockerfile:1-126](), [api/entrypoint.sh:108-124]()

### Docker Compose (Separate Services)

For more control, run API and UI as separate services:

```bash
docker compose up
```

For Mac Silicon users:
```bash
DOCKER_DEFAULT_PLATFORM=linux/arm64 docker compose up
```

This starts the services as defined in `docker-compose.yml`:
- **API service**: Port 3000 [docker-compose.yml:5]()
- **UI service**: Port 5173 [docker-compose.yml:22]()
- **Volumes**: Persistent `logs` for DuckDB and `exports` for file management [docker-compose.yml:35-40]()

```mermaid
graph TB
    subgraph "Host Machine"
        Port3000["Port 3000<br/>(API)"]
        Port9223["Port 9223<br/>(CDP)"]
        Port5173["Port 5173<br/>(UI)"]
        CacheDir[".cache directory<br/>(bind mount)"]
    end
    
    subgraph "Docker Network: steel-network"
        subgraph "API Container"
            NodeAPI["Node.js Server<br/>node ./api/build/index.js"]
            Chrome["Chromium Browser<br/>/usr/bin/chromium"]
            Xvfb["Xvfb :10<br/>(virtual display)"]
            CacheMountAPI["/app/.cache<br/>PUPPETEER_CACHE_DIR"]
            LogsMount["/data/logs<br/>DuckDB storage"]
        end
        
        subgraph "UI Container"
            NginxUI["nginx:alpine<br/>Static serving"]
        end
        
        subgraph "Docker Volumes"
            LogsVol["logs volume"]
            ExportsVol["exports volume"]
        end
    end
    
    Port3000 --> NodeAPI
    Port9223 --> Chrome
    Port5173 --> NginxUI
    
    CacheDir -.->|bind mount| CacheMountAPI
    LogsVol --> LogsMount
    ExportsVol --> NodeAPI
    
    NodeAPI -.->|internal DNS| NginxUI
    NodeAPI --> Chrome
    NodeAPI --> Xvfb
```

Sources: [docker-compose.yml:1-40](), [api/Dockerfile:1-110](), [ui/Dockerfile:1-30]()

### Local Node.js Development

For direct Node.js execution:

```bash
npm install
npm run dev
```

This starts the API server and the UI dev server via the root workspace [README.md:128-130]().

**Chrome Resolution:**
The system searches for Chrome in standard paths (e.g., `/usr/bin/google-chrome` on Linux or `/Applications/Google Chrome.app/...` on macOS) [README.md:136-145](). You can override this by setting `CHROME_EXECUTABLE_PATH` [README.md:151]().

Sources: [README.md:123-154]()

### Cloud Platform Deployment

#### Railway & Render
Steel provides 1-click deployment buttons and configuration files for cloud providers.
- **Railway**: Uses the combined `Dockerfile` [README.md:79]().
- **Render**: Configured via `render.yaml`, which specifies a 1GB persistent disk for caching [render.yaml:14-17]().

Sources: [README.md:76-80](), [render.yaml:1-18]()

## Verifying Installation

### 1. Check API Health
```bash
curl http://localhost:3000/v1/health
```
This endpoint is used by Render for health checks [render.yaml:6]().

### 2. Access OpenAPI Documentation
Navigate to `http://localhost:3000/documentation` to access the interactive Swagger/Scalar UI [README.md:60]().

### 3. Test Session Creation
```bash
curl -X POST http://localhost:3000/v1/sessions \
  -H "Content-Type: application/json" \
  -d '{"blockAds": true}'
```

## Container Build Process

The Docker image uses a multi-stage build [Dockerfile:1-126]() to produce a lean production image.

```mermaid
graph TB
    subgraph "Stage: ui-build"
        UIBuild["npm run build -w ui"]
    end
    
    subgraph "Stage: api-build"
        APITSBuild["npm run build -w api"]
        APIRecorder["Build recorder extension"]
        APIPrune["npm prune --omit=dev"]
    end
    
    subgraph "Stage: production"
        ProdDeps["Install nginx, chromium, xvfb"]
        ProdCopyAPI["COPY --from=api-build"]
        ProdCopyUI["COPY --from=ui-build"]
        ProdEntry["ENTRYPOINT entrypoint.sh"]
    end
    
    UIBuild --> ProdCopyUI
    APITSBuild --> APIRecorder
    APIRecorder --> APIPrune
    APIPrune --> ProdCopyAPI
    ProdDeps --> ProdCopyAPI
    ProdCopyAPI --> ProdCopyUI
    ProdCopyUI --> ProdEntry
```

Sources: [Dockerfile:1-126](), [api/Dockerfile:1-110]()

## Container Initialization

The `entrypoint.sh` script orchestrates the startup of system dependencies before launching the Node.js application.

1. **DBus**: Initialized to support Chrome IPC [api/entrypoint.sh:12-31]().
2. **Chrome Verification**: Checks for `chromium` and `chromedriver` [api/entrypoint.sh:34-63]().
3. **Nginx**: Starts the reverse proxy unless `--no-nginx` is passed [api/entrypoint.sh:66-89]().
4. **Execution**: Replaces the shell with the Node.js process using `exec` to ensure proper signal handling [api/entrypoint.sh:124]().

Sources: [api/entrypoint.sh:1-127]()

## Next Steps

- **Configure Environment**: See [Environment Configuration](#2.2) for variable references.
- **Docker Deployment**: See [Docker Deployment](#2.3) for advanced container orchestration.
- **Usage**: Check the [Steel Cookbook](https://github.com/steel-dev/steel-cookbook) for API examples.

---

# Page: Installation

# Installation

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Dockerfile](Dockerfile)
- [README.md](README.md)
- [api/Dockerfile](api/Dockerfile)
- [api/entrypoint.sh](api/entrypoint.sh)
- [docker-compose.dev.yml](docker-compose.dev.yml)
- [docker-compose.yml](docker-compose.yml)
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- [docs/DEVELOPMENT_SETUP.md](docs/DEVELOPMENT_SETUP.md)
- [docs/README.md](docs/README.md)
- [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)
- [images/star_img.png](images/star_img.png)
- [render.yaml](render.yaml)
- [ui/Dockerfile](ui/Dockerfile)

</details>



This page covers all methods for installing and deploying Steel Browser. It includes Docker-based deployments, local development setup, and cloud hosting options. For detailed environment configuration after installation, see [Environment Configuration](#2.2). For understanding the container architecture, see [Docker Deployment](#2.3).

## Overview

Steel Browser can be installed through multiple methods depending on your use case:

| Installation Method | Use Case | Complexity | Reference |
|-------------------|----------|------------|-----------|
| Pre-built Docker Image | Quick start, production | Low | [README.md:86-96]() |
| Docker Compose | Separated API/UI services | Low | [README.md:97-106]() |
| Local Node.js | Development, custom Chrome | Medium | [README.md:123-154]() |
| Railway | 1-click cloud deployment | Low | [README.md:79]() |
| Render | Cloud deployment | Medium | [render.yaml:1-14]() |
| Steel Cloud | Managed service | Low | [README.md:71]() |

The installation architecture follows a multi-stage build pattern where dependencies are compiled separately from runtime requirements, minimizing the final image size.

```mermaid
graph TB
    subgraph "InstallationMethods"
        [PreBuilt] -- "ghcr.io/steel-dev/steel-browser" --> [CombinedImg]
        [Compose] -- "API + UI containers" --> [APIImg]
        [Compose] --> [UIImg]
        [Local] -. "npm run dev" .-> [NodeAPI]
        [Cloud] --> [CombinedImg]
    end
    
    subgraph "ImageSources"
        [CombinedImg] -- "Dockerfile" --> [Entrypoint]
        [APIImg] -- "api/Dockerfile" --> [Entrypoint]
        [UIImg] -- "ui/Dockerfile" --> [UIServe]
    end
    
    subgraph "RuntimeComponents"
        [NodeAPI] -- "Port 3000" --> [Chrome]
        [Chrome] -- "Port 9223" --> [CDP]
        [UIServe] -- "Port 5173/80" --> [Browser]
        [Entrypoint] -- "Initialization" --> [NodeAPI]
        [Entrypoint] --> [Chrome]
    end
    
    [CombinedImg] --> [UIServe]
```

**Diagram: Installation Method Flow**

The diagram maps each installation method to the specific Docker build files and runtime components. `Dockerfile` builds a combined image, while `api/Dockerfile` and `ui/Dockerfile` build separate services for Docker Compose deployments.

Sources: [README.md:70-154](), [Dockerfile:1-126](), [api/Dockerfile:1-110](), [ui/Dockerfile:1-30]()

## Pre-built Docker Image

The simplest installation method uses the pre-built image from GitHub Container Registry. This image combines both the API server and UI dashboard in a single container.

### Basic Deployment

```bash
docker run -p 3000:3000 -p 9223:9223 ghcr.io/steel-dev/steel-browser
```

This command:
- Exposes port `3000` for the API and UI (`http://localhost:3000`) [Dockerfile:120]()
- Exposes port `9223` for Chrome DevTools Protocol [Dockerfile:120]()
- Uses default configuration from [api/Dockerfile:104-106]()

### With Persistent Cache

```bash
docker run -p 3000:3000 -p 9223:9223 \
  -v $(pwd)/.cache:/app/.cache \
  ghcr.io/steel-dev/steel-browser
```

The `-v $(pwd)/.cache:/app/.cache` bind mount persists Puppeteer's browser binaries between container restarts. The cache directory is defined by `PUPPETEER_CACHE_DIR` at [api/Dockerfile:8]() and [Dockerfile:8]().

### Image Build Process

```mermaid
graph LR
    subgraph "Multi-StageBuild"
        [UIBuildStage] -- "Dockerfile:23-33" --> [UIAssets]
        [APIBuildStage] -- "Dockerfile:36-69" --> [APIBuilt]
        [APIBuildStage] --> [RecorderExt]
        [ProdStage] -- "Dockerfile:72-126" --> [Runtime]
    end
    
    subgraph "BuildArtifacts"
        [UIAssets] -- "/app/ui/dist" --> [ProdStage]
        [APIBuilt] -- "/app/api/build" --> [ProdStage]
        [RecorderExt] -- "extensions/recorder/dist" --> [ProdStage]
    end
    
    subgraph "ProductionRuntime"
        [Runtime] --> [ChromiumPkg]
        [Runtime] --> [ChromeDriverPkg]
        [Runtime] --> [NginxPkg]
        [Runtime] --> [XvfbPkg]
    end
```

**Diagram: Combined Docker Image Build Pipeline**

The build uses three stages defined in [Dockerfile:23-126](). Stage 1 (`ui-build`) compiles the React UI at [Dockerfile:23-33]() with `--base=/ui` to serve from the `/ui` path. Stage 2 (`api-build`) compiles the API and recorder extension at [Dockerfile:36-69](). Stage 3 (`production`) installs runtime dependencies and copies artifacts from both build stages.

Sources: [Dockerfile:1-126](), [api/entrypoint.sh:1-127]()

## Docker Compose Deployment

Docker Compose deploys separate containers for the API and UI services, allowing independent scaling and configuration.

### Production Deployment

```bash
docker compose up
```

This uses [docker-compose.yml:1-40]() which defines:
- `api` service: Built from `ghcr.io/steel-dev/steel-browser-api:latest` [docker-compose.yml:3]()
- `ui` service: Built from `ghcr.io/steel-dev/steel-browser-ui:latest` [docker-compose.yml:20]()
- `steel-network`: Bridge network for inter-container communication [docker-compose.yml:31-33]()
- Named volumes: `logs` and `exports` for persistent storage [docker-compose.yml:35-39]()

### Development Deployment

```bash
docker compose -f docker-compose.dev.yml up --build
```

This uses [docker-compose.dev.yml:1-35]() which builds images from source directories instead of pulling pre-built images. The `--build` flag ensures images are rebuilt when source code changes [README.md:118-120]().

### Service Architecture

```mermaid
graph TB
    subgraph "DockerComposeConfig"
        [APIService] -- "api/Dockerfile" --> [Network]
        [UIService] -- "ui/Dockerfile" --> [Network]
        [Network] -- "bridge" --> [SteelNetwork]
    end
    
    subgraph "VolumeMounts"
        [APIService] -- "/data/logs" --> [LogsVol]
        [APIService] -- "/tmp/steel-browser-exports" --> [ExportsVol]
        [APIService] -- "/app/.cache" --> [CacheBind]
    end
    
    subgraph "EnvironmentConfig"
        [APIService] -- "DOMAIN" --> [Localhost3000]
        [APIService] -- "LOG_STORAGE_PATH" --> [DuckDB]
        [UIService] -- "API_URL" --> [APIService]
    end
```

**Diagram: Docker Compose Service Configuration**

The `api` service configuration at [docker-compose.yml:2-17]() defines three mount strategies: named volumes for logs and exports, and bind mount for cache. The `ui` service at [docker-compose.yml:19-28]() connects to the API using the internal DNS name `api:3000` via the `steel-network` bridge [docker-compose.yml:24]().

### Mac Silicon Compatibility

```bash
DOCKER_DEFAULT_PLATFORM=linux/arm64 docker compose up
```

Mac M1/M2 users must set the platform as noted in [README.md:103-106]() because the pre-built images target `linux/amd64` by default.

Sources: [docker-compose.yml:1-40](), [docker-compose.dev.yml:1-35](), [README.md:97-122]()

## Local Development Setup

Local installation requires Node.js and Chrome/Chromium. This method provides faster iteration during development without Docker overhead.

### Prerequisites

The system requires:
- Node.js version specified at [api/Dockerfile:1]() and [Dockerfile:1]() (22.13.0)
- Chrome/Chromium executable at platform-specific paths [README.md:135-143]()
- Minimum 1GB disk space for browser binaries

### Installation Steps

```bash
# Install all workspace dependencies
npm install

# Start development environment
npm run dev
```

The `npm run dev` command defined in the root `package.json` starts the API server on port `3000` and the UI development server on port `5173` [README.md:129-132]().

### Chrome Executable Detection

The Chrome detection logic is implemented in `api/src/utils/browser.ts` and checks paths in order of precedence: environment variable, then platform-specific defaults documented at [README.md:135-143]().

| Platform | Default Path |
|----------|--------------|
| **Linux** | `/usr/bin/google-chrome` |
| **MacOS** | `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome` |
| **Windows** | `C:\Program Files\Google\Chrome\Application\chrome.exe` |

### Custom Chrome Path

```bash
export CHROME_EXECUTABLE_PATH=/path/to/chrome
npm run dev
```

Override detection by setting `CHROME_EXECUTABLE_PATH` as mentioned in [README.md:148-152](). This is useful for Chromium installations, custom builds, or non-standard paths.

Sources: [README.md:123-154](), [api/src/utils/browser.ts:1-155]()

## Cloud Deployments

### Railway Deployment

Railway provides 1-click deployment via their template system referenced at [README.md:79](). It uses the combined Docker image from [Dockerfile:1-126]().

### Render Deployment

Render deployment is configured via [render.yaml:1-14]():

```yaml
services:
  - type: web
    runtime: docker
    name: steel-browser
    dockerfilePath: ./Dockerfile
    healthCheckPath: /v1/health
    envVars:
      - key: NODE_ENV
        value: production
    disk:
      name: cache
      mountPath: /app/.cache
      sizeGB: 1
```

The configuration:
- Uses `Dockerfile` at [render.yaml:5]() for the container build.
- Defines health check endpoint at [render.yaml:6]().
- Mounts a 1GB persistent disk for cache at [render.yaml:14-17]().

### Steel Cloud

Steel Cloud (https://app.steel.dev) is the managed hosting option referenced at [README.md:71](). This provides fully managed infrastructure without deployment configuration.

Sources: [README.md:71-79](), [render.yaml:1-14]()

## Container Initialization

All Docker-based installations use the entrypoint script for initialization.

```mermaid
graph TB
    [Start] -- "ENTRYPOINT" --> [ParseArgs]
    [ParseArgs] -- "entrypoint.sh:93-100" --> [CheckDebug]
    
    [CheckDebug] -- "DEBUG=true" --> [InitDBus]
    [InitDBus] -- "entrypoint.sh:12-31" --> [VerifyChrome]
    [VerifyChrome] -- "entrypoint.sh:33-63" --> [CheckNginx]
    
    [CheckNginx] -- "START_NGINX=true" --> [StartNginx]
    [StartNginx] -- "entrypoint.sh:66-89" --> [SetEnv]
    
    [SetEnv] -- "CDP_REDIRECT_PORT=9223" --> [LaunchNode]
    [LaunchNode] -- "exec node ./api/build/index.js" --> [SteelAPI]
```

**Diagram: Entrypoint Initialization Sequence**

The entrypoint script at [api/entrypoint.sh:92-127]() performs initialization in sequence:

1. **Argument Parsing**: Checks for `--no-nginx` flag [api/entrypoint.sh:93-100]().
2. **Debug Mode**: If `DEBUG=true`, initializes DBus and verifies Chrome [api/entrypoint.sh:102-105]().
3. **DBus Initialization**: Starts system DBus daemon [api/entrypoint.sh:12-31]().
4. **Chrome Verification**: Validates Chromium and ChromeDriver binaries [api/entrypoint.sh:33-63]().
5. **Nginx Startup**: Starts nginx if not disabled [api/entrypoint.sh:66-89]().
6. **Environment Setup**: Sets `CDP_REDIRECT_PORT=9223` and `DISPLAY=:10` [api/entrypoint.sh:109-110]().
7. **Node Launch**: Executes Node.js directly (not via npm) to preserve signal handling [api/entrypoint.sh:124]().

Sources: [api/entrypoint.sh:1-127](), [api/Dockerfile:100-110](), [Dockerfile:118-126]()

## Post-Installation Verification

### Health Check
```bash
curl http://localhost:3000/v1/health
```
The health check endpoint is used by Render for deployment validation [render.yaml:6]().

### API Documentation
Access the Swagger UI at `http://localhost:3000/documentation` [README.md:60]().

### CDP Debugger
Connect Chrome DevTools to `http://localhost:9223`. The CDP port is exposed at [docker-compose.yml:6]() and configured via `CDP_REDIRECT_PORT` at [api/entrypoint.sh:109]().

Sources: [README.md:60](), [README.md:93](), [README.md:167](), [docker-compose.yml:5-6]()

---

# Page: Environment Configuration

# Environment Configuration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.env.example](.env.example)
- [api/.env.example](api/.env.example)
- [api/Dockerfile](api/Dockerfile)
- [api/entrypoint.sh](api/entrypoint.sh)
- [api/src/env.ts](api/src/env.ts)
- [api/src/plugins/schemas.ts](api/src/plugins/schemas.ts)
- [api/src/routes.ts](api/src/routes.ts)
- [docker-compose.dev.yml](docker-compose.dev.yml)
- [docker-compose.yml](docker-compose.yml)
- [ui/.env.local.example](ui/.env.local.example)
- [ui/Dockerfile](ui/Dockerfile)
- [ui/entrypoint.sh](ui/entrypoint.sh)
- [ui/nginx.conf.template](ui/nginx.conf.template)

</details>



## Purpose and Scope

This document provides a comprehensive reference for configuring the steel-browser system through environment variables. The configuration system controls all aspects of the application including server settings, browser behavior, logging, proxy support, and security features. All configuration is validated at startup using Zod schemas to ensure type safety and catch errors early.

For information about deploying the system with Docker, see [Docker Deployment](#2.3). For browser session-specific configuration options, see [Session Configuration](#4.2).

---

## Configuration System Overview

The steel-browser configuration system uses environment variables as the primary configuration mechanism, with validation performed by Zod schemas at application startup. This ensures that invalid configurations are caught immediately rather than causing runtime errors.

### Configuration Flow

```mermaid
graph TB
    subgraph "Configuration Sources"
        EnvVars["process.env<br/>System Environment Variables"]
        DotEnv[".env files<br/>api/.env.example"]
        DockerEnv["Docker Environment<br/>docker-compose.yml"]
        EntryPoint["entrypoint.sh<br/>Runtime overrides"]
    end
    
    subgraph "Validation Layer"
        DotEnvLoader["dotenv.config()<br/>Load .env files"]
        ZodSchema["envSchema<br/>z.object() definition"]
        Parser["envSchema.parse()<br/>Validate & transform"]
    end
    
    subgraph "Configuration Object"
        EnvObject["env object<br/>Type-safe configuration"]
    end
    
    subgraph "Consumers"
        FastifySetup["Fastify Server<br/>Host, Port, SSL"]
        CDPService["CDPService<br/>Browser launch options"]
        SessionService["SessionService<br/>Session defaults"]
        LogStorage["BrowserLogger<br/>DuckDB configuration"]
        ProxyFactory["ProxyServer<br/>Proxy settings"]
    end
    
    EnvVars --> DotEnvLoader
    DotEnv --> DotEnvLoader
    DockerEnv --> EnvVars
    EntryPoint --> EnvVars
    
    DotEnvLoader --> ZodSchema
    ZodSchema --> Parser
    Parser --> EnvObject
    
    EnvObject --> FastifySetup
    EnvObject --> CDPService
    EnvObject --> SessionService
    EnvObject --> LogStorage
    EnvObject --> ProxyFactory
```

**Sources:** [api/src/env.ts:1-86](), [api/entrypoint.sh:92-127]()

---

## Configuration Sources

The configuration system reads from multiple sources in order of precedence:

### 1. System Environment Variables

Environment variables set in the shell or container environment take highest precedence:

```bash
export NODE_ENV=production
export CHROME_HEADLESS=true
npm start
```

### 2. .env Files

The application loads environment variables from `.env` files using the `dotenv` package. An example configuration is provided in [api/.env.example:1-31]():

```bash
NODE_ENV=development
HOST=0.0.0.0
PORT=3000
CHROME_HEADLESS=true
```

### 3. Docker Environment

Docker containers set environment variables through `docker-compose.yml` or directly in the Dockerfile:

```yaml
environment:
  - DOMAIN=localhost:3000
  - CDP_DOMAIN=localhost:9223
  - LOG_STORAGE_ENABLED=true
```

### 4. Runtime Overrides

The `entrypoint.sh` script sets critical runtime variables that override other sources:

```bash
export CDP_REDIRECT_PORT=9223
export DISPLAY=:10
```

**Sources:** [api/src/env.ts:1-4](), [api/.env.example:1-31](), [docker-compose.yml:11-15](), [api/entrypoint.sh:108-116]()

---

## Configuration Validation

All environment variables are validated using Zod schemas defined in [api/src/env.ts:6-84](). The validation system:

1. **Parses** raw string environment variables into typed values
2. **Transforms** string values (e.g., `"true"` → `true`)
3. **Validates** against schema constraints
4. **Provides defaults** for optional values
5. **Throws errors** for invalid configurations at startup

### Validation Architecture

```mermaid
graph LR
    subgraph "Schema Definition"
        EnvSchema["envSchema<br/>z.object()"]
        NodeEnv["NODE_ENV<br/>z.enum()"]
        ChromeHeadless["CHROME_HEADLESS<br/>z.string().transform()"]
        DefaultHeaders["DEFAULT_HEADERS<br/>z.string().transform(JSON.parse)"]
    end
    
    subgraph "Validation Process"
        ProcessEnv["process.env<br/>Raw strings"]
        Parse["envSchema.parse()<br/>Validate & transform"]
        Result["env object<br/>Typed values"]
    end
    
    subgraph "Error Handling"
        ValidationError["ZodError<br/>Invalid configuration"]
        Startup["Application startup fails<br/>Error message displayed"]
    end
    
    EnvSchema --> NodeEnv
    EnvSchema --> ChromeHeadless
    EnvSchema --> DefaultHeaders
    
    ProcessEnv --> Parse
    EnvSchema --> Parse
    Parse --> Result
    Parse -.->|validation fails| ValidationError
    ValidationError --> Startup
```

**Sources:** [api/src/env.ts:6-86]()

### Type Transformations

The validation system transforms string environment variables into appropriate types:

| Transformation Type | Example | Implementation |
|---|---|---|
| Boolean | `"true"` → `true` | `transform((val) => val === "true" \|\| val === "1")` |
| Enum | `"development"` → valid enum | `z.enum(["test", "development", "staging", "production", "preview"])` |
| JSON | `'{"key":"value"}'` → object | `transform((val) => val ? JSON.parse(val) : {})` |
| Array | `"--arg1 --arg2"` → `["--arg1", "--arg2"]` | `transform((val) => val.split(" ").map(arg => arg.trim()))` |
| Number | `"3000"` → (kept as string) | String type for PORT for flexibility |

**Sources:** [api/src/env.ts:7-83]()

---

## Configuration Categories

### Server Configuration

Controls the server behavior and network settings.

| Variable | Type | Default | Description |
|---|---|---|---|
| `NODE_ENV` | enum | `"development"` | Environment mode: `test`, `development`, `staging`, `production`, `preview` |
| `HOST` | string | `"0.0.0.0"` | Server bind address. Use `0.0.0.0` to accept external connections |
| `DOMAIN` | string | undefined | Full domain name for the server (e.g., `example.com`). Overrides HOST:PORT |
| `PORT` | string | `"3000"` | Server port number |
| `USE_SSL` | boolean | `false` | Enable HTTPS/WSS instead of HTTP/WS |

**Sources:** [api/src/env.ts:7-17]()

---

### Chrome Browser Configuration

Controls Chrome/Chromium browser launch behavior and runtime settings.

| Variable | Type | Default | Description |
|---|---|---|---|
| `CHROME_EXECUTABLE_PATH` | string | undefined | Path to Chrome/Chromium binary. Auto-detected if not set |
| `CHROME_HEADLESS` | boolean | `true` | Run Chrome in headless mode |
| `DISPLAY` | string | `":10"` | X11 display server for headless rendering (used with Xvfb) |
| `CHROME_ARGS` | string[] | `[]` | Additional Chrome launch arguments (space-separated) |
| `FILTER_CHROME_ARGS` | string[] | `[]` | Chrome arguments to filter out from default args |
| `DEBUG_CHROME_PROCESS` | boolean | `false` | Enable Chrome process debugging output |
| `CHROME_USER_DATA_DIR` | string | undefined | Chrome user data directory for profile persistence |
| `DISABLE_CHROME_SANDBOX` | boolean | `false` | Disable Chrome sandbox (useful in some Docker environments) |

**Docker Configuration:**

The Dockerfile sets Chrome-related environment variables:

```dockerfile
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROME_PATH=/usr/bin/chromium
ENV DISPLAY=:10
```

**Runtime Setup:**

The entrypoint script verifies Chrome installation and sets the display:

```bash
export DISPLAY=:10
verify_chrome() {
    if [ ! -f "/usr/bin/chromium" ] && [ -z "$CHROME_EXECUTABLE_PATH" ]; then
        log "ERROR: Chrome binary not found"
        return 1
    fi
}
```

**Sources:** [api/src/env.ts:27-83](), [api/Dockerfile:9-12](), [api/entrypoint.sh:33-63]()

---

### CDP Configuration

Chrome DevTools Protocol configuration for browser communication.

| Variable | Type | Default | Description |
|---|---|---|---|
| `CDP_REDIRECT_PORT` | string | `"9222"` | Port for CDP endpoint exposure (typically 9223 in Docker) |
| `CDP_DOMAIN` | string | undefined | Full domain for CDP endpoint (e.g., `example.com:9223`) |

**Docker Port Mapping:**

```yaml
ports:
  - "9223:9223"  # CDP port exposed to host
```

**Sources:** [api/src/env.ts:18-19](), [docker-compose.yml:6](), [api/entrypoint.sh:109]()

---

### Proxy Configuration

Controls proxy server integration for session traffic routing.

| Variable | Type | Default | Description |
|---|---|---|---|
| `PROXY_URL` | string | undefined | Upstream proxy URL (e.g., `http://user:pass@proxy.com:8080`) |
| `PROXY_INTERNAL_BYPASS` | string | undefined | Comma-separated list of hosts to bypass proxy (e.g., `localhost,127.0.0.1`) |

**Proxy Architecture:**

```mermaid
graph LR
    subgraph "Configuration"
        ProxyUrl["PROXY_URL<br/>env variable"]
        ProxyBypass["PROXY_INTERNAL_BYPASS<br/>localhost,127.0.0.1"]
    end
    
    subgraph "Session Creation"
        SessionConfig["BrowserLauncherOptions<br/>proxy: string"]
        ProxyFactory["ProxyServer.create()<br/>Proxy chain creation"]
    end
    
    subgraph "Browser Traffic"
        Chrome["Chrome Browser"]
        LocalProxy["Local Proxy Server<br/>Per-session port"]
        UpstreamProxy["Upstream Proxy<br/>From PROXY_URL"]
        Target["Target Website"]
    end
    
    ProxyUrl --> ProxyFactory
    ProxyBypass --> ProxyFactory
    SessionConfig --> ProxyFactory
    
    ProxyFactory --> LocalProxy
    Chrome --> LocalProxy
    LocalProxy -.->|bypass list| Target
    LocalProxy --> UpstreamProxy
    UpstreamProxy --> Target
```

**Sources:** [api/src/env.ts:20-21](), [api/src/env.ts:71]()

---

### Logging Configuration

Controls browser event logging, storage, and debug output.

| Variable | Type | Default | Description |
|---|---|---|---|
| `LOG_STORAGE_ENABLED` | boolean | `false` | Enable DuckDB storage for browser events |
| `LOG_STORAGE_PATH` | string | undefined | Path to DuckDB log file (e.g., `/data/logs/browser-logs.duckdb`) |
| `ENABLE_CDP_LOGGING` | boolean | `false` | Log all CDP messages (very verbose) |
| `LOG_CUSTOM_EMIT_EVENTS` | boolean | `false` | Log custom event emissions |
| `ENABLE_VERBOSE_LOGGING` | boolean | `false` | Enable verbose logging throughout the application |

**Log Storage Flow:**

```mermaid
graph TB
    subgraph "Configuration"
        LogEnabled["LOG_STORAGE_ENABLED<br/>true/false"]
        LogPath["LOG_STORAGE_PATH<br/>File path"]
    end
    
    subgraph "Instrumentation"
        TIM["TargetInstrumentationManager<br/>Event capture"]
        Events["Browser Events<br/>Network, Console, Runtime"]
    end
    
    subgraph "Storage"
        BrowserLogger["BrowserLogger<br/>Event aggregation"]
        DuckDB["DuckDB<br/>browser-logs.duckdb"]
    end
    
    subgraph "Query Layer"
        LogRoutes["LogsRoutes<br/>GET /v1/logs/query"]
        LogStream["WebSocket<br/>/v1/sessions/logs"]
    end
    
    LogEnabled --> BrowserLogger
    LogPath --> DuckDB
    
    TIM --> Events
    Events --> BrowserLogger
    BrowserLogger -.->|if enabled| DuckDB
    
    DuckDB --> LogRoutes
    DuckDB --> LogStream
```

**Docker Configuration:**

Docker Compose sets up log storage with persistent volumes:

```yaml
volumes:
  - logs:/data/logs
environment:
  - LOG_STORAGE_ENABLED=true
  - LOG_STORAGE_PATH=/data/logs/browser-logs.duckdb
```

**Sources:** [api/src/env.ts:34-78](), [docker-compose.yml:8-15]()

---

### Security and Stealth Configuration

Controls browser fingerprinting and anti-detection features.

| Variable | Type | Default | Description |
|---|---|---|---|
| `SKIP_FINGERPRINT_INJECTION` | boolean | `false` | Disable automatic fingerprint injection in browser contexts |
| `DEFAULT_HEADERS` | object | `{}` | Default HTTP headers to inject (JSON format) |
| `DEFAULT_TIMEZONE` | string | undefined | Default timezone for browser sessions (e.g., `America/New_York`) |
| `TIMEZONE_SERVICE_URL` | string | undefined | URL for timezone lookup service by IP/location |

**Fingerprint Configuration:**

```mermaid
graph LR
    subgraph "Environment Config"
        SkipFlag["SKIP_FINGERPRINT_INJECTION<br/>false = enabled"]
        DefaultHeaders["DEFAULT_HEADERS<br/>JSON object"]
        DefaultTZ["DEFAULT_TIMEZONE<br/>Timezone string"]
    end
    
    subgraph "Session Config"
        SessionOpts["BrowserLauncherOptions<br/>stealth: boolean"]
        FingerprintGen["fingerprint-generator<br/>Generate fingerprint"]
    end
    
    subgraph "Injection"
        FingerprintScript["loadFingerprintScript()<br/>Generate JS code"]
        PageContext["Page Context<br/>API overrides"]
    end
    
    SkipFlag -.->|if false| FingerprintGen
    SessionOpts --> FingerprintGen
    DefaultHeaders --> PageContext
    DefaultTZ --> SessionOpts
    
    FingerprintGen --> FingerprintScript
    FingerprintScript --> PageContext
```

**Sources:** [api/src/env.ts:21-55]()

---

### Storage Configuration

Controls file storage, cache directories, and data persistence.

| Variable | Type | Default | Description |
|---|---|---|---|
| `KILL_TIMEOUT` | string | `"0"` | Timeout in ms before forcefully killing browser processes (0 = no timeout) |

**Docker Volume Configuration:**

```mermaid
graph TB
    subgraph "Docker Volumes"
        LogsVol["logs volume<br/>/data/logs"]
        ExportsVol["exports volume<br/>/tmp/steel-browser-exports"]
        CacheVol[".cache volume<br/>/app/.cache"]
    end
    
    subgraph "Volume Usage"
        DuckDB["browser-logs.duckdb<br/>LOG_STORAGE_PATH"]
        SessionFiles["Session files<br/>FileService uploads/downloads"]
        PuppeteerCache["Puppeteer browser binaries<br/>PUPPETEER_CACHE_DIR"]
    end
    
    LogsVol --> DuckDB
    ExportsVol --> SessionFiles
    CacheVol --> PuppeteerCache
```

**Docker Compose Configuration:**

```yaml
volumes:
  - logs:/data/logs
  - exports:/tmp/steel-browser-exports
  - ./.cache:/app/.cache

volumes:
  logs:
    driver: local
  exports:
    driver: local
```

**Dockerfile Environment:**

```dockerfile
ENV PUPPETEER_CACHE_DIR=/app/.cache
```

**Sources:** [api/src/env.ts:26](), [docker-compose.yml:7-10](), [docker-compose.yml:35-39](), [api/Dockerfile:8]()

---

## Docker-Specific Configuration

### Container Environment Variables

The Docker container sets several environment variables that differ from local development:

```mermaid
graph TB
    subgraph "Dockerfile ENV"
        NodeEnv["NODE_ENV=production"]
        PuppeteerCache["PUPPETEER_CACHE_DIR=/app/.cache"]
        Display["DISPLAY=:10"]
        ChromeBin["CHROME_BIN=/usr/bin/chromium"]
    end
    
    subgraph "Entrypoint Overrides"
        CdpPort["CDP_REDIRECT_PORT=9223"]
        DisplayOverride["DISPLAY=:10"]
        DbusAddr["DBUS_SESSION_BUS_ADDRESS=autolaunch:"]
    end
    
    subgraph "Docker Compose ENV"
        Domain["DOMAIN=localhost:3000"]
        CdpDomain["CDP_DOMAIN=localhost:9223"]
        LogEnabled["LOG_STORAGE_ENABLED=true"]
        LogPath["LOG_STORAGE_PATH=/data/logs/browser-logs.duckdb"]
    end
    
    subgraph "Runtime Configuration"
        App["Node.js Application<br/>api/build/index.js"]
    end
    
    NodeEnv --> App
    PuppeteerCache --> App
    Display --> App
    ChromeBin --> App
    
    CdpPort --> App
    DisplayOverride --> App
    DbusAddr --> App
    
    Domain --> App
    CdpDomain --> App
    LogEnabled --> App
    LogPath --> App
```

**Sources:** [api/Dockerfile:7-12](), [api/Dockerfile:104-105](), [api/entrypoint.sh:108-116](), [docker-compose.yml:11-15]()

### Initialization Sequence

The Docker entrypoint performs the following initialization steps:

1. **DBus Initialization** - Required for Chrome browser communication ([api/entrypoint.sh:12-31]())
2. **Chrome Verification** - Validates Chrome and ChromeDriver installation ([api/entrypoint.sh:33-63]())
3. **Nginx Startup** - Launches nginx reverse proxy (unless `--no-nginx` flag) ([api/entrypoint.sh:66-89]())
4. **Environment Export** - Sets `CDP_REDIRECT_PORT` and `DISPLAY` ([api/entrypoint.sh:109-110]())
5. **Application Launch** - Starts Node.js application directly (bypassing npm) ([api/entrypoint.sh:124]())

**Sources:** [api/entrypoint.sh:92-127]()

---

## UI Configuration

The UI workspace has its own configuration system for connecting to the API server.

### UI Environment Variables

| Variable | Type | Description |
|---|---|---|
| `VITE_API_URL` | string | API server URL (e.g., `http://localhost:3000`) |
| `VITE_WS_URL` | string | WebSocket server URL (e.g., `ws://localhost:3000`) |
| `API_URL` | string | Used by nginx template to configure API proxy in Docker |

**Sources:** [.env.example:1-2](), [ui/.env.local.example:1-2](), [ui/nginx.conf.template:13-19]()

### UI Configuration Flow

```mermaid
graph LR
    subgraph "Build Time"
        ViteConfig[".env files<br/>VITE_API_URL"]
        Build["Vite Build<br/>Embedded in bundle"]
        StaticFiles["Static Files<br/>/usr/share/nginx/html"]
    end
    
    subgraph "Runtime"
        NginxTemplate["nginx.conf.template<br/>API_URL variable"]
        Entrypoint["entrypoint.sh<br/>envsubst processing"]
        NginxConfig["nginx.conf<br/>Final configuration"]
    end
    
    subgraph "Client"
        Browser["Web Browser"]
        ApiClient["Generated API Client<br/>Uses VITE_API_URL"]
    end
    
    ViteConfig --> Build
    Build --> StaticFiles
    
    NginxTemplate --> Entrypoint
    Entrypoint --> NginxConfig
    
    StaticFiles --> Browser
    Browser --> ApiClient
    NginxConfig -.->|proxies| ApiClient
```

**Sources:** [docker-compose.yml:19-28](), [ui/Dockerfile:22-26](), [ui/nginx.conf.template:1-33]()

---

## Complete Configuration Reference

### Environment Variables by Category

| Category | Variables | Location in Code |
|---|---|---|
| **Server** | `NODE_ENV`, `HOST`, `DOMAIN`, `PORT`, `USE_SSL` | [api/src/env.ts:7-17]() |
| **CDP** | `CDP_REDIRECT_PORT`, `CDP_DOMAIN` | [api/src/env.ts:18-19]() |
| **Proxy** | `PROXY_URL`, `PROXY_INTERNAL_BYPASS` | [api/src/env.ts:20-21](), [api/src/env.ts:71]() |
| **Chrome** | `CHROME_EXECUTABLE_PATH`, `CHROME_HEADLESS`, `DISPLAY`, `CHROME_ARGS`, `FILTER_CHROME_ARGS`, `DEBUG_CHROME_PROCESS`, `CHROME_USER_DATA_DIR`, `DISABLE_CHROME_SANDBOX` | [api/src/env.ts:27-83]() |
| **Logging** | `ENABLE_CDP_LOGGING`, `LOG_CUSTOM_EMIT_EVENTS`, `ENABLE_VERBOSE_LOGGING`, `LOG_STORAGE_ENABLED`, `LOG_STORAGE_PATH` | [api/src/env.ts:34-78]() |
| **Security** | `SKIP_FINGERPRINT_INJECTION`, `DEFAULT_HEADERS`, `DEFAULT_TIMEZONE`, `TIMEZONE_SERVICE_URL` | [api/src/env.ts:21-55]() |
| **Storage** | `KILL_TIMEOUT` | [api/src/env.ts:26]() |

### Configuration Access Pattern

All configuration is accessed through the type-safe `env` object exported from [api/src/env.ts:86]():

```typescript
import { env } from "./env.js";

// Type-safe access with IntelliSense
const port = env.PORT;
const isHeadless = env.CHROME_HEADLESS;
const headers = env.DEFAULT_HEADERS;
```

**Sources:** [api/src/env.ts:1-86]()

---

# Page: Docker Deployment

# Docker Deployment

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.dockerignore](.dockerignore)
- [.github/workflows/check-build.yml](.github/workflows/check-build.yml)
- [Dockerfile](Dockerfile)
- [README.md](README.md)
- [api/.dockerignore](api/.dockerignore)
- [api/Dockerfile](api/Dockerfile)
- [api/entrypoint.sh](api/entrypoint.sh)
- [docker-compose.dev.yml](docker-compose.dev.yml)
- [docker-compose.yml](docker-compose.yml)
- [images/star_img.png](images/star_img.png)
- [render.yaml](render.yaml)
- [ui/Dockerfile](ui/Dockerfile)

</details>



## Purpose and Scope

This document covers the Docker deployment architecture for Steel Browser, including multi-stage build processes, container orchestration, volume strategies, network configuration, and initialization procedures. For general installation instructions, see [Installation](#2.1). For environment variable configuration, see [Environment Configuration](#2.2). For production operations and monitoring, see [Container Architecture](#13.1) and [Storage & Persistence](#13.2).

Steel Browser provides three deployment approaches via Docker:
1. **Combined API + UI image** - Single container with both services.
2. **Separate API and UI images** - Multi-container orchestration via Docker Compose.
3. **Development mode** - Build-from-source with live updates.

## Deployment Options

Steel Browser is distributed as pre-built Docker images via GitHub Container Registry:

| Image | Purpose | Base Image | Entry Point |
|-------|---------|------------|-------------|
| `ghcr.io/steel-dev/steel-browser` | Combined API + UI | `node:22.13.0` | `/app/api/entrypoint.sh` |
| `ghcr.io/steel-dev/steel-browser-api` | API service only | `node:22.13.0-slim` | `/app/api/entrypoint.sh` |
| `ghcr.io/steel-dev/steel-browser-ui` | UI service only | `nginx:alpine` | `/docker-entrypoint.sh` |

**Quick start commands:**

```bash
# Single container deployment (API + UI combined)
docker run -p 3000:3000 -p 9223:9223 ghcr.io/steel-dev/steel-browser

# Multi-container deployment (API + UI separate)
docker compose up

# Development mode (build from source)
docker compose -f docker-compose.dev.yml up --build
```

**Sources:** [README.md:84-106](), [docker-compose.yml:1-40](), [docker-compose.dev.yml:1-35]()

## Multi-Stage Build Architecture

Steel Browser uses Docker multi-stage builds to optimize image size and separate build-time from runtime dependencies.

### API Container Build Stages

```mermaid
graph TB
    subgraph "Stage 1: base"
        Base["base stage<br/>node:22.13.0-slim"]
        BaseEnv["Environment Setup<br/>PUPPETEER_CACHE_DIR=/app/.cache<br/>DISPLAY=:10<br/>CHROME_BIN=/usr/bin/chromium"]
        BaseDeps["Runtime Dependencies<br/>expat, libxslt1.1, libpam0g"]
        
        Base --> BaseEnv
        Base --> BaseDeps
    end
    
    subgraph "Stage 2: build"
        BuildStage["build stage<br/>FROM base"]
        BuildTools["Build Tools<br/>build-essential<br/>pkg-config<br/>python-is-python3<br/>xvfb"]
        Workspace["Workspace Files<br/>package.json<br/>package-lock.json<br/>api/"]
        NpmInstall["npm ci --include=dev<br/>--workspace=api"]
        NpmBuild["npm run build -w api"]
        RecorderBuild["Build recorder extension<br/>api/extensions/recorder"]
        NpmPrune["npm prune --omit=dev"]
        
        BuildStage --> BuildTools
        BuildStage --> Workspace
        Workspace --> NpmInstall
        NpmInstall --> NpmBuild
        NpmBuild --> RecorderBuild
        RecorderBuild --> NpmPrune
    end
    
    subgraph "Stage 3: production"
        ProdStage["production stage<br/>FROM base"]
        ProdDeps["Production Dependencies<br/>nginx, chromium, chromium-driver<br/>xvfb, fonts, dbus, JRE"]
        CopyArtifacts["COPY --from=build /app /app"]
        Entrypoint["ENTRYPOINT<br/>/app/api/entrypoint.sh"]
        Expose["EXPOSE 3000 9223"]
        
        ProdStage --> ProdDeps
        ProdStage --> CopyArtifacts
        ProdStage --> Entrypoint
        ProdStage --> Expose
    end
    
    BaseDeps -.->|inherited| BuildStage
    NpmPrune -.->|artifacts| CopyArtifacts
```

The `base` stage establishes the foundation with minimal dependencies [api/Dockerfile:3-26](). The `build` stage inherits from `base` and adds build tools like `build-essential` and `xvfb` [api/Dockerfile:28-43](). It builds the API and the recorder extension [api/Dockerfile:52-56](). The `production` stage copies compiled artifacts and installs runtime tools like `chromium` and `chromium-driver` [api/Dockerfile:62-109]().

**Sources:** [api/Dockerfile:1-110](), [Dockerfile:1-126]()

### Combined Image Build Strategy

The combined API + UI image uses a three-stage build process to integrate both services:

```mermaid
graph LR
    subgraph "ui-build stage"
        UIBase["node:22.13.0"]
        UIWorkspace["ui/ directory<br/>package.json"]
        UIInstall["npm ci -w ui"]
        UIBuild["npm run build -w ui<br/>--base=/ui"]
        UIDist["ui/dist artifacts"]
        
        UIBase --> UIWorkspace
        UIWorkspace --> UIInstall
        UIInstall --> UIBuild
        UIBuild --> UIDist
    end
    
    subgraph "api-build stage"
        APIBase["base stage"]
        APIWorkspace["api/ directory<br/>extensions/recorder"]
        APIInstall["npm ci -w api"]
        APIBuild["npm run build -w api"]
        APIArtifacts["api/build artifacts"]
        
        APIBase --> APIWorkspace
        APIWorkspace --> APIInstall
        APIInstall --> APIBuild
        APIBuild --> APIArtifacts
    end
    
    subgraph "production stage"
        ProdBase["base stage"]
        CopyAPI["COPY --from=api-build<br/>/app /app"]
        CopyUI["COPY --from=ui-build<br/>/app/ui/dist /app/ui/dist"]
        FinalImage["Combined Image<br/>ghcr.io/steel-dev/steel-browser"]
        
        ProdBase --> CopyAPI
        CopyAPI --> CopyUI
        CopyUI --> FinalImage
    end
    
    UIDist -.->|copy| CopyUI
    APIArtifacts -.->|copy| CopyAPI
```

The UI build stage compiles React assets with the `--base=/ui` flag [Dockerfile:33](). The API build stage compiles the core service and the recorder extension [Dockerfile:59-66](). The production stage merges both into a single image [Dockerfile:112-115]().

**Sources:** [Dockerfile:1-126](), [ui/Dockerfile:1-30]()

## Container Services and Orchestration

Docker Compose orchestrates the Steel Browser services using the `steel-network` bridge network [docker-compose.yml:31-33]().

### Service Architecture

```mermaid
graph TB
    subgraph "Host Machine"
        HostAPI["localhost:3000<br/>API endpoint"]
        HostCDP["localhost:9223<br/>CDP debugger"]
        HostUI["localhost:5173<br/>UI dashboard"]
    end
    
    subgraph "Docker Network: steel-network"
        subgraph "api service"
            APIContainer["API Container<br/>ghcr.io/steel-dev/steel-browser-api"]
            NodeProcess["Node.js Process<br/>node ./api/build/index.js"]
            ChromiumProcess["Chromium Browser<br/>/usr/bin/chromium"]
            XvfbProcess["Xvfb Display<br/>:10"]
            
            APIContainer --> NodeProcess
            APIContainer --> ChromiumProcess
            APIContainer --> XvfbProcess
        end
        
        subgraph "ui service"
            UIContainer["UI Container<br/>ghcr.io/steel-dev/steel-browser-ui"]
            UIProcess["nginx:alpine<br/>Serves static assets"]
            
            UIContainer --> UIProcess
        end
    end
    
    HostAPI --> APIContainer
    HostCDP --> ChromiumProcess
    HostUI --> UIContainer
    
    UIContainer -.->|API_URL| APIContainer
```

**Service definitions in `docker-compose.yml`:**

| Service | Image | Ports | Internal DNS |
|---------|-------|-------|--------------|
| `api` | `steel-browser-api:latest` | 3000, 9223 | `api:3000` |
| `ui` | `steel-browser-ui:latest` | 5173 → 80 | `ui:80` |

The API service is accessible at `http://api:3000` from within the network [docker-compose.yml:24]().

**Sources:** [docker-compose.yml:1-40](), [docker-compose.dev.yml:1-35]()

## Volume Management Strategies

Steel Browser employs distinct storage strategies for cache, logs, and exports.

```mermaid
graph TB
    subgraph "API Container Storage"
        NodeApp["Node.js App"]
        
        subgraph "Volumes & Mounts"
            CacheMount["/app/.cache<br/>PUPPETEER_CACHE_DIR"]
            LogPath["/data/logs<br/>LOG_STORAGE_PATH"]
            ExportPath["/tmp/steel-browser-exports"]
        end
        
        NodeApp --> CacheMount
        NodeApp --> LogPath
        NodeApp --> ExportPath
    end
    
    subgraph "Host Persistence"
        HostCache[".cache/ (bind)"]
        LogsVol["logs (named volume)"]
        ExportsVol["exports (named volume)"]
    end
    
    CacheMount --- HostCache
    LogPath --- LogsVol
    ExportPath --- ExportsVol
```

| Mount Point | Type | Persistence | Reason |
|-------------|------|-------------|---------|
| `/app/.cache` | Bind mount | Host-level | Share Puppeteer binaries [docker-compose.yml:10]() |
| `/data/logs` | Named volume | Docker-managed | Persistent DuckDB logs [docker-compose.yml:15]() |
| `/tmp/steel-browser-exports` | Named volume | Docker-managed | Temporary session archives [docker-compose.yml:9]() |

**Sources:** [docker-compose.yml:7-15](), [api/Dockerfile:8](), [Dockerfile:8]()

## Entrypoint Initialization Process

The `entrypoint.sh` script performs container initialization before launching the Node.js application [api/entrypoint.sh:124]().

### Initialization Sequence

```mermaid
graph TB
    Start["ENTRYPOINT /app/api/entrypoint.sh"]
    
    ParseArgs["Parse --no-nginx"]
    
    DebugCheck{"DEBUG=true?"}
    InitDBus["init_dbus()<br/>dbus-daemon --system"]
    VerifyChrome["verify_chrome()<br/>Check chromium & chromedriver"]
    
    NginxCheck{"START_NGINX=true?"}
    StartNginx["start_nginx()<br/>nginx -c /app/api/nginx.conf"]
    
    SetEnv["Set CDP_REDIRECT_PORT=9223<br/>DISPLAY=:10"]
    
    ExecNode["exec node ./api/build/index.js"]
    
    Start --> ParseArgs
    ParseArgs --> DebugCheck
    DebugCheck -->|Yes| InitDBus
    InitDBus --> VerifyChrome
    VerifyChrome --> NginxCheck
    NginxCheck -->|Yes| StartNginx
    StartNginx --> SetEnv
    SetEnv --> ExecNode
```

The script uses `exec` to replace the shell process, ensuring proper signal handling for graceful shutdown [api/entrypoint.sh:124](). It verifies that `chromium` and `chromedriver` are correctly installed in the production environment [api/entrypoint.sh:33-63]().

**Sources:** [api/entrypoint.sh:1-127](), [api/Dockerfile:100-107]()

## Network Configuration

Steel Browser uses Docker bridge networking for service discovery.

| Host Port | Container Port | Service | Protocol | Purpose |
|-----------|----------------|---------|----------|---------|
| 3000 | 3000 | api | HTTP/WS | REST API [docker-compose.yml:5]() |
| 9223 | 9223 | api | WS | CDP Debugging [docker-compose.yml:6]() |
| 5173 | 80 | ui | HTTP | React Dashboard [docker-compose.yml:22]() |

**Sources:** [docker-compose.yml:1-40](), [docker-compose.dev.yml:1-35]()

## Development vs Production Compose Files

Steel Browser provides two configurations: `docker-compose.yml` for production and `docker-compose.dev.yml` for local development.

| Feature | docker-compose.yml | docker-compose.dev.yml |
|---------|-------------------|------------------------|
| Images | Pre-built from GHCR [docker-compose.yml:3]() | Built from Dockerfiles [docker-compose.dev.yml:3]() |
| Build Context | N/A | Root directory [docker-compose.dev.yml:4]() |
| Volumes | Full persistence (logs, exports) | Minimal (cache only) [docker-compose.dev.yml:15]() |
| Logging | DuckDB storage enabled [docker-compose.yml:14]() | Disabled by default |

For Mac Silicon users, use `DOCKER_DEFAULT_PLATFORM=linux/arm64` when running compose [README.md:103-106]().

**Sources:** [docker-compose.yml:1-40](), [docker-compose.dev.yml:1-35](), [README.md:97-122]()

## Single Container Deployment

The combined image (`ghcr.io/steel-dev/steel-browser`) runs both API and UI in one container.

- **API Endpoint**: `http://localhost:3000`
- **UI Endpoint**: `http://localhost:3000/ui`
- **CDP Port**: `9223`

This is achieved by copying the UI build artifacts into the API container's `/app/ui/dist` directory [Dockerfile:115]().

**Sources:** [Dockerfile:1-126](), [README.md:86-93]()

## Cloud Platform Deployment

### Render.com
The `render.yaml` configuration defines a web service using the root `Dockerfile` [render.yaml:3-5](). It includes a 1GB persistent disk for the browser cache [render.yaml:14-17]().

### Railway
Railway deployments use the root `Dockerfile` and are triggered via the 1-click deploy button [README.md:79]().

**Sources:** [render.yaml:1-18](), [README.md:73-79]()

---

# Page: Core Services

# Core Services

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [api/src/modules/files/files.controller.ts](api/src/modules/files/files.controller.ts)
- [api/src/modules/files/files.routes.ts](api/src/modules/files/files.routes.ts)
- [api/src/modules/files/files.schema.ts](api/src/modules/files/files.schema.ts)
- [api/src/plugins/file-storage.ts](api/src/plugins/file-storage.ts)
- [api/src/services/cdp/cdp.service.ts](api/src/services/cdp/cdp.service.ts)
- [api/src/services/cdp/plugins/core/base-plugin.ts](api/src/services/cdp/plugins/core/base-plugin.ts)
- [api/src/services/cdp/plugins/core/plugin-manager.ts](api/src/services/cdp/plugins/core/plugin-manager.ts)
- [api/src/services/file.service.ts](api/src/services/file.service.ts)
- [api/src/services/session.service.ts](api/src/services/session.service.ts)

</details>



This page documents the core service layer of the steel-browser system, which consists of three primary services: `CDPService`, `SessionService`, and `FileService`. These services form the backbone of the browser automation infrastructure, handling browser lifecycle management, session orchestration, and file operations.

For detailed information about specific service features:
- For browser control via Chrome DevTools Protocol, see [CDPService](#3.1)
- For session lifecycle and proxy management, see [SessionService](#3.2)  
- For file upload/download operations, see [FileService](#3.3)
- For WebDriver compatibility, see [Selenium Support](#8.2)
- For real-time event streaming, see [Real-time Communication](#10)

## Service Layer Architecture

The core services implement a layered architecture where `SessionService` orchestrates high-level session management while delegating browser control to either `CDPService` (primary) or `SeleniumService` (compatibility mode). `FileService` provides cross-cutting file management capabilities including real-time file watching and archive generation.

### Service Dependency Graph

```mermaid
graph TB
    SessionService["SessionService<br/>(api/src/services/session.service.ts)"]
    CDPService["CDPService<br/>(api/src/services/cdp/cdp.service.ts)"]
    SeleniumService["SeleniumService<br/>(api/src/services/selenium.service.ts)"]
    FileService["FileService<br/>(api/src/services/file.service.ts)"]
    
    PluginManager["PluginManager<br/>(api/src/services/cdp/plugins/core/plugin-manager.ts)"]
    ChromeContextService["ChromeContextService<br/>(api/src/services/context/chrome-context.service.ts)"]
    TargetInstrumentationManager["TargetInstrumentationManager<br/>(api/src/services/cdp/instrumentation/target-manager.ts)"]
    BrowserLogger["BrowserLogger<br/>(api/src/services/cdp/instrumentation/browser-logger.ts)"]
    TimezoneFetcher["TimezoneFetcher<br/>(api/src/services/timezone-fetcher.service.ts)"]
    ProxyServer["ProxyServer<br/>(api/src/utils/proxy.ts)"]
    
    ChromeBrowser["Chrome/Chromium<br/>Browser Process"]
    DuckDB["DuckDB<br/>browser-logs.duckdb"]
    FileStorage["File Storage<br/>/files"]
    
    SessionService -->|"orchestrates"| CDPService
    SessionService -->|"alternative mode"| SeleniumService
    SessionService -->|"manages files"| FileService
    SessionService -->|"creates proxies"| ProxyServer
    SessionService -->|"resolves timezone"| TimezoneFetcher
    
    CDPService -->|"launches & controls"| ChromeBrowser
    CDPService -->|"manages plugins"| PluginManager
    CDPService -->|"persists context"| ChromeContextService
    CDPService -->|"instruments targets"| TargetInstrumentationManager
    CDPService -->|"uses singleton"| FileService
    
    SeleniumService -->|"controls via WebDriver"| ChromeBrowser
    
    TargetInstrumentationManager -->|"logs events to"| BrowserLogger
    BrowserLogger -->|"stores in"| DuckDB
    
    FileService -->|"manages uploads/downloads"| FileStorage
    
    ChromeBrowser -.->|"routes through"| ProxyServer
```

**Sources:** [api/src/services/session.service.ts:58-91](), [api/src/services/cdp/cdp.service.ts:83-185](), [api/src/services/file.service.ts:16-45]()

## Service Responsibilities

| Service | Primary Role | Key Dependencies | Storage |
|---------|-------------|------------------|---------|
| `SessionService` | Session lifecycle orchestration, proxy management | `CDPService`, `SeleniumService`, `FileService`, `TimezoneFetcher` | Session metadata in memory |
| `CDPService` | Browser process control, CDP protocol handling, fingerprinting | `PluginManager`, `ChromeContextService`, `TargetInstrumentationManager`, `BrowserLogger` | Context in userDataDir, logs in DuckDB |
| `FileService` | File upload/download, archive generation, file watching | `chokidar`, `archiver` | `/files` (prod) or `/tmp/files` (dev) |

**Sources:** [api/src/services/session.service.ts:69-91](), [api/src/services/cdp/cdp.service.ts:121-185](), [api/src/services/file.service.ts:27-38]()

## CDPService

The `CDPService` class is the primary browser automation service, responsible for launching Chrome/Chromium browsers, controlling them via the Chrome DevTools Protocol, and managing all browser-level operations. It integrates a plugin system via `PluginManager` to allow lifecycle hooks.

### Core Components

The `CDPService` constructor initializes multiple subsystems:

```mermaid
graph LR
    CDPService["CDPService"]
    
    subgraph "Browser Control"
        browserInstance["browserInstance: Browser | null"]
        wsEndpoint["wsEndpoint: string | null"]
        primaryPage["primaryPage: Page | null"]
        wsProxyServer["wsProxyServer: httpProxy"]
    end
    
    subgraph "Configuration"
        launchConfig["launchConfig: BrowserLauncherOptions"]
        currentSessionConfig["currentSessionConfig: BrowserLauncherOptions | null"]
        defaultLaunchConfig["defaultLaunchConfig: BrowserLauncherOptions"]
        fingerprintData["fingerprintData: BrowserFingerprintWithHeaders | null"]
    end
    
    subgraph "Context & State"
        sessionContext["sessionContext: SessionData | null"]
        trackedOrigins["trackedOrigins: Set<string>"]
        chromeSessionService["chromeSessionService: ChromeContextService"]
    end
    
    subgraph "Plugin System"
        pluginManager["pluginManager: PluginManager"]
        launchMutators["launchMutators: Function[]"]
        shutdownMutators["shutdownMutators: Function[]"]
    end
    
    subgraph "Instrumentation"
        targetInstrumentationManager["targetInstrumentationManager: TargetInstrumentationManager"]
        instrumentationLogger["instrumentationLogger: BrowserLogger"]
    end
    
    subgraph "Utilities"
        retryManager["retryManager: RetryManager"]
        chromeExecPath["chromeExecPath: string"]
        logger["logger: FastifyBaseLogger"]
    end
    
    CDPService --> browserInstance
    CDPService --> launchConfig
    CDPService --> sessionContext
    CDPService --> pluginManager
    CDPService --> targetInstrumentationManager
    CDPService --> retryManager
```

**Sources:** [api/src/services/cdp/cdp.service.ts:83-185]()

### Plugin System Hooks

`CDPService` utilizes `PluginManager` to notify registered plugins of browser events. Plugins extend `BasePlugin` and can react to session start, browser launch, page creation, and shutdown.

| Hook | Description |
|------|-------------|
| `onSessionStart` | Called before a session begins |
| `onBrowserLaunch` | Called immediately after the browser process starts |
| `onPageCreated` | Triggered when a new `Page` (tab) is opened |
| `onShutdown` | Triggered during service termination with a `ShutdownReason` |

**Sources:** [api/src/services/cdp/plugins/core/base-plugin.ts:43-55](), [api/src/services/cdp/plugins/core/plugin-manager.ts:54-216]()

## SessionService

The `SessionService` orchestrates browser sessions at a higher level than `CDPService`, managing session lifecycle, proxy configuration, and coordination between CDP and Selenium modes.

### Session Structure

Each session in `SessionService` is represented by the `Session` type, which includes URLs for debugging and the session viewer.

```typescript
type Session = SessionDetails & {
  completion: Promise<void>;
  complete: (value: void) => void;
  proxyServer: IProxyServer | undefined;
};
```

**Sources:** [api/src/services/session.service.ts:25-29](), [api/src/services/session.service.ts:40-51]()

### Proxy Factory Pattern

The `SessionService` uses a factory pattern for proxy creation, allowing customization and bandwidth optimization through `IProxyServer`.

```mermaid
graph LR
    SessionService["SessionService"]
    ProxyFactory["proxyFactory: ProxyFactory"]
    DefaultFactory["Default:<br/>(proxyUrl) => new ProxyServer(proxyUrl)"]
    
    ProxyServer["ProxyServer<br/>Instance"]
    
    StartSession["startSession(options)"]
    
    SessionService --> ProxyFactory
    ProxyFactory -.->|"Default"| DefaultFactory
    
    StartSession --> ProxyFactory
    ProxyFactory --> ProxyServer
    
    ProxyServer --> Listen["listen()<br/>Start proxy"]
    ProxyServer --> Stats["txBytes, rxBytes<br/>Traffic statistics"]
```

**Sources:** [api/src/services/session.service.ts:53-56](), [api/src/services/session.service.ts:64](), [api/src/services/session.service.ts:208-211]()

## FileService

The `FileService` provides file management capabilities for browser sessions. Unlike the other services, it includes a `chokidar` file watcher that automatically triggers ZIP archive generation whenever files are added or modified in the session storage.

### Archive Generation and Watching

`FileService` maintains a debounced archive process to ensure the `files.zip` is up-to-date for bulk downloads.

```mermaid
graph TB
    FileService["FileService"]
    Watcher["chokidar.watch()"]
    Storage["/files directory"]
    Debounce["debouncedCreateArchive()"]
    Archiver["archiver ('zip')"]
    ZipFile["files.zip"]

    Storage -- "FS Events" --> Watcher
    Watcher -- "add/unlink/change" --> Debounce
    Debounce -- "Trigger" --> Archiver
    Archiver -- "Output" --> ZipFile
```

**Sources:** [api/src/services/file.service.ts:27-38](), [api/src/services/file.service.ts:62-86]()

### File Operations API

The `FilesController` interfaces with `FileService` to provide RESTful access to session files.

| Operation | Controller Method | Service Method |
|-----------|-------------------|----------------|
| Upload | `handleFileUpload` | `saveFile` |
| Download | `handleFileDownload` | `downloadFile` |
| List | `handleFileList` | `listFiles` |
| Bulk Download | `handleDownloadArchive` | `getPrebuiltArchivePath` |

**Sources:** [api/src/modules/files/files.controller.ts:41-157](), [api/src/modules/files/files.routes.ts:18-146](), [api/src/services/file.service.ts:110-220]()

## Service Integration Points

### SessionService → CDPService Coordination

`SessionService` manages the transition between browser modes. If a session is requested in Selenium mode, it shuts down the `CDPService` instance before handing control to `SeleniumService`.

**Sources:** [api/src/services/session.service.ts:213-242]()

### Error Handling Strategy

The core services implement a tiered error handling approach defined in `launch-errors.ts`, categorizing failures into `NetworkError`, `FingerprintError`, `PluginError`, and others to provide better debugging context.

**Sources:** [api/src/services/cdp/errors/launch-errors.ts:52-71](), [api/src/services/cdp/cdp.service.ts:80]()

---

# Page: CDPService

# CDPService

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [api/.prettierrc](api/.prettierrc)
- [api/src/scripts/index.ts](api/src/scripts/index.ts)
- [api/src/services/cdp/cdp.service.ts](api/src/services/cdp/cdp.service.ts)
- [api/src/services/cdp/errors/launch-errors.ts](api/src/services/cdp/errors/launch-errors.ts)
- [api/src/services/cdp/plugins/core/base-plugin.ts](api/src/services/cdp/plugins/core/base-plugin.ts)
- [api/src/services/cdp/plugins/core/plugin-manager.ts](api/src/services/cdp/plugins/core/plugin-manager.ts)
- [api/src/services/cdp/utils/error-handlers.ts](api/src/services/cdp/utils/error-handlers.ts)
- [api/src/services/cdp/utils/validation.ts](api/src/services/cdp/utils/validation.ts)
- [api/src/utils/browser.ts](api/src/utils/browser.ts)
- [repl/package.json](repl/package.json)
- [ui/package.json](ui/package.json)

</details>



## Overview

`CDPService` is the core service responsible for managing Chrome/Chromium browser instances via the Chrome DevTools Protocol (CDP). It handles the complete browser lifecycle including launch, configuration, fingerprinting, request interception, session management, and cleanup. `CDPService` serves as the primary interface between the steel-browser API and the underlying browser automation infrastructure.

For information about orchestrating multiple browser sessions, see [SessionService](3.2). For details on the plugin architecture that extends `CDPService` functionality, see [Plugin System](9).

**Sources:** [api/src/services/cdp/cdp.service.ts:83-185]()

---

## System Architecture

`CDPService` acts as the central coordinator for browser automation, integrating multiple subsystems to provide comprehensive browser control.

### Core Component Architecture

```mermaid
graph TB
    CDPService["CDPService<br/>(EventEmitter)"]
    
    subgraph "Browser Control"
        Browser["Browser<br/>(puppeteer-core)"]
        PrimaryPage["primaryPage<br/>(Page)"]
        WSEndpoint["wsEndpoint<br/>(WebSocket)"]
        BrowserProcess["Browser Process"]
    end
    
    subgraph "Plugin System"
        PluginManager["PluginManager"]
        BasePlugins["BasePlugin[]<br/>(Registered Plugins)"]
    end
    
    subgraph "Instrumentation"
        TargetInstrumentationManager["TargetInstrumentationManager"]
        BrowserLogger["BrowserLogger<br/>(instrumentationLogger)"]
    end
    
    subgraph "Configuration"
        LaunchConfig["launchConfig<br/>(BrowserLauncherOptions)"]
        FingerprintData["fingerprintData<br/>(BrowserFingerprintWithHeaders)"]
        SessionContext["sessionContext<br/>(SessionData)"]
    end
    
    subgraph "Support Services"
        ChromeContextService["ChromeContextService<br/>(chromeSessionService)"]
        RetryManager["RetryManager<br/>(retryManager)"]
        FileService["FileService<br/>(singleton)"]
        TimezoneFetcher["TimezoneFetcher"]
    end
    
    CDPService --> Browser
    CDPService --> PluginManager
    CDPService --> TargetInstrumentationManager
    CDPService --> ChromeContextService
    CDPService --> RetryManager
    CDPService --> FileService
    
    Browser --> PrimaryPage
    Browser --> WSEndpoint
    Browser --> BrowserProcess
    
    PluginManager --> BasePlugins
    TargetInstrumentationManager --> BrowserLogger
    
    CDPService -.->|"stores"| LaunchConfig
    CDPService -.->|"stores"| FingerprintData
    CDPService -.->|"stores"| SessionContext
```

**Sources:** [api/src/services/cdp/cdp.service.ts:83-185](), [api/src/services/cdp/plugins/core/plugin-manager.ts:7-16](), [api/src/services/cdp/instrumentation/target-manager.ts:1-20]()

### Key Class Members

| Member | Type | Purpose |
|--------|------|---------|
| `browserInstance` | `Browser \| null` | Active Puppeteer browser instance [api/src/services/cdp/cdp.service.ts:87]() |
| `wsEndpoint` | `string \| null` | WebSocket endpoint for CDP connections [api/src/services/cdp/cdp.service.ts:88]() |
| `primaryPage` | `Page \| null` | Primary browser page for operations [api/src/services/cdp/cdp.service.ts:93]() |
| `fingerprintData` | `BrowserFingerprintWithHeaders \| null` | Generated browser fingerprint [api/src/services/cdp/cdp.service.ts:89]() |
| `sessionContext` | `SessionData \| null` | Current session state (cookies, storage) [api/src/services/cdp/cdp.service.ts:90]() |
| `launchConfig` | `BrowserLauncherOptions \| undefined` | Current launch configuration [api/src/services/cdp/cdp.service.ts:94]() |
| `pluginManager` | `PluginManager` | Manages plugin lifecycle [api/src/services/cdp/cdp.service.ts:99]() |
| `targetInstrumentationManager` | `TargetInstrumentationManager` | Instruments targets for logging [api/src/services/cdp/cdp.service.ts:103]() |
| `instrumentationLogger` | `BrowserLogger` | Logs browser events to storage [api/src/services/cdp/cdp.service.ts:104]() |
| `chromeSessionService` | `ChromeContextService` | Manages session context persistence [api/src/services/cdp/cdp.service.ts:101]() |
| `retryManager` | `RetryManager` | Handles launch retries [api/src/services/cdp/cdp.service.ts:102]() |

**Sources:** [api/src/services/cdp/cdp.service.ts:83-104]()

---

## Browser Lifecycle Management

`CDPService` manages the complete browser lifecycle from launch to shutdown, including session management and browser reuse optimization.

### Launch Process

```mermaid
stateDiagram-v2
    [*] --> ValidateConfig: launch(config)
    
    ValidateConfig --> CheckExisting: Configuration validated
    
    CheckExisting --> ReuseInstance: Similar config detected
    CheckExisting --> ShutdownExisting: Different config
    CheckExisting --> LaunchNew: No existing instance
    
    ReuseInstance --> RefreshPrimaryPage
    RefreshPrimaryPage --> InjectContext: Session context provided
    RefreshPrimaryPage --> NotifyPlugins: No session context
    InjectContext --> NotifyPlugins
    NotifyPlugins --> [*]: Browser ready
    
    ShutdownExisting --> LaunchNew: Shutdown complete
    
    LaunchNew --> CleanupFiles
    CleanupFiles --> GenerateFingerprint: Stealth enabled
    CleanupFiles --> SetupExtensions: Stealth disabled
    GenerateFingerprint --> SetupExtensions
    SetupExtensions --> ValidateTimezone
    ValidateTimezone --> BuildLaunchArgs
    BuildLaunchArgs --> SetupUserPreferences
    SetupUserPreferences --> LaunchBrowser
    LaunchBrowser --> ConfigureDownloads
    ConfigureDownloads --> AttachHandlers
    AttachHandlers --> InstrumentTargets
    InstrumentTargets --> InjectContextNew: Session context provided
    InstrumentTargets --> FinalizeSetup: No session context
    InjectContextNew --> FinalizeSetup
    FinalizeSetup --> [*]: Browser ready
```

**Sources:** [api/src/services/cdp/cdp.service.ts:516-1041](), [api/src/services/cdp/utils/validation.ts:114-189]()

### Browser Launch Method

The `launch()` method is the primary entry point for starting a browser instance. It includes retry logic and comprehensive error handling:

```typescript
public async launch(
  config?: BrowserLauncherOptions,
  retryOptions?: Partial<RetryOptions>,
): Promise<Browser>
```

Key steps in the launch process:

1. **Configuration Validation** - Validates dimensions, proxy URL, and other parameters [api/src/services/cdp/utils/validation.ts:31-62]().
2. **File Cleanup** - Cleans up temporary files before launch [api/src/services/cdp/cdp.service.ts:618-631]().
3. **Launch Mutators** - Executes registered pre-launch hooks [api/src/services/cdp/cdp.service.ts:637-651]().
4. **Fingerprint Generation** - Generates realistic browser fingerprint if stealth enabled [api/src/services/cdp/cdp.service.ts:655-698]().
5. **Extension Resolution** - Resolves extension paths including session extensions [api/src/services/cdp/cdp.service.ts:709-741]().
6. **Timezone Validation** - Validates and resolves timezone configuration [api/src/services/cdp/utils/validation.ts:72-105]().
7. **Chrome Arguments** - Builds comprehensive Chrome launch arguments [api/src/services/cdp/cdp.service.ts:774-854]().
8. **User Preferences** - Sets up Chrome user preferences [api/src/services/cdp/cdp.service.ts:875-882]().
9. **Browser Process Launch** - Launches browser via `puppeteer-core` [api/src/services/cdp/cdp.service.ts:885-896]().
10. **Event Handler Attachment** - Attaches browser event handlers [api/src/services/cdp/cdp.service.ts:912-977]().
11. **Target Instrumentation** - Instruments existing targets for logging [api/src/services/cdp/cdp.service.ts:1004-1016]().
12. **Plugin Notification** - Notifies plugins that browser is ready [api/src/services/cdp/plugins/core/plugin-manager.ts:107-118]().

**Sources:** [api/src/services/cdp/cdp.service.ts:516-1041](), [api/src/services/cdp/utils/error-handlers.ts:18-27]()

### Shutdown Process

```mermaid
sequenceDiagram
    participant Client
    participant CDPService
    participant PluginManager
    participant Browser
    participant FileService
    
    Client->>CDPService: shutdown()
    CDPService->>CDPService: Set shuttingDown = true
    
    CDPService->>PluginManager: onBrowserClose(browser)
    PluginManager-->>CDPService: Plugins notified
    
    CDPService->>PluginManager: onShutdown()
    PluginManager-->>CDPService: Shutdown complete
    
    CDPService->>CDPService: removeAllHandlers()
    
    CDPService->>Browser: close()
    CDPService->>Browser: process().kill()
    
    CDPService->>FileService: cleanupFiles()
    FileService-->>CDPService: Files cleaned
    
    CDPService->>CDPService: Reset state
    CDPService->>CDPService: emit('close')
    CDPService->>CDPService: Set shuttingDown = false
    
    CDPService-->>Client: Shutdown complete
```

**Sources:** [api/src/services/cdp/cdp.service.ts:454-503](), [api/src/services/cdp/plugins/core/plugin-manager.ts:137-146]()

---

## Configuration System

`CDPService` accepts comprehensive configuration through `BrowserLauncherOptions`, which controls all aspects of browser behavior.

### BrowserLauncherOptions Structure

The `BrowserLauncherOptions` type defines the parameters for launching a browser session, including headless mode, proxy settings, user agents, and ad-blocking preferences.

**Sources:** [api/src/types/index.js](), [api/src/services/cdp/cdp.service.ts:94-96]()

### Default Configuration

`CDPService` initializes with a default configuration that can be overridden:

```typescript
this.defaultLaunchConfig = {
  options: {
    headless: env.CHROME_HEADLESS,
    args: [],
    ignoreDefaultArgs: ["--enable-automation"],
  },
  blockAds: true,
  extensions: [],
  userDataDir: env.CHROME_USER_DATA_DIR || path.join(os.tmpdir(), "steel-chrome"),
  timezone: coldStartTimezone,
  userPreferences: {
    plugins: {
      always_open_pdf_externally: true,
      plugins_disabled: ["Chrome PDF Viewer"],
    },
  },
  deviceConfig: { device: "desktop" },
};
```

**Sources:** [api/src/services/cdp/cdp.service.ts:150-167]()

### Configuration Validation

Configuration is validated before browser launch using `validateLaunchConfig()`:

- **Dimensions validation**: Checks positive values and reasonable max size (7680x4320) [api/src/services/cdp/utils/validation.ts:33-48]().
- **Proxy URL validation**: Validates URL format [api/src/services/cdp/utils/validation.ts:51-62]().
- **Timezone validation**: Validates timezone with timeout mechanism [api/src/services/cdp/utils/validation.ts:72-105]().

**Sources:** [api/src/services/cdp/utils/validation.ts:31-105]()

### Configuration Reuse Optimization

`CDPService` implements intelligent configuration comparison to determine if an existing browser instance can be reused via `isSimilarConfig()`. It compares headless state, proxies, user agents, data directories, dimensions, and Chrome arguments.

**Sources:** [api/src/services/cdp/utils/validation.ts:114-189]()

---

## Fingerprinting and Stealth Features

`CDPService` implements comprehensive browser fingerprinting to make automated browsers appear as regular user browsers.

### Fingerprint Generation Process

```mermaid
sequenceDiagram
    participant Launch as launch()
    participant FPGen as FingerprintGenerator
    participant CDPService
    participant Page
    participant CDP as CDP Session
    
    Launch->>CDPService: Check fingerprint conditions
    
    alt Fingerprint not provided
        CDPService->>FPGen: Generate fingerprint
        Note over FPGen: Configure based on<br/>device type (desktop/mobile)
        FPGen-->>CDPService: BrowserFingerprintWithHeaders
    end
    
    Launch->>Page: Create/access page
    Launch->>CDPService: injectFingerprintSafely(page)
    
    CDPService->>Page: setUserAgent()
    CDPService->>CDP: createCDPSession()
    CDPService->>CDP: Page.setDeviceMetricsOverride()
    CDPService->>Page: setExtraHTTPHeaders()
    CDPService->>CDP: Emulation.setUserAgentOverride()
    CDPService->>Page: evaluateOnNewDocument(fingerprintScript)
    CDPService->>CDP: detach()
```

**Sources:** [api/src/services/cdp/cdp.service.ts:655-698](), [api/src/services/cdp/cdp.service.ts:1335-1428](), [api/src/scripts/index.ts:15-72]()

### Stealth Features

`CDPService` implements multiple stealth features:

| Feature | Implementation | Purpose |
|---------|---------------|---------|
| **Automation flag removal** | `--disable-blink-features=AutomationControlled` | Removes `navigator.webdriver` flag [api/src/services/cdp/cdp.service.ts:827]() |
| **Chrome args filtering** | Removes `--enable-automation` | Prevents detection via default args [api/src/services/cdp/cdp.service.ts:154]() |
| **Accept-language removal** | Deletes header in request handler | Prevents fingerprinting inconsistency [api/src/utils/browser.ts:148-165]() |
| **Fixed constants** | Injects `FIXED_*` values via script | Ensures consistent fingerprint [api/src/scripts/index.ts:51-71]() |

**Sources:** [api/src/services/cdp/cdp.service.ts:150-167](), [api/src/utils/browser.ts:148-165](), [api/src/scripts/index.ts:51-71]()

---

## Request Interception and Filtering

`CDPService` implements comprehensive request interception for ad blocking, bandwidth optimization, and resource filtering.

### Request Interception Flow

```mermaid
flowchart TD
    Request["HTTPRequest received"]
    RemoveLanguage["Remove accept-language header"]
    CheckAds["blockAds enabled?"]
    IsAd["isAdRequest()?"]
    CheckHost["Host blocked?"]
    CheckPattern["Pattern matched?"]
    CheckOptimize["optimizeBandwidth configured?"]
    CheckImages["Block images?"]
    CheckMedia["Block media?"]
    CheckStylesheets["Block stylesheets?"]
    CheckFileProtocol["File protocol?"]
    Continue["request.continue()"]
    Abort["request.abort()"]
    CloseShutdown["page.close() + shutdown()"]
    
    Request --> RemoveLanguage
    RemoveLanguage --> CheckAds
    CheckAds -->|Yes| IsAd
    CheckAds -->|No| CheckHost
    IsAd -->|Yes| Abort
    IsAd -->|No| CheckHost
    CheckHost -->|Yes| Abort
    CheckHost -->|No| CheckPattern
    CheckPattern -->|Yes| Abort
    CheckPattern -->|No| CheckOptimize
    CheckOptimize -->|Yes| CheckImages
    CheckOptimize -->|No| CheckFileProtocol
    CheckImages -->|Match| Abort
    CheckImages -->|No match| CheckMedia
    CheckMedia -->|Match| Abort
    CheckMedia -->|No match| CheckStylesheets
    CheckStylesheets -->|Match| Abort
    CheckStylesheets -->|No match| CheckFileProtocol
    CheckFileProtocol -->|Yes| CloseShutdown
    CheckFileProtocol -->|No| Continue
```

**Sources:** [api/src/services/cdp/cdp.service.ts:385-439](), [api/src/utils/requests.ts:32-38]()

---

## Plugin System Integration

`CDPService` integrates with the plugin system via `PluginManager`, enabling extensibility through lifecycle hooks defined in `BasePlugin`.

### Plugin Hook Methods

| Hook | When Called | Purpose |
|------|-------------|---------|
| `onSessionStart` | Before launch/reuse | Initialize session state [api/src/services/cdp/plugins/core/base-plugin.ts:43]() |
| `onBrowserLaunch` | After browser process starts | Initialize browser features [api/src/services/cdp/plugins/core/base-plugin.ts:46]() |
| `onBrowserReady` | After all setup complete | Final browser configuration [api/src/services/cdp/plugins/core/base-plugin.ts:47]() |
| `onPageCreated` | When new page/target created | Initialize page features [api/src/services/cdp/plugins/core/base-plugin.ts:48]() |
| `onShutdown` | During `CDPService` shutdown | Final cleanup based on `ShutdownReason` [api/src/services/cdp/plugins/core/base-plugin.ts:53]() |

**Sources:** [api/src/services/cdp/plugins/core/base-plugin.ts:42-55](), [api/src/services/cdp/plugins/core/plugin-manager.ts:54-216]()

---

## Error Handling and Retry Mechanism

`CDPService` implements sophisticated error handling with categorization and retry logic via `RetryManager`.

### Error Categories

| Error Class | Retryable | Purpose |
|-------------|-----------|---------|
| `BrowserProcessError` | Yes | Browser process launch/management failures [api/src/services/cdp/errors/launch-errors.ts:267]() |
| `NetworkError` | Yes | Network-related failures (proxy, WebSocket) [api/src/services/cdp/errors/launch-errors.ts:188]() |
| `ConfigurationError` | No | Invalid configuration parameters [api/src/services/cdp/errors/launch-errors.ts:124]() |
| `LaunchTimeoutError` | Yes | Launch timeout (default 30s) [api/src/services/cdp/errors/launch-errors.ts:106]() |

**Sources:** [api/src/services/cdp/errors/launch-errors.ts:77-285](), [api/src/services/cdp/utils/error-handlers.ts:18-87]()

### Error Handling Utilities

`CDPService` uses functional wrappers to handle different levels of criticality:

1.  **`executeCritical`**: Operation must succeed or launch fails [api/src/services/cdp/utils/error-handlers.ts:18]().
2.  **`executeOptional`**: Logs a warning but continues execution on failure [api/src/services/cdp/utils/error-handlers.ts:46]().
3.  **`executeBestEffort`**: Silently logs on failure [api/src/services/cdp/utils/error-handlers.ts:70]().

**Sources:** [api/src/services/cdp/utils/error-handlers.ts:1-87]()

---

# Page: SessionService

# SessionService

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [api/src/plugins/browser-session.ts](api/src/plugins/browser-session.ts)
- [api/src/services/context/chrome-context.service.ts](api/src/services/context/chrome-context.service.ts)
- [api/src/services/leveldb/sessionstorage.ts](api/src/services/leveldb/sessionstorage.ts)
- [api/src/services/session.service.ts](api/src/services/session.service.ts)
- [api/src/services/timezone-fetcher.service.ts](api/src/services/timezone-fetcher.service.ts)
- [api/src/types/fastify.d.ts](api/src/types/fastify.d.ts)
- [api/src/utils/context.ts](api/src/utils/context.ts)
- [api/src/utils/extensions.ts](api/src/utils/extensions.ts)

</details>



## Purpose and Scope

The **SessionService** is a core orchestration layer that manages the lifecycle of browser sessions in the steel-browser system. It coordinates between the `CDPService` (Chrome DevTools Protocol) and `SeleniumService` (WebDriver compatibility), handles proxy management, tracks session state, and integrates with supporting services for file management and timezone resolution.

For detailed information about browser control via CDP, see [CDPService](3.1). For file management within sessions, see [FileService](3.3). For session configuration options, see [Session Configuration](4.2).

**Sources:** [api/src/services/session.service.ts:1-301]()

---

## System Architecture

The following diagram shows how `SessionService` fits into the overall service architecture and its relationships with other core components:

```mermaid
graph TB
    subgraph "API Controllers"
        SessionController["sessions.controller.ts<br/>HTTP Request Handlers"]
    end
    
    subgraph "SessionService Layer"
        SS["SessionService<br/>Session Orchestration"]
        ActiveSession["activeSession<br/>Current Session State"]
        PastSessions["pastSessions[]<br/>Historical Sessions"]
        ProxyFactory["proxyFactory<br/>Proxy Creation"]
    end
    
    subgraph "Browser Control Services"
        CDPS["CDPService<br/>Chrome DevTools Protocol"]
        SELS["SeleniumService<br/>WebDriver Protocol"]
    end
    
    subgraph "Supporting Services"
        FS["FileService<br/>File Operations"]
        TZ["TimezoneFetcher<br/>Timezone Resolution"]
        PS["ProxyServer<br/>Proxy Instance"]
    end
    
    subgraph "Browser Process"
        Chrome["Chrome Browser<br/>Managed Process"]
    end
    
    SessionController -->|"startSession()<br/>endSession()"| SS
    
    SS -->|"manages"| ActiveSession
    SS -->|"archives"| PastSessions
    SS -->|"creates proxies via"| ProxyFactory
    
    SS -->|"launch()<br/>startNewSession()<br/>endSession()"| CDPS
    SS -->|"launch()<br/>close()"| SELS
    SS -->|"getTimezone()"| TZ
    SS -->|"getInstance()"| FS
    
    ProxyFactory -->|"instantiates"| PS
    
    CDPS -->|"controls"| Chrome
    SELS -->|"controls"| Chrome
    
    PS -->|"proxies traffic"| Chrome
```

**Sources:** [api/src/services/session.service.ts:50-300](), [api/src/plugins/browser-session.ts:5-13]()

---

## Core Components

### SessionService Class

The `SessionService` class is defined at [api/src/services/session.service.ts:58-301]() and contains the following key properties:

| Property | Type | Purpose |
|----------|------|---------|
| `cdpService` | `CDPService` | Primary browser control service using Chrome DevTools Protocol |
| `seleniumService` | `SeleniumService` | Alternative browser control for WebDriver compatibility |
| `fileService` | `FileService` | Manages file uploads, downloads, and cleanup |
| `timezoneFetcher` | `TimezoneFetcher` | Resolves timezone based on proxy location |
| `proxyFactory` | `ProxyFactory` | Factory function for creating proxy server instances |
| `activeSession` | `Session` | Current active session with state and completion promise |
| `pastSessions` | `Session[]` | Array of completed sessions for historical tracking |

**Sources:** [api/src/services/session.service.ts:59-67]()

### Session Type

The internal `Session` type extends `SessionDetails` with completion tracking and proxy management:

```typescript
type Session = SessionDetails & {
  completion: Promise<void>;
  complete: (value: void) => void;
  proxyServer: IProxyServer | undefined;
};
```

**Sources:** [api/src/services/session.service.ts:25-29]()

---

## Session Lifecycle Management

### Session Creation Flow

The following diagram illustrates the complete session creation process:

```mermaid
sequenceDiagram
    participant Controller as "sessions.controller"
    participant SS as "SessionService"
    participant TZ as "TimezoneFetcher"
    participant PF as "proxyFactory"
    participant PS as "ProxyServer"
    participant CDPS as "CDPService"
    participant SELS as "SeleniumService"
    
    Controller->>SS: startSession(options)
    
    SS->>TZ: getTimezone(proxyUrl, fallback)
    Note over TZ: Async timezone resolution<br/>starts immediately
    
    SS->>SS: resetSessionInfo(sessionData)
    Note over SS: Creates new session ID<br/>and completion promise
    
    alt proxyUrl provided
        SS->>PF: proxyFactory(proxyUrl)
        PF-->>SS: ProxyServer instance
        SS->>PS: listen()
        Note over PS: Proxy server starts
    end
    
    alt isSelenium mode
        SS->>CDPS: shutdown()
        SS->>SELS: launch(browserLauncherOptions)
    else CDP mode (default)
        SS->>CDPS: startNewSession(browserLauncherOptions)
    end
    
    SS-->>Controller: SessionDetails
```

**Sources:** [api/src/services/session.service.ts:93-243]()

### startSession Method

The `startSession` method at [api/src/services/session.service.ts:93-243]() orchestrates the following steps:

1. **Early Timezone Resolution**: Initiates timezone fetching as early as possible to avoid blocking ([lines 143-151]())
2. **Session Initialization**: Creates new session state via `resetSessionInfo` with provided or generated UUID ([lines 166-174]())
3. **User Data Directory Setup**: Creates persistent or temporary user data directory ([lines 176-180]())
4. **Proxy Configuration**: If `proxyUrl` is provided, creates and starts proxy server via `proxyFactory` ([lines 208-211]())
5. **User Preferences Merge**: Combines default and custom user preferences using `deepMerge` ([lines 182-191]())
6. **Bandwidth Optimization**: Normalizes boolean/object configuration via `normalizeOptimizeBandwidth` ([lines 194-206]())
7. **Browser Launch**: Launches either Selenium or CDP-based browser ([lines 212-241]())

**Sources:** [api/src/services/session.service.ts:93-243]()

### Configuration Processing

The method processes configuration in the following order:

| Configuration Stage | Processing | Lines |
|-------------------|-----------|-------|
| Dimensions | Uses provided or falls back to `cdpService.getDimensions()` | [157-164]() |
| Timezone | Async resolution via `TimezoneFetcher` or direct value | [143-151]() |
| User Data Dir | Creates from `userDataDir`, `persist` flag, or default temp dir | [176-180]() |
| User Preferences | Deep merges with PDF viewer defaults | [182-191]() |
| Optimize Bandwidth | Normalizes boolean to full object structure | [194-206]() |
| Browser Launcher Options | Assembles complete `BrowserLauncherOptions` object | [213-233]() |

**Sources:** [api/src/services/session.service.ts:93-243]()

---

## Session State Tracking

### Active Session Management

The `activeSession` property tracks the current session state. It is initialized in the constructor at [api/src/services/session.service.ts:80-90]() with default values:

```typescript
this.activeSession = {
  id: uuidv4(),
  createdAt: new Date().toISOString(),
  ...defaultSession,
  ...sessionStats,
  userAgent: this.cdpService.getUserAgent() ?? "",
  dimensions: this.cdpService.getDimensions(),
  completion: Promise.resolve(),
  complete: () => {},
  proxyServer: undefined,
};
```

The session structure includes:

| Field Group | Fields | Purpose |
|------------|--------|---------|
| Identity | `id`, `createdAt` | Unique identification and timestamp |
| URLs | `websocketUrl`, `debugUrl`, `debuggerUrl`, `sessionViewerUrl` | Access endpoints for session monitoring |
| Browser Config | `userAgent`, `dimensions`, `isSelenium` | Browser configuration state |
| Proxy | `proxy`, `proxyServer`, `proxyTxBytes`, `proxyRxBytes` | Proxy configuration and traffic metrics |
| Stats | `duration`, `eventCount`, `timeout`, `creditsUsed` | Usage and performance metrics |
| Lifecycle | `status`, `completion`, `complete` | Session state and completion handling |

**Sources:** [api/src/services/session.service.ts:40-51](), [api/src/services/session.service.ts:80-90]()

---

## Session Termination

### endSession Method

The `endSession` method at [api/src/services/session.service.ts:245-273]() performs cleanup and state transitions:

```mermaid
graph TD
    Start["endSession() called"]
    Complete["activeSession.complete()"]
    UpdateStatus["Set status = 'released'"]
    CalcDuration["Calculate session duration"]
    ProxyStats["Record proxy traffic stats"]
    CheckMode{"isSelenium?"}
    CloseSelenium["seleniumService.close()"]
    LaunchCDP["cdpService.launch()"]
    EndCDP["cdpService.endSession()"]
    Reset["resetSessionInfo()"]
    Archive["Add to pastSessions[]"]
    Return["Return released session"]
    
    Start --> Complete
    Complete --> UpdateStatus
    UpdateStatus --> CalcDuration
    CalcDuration --> ProxyStats
    ProxyStats --> CheckMode
    CheckMode -->|Yes| CloseSelenium
    CloseSelenium --> LaunchCDP
    CheckMode -->|No| EndCDP
    LaunchCDP --> Reset
    EndCDP --> Reset
    Reset --> Archive
    Archive --> Return
```

**Sources:** [api/src/services/session.service.ts:245-273]()

### Cleanup Operations

The termination process performs the following operations:

1. **Completion Signal**: Resolves the session's completion promise ([line 246]())
2. **Status Update**: Changes status to `"released"` ([line 247]())
3. **Duration Calculation**: Computes total session time ([lines 248-249]())
4. **Proxy Statistics**: Records transmitted and received bytes from `proxyServer` ([lines 251-254]())
5. **Browser Shutdown**: Closes `SeleniumService` or ends `CDPService` session ([lines 256-261]())
6. **Session Reset**: Creates new idle session state via `resetSessionInfo` ([lines 265-268]())
7. **Archival**: Stores completed session in `pastSessions` array ([line 270]())

**Sources:** [api/src/services/session.service.ts:245-273]()

---

## Proxy Management

### ProxyFactory Pattern

`SessionService` uses a factory pattern for proxy creation, allowing custom proxy implementations:

```mermaid
graph LR
    subgraph "Proxy Factory Pattern"
        PF["proxyFactory: ProxyFactory"]
        DefaultImpl["Default: (url) => new ProxyServer(url)"]
        CustomImpl["Custom: User-provided factory"]
    end
    
    subgraph "Proxy Lifecycle"
        Create["Create proxy instance"]
        Listen["Start listening"]
        Track["Track tx/rx bytes"]
        Close["Close on session end"]
    end
    
    PF -->|default| DefaultImpl
    PF -->|via setProxyFactory| CustomImpl
    
    DefaultImpl --> Create
    CustomImpl --> Create
    Create --> Listen
    Listen --> Track
    Track --> Close
```

**Sources:** [api/src/services/session.service.ts:53-56](), [api/src/services/session.service.ts:297-299]()

### Proxy Integration

The proxy integration occurs at [api/src/services/session.service.ts:208-211]():

```typescript
if (proxyUrl) {
  this.activeSession.proxyServer = await this.proxyFactory(proxyUrl, normalizedOptimize);
  await this.activeSession.proxyServer.listen();
}
```

The proxy server is passed to the browser launcher at [api/src/services/session.service.ts:216]():

```typescript
proxyUrl: this.activeSession.proxyServer?.url,
```

**Sources:** [api/src/services/session.service.ts:208-211](), [api/src/services/session.service.ts:216]()

---

## Service Orchestration

### CDP vs Selenium Mode

`SessionService` supports two browser control modes with different capabilities:

```mermaid
graph TB
    subgraph "Mode Selection"
        StartSession["startSession(options)"]
        CheckMode{"isSelenium<br/>flag?"}
    end
    
    subgraph "Selenium Mode"
        ShutdownCDP["cdpService.shutdown()"]
        LaunchSelenium["seleniumService.launch()"]
        SeleniumConfig["Limited URLs:<br/>No websocket, debug, viewer"]
        SeleniumUA["Fallback user agent"]
    end
    
    subgraph "CDP Mode (Default)"
        StartCDP["cdpService.startNewSession()"]
        CDPConfig["Full URLs:<br/>websocket, debug, viewer"]
        CDPUA["Dynamic user agent<br/>from fingerprint"]
    end
    
    StartSession --> CheckMode
    CheckMode -->|true| ShutdownCDP
    CheckMode -->|false| StartCDP
    
    ShutdownCDP --> LaunchSelenium
    LaunchSelenium --> SeleniumConfig
    SeleniumConfig --> SeleniumUA
    
    StartCDP --> CDPConfig
    CDPConfig --> CDPUA
```

**Sources:** [api/src/services/session.service.ts:212-241]()

### Mode Switching on Termination

When ending a session, the service switches back to CDP mode if Selenium was active:

```typescript
if (this.activeSession.isSelenium) {
  this.seleniumService.close();
  await this.cdpService.launch();
} else {
  await this.cdpService.endSession();
}
```

This ensures the system returns to its default CDP state at [api/src/services/session.service.ts:256-261]().

**Sources:** [api/src/services/session.service.ts:256-261]()

---

## TimezoneFetcher Integration

`SessionService` uses `TimezoneFetcher` to resolve timezone based on proxy location. The resolution starts early in the session creation process:

```mermaid
sequenceDiagram
    participant SS as "SessionService"
    participant TZ as "TimezoneFetcher"
    participant CDPS as "CDPService"
    
    Note over SS: startSession() called
    
    alt timezone provided
        SS->>SS: timezonePromise = Promise.resolve(timezone)
    else no timezone
        SS->>TZ: getTimezone(proxyUrl, defaultTimezone)
        TZ-->>SS: timezonePromise (async)
    end
    
    Note over SS: Continue session setup...<br/>(proxy, dimensions, etc)
    
    SS->>SS: Construct BrowserLauncherOptions<br/>with timezonePromise
    
    SS->>CDPS: startNewSession(options)
    Note over CDPS: Awaits timezone resolution<br/>during launch
```

The timezone is fetched at [api/src/services/session.service.ts:143-151]() and included in browser options at [api/src/services/session.service.ts:228]().

**Sources:** [api/src/services/session.service.ts:79](), [api/src/services/session.service.ts:143-151](), [api/src/services/timezone-fetcher.service.ts:58-89]()

---

## State Reset Pattern

The `resetSessionInfo` method at [api/src/services/session.service.ts:275-295]() implements a clean state reset:

1. **Complete Previous Session**: Resolves the old completion promise ([line 276]())
2. **Close Proxy**: Cleanly shuts down `proxyServer` if active ([line 278]())
3. **Create New State**: Constructs fresh session with defaults and overrides ([lines 281-290]())
4. **Generate New Promise**: Creates new completion promise with resolvers ([lines 287-288]())

This ensures proper cleanup and fresh state for each session.

**Sources:** [api/src/services/session.service.ts:275-295]()

---

# Page: FileService

# FileService

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [api/src/modules/files/files.controller.ts](api/src/modules/files/files.controller.ts)
- [api/src/modules/files/files.routes.ts](api/src/modules/files/files.routes.ts)
- [api/src/modules/files/files.schema.ts](api/src/modules/files/files.schema.ts)
- [api/src/plugins/file-storage.ts](api/src/plugins/file-storage.ts)
- [api/src/services/file.service.ts](api/src/services/file.service.ts)

</details>



## Purpose and Scope

The `FileService` provides centralized file management capabilities for browser sessions in steel-browser. It handles file upload, download, listing, deletion, and automatic archive generation with real-time file system watching. This service operates as a singleton instance that manages a shared file storage directory and maintains prebuilt ZIP archives of all session files.

For information about the File API endpoints and HTTP routes, see [File API](#7.1). For details on automatic archive generation and bulk download, see [Archive Management](#7.2).

---

## Architecture Overview

The `FileService` is a singleton service that manages all file operations and integrates with the HTTP API layer through the `FilesController`.

```mermaid
graph TB
    subgraph "HTTP Layer"
        Routes["files.routes.ts<br/>File API Endpoints"]
        Controller["FilesController<br/>Request Handling"]
    end
    
    subgraph "Service Layer"
        FileService["FileService<br/>Singleton Instance"]
        getInstance["getInstance()"]
    end
    
    subgraph "File System"
        BaseDir["/files or /tmp/files<br/>baseFilesPath"]
        ArchiveDir["/tmp/.steel<br/>prebuiltArchiveDir"]
        Archive["files.zip<br/>prebuiltArchivePath"]
    end
    
    subgraph "File Watching"
        Chokidar["chokidar.FSWatcher<br/>File System Monitor"]
        Debounce["debouncedCreateArchive<br/>500ms debounce"]
    end
    
    subgraph "Archive Creation"
        Archiver["archiver<br/>ZIP Compression"]
        TempArchive["files-{timestamp}.zip.tmp"]
    end
    
    Routes --> Controller
    Controller --> FileService
    FileService --> getInstance
    
    FileService --> BaseDir
    FileService --> ArchiveDir
    
    FileService --> Chokidar
    Chokidar -->|"file change events"| Debounce
    Debounce --> Archiver
    
    Archiver --> TempArchive
    TempArchive -->|"atomic rename"| Archive
```

**Sources:** [api/src/services/file.service.ts:16-38](), [api/src/modules/files/files.controller.ts:17-18](), [api/src/modules/files/files.routes.ts:8-16]()

---

## Singleton Pattern

The `FileService` implements the singleton pattern to ensure only one instance manages the file storage system across the application lifecycle.

```mermaid
graph LR
    Plugin["file-storage.ts<br/>Fastify Plugin"]
    Controller["FilesController"]
    getInstance["FileService.getInstance()"]
    Instance["FileService<br/>Singleton Instance"]
    
    Plugin --> getInstance
    Controller --> getInstance
    getInstance --> Instance
```

The singleton is initialized lazily on first access and registered as a Fastify decorator:

| Method | Description |
|--------|-------------|
| `FileService.getInstance()` | Returns the singleton instance, creating it if it doesn't exist |
| `constructor()` (private) | Initializes storage paths, creates directories, and starts file watcher |

**Sources:** [api/src/services/file.service.ts:16-45](), [api/src/plugins/file-storage.ts:5-8]()

---

## File Storage Configuration

The `FileService` configures storage paths based on the runtime environment:

```mermaid
graph TB
    EnvCheck{"env.NODE_ENV"}
    ProdPath["/files<br/>Production Path"]
    DevPath["/tmp/files<br/>Development Path"]
    ArchivePath["/tmp/.steel<br/>Archive Directory"]
    
    EnvCheck -->|"production"| ProdPath
    EnvCheck -->|"development"| DevPath
    
    ProdPath --> BaseFiles["baseFilesPath"]
    DevPath --> BaseFiles
    
    ArchivePath --> PrebuiltDir["prebuiltArchiveDir"]
    PrebuiltDir --> ZipFile["files.zip<br/>prebuiltArchivePath"]
```

| Configuration | Development | Production |
|---------------|-------------|------------|
| `baseFilesPath` | `/tmp/files` | `/files` |
| `prebuiltArchiveDir` | `/tmp/.steel` | `/tmp/.steel` |
| `prebuiltArchivePath` | `/tmp/.steel/files.zip` | `/tmp/.steel/files.zip` |

All directories are created recursively during service initialization using `fs.mkdirSync()`.

**Sources:** [api/src/services/file.service.ts:27-32]()

---

## File Operations

### Save File

The `saveFile()` method stores files to the file system from a readable stream. It handles directory creation and ensures path safety before writing.

```mermaid
graph TB
    Input["saveFile({filePath, stream})"]
    Validate["getSafeFilePath()<br/>Path Validation"]
    CreateDir["mkdir -p<br/>Parent Directory"]
    Write["fs.promises.writeFile()"]
    Stat["fs.promises.stat()"]
    Trigger["debouncedCreateArchive()"]
    Cleanup["Error: unlink file"]
    
    Input --> Validate
    Validate --> CreateDir
    CreateDir --> Write
    Write --> Stat
    Stat --> Trigger
    Stat -->|success| Return["Return File Metadata"]
    Write -->|error| Cleanup
    Cleanup --> Error["Throw Error"]
```

The method returns file metadata on success:

```typescript
{
  path: string;          // Absolute file path
  size: number;          // File size in bytes
  lastModified: Date;    // Modification timestamp
}
```

**Sources:** [api/src/services/file.service.ts:110-148]()

### Download File

The `downloadFile()` method retrieves files as readable streams. It verifies that the requested path exists and is a file before opening a read stream.

```mermaid
graph TB
    Input["downloadFile({filePath})"]
    Validate["getSafeFilePath()"]
    Stat["fs.promises.stat()"]
    CheckFile{"isFile()?"}
    Stream["fs.createReadStream()"]
    Return["Return {stream, size, lastModified}"]
    NotFound["Throw: File not found"]
    
    Input --> Validate
    Validate --> Stat
    Stat --> CheckFile
    CheckFile -->|yes| Stream
    CheckFile -->|no| NotFound
    Stream --> Return
    Stat -->|ENOENT| NotFound
```

**Sources:** [api/src/services/file.service.ts:150-179]()

### List Files

The `listFiles()` method recursively scans the base directory and returns all files sorted by modification time (descending).

```mermaid
graph TB
    Start["listFiles()"]
    Collect["collectFilesRecursively()"]
    ReadDir["fs.promises.readdir()"]
    Loop["For each entry"]
    CheckType{"Type?"}
    GetStats["fs.promises.stat()"]
    AddFile["allFiles.push()"]
    Recurse["collectFilesRecursively()"]
    Sort["Sort by lastModified DESC"]
    Return["Return Array"]
    
    Start --> Collect
    Collect --> ReadDir
    ReadDir --> Loop
    Loop --> CheckType
    CheckType -->|file| GetStats
    CheckType -->|directory| Recurse
    GetStats --> AddFile
    Recurse --> Loop
    AddFile --> Loop
    Loop -->|done| Sort
    Sort --> Return
```

**Sources:** [api/src/services/file.service.ts:204-250]()

### Delete File

The `deleteFile()` method removes individual files and triggers a background archive update.

```mermaid
graph TB
    Input["deleteFile({filePath})"]
    Validate["getSafeFilePath()"]
    Exists{"exists()?"}
    Stat["fs.promises.stat()"]
    IsFile{"isFile()?"}
    Unlink["fs.promises.unlink()"]
    Trigger["debouncedCreateArchive()"]
    Skip["Skip: Not Found"]
    
    Input --> Validate
    Validate --> Exists
    Exists -->|no| Skip
    Exists -->|yes| Stat
    Stat --> IsFile
    IsFile -->|yes| Unlink
    IsFile -->|no| Skip
    Unlink --> Trigger
```

**Sources:** [api/src/services/file.service.ts:252-278]()

---

## Path Security

The `FileService` implements path validation through the `getSafeFilePath()` method to prevent directory traversal attacks:

```mermaid
graph TB
    Input["relativePath"]
    Resolve["path.resolve(baseFilesPath, relativePath)"]
    Check{"Starts with<br/>baseFilesPath?"}
    Valid["Return Safe Path"]
    Invalid["Throw: Invalid path"]
    
    Input --> Resolve
    Resolve --> Check
    Check -->|yes| Valid
    Check -->|no| Invalid
```

Additionally, the `FilesController` performs validation on user-provided paths:

| Validation Rule | Check |
|----------------|-------|
| Absolute path | `path.isAbsolute()` → reject |
| Parent traversal | Contains `..` → reject |
| Null bytes | Contains `\0` → reject |
| Normalized path | Starts with `..` after normalization → reject |

**Sources:** [api/src/services/file.service.ts:88-97](), [api/src/modules/files/files.controller.ts:20-39]()

---

## Archive Management System

The `FileService` maintains a prebuilt ZIP archive of all files using automatic regeneration triggered by file system changes.

### Archive Creation Flow

```mermaid
graph TB
    FileChange["File System Change<br/>(add/delete/modify)"]
    Debounce["debouncedCreateArchive<br/>500ms debounce window"]
    CreateArchive["_createArchive()"]
    CheckLock{"isArchiving?"}
    SetLock["isArchiving = true"]
    TempFile["Create files-{timestamp}.zip.tmp"]
    Archiver["archiver.directory()"]
    Finalize["archiver.finalize()"]
    Close["output stream close event"]
    Rename["Atomic rename to files.zip"]
    UnsetLock["isArchiving = false"]
    
    FileChange --> Debounce
    Debounce --> CreateArchive
    CreateArchive --> CheckLock
    CheckLock -->|no| SetLock
    CheckLock -->|yes| Warn["Log Warning"]
    SetLock --> TempFile
    TempFile --> Archiver
    Archiver --> Finalize
    Finalize --> Close
    Close --> Rename
    Rename --> UnsetLock
```

### Archive Creation Configuration

| Setting | Value | Purpose |
|---------|-------|---------|
| `archiveDebounceTime` | 500ms | Minimum delay between archive rebuilds |
| Compression level | 9 (maximum) | Optimizes file size |
| Archive format | ZIP | Standard format for cross-platform compatibility |
| Atomic creation | Temp file + rename | Ensures archive is never partially written |

**Sources:** [api/src/services/file.service.ts:339-472]()

---

## File Watching System

The `FileService` uses `chokidar` to monitor the base files directory for changes:

```mermaid
graph TB
    Init["initFileWatcher()"]
    Create["chokidar.watch(baseFilesPath)"]
    
    Events["File System Events"]
    Add["add<br/>(file created)"]
    Unlink["unlink<br/>(file deleted)"]
    AddDir["addDir<br/>(directory created)"]
    UnlinkDir["unlinkDir<br/>(directory deleted)"]
    Error["error"]
    Ready["ready<br/>(initial scan complete)"]
    
    Handler["handleFileAdd/Delete/DirChange"]
    Trigger["debouncedCreateArchive()"]
    
    Init --> Create
    Create --> Events
    Events --> Add
    Events --> Unlink
    Events --> AddDir
    Events --> UnlinkDir
    Events --> Error
    Events --> Ready
    
    Add --> Handler
    Unlink --> Handler
    AddDir --> Handler
    UnlinkDir --> Handler
    
    Handler --> Trigger
    Ready --> Trigger
```

### Chokidar Configuration

```typescript
{
  ignored: /(^|[\/\\])\../,           // Ignore dotfiles
  persistent: true,                    // Keep process running
  ignoreInitial: false,                // Process existing files
  awaitWriteFinish: {
    stabilityThreshold: 500,           // Wait 500ms after last change
    pollInterval: 100                  // Check every 100ms
  },
  depth: undefined                     // Unlimited recursion depth
}
```

The `awaitWriteFinish` configuration ensures files are completely written before triggering archive regeneration, preventing corruption from partial writes.

**Sources:** [api/src/services/file.service.ts:62-86]()

---

## Integration with HTTP API

The `FileService` is consumed by the `FilesController`, which translates HTTP requests into service method calls.

### File Upload Processing

The `FilesController.handleFileUpload()` supports two upload methods:

| Method | Field Name | Processing |
|--------|------------|------------|
| Multipart file upload | `file` (binary) | Stream to disk → `saveFile()` |
| URL download | `file` (string URL) | HTTP GET via `createStreamFromUrl()` → `saveFile()` |

Both methods support an optional `path` field to specify the storage location. If omitted for binary uploads, a random UUID is generated as the filename. For URLs, the filename is extracted from the URL or headers.

**Sources:** [api/src/modules/files/files.controller.ts:41-157](), [api/src/modules/files/files.controller.ts:159-191]()

### Archive Download Behavior

The `handleDownloadArchive()` method serves the prebuilt archive if available. If the prebuilt archive doesn't exist (e.g., immediately after startup), an empty archive is generated on-the-fly.

**Sources:** [api/src/modules/files/files.controller.ts:291-335]()

---

## Configuration and Limits

File upload limits are configured through the Fastify multipart plugin during route registration.

```typescript
{
  limits: {
    fileSize: server.steelBrowserConfig.fileStorage?.maxSizePerSession ?? 100 * MB
  }
}
```

| Configuration | Default Value | Description |
|--------------|---------------|-------------|
| `maxSizePerSession` | 100 MB | Maximum total size for uploaded files per session |

**Sources:** [api/src/modules/files/files.routes.ts:11-16]()

---

## Error Handling

The `FileService` implements comprehensive error handling across all operations:

| Operation | Error Condition | Behavior |
|-----------|----------------|----------|
| `saveFile()` | Write failure | Delete partial file, throw error |
| `downloadFile()` | File not found (ENOENT) | Throw "File not found" |
| `downloadFile()` | Not a file | Throw "Path is not a file" |
| `deleteFile()` | File not found | Log and skip (no error) |
| `listFiles()` | Directory read error | Log error, continue with other directories |
| `_createArchive()` | Stream error | Delete temp archive, reject promise |

**Sources:** [api/src/services/file.service.ts:133-147](), [api/src/services/file.service.ts:172-178](), [api/src/services/file.service.ts:252-278]()

---

# Page: Browser Sessions

# Browser Sessions

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [api/src/modules/sessions/sessions.controller.ts](api/src/modules/sessions/sessions.controller.ts)
- [api/src/modules/sessions/sessions.schema.ts](api/src/modules/sessions/sessions.schema.ts)
- [api/src/services/session.service.ts](api/src/services/session.service.ts)

</details>



This page documents the browser session system in Steel Browser, which is the core mechanism for creating, managing, and interacting with browser instances. Browser sessions enable stateful browsing experiences with persistence of cookies, local storage, and other browser state.

For detailed documentation on specific session topics, see the following child pages:
- [Session Management API](#4.1) — Document session lifecycle endpoints: create, list, retrieve, release, and configuration options.
- [Session Configuration](#4.2) — Detailed reference for `BrowserLauncherOptions` and session configuration parameters.
- [Session Storage & State](#4.3) — Explain session context: cookies, `localStorage`, `sessionStorage`, `indexedDB` persistence.
- [Live Session Monitoring](#4.4) — Document live session details, streaming, and debugging capabilities.

## Session Overview

A browser session in Steel represents a fully-functioning browser instance with its own isolated state, configuration, and lifecycle. Sessions provide a consistent way to manage browser instances, their proxy configurations, and browser state across operations.

```mermaid
graph TB
    Client["Client"] --> |"Creates via handleLaunchBrowserSession"| Session["Session (SessionDetails)"]
    Session --> |"Contains"| Browser["Browser Instance (CDPService)"]
    Session --> |"Contains"| State["SessionContext"]
    Session --> |"Can use"| Proxy["IProxyServer"]
    
    subgraph "Browser Instance Space"
        CDP["CDPService"]
        Selenium["SeleniumService"]
        Extensions["Browser Extensions"]
    end
    
    subgraph "Code Entity: SessionContext"
        Cookies["CookieData[]"]
        LocalStorage["Record<string, Record<string, any>>"]
        UserAgent["userAgent: string"]
    end
    
    subgraph "Code Entity: ProxyServer"
        ProxyURL["proxyUrl: string"]
        ProxyStats["proxyTxBytes / proxyRxBytes"]
    end
    
    State --- Cookies
    State --- LocalStorage
    State --- UserAgent
    
    Browser --- CDP
    Browser --- Selenium
    Browser --- Extensions
    
    Proxy --- ProxyURL
    Proxy --- ProxyStats
```

Sources: [api/src/services/session.service.ts:25-29](), [api/src/modules/sessions/sessions.schema.ts:93-127](), [api/src/services/session.service.ts:93-119]()

## Session Lifecycle

Browser sessions follow a specific lifecycle managed by the `SessionService`. The service maintains an `activeSession` and a history of `pastSessions`. For details on managing this lifecycle via API, see [Session Management API](#4.1).

```mermaid
stateDiagram-v2
    [*] --> "idle" : SessionService Constructor
    "idle" --> "live" : startSession()
    "live" --> "live" : CDP/Selenium Interactions
    "live" --> "released" : endSession()
    "live" --> "failed" : Exception in startSession/CDP
    "released" --> "idle" : resetSessionInfo()
    "failed" --> "idle" : resetSessionInfo()
    
    note right of "idle"
      defaultSession values applied
    end note
    
    note right of "live"
      Browser process running
      ProxyServer.listen() active
    end note
    
    note right of "released"
      Session pushed to pastSessions[]
      Cleanup via fileService.cleanupFiles()
    end note
```

Sources: [api/src/services/session.service.ts:40-51](), [api/src/services/session.service.ts:66-67](), [api/src/services/session.service.ts:166-174](), [api/src/services/session.service.ts:286-308]()

## Session Configuration

When creating a new browser session, you can configure various aspects of the browser's behavior, including anti-detection features, proxy settings, and viewport dimensions. For a full reference of available options, see [Session Configuration](#4.2).

| Property | Description | Code Entity |
|----------|-------------|-------------|
| `proxyUrl` | Upstream proxy to route traffic through | `CreateSession.proxyUrl` |
| `userAgent` | Custom string or generated via fingerprint | `CreateSession.userAgent` |
| `dimensions` | Viewport width and height | `CreateSession.dimensions` |
| `isSelenium` | Toggle between CDP and Selenium modes | `CreateSession.isSelenium` |
| `optimizeBandwidth` | Block images/media to save data | `OptimizeBandwidthOptions` |
| `deviceConfig` | Emulate "desktop" or "mobile" | `deviceConfigSchema` |

Sources: [api/src/modules/sessions/sessions.schema.ts:28-91](), [api/src/services/session.service.ts:194-204]()

## Session Storage & Persistence

Steel Browser can preserve and restore browser state including cookies and `localStorage`. This is critical for automation that requires login persistence. For details on how state is handled, see [Session Storage & State](#4.3).

```mermaid
graph TD
    subgraph "Natural Language: State Persistence"
        Input["Client SessionContext"]
        Storage["User Data Directory"]
        Output["Extracted Browser State"]
    end

    subgraph "Code Entity Space"
        SessionContextSchema["SessionContextSchema"]
        UserDataDir["userDataDir (path.join)"]
        GetBrowserState["CDPService.getBrowserState()"]
    end

    Input --> SessionContextSchema
    SessionContextSchema --> |"Injected into"| UserDataDir
    UserDataDir --> |"Used by"| CDPService["CDPService.startNewSession()"]
    CDPService --> |"Captured by"| GetBrowserState
    GetBrowserState --> Output
```

Sources: [api/src/modules/sessions/sessions.schema.ts:32-34](), [api/src/services/session.service.ts:176-180](), [api/src/modules/sessions/sessions.controller.ts:82-89]()

## Live Session Monitoring

Active sessions can be monitored in real-time through the UI Dashboard or via direct API calls to retrieve page lists and screenshots. For information on the streaming architecture and debugging tools, see [Live Session Monitoring](#4.4).

The `SessionService` provides metadata for these tools:
- `websocketUrl`: For real-time event streaming. [api/src/services/session.service.ts:42]()
- `debugUrl`: For viewing the live browser instance. [api/src/services/session.service.ts:43]()
- `sessionViewerUrl`: For the dashboard interface. [api/src/services/session.service.ts:45]()

Sources: [api/src/modules/sessions/sessions.controller.ts:169-235](), [api/src/services/session.service.ts:80-91]()

## Session Management Implementation

The `SessionService` class acts as the orchestrator, coordinating between the `CDPService` (for browser control), `ProxyServer` (for networking), and `FileService` (for session artifacts).

```mermaid
classDiagram
    class SessionService {
        +activeSession: Session
        +pastSessions: Session[]
        +startSession(options) Promise
        +endSession() Promise
        -resetSessionInfo(overrides)
    }
    
    class CDPService {
        +startNewSession(options)
        +endSession()
        +getAllPages()
    }
    
    class ProxyServer {
        +url: string
        +listen()
        +close()
    }
    
    SessionService --> CDPService : "launches/stops browser"
    SessionService --> ProxyServer : "manages networking"
    SessionService --> FileService : "cleans up session files"
```

Sources: [api/src/services/session.service.ts:58-91](), [api/src/services/session.service.ts:208-211](), [api/src/services/session.service.ts:303-305]()

---

# Page: Session Management API

# Session Management API

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [api/src/modules/sessions/sessions.controller.ts](api/src/modules/sessions/sessions.controller.ts)
- [api/src/modules/sessions/sessions.routes.ts](api/src/modules/sessions/sessions.routes.ts)
- [api/src/modules/sessions/sessions.schema.ts](api/src/modules/sessions/sessions.schema.ts)
- [ui/src/steel-client/services.gen.ts](ui/src/steel-client/services.gen.ts)
- [ui/src/steel-client/types.gen.ts](ui/src/steel-client/types.gen.ts)

</details>



## Purpose and Scope

This document describes the HTTP REST API endpoints for managing browser session lifecycles in steel-browser. It covers creating sessions, querying session state, retrieving session details, and releasing sessions when complete.

For detailed information about session configuration options (e.g., proxy settings, fingerprinting, extensions), see [Session Configuration](#4.2). For information about session context persistence (cookies, localStorage, indexedDB), see [Session Storage & State](#4.3). For real-time session monitoring and WebSocket streaming, see [Live Session Monitoring](#4.4).

## Session Lifecycle Overview

Browser sessions in steel-browser follow a defined lifecycle with four possible states:

| Status | Description |
|--------|-------------|
| `idle` | Session created but not yet in use |
| `live` | Session actively running with browser instance |
| `released` | Session terminated and browser closed |
| `failed` | Session encountered an error and terminated |

**Session Lifecycle Flow**

```mermaid
stateDiagram-v2
    [*] --> idle: POST /v1/sessions
    idle --> live: Browser launch complete
    live --> live: Active automation
    live --> released: POST /v1/sessions/:id/release
    live --> failed: Error occurs
    released --> [*]
    failed --> [*]
```

**Sources:** [api/src/modules/sessions/sessions.schema.ts:93-96]()

## Core Endpoints

### Create Session

Creates a new browser session with specified configuration.

**Endpoint:** `POST /v1/sessions`

**Request Body:** `CreateSession` schema [api/src/modules/sessions/sessions.schema.ts:28-91]()

**Handler:** `handleLaunchBrowserSession` in [api/src/modules/sessions/sessions.controller.ts:8-65]()

**Response:** `SessionDetails` object [api/src/modules/sessions/sessions.schema.ts:93-127]()

```mermaid
graph LR
    Client["HTTP Client"] --> Route["POST /v1/sessions"]
    Route --> Handler["handleLaunchBrowserSession"]
    Handler --> SessionService["server.sessionService.startSession()"]
    SessionService --> CDPService["CDPService.launch()"]
    CDPService --> Browser["Chrome Browser"]
    Browser --> Response["SessionDetails"]
    Response --> Client
```

**Key Request Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `sessionId` | string (UUID) | Optional unique identifier for the session |
| `proxyUrl` | string | Proxy URL to route browser traffic through |
| `userAgent` | string | Custom user agent string |
| `sessionContext` | object | Initial cookies, localStorage, sessionStorage |
| `isSelenium` | boolean | Enable Selenium WebDriver compatibility mode |
| `blockAds` | boolean | Enable ad blocking |
| `optimizeBandwidth` | boolean \| object | Enable bandwidth optimizations |
| `skipFingerprintInjection` | boolean | Skip browser fingerprinting |
| `deviceConfig` | object | Device type configuration (desktop/mobile) |
| `extensions` | string[] | Chrome extension paths to load |
| `timezone` | string | IANA timezone string |
| `dimensions` | object | Browser viewport dimensions |
| `userPreferences` | object | Chrome user preferences |
| `headless` | boolean | Run browser in headless mode |

**Sources:** [api/src/modules/sessions/sessions.schema.ts:28-91](), [api/src/modules/sessions/sessions.routes.ts:41-57]()

### List Sessions

Retrieves all sessions (current and past).

**Endpoint:** `GET /v1/sessions`

**Handler:** `handleGetSessions` in [api/src/modules/sessions/sessions.controller.ts:128-140]()

**Response:** `MultipleSessions` object containing array of `SessionDetails` [api/src/modules/sessions/sessions.schema.ts:179-181]()

```typescript
{
  "sessions": [
    {
      "id": "uuid",
      "status": "live",
      "createdAt": "2024-01-01T00:00:00Z",
      "duration": 45000,
      ...
    }
  ]
}
```

The handler returns:
- Current active session (from `server.sessionService.activeSession`)
- Past sessions (from `server.sessionService.pastSessions`)

**Sources:** [api/src/modules/sessions/sessions.controller.ts:128-140](), [api/src/modules/sessions/sessions.routes.ts:59-74]()

### Get Session Details

Retrieves details for a specific session by ID.

**Endpoint:** `GET /v1/sessions/:sessionId`

**Handler:** `handleGetSessionDetails` in [api/src/modules/sessions/sessions.controller.ts:91-126]()

**Response:** `SessionDetails` object [api/src/modules/sessions/sessions.schema.ts:93-127]()

The handler checks if the requested session ID matches the active session. If not, it returns a stub response with `status: "released"`. For active sessions, it returns full details including calculated duration.

**Sources:** [api/src/modules/sessions/sessions.controller.ts:91-126](), [api/src/modules/sessions/sessions.routes.ts:76-91]()

### Get Browser Context

Retrieves current browser state including cookies and storage.

**Endpoint:** `GET /v1/sessions/:sessionId/context`

**Handler:** `handleGetBrowserContext` in [api/src/modules/sessions/sessions.controller.ts:82-89]()

**Response:** `SessionContextSchema` object containing:
- `cookies`: Array of cookie objects
- `localStorage`: Domain-keyed localStorage data
- `sessionStorage`: Domain-keyed sessionStorage data
- `indexedDB`: Domain-keyed indexedDB databases

**Sources:** [api/src/modules/sessions/sessions.controller.ts:82-89](), [api/src/modules/sessions/sessions.routes.ts:93-108]()

### Release Session

Terminates a browser session and releases resources.

**Endpoint:** `POST /v1/sessions/:sessionId/release`

**Alternative Endpoint:** `POST /v1/sessions/release` (releases current session without ID)

**Handler:** `handleExitBrowserSession` in [api/src/modules/sessions/sessions.controller.ts:67-80]()

**Response:** `ReleaseSession` object (extends `SessionDetails` with `success: boolean`) [api/src/modules/sessions/sessions.schema.ts:129-131]()

The handler calls `server.sessionService.endSession()` which closes the browser instance and moves the session to past sessions.

**Sources:** [api/src/modules/sessions/sessions.controller.ts:67-80](), [api/src/modules/sessions/sessions.routes.ts:110-142]()

## Session Details Schema

The `SessionDetails` object is returned by most session endpoints and contains comprehensive session information.

**SessionDetails Type Definition**

```mermaid
graph TD
    SessionDetails["SessionDetails"]
    SessionDetails --> Identity["Identity<br/>id: UUID<br/>createdAt: DateTime<br/>status: enum"]
    SessionDetails --> Metrics["Metrics<br/>duration: ms<br/>eventCount: number<br/>creditsUsed: number"]
    SessionDetails --> Config["Configuration<br/>userAgent: string<br/>proxy: string<br/>isSelenium: boolean<br/>dimensions: object"]
    SessionDetails --> URLs["Access URLs<br/>websocketUrl: string<br/>debugUrl: string<br/>debuggerUrl: string<br/>sessionViewerUrl: string"]
    SessionDetails --> ProxyStats["Proxy Statistics<br/>proxyTxBytes: number<br/>proxyRxBytes: number"]
```

**Required Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `id` | string (UUID) | Unique session identifier |
| `createdAt` | string (ISO 8601) | Session creation timestamp |
| `status` | enum | Current session status (idle/live/released/failed) |
| `duration` | integer | Session duration in milliseconds |
| `eventCount` | integer | Number of browser events captured |
| `timeout` | integer | Session timeout in milliseconds |
| `creditsUsed` | integer | Credits consumed by session |
| `websocketUrl` | string | WebSocket endpoint for real-time events |
| `debugUrl` | string | URL for live browser view |
| `debuggerUrl` | string | Chrome DevTools inspector URL |
| `sessionViewerUrl` | string | Session viewer dashboard URL |
| `proxyTxBytes` | integer | Bytes transmitted through proxy |
| `proxyRxBytes` | integer | Bytes received through proxy |

**Sources:** [api/src/modules/sessions/sessions.schema.ts:93-127](), [ui/src/steel-client/types.gen.ts:286-363]()

## Live Session Monitoring

### Get Live Session Details

Retrieves real-time information about the active session including all open pages/tabs.

**Endpoint:** `GET /v1/sessions/:id/live-details`

**Handler:** `handleGetSessionLiveDetails` in [api/src/modules/sessions/sessions.controller.ts:169-243]()

**Response:** `SessionLiveDetailsResponse` object [api/src/modules/sessions/sessions.schema.ts:153-175]()

The handler:
1. Calls `server.cdpService.getAllPages()` to get all browser pages [api/src/modules/sessions/sessions.controller.ts:175]()
2. For each page, extracts URL, title, and favicon [api/src/modules/sessions/sessions.controller.ts:178-212]()
3. Retrieves browser state from `server.cdpService.getBrowserState()` [api/src/modules/sessions/sessions.controller.ts:216]()
4. Returns combined session and page information [api/src/modules/sessions/sessions.controller.ts:229-235]()

**Sources:** [api/src/modules/sessions/sessions.controller.ts:169-243](), [api/src/modules/sessions/sessions.routes.ts:184-201]()

### Get Session Debugger Stream

Returns an HTML page with embedded live browser view.

**Endpoint:** `GET /v1/sessions/debug`

**Handler:** `handleGetSessionStream` in [api/src/modules/sessions/sessions.controller.ts:142-167]()

**Response:** HTML content (`live-session-streamer.ejs`) with embedded WebSocket streaming [api/src/modules/sessions/sessions.controller.ts:159-166]()

**Sources:** [api/src/modules/sessions/sessions.controller.ts:142-167](), [api/src/modules/sessions/sessions.routes.ts:144-161]()

## Event Recording

### Receive Recorded Events

Accepts browser events recorded from client-side instrumentation.

**Endpoint:** `POST /v1/events`

**Request Body:** `RecordedEvents` schema [api/src/modules/sessions/sessions.schema.ts:133-135]()

**Handler Implementation:** [api/src/modules/sessions/sessions.routes.ts:174-181]()

The handler records events to the instrumentation logger via `server.cdpService.getInstrumentationLogger().record()`.

**Sources:** [api/src/modules/sessions/sessions.routes.ts:163-182](), [api/src/modules/sessions/sessions.schema.ts:133-135]()

## Request Flow Architecture

**End-to-End Request Processing**

```mermaid
graph TB
    Client["HTTP Client"] --> Fastify["Fastify Server"]
    Fastify --> RouteHandler["Route Handler<br/>sessions.routes.ts"]
    RouteHandler --> Controller["Controller<br/>sessions.controller.ts"]
    Controller --> SessionService["SessionService"]
    
    SessionService --> CDPService["CDPService"]
    
    CDPService --> Browser["Chrome Browser"]
    
    Browser --> Response["SessionDetails<br/>Response"]
    Response --> Client
```

**Route Registration:** Routes are registered in [api/src/modules/sessions/sessions.routes.ts:23-258]() using Fastify's route definition syntax with schema references via `$ref()`.

**Sources:** [api/src/modules/sessions/sessions.routes.ts:23-258](), [api/src/modules/sessions/sessions.controller.ts]()

## Session Actions Within Sessions

In addition to lifecycle management, sessions support quick actions like scraping and screenshots. These operate on the current active session.

| Endpoint | Purpose | Handler |
|----------|---------|---------|
| `POST /v1/sessions/scrape` | Scrape current page | `handleScrape` |
| `POST /v1/sessions/screenshot` | Capture screenshot | `handleScreenshot` |
| `POST /v1/sessions/pdf` | Generate PDF | `handlePDF` |

**Sources:** [api/src/modules/sessions/sessions.routes.ts:203-255]()

## Generated Client Usage

External clients use a type-safe generated client from the OpenAPI specification.

**Client Function Mapping:**

| API Endpoint | Generated Function | Location |
|--------------|-------------------|----------|
| `POST /v1/sessions` | `launchBrowserSession()` | [ui/src/steel-client/services.gen.ts:168-179]() |
| `GET /v1/sessions` | `getSessions()` | [ui/src/steel-client/services.gen.ts:186-197]() |
| `GET /v1/sessions/:id` | `getSessionDetails()` | [ui/src/steel-client/services.gen.ts:203-214]() |
| `GET /v1/sessions/:id/context` | `getBrowserContext()` | [ui/src/steel-client/services.gen.ts:221-232]() |
| `POST /v1/sessions/:id/release` | `releaseBrowserSession()` | [ui/src/steel-client/services.gen.ts:238-249]() |
| `POST /v1/sessions/release` | `releaseBrowserSessions()` | [ui/src/steel-client/services.gen.ts:256-267]() |

**Sources:** [ui/src/steel-client/services.gen.ts:168-267](), [ui/src/steel-client/types.gen.ts:74-284]()

## Error Handling

All session endpoints implement consistent error handling using `getErrors` utility [api/src/modules/sessions/sessions.controller.ts:62]().

The health check endpoint (`GET /v1/health`) returns 503 status when the browser service is not running:

```typescript
if (!server.cdpService.isRunning()) {
  return reply.status(503).send({ status: "service_unavailable" });
}
```

**Sources:** [api/src/modules/sessions/sessions.controller.ts:60-64](), [api/src/modules/sessions/sessions.routes.ts:35-37]()

---

# Page: Session Configuration

# Session Configuration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [api/src/modules/sessions/sessions.controller.ts](api/src/modules/sessions/sessions.controller.ts)
- [api/src/modules/sessions/sessions.schema.ts](api/src/modules/sessions/sessions.schema.ts)
- [api/src/services/session.service.ts](api/src/services/session.service.ts)
- [api/src/types/browser.ts](api/src/types/browser.ts)

</details>



This page provides a detailed reference for browser session configuration parameters. The configuration system controls browser launch options, anti-detection features, request filtering, session context persistence, and other automation behaviors.

For information about managing session lifecycles through API endpoints, see [Session Management API](4.1). For details on how session state is persisted and restored, see [Session Storage & State](4.3).

## Configuration Object Overview

Browser sessions are configured using the `BrowserLauncherOptions` interface defined in [api/src/types/browser.ts:28-58](). This interface serves as the primary configuration object passed to the `CDPService` when launching browser instances.

```mermaid
graph TB
    BLO["BrowserLauncherOptions"]
    BSO["BrowserServerOptions"]
    SC["sessionContext"]
    OB["OptimizeBandwidthOptions"]
    Fingerprint["BrowserFingerprintWithHeaders"]
    Credentials["CredentialsOptions"]
    
    BLO --> BSO
    BLO --> SC
    BLO --> OB
    BLO --> Fingerprint
    BLO --> Credentials
    
    BSO --> args["args: string[]"]
    BSO --> headless["headless: boolean"]
    BSO --> proxyUrl["proxyUrl: string"]
    BSO --> timeout["timeout: number"]
    BSO --> chromiumSandbox["chromiumSandbox: boolean"]
    
    SC --> cookies["cookies: CookieData[]"]
    SC --> localStorage["localStorage: Record[string, LocalStorageData]"]
    SC --> sessionStorage["sessionStorage: Record[string, SessionStorageData]"]
    SC --> indexedDB["indexedDB: Record[string, IndexedDBDatabase[]]"]
    
    OB --> blockImages["blockImages: boolean"]
    OB --> blockMedia["blockMedia: boolean"]
    OB --> blockStylesheets["blockStylesheets: boolean"]
    OB --> blockHosts["blockHosts: string[]"]
    OB --> blockUrlPatterns["blockUrlPatterns: string[]"]
    
    BLO --> stealth["stealth: boolean"]
    BLO --> userAgent["userAgent: string"]
    BLO --> blockAds["blockAds: boolean"]
    BLO --> customHeaders["customHeaders: Record[string, string]"]
    BLO --> timezone["timezone: Promise[string]"]
    BLO --> dimensions["dimensions: {width, height}"]
    BLO --> userDataDir["userDataDir: string"]
    BLO --> extensions["extensions: string[]"]
    BLO --> skipFingerprintInjection["skipFingerprintInjection: boolean"]
    BLO --> deviceConfig["deviceConfig: {device: 'desktop' | 'mobile'}"]
```

**Configuration Structure Diagram**: Shows the `BrowserLauncherOptions` interface and its nested configuration objects.

**Sources:** [api/src/types/browser.ts:28-58](), [api/src/modules/sessions/sessions.schema.ts:28-91]()

## Browser Server Options

The `BrowserServerOptions` interface [api/src/types/browser.ts:60-70]() controls low-level browser launch parameters.

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `headless` | `boolean` | `env.CHROME_HEADLESS` | Launch browser in headless mode [api/src/services/session.service.ts:215-215]() |
| `args` | `string[]` | `[]` | Chrome command-line arguments |
| `chromiumSandbox` | `boolean` | `false` | Enable Chromium sandbox |
| `devtools` | `boolean` | `false` | Auto-open DevTools |
| `proxyUrl` | `string` | `undefined` | Proxy server URL [api/src/services/session.service.ts:216-216]() |
| `timeout` | `number` | `30000` | Browser launch timeout |
| `downloadsPath` | `string` | `undefined` | Directory for downloads |

**Sources:** [api/src/types/browser.ts:60-70](), [api/src/services/session.service.ts:213-217]()

## Session Context Configuration

The `sessionContext` option [api/src/types/browser.ts:32-37]() restores browser state from a previous session. This is useful for maintaining logged-in states.

### Context Data Types

```mermaid
graph LR
    sessionContext["sessionContext"]
    
    sessionContext --> cookies["cookies: CookieData[]"]
    sessionContext --> localStorage["localStorage: Record[string, LocalStorageData]"]
    sessionContext --> sessionStorage["sessionStorage: Record[string, SessionStorageData]"]
    sessionContext --> indexedDB["indexedDB: Record[string, IndexedDBDatabase[]]"]
    
    cookies --> CookieData["CookieData"]
    localStorage --> LocalStorageData["LocalStorageData"]
    sessionStorage --> SessionStorageData["SessionStorageData"]
    indexedDB --> IndexedDBDatabase["IndexedDBDatabase"]
```

**Session Context Types Diagram**: Shows the structure of session context data used for state restoration.

**Sources:** [api/src/types/browser.ts:32-37](), [api/src/modules/sessions/sessions.schema.ts:32-34]()

## Anti-Detection Configuration

Steel-browser includes anti-detection capabilities controlled through several configuration options.

### Stealth and Fingerprinting

| Option | Type | Description |
|--------|------|-------------|
| `stealth` | `boolean` | Enable comprehensive anti-detection features [api/src/types/browser.ts:31]() |
| `skipFingerprintInjection` | `boolean` | Skip fingerprint script injection [api/src/modules/sessions/sessions.schema.ts:57-60]() |
| `userAgent` | `string` | Custom user agent string [api/src/modules/sessions/sessions.schema.ts:31-31]() |
| `deviceConfig` | `{device: "desktop" \| "mobile"}` | Device profile for fingerprint generation [api/src/modules/sessions/sessions.schema.ts:10-15]() |

### Fingerprint Injection Flow

```mermaid
graph TB
    Config["BrowserLauncherOptions"]
    SessionService["SessionService.startSession"]
    CDPService["CDPService"]
    
    Config --> SessionService
    SessionService -->|"skipFingerprintInjection check"| CDPService
    CDPService -->|"Inject Fingerprint"| Page["Browser Page"]
```

**Fingerprint Injection Flow**: Shows how fingerprint configuration flows from `BrowserLauncherOptions` through the services.

**Sources:** [api/src/services/session.service.ts:93-119](), [api/src/modules/sessions/sessions.schema.ts:57-60]()

## Request Filtering & Optimization

Steel-browser provides control over network requests to reduce bandwidth usage and block unwanted content.

### Ad Blocking

The `blockAds` option [api/src/modules/sessions/sessions.schema.ts:36-39]() enables filtering of common advertising and tracking domains.

### Bandwidth Optimization

The `optimizeBandwidth` option [api/src/modules/sessions/sessions.schema.ts:40-56]() accepts either a boolean or a detailed `OptimizeBandwidthOptions` object. If `true`, it enables blocking for images, media, and stylesheets [api/src/services/session.service.ts:197-199]().

```mermaid
graph TB
    optimizeBandwidth["optimizeBandwidth"]
    
    optimizeBandwidth --> booleanMode{Type}
    booleanMode -->|"true"| enableAll["Block: Images, Media, Stylesheets"]
    booleanMode -->|"object"| optionsMode["OptimizeBandwidthOptions"]
    
    optionsMode --> blockImages["blockImages: boolean"]
    optionsMode --> blockMedia["blockMedia: boolean"]
    optionsMode --> blockStylesheets["blockStylesheets: boolean"]
    optionsMode --> blockHosts["blockHosts: string[]"]
    optionsMode --> blockUrlPatterns["blockUrlPatterns: string[]"]
```

**Bandwidth Optimization Flow**: Maps configuration options to optimization behaviors.

**Sources:** [api/src/services/session.service.ts:194-206](), [api/src/types/browser.ts:11-17]()

## Browser Dimensions & Viewport

The `dimensions` option [api/src/modules/sessions/sessions.schema.ts:72-78]() controls the browser viewport size.

### Mobile Device Logic
If `deviceConfig.device` is set to `"mobile"`, the system enforces minimum dimensions of 508x1074 [api/src/services/session.service.ts:154-164]().

**Sources:** [api/src/services/session.service.ts:154-164](), [api/src/modules/sessions/sessions.schema.ts:72-78]()

## Timezone Configuration

The `timezone` option [api/src/modules/sessions/sessions.schema.ts:71-71]() allows setting a specific timezone for the session.

If not provided, the `SessionService` attempts to fetch the timezone based on the `proxyUrl` using the `TimezoneFetcher` [api/src/services/session.service.ts:143-151]().

**Sources:** [api/src/services/session.service.ts:143-151](), [api/src/services/timezone-fetcher.service.ts:1-80]()

## User Preferences & Extensions

### User Preferences
The `userPreferences` option [api/src/modules/sessions/sessions.schema.ts:79-84]() allows setting Chrome profile preferences. By default, Steel-browser disables the internal PDF viewer [api/src/services/session.service.ts:182-187]().

### Chrome Extensions
The `extensions` option [api/src/modules/sessions/sessions.schema.ts:68-68]() accepts an array of strings representing extensions to be loaded into the browser session.

**Sources:** [api/src/services/session.service.ts:182-191](), [api/src/modules/sessions/sessions.schema.ts:68-84]()

## Complete Configuration Reference Table

| Option | Type | Description |
|--------|------|-------------|
| `sessionId` | `string` | Unique identifier for the session [api/src/modules/sessions/sessions.schema.ts:29]() |
| `proxyUrl` | `string` | Proxy URL for the session [api/src/modules/sessions/sessions.schema.ts:30]() |
| `isSelenium` | `boolean` | Indicates if Selenium is used [api/src/modules/sessions/sessions.schema.ts:35]() |
| `persist` | `boolean` | Flag to indicate if session should be persisted [api/src/modules/sessions/sessions.schema.ts:69]() |
| `userDataDir` | `string` | User data directory path [api/src/modules/sessions/sessions.schema.ts:70]() |
| `headless` | `boolean` | Headless mode for the session [api/src/modules/sessions/sessions.schema.ts:90]() |
| `fullscreen` | `boolean` | Launch in fullscreen mode [api/src/modules/sessions/sessions.schema.ts:62-65]() |
| `credentials` | `CredentialsOptions` | Configuration for session credentials [api/src/modules/sessions/sessions.schema.ts:18-26]() |

**Sources:** [api/src/modules/sessions/sessions.schema.ts:28-91](), [api/src/types/browser.ts:28-58]()

---

# Page: Session Storage & State

# Session Storage & State

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [api/src/plugins/request-logger.ts](api/src/plugins/request-logger.ts)
- [api/src/services/cdp/cdp.service.ts](api/src/services/cdp/cdp.service.ts)
- [api/src/services/cdp/plugins/core/base-plugin.ts](api/src/services/cdp/plugins/core/base-plugin.ts)
- [api/src/services/cdp/plugins/core/plugin-manager.ts](api/src/services/cdp/plugins/core/plugin-manager.ts)
- [api/src/services/context/chrome-context.service.ts](api/src/services/context/chrome-context.service.ts)
- [api/src/services/context/types.ts](api/src/services/context/types.ts)
- [api/src/services/leveldb/localstorage.ts](api/src/services/leveldb/localstorage.ts)
- [api/src/services/leveldb/sessionstorage.ts](api/src/services/leveldb/sessionstorage.ts)
- [api/src/services/timezone-fetcher.service.ts](api/src/services/timezone-fetcher.service.ts)
- [api/src/utils/context.ts](api/src/utils/context.ts)
- [api/src/utils/extensions.ts](api/src/utils/extensions.ts)

</details>



This page documents how steel-browser captures, persists, and restores browser session state including cookies, localStorage, sessionStorage, and IndexedDB. Session context enables sessions to maintain state across browser restarts and allows state to be transferred between sessions.

---

## Overview

Session context in steel-browser encompasses all client-side state that defines a browser session:

| **Component** | **Description** | **Scope** |
|---------------|----------------|-----------|
| **Cookies** | HTTP cookies with domain, path, and expiration | Per-domain |
| **localStorage** | Persistent key-value storage | Per-origin |
| **sessionStorage** | Temporary key-value storage | Per-origin, per-tab |
| **IndexedDB** | Structured client-side database | Per-origin |

Session context is both **extracted** (when ending a session) and **injected** (when starting a session), enabling state persistence and multi-step automation workflows.

**Sources:** [api/src/services/context/types.ts:3-8](), [api/src/services/context/types.ts:58-63]()

---

## Session Context Data Structure

The `SessionData` type defines the structure for all session state, utilizing Zod for validation.

```typescript
export type SessionData = {
  [StorageProviderName.Cookies]?: CookieData[];
  [StorageProviderName.LocalStorage]?: Record<string, LocalStorageData>;
  [StorageProviderName.SessionStorage]?: Record<string, SessionStorageData>;
  [StorageProviderName.IndexedDB]?: Record<string, Array<IndexedDBDatabase>>;
};
```

### Cookie Data Structure
Cookies map to the `CDPCookieSchema`, aligning with the Chrome DevTools Protocol `Network.Cookie` type. Key fields include `name`, `value`, `domain`, `path`, `expires`, and `partitionKey` for partitioned cookies.

### Storage & IndexedDB Structure
`localStorage` and `sessionStorage` are mapped as `Record<string, Record<string, string>>`, where the first key is the origin/domain. `IndexedDB` is represented by `IndexedDBDatabase` objects containing `IndexedDBObjectStore` and `IndexedDBRecord` arrays.

**Sources:** [api/src/services/context/types.ts:58-63](), [api/src/services/context/types.ts:82-114](), [api/src/services/context/types.ts:17-33]()

---

## Session Context Lifecycle

The following diagram illustrates the interaction between core services during context injection and extraction.

**Diagram: Session Context Lifecycle Flow**

```mermaid
sequenceDiagram
    participant Client
    participant SessionService
    participant CDPService [CDPService]
    participant Browser [puppeteer-core]
    participant ChromeContextService [ChromeContextService]
    participant Reader [ChromeLocalStorageReader]

    Note over Client,Reader: Session Creation with Context
    Client->>SessionService: startSession(sessionContext)
    SessionService->>CDPService: launch(config)
    CDPService->>Browser: Launch with userDataDir
    CDPService->>CDPService: injectSessionContext(page, context)
    CDPService->>Browser: CDP: Network.setCookies
    
    Note over Client,Reader: Session Context Extraction
    Client->>SessionService: endSession()
    SessionService->>CDPService: getBrowserState()
    CDPService->>Browser: CDP: Network.getAllCookies
    CDPService->>CDPService: getExistingPageSessionData()
    CDPService->>ChromeContextService: getSessionData(userDataDir)
    ChromeContextService->>Reader: readLocalStorage(path)
    Reader-->>CDPService: Extracted LevelDB Data
    CDPService-->>SessionService: Merged SessionData
    SessionService-->>Client: Session Context JSON
```

**Sources:** [api/src/services/cdp/cdp.service.ts:126-133](), [api/src/services/context/chrome-context.service.ts:21-56](), [api/src/utils/context.ts:19-27]()

---

## Context Extraction Methods

`CDPService` combines live browser data with on-disk persistence for a complete state snapshot.

### 1. getBrowserState()
This method aggregates data from three distinct sources in parallel:
1.  **CDP Cookies**: Fetched via `Network.getAllCookies`.
2.  **Live Storage**: Extracted from active pages using `getExistingPageSessionData()`.
3.  **On-Disk Persistence**: Extracted from Chrome's LevelDB files via `ChromeContextService`.

**Sources:** [api/src/services/cdp/cdp.service.ts:1129-1175]()

### 2. getExistingPageSessionData() & extractStorageForPage()
The `extractStorageForPage` utility uses CDP to query `DOMStorage` and `IndexedDB` domains directly from the browser's memory for a specific page.

```mermaid
graph TB
    subgraph "extractStorageForPage Function"
        DOM["DOMStorage.getDOMStorageItems"]
        IDB_Names["IndexedDB.requestDatabaseNames"]
        IDB_Data["IndexedDB.requestData"]
    end

    Page["puppeteer.Page"] --> DOM
    Page --> IDB_Names
    IDB_Names --> IDB_Data
    
    DOM --> Result["SessionData"]
    IDB_Data --> Result
```

**Sources:** [api/src/utils/context.ts:19-185]()

### 3. ChromeContextService & LevelDB Readers
When a session ends, `ChromeContextService` reads the `userDataDir` to capture state that might not be tied to an open tab. It uses:
*   `ChromeLocalStorageReader`: Parses LevelDB files in the `Local Storage` directory.
*   `ChromeSessionStorageReader`: Parses LevelDB files in the `Session Storage` directory.

These readers handle the complexity of Chrome's binary encoding (UTF-16LE and Latin1) and LevelDB iterator logic.

**Sources:** [api/src/services/context/chrome-context.service.ts:61-97](), [api/src/services/leveldb/localstorage.ts:127-150](), [api/src/services/leveldb/sessionstorage.ts:204-229]()

---

## Context Injection

Injection occurs in two phases to ensure state is available before the page executes its own scripts.

### Phase 1: Immediate Cookie Injection
Cookies are injected via `Network.setCookies` immediately upon session start.

**Sources:** [api/src/services/cdp/cdp.service.ts:1297-1310]()

### Phase 2: Dynamic Storage Injection
`CDPService` registers a `framenavigated` listener. When a frame navigates to an origin that exists in the `SessionData`, the `handleFrameNavigated` utility injects the corresponding `localStorage` and `sessionStorage` items using `page.evaluate`.

```mermaid
graph LR
    CDP["CDPService"]
    Handler["handleFrameNavigated"]
    OriginMap["storageByOrigin (Map)"]
    Page["Page.evaluate"]

    CDP -- "on('framenavigated')" --> Handler
    Handler -- "Lookup" --> OriginMap
    OriginMap -- "Data Found" --> Page
```

**Sources:** [api/src/services/cdp/cdp.service.ts:1330-1371](), [api/src/utils/context.ts:188-212]()

---

## Persistence Strategies

The persistence of state depends on the session configuration:

1.  **Ephemeral (Default)**: If `userDataDir` is not provided, a temporary directory is used and typically cleaned up, making `SessionData` extraction vital for state reuse.
2.  **Persistent**: If `userDataDir` is specified in `BrowserLauncherOptions`, Chrome natively persists state to disk. `ChromeContextService` reads this directory to provide a portable `SessionData` object.
3.  **Context Transfer**: Users can manually fetch context from one session and provide it as `sessionContext` in the launch configuration of another session.

**Sources:** [api/src/services/cdp/cdp.service.ts:158-159](), [api/src/services/context/chrome-context.service.ts:21-30]()

---

## Summary Table: Storage Providers

| Provider | Reader Class | CDP Domain | Path in `userDataDir` |
| :--- | :--- | :--- | :--- |
| **Cookies** | N/A (CDP) | `Network` | `Default/Cookies` |
| **LocalStorage** | `ChromeLocalStorageReader` | `DOMStorage` | `Default/Local Storage/leveldb` |
| **SessionStorage** | `ChromeSessionStorageReader` | `DOMStorage` | `Default/Session Storage` |
| **IndexedDB** | N/A (CDP Only) | `IndexedDB` | `Default/IndexedDB` |

**Sources:** [api/src/services/context/chrome-context.service.ts:64-84](), [api/src/utils/context.ts:53-171]()

---

# Page: Live Session Monitoring

# Live Session Monitoring

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [api/src/modules/sessions/sessions.controller.ts](api/src/modules/sessions/sessions.controller.ts)
- [api/src/modules/sessions/sessions.schema.ts](api/src/modules/sessions/sessions.schema.ts)
- [api/src/plugins/browser-socket/casting.handler.ts](api/src/plugins/browser-socket/casting.handler.ts)
- [api/src/templates/live-session-streamer.ejs](api/src/templates/live-session-streamer.ejs)
- [api/src/types/casting.ts](api/src/types/casting.ts)
- [api/src/utils/casting.ts](api/src/utils/casting.ts)

</details>



This document covers the real-time monitoring and debugging capabilities for active browser sessions, including live page information retrieval, WebSocket streaming of browser events, and embedded browser viewing interfaces.

For information about session creation and lifecycle management, see [Session Management API](#4.1). For details on browser event logging and storage, see [Browser Instrumentation & Logging](#10.2). For WebSocket endpoint specifications, see [WebSocket API](#10.1).

---

## Overview

Live Session Monitoring provides real-time visibility into active browser sessions through HTTP endpoints and WebSocket streams. This functionality enables debugging, monitoring page state, viewing live browser output, and tracking session metrics as they occur.

**Key capabilities:**
- Retrieve information about all open pages/tabs in a session.
- Stream browser events and screencasts in real-time via WebSocket connections.
- Embed live browser views in external applications with interaction support.
- Monitor session state, duration, and resource usage.
- Access debugging interfaces for Chrome DevTools integration.

Sources: [api/src/modules/sessions/sessions.controller.ts:169-243](), [api/src/modules/sessions/sessions.schema.ts:148-170]()

---

## Live Session Monitoring Architecture

```mermaid
graph TB
    subgraph "Client Applications"
        HTTPClient["HTTP Client"]
        WSClient["WebSocket Client"]
        UIApp["UI Application"]
    end
    
    subgraph "API Endpoints"
        LiveDetailsEndpoint["GET /v1/sessions/:id/live-details<br/>handleGetSessionLiveDetails"]
        StreamEndpoint["GET /v1/sessions/:id/stream<br/>handleGetSessionStream"]
    end
    
    subgraph "WebSocket Handlers"
        LogsWS["WS /v1/sessions/logs<br/>logsHandler"]
        RecordingWS["WS /v1/sessions/recording<br/>recordingHandler"]
        PageIdWS["WS /v1/sessions/pageId<br/>pageIdHandler"]
        CastWS["WS /v1/sessions/cast<br/>handleCastSession"]
    end
    
    subgraph "Service Layer"
        SessionService["SessionService<br/>activeSession"]
        CDPService["CDPService<br/>getAllPages()<br/>getBrowserState()"]
    end
    
    subgraph "Browser Instance"
        ChromePages["Chrome Pages<br/>Puppeteer Page objects"]
        CDPEvents["CDP Events<br/>EmitEvent.Log<br/>EmitEvent.Recording"]
    end
    
    subgraph "Response Data"
        LiveDetailsResp["SessionLiveDetailsResponse<br/>pages[]<br/>browserState<br/>websocketUrl"]
        StreamHTML["live-session-streamer.ejs<br/>HTML with embedded viewer"]
    end
    
    HTTPClient -->|"GET with sessionId"| LiveDetailsEndpoint
    HTTPClient -->|"GET with query params"| StreamEndpoint
    WSClient -->|"Connect"| LogsWS
    WSClient -->|"Connect"| RecordingWS
    WSClient -->|"Connect"| PageIdWS
    WSClient -->|"Connect"| CastWS
    UIApp -->|"Embed"| StreamHTML
    
    LiveDetailsEndpoint --> SessionService
    LiveDetailsEndpoint --> CDPService
    StreamEndpoint --> SessionService
    
    CDPService --> ChromePages
    CDPService --> CDPEvents
    
    LogsWS --> CDPEvents
    RecordingWS --> CDPEvents
    PageIdWS --> CDPEvents
    CastWS --> ChromePages
    
    ChromePages -->|"title, url, favicon"| LiveDetailsResp
    SessionService -->|"status, dimensions"| LiveDetailsResp
    
    LiveDetailsEndpoint --> LiveDetailsResp
    StreamEndpoint --> StreamHTML
    
    LiveDetailsResp -->|"JSON"| HTTPClient
    StreamHTML -->|"HTML"| HTTPClient
```

**Diagram: Live Session Monitoring Data Flow**

This architecture shows how live session data flows from the browser through `CDPService` and specialized WebSocket handlers to client applications.

Sources: [api/src/modules/sessions/sessions.controller.ts:1-244](), [api/src/plugins/browser-socket/casting.handler.ts:18-53]()

---

## Live Details Endpoint

The live details endpoint provides comprehensive information about an active browser session, including all open pages, browser state, and URLs for real-time monitoring.

### Endpoint Specification

| Attribute | Value |
|-----------|-------|
| **Method** | GET |
| **Path** | `/v1/sessions/:id/live-details` |
| **Handler** | `handleGetSessionLiveDetails` |
| **Response** | `SessionLiveDetailsResponse` |
| **Purpose** | Retrieve current state of all pages and browser metadata |

### Response Schema

The `SessionLiveDetailsResponse` schema includes:

```typescript
{
  pages: Array<{
    id: string,           // Target ID from page.target()._targetId
    url: string,          // Current page URL
    title: string,        // Page title from page.title()
    favicon: string | null // Extracted favicon URL or null
  }>,
  browserState: {
    status: "idle" | "live" | "released" | "failed",
    userAgent: string,
    browserVersion: string,
    initialDimensions: { width: number, height: number },
    pageCount: number
  },
  websocketUrl: string,           // Base WebSocket URL for streaming
  sessionViewerUrl: string,       // URL to embedded viewer
  sessionViewerFullscreenUrl: string  // Viewer without controls
}
```

Sources: [api/src/modules/sessions/sessions.schema.ts:153-175]()

### Implementation Details

The `handleGetSessionLiveDetails` function performs the following operations:

1. **Page Enumeration** - Calls `server.cdpService.getAllPages()` to retrieve all Puppeteer `Page` objects [api/src/modules/sessions/sessions.controller.ts:175-175]().
2. **Page Information Extraction** - For each page:
   - Extracts target ID via `page.target()._targetId` [api/src/modules/sessions/sessions.controller.ts:180-180]().
   - Retrieves page title using `page.title()` [api/src/modules/sessions/sessions.controller.ts:182-182]().
   - Evaluates JavaScript in page context to extract favicon URL [api/src/modules/sessions/sessions.controller.ts:186-198]().
3. **Browser State Collection** - Retrieves browser version from `server.cdpService.getBrowserState()` [api/src/modules/sessions/sessions.controller.ts:216-216]().
4. **Session Data Assembly** - Combines page info with session metadata from `server.sessionService.activeSession` [api/src/modules/sessions/sessions.controller.ts:219-234]().

Sources: [api/src/modules/sessions/sessions.controller.ts:169-243]()

---

## Session Streaming Interface

The session streaming interface provides an embeddable HTML viewer for real-time browser interaction and observation.

### Endpoint Specification

| Attribute | Value |
|-----------|-------|
| **Method** | GET |
| **Path** | `/v1/sessions/:id/stream` |
| **Handler** | `handleGetSessionStream` |
| **Response** | HTML content (rendered from EJS template) |
| **Purpose** | Embed live browser view in external applications |

### Query Parameters

The `SessionStreamQuery` schema defines customization options:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `showControls` | boolean | `true` | Display browser navigation controls |
| `theme` | `"dark"` \| `"light"` | `"dark"` | UI theme for embedded viewer |
| `interactive` | boolean | `true` | Enable user interaction with browser |
| `pageId` | string | - | Connect to specific page by target ID |
| `pageIndex` | string | - | Connect to page by tab index |

Sources: [api/src/modules/sessions/sessions.schema.ts:137-151]()

### Single Page vs Multi-Page Mode

The streaming interface operates in two modes:

**Multi-Page Mode (default):**
- Displays all browser tabs/pages.
- Allows switching between pages.
- WebSocket URL: `ws://domain/v1/sessions/cast`.

**Single Page Mode:**
- Triggered when `pageId` or `pageIndex` is specified [api/src/modules/sessions/sessions.controller.ts:149-149]().
- Displays only the targeted page.
- WebSocket URL includes page identifier: `ws://domain/v1/sessions/cast?pageId=xxx` [api/src/modules/sessions/sessions.controller.ts:152-157]().

Sources: [api/src/modules/sessions/sessions.controller.ts:142-167]()

---

## WebSocket Streaming Channels

Live session monitoring utilizes multiple WebSocket channels for different types of real-time data streaming.

### Cast Channel (Interactive Screencasting)

**Path:** `/v1/sessions/:id/cast`  
**Handler:** `handleCastSession` [api/src/plugins/browser-socket/casting.handler.ts:18-18]()

The Cast Channel is the primary mechanism for real-time visual streaming and interaction. It uses Puppeteer's `CDPSession` to start a screencast and handles incoming user input events (mouse, keyboard, navigation).

**Key Features:**
- **Screencasting**: Uses `Page.startScreencast` to stream frames to the client [api/src/plugins/browser-socket/casting.handler.ts:76-81]().
- **Input Handling**: Translates client WebSocket messages into Puppeteer actions like `mouseEvent`, `keyEvent`, and `navigation` [api/src/types/casting.ts:1-36]().
- **Tab Discovery**: In multi-page mode, it tracks `targetcreated` and `targetdestroyed` events to notify the client of tab changes [api/src/plugins/browser-socket/casting.handler.ts:199-230]().

**Interaction Logic:**
When a `navigation` event is received, the `navigatePage` utility executes the requested action (back, forward, refresh, or goto) [api/src/utils/casting.ts:5-19]().

Sources: [api/src/plugins/browser-socket/casting.handler.ts:1-240](), [api/src/utils/casting.ts:5-19]()

### Other Streaming Channels

| Channel | Path | Purpose |
|---------|------|---------|
| **Logs** | `/v1/sessions/logs` | Streams browser console logs (Console, Network, etc.) |
| **Recording** | `/v1/sessions/recording` | Streams events for session replay/instrumentation |
| **Page ID** | `/v1/sessions/pageId` | Notifies when the active tab/target changes |

Sources: [api/src/plugins/browser-socket/browser-socket.ts:25-35]()

---

## Page Information Collection

The live details endpoint and the cast handler both need to resolve page metadata.

### Collection Logic Flow

```mermaid
sequenceDiagram
    participant Client as Client Application
    participant Controller as handleGetSessionLiveDetails
    participant CDP as CDPService
    participant Page as Puppeteer Page
    
    Client->>Controller: GET /v1/sessions/:id/live-details
    Controller->>CDP: getAllPages()
    CDP-->>Controller: Page[]
    
    loop for each Page
        Controller->>Page: Get targetId, title, url
        Controller->>Page: evaluate(faviconExtractor)
        Page-->>Controller: PageInfo
    end
    
    Controller-->>Client: SessionLiveDetailsResponse
```

**Diagram: Page Metadata Resolution Sequence**

The system uses `getPageTitle` and `getPageFavicon` utilities to safely extract data from pages. The favicon extractor evaluates a script in the browser context to find `<link rel="icon">` tags and resolve them to absolute URLs [api/src/utils/casting.ts:21-45]().

Sources: [api/src/modules/sessions/sessions.controller.ts:175-214](), [api/src/utils/casting.ts:21-45]()

---

## Browser Session Metrics

The `SessionDetails` schema defines the metrics tracked during a live session:

| Metric | Source | Description |
|--------|--------|-------------|
| `duration` | Computed | Elapsed time in ms since `createdAt` [api/src/modules/sessions/sessions.controller.ts:120-120]() |
| `eventCount` | `activeSession` | Number of CDP events processed [api/src/modules/sessions/sessions.schema.ts:98-98]() |
| `proxyTxBytes` | `activeSession` | Data transmitted through proxy [api/src/modules/sessions/sessions.schema.ts:114-118]() |
| `proxyRxBytes` | `activeSession` | Data received through proxy [api/src/modules/sessions/sessions.schema.ts:119-123]() |
| `status` | `activeSession` | Current lifecycle: `idle`, `live`, `released`, `failed` [api/src/modules/sessions/sessions.schema.ts:96-96]() |

Sources: [api/src/modules/sessions/sessions.schema.ts:93-127](), [api/src/modules/sessions/sessions.controller.ts:120-125]()

---

## Error Handling and Resilience

### Screencast Cleanup
The `handleCastSession` function implements a robust `handleSessionCleanup` routine to prevent memory leaks and dangling browser connections. It stops screencasts, detaches CDP clients, removes event listeners, and disconnects the browser instance when the WebSocket closes [api/src/plugins/browser-socket/casting.handler.ts:63-116]().

### Isolation
If a single page fails during info collection (e.g., due to a crash or navigation), the `handleGetSessionLiveDetails` loop catches the error and continues processing other pages, ensuring the monitoring dashboard remains functional [api/src/modules/sessions/sessions.controller.ts:207-214]().

Sources: [api/src/plugins/browser-socket/casting.handler.ts:63-116](), [api/src/modules/sessions/sessions.controller.ts:207-214]()

---

# Page: Quick Actions API

# Quick Actions API

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [api/src/modules/actions/actions.controller.ts](api/src/modules/actions/actions.controller.ts)
- [api/src/modules/actions/actions.routes.ts](api/src/modules/actions/actions.routes.ts)
- [api/src/modules/actions/actions.schema.ts](api/src/modules/actions/actions.schema.ts)
- [api/src/services/selenium.service.ts](api/src/services/selenium.service.ts)
- [api/src/utils/passthough-proxy.ts](api/src/utils/passthough-proxy.ts)
- [api/src/utils/proxy.ts](api/src/utils/proxy.ts)

</details>



The Quick Actions API provides stateless, single-shot browser operations for common web automation tasks. These endpoints enable simple, read-only operations without requiring session management or maintaining persistent browser state.

For comprehensive session-based browser automation with state persistence, see [Browser Sessions](#4). For detailed documentation on specific operations, see [Web Scraping](#5.1) and [Screenshots & PDF Generation](#5.2).

## Overview

Quick Actions are ephemeral browser operations that execute a single task and automatically clean up resources. Unlike sessions, these endpoints do not maintain browser state between requests and are ideal for simple automation workflows.

### Available Endpoints

| Endpoint | Purpose | Response Format |
|----------|---------|-----------------|
| `POST /v1/scrape` | Extract webpage content in multiple formats | JSON with content, metadata, links |
| `POST /v1/screenshot` | Capture webpage screenshot | Binary image (JPEG) |
| `POST /v1/pdf` | Generate PDF of webpage | Binary PDF document |
| `POST /v1/search` | Execute search engine queries | JSON with titles, URLs, descriptions |

**Architecture Context**

```mermaid
graph TB
    Client["HTTP Client"]
    ActionsRoutes["actions.routes.ts<br/>/v1/scrape, /v1/screenshot, /v1/pdf, /v1/search"]
    ActionsController["actions.controller.ts<br/>handleScrape, handleScreenshot, handlePDF, handleSearch"]
    SessionService["SessionService<br/>proxyFactory"]
    CDPService["CDPService<br/>launch, getPrimaryPage, createBrowserContext"]
    ProxyServer["ProxyServer<br/>Per-request proxy"]
    PassthroughServer["PassthroughServer<br/>Internal bypass"]
    Browser["Puppeteer Browser<br/>Chromium instance"]
    
    Client -->|"POST request"| ActionsRoutes
    ActionsRoutes -->|"delegate"| ActionsController
    ActionsController -->|"create proxy"| SessionService
    SessionService -->|"returns"| ProxyServer
    ProxyServer -->|"internal hosts"| PassthroughServer
    ActionsController -->|"get page"| CDPService
    CDPService -->|"controls"| Browser
    ActionsController -->|"with proxy"| ProxyServer
```

Sources: [api/src/modules/actions/actions.routes.ts:1-81](), [api/src/modules/actions/actions.controller.ts:25-151](), [api/src/utils/proxy.ts:15-69]()

### When to Use Quick Actions vs Sessions

**Use Quick Actions when:**
- Single webpage operation needed.
- No state persistence required.
- Simple read-only data extraction.
- One-off screenshot or PDF generation.
- Minimal configuration needed.

**Use Sessions when:**
- Multiple page navigation required.
- Cookies/storage persistence needed.
- Custom browser extensions required.
- CDP access for automation frameworks (Puppeteer/Playwright/Selenium).
- Complex multi-step workflows.

Sources: [api/src/modules/actions/actions.controller.ts:50-63]()

## Common Request Parameters

All Quick Action endpoints share these common parameters defined in Zod schemas:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `url` | string | Optional | Target URL to navigate to. If omitted, operates on current page. |
| `proxyUrl` | string\|null | Optional | Per-request proxy. Set to `null` to disable session proxy. |
| `delay` | number | Optional | Milliseconds to wait after page load before operation. |
| `logUrl` | string | Optional | Webhook URL for performance timing logs. |

**Schema Definition**

```mermaid
graph LR
    ScrapeRequest["ScrapeRequest<br/>url, format[], screenshot, pdf"]
    ScreenshotRequest["ScreenshotRequest<br/>url, fullPage"]
    PDFRequest["PDFRequest<br/>url"]
    SearchRequest["SearchRequest<br/>query"]
    CommonParams["Common Parameters<br/>proxyUrl, delay, logUrl"]
    
    ScrapeRequest -.->|"extends"| CommonParams
    ScreenshotRequest -.->|"extends"| CommonParams
    PDFRequest -.->|"extends"| CommonParams
    SearchRequest -.->|"extends"| CommonParams
```

Sources: [api/src/modules/actions/actions.schema.ts:5-108]()

## Request Processing Pipeline

All Quick Actions follow a common processing pipeline with distinct phases:

**Pipeline Flow**

```mermaid
graph TB
    Start["Request received"]
    ValidateSchema["Schema validation<br/>Zod schemas"]
    SetupProxy["Proxy setup<br/>SessionService.proxyFactory"]
    EnsureBrowser["Ensure browser<br/>CDPService.isRunning, launch"]
    GetPage["Acquire page<br/>createBrowserContext or getPrimaryPage"]
    Navigate["Navigate to URL<br/>safeGoto with timeout"]
    Delay["Optional delay<br/>setTimeout"]
    Execute["Execute operation<br/>scrape/screenshot/pdf/search"]
    Response["Return response<br/>reply.send"]
    Cleanup["Cleanup resources<br/>context.close, proxy.close"]
    Error["Error handling<br/>refreshPrimaryPage"]
    
    Start --> ValidateSchema
    ValidateSchema --> SetupProxy
    SetupProxy --> EnsureBrowser
    EnsureBrowser --> GetPage
    GetPage --> Navigate
    Navigate --> Delay
    Delay --> Execute
    Execute --> Response
    Response --> Cleanup
    Execute -.->|"error"| Error
    Error --> Cleanup
```

Sources: [api/src/modules/actions/actions.controller.ts:31-150]()

### Phase 1: Proxy Setup

When a `proxyUrl` is provided, the system creates a per-request proxy instance via `SessionService.proxyFactory`:

```mermaid
graph TB
    Request["Request with proxyUrl"]
    ProxyFactory["sessionService.proxyFactory"]
    ProxyServer["ProxyServer instance<br/>proxy-chain wrapper"]
    Listen["proxy.listen<br/>Bind to port 0"]
    InternalBypass["Internal bypass check<br/>PROXY_INTERNAL_BYPASS"]
    PassthroughServer["PassthroughServer<br/>Direct connection"]
    UpstreamProxy["Upstream proxy<br/>External proxy server"]
    
    Request --> ProxyFactory
    ProxyFactory --> ProxyServer
    ProxyServer --> Listen
    Listen --> InternalBypass
    InternalBypass -->|"internal host"| PassthroughServer
    InternalBypass -->|"external host"| UpstreamProxy
```

The `ProxyServer` class wraps the `proxy-chain` library and implements intelligent request routing. It checks for internal hostnames (localhost, etc.) to prevent routing loops.

Sources: [api/src/utils/proxy.ts:22-63](), [api/src/utils/passthough-proxy.ts:20-71]()

### Phase 2: Browser Page Acquisition

The system acquires a browser page using one of two strategies:

**Page Acquisition Strategy**

```mermaid
graph LR
    NeedsPage["Need page for operation"]
    HasProxy{"proxyUrl<br/>provided?"}
    CreateContext["CDPService.createBrowserContext<br/>with proxy URL"]
    NewPage["context.newPage"]
    GetPrimary["CDPService.getPrimaryPage<br/>Reuse existing"]
    
    NeedsPage --> HasProxy
    HasProxy -->|"yes"| CreateContext
    CreateContext --> NewPage
    HasProxy -->|"no"| GetPrimary
```

**With Proxy**: Creates an isolated `BrowserContext` with the proxy configuration [api/src/modules/actions/actions.controller.ts:57-58]().

**Without Proxy**: Reuses the primary page from the main browser instance via `getPrimaryPage()` [api/src/modules/actions/actions.controller.ts:61]().

### Phase 3: Navigation and Execution

Navigation is handled by `safeGoto`, which includes PDF detection and specific timeout settings:

```typescript
const safeResponse = normalizedUrl
  ? await safeGoto(page, normalizedUrl, {
      timeout: 30000,
      waitUntil: "domcontentloaded",
    })
  : { response: null, isPdf: false, pdfResponse: null };
```

If the target is a PDF, the system switches to a `node-fetch-with-cookies` strategy to acquire the buffer [api/src/modules/actions/actions.controller.ts:97-118]().

Sources: [api/src/modules/actions/actions.controller.ts:75-84](), [api/src/utils/scrape/safeGoTo.js]()

### Phase 4: Cleanup and Error Handling

All Quick Actions implement consistent cleanup patterns using try-catch-finally blocks:

**Error Recovery**: If an error occurs, the system captures it using the `getErrors` utility [api/src/modules/actions/actions.controller.ts:6](). If a URL was provided, `refreshPrimaryPage()` is called to ensure the browser remains in a clean state [api/src/modules/actions/actions.controller.ts:207]().

**Resource Cleanup**: Browser contexts and proxy servers are closed in the `finally` block to prevent resource leaks [api/src/modules/actions/actions.controller.ts:209-216]().

## Per-Request Proxy Architecture

The proxy system enables per-request proxy configuration without affecting the global browser session.

### Internal Bypass Configuration

The `PROXY_INTERNAL_BYPASS` environment variable configures hostnames that should bypass the upstream proxy. This is critical for preventing routing loops when the browser needs to reach the Steel API or local services [api/src/utils/proxy.ts:29-37]().

### PassthroughServer Implementation

The `PassthroughServer` is a simple HTTP proxy used when a request matches the internal bypass list. It forwards requests directly to the original host, filtering out hop-by-hop headers like `connection` and `proxy-authenticate` [api/src/utils/passthough-proxy.ts:5-14]().

## Browser Lifecycle Management

Quick Actions leverage the shared `CDPService` instance. The browser is launched lazily on the first request if it is not already running [api/src/modules/actions/actions.controller.ts:50-52]().

### Context vs Primary Page

- **BrowserContext**: Used for proxy requests. Isolated environment with separate cookies and storage. Closed immediately after use [api/src/modules/actions/actions.controller.ts:57]().
- **Primary Page**: Shared page used for non-proxy requests. Reused across requests for performance. Refreshed on errors [api/src/modules/actions/actions.controller.ts:61]().

## Performance Timing

All Quick Actions support performance logging via the `logUrl` parameter. Metrics include `proxyTime`, `pageTime`, `pageLoadTime`, and extraction/capture times [api/src/modules/actions/actions.controller.ts:31-62](). Timing data is updated via `updateLog` and sent to the provided webhook [api/src/utils/logging.js]().

## Schema Validation

All Quick Action endpoints use Zod schemas defined in `actions.schema.ts` for request validation and OpenAPI documentation generation [api/src/modules/actions/actions.schema.ts:1-135](). These schemas ensure type safety for parameters like `ScrapeFormat` and request bodies [api/src/modules/actions/actions.schema.ts:3-12]().

## Route Definitions

Routes are registered in `actions.routes.ts`. Each route includes metadata for Swagger/OpenAPI documentation, such as `operationId`, `summary`, and `tags` [api/src/modules/actions/actions.routes.ts:7-77]().

Sources: [api/src/modules/actions/actions.routes.ts:1-81](), [api/src/modules/actions/actions.schema.ts:124-133]()

---

# Page: Web Scraping

# Web Scraping

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [api/src/modules/actions/actions.controller.ts](api/src/modules/actions/actions.controller.ts)
- [api/src/modules/actions/actions.routes.ts](api/src/modules/actions/actions.routes.ts)
- [api/src/modules/actions/actions.schema.ts](api/src/modules/actions/actions.schema.ts)
- [api/src/services/selenium.service.ts](api/src/services/selenium.service.ts)
- [api/src/types/turndown.d.ts](api/src/types/turndown.d.ts)
- [api/src/utils/passthough-proxy.ts](api/src/utils/passthough-proxy.ts)
- [api/src/utils/proxy.ts](api/src/utils/proxy.ts)
- [api/src/utils/schema.ts](api/src/utils/schema.ts)
- [api/src/utils/scrape/cleanHtml.ts](api/src/utils/scrape/cleanHtml.ts)
- [api/src/utils/scrape/htmlToMarkdown.ts](api/src/utils/scrape/htmlToMarkdown.ts)
- [api/src/utils/scrape/index.ts](api/src/utils/scrape/index.ts)
- [api/src/utils/scrape/pdfToHtml.ts](api/src/utils/scrape/pdfToHtml.ts)
- [api/src/utils/scrape/readability.ts](api/src/utils/scrape/readability.ts)
- [api/src/utils/scrape/safeGoTo.ts](api/src/utils/scrape/safeGoTo.ts)
- [api/src/utils/scrape/transformHtml.ts](api/src/utils/scrape/transformHtml.ts)

</details>



This page documents the web scraping functionality in Steel Browser, focusing on the Quick Actions API endpoint `/v1/scrape` which allows extraction of content from web pages in various formats. This stateless API provides a simple way to scrape web content without maintaining browser state between requests.

For information about capturing screenshots and generating PDFs, see [Screenshots & PDF Generation](5.2).

## Web Scraping Architecture

The web scraping system in Steel Browser enables extracting content from any webpage through a simple API request. It leverages the Chrome DevTools Protocol (CDP) via the `CDPService` to control browser instances and extract content.

### System Mapping: API to Code Entities

The following diagram bridges the logical scraping flow to the specific classes and functions in the codebase.

```mermaid
flowchart TD
    subgraph "API Layer"
        Route["actions.routes.ts\n/scrape"]
        Controller["actions.controller.ts\nhandleScrape()"]
        Schema["actions.schema.ts\nScrapeRequest"]
    end

    subgraph "Service Layer"
        CDP["CDPService\nlaunch()\ncreateBrowserContext()"]
        Session["SessionService\nproxyFactory()"]
    end

    subgraph "Extraction & Transformation"
        SafeGo["safeGoTo.ts\nsafeGoto()"]
        PDFConv["pdfToHtml.ts\nextractLinksFromConvertedHtml()"]
        Clean["cleanHtml.ts\ncleanHtml()"]
        MD["htmlToMarkdown.ts\nhtmlToMarkdown()"]
        Read["readability.ts\ngetDefuddleContent()"]
    end

    Route --> Controller
    Controller -.-> Schema
    Controller --> Session
    Controller --> CDP
    Controller --> SafeGo
    Controller --> Clean
    Controller --> MD
    Controller --> Read
    SafeGo -.-> PDFConv
```

Sources: [api/src/modules/actions/actions.routes.ts:7-23](), [api/src/modules/actions/actions.controller.ts:25-30](), [api/src/services/cdp/cdp.service.ts:3-10](), [api/src/utils/scrape/safeGoTo.ts:11-43]()

## Request Parameters

The scrape endpoint accepts parameters defined in the `ScrapeRequest` Zod schema [api/src/modules/actions/actions.schema.ts:5-19]().

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `url` | string | No | The URL of the webpage to scrape. |
| `format` | `ScrapeFormat[]` | No | Array of output formats: `HTML`, `MARKDOWN`, `CLEANED_HTML`, `READABILITY`. |
| `screenshot` | boolean | No | Whether to include a base64 screenshot in the response. |
| `pdf` | boolean | No | Whether to include a base64 PDF in the response. |
| `proxyUrl` | string | No | Optional proxy URL. If provided, a temporary `ProxyServer` is spawned. |
| `delay` | number | No | Milliseconds to wait after page load before extraction. |

Sources: [api/src/modules/actions/actions.schema.ts:5-19](), [api/src/modules/actions/actions.controller.ts:33]()

## Scraping Process Flow

The scraping process in `handleScrape` manages the browser lifecycle, handles PDF-specific logic, and performs content transformation.

```mermaid
sequenceDiagram
    participant C as Client
    participant H as handleScrape
    participant P as ProxyServer
    participant B as CDPService
    participant S as safeGoto
    participant U as Scrape Utils

    C->>H: POST /scrape
    opt proxyUrl provided
        H->>P: sessionService.proxyFactory(url)
        H->>P: listen()
    end
    H->>B: launch() (if not running)
    alt Using Proxy
        H->>B: createBrowserContext(proxy.url)
    else No Proxy
        H->>B: getPrimaryPage()
    end
    H->>S: safeGoto(page, url)
    S-->>H: { response, isPdf, pdfResponse }
    
    alt isPdf == true
        H->>H: node-fetch with cookies
        H->>U: pdf2html.html(buffer)
    else isPdf == false
        H->>B: page.evaluate() (Extract DOM/Meta)
    end

    par Format Processing
        H->>U: cleanHtml()
        H->>U: htmlToMarkdown()
        H->>U: getDefuddleContent()
    end
    
    H->>C: ScrapeResponse
```

Sources: [api/src/modules/actions/actions.controller.ts:38-151](), [api/src/utils/scrape/safeGoTo.ts:11-43]()

## Output Formats & Transformation

Steel Browser provides several transformation utilities to prepare content for LLMs or storage:

| Format | Code Entity | Description |
|--------|-------------|------------|
| `HTML` | `document.documentElement.outerHTML` | Full raw source from the browser evaluation [api/src/modules/actions/actions.controller.ts:182](). |
| `CLEANED_HTML` | `cleanHtml()` | Removes blacklisted tags like `script`, `style`, `svg`, and `path`. Strips attributes like `onerror` and `js.*` [api/src/utils/scrape/cleanHtml.ts:3-66](). |
| `MARKDOWN` | `htmlToMarkdown()` | Uses `Turndown` with plugins for tables, task lists, and code blocks. Includes a linting pass to fix formatting [api/src/utils/scrape/htmlToMarkdown.ts:10-28](). |
| `READABILITY` | `getDefuddleContent()` | Uses the `defuddle` library (Readability port) to extract the "main" article content [api/src/modules/actions/actions.controller.ts:17](). |

### Metadata Extraction
Regardless of the format, the system extracts rich metadata during the `page.evaluate()` phase, including:
- Standard meta: `title`, `description`, `author`, `keywords`.
- OpenGraph: `og:title`, `og:image`, `og:description`.
- Linked Data: `application/ld+json` blocks.
- Page details: `language`, `urlSource`, `timestamp`.

Sources: [api/src/modules/actions/actions.controller.ts:158-204](), [api/src/utils/scrape/cleanHtml.ts:4-30]()

## PDF Handling

Steel Browser includes a specialized path for URLs that resolve to PDF files. The `safeGoto` utility detects `application/pdf` content-types [api/src/utils/scrape/safeGoTo.ts:23-25]().

1. **Detection**: If `safeGoto` detects a PDF, it returns `isPdf: true`.
2. **Acquisition**: The controller performs a `node-fetch` using the browser's current cookies to download the PDF buffer [api/src/modules/actions/actions.controller.ts:100-118]().
3. **Conversion**: The buffer is converted to HTML using `pdf2html` [api/src/modules/actions/actions.controller.ts:121]().
4. **Metadata Mapping**: `buildHtmlLikeMetadataFromPdf` maps PDF metadata (Title, Author, CreationDate) into the standard HTML metadata schema [api/src/utils/scrape/pdfToHtml.ts:67-138]().

Sources: [api/src/modules/actions/actions.controller.ts:97-150](), [api/src/utils/scrape/pdfToHtml.ts:67-138]()

## Proxy Implementation

When `proxyUrl` is passed to the scrape endpoint, Steel Browser creates a local `ProxyServer` instance [api/src/utils/proxy.ts:15]().

- **Internal Bypass**: The proxy automatically detects and bypasses requests to internal hosts defined in `env.PROXY_INTERNAL_BYPASS` or the local host [api/src/utils/proxy.ts:29-37]().
- **Passthrough**: For bypassed requests, it uses `PassthroughServer` to avoid header corruption [api/src/utils/passthough-proxy.ts:20]().
- **Upstream**: Standard requests are forwarded to the provided `upstreamProxyUrl` [api/src/utils/proxy.ts:48]().

Sources: [api/src/utils/proxy.ts:15-69](), [api/src/utils/passthough-proxy.ts:20-71]()

## Error Handling

The endpoint uses `getErrors` and `updateLog` to manage failures [api/src/modules/actions/actions.controller.ts:6-7]().
- **Navigation Errors**: If `page.goto` fails (e.g., timeout), the error is caught, and resources are cleaned up.
- **Cleanup**: In the `finally` block, if a proxy context was created, it is closed via `context.close()`. If the primary page was used, it is navigated to `about:blank` to reset state for the next request [api/src/modules/actions/actions.controller.ts:275-285]().

Sources: [api/src/modules/actions/actions.controller.ts:275-295]()

---

# Page: Screenshots & PDF Generation

# Screenshots & PDF Generation

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [api/src/modules/actions/actions.controller.ts](api/src/modules/actions/actions.controller.ts)
- [api/src/modules/actions/actions.routes.ts](api/src/modules/actions/actions.routes.ts)
- [api/src/modules/actions/actions.schema.ts](api/src/modules/actions/actions.schema.ts)
- [api/src/services/selenium.service.ts](api/src/services/selenium.service.ts)
- [api/src/utils/passthough-proxy.ts](api/src/utils/passthough-proxy.ts)
- [api/src/utils/proxy.ts](api/src/utils/proxy.ts)
- [api/src/utils/scrape/pdfToHtml.ts](api/src/utils/scrape/pdfToHtml.ts)
- [api/src/utils/scrape/safeGoTo.ts](api/src/utils/scrape/safeGoTo.ts)

</details>



Steel Browser provides robust capabilities for capturing screenshots and generating PDF documents from web pages. These features are available through both stateless quick action API endpoints and as part of browser sessions. This document details how to use these features, the implementation details, and configuration options.

For information about web scraping capabilities, see [Web Scraping](#5.1).

## 1. Overview

Steel provides screenshot and PDF generation capabilities through dedicated API endpoints. These features allow you to:

- Capture full-page or viewport-only screenshots in JPEG format [api/src/modules/actions/actions.controller.ts:268-268]()
- Generate PDF documents from rendered web pages [api/src/modules/actions/actions.controller.ts:348-348]()
- Use per-request proxy configuration [api/src/modules/actions/actions.controller.ts:229-232]()
- Apply custom delays for dynamic content loading [api/src/modules/actions/actions.controller.ts:258-260]()
- Track detailed timing metrics [api/src/modules/actions/actions.controller.ts:225-226]()

Both features are available as:
1. **Quick Actions** - Stateless endpoints at `/v1/screenshot` and `/v1/pdf` [api/src/modules/actions/actions.routes.ts:26-59]()
2. **Session Actions** - Session-aware endpoints that use existing browser contexts.

**Screenshot & PDF Request Flow**

```mermaid
flowchart TD
    Client["Client"] -->|"POST request"| Route["actions.routes.ts"]
    Route -->|"handleScreenshot() or handlePDF()"| Controller["actions.controller.ts"]
    Controller -->|"proxyFactory()"| SessionService["SessionService"]
    SessionService -->|"create ProxyServer"| ProxyServer["ProxyServer (utils/proxy.ts)"]
    Controller -->|"launch() if not running"| CDPService["CDPService"]
    CDPService -->|"getBrowser()"| Browser["Puppeteer Browser"]
    
    Controller -->|"with proxy"| Context["createBrowserContext()"]
    Controller -->|"no proxy"| PrimaryPage["getPrimaryPage()"]
    
    Context --> Page["context.newPage()"]
    PrimaryPage --> Page
    
    Page -->|"page.goto()"| Navigation["Page Navigation"]
    Navigation -->|"page.screenshot() or page.pdf()"| Capture["Capture/Generate"]
    Capture --> Binary["Binary Data (JPEG/PDF)"]
    Binary --> Client
```

Sources: [api/src/modules/actions/actions.controller.ts:219-376](), [api/src/modules/actions/actions.routes.ts:26-59]()

## 2. API Endpoints

Steel provides endpoints for screenshot and PDF generation within the `actions` module.

### 2.1 Quick Action Endpoints

**Screenshot:**
```
POST /v1/screenshot
```
Captures a JPEG screenshot. Returns binary image data.
[api/src/modules/actions/actions.routes.ts:26-41]()

**PDF:**
```
POST /v1/pdf
```
Generates a PDF document. Returns binary PDF data.
[api/src/modules/actions/actions.routes.ts:43-59]()

## 3. Request and Response Schemas

### 3.1 Screenshot Request Schema (`ScreenshotRequest`)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `url` | string | No | Target URL to screenshot. |
| `proxyUrl` | string \| null | No | Proxy URL or `null` to disable proxy. |
| `delay` | number | No | Milliseconds to wait before capturing. |
| `fullPage` | boolean | No | Capture entire scrollable page (default: false). |
| `logUrl` | string | No | URL to POST timing metrics. |

Sources: [api/src/modules/actions/actions.schema.ts:59-71]()

### 3.2 PDF Request Schema (`PDFRequest`)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `url` | string | No | Target URL to render as PDF. |
| `proxyUrl` | string \| null | No | Proxy URL or `null` to disable proxy. |
| `delay` | number | No | Milliseconds to wait before generating. |
| `logUrl` | string | No | URL to POST timing metrics. |

Sources: [api/src/modules/actions/actions.schema.ts:75-86]()

## 4. Implementation Details

**Processing Sequence**

```mermaid
sequenceDiagram
    participant Client
    participant Controller as actions.controller.ts
    participant Proxy as ProxyServer (utils/proxy.ts)
    participant CDP as CDPService
    participant Page as Puppeteer Page
    
    Client->>Controller: POST (ScreenshotRequest/PDFRequest)
    Controller->>Controller: startTime = Date.now()
    
    opt proxyUrl provided
        Controller->>Proxy: new ProxyServer(proxyUrl)
        Proxy->>Proxy: listen()
    end
    
    Controller->>CDP: launch() if !isRunning()
    
    alt with proxy
        Controller->>CDP: createBrowserContext(proxy.url)
        CDP-->>Controller: context
        Controller->>Page: context.newPage()
    else no proxy
        Controller->>CDP: getPrimaryPage()
        CDP-->>Controller: page
    end
    
    opt url provided
        Controller->>Page: safeGoto(url)
    end
    
    opt delay specified
        Controller->>Controller: setTimeout(delay)
    end
    
    alt Screenshot
        Controller->>Page: page.screenshot({type: "jpeg", quality: 100})
    else PDF
        Controller->>Page: page.pdf()
    end
    
    Controller->>Client: Send Binary Buffer
```

Sources: [api/src/modules/actions/actions.controller.ts:219-376](), [api/src/utils/scrape/safeGoTo.ts:11-43]()

### 4.1 Screenshot Capture

Screenshots use Puppeteer's `page.screenshot()` method with high-quality settings [api/src/modules/actions/actions.controller.ts:268-268]():

- **Format**: `jpeg`
- **Quality**: `100`
- **Full Page**: Configurable via `fullPage` boolean in request [api/src/modules/actions/actions.schema.ts:69-69]().

### 4.2 PDF Generation

PDFs are generated using Puppeteer's `page.pdf()` method [api/src/modules/actions/actions.controller.ts:348-348]().

## 5. Proxy Support

The `ProxyServer` class in `api/src/utils/proxy.ts` handles per-request proxying.

### 5.1 ProxyServer Implementation

The `ProxyServer` extends `proxy-chain.Server` [api/src/utils/proxy.ts:15-15](). It includes a `prepareRequestFunction` that implements:

- **Internal Bypass**: Checks if the hostname is `0.0.0.0`, the system `HOST`, or listed in `env.PROXY_INTERNAL_BYPASS` [api/src/utils/proxy.ts:29-37]().
- **Passthrough**: If bypassed, it uses a `PassthroughServer` (Node `http.createServer`) to forward requests manually [api/src/utils/passthough-proxy.ts:20-71]().
- **Upstream Forwarding**: Otherwise, it forwards to the provided `upstreamProxyUrl` [api/src/utils/proxy.ts:48-49]().

Sources: [api/src/utils/proxy.ts:15-69](), [api/src/utils/passthough-proxy.ts:20-125]()

## 6. Integration with Scraping

The `/v1/scrape` endpoint can optionally return screenshots or PDFs alongside extracted content [api/src/modules/actions/actions.schema.ts:8-9]().

### 6.1 PDF to HTML Conversion
When a target URL returns a PDF content-type, Steel uses `pdf2html` to convert the document for scraping [api/src/modules/actions/actions.controller.ts:121-121]().
- **Metadata Extraction**: `pdf2html.meta` extracts document properties [api/src/modules/actions/actions.controller.ts:125-125]().
- **Link Extraction**: `extractLinksFromConvertedHtml` uses `cheerio` to find links in the converted HTML [api/src/utils/scrape/pdfToHtml.ts:56-65]().

### 6.2 Safe Navigation
`safeGoto` is used to handle navigations where the response might be a PDF, preventing Puppeteer from throwing `net::ERR_ABORTED` [api/src/utils/scrape/safeGoTo.ts:11-43]().

Sources: [api/src/modules/actions/actions.controller.ts:97-150](), [api/src/utils/scrape/pdfToHtml.ts:67-138]()

## 7. Performance Tracking

Detailed timing metrics are collected for both operations:

| Metric | Code Reference |
|--------|----------------|
| `proxyTime` | [api/src/modules/actions/actions.controller.ts:233-233]() |
| `pageLoadTime` | [api/src/modules/actions/actions.controller.ts:262-262]() |
| `screenshotTime` | [api/src/modules/actions/actions.controller.ts:270-270]() |
| `pdfTime` | [api/src/modules/actions/actions.controller.ts:350-350]() |

If a `logUrl` is provided, these metrics are sent to the external sink via `updateLog` [api/src/modules/actions/actions.controller.ts:273-275]().

Sources: [api/src/modules/actions/actions.controller.ts:225-275](), [api/src/utils/logging.ts:1-10]()

---

# Page: Proxy Support

# Proxy Support

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [api/src/modules/actions/actions.controller.ts](api/src/modules/actions/actions.controller.ts)
- [api/src/modules/actions/actions.routes.ts](api/src/modules/actions/actions.routes.ts)
- [api/src/modules/actions/actions.schema.ts](api/src/modules/actions/actions.schema.ts)
- [api/src/services/selenium.service.ts](api/src/services/selenium.service.ts)
- [api/src/services/session.service.ts](api/src/services/session.service.ts)
- [api/src/utils/passthough-proxy.ts](api/src/utils/passthough-proxy.ts)
- [api/src/utils/proxy.ts](api/src/utils/proxy.ts)
- [api/src/utils/requests.ts](api/src/utils/requests.ts)

</details>



This document describes the proxy infrastructure in Steel Browser, including the `ProxyServer` implementation, internal bypass mechanisms, traffic monitoring, and per-request proxy overrides. The system is designed to provide seamless integration between browser automation and external proxy providers while maintaining high performance for internal communications.

---

## Overview

Steel Browser provides a flexible proxy system that supports:
- **Session-level proxy configuration**: Persistent browser sessions using a single proxy identity.
- **Per-request proxy overrides**: Dynamic proxy switching for quick actions (scrape, screenshot, PDF).
- **Internal request bypass**: Prevents proxy loops for traffic destined for the local system.
- **Traffic monitoring**: Real-time accounting of transmitted (`txBytes`) and received (`rxBytes`) data.
- **Bandwidth optimization**: Integration with request interception to block images, media, or ads before they reach the proxy.

The proxy implementation wraps the `proxy-chain` library, extending it with Steel-specific logic for internal routing and traffic tracking.

**Sources**: [api/src/utils/proxy.ts:1-70](), [api/src/services/session.service.ts:93-119](), [api/src/utils/passthough-proxy.ts:1-126]()

---

## Proxy Architecture

The following diagram illustrates how the `SessionService` coordinates with the `ProxyServer` and `CDPService` to route traffic.

```mermaid
graph TB
    subgraph "Entry Points"
        ActionsCtrl["actions.controller.ts<br/>handleScrape"]
        SessionSvc["session.service.ts<br/>startSession"]
    end
    
    subgraph "Proxy Logic Space"
        ProxyFactory["ProxyFactory<br/>(Function Type)"]
        ProxyServer["ProxyServer<br/>(Class)"]
        PassthroughServer["PassthroughServer<br/>(http.Server)"]
    end
    
    subgraph "External World"
        UpstreamProxy["Upstream Proxy<br/>(Residential/Data Center)"]
        InternalAPI["Internal API<br/>(Localhost/Steel API)"]
    end

    ActionsCtrl -->|"proxyFactory()"| ProxyFactory
    SessionSvc -->|"proxyFactory()"| ProxyFactory
    ProxyFactory -->|"new"| ProxyServer
    
    ProxyServer -->|"prepareRequestFunction"| Routing{"Is Internal?"}
    Routing -->|"Yes"| PassthroughServer
    Routing -->|"No"| UpstreamProxy
    
    PassthroughServer --> InternalAPI
```

**Sources**: [api/src/utils/proxy.ts:15-69](), [api/src/services/session.service.ts:64-64](), [api/src/modules/actions/actions.controller.ts:39-42]()

---

## IProxyServer Interface

The `IProxyServer` interface defines the contract for all proxy implementations within the system.

| Property/Method | Type | Description |
|----------------|------|-------------|
| `url` | `string` | The local URL the browser connects to (e.g., `http://127.0.0.1:PORT`). |
| `upstreamProxyUrl` | `string` | The actual external proxy URL being wrapped. |
| `txBytes` | `number` | Total bytes transmitted to the upstream proxy. |
| `rxBytes` | `number` | Total bytes received from the upstream proxy. |
| `listen()` | `Promise<void>` | Starts the server on a dynamic port. |
| `close(force?)` | `Promise<void>` | Stops the server and cleans up resources. |

**Sources**: [api/src/utils/proxy.ts:6-13]()

---

## ProxyServer Implementation

### Class Structure and Routing

The `ProxyServer` class extends `proxy-chain`'s `Server`. Its primary responsibility is to decide whether a request should be forwarded to an external provider or handled internally.

[api/src/utils/proxy.ts:15-69]()

### Internal Bypass Logic

To prevent performance degradation and infinite loops, the system identifies internal traffic (e.g., the browser communicating with the Steel API) and bypasses the upstream proxy.

[api/src/utils/proxy.ts:26-50]()

1. **Default Bypass**: Always includes `0.0.0.0` and the value of `process.env.HOST`.
2. **Configuration**: Users can extend this list via the `PROXY_INTERNAL_BYPASS` environment variable.
3. **Execution**: If a match is found, the request is handed off to `PassthroughServer` and `makePassthrough`.

**Sources**: [api/src/utils/proxy.ts:29-45](), [api/src/env.js:1-10]()

### Traffic Accounting

The proxy tracks bytes only for external (upstream) connections to ensure accurate billing and usage reporting.

[api/src/utils/proxy.ts:53-59]()

- **Event**: Listens to the `connectionClosed` event.
- **Filter**: If the `connectionId` is found in the `hostConnections` set (internal traffic), it is ignored.
- **Aggregation**: Adds `stats.trgTxBytes` and `stats.trgRxBytes` to the session totals.

---

## PassthroughServer & makePassthrough

Internal requests require a specialized handler because `proxy-chain` can occasionally corrupt internal chunked requests. The `PassthroughServer` provides a clean HTTP reverse proxy.

### Hop-by-Hop Header Filtering

To comply with RFC 2616, the system strips connection-specific headers before forwarding internal requests.

[api/src/utils/passthough-proxy.ts:4-14]()

Headers stripped include: `connection`, `proxy-authenticate`, `keep-alive`, `transfer-encoding`, and `upgrade`.

### Request Forwarding

The `makePassthrough` function manually pipes the client request to the target and collects the response.

[api/src/utils/passthough-proxy.ts:79-125]()

---

## Proxy Usage Patterns

### Session-Level Proxies

In a standard session, the proxy is initialized during `startSession` and remains active until the session is closed.

```mermaid
sequenceDiagram
    participant S as SessionService
    participant P as ProxyServer
    participant B as Browser (Chrome)
    
    S->>P: proxyFactory(proxyUrl)
    P->>P: listen() (Assigns dynamic port)
    S->>B: Launch with --proxy-server=P.url
    Note over B, P: All browser traffic flows through P
    B->>P: Request google.com
    P->>P: Check Internal Bypass
    P->>External: Forward to Upstream Proxy
```

**Sources**: [api/src/services/session.service.ts:208-211](), [api/src/services/session.service.ts:216-217]()

### Per-Request Overrides (Quick Actions)

For endpoints like `/scrape`, a user can provide a `proxyUrl` in the request body. This creates an ephemeral proxy and a temporary browser context.

[api/src/modules/actions/actions.controller.ts:39-58]()

1. **Proxy Creation**: `sessionService.proxyFactory(proxyUrl)` is called.
2. **Context Isolation**: `browserService.createBrowserContext(proxy.url)` ensures this proxy is only used for the specific request.
3. **Cleanup**: The context and proxy are closed immediately after the action completes.

**Sources**: [api/src/modules/actions/actions.controller.ts:39-42](), [api/src/modules/actions/actions.controller.ts:57-58]()

---

## Bandwidth Optimization

Steel Browser can reduce proxy costs by blocking heavy resources before they are requested from the proxy server.

[api/src/services/session.service.ts:193-206]()

When `optimizeBandwidth` is enabled, the `CDPService` filters requests based on patterns defined in `utils/requests.ts`:
- **Images**: `RE_IMAGE_EXT` (jpg, png, webp, etc.) [api/src/utils/requests.ts:53-53]()
- **Media**: `RE_VIDEO_EXT` (mp4, m3u8, etc.) [api/src/utils/requests.ts:54-54]()
- **Ads**: `AD_HOSTS` list (doubleclick.net, google-analytics.com, etc.) [api/src/utils/requests.ts:1-51]()

**Sources**: [api/src/utils/requests.ts:65-79](), [api/src/services/session.service.ts:193-206]()

---

## Selenium Support

Selenium sessions also support proxying by passing the local proxy URL into the Chrome arguments.

[api/src/services/selenium.service.ts:20-30]()

The `SeleniumService` filters the `launchOptions` and injects the `proxy-server` argument into the `java -jar selenium-server.jar` execution.

**Sources**: [api/src/services/selenium.service.ts:27-27](), [api/src/services/session.service.ts:216-230]()

---

# Page: File Management

# File Management

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [api/src/modules/files/files.controller.ts](api/src/modules/files/files.controller.ts)
- [api/src/modules/files/files.routes.ts](api/src/modules/files/files.routes.ts)
- [api/src/modules/files/files.schema.ts](api/src/modules/files/files.schema.ts)
- [api/src/plugins/file-storage.ts](api/src/plugins/file-storage.ts)
- [api/src/services/file.service.ts](api/src/services/file.service.ts)

</details>



The File Management system provides persistent storage for files associated with browser sessions. This system enables uploading, downloading, listing, and deleting files, along with automatic zip archive creation for bulk downloads. The implementation uses a singleton `FileService` with filesystem watching via `chokidar` to maintain a continuously updated archive.

For detailed information on the REST API endpoints and request validation, see [File API](#7.1). For the automatic archive generation system and debouncing logic, see [Archive Management](#7.2).

## System Overview

The file management system consists of three primary layers: the API layer (`FilesController`), the service layer (`FileService`), and the storage layer (filesystem with `chokidar` monitoring). The `FileService` implements a singleton pattern to ensure consistent state and coordinate file watching across the application.

### File Management Architecture

```mermaid
graph TB
    subgraph "API Layer"
        FilesRoutes["files.routes.ts<br/>Route Definitions"]
        FilesController["FilesController<br/>Request Handlers"]
        FilesSchemas["files.schema.ts<br/>Zod Validation"]
    end
    
    subgraph "Service Layer"
        FileService["FileService<br/>Singleton Instance"]
        getInstance["FileService.getInstance()"]
        
        FileService --> getInstance
    end
    
    subgraph "Storage & Monitoring"
        BaseFilesPath["baseFilesPath<br/>/files or tmpdir()/files"]
        FSWatcher["chokidar.FSWatcher<br/>File System Monitor"]
        PrebuiltArchive["prebuiltArchivePath<br/>/tmp/.steel/files.zip"]
        
        FSWatcher -->|watches| BaseFilesPath
        FSWatcher -->|triggers| DebouncedArchive["debouncedCreateArchive<br/>500ms debounce"]
        DebouncedArchive -->|creates| PrebuiltArchive
    end
    
    subgraph "File Operations"
        SaveFile["saveFile()"]
        DownloadFile["downloadFile()"]
        ListFiles["listFiles()"]
        DeleteFile["deleteFile()"]
        CleanupFiles["cleanupFiles()"]
    end
    
    FilesRoutes --> FilesController
    FilesController --> FilesSchemas
    FilesController --> FileService
    
    FileService --> SaveFile
    FileService --> DownloadFile
    FileService --> ListFiles
    FileService --> DeleteFile
    FileService --> CleanupFiles
    
    SaveFile --> BaseFilesPath
    DownloadFile --> BaseFilesPath
    ListFiles --> BaseFilesPath
    DeleteFile --> BaseFilesPath
    CleanupFiles --> BaseFilesPath
    
    SaveFile -->|triggers| FSWatcher
    DeleteFile -->|triggers| FSWatcher
```

**Sources:** [api/src/modules/files/files.controller.ts:17-18](), [api/src/services/file.service.ts:16-45](), [api/src/modules/files/files.routes.ts:8-146]()

## FileService Architecture

The `FileService` class uses a singleton pattern to maintain a single instance throughout the application lifecycle. This ensures consistent file watching state and prevents duplicate archive creation operations.

| Component | Type | Purpose |
|-----------|------|---------|
| `baseFilesPath` | `string` | Root directory for file storage (`/files` in production, `tmpdir()/files` in development) [api/src/services/file.service.ts:28-28]() |
| `fileWatcher` | `FSWatcher \| null` | Chokidar instance monitoring the base files directory [api/src/services/file.service.ts:18-18]() |
| `prebuiltArchivePath` | `string` | Path to the continuously maintained zip archive (`/tmp/.steel/files.zip`) [api/src/services/file.service.ts:30-30]() |
| `isArchiving` | `boolean` | Flag preventing concurrent archive creation operations [api/src/services/file.service.ts:22-22]() |
| `debouncedCreateArchive` | `DebouncedFunc` | Debounced function (500ms) that triggers archive rebuilding [api/src/services/file.service.ts:25-35]() |

The singleton is accessed via `FileService.getInstance()`, which is registered as a Fastify decorator through the `fileStoragePlugin` [api/src/plugins/file-storage.ts:5-8]().

**Sources:** [api/src/services/file.service.ts:16-45](), [api/src/plugins/file-storage.ts:1-10]()

## Storage Structure and Path Security

Files are stored in a hierarchical directory structure under `baseFilesPath`. The system implements multiple layers of path validation to prevent directory traversal attacks.

### Path Validation Flow

```mermaid
graph TB
    subgraph "Path Validation Pipeline"
        InputPath["User-provided Path<br/>e.g., 'documents/file.pdf'"]
        ValidatePath["FilesController.validatePath()"]
        GetSafeFilePath["FileService.getSafeFilePath()"]
        ResolvedPath["Resolved Absolute Path"]
        
        InputPath --> ValidatePath
        ValidatePath -->|pass| GetSafeFilePath
        ValidatePath -->|fail| Reject400["400 Bad Request"]
        GetSafeFilePath -->|validated| ResolvedPath
        GetSafeFilePath -->|outside base| RejectError["Error: Invalid path"]
    end
    
    subgraph "Validation Logic"
        Rule1["path.isAbsolute() = false"]
        Rule2["!includes('..')"]
        Rule3["!includes('\\0')"]
        Rule4["!normalized.startsWith('..')"]
        Rule5["resolvedPath.startsWith(baseFilesPath)"]
    end
    
    ValidatePath -.->|checks| Rule1
    ValidatePath -.->|checks| Rule2
    ValidatePath -.->|checks| Rule3
    ValidatePath -.->|checks| Rule4
    
    GetSafeFilePath -.->|checks| Rule5
```

The `validatePath` method in `FilesController` performs initial string-based validation [api/src/modules/files/files.controller.ts:20-39](), while `getSafeFilePath` in `FileService` performs final path resolution and containment verification [api/src/services/file.service.ts:88-97]().

**Sources:** [api/src/modules/files/files.controller.ts:20-39](), [api/src/services/file.service.ts:88-97]()

## File Upload Flow

File uploads support two input methods: direct binary data via `multipart/form-data` submission, or URLs for remote file download. The system uses temporary staging before moving files to their final location.

```mermaid
sequenceDiagram
    participant Client
    participant FilesController
    participant TempDir as "tmpdir()"
    participant FileService
    participant BaseFilesPath as "baseFilesPath"
    
    Client->>FilesController: POST /sessions/:id/files
    
    alt Binary File Upload
        FilesController->>TempDir: Create temp file upload_${uuid}
        FilesController->>FilesController: validatePath(path)
        FilesController->>FileService: saveFile({filePath, stream})
        FileService->>BaseFilesPath: writeFile(safeFilePath, stream)
        FileService-->>FilesController: FileDetails
        FilesController->>TempDir: unlink(tempFile)
    else URL Download
        FilesController->>FilesController: createStreamFromUrl(url)
        FilesController->>FileService: saveFile({filePath, stream})
        FileService->>BaseFilesPath: writeFile(safeFilePath, stream)
        FileService-->>FilesController: FileDetails
    end
    
    FilesController-->>Client: 200 FileDetails
```

The upload handler processes multipart requests, extracting the `file` field (binary or URL) and optional `path` [api/src/modules/files/files.controller.ts:41-157](). For URL-based uploads, `createStreamFromUrl` performs the fetch [api/src/modules/files/files.controller.ts:159-191]().

**Sources:** [api/src/modules/files/files.controller.ts:41-191](), [api/src/services/file.service.ts:110-148]()

## File System Watching

The file watching system uses `chokidar` to monitor all changes within `baseFilesPath` and automatically trigger archive rebuilding. The watcher is initialized during `FileService` construction [api/src/services/file.service.ts:37-37]().

The watcher configuration uses `awaitWriteFinish` to ensure files are completely written before triggering events [api/src/services/file.service.ts:63-72](). All file system events (add, unlink, etc.) invoke the `debouncedCreateArchive` function [api/src/services/file.service.ts:76-85]().

**Sources:** [api/src/services/file.service.ts:62-86](), [api/src/services/file.service.ts:47-60]()

## File Listing and Metadata

The `listFiles` method recursively scans the entire `baseFilesPath` directory tree, collecting file metadata (size, lastModified) for all discovered files [api/src/services/file.service.ts:204-250](). The results are sorted by modification time in descending order.

**Sources:** [api/src/services/file.service.ts:204-250]()

## Archive Download Mechanism

The archive download endpoint serves a pre-built `files.zip` that is continuously maintained. When clients request `/sessions/:sessionId/files.zip`, the system attempts to serve the existing archive from `prebuiltArchivePath` [api/src/modules/files/files.controller.ts:291-335]().

**Sources:** [api/src/modules/files/files.controller.ts:291-335](), [api/src/services/file.service.ts:329-331]()

## File Deletion and Cleanup

Individual files can be deleted via `DELETE /sessions/:sessionId/files/*`, while `DELETE /sessions/:sessionId/files` removes all files using `cleanupFiles()` [api/src/modules/files/files.routes.ts:92-131]().

The `cleanupFiles` method performs a comprehensive teardown:
1. Cancels pending debounced archive operations [api/src/services/file.service.ts:284-284]().
2. Removes the existing `files.zip` [api/src/services/file.service.ts:287-287]().
3. Recursively deletes and recreates the `baseFilesPath` [api/src/services/file.service.ts:297-319]().

**Sources:** [api/src/services/file.service.ts:280-323](), [api/src/modules/files/files.controller.ts:261-289]()

## Configuration

File storage behavior is configured through `steelBrowserConfig.fileStorage`. This includes the `maxSizePerSession` limit which is applied to the `fastify-multipart` plugin [api/src/modules/files/files.routes.ts:11-16]().

**Sources:** [api/src/modules/files/files.routes.ts:11-16](), [api/src/services/file.service.ts:28-30]()

---

# Page: File API

# File API

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [api/src/modules/files/files.controller.ts](api/src/modules/files/files.controller.ts)
- [api/src/modules/files/files.routes.ts](api/src/modules/files/files.routes.ts)
- [api/src/modules/files/files.schema.ts](api/src/modules/files/files.schema.ts)
- [api/src/plugins/file-storage.ts](api/src/plugins/file-storage.ts)
- [api/src/services/file.service.ts](api/src/services/file.service.ts)

</details>



## Purpose and Scope

This document describes the HTTP REST API for managing files within browser sessions. The File API provides endpoints for uploading files (via binary data or URL), downloading files, listing files, deleting files, and retrieving bulk archives. Each session maintains its own isolated file storage namespace.

For information about the automatic archive generation system and file watching mechanism that powers the archive endpoint, see [Archive Management](#7.2). For general session management concepts, see [Session Management API](#4.1).

---

## API Architecture

The File API follows a three-layer architecture: routes define HTTP endpoints, controllers handle request/response logic, and the `FileService` singleton manages the underlying file operations.

```mermaid
graph TB
    Client["HTTP Client"]
    
    subgraph "Route Layer"
        Routes["files.routes.ts<br/>POST /sessions/:sessionId/files<br/>GET /sessions/:sessionId/files/*<br/>GET /sessions/:sessionId/files<br/>DELETE /sessions/:sessionId/files/*<br/>DELETE /sessions/:sessionId/files<br/>GET /sessions/:sessionId/files.zip"]
    end
    
    subgraph "Controller Layer"
        Controller["FilesController"]
        handleFileUpload["handleFileUpload()"]
        handleFileDownload["handleFileDownload()"]
        handleFileList["handleFileList()"]
        handleFileDelete["handleFileDelete()"]
        handleFileDeleteAll["handleFileDeleteAll()"]
        handleDownloadArchive["handleDownloadArchive()"]
        validatePath["validatePath()"]
        createStreamFromUrl["createStreamFromUrl()"]
    end
    
    subgraph "Service Layer"
        FileService["FileService<br/>(Singleton)"]
        saveFile["saveFile()"]
        downloadFile["downloadFile()"]
        listFiles["listFiles()"]
        deleteFile["deleteFile()"]
        cleanupFiles["cleanupFiles()"]
        getPrebuiltArchivePath["getPrebuiltArchivePath()"]
    end
    
    subgraph "Storage"
        FileSystem["File System<br/>/files (production)<br/>/tmp/files (dev)"]
        ArchiveCache["/tmp/.steel/files.zip"]
    end
    
    Client --> Routes
    Routes --> Controller
    
    Controller --> handleFileUpload
    Controller --> handleFileDownload
    Controller --> handleFileList
    Controller --> handleFileDelete
    Controller --> handleFileDeleteAll
    Controller --> handleDownloadArchive
    
    handleFileUpload --> validatePath
    handleFileUpload --> createStreamFromUrl
    handleFileUpload --> saveFile
    
    handleFileDownload --> downloadFile
    handleFileList --> listFiles
    handleFileDelete --> deleteFile
    handleFileDeleteAll --> cleanupFiles
    handleDownloadArchive --> getPrebuiltArchivePath
    
    saveFile --> FileSystem
    downloadFile --> FileSystem
    listFiles --> FileSystem
    deleteFile --> FileSystem
    cleanupFiles --> FileSystem
    
    getPrebuiltArchivePath --> ArchiveCache
```

**Sources:** [api/src/modules/files/files.routes.ts:1-149](), [api/src/modules/files/files.controller.ts:1-337](), [api/src/services/file.service.ts:1-474]()

---

## API Endpoints Reference

| Method | Endpoint | Operation ID | Description |
|--------|----------|--------------|-------------|
| `POST` | `/sessions/:sessionId/files` | `upload_file` | Upload a file via binary data or URL |
| `HEAD` | `/sessions/:sessionId/files/*` | `head_file` | Get file metadata without downloading |
| `GET` | `/sessions/:sessionId/files/*` | `download_file` | Download a specific file |
| `GET` | `/sessions/:sessionId/files` | `list_files` | List all files in the session |
| `DELETE` | `/sessions/:sessionId/files/*` | `delete_file` | Delete a specific file |
| `DELETE` | `/sessions/:sessionId/files` | `delete_all_files` | Delete all files in the session |
| `GET` | `/sessions/:sessionId/files.zip` | `download_archive` | Download all files as a zip archive |

**Sources:** [api/src/modules/files/files.routes.ts:18-146]()

---

## File Upload

### Multipart Form Data

File uploads use `multipart/form-data` encoding with two fields:

- **`file`** (required): Either binary file data or a URL string to download from.
- **`path`** (optional): Destination path in the session's file storage.

```mermaid
graph TB
    Request["POST /sessions/:sessionId/files<br/>Content-Type: multipart/form-data"]
    
    subgraph "Multipart Processing"
        MultipartCheck["request.isMultipart()"]
        ParseParts["Iterate request.parts()"]
        FileField["field: 'file'<br/>type: 'file' or 'field'"]
        PathField["field: 'path'<br/>type: 'field'"]
    end
    
    subgraph "File Handling"
        BinaryUpload["Binary Upload<br/>Write to temp file<br/>/tmp/upload_uuid"]
        URLDownload["URL Download<br/>createStreamFromUrl()<br/>http.get() or https.get()"]
    end
    
    subgraph "Path Resolution"
        PathProvided{"path provided?"}
        ValidatePath["validatePath()<br/>Check for:<br/>- Absolute paths<br/>- '..' traversal<br/>- Null bytes"]
        GenerateUUID["Generate randomUUID()"]
        UsePath["Use provided path"]
    end
    
    subgraph "Storage"
        SaveFile["FileService.saveFile()<br/>getSafeFilePath()<br/>mkdir parent dir<br/>writeFile"]
        FileSystem["File System<br/>/files/..."]
        CleanupTemp["Delete temp file<br/>unlink /tmp/upload_uuid"]
    end
    
    Response["200 OK<br/>{ path, size, lastModified }"]
    
    Request --> MultipartCheck
    MultipartCheck -->|true| ParseParts
    MultipartCheck -->|false| Error400["400 Bad Request"]
    
    ParseParts --> FileField
    ParseParts --> PathField
    
    FileField -->|type: file| BinaryUpload
    FileField -->|type: field| URLDownload
    
    BinaryUpload --> PathProvided
    URLDownload --> PathProvided
    
    PathProvided -->|yes| ValidatePath
    PathProvided -->|no| GenerateUUID
    
    ValidatePath -->|valid| UsePath
    ValidatePath -->|invalid| Error400b["400 Bad Request<br/>Invalid path"]
    
    GenerateUUID --> SaveFile
    UsePath --> SaveFile
    
    SaveFile --> FileSystem
    SaveFile --> CleanupTemp
    
    CleanupTemp --> Response
```

**Sources:** [api/src/modules/files/files.controller.ts:41-157](), [api/src/modules/files/files.routes.ts:18-41]()

### Binary File Upload

When uploading binary file data, the controller writes the multipart stream to a temporary file in `/tmp/upload_${uuid}`, then reads it back as a stream for the `FileService`:

```typescript
// Implementation details from handleFileUpload
tempFilePath = path.join(tmpdir(), `upload_${uuidv4()}`);
const writeStream = fs.createWriteStream(tempFilePath);
await pipeline(file.file, writeStream);

// Then read back and save
const readStream = fs.createReadStream(tempFilePath);
saveFileResult = await this.fileService.saveFile({
  filePath: finalPath,
  stream: readStream,
});
```

**Sources:** [api/src/modules/files/files.controller.ts:67-114]()

### URL Download

When the `file` field contains a URL string instead of binary data, the controller downloads the file using Node.js's `http` or `https` modules via `createStreamFromUrl()`:

```typescript
// Implementation details from createStreamFromUrl
const protocol = url.startsWith("https") ? https : http;
protocol.get(url, (response) => {
  if (response.statusCode !== 200) {
    return reject(new Error(`Failed to fetch file: ${response.statusCode}`));
  }
  // ... extract name and resolve stream
});
```

**Sources:** [api/src/modules/files/files.controller.ts:115-136](), [api/src/modules/files/files.controller.ts:159-191]()

### Path Validation

The `validatePath()` method enforces security constraints on file paths to prevent directory traversal attacks:

| Check | Rule | Reason |
|-------|------|--------|
| Absolute paths | `path.isAbsolute()` must return `false` | Prevents writing outside base directory |
| Parent directory | No `..` sequences allowed | Prevents traversal attacks |
| Null bytes | No `\0` characters allowed | Prevents null byte injection |
| Normalized path | `path.normalize()` must not start with `..` | Catches additional traversal attempts |

**Sources:** [api/src/modules/files/files.controller.ts:20-39]()

### File Size Limits

The multipart parser enforces a configurable maximum file size per session, defaulting to 100MB:

```typescript
// From files.routes.ts
await server.register(fastifyMultipart, {
  limits: {
    fileSize: server.steelBrowserConfig.fileStorage?.maxSizePerSession ?? 100 * MB,
  },
  attachFieldsToBody: false,
});
```

**Sources:** [api/src/modules/files/files.routes.ts:11-16]()

---

## File Download

### Single File Download

The `GET /sessions/:sessionId/files/*` endpoint serves individual files with appropriate headers:

```mermaid
graph LR
    Request["GET /sessions/:sessionId/files/path/to/file.pdf"]
    Controller["handleFileDownload()"]
    Service["FileService.downloadFile()"]
    GetSafePath["getSafeFilePath()<br/>Validate path is within baseFilesPath"]
    StatFile["fs.promises.stat()<br/>Verify file exists and is a file"]
    CreateStream["fs.createReadStream()"]
    
    subgraph "Response Headers"
        ContentType["Content-Type<br/>mime.lookup(path)"]
        ContentLength["Content-Length<br/>stats.size"]
        ContentDisposition["Content-Disposition<br/>attachment; filename=..."]
        LastModified["Last-Modified<br/>stats.mtime"]
    end
    
    Stream["Stream file to response"]
    
    Request --> Controller
    Controller --> Service
    Service --> GetSafePath
    GetSafePath --> StatFile
    StatFile --> CreateStream
    CreateStream --> ContentType
    CreateStream --> ContentLength
    CreateStream --> ContentDisposition
    CreateStream --> LastModified
    ContentType --> Stream
    ContentLength --> Stream
    ContentDisposition --> Stream
    LastModified --> Stream
```

**Sources:** [api/src/modules/files/files.controller.ts:193-216](), [api/src/services/file.service.ts:149-178]()

### HEAD Request Support

The `HEAD /sessions/:sessionId/files/*` endpoint returns the same headers as GET but without the file body, allowing clients to check file existence and metadata efficiently via `fileService.getFile()`:

**Sources:** [api/src/modules/files/files.controller.ts:218-236](), [api/src/modules/files/files.routes.ts:43-55]()

---

## File Listing

The `GET /sessions/:sessionId/files` endpoint recursively lists all files in the session's storage directory using `fileService.listFiles()`:

```typescript
// Response format (Zod schema: MultipleFiles)
{
  "data": [
    {
      "path": "document.pdf",
      "size": 1048576,
      "lastModified": "2024-01-15T10:30:00.000Z"
    }
  ]
}
```

Files are sorted by `lastModified` in descending order (newest first).

**Sources:** [api/src/modules/files/files.controller.ts:238-259](), [api/src/services/file.service.ts:203-250](), [api/src/modules/files/files.schema.ts:14-16]()

---

## File Deletion

### Single File Deletion

The `DELETE /sessions/:sessionId/files/*` endpoint deletes a specific file via `fileService.deleteFile()`:

```mermaid
graph TB
    Request["DELETE /sessions/:sessionId/files/path/to/file.pdf"]
    Controller["handleFileDelete()"]
    Service["FileService.deleteFile()"]
    SafePath["getSafeFilePath()"]
    Exists["exists() check"]
    StatCheck["fs.promises.stat()<br/>Verify is file"]
    Unlink["fs.promises.unlink()"]
    TriggerArchive["debouncedCreateArchive()"]
    Response["204 No Content"]
    
    Request --> Controller
    Controller --> Service
    Service --> SafePath
    SafePath --> Exists
    Exists -->|true| StatCheck
    Exists -->|false| Skip["Log and skip"]
    StatCheck -->|is file| Unlink
    StatCheck -->|not file| Warn["Log warning and skip"]
    Unlink --> TriggerArchive
    TriggerArchive --> Response
    Skip --> Response
    Warn --> Response
```

**Sources:** [api/src/modules/files/files.controller.ts:261-275](), [api/src/services/file.service.ts:252-278]()

### Bulk Deletion

The `DELETE /sessions/:sessionId/files` endpoint removes all files and resets the session's file storage via `fileService.cleanupFiles()`:

**Process:**
1. Cancel any pending archive creation operations.
2. Delete the prebuilt archive file (`/tmp/.steel/files.zip`).
3. Delete all temporary archive files (`files-*.zip.tmp`).
4. Recursively remove all files from the base files directory.
5. Trigger creation of a new empty archive.

**Sources:** [api/src/modules/files/files.controller.ts:277-289](), [api/src/services/file.service.ts:280-329]()

---

## Archive Download

The `GET /sessions/:sessionId/files.zip` endpoint serves a pre-generated zip archive containing all session files. The archive is automatically maintained by the `FileService`'s file watching mechanism.

### Endpoint Behavior

```mermaid
graph TB
    Request["GET /sessions/:sessionId/files.zip"]
    GetPath["fileService.getPrebuiltArchivePath()"]
    CheckArchive["fs.promises.stat(prebuiltArchivePath)"]
    
    ArchiveExists{"Archive exists<br/>and is file?"}
    
    subgraph "Serve Prebuilt Archive"
        ReadStream["fs.createReadStream(prebuiltArchivePath)"]
        SetHeaders["Content-Type: application/zip<br/>Content-Disposition: attachment<br/>Content-Length: stats.size<br/>Last-Modified: stats.mtime"]
        StreamResponse["Stream archive to client"]
    end
    
    subgraph "Generate Empty Archive"
        EmptyArchive["archiver('zip')<br/>No files added"]
        Finalize["archive.finalize()"]
        StreamEmpty["Stream to response"]
    end
    
    Request --> GetPath
    GetPath --> CheckArchive
    CheckArchive --> ArchiveExists
    
    ArchiveExists -->|yes| ReadStream
    ReadStream --> SetHeaders
    SetHeaders --> StreamResponse
    
    ArchiveExists -->|no| EmptyArchive
    EmptyArchive --> Finalize
    Finalize --> StreamEmpty
```

**Sources:** [api/src/modules/files/files.controller.ts:291-335](), [api/src/modules/files/files.routes.ts:133-145]()

### Archive Path

The prebuilt archive is stored at `/tmp/.steel/files.zip`. This location is initialized in the `FileService` constructor:

**Sources:** [api/src/services/file.service.ts:26-30](), [api/src/services/file.service.ts:335-337]()

---

## Request/Response Schemas

The File API uses Zod schemas for request/response validation, which are also used to generate OpenAPI documentation.

### FileUploadRequest
- `file`: The file to upload (binary) or URL string to download from.
- `path`: (Optional) Path to the file in the storage system.

**Sources:** [api/src/modules/files/files.schema.ts:3-6]()

### FileDetails
- `path`: Path to the file in the storage system.
- `size`: Size of the file in bytes.
- `lastModified`: Timestamp when the file was last updated.

**Sources:** [api/src/modules/files/files.schema.ts:8-12]()

### MultipleFiles
- `data`: Array of `FileDetails` for the current page.

**Sources:** [api/src/modules/files/files.schema.ts:14-16]()

---

## Security Considerations

### Path Safety

The `FileService` implements multiple layers of path validation:

1. **Relative path enforcement**: `getSafeFilePath()` rejects absolute paths.
2. **Base path containment**: Resolved paths must start with `baseFilesPath`.
3. **Traversal prevention**: Paths containing `..` are rejected.
4. **Normalization**: Paths are normalized before validation.

```typescript
// From FileService.getSafeFilePath()
const resolvedPath = resolve(this.baseFilesPath, relativePath);
if (
  !resolvedPath.startsWith(this.baseFilesPath + path.sep) &&
  resolvedPath !== this.baseFilesPath
) {
  throw new Error("Invalid path");
}
```

**Sources:** [api/src/services/file.service.ts:87-96]()

### File System Isolation

Each session's files are stored in the base files directory. In production, this is `/files`; in development, it's a directory in `tmpdir()`:

**Sources:** [api/src/services/file.service.ts:27-28]()

### Error Handling

The controller catches and logs errors, returning appropriate HTTP status codes:

- **400 Bad Request**: Invalid path, missing file, or request not being multipart.
- **500 Internal Server Error**: File system errors or stream failures.

**Sources:** [api/src/modules/files/files.controller.ts:49-54](), [api/src/modules/files/files.controller.ts:150-156]()

---

## Plugin Registration

The `FileService` is registered as a Fastify decorator via the `file-storage` plugin, making it available throughout the application:

```typescript
// From api/src/plugins/file-storage.ts
const fileStoragePlugin: FastifyPluginAsync = async (fastify, _options) => {
  fastify.log.info("Registering file service");
  fastify.decorate("fileService", FileService.getInstance());
};
```

This ensures a single `FileService` instance handles all file operations across the application.

**Sources:** [api/src/plugins/file-storage.ts:1-10]()

---

# Page: Archive Management

# Archive Management

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [api/src/modules/files/files.controller.ts](api/src/modules/files/files.controller.ts)
- [api/src/modules/files/files.routes.ts](api/src/modules/files/files.routes.ts)
- [api/src/modules/files/files.schema.ts](api/src/modules/files/files.schema.ts)
- [api/src/plugins/file-storage.ts](api/src/plugins/file-storage.ts)
- [api/src/services/file.service.ts](api/src/services/file.service.ts)

</details>



This page documents the automatic archive generation system in steel-browser, which maintains a continuously updated zip archive of all session files. When files are added, modified, or deleted, the system automatically regenerates a prebuilt archive that can be downloaded instantly via the archive endpoint. For individual file operations (upload, download, delete), see [File API](#7.1).

---

## Overview

The archive management system provides bulk download functionality for all files in a session. Rather than creating archives on-demand (which would be slow for large file sets), the system maintains a prebuilt archive that is automatically regenerated whenever the file system changes.

**Key Components:**

| Component | Purpose |
|-----------|---------|
| `FileService` | Singleton service managing file storage and archive generation |
| `chokidar.FSWatcher` | File system watcher monitoring for changes |
| `archiver` | Library for creating zip archives |
| Debounce mechanism | Prevents excessive archive regeneration during rapid file changes |
| Prebuilt archive | Continuously maintained zip file at `/tmp/.steel/files.zip` |

Sources: [api/src/services/file.service.ts:16-38]()

---

## Architecture

### Archive Management System Architecture

```mermaid
graph TB
    subgraph "Client Layer"
        Client["HTTP Client"]
    end
    
    subgraph "API Layer"
        Route["GET /sessions/:sessionId/files.zip"]
        Controller["FilesController.handleDownloadArchive()"]
    end
    
    subgraph "Service Layer"
        FileService["FileService (Singleton)"]
        GetArchivePath["getPrebuiltArchivePath()"]
        CreateArchive["_createArchive()"]
        DebouncedCreate["debouncedCreateArchive"]
    end
    
    subgraph "File System Monitoring"
        Watcher["chokidar.FSWatcher"]
        HandleAdd["handleFileAdd()"]
        HandleDelete["handleFileDelete()"]
        HandleDirChange["handleDirChange()"]
    end
    
    subgraph "File System"
        BaseFilesPath["/files or tmpdir()/files"]
        PrebuiltArchive["/tmp/.steel/files.zip"]
        TempArchive["/tmp/.steel/files-{timestamp}.zip.tmp"]
    end
    
    subgraph "Archive Creation"
        Archiver["archiver library"]
        WriteStream["fs.createWriteStream()"]
    end
    
    Client -->|"HTTP GET"| Route
    Route --> Controller
    Controller --> GetArchivePath
    GetArchivePath --> PrebuiltArchive
    Controller -->|"Serves if exists"| PrebuiltArchive
    
    Watcher -->|"Monitors"| BaseFilesPath
    Watcher -->|"'add' event"| HandleAdd
    Watcher -->|"'unlink' event"| HandleDelete
    Watcher -->|"'addDir'/'unlinkDir' events"| HandleDirChange
    
    HandleAdd --> DebouncedCreate
    HandleDelete --> DebouncedCreate
    HandleDirChange --> DebouncedCreate
    
    DebouncedCreate -->|"After 500ms delay"| CreateArchive
    
    CreateArchive --> Archiver
    CreateArchive --> WriteStream
    WriteStream --> TempArchive
    TempArchive -->|"fs.rename()"| PrebuiltArchive
    
    FileService --> Watcher
    FileService --> CreateArchive
```

Sources: [api/src/services/file.service.ts:16-37](), [api/src/modules/files/files.controller.ts:291-335]()

---

## File Watching System

The archive management system uses `chokidar` to monitor the file system for changes. The watcher is initialized when the `FileService` singleton is created and runs continuously throughout the application lifecycle.

### Watcher Configuration

The file watcher is configured in `initFileWatcher()` with the following options:

| Option | Value | Purpose |
|--------|-------|---------|
| `ignored` | `/(^|[\/\\])\../` | Ignore hidden files (starting with `.`) |
| `persistent` | `true` | Keep process running while watching |
| `ignoreInitial` | `false` | Trigger events for existing files on startup |
| `awaitWriteFinish.stabilityThreshold` | `500ms` | Wait 500ms for file writes to stabilize |
| `awaitWriteFinish.pollInterval` | `100ms` | Poll every 100ms to check if write is complete |
| `depth` | `undefined` | Watch all subdirectories recursively |

Sources: [api/src/services/file.service.ts:61-72]()

### File System Event Flow

```mermaid
graph LR
    subgraph "File System Changes"
        FileAdd["File Added"]
        FileDelete["File Deleted"]
        DirAdd["Directory Added"]
        DirDelete["Directory Deleted"]
    end
    
    subgraph "Chokidar Events"
        AddEvent["'add' event"]
        UnlinkEvent["'unlink' event"]
        AddDirEvent["'addDir' event"]
        UnlinkDirEvent["'unlinkDir' event"]
        ErrorEvent["'error' event"]
        ReadyEvent["'ready' event"]
    end
    
    subgraph "Event Handlers"
        HandleFileAdd["handleFileAdd(filePath)"]
        HandleFileDelete["handleFileDelete(filePath)"]
        HandleDirChange["handleDirChange(filePath)"]
        LogError["console.error()"]
        InitialScan["Initial scan complete"]
    end
    
    subgraph "Archive Trigger"
        Debounced["debouncedCreateArchive()"]
    end
    
    FileAdd --> AddEvent
    FileDelete --> UnlinkEvent
    DirAdd --> AddDirEvent
    DirDelete --> UnlinkDirEvent
    
    AddEvent --> HandleFileAdd
    UnlinkEvent --> HandleFileDelete
    AddDirEvent --> HandleDirChange
    UnlinkDirEvent --> HandleDirChange
    ErrorEvent --> LogError
    ReadyEvent --> InitialScan
    
    HandleFileAdd --> Debounced
    HandleFileDelete --> Debounced
    HandleDirChange --> Debounced
    InitialScan --> Debounced
```

Sources: [api/src/services/file.service.ts:47-85]()

### Event Handlers

Each event handler logs the change and triggers the debounced archive creation:

```typescript
// Implementation of event handlers
private async handleFileAdd(filePath: string) {
  console.log(`[FileService] File added detected: ${filePath}`);
  this.debouncedCreateArchive();
}

private handleFileDelete(filePath: string) {
  console.log(`[FileService] File deleted detected: ${filePath}`);
  this.debouncedCreateArchive();
}

private handleDirChange(filePath: string) {
  console.log(`[FileService] Directory change detected: ${filePath}`);
  this.debouncedCreateArchive();
}
```

Sources: [api/src/services/file.service.ts:47-60]()

---

## Automatic Archive Generation

The archive is automatically regenerated whenever files change, using a debounced approach to handle rapid successive changes efficiently.

### Debouncing Mechanism

The `debouncedCreateArchive` function is created using lodash's `debounce` utility with a 500ms delay:

| Property | Value | Purpose |
|----------|-------|---------|
| `archiveDebounceTime` | `500` | Milliseconds to wait before creating archive |
| `debouncedCreateArchive` | `DebouncedFunc<() => Promise<string \| null>>` | Debounced wrapper around `_createArchive` |

This means:
- If multiple file changes occur within 500ms, only one archive creation is triggered
- The archive creation waits until file operations have stabilized
- Prevents system load from excessive archive regeneration

Sources: [api/src/services/file.service.ts:24-35]()

### Archive Creation Process

```mermaid
graph TB
    Start["_createArchive() invoked"]
    CheckArchiving{"isArchiving === true?"}
    SetFlag["Set isArchiving = true"]
    CreateTemp["Create temporary path<br/>/tmp/.steel/files-{timestamp}.zip.tmp"]
    CreateDir["Ensure /tmp/.steel directory exists"]
    CreateStream["Create fs.WriteStream to temp file"]
    CreateArchiver["Create archiver('zip', {level: 9})"]
    CheckBaseDir{"Base directory exists?"}
    CheckEmpty{"Directory empty?"}
    AddFiles["archive.directory(baseFilesPath, false)"]
    EmptyArchive["Create empty archive"]
    Pipe["Pipe archive to output stream"]
    Finalize["archive.finalize()"]
    StreamClose["Wait for 'close' event"]
    DeleteOld["Delete existing /tmp/.steel/files.zip if exists"]
    Rename["Rename temp file to files.zip"]
    Success["Return archive path"]
    Cleanup["Set isArchiving = false<br/>Delete temp file if error"]
    
    Start --> CheckArchiving
    CheckArchiving -->|"Yes"| LogWarning["Log warning about concurrent archiving"]
    CheckArchiving -->|"No"| SetFlag
    LogWarning --> SetFlag
    SetFlag --> CreateTemp
    CreateTemp --> CreateDir
    CreateDir --> CreateStream
    CreateStream --> CreateArchiver
    CreateArchiver --> CheckBaseDir
    CheckBaseDir -->|"No"| EmptyArchive
    CheckBaseDir -->|"Yes"| CheckEmpty
    CheckEmpty -->|"Yes"| EmptyArchive
    CheckEmpty -->|"No"| AddFiles
    AddFiles --> Pipe
    EmptyArchive --> Pipe
    Pipe --> Finalize
    Finalize --> StreamClose
    StreamClose --> DeleteOld
    DeleteOld --> Rename
    Rename --> Success
    Success --> Cleanup
```

Sources: [api/src/services/file.service.ts:339-472]()

### Archive File Paths

The system uses specific file paths for archive management:

| Path Variable | Value | Purpose |
|---------------|-------|---------|
| `prebuiltArchiveDir` | `/tmp/.steel` | Directory for archive storage |
| `prebuiltArchivePath` | `/tmp/.steel/files.zip` | Final archive location |
| `tempArchivePath` | `/tmp/.steel/files-{timestamp}.zip.tmp` | Temporary file during creation |

Sources: [api/src/services/file.service.ts:29-30](), [api/src/services/file.service.ts:350]()

### Concurrency Handling

The `_createArchive()` method includes protection against concurrent archive creation:

```typescript
if (this.isArchiving) {
  console.warn(
    `[_createArchive] Warning: Archiving process initiated while another is already in progress.`
  );
}
this.isArchiving = true;
```

While the warning is logged, the method continues execution. This is acceptable because the debounce mechanism prevents most concurrent calls and the final rename operation is atomic.

Sources: [api/src/services/file.service.ts:341-347]()

### Error Handling

The archive creation process includes comprehensive error handling. Output stream errors trigger cleanup and reject the promise, while archive warnings (e.g., ENOENT for missing files) are logged but don't fail the operation.

Sources: [api/src/services/file.service.ts:368-391](), [api/src/services/file.service.ts:415-439]()

---

## Archive Download API

### Endpoint

**Route:** `GET /sessions/:sessionId/files.zip`

**Operation ID:** `download_archive`

**Summary:** Download all files from the session as a zip archive

Sources: [api/src/modules/files/files.routes.ts:133-145]()

### Request/Response Flow

```mermaid
sequenceDiagram
    participant Client
    participant Route as "/sessions/:id/files.zip"
    participant Controller as "FilesController"
    participant FileService
    participant FS as "File System"
    
    Client->>Route: GET /sessions/:id/files.zip
    Route->>Controller: handleDownloadArchive(request, reply)
    Controller->>FileService: getPrebuiltArchivePath()
    FileService-->>Controller: "/tmp/.steel/files.zip"
    
    Controller->>FS: fs.promises.stat(prebuiltArchivePath)
    
    alt Prebuilt archive exists
        FS-->>Controller: stats (file metadata)
        Controller->>FS: fs.createReadStream(prebuiltArchivePath)
        FS-->>Controller: ReadStream
        Controller->>Client: Stream archive with headers<br/>Content-Type: application/zip<br/>Content-Disposition: attachment<br/>Content-Length: {size}<br/>Last-Modified: {mtime}
    else Archive doesn't exist or is not a file
        Controller->>Controller: Create empty archiver
        Controller->>Client: Stream empty archive<br/>Content-Type: application/zip<br/>Content-Disposition: attachment
    end
```

Sources: [api/src/modules/files/files.controller.ts:291-335]()

### Response Headers

The endpoint sets headers for zip format, filename disposition, size, and modification time.

Sources: [api/src/modules/files/files.controller.ts:304-307]()

### Empty Archive Handling

If the prebuilt archive doesn't exist, the endpoint generates an empty zip archive on-the-fly using `archiver`.

Sources: [api/src/modules/files/files.controller.ts:313-320]()

---

## Integration with File Operations

The archive management system integrates with all file operations through the file watcher and explicit triggers in `FileService` methods.

### Automatic Regeneration Triggers

| File Operation | Method | Archive Trigger |
|----------------|--------|-----------------|
| File Upload | `saveFile()` | Calls `debouncedCreateArchive()` after successful save |
| File Delete | `deleteFile()` | Calls `debouncedCreateArchive()` after successful deletion |
| Cleanup All Files | `cleanupFiles()` | Cancels pending debounced call, then explicitly calls `debouncedCreateArchive()` |
| File System Watch | Event handlers | Each file/directory change triggers `debouncedCreateArchive()` |

Sources: [api/src/services/file.service.ts:131](), [api/src/services/file.service.ts:271](), [api/src/services/file.service.ts:328]()

---

## Performance Considerations

### Compression Level

The archive is created with maximum compression (`zlib: { level: 9 }`) to prioritize smaller file sizes.

Sources: [api/src/services/file.service.ts:365]()

### Atomic File Operations

The archive creation uses atomic file operations (writing to `.tmp` then renaming) to prevent serving partially-written archives.

Sources: [api/src/services/file.service.ts:350-404]()

---

## Code Entity Reference

### FileService Class

**Location:** [api/src/services/file.service.ts:16-473]()

**Key Properties:**

| Property | Type | Description |
|----------|------|-------------|
| `baseFilesPath` | `string` | Base directory for file storage |
| `prebuiltArchivePath` | `string` | Full path to prebuilt archive (`/tmp/.steel/files.zip`) |
| `isArchiving` | `boolean` | Flag indicating archive creation in progress |
| `debouncedCreateArchive` | `DebouncedFunc<...>` | Debounced wrapper for `_createArchive()` |

**Key Methods:**

| Method | Return Type | Description |
|--------|-------------|-------------|
| `getInstance()` | `FileService` | Returns singleton instance |
| `_createArchive()` | `Promise<string \| null>` | Creates zip archive at prebuilt path |
| `getPrebuiltArchivePath()` | `Promise<string>` | Returns path to prebuilt archive |

Sources: [api/src/services/file.service.ts:16-473]()

### FilesController Class

**Location:** [api/src/modules/files/files.controller.ts:17-336]()

Sources: [api/src/modules/files/files.controller.ts:291-335]()

---

# Page: Browser Automation Features

# Browser Automation Features

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [api/src/modules/actions/actions.controller.ts](api/src/modules/actions/actions.controller.ts)
- [api/src/modules/actions/actions.routes.ts](api/src/modules/actions/actions.routes.ts)
- [api/src/modules/actions/actions.schema.ts](api/src/modules/actions/actions.schema.ts)
- [api/src/services/cdp/cdp.service.ts](api/src/services/cdp/cdp.service.ts)
- [api/src/services/cdp/plugins/core/base-plugin.ts](api/src/services/cdp/plugins/core/base-plugin.ts)
- [api/src/services/cdp/plugins/core/plugin-manager.ts](api/src/services/cdp/plugins/core/plugin-manager.ts)
- [api/src/services/selenium.service.ts](api/src/services/selenium.service.ts)
- [api/src/utils/passthough-proxy.ts](api/src/utils/passthough-proxy.ts)
- [api/src/utils/proxy.ts](api/src/utils/proxy.ts)

</details>



## Purpose and Scope

This page provides an overview of the browser automation capabilities in steel-browser. It covers the core automation mechanisms (Chrome DevTools Protocol and Selenium WebDriver), anti-detection features, request interception, and extension support. For detailed information on specific features, see:
- Session lifecycle management: [Browser Sessions](#4)
- Quick action APIs for scraping/screenshots: [Quick Actions API](#5)
- Plugin extensibility: [Plugin System](#9)

## Core Automation Architecture

steel-browser provides two automation modes orchestrated by `SessionService`:

| Mode | Service | Protocol | Use Case |
|------|---------|----------|----------|
| **CDP** (default) | `CDPService` | Chrome DevTools Protocol | Full-featured automation with fingerprinting, plugins, instrumentation |
| **Selenium** | `SeleniumService` | WebDriver Protocol | Compatibility with existing Selenium/WebDriver scripts |

### Session Service Orchestration

```mermaid
graph TB
    SessionService["SessionService"]
    CDPService["CDPService<br/>api/src/services/cdp/cdp.service.ts"]
    SeleniumService["SeleniumService<br/>api/src/services/selenium.service.ts"]
    Browser["Chrome/Chromium Process"]
    ProxyServer["ProxyServer<br/>api/src/utils/proxy.ts"]
    
    SessionService -->|"isSelenium=true"| SeleniumService
    SessionService -->|"isSelenium=false (default)"| CDPService
    SessionService -->|"manages proxy"| ProxyServer
    
    CDPService -->|"launches & controls via CDP"| Browser
    SeleniumService -->|"controls via WebDriver"| Browser
    
    ProxyServer -->|"routes traffic"| Browser
```

**Diagram: Session Service Architecture**

The `SessionService` acts as the orchestration layer, selecting the appropriate automation backend. While `CDPService` uses `puppeteer-core` to manage the browser via CDP [api/src/services/cdp/cdp.service.ts:24](), `SeleniumService` spawns a standalone Selenium server to interface with the browser via WebDriver [api/src/services/selenium.service.ts:40-44]().

Sources: [api/src/services/cdp/cdp.service.ts:83-182](), [api/src/services/selenium.service.ts:8-18]()

## Browser Launch Configuration

Browser sessions are configured via `BrowserLauncherOptions`, which provides extensive control over browser behavior:

```mermaid
graph LR
    BrowserLauncherOptions["BrowserLauncherOptions"]
    Options["options<br/>BrowserServerOptions"]
    Context["sessionContext<br/>cookies, localStorage, etc"]
    Fingerprint["fingerprint<br/>BrowserFingerprintWithHeaders"]
    OptimizeBandwidth["optimizeBandwidth<br/>OptimizeBandwidthOptions"]
    Extensions["extensions<br/>string[]"]
    
    BrowserLauncherOptions --> Options
    BrowserLauncherOptions --> Context
    BrowserLauncherOptions --> Fingerprint
    BrowserLauncherOptions --> OptimizeBandwidth
    BrowserLauncherOptions --> Extensions
    
    Options --> headless["headless: boolean"]
    Options --> proxyUrl["proxyUrl: string"]
    Options --> args["args: string[]"]
```

**Diagram: Browser Launch Configuration Structure**

### Key Configuration Options

| Option | Type | Purpose |
|--------|------|---------|
| `options.headless` | `boolean` | Run browser in headless mode [api/src/services/cdp/cdp.service.ts:152]() |
| `options.proxyUrl` | `string` | Upstream proxy URL for routing traffic [api/src/utils/proxy.ts:48-49]() |
| `blockAds` | `boolean` | Block requests to known ad networks [api/src/services/cdp/cdp.service.ts:156]() |
| `timezone` | `string` | Override browser timezone [api/src/services/cdp/cdp.service.ts:159]() |
| `userPreferences` | `object` | Chrome user preferences (e.g., PDF viewer settings) [api/src/services/cdp/cdp.service.ts:160-165]() |

Sources: [api/src/services/cdp/cdp.service.ts:150-167](), [api/src/utils/proxy.ts:22-51]()

## Browser Launch Process

The browser launch process in `CDPService` follows a structured sequence with comprehensive error handling:

```mermaid
graph TB
    Start["launch()"]
    PluginBrowserLaunch["pluginManager.onBrowserLaunch()"]
    GetPrimaryPage["Get primary page"]
    InjectContext["injectSessionContext()"]
    PluginReady["pluginManager.onBrowserReady()"]
    
    Start --> LaunchBrowser["puppeteer.launch()"]
    LaunchBrowser --> PluginBrowserLaunch
    PluginBrowserLaunch --> GetPrimaryPage
    GetPrimaryPage --> InjectContext
    InjectContext --> PluginReady
```

**Diagram: Browser Launch Sequence**

The `CDPService` utilizes a `PluginManager` to notify registered plugins at various stages of the lifecycle, such as `onBrowserLaunch` and `onBrowserReady` [api/src/services/cdp/plugins/core/plugin-manager.ts:96-118]().

Sources: [api/src/services/cdp/cdp.service.ts:169-180](), [api/src/services/cdp/plugins/core/plugin-manager.ts:54-118]()

## Target and Page Management

The `CDPService` handles browser targets (pages, workers, extensions) through event-driven lifecycle management:

```mermaid
graph TB
    Browser["Browser Instance"]
    TargetCreated["targetcreated event"]
    HandleNewTarget["handleNewTarget()"]
    PluginPageCreated["pluginManager.onPageCreated()"]
    SetupRequestInterception["page.setRequestInterception(true)"]
    
    Browser --> TargetCreated
    TargetCreated --> HandleNewTarget
    HandleNewTarget --> PluginPageCreated
    PluginPageCreated --> SetupRequestInterception
```

**Diagram: Target Lifecycle Management**

When a new page target is created, `CDPService` performs several setup tasks:
1. **Instrumentation**: Attaches `TargetInstrumentationManager` to capture logs and events [api/src/services/cdp/cdp.service.ts:177-180]().
2. **Plugin Notification**: Invokes `onPageCreated` for all active plugins [api/src/services/cdp/plugins/core/plugin-manager.ts:123-132]().
3. **Request Control**: Enables request interception to allow filtering of ads or specific resource types [api/src/services/cdp/cdp.service.ts:36-38]().

Sources: [api/src/services/cdp/cdp.service.ts:103-104](), [api/src/services/cdp/plugins/core/plugin-manager.ts:123-132]()

## Request Interception and Filtering

The system provides robust request filtering to optimize performance and security. The logic resides in `api/src/utils/requests.ts` and is applied during the page lifecycle.

| Feature | Function | Description |
|--------|----------|-------------|
| **Ad Blocking** | `isAdRequest()` | Blocks known tracking and advertisement domains [api/src/utils/requests.ts:32](). |
| **Media Blocking** | `isHeavyMediaRequest()` | Filters large video or audio files to save bandwidth [api/src/utils/requests.ts:33](). |
| **Host Blocking** | `isHostBlocked()` | Prevents navigation to specific blacklisted hostnames [api/src/utils/requests.ts:34](). |
| **Pattern Matching** | `isUrlMatchingPatterns()` | Blocks URLs based on regex or glob patterns [api/src/utils/requests.ts:35](). |

Sources: [api/src/services/cdp/cdp.service.ts:30-38](), [api/src/utils/requests.ts:30-38]()

## Browser Extensions

steel-browser supports loading Chrome extensions to enhance automation capabilities. Extension paths are resolved and passed to the browser during the launch phase [api/src/services/cdp/cdp.service.ts:47]().

- **Loading**: Extensions are specified in the `BrowserLauncherOptions` [api/src/services/cdp/cdp.service.ts:157]().
- **Default Extensions**: The system can be configured to load a set of default extensions for every session.

Sources: [api/src/services/cdp/cdp.service.ts:47](), [api/src/services/cdp/cdp.service.ts:157]()

## CDP Integration Details

For in-depth information on Chrome DevTools Protocol integration, page control, and browser events, see [CDP Integration](#8.1).

## Selenium WebDriver Support

The `SeleniumService` provides a compatibility layer for users migrating from traditional Selenium grids. It manages the lifecycle of the `selenium-server.jar` and provides the necessary connection URL [api/src/services/selenium.service.ts:40-45](). For more details, see [Selenium Support](#8.2).

## Anti-Detection Features

Stealth is a core component of the automation engine. The `CDPService` integrates `FingerprintGenerator` and `FingerprintInjector` to mask automation signatures [api/src/services/cdp/cdp.service.ts:4-9](). For detailed stealth configuration, see [Anti-Detection Features](#8.3).

## Request Interception & Filtering

For advanced details on how to configure ad-blocking and resource filtering, see [Request Interception & Filtering](#8.4).

## Browser Extensions

To learn how to package and deploy custom extensions within your sessions, see [Browser Extensions](#8.5).

---

# Page: CDP Integration

# CDP Integration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [api/src/modules/cdp/cdp.routes.ts](api/src/modules/cdp/cdp.routes.ts)
- [api/src/services/cdp/cdp.service.ts](api/src/services/cdp/cdp.service.ts)
- [api/src/services/cdp/instrumentation/cdp-events.ts](api/src/services/cdp/instrumentation/cdp-events.ts)
- [api/src/services/cdp/instrumentation/page-events.ts](api/src/services/cdp/instrumentation/page-events.ts)
- [api/src/services/cdp/instrumentation/target-manager.ts](api/src/services/cdp/instrumentation/target-manager.ts)
- [api/src/services/cdp/instrumentation/types.ts](api/src/services/cdp/instrumentation/types.ts)
- [api/src/services/cdp/plugins/core/base-plugin.ts](api/src/services/cdp/plugins/core/base-plugin.ts)
- [api/src/services/cdp/plugins/core/plugin-manager.ts](api/src/services/cdp/plugins/core/plugin-manager.ts)
- [api/src/types/enums.ts](api/src/types/enums.ts)

</details>



This document details how Steel Browser integrates with the Chrome DevTools Protocol (CDP), exposing direct browser control to external clients through WebSocket proxying and internal instrumentation for event tracking. CDP is Chrome's native protocol for browser automation, and Steel exposes it to enable integration with tools like Puppeteer, Playwright, and Chrome DevTools itself.

## Overview

Steel Browser runs a Chromium instance with CDP enabled on an internal port (9222) and proxies CDP WebSocket connections through a configurable external port (default 9223). This allows external automation tools and debuggers to connect directly to the browser while Steel manages the browser lifecycle, fingerprinting, and session state.

**CDP Integration Architecture**

```mermaid
graph TB
    subgraph "External Clients"
        Puppeteer["Puppeteer/Playwright"]
        DevTools["Chrome DevTools"]
        Debugger["Remote Debugger"]
    end
    
    subgraph "Steel Browser API Container"
        FastifyAPI["Fastify Server<br/>Port 3000"]
        CDPService["CDPService"]
        wsProxyServer["http-proxy<br/>WebSocket Proxy"]
        TargetManager["TargetInstrumentationManager"]
        
        FastifyAPI --> CDPService
        CDPService --> wsProxyServer
        CDPService --> TargetManager
    end
    
    subgraph "Browser Instance"
        Chrome["Chrome/Chromium<br/>Internal CDP Port 9222"]
        wsEndpoint["CDP WebSocket<br/>ws://localhost:9222/devtools/page/..."]
        
        Chrome --> wsEndpoint
    end
    
    Puppeteer -->|"WebSocket<br/>Port 9223"| wsProxyServer
    DevTools -->|"HTTP/WS<br/>Port 9223"| wsProxyServer
    Debugger -->|"WebSocket<br/>Port 9223"| wsProxyServer
    
    wsProxyServer -->|proxies to| wsEndpoint
    TargetManager -->|instrumentation via| wsEndpoint
```

The `CDPService` creates an `httpProxy` instance that forwards WebSocket connections from external clients to the browser's internal CDP endpoint. Simultaneously, it uses `TargetInstrumentationManager` to attach internal listeners for logging and event capture.

Sources: [api/src/services/cdp/cdp.service.ts:83-185](), [api/src/services/cdp/instrumentation/target-manager.ts:14-26]()

## CDPService Architecture

The `CDPService` class manages the browser lifecycle and exposes CDP access through WebSocket proxying. It maintains a reference to the browser instance, the WebSocket endpoint, and an HTTP proxy server for routing external connections.

**CDPService Core Components**

```mermaid
classDiagram
    class CDPService {
        -browserInstance: Browser
        -wsEndpoint: string
        -wsProxyServer: httpProxy
        -pluginManager: PluginManager
        -targetInstrumentationManager: TargetInstrumentationManager
        -instrumentationLogger: BrowserLogger
        
        +setProxyWebSocketHandler(handler)
        +getBrowserInstance()
        +getInstrumentationLogger()
        +launch(config, retryOptions)
        +shutdown()
    }
    
    class PluginManager {
        -plugins: Map~string, BasePlugin~
        +register(plugin)
        +onPageCreated(page)
        +onBrowserLaunch(browser)
    }
    
    class TargetInstrumentationManager {
        -cdpSessions: Map~string, CDPSession~
        +attach(target, type)
        +detach(targetId)
    }
    
    CDPService --> PluginManager: pluginManager
    CDPService --> TargetInstrumentationManager: targetInstrumentationManager
```

The service is initialized with a `PluginManager` for lifecycle hooks and a `TargetInstrumentationManager` for monitoring targets. It also initializes an `instrumentationLogger` that emits logs via the `EmitEvent.Log` event.

Sources: [api/src/services/cdp/cdp.service.ts:83-185](), [api/src/services/cdp/plugins/core/plugin-manager.ts:7-16](), [api/src/services/cdp/instrumentation/target-manager.ts:14-26]()

## Target Instrumentation & Events

Steel uses a multi-layered instrumentation strategy to capture browser activity. When a new target (page, worker, or extension) is created, the `TargetInstrumentationManager` attaches listeners to specific CDP domains.

### Domain Enablement
The system enables different CDP domains based on the `TargetType`:
- **PAGE / BACKGROUND_PAGE**: Enables `Runtime`, `Log`, and `Network`. [api/src/services/cdp/instrumentation/target-manager.ts:147-152]()
- **WORKERS**: Enables `Runtime` and `Log`. [api/src/services/cdp/instrumentation/target-manager.ts:154-161]()
- **EXTENSIONS**: Enables `Network` even for service workers. [api/src/services/cdp/instrumentation/target-manager.ts:158-160]()

### Event Mapping
Events captured from CDP are mapped to internal `BrowserEventType` definitions:

| CDP Event / Source | Internal Event Type | Description |
|-------------------|---------------------|-------------|
| `Network.requestWillBeSent` | `BrowserEventType.Request` | Outgoing HTTP requests |
| `Network.responseReceived` | `BrowserEventType.Response` | Incoming HTTP responses |
| `Network.loadingFinished` | `BrowserEventType.ResponseBody` | Captures response bodies (if enabled) |
| `Runtime.consoleAPICalled` | `BrowserEventType.Console` | Browser console logs |
| `Runtime.exceptionThrown` | `BrowserEventType.PageError` | Uncaught JS exceptions |
| `framenavigated` | `BrowserEventType.Navigation` | Page URL changes |

Sources: [api/src/services/cdp/instrumentation/page-events.ts:24-202](), [api/src/types/enums.ts:10-25](), [api/src/services/cdp/instrumentation/types.ts:4-115]()

## Plugin System Lifecycle

The `CDPService` integrates a plugin system that hooks into various stages of the CDP lifecycle. Plugins extend `BasePlugin` and are notified by the `PluginManager`.

**Plugin Lifecycle Flow**

```mermaid
sequenceDiagram
    participant S as CDPService
    participant PM as PluginManager
    participant P as BasePlugin
    
    S->>PM: onSessionStart(config)
    PM->>P: onSessionStart()
    
    S->>S: Launch Browser
    S->>PM: onBrowserLaunch(browser)
    PM->>P: onBrowserLaunch()
    
    Note over S,P: Target Created (Page)
    
    S->>PM: onPageCreated(page)
    PM->>P: onPageCreated()
    
    S->>PM: onPageNavigate(page)
    PM->>P: onPageNavigate()
    
    S->>S: Shutdown
    S->>PM: onShutdown(reason)
    PM->>P: onShutdown()
```

Plugins can react to events like `onPageCreated` or `onBrowserLaunch` to perform tasks like ad-blocking, custom header injection, or fingerprinting.

Sources: [api/src/services/cdp/plugins/core/base-plugin.ts:27-55](), [api/src/services/cdp/plugins/core/plugin-manager.ts:52-217]()

## CDP Protocol Tracing

For debugging automation flows, Steel can log the raw CDP commands and results. This is handled by `attachCDPEvents`, which wraps the `session.send` method.

**CDP Command Instrumentation**
```typescript
session.send = async function (method: Method, params?: object) {
  // Logs BrowserEventType.CDPCommand before execution
  // Executes original session.send
  // Logs BrowserEventType.CDPCommandResult with duration and success status
}
```
The tracer ignores high-frequency events like `Network.*` (which are handled by specialized listeners) to avoid log bloat.

Sources: [api/src/services/cdp/instrumentation/cdp-events.ts:9-76]()

## WebSocket Proxying

The `CDPService` handles incoming WebSocket connections and forwards them to the browser's CDP endpoint. This enables external tools to connect and control the browser directly.

The proxy server maintains cleanup listeners for browser close events and socket errors. A custom WebSocket handler can be set using `setProxyWebSocketHandler()` for advanced routing, such as directing traffic to specific plugins or instrumentation streams.

Sources: [api/src/services/cdp/cdp.service.ts:195-199](), [api/src/modules/cdp/cdp.routes.ts:7-29]()

## Debugger URL Generation

The `CDPService` provides methods to generate URLs for connecting to the browser's debugger interface. These URLs enable external tools to connect via HTTP or WebSocket.

| Method | Description |
|--------|-------------|
| `getDebuggerUrl()` | Returns HTTP URL for DevTools UI |
| `getDebuggerWsUrl(pageId?)` | Returns WebSocket URL for CDP connection |

The `/devtools/inspector.html` route facilitates this by redirecting clients to the appropriate debugger URL based on the provided `pageId`.

Sources: [api/src/modules/cdp/cdp.routes.ts:7-29]()

---

# Page: Selenium Support

# Selenium Support

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [api/src/modules/actions/actions.controller.ts](api/src/modules/actions/actions.controller.ts)
- [api/src/modules/actions/actions.routes.ts](api/src/modules/actions/actions.routes.ts)
- [api/src/modules/actions/actions.schema.ts](api/src/modules/actions/actions.schema.ts)
- [api/src/modules/logs/logs.routes.ts](api/src/modules/logs/logs.routes.ts)
- [api/src/modules/logs/logs.schema.ts](api/src/modules/logs/logs.schema.ts)
- [api/src/modules/selenium/selenium.routes.ts](api/src/modules/selenium/selenium.routes.ts)
- [api/src/modules/selenium/selenium.schema.ts](api/src/modules/selenium/selenium.schema.ts)
- [api/src/services/selenium.service.ts](api/src/services/selenium.service.ts)
- [api/src/utils/passthough-proxy.ts](api/src/utils/passthough-proxy.ts)
- [api/src/utils/proxy.ts](api/src/utils/proxy.ts)

</details>



## Purpose and Scope

This document describes steel-browser's Selenium WebDriver compatibility mode, which provides a drop-in replacement for teams with existing Selenium workflows. The Selenium integration allows standard Selenium clients (Java, Python, JavaScript, etc.) to connect to steel-browser sessions using the WebDriver protocol.

For information about the primary Chrome DevTools Protocol (CDP) integration, see [CDP Integration](#8.1). For general session management concepts, see [Session Management API](#4.1).

**Note:** The Selenium integration is a compatibility layer that does not support all features available in CDP-based sessions. It is designed for teams migrating from or maintaining existing Selenium codebases.

---

## Architecture Overview

steel-browser supports two browser control modes through distinct service layers. The `SeleniumService` manages a standalone Selenium server process.

```mermaid
graph TB
    subgraph "Application Layer"
        SessionService["SessionService<br/>api/src/services/session.service.ts"]
    end
    
    subgraph "Browser Control Layer"
        CDPService["CDPService<br/>api/src/services/cdp/cdp.service.ts"]
        SeleniumService["SeleniumService<br/>api/src/services/selenium.service.ts"]
    end
    
    subgraph "External Processes"
        SeleniumServer["Selenium Standalone Server<br/>selenium-server.jar"]
        Chrome["Chrome Browser Instance"]
    end
    
    SessionService -->|"isSelenium: false"| CDPService
    SessionService -->|"isSelenium: true"| SeleniumService
    
    SeleniumService -->|"spawn('java', ...)"| SeleniumServer
    SeleniumServer -->|"WebDriver Protocol"| Chrome
```

**Sources:** [api/src/services/selenium.service.ts:8-12](), [api/src/services/selenium.service.ts:39-44]()

The `SeleniumService` orchestrates the lifecycle of the `selenium-server.jar` process, which acts as the WebDriver endpoint for external clients.

---

## Selenium Server Lifecycle

### Launching the Service

When a Selenium session is requested, `SeleniumService.launch` is invoked. It spawns a Java process running the Selenium Standalone server.

```mermaid
sequenceDiagram
    participant SS as SeleniumService
    participant Proc as ChildProcess (Java)
    participant Log as LogSink
    
    SS->>SS: Resolve selenium-server.jar path
    SS->>Proc: spawn("java", ["-jar", ..., "standalone"])
    
    Proc-->>SS: stdout ("Started Selenium Standalone")
    SS->>SS: Resolve launch promise
    
    loop Monitoring
        Proc-->>SS: stdout/stderr data
        SS->>Log: postLog(BrowserEvent)
    end
```

**Sources:** [api/src/services/selenium.service.ts:32-82](), [api/src/services/selenium.service.ts:95-106]()

### Key Functions and Configuration

| Function | Description |
|----------|-------------|
| `launch(launchOptions)` | Spawns the Selenium server process and waits for the "Started Selenium Standalone" log message. [api/src/services/selenium.service.ts:32-82]() |
| `getChromeArgs()` | Normalizes `BrowserLauncherOptions` into Chrome command-line arguments (e.g., `--proxy-server`, `--user-agent`). [api/src/services/selenium.service.ts:20-30]() |
| `close()` | Sends `SIGINT` to the Selenium process to gracefully shut down. [api/src/services/selenium.service.ts:84-89]() |
| `postLog(browserLog)` | Forwards Selenium process logs to a remote `logSinkUrl` if configured. [api/src/services/selenium.service.ts:95-106]() |

---

## WebDriver Routing and Proxying

The API provides a proxy route that forwards standard WebDriver commands to the internal Selenium server.

```mermaid
graph LR
    Client["Selenium WebDriver Client"]
    Fastify["Fastify Server<br/>api/src/modules/selenium/selenium.routes.ts"]
    InternalServer["Selenium Standalone<br/>Port 4444"]
    
    Client -->|"POST /selenium/wd/session"| Fastify
    Fastify -->|"Inject Chrome Args"| Fastify
    Fastify -->|"reply.from('/session')"| InternalServer
```

**Sources:** [api/src/modules/selenium/selenium.routes.ts:9-13](), [api/src/modules/selenium/selenium.routes.ts:31-43]()

### Command Injection
When a client creates a new session via `POST /selenium/wd/session`, the route handler automatically injects the necessary Chrome capabilities (like proxy settings and user agents) retrieved from `seleniumService.getChromeArgs()`.

**Sources:** [api/src/modules/selenium/selenium.routes.ts:13-29]()

---

## Session Properties

Selenium sessions return different properties compared to CDP sessions. Notably, standard CDP features like live streaming and the session viewer are disabled.

### Property Comparison

| Property | CDP Session Value | Selenium Session Value | Notes |
|----------|------------------|------------------------|-------|
| `websocketUrl` | `ws://host:port/ws` | `""` (empty) | No WebSocket streaming in Selenium mode |
| `debugUrl` | `/v1/sessions/debug` | `""` (empty) | No live debugger in Selenium mode |
| `isSelenium` | `false` | `true` | Identifies session mode |

**Sources:** [api/src/modules/selenium/selenium.schema.ts:3-30]()

---

## Browser Actions Compatibility

While Selenium sessions are intended for external WebDriver control, the Steel **Quick Actions API** (Scrape, Screenshot, PDF) still operates via `CDPService` or independent fetch mechanisms.

### Scrape and PDF Flow
The `handleScrape` function in `actions.controller.ts` uses `CDPService` to create a context even if a proxy is used, but for PDF acquisition, it uses a node-fetch approach with session cookies.

```mermaid
graph TD
    ScrapeReq["Scrape Request<br/>actions.controller.ts"]
    ProxyCheck{"Proxy URL?"}
    CDP["CDPService.createBrowserContext"]
    Fetch["Node Fetch (with cookies)"]
    
    ScrapeReq --> ProxyCheck
    ProxyCheck -->|Yes| CDP
    ScrapeReq -->|"If PDF"| Fetch
```

**Sources:** [api/src/modules/actions/actions.controller.ts:33-63](), [api/src/modules/actions/actions.controller.ts:97-118]()

---

## Proxy Handling

For Selenium sessions, proxies are handled via a passthrough mechanism to avoid issues with chunked requests in standard proxy-chain implementations.

| Component | File Path | Role |
|-----------|-----------|------|
| `ProxyServer` | [api/src/utils/proxy.ts:15]() | Extends `proxy-chain` Server to handle upstream proxying. |
| `PassthroughServer` | [api/src/utils/passthough-proxy.ts:20]() | A simple HTTP server that reverse proxies requests to the original host. |
| `makePassthrough` | [api/src/utils/passthough-proxy.ts:79]() | Manually forwards requests and pipes bodies to prevent corruption. |

**Sources:** [api/src/utils/proxy.ts:26-51](), [api/src/utils/passthough-proxy.ts:20-71]()

---

## Summary of Support

| Feature | Supported in Selenium Mode | Implementation Detail |
|---------|---------------------------|-----------------------|
| **WebDriver Protocol** | ✅ Full | Via `selenium-server.jar` standalone. |
| **Chrome Args** | ✅ Full | Injected into session capabilities. |
| **Proxying** | ✅ Full | Via `ProxyServer` and passthrough logic. |
| **Live View** | ❌ No | WebSocket and Debug URLs are empty. |
| **Instrumentation** | ❌ Limited | Only process stdout/stderr logs are captured. |

**Sources:** [api/src/services/selenium.service.ts:20-30](), [api/src/modules/selenium/selenium.routes.ts:10-59](), [api/src/modules/selenium/selenium.schema.ts:32-34]()

---

# Page: Anti-Detection Features

# Anti-Detection Features

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [api/src/scripts/fingerprint.js](api/src/scripts/fingerprint.js)
- [api/src/scripts/index.ts](api/src/scripts/index.ts)
- [api/src/services/cdp/cdp.service.ts](api/src/services/cdp/cdp.service.ts)
- [api/src/services/cdp/plugins/core/base-plugin.ts](api/src/services/cdp/plugins/core/base-plugin.ts)
- [api/src/services/cdp/plugins/core/plugin-manager.ts](api/src/services/cdp/plugins/core/plugin-manager.ts)
- [api/src/utils/browser.ts](api/src/utils/browser.ts)

</details>



## Purpose and Scope

This document describes the anti-detection features that make automated browsers appear as regular user browsers to detection systems. These features include browser fingerprinting, user agent spoofing, request header manipulation, and Chrome launch configuration to disable automation signals.

For information about request filtering and ad blocking, see [8.4 Request Interception & Filtering](). For proxy configuration to mask IP addresses, see [6. Proxy Support]().

---

## Overview

The `steel-browser` system implements multiple layers of anti-detection mechanisms to evade browser automation detection systems. These mechanisms fall into four categories:

| Category | Techniques | Primary Implementation |
|----------|-----------|----------------------|
| **Browser Fingerprinting** | Hardware, platform, and browser attribute spoofing | `CDPService`, `loadFingerprintScript` |
| **Launch Configuration** | Chrome arguments to disable automation signals | `CDPService.launchInternal` |
| **Request Manipulation** | Header filtering, custom headers, ad blocking | `handlePageRequest`, `filterHeaders` |
| **User Agent Spoofing** | Custom user agent strings | `BrowserLauncherOptions.userAgent` |

---

## Fingerprint Generation

### Fingerprint Generator Library

The system uses the `fingerprint-generator` library to create realistic browser fingerprints based on device type and configuration. Fingerprints are generated during browser launch when stealth mode is enabled.

```mermaid
graph TB
    subgraph "Natural Language Space"
        UserRequest["User Session Request"]
        StealthConfig["Stealth Configuration"]
    end

    subgraph "Code Entity Space"
        LaunchConfig["BrowserLauncherOptions"]
        CheckStealth["CDPService.launchInternal logic"]
        GenInstance["FingerprintGenerator"]
        FingerprintData["BrowserFingerprintWithHeaders"]
        CDPService["CDPService"]
    end

    UserRequest --> LaunchConfig
    LaunchConfig --> CheckStealth
    CheckStealth -->|"stealth: true"| GenInstance
    GenInstance -->|"generate()"| FingerprintData
    FingerprintData -->|"stored in"| CDPService
```

**Sources:** [api/src/services/cdp/cdp.service.ts:656-693](), [api/src/services/cdp/cdp.service.ts:89-89]()

### Configuration Parameters

The fingerprint generation logic checks several configuration flags within `BrowserLauncherOptions`:

| Field | Type | Default | Purpose |
|-------|------|---------|---------|
| `stealth` | `boolean` | `undefined` | Enables stealth mode features |
| `skipFingerprintInjection` | `boolean` | `false` | Bypasses fingerprint injection |
| `fingerprint` | `BrowserFingerprintWithHeaders` | `null` | Allows pre-generated fingerprints |
| `userAgent` | `string` | `undefined` | Custom user agent string |
| `deviceConfig.device` | `"desktop" \| "mobile"` | `"desktop"` | Device type for fingerprint |
| `dimensions` | `{width, height}` | `{1920, 1080}` | Screen dimensions |

**Sources:** [api/src/services/cdp/cdp.service.ts:656-698]()

---

## Fingerprint Injection

### Injection Mechanism

Fingerprints are injected into every new page using the `injectFingerprintSafely` method. The injection occurs in the `handleNewTarget` event handler when a new page is created.

```mermaid
graph TB
    subgraph "Event Pipeline"
        TargetCreated["Browser Target Created"]
        HandleNewTarget["CDPService.handleNewTarget"]
        InjectFunc["CDPService.injectFingerprintSafely"]
        ScriptLoader["loadFingerprintScript"]
        PageEval["Page.evaluateOnNewDocument"]
    end

    TargetCreated --> HandleNewTarget
    HandleNewTarget -->|"if target.type === 'page'"| InjectFunc
    InjectFunc --> ScriptLoader
    ScriptLoader -->|"returns JS string"| PageEval
    PageEval -->|"Injected into Browser"| BrowserContext["V8 Runtime"]
```

**Sources:** [api/src/services/cdp/cdp.service.ts:313-383](), [api/src/services/cdp/cdp.service.ts:1145-1193]()

### Fixed Constants and API Overrides

The `loadFingerprintScript` function in `api/src/scripts/index.ts` generates JavaScript code that defines fixed constants and loads the fingerprint override script (`fingerprint.js`).

| Constant | Purpose | Implementation Detail |
|----------|---------|-----------------------|
| `FIXED_VENDOR` | GPU vendor name | Defaults to `"Google Inc."` |
| `FIXED_RENDERER` | GPU renderer | Defaults to `"ANGLE (Intel...)"` |
| `FIXED_HARDWARE_CONCURRENCY` | CPU cores | Spoofed value from generator |
| `FIXED_DEVICE_MEMORY` | RAM in GB | Spoofed value from generator |
| `FIXED_PLATFORM` | Operating system | Defaults to `"Linux x86_64"` |
| `FIXED_BRANDS` | Browser brands | Array of brand/version objects |

The generated script then executes `fingerprint.js`, which uses obfuscated logic to delete automation signals like `window.cdc_adoQpo...` and override `navigator` properties.

**Sources:** [api/src/scripts/index.ts:15-72](), [api/src/scripts/fingerprint.js:37-39]()

---

## Chrome Launch Arguments

### Automation Detection Disablement

The system uses specific Chrome launch arguments to disable automation detection features. These arguments vary between headless and headful modes.

**Critical Anti-Detection Arguments:**
- `--disable-blink-features=AutomationControlled`: Removes the `navigator.webdriver` property (headless only).
- `--disable-features=IsolateOrigins,site-per-process`: Disables site isolation that can be detected by timing attacks.
- `--webrtc-ip-handling-policy=disable_non_proxied_udp`: Prevents WebRTC IP leaks.

**Sources:** [api/src/services/cdp/cdp.service.ts:776-854]()

---

## Request Interception and Header Manipulation

### Header Filtering

The `filterHeaders` function in `api/src/utils/browser.ts` removes fingerprinting headers from outgoing requests that might reveal automation:

| Removed Header | Reason |
|----------------|--------|
| `accept-encoding` | Can reveal automation through encoding preferences |
| `sec-fetch-dest` | Reveals request destination context |
| `sec-fetch-mode` | Reveals fetch mode (navigate, cors, etc.) |
| `sec-fetch-site` | Reveals request origin relationship |
| `upgrade-insecure-requests` | Standard browser-specific header |

**Sources:** [api/src/utils/browser.ts:148-165]()

### Request Interception Pipeline

The `CDPService.handlePageRequest` method intercepts every request to apply anti-detection logic.

```mermaid
sequenceDiagram
    participant P as Page
    participant S as CDPService.handlePageRequest
    participant U as Request Utils
    
    P->>S: Request Event
    S->>S: Delete 'accept-language'
    S->>U: isAdRequest(url)
    alt is Ad
        S->>P: request.abort()
    else is Valid
        S->>U: isHostBlocked(host)
        alt is Blocked
            S->>P: request.abort()
        else is Allowed
            S->>P: request.continue({ headers })
        end
    end
```

**Sources:** [api/src/services/cdp/cdp.service.ts:385-438]()

---

## Plugin System Integration

Anti-detection features can be extended or modified via the Plugin System. The `PluginManager` triggers hooks throughout the browser lifecycle, allowing plugins to perform additional stealth actions.

- `onPageCreated`: Used to set up initial page-level stealth.
- `onBrowserLaunch`: Used to modify browser-wide settings.
- `onPageNavigate`: Used to re-apply stealth settings during navigation.

**Sources:** [api/src/services/cdp/plugins/core/plugin-manager.ts:123-132](), [api/src/services/cdp/plugins/core/base-plugin.ts:46-49]()

---

## Summary of Implementation Entities

| Component | File | Responsibility |
|-----------|------|----------------|
| `CDPService` | [api/src/services/cdp/cdp.service.ts]() | Orchestrates fingerprinting, launch args, and request interception. |
| `FingerprintInjector` | [api/src/services/cdp/cdp.service.ts:9]() | External library used to inject fingerprints into the browser context. |
| `loadFingerprintScript` | [api/src/scripts/index.ts:15]() | Compiles the JS payload for `Page.evaluateOnNewDocument`. |
| `filterHeaders` | [api/src/utils/browser.ts:148]() | Cleans headers to prevent passive fingerprinting. |
| `installMouseHelper` | [api/src/utils/browser.ts:35]() | Injects a visual cursor to simulate human-like interaction in screenshots/videos. |

**Sources:** [api/src/services/cdp/cdp.service.ts](), [api/src/scripts/index.ts](), [api/src/utils/browser.ts]()

---

# Page: Request Interception & Filtering

# Request Interception & Filtering

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [api/src/modules/sessions/sessions.controller.ts](api/src/modules/sessions/sessions.controller.ts)
- [api/src/modules/sessions/sessions.schema.ts](api/src/modules/sessions/sessions.schema.ts)
- [api/src/services/cdp/cdp.service.ts](api/src/services/cdp/cdp.service.ts)
- [api/src/services/cdp/plugins/core/base-plugin.ts](api/src/services/cdp/plugins/core/base-plugin.ts)
- [api/src/services/cdp/plugins/core/plugin-manager.ts](api/src/services/cdp/plugins/core/plugin-manager.ts)

</details>



This document describes the request interception and filtering system in steel-browser, which provides fine-grained control over network requests made by browser sessions. The system enables ad blocking, bandwidth optimization, custom host/URL filtering, and security protections.

For information about anti-detection fingerprinting and header manipulation, see [8.3 Anti-Detection Features](). For browser launch configuration, see [4.2 Session Configuration]().

## Purpose and Architecture

The request interception system operates at the Chrome DevTools Protocol (CDP) level using `puppeteer-core`, intercepting every HTTP request before it leaves the browser. This allows steel-browser to block, modify, or allow requests based on configurable criteria including ad detection, resource type, host patterns, and URL patterns.

Request interception is implemented in the `CDPService` and configured through `BrowserLauncherOptions` when creating sessions. All filtering happens synchronously during the request lifecycle, ensuring minimal performance impact while maximizing control.

**Sources:** [api/src/services/cdp/cdp.service.ts:83-106](), [api/src/services/cdp/cdp.service.ts:366-439](), [api/src/modules/sessions/sessions.schema.ts:36-56]()

## Request Interception Flow

```mermaid
graph TB
    PageLoad["Page initiates HTTP request"]
    Intercept["CDPService.handlePageRequest()"]
    AcceptLang["Remove accept-language header"]
    CheckAds["isAdRequest(url)"]
    CheckHosts["isHostBlocked(url, blockHosts)"]
    CheckPatterns["isUrlMatchingPatterns(url, blockUrlPatterns)"]
    CheckImages["blockImages && isImageRequest(url)"]
    CheckMedia["blockMedia && isHeavyMediaRequest(url)"]
    CheckStylesheets["blockStylesheets && resourceType === 'stylesheet'"]
    CheckFileProtocol["url.startsWith('file://')"]
    Abort["request.abort()"]
    Continue["request.continue({ headers })"]
    
    PageLoad --> Intercept
    Intercept --> AcceptLang
    AcceptLang --> CheckAds
    CheckAds -->|"blockAds=true && matched"| Abort
    CheckAds -->|"not matched"| CheckHosts
    CheckHosts -->|"matched"| Abort
    CheckHosts -->|"not matched"| CheckPatterns
    CheckPatterns -->|"matched"| Abort
    CheckPatterns -->|"not matched"| CheckImages
    CheckImages -->|"matched"| Abort
    CheckImages -->|"not matched"| CheckMedia
    CheckMedia -->|"matched"| Abort
    CheckMedia -->|"not matched"| CheckStylesheets
    CheckStylesheets -->|"matched"| Abort
    CheckStylesheets -->|"not matched"| CheckFileProtocol
    CheckFileProtocol -->|"matched"| Abort
    CheckFileProtocol -->|"not matched"| Continue
```

**Sources:** [api/src/services/cdp/cdp.service.ts:385-439](), [api/src/utils/requests.ts:1-111]()

## Request Interception Configuration

The following diagram maps the configuration schema to the internal runtime entities within `CDPService`.

```mermaid
graph LR
    subgraph "Natural Language Space"
        UserReq["User Session Request"]
    end

    subgraph "Code Entity Space (Schema)"
        CreateSession["CreateSession schema"]
        BlockAdsField["blockAds: boolean"]
        OptimizeField["optimizeBandwidth: boolean | object"]
    end
    
    subgraph "Code Entity Space (Runtime)"
        CDPS["CDPService"]
        LaunchConfig["this.launchConfig"]
        HandleReq["handlePageRequest(request, page)"]
        IsAd["isAdRequest(url)"]
        IsHeavy["isHeavyMediaRequest(url)"]
    end
    
    UserReq --> CreateSession
    CreateSession --> BlockAdsField
    CreateSession --> OptimizeField
    
    BlockAdsField --> LaunchConfig
    OptimizeField --> LaunchConfig
    
    LaunchConfig --> HandleReq
    HandleReq --> IsAd
    HandleReq --> IsHeavy
```

**Sources:** [api/src/modules/sessions/sessions.schema.ts:28-56](), [api/src/services/cdp/cdp.service.ts:385-439](), [api/src/utils/requests.ts:30-51]()

## Ad Blocking

### Overview

The `blockAds` configuration option enables automatic blocking of requests to known advertising and tracking domains. When enabled, steel-browser maintains a curated list of ad networks, analytics services, and tracking platforms.

### Implementation

Ad blocking is implemented through the `isAdRequest()` utility function, which checks if the request hostname matches any domain in the `AD_HOSTS` list. The check performs both exact matches and subdomain matches.

```typescript
// Configuration in sessions.schema.ts
blockAds: z.boolean().optional()
```

### Blocked Hosts

The system blocks requests to categories including Ad Networks, Analytics, Ad Exchanges, and Social Tracking via the `AD_HOSTS` array defined in `requests.ts`.

### Request Flow

When ad blocking is enabled:

1. Page initiates HTTP request.
2. `handlePageRequest()` receives the request.
3. `isAdRequest(request.url())` checks hostname against `AD_HOSTS`.
4. If matched, `request.abort()` is called and request is logged.
5. If not matched, request continues to next filter.

**Sources:** [api/src/services/cdp/cdp.service.ts:393-397](), [api/src/utils/requests.ts:1-60](), [api/src/modules/sessions/sessions.schema.ts:36-39]()

## Bandwidth Optimization

### Overview

The `optimizeBandwidth` option provides multiple strategies for reducing bandwidth consumption by blocking resource types and specific hosts/URLs. It can be configured as a boolean (enabling all optimizations) or as an object with granular control.

### Configuration Modes

#### Boolean Mode

When set to `true`, the system enables `blockImages`, `blockMedia`, and `blockStylesheets`.

#### Object Mode

```typescript
optimizeBandwidth: {
  blockImages: boolean;
  blockMedia: boolean;
  blockStylesheets: boolean;
  blockHosts: string[];
  blockUrlPatterns: string[];
}
```

### Resource Type Filtering

#### Image Blocking

When `blockImages: true`, the system blocks:
- Resources with `resourceType === "image"`.
- URLs matching image extensions via `isImageRequest()`.

#### Media Blocking

When `blockMedia: true`, the system blocks:
- Resources with `resourceType === "media"`.
- URLs matching video extensions or streaming protocols via `isHeavyMediaRequest()`.

#### Stylesheet Blocking

When `blockStylesheets: true`, the system blocks:
- Resources with `resourceType === "stylesheet"`.

### Host and Pattern Blocking

#### Host Blocking

The `blockHosts` array accepts domain names that should be completely blocked. The `isHostBlocked()` function performs exact hostname and subdomain matching.

#### URL Pattern Blocking

The `blockUrlPatterns` array accepts glob-style patterns. The `isUrlMatchingPatterns()` function converts these to regular expressions.

**Sources:** [api/src/services/cdp/cdp.service.ts:389-430](), [api/src/utils/requests.ts:62-111](), [api/src/modules/sessions/sessions.schema.ts:40-56]()

## Header Manipulation

### Accept-Language Removal

The request interception system automatically removes the `accept-language` header from all requests as an anti-detection measure. This helps prevent headless browser detection through language fingerprinting.

```typescript
const headers = request.headers();
delete headers["accept-language"]; 
```

This modification occurs in `handlePageRequest` before any other filtering logic.

**Sources:** [api/src/services/cdp/cdp.service.ts:386-388]()

## Security Filtering

### File Protocol Protection

The system includes automatic protection against file protocol requests (`file://`), which could expose the local filesystem. 

1. **Request Level**: Any request to a `file://` URL triggers `request.abort()`, logs the violation, and initiates a browser shutdown via `this.shutdown()`.
2. **Response Level**: If a response is received from a `file://` URL, the page is closed and the browser is shut down.

**Sources:** [api/src/services/cdp/cdp.service.ts:432-438](), [api/src/services/cdp/cdp.service.ts:370-378]()

## Implementation Details

### Request Interception Setup

Request interception is enabled for every page created in the browser. The `CDPService` listens for the `targetcreated` event. If the target is a page, it calls `page.setRequestInterception(true)` and attaches the `handlePageRequest` handler.

### Handler Logic Association

The following diagram bridges the logical request handling steps to the specific code functions.

```mermaid
graph TD
    RequestEvent["Page 'request' event"]
    HandlePR["CDPService.handlePageRequest()"]
    
    subgraph "Utility Logic"
        IsAd["isAdRequest()"]
        IsHeavy["isHeavyMediaRequest()"]
        IsHostB["isHostBlocked()"]
        IsUrlM["isUrlMatchingPatterns()"]
        IsImg["isImageRequest()"]
    end
    
    RequestEvent --> HandlePR
    HandlePR --> IsAd
    HandlePR --> IsHeavy
    HandlePR --> IsHostB
    HandlePR --> IsUrlM
    HandlePR --> IsImg
```

**Sources:** [api/src/services/cdp/cdp.service.ts:385-439](), [api/src/utils/requests.ts:1-111]()

## Configuration Reference

### BrowserLauncherOptions & Schema

| Field | Type | Description |
|-------|------|-------------|
| `blockAds` | `boolean` | Enable ad blocking. |
| `optimizeBandwidth` | `boolean \| object` | Enable bandwidth optimization (images, media, stylesheets, hosts, patterns). |
| `skipFingerprintInjection`| `boolean` | Flag to skip fingerprint injection. |

**Sources:** [api/src/modules/sessions/sessions.schema.ts:28-60](), [api/src/services/cdp/cdp.service.ts:150-167]()

## Logging

Blocked requests are logged via the `CDPService` logger:

- **Ads**: `[CDPService] Blocked request to ad related resource: ${url}`
- **Hosts/Patterns**: `[CDPService] Blocked request to blocked host or pattern: ${url}`
- **Resources**: `[CDPService] Blocked ${resourceType} resource due to optimizeBandwidth...`
- **Security**: `[CDPService] Blocked request to file protocol: ${url}`

**Sources:** [api/src/services/cdp/cdp.service.ts:394-434]()

---

# Page: Browser Extensions

# Browser Extensions

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [api/extensions/recorder/.gitignore](api/extensions/recorder/.gitignore)
- [api/extensions/recorder/manifest.json](api/extensions/recorder/manifest.json)
- [api/extensions/recorder/package-lock.json](api/extensions/recorder/package-lock.json)
- [api/extensions/recorder/package.json](api/extensions/recorder/package.json)
- [api/extensions/recorder/src/background.js](api/extensions/recorder/src/background.js)
- [api/extensions/recorder/src/inject.js](api/extensions/recorder/src/inject.js)
- [api/src/services/context/chrome-context.service.ts](api/src/services/context/chrome-context.service.ts)
- [api/src/services/leveldb/sessionstorage.ts](api/src/services/leveldb/sessionstorage.ts)
- [api/src/services/timezone-fetcher.service.ts](api/src/services/timezone-fetcher.service.ts)
- [api/src/utils/context.ts](api/src/utils/context.ts)
- [api/src/utils/extensions.ts](api/src/utils/extensions.ts)

</details>



This document describes how Chrome extensions are loaded and managed in steel-browser sessions. Browser extensions are packaged Chrome extensions that can be loaded into browser instances to add functionality such as recording, automation helpers, or custom tooling.

For information about the Plugin system that provides lifecycle hooks for extending browser automation behavior, see [Plugin System](#9).

---

## Overview

Steel-browser supports loading Chrome extensions into browser sessions. Extensions can be:
- Built-in extensions bundled with the system (e.g., the recorder extension)
- Named extensions resolved from the extensions directory
- Custom extensions provided as file system paths

Extensions are loaded during browser launch and remain active throughout the session lifecycle. Each extension runs in its own background page context and can interact with web pages through Chrome's extension APIs.

**Sources:**
- [api/src/utils/extensions.ts:4-38]()
- [api/extensions/recorder/manifest.json:1-26]()

---

## Extension Types

Steel-browser supports three types of extensions:

| Extension Type | Description | Configuration Method | Example |
|---------------|-------------|---------------------|---------|
| Built-in | System extensions bundled with steel-browser | Automatically loaded based on headless mode | `recorder` |
| Named | Extensions resolved from the extensions directory | Specified by name in `extensions` array | `["my-extension"]` |
| Session-specific | External extensions provided via API | Passed in `extra.orgExtensions.paths` | Absolute file paths |

### Extension Source Resolution

The system uses `getExtensionPaths` to resolve named extensions by checking the `api/extensions` directory.

```mermaid
graph TB
    subgraph "Extension Sources"
        BuiltIn["Built-in Extensions<br/>Automatic based on mode"]
        Named["Named Extensions<br/>extensions: ['name']"]
        Session["Session Extensions<br/>extra.orgExtensions.paths"]
    end
    
    subgraph "Resolution Process"
        DefaultExt["Default Extensions<br/>['recorder'] in headless"]
        CustomExt["Custom Extensions<br/>User-specified names"]
        ExtResolver["getExtensionPaths()<br/>api/src/utils/extensions.ts"]
        SessionPaths["Session Extension Paths<br/>Already resolved"]
    end
    
    subgraph "Chrome Launch"
        ExtArgs["Chrome Args<br/>--load-extension<br/>--disable-extensions-except"]
        Browser["Browser Instance<br/>Extensions Active"]
    end
    
    BuiltIn --> DefaultExt
    Named --> CustomExt
    
    DefaultExt --> ExtResolver
    CustomExt --> ExtResolver
    Session --> SessionPaths
    
    ExtResolver --> ExtArgs
    SessionPaths --> ExtArgs
    
    ExtArgs --> Browser
```

**Sources:**
- [api/src/utils/extensions.ts:4-10]()
- [api/src/utils/extensions.ts:21-23]()

---

## Built-in Extensions: The Recorder

Steel-browser includes a built-in `recorder` extension located in `api/extensions/recorder/`. This extension uses `rrweb` to capture session events for playback and debugging.

### Recorder Implementation

The recorder consists of three main components:
1.  **Manifest**: Defines permissions (`scripting`, `activeTab`) and the background service worker [api/extensions/recorder/manifest.json:1-26]().
2.  **Background Script**: Injects the recorder into tabs and forwards events to the Steel API at `/v1/events` [api/extensions/recorder/src/background.js:1-55]().
3.  **Injected Script**: Uses `rrweb` to record DOM changes and also handles WebRTC blocking for privacy on specific sites [api/extensions/recorder/src/inject.js:1-57]().

### WebRTC Blocking Logic
The recorder extension includes a privacy feature that disables WebRTC on all sites except a whitelist (e.g., Google Meet, Zoom, Discord) to prevent IP leaks [api/extensions/recorder/src/inject.js:28-54]().

```mermaid
graph TD
    subgraph "api/extensions/recorder/src/inject.js"
        RRWeb["rrweb.record()"]
        RTCBlock["WebRTC Blocking Logic"]
    end

    subgraph "api/extensions/recorder/src/background.js"
        Inject["chrome.scripting.executeScript"]
        Forwarder["fetch('http://localhost:3000/v1/events')"]
    end

    RRWeb -->|SAVE_EVENTS| Forwarder
    RTCBlock -->|Protects IP| BrowserContext["Browser Context"]
    Forwarder -->|POST| SteelAPI["Steel API Event Endpoint"]
```

**Sources:**
- [api/extensions/recorder/src/inject.js:4-26]()
- [api/extensions/recorder/src/inject.js:28-54]()
- [api/extensions/recorder/src/background.js:1-3]()

---

## Configuration

Extensions are configured when creating a browser session through the `BrowserLauncherOptions` interface.

### Session Creation with Extensions

Extensions can be specified in the session creation request:

```typescript
// In BrowserLauncherOptions
{
  extensions?: string[],          // Named extensions to load from api/extensions/
  extra?: {
    orgExtensions?: {
      paths: string[]              // Absolute paths to custom extension directories
    }
  }
}
```

**Sources:**
- [api/src/utils/extensions.ts:4-38]()

---

## Extension Loading Mechanism

Extensions are loaded via Chrome command-line arguments. The `CDPService` (or similar launcher) aggregates paths from `getExtensionPaths` and any session-specific paths provided in the `extra` field.

### Launch Arguments Format

When extensions are present, two Chrome arguments are added:

| Argument | Purpose | Format |
|----------|---------|--------|
| `--load-extension` | Loads specified extensions on startup | Comma-separated absolute paths |
| `--disable-extensions-except` | Disables all extensions except the specified ones | Comma-separated absolute paths |

**Sources:**
- [api/src/utils/extensions.ts:21-23]()
- [api/extensions/recorder/manifest.json:13-25]()

---

## Data Extraction and Storage

While extensions provide active functionality, Steel-browser also uses CDP (Chrome DevTools Protocol) and direct filesystem access to manage session state like `localStorage` and `sessionStorage`.

### Storage Resolution Flow

The `ChromeContextService` and `ChromeSessionStorageReader` handle persistent state that extensions or pages might create.

```mermaid
graph LR
    subgraph "Storage Extraction"
        LevelDB["Chrome LevelDB Files"]
        SSReader["ChromeSessionStorageReader<br/>api/src/services/leveldb/sessionstorage.ts"]
        CCService["ChromeContextService<br/>api/src/services/context/chrome-context.service.ts"]
    end

    subgraph "CDP Extraction"
        CDP["CDP Session"]
        ExtStorage["extractStorageForPage()<br/>api/src/utils/context.ts"]
    end

    LevelDB --> SSReader
    SSReader --> CCService
    CDP --> ExtStorage
    CCService --> FinalData["SessionData Object"]
    ExtStorage --> FinalData
```

**Sources:**
- [api/src/services/leveldb/sessionstorage.ts:204-229]()
- [api/src/services/context/chrome-context.service.ts:8-56]()
- [api/src/utils/context.ts:19-27]()

---

## Extension Lifecycle

Extensions follow the browser session lifecycle and are loaded during launch and closed during shutdown.

1.  **Launch Phase**: The system identifies required extensions, resolves paths via `getExtensionPaths`, and starts Chrome with `--load-extension`.
2.  **Active Phase**: Extension background scripts (like `background.js` in the recorder) listen for events. Content scripts (like `inject.js`) are injected into pages as they load [api/extensions/recorder/manifest.json:16-25]().
3.  **Shutdown Phase**: Extensions are unloaded when the browser process is terminated.

**Sources:**
- [api/extensions/recorder/src/background.js:5-19]()
- [api/src/utils/extensions.ts:4-38]()

---

# Page: Plugin System

# Plugin System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [api/src/services/cdp/cdp.service.ts](api/src/services/cdp/cdp.service.ts)
- [api/src/services/cdp/plugins/core/base-plugin.ts](api/src/services/cdp/plugins/core/base-plugin.ts)
- [api/src/services/cdp/plugins/core/plugin-manager.ts](api/src/services/cdp/plugins/core/plugin-manager.ts)

</details>



## Purpose and Scope

The Plugin System provides a modular, event-driven architecture for extending browser automation functionality in steel-browser. Plugins intercept key browser lifecycle events (browser launch, page creation, navigation, etc.) to inject custom behavior without modifying core services. The system uses the `BasePlugin` abstract class and `PluginManager` orchestration to provide a clean extension mechanism.

For detailed guidance on creating custom plugins, see [Creating Custom Plugins](#14.4). For documentation of specific built-in plugins, see [Built-in Plugins](#9.2). For information on how plugins integrate with the broader CDP automation system, see [CDPService](#3.1).

---

## Architecture Overview

The plugin system consists of three core components:

| Component | File | Responsibility |
|-----------|------|----------------|
| `BasePlugin` | [api/src/services/cdp/plugins/core/base-plugin.ts]() | Abstract base class defining plugin interface and lifecycle hooks |
| `PluginManager` | [api/src/services/cdp/plugins/core/plugin-manager.ts]() | Orchestrates plugin registration and lifecycle event dispatch |
| `CDPService` | [api/src/services/cdp/cdp.service.ts]() | Owns plugin manager and triggers lifecycle events |

### Plugin Architecture

```mermaid
graph TB
    CDPService["CDPService"]
    PluginManager["PluginManager"]
    BasePlugin["BasePlugin<br/>(abstract)"]
    
    subgraph "Plugin Instances"
        Plugin1["LoggingPlugin<br/>extends BasePlugin"]
        Plugin2["RecordingPlugin<br/>extends BasePlugin"]
        Plugin3["CustomPlugin<br/>extends BasePlugin"]
    end
    
    subgraph "Browser Events"
        BrowserLaunch["Browser Launch Event"]
        PageCreated["Page Created Event"]
        PageNavigate["Page Navigate Event"]
        BrowserClose["Browser Close Event"]
    end
    
    CDPService -->|"owns"| PluginManager
    CDPService -->|"triggers"| BrowserLaunch
    CDPService -->|"triggers"| PageCreated
    CDPService -->|"triggers"| PageNavigate
    CDPService -->|"triggers"| BrowserClose
    
    PluginManager -->|"maintains Map<string, BasePlugin>"| BasePlugin
    PluginManager -->|"register()"| Plugin1
    PluginManager -->|"register()"| Plugin2
    PluginManager -->|"register()"| Plugin3
    
    BrowserLaunch -->|"onBrowserLaunch()"| PluginManager
    PageCreated -->|"onPageCreated()"| PluginManager
    PageNavigate -->|"onPageNavigate()"| PluginManager
    BrowserClose -->|"onBrowserClose()"| PluginManager
    
    PluginManager -->|"dispatch to all"| Plugin1
    PluginManager -->|"dispatch to all"| Plugin2
    PluginManager -->|"dispatch to all"| Plugin3
    
    BasePlugin -->|"setService()"| CDPService
```

**Sources:** [api/src/services/cdp/plugins/core/base-plugin.ts:27-40](), [api/src/services/cdp/plugins/core/plugin-manager.ts:7-16](), [api/src/services/cdp/cdp.service.ts:99-169]()

---

## Plugin Lifecycle Hooks

`BasePlugin` defines multiple lifecycle hooks that plugins can override to inject behavior at specific points in the browser automation flow. All hooks receive relevant context objects.

### Lifecycle Hook Reference

| Hook | Signature | Timing | Common Use Cases |
|------|-----------|--------|------------------|
| `onSessionStart` | `onSessionStart(sessionConfig: BrowserLauncherOptions): void \| Promise<void>` | Before session launch or reuse | Initialize session-level resources |
| `onBrowserLaunch` | `async onBrowserLaunch(browser: Browser): Promise<void>` | Immediately after browser process starts | Initialize browser-level state |
| `onBrowserReady` | `onBrowserReady(context: BrowserLauncherOptions): void \| Promise<void>` | After browser launch completes | Access final session configuration |
| `onPageCreated` | `async onPageCreated(page: Page): Promise<void>` | When a new page/tab is created | Inject scripts, set up page event listeners |
| `onPageNavigate` | `async onPageNavigate(page: Page): Promise<void>` | Before page navigation starts | Modify navigation parameters |
| `onPageUnload` | `async onPageUnload(page: Page): Promise<void>` | When page begins to unload | Capture pre-unload state |
| `onBeforePageClose` | `async onBeforePageClose(page: Page): Promise<void>` | Before page closes | Clean up page-specific resources |
| `onBrowserClose` | `async onBrowserClose(browser: Browser): Promise<void>` | Before browser process terminates | Clean up browser-level resources |
| `onShutdown` | `async onShutdown(reason: ShutdownReason): Promise<void>` | When service shuts down | Global cleanup based on `ShutdownReason` |
| `onSessionEnd` | `async onSessionEnd(sessionConfig: BrowserLauncherOptions): Promise<void>` | When session terminates | Post-session cleanup |

**Sources:** [api/src/services/cdp/plugins/core/base-plugin.ts:43-54]()

### Lifecycle Event Flow

```mermaid
sequenceDiagram
    participant CDP as CDPService
    participant PM as PluginManager
    participant P1 as Plugin1
    participant P2 as Plugin2
    participant Browser
    participant Page

    Note over CDP: Session start requested
    CDP->>PM: onSessionStart(config)
    PM->>P1: onSessionStart(config)
    PM->>P2: onSessionStart(config)

    CDP->>Browser: Launch browser process
    Browser-->>CDP: Browser instance
    
    CDP->>PM: onBrowserLaunch(browser)
    PM->>P1: onBrowserLaunch(browser)
    PM->>P2: onBrowserLaunch(browser)
    
    Note over CDP: Apply configuration
    CDP->>PM: onBrowserReady(context)
    PM->>P1: onBrowserReady(context)
    PM->>P2: onBrowserReady(context)
    
    Browser->>Page: Create page
    CDP->>PM: onPageCreated(page)
    PM->>P1: onPageCreated(page)
    PM->>P2: onPageCreated(page)
    
    Page->>Page: Navigate to URL
    CDP->>PM: onPageNavigate(page)
    PM->>P1: onPageNavigate(page)
    PM->>P2: onPageNavigate(page)
    
    Note over CDP: Session ending
    CDP->>PM: onBeforeSessionEnd(config)
    
    CDP->>PM: onBrowserClose(browser)
    PM->>P1: onBrowserClose(browser)
    PM->>P2: onBrowserClose(browser)
    
    CDP->>PM: onSessionEnd(config)
    PM->>P1: onSessionEnd(config)
    PM->>P2: onSessionEnd(config)
```

**Sources:** [api/src/services/cdp/plugins/core/plugin-manager.ts:54-216]()

---

## Plugin Registration and Management

`PluginManager` maintains a `Map<string, BasePlugin>` of registered plugins, indexed by plugin name. It provides methods for plugin lifecycle management and ensures safe, isolated execution of plugin hooks.

### PluginManager Interface

```mermaid
classDiagram
    class PluginManager {
        -Map~string, BasePlugin~ plugins
        -CDPService service
        -FastifyBaseLogger logger
        +constructor(service, logger)
        +register(plugin: BasePlugin): void
        +unregister(pluginName: string): boolean
        +getPlugin~T~(pluginName: string): T | undefined
        +onSessionStart(sessionConfig: BrowserLauncherOptions): Promise~void~
        +onBrowserLaunch(browser: Browser): Promise~void~
        +onBrowserReady(context: BrowserLauncherOptions): Promise~void~
        +onPageCreated(page: Page): Promise~void~
        +onPageNavigate(page: Page): Promise~void~
        +onPageUnload(page: Page): Promise~void~
        +onBeforePageClose(page: Page): Promise~void~
        +onBrowserClose(browser: Browser): Promise~void~
        +onShutdown(reason: ShutdownReason): Promise~void~
        +onSessionEnd(sessionConfig: BrowserLauncherOptions): Promise~void~
    }
    
    class BasePlugin {
        <<abstract>>
        +string name
        #PluginOptions options
        #CDPService | null cdpService
        +constructor(options: PluginOptions)
        +setService(service: CDPService): void
        +onSessionStart(sessionConfig: BrowserLauncherOptions): void
        +onBrowserLaunch(browser: Browser): Promise~void~
        +onBrowserReady(context: BrowserLauncherOptions): void
        +onPageCreated(page: Page): Promise~void~
        +onPageNavigate(page: Page): Promise~void~
        +onPageUnload(page: Page): Promise~void~
        +onBeforePageClose(page: Page): Promise~void~
        +onBrowserClose(browser: Browser): Promise~void~
        +onShutdown(reason: ShutdownReason): Promise~void~
        +onSessionEnd(sessionConfig: BrowserLauncherOptions): Promise~void~
    }
    
    PluginManager --> BasePlugin : manages
```

**Sources:** [api/src/services/cdp/plugins/core/plugin-manager.ts:7-217](), [api/src/services/cdp/plugins/core/base-plugin.ts:27-55]()

### Registration Process

1. **Plugin Instantiation**: Create a plugin instance extending `BasePlugin` with a unique name.
2. **Registration**: Call `pluginManager.register(plugin)`.
3. **Service Injection**: `PluginManager` calls `plugin.setService(service)` to provide access to `CDPService`. [api/src/services/cdp/plugins/core/plugin-manager.ts:26]()
4. **Storage**: Plugin stored in internal `Map<string, BasePlugin>` indexed by `plugin.name`. [api/src/services/cdp/plugins/core/plugin-manager.ts:27]()

### Management Operations

| Method | Parameters | Returns | Behavior |
|--------|------------|---------|----------|
| `register()` | `plugin: BasePlugin` | `void` | Adds plugin to registry. If name exists, overwrites with warning. [api/src/services/cdp/plugins/core/plugin-manager.ts:21-29]() |
| `unregister()` | `pluginName: string` | `boolean` | Removes plugin from registry by name. [api/src/services/cdp/plugins/core/plugin-manager.ts:34-42]() |
| `getPlugin<T>()` | `pluginName: string` | `T \| undefined` | Retrieves plugin by name with type casting. [api/src/services/cdp/plugins/core/plugin-manager.ts:47-49]() |

---

## Event Dispatch Mechanism

When `CDPService` triggers a lifecycle event, `PluginManager` dispatches it to all registered plugins using a parallel, fault-isolated execution model:

### Execution Characteristics

1. **Parallel Dispatch**: All plugins receive events concurrently via `Promise.all()`. [api/src/services/cdp/plugins/core/plugin-manager.ts:62]()
2. **Error Isolation**: Each plugin wrapped in try-catch; failures logged but don't affect other plugins. [api/src/services/cdp/plugins/core/plugin-manager.ts:58-60]()
3. **Async/Sync Flexibility**: Hooks handle both sync and async implementations via `Promise.resolve()`. [api/src/services/cdp/plugins/core/plugin-manager.ts:57]()
4. **Shutdown Context**: `onShutdown` receives a `ShutdownReason` (e.g., `SESSION_END`, `SECURITY_VIOLATION`, `LAUNCH_FAILURE`) to determine cleanup logic. [api/src/services/cdp/plugins/core/base-plugin.ts:9-20]()

### Error Handling Example

```mermaid
graph TB
    PM["PluginManager.onPageCreated(page)"]
    
    subgraph "Parallel Execution"
        P1["Plugin1.onPageCreated(page)"]
        P2["Plugin2.onPageCreated(page)"]
        P3["Plugin3.onPageCreated(page)"]
    end
    
    P1Success["✓ Success"]
    P2Error["✗ Error thrown"]
    P3Success["✓ Success"]
    
    Logger["FastifyBaseLogger"]
    
    PM -->|"Promise.all()"| P1
    PM -->|"Promise.all()"| P2
    PM -->|"Promise.all()"| P3
    
    P1 -->|"try/catch"| P1Success
    P2 -->|"try/catch"| P2Error
    P3 -->|"try/catch"| P3Success
    
    P2Error -->|"logger.error()"| Logger
```

**Sources:** [api/src/services/cdp/plugins/core/plugin-manager.ts:123-132]()

---

## Plugin Options and Configuration

Plugins receive configuration through the `PluginOptions` interface passed to their constructor.

### Base Plugin Structure

```typescript
export interface PluginOptions {
  name: string;           // Required: Unique identifier for plugin
  [key: string]: any;     // Optional: Plugin-specific configuration
}

export abstract class BasePlugin {
  public name: string;
  protected options: PluginOptions;
  protected cdpService: CDPService | null;
  
  constructor(options: PluginOptions) {
    this.name = options.name;
    this.options = options;
    this.cdpService = null;
  }
}
```

**Sources:** [api/src/services/cdp/plugins/core/base-plugin.ts:22-36]()

### CDPService Access

After registration, plugins can access the full `CDPService` API through the `cdpService` property. This enables plugins to interact with the broader automation system while maintaining encapsulation. [api/src/services/cdp/plugins/core/base-plugin.ts:38-40]()

---

## Integration Points

The plugin system integrates with `CDPService` at key lifecycle points:

| CDPService Action | Plugin Hook Triggered | Context Passed |
|-------------------|----------------------|----------------|
| Session Start | `onSessionStart()` | `BrowserLauncherOptions` |
| Browser Launch | `onBrowserLaunch()` | `Browser` instance |
| Browser Ready | `onBrowserReady()` | `BrowserLauncherOptions` |
| Page Created | `onPageCreated()` | `Page` instance |
| Navigation | `onPageNavigate()` | `Page` instance |
| Page Unload | `onPageUnload()` | `Page` instance |
| Page Close | `onBeforePageClose()` | `Page` instance |
| Browser Close | `onBrowserClose()` | `Browser` instance |
| Shutdown | `onShutdown()` | `ShutdownReason` |
| Session End | `onSessionEnd()` | `BrowserLauncherOptions` |

**Sources:** [api/src/services/cdp/plugins/core/base-plugin.ts:43-54](), [api/src/services/cdp/plugins/core/plugin-manager.ts:54-216]()

---

# Page: BasePlugin & PluginManager

# BasePlugin & PluginManager

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [api/src/plugins/browser-socket/handlers/cast.handler.ts](api/src/plugins/browser-socket/handlers/cast.handler.ts)
- [api/src/plugins/browser-socket/handlers/index.ts](api/src/plugins/browser-socket/handlers/index.ts)
- [api/src/services/cdp/cdp.service.ts](api/src/services/cdp/cdp.service.ts)
- [api/src/services/cdp/plugins/core/base-plugin.ts](api/src/services/cdp/plugins/core/base-plugin.ts)
- [api/src/services/cdp/plugins/core/index.ts](api/src/services/cdp/plugins/core/index.ts)
- [api/src/services/cdp/plugins/core/plugin-manager.ts](api/src/services/cdp/plugins/core/plugin-manager.ts)
- [api/src/services/websocket-registry.service.ts](api/src/services/websocket-registry.service.ts)
- [api/src/steel-browser-plugin.ts](api/src/steel-browser-plugin.ts)
- [api/src/types/index.ts](api/src/types/index.ts)
- [api/src/types/websocket.ts](api/src/types/websocket.ts)
- [docs/PLUGIN_DEVELOPMENT.md](docs/PLUGIN_DEVELOPMENT.md)
- [ui/vite.config.ts](ui/vite.config.ts)

</details>



## Purpose and Scope

The plugin system provides an extensible architecture for customizing browser automation behavior at key points in the browser and page lifecycle. The `BasePlugin` abstract class defines lifecycle hooks that plugins can implement, while the `PluginManager` orchestrates plugin registration and event distribution across all registered plugins.

This document covers the plugin architecture, lifecycle hooks, and the mechanics of plugin registration and execution.

**Sources:** [api/src/services/cdp/plugins/core/base-plugin.ts:27-55](), [api/src/services/cdp/plugins/core/plugin-manager.ts:7-217]()

---

## Plugin Architecture Overview

The plugin system consists of three primary components that work together to enable modular browser automation extensions:

```mermaid
graph TB
    CDPService["CDPService"]
    PluginManager["PluginManager"]
    BasePlugin1["BasePlugin<br/>(e.g. AdBlocker)"]
    BasePlugin2["BasePlugin<br/>(e.g. RequestLogger)"]
    BasePlugin3["BasePlugin<br/>(Custom Plugin)"]
    Browser["Browser<br/>(puppeteer-core)"]
    Page["Page<br/>(puppeteer-core)"]
    
    CDPService -->|"owns"| PluginManager
    PluginManager -->|"manages"| BasePlugin1
    PluginManager -->|"manages"| BasePlugin2
    PluginManager -->|"manages"| BasePlugin3
    
    BasePlugin1 -.->|"setService()"| CDPService
    BasePlugin2 -.->|"setService()"| CDPService
    BasePlugin3 -.->|"setService()"| CDPService
    
    CDPService -->|"controls"| Browser
    Browser -->|"creates"| Page
    
    PluginManager -->|"onBrowserLaunch()"| BasePlugin1
    PluginManager -->|"onBrowserLaunch()"| BasePlugin2
    PluginManager -->|"onBrowserLaunch()"| BasePlugin3
    
    PluginManager -->|"onPageCreated()"| BasePlugin1
    PluginManager -->|"onPageCreated()"| BasePlugin2
    PluginManager -->|"onPageCreated()"| BasePlugin3
```

**Diagram: Plugin System Component Relationships**

The `CDPService` owns the `PluginManager`, which maintains a registry of `BasePlugin` instances. Each plugin receives a reference to `CDPService` via `setService()`, allowing plugins to access browser instances and CDP functionality. When lifecycle events occur (browser launch, page creation, etc.), `CDPService` calls the corresponding method on `PluginManager`, which propagates the event to all registered plugins in parallel.

**Sources:** [api/src/services/cdp/cdp.service.ts:169-169](), [api/src/services/cdp/plugins/core/base-plugin.ts:27-40](), [api/src/services/cdp/plugins/core/plugin-manager.ts:7-16]()

---

## BasePlugin Class

The `BasePlugin` abstract class serves as the base for all plugins in the system. Plugins extend this class and implement the lifecycle hooks they need to customize browser behavior.

### Class Structure

```typescript
export abstract class BasePlugin {
  public name: string;
  protected options: PluginOptions;
  protected cdpService: CDPService | null;
}
```

| Property | Type | Description |
|----------|------|-------------|
| `name` | `string` | Unique identifier for the plugin, used for registration and retrieval |
| `options` | `PluginOptions` | Configuration options passed during plugin construction |
| `cdpService` | `CDPService \| null` | Reference to `CDPService`, set by `PluginManager` after registration |

**Sources:** [api/src/services/cdp/plugins/core/base-plugin.ts:27-36]()

### Constructor and Service Injection

The `BasePlugin` constructor accepts a `PluginOptions` object that includes a `name` property. The `cdpService` reference is initially `null` and is injected by `PluginManager.register()` via the `setService()` method:

```typescript
constructor(options: PluginOptions) {
  this.name = options.name;
  this.options = options;
  this.cdpService = null;
}

public setService(service: CDPService): void {
  this.cdpService = service;
}
```

This dependency injection pattern allows plugins to access browser instances, pages, and CDP functionality through the `CDPService` instance.

**Sources:** [api/src/services/cdp/plugins/core/base-plugin.ts:32-40]()

### Lifecycle Hooks

`BasePlugin` defines multiple lifecycle hooks that plugins can override. All hooks have default empty implementations:

| Hook | Parameters | Called When |
|------|------------|-------------|
| `onSessionStart` | `sessionConfig` | Before a session begins (launch or reuse) |
| `onBrowserLaunch` | `browser` | Immediately after the browser process launches |
| `onBrowserReady` | `context` | After browser is fully configured and ready |
| `onPageCreated` | `page` | When a new page/tab is created |
| `onPageNavigate` | `page` | Before page begins navigation |
| `onPageUnload` | `page` | Before page content unloads |
| `onBeforePageClose` | `page` | Before a page is closed |
| `onBrowserClose` | `browser` | Before the browser process closes |
| `onBeforeSessionEnd`| `sessionConfig` | Before session shutdown begins |
| `onSessionEnd` | `sessionConfig` | After teardown and session-end work is complete |
| `onShutdown` | `reason` | During system shutdown with a specific `ShutdownReason` |

**Sources:** [api/src/services/cdp/plugins/core/base-plugin.ts:42-55]()

### Shutdown Reasons

The `ShutdownReason` enum provides context to the `onShutdown` hook:

| Reason | Description |
|--------|-------------|
| `SESSION_END` | Normal graceful session termination |
| `SECURITY_VIOLATION` | Security violation detected (e.g., restricted protocol access) |
| `RELAUNCH` | Browser is closing to be replaced by a new instance |
| `LAUNCH_FAILURE` | Cleanup before a retry after a failed launch |
| `MODE_SWITCH` | Switching browser modes (e.g., CDP to Selenium) |

**Sources:** [api/src/services/cdp/plugins/core/base-plugin.ts:9-20]()

---

## PluginManager Class

The `PluginManager` maintains the plugin registry and coordinates lifecycle event distribution across all registered plugins.

### Class Structure

```typescript
export class PluginManager {
  private plugins: Map<string, BasePlugin>;
  private service: CDPService;
  private logger: FastifyBaseLogger;
}
```

The `PluginManager` constructor requires both a `CDPService` instance and a logger:

```typescript
constructor(service: CDPService, logger: FastifyBaseLogger) {
  this.plugins = new Map();
  this.service = service;
  this.logger = logger;
}
```

**Sources:** [api/src/services/cdp/plugins/core/plugin-manager.ts:7-16]()

### Plugin Registration and Management

The `register()` method adds a plugin to the registry and injects the service:

```typescript
public register(plugin: BasePlugin): void {
  if (this.plugins.has(plugin.name)) {
    this.logger.warn(`Plugin with name ${plugin.name} is already registered. Overwriting.`);
  }

  plugin.setService(this.service);
  this.plugins.set(plugin.name, plugin);
  this.logger.info(`Registered plugin: ${plugin.name}`);
}
```

The `PluginManager` also provides `unregister(pluginName)` to remove plugins and `getPlugin<T>(pluginName)` to retrieve a specific instance with type safety.

**Sources:** [api/src/services/cdp/plugins/core/plugin-manager.ts:21-49]()

### Event Propagation Pattern

Each lifecycle event method in `PluginManager` follows a parallel execution pattern using `Promise.all()`. This ensures that one slow or failing plugin does not block others.

```mermaid
sequenceDiagram
    participant CDP as CDPService
    participant PM as PluginManager
    participant P1 as Plugin_A
    participant P2 as Plugin_B

    CDP->>PM: onPageCreated(page)
    activate PM
    PM->>P1: onPageCreated(page)
    PM->>P2: onPageCreated(page)
    Note over P1,P2: Execution happens in parallel
    P1-->>PM: resolve
    P2-->>PM: resolve
    deactivate PM
    PM-->>CDP: complete
```

**Diagram: Parallel Plugin Execution Sequence**

Example implementation from `onBrowserLaunch()`:

```typescript
public async onBrowserLaunch(browser: Browser): Promise<void> {
  const promises = Array.from(this.plugins.values()).map(async (plugin) => {
    try {
      await plugin.onBrowserLaunch(browser);
    } catch (error) {
      this.logger.error(`Error in plugin ${plugin.name}.onBrowserLaunch: ${error}`);
    }
  });
  await Promise.all(promises);
}
```

**Sources:** [api/src/services/cdp/plugins/core/plugin-manager.ts:96-105]()

---

## Integration with CDPService

`CDPService` integrates the `PluginManager` throughout its core methods.

### Initialization
The `PluginManager` is instantiated in the `CDPService` constructor.

**Sources:** [api/src/services/cdp/cdp.service.ts:169-169]()

### Event Triggering
`CDPService` triggers plugin hooks at critical junctions. For example, during session termination, it calls multiple hooks to ensure plugins can perform cleanup:

1. `onBeforeSessionEnd` is called at the start of the shutdown process.
2. `onShutdown` is called with the specific `ShutdownReason`.
3. `onSessionEnd` or `onAfterSessionEnd` are called once cleanup is finalized.

**Sources:** [api/src/services/cdp/plugins/core/plugin-manager.ts:68-91](), [api/src/services/cdp/plugins/core/plugin-manager.ts:193-216]()

---

## Creating Custom Plugins

To create a custom plugin, developers should follow the pattern outlined in the `PLUGIN_DEVELOPMENT.md` guide:

1. **Extend BasePlugin**: Create a class extending `BasePlugin`.
2. **Implement Hooks**: Override the necessary lifecycle methods.
3. **Register**: Use `cdpService.registerPlugin(instance)` to activate it.

### Example: Simple Hello World Plugin

```typescript
import { BasePlugin, PluginOptions } from './core/base-plugin.js';
import { Browser, Page } from 'puppeteer-core';

export class HelloWorldPlugin extends BasePlugin {
  constructor(options: PluginOptions) {
    super({ name: 'hello-world', ...options });
  }

  async onBrowserLaunch(browser: Browser): Promise<void> {
    console.log('Browser process started');
  }

  async onPageCreated(page: Page): Promise<void> {
    console.log(`New page created: ${page.url()}`);
  }
}
```

**Sources:** [docs/PLUGIN_DEVELOPMENT.md:9-30]()

---

# Page: Built-in Plugins

# Built-in Plugins

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [api/src/plugins/browser-session.ts](api/src/plugins/browser-session.ts)
- [api/src/plugins/browser-socket/handlers/cast.handler.ts](api/src/plugins/browser-socket/handlers/cast.handler.ts)
- [api/src/plugins/browser-socket/handlers/index.ts](api/src/plugins/browser-socket/handlers/index.ts)
- [api/src/plugins/browser.ts](api/src/plugins/browser.ts)
- [api/src/services/cdp/instrumentation/storage/in-memory-storage.ts](api/src/services/cdp/instrumentation/storage/in-memory-storage.ts)
- [api/src/services/cdp/instrumentation/storage/log-storage.interface.ts](api/src/services/cdp/instrumentation/storage/log-storage.interface.ts)
- [api/src/services/cdp/instrumentation/worker-events.ts](api/src/services/cdp/instrumentation/worker-events.ts)
- [api/src/services/websocket-registry.service.ts](api/src/services/websocket-registry.service.ts)
- [api/src/steel-browser-plugin.ts](api/src/steel-browser-plugin.ts)
- [api/src/types/fastify.d.ts](api/src/types/fastify.d.ts)
- [api/src/types/index.ts](api/src/types/index.ts)
- [api/src/types/websocket.ts](api/src/types/websocket.ts)
- [ui/vite.config.ts](ui/vite.config.ts)

</details>



This page documents the built-in plugins provided by steel-browser for logging, recording, and browser instrumentation. These plugins extend browser automation capabilities through the plugin system architecture and are integrated into the Fastify server lifecycle.

---

## Overview

The steel-browser system utilizes a set of built-in plugins to manage core services and extend browser functionality. These plugins are registered during the server initialization sequence in `api/src/steel-browser-plugin.ts` [api/src/steel-browser-plugin.ts:59-90]().

Key built-in plugins include:
- **Browser Instance Plugin**: Manages the `CDPService` lifecycle and log storage initialization [api/src/plugins/browser.ts:24-75]().
- **Browser Session Plugin**: Orchestrates the `SessionService` which links CDP, Selenium, and File services [api/src/plugins/browser-session.ts:5-13]().
- **Browser WebSocket Plugin**: Handles real-time communication for logs, recordings, and live views [api/src/plugins/browser-socket/browser-socket.ts]().
- **Logging & Storage**: Provides persistent event capture using DuckDB or in-memory backends [api/src/plugins/browser.ts:29-53]().

Sources: [api/src/steel-browser-plugin.ts:1-96](), [api/src/plugins/browser.ts:1-77]()

---

## Plugin Integration Architecture

The following diagram illustrates how built-in plugins bridge the Natural Language Space of "Browser Management" to the Code Entity Space of Fastify decorators and services.

```mermaid
graph TB
    subgraph "Fastify Instance (Code Entity Space)"
        FI["FastifyInstance"]
        
        subgraph "Decorators"
            D1["cdpService: CDPService"]
            D2["sessionService: SessionService"]
            D3["webSocketRegistry: WebSocketRegistryService"]
            D4["fileService: FileService"]
        end
    end
    
    subgraph "Built-in Plugins (Logic)"
        BP["browserInstancePlugin"]
        BSP["browserSessionPlugin"]
        BWS["browserWebSocket"]
        FSP["fileStoragePlugin"]
    end
    
    subgraph "Core Services"
        CDPS["CDPService"]
        SS["SessionService"]
        WRS["WebSocketRegistryService"]
    end

    BP -- "decorates" --> D1
    BSP -- "decorates" --> D2
    BWS -- "decorates" --> D3
    FSP -- "decorates" --> D4

    BP -- "instantiates" --> CDPS
    BSP -- "instantiates" --> SS
    BWS -- "instantiates" --> WRS

    SS -- "references" --> CDPS
    SS -- "references" --> D4
```

**Service-Plugin Mapping**

The `SteelBrowserConfig` is passed to the main plugin [api/src/steel-browser-plugin.ts:59](), which then distributes configuration to specific built-in plugins like `browserWebSocket` [api/src/steel-browser-plugin.ts:73-75]().

Sources: [api/src/steel-browser-plugin.ts:31-57](), [api/src/plugins/browser-session.ts:6-12](), [api/src/types/fastify.d.ts:8-15]()

---

## Logging & Storage Plugin

The `browserInstancePlugin` [api/src/plugins/browser.ts:24]() is responsible for initializing the log storage backend. It selects between persistent and ephemeral storage based on environment variables or configuration.

### Storage Selection Logic

| Environment Variable | Config Property | Storage Implementation | Description |
|----------------------|-----------------|------------------------|-------------|
| `LOG_STORAGE_ENABLED`| `logging.enableStorage` | `DuckDBStorage` | Persistent columnar storage for high-performance event analysis [api/src/plugins/browser.ts:36-44](). |
| N/A (Default)        | N/A             | `InMemoryStorage`      | Ephemeral storage with a fixed event limit (default 1000) [api/src/plugins/browser.ts:50-52](). |

### DuckDB Configuration
When `DuckDBStorage` is used, it is initialized with specific performance parameters:
- **maxThreads**: 1 [api/src/plugins/browser.ts:38]()
- **memoryLimit**: 128MB [api/src/plugins/browser.ts:39]()
- **writeBufferSize**: 200 events [api/src/plugins/browser.ts:42]()
- **flushInterval**: 2000ms [api/src/plugins/browser.ts:43]()

Sources: [api/src/plugins/browser.ts:25-53](), [api/src/services/cdp/instrumentation/storage/in-memory-storage.ts:14-20]()

---

## Browser Instrumentation & Worker Events

Instrumentation is automatically attached to browser targets. The `attachWorkerEvents` function demonstrates how internal listeners are registered to capture console logs and errors from Service Workers and other non-page targets.

```mermaid
graph LR
    subgraph "CDP Session (Target)"
        CS["CDPSession"]
    end

    subgraph "Instrumentation Logic"
        AWE["attachWorkerEvents"]
        RE["record()"]
    end

    subgraph "Event Types (Code Entities)"
        EC["BrowserEventType.Console"]
        EE["BrowserEventType.PageError"]
    end

    CS -- "Runtime.consoleAPICalled" --> AWE
    CS -- "Runtime.exceptionThrown" --> AWE
    AWE -- "format/serialize" --> RE
    RE -- "emits" --> EC
    RE -- "emits" --> EE
```

**Worker Event Data Flow**

When a console event occurs in a worker, the `serializeRemoteObject` utility [api/src/services/cdp/instrumentation/worker-events.ts:15]() converts complex CDP objects into strings before they are recorded by the `BrowserLogger` [api/src/services/cdp/instrumentation/worker-events.ts:18-24]().

Sources: [api/src/services/cdp/instrumentation/worker-events.ts:6-37](), [api/src/services/cdp/instrumentation/storage/log-storage.interface.ts:1-17]()

---

## WebSocket Handler Registry

The `browserWebSocket` plugin [api/src/steel-browser-plugin.ts:73]() registers a suite of default handlers that allow real-time interaction with browser sessions.

### Default Handlers
The system provides several built-in handlers defined in `api/src/plugins/browser-socket/handlers/index.ts` [api/src/plugins/browser-socket/handlers/index.ts:12-17]():

- **logsHandler**: Streams real-time logs from the storage backend.
- **castHandler**: Provides a live screen-cast of the browser session.
- **pageIdHandler**: Manages target-specific communication.
- **recordingHandler**: Streams DOM mutation events for session replay.

### Handler Registration Flow
1. **Plugin Initialization**: `browserWebSocket` receives `customHandlers` from `SteelBrowserConfig` [api/src/steel-browser-plugin.ts:74]().
2. **Registry Service**: Handlers are registered in the `WebSocketRegistryService` [api/src/services/websocket-registry.service.ts:6-8]().
3. **URL Matching**: The `matchHandler` method [api/src/services/websocket-registry.service.ts:14-23]() uses path-prefix matching to route incoming WebSocket connections to the correct logic.

Sources: [api/src/services/websocket-registry.service.ts:1-24](), [api/src/types/websocket.ts:12-27]()

---

## Plugin Lifecycle Hooks

The `browserInstancePlugin` decorates the Fastify instance with hooks that allow other parts of the system to react to browser lifecycle events.

- **registerCDPLaunchHook**: Allows registration of functions that run before the browser starts [api/src/plugins/browser.ts:58-63]().
- **registerCDPShutdownHook**: Allows registration of cleanup functions that run after the browser stops [api/src/plugins/browser.ts:64-69]().
- **onListen Hook**: The plugin automatically triggers `cdpService.launch()` when the Fastify server starts listening [api/src/plugins/browser.ts:71-74]().

Sources: [api/src/plugins/browser.ts:58-74](), [api/src/steel-browser-plugin.ts:37-41]()

---

## Summary of Configuration Options

Built-in plugins are configured via the `SteelBrowserConfig` interface passed during registration:

| Property | Sub-property | Description |
|----------|--------------|-------------|
| `fileStorage` | `maxSizePerSession` | Limits disk usage for session files [api/src/steel-browser-plugin.ts:47-49](). |
| `logging` | `enableStorage` | Toggles persistent DuckDB storage [api/src/steel-browser-plugin.ts:52](). |
| `logging` | `storagePath` | Custom path for the `.duckdb` file [api/src/steel-browser-plugin.ts:53](). |
| `logging` | `enableLogsRoutes` | Toggles the `/v1/logs` API endpoints [api/src/steel-browser-plugin.ts:55](). |
| `customWsHandlers`| N/A | Array of user-defined WebSocket handlers [api/src/steel-browser-plugin.ts:50](). |

Sources: [api/src/steel-browser-plugin.ts:46-57](), [api/src/plugins/browser.ts:25-34]()

---

# Page: Real-time Communication

# Real-time Communication

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [api/src/plugins/browser-socket/browser-socket.ts](api/src/plugins/browser-socket/browser-socket.ts)
- [api/src/plugins/browser-socket/casting.handler.ts](api/src/plugins/browser-socket/casting.handler.ts)
- [api/src/plugins/browser-socket/handlers/logs.handler.ts](api/src/plugins/browser-socket/handlers/logs.handler.ts)
- [api/src/plugins/browser-socket/handlers/pageId.handler.ts](api/src/plugins/browser-socket/handlers/pageId.handler.ts)
- [api/src/plugins/browser-socket/handlers/recording.handler.ts](api/src/plugins/browser-socket/handlers/recording.handler.ts)
- [api/src/templates/live-session-streamer.ejs](api/src/templates/live-session-streamer.ejs)
- [api/src/types/casting.ts](api/src/types/casting.ts)
- [api/src/utils/casting.ts](api/src/utils/casting.ts)
- [api/src/utils/retry.ts](api/src/utils/retry.ts)

</details>



Steel Browser provides a real-time communication layer that enables clients to receive live updates about browser activity and interact with sessions. This system is built on WebSocket connections that stream events from the browser to connected clients, enabling interactive debugging, monitoring, and live "casting" of browser sessions.

For detailed information about WebSocket endpoint implementation and the connection upgrade mechanism, see [WebSocket API](#10.1). For information about how browser events are captured and logged, see [Browser Instrumentation & Logging](#10.2).

## Purpose and Scope

This document covers the real-time event streaming architecture in Steel Browser, including:

- Event emission from the `CDPService` and `SessionService`.
- WebSocket endpoint handlers and routing via the `browserWebSocket` plugin.
- Live session streaming ("casting") and interactive input handling.
- Integration between browser instrumentation and WebSocket delivery.

For information about the CDP WebSocket proxy for direct browser control, see [CDP Integration](#8.1). For session management APIs, see [Session Management API](#4.1).

## Architecture Overview

The real-time communication system consists of three layers:

1.  **Event Emission Layer**: `CDPService` captures browser events via instrumentation and emits them through Node.js `EventEmitter` [api/src/services/cdp/cdp.service.ts:80-183]().
2.  **WebSocket Server Layer**: `browserWebSocket` plugin manages WebSocket connections and routes them to appropriate handlers using a `WebSocketRegistryService` [api/src/plugins/browser-socket/browser-socket.ts:15-37]().
3.  **Handler Layer**: Specialized handlers (`logsHandler`, `recordingHandler`, `handleCastSession`) subscribe to events or interact with Puppeteer to stream data to clients.

**Sources**: [api/src/services/cdp/cdp.service.ts:80-183](), [api/src/plugins/browser-socket/browser-socket.ts:1-73]()

### Event Emission and Routing Architecture

```mermaid
graph TB
    subgraph "Browser Layer"
        Chrome["Chrome Browser"]
        Pages["Browser Pages"]
    end
    
    subgraph "Event Source Layer"
        CDP["CDPService<br/>(EventEmitter)"]
        Sess["SessionService"]
    end
    
    subgraph "WebSocket Registry Layer"
        Registry["WebSocketRegistryService"]
        WSS["WebSocketServer<br/>(wss)"]
    end
    
    subgraph "Handlers [api/src/plugins/browser-socket/handlers/]"
        LH["logsHandler<br/>/v1/sessions/logs"]
        RH["recordingHandler<br/>/v1/sessions/recording"]
        PH["pageIdHandler<br/>/v1/sessions/pageId"]
        CH["handleCastSession<br/>/v1/sessions/:id/cast"]
    end
    
    Chrome --> CDP
    CDP --> LH
    CDP --> RH
    CDP --> PH
    Sess --> CH
    
    WSS --> Registry
    Registry --> LH
    Registry --> RH
    Registry --> PH
    Registry --> CH
```

**Sources**: [api/src/plugins/browser-socket/browser-socket.ts:25-70](), [api/src/plugins/browser-socket/handlers/logs.handler.ts:28-39](), [api/src/plugins/browser-socket/casting.handler.ts:18-25]()

## Live Session Casting

Steel Browser supports high-performance live streaming of browser sessions via the `handleCastSession` handler. This allows users to view and interact with a remote browser in real-time.

### Casting Architecture

The casting system uses Puppeteer's `Page.startScreencast` to capture frames and forwards them over WebSockets. It also translates client-side mouse and keyboard events back into browser actions.

```mermaid
sequenceDiagram
    participant Client as "Web UI / Client"
    participant CastHandler as "handleCastSession"
    participant Puppeteer as "Puppeteer-core"
    participant Browser as "Chromium Instance"

    Client->>CastHandler: WS Connect (/cast)
    CastHandler->>Puppeteer: connect({browserWSEndpoint})
    CastHandler->>Puppeteer: page.target().createCDPSession()
    CastHandler->>Puppeteer: client.send('Page.startScreencast')
    
    loop Stream Frames
        Browser->>CastHandler: screencastFrame event
        CastHandler->>Client: Binary/JSON Frame Data
    end

    loop Interaction
        Client->>CastHandler: MouseEvent / KeyEvent
        CastHandler->>Puppeteer: page.mouse.move() / page.keyboard.down()
    end
```

**Sources**: [api/src/plugins/browser-socket/casting.handler.ts:176-250](), [api/src/plugins/browser-socket/casting.handler.ts:444-510](), [api/src/types/casting.ts:1-36]()

### Interactive Events

The system supports several event types for remote interaction:
- **MouseEvents**: Coordinates, button states, and click counts [api/src/types/casting.ts:1-14]().
- **KeyEvents**: Key codes, text input, and modifiers [api/src/types/casting.ts:16-27]().
- **Navigation**: Back, forward, refresh, and direct URL navigation [api/src/types/casting.ts:29-36]().

## WebSocket Handler System

The `browserWebSocket` plugin initializes a `WebSocketServer` in `noServer` mode [api/src/plugins/browser-socket/browser-socket.ts:13]() and hooks into the Fastify server's `upgrade` event [api/src/plugins/browser-socket/browser-socket.ts:39]().

### Default Handlers

Steel Browser includes several default handlers registered in the `WebSocketRegistryService`:

| Handler | Path | Description |
| :--- | :--- | :--- |
| `logsHandler` | `/v1/sessions/logs` | Streams instrumentation logs (console, network) [api/src/plugins/browser-socket/handlers/logs.handler.ts:29](). |
| `recordingHandler` | `/v1/sessions/recording` | Streams rrweb-compatible DOM recording events [api/src/plugins/browser-socket/handlers/recording.handler.ts:32](). |
| `pageIdHandler` | `/v1/sessions/pageId` | Notifies clients of the currently active page ID [api/src/plugins/browser-socket/handlers/pageId.handler.ts:28](). |
| `handleCastSession` | `/v1/sessions/:id/cast` | Provides the live video feed and interaction layer [api/src/plugins/browser-socket/casting.handler.ts:18](). |

### Connection Upgrade Flow

When an `upgrade` request arrives, the registry attempts to match the URL:
1.  **Matched**: The specific handler takes control of the socket [api/src/plugins/browser-socket/browser-socket.ts:56]().
2.  **Unmatched**: The request is proxied directly to the CDP WebSocket endpoint [api/src/plugins/browser-socket/browser-socket.ts:64]().

**Sources**: [api/src/plugins/browser-socket/browser-socket.ts:52-70]()

## Integration with UI Dashboard

The real-time communication system powers the **Steel Session Player**, a specialized UI for monitoring sessions.

- **Canvas Rendering**: Uses a `<canvas>` element to display screencast frames [api/src/templates/live-session-streamer.ejs:123-130]().
- **Tab Management**: Displays active browser tabs and allows switching via the `tabList` event [api/src/plugins/browser-socket/casting.handler.ts:118-143]().
- **URL Bar**: Reflects the current browser URL and allows remote navigation [api/src/templates/live-session-streamer.ejs:69-101]().

**Sources**: [api/src/templates/live-session-streamer.ejs:1-130](), [api/src/plugins/browser-socket/casting.handler.ts:118-143]()

## Summary

The real-time communication system in Steel Browser provides a robust architecture for live session interaction. Key components include:

- **CDPService**: The central hub for browser event emission [api/src/services/cdp/cdp.service.ts:80]().
- **WebSocketRegistryService**: Manages the routing of WebSocket connections to specialized handlers [api/src/plugins/browser-socket/browser-socket.ts:25]().
- **Casting Handler**: Leverages Puppeteer and CDP to provide a low-latency interactive stream [api/src/plugins/browser-socket/casting.handler.ts:18]().
- **Instrumentation Handlers**: Provide real-time access to logs and session recordings.

For details on the specific endpoints, see [WebSocket API](#10.1). For the underlying event capture logic, see [Browser Instrumentation & Logging](#10.2).

---

# Page: WebSocket API

# WebSocket API

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [api/src/plugins/browser-socket/browser-socket.ts](api/src/plugins/browser-socket/browser-socket.ts)
- [api/src/plugins/browser-socket/casting.handler.ts](api/src/plugins/browser-socket/casting.handler.ts)
- [api/src/plugins/browser-socket/handlers/cast.handler.ts](api/src/plugins/browser-socket/handlers/cast.handler.ts)
- [api/src/plugins/browser-socket/handlers/index.ts](api/src/plugins/browser-socket/handlers/index.ts)
- [api/src/plugins/browser-socket/handlers/logs.handler.ts](api/src/plugins/browser-socket/handlers/logs.handler.ts)
- [api/src/plugins/browser-socket/handlers/pageId.handler.ts](api/src/plugins/browser-socket/handlers/pageId.handler.ts)
- [api/src/plugins/browser-socket/handlers/recording.handler.ts](api/src/plugins/browser-socket/handlers/recording.handler.ts)
- [api/src/services/websocket-registry.service.ts](api/src/services/websocket-registry.service.ts)
- [api/src/steel-browser-plugin.ts](api/src/steel-browser-plugin.ts)
- [api/src/templates/live-session-streamer.ejs](api/src/templates/live-session-streamer.ejs)
- [api/src/types/casting.ts](api/src/types/casting.ts)
- [api/src/types/index.ts](api/src/types/index.ts)
- [api/src/types/websocket.ts](api/src/types/websocket.ts)
- [api/src/utils/casting.ts](api/src/utils/casting.ts)
- [api/src/utils/retry.ts](api/src/utils/retry.ts)
- [ui/vite.config.ts](ui/vite.config.ts)

</details>



## Purpose and Scope

This document describes the WebSocket API infrastructure in `steel-browser`, which enables real-time streaming of browser events, recordings, and live browser session "casting" (streaming and interaction). The WebSocket layer sits on top of the `CDPService` [api/src/services/cdp/cdp.service.ts:25]() and provides specialized endpoints for different types of real-time data.

For information about the underlying browser instrumentation that generates events, see [Browser Instrumentation & Logging](#10.2). For session management, see [Session Management API](#4.1).

## WebSocket Plugin Architecture

The WebSocket infrastructure is implemented as a Fastify plugin called `browser-socket`, which establishes a WebSocket server and registers specialized handlers.

```mermaid
graph TB
    FastifyServer["FastifyInstance"]
    BrowserSocketPlugin["browser-websocket plugin<br/>(browser-socket.ts)"]
    WSS["WebSocketServer<br/>(ws library)"]
    Registry["WebSocketRegistryService"]
    
    subgraph "Handler Registration"
        DefaultHandlers["defaultHandlers[]"]
        LogsHandler["logsHandler"]
        RecordingHandler["recordingHandler"]
        PageIdHandler["pageIdHandler"]
        CastHandler["castHandler"]
    end
    
    subgraph "Request Processing"
        UpgradeEvent["'upgrade' event"]
        MatchHandler["registry.matchHandler()"]
        HandlerExec["handler.handler()"]
        CDPProxy["cdpService.proxyWebSocket()"]
    end
    
    FastifyServer -->|"registers"| BrowserSocketPlugin
    BrowserSocketPlugin -->|"creates"| WSS
    BrowserSocketPlugin -->|"creates"| Registry
    BrowserSocketPlugin -->|"registers"| DefaultHandlers
    
    DefaultHandlers -->|"contains"| LogsHandler
    DefaultHandlers -->|"contains"| RecordingHandler
    DefaultHandlers -->|"contains"| PageIdHandler
    DefaultHandlers -->|"contains"| CastHandler
    
    FastifyServer -->|"emits"| UpgradeEvent
    UpgradeEvent -->|"URL matching"| MatchHandler
    MatchHandler -->|"handler found"| HandlerExec
    MatchHandler -->|"no handler"| CDPProxy
```

**Sources:** [api/src/plugins/browser-socket/browser-socket.ts:15-74](), [api/src/plugins/browser-socket/handlers/index.ts:1-10](), [api/src/services/websocket-registry.service.ts:1-10]()

### Plugin Initialization

The `browser-websocket` plugin initializes during Fastify server startup:

1.  **Browser Launch**: Ensures `cdpService` has launched a browser instance [api/src/plugins/browser-socket/browser-socket.ts:19-23]().
2.  **Registry Creation**: Creates a `WebSocketRegistryService` to manage handler routing [api/src/plugins/browser-socket/browser-socket.ts:25]().
3.  **Handler Registration**: Registers default handlers (logs, recording, casting) and any custom handlers provided in `BrowserSocketOptions` [api/src/plugins/browser-socket/browser-socket.ts:27-35]().
4.  **Upgrade Listener**: Attaches an `upgrade` event listener to the HTTP server to intercept WebSocket requests [api/src/plugins/browser-socket/browser-socket.ts:39-70]().

### Handler Interface

All WebSocket handlers implement the `WebSocketHandler` interface [api/src/types/websocket.ts:12-21]():

```typescript
export interface WebSocketHandler {
  path: string; // URL path pattern
  handler: (
    request: IncomingMessage,
    socket: Duplex,
    head: Buffer,
    context: WebSocketHandlerContext,
  ) => void | Promise<void>;
}
```

The `WebSocketHandlerContext` [api/src/types/websocket.ts:23-27]() provides access to the `FastifyInstance`, the shared `WebSocketServer` (`wss`), and URL query parameters.

**Sources:** [api/src/plugins/browser-socket/browser-socket.ts:46-50](), [api/src/types/websocket.ts:1-27]()

## Available WebSocket Endpoints

| Endpoint | Purpose | Event Source | Payload Format |
| :--- | :--- | :--- | :--- |
| `/v1/sessions/logs` | Stream browser console/network logs | `EmitEvent.Log` | JSON array of log objects |
| `/v1/sessions/recording` | Stream rrweb recording events | `EmitEvent.Recording` | JSON array of events |
| `/v1/sessions/pageId` | Stream current page ID changes | `"pageId"` event | JSON object `{ pageId: string }` |
| `/v1/sessions/:id/cast` | Live browser streaming/interaction | `Page.startScreencast` | Binary (JPEG) + JSON control |
| **CDP Proxy** | Direct CDP protocol access | Browser CDP | Raw CDP protocol messages |

**Sources:** [api/src/plugins/browser-socket/handlers/logs.handler.ts:29](), [api/src/plugins/browser-socket/handlers/recording.handler.ts:32](), [api/src/plugins/browser-socket/handlers/pageId.handler.ts:28](), [api/src/plugins/browser-socket/handlers/cast.handler.ts:1-20]()

### Live Session Streaming (Casting)

The `handleCastSession` handler provides a high-performance live view of a browser session, allowing for both visual streaming and remote interaction.

**Key Features:**
*   **Screencasting**: Uses Chrome's `Page.startScreencast` to stream JPEG frames of the browser window [api/src/plugins/browser-socket/casting.handler.ts:300-315]().
*   **Bi-directional Interaction**: Supports `mouseEvent`, `keyEvent`, and `navigation` events sent from the client to control the browser [api/src/plugins/browser-socket/casting.handler.ts:340-420]().
*   **Tab Management**: Supports tab discovery mode, tab switching, and closing tabs [api/src/plugins/browser-socket/casting.handler.ts:118-143]().

```mermaid
sequenceDiagram
    participant Client as "Client (UI)"
    participant Cast as "casting.handler.ts"
    participant Puppeteer as "puppeteer-core"
    participant Browser as "Chromium Instance"

    Client->>Cast: Upgrade to WS (/v1/sessions/:id/cast)
    Cast->>Puppeteer: connect({ browserWSEndpoint })
    Cast->>Browser: Page.startScreencast
    
    loop Stream
        Browser->>Cast: Screencast Frame (Base64)
        Cast->>Client: JSON { type: "screencastFrame", data: ... }
    end

    Client->>Cast: MouseEvent { x, y, button }
    Cast->>Browser: page.mouse.move/click
```

**Sources:** [api/src/plugins/browser-socket/casting.handler.ts:18-116](), [api/src/plugins/browser-socket/casting.handler.ts:176-184](), [api/src/types/casting.ts:1-41]()

### Logs and Recording Handlers

These handlers function as event forwarders between the `CDPService` and the connected WebSocket clients.

*   **Logs**: Listens for `EmitEvent.Log` and sends JSON payloads [api/src/plugins/browser-socket/handlers/logs.handler.ts:10-16]().
*   **Recording**: Listens for `EmitEvent.Recording` and sends arrays of recorded events [api/src/plugins/browser-socket/handlers/recording.handler.ts:10-16]().

**Sources:** [api/src/plugins/browser-socket/handlers/logs.handler.ts:1-40](), [api/src/plugins/browser-socket/handlers/recording.handler.ts:1-43]()

## Connection Lifecycle and Cleanup

To prevent resource exhaustion, the WebSocket API implements strict cleanup logic:

1.  **Heartbeats**: The cast handler maintains a heartbeat to detect dead connections [api/src/plugins/browser-socket/casting.handler.ts:280-295]().
2.  **Listener Removal**: Handlers remove their listeners from `cdpService` when the socket closes [api/src/plugins/browser-socket/handlers/logs.handler.ts:22-25]().
3.  **Browser Disconnection**: The casting handler explicitly calls `browser.disconnect()` and stops screencasts upon socket closure [api/src/plugins/browser-socket/casting.handler.ts:63-116]().
4.  **Error Handling**: Errors in the upgrade process result in socket destruction to prevent hanging sockets [api/src/plugins/browser-socket/browser-socket.ts:55-60]().

**Sources:** [api/src/plugins/browser-socket/browser-socket.ts:55-69](), [api/src/plugins/browser-socket/casting.handler.ts:63-116]()

## CDP WebSocket Proxy

If a WebSocket upgrade request does not match any registered handler (e.g., `/v1/sessions/logs`), the system defaults to proxying the request directly to the internal browser's CDP endpoint [api/src/plugins/browser-socket/browser-socket.ts:61-69](). This allows standard automation tools (like Playwright or Puppeteer) to connect directly to `steel-browser` using its primary WebSocket port.

**Sources:** [api/src/plugins/browser-socket/browser-socket.ts:64-68]()

---

# Page: Browser Instrumentation & Logging

# Browser Instrumentation & Logging

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [api/src/plugins/browser.ts](api/src/plugins/browser.ts)
- [api/src/services/cdp/instrumentation/browser-logger.ts](api/src/services/cdp/instrumentation/browser-logger.ts)
- [api/src/services/cdp/instrumentation/cdp-events.ts](api/src/services/cdp/instrumentation/cdp-events.ts)
- [api/src/services/cdp/instrumentation/page-events.ts](api/src/services/cdp/instrumentation/page-events.ts)
- [api/src/services/cdp/instrumentation/storage/duckdb-storage.ts](api/src/services/cdp/instrumentation/storage/duckdb-storage.ts)
- [api/src/services/cdp/instrumentation/storage/in-memory-storage.ts](api/src/services/cdp/instrumentation/storage/in-memory-storage.ts)
- [api/src/services/cdp/instrumentation/storage/log-storage.interface.ts](api/src/services/cdp/instrumentation/storage/log-storage.interface.ts)
- [api/src/services/cdp/instrumentation/storage/safe-json.ts](api/src/services/cdp/instrumentation/storage/safe-json.ts)
- [api/src/services/cdp/instrumentation/target-manager.ts](api/src/services/cdp/instrumentation/target-manager.ts)
- [api/src/services/cdp/instrumentation/types.ts](api/src/services/cdp/instrumentation/types.ts)
- [api/src/services/cdp/instrumentation/utils.ts](api/src/services/cdp/instrumentation/utils.ts)
- [api/src/services/cdp/instrumentation/worker-events.ts](api/src/services/cdp/instrumentation/worker-events.ts)
- [api/src/types/enums.ts](api/src/types/enums.ts)

</details>



This document describes the browser instrumentation and logging system in Steel Browser. This system captures comprehensive browser events including console logs, network requests, page navigations, and errors, making them available both in real-time via WebSocket streams and through persistent storage.

---

## Purpose and Architecture

The instrumentation system monitors all browser targets (pages, service workers, shared workers) and captures their events into structured log records. These logs are emitted as real-time events and persisted to storage backends.

### Core Components

The instrumentation architecture consists of three primary components:

| Component | Type | Purpose |
|-----------|------|---------|
| `TargetInstrumentationManager` | Target Monitor | Attaches/detaches from browser targets, manages CDP domain lifecycle. |
| `BrowserLogger` | Event Recorder | Captures events, transforms them to structured records, emits/stores. |
| `LogStorage` | Storage Interface | Persists logs to DuckDB or in-memory store. |

```mermaid
graph TB
    subgraph BrowserProcess["Browser Process (Puppeteer)"]
        BrowserTargets["Browser Targets<br/>(Page, Worker, Webview)"]
        CDP["Chrome DevTools Protocol"]
    end
    
    subgraph InstrumentationLayer["Instrumentation Layer"]
        TargetInstrMgr["TargetInstrumentationManager<br/>target-manager.ts"]
        BrowserLogger["BrowserLogger<br/>browser-logger.ts"]
        PageEvents["page-events.ts"]
        CDPEvents["cdp-events.ts"]
    end
    
    subgraph StorageLayer["Storage Layer"]
        LogStorageIface["LogStorage Interface"]
        DuckDB["DuckDBStorage<br/>duckdb-storage.ts"]
        InMemory["InMemoryStorage<br/>in-memory-storage.ts"]
    end
    
    subgraph EventDistribution["Event Distribution"]
        EventEmitter["EventEmitter<br/>EmitEvent.Log"]
    end
    
    BrowserTargets -->|"CDP events"| CDP
    CDP -->|"Network, Runtime, Log"| TargetInstrMgr
    TargetInstrMgr -->|"attach()"| PageEvents
    TargetInstrMgr -->|"attach()"| CDPEvents
    PageEvents -->|"record()"| BrowserLogger
    CDPEvents -->|"record()"| BrowserLogger
    
    BrowserLogger -->|"write()"| LogStorageIface
    BrowserLogger -->|"emit(EmitEvent.Log)"| EventEmitter
    
    LogStorageIface -.->|"implements"| DuckDB
    LogStorageIface -.->|"implements"| InMemory
```

**Sources:**
- [api/src/services/cdp/instrumentation/target-manager.ts:14-26]()
- [api/src/services/cdp/instrumentation/browser-logger.ts:37-112]()
- [api/src/plugins/browser.ts:24-55]()

---

## TargetInstrumentationManager

The `TargetInstrumentationManager` is responsible for monitoring browser targets and attaching instrumentation. It tracks the lifecycle of pages, service workers, and webviews.

### Target Lifecycle and Domain Management

When a target is attached via `attach(target, type)`, the manager creates a dedicated CDP session and enables specific domains based on the target type:

- **PAGE / BACKGROUND_PAGE**: Enables `Runtime`, `Log`, and `Network` [api/src/services/cdp/instrumentation/target-manager.ts:147-152]().
- **SERVICE_WORKER**: Enables `Runtime` and `Log`. `Network` is only enabled if it's an extension worker [api/src/services/cdp/instrumentation/target-manager.ts:154-161]().

```mermaid
sequenceDiagram
    participant TM as TargetInstrumentationManager
    participant T as Target (Puppeteer)
    participant S as CDPSession
    participant L as BrowserLogger
    
    TM->>T: attach(target, type)
    T->>S: createCDPSession()
    TM->>S: session.send("Runtime.enable")
    TM->>S: session.send("Network.enable")
    TM->>TM: page-events.attachPageEvents(page, session, logger)
    TM->>TM: cdp-events.attachCDPEvents(session, logger)
```

**Sources:**
- [api/src/services/cdp/instrumentation/target-manager.ts:28-116]()
- [api/src/services/cdp/instrumentation/target-manager.ts:129-175]()

---

## Event Capture Implementation

### Page & Network Events
The `attachPageEvents` function [api/src/services/cdp/instrumentation/page-events.ts:24-30]() handles the bulk of high-level instrumentation:
- **Navigation**: Listens for `framenavigated` to record URL changes [api/src/services/cdp/instrumentation/page-events.ts:35-44]().
- **Network**: Uses CDP `Network.requestWillBeSent` and `Network.responseReceived` instead of Puppeteer's high-level events to ensure same-tab navigations and POST data are captured [api/src/services/cdp/instrumentation/page-events.ts:62-110]().
- **Response Bodies**: If `dangerouslyLogRequestDetails` is enabled, it fetches bodies via `Network.getResponseBody` for text-based MIME types [api/src/services/cdp/instrumentation/page-events.ts:115-143]().

### Console & Errors
- **Console**: Captures `Runtime.consoleAPICalled`. It serializes remote objects and formats stack traces into a string location [api/src/services/cdp/instrumentation/page-events.ts:158-170]().
- **Exceptions**: Captures `Runtime.exceptionThrown` for uncaught JavaScript errors [api/src/services/cdp/instrumentation/page-events.ts:172-181]().

### Protocol Tracing (CDP Events)
The `attachCDPEvents` function wraps the `session.send` method to log every command sent to the browser and its result/duration [api/src/services/cdp/instrumentation/cdp-events.ts:9-51](). It also listens for the generic `event` to log incoming CDP notifications, excluding redundant network events [api/src/services/cdp/instrumentation/cdp-events.ts:67-75]().

**Sources:**
- [api/src/services/cdp/instrumentation/page-events.ts:1-202]()
- [api/src/services/cdp/instrumentation/cdp-events.ts:1-76]()

---

## BrowserLogger

The `BrowserLogger` created by `createBrowserLogger` [api/src/services/cdp/instrumentation/browser-logger.ts:37]() acts as the central hub.

- **Context Management**: Allows attaching metadata (like `sessionId`) to all events via `setContext` [api/src/services/cdp/instrumentation/browser-logger.ts:47-56]().
- **Event Recording**: The `record(event)` method merges the event with the current context and dispatches it to:
    1. **Console**: If `enableConsoleLogging` is true [api/src/services/cdp/instrumentation/browser-logger.ts:63-65]().
    2. **Storage**: Calls `storage.write(event, context)` [api/src/services/cdp/instrumentation/browser-logger.ts:67-71]().
    3. **Real-time**: Emits `EmitEvent.Log` via an internal `EventEmitter` [api/src/services/cdp/instrumentation/browser-logger.ts:73]().

**Sources:**
- [api/src/services/cdp/instrumentation/browser-logger.ts:37-112]()
- [api/src/types/enums.ts:27-31]()

---

## Log Storage in DuckDB

Steel Browser uses **DuckDB** for high-performance analytical log storage.

### Schema
The `browser_events` table is designed for fast querying and filtering:

| Column | Type | Description |
|--------|------|-------------|
| `id` | VARCHAR | Primary key (UUID) |
| `timestamp` | TIMESTAMP | Event occurrence time |
| `event_type` | VARCHAR | Type (Request, Console, etc.) |
| `page_id` | VARCHAR | Target identifier |
| `data` | JSON | The serialized `BrowserEventUnion` |
| `context` | JSON | Session metadata |

[api/src/services/cdp/instrumentation/storage/duckdb-storage.ts:86-96]()

### Write Buffering
To minimize CPU impact and disk I/O spikes, `DuckDBStorage` implements a write buffer:
- Events are batched until the `writeBufferSize` (default 200) is reached [api/src/services/cdp/instrumentation/storage/duckdb-storage.ts:42, 163]().
- A periodic flush occurs every `writeBufferFlushInterval` (default 2000ms) [api/src/services/cdp/instrumentation/storage/duckdb-storage.ts:43, 120-127]().

### Configuration
Storage is initialized in the browser plugin based on environment variables or `logging` config [api/src/plugins/browser.ts:25-47]().

| Setting | Default | Env Var |
|---------|---------|---------|
| Enable Storage | `false` | `LOG_STORAGE_ENABLED` |
| Storage Path | `.../logs.duckdb` | `LOG_STORAGE_PATH` |

**Sources:**
- [api/src/services/cdp/instrumentation/storage/duckdb-storage.ts:11-116]()
- [api/src/plugins/browser.ts:24-53]()

---

## Event Types Reference

The system uses `BrowserEventType` to categorize all captured data:

| Event Type | Description |
|------------|-------------|
| `Request` | Outgoing HTTP request metadata [api/src/services/cdp/instrumentation/types.ts:11-20]() |
| `Response` | Incoming HTTP response metadata [api/src/services/cdp/instrumentation/types.ts:22-31]() |
| `ResponseBody` | Captured response content (if enabled) [api/src/services/cdp/instrumentation/types.ts:33-40]() |
| `Console` | `console.*` output from the page [api/src/services/cdp/instrumentation/types.ts:47-50]() |
| `PageError` | Uncaught JS exceptions [api/src/services/cdp/instrumentation/types.ts:52-59]() |
| `CDPCommand` | Protocol command sent to browser [api/src/services/cdp/instrumentation/types.ts:74-81]() |
| `CDPEvent` | Protocol notification from browser [api/src/services/cdp/instrumentation/types.ts:66-72]() |

**Sources:**
- [api/src/types/enums.ts:10-25]()
- [api/src/services/cdp/instrumentation/types.ts:4-115]()

---

# Page: UI Dashboard

# UI Dashboard

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [ui/src/components/sessions/session-console/session-logs.tsx](ui/src/components/sessions/session-console/session-logs.tsx)
- [ui/src/components/sessions/session-viewer/session-viewer.tsx](ui/src/components/sessions/session-viewer/session-viewer.tsx)
- [ui/src/containers/session-container.tsx](ui/src/containers/session-container.tsx)
- [ui/src/contexts/sessions-context/sessions-context.tsx](ui/src/contexts/sessions-context/sessions-context.tsx)
- [ui/src/contexts/sessions-context/sessions-context.types.ts](ui/src/contexts/sessions-context/sessions-context.types.ts)
- [ui/src/lib/query-client.ts](ui/src/lib/query-client.ts)
- [ui/src/main.tsx](ui/src/main.tsx)
- [ui/src/root-layout.tsx](ui/src/root-layout.tsx)

</details>



The UI Dashboard is a React-based web application that provides a graphical interface for managing and monitoring browser automation sessions. It serves as the primary user interface for interacting with the steel-browser API, enabling session creation, real-time monitoring, and session management through an intuitive web interface.

For programmatic API access and automation workflows, see [API Reference](#12). For details on the underlying session management logic, see [Session Management API](#4.1).

---

## Purpose and Scope

The UI Dashboard provides:

- **Session Management Interface**: Create, monitor, and release browser sessions through a visual interface. For details, see [Session Management Interface](#11.1).
- **Real-time Monitoring**: Live session details, browser state, and event streaming via WebSockets.
- **Type-Safe API Client**: Auto-generated TypeScript client from OpenAPI specifications. For details, see [Generated API Client](#11.2).
- **Responsive UI Components**: Built with Radix UI and Tailwind CSS for modern UX.

The UI workspace is located at [ui/]() within the steel-browser monorepo and runs independently on port 5173 during development.

---

## Architecture Overview

The UI Dashboard follows a modern React architecture with clear separation between the presentation layer and API communication layer.

### UI Component to API Mapping

The following diagram bridges the natural language UI concepts to the specific code entities responsible for their implementation.

```mermaid
graph TD
    subgraph "Natural Language Space"
        SessionList["Session List View"]
        LiveView["Live Browser View"]
        ConsoleView["Log Console"]
        SessionActions["Session Control"]
    end

    subgraph "Code Entity Space"
        SessionList --> SessionProvider["SessionsProvider<br/>(sessions-context.tsx)"]
        SessionProvider --> getSessions["getSessions()<br/>(services.gen.ts)"]
        
        LiveView --> SessionViewer["SessionViewer<br/>(session-viewer.tsx)"]
        SessionViewer --> debugUrl["session.debugUrl<br/>(types.gen.ts)"]
        
        ConsoleView --> SessionLogs["SessionLogs<br/>(session-logs.tsx)"]
        SessionLogs --> WSLogs["WebSocket /v1/sessions/logs"]
        
        SessionActions --> useRelease["useReleaseSessionMutation<br/>(sessions-context.tsx)"]
        useRelease --> releaseAPI["releaseBrowserSession()<br/>(services.gen.ts)"]
    end
```

**Sources:**
- [ui/src/contexts/sessions-context/sessions-context.tsx:24-94]()
- [ui/src/components/sessions/session-viewer/session-viewer.tsx:12-195]()
- [ui/src/components/sessions/session-console/session-logs.tsx:4-88]()

---

## Session Management Interface

The dashboard organizes session monitoring through a unified container that manages the layout between the browser view and the developer console.

- **Session Context**: The `SessionsProvider` manages the global state for the active session and provides hooks like `useSession` and `useReleaseSessionMutation` to child components [ui/src/contexts/sessions-context/sessions-context.tsx:24-81]().
- **Live Viewer**: The `SessionViewer` component renders an `<iframe>` targeting the session's `debugUrl` [ui/src/components/sessions/session-viewer/session-viewer.tsx:184-193](). It implements a clipboard bridge to allow copy-paste operations between the host OS and the remote browser [ui/src/components/sessions/session-viewer/session-viewer.tsx:24-86]().
- **Real-time Logs**: The `SessionLogs` component establishes a WebSocket connection to stream browser events, network requests, and console logs directly to the UI [ui/src/components/sessions/session-console/session-logs.tsx:8-26]().

For details, see [Session Management Interface](#11.1).

**Sources:**
- [ui/src/containers/session-container.tsx:9-51]()
- [ui/src/components/sessions/session-viewer/session-viewer.tsx:12-195]()
- [ui/src/components/sessions/session-console/session-logs.tsx:4-88]()

---

## Generated API Client

The UI uses a fully type-safe API client generated from the OpenAPI specification exposed by the Fastify backend. This eliminates manual API client maintenance and ensures type safety across the stack.

### Client-Side Data Flow

```mermaid
graph LR
    subgraph "API Client (steel-client)"
        ServiceFunc["services.gen.ts<br/>(e.g. getSessionDetails)"]
        Types["types.gen.ts<br/>(e.g. SessionDetails)"]
    end

    subgraph "React State (TanStack Query)"
        QueryClient["queryClient.ts"]
        SessionsCtx["SessionsProvider<br/>(sessions-context.tsx)"]
    end

    subgraph "UI Components"
        SContainer["SessionContainer"]
        SViewer["SessionViewer"]
    end

    ServiceFunc --> SessionsCtx
    Types --> SessionsCtx
    SessionsCtx --> QueryClient
    QueryClient --> SContainer
    SContainer --> SViewer
```

The client provides functions like `getSessions`, `getSessionDetails`, and `releaseBrowserSession` which are wrapped by React Query for caching and automatic refetching [ui/src/contexts/sessions-context/sessions-context.tsx:30-56]().

For details, see [Generated API Client](#11.2).

**Sources:**
- [ui/src/contexts/sessions-context/sessions-context.tsx:6-14]()
- [ui/src/lib/query-client.ts:1-10]()
- [ui/src/contexts/sessions-context/sessions-context.tsx:58-81]()

---

## Technology Stack

The UI Dashboard leverages modern React ecosystem tools for optimal developer experience and performance.

| Category | Technology | Purpose |
|----------|------------|---------|
| **Framework** | React 18 | UI library [ui/src/main.tsx:1-12]() |
| **State Management** | TanStack Query | Server state and caching [ui/src/lib/query-client.ts:3-9]() |
| **Routing** | React Router | Client-side navigation [ui/src/containers/session-container.tsx:10]() |
| **Styling** | Tailwind CSS | Utility-first styling [ui/src/index.css]() |
| **Icons** | Radix UI Icons | UI iconography [ui/src/containers/session-container.tsx:5]() |
| **API Client** | OpenAPI TS | Generated fetch client [ui/src/contexts/sessions-context/sessions-context.tsx:14]() |

---

## Development Workflow

### Running the UI

| Command | Purpose |
|---------|---------|
| `npm run dev -w ui` | Start development server (port 5173) |
| `npm run build -w ui` | Build production bundle |
| `npm run generate-api -w ui` | Regenerate API client from schemas |

### Configuration

The UI can be configured via environment variables:

| Variable | Purpose | Usage Site |
|----------|---------|------------|
| `VITE_WS_URL` | WebSocket base URL | [ui/src/components/sessions/session-console/session-logs.tsx:9]() |
| `VITE_API_URL` | API base URL | Used by generated client configuration |

**Sources:**
- [ui/src/components/sessions/session-console/session-logs.tsx:1-9]()
- [ui/package.json:8-12]()

---

# Page: Session Management Interface

# Session Management Interface

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/ISSUE_TEMPLATE/bug_report.md](.github/ISSUE_TEMPLATE/bug_report.md)
- [ui/src/App.tsx](ui/src/App.tsx)
- [ui/src/components/header/header.tsx](ui/src/components/header/header.tsx)
- [ui/src/components/sessions/session-console/session-devtools.tsx](ui/src/components/sessions/session-console/session-devtools.tsx)
- [ui/src/components/sessions/session-console/session-logs.tsx](ui/src/components/sessions/session-console/session-logs.tsx)
- [ui/src/components/sessions/session-viewer/empty-state.tsx](ui/src/components/sessions/session-viewer/empty-state.tsx)
- [ui/src/components/sessions/session-viewer/session-viewer.tsx](ui/src/components/sessions/session-viewer/session-viewer.tsx)
- [ui/src/containers/session-container.tsx](ui/src/containers/session-container.tsx)
- [ui/src/contexts/sessions-context/sessions-context.tsx](ui/src/contexts/sessions-context/sessions-context.tsx)
- [ui/src/contexts/sessions-context/sessions-context.types.ts](ui/src/contexts/sessions-context/sessions-context.types.ts)
- [ui/src/lib/query-client.ts](ui/src/lib/query-client.ts)
- [ui/src/main.tsx](ui/src/main.tsx)
- [ui/src/root-layout.tsx](ui/src/root-layout.tsx)

</details>



## Purpose and Scope

This document describes the React-based user interface for managing browser sessions in steel-browser. The Session Management Interface provides a web-based dashboard for creating, monitoring, and managing browser automation sessions. This page covers the UI components, session contexts, real-time log streaming, and the interactive session viewer.

For information about the backend session management API endpoints, see [Session Management API](). For details on the generated API client used by this interface, see [Generated API Client](). For WebSocket streaming capabilities, see [WebSocket API]().

## Overview

The Session Management Interface is a React application that provides a visual interface for session lifecycle operations and real-time monitoring. It is built using modern web technologies to ensure a responsive and type-safe experience.

### Key Features

- **Session Viewer**: An interactive iframe-based viewer for live browser sessions with clipboard synchronization [ui/src/components/sessions/session-viewer/session-viewer.tsx:12-195]().
- **Real-time Log Streaming**: A console interface that streams browser events, network requests, and console logs via WebSockets [ui/src/components/sessions/session-console/session-logs.tsx:4-88]().
- **Session Lifecycle Management**: Context-driven hooks for fetching session details and releasing active sessions [ui/src/contexts/sessions-context/sessions-context.tsx:24-94]().
- **Embedded DevTools**: Integration with Chrome DevTools Protocol (CDP) inspector for deep debugging [ui/src/components/sessions/session-console/session-devtools.tsx:4-36]().

### Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Framework | React 18 | UI component framework [ui/src/main.tsx:6-11]() |
| State Management | TanStack React Query | Server state, caching, and polling [ui/src/lib/query-client.ts:1-10]() |
| Context API | React Context | Global session state and mutations [ui/src/contexts/sessions-context/sessions-context.tsx:20-22]() |
| Real-time | WebSockets | Live log and event streaming [ui/src/components/sessions/session-console/session-logs.tsx:9-24]() |
| Styling | Tailwind CSS | Utility-first styling [ui/src/App.tsx:1-11]() |

**Sources:** [ui/src/main.tsx:1-11](), [ui/src/lib/query-client.ts:1-10](), [ui/src/contexts/sessions-context/sessions-context.tsx:1-94]()

## Session Context and State Management

The UI manages session data through a centralized `SessionsProvider`. This provider utilizes TanStack React Query to handle data fetching, caching, and automatic refetching.

### SessionsContext Implementation

The `SessionsContext` provides hooks for components to interact with session data without manual state management.

```mermaid
graph TD
    subgraph "SessionsProvider [ui/src/contexts/sessions-context/sessions-context.tsx]"
        useSession["useSession(id)"]
        useReleaseMutation["useReleaseSessionMutation()"]
        CurrentSessionState["currentSession state"]
    end

    subgraph "API Client [ui/src/steel-client]"
        getSessions["getSessions()"]
        getSessionDetails["getSessionDetails()"]
        releaseBrowserSession["releaseBrowserSession()"]
    end

    useSession -->|"queryFn"| getSessionDetails
    useSession -->|"queryFn (if no id)"| getSessions
    useReleaseMutation -->|"mutationFn"| releaseBrowserSession
    
    useSession -.->|"refetchInterval: 1000ms"| getSessionDetails
```

- **`useSession`**: Fetches session details by ID. It implements a `refetchInterval` of 1000ms to keep the UI synchronized with the backend session status [ui/src/contexts/sessions-context/sessions-context.tsx:30-56]().
- **`useReleaseSessionMutation`**: Handles session termination. Upon success, it invalidates the `sessions` query and refetches the specific session query to update the UI state [ui/src/contexts/sessions-context/sessions-context.tsx:58-81]().

**Sources:** [ui/src/contexts/sessions-context/sessions-context.tsx:24-94](), [ui/src/contexts/sessions-context/sessions-context.types.ts:10-20]()

## Session Viewer Component

The `SessionViewer` is the primary interface for interacting with a live browser session. It embeds the browser's debug URL in an iframe and manages a complex "Clipboard Bridge".

### Clipboard Synchronization

Since the browser session runs in a remote container, the UI implements a bridge to synchronize the local user's clipboard with the remote browser.

```mermaid
sequenceDiagram
    participant User
    participant UI as "SessionViewer (React)"
    participant Iframe as "Remote Browser Iframe"
    
    User->>UI: Press Ctrl+C / Cmd+C
    UI->>UI: handleKeyDown() [line 89]
    UI->>Iframe: postMessage({ type: 'triggerCopy' }) [line 102]
    Iframe-->>UI: message({ type: 'requestClipboardWrite', text: '...' })
    UI->>UI: navigator.clipboard.writeText() [line 58]
    UI->>Iframe: postMessage({ type: 'clipboardWriteResponse' })
```

- **Keyboard Interception**: The component captures `Ctrl+C` and `Ctrl+V` events to trigger programmatic copy/paste actions within the iframe [ui/src/components/sessions/session-viewer/session-viewer.tsx:89-128]().
- **Message Handling**: It listens for `MessageEvent` from the iframe to fulfill `requestClipboardRead` and `requestClipboardWrite` requests using the browser's `navigator.clipboard` API [ui/src/components/sessions/session-viewer/session-viewer.tsx:24-86]().
- **Sandbox Security**: The iframe is configured with specific sandbox permissions (`allow-same-origin`, `allow-scripts`, `allow-clipboard-write`, `allow-clipboard-read`) to enable these features safely [ui/src/components/sessions/session-viewer/session-viewer.tsx:189-192]().

**Sources:** [ui/src/components/sessions/session-viewer/session-viewer.tsx:10-195]()

## Real-time Monitoring and Logs

The `SessionLogs` component provides a terminal-like interface for viewing session activity in real-time via WebSockets.

### Log Processing Logic

Logs are received as JSON strings over a WebSocket connection to `${env.VITE_WS_URL}/v1/sessions/logs` [ui/src/components/sessions/session-console/session-logs.tsx:9]().

| Log Type | Visual Indicator (Color) | Formatting Logic |
|----------|--------------------------|------------------|
| **Console** | `var(--cyan-a11)` | Strips timestamp/level prefixes from message [ui/src/components/sessions/session-console/session-logs.tsx:42-50]() |
| **Request** | `var(--pink-a11)` | Displays `[METHOD] URL` [ui/src/components/sessions/session-console/session-logs.tsx:51]() |
| **Response** | `var(--green-a11)` | Displays `[STATUS] URL` [ui/src/components/sessions/session-console/session-logs.tsx:52]() |
| **Error** | `var(--red-a11)` | Displays the error message [ui/src/components/sessions/session-console/session-logs.tsx:53]() |

The console automatically scrolls to the bottom as new logs arrive [ui/src/components/sessions/session-console/session-logs.tsx:28-32]().

**Sources:** [ui/src/components/sessions/session-console/session-logs.tsx:4-88]()

## Debugging and DevTools

For advanced troubleshooting, the UI integrates a `SessionDevTools` component.

- **CDP Inspector**: It embeds an iframe pointing to the backend's devtools inspector (`/v1/devtools/inspector.html`) [ui/src/components/sessions/session-console/session-devtools.tsx:29-35]().
- **Dynamic Page ID**: It subscribes to a WebSocket (`/v1/sessions/pageId`) to receive the current active page's ID, ensuring the inspector stays attached to the correct tab [ui/src/components/sessions/session-console/session-devtools.tsx:8-17]().

**Sources:** [ui/src/components/sessions/session-console/session-devtools.tsx:4-36]()

## UI Layout and Navigation

The dashboard layout is managed by `RootLayout` and `SessionContainer`.

- **`RootLayout`**: Wraps the application in `QueryClientProvider`, `SessionsProvider`, and `ThemeProvider` [ui/src/root-layout.tsx:9-25]().
- **`Header`**: Displays the current session ID (truncated) and a "Live" badge if the session status is active [ui/src/components/header/header.tsx:34-52]().
- **`SessionContainer`**: Provides a split-pane view between the `SessionViewer` and the `SessionConsole`. Users can toggle the console visibility using a side button [ui/src/containers/session-container.tsx:19-50]().
- **Empty State**: Displays a custom illustration and help links if a session has no events [ui/src/components/sessions/session-viewer/empty-state.tsx:5-36]().

**Sources:** [ui/src/root-layout.tsx:9-25](), [ui/src/containers/session-container.tsx:9-51](), [ui/src/components/header/header.tsx:7-74]()

---

# Page: Generated API Client

# Generated API Client

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [api/openapi/generate.ts](api/openapi/generate.ts)
- [api/openapi/schemas.json](api/openapi/schemas.json)
- [api/src/config.ts](api/src/config.ts)
- [api/src/modules/sessions/sessions.routes.ts](api/src/modules/sessions/sessions.routes.ts)
- [ui/src/steel-client/schemas.gen.ts](ui/src/steel-client/schemas.gen.ts)
- [ui/src/steel-client/services.gen.ts](ui/src/steel-client/services.gen.ts)
- [ui/src/steel-client/types.gen.ts](ui/src/steel-client/types.gen.ts)

</details>



This document describes the auto-generated TypeScript API client used by the Steel Browser UI to communicate with the Fastify API service. The client provides type-safe access to all API endpoints with automatic request/response validation and transformation.

## Overview

The Steel Browser UI uses a code-generated TypeScript client created by `@hey-api/openapi-ts` from the OpenAPI specification. This ensures type safety across the entire stack: Zod schemas in the API generate OpenAPI specs, which then generate TypeScript types and service functions for the UI. The generated client is located in `ui/src/steel-client/` and consists of three main artifacts:

- **types.gen.ts** - TypeScript type definitions for all request/response schemas. [ui/src/steel-client/types.gen.ts:1-10]()
- **services.gen.ts** - API service functions with automatic type inference. [ui/src/steel-client/services.gen.ts:1-98]()
- **schemas.gen.ts** - JSON schema definitions for runtime validation. [ui/src/steel-client/schemas.gen.ts:1-10]()

Sources: [ui/src/steel-client/types.gen.ts:1-10](), [ui/src/steel-client/services.gen.ts:1-98](), [ui/src/steel-client/schemas.gen.ts:1-10]()

## Generation Pipeline

The pipeline bridges the "Natural Language Space" of API definitions into the "Code Entity Space" of the UI client.

### API to Client Bridge

Title: "API Schema to UI Client Flow"
```mermaid
graph LR
    subgraph "api/src/modules"
        ZodSchemas["sessions.schema.ts<br/>Zod Schemas"]
        Routes["sessions.routes.ts<br/>Fastify Routes"]
    end
    
    subgraph "api/openapi"
        GenerateScript["generate.ts<br/>server.swagger()"]
        OpenAPIJSON["schemas.json<br/>OpenAPI 3.0.3 Spec"]
    end
    
    subgraph "ui/src/steel-client"
        HeyAPITool["@hey-api/openapi-ts<br/>Generator"]
        TypesGen["types.gen.ts<br/>TS Interfaces"]
        ServicesGen["services.gen.ts<br/>Fetch Wrappers"]
    end
    
    ZodSchemas --> Routes
    Routes -->|"server.swagger()"| GenerateScript
    GenerateScript -->|"writeFileSync"| OpenAPIJSON
    OpenAPIJSON -->|"npm run generate-api"| HeyAPITool
    HeyAPITool --> TypesGen
    HeyAPITool --> ServicesGen
```

**Generation Flow:**

1. The API service registers routes in [api/src/modules/sessions/sessions.routes.ts:23-242]() using schemas defined in `sessions.schema.ts`.
2. The [api/openapi/generate.ts:15-35]() script starts the Fastify server, calls `server.swagger()`, and adds the server URL from environment variables. [api/openapi/generate.ts:19-26]()
3. The resulting JSON is written to [api/openapi/schemas.json]().
4. The UI runs the `@hey-api/openapi-ts` generator to produce the type-safe client.

Sources: [api/src/modules/sessions/sessions.routes.ts:23-242](), [api/openapi/generate.ts:1-36](), [api/openapi/schemas.json:1-10]()

## Generated Type Definitions

### Core Request/Response Types

The [ui/src/steel-client/types.gen.ts]() file contains TypeScript interfaces for all API operations.

| Type Category | Examples | Purpose |
|---------------|----------|---------|
| Request Bodies | `CreateSession`, `ScrapeRequest` | Input parameters for API calls |
| Response Bodies | `ScrapeResponse`, `SessionDetails` | Returned data structures |
| Options | `LaunchBrowserSessionData` | Wrappers containing body, path, and query params |

**Example: CreateSession Type**
The `CreateSession` type in [ui/src/steel-client/types.gen.ts:74-280]() includes detailed configurations for proxies, user agents, and browser contexts including cookies and storage.

Sources: [ui/src/steel-client/types.gen.ts:3-47](), [ui/src/steel-client/types.gen.ts:74-280]()

## Generated Service Functions

### Client Initialization

The [ui/src/steel-client/services.gen.ts:97]() file initializes the fetch-based client:

```typescript
export const client = createClient(createConfig());
```

### Service Function Pattern

Service functions wrap the HTTP calls with full type awareness for the `data` and `error` payloads.

Title: "Code Entity Interaction: UI to API"
```mermaid
graph TB
    UIComp["UI Component"]
    
    subgraph "ui/src/steel-client/services.gen.ts"
        LaunchFn["launchBrowserSession()"]
        GetSessionsFn["getSessions()"]
        ReleaseFn["releaseBrowserSession()"]
    end
    
    subgraph "api/src/modules/sessions"
        SessController["sessions.controller.ts"]
        SessRoutes["sessions.routes.ts"]
    end

    UIComp --> LaunchFn
    LaunchFn -->|"POST /v1/sessions"| SessRoutes
    SessRoutes --> SessController
```

**Example Service Function: `launchBrowserSession`**
From [ui/src/steel-client/services.gen.ts:168-180]():
```typescript
export const launchBrowserSession = <ThrowOnError extends boolean = false>(
  options?: Options<LaunchBrowserSessionData, ThrowOnError>,
) => {
  return (options?.client ?? client).post<
    LaunchBrowserSessionResponse,
    LaunchBrowserSessionError,
    ThrowOnError
  >({
    ...options,
    url: "/v1/sessions",
    responseTransformer: LaunchBrowserSessionResponseTransformer,
  });
};
```

### Key Service Functions

| Service Function | Method | Endpoint | Source |
|-----------------|--------|----------|--------|
| `scrape` | POST | `/v1/scrape` | [ui/src/steel-client/services.gen.ts:103-115]() |
| `health` | GET | `/v1/health` | [ui/src/steel-client/services.gen.ts:151-162]() |
| `launchBrowserSession` | POST | `/v1/sessions` | [ui/src/steel-client/services.gen.ts:168-180]() |
| `getSessions` | GET | `/v1/sessions` | [ui/src/steel-client/services.gen.ts:186-197]() |
| `getSessionDetails` | GET | `/v1/sessions/{sessionId}` | [ui/src/steel-client/services.gen.ts:203-215]() |
| `releaseBrowserSession`| POST | `/v1/sessions/{sessionId}/release` | [ui/src/steel-client/services.gen.ts:238-250]() |

Sources: [ui/src/steel-client/services.gen.ts:103-250]()

## Generated JSON Schemas

The [ui/src/steel-client/schemas.gen.ts]() file contains the raw OpenAPI schema objects as `const` objects. These are used by the generated client for metadata and can be utilized for runtime validation in the UI.

**Example: ScrapeRequestSchema**
From [ui/src/steel-client/schemas.gen.ts:3-37]():
```typescript
export const ScrapeRequestSchema = {
  title: "ScrapeRequest",
  type: "object",
  properties: {
    url: { type: "string" },
    format: {
      type: "array",
      items: {
        type: "string",
        enum: ["html", "readability", "cleaned_html", "markdown"],
      },
    },
    // ...
  },
  additionalProperties: false,
} as const;
```

Sources: [ui/src/steel-client/schemas.gen.ts:3-37](), [ui/src/steel-client/schemas.gen.ts:194-210]()

## Type Safety Guarantees

The integration of the generated client ensures that:
1. **URL Parameters**: Path parameters like `{sessionId}` are strictly typed and required in the `options.path` object. [ui/src/steel-client/services.gen.ts:212]()
2. **Request Bodies**: The `body` property of the options object must match the Zod-defined schema from the API. [ui/src/steel-client/services.gen.ts:171]()
3. **Response Handling**: The `data` returned from service calls is automatically typed, reducing the need for manual type assertions in React components. [ui/src/steel-client/services.gen.ts:106-110]()

Sources: [ui/src/steel-client/services.gen.ts:103-215](), [api/src/modules/sessions/sessions.routes.ts:41-57]()

---

# Page: API Reference

# API Reference

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [api/.env.example](api/.env.example)
- [api/openapi/generate.ts](api/openapi/generate.ts)
- [api/openapi/schemas.json](api/openapi/schemas.json)
- [api/src/config.ts](api/src/config.ts)
- [api/src/env.ts](api/src/env.ts)
- [api/src/plugins/schemas.ts](api/src/plugins/schemas.ts)
- [api/src/routes.ts](api/src/routes.ts)
- [ui/src/steel-client/schemas.gen.ts](ui/src/steel-client/schemas.gen.ts)

</details>



This page provides a complete reference for the steel-browser REST API, including all HTTP endpoints, WebSocket connections, request/response schemas, and the type system. For information about specific session configuration options, see [Session Configuration](#4.2). For details on using quick actions, see [Quick Actions API](#5). For WebSocket streaming capabilities, see [WebSocket API](#10.1).

For detailed technical specifications, refer to the following child pages:
- [OpenAPI Schema](#12.1) — Document the OpenAPI specification generation and schema structure
- [Type System](#12.2) — Explain Zod schemas, TypeScript types, and validation

## API Overview

The steel-browser API is a RESTful HTTP service organized under the `/v1` base path. All endpoints enforce schema validation using Zod schemas that are automatically transformed into OpenAPI specifications. The API is exposed through a Fastify server and includes both stateless quick actions and stateful session management endpoints.

**Base URL Structure**
```
http://{HOST}:{PORT}/v1/*
```

**API Categories**
- **Health**: Service health checks
- **Sessions**: Browser session lifecycle management
- **Quick Actions**: Single-request operations (scrape, screenshot, PDF)
- **Session Actions**: Operations within existing sessions
- **File Operations**: File upload/download per session
- **Logs & Monitoring**: Browser event query and streaming
- **CDP Integration**: Chrome DevTools Protocol access
- **Selenium**: WebDriver compatibility endpoints

Sources: [api/src/modules/sessions/sessions.routes.ts](), [api/openapi/schemas.json](), [api/src/plugins/schemas.ts]()

## Schema Registration Architecture

The following diagram shows how schemas flow from Zod definitions through the Fastify server to OpenAPI generation and client code generation:

```mermaid
graph TB
    subgraph "Schema Definition Layer"
        ActionSchemas["actionSchemas<br/>(actions.schema.js)"]
        BrowserSchemas["browserSchemas<br/>(sessions.schema.js)"]
        LogsSchemas["logsSchemas<br/>(logs.schema.js)"]
        CDPSchemas["cdpSchemas<br/>(cdp.schemas.js)"]
        SeleniumSchemas["seleniumSchemas<br/>(selenium.schema.js)"]
        FilesSchemas["filesSchemas<br/>(files.schema.js)"]
    end
    
    subgraph "Schema Aggregation"
        SCHEMAS["SCHEMAS object<br/>(plugins/schemas.ts)"]
        buildJsonSchemas["buildJsonSchemas()<br/>Converts to JSON Schema"]
        schemas["schemas array"]
        dollarRef["$ref() helper<br/>Reference schemas by ID"]
    end
    
    subgraph "Fastify Server"
        fastify["fastify.addSchema()<br/>Register each schema"]
        fastifySwagger["@fastify/swagger<br/>OpenAPI generation"]
        fastifyScalar["@scalar/fastify-api-reference<br/>/documentation route"]
    end
    
    subgraph "Generated Artifacts"
        openApiJSON["openapi/schemas.json<br/>OpenAPI 3.0.3 spec"]
        UITypes["ui/src/steel-client/types.gen.ts<br/>TypeScript types"]
        UIServices["ui/src/steel-client/services.gen.ts<br/>API client functions"]
        UISchemas["ui/src/steel-client/schemas.gen.ts<br/>Client-side schemas"]
    end
    
    ActionSchemas --> SCHEMAS
    BrowserSchemas --> SCHEMAS
    LogsSchemas --> SCHEMAS
    CDPSchemas --> SCHEMAS
    SeleniumSchemas --> SCHEMAS
    FilesSchemas --> SCHEMAS
    
    SCHEMAS --> buildJsonSchemas
    buildJsonSchemas --> schemas
    buildJsonSchemas --> dollarRef
    
    schemas --> fastify
    fastify --> fastifySwagger
    fastifySwagger --> fastifyScalar
    fastifySwagger --> openApiJSON
    
    openApiJSON --> UITypes
    openApiJSON --> UIServices
    openApiJSON --> UISchemas
```

Sources: [api/src/plugins/schemas.ts:16-25](), [api/src/plugins/schemas.ts:27-66](), [api/openapi/generate.ts]()

## HTTP Endpoint Reference

### Health Endpoints

| Method | Path | Operation ID | Description | Request | Response |
|--------|------|--------------|-------------|---------|----------|
| GET | `/v1/health` | `health` | Check server and browser status | - | `{ status: "ok" }` or 503 |

Sources: [api/src/modules/sessions/sessions.routes.ts:24-40]()

### Session Management Endpoints

| Method | Path | Operation ID | Description | Request Schema | Response Schema |
|--------|------|--------------|-------------|----------------|-----------------|
| POST | `/v1/sessions` | `launch_browser_session` | Launch a new browser session | `CreateSession` | `SessionDetails` |
| GET | `/v1/sessions` | `get_sessions` | List all active sessions | - | `MultipleSessions` |
| GET | `/v1/sessions/:sessionId` | `get_session_details` | Get details for a specific session | - | `SessionDetails` |
| GET | `/v1/sessions/:sessionId/context` | `get_browser_context` | Retrieve session context (cookies, storage) | - | `SessionContextSchema` |
| POST | `/v1/sessions/:sessionId/release` | `release_browser_session` | Release a specific session | - | `ReleaseSession` |
| POST | `/v1/sessions/release` | `release_browser_sessions` | Release all sessions | - | `ReleaseSession` |
| GET | `/v1/sessions/:id/live-details` | `get_session_live_details` | Get live session state with pages | - | `SessionLiveDetailsResponse` |
| GET | `/v1/sessions/debug` | `get_session_debugger_stream` | HTML debugger view of session | `SessionStreamQuery` | HTML content |
| POST | `/v1/events` | `receive_events` | Receive browser recording events | `RecordedEvents` | `{ status: "ok" }` |

Sources: [api/src/modules/sessions/sessions.routes.ts:41-201](), [api/openapi/schemas.json:207-848]()

### Quick Action Endpoints

These endpoints perform single-request operations that launch a browser, execute the action, and clean up automatically:

| Method | Path | Operation ID | Description | Request Schema | Response Schema |
|--------|------|--------------|-------------|----------------|-----------------|
| POST | `/v1/scrape` | `scrape` | Scrape content from URL | `ScrapeRequest` | `ScrapeResponse` |
| POST | `/v1/screenshot` | `screenshot` | Capture screenshot of URL | `ScreenshotRequest` | `ScreenshotResponse` |
| POST | `/v1/pdf` | `pdf` | Generate PDF of URL | `PDFRequest` | `PDFResponse` |

Sources: [api/openapi/schemas.json:11-206]()

### Session Action Endpoints

These endpoints perform actions within an existing session context:

| Method | Path | Operation ID | Description | Request Schema | Response Schema |
|--------|------|--------------|-------------|----------------|-----------------|
| POST | `/v1/sessions/scrape` | `scrape_session` | Scrape current session page | `ScrapeRequest` | `ScrapeResponse` |
| POST | `/v1/sessions/screenshot` | `screenshot_session` | Screenshot current session page | `ScreenshotRequest` | `ScreenshotResponse` |
| POST | `/v1/sessions/pdf` | `pdf_session` | Generate PDF of current session page | `PDFRequest` | `PDFResponse` |

Sources: [api/src/modules/sessions/sessions.routes.ts:203-255]()

### File Operation Endpoints

| Method | Path | Operation ID | Description | Request | Response Schema |
|--------|------|--------------|-------------|---------|-----------------|
| POST | `/v1/sessions/:sessionId/files` | `upload_file` | Upload file via multipart/form-data | `FileUploadRequest` | `FileDetails` |
| GET | `/v1/sessions/:sessionId/files` | `list_files` | List all session files | - | `MultipleFiles` |
| GET | `/v1/sessions/:sessionId/files/*` | `download_file` | Download specific file | - | Binary data |
| DELETE | `/v1/sessions/:sessionId/files/*` | `delete_file` | Delete specific file | - | `void` |
| DELETE | `/v1/sessions/:sessionId/files` | `delete_all_files` | Delete all session files | - | `void` |
| GET | `/v1/sessions/:sessionId/files.zip` | `download_archive` | Download all files as ZIP | - | Binary ZIP data |

Sources: [api/openapi/schemas.json]()

### Logs & Monitoring Endpoints

| Method | Path | Operation ID | Description | Query Parameters | Response |
|--------|------|--------------|-------------|------------------|----------|
| GET | `/v1/logs/query` | `get_v1_logs_query` | Query stored browser logs | `LogQuerySchema` | Log events array |
| GET | `/v1/logs/stats` | `get_v1_logs_stats` | Get log statistics | - | `LogStatsSchema` |
| GET | `/v1/logs/stream` | `get_v1_logs_stream` | Stream logs via SSE | - | Server-Sent Events |
| POST | `/v1/logs/export` | `post_v1_logs_export` | Export logs to Parquet | `ExportLogsSchema` | Parquet file |
| DELETE | `/v1/logs/` | `delete_v1_logs` | Clear all logs | - | Success response |

Sources: [api/openapi/schemas.json]()

### CDP Integration Endpoints

| Method | Path | Operation ID | Description |
|--------|------|--------------|-------------|
| GET | `/v1/devtools/inspector.html` | `get_devtools_url` | Get Chrome DevTools inspector URL |

Sources: [ui/src/steel-client/services.gen.ts:373-388]()

## Schema Type System

The following diagram illustrates how Zod schemas are transformed into TypeScript types and used for validation:

```mermaid
graph LR
    subgraph "Schema Definition (Zod)"
        ZodSchema["z.object({<br/>  sessionId: z.string().uuid(),<br/>  proxyUrl: z.string().optional(),<br/>  ...<br/>})"]
    end
    
    subgraph "Schema Registration"
        SchemaID["Schema $id<br/>'CreateSession'"]
        JSONSchema["JSON Schema<br/>(OpenAPI compatible)"]
    end
    
    subgraph "Runtime Validation"
        FastifyRoute["Fastify Route Handler"]
        SchemaValidation["Request validation<br/>(automatic)"]
        TypedRequest["Typed Request object<br/>CreateSessionRequest"]
    end
    
    subgraph "Type Generation"
        OpenAPISpec["OpenAPI 3.0.3 Spec<br/>schemas.json"]
        TSTypes["TypeScript Types<br/>CreateSession interface"]
        ClientFunctions["Client Functions<br/>launchBrowserSession()"]
    end
    
    ZodSchema --> SchemaID
    ZodSchema --> JSONSchema
    SchemaID --> FastifyRoute
    JSONSchema --> SchemaValidation
    SchemaValidation --> TypedRequest
    
    JSONSchema --> OpenAPISpec
    OpenAPISpec --> TSTypes
    OpenAPISpec --> ClientFunctions
```

Sources: [api/src/plugins/schemas.ts](), [api/src/utils/schema.js](), [ui/src/steel-client/types.gen.ts]()

## Core Request/Response Schemas

For a deep dive into the Zod-based validation and full TypeScript type definitions, see [Type System](#12.2).

### CreateSession Schema

The `CreateSession` schema defines all options for launching a new browser session.

**Key Properties:**

| Property | Type | Description |
|----------|------|-------------|
| `sessionId` | `string (uuid)` | Optional unique identifier for the session |
| `proxyUrl` | `string` | Proxy URL for the session |
| `userAgent` | `string` | Custom user agent string |
| `sessionContext` | `SessionContextSchema` | Cookies, localStorage, sessionStorage, indexedDB to initialize |
| `isSelenium` | `boolean` | Enable Selenium WebDriver compatibility mode |
| `blockAds` | `boolean` | Block advertisements |
| `headless` | `boolean` | Run browser in headless mode |

Sources: [api/openapi/schemas.json:207-602](), [ui/src/steel-client/types.gen.ts:74-292]()

### ScrapeRequest Schema

Request schema for web scraping operations.

| Property | Type | Description |
|----------|------|-------------|
| `url` | `string` | URL to scrape |
| `format` | `Array<"html" \| "readability" \| "cleaned_html" \| "markdown">` | Output format(s) |
| `screenshot` | `boolean` | Include screenshot |
| `pdf` | `boolean` | Include PDF |

Sources: [api/openapi/schemas.json:11-49](), [ui/src/steel-client/types.gen.ts:3-14]()

## Environment Configuration Schema

The environment configuration is validated using Zod schemas in `env.ts`.

**Server Configuration:**

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `NODE_ENV` | `"test" \| "development" \| "staging" \| "production" \| "preview"` | `"development"` | Runtime environment |
| `PORT` | `string` | `"3000"` | Server port |
| `USE_SSL` | `boolean` | `false` | Enable HTTPS/WSS |

**Browser Configuration:**

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `CHROME_EXECUTABLE_PATH` | `string` | - | Path to Chrome binary |
| `CHROME_HEADLESS` | `boolean` | `true` | Run Chrome in headless mode |
| `CDP_REDIRECT_PORT` | `string` | `"9222"` | Chrome DevTools Protocol port |

Sources: [api/src/env.ts:6-82](), [api/.env.example:1-31]()

## OpenAPI Specification Generation

The system automatically generates an OpenAPI 3.0.3 specification from registered schemas. For more details on the generation logic and schema structure, see [OpenAPI Schema](#12.1).

**Generation Process:**
1. **Schema Definition**: Zod schemas defined in module schema files.
2. **Schema Aggregation**: Combined in `SCHEMAS` object in `plugins/schemas.ts`.
3. **JSON Schema Conversion**: `buildJsonSchemas()` converts Zod to JSON Schema.
4. **Fastify Registration**: Each schema registered with `fastify.addSchema()`.
5. **File Export**: `openapi/generate.ts` writes `schemas.json`.

Sources: [api/openapi/generate.ts:15-35](), [api/src/plugins/schemas.ts:32-64](), [api/openapi/schemas.json:1-10]()

## Type-Safe Client Generation

The system generates a fully type-safe TypeScript client from the OpenAPI specification using `@hey-api/openapi-ts`.

| File | Purpose |
|------|---------|
| `ui/src/steel-client/types.gen.ts` | TypeScript interfaces for all schemas |
| `ui/src/steel-client/services.gen.ts` | Type-safe API client functions |
| `ui/src/steel-client/schemas.gen.ts` | Client-side Zod schemas |

Sources: [ui/src/steel-client/services.gen.ts:1-96](), [ui/src/steel-client/types.gen.ts:1-1246](), [ui/src/steel-client/schemas.gen.ts:1-37]()

---

# Page: OpenAPI Schema

# OpenAPI Schema

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [api/.env.example](api/.env.example)
- [api/openapi/generate.ts](api/openapi/generate.ts)
- [api/openapi/schemas.json](api/openapi/schemas.json)
- [api/src/config.ts](api/src/config.ts)
- [api/src/env.ts](api/src/env.ts)
- [api/src/plugins/schemas.ts](api/src/plugins/schemas.ts)
- [api/src/routes.ts](api/src/routes.ts)
- [ui/src/steel-client/schemas.gen.ts](ui/src/steel-client/schemas.gen.ts)

</details>



This document explains the OpenAPI specification system used in steel-browser. It covers how schemas are defined, registered, validated, and used to automatically generate API documentation and type-safe client code.

For information about specific API endpoints and their usage, see [Session Management API](#4.1) and [Quick Actions API](#5). For details on the underlying type system using Zod, see [Type System](#12.2).

---

## Purpose and Architecture

The OpenAPI schema system in steel-browser provides:

1. **Type-safe request/response validation** using Zod schemas converted to JSON Schema.
2. **Auto-generated API documentation** served at `/documentation` via Scalar UI.
3. **Type-safe client code generation** for the React UI workspace.
4. **Contract-first API design** ensuring consistency between server and clients.

The schema system follows a modular architecture where each feature module (sessions, actions, files, logs, CDP, Selenium) defines its own schemas, which are then aggregated and registered with Fastify.

### System Data Flow

The following diagram bridges the natural language concepts of "API Definitions" to the actual code entities that implement them.

**Schema to Client Flow**
```mermaid
graph TB
    subgraph "Natural Language: Schema Definition"
        ActionSchemas["actions.schema.ts<br/>ScrapeRequest, ScreenshotRequest"]
        SessionSchemas["sessions.schema.ts<br/>CreateSession, SessionDetails"]
        FileSchemas["files.schema.ts<br/>FileUploadRequest, FileDetails"]
        LogSchemas["logs.schema.ts<br/>LogQuerySchema, LogStatsSchema"]
        CDPSchemas["cdp.schemas.ts<br/>CDP-specific schemas"]
        SeleniumSchemas["selenium.schema.ts<br/>Selenium-specific schemas"]
    end
    
    subgraph "Code Entity: Schema Registration"
        SchemaPlugin["schemaPlugin (api/src/plugins/schemas.ts)"]
        BuildJsonSchemas["buildJsonSchemas() (api/src/utils/schema.ts)"]
        FastifySwagger["fastifySwagger (@fastify/swagger)"]
    end
    
    subgraph "Code Entity: Runtime Validation"
        Routes["sessionsRoutes, actionsRoutes, etc.<br/>(api/src/routes.ts)"]
        RefFunction["$ref() function"]
        FastifyValidation["Fastify Validation Engine"]
    end
    
    subgraph "Code Entity: Code Generation"
        GenerateScript["api/openapi/generate.ts"]
        SchemasJSON["api/openapi/schemas.json"]
        HeyAPI["@hey-api/openapi-ts"]
        GeneratedClient["ui/src/steel-client/<br/>services.gen.ts<br/>types.gen.ts<br/>schemas.gen.ts"]
    end
    
    subgraph "Natural Language: Documentation"
        ScalarUI["fastifyScalar (@scalar/fastify-api-reference)<br/>/documentation endpoint"]
    end
    
    ActionSchemas --> SchemaPlugin
    SessionSchemas --> SchemaPlugin
    FileSchemas --> SchemaPlugin
    LogSchemas --> SchemaPlugin
    CDPSchemas --> SchemaPlugin
    SeleniumSchemas --> SchemaPlugin
    
    SchemaPlugin --> BuildJsonSchemas
    BuildJsonSchemas --> FastifySwagger
    FastifySwagger --> Routes
    FastifySwagger --> ScalarUI
    
    Routes --> RefFunction
    RefFunction --> FastifyValidation
    
    FastifySwagger --> GenerateScript
    GenerateScript --> SchemasJSON
    SchemasJSON --> HeyAPI
    HeyAPI --> GeneratedClient
```

**Sources:** [api/src/plugins/schemas.ts:1-67](), [api/openapi/generate.ts:1-36](), [api/src/routes.ts:1-7]()

---

## Schema Plugin Registration

The schema plugin is the central orchestrator for the OpenAPI system. It aggregates all feature-specific schemas, registers them with Fastify, and configures the OpenAPI documentation.

### Schema Aggregation

All schemas from feature modules are collected into a single `SCHEMAS` object:
[api/src/plugins/schemas.ts:16-23]()

The `buildJsonSchemas()` utility converts these Zod schemas to JSON Schema format and provides the `$ref()` function for referencing schemas in routes:
[api/src/plugins/schemas.ts:25]()

### Fastify Registration

The `schemaPlugin` registers each schema with Fastify and configures the OpenAPI specification:

**Fastify Schema Integration**
```mermaid
graph LR
    SCHEMAS["SCHEMAS object"]
    BuildJsonSchemas["buildJsonSchemas(SCHEMAS)"]
    SchemasArray["schemas array (JSON Schema)"]
    RefFunction["$ref() function"]
    AddSchema["fastify.addSchema()"]
    SwaggerPlugin["fastifySwagger"]
    
    SCHEMAS --> BuildJsonSchemas
    BuildJsonSchemas --> SchemasArray
    BuildJsonSchemas --> RefFunction
    SchemasArray --> AddSchema
    AddSchema --> SwaggerPlugin
    RefFunction -.->|"Used in routes.ts"| SwaggerPlugin
```

**Sources:** [api/src/plugins/schemas.ts:27-55]()

### OpenAPI Configuration

The OpenAPI specification is configured with metadata and server information. The `refResolver` is customized to use the schema's `$id` in title case for clean documentation labels.

| Configuration | Value | Purpose |
|--------------|-------|---------|
| `openapi` | `3.0.3` | OpenAPI specification version [api/openapi/schemas.json:2]() |
| `info.title` | "Steel Browser Instance API" | API title [api/src/plugins/schemas.ts:35]() |
| `info.version` | `0.0.1` | API version [api/src/plugins/schemas.ts:37]() |
| `servers[0].url` | From `getBaseUrl()` | Server URL [api/src/plugins/schemas.ts:41]() |
| `refResolver.buildLocalReference` | `titleCase(json.$id)` | Schema reference naming [api/src/plugins/schemas.ts:51-53]() |

**Sources:** [api/src/plugins/schemas.ts:32-55](), [api/openapi/schemas.json:1-7]()

---

## Schema Definition Structure

Each feature module defines its schemas using Zod for type-safe validation. The schemas follow consistent patterns for requests, responses, and shared types.

### Schema Organization by Module

The system categorizes schemas into functional groups:

| Module | Primary Schemas | File Source |
|--------|-----------------|-------------|
| **Actions** | `ScrapeRequest`, `ScrapeResponse`, `ScreenshotRequest`, `PDFRequest` | [api/openapi/schemas.json:11-206]() |
| **Sessions** | `CreateSession`, `SessionDetails`, `SessionContextSchema` | [api/openapi/schemas.json:207-350]() |
| **Files** | `FileUploadRequest`, `FileDetails`, `MultipleFiles` | [api/src/plugins/schemas.ts:22]() |
| **Logs** | `LogQuerySchema`, `LogStatsSchema` | [api/src/plugins/schemas.ts:19]() |

**Sources:** [api/src/plugins/schemas.ts:16-23](), [api/openapi/schemas.json:11-207]()

### Common Schema Patterns

#### Request Schema Pattern
Request schemas define optional and required fields with strict validation. For example, the `ScrapeRequest` defines supported formats and proxy options.
[api/openapi/schemas.json:11-49]()

#### Response Schema Pattern
Response schemas define the structure of successful responses, such as `ScrapeResponse` which includes `content`, `metadata`, and `links`.
[api/openapi/schemas.json:50-155]()

---

## OpenAPI Document Generation

The OpenAPI specification is generated at build time and exported as JSON. This document serves as the contract for client code generation.

### Generation Process

The `api/openapi/generate.ts` script initializes the Fastify server, waits for it to be ready, and then writes the swagger output to a file.

**Generation Sequence**
```mermaid
sequenceDiagram
    participant Script as generate.ts
    participant Server as server (api/src/index.ts)
    participant Swagger as server.swagger()
    participant File as openapi/schemas.json
    
    Script->>Server: Import and initialize
    Server->>Server: Register schemaPlugin
    Script->>Server: server.ready()
    Server->>Swagger: Generate OpenAPI spec
    Swagger-->>Script: Return OpenAPIDocument
    Script->>Script: Add server URL from env.HOST/PORT
    Script->>File: writeFileSync()
    Script->>Server: server.close()
```

**Sources:** [api/openapi/generate.ts:1-36]()

### Server URL Injection
The generation script specifically injects the server URL derived from the environment variables `HOST` and `PORT`.
[api/openapi/generate.ts:19-26]()

---

## Client Code Generation

The OpenAPI specification is used to generate type-safe client code for the React UI. This ensures perfect synchronization between the API and frontend.

### Generated Service Functions
Each API endpoint becomes a typed function in `ui/src/steel-client/services.gen.ts`. For example, scraping operations are mapped to service calls.
[ui/src/steel-client/services.gen.ts:164-180]()

### Generated TypeScript Types
Request and response types are generated from schemas. The `ScrapeRequest` type in the client workspace perfectly matches the server-side Zod definition.
[ui/src/steel-client/types.gen.ts:74-110]()

### Generated Schema Objects
Schema objects are also exported to the client for runtime validation or form handling.
[ui/src/steel-client/schemas.gen.ts:3-37]()

**Sources:** [ui/src/steel-client/services.gen.ts:1-577](), [ui/src/steel-client/types.gen.ts:1-1246](), [ui/src/steel-client/schemas.gen.ts:1-193]()

---

## API Documentation UI

The Scalar UI provides interactive API documentation at `/documentation`, generated from the OpenAPI specification.

### Scalar Configuration
The Scalar plugin is registered with custom theming provided by `scalarTheme`.
[api/src/plugins/schemas.ts:57-64]()

### Accessing Documentation
- **Route:** `/documentation` [api/src/plugins/schemas.ts:59]()
- **Base URL:** Dynamically determined by `getBaseUrl()` [api/src/plugins/schemas.ts:41]()

**Sources:** [api/src/plugins/schemas.ts:57-64](), [api/src/utils/url.ts]()

---

## Environment Integration

The schema system integrates with environment configuration for server URLs and validation settings.

### Environment Variables
The `envSchema` defines the configuration parameters that influence the API behavior and schema generation.
[api/src/env.ts:6-84]()

| Variable | Default | Purpose |
|----------|---------|---------|
| `HOST` | `0.0.0.0` | Server hostname [api/src/env.ts:10]() |
| `PORT` | `3000` | Server port [api/src/env.ts:12]() |
| `DOMAIN` | - | Optional domain override [api/src/env.ts:11]() |
| `USE_SSL` | `false` | Protocol selection (HTTP vs HTTPS) [api/src/env.ts:13-17]() |

**Sources:** [api/src/env.ts:6-84](), [api/.env.example:1-31]()

---

# Page: Type System

# Type System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [api/.env.example](api/.env.example)
- [api/src/env.ts](api/src/env.ts)
- [api/src/modules/sessions/sessions.controller.ts](api/src/modules/sessions/sessions.controller.ts)
- [api/src/modules/sessions/sessions.schema.ts](api/src/modules/sessions/sessions.schema.ts)
- [api/src/plugins/schemas.ts](api/src/plugins/schemas.ts)
- [api/src/routes.ts](api/src/routes.ts)
- [api/src/services/cdp/utils/validation.ts](api/src/services/cdp/utils/validation.ts)
- [api/src/types/browser.ts](api/src/types/browser.ts)
- [repl/package.json](repl/package.json)
- [ui/package.json](ui/package.json)

</details>



## Purpose

This document explains the type system architecture in `steel-browser`, which provides end-to-end type safety from API request validation to client-side type checking. The system uses Zod schemas as the single source of truth, automatically generates OpenAPI specifications, and produces type-safe TypeScript clients for the UI workspace.

For information about environment configuration validation, see [Environment Configuration](#2.2). For API endpoint documentation, see [OpenAPI Schema](#12.1).

---

## Architecture Overview

The `steel-browser` type system follows a unidirectional flow where Zod schemas serve as the canonical definition, which are then transformed into OpenAPI specifications and finally into TypeScript types for the client.

**Type System Flow Diagram**

```mermaid
graph LR
    ZodSchemas["Zod Schemas<br/>(api/src/modules/*.schema.ts)"]
    FastifyPlugin["@fastify/swagger<br/>Plugin"]
    OpenAPISpec["OpenAPI JSON<br/>(api/openapi/schemas.json)"]
    ClientGenerator["@hey-api/openapi-ts<br/>Generator"]
    TSTypes["TypeScript Types<br/>(ui/src/steel-client/types.gen.ts)"]
    TSClient["TypeScript Client<br/>(ui/src/steel-client/services.gen.ts)"]
    RuntimeValidation["Runtime Validation<br/>($ref schema references)"]
    
    ZodSchemas -->|"registered with"| FastifyPlugin
    FastifyPlugin -->|"generates"| OpenAPISpec
    OpenAPISpec -->|"consumed by"| ClientGenerator
    ClientGenerator -->|"generates"| TSTypes
    ClientGenerator -->|"generates"| TSClient
    ZodSchemas -->|"validates"| RuntimeValidation
```

**Sources:** [api/src/plugins/schemas.ts:1-25](), [ui/package.json:53-54]()

---

## Schema Definition with Zod

Zod schemas define request and response structures in the API workspace. Each module defines its schemas using Zod, which are then registered with Fastify's schema plugin using the `buildJsonSchemas` helper.

**Schema Registration Pattern**

```mermaid
graph TB
    SchemaFile["sessions.schema.ts<br/>Define Zod schemas"]
    BuildSchemas["buildJsonSchemas()<br/>Convert to JSON Schema"]
    RegisterPlugin["server.register(schemaPlugin)<br/>Register with Fastify"]
    RouteSchema["Route schema: $ref"]
    
    SchemaFile -->|"exports SCHEMAS"| BuildSchemas
    BuildSchemas -->|"returns { schemas, $ref }"| RegisterPlugin
    RegisterPlugin -->|"fastify.addSchema()"| RouteSchema
```

**Sources:** [api/src/modules/sessions/sessions.schema.ts:10-182](), [api/src/plugins/schemas.ts:16-30]()

### Schema Reference System

Routes reference schemas using the `$ref` helper function, which creates JSON Schema `$ref` pointers to registered schemas. This enables schema reuse and automatic validation.

**Example Route Schema Definition**

The session creation endpoint demonstrates the pattern in `sessions.routes.ts`:

```typescript
// Conceptual example based on registration pattern
server.post("/sessions", {
  schema: {
    body: $ref("CreateSession"),    // Request validation
    response: {
      200: $ref("SessionDetails"),  // Response validation
    },
  },
})
```

**Sources:** [api/src/plugins/schemas.ts:25-30](), [api/src/modules/sessions/sessions.schema.ts:28-127]()

---

## OpenAPI Schema Generation

The system generates OpenAPI 3.0.3 specifications from the registered Zod schemas. This happens during the build process and creates a machine-readable API contract.

**OpenAPI Generation Process**

```mermaid
graph LR
    Server["Fastify Server<br/>with registered schemas"]
    SwaggerMethod["fastifySwagger<br/>Extract OpenAPI spec"]
    BaseUrl["getBaseUrl()<br/>Configured from ENV"]
    OutputFile["schemas.json<br/>OpenAPI 3.0.3 spec"]
    
    Server -->|"register plugin"| SwaggerMethod
    BaseUrl -->|"add server URL"| SwaggerMethod
    SwaggerMethod -->|"export to"| OutputFile
```

**Sources:** [api/src/plugins/schemas.ts:32-55](), [api/src/utils/url.ts]()

### Key Schema Types

| Schema Name | Purpose | Key Fields |
|------------|---------|----------------|
| `CreateSession` | Session creation request | `sessionId`, `proxyUrl`, `userAgent`, `sessionContext`, `dimensions` |
| `SessionDetails` | Session information response | `id`, `createdAt`, `status`, `duration`, `websocketUrl`, `debugUrl` |
| `SessionContextSchema` | Browser state persistence | `cookies`, `localStorage` |
| `deviceConfigSchema` | Viewport/UA configuration | `device` (desktop/mobile) |

**Sources:** [api/src/modules/sessions/sessions.schema.ts:10-127]()

---

## Type-Safe Client Generation

The UI workspace uses `@hey-api/openapi-ts` to generate a fully type-safe client from the OpenAPI specification. This ensures compile-time type safety when making API calls from the React frontend.

**Client Generation Flow**

```mermaid
graph TB
    OpenAPIJSON["api/openapi/schemas.json"]
    Generator["@hey-api/openapi-ts"]
    TypesFile["types.gen.ts<br/>TypeScript interfaces"]
    ServicesFile["services.gen.ts<br/>API client functions"]
    UICode["React Components<br/>Type-safe API calls"]
    
    OpenAPIJSON -->|"input"| Generator
    Generator -->|"generates"| TypesFile
    Generator -->|"generates"| ServicesFile
    TypesFile -->|"imports"| UICode
    ServicesFile -->|"imports"| UICode
```

**Sources:** [ui/package.json:12](), [ui/package.json:54]()

---

## Runtime Validation

Fastify performs runtime validation of incoming requests against the registered Zod-derived schemas. This catches type mismatches before they reach application code.

**Validation Flow**

```mermaid
graph TB
    IncomingRequest["HTTP Request"]
    SchemaValidation["Fastify Schema Validation<br/>Against Zod-derived schema"]
    ValidationError["400 Bad Request<br/>Validation error details"]
    RouteHandler["handleLaunchBrowserSession<br/>Type-safe request object"]
    SessionService["SessionService.startSession()<br/>Business logic"]
    
    IncomingRequest --> SchemaValidation
    SchemaValidation -->|"invalid"| ValidationError
    SchemaValidation -->|"valid"| RouteHandler
    RouteHandler --> SessionService
```

**Sources:** [api/src/modules/sessions/sessions.controller.ts:8-65](), [api/src/modules/sessions/sessions.schema.ts:28-91]()

---

## Configuration Validation

The system validates configuration using custom validation logic in `validation.ts` for complex constraints that cannot be expressed in basic schemas.

**Configuration Validation Functions**

```mermaid
graph TB
    LaunchConfig["BrowserLauncherOptions"]
    ValidateLaunchConfig["validateLaunchConfig()<br/>Dimension & proxy checks"]
    ValidateTimezone["validateTimezone()<br/>Timezone resolution"]
    IsSimilarConfig["isSimilarConfig()<br/>Browser reuse check"]
    ConfigError["ConfigurationError<br/>with field & value"]
    ValidConfig["Valid Configuration"]
    
    LaunchConfig --> ValidateLaunchConfig
    LaunchConfig --> ValidateTimezone
    ValidateLaunchConfig -->|"invalid"| ConfigError
    ValidateTimezone -->|"invalid"| ConfigError
    ValidateLaunchConfig -->|"valid"| ValidConfig
    ValidateTimezone -->|"valid"| ValidConfig
    LaunchConfig --> IsSimilarConfig
```

**Sources:** [api/src/services/cdp/utils/validation.ts:31-105]()

### Dimension Validation

The `validateLaunchConfig` function enforces constraints on browser dimensions:

- Dimensions must be positive numbers.
- Maximum dimensions: 7680x4320 pixels (8K resolution).
- Proxy URLs must be valid URL format.

**Sources:** [api/src/services/cdp/utils/validation.ts:31-62]()

### Timezone Validation

The `validateTimezone` function validates timezone strings and includes timeout protection:

- Resolves timezone promises with a default 10-second timeout.
- Validates using `Intl.DateTimeFormat` API.
- Throws `ConfigurationError` with `ConfigurationField.TIMEZONE` on failure.

**Sources:** [api/src/services/cdp/utils/validation.ts:72-105]()

### Configuration Comparison

The `isSimilarConfig` function determines if two browser configurations are similar enough to reuse an existing browser instance. It compares fields like `headless`, `proxyUrl`, `userAgent`, and `dimensions`.

**Sources:** [api/src/services/cdp/utils/validation.ts:114-189]()

---

## Environment Variable Validation

The system uses Zod to validate environment variables at startup, ensuring that the application doesn't run with invalid configuration.

**Environment Schema Definition**

The `envSchema` in `api/src/env.ts` handles:
- **Type Coercion**: Converting string env vars to booleans or numbers.
- **Default Values**: Providing sensible defaults (e.g., `PORT: "3000"`).
- **Complex Parsing**: Parsing `DEFAULT_HEADERS` from a JSON string into a record.

**Sources:** [api/src/env.ts:6-86]()

---

## Type System Components

**Component Mapping**

```mermaid
graph TB
    subgraph "API Workspace"
        ZodSchemas["Zod Schema Definitions<br/>sessions.schema.ts"]
        EnvSchema["Environment Schema<br/>env.ts"]
        ValidationLogic["Custom Validation<br/>validation.ts"]
        RouteHandlers["Controller Handlers<br/>sessions.controller.ts"]
    end
    
    subgraph "UI Workspace"
        GeneratedTypes["Generated Types<br/>@hey-api/openapi-ts"]
        FormResolvers["Zod Resolvers<br/>@hookform/resolvers"]
        ReactComponents["React Components"]
    end
    
    ZodSchemas --> RouteHandlers
    EnvSchema --> ValidationLogic
    RouteHandlers --> GeneratedTypes
    GeneratedTypes --> ReactComponents
    FormResolvers --> ReactComponents
```

**Sources:** [api/src/env.ts:1-86](), [api/src/modules/sessions/sessions.schema.ts:1-127](), [ui/package.json:16-17]()

---

## Complex Type Examples

### Browser Launcher Options

The `BrowserLauncherOptions` interface in `api/src/types/browser.ts` is the central type for browser configuration, bridging the API schema and the `CDPService`.

**Key Fields:**
- `sessionContext`: Includes cookies, localStorage, and IndexedDB state.
- `optimizeBandwidth`: A boolean or a granular `OptimizeBandwidthOptions` object.
- `fingerprint`: Uses `BrowserFingerprintWithHeaders` from `fingerprint-generator`.

**Sources:** [api/src/types/browser.ts:28-58]()

### Session Details

The `SessionDetails` schema provides a comprehensive view of a session's state, including usage metrics and connection URLs.

**Key Fields:**
- `status`: Enum of `["idle", "live", "released", "failed"]`.
- `proxyTxBytes` / `proxyRxBytes`: Metrics for data transmitted through the proxy.
- `websocketUrl`: The endpoint for streaming the browser view.

**Sources:** [api/src/modules/sessions/sessions.schema.ts:93-127]()

---

# Page: Deployment & Operations

# Deployment & Operations

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Dockerfile](Dockerfile)
- [README.md](README.md)
- [api/Dockerfile](api/Dockerfile)
- [api/entrypoint.sh](api/entrypoint.sh)
- [docker-compose.dev.yml](docker-compose.dev.yml)
- [docker-compose.yml](docker-compose.yml)
- [images/star_img.png](images/star_img.png)
- [render.yaml](render.yaml)
- [ui/Dockerfile](ui/Dockerfile)

</details>



This document covers production deployment, container architecture, and operational considerations for the steel-browser system. It provides an overview of deployment options, runtime dependencies, environment configuration, and operational best practices.

For detailed configuration of individual subsystems, see:
- Container internals and build process: [Container Architecture](#13.1)
- Volume configuration and data persistence: [Storage & Persistence](#13.2)
- Port configuration and network setup: [Network Configuration](#13.3)
- Automated build and deployment: [CI/CD Pipeline](#13.4)
- System monitoring and health endpoints: [Health Checks & Monitoring](#13.5)

For initial setup and configuration details, see [Getting Started](#2).

## Deployment Options

The steel-browser system supports three primary deployment modes:

| Deployment Mode | Image(s) | Use Case |
|----------------|----------|----------|
| **Combined Container** | `ghcr.io/steel-dev/steel-browser:latest` | Single-container deployment with API and UI bundled. [Dockerfile:71-125]() |
| **Separate Containers** | `ghcr.io/steel-dev/steel-browser-api:latest`<br/>`ghcr.io/steel-dev/steel-browser-ui:latest` | Multi-container deployment with independent scaling. [docker-compose.yml:1-29]() |
| **Standalone** | Build from source | Development or custom environments using `npm run dev`. [README.md:124-132]() |

The combined container includes both the Fastify API server and the React UI application, served through a single Nginx instance. The separate container approach allows independent scaling and deployment of the API and UI layers.

**Sources:** [docker-compose.yml:1-40](), [Dockerfile:1-126](), [README.md:76-108]()

## Runtime Stack

```mermaid
graph TB
    subgraph Container["steel-browser-api Container"]
        Nginx["Nginx<br/>(Port 9223 → 9222)"]
        Fastify["Fastify API Server<br/>(Port 3000)"]
        Node["Node.js 22.13.0"]
        
        subgraph Browser["Browser Components"]
            Chromium["Chromium Browser<br/>(/usr/bin/chromium)"]
            ChromeDriver["ChromeDriver<br/>(/usr/bin/chromedriver)"]
            CDP["CDP Endpoint<br/>(Port 9222)"]
        end
        
        subgraph System["System Services"]
            DBus["DBus Daemon<br/>(/var/run/dbus)"]
            Xvfb["Xvfb Display<br/>(:10)"]
        end
        
        subgraph Runtime["Runtime Dependencies"]
            Java["JRE<br/>(Selenium support)"]
            Fonts["Font Packages<br/>(Multi-language)"]
        end
    end
    
    Nginx -->|"proxy_pass"| CDP
    Fastify -->|"puppeteer-core"| Chromium
    Fastify -->|"WebDriver"| ChromeDriver
    Chromium -->|"requires"| DBus
    Chromium -->|"headless display"| Xvfb
    Chromium -->|"exposes"| CDP
    ChromeDriver -->|"controls"| Chromium
    
    Node -->|"runs"| Fastify
```

**Runtime Stack Components:**

| Component | Purpose | Location |
|-----------|---------|----------|
| **Node.js 22.13.0** | JavaScript runtime for API server | [api/Dockerfile:1]() |
| **Nginx** | Reverse proxy for CDP connections | [api/Dockerfile:67]() |
| **Chromium** | Browser automation target | [api/Dockerfile:92]() |
| **ChromeDriver** | Selenium WebDriver implementation | [api/Dockerfile:92]() |
| **DBus** | Inter-process communication for Chrome | [api/Dockerfile:90]() |
| **Xvfb** | Virtual framebuffer for headless rendering | [api/Dockerfile:75]() |
| **JRE** | Java runtime for Selenium Grid compatibility | [api/Dockerfile:78]() |

**Sources:** [api/Dockerfile:1-110](), [api/entrypoint.sh:1-127]()

## Container Initialization Flow

```mermaid
sequenceDiagram
    participant Docker
    participant Entrypoint as "entrypoint.sh"
    participant DBus
    participant Nginx
    participant Chrome as "Chrome/ChromeDriver"
    participant API as "Fastify API"
    
    Docker->>Entrypoint: Start container
    
    alt DEBUG=true
        Entrypoint->>DBus: init_dbus()
        DBus-->>Entrypoint: System bus ready
        Entrypoint->>Chrome: verify_chrome()
        Chrome-->>Entrypoint: Versions verified
    end
    
    alt START_NGINX=true
        Entrypoint->>Nginx: start_nginx()
        Nginx-->>Entrypoint: Listening on 9223
    end
    
    Entrypoint->>Entrypoint: Export CDP_REDIRECT_PORT=9223
    Entrypoint->>Entrypoint: Export DISPLAY=:10
    
    Entrypoint->>API: exec node ./api/build/index.js
    API->>API: Initialize Fastify plugins
    API->>API: Start WebSocket server
    API-->>Docker: Ready (Port 3000)
```

The [api/entrypoint.sh]() script orchestrates container startup:

1. **Parse Arguments** - Check for `--no-nginx` flag [api/entrypoint.sh:93-100]()
2. **Initialize DBus** - Start system bus daemon [api/entrypoint.sh:12-31]()
3. **Verify Chrome** - Check browser and driver installation [api/entrypoint.sh:33-63]()
4. **Start Nginx** - Launch reverse proxy for CDP [api/entrypoint.sh:65-89]()
5. **Set Environment** - Configure `CDP_REDIRECT_PORT` and `DISPLAY` [api/entrypoint.sh:108-110]()
6. **Start API** - Execute node directly (not via npm) [api/entrypoint.sh:124]()

The script uses `exec` to replace the shell process with the Node.js process, ensuring proper signal handling for graceful shutdown.

**Sources:** [api/entrypoint.sh:91-127]()

## Environment Variables

### Core Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `NODE_ENV` | `production` | Runtime environment mode. [api/Dockerfile:7]() |
| `PUPPETEER_CACHE_DIR` | `/app/.cache` | Puppeteer browser cache location. [api/Dockerfile:8]() |
| `DISPLAY` | `:10` | X11 display for headless rendering. [api/Dockerfile:9]() |
| `CHROME_BIN` | `/usr/bin/chromium` | Chrome binary path. [api/Dockerfile:11]() |
| `CHROME_PATH` | `/usr/bin/chromium` | Alternate Chrome path variable. [api/Dockerfile:12]() |

**Sources:** [api/Dockerfile:7-12]()

### Network Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_IP` | `localhost` | Host IP address for binding. [api/Dockerfile:104]() |
| `CDP_REDIRECT_PORT` | `9223` | External CDP port (Nginx). [api/entrypoint.sh:109]() |
| `DOMAIN` | `localhost:3000` | API domain for URL generation. [docker-compose.yml:12]() |
| `CDP_DOMAIN` | `localhost:9223` | CDP domain for client connections. [docker-compose.yml:13]() |

**Sources:** [api/Dockerfile:104-105](), [api/entrypoint.sh:109](), [docker-compose.yml:12-13]()

### Storage Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `LOG_STORAGE_ENABLED` | `false` | Enable DuckDB event logging. [docker-compose.yml:14]() |
| `LOG_STORAGE_PATH` | `/data/logs/browser-logs.duckdb` | DuckDB database path. [docker-compose.yml:15]() |

**Sources:** [docker-compose.yml:14-15]()

### UI Configuration

The UI container uses environment variables that are substituted at runtime:

| Variable | Default | Description |
|----------|---------|-------------|
| `API_URL` | `http://api:3000` | Backend API URL (Docker network). [docker-compose.yml:24]() |
| `VITE_API_URL` | `""` | API endpoint path (proxied by Nginx). [Dockerfile:33]() |

**Sources:** [docker-compose.yml:24](), [Dockerfile:33]()

## Docker Compose Deployment

### Production Configuration

The standard production deployment uses two services: `api` and `ui`.

```yaml
# docker-compose.yml
services:
  api:
    image: ghcr.io/steel-dev/steel-browser-api:latest
    ports:
      - "3000:3000"  # Fastify API
      - "9223:9223"  # CDP proxy
    volumes:
      - logs:/data/logs
      - exports:/tmp/steel-browser-exports
      - ./.cache:/app/.cache
    environment:
      - DOMAIN=${DOMAIN:-localhost:3000}
      - CDP_DOMAIN=${CDP_DOMAIN:-localhost:9223}
      - LOG_STORAGE_ENABLED=true
    networks:
      - steel-network

  ui:
    image: ghcr.io/steel-dev/steel-browser-ui:latest
    ports:
      - "5173:80"  # Nginx serving UI
    environment:
      - API_URL=${API_URL:-http://api:3000}
    depends_on:
      - api
    networks:
      - steel-network
```

**Sources:** [docker-compose.yml:1-40]()

### Volume Mounts

| Volume | Mount Point | Purpose |
|--------|-------------|---------|
| `logs` | `/data/logs` | DuckDB browser event logs. [docker-compose.yml:8]() |
| `exports` | `/tmp/steel-browser-exports` | Session file storage and archives. [docker-compose.yml:9]() |
| `.cache` | `/app/.cache` | Puppeteer browser binaries. [docker-compose.yml:10]() |

The `logs` and `exports` volumes use Docker managed volumes for persistence, while `.cache` is mounted from the host to share browser binaries across container restarts.

**Sources:** [docker-compose.yml:7-10](), [docker-compose.yml:35-39]()

## Port Configuration

```mermaid
graph LR
    subgraph External["External Clients"]
        Client["HTTP/WS Clients"]
        Browser["Web Browser"]
        CDPClient["CDP Clients"]
    end
    
    subgraph Host["Host System"]
        Port3000["Port 3000"]
        Port9223["Port 9223"]
        Port5173["Port 5173"]
    end
    
    subgraph APIContainer["steel-browser-api Container"]
        Nginx9223["Nginx :9223"]
        Fastify3000["Fastify :3000"]
        CDP9222["Chromium CDP :9222"]
    end
    
    subgraph UIContainer["steel-browser-ui Container"]
        NginxUI["Nginx :80"]
    end
    
    Client -->|"HTTP/WS"| Port3000
    CDPClient -->|"CDP/WS"| Port9223
    Browser -->|"HTTP"| Port5173
    
    Port3000 -->|"forward"| Fastify3000
    Port9223 -->|"forward"| Nginx9223
    Port5173 -->|"forward"| NginxUI
    
    Nginx9223 -->|"proxy_pass"| CDP9222
```

| Port | Service | Protocol | Purpose |
|------|---------|----------|---------|
| **3000** | Fastify API | HTTP/WS | REST API and WebSocket streaming. [api/Dockerfile:102]() |
| **9223** | Nginx (CDP Proxy) | CDP/WS | Chrome DevTools Protocol connections. [api/Dockerfile:102]() |
| **5173** | Nginx (UI) | HTTP | React UI application (host mapping). [docker-compose.yml:22]() |

The Nginx reverse proxy at port 9223 translates external CDP connections to the internal Chromium CDP port, enabling CDP access without exposing the browser directly.

**Sources:** [api/Dockerfile:102](), [docker-compose.yml:4-6](), [docker-compose.yml:21-22]()

## Multi-Stage Build Process

```mermaid
graph TB
    subgraph Base["Base Stage<br/>(node:22.13.0)"]
        BaseEnv["Environment Setup<br/>PUPPETEER_CACHE_DIR<br/>DISPLAY<br/>PATH"]
    end
    
    subgraph UIBuild["UI Build Stage"]
        UIInstall["npm ci -w ui"]
        UIRunBuild["npm run build -w ui"]
    end
    
    subgraph APIBuild["API Build Stage"]
        BuildTools["Build Tools<br/>build-essential, xvfb"]
        APIInstall["npm ci -w api"]
        APIRunBuild["npm run build -w api"]
        ExtBuild["Build recorder extension"]
    end
    
    subgraph Production["Production Stage"]
        RuntimeDeps["Runtime Dependencies<br/>nginx, chromium<br/>fonts, dbus"]
        CopyAPI["COPY --from=api-build"]
        CopyUI["COPY --from=ui-build"]
        Entrypoint["entrypoint.sh"]
    end
    
    Base --> UIBuild
    Base --> APIBuild
    Base --> Production
    UIBuild --> CopyUI
    APIBuild --> CopyAPI
    RuntimeDeps --> Entrypoint
```

The [Dockerfile]() for the combined image uses a four-stage build:

1. **Base Stage** - Sets up common Node.js environment. [Dockerfile:3-12]()
2. **UI Build Stage** - Builds the React frontend. [Dockerfile:23-33]()
3. **API Build Stage** - Builds the Fastify backend and extensions. [Dockerfile:36-70]()
4. **Production Stage** - Installs system dependencies and assembles the final image. [Dockerfile:72-126]()

This approach minimizes the final image size by excluding build tools and dev dependencies.

**Sources:** [Dockerfile:1-126]()

## Graceful Shutdown

The entrypoint script uses `exec` to replace the shell process with the Node.js process, ensuring signals (SIGTERM, SIGINT) are delivered directly to the API server:

```bash
# api/entrypoint.sh:124
exec node ./api/build/index.js
```

This enables the application to implement graceful shutdown logic, waiting for active browser sessions to complete or be released before terminating. Using `npm run start` would introduce npm's signal handling, preventing proper cleanup.

**Sources:** [api/entrypoint.sh:118-124]()

## Operational Considerations

### Resource Requirements

| Resource | Minimum | Recommended |
|----------|---------|-------------|
| **CPU** | 2 cores | 4+ cores |
| **Memory** | 2 GB | 4+ GB |
| **Disk** | 5 GB | 20+ GB (for logs/exports) |

Each browser session requires significant memory. Plan capacity based on expected concurrent sessions.

### Container Lifecycle

```mermaid
stateDiagram-v2
    [*] --> Initializing: docker run
    Initializing --> DBusInit: DEBUG=true
    Initializing --> NginxStart: DEBUG=false
    DBusInit --> ChromeVerify
    ChromeVerify --> NginxStart
    NginxStart --> EnvSetup
    EnvSetup --> Running: exec node
    Running --> Shutdown: SIGTERM/SIGINT
    Shutdown --> WaitSessions: Graceful cleanup
    WaitSessions --> [*]: Sessions released
```

1. **Initialization** - DBus and system services start. [api/entrypoint.sh:12-31]()
2. **Chrome Verification** - Browser and driver versions checked (if `DEBUG=true`). [api/entrypoint.sh:33-63]()
3. **Nginx Launch** - CDP proxy starts (unless `--no-nginx`). [api/entrypoint.sh:65-89]()
4. **Environment Setup** - CDP port and display configured. [api/entrypoint.sh:108-110]()
5. **API Start** - Fastify server launches. [api/entrypoint.sh:124]()

**Sources:** [api/entrypoint.sh:91-127]()

### Debugging and Logging

Enable debug logging by setting `DEBUG=true`:

```bash
docker run -e DEBUG=true ghcr.io/steel-dev/steel-browser
```

Debug mode enables:
- DBus initialization logging. [api/entrypoint.sh:13]()
- Chrome/ChromeDriver version verification. [api/entrypoint.sh:35]()
- Nginx startup logging. [api/entrypoint.sh:68]()
- Environment state logging. [api/entrypoint.sh:113]()

**Sources:** [api/entrypoint.sh:5-9]()

### Health Checks

For production deployments (e.g., Render), a health check endpoint is available at `/v1/health`.

**Sources:** [render.yaml:6]()

---

# Page: Container Architecture

# Container Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.dockerignore](.dockerignore)
- [.github/workflows/check-build.yml](.github/workflows/check-build.yml)
- [api/.dockerignore](api/.dockerignore)
- [api/Dockerfile](api/Dockerfile)
- [api/entrypoint.sh](api/entrypoint.sh)
- [docker-compose.dev.yml](docker-compose.dev.yml)
- [docker-compose.yml](docker-compose.yml)
- [ui/Dockerfile](ui/Dockerfile)

</details>



This document explains the Docker container architecture of Steel Browser, including multi-stage build processes, initialization sequences, runtime process management, and container orchestration. This covers the physical deployment structure and how processes are managed within containers.

For information about storage volumes and data persistence, see [Storage & Persistence](#13.2). For network configuration and port mappings, see [Network Configuration](#13.3). For details about Docker Compose environment variables, see [Environment Configuration](#2.2).

## Overview

Steel Browser uses a multi-container architecture orchestrated by Docker Compose. The system consists of two primary service containers:

- **API Container**: Runs the Node.js Fastify server, manages Chromium browser processes, and provides the core automation engine.
- **UI Container**: Serves the React dashboard via nginx.

Both containers use multi-stage builds to separate build-time dependencies from runtime environments, minimizing production image size and attack surface.

Sources: [docker-compose.yml:1-40](), [api/Dockerfile:1-110](), [ui/Dockerfile:1-30]()

## API Container Multi-Stage Build

The API container uses a three-stage build process defined in the `api/Dockerfile`.

### Stage 1: Base Image (`base`)

```mermaid
graph TB
    NodeBase["node:22.13.0-slim"]
    BaseStage["base stage"]
    WorkDir["/app working directory"]
    EnvVars["Environment Variables<br/>NODE_ENV=production<br/>PUPPETEER_CACHE_DIR=/app/.cache<br/>DISPLAY=:10<br/>CHROME_BIN=/usr/bin/chromium"]
    BaseDeps["Base System Dependencies<br/>expat, libxslt1.1, libpam0g"]
    
    NodeBase --> BaseStage
    BaseStage --> WorkDir
    BaseStage --> EnvVars
    BaseStage --> BaseDeps
```

The base stage establishes the foundation image with Node.js 22.13.0-slim and installs minimal runtime dependencies. Key environment variables are set at this stage:

| Environment Variable | Value | Purpose |
|---------------------|-------|---------|
| `NODE_ENV` | `production` | Optimizes Node.js runtime behavior |
| `PUPPETEER_CACHE_DIR` | `/app/.cache` | Stores Puppeteer browser binaries |
| `DISPLAY` | `:10` | X11 display for headless browser |
| `CHROME_BIN` | `/usr/bin/chromium` | Chrome binary location |
| `CHROME_PATH` | `/usr/bin/chromium` | Alternate Chrome path reference |

Sources: [api/Dockerfile:3-26]()

### Stage 2: Build Stage (`build`)

```mermaid
graph TB
    BaseStage["FROM base"]
    BuildTools["Install Build Tools<br/>build-essential<br/>pkg-config<br/>python-is-python3<br/>xvfb"]
    CopyFiles["Copy Source Files<br/>package.json<br/>package-lock.json<br/>api/"]
    HuskySkip["npm pkg set scripts.prepare"]
    NpmCI["npm ci --include=dev --workspace=api"]
    BuildAPI["npm run build -w api"]
    ExtensionBuild["Build recorder extension<br/>api/extensions/recorder"]
    Prune["npm prune --omit=dev"]
    
    BaseStage --> BuildTools
    BuildTools --> CopyFiles
    CopyFiles --> HuskySkip
    HuskySkip --> NpmCI
    NpmCI --> BuildAPI
    BuildAPI --> ExtensionBuild
    ExtensionBuild --> Prune
```

The build stage installs development dependencies and compiles the TypeScript source code. Notable steps:

1. **Husky Skip**: Disables git hooks in Docker environment [api/Dockerfile:41]().
2. **Workspace Install**: Uses npm workspaces to install only API dependencies [api/Dockerfile:46]().
3. **Extension Build**: Separately builds the recorder browser extension [api/Dockerfile:48-56]().
4. **Dependency Pruning**: Removes dev dependencies to reduce artifact size [api/Dockerfile:59-60]().

Sources: [api/Dockerfile:28-61]()

### Stage 3: Production Stage (`production`)

```mermaid
graph TB
    BaseStage["FROM base"]
    
    subgraph "System Dependencies"
        BrowserDeps["Browser Dependencies<br/>fonts-ipafont-gothic<br/>fonts-wqy-zenhei<br/>fonts-thai-tlwg<br/>libxss1"]
        ChromiumPkg["Chromium Installation<br/>chromium<br/>chromium-driver"]
        RuntimeTools["Runtime Tools<br/>nginx, wget, curl<br/>unzip, default-jre<br/>dbus, procps<br/>x11-xserver-utils"]
    end
    
    subgraph "File System Setup"
        FilesDir["mkdir -p /files"]
        Entrypoint["COPY entrypoint.sh"]
        BuildArtifacts["COPY --from=build /app /app"]
    end
    
    subgraph "Container Configuration"
        Ports["EXPOSE 3000 9223"]
        EnvOverrides["HOST_IP=localhost<br/>DBUS_SESSION_BUS_ADDRESS=autolaunch:"]
        EntrypointCmd["ENTRYPOINT /app/api/entrypoint.sh"]
    end
    
    BaseStage --> BrowserDeps
    BaseStage --> ChromiumPkg
    BaseStage --> RuntimeTools
    BaseStage --> FilesDir
    BaseStage --> Entrypoint
    BaseStage --> BuildArtifacts
    BaseStage --> Ports
    BaseStage --> EnvOverrides
    BaseStage --> EntrypointCmd
```

The production stage installs all runtime dependencies and copies build artifacts. Key components:

- **Chromium**: Installs both the browser (`chromium`) and WebDriver (`chromium-driver`) [api/Dockerfile:92]().
- **nginx**: Provides optional reverse proxy functionality [api/Dockerfile:67]().
- **Xvfb**: Virtual framebuffer for headless display [api/Dockerfile:75]().
- **DBus**: Inter-process communication required for Chrome [api/Dockerfile:79-80]().
- **Fonts**: International font support for browser rendering [api/Dockerfile:69-73]().
- **Java**: Required for Selenium WebDriver support (`default-jre`) [api/Dockerfile:78]().

Sources: [api/Dockerfile:62-110]()

## Container Initialization Process

The `api/entrypoint.sh` script orchestrates container startup, performing initialization checks and starting required services before launching the Node.js application.

```mermaid
graph TB
    Start["entrypoint.sh execution"]
    ParseArgs["Parse CLI Arguments<br/>--no-nginx flag"]
    
    subgraph "Conditional Initialization (DEBUG=true)"
        InitDBus["init_dbus()<br/>Start dbus-daemon --system --fork<br/>Verify with dbus-send"]
        VerifyChrome["verify_chrome()<br/>Check /usr/bin/chromium<br/>Check /usr/bin/chromedriver<br/>Log versions"]
    end
    
    StartNginx["start_nginx()<br/>nginx -c /app/api/nginx.conf<br/>Verify with nginx -t"]
    
    SetEnv["Export Environment<br/>CDP_REDIRECT_PORT=9223<br/>DISPLAY=:10"]
    
    ExecNode["exec node ./api/build/index.js"]
    
    Start --> ParseArgs
    ParseArgs --> InitDBus
    InitDBus --> VerifyChrome
    VerifyChrome --> StartNginx
    ParseArgs --> StartNginx
    StartNginx --> SetEnv
    SetEnv --> ExecNode
```

### Initialization Functions

#### `init_dbus()`

Initializes the D-Bus system message bus required for Chrome inter-process communication:

1. Creates `/var/run/dbus` directory [api/entrypoint.sh:14]().
2. Removes stale PID file if present [api/entrypoint.sh:16-18]().
3. Starts `dbus-daemon --system --fork` [api/entrypoint.sh:20]().
4. Validates connection with `dbus-send` [api/entrypoint.sh:23-26]().

This function only runs when `DEBUG=true` [api/entrypoint.sh:102-103]().

Sources: [api/entrypoint.sh:12-31]()

#### `verify_chrome()`

Validates Chrome and ChromeDriver installation:

| Check | Path | Fallback |
|-------|------|----------|
| Chrome binary | `/usr/bin/chromium` | `$CHROME_EXECUTABLE_PATH` |
| ChromeDriver | `/usr/bin/chromedriver` | None (required) |

The function logs version information for both executables and only runs in DEBUG mode [api/entrypoint.sh:104]().

Sources: [api/entrypoint.sh:33-63]()

#### `start_nginx()`

Starts nginx if `START_NGINX=true`:

1. Launches nginx with custom config: `nginx -c /app/api/nginx.conf` [api/entrypoint.sh:69]().
2. Polls for successful startup with 10 retry attempts [api/entrypoint.sh:72-82]().
3. Skips startup if `--no-nginx` CLI flag detected [api/entrypoint.sh:86]().

The nginx process acts as a reverse proxy for certain API routes and static file serving.

Sources: [api/entrypoint.sh:65-89]()

### Final Execution

The entrypoint script uses `exec` to replace the shell process with the Node.js application:

```bash
exec node ./api/build/index.js
```

This ensures:
- The Node.js process becomes PID 1, receiving signals directly.
- Graceful shutdown hooks in the application receive SIGTERM.
- No intermediate shell process interferes with signal handling.

The direct execution is critical for session cleanup during container shutdown [api/entrypoint.sh:120-124]().

Sources: [api/entrypoint.sh:91-127]()

## Runtime Process Architecture

The API container runs multiple processes simultaneously:

```mermaid
graph TB
    subgraph "Container PID Namespace"
        PID1["PID 1<br/>node ./api/build/index.js<br/>(Fastify Server)"]
        
        subgraph "Child Processes"
            Nginx["nginx worker processes<br/>(if START_NGINX=true)"]
            XvfbProc["Xvfb :10<br/>(Virtual Display)"]
            ChromeProc["chromium-browser<br/>--remote-debugging-port=9223"]
            ChromeDriver["chromedriver<br/>(if isSelenium=true)"]
        end
        
        PID1 -.->|spawns via Puppeteer| ChromeProc
        PID1 -.->|spawns if needed| ChromeDriver
        ChromeProc -->|connects to| XvfbProc
    end
    
    subgraph "External Connections"
        Port3000["Port 3000<br/>HTTP API"]
        Port9223["Port 9223<br/>CDP WebSocket"]
    end
    
    PID1 --> Port3000
    ChromeProc --> Port9223
    Nginx -.->|proxies| PID1
```

### Process Lifecycle

| Process | Started By | Lifecycle | Purpose |
|---------|-----------|-----------|---------|
| `node` | `api/entrypoint.sh` (PID 1) | Container lifetime | Fastify API server |
| `nginx` | `api/entrypoint.sh` | Container lifetime | Optional reverse proxy |
| `Xvfb` | Environment setup | Container lifetime | Virtual display server |
| `chromium` | Puppeteer (`CDPService`) | Session lifetime | Browser automation |
| `chromedriver` | Selenium mode | Session lifetime | WebDriver protocol |

The Node.js process (PID 1) is responsible for:
- Spawning Chrome via Puppeteer's `browser.launch()` method.
- Managing Chrome subprocess lifecycle.
- Handling SIGTERM for graceful session release.
- Cleaning up temporary files and browser profiles.

Sources: [api/Dockerfile:9-12](), [api/entrypoint.sh:109-124]()

## UI Container Architecture

The UI container uses a simpler two-stage build optimized for static asset serving:

```mermaid
graph LR
    subgraph "Build Stage (node:22.13.0)"
        NodeBase["Node base image"]
        CopyPkg["COPY package files<br/>and ui/ directory"]
        NpmCI["npm ci -w ui<br/>--ignore-scripts"]
        NpmBuild["npm run build -w ui"]
        Prune["npm prune --omit=dev"]
        DistDir["ui/dist output"]
    end
    
    subgraph "Production Stage (nginx:alpine)"
        NginxAlpine["nginx:alpine"]
        CopyDist["COPY --from=base<br/>/app/ui/dist"]
        CopyNginxConf["COPY nginx.conf.template"]
        CopyEntrypoint["COPY entrypoint.sh"]
        ServeDir["/usr/share/nginx/html"]
        Port80["EXPOSE 80"]
    end
    
    NodeBase --> CopyPkg
    CopyPkg --> NpmCI
    NpmCI --> NpmBuild
    NpmBuild --> Prune
    Prune --> DistDir
    
    NginxAlpine --> CopyDist
    NginxAlpine --> CopyNginxConf
    NginxAlpine --> CopyEntrypoint
    CopyDist --> ServeDir
    CopyNginxConf --> Port80
    CopyEntrypoint --> Port80
```

Key differences from API container:

- **Single-purpose**: Only serves static files, no backend logic.
- **Minimal runtime**: Alpine-based nginx image (~40MB total).
- **No browser dependencies**: No Chrome, fonts, or X11 requirements.
- **Template-based config**: nginx configuration supports runtime environment variable substitution via `entrypoint.sh` [ui/Dockerfile:24-25]().

Sources: [ui/Dockerfile:1-30]()

## Docker Compose Orchestration

The `docker-compose.yml` file defines service composition, networking, and volume management.

```mermaid
graph TB
    subgraph "Services"
        APIService["api service<br/>ghcr.io/steel-dev/steel-browser-api:latest"]
        UIService["ui service<br/>ghcr.io/steel-dev/steel-browser-ui:latest"]
    end
    
    subgraph "Network"
        Bridge["steel-network<br/>driver: bridge"]
    end
    
    subgraph "Volumes"
        LogsVol["logs volume<br/>driver: local"]
        ExportsVol["exports volume<br/>driver: local"]
        CacheBind[".cache directory<br/>bind mount"]
    end
    
    subgraph "Port Mappings"
        API3000["Host:3000 → Container:3000<br/>(HTTP API)"]
        API9223["Host:9223 → Container:9223<br/>(CDP)"]
        UI5173["Host:5173 → Container:80<br/>(UI Dashboard)"]
    end
    
    APIService --> Bridge
    UIService --> Bridge
    
    APIService --> LogsVol
    APIService --> ExportsVol
    APIService --> CacheBind
    
    APIService --> API3000
    APIService --> API9223
    UIService --> UI5173
    
    UIService -.->|depends_on| APIService
```

### Service Definitions

#### API Service Configuration

```yaml
volumes:
  - logs:/data/logs                      # DuckDB log storage
  - exports:/tmp/steel-browser-exports   # Temporary export files
  - ./.cache:/app/.cache                 # Puppeteer browser cache
```

The API service mounts three volumes:
- **Named volume `logs`**: Persists browser logs stored in DuckDB [docker-compose.yml:8]().
- **Named volume `exports`**: Temporary storage for file exports [docker-compose.yml:9]().
- **Bind mount `.cache`**: Shares Puppeteer browser binaries with host [docker-compose.yml:10]().

Environment variables configure external connectivity:
- `DOMAIN`: API server's external hostname [docker-compose.yml:12]().
- `CDP_DOMAIN`: CDP WebSocket endpoint hostname [docker-compose.yml:13]().
- `LOG_STORAGE_PATH`: DuckDB database file location [docker-compose.yml:15]().

Sources: [docker-compose.yml:2-17]()

#### UI Service Configuration

The UI service is simpler, with only environment configuration:

```yaml
environment:
  - API_URL=${API_URL:-http://api:3000}
```

The `API_URL` uses Docker's internal DNS (`api:3000`) to communicate with the API service over the `steel-network` bridge [docker-compose.yml:24](). The `depends_on` directive ensures the API starts before the UI [docker-compose.yml:25-26]().

Sources: [docker-compose.yml:19-28]()

### Network Configuration

```yaml
networks:
  steel-network:
    name: steel-network
    driver: bridge
```

The `steel-network` bridge provides:
- Internal DNS resolution (services can reference each other by name).
- Network isolation from other Docker networks.
- Default NAT for external connectivity.

Both services join this network, enabling the UI to call the API using the hostname `api` [docker-compose.yml:30-33]().

Sources: [docker-compose.yml:30-33]()

### Volume Strategy

| Volume Type | Name | Container Path | Purpose | Persistence |
|-------------|------|----------------|---------|-------------|
| Named | `logs` | `/data/logs` | DuckDB browser logs | Docker-managed |
| Named | `exports` | `/tmp/steel-browser-exports` | Temporary exports | Docker-managed |
| Bind | `.cache` | `/app/.cache` | Puppeteer binaries | Host filesystem |

The bind mount for `.cache` enables sharing browser binaries across container recreations and with the host system, avoiding repeated downloads [docker-compose.yml:10]().

Sources: [docker-compose.yml:35-39]()

## Development vs Production Configuration

The development Compose file (`docker-compose.dev.yml`) differs from production in key ways:

```mermaid
graph TB
    subgraph "docker-compose.yml (Production)"
        ProdAPI["api:<br/>image: ghcr.io/.../api:latest"]
        ProdUI["ui:<br/>image: ghcr.io/.../ui:latest"]
        ProdVols["volumes:<br/>logs (named)<br/>exports (named)<br/>.cache (bind)"]
    end
    
    subgraph "docker-compose.dev.yml (Development)"
        DevAPI["api:<br/>build: ./api/Dockerfile"]
        DevUI["ui:<br/>build: ./ui/Dockerfile"]
        DevVols["volumes:<br/>.cache (bind only)"]
    end
    
    ProdAPI -.->|uses pre-built| ProdVols
    ProdUI -.->|images from registry| ProdVols
    
    DevAPI -.->|builds from source| DevVols
    DevUI -.->|local Dockerfile| DevVols
```

Key differences:

| Aspect | Production | Development |
|--------|-----------|-------------|
| Image source | Pre-built from GHCR | Local build from Dockerfile |
| Log volume | Persistent named volume | None (ephemeral) |
| Export volume | Named volume | None |
| Cache volume | Bind mount | Bind mount |
| Build context | Not applicable | Current directory `.` |

Development mode builds from source and omits log/export volumes since these are typically not needed during development, reducing setup complexity [docker-compose.dev.yml:1-35]().

Sources: [docker-compose.dev.yml:1-35]()

## Container Lifecycle Sequence

```mermaid
sequenceDiagram
    participant DC as docker-compose
    participant API as API Container
    participant UI as UI Container
    participant Entrypoint as entrypoint.sh
    participant Node as Node Process
    participant Chrome as Chrome Process
    
    DC->>API: docker-compose up
    DC->>UI: docker-compose up
    
    API->>Entrypoint: Execute /app/api/entrypoint.sh
    
    alt DEBUG=true
        Entrypoint->>Entrypoint: init_dbus()
        Entrypoint->>Entrypoint: verify_chrome()
    end
    
    Entrypoint->>Entrypoint: start_nginx()
    Entrypoint->>Node: exec node ./api/build/index.js
    
    Node->>Node: Initialize Fastify
    Node->>Node: Register plugins
    Node->>Node: Listen on port 3000
    
    Note over Node: Ready to accept requests
    
    UI->>UI: Start nginx on port 80
    UI->>UI: Serve static files
    
    Note over API,UI: System operational
    
    Node->>Chrome: Spawn via Puppeteer (on demand)
    Chrome->>Chrome: Launch with --remote-debugging-port=9223
    
    DC->>API: docker-compose stop (SIGTERM)
    Node->>Node: Graceful shutdown hooks
    Node->>Chrome: Close browser sessions
    Chrome->>Chrome: Cleanup profiles
    Node->>Node: Exit with code 0
    
    DC->>UI: docker-compose stop (SIGTERM)
    UI->>UI: nginx graceful shutdown
```

The lifecycle demonstrates:

1. **Sequential startup**: Entrypoint initialization before application launch.
2. **On-demand browser**: Chrome processes spawn only when sessions are created.
3. **Graceful shutdown**: SIGTERM propagates properly because Node.js is PID 1.
4. **Session cleanup**: Application code handles session release before exit.

The `exec` command in `api/entrypoint.sh` is critical for proper signal handling [api/entrypoint.sh:124]().

Sources: [api/entrypoint.sh:91-127](), [docker-compose.yml:1-40]()

---

# Page: Storage & Persistence

# Storage & Persistence

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [api/Dockerfile](api/Dockerfile)
- [api/entrypoint.sh](api/entrypoint.sh)
- [api/src/modules/files/files.controller.ts](api/src/modules/files/files.controller.ts)
- [api/src/modules/files/files.routes.ts](api/src/modules/files/files.routes.ts)
- [api/src/modules/files/files.schema.ts](api/src/modules/files/files.schema.ts)
- [api/src/plugins/file-storage.ts](api/src/plugins/file-storage.ts)
- [api/src/services/cdp/instrumentation/storage/duckdb-storage.ts](api/src/services/cdp/instrumentation/storage/duckdb-storage.ts)
- [api/src/services/cdp/instrumentation/storage/safe-json.ts](api/src/services/cdp/instrumentation/storage/safe-json.ts)
- [api/src/services/cdp/instrumentation/utils.ts](api/src/services/cdp/instrumentation/utils.ts)
- [api/src/services/file.service.ts](api/src/services/file.service.ts)
- [docker-compose.dev.yml](docker-compose.dev.yml)
- [docker-compose.yml](docker-compose.yml)
- [ui/Dockerfile](ui/Dockerfile)

</details>



This document explains how Steel Browser manages data storage and persistence across container restarts, including volume strategies, cache management, log storage, and data lifecycle patterns. This page focuses on the deployment storage architecture. For session state management (cookies, localStorage, sessionStorage), see [4.3](). For file upload/download operations, see [7]().

## Volume Strategy Overview

Steel Browser employs three distinct storage strategies to balance performance, persistence, and host-level resource sharing:

```mermaid
graph TB
    subgraph HostMachine["Host Machine"]
        HostCacheDir[".cache directory<br/>(bind mount)"]
        DockerEngine["Docker Engine<br/>Volume Management"]
    end
    
    subgraph APIContainer["API Container"]
        PuppeteerCache["/app/.cache<br/>PUPPETEER_CACHE_DIR<br/>Browser Binaries"]
        LogsMount["/data/logs<br/>DuckDB Storage<br/>Browser Logs"]
        ExportsMount["/tmp/steel-browser-exports<br/>Temporary Exports<br/>PDFs, Screenshots"]
        FilesDir["/files<br/>Session Files<br/>Uploads"]
    end
    
    subgraph DockerVolumes["Docker Named Volumes"]
        LogsVolume["logs volume<br/>Persistent Storage"]
        ExportsVolume["exports volume<br/>Temporary Storage"]
    end
    
    HostCacheDir -->|"bind mount"| PuppeteerCache
    DockerEngine --> LogsVolume
    DockerEngine --> ExportsVolume
    LogsVolume -->|"mount"| LogsMount
    ExportsVolume -->|"mount"| ExportsMount
    
    PuppeteerCache -.->|"stores"| BrowserBinaries["Chromium Binaries<br/>ChromeDriver"]
    LogsMount -.->|"stores"| BrowserLogs["Browser Logs<br/>Console Output<br/>Network Events"]
    ExportsMount -.->|"stores"| ExportFiles["PDF Files<br/>Screenshots<br/>Archives"]
    FilesDir -.->|"stores"| SessionFiles["Uploaded Files<br/>Session Data<br/>files.zip"]
```

Sources: [docker-compose.yml:8-10](), [api/Dockerfile:8](), [api/Dockerfile:98]()

### Storage Strategy Comparison

| Storage Type | Location | Purpose | Persistence | Sharing |
|--------------|----------|---------|-------------|---------|
| **Bind Mount** | `./.cache:/app/.cache` | Puppeteer browser binaries | Survives container deletion | Shared across containers and host |
| **Named Volume (logs)** | `logs:/data/logs` | DuckDB browser logs database | Docker-managed persistent | Container-isolated |
| **Named Volume (exports)** | `exports:/tmp/steel-browser-exports` | Temporary export files | Docker-managed persistent | Container-isolated |
| **Container Filesystem** | `/files` | Session file uploads | Lost on container deletion | Not shared |

Sources: [docker-compose.yml:8-10](), [docker-compose.yml:35-40]()

## Puppeteer Cache Management

### Cache Directory Configuration

The Puppeteer cache directory is configured via the `PUPPETEER_CACHE_DIR` environment variable and uses a bind mount strategy to enable host-level sharing and persistence beyond container lifecycle:

```mermaid
graph LR
    subgraph Configuration["Environment Configuration"]
        EnvVar["PUPPETEER_CACHE_DIR<br/>/app/.cache"]
        DockerEnv["Dockerfile ENV<br/>Line 8"]
    end
    
    subgraph BindMount["Bind Mount Strategy"]
        HostCache["Host: ./.cache"]
        ContainerCache["Container: /app/.cache"]
    end
    
    subgraph CachedContent["Cached Content"]
        ChromiumBinary["Chromium Binary<br/>~300MB"]
        ChromeDriver["ChromeDriver Binary<br/>~20MB"]
        PuppeteerMetadata["Puppeteer Metadata<br/>revision info"]
    end
    
    DockerEnv --> EnvVar
    EnvVar --> ContainerCache
    HostCache <|--|>|"bidirectional sync"| ContainerCache
    ContainerCache --> ChromiumBinary
    ContainerCache --> ChromeDriver
    ContainerCache --> PuppeteerMetadata
```

**Key Characteristics:**

- **Path**: `/app/.cache` inside container, mapped to `./.cache` on host [api/Dockerfile:8](), [docker-compose.yml:10]()
- **Size**: Approximately 320MB for Chromium and ChromeDriver binaries.
- **Lifecycle**: Persists across container restarts and deletions.
- **Benefit**: Avoids re-downloading browser binaries on each container rebuild.

Sources: [api/Dockerfile:8](), [docker-compose.yml:10]()

### Browser Binary Storage

When Puppeteer launches, it checks `PUPPETEER_CACHE_DIR` for compatible browser binaries. The entrypoint script verifies Chrome availability at `/usr/bin/chromium` or via `CHROME_EXECUTABLE_PATH` [api/entrypoint.sh:34-63](). The `api/Dockerfile` installs `chromium` and `chromium-driver` directly via `apt-get` [api/Dockerfile:92](), while the cache directory handles Puppeteer-managed downloads.

Sources: [api/Dockerfile:92](), [api/entrypoint.sh:34-63]()

## Log Storage

### DuckDB Persistent Storage

Steel Browser utilizes `DuckDBStorage` for high-performance browser event persistence. This storage backend is initialized with configurable resource limits to minimize CPU and memory impact.

```mermaid
graph TD
    subgraph "DuckDBStorage Implementation"
        Init["initialize()"]
        Write["write(event, context)"]
        Flush["flushWriteBuffer()"]
        Table["browser_events Table"]
    end

    subgraph "Data Flow"
        Events["BrowserEventUnion"] -->|"Buffered"| Write
        Write -->|"Batch"| Flush
        Flush -->|"SQL INSERT"| Table
    end

    subgraph "Persistence"
        Table -->|"Saves to"| DBFile["/data/logs/browser-logs.duckdb"]
    end
```

**Configuration Options:**
- **`maxThreads`**: Defaults to 2 to throttle CPU usage [api/src/services/cdp/instrumentation/storage/duckdb-storage.ts:66]().
- **`memoryLimit`**: Defaults to "256MB" [api/src/services/cdp/instrumentation/storage/duckdb-storage.ts:67]().
- **`parquetCompression`**: Supports `zstd`, `snappy` (default), `gzip`, or `none` [api/src/services/cdp/instrumentation/storage/duckdb-storage.ts:68]().
- **`writeBufferEnabled`**: Writes are batched (default 100 events) and flushed periodically (default 1000ms) to reduce I/O overhead [api/src/services/cdp/instrumentation/storage/duckdb-storage.ts:69-71]().

**Table Schema:**
The `browser_events` table includes fields for `id`, `timestamp`, `event_type`, `target_type`, `page_id`, `data` (JSON), and `context` (JSON) [api/src/services/cdp/instrumentation/storage/duckdb-storage.ts:86-96]().

Sources: [api/src/services/cdp/instrumentation/storage/duckdb-storage.ts:48-116](), [docker-compose.yml:14-15]()

## Session File Storage

### File Service Architecture

The `FileService` manages session-specific files stored in `/files` [api/src/services/file.service.ts:28](). It uses a singleton pattern and integrates with `chokidar` to monitor filesystem changes.

```mermaid
graph LR
    subgraph "FileService (api/src/services/file.service.ts)"
        FSW["FSWatcher (chokidar)"]
        Save["saveFile()"]
        Zip["_createArchive()"]
        Debounce["debouncedCreateArchive"]
    end

    subgraph "Filesystem"
        BaseDir["/files"]
        ZipFile["/tmp/.steel/files.zip"]
    end

    Save -->|"Write"| BaseDir
    BaseDir -->|"Event"| FSW
    FSW -->|"Trigger"| Debounce
    Debounce -->|"Execute"| Zip
    Zip -->|"Output"| ZipFile
```

**Key Behaviors:**
- **Path Security**: `getSafeFilePath` ensures files remain within `baseFilesPath` and prevents directory traversal [api/src/services/file.service.ts:88-97]().
- **Automated Archiving**: Any file addition, deletion, or directory change triggers a debounced call (500ms) to create a `files.zip` archive using the `archiver` library [api/src/services/file.service.ts:34-37, 47-60]().
- **Upload Handling**: The `FilesController` processes `multipart/form-data` uploads, supporting both binary file fields and URL-based downloads [api/src/modules/files/files.controller.ts:41-157]().

Sources: [api/src/services/file.service.ts:16-86](), [api/src/modules/files/files.controller.ts:17-40]()

## Export Files Storage

### Temporary Export Volume

Export files (PDFs, screenshots) are stored in `/tmp/steel-browser-exports` and mounted to a Docker named volume in production [docker-compose.yml:9]().

**Characteristics:**
- **Persistence**: Survives container restarts via the `exports` named volume [docker-compose.yml:38-39]().
- **Cleanup**: No automatic cleanup is performed by the `FileService`. Users must manage disk space manually or via external cron jobs.
- **Access**: Files are accessible via the `FilesController` download endpoints [api/src/modules/files/files.routes.ts:57-69]().

Sources: [docker-compose.yml:9, 38-39](), [api/src/modules/files/files.routes.ts:133-145]()

## Data Persistence Summary

| Data Type | Location | Persistence Level | Implementation |
|-----------|----------|-------------------|----------------|
| **Browser Binaries** | `/app/.cache` | High (Bind Mount) | `PUPPETEER_CACHE_DIR` |
| **Browser Logs** | `/data/logs/*.duckdb` | High (Named Volume) | `DuckDBStorage` |
| **Session Files** | `/files` | Ephemeral (Container) | `FileService` |
| **Export Files** | `/tmp/steel-browser-exports` | Medium (Named Volume) | `FilesController` |

Sources: [api/Dockerfile:98](), [docker-compose.yml:7-10](), [api/src/services/cdp/instrumentation/storage/duckdb-storage.ts:50]()

---

# Page: Network Configuration

# Network Configuration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.env.example](.env.example)
- [.github/workflows/build-docker.yml](.github/workflows/build-docker.yml)
- [api/Dockerfile](api/Dockerfile)
- [api/entrypoint.sh](api/entrypoint.sh)
- [api/nginx.conf](api/nginx.conf)
- [docker-compose.dev.yml](docker-compose.dev.yml)
- [docker-compose.yml](docker-compose.yml)
- [ui/.env.local.example](ui/.env.local.example)
- [ui/Dockerfile](ui/Dockerfile)
- [ui/entrypoint.sh](ui/entrypoint.sh)
- [ui/nginx.conf.template](ui/nginx.conf.template)
- [ui/src/env.ts](ui/src/env.ts)

</details>



This document covers the network architecture and configuration for Steel Browser deployment. It explains port mappings, Nginx proxying for CDP and UI services, WebSocket setup, and network-related environment variables.

## Overview

Steel Browser's network configuration utilizes a multi-layered approach to handle standard REST traffic, real-time WebSocket streaming, and Chrome DevTools Protocol (CDP) debugging:

1.  **Nginx Proxy Layer**: Used within both API and UI containers to route traffic, handle WebSocket upgrades, and provide a unified interface.
2.  **Docker Bridge Network**: Enables isolated inter-container communication using service-based DNS.
3.  **WebSocket Orchestration**: Dedicated handling for session logs, recordings, and direct browser control.

---

## Port Mappings and Nginx Proxying

### Container Port Exposure

The system exposes specific ports to facilitate different communication protocols.

| Container Port | Host Port | Service | Protocol | Purpose |
| :--- | :--- | :--- | :--- | :--- |
| `3000` | `3000` | API | HTTP/WS | REST API and WebSocket endpoints [api/Dockerfile:102]() |
| `9223` | `9223` | API (Nginx) | CDP/WS | Proxied access to internal Chromium CDP [api/Dockerfile:102]() |
| `80` | `5173` | UI (Nginx) | HTTP | Dashboard interface [ui/Dockerfile:27]() |

### API Internal Proxy (Port 9223)

The API container runs an internal Nginx instance to proxy external CDP requests (on port `9223`) to the actual Chromium instance (typically on port `9222`). This allows for better connection management and WebSocket header handling.

**Nginx CDP Configuration:**
[api/nginx.conf:6-26]()
- **WebSocket Support**: Uses `Upgrade` and `Connection` headers to support the `chrome-remote-interface`.
- **Buffering**: Disabled (`proxy_buffering off`) to ensure low-latency communication with the browser.
- **Timeouts**: Set to `86400` (24 hours) to prevent session disconnection during long-running automation.

### UI Proxy (Port 80)

The UI container uses Nginx to serve static assets and proxy API/WebSocket requests to the backend service.

**UI Nginx Configuration Template:**
[ui/nginx.conf.template:12-25]()
- `/api/`: Proxies REST requests to the backend defined by `__API_URL__`.
- `/ws/`: Handles WebSocket upgrades for real-time streaming from the backend.

```mermaid
graph TD
    subgraph "External Traffic"
        Client["User / Automation Script"]
    end

    subgraph "UI Container (nginx)"
        UINginx["Nginx (Port 80)"]
        Static["Static React Files"]
        UINginx -->|"/api/"| APIProxy["Proxy to API_URL"]
        UINginx -->|"/ws/"| WSProxy["WS Upgrade to API_URL"]
    end

    subgraph "API Container"
        Fastify["Fastify Server (Port 3000)"]
        APINginx["Nginx (Port 9223)"]
        Chromium["Chromium (Port 9222)"]
        
        APINginx -->|"Proxy WS"| Chromium
        Fastify -->|"Internal Logic"| Chromium
    end

    Client -->|Port 5173| UINginx
    Client -->|Port 3000| Fastify
    Client -->|Port 9223| APINginx
    APIProxy -.->|Internal Network| Fastify
    WSProxy -.->|Internal Network| Fastify

    Sources: [ui/nginx.conf.template:12-25](), [api/nginx.conf:10-27](), [docker-compose.yml:4-28]()
```

Sources: [api/Dockerfile:102](), [api/nginx.conf:6-26](), [ui/nginx.conf.template:12-25](), [docker-compose.yml:4-28]()

---

## WebSocket Connectivity

### Protocol Upgrades

Steel Browser relies heavily on WebSockets for live session monitoring and CDP. The networking layer must support the `101 Switching Protocols` status.

**WebSocket Endpoints:**
- **Logs/Recordings**: Handled by the Fastify server on port `3000`.
- **CDP**: Handled by Nginx on port `9223` [api/nginx.conf:13-17]().

**Client Configuration (UI):**
The UI application defaults to using relative paths for proxies, which Nginx resolves to the backend.
[ui/src/env.ts:5-6]()
- `VITE_API_URL`: Defaults to `/api`.
- `VITE_WS_URL`: Defaults to `/ws`.

### Data Flow for Live Streaming

```mermaid
sequenceDiagram
    participant UI as "React UI (Browser)"
    participant UINginx as "UI Nginx Proxy"
    participant API as "Fastify Backend"
    participant Browser as "Chromium Instance"

    UI->>UINginx: GET /ws/v1/sessions/logs (Upgrade: websocket)
    UINginx->>API: Proxy WS Upgrade [ui/nginx.conf.template:18-25]
    API->>UI: 101 Switching Protocols
    
    loop Stream Events
        Browser->>API: CDP Event (Console/Network)
        API->>UI: WebSocket Message (Log Entry)
    end

    Sources: [ui/nginx.conf.template:18-25](), [ui/src/env.ts:5-6]()
```

Sources: [ui/nginx.conf.template:18-25](), [ui/src/env.ts:5-6](), [api/nginx.conf:13-17]()

---

## Docker Network Architecture

### Bridge Network Topology

The `steel-network` facilitates communication between the API and UI services using the Docker bridge driver [docker-compose.yml:30-33]().

**Service Hostnames:**
- `api`: Reachable by the UI at `http://api:3000` [docker-compose.yml:24]().
- `ui`: Serves the dashboard.

### Environment-Based Discovery

The networking behavior is influenced by variables defined in the Docker compose files:
- `DOMAIN`: The external domain for the API [docker-compose.yml:12]().
- `CDP_DOMAIN`: The external domain for CDP access [docker-compose.yml:13]().
- `API_URL`: Used by the UI container to locate the backend [docker-compose.yml:24]().

**Initialization Sequence:**
1.  **Entrypoint Start**: The `entrypoint.sh` script is invoked.
2.  **Nginx Initialization**: In the API container, `start_nginx` is called unless `--no-nginx` is passed [api/entrypoint.sh:66-89]().
3.  **Port Hardcoding**: `CDP_REDIRECT_PORT` is exported as `9223` to match the Nginx listener [api/entrypoint.sh:109]().
4.  **UI Variable Substitution**: The UI `entrypoint.sh` uses `sed` to inject the `API_URL` into the Nginx configuration template [ui/entrypoint.sh:8-11]().

Sources: [docker-compose.yml:12-33](), [api/entrypoint.sh:66-109](), [ui/entrypoint.sh:8-11]()

---

## Network Environment Variables

### Core Configuration

| Variable | Default | Purpose |
| :--- | :--- | :--- |
| `HOST_IP` | `localhost` | Local binding for DBus and internal services [api/Dockerfile:104]() |
| `DOMAIN` | `localhost:3000` | Publicly accessible API address [docker-compose.yml:12]() |
| `CDP_DOMAIN` | `localhost:9223` | Publicly accessible CDP address [docker-compose.yml:13]() |
| `API_URL` | `http://api:3000` | Backend address used by UI Nginx [docker-compose.yml:24]() |
| `VITE_API_URL` | `/api` | UI internal path for API requests [ui/src/env.ts:5]() |
| `VITE_WS_URL` | `/ws` | UI internal path for WebSockets [ui/src/env.ts:6]() |

### Proxy and Bypass

The system supports outbound proxying for browser sessions, which can be configured to bypass internal networks.
- `PROXY_URL`: Outbound proxy for the browser.
- `PROXY_INTERNAL_BYPASS`: Prevents the browser from using the proxy for internal service addresses.

Sources: [api/Dockerfile:104](), [docker-compose.yml:12-24](), [ui/src/env.ts:5-6]()

---

## SSL/TLS and Production Considerations

### External Termination

In production environments, SSL is typically terminated at an external load balancer or a global Nginx instance.

**Requirements for Upstream Proxies:**
1.  **WebSocket Headers**: Must pass `Upgrade` and `Connection` headers.
2.  **Timeout Settings**: Must support long-lived connections (matching the internal Nginx `86400` seconds) [api/nginx.conf:21-22]().
3.  **Large Payloads**: CDP messages can be large; ensure buffer sizes are sufficient.

### Production Build Flow

The production Docker images are built using multi-stage builds to minimize the attack surface and optimize network delivery of assets [api/Dockerfile:62-110]().
- **API Build**: Installs `chromium` and `nginx` [api/Dockerfile:67, 92]().
- **UI Build**: Uses `nginx:alpine` for a lightweight footprint [ui/Dockerfile:22]().

Sources: [api/Dockerfile:62-110](), [ui/Dockerfile:22](), [api/nginx.conf:21-22]()

---

# Page: CI/CD Pipeline

# CI/CD Pipeline

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/labeler.yml](.github/labeler.yml)
- [.github/workflows/build-docker.yml](.github/workflows/build-docker.yml)
- [.github/workflows/pr-checks.yml](.github/workflows/pr-checks.yml)
- [.github/workflows/release.yml](.github/workflows/release.yml)
- [api/nginx.conf](api/nginx.conf)
- [ui/src/env.ts](ui/src/env.ts)

</details>



## Purpose and Scope

This document describes the Continuous Integration and Continuous Deployment (CI/CD) pipeline for the steel-browser system. The pipeline automates building and publishing multi-platform Docker images to GitHub Container Registry (GHCR), manages semantic versioning, and performs quality checks on pull requests.

For details on container architecture and multi-stage builds, see [Container Architecture](#13.1). For deployment instructions using published images, see [Docker Deployment](#2.3).

---

## Overview

The steel-browser CI/CD pipeline is implemented using GitHub Actions and consists of three primary workflows:
1. **Docker Build**: Automates multi-platform image builds.
2. **Quality Checks**: Validates PR titles and monitors for breaking changes.
3. **Automatic Release**: Handles semantic versioning, tagging, and changelog generation.

**Sources:** [.github/workflows/build-docker.yml:1-38](), [.github/workflows/pr-checks.yml:1-44](), [.github/workflows/release.yml:1-113]()

---

## Workflow Architecture

### Build and Push Workflow

The primary workflow `build-docker.yml` executes on every push to the `main` branch and performs the following operations:

```mermaid
graph TB
    PushMain["Push to main branch"]
    CheckoutRepo["Checkout repository<br/>(actions/checkout@v4)"]
    SetupBuildx["Setup Docker Buildx<br/>(docker/setup-buildx-action@v3)"]
    LoginGHCR["Login to GHCR<br/>(docker/login-action@v3)"]
    
    subgraph "Image Build Jobs"
        BuildSteel["Build steel-browser:latest<br/>Dockerfile: ./Dockerfile<br/>Platforms: linux/amd64, linux/arm64"]
        BuildAPI["Build steel-browser-api:latest<br/>Dockerfile: ./api/Dockerfile<br/>Platforms: linux/amd64, linux/arm64"]
        BuildUI["Build steel-browser-ui:latest<br/>Dockerfile: ./ui/Dockerfile<br/>Platforms: linux/amd64, linux/arm64"]
    end
    
    PushGHCR["Push images to ghcr.io/steel-dev"]
    
    PushMain --> CheckoutRepo
    CheckoutRepo --> SetupBuildx
    SetupBuildx --> LoginGHCR
    LoginGHCR --> BuildSteel
    LoginGHCR --> BuildAPI
    LoginGHCR --> BuildUI
    
    BuildSteel --> PushGHCR
    BuildAPI --> PushGHCR
    BuildUI --> PushGHCR
```

**Workflow Structure:**

| Step | Action | Purpose |
|------|--------|---------|
| Checkout | `actions/checkout@v4` | Clones the repository to the runner [.github/workflows/build-docker.yml:13-14]() |
| Setup Buildx | `docker/setup-buildx-action@v3` | Configures Docker Buildx for multi-platform builds [.github/workflows/build-docker.yml:16-18]() |
| Login | `docker/login-action@v3` | Authenticates to GitHub Container Registry [.github/workflows/build-docker.yml:20-25]() |
| Build & Push | `docker buildx build` | Builds and pushes images for multiple platforms [.github/workflows/build-docker.yml:27-37]() |

---

## Pull Request Quality Checks

The `pr-checks.yml` workflow ensures that contributions maintain project standards.

### Validation Logic

The workflow monitors specific file paths to warn reviewers about potential breaking changes in core services:

```mermaid
graph TD
    PR["Pull Request Created"] --> TitleCheck["Validate PR Title<br/>(Conventional Commits)"]
    PR --> Labeler["Auto-label based on<br/>labeler.yml"]
    PR --> BreakingCheck["Check for Breaking Changes"]

    subgraph "Sensitive Paths"
        Types["api/src/types/"]
        PluginBase["api/src/steel-browser-plugin.ts"]
        CorePlugins["api/src/services/cdp/plugins/core/"]
    end

    BreakingCheck -- "Match found" --> Warning["Post Warning Comment"]
```

- **Semantic PRs**: Enforces conventional commit messages for automated versioning [.github/workflows/pr-checks.yml:17-20]().
- **Path-Based Labeling**: Uses `.github/labeler.yml` to categorize PRs (e.g., `api`, `ui`, `cdp`, `plugin-system`) [.github/labeler.yml:1-72]().
- **Breaking Change Detection**: Triggers warnings if files in `api/src/types/` or core plugin directories are modified [.github/workflows/pr-checks.yml:35-38]().

**Sources:** [.github/workflows/pr-checks.yml:13-44](), [.github/labeler.yml:1-72]()

---

## Release and Versioning

The `release.yml` workflow automates the software lifecycle using semantic versioning.

### Automatic Version Bumping

The pipeline calculates the next version based on commit message keywords:
- **Major**: `breaking`, `breaking-change`, `major` [.github/workflows/release.yml:29]()
- **Patch**: `patch`, `fix`, `docs`, `feat`, `minor` [.github/workflows/release.yml:27]()
- **Suffix**: All automated releases currently use a `-beta` suffix [.github/workflows/release.yml:25]()

### Changelog Generation

A changelog is automatically generated by categorizing commits into:
- **Improvements**: Commits labeled `feat` or `feature` [.github/workflows/release.yml:56-61]()
- **Bug Fixes**: Commits labeled `fix` or `bug` [.github/workflows/release.yml:63-68]()
- **Documentation**: Commits labeled `docs` [.github/workflows/release.yml:70-74]()

**Sources:** [.github/workflows/release.yml:20-91]()

---

## Docker Image Build Pipeline

The workflow builds three distinct Docker images:

### Image Types

**1. steel-browser:latest (Combined Image)**
- Built from root `Dockerfile` [.github/workflows/build-docker.yml:29]()
- Contains both API server and UI static files.

**2. steel-browser-api:latest (API Image)**
- Built from `api/Dockerfile` [.github/workflows/build-docker.yml:33]()
- Contains Fastify API, Chromium browser, and Nginx.
- Nginx configuration in `api/nginx.conf` handles CDP proxying on port 9223 [.api/nginx.conf:10-27]().

**3. steel-browser-ui:latest (UI Image)**
- Built from `ui/Dockerfile` [.github/workflows/build-docker.yml:37]()
- Contains static React UI build artifacts.
- Uses `VITE_API_URL` (default `/api`) and `VITE_WS_URL` (default `/ws`) for backend communication [ui/src/env.ts:3-7]().

---

## Multi-Platform Build Configuration

### Platform Support

The pipeline uses Docker Buildx to create multi-architecture images supporting:
- **linux/amd64**: Standard x86_64 architecture.
- **linux/arm64**: ARM64 architecture (Apple Silicon, AWS Graviton).

### Build Command Structure

```bash
docker buildx build --platform linux/amd64,linux/arm64 --push -t ghcr.io/steel-dev/steel-browser:latest .
```

**Sources:** [.github/workflows/build-docker.yml:28-37]()

---

## Container Registry Publishing

### GitHub Container Registry (GHCR)

All images are published to `ghcr.io/steel-dev` using the following authentication:
- **Registry**: `ghcr.io` [.github/workflows/build-docker.yml:23]()
- **Username**: `${{ secrets.GH_USERNAME }}` [.github/workflows/build-docker.yml:24]()
- **Password**: `${{ secrets.GH_TOKEN }}` [.github/workflows/build-docker.yml:25]()

---

## Related Pages

- [Container Architecture](#13.1) - Detailed container structure and multi-stage builds
- [Docker Deployment](#2.3) - Instructions for deploying published images
- [Network Configuration](#13.3) - Port and proxy configuration for deployments
- [Environment Configuration](#2.2) - Comprehensive guide to environment variables referenced in CI/CD

---

# Page: Health Checks & Monitoring

# Health Checks & Monitoring

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Dockerfile](Dockerfile)
- [README.md](README.md)
- [api/.env.example](api/.env.example)
- [api/src/env.ts](api/src/env.ts)
- [api/src/plugins/schemas.ts](api/src/plugins/schemas.ts)
- [api/src/routes.ts](api/src/routes.ts)
- [api/src/telemetry/noop.ts](api/src/telemetry/noop.ts)
- [api/src/telemetry/tracer.ts](api/src/telemetry/tracer.ts)
- [images/star_img.png](images/star_img.png)
- [render.yaml](render.yaml)

</details>



This document covers the health check endpoints, browser state monitoring, session statistics, and operational metrics available in Steel Browser. These features enable production monitoring, debugging, and observability of browser sessions and system health.

For information about real-time event streaming and WebSocket-based monitoring, see [WebSocket API](). For deployment architecture and container health, see [Container Architecture]().

## Overview

Steel Browser provides multiple monitoring surfaces:
- **Health Check Endpoint**: Basic service health validation for container orchestration.
- **Session Statistics**: Detailed metrics about active and past browser sessions.
- **Live Browser State**: Real-time information about running browser instances and pages.
- **Operational Metrics**: Resource usage, proxy statistics, and session performance data.
- **Telemetry**: OpenTelemetry integration for tracing system execution.

## Health Check Endpoint

The system exposes a health check endpoint at `/v1/health` for container orchestrators and monitoring tools to verify service availability.

### Health Check Configuration

```mermaid
graph TB
    subgraph "Natural Language Space"
        UserConfig["User Deployment Config"]
        Orchestrator["Orchestrator (Render/K8s)"]
    end

    subgraph "Code Entity Space"
        RenderYAML["render.yaml"]
        HealthRoute["GET /v1/health"]
    end

    UserConfig --> RenderYAML
    RenderYAML -->|"healthCheckPath"| Orchestrator
    Orchestrator -->|"HTTP GET"| HealthRoute
    HealthRoute -->|"200 OK"| Healthy["Service Available"]
```

**Sources:** [render.yaml:6-6]()

The health check path is configured in deployment manifests and invoked periodically by the orchestration platform to determine if the container should receive traffic or needs to be restarted.

**Sources:** [render.yaml:1-13]()

## Session Monitoring API

The Sessions API provides comprehensive monitoring of browser session lifecycle, state, and resource consumption.

### Session Details Endpoint

The `GET /v1/sessions/:id` endpoint returns detailed information about a specific session.

```mermaid
graph LR
    Request["GET /v1/sessions/:id"]
    Controller["handleGetSessionDetails"]
    SessionService["SessionService.activeSession"]
    Response["SessionDetails Schema"]
    
    Request --> Controller
    Controller -->|"lookup session"| SessionService
    SessionService --> Response
    
    Response -->|"metrics"| Metrics["duration, eventCount, creditsUsed, proxyTxBytes, proxyRxBytes"]
    Response -->|"connectivity"| URLs["websocketUrl, debugUrl, debuggerUrl, sessionViewerUrl"]
```

**Sources:** [api/src/modules/sessions/sessions.schema.ts:89-122](), [api/src/routes.ts:2-2]()

### Session Details Schema

| Field | Type | Description |
|-------|------|-------------|
| `id` | `string (uuid)` | Unique identifier for the session |
| `status` | `enum` | Current status: `idle`, `live`, `released`, `failed` |
| `duration` | `number` | Session duration in milliseconds |
| `eventCount` | `number` | Number of events processed |
| `proxyTxBytes` | `number` | Data transmitted through proxy (bytes) |
| `proxyRxBytes` | `number` | Data received through proxy (bytes) |
| `websocketUrl` | `string` | WebSocket connection URL for events |
| `debugUrl` | `string` | Live browser view URL |

**Sources:** [api/src/modules/sessions/sessions.schema.ts:89-122]()

## Live Browser State Monitoring

The live details endpoint provides real-time information about the browser instance, including all open pages and their current state.

### Live Session Details Data Flow

```mermaid
graph TB
    subgraph "API Layer"
        LiveRoute["GET /v1/sessions/:id/live"]
    end

    subgraph "Service Layer"
        CDP["CDPService"]
        SessSvc["SessionService"]
    end

    LiveRoute --> CDP
    LiveRoute --> SessSvc
    
    CDP -->|"page.url()"| PageData["Page Metadata (Title, URL, Favicon)"]
    CDP -->|"getBrowserState()"| BrowserMeta["Browser Version, Page Count"]
    SessSvc -->|"activeSession"| SessionMeta["User Agent, Dimensions"]
```

**Sources:** [api/src/modules/sessions/sessions.schema.ts:148-170](), [api/src/routes.ts:2-2]()

### Browser State Object

The `browserState` object in the live details response includes:
- **`status`**: Current lifecycle state (`idle`, `live`, `released`, `failed`).
- **`userAgent`**: The specific User-Agent string used by the browser instance.
- **`browserVersion`**: Version string retrieved from the Chrome process.
- **`pageCount`**: Number of active tabs/pages currently open.

**Sources:** [api/src/modules/sessions/sessions.schema.ts:155-165]()

## Telemetry & Tracing

Steel Browser includes an OpenTelemetry-based tracing system to monitor internal function execution and performance.

### Tracer Implementation

The system uses a `tracer` utility to wrap core functions in active spans. This is implemented in `api/src/telemetry/tracer.ts`.

```mermaid
graph TB
    subgraph "Telemetry Logic"
        Tracer["tracer object"]
        Traceable["@traceable decorator"]
        OTel["@opentelemetry/api"]
    end

    Traceable -->|"wraps"| Methods["Core Service Methods"]
    Methods --> Tracer
    Tracer -->|"startActiveSpan"| OTel
    OTel -->|"Export"| Collector["OTLP/Jaeger/Zipkin"]
```

**Sources:** [api/src/telemetry/tracer.ts:18-75]()

### Tracing Utilities
- **`@traceable`**: A method decorator used to automatically create spans for class methods. It converts class names to kebab-case for tracer names (e.g., `SessionService` becomes `session-service`). [api/src/telemetry/tracer.ts:77-122]()
- **`tracer.startActiveSpan`**: A functional wrapper for manual instrumentation. [api/src/telemetry/tracer.ts:19-63]()
- **`noopSpan`**: A fallback implementation used when OpenTelemetry is not configured or fails to load, preventing system crashes during monitoring failures. [api/src/telemetry/noop.ts:3-38]()

## Operational Configuration

Monitoring behavior is influenced by several environment variables defined in `api/src/env.ts`:

| Variable | Default | Description |
|----------|---------|-------------|
| `ENABLE_CDP_LOGGING` | `false` | Enables verbose logging of Chrome DevTools Protocol traffic. |
| `ENABLE_VERBOSE_LOGGING`| `false` | Increases log granularity for debugging. |
| `LOG_STORAGE_ENABLED` | `false` | Enables persistent storage of logs (typically via DuckDB). |
| `LOG_STORAGE_PATH` | - | Filesystem path for persistent log storage. |

**Sources:** [api/src/env.ts:34-48](), [api/src/env.ts:73-78]()

## Monitoring Released Sessions

When a session is released, the system maintains a record of its final metrics in `pastSessions`. Monitoring systems can still query these IDs to retrieve historical performance data such as total duration and final proxy usage.

**Sources:** [api/src/modules/sessions/sessions.schema.ts:89-122]()

---

# Page: Development Guide

# Development Guide

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CONTRIBUTING.md](CONTRIBUTING.md)
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- [docs/DEVELOPMENT_SETUP.md](docs/DEVELOPMENT_SETUP.md)
- [docs/README.md](docs/README.md)
- [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)

</details>



This guide provides an overview of the steel-browser codebase structure, development patterns, and extension mechanisms for developers who want to contribute to or extend the system. It covers the monorepo organization, core architectural patterns, plugin development, and testing strategies.

For detailed environment setup instructions, see [Development Environment Setup](#14.1). For in-depth architectural explanations, see [Architecture Deep Dive](#14.2). For plugin development, see [Creating Custom Plugins](#14.4).

## Monorepo Structure

The steel-browser codebase is organized as an npm workspace monorepo with three primary workspaces:

| Workspace | Directory | Purpose | Technology Stack |
|-----------|-----------|---------|------------------|
| **api** | `/api` | Backend server and browser automation engine | Fastify, TypeScript, Puppeteer |
| **ui** | `/ui` | Web-based session management dashboard | React, Vite, TanStack Query |
| **repl** | `/repl` | Interactive scripting environment | Node.js, Puppeteer |

**Workspace Structure**

```mermaid
graph TB
    Root["Root package.json<br/>(Workspace Manager)"]
    
    API["api/<br/>@steel-browser/api"]
    UI["ui/<br/>@steel-browser/ui"]
    REPL["repl/<br/>@steel-browser/repl"]
    
    Root -->|workspace| API
    Root -->|workspace| UI
    Root -->|workspace| REPL
    
    APISrc["api/src/<br/>TypeScript Sources"]
    APIBuild["api/build/<br/>Compiled JavaScript"]
    
    UISrc["ui/src/<br/>React Components"]
    UIBuild["ui/dist/<br/>Static Assets"]
    
    REPLSrc["repl/src/<br/>Example Scripts"]
    
    API --> APISrc
    API --> APIBuild
    
    UI --> UISrc
    UI --> UIBuild
    
    REPL --> REPLSrc
    
    APISrc --> CDPService["services/cdp/cdp.service.ts"]
    APISrc --> SessionService["services/session.service.ts"]
    APISrc --> Plugins["services/cdp/plugins/"]
```

**Sources:** [CONTRIBUTING.md:53-71](), [docs/DEVELOPMENT_SETUP.md:121-152]()

## Core Service Architecture

The API workspace contains the core browser automation engine, organized into distinct service layers.

**Service Layer Class Hierarchy**

```mermaid
graph TB
    FastifyApp["Fastify Server<br/>api/src/index.ts"]
    
    SessionService["SessionService<br/>api/src/services/session.service.ts"]
    CDPService["CDPService<br/>api/src/services/cdp/cdp.service.ts"]
    FileService["FileService<br/>api/src/services/file.service.ts"]
    
    PluginManager["PluginManager<br/>cdp/plugins/core/plugin-manager.ts"]
    BasePlugin["BasePlugin<br/>cdp/plugins/core/base-plugin.ts"]
    
    FastifyApp -->|registers| SteelBrowserPlugin["api/src/steel-browser-plugin.ts"]
    SteelBrowserPlugin -->|injects| SessionService
    SteelBrowserPlugin -->|injects| CDPService
    SteelBrowserPlugin -->|injects| FileService
    
    SessionService -->|orchestrates| CDPService
    SessionService -->|manages files| FileService
    
    CDPService -->|manages| PluginManager
    PluginManager -->|registers| BasePlugin
```

**Sources:** [docs/ARCHITECTURE.md:26-115](), [CONTRIBUTING.md:73-101]()

### Key Service Classes

**CDPService** (`api/src/services/cdp/cdp.service.ts`)
- Primary browser automation service using Chrome DevTools Protocol. [docs/ARCHITECTURE.md:28-38]()
- Manages browser lifecycle, context isolation, and fingerprinting. [docs/ARCHITECTURE.md:33-38]()
- Implements plugin architecture via `PluginManager`. [docs/ARCHITECTURE.md:77-85]()
- Key methods: `launch()`, `shutdown()`, `createPage()`, `getPages()`. [docs/ARCHITECTURE.md:41-56]()

**SessionService** (`api/src/services/session.service.ts`)
- Orchestrates browser sessions with isolated contexts (cookies, storage). [docs/ARCHITECTURE.md:86-96]()
- Handles session persistence, cleanup, and concurrent management. [docs/ARCHITECTURE.md:91-95]()
- Interfaces with `CDPService` for browser execution. [CONTRIBUTING.md:94-97]()

**FileService** (`api/src/services/file.service.ts`)
- Handles session-scoped file operations (uploads, downloads). [docs/ARCHITECTURE.md:107-114]()
- Manages storage isolation and automatic cleanup on session end. [docs/ARCHITECTURE.md:113-114]()

**Sources:** [docs/ARCHITECTURE.md:28-115](), [CONTRIBUTING.md:84-101]()

## Development Workflow

The repository uses npm workspaces for dependency management and provides unified build and development commands.

**Development Commands**

```bash
# Start all workspaces in development mode with hot-reloading
npm run dev

# Build all workspaces
npm run build

# Development mode for API only
npm run dev -w api

# Development mode for UI only
npm run dev -w ui
```

**Sources:** [docs/DEVELOPMENT_SETUP.md:142-163](), [CONTRIBUTING.md:28-36]()

### API Development Workflow

The API uses Fastify's plugin system for modular design. [docs/ARCHITECTURE.md:174-188]() All API endpoints use Zod schemas for validation. [docs/ARCHITECTURE.md:202-212]()

**Route Organization**
- **Actions** (`/v1/*`): Scrape, screenshot, PDF. [docs/ARCHITECTURE.md:194]()
- **Sessions** (`/v1/sessions/*`): Session management. [docs/ARCHITECTURE.md:195]()
- **CDP** (`/v1/cdp/*`): Direct protocol access. [docs/ARCHITECTURE.md:196]()
- **Files** (`/v1/files/*`): Upload/download. [docs/ARCHITECTURE.md:197]()

**Sources:** [docs/ARCHITECTURE.md:172-212]()

## Plugin System Architecture

The plugin system enables extending browser automation behavior through lifecycle hooks without modifying core code. [docs/ARCHITECTURE.md:58-60]()

**Plugin Lifecycle Flow**

```mermaid
sequenceDiagram
    participant SB as Steel Browser
    participant PM as PluginManager
    participant BP as BasePlugin
    
    SB->>PM: onBrowserLaunch(browser)
    PM->>BP: onBrowserLaunch(browser)
    
    SB->>PM: onPageCreated(page)
    PM->>BP: onPageCreated(page)
    
    SB->>PM: onPageNavigate(page)
    PM->>BP: onPageNavigate(page)
    
    SB->>PM: onBrowserClose(browser)
    PM->>BP: onBrowserClose(browser)
    
    SB->>PM: onShutdown()
    PM->>BP: onShutdown()
```

**Sources:** [docs/ARCHITECTURE.md:118-141](), [CONTRIBUTING.md:181-193]()

### Plugin Lifecycle Hooks

Plugins extend `BasePlugin` and can implement methods such as:
- `onBrowserLaunch(browser)`: Called when browser process starts. [CONTRIBUTING.md:185]()
- `onPageCreated(page)`: Called for each new page/tab. [CONTRIBUTING.md:186]()
- `onPageNavigate(page)`: Called on page navigation. [CONTRIBUTING.md:187]()
- `onBrowserClose(browser)`: Called when browser closes. [CONTRIBUTING.md:190]()
- `onShutdown()`: Final cleanup hook. [CONTRIBUTING.md:191]()

**Sources:** [docs/ARCHITECTURE.md:65-74](), [CONTRIBUTING.md:181-193]()

## Configuration and Environment

Configuration is managed through environment variables. For local development, these are typically placed in a `.env` file. [docs/DEVELOPMENT_SETUP.md:211-215]()

| Variable | Description | Default |
|----------|-------------|---------|
| `PORT` | API server port | `3000` |
| `CHROME_HEADLESS` | Run browser in headless mode | `false` (dev) |
| `CHROME_EXECUTABLE_PATH` | Path to Chrome/Chromium binary | System dependent |
| `ENABLE_CDP_LOGGING` | Enable detailed CDP protocol logs | `true` (dev) |

**Sources:** [docs/DEVELOPMENT_SETUP.md:211-234](), [docs/TROUBLESHOOTING.md:50-58]()

## Debugging Techniques

### Enable Debug Logging
You can enable various levels of logging to troubleshoot issues:
```bash
export ENABLE_VERBOSE_LOGGING=true
export ENABLE_CDP_LOGGING=true
export LOG_CUSTOM_EMIT_EVENTS=true
```
**Sources:** [docs/TROUBLESHOOTING.md:203-214]()

### Browser Debugging
To see what the browser is doing during automation, disable headless mode:
```bash
export CHROME_HEADLESS=false
```
You can also connect to the browser's DevTools directly at `http://localhost:9223`. [docs/TROUBLESHOOTING.md:231-240]()

### Node.js Inspector
Start the API with the inspector enabled for debugging with VS Code or Chrome DevTools:
```bash
node --inspect ./api/build/index.js
```
**Sources:** [docs/TROUBLESHOOTING.md:216-227]()

## Troubleshooting Common Issues

### Browser Launch Failures
Often caused by missing dependencies or incorrect paths. [docs/TROUBLESHOOTING.md:41-48]()
- **Solution**: Verify `CHROME_EXECUTABLE_PATH` is set correctly. [docs/TROUBLESHOOTING.md:50-58]()
- **Solution (Linux)**: Ensure required system libraries (like `libnss3`) are installed. [docs/TROUBLESHOOTING.md:60-77]()

### Port Conflicts
If port `3000` (API) or `5173` (UI) is already in use. [docs/TROUBLESHOOTING.md:89-95]()
- **Solution**: Use `lsof -i :3000` to find the process and kill it, or change the `PORT` env variable. [docs/TROUBLESHOOTING.md:97-110]()

**Sources:** [docs/TROUBLESHOOTING.md:41-110]()

---

# Page: Development Environment Setup

# Development Environment Setup

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [api/package.json](api/package.json)
- [api/src/index.ts](api/src/index.ts)
- [api/src/plugins/selenium.ts](api/src/plugins/selenium.ts)
- [api/tsconfig.json](api/tsconfig.json)
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- [docs/DEVELOPMENT_SETUP.md](docs/DEVELOPMENT_SETUP.md)
- [docs/README.md](docs/README.md)
- [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)
- [package-lock.json](package-lock.json)

</details>



This document covers the local development workflow for Steel Browser, including environment setup, npm scripts, development servers, hot reload mechanisms, and debugging tools. This guide is intended for contributors developing and extending the Steel Browser codebase.

For production deployment configuration, see [Docker Deployment](). For environment variable configuration, see [Environment Configuration]().

---

## Prerequisites

Steel Browser requires the following tools for local development:

| Requirement | Version | Purpose |
|------------|---------|---------|
| Node.js | >= 22.0.0 | Runtime for API and build tools |
| npm | Latest | Package manager |
| Chrome/Chromium | Latest stable | Browser automation target |
| Docker (optional) | Latest | Containerized development |

The Node.js version requirement is specified in the root engines configuration [package-lock.json:32-34]().

**Sources:** [package-lock.json:32-34](), [docs/DEVELOPMENT_SETUP.md:16-41](), [docs/TROUBLESHOOTING.md:23-37]()

---

## Development Workflow Architecture

Steel Browser supports two development workflows: Docker-based and local Node.js-based. Both approaches provide hot reload capabilities and access to all development tools.

### Development Flow Overview

```mermaid
graph TB
    subgraph "Development Options"
        DockerFlow["Docker-based Development<br/>docker-compose.dev.yml"]
        LocalFlow["Local Node.js Development<br/>npm run dev"]
    end
    
    subgraph "Docker Development Path"
        DockerCompose["docker-compose -f docker-compose.dev.yml up --build"]
        DockerAPI["API Container<br/>Port 3000<br/>Volume: ./api → /app/api"]
        DockerUI["UI Container<br/>Port 5173<br/>Volume: ./ui → /app/ui"]
        DockerChrome["Chrome in Container<br/>Port 9223"]
        
        DockerCompose --> DockerAPI
        DockerCompose --> DockerUI
        DockerAPI --> DockerChrome
    end
    
    subgraph "Local Development Path"
        NpmInstall["npm install<br/>Workspace installation"]
        NpmDev["npm run dev<br/>Concurrently start servers"]
        LocalAPI["API Dev Server<br/>Port 3000<br/>tsx watch src/index.ts"]
        LocalUI["Vite Dev Server<br/>Port 5173<br/>HMR enabled"]
        LocalChrome["Local Chrome<br/>CHROME_EXECUTABLE_PATH"]
        
        NpmInstall --> NpmDev
        NpmDev --> LocalAPI
        NpmDev --> LocalUI
        LocalAPI --> LocalChrome
    end
    
    DockerFlow --> DockerCompose
    LocalFlow --> NpmInstall
    
    DockerAPI -.->|"Hot reload<br/>via volume mount"| CodeChanges["Code Changes<br/>./api, ./ui"]
    LocalAPI -.->|"Hot reload<br/>via tsx watch"| CodeChanges
    LocalUI -.->|"HMR"| CodeChanges
```

**Sources:** [docs/DEVELOPMENT_SETUP.md:119-176](), [docs/DEVELOPMENT_SETUP.md:180-191](), [api/package.json:47]()

---

## Docker-based Development

### Using docker-compose.dev.yml

The development Docker Compose configuration mounts local source directories into containers, enabling live code changes without rebuilding images.

```bash
# Start development environment with volume mounts
docker-compose -f docker-compose.dev.yml up --build

# View logs
docker-compose -f docker-compose.dev.yml logs -f
```

The `docker-compose.dev.yml` file allows developers to modify code in `./api` or `./ui` and see changes reflected immediately via container-side watchers.

### Port Mappings

| Service | Container Port | Host Port | Purpose |
|---------|---------------|-----------|---------|
| API | 3000 | 3000 | Fastify server and REST API [api/src/index.ts:11]() |
| UI Dev Server | 5173 | 5173 | Vite development server |
| CDP | 9223 | 9223 | Chrome DevTools Protocol [docs/DEVELOPMENT_SETUP.md:220]() |

**Sources:** [docs/DEVELOPMENT_SETUP.md:180-191](), [docs/DEVELOPMENT_SETUP.md:213-234](), [api/src/index.ts:10-18]()

---

## Local Node.js Development

### Installation and Setup

The Steel Browser monorepo uses npm workspaces to manage the `api`, `ui`, and `repl` packages.

```bash
# Install dependencies for all workspaces
npm install

# Build all workspaces
npm run build

# Start both API and UI development servers
npm run dev
```

### Workspace Structure

The workspace configuration is defined in [package-lock.json:11-15]():

```mermaid
graph TB
    Root["Root Workspace<br/>package-lock.json"]
    
    API["API Workspace<br/>./api/package.json"]
    UI["UI Workspace<br/>./ui/package.json"]
    REPL["REPL Workspace<br/>./repl/package.json"]
    
    Root --> API
    Root --> UI
    Root --> REPL
    
    APIScripts["API Scripts<br/>• dev: tsx watch<br/>• build: tsc & copy<br/>• generate:openapi"]
    
    UIScripts["UI Scripts<br/>• dev: Vite dev server<br/>• build: production build"]
    
    REPLScripts["REPL Scripts<br/>• start: Run script.ts"]
    
    API --> APIScripts
    UI --> UIScripts
    REPL --> REPLScripts
```

**Sources:** [package-lock.json:11-15](), [api/package.json:40-51](), [docs/DEVELOPMENT_SETUP.md:132-163]()

---

## NPM Script Reference

### API Workspace Scripts

Defined in [api/package.json:40-51]():

| Script | Command | Description |
|--------|---------|-------------|
| `dev` | `npm run prepare:recorder && tsx watch src/index.ts` | Start API with auto-restart and recorder build |
| `build` | `tsc && npm run copy:templates && npm run copy:fingerprint` | Compile TS and copy assets to `build/` |
| `prepare:recorder` | `cd extensions/recorder && npm install && npm run build` | Build the browser extension for session recording |
| `generate:openapi` | `tsx ./openapi/generate.ts` | Generate the OpenAPI specification |

### Root and UI Scripts

The root workspace uses `concurrently` to run both the API and UI development servers simultaneously [docs/DEVELOPMENT_SETUP.md:157]().

```mermaid
graph LR
    NpmDev["npm run dev"]
    Concurrently["concurrently"]
    
    APIDevCmd["npm run dev -w api"]
    UIDevCmd["npm run dev -w ui"]
    
    APIServer["Fastify API<br/>Port 3000<br/>tsx watch"]
    UIServer["Vite UI<br/>Port 5173<br/>HMR enabled"]
    
    NpmDev --> Concurrently
    Concurrently --> APIDevCmd
    Concurrently --> UIDevCmd
    APIDevCmd --> APIServer
    UIDevCmd --> UIServer
```

**Sources:** [api/package.json:40-51](), [docs/DEVELOPMENT_SETUP.md:144-163]()

---

## Chrome Executable Configuration

### Required Paths

Steel Browser requires a Chrome or Chromium executable. Developers must ensure the `CHROME_EXECUTABLE_PATH` environment variable points to a valid binary if it is not in the system PATH [docs/DEVELOPMENT_SETUP.md:224]().

| Platform | Common Paths |
|----------|-------------|
| Linux | `/usr/bin/google-chrome` |
| macOS | `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome` |
| Windows | `C:\Program Files\Google\Chrome\Application\chrome.exe` |

### Environment Variables

Configure these in a `.env` file at the root or within the `api` directory:

```bash
# Browser Configuration
CHROME_HEADLESS=false  # Set to true for headless mode
CHROME_EXECUTABLE_PATH=/usr/bin/google-chrome
ENABLE_CDP_LOGGING=true
ENABLE_VERBOSE_LOGGING=true

# Network
HOST=0.0.0.0
PORT=3000
CDP_REDIRECT_PORT=9223
```

**Sources:** [docs/DEVELOPMENT_SETUP.md:211-234](), [docs/TROUBLESHOOTING.md:50-58]()

---

## Hot Reload and Live Development

### API Server Auto-restart

The API uses `tsx watch` to monitor source files in `api/src/`. When a file change is detected, the process is restarted, reloading the Fastify server and re-initializing services like `CDPService` and `SessionService` [api/package.json:47]().

### Vite Hot Module Replacement (HMR)

The UI development server (Vite) provides instant HMR. It tracks changes in the `ui/src` directory and pushes updates to the browser via WebSockets without a full page refresh.

### Docker Volume Mounts

In `docker-compose.dev.yml`, the following mounts are critical for hot reloading:

| Source | Container Destination | Purpose |
|-------|--------|-------------|
| `./api` | `/app/api` | API Source & built assets |
| `./ui` | `/app/ui` | UI Source & Vite config |
| `./.cache` | `/app/.cache` | Persistent browser profiles |

**Sources:** [api/package.json:47](), [docs/DEVELOPMENT_SETUP.md:180-191](), [docs/TROUBLESHOOTING.md:197-199]()

---

## Debugging Setup

### Chrome DevTools Protocol Access

Steel Browser exposes a CDP redirect port (default `9223`) which proxies connections to the underlying Chromium instances [docs/DEVELOPMENT_SETUP.md:220]().

1. Start the API in dev mode: `npm run dev -w api`.
2. Open Chrome and navigate to `chrome://inspect`.
3. Configure "Discover network targets" to include `localhost:9223`.

### Node.js Debugging

To debug the API logic itself:

```bash
# Start API with inspector
node --inspect ./api/build/index.js
```

You can then attach VS Code or Chrome DevTools to the Node.js process (default port `9229`) [docs/TROUBLESHOOTING.md:219-227]().

### REPL Testing

The `repl` workspace provides a `script.ts` for quick prototyping against a running API instance [docs/DEVELOPMENT_SETUP.md:173-176]().

```bash
cd repl
npm start
```

**Sources:** [docs/DEVELOPMENT_SETUP.md:211-234](), [docs/TROUBLESHOOTING.md:203-227](), [docs/DEVELOPMENT_SETUP.md:173-176]()

---

## Building for Production

The build process involves compiling TypeScript and preparing static assets.

```bash
# Build API
npm run build -w api
```

The API build script [api/package.json:42]() performs:
1. `tsc`: Compiles TypeScript to the `build/` directory using settings in [api/tsconfig.json]().
2. `copy:templates`: Copies EJS templates to `build/templates/`.
3. `copy:fingerprint`: Copies the `fingerprint.js` script to `build/scripts/`.

In production mode, the API server can also serve the UI static files if `NODE_ENV` is set to `production` and the UI files exist in `ui/dist` [api/src/index.ts:25-30]().

**Sources:** [api/package.json:42-45](), [api/tsconfig.json:1-25](), [api/src/index.ts:25-30]()

---

# Page: Architecture Deep Dive

# Architecture Deep Dive

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [api/src/plugins/browser.ts](api/src/plugins/browser.ts)
- [api/src/services/cdp/cdp.service.ts](api/src/services/cdp/cdp.service.ts)
- [api/src/services/cdp/instrumentation/storage/in-memory-storage.ts](api/src/services/cdp/instrumentation/storage/in-memory-storage.ts)
- [api/src/services/cdp/instrumentation/storage/log-storage.interface.ts](api/src/services/cdp/instrumentation/storage/log-storage.interface.ts)
- [api/src/services/cdp/instrumentation/worker-events.ts](api/src/services/cdp/instrumentation/worker-events.ts)
- [api/src/services/cdp/plugins/core/base-plugin.ts](api/src/services/cdp/plugins/core/base-plugin.ts)
- [api/src/services/cdp/plugins/core/plugin-manager.ts](api/src/services/cdp/plugins/core/plugin-manager.ts)
- [api/src/services/session.service.ts](api/src/services/session.service.ts)
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- [docs/DEVELOPMENT_SETUP.md](docs/DEVELOPMENT_SETUP.md)
- [docs/README.md](docs/README.md)
- [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)

</details>



## Purpose and Scope

This document provides a detailed technical explanation of the Steel Browser service layer architecture, focusing on how services are structured, how dependencies are injected via Fastify plugins, the event-driven communication patterns, sophisticated error handling strategies, and resource lifecycle management. This is intended for developers contributing to the Steel Browser codebase or extending it with custom functionality.

For configuration validation details, see [Configuration Validation](#14.3). For initial setup instructions, see [Development Environment Setup](#14.1). For plugin development, see [BasePlugin & PluginManager](#9.1).

---

## Service Layer Architecture

### Core Services Overview

Steel Browser is built around three primary service classes that form the core business logic layer, operating beneath the HTTP controller layer and above the browser automation primitives.

**Core Services Architecture Diagram**

```mermaid
graph TB
    subgraph ControllerLayer["Controller Layer"]
        SessionsController["handleLaunchBrowserSession<br/>handleExitBrowserSession<br/>sessions.controller.ts"]
        ActionsController["handleScrape<br/>handleScreenshot<br/>actions.controller.ts"]
        FilesController["handleUploadFile<br/>handleDownloadFile<br/>files.controller.ts"]
    end
    
    subgraph CoreServices["Service Layer - Core Services"]
        SessionService["SessionService<br/>startSession()<br/>endSession()<br/>session.service.ts:58"]
        CDPService["CDPService<br/>launch()<br/>shutdown()<br/>cdp.service.ts:83"]
        FileService["FileService<br/>uploadFile()<br/>cleanupFiles()<br/>file.service.ts"]
        SeleniumService["SeleniumService<br/>launch()<br/>close()<br/>selenium.service.ts"]
    end
    
    subgraph SupportServices["Service Layer - Supporting Services"]
        ChromeContextService["ChromeContextService<br/>getSessionData()<br/>chrome-context.service.ts"]
        TimezoneFetcher["TimezoneFetcher<br/>getTimezone()<br/>timezone-fetcher.service.ts"]
        ProxyServer["ProxyServer<br/>listen()<br/>close()<br/>proxy.ts"]
    end
    
    subgraph PluginSystem["Plugin System"]
        PluginManager["PluginManager<br/>register()<br/>onBrowserLaunch()<br/>plugin-manager.ts:7"]
        BasePlugin["BasePlugin<br/>onBrowserLaunch()<br/>onPageCreated()<br/>base-plugin.ts:27"]
    end
    
    subgraph InstrumentationSystem["Instrumentation System"]
        TargetInstrumentationManager["TargetInstrumentationManager<br/>attach()<br/>detach()<br/>target-manager.ts"]
        BrowserLogger["BrowserLogger<br/>record()<br/>createInstrumentationLogger<br/>browser-logger.ts"]
        LogStorage["DuckDBStorage<br/>InMemoryStorage<br/>in-memory-storage.ts:14"]
    end
    
    SessionsController --> SessionService
    ActionsController --> SessionService
    FilesController --> FileService
    
    SessionService --> CDPService
    SessionService --> SeleniumService
    SessionService --> FileService
    SessionService --> TimezoneFetcher
    SessionService --> ProxyServer
    
    CDPService --> PluginManager
    CDPService --> TargetInstrumentationManager
    CDPService --> ChromeContextService
    CDPService --> FileService
    
    PluginManager --> BasePlugin
    
    TargetInstrumentationManager --> BrowserLogger
    BrowserLogger --> LogStorage
```

**Sources:** [api/src/services/cdp/cdp.service.ts:83-185](), [api/src/services/session.service.ts:58-91](), [docs/ARCHITECTURE.md:28-55]()

### Service Responsibilities

| Service | Primary Responsibility | Key Methods | Lifecycle |
|---------|----------------------|-------------|-----------|
| `CDPService` | Browser process orchestration, page management, CDP protocol communication | `launch()` [517]*, `shutdown()` [455]*, `createPage()` [441]* | Singleton per API server, manages browser instance [api/src/services/cdp/cdp.service.ts:83]() |
| `SessionService` | Session lifecycle, state tracking, proxy setup, session metadata | `startSession()` [93](), `endSession()` [245](), `resetSessionInfo()` [275]() | Singleton per API server, maintains session registry [api/src/services/session.service.ts:58]() |
| `FileService` | File storage, upload/download, automatic zip archiving | `uploadFile()`, `downloadFile()`, `cleanupFiles()` | Singleton managed by SessionService [api/src/services/session.service.ts:72]() |
| `SeleniumService` | WebDriver protocol compatibility for Selenium mode | `launch()`, `close()` | Created on-demand for Selenium sessions [api/src/services/session.service.ts:61]() |
| `PluginManager` | Plugin lifecycle hooks, plugin registration | `register()` [21](), `onBrowserLaunch()` [96]() | Owned by CDPService instance [api/src/services/cdp/cdp.service.ts:99]() |

\* *Line numbers refer to approximate locations in CDPService as seen in `docs/ARCHITECTURE.md`*

**Sources:** [api/src/services/cdp/cdp.service.ts:83-185](), [api/src/services/session.service.ts:58-91](), [api/src/services/cdp/plugins/core/plugin-manager.ts:7-217]()

### Service Communication Patterns

The services communicate through three primary patterns:

1. **Direct Method Calls**: `SessionService` calls `CDPService` methods directly for browser operations, such as `this.cdpService.launch()` [api/src/services/session.service.ts:228]().
2. **Event Emission**: `CDPService` extends `EventEmitter` to broadcast browser events [api/src/services/cdp/cdp.service.ts:83]().
3. **Plugin Hooks**: Plugins register with `PluginManager` to receive lifecycle notifications like `onBrowserLaunch` [api/src/services/cdp/plugins/core/plugin-manager.ts:96]().

**Session Creation Sequence Diagram**

```mermaid
sequenceDiagram
    participant Controller as "SessionsController"
    participant SessionSvc as "SessionService"
    participant ProxyFactory as "ProxyFactory"
    participant CDPSvc as "CDPService"
    participant PluginMgr as "PluginManager"
    
    Controller->>SessionSvc: startSession(options)
    SessionSvc->>SessionSvc: resetSessionInfo()<br/>[166]
    
    alt proxyUrl provided
        SessionSvc->>ProxyFactory: proxyFactory(proxyUrl)<br/>[209]
        ProxyFactory-->>SessionSvc: IProxyServer
        SessionSvc->>ProxyFactory: proxyServer.listen()<br/>[210]
    end
    
    SessionSvc->>CDPSvc: launch(browserLauncherOptions)<br/>[228]
    CDPSvc->>PluginMgr: onSessionStart(config)<br/>[54]*
    
    CDPSvc->>CDPSvc: Execute launchMutators
    
    CDPSvc->>CDPSvc: puppeteer.launch()
    
    CDPSvc->>PluginMgr: onBrowserLaunch(browser)<br/>[96]
    CDPSvc->>PluginMgr: onBrowserReady(config)<br/>[107]
    
    CDPSvc-->>SessionSvc: Browser instance
    SessionSvc-->>Controller: SessionDetails
```

\* *Line numbers for PluginManager refer to `api/src/services/cdp/plugins/core/plugin-manager.ts`*

**Sources:** [api/src/services/session.service.ts:93-243](), [api/src/services/cdp/cdp.service.ts:169-213](), [api/src/services/cdp/plugins/core/plugin-manager.ts:54-118]()

---

## Dependency Injection via Fastify Plugins

Steel Browser uses Fastify's plugin system as a lightweight dependency injection framework. Services are instantiated and registered as decorators on the Fastify instance.

### Plugin Registration Flow

```mermaid
graph TB
    steelBrowserPlugin["steelBrowserPlugin<br/>steel-browser-plugin.ts"]
    
    subgraph "Service Registration Plugins"
        browserInstancePlugin["browserInstancePlugin<br/>CDPService + storage<br/>api/src/plugins/browser.ts"]
        browserSessionPlugin["browserSessionPlugin<br/>SessionService"]
    end
    
    steelBrowserPlugin --> browserInstancePlugin
    browserInstancePlugin --> browserSessionPlugin
```

**Sources:** [api/src/plugins/browser.ts:24-75](), [docs/ARCHITECTURE.md:173-188]()

### Decorated Services and Hooks

The Fastify instance is decorated with several service instances and hook registration functions in `api/src/plugins/browser.ts`:

- `fastify.cdpService`: The singleton `CDPService` [api/src/plugins/browser.ts:57]().
- `fastify.registerCDPLaunchHook`: For adding custom launch logic [api/src/plugins/browser.ts:58-63]().
- `fastify.registerCDPShutdownHook`: For adding custom cleanup logic [api/src/plugins/browser.ts:64-69]().

The registration happens in sequence:
1. **Log Storage Initialization**: Initializes `DuckDBStorage` or `InMemoryStorage` [api/src/plugins/browser.ts:30-53]().
2. **CDPService Creation**: Instantiates `CDPService` with the storage [api/src/plugins/browser.ts:55]().
3. **Automatic Launch**: The browser is launched when Fastify starts listening [api/src/plugins/browser.ts:71-74]().

**Sources:** [api/src/plugins/browser.ts:24-75]()

---

## Event-Driven Architecture

### EventEmitter Pattern in CDPService

The `CDPService` extends Node.js `EventEmitter` to broadcast browser-related events [api/src/services/cdp/cdp.service.ts:83]().

**Instrumentation Event Flow**

The instrumentation system captures browser events (Console, Errors) and propagates them through the `BrowserLogger` [api/src/services/cdp/instrumentation/worker-events.ts:6-37]().

| Event Type | Source | Trigger | Destination |
|------------|--------|---------|-------------|
| `Console` | `CDPSession` | `Runtime.consoleAPICalled` | `BrowserLogger.record` [api/src/services/cdp/instrumentation/worker-events.ts:14-25]() |
| `PageError` | `CDPSession` | `Runtime.exceptionThrown` | `BrowserLogger.record` [api/src/services/cdp/instrumentation/worker-events.ts:27-36]() |
| `Log` | `BrowserLogger` | Any recorded event | `CDPService` emission [api/src/services/cdp/cdp.service.ts:181-183]() |

### Plugin Lifecycle Architecture

The `PluginManager` coordinates event distribution to all registered plugins:

```mermaid
graph LR
    subgraph CDP["CDP Service"]
        Launch["launch()"]
        CreatePage["createPage()"]
        Shutdown["shutdown()"]
    end
    
    subgraph PM["Plugin Manager"]
        PM_Launch["onBrowserLaunch()"]
        PM_Page["onPageCreated()"]
        PM_Shutdown["onShutdown()"]
    end
    
    subgraph Plugins["Plugins (BasePlugin)"]
        P1["Plugin A"]
        P2["Plugin B"]
    end
    
    Launch --> PM_Launch
    CreatePage --> PM_Page
    Shutdown --> PM_Shutdown
    
    PM_Launch --> P1
    PM_Launch --> P2
    PM_Page --> P1
    PM_Shutdown --> P2
```

**Sources:** [api/src/services/cdp/plugins/core/plugin-manager.ts:96-202](), [api/src/services/cdp/plugins/core/base-plugin.ts:43-54]()

---

## Error Handling Strategies

Steel Browser implements a tiered error handling system, distinguishing between critical operations and best-effort attempts.

### Categorized Error Types

Errors are categorized into specific types such as `BrowserProcessError`, `FingerprintError`, and `PluginError` [api/src/services/cdp/errors/launch-errors.ts]().

### Three-Tier Error Handling Functions

CDPService uses utility functions to manage execution risk:

| Function | Purpose | Location |
|----------|---------|----------|
| `executeCritical` | Operations that must succeed (e.g., Puppeteer launch) | [api/src/services/cdp/cdp.service.ts:80]() |
| `executeBestEffort` | Operations that should succeed but aren't fatal | [api/src/services/cdp/cdp.service.ts:80]() |
| `executeOptional` | Nice-to-have operations (e.g., instrumentation) | [api/src/services/cdp/cdp.service.ts:80]() |

**Sources:** [api/src/services/cdp/cdp.service.ts:80](), [api/src/services/cdp/errors/launch-errors.ts]()

---

## Resource Lifecycle Management

### Browser Instance Lifecycle

The browser instance is managed by `CDPService`, which handles setup, plugins, and instrumentation [api/src/services/cdp/cdp.service.ts:121-185]().

### Cleanup Patterns

Cleanup occurs at multiple levels to ensure no orphaned processes or files remain.

#### Browser Shutdown Sequence

When `shutdown()` is called, the system performs the following in order:
1. **Plugin Notification**: Calls `onBrowserClose` and `onShutdown` for all plugins [api/src/services/cdp/plugins/core/plugin-manager.ts:137-193]().
2. **Process Termination**: Closes the browser instance.
3. **Hook Execution**: Runs all registered `shutdownMutators` [api/src/services/cdp/cdp.service.ts:108]().

#### Session Cleanup Sequence

The `SessionService.endSession()` method handles the graceful exit of a session:
1. **Status Update**: Marks session as `released` [api/src/services/session.service.ts:247]().
2. **Proxy Shutdown**: Closes the `proxyServer` if one was used [api/src/services/session.service.ts:278]().
3. **Service Handover**: For CDP sessions, it calls `cdpService.endSession()` [api/src/services/session.service.ts:260]().
4. **Archiving**: Moves the session to `pastSessions` [api/src/services/session.service.ts:270]().

**Sources:** [api/src/services/session.service.ts:245-273](), [api/src/services/cdp/cdp.service.ts:455-503](), [api/src/services/cdp/plugins/core/plugin-manager.ts:137-216]()

### Memory Management Patterns

Steel Browser employs several patterns to prevent memory leaks:

| Pattern | Implementation | Purpose |
|---------|----------------|---------|
| **In-Memory Trimming** | `InMemoryStorage` slices events array at `maxEvents` [api/src/services/cdp/instrumentation/storage/in-memory-storage.ts:34-36]() | Prevents log storage from consuming all RAM |
| **Batch Flushing** | `DuckDBStorage` uses write buffers [api/src/plugins/browser.ts:41-43]() | Optimizes I/O and memory pressure |
| **Explicit Nullification** | `CDPService` nullifies `browserInstance` on shutdown | Ensures garbage collection of large browser objects |

**Sources:** [api/src/services/cdp/instrumentation/storage/in-memory-storage.ts:14-37](), [api/src/plugins/browser.ts:36-44]()

---

# Page: Configuration Validation

# Configuration Validation

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [api/.env.example](api/.env.example)
- [api/.prettierrc](api/.prettierrc)
- [api/src/env.ts](api/src/env.ts)
- [api/src/plugins/schemas.ts](api/src/plugins/schemas.ts)
- [api/src/routes.ts](api/src/routes.ts)
- [api/src/services/cdp/errors/launch-errors.ts](api/src/services/cdp/errors/launch-errors.ts)
- [api/src/services/cdp/utils/error-handlers.ts](api/src/services/cdp/utils/error-handlers.ts)
- [api/src/services/cdp/utils/validation.ts](api/src/services/cdp/utils/validation.ts)
- [repl/package.json](repl/package.json)
- [ui/package.json](ui/package.json)

</details>



This document covers the configuration validation system used to ensure browser launch parameters are valid and to determine when browser instances can be reused. Configuration validation occurs before browser launch and during session management to prevent runtime errors and optimize resource usage.

For information about the configuration interface being validated, see [api/src/types/index.js](). For environment variable validation, see [api/src/env.ts]().

## Purpose and Scope

Configuration validation serves three primary functions:

1.  **Pre-launch Validation** - Validates browser launch parameters before attempting to start a browser instance.
2.  **Timezone Resolution** - Asynchronously validates and resolves timezone configurations with timeout handling.
3.  **Configuration Comparison** - Determines if two configurations are similar enough to reuse an existing browser instance.

All validation logic is centralized in `api/src/services/cdp/utils/validation.ts`.

Sources: [api/src/services/cdp/utils/validation.ts:1-190](), [api/src/env.ts:1-84]()

## Validation Functions Overview

The system uses `zod` for environment-level validation and custom logic for runtime browser configurations.

```mermaid
graph TB
    subgraph "Validation Entry Points"
        LaunchReq["validateLaunchConfig()<br/>BrowserLauncherOptions"]
        TimezoneReq["validateTimezone()<br/>Promise&lt;string&gt;"]
        CompareReq["isSimilarConfig()<br/>current vs next config"]
        EnvReq["envSchema.parse()<br/>process.env"]
    end
    
    subgraph "Logic Entities"
        ValidateLaunch["validateLaunchConfig<br/>Line 31"]
        ValidateTZ["validateTimezone<br/>Line 72"]
        CompareSimilar["isSimilarConfig<br/>Line 114"]
        EnvSchema["envSchema<br/>Line 6"]
    end
    
    subgraph "Results & Errors"
        LaunchResult["throws ConfigurationError"]
        TZResult["returns resolved string"]
        CompareResult["returns boolean"]
        EnvResult["returns typed env object"]
    end
    
    LaunchReq --> ValidateLaunch
    TimezoneReq --> ValidateTZ
    CompareReq --> CompareSimilar
    EnvReq --> EnvSchema
    
    ValidateLaunch --> LaunchResult
    ValidateTZ --> TZResult
    CompareSimilar --> CompareResult
    EnvSchema --> EnvResult
    
    style ValidateLaunch fill:none
    style ValidateTZ fill:none
    style CompareSimilar fill:none
    style EnvSchema fill:none
```

Sources: [api/src/services/cdp/utils/validation.ts:31-190](), [api/src/env.ts:6-86]()

## validateLaunchConfig

The `validateLaunchConfig` function performs pre-launch validation of browser configuration parameters. This validation catches common configuration errors before attempting to launch a browser.

### Validation Rules

| Configuration Field | Validation Rule | Error Type |
| :--- | :--- | :--- |
| `dimensions.width` | Must be > 0 and ≤ 7680 | `ConfigurationError` (`DIMENSIONS`) |
| `dimensions.height` | Must be > 0 and ≤ 4320 | `ConfigurationError` (`DIMENSIONS`) |
| `options.proxyUrl` | Must be valid URL format | `ConfigurationError` (`PROXY_URL`) |

### Dimensions Validation

The function enforces a minimum dimension of 1 pixel and a maximum of 8K resolution (7680x4320) to prevent resource exhaustion or browser crashes.

```mermaid
graph LR
    Input["config.dimensions"]
    
    CheckExists{"dimensions<br/>exists?"}
    CheckPositive{"width > 0<br/>height > 0"}
    CheckMax{"width ≤ 7680<br/>height ≤ 4320"}
    
    Valid["Validation passes"]
    ErrorPositive["ConfigurationError:<br/>must be positive"]
    ErrorMax["ConfigurationError:<br/>unreasonably large"]
    
    Input --> CheckExists
    CheckExists -->|"null/undefined"| Valid
    CheckExists -->|"exists"| CheckPositive
    CheckPositive -->|"no"| ErrorPositive
    CheckPositive -->|"yes"| CheckMax
    CheckMax -->|"no"| ErrorMax
    CheckMax -->|"yes"| Valid
```

Sources: [api/src/services/cdp/utils/validation.ts:31-48]()

### Proxy URL Validation

Proxy URL validation uses the built-in `URL` constructor to verify format validity:

```typescript
if (config.options.proxyUrl) {
  try {
    new URL(config.options.proxyUrl);
  } catch {
    throw new ConfigurationError(
      `Invalid proxy URL format: ${config.options.proxyUrl}`,
      ConfigurationField.PROXY_URL,
      config.options.proxyUrl,
    );
  }
}
```

Sources: [api/src/services/cdp/utils/validation.ts:50-61]()

## validateTimezone

The `validateTimezone` function handles asynchronous timezone validation with timeout protection. Timezone resolution may involve external API calls, so this function implements a race mechanism to prevent hanging.

### Validation Flow

The function implements a race between the `timezonePromise` and a timeout (default 10000ms).

| Parameter | Default | Purpose |
| :--- | :--- | :--- |
| `timezonePromise` | (required) | Async timezone resolution |
| `timeoutMs` | 10000 | Maximum wait time |

After resolution, it validates the string using `Intl.DateTimeFormat`:

```typescript
try {
  Intl.DateTimeFormat(undefined, { timeZone: timezone });
  return timezone;
} catch (timezoneError) {
  throw new ConfigurationError(
    `Invalid timezone resolved: ${timezone}`,
    ConfigurationField.TIMEZONE,
    timezone,
  );
}
```

Sources: [api/src/services/cdp/utils/validation.ts:72-105]()

## isSimilarConfig

The `isSimilarConfig` function determines whether two browser launch configurations are similar enough to reuse an existing browser instance. This avoids the overhead of launching a new browser when differences are negligible.

### Configuration Normalization

Before comparison, the function normalizes values to handle defaults and array sorting:

*   **`normalizeArgs`**: Filters out falsy values and sorts alphabetically [api/src/services/cdp/utils/validation.ts:129-129]().
*   **`normalizeExt`**: Sorts extensions alphabetically [api/src/services/cdp/utils/validation.ts:130-130]().
*   **`extra` Handling**: Destructures to remove `session` and `streaming` properties which do not affect browser-level reuse [api/src/services/cdp/utils/validation.ts:162-171]().

### Comparison Logic

The function performs a deep equality check using `JSON.stringify` for objects and arrays, and strict equality for primitives. It also performs an asynchronous comparison for timezones using `comparePromiseValues` [api/src/services/cdp/utils/validation.ts:12-26]().

```typescript
return (
  currentHeadless === nextHeadless &&
  currentProxy === nextProxy &&
  currentUserAgent === nextUserAgent &&
  // ... other primitive checks
  JSON.stringify(currentArgs) === JSON.stringify(nextArgs) &&
  JSON.stringify(currentExtra) === JSON.stringify(nextExtra) &&
  (await timezoneComparisonPromise)
);
```

Sources: [api/src/services/cdp/utils/validation.ts:114-189]()

## Error Handling and Execution Utilities

The system provides utility functions in `api/src/services/cdp/utils/error-handlers.ts` to categorize operations by criticality.

| Function | Behavior | Use Case |
| :--- | :--- | :--- |
| `executeCritical` | Throws a categorized error on failure | Essential steps like browser launch |
| `executeOptional` | Logs warning but continues on failure | Non-essential cleanup or optimization |
| `executeBestEffort` | Silently logs on failure | Optional features or logging |

### Launch Error Types

Errors are categorized using `LaunchErrorType` to allow for intelligent recovery strategies:
*   `TIMEOUT`: Browser failed to start within limits.
*   `CONFIGURATION`: Invalid parameters provided.
*   `RESOURCE`: Missing binary or disk space.
*   `NETWORK`: Proxy or WebSocket binding failures.

Sources: [api/src/services/cdp/utils/error-handlers.ts:18-87](), [api/src/services/cdp/errors/launch-errors.ts:6-17]()

## Environment Validation

Environment variables are validated at startup using `zod`. This ensures the application does not start with invalid system paths or malformed configuration strings.

### Key Environment Schemas

| Variable | Type | Default | Transformation |
| :--- | :--- | :--- | :--- |
| `USE_SSL` | Boolean | `false` | Transforms `"true"`/`"1"` to `true` |
| `DEFAULT_HEADERS` | Object | `{}` | Parses JSON string to record |
| `CHROME_ARGS` | Array | `[]` | Splits space-separated string |
| `PORT` | String | `"3000"` | Default string port |

Sources: [api/src/env.ts:6-86]()

---

# Page: Creating Custom Plugins

# Creating Custom Plugins

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [api/src/plugins/browser-socket/handlers/cast.handler.ts](api/src/plugins/browser-socket/handlers/cast.handler.ts)
- [api/src/plugins/browser-socket/handlers/index.ts](api/src/plugins/browser-socket/handlers/index.ts)
- [api/src/services/cdp/cdp.service.ts](api/src/services/cdp/cdp.service.ts)
- [api/src/services/cdp/plugins/core/base-plugin.ts](api/src/services/cdp/plugins/core/base-plugin.ts)
- [api/src/services/cdp/plugins/core/plugin-manager.ts](api/src/services/cdp/plugins/core/plugin-manager.ts)
- [api/src/services/websocket-registry.service.ts](api/src/services/websocket-registry.service.ts)
- [api/src/steel-browser-plugin.ts](api/src/steel-browser-plugin.ts)
- [api/src/types/index.ts](api/src/types/index.ts)
- [api/src/types/websocket.ts](api/src/types/websocket.ts)
- [docs/PLUGIN_DEVELOPMENT.md](docs/PLUGIN_DEVELOPMENT.md)
- [ui/vite.config.ts](ui/vite.config.ts)

</details>



This document provides a step-by-step guide for developers who want to extend steel-browser's browser automation capabilities by creating custom plugins. Plugins allow you to hook into the browser lifecycle and execute custom logic at key points during browser sessions.

For architectural background on the plugin system, see [BasePlugin & PluginManager](#9.1). For information about built-in plugins already available, see [Built-in Plugins](#9.2).

## Overview

The plugin system in steel-browser is built around an event-driven architecture that allows you to extend browser automation functionality without modifying core services. Plugins extend the `BasePlugin` abstract class and implement lifecycle hooks that are called at specific points during browser and page lifecycles.

**Sources:** [api/src/services/cdp/plugins/core/base-plugin.ts:1-55](), [api/src/services/cdp/plugins/core/plugin-manager.ts:1-217]()

## Plugin Architecture

The following diagram shows how plugins integrate with the core `CDPService` and `PluginManager`:

```mermaid
graph TB
    CDPService["CDPService"]
    PluginManager["PluginManager"]
    BasePlugin1["BasePlugin<br/>(Custom Plugin 1)"]
    BasePlugin2["BasePlugin<br/>(Custom Plugin 2)"]
    BasePlugin3["BasePlugin<br/>(Custom Plugin 3)"]
    
    Browser["Browser<br/>(puppeteer-core)"]
    Page["Page<br/>(puppeteer-core)"]
    
    CDPService -->|"creates & owns"| PluginManager
    CDPService -->|"controls"| Browser
    Browser -->|"creates"| Page
    
    PluginManager -->|"register(plugin)"| BasePlugin1
    PluginManager -->|"register(plugin)"| BasePlugin2
    PluginManager -->|"register(plugin)"| BasePlugin3
    
    BasePlugin1 -->|"setService(cdpService)"| CDPService
    BasePlugin2 -->|"setService(cdpService)"| CDPService
    BasePlugin3 -->|"setService(cdpService)"| CDPService
    
    Browser -.->|"onBrowserLaunch(browser)"| PluginManager
    Browser -.->|"onBrowserClose(browser)"| PluginManager
    Page -.->|"onPageCreated(page)"| PluginManager
    Page -.->|"onPageNavigate(page)"| PluginManager
    Page -.->|"onPageUnload(page)"| PluginManager
    Page -.->|"onBeforePageClose(page)"| PluginManager
    
    PluginManager -.->|"triggers lifecycle hooks"| BasePlugin1
    PluginManager -.->|"triggers lifecycle hooks"| BasePlugin2
    PluginManager -.->|"triggers lifecycle hooks"| BasePlugin3
```

**Sources:** [api/src/services/cdp/plugins/core/plugin-manager.ts:7-16](), [api/src/services/cdp/plugins/core/base-plugin.ts:27-40]()

## BasePlugin Class

All custom plugins must extend the `BasePlugin` abstract class. The class provides:

| Member | Type | Description |
|--------|------|-------------|
| `name` | `string` | Unique identifier for the plugin |
| `options` | `PluginOptions` | Configuration options passed to constructor |
| `cdpService` | `CDPService \| null` | Reference to `CDPService` (set by `PluginManager`) |

**Constructor Signature:**
```typescript
constructor(options: PluginOptions)
```

The `PluginOptions` interface requires a `name` property and accepts arbitrary additional properties:

```typescript
export interface PluginOptions {
  name: string;
  [key: string]: any;
}
```

**Sources:** [api/src/services/cdp/plugins/core/base-plugin.ts:22-36]()

## Lifecycle Hooks

The `BasePlugin` class defines lifecycle hooks that your plugin can override. All hooks are optional and have default no-op implementations. The following table describes when each hook is called:

| Hook Method | Parameters | When Called | Use Cases |
|-------------|-----------|-------------|-----------|
| `onSessionStart` | `sessionConfig: BrowserLauncherOptions` | Before browser launch/reuse | Pre-launch configuration changes |
| `onBrowserLaunch` | `browser: Browser` | After browser process starts | Initialize browser-level resources |
| `onBrowserReady` | `context: BrowserLauncherOptions` | After browser is fully initialized | Access final configuration |
| `onPageCreated` | `page: Page` | When any page/tab is created | Inject scripts, set up page-level event listeners |
| `onPageNavigate` | `page: Page` | Before page navigates to new URL | Pre-navigation setup |
| `onPageUnload` | `page: Page` | Before page unloads | Capture state before navigation away |
| `onBeforePageClose` | `page: Page` | Before page closes | Save page data, cleanup resources |
| `onBrowserClose` | `browser: Browser` | Before browser process closes | Cleanup browser-level resources |
| `onBeforeSessionEnd` | `sessionConfig: BrowserLauncherOptions` | Before shutdown begins | Final data capture |
| `onSessionEnd` | `sessionConfig: BrowserLauncherOptions` | After all teardown is complete | Save session summary, finalize logs |
| `onShutdown` | `reason: ShutdownReason` | During service shutdown | Global cleanup based on `ShutdownReason` |

**Hook Execution Flow:**

```mermaid
sequenceDiagram
    participant CDPService
    participant PluginManager
    participant Plugin1
    participant Plugin2
    participant Browser
    
    CDPService->>PluginManager: onSessionStart(config)
    PluginManager->>Plugin1: onSessionStart(config)
    PluginManager->>Plugin2: onSessionStart(config)

    CDPService->>Browser: launch()
    CDPService->>PluginManager: onBrowserLaunch(browser)
    PluginManager->>Plugin1: onBrowserLaunch(browser)
    PluginManager->>Plugin2: onBrowserLaunch(browser)
    
    CDPService->>PluginManager: onBrowserReady(context)
    PluginManager->>Plugin1: onBrowserReady(context)
    PluginManager->>Plugin2: onBrowserReady(context)
    
    Browser->>Browser: new Page created
    CDPService->>PluginManager: onPageCreated(page)
    PluginManager->>Plugin1: onPageCreated(page)
    PluginManager->>Plugin2: onPageCreated(page)
    
    Browser->>Browser: page.goto()
    CDPService->>PluginManager: onPageNavigate(page)
    PluginManager->>Plugin1: onPageNavigate(page)
    PluginManager->>Plugin2: onPageNavigate(page)
    
    Browser->>Browser: page.close()
    CDPService->>PluginManager: onBeforePageClose(page)
    PluginManager->>Plugin1: onBeforePageClose(page)
    PluginManager->>Plugin2: onBeforePageClose(page)
    
    CDPService->>Browser: close()
    CDPService->>PluginManager: onBrowserClose(browser)
    PluginManager->>Plugin1: onBrowserClose(browser)
    PluginManager->>Plugin2: onBrowserClose(browser)
    
    CDPService->>PluginManager: onSessionEnd(config)
    PluginManager->>Plugin1: onSessionEnd(config)
    PluginManager->>Plugin2: onSessionEnd(config)
```

All hooks return `Promise<void>` or `void`, and the `PluginManager` executes all plugins' hooks in parallel using `Promise.all()`.

**Sources:** [api/src/services/cdp/plugins/core/base-plugin.ts:43-54](), [api/src/services/cdp/plugins/core/plugin-manager.ts:54-216]()

## Creating a Custom Plugin: Step-by-Step

### Step 1: Create Plugin Class

Create a new TypeScript file for your plugin and extend `BasePlugin`:

```typescript
// Example: custom-analytics-plugin.ts
import { BasePlugin, PluginOptions } from "./base-plugin.js";
import { Browser, Page } from "puppeteer-core";

interface AnalyticsPluginOptions extends PluginOptions {
  trackingId: string;
  endpoint: string;
}

export class AnalyticsPlugin extends BasePlugin {
  private trackingId: string;
  private endpoint: string;
  private pageViews: number = 0;

  constructor(options: AnalyticsPluginOptions) {
    super(options);
    this.trackingId = options.trackingId;
    this.endpoint = options.endpoint;
  }
}
```

**Key Points:**
- Extend `BasePlugin` from [api/src/services/cdp/plugins/core/base-plugin.ts:27]()
- Create custom options interface extending `PluginOptions`
- Call `super(options)` in constructor to initialize base properties

### Step 2: Implement Lifecycle Hooks

Override the lifecycle hooks you need. Each hook can be `async` if it performs asynchronous operations:

```typescript
export class AnalyticsPlugin extends BasePlugin {
  // ... constructor and properties ...

  public async onBrowserLaunch(browser: Browser): Promise<void> {
    console.log(`[${this.name}] Browser launched with tracking ID: ${this.trackingId}`);
  }

  public async onPageCreated(page: Page): Promise<void> {
    // Inject analytics script into page
    await page.evaluateOnNewDocument((trackingId) => {
      (window as any).__analytics = { trackingId };
    }, this.trackingId);
  }

  public async onPageNavigate(page: Page): Promise<void> {
    this.pageViews++;
    await this.sendEvent('pageview', { url: page.url() });
  }

  public async onSessionEnd(): Promise<void> {
    await this.sendEvent('session_end', { totalPageViews: this.pageViews });
  }

  private async sendEvent(eventType: string, data: any): Promise<void> {
    // Implementation for sending event
  }
}
```

**Sources:** [api/src/services/cdp/plugins/core/base-plugin.ts:43-54]()

### Step 3: Access CDPService

If your plugin needs access to the `CDPService`, use the `cdpService` property (set by `PluginManager`):

```typescript
export class AdvancedPlugin extends BasePlugin {
  public async onPageCreated(page: Page): Promise<void> {
    if (this.cdpService) {
      const browser = this.cdpService.getBrowserInstance();
      // Access CDPService methods...
    }
  }
}
```

**Sources:** [api/src/services/cdp/plugins/core/base-plugin.ts:30-40](), [api/src/services/cdp/cdp.service.ts:205]()

## Registering Your Plugin

### Registration with PluginManager

Plugins are registered with the `PluginManager` instance owned by `CDPService`.

```mermaid
graph LR
    PluginInstance["new CustomPlugin(options)"]
    PluginManager["pluginManager.register()"]
    SetService["plugin.setService(cdpService)"]
    PluginsMap["plugins Map<string, BasePlugin>"]
    
    PluginInstance -->|"plugin instance"| PluginManager
    PluginManager -->|"calls"| SetService
    SetService -->|"stores in"| PluginsMap
```

The `PluginManager.register()` method:
1. Checks if plugin name already exists (logs warning if duplicate).
2. Calls `plugin.setService(this.service)` to inject `CDPService` reference.
3. Stores plugin in internal `Map<string, BasePlugin>`.

**Sources:** [api/src/services/cdp/plugins/core/plugin-manager.ts:21-29]()

### Example Registration

```typescript
// Inside CDPService or during app setup
const analyticsPlugin = new AnalyticsPlugin({
  name: 'analytics',
  trackingId: 'UA-12345',
  endpoint: 'https://api.analytics.com'
});

cdpService.pluginManager.register(analyticsPlugin);
```

## Error Handling

The `PluginManager` wraps all plugin lifecycle hook calls in try-catch blocks to prevent plugin errors from crashing the browser automation:

```mermaid
graph TD
    PluginManager["PluginManager lifecycle method"]
    GetPlugins["Get all registered plugins"]
    CreatePromises["Create Promise.all() for all plugins"]
    TryCatch["Try-catch wrapper per plugin"]
    PluginHook["plugin.onXXX() call"]
    CatchError["Catch error"]
    LogError["logger.error()"]
    ContinueOthers["Other plugins continue"]
    
    PluginManager --> GetPlugins
    GetPlugins --> CreatePromises
    CreatePromises --> TryCatch
    TryCatch --> PluginHook
    PluginHook -->|"success"| ContinueOthers
    PluginHook -->|"error"| CatchError
    CatchError --> LogError
    LogError --> ContinueOthers
```

Example implementation from `PluginManager`:
[api/src/services/cdp/plugins/core/plugin-manager.ts:123-132]()
```typescript
  public async onPageCreated(page: Page): Promise<void> {
    const promises = Array.from(this.plugins.values()).map(async (plugin) => {
      try {
        await plugin.onPageCreated(page);
      } catch (error) {
        this.logger.error(`Error in plugin ${plugin.name}.onPageCreated: ${error}`);
      }
    });
    await Promise.all(promises);
  }
```

**Sources:** [api/src/services/cdp/plugins/core/plugin-manager.ts:54-216]()

## Unregistering and Retrieval

Plugins can be managed dynamically:

- **Unregister**: `pluginManager.unregister('pluginName')` removes the plugin. [api/src/services/cdp/plugins/core/plugin-manager.ts:34-42]()
- **Retrieval**: `pluginManager.getPlugin<T>('pluginName')` retrieves a registered instance. [api/src/services/cdp/plugins/core/plugin-manager.ts:47-49]()

## Shutdown Reasons

When `onShutdown` is called, it receives a `ShutdownReason` enum value to help the plugin decide what cleanup to perform:

| Reason | Description |
|--------|-------------|
| `SESSION_END` | Normal graceful session termination |
| `SECURITY_VIOLATION` | Violation detected (e.g. `file://` access) |
| `RELAUNCH` | Closing instance before a new launch |
| `LAUNCH_FAILURE` | Cleanup after a failed launch attempt |
| `MODE_SWITCH` | Switching between CDP and Selenium |

**Sources:** [api/src/services/cdp/plugins/core/base-plugin.ts:9-20]()

---

# Page: Troubleshooting

# Troubleshooting

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Dockerfile](Dockerfile)
- [README.md](README.md)
- [api/.prettierrc](api/.prettierrc)
- [api/src/services/cdp/errors/launch-errors.ts](api/src/services/cdp/errors/launch-errors.ts)
- [api/src/services/cdp/utils/error-handlers.ts](api/src/services/cdp/utils/error-handlers.ts)
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- [docs/DEVELOPMENT_SETUP.md](docs/DEVELOPMENT_SETUP.md)
- [docs/README.md](docs/README.md)
- [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)
- [images/star_img.png](images/star_img.png)
- [render.yaml](render.yaml)

</details>



This page provides solutions for common issues encountered when using Steel Browser, along with debugging techniques to help diagnose and resolve problems.

## Error Handling Architecture

Steel Browser implements a structured error handling system with categorized error types and automatic retries. Understanding this system helps diagnose issues more effectively.

### Error Categorization System

The `CDPService` and associated utilities categorize launch failures into specific types defined in [api/src/services/cdp/errors/launch-errors.ts:6-17](). Each error type inherits from `BaseLaunchError` [api/src/services/cdp/errors/launch-errors.ts:77-100](), which includes an `isRetryable` flag.

| Error Type | Retryable | Common Causes |
|------------|-----------|---------------|
| `TIMEOUT` | Yes | Browser launch exceeds the 30s timeout [api/src/services/cdp/errors/launch-errors.ts:106-118]() |
| `CONFIGURATION` | No | Invalid dimensions, timezone, or proxy URL [api/src/services/cdp/errors/launch-errors.ts:124-142]() |
| `RESOURCE` | Varies | Missing Chrome binary, extension loading failures [api/src/services/cdp/errors/launch-errors.ts:148-163]() |
| `SYSTEM` | Yes | File access or OS-level operation failures [api/src/services/cdp/errors/launch-errors.ts:169-182]() |
| `NETWORK` | Yes | Port binding or WebSocket setup failures [api/src/services/cdp/errors/launch-errors.ts:188-200]() |
| `BROWSER_PROCESS` | Yes | Process crashes during launch or target setup [api/src/services/cdp/errors/launch-errors.ts:267-281]() |
| `FINGERPRINT` | Yes | Failures during fingerprint generation or injection [api/src/services/cdp/errors/launch-errors.ts:206-218]() |

Sources: [api/src/services/cdp/errors/launch-errors.ts:6-281]()

### Execution Wrappers

The codebase uses specific wrappers to handle errors based on their criticality:

*   **`executeCritical`**: Executes operations that MUST succeed. Throws categorized errors on failure [api/src/services/cdp/utils/error-handlers.ts:18-27]().
*   **`executeOptional`**: Logs a warning but continues execution if the operation fails [api/src/services/cdp/utils/error-handlers.ts:46-59]().
*   **`executeBestEffort`**: Silently logs debug info and continues on failure [api/src/services/cdp/utils/error-handlers.ts:76-87]().

Sources: [api/src/services/cdp/utils/error-handlers.ts:1-88]()

## Common Issues & Solutions

### 1. Browser Launch Failures

#### Symptoms
*   "Failed to launch browser" errors in logs.
*   Chrome executable not found.
*   Permission denied errors.

#### Solutions
**Verify Chrome Path**: Ensure `CHROME_EXECUTABLE_PATH` is set correctly for your OS [README.md:148-155]().
*   **Linux**: `/usr/bin/google-chrome`
*   **MacOS**: `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome`
*   **Windows**: `C:\Program Files\Google\Chrome\Application\chrome.exe`

**Linux Dependencies**: If running on Linux, ensure system dependencies for Chromium are installed [docs/TROUBLESHOOTING.md:65-77]().

```mermaid
graph TD
    subgraph "Code Entity Space"
        B_UTIL["api/src/utils/browser.ts"]
        CDP_S["api/src/services/cdp/cdp.service.ts"]
        ERR_H["api/src/services/cdp/utils/error-handlers.ts"]
    end

    subgraph "Natural Language Space"
        START["Request Launch"]
        FIND["Find Chrome Path"]
        EXEC["Spawn Process"]
        FAIL["Launch Error"]
    end

    START --> CDP_S
    CDP_S -- "calls" --> B_UTIL
    B_UTIL -- "checks env" --> FIND
    CDP_S -- "uses" --> ERR_H
    ERR_H -- "wraps" --> EXEC
    EXEC -- "throws" --> FAIL
```
Sources: [README.md:134-155](), [docs/TROUBLESHOOTING.md:41-87](), [api/src/services/cdp/utils/error-handlers.ts:18-27]()

### 2. Docker & Container Issues

#### Symptoms
*   Container fails to start or crashes immediately.
*   "Out of memory" errors in container logs.

#### Solutions
*   **Memory Limits**: Increase Node.js memory if sessions crash [docs/TROUBLESHOOTING.md:122-123]().
*   **Platform Flags**: For Mac Silicon (M1/M2/M3) users, use `DOCKER_DEFAULT_PLATFORM=linux/arm64` when running `docker compose` [README.md:104-106]().
*   **Zombie Processes**: The entrypoint script `api/entrypoint.sh` is designed to handle process reaping; ensure it is being used [Dockerfile:125]().

Sources: [README.md:104-106](), [docs/TROUBLESHOOTING.md:112-132](), [Dockerfile:118-125]()

### 3. Network & Proxy Issues

#### Symptoms
*   Cannot reach external websites.
*   Proxy authentication failures.

#### Solutions
*   **Proxy Config**: Set `PROXY_URL` with the format `http://username:password@host:port` [docs/TROUBLESHOOTING.md:143-145]().
*   **Health Check**: Use the health endpoint to verify the API is reachable: `curl http://localhost:3000/v1/health` [docs/TROUBLESHOOTING.md:11]().

Sources: [docs/TROUBLESHOOTING.md:133-152](), [render.yaml:6]()

## Debugging Techniques

### Enabling Verbose Logs
To diagnose deep issues within the CDP or browser process, set the following environment variables:
*   `ENABLE_VERBOSE_LOGGING=true` [docs/TROUBLESHOOTING.md:208]()
*   `ENABLE_CDP_LOGGING=true` [docs/TROUBLESHOOTING.md:209]()
*   `DEBUG_CHROME_PROCESS=true` [docs/TROUBLESHOOTING.md:236]()

### System Diagnostics
Use these commands to inspect the state of the host or container:

| Command | Purpose |
|---------|---------|
| `ps aux \| grep chrome` | Check for orphaned Chrome processes [docs/TROUBLESHOOTING.md:308]() |
| `lsof -i :3000` | Check if the API port is occupied [docs/TROUBLESHOOTING.md:100]() |
| `df -h` | Check for disk space issues (logs/cache) [docs/TROUBLESHOOTING.md:169]() |

```mermaid
flowchart TD
    subgraph "System State"
        PROC["OS Processes"]
        NET["Network Ports"]
        DISK["Disk Storage"]
    end

    subgraph "Steel Entities"
        CDP["CDPService"]
        SESS["SessionService"]
        FILE["FileService"]
    end

    CDP -- "manages" --> PROC
    SESS -- "binds" --> NET
    FILE -- "writes" --> DISK

    DIAG["Troubleshooting Guide"]
    DIAG -- "recommends" --> PS["ps aux"]
    DIAG -- "recommends" --> LSOF["lsof"]
    DIAG -- "recommends" --> DF["df -h"]

    PS -.-> PROC
    LSOF -.-> NET
    DF -.-> DISK
```
Sources: [docs/TROUBLESHOOTING.md:89-111](), [docs/TROUBLESHOOTING.md:154-176](), [docs/TROUBLESHOOTING.md:301-311]()

## Log Analysis Patterns

When reviewing logs, look for these specific patterns to identify the source of failure:

*   **`[CDPService] ... - continuing with launch`**: Indicates an error was caught by `executeOptional`. The launch will likely succeed, but a specific feature (like a plugin or cleanup) failed [api/src/services/cdp/utils/error-handlers.ts:56]().
*   **`Browser process error (launch_failed)`**: Indicates the binary failed to execute. Check `CHROME_PATH` [api/src/services/cdp/errors/launch-errors.ts:21]().
*   **`Network error during websocket setup`**: Indicates the browser started but the API cannot connect to its debugging port [api/src/services/cdp/errors/launch-errors.ts:59]().

Sources: [api/src/services/cdp/utils/error-handlers.ts:46-59](), [api/src/services/cdp/errors/launch-errors.ts:19-62]()

---

# Page: Glossary

# Glossary

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Dockerfile](Dockerfile)
- [README.md](README.md)
- [api/.env.example](api/.env.example)
- [api/package.json](api/package.json)
- [api/src/env.ts](api/src/env.ts)
- [api/src/modules/actions/actions.controller.ts](api/src/modules/actions/actions.controller.ts)
- [api/src/modules/actions/actions.routes.ts](api/src/modules/actions/actions.routes.ts)
- [api/src/modules/actions/actions.schema.ts](api/src/modules/actions/actions.schema.ts)
- [api/src/plugins/schemas.ts](api/src/plugins/schemas.ts)
- [api/src/routes.ts](api/src/routes.ts)
- [api/src/services/cdp/cdp.service.ts](api/src/services/cdp/cdp.service.ts)
- [api/src/services/cdp/plugins/core/base-plugin.ts](api/src/services/cdp/plugins/core/base-plugin.ts)
- [api/src/services/cdp/plugins/core/plugin-manager.ts](api/src/services/cdp/plugins/core/plugin-manager.ts)
- [api/src/services/selenium.service.ts](api/src/services/selenium.service.ts)
- [api/src/services/session.service.ts](api/src/services/session.service.ts)
- [api/src/utils/passthough-proxy.ts](api/src/utils/passthough-proxy.ts)
- [api/src/utils/proxy.ts](api/src/utils/proxy.ts)
- [images/star_img.png](images/star_img.png)
- [package-lock.json](package-lock.json)
- [render.yaml](render.yaml)

</details>



This glossary defines codebase-specific terms, abbreviations, and domain concepts used within the Steel Browser project. It serves as a technical reference for engineers to map natural language concepts to their respective implementations.

## Core Domain Concepts

### CDP (Chrome DevTools Protocol)
The primary protocol used by Steel to communicate with and control Chromium-based browsers. Unlike higher-level automation frameworks, Steel interacts directly with CDP to provide granular control over network interception, console logs, and target management.
*   **Implementation**: Managed via `CDPService`.
*   **Key Class**: `CDPService` [api/src/services/cdp/cdp.service.ts:83-83]()
*   **Data Flow**: The service maintains a `browserInstance` [api/src/services/cdp/cdp.service.ts:87-87]() and handles lifecycle events like `onBrowserLaunch` and `onPageCreated`.

### Session
A logical grouping of a browser instance (or context), its associated state (cookies, storage), and infrastructure (proxies). Sessions in Steel are designed to be long-lived or ephemeral depending on the `keepAlive` configuration.
*   **Implementation**: Tracked by `SessionService`.
*   **Key Type**: `SessionDetails` [api/src/modules/sessions/sessions.schema.js:9-9]()
*   **Management**: `SessionService` maintains an `activeSession` and a history of `pastSessions` [api/src/services/session.service.ts:66-67]().

### Fingerprinting
The process of generating and injecting browser attributes (User Agent, WebGL vendor, screen dimensions, etc.) to make the automated browser appear as a legitimate user device.
*   **Tools**: Uses `fingerprint-generator` and `fingerprint-injector` [api/src/services/cdp/cdp.service.ts:4-9]().
*   **Injection**: Handled during the browser launch sequence in `CDPService`.

### Proxy Chain
The mechanism where Steel acts as a local proxy server (`ProxyServer`) that forwards traffic to an upstream provider. This allows Steel to intercept requests for ad-blocking and bandwidth optimization before they leave the local environment.
*   **Implementation**: `ProxyServer` [api/src/utils/proxy.ts:15-15]().
*   **Bypass**: Internal traffic (e.g., to the API itself) is bypassed via `PROXY_INTERNAL_BYPASS` [api/src/utils/proxy.ts:31-37]().

---

## System Architecture Mapping

The following diagram illustrates how natural language concepts map to specific classes and services within the codebase.

**Concept to Code Entity Mapping**
```mermaid
graph TD
    subgraph "Natural Language Space"
        A["Browser Instance"]
        B["User State"]
        C["Network Gateway"]
        D["Automation Script"]
    end

    subgraph "Code Entity Space"
        A1["CDPService"]
        B1["ChromeContextService"]
        C1["ProxyServer"]
        D1["BasePlugin"]
    end

    A --- A1
    B --- B1
    C --- C1
    D --- D1

    A1 -->|manages| B1
    A1 -->|uses| C1
    A1 -->|executes| D1
```
**Sources**: [api/src/services/cdp/cdp.service.ts:83-104](), [api/src/services/session.service.ts:58-80](), [api/src/utils/proxy.ts:15-22]()

---

## Technical Terminology

| Term | Definition | Code Pointer |
| :--- | :--- | :--- |
| **CDP Redirect Port** | The port used to expose the browser's remote debugging interface. | `CDP_REDIRECT_PORT` [api/src/env.ts:18-18]() |
| **Primary Page** | The main tab of a browser session, often reused for quick actions like scraping. | `this.primaryPage` [api/src/services/cdp/cdp.service.ts:93-93]() |
| **Plugin Manager** | Orchestrates the lifecycle hooks (onPageCreated, onShutdown) for all registered plugins. | `PluginManager` [api/src/services/cdp/plugins/core/plugin-manager.ts:7-7]() |
| **Stealth** | Features intended to bypass bot detection, including fingerprint injection and header manipulation. | `Anti-Detection Features` [README.md:55-55]() |
| **Scrape Format** | The output format requested for a web page (HTML, Markdown, or Readability). | `ScrapeFormat` [api/src/modules/actions/actions.controller.ts:5-5]() |
| **Target Instrumentation** | The system for capturing and logging browser-level events (logs, network, console). | `TargetInstrumentationManager` [api/src/services/cdp/cdp.service.ts:75-75]() |

---

## Session Lifecycle Data Flow

The following diagram shows the transition of a session from request to active state, highlighting the interaction between services.

**Session Initialization Flow**
```mermaid
sequenceDiagram
    participant API as "sessions.controller"
    participant SS as "SessionService"
    participant CDP as "CDPService"
    participant PX as "ProxyServer"

    API->>SS: startSession(options)
    activate SS
    SS->>PX: new ProxyServer(proxyUrl)
    SS->>PX: listen()
    SS->>CDP: launch(browserLauncherOptions)
    activate CDP
    CDP->>CDP: getChromeExecutablePath()
    CDP->>CDP: injectFingerprint()
    CDP-->>SS: Browser Instance Ready
    deactivate CDP
    SS-->>API: SessionDetails
    deactivate SS
```
**Sources**: [api/src/services/session.service.ts:119-175](), [api/src/services/cdp/cdp.service.ts:130-167](), [api/src/utils/proxy.ts:65-69]()

---

## Environment & Infrastructure

*   **`CHROME_EXECUTABLE_PATH`**: The absolute path to the Google Chrome or Chromium binary. If not provided, the system attempts to auto-detect it based on the OS [api/src/utils/browser.ts:130-155]().
*   **`USER_DATA_DIR`**: The directory where Chrome stores profile data (cookies, cache). Steel can persist this directory to maintain state across sessions [api/src/services/session.service.ts:176-180]().
*   **`OptimizeBandwidth`**: A configuration flag that triggers the blocking of images, media, and stylesheets to reduce data usage [api/src/services/session.service.ts:194-204]().
*   **`ShutdownReason`**: An enumeration used by the `PluginManager` to inform plugins why a browser is closing (e.g., `SECURITY_VIOLATION`, `SESSION_END`) [api/src/services/cdp/plugins/core/base-plugin.ts:9-20]().

**Sources**: [api/src/env.ts:27-32](), [api/src/services/session.service.ts:176-204](), [api/src/services/cdp/plugins/core/base-plugin.ts:9-20]()