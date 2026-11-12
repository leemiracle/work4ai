<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/aisheets · page 4 Architecture · fetched 2026-10-26 -->

# Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Dockerfile](Dockerfile)
- [package.json](package.json)
- [pnpm-lock.yaml](pnpm-lock.yaml)
- [src/routes/index.tsx](src/routes/index.tsx)
- [src/routes/layout.tsx](src/routes/layout.tsx)
- [src/state/session.ts](src/state/session.ts)

</details>



This document provides a technical overview of AI Sheets' overall system architecture, covering the frontend/backend separation, request handling patterns, and core design principles. For detailed information about frontend components and state management, see [Frontend Architecture](#4.1). For backend services, API endpoints, and deployment details, see [Backend Architecture](#4.2).

## System Overview

AI Sheets follows a modern full-stack architecture built on Qwik and Express.js, designed as a no-code AI-powered dataset creation and enrichment platform. The system employs a multi-database strategy and integrates deeply with the Hugging Face ecosystem for AI model access and inference.

### High-Level Architecture

```mermaid
graph TB
    subgraph "Client Layer"
        Browser["Browser"]
        QwikApp["Qwik Application"]
    end
    
    subgraph "Server Layer"
        ExpressServer["Express Server"]
        QwikCity["Qwik City SSR"]
        SessionMgmt["Session Management"]
    end
    
    subgraph "Application Layer"
        Routes["Route Handlers"]
        UseCases["Use Cases"]
        Services["Service Layer"]
    end
    
    subgraph "Data Layer"
        SQLite[("SQLite DB")]
        DuckDB[("DuckDB")]
        LanceDB[("LanceDB")]
        FileSystem["File System"]
    end
    
    subgraph "External Integration"
        HuggingFace["Hugging Face Hub"]
        WebSearch["Web Search API"]
        OAuth["OAuth Providers"]
    end
    
    Browser --> QwikApp
    QwikApp --> ExpressServer
    ExpressServer --> QwikCity
    ExpressServer --> SessionMgmt
    
    QwikCity --> Routes
    Routes --> UseCases
    UseCases --> Services
    
    Services --> SQLite
    Services --> DuckDB  
    Services --> LanceDB
    Services --> FileSystem
    
    Services --> HuggingFace
    Services --> WebSearch
    SessionMgmt --> OAuth
```

Sources: [package.json:1-105](), [src/routes/layout.tsx:1-29](), [Dockerfile:1-61]()

## Request Flow Architecture

The system implements a hybrid SSR/SPA architecture where Qwik handles both server-side rendering and client-side interactivity through a unified request pipeline.

```mermaid
sequenceDiagram
    participant Client as "Browser Client"
    participant QwikApp as "Qwik Application"  
    participant Layout as "layout.tsx"
    participant Session as "useServerSession"
    participant Routes as "Route Handlers"
    participant Services as "Service Layer"
    participant DB as "Database Layer"
    
    Client->>QwikApp: "HTTP Request"
    QwikApp->>Layout: "onGet handler"
    Layout->>Session: "checkSession(event)"
    
    alt Session Valid
        Session-->>Layout: "Session object"
        Layout->>Routes: "Continue to route"
        Routes->>Services: "Business logic"
        Services->>DB: "Data operations"
        DB-->>Services: "Query results"
        Services-->>Routes: "Processed data"
        Routes-->>QwikApp: "Response data"
    else Session Invalid
        Session-->>Layout: "throw error"
        Layout->>Client: "redirect(302, '/')"
    end
    
    QwikApp-->>Client: "Rendered page/JSON"
```

Sources: [src/routes/layout.tsx:8-28](), [src/state/session.ts:14-26](), [src/routes/index.tsx:3-7]()

## Core Architectural Patterns

### 1. Universal JavaScript Architecture

The application uses Qwik's universal JavaScript approach where the same codebase runs on both client and server, enabling:

- **Server-Side Rendering (SSR)**: Initial page loads are rendered on the server
- **Progressive Hydration**: Client-side interactivity is added incrementally  
- **Resumable Applications**: State is serialized and resumed without re-execution

```mermaid
graph LR
    subgraph "Universal Codebase"
        SharedComponents["Shared Components"]
        SharedState["Shared State"]
        SharedTypes["Shared Types"]
    end
    
    subgraph "Server Context"
        SSREngine["Qwik City SSR"]
        ServerSession["useServerSession"]
        RouteHandlers["onGet/onPost handlers"]
    end
    
    subgraph "Client Context"  
        ClientHydration["Progressive Hydration"]
        ClientState["Client State Management"]
        UserInteractions["User Interactions"]
    end
    
    SharedComponents --> SSREngine
    SharedComponents --> ClientHydration
    SharedState --> ServerSession
    SharedState --> ClientState
    RouteHandlers --> SSREngine
    UserInteractions --> ClientHydration
```

Sources: [package.json:38-39](), [src/routes/layout.tsx:19-28](), [src/state/session.ts:14-19]()

### 2. Multi-Database Strategy

AI Sheets employs a specialized multi-database architecture where each database serves specific use cases:

| Database | Purpose | Key Use Cases |
|----------|---------|---------------|
| SQLite | Application data | User sessions, dataset metadata, configuration |
| DuckDB | Analytics | OLAP queries, data analysis, large dataset processing |
| LanceDB | Vector operations | Embeddings, similarity search, AI model storage |

```mermaid
graph TB
    subgraph "Application Logic"
        DataService["Data Service Layer"]
        AnalyticsService["Analytics Service"]  
        VectorService["Vector Service"]
    end
    
    subgraph "Database Layer"
        SQLiteDB[("SQLite<br/>sequelize")]
        DuckDBInstance[("DuckDB<br/>@duckdb/node-api")]
        LanceDBInstance[("LanceDB<br/>@lancedb/lancedb")]
    end
    
    subgraph "Data Types"
        AppData["User data<br/>Sessions<br/>Metadata"]
        AnalyticsData["Query results<br/>Aggregations<br/>Reports"]
        VectorData["Embeddings<br/>Similarity indices<br/>AI models"]
    end
    
    DataService --> SQLiteDB
    AnalyticsService --> DuckDBInstance
    VectorService --> LanceDBInstance
    
    SQLiteDB -.-> AppData
    DuckDBInstance -.-> AnalyticsData
    LanceDBInstance -.-> VectorData
```

Sources: [package.json:71-77](), [package.json:91-92]()

### 3. Session Management Pattern

The application implements server-side session management with automatic redirection for unauthenticated requests:

```mermaid
graph TD
    RequestEvent["RequestEvent"]
    LayoutHandler["layout.tsx onGet"]
    CheckSession["checkSession()"]
    UseServerSession["useServerSession()"]
    SharedMap["sharedMap"]
    
    RequestEvent --> LayoutHandler
    LayoutHandler --> CheckSession
    CheckSession --> UseServerSession
    UseServerSession --> SharedMap
    
    SharedMap -->|"session found"| SessionObject["Session Object"]
    SharedMap -->|"no session"| ThrowError["throw Error"]
    ThrowError --> RedirectLogin["redirect(302, '/')"]
    
    SessionObject --> CacheControl["cacheControl()"]
    CacheControl --> ContinueRequest["Continue to Route"]
```

Sources: [src/routes/layout.tsx:8-28](), [src/state/session.ts:14-26]()

## Build and Deployment Architecture

The system uses a multi-stage Docker build process optimized for production deployment:

### Build Pipeline

```mermaid
graph TD
    subgraph "Build Stage (node:22-slim)"
        SourceCode["Source Code"]
        PnpmInstall["pnpm install"]
        QwikBuild["pnpm build"]
        BuildArtifacts["dist/ + server/"]
    end
    
    subgraph "Production Stage (node:22-slim)"  
        CopyArtifacts["Copy build artifacts"]
        PlaywrightInstall["Install Playwright"]
        ExpressStart["node server/entry.express"]
    end
    
    subgraph "Runtime Dependencies"
        NodeModules["node_modules/"]
        PlaywrightBrowsers["Chromium browser"]
        SQLiteRuntime["SQLite runtime"]
    end
    
    SourceCode --> PnpmInstall
    PnpmInstall --> QwikBuild
    QwikBuild --> BuildArtifacts
    
    BuildArtifacts --> CopyArtifacts
    CopyArtifacts --> PlaywrightInstall
    PlaywrightInstall --> ExpressStart
    
    NodeModules --> ExpressStart
    PlaywrightBrowsers --> ExpressStart
    SQLiteRuntime --> ExpressStart
```

Sources: [Dockerfile:1-61](), [package.json:16-22](), [package.json:29]()

### Environment Configuration

The build process includes several optimization strategies:

- **Memory Management**: `NODE_OPTIONS="--max-old-space-size=4096"` for build stage
- **Dependency Optimization**: `SKIP_POSTINSTALL=1` during Docker build
- **Browser Automation**: Playwright with Chromium for web scraping capabilities
- **Database Runtime**: Native SQLite support with build tools

Sources: [Dockerfile:7-10](), [Dockerfile:50-54](), [package.json:15-16]()

## Integration Architecture

The system integrates with external services through a service layer abstraction:

```mermaid
graph TB
    subgraph "Core Services"
        DatasetService["Dataset Service"]
        AIService["AI Service"] 
        SearchService["Search Service"]
        AuthService["Auth Service"]
    end
    
    subgraph "External APIs"
        HFHub["@huggingface/hub"]
        HFInference["@huggingface/inference"] 
        HFTransformers["@huggingface/transformers"]
        WebSearchAPI["Web Search API"]
        OAuthProvider["OAuth Provider"]
    end
    
    subgraph "Data Processing"
        ArrowJS["apache-arrow"]
        DOMPurify["dompurify"]
        MarkdownParser["marked + highlight.js"]
        YAMLParser["yaml"]
    end
    
    DatasetService --> HFHub
    AIService --> HFInference
    AIService --> HFTransformers
    SearchService --> WebSearchAPI
    AuthService --> OAuthProvider
    
    AIService --> ArrowJS
    DatasetService --> DOMPurify
    DatasetService --> MarkdownParser
    SearchService --> YAMLParser
```

Sources: [package.json:72-75](), [package.json:80-94]()

This architecture provides a scalable foundation for AI-powered dataset operations while maintaining clear separation of concerns between presentation, business logic, and data persistence layers.

---

