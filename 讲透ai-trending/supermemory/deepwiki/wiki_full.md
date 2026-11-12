# Page: Overview

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitignore](.gitignore)
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [README.md](README.md)
- [README.zh-CN.md](README.zh-CN.md)
- [apps/docs/cookbook/overview.mdx](apps/docs/cookbook/overview.mdx)
- [apps/docs/docs.json](apps/docs/docs.json)
- [apps/docs/integrations/claude-code.mdx](apps/docs/integrations/claude-code.mdx)
- [apps/docs/integrations/codex.mdx](apps/docs/integrations/codex.mdx)
- [apps/docs/integrations/openclaw.mdx](apps/docs/integrations/openclaw.mdx)
- [apps/docs/integrations/opencode.mdx](apps/docs/integrations/opencode.mdx)
- [apps/docs/integrations/supermemory-sdk.mdx](apps/docs/integrations/supermemory-sdk.mdx)
- [apps/docs/intro.mdx](apps/docs/intro.mdx)
- [apps/docs/memory-api/sdks/overview.mdx](apps/docs/memory-api/sdks/overview.mdx)
- [apps/docs/migration/from-mem0.mdx](apps/docs/migration/from-mem0.mdx)
- [apps/docs/migration/mem0-migration-script.py](apps/docs/migration/mem0-migration-script.py)
- [apps/docs/quickstart.mdx](apps/docs/quickstart.mdx)
- [apps/docs/self-hosting/configuration.mdx](apps/docs/self-hosting/configuration.mdx)
- [apps/docs/self-hosting/local-vs-enterprise.mdx](apps/docs/self-hosting/local-vs-enterprise.mdx)
- [apps/web/.gitignore](apps/web/.gitignore)
- [apps/web/app/global-error.tsx](apps/web/app/global-error.tsx)
- [apps/web/app/layout.tsx](apps/web/app/layout.tsx)
- [apps/web/package.json](apps/web/package.json)
- [apps/web/public/OG.png](apps/web/public/OG.png)
- [apps/web/tsconfig.json](apps/web/tsconfig.json)
- [apps/web/wrangler.jsonc](apps/web/wrangler.jsonc)
- [bun.lock](bun.lock)
- [package.json](package.json)
- [turbo.json](turbo.json)

</details>



Supermemory is a state-of-the-art memory and context engine for AI applications. It solves the "Goldfish Memory" problem where AI systems forget everything between sessions. It automatically extracts facts from conversations, builds evolving user profiles, resolves knowledge contradictions, and delivers relevant context on demand. The system ranks #1 on **LongMemEval**, **LoCoMo**, and **ConvoMem** — the three major benchmarks for AI memory evaluation. [README.md:33-40]()

**Who it's for:**
- **AI Users**: Get persistent memory across Claude Desktop, Cursor, Windsurf, and VS Code via the MCP server (`apps/mcp/`) and browser extension (`apps/browser-extension/`). [README.md:102-106](), [README.md:160-163]()
- **AI Builders**: Add memory, RAG, user profiles, and connectors to agents via the REST API, TypeScript/Python SDKs, or `@supermemory/tools` middleware. [README.md:73-79](), [apps/docs/quickstart.mdx:21-36]()

This page maps the major components of the codebase at a high level. Detailed coverage is split across child pages:

| Section | Covers |
|---------|--------|
| [System Architecture](#1.1) | Component diagrams, data flow, and deployment topology. |
| [Core Features](#1.2) | Memory extraction, user profiles, hybrid search, and connectors. |
| [Monorepo Structure](#1.3) | Workspace layout, Turbo task orchestration, and package roles. |

## High-Level System Map

Supermemory is organized as a monorepo using **Turbo** (`turbo@2.5.4`) and **Bun** (`bun@1.3.6`). [package.json:16-64]()

### Bridge: Natural Language to Code Entities
The following diagram associates high-level system concepts with the specific code entities that implement them.

```mermaid
graph TD
    subgraph "Natural Language Space"
        User["'I want my AI to remember me'"]
        Dev["'I want to add memory to my app'"]
        Search["'Search my bookmarks and notes'"]
    end

    subgraph "Code Entity Space"
        subgraph "Entry Points"
            MCPServer["apps/mcp/src/index.ts<br/>(MCP Server)"]
            WebApp["apps/web/app/layout.tsx<br/>(Root Layout)"]
            BrowserExt["apps/browser-extension/entrypoints/background.ts<br/>(WXT Extension)"]
        end

        subgraph "Core Logic"
            WithSM["packages/tools/src/withSupermemory.ts<br/>(Middleware)"]
            SMClient["packages/openai-sdk-ts/src/index.ts<br/>(SDK Client)"]
            ProfileAPI["apps/web/app/api/v4/profile/route.ts<br/>(Context Engine)"]
        end

        subgraph "Storage"
            DrizzleDB["packages/lib/src/db/schema.ts<br/>(PostgreSQL Schema)"]
            VectorSearch["apps/web/src/lib/vector-search.ts<br/>(Semantic Search)"]
        end
    end

    User --> MCPServer
    User --> BrowserExt
    Dev --> WithSM
    Dev --> SMClient
    Search --> WebApp
    
    MCPServer --> ProfileAPI
    WithSM --> ProfileAPI
    WebApp --> VectorSearch
    ProfileAPI --> DrizzleDB
```
Sources: [package.json:17-22](), [apps/web/package.json:22-118](), [apps/mcp/package.json:86-108](), [CONTRIBUTING.md:58-83]()

## Core Components

The repository is divided into applications (`apps/`) and shared logic (`packages/`). [package.json:17-22]()

### Applications
- **Web Application** (`apps/web/`): A Next.js 16 application deployed to Cloudflare via `opennextjs-cloudflare`. It provides the dashboard, chat interface (Nova), and memory management. [apps/web/package.json:9-18](), [apps/web/app/layout.tsx:83-115]()
- **MCP Server** (`apps/mcp/`): Implements the Model Context Protocol, allowing tools like Cursor or Claude Desktop to call `memory()` and `recall()` tools. [apps/mcp/package.json:86-98](), [README.md:131-139]()
- **Browser Extension** (`apps/browser-extension/`): A WXT-based extension for capturing web content and importing Twitter bookmarks. [apps/browser-extension/package.json:53-74]()
- **Memory Graph Playground** (`apps/memory-graph-playground/`): A demo for the `@supermemory/memory-graph` visualization package. [apps/memory-graph-playground/package.json:110-118]()

### Major Packages
- **@supermemory/tools** (`packages/tools/`): Provides the `withSupermemory` higher-order function to wrap LLM calls with memory injection. [CONTRIBUTING.md:74]()
- **Memory Graph** (`packages/memory-graph/`): A React component library for visualizing knowledge relationships. [apps/web/package.json:56]()
- **Shared Libraries**: Includes `@repo/lib` (utilities), `@repo/ui` (Shadcn/Tailwind components), and `@repo/validation` (Zod schemas). [apps/web/package.json:53-54](), [CONTRIBUTING.md:69-73]()

## Technical Stack & Infrastructure

Supermemory leverages a modern, high-performance stack optimized for edge deployment and AI orchestration.

| Layer | Technology | Code Reference |
|-------|------------|----------------|
| **Runtime** | Bun & Cloudflare Workers | [package.json:16](), [apps/mcp/package.json:100]() |
| **Framework** | Next.js 16 (App Router) & React 19 | [apps/web/package.json:95-102]() |
| **Database** | PostgreSQL + Drizzle ORM | [package.json:44-52]() |
| **AI Orchestration** | Vercel AI SDK (`ai`) | [package.json:35](), [apps/web/package.json:77]() |
| **Styling** | Tailwind CSS 4 & Radix UI | [apps/web/package.json:129](), [apps/web/package.json:35-49]() |
| **Observability** | Sentry & PostHog | [apps/web/package.json:55](), [apps/web/package.json:99]() |

### Data Flow Architecture
The following diagram bridges the "Natural Language" intent of saving a memory to the "Code Entity" flow that persists it.

```mermaid
sequenceDiagram
    participant User as "User (Natural Language)"
    participant Ext as "apps/browser-extension/<br/>(Content Script)"
    participant API as "apps/web/api/v3/add<br/>(Hono/Next Route)"
    participant Proc as "packages/ai-sdk/<br/>(Extraction Logic)"
    participant DB as "packages/lib/db<br/>(Drizzle/Postgres)"

    User->>Ext: Click "Save to Supermemory"
    Ext->>API: POST /v3/add { content, containerTag }
    API->>Proc: extractMemories(content)
    Note over Proc: AI identifies facts<br/>and user preferences
    Proc->>DB: db.insert(memories).values(...)
    DB-->>User: Memory Persisted & Indexed
```
Sources: [README.md:143-148](), [apps/docs/quickstart.mdx:116-120](), [apps/docs/intro.mdx:21-23]()

## Development Orchestration

The monorepo uses `turbo` to manage tasks across all workspaces. [package.json:4-11]()

- **Build Pipeline**: `turbo run build` handles dependencies between `@repo/lib` and `apps/web`. [package.json:5]()
- **Type Safety**: `turbo run check-types` ensures consistency across the TypeScript 5.8.3 codebase. [package.json:9](), [package.json:65]()
- **Code Quality**: **Biome** (`@biomejs/biome@2.2.0`) is used for unified linting and formatting instead of ESLint/Prettier. [package.json:59](), [package.json:8]()
- **Error Tracking**: A `postbuild` hook automatically triggers `sentry-cli` to upload source maps for the `consumer-app` project. [package.json:10-11]()

Sources: [package.json:1-67](), [CONTRIBUTING.md:85-109]()

---

# Page: System Architecture

# System Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitignore](.gitignore)
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [README.md](README.md)
- [README.zh-CN.md](README.zh-CN.md)
- [apps/docs/cookbook/overview.mdx](apps/docs/cookbook/overview.mdx)
- [apps/docs/memory-api/sdks/overview.mdx](apps/docs/memory-api/sdks/overview.mdx)
- [apps/docs/migration/from-mem0.mdx](apps/docs/migration/from-mem0.mdx)
- [apps/docs/migration/mem0-migration-script.py](apps/docs/migration/mem0-migration-script.py)
- [apps/web/.gitignore](apps/web/.gitignore)
- [apps/web/app/global-error.tsx](apps/web/app/global-error.tsx)
- [apps/web/app/layout.tsx](apps/web/app/layout.tsx)
- [apps/web/hooks/use-container-tags.ts](apps/web/hooks/use-container-tags.ts)
- [apps/web/hooks/use-project-mutations.ts](apps/web/hooks/use-project-mutations.ts)
- [apps/web/package.json](apps/web/package.json)
- [apps/web/public/OG.png](apps/web/public/OG.png)
- [apps/web/stores/index.ts](apps/web/stores/index.ts)
- [apps/web/tsconfig.json](apps/web/tsconfig.json)
- [apps/web/wrangler.jsonc](apps/web/wrangler.jsonc)
- [bun.lock](bun.lock)
- [package.json](package.json)
- [packages/lib/api.ts](packages/lib/api.ts)
- [packages/lib/types.ts](packages/lib/types.ts)
- [packages/validation/api.ts](packages/validation/api.ts)
- [turbo.json](turbo.json)

</details>



This page describes the overall structure of the supermemory monorepo: what the major components are, how they relate to each other, and how data flows between them. It covers `apps/web`, `apps/mcp`, `apps/browser-extension`, the published SDK packages, shared internal packages, and the backend API they all communicate with.

For monorepo workspace configuration and build orchestration details, see [1.3](). For a summary of the capabilities each component exposes, see [1.2]().

---

## Component Summary

The monorepo is structured as a Bun workspace with two top-level groups, `apps/*` and `packages/*`, as defined in [package.json:17-22](). The table below maps each deployable component to its directory, runtime, and public endpoint.

| Component | Directory | Runtime | Public Endpoint |
|---|---|---|---|
| Web Application | `apps/web` | Cloudflare Pages (via `opennextjs-cloudflare`) | `app.supermemory.ai` |
| MCP Server | `apps/mcp` | Cloudflare Workers + DurableObjects | `mcp.supermemory.ai/mcp` |
| Browser Extension | `apps/browser-extension` | Chrome / Firefox (WXT-based) | — |
| Memory Graph Playground | `apps/memory-graph-playground` | Next.js | — |
| Docs Site | `apps/docs` | Static (Mintlify) | `supermemory.ai/docs` |
| Backend API | (external service) | — | `api.supermemory.ai` |
| TypeScript SDK | `packages/openai-sdk-ts` | npm (`supermemory`) | — |
| Python SDK | `packages/openai-sdk-python` | PyPI (`supermemory`) | — |
| AI Tools Package | `packages/tools` | npm (`@supermemory/tools`) | — |
| Memory Graph Component | `packages/memory-graph` | React/WebGL | — |

Sources: [package.json:17-22](), [CONTRIBUTING.md:63-79](), [apps/web/package.json:15-17](), [apps/mcp/package.json:86-108](), [apps/memory-graph-playground/package.json:110-118]()

---

## Architecture Overview

The following diagram shows the runtime components and the communication paths between them. All client-facing components call `api.supermemory.ai` over HTTPS. The MCP server acts as a protocol adapter between AI clients speaking the Model Context Protocol and the REST backend API.

**Top-level component and communication diagram**

```mermaid
graph TD
    subgraph "ClientSurface"
        WebApp["apps/web"]
        BrowserExt["apps/browser-extension"]
        AIClients["AI Clients (Cursor, Claude, VSCode...)"]
        DevApps["Developer Applications"]
    end

    subgraph "CloudflareWorkers"
        MCPServer["apps/mcp"]
    end

    subgraph "PublishedPackages"
        Tools["@supermemory/tools"]
        TsSDK["supermemory (TS)"]
        PySDK["supermemory (Python)"]
    end

    subgraph "SharedInternalPackages"
        UI["packages/ui"]
        Lib["packages/lib"]
        Validation["packages/validation"]
        MemGraph["packages/memory-graph"]
    end

    BackendAPI["api.supermemory.ai (REST API)"]

    WebApp -->|"HTTPS + API key"| BackendAPI
    BrowserExt -->|"HTTPS + API key"| BackendAPI
    AIClients -->|"MCP Protocol"| MCPServer
    MCPServer -->|"HTTPS + API key"| BackendAPI
    DevApps --> Tools
    DevApps --> TsSDK
    DevApps --> PySDK
    Tools -->|"HTTPS + API key"| BackendAPI
    TsSDK -->|"HTTPS + API key"| BackendAPI
    PySDK -->|"HTTPS + API key"| BackendAPI
    WebApp --> UI
    WebApp --> Lib
    WebApp --> Validation
    WebApp --> MemGraph
```

Sources: [package.json:17-22](), [README.md:102-140](), [CONTRIBUTING.md:63-79]()

---

## Web Application (`apps/web`)

`apps/web` is a Next.js 16 application deployed to Cloudflare Pages via `opennextjs-cloudflare` [apps/web/package.json:34](). It is the primary consumer-facing UI, accessible at `app.supermemory.ai`.

All HTTP calls to the backend are authenticated and typically use the `Authorization: Bearer <api_key>` pattern. The web app integrates various AI models through `@ai-sdk/google`, `@ai-sdk/react`, and `@ai-sdk/xai` [apps/web/package.json:23-25]().

**Key responsibilities:**
- Memory and document CRUD, displayed in a masonry grid via `masonic` [apps/web/package.json:93]().
- Chat interface (Nova agent) using the Vercel AI SDK [apps/web/package.json:77]().
- Knowledge visualization using the internal `@supermemory/memory-graph` package [apps/web/package.json:56]().
- Connector management (Google Drive, Notion, OneDrive, GitHub) via `$fetch` wrapper using `apiSchema` [packages/lib/api.ts:59-167]().
- User onboarding and profile management.

**Client-side state** uses `zustand` for local stores [apps/web/package.json:117]() and TanStack Query (`@tanstack/react-query`) for server state [apps/web/package.json:59](). Authentication is handled by `better-auth` [package.json:38]().

**Build and deployment scripts** are defined in [apps/web/package.json:9-21]():

| Script | Command |
|---|---|
| `dev` | `next dev` |
| `build` | `next build` |
| `preview` | `opennextjs-cloudflare build && opennextjs-cloudflare preview` |
| `deploy` | `opennextjs-cloudflare build && opennextjs-cloudflare deploy` |
| `cf-typegen` | `wrangler types --env-interface CloudflareEnv cloudflare-env.d.ts` |

Sources: [apps/web/package.json:1-137](), [apps/web/app/layout.tsx:1-115](), [packages/lib/api.ts:59-167]()

---

## MCP Server (`apps/mcp`)

`apps/mcp` is a Cloudflare Worker that implements the [Model Context Protocol](https://modelcontextprotocol.io). It bridges AI clients (Cursor, Claude Desktop, VS Code, etc.) to the Supermemory REST API.

**MCP server code entity map**

```mermaid
graph TD
    subgraph "apps/mcp"
        McpServer["@modelcontextprotocol/sdk"]
        SupermemoryMCP["supermemory (internal dep)"]
        HonoApp["hono (Server)"]
    end

    subgraph "MCPTools"
        MemoryTool["tool: memory"]
        RecallTool["tool: recall"]
        ProfileResource["resource: User Profile"]
    end

    AIClients["AI Clients (Cursor, Claude)"]
    BackendAPI["api.supermemory.ai"]

    AIClients -->|"JSON-RPC"| McpServer
    McpServer --> HonoApp
    HonoApp --> SupermemoryMCP
    SupermemoryMCP --> MemoryTool
    SupermemoryMCP --> RecallTool
    RecallTool --> BackendAPI
    MemoryTool --> BackendAPI
```

The MCP server uses `hono` for request handling [apps/mcp/package.json:94]() and the `@modelcontextprotocol/sdk` [apps/mcp/package.json:92](). It allows AI assistants to automatically call `memory` to save facts and `recall` to search memories [README.md:143-148]().

Sources: [apps/mcp/package.json:86-108](), [README.md:131-177]()

---

## AI Tools and SDKs

The repository provides multiple entry points for developers to integrate memory into AI applications. The core logic for these integrations is centralized in `packages/lib/api.ts`, which defines the `apiSchema` using `@better-fetch/fetch` [packages/lib/api.ts:1-59]().

**SDK and tools integration map**

```mermaid
graph LR
    subgraph "packages/lib"
        apiSchema["apiSchema (Definition)"]
        fetchWrapper["$fetch (Better-Fetch)"]
    end

    subgraph "FrameworkIntegration"
        VercelAISDK["ai (Vercel AI SDK)"]
        OpenAI["openai (SDK)"]
        Mastra["Mastra Agent"]
    end

    BackendAPI["api.supermemory.ai"]

    apiSchema --> fetchWrapper
    fetchWrapper --> BackendAPI
    VercelAISDK -->|"uses"| apiSchema
    OpenAI -->|"uses"| apiSchema
```

The system uses `containerTags` to scope memories and profiles, allowing developers to separate work and personal context [README.md:157-158](). Scoped API keys can be managed via the `@post/auth/scoped-key` endpoint defined in the API schema.

Sources: [packages/lib/api.ts:1-270](), [README.md:141-158](), [CONTRIBUTING.md:73-77]()

---

## Shared Packages

Shared internal packages provide the foundation for the applications in the monorepo.

| Package | Contents |
|---|---|
| `packages/ui` | Shared Shadcn UI components and Tailwind configuration [CONTRIBUTING.md:70](). |
| `packages/lib` | Shared utilities, API client logic (`apiSchema`), and auth context [CONTRIBUTING.md:71](). |
| `packages/validation` | Zod schemas for shared data structures and API validation [CONTRIBUTING.md:73](). |
| `packages/memory-graph` | React component for knowledge graph visualization [apps/web/package.json:56](). |

The monorepo uses `turbo` to orchestrate tasks across these packages, ensuring that dependencies are built in the correct order [turbo.json:1-25]().

Sources: [CONTRIBUTING.md:63-79](), [package.json:17-22](), [turbo.json:1-25]()

---

# Page: Core Features

# Core Features

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CONTRIBUTING.md](CONTRIBUTING.md)
- [README.md](README.md)
- [README.zh-CN.md](README.zh-CN.md)
- [apps/docs/add-memories.mdx](apps/docs/add-memories.mdx)
- [apps/docs/concepts/customization.mdx](apps/docs/concepts/customization.mdx)
- [apps/docs/cookbook/overview.mdx](apps/docs/cookbook/overview.mdx)
- [apps/docs/docs.json](apps/docs/docs.json)
- [apps/docs/images/memory-graph.png](apps/docs/images/memory-graph.png)
- [apps/docs/install.md](apps/docs/install.md)
- [apps/docs/integrations/claude-code.mdx](apps/docs/integrations/claude-code.mdx)
- [apps/docs/integrations/codex.mdx](apps/docs/integrations/codex.mdx)
- [apps/docs/integrations/openclaw.mdx](apps/docs/integrations/openclaw.mdx)
- [apps/docs/integrations/opencode.mdx](apps/docs/integrations/opencode.mdx)
- [apps/docs/integrations/supermemory-sdk.mdx](apps/docs/integrations/supermemory-sdk.mdx)
- [apps/docs/intro.mdx](apps/docs/intro.mdx)
- [apps/docs/memory-api/sdks/overview.mdx](apps/docs/memory-api/sdks/overview.mdx)
- [apps/docs/migration/from-mem0.mdx](apps/docs/migration/from-mem0.mdx)
- [apps/docs/migration/mem0-migration-script.py](apps/docs/migration/mem0-migration-script.py)
- [apps/docs/quickstart.mdx](apps/docs/quickstart.mdx)
- [apps/docs/self-hosting/configuration.mdx](apps/docs/self-hosting/configuration.mdx)
- [apps/docs/self-hosting/local-vs-enterprise.mdx](apps/docs/self-hosting/local-vs-enterprise.mdx)
- [apps/docs/test.py](apps/docs/test.py)
- [apps/docs/test.ts](apps/docs/test.ts)
- [apps/docs/user-profiles.mdx](apps/docs/user-profiles.mdx)
- [apps/docs/user-profiles/api.mdx](apps/docs/user-profiles/api.mdx)
- [apps/docs/user-profiles/examples.mdx](apps/docs/user-profiles/examples.mdx)
- [apps/docs/vibe-coding.mdx](apps/docs/vibe-coding.mdx)
- [packages/docs-test/tests/integrations/ai-sdk.ts](packages/docs-test/tests/integrations/ai-sdk.ts)
- [turbo.json](turbo.json)

</details>



This page summarizes the key capabilities that supermemory exposes across its components. It describes what each feature does and which code entities implement it, without going deep into any single component's internals. For architecture and component relationships, see [System Architecture](#1.1). For monorepo layout and package roles, see [Monorepo Structure](#1.3).

---

## Overview

Supermemory provides a unified context and memory layer for AI applications. Its features span the REST API, TypeScript/Python SDKs, the `@supermemory/tools` middleware package, an MCP server, and a browser extension. All features are built around a single memory ontology indexed under **container tags** — string identifiers that scope memories and profiles to a user, project, or session. [README.md:156-157](), [apps/docs/intro.mdx:72-74](), [apps/docs/install.md:60-61]()

**Feature summary:**

| Feature | What it does | Primary entry point |
|---|---|---|
| Memory extraction | Extracts and stores facts from conversations | `client.add()` / `POST /v3/documents` |
| User profiles | Auto-maintained static + dynamic user context | `client.profile()` / `POST /v4/profile` |
| Hybrid search | RAG + memory retrieval in one query | `client.search()` / `POST /v4/search` |
| Connectors | OAuth sync from Drive, Gmail, Notion, GitHub, etc. | `POST /v3/connections/{provider}` |
| MCP server | Tool-based memory for AI coding clients | `mcp.supermemory.ai/mcp` |
| SDK middleware | Drop-in memory for Vercel AI SDK, Mastra, etc. | `withSupermemory()` in `@supermemory/tools` |
| File processing | PDFs, images, video, code → searchable chunks | `client.documents.uploadFile()` |
| SMFS | Virtual filesystem for agentic memory access | `curl -fsSL https://supermemory.ai/install` |

Sources: [README.md:36-47](), [apps/docs/intro.mdx:9-13](), [apps/docs/install.md:124-130](), [apps/docs/docs.json:160-165]()

---

## Memory Extraction

The core function of supermemory is converting raw conversations or text into structured, queryable facts. When content is submitted via `client.add()` or `POST /v3/documents`, the backend extracts discrete facts and preferences, resolves contradictions, and handles temporal expiry. [README.md:32-34](), [apps/docs/add-memories.mdx:8-9]()

Content types accepted include plain text, conversation transcripts, URLs, PDFs, images (OCR), video (transcription), and code (AST-aware chunking). [README.md:47-47](), [apps/docs/add-memories.mdx:181-189]()

**Memory submission flow:**

```mermaid
flowchart LR
    A["client.add(content, containerTag)"] --> B["POST /v3/documents"]
    B --> C["Content parser / chunker"]
    C --> D["Fact extractor"]
    D --> E["Contradiction resolver"]
    E --> F["Memory store (containerTag scoped)"]
```

Sources: [apps/docs/add-memories.mdx:24-28](), [apps/docs/add-memories.mdx:196-205](), [apps/docs/intro.mdx:21-23]()

---

## User Profiles (Static and Dynamic)

The profile feature auto-maintains two classes of user context without requiring explicit queries. This is implemented via the `POST /v4/profile` endpoint. [apps/docs/intro.mdx:50-52](), [apps/docs/install.md:221-224]()

- **`profile.static`**: Long-term, stable facts about the user (e.g., information that the agent should **always** know). [apps/docs/intro.mdx:55-55](), [apps/docs/quickstart.mdx:61-62]()
- **`profile.dynamic`**: Recent context and episodic information (e.g., recent conversations or current tasks). [apps/docs/intro.mdx:56-56](), [apps/docs/quickstart.mdx:64-65]()

The profile can be retrieved standalone or combined with semantic search results by providing a `q` parameter. [apps/docs/quickstart.mdx:95-99](), [apps/docs/install.md:31-32]()

**Profile API response shape:**

```json
{
  "profile": {
    "static": ["User is a software engineer", "Prefers dark mode"],
    "dynamic": ["Working on Project Alpha", "Learning Rust"]
  },
  "searchResults": {
    "results": [...],
    "total": 15
  }
}
```

**Profile endpoint data flow:**

```mermaid
flowchart TD
    A["POST /v4/profile\n{containerTag, q?, threshold?}"] --> B["Profile builder"]
    B --> C["profile.static\n(long-term facts)"]
    B --> D["profile.dynamic\n(recent context)"]
    A --> E{"q parameter\npresent?"}
    E -- "yes" --> F["Semantic search over memories"]
    F --> G["searchResults.results"]
    E -- "no" --> H["searchResults omitted"]
```

Sources: [apps/docs/quickstart.mdx:54-68](), [apps/docs/intro.mdx:50-58](), [apps/docs/install.md:132-136]()

---

## Hybrid Search and RAG

Supermemory provides hybrid search capabilities that combine traditional RAG (document chunks) with personalized memory context. [README.md:45-45]()

- **Search Modes**: The API supports `hybrid` mode which searches both memories and document chunks. [apps/docs/install.md:166-170](), [apps/docs/install.md:230-230]()
- **Metadata Filtering**: Supports advanced metadata filtering for precise retrieval. [apps/docs/intro.mdx:63-63](), [apps/docs/add-memories.mdx:201-202]()

**Search call path:**

```mermaid
flowchart LR
    A["client.search({q, containerTag, searchMode})"] --> B["POST /v4/search"]
    B --> C{"searchMode"}
    C -- "hybrid" --> D["Vector search over documents"]
    C -- "hybrid" --> E["Memory fact lookup"]
    D --> F["Merged & Deduplicated results"]
    E --> F
```

Sources: [apps/docs/intro.mdx:60-66](), [apps/docs/install.md:166-172](), [apps/docs/install.md:227-231]()

---

## Connectors

Connectors sync external data sources into the supermemory index automatically using real-time webhooks where supported. [README.md:46-46]()

| Provider | Sync Type |
|---|---|
| Google Drive | OAuth + Auto-sync |
| Gmail | OAuth + Auto-sync |
| Notion | OAuth + Auto-sync |
| OneDrive | OAuth + Auto-sync |
| GitHub | OAuth + Webhooks |
| Web Crawler | URL-based ingestion |

Sources: [README.md:46-46](), [apps/docs/docs.json:119-127]()

---

## MCP Integration

The MCP server (`apps/mcp`) implements the Model Context Protocol, exposing supermemory as tools for AI clients like Claude Desktop, Cursor, and VS Code. [README.md:104-105](), [README.md:139-140]()

**Registered MCP tools:** [README.md:143-148]()
- `memory`: Save or forget information.
- `recall`: Search memories by query.
- `context`: Injects full profile (preferences, recent activity) into the conversation.

Sources: [README.md:133-134](), [README.md:141-148]()

---

## SMFS (Supermemory Filesystem)

SMFS allows AI agents to interact with memory as if it were a local filesystem. This is particularly useful for agents running in sandboxed environments like E2B or Daytona. [apps/docs/docs.json:160-165]()

- **Mount**: Mounts a container as a directory using NFSv3 or FUSE. [apps/docs/docs.json:165-165]()
- **Bash Tool**: A programmatic interface for agents to execute shell commands against memory. [apps/docs/docs.json:166-167]()

Sources: [apps/docs/docs.json:160-180](), [README.md:91-91]()

---

## SDK and Middleware Support

### TypeScript/Python SDKs
Official SDKs provide typed wrappers for the REST API, including `client.add`, `client.profile`, and `client.search`. [apps/docs/quickstart.mdx:43-45](), [apps/docs/quickstart.mdx:84-86]()

### AI SDK Middleware
The `@supermemory/tools` package provides `withSupermemory`, a higher-order function that wraps models from the Vercel AI SDK. [apps/docs/install.md:111-112]()

**Middleware logic:**
1. **Intercepts** LLM calls. [apps/docs/install.md:121-121]()
2. **Fetches** user profile context automatically. [apps/docs/install.md:111-115]()
3. **Injects** data into the context window. [apps/docs/install.md:121-121]()

**Middleware data flow:**

```mermaid
flowchart TD
    A["withSupermemory(model, {containerTag})"] --> B["Wrapped LanguageModel"]
    B --> C["Intercept Generation"]
    C --> D["Fetch Profile Context\nPOST /v4/profile"]
    D --> E["Inject into System Messages"]
    E --> F["Call Original Model Provider"]
```

Sources: [apps/docs/install.md:93-122](), [apps/docs/vibe-coding.mdx:182-194]()

---

# Page: Monorepo Structure

# Monorepo Structure

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitignore](.gitignore)
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [README.md](README.md)
- [README.zh-CN.md](README.zh-CN.md)
- [apps/browser-extension/utils/posthog.ts](apps/browser-extension/utils/posthog.ts)
- [apps/docs/cookbook/overview.mdx](apps/docs/cookbook/overview.mdx)
- [apps/docs/memory-api/sdks/overview.mdx](apps/docs/memory-api/sdks/overview.mdx)
- [apps/docs/migration/from-mem0.mdx](apps/docs/migration/from-mem0.mdx)
- [apps/docs/migration/mem0-migration-script.py](apps/docs/migration/mem0-migration-script.py)
- [apps/docs/package.json](apps/docs/package.json)
- [apps/memory-graph-playground/package.json](apps/memory-graph-playground/package.json)
- [apps/web/.gitignore](apps/web/.gitignore)
- [apps/web/app/global-error.tsx](apps/web/app/global-error.tsx)
- [apps/web/app/layout.tsx](apps/web/app/layout.tsx)
- [apps/web/package.json](apps/web/package.json)
- [apps/web/public/OG.png](apps/web/public/OG.png)
- [apps/web/tsconfig.json](apps/web/tsconfig.json)
- [apps/web/wrangler.jsonc](apps/web/wrangler.jsonc)
- [bun.lock](bun.lock)
- [package.json](package.json)
- [packages/docs-test/package.json](packages/docs-test/package.json)
- [packages/tools/test/chatapp/package.json](packages/tools/test/chatapp/package.json)
- [portless.json](portless.json)
- [turbo.json](turbo.json)

</details>



This document describes the organization of the Supermemory codebase as a Turborepo monorepo, including workspace structure, package management with Bun, shared packages, build orchestration, and dependency relationships between workspaces.

## Overview

Supermemory is organized as a monorepo using Turbo for build orchestration and Bun as the primary package manager [package.json:1-66](). The repository contains multiple applications (`apps/*`) and shared packages (`packages/*`) that enable code reuse across the platform, from the Next.js web application to the browser extension and Model Context Protocol (MCP) server.

**Sources:** [package.json:1-70](), [README.md:1-120]()

## Workspace Organization

The monorepo uses Bun workspaces to manage multiple packages within a single repository. Workspaces are defined in the root `package.json` [package.json:16-21]():

### Monorepo Workspace Map

```mermaid
graph TB
    subgraph "Root [supermemory]"
        Root["package.json"]
    end
    
    subgraph "apps/* [Workspaces]"
        Web["apps/web [@repo/web]"]
        BrowserExt["apps/browser-extension [supermemory-browser-extension]"]
        MCP["apps/mcp [supermemory-mcp]"]
        Docs["apps/docs [@repo/docs]"]
        MemGraphPlay["apps/memory-graph-playground"]
    end
    
    subgraph "packages/* [Workspaces]"
        UI["packages/ui [@repo/ui]"]
        Lib["packages/lib [@repo/lib]"]
        Tools["packages/tools [@supermemory/tools]"]
        Validation["packages/validation [@repo/validation]"]
        MemGraphPkg["packages/memory-graph [@supermemory/memory-graph]"]
    end
    
    Root --> Web
    Root --> BrowserExt
    Root --> MCP
    Root --> Docs
    Root --> MemGraphPlay
    Root --> UI
    Root --> Lib
    Root --> Tools
    Root --> Validation
    Root --> MemGraphPkg
```

The workspace configuration explicitly excludes certain directories to avoid dependency conflicts or because they have independent build processes [package.json:18-20]():
- `!apps/raycast-extension`: Managed separately for the Raycast store.
- `!tools/test/chatapp`: Internal testing sandbox.

**Sources:** [package.json:16-21](), [bun.lock:4-127](), [CONTRIBUTING.md:58-81]()

## Package Manager: Bun

The project uses Bun as the package manager, specified in `package.json` [package.json:15-16]():

| Configuration | Value |
|---------------|-------|
| Package Manager | `bun@1.3.6` [package.json:16]() |
| Node Version Requirement | `>=20` [package.json:14]() |
| Lockfile | `bun.lock` |

Bun provides fast dependency installation and native TypeScript execution. The lockfile format tracks all workspace dependencies and their versions across the entire tree [bun.lock:1-41]().

**Sources:** [package.json:12-16](), [bun.lock:1-52](), [CONTRIBUTING.md:9-11]()

## Build System: Turbo

Turbo orchestrates builds across the monorepo, enabling parallel execution and intelligent caching. The root `package.json` defines workspace-level scripts that delegate to `turbo` [package.json:4-11]():

```json
{
  "scripts": {
    "build": "turbo run build",
    "dev": "turbo run dev",
    "check-types": "turbo run check-types"
  }
}
```

### Task Orchestration

Task behavior is defined in `turbo.json`, which configures task dependencies and cache outputs [turbo.json:1-25]().

1. **Build Dependencies**: The `build` task depends on the build of upstream workspaces (`^build`) [turbo.json:6]().
2. **Input Tracking**: Turbo tracks `.env` files and default inputs to determine cache hits [turbo.json:7]().
3. **Caching**: Build outputs for Next.js apps are stored in `.next/**`, excluding the cache directory [turbo.json:8]().
4. **Persistent Tasks**: Development tasks like `dev` and `dev:app` are marked as persistent and do not use the cache [turbo.json:16-23]().

**Sources:** [package.json:4-11](), [turbo.json:1-25](), [.gitignore:21-22]()

## Shared Root Dependencies

The root `package.json` contains shared dependencies hoisted to the monorepo level. This includes major AI SDKs and infrastructure tools used by multiple packages [package.json:23-57]():

### Infrastructure & Tooling Matrix

| Category | Key Code Entities / Packages |
|----------|---------------------------|
| **AI Providers** | `@ai-sdk/anthropic`, `@ai-sdk/google`, `@ai-sdk/openai`, `ai` [package.json:24-35]() |
| **Database** | `drizzle-orm`, `pg`, `postgres`, `drizzle-zod` [package.json:44-52]() |
| **Auth & API** | `better-auth`, `hono-openapi`, `zod-openapi` [package.json:38-56]() |
| **Build/Lint** | `typescript@5.8.3`, `@biomejs/biome@2.2.0`, `turbo@2.5.4`, `wrangler` [package.json:59-66]() |

**Sources:** [package.json:23-67]()

## Shared Packages

### packages/ui (@repo/ui)
Provides shared UI components built on Radix UI primitives with Tailwind CSS styling. It is imported by apps and other packages to maintain visual consistency [apps/web/tsconfig.json:7-8]().

### packages/lib (@repo/lib)
Contains shared business logic, utility functions, and custom hooks. It is imported by `apps/web` via workspace linking [apps/web/package.json:53]() and configured in path aliases [apps/web/tsconfig.json:9]().

### packages/tools (@supermemory/tools)
The core package for AI middleware. It provides drop-in tools for search and memory injection for frameworks like Vercel AI SDK [README.md:143-148]().

### packages/memory-graph (@supermemory/memory-graph)
A specialized package for knowledge graph visualization using D3-force [apps/web/package.json:56](), [apps/web/package.json:82](). It is demonstrated in the `apps/memory-graph-playground` [apps/memory-graph-playground/package.json:13]().

**Sources:** [CONTRIBUTING.md:67-77](), [apps/web/package.json:53-56](), [apps/web/tsconfig.json:5-11](), [apps/memory-graph-playground/package.json:12-17]()

## Application Packages

### apps/web (@repo/web)
The primary Next.js consumer application. It is deployed to Cloudflare Workers using `@opennextjs/cloudflare` [apps/web/package.json:34](). It depends on several internal workspaces including `@repo/lib`, `@repo/validation`, and `@supermemory/memory-graph` [apps/web/package.json:53-56]().

### apps/mcp (supermemory-mcp)
The Model Context Protocol server implementation. It enables AI clients like Claude Desktop or Cursor to access Supermemory tools [README.md:131-139](). It depends on the `supermemory` package [bun.lock:96]().

### apps/browser-extension (supermemory-browser-extension)
A WXT-based extension [bun.lock:72](). It uses `@tanstack/react-query` for state management and `posthog-js` for analytics [bun.lock:58-59]().

**Sources:** [apps/web/package.json:1-137](), [bun.lock:53-109](), [README.md:102-140]()

## Dependency Flow & Code Associations

The following diagrams bridge the high-level architecture to specific code entities and workspace relationships.

### System Entity Mapping

```mermaid
graph LR
    subgraph "Natural Language Space"
        UserAuth["User Authentication"]
        MemStore["Memory Storage"]
        Visual["Graph Visualization"]
        AIContext["AI Model Context"]
    end

    subgraph "Code Entity Space"
        AuthProv["AuthProvider [apps/web/app/layout.tsx]"]
        Drizzle["drizzle-orm [root package.json]"]
        MemGraph["@supermemory/memory-graph [packages/memory-graph]"]
        MCPServer["supermemory-mcp [apps/mcp]"]
        WebBuild["opennextjs-cloudflare build [apps/web/package.json]"]
    end

    UserAuth -.-> AuthProv
    MemStore -.-> Drizzle
    Visual -.-> MemGraph
    AIContext -.-> MCPServer
    
    AuthProv --> WebBuild
    MemGraph --> WebBuild
```

### Component Relationship Diagram

```mermaid
graph TD
    subgraph "Apps"
        Web["@repo/web [apps/web]"]
        MCP["supermemory-mcp [apps/mcp]"]
        Extension["browser-extension [apps/browser-extension]"]
    end

    subgraph "Shared Packages"
        Lib["@repo/lib [packages/lib]"]
        UI["@repo/ui [packages/ui]"]
        Val["@repo/validation [packages/validation]"]
        Graph["@supermemory/memory-graph [packages/memory-graph]"]
    end

    Web --> Lib
    Web --> UI
    Web --> Val
    Web --> Graph

    MCP --> Lib
    Extension --> Lib

    subgraph "Infrastructure"
        DB["Drizzle ORM [package.json]"]
        Auth["Better Auth [package.json]"]
        Cloudflare["OpenNext / Wrangler [apps/web/package.json]"]
    end

    Web --> Cloudflare
    Lib --> DB
    Lib --> Auth
```

**Sources:** [apps/web/app/layout.tsx:5](), [package.json:44](), [apps/web/package.json:15-17](), [bun.lock:87](), [apps/web/package.json:53-56](), [apps/web/tsconfig.json:5-11]()

## Deployment & CI/CD Orchestration

Deployment is handled via workspace-specific scripts coordinated by the root build task [package.json:5]().

### Deployment Flow

```mermaid
sequenceDiagram
    participant Dev as Developer
    participant Turbo as Turbo Orchestrator
    participant Web as apps/web
    participant Sentry as Sentry CLI
    
    Dev->>Turbo: bun run build
    Turbo->>Web: next build [apps/web/package.json:12]
    Web->>Turbo: Build complete
    Turbo->>Sentry: sentry:sourcemaps (postbuild) [package.json:11]
    Note over Sentry: sentry-cli sourcemaps upload [package.json:10]
    
    Dev->>Web: bun run deploy
    Note over Web: opennextjs-cloudflare deploy [apps/web/package.json:16]
```

**Sources:** [package.json:5-11](), [apps/web/package.json:9-21](), [CONTRIBUTING.md:103-109]()

---

# Page: Web Application

# Web Application

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitignore](.gitignore)
- [apps/web/.gitignore](apps/web/.gitignore)
- [apps/web/app/global-error.tsx](apps/web/app/global-error.tsx)
- [apps/web/app/layout.tsx](apps/web/app/layout.tsx)
- [apps/web/components/dashboard-view.tsx](apps/web/components/dashboard-view.tsx)
- [apps/web/components/highlights-card.tsx](apps/web/components/highlights-card.tsx)
- [apps/web/components/select-spaces-modal.tsx](apps/web/components/select-spaces-modal.tsx)
- [apps/web/components/space-selector.tsx](apps/web/components/space-selector.tsx)
- [apps/web/globals.css](apps/web/globals.css)
- [apps/web/hooks/use-personalization.ts](apps/web/hooks/use-personalization.ts)
- [apps/web/lib/chat-space-label.ts](apps/web/lib/chat-space-label.ts)
- [apps/web/lib/ingest-auto-space.ts](apps/web/lib/ingest-auto-space.ts)
- [apps/web/package.json](apps/web/package.json)
- [apps/web/public/OG.png](apps/web/public/OG.png)
- [apps/web/tsconfig.json](apps/web/tsconfig.json)
- [apps/web/wrangler.jsonc](apps/web/wrangler.jsonc)
- [bun.lock](bun.lock)
- [package.json](package.json)

</details>



## Purpose and Scope

This document provides an overview of the Supermemory web application, a Next.js-based consumer interface deployed on Cloudflare Workers. The application serves as the primary user interface for interacting with the Supermemory memory system, providing chat functionality, document management, search capabilities, and integration management.

For detailed information about specific subsystems:

| Page | Topic |
|------|-------|
| [Application Structure & Providers](#2.1) | Document the `RootLayout`, provider stack, global styles, and font configuration. |
| [Chat Interface](#2.2) | Document the chat UI: messages, model selector, input, sidebar, and conversation storage. |
| [Memory Management](#2.3) | Document memory creation, grid display, optimistic updates, and project organization. |
| [Document Display & Search](#2.4) | Document document cards, command palette, graph view, and URL-driven state. |
| [Integrations & Connections](#2.5) | Document the integrations view, `ConnectAIModal` for MCP, and data source management. |
| [Settings & Profile](#2.6) | Document settings tab structure, onboarding profile steps, and account configuration. |
| [State Management](#2.7) | Document Zustand stores, React Query server state, and auth context. |
| [Onboarding Flow](#2.8) | Document the multi-step onboarding system and completion tracking. |
| [Cloudflare Deployment](#2.9) | Document `opennextjs-cloudflare` deployment, `wrangler.toml`, and build scripts. |
| [UI Component System](#2.10) | Document Shadcn UI setup, Tailwind configuration, and shared UI packages. |
| [Analytics & Error Tracking](#2.11) | Document PostHog, Sentry, and interaction tracking hooks. |

Sources: [apps/web/package.json:1-138]()

## Technology Stack

The web application is built using the following core technologies:

| Technology | Purpose |
|------------|---------|
| **Next.js 16** | React framework with App Router and server components [apps/web/package.json:95](). |
| **Cloudflare Workers** | Edge runtime deployment target using `opennextjs-cloudflare` [apps/web/package.json:34](). |
| **Tailwind CSS 4** | Utility-first styling with shared configuration and `@theme` variables [apps/web/globals.css:2-30](). |
| **Shadcn UI** | Component library using Radix UI primitives and `lucide-react` [apps/web/package.json:35-49, 92](). |
| **Zustand** | Client-side state management with `IndexedDB` persistence via `idb-keyval` [apps/web/package.json:90, 117](). |
| **React Query** | Server state management, caching, and optimistic mutations [apps/web/package.json:59](). |
| **Nuqs** | Type-safe URL search params state management [apps/web/package.json:97](). |

Sources: [apps/web/package.json:22-118](), [apps/web/globals.css:1-30]()

## Application Architecture

### Provider Hierarchy

The `RootLayout` in [apps/web/app/layout.tsx:64-115]() establishes the global context for the application. It wraps the component tree in a specific order of providers to ensure dependencies (like authentication for API calls) are met.

**System-to-Code Provider Mapping:**

```mermaid
graph TD
    Root["RootLayout (apps/web/app/layout.tsx)"]
    Theme["ThemeProvider (lib/theme-provider.tsx)"]
    Autumn["AutumnProvider (autumn-js/react)"]
    Query["QueryProvider (components/query-client.tsx)"]
    Auth["AuthProvider (@lib/auth-context)"]
    PH["PostHogProvider (@lib/posthog)"]
    Err["ErrorTrackingProvider (@lib/error-tracking)"]
    Nuqs["NuqsAdapter (nuqs/adapters/next/app)"]

    Root --> Theme
    Theme --> Autumn
    Autumn --> Query
    Query --> Auth
    Auth --> PH
    PH --> Err
    Err --> Nuqs
    Nuqs --> Content["Children / Pages"]
```

Sources: [apps/web/app/layout.tsx:83-111]()

### Global Styling and Fonts

The application uses `Space_Grotesk` as the primary sans-serif font [apps/web/app/layout.tsx:15-18](). Global styles are managed through a combination of local styles and shared UI package styles [apps/web/app/layout.tsx:3-4](). Tailwind CSS 4 variables define the color palette for the surface and foreground [apps/web/globals.css:8-18]().

Sources: [apps/web/app/layout.tsx:15-18](), [apps/web/globals.css:5-30]()

## Core Architectural Layers

### UI Component System
The UI is built on a Shadcn implementation using Lucide for icons [apps/web/package.json:92](). It utilizes Radix UI primitives for accessible components like dialogs, dropdowns, and tabs [apps/web/package.json:35-49]().

### Deployment & Environment
The app is configured for Cloudflare deployment. It uses `opennextjs-cloudflare` for building and previewing [apps/web/package.json:15-17](). Environment variable typing is handled via `cf-typegen` [apps/web/package.json:18]().

### State and Data Flow
Data fetching and mutation are handled via `QueryProvider` [apps/web/app/layout.tsx:98](), while URL-based UI state is synchronized using the `NuqsAdapter` [apps/web/app/layout.tsx:102]().

**Data Interaction Model:**

```mermaid
graph LR
    subgraph "Client-Side Space"
        Zustand["Zustand Stores\n(zustand)"]
        RQuery["React Query Cache\n(server state)"]
        URL["URL Search Params\n(nuqs state)"]
        IDB["IndexedDB\n(idb-keyval)"]
    end

    subgraph "External Space"
        API["Supermemory API\n(api.supermemory.ai)"]
        AuthSrv["Better Auth\n(Session Management)"]
    end

    RQuery <-->|"Fetch/Mutate"| API
    URL <-->|"Sync"| UI["Next.js Pages/Components"]
    Zustand <-->|"Persist"| IDB
    AuthSrv -->|"Session"| AuthContext["AuthProvider"]
```

Sources: [apps/web/app/layout.tsx:90-110](), [apps/web/package.json:90, 117]()

## Key Interface Components

### Main Dashboard View
The `DashboardView` [apps/web/components/dashboard-view.tsx:1-45]() provides a personalized landing experience. It features dynamic headlines [apps/web/components/dashboard-view.tsx:62-78]() and profession-based taglines for plugins [apps/web/components/dashboard-view.tsx:80-137]() to guide users based on their `Profession` [apps/web/components/dashboard-view.tsx:40]().

### Space Management
The application uses "Spaces" (backed by `containerTag` in the API) to organize content. The `SpaceSelector` [apps/web/components/space-selector.tsx:109-120]() and `SelectSpacesModal` [apps/web/components/select-spaces-modal.tsx:93-106]() allow users to switch between their own spaces or plugin-generated spaces detected via `detectPluginSpace` [apps/web/components/select-spaces-modal.tsx:127]().

### Content Highlights
The `HighlightsCard` component [apps/web/components/highlights-card.tsx:74-80]() visualizes extracted memories. It supports multiple formats like `paragraph`, `bullets`, `quote`, and `one_liner` [apps/web/components/highlights-card.tsx:25-34](). It allows users to chat directly about a specific highlight via the `onChat` callback [apps/web/components/highlights-card.tsx:38]().

### Chat and Interaction
The chat interface utilizes the `ai` package for streaming responses and `react-markdown` for rendering [apps/web/package.json:77, 105](). It supports specific AI features like "Auto" space routing via `AUTO_CHAT_SPACE_ID` [apps/web/components/space-selector.tsx:12]().

## Key Metadata and Assets

The application identifies itself via global metadata and a custom font configuration in the root layout:
- **Font**: `Space_Grotesk` is used as the primary sans-serif font, injected via the `--font-sans` CSS variable [apps/web/app/layout.tsx:15-18]().
- **Metadata**: The base URL is set to `https://app.supermemory.ai` [apps/web/app/layout.tsx:21-21]().
- **Styling**: Scrollbars are customized globally to be thin and themed [apps/web/globals.css:39-66]().

Sources: [apps/web/app/layout.tsx:15-55](), [apps/web/globals.css:32-70]()

---

# Page: Application Structure & Providers

# Application Structure & Providers

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitignore](.gitignore)
- [apps/web/.gitignore](apps/web/.gitignore)
- [apps/web/app/(app)/layout.tsx](apps/web/app/(app)/layout.tsx)
- [apps/web/app/global-error.tsx](apps/web/app/global-error.tsx)
- [apps/web/app/layout.tsx](apps/web/app/layout.tsx)
- [apps/web/components/ensure-workspace.tsx](apps/web/components/ensure-workspace.tsx)
- [apps/web/components/pwa-install-prompt.tsx](apps/web/components/pwa-install-prompt.tsx)
- [apps/web/middleware.ts](apps/web/middleware.ts)
- [apps/web/package.json](apps/web/package.json)
- [apps/web/public/OG.png](apps/web/public/OG.png)
- [apps/web/tsconfig.json](apps/web/tsconfig.json)
- [apps/web/wrangler.jsonc](apps/web/wrangler.jsonc)
- [bun.lock](bun.lock)
- [package.json](package.json)
- [packages/lib/auth-context.tsx](packages/lib/auth-context.tsx)
- [packages/lib/error-tracking.tsx](packages/lib/error-tracking.tsx)
- [packages/lib/posthog.tsx](packages/lib/posthog.tsx)
- [packages/ui/components/dialog.tsx](packages/ui/components/dialog.tsx)

</details>



This page documents the foundational architecture of the `apps/web` Next.js application, focusing on the `RootLayout`, the hierarchical provider stack, font configuration, and global styling.

---

## RootLayout

The `RootLayout` defined in [apps/web/app/layout.tsx:64-115]() serves as the entry point for the entire web application. It is a Next.js App Router layout that wraps every page, ensuring a consistent environment for fonts, styles, and context providers.

**Key Responsibilities:**
- **HTML/Body Setup**: Configures the `<html>` and `<body>` tags with `suppressHydrationWarning` and applies global font variables [apps/web/app/layout.tsx:70-82]().
- **Development Tooling**: Injects `react-scan` for performance monitoring when `NODE_ENV` is "development" [apps/web/app/layout.tsx:72-78]().
- **Metadata**: Defines the application title, description, and base URL for SEO and social sharing [apps/web/app/layout.tsx:20-55]().
- **Viewport**: Configures mobile-responsive settings including `viewportFit: "cover"` and `interactiveWidget: "resizes-content"` [apps/web/app/layout.tsx:57-62]().
- **Toast Notifications**: Mounts the `<Toaster />` component from `@ui/components/sonner` at the root [apps/web/app/layout.tsx:104]().

**Sources:** [apps/web/app/layout.tsx:1-115]()

---

## Font & Style Configuration

### Typeface
The application uses **Space Grotesk** as its primary typeface, loaded via `next/font/google` [apps/web/app/layout.tsx:2-18]().
- **Variable**: `--font-sans`
- **Subsets**: `latin`
- **Application**: Applied to the `body` class via `${font.variable}` [apps/web/app/layout.tsx:80]().

### Global Stylesheets
The application imports two primary CSS entry points [apps/web/app/layout.tsx:3-4]():
1. `../globals.css`: Local styles specific to the web application.
2. `@ui/globals.css`: Shared global styles from the `@supermemory/ui` package.

The UI package utilizes **Tailwind CSS v4** (via `@tailwindcss/postcss`) and `tw-animate-css` [apps/web/package.json:114-129](). 

**Sources:** [apps/web/app/layout.tsx:2-18](), [apps/web/package.json:114-129]()

---

## Provider Stack

The application uses a deeply nested provider pattern to manage theme, billing, data fetching, authentication, and analytics. The order is critical as inner providers often depend on the context of outer ones (e.g., `AuthProvider` using the query client).

**Code-to-Entity Provider Hierarchy:**

Title: Web Application Provider Stack
```mermaid
graph TD
    subgraph "RootLayout (apps/web/app/layout.tsx)"
        TP["ThemeProvider (apps/web/lib/theme-provider.tsx)"]
        AP["AutumnProvider (autumn-js/react)"]
        QP["QueryProvider (apps/web/components/query-client.tsx)"]
        AUP["AuthProvider (packages/lib/auth-context.tsx)"]
        PHP["PostHogProvider (packages/lib/posthog.tsx)"]
        ETP["ErrorTrackingProvider (packages/lib/error-tracking.tsx)"]
        NA["NuqsAdapter (nuqs/adapters/next/app)"]
        SUS["Suspense (react)"]
        CHILD["{children}"]
    end

    TP --> AP
    AP --> QP
    QP --> AUP
    AUP --> PHP
    PHP --> ETP
    ETP --> NA
    NA --> SUS
    SUS --> CHILD
```

### Provider Details

| Provider | Purpose | Key Configuration |
| :--- | :--- | :--- |
| **ThemeProvider** | Manages light/dark mode using `next-themes`. | Forced to `dark` [apps/web/app/layout.tsx:83-89](). |
| **AutumnProvider** | Handles billing and subscription logic via `autumn-js`. | Points to `NEXT_PUBLIC_BACKEND_URL` or `api.supermemory.ai` [apps/web/app/layout.tsx:90-97](). |
| **QueryProvider** | Initializes the `TanStack Query` client for server state. | Wraps all data-fetching hooks [apps/web/app/layout.tsx:98](). |
| **AuthProvider** | Manages sessions and active organization state using `better-auth`. | Context provider for `useAuth` hook [apps/web/app/layout.tsx:99](), [packages/lib/auth-context.tsx:37-226](). |
| **PostHogProvider** | Client-side analytics tracking and pageview capture. | Initialized with `api_host` pointing to `/orange` proxy [packages/lib/posthog.tsx:36-75](). |
| **NuqsAdapter** | URL search param state management. | Enables type-safe query params [apps/web/app/layout.tsx:102](). |

**Sources:** [apps/web/app/layout.tsx:83-111](), [packages/lib/posthog.tsx:36-75](), [packages/lib/auth-context.tsx:37-226]()

---

## Authentication & Middleware

Authentication is handled by `better-auth`. The application uses a `middleware.ts` file to protect routes and handle redirects.

### Middleware Logic
The middleware in [apps/web/middleware.ts:12-83]() performs the following:
- **Public Paths**: Allows access to `/login`, `/login/new`, and specific views like `mcp` or `integrations` (in guest mode) [apps/web/middleware.ts:23-37]().
- **API Protection**: Returns a `401 Unauthorized` for `/api/` routes if no session cookie exists [apps/web/middleware.ts:39-49]().
- **Redirects**: Unauthenticated users trying to access private routes are redirected to `/login` with a `redirect` parameter [apps/web/middleware.ts:52-59]().

### Auth Restoration Flow
The `AuthProvider` manages the restoration of the user's active organization from `localStorage` using the key `supermemory-consumer-last-org-slug` [packages/lib/auth-context.tsx:19-177]().

Title: AuthProvider Session Restoration
```mermaid
flowchart TD
    Start["AuthProvider.useEffect() (packages/lib/auth-context.tsx)"]
    SessionCheck{"session?.session exists?"}
    Restore["setIsRestoring(true)"]
    OrgsPending{"organizations Pending?"}
    CheckStorage["Check localStorage: 'supermemory-consumer-last-org-slug'"]
    SetOrg["setOrg(fullOrg)"]
    Finish["setIsRestoring(false)"]

    Start --> SessionCheck
    SessionCheck -- No --> Finish
    SessionCheck -- Yes --> Restore
    Restore --> OrgsPending
    OrgsPending -- Yes --> Finish
    OrgsPending -- No --> CheckStorage
    CheckStorage --> SetOrg
    SetOrg --> Finish
```

**Sources:** [apps/web/middleware.ts:1-83](), [packages/lib/auth-context.tsx:19-177]()

---

## Workspace Enforcement

The `EnsureWorkspace` component [apps/web/components/ensure-workspace.tsx:19-68]() acts as a client-side guard within the `AppLayout` [apps/web/app/(app)/layout.tsx:7-14](). It monitors the `AuthProvider` state and enforces the following:
1. **Unauthenticated Users**: Redirected to `/login` with the current URL as a redirect target [apps/web/components/ensure-workspace.tsx:34-39]().
2. **New Users**: If a user is authenticated but has no organizations (`organizations.length === 0`), they are redirected to `/onboarding` [apps/web/components/ensure-workspace.tsx:41-43]().
3. **Loading State**: Displays a `WorkspaceLoadingShell` with a spinner while session or organization data is being restored [apps/web/components/ensure-workspace.tsx:53-65]().

Additionally, the `AppLayout` provides the `SettingsModalProvider` and the `PWAInstallPrompt` for mobile users [apps/web/app/(app)/layout.tsx:9-12]().

**Sources:** [apps/web/components/ensure-workspace.tsx:1-68](), [apps/web/app/(app)/layout.tsx:1-14](), [apps/web/components/pwa-install-prompt.tsx:168-232]()

---

# Page: Chat Interface

# Chat Interface

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [apps/web/app/(app)/page.tsx](apps/web/app/(app)/page.tsx)
- [apps/web/components/chat/attachments.ts](apps/web/components/chat/attachments.ts)
- [apps/web/components/chat/home-chat-composer.tsx](apps/web/components/chat/home-chat-composer.tsx)
- [apps/web/components/chat/index.tsx](apps/web/components/chat/index.tsx)
- [apps/web/components/chat/input/actions.tsx](apps/web/components/chat/input/actions.tsx)
- [apps/web/components/chat/input/chain-of-thought.tsx](apps/web/components/chat/input/chain-of-thought.tsx)
- [apps/web/components/chat/input/index.tsx](apps/web/components/chat/input/index.tsx)
- [apps/web/components/chat/message/agent-message.tsx](apps/web/components/chat/message/agent-message.tsx)
- [apps/web/components/chat/message/memory-search-result-card.tsx](apps/web/components/chat/message/memory-search-result-card.tsx)
- [apps/web/components/chat/message/related-memories.tsx](apps/web/components/chat/message/related-memories.tsx)
- [apps/web/components/chat/message/user-message.tsx](apps/web/components/chat/message/user-message.tsx)
- [apps/web/components/chat/model-selector.tsx](apps/web/components/chat/model-selector.tsx)
- [apps/web/components/chat/reasoning-selector.tsx](apps/web/components/chat/reasoning-selector.tsx)
- [apps/web/components/document-modal/content/image-preview.tsx](apps/web/components/document-modal/content/image-preview.tsx)
- [apps/web/components/document-modal/content/index.tsx](apps/web/components/document-modal/content/index.tsx)
- [apps/web/components/document-modal/content/pdf.tsx](apps/web/components/document-modal/content/pdf.tsx)
- [apps/web/components/superloader.tsx](apps/web/components/superloader.tsx)
- [apps/web/lib/chat-search-memory-results.ts](apps/web/lib/chat-search-memory-results.ts)
- [apps/web/lib/chat-web-search-tools.ts](apps/web/lib/chat-web-search-tools.ts)
- [apps/web/lib/file-cache.ts](apps/web/lib/file-cache.ts)
- [apps/web/lib/models.tsx](apps/web/lib/models.tsx)
- [apps/web/stores/chat.ts](apps/web/stores/chat.ts)
- [apps/web/stores/indexeddb-storage.ts](apps/web/stores/indexeddb-storage.ts)

</details>



## Purpose and Scope

The Chat Interface is the primary conversational surface for interacting with Nova, Supermemory's AI assistant. It enables users to ask questions and receive personalized responses that incorporate their stored memories and documents. This page documents the chat system's architecture, AI model selection, message threading, memory injection mechanism, and user interaction features.

The interface is implemented primarily in `apps/web/components/chat/index.tsx` [apps/web/components/chat/index.tsx:1-223](), utilizing the Vercel AI SDK for streaming and state management.

## Chat Activation and Entry Points

The chat interface can be triggered from multiple locations within the web application. The primary entry point is the `ChatLaunchFab` [apps/web/components/chat/index.tsx:103-143](), which renders a floating action button (FAB) containing the `NovaOrb` component.

**Chat Interface Entry Points:**

| Surface | Code Location | Component |
|---------|--------------|-----------|
| Floating Action Button | [apps/web/components/chat/index.tsx:103-143]() | `ChatLaunchFab` |
| Home Dashboard | [apps/web/app/(app)/page.tsx:15-16]() | `HomeChatComposer` |
| Mobile Navigation | [apps/web/app/(app)/page.tsx:14]() | `MobileBottomNav` |

**`HomeChatComposer` component:**
The `HomeChatComposer` [apps/web/components/chat/home-chat-composer.tsx:22-170]() provides a large, centered input area on the landing dashboard. It allows users to select a model, reasoning effort, and target space before initiating a chat session via the `onStartChat` callback [apps/web/components/chat/home-chat-composer.tsx:26-33]().

**Entry point flow diagram:**

```mermaid
graph TB
    subgraph "apps/web/app/(app)/page.tsx"
        [NewPage] --> [HomeChatComposer]
        [NewPage] --> [ChatSidebar]
        [NewPage] --> [ChatLaunchFab]
    end

    subgraph "apps/web/components/chat/index.tsx"
        [ChatSidebar] --> [ChatInput]
        [ChatSidebar] --> [ChatModelSelector]
        [ChatSidebar] --> [ReasoningSelector]
    end

    subgraph "nuqs"
        [threadParam]
    end

    [HomeChatComposer] -->|"onStartChat"| [threadParam]
    [ChatLaunchFab] -->|"onOpen"| [ChatSidebar]
```

Sources: [apps/web/app/(app)/page.tsx:109-180](), [apps/web/components/chat/index.tsx:103-143](), [apps/web/components/chat/home-chat-composer.tsx:22-34]()

## AI Model Selection and Reasoning

Nova supports multiple AI models and reasoning modes. These are defined in `apps/web/lib/models.tsx`.

### Supported Models
| Model ID | Display Name | Version | Description |
|----------|--------------|---------|-------------|
| `grok-4.3` | Grok | 4.3 | xAI's latest model [apps/web/lib/models.tsx:3-6]() |
| `gpt-5.1` | GPT | 5.1 | OpenAI's latest model [apps/web/lib/models.tsx:8-11]() |
| `claude-sonnet-4.6` | Claude | 4.6 | Anthropic's advanced model [apps/web/lib/models.tsx:13-16]() |
| `gemini-2.5-pro` | Gemini | 3 Pro | Google's most capable model [apps/web/lib/models.tsx:18-21]() |

### Reasoning Effort
Users can toggle between two reasoning modes via the `ReasoningSelector` [apps/web/components/chat/reasoning-selector.tsx:1-73]():
- **Instant**: Faster answers for everyday prompts [apps/web/lib/models.tsx:40-43]().
- **Thinking**: Deeper reasoning for harder questions [apps/web/lib/models.tsx:45-48]().

**Model data flow diagram:**

```mermaid
graph LR
    subgraph "apps/web/lib/models.tsx"
        [models] --> [ModelId]
        [reasoningOptions] --> [ReasoningEffort]
    end

    subgraph "apps/web/components/chat/model-selector.tsx"
        [ChatModelSelector]
    end

    subgraph "apps/web/components/chat/index.tsx"
        [selectedModel]
        [reasoningEffort]
    end

    [ModelId] --> [ChatModelSelector]
    [ChatModelSelector] --> [selectedModel]
    [ReasoningEffort] --> [reasoningEffort]
```

Sources: [apps/web/lib/models.tsx:1-53](), [apps/web/components/chat/model-selector.tsx:20-58](), [apps/web/components/chat/reasoning-selector.tsx:7-27]()

## Message Flow and Attachments

Conversations are managed using the `useChat` hook from `@ai-sdk/react` [apps/web/components/chat/index.tsx:9]().

### Chat Attachments
The interface supports uploading files as context for the conversation. 
- **Drafting**: `createChatAttachmentDraft` [apps/web/components/chat/attachments.ts:66]() creates a local preview.
- **Persistence**: Attachments can be toggled to `saveToMemory` [apps/web/components/chat/index.tsx:96]().
- **Caching**: Files are cached locally using `cacheFileBlob` [apps/web/lib/file-cache.ts]() to avoid re-uploading.

### Message Rendering
- **`UserMessage`**: Handles text display, attachment chips, and inline editing [apps/web/components/chat/message/user-message.tsx:31-193](). It allows switching models and reasoning effort during a regeneration [apps/web/components/chat/message/user-message.tsx:62]().
- **`AgentMessage`**: Renders AI responses with markdown support and specialized tool-call UI [apps/web/components/chat/message/agent-message.tsx:1-25]().

**Message Interaction Sequence:**

```mermaid
sequenceDiagram
    participant User
    participant ChatInput
    participant useChat
    participant API as Backend API

    User->>ChatInput: Enters text + attaches PDF
    ChatInput->>ChatInput: handleAddAttachmentFiles()
    User->>ChatInput: Clicks Send
    ChatInput->>useChat: append()
    useChat->>API: POST /api/chat (model, reasoning, attachments)
    API-->>useChat: Stream text chunks + tool calls
    useChat-->>User: Update AgentMessage UI
```

Sources: [apps/web/components/chat/index.tsx:79-101](), [apps/web/components/chat/message/user-message.tsx:102-160](), [apps/web/components/chat/message/agent-message.tsx:26-37](), [apps/web/components/chat/home-chat-composer.tsx:75-114]()

## Tool Call Visualization and Context

When the AI assistant performs actions, the `AgentMessage` component visualizes these as tool calls [apps/web/components/chat/message/agent-message.tsx:39-46]().

### Supported Tools
- **Memory Tools**: `bash` (SMFS interface), `searchMemories`, `addMemory`, `fetchMemory` [apps/web/components/chat/message/agent-message.tsx:26-37]().
- **Search Tools**: `web_search`, `google_search` [apps/web/components/chat/message/agent-message.tsx:28-29]().
- **Task Tools**: `scheduleTask`, `listSchedules`, `cancelSchedule` [apps/web/components/chat/message/agent-message.tsx:34-36]().

### Document Integration
If the AI references specific documents, the `DocumentContent` component [apps/web/components/document-modal/content/index.tsx:76-153]() handles rendering based on type:
- **PDF**: `PdfViewer` using `react-pdf` [apps/web/components/document-modal/content/pdf.tsx:21-170]().
- **Images**: `ImagePreview` with blur-up loading [apps/web/components/document-modal/content/image-preview.tsx:13-96]().
- **External**: `TweetContent`, `NotionDoc`, `YoutubeVideo`, and `GoogleDocViewer` [apps/web/components/document-modal/content/index.tsx:99-148]().

Sources: [apps/web/components/chat/message/agent-message.tsx:26-37](), [apps/web/components/document-modal/content/index.tsx:54-74](), [apps/web/components/document-modal/content/pdf.tsx:3-12]()

## Conversation Storage and Threading

Conversation state is persisted locally using `usePersistentChatStore` with IndexedDB [apps/web/stores/chat.ts:73-185]().

### Thread Management
- **Persistence**: Threads are identified by `threadId` in the URL [apps/web/app/(app)/page.tsx:160]() and stored in the `byProject` map in Zustand [apps/web/stores/chat.ts:57-71]().
- **Space Selection**: Users can scope chats to specific "Spaces" (projects) using the `SpaceSelector` [apps/web/components/chat/home-chat-composer.tsx:157-165]().
- **Auto-Space**: The `AUTO_CHAT_SPACE_ID` [apps/web/components/chat/home-chat-composer.tsx:45]() allows the AI to automatically determine the most relevant context.
- **Summaries**: The store maintains `ConversationSummary` objects containing `id`, `title`, and `lastUpdated` [apps/web/stores/chat.ts:40-44]().

**Conversation State Diagram:**

```mermaid
graph TB
    subgraph "Client State (nuqs)"
        [threadParam]
    end

    subgraph "Zustand / IndexedDB (usePersistentChatStore)"
        [byProject]
        [conversations_Record]
        [messages_UIMessage]
    end

    subgraph "Components"
        [ChatSidebar]
        [HomeChatComposer]
    end

    [threadParam] --> [ChatSidebar]
    [byProject] --> [conversations_Record]
    [conversations_Record] --> [messages_UIMessage]
    [ChatSidebar] -->|"Switch Thread"| [threadParam]
```

Sources: [apps/web/app/(app)/page.tsx:151-180](), [apps/web/components/chat/home-chat-composer.tsx:43-46](), [apps/web/components/chat/index.tsx:59-60](), [apps/web/stores/chat.ts:46-56]()

## Analytics and Error Tracking

### Interaction Tracking
The chat interface tracks several events via the `analytics` utility:
- **Model Changes**: `analytics.modelChanged({ model })` [apps/web/components/chat/model-selector.tsx:56]().
- **Message Sending**: Captured within the `useChat` submission flow.

### Error Handling
Streaming errors are caught and transformed into user-friendly copy using `getNovaChatErrorCopy` [apps/web/components/chat/index.tsx:38](), which handles common issues like rate limits or model-specific availability.

Sources: [apps/web/components/chat/model-selector.tsx:56](), [apps/web/components/chat/index.tsx:38]()

---

# Page: Memory Management

# Memory Management

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [apps/web/components/add-document/file.tsx](apps/web/components/add-document/file.tsx)
- [apps/web/components/add-document/index.tsx](apps/web/components/add-document/index.tsx)
- [apps/web/components/add-document/link.tsx](apps/web/components/add-document/link.tsx)
- [apps/web/components/add-document/note.tsx](apps/web/components/add-document/note.tsx)
- [apps/web/components/document-cards/file-preview.tsx](apps/web/components/document-cards/file-preview.tsx)
- [apps/web/components/document-cards/google-docs-preview.tsx](apps/web/components/document-cards/google-docs-preview.tsx)
- [apps/web/components/document-cards/notion-preview.tsx](apps/web/components/document-cards/notion-preview.tsx)
- [apps/web/components/document-cards/tweet-preview.tsx](apps/web/components/document-cards/tweet-preview.tsx)
- [apps/web/components/document-cards/website-preview.tsx](apps/web/components/document-cards/website-preview.tsx)
- [apps/web/components/document-cards/youtube-preview.tsx](apps/web/components/document-cards/youtube-preview.tsx)
- [apps/web/components/document-icon.tsx](apps/web/components/document-icon.tsx)
- [apps/web/components/document-modal/content/text-editor-content.tsx](apps/web/components/document-modal/content/text-editor-content.tsx)
- [apps/web/components/document-modal/index.tsx](apps/web/components/document-modal/index.tsx)
- [apps/web/components/fullscreen-note-modal.tsx](apps/web/components/fullscreen-note-modal.tsx)
- [apps/web/components/memories-grid.tsx](apps/web/components/memories-grid.tsx)
- [apps/web/components/quick-note-card.tsx](apps/web/components/quick-note-card.tsx)
- [apps/web/components/text-editor/extensions.tsx](apps/web/components/text-editor/extensions.tsx)
- [apps/web/components/text-editor/index.tsx](apps/web/components/text-editor/index.tsx)
- [apps/web/components/text-editor/slash-command.tsx](apps/web/components/text-editor/slash-command.tsx)
- [apps/web/components/timeline-view.tsx](apps/web/components/timeline-view.tsx)
- [apps/web/hooks/use-document-mutations.ts](apps/web/hooks/use-document-mutations.ts)
- [apps/web/hooks/use-full-document.ts](apps/web/hooks/use-full-document.ts)
- [apps/web/lib/url-helpers.ts](apps/web/lib/url-helpers.ts)

</details>



This page covers how the web application (`apps/web`) creates, displays, and deletes memory documents—and how documents are organized by projects and spaces. It focuses on the client-side implementation using React Query mutations, optimistic updates, and the masonry grid display.

---

## Data Model

A document (or "memory") is the core unit of storage. The TypeScript interface is derived from the `DocumentsWithMemoriesResponseSchema` [apps/web/components/memories-grid.tsx:96-97]().

| Field | Type | Description |
|---|---|---|
| `id` | `string` | Unique identifier for the document [apps/web/hooks/use-document-mutations.ts:26-26]() |
| `content` | `string` | The raw text, URL, or note content [apps/web/hooks/use-document-mutations.ts:36-36]() |
| `title` | `string` | User-provided or AI-generated title [apps/web/hooks/use-document-mutations.ts:38-38]() |
| `containerTags`| `string[]` | Scoping tags (e.g., project IDs) [apps/web/hooks/use-document-mutations.ts:40-40]() |
| `status` | `string` | Processing state (e.g., `pending`, `success`, `error`) [apps/web/hooks/use-document-mutations.ts:43-43]() |
| `type` | `string` | Category (e.g., `note`, `link`, `tweet`, `file`) [apps/web/hooks/use-document-mutations.ts:44-44]() |

Sources: [apps/web/hooks/use-document-mutations.ts:34-48](), [apps/web/components/memories-grid.tsx:75-97]()

---

## Memories Grid Implementation

The `MemoriesGrid` [apps/web/components/memories-grid.tsx:247-247]() is the primary interface for browsing memories. It uses a masonry layout via the `Masonry` component [apps/web/components/memories-grid.tsx:11-11]() to handle varying card heights and supports infinite scrolling.

### Data Fetching and Display
It utilizes `useInfiniteQuery` to fetch documents from the backend [apps/web/components/memories-grid.tsx:6-6]().
- **Filtering**: The grid supports filtering by categories such as `webpage`, `tweet`, `google_drive`, `notion`, `files`, and `mcp` [apps/web/components/memories-grid.tsx:75-83]().
- **Loading States**: A rotating label system provides feedback during data fetching [apps/web/components/memories-grid.tsx:150-172]().
- **Timeline View**: Alternatively, memories can be viewed in a `TimelineView` [apps/web/components/timeline-view.tsx:189-189]() which groups documents by time periods like "Today", "Yesterday", or specific dates [apps/web/components/timeline-view.tsx:18-35]().

### Specialized Preview Components
The grid maps documents to specialized preview components based on their metadata and type:
- **TweetPreview**: For Twitter/X content [apps/web/components/memories-grid.tsx:18-18]().
- **WebsitePreview**: For standard web links [apps/web/components/memories-grid.tsx:19-19]().
- **FilePreview**: Handles images (with blur-up loading), PDFs, and other uploads [apps/web/components/document-cards/file-preview.tsx:47-47]().
- **NotePreview**: Displays user-created markdown notes [apps/web/components/memories-grid.tsx:22-22]().

Sources: [apps/web/components/memories-grid.tsx:1-83](), [apps/web/components/timeline-view.tsx:18-189](), [apps/web/components/document-cards/file-preview.tsx:75-135]()

---

## Document Mutations & Optimistic Updates

The `useDocumentMutations` hook [apps/web/hooks/use-document-mutations.ts:224-225]() centralizes all write operations. It ensures the UI feels instantaneous by updating the React Query cache before the server responds.

### Optimistic Logic Flow
1. **Cancel & Snapshot**: In-flight queries for `["documents-with-memories"]` are cancelled to prevent race conditions, and current data is snapshotted for potential rollback [apps/web/hooks/use-document-mutations.ts:195-200]().
2. **Cache Mutation**:
    - **Add**: `addOptimisticMemoryToQueryData` prepends a temporary object with `isOptimistic: true` to the query cache [apps/web/hooks/use-document-mutations.ts:50-90]().
    - **Delete**: `removeDocumentFromQueryData` [apps/web/hooks/use-document-mutations.ts:92-95]() or `removeDocumentsFromQueryData` (for bulk) [apps/web/hooks/use-document-mutations.ts:139-142]() filters out the target IDs immediately.
3. **Settlement**: On success, queries are invalidated. On failure, the snapshot is restored using `restoreQueriesFromSnapshot` [apps/web/hooks/use-document-mutations.ts:202-210]().

### Code Entity Relationship Diagram

```mermaid
graph TD
    subgraph "TanStack Query Cache"
        Cache["QueryKey: ['documents-with-memories']"]
    end

    subgraph "useDocumentMutations Hook"
        noteMut["noteMutation"]
        linkMut["linkMutation"]
        fileMut["fileMutation"]
        delMut["deleteMutation"]
    end

    subgraph "API Operations ($fetch)"
        PostAdd["POST /v3/add"]
        DelDoc["DELETE /v3/documents/:id"]
    end

    noteMut -->|addOptimisticMemoryToQueryData| Cache
    noteMut -->|Network Call| PostAdd
    
    delMut -->|removeDocumentFromQueryData| Cache
    delMut -->|Network Call| DelDoc
    
    AddDocModal["AddDocumentModal"] --> noteMut
    AddDocModal --> fileMut
    DocumentModal["DocumentModal"] --> delMut
```
Sources: [apps/web/hooks/use-document-mutations.ts:50-245](), [apps/web/components/add-document/index.tsx:150-152](), [apps/web/components/document-modal/index.tsx:200-200]()

---

## Projects and Spaces Organization

Memories are organized into "Spaces" (projects), which act as containers for related information using `containerTags`.

### Scoping via Container Tags
Every document creation request includes a `project` (containerTag) [apps/web/hooks/use-document-mutations.ts:248-253]().
- **Contextual Context**: When adding a memory, the system resolves an `entityContext` for the space to provide better AI understanding [apps/web/hooks/use-document-mutations.ts:232-245]().
- **Space Profiles**: Each space has a profile consisting of `static` and `dynamic` traits derived from its memories, fetched via `useSpaceProfile` (see glossary for containerTag relationships).

### Space Selection and Management
The `SpaceSelector` [apps/web/components/add-document/index.tsx:21-21]() allows users to choose which project a new document should be added to. The `useProject` store [apps/web/components/add-document/index.tsx:15-15]() tracks the currently active global project, which is used as the default for new memories [apps/web/components/add-document/index.tsx:130-133]().

### Space Logic Diagram

```mermaid
flowchart LR
    subgraph "State Stores"
        useProject["useProject() Store"]
        useQuickNoteDraft["useQuickNoteDraft(project)"]
    end

    subgraph "Mutations & Hooks"
        useDocMut["useDocumentMutations"]
    end

    subgraph "UI Components"
        AddModal["AddDocumentModal"]
        QuickNote["QuickNoteCard"]
        MemoriesGrid["MemoriesGrid"]
    end

    useProject -->|selectedProject| AddModal
    useProject -->|selectedProject| useQuickNoteDraft
    useQuickNoteDraft -->|draft| QuickNote
    AddModal -->|mutate with project| useDocMut
    MemoriesGrid -->|selectedDocumentIds| useDocMut
```
Sources: [apps/web/hooks/use-document-mutations.ts:248-253](), [apps/web/components/add-document/index.tsx:121-133](), [apps/web/components/quick-note-card.tsx:50-51]()

---

## Creation Workflows

### 1. Manual Creation (AddDocumentModal)
The `AddDocumentModal` [apps/web/components/add-document/index.tsx:32-32]() provides a tabbed interface for:
- **Notes**: Direct text entry using a Tiptap-based `TextEditor` [apps/web/components/add-document/note.tsx:38-44]().
- **Links**: URL ingestion for webpages [apps/web/components/add-document/index.tsx:188-197]().
- **Files**: Multi-file upload for PDFs, images, and markdown [apps/web/components/add-document/file.tsx:10-11](). It uses a `FileContent` component to manage a queue of `pending`, `uploading`, `success`, or `error` items [apps/web/components/add-document/file.tsx:13-20]().

### 2. Quick Notes
The `QuickNoteCard` [apps/web/components/quick-note-card.tsx:43-43]() allows for rapid thought capture directly from the memories grid.
- **Draft Persistence**: Drafts are stored per-project using the `useQuickNoteDraft` store [apps/web/components/quick-note-card.tsx:51-51]().
- **Expansion**: Notes can be expanded to a larger overlay [apps/web/components/quick-note-card.tsx:67-82]() or a `FullscreenNoteModal` [apps/web/components/fullscreen-note-modal.tsx:23-23]().

### 3. Deletion
- **Single Delete**: The `DeleteButton` in the `DocumentModal` handles single document removal with a confirmation state [apps/web/components/document-modal/index.tsx:83-106]().
- **Bulk Delete**: The `MemoriesGrid` supports a selection mode where multiple documents can be selected and deleted at once via `onBulkDelete` [apps/web/components/memories-grid.tsx:234-241]().

Sources: [apps/web/components/add-document/index.tsx:82-112](), [apps/web/components/quick-note-card.tsx:43-105](), [apps/web/components/document-modal/index.tsx:83-159](), [apps/web/hooks/use-document-mutations.ts:212-212]()

---

# Page: Document Display & Search

# Document Display & Search

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [apps/web/app/(app)/settings/page.tsx](apps/web/app/(app)/settings/page.tsx)
- [apps/web/components/add-document/note.tsx](apps/web/components/add-document/note.tsx)
- [apps/web/components/bottom-nav.tsx](apps/web/components/bottom-nav.tsx)
- [apps/web/components/digests-view.tsx](apps/web/components/digests-view.tsx)
- [apps/web/components/document-modal/content/text-editor-content.tsx](apps/web/components/document-modal/content/text-editor-content.tsx)
- [apps/web/components/document-modal/index.tsx](apps/web/components/document-modal/index.tsx)
- [apps/web/components/documents-command-palette.tsx](apps/web/components/documents-command-palette.tsx)
- [apps/web/components/fullscreen-note-modal.tsx](apps/web/components/fullscreen-note-modal.tsx)
- [apps/web/components/header.tsx](apps/web/components/header.tsx)
- [apps/web/components/memories-grid.tsx](apps/web/components/memories-grid.tsx)
- [apps/web/components/org-plan-badge.tsx](apps/web/components/org-plan-badge.tsx)
- [apps/web/components/quick-note-card.tsx](apps/web/components/quick-note-card.tsx)
- [apps/web/components/settings/account.tsx](apps/web/components/settings/account.tsx)
- [apps/web/components/settings/billing.tsx](apps/web/components/settings/billing.tsx)
- [apps/web/components/settings/cancel-reasons.ts](apps/web/components/settings/cancel-reasons.ts)
- [apps/web/components/settings/connections-mcp.tsx](apps/web/components/settings/connections-mcp.tsx)
- [apps/web/components/settings/org-context.tsx](apps/web/components/settings/org-context.tsx)
- [apps/web/components/text-editor/extensions.tsx](apps/web/components/text-editor/extensions.tsx)
- [apps/web/components/text-editor/index.tsx](apps/web/components/text-editor/index.tsx)
- [apps/web/components/text-editor/slash-command.tsx](apps/web/components/text-editor/slash-command.tsx)
- [apps/web/components/timeline-view.tsx](apps/web/components/timeline-view.tsx)
- [apps/web/components/user-profile-menu.tsx](apps/web/components/user-profile-menu.tsx)
- [apps/web/hooks/use-digests.ts](apps/web/hooks/use-digests.ts)
- [apps/web/lib/search-params.ts](apps/web/lib/search-params.ts)
- [apps/web/public/images/digest/feat-fs.svg](apps/web/public/images/digest/feat-fs.svg)

</details>



This page documents how documents are displayed, browsed, and searched in the `apps/web` Next.js application. It covers the URL-driven state system that drives UI visibility, the command palette search interface, the masonry document grid, the timeline view, and the specialized cards for highlights and quick notes.

---

## URL-Driven UI State

The application uses a "URL-as-state" architecture where major modal and view states are encoded as query parameters. This is implemented using the `nuqs` library, enabling deep-linking and consistent browser history behavior.

### Parameter Definitions
All parameters are centralized in `apps/web/lib/search-params.ts`.

| Parameter | Type | Default | Purpose |
|-----------|------|---------|---------|
| `add` | `StringLiteral` | `null` | Controls `AddDocumentModal` tab (`note`, `link`, `file`, `connect`) [apps/web/lib/search-params.ts:9-14]() |
| `search` | `boolean` | `false` | Opens/closes the document search command palette [apps/web/lib/search-params.ts:16-16]() |
| `q` | `string` | `""` | The active search query string [apps/web/lib/search-params.ts:17-17]() |
| `doc` | `string` | `null` | ID of the document currently open in the `DocumentModal` [apps/web/lib/search-params.ts:18-18]() |
| `fullscreen`| `boolean` | `false` | Toggles `FullscreenNoteModal` for the text editor [apps/web/lib/search-params.ts:19-19]() |
| `view` | `StringLiteral` | `dashboard` | Main content view: `dashboard`, `graph`, `list`, `integrations`, etc. [apps/web/lib/search-params.ts:26-44]() |
| `categories`| `string[]` | `[]` | Filter for document types (e.g., `tweet`, `webpage`) [apps/web/lib/search-params.ts:58-60]() |
| `settings` | `string` | `null` | Opens the settings modal to a specific tab [apps/web/app/(app)/settings/page.tsx:17-19]() |

**Sources:** [apps/web/lib/search-params.ts:1-61](), [apps/web/app/(app)/settings/page.tsx:1-24]()

---

## Component & Parameter Wiring

The following diagram maps how specific URL parameters drive the visibility and state of high-level UI components.

**Diagram: URL Parameters to Code Entities**

```mermaid
flowchart LR
    subgraph "URL_Query_Parameters"
        addParam["'add'"]
        searchParam["'search'"]
        docParam["'doc'"]
        fullParam["'fullscreen'"]
        viewParam["'view'"]
        settingsParam["'settings'"]
    end

    subgraph "React_Components"
        AddModal["AddDocumentModal"]
        CmdPalette["DocumentsCommandPalette"]
        DocModal["DocumentModal"]
        FullNote["FullscreenNoteModal"]
        MemGrid["MemoriesGrid"]
        SettingsModal["SettingsModal"]
    end

    addParam -.->|controls| AddModal
    searchParam -.->|triggers| CmdPalette
    docParam -.->|hydrates| DocModal
    fullParam -.->|toggles| FullNote
    viewParam -.->|switches| MemGrid
    settingsParam -.->|opens| SettingsModal
```

**Sources:** [apps/web/lib/search-params.ts:1-61](), [apps/web/app/(app)/settings/page.tsx:11-20](), [apps/web/components/memories-grid.tsx:247-255]()

---

## Memories Grid & Timeline View

The application provides two primary ways to browse documents: a masonry grid and a grouped timeline.

### 1. Memories Grid
The `MemoriesGrid` component uses `masonic` for a high-performance masonry layout [apps/web/components/memories-grid.tsx:11](). It renders specialized preview cards based on the document type:
- `TweetPreview`: Renders tweets using `react-tweet` [apps/web/components/memories-grid.tsx:18]().
- `WebsitePreview`: Displays OpenGraph metadata fetched via `/api/og` [apps/web/components/memories-grid.tsx:109-144]().
- `FilePreview`: Handles images, PDFs, and code files [apps/web/components/memories-grid.tsx:21]().
- `NotePreview`: Displays markdown content created via the internal editor [apps/web/components/memories-grid.tsx:22]().
- `McpPreview` & `NotionPreview`: Specialized cards for external integrations [apps/web/components/memories-grid.tsx:31-32]().

### 2. Timeline View
The `TimelineView` groups documents by time periods (e.g., "Today", "Yesterday") and then by category [apps/web/components/timeline-view.tsx:142-187](). 
- **Grouping Logic:** It uses `getTimePeriodLabel` to calculate human-readable date strings [apps/web/components/timeline-view.tsx:18-35]().
- **Data Flow:** Documents are fetched via `useInfiniteQuery` and processed into facets (categories) like `webpage`, `tweet`, and `files` [apps/web/components/memories-grid.tsx:75-94]().

**Sources:** [apps/web/components/memories-grid.tsx:1-246](), [apps/web/components/timeline-view.tsx:1-233]()

---

## Document Detail & Editing

### Document Modal
When a document is selected (`?doc=ID`), the `DocumentModal` opens. It provides:
- **Tabs:** Switches between "Summary", "Content", and "Memories" (graph list) [apps/web/components/document-modal/index.tsx:6-22]().
- **Source Links:** Resolves original URLs for Google Docs/Sheets/Slides using `getDocumentSourceUrl` [apps/web/components/document-modal/index.tsx:35-59]().
- **Mutations:** Allows updating titles or deleting documents via `useDocumentMutations` [apps/web/components/document-modal/index.tsx:200-201](). It includes a `DeleteButton` with confirmation logic and temporary ID checking to prevent deleting documents still in processing [apps/web/components/document-modal/index.tsx:83-159]().

### Fullscreen Editor
The `FullscreenNoteModal` provides a focused writing environment using the `TextEditor` component [apps/web/components/fullscreen-note-modal.tsx:10-153]().
- **Implementation:** Built on Tiptap with markdown support [apps/web/components/text-editor/index.tsx:14-92]().
- **Persistence:** Uses `useQuickNoteDraft` to save progress to local storage/Zustand during the session [apps/web/components/fullscreen-note-modal.tsx:33-67]().
- **Keyboard Shortcuts:** Supports `Mod+Enter` for saving and `Esc` for closing [apps/web/components/fullscreen-note-modal.tsx:73-88]().

**Sources:** [apps/web/components/document-modal/index.tsx:1-205](), [apps/web/components/fullscreen-note-modal.tsx:1-226]()

---

## Dashboard & Highlights

The `DashboardView` serves as the home surface, displaying high-level context and quick actions.

### Highlights Card
The `HighlightsCard` displays AI-generated summaries and key insights from the user's knowledge base.
- **Interaction:** Users can click "Chat" to open a focused conversation about a specific highlight or "Related" to search for connected concepts [apps/web/components/memories-grid.tsx:217-221]().
- **Quick Notes:** Integrated `QuickNoteCard` allows users to save notes directly from the grid or maximize them into the fullscreen editor [apps/web/components/memories-grid.tsx:210-214]().

### Data Flow for Search & Display
```mermaid
sequenceDiagram
    participant User
    participant Header as HeaderComponent
    participant URL as NuqsSearchParams
    participant Grid as MemoriesGrid
    participant API as BackendAPI

    User->>Header: Clicks Search Icon
    Header->>URL: setOpenSearch(true)
    URL->>Grid: Triggers search UI
    User->>Grid: Enters query 'q'
    Grid->>API: Fetch documents(q, categories, project)
    API-->>Grid: Return DocumentWithMemories[]
    Grid->>User: Render Masonry items
```

**Sources:** [apps/web/components/header.tsx:68-83](), [apps/web/components/memories-grid.tsx:247-270](), [apps/web/lib/search-params.ts:16-17]()

---

## Document Search & Palette

Search is driven by the `q` parameter and the `DocumentsCommandPalette`.

1. **Search Parameter:** `qParam` in `nuqs` syncs the search input with the URL [apps/web/lib/search-params.ts:17]().
2. **Command Palette:** Triggered by `onOpenSearch` from the `Header` [apps/web/components/header.tsx:68](). It performs hybrid search across the user's documents.
3. **Filtering:** Filters are applied via `categoriesParam` and `projectParam`, which are passed to the backend API to scope the results [apps/web/lib/search-params.ts:58-61]().
4. **Mobile Navigation:** The `MobileBottomNav` provides a dedicated search trigger in the "More" dropdown for mobile users [apps/web/components/bottom-nav.tsx:110-133]().

**Sources:** [apps/web/lib/search-params.ts:1-61](), [apps/web/components/header.tsx:105-122](), [apps/web/components/bottom-nav.tsx:45-137]()

---

# Page: Integrations & Connections

# Integrations & Connections

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [apps/web/app/auth/agent-connect/page.tsx](apps/web/app/auth/agent-connect/page.tsx)
- [apps/web/app/auth/connect/page.tsx](apps/web/app/auth/connect/page.tsx)
- [apps/web/components/add-document/connections.tsx](apps/web/components/add-document/connections.tsx)
- [apps/web/components/connect-ai-modal.tsx](apps/web/components/connect-ai-modal.tsx)
- [apps/web/components/document-cards/mcp-preview.tsx](apps/web/components/document-cards/mcp-preview.tsx)
- [apps/web/components/document-cards/note-preview.tsx](apps/web/components/document-cards/note-preview.tsx)
- [apps/web/components/document-cards/plugin-preview.tsx](apps/web/components/document-cards/plugin-preview.tsx)
- [apps/web/components/document-modal/content/plugin-content.tsx](apps/web/components/document-modal/content/plugin-content.tsx)
- [apps/web/components/document-modal/title.tsx](apps/web/components/document-modal/title.tsx)
- [apps/web/components/integrations-view.tsx](apps/web/components/integrations-view.tsx)
- [apps/web/components/integrations/plugins-detail.tsx](apps/web/components/integrations/plugins-detail.tsx)
- [apps/web/components/mcp-modal/mcp-detail-view.tsx](apps/web/components/mcp-modal/mcp-detail-view.tsx)
- [apps/web/hooks/use-token-usage.ts](apps/web/hooks/use-token-usage.ts)
- [apps/web/lib/billing-utils.ts](apps/web/lib/billing-utils.ts)
- [apps/web/lib/mcp-client-setup.ts](apps/web/lib/mcp-client-setup.ts)
- [apps/web/lib/mcp-manual-instructions.ts](apps/web/lib/mcp-manual-instructions.ts)
- [apps/web/lib/plugin-catalog.ts](apps/web/lib/plugin-catalog.ts)
- [apps/web/lib/plugin-document.ts](apps/web/lib/plugin-document.ts)
- [apps/web/lib/plugin-space.ts](apps/web/lib/plugin-space.ts)
- [apps/web/public/mcp-supported-tools/antigravity.png](apps/web/public/mcp-supported-tools/antigravity.png)
- [packages/lib/queries.ts](packages/lib/queries.ts)

</details>



This document covers the external service integrations and connection management system in the Supermemory web application. It explains how users connect cloud storage providers (Google Drive, Notion, OneDrive), manage MCP (Model Context Protocol) setups via the `ConnectAIModal`, and configure programmatic access for tools like Claude Code and Raycast.

**Sources:** [apps/web/components/connect-ai-modal.tsx:1-50](), [apps/web/components/integrations-view.tsx:1-100](), [apps/web/components/add-document/connections.tsx:1-45]()

---

## Integration Architecture Overview

The integrations system distinguishes between **OAuth-based Connections** (managed via the Connections tab) and **API Key-based Plugins/MCP** (managed via the Integrations view).

### Natural Language to Code Entity Mapping

The following table maps high-level integration concepts to their implementation entities in the codebase.

| System Name | Code Entity | Purpose |
| :--- | :--- | :--- |
| **Integrations View** | `IntegrationsView` | Main hub for browsing and managing all external tools and connectors. [apps/web/components/integrations-view.tsx:1]() |
| **Connection Row** | `ConnectionRow` | UI component for individual OAuth connections with sync status and history. [apps/web/components/add-document/connections.tsx:103]() |
| **MCP Setup Modal** | `ConnectAIModal` | Handles multi-step setup for AI clients like Cursor and Claude Desktop. [apps/web/components/connect-ai-modal.tsx:126]() |
| **Plugin Registry** | `PLUGIN_CATALOG` | Defines metadata and install steps for external AI tools. [apps/web/lib/plugin-catalog.ts:31]() |
| **Auth Client** | `authClient.apiKey` | Better-auth wrapper for managing keys and metadata. [apps/web/components/connect-ai-modal.tsx:245]() |
| **Billing Guard** | `hasActivePlan` | Utility to check subscription status before allowing connection. [packages/lib/queries.ts:59]() |

**Sources:** [apps/web/components/integrations-view.tsx:155-235](), [apps/web/components/add-document/connections.tsx:103-125](), [apps/web/components/integrations/plugins-detail.tsx:26-31](), [packages/lib/queries.ts:59-64]()

### Data Flow Diagram

```mermaid
graph TD
    subgraph "Web UI [apps/web]"
        A["IntegrationsView"] -- "useQuery(['connections'])" --> B["$fetch(@get/connections/list)"]
        C["ConnectAIModal"] -- "Mutation" --> D["authClient.apiKey.create"]
        E["PluginsDetail"] -- "Mutation" --> F["fetch(/v3/auth/key)"]
        G["ConnectionRow"] -- "useTriggerSync" --> H["$fetch(@post/connections/sync)"]
    end

    subgraph "Backend Services [api.supermemory.ai]"
        B --> I["Connections API"]
        D --> J["Better-Auth / PostgreSQL"]
        F --> K["Plugin Auth Controller"]
        H --> L["Sync Worker / BullMQ"]
    end

    subgraph "External Providers"
        I --> M["Google Drive / Notion / OneDrive"]
        L --> M
    end

    subgraph "AI Clients"
        J --> N["Cursor / Claude Desktop (MCP)"]
        K --> O["Claude Code / OpenCode / Hermes"]
    end
```

**Sources:** [apps/web/components/integrations-view.tsx:3-10](), [apps/web/components/add-document/connections.tsx:3-6](), [apps/web/components/connect-ai-modal.tsx:239-250](), [apps/web/hooks/use-trigger-sync.ts:1-10]()

---

## Cloud Storage Connections

Cloud storage integrations (Google Drive, Notion, OneDrive, and Granola) use OAuth 2.0 or workspace-level syncing. These are managed in the "Connections" tab and the "Add Document" modal.

### Provider Configuration
Providers are defined in a `CONNECTORS` map which provides metadata for UI rendering.

| Provider | Title | Description |
| :--- | :--- | :--- |
| `google-drive` | Google Drive | Connect Google docs, sheets and slides |
| `notion` | Notion | Import Notion pages and databases |
| `onedrive` | OneDrive | Access Microsoft Office documents |
| `granola` | Granola | Sync AI meeting notes and transcripts |

**Sources:** [apps/web/components/add-document/connections.tsx:57-90]()

### Connection Management & Health
- **Sync Triggering**: The `useTriggerSync` hook allows users to manually initiate a refresh of their data from the UI. [apps/web/components/add-document/connections.tsx:39-39]()
- **Health Checks**: `useConnectionHealth` monitors if a connection has expired and needs re-authentication. If `needsReauth` is true, the UI displays a "Reconnect" button. [apps/web/components/add-document/connections.tsx:124-129](), [apps/web/components/add-document/connections.tsx:179-198]()
- **Sync History**: The `SyncHistoryPanel` provides visibility into past synchronization runs, including status (success/failure) and document counts. [apps/web/components/add-document/connections.tsx:37-37](), [apps/web/components/add-document/connections.tsx:93-101]()

---

## MCP & AI Client Integration (`ConnectAIModal`)

The `ConnectAIModal` provides a specialized setup flow for the Model Context Protocol (MCP), enabling Supermemory as a tool for local LLM clients.

### Supported MCP Clients
The modal and `MCPSteps` component map specialized setup instructions for various clients.

| Client Key | Name | Implementation Detail |
| :--- | :--- | :--- |
| `cursor` | Cursor | Uses `getCursorDeeplink` for one-click install. [apps/web/components/mcp-modal/mcp-detail-view.tsx:222]() |
| `claude` | Claude Desktop | Renders `Claude Desktop Manual Timeline`. [apps/web/components/mcp-modal/mcp-detail-view.tsx:32]() |
| `chatgpt` | ChatGPT | Uses `CHATGPT_REMOTE_MCP_URL`. [apps/web/lib/mcp-manual-instructions.ts:1]() |
| `mcp-url` | MCP URL | Generic SSE endpoint: `https://mcp.supermemory.ai/userId/sse`. [apps/web/components/connect-ai-modal.tsx:69]() |

**Sources:** [apps/web/components/connect-ai-modal.tsx:51-61](), [apps/web/components/integrations-view.tsx:168-235](), [apps/web/components/mcp-modal/mcp-detail-view.tsx:95-106]()

### Setup Logic
1. **API Key Generation**: For manual or one-click setups, the modal uses `authClient.apiKey.create` with metadata `{ type: "mcp-manual" }`. [apps/web/components/connect-ai-modal.tsx:239-250]()
2. **Instruction Rendering**: `getMcpClientSetup` and `getManualInstallEntry` resolve the specific JSON configuration snippets or terminal commands needed for the selected client. [apps/web/components/connect-ai-modal.tsx:34-46]()
3. **Migration**: A migration utility allows users to move documents from a legacy user-scoped MCP URL to a project-scoped container using `migrateMCPMutation`. [apps/web/components/connect-ai-modal.tsx:206-225]()

---

## Plugins & Programmatic Access

Supermemory supports "Plugins"—external tools that integrate via API keys rather than OAuth. These are managed through `IntegrationsView` and `PluginsDetail`.

### Key Generation Flow
Plugins like **Claude Code**, **OpenCode**, and **Hermes** require a specific handshake. The `AuthConnectContent` component handles the `auth/connect` route, which:
1. Validates the `callback` URL against localhost/127.0.0.1. [apps/web/app/auth/connect/page.tsx:18-29](), [apps/web/app/auth/connect/page.tsx:164-168]()
2. Checks for an active organization. [apps/web/app/auth/connect/page.tsx:169-175]()
3. Fetches a new API key from `${API_URL}/v3/auth/key` with the `client` parameter. [apps/web/app/auth/connect/page.tsx:182-184]()
4. Redirects back to the tool with the key in the query string. [apps/web/app/auth/connect/page.tsx:200-203]()

### Plugin Authentication Metadata
API keys for plugins are distinguished by their metadata during listing in `IntegrationsView`:
- `sm_type`: Must be set to `"plugin_auth"`. [apps/web/components/integrations-view.tsx:130]()
- `sm_client`: Identifies the specific tool (e.g., `"claude_code"`). [apps/web/components/integrations-view.tsx:130]()
- **Normalization**: Client IDs are normalized using `normalizePluginClientId` to match the catalog. [apps/web/components/integrations-view.tsx:134](), [apps/web/lib/plugin-catalog.ts:193]()

**Sources:** [apps/web/components/integrations-view.tsx:113-143](), [apps/web/app/auth/connect/page.tsx:119-209]()

---

## Plugin Document Handling

When memories are captured via plugins (e.g., Claude Code session turns), they are rendered using specialized logic to handle transcripts and metadata.

### Entity Relationship Diagram

```mermaid
classDiagram
    class DocumentWithMemories {
        +string source
        +Record metadata
        +Array memoryEntries
    }
    class PluginIdentity {
        +string pluginId
        +string label
        +string iconSrc
    }
    class ParsedPluginDocument {
        +string kind
        +string title
        +Array messages
        +Array artifacts
    }
    DocumentWithMemories --> PluginIdentity : "getDocumentPluginIdentity()"
    PluginIdentity --> ParsedPluginDocument : "parseTranscriptMessages()"
```

**Sources:** [apps/web/lib/plugin-document.ts:175-193](), [apps/web/lib/plugin-document.ts:224-254]()

### Space Detection
The system automatically resolves the correct "Space" or project for a plugin document by checking `containerTags` and `memoryEntries`. The `detectPluginSpace` function parses prefixes like `claudecode_` or `opencode_` to extract project IDs.

**Sources:** [apps/web/lib/plugin-space.ts:185-218](), [apps/web/lib/plugin-space.ts:155-183]()

---

## Subscription & Usage Limits

Access to integrations is gated by the `autumn-js` entitlement system.

- **Tier Verification**: `hasActivePlan` is used to verify if a user meets the `api_pro` (or higher) requirement for specific connectors. [packages/lib/queries.ts:59-64]()
- **Usage Normalization**: The `useTokenUsage` hook normalizes plan types (free, pro, max, scale, enterprise) and calculates usage percentages for tokens and search queries based on the `autumn` balances. [apps/web/hooks/use-token-usage.ts:24-32](), [apps/web/hooks/use-token-usage.ts:57-72]()
- **Plan Ranking**: Plans are ranked numerically (`PLAN_RANK`) to handle feature escalation and UI priority. [apps/web/hooks/use-token-usage.ts:16-22]()

**Sources:** [apps/web/hooks/use-token-usage.ts:1-94](), [packages/lib/queries.ts:10-57]()

---

# Page: Settings & Profile

# Settings & Profile

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [apps/web/app/(app)/settings/integrations/page.tsx](apps/web/app/(app)/settings/integrations/page.tsx)
- [apps/web/app/(app)/settings/page.tsx](apps/web/app/(app)/settings/page.tsx)
- [apps/web/components/bottom-nav.tsx](apps/web/components/bottom-nav.tsx)
- [apps/web/components/documents-command-palette.tsx](apps/web/components/documents-command-palette.tsx)
- [apps/web/components/header.tsx](apps/web/components/header.tsx)
- [apps/web/components/integrations/chrome-detail.tsx](apps/web/components/integrations/chrome-detail.tsx)
- [apps/web/components/integrations/raycast-detail.tsx](apps/web/components/integrations/raycast-detail.tsx)
- [apps/web/components/integrations/raycast-setup-modal.tsx](apps/web/components/integrations/raycast-setup-modal.tsx)
- [apps/web/components/integrations/shortcuts-detail.tsx](apps/web/components/integrations/shortcuts-detail.tsx)
- [apps/web/components/org-plan-badge.tsx](apps/web/components/org-plan-badge.tsx)
- [apps/web/components/settings/account.tsx](apps/web/components/settings/account.tsx)
- [apps/web/components/settings/billing.tsx](apps/web/components/settings/billing.tsx)
- [apps/web/components/settings/cancel-reasons.ts](apps/web/components/settings/cancel-reasons.ts)
- [apps/web/components/settings/connections-mcp.tsx](apps/web/components/settings/connections-mcp.tsx)
- [apps/web/components/settings/integrations.tsx](apps/web/components/settings/integrations.tsx)
- [apps/web/components/settings/org-context.tsx](apps/web/components/settings/org-context.tsx)
- [apps/web/components/settings/settings-content.tsx](apps/web/components/settings/settings-content.tsx)
- [apps/web/components/settings/settings-modal.tsx](apps/web/components/settings/settings-modal.tsx)
- [apps/web/components/settings/support.tsx](apps/web/components/settings/support.tsx)
- [apps/web/components/user-profile-menu.tsx](apps/web/components/user-profile-menu.tsx)
- [apps/web/hooks/use-account-settings.ts](apps/web/hooks/use-account-settings.ts)
- [apps/web/hooks/use-delete-organization.ts](apps/web/hooks/use-delete-organization.ts)
- [apps/web/public/images/plugins/cursor.png](apps/web/public/images/plugins/cursor.png)
- [packages/lib/auth.ts](packages/lib/auth.ts)

</details>



This page documents the user settings and profile management systems in supermemory, including the multi-tab settings structure, onboarding profile configuration, and the underlying authentication, organization context, and billing integrations.

---

## Settings Interface

The settings experience is a modal-driven interface accessible via the `?settings=<tab>` URL state [apps/web/app/(app)/settings/page.tsx:8-10](). The global state for this modal is managed via the `useSettingsModal` hook, which is consumed by the `Header` and `MobileBottomNav` to trigger the view [apps/web/components/header.tsx:77](), [apps/web/components/bottom-nav.tsx:27]().

### Tab Structure

The settings interface is organized into functional areas defined in the `TABS` constant [apps/web/components/settings/settings-content.tsx:42-49]().

| Tab | Component | Description |
|-----|-----------|-------------|
| **Account** | `Account` | Team management, roles (Owner, Admin, Member), and organization context prompts [apps/web/components/settings/account.tsx:134](). |
| **Billing** | `Billing` | Plan management (Free, Pro, Max, Scale), credit balance, and auto-topup configuration [apps/web/components/settings/billing.tsx:126-210](). |
| **Integrations** | `Integrations` | Setup for Browser Extension, Raycast, and iOS Shortcuts [apps/web/components/settings/integrations.tsx:116](). |
| **Connections** | `ConnectionsMCP` | External data sync (Google Drive, Notion, etc.) and MCP client setup [apps/web/components/settings/connections-mcp.tsx:55-80](). |
| **Support** | `Support` | Help resources, Discord community links, and feedback mechanisms [apps/web/components/settings/support.tsx](). |

### Implementation Detail: URL State
The `SettingsRedirect` component handles legacy `/settings#tab` paths by parsing the hash and replacing it with the query parameter format `/?settings=tab` [apps/web/app/(app)/settings/page.tsx:11-20](). The `parseHashToTab` function ensures that only valid `SettingsTab` values are used [apps/web/components/settings/settings-content.tsx:91-96]().

**Sources:** [apps/web/app/(app)/settings/page.tsx:1-24](), [apps/web/components/settings/settings-content.tsx:42-89](), [apps/web/components/header.tsx:68-105]()

---

## Authentication & Workspace Management

supermemory utilizes the `useAuth` hook (built on `better-auth`) to manage user sessions and the "Active Organization" context, which acts as the primary scoping mechanism for memories.

### User Profile & Display
User information is displayed in the `UserProfileMenu` and the `IdentityCard` within settings [apps/web/components/user-profile-menu.tsx:22](), [apps/web/components/settings/settings-content.tsx:98]().
- **Initials Generation**: The `initials` logic extracts the first letters of the name or email for the avatar fallback [apps/web/components/user-profile-menu.tsx:65-74]().
- **Avatar Color**: A deterministic palette is used based on the user's email hash [apps/web/components/user-profile-menu.tsx:76-92]().

### Workspace Switching
The `SettingsOrgSwitcher` and the `Header` dropdown allow users to switch between different organizations [apps/web/components/settings/settings-content.tsx:239](), [apps/web/components/header.tsx:107](). Switching triggers `setActiveOrg`, which updates the session and reloads the application to ensure data consistency [apps/web/components/header.tsx:100-103]().

**Sources:** [apps/web/components/user-profile-menu.tsx:63-93](), [apps/web/components/header.tsx:69-103](), [apps/web/components/settings/settings-content.tsx:124-183]()

---

## Account & Team Management

The `Account` component provides the interface for managing organization-level configuration and team collaboration.

### Team Roles & Invitations
Organizations support hierarchical roles: `owner`, `admin`, and `member` [apps/web/components/settings/account.tsx:78-82]().
- **Restricted Access**: Admins can invite members with "Restricted" access, scoping their permissions to specific `containerTags` (projects) [apps/web/components/settings/account.tsx:143-148]().
- **Invitations**: Handled via `inviteMemberMutation`, which uses the `authClient.organization.inviteMember` method [apps/web/components/settings/account.tsx:228-245]().

### Organization Context
The `OrgContext` component allows users to define a custom prompt (up to 750 characters) that guides the AI (Nova) on what to focus on or extract during memory creation [apps/web/components/settings/org-context.tsx:22-48]().

```mermaid
graph TD
    subgraph "Organization Configuration [apps/web/components/settings/org-context.tsx]"
        UI["OrgContext Textarea"] --> UpdateHook["useUpdateOrgSettings()"]
        UpdateHook --> API["PATCH /v3/organization/settings"]
        API --> DB["Drizzle Store (shouldLLMFilter, filterPrompt)"]
    end

    subgraph "Team Management [apps/web/components/settings/account.tsx]"
        InviteUI["Invite Dialog"] --> InviteMut["inviteMemberMutation"]
        InviteMut --> B_Auth["Better-Auth API"]
        B_Auth --> MemberTable["Organization Memberships"]
    end
```

**Sources:** [apps/web/components/settings/account.tsx:134-210](), [apps/web/components/settings/org-context.tsx:48-88](), [apps/web/components/settings/org-context.tsx:89-127]()

---

## Integrations & Connections

The settings interface facilitates the connection of external data sources and the configuration of Model Context Protocol (MCP) clients.

### Connection Management
The `ConnectionsMCP` component manages synchronization for various providers [apps/web/components/settings/connections-mcp.tsx:55-80]():
- **Providers**: Google Drive, Notion, OneDrive, and Granola.
- **Metadata**: Tracks `syncInProgress`, `lastSyncedAt`, and `documentCount` [apps/web/components/settings/connections-mcp.tsx:45-53]().
- **Health**: Uses `useConnectionHealth` to detect expired OAuth tokens that require re-authentication [apps/web/components/settings/connections-mcp.tsx:189-195]().

### Integration Setup
The `Integrations` component handles the setup of client-side tools [apps/web/components/settings/integrations.tsx:116]():
- **Browser Extension**: Deep-links to the Chrome Web Store [apps/web/components/settings/integrations.tsx:213-217]().
- **iOS Shortcuts**: Generates API keys specifically tagged with `type: "ios-shortcut"` for use in mobile workflows [apps/web/components/settings/integrations.tsx:145-154]().
- **Raycast**: Provides a setup modal and generates API keys with `type: "raycast-extension"` [apps/web/components/settings/integrations.tsx:170-188]().

```mermaid
graph LR
    subgraph "Integrations Flow [apps/web/components/settings/integrations.tsx]"
        ShortcutBtn["Add Shortcut"] --> KeyMut["createApiKeyMutation"]
        KeyMut --> API_Key["authClient.apiKey.create"]
        API_Key --> KeyDisplay["Show API Key Modal"]
    end

    subgraph "Sync Flow [apps/web/components/settings/connections-mcp.tsx]"
        SyncBtn["Trigger Sync"] --> SyncHook["useTriggerSync()"]
        SyncHook --> Backend["POST /v3/connections/sync"]
        Backend --> MetaUpdate["Update Connection Metadata"]
    end
```

**Sources:** [apps/web/components/settings/connections-mcp.tsx:42-83](), [apps/web/components/settings/integrations.tsx:116-168](), [apps/web/components/settings/connections-mcp.tsx:211-245]()

---

## Billing & Plan Configuration

The `Billing` component integrates with **Autumn JS** for usage tracking and plan management [apps/web/components/settings/billing.tsx:4-16]().

### Plan Hierarchy
Plans are ranked to determine feature availability and credit allocations [apps/web/components/settings/billing.tsx:204-210]():
1. **Free**: Includes $5 initial credits [apps/web/components/settings/billing.tsx:128-140]().
2. **Pro**: Includes $20 credits and basic connectors [apps/web/components/settings/billing.tsx:141-156]().
3. **Max**: Includes $130 credits and Gmail connector [apps/web/components/settings/billing.tsx:159-170]().
4. **Scale**: Includes $600 credits, S3, and Web Crawler [apps/web/components/settings/billing.tsx:171-185]().
5. **Enterprise**: Custom deployments and unlimited credits [apps/web/components/settings/billing.tsx:186-202]().

### Usage & Top-ups
- **Credit Feature**: Credits are tracked via the `usd_credits` feature ID [apps/web/components/settings/billing.tsx:73]().
- **Auto Top-up**: Users can configure the `AutoTopupConfig` to automatically purchase credits when the balance hits a threshold [apps/web/components/settings/billing.tsx:92-102]().
- **Invoices**: Recent billing history is fetched and displayed with links to hosted Stripe invoices [apps/web/components/settings/billing.tsx:82-90]().

**Sources:** [apps/web/components/settings/billing.tsx:126-210](), [apps/web/hooks/use-token-usage.ts](), [apps/web/components/user-profile-menu.tsx:35-46]()

---

# Page: State Management

# State Management

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [apps/web/app/(app)/layout.tsx](apps/web/app/(app)/layout.tsx)
- [apps/web/components/ensure-workspace.tsx](apps/web/components/ensure-workspace.tsx)
- [apps/web/components/pwa-install-prompt.tsx](apps/web/components/pwa-install-prompt.tsx)
- [apps/web/hooks/use-container-tags.ts](apps/web/hooks/use-container-tags.ts)
- [apps/web/hooks/use-project-mutations.ts](apps/web/hooks/use-project-mutations.ts)
- [apps/web/middleware.ts](apps/web/middleware.ts)
- [apps/web/stores/chat.ts](apps/web/stores/chat.ts)
- [apps/web/stores/index.ts](apps/web/stores/index.ts)
- [apps/web/stores/indexeddb-storage.ts](apps/web/stores/indexeddb-storage.ts)
- [packages/lib/api.ts](packages/lib/api.ts)
- [packages/lib/auth-context.tsx](packages/lib/auth-context.tsx)
- [packages/lib/types.ts](packages/lib/types.ts)
- [packages/ui/components/dialog.tsx](packages/ui/components/dialog.tsx)
- [packages/validation/api.ts](packages/validation/api.ts)

</details>



This page documents the client-side state architecture of the Supermemory web application, including persistent Zustand stores, server state synchronization via React Query, and the central authentication context.

## State Architecture Overview

The application employs a layered state management strategy to balance performance, persistence, and developer experience.

```mermaid
graph TB
    subgraph "Application_State_Layers"
        URL["URL_State<br/>nuqs/NuqsAdapter"]
        Local["Local_Component_State<br/>useState/useChat"]
        Zustand["Zustand_Stores<br/>Persistent_Client_State"]
        Context["React_Context<br/>AuthProvider"]
        ReactQuery["TanStack_Query<br/>Server_State_Cache"]
        IndexedDB["IndexedDB<br/>Persistent_Storage"]
    end
    
    subgraph "Data_Sources"
        Backend["Supermemory_API"]
        AuthService["Better_Auth_Client"]
    end
    
    Local --> URL
    Zustand --> IndexedDB
    ReactQuery --> Backend
    Context --> AuthService
    
    style Zustand stroke-width:2px
    style ReactQuery stroke-width:2px
    style Context stroke-width:2px
```

**Sources:** [apps/web/stores/chat.ts:73-185](), [apps/web/stores/index.ts:8-40](), [packages/lib/auth-context.tsx:35-37]()

## Authentication Context

The `AuthProvider` serves as the root of the application's identity state, wrapping the `better-auth` client. It manages user sessions, active organizations, and restoration logic.

### Organization Management
The context tracks the `activeOrganizationId` from the session and synchronizes it with a local `Organization` object. It uses `localStorage` (key: `supermemory-consumer-last-org-slug`) to persist the user's last selected organization across sessions [packages/lib/auth-context.tsx:19-21]().

*   **Restoration Logic:** On mount, the provider attempts to restore the organization from `localStorage` or defaults to the first available organization if only one exists [packages/lib/auth-context.tsx:112-171]().
*   **Metadata Updates:** `updateOrgMetadata` allows for optimistic or partial updates to organization-specific settings without a full refetch [packages/lib/auth-context.tsx:75-86]().

**Sources:** [packages/lib/auth-context.tsx:1-234]()

## Zustand Store Architecture

Supermemory uses Zustand for persistent client-side state. The primary store is the `usePersistentChatStore`, which manages chat history across different projects.

### Persistent Chat Store

The chat store is partitioned by `projectId` (container tag) to ensure conversations are scoped correctly. It utilizes a custom `indexedDBStorage` engine to handle large message histories that might exceed `localStorage` limits.

```mermaid
graph TD
    subgraph "usePersistentChatStore_State"
        ByProject["byProject: Record&lt;string, ProjectConversationsState&gt;"]
    end

    subgraph "ProjectConversationsState"
        CurrentID["currentChatId: string | null"]
        Convs["conversations: Record&lt;string, ConversationRecord&gt;"]
    end

    subgraph "ConversationRecord"
        Msgs["messages: UIMessage[]"]
        Title["title?: string"]
        Updated["lastUpdated: string"]
    end

    ByProject --> ProjectConversationsState
    ProjectConversationsState --> Convs
    Convs --> ConversationRecord
```

| Function | Description | File Reference |
| :--- | :--- | :--- |
| `setConversation` | Updates messages for a specific chat ID, checking for deep equality via `areUIMessageArraysEqual` before triggering a state update. | [apps/web/stores/chat.ts:93-136]() |
| `setCurrentChatId` | Updates the active chat ID for the specified project. | [apps/web/stores/chat.ts:78-91]() |
| `areUIMessageArraysEqual` | Optimized deep equality check for AI SDK `UIMessage` objects to prevent redundant renders and writes. | [apps/web/stores/chat.ts:10-38]() |
| `usePersistentChat` | A convenience hook that automatically scopes store actions to the `selectedProject` from `useProject`. | [apps/web/stores/chat.ts:190-265]() |

**Sources:** [apps/web/stores/chat.ts:1-265](), [apps/web/stores/index.ts:42-42]()

### IndexedDB Persistence Layer

The `indexedDBStorage` implementation (used by `persist` middleware) handles asynchronous reads and writes to the browser's IndexedDB.

```mermaid
sequenceDiagram
    participant Store as "usePersistentChatStore"
    participant Storage as "indexedDBStorage"
    participant IDB as "IndexedDB (idb-keyval)"
    
    Store->>Storage: getItem("supermemory-chats")
    Storage->>IDB: get("supermemory-chats")
    IDB-->>Store: current_state
    
    Note over Store, IDB: On state change
    Store->>Storage: setItem("supermemory-chats", next_state)
    Storage->>IDB: set("supermemory-chats", next_state)
```

**Sources:** [apps/web/stores/chat.ts:180-184](), [apps/web/stores/indexeddb-storage.ts:1-24]()

## Server State with React Query

Server-side data is managed using `@tanstack/react-query`. This handles caching, invalidation, and optimistic updates for resources like projects and memories.

### Project Mutations

The `useProjectMutations` hook encapsulates logic for modifying project state on the server while keeping the client UI and URL state in sync.

*   **Creation:** `createProjectMutation` calls `@post/projects`, invalidates project queries, and automatically updates the selected project in the URL state via `setSelectedProjects` [apps/web/hooks/use-project-mutations.ts:21-50]().
*   **Deletion:** `deleteProjectMutation` handles removing projects and cleanup of local selection state if the deleted project was active [apps/web/hooks/use-project-mutations.ts:52-105]().
*   **Updating:** `updateProjectMutation` implements optimistic updates, modifying the query cache for `["projects"]` and `["container-tags"]` before the network request completes [apps/web/hooks/use-project-mutations.ts:182-255]().

**Sources:** [apps/web/hooks/use-project-mutations.ts:16-255](), [packages/lib/api.ts:253-259]()

## URL State (Search Parameters)

The application heavily utilizes URL state for navigation and filtering, managed by `nuqs`.

*   **Project Selection:** The `useProject` hook synchronizes the `project` URL parameter with the application's effective container tags used for API requests. It defaults to `DEFAULT_PROJECT_ID` if no project is selected [apps/web/stores/index.ts:8-40]().
*   **Navigation Safety:** The `EnsureWorkspace` component acts as a state gate, checking for an active session and organization before allowing access to app routes. If state is missing, it redirects to `/login` or `/onboarding` [apps/web/components/ensure-workspace.tsx:19-68]().

**Sources:** [apps/web/stores/index.ts:8-40](), [apps/web/components/ensure-workspace.tsx:19-68]()

## PWA and Device State

The application tracks environmental state to provide a native-like experience.

*   **PWA Install Prompt:** Tracks `BeforeInstallPromptEvent` and device info (iOS vs Android) to show contextual installation instructions [apps/web/components/pwa-install-prompt.tsx:168-198]().
*   **Dismissal State:** Persists user dismissal of the PWA prompt in `localStorage` under `pwa-install-dismissed` for a duration of 7 days [apps/web/components/pwa-install-prompt.tsx:11-13]().

**Sources:** [apps/web/components/pwa-install-prompt.tsx:1-232]()

---

# Page: Onboarding Flow

# Onboarding Flow

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [apps/web/.env.example](apps/web/.env.example)
- [apps/web/app/(app)/brain-home/page.tsx](apps/web/app/(app)/brain-home/page.tsx)
- [apps/web/app/(app)/onboarding/[...slug]/page.tsx](apps/web/app/(app)/onboarding/[...slug]/page.tsx)
- [apps/web/app/(app)/onboarding/page.tsx](apps/web/app/(app)/onboarding/page.tsx)
- [apps/web/app/api/onboarding/extract-content/route.ts](apps/web/app/api/onboarding/extract-content/route.ts)
- [apps/web/app/api/onboarding/research/route.ts](apps/web/app/api/onboarding/research/route.ts)
- [apps/web/components/brain-home/data.ts](apps/web/components/brain-home/data.ts)
- [apps/web/components/brain-home/widgets.tsx](apps/web/components/brain-home/widgets.tsx)
- [apps/web/components/initial-header.tsx](apps/web/components/initial-header.tsx)
- [apps/web/components/onboarding-brain/onboarding-confetti.tsx](apps/web/components/onboarding-brain/onboarding-confetti.tsx)
- [apps/web/components/onboarding-brain/shell.tsx](apps/web/components/onboarding-brain/shell.tsx)
- [apps/web/components/onboarding-brain/step-about.tsx](apps/web/components/onboarding-brain/step-about.tsx)
- [apps/web/components/onboarding-brain/step-ingest.tsx](apps/web/components/onboarding-brain/step-ingest.tsx)
- [apps/web/components/onboarding-brain/step-sources.tsx](apps/web/components/onboarding-brain/step-sources.tsx)
- [apps/web/components/onboarding-brain/step-team.tsx](apps/web/components/onboarding-brain/step-team.tsx)
- [apps/web/lib/analytics.ts](apps/web/lib/analytics.ts)
- [apps/web/lib/constants.ts](apps/web/lib/constants.ts)
- [packages/hooks/use-org-onboarding.ts](packages/hooks/use-org-onboarding.ts)

</details>



## Purpose and Scope

The onboarding flow is a sophisticated, multi-step system designed to initialize a user's workspace (Organization), configure their identity, and establish initial data connections. It bridges the gap between a raw authenticated session and a fully functional memory environment by automating organization creation, user profile enrichment via AI, and integration setup for tools like the Browser Extension, MCP, and external connectors (Google Drive, Notion, etc.).

---

## Onboarding Architecture

The onboarding system is primarily contained within `apps/web/app/(app)/onboarding/` and uses a centralized state machine approach managed by the `BrainOnboardingPage`.

### Core Components and Layouts

| Component | File Path | Role |
|:---|:---|:---|
| `BrainOnboardingPage` | [apps/web/app/(app)/onboarding/page.tsx:41-41]() | Main controller; manages step state, `localStorage` persistence, and organization creation. |
| `BrainShell` | [apps/web/components/onboarding-brain/shell.tsx:15-15]() | Visual wrapper providing the layout, background gradients, and the `StepIndicator`. |
| `StepIndicator` | [apps/web/components/onboarding-brain/shell.tsx:75-75]() | Renders progress dots and labels defined in `BRAIN_STEPS`. |
| `StepAbout` | [apps/web/components/onboarding-brain/step-about.tsx:58-58]() | Collects user name, workspace name, and "about" context. |
| `StepSources` | [apps/web/components/onboarding-brain/step-sources.tsx:225-225]() | Configures integrations (Google Drive, Notion, Browser Extension). |
| `StepIngest` | [apps/web/components/onboarding-brain/step-ingest.tsx:108-108]() | Handles MCP setup and tool selection (Cursor, Claude Code, etc.). |
| `StepTeam` | [apps/web/components/onboarding-brain/step-team.tsx:1-1]() | Handles team invitations and visibility settings. |

Sources: [apps/web/app/(app)/onboarding/page.tsx:7-34](), [apps/web/components/onboarding-brain/shell.tsx:7-13]()

---

## Data Flow and Persistence

The onboarding state is persisted in `localStorage` under the key `supermemory-brain-onboarding-v1` [apps/web/app/(app)/onboarding/page.tsx:36-36](). This ensures users can resume if they refresh or navigate away.

### Workspace Initialization Sequence
1. **Detection**: `detectModeFromEmail`, `workspaceNameFromEmail`, and `workspaceDomainFromEmail` suggest initial values based on the user's email domain [apps/web/app/(app)/onboarding/page.tsx:54-65]().
2. **Organization Creation**: Triggered in `handleAboutContinue`. The `ensureOrg` function calls `authClient.organization.create` with metadata including `brainMode` and `brainContainerTag` [apps/web/app/(app)/onboarding/page.tsx:195-213]().
3. **User Profile Update**: `authClient.updateUser` is called to sync the user's display name and generate a username [apps/web/app/(app)/onboarding/page.tsx:215-221]().

### Technical Entity Mapping

```mermaid
graph TD
    UI["BrainOnboardingPage (page.tsx)"] -- "authClient.organization.create" --> DB_Org["Organization Entity"]
    UI -- "authClient.updateUser" --> DB_User["User Profile"]
    
    subgraph "Onboarding State"
        About["StepAbout Values"]
        Sources["StepSources Values"]
        Team["StepTeam Values"]
    end
    
    About --> Metadata["Org Metadata (brainMode, brainContainerTag)"]
    Metadata --> DB_Org
    
    subgraph "External Logic"
        Research["/api/onboarding/research"]
        Exa["/api/onboarding/extract-content"]
    end
    
    About -- "X/Twitter Handle" --> Research
    Research -- "grok-4-fast" --> ProfileContext["brainAbout Context"]
```

Sources: [apps/web/app/(app)/onboarding/page.tsx:195-237](), [apps/web/app/api/onboarding/research/route.ts:65-109]()

---

## Integration and Sources Step

The `StepSources` component handles both OAuth-based connectors and client-side tool installation [apps/web/components/onboarding-brain/step-sources.tsx:225-232]().

### Supported Integrations
- **Cloud Connectors**: Google Drive, Notion, OneDrive, Gmail [apps/web/components/onboarding-brain/step-sources.tsx:114-119]().
- **Developer Tools**: GitHub, MCP (Model Context Protocol).
- **Browsing/Shortcuts**: Chrome Extension, Raycast Extension, Apple Shortcuts [apps/web/components/onboarding-brain/step-sources.tsx:122-124]().

### Plan-Gated Features
Certain connectors are gated by user plans (Pro, Max, Scale). For example, the Gmail connector is noted as a "Max" plan feature [apps/web/components/onboarding-brain/step-sources.tsx:180-180](), while S3 and Web Crawler are "Scale" features [apps/web/components/onboarding-brain/step-sources.tsx:193-193]().

Sources: [apps/web/components/onboarding-brain/step-sources.tsx:114-213]()

---

## MCP and Tool Setup

The `StepIngest` component allows users to connect their memory to external agents via the Model Context Protocol (MCP) [apps/web/components/onboarding-brain/step-ingest.tsx:108-108]().

### Agent Catalog
The system provides tailored setup instructions for various agents:
- **Coding**: Cursor, Claude Code, VS Code, Cline, Codex, Gemini CLI [apps/web/components/onboarding-brain/step-ingest.tsx:41-79]().
- **Productivity**: Claude Desktop, ChatGPT [apps/web/components/onboarding-brain/step-ingest.tsx:81-92]().

### Setup Logic
- **Universal URL**: Users are provided with a `Universal MCP URL` to copy into their agent configuration [apps/web/components/onboarding-brain/step-ingest.tsx:243-247]().
- **Embedded Instructions**: Uses `MCPSteps` from the MCP modal to show step-by-step setup guides [apps/web/components/onboarding-brain/step-ingest.tsx:183-183]().

Sources: [apps/web/components/onboarding-brain/step-ingest.tsx:33-106](), [apps/web/components/onboarding-brain/step-ingest.tsx:209-253]()

---

## AI-Powered Profile Enrichment

Supermemory uses AI during onboarding to research users and extract content to provide an immediate "populated" feel.

### Research API
The route `/api/onboarding/research` uses the `xai` provider with the `grok-4-fast` model [apps/web/app/api/onboarding/research/route.ts:93-94]().
- **Input**: X (Twitter) URL or handle [apps/web/app/api/onboarding/research/route.ts:67-76]().
- **Tools**: It utilizes `xai.tools.webSearch()` and `xai.tools.xSearch()` to analyze the user's professional background and interests [apps/web/app/api/onboarding/research/route.ts:96-101]().

### Content Extraction
The `/api/onboarding/extract-content` route interfaces with the **Exa API** [apps/web/app/api/onboarding/extract-content/route.ts:44-55](). It takes an array of URLs and returns cleaned text and metadata using the `livecrawl: "fallback"` mode [apps/web/app/api/onboarding/extract-content/route.ts:50-54]().

Sources: [apps/web/app/api/onboarding/research/route.ts:93-102](), [apps/web/app/api/onboarding/extract-content/route.ts:19-55]()

---

## Completion and Tracking

### Tracking Progress
Progress is tracked via the `analytics` utility, capturing events for every step viewed or completed:
- `onboardingStarted`: Triggered on mount [apps/web/app/(app)/onboarding/page.tsx:115-118]().
- `onboardingStepViewed`: Triggered whenever the `step` state changes [apps/web/app/(app)/onboarding/page.tsx:133-137]().
- `onboardingStepCompleted`: Triggered when `goNext` is called [apps/web/app/(app)/onboarding/page.tsx:183-183]().

### Final Transition
The `finish` function in `BrainOnboardingPage` clears the local storage and redirects the user to the home dashboard with the success flag `?onboarded=1` [apps/web/app/(app)/onboarding/page.tsx:166-179](). This flag triggers the `OnboardingConfetti` component [apps/web/components/onboarding-brain/onboarding-confetti.tsx:13-15]().

### Skip Logic
Users can bypass the flow via `InitialHeader` which calls `markOrgOnboarded` [apps/web/components/initial-header.tsx:23-27](). If a `PENDING_CONNECT_URL_KEY` exists in `sessionStorage`, the user is redirected back to their original plugin connection intent [apps/web/lib/constants.ts:17-28]().

```mermaid
sequenceDiagram
    participant User
    participant Web as apps/web/onboarding
    participant Auth as @lib/auth
    participant Analytics as @lib/analytics
    
    User->>Web: Complete Steps
    Web->>Analytics: onboardingStepCompleted
    Web->>Auth: authClient.organization.create
    Web->>Analytics: onboardingCompleted
    Web->>Web: localStorage.removeItem(STORAGE_KEY)
    Web->>User: Redirect to /?onboarded=1
```

Sources: [apps/web/app/(app)/onboarding/page.tsx:166-190](), [apps/web/lib/analytics.ts:121-179](), [apps/web/components/initial-header.tsx:23-27]()

---

# Page: Cloudflare Deployment

# Cloudflare Deployment

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitignore](.gitignore)
- [apps/web/.gitignore](apps/web/.gitignore)
- [apps/web/app/global-error.tsx](apps/web/app/global-error.tsx)
- [apps/web/app/layout.tsx](apps/web/app/layout.tsx)
- [apps/web/components/next-app-research-cta.tsx](apps/web/components/next-app-research-cta.tsx)
- [apps/web/instrumentation-client.ts](apps/web/instrumentation-client.ts)
- [apps/web/lib/chat-stream-error.ts](apps/web/lib/chat-stream-error.ts)
- [apps/web/next.config.ts](apps/web/next.config.ts)
- [apps/web/package.json](apps/web/package.json)
- [apps/web/public/OG.png](apps/web/public/OG.png)
- [apps/web/tsconfig.json](apps/web/tsconfig.json)
- [apps/web/wrangler.jsonc](apps/web/wrangler.jsonc)
- [bun.lock](bun.lock)
- [package.json](package.json)

</details>



This page documents how `apps/web` (the Next.js consumer application) is built and deployed to Cloudflare using the `@opennextjs/cloudflare` adapter. It covers the adapter setup, environment variable typing with `cf-typegen`, and the specific build, deploy, and upload scripts.

---

## Overview

The `apps/web` application is a Next.js project designed to run on Cloudflare's edge infrastructure (Workers and Pages) rather than a standard Node.js environment. This is achieved using the `@opennextjs/cloudflare` adapter, which transforms the Next.js build output into a format compatible with the `workerd` runtime.

The core dependency for this integration is defined in the workspace configuration:
- `@opennextjs/cloudflare`: [apps/web/package.json:34-34]()
- `wrangler`: [apps/web/package.json:131-131]() (Dev dependency for CLI operations)

To support the deployment, the project uses the `wrangler.jsonc` configuration file [apps/web/wrangler.jsonc:1-32]() to define bindings, compatibility flags, and R2 bucket associations.

---

## Build and Deploy Pipeline

The deployment process involves wrapping the standard `next build` with the OpenNext adapter to generate a Cloudflare-ready bundle in the `.open-next/` directory.

### Deployment Flow Diagram

```mermaid
flowchart TD
  subgraph "Source_Space"
    SRC["Next.js Source\n(apps/web)"]
  end

  subgraph "Build_Space_Local_CI"
    NB["next build\n(apps/web/package.json:12)"]
    ONB["opennextjs-cloudflare build\n(Adapter Transformation)"]
    ART[".open-next/ output\n(apps/web/.gitignore:2)"]
  end

  subgraph "Cloudflare_Space"
    CW["Cloudflare Worker\n(Runtime: workerd)"]
    CA["Cloudflare Assets\n(Static Files: .open-next/assets)"]
    R2["R2 Bucket\n(supermemory-console-cache)"]
  end

  SRC --> NB
  NB --> ONB
  ONB --> ART
  ART -->|"opennextjs-cloudflare deploy"| CW
  ART -->|"opennextjs-cloudflare upload"| CA
  CW -.->|"NEXT_INC_CACHE_R2_BUCKET"| R2
```

Sources: [apps/web/package.json:12-17](), [apps/web/wrangler.jsonc:14-30](), [apps/web/.gitignore:2-2]()

### Deployment Scripts

The following scripts in `apps/web/package.json` manage the lifecycle of the Cloudflare application:

| Script | Command | Description |
| :--- | :--- | :--- |
| `build` | `next build` | Standard Next.js production build. [apps/web/package.json:12-12]() |
| `preview` | `opennextjs-cloudflare build && opennextjs-cloudflare preview` | Builds for Cloudflare and runs a local emulation of the Worker environment. [apps/web/package.json:15-15]() |
| `deploy` | `opennextjs-cloudflare build && opennextjs-cloudflare deploy` | Full build and deployment to the Cloudflare production environment. [apps/web/package.json:16-16]() |
| `upload` | `opennextjs-cloudflare build && opennextjs-cloudflare upload` | Builds and uploads static assets without updating the Worker logic. [apps/web/package.json:17-17]() |
| `cf-typegen` | `wrangler types --env-interface CloudflareEnv cloudflare-env.d.ts` | Generates TypeScript types for Cloudflare bindings. [apps/web/package.json:18-18]() |

---

## Environment Variable Typing (`cf-typegen`)

Cloudflare Workers do not use `process.env` for secrets and bindings in the same way Node.js does; instead, they inject an environment object into the request handler. To maintain type safety within the Next.js application, the project uses `wrangler types`.

### Type Generation Mapping

```mermaid
graph LR
  subgraph "Configuration_Space"
    WT["wrangler.jsonc\n(apps/web/wrangler.jsonc)"]
  end

  subgraph "Type_Space"
    TG["wrangler types\n(cf-typegen script)"]
    INT["interface CloudflareEnv\n(cloudflare-env.d.ts)"]
  end

  subgraph "Code_Space"
    APP["Next.js App\n(apps/web/app/layout.tsx)"]
  end

  WT --> TG
  TG --> INT
  INT --> APP
```

Sources: [apps/web/package.json:18-18](), [apps/web/wrangler.jsonc:1-31]()

The `cf-typegen` script reads the local configuration (like the `R2_BUCKET` binding [apps/web/wrangler.jsonc:27-28]()) and produces `apps/web/cloudflare-env.d.ts`. This file defines the `CloudflareEnv` interface, which typically includes definitions for KV Namespaces, R2 Buckets, and other bindings required by the application.

---

## Sentry Integration and Source Maps

Because Cloudflare deployments involve minified code running on the edge, source maps must be uploaded to Sentry to ensure readable stack traces.

### Post-Deployment Hook

The `apps/web` package includes a `postdeploy` hook that triggers automatically after a successful Cloudflare deployment:

- **Script**: `postdeploy` calls `bun run sentry:sourcemaps`. [apps/web/package.json:20-20]()
- **Sentry Upload**: Uses `sentry-cli` to create a new release for project `consumer-app` and upload the maps from the build directory. [apps/web/package.json:19-19]()
- **Global Orchestration**: The root `package.json` also defines `sentry:sourcemaps` and a `postbuild` hook to ensure maps are handled across the monorepo. [package.json:10-11]()

---

## Configuration Reference

### Application Metadata
The root layout defines the `metadataBase` as `https://app.supermemory.ai` [apps/web/app/layout.tsx:21-21]() and specifies various social sharing images and icons [apps/web/app/layout.tsx:23-55]().

### `.gitignore`
The build artifacts for Cloudflare and standard Next.js are specifically ignored to prevent large generated bundles from entering version control:
- `.open-next/`: [apps/web/.gitignore:2-2]()
- `/.next/`: [apps/web/.gitignore:14-14]()
- `dist`: [apps/web/.gitignore:18-18]()

### Development and Runtimes
For local development, the `next.config.ts` initializes OpenNext for Cloudflare emulation [apps/web/next.config.ts:89-91](). The project also enforces a minimum Node.js version of 20 [package.json:14-14]() and uses `bun` as the primary package manager [package.json:16-16]().

Sources: [apps/web/package.json:12-21](), [package.json:10-16](), [apps/web/app/layout.tsx:1-115](), [apps/web/wrangler.jsonc:1-32](), [apps/web/next.config.ts:89-91]()

---

# Page: UI Component System

# UI Component System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [apps/web/README.md](apps/web/README.md)
- [apps/web/biome.json](apps/web/biome.json)
- [apps/web/components.json](apps/web/components.json)
- [packages/lib/package.json](packages/lib/package.json)
- [packages/ui/assets/Logo.tsx](packages/ui/assets/Logo.tsx)
- [packages/ui/biome.json](packages/ui/biome.json)
- [packages/ui/button/external-auth.tsx](packages/ui/button/external-auth.tsx)
- [packages/ui/components/text-separator.tsx](packages/ui/components/text-separator.tsx)
- [packages/ui/globals.css](packages/ui/globals.css)
- [packages/ui/input/labeled-input.tsx](packages/ui/input/labeled-input.tsx)
- [packages/ui/package.json](packages/ui/package.json)
- [packages/ui/text/label/label-2-medium.tsx](packages/ui/text/label/label-2-medium.tsx)
- [packages/ui/text/label/label-2-regular.tsx](packages/ui/text/label/label-2-regular.tsx)
- [packages/ui/text/label/label-3-medium.tsx](packages/ui/text/label/label-3-medium.tsx)
- [packages/ui/text/label/label-3-regular.tsx](packages/ui/text/label/label-3-regular.tsx)

</details>



This page documents the UI component infrastructure used by `apps/web`: the Shadcn UI configuration, Tailwind CSS setup, the shared `packages/ui` component package, path aliases, font configuration, and the application header and navigation components.

For details about how providers are layered into the root layout, see [Application Structure & Providers](). For analytics and error tracking hooks that integrate with UI interactions, see [Analytics & Error Tracking]().

---

## Shadcn UI Configuration

The `apps/web` application uses [Shadcn UI](https://ui.shadcn.com/) with a specific configuration defined in `components.json`. The setup utilizes the `new-york` style and is optimized for React Server Components (RSC).

| Field | Value | Effect |
|---|---|---|
| `style` | `new-york` | Applies the New York visual style (sharper corners, denser spacing). |
| `rsc` | `true` | Generates components compatible with React Server Components. |
| `tsx` | `true` | Uses TypeScript `.tsx` extensions. |
| `tailwind.css` | `../../packages/ui/globals.css` | Points Tailwind to the shared package's global CSS. |
| `tailwind.baseColor` | `zinc` | Default color scale for generated components. |
| `tailwind.cssVariables` | `true` | Uses CSS custom properties for theming rather than static classes. |
| `iconLibrary` | `lucide` | Uses Lucide icons throughout generated components. |

Sources: [apps/web/components.json:2-15](), [packages/ui/globals.css:1-3]()

---

## Path Aliases

The monorepo configuration uses path aliases to bridge the application code with the shared UI library and internal utilities. These are resolved by the bundler and TypeScript.

**Path alias resolution table:**

| Alias | Resolves To | Purpose |
|---|---|---|
| `@ui/*` | `packages/ui/*` | Shared components and assets. |
| `@lib/*` | `packages/lib/*` | Shared logic (auth, utils, context). |
| `@/*` | `apps/web/*` | Application-specific source code. |
| `@hooks/*` | `apps/web/hooks/*` | Application-specific hooks. |

Diagram: Path Alias Resolution

```mermaid
graph LR
  subgraph "Natural_Language_Alias"
    A["@ui/components/*"]
    C["@hooks/*"]
    E["@lib/utils"]
    G["@/components/header"]
  end

  subgraph "Code_Entity_Space"
    B["packages/ui/components/*"]
    D["apps/web/hooks/*"]
    F["packages/lib/utils.ts"]
    H["apps/web/components/header.tsx"]
  end

  A --> B
  C --> D
  E --> F
  G --> H
```

Sources: [packages/ui/button/external-auth.tsx:1-2](), [packages/ui/input/labeled-input.tsx:1-3](), [packages/ui/components/text-separator.tsx:1-1]()

---

## Shared `packages/ui` Package

All reusable primitive components and design tokens live in `packages/ui`. This package is a central repository for the design system.

### Package Dependencies
The UI package manages a comprehensive set of Radix UI primitives and visualization libraries:
- **Primitives**: `@radix-ui/react-accordion`, `react-dialog`, `react-dropdown-menu`, `react-select`, `react-slot`, etc. [packages/ui/package.json:11-29]()
- **Icons**: `lucide-react` [packages/ui/package.json:33-33]()
- **Animation**: `motion` (Framer Motion) and `tw-animate-css` [packages/ui/package.json:34-34](), [packages/ui/package.json:40-40]()
- **Visualization**: `@pixi/react`, `pixi.js` (for memory graph), and `recharts` [packages/ui/package.json:10-10](), [packages/ui/package.json:36-37]()
- **Styling**: `class-variance-authority`, `tailwindcss`, and `next-themes` [packages/ui/package.json:30-30](), [packages/ui/package.json:35-35](), [packages/ui/package.json:39-39]()

### CSS Globals
The application uses Tailwind CSS v4 directives and theme variables defined in the shared package.
- `@ui/globals.css`: Shared design tokens, OKLCH color variables, and custom scrollbar styles [packages/ui/globals.css:1-170]().
- **Theming**: Supports dark mode via the `.dark` selector and `@custom-variant dark` [packages/ui/globals.css:4-4](), [packages/ui/globals.css:112-170]().

Diagram: Shared UI Package Structure

```mermaid
graph TD
  pkg["@repo/ui_(packages/ui)"]
  globals["globals.css_(Tailwind_v4_Theme)"]
  components["components/_(Radix_Wrappers)"]
  assets["assets/_(Logo_&_SVG)"]
  text["text/_(Typography_Primitives)"]
  
  pkg --> globals
  pkg --> components
  pkg --> assets
  pkg --> text

  components --> "button.tsx"
  components --> "input.tsx"
  components --> "text-separator.tsx"
  
  text --> "label-1-regular.tsx"
  text --> "label-3-medium.tsx"

  webApp["apps/web"]
  webApp -->|"@ui/globals.css"| globals
  webApp -->|"@ui/components/*"| components
  webApp -->|"@ui/assets/Logo"| assets
```

Sources: [packages/ui/package.json:1-43](), [packages/ui/globals.css:9-49](), [packages/ui/assets/Logo.tsx:1-25]()

---

## Tailwind CSS and Typography

The styling system is driven by Tailwind CSS v4, utilizing a theme configuration based on CSS variables [packages/ui/globals.css:9-49]().

- **Fonts**: 
    - **Sans**: `Space Grotesk` and `Inter` [packages/ui/globals.css:12-14]().
    - **Mono**: `Space Mono` [packages/ui/globals.css:87-87]().
- **Typography Components**: Reusable text components like `Label3Medium` and `Label2Medium` provide consistent sizing and tracking across the app [packages/ui/text/label/label-3-medium.tsx:4-19](), [packages/ui/text/label/label-2-medium.tsx:4-19]().
- **Colors**: Uses `oklch` color space for high-precision color definitions (e.g., `--primary: oklch(0.614 0.2014 258.1073)`) [packages/ui/globals.css:53-84]().

---

## Shared UI Components

The system provides specialized components for common patterns:

### Labeled Input
The `LabeledInput` component wraps the standard `Input` with a `Label1Regular` and handles error states [packages/ui/input/labeled-input.tsx:13-51](). It uses a custom background (`#070E1B`) and specific box-shadows to match the dark theme aesthetic [packages/ui/input/labeled-input.tsx:36-38]().

### External Auth Button
The `ExternalAuthButton` is a specialized button for OAuth providers (e.g., Google, GitHub). It features a linear gradient background and a specific height of `44px` [packages/ui/button/external-auth.tsx:10-38]().

### Text Separator
Used for "OR" dividers in login forms, the `TextSeparator` provides a horizontal line with uppercase text [packages/ui/components/text-separator.tsx:7-22]().

Diagram: Component Composition

```mermaid
graph TD
  subgraph "Atomic_Primitives"
    Btn["Button.tsx"]
    Inp["Input.tsx"]
    Txt["Label1Regular.tsx"]
  end

  subgraph "Composite_Components"
    LInp["LabeledInput.tsx"]
    EAuth["ExternalAuthButton.tsx"]
  end

  LInp --> Inp
  LInp --> Txt
  EAuth --> Btn
```

Sources: [packages/ui/input/labeled-input.tsx:27-43](), [packages/ui/button/external-auth.tsx:17-36](), [packages/ui/components/text-separator.tsx:13-20]()

---

## Navigation and Assets

### Brand Assets
The `Logo` and `LogoFull` components are exported as SVG components from `@ui/assets/Logo.tsx`, allowing for easy color manipulation via the `currentColor` fill property [packages/ui/assets/Logo.tsx:25-41]().

### Global Styling
The `globals.css` file defines the root variables for the entire design system, including shadows (`--shadow-sm`, `--shadow-md`), border radius (`--radius: 0.75rem`), and sidebar-specific colors [packages/ui/globals.css:52-108]().

Sources: [packages/ui/assets/Logo.tsx:25-41](), [packages/ui/globals.css:52-83]()

---

# Page: Analytics & Error Tracking

# Analytics & Error Tracking

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [apps/web/app/(app)/brain-home/page.tsx](apps/web/app/(app)/brain-home/page.tsx)
- [apps/web/app/(app)/onboarding/page.tsx](apps/web/app/(app)/onboarding/page.tsx)
- [apps/web/components/brain-home/data.ts](apps/web/components/brain-home/data.ts)
- [apps/web/components/brain-home/widgets.tsx](apps/web/components/brain-home/widgets.tsx)
- [apps/web/components/initial-header.tsx](apps/web/components/initial-header.tsx)
- [apps/web/components/onboarding-brain/onboarding-confetti.tsx](apps/web/components/onboarding-brain/onboarding-confetti.tsx)
- [apps/web/components/onboarding-brain/shell.tsx](apps/web/components/onboarding-brain/shell.tsx)
- [apps/web/components/onboarding-brain/step-about.tsx](apps/web/components/onboarding-brain/step-about.tsx)
- [apps/web/components/onboarding-brain/step-ingest.tsx](apps/web/components/onboarding-brain/step-ingest.tsx)
- [apps/web/components/onboarding-brain/step-sources.tsx](apps/web/components/onboarding-brain/step-sources.tsx)
- [apps/web/components/onboarding-brain/step-team.tsx](apps/web/components/onboarding-brain/step-team.tsx)
- [apps/web/lib/analytics.ts](apps/web/lib/analytics.ts)
- [apps/web/lib/constants.ts](apps/web/lib/constants.ts)
- [packages/lib/error-tracking.tsx](packages/lib/error-tracking.tsx)
- [packages/lib/posthog.tsx](packages/lib/posthog.tsx)

</details>



This page documents the observability stack used in the supermemory ecosystem. It covers the PostHog analytics integration for user behavior tracking across the web app, Sentry for runtime error monitoring, and the structured event catalog used to maintain data consistency.

---

## Overview

Supermemory uses a dual-tool strategy for observability:

| Tool | Purpose | Primary Implementation |
|---|---|---|
| **PostHog** | Product analytics, feature usage, user identification, and interaction tracking. | [packages/lib/posthog.tsx:36-75](), [apps/web/lib/analytics.ts:7-220]() |
| **Sentry** | Exception tracking, performance monitoring, and session replays. | [packages/lib/error-tracking.tsx:8-72]() |

PostHog events are proxied through the backend to prevent ad-blocker interference, while Sentry is integrated into the client runtime and build process.

---

## PostHog Analytics Integration

### Web Application Provider

The `PostHogProvider` manages the initialization and lifecycle of the PostHog SDK. It is mounted in the root provider stack of the application.

**Key Implementation Details:**
- **Initialization**: PostHog is initialized with a proxy `api_host` pointing to `${backendUrl}/orange` to bypass client-side blockers [packages/lib/posthog.tsx:41-51]().
- **User Identification**: When a user session is active, the provider calls `posthog.identify` to link the anonymous ID with the user's email, name, and internal `userId` [packages/lib/posthog.tsx:56-65]().
- **Page Tracking**: The `PostHogPageTracking` component captures `$pageview` events on route changes, including context like `page_type` and `org_slug` extracted from the URL [packages/lib/posthog.tsx:8-31]().

**PostHog Initialization Flow:**

```mermaid
sequenceDiagram
    participant "RootLayout" as "RootLayout"
    participant "PostHogProvider" as "PostHogProvider"
    participant "posthog-js" as "posthog-js"
    participant "Backend" as "api.supermemory.ai/orange"

    "RootLayout"->>"PostHogProvider": "Mount"
    "PostHogProvider"->>"posthog-js": "init(key, { api_host: '/orange' })"
    "PostHogProvider"->>"posthog-js": "register({ app: 'app' })"
    Note over "PostHogProvider": "Wait for Session (useSession)"
    "PostHogProvider"->>"posthog-js": "identify(user.id, { email, name })"
    "posthog-js"-->>"Backend": "Proxy Event Data"
```
Sources: [packages/lib/posthog.tsx:8-75]()

---

### Structured Event Catalog

The `analytics` object in `apps/web/lib/analytics.ts` provides a type-safe interface for capturing business events. It uses a `safeCapture` helper that buffers events if the SDK is not yet loaded [apps/web/lib/analytics.ts:40-51]().

#### Buffering Logic
If `posthog.__loaded` is false, events are pushed to `pendingEvents` [apps/web/lib/analytics.ts:49](). A `flushTimer` periodically checks for readiness and dispatches buffered events once the SDK is available [apps/web/lib/analytics.ts:11-38]().

#### Key Event Categories

| Category | Events | Implementation Site |
|---|---|---|
| **Memories** | `memoryAdded`, `memoryDetailOpened`, `documentAdded` | [apps/web/lib/analytics.ts:56-64](), [apps/web/lib/analytics.ts:110-113]() |
| **Chat** | `chatMessageSent`, `chatMessageLiked`, `chatMemoryExpanded` | [apps/web/lib/analytics.ts:196-201](), [apps/web/lib/analytics.ts:206-207](), [apps/web/lib/analytics.ts:215-216]() |
| **Onboarding** | `onboardingStarted`, `onboardingStepViewed`, `onboardingCompleted` | [apps/web/lib/analytics.ts:122-132](), [apps/web/lib/analytics.ts:173-178]() |
| **Integrations** | `connectionAuthStarted`, `mcpViewOpened`, `mcpInstallCmdCopied` | [apps/web/lib/analytics.ts:84-85](), [apps/web/lib/analytics.ts:104-105]() |

**Onboarding Analytics Implementation:**
The `BrainOnboardingPage` uses these methods to track the funnel. It triggers `onboardingStarted` and `onboardingStepViewed` on mount [apps/web/app/(app)/onboarding/page.tsx:115-123](). Navigation between steps (e.g., `StepAbout`, `StepSources`) triggers `onboardingStepCompleted` [apps/web/app/(app)/onboarding/page.tsx:183]().

Sources: [apps/web/lib/analytics.ts:1-220](), [apps/web/app/(app)/onboarding/page.tsx:112-183]()

---

## Error Tracking Hooks

The `packages/lib/error-tracking.tsx` file provides specialized hooks for capturing errors and interactions.

### `useErrorTracking`
This hook provides functions to track different failure modes [packages/lib/error-tracking.tsx:8-72]():
- `trackError`: Generic error capture with stack traces.
- `trackApiError`: Specifically for failed network requests, including `endpoint` and `status`.
- `trackComponentError`: For UI-level failures.
- `trackValidationError`: For form submission failures.

### `useInteractionTracking`
Designed for granular UI analytics, this hook tracks how users navigate the interface [packages/lib/error-tracking.tsx:115-194]():
- `trackButtonClick`: Logs the button name and context.
- `trackModalOpen` / `trackModalClose`: Monitors dialog lifecycle.
- `trackTabChange`: Captures navigation between UI sections.

### `ErrorTrackingProvider`
A global component that attaches listeners to the `window` object to catch unhandled promise rejections and global runtime errors [packages/lib/error-tracking.tsx:75-112]().

Sources: [packages/lib/error-tracking.tsx:1-194]()

---

## Observability Data Flow

The following diagram bridges the Natural Language concepts (Tracking, Analytics) to Code Entities (`safeCapture`, `PostHogProvider`, `trackError`).

**Observability Architecture:**

```mermaid
graph TD
    subgraph "Client Runtime [apps/web]"
        "useErrorTracking"["useErrorTracking (packages/lib)"]
        "ErrorTrackingProvider"["ErrorTrackingProvider (packages/lib)"]
        "analytics"["analytics object (lib/analytics.ts)"]
        "safeCapture"["safeCapture function (lib/analytics.ts)"]
    end

    subgraph "Tracking Libraries"
        "posthog-js"["posthog-js SDK"]
    end

    subgraph "External Collectors"
        "PostHog_Ingest"["PostHog Ingest (/orange proxy)"]
    end

    "analytics" --> "safeCapture"
    "safeCapture" -->|posthog.capture| "posthog-js"
    "useErrorTracking" -->|trackError| "posthog-js"
    "ErrorTrackingProvider" -->|window.onerror| "posthog-js"
    "posthog-js" --> "PostHog_Ingest"
```
Sources: [apps/web/lib/analytics.ts:40-51](), [packages/lib/error-tracking.tsx:8-72](), [packages/lib/error-tracking.tsx:75-112](), [packages/lib/posthog.tsx:41-51]()

---

## Usage in Components

### Onboarding tracking
In `StepIngest`, when a user selects an agent like Cursor or Claude Desktop, it calls `analytics.onboardingAgentSelected` [apps/web/components/onboarding-brain/step-ingest.tsx:124-126](). Skipping the step triggers `analytics.onboardingIngestSkipped` [apps/web/components/onboarding-brain/step-ingest.tsx:134]().

### Integration tracking
In `StepSources`, when a user interacts with integration cards, the system tracks which source is being connected via `analytics.onboardingIntegrationClicked` [apps/web/components/onboarding-brain/step-sources.tsx:111]().

Sources: [apps/web/components/onboarding-brain/step-ingest.tsx:124-134](), [apps/web/components/onboarding-brain/step-sources.tsx:111]()

---

# Page: Browser Extension

# Browser Extension

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [apps/browser-extension/components/icons.tsx](apps/browser-extension/components/icons.tsx)
- [apps/browser-extension/entrypoints/background.ts](apps/browser-extension/entrypoints/background.ts)
- [apps/browser-extension/entrypoints/content/claude.ts](apps/browser-extension/entrypoints/content/claude.ts)
- [apps/browser-extension/entrypoints/content/grok.ts](apps/browser-extension/entrypoints/content/grok.ts)
- [apps/browser-extension/entrypoints/content/index.ts](apps/browser-extension/entrypoints/content/index.ts)
- [apps/browser-extension/entrypoints/content/twitter.ts](apps/browser-extension/entrypoints/content/twitter.ts)
- [apps/browser-extension/entrypoints/popup/App.tsx](apps/browser-extension/entrypoints/popup/App.tsx)
- [apps/browser-extension/entrypoints/popup/style.css](apps/browser-extension/entrypoints/popup/style.css)
- [apps/browser-extension/entrypoints/welcome/Welcome.tsx](apps/browser-extension/entrypoints/welcome/Welcome.tsx)
- [apps/browser-extension/package.json](apps/browser-extension/package.json)
- [apps/browser-extension/public/claude.png](apps/browser-extension/public/claude.png)
- [apps/browser-extension/public/gemini.png](apps/browser-extension/public/gemini.png)
- [apps/browser-extension/public/icon-48.png](apps/browser-extension/public/icon-48.png)
- [apps/browser-extension/public/logo-fullmark.svg](apps/browser-extension/public/logo-fullmark.svg)
- [apps/browser-extension/utils/api.ts](apps/browser-extension/utils/api.ts)
- [apps/browser-extension/utils/constants.ts](apps/browser-extension/utils/constants.ts)
- [apps/browser-extension/utils/twitter-import.ts](apps/browser-extension/utils/twitter-import.ts)
- [apps/browser-extension/utils/twitter-utils.ts](apps/browser-extension/utils/twitter-utils.ts)
- [apps/browser-extension/utils/types.ts](apps/browser-extension/utils/types.ts)
- [apps/browser-extension/utils/ui-components.ts](apps/browser-extension/utils/ui-components.ts)
- [apps/browser-extension/wxt.config.ts](apps/browser-extension/wxt.config.ts)

</details>



The Browser Extension is a WXT-based Chrome/Edge extension that enables users to save web pages, import bookmarks, and integrate Supermemory with AI chat applications. It provides a popup interface for manual page saving, content scripts for platform-specific integrations, and a message-passing system for communication between extension components.

For information about the AI Tools integration used in chat applications, see [AI Tools Package](#4). For details about the backend API endpoints the extension calls, see [API Reference](#6).

## Purpose and Scope

This extension serves multiple functions:
- **Page Saving**: Save any web page to Supermemory with a single click or keyboard shortcut.
- **Twitter Import**: Batch import Twitter/X bookmarks with project selection.
- **AI Chat Integration**: Auto-search memories and capture prompts in ChatGPT, Claude, Grok, and T3.chat.

For detailed sub-system documentation, see: [Extension Architecture](#3.1), [AI Chat Integration](#3.2), [Twitter Bookmark Import](#3.3), and [UI Components & Storage](#3.4).

## Extension Architecture

The extension is built on the [WXT framework](https://wxt.dev/), which provides a modern development experience with Vite integration and TypeScript support [apps/browser-extension/wxt.config.ts:13-14]().

### System Components Diagram

```mermaid
graph TB
    subgraph "Extension Components"
        Popup["Popup UI<br/>(entrypoints/popup/App.tsx)"]
        Background["Background Service Worker<br/>(entrypoints/background.ts)"]
        ContentMain["Content Script<br/>(entrypoints/content/index.ts)"]

        subgraph "Platform Content Scripts"
            Twitter["Twitter Integration<br/>(content/twitter.ts)"]
            ChatGPT["ChatGPT Integration<br/>(content/chatgpt.ts)"]
            Claude["Claude Integration<br/>(content/claude.ts)"]
            Grok["Grok Integration<br/>(content/grok.ts)"]
            T3["T3 Integration<br/>(content/t3.ts)"]
        end

        subgraph "Shared Utilities"
            API["API Service<br/>(utils/api.ts)"]
            Storage["Storage Layer<br/>(utils/storage.ts)"]
            UIComponents["UI Components<br/>(utils/ui-components.ts)"]
            Constants["Constants<br/>(utils/constants.ts)"]
        end
    end

    subgraph "External APIs"
        MemoryAPI["Supermemory API<br/>/v3/documents, /v4/search<br/>/v3/projects"]
        ChromeAPIs["Chrome APIs<br/>storage, tabs, runtime,<br/>webRequest"]
    end

    Popup --> Storage
    Popup --> API
    ContentMain --> Twitter
    ContentMain --> ChatGPT
    ContentMain --> Claude
    ContentMain --> Grok
    ContentMain --> T3

    Twitter --> UIComponents
    ChatGPT --> UIComponents
    Claude --> UIComponents
    Grok --> UIComponents
    T3 --> UIComponents

    API --> MemoryAPI
    Storage --> ChromeAPIs
    UIComponents --> Constants

    Background --> ChromeAPIs
    Background --> API

    Popup -. "MESSAGE_TYPES" .-> Background
    ContentMain -. "MESSAGE_TYPES" .-> Background
```

**Sources:** [apps/browser-extension/wxt.config.ts:13-53](), [apps/browser-extension/entrypoints/background.ts:24-172](), [apps/browser-extension/entrypoints/content/index.ts:23-35](), [apps/browser-extension/utils/constants.ts:77-87]()

### Manifest Configuration

The extension requires specific permissions and host access to function across different platforms.

| Permission | Purpose |
|------------|---------|
| `storage` | Persist authentication tokens and user settings [apps/browser-extension/wxt.config.ts:33]() |
| `activeTab` | Access current tab URL and content for saving [apps/browser-extension/wxt.config.ts:33]() |
| `webRequest` | Monitor requests for Twitter token capture [apps/browser-extension/wxt.config.ts:33]() |
| `tabs` | Open new tabs (e.g., welcome page) and query tab state [apps/browser-extension/wxt.config.ts:33]() |

**Host Permissions:**
- `*://x.com/*`, `*://twitter.com/*` - Twitter bookmark import [apps/browser-extension/wxt.config.ts:35-36]()
- `*://chatgpt.com/*`, `*://chat.openai.com/*` - ChatGPT integration [apps/browser-extension/wxt.config.ts:39-40]()
- `*://claude.ai/*` - Claude integration [apps/browser-extension/utils/constants.ts:60]()
- `*://supermemory.ai/*`, `*://api.supermemory.ai/*` - API access [apps/browser-extension/wxt.config.ts:37-38]()
- `https://*.posthog.com/*` - Analytics tracking [apps/browser-extension/wxt.config.ts:45]()

**Sources:** [apps/browser-extension/wxt.config.ts:29-53](), [apps/browser-extension/utils/constants.ts:57-64]()

## Popup Interface

The popup provides the primary user interface for the extension, built with React and Tailwind CSS. It handles authentication state, project selection, and manual saving.

### Popup State & UI Structure

```mermaid
graph TB
    App["App Component<br/>(popup/App.tsx)"]
    
    subgraph "State Management"
        AuthState["userSignedIn: boolean<br/>authInvalidated: boolean"]
        TabState["activeTab: 'save' | 'imports' | 'settings'"]
        ProjectState["defaultProject: Project<br/>showProjectSelector: boolean"]
    end
    
    subgraph "React Query Hooks"
        UseProjects["useProjects()<br/>Fetch available projects"]
        UseDefaultProject["useDefaultProject()<br/>Get selected project"]
        UseUserData["useUserData()<br/>Fetch email, name"]
        SetDefaultProject["useSetDefaultProject()<br/>Update selection"]
    end
    
    subgraph "UI Sections"
        SaveTab["Save Tab<br/>- Current page info<br/>- Project selector<br/>- Save button"]
        ImportsTab["Imports Tab<br/>- ChatGPT memories<br/>- Twitter bookmarks"]
        SettingsTab["Settings Tab<br/>- Account info<br/>- Auto search toggle<br/>- Auto capture toggle"]
    end
    
    App --> AuthState
    App --> TabState
    App --> ProjectState
    
    App --> UseProjects
    App --> UseDefaultProject
    App --> UseUserData
    App --> SetDefaultProject
    
    TabState --> SaveTab
    TabState --> ImportsTab
    TabState --> SettingsTab
```

**Sources:** [apps/browser-extension/entrypoints/popup/App.tsx:6-18](), [apps/browser-extension/utils/query-hooks.ts:1-20]()

### Authentication & Token Validation

The popup uses `validateAuthToken` to check the validity of the stored `bearerToken`. If invalid, it clears the local session.

- **Token Valid**: Loads user data and projects via `useProjects` [apps/browser-extension/utils/api.ts:101-105]().
- **Token Invalid/Missing**: Throws `AuthenticationError`, prompting the user to log in via the web application [apps/browser-extension/utils/api.ts:106-112](), [apps/browser-extension/entrypoints/welcome/Welcome.tsx:75-85]().

**Sources:** [apps/browser-extension/utils/api.ts:99-112](), [apps/browser-extension/entrypoints/popup/App.tsx:4-5]()

## Twitter Bookmark Import

The Twitter integration allows for bulk importing bookmarks into specific projects. It utilizes a specialized `TwitterImporter` class and a background service worker to handle authentication headers.

- **Import Intent**: Uses a TTL mechanism (`IMPORT_INTENT_TTL`) in storage to trigger the import modal when a user navigates to the bookmarks page [apps/browser-extension/utils/constants.ts:45](), [apps/browser-extension/entrypoints/content/twitter.ts:34-54]().
- **Folder Import**: Injects "Import Bookmarks" buttons into Twitter's bookmark folder UI [apps/browser-extension/utils/ui-components.ts:166-199]().
- **Background Processing**: The `TwitterImporter` in the background script handles the actual fetching and saving logic [apps/browser-extension/entrypoints/background.ts:176-192](), [apps/browser-extension/utils/twitter-import.ts:16-17]().

For details, see [Twitter Bookmark Import](#3.3).

**Sources:** [apps/browser-extension/entrypoints/content/twitter.ts:84-124](), [apps/browser-extension/entrypoints/background.ts:176-192]()

## AI Chat Integration

The extension enhances AI chat interfaces by injecting memory search and prompt capture capabilities.

- **Auto-Search**: Automatically queries Supermemory as the user types, using a debounce delay defined in `UI_CONFIG.AUTO_SEARCH_DEBOUNCE_DELAY` [apps/browser-extension/utils/constants.ts:48](), [apps/browser-extension/entrypoints/content/claude.ts:159-232]().
- **Auto-Capture**: Saves user prompts as memories upon submission if `autoCapturePromptsEnabled` is active [apps/browser-extension/entrypoints/background.ts:231-251]().
- **Related Memories**: The background script handles the `GET_RELATED_MEMORIES` action by calling the `/v4/search` endpoint [apps/browser-extension/entrypoints/background.ts:146-168](), [apps/browser-extension/utils/api.ts:148-162]().

For details, see [AI Chat Integration](#3.2).

**Sources:** [apps/browser-extension/entrypoints/background.ts:213-229](), [apps/browser-extension/entrypoints/content/claude.ts:34-37](), [apps/browser-extension/utils/constants.ts:83-84]()

## UI Components & Storage

The extension uses a shared utility layer for DOM manipulation, storage access, and API calls.

- **Toasts**: A custom toast system (`createToast`) provides feedback for loading, success, and error states [apps/browser-extension/utils/ui-components.ts:14-159]().
- **Storage Layer**: Uses `wxt/storage` to manage `bearerToken`, `userData`, and `defaultProject` [apps/browser-extension/utils/storage.ts:5-18]().
- **API Endpoints**: Communicates with the Supermemory API via `v3` (documents/projects) and `v4` (search) endpoints [apps/browser-extension/utils/api.ts:4-11]().

For details, see [UI Components & Storage](#3.4).

**Sources:** [apps/browser-extension/utils/ui-components.ts:1-200](), [apps/browser-extension/utils/api.ts:1-162](), [apps/browser-extension/utils/constants.ts:4-11]()

---

# Page: Extension Architecture

# Extension Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [apps/browser-extension/components/icons.tsx](apps/browser-extension/components/icons.tsx)
- [apps/browser-extension/entrypoints/background.ts](apps/browser-extension/entrypoints/background.ts)
- [apps/browser-extension/entrypoints/content/claude.ts](apps/browser-extension/entrypoints/content/claude.ts)
- [apps/browser-extension/entrypoints/content/grok.ts](apps/browser-extension/entrypoints/content/grok.ts)
- [apps/browser-extension/entrypoints/content/index.ts](apps/browser-extension/entrypoints/content/index.ts)
- [apps/browser-extension/entrypoints/content/twitter.ts](apps/browser-extension/entrypoints/content/twitter.ts)
- [apps/browser-extension/entrypoints/popup/App.tsx](apps/browser-extension/entrypoints/popup/App.tsx)
- [apps/browser-extension/entrypoints/popup/style.css](apps/browser-extension/entrypoints/popup/style.css)
- [apps/browser-extension/entrypoints/welcome/Welcome.tsx](apps/browser-extension/entrypoints/welcome/Welcome.tsx)
- [apps/browser-extension/package.json](apps/browser-extension/package.json)
- [apps/browser-extension/public/claude.png](apps/browser-extension/public/claude.png)
- [apps/browser-extension/public/gemini.png](apps/browser-extension/public/gemini.png)
- [apps/browser-extension/public/icon-48.png](apps/browser-extension/public/icon-48.png)
- [apps/browser-extension/public/logo-fullmark.svg](apps/browser-extension/public/logo-fullmark.svg)
- [apps/browser-extension/utils/api.ts](apps/browser-extension/utils/api.ts)
- [apps/browser-extension/utils/constants.ts](apps/browser-extension/utils/constants.ts)
- [apps/browser-extension/utils/twitter-import.ts](apps/browser-extension/utils/twitter-import.ts)
- [apps/browser-extension/utils/twitter-utils.ts](apps/browser-extension/utils/twitter-utils.ts)
- [apps/browser-extension/utils/types.ts](apps/browser-extension/utils/types.ts)
- [apps/browser-extension/utils/ui-components.ts](apps/browser-extension/utils/ui-components.ts)
- [apps/browser-extension/wxt.config.ts](apps/browser-extension/wxt.config.ts)

</details>



This page covers the build configuration, manifest permissions, runtime entry points, and inter-component message-passing protocol for the Supermemory browser extension located at `apps/browser-extension/`.

---

## Build System: WXT Framework

The extension is built with [WXT](https://wxt.dev/), a Vite-based framework for browser extensions. WXT handles entry point discovery, manifest generation, and cross-browser output.

| Script | Command |
|---|---|
| Dev (Chrome) | `wxt --port 3001` | [apps/browser-extension/package.json:8]() |
| Dev (Firefox) | `wxt -b firefox` | [apps/browser-extension/package.json:9]() |
| Build (Chrome) | `wxt build` | [apps/browser-extension/package.json:10]() |
| Build (Firefox) | `wxt build -b firefox` | [apps/browser-extension/package.json:11]() |
| Package zip | `wxt zip` | [apps/browser-extension/package.json:12]() |
| Post-install prepare | `wxt prepare` | [apps/browser-extension/package.json:15]() |

WXT configuration is defined in [apps/browser-extension/wxt.config.ts:13-53](). The React module (`@wxt-dev/module-react`) and Tailwind CSS (`tailwindcss()`) are loaded as Vite plugins [apps/browser-extension/wxt.config.ts:14-17](). The build process also includes specific optimizations for React and TanStack Query [apps/browser-extension/wxt.config.ts:25-27]().

Key runtime dependencies declared in [apps/browser-extension/package.json:17-35]():

| Package | Purpose |
|---|---|
| `wxt` | Build framework and CLI [apps/browser-extension/package.json:33]() |
| `@wxt-dev/module-react` | React support for WXT [apps/browser-extension/package.json:31]() |
| `@tanstack/react-query` | Server state management in popup [apps/browser-extension/package.json:19]() |
| `posthog-js` | Analytics tracking [apps/browser-extension/package.json:20]() |
| `turndown` | HTML-to-Markdown conversion for memories [apps/browser-extension/package.json:24]() |
| `tailwindcss` | Utility-first styling [apps/browser-extension/package.json:23]() |

Sources: [apps/browser-extension/wxt.config.ts:1-53](), [apps/browser-extension/package.json:1-35]()

---

## Manifest Configuration

The manifest is defined inline within `wxt.config.ts` [apps/browser-extension/wxt.config.ts:29-49]().

### Permissions

```typescript
permissions: ["storage", "activeTab", "webRequest", "tabs"]
```

| Permission | Used For |
|---|---|
| `storage` | Persist `bearerToken`, `userData`, `defaultProject`, and feature flags [apps/browser-extension/wxt.config.ts:33]() |
| `activeTab` | Read current tab URL and title for saving memories [apps/browser-extension/wxt.config.ts:33]() |
| `webRequest` | Intercept X/Twitter requests to capture auth headers [apps/browser-extension/entrypoints/background.ts:40-47]() |
| `tabs` | Open new tabs (welcome page, login, bookmarks page) [apps/browser-extension/entrypoints/background.ts:33-35]() |

### Host Permissions

Declared at [apps/browser-extension/wxt.config.ts:34-42]():

| Host Pattern | Purpose |
|---|---|
| `*://x.com/*` | Twitter/X content script, `webRequest` intercept [apps/browser-extension/wxt.config.ts:35]() |
| `*://twitter.com/*` | Twitter/X content script, `webRequest` intercept [apps/browser-extension/wxt.config.ts:36]() |
| `*://supermemory.ai/*` | Cookie/session passthrough [apps/browser-extension/wxt.config.ts:37]() |
| `*://api.supermemory.ai/*` | Direct API calls from extension [apps/browser-extension/wxt.config.ts:38]() |
| `*://chatgpt.com/*` | ChatGPT content script injection [apps/browser-extension/wxt.config.ts:39]() |
| `*://chat.openai.com/*` | Legacy ChatGPT domain injection [apps/browser-extension/wxt.config.ts:40]() |
| `https://*.posthog.com/*` | Analytics event reporting [apps/browser-extension/wxt.config.ts:45]() |

### Web-Accessible Resources

Fonts (SpaceGrotesk `.ttf` files) and `icon-16.png` are exposed to content scripts via `web_accessible_resources` [apps/browser-extension/wxt.config.ts:43-48]() so injected UI elements can load them with `chrome.runtime.getURL()` or `browser.runtime.getURL()` [apps/browser-extension/utils/ui-components.ts:48-77]().

Sources: [apps/browser-extension/wxt.config.ts:29-53](), [apps/browser-extension/utils/ui-components.ts:39-92]()

---

## Extension Entry Points

WXT discovers entry points by convention from the `entrypoints/` directory.

**Extension Entry Points and Their Files:**

```mermaid
graph TD
    ext["Browser Extension"]

    ext --> popup["Popup App\nentrypoints/popup/App.tsx"]
    ext --> background["Background Service Worker\nentrypoints/background.ts"]
    ext --> content["Content Script Index\nentrypoints/content/index.ts"]
    ext --> welcome["Welcome Page\nentrypoints/welcome/Welcome.tsx"]

    popup --> popupCSS["entrypoints/popup/style.css"]
    content --> twitter["content/twitter.ts"]
    content --> chatgpt["content/chatgpt.ts"]
    content --> claude["content/claude.ts"]
    content --> t3["content/t3.ts"]
    content --> shared["content/shared.ts"]
```

Sources: [apps/browser-extension/entrypoints/content/index.ts:1-78](), [apps/browser-extension/entrypoints/background.ts:1-256](), [apps/browser-extension/entrypoints/popup/App.tsx:1-10]()

### Popup (`entrypoints/popup/App.tsx`)

The popup is a React app rendered in the browser action popup. The root component `App` manages UI for authenticated users and login flows [apps/browser-extension/entrypoints/popup/App.tsx:1-10]().

On load, `App` reads the `bearerToken` from storage, validates it via `validateAuthToken()`, and conditionally renders a signed-in or sign-in UI [apps/browser-extension/entrypoints/popup/App.tsx:4-5]().

The popup uses `@tanstack/react-query` hooks (`useProjects`, `useDefaultProject`, `useUserData`, `useSetDefaultProject`) for all server-state operations [apps/browser-extension/entrypoints/popup/App.tsx:6-11]().

Sources: [apps/browser-extension/entrypoints/popup/App.tsx:1-200]()

### Background Service Worker (`entrypoints/background.ts`)

Defined with `defineBackground()`, the service worker runs persistently and handles:

1. **Install event** — opens the welcome page on first install [apps/browser-extension/entrypoints/background.ts:27-37]().
2. **`webRequest` listener** — intercepts all requests to X/Twitter domains to call `captureTwitterTokens(details)` [apps/browser-extension/entrypoints/background.ts:40-47]().
3. **`runtime.onMessage` listener** — dispatches on `message.type` or `message.action` [apps/browser-extension/entrypoints/background.ts:173-256]().

The background instantiates a `TwitterImporter` object on demand when a `BATCH_IMPORT_ALL` message is received [apps/browser-extension/entrypoints/background.ts:176-192](). It also contains the logic for `saveMemoryToSupermemory` [apps/browser-extension/entrypoints/background.ts:82-144]() and `getRelatedMemories` [apps/browser-extension/entrypoints/background.ts:146-168]().

Sources: [apps/browser-extension/entrypoints/background.ts:24-256]()

### Content Script (`entrypoints/content/index.ts`)

Registered with `matches: ["<all_urls>"]` [apps/browser-extension/entrypoints/content/index.ts:19-20](). The main entry:

1. Registers a `browser.runtime.onMessage` listener for messages from the popup and background [apps/browser-extension/entrypoints/content/index.ts:23-35]().
2. Calls `setupGlobalKeyboardShortcut()` and `setupStorageListener()` from `content/shared.ts` [apps/browser-extension/entrypoints/content/index.ts:37-41]().
3. Calls platform-specific initializers: `initializeChatGPT()`, `initializeClaude()`, `initializeT3()`, `initializeTwitter()` [apps/browser-extension/entrypoints/content/index.ts:70-74]().
4. Attaches a `MutationObserver` that re-runs the appropriate initializer whenever the DOM changes [apps/browser-extension/entrypoints/content/index.ts:44-67]().

Sources: [apps/browser-extension/entrypoints/content/index.ts:1-84]()

---

## Message-Passing Protocol

The extension uses `chrome.tabs.sendMessage` (background → content script) and `browser.runtime.sendMessage` (content script → background) as the primary communication channels.

### Message Type Constants

Centralized in `MESSAGE_TYPES` at [apps/browser-extension/utils/constants.ts:77-87]():

| Constant | String Value | Direction |
|---|---|---|
| `SAVE_MEMORY` | `"sm-save-memory"` | Content → Background [apps/browser-extension/entrypoints/background.ts:195]() |
| `SHOW_TOAST` | `"sm-show-toast"` | Popup → Content [apps/browser-extension/entrypoints/content/index.ts:24]() |
| `BATCH_IMPORT_ALL` | `"sm-batch-import-all"` | Content → Background [apps/browser-extension/entrypoints/background.ts:176]() |
| `IMPORT_UPDATE` | `"sm-import-update"` | Background → Content [apps/browser-extension/entrypoints/background.ts:57]() |
| `IMPORT_DONE` | `"sm-import-done"` | Background → Content [apps/browser-extension/entrypoints/background.ts:73]() |
| `GET_RELATED_MEMORIES` | `"sm-get-related-memories"` | Content → Background [apps/browser-extension/entrypoints/background.ts:213]() |
| `CAPTURE_PROMPT` | `"sm-capture-prompt"` | Content → Background [apps/browser-extension/entrypoints/background.ts:231]() |
| `FETCH_PROJECTS` | `"sm-fetch-projects"` | Content → Background [apps/browser-extension/entrypoints/content/twitter.ts:132]() |

### Message Flow Diagram

**Message-Passing Flow Between Extension Components:**

```mermaid
sequenceDiagram
    participant C as "Content Script (content/index.ts)"
    participant B as "Background (background.ts)"
    participant A as "API (utils/api.ts)"

    Note over C,B: "Twitter Bookmark Import"
    C->>B: "MESSAGE_TYPES.BATCH_IMPORT_ALL"
    B->>A: "saveAllTweets(documents)"
    B-->>C: "MESSAGE_TYPES.IMPORT_UPDATE"
    B-->>C: "MESSAGE_TYPES.IMPORT_DONE"

    Note over C,B: "AI Chat Memory Retrieval"
    C->>B: "MESSAGE_TYPES.GET_RELATED_MEMORIES"
    B->>A: "searchMemories(query)"
    A-->>B: "search results"
    B-->>C: "success: true, data: memories"
```

Sources: [apps/browser-extension/entrypoints/background.ts:173-256](), [apps/browser-extension/entrypoints/content/index.ts:22-34](), [apps/browser-extension/entrypoints/content/twitter.ts:129-183]()

---

## Storage Layer

Storage keys and typed storage helpers are defined across `utils/constants.ts` and `utils/storage.ts`.

**Storage key constants** [apps/browser-extension/utils/constants.ts:32-36]():

| Key | Purpose |
|---|---|
| `TWITTER_BOOKMARKS_ONBOARDING_SEEN` | Tracks if onboarding toast was shown [apps/browser-extension/utils/constants.ts:33]() |
| `TWITTER_BOOKMARKS_IMPORT_INTENT_UNTIL` | TTL timestamp for pending import intent [apps/browser-extension/utils/constants.ts:34-35]() |

**WXT-typed storage items** (defined in `utils/storage.ts` and referenced in `entrypoints/popup/App.tsx`):

| Export | Type | Purpose |
|---|---|---|
| `bearerToken` | `StorageItem<string>` | Supermemory API auth token [apps/browser-extension/entrypoints/popup/App.tsx:15]() |
| `userData` | `StorageItem<any>` | Cached user profile [apps/browser-extension/entrypoints/popup/App.tsx:17]() |
| `defaultProject` | `StorageItem<Project>` | Last selected project/space [apps/browser-extension/entrypoints/popup/App.tsx:16]() |
| `autoSearchEnabled` | `StorageItem<boolean>` | Toggle for auto-search in chat UIs [apps/browser-extension/entrypoints/popup/App.tsx:13]() |
| `autoCapturePromptsEnabled` | `StorageItem<boolean>` | Toggle for auto-capture in chat UIs [apps/browser-extension/entrypoints/popup/App.tsx:14]() |

Sources: [apps/browser-extension/utils/constants.ts:32-52](), [apps/browser-extension/entrypoints/popup/App.tsx:12-18]()

---

## API Layer

All HTTP calls go through `utils/api.ts`, which wraps fetch with a bearer token from storage.

**API function to endpoint mapping:**

```mermaid
graph LR
    saveMemory["saveMemory(payload)"] --> docPost["POST /v3/documents"]
    searchMemories["searchMemories(query)"] --> searchPost["POST /v4/search"]
    fetchProjects["fetchProjects()"] --> projGet["GET /v3/projects"]
    saveAllTweets["saveAllTweets(documents)"] --> batchPost["POST /v3/documents/batch"]
```

All authenticated calls go through `makeAuthenticatedRequest<T>(endpoint, options)` [apps/browser-extension/utils/api.ts:30-57](), which:

1. Reads the bearer token via `getBearerToken()` [apps/browser-extension/utils/api.ts:17-25]().
2. Prepends `API_ENDPOINTS.SUPERMEMORY_API` (production: `https://api.supermemory.ai`) [apps/browser-extension/utils/api.ts:36]().
3. On HTTP 401, throws `AuthenticationError`; on other failures, throws `SupermemoryAPIError` [apps/browser-extension/utils/api.ts:47-53]().

Sources: [apps/browser-extension/utils/api.ts:1-193](), [apps/browser-extension/utils/constants.ts:4-11]()

---

## Domain Routing in Content Scripts

The `DOMAINS` constant defines the sets of hostnames each feature operates on [apps/browser-extension/utils/constants.ts:57-64]().

| Constant | Hostnames | Feature |
|---|---|---|
| `DOMAINS.TWITTER` | `x.com`, `twitter.com` | Bookmark import [apps/browser-extension/entrypoints/content/twitter.ts:85]() |
| `DOMAINS.CHATGPT` | `chatgpt.com`, `chat.openai.com` | AI chat integration [apps/browser-extension/entrypoints/content/index.ts:46]() |
| `DOMAINS.CLAUDE` | `claude.ai` | AI chat integration [apps/browser-extension/entrypoints/content/index.ts:49]() |
| `DOMAINS.T3` | `t3.chat` | AI chat integration [apps/browser-extension/entrypoints/content/index.ts:55]() |

The `MutationObserver` in `content/index.ts` re-checks the domain on every DOM mutation, allowing the extension to respond to SPA navigation [apps/browser-extension/entrypoints/content/index.ts:44-67]().

Sources: [apps/browser-extension/utils/constants.ts:57-64](), [apps/browser-extension/entrypoints/content/index.ts:44-67]()

---

# Page: AI Chat Integration

# AI Chat Integration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [apps/browser-extension/entrypoints/content/chatgpt.ts](apps/browser-extension/entrypoints/content/chatgpt.ts)
- [apps/browser-extension/entrypoints/content/claude.ts](apps/browser-extension/entrypoints/content/claude.ts)
- [apps/browser-extension/entrypoints/content/grok.ts](apps/browser-extension/entrypoints/content/grok.ts)
- [apps/browser-extension/entrypoints/content/index.ts](apps/browser-extension/entrypoints/content/index.ts)
- [apps/browser-extension/entrypoints/content/shared.ts](apps/browser-extension/entrypoints/content/shared.ts)
- [apps/browser-extension/entrypoints/content/t3.ts](apps/browser-extension/entrypoints/content/t3.ts)
- [apps/browser-extension/entrypoints/popup/App.tsx](apps/browser-extension/entrypoints/popup/App.tsx)
- [apps/browser-extension/public/claude.png](apps/browser-extension/public/claude.png)
- [apps/browser-extension/public/gemini.png](apps/browser-extension/public/gemini.png)
- [apps/browser-extension/utils/constants.ts](apps/browser-extension/utils/constants.ts)
- [apps/browser-extension/utils/storage.ts](apps/browser-extension/utils/storage.ts)
- [apps/browser-extension/utils/twitter-auth.ts](apps/browser-extension/utils/twitter-auth.ts)
- [apps/browser-extension/wxt.config.ts](apps/browser-extension/wxt.config.ts)
- [apps/web/public/images/plugins/codex.png](apps/web/public/images/plugins/codex.png)

</details>



This document covers the browser extension's integration with AI chat platforms (ChatGPT, Claude, T3.chat, and Grok), enabling users to search their Supermemory knowledge base from within chat interfaces and automatically capture prompts as memories.

## Purpose and Scope

The AI chat integration system injects UI elements and functionality into AI chat platforms to:
- Provide manual memory search buttons in chat input areas.
- Automatically search memories as users type (with debouncing).
- Capture user prompts as memories for future reference.
- Display relevant memories from the user's knowledge base.
- Import platform-native memories (e.g., ChatGPT "Saved memories", Grok "Memory from your chats").

This system operates via platform-specific content scripts that detect chat interfaces and instrument them with Supermemory functionality.

---

## Architecture Overview

The AI chat integration follows a distributed architecture where content scripts handle DOM manipulation, the background script manages API communication, and the popup UI manages user preferences.

### System Interaction Diagram

```mermaid
graph TB
    subgraph "Chat Platforms (Natural Language Space)"
        ChatGPT["ChatGPT<br/>(chatgpt.com)"]
        Claude["Claude<br/>(claude.ai)"]
        T3["T3.chat<br/>(t3.chat)"]
        Grok["Grok<br/>(grok.com)"]
    end
    
    subgraph "Content Scripts (Code Entity Space)"
        ChatGPTCS["chatgpt.ts<br/>initializeChatGPT()"]
        ClaudeCS["claude.ts<br/>initializeClaude()"]
        T3CS["t3.ts<br/>initializeT3()"]
        GrokCS["grok.ts<br/>initializeGrok()"]
    end
    
    subgraph "UI Injection"
        SearchButton["Input Bar Element<br/>createT3InputBarElement()"]
        Toast["Toast Notifications<br/>DOMUtils.showToast()"]
    end
    
    subgraph "Background Script"
        GetMemories["getRelatedMemories()<br/>MESSAGE_TYPES.GET_RELATED_MEMORIES"]
        CapturePrompt["saveMemoryToSupermemory()<br/>MESSAGE_TYPES.CAPTURE_PROMPT"]
        SearchAPI["POST /v4/search"]
        SaveAPI["POST /v3/documents"]
    end
    
    ChatGPT -->|"MutationObserver"| ChatGPTCS
    Claude -->|"MutationObserver"| ClaudeCS
    T3 -->|"MutationObserver"| T3CS
    Grok -->|"MutationObserver"| GrokCS
    
    ChatGPTCS --> SearchButton
    ClaudeCS --> SearchButton
    T3CS --> SearchButton
    
    SearchButton -->|"sendMessage"| GetMemories
    T3CS -->|"Debounce: 1500ms"| GetMemories
    T3CS -->|"On submit"| CapturePrompt
    
    GetMemories --> SearchAPI
    CapturePrompt --> SaveAPI
```

**Sources:** [apps/browser-extension/entrypoints/content/chatgpt.ts:22-42](), [apps/browser-extension/entrypoints/content/t3.ts:19-39](), [apps/browser-extension/entrypoints/content/claude.ts:22-41](), [apps/browser-extension/entrypoints/content/grok.ts:10-27](), [apps/browser-extension/entrypoints/content/shared.ts:6-10]()

---

## Supported Platforms

The extension integrates with four major AI chat platforms using domain-specific detection defined in the `DOMAINS` constant.

| Platform | Domain(s) | Injection ID | PostHog Event Key |
|----------|-----------|--------------------|---------------------|
| **ChatGPT** | `chatgpt.com`, `chat.openai.com` | `CHATGPT_INPUT_BAR_ELEMENT` | `CHATGPT_CHAT_MEMORIES_SEARCHED` |
| **Claude** | `claude.ai` | `CLAUDE_INPUT_BAR_ELEMENT` | `CLAUDE_CHAT_MEMORIES_SEARCHED` |
| **T3.chat** | `t3.chat` | `T3_INPUT_BAR_ELEMENT` | `T3_CHAT_MEMORIES_SEARCHED` |
| **Grok** | `grok.com`, `x.ai` | N/A (Dialog injection) | N/A |

**Sources:** [apps/browser-extension/utils/constants.ts:23-25](), [apps/browser-extension/utils/constants.ts:57-64](), [apps/browser-extension/utils/constants.ts:93-100]()

---

## Core Features

### 1. Memory Search Button Injection

Each platform receives a platform-specific search button injected into its chat input area. The initialization functions (e.g., `initializeT3`) detect the input container and prepend the Supermemory icon.

### UI Injection Sequence

```mermaid
sequenceDiagram
    participant User
    participant CS as "t3.ts / initializeT3()"
    participant UI as "ui-components.ts"
    participant BG as "background.ts"
    participant API as "Supermemory API"
    
    CS->>CS: MutationObserver detects input
    CS->>UI: createT3InputBarElement(onClick)
    UI-->>CS: HTMLElement (sm-t3-input-bar-element)
    CS->>User: Renders icon in chat input
    
    User->>CS: Clicks icon
    CS->>CS: getRelatedMemoriesForT3()
    CS->>BG: sendMessage(GET_RELATED_MEMORIES)
    BG->>API: POST /v4/search { q: userQuery }
    API-->>BG: { results: [...] }
    BG-->>CS: { success: true, data: memories }
    CS->>User: Updates icon feedback ("Included Memories")
```

**Implementation Details:**
- **ChatGPT:** The script uses a `MutationObserver` to watch for `#prompt-textarea` or `button.composer-btn`. It injects the button via `addSaveChatGPTElementBeforeComposerBtn` [apps/browser-extension/entrypoints/content/chatgpt.ts:72-109](). It also adds a "Save to supermemory" button directly to the ChatGPT "Saved memories" dialog [apps/browser-extension/entrypoints/content/chatgpt.ts:196-228]().
- **T3.chat:** Targets the `.flex.min-w-0.items-center.gap-2` container and prepends the icon using `createT3InputBarElement` [apps/browser-extension/entrypoints/content/t3.ts:119-150]().
- **Claude:** Targets `.relative.flex-1.flex.items-center.gap-2.shrink.min-w-0` and prepends the icon via `createClaudeInputBarElement` [apps/browser-extension/entrypoints/content/claude.ts:121-150]().
- **Grok:** Injects a "Save to supermemory" button into the Grok memory dialog ("Memory from your chats") found via `getGrokMemoryDialog` [apps/browser-extension/entrypoints/content/grok.ts:234-266]().

**Sources:** [apps/browser-extension/entrypoints/content/t3.ts:119-150](), [apps/browser-extension/entrypoints/content/chatgpt.ts:72-109](), [apps/browser-extension/entrypoints/content/claude.ts:121-150](), [apps/browser-extension/entrypoints/content/grok.ts:234-266]()

### 2. Auto-Search with Debouncing

When `autoSearchEnabled` is active in storage, the extension automatically triggers a search as the user types.

- **Debounce:** Uses a platform-specific debounce timeout (e.g., `t3DebounceTimeout`) to prevent excessive API calls [apps/browser-extension/entrypoints/content/t3.ts:14](). The delay is governed by `UI_CONFIG.AUTO_SEARCH_DEBOUNCE_DELAY` (1500ms) [apps/browser-extension/utils/constants.ts:48]().
- **Query Extraction:** The content scripts extract text from `textarea` or `contenteditable` elements. For T3, it checks `textarea` values and fallback `contenteditable` divs [apps/browser-extension/entrypoints/content/t3.ts:154-184](). For Claude, it specifically looks for `p` tags within the input area [apps/browser-extension/entrypoints/content/claude.ts:161-166]().
- **Context Injection:** Upon a successful search, retrieved memories are stored in the input element's `dataset.supermemories` attribute, providing context for the AI [apps/browser-extension/entrypoints/content/t3.ts:241-242]().

**Sources:** [apps/browser-extension/entrypoints/content/t3.ts:152-258](), [apps/browser-extension/entrypoints/content/claude.ts:153-250](), [apps/browser-extension/utils/constants.ts:48](), [apps/browser-extension/utils/storage.ts:13]()

### 3. Automatic Prompt Capture

When `autoCapturePromptsEnabled` is enabled, user prompts are automatically saved to Supermemory.

- **Message Type:** Communication uses `MESSAGE_TYPES.GET_RELATED_MEMORIES` for retrieval and `MESSAGE_TYPES.SAVE_MEMORY` for persistence [apps/browser-extension/utils/constants.ts:83-84]().
- **Processing:** Content scripts listen for input events and trigger `saveMemory` from `shared.ts`, which captures the URL, title, and highlighted text or full page markdown [apps/browser-extension/entrypoints/content/shared.ts:6-71]().
- **Markdown Conversion:** The extension uses `TurndownService` to convert captured HTML into markdown before saving [apps/browser-extension/entrypoints/content/shared.ts:61-64]().

**Sources:** [apps/browser-extension/entrypoints/content/shared.ts:6-71](), [apps/browser-extension/utils/storage.ts:14]()

---

## Data Flow and API Integration

The background script acts as the bridge to the Supermemory API.

### Memory Search Logic (`getRelatedMemories`)
1. Content script sends `MESSAGE_TYPES.GET_RELATED_MEMORIES` with the `userQuery` [apps/browser-extension/entrypoints/content/t3.ts:212-216]().
2. The background script calls the search API (e.g., `api.supermemory.ai/v4/search`).
3. Results are returned to the content script and injected into the DOM `dataset` [apps/browser-extension/entrypoints/content/t3.ts:241-243]().

### Memory Storage Logic (`saveMemory`)
1. Captures metadata: `url`, `ogImage`, `title`, and `highlightedText` [apps/browser-extension/entrypoints/content/shared.ts:10-41]().
2. Sends `MESSAGE_TYPES.SAVE_MEMORY` to the background script [apps/browser-extension/entrypoints/content/shared.ts:67-71]().
3. Background script resolves the `defaultProject` from storage to determine the target container [apps/browser-extension/utils/storage.ts:16]().

**Sources:** [apps/browser-extension/entrypoints/content/shared.ts:6-71](), [apps/browser-extension/entrypoints/content/t3.ts:212-243](), [apps/browser-extension/utils/storage.ts:16]()

---

## Configuration & UI State

The extension manages state using WXT's storage API.

| Key | Description | Type |
|-----------|-------|-------------|
| `autoSearchEnabled` | Toggles automatic memory search as user types. | `StorageItem<boolean>` |
| `autoCapturePromptsEnabled` | Toggles automatic saving of chat prompts. | `StorageItem<boolean>` |
| `defaultProject` | The target project/container for saved memories. | `StorageItem<Project>` |
| `bearerToken` | The authentication token for Supermemory API. | `StorageItem<string>` |

**Sources:** [apps/browser-extension/utils/storage.ts:13-16]()

### Feedback System
The extension provides visual feedback through `DOMUtils`:
- **Toasts:** Displays status notifications (loading, success, error) [apps/browser-extension/entrypoints/content/shared.ts:8-78]().
- **Icon Feedback:** Updates the injected icon text (e.g., "Searching memories...", "Included Memories") to reflect current API status [apps/browser-extension/entrypoints/content/t3.ts:202-245]().

**Sources:** [apps/browser-extension/entrypoints/content/shared.ts:8-78](), [apps/browser-extension/entrypoints/content/t3.ts:202-245]()

---

# Page: Twitter Bookmark Import

# Twitter Bookmark Import

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [apps/browser-extension/components/icons.tsx](apps/browser-extension/components/icons.tsx)
- [apps/browser-extension/entrypoints/background.ts](apps/browser-extension/entrypoints/background.ts)
- [apps/browser-extension/entrypoints/content/twitter.ts](apps/browser-extension/entrypoints/content/twitter.ts)
- [apps/browser-extension/entrypoints/popup/style.css](apps/browser-extension/entrypoints/popup/style.css)
- [apps/browser-extension/entrypoints/welcome/Welcome.tsx](apps/browser-extension/entrypoints/welcome/Welcome.tsx)
- [apps/browser-extension/package.json](apps/browser-extension/package.json)
- [apps/browser-extension/public/icon-48.png](apps/browser-extension/public/icon-48.png)
- [apps/browser-extension/public/logo-fullmark.svg](apps/browser-extension/public/logo-fullmark.svg)
- [apps/browser-extension/utils/api.ts](apps/browser-extension/utils/api.ts)
- [apps/browser-extension/utils/twitter-import.ts](apps/browser-extension/utils/twitter-import.ts)
- [apps/browser-extension/utils/twitter-utils.ts](apps/browser-extension/utils/twitter-utils.ts)
- [apps/browser-extension/utils/types.ts](apps/browser-extension/utils/types.ts)
- [apps/browser-extension/utils/ui-components.ts](apps/browser-extension/utils/ui-components.ts)

</details>



This page documents the Twitter/X bookmark import subsystem of the Supermemory browser extension. It covers the full flow from user-initiated import in the popup through content script orchestration, background processing, and progress reporting back to the page.

For general extension architecture and message-passing conventions, see [3.1](). For the UI components (`createProjectSelectionModal`, `createTwitterImportButton`, toast utilities) used here, see [3.4]().

---

## Overview

The Twitter bookmark import subsystem allows users to bulk-import their X/Twitter bookmarks (including folder-scoped bookmark collections) into Supermemory. It is composed of three cooperating parts:

| Part | File | Role |
|---|---|---|
| Popup UI | `entrypoints/popup/App.tsx` | Entry point; triggers navigation or sends modal-open message |
| Content Script | `entrypoints/content/twitter.ts` | DOM orchestration on x.com, modal display, progress toasts |
| Background Worker | `entrypoints/background.ts` | Runs `TwitterImporter`, relays progress to content script |

The `TwitterImporter` class performs the actual Twitter API pagination and Supermemory batch upload. Authentication tokens are captured passively from Twitter's outgoing web requests via `captureTwitterTokens()`.

Sources: [apps/browser-extension/entrypoints/background.ts:16-17](), [apps/browser-extension/entrypoints/background.ts:40-47](), [apps/browser-extension/utils/twitter-import.ts:61-65](), [apps/browser-extension/entrypoints/content/twitter.ts:84-124]()

---

## Import Entry Points

There are two ways to start an import.

### 1. Popup Button

The "Imports" tab in the popup contains an **Import X/Twitter Bookmarks** button.

When clicked, it checks whether the active tab is already on the bookmarks page (`x.com/i/bookmarks`):

- **Already on bookmarks page** → sends `MESSAGE_TYPES.TWITTER_IMPORT_OPEN_MODAL` directly to the content script.
- **Not on bookmarks page** → writes an expiring intent to `chrome.storage.local` under the key `STORAGE_KEYS.TWITTER_BOOKMARKS_IMPORT_INTENT_UNTIL`, then opens `https://x.com/i/bookmarks` in a new tab. The content script reads and consumes this intent on page load.

The intent TTL is defined as `UI_CONFIG.IMPORT_INTENT_TTL = 2 * 60 * 1000` (2 minutes).

Sources: [apps/browser-extension/entrypoints/popup/App.tsx:73-86](), [apps/browser-extension/utils/constants.ts:45-45](), [apps/browser-extension/entrypoints/content/twitter.ts:34-54]()

### 2. Folder-Level Import Buttons

On `/i/bookmarks`, the content script injects a button next to each bookmark folder element via `addTwitterImportButtonForFolders()`. Clicking it opens a project selection modal scoped to that folder's `bookmarkCollectionId`, extracted from the folder's `href` attribute.

Sources: [apps/browser-extension/entrypoints/content/twitter.ts:109-109](), [apps/browser-extension/utils/ui-components.ts:166-166]()

---

## Content Script Initialization Flow

**Diagram: Content script initialization on Twitter/X**

```mermaid
flowchart TD
    A["initializeTwitter()"] --> B{"pathname == /i/bookmarks?"}
    B -- "No" --> C["removeAllTwitterUI()"]
    B -- "Yes" --> D["setTimeout 2000ms"]
    D --> E["handleBookmarksPageLoad()"]
    E --> F["addTwitterImportButtonForFolders()"]
    F --> G["checkAndConsumeImportIntent()"]
    G -- "intent valid" --> H["openImportModal()"]
    G -- "no intent" --> I["hasOnboardingBeenShown()"]
    I -- "not shown" --> J["showOnboardingToast()"]
    I -- "already shown" --> K["(idle - await user action)"]
    J --> L["markOnboardingAsShown()"]
```

Sources: [apps/browser-extension/entrypoints/content/twitter.ts:84-124]()

The 2-second delay in `initializeTwitter` accommodates Twitter's SPA rendering. The `MutationObserver` in the content script index calls `handleTwitterNavigation()` on DOM changes, which re-runs `handleBookmarksPageLoad()` when the user navigates to the bookmarks route.

Sources: [apps/browser-extension/entrypoints/content/twitter.ts:84-100](), [apps/browser-extension/utils/constants.ts:50-50]()

---

## Import Intent TTL Mechanism

The intent mechanism bridges the popup (which runs in a separate context) to the content script on the newly opened tab.

```mermaid
sequenceDiagram
    participant Popup as "Popup (App.tsx)"
    participant Storage as "chrome.storage.local"
    participant Tab as "New tab (x.com/i/bookmarks)"
    participant CS as "Content Script (twitter.ts)"

    Popup->>Storage: "set TWITTER_BOOKMARKS_IMPORT_INTENT_UNTIL = now + 2min"
    Popup->>Tab: "chrome.tabs.create({ url: x.com/i/bookmarks })"
    Tab->>CS: "page load → initializeTwitter()"
    CS->>Storage: "get TWITTER_BOOKMARKS_IMPORT_INTENT_UNTIL"
    Storage-->>CS: "intentUntil timestamp"
    CS->>CS: "Date.now() < intentUntil? → consume & openImportModal()"
    CS->>Storage: "remove TWITTER_BOOKMARKS_IMPORT_INTENT_UNTIL"
```

Sources: [apps/browser-extension/entrypoints/content/twitter.ts:34-54](), [apps/browser-extension/utils/constants.ts:34-36]()

**Storage keys involved:**

| Key constant | `chrome.storage.local` key | Value |
|---|---|---|
| `STORAGE_KEYS.TWITTER_BOOKMARKS_IMPORT_INTENT_UNTIL` | `sm_twitter_bookmarks_import_intent_until` | Unix timestamp (ms) |
| `STORAGE_KEYS.TWITTER_BOOKMARKS_ONBOARDING_SEEN` | `sm_twitter_bookmarks_onboarding_seen` | boolean |

Sources: [apps/browser-extension/utils/constants.ts:32-36]()

---

## Onboarding Toast

When a user lands on `/i/bookmarks` for the first time (no import intent, onboarding not seen), `showOnboardingToast()` displays a one-time notification.

**Features of the onboarding toast:**

- Element ID: `ELEMENT_IDS.TWITTER_ONBOARDING_TOAST` (`sm-twitter-onboarding-toast`)
- Duration: `UI_CONFIG.ONBOARDING_TOAST_DURATION` = **6000ms**
- Animated gradient progress bar at bottom tracks auto-dismiss timer via `smProgressGrow` CSS keyframe
- Stored as seen via `markOnboardingAsShown()` before display, preventing re-show on refresh

Sources: [apps/browser-extension/entrypoints/content/twitter.ts:189-224](), [apps/browser-extension/utils/constants.ts:44-44]()

---

## Modal: `openImportModal()` (All Bookmarks)

`openImportModal()` is the single entry point for starting an import of all bookmarks (non-folder).

```mermaid
flowchart TD
    A["openImportModal()"] --> B["FETCH_PROJECTS → background"]
    B --> C{"projects.length == 0?"}
    C -- "Yes" --> D["BATCH_IMPORT_ALL (no project)"]
    C -- "No" --> E["showAllBookmarksProjectModal(projects)"]
    E --> F["createProjectSelectionModal(...)"]
    F --> G{"User selects project & clicks Import"}
    G --> H["BATCH_IMPORT_ALL + selectedProject"]
```

Sources: [apps/browser-extension/entrypoints/content/twitter.ts:129-153]()

---

## `BATCH_IMPORT_ALL` Message Flow

**Diagram: BATCH_IMPORT_ALL message from content script to background**

```mermaid
flowchart LR
    CS["Content Script\n(twitter.ts)"] -- "BATCH_IMPORT_ALL\n{ isFolderImport, bookmarkCollectionId, selectedProject }" --> BG["Background\n(background.ts)"]
    BG --> TI["new TwitterImporter(importConfig)"]
    TI -- "startImport()" --> API["saveAllTweets()\n→ POST /v3/documents/batch"]
    TI -- "onProgress(msg)" --> BG
    TI -- "onComplete(total)" --> BG
    BG -- "IMPORT_UPDATE\n{ importedMessage }" --> CS2["Content Script\n(twitter.ts)"]
    BG -- "IMPORT_DONE\n{ totalImported }" --> CS2
```

Sources: [apps/browser-extension/entrypoints/background.ts:176-192](), [apps/browser-extension/utils/api.ts:167-192]()

### `TwitterImportConfig` interface

The background worker instantiates `TwitterImporter` using the `TwitterImportConfig` object:

| Field | Type | Source |
|---|---|---|
| `isFolderImport` | `boolean \| undefined` | from `ExtensionMessage` |
| `bookmarkCollectionId` | `string \| undefined` | folder's URL slug |
| `selectedProject` | `Project \| undefined` | from project selection modal |
| `onProgress` | `(msg: string) => Promise<void>` | `sendMessageToCurrentTab` |
| `onComplete` | `(total: number) => Promise<void>` | `sendImportDoneMessage` |

Sources: [apps/browser-extension/entrypoints/background.ts:177-186](), [apps/browser-extension/utils/twitter-import.ts:23-34]()

### Batch upload API call

`saveAllTweets()` posts to `/v3/documents/batch` with a shared metadata group identifier:

```typescript
// apps/browser-extension/utils/api.ts:167-184
export async function saveAllTweets(
	documents: MemoryPayload[],
): Promise<unknown> {
	try {
		const response = await makeAuthenticatedRequest<unknown>(
			"/v3/documents/batch",
			{
				method: "POST",
				body: JSON.stringify({
					documents,
					metadata: {
						sm_source: "consumer",
						sm_internal_group_id: "twitter_bookmarks",
					},
				}),
			},
		)
		return response
	} catch (error) { ... }
}
```

409 Conflict responses (duplicate documents) are silently swallowed in `saveAllTweets`.

Sources: [apps/browser-extension/utils/api.ts:167-192]()

---

## Progress Reporting

Progress is displayed via `showOrUpdateImportProgressToast()` in the content script, which maintains a single persistent toast with element ID `ELEMENT_IDS.TWITTER_IMPORT_PROGRESS_TOAST` (`sm-twitter-import-progress-toast`).

| Message type | Handler | Toast behavior |
|---|---|---|
| `MESSAGE_TYPES.IMPORT_UPDATE` | `onProgress` callback | Creates or updates toast text with current progress message |
| `MESSAGE_TYPES.IMPORT_DONE` | `onComplete` callback | Displays total count and auto-dismisses |

Sources: [apps/browser-extension/entrypoints/background.ts:50-77](), [apps/browser-extension/utils/constants.ts:79-81]()

---

## Cleanup

`removeAllTwitterUI()` removes all injected elements when the user navigates away from `/i/bookmarks`:

| Removed element | Element ID constant |
|---|---|
| Import button | `ELEMENT_IDS.TWITTER_IMPORT_BUTTON` |
| Onboarding toast | `ELEMENT_IDS.TWITTER_ONBOARDING_TOAST` |
| Import progress toast | `ELEMENT_IDS.TWITTER_IMPORT_PROGRESS_TOAST` |

Sources: [apps/browser-extension/utils/constants.ts:16-19](), [apps/browser-extension/entrypoints/content/twitter.ts:97-98]()

---

## Required Permissions

The extension declares the following permissions relevant to Twitter import in `wxt.config.ts`:

| Permission | Purpose |
|---|---|
| `host_permissions: *://x.com/*` | Content script injection and web request interception |
| `host_permissions: *://twitter.com/*` | Legacy domain support |
| `webRequest` | Capturing Twitter auth tokens via `onBeforeSendHeaders` |
| `storage` | Persisting intent TTL and onboarding-seen flag |
| `tabs` | Opening `x.com/i/bookmarks` tab and querying active tab |

Sources: [apps/browser-extension/wxt.config.ts:33-42](), [apps/browser-extension/entrypoints/background.ts:40-47]()

---

# Page: UI Components & Storage

# UI Components & Storage

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [apps/browser-extension/components/icons.tsx](apps/browser-extension/components/icons.tsx)
- [apps/browser-extension/entrypoints/background.ts](apps/browser-extension/entrypoints/background.ts)
- [apps/browser-extension/entrypoints/content/chatgpt.ts](apps/browser-extension/entrypoints/content/chatgpt.ts)
- [apps/browser-extension/entrypoints/content/shared.ts](apps/browser-extension/entrypoints/content/shared.ts)
- [apps/browser-extension/entrypoints/content/t3.ts](apps/browser-extension/entrypoints/content/t3.ts)
- [apps/browser-extension/entrypoints/content/twitter.ts](apps/browser-extension/entrypoints/content/twitter.ts)
- [apps/browser-extension/entrypoints/popup/style.css](apps/browser-extension/entrypoints/popup/style.css)
- [apps/browser-extension/entrypoints/welcome/Welcome.tsx](apps/browser-extension/entrypoints/welcome/Welcome.tsx)
- [apps/browser-extension/package.json](apps/browser-extension/package.json)
- [apps/browser-extension/public/icon-48.png](apps/browser-extension/public/icon-48.png)
- [apps/browser-extension/public/logo-fullmark.svg](apps/browser-extension/public/logo-fullmark.svg)
- [apps/browser-extension/utils/api.ts](apps/browser-extension/utils/api.ts)
- [apps/browser-extension/utils/storage.ts](apps/browser-extension/utils/storage.ts)
- [apps/browser-extension/utils/twitter-auth.ts](apps/browser-extension/utils/twitter-auth.ts)
- [apps/browser-extension/utils/twitter-import.ts](apps/browser-extension/utils/twitter-import.ts)
- [apps/browser-extension/utils/twitter-utils.ts](apps/browser-extension/utils/twitter-utils.ts)
- [apps/browser-extension/utils/types.ts](apps/browser-extension/utils/types.ts)
- [apps/browser-extension/utils/ui-components.ts](apps/browser-extension/utils/ui-components.ts)
- [apps/web/public/images/plugins/codex.png](apps/web/public/images/plugins/codex.png)

</details>



## Purpose and Scope

This document covers the UI component system and browser storage patterns used in the Supermemory browser extension. It details the reusable component factories, popup interface, injected content elements, and persistent storage mechanisms. For information about the extension's overall architecture and message passing, see [Extension Architecture (3.1)](). For AI chat integration functionality, see [AI Chat Integration (3.2)]().

---

## UI Component Architecture

The extension implements a component system that creates DOM elements programmatically rather than using a templating system. Components are divided into two categories: the popup interface rendered in React, and content script components injected into web pages as native DOM elements.

### Component Type Hierarchy

**Popup components** (React, rendered via `entrypoints/popup/App.tsx`) and **content script components** (native DOM, created by `utils/ui-components.ts`) are entirely separate rendering contexts. Popup components use Tailwind CSS utility classes; content script components use inline `style.cssText` strings to avoid host-page style conflicts [apps/browser-extension/utils/ui-components.ts:18-36]().

```mermaid
graph TB
    subgraph "Popup UI (React — entrypoints/popup/App.tsx)"
        PopupApp["App"]
        AuthView["Authentication View"]
        SaveTab["Save Tab"]
        ImportsTab["Imports Tab"]
        SettingsTab["Settings Tab"]
        ProjectSelector["Project Selector Dropdown"]
    end

    subgraph "Content Script UI (Native DOM — utils/ui-components.ts)"
        ToastFactory["createToast()"]
        ButtonFactories["Button Factories"]
        ModalFactory["createProjectSelectionModal()"]
    end

    subgraph "Button Factories"
        TwitterButton["createTwitterImportButton()"]
        TweetButton["createSaveTweetElement()"]
        ChatGPTButton["createChatGPTInputBarElement()"]
        ClaudeButton["createClaudeInputBarElement()"]
        T3Button["createT3InputBarElement()"]
    end

    subgraph "Utility Layer"
        DOMUtils["DOMUtils object"]
        Constants["ELEMENT_IDS, UI_CONFIG (utils/constants.ts)"]
    end

    PopupApp --> AuthView
    PopupApp --> SaveTab
    PopupApp --> ImportsTab
    PopupApp --> SettingsTab
    SaveTab --> ProjectSelector

    ButtonFactories --> TwitterButton
    ButtonFactories --> TweetButton
    ButtonFactories --> ChatGPTButton
    ButtonFactories --> ClaudeButton
    ButtonFactories --> T3Button

    ToastFactory --> DOMUtils
    ButtonFactories --> DOMUtils
    ModalFactory --> DOMUtils

    DOMUtils --> Constants
```

Sources: [apps/browser-extension/utils/ui-components.ts:14-166](), [apps/browser-extension/utils/ui-components.ts:395-400]()

---

## Popup UI Components

### Main Popup Interface

The popup is a React application rendered when users click the extension icon. It uses a fixed-width container with a dark background [apps/browser-extension/entrypoints/popup/style.css:7-10]() and provides three main tabs: "save", "imports", and "settings".

#### Popup Structure

```mermaid
graph TB
    PopupRoot["div<br/>Fixed 320px width<br/>Dark background"]
    
    Header["Header<br/>Logo + User info + Logout"]
    TabNav["Tab Navigation<br/>Save | Imports | Settings"]
    
    SaveContent["Save Tab Content"]
    ImportsContent["Imports Tab Content"]
    SettingsContent["Settings Tab Content"]
    
    SaveContent --> CurrentPageInfo["Current Page Info Card"]
    SaveContent --> SpaceSelector["Space Selector"]
    SaveContent --> SaveButton["Save Button"]
    
    ImportsContent --> ChatGPTImport["ChatGPT Memories Import"]
    ImportsContent --> TwitterImport["Twitter Bookmarks Import"]
    
    SettingsContent --> EmailDisplay["Email Display"]
    SettingsContent --> AutoSearchToggle["Auto Search Toggle"]
    SettingsContent --> AutoCaptureToggle["Auto Capture Prompts Toggle"]
    
    PopupRoot --> Header
    PopupRoot --> TabNav
    TabNav --> SaveContent
    TabNav --> ImportsContent
    TabNav --> SettingsContent
```

Sources: [apps/browser-extension/entrypoints/popup/style.css:1-17](), [apps/browser-extension/entrypoints/popup/style.css:7-10]()

### Authentication Flow

The popup validates the user's session using the `validateAuthToken` utility [apps/browser-extension/utils/api.ts:101-112]().

```mermaid
sequenceDiagram
    participant User
    participant PopupApp as "App.tsx"
    participant Storage as "bearerToken (storage.ts)"
    participant API as "validateAuthToken (api.ts)"
    
    User->>PopupApp: Opens popup
    PopupApp->>Storage: bearerToken.getValue()
    Storage-->>PopupApp: token or null
    
    alt Token exists
        PopupApp->>API: validateAuthToken()
        alt Token valid
            API-->>PopupApp: true
        else Token invalid
            API-->>PopupApp: false
            PopupApp->>Storage: Remove token
        end
    end
```

Sources: [apps/browser-extension/utils/api.ts:101-112](), [apps/browser-extension/utils/storage.ts:15]()

---

## Content Script UI Components

### Toast Notifications

Toast notifications appear in the top-right corner of web pages to provide feedback for extension actions. The `createToast()` function generates a toast element with three states [apps/browser-extension/utils/ui-components.ts:14-16]().

#### Toast States

| State | Icon | Text |
|-------|------|------|
| `loading` | Spinning loader (indigo) | "Adding to Memory..." [apps/browser-extension/utils/ui-components.ts:116]() |
| `success` | Extension icon (`/icon-16.png`) | "Added to Memory" [apps/browser-extension/utils/ui-components.ts:122]() |
| `error` | Red X circle | "Failed to save memory" + "Make sure you are logged in" [apps/browser-extension/utils/ui-components.ts:140-145]() |

The toast uses inline styles with animations defined in a dynamically injected `<style>` element with ID `supermemory-toast-styles` [apps/browser-extension/utils/ui-components.ts:41-42](). It also handles font injection for "Space Grotesk" via `chrome.runtime.getURL` [apps/browser-extension/utils/ui-components.ts:43-77]().

Sources: [apps/browser-extension/utils/ui-components.ts:14-159]()

### Injected Button Components

The extension injects save and search buttons into various platforms' UI. Each platform has a dedicated factory function in `utils/ui-components.ts`.

#### Button Factory Functions

| Function | Element ID constant | Platform Target |
|----------|---------------------|-----------------|
| `createTwitterImportButton` | `TWITTER_IMPORT_BUTTON` | Twitter Bookmarks page [apps/browser-extension/utils/ui-components.ts:166-172]() |
| `createChatGPTInputBarElement` | `CHATGPT_INPUT_BAR_ELEMENT` | ChatGPT interface [apps/browser-extension/entrypoints/content/chatgpt.ts:13]() |
| `createT3InputBarElement` | `T3_INPUT_BAR_ELEMENT` | T3.chat interface [apps/browser-extension/entrypoints/content/t3.ts:12]() |
| `createSaveTweetElement` | `SAVE_TWEET_ELEMENT` | Twitter individual tweets [apps/browser-extension/utils/ui-components.ts:245-250]() |

Sources: [apps/browser-extension/utils/ui-components.ts:166-250](), [apps/browser-extension/entrypoints/content/t3.ts:12](), [apps/browser-extension/entrypoints/content/chatgpt.ts:13]()

### Project Selection Modal

The `createProjectSelectionModal()` function creates a full-screen overlay modal for selecting a project/space when importing content [apps/browser-extension/utils/ui-components.ts:395-400](). This is primarily used during the Twitter bookmark import flow in `entrypoints/content/twitter.ts` [apps/browser-extension/entrypoints/content/twitter.ts:160-181]().

**Behavior:**
1. **Dynamic Project Loading**: Initially renders with empty projects array, then updates via `updateModalWithProjects()`.
2. **Selection State**: Import button disabled until user selects a project.
3. **Dismissal**: Clicking overlay, Cancel button, or Escape key closes modal.
4. **Font Loading**: Calls `loadSpaceGroteskFonts()` to ensure consistent typography [apps/browser-extension/entrypoints/content/twitter.ts:16-29]().

Sources: [apps/browser-extension/utils/ui-components.ts:395-644](), [apps/browser-extension/entrypoints/content/twitter.ts:160-181]()

---

## Storage System

### Browser Storage API Usage

The extension uses the WXT storage wrapper around `chrome.storage.local` for persistence [apps/browser-extension/utils/storage.ts:1-20]().

#### Storage Pattern Architecture

```mermaid
graph TB
    subgraph "High-Level API (storage.ts)"
        BearerToken["bearerToken"]
        UserData["userData"]
        DefaultProject["defaultProject"]
        AutoSearch["autoSearchEnabled"]
        AutoCapture["autoCapturePromptsEnabled"]
    end
    
    subgraph "Storage Keys (utils/constants.ts)"
        OnboardingKey["TWITTER_BOOKMARKS_ONBOARDING_SEEN"]
        IntentKey["TWITTER_BOOKMARKS_IMPORT_INTENT_UNTIL"]
    end
    
    subgraph "Browser Storage API"
        LocalStorage["chrome.storage.local"]
    end
    
    BearerToken --> LocalStorage
    UserData --> LocalStorage
    DefaultProject --> LocalStorage
    AutoSearch --> LocalStorage
    AutoCapture --> LocalStorage
    
    OnboardingKey --> LocalStorage
    IntentKey --> LocalStorage
```

Sources: [apps/browser-extension/utils/storage.ts:1-20](), [apps/browser-extension/utils/constants.ts:32-36]()

### Storage Keys Reference

| Key | Type | Purpose |
|-----|------|---------|
| `TWITTER_BOOKMARKS_ONBOARDING_SEEN` | `boolean` | Tracks if onboarding toast was shown [apps/browser-extension/utils/constants.ts:33]() |
| `TWITTER_BOOKMARKS_IMPORT_INTENT_UNTIL` | `number` | TTL for import intent [apps/browser-extension/utils/constants.ts:34-35]() |
| `bearerToken` | `string` | User's JWT authentication token [apps/browser-extension/utils/storage.ts:15]() |
| `userData` | `object` | Cached user profile (email, name) [apps/browser-extension/utils/storage.ts:17]() |
| `defaultProject` | `Project` | Currently selected project for saves [apps/browser-extension/utils/storage.ts:16]() |

Sources: [apps/browser-extension/utils/constants.ts:32-36](), [apps/browser-extension/utils/storage.ts:1-20]()

---

## API Utility Functions

The `utils/api.ts` module provides authenticated wrappers for the Supermemory API using the `makeAuthenticatedRequest` helper [apps/browser-extension/utils/api.ts:30-57]().

| Function | Endpoint | Purpose |
|----------|----------|---------|
| `fetchProjects` | `/v3/projects` | Retrieves list of user projects [apps/browser-extension/utils/api.ts:62-65]() |
| `saveMemory` | `/v3/documents` | POSTs new memory content [apps/browser-extension/utils/api.ts:132-137]() |
| `searchMemories` | `/v4/search` | Performs vector search on memories [apps/browser-extension/utils/api.ts:148-156]() |
| `saveAllTweets` | `/v3/documents/batch` | Batch save for Twitter bookmarks [apps/browser-extension/utils/api.ts:167-173]() |
| `validateAuthToken`| `/v3/projects` | Checks if current token is valid [apps/browser-extension/utils/api.ts:101-112]() |

Sources: [apps/browser-extension/utils/api.ts:1-192]()

---

# Page: AI Tools Package

# AI Tools Package

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [biome.json](biome.json)
- [packages/tools/README.md](packages/tools/README.md)
- [packages/tools/package.json](packages/tools/package.json)
- [packages/tools/src/ai-sdk.ts](packages/tools/src/ai-sdk.ts)
- [packages/tools/src/openai/tools.ts](packages/tools/src/openai/tools.ts)
- [packages/tools/src/tools-shared.ts](packages/tools/src/tools-shared.ts)
- [packages/tools/src/tools.test.ts](packages/tools/src/tools.test.ts)
- [packages/tools/src/types.ts](packages/tools/src/types.ts)
- [packages/tools/src/vercel/index.ts](packages/tools/src/vercel/index.ts)
- [packages/tools/src/vercel/logger.ts](packages/tools/src/vercel/logger.ts)
- [packages/tools/src/vercel/memory-prompt.ts](packages/tools/src/vercel/memory-prompt.ts)
- [packages/tools/src/vercel/middleware.ts](packages/tools/src/vercel/middleware.ts)
- [packages/tools/src/vercel/util.ts](packages/tools/src/vercel/util.ts)

</details>



## Purpose and Scope

The `@supermemory/tools` package provides memory enhancement middleware and function-calling tools for AI applications. It serves as a bridge between the Supermemory API and popular AI frameworks, including the **Vercel AI SDK** (v2 and v3), **OpenAI SDK**, **Mastra**, and **VoltAgent** [packages/tools/package.json:5]().

The package enables two primary workflows:
1. **Automatic Injection**: Transparently enhancing AI prompts with relevant user memories via middleware that intercepts LLM calls [packages/tools/src/vercel/index.ts:66-72]().
2. **Explicit Operations**: Providing the AI with function-calling tools to search, add, or manage memories [packages/tools/src/ai-sdk.ts:13-119]().

A key optimization is **per-turn memory caching** implemented via `MemoryCache` [packages/tools/src/vercel/middleware.ts:160-164](), which avoids redundant API calls during multi-step tool interactions or multi-step generation flows by reusing memories within the same user turn [packages/tools/src/vercel/middleware.ts:248-255]().

**Sources:** [packages/tools/package.json:1-21](), [packages/tools/README.md:1-18](), [packages/tools/src/vercel/middleware.ts:160-164]()

---

## Package Architecture

The package is organized around submodule exports to provide tailored integrations for different frameworks while sharing a common core for memory retrieval and formatting.

### Package Exports and File Structure

**Package exports mapped to source files**

```mermaid
graph TB
    subgraph "Package_Exports_(@supermemory/tools/)"
        AISDKExport["ai-sdk"]
        OpenAIExport["openai"]
        MastraExport["mastra"]
        VoltAgentExport["voltagent"]
        ClaudeMemory["claude-memory"]
    end

    subgraph "src/vercel/_(AI_SDK_Core)"
        VercelIndex["index.ts<br/>wrapVercelLanguageModel()<br/>withSupermemory()"]
        VercelMiddleware["middleware.ts<br/>transformParamsWithMemory()<br/>saveMemoryAfterResponse()"]
        VercelPrompt["memory-prompt.ts<br/>extractQueryText()<br/>injectMemoriesIntoParams()"]
    end

    subgraph "src/_(Framework_Adapters)"
        MastraSrc["mastra.ts<br/>withSupermemory()<br/>createSupermemoryProcessors()"]
        VoltAgentSrc["voltagent/index.ts<br/>withSupermemory()<br/>createSupermemoryProcessors()"]
        ClaudeSrc["claude-memory.ts<br/>createClaudeMemoryTool()"]
    end

    subgraph "Shared_Infrastructure"
        ConversationsClient["conversations-client.ts<br/>addConversation()"]
        SharedModule["shared.ts<br/>buildMemoriesText()<br/>MemoryCache<br/>normalizeBaseUrl()"]
        ToolsShared["tools-shared.ts<br/>TOOL_DESCRIPTIONS<br/>getContainerTags()"]
    end

    AISDKExport --> VercelIndex
    VercelIndex --> VercelMiddleware
    VercelMiddleware --> VercelPrompt
    VercelMiddleware --> ConversationsClient
    VercelMiddleware --> SharedModule

    MastraExport --> MastraSrc
    VoltAgentExport --> VoltAgentSrc
    ClaudeMemory --> ClaudeSrc
    
    MastraSrc --> SharedModule
    VoltAgentSrc --> SharedModule
```

**Sources:** [packages/tools/package.json:49-57](), [packages/tools/src/vercel/index.ts:1-12](), [packages/tools/src/ai-sdk.ts:1-10](), [packages/tools/src/tools-shared.ts:6-21]()

### Core Dependencies

| Dependency | Purpose | Version |
|------------|---------|---------|
| `@ai-sdk/provider` | `LanguageModelV2` / `LanguageModelV3` interface types | ^3.0.0 |
| `ai` | Vercel AI SDK core components and `tool()` helper | ^5.0.29 |
| `openai` | Direct OpenAI SDK integration and type definitions | ^4.104.0 |
| `supermemory` | Official Supermemory API client | ^3.0.0-alpha.26 |
| `@mastra/core` | Integration for Mastra AI agents | ^1.0.0 |
| `@voltagent/core` | Integration for VoltAgent agents | ^2.6.12 |

**Sources:** [packages/tools/package.json:13-32]()

---

## Integration Approaches

### 1. Middleware Pattern (Transparent)

The middleware approach intercepts AI calls to automatically enrich prompts with relevant memories. This is implemented via `withSupermemory()` which wraps `LanguageModel` instances for Vercel AI SDK [packages/tools/src/vercel/index.ts:111-144]().

**Middleware Request-Response Flow with Per-Turn Caching**

```mermaid
sequenceDiagram
    participant App as "Application Code"
    participant Wrapped as "wrapVercelLanguageModel<br/>(Proxy)"
    participant Transform as "transformParamsWithMemory()"
    participant Cache as "MemoryCache<br/>(LRU Cache)"
    participant API as "Supermemory API<br/>/v4/profile"
    participant LLM as "Actual AI Model<br/>(doGenerate)"
    
    App->>Wrapped: generateText({messages})
    Wrapped->>Transform: params, context
    Transform->>Transform: makeTurnKey(containerTag, userMessage)
    Transform->>Cache: memoryCache.get(turnKey)
    
    alt Cache Hit
        Cache-->>Transform: cached memories
    else Cache Miss
        Transform->>API: buildMemoriesText()
        API-->>Transform: Formatted Memories
        Transform->>Cache: memoryCache.set(turnKey, memories)
    end
    
    Transform->>LLM: transformedParams (with injected memories)
    LLM-->>Wrapped: result
    
    alt addMemory: "always"
        Wrapped->>API: saveMemoryAfterResponse()
    end
    
    Wrapped-->>App: result
```

For detailed implementation of the middleware lifecycle, see [Middleware Integration](#4.1).

**Sources:** [packages/tools/src/vercel/middleware.ts:232-263](), [packages/tools/src/vercel/middleware.ts:248-255](), [packages/tools/src/vercel/index.ts:144-180](), [packages/tools/src/vercel/middleware.ts:78-113]()

### 2. Function Calling Pattern (Explicit)

The function-calling approach provides a suite of tools that the AI can explicitly invoke. This gives the model control over when to query its "long-term memory" or when to save a specific fact.

**Available Tools and Descriptions**

| Tool Name | Purpose | Code Reference |
|-----------|---------|----------------|
| `searchMemories` | Semantic search for specific information | [packages/tools/src/tools-shared.ts:7-8]() |
| `addMemory` | Save a short fact or sentence to memory | [packages/tools/src/tools-shared.ts:9-10]() |
| `getProfile` | Retrieve the full user profile (static/dynamic) | [packages/tools/src/tools-shared.ts:11-12]() |
| `documentList` | List stored documents with filtering | [packages/tools/src/tools-shared.ts:13-14]() |
| `documentAdd` | Queue content/URL for processing | [packages/tools/src/tools-shared.ts:17-18]() |
| `documentDelete` | Permanently delete saved content | [packages/tools/src/tools-shared.ts:15-16]() |
| `memoryForget` | Soft-delete a specific memory entry | [packages/tools/src/tools-shared.ts:19-21]() |

For tool schemas and parameter details, see [Function Calling Tools](#4.2).

**Sources:** [packages/tools/src/ai-sdk.ts:13-119](), [packages/tools/src/openai/tools.ts:67-219](), [packages/tools/src/tools-shared.ts:6-21]()

---

## Memory Enhancement Logic

The middleware uses `transformParamsWithMemory` to fetch and format data. It supports three distinct modes:
- **`profile`**: Default. Retrieves user profile memories (static + dynamic) without query filtering [packages/tools/src/vercel/middleware.ts:129]().
- **`query`**: Searches memories based on semantic similarity to the last user message [packages/tools/src/vercel/middleware.ts:130]().
- **`full`**: Combines both profile and query-based results [packages/tools/src/vercel/middleware.ts:131]().

### Context and State Management
- **`containerTag`**: The primary scoping identifier (e.g., a user ID or project ID) used to isolate memories [packages/tools/src/vercel/middleware.ts:120]().
- **`customId`**: Required ID to group messages into a single document for contextual memory generation [packages/tools/src/vercel/middleware.ts:124]().
- **`addMemory`**: Determines if the middleware should automatically persist the assistant's response and user's prompt via `saveMemoryAfterResponse` [packages/tools/src/vercel/middleware.ts:135-139]().

For configuration options and advanced patterns, see [Configuration & Usage Patterns](#4.3).

**Sources:** [packages/tools/src/vercel/middleware.ts:118-146](), [packages/tools/src/vercel/memory-prompt.ts:23-48](), [packages/tools/src/vercel/index.ts:123-140]()

---

## Specialized Framework Integrations

Beyond the standard Vercel AI SDK and OpenAI integrations, the package provides specialized support for:

- **Mastra & Claude**: Wrappers for Mastra agents and a native Claude memory tool compatible with `memory_20250818`. See [Mastra & Claude Memory Integration](#4.4).
- **VoltAgent**: Hook-based integration using `createSupermemoryProcessors` for input/output transformation. See [VoltAgent Integration](#4.5).

**Sources:** [packages/tools/package.json:52-55](), [packages/tools/README.md:15-18]()

---

# Page: Middleware Integration

# Middleware Integration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [packages/tools/README.md](packages/tools/README.md)
- [packages/tools/package.json](packages/tools/package.json)
- [packages/tools/src/openai/index.ts](packages/tools/src/openai/index.ts)
- [packages/tools/src/openai/middleware.ts](packages/tools/src/openai/middleware.ts)
- [packages/tools/src/vercel/index.ts](packages/tools/src/vercel/index.ts)
- [packages/tools/src/vercel/memory-prompt.ts](packages/tools/src/vercel/memory-prompt.ts)
- [packages/tools/src/vercel/middleware.ts](packages/tools/src/vercel/middleware.ts)
- [packages/tools/src/vercel/util.ts](packages/tools/src/vercel/util.ts)
- [packages/tools/test/chatapp/app/api/openai-chat/route.ts](packages/tools/test/chatapp/app/api/openai-chat/route.ts)
- [packages/tools/test/openai-responses-test.ts](packages/tools/test/openai-responses-test.ts)

</details>



This page documents the `withSupermemory` middleware for the **Vercel AI SDK** and the **OpenAI SDK**, both exported from the `@supermemory/tools` package [[packages/tools/package.json:1-5]](). The middleware intercepts outgoing LLM calls, fetches memories from Supermemory, injects them into the system prompt, and optionally saves conversation turns back to Supermemory.

---

## Package Structure

The `@supermemory/tools` package uses submodule exports to provide framework-specific logic while sharing core utilities.

| Export path | File | Description |
|---|---|---|
| `@supermemory/tools/ai-sdk` | [[packages/tools/src/vercel/index.ts:1-110]]() | Vercel AI SDK (`LanguageModelV2`/`V3`) wrapper |
| `@supermemory/tools/openai` | [[packages/tools/src/openai/index.ts:1-131]]() | OpenAI SDK client wrapper |

Sources: [[packages/tools/package.json:49-57]]()

---

## Vercel AI SDK Middleware

### `withSupermemory` (Vercel)

Exported as `wrapVercelLanguageModel` and aliased as `withSupermemory`. It wraps any Vercel AI SDK language model object (compatible with both SDK v5 `LanguageModelV2` and SDK v6 `LanguageModelV3`) by overriding its `doGenerate` and `doStream` methods using a `Proxy` [[packages/tools/src/vercel/index.ts:111-144]]().

**Signature:**
```typescript
withSupermemory(model, options) => WrappedModel
```

Sources: [[packages/tools/src/vercel/index.ts:111-114]]()

---

**Vercel Middleware — Call Flow Diagram**

```mermaid
sequenceDiagram
    participant "Caller" as [Caller]
    participant "withSupermemory" as [wrapVercelLanguageModel]
    participant "TPM" as [transformParamsWithMemory]
    participant "BM" as [buildMemoriesText]
    participant "MC" as [MemoryCache]
    participant "LM" as [LanguageModel]
    participant "SM" as [saveMemoryAfterResponse]

    Caller->>"withSupermemory": "doGenerate(params) or doStream(params)"
    "withSupermemory"->>"TPM": "transformParamsWithMemory(params, ctx)"
    "TPM"->>"MC": "cache.get(turnKey)"
    alt "cache hit (tool-call continuation)"
        "MC"-->>"TPM": "cached memories string"
    else "cache miss (new user turn)"
        "TPM"->>"BM": "buildMemoriesText({containerTag, queryText, mode})"
        "BM"-->>"TPM": "formatted memories string"
        "TPM"->>"MC": "cache.set(turnKey, memories)"
    end
    "TPM"->>"TPM": "injectMemoriesIntoParams(params, memories)"
    "TPM"-->>"withSupermemory": "transformedParams"
    "withSupermemory"->>"LM": "model.doGenerate(transformedParams)"
    "LM"-->>"withSupermemory": "result"
    opt "addMemory === 'always'"
        "withSupermemory"->>"SM": "saveMemoryAfterResponse(...)"
        note over "SM": "fire-and-forget, no await"
    end
    "withSupermemory"-->>Caller: "result"
```

Sources: [[packages/tools/src/vercel/index.ts:144-187]](), [[packages/tools/src/vercel/middleware.ts:232-321]]()

---

### Context Initialization — `createSupermemoryContext`

`createSupermemoryContext` is called once when `withSupermemory` is invoked. It initializes a `SupermemoryMiddlewareContext` object that is shared across all calls to `doGenerate` and `doStream` on the wrapped model [[packages/tools/src/vercel/middleware.ts:166-206]]().

| Context field | Source / Implementation |
|---|---|
| `client` | `new Supermemory({ apiKey, baseURL? })` [[packages/tools/src/vercel/middleware.ts:184-189]]() |
| `logger` | `createLogger(verbose)` — logs to console when `verbose: true` [[packages/tools/src/vercel/middleware.ts:181]]() |
| `memoryCache` | `new MemoryCache<string>()` — per-instance, keyed by turn [[packages/tools/src/vercel/middleware.ts:204]]() |
| `containerTag` | Identifier for memory search (e.g., user ID) [[packages/tools/src/vercel/middleware.ts:170]]() |
| `mode` | `"profile"`, `"query"`, or `"full"` [[packages/tools/src/vercel/middleware.ts:174]]() |
| `addMemory` | `"always"` or `"never"` [[packages/tools/src/vercel/middleware.ts:175]]() |

Sources: [[packages/tools/src/vercel/middleware.ts:148-164]]()

---

### Memory Injection — `transformParamsWithMemory`

`transformParamsWithMemory` is the core transformation step [[packages/tools/src/vercel/middleware.ts:232-235]]():

1. Extracts the last user message via `getLastUserMessage` [[packages/tools/src/vercel/util.ts:50-74]]().
2. Generates a `turnKey` via `makeTurnKey` which uses `MemoryCache.makeTurnKey` [[packages/tools/src/vercel/middleware.ts:212-222]]().
3. Detects if this is a **new user turn** (last message role is `"user"`) via `isNewUserTurn` [[packages/tools/src/vercel/middleware.ts:227-230]]().
4. On a tool-call continuation with a cached result, skips the API call and reuses the cached string [[packages/tools/src/vercel/middleware.ts:249-255]]().
5. Otherwise, calls `buildMemoriesText` which triggers a request to the Supermemory API [[packages/tools/src/vercel/memory-prompt.ts:109-117]]().
6. Calls `injectMemoriesIntoParams` to modify the system prompt [[packages/tools/src/vercel/memory-prompt.ts:59-88]]().

Sources: [[packages/tools/src/vercel/middleware.ts:232-321]](), [[packages/tools/src/vercel/memory-prompt.ts:59-88]]()

---

### Memory Persistence — `saveMemoryAfterResponse`

When `addMemory: "always"`, the middleware calls `saveMemoryAfterResponse` after the LLM responds [[packages/tools/src/vercel/middleware.ts:78-87]](). This is **fire-and-forget** (no `await`), so it does not block the response stream [[packages/tools/src/vercel/index.ts:180-187]]().

It converts the Vercel `LanguageModelCallOptions` and the assistant response into `ConversationMessage[]` using `convertToConversationMessages` [[packages/tools/src/vercel/middleware.ts:18-76]](), then calls `addConversation` from the `conversations-client` which POSTs to `/v4/conversations` [[packages/tools/src/vercel/middleware.ts:94-100]]().

Sources: [[packages/tools/src/vercel/middleware.ts:78-113]](), [[packages/tools/src/vercel/index.ts:180-187]]()

---

## OpenAI SDK Middleware

### `withSupermemory` (OpenAI)

Exported from [[packages/tools/src/openai/index.ts:62-99]](). It wraps an existing `OpenAI` client instance by calling `createOpenAIMiddleware` [[packages/tools/src/openai/index.ts:87-96]]().

**Signature:**
```typescript
withSupermemory(openaiClient, options) => OpenAI
```

Sources: [[packages/tools/src/openai/index.ts:62-65]]()

---

**OpenAI Middleware — Call Flow Diagram**

```mermaid
sequenceDiagram
    participant "Caller" as [Caller]
    participant "CWM" as [createOpenAIMiddleware]
    participant "SPS" as [supermemoryProfileSearch]
    participant "ASP" as [addSystemPrompt]
    participant "OC" as [originalCreate]

    Caller->>"CWM": "chat.completions.create(params)"
    "CWM"->>"SPS": "supermemoryProfileSearch(containerTag, queryText, baseUrl)"
    "SPS"-->>"CWM": "profile + searchResults"
    "CWM"->>"ASP": "addSystemPrompt(messages, containerTag, logger, mode, baseUrl)"
    "ASP"-->>"CWM": "enhancedMessages"
    "CWM"->>"OC": "originalCreate({ ...params, messages: enhancedMessages })"
    "OC"-->>"CWM": "completion"
    "CWM"-->>Caller: "completion"
```

Sources: [[packages/tools/src/openai/middleware.ts:158-164]](), [[packages/tools/src/openai/index.ts:87-96]]()

---

## Component Relationship Diagram

```mermaid
graph TD
    subgraph "Vercel SDK Integration"
        VI["[vercel/index.ts]\nwithSupermemory"]
        VM["[vercel/middleware.ts]\ntransformParamsWithMemory\nsaveMemoryAfterResponse"]
        VMP["[vercel/memory-prompt.ts]\ninjectMemoriesIntoParams"]
    end

    subgraph "OpenAI SDK Integration"
        OI["[openai/index.ts]\nwithSupermemory"]
        OM["[openai/middleware.ts]\ncreateOpenAIMiddleware\nsupermemoryProfileSearch"]
    end

    subgraph "Core Shared Logic"
        CC["[conversations-client.ts]\naddConversation"]
        SH["[shared.ts]\nbuildMemoriesText\nMemoryCache"]
    end

    VI --> VM
    VM --> VMP
    VM --> CC
    VM --> SH
    OI --> OM
    OM --> CC
    OM --> SH
```

Sources: [[packages/tools/src/vercel/index.ts]](), [[packages/tools/src/vercel/middleware.ts]](), [[packages/tools/src/openai/index.ts]](), [[packages/tools/src/openai/middleware.ts]]()

---

## Configuration Options

Both `withSupermemory` variants accept an options object:

| Option | Type | Default | Description |
|---|---|---|---|
| `containerTag` | `string` | (Required) | Identifier for memory search (e.g., user ID, project ID) [[packages/tools/src/vercel/index.ts:19]](). |
| `customId`| `string` | (Required) | Groups messages into one document for contextual memory generation [[packages/tools/src/vercel/index.ts:21]](). |
| `verbose` | `boolean` | `false` | Enables detailed logging of memory search and injection [[packages/tools/src/vercel/index.ts:23]](). |
| `mode` | `"profile" \| "query" \| "full"` | `"profile"` | Retrieval mode: user profile, semantic search, or both [[packages/tools/src/vercel/index.ts:30]](). |
| `addMemory` | `"always" \| "never"` | `"always"` | Automatically save conversations as memories [[packages/tools/src/vercel/index.ts:36]](). |
| `apiKey` | `string` | `env.SUPERMEMORY_API_KEY` | Supermemory API key [[packages/tools/src/vercel/index.ts:38]](). |
| `promptTemplate`| `PromptTemplate` | Default | Custom function to format memory data into the system prompt [[packages/tools/src/vercel/index.ts:56]](). |

Sources: [[packages/tools/src/vercel/index.ts:17-63]](), [[packages/tools/src/vercel/middleware.ts:118-146]](), [[packages/tools/src/openai/middleware.ts:14-23]]()

---

## Memory Modes

| Mode | Behavior |
|---|---|
| `"profile"` | Retrieves user profile memories (static + dynamic) without query filtering [[packages/tools/src/vercel/middleware.ts:129]](). |
| `"query"` | Searches memories based on semantic similarity to the user's message [[packages/tools/src/vercel/middleware.ts:130]](). |
| `"full"` | Combines both profile and query-based results [[packages/tools/src/vercel/middleware.ts:131]](). |

Sources: [[packages/tools/src/vercel/middleware.ts:128-133]](), [[packages/tools/src/openai/middleware.ts:162]]()

---

# Page: Function Calling Tools

# Function Calling Tools

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [apps/docs/ai-sdk/examples.mdx](apps/docs/ai-sdk/examples.mdx)
- [apps/docs/ai-sdk/infinite-chat.mdx](apps/docs/ai-sdk/infinite-chat.mdx)
- [apps/docs/ai-sdk/memory-tools.mdx](apps/docs/ai-sdk/memory-tools.mdx)
- [apps/docs/cookbook/ai-sdk-integration.mdx](apps/docs/cookbook/ai-sdk-integration.mdx)
- [apps/docs/cookbook/customer-support.mdx](apps/docs/cookbook/customer-support.mdx)
- [apps/docs/cookbook/document-qa.mdx](apps/docs/cookbook/document-qa.mdx)
- [apps/docs/cookbook/personal-assistant.mdx](apps/docs/cookbook/personal-assistant.mdx)
- [apps/docs/memory-api/sdks/openai-plugins.mdx](apps/docs/memory-api/sdks/openai-plugins.mdx)
- [apps/docs/memory-router/usage.mdx](apps/docs/memory-router/usage.mdx)
- [apps/docs/memory-router/with-memory-api.mdx](apps/docs/memory-router/with-memory-api.mdx)
- [biome.json](biome.json)
- [packages/ai-sdk/README.md](packages/ai-sdk/README.md)
- [packages/ai-sdk/src/tools.test.ts](packages/ai-sdk/src/tools.test.ts)
- [packages/ai-sdk/src/tools.ts](packages/ai-sdk/src/tools.ts)
- [packages/tools/src/ai-sdk.ts](packages/tools/src/ai-sdk.ts)
- [packages/tools/src/openai/tools.ts](packages/tools/src/openai/tools.ts)
- [packages/tools/src/tools-shared.ts](packages/tools/src/tools-shared.ts)
- [packages/tools/src/tools.test.ts](packages/tools/src/tools.test.ts)
- [packages/tools/src/types.ts](packages/tools/src/types.ts)
- [packages/tools/src/vercel/logger.ts](packages/tools/src/vercel/logger.ts)

</details>



This document covers the explicit function calling tools provided by `@supermemory/tools` for AI SDK, OpenAI SDK, and other agent frameworks. These tools give language models the ability to search, add, and manage memories through explicit tool invocations, providing granular control over when the model interacts with the Supermemory knowledge base.

Function calling tools are appropriate when you want the language model to explicitly decide when to search or save memories, rather than having memories automatically injected into every request via middleware.

---

## Tool Architecture

The `@supermemory/tools` package provides a suite of tools that wrap the Supermemory SDK. While `searchMemoriesTool` and `addMemoryTool` are the most common, the package also includes tools for profile retrieval and document management.

**Tool Architecture: Submodule Exports**

```mermaid
graph TB
    subgraph "Submodule_Exports"
        AISDK["@supermemory/tools/ai-sdk"]
        OpenAISDK["@supermemory/tools/openai"]
        Mastra["@supermemory/tools/mastra"]
    end

    subgraph "Logic_Layer_packages_tools_src"
        Shared["tools-shared.ts"]
        VercelTools["ai-sdk.ts"]
        OpenAITools["openai/tools.ts"]
    end

    subgraph "Code_Entities_SDK"
        SMClient["class Supermemory"]
        SearchAPI["client.search.execute()"]
        AddAPI["client.add()"]
        ProfileAPI["client.profile()"]
        DocList["client.documents.list()"]
    end

    AISDK --> VercelTools
    OpenAISDK --> OpenAITools
    VercelTools --> SMClient
    OpenAITools --> SMClient
    
    SMClient --> SearchAPI
    SMClient --> AddAPI
    SMClient --> ProfileAPI
    SMClient --> DocList
    
    VercelTools -.-> Shared
    OpenAITools -.-> Shared
```
Sources: [packages/tools/src/ai-sdk.ts:1-12](), [packages/tools/src/openai/tools.ts:1-8](), [packages/ai-sdk/src/tools.ts:1-34]()

---

## AI SDK Function Tools

The AI SDK tools use the `tool()` function from the `ai` package to create structured function definitions compatible with the Vercel AI SDK's tool calling system. [packages/tools/src/ai-sdk.ts:2](), [packages/ai-sdk/src/tools.ts:1]()

### searchMemoriesTool
Creates a tool that performs semantic search across user memories. It uses `client.search.execute()` with a default `chunkThreshold`. [packages/tools/src/ai-sdk.ts:13-79](), [packages/ai-sdk/src/tools.ts:40-90]()

**Input Schema (Zod/JSON Schema):**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `informationToGet` | `string` | required | Terms to search for in the user's memories. |
| `includeFullDocs` | `boolean` | `true` | Whether to include the full document content. |
| `limit` | `number` | `10` | Maximum number of results to return. |

### addMemoryTool
Creates a tool that stores new information by calling `client.add()`. [packages/tools/src/ai-sdk.ts:81-119](), [packages/ai-sdk/src/tools.ts:92-127]()

**Input Schema (Zod/JSON Schema):**
| Parameter | Type | Description |
|-----------|------|-------------|
| `memory` | `string` | The text content of the memory to add. |

### Additional AI SDK Tools
- `getProfileTool`: Retrieves user profile (static and dynamic) via `client.profile()`. [packages/tools/src/ai-sdk.ts:121-163]()
- `documentListTool`: Lists documents in a container using `client.documents.list()`. [packages/tools/src/ai-sdk.ts:165-221]()
- `documentDeleteTool`: Deletes a specific document by ID using `client.documents.delete()`. [packages/tools/src/ai-sdk.ts:223-253]()
- `documentAddTool`: Adds a new document (URL or text) to memory. [packages/tools/src/ai-sdk.ts:255-296]()
- `memoryForgetTool`: Marks a specific memory as forgotten. [packages/tools/src/ai-sdk.ts:298-335]()

Sources: [packages/tools/src/ai-sdk.ts:13-335](), [packages/ai-sdk/src/tools.ts:40-133](), [packages/tools/src/tools-shared.ts:6-21]()

---

## OpenAI SDK Function Tools

The OpenAI implementation provides tools compatible with OpenAI's native `FunctionDefinition` format. [packages/tools/src/openai/tools.ts:67-219]()

### Tool Definitions and Schemas
`memoryToolSchemas` contains raw OpenAI-format schemas for all memory operations, including `searchMemories`, `addMemory`, `getProfile`, `documentList`, and `memoryForget`. [packages/tools/src/openai/tools.ts:67-219]()

**Key OpenAI Utilities:**
| Function | Description |
|----------|-------------|
| `getToolDefinitions()` | Returns an array of `ChatCompletionTool` objects for OpenAI API. [packages/tools/src/openai/tools.ts:311-313]() |
| `createToolCallExecutor()` | Returns an async function that dispatches a `tool_call` to the correct Supermemory method. [packages/tools/src/openai/tools.ts:321-344]() |
| `supermemoryTools()` | Returns a map of individual tool functions for manual execution. [packages/tools/src/openai/tools.ts:302-309]() |

Sources: [packages/tools/src/openai/tools.ts:67-344](), [apps/docs/memory-api/sdks/openai-plugins.mdx:85-119]()

---

## Tool Configuration

Both SDKs utilize the `SupermemoryToolsConfig` to scope operations. [packages/tools/src/types.ts:5-24]()

```typescript
export interface SupermemoryToolsConfig {
	baseUrl?: string
	containerTags?: string[]
	projectId?: string
	strict?: boolean
}
```

### Container Tag Resolution
The tools resolve the target scope using `getContainerTags()`. If a `projectId` is provided, it is automatically transformed into a container tag with the prefix `sm_project_`. [packages/tools/src/tools-shared.ts:62-70]()

**Code Entity Mapping: Natural Language to Code**
```mermaid
graph LR
    NL["'Search my project memories'"] -- "config.projectId = '123'" --> Code["containerTags = ['sm_project_123']"]
    NL2["'Add to user scope'"] -- "config.containerTags = ['user_A']" --> Code2["containerTags = ['user_A']"]
    
    Code --> API["client.search.execute()"]
    Code2 --> API2["client.add()"]
```
Sources: [packages/tools/src/tools-shared.ts:54-70](), [packages/ai-sdk/src/tools.ts:36-39](), [packages/tools/src/ai-sdk.ts:22]()

---

## Execution and Data Flow

The following diagram illustrates the lifecycle of a tool call within the AI SDK environment.

**Tool Execution Sequence**

```mermaid
sequenceDiagram
    participant LLM as "Language Model"
    participant Tool as "searchMemoriesTool"
    participant Schema as "Zod/JSON Schema"
    participant SM as "Supermemory SDK"
    participant API as "Supermemory API"

    LLM->>Tool: "Call searchMemories(informationToGet: 'React hooks')"
    Tool->>Schema: "Validate input"
    Schema-->>Tool: "Valid"
    Tool->>SM: "client.search.execute({ q: 'React hooks', ... })"
    SM->>API: "POST /v3/search"
    API-->>SM: "JSON Results"
    SM-->>Tool: "Response Object"
    Tool-->>LLM: "{ success: true, results: [...] }"
```
Sources: [packages/tools/src/ai-sdk.ts:52-77](), [packages/ai-sdk/src/tools.ts:64-89](), [packages/tools/src/openai/tools.ts:244-274]()

---

## Usage Patterns

### AI SDK Integration
The `supermemoryTools` function returns an object containing all available tools for the AI SDK `tools` parameter. [packages/ai-sdk/src/tools.ts:27-133]()

```typescript
import { supermemoryTools } from "@supermemory/tools/ai-sdk"

const result = await generateText({
  model: openai("gpt-4o"),
  tools: {
    ...supermemoryTools(apiKey, { projectId: "my-project" })
  },
  prompt: "What did I say about the project architecture?"
})
```
Sources: [packages/ai-sdk/src/tools.ts:27-133](), [packages/tools/src/tools.test.ts:112-118]()

### OpenAI Integration
OpenAI integration requires handling tool calls returned by the model using the `createToolCallExecutor`. [packages/tools/src/openai/tools.ts:321-344]()

```typescript
import { getToolDefinitions, createToolCallExecutor } from "@supermemory/tools/openai"

const tools = getToolDefinitions()
const executor = createToolCallExecutor(apiKey, { projectId: "my-project" })

// After receiving tool_calls from OpenAI:
for (const toolCall of response.choices[0].message.tool_calls) {
  const result = await executor(toolCall)
  // Send result back to OpenAI as a tool message
}
```
Sources: [apps/docs/memory-api/sdks/openai-plugins.mdx:85-119](), [packages/tools/src/openai/tools.ts:321-344]()

---

# Page: Configuration & Usage Patterns

# Configuration & Usage Patterns

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [packages/tools/README.md](packages/tools/README.md)
- [packages/tools/package.json](packages/tools/package.json)
- [packages/tools/src/conversations-client.ts](packages/tools/src/conversations-client.ts)
- [packages/tools/src/index.ts](packages/tools/src/index.ts)
- [packages/tools/src/vercel/index.ts](packages/tools/src/vercel/index.ts)
- [packages/tools/src/vercel/memory-prompt.ts](packages/tools/src/vercel/memory-prompt.ts)
- [packages/tools/src/vercel/middleware.ts](packages/tools/src/vercel/middleware.ts)
- [packages/tools/src/vercel/util.ts](packages/tools/src/vercel/util.ts)
- [packages/tools/src/voltagent/hooks.ts](packages/tools/src/voltagent/hooks.ts)
- [packages/tools/src/voltagent/index.ts](packages/tools/src/voltagent/index.ts)
- [packages/tools/src/voltagent/middleware.ts](packages/tools/src/voltagent/middleware.ts)
- [packages/tools/src/voltagent/types.ts](packages/tools/src/voltagent/types.ts)
- [packages/tools/test/ai-sdk-test.ts](packages/tools/test/ai-sdk-test.ts)
- [packages/tools/test/chatapp/app/api/chat/route.ts](packages/tools/test/chatapp/app/api/chat/route.ts)
- [packages/tools/test/chatapp/app/api/stream/route.ts](packages/tools/test/chatapp/app/api/stream/route.ts)
- [packages/tools/test/chatapp/app/stream/page.tsx](packages/tools/test/chatapp/app/stream/page.tsx)
- [packages/tools/test/chatapp/bun.lock](packages/tools/test/chatapp/bun.lock)
- [packages/tools/test/with-supermemory/integration.test.ts](packages/tools/test/with-supermemory/integration.test.ts)
- [packages/tools/test/with-supermemory/unit.test.ts](packages/tools/test/with-supermemory/unit.test.ts)
- [packages/tools/tsdown.config.ts](packages/tools/tsdown.config.ts)

</details>



This page documents the configuration interfaces, memory mode semantics, conversation client behavior, and concrete usage patterns for the `@supermemory/tools` package. It covers the options accepted by `withSupermemory` across supported frameworks (Vercel AI SDK, OpenAI SDK, and Mastra), the `MemoryMode` type, and the internal mechanisms for memory persistence and caching.

---

## Configuration Interfaces

### `WithSupermemoryOptions` (Vercel AI SDK)

The configuration for the Vercel AI SDK middleware is defined as `SupermemoryMiddlewareOptions` in [packages/tools/src/vercel/middleware.ts:118-146]() and utilized by the `withSupermemory` wrapper (aliased from `WrapVercelLanguageModelOptions` in [packages/tools/src/vercel/index.ts:17-63]()).

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `containerTag` | `string` | — | **Required.** Scopes memories to a specific user or project ID [packages/tools/src/vercel/index.ts:19-19](). |
| `customId` | `string` | — | **Required.** Groups messages into a single document for contextual memory generation [packages/tools/src/vercel/index.ts:21-21](). |
| `verbose` | `boolean` | `false` | Enables detailed logging of memory search and injection steps [packages/tools/src/vercel/index.ts:23-23](). |
| `mode` | `"profile" \| "query" \| "full"` | `"profile"` | Controls the memory retrieval strategy (see [MemoryMode](#memorymode) below) [packages/tools/src/vercel/index.ts:30-30](). |
| `addMemory` | `"always" \| "never"` | `"always"` | When `"always"`, automatically saves conversation turns to Supermemory after each LLM response [packages/tools/src/vercel/index.ts:36-36](). |
| `apiKey` | `string` | `process.env.SUPERMEMORY_API_KEY` | Explicit API key. Required if the environment variable is not set [packages/tools/src/vercel/index.ts:115-121](). |
| `baseUrl` | `string` | `"https://api.supermemory.ai"` | Custom API endpoint. Normalized by `normalizeBaseUrl` [packages/tools/src/vercel/middleware.ts:182-182](). |
| `promptTemplate` | `PromptTemplate` | Default markdown | Custom function to format memory data into the system prompt [packages/tools/src/vercel/index.ts:56-56](). |
| `skipMemoryOnError`| `boolean` | `true` | If `true`, logs errors and continues without memories. If `false`, propagates the error [packages/tools/src/vercel/index.ts:62-62](). |

**Sources:** [packages/tools/src/vercel/index.ts:17-63](), [packages/tools/src/vercel/middleware.ts:118-146]()

---

## MemoryMode

The `MemoryMode` type determines which Supermemory API capabilities are utilized and how the system prompt is augmented.

**Decision diagram: MemoryMode → Code Entity Interaction**

```mermaid
flowchart TD
    A["mode parameter"] --> B{"value?"}
    B -- "profile" --> C["extractQueryText returns ''"]
    B -- "query" --> D["extractQueryText returns last user message"]
    B -- "full" --> E["extractQueryText returns last user message"]

    C --> F["buildMemoriesText calls /v4/profile\n(no q param)"]
    D --> G["buildMemoriesText calls /v4/profile\n(with q param)"]
    E --> H["buildMemoriesText calls /v4/profile\n(with q param)"]

    F --> I["Injected Prompt: Static + Dynamic Profile"]
    G --> J["Injected Prompt: Search Results Only"]
    H --> K["Injected Prompt: Profile + Search Results"]
    
    subgraph "Code Entities"
    D["extractQueryText()"]
    C["extractQueryText()"]
    E["extractQueryText()"]
    F["buildMemoriesText()"]
    G["buildMemoriesText()"]
    H["buildMemoriesText()"]
    end
```

| Mode | Behavior | Implementation Detail |
|------|----------|-----------------------|
| `"profile"` | Retrieves user profile (static + dynamic) without query filtering [packages/tools/src/vercel/middleware.ts:129-130](). | `extractQueryText` returns an empty string [packages/tools/src/vercel/memory-prompt.ts:27-29](). |
| `"query"` | Searches memories based on semantic similarity to the user's message [packages/tools/src/vercel/middleware.ts:131-131](). | `extractQueryText` parses `params.prompt` for the last user message [packages/tools/src/vercel/memory-prompt.ts:31-48](). |
| `"full"` | Combines both profile and query-based results [packages/tools/src/vercel/middleware.ts:132-132](). | Fetches both profile and search data from the API [packages/tools/src/vercel/middleware.ts:132-132](). |

**Sources:** [packages/tools/src/vercel/middleware.ts:128-133](), [packages/tools/src/vercel/memory-prompt.ts:23-48]()

---

## Conversations Client

When `addMemory` is set to `"always"`, the middleware captures the assistant's response and saves the turn using the `addConversation` client [packages/tools/src/vercel/middleware.ts:94-100]().

### Save Flow: `saveMemoryAfterResponse`
The function `saveMemoryAfterResponse` in [packages/tools/src/vercel/middleware.ts:78-113]() orchestrates the persistence:
1. **Conversion**: `convertToConversationMessages` transforms Vercel AI SDK `LanguageModelCallOptions` and the assistant's text into `ConversationMessage[]` [packages/tools/src/vercel/middleware.ts:18-76]().
2. **API Call**: Calls `addConversation` with the `customId` (mapped to `conversationId`), the message array, and the `containerTag` [packages/tools/src/vercel/middleware.ts:94-100]().

```mermaid
flowchart LR
    A["LanguageModel.doGenerate()"] --> B["extractAssistantResponseText()"]
    B --> C["saveMemoryAfterResponse()"]
    C --> D["convertToConversationMessages()"]
    D --> E["addConversation()"]
    E --> F["POST /v4/conversations"]
    
    subgraph "packages/tools/src/vercel/middleware.ts"
    C["saveMemoryAfterResponse"]
    D["convertToConversationMessages"]
    end
    subgraph "packages/tools/src/conversations-client.ts"
    E["addConversation"]
    end
```

**Sources:** [packages/tools/src/vercel/middleware.ts:18-113](), [packages/tools/src/vercel/index.ts:179-195]()

---

## Per-Turn Memory Caching

To prevent redundant API calls during multi-step tool-call sequences (where the AI SDK calls the model multiple times for a single user turn), the middleware implements a `MemoryCache` [packages/tools/src/vercel/middleware.ts:163-163]().

**Cache Logic**:
- **Key Generation**: `makeTurnKey` uses the `containerTag`, `customId`, `mode`, and the user's message text [packages/tools/src/vercel/middleware.ts:212-222]().
- **Hit Detection**: If `isNewUserTurn` is false (meaning the last message is from the assistant or a tool), the middleware retrieves memories from the cache [packages/tools/src/vercel/middleware.ts:250-255]().
- **Fresh Fetch**: A new fetch to the Supermemory API only occurs when a new user message is detected [packages/tools/src/vercel/middleware.ts:257-263]().

**Sources:** [packages/tools/src/vercel/middleware.ts:204-263](), [packages/tools/test/with-supermemory/unit.test.ts:140-246]()

---

## Framework Usage Patterns

### Vercel AI SDK (`@supermemory/tools/ai-sdk`)
The `withSupermemory` wrapper uses a `Proxy` to intercept `doGenerate` and `doStream` calls [packages/tools/src/vercel/index.ts:144-147]().

```typescript
import { withSupermemory } from "@supermemory/tools/ai-sdk"
import { openai } from "@ai-sdk/openai"

const model = withSupermemory(openai("gpt-4"), {
  containerTag: "user-123",
  customId: "session-789",
  mode: "full",
  addMemory: "always"
})
```
**Sources:** [packages/tools/src/vercel/index.ts:111-147](), [packages/tools/README.md:69-80]()

### Function Calling Tools
The package provides `searchMemoriesTool` and `addMemoryTool` which can be used directly with `generateText` or `streamText` [packages/tools/README.md:23-56]().

```typescript
import { supermemoryTools } from "@supermemory/tools/ai-sdk"
import { generateText } from "ai"

const result = await generateText({
  model: openai("gpt-4"),
  tools: supermemoryTools(process.env.SUPERMEMORY_API_KEY!, {
    containerTags: ["user-123"]
  }),
  prompt: "What are my preferences?"
})
```
**Sources:** [packages/tools/README.md:23-56]()

### OpenAI SDK (`@supermemory/tools/openai`)
A similar wrapper exists for the native OpenAI client, enabling memory injection and tool usage patterns for non-Vercel SDK users [packages/tools/README.md:15-18]().

---

## Environment Variables

| Variable | Used by | Description |
|----------|---------|-------------|
| `SUPERMEMORY_API_KEY` | Middleware & Tools | Default authentication key if `apiKey` is not provided in options [packages/tools/src/vercel/index.ts:115-121](). |
| `SUPERMEMORY_BASE_URL` | Middleware & Tools | Default API endpoint (defaults to `https://api.supermemory.ai`) [packages/tools/src/vercel/index.ts:136-136](). |

**Sources:** [packages/tools/src/vercel/index.ts:115-136](), [packages/tools/test/chatapp/app/api/stream/route.ts:13-16]()

---

# Page: Mastra & Claude Memory Integration

# Mastra & Claude Memory Integration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [apps/docs/integrations/mastra.mdx](apps/docs/integrations/mastra.mdx)
- [apps/docs/memory-api/sdks/anthropic-claude-memory.mdx](apps/docs/memory-api/sdks/anthropic-claude-memory.mdx)
- [packages/tools/src/claude-memory-simple-example.ts](packages/tools/src/claude-memory-simple-example.ts)
- [packages/tools/src/claude-memory.test.ts](packages/tools/src/claude-memory.test.ts)
- [packages/tools/src/claude-memory.ts](packages/tools/src/claude-memory.ts)
- [packages/tools/src/mastra/processor.ts](packages/tools/src/mastra/processor.ts)
- [packages/tools/src/mastra/types.ts](packages/tools/src/mastra/types.ts)
- [packages/tools/src/mastra/wrapper.ts](packages/tools/src/mastra/wrapper.ts)
- [packages/tools/test/anthropic-example.ts](packages/tools/test/anthropic-example.ts)
- [packages/tools/test/claude-memory-examples.ts](packages/tools/test/claude-memory-examples.ts)
- [packages/tools/test/claude-memory-real-example.ts](packages/tools/test/claude-memory-real-example.ts)
- [packages/tools/test/claude-memory.test.ts](packages/tools/test/claude-memory.test.ts)
- [packages/tools/test/mastra/integration.test.ts](packages/tools/test/mastra/integration.test.ts)
- [packages/tools/test/mastra/unit.test.ts](packages/tools/test/mastra/unit.test.ts)

</details>



This page documents the specialized integrations for the Mastra agent framework and the native Claude memory tool within the `@supermemory/tools` package. These integrations provide deep, framework-specific hooks for memory retrieval and persistence, differing from the generic middleware approach used for the Vercel AI SDK.

## Mastra Agent Integration

The Mastra integration leverages Mastra's native `Processor` architecture to intercept agent inputs and outputs. This allows for seamless memory injection and automatic conversation saving without manual tool calls.

### Core Components

The integration is primarily defined within the `packages/tools/src/mastra/` directory.

1.  **`withSupermemory`**: A high-order function that wraps a Mastra `AgentConfig`. It automatically attaches both input and output processors to the agent configuration [packages/tools/src/mastra/wrapper.ts:69-111]().
2.  **`SupermemoryInputProcessor`**: An `InputProcessor` that fetches relevant memories from Supermemory before LLM calls. It utilizes `buildMemoriesText` to retrieve context based on the chosen `MemoryMode` (`profile`, `query`, or `full`) and injects them into the system prompt [packages/tools/src/mastra/processor.ts:128-202]().
3.  **`SupermemoryOutputProcessor`**: An `OutputProcessor` that runs after the LLM responds. If `addMemory` is set to `"always"`, it saves the resulting conversation back to Supermemory using the `addConversation` client [packages/tools/src/mastra/processor.ts:231-285]().
4.  **`createSupermemoryProcessors`**: A utility function to create both processors simultaneously for manual configuration [packages/tools/src/mastra/index.ts:1-20]().

### Data Flow in Mastra

The following diagram illustrates how Supermemory interacts with the Mastra agent lifecycle via the processor pipeline.

**Mastra Agent Memory Lifecycle**
```mermaid
sequenceDiagram
    participant U as "User"
    participant A as "Agent (@mastra/core)"
    participant IP as "SupermemoryInputProcessor"
    participant LLM as "Language Model"
    participant OP as "SupermemoryOutputProcessor"
    participant SM as "Supermemory API (/v4/profile)"

    U->>A: "agent.generate(prompt)"
    A->>IP: "processInput(args)"
    IP->>SM: "buildMemoriesText(containerTag, queryText)"
    SM-->>IP: "Return formatted memories"
    IP->>A: "messageList.addSystem(memories, 'supermemory')"
    A->>LLM: "Generate response with enhanced prompt"
    LLM-->>A: "Return Assistant Response"
    A->>OP: "processOutputResult(args)"
    OP->>SM: "addConversation(messages) [if enabled]"
    A-->>U: "Final Response"
```
Sources: [apps/docs/integrations/mastra.mdx:75-94](), [packages/tools/src/mastra/processor.ts:138-194](), [packages/tools/src/mastra/processor.ts:241-260]()

### Configuration Options

The Mastra integration uses `SupermemoryMastraOptions` [packages/tools/src/mastra/types.ts:37-54]():

| Option | Type | Description |
| :--- | :--- | :--- |
| `containerTag` | `string` | **Required**. Scopes memories to a specific user or project [packages/tools/src/mastra/types.ts:39-39](). |
| `customId` | `string` | **Required**. Groups messages into a single document for contextual memory [packages/tools/src/mastra/types.ts:41-41](). |
| `mode` | `"profile" \| "query" \| "full"` | Memory retrieval mode (default: `"profile"`) [packages/tools/src/mastra/types.ts:47-47](). |
| `addMemory` | `"always" \| "never"` | Controls auto-saving of conversations (default: `"always"`) [packages/tools/src/mastra/types.ts:49-49](). |
| `promptTemplate` | `PromptTemplate` | Custom function to format memory data into the system prompt [packages/tools/src/mastra/types.ts:53-53](). |

Sources: [packages/tools/src/mastra/types.ts:37-54](), [apps/docs/integrations/mastra.mdx:98-110]()

---

## Claude Native Memory Tool

The Claude Native Memory integration uses the Anthropic `memory_20250818` tool type. This allows Claude to manage its own long-term memory via file-like operations, acting as a "thinking" memory rather than just static context injection.

### Key Components

*   **`ClaudeMemoryTool`**: A class that maps Claude's filesystem-style commands (`view`, `create`, `str_replace`, `insert`, `delete`, `rename`) to Supermemory document operations [packages/tools/src/claude-memory.ts:44-145]().
*   **`createClaudeMemoryTool`**: Factory function to initialize the tool with specific configuration like `memoryContainerTag` [packages/tools/src/claude-memory.ts:1084-1093]().
*   **Path Normalization**: The tool converts virtual paths (e.g., `/memories/notes.txt`) into Supermemory `customId` strings (e.g., `memories_notes_txt`) for persistent storage [packages/tools/src/claude-memory.ts:53-58]().

### Integration Logic

The Claude integration uses a tool-calling loop:

1.  **Tool Definition**: The model is provided with a tool named `memory` of type `memory_20250818` [packages/tools/test/claude-memory-real-example.ts:94-99]().
2.  **Explicit Command Execution**: When Claude emits a `tool_use` block, the `handleCommand` method executes the specific operation [packages/tools/src/claude-memory.ts:77-138]().
3.  **Line-Range Support**: The `view` command supports `view_range` parameters. An end range of `-1` is handled as "read to end of file" [packages/tools/src/claude-memory.test.ts:41-57]().
4.  **Formatting**: Responses to Claude are formatted as `MemoryToolResult` objects containing `tool_use_id`, `content`, and `is_error` status [packages/tools/src/claude-memory.ts:150-164]().

---

## Comparison of Integration Strategies

| Feature | Vercel AI SDK (`withSupermemory`) | Mastra (`withSupermemory`) | Claude Tool (`ClaudeMemoryTool`) |
| :--- | :--- | :--- | :--- |
| **Mechanism** | Higher-order Model / Proxy | Input/Output Processors | Native Tool Calling (Filesystem) |
| **Control** | Automatic injection | Automatic injection | Model-driven (decides when to read/write) |
| **Persistence** | Auto-saves turns | `SupermemoryOutputProcessor` | Manual `create`/`str_replace` by model |
| **Primary File** | `src/ai-sdk.ts` | `src/mastra/wrapper.ts` | `src/claude-memory.ts` |

### Architecture: Code Entity Space to Natural Language Space

This diagram shows how specific code entities in the `packages/tools` package map to the user's conceptual experience of "Memory".

**Memory Integration Architecture**
```mermaid
graph TD
    subgraph "Natural Language Space (User Intent)"
        UI1["'Remember my coding preferences'"]
        UI2["'Search my technical notes'"]
        UI3["'Update my project deadline'"]
    end

    subgraph "Code Entity Space (@supermemory/tools)"
        MastraWrap["withSupermemory (Mastra)"]
        ClaudeTool["ClaudeMemoryTool.handleCommand"]
        
        InputProc["SupermemoryInputProcessor"]
        OutputProc["SupermemoryOutputProcessor"]
        
        SharedShared["buildMemoriesText"]
        ConvClient["addConversation"]
    end

    subgraph "Infrastructure (Backend)"
        API_V4["POST /v4/profile"]
        API_V3_ADD["POST /v3/add"]
        API_V3_SEARCH["POST /v3/search"]
    end

    UI1 --> MastraWrap
    MastraWrap --> InputProc
    InputProc --> SharedShared
    SharedShared --> API_V4
    
    UI2 --> ClaudeTool
    ClaudeTool --> API_V3_SEARCH
    
    UI3 --> ClaudeTool
    ClaudeTool --> API_V3_ADD
    
    MastraWrap --> OutputProc
    OutputProc --> ConvClient
    ConvClient --> API_V3_ADD
```
Sources: [packages/tools/src/mastra/processor.ts:176-184](), [packages/tools/src/claude-memory.ts:87-138](), [packages/tools/src/mastra/wrapper.ts:88-109]()

### Implementation Detail: Path-to-Memory Mapping

Claude interacts with memory as if it were a filesystem. The `ClaudeMemoryTool` translates these intents into Supermemory API calls:

| Claude Intent | MemoryCommand | Supermemory Action |
| :--- | :--- | :--- |
| List files | `view` (path: `/memories/`) | `client.search.execute` with `q: "*"` and prefix filtering [packages/tools/src/claude-memory.ts:187-195]() |
| Read file | `view` (path: `/file.txt`) | `client.search.execute` for specific `documentId` [packages/tools/src/claude-memory.ts:253-260]() |
| Save fact | `create` | `client.add` with normalized `customId` [packages/tools/src/claude-memory.ts:90-97]() |
| Update fact | `str_replace` | Fetch content, replace string, then `client.add` [packages/tools/src/claude-memory.ts:98-109]() |

Sources: [packages/tools/src/claude-memory.ts:87-138](), [packages/tools/src/claude-memory.test.ts:24-30]()

---

# Page: VoltAgent Integration

# VoltAgent Integration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [apps/docs/ai-sdk/overview.mdx](apps/docs/ai-sdk/overview.mdx)
- [apps/docs/ai-sdk/user-profiles.mdx](apps/docs/ai-sdk/user-profiles.mdx)
- [apps/docs/integrations/ai-sdk.mdx](apps/docs/integrations/ai-sdk.mdx)
- [apps/docs/integrations/openai.mdx](apps/docs/integrations/openai.mdx)
- [apps/docs/integrations/voltagent.mdx](apps/docs/integrations/voltagent.mdx)
- [apps/docs/migration/tools-v2-upgrade.mdx](apps/docs/migration/tools-v2-upgrade.mdx)
- [packages/tools/src/conversations-client.ts](packages/tools/src/conversations-client.ts)
- [packages/tools/src/index.ts](packages/tools/src/index.ts)
- [packages/tools/src/shared/memory-client.ts](packages/tools/src/shared/memory-client.ts)
- [packages/tools/src/shared/types.ts](packages/tools/src/shared/types.ts)
- [packages/tools/src/voltagent/hooks.ts](packages/tools/src/voltagent/hooks.ts)
- [packages/tools/src/voltagent/index.ts](packages/tools/src/voltagent/index.ts)
- [packages/tools/src/voltagent/middleware.ts](packages/tools/src/voltagent/middleware.ts)
- [packages/tools/src/voltagent/types.ts](packages/tools/src/voltagent/types.ts)
- [packages/tools/tsdown.config.ts](packages/tools/tsdown.config.ts)

</details>



Supermemory integrates with [VoltAgent](https://github.com/VoltAgent/voltagent) to provide long-term memory capabilities through a middleware-like hook system. This integration allows agents to automatically retrieve relevant user history and persist new conversation turns as memories.

## Overview

The VoltAgent integration is centered around the `withSupermemory` wrapper, which enhances a standard VoltAgent `AgentConfig` by injecting memory retrieval and storage logic into the agent's lifecycle hooks: `onPrepareMessages` and `onEnd` [packages/tools/src/voltagent/types.ts:165-172]().

### Key Differences from Vercel AI SDK
Unlike the Vercel AI SDK integration which uses a middleware pattern to intercept low-level provider calls [apps/docs/ai-sdk/user-profiles.mdx:39-44](), the VoltAgent integration operates at the **Agent level** using hooks [packages/tools/src/voltagent/types.ts:4-5](). 

*   **Vercel AI SDK**: Intercepts `generateText`/`streamText` at the model provider level [apps/docs/ai-sdk/user-profiles.mdx:22-26]().
*   **VoltAgent**: Intercepts the agent's message preparation phase (`onPrepareMessages`) and completion phase (`onEnd`) [apps/docs/integrations/voltagent.mdx:79-90]().

## Implementation & Data Flow

The integration follows a two-step process: context initialization and hook execution.

### 1. Context Initialization
The `createSupermemoryContext` function validates required parameters like `containerTag` and `customId`, initializes the `Supermemory` client, and sets up a `MemoryCache` to prevent redundant API calls during multi-turn interactions [packages/tools/src/voltagent/middleware.ts:67-134](). It also normalizes the `baseUrl` and prepares the logger [packages/tools/src/voltagent/middleware.ts:103-111]().

### 2. Lifecycle Hooks
The integration implements two primary hooks via `createSupermemoryProcessors` [packages/tools/src/voltagent/middleware.ts:316-353]():
*   **`onPrepareMessages`**: Triggered before the LLM call. It extracts the last user message using `getLastUserMessage`, searches Supermemory for relevant context (static/dynamic profiles or semantic search) via `enhanceMessagesWithMemories`, and injects the results into the system prompt [packages/tools/src/voltagent/middleware.ts:196-229]().
*   **`onEnd`**: Triggered after a successful agent response. If `addMemory` is set to `"always"` (the default for VoltAgent [packages/tools/src/voltagent/middleware.ts:81]()), it sends the updated conversation thread to the `/v4/conversations` endpoint using the `addConversation` client [packages/tools/src/voltagent/middleware.ts:316-353]().

### Data Flow Diagram

The following diagram illustrates how the `withSupermemory` wrapper orchestrates data between the VoltAgent lifecycle and the Supermemory API.

**VoltAgent Integration Data Flow**
```mermaid
sequenceDiagram
    participant App as "VoltAgent Application"
    participant Hook as "withSupermemory Hooks"
    participant API as "Supermemory API (/v4)"
    participant LLM as "LLM Provider"

    App->>Hook: agent.generateText()
    Hook->>Hook: onPrepareMessages()
    Note over Hook, API: Calls supermemoryProfileSearch
    Hook->>API: POST /v4/profile (queryText)
    API-->>Hook: ProfileStructure (static, dynamic, search)
    Hook->>Hook: buildMemoriesText()
    Hook->>LLM: Call with Enhanced System Prompt
    LLM-->>Hook: Assistant Response
    Hook->>Hook: onEnd()
    Note over Hook, API: Calls addConversation
    Hook->>API: POST /v4/conversations (customId)
    Hook-->>App: Final Result
```
Sources: [packages/tools/src/voltagent/middleware.ts:196-353](), [packages/tools/src/shared/memory-client.ts:24-65](), [packages/tools/src/conversations-client.ts:73-102]()

## Key Functions and Classes

### `withSupermemory`
The primary entry point. It takes a `SupermemoryVoltAgent` configuration and returns a modified `VoltAgentConfig` with pre-configured hooks [apps/docs/integrations/voltagent.mdx:34-50]().

### `createSupermemoryProcessors`
Internal utility used to generate the `onPrepareMessages` and `onEnd` logic. It leverages `enhanceMessagesWithMemories` for retrieval and `addConversation` for storage [packages/tools/src/voltagent/middleware.ts:316-353]().

### Configuration Interface: `SupermemoryVoltAgent`
This interface extends base options with VoltAgent-specific search and storage parameters.

| Parameter | Type | Role |
| :--- | :--- | :--- |
| `containerTag` | `string` | **Required**. Scopes memories to a specific user or workspace [packages/tools/src/voltagent/types.ts:20-25](). |
| `customId` | `string` | **Required**. Groups messages into a single document/thread [packages/tools/src/voltagent/types.ts:25](). |
| `mode` | `MemoryMode` | Retrieval strategy: `profile`, `query`, or `full` [packages/tools/src/voltagent/types.ts:98-111](). |
| `searchMode` | `string` | Filters results by `memories`, `documents`, or `hybrid` [packages/tools/src/voltagent/types.ts:81-88](). |
| `addMemory` | `AddMemoryMode` | Defaults to `"always"` to persist conversations [packages/tools/src/voltagent/middleware.ts:81](). |
| `entityContext`| `string` | Guides memory extraction during conversation saving [packages/tools/src/voltagent/types.ts:90-96](). |

Sources: [packages/tools/src/voltagent/types.ts:20-97](), [packages/tools/src/voltagent/middleware.ts:78-92]()

## Code Entity Space Mapping

The following diagrams bridge the conceptual middleware components to the specific code entities in the `@supermemory/tools` package.

**Memory Retrieval Entity Map**
```mermaid
graph TD
    subgraph "Natural Language Space"
        UserQuery["'What is my favorite language?'"]
        Context["User Profile & Past Chats"]
    end

    subgraph "Code Entity Space"
        direction TB
        Hook["onPrepareMessages (hooks.ts)"]
        Extract["extractQueryText (shared/memory-client.ts)"]
        Search["supermemoryProfileSearch (shared/memory-client.ts)"]
        Format["buildMemoriesText (shared/memory-client.ts)"]
        Config["SupermemoryVoltAgent (types.ts)"]
        Cache["MemoryCache (shared/index.ts)"]
    end

    UserQuery --> Extract
    Extract --> Hook
    Hook --> Config
    Hook --> Search
    Hook --> Cache
    Search --> Format
    Format --> Context
```
Sources: [packages/tools/src/voltagent/hooks.ts](), [packages/tools/src/voltagent/types.ts:20-97](), [packages/tools/src/shared/memory-client.ts:88-175](), [packages/tools/src/shared/memory-client.ts:197-241]()

**Conversation Storage Entity Map**
```mermaid
graph LR
    subgraph "Natural Language Space"
        Turn["User/Assistant Interaction"]
        Thread["Persistent Chat History"]
    end

    subgraph "Code Entity Space"
        direction TB
        EndHook["onEnd (hooks.ts)"]
        ConvClient["addConversation (conversations-client.ts)"]
        API_Endpoint["/v4/conversations"]
    end

    Turn --> EndHook
    EndHook --> ConvClient
    ConvClient --> API_Endpoint
    API_Endpoint --> Thread
```
Sources: [packages/tools/src/voltagent/hooks.ts](), [packages/tools/src/conversations-client.ts:73-102](), [packages/tools/src/voltagent/middleware.ts:316-353]()

## Advanced Search Configuration

VoltAgent integration supports advanced search parameters that are passed directly to the Supermemory API via `supermemoryProfileSearch` [packages/tools/src/shared/memory-client.ts:24-30](). Note that these are only effective when `mode` is set to `"query"` or `"full"`; they are ignored in `"profile"` mode [packages/tools/src/voltagent/middleware.ts:249-254]().

*   **`threshold`**: Controls similarity sensitivity (0.0 to 1.0). Default is 0.1 [packages/tools/src/voltagent/types.ts:34]().
*   **`rerank`**: If `true`, uses a reranking model to improve relevance [packages/tools/src/voltagent/types.ts:49]().
*   **`rewriteQuery`**: Uses AI to expand the user query for better semantic matching [packages/tools/src/voltagent/types.ts:57]().
*   **`filters`**: Supports complex boolean logic (`AND`/`OR`) on memory metadata [packages/tools/src/voltagent/types.ts:65]().
*   **`include`**: Control inclusion of `chunks`, `documents`, `summaries`, or `relatedMemories` [packages/tools/src/voltagent/types.ts:107-134]().

Sources: [packages/tools/src/voltagent/types.ts:27-72](), [packages/tools/src/voltagent/middleware.ts:238-254](), [packages/tools/src/shared/memory-client.ts:24-65]()

---

# Page: MCP Server

# MCP Server

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CLAUDE.md](CLAUDE.md)
- [apps/mcp/.dev.vars.example](apps/mcp/.dev.vars.example)
- [apps/mcp/.gitignore](apps/mcp/.gitignore)
- [apps/mcp/mcp-app.html](apps/mcp/mcp-app.html)
- [apps/mcp/src/auth.ts](apps/mcp/src/auth.ts)
- [apps/mcp/src/client.ts](apps/mcp/src/client.ts)
- [apps/mcp/src/format.ts](apps/mcp/src/format.ts)
- [apps/mcp/src/html.d.ts](apps/mcp/src/html.d.ts)
- [apps/mcp/src/index.ts](apps/mcp/src/index.ts)
- [apps/mcp/src/posthog.ts](apps/mcp/src/posthog.ts)
- [apps/mcp/src/server.ts](apps/mcp/src/server.ts)
- [apps/mcp/src/ui/global.css](apps/mcp/src/ui/global.css)
- [apps/mcp/src/ui/mcp-app.css](apps/mcp/src/ui/mcp-app.css)
- [apps/mcp/src/ui/mcp-app.ts](apps/mcp/src/ui/mcp-app.ts)
- [apps/mcp/tsconfig.json](apps/mcp/tsconfig.json)
- [apps/mcp/vite.config.ts](apps/mcp/vite.config.ts)
- [apps/mcp/wrangler.jsonc](apps/mcp/wrangler.jsonc)
- [apps/web/components/chat/chat-graph-context-rail.tsx](apps/web/components/chat/chat-graph-context-rail.tsx)
- [apps/web/lib/chat-auto-space.ts](apps/web/lib/chat-auto-space.ts)

</details>



This page covers the `apps/mcp` Cloudflare Worker that implements a [Model Context Protocol (MCP)](https://modelcontextprotocol.io) server, giving AI assistants persistent memory via the Supermemory API. It describes the server's architecture, registered tools and resources, authentication model, and session mechanics.

For how end users connect their AI clients to the MCP server, see [Setup & Installation](#5.1). For the individual MCP tools, resources, and prompts in detail, see [Tools, Resources & Prompts](#5.2). For the authentication and session model, see [Authentication & Session Management](#5.3). For how the web application exposes the MCP connection wizard, see [Integrations & Connections](#2.5).

---

## Role in the System

The MCP server is the bridge between MCP-compatible AI clients (Cursor, Claude Desktop, VS Code, Windsurf, etc.) and the Supermemory memory API. AI clients call it during conversations to save and recall user memories without the client application needing to implement memory logic directly. It is built as a Cloudflare Worker using Durable Objects to maintain session state.

**System placement diagram:**

```mermaid
graph TD
  subgraph "External_AI_Clients"
    ["AI_Client"]
  end

  subgraph "apps/mcp_(Cloudflare_Worker)"
    ["index.ts"]
    ["SupermemoryMCP"]
    ["DurableObject_Storage"]
    ["SupermemoryClient"]
  end

  subgraph "Backend"
    ["Supermemory_REST_API"]
  end

  ["AI_Client"] -->|"MCP protocol"| ["index.ts"]
  ["index.ts"] -->|"mounts"| ["SupermemoryMCP"]
  ["SupermemoryMCP"] -->|"session storage"| ["DurableObject_Storage"]
  ["SupermemoryMCP"] -->|"instantiates"| ["SupermemoryClient"]
  ["SupermemoryClient"] -->|"SDK calls"| ["Supermemory_REST_API"]
```

Sources: [apps/mcp/src/server.ts:32-40](), [apps/mcp/src/index.ts:119-191](), [apps/mcp/wrangler.jsonc:23-30]()

---

## Architecture

The server utilizes the `@modelcontextprotocol/sdk` and a custom `McpAgent` base class from the `agents/mcp` package to handle the protocol lifecycle. It uses a `SupermemoryClient` wrapper around the core `supermemory` SDK to interface with the backend.

**Class and dependency diagram:**

```mermaid
classDiagram
  class SupermemoryMCP {
    +server McpServer
    -clientInfo clientInfo
    -cachedContainerTags cachedContainerTags
    +init() Promise
    -getClient() SupermemoryClient
    -handleMemory() Promise
    -handleRecall() Promise
  }
  class McpAgent {
    +ctx ctx
    +env env
    +props props
  }
  class McpServer {
    +registerTool()
    +registerResource()
  }
  class SupermemoryClient {
    -client Supermemory
    +createMemory()
    +forgetMemory()
    +search()
    +getProfile()
  }

  SupermemoryMCP --|> McpAgent
  SupermemoryMCP --> McpServer : "server"
  SupermemoryMCP --> SupermemoryClient : "creates via getClient()"
```

Sources: [apps/mcp/src/server.ts:32-40](), [apps/mcp/src/client.ts:129-147](), [apps/mcp/src/server.ts:1-2]()

### Key Types

| Type | Location | Purpose |
|---|---|---|
| `Env` | `apps/mcp/src/server.ts:14-18` | Cloudflare Worker bindings: `MCP_SERVER`, `API_URL`, `POSTHOG_API_KEY` |
| `Props` | `apps/mcp/src/server.ts:20-26` | Per-session user data injected by auth: `userId`, `apiKey`, `containerTag`, `email`, `name` |
| `SupermemoryMCP` | `apps/mcp/src/server.ts:32` | Main Durable Object class; handles tool/resource registration and execution |

Sources: [apps/mcp/src/server.ts:14-32]()

---

## Initialization Flow

The `init()` method on `SupermemoryMCP` runs once per DurableObject session. It restores client info from durable storage, initializes analytics via PostHog, and registers all tools and resources.

**Initialization sequence:**

```mermaid
sequenceDiagram
  participant DO as "DurableObject_Storage"
  participant MCP as "SupermemoryMCP.init()"
  participant SDK as "McpServer"

  MCP->>DO: "get('clientInfo')"
  DO-->>MCP: "stored clientInfo"
  MCP->>MCP: "refreshContainerTags()"
  MCP->>SDK: "registerTool('memory')"
  MCP->>SDK: "registerTool('recall')"
  MCP->>SDK: "registerTool('listProjects')"
  MCP->>SDK: "registerTool('whoAmI')"
  MCP->>SDK: "registerResource('User Profile')"
  MCP->>SDK: "registerResource('My Projects')"
```

Sources: [apps/mcp/src/server.ts:42-131](), [apps/mcp/src/server.ts:133-253](), [apps/mcp/src/server.ts:256-277]()

---

## Registered Tools

Tools are the primary way AI assistants interact with Supermemory.

### `memory`
Saves or forgets information. Uses `SupermemoryClient.createMemory` or `SupermemoryClient.forgetMemory`.
- **Action**: `save` (default) or `forget`.
- **Content**: The text to remember/remove (up to 200,000 characters).
- **Container**: Scoped to `containerTag` if provided.

Sources: [apps/mcp/src/server.ts:109-118](), [apps/mcp/src/client.ts:150-169](), [apps/mcp/src/client.ts:172-239]()

### `recall`
Searches memories. Uses `SupermemoryClient.search` or `SupermemoryClient.getProfile`.
- **Query**: Semantic search string.
- **includeProfile**: Boolean to toggle user preference context.

Sources: [apps/mcp/src/server.ts:121-130](), [apps/mcp/src/client.ts:242-284]()

### `listProjects`
Discovers valid project names (container tags) for the user to help assistants organize memories correctly.
Sources: [apps/mcp/src/server.ts:193-253]()

### `whoAmI`
Returns current session info, including `userId`, `email`, and `sessionId`.
Sources: [apps/mcp/src/server.ts:256-286]()

---

## Registered Resources

Resources provide static or dynamic data as URI-addressable entities.

| Resource Name | URI | Format | Description |
|---|---|---|---|
| `User Profile` | `supermemory://profile` | `text/plain` | Formatted markdown of stable preferences and recent activity. |
| `My Projects` | `supermemory://projects` | `application/json` | JSON list of user projects and container tags. |

Sources: [apps/mcp/src/server.ts:133-190]()

---

## Interactive Visualization

The MCP server includes a built-in interactive memory graph visualization. This is served as a single-file HTML application embedded within the server package via `mcp-app.html`.

- **Implementation**: The server imports `mcpAppHtml` [apps/mcp/src/server.ts:12]() and exposes it for client-side rendering.
- **Client UI**: The UI logic in `apps/mcp/src/ui/mcp-app.ts` uses `force-graph` to render a 2D/3D force-directed graph [apps/mcp/src/ui/mcp-app.ts:12]().
- **Integration**: In the web application, `ChatGraphContextRail` uses the `MemoryGraph` component to show memories used by the AI assistant (Nova) during chat [apps/web/components/chat/chat-graph-context-rail.tsx:12-63]().

**Graph Entity Mapping:**

```mermaid
graph LR
  subgraph "Code_Entity_Space"
    [DocumentNode]
    [MemoryNode]
    [GraphLink]
  end

  subgraph "Visual_Space"
    ["Blue_Circle"]
    ["Hexagon"]
    ["Dashed_Line"]
  end

  [DocumentNode] ---|"renders as"| ["Blue_Circle"]
  [MemoryNode] ---|"renders as"| ["Hexagon"]
  [GraphLink] ---|"renders as"| ["Dashed_Line"]
```

Sources: [apps/mcp/src/ui/mcp-app.ts:60-90](), [apps/mcp/mcp-app.html:50-89]()

---

## Authentication & Routing

The `apps/mcp/src/index.ts` file uses `Hono` to route incoming MCP requests and handle authentication.

1. **Discovery**: Implements `/.well-known/oauth-protected-resource` for MCP client discovery of the authorization server [apps/mcp/src/index.ts:69-81]().
2. **Auth Validation**: Intercepts requests to `/mcp/*`, validating either a Bearer API key (checked via `isApiKey`) or an OAuth token [apps/mcp/src/index.ts:145-151]().
3. **Context Injection**: After validation, it populates `Props` (userId, apiKey, containerTag, etc.) and forwards the request to the `SupermemoryMCP` Durable Object [apps/mcp/src/index.ts:179-192]().

Sources: [apps/mcp/src/index.ts:119-192](), [apps/mcp/src/auth.ts:1-10]()

---

## Analytics

The server integrates with PostHog to track tool usage and session metrics.

- **Initialization**: `initPosthog` is called with `POSTHOG_API_KEY` from environment bindings [apps/mcp/src/server.ts:51]().
- **Client Capture**: Hooks `oninitialized` to capture and store the MCP client name and version in Durable Object storage [apps/mcp/src/server.ts:54-63]().
- **Events**: The server tracks interactions via the `posthog` instance.

Sources: [apps/mcp/src/posthog.ts:14-25](), [apps/mcp/src/server.ts:51-63]()

---

# Page: Setup & Installation

# Setup & Installation

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [apps/docs/images/supermemory-mcp/claude-desktop/step-1.png](apps/docs/images/supermemory-mcp/claude-desktop/step-1.png)
- [apps/docs/images/supermemory-mcp/claude-desktop/step-2.png](apps/docs/images/supermemory-mcp/claude-desktop/step-2.png)
- [apps/docs/images/supermemory-mcp/claude-desktop/step-3.png](apps/docs/images/supermemory-mcp/claude-desktop/step-3.png)
- [apps/docs/images/supermemory-mcp/claude-desktop/step-4.png](apps/docs/images/supermemory-mcp/claude-desktop/step-4.png)
- [apps/docs/supermemory-mcp/claude-desktop.mdx](apps/docs/supermemory-mcp/claude-desktop.mdx)
- [apps/docs/supermemory-mcp/introduction.mdx](apps/docs/supermemory-mcp/introduction.mdx)
- [apps/docs/supermemory-mcp/mcp.mdx](apps/docs/supermemory-mcp/mcp.mdx)
- [apps/docs/supermemory-mcp/setup.mdx](apps/docs/supermemory-mcp/setup.mdx)
- [apps/mcp/README.md](apps/mcp/README.md)
- [apps/mcp/e2e/auth.test.ts](apps/mcp/e2e/auth.test.ts)
- [apps/mcp/e2e/capture-oauth-token.ts](apps/mcp/e2e/capture-oauth-token.ts)
- [apps/mcp/e2e/discovery.test.ts](apps/mcp/e2e/discovery.test.ts)
- [apps/mcp/e2e/graph.test.ts](apps/mcp/e2e/graph.test.ts)
- [apps/mcp/e2e/helpers.ts](apps/mcp/e2e/helpers.ts)
- [apps/mcp/e2e/memory.test.ts](apps/mcp/e2e/memory.test.ts)
- [apps/mcp/e2e/oauth.test.ts](apps/mcp/e2e/oauth.test.ts)
- [apps/mcp/e2e/root-scope.test.ts](apps/mcp/e2e/root-scope.test.ts)
- [apps/mcp/package.json](apps/mcp/package.json)
- [apps/mcp/vitest.config.ts](apps/mcp/vitest.config.ts)
- [apps/web/components/connect-ai-modal.tsx](apps/web/components/connect-ai-modal.tsx)
- [apps/web/components/mcp-modal/claude-desktop-manual-timeline.tsx](apps/web/components/mcp-modal/claude-desktop-manual-timeline.tsx)
- [apps/web/components/mcp-modal/mcp-detail-view.tsx](apps/web/components/mcp-modal/mcp-detail-view.tsx)
- [apps/web/lib/mcp-client-setup.ts](apps/web/lib/mcp-client-setup.ts)
- [apps/web/lib/mcp-manual-instructions.ts](apps/web/lib/mcp-manual-instructions.ts)
- [apps/web/public/mcp-supported-tools/antigravity.png](apps/web/public/mcp-supported-tools/antigravity.png)

</details>



This page covers the installation and technical configuration of the Supermemory MCP Server. The MCP Server enables AI assistants such as Claude Desktop, Cursor, and Windsurf to maintain persistent memory across conversations using the Model Context Protocol (MCP).

## Overview

The Supermemory MCP Server is a standalone component built on Cloudflare Workers that gives AI assistants persistent memory across conversations [apps/mcp/README.md:1-3](). It leverages Durable Objects for scalable, persistent connections and supports both OAuth and API key authentication [apps/mcp/README.md:3-7]().

### System Components

| Component | Identifier | Purpose |
|-----------|------------|---------|
| **MCP Server** | `supermemory-mcp` | The core service implementing the Model Context Protocol [apps/mcp/package.json:2](). |
| **Authentication** | `OAuth / API Key` | Secure access via Supermemory accounts or `sm_` prefixed keys [apps/docs/supermemory-mcp/introduction.mdx:46-50](). |
| **Client Info** | `whoAmI` | Tool to resolve current user identity and session details [apps/mcp/README.md:113-121](). |
| **Resources** | `supermemory://` | URI-based access to user profiles and project lists [apps/mcp/README.md:123-128](). |

Sources: [apps/mcp/README.md:1-128](), [apps/mcp/package.json:1-23](), [apps/docs/supermemory-mcp/introduction.mdx:46-50]()

## Installation Architecture

```mermaid
graph TB
    subgraph "Natural Language Space (AI Clients)"
        Claude["Claude Desktop"]
        Cursor["Cursor IDE"]
        Windsurf["Windsurf"]
        Cline["Cline / Roo-Cline"]
    end

    subgraph "Code Entity Space (MCP Server)"
        MCP_URL["https://mcp.supermemory.ai/mcp"]
        Handshake["Handshake Handler<br/>apps/mcp/e2e/discovery.test.ts"]
        AuthLogic["Auth Logic<br/>apps/mcp/e2e/auth.test.ts"]
        
        subgraph "Tools & Resources"
            MemoryTool["memory tool<br/>apps/mcp/README.md:77"]
            RecallTool["recall tool<br/>apps/mcp/README.md:95"]
            ProfileRes["supermemory://profile<br/>apps/mcp/README.md:127"]
        end
    end

    subgraph "Supermemory Backend"
        API["api.supermemory.ai"]
        Ingestion["Ingestion Pipeline"]
    end

    Claude -->|"JSON-RPC"| MCP_URL
    Cursor -->|"JSON-RPC"| MCP_URL
    MCP_URL --> Handshake
    Handshake --> AuthLogic
    AuthLogic -->|"Validate"| API
    MemoryTool -->|"Save/Forget"| Ingestion
    RecallTool -->|"Search"| API
```

**Supermemory MCP Installation Data Flow**

The diagram illustrates how AI clients connect to the MCP URL, which performs a handshake and validates authentication before exposing memory tools.

Sources: [apps/mcp/README.md:17-112](), [apps/mcp/e2e/discovery.test.ts:22-40](), [apps/mcp/e2e/auth.test.ts:23-64]()

## Quick Install (npx)

The recommended way to install the MCP server is using the `install-mcp` CLI. This utility automates the modification of client configuration files.

### Command Usage
```bash
npx -y install-mcp@latest https://mcp.supermemory.ai/mcp --client <client> --oauth=yes
```
*   **`--client`**: Specify `claude`, `cursor`, `windsurf`, `vscode`, `cline`, or `antigravity` [apps/docs/supermemory-mcp/mcp.mdx:11-15](), [apps/web/lib/mcp-manual-instructions.ts:63-68]().
*   **`--oauth=yes`**: Enables the standard OAuth flow for authentication [apps/docs/supermemory-mcp/mcp.mdx:12]().
*   **`--project`**: Optionally scope the installation to a specific project ID [apps/web/components/mcp-modal/mcp-detail-view.tsx:232-234]().

Sources: [apps/docs/supermemory-mcp/mcp.mdx:9-15](), [apps/docs/supermemory-mcp/setup.mdx:7-13](), [apps/mcp/README.md:17-21](), [apps/web/components/mcp-modal/mcp-detail-view.tsx:226-235]()

## Manual Configuration

If the CLI tool is not used, the server can be added manually to the JSON configuration files of supported AI clients.

### Standard JSON Structure
Add the following to your MCP client config (e.g., `claude_desktop_config.json` or `mcp.json`):

```json
{
  "mcpServers": {
    "supermemory": {
      "url": "https://mcp.supermemory.ai/mcp"
    }
  }
}
```

### API Key Authentication (Alternative)
While OAuth is the default [apps/docs/supermemory-mcp/setup.mdx:29](), you can provide a static API key via the `Authorization` header. Keys must start with the `sm_` prefix to be recognized and skip the OAuth flow [apps/mcp/README.md:39-54](). The web UI provides a `ConnectAIModal` to generate these keys with the metadata type `mcp-manual` [apps/web/components/connect-ai-modal.tsx:245-250]().

```json
{
  "mcpServers": {
    "supermemory": {
      "url": "https://mcp.supermemory.ai/mcp",
      "headers": {
        "Authorization": "Bearer sm_your_api_key_here"
      }
    }
  }
}
```

### Project Scoping
To isolate memories by project, use the `x-sm-project` header. This locks the connection to a specific project ID and strips the `containerTag` parameter from tool schemas to prevent cross-project leakage [apps/mcp/e2e/root-scope.test.ts:18-34]().

```json
{
  "mcpServers": {
    "supermemory": {
      "url": "https://mcp.supermemory.ai/mcp",
      "headers": {
        "x-sm-project": "your-project-id"
      }
    }
  }
}
```

Sources: [apps/docs/supermemory-mcp/setup.mdx:15-65](), [apps/mcp/README.md:39-73](), [apps/mcp/e2e/root-scope.test.ts:18-34](), [apps/web/components/connect-ai-modal.tsx:239-255]()

## Implementation & Testing

The server implementation is verified through an extensive E2E suite that drives a real MCP server over streamable HTTP [apps/mcp/README.md:173-178]().

```mermaid
classDiagram
    class MCP_Server_4_0 {
        +Handshake()
        +ToolDiscovery()
        +ResourceDiscovery()
    }
    class Auth_Tiers {
        +Tier_A_Discovery()
        +Tier_B_Registration()
        +Tier_C_Negative_Tests()
        +Tier_D_Real_Token()
    }
    class Memory_Operations {
        +Save(content, containerTag)
        +Recall(query, includeProfile)
        +Forget(content)
    }
    MCP_Server_4_0 --> Auth_Tiers : validates
    MCP_Server_4_0 --> Memory_Operations : executes
```

**Technical Implementation Tiers**

The testing infrastructure splits authentication into four tiers, ranging from public discovery (Tier A) to real OAuth token exchange (Tier D) [apps/mcp/e2e/oauth.test.ts:15-125]().

### Key Tools & Behavior
*   **`memory`**: Saves or forgets information. Ingestion into the search index is eventually consistent and may take up to 90 seconds [apps/mcp/README.md:77-94, 216-218]().
*   **`recall`**: Performs semantic search and optionally retrieves the user profile [apps/mcp/README.md:95-112]().
*   **`context` Prompt**: A pre-formatted system message that injects stable preferences and recent activity into the AI's context window [apps/docs/supermemory-mcp/mcp.mdx:104-120]().
*   **`memory-graph`**: Returns a summary and structured documents for visualization [apps/mcp/e2e/graph.test.ts:14-23]().

Sources: [apps/mcp/e2e/oauth.test.ts:15-125](), [apps/mcp/README.md:216-218](), [apps/docs/supermemory-mcp/mcp.mdx:104-120](), [apps/mcp/e2e/graph.test.ts:14-23]()

## Client-Specific Configuration Paths

The `getManualInstallEntry` function in the codebase defines the specific paths and snippets for various clients [apps/web/lib/mcp-manual-instructions.ts:57-129]().

| Client | Configuration File Path | Format |
|--------|-------------------------|--------|
| **Claude Desktop** | `~/Library/Application Support/Claude/claude_desktop_config.json` | JSON [apps/web/components/mcp-modal/claude-desktop-manual-timeline.tsx:29-38]() |
| **Cursor** | `~/.cursor/mcp.json` (global) or `.cursor/mcp.json` (local) | JSON [apps/web/lib/mcp-manual-instructions.ts:82-84]() |
| **VS Code** | `~/Library/Application Support/Code/User/mcp.json` (macOS) | JSON [apps/web/lib/mcp-manual-instructions.ts:90-92]() |
| **Antigravity** | `~/.gemini/config/mcp_config.json` | JSON [apps/web/lib/mcp-manual-instructions.ts:66-68]() |
| **Codex** | `~/.codex/config.toml` | TOML [apps/web/lib/mcp-manual-instructions.ts:74-76]() |
| **Cline** | `globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json` | JSON [apps/web/lib/mcp-manual-instructions.ts:98-100]() |

Sources: [apps/web/lib/mcp-manual-instructions.ts:57-129](), [apps/web/components/mcp-modal/claude-desktop-manual-timeline.tsx:29-38](), [apps/docs/supermemory-mcp/setup.mdx:69-93]()

---

# Page: Tools, Resources & Prompts

# Tools, Resources & Prompts

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CLAUDE.md](CLAUDE.md)
- [apps/mcp/.dev.vars.example](apps/mcp/.dev.vars.example)
- [apps/mcp/.gitignore](apps/mcp/.gitignore)
- [apps/mcp/mcp-app.html](apps/mcp/mcp-app.html)
- [apps/mcp/src/auth.ts](apps/mcp/src/auth.ts)
- [apps/mcp/src/client.ts](apps/mcp/src/client.ts)
- [apps/mcp/src/format.ts](apps/mcp/src/format.ts)
- [apps/mcp/src/html.d.ts](apps/mcp/src/html.d.ts)
- [apps/mcp/src/index.ts](apps/mcp/src/index.ts)
- [apps/mcp/src/posthog.ts](apps/mcp/src/posthog.ts)
- [apps/mcp/src/server.ts](apps/mcp/src/server.ts)
- [apps/mcp/src/ui/global.css](apps/mcp/src/ui/global.css)
- [apps/mcp/src/ui/mcp-app.css](apps/mcp/src/ui/mcp-app.css)
- [apps/mcp/src/ui/mcp-app.ts](apps/mcp/src/ui/mcp-app.ts)
- [apps/mcp/tsconfig.json](apps/mcp/tsconfig.json)
- [apps/mcp/vite.config.ts](apps/mcp/vite.config.ts)
- [apps/mcp/wrangler.jsonc](apps/mcp/wrangler.jsonc)
- [apps/web/components/chat/chat-graph-context-rail.tsx](apps/web/components/chat/chat-graph-context-rail.tsx)
- [apps/web/lib/chat-auto-space.ts](apps/web/lib/chat-auto-space.ts)

</details>



The Supermemory MCP server, implemented as a Cloudflare Worker using Durable Objects, provides a standardized interface for AI assistants to interact with a user's knowledge base. This page documents the specific tools, resources, and prompts registered within the MCP server, their underlying implementation in `SupermemoryMCP`, and the data flow between the MCP protocol and the Supermemory API.

## MCP Tools

Tools are executable functions that an AI assistant can call. The Supermemory MCP server registers five primary tools to manage memories, discover project contexts, and visualize the memory graph.

### Tool Definition and Registration

Tools are defined using Zod schemas for input validation and registered via the `this.server.registerTool` method within the `SupermemoryMCP` class [apps/mcp/src/server.ts:109-130]().

```mermaid
graph TD
    subgraph "MCP Client (e.g. Claude Desktop)"
        Call["callTool('recall', {query: '...'})"]
    end

    subgraph "apps/mcp/src/server.ts"
        SM_MCP["SupermemoryMCP Class"]
        HandleRecall["handleRecall(args)"]
    end

    subgraph "apps/mcp/src/client.ts"
        Client["SupermemoryClient"]
        Search["search(query, limit, threshold)"]
    end

    subgraph "External API"
        API["api.supermemory.ai/v3/search/memories"]
    end

    Call --> SM_MCP
    SM_MCP --> HandleRecall
    HandleRecall --> Client
    Client --> Search
    Search --> API
```
**Sources:** [apps/mcp/src/server.ts:121-130](), [apps/mcp/src/client.ts:242-258]()

### 1. `memory`
Used to persist or remove information. It acts as the primary write interface for the AI's long-term memory.

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `content` | `string` | The text to remember or forget (max 200,000 chars). | Required |
| `action` | `"save" \| "forget"` | Whether to store the information or remove it. | `"save"` |
| `containerTag`| `string` | Optional project identifier to scope the memory. | Root tag |

**Behavior:**
- **Save:** Calls `this.client.createMemory(content)` which uses the SDK's `client.add` method [apps/mcp/src/client.ts:150-169]().
- **Forget:** Attempts an exact match first via `client.memories.forget`. If not found (404), it performs a semantic search with a high similarity threshold (0.85) to find and delete the most relevant memory [apps/mcp/src/client.ts:172-239]().

**Sources:** [apps/mcp/src/server.ts:77-84](), [apps/mcp/src/server.ts:109-118](), [apps/mcp/src/client.ts:172-239]()

### 2. `recall`
The primary retrieval tool for searching the user's knowledge base.

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `query` | `string` | Search query for semantic/hybrid search. | Required |
| `includeProfile`| `boolean` | Whether to append the user's profile summary to the results. | `true` |
| `containerTag` | `string` | Optional project identifier to scope the search. | Root tag |

**Return Value:**
Returns a list of relevant memories (or document chunks) formatted via `formatMemories` and, if requested, the user's profile summary [apps/mcp/src/server.ts:121-130](), [apps/mcp/src/format.ts:1-11]().

**Sources:** [apps/mcp/src/server.ts:86-93](), [apps/mcp/src/server.ts:121-130](), [apps/mcp/src/format.ts:1-157]()

### 3. `listProjects`
Allows the AI to discover valid `containerTag` values for organizing information.

**Behavior:**
- Triggers a refresh of tags from the server using `this.refreshContainerTags()` or ensures they are fresh based on `CONTAINER_TAGS_TTL_MS` [apps/mcp/src/server.ts:211-215]().
- Accesses the cached list in `this.cachedContainerTags` [apps/mcp/src/server.ts:216]().
- Returns a formatted list of project names for the AI to use in subsequent `memory` or `recall` calls [apps/mcp/src/server.ts:233]().

**Sources:** [apps/mcp/src/server.ts:193-253]()

### 4. `whoAmI`
Returns metadata about the current authenticated session.

**Return Value:**
An object containing `userId`, `email`, `name`, and the client info (name and version) stored in the Durable Object storage [apps/mcp/src/server.ts:256-274]().

**Sources:** [apps/mcp/src/server.ts:256-274]()

### 5. `memory_graph`
Registered via `registerAppTool`, this provides an interactive visualization of the knowledge graph within supporting MCP clients (like Claude Desktop) [apps/mcp/src/server.ts:4-7]().

- **Behavior:** It fetches documents and their associated memory entries for a specific `containerTag` [apps/mcp/src/ui/mcp-app.ts:189-217]().
- **UI Implementation:** Uses `force-graph` to render a force-directed graph [apps/mcp/src/ui/mcp-app.ts:12]().
- **Visual Encoding:**
    - **Documents:** Rectangular nodes [apps/mcp/src/ui/mcp-app.ts:207-217]().
    - **Memories:** Hexagonal nodes, color-coded by state: Recent (Green), Expiring (Orange), Forgotten (Red), or Default (Blue) [apps/mcp/src/ui/mcp-app.ts:95-100](), [apps/mcp/src/ui/mcp-app.ts:162-171]().

**Sources:** [apps/mcp/src/ui/mcp-app.ts:1-217](), [apps/mcp/mcp-app.html:1-95]()

---

## MCP Resources

Resources are read-only data sources that the AI can "open" or subscribe to. They are identified by URIs.

### 1. User Profile (`supermemory://profile`)
Provides a comprehensive view of the user's identity derived from their memories.

- **Implementation:** Calls `client.getProfile()` [apps/mcp/src/server.ts:139]().
- **Data Structure:**
    - **Stable Preferences:** Static facts about the user (e.g., "Prefers TypeScript").
    - **Recent Activity:** Dynamic facts or recent interactions.
- **MIME Type:** `text/plain` [apps/mcp/src/server.ts:160]().

**Sources:** [apps/mcp/src/server.ts:133-169](), [apps/mcp/src/client.ts:274-286]()

### 2. My Projects (`supermemory://projects`)
Provides a machine-readable list of the user's projects.

- **Implementation:** Uses `this.cachedContainerTags` after ensuring they are fresh [apps/mcp/src/server.ts:177-178]().
- **MIME Type:** `application/json` [apps/mcp/src/server.ts:184]().

**Sources:** [apps/mcp/src/server.ts:172-190]()

---

## Context Prompts

Prompts are predefined templates that help guide the AI's behavior or provide system-level context.

### `context` Prompt
The `context` prompt is designed to be injected into the system message to give the AI assistant a "personality" and awareness of the user's preferences.

- **Arguments:** `includeRecent` (boolean, default `true`) and `containerTag` (optional string) [apps/mcp/src/server.ts:95-102]().
- **Behavior:** It fetches the user's profile and formats it into a system instruction, emphasizing that the AI should act as an extension of the user's memory [apps/mcp/src/server.ts:335-349]().

**Sources:** [apps/mcp/src/server.ts:335-349]()

---

## Data Flow: MCP to Code Entities

The following diagram maps the Natural Language MCP interface to the specific classes and functions in the codebase.

```mermaid
graph LR
    subgraph "MCP Interface (Natural Language)"
        T1["Tool: memory"]
        T2["Tool: recall"]
        T3["Tool: memory_graph"]
        R1["Resource: User Profile"]
    end

    subgraph "Code Entity Space (apps/mcp/src/)"
        Srv["SupermemoryMCP (server.ts)"]
        H_Mem["handleMemory()"]
        H_Rec["handleRecall()"]
        UI_App["mcp-app.ts (UI)"]
        
        Cl["SupermemoryClient (client.ts)"]
        C_Add["createMemory()"]
        C_Sch["search()"]
        C_Prf["getProfile()"]
        C_Doc["getDocuments()"]
    end

    subgraph "External SDK (packages/supermemory/)"
        SDK["Supermemory SDK (client.ts)"]
    end

    T1 --> H_Mem
    T2 --> H_Rec
    T3 --> UI_App
    R1 --> Srv

    H_Mem --> C_Add
    H_Rec --> C_Sch
    Srv --> C_Prf
    UI_App --> C_Doc

    C_Add --> SDK
    C_Sch --> SDK
    C_Prf --> SDK
    C_Doc --> SDK
```
**Sources:** [apps/mcp/src/server.ts:109-130](), [apps/mcp/src/client.ts:129-147](), [apps/mcp/src/ui/mcp-app.ts:189-217]()

## Implementation Details: `SupermemoryClient`

The `SupermemoryClient` class in `apps/mcp/src/client.ts` acts as a wrapper around the official `supermemory` SDK to provide MCP-specific logic like character limiting and semantic deletion fallback.

- **Character Limiting:** All text returned to the MCP client is truncated via `limitByChars` (default 200,000 characters) to prevent context window overflow [apps/mcp/src/client.ts:3](), [apps/mcp/src/client.ts:110-112]().
- **Memory vs. Chunk:** The client distinguishes between atomic `memories` (facts) and document `chunks` (segments of uploaded files) using the `getMemoryText` utility [apps/mcp/src/client.ts:106-108]().
- **Normalization:** Search results from the SDK are mapped to a consistent `Memory` type that includes `id`, `similarity`, and the text content [apps/mcp/src/client.ts:260-271]().
- **Formatting:** The `formatMemories` utility in `apps/mcp/src/format.ts` provides a human-readable string representation of search results, including source metadata, document summaries, and relational context (parents, children, related) [apps/mcp/src/format.ts:1-157]().

**Sources:** [apps/mcp/src/client.ts:3-128](), [apps/mcp/src/client.ts:106-112](), [apps/mcp/src/format.ts:1-157]()

---

# Page: Authentication & Session Management

# Authentication & Session Management

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CLAUDE.md](CLAUDE.md)
- [apps/mcp/.dev.vars.example](apps/mcp/.dev.vars.example)
- [apps/mcp/.gitignore](apps/mcp/.gitignore)
- [apps/mcp/README.md](apps/mcp/README.md)
- [apps/mcp/e2e/auth.test.ts](apps/mcp/e2e/auth.test.ts)
- [apps/mcp/e2e/capture-oauth-token.ts](apps/mcp/e2e/capture-oauth-token.ts)
- [apps/mcp/e2e/discovery.test.ts](apps/mcp/e2e/discovery.test.ts)
- [apps/mcp/e2e/graph.test.ts](apps/mcp/e2e/graph.test.ts)
- [apps/mcp/e2e/helpers.ts](apps/mcp/e2e/helpers.ts)
- [apps/mcp/e2e/memory.test.ts](apps/mcp/e2e/memory.test.ts)
- [apps/mcp/e2e/oauth.test.ts](apps/mcp/e2e/oauth.test.ts)
- [apps/mcp/e2e/root-scope.test.ts](apps/mcp/e2e/root-scope.test.ts)
- [apps/mcp/mcp-app.html](apps/mcp/mcp-app.html)
- [apps/mcp/package.json](apps/mcp/package.json)
- [apps/mcp/src/auth.ts](apps/mcp/src/auth.ts)
- [apps/mcp/src/client.ts](apps/mcp/src/client.ts)
- [apps/mcp/src/format.ts](apps/mcp/src/format.ts)
- [apps/mcp/src/html.d.ts](apps/mcp/src/html.d.ts)
- [apps/mcp/src/index.ts](apps/mcp/src/index.ts)
- [apps/mcp/src/posthog.ts](apps/mcp/src/posthog.ts)
- [apps/mcp/src/server.ts](apps/mcp/src/server.ts)
- [apps/mcp/src/ui/global.css](apps/mcp/src/ui/global.css)
- [apps/mcp/src/ui/mcp-app.css](apps/mcp/src/ui/mcp-app.css)
- [apps/mcp/src/ui/mcp-app.ts](apps/mcp/src/ui/mcp-app.ts)
- [apps/mcp/tsconfig.json](apps/mcp/tsconfig.json)
- [apps/mcp/vite.config.ts](apps/mcp/vite.config.ts)
- [apps/mcp/vitest.config.ts](apps/mcp/vitest.config.ts)
- [apps/mcp/wrangler.jsonc](apps/mcp/wrangler.jsonc)
- [apps/web/components/chat/chat-graph-context-rail.tsx](apps/web/components/chat/chat-graph-context-rail.tsx)
- [apps/web/lib/chat-auto-space.ts](apps/web/lib/chat-auto-space.ts)

</details>



This page documents the authentication mechanisms and session management implementation within the Supermemory MCP server. The server supports a dual-authentication strategy using both API keys and OAuth 2.0, with session state persisted via Cloudflare Durable Objects to provide stable, stateful connections for AI assistants.

**Sources:** [apps/mcp/src/index.ts:1-178](), [apps/mcp/src/server.ts:27-60]()

## Overview

The MCP server acts as a stateful bridge between MCP clients (like Claude Desktop or Cursor) and the Supermemory API. Authentication is handled at the edge by a Hono router before requests are forwarded to a dedicated Durable Object instance that manages the protocol state. The server is deployed as a Cloudflare Worker using the `SupermemoryMCP` Durable Object class to maintain persistent state for MCP sessions.

**Sources:** [apps/mcp/src/index.ts:119-198](), [apps/mcp/wrangler.jsonc:23-37]()

## Authentication Mechanisms

### API Key Authentication
API keys are the primary method for programmatic or manual configuration. They are identified by the `sm_` prefix via the `isApiKey` utility. When a request includes an `Authorization: Bearer sm_...` header, the server uses `validateApiKey` to verify the credential against the Supermemory API `/v3/session` endpoint.

**Sources:** [apps/mcp/src/index.ts:145-147](), [apps/mcp/src/auth.ts:25-90]()

### OAuth 2.0 Discovery
For interactive clients, the server implements the MCP OAuth discovery specification. It exposes a `.well-known/oauth-protected-resource` endpoint that directs clients to `api.supermemory.ai` for authorization. If a client looks for the authorization server on the MCP domain directly, a proxy endpoint at `.well-known/oauth-authorization-server` fetches metadata from the main API.

**Sources:** [apps/mcp/src/index.ts:69-107]()

### Validation Logic
Both authentication paths resolve to an `authUser` object containing the user's ID and an API key used for subsequent data operations.

| Method | Detection | API Endpoint | Result |
| :--- | :--- | :--- | :--- |
| **API Key** | Starts with `sm_` | `/v3/session` | Validates existing key |
| **OAuth** | No `sm_` prefix | `/v3/mcp/session-with-key` | Exchanges token for API key |

**Sources:** [apps/mcp/src/index.ts:138-151](), [apps/mcp/src/auth.ts:92-161]()

## Request Flow & Data Mapping

The following diagram illustrates how natural language requests from an AI assistant are authenticated and mapped to internal code entities.

**Authentication and Entity Mapping Diagram**

```mermaid
sequenceDiagram
    participant Client as "MCP Client (Claude/Cursor)"
    participant Hono as "Hono Router (index.ts)"
    participant Auth as "auth.ts (validateApiKey/OAuth)"
    participant API as "Supermemory API (v3)"
    participant DO as "SupermemoryMCP (server.ts)"

    Client->>Hono: "POST /mcp/rpc (Bearer token)"
    Hono->>Auth: "isApiKey(token)"
    
    alt "Is API Key"
        Auth->>API: "GET /v3/session"
    else "Is OAuth"
        Auth->>API: "GET /v3/mcp/session-with-key"
    end
    
    API-->>Auth: "{ userId, apiKey, email, name }"
    Auth-->>Hono: "authUser object"
    
    Hono->>DO: "fetch() with Props"
    Note over DO: "Props: { userId, apiKey, containerTag }"
    DO->>DO: "getClient()"
    Note over DO: "Instantiates SupermemoryClient (client.ts)"
```

**Sources:** [apps/mcp/src/index.ts:119-192](), [apps/mcp/src/auth.ts:1-161](), [apps/mcp/src/server.ts:362-376]()

## Session Management with Durable Objects

The `SupermemoryMCP` class (extending `McpAgent`) manages the lifecycle of an MCP session. It utilizes Cloudflare Durable Object storage to persist metadata about the connecting client.

### Client Information Storage
During the MCP initialization handshake, the server captures the client's name and version using `this.server.server.oninitialized`. This information is persisted in the Durable Object's storage via `this.ctx.storage.put`. On subsequent loads, `init()` restores this from storage.

**Sources:** [apps/mcp/src/server.ts:42-63](), [apps/mcp/wrangler.jsonc:23-29]()

### Durable Object State Diagram

```mermaid
graph TD
    subgraph "SupermemoryMCP Instance [server.ts]"
        S["server: McpServer"]
        CI["clientInfo: {name, version}"]
        CT["cachedContainerTags: string[]"]
        P["props: Props (Ephemeral)"]
    end

    subgraph "ctx.storage (DurableObject Storage)"
        KVC["Key: 'clientInfo'"]
    end

    S -- "oninitialized" --> CI
    CI -- "storage.put()" --> KVC
    KVC -- "storage.get() in init()" --> CI
    
    P -- "apiKey" --> SC["SupermemoryClient [client.ts]"]
    P -- "containerTag" --> SC
```

**Sources:** [apps/mcp/src/server.ts:32-63](), [apps/mcp/src/server.ts:362-376]()

## Container Tag Scoping

The `containerTag` (or Project ID) determines the scope of memories and documents accessible during a session.

### Scoping Priority
1.  **Tool Argument:** A `containerTag` explicitly passed to a tool (e.g., `recall`) overrides all other settings. [apps/mcp/src/server.ts:86-93]()
2.  **Session Header:** The `x-sm-project` HTTP header sets a session-wide default stored in `this.props.containerTag`. [apps/mcp/src/index.ts:122](), [apps/mcp/src/index.ts:185]()
3.  **Global Default:** If neither is provided, the `SupermemoryClient` defaults to `sm_project_default`. [apps/mcp/src/client.ts:4](), [apps/mcp/src/client.ts:146]()

### Dynamic Schema Adjustment
The server dynamically adjusts Zod schemas based on whether a `containerTag` was provided at the session level. If `hasRootContainerTag` is true, the `containerTag` field is omitted from tool schemas to prevent the AI from overriding the user-defined project scope.

**Sources:** [apps/mcp/src/server.ts:67-84]()

## Project Caching & Refreshing

To minimize API calls, the MCP server caches the list of available projects (container tags) for a specific user.

*   **Cache Duration:** Controlled by `CONTAINER_TAGS_TTL_MS`, set to 5 minutes. [apps/mcp/src/server.ts:28-28]()
*   **Freshness Check:** The `ensureContainerTagsFresh` method checks if the cache has expired and triggers a refresh if needed. [apps/mcp/src/server.ts:430-438]()
*   **Manual Refresh:** The `listProjects` tool allows users to force a refresh by passing a `refresh: true` argument. [apps/mcp/src/server.ts:193-212]()

**Sources:** [apps/mcp/src/server.ts:28-28](), [apps/mcp/src/server.ts:430-448]()

## Error Handling & Status Mapping

The authentication layer maps Supermemory API error codes to human-readable messages for the MCP client.

| Status Code | Internal Mapping | User-Facing Message |
| :--- | :--- | :--- |
| **401** | Unauthorized | "Invalid or expired API key/token" |
| **402** | Payment Required | "Memory limit reached. Upgrade at supermemory.ai" |
| **429** | Too Many Requests | "Rate limit exceeded. Please wait a moment" |
| **500+** | Server Error | "Server error. Service may be temporarily unavailable" |

**Sources:** [apps/mcp/src/auth.ts:36-59](), [apps/mcp/src/auth.ts:108-130]()

If authentication fails in the Hono middleware, the server returns a JSON-RPC error response with code `-32000` and includes a `WWW-Authenticate` header pointing to the resource metadata URL for discovery.

**Sources:** [apps/mcp/src/index.ts:158-177]()

---

# Page: API Reference

# API Reference

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [apps/docs/authentication.mdx](apps/docs/authentication.mdx)
- [apps/docs/docs.json](apps/docs/docs.json)
- [apps/docs/integrations/claude-code.mdx](apps/docs/integrations/claude-code.mdx)
- [apps/docs/integrations/codex.mdx](apps/docs/integrations/codex.mdx)
- [apps/docs/integrations/openclaw.mdx](apps/docs/integrations/openclaw.mdx)
- [apps/docs/integrations/opencode.mdx](apps/docs/integrations/opencode.mdx)
- [apps/docs/integrations/supermemory-sdk.mdx](apps/docs/integrations/supermemory-sdk.mdx)
- [apps/docs/intro.mdx](apps/docs/intro.mdx)
- [apps/docs/quickstart.mdx](apps/docs/quickstart.mdx)
- [apps/docs/self-hosting/configuration.mdx](apps/docs/self-hosting/configuration.mdx)
- [apps/docs/self-hosting/local-vs-enterprise.mdx](apps/docs/self-hosting/local-vs-enterprise.mdx)

</details>



This page provides a high-level overview of the Supermemory REST API, including base URLs, versioning conventions, authentication, and the core endpoint groups. Supermemory is designed as a "Memory-as-a-Service" platform, offering a unified interface for ingestion, semantic search, and automated user profiling.

For detailed implementation guides on specific endpoint groups, refer to the child pages linked below.

---

## Base URL and Versioning

All API requests are directed to the root production domain or a self-hosted instance. The API uses path-based versioning to manage feature evolution. [apps/docs/docs.json:8-8]()

| Environment | Base URL |
| :--- | :--- |
| **Production API** | `https://api.supermemory.ai` |
| **Self-Hosted (Local)** | `http://localhost:6767` |
| **OpenAPI Spec** | `https://api.supermemory.ai/v3/openapi` |

### Active Versions

*   **`v3`**: The stable foundation for document ingestion (`/v3/add`), document management (`/v3/documents`), search (`/v3/search`), and connector management (`/v3/connections`). [apps/docs/docs.json:131-132]()
*   **`v4`**: Optimized endpoints for conversational AI and advanced retrieval, including the unified User Profile endpoint (`/v4/profile`) and updated search modes. [apps/docs/quickstart.mdx:96-99]()

Sources: [apps/docs/docs.json:8-8](), [apps/docs/quickstart.mdx:96-99](), [apps/docs/self-hosting/configuration.mdx:16-16]()

---

## Authentication

Supermemory uses Bearer Token authentication. All requests must include an `Authorization` header. [apps/docs/authentication.mdx:7-9]()

```http
Authorization: Bearer <YOUR_SUPERMEMORY_API_KEY>
```

### Key Types
1.  **Organization Keys**: Created via the [Supermemory Console](https://console.supermemory.ai). These have full access to all resources within an organization. [apps/docs/authentication.mdx:7-9]()
2.  **Scoped API Keys**: Created programmatically via `POST /v3/auth/scoped-key`. These are restricted to specific `containerTags`, providing fine-grained access control for multi-tenant applications. [apps/docs/authentication.mdx:60-65]()

For details, see [Authentication & Scoped Keys](#6.5).

Sources: [apps/docs/authentication.mdx:7-9](), [apps/docs/authentication.mdx:60-65](), [apps/docs/quickstart.mdx:17-19]()

---

## Core Concepts: Documents vs. Memories

Understanding the distinction between these two entities is critical for effective API usage.

*   **Documents**: The raw data you ingest (Text, PDFs, Images, Conversations). They serve as the "ground truth." [apps/docs/intro.mdx:29-34]()
*   **Memories**: Automatically extracted by Supermemory from documents and conversations. These are atomic, interconnected facts and preferences inferred from the source data to build a knowledge graph. [apps/docs/intro.mdx:43-46]()

### System Entity Mapping
The following diagram bridges the natural language concepts to the API routes and data structures.

```mermaid
graph TD
    subgraph "Natural Language Space"
        User["User Identity"]
        RawData["Files & Conversations"]
        Query["User Questions"]
    end

    subgraph "Code Entity Space"
        CT["containerTag (string)"]
        ADD["POST /v3/add (Document)"]
        MEM["Memory (Extracted Entity)"]
        PROF["POST /v4/profile (User Profile)"]
    end

    User -- "Identified by" --> CT
    RawData -- "Ingested via" --> ADD
    ADD -- "Processed into" --> MEM
    Query -- "Triggers" --> PROF
    MEM -- "Populates" --> PROF
    CT -- "Scopes" --> ADD
    CT -- "Scopes" --> MEM
```
Sources: [apps/docs/quickstart.mdx:96-99](), [apps/docs/authentication.mdx:83-85](), [apps/docs/intro.mdx:43-46]()

---

## Endpoint Groups

The Supermemory API is organized into functional groups. Each group is detailed in its respective child page.

### 1. Memory & Document Endpoints
Handles the ingestion pipeline, including text snippets, file uploads (PDF, Images), and conversation transcripts. It also provides listing and deletion capabilities. [apps/docs/integrations/supermemory-sdk.mdx:38-40]()
*   **Key Routes**: `POST /v3/add`, `GET /v3/documents/list`, `DELETE /v3/documents/delete`.
*   **For details, see [Memory & Document Endpoints](#6.1)**.

### 2. Profile & Search Endpoints
Provides semantic and hybrid search capabilities. The Profile endpoint returns "Static" facts (long-term) and "Dynamic" context (episodic) for LLM system prompts. [apps/docs/intro.mdx:52-58]()
*   **Key Routes**: `POST /v4/profile`, `POST /v3/search`.
*   **For details, see [Profile & Search Endpoints](#6.2)**.

### 3. Connectors API
Manage automated syncing from external platforms like GitHub, Gmail, Google Drive, Notion, and OneDrive. [apps/docs/docs.json:115-132]()
*   **Key Routes**: `POST /v3/connections/{provider}`, `DELETE /v3/connections/{id}`.
*   **For details, see [Connectors API](#6.3)**.

### 4. Projects & Container Tags
Explains the logical isolation of data using `containerTag`. This is the primary mechanism for multi-tenancy and scoping search results. [apps/docs/authentication.mdx:60-61]()
*   **For details, see [Projects & Container Tags](#6.4)**.

### 5. Authentication & Scoped Keys
Technical details on managing API keys and programmatic key rotation, including creating keys restricted to specific containers. [apps/docs/authentication.mdx:58-65]()
*   **For details, see [Authentication & Scoped Keys](#6.5)**.

---

## Request Flow Architecture

This diagram illustrates how a client request moves through the API layers to the underlying storage and processing engines.

```mermaid
sequenceDiagram
    participant C as Client (SDK/cURL)
    participant API as api.supermemory.ai (Hono/Cloudflare)
    participant Auth as Auth Middleware
    participant Pipe as Ingestion Pipeline (v3/add)
    participant Engine as Graph & Vector Engine

    C->>API: POST /v3/add { content, containerTag }
    API->>Auth: Validate Bearer Token
    Auth-->>API: Token Valid (Org/Scoped)
    API->>Pipe: Dispatch Ingestion Job
    Pipe-->>API: Document ID (doc_123)
    API-->>C: 200 OK { id: "doc_123" }
    
    Note over Pipe, Engine: Async Extraction (OCR, Fact Extraction, Graph Update)
    Pipe->>Engine: Store Memories & Chunks
```
Sources: [apps/docs/quickstart.mdx:116-120](), [apps/docs/authentication.mdx:17-22](), [apps/docs/intro.mdx:21-23]()

---

## Standard Responses

### Success
Most POST endpoints return a standard object containing the resource ID.
```json
{
  "id": "doc_123",
  "success": true
}
```

### Errors
The API uses standard HTTP status codes:
*   **400 Bad Request**: Missing parameters (e.g., missing `containerTag`).
*   **401 Unauthorized**: Invalid or expired API key. [apps/docs/authentication.mdx:104-107]()
*   **404 Not Found**: Resource (document or connection) does not exist.
*   **429 Too Many Requests**: Rate limit exceeded for the provided key. [apps/docs/authentication.mdx:86-87]()

Sources: [apps/docs/authentication.mdx:104-107](), [apps/docs/authentication.mdx:86-87](), [apps/docs/quickstart.mdx:17-19]()

---

# Page: Memory & Document Endpoints

# Memory & Document Endpoints

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [apps/docs/add-memories/overview.mdx](apps/docs/add-memories/overview.mdx)
- [apps/docs/document-operations.mdx](apps/docs/document-operations.mdx)
- [apps/docs/memory-api/creation/adding-memories.mdx](apps/docs/memory-api/creation/adding-memories.mdx)
- [apps/docs/memory-api/ingesting.mdx](apps/docs/memory-api/ingesting.mdx)
- [apps/docs/memory-api/introduction.mdx](apps/docs/memory-api/introduction.mdx)
- [apps/docs/memory-api/overview.mdx](apps/docs/memory-api/overview.mdx)
- [apps/docs/memory-api/sdks/native.mdx](apps/docs/memory-api/sdks/native.mdx)
- [apps/docs/memory-api/sdks/python.mdx](apps/docs/memory-api/sdks/python.mdx)
- [apps/docs/memory-api/sdks/typescript.mdx](apps/docs/memory-api/sdks/typescript.mdx)
- [apps/docs/memory-api/searching/searching-memories.mdx](apps/docs/memory-api/searching/searching-memories.mdx)
- [apps/docs/memory-api/track-progress.mdx](apps/docs/memory-api/track-progress.mdx)
- [apps/docs/migration/from-zep.mdx](apps/docs/migration/from-zep.mdx)
- [apps/docs/n8n.mdx](apps/docs/n8n.mdx)
- [apps/docs/update-delete-memories/overview.mdx](apps/docs/update-delete-memories/overview.mdx)
- [apps/docs/zapier.mdx](apps/docs/zapier.mdx)

</details>



This page documents the core document management API endpoints for creating, updating, deleting, and retrieving documents in Supermemory. These endpoints form the foundation for ingesting content into the memory system.

**Scope**: This page covers document CRUD operations, file uploads, and batch processing. For semantic search and retrieval operations, see **Profile & Search Endpoints (6.2)**. For automated data ingestion from external services, see **Connectors API (6.3)**. For organizing documents with container tags, see **Projects & Container Tags (6.4)**.

---

## Document Lifecycle

Supermemory distinguishes between **Documents** (raw input like files, URLs, or text) and **Memories** (intelligently chunked, searchable pieces derived from documents) [apps/docs/memory-api/ingesting.mdx:13-18]().

### Code Entity to System Space Mapping
The following diagram illustrates how API requests interact with the internal processing pipeline and storage entities.

Title: "Document Ingestion Architecture"
```mermaid
graph TD
    subgraph "Ingestion_Space_(Code_Entities)"
        A["POST /v3/documents"] -->|"client.add()"| P["Processing_Pipeline"]
        B["POST /v3/documents/file"] -->|"client.documents.uploadFile()"| P
        D["Connector_Sync"] -->|"Ingestion_Engine"| P
    end
    
    subgraph "Processing_Pipeline_(Logic)"
        P --> E["Content_Extraction_(OCR/Transcription)"]
        E --> F["Chunking"]
        F --> G["Embedding_Generation"]
        G --> H["Memory_Extraction"]
    end
    
    subgraph "Storage_Space_(Database_Entities)"
        H --> I[("Documents_Table")]
        H --> J[("Memories_Table")]
        H --> K[("Vector_Index")]
    end
    
    subgraph "Management_Space_(Code_Entities)"
        L["PATCH /v3/documents/:id"] -->|"client.documents.update()"| I
        M["DELETE /v3/documents/:id"] -->|"client.documents.delete()"| I
        N["GET /v3/documents/list"] -->|"client.documents.list()"| I
    end
    
    I --> N
```

**Document Flow**: Content enters through direct API calls or connectors, undergoes processing (extraction, chunking, embedding), and is stored. Documents are automatically broken into optimal memories for search [apps/docs/memory-api/ingesting.mdx:48-67]().

Sources: [apps/docs/memory-api/ingesting.mdx:13-27](), [apps/docs/memory-api/ingesting.mdx:48-67](), [apps/docs/memory-api/ingesting.mdx:15-18]()

---

## Creating Documents

### POST /v3/documents
The primary endpoint for adding content. It supports text, URLs (auto-extracted), and metadata [apps/docs/add-memories/overview.mdx:121-123]().

#### Request Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `content` | string | Yes | Text, URL, or supported format to process [apps/docs/memory-api/ingesting.mdx:150](). |
| `containerTag` | string | No | **Recommended**: Single tag to group memories in a space [apps/docs/memory-api/ingesting.mdx:151](). |
| `customId` | string | No | Your identifier (max 100 chars). Enables idempotent updates [apps/docs/update-delete-memories/overview.mdx:161-165](). |
| `metadata` | object | No | Additional key-value metadata (strings, numbers, booleans) [apps/docs/memory-api/ingesting.mdx:153](). |

#### Response Schema
```json
{
  "id": "D2Ar7Vo7ub83w3PRPZcaP1",
  "status": "queued"
}
```
[apps/docs/memory-api/ingesting.mdx:161-166]()

#### Idempotency with customId
Using `customId` enables idempotent operations. If a document with the same `customId` is sent via `client.add()`, Supermemory updates the existing document instead of creating a duplicate [apps/docs/update-delete-memories/overview.mdx:68-70]().

Sources: [apps/docs/memory-api/ingesting.mdx:146-166](), [apps/docs/update-delete-memories/overview.mdx:68-165](), [apps/docs/add-memories/overview.mdx:119-148]()

---

## File Upload

### POST /v3/documents/file
Uploads binary files for automatic extraction. Supports OCR for images and transcription for videos [apps/docs/memory-api/ingesting.mdx:180-182]().

#### Supported Content Types
| Category | Formats | Processing |
|----------|---------|------------|
| Documents | PDF, Google Docs, Office files | Text extraction + OCR for scans [apps/docs/add-memories/overview.mdx:212-217]() |
| Images | JPG, PNG, GIF, WebP | OCR text extraction [apps/docs/add-memories/overview.mdx:219]() |
| Media | YouTube videos, MP4 | Transcription/Caption extraction [apps/docs/add-memories/overview.mdx:223]() |

#### Example: SDK Upload
```typescript
import Supermemory from 'supermemory';
import fs from 'fs';

await client.documents.uploadFile({
  file: fs.createReadStream('/path/to/file'),
  containerTag: "research"
});
```
[apps/docs/memory-api/sdks/typescript.mdx:64-71]()

Sources: [apps/docs/memory-api/ingesting.mdx:177-197](), [apps/docs/add-memories/overview.mdx:210-230](), [apps/docs/memory-api/sdks/typescript.mdx:55-82]()

---

## Listing & Tracking

### GET /v3/documents/processing
Monitors all documents currently being processed across an account [apps/docs/memory-api/track-progress.mdx:30]().

### GET /v3/documents/{id}
Retrieves the status and content of a specific document [apps/docs/memory-api/track-progress.mdx:103]().

### Listing Documents
While not explicitly detailed as a single `list` endpoint in the docs provided, the SDK supports `client.documents.list()` to retrieve document records.

Sources: [apps/docs/memory-api/track-progress.mdx:26-103](), [apps/docs/memory-api/sdks/typescript.mdx:43-49]()

---

## Updating & Deleting

### PATCH /v3/documents/{id}
Updates existing document content or metadata [apps/docs/add-memories/overview.mdx:183]().
- **Content change**: Triggers full reprocessing (status becomes `queued`) [apps/docs/update-delete-memories/overview.mdx:13]().
- **Metadata-only change**: Document is updated in place with no reindexing [apps/docs/update-delete-memories/overview.mdx:14]().

### DELETE /v3/documents/{id}
Performs a permanent hard delete of a document by its ID [apps/docs/update-delete-memories/overview.mdx:167-169]().

### DELETE /v3/documents/bulk
Deletes multiple memories at once by providing an array of IDs (max 100 per request) [apps/docs/update-delete-memories/overview.mdx:206-208]().

Title: "Mutation Flow in Web Client"
```mermaid
graph LR
    subgraph "Web_App_(apps/web)"
        UI["Memories_Grid_UI"]
        Hook["useDeleteDocument_Hook"]
    end

    subgraph "API_Client"
        DeleteCall["DELETE /v3/documents/:id"]
    end

    UI -->|"user clicks delete"| Hook
    Hook -->|"optimistic update"| UI
    Hook -->|"API request"| DeleteCall
```

Sources: [apps/docs/update-delete-memories/overview.mdx:9-231](), [apps/docs/add-memories/overview.mdx:181-208]()

---

## Processing Statuses

When a document is created, it moves through a pipeline. Typical durations vary by content type [apps/docs/memory-api/track-progress.mdx:9-24]().

| Status | Description | Typical Duration |
|--------|-------------|------------------|
| `queued` | Waiting in the processing queue [apps/docs/memory-api/track-progress.mdx:163](). | < 5 seconds |
| `extracting` | OCR or transcription in progress [apps/docs/memory-api/track-progress.mdx:164](). | 5-30 seconds |
| `chunking` | Breaking content into searchable pieces [apps/docs/memory-api/track-progress.mdx:165](). | 5-15 seconds |
| `embedding` | Creating vector representations [apps/docs/memory-api/track-progress.mdx:166](). | 10-30 seconds |
| `indexing` | Adding to the search index [apps/docs/memory-api/track-progress.mdx:167](). | 5-10 seconds |
| `done` | Fully processed and searchable [apps/docs/memory-api/track-progress.mdx:168](). | - |
| `failed` | Processing encountered an error [apps/docs/memory-api/track-progress.mdx:169](). | - |

Sources: [apps/docs/memory-api/track-progress.mdx:159-170](), [apps/docs/memory-api/overview.mdx:88-97]()

---

# Page: Profile & Search Endpoints

# Profile & Search Endpoints

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [apps/docs/add-memories.mdx](apps/docs/add-memories.mdx)
- [apps/docs/analytics.mdx](apps/docs/analytics.mdx)
- [apps/docs/concepts/customization.mdx](apps/docs/concepts/customization.mdx)
- [apps/docs/images/memory-graph.png](apps/docs/images/memory-graph.png)
- [apps/docs/install.md](apps/docs/install.md)
- [apps/docs/list-memories/examples/monitoring.mdx](apps/docs/list-memories/examples/monitoring.mdx)
- [apps/docs/search/examples/memory-search.mdx](apps/docs/search/examples/memory-search.mdx)
- [apps/docs/search/overview.mdx](apps/docs/search/overview.mdx)
- [apps/docs/search/parameters.mdx](apps/docs/search/parameters.mdx)
- [apps/docs/search/response-schema.mdx](apps/docs/search/response-schema.mdx)
- [apps/docs/test.py](apps/docs/test.py)
- [apps/docs/test.ts](apps/docs/test.ts)
- [apps/docs/user-profiles.mdx](apps/docs/user-profiles.mdx)
- [apps/docs/user-profiles/api.mdx](apps/docs/user-profiles/api.mdx)
- [apps/docs/user-profiles/examples.mdx](apps/docs/user-profiles/examples.mdx)
- [apps/docs/vibe-coding.mdx](apps/docs/vibe-coding.mdx)
- [packages/docs-test/tests/integrations/ai-sdk.ts](packages/docs-test/tests/integrations/ai-sdk.ts)

</details>



This page documents the primary read endpoints of the Supermemory REST API: `POST /v4/profile` for fetching user profiles (with optional embedded search), and the search ecosystem comprising `POST /v3/search` (Document-centric) and `POST /v4/search` (Memory-centric). These endpoints require a `containerTag` to scope results to a specific user, project, or organization.

---

## Overview

Supermemory provides distinct endpoints optimized for different retrieval needs, ranging from low-latency conversational context to deep document RAG.

| Endpoint | Primary Use | Data Source | Key Features |
|---|---|---|---|
| `POST /v4/profile` | Personalized LLM Context | Profile Store + Memories | Static facts, Dynamic context, Optional search |
| `POST /v4/search` | Fast Conversational Search | Memories | Minimal latency, optimized for Chatbots |
| `POST /v3/search` | Advanced RAG | Documents | Full control, Reranking, Query rewriting |

Sources: [apps/docs/search/overview.mdx:48-62](), [apps/docs/install.md:220-231]()

---

## POST /v4/profile

### Purpose
Retrieves a synthesized user profile for a `containerTag`. Supermemory maintains two layers of context automatically:
- **`static`**: Long-term, stable facts (e.g., "User is a software engineer"). [apps/docs/user-profiles/api.mdx:59-59]()
- **`dynamic`**: Recently learned or frequently updated information (e.g., "User is working on Project Alpha"). [apps/docs/user-profiles/api.mdx:60-60]()

If a query `q` is provided, it executes a memory search in the same call, enabling a "one-shot" context injection for LLM system prompts. [apps/docs/user-profiles.mdx:79-82]()

### Request Structure
**`POST https://api.supermemory.ai/v4/profile`**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `containerTag` | `string` | Yes | The unique identifier for the user or project. |
| `q` | `string` | No | Optional search query to include relevant memories. |
| `threshold` | `float` | No | Minimum relevance score (0-1) for search results. |

Sources: [apps/docs/user-profiles/api.mdx:25-29](), [apps/docs/search/parameters.mdx:195-206]()

### Response Schema
The response contains the profile facts and query-specific search results if `q` was passed.
```json
{
  "profile": {
    "static": ["User is a software engineer"],
    "dynamic": ["User is debugging authentication issues"]
  },
  "searchResults": {
    "results": [
      { "memory": "Relevant memory found via q", "score": 0.85 }
    ],
    "total": 1,
    "timing": 45.2
  }
}
```
Sources: [apps/docs/user-profiles/api.mdx:33-53](), [apps/docs/user-profiles.mdx:249-261]()

---

## Search Endpoints

Supermemory distinguishes between **Documents** (raw ingested sources like PDFs, videos, URLs) and **Memories** (extracted facts inferred from documents). [apps/docs/search/overview.mdx:64-71]()

### 1. Memories Search (`POST /v4/search`)
Optimized for minimal latency in conversational AI. It searches through extracted facts and user preferences.

**Key Parameters:**
- `searchMode`: `"memories"` (default) or `"hybrid"` (falls back to document chunks if memory results are insufficient). [apps/docs/search/overview.mdx:197-206]()
- `rerank`: Boolean to enable secondary ranking to improve relevance. [apps/docs/search/parameters.mdx:67-76]()
- `rewriteQuery`: Boolean to expand query via LLM for better matching. [apps/docs/search/parameters.mdx:78-93]()

Sources: [apps/docs/search/overview.mdx:183-206](), [apps/docs/search/parameters.mdx:191-214]()

### 2. Document Search (`POST /v3/search`)
Designed for "literal" search through ingested files and text. This is the primary RAG (Retrieval-Augmented Generation) endpoint.

**Key Parameters:**
- `documentThreshold` / `chunkThreshold`: Granular sensitivity controls for filtering. [apps/docs/search/parameters.mdx:99-123]()
- `includeFullDocs`: Returns the entire document content. [apps/docs/search/parameters.mdx:150-163]()
- `includeSummary`: Returns AI-generated summaries. [apps/docs/search/parameters.mdx:165-174]()

Sources: [apps/docs/search/overview.mdx:73-85](), [apps/docs/search/parameters.mdx:95-174]()

---

## Data Flow & Implementation

### Search Dispatcher Logic
The system differentiates between searching raw source material (documents) and processed knowledge (memories).

**Diagram: Search Routing Logic**
```mermaid
flowchart TD
    A["API Request (POST /v3/search or /v4/search)"] --> B{"Endpoint Path?"}
    B -->|"/v4/search"| C["Memory-Centric Path (client.search.memories)"]
    B -->|"/v3/search"| D["Document-Centric Path (client.search.documents)"]
    
    C --> E{"searchMode?"}
    E -->|"memories"| F["Query MemoryStore (Extracted Facts)"]
    E -->|"hybrid"| G["Query MemoryStore + DocumentChunks"]
    
    G --> H["Merge & Deduplicate by Similarity Score"]
    H --> I["Return searchResults Structure"]
    F --> I
    
    D --> J["Query DocumentStore (RAG Chunks)"]
    J --> I
```
Sources: [apps/docs/search/overview.mdx:197-206](), [apps/docs/search/parameters.mdx:208-214](), [apps/docs/search/response-schema.mdx:165-178]()

### Profile Retrieval Architecture
The profile endpoint bridges the gap between long-term facts and immediate query context.

**Diagram: Context Retrieval Architecture**
```mermaid
flowchart LR
    subgraph "Consumer Application Space"
        SDK["Supermemory SDK Client"]
        TOOLS["@supermemory/tools (withSupermemory)"]
    end

    subgraph "Code Entity Space: Supermemory API"
        PE["POST /v4/profile Route"]
        SE["POST /v4/search Route"]
    end

    subgraph "Data Storage Space"
        PF["ProfileStore (Static & Dynamic Facts)"]
        MS["MemoryStore (Extracted Knowledge)"]
        DS["DocumentStore (Raw Source Chunks)"]
    end

    SDK -->|"client.profile()"| PE
    TOOLS -->|"withSupermemory Middleware"| PE
    PE --> PF
    PE -.->|"if q parameter provided"| MS
    SE --> MS
    SE -.->|"if searchMode='hybrid'"| DS
```
Sources: [apps/docs/user-profiles/api.mdx:10-30](), [apps/docs/install.md:111-122](), [apps/docs/user-profiles.mdx:225-243]()

---

## Integration Patterns

### Personalized Prompt Injection
The most common use case is injecting profile data into an LLM's system prompt to provide persona-aware responses.

```typescript
// Fetching profile to build system prompt
const { profile } = await client.profile({ containerTag: userId });

const systemPrompt = `You are assisting a user.
ABOUT THE USER:
${profile.static.join('\n')}

CURRENT CONTEXT:
${profile.dynamic.join('\n')}`;
```
Sources: [apps/docs/user-profiles.mdx:131-152](), [apps/docs/user-profiles/examples.mdx:28-37]()

### Metadata Filtering
Both search and profile endpoints support advanced metadata filtering using a JSON logic structure.

```json
{
  "AND": [
    { "key": "category", "value": "ai", "negate": false },
    { "key": "priority", "value": "high", "negate": false }
  ]
}
```
Sources: [apps/docs/search/parameters.mdx:48-65](), [apps/docs/search/parameters.mdx:176-189]()

---

## Response Structure & Filtering

### Search Results Structure
Search results typically include metadata and scores. In hybrid mode, results are distinguished by their content keys.

- **Memories**: Contain a `memory` string field. [apps/docs/search/overview.mdx:201-201]()
- **Chunks**: Contain a `chunk` string field (in hybrid mode) or are nested within document objects (in v3 search). [apps/docs/search/overview.mdx:202-202]()

### Error Handling
Common status codes for these endpoints include:
- `400`: Missing `containerTag` or invalid `threshold`. [apps/docs/user-profiles/api.mdx:215-215]()
- `401`: Invalid or missing `Authorization` Bearer token. [apps/docs/user-profiles/api.mdx:216-216]()
- `404`: Container not found. [apps/docs/user-profiles/api.mdx:217-217]()

Sources: [apps/docs/user-profiles/api.mdx:211-218]()

---

# Page: Connectors API

# Connectors API

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [apps/docs/connectors/github.mdx](apps/docs/connectors/github.mdx)
- [apps/docs/connectors/gmail.mdx](apps/docs/connectors/gmail.mdx)
- [apps/docs/connectors/granola.mdx](apps/docs/connectors/granola.mdx)
- [apps/docs/connectors/notion.mdx](apps/docs/connectors/notion.mdx)
- [apps/docs/connectors/overview.mdx](apps/docs/connectors/overview.mdx)
- [apps/docs/connectors/s3.mdx](apps/docs/connectors/s3.mdx)
- [apps/docs/connectors/troubleshooting.mdx](apps/docs/connectors/troubleshooting.mdx)
- [apps/docs/connectors/web-crawler.mdx](apps/docs/connectors/web-crawler.mdx)
- [apps/docs/images/granola.svg](apps/docs/images/granola.svg)
- [apps/docs/memory-api/connectors/creating-connection.mdx](apps/docs/memory-api/connectors/creating-connection.mdx)
- [apps/docs/memory-api/connectors/managing-resources.mdx](apps/docs/memory-api/connectors/managing-resources.mdx)
- [apps/docs/memory-api/connectors/overview.mdx](apps/docs/memory-api/connectors/overview.mdx)
- [apps/web/components/remove-connection-dialog.tsx](apps/web/components/remove-connection-dialog.tsx)

</details>



This page documents the REST endpoints that make up the Connections API under the `/v3/connections` path. It covers creating connections to external providers, listing and deleting them, triggering manual syncs, and listing or configuring provider-specific resources (e.g., GitHub repositories).

For a conceptual explanation of what connectors are, which providers are supported, and how the sync lifecycle works, see the Connector Overview ([7]()), ([7.1]()). For provider-specific OAuth flows, setup, and behavior, see the individual connector pages ([7.2](), [7.3](), [7.4](), [7.5]()). For API authentication and search integration, see ([6.2]()) and ([6.5]()).

---

## Endpoint Map

The following diagram shows all connection-related endpoints grouped by operation type, mapping the high-level actions to the API routes.

**Connections API Endpoint Topology**

```mermaid
graph LR
  subgraph "Create [@POST/v3/connections/:provider]"
    C1["POST /v3/connections/{provider}"]
  end
  subgraph "Read [@POST/v3/connections/list]"
    R1["POST /v3/connections/list"]
    R2["GET /v3/connections/{connectionId}/resources"]
    R3["POST /v3/connections/{provider}/connection"]
    R4["POST /v3/connections/{provider}/documents"]
  end
  subgraph "Delete [@DELETE/v3/connections/:id]"
    D1["DELETE /v3/connections/{connectionId}"]
    D2["POST /v3/connections/delete-by-provider"]
  end
  subgraph "Sync [@POST/v3/connections/:provider/import]"
    S1["POST /v3/connections/{provider}/import"]
    S2["POST /v3/connections/{provider}/sync"]
  end
  subgraph "Configure [@POST/v3/connections/:id/configure]"
    CF1["POST /v3/connections/{connectionId}/configure"]
  end
```

Sources: [apps/docs/memory-api/connectors/creating-connection.mdx:6-7](), [apps/docs/memory-api/connectors/managing-resources.mdx:16-106](), [apps/docs/connectors/overview.mdx:106-191](), [apps/docs/connectors/notion.mdx:122-141]()

---

## Supported Providers

The `{provider}` path parameter in these endpoints accepts the following values. Note that some providers like `gmail`, `github`, `granola`, and `s3` require specific billing plans.

| Provider value | Auth type | Real-time sync | Plan Required |
|---|---|---|---|
| `notion` | OAuth | Webhooks | Any |
| `google-drive` | OAuth | Webhooks | Any |
| `gmail` | OAuth | Pub/Sub (Real-time) | Scale/Enterprise |
| `onedrive` | OAuth | Webhooks (Scheduled) | Any |
| `github` | OAuth | Webhooks | Scale/Enterprise |
| `s3` | API Keys | Scheduled | Scale |
| `granola` | API Keys | API-based | Pro/Max |
| `web-crawler` | URL-based | Scheduled | Any |

Sources: [apps/docs/connectors/overview.mdx:12-54](), [apps/docs/connectors/gmail.mdx:9-11](), [apps/docs/connectors/github.mdx:9-11](), [apps/docs/connectors/s3.mdx:9-11](), [apps/docs/connectors/granola.mdx:9-11](), [apps/web/components/remove-connection-dialog.tsx:17-25]()

---

## Create Connection

```
POST /v3/connections/{provider}
```

Initiates a connection. For OAuth providers (Notion, Google Drive, OneDrive, Gmail, GitHub), the response includes an `authLink`. For credential-based providers (`s3`, `granola`), credentials are passed in the `metadata` object.

### Request Body (General)

| Field | Type | Required | Description |
|---|---|---|---|
| `redirectUrl` | string | OAuth only | URL for OAuth callback |
| `containerTags` | string[] | No | Scoping tags (e.g. `["user-123"]`) |
| `metadata` | object | No | Provider-specific config (e.g. `startUrl` for crawler) |
| `documentLimit` | number | No | Max documents to sync. Range: `1-10000` |

### Provider-Specific Metadata

- **S3**: Requires `accessKeyId`, `secretAccessKey`, `bucket`, and `region` in the `metadata` object [apps/docs/connectors/s3.mdx:76-81]().
- **Granola**: Requires `apiKey` in the `metadata` object [apps/docs/connectors/granola.mdx:95]().
- **Web Crawler**: Requires `startUrl` in the `metadata` object [apps/docs/memory-api/connectors/creating-connection.mdx:73]().

Sources: [apps/docs/memory-api/connectors/creating-connection.mdx:64-77](), [apps/docs/connectors/overview.mdx:106-114](), [apps/docs/connectors/s3.mdx:56-68]()

---

## List Connections

```
POST /v3/connections/list
```

Returns connections associated with the organization or specific tags.

### Request Body

| Field | Type | Required | Description |
|---|---|---|---|
| `containerTags` | string[] | No | Filter by tags |
| `provider` | string | No | Filter by specific provider |

### Response

Array of connection objects containing:
- `id`: Connection identifier
- `provider`: Provider name
- `email`: Connected account email (if applicable)
- `createdAt`: ISO timestamp
- `documentLimit`: Current sync limit

Sources: [apps/docs/connectors/overview.mdx:188-191](), [apps/docs/connectors/gmail.mdx:129-135](), [apps/docs/connectors/notion.mdx:122-135]()

---

## Delete Connection

### By ID
```
DELETE /v3/connections/{connectionId}?deleteDocuments=true
```

Deleting a connection removes OAuth authorization and stops syncing. By default, it also removes all synced documents.

| Query Parameter | Type | Default | Description |
|---|---|---|---|
| `deleteDocuments` | boolean | `true` | Whether to permanently delete synced memories |

In the web UI, this is handled by the `RemoveConnectionDialog` component [apps/web/components/remove-connection-dialog.tsx:37-45]().

Sources: [apps/docs/connectors/s3.mdx:190-198](), [apps/docs/connectors/granola.mdx:158-166](), [apps/web/components/remove-connection-dialog.tsx:148-162]()

---

## Resource Management (GitHub)

Providers that support resource management (currently GitHub) require selecting which resources (repositories) to sync.

### 1. Get Resources
```
GET /v3/connections/{connectionId}/resources?page=1&per_page=30
```

Returns available resources for the connection using stored credentials. This calls the provider's `fetchResources()` method [apps/docs/memory-api/connectors/managing-resources.mdx:101]().

### 2. Configure Connection
```
POST /v3/connections/{connectionId}/configure
```

**Request Body:**
```json
{
  "resources": [
    {
      "id": 123456789,
      "name": "org/repo",
      "defaultBranch": "main"
    }
  ]
}
```

Sources: [apps/docs/memory-api/connectors/managing-resources.mdx:16-106](), [apps/docs/memory-api/connectors/managing-resources.mdx:182-200](), [apps/docs/connectors/github.mdx:169-190]()

---

## Data Flow: Connection Lifecycle

The following diagram maps the relationship between the API endpoints and the internal state of a connection.

**Code Entity & API Flow Map**

```mermaid
sequenceDiagram
  participant Client as "SDK / Web UI"
  participant API as "Supermemory API (/v3/connections)"
  participant Provider as "External Provider (GitHub/Notion)"
  participant DB as "Database (Drizzle/Cloudflare D1)"

  Client->>API: POST /{provider} (Create Connection)
  API-->>Client: Return {authLink, id}
  Client->>Provider: User grants OAuth permissions
  Provider-->>API: Redirect to callbackUrl
  API->>DB: Store credentials & metadata
  
  Note over Client, DB: For Resource-based Providers (GitHub)
  
  Client->>API: GET /{id}/resources (fetchResources)
  API->>Provider: Request resource list (e.g. repos)
  API-->>Client: List of available resources
  Client->>API: POST /{id}/configure (configureConnection)
  API->>DB: Save selected resource IDs
  API->>Provider: Register Webhooks (if supported)
  Note right of DB: Initial sync triggered automatically
```

Sources: [apps/docs/connectors/overview.mdx:208-214](), [apps/docs/memory-api/connectors/managing-resources.mdx:240-245](), [apps/docs/connectors/github.mdx:15-132]()

---

## Troubleshooting & Health Checks

Users can verify connection health by checking for failed document imports.

```typescript
// Example: Checking for failed documents in a connection
const documents = await client.connections.listDocuments('notion', {
  containerTags: ['user-123']
});

const failed = documents.filter(doc => doc.status === 'failed');
```

Common error codes:
- `400`: Connection missing refresh token [apps/docs/memory-api/connectors/managing-resources.mdx:95]().
- `401`: Unauthorized API key [apps/docs/memory-api/connectors/managing-resources.mdx:96]().
- `404`: Connection not found [apps/docs/memory-api/connectors/managing-resources.mdx:97]().
- `501`: Provider does not support resource fetching/configuration [apps/docs/memory-api/connectors/managing-resources.mdx:98]().

Sources: [apps/docs/connectors/troubleshooting.mdx:16-34](), [apps/docs/memory-api/connectors/managing-resources.mdx:93-102](), [apps/docs/connectors/granola.mdx:208-214]()

---

# Page: Projects & Container Tags

# Projects & Container Tags

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [apps/docs/concepts/container-tags.mdx](apps/docs/concepts/container-tags.mdx)
- [apps/web/components/dashboard-view.tsx](apps/web/components/dashboard-view.tsx)
- [apps/web/components/highlights-card.tsx](apps/web/components/highlights-card.tsx)
- [apps/web/components/select-spaces-modal.tsx](apps/web/components/select-spaces-modal.tsx)
- [apps/web/components/space-selector.tsx](apps/web/components/space-selector.tsx)
- [apps/web/globals.css](apps/web/globals.css)
- [apps/web/hooks/use-personalization.ts](apps/web/hooks/use-personalization.ts)
- [apps/web/lib/chat-space-label.ts](apps/web/lib/chat-space-label.ts)
- [apps/web/lib/ingest-auto-space.ts](apps/web/lib/ingest-auto-space.ts)

</details>



This page documents the projects and container tags system in Supermemory, which provides data isolation and multi-tenancy capabilities. Container tags are the low-level scoping mechanism used throughout the API, while Projects and Spaces provide the user-facing abstraction for organizing memories, documents, and connections.

---

## Container Tags Concept

A **container tag** is the primary isolation boundary in Supermemory. It acts as a namespace that groups and partitions memories by user, project, or any logical scope [apps/docs/concepts/container-tags.mdx:4-10]().

**Key characteristics:**
- **Namespace Isolation**: Every memory tagged with a specific string (e.g., `user_alex`) lives in an isolated space. Search and retrieval operations never leak across these boundaries [apps/docs/concepts/container-tags.mdx:10-18]().
- **Automatic Provisioning**: Supermemory automatically creates a space for a tag upon the first write request. No pre-provisioning is required [apps/docs/concepts/container-tags.mdx:25-32]().
- **Physical Isolation**: Under the hood, each container tag is hashed into a dedicated vector namespace. There is no shared index to filter through, ensuring strict isolation [apps/docs/concepts/container-tags.mdx:41-42]().
- **Naming Rules**: Tags must be 100 characters or less and match the pattern `^[a-zA-Z0-9_:-]+$`. The colon (`:`) is allowed to support hierarchical tagging (e.g., `org:acme:user:john`) [apps/docs/concepts/container-tags.mdx:51-71]().

**Container Tag Implementation Flow**

```mermaid
graph TB
    subgraph "API Request"
        Add["client.add({ containerTag: 'project_1' })"]
        Search["client.search({ containerTag: 'project_1' })"]
    end
    
    subgraph "Logic Layer"
        Validate["Validate Naming Rules<br/>(^[a-zA-Z0-9_:-]+$)"]
        Hash["Hash Tag to Namespace ID"]
    end
    
    subgraph "Storage Layer"
        VectorDB["Vector Store Namespace<br/>(Isolated Embeddings)"]
        RelDB["Relational Store<br/>(Metadata Scoped to Tag)"]
    end
    
    Add --> Validate
    Search --> Validate
    Validate --> Hash
    Hash --> VectorDB
    Hash --> RelDB
```

**Sources:** [apps/docs/concepts/container-tags.mdx:8-18](), [apps/docs/concepts/container-tags.mdx:25-32](), [apps/docs/concepts/container-tags.mdx:41-42](), [apps/docs/concepts/container-tags.mdx:51-71]()

---

## Projects & Spaces in UI

In the Supermemory web application, container tags are presented as **Spaces** or **Projects**. The `SpaceSelector` component allows users to switch between different `containerTags`, including the default user space and auto-provisioned plugin spaces [apps/web/components/space-selector.tsx:109-120]().

### UI Abstractions
- **My Space**: The default container for a user, represented by `DEFAULT_PROJECT_ID` (usually `sm_project_default`) [apps/web/components/select-spaces-modal.tsx:135-144](), [apps/web/lib/chat-space-label.ts:11-13]().
- **Plugin Spaces**: Containers auto-created by integrations (e.g., Twitter, GitHub). These are detected via `detectPluginSpace` and often use specific naming conventions [apps/web/components/select-spaces-modal.tsx:124-130](), [apps/web/lib/ingest-auto-space.ts:11-16]().
- **Nova Chats**: A special space for conversation history, typically scoped to the user's ID [apps/web/lib/ingest-auto-space.ts:29-34]().

### Project Data Structure

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique identifier for the project record. |
| `name` | string | Human-friendly display name (e.g., "Space project_123" for auto-provisioned ones) [apps/web/lib/ingest-auto-space.ts:11-16](). |
| `containerTag` | string | The underlying identifier used for API scoping [apps/docs/concepts/container-tags.mdx:137-137](). |
| `entityContext` | string | A custom context prompt applied during processing to steer extraction per project [apps/docs/concepts/container-tags.mdx:138-143](). |

**Sources:** [apps/web/components/space-selector.tsx:148-155](), [apps/web/lib/ingest-auto-space.ts:4-16](), [apps/web/lib/chat-space-label.ts:5-16](), [apps/docs/concepts/container-tags.mdx:131-143]()

---

## Data Isolation Architecture

All data operations respect container tag boundaries. The system provides strict isolation at the data layer, ensuring that queries only return results from the specified `containerTag`.

**Implementation Scoping**

```mermaid
graph LR
    subgraph "Client"
        SDK["SDK Client"]
    end
    
    subgraph "Server (Cloudflare Workers / Next.js)"
        Auth["Auth Middleware<br/>(Verify Scoped Key)"]
        Router["API Router"]
    end
    
    subgraph "Data Entities"
        Docs["Documents / Memories"]
        Profiles["User Profiles"]
        Conns["Connections"]
    end
    
    SDK -->|containerTag| Auth
    Auth -->|Validates Scope| Router
    Router -->|Filter by Tag| Docs
    Router -->|Filter by Tag| Profiles
    Router -->|Filter by Tag| Conns
```

### Scoping Across API Endpoints

| Endpoint | Parameter | Behavior |
|----------|-----------|----------|
| `POST /v3/add` | `containerTag` | Writes memory into the tag's isolated container [apps/docs/concepts/container-tags.mdx:96-96](). |
| `POST /v3/search` | `containerTag` | Restricts retrieval to the given tag's namespace [apps/docs/concepts/container-tags.mdx:97-97](). |
| `POST /v4/profile` | `containerTag` | Scopes the AI profile generation to the specific project context [apps/docs/concepts/container-tags.mdx:97-98](). |
| `documents/list` | `containerTags` | Returns documents belonging to the specified tags [apps/web/components/space-selector.tsx:159-167](). |

**Sources:** [apps/docs/concepts/container-tags.mdx:90-110](), [apps/web/components/space-selector.tsx:156-177](), [apps/docs/concepts/container-tags.mdx:131-143]()

---

## Scoped API Keys

To support fine-grained access control, Supermemory allows the creation of API keys restricted to specific container tags. This is an authorization boundary enforced at the data layer [apps/docs/concepts/container-tags.mdx:114-116]().

- **Enforcement**: Requesting a tag outside the allowed set returns a `403 Forbidden` [apps/docs/concepts/container-tags.mdx:123-123]().
- **Automatic Scoping**: If a restricted caller provides no tag, the request is automatically scoped to their allowed tags [apps/docs/concepts/container-tags.mdx:125-125]().
- **Write Protection**: Write operations to a tag where the key only has read permissions are rejected [apps/docs/concepts/container-tags.mdx:124-124]().

**Sources:** [apps/docs/concepts/container-tags.mdx:114-127]()

---

## Data Model Summary

**Entity Relationship Diagram**

```mermaid
erDiagram
    "Organization/User" ||--o{ "ContainerTag" : "owns"
    "ContainerTag" ||--o{ "Document" : "contains"
    "ContainerTag" ||--o{ "Memory" : "contains"
    "ContainerTag" ||--|| "UserProfile" : "associated_with"
    "ContainerTag" ||--o{ "ScopedKey" : "limits_access"
    
    "ContainerTag" {
        string identifier "e.g. user_123"
        string name "Display Name"
        string entityContext "Custom steering prompt"
    }
    
    "Document" {
        string content
        string sourceUrl
        string[] containerTags
    }
    
    "ScopedKey" {
        string keyHash
        string[] allowedTags
        string permissions "read | write"
    }
```

**Sources:** [apps/docs/concepts/container-tags.mdx:114-143](), [apps/docs/concepts/container-tags.mdx:8-10](), [apps/web/components/space-selector.tsx:159-167]()

---

# Page: Authentication & Scoped Keys

# Authentication & Scoped Keys

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [apps/docs/authentication.mdx](apps/docs/authentication.mdx)
- [apps/web/app/(app)/connect/page.tsx](apps/web/app/(app)/connect/page.tsx)
- [apps/web/app/(auth)/login/new/page.tsx](apps/web/app/(auth)/login/new/page.tsx)
- [apps/web/app/(auth)/login/page.tsx](apps/web/app/(auth)/login/page.tsx)
- [apps/web/app/oauth/consent/ConsentCard.tsx](apps/web/app/oauth/consent/ConsentCard.tsx)
- [apps/web/app/oauth/consent/page.tsx](apps/web/app/oauth/consent/page.tsx)
- [apps/web/lib/oauth-plugins.ts](apps/web/lib/oauth-plugins.ts)

</details>



This page documents the authentication mechanisms for the Supermemory API, including API key types, scoped keys for container-level access control, the Model Context Protocol (MCP) OAuth flow, and how Authorization headers are utilized across the platform.

---

## API Key Authentication

All Supermemory API requests require authentication using a Bearer token. Primary API keys are obtained from the [Developer Platform](https://console.supermemory.ai) and must be included in the `Authorization` header [apps/docs/authentication.mdx:7-13]().

### Usage

Include the API key in the `Authorization` header with the `Bearer` scheme:

```bash
curl https://api.supermemory.ai/v3/search \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"q": "hello"}'
```

**Sources:** [apps/docs/authentication.mdx:15-22]()

---

## Scoped API Keys

Scoped keys provide fine-grained access control by restricting a token to a single `containerTag`. These keys are limited to document and memory operations within that specific container, preventing access to the rest of the organization's data [apps/docs/authentication.mdx:58-61]().

### Allowed Endpoints
Scoped keys are restricted to a specific subset of the API [apps/docs/authentication.mdx:63-63]():
*   `/v3/documents`
*   `/v3/memories` / `/v4/memories`
*   `/v3/search` / `/v4/search`
*   `/v4/profile`

### Lifecycle Management

| Action | Method | Endpoint | Description |
| :--- | :--- | :--- | :--- |
| **Create** | `POST` | `/v3/auth/scoped-key` | Generates a new key for a `containerTag` [apps/docs/authentication.mdx:68-77](). |
| **Revoke** | `DELETE` | `/v3/auth/scoped-key/{id}` | Immediately disables the key; does not delete data [apps/docs/authentication.mdx:109-112](). |

**Creation Parameters:**
*   `containerTag` (Required): Alphanumeric identifier for the scope [apps/docs/authentication.mdx:83-83]().
*   `expiresInDays` (Optional): Validity period between 1–365 days [apps/docs/authentication.mdx:85-85]().
*   `rateLimitMax` (Optional): Max requests per window (Default: 500) [apps/docs/authentication.mdx:86-86]().

**Sources:** [apps/docs/authentication.mdx:58-118]()

---

## MCP OAuth & Consent Flow

Supermemory implements an OAuth2-based flow for Model Context Protocol (MCP) clients and external plugins like Claude Code. This allows users to grant specific permissions (read/write) and scopes (full or container-restricted) to third-party applications [apps/web/app/oauth/consent/page.tsx:81-108]().

### Authorization Resume
When an MCP client initiates an OAuth flow, the `LoginPage` detects the context using `isMcpOAuthAuthorizeContext` [apps/web/app/(auth)/login/page.tsx:24-26](). After the user authenticates via Next.js Auth, they are redirected to the resume URL [apps/web/app/(auth)/login/page.tsx:49-50](), which leads to the consent screen.

### Consent & Scoping
The `OAuthConsentContent` component allows users to:
1.  **Select Organization**: Switch active organizations via `authClient.organization.setActive` [apps/web/app/oauth/consent/page.tsx:43-57]().
2.  **Pick Spaces**: Restrict the plugin to specific `containerTags` using the `SpacesPicker` [apps/web/app/oauth/consent/ConsentCard.tsx:122-134]().
3.  **Set Expiry**: Choose how long the grant remains valid (e.g., 30 days, 1 year, or never) [apps/web/app/oauth/consent/ConsentCard.tsx:53-60]().

### Grant Revocation
Users can manage and revoke these permissions at any time via the `/connect` page, which calls `DELETE /v3/oauth/grants/{clientId}` [apps/web/app/(app)/connect/page.tsx:97-115]().

```mermaid
sequenceDiagram
    participant Tool as "MCP Client (e.g. Claude Code)"
    participant Web as "Web App (apps/web)"
    participant API as "Backend API"

    Tool->>Web: Redirect to /login (with OAuth params)
    Web->>Web: User Authenticates
    Web->>API: POST /v3/mcp/connect-scope (Permissions + Tags)
    API-->>Web: 200 OK
    Web->>API: POST /api/auth/oauth2/consent (accept: true)
    API-->>Web: Return redirect_uri with code
    Web->>Tool: Redirect back to local loopback
```

**Diagram: MCP OAuth Authorization Flow**
Bridges the interaction between the `LoginPage` [apps/web/app/(auth)/login/page.tsx:114](), the `OAuthConsentContent` [apps/web/app/oauth/consent/page.tsx:17](), and the backend OAuth handlers.

**Sources:** [apps/web/app/(auth)/login/page.tsx:24-50](), [apps/web/app/oauth/consent/page.tsx:81-187](), [apps/web/app/(app)/connect/page.tsx:97-115]()

---

## Authentication Data Flow

The following diagram maps how different authentication entities in the code interact during a request.

```mermaid
graph TD
    subgraph "Request Layer"
        Req["Incoming Request"]
        Header["Authorization: Bearer <key>"]
    end

    subgraph "Logic Layer (Backend)"
        AuthHandler["Auth Middleware / v3/auth"]
        ScopedCheck["Scoped Key Validator"]
        OAuthCheck["OAuth Grant Validator"]
    end

    subgraph "Entity Space (Code)"
        DB_Keys["D1: API Keys Table"]
        DB_Grants["D1: OAuth Grants Table"]
        Session["Better-Auth Session"]
    end

    Req --> Header
    Header --> AuthHandler
    AuthHandler --> ScopedCheck
    AuthHandler --> OAuthCheck
    
    ScopedCheck -- "Lookup Hash" --> DB_Keys
    OAuthCheck -- "Verify ClientID" --> DB_Grants
    AuthHandler -- "Internal Web Calls" --> Session
```

**Diagram: Authentication Verification Architecture**
This diagram shows how the system differentiates between raw API keys (verified via hash lookup in D1) and web-based session authentication used for the consent flow [apps/web/app/oauth/consent/page.tsx:122-130]().

**Sources:** [apps/docs/authentication.mdx:93-99](), [apps/web/app/oauth/consent/page.tsx:96-108](), [apps/web/app/(app)/connect/page.tsx:77-82]()

---

## Summary of Key Types

| Key Type | Use Case | Prefix | Revocation |
| :--- | :--- | :--- | :--- |
| **Standard API Key** | Full programmatic access to organization resources. | `sm_` | Developer Console [apps/docs/authentication.mdx:7-11]() |
| **Scoped API Key** | Third-party integrations limited to one `containerTag`. | `sm_` | `DELETE /v3/auth/scoped-key/{id}` [apps/docs/authentication.mdx:104-106]() |
| **OAuth Grant** | Browser-based authorization for MCP tools/plugins. | N/A | `/connect` UI or `DELETE /v3/oauth/grants/{id}` [apps/web/app/(app)/connect/page.tsx:97-103]() |

**Sources:** [apps/docs/authentication.mdx:58-112](), [apps/web/app/(app)/connect/page.tsx:13-23]()

---

# Page: Connectors System

# Connectors System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [apps/docs/connectors/github.mdx](apps/docs/connectors/github.mdx)
- [apps/docs/connectors/gmail.mdx](apps/docs/connectors/gmail.mdx)
- [apps/docs/connectors/granola.mdx](apps/docs/connectors/granola.mdx)
- [apps/docs/connectors/overview.mdx](apps/docs/connectors/overview.mdx)
- [apps/docs/connectors/s3.mdx](apps/docs/connectors/s3.mdx)
- [apps/docs/connectors/troubleshooting.mdx](apps/docs/connectors/troubleshooting.mdx)
- [apps/docs/images/granola.svg](apps/docs/images/granola.svg)
- [apps/docs/memory-api/connectors/managing-resources.mdx](apps/docs/memory-api/connectors/managing-resources.mdx)
- [apps/web/app/auth/connect/page.tsx](apps/web/app/auth/connect/page.tsx)
- [apps/web/components/add-document/connections.tsx](apps/web/components/add-document/connections.tsx)
- [apps/web/components/integrations-view.tsx](apps/web/components/integrations-view.tsx)
- [apps/web/components/integrations/plugins-detail.tsx](apps/web/components/integrations/plugins-detail.tsx)
- [apps/web/components/remove-connection-dialog.tsx](apps/web/components/remove-connection-dialog.tsx)
- [apps/web/hooks/use-token-usage.ts](apps/web/hooks/use-token-usage.ts)
- [apps/web/lib/billing-utils.ts](apps/web/lib/billing-utils.ts)
- [packages/lib/queries.ts](packages/lib/queries.ts)

</details>



The Connectors System allows Supermemory to pull content from external platforms and sync it into a user's knowledge base. This page covers the purpose of connectors, which providers are supported, the core sync lifecycle, and the document processing pipeline. For detailed per-provider setup, see pages [Connector Overview](#7.1) through [Web Crawler](#7.5). For the REST API endpoints that back these operations, see [Connectors API](#6.3).

---

## What Connectors Do

A connector is a persistent, authenticated link between a Supermemory container and an external data source. Once established, the connector continuously keeps that source's content synchronized as memories in Supermemory's index, making it searchable via the standard search and RAG APIs.

Connectors are scoped to `containerTags`, which map to users, projects, or tenants in your application. A single organization API key can manage connections for many containers. 

Sources: [apps/docs/connectors/overview.mdx:7-9](), [apps/docs/connectors/overview.mdx:70-75]()

---

## Supported Providers

| Provider | Auth Method | Real-time Sync | Scheduled Sync | Manual Sync | Plan Required |
|----------|-------------|----------------|----------------|-------------|---------------|
| **Google Drive** | OAuth | ✅ Webhooks | ✅ Every 4 hours | ✅ | — |
| **Gmail** | OAuth | ✅ Pub/Sub | ✅ Every 4 hours | ✅ | Scale / Enterprise |
| **Notion** | OAuth | ✅ Webhooks | ✅ Every 4 hours | ✅ | — |
| **OneDrive** | OAuth | ✅ Webhooks | ✅ Every 4 hours | ✅ | — |
| **GitHub** | OAuth | ✅ Webhooks | ✅ Every 4 hours | ✅ | Scale / Enterprise |
| **Granola** | API Key | ❌ | ✅ Incremental | ✅ | Pro |
| **Web Crawler** | None | ❌ | ✅ Recrawl | ✅ | Scale / Enterprise |
| **S3** | Access Keys | ❌ | ✅ Every 4 hours | ✅ | Scale / Enterprise |

Sources: [apps/docs/connectors/overview.mdx:12-54](), [apps/docs/connectors/overview.mdx:230-238](), [apps/docs/connectors/s3.mdx:9-11](), [apps/docs/connectors/granola.mdx:9-11](), [apps/web/components/add-document/connections.tsx:83-90]()

---

## Connection Lifecycle

There are distinct creation flows depending on whether the provider requires OAuth.

### OAuth Provider Flow

**OAuth Providers:** `google-drive`, `gmail`, `notion`, `onedrive`, `github`

**OAuth Sync Lifecycle**
```mermaid
sequenceDiagram
    participant "App" as "Client Application"
    participant "API" as "POST /v3/connections/:provider"
    participant "OAuth" as "External Provider OAuth"
    participant "Sync" as "Sync Engine"

    App->>API: "POST with redirectUrl & containerTags"
    Note right of API: "Uses @post/connections/:provider"
    API-->>App: "Returns { authLink, id, expiresIn }"
    App->>OAuth: "Redirect user to authLink"
    OAuth-->>App: "Redirect to redirectUrl with code"
    Note over API, Sync: "Connection status moves to 'active'"
    API->>Sync: "Initial sync triggered"
```

Sources: [apps/docs/connectors/overview.mdx:208-213](), [apps/docs/connectors/overview.mdx:106-121]()

### Key-Based Provider Flow

**Providers:** `s3`, `granola`, `web-crawler`

**Non-OAuth Creation Flow**
```mermaid
sequenceDiagram
    participant "App" as "Client Application"
    participant "API" as "POST /v3/connections/:provider"
    participant "Sync" as "Sync Engine"

    App->>API: "POST with metadata { apiKey } or { accessKeyId }"
    API-->>App: "Returns { id, authLink: null }"
    API->>Sync: "Initial sync/crawl begins immediately"
```

Sources: [apps/docs/connectors/granola.mdx:41-50](), [apps/docs/connectors/s3.mdx:24-32]()

---

## Sync Monitoring & Health

Supermemory provides detailed visibility into the sync status and health of every connection. This is managed via hooks like `useConnectionHealth` and displayed using `SyncStatusBadge`.

**Connection Health and Sync UI**
```mermaid
flowchart TD
    subgraph "Code Entity Space"
        H1["useConnectionHealth(connectionId)"]
        H2["useTriggerSync()"]
        H3["ConnectionResponseSchema"]
    end

    subgraph "UI Components"
        U1["ConnectionRow"]
        U2["SyncStatusBadge"]
        U3["SyncHistoryPanel"]
    end

    H1 --> U1
    H2 --> U1
    U1 --> U2
    U1 --> U3
    U2 --- H3
```

- **Sync Statuses:** Connections track `syncInProgress`, `lastSyncedAt`, and `documentCount` within their metadata. [apps/web/components/add-document/connections.tsx:93-101]()
- **Health Checks:** The `useConnectionHealth` hook identifies if a connection `needsReauth`. [apps/web/components/add-document/connections.tsx:124-129]()
- **Manual Triggers:** Users can manually trigger a sync using `onTriggerSync` which calls the `useTriggerSync` hook. [apps/web/components/add-document/connections.tsx:202-217]()

Sources: [apps/web/components/add-document/connections.tsx:93-101](), [apps/web/components/add-document/connections.tsx:124-129](), [apps/web/components/settings/sync-status-badge.tsx:5-14]()

---

## Document Processing Pipeline

After a connector is triggered, each document goes through this pipeline:

**Ingestion Pipeline**
```mermaid
flowchart TD
    A["External Source\n(S3 / Drive / GitHub)"] --> B["Trigger\n(Webhook / Schedule / Manual)"]
    B --> C["Content Extraction\n(Markdown / Text Conversion)"]
    C --> D["Chunking & Embedding"]
    D --> E["Index in Supermemory\n(Vector Store)"]
    E --> F["Searchable Memory"]
    
    subgraph "Code Entity Space"
        S1["CONNECTORS"]
        S2["getConnectionMeta"]
    end
    B --- S2
    A --- S1
```

Sources: [apps/docs/connectors/overview.mdx:217-226](), [apps/web/components/add-document/connections.tsx:57-90]()

---

## Connection Management

### Deleting Connections
When deleting a connection via `RemoveConnectionDialog`, users can choose to:
1. **Remove connection only:** Disconnect the integration but keep all imported memories.
2. **Remove connection and memories:** Permanently delete all memories imported from this connection by setting `alsoDelete` to true.

Sources: [apps/web/components/remove-connection-dialog.tsx:37-46](), [apps/docs/connectors/s3.mdx:196-198]()

### Resource Selection (GitHub)
GitHub requires an explicit resource-selection step. After OAuth completes, the user must select which repositories to sync using the resource management endpoints.
- `client.connections.github.listRepositories(connectionId)`
- `client.connections.github.configure(connectionId, { repositories })`

Sources: [apps/docs/connectors/github.mdx:105-130]()

---

## Sub-pages

| Page | Content |
|------|---------|
| [Connector Overview](#7.1) | Creation flow, OAuth vs non-OAuth, and listing/deleting connections. |
| [GitHub Connector](#7.2) | Repository selection, webhook setup, and incremental syncing. |
| [Gmail Connector](#7.3) | OAuth flow, Pub/Sub webhooks, and email thread processing. |
| [Google Drive, Notion & OneDrive](#7.4) | Supported document types and provider-specific configurations. |
| [Web Crawler](#7.5) | Creating crawl jobs, URL configuration, and ingestion. |
| [Connector Troubleshooting](#7.6) | Health checks, common sync issues, and forcing re-syncs. |

---

# Page: Connector Overview

# Connector Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [apps/docs/connectors/github.mdx](apps/docs/connectors/github.mdx)
- [apps/docs/connectors/gmail.mdx](apps/docs/connectors/gmail.mdx)
- [apps/docs/connectors/granola.mdx](apps/docs/connectors/granola.mdx)
- [apps/docs/connectors/overview.mdx](apps/docs/connectors/overview.mdx)
- [apps/docs/connectors/s3.mdx](apps/docs/connectors/s3.mdx)
- [apps/docs/connectors/troubleshooting.mdx](apps/docs/connectors/troubleshooting.mdx)
- [apps/docs/images/granola.svg](apps/docs/images/granola.svg)
- [apps/docs/memory-api/connectors/managing-resources.mdx](apps/docs/memory-api/connectors/managing-resources.mdx)
- [apps/web/components/remove-connection-dialog.tsx](apps/web/components/remove-connection-dialog.tsx)

</details>



This page documents the general connector creation flow, the distinction between OAuth and non-OAuth providers, `authLink` redirect handling, and the API calls for listing and deleting connections. Connectors link external data sources to a Supermemory knowledge base, where content is ingested, chunked, and made searchable.

---

## What Connectors Do

Connectors automate the ingestion of external documents into Supermemory. Once a connection is established, the system handles content extraction (e.g., converting HTML, Google Docs, or GitHub Markdown to Markdown), chunking, and generating vector embeddings. Connectors are scoped to one or more `containerTag` values to ensure data isolation between users or projects.

Sources: [apps/docs/connectors/overview.mdx:7-9](), [apps/docs/connectors/overview.mdx:215-226](), [apps/docs/memory-api/connectors/creating-connection.mdx:69-70]()

---

## Supported Providers

| Provider | Auth Method | Real-time Sync | Scheduled Sync |
|---|---|---|---|
| `notion` | OAuth | ✅ Webhooks | ✅ Every 4 hours |
| `google-drive` | OAuth | ✅ Webhooks | ✅ Every 4 hours |
| `gmail` | OAuth | ✅ Pub/Sub | ✅ Every 4 hours |
| `onedrive` | OAuth | ✅ Webhooks | ✅ Every 4 hours |
| `github` | OAuth | ✅ Webhooks | ✅ Every 4 hours |
| `s3` | API Key/Secret | ❌ Not supported | ✅ Every 4 hours |
| `granola` | API Key | ❌ Not supported | ✅ Incremental Sync |
| `web-crawler` | None | ❌ Not supported | ✅ Scheduled recrawl |

Sources: [apps/docs/connectors/overview.mdx:223-231](), [apps/docs/connectors/s3.mdx:179-187](), [apps/docs/connectors/granola.mdx:198-204](), [apps/docs/connectors/overview.mdx:50-54]()

---

## Connection Creation Flow

The creation of a connector is initiated via `POST /v3/connections/{provider}`.

### OAuth Providers

**OAuth Connection Flow**

```mermaid
sequenceDiagram
    participant "ClientApp" as [apps/web]
    participant "API_Endpoint" as [POST /v3/connections/:provider]
    participant "OAuthProvider" as [External Service]
    participant "CallbackURL" as [User Redirect]

    ClientApp->>API_Endpoint: "Request { redirectUrl, containerTags, documentLimit }"
    API_Endpoint-->>ClientApp: "Response { id, authLink, expiresIn, redirectsTo }"
    ClientApp->>OAuthProvider: "Redirect user to authLink"
    OAuthProvider-->>CallbackURL: "Redirect after authorization"
    Note over API_Endpoint,OAuthProvider: "Backend establishes connection and starts sync"
```

Sources: [apps/docs/memory-api/connectors/creating-connection.mdx:6-25](), [apps/docs/connectors/overview.mdx:208-212]()

The `authLink` is a provider-specific URL (e.g., Notion or Google OAuth page). After the user grants permissions, the provider redirects to the `redirectUrl` provided in the initial request [apps/docs/memory-api/connectors/creating-connection.mdx:85-93]().

### Non-OAuth Providers (S3, Granola & Web Crawler)

For providers like `s3` and `granola`, credentials (API keys/secrets) are passed directly in the `metadata` object of the creation request.

*   **S3**: Requires `accessKeyId`, `secretAccessKey`, `bucket`, and `region` [apps/docs/connectors/s3.mdx:76-81]().
*   **Granola**: Requires `apiKey` [apps/docs/connectors/granola.mdx:93-95]().
*   **Web Crawler**: Requires a `startUrl` in metadata.

These connections are active as soon as the API call returns successfully.

Sources: [apps/docs/connectors/s3.mdx:56-68](), [apps/docs/connectors/granola.mdx:73-83](), [apps/docs/memory-api/connectors/creating-connection.mdx:20-24]()

---

## Request Parameters

The `POST /v3/connections/{provider}` endpoint accepts the following structure:

| Parameter | Type | Required | Description |
|---|---|---|---|
| `provider` | `string` | Yes (Path) | `google-drive`, `notion`, `onedrive`, `gmail`, `github`, `s3`, `granola`, `web-crawler`. |
| `redirectUrl` | `string` | OAuth Only | The callback URL in your application. |
| `containerTags` | `string[]` | No | Tags used to partition data (e.g., `["user_123"]`). |
| `documentLimit` | `number` | No | Max items to sync per run (default 10,000). |
| `metadata` | `object` | No | Provider-specific config (e.g., `apiKey` for Granola). |

Sources: [apps/docs/memory-api/connectors/creating-connection.mdx:64-77](), [apps/docs/connectors/granola.mdx:93-97](), [apps/docs/connectors/s3.mdx:76-87]()

---

## Document Processing Pipeline

The pipeline transforms raw external data into searchable "Memories".

**Document Ingestion Pipeline**

```mermaid
flowchart TD
    A["ExternalSource\n(GitHub, Notion, S3)"] --> B["SyncTrigger\n(Webhook/Schedule)"]
    B --> C["ContentExtraction\n(Markdown Conversion)"]
    C --> D["ChunkingAndEmbedding\n(Backend Pipeline)"]
    D --> E["Index in Supermemory\n(Scoped by containerTag)"]
    E --> F["Searchable Memory\n(POST /v3/search)"]
    E --> G["Document List\n(POST /v3/documents/list)"]
```

Sources: [apps/docs/connectors/overview.mdx:217-226](), [apps/docs/connectors/notion.mdx:178-190](), [apps/docs/connectors/gmail.mdx:163-176]()

---

## Connection Management

### Listing Connections
Connections can be retrieved by provider and tags.
- `POST /v3/connections/list`: Returns all connections for specified `containerTags` [apps/docs/connectors/overview.mdx:188-191]().
- `POST /v3/connections/{provider}/connection`: Returns details for a specific provider connection matching the tags.

### Deleting Connections
Connections are removed via `DELETE /v3/connections/:connectionId`.

**Associated Document Handling:**
The API supports an optional `deleteDocuments` boolean query parameter [apps/docs/connectors/s3.mdx:197-198]().
- If `true`: All memories imported via this connection are permanently deleted.
- If `false` (or omitted): The connection is removed, but previously imported memories remain.

In the web application, this is handled by the `RemoveConnectionDialog` component [apps/web/components/remove-connection-dialog.tsx:37](), which uses `PROVIDER_LABELS` for display and prompts the user for document deletion via a `Checkbox` [apps/web/components/remove-connection-dialog.tsx:119-123]().

Sources: [apps/docs/connectors/s3.mdx:190-198](), [apps/web/components/remove-connection-dialog.tsx:17-25](), [apps/web/components/remove-connection-dialog.tsx:114-130]()

---

## Resource Management (GitHub)

The GitHub connector requires an intermediate step where users select specific repositories (resources) to sync.

**GitHub Resource Configuration**

```mermaid
flowchart LR
    A["POST /v3/connections/github"] --> B["OAuth Callback"]
    B --> C["GET /v3/connections/:id/resources\n(List Repositories)"]
    C --> D["User Selection in UI"]
    D --> E["POST /v3/connections/:id/configure\n(Configure Resources)"]
    E --> F["Initial Sync Started"]
```

- `GET /v3/connections/:connectionId/resources`: Returns available repositories (name, id, default branch) for the authenticated user [apps/docs/memory-api/connectors/managing-resources.mdx:16-18]().
- `POST /v3/connections/:connectionId/configure`: Accepts an array of resource objects to begin indexing [apps/docs/memory-api/connectors/managing-resources.mdx:106-108]().

Sources: [apps/docs/connectors/github.mdx:93-133](), [apps/docs/memory-api/connectors/managing-resources.mdx:14-18](), [apps/docs/memory-api/connectors/managing-resources.mdx:104-108]()

---

## Sync Mechanisms

| Frequency | Trigger | Provider Support |
|---|---|---|
| **Instant** | Webhooks | Notion, Google Drive, GitHub, Gmail (Pub/Sub) |
| **Scheduled** | 4 Hours | OAuth providers (fallback), S3 |
| **Incremental** | Manual/Auto | Granola (via `updated_at` timestamps) |
| **Manual** | API Call | `POST /v3/connections/{provider}/import` |

Sources: [apps/docs/connectors/overview.mdx:213-214](), [apps/docs/connectors/granola.mdx:198-204](), [apps/docs/connectors/s3.mdx:202-212]()

---

# Page: GitHub Connector

# GitHub Connector

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [apps/docs/connectors/github.mdx](apps/docs/connectors/github.mdx)
- [apps/docs/connectors/gmail.mdx](apps/docs/connectors/gmail.mdx)
- [apps/docs/connectors/granola.mdx](apps/docs/connectors/granola.mdx)
- [apps/docs/connectors/overview.mdx](apps/docs/connectors/overview.mdx)
- [apps/docs/connectors/s3.mdx](apps/docs/connectors/s3.mdx)
- [apps/docs/connectors/troubleshooting.mdx](apps/docs/connectors/troubleshooting.mdx)
- [apps/docs/images/granola.svg](apps/docs/images/granola.svg)
- [apps/docs/memory-api/connectors/managing-resources.mdx](apps/docs/memory-api/connectors/managing-resources.mdx)
- [apps/web/components/remove-connection-dialog.tsx](apps/web/components/remove-connection-dialog.tsx)

</details>



This document describes the GitHub connector system, which enables automated synchronization of documentation files from GitHub repositories into Supermemory's knowledge base. The GitHub connector uses OAuth authentication, webhook-based incremental syncing, and repository-level resource selection.

For information about the general connector architecture and sync mechanisms shared across all providers, see [Connector Overview](#7.1). For Gmail, Google Drive, Notion, and OneDrive connectors, see their respective sections ([Gmail Connector](#7.3), [Google Drive, Notion & OneDrive](#7.4)). For web crawling without OAuth, see [Web Crawler](#7.5).

## Overview

The GitHub connector is a Scale Plan/Enterprise Plan feature that syncs documentation files from GitHub repositories [apps/docs/connectors/github.mdx:9-11](). Unlike other connectors, it requires explicit repository selection before syncing begins, giving users fine-grained control over which repositories to index [apps/docs/connectors/github.mdx:93-95](). The connector uses webhooks for real-time incremental updates and supports both public and private repositories [apps/docs/connectors/github.mdx:221-223]().

**Key characteristics:**
- OAuth-based authentication with repository and webhook scopes [apps/docs/connectors/github.mdx:82-87]().
- Two-phase setup: OAuth flow followed by repository selection [apps/docs/connectors/github.mdx:89-95]().
- Webhook-based incremental sync with 10-minute batch delay [apps/docs/connectors/github.mdx:224-227]().
- Per-repository webhook installation with unique secrets [apps/docs/connectors/github.mdx:238-239]().
- Supports only documentation file types (`.md`, `.mdx`, `.txt`, etc.) [apps/docs/connectors/github.mdx:207-215]().

Sources: [apps/docs/connectors/github.mdx:1-25](), [apps/docs/connectors/overview.mdx:38-42]()

## Architecture Overview

Title: GitHub Connector Architecture
```mermaid
graph TB
    subgraph "ClientApplication"
        App["Application"]
    end
    
    subgraph "SupermemoryAPI"
        CreateConn["POST /v3/connections/github"]
        GetResources["GET /v3/connections/:id/resources"]
        Configure["POST /v3/connections/:id/configure"]
        Import["POST /v3/connections/github/import"]
        ListConns["POST /v3/connections/list"]
        DeleteConn["DELETE /v3/connections/:id"]
    end
    
    subgraph "GitHubAPIs"
        GitHubOAuth["GitHub OAuth"]
        GitHubAPI["GitHub REST API"]
        GitHubWebhooks["Repository Webhooks"]
    end
    
    subgraph "ProcessingPipeline"
        WebhookHandler["Webhook Handler"]
        FileExtractor["File Extractor"]
        HistorySync["History-based Sync"]
        DocumentIndex["Document Indexing"]
    end
    
    App -->|"1. Create connection"| CreateConn
    CreateConn -->|"2. Redirect URL"| GitHubOAuth
    GitHubOAuth -->|"3. OAuth callback"| App
    App -->|"4. List repos"| GetResources
    GetResources -->|"Fetch using token"| GitHubAPI
    App -->|"5. Configure repos"| Configure
    Configure -->|"Install webhooks"| GitHubAPI
    
    GitHubWebhooks -->|"Push/delete events"| WebhookHandler
    WebhookHandler -->|"Fetch changed files"| GitHubAPI
    WebhookHandler --> FileExtractor
    FileExtractor --> HistorySync
    HistorySync --> DocumentIndex
    
    Import -->|"Trigger full sync"| HistorySync
    App --> ListConns
    App --> DeleteConn
    DeleteConn -->|"Remove webhooks"| GitHubAPI
```

Sources: [apps/docs/connectors/github.mdx:1-100](), [apps/docs/memory-api/connectors/managing-resources.mdx:1-50](), [apps/docs/connectors/overview.mdx:9-35]()

## OAuth Flow and Required Scopes

The GitHub connector requires a standard OAuth 2.0 authorization flow with specific scopes for repository access and webhook management [apps/docs/connectors/github.mdx:82-87]().

### Required OAuth Scopes

| Scope | Purpose |
|-------|---------|
| `repo` | Access to private and public repositories [apps/docs/connectors/github.mdx:84-84]() |
| `user:email` | Access to user's email address [apps/docs/connectors/github.mdx:85-85]() |
| `admin:repo_hook` | Manage webhooks for incremental sync [apps/docs/connectors/github.mdx:86-86]() |

The `admin:repo_hook` scope is critical for the connector's webhook-based incremental sync mechanism. Without it, the connector cannot install webhooks and must rely solely on scheduled syncing [apps/docs/connectors/github.mdx:86-87]().

Sources: [apps/docs/connectors/github.mdx:82-87]()

### OAuth Flow Sequence

Title: OAuth Flow and Repository Selection Sequence
```mermaid
sequenceDiagram
    participant App as "Client App"
    participant API as "POST /v3/connections/github"
    participant GitHub as "GitHub OAuth"
    participant Callback as "OAuth Callback Handler"
    participant Resources as "GET /v3/connections/:id/resources"
    participant Config as "POST /v3/connections/:id/configure"
    
    App->>API: Create connection
    API-->>App: {authLink, expiresIn, id}
    App->>GitHub: Redirect to authLink
    GitHub->>Callback: Redirect with code
    Note over Callback: Exchange code for access_token
    Callback-->>App: Redirect to redirectUrl
    App->>Resources: List repositories
    Resources-->>App: {resources, total_count}
    Note over App: User selects repositories
    App->>Config: Configure repositories
    Note over Config: Install webhooks
    Config-->>App: {success, webhooksRegistered}
```

Sources: [apps/docs/connectors/github.mdx:89-92](), [apps/docs/memory-api/connectors/managing-resources.mdx:14-102]()

## Repository Selection and Resource Management

Unlike other connectors that immediately begin syncing after OAuth, the GitHub connector requires explicit repository selection [apps/docs/memory-api/connectors/managing-resources.mdx:9-10](). This two-phase approach gives users control over which repositories to index and enables per-repository webhook configuration.

### Listing Available Repositories

After OAuth completion, use the generic resource endpoint to fetch repositories [apps/docs/memory-api/connectors/managing-resources.mdx:16-16]():

**Endpoint:** `GET /v3/connections/:connectionId/resources`

**Query Parameters:**
- `page` (optional): Page number, default `1` [apps/docs/memory-api/connectors/managing-resources.mdx:71-71]()
- `per_page` (optional): Results per page, default `30` [apps/docs/memory-api/connectors/managing-resources.mdx:72-72]()

**Response Structure:**

| Field | Type | Description |
|-------|------|-------------|
| `resources` | Array | List of repository objects [apps/docs/memory-api/connectors/managing-resources.mdx:78-78]() |
| `total_count` | Number | Total repositories available [apps/docs/memory-api/connectors/managing-resources.mdx:89-89]() |

**Repository Object Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `id` | Number | GitHub repository ID (unique) [apps/docs/memory-api/connectors/managing-resources.mdx:80-80]() |
| `name` | String | Repository name (e.g., `"your-org/docs"`) [apps/docs/memory-api/connectors/managing-resources.mdx:81-81]() |
| `full_name` | String | Full repository name [apps/docs/memory-api/connectors/managing-resources.mdx:82-82]() |
| `description` | String | Repository description [apps/docs/memory-api/connectors/managing-resources.mdx:83-83]() |
| `private` | Boolean | Whether repository is private [apps/docs/memory-api/connectors/managing-resources.mdx:84-84]() |
| `default_branch` | String | Default branch name [apps/docs/memory-api/connectors/managing-resources.mdx:85-85]() |
| `updated_at` | String | Last update timestamp (ISO 8601) [apps/docs/memory-api/connectors/managing-resources.mdx:86-86]() |

Sources: [apps/docs/memory-api/connectors/managing-resources.mdx:14-91](), [apps/docs/connectors/github.mdx:93-120]()

### Configuring Selected Repositories

After repository selection, configure the connection to set up webhooks and initiate syncing [apps/docs/memory-api/connectors/managing-resources.mdx:106-108]():

**Endpoint:** `POST /v3/connections/:connectionId/configure`

**Request Body:**
```json
{
  "resources": [
    {
      "id": 123456789,
      "name": "your-org/documentation",
      "defaultBranch": "main"
    }
  ]
}
```
[apps/docs/memory-api/connectors/managing-resources.mdx:205-215]()

The configuration endpoint stores repository configuration and triggers an initial sync automatically [apps/docs/memory-api/connectors/managing-resources.mdx:239-241]().

Sources: [apps/docs/memory-api/connectors/managing-resources.mdx:104-241](), [apps/docs/connectors/github.mdx:172-190]()

## Webhook-Based Incremental Sync

The GitHub connector uses webhooks for real-time incremental synchronization, processing only changed files rather than re-syncing entire repositories [apps/docs/connectors/github.mdx:221-223]().

### Webhook Installation

When repositories are configured via `POST /v3/connections/:id/configure`, the connector automatically installs webhooks on each repository. Webhooks are configured for `push` and `delete` events [apps/docs/connectors/github.mdx:221-223]().

Each webhook uses HMAC-SHA256 signature validation with constant-time comparison to verify authenticity [apps/docs/connectors/github.mdx:236-239]().

Sources: [apps/docs/connectors/github.mdx:221-239]()

### Incremental Sync Mechanism

Title: Webhook-Based Incremental Sync Pipeline
```mermaid
graph TB
    subgraph "GitHubRepository"
        Push["Git Push"]
        Delete["File Delete"]
    end
    
    subgraph "WebhookProcessing"
        Receive["Webhook Receiver"]
        Queue["Event Queue"]
        ValidateEvent["Event Validation"]
    end
    
    subgraph "HistoryBasedSync"
        FetchHistory["Fetch History"]
        FilterDocs["Filter Doc Files"]
        FetchContent["Fetch Content"]
    end
    
    subgraph "ProcessingPipeline"
        ExtractContent["Content Extraction"]
        GenerateChunks["Chunking"]
        CreateEmbeddings["Embedding Generation"]
        IndexDocs["Index as github_markdown"]
    end
    
    Push --> Receive
    Delete --> Receive
    Receive --> ValidateEvent
    Receive --> Queue
    ValidateEvent -->|"Valid signature"| Queue
    ValidateEvent -->|"Invalid signature"| Reject["Reject Event"]
    Queue -->|"Batch Delay"| FetchHistory
    FetchHistory --> FilterDocs
    FilterDocs --> FetchContent
    FetchContent --> ExtractContent
    ExtractContent --> GenerateChunks
    GenerateChunks --> CreateEmbeddings
    CreateEmbeddings --> IndexDocs
```

Sources: [apps/docs/connectors/github.mdx:221-235]()

### Batch Processing Delay

Webhook events are processed in batches with a **10-minute delay** to optimize performance [apps/docs/connectors/github.mdx:224-227]():

**Rationale:**
- Prevents excessive syncing during rapid commits (e.g., documentation updates) [apps/docs/connectors/github.mdx:224-227]().
- Reduces API calls to GitHub REST API.
- Minimizes database write operations.

Sources: [apps/docs/connectors/github.mdx:224-227]()

## Supported Document Types

The GitHub connector syncs only documentation and text files, excluding code files, images, and other binary formats [apps/docs/connectors/github.mdx:217-219]().

### File Extensions

| Extension | Type | Indexed As |
|-----------|------|-----------|
| `.md` | Markdown | `github_markdown` [apps/docs/connectors/github.mdx:209-215]() |
| `.mdx` | MDX (Markdown + JSX) | `github_markdown` [apps/docs/connectors/github.mdx:209-215]() |
| `.markdown` | Markdown | `github_markdown` [apps/docs/connectors/github.mdx:209-215]() |
| `.txt` | Plain text | `github_markdown` [apps/docs/connectors/github.mdx:210-215]() |
| `.rst` | reStructuredText | `github_markdown` [apps/docs/connectors/github.mdx:211-215]() |
| `.adoc` | AsciiDoc | `github_markdown` [apps/docs/connectors/github.mdx:212-215]() |
| `.org` | Org-mode | `github_markdown` [apps/docs/connectors/github.mdx:213-215]() |

Sources: [apps/docs/connectors/github.mdx:205-219]()

## API Endpoints Reference

### Connection Creation

**Endpoint:** `POST /v3/connections/github` [apps/docs/connectors/github.mdx:66-66]()

**Request Body Schema:**
```typescript
{
  containerTags?: string[];
  documentLimit?: number;
  metadata?: Record<string, any>;
  redirectUrl?: string;
}
```
[apps/docs/connectors/github.mdx:69-77]()

**Response Schema:**
```typescript
{
  authLink: string;
  expiresIn: string;
  id: string;
}
```
[apps/docs/connectors/overview.mdx:116-121]()

Sources: [apps/docs/connectors/github.mdx:64-80](), [apps/docs/connectors/overview.mdx:105-122]()

### Get Available Resources

**Endpoint:** `GET /v3/connections/:connectionId/resources` [apps/docs/memory-api/connectors/managing-resources.mdx:16-16]()

**Response:**
```typescript
{
  "resources": [
    {
      "id": 123456789,
      "name": "your-org/documentation",
      "full_name": "your-org/documentation",
      "description": "Documentation repository",
      "private": false,
      "default_branch": "main",
      "updated_at": "2024-01-15T10:00:00Z"
    }
  ],
  "total_count": 45
}
```
[apps/docs/memory-api/connectors/managing-resources.mdx:76-91]()

Sources: [apps/docs/memory-api/connectors/managing-resources.mdx:14-91]()

### Delete Connection

**Endpoint:** `DELETE /v3/connections/:connectionId` [apps/docs/connectors/s3.mdx:190-190]()

**Query Parameters:**
- `deleteDocuments` (boolean, optional): Whether to delete synced memories [apps/docs/connectors/s3.mdx:197-197]().

The `RemoveConnectionDialog` component in the web app handles this interaction, allowing users to choose between keeping or deleting documents [apps/web/components/remove-connection-dialog.tsx:115-187]().

Sources: [apps/docs/connectors/s3.mdx:180-198](), [apps/web/components/remove-connection-dialog.tsx:36-51]()

## Sync Mechanisms Summary

The GitHub connector supports three sync mechanisms:

| Mechanism | Trigger | Use Case |
|-----------|---------|----------|
| **Webhook-based** | Git push/delete events [apps/docs/connectors/github.mdx:221-223]() | Real-time incremental updates |
| **Scheduled** | Every 4 hours [apps/docs/connectors/overview.mdx:230-230]() | Consistency check |
| **Manual** | API call (`/import`) [apps/docs/connectors/s3.mdx:211-215]() | Troubleshooting, forced refresh |

Sources: [apps/docs/connectors/overview.mdx:206-230](), [apps/docs/connectors/github.mdx:221-227]()

## Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| **OAuth Callback Fails** | Redirect URL mismatch [apps/docs/connectors/troubleshooting.mdx:73-73]() | Match redirect URL exactly with OAuth app settings [apps/docs/connectors/troubleshooting.mdx:75-75](). |
| **Documents Not Syncing** | Stuck in queued/extracting [apps/docs/connectors/troubleshooting.mdx:95-95]() | Trigger manual sync via `client.connections.import()` [apps/docs/connectors/troubleshooting.mdx:97-104](). |
| **Permission Denied** | Insufficient scopes [apps/docs/connectors/troubleshooting.mdx:113-113]() | Re-authenticate with `repo` and `admin:repo_hook` scopes [apps/docs/connectors/github.mdx:82-87](). |

Sources: [apps/docs/connectors/troubleshooting.mdx:69-130]()

---

# Page: Gmail Connector

# Gmail Connector

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [apps/docs/connectors/github.mdx](apps/docs/connectors/github.mdx)
- [apps/docs/connectors/gmail.mdx](apps/docs/connectors/gmail.mdx)
- [apps/docs/connectors/granola.mdx](apps/docs/connectors/granola.mdx)
- [apps/docs/connectors/overview.mdx](apps/docs/connectors/overview.mdx)
- [apps/docs/connectors/s3.mdx](apps/docs/connectors/s3.mdx)
- [apps/docs/connectors/troubleshooting.mdx](apps/docs/connectors/troubleshooting.mdx)
- [apps/docs/images/granola.svg](apps/docs/images/granola.svg)
- [apps/docs/memory-api/connectors/managing-resources.mdx](apps/docs/memory-api/connectors/managing-resources.mdx)
- [apps/web/components/granola-connect-modal.tsx](apps/web/components/granola-connect-modal.tsx)
- [apps/web/components/remove-connection-dialog.tsx](apps/web/components/remove-connection-dialog.tsx)
- [apps/web/components/settings/sync-history-panel.tsx](apps/web/components/settings/sync-history-panel.tsx)
- [apps/web/components/settings/sync-status-badge.tsx](apps/web/components/settings/sync-status-badge.tsx)
- [apps/web/components/settings/sync-utils.ts](apps/web/components/settings/sync-utils.ts)
- [apps/web/hooks/use-sync-runs.ts](apps/web/hooks/use-sync-runs.ts)
- [apps/web/hooks/use-trigger-sync.ts](apps/web/hooks/use-trigger-sync.ts)
- [packages/ui/assets/icons.tsx](packages/ui/assets/icons.tsx)

</details>



This page documents the Gmail connector for Supermemory: how to create and authenticate a Gmail connection, what email data gets synced, how sync is triggered and maintained, and how to manage or remove a connection. For a general overview of how all connectors work, see [Connector Overview](7.1). For troubleshooting failed or stalled connections, see [Connector Troubleshooting](7.6).

---

## Overview

The Gmail connector syncs email threads from a user's Gmail account into Supermemory as searchable documents. It uses Google's OAuth 2.0 flow for authorization and Google Cloud Pub/Sub for real-time change notifications. [apps/docs/connectors/gmail.mdx:1-7]()

> **Plan requirement:** The Gmail connector is available on **Scale** and **Enterprise** plans only. [apps/docs/connectors/gmail.mdx:9-11]()

The provider identifier used in all API calls is `"gmail"`. [apps/web/components/settings/sync-utils.ts:41-41]() [apps/web/components/remove-connection-dialog.tsx:21-21]()

Sources: [apps/docs/connectors/gmail.mdx:1-11](), [apps/web/components/remove-connection-dialog.tsx:17-25](), [apps/web/components/settings/sync-utils.ts:37-46]()

---

## OAuth Flow

The Gmail connector follows the standard OAuth-based connector flow. The Supermemory backend manages the exchange of authorization codes for refresh tokens and sets up the necessary webhooks.

### Setup Flow Diagram

```mermaid
sequenceDiagram
    participant "Client App" as [apps/web]
    participant "Supermemory API" as [packages/lib/api.ts]
    participant "Google OAuth" as "Google OAuth 2.0"
    participant "Google Pub/Sub" as "Google Cloud Pub/Sub"

    "[apps/web]"->>"[packages/lib/api.ts]": "POST /v3/connections/gmail"
    Note over "[packages/lib/api.ts]": "API client handles connection creation"
    "[packages/lib/api.ts]"-->>"[apps/web]": "{ authLink, id, expiresIn }"
    "[apps/web]"->>"Google OAuth 2.0": "Redirect user to authLink"
    "Google OAuth 2.0"-->>"[apps/web]": "Redirect to redirectUrl (OAuth callback)"
    "[packages/lib/api.ts]"->>"Google OAuth 2.0": "Exchange code for tokens"
    "[packages/lib/api.ts]"->>"Google Cloud Pub/Sub": "Register Gmail watch subscription"
    "Google Cloud Pub/Sub"-->>"[packages/lib/api.ts]": "Watch active (7-day TTL)"
    "[packages/lib/api.ts]"-->>"[apps/web]": "Connection established, sync begins"
```
Sources: [apps/docs/connectors/gmail.mdx:15-84](), [apps/docs/connectors/overview.mdx:208-214](), [apps/docs/connectors/overview.mdx:59-82]()

### Create a Connection

The connection is initiated via the API using the `POST /v3/connections/gmail` endpoint. [apps/docs/connectors/gmail.mdx:66-78]()

| Parameter | Required | Description |
|---|---|---|
| `redirectUrl` | Yes | Your app's OAuth callback URL |
| `containerTags` | No | Scope the connection to specific users/orgs |
| `documentLimit` | No | Max threads to sync (default: 10,000) |
| `metadata` | No | Key-value pairs added to every synced document |

**Response fields:** [apps/docs/connectors/overview.mdx:116-122]()

| Field | Description |
|---|---|
| `id` | Connection identifier |
| `authLink` | Google OAuth URL to redirect the user to |
| `expiresIn` | Expiry of the auth link (e.g., "1 hour") |
| `redirectsTo` | The `redirectUrl` you provided |

Sources: [apps/docs/connectors/gmail.mdx:15-78](), [apps/docs/connectors/overview.mdx:106-122]()

---

## What Gets Synced

Gmail threads (full conversation histories) are synced as individual documents with type `gmail_thread`. [apps/docs/connectors/gmail.mdx:151-167]()

**Data ingested per thread:** [apps/docs/connectors/gmail.mdx:153-159]()

- **Thread content**: Converted to structured markdown.
- **Messages**: All messages in the thread preserved in order.
- **Metadata**: Subject, from, to, cc, bcc, and date.
- **HTML Cleanup**: HTML content is converted to clean markdown.
- **Attachments**: Filename, MIME type, and size are stored as metadata. Content is referenced, not stored.

### Document Metadata Fields

Each synced thread includes searchable metadata used in filters: [apps/docs/connectors/gmail.mdx:165-176]()

| Field | Description |
|---|---|
| `type` | Always `gmail_thread` |
| `subject` | Email subject line |
| `threadId` | Gmail thread ID |
| `from` | Sender email address |
| `to` | Recipient email addresses |
| `date` | Date of the first message |
| `messageCount` | Number of messages in thread |
| `attachmentCount` | Number of attachments |
| `attachmentNames` | List of attachment filenames |

Sources: [apps/docs/connectors/gmail.mdx:165-176](), [apps/docs/connectors/gmail.mdx:179-190]()

---

## Sync Mechanisms

The Gmail connector utilizes a hybrid approach to ensure data freshness while respecting API rate limits.

### Sync Architecture Diagram

```mermaid
graph TD
    subgraph "External Services"
        GmailAPI["Gmail API"]
        PubSub["Google Cloud Pub/Sub"]
    end

    subgraph "Supermemory Backend"
        Watch["Gmail watch subscription\n(7-day TTL, auto-renewed)"]
        Scheduler["Scheduled sync\n(every 4 hours)"]
        ManualSync["Manual sync\nPOST /v3/connections/gmail/import"]
        HistoryId["historyId\n(incremental marker)"]
        Ingest["Document ingestion pipeline"]
    end

    GmailAPI --> Watch
    Watch --> PubSub
    PubSub -->|"INBOX change notification"| HistoryId
    Scheduler --> HistoryId
    ManualSync --> HistoryId
    HistoryId -->|"Fetch changed threads"| Ingest
    Ingest --> SM["Supermemory Vector Store"]
```
Sources: [apps/docs/connectors/gmail.mdx:7-11](), [apps/docs/connectors/overview.mdx:213-214](), [apps/docs/connectors/overview.mdx:218-226]()

| Sync Method | Behavior |
|---|---|
| **Real-time (Pub/Sub)** | Triggers on **INBOX** changes via Google Cloud Pub/Sub webhooks. [apps/docs/connectors/troubleshooting.mdx:191-193]() |
| **Scheduled** | Runs every 4 hours to catch changes missed by webhooks. [apps/docs/connectors/overview.mdx:213-214]() |
| **Manual** | On-demand via `POST /v3/connections/gmail/import`. [apps/docs/connectors/gmail.mdx:197-199]() |
| **Incremental** | Uses Gmail's `historyId` and `updated_at` timestamps to fetch only threads changed since the last sync. [apps/docs/connectors/gmail.mdx:7-7]() |

---

## Connection Management

### List Connections

Connections can be retrieved using the `POST /v3/connections/list` endpoint, filtering by provider or tags. [apps/docs/connectors/gmail.mdx:129-135]()

### Delete a Connection

Connections can be removed via the API or the web UI using the `RemoveConnectionDialog`. [apps/web/components/remove-connection-dialog.tsx:37-45]()

`DELETE /v3/connections/:connectionId` [apps/docs/connectors/troubleshooting.mdx:212-214]()

| Parameter | Type | Description |
|---|---|---|
| `connectionId` | Param | The unique ID of the connection |
| `deleteDocuments` | Query | Boolean. If `true`, permanently deletes all imported memories. [apps/web/components/remove-connection-dialog.tsx:53-55]() |

**UI Implementation**: The `RemoveConnectionDialog` component provides a toggle for users to choose between "Disconnect" (keeping imported memories) or "Disconnect and delete memories". [apps/web/components/remove-connection-dialog.tsx:114-130]()

Sources: [apps/docs/connectors/gmail.mdx:194-212](), [apps/web/components/remove-connection-dialog.tsx:114-162]()

---

## Troubleshooting

### Common Gmail Issues

| Problem | Potential Cause | Solution |
|---|---|---|
| **OAuth Callback Fails** | Redirect URL mismatch | Ensure `redirectUrl` matches the OAuth app configuration exactly. [apps/docs/connectors/troubleshooting.mdx:71-86]() |
| **Sync Stops** | Revoked access or expired refresh token | Delete and recreate the connection to force a fresh OAuth flow. [apps/docs/connectors/troubleshooting.mdx:203-220]() |
| **Real-time Sync Fails** | Non-INBOX label | Real-time sync only triggers on INBOX changes. Use manual sync for other labels. [apps/docs/connectors/troubleshooting.mdx:187-201]() |
| **Plan Error** | Subscription mismatch | Verify the organization is on a **Scale** or **Enterprise** plan. [apps/docs/connectors/troubleshooting.mdx:222-226]() |

Sources: [apps/docs/connectors/troubleshooting.mdx:71-227]()

---

# Page: Google Drive, Notion & OneDrive

# Google Drive, Notion & OneDrive

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [apps/docs/connectors/notion.mdx](apps/docs/connectors/notion.mdx)
- [apps/docs/connectors/web-crawler.mdx](apps/docs/connectors/web-crawler.mdx)
- [apps/docs/memory-api/connectors/creating-connection.mdx](apps/docs/memory-api/connectors/creating-connection.mdx)
- [apps/docs/memory-api/connectors/overview.mdx](apps/docs/memory-api/connectors/overview.mdx)
- [apps/web/components/granola-connect-modal.tsx](apps/web/components/granola-connect-modal.tsx)
- [apps/web/components/settings/sync-history-panel.tsx](apps/web/components/settings/sync-history-panel.tsx)
- [apps/web/components/settings/sync-status-badge.tsx](apps/web/components/settings/sync-status-badge.tsx)
- [apps/web/components/settings/sync-utils.ts](apps/web/components/settings/sync-utils.ts)
- [apps/web/hooks/use-sync-runs.ts](apps/web/hooks/use-sync-runs.ts)
- [apps/web/hooks/use-trigger-sync.ts](apps/web/hooks/use-trigger-sync.ts)
- [packages/ui/assets/icons.tsx](packages/ui/assets/icons.tsx)

</details>



This document covers the Google Drive, Notion, and OneDrive connector implementations. These three connectors share a common OAuth-based authentication pattern and sync mechanism, while differing in their provider-specific APIs and document handling.

## Purpose and Scope

These connectors automatically sync documents from external services into Supermemory's knowledge base. They bridge the gap between third-party storage and the Supermemory "Natural Language Space" by extracting content and converting it into searchable memories.

- **Google Drive**: Syncs Google Docs, Slides, and Sheets. Real-time sync is achieved via webhooks. [apps/docs/memory-api/connectors/overview.mdx:29-29]()
- **Notion**: Syncs workspace pages, databases, and blocks. Supports rich formatting and database properties. [apps/docs/connectors/notion.mdx:6-6]()
- **OneDrive**: Syncs Microsoft Word, Excel, and PowerPoint files. [apps/docs/memory-api/connectors/overview.mdx:7-7]()

## OAuth Authentication Flow

The authentication flow is standardized across these providers. The flow begins with a call to the `/v3/connections/{provider}` endpoint, which generates an `authLink` for user redirection.

### Connection Creation

```mermaid
sequenceDiagram
    participant Client as "Client Application (apps/web)"
    participant API as "POST /v3/connections/:provider"
    participant OAuth as "Provider OAuth Server"
    
    Note over Client, API: provider = google-drive | notion | onedrive
    Client->>API: "$fetch('@post/connections/:provider')"
    Note right of Client: Body: {redirectUrl, containerTags, documentLimit}
    API-->>Client: "{authLink, id, expiresIn, redirectsTo}"
    
    Client->>OAuth: "Redirect user to authLink"
    OAuth-->>Client: "Redirect to redirectUrl (Callback)"
    Note over Client: "Sync begins automatically"
```

**Connection Initialization: OAuth Flow and Token Exchange**

Sources: [apps/docs/memory-api/connectors/creating-connection.mdx:6-25](), [apps/docs/memory-api/connectors/overview.mdx:9-16](), [apps/web/components/granola-connect-modal.tsx:53-59]()

### Request Parameters
The connection API validates several key parameters:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `containerTags` | `string[]` | No | Groups memories (e.g., by `userId` or `projectId`). [apps/docs/memory-api/connectors/creating-connection.mdx:69-70]() |
| `documentLimit` | `number` | No | Max documents to sync (1-10,000). [apps/docs/memory-api/connectors/creating-connection.mdx:74-77]() |
| `redirectUrl` | `string` | Yes | Where to send user after OAuth. [apps/docs/memory-api/connectors/creating-connection.mdx:67-67]() |
| `metadata` | `object` | No | Associated metadata for every document synced. [apps/docs/memory-api/connectors/creating-connection.mdx:71-73]() |

Sources: [apps/docs/memory-api/connectors/creating-connection.mdx:64-77]()

## Sync Mechanisms

Supermemory employs a multi-tier sync strategy to ensure data consistency:
1. **Real-time (Webhooks)**: Immediate updates when files change (Google Drive & Notion). [apps/docs/memory-api/connectors/overview.mdx:27-29]()
2. **Scheduled Sync**: Every four hours for OAuth-based connectors. [apps/docs/memory-api/connectors/overview.mdx:31-31]()
3. **Manual Sync**: Triggered via the `useTriggerSync` hook or API. [apps/web/hooks/use-trigger-sync.ts:13-37]()

### Provider-Specific Sync Lifecycles

| Provider | Real-time Sync | Scheduled Sync | Notes |
|----------|----------------|----------------|-------|
| **Google Drive** | Yes (Webhooks) | Every 4 hours | Documents synced instantaneously. [apps/docs/memory-api/connectors/overview.mdx:29-29]() |
| **Notion** | Yes (Webhooks) | Every 4 hours | Uses Notion Search API, newest edited first. [apps/docs/connectors/notion.mdx:154-155]() |
| **OneDrive** | No | Every 4 hours | Standard scheduled sync. [apps/docs/memory-api/connectors/overview.mdx:31-31]() |

Sources: [apps/docs/memory-api/connectors/overview.mdx:24-35](), [apps/docs/connectors/notion.mdx:152-160]()

### Document Processing Pipeline

Once a document is fetched, it is processed into the Supermemory index.

```mermaid
graph TD
    subgraph "External_Provider_Space"
        GDrive["Google Drive File"]
        NotionPage["Notion Page"]
        OneDriveFile["OneDrive Doc"]
    end

    subgraph "Code_Entity_Space"
        Trigger["useTriggerSync / Cron Trigger"]
        Extraction["$fetch('@post/connections/:provider/import')"]
        SyncRun["SyncRun (apps/web/hooks/use-sync-runs.ts)"]
    end

    subgraph "Supermemory_Index"
        Memory["Searchable Memory"]
        Status["SyncStatusBadge (apps/web/components/settings/sync-status-badge.tsx)"]
    end

    GDrive --> Trigger
    NotionPage --> Trigger
    OneDriveFile --> Trigger
    Trigger --> Extraction
    Extraction --> SyncRun
    SyncRun --> Memory
    SyncRun --> Status
```

**Bridge: Provider Content to Code Ingestion Entities**

Sources: [apps/web/hooks/use-trigger-sync.ts:13-37](), [apps/web/hooks/use-sync-runs.ts:10-20](), [apps/web/components/settings/sync-status-badge.tsx:23-28]()

## Supported Document Types

Supermemory processes various formats depending on the provider.

- **Google Drive**: Google Docs, Slides, Sheets. [packages/ui/assets/icons.tsx:76-116]()
- **Notion**: Pages, Databases (Properties preserved), Blocks (Text, Heading, Code, Quote, Callout, Table, Image, Embed). [apps/docs/connectors/notion.mdx:163-189]()
- **OneDrive**: Microsoft Word, Excel, PowerPoint. [packages/ui/assets/icons.tsx:1-25](), [packages/ui/assets/icons.tsx:132-145]()

## Monitoring and Management

### Sync Status and History
The web application provides detailed monitoring of sync operations via the `SyncHistoryPanel` and `SyncStatusBadge`.

- **SyncStatusBadge**: Displays the current state (`syncing`, `synced`, `expired`, `idle`). [apps/web/components/settings/sync-status-badge.tsx:5-14]()
- **SyncHistoryPanel**: Shows a timeline of `SyncRun` objects, including items processed, failures, and trigger types (Manual, Scheduled, Webhook). [apps/web/components/settings/sync-history-panel.tsx:79-157]()
- **useSyncRuns**: A hook that polls for updates every 5 seconds if a sync is currently `running`. [apps/web/hooks/use-sync-runs.ts:37-43]()

### Manual Sync Trigger
Users can manually trigger a re-sync through the UI, which utilizes optimistic updates to provide immediate feedback.

```typescript
// useTriggerSync implementation detail
onMutate: async (variables) => {
    // Optimistically set syncInProgress to true in the connections cache
    queryClient.setQueryData(['connections'], (old) => 
        old?.map(c => c.provider === variables.provider ? { ...c, metadata: { ...c.metadata, syncInProgress: true } } : c)
    );
}
```

Sources: [apps/web/hooks/use-trigger-sync.ts:39-56](), [apps/web/components/settings/sync-utils.ts:30-34]()

## Configuration and Limits

- **Document Limits**: Notion syncs are ordered by `last edited time, newest first`. If the `documentLimit` is reached, older pages are skipped until a subsequent sync run. [apps/docs/connectors/notion.mdx:154-157]()
- **Re-authentication**: If a connection's credentials expire, the `SyncStatusBadge` will display "Needs reauth" based on the `isExpired` flag. [apps/web/components/settings/sync-status-badge.tsx:73-82]()

Sources: [apps/docs/connectors/notion.mdx:152-160](), [apps/web/components/settings/sync-status-badge.tsx:23-30]()

---

# Page: Web Crawler

# Web Crawler

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [apps/docs/connectors/github.mdx](apps/docs/connectors/github.mdx)
- [apps/docs/connectors/gmail.mdx](apps/docs/connectors/gmail.mdx)
- [apps/docs/connectors/granola.mdx](apps/docs/connectors/granola.mdx)
- [apps/docs/connectors/notion.mdx](apps/docs/connectors/notion.mdx)
- [apps/docs/connectors/overview.mdx](apps/docs/connectors/overview.mdx)
- [apps/docs/connectors/s3.mdx](apps/docs/connectors/s3.mdx)
- [apps/docs/connectors/troubleshooting.mdx](apps/docs/connectors/troubleshooting.mdx)
- [apps/docs/connectors/web-crawler.mdx](apps/docs/connectors/web-crawler.mdx)
- [apps/docs/images/granola.svg](apps/docs/images/granola.svg)
- [apps/docs/memory-api/connectors/creating-connection.mdx](apps/docs/memory-api/connectors/creating-connection.mdx)
- [apps/docs/memory-api/connectors/managing-resources.mdx](apps/docs/memory-api/connectors/managing-resources.mdx)
- [apps/docs/memory-api/connectors/overview.mdx](apps/docs/memory-api/connectors/overview.mdx)
- [apps/web/components/remove-connection-dialog.tsx](apps/web/components/remove-connection-dialog.tsx)

</details>



The Web Crawler connector automatically ingests and syncs web pages from public websites into Supermemory's knowledge base. Unlike other connectors that use OAuth and real-time webhooks, the web crawler operates without authentication and uses scheduled recrawling to keep content up-to-date.

**Scope**: This document covers the web crawler connector implementation, including connection setup, crawl mechanisms, URL validation, security protections, and scheduled recrawling.

**Plan Requirement**: The web crawler requires a **Scale Plan** or **Enterprise Plan** [apps/docs/connectors/web-crawler.mdx:9-11]().

## Connection Creation

The web crawler follows a simplified connection flow compared to OAuth-based connectors. No user authentication or OAuth redirect is required—the connection is established immediately upon creation [apps/docs/connectors/web-crawler.mdx:88-90]().

**Connection creation sequence for `POST /v3/connections/web-crawler`**

```mermaid
sequenceDiagram
    participant Client as "Client Application"
    participant API as "POST /v3/connections/web-crawler"
    participant SSRFCheck as "SSRF Validator"
    participant RobotsCheck as "robots.txt Compliance"
    participant Scheduler as "Crawl Scheduler"
    participant DB as "Connection Store"

    Client->>API: "POST {metadata: {startUrl}, containerTags, documentLimit}"
    API->>SSRFCheck: "Validate startUrl (Public access check)"
    SSRFCheck->>SSRFCheck: "Block private IPs, localhost"
    SSRFCheck-->>API: "URL valid"
    API->>DB: "Store connection record"
    API->>Scheduler: "Queue initial crawl"
    Scheduler->>RobotsCheck: "Verify robots.txt rules"
    API-->>Client: "Response: {id, authLink: null, expiresIn: null}"
    Note over Scheduler: "Initial crawl begins immediately"
```
Sources: [apps/docs/memory-api/connectors/overview.mdx:17-20](), [apps/docs/connectors/web-crawler.mdx:175-178](), [apps/docs/memory-api/connectors/creating-connection.mdx:21-24]()

### API Request Parameters

The connection creation request to `POST /v3/connections/web-crawler` accepts the following parameters:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `metadata` | `object` | Yes | Must include `startUrl` (e.g., `{"startUrl": "https://docs.example.com"}`) [apps/docs/memory-api/connectors/creating-connection.mdx:71-73]() |
| `containerTags` | `string[]` | No | Optional tags for partitioning data [apps/docs/memory-api/connectors/creating-connection.mdx:69-70]() |
| `documentLimit` | `number` | No | Caps pages fetched per sync (Range: 1–10,000) [apps/docs/memory-api/connectors/creating-connection.mdx:74-77]() |
| `redirectUrl` | `string` | No | Optional; not required for crawler functionality [apps/docs/memory-api/connectors/creating-connection.mdx:67-68]() |

**Response Structure**: Unlike OAuth connectors, `authLink` and `expiresIn` are `null` [apps/docs/memory-api/connectors/creating-connection.mdx:94-96]().

```json
{
  "id": "conn_wc123",
  "authLink": null,
  "expiresIn": null,
  "redirectsTo": "https://yourapp.com/callback"
}
```
Sources: [apps/docs/memory-api/connectors/creating-connection.mdx:82-90](), [apps/docs/connectors/web-crawler.mdx:78-84]()

## Crawl Mechanism

The web crawler operates on a scheduled recrawling model rather than real-time webhooks [apps/docs/connectors/web-crawler.mdx:182-187]().

### Sync Timing Architecture

```mermaid
graph LR
    subgraph "Initial State"
        A["POST /v3/connections/web-crawler"] --> B["Initial Crawl Queued"]
    end
    
    subgraph "Ongoing Sync"
        B --> C["Crawl startUrl"]
        C --> D["Extract Same-Domain Links"]
        D --> E["Process HTML to Markdown"]
        E --> F["Store as Memory"]
    end
    
    subgraph "Scheduled Recrawl"
        F --> G["Wait Period"]
        G --> H{"Last sync > 7 days?"}
        H -->|Yes| I["Queue Recrawl"]
        H -->|No| G
        I --> C
    end
```
Sources: [apps/docs/memory-api/connectors/overview.mdx:30-32](), [apps/docs/connectors/web-crawler.mdx:184-186](), [apps/docs/connectors/web-crawler.mdx:168-171]()

### Recrawl Schedule Logic

The recrawl mechanism follows these principles:

1. **Trigger Condition**: Sites are recrawled if they haven't been synced in 7+ days [apps/docs/memory-api/connectors/overview.mdx:32-32]().
2. **Domain Boundary**: Crawling is restricted to **same-domain** only (respects hostname boundaries) [apps/docs/connectors/web-crawler.mdx:169-169]().
3. **Manual Sync**: Users can trigger a sync manually via `POST /v3/connections/web-crawler/sync` [apps/docs/memory-api/connectors/overview.mdx:34-34]().

## URL Validation and Security

The web crawler implements strict protections to prevent Server-Side Request Forgery (SSRF) and ensure compliance with site owner preferences.

### Security Validation Pipeline

| Protection | Requirement |
|------------|-------------|
| **SSRF Protection** | Blocks localhost, private IPs (10.x, 192.168.x), and cloud metadata endpoints [apps/docs/connectors/web-crawler.mdx:7-7](), [apps/docs/connectors/web-crawler.mdx:175-176](). |
| **Robots.txt** | Respects `robots.txt` disallow rules for the target domain [apps/docs/connectors/web-crawler.mdx:170-170](). |
| **Content Filtering** | Only processes valid public URLs that return HTML content; non-HTML files are skipped [apps/docs/connectors/web-crawler.mdx:171-178](). |

Sources: [apps/docs/connectors/web-crawler.mdx:7-7](), [apps/docs/connectors/web-crawler.mdx:170-178]()

## Content Ingestion as Memories

Crawled pages are transformed into memories and can be monitored via the connections API.

### Document Metadata

Each crawled web page is stored as a document with the following properties:
- **Type**: `webpage` [apps/docs/connectors/web-crawler.mdx:158-159]().
- **Status**: `done` or `pending` [apps/docs/connectors/web-crawler.mdx:158-159]().
- **Source**: The `url` of the crawled page [apps/docs/connectors/web-crawler.mdx:158-159]().

### Monitoring Sync Progress

Developers can list the synced pages for a specific web crawler connection:

```typescript
// List synced web pages
const documents = await client.connections.listDocuments('web-crawler', {
  containerTags: ['user-123', 'website-sync']
});
```
Sources: [apps/docs/connectors/web-crawler.mdx:106-108](), [apps/docs/connectors/web-crawler.mdx:151-161]()

## Troubleshooting

Common issues with the web crawler include:
- **Robots.txt Block**: The site owner has explicitly blocked crawlers via `robots.txt` [apps/docs/connectors/web-crawler.mdx:170-170]().
- **Private URLs**: The crawler cannot access `localhost`, internal domains, or password-protected sites [apps/docs/connectors/web-crawler.mdx:175-178]().
- **Document Limit**: If the `documentLimit` (max 10,000) is reached, further pages on the site will not be crawled until the limit is increased [apps/docs/memory-api/connectors/creating-connection.mdx:74-77]().

Sources: [apps/docs/connectors/web-crawler.mdx:170-178](), [apps/docs/memory-api/connectors/creating-connection.mdx:74-77]()

---

# Page: Connector Troubleshooting

# Connector Troubleshooting

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [apps/docs/connectors/github.mdx](apps/docs/connectors/github.mdx)
- [apps/docs/connectors/gmail.mdx](apps/docs/connectors/gmail.mdx)
- [apps/docs/connectors/granola.mdx](apps/docs/connectors/granola.mdx)
- [apps/docs/connectors/overview.mdx](apps/docs/connectors/overview.mdx)
- [apps/docs/connectors/s3.mdx](apps/docs/connectors/s3.mdx)
- [apps/docs/connectors/troubleshooting.mdx](apps/docs/connectors/troubleshooting.mdx)
- [apps/docs/images/granola.svg](apps/docs/images/granola.svg)
- [apps/docs/memory-api/connectors/managing-resources.mdx](apps/docs/memory-api/connectors/managing-resources.mdx)
- [apps/web/components/granola-connect-modal.tsx](apps/web/components/granola-connect-modal.tsx)
- [apps/web/components/remove-connection-dialog.tsx](apps/web/components/remove-connection-dialog.tsx)
- [apps/web/components/settings/sync-history-panel.tsx](apps/web/components/settings/sync-history-panel.tsx)
- [apps/web/components/settings/sync-status-badge.tsx](apps/web/components/settings/sync-status-badge.tsx)
- [apps/web/components/settings/sync-utils.ts](apps/web/components/settings/sync-utils.ts)
- [apps/web/hooks/use-sync-runs.ts](apps/web/hooks/use-sync-runs.ts)
- [apps/web/hooks/use-trigger-sync.ts](apps/web/hooks/use-trigger-sync.ts)
- [packages/ui/assets/icons.tsx](packages/ui/assets/icons.tsx)

</details>



This document provides diagnostic procedures and resolution strategies for issues with the Supermemory connector system. Connectors automatically sync content from external services (GitHub, Gmail, Notion, Google Drive, OneDrive, S3, Granola, Web Crawler) into the Supermemory knowledge base.

### Plan Requirements

Access to specific connectors is gated by user plans. If a connection fails with a "Plan Required" error, verify the organization's current subscription level.

| Provider | Required Plan |
|----------|--------------|
| GitHub | Scale or Enterprise |
| Gmail | Scale or Enterprise |
| Web Crawler | Scale or Enterprise |
| S3 | Scale or Higher |
| Granola | Pro or Higher |
| Google Drive | Paid Plans |
| Notion | Paid Plans |
| OneDrive | Paid Plans |

Sources: [apps/docs/connectors/github.mdx:9-11](), [apps/docs/connectors/gmail.mdx:9-12](), [apps/docs/connectors/s3.mdx:9-11](), [apps/docs/connectors/granola.mdx:9-11]()

## Diagnostic Overview

The connector system follows a multi-stage pipeline. Failures can occur during authentication, resource selection, webhook registration, or content extraction.

### Connector Lifecycle and Data Flow

**Connector Data Flow: From External Provider to Vector Index**

```mermaid
flowchart TD
    subgraph "External Space"
        GitHub["GitHub Repo"]
        Gmail["Gmail Thread"]
        S3["S3 Bucket"]
    end

    subgraph "Connection Management"
        Create["POST /v3/connections/:provider"]
        Auth["OAuth Flow / API Key Validation"]
        Configure["POST /v3/connections/:id/configure"]
    end

    subgraph "Sync Engine"
        Webhook["Webhook Trigger"]
        Manual["Manual Import Trigger"]
        Extraction["Content Extraction"]
        Chunking["Chunking & Embedding"]
    end

    subgraph "Storage"
        Drizzle["Drizzle ORM (Metadata)"]
        Vector["Vector Index (Memories)"]
    end

    GitHub --> Auth
    Gmail --> Auth
    S3 --> Auth
    Auth --> Configure
    Configure --> Webhook
    Webhook --> Extraction
    Manual --> Extraction
    Extraction --> Chunking
    Chunking --> Drizzle
    Chunking --> Vector
```

**Key Failure Points:**
- **OAuth Stage**: `redirectUrl` mismatch or missing scopes (e.g., `admin:repo_hook` for GitHub). [apps/docs/connectors/troubleshooting.mdx:71-86](), [apps/docs/connectors/github.mdx:82-87]()
- **Credential Stage**: Invalid API Key for Granola or incorrect AWS keys for S3. [apps/docs/connectors/granola.mdx:208-212](), [apps/docs/connectors/s3.mdx:213-214]()
- **Sync Stage**: Rate limiting, document size limits (>50MB), or unsupported file types. [apps/docs/connectors/troubleshooting.mdx:106-109]()
- **Processing Stage**: Content extraction timeouts or embedding failures. [apps/docs/connectors/troubleshooting.mdx:94-96]()

Sources: [apps/docs/connectors/troubleshooting.mdx:71-131](), [apps/docs/connectors/overview.mdx:215-226](), [apps/docs/connectors/github.mdx:82-87](), [apps/docs/connectors/granola.mdx:208-214]()

## Sync Status and Monitoring

Supermemory provides several mechanisms to check the health of active connections.

### Health Check via SDK/API
You can programmatically check for "stuck" or failed documents using the `client.connections.listDocuments` method or the `/v3/documents/list` endpoint.

```typescript
// Check for failed documents in a Notion connection
const documents = await client.connections.listDocuments('notion', {
  containerTags: ['user-123']
});

const failed = documents.filter(doc => doc.status === 'failed');
if (failed.length > 0) {
  console.log(`⚠️ ${failed.length} documents failed to sync`);
}
```
Sources: [apps/docs/connectors/troubleshooting.mdx:25-34](), [apps/docs/connectors/troubleshooting.mdx:60-65]()

### UI Status Mapping
The web application uses the `formatRelativeTime` utility and `TRIGGER_TYPE_LABELS` to display sync metadata in the settings panel.

| Internal Trigger | UI Label | Source |
|------------------|----------|--------|
| `event` | Webhook | [apps/web/components/settings/sync-utils.ts:31-31]() |
| `cron` | Scheduled | [apps/web/components/settings/sync-utils.ts:32-32]() |
| `manual` | Manual | [apps/web/components/settings/sync-utils.ts:33-33]() |

Sources: [apps/web/components/settings/sync-utils.ts:30-34](), [apps/web/components/settings/sync-utils.ts:5-27]()

## Common Issues and Resolutions

### 1. OAuth Callback Failures
**Problem**: "Invalid redirect URI" error during the OAuth handshake.
**Solution**: Ensure the `redirectUrl` passed to `client.connections.create` matches the one configured in the provider's developer console (Google, Notion, GitHub) exactly. [apps/docs/connectors/troubleshooting.mdx:75-86]()

### 2. GitHub Repository Not Syncing
**Problem**: GitHub connection is active but no files are appearing.
**Solution**: GitHub requires explicit resource configuration. Use the `configure` endpoint to select specific repositories.
```typescript
await client.connections.github.configure(connectionId, {
  repositories: [{ id: repoId, name: "org/repo", defaultBranch: "main" }]
});
```
Sources: [apps/docs/connectors/github.mdx:121-130](), [apps/docs/memory-api/connectors/managing-resources.mdx:104-108]()

### 3. Gmail Real-time Sync Stopped
**Problem**: New emails aren't appearing immediately.
**Root Cause**: Gmail real-time sync relies on Google Cloud Pub/Sub "watch" subscriptions which expire every 7 days. While Supermemory attempts auto-renewal, a manual re-sync can fix stuck states. [apps/docs/connectors/troubleshooting.mdx:187-194]()
**Resolution**: Trigger a manual import.
```typescript
await client.connections.import('gmail', { containerTags: ['user-123'] });
```
Sources: [apps/docs/connectors/troubleshooting.mdx:196-200]()

### 4. Granola Connection Errors
**Problem**: `Granola API key is invalid`.
**Solution**: Verify the key in Granola under **Settings > Connectors > API keys**. Note that Granola requires a plan that supports API key generation. [apps/docs/connectors/granola.mdx:211-212](), [apps/docs/connectors/granola.mdx:176-178]()

## Summary of Troubleshooting Entities

**Bridge: UI Components to API Hooks**

```mermaid
classDiagram
    class SyncUI {
        << apps/web/components/settings >>
        +SyncStatusBadge
        +SyncHistoryPanel
        +formatRelativeTime()
        +TRIGGER_TYPE_LABELS
    }
    class SyncHooks {
        << apps/web/hooks >>
        +useSyncRuns(connectionId)
        +useTriggerSync()
    }
    class APIClient {
        << packages/lib/api.ts >>
        +@get/connections/:connectionId/sync-runs
        +@post/connections/:provider/import
        +@post/connections/:connectionId/configure
    }

    SyncUI --|> SyncHooks : "Observes sync state"
    SyncHooks --|> APIClient : "Fetches history & triggers"
    SyncUI --|> APIClient : "Configures resources"
```

Sources: [apps/web/hooks/use-sync-runs.ts:10-20](), [apps/web/components/settings/sync-utils.ts:30-34](), [apps/web/components/settings/sync-status-badge.tsx:5-14]()

---

# Page: SDKs & Client Libraries

# SDKs & Client Libraries

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [apps/docs/memory-api/sdks/native.mdx](apps/docs/memory-api/sdks/native.mdx)
- [apps/docs/memory-api/sdks/python.mdx](apps/docs/memory-api/sdks/python.mdx)
- [apps/docs/memory-api/sdks/typescript.mdx](apps/docs/memory-api/sdks/typescript.mdx)
- [packages/tools/README.md](packages/tools/README.md)
- [packages/tools/package.json](packages/tools/package.json)
- [packages/tools/src/vercel/index.ts](packages/tools/src/vercel/index.ts)
- [packages/tools/src/vercel/memory-prompt.ts](packages/tools/src/vercel/memory-prompt.ts)
- [packages/tools/src/vercel/middleware.ts](packages/tools/src/vercel/middleware.ts)
- [packages/tools/src/vercel/util.ts](packages/tools/src/vercel/util.ts)

</details>



This document provides a high-level overview of the official Supermemory SDKs available for TypeScript/JavaScript and Python, as well as specialized integration libraries for AI frameworks. These SDKs wrap the Supermemory REST API to provide idiomatic, type-safe interfaces for managing memories, documents, and user profiles.

For deep technical details on specific methods, refer to the child pages:
- [TypeScript/JavaScript SDK](#8.1) — Installation and core methods for web/Node.js.
- [Python SDK](#8.2) — Installation and method parity for Python environments.
- [Migration from Mem0](#8.3) — Transitioning from Mem0 to Supermemory.
- [Agent Framework Integrations](#8.4) — Middleware for Vercel AI SDK, Mastra, and Pipecat.
- [Memory Router & Model Enhancement](#8.5) — Transparent proxying via `api.supermemory.ai/v3/`.
- [LangChain, LangGraph & Multi-Agent Frameworks](#8.6) — Injecting context into complex agent pipelines.
- [Automation & No-Code Integrations](#8.7) — n8n, Zapier, and ViaSocket support.
- [Voice & Cartesia Integration](#8.8) — Real-time memory for voice agents.

---

## SDK Architecture

The official SDKs bridge the gap between your application code and the Supermemory backend. They handle authentication via API keys, request formatting, and response parsing.

### System Flow: SDK to Backend
This diagram maps the SDK methods to the corresponding backend API entities and endpoints.

```mermaid
graph TD
    subgraph "Application Code"
        [App_Logic]
    end

    subgraph "Supermemory SDKs"
        [supermemory_NPM]
        [supermemory_PyPI]
    end

    subgraph "Backend API (api.supermemory.ai)"
        [POST_v3_add]
        [POST_v4_profile]
        [POST_v3_search]
        [GET_v3_documents_list]
    end

    [App_Logic] -->|"client.add()"| [supermemory_NPM]
    [App_Logic] -->|"client.add()"| [supermemory_PyPI]
    [App_Logic] -->|"client.search.execute()"| [supermemory_NPM]
    [App_Logic] -->|"client.search.execute()"| [supermemory_PyPI]

    [supermemory_NPM] --> [POST_v3_add]
    [supermemory_NPM] --> [POST_v4_profile]
    [supermemory_PyPI] --> [POST_v3_add]
    [supermemory_PyPI] --> [POST_v4_profile]
    
    subgraph "AI Tools Package (@supermemory/tools)"
        [searchMemoriesTool]
        [addMemoryTool]
        [withSupermemory]
    end

    [searchMemoriesTool] --> [POST_v3_search]
    [addMemoryTool] --> [POST_v3_add]
    [withSupermemory] --> [POST_v4_profile]

    style [supermemory_NPM] stroke-width:2px
    style [supermemory_PyPI] stroke-width:2px
```
Sources: [apps/docs/memory-api/sdks/typescript.mdx:18-29](), [apps/docs/memory-api/sdks/python.mdx:21-29](), [packages/tools/src/vercel/index.ts:111-140]()

---

## Available SDKs

### TypeScript/JavaScript SDK
The TypeScript SDK is the primary library for web and Node.js applications. It provides full type safety and is used for both browser extensions and server-side integrations.

**Key Features:**
- **Client Initialization**: Uses `new Supermemory({ apiKey })` [apps/docs/memory-api/sdks/typescript.mdx:18-20]().
- **Core Methods**: Includes `client.add` for storing content, `client.search.execute` for retrieval, and `client.documents.uploadFile` for binary data [apps/docs/memory-api/sdks/typescript.mdx:43-48](), [apps/docs/memory-api/sdks/typescript.mdx:71-82]().
- **Error Handling**: Uses a subclass of `APIError` for 4xx/5xx responses [apps/docs/memory-api/sdks/typescript.mdx:95-103]().

For details, see [TypeScript/JavaScript SDK](#8.1).

### Python SDK
The Python SDK offers parity with the TypeScript version, allowing Python developers to integrate Supermemory into AI agents, data pipelines, and frameworks.

**Key Features:**
- **Installation**: Available via `pip install --pre supermemory` [apps/docs/memory-api/sdks/python.mdx:11]().
- **Async Support**: Includes `AsyncSupermemory` for non-blocking I/O [apps/docs/memory-api/sdks/python.mdx:43-47]().
- **Type Safety**: Uses Pydantic models for responses and TypedDicts for request parameters [apps/docs/memory-api/sdks/python.mdx:64-67]().

For details, see [Python SDK](#8.2).

---

## Framework Integrations

The `@supermemory/tools` package provides specialized middleware and function-calling tools for modern AI frameworks.

### Tool-Calling & Middleware Flow
This diagram shows how the `withSupermemory` middleware intercepts model calls to inject context.

```mermaid
graph LR
    subgraph "AI Framework (e.g. Vercel AI SDK)"
        [generateText]
    end

    subgraph "Supermemory Middleware"
        [withSupermemory]
        [transformParamsWithMemory]
        [saveMemoryAfterResponse]
    end

    [generateText] -->|"intercepts"| [withSupermemory]
    [withSupermemory] -->|"calls"| [transformParamsWithMemory]
    [transformParamsWithMemory] -->|"injects context"| [LLM_Provider]
    [LLM_Provider] -->|"response"| [saveMemoryAfterResponse]
```
Sources: [packages/tools/src/vercel/index.ts:146-187](), [packages/tools/src/vercel/middleware.ts:232-265]()

**Supported Submodules:**
- `@supermemory/tools/ai-sdk`: For Vercel AI SDK, featuring `withSupermemory` and `supermemoryTools` [packages/tools/README.md:20-23]().
- `@supermemory/tools/openai`: For OpenAI SDK integration [packages/tools/README.md:17]().
- `@supermemory/tools/mastra`: For Mastra AI agents [packages/tools/README.md:18]().
- `@supermemory/tools/voltagent`: For VoltAgent configurations [packages/tools/package.json:55]().

---

## Summary Table

| Library | Platform | Exports / Submodules |
| :--- | :--- | :--- |
| `supermemory` | TS/JS | Core client, `toFile` helper [apps/docs/memory-api/sdks/typescript.mdx:66-68]() |
| `supermemory` | Python | `Supermemory`, `AsyncSupermemory` [apps/docs/memory-api/sdks/python.mdx:19-45]() |
| `@supermemory/tools` | TS/JS | `/ai-sdk`, `/openai`, `/mastra`, `/voltagent`, `/claude-memory` [packages/tools/package.json:49-57]() |
| `supermemory-pipecat` | Python | Pipecat voice agent service |
| `supermemory-cartesia` | Python | Cartesia voice model integration |

Sources: [packages/tools/package.json:49-57](), [apps/docs/memory-api/sdks/typescript.mdx:16-18](), [apps/docs/memory-api/sdks/python.mdx:19-45]()

---

# Page: TypeScript/JavaScript SDK

# TypeScript/JavaScript SDK

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [apps/docs/ai-sdk/examples.mdx](apps/docs/ai-sdk/examples.mdx)
- [apps/docs/ai-sdk/infinite-chat.mdx](apps/docs/ai-sdk/infinite-chat.mdx)
- [apps/docs/ai-sdk/memory-tools.mdx](apps/docs/ai-sdk/memory-tools.mdx)
- [apps/docs/cookbook/ai-sdk-integration.mdx](apps/docs/cookbook/ai-sdk-integration.mdx)
- [apps/docs/cookbook/customer-support.mdx](apps/docs/cookbook/customer-support.mdx)
- [apps/docs/cookbook/document-qa.mdx](apps/docs/cookbook/document-qa.mdx)
- [apps/docs/cookbook/personal-assistant.mdx](apps/docs/cookbook/personal-assistant.mdx)
- [apps/docs/memory-api/sdks/native.mdx](apps/docs/memory-api/sdks/native.mdx)
- [apps/docs/memory-api/sdks/openai-plugins.mdx](apps/docs/memory-api/sdks/openai-plugins.mdx)
- [apps/docs/memory-api/sdks/python.mdx](apps/docs/memory-api/sdks/python.mdx)
- [apps/docs/memory-api/sdks/typescript.mdx](apps/docs/memory-api/sdks/typescript.mdx)
- [apps/docs/memory-router/usage.mdx](apps/docs/memory-router/usage.mdx)
- [apps/docs/memory-router/with-memory-api.mdx](apps/docs/memory-router/with-memory-api.mdx)
- [packages/ai-sdk/.npmignore](packages/ai-sdk/.npmignore)
- [packages/ai-sdk/README.md](packages/ai-sdk/README.md)
- [packages/ai-sdk/package.json](packages/ai-sdk/package.json)
- [packages/ai-sdk/src/tools.test.ts](packages/ai-sdk/src/tools.test.ts)
- [packages/ai-sdk/src/tools.ts](packages/ai-sdk/src/tools.ts)
- [packages/ai-sdk/tsconfig.json](packages/ai-sdk/tsconfig.json)
- [packages/ai-sdk/tsdown.config.ts](packages/ai-sdk/tsdown.config.ts)

</details>



This page documents the TypeScript/JavaScript SDK surface for Supermemory, primarily focusing on the `supermemory` core client and the `@supermemory/ai-sdk` framework-integration package. It covers client initialization, core methods, and integration with the Vercel AI SDK and OpenAI SDK.

---

## Packages at a Glance

The SDK ecosystem consists of the core client and framework-specific utilities:

| Package | Install | Purpose |
|---|---|---|
| `supermemory` | `npm install supermemory` | Core API client — `add`, `search`, `documents`, `profile` [apps/docs/memory-api/sdks/typescript.mdx:10]() |
| `@supermemory/ai-sdk` | `npm install @supermemory/ai-sdk` | Vercel AI SDK tools and "Infinite Chat" context management [packages/ai-sdk/package.json:2-16]() |
| `@supermemory/tools` | `npm install @supermemory/tools` | Function calling tools for OpenAI SDK and other frameworks [apps/docs/memory-api/sdks/openai-plugins.mdx:30-31]() |

---

**SDK Entity Map**

```mermaid
graph TD
  pkg1["supermemory"]
  pkg2["@supermemory/ai-sdk"]
  pkg3["@supermemory/tools"]

  pkg1 --> cls["Supermemory (default export)"]
  cls --> m1["client.add()"]
  cls --> m2["client.search.execute()"]
  cls --> m3["client.search.documents()"]
  cls --> m4["client.documents.uploadFile()"]

  pkg2 --> t1["supermemoryTools()"]
  pkg2 --> t2["searchMemoriesTool()"]
  pkg2 --> t3["addMemoryTool()"]
  
  pkg3 --> o1["getToolDefinitions()"]
  pkg3 --> o2["createToolCallExecutor()"]
  
  t1 --> tool1["searchMemories (AI SDK tool)"]
  t1 --> tool2["addMemory (AI SDK tool)"]
```

Sources: [apps/docs/memory-api/sdks/typescript.mdx:16-23](), [packages/ai-sdk/src/tools.ts:27-150](), [apps/docs/memory-api/sdks/openai-plugins.mdx:85-98]()

---

## Core Client (`supermemory`)

### Initialization

```typescript
import Supermemory from 'supermemory';

const client = new Supermemory({
  apiKey: process.env['SUPERMEMORY_API_KEY'], // Defaults to env var if omitted
});
```

Sources: [apps/docs/memory-api/sdks/typescript.mdx:16-20]()

### Core Methods

#### `client.add(params)`
Stores text or content in a memory container.
```typescript
const response = await client.add({
  content: 'User prefers functional programming and TypeScript.',
  containerTags: ['user_123']
});
```
Sources: [apps/docs/memory-api/sdks/typescript.mdx:43-48](), [packages/ai-sdk/src/tools.ts:110-114]()

#### `client.search.execute(params)`
Performs a semantic search across memories.
```typescript
const response = await client.search.execute({ 
  q: 'documents related to python',
  limit: 10
});
```
Sources: [apps/docs/memory-api/sdks/typescript.mdx:23-25](), [packages/ai-sdk/src/tools.ts:70-76]()

#### `client.documents.uploadFile(params)`
Uploads files (PDFs, text, etc.) for indexing. Supports `File` objects, `fs.ReadStream`, or `fetch` Responses.
```typescript
import fs from 'fs';
await client.documents.uploadFile({ 
  file: fs.createReadStream('/path/to/file') 
});
```
Sources: [apps/docs/memory-api/sdks/typescript.mdx:64-82]()

---

## Vercel AI SDK Integration (`@supermemory/ai-sdk`)

The `@supermemory/ai-sdk` package provides two primary ways to integrate memory: **Infinite Chat** and **Memory Tools**.

### 1. Infinite Chat Provider
This approach uses a custom `baseUrl` to route LLM requests through Supermemory's context-enhancement proxy. It automatically injects relevant context without requiring explicit tool calls.

```typescript
import { createOpenAI } from '@ai-sdk/openai'
import { generateText } from 'ai'

const supermemoryOpenai = createOpenAI({
  baseUrl: 'https://api.supermemory.ai/v3/https://api.openai.com/v1',
  apiKey: 'your-openai-api-key',
  headers: {
    'x-supermemory-api-key': 'your-supermemory-api-key',
    'x-sm-conversation-id': 'unique-conversation-id'
  }
})

const result = await generateText({
  model: supermemoryOpenai('gpt-4o'),
  messages: [{ role: 'user', content: 'What are my preferences?' }]
})
```
Sources: [packages/ai-sdk/README.md:32-47]()

### 2. Memory Tools
This provides explicit tools that the LLM can call to `searchMemories` or `addMemory`.

```typescript
import { supermemoryTools } from '@supermemory/ai-sdk'
import { generateText } from 'ai'
import { openai } from '@ai-sdk/openai'

const result = await generateText({
  model: openai('gpt-4o'),
  tools: {
    ...supermemoryTools(process.env.SUPERMEMORY_API_KEY!, {
      containerTags: ['user_123']
    })
  },
  messages: [{ role: 'user', content: 'Remember that I love Oolong tea' }]
})
```
Sources: [packages/ai-sdk/src/tools.ts:27-133](), [packages/ai-sdk/README.md:155-161]()

#### Available Tools Definition
The `supermemoryTools` function returns `tool` objects for use with `generateText` or `streamText`:

| Tool | Description | Implementation |
|---|---|---|
| `searchMemories` | Semantic search for user facts/details | Calls `client.search.execute` with `chunkThreshold: 0.6` [packages/ai-sdk/src/tools.ts:40-90]() |
| `addMemory` | Stores new information about the user | Calls `client.add` with the provided string [packages/ai-sdk/src/tools.ts:92-127]() |

**Data Flow: AI SDK Tool Execution**

```mermaid
sequenceDiagram
  participant LLM as "LLM (GPT-4o/Claude)"
  participant Tool as "supermemoryTools (execute)"
  participant Client as "Supermemory Core Client"
  participant API as "Supermemory API"

  LLM->>Tool: call searchMemories({ informationToGet: "..." })
  Tool->>Client: client.search.execute({ q: "...", containerTags })
  Client->>API: POST /v3/search
  API-->>Client: { results: [...] }
  Client-->>Tool: results
  Tool-->>LLM: { success: true, results: [...] }
```
Sources: [packages/ai-sdk/src/tools.ts:64-89](), [packages/ai-sdk/src/tools.ts:106-126]()

---

## OpenAI SDK Integration (`@supermemory/tools/openai`)

For projects using the official OpenAI SDK instead of the Vercel AI SDK, the `@supermemory/tools` package provides helpers to generate function definitions and execute tool calls.

```typescript
import { getToolDefinitions, createToolCallExecutor } from "@supermemory/tools/openai"
import OpenAI from "openai"

const toolDefinitions = getToolDefinitions()
const executeToolCall = createToolCallExecutor(process.env.SUPERMEMORY_API_KEY!, {
  projectId: "your-project-id",
})

const completion = await client.chat.completions.create({
  model: "gpt-4o",
  messages: [{ role: "user", content: "What do you remember?" }],
  tools: toolDefinitions,
})

if (completion.choices[0]?.message.tool_calls) {
  for (const toolCall of completion.choices[0].message.tool_calls) {
    const result = await executeToolCall(toolCall)
  }
}
```
Sources: [apps/docs/memory-api/sdks/openai-plugins.mdx:85-118]()

---

## Error Handling

The SDK throws specific subclasses of `APIError` for non-success status codes.

| Status Code | Error Type |
|---|---|
| 400 | `BadRequestError` |
| 401 | `AuthenticationError` |
| 429 | `RateLimitError` |
| >=500 | `InternalServerError` |

Sources: [apps/docs/memory-api/sdks/typescript.mdx:111-121]()

### Retries & Timeouts
- **Retries:** By default, the SDK retries 2 times for connection errors, 408, 409, 429, and >=500 errors using exponential backoff [apps/docs/memory-api/sdks/typescript.mdx:123-126]().
- **Timeouts:** Requests time out after 1 minute by default. This is configurable via the `timeout` option in the constructor [apps/docs/memory-api/sdks/typescript.mdx:143-152]().

---

## Configuration Options

`SupermemoryToolsConfig` for AI SDK tools [packages/ai-sdk/src/tools.ts:8-12]():

| Field | Type | Description |
|---|---|---|
| `baseUrl` | `string` | Custom endpoint for self-hosted instances. |
| `containerTags` | `string[]` | Array of tags to scope the search/storage. |
| `projectId` | `string` | Scopes memories to `sm_project_${projectId}` (mutually exclusive with `containerTags`). |

Sources: [packages/ai-sdk/src/tools.ts:8-12](), [packages/ai-sdk/src/tools.ts:36-39]()

---

# Page: Python SDK

# Python SDK

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [packages/agent-framework-python/README.md](packages/agent-framework-python/README.md)
- [packages/openai-sdk-python/LICENSE](packages/openai-sdk-python/LICENSE)
- [packages/openai-sdk-python/README.md](packages/openai-sdk-python/README.md)
- [packages/openai-sdk-python/pyproject.toml](packages/openai-sdk-python/pyproject.toml)
- [packages/openai-sdk-python/src/supermemory_openai/__init__.py](packages/openai-sdk-python/src/supermemory_openai/__init__.py)
- [packages/openai-sdk-python/src/supermemory_openai/exceptions.py](packages/openai-sdk-python/src/supermemory_openai/exceptions.py)
- [packages/openai-sdk-python/src/supermemory_openai/middleware.py](packages/openai-sdk-python/src/supermemory_openai/middleware.py)
- [packages/openai-sdk-python/src/supermemory_openai/tools.py](packages/openai-sdk-python/src/supermemory_openai/tools.py)
- [packages/openai-sdk-python/src/supermemory_openai/utils.py](packages/openai-sdk-python/src/supermemory_openai/utils.py)
- [packages/openai-sdk-python/test_integration.py](packages/openai-sdk-python/test_integration.py)
- [packages/openai-sdk-python/tests/test_middleware.py](packages/openai-sdk-python/tests/test_middleware.py)
- [packages/openai-sdk-python/tests/test_tools.py](packages/openai-sdk-python/tests/test_tools.py)
- [packages/openai-sdk-python/uv.lock](packages/openai-sdk-python/uv.lock)
- [packages/tools/LICENSE](packages/tools/LICENSE)
- [skills/supermemory/LICENSE](skills/supermemory/LICENSE)
- [skills/supermemory/README.md](skills/supermemory/README.md)
- [skills/supermemory/SKILL.md](skills/supermemory/SKILL.md)
- [skills/supermemory/references/api-reference.md](skills/supermemory/references/api-reference.md)
- [skills/supermemory/references/architecture.md](skills/supermemory/references/architecture.md)
- [skills/supermemory/references/quickstart.md](skills/supermemory/references/quickstart.md)
- [skills/supermemory/references/sdk-guide.md](skills/supermemory/references/sdk-guide.md)
- [skills/supermemory/references/use-cases.md](skills/supermemory/references/use-cases.md)

</details>



## Purpose and Scope

The Python SDK provides a high-level interface to the Supermemory Memory API, enabling developers to integrate persistent memory, context management, and user profiles into Python applications. It consists of the core `supermemory` client for direct API interaction and specialized integration packages like `supermemory-openai-sdk` and `supermemory-agent-framework`.

The SDK handles authentication, request formatting, and response parsing for core operations including memory addition, profile retrieval, and semantic search.

Sources: [packages/openai-sdk-python/README.md:3-5](), [packages/openai-sdk-python/src/supermemory_openai/__init__.py:1-42]()

---

## Installation

The SDK is distributed via PyPI and can be installed using standard Python package managers.

### Core SDK
```bash
pip install supermemory
```
Sources: [skills/supermemory/references/sdk-guide.md:21-25]()

### OpenAI Integration SDK
For developers using the OpenAI Python SDK, a specialized integration package provides middleware and tool definitions.

```bash
# Standard installation
pip install supermemory-openai-sdk

# With async support (recommended for aiohttp usage)
pip install 'supermemory-openai-sdk[async]'
```
Sources: [packages/openai-sdk-python/README.md:15-27](), [packages/openai-sdk-python/pyproject.toml:27-35]()

### Agent Framework SDK
For Microsoft Agent Framework users:
```bash
pip install --pre supermemory-agent-framework
```
Sources: [packages/agent-framework-python/README.md:7-19]()

---

## SDK Architecture

The Python ecosystem for Supermemory consists of the base `supermemory` client and various framework-specific SDKs that extend it with middleware and tool capabilities.

### Class Relationship Diagram

```mermaid
graph TD
    subgraph "Base SDK (supermemory)"
        [SMClient] --> [AddMethod]
        [SMClient] --> [ProfileMethod]
        [SMClient] --> [SearchNS]
        [SMClient] --> [AsyncSMClient]
    end

    subgraph "OpenAI Integration (supermemory-openai-sdk)"
        [with_supermemory] -.->|"Wraps"| [SMClient]
        [SupermemoryTools] -->|"Initializes"| [SMClient]
        [with_supermemory] --> [OpenAIMiddlewareOptions]
    end

    subgraph "Agent Framework (supermemory-agent-framework)"
        [SupermemoryChatMiddleware] --> [SupermemoryMiddlewareOptions]
        [SupermemoryContextProvider] --> [SMClient]
    end

    [SMClient]:::code
    [AddMethod]:::code
    [ProfileMethod]:::code
    [SearchNS]:::code
    [AsyncSMClient]:::code
    [with_supermemory]:::code
    [SupermemoryTools]:::code
    [OpenAIMiddlewareOptions]:::code
    [SupermemoryChatMiddleware]:::code
    [SupermemoryContextProvider]:::code

    classDef code font-family:monospace
```
Sources: [packages/openai-sdk-python/src/supermemory_openai/middleware.py:33-40](), [packages/openai-sdk-python/src/supermemory_openai/tools.py:111-137](), [packages/agent-framework-python/README.md:35-107]()

---

## Core Client Usage

The base `Supermemory` client is used for direct data operations and is the foundation for other integrations.

### Initialization
The SDK supports both synchronous and asynchronous clients.
```python
import os
from supermemory import Supermemory, AsyncSupermemory

# Synchronous client
client = Supermemory(
    api_key=os.environ.get("SUPERMEMORY_API_KEY"),
    base_url="https://api.supermemory.ai"
)

# Asynchronous client
async_client = AsyncSupermemory(
    api_key=os.environ.get("SUPERMEMORY_API_KEY")
)
```
Sources: [skills/supermemory/references/sdk-guide.md:46-61]()

### Adding Memories
The `add` method stores content and associates it with a `container_tag` (often a user ID or project ID).
```python
client.add(
    content="User prefers dark mode and Python.",
    container_tag="user_123",
    metadata={"source": "onboarding"}
)
```
Sources: [skills/supermemory/references/sdk-guide.md:81-89]()

### Retrieving Profiles
The `profile` method returns a structured view of the user's long-term (static) and short-term (dynamic) context.
```python
response = client.profile(
    container_tag="user_123",
    q="What are the user's coding preferences?"
)

# Access profile data
print(response["profile"]["static"]) 
print(response["profile"]["dynamic"])
```
Sources: [skills/supermemory/references/sdk-guide.md:157-176]()

---

## OpenAI Integration

The `supermemory-openai-sdk` provides two primary ways to enhance OpenAI-based agents: **Automatic Middleware** and **Manual Tools**.

### 1. Automatic Memory Injection (Middleware)
The `with_supermemory` function wraps an `OpenAI` or `AsyncOpenAI` client. It intercepts `chat.completions.create` calls to fetch memories and inject them into the system prompt.

```python
from openai import AsyncOpenAI
from supermemory_openai import with_supermemory, OpenAIMiddlewareOptions

openai = AsyncOpenAI()
openai_with_memory = with_supermemory(
    openai,
    OpenAIMiddlewareOptions(
        container_tag="user_123",
        custom_id="chat-session-456",
        mode="full",         # Injects profile + search results
        add_memory="always"  # Automatically saves the conversation
    )
)
```
Sources: [packages/openai-sdk-python/README.md:31-66](), [packages/openai-sdk-python/src/supermemory_openai/middleware.py:109-213]()

### 2. Manual Memory Tools
The `SupermemoryTools` class generates tool definitions for OpenAI function calling.

| Tool Name | Implementation | Description |
|-----------|----------------|-------------|
| `search_memories` | `search_memories()` | Semantic recall of user information. |
| `add_memory` | `add_memory()` | Explicitly saves a fact to the user's memory. |

Sources: [packages/openai-sdk-python/src/supermemory_openai/tools.py:59-108](), [packages/openai-sdk-python/src/supermemory_openai/tools.py:173-225]()

---

## Agent Framework Integration

The `supermemory-agent-framework` package integrates with Microsoft's Agent Framework via `SupermemoryChatMiddleware` or `SupermemoryContextProvider`.

### Context Provider Pattern
This is the idiomatic way to add memory in Agent Framework, providing automatic context injection within an `AgentSession`.

```python
from agent_framework.openai import OpenAIResponsesClient
from supermemory_agent_framework import SupermemoryContextProvider

provider = SupermemoryContextProvider(
    container_tag="user-123",
    mode="full",
    store_conversations=True,
)

agent = OpenAIResponsesClient().as_agent(
    name="MemoryAgent",
    context_providers=[provider],
)
```
Sources: [packages/agent-framework-python/README.md:75-107]()

---

## Data Flow: Context Injection

The following diagram illustrates how the middleware (both OpenAI and Agent Framework) bridges the natural language space to code entities during a chat completion.

```mermaid
sequenceDiagram
    participant App as "Python Application"
    participant Wrap as "SupermemoryOpenAIWrapper"
    participant Util as "utils.py"
    participant API as "https://api.supermemory.ai/v4/profile"
    participant OpenAI as "OpenAI API"

    App->>Wrap: chat.completions.create(messages)
    Wrap->>Util: get_last_user_message(messages)
    Wrap->>API: supermemory_profile_search(container_tag, q)
    API-->>Wrap: {profile, searchResults}
    Wrap->>Util: deduplicate_memories()
    Wrap->>Util: convert_profile_to_markdown()
    Wrap->>Wrap: add_system_prompt(augmented_content)
    Wrap->>OpenAI: chat.completions.create(augmented_messages)
    Note right of Wrap: Background: add_memory_tool()
```
Sources: [packages/openai-sdk-python/src/supermemory_openai/middleware.py:109-213](), [packages/openai-sdk-python/src/supermemory_openai/utils.py:199-230](), [packages/openai-sdk-python/src/supermemory_openai/middleware.py:216-232]()

---

## Configuration and Utilities

### Memory Modes
- `"profile"`: Injects all static and dynamic profile memories.
- `"query"`: Only searches for memories relevant to the current user message.
- `"full"`: Combines both profile and query results.

Sources: [packages/openai-sdk-python/README.md:167-199]()

### Background Task Management
When `add_memory="always"`, the middleware tracks background tasks. It is recommended to use the context manager or call `wait_for_background_tasks()` to ensure data persistence.

```python
async with with_supermemory(openai, options) as client:
    await client.chat.completions.create(...)
# Tasks are automatically awaited on exit
```
Sources: [packages/openai-sdk-python/README.md:143-163](), [packages/openai-sdk-python/test_integration.py:141-169]()

---

# Page: Migration from Mem0

# Migration from Mem0

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CONTRIBUTING.md](CONTRIBUTING.md)
- [README.md](README.md)
- [README.zh-CN.md](README.zh-CN.md)
- [apps/docs/cookbook/overview.mdx](apps/docs/cookbook/overview.mdx)
- [apps/docs/memory-api/sdks/overview.mdx](apps/docs/memory-api/sdks/overview.mdx)
- [apps/docs/migration/from-mem0.mdx](apps/docs/migration/from-mem0.mdx)
- [apps/docs/migration/mem0-migration-script.py](apps/docs/migration/mem0-migration-script.py)
- [turbo.json](turbo.json)

</details>



This page covers the process of migrating an existing Mem0 integration to Supermemory, including the conceptual mapping between the two systems, the API translation layer, and the provided migration script. For information about the Supermemory Python SDK used during migration, see [8.2](). For the TypeScript SDK equivalents, see [8.1]().

---

## Conceptual Mapping

Mem0 and Supermemory share the same high-level goal — persisting user memory across AI sessions — but model their data differently. Supermemory uses a "container" approach where all identity fields are flattened into tags.

| Mem0 concept | Supermemory equivalent | Notes |
|---|---|---|
| `user_id` | `container_tags` (e.g. `["user_alice"]`) | Supermemory uses arbitrary string tags instead of a typed user ID field [apps/docs/migration/mem0-migration-script.py:147-149]() |
| `agent_id` | additional `container_tags` (e.g. `["agent_mybot"]`) | Multiple tags can be applied to a single `add()` call [apps/docs/migration/mem0-migration-script.py:152-154]() |
| `app_id` | additional `container_tags` (e.g. `["app_myapp"]`) | Same mechanism as agent scoping [apps/docs/migration/mem0-migration-script.py:157-159]() |
| `run_id` / `session_id` | additional `container_tags` (e.g. `["session_xyz"]`) | Sessions are expressed as tags [apps/docs/migration/mem0-migration-script.py:162-164]() |
| `memory_id` | document `id` / `custom_id` | Supermemory accepts `custom_id` to preserve original IDs [apps/docs/migration/mem0-migration-script.py:181-182]() |
| `client.add(messages=…)` | `client.add(content=…)` | Field name change; Supermemory accepts raw text [apps/docs/migration/from-mem0.mdx:169-187]() |
| `client.search(query=…)` | `client.documents.search(query=…)` | Namespaced under `documents` in the SDK [apps/docs/migration/from-mem0.mdx:195-207]() |
| `client.get_all(user_id=…)` | `client.documents.list(container_tags=[…])` | Namespaced under `documents` [apps/docs/migration/from-mem0.mdx:215-226]() |
| `client.delete(memory_id=…)` | `client.documents.delete(id)` | Namespaced under `documents` [apps/docs/migration/from-mem0.mdx:234-240]() |

**Key structural difference:** Mem0 uses typed identity fields (`user_id`, `agent_id`, `app_id`). Supermemory collapses all of these into a flat list of `container_tags`, which are arbitrary strings. A memory in Supermemory can belong to multiple containers simultaneously [apps/docs/migration/mem0-migration-script.py:144-164]().

---

## Architecture: Before and After Migration

**Migration data flow**

The migration process involves exporting data from Mem0's API, processing it locally, and ingesting it into Supermemory using the Python SDK.

"Migration data flow"
```mermaid
flowchart LR
    subgraph "Mem0_System"
        M0C["MemoryClient"]
        M0E["create_memory_export()"]
        M0G["get_memory_export()"]
        M0J["mem0_export.json"]
    end

    subgraph "Migration_Logic"
        EXP["export_from_mem0()"]
        IMP["import_to_supermemory()"]
        VER["verify_migration()"]
    end

    subgraph "Supermemory_System"
        SMC["Supermemory_client"]
        ADD["client.add()"]
        LIST["client.documents.list()"]
    end

    M0C --> M0E --> M0G --> M0J
    M0J --> EXP --> IMP
    IMP --> ADD
    VER --> LIST
```

Sources: [apps/docs/migration/mem0-migration-script.py:35-112](), [apps/docs/migration/mem0-migration-script.py:115-225](), [apps/docs/migration/mem0-migration-script.py:228-261]()

---

**Conceptual field mapping from Mem0 identity fields to Supermemory container tags**

The script transforms Mem0's specific identity fields into namespaced strings within the `container_tags` array.

"Field Mapping Transformation"
```mermaid
flowchart TD
    subgraph "Mem0_memory_object"
        UID["user_id"]
        AID["agent_id"]
        APPID["app_id"]
        SID["session_id"]
        MID["id"]
        CONT["content"]
        META["metadata"]
    end

    subgraph "Supermemory_add_call"
        CTAGS["container_tags_list"]
        CUST["custom_id"]
        SMCONT["content"]
        SMMETA["metadata_dict"]
    end

    UID -->|"user_{user_id}"| CTAGS
    AID -->|"agent_{agent_id}"| CTAGS
    APPID -->|"app_{app_id}"| CTAGS
    SID -->|"session_{session_id}"| CTAGS
    CTAGS -->|"always_includes"| FIXED["imported_from_mem0"]
    MID --> CUST
    CONT --> SMCONT
    META --> SMMETA
```

Sources: [apps/docs/migration/mem0-migration-script.py:143-165](), [apps/docs/migration/mem0-migration-script.py:181-182](), [apps/docs/migration/mem0-migration-script.py:203-205]()

---

## Migration Script

The migration script lives at `apps/docs/migration/mem0-migration-script.py` and is a self-contained Python program with three distinct phases.

### Prerequisites

```bash
pip install mem0ai supermemory python-dotenv
```

Environment variables required:

| Variable | Required | Description |
|---|---|---|
| `MEM0_API_KEY` | Yes | Mem0 API key |
| `MEM0_ORG_ID` | No | Mem0 organization ID |
| `MEM0_PROJECT_ID` | No | Mem0 project ID |
| `SUPERMEMORY_API_KEY` | Yes | Supermemory API key |

Sources: [apps/docs/migration/mem0-migration-script.py:7-15]()

### Phase 1: `export_from_mem0()`

[apps/docs/migration/mem0-migration-script.py:35-112]()

Initializes a `MemoryClient` from the `mem0` package and calls `create_memory_export()` with a JSON Schema describing the expected shape of the export. The schema requests `id`, `content`, `user_id`, `agent_id`, `app_id`, `run_id`, `metadata`, `created_at`, and `updated_at` for each memory [apps/docs/migration/mem0-migration-script.py:47-71]().

After a 5-second wait (the export job is asynchronous), it calls `get_memory_export(memory_export_id=export_id)` to retrieve the result [apps/docs/migration/mem0-migration-script.py:85-89](). The raw response is written to a timestamped backup file (`mem0_export_YYYYMMDD_HHMMSS.json`) before any further processing [apps/docs/migration/mem0-migration-script.py:92-94]().

### Phase 2: `import_to_supermemory()`

[apps/docs/migration/mem0-migration-script.py:115-225]()

Iterates over the `memories` list from the exported JSON. For each entry:

1. Skips records with empty `content` [apps/docs/migration/mem0-migration-script.py:137-141]().
2. Builds `container_tags` starting with `"imported_from_mem0"`, then appends `user_{user_id}`, `agent_{agent_id}`, `app_{app_id}`, and `session_{session_id}` for any non-`None` identity fields [apps/docs/migration/mem0-migration-script.py:144-164]().
3. Constructs a `custom_id` to preserve the original Mem0 ID or an MD5 hash of content if no ID exists [apps/docs/migration/mem0-migration-script.py:167-172]().
4. Assembles a `metadata` dict preserving `original_id`, `original_created_at`, `original_updated_at`, `original_hash`, `migration_date`, and merges in any existing Mem0 metadata [apps/docs/migration/mem0-migration-script.py:175-205]().
5. Calls `client.add(content=content, container_tags=container_tags, metadata=metadata)` [apps/docs/migration/mem0-migration-script.py:212-216]().
6. Pauses for 0.5 seconds every 10 records to avoid rate limiting [apps/docs/migration/mem0-migration-script.py:218-220]().

Returns a `stats` dict with `imported`, `failed`, and `skipped` counts.

### Phase 3: `verify_migration()`

[apps/docs/migration/mem0-migration-script.py:228-261]()

Calls `client.documents.list(container_tags=["imported_from_mem0"], limit=100)` and compares the returned total items against the expected count from the Mem0 export [apps/docs/migration/mem0-migration-script.py:241-248]().

---

## API Reference: Mem0 → Supermemory

The table below shows each common Mem0 operation and its Supermemory equivalent using the Python SDK.

### Adding a memory

| | Mem0 | Supermemory |
|---|---|---|
| Method | `client.add(messages=…, user_id=…)` | `client.add(content=…, container_tags=[…])` |
| Identity scoping | `user_id="alice"` (typed field) | `container_tags=["user_alice"]` (string tag) |

Sources: [apps/docs/migration/from-mem0.mdx:169-187]()

### Searching memories

| | Mem0 | Supermemory |
|---|---|---|
| Method | `client.search(query=…, user_id=…)` | `client.documents.search(query=…, container_tags=[…])` |
| Return type | list of memory objects | `searchResults` with ranked entries |

Sources: [apps/docs/migration/from-mem0.mdx:195-207]()

### Listing all memories

| | Mem0 | Supermemory |
|---|---|---|
| Method | `client.get_all(user_id=…)` | `client.documents.list(container_tags=[…], limit=…)` |
| Pagination | implicit | `limit` parameter [apps/docs/migration/from-mem0.mdx:221-226]() |

Sources: [apps/docs/migration/from-mem0.mdx:215-226]()

### Deleting a memory

| | Mem0 | Supermemory |
|---|---|---|
| Method | `client.delete(memory_id="mem_123")` | `client.documents.delete("mem_123")` |

Sources: [apps/docs/migration/from-mem0.mdx:234-240]()

---

## Quick One-Script Migration

For small memory sets, the full export and import can be done inline without saving an intermediate file:

[apps/docs/migration/from-mem0.mdx:21-46]()

The inline script:
1. Instantiates `MemoryClient` with a Mem0 API key [apps/docs/migration/from-mem0.mdx:27]().
2. Calls `create_memory_export()` with a minimal schema and empty `filters` [apps/docs/migration/from-mem0.mdx:28-31]().
3. Waits 5 seconds, then calls `get_memory_export()` [apps/docs/migration/from-mem0.mdx:32-33]().
4. Loops over `data["memories"]`, skipping entries without `content` [apps/docs/migration/from-mem0.mdx:37-38]().
5. Calls `supermemory.memories.add()` with `container_tags=["imported_from_mem0"]` [apps/docs/migration/from-mem0.mdx:39-42]().

---

## Step-by-Step Migration Checklist

"Migration Checklist Flow"
```mermaid
flowchart TD
    A["Install packages\nmem0ai supermemory python-dotenv"] --> B["Set environment variables\nMEM0_API_KEY, SUPERMEMORY_API_KEY"]
    B --> C["Run export_from_mem0()\ngets backup JSON file"]
    C --> D{"Large dataset?"}
    D -->|"Yes"| E["Run full script\nmem0-migration-script.py"]
    D -->|"No"| F["Run inline quick script\nfrom from-mem0.mdx"]
    E --> G["Run verify_migration()\nclient.documents.list()"]
    F --> G
    G --> H["Update application code\nreplace Mem0 API calls"]
    H --> I["Remove mem0ai dependency"]
```

Sources: [apps/docs/migration/from-mem0.mdx:50-158](), [apps/docs/migration/mem0-migration-script.py:264-336]()

### Application code changes

After data migration, update your application integration:

1. Replace `from mem0 import MemoryClient` with `from supermemory import Supermemory`.
2. Replace `MemoryClient(api_key=…)` with `Supermemory(api_key=…)`.
3. Replace all `user_id="alice"` arguments with `container_tags=["user_alice"]`.
4. Rename `messages=` parameter to `content=` in `add()` calls.
5. Update search calls from `client.search(query=…)` to `client.documents.search(query=…, container_tags=[…])`.
6. Update list calls from `client.get_all(user_id=…)` to `client.documents.list(container_tags=[…])`.
7. Update delete calls from `client.delete(memory_id=…)` to `client.documents.delete(id)`.

---

## Notes on `container_tags`

The `container_tags` field is central to understanding how Supermemory replaces Mem0's identity system. In Mem0, identity is expressed through typed fields (`user_id`, `agent_id`, `app_id`). In Supermemory, these collapse into a flat, multi-valued `container_tags` list.

- A single memory can belong to multiple containers simultaneously [apps/docs/migration/mem0-migration-script.py:144-164]().
- Filtering with `container_tags` during search or list operations returns memories that match the listed tags [apps/docs/migration/from-mem0.mdx:205]().
- The migration script maps each non-null Mem0 identity field to a namespaced tag string to preserve the original scoping structure [apps/docs/migration/mem0-migration-script.py:147-164]().

For more on how `containerTag` works as a general concept in the API, see [6.4]().

---

## Enterprise Migration

For large-scale or complex migrations, contact [support@supermemory.ai](mailto:support@supermemory.ai) [apps/docs/migration/from-mem0.mdx:244-246](). The migration script's `filters` parameter (passed to `create_memory_export()`) can be used to export subsets of Mem0 data, for example `{"AND": [{"user_id": "specific_user"}]}`, enabling phased migration [apps/docs/migration/mem0-migration-script.py:39]().

Sources: [apps/docs/migration/from-mem0.mdx:244-246](), [apps/docs/migration/mem0-migration-script.py:39]()

---

# Page: Agent Framework Integrations

# Agent Framework Integrations

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [apps/docs/integrations/pipecat.mdx](apps/docs/integrations/pipecat.mdx)
- [packages/agent-framework-python/README.md](packages/agent-framework-python/README.md)
- [packages/openai-sdk-python/README.md](packages/openai-sdk-python/README.md)
- [packages/pipecat-sdk-python/Agents.md](packages/pipecat-sdk-python/Agents.md)
- [packages/pipecat-sdk-python/README.md](packages/pipecat-sdk-python/README.md)
- [packages/pipecat-sdk-python/pyproject.toml](packages/pipecat-sdk-python/pyproject.toml)
- [packages/pipecat-sdk-python/src/supermemory_pipecat/__init__.py](packages/pipecat-sdk-python/src/supermemory_pipecat/__init__.py)
- [packages/pipecat-sdk-python/src/supermemory_pipecat/exceptions.py](packages/pipecat-sdk-python/src/supermemory_pipecat/exceptions.py)
- [packages/pipecat-sdk-python/src/supermemory_pipecat/service.py](packages/pipecat-sdk-python/src/supermemory_pipecat/service.py)
- [packages/pipecat-sdk-python/src/supermemory_pipecat/utils.py](packages/pipecat-sdk-python/src/supermemory_pipecat/utils.py)
- [packages/pipecat-sdk-python/tests/__init__.py](packages/pipecat-sdk-python/tests/__init__.py)
- [packages/pipecat-sdk-python/tests/test_empty_profile.py](packages/pipecat-sdk-python/tests/test_empty_profile.py)
- [skills/supermemory/LICENSE](skills/supermemory/LICENSE)
- [skills/supermemory/README.md](skills/supermemory/README.md)
- [skills/supermemory/SKILL.md](skills/supermemory/SKILL.md)
- [skills/supermemory/references/api-reference.md](skills/supermemory/references/api-reference.md)
- [skills/supermemory/references/architecture.md](skills/supermemory/references/architecture.md)
- [skills/supermemory/references/quickstart.md](skills/supermemory/references/quickstart.md)
- [skills/supermemory/references/sdk-guide.md](skills/supermemory/references/sdk-guide.md)
- [skills/supermemory/references/use-cases.md](skills/supermemory/references/use-cases.md)

</details>



Supermemory provides native Python SDKs for popular agentic and conversational AI frameworks, specifically **Microsoft Agent Framework**, **Pipecat**, and **OpenAI-compatible agent frameworks**. These integrations allow developers to inject persistent user memory, profiles, and semantic search capabilities directly into AI pipelines with minimal configuration.

## 1. Microsoft Agent Framework Integration (`supermemory-agent-framework`)

The `supermemory-agent-framework` package provides multiple patterns for adding memory to agents built with Microsoft's [Agent Framework](https://github.com/microsoft/agent-framework). It supports automatic context injection via middleware or context providers, as well as explicit memory management through tools.

### 1.1 Installation

Install the package via pip or uv. Note that the `--pre` flag is required due to dependencies on pre-release Azure packages [packages/agent-framework-python/README.md:15-21]().

```bash
pip install --pre supermemory-agent-framework
# For async support
pip install 'supermemory-agent-framework[async]'
```

### 1.2 Integration Patterns

The SDK offers three primary ways to integrate memory [packages/agent-framework-python/README.md:33-139]():

| Pattern | Class | Use Case |
| :--- | :--- | :--- |
| **Middleware** | `SupermemoryChatMiddleware` | Automatic injection for standard agent runs. |
| **Context Provider** | `SupermemoryContextProvider` | Idiomatic integration for `AgentSession` based workflows. |
| **Tools** | `SupermemoryTools` | Explicit memory search and storage by the agent itself. |

**Agent Framework Data Flow**
"Microsoft Agent Framework Memory Injection"
```mermaid
graph TD
    subgraph "Agent Framework Pipeline"
        UserMsg["Agent.run(message)"] --> Provider["SupermemoryContextProvider"]
        Provider --> Middleware["SupermemoryChatMiddleware"]
        Middleware --> LLM["OpenAIResponsesClient"]
    end

    subgraph "Supermemory Services"
        ProfileAPI["POST /v4/profile"]
        AddAPI["POST /v3/add"]
    end

    Provider -- "Fetch Context" --> ProfileAPI
    Middleware -- "Inject/Store" --> ProfileAPI
    Middleware -- "Background Save" --> AddAPI
    LLM -- "Explicit Tool Call" --> Tools["SupermemoryTools"]
    Tools -- "Search/Add" --> ProfileAPI
```
**Sources:** [packages/agent-framework-python/README.md:45-107](), [packages/agent-framework-python/README.md:141-180]()

## 2. Pipecat Integration (`supermemory-pipecat`)

The `supermemory-pipecat` package provides a way to add persistent memory to voice and conversational AI applications built with [Pipecat](https://github.com/pipecat-ai/pipecat). It functions as a `FrameProcessor` that intercepts conversation context and enhances it with relevant memories [packages/pipecat-sdk-python/src/supermemory_pipecat/service.py:37-42]().

### 2.1 Installation and Basic Setup

```bash
pip install supermemory-pipecat
```

Initialize the `SupermemoryPipecatService` and add it to your pipeline [packages/pipecat-sdk-python/src/supermemory_pipecat/__init__.py:7-25]().

```python
from supermemory_pipecat import SupermemoryPipecatService

memory = SupermemoryPipecatService(
    api_key=os.getenv("SUPERMEMORY_API_KEY"),
    user_id="user-123",  # Scopes memories to this user
)

pipeline = Pipeline([
    transport.input(),
    stt,
    user_context,
    memory,  # Intercepts frames and injects memory
    llm,
    transport.output(),
])
```
**Sources:** [packages/pipecat-sdk-python/README.md:19-35](), [packages/pipecat-sdk-python/src/supermemory_pipecat/service.py:71-106]()

### 2.2 Data Flow and Implementation

The service listens for `LLMContextFrame` or `OpenAILLMContextFrame` objects [packages/pipecat-sdk-python/src/supermemory_pipecat/service.py:17-20](). It retrieves memories via the `_retrieve_memories` method, which calls the Supermemory profile endpoint [packages/pipecat-sdk-python/src/supermemory_pipecat/service.py:122-147]().

**Pipecat Memory Flow Diagram**
"Pipecat Service Architecture"
```mermaid
graph TD
    subgraph "Pipecat Pipeline"
        Input["transport.input()"] --> Context["LLMContext (Aggregator)"]
        Context --> SMService["SupermemoryPipecatService"]
        SMService --> LLM["LLM Service"]
    end

    subgraph "Supermemory Cloud"
        API["/v4/profile API"]
        Store["/v3/add API"]
    end

    SMService -- "1. _retrieve_memories(query)" --> API
    SMService -- "2. _enhance_context_with_memories()" --> SMService
    SMService -- "3. _store_messages() (Background)" --> Store
```
**Sources:** [packages/pipecat-sdk-python/src/supermemory_pipecat/service.py:37-52](), [packages/pipecat-sdk-python/README.md:74-80]()

## 3. OpenAI Agent Integration (`supermemory-openai-sdk`)

The `supermemory-openai-sdk` provides middleware and toolsets for building memory-augmented agents using OpenAI's Python SDK [packages/openai-sdk-python/README.md:1-5]().

### 3.1 Context Injection via Middleware

The framework uses `with_supermemory()` to wrap an `OpenAI` or `AsyncOpenAI` client [packages/openai-sdk-python/README.md:33-54](). 
- **Profile Mode**: Injects static and dynamic profile facts [packages/openai-sdk-python/README.md:171-179]().
- **Query Mode**: Searches for memories relevant to the current message [packages/openai-sdk-python/README.md:181-189]().
- **Full Mode**: Combines both profile and query-based search [packages/openai-sdk-python/README.md:191-199]().

### 3.2 SupermemoryTools

For agents that require autonomous memory management, the integration provides `SupermemoryTools` [packages/openai-sdk-python/README.md:232-235](). These allow the agent to explicitly call functions to:
- `add_memory`: Save facts to the user's memory [packages/openai-sdk-python/README.md:95-97]().
- `search_memories`: Perform semantic search over past interactions [packages/openai-sdk-python/README.md:104-108]().

## 4. Technical Entity Mapping

The following diagram bridges the framework concepts to the specific code entities used in the Python integrations.

**Code Entity Mapping Diagram**
"Agent Integration Entity Map"
```mermaid
graph LR
    subgraph "Natural Language Space"
        UserIntent["'User wants to know about X'"]
        UserFact["'User prefers Python over JS'"]
    end

    subgraph "Framework Entity Space"
        ServiceClass["SupermemoryPipecatService"]
        Middleware["SupermemoryChatMiddleware"]
        UtilDedupe["deduplicate_memories()"]
        UtilFormat["format_memories_to_text()"]
        Client["AsyncSupermemory"]
    end

    subgraph "API Space"
        V4Profile["POST /v4/profile"]
        V3Add["POST /v3/add"]
    end

    UserIntent --> ServiceClass
    UserIntent --> Middleware
    ServiceClass -- "Uses" --> Client
    Middleware -- "Uses" --> Client
    Client -- "Calls" --> V4Profile
    V4Profile -- "Returns JSON" --> UtilDedupe
    UtilDedupe --> UtilFormat
    UtilFormat -- "Injected Context" --> UserFact
    ServiceClass -- "Background Sync" --> V3Add
    Middleware -- "Background Sync" --> V3Add
```
**Sources:** [packages/pipecat-sdk-python/src/supermemory_pipecat/service.py:122-148](), [packages/pipecat-sdk-python/src/supermemory_pipecat/utils.py:52-96](), [packages/agent-framework-python/README.md:247-250]()

## 5. Key Utilities and Configuration

| Class/Function | Role |
| :--- | :--- |
| `InputParams` | Configures `search_limit`, `search_threshold`, and `mode` in Pipecat [packages/pipecat-sdk-python/src/supermemory_pipecat/service.py:54-70](). |
| `SupermemoryMiddlewareOptions` | Configures `add_memory` (always/never) and `mode` for Agent Framework [packages/agent-framework-python/README.md:184-226](). |
| `deduplicate_memories` | Merges profile and search results with priority: Static > Dynamic > Search [packages/pipecat-sdk-python/src/supermemory_pipecat/utils.py:52-58](). |
| `format_memories_to_text` | Formats memories into a system prompt string with relative timestamps [packages/pipecat-sdk-python/src/supermemory_pipecat/utils.py:90-134](). |

**Sources:** [packages/pipecat-sdk-python/src/supermemory_pipecat/service.py:54-70](), [packages/pipecat-sdk-python/src/supermemory_pipecat/utils.py:52-134](), [packages/agent-framework-python/README.md:184-226]()

---

# Page: Memory Router & Model Enhancement

# Memory Router & Model Enhancement

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [apps/docs/ai-sdk/examples.mdx](apps/docs/ai-sdk/examples.mdx)
- [apps/docs/ai-sdk/infinite-chat.mdx](apps/docs/ai-sdk/infinite-chat.mdx)
- [apps/docs/ai-sdk/memory-tools.mdx](apps/docs/ai-sdk/memory-tools.mdx)
- [apps/docs/ai-sdk/overview.mdx](apps/docs/ai-sdk/overview.mdx)
- [apps/docs/ai-sdk/user-profiles.mdx](apps/docs/ai-sdk/user-profiles.mdx)
- [apps/docs/cookbook/ai-sdk-integration.mdx](apps/docs/cookbook/ai-sdk-integration.mdx)
- [apps/docs/cookbook/customer-support.mdx](apps/docs/cookbook/customer-support.mdx)
- [apps/docs/cookbook/document-qa.mdx](apps/docs/cookbook/document-qa.mdx)
- [apps/docs/cookbook/personal-assistant.mdx](apps/docs/cookbook/personal-assistant.mdx)
- [apps/docs/integrations/ai-sdk.mdx](apps/docs/integrations/ai-sdk.mdx)
- [apps/docs/integrations/openai.mdx](apps/docs/integrations/openai.mdx)
- [apps/docs/integrations/voltagent.mdx](apps/docs/integrations/voltagent.mdx)
- [apps/docs/memory-api/sdks/openai-plugins.mdx](apps/docs/memory-api/sdks/openai-plugins.mdx)
- [apps/docs/memory-router/usage.mdx](apps/docs/memory-router/usage.mdx)
- [apps/docs/memory-router/with-memory-api.mdx](apps/docs/memory-router/with-memory-api.mdx)
- [apps/docs/migration/tools-v2-upgrade.mdx](apps/docs/migration/tools-v2-upgrade.mdx)
- [packages/ai-sdk/README.md](packages/ai-sdk/README.md)
- [packages/ai-sdk/src/tools.test.ts](packages/ai-sdk/src/tools.test.ts)
- [packages/ai-sdk/src/tools.ts](packages/ai-sdk/src/tools.ts)
- [packages/tools/src/shared/memory-client.ts](packages/tools/src/shared/memory-client.ts)
- [packages/tools/src/shared/types.ts](packages/tools/src/shared/types.ts)

</details>



The Memory Router is a transparent proxy layer provided by Supermemory that allows developers to route standard LLM requests through the Supermemory infrastructure. This architecture enables "drop-in" memory capabilities by intercepting requests, injecting relevant user context (memories and profiles), and enhancing the model's response without requiring complex changes to existing application logic.

## Overview and Purpose

The Memory Router acts as a middleware between the application and the LLM provider (OpenAI, Anthropic, Gemini, Groq). By changing the base URL of the LLM client to route through `api.supermemory.ai/v3/`, developers can leverage Supermemory's context-extender features.

Key benefits include:
*   **Transparent Context Injection**: Automatically fetches and injects memories based on the conversation history.
*   **User Profiling**: Injects stable facts (static) and recent activity (dynamic) into the system prompt [apps/docs/ai-sdk/user-profiles.mdx:39-46]().
*   **Multi-Provider Support**: Unified interface for leading LLM providers [packages/ai-sdk/README.md:90-103]().
*   **Zero-Config RAG**: Context is managed automatically via middleware or proxy without manual vector search logic [apps/docs/ai-sdk/overview.mdx:7-11]().

## Implementation & Data Flow

The router functions by intercepting the standard chat completion payload. It uses identifiers to map requests to specific `containerTag` scopes, ensuring data isolation and relevant context retrieval.

### Request Routing Architecture

The following diagram illustrates how a request moves from a client through the Memory Router to the final LLM provider.

**LLM Request Enrichment Flow**
```mermaid
graph TD
    subgraph "Client_Space"
        A["LLM_Client_SDK"]
    end

    subgraph "Supermemory_Router_v3"
        B["Proxy_Entry_Point"]
        C["Context_Extender_Engine"]
        D["buildMemoriesText"]
        E["supermemoryProfileSearch"]
    end

    subgraph "LLM_Provider_Space"
        F["OpenAI_API"]
        G["Anthropic_API"]
        H["Gemini_Groq_API"]
    end

    A -- "BaseURL_v3_plus_Headers" --> B
    B --> C
    C -- "internal_call" --> D
    D -- "POST /v4/profile" --> E
    D & E --> C
    C -- "Enriched_Prompt" --> F
    C -- "Enriched_Prompt" --> G
    C -- "Enriched_Prompt" --> H
    F & G & H --> B
    B --> A
```
Sources: [packages/ai-sdk/README.md:32-39](), [packages/tools/src/shared/memory-client.ts:24-30](), [packages/tools/src/shared/memory-client.ts:88-90]()

## Configuration

To use the Memory Router, the client must be configured with the Supermemory base URL and the necessary identification headers.

### Supported Providers
The router supports leading providers by prepending the Supermemory proxy URL to the provider's API endpoint:
*   **OpenAI**: Set `baseURL` to `https://api.supermemory.ai/v3/https://api.openai.com/v1` [packages/ai-sdk/README.md:33]().
*   **Anthropic**: Use `https://api.supermemory.ai/v3/https://api.anthropic.com/v1`.
*   **Groq/Gemini**: Supported by routing through the unified `/v3/` prefix.

### Identifying Users and Conversations
Supermemory identifies the context to inject using several mechanisms:

1.  **`x-sm-user-id` header**: Maps to the `containerTag` for memory isolation.
2.  **`x-supermemory-api-key`**: The Supermemory API key used for authentication [packages/ai-sdk/README.md:36]().
3.  **`x-sm-conversation-id`**: Maps to the `customId` to track specific threads and enable automatic backfilling [packages/ai-sdk/README.md:37]().

| Header | Description |
| :--- | :--- |
| `Authorization` | Standard provider API key (e.g., OpenAI Key) [packages/ai-sdk/README.md:34](). |
| `x-supermemory-api-key` | Supermemory API key for context access [packages/ai-sdk/README.md:36](). |
| `x-sm-conversation-id` | Groups messages into a specific document [packages/ai-sdk/README.md:37](). |

Sources: [packages/ai-sdk/README.md:31-40](), [apps/docs/integrations/ai-sdk.mdx:53-59]()

## Model Enhancement (Context Extender)

The Model Enhancement feature uses a "Context Extender" pattern. When a request hits the router or middleware, the system performs internal operations to "enhance" the prompt.

### Enhancement Components

1.  **Memory Extraction**: Conversations are saved as memories automatically when `addMemory` is set to `"always"` (the default in v2) [apps/docs/migration/tools-v2-upgrade.mdx:137-140]().
2.  **User Profiles**: The system fetches `static` facts (stable) and `dynamic` facts (recent activity) [packages/tools/src/shared/types.ts:70-82]().
3.  **Context Building**: The `buildMemoriesText` function formats retrieved data into a string for system prompt injection [packages/tools/src/shared/memory-client.ts:88-100]().

### Data Entity Mapping

This diagram bridges the conceptual "Enhancement" to the specific code entities used within the `@supermemory/tools` and `@supermemory/ai-sdk` packages.

**Context Extender Entity Map**
```mermaid
classDiagram
    class withSupermemory {
        <<Middleware>>
        +containerTag: string
        +customId: string
        +mode: MemoryMode
    }
    class buildMemoriesText {
        <<Logic>>
        +deduplicateMemories()
        +convertProfileToMarkdown()
    }
    class supermemoryProfileSearch {
        <<API_Client>>
        +POST_v4_profile()
    }
    class ProfileStructure {
        <<Data_Entity>>
        +static: Array
        +dynamic: Array
        +searchResults: Array
    }

    withSupermemory ..> buildMemoriesText : "Calls to generate prompt"
    buildMemoriesText ..> supermemoryProfileSearch : "Fetches data"
    supermemoryProfileSearch ..> ProfileStructure : "Returns"
```
Sources: [packages/tools/src/shared/memory-client.ts:88-108](), [packages/tools/src/shared/types.ts:70-90](), [apps/docs/integrations/ai-sdk.mdx:42-45]()

## Integration Patterns

### Direct Middleware Usage
Instead of the transparent proxy, developers can use the `withSupermemory` middleware which performs the same enhancement logic locally before calling the LLM.

```typescript
const modelWithMemory = withSupermemory(openai("gpt-4"), {
  containerTag: "user-123",
  customId: "conversation-456",
  mode: "full" // Combines profile and query search
})
```
Sources: [apps/docs/ai-sdk/user-profiles.mdx:17-26](), [apps/docs/ai-sdk/user-profiles.mdx:110-118]()

### Comparison: Router vs. Tools
Supermemory supports two primary integration patterns:
*   **Infinite Chat (Router/Middleware)**: Context is injected into the system prompt automatically. Best for general personalization [packages/ai-sdk/README.md:24-26]().
*   **Memory Tools**: The AI model explicitly calls tools like `searchMemories` or `addMemory` to interact with Supermemory. Best for agents needing explicit control [packages/ai-sdk/src/tools.ts:27-34]().

Sources: [packages/ai-sdk/README.md:17-22](), [apps/docs/integrations/ai-sdk.mdx:24-30]()

---

# Page: LangChain, LangGraph & Multi-Agent Frameworks

# LangChain, LangGraph & Multi-Agent Frameworks

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [apps/docs/ai-sdk/examples.mdx](apps/docs/ai-sdk/examples.mdx)
- [apps/docs/ai-sdk/infinite-chat.mdx](apps/docs/ai-sdk/infinite-chat.mdx)
- [apps/docs/ai-sdk/memory-tools.mdx](apps/docs/ai-sdk/memory-tools.mdx)
- [apps/docs/cookbook/ai-sdk-integration.mdx](apps/docs/cookbook/ai-sdk-integration.mdx)
- [apps/docs/cookbook/customer-support.mdx](apps/docs/cookbook/customer-support.mdx)
- [apps/docs/cookbook/document-qa.mdx](apps/docs/cookbook/document-qa.mdx)
- [apps/docs/cookbook/personal-assistant.mdx](apps/docs/cookbook/personal-assistant.mdx)
- [apps/docs/images/langgraph.svg](apps/docs/images/langgraph.svg)
- [apps/docs/integrations/langgraph.mdx](apps/docs/integrations/langgraph.mdx)
- [apps/docs/memory-api/sdks/openai-plugins.mdx](apps/docs/memory-api/sdks/openai-plugins.mdx)
- [apps/docs/memory-router/usage.mdx](apps/docs/memory-router/usage.mdx)
- [apps/docs/memory-router/with-memory-api.mdx](apps/docs/memory-router/with-memory-api.mdx)
- [packages/ai-sdk/README.md](packages/ai-sdk/README.md)
- [packages/ai-sdk/src/tools.test.ts](packages/ai-sdk/src/tools.test.ts)
- [packages/ai-sdk/src/tools.ts](packages/ai-sdk/src/tools.ts)

</details>



This page documents the integration of Supermemory into advanced AI orchestration frameworks including LangChain, LangGraph, CrewAI, Agno, and the OpenAI Agents SDK. These integrations allow developers to inject persistent user context into agents, store agentic outputs as long-term memories, and utilize Supermemory's hybrid search as a tool within multi-agent pipelines.

## Multi-Agent Context Flow

In multi-agent systems, Supermemory acts as a centralized "Context Layer." Instead of passing massive message histories between agents, agents can query Supermemory for specific user preferences or past project states.

### Implementation Logic
1.  **User Identification**: Every agent request is scoped using a `containerTags` or `projectId` which is used to isolate memories [packages/ai-sdk/src/tools.ts:36-39]().
2.  **Context Injection**: Agents fetch user profiles containing static facts (permanent information) and dynamic context (recent activity) to set the system prompt [apps/docs/integrations/langgraph.mdx:64-81]().
3.  **Memory Synthesis**: As agents complete tasks, they use the `addMemory` tool to persist findings for future runs [packages/ai-sdk/src/tools.ts:92-127]().

### Data Flow Diagram: Multi-Agent Memory
This diagram shows how a Coordinator agent uses Supermemory to inform specialized workers.

```mermaid
graph TD
    User["User Interaction"] --> Coordinator["Coordinator Agent"]
    Coordinator -- "searchMemories" --> SM_SDK["Supermemory SDK"]
    SM_SDK -- "client.search.execute()" --> Backend["Supermemory API"]
    Backend -- "Relevant Context + Profile" --> Coordinator
    Coordinator -- "Task + Context" --> WorkerA["Researcher Agent"]
    Coordinator -- "Task + Context" --> WorkerB["Writer Agent"]
    WorkerA -- "addMemory" --> SM_SDK
    WorkerB -- "addMemory" --> SM_SDK
    SM_SDK -- "client.add()" --> Backend

    subgraph "Code Entity Space"
        SM_SDK["Supermemory Class"]
        Backend["api.supermemory.ai"]
    end
```
Sources: [packages/ai-sdk/src/tools.ts:27-133](), [apps/docs/integrations/langgraph.mdx:59-92]()

---

## LangChain & LangGraph Integration

Supermemory integrates with LangChain through custom Tool definitions. In LangGraph, Supermemory is typically implemented as a node that manages state persistence or as a tool available to the graph's agents.

### Tool Configuration
The `@supermemory/ai-sdk` package provides tools compatible with the Vercel AI SDK and LangChain. The `supermemoryTools` helper initializes a suite of memory operations [packages/ai-sdk/src/tools.ts:27-30]().

| Tool Name | Purpose | Key Parameters |
| :--- | :--- | :--- |
| `searchMemories` | Semantic retrieval of user-specific data [packages/ai-sdk/src/tools.ts:40-42]() | `informationToGet`, `limit`, `includeFullDocs` |
| `addMemory` | Persisting new facts or short sentences [packages/ai-sdk/src/tools.ts:92-94]() | `memory` |

### LangGraph Implementation
In LangGraph, you can define a state that includes a `user_id` to scope all Supermemory calls within nodes [apps/docs/integrations/langgraph.mdx:55-57]().

```mermaid
sequenceDiagram
    participant LG as StateGraph Node
    participant SM as Supermemory Client
    participant LLM as ChatOpenAI

    LG->>SM: memory.profile(container_tag=user_id, q=query)
    SM-->>LG: return profile (static + dynamic)
    LG->>LLM: SystemMessage(context) + messages
    LLM-->>LG: AIMessage
    LG->>SM: memory.add(content=interaction, container_tag=user_id)
```
Sources: [apps/docs/integrations/langgraph.mdx:59-92](), [apps/docs/integrations/langgraph.mdx:183-221]()

---

## OpenAI SDK & Agents Integration

Supermemory provides specialized support for OpenAI function calling via the `@supermemory/tools/openai` module (JavaScript/TypeScript) and the `supermemory-openai-sdk` (Python).

### Function Calling Pipeline
1.  **Tool Definitions**: Use `getToolDefinitions()` (TS) or `tools.get_tool_definitions()` (Python) to get OpenAI-compatible function objects [apps/docs/memory-api/sdks/openai-plugins.mdx:67-68](), [apps/docs/memory-api/sdks/openai-plugins.mdx:93-94]().
2.  **Execution Handlers**: Use `execute_memory_tool_calls` (Python) or `createToolCallExecutor` (TS) to process the tool outputs returned by the LLM [apps/docs/memory-api/sdks/openai-plugins.mdx:72-76](), [apps/docs/memory-api/sdks/openai-plugins.mdx:96-98]().

### Configuration & Scoping
You can scope an entire agentic session to a specific project or user using the `SupermemoryToolsConfig` [packages/ai-sdk/src/tools.ts:8-12]().
*   `projectId`: Automatically mapped to a container tag `sm_project_{id}` [packages/ai-sdk/src/tools.ts:36-37]().
*   `containerTags`: A list of strings used to partition memory [packages/ai-sdk/src/tools.ts:38]().

Sources: [apps/docs/memory-api/sdks/openai-plugins.mdx:42-82](), [packages/ai-sdk/src/tools.ts:8-39]()

---

## Python Multi-Agent Support

For Python-based frameworks like CrewAI, Agno, or LangGraph Python, the `supermemory` Python package provides a standard interface for memory operations.

### Core Memory Operations
Agents can be given access to specific methods from the `Supermemory` class to manage their own long-term state [apps/docs/integrations/langgraph.mdx:53-54]().

```python
from supermemory import Supermemory

memory = Supermemory()

# Search memories across sessions
results = memory.search.memories(
    q="project goals",
    container_tag="agent_001",
    search_mode="hybrid"
)

# Store new findings
memory.add(
    content="User prefers async patterns in Python",
    container_tag="agent_001"
)
```
Sources: [apps/docs/integrations/langgraph.mdx:132-147](), [apps/docs/integrations/langgraph.mdx:153-163]()

### Profile-Driven Personalization
Supermemory automatically builds user profiles from stored memories, which can be injected into agent system prompts to provide immediate context without manual tool calls [apps/docs/integrations/langgraph.mdx:115-128]().

*   **Static facts**: Long-term information like preferences or expertise [apps/docs/integrations/langgraph.mdx:117]().
*   **Dynamic context**: Recent activity and current focus [apps/docs/integrations/langgraph.mdx:118]().

Sources: [apps/docs/integrations/langgraph.mdx:113-128](), [apps/docs/integrations/langgraph.mdx:201-220]()

---

# Page: Automation & No-Code Integrations

# Automation & No-Code Integrations

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [apps/docs/add-memories/overview.mdx](apps/docs/add-memories/overview.mdx)
- [apps/docs/document-operations.mdx](apps/docs/document-operations.mdx)
- [apps/docs/images/viaSocket-supermemory-auth.png](apps/docs/images/viaSocket-supermemory-auth.png)
- [apps/docs/images/viaSocket-supermemory-connect.png](apps/docs/images/viaSocket-supermemory-connect.png)
- [apps/docs/images/viaSocket-supermemory-trigger.png](apps/docs/images/viaSocket-supermemory-trigger.png)
- [apps/docs/images/viasocket-icon-ico.ico](apps/docs/images/viasocket-icon-ico.ico)
- [apps/docs/images/viasocket-supermemory-action.png](apps/docs/images/viasocket-supermemory-action.png)
- [apps/docs/images/viasocket-supermemory-configured-trigger.png](apps/docs/images/viasocket-supermemory-configured-trigger.png)
- [apps/docs/images/viasocket-supermemory-connection.png](apps/docs/images/viasocket-supermemory-connection.png)
- [apps/docs/images/viasocket-supermemory-go-live.png](apps/docs/images/viasocket-supermemory-go-live.png)
- [apps/docs/integrations/convex.mdx](apps/docs/integrations/convex.mdx)
- [apps/docs/integrations/viasocket.mdx](apps/docs/integrations/viasocket.mdx)
- [apps/docs/memory-api/creation/adding-memories.mdx](apps/docs/memory-api/creation/adding-memories.mdx)
- [apps/docs/memory-api/ingesting.mdx](apps/docs/memory-api/ingesting.mdx)
- [apps/docs/memory-api/introduction.mdx](apps/docs/memory-api/introduction.mdx)
- [apps/docs/memory-api/overview.mdx](apps/docs/memory-api/overview.mdx)
- [apps/docs/memory-api/searching/searching-memories.mdx](apps/docs/memory-api/searching/searching-memories.mdx)
- [apps/docs/memory-api/track-progress.mdx](apps/docs/memory-api/track-progress.mdx)
- [apps/docs/migration/from-zep.mdx](apps/docs/migration/from-zep.mdx)
- [apps/docs/n8n.mdx](apps/docs/n8n.mdx)
- [apps/docs/update-delete-memories/overview.mdx](apps/docs/update-delete-memories/overview.mdx)
- [apps/docs/zapier.mdx](apps/docs/zapier.mdx)

</details>



Supermemory provides native support and implementation patterns for automation and no-code platforms, allowing users to build persistent memory layers into automated workflows. This enables AI agents and automation scripts to maintain context across sessions, build dynamic user profiles, and perform hybrid searches without manual data management.

## Convex Integration

Supermemory acts as a persistent memory layer for Convex applications, which do not have built-in stateful memory for AI.

### Core Implementation
Integration is achieved by creating Convex actions that wrap the Supermemory SDK. This allows Convex functions to interact with the Supermemory backend for adding, searching, and profiling memories.

| Operation | Convex Helper Function | Supermemory Method |
| :--- | :--- | :--- |
| **Add Memory** | `addMemory` | `memory.add` |
| **Search** | `searchMemories` | `memory.search.memories` |
| **User Profile** | `getProfile` | `memory.profile` |

Sources: [apps/docs/integrations/convex.mdx:41-85]()

### AI SDK Middleware in Convex
For chat-based applications, the `withSupermemory` middleware from `@supermemory/tools/ai-sdk` can be used within a Convex action to automatically inject context and save conversation turns.

Sources: [apps/docs/integrations/convex.mdx:94-121]()

### Data Flow: Convex to Supermemory
The following diagram illustrates how a Convex action interacts with the `Supermemory` client and optionally syncs data to a local Convex table.

**Convex Integration Data Flow**
```mermaid
graph TD
    subgraph "Convex Action Space"
        A["action handler (convex/memory.ts)"] --> B["Supermemory Client (SDK)"]
        A --> C["ctx.runMutation"]
    end

    subgraph "Code Entity Space"
        B -- "memory.add()" --> D["POST /v3/documents"]
        C -- "api.memory.storeMemory" --> E["ctx.db.insert('memories')"]
    end

    subgraph "Storage"
        D --> F["Supermemory Backend"]
        E --> G["Convex Table: memories"]
    end
```
Sources: [apps/docs/integrations/convex.mdx:49-85](), [apps/docs/integrations/convex.mdx:144-189](), [apps/docs/memory-api/ingesting.mdx:75-75]()

---

## n8n Integration

Supermemory integrates with n8n using the **HTTP Request** node to build intelligent automation agents.

### Setup and Authentication
1. **Node Type**: Use the **HTTP Request** node (Core).
2. **Authentication**: Select **Generic Credential Type** → **Bearer Auth**. Paste the API key from the [Supermemory Console](https://console.supermemory.ai) into the Token field.
3. **Endpoint**: Use `https://api.supermemory.ai/v3/documents` for ingestion or `https://api.supermemory.ai/v4/search` for retrieval.

Sources: [apps/docs/n8n.mdx:17-30]()

### Implementation Pattern: Gmail Archive
A common pattern is archiving Gmail snippets into Supermemory.
*   **Trigger**: Gmail "Message Received" node.
*   **Action**: HTTP Request node with JSON body mapping `content` to `{{ $json.snippet }}` and `containerTag` to `gmail`.

Sources: [apps/docs/n8n.mdx:36-66]()

---

## Zapier Integration

Zapier integration is typically handled via the **Code by Zapier** block using Python to interact with the Supermemory API.

### Implementation Logic
```mermaid
graph TD
    subgraph "Zapier Workflow"
        Z1["Trigger: New Gmail Email"] --> Z2["Action: Code by Zapier (Python)"]
    end

    subgraph "Code Entity Space"
        Z2 -- "requests.post()" --> API["POST /v3/documents"]
        API -- "Payload: {content, containerTag}" --> SM["Supermemory Backend"]
    end
```
Sources: [apps/docs/zapier.mdx:14-51]()

### Configuration
Users map input data (e.g., Gmail raw snippet) to a variable like `content` in the Zapier UI, which is then accessed in the Python script via `inputData['content']`.

Sources: [apps/docs/zapier.mdx:25-53]()

---

## viaSocket Integration

viaSocket allows connecting Supermemory to third-party services through visual automation flows with dedicated triggers.

### Setup and Authentication
1. **API Key**: Retrieve a Personal API key from **Settings → API Key**.
2. **Connection**: In viaSocket, search for the **Supermemory** trigger and paste the API key to authenticate.

Sources: [apps/docs/integrations/viasocket.mdx:18-41]()

### Supported Triggers
*   **Search Memory**: Executes a hybrid search against stored memories.
*   **Search User Profile**: Retrieves dynamic or static profile information.

Sources: [apps/docs/integrations/viasocket.mdx:29-31]()

---

## Technical Reference: Common Integration Patterns

### Scoping with `containerTag`
In all no-code integrations, the `containerTag` (formerly `userId` in some legacy contexts) is critical. It ensures that memories are scoped to specific users or projects, preventing cross-pollination of data.

Sources: [apps/docs/memory-api/creation/adding-memories.mdx:9-13](), [apps/docs/memory-api/ingesting.mdx:148-152]()

### Document vs Memory Model
Integrations primarily interact with **Documents**. When an automation adds content via `POST /v3/documents`, Supermemory asynchronously processes it through a pipeline:
1. **Queued**: Initial submission.
2. **Extracting**: OCR/Transcription.
3. **Chunking**: Semantic splitting.
4. **Embedding**: Vector generation.
5. **Indexing**: Search availability.

Sources: [apps/docs/memory-api/ingesting.mdx:13-26](), [apps/docs/memory-api/track-progress.mdx:9-20]()

### Idempotency with `customId`
For automations that might trigger multiple times for the same event (e.g., webhook retries), use `customId`. Providing the same `customId` with a `POST /v3/documents` request will update the existing document instead of creating a duplicate.

Sources: [apps/docs/update-delete-memories/overview.mdx:68-71](), [apps/docs/update-delete-memories/overview.mdx:157-159]()

---

# Page: Voice & Cartesia Integration

# Voice & Cartesia Integration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [apps/docs/integrations/cartesia.mdx](apps/docs/integrations/cartesia.mdx)
- [packages/cartesia-sdk-python/README.md](packages/cartesia-sdk-python/README.md)
- [packages/cartesia-sdk-python/pyproject.toml](packages/cartesia-sdk-python/pyproject.toml)
- [packages/cartesia-sdk-python/requirements.txt](packages/cartesia-sdk-python/requirements.txt)
- [packages/cartesia-sdk-python/src/supermemory_cartesia/__init__.py](packages/cartesia-sdk-python/src/supermemory_cartesia/__init__.py)
- [packages/cartesia-sdk-python/src/supermemory_cartesia/agent.py](packages/cartesia-sdk-python/src/supermemory_cartesia/agent.py)
- [packages/cartesia-sdk-python/src/supermemory_cartesia/exceptions.py](packages/cartesia-sdk-python/src/supermemory_cartesia/exceptions.py)
- [packages/cartesia-sdk-python/src/supermemory_cartesia/utils.py](packages/cartesia-sdk-python/src/supermemory_cartesia/utils.py)

</details>



The Supermemory ecosystem provides specialized SDKs for integrating persistent memory into voice-based AI agents. This integration primarily targets **Cartesia Line** and **Pipecat**, allowing voice assistants to maintain long-term context, recall user facts (static profiles), and adapt to recent interactions (dynamic profiles) during low-latency voice conversations.

## Supermemory Cartesia SDK

The `supermemory-cartesia` package provides a high-level wrapper for Cartesia Line agents. It intercepts conversation events to inject memory context before the LLM generates a response.

### Installation & Configuration

Install the package via pip:
```bash
pip install supermemory-cartesia
```
[packages/cartesia-sdk-python/README.md:7-9]()

The integration relies on the `SupermemoryCartesiaAgent` class which wraps a standard Cartesia `LlmAgent` [packages/cartesia-sdk-python/src/supermemory_cartesia/agent.py:33-60](). It requires a `container_tag` for scoping and a `custom_id` to group messages into a single document [packages/cartesia-sdk-python/src/supermemory_cartesia/agent.py:91-96]().

### The SupermemoryCartesiaAgent Wrapper

The wrapper monitors `UserTurnEnded` events from the Cartesia pipeline. When a user finishes speaking, the agent performs a memory lookup using the user's last utterance as a query [apps/docs/integrations/cartesia.mdx:89-99]().

| Parameter | Type | Description |
| :--- | :--- | :--- |
| `agent` | `Any` | The inner Cartesia Line agent to wrap. |
| `container_tag` | `str` | Primary tag for memory scoping (usually User ID). |
| `custom_id` | `str` | Required. Groups messages into a single document (e.g., Call ID). |
| `add_memory` | `Literal["always", "never"]` | Persistence mode (default: "always"). |
| `config` | `MemoryConfig` | Advanced settings for search limits and thresholds. |

**Sources:** [packages/cartesia-sdk-python/src/supermemory_cartesia/agent.py:77-105](), [apps/docs/integrations/cartesia.mdx:150-160]()

### Memory Context Injection

Memories are retrieved via the `profile` endpoint, which returns three types of data:
1.  **Static Profile**: Persistent facts (e.g., "User lives in New York").
2.  **Dynamic Profile**: Evolving preferences (e.g., "User is currently looking for a pizza place").
3.  **Search Results**: Semantically relevant snippets from past transcripts.

These are formatted into a text block and wrapped in `MEMORY_TAG_START` (`<user_memories>`) and `MEMORY_TAG_END` (`</user_memories>`) XML tags before being injected into the agent's system prompt [packages/cartesia-sdk-python/src/supermemory_cartesia/agent.py:28-31]().

### Data Flow: Cartesia Voice Agent

The following diagram illustrates how the `SupermemoryCartesiaAgent` mediates between the Cartesia event loop and the Supermemory API.

**Voice Agent Memory Flow**
```mermaid
sequenceDiagram
    participant C as "Cartesia_Line"
    participant W as "SupermemoryCartesiaAgent"
    participant API as "Supermemory_API_v4"

    C->>W: "UserTurnEnded Event"
    W->>W: "get_last_user_message()"
    W->>API: "POST /v4/profile (q=query, container_tag=user_id)"
    API-->>W: "Return Static/Dynamic Profile + Search Results"
    W->>W: "format_memories_to_text()"
    W->>W: "Inject <user_memories> into system_prompt"
    W->>C: "Forward enriched context to wrapped LlmAgent"
    Note over W, API: "Background: add_memory task stores turn"
```
**Sources:** [packages/cartesia-sdk-python/src/supermemory_cartesia/agent.py:148-183](), [apps/docs/integrations/cartesia.mdx:85-104](), [packages/cartesia-sdk-python/src/supermemory_cartesia/utils.py:7-12]()

---

## Technical Implementation Details

### Memory Deduplication & Formatting
The SDK handles overlapping data using the `deduplicate_memories` utility. If a fact appears in both the static profile and search results, it ensures the fact is only presented once, prioritizing static > dynamic > search [packages/cartesia-sdk-python/src/supermemory_cartesia/utils.py:52-87]().

The `format_memories_to_text` function generates a structured string with headers [packages/cartesia-sdk-python/src/supermemory_cartesia/utils.py:90-134]():
- `## User Profile (Persistent)`
- `## Recent Context`
- `## Relevant Memories` (includes relative timestamps generated by `format_relative_time` [packages/cartesia-sdk-python/src/supermemory_cartesia/utils.py:15-50]())

### Code Entity Map: SDK Structure

This diagram maps the Python classes to their respective roles in the voice integration ecosystem.

**SDK Entity Architecture**
```mermaid
graph TD
    subgraph "supermemory-cartesia"
        Agent["SupermemoryCartesiaAgent"] --> UtilsC["utils.py"]
        Agent --> ConfigC["MemoryConfig (BaseModel)"]
        Agent --> ExcC["exceptions.py"]
    end

    subgraph "Core_Python_SDK"
        Client["AsyncSupermemory"]
    end

    Agent -- "uses" --> Client
    
    UtilsC -- "format_memories_to_text" --> Agent
    UtilsC -- "deduplicate_memories" --> Agent
    ConfigC -- "defines" --> Agent
    ExcC -- "raises" --> Agent
```
**Sources:** [packages/cartesia-sdk-python/src/supermemory_cartesia/agent.py:33-88](), [packages/cartesia-sdk-python/src/supermemory_cartesia/utils.py:90-96](), [packages/cartesia-sdk-python/src/supermemory_cartesia/exceptions.py:6-34]()

### Memory Retrieval Modes
The integration supports three operational modes via the `MemoryConfig.mode` parameter [packages/cartesia-sdk-python/src/supermemory_cartesia/agent.py:75]():

| Mode | Description | Data Fetched |
| :--- | :--- | :--- |
| `profile` | Fast personalization | Static & Dynamic Profiles only |
| `query` | Deep recall | Vector Search Results only |
| `full` | Comprehensive (Default) | Profiles + Search Results |

**Sources:** [apps/docs/integrations/cartesia.mdx:106-112](), [packages/cartesia-sdk-python/src/supermemory_cartesia/agent.py:72-75]()

### Exception Handling
The SDK defines a hierarchy of exceptions for robust error handling [packages/cartesia-sdk-python/src/supermemory_cartesia/exceptions.py:6-58]():
- `ConfigurationError`: Missing API keys or required parameters.
- `MemoryRetrievalError`: Failures during lookup.
- `MemoryStorageError`: Failures during background persistence.
- `APIError`: Direct Supermemory API request failures (includes status codes).

---

# Page: SMFS — Supermemory Filesystem

# SMFS — Supermemory Filesystem

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [apps/docs/smfs/bash-tool-python.mdx](apps/docs/smfs/bash-tool-python.mdx)
- [apps/docs/smfs/bash-tool.mdx](apps/docs/smfs/bash-tool.mdx)
- [apps/docs/smfs/examples.mdx](apps/docs/smfs/examples.mdx)
- [apps/docs/smfs/install.mdx](apps/docs/smfs/install.mdx)
- [apps/docs/smfs/mount.mdx](apps/docs/smfs/mount.mdx)
- [apps/docs/smfs/overview.mdx](apps/docs/smfs/overview.mdx)
- [apps/docs/smfs/providers/cloudflare.mdx](apps/docs/smfs/providers/cloudflare.mdx)
- [apps/docs/smfs/providers/daytona.mdx](apps/docs/smfs/providers/daytona.mdx)
- [apps/docs/smfs/providers/e2b.mdx](apps/docs/smfs/providers/e2b.mdx)
- [apps/docs/smfs/providers/vercel.mdx](apps/docs/smfs/providers/vercel.mdx)

</details>



**SMFS** (Supermemory Filesystem) mounts a Supermemory container as a real directory, allowing AI agents to use standard shell commands like `ls`, `cat`, and `grep` to interact with memory [apps/docs/smfs/overview.mdx:8-10](). By providing a filesystem interface, SMFS removes the need for agents to learn complex API schemas, leveraging the model's existing proficiency with Unix-style operations [apps/docs/smfs/overview.mdx:14-15]().

## Why a Filesystem Interface?

While standard filesystems are familiar, they often struggle with large-scale memory retrieval due to context window limits. SMFS solves this by providing:
- **Semantic `grep`**: The `sgrep` command performs vector search across the container, returning results ranked by meaning rather than just literal matches [apps/docs/smfs/overview.mdx:20-21]().
- **Memory Distillation**: Files at specific paths (e.g., `user.md`, `memory.md`) are automatically extracted and indexed as persistent memories [apps/docs/smfs/mount.mdx:30-37]().
- **Virtual `profile.md`**: A live, read-only digest of the entire container is exposed at the root, allowing models to get a "one-shot" summary of the user or session [apps/docs/smfs/mount.mdx:55-58]().

### SMFS Concept: From Shell to Supermemory
```mermaid
graph LR
    subgraph "Natural Language Space"
        Agent["AI Agent (Claude/GPT)"]
        Query["'What are my Q3 notes?'"]
    end

    subgraph "Code Entity Space"
        Shell["bash.exec() / smfs binary"]
        Command["sgrep 'Q3 notes' /memory"]
        API["POST /v4/profile"]
        DB[("Supermemory Vector Store")]
    end

    Agent -->|"Generates"| Query
    Query -->|"Invokes"| Shell
    Shell -->|"Executes"| Command
    Command -->|"Calls"| API
    API -->|"Queries"| DB
```
Sources: [apps/docs/smfs/overview.mdx](), [apps/docs/smfs/bash-tool.mdx:34-36]()

## Two Modes of Operation

SMFS can be used either as a persistent system mount or as a virtualized bash tool for serverless environments [apps/docs/smfs/overview.mdx:27-38]().

| Feature | **SMFS Mount (Binary)** | **SMFS Bash Tool (SDK)** |
| :--- | :--- | :--- |
| **Runtime** | Long-lived (VMs, Docker, Local) | Serverless / Edge (Vercel, Cloudflare) |
| **Tech** | NFSv3 (macOS) / FUSE (Linux) | HTTPS Proxy (No FUSE required) |
| **Installation** | `curl | bash` | `npm install @supermemory/bash` |
| **Usage** | Real directory on disk | `bash.exec("ls /")` via SDK |
| **Sync** | Background daemon | Eager-load cache |

### Provider Architecture: Mount vs. Bash Tool
```mermaid
graph TD
    subgraph "Pattern A: Real Mount"
        VM["Long-lived Server (E2B/Daytona)"]
        Daemon["smfs mount daemon"]
        FS["/home/user/memory"]
        VM --> Daemon
        Daemon <--> FS
    end

    subgraph "Pattern B: Bash Tool"
        Edge["Edge Runtime (Vercel/Cloudflare)"]
        SDK["@supermemory/bash"]
        Edge --> SDK
    end

    Daemon <--> Cloud["Supermemory Cloud API"]
    SDK <--> Cloud
```
Sources: [apps/docs/smfs/providers/vercel.mdx:19-45](), [apps/docs/smfs/providers/e2b.mdx:14-41]()

## SMFS Mount & Installation
The `smfs` binary turns a Supermemory container into a directory. It supports multiple sync modes: **Bidirectional** (default), **No-sync** (read-only poll), and **Ephemeral** (in-memory cache for throwaway sandboxes) [apps/docs/smfs/mount.mdx:65-98]().

For detailed instructions on the `smfs login`, `smfs mount`, and `smfs sync` commands, see [SMFS Mount & Installation](#9.1).

## SMFS Bash Tool
The Bash Tool is a virtualized shell environment that communicates with Supermemory over HTTPS. It is available as `@supermemory/bash` for TypeScript and `supermemory-bash` for Python [apps/docs/smfs/bash-tool.mdx:8-10](). It includes a `toolDescription` that can be passed directly to LLMs to define the `bash` tool schema [apps/docs/smfs/bash-tool.mdx:41-42]().

For SDK usage patterns and framework integrations (Vercel AI SDK, Anthropic, OpenAI), see [SMFS Bash Tool](#9.2).

## SMFS Provider Guides
SMFS is optimized for AI sandbox providers where agents need a workspace to read and write.
- **Daytona**: isolated Linux sandboxes [apps/docs/smfs/providers/daytona.mdx:6-8]().
- **E2B**: Firecracker microVMs for code execution [apps/docs/smfs/providers/e2b.mdx:6-7]().
- **Cloudflare**: Workers and Containers [apps/docs/smfs/providers/cloudflare.mdx:6-8]().

For platform-specific setup and Dockerfile examples, see [SMFS Provider Guides](#9.3).

Sources: [apps/docs/smfs/overview.mdx](), [apps/docs/smfs/mount.mdx](), [apps/docs/smfs/bash-tool.mdx](), [apps/docs/smfs/providers/vercel.mdx]()

---

# Page: SMFS Mount & Installation

# SMFS Mount & Installation

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [apps/docs/smfs/bash-tool-python.mdx](apps/docs/smfs/bash-tool-python.mdx)
- [apps/docs/smfs/bash-tool.mdx](apps/docs/smfs/bash-tool.mdx)
- [apps/docs/smfs/examples.mdx](apps/docs/smfs/examples.mdx)
- [apps/docs/smfs/install.mdx](apps/docs/smfs/install.mdx)
- [apps/docs/smfs/mount.mdx](apps/docs/smfs/mount.mdx)
- [apps/docs/smfs/overview.mdx](apps/docs/smfs/overview.mdx)
- [apps/docs/smfs/providers/cloudflare.mdx](apps/docs/smfs/providers/cloudflare.mdx)
- [apps/docs/smfs/providers/daytona.mdx](apps/docs/smfs/providers/daytona.mdx)
- [apps/docs/smfs/providers/e2b.mdx](apps/docs/smfs/providers/e2b.mdx)
- [apps/docs/smfs/providers/vercel.mdx](apps/docs/smfs/providers/vercel.mdx)

</details>



The **Supermemory Filesystem (SMFS)** provides a bridge between high-level AI memory and standard operating system primitives. By mounting a Supermemory container as a directory, agents can interact with their memory using familiar shell commands like `ls`, `cat`, and `grep` [apps/docs/smfs/overview.mdx:8-8](). SMFS handles the translation of filesystem operations into API calls, ensuring that data is both locally accessible and globally persistent.

### Installation & Setup

SMFS is distributed as a pre-compiled binary for macOS and Linux (both arm64 and x64 architectures).

#### 1. Binary Installation
The recommended installation method is a shell script that downloads the appropriate binary to `~/.local/bin` [apps/docs/smfs/install.mdx:10-14]().

```bash
curl -fsSL https://smfs.ai/install | bash
```

#### 2. Authentication
Before mounting, the CLI must be authenticated with a Supermemory API key. This is a one-time operation that stores credentials globally [apps/docs/smfs/install.mdx:20-24]().

```bash
smfs login --key <YOUR_API_KEY>
```

#### 3. Initialization
To enable semantic search features, the `init` command installs a shell wrapper into the user's `.zshrc` or equivalent profile [apps/docs/smfs/install.mdx:50-56](). This wrapper allows the standard `grep` command to perform semantic searches when executed inside an SMFS mount [apps/docs/smfs/install.mdx:58-59]().

Sources: [apps/docs/smfs/install.mdx:10-59](), [apps/docs/smfs/overview.mdx:32-34]()

---

### Mounting Containers

The `smfs mount` command initiates a background daemon that manages the filesystem interface [apps/docs/smfs/mount.mdx:20-20]().

#### Platform Implementations
*   **macOS**: Utilizes **NFSv3** to expose the directory [apps/docs/smfs/mount.mdx:8-8]().
*   **Linux**: Utilizes **FUSE** (Filesystem in Userspace) [apps/docs/smfs/mount.mdx:8-8]().

#### Mount Command Syntax
```bash
smfs mount <container-tag> --path <local-dir> [flags]
```

#### Core Mount Flags
| Flag | Description |
| :--- | :--- |
| `--path` | Specifies the local directory for the mount. Defaults to `./<container-tag>/` [apps/docs/smfs/mount.mdx:111-111](). |
| `--memory-paths` | Comma-separated absolute paths to be treated as "memories" [apps/docs/smfs/mount.mdx:112-112](). |
| `--no-sync` | Disables polling for remote changes; local writes still push to the cloud [apps/docs/smfs/mount.mdx:113-113](). |
| `--ephemeral` | Uses an in-memory cache; no data persists locally after unmounting [apps/docs/smfs/mount.mdx:115-115](). |
| `--foreground` | Runs the daemon in the current shell instead of detaching [apps/docs/smfs/mount.mdx:118-118](). |

#### SMFS Operational Architecture
The following diagram illustrates how the `smfs` binary bridges the local environment to the Supermemory API.

**Diagram: SMFS Mount Architecture**
```mermaid
graph TD
    subgraph "Local-Environment"
        ["smfs-CLI"]
        ["SMFS-Daemon-Background"]
        ["FS-NFSv3-FUSE"]
        ["Local-Cache-Disk-Memory"]
        
        ["smfs-CLI"] -->|"mount-command"| ["SMFS-Daemon-Background"]
        ["SMFS-Daemon-Background"] -->|"exports-mounts"| ["FS-NFSv3-FUSE"]
        ["SMFS-Daemon-Background"] <-->|"read-write"| ["Local-Cache-Disk-Memory"]
    end

    subgraph "Supermemory-Cloud"
        ["Supermemory-API"]
        ["Vector-Index-SuperRAG"]
        ["Metadata-Store"]
    end

    ["SMFS-Daemon-Background"] <-->|"HTTPS-Sync-Search"| ["Supermemory-API"]
    ["Supermemory-API"] <--> ["Vector-Index-SuperRAG"]
    ["Supermemory-API"] <--> ["Metadata-Store"]
    
    ["Agent-User"] -->|"ls-cat-grep"| ["FS-NFSv3-FUSE"]
```
Sources: [apps/docs/smfs/mount.mdx:8-20](), [apps/docs/smfs/mount.mdx:109-121](), [apps/docs/smfs/overview.mdx:18-23]()

---

### Memory Distillation & Virtual Files

SMFS distinguishes between standard files and "Memory Paths". 

#### Memory Paths
Files designated as memory paths are automatically extracted, summarized, and indexed as memories in the Supermemory platform [apps/docs/smfs/mount.mdx:30-30](). 
*   **Default paths**: `user.md` and `memory.md` [apps/docs/smfs/mount.mdx:36-36]().
*   **Customization**: Use `configureMemoryPaths` (in SDKs) or `--memory-paths` (in CLI) to define recursive directories (trailing `/`) or specific files [apps/docs/smfs/mount.mdx:48-51]().

#### Virtual `profile.md`
Every mount includes a read-only virtual file at the root named `profile.md` [apps/docs/smfs/mount.mdx:55-55](). This file provides a live, LLM-generated digest of the entire container's contents [apps/docs/smfs/overview.mdx:22-22](). It allows agents to gain immediate context without performing an expensive recursive tree walk [apps/docs/smfs/mount.mdx:57-57]().

Sources: [apps/docs/smfs/mount.mdx:30-63](), [apps/docs/smfs/overview.mdx:22-22]()

---

### Sync Behavior

SMFS employs a bidirectional synchronization strategy to ensure data consistency across multiple agents or devices.

1.  **Local Reads**: Served from the local cache for high performance [apps/docs/smfs/mount.mdx:71-71]().
2.  **Local Writes**: Queued and pushed to the Supermemory API in the background [apps/docs/smfs/mount.mdx:71-71]().
3.  **Remote Changes**: The daemon polls the API (default every 30 seconds) to pull updates made by other writers [apps/docs/smfs/mount.mdx:71-71](), [apps/docs/smfs/mount.mdx:116-116]().
4.  **Force Sync**: The `smfs sync` command flushes the write queue and pulls remote changes immediately [apps/docs/smfs/mount.mdx:101-105]().

**Diagram: Data Flow and Entity Mapping**
This diagram maps filesystem operations to the internal sync logic and API entities.

```mermaid
graph LR
    subgraph "Agent-Commands"
        ["echo-data-to-memory-md"]
        ["cat-profile-md"]
        ["grep-query-dot"]
    end

    subgraph "SMFS-Logic-smfs-daemon"
        ["Write-Queue"]
        ["Poll-Engine"]
        ["Virtual-File-Provider"]
        ["Semantic-Grep-Wrapper"]
    end

    subgraph "Supermemory-API-Entities"
        ["Memory-Object"]
        ["Document-Object"]
        ["v3-search-route"]
        ["v3-add-route"]
    end

    ["echo-data-to-memory-md"] --> ["Write-Queue"]
    ["Write-Queue"] -->|"distill-to-memory"| ["v3-add-route"]
    ["v3-add-route"] --> ["Memory-Object"]

    ["cat-profile-md"] --> ["Virtual-File-Provider"]
    ["Virtual-File-Provider"] -->|"fetch-digest"| ["Document-Object"]

    ["grep-query-dot"] --> ["Semantic-Grep-Wrapper"]
    ["Semantic-Grep-Wrapper"] -->|"vector-search"| ["v3-search-route"]
```
Sources: [apps/docs/smfs/mount.mdx:69-105](), [apps/docs/smfs/overview.mdx:18-23](), [apps/docs/smfs/install.mdx:58-59]()

---

### Sandbox Installation Examples

SMFS is frequently used within isolated environments like E2B, Daytona, or Cloudflare Containers.

#### E2B (Linux/FUSE)
In E2B sandboxes, FUSE permissions must be adjusted before mounting [apps/docs/smfs/providers/e2b.mdx:115-115]().

```python
# Setup in E2B Python SDK
sbx.commands.run("sudo chmod 666 /dev/fuse")
sbx.commands.run("smfs login --key $SUPERMEMORY_API_KEY")
sbx.commands.run("smfs mount my_agent --path /home/user/memory --foreground &")
```

#### Daytona
Because Daytona environments may have restricted outbound access, the binary is often downloaded directly from GitHub Releases rather than the `smfs.ai` redirector [apps/docs/smfs/providers/daytona.mdx:57-61]().

```bash
# Daytona direct download
curl -sL https://github.com/supermemoryai/smfs/releases/download/v0.0.1-rc2/smfs-linux-x64 -o ~/.local/bin/smfs
```

#### Cloudflare Containers
Cloudflare Containers allow mounting SMFS as a background process within the container entrypoint [apps/docs/smfs/providers/cloudflare.mdx:86-95]().

```bash
# entrypoint.sh in Cloudflare Container
smfs login --key "$SUPERMEMORY_API_KEY"
smfs mount my_agent --ephemeral --path /memory --foreground &
sleep 3
exec python3 /app/agent.py
```

Sources: [apps/docs/smfs/providers/e2b.mdx:115-123](), [apps/docs/smfs/providers/daytona.mdx:65-85](), [apps/docs/smfs/providers/cloudflare.mdx:86-95]()

---

# Page: SMFS Bash Tool

# SMFS Bash Tool

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [apps/docs/smfs/bash-tool-python.mdx](apps/docs/smfs/bash-tool-python.mdx)
- [apps/docs/smfs/bash-tool.mdx](apps/docs/smfs/bash-tool.mdx)
- [apps/docs/smfs/examples.mdx](apps/docs/smfs/examples.mdx)
- [apps/docs/smfs/install.mdx](apps/docs/smfs/install.mdx)
- [apps/docs/smfs/mount.mdx](apps/docs/smfs/mount.mdx)
- [apps/docs/smfs/overview.mdx](apps/docs/smfs/overview.mdx)
- [apps/docs/smfs/providers/cloudflare.mdx](apps/docs/smfs/providers/cloudflare.mdx)
- [apps/docs/smfs/providers/daytona.mdx](apps/docs/smfs/providers/daytona.mdx)
- [apps/docs/smfs/providers/e2b.mdx](apps/docs/smfs/providers/e2b.mdx)
- [apps/docs/smfs/providers/vercel.mdx](apps/docs/smfs/providers/vercel.mdx)

</details>



The SMFS Bash Tool provides a virtualized shell environment for AI agents to interact with Supermemory containers as if they were local filesystems. It is specifically designed for environments where a real FUSE or NFS mount is not possible, such as **Vercel Functions**, **Cloudflare Workers**, **AWS Lambda**, or other serverless/edge runtimes [apps/docs/smfs/providers/vercel.mdx:12-15]().

The tool is available via two packages:
- **TypeScript**: `@supermemory/bash` [apps/docs/smfs/bash-tool.mdx:15-16]()
- **Python**: `supermemory-bash` [apps/docs/smfs/bash-tool-python.mdx:15-16]()

## Overview and Purpose

SMFS (Supermemory Filesystem) abstracts the Supermemory API into standard shell commands (`ls`, `cat`, `grep`, `echo`). While the `smfs` binary creates a real mount on long-lived servers [apps/docs/smfs/overview.mdx:32-34](), the Bash Tool proxies these commands over HTTPS to the Supermemory backend, allowing stateless execution [apps/docs/smfs/providers/vercel.mdx:39-45]().

### Key Features
- **Semantic Search**: The `sgrep` command provides vector-based search across all files in the container [apps/docs/smfs/bash-tool.mdx:171-171]().
- **Virtual `profile.md`**: A live-generated summary of the container's contents, providing immediate context to the model without manual file traversal [apps/docs/smfs/mount.mdx:55-57]().
- **Memory Path Distillation**: Specific directories can be configured so that files written to them are automatically indexed as memories [apps/docs/smfs/mount.mdx:38-40]().

## Implementation & Data Flow

The Bash Tool operates by intercepting bash commands from the LLM and executing them against a virtualized file tree hosted in the Supermemory cloud.

### Architecture Diagram: Serverless Execution
```mermaid
graph TD
    subgraph "Client Runtime (Vercel/Cloudflare)"
        A["LLM (Claude/GPT)"] -- "tool_call: bash(cmd)" --> B["Bash Tool (@supermemory/bash)"]
        B -- "HTTPS Request" --> C["Supermemory API"]
    end

    subgraph "Supermemory Backend"
        C -- "Virtual FS Ops" --> D["S3/KV Storage"]
        C -- "Vector Search" --> E["Vector DB"]
        D -- "Sync" --> E
    end

    C -- "JSON Response" --> B
    B -- "tool_result (stdout/stderr)" --> A
```
Sources: [apps/docs/smfs/providers/vercel.mdx:39-45](), [apps/docs/smfs/overview.mdx:18-24]()

## Key Functions and Classes

### `createBash()` / `create_bash()`
The entry point for initializing the tool. It requires a Supermemory API key and a `containerTag` to scope the filesystem [apps/docs/smfs/bash-tool.mdx:29-32]().

**Returns:**
- `bash`: An object/instance containing the `exec` method [apps/docs/smfs/bash-tool.mdx:40-40]().
- `toolDescription`: A pre-written prompt for the LLM explaining how to use the virtual filesystem [apps/docs/smfs/bash-tool.mdx:41-41]().
- `configureMemoryPaths(paths)`: A function to define which paths trigger memory extraction [apps/docs/smfs/bash-tool.mdx:42-42]().

### `bash.exec(command)`
Executes a string command. It supports standard Unix-like operations including pipes and redirects [apps/docs/smfs/bash-tool.mdx:150-185]().

| Command | Behavior in Bash Tool |
| :--- | :--- |
| `ls` | Lists files in the virtual container [apps/docs/smfs/bash-tool.mdx:158-158](). |
| `cat` | Reads content of a virtual file [apps/docs/smfs/bash-tool.mdx:159-159](). |
| `sgrep` | Performs semantic search across the container [apps/docs/smfs/bash-tool.mdx:171-171](). |
| `echo "text" > file` | Writes content to the virtual filesystem [apps/docs/smfs/bash-tool.mdx:166-166](). |

Sources: [apps/docs/smfs/bash-tool.mdx:150-185](), [apps/docs/smfs/bash-tool-python.mdx:223-224]()

## Model Integration

The Bash Tool is designed to be passed directly to LLMs using function calling (OpenAI) or tool use (Anthropic).

### Vercel AI SDK Usage
In the Vercel AI SDK, the tool is integrated into `generateText` or `streamText` by wrapping `bash.exec` [apps/docs/smfs/providers/vercel.mdx:113-142]().

```typescript
// Example Integration
const { bash, toolDescription } = await createBash({
  apiKey: process.env.SUPERMEMORY_API_KEY,
  containerTag: "my_agent"
});

const result = await generateText({
  model: anthropic("claude-3-5-sonnet"),
  tools: {
    bash: tool({
      description: toolDescription,
      inputSchema: z.object({ cmd: z.string() }),
      execute: async ({ cmd }) => bash.exec(cmd),
    }),
  },
  maxSteps: 10, // Recommended for multi-step reasoning
  prompt: "What do you know about my project from my notes?",
});
```
Sources: [apps/docs/smfs/providers/vercel.mdx:113-142](), [apps/docs/smfs/providers/vercel.mdx:145-148]()

### Python SDK Usage (OpenAI/Anthropic)
The Python package `supermemory-bash` provides similar functionality for the Python ecosystem [apps/docs/smfs/bash-tool-python.mdx:4-8]().

```python
# Example for Anthropic Python SDK
result = await create_bash(api_key=key, container_tag="user_42")
bash = result.bash

response = client.messages.create(
    model="claude-sonnet-4-20250514",
    tools=[{
        "name": "bash",
        "description": result.tool_description,
        "input_schema": { ... }
    }],
    messages=[{"role": "user", "content": "Search my notes"}]
)
# Dispatch tool_use to bash.exec()
```
Sources: [apps/docs/smfs/bash-tool-python.mdx:66-124]()

## Configuration and Runtimes

### Memory Paths
You can control which parts of the filesystem are "intelligent" by configuring memory paths. Files in these paths are automatically summarized and indexed [apps/docs/smfs/bash-tool.mdx:134-142]().

```typescript
// Paths ending in / are recursive
const { configureMemoryPaths } = await createBash({ apiKey, containerTag });
await configureMemoryPaths(["/notes/", "/journal.md"]);
```
Sources: [apps/docs/smfs/bash-tool.mdx:137-139](), [apps/docs/smfs/bash-tool-python.mdx:210-216]()

### Runtime Support
| Runtime | Support Level | Implementation Method |
| :--- | :--- | :--- |
| **Cloudflare Workers** | Full | Bash Tool (stateless HTTPS) [apps/docs/smfs/providers/cloudflare.mdx:33-35]() |
| **Vercel Edge** | Full | Bash Tool (stateless HTTPS) [apps/docs/smfs/providers/vercel.mdx:103-108]() |
| **E2B / Daytona** | Full | Real Mount (FUSE) OR Bash Tool [apps/docs/smfs/providers/e2b.mdx:11-15](), [apps/docs/smfs/providers/daytona.mdx:18-22]() |
| **Local / Docker** | Full | Real Mount (`smfs mount`) [apps/docs/smfs/install.mdx:32-36]() |

### Code-to-System Mapping
The following diagram maps the Natural Language concepts to the specific TypeScript/Python entities used in the codebase.

```mermaid
graph LR
    subgraph "Natural Language Space"
        N1["'Run a command'"]
        N2["'Set memory rules'"]
        N3["'Describe tool to AI'"]
    end

    subgraph "Code Entity Space (@supermemory/bash)"
        E1["bash.exec()"]
        E2["configureMemoryPaths()"]
        E3["toolDescription"]
        E4["createBash()"]
    end

    N1 --- E1
    N2 --- E2
    N3 --- E3
    E4 --> E1
    E4 --> E2
    E4 --> E3
```
Sources: [apps/docs/smfs/bash-tool.mdx:38-43](), [apps/docs/smfs/providers/vercel.mdx:122-134]()

### Class Relationship Diagram
This diagram shows how the `createBash` factory function relates to the operational entities.

```mermaid
graph TD
    subgraph "Initialization"
        CB["createBash(apiKey, containerTag)"]
    end

    subgraph "Operational Instance"
        B["bash (Shell Instance)"]
        TD["toolDescription (String)"]
        CMP["configureMemoryPaths(paths)"]
        REF["refresh()"]
    end

    CB --> B
    CB --> TD
    CB --> CMP
    CB --> REF

    B -- "execute command" --> EX["bash.exec(cmd)"]
```
Sources: [apps/docs/smfs/bash-tool.mdx:38-43](), [apps/docs/smfs/bash-tool-python.mdx:45-50]()

## Comparison: Mount vs. Bash Tool

| Feature | `smfs mount` (Binary) | Bash Tool (Package) |
| :--- | :--- | :--- |
| **Requirement** | FUSE / NFS Support | Node.js / Python Runtime |
| **Persistence** | Background Daemon | Stateless (HTTPS) |
| **Best For** | Local Dev, Docker, Sandboxes | Serverless, Edge, Lambda |
| **Command Execution** | Real System Shell | Virtual Shell Proxy |

Sources: [apps/docs/smfs/overview.mdx:27-38](), [apps/docs/smfs/providers/vercel.mdx:5-15]()

---

# Page: SMFS Provider Guides

# SMFS Provider Guides

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [apps/docs/smfs/bash-tool-python.mdx](apps/docs/smfs/bash-tool-python.mdx)
- [apps/docs/smfs/bash-tool.mdx](apps/docs/smfs/bash-tool.mdx)
- [apps/docs/smfs/examples.mdx](apps/docs/smfs/examples.mdx)
- [apps/docs/smfs/install.mdx](apps/docs/smfs/install.mdx)
- [apps/docs/smfs/mount.mdx](apps/docs/smfs/mount.mdx)
- [apps/docs/smfs/overview.mdx](apps/docs/smfs/overview.mdx)
- [apps/docs/smfs/providers/cloudflare.mdx](apps/docs/smfs/providers/cloudflare.mdx)
- [apps/docs/smfs/providers/daytona.mdx](apps/docs/smfs/providers/daytona.mdx)
- [apps/docs/smfs/providers/e2b.mdx](apps/docs/smfs/providers/e2b.mdx)
- [apps/docs/smfs/providers/vercel.mdx](apps/docs/smfs/providers/vercel.mdx)

</details>



The Supermemory Filesystem (SMFS) is designed to be highly portable, allowing AI agents to interact with persistent memory through standard shell commands across various environments. This guide details how to implement SMFS with specific sandbox providers (Daytona, E2B), serverless platforms (Vercel, Cloudflare Workers), and container runtimes.

## Architecture Overview

SMFS can be integrated into a provider environment using two primary patterns:
1.  **Direct Mount**: Using the `smfs` binary to create a real FUSE (Linux) or NFS (macOS) mount point [apps/docs/smfs/mount.mdx:8-12](). This allows agents to use any language or tool that interacts with a standard filesystem.
2.  **Bash Tool**: Using `@supermemory/bash` (TypeScript) or `supermemory-bash` (Python) to provide a virtual bash interface [apps/docs/smfs/bash-tool.mdx:8-10](). This is ideal for serverless or edge runtimes where FUSE mounts are not possible.

### Data Flow: Natural Language to Code Entities

The following diagram illustrates how natural language prompts from an agent are translated into filesystem operations that eventually interact with the Supermemory API via SMFS entities.

**SMFS Operational Flow**
```mermaid
graph TD
    subgraph "Natural Language Space"
        UserPrompt["'What are my Q3 notes?'"]
    end

    subgraph "Agent Platform (Code Entity Space)"
        Agent["Claude Agent / AI SDK"]
        ToolCall["bash.exec('sgrep Q3 /notes/')"]
    end

    subgraph "SMFS Provider Integration"
        BashTool["@supermemory/bash"]
        SMFS_Binary["smfs mount daemon"]
    end

    subgraph "Supermemory Backend"
        API_V3["POST /v3/search"]
        ProfileMD["profile.md generator"]
    end

    UserPrompt --> Agent
    Agent --> ToolCall
    ToolCall --> BashTool
    ToolCall --> SMFS_Binary
    BashTool --> API_V3
    SMFS_Binary --> API_V3
    API_V3 --> ProfileMD
```
Sources: [apps/docs/smfs/bash-tool.mdx:26-36](), [apps/docs/smfs/mount.mdx:201-208](), [apps/docs/smfs/overview.mdx:18-25]()

---

## E2B (Firecracker MicroVMs)

E2B provides isolated sandboxes for AI code execution. SMFS can be baked into an E2B custom template to provide persistent storage across sandbox sessions.

### Implementation Patterns
*   **Agent Inside**: The agent process runs directly inside the microVM and accesses the SMFS mount locally [apps/docs/smfs/providers/e2b.mdx:14-17]().
*   **Agent Outside**: The agent runs on your server and uses `sbx.commands.run()` to interact with the SMFS mount inside the sandbox remotely [apps/docs/smfs/providers/e2b.mdx:27-31]().

### Setup and Configuration
1.  **Custom Template**: Install `fuse3` and the `smfs` binary in the Dockerfile [apps/docs/smfs/providers/e2b.mdx:52-60]().
2.  **Permissions**: Run `sudo chmod 666 /dev/fuse` inside the sandbox to allow non-root mounting [apps/docs/smfs/providers/e2b.mdx:115-115]().
3.  **Mounting**: Execute `smfs login` followed by `smfs mount` with the `--foreground` flag in a background shell [apps/docs/smfs/providers/e2b.mdx:119-123]().

**E2B Integration Diagram**
```mermaid
graph LR
    subgraph "E2B_Sandbox"
        FUSE["/dev/fuse"]
        MountDir["/home/user/memory"]
        SMFS_Bin["smfs_binary"]
    end
    
    Orchestrator["Node/Python Server"] -- "sbx.commands.run()" --> SMFS_Bin
    SMFS_Bin -- "FUSE_Mount" --> MountDir
    SMFS_Bin -- "HTTPS_Sync" --> Supermemory["api.supermemory.ai"]
```
Sources: [apps/docs/smfs/providers/e2b.mdx:33-40](), [apps/docs/smfs/providers/e2b.mdx:115-123]()

---

## Daytona (Isolated Linux Sandboxes)

Daytona sandboxes provide millisecond boot times for Linux-based agent environments.

### Installation
Since Daytona sandboxes may have restricted outbound access from certain datacenter IPs, the recommended installation method is downloading the binary directly from GitHub Releases and adding it to the local bin [apps/docs/smfs/providers/daytona.mdx:9-16](), [apps/docs/smfs/providers/daytona.mdx:57-61]().

```python
# Installation snippet for Daytona
SMFS_INSTALL = (
    "mkdir -p $HOME/.local/bin && "
    "curl -sL https://github.com/supermemoryai/smfs/releases/download/v0.0.1-rc2/smfs-linux-x64 -o $HOME/.local/bin/smfs && "
    "chmod +x $HOME/.local/bin/smfs && "
    "echo 'user_allow_other' | sudo tee -a /etc/fuse.conf > /dev/null"
)
```
Sources: [apps/docs/smfs/providers/daytona.mdx:65-74]()

---

## Vercel AI SDK Integration

For the Vercel AI SDK, the choice of SMFS provider depends on the runtime environment rather than the hosting provider.

### 1. Self-hosted Node (Long-lived)
If running on a standard VM (ECS, Railway, etc.), use the `smfs` binary to create a persistent mount point at `./memory` [apps/docs/smfs/providers/vercel.mdx:19-23](). Start the mount once at server boot, not per-request [apps/docs/smfs/providers/vercel.mdx:60-65]().

### 2. Serverless / Edge (Vercel Functions)
Serverless runtimes cannot maintain FUSE mounts. Instead, use the `@supermemory/bash` package to create a tool for `generateText` [apps/docs/smfs/providers/vercel.mdx:33-37]().

**Vercel AI SDK Code Mapping**
```mermaid
graph TD
    subgraph "Vercel_AI_SDK_Runtime"
        GenText["generateText()"]
        ToolDef["tool()"]
    end

    subgraph "SMFS_Bash_Package"
        CB["createBash()"]
        BashExec["bash.exec()"]
        TDesc["toolDescription"]
    end

    GenText --> ToolDef
    ToolDef -- "uses" --> TDesc
    ToolDef -- "calls" --> BashExec
    CB -- "returns" --> BashExec
    CB -- "returns" --> TDesc
```
Sources: [apps/docs/smfs/providers/vercel.mdx:113-141](), [apps/docs/smfs/bash-tool.mdx:26-36]()

### Key Functions
*   `createBash({ apiKey, containerTag })`: Initializes the virtual bash environment [apps/docs/smfs/bash-tool.mdx:27-32]().
*   `bash.exec(cmd)`: Executes standard Unix commands (ls, cat, grep) or semantic `sgrep` [apps/docs/smfs/bash-tool.mdx:170-171]().
*   `configureMemoryPaths(paths)`: Defines which directories/files should be distilled into permanent memories [apps/docs/smfs/bash-tool.mdx:137-140]().

---

## Cloudflare (Workers & Containers)

### Cloudflare Containers
Cloudflare Containers allow for real FUSE mounts. SMFS is typically started in the container's `entrypoint.sh` using the `--foreground` flag to keep the daemon running [apps/docs/smfs/providers/cloudflare.mdx:84-95]().

### Cloudflare Workers
Workers use the `@supermemory/bash` tool. Because Workers are addressable via Durable Objects, you can maintain a persistent agent state that interacts with SMFS over HTTP [apps/docs/smfs/providers/cloudflare.mdx:125-136]().

| Feature | Cloudflare Container | Cloudflare Worker |
| :--- | :--- | :--- |
| **Interface** | Real Filesystem (FUSE) | Virtual Bash Tool |
| **Sync Mode** | Bidirectional Background | Request-Response Proxy |
| **Memory Extraction** | Automatic via paths | Manual or Path-based |
| **Best For** | Heavy Agent Workloads | Edge-first, Low Latency |

Sources: [apps/docs/smfs/providers/cloudflare.mdx:15-40](), [apps/docs/smfs/providers/cloudflare.mdx:50-56]()

---

## Provider Comparison Table

| Provider | Implementation Type | Recommended Tooling | Persistence |
| :--- | :--- | :--- | :--- |
| **E2B** | FUSE Mount | `smfs` binary + `e2b-code-interpreter` | Full (via SMFS Sync) |
| **Daytona** | FUSE Mount | `smfs` binary + `daytona-sdk` | Full (via SMFS Sync) |
| **Vercel Functions** | Virtual Bash | `@supermemory/bash` | Session-based |
| **CF Workers** | Virtual Bash | `@supermemory/bash` | Durable Object backed |
| **CF Containers** | FUSE Mount | `smfs` binary | Full (via SMFS Sync) |

Sources: [apps/docs/smfs/overview.mdx:40-57](), [apps/docs/smfs/providers/vercel.mdx:7-15]()

---

# Page: Development Guide

# Development Guide

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/ci.yml](.github/workflows/ci.yml)
- [.github/workflows/claude-auto-fix-ci.yml](.github/workflows/claude-auto-fix-ci.yml)
- [.github/workflows/claude-code-review.yml](.github/workflows/claude-code-review.yml)
- [.github/workflows/claude.yml](.github/workflows/claude.yml)
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [README.md](README.md)
- [README.zh-CN.md](README.zh-CN.md)
- [apps/docs/cookbook/overview.mdx](apps/docs/cookbook/overview.mdx)
- [apps/docs/memory-api/sdks/overview.mdx](apps/docs/memory-api/sdks/overview.mdx)
- [apps/docs/migration/from-mem0.mdx](apps/docs/migration/from-mem0.mdx)
- [apps/docs/migration/mem0-migration-script.py](apps/docs/migration/mem0-migration-script.py)
- [turbo.json](turbo.json)

</details>



This section covers everything needed to work on the supermemory codebase as a contributor or internal developer. It spans local environment setup, the build system, code quality tooling, deployment pipelines, and contribution workflows.

This page gives a high-level orientation. Detailed information is in the child pages:

- Environment setup → [Local Development Setup](#10.1)
- Build orchestration → [Build System & Turbo](#10.2)
- Linting, formatting, and tests → [Code Quality & Testing](#10.3)
- Cloudflare and CI/CD deployment → [Deployment & CI/CD](#10.4)
- Branching, PRs, and code style → [Contributing Guidelines](#10.5)

For information on the overall monorepo layout (apps, packages, workspace relationships), see [Monorepo Structure](#1.3).

---

## Toolchain at a Glance

The project uses a consistent set of modern tools across all workspaces to ensure high performance and developer velocity:

| Tool | Version | Role |
|---|---|---|
| **Bun** | `>=1.2.17` | Primary package manager and runtime [CONTRIBUTING.md:11]() |
| **Node.js** | `>=20` | Required runtime floor |
| **Turbo** | `^2.x` | Task orchestration and build caching [CONTRIBUTING.md:60]() |
| **Biome** | `^1.x` | Linter and formatter (replacing ESLint/Prettier) [CONTRIBUTING.md:99]() |
| **TypeScript** | `^5.x` | Static typing for all new code [CONTRIBUTING.md:166]() |
| **Next.js** | `15` | Web application framework [CONTRIBUTING.md:113]() |
| **React** | `19` | UI Library [CONTRIBUTING.md:113]() |

Sources: [CONTRIBUTING.md:11-13](), [CONTRIBUTING.md:60-118]()

---

## Workspace Layout

**Monorepo workspace configuration** — how Bun and Turbo see the project:

```mermaid
graph TD
    root["package.json (root)"]
    root --> apps["apps/* (included)"]
    root --> packages["packages/* (included)"]

    apps --> web["apps/web (Next.js)"]
    apps --> mcp["apps/mcp (Cloudflare Worker)"]
    apps --> browserext["apps/browser-extension (WXT)"]
    apps --> docs["apps/docs (Mintlify)"]
    apps --> raycast["apps/raycast-extension"]

    packages --> ui["packages/ui (Shared Components)"]
    packages --> tools["packages/tools (@supermemory/tools)"]
    packages --> lib["packages/lib (Shared Logic)"]
    packages --> aisdk["packages/ai-sdk"]
    packages --> validation["packages/validation (Zod)"]
```

The monorepo structure allows for shared logic across different surfaces (web, extension, MCP) while maintaining clear boundaries [CONTRIBUTING.md:60-83]().

Sources: [CONTRIBUTING.md:60-83]()

---

## Root-Level Scripts

All primary workflows run from the repository root using `bun run <script>`:

| Script | Command | Description |
|---|---|---|
| `dev:local` | `bun run dev:local` | Start dev servers on plain localhost ports [CONTRIBUTING.md:89]() |
| `dev` | `bun run dev` | Start dev servers through portless (internal team) [CONTRIBUTING.md:90]() |
| `build` | `bun run build` | Build all applications in the monorepo [CONTRIBUTING.md:91]() |
| `format-lint` | `bun run format-lint` | Format and lint code using Biome [CONTRIBUTING.md:92]() |
| `check-types` | `bun run check-types` | Run TypeScript type checking across all packages [CONTRIBUTING.md:93]() |

Sources: [CONTRIBUTING.md:87-93]()

---

## Developer Workflow Overview

**End-to-end developer workflow** from local setup to production deployment:

```mermaid
flowchart TD
    subgraph "Local Development"
    A["Clone repo"] --> B["bun install"]
    B --> C["cp .env.example .env.local"]
    C --> D["bun run dev:local"]
    end

    subgraph "Quality Control"
    D --> E["Edit Code"]
    E --> F["bun run format-lint"]
    F --> G["bun run check-types"]
    end

    subgraph "CI/CD Pipeline"
    G --> H["Open Pull Request"]
    H --> I["Claude Code Review"]
    I --> J["Review & Merge"]
    J --> K["Deployment Pipeline"]
    end
```

The workflow is supported by automated CI checks that run type checking and linting on every PR [ci.yml:1-29](). Additionally, an automated **Claude Code Review** job scans PRs for logic errors and security bugs [claude-code-review.yml:1-123](). If CI fails, the **Auto Fix CI Failures** workflow uses Claude to attempt automatic remediation [claude-auto-fix-ci.yml:1-103]().

Sources: [CONTRIBUTING.md:14-54](), [CONTRIBUTING.md:138-160](), [CONTRIBUTING.md:205-236](), [ci.yml:1-29](), [claude-code-review.yml:1-123](), [claude-auto-fix-ci.yml:1-103]()

---

## Coding Standards

Contributors are expected to follow these core guidelines to maintain consistency:

- **Language**: Use **TypeScript** for all new code [CONTRIBUTING.md:166]().
- **Components**: Use functional components with hooks and prefer composition [CONTRIBUTING.md:174-175]().
- **Naming**: `kebab-case` for file names, `PascalCase` for component files, and `camelCase` for utility functions [CONTRIBUTING.md:181-183]().
- **Organization**: Follow the standard import order: React/Next.js -> Third-party -> Internal packages -> Relative imports [CONTRIBUTING.md:187-203]().

Sources: [CONTRIBUTING.md:162-203]()

---

## Where to Go Next

| Goal | Page |
|---|---|
| Run the project locally for the first time | [Local Development Setup](#10.1) |
| Understand how Turbo pipelines work | [Build System & Turbo](#10.2) |
| Configure Biome or run tests | [Code Quality & Testing](#10.3) |
| Deploy to Cloudflare | [Deployment & CI/CD](#10.4) |
| Submit a pull request | [Contributing Guidelines](#10.5) |

---

# Page: Local Development Setup

# Local Development Setup

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CONTRIBUTING.md](CONTRIBUTING.md)
- [README.md](README.md)
- [README.zh-CN.md](README.zh-CN.md)
- [apps/docs/cookbook/overview.mdx](apps/docs/cookbook/overview.mdx)
- [apps/docs/memory-api/sdks/overview.mdx](apps/docs/memory-api/sdks/overview.mdx)
- [apps/docs/migration/from-mem0.mdx](apps/docs/migration/from-mem0.mdx)
- [apps/docs/migration/mem0-migration-script.py](apps/docs/migration/mem0-migration-script.py)
- [apps/web/.env.example](apps/web/.env.example)
- [apps/web/app/api/onboarding/extract-content/route.ts](apps/web/app/api/onboarding/extract-content/route.ts)
- [apps/web/app/api/onboarding/research/route.ts](apps/web/app/api/onboarding/research/route.ts)
- [packages/hooks/use-org-onboarding.ts](packages/hooks/use-org-onboarding.ts)
- [turbo.json](turbo.json)

</details>



This page provides a step-by-step guide for setting up a local development environment for Supermemory. It covers cloning the repository, installing dependencies with Bun, configuring environment variables, and starting development servers across the monorepo.

## Prerequisites

Before setting up the development environment, ensure the following tools are installed:

| Tool | Minimum Version | Purpose |
|------|----------------|---------|
| **Bun** | 1.2.17 | Primary package manager and runtime [CONTRIBUTING.md:11]() |
| **Git** | Any recent | Version control [CONTRIBUTING.md:12]() |
| **Node.js** | 20 or higher | Runtime for specific build tools |

The codebase explicitly requires Bun as the package manager for performance and workspace management [CONTRIBUTING.md:11]().

**Sources:** [CONTRIBUTING.md:7-13]()

## Monorepo Structure & Data Flow

Supermemory is organized as a Turbo monorepo. The following diagram bridges the natural language components to their specific code entities and locations.

### Component to Code Entity Mapping

```mermaid
graph TD
    subgraph "Applications (apps/*)"
        Web["Next.js Web App<br/>(apps/web)"]
        MCP["MCP Server<br/>(apps/mcp)"]
        Browser["Browser Extension<br/>(apps/browser-extension)"]
        Docs["Documentation Site<br/>(apps/docs)"]
    end

    subgraph "Shared Packages (packages/*)"
        UI["@repo/ui<br/>(packages/ui)"]
        Lib["@repo/lib<br/>(packages/lib)"]
        AISDK["@supermemory/tools<br/>(packages/ai-sdk)"]
        Validation["@repo/validation<br/>(packages/validation)"]
    end

    Web -- "imports" --> Validation
    Web -- "uses" --> UI
    Web -- "uses" --> Lib
    MCP -- "uses" --> AISDK
    Browser -- "interacts with" --> Web
    
    style Web stroke-width:2px
    style MCP stroke-width:2px
    style Browser stroke-width:2px
```

**Workspace Configuration**
The monorepo uses Bun and Turbo for orchestration, defined in `package.json` and `turbo.json` [turbo.json:1-25](). Shared logic is encapsulated in `packages/` while consumer-facing interfaces reside in `apps/` [CONTRIBUTING.md:58-83]().

**Sources:** [CONTRIBUTING.md:58-83](), [turbo.json:1-25]()

## Initial Setup

### 1. Clone and Install
```bash
git clone https://github.com/supermemoryai/supermemory.git
cd supermemory
bun install
```
The `bun install` command resolves dependencies for the entire workspace [CONTRIBUTING.md:23-27]().

### 2. Environment Variables
You must set up environment variables for the applications to function.
```bash
# Copy the example environment file
cp .env.example .env.local
```
Key variables required across the stack include API keys for AI providers and database URLs [CONTRIBUTING.md:29-37](). For the web application, specific keys like `EXA_API_KEY` are used for content extraction [apps/web/.env.example:3](), [apps/web/app/api/onboarding/extract-content/route.ts:12-17](), and `XAI_API_KEY` is used for user research [apps/web/.env.example:4](), [apps/web/app/api/onboarding/research/route.ts:1-2]().

### 3. Local Proxy Configuration
For local development of the web application, you must bypass the session retrieval for `localhost` in `apps/web/proxy.ts` [CONTRIBUTING.md:39-47]().

```typescript
if (url.hostname === "localhost") {
  return NextResponse.next();
}
```

**Sources:** [CONTRIBUTING.md:14-47](), [apps/web/.env.example:1-4](), [apps/web/app/api/onboarding/extract-content/route.ts:12-17]()

## Running Development Servers

### Development Modes
Supermemory supports two primary development modes:

1.  **OSS/Local Mode:** Recommended for outside contributors. Starts servers on standard `localhost` ports [CONTRIBUTING.md:54-55]().
    ```bash
    bun run dev:local
    ```
2.  **Internal/Portless Mode:** Used by the internal team to provide `*.dev.supermemory.ai` HTTPS URLs with shared cookies [CONTRIBUTING.md:56-57]().
    ```bash
    bun run dev
    ```

### Port Assignments (Local Mode)

| Application | Port | Location |
|-------------|------|----------|
| **Web App** | 3000 | [apps/web]() |
| **MCP Server** | 8788 | [apps/mcp]() |
| **Docs** | 3003 | [apps/docs]() |
| **Graph Playground** | 3004 | [apps/memory-graph-playground]() |

**Sources:** [CONTRIBUTING.md:49-57](), [CONTRIBUTING.md:87-94]()

## Local Development Workflow

### Code Quality Tools
Before submitting a Pull Request, ensure your code passes linting, type checking, and build tests [CONTRIBUTING.md:103-109]().

- **Format & Lint:** `bun run format-lint` (uses Biome) [CONTRIBUTING.md:92]().
- **Type Check:** `bun run check-types` [CONTRIBUTING.md:93]().
- **Build:** `bun run build` [CONTRIBUTING.md:91]().

### Development Architecture Diagram

This diagram illustrates the interaction between local entities during a development session.

```mermaid
sequenceDiagram
    participant Dev as "Developer"
    participant Turbo as "Turbo (Root)"
    participant Web as "Next.js (apps/web)"
    participant API as "Public API (api.supermemory.ai)"
    participant AI as "AI Providers (xAI/Exa)"

    Dev->>Turbo: "bun run dev:local"
    Turbo->>Web: "next dev"
    Dev->>Web: "Interaction (localhost:3000)"
    Web->>API: "Requests (NEXT_PUBLIC_BACKEND_URL)"
    Web->>AI: "Onboarding APIs (research/extract-content)"
    AI-->>Web: "Response"
    Web-->>Dev: "UI Update"
```

### Troubleshooting Local Setup

| Symptom | Potential Cause | Fix |
|---------|----------------|-----|
| OAuth Sign-in Fails | Redirect URL mismatch | Use Magic Link/Email OTP for localhost; OAuth requires the `dev.supermemory.ai` proxy [CONTRIBUTING.md:54-55](). |
| Missing Research Data | Missing `XAI_API_KEY` | Ensure `XAI_API_KEY` is set in `.env.local` for the research route [apps/web/app/api/onboarding/research/route.ts:1-2](). |
| Extraction Fails | Missing `EXA_API_KEY` | Check if `EXA_API_KEY` is configured in the environment [apps/web/app/api/onboarding/extract-content/route.ts:12-17](). |

**Sources:** [CONTRIBUTING.md:54-57](), [apps/web/app/api/onboarding/research/route.ts:1-2](), [apps/web/app/api/onboarding/extract-content/route.ts:12-17]()

---

# Page: Build System & Turbo

# Build System & Turbo

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitignore](.gitignore)
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [README.md](README.md)
- [README.zh-CN.md](README.zh-CN.md)
- [apps/docs/cookbook/overview.mdx](apps/docs/cookbook/overview.mdx)
- [apps/docs/memory-api/sdks/overview.mdx](apps/docs/memory-api/sdks/overview.mdx)
- [apps/docs/migration/from-mem0.mdx](apps/docs/migration/from-mem0.mdx)
- [apps/docs/migration/mem0-migration-script.py](apps/docs/migration/mem0-migration-script.py)
- [apps/web/.gitignore](apps/web/.gitignore)
- [apps/web/app/global-error.tsx](apps/web/app/global-error.tsx)
- [apps/web/app/layout.tsx](apps/web/app/layout.tsx)
- [apps/web/package.json](apps/web/package.json)
- [apps/web/public/OG.png](apps/web/public/OG.png)
- [apps/web/tsconfig.json](apps/web/tsconfig.json)
- [apps/web/wrangler.jsonc](apps/web/wrangler.jsonc)
- [bun.lock](bun.lock)
- [package.json](package.json)
- [turbo.json](turbo.json)

</details>



## Purpose and Scope

This document explains the build system architecture of the supermemory monorepo, including Turborepo task orchestration, Bun package management, workspace exclusions, and production build pipelines. It details how tasks are scoped across the repository and how individual workspace builds are executed.

## Overview

The supermemory monorepo uses a modern toolchain optimized for speed and Cloudflare-native deployment:

| Tool | Version | Role |
|------|---------|------|
| **Turborepo** | `^2.5.4` | Parallel task execution and intelligent caching |
| **Bun** | `1.3.6` | Package manager and workspace orchestration |
| **TypeScript** | `5.8.3` | Static type checking across all packages |
| **Biome** | `^2.2.0` | Unified linter and formatter |
| **Wrangler** | `^4.42.2` | Cloudflare Workers CLI for deployment and type generation |

The build system coordinates multiple complex outputs, including a Next.js app adapted for Cloudflare via `opennextjs-cloudflare`, a WXT-based browser extension, and a Model Context Protocol (MCP) server.

Sources: [package.json:15-67](), [bun.lock:48-50]()

## Build System Architecture

The build system is designed around a Directed Acyclic Graph (DAG) managed by Turbo. Root-level scripts delegate to Turbo to ensure that shared packages (like `@repo/lib` or `@repo/validation`) are built before the applications that consume them.

**Root Build Pipeline**

```mermaid
graph TB
    subgraph "RootScripts [package.json]"
        RootBuild["bun run build<br/>(turbo run build)"]
        RootDev["bun run dev<br/>(turbo run dev)"]
        TypeCheck["bun run check-types<br/>(turbo run check-types)"]
    end

    subgraph "TurboOrchestration"
        TurboPipeline["turbo.json config"]
        TurboCache[".turbo/cache/"]
    end

    subgraph "WorkspaceBuilds"
        WebBuild["@repo/web:<br/>next build"]
        MCPBuild["supermemory-mcp:<br/>wrangler deploy"]
        ExtBuild["supermemory-browser-extension:<br/>wxt build"]
    end

    subgraph "BuildOutputs"
        NextOut[".next/ & .open-next/"]
        WorkerBundle["Worker script"]
        ExtOut["dist/ (extension)"]
    end

    RootBuild --> TurboPipeline
    RootDev --> TurboPipeline
    TypeCheck --> TurboPipeline

    TurboPipeline --> TurboCache
    TurboCache --> WebBuild
    TurboCache --> MCPBuild
    TurboCache --> ExtBuild

    WebBuild --> NextOut
    MCPBuild --> WorkerBundle
    ExtBuild --> ExtOut
```

Sources: [package.json:4-12](), [apps/web/package.json:9-21](), [apps/mcp/package.json:106-107]()

## Workspace Configuration & Exclusions

The monorepo structure is defined in the root `package.json`. While most projects are part of the unified build graph, specific workspaces are excluded to prevent dependency conflicts or because they require specialized build environments.

### Included and Excluded Workspaces

Workspaces are configured in [package.json:17-22]():

```json
"workspaces": [
  "apps/*",
  "!apps/raycast-extension",
  "!tools/test/chatapp",
  "packages/*"
]
```

| Workspace Path | Status | Reason for Exclusion |
|---|---|---|
| `apps/web` | **Included** | Core Next.js application |
| `apps/mcp` | **Included** | Cloudflare Worker MCP server |
| `packages/*` | **Included** | Shared libraries (UI, Lib, Validation) |
| `apps/raycast-extension` | **Excluded** | Requires native Raycast environment and `npm`-specific tooling |
| `tools/test/chatapp` | **Excluded** | Isolated test harness for tools |

To run builds for excluded workspaces, developers must navigate into the specific directory and use the local package manager (often `npm` for Raycast or `bun` for the test app).

Sources: [package.json:17-22](), [bun.lock:5-52](), [CONTRIBUTING.md:58-83]()

## Turborepo Task Orchestration

### Core Tasks

Turbo orchestrates the following primary tasks defined in `turbo.json` and the root `package.json`:

| Task | Configuration | Behavior |
|--------|---------|----------|
| `build` | `dependsOn: ["^build"]` | Builds workspaces. Caches `.next/**` and `.env*` inputs. |
| `lint` | `dependsOn: ["^lint"]` | Runs linting across the graph. |
| `check-types` | `dependsOn: ["^check-types"]` | Validates types without emitting files. |
| `dev` | `cache: false` | Starts persistent dev servers. |

Sources: [turbo.json:1-25](), [package.json:4-12]()

### Running Individual Workspace Builds

Individual builds can be triggered using the `--filter` flag, which targets the `name` field in a workspace's `package.json`.

*   **Build Web App:** `turbo run build --filter=@repo/web`
*   **Build MCP Server:** `turbo run build --filter=supermemory-mcp`
*   **Build Browser Extension:** `turbo run build --filter=supermemory-browser-extension`

Sources: [package.json:1-12](), [apps/web/package.json:2](), [apps/mcp/package.json:87](), [bun.lock:54]()

## App-Specific Build Pipelines

### Web Application (`apps/web`)

The web app uses `opennextjs-cloudflare` to bridge Next.js with the Cloudflare ecosystem. It utilizes path aliases to reference shared packages such as `@ui/*`, `@lib/*`, and `@hooks/*`.

**Web Build Entity Mapping**

```mermaid
graph TD
    subgraph "Natural Language Space"
        N1["Web UI Build"]
        N2["Cloudflare Environment Types"]
        N3["Sentry Integration"]
    end

    subgraph "Code Entity Space"
        C1["next build"]
        C2["wrangler types --env-interface CloudflareEnv"]
        C3["sentry-cli sourcemaps upload"]
        C4["opennextjs-cloudflare build"]
    end

    N1 --- C1
    N1 --- C4
    N2 --- C2
    N3 --- C3
```

Key scripts in `apps/web/package.json`:
*   `cf-typegen`: Generates TypeScript interfaces for Cloudflare bindings via `wrangler types` [apps/web/package.json:18]().
*   `deploy`: Executes the OpenNext build and deploys to Cloudflare [apps/web/package.json:16]().
*   `sentry:sourcemaps`: Uploads sourcemaps to Sentry for production error tracking [apps/web/package.json:19]().

Sources: [apps/web/package.json:9-21](), [apps/web/tsconfig.json:5-11](), [CONTRIBUTING.md:111-119]()

### Browser Extension (`apps/browser-extension`)

Built using the WXT framework. The build command `wxt build` (invoked via Turbo) generates extension bundles for multiple browsers. It uses `turndown` for markdown conversion and `react` for UI components.

Sources: [bun.lock:72](), [apps/browser-extension/package.json:53-73]()

### MCP Server (`apps/mcp`)

The MCP server is a Cloudflare Worker application. Its build process involves `wrangler` and specialized plugins like `vite-plugin-singlefile` for bundling.

**MCP Build Entity Mapping**

```mermaid
graph TD
    subgraph "Natural Language Space"
        N1["MCP Worker Deployment"]
        N2["Local Testing"]
        N3["SDK Integration"]
    end

    subgraph "Code Entity Space"
        C1["wrangler deploy"]
        C2["vitest"]
        C3["@modelcontextprotocol/sdk"]
        C4["supermemory-mcp (package name)"]
    end

    N1 --- C1
    N1 --- C4
    N2 --- C2
    N3 --- C3
```

Sources: [apps/mcp/package.json:87-108](), [bun.lock:86-108]()

## Production Build & Sentry Integration

The production build includes a `postbuild` hook at the root level to ensure sourcemaps are synced with Sentry.

**Sentry Release Flow**

```mermaid
sequenceDiagram
    participant B as Bun/Turbo
    participant S as Sentry CLI (sentry-cli)
    participant API as Sentry API

    B->>B: turbo run build
    B->>S: bun run sentry:sourcemaps
    Note over S: proposes version
    S->>API: releases new [version]
    S->>API: sourcemaps upload [dist]
```

The root `sentry:sourcemaps` script handles the organization (`supermemory`) and project (`consumer-app`) targeting [package.json:10](). In the web app, this is triggered after deployment via `postdeploy` [apps/web/package.json:20]().

Sources: [package.json:10-11](), [apps/web/package.json:19-20]()

## TypeScript & Type Checking

The repo uses TypeScript `5.8.3`. Type checking is performed globally via `turbo run check-types`. 

Workspaces extend a shared base configuration:
*   `@total-typescript/tsconfig` is used as a base [package.json:61]().
*   The `check-types` task ensures consistency across the monorepo without requiring individual workspace `tsc` calls during every development iteration [turbo.json:13-15]().

Sources: [package.json:65](), [turbo.json:13-15](), [CONTRIBUTING.md:93-102]()

---

# Page: Code Quality & Testing

# Code Quality & Testing

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/ci.yml](.github/workflows/ci.yml)
- [.github/workflows/claude-auto-fix-ci.yml](.github/workflows/claude-auto-fix-ci.yml)
- [.github/workflows/claude-code-review.yml](.github/workflows/claude-code-review.yml)
- [.github/workflows/claude.yml](.github/workflows/claude.yml)
- [apps/web/biome.json](apps/web/biome.json)
- [packages/tools/test/ai-sdk-test.ts](packages/tools/test/ai-sdk-test.ts)
- [packages/tools/test/chatapp/app/api/chat/route.ts](packages/tools/test/chatapp/app/api/chat/route.ts)
- [packages/tools/test/chatapp/app/api/stream/route.ts](packages/tools/test/chatapp/app/api/stream/route.ts)
- [packages/tools/test/chatapp/app/stream/page.tsx](packages/tools/test/chatapp/app/stream/page.tsx)
- [packages/tools/test/chatapp/bun.lock](packages/tools/test/chatapp/bun.lock)
- [packages/tools/test/with-supermemory/integration.test.ts](packages/tools/test/with-supermemory/integration.test.ts)
- [packages/tools/test/with-supermemory/unit.test.ts](packages/tools/test/with-supermemory/unit.test.ts)
- [packages/ui/assets/Logo.tsx](packages/ui/assets/Logo.tsx)
- [packages/ui/biome.json](packages/ui/biome.json)
- [packages/ui/globals.css](packages/ui/globals.css)

</details>



## Purpose and Scope

This document covers the code quality tools, testing infrastructure, and quality standards used across the Supermemory monorepo. It details the linting and formatting setup with Biome, TypeScript type checking orchestration via Turborepo, the testing structure for AI tools, and automated AI-driven code reviews and CI self-healing.

---

## Code Formatting & Linting with Biome

The repository uses **Biome** as the primary code quality tool, replacing ESLint and Prettier. Biome provides high-performance code formatting and lint checking across all packages and applications.

### Configuration

Biome is configured via a root `biome.json` file. It is set to use `tab` indentation and `double` quotes for JavaScript. Individual packages, such as `packages/ui` and `apps/web`, contain their own `biome.json` files that extend the root configuration [.github/workflows/ci.yml:27-28](), [packages/ui/biome.json:1-5](), [apps/web/biome.json:1-5]().

Key linter rules include:
- **Correctness**: `noUnusedVariables` and `noUnusedImports` are prioritized.
- **Tailwind Support**: The CSS parser is configured to support Tailwind directives, specifically used in `packages/ui/globals.css` [packages/ui/globals.css:1-8]().

```mermaid
graph TD
    subgraph "Biome_Tooling_Structure"
        RootConfig["root/biome.json"]
        WebConfig["apps/web/biome.json"]
        UIConfig["packages/ui/biome.json"]
        
        WebConfig -- "extends" --> RootConfig
        UIConfig -- "extends" --> RootConfig
        
        RootConfig --> Formatter["Formatter: Tabs, Double Quotes"]
        RootConfig --> Linter["Linter: Recommended + Style Rules"]
    end

    subgraph "Target_Code_Entities"
        Formatter --> TS["*.ts, *.tsx"]
        Linter --> CSS["packages/ui/globals.css"]
        Linter --> Tools["packages/tools/src"]
    end
```
**Biome Tooling Structure**

**Sources:** [packages/ui/biome.json:1-5](), [apps/web/biome.json:1-5](), [packages/ui/globals.css:1-8](), [.github/workflows/ci.yml:27-28]()

---

## TypeScript Type Checking

TypeScript type checking is orchestrated through **Turborepo** to run across workspace members in parallel. The CI pipeline specifically targets core packages like `@supermemory/ai-sdk` and `@supermemory/memory-graph` [.github/workflows/ci.yml:24-25]().

### Type Checking Flow

The root `package.json` defines a `check-types` script that triggers `turbo run check-types`.

```mermaid
graph LR
    "Developer/CI" -- "bunx turbo run check-types" --> Turbo["Turbo Orchestrator"]
    
    subgraph "Parallel_Execution"
        Turbo -- "--filter=@supermemory/ai-sdk" --> SDK["packages/tools: tsc"]
        Turbo -- "--filter=@supermemory/memory-graph" --> Graph["packages/memory-graph: tsc"]
    end
    
    SDK --> Results["Aggregated CI Results"]
    Graph --> Results
```
**Type Checking Orchestration**

**Sources:** [.github/workflows/ci.yml:24-25]()

---

## Testing Infrastructure

Testing is concentrated in `packages/tools` to ensure the reliability of the AI middleware and SDK wrappers. The project uses **Vitest** for unit and integration testing [packages/tools/test/with-supermemory/unit.test.ts:5]().

### SDK Middleware Testing
Tests verify the `withSupermemory` wrapper which enhances AI models with long-term memory.

*   **Unit Tests**: Located in `packages/tools/test/with-supermemory/unit.test.ts`. These tests mock `LanguageModelV2` and verify the `transformParamsWithMemory` logic and the `memoryCache` mechanism [packages/tools/test/with-supermemory/unit.test.ts:6-15](), [packages/tools/test/with-supermemory/unit.test.ts:140-179]().
*   **Integration Tests**: Located in `packages/tools/test/with-supermemory/integration.test.ts`. These run against the real Supermemory API (e.g., `https://api.supermemory.ai`) when a `SUPERMEMORY_API_KEY` is provided [packages/tools/test/with-supermemory/integration.test.ts:13-17](), [packages/tools/test/with-supermemory/integration.test.ts:94-113]().
*   **Chat App Simulation**: A test chat application in `packages/tools/test/chatapp` provides a real-world environment for testing `streamText` with `withSupermemory` [packages/tools/test/chatapp/app/api/stream/route.ts:36-47](), [packages/tools/test/chatapp/app/stream/page.tsx:10-14]().

**Sources:** [packages/tools/test/with-supermemory/unit.test.ts:5-15](), [packages/tools/test/with-supermemory/integration.test.ts:13-17](), [packages/tools/test/chatapp/app/api/stream/route.ts:36-47]()

---

## Automated AI Quality Control

Supermemory utilizes **Claude Code** via GitHub Actions for both proactive code reviews and reactive CI self-healing.

### 1. Claude Code Review
The `Claude Code Review` workflow triggers on PR events [.github/workflows/claude-code-review.yml:3-5](). It acts as a senior engineer, focusing on:
*   **Logic Errors**: Race conditions, null access, and incorrect `await` usage [.github/workflows/claude-code-review.yml:73]().
*   **Security**: SQL injection, XSS, and auth bypass [.github/workflows/claude-code-review.yml:74]().
*   **Data Integrity**: Missing transactions or incorrect cascade deletes [.github/workflows/claude-code-review.yml:75]().

### 2. Auto-Fix CI Failures
The `Auto Fix CI Failures` workflow triggers when the standard CI (Type Check, Format & Lint) fails [.github/workflows/claude-auto-fix-ci.yml:4-7](). It uses Claude to:
1.  Analyze failure details via `actions/github-script` [.github/workflows/claude-auto-fix-ci.yml:41-43]().
2.  Run `biome check --fix` or fix type errors [.github/workflows/claude-auto-fix-ci.yml:78-79]().
3.  Commit and push fixes directly back to the PR branch [.github/workflows/claude-auto-fix-ci.yml:82-83]().

```mermaid
graph TD
    subgraph "Natural_Language_Review_Space"
        Reviewer["Claude Code Action"]
        Policy["Review Philosophy: Catch Bugs/Security"]
    end

    subgraph "Code_Entity_Space"
        Diff["mcp__github__get_pull_request_diff"]
        Fix["biome check --fix"]
        Check["turbo run check-types"]
    end

    Reviewer -- "Uses" --> Diff
    Reviewer -- "Enforces" --> Policy
    CI_Fail["CI Failure"] -- "Triggers" --> Reviewer
    Reviewer -- "Executes" --> Fix
    Reviewer -- "Validates" --> Check
```
**AI-Driven Quality Loop**

**Sources:** [.github/workflows/claude-code-review.yml:1-123](), [.github/workflows/claude-auto-fix-ci.yml:1-103](), [.github/workflows/ci.yml:1-29]()

---

## Summary of Quality Commands

| Command | Scope | Purpose |
|---------|-------|---------|
| `bunx biome ci --changed` | CI | Lints and formats changed files against `origin/main` [.github/workflows/ci.yml:28]() |
| `bunx turbo run check-types` | Root | Parallel TypeScript validation across workspaces [.github/workflows/ci.yml:25]() |
| `vitest` | `packages/tools` | Executes unit and integration tests for AI SDK wrappers [packages/tools/test/with-supermemory/unit.test.ts:5]() |
| `biome check --fix .` | Local | Automatically fixes linting and formatting issues [.github/workflows/claude-auto-fix-ci.yml:78]() |

**Sources:** [.github/workflows/ci.yml:24-28](), [packages/tools/test/with-supermemory/unit.test.ts:5](), [.github/workflows/claude-auto-fix-ci.yml:78-79]()

---

# Page: Deployment & CI/CD

# Deployment & CI/CD

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/ci.yml](.github/workflows/ci.yml)
- [.github/workflows/claude-auto-fix-ci.yml](.github/workflows/claude-auto-fix-ci.yml)
- [.github/workflows/claude-code-review.yml](.github/workflows/claude-code-review.yml)
- [.github/workflows/claude.yml](.github/workflows/claude.yml)
- [.github/workflows/publish-agent-framework-python.yml](.github/workflows/publish-agent-framework-python.yml)
- [.github/workflows/publish-ai-sdk.yml](.github/workflows/publish-ai-sdk.yml)
- [.github/workflows/publish-cartesia-sdk-python.yml](.github/workflows/publish-cartesia-sdk-python.yml)
- [.github/workflows/publish-memory-graph.yml](.github/workflows/publish-memory-graph.yml)
- [.github/workflows/publish-openai-sdk-python.yml](.github/workflows/publish-openai-sdk-python.yml)
- [.github/workflows/publish-pipecat-sdk-python.yml](.github/workflows/publish-pipecat-sdk-python.yml)
- [.github/workflows/publish-tools.yml](.github/workflows/publish-tools.yml)
- [.gitignore](.gitignore)
- [apps/web/.gitignore](apps/web/.gitignore)
- [apps/web/app/global-error.tsx](apps/web/app/global-error.tsx)
- [apps/web/app/layout.tsx](apps/web/app/layout.tsx)
- [apps/web/package.json](apps/web/package.json)
- [apps/web/public/OG.png](apps/web/public/OG.png)
- [apps/web/tsconfig.json](apps/web/tsconfig.json)
- [apps/web/wrangler.jsonc](apps/web/wrangler.jsonc)
- [bun.lock](bun.lock)
- [package.json](package.json)

</details>



This document covers the deployment pipeline and CI/CD configuration for the Supermemory project. It focuses on how `apps/web` is deployed to Cloudflare via `opennextjs-cloudflare`, how `apps/mcp` is deployed as a Cloudflare Worker via `wrangler`, and the automated CI workflows using GitHub Actions and Claude.

## Build System Overview

The project uses **Turbo** to orchestrate builds across the monorepo with **Bun** as the package manager [package.json:5-16](). Deployable apps include `apps/web` (Next.js on Cloudflare Workers) and `apps/mcp` (Cloudflare Worker).

**Diagram: Monorepo build and deployment flow**

```mermaid
graph TB
    subgraph "root_package_json[package.json]"
        build["turbo run build"]
        postbuild["bun run sentry:sourcemaps (postbuild)"]
    end

    subgraph "apps_web_package_json[apps/web/package.json]"
        nextbuild["next build"]
        opennextbuild["opennextjs-cloudflare build"]
        deploy["opennextjs-cloudflare deploy"]
        upload["opennextjs-cloudflare upload"]
    end

    subgraph "apps_mcp"
        wranglerdeploy["wrangler deploy"]
    end

    build --> nextbuild
    nextbuild --> opennextbuild
    opennextbuild --> deploy
    opennextbuild --> upload
    build --> postbuild

    deploy --> CFWorkers["Cloudflare Workers (apps/web)"]
    wranglerdeploy --> CFWorkersMCP["Cloudflare Workers (apps/mcp)"]
```

Sources: [package.json:5-12](), [apps/web/package.json:12-20]().

## CI Configuration

The repository uses several GitHub Action workflows to ensure code quality and automate fixes.

### Quality Checks (CI)
The primary CI workflow `CI - Type Check, Format & Lint` runs on every pull request. It performs:
1. **Type Checking**: Runs `turbo run check-types` across the workspace [package.json:9-9]().
2. **Linting & Formatting**: Uses `bunx biome check --write` to maintain code standards [package.json:8-8]().

### Automated Fixes with Claude
Supermemory integrates `claude-code-action` to automatically fix CI failures and perform deep code reviews.

- **Claude Code Review**: A "Senior Engineer" persona review triggered on pull requests [ .github/workflows/claude-code-review.yml:3-5](). It focuses on production incidents, security vulnerabilities (SQLi, XSS), and data loss risks [.github/workflows/claude-code-review.yml:62-78](). It utilizes MCP tools like `mcp__github__get_pull_request_diff` to analyze code intent [.github/workflows/claude-code-review.yml:88-88]().
- **Interactive Claude**: A workflow that allows developers to tag `@claude` in comments or issue descriptions to trigger automated tasks [.github/workflows/claude.yml:15-19](). It uses the `claude-opus-4-5-20251101` model with access to both `supermemory` and `github` MCP servers [.github/workflows/claude.yml:44-56]().

**Diagram: Claude Code Review workflow**

```mermaid
sequenceDiagram
    participant PR as "GitHub Pull Request"
    participant Action as "Claude Code Action"
    participant MCP as "MCP Servers (supermemory/github)"
    
    PR->>Action: "PR opened/synchronized"
    Action->>MCP: "mcp__github__get_pull_request_diff"
    MCP-->>Action: "Diff Data"
    Action->>Action: "Analyze for Bugs/Security (Senior Engineer persona)"
    Action->>MCP: "mcp__github__create_pending_pull_request_review"
    Action->>MCP: "mcp__github__submit_pending_pull_request_review"
    MCP-->>PR: "Review Summary & Inline Comments"
```

Sources: [.github/workflows/claude-code-review.yml:1-123](), [.github/workflows/claude.yml:1-57]().

## Automated Package Publishing

The repository includes several workflows for publishing packages to npm and PyPI upon version changes in the `main` branch.

### NPM Publishing
Workflows for `@supermemory/ai-sdk`, `@supermemory/tools`, and `@supermemory/memory-graph` follow a standard pattern:
1. **Version Check**: Compares the local version in `package.json` with the latest version on npm using `npm view` [.github/workflows/publish-ai-sdk.yml:38-50]().
2. **Build**: Runs `bun run build` if the version has changed [.github/workflows/publish-ai-sdk.yml:52-54]().
3. **Publish**: Executes `npm publish --access public --provenance` [.github/workflows/publish-ai-sdk.yml:56-58]().

### Python (PyPI) Publishing
Python SDKs (Pipecat, OpenAI, Agent Framework, Cartesia) are published using GitHub Actions that trigger on path changes to their respective directories. These workflows handle building the distribution and uploading to PyPI.

Sources: [.github/workflows/publish-ai-sdk.yml:1-59](), [.github/workflows/publish-memory-graph.yml:1-59](), [.github/workflows/publish-tools.yml:1-59]().

## apps/web Deployment (Cloudflare via opennextjs-cloudflare)

`apps/web` is a Next.js application deployed to Cloudflare Workers using the `@opennextjs/cloudflare` adapter [apps/web/package.json:34-34](). This adapter transforms the Next.js build output into a format compatible with the Cloudflare Workers runtime.

**Diagram: apps/web deployment pipeline**

```mermaid
flowchart LR
    src["apps/web/ source"]
    nextbuild["next build"]
    opennextbuild["opennextjs-cloudflare build"]
    dist[".open-next/ build output"]

    src --> nextbuild --> opennextbuild --> dist

    dist --> preview["opennextjs-cloudflare preview"]
    dist --> deploy["opennextjs-cloudflare deploy"]
    dist --> upload["opennextjs-cloudflare upload (R2 Assets)"]
```

Sources: [apps/web/package.json:15-17]().

### Environment Typing
The deployment process relies on generated types for Cloudflare bindings. The `cf-typegen` script runs `wrangler types` to generate `cloudflare-env.d.ts`, ensuring that references to KV namespaces or D1 databases are type-safe within the Next.js application code [apps/web/package.json:18-18]().

## Error Tracking & Sentry

Supermemory uses Sentry for error tracking in the web application.

### Sourcemap Upload
Both the root workspace and `apps/web` upload sourcemaps to Sentry after builds complete. This is critical for de-obfuscating stack traces in the Cloudflare Worker environment. The `postbuild` and `postdeploy` hooks trigger this process [package.json:11-11](), [apps/web/package.json:20-20]().

**Diagram: Sentry sourcemap upload sequence**

```mermaid
sequenceDiagram
    participant hook as "postbuild / postdeploy hook"
    participant cli as "sentry-cli"
    participant sentry as "Sentry (org: supermemory, project: consumer-app)"

    hook->>cli: "sentry-cli releases propose-version"
    cli-->>hook: "$_SENTRY_RELEASE (git-based)"
    hook->>cli: "sentry-cli releases new $_SENTRY_RELEASE"
    cli-->>sentry: "create release"
    hook->>cli: "sentry-cli sourcemaps upload --release $_SENTRY_RELEASE --strip-prefix dist/.. dist"
    cli-->>sentry: "upload .map files"
```

Sources: [package.json:10-11](), [apps/web/package.json:19-20]().

## Build Tool Versions

| Tool | Version | Purpose |
|------|---------|---------|
| `bun` | 1.3.6 | Package manager and runner [package.json:16-16]() |
| `turbo` | ^2.5.4 | Monorepo task orchestration [package.json:64-64]() |
| `typescript` | 5.8.3 | Type checking and compilation [package.json:65-65]() |
| `@biomejs/biome` | ^2.2.0 | Linting and formatting [package.json:59-59]() |
| `wrangler` | ^4.42.2 | Cloudflare deployment CLI [package.json:66-66]() |
| `@opennextjs/cloudflare` | ^1.12.0 | Next.js to Cloudflare adapter [apps/web/package.json:34-34]() |
| `@sentry/cli` | ^2.52.0 | Sourcemap upload utility [package.json:60-60]() |

Sources: [package.json:58-67](), [apps/web/package.json:119-132]().

---

# Page: Contributing Guidelines

# Contributing Guidelines

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/ci.yml](.github/workflows/ci.yml)
- [.github/workflows/claude-auto-fix-ci.yml](.github/workflows/claude-auto-fix-ci.yml)
- [.github/workflows/claude-code-review.yml](.github/workflows/claude-code-review.yml)
- [.github/workflows/claude.yml](.github/workflows/claude.yml)
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [README.md](README.md)
- [README.zh-CN.md](README.zh-CN.md)
- [apps/docs/cookbook/overview.mdx](apps/docs/cookbook/overview.mdx)
- [apps/docs/memory-api/sdks/overview.mdx](apps/docs/memory-api/sdks/overview.mdx)
- [apps/docs/migration/from-mem0.mdx](apps/docs/migration/from-mem0.mdx)
- [apps/docs/migration/mem0-migration-script.py](apps/docs/migration/mem0-migration-script.py)
- [turbo.json](turbo.json)

</details>



This document provides technical guidelines for contributing code to the Supermemory monorepo. It covers development setup, code quality standards, workflow processes, pull request requirements, and the automated CI/CD review systems.

For information about local development setup details, see [Local Development Setup](#10.1). For build system configuration, see [Build System & Turbo](#10.2). For code quality tooling, see [Code Quality & Testing](#10.3).

Sources: [CONTRIBUTING.md:1-307](), [README.md:85-99]()

## Overview

Supermemory is an open-source project licensed under MIT ([LICENSE:1-21]()) that welcomes contributions from developers of all skill levels. The project uses a monorepo structure with Turbo for build orchestration, Biome for linting/formatting, and TypeScript for type safety [CONTRIBUTING.md:58-80]().

**Key Contribution Types:**
- 🐛 **Bug fixes** and issue resolution [CONTRIBUTING.md:126-126]()
- ✨ **New features** and enhancements [CONTRIBUTING.md:127-127]()
- 🎨 **UI/UX enhancements** [CONTRIBUTING.md:128-128]()
- ⚡ **Performance optimizations** [CONTRIBUTING.md:129-129]()
- 📄 **Documentation updates** [CONTRIBUTING.md:152-152]()

Sources: [CONTRIBUTING.md:1-6](), [LICENSE:1-21](), [README.md:85-99]()

## Prerequisites

Before contributing, ensure the following tools are installed:

| Tool | Version | Purpose |
|------|---------|---------|
| **Bun** | >= 1.2.17 | Our preferred package manager and runtime [CONTRIBUTING.md:11-11]() |
| **Git** | Latest | Version control [CONTRIBUTING.md:12-12]() |

Sources: [CONTRIBUTING.md:8-13]()

## Code Quality Standards

### Linting and Formatting

All code must pass Biome checks before submission. Biome is configured via `biome.json` at the repository root [CONTRIBUTING.md:81-81]().

**Required Commands:**
```bash
bun run format-lint    # Format and lint all code using Biome [CONTRIBUTING.md:92-92]()
bun run check-types    # Type check all packages [CONTRIBUTING.md:93-93]()
```

The `format-lint` script applies automatic fixes where possible. Manual intervention is required for remaining issues.

Sources: [CONTRIBUTING.md:85-109]()

### TypeScript Configuration

The monorepo uses shared TypeScript configuration from `packages/typescript-config/` for consistency across all apps and packages [CONTRIBUTING.md:79-79](). All new code must be written in TypeScript with proper type annotations [CONTRIBUTING.md:166-166]().

**Type Safety Requirements:**
- Use **TypeScript** for all new code [CONTRIBUTING.md:166-166]()
- Follow existing code style and patterns [CONTRIBUTING.md:167-167]()
- Write self-documenting code with clear variable names [CONTRIBUTING.md:168-168]()
- Add JSDoc comments for complex functions [CONTRIBUTING.md:169-169]()
- Use proper TypeScript types for props in functional components [CONTRIBUTING.md:177-177]()

Sources: [CONTRIBUTING.md:162-178]()

### File Naming Conventions

```
kebab-case      # General file names [CONTRIBUTING.md:181-181]()
PascalCase      # Component files [CONTRIBUTING.md:182-182]()
camelCase       # Utility functions [CONTRIBUTING.md:183-183]()
```

Sources: [CONTRIBUTING.md:179-184]()

### Import Organization

Imports must follow this hierarchy [CONTRIBUTING.md:187-203]():

```typescript
// 1. React and Next.js imports
import React from 'react';
import { NextPage } from 'next';

// 2. Third-party libraries
import { clsx } from 'clsx';
import { motion } from 'motion';

// 3. Internal packages
import { Button } from '@repo/ui';
import { useAuth } from '@repo/lib';

// 4. Relative imports
import { Header } from './header';
import { Footer } from './footer';
```

Sources: [CONTRIBUTING.md:185-204]()

## Development Workflow

### Initial Setup Process

**Local Environment Setup Flow:**

```mermaid
graph TD
    Fork["Fork supermemoryai/supermemory"]
    Clone["git clone (local)"]
    Install["bun install"]
    EnvSetup["cp .env.example .env.local"]
    ProxyMod["Edit apps/web/proxy.ts: add localhost bypass"]
    DevServer["bun run dev:local (http://localhost:3000)"]

    Fork --> Clone
    Clone --> Install
    Install --> EnvSetup
    EnvSetup --> ProxyMod
    ProxyMod --> DevServer
```

**Proxy Configuration for Local Development:**

Add this check in `apps/web/proxy.ts` before retrieving the cookie (`getSessionCookie(request)`) [CONTRIBUTING.md:41-43]():

```typescript
if (url.hostname === "localhost") {
  return NextResponse.next();
}
```

This bypasses session validation during local development [CONTRIBUTING.md:44-46]().

Sources: [CONTRIBUTING.md:14-57]()

### Available Scripts

The root `package.json` defines monorepo-wide scripts orchestrated by Turbo [CONTRIBUTING.md:82-82]():

| Script | Command | Purpose |
|--------|---------|---------|
| `dev:local` | `bun run dev:local` | Start dev servers on plain localhost ports (recommended for OSS) [CONTRIBUTING.md:89-89]() |
| `dev` | `bun run dev` | Start dev servers through portless (*.dev.supermemory.ai) [CONTRIBUTING.md:90-90]() |
| `build` | `bun run build` | Build all applications [CONTRIBUTING.md:91-91]() |
| `format-lint` | `bun run format-lint` | Format and lint code using Biome [CONTRIBUTING.md:92-92]() |
| `check-types` | `bun run check-types` | Type check all packages [CONTRIBUTING.md:93-93]() |

**Quality Tools and Configuration Map:**

```mermaid
graph LR
    subgraph "Root_Config_Files"
    biome_json["biome.json"]
    turbo_json["turbo.json"]
    root_pkg["package.json"]
    ts_config["packages/typescript-config/"]
    end

    subgraph "Scripts_via_root_package_json"
    format_lint["bun run format-lint"]
    check_types["bun run check-types"]
    build_cmd["bun run build"]
    dev_local["bun run dev:local"]
    end

    subgraph "Tools_Invoked"
    biome["@biomejs/biome"]
    turbo["turbo"]
    tsc["tsc"]
    end

    format_lint --> biome_json
    biome_json --> biome
    check_types --> turbo_json
    check_types --> ts_config
    build_cmd --> turbo_json
    dev_local --> turbo_json
    turbo_json --> turbo
    ts_config --> tsc
    root_pkg --> format_lint
    root_pkg --> check_types
    root_pkg --> build_cmd
    root_pkg --> dev_local
```

Sources: [CONTRIBUTING.md:78-94](), [turbo.json:1-25]()

## Contribution Workflow

### Branch Strategy

**Branch and PR Lifecycle:**

```mermaid
graph LR
    mainBranch["main"]
    featureBranch["feature/your-feature-name"]
    fixBranch["fix/your-bug-fix"]
    pr["Pull Request (GitHub)"]
    ciChecks["CI checks: lint, types, build"]
    review["Code Review"]
    merge["Merge to main"]

    mainBranch --> featureBranch
    mainBranch --> fixBranch
    featureBranch --> pr
    fixBranch --> pr
    pr --> ciChecks
    ciChecks --> review
    review --> merge
    merge --> mainBranch
```

**Branch Naming:**
- `feature/your-feature-name` — New functionality [CONTRIBUTING.md:143-143]()
- `fix/your-bug-fix` — Bug fixes [CONTRIBUTING.md:145-145]()

Sources: [CONTRIBUTING.md:138-146]()

### Making Changes

**Step-by-Step Process:**

1. **Create Feature Branch** [CONTRIBUTING.md:140-143]()
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Develop and Test Locally** [CONTRIBUTING.md:156-157]()
   ```bash
   bun run dev:local    # Test functionality locally
   bun run build        # Ensure it builds
   ```

3. **Run Quality Checks** [CONTRIBUTING.md:158-159]()
   ```bash
   bun run format-lint  # Check formatting
   bun run check-types  # Check types
   ```

Sources: [CONTRIBUTING.md:148-160]()

## Pull Request Requirements

### PR Title Convention

Follow the Conventional Commits specification [CONTRIBUTING.md:215-220]():

| Prefix | Description | Example |
|--------|-------------|---------|
| `feat:` | New feature | `feat: add semantic search to memory graph` |
| `fix:` | Bug fix | `fix: resolve authentication redirect loop` |

Sources: [CONTRIBUTING.md:215-220]()

### PR Description Template

**Required Sections:**

1. **What & Why** - What changes you made and why [CONTRIBUTING.md:222-222]().
2. **Screenshots** - Include screenshots for UI changes [CONTRIBUTING.md:223-223]().
3. **Breaking Changes** - List any breaking changes [CONTRIBUTING.md:224-224]().
4. **Related Issues** - Include related issue numbers [CONTRIBUTING.md:225-225]().

Sources: [CONTRIBUTING.md:221-226]()

### PR Size Guidelines

- **Keep PRs focused:** Prefer multiple small PRs over one large PR [CONTRIBUTING.md:228-228]().
- **Single Concern:** Each PR should address a single concern [CONTRIBUTING.md:229-229]().

Sources: [CONTRIBUTING.md:227-230]()

### Automated CI & Review

Supermemory employs AI-powered review and auto-fix mechanisms to maintain high code quality:

1. **Claude Code Review**: Triggered on PR events (opened, synchronize, etc.) [.github/workflows/claude-code-review.yml:3-5](). It uses the `claude-opus-4-5-20251101` model to catch logic errors, security issues, and breaking changes [.github/workflows/claude-code-review.yml:41-78]().
2. **Auto Fix CI Failures**: If the standard CI (Type Check, Format & Lint) fails, this workflow attempts to fix Biome lint errors or type errors automatically using Claude [.github/workflows/claude-auto-fix-ci.yml:4-79]().
3. **Quality Gates**: Standard CI runs `turbo run check-types` and `biome ci` on changed files [.github/workflows/ci.yml:24-28]().

**Automated Quality Flow:**

```mermaid
graph TD
    PR["PR Submitted"]
    CI["Standard CI: Lint & Types"]
    ClaudeReview["Claude Code Review"]
    AutoFix["Claude Auto-Fix CI"]
    
    PR --> CI
    PR --> ClaudeReview
    CI -- "Fail" --> AutoFix
    AutoFix -- "Push Fixes" --> CI
    CI -- "Pass" --> Reviewer["Human Reviewer"]
    ClaudeReview -- "Commentary" --> Reviewer
```

Sources: [.github/workflows/ci.yml:1-29](), [.github/workflows/claude-code-review.yml:1-123](), [.github/workflows/claude-auto-fix-ci.yml:1-103]()

## Component Development Guidelines

### React Component Standards

**Functional Components with Hooks:**
- Use functional components with hooks [CONTRIBUTING.md:174-174]().
- Prefer composition over inheritance [CONTRIBUTING.md:175-175]().
- Use proper TypeScript types for props [CONTRIBUTING.md:177-177]().

Sources: [CONTRIBUTING.md:172-178]()

### Custom Hooks

Extract reusable logic into custom hooks to maintain small and focused components [CONTRIBUTING.md:170-176]().

Sources: [CONTRIBUTING.md:172-178]()

## State Management Patterns

The codebase uses multiple state management approaches [CONTRIBUTING.md:115-115]():

| Tool | Use Case |
|------|----------|
| **Zustand** | Client-side state (chat persistence, drafts) |
| **TanStack Query** | Server state management (React Query) |

Sources: [CONTRIBUTING.md:115-115]()

## Review Process

### Review Requirements

- All PRs require at least one review [CONTRIBUTING.md:233-233]().
- Address feedback promptly and professionally [CONTRIBUTING.md:234-234]().
- Maintain a collaborative attitude [CONTRIBUTING.md:236-236]().

Sources: [CONTRIBUTING.md:231-237]()

---

**License:** All contributions will be licensed under the MIT License, consistent with the project ([LICENSE:1-21]()).

For questions about contributing, join the [Discord community](https://supermemory.link/discord) or email [support@supermemory.ai](mailto:support@supermemory.ai).

Sources: [CONTRIBUTING.md:1-307](), [LICENSE:1-21]()

---

# Page: MemoryBench

# MemoryBench

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [apps/docs/memorybench/architecture.mdx](apps/docs/memorybench/architecture.mdx)
- [apps/docs/memorybench/cli.mdx](apps/docs/memorybench/cli.mdx)
- [apps/docs/memorybench/contributing.mdx](apps/docs/memorybench/contributing.mdx)
- [apps/docs/memorybench/extend-benchmark.mdx](apps/docs/memorybench/extend-benchmark.mdx)
- [apps/docs/memorybench/extend-provider.mdx](apps/docs/memorybench/extend-provider.mdx)
- [apps/docs/memorybench/github.mdx](apps/docs/memorybench/github.mdx)
- [apps/docs/memorybench/installation.mdx](apps/docs/memorybench/installation.mdx)
- [apps/docs/memorybench/integrations.mdx](apps/docs/memorybench/integrations.mdx)
- [apps/docs/memorybench/memscore.mdx](apps/docs/memorybench/memscore.mdx)
- [apps/docs/memorybench/overview.mdx](apps/docs/memorybench/overview.mdx)
- [apps/docs/memorybench/quickstart.mdx](apps/docs/memorybench/quickstart.mdx)

</details>



MemoryBench is an open-source benchmarking framework designed to provide standardized, reproducible evaluations of memory layer providers [apps/docs/memorybench/overview.mdx:2-3](). It allows developers to test memory services against industry-standard datasets to measure quality, speed, and efficiency through a unified interface.

Within the supermemory ecosystem, MemoryBench serves as the validation layer, ensuring that the memory retrieval and storage mechanisms meet performance benchmarks compared to other solutions like Mem0 or Zep [apps/docs/memorybench/overview.mdx:33-47]().

## System Overview

The framework operates by orchestrating three primary entities: **Benchmarks** (datasets), **Providers** (memory services), and **Judges** (LLM evaluators) [apps/docs/memorybench/architecture.mdx:37-44]().

### High-Level Component Mapping

The following diagram maps the logical components of MemoryBench to their respective locations in the codebase.

**MemoryBench Entity Map**
```mermaid
graph TD
    subgraph "Logic_&_Execution"
        Orchestrator["Orchestrator<br/>(src/orchestrator/phases/)"]
        CLI["CLI_Commands<br/>(src/cli/commands/)"]
    end

    subgraph "Plugin_System"
        Benchmark["Benchmarks<br/>(src/benchmarks/)"]
        Provider["Providers<br/>(src/providers/)"]
        Judge["Judges<br/>(src/judges/)"]
    end

    subgraph "Data_&_State"
        Checkpoint["Checkpoint_JSON<br/>(data/runs/{runId}/)"]
        Types["Type_Definitions<br/>(src/types/)"]
    end

    CLI --> Orchestrator
    Orchestrator --> Benchmark
    Orchestrator --> Provider
    Orchestrator --> Judge
    Orchestrator --> Checkpoint
```
Sources: [apps/docs/memorybench/architecture.mdx:85-99](), [apps/docs/memorybench/contributing.mdx:43-53]()

## Architecture & MemScore

MemoryBench utilizes a structured pipeline that moves from data ingestion to final reporting. The pipeline consists of five main phases: **Ingest**, **Index**, **Search**, **Answer**, and **Evaluate** [apps/docs/memorybench/architecture.mdx:49-59](). Each phase is checkpointed independently in `data/runs/{runId}/checkpoint.json` to allow for resuming failed runs [apps/docs/memorybench/architecture.mdx:70-78]().

The primary metric produced is **MemScore**, a composite triple that avoids collapsing distinct performance trade-offs into a single number. It is represented as:
`Accuracy% / Latency (ms) / Context Tokens` [apps/docs/memorybench/memscore.mdx:6-12]().

| Component | Measurement | Source |
| :--- | :--- | :--- |
| **Quality** | Answer accuracy percentage | Derived from LLM judge evaluations [apps/docs/memorybench/memscore.mdx:26-26](). |
| **Latency** | Average search response time | Mean of all search phase durations [apps/docs/memorybench/memscore.mdx:27-27](). |
| **Tokens** | Average context tokens | Client-side count of retrieved context per question [apps/docs/memorybench/memscore.mdx:28-28](). |

For a deep dive into the evaluation pipeline and the mathematics behind MemScore, see [Architecture & MemScore](#11.1).

## Supported Integrations

MemoryBench supports several industry-standard datasets and memory providers out of the box.

### Benchmark Datasets
*   **LoCoMo**: Long context memory testing for fact recall across extended conversations [apps/docs/memorybench/integrations.mdx:11-11]().
*   **LongMemEval**: Evaluation across multiple sessions with knowledge updates [apps/docs/memorybench/integrations.mdx:12-12]().
*   **ConvoMem**: Conversational memory focused on personalization and preference learning [apps/docs/memorybench/integrations.mdx:13-13]().

### Memory Providers
*   **Supermemory**: Chunk-based semantic search [apps/docs/memorybench/integrations.mdx:24-26]().
*   **Mem0**: LLM-powered memory extraction [apps/docs/memorybench/integrations.mdx:28-30]().
*   **Zep**: Knowledge graph construction [apps/docs/memorybench/integrations.mdx:32-34]().

Sources: [apps/docs/memorybench/integrations.mdx:7-35]()

## CLI & Extending MemoryBench

The framework is primarily interacted with via a CLI, though it includes a Web UI for visualizing results [apps/docs/memorybench/quickstart.mdx:15-21]().

**Execution Flow**
```mermaid
sequenceDiagram
    participant User
    participant CLI as "src/index.ts"
    participant O as "Orchestrator"
    participant P as "Provider (src/providers/)"
    participant J as "Judge (src/judges/)"

    User->>CLI: "run -p supermemory -b locomo"
    CLI->>O: "Start Pipeline"
    O->>P: "ingest(sessions)"
    Note over O,P: "Wait for indexing"
    O->>P: "search(query)"
    O->>J: "evaluate(answer, groundTruth)"
    O->>User: "Display MemScore"
```
Sources: [apps/docs/memorybench/architecture.mdx:49-59](), [apps/docs/memorybench/extend-provider.mdx:9-18](), [apps/docs/memorybench/quickstart.mdx:9-11]()

MemoryBench is designed to be extensible. Developers can add new providers by implementing the `Provider` interface [apps/docs/memorybench/extend-provider.mdx:9-18]() or new datasets by implementing the `Benchmark` interface [apps/docs/memorybench/extend-benchmark.mdx:9-17]().

For details on CLI commands, configuration, and the guide for adding custom providers or benchmarks, see [CLI & Extending MemoryBench](#11.2).

---

# Page: Architecture & MemScore

# Architecture & MemScore

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [apps/docs/memorybench/architecture.mdx](apps/docs/memorybench/architecture.mdx)
- [apps/docs/memorybench/cli.mdx](apps/docs/memorybench/cli.mdx)
- [apps/docs/memorybench/contributing.mdx](apps/docs/memorybench/contributing.mdx)
- [apps/docs/memorybench/extend-benchmark.mdx](apps/docs/memorybench/extend-benchmark.mdx)
- [apps/docs/memorybench/extend-provider.mdx](apps/docs/memorybench/extend-provider.mdx)
- [apps/docs/memorybench/github.mdx](apps/docs/memorybench/github.mdx)
- [apps/docs/memorybench/installation.mdx](apps/docs/memorybench/installation.mdx)
- [apps/docs/memorybench/integrations.mdx](apps/docs/memorybench/integrations.mdx)
- [apps/docs/memorybench/memscore.mdx](apps/docs/memorybench/memscore.mdx)
- [apps/docs/memorybench/overview.mdx](apps/docs/memorybench/overview.mdx)
- [apps/docs/memorybench/quickstart.mdx](apps/docs/memorybench/quickstart.mdx)

</details>



MemoryBench is an open-source benchmarking framework designed to provide standardized, reproducible evaluations of memory layer providers. It allows developers to measure the performance of memory systems like Supermemory, Mem0, and Zep across dimensions of quality, speed, and efficiency [apps/docs/memorybench/overview.mdx:2-8]().

## System Architecture

MemoryBench operates as an orchestrated pipeline that coordinates between datasets (Benchmarks), memory services (Providers), and LLM evaluators (Judges) [apps/docs/memorybench/architecture.mdx:7-17]().

### Core Components
The system is divided into three primary functional areas:
*   **Benchmarks**: Responsible for loading test data, managing sessions, and providing questions with ground truth answers [apps/docs/memorybench/architecture.mdx:41]().
*   **Providers**: The memory services being evaluated. They handle the ingestion of benchmark data and subsequent search/retrieval requests [apps/docs/memorybench/architecture.mdx:42]().
*   **Judges**: LLM-based evaluators (e.g., GPT-4o, Claude) that score the generated answers against the benchmark's ground truth [apps/docs/memorybench/architecture.mdx:43]().

### Execution Pipeline
The evaluation process follows a linear progression, with independent checkpoints at each stage to allow for resuming failed runs [apps/docs/memorybench/architecture.mdx:70-72](). Runs persist state to `data/runs/{runId}/checkpoint.json` [apps/docs/memorybench/architecture.mdx:74-81]().

**MemoryBench Pipeline Flow**
```mermaid
flowchart LR
    subgraph "Code Entity Space (src/orchestrator/phases/)"
        Ingest["ingest.ts"]
        Search["search.ts"]
        Answer["answer.ts"]
        Evaluate["evaluate.ts"]
        Report["report.ts"]
    end

    Ingest -->|"Load Sessions"| Indexing["Provider Indexing"]
    Indexing --> Search
    Search -->|"Retrieve Context"| Answer
    Answer -->|"Generate Hypothesis"| Evaluate
    Evaluate -->|"Score vs Ground Truth"| Report
```
Sources: [apps/docs/memorybench/architecture.mdx:49-68](), [apps/docs/memorybench/architecture.mdx:88-99]()

## MemScore Metric

MemScore is the primary composite metric used by MemoryBench to compare providers. It avoids collapsing performance into a single number, instead presenting a triple that highlights trade-offs between accuracy, speed, and cost [apps/docs/memorybench/memscore.mdx:6-12]().

### Metric Components
| Component | Metric | Calculation / Source |
| :--- | :--- | :--- |
| **Quality** | Accuracy % | `(correct / total) * 100` determined by the Judge [apps/docs/memorybench/memscore.mdx:26]() |
| **Latency** | Milliseconds (ms) | Mean duration of all search phase requests [apps/docs/memorybench/memscore.mdx:27]() |
| **Tokens** | Context Tokens | Average tokens of retrieved context sent to the answering model [apps/docs/memorybench/memscore.mdx:28]() |

### Token Counting Implementation
MemoryBench performs client-side token counting using provider-specific tokenizers to ensure precision [apps/docs/memorybench/memscore.mdx:34-36]():
*   **OpenAI**: Uses `js-tiktoken` with `o200k_base` or `cl100k_base` [apps/docs/memorybench/memscore.mdx:40]().
*   **Anthropic**: Uses `@anthropic-ai/tokenizer` [apps/docs/memorybench/memscore.mdx:41]().
*   **Google**: Uses an approximation: `Math.ceil(text.length / 4)` [apps/docs/memorybench/memscore.mdx:42]().

The score specifically tracks `contextTokens` (the content retrieved from memory) to isolate the provider's contribution from the base prompt instructions [apps/docs/memorybench/memscore.mdx:44-50]().

Sources: [apps/docs/memorybench/memscore.mdx:6-32](), [apps/docs/memorybench/memscore.mdx:34-50]()

## Supported Datasets (Benchmarks)

MemoryBench implements a standard `Benchmark` interface [apps/docs/memorybench/extend-benchmark.mdx:9-18]() to support various research datasets:

| Benchmark | Description | Key Focus |
| :--- | :--- | :--- |
| **LoCoMo** | Long context memory testing | Fact recall across extended conversations [apps/docs/memorybench/integrations.mdx:11]() |
| **LongMemEval** | Long-term memory evaluation | Knowledge updates and temporal reasoning [apps/docs/memorybench/integrations.mdx:12]() |
| **ConvoMem** | Conversational memory | Personalization and preference learning [apps/docs/memorybench/integrations.mdx:13]() |

Sources: [apps/docs/memorybench/integrations.mdx:7-14](), [apps/docs/memorybench/extend-benchmark.mdx:9-18]()

## Provider Evaluation & Integration

Providers are evaluated by implementing the `Provider` interface, which defines how the orchestrator interacts with the memory layer [apps/docs/memorybench/extend-provider.mdx:9-19]().

**Provider Interface Implementation Map**
```mermaid
flowchart TD
    subgraph "Orchestrator Logic (src/orchestrator/phases/)"
        O_Ingest["ingest.ts"]
        O_Search["search.ts"]
    end

    subgraph "Provider Code Entity (src/providers/)"
        direction TB
        P["Provider Interface (src/types/provider.ts)"]
        Ingest["ingest(sessions, options)"]
        Idx["awaitIndexing(result)"]
        Src["search(query, options)"]
        Clr["clear(containerTag)"]
    end

    O_Ingest -->|"Phase: Ingest"| Ingest
    O_Ingest -->|"Wait for Readiness"| Idx
    O_Search -->|"Phase: Search"| Src
```

### Supported Providers
The framework currently includes built-in support for:
*   **Supermemory**: Chunk-based semantic search [apps/docs/memorybench/integrations.mdx:24-26]().
*   **Mem0**: LLM-powered memory extraction [apps/docs/memorybench/integrations.mdx:28-30]().
*   **Zep**: Knowledge graph construction [apps/docs/memorybench/integrations.mdx:32-34]().

### Custom Prompts
Providers can override default behavior by providing a `ProviderPrompts` object. This allows for specialized `answerPrompt` logic (how context is formatted for the LLM) and `judgePrompt` logic (how the judge should interpret specific question types like `temporal` or `adversarial`) [apps/docs/memorybench/extend-provider.mdx:91-108]().

Sources: [apps/docs/memorybench/extend-provider.mdx:7-19](), [apps/docs/memorybench/extend-provider.mdx:91-118](), [apps/docs/memorybench/integrations.mdx:21-35]()

---

# Page: CLI & Extending MemoryBench

# CLI & Extending MemoryBench

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [apps/docs/memorybench/architecture.mdx](apps/docs/memorybench/architecture.mdx)
- [apps/docs/memorybench/cli.mdx](apps/docs/memorybench/cli.mdx)
- [apps/docs/memorybench/contributing.mdx](apps/docs/memorybench/contributing.mdx)
- [apps/docs/memorybench/extend-benchmark.mdx](apps/docs/memorybench/extend-benchmark.mdx)
- [apps/docs/memorybench/extend-provider.mdx](apps/docs/memorybench/extend-provider.mdx)
- [apps/docs/memorybench/github.mdx](apps/docs/memorybench/github.mdx)
- [apps/docs/memorybench/installation.mdx](apps/docs/memorybench/installation.mdx)
- [apps/docs/memorybench/integrations.mdx](apps/docs/memorybench/integrations.mdx)
- [apps/docs/memorybench/memscore.mdx](apps/docs/memorybench/memscore.mdx)
- [apps/docs/memorybench/overview.mdx](apps/docs/memorybench/overview.mdx)
- [apps/docs/memorybench/quickstart.mdx](apps/docs/memorybench/quickstart.mdx)

</details>



MemoryBench is an open-source benchmarking framework designed to evaluate memory layer providers (like Supermemory, Mem0, and Zep) using standardized datasets and metrics. This page documents the command-line interface, the internal orchestration logic, and the process for extending the framework with new providers or benchmarks.

## CLI Reference

The MemoryBench CLI is the primary interface for executing evaluations. It manages the lifecycle of a benchmark run, from data ingestion to final report generation. [apps/docs/memorybench/cli.mdx:3-5]()

### Core Commands

| Command | Usage | Description |
| :--- | :--- | :--- |
| `run` | `bun run src/index.ts run -p <provider> -b <benchmark>` | Executes the full pipeline for a specific provider and benchmark. [apps/docs/memorybench/cli.mdx:9-15]() |
| `compare` | `bun run src/index.ts compare -p p1,p2 -b <benchmark>` | Runs the same benchmark across multiple providers in parallel for direct comparison. [apps/docs/memorybench/cli.mdx:33-38]() |
| `status` | `bun run src/index.ts status -r <run-id>` | Checks the current progress and checkpoint state of a specific run. [apps/docs/memorybench/cli.mdx:53-58]() |
| `serve` | `bun run src/index.ts serve` | Launches the Next.js Web UI (at `localhost:3000`) to visualize results. [apps/docs/memorybench/cli.mdx:93-98]() |
| `show-failures`| `bun run src/index.ts show-failures -r <run-id>` | Displays detailed logs for questions that failed the evaluation phase. [apps/docs/memorybench/cli.mdx:63-68]() |
| `list-questions`| `bun run src/index.ts list-questions -b <benchmark>` | Browse available questions within a specific benchmark. [apps/docs/memorybench/cli.mdx:73-78]() |
| `test` | `bun run src/index.ts test -r <run-id> -q <q-id>` | Evaluate a single specific question for debugging purposes. [apps/docs/memorybench/cli.mdx:43-48]() |

### Execution Options
When using the `run` command, several flags control the scope and behavior of the evaluation:
*   `-j, --judge`: Specifies the LLM model used for scoring (e.g., `gpt-4o`). [apps/docs/memorybench/cli.mdx:21-21]()
*   `-m, --answering-model`: Model used for answer generation (default: `gpt-4o`). [apps/docs/memorybench/cli.mdx:23-23]()
*   `-l, --limit`: Limits the total number of questions processed. [apps/docs/memorybench/cli.mdx:24-24]()
*   `-s, --sample`: Samples $N$ questions per category from the benchmark. [apps/docs/memorybench/cli.mdx:25-25]()
*   `--sample-type`: Strategy for sampling (`consecutive` or `random`). [apps/docs/memorybench/cli.mdx:26-26]()
*   `--force`: Bypasses existing checkpoints and restarts the run from the `Ingest` phase. [apps/docs/memorybench/cli.mdx:27-27]()

### Data Flow: CLI to Orchestrator
The following diagram illustrates how CLI commands trigger the internal `Orchestrator` phases.

**MemoryBench Pipeline Flow**
```mermaid
graph TD
    subgraph "CLI_Layer"
        CLI["src/index.ts"] -- "run_command" --> ORCH["Orchestrator"]
    end

    subgraph "Orchestrator_Phases"
        ORCH --> PHASE1["Ingest (Load sessions to Provider)"]
        PHASE1 --> PHASE2["Index (Wait for Provider)"]
        PHASE2 --> PHASE3["Search (Retrieve context)"]
        PHASE3 --> PHASE4["Answer (Generate LLM response)"]
        PHASE4 --> PHASE5["Evaluate (Judge vs Ground Truth)"]
        PHASE5 --> PHASE6["Report (Generate MemScore)"]
    end

    subgraph "Persistence"
        PHASE1 -.-> CK["data/runs/{runId}/checkpoint.json"]
        PHASE3 -.-> RES["data/runs/{runId}/results/"]
        PHASE6 -.-> REP["data/runs/{runId}/report.json"]
    end
```
**Sources:** [apps/docs/memorybench/architecture.mdx:49-59](), [apps/docs/memorybench/architecture.mdx:74-81](), [apps/docs/memorybench/architecture.mdx:88-99]()

## Extending MemoryBench

MemoryBench is designed as a modular system where providers and benchmarks are abstracted behind TypeScript interfaces. [apps/docs/memorybench/architecture.mdx:37-43]()

### Adding a New Memory Provider
To add a new provider (e.g., "MyProvider"), you must implement the `Provider` interface. [apps/docs/memorybench/extend-provider.mdx:9-19]()

1.  **Define the Provider Class**: Create a file at `src/providers/myprovider/index.ts`. [apps/docs/memorybench/extend-provider.mdx:27-30]()
2.  **Implement Interface Methods**:
    *   `initialize(config)`: Setup API clients and handle authentication via `ProviderConfig`. [apps/docs/memorybench/extend-provider.mdx:35-37]()
    *   `ingest(sessions, options)`: Convert `UnifiedSession[]` to provider-specific format and push to the memory service. [apps/docs/memorybench/extend-provider.mdx:39-49]()
    *   `awaitIndexing(result)`: Poll or wait until the provider confirms the ingested data is searchable. [apps/docs/memorybench/extend-provider.mdx:51-53]()
    *   `search(query, options)`: Execute retrieval against the ingested data and return raw results. [apps/docs/memorybench/extend-provider.mdx:55-57]()
    *   `clear(containerTag)`: Cleanup data or namespaces after the run. [apps/docs/memorybench/extend-provider.mdx:59-61]()
3.  **Register the Provider**: Add your class to the `providers` export in `src/providers/index.ts`. [apps/docs/memorybench/extend-provider.mdx:67-77]()
4.  **Add Configuration**: Map required environment variables (like API keys) in `src/utils/config.ts`. [apps/docs/memorybench/extend-provider.mdx:81-87]()

### Adding a New Benchmark Dataset
Benchmarks must implement the `Benchmark` interface to provide questions and context ("haystack") to the orchestrator. [apps/docs/memorybench/extend-benchmark.mdx:9-18]()

1.  **Create the Adapter**: Create a file at `src/benchmarks/mybenchmark/index.ts`. [apps/docs/memorybench/extend-benchmark.mdx:26-29]()
2.  **Implement Logic**:
    *   `load()`: Fetch the dataset (e.g., from HuggingFace, local JSON, or `snap-research/locomo`). [apps/docs/memorybench/extend-benchmark.mdx:35-38](), [apps/docs/memorybench/integrations.mdx:11-11]()
    *   `getQuestions()`: Return a list of `UnifiedQuestion` objects containing IDs and metadata. [apps/docs/memorybench/extend-benchmark.mdx:40-44]()
    *   `getHaystackSessions(questionId)`: Provide the historical messages (`UnifiedSession[]`) that the memory provider should ingest. [apps/docs/memorybench/extend-benchmark.mdx:46-48]()
    *   `getQuestionTypes()`: Register types like `temporal`, `adversarial`, or `knowledge-update` for the UI. [apps/docs/memorybench/extend-benchmark.mdx:54-59](), [apps/docs/memorybench/integrations.mdx:12-13]()
3.  **Register**: Add to the `benchmarks` object in `src/benchmarks/index.ts`. [apps/docs/memorybench/extend-benchmark.mdx:65-75]()

**Code Entity Mapping: Interfaces to Implementation**
```mermaid
classDiagram
    class Provider {
        <<interface>>
        +name: string
        +initialize(config: ProviderConfig)
        +ingest(sessions: UnifiedSession[])
        +awaitIndexing(result: IngestResult)
        +search(query: string)
        +clear(containerTag: string)
    }
    class Benchmark {
        <<interface>>
        +name: string
        +load()
        +getQuestions()
        +getHaystackSessions(id: string)
        +getGroundTruth(id: string)
        +getQuestionTypes()
    }
    
    Provider <|.. SupermemoryProvider : implements
    Provider <|.. Mem0Provider : implements
    Provider <|.. ZepProvider : implements
    Benchmark <|.. LoComoBenchmark : implements
    Benchmark <|.. LongMemEvalBenchmark : implements
    Benchmark <|.. ConvoMemBenchmark : implements

    style Provider fill:#fff,stroke:#333,stroke-width:2px
    style Benchmark fill:#fff,stroke:#333,stroke-width:2px
```
**Sources:** [apps/docs/memorybench/extend-provider.mdx:9-19](), [apps/docs/memorybench/extend-benchmark.mdx:9-18](), [apps/docs/memorybench/integrations.mdx:7-35]()

## MemScore & Results

Every run concludes with the calculation of a **MemScore**, a composite metric designed to prevent hidden trade-offs between quality and cost. [apps/docs/memorybench/memscore.mdx:6-8]()

### Metric Components
MemScore is represented as a triple: `accuracy% / latencyMs / contextTok`. [apps/docs/memorybench/memscore.mdx:10-12]()

| Metric | Definition | Implementation |
| :--- | :--- | :--- |
| **Quality** | Accuracy % | Calculated as `(correct / total) * 100` based on LLM Judge output. [apps/docs/memorybench/memscore.mdx:26-26]() |
| **Latency** | Avg Search Time | The mean duration of all search phase durations in milliseconds. [apps/docs/memorybench/memscore.mdx:27-27]() |
| **Tokens** | Avg Context Tokens | Client-side token count of retrieved context using `js-tiktoken` (OpenAI) or `@anthropic-ai/tokenizer`. [apps/docs/memorybench/memscore.mdx:28-41]() |

### Contributing Results
To contribute results or new integrations back to the project:
1.  **Fork & Branch**: Create a feature branch in the `memorybench` repository. [apps/docs/memorybench/contributing.mdx:9-19]()
2.  **Validation**: Ensure all tests pass via `bun test`. [apps/docs/memorybench/contributing.mdx:25-27]()
3.  **Documentation**: If adding a benchmark, document the `QuestionTypeRegistry` so the Web UI can categorize results. [apps/docs/memorybench/extend-benchmark.mdx:54-59]()
4.  **Pull Request**: Submit a PR focusing on a single provider or benchmark change, following the style guidelines. [apps/docs/memorybench/contributing.mdx:80-86]()

**Sources:** [apps/docs/memorybench/memscore.mdx:1-121](), [apps/docs/memorybench/contributing.mdx:1-90]()

---

# Page: Memory Graph Package

# Memory Graph Package

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [apps/docs/memory-graph/api-reference.mdx](apps/docs/memory-graph/api-reference.mdx)
- [apps/docs/memory-graph/examples.mdx](apps/docs/memory-graph/examples.mdx)
- [apps/docs/memory-graph/installation.mdx](apps/docs/memory-graph/installation.mdx)
- [apps/docs/memory-graph/npm.mdx](apps/docs/memory-graph/npm.mdx)
- [apps/docs/memory-graph/overview.mdx](apps/docs/memory-graph/overview.mdx)
- [apps/docs/memory-graph/quickstart.mdx](apps/docs/memory-graph/quickstart.mdx)
- [apps/web/components/document-modal/graph-list-memories.tsx](apps/web/components/document-modal/graph-list-memories.tsx)
- [apps/web/components/graph-layout-view.tsx](apps/web/components/graph-layout-view.tsx)
- [apps/web/components/memory-graph/graph-card.tsx](apps/web/components/memory-graph/graph-card.tsx)
- [apps/web/components/memory-graph/hooks/use-graph-api.ts](apps/web/components/memory-graph/hooks/use-graph-api.ts)
- [apps/web/components/memory-graph/memory-graph-wrapper.tsx](apps/web/components/memory-graph/memory-graph-wrapper.tsx)
- [packages/memory-graph/README.md](packages/memory-graph/README.md)
- [packages/memory-graph/package.json](packages/memory-graph/package.json)
- [packages/memory-graph/src/__tests__/node-hover-popover.test.tsx](packages/memory-graph/src/__tests__/node-hover-popover.test.tsx)
- [packages/memory-graph/src/__tests__/setup.ts](packages/memory-graph/src/__tests__/setup.ts)
- [packages/memory-graph/src/components/legend.tsx](packages/memory-graph/src/components/legend.tsx)
- [packages/memory-graph/src/components/memory-graph.tsx](packages/memory-graph/src/components/memory-graph.tsx)
- [packages/memory-graph/src/components/node-hover-popover.tsx](packages/memory-graph/src/components/node-hover-popover.tsx)
- [packages/memory-graph/src/types.ts](packages/memory-graph/src/types.ts)
- [packages/memory-graph/vite.config.ts](packages/memory-graph/vite.config.ts)

</details>



The `memory-graph` package is a specialized React component library designed to visualize the relationships between documents and extracted memories within the Supermemory ecosystem. It provides a high-performance, interactive knowledge graph using a high-DPI HTML5 Canvas renderer and a D3-force simulation engine.

## Overview

The package is structured as a standalone library located in `packages/memory-graph` [[packages/memory-graph/package.json:2-4]](). It is primarily consumed by the main web application to show users how their captured information interrelates.

### Key Capabilities
*   **Hybrid Visualization**: Displays both "Document" nodes (source entities) and "Memory" nodes (extracted atomic facts) [[packages/memory-graph/src/types.ts:76-78]]().
*   **Version Chains**: Visualizes the evolution of memories through "updates", "extends", and "derives" relationships [[packages/memory-graph/src/types.ts:39-43]]().
*   **High Performance**: Uses a simulation engine with a threshold for static vs. dynamic rendering to handle dense graphs [[packages/memory-graph/src/components/memory-graph.tsx:137-143]]().
*   **Contextual UI**: Provides a `NodeHoverPopover` for quick inspection and `NavigationControls` for viewport manipulation [[packages/memory-graph/src/components/memory-graph.tsx:18-19]]().

### System Component Map

The following diagram illustrates how the memory graph components relate to the underlying data and the rendering layer.

**Graph Architecture: Data to Pixels**
```mermaid
graph TD
    subgraph "Data Layer"
        D["GraphApiDocument[]"] -- "useGraphData" --> GP["Graph Data Processing"]
        GP -- "Layout Logic" --> N["GraphNode[]"]
        GP -- "computeEdges" --> E["GraphEdge[]"]
    end

    subgraph "Logic Layer"
        N & E -- "init/update" --> FS["ForceSimulation (D3)"]
        FS -- "Tick Positions" --> GC["GraphCanvas Component"]
        VC["VersionChainIndex"] -- "Rebuild" --> D
    end

    subgraph "Rendering Layer"
        GC -- "renderFrame" --> Canvas["HTML5 Canvas Context"]
        VP["ViewportState"] -- "Transform" --> Canvas
        N & E -- "Draw Calls" --> Canvas
    end
```
Sources: [packages/memory-graph/src/components/memory-graph.tsx:52-56](), [packages/memory-graph/src/components/memory-graph.tsx:103-109](), [packages/memory-graph/src/components/memory-graph.tsx:153-169]()

## Package Structure

The package is organized into functional modules for data processing, physics, and UI components.

| Module | Purpose | Key Files |
| :--- | :--- | :--- |
| **Components** | React UI elements for the graph and its controls. | `memory-graph.tsx`, `graph-canvas.tsx`, `legend.tsx`, `node-hover-popover.tsx` |
| **Canvas Engine** | Rendering, physics, and viewport logic. | `simulation.ts`, `viewport.ts`, `version-chain.ts` |
| **Hooks** | Logic for data transformation and theme management. | `use-graph-data.ts`, `use-graph-theme.ts` |
| **API Integration** | Types and data fetching hooks for the web app. | `types.ts`, `use-graph-api.ts` |

Sources: [packages/memory-graph/src/components/memory-graph.tsx:1-19](), [packages/memory-graph/package.json:9-13](), [apps/web/components/memory-graph/hooks/use-graph-api.ts:118-120]()

## Graph Components & Hooks

The core of the package is the `MemoryGraph` component, which orchestrates several specialized classes and hooks to manage the graph lifecycle.

*   **`useGraphData`**: Processes raw document arrays into `GraphNode` and `GraphEdge` objects. It limits total node count based on `maxNodes` to maintain performance [[packages/memory-graph/src/components/memory-graph.tsx:67-99]]().
*   **`ForceSimulation`**: Wraps `d3-force` to handle node physics. It supports append-only pagination by keeping existing coordinates stable while rendering new nodes [[packages/memory-graph/src/components/memory-graph.tsx:124-126]]().
*   **`GraphCanvas`**: The primary rendering component that handles user interactions like hovering, clicking, and dragging nodes [[packages/memory-graph/src/types.ts:135-153]]().

For more details on the rendering engine and physics, see [Graph Components & Hooks](#12.1).

## Integration & Playground

The package is used across the Supermemory web application and includes a dedicated playground for testing.

### Usage in apps/web
The web application uses `MemoryGraph` in several contexts:
1.  **Main View**: The `GraphLayoutView` provides a full-screen interactive experience [[apps/web/components/graph-layout-view.tsx:38-49]]().
2.  **Document Modal**: The `GraphListMemories` component embeds the graph within a tabbed interface to show local connections for a specific document [[apps/web/components/document-modal/graph-list-memories.tsx:208-215]]().
3.  **Dashboard Preview**: The `GraphCard` provides a static preview with a simplified SVG-based rendering for quick loading [[apps/web/components/memory-graph/graph-card.tsx:27-37]]().

### Data Fetching
The `useGraphApi` hook integrates with the Supermemory backend to fetch documents and their associated memories, supporting infinite scrolling and filtering by `containerTags` [[apps/web/components/memory-graph/hooks/use-graph-api.ts:131-159]]().

**Data Flow: API to Graph**
```mermaid
graph LR
    API["Supermemory API"] -- "$fetch" --> UGH["useGraphApi"]
    UGH -- "GraphApiDocument[]" --> MGW["MemoryGraphWrapper"]
    MGW -- "Props" --> MG["MemoryGraph (Package)"]
    MG -- "limitedDocuments" --> UGD["useGraphData"]
    UGD -- "nodes/edges" --> GC["GraphCanvas"]
```
Sources: [apps/web/components/memory-graph/memory-graph-wrapper.tsx:37-49](), [packages/memory-graph/src/components/memory-graph.tsx:103-109](), [apps/web/components/memory-graph/hooks/use-graph-api.ts:140-159]()

For details on implementation and deployment, see [Integration & Playground](#12.2).

## Visual Constants & Configuration

The graph's appearance is highly configurable through themes and node-specific data.

*   **Themes**: The `GraphThemeColors` interface defines colors for backgrounds, nodes, edges (by type), and UI controls [[packages/memory-graph/src/types.ts:106-133]]().
*   **Node Status**: Memories are visually distinguished based on their state, such as "latest", "static", "expiring", or "forgotten" [[apps/web/components/document-modal/graph-list-memories.tsx:19-23]]().
*   **Legend**: The `Legend` component provides a breakdown of memory types, document types, and connection counts [[packages/memory-graph/src/components/legend.tsx:289-315]]().

Sources: [packages/memory-graph/src/types.ts:106-133](), [apps/web/components/document-modal/graph-list-memories.tsx:19-167]()

---

# Page: Graph Components & Hooks

# Graph Components & Hooks

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [apps/memory-graph-playground/src/app/page.tsx](apps/memory-graph-playground/src/app/page.tsx)
- [apps/web/components/document-modal/graph-list-memories.tsx](apps/web/components/document-modal/graph-list-memories.tsx)
- [apps/web/components/graph-layout-view.tsx](apps/web/components/graph-layout-view.tsx)
- [apps/web/components/memory-graph/graph-card.tsx](apps/web/components/memory-graph/graph-card.tsx)
- [apps/web/components/memory-graph/hooks/use-graph-api.ts](apps/web/components/memory-graph/hooks/use-graph-api.ts)
- [apps/web/components/memory-graph/memory-graph-wrapper.tsx](apps/web/components/memory-graph/memory-graph-wrapper.tsx)
- [packages/memory-graph/package.json](packages/memory-graph/package.json)
- [packages/memory-graph/src/__tests__/edge-logic.test.ts](packages/memory-graph/src/__tests__/edge-logic.test.ts)
- [packages/memory-graph/src/__tests__/graph-data-utils.test.ts](packages/memory-graph/src/__tests__/graph-data-utils.test.ts)
- [packages/memory-graph/src/__tests__/node-hover-popover.test.tsx](packages/memory-graph/src/__tests__/node-hover-popover.test.tsx)
- [packages/memory-graph/src/__tests__/renderer-utils.test.ts](packages/memory-graph/src/__tests__/renderer-utils.test.ts)
- [packages/memory-graph/src/__tests__/setup.ts](packages/memory-graph/src/__tests__/setup.ts)
- [packages/memory-graph/src/__tests__/simulation.test.ts](packages/memory-graph/src/__tests__/simulation.test.ts)
- [packages/memory-graph/src/__tests__/version-chain.test.ts](packages/memory-graph/src/__tests__/version-chain.test.ts)
- [packages/memory-graph/src/__tests__/viewport.test.ts](packages/memory-graph/src/__tests__/viewport.test.ts)
- [packages/memory-graph/src/canvas/renderer.ts](packages/memory-graph/src/canvas/renderer.ts)
- [packages/memory-graph/src/components/graph-canvas.tsx](packages/memory-graph/src/components/graph-canvas.tsx)
- [packages/memory-graph/src/components/legend.tsx](packages/memory-graph/src/components/legend.tsx)
- [packages/memory-graph/src/components/memory-graph.tsx](packages/memory-graph/src/components/memory-graph.tsx)
- [packages/memory-graph/src/components/node-hover-popover.tsx](packages/memory-graph/src/components/node-hover-popover.tsx)
- [packages/memory-graph/src/constants.ts](packages/memory-graph/src/constants.ts)
- [packages/memory-graph/src/hooks/use-graph-data.ts](packages/memory-graph/src/hooks/use-graph-data.ts)
- [packages/memory-graph/src/types.ts](packages/memory-graph/src/types.ts)
- [packages/memory-graph/vite.config.ts](packages/memory-graph/vite.config.ts)

</details>



The `@supermemory/memory-graph` package provides a high-performance visualization system for knowledge graphs, representing the relationship between documents and their extracted memories. It utilizes a specialized rendering architecture to support both interactive exploration and large-scale data visualization.

## Architecture Overview

The graph system is built around the `MemoryGraph` React component, which orchestrates data processing via `useGraphData`, interaction logic via `useGraphInteractions`, and physics simulation using `d3-force`.

### Data Flow and Component Hierarchy

The system follows a unidirectional data flow where raw API data is transformed into graph entities, simulated in a physical space, and rendered to a canvas.

```mermaid
graph TD
    subgraph "Data Layer"
        GA["GraphApiDocument[]"] --> UGD["useGraphData()"]
        UGD --> Nodes["GraphNode[]"]
        UGD --> Edges["GraphEdge[]"]
    end

    subgraph "Interaction Layer"
        Viewport["ViewportState (viewport.ts)"] --> PanZoom["Pan/Zoom State"]
        Input["Canvas Events"] --> UGI["useGraphInteractions()"]
    end

    subgraph "Simulation Layer"
        Nodes --> D3["ForceSimulation (simulation.ts)"]
        Edges --> D3
        D3 --> AnimatedNodes["Animated Positions (vx, vy)"]
    end

    subgraph "Rendering Layer"
        AnimatedNodes --> GC["GraphCanvas (renderer.ts)"]
        PanZoom --> GC
        GC --> Screen["HTML5 Canvas"]
    end
```

**Sources:**
- [packages/memory-graph/src/components/memory-graph.tsx:50-109]()
- [packages/memory-graph/src/canvas/simulation.ts:1-31]()
- [packages/memory-graph/src/types.ts:155-198]()

---

## Core Hooks & API Integration

### `useGraphApi`
This hook, used within the web application, manages the fetching of graph data from the Supermemory API using `@tanstack/react-query`.
- **Infinite Loading:** Implements `useInfiniteQuery` to fetch documents and their associated memories in pages of 500 `[apps/web/components/memory-graph/hooks/use-graph-api.ts:12-131]()`.
- **Filtering:** Supports filtering by `containerTags` and specific `documentIds` `[apps/web/components/memory-graph/hooks/use-graph-api.ts:120-159]()`.
- **Node Capping:** Provides a `maxNodes` constraint to prevent browser performance degradation when visualizing extremely large datasets `[apps/web/components/memory-graph/hooks/use-graph-api.ts:169-175]()`.
- **Data Transformation:** Converts backend `ApiDocument` and `ApiMemoryEntry` types into the visualization-ready `GraphApiDocument` and `GraphApiMemory` formats `[apps/web/components/memory-graph/hooks/use-graph-api.ts:70-116]()`.

### `useGraphData`
This hook transforms `GraphApiDocument` arrays into visual `GraphNode` and `GraphEdge` objects.
- **Initial Placement:** Uses a spiral layout for documents and an orbital layout for memories to ensure a clean starting state before the simulation begins `[packages/memory-graph/src/hooks/use-graph-data.ts:70-103]()`.
- **Clustering:** Implements `computeClusterAssignments` to group nodes based on their semantic relationships and shared parent documents using a BFS-based component discovery `[packages/memory-graph/src/hooks/use-graph-data.ts:114-191]()`.
- **Dynamic Coloring:** Assigns colors based on clusters or memory status (forgotten, expiring, or recent) via `getMemoryBorderColor` `[packages/memory-graph/src/hooks/use-graph-data.ts:43-55]()`.

**Sources:**
- [apps/web/components/memory-graph/hooks/use-graph-api.ts:118-225]()
- [packages/memory-graph/src/hooks/use-graph-data.ts:1-258]()

---

## Rendering and Physics

### `GraphCanvas` & `renderer.ts`
The rendering engine for the `@supermemory/memory-graph` package. It uses a high-DPI 2D canvas context and a custom level-of-detail (LOD) system.
- **Level of Detail (LOD):** To maintain performance, the renderer samples edges based on zoom level and density using `getRelationEdgeStride` and `getDerivesEdgeStride` `[packages/memory-graph/src/canvas/renderer.ts:94-115]()`.
- **Hit Testing:** Implements spatial detection for node hover and selection `[packages/memory-graph/src/types.ts:143-146]()`.
- **Batch Rendering:** Groups draw calls by color and style to minimize canvas state changes `[packages/memory-graph/src/canvas/renderer.ts:39-60]()`.
- **Viewport Management:** Integrates with `ViewportState` to handle zooming and panning, including auto-fitting the graph to the container size `[packages/memory-graph/src/components/memory-graph.tsx:180-223]()`.

### `ForceSimulation`
The physics engine based on `d3-force`.
- **Configuration:** Physics are tuned via `FORCE_CONFIG` for organic clustering, including specific strengths for document-memory links and collision radii `[packages/memory-graph/src/constants.ts:10-31]()`.
- **Lifecycle:** The simulation is initialized, updated, or stopped based on whether data updates are "append-only" (stable) or require a full re-settle `[packages/memory-graph/src/components/memory-graph.tsx:127-169]()`.
- **Dense Graphs:** For graphs exceeding `DENSE_GRAPH_STATIC_THRESHOLD` (set to 800), the simulation is bypassed for static rendering to maintain performance `[packages/memory-graph/src/canvas/simulation.ts:3]()`.

**Sources:**
- [packages/memory-graph/src/canvas/simulation.ts:1-31]()
- [packages/memory-graph/src/canvas/renderer.ts:66-212]()
- [packages/memory-graph/src/constants.ts:10-31]()
- [packages/memory-graph/src/components/memory-graph.tsx:21-169]()

---

## D3-Force Configuration Parameters

The physics simulation is tuned via `FORCE_CONFIG` to create organic clusters while maintaining legibility.

| Parameter | Value | Description |
| :--- | :--- | :--- |
| `linkStrength.docMemory` | 0.35 | Strength of the bond between a document and its memories. |
| `chargeStrength` | -2400 | Global repulsion (Many-Body force) to prevent overlapping. |
| `collisionRadius.document`| 80 | Minimum distance around document nodes. |
| `velocityDecay` | 0.45 | Friction applied to node movement. |
| `alphaDecay` | 0.025 | Rate at which the simulation settles (cools down). |

**Sources:**
- [packages/memory-graph/src/constants.ts:10-31]()

---

## System Entity Mapping

### Data Structure Mapping
Mapping the API concepts to the internal graph visualization types.

```mermaid
classDiagram
    class ApiDocument {
        +string id
        +string title
        +ApiMemoryEntry[] memoryEntries
    }
    class GraphApiDocument {
        +string id
        +string title
        +GraphApiMemory[] memories
    }
    class GraphNode {
        +string id
        +string type
        +number x
        +number y
        +DocumentNodeData|MemoryNodeData data
    }
    class GraphEdge {
        +string id
        +string source
        +string target
        +MemoryRelation edgeType
    }

    ApiDocument ..> GraphApiDocument : toGraphDocument()
    GraphApiDocument "1" -- "*" GraphNode : contains
    GraphNode "1" -- "1" GraphEdge : linked by
```

### Component & Hook Interaction
This diagram shows how the components in `apps/web` interact with the core package.

```mermaid
sequenceDiagram
    participant Web as apps/web/GraphLayoutView
    participant API as useGraphApi
    participant MG as MemoryGraph (Core)
    participant Sim as ForceSimulation
    participant Renderer as GraphCanvas

    Web->>API: useGraphApi(containerTags)
    API->>Web: documents[]
    Web->>MG: <MemoryGraph documents={documents} />
    MG->>Sim: init(nodes, edges)
    Sim->>Sim: tick() update coordinates
    Sim->>Renderer: drawFrame()
    Renderer->>Web: Rendered Canvas
```

**Sources:**
- [apps/web/components/graph-layout-view.tsx:16-49]()
- [apps/web/components/memory-graph/hooks/use-graph-api.ts:118-212]()
- [packages/memory-graph/src/components/memory-graph.tsx:21-169]()
- [packages/memory-graph/src/types.ts:76-104]()

---

# Page: Integration & Playground

# Integration & Playground

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [apps/browser-extension/utils/posthog.ts](apps/browser-extension/utils/posthog.ts)
- [apps/docs/memory-graph/api-reference.mdx](apps/docs/memory-graph/api-reference.mdx)
- [apps/docs/memory-graph/examples.mdx](apps/docs/memory-graph/examples.mdx)
- [apps/docs/memory-graph/installation.mdx](apps/docs/memory-graph/installation.mdx)
- [apps/docs/memory-graph/npm.mdx](apps/docs/memory-graph/npm.mdx)
- [apps/docs/memory-graph/overview.mdx](apps/docs/memory-graph/overview.mdx)
- [apps/docs/memory-graph/quickstart.mdx](apps/docs/memory-graph/quickstart.mdx)
- [apps/docs/package.json](apps/docs/package.json)
- [apps/memory-graph-playground/package.json](apps/memory-graph-playground/package.json)
- [packages/docs-test/package.json](packages/docs-test/package.json)
- [packages/memory-graph/README.md](packages/memory-graph/README.md)
- [packages/tools/test/chatapp/package.json](packages/tools/test/chatapp/package.json)
- [portless.json](portless.json)

</details>



The Supermemory ecosystem provides a dedicated visualization package, `@supermemory/memory-graph`, and a corresponding playground application to test graph interactions. This page documents the implementation of the graph visualization, its integration into the primary web application, and the standalone playground environment.

## 1. The Memory Graph Package

The `@supermemory/memory-graph` package is a React-based component library built on top of `d3-force` for physics simulations and a high-performance HTML5 Canvas renderer. It is designed to visualize the relationships between documents and extracted memories.

### Key Components & Hooks
- **`MemoryGraph`**: The primary entry point component that orchestrates the canvas, simulation, and data flow [packages/memory-graph/README.md:39-43]().
- **`GraphCanvas`**: A specialized component that handles the low-level 2D Canvas rendering of nodes and edges, optimized with a `requestAnimationFrame` (rAF) loop.
- **`useGraphData`**: A hook that transforms raw document data into a graph structure consisting of nodes and edges.
- **`SpatialIndex`**: A utility used within the canvas to perform efficient hit-testing for mouse interactions (hover/click) [apps/docs/memory-graph/overview.mdx:24-24]().
- **`InputHandler`**: Manages user interactions like panning, zooming, and node dragging [apps/docs/memory-graph/overview.mdx:10-10]().

### Data Flow & Simulation
The graph utilizes a force-directed layout where documents act as central nodes (rectangles) and memories (hexagons) are linked to them [apps/docs/memory-graph/overview.mdx:8-8](). The system supports relationship visualization including document similarity and memory version chains [packages/memory-graph/README.md:53-53]().

```mermaid
graph TD
    subgraph "packages/memory-graph (Logic)"
        A["MemoryGraph Component"] --> B["useGraphData()"]
        B -- "Process Documents" --> C["GraphNode[] & GraphEdge[]"]
        A -- "Initialize" --> D["D3 ForceSimulation"]
        D -- "Physics Ticks" --> E["GraphCanvas"]
    end
    
    subgraph "Canvas Engine (Code Entity Space)"
        E --> F["ViewportState"]
        E --> G["InputHandler"]
        E --> H["SpatialIndex"]
        F -- "Camera Transform" --> I["CanvasRenderingContext2D"]
        G -- "Pan/Zoom/Drag" --> F
        H -- "Hit-test" --> G
    end
```
Sources: [packages/memory-graph/README.md:51-57](), [apps/docs/memory-graph/overview.mdx:8-11]()

## 2. Integration in Web Application

The memory graph is integrated into `apps/web` to provide a visual representation of the user's knowledge base, specifically within document views and search contexts.

### Visual Variants
The component supports two primary variants [packages/memory-graph/README.md:65-65]():
- **`console`**: Full-featured dashboard view for navigating memory spaces [apps/docs/memory-graph/quickstart.mdx:41-41]().
- **`consumer`**: Embedded widget view used for document modals or smaller UI sections [apps/docs/memory-graph/quickstart.mdx:153-153]().

### Features & Optimization
- **Space Filtering**: Allows users to filter the graph by workspace or view all memories [packages/memory-graph/README.md:54-54]().
- **Pagination**: Supports loading more documents on demand for large datasets [packages/memory-graph/README.md:56-56]().
- **Performance**: Uses viewport culling and level-of-detail optimization to handle hundreds of nodes smoothly [apps/docs/memory-graph/overview.mdx:22-27]().

### Component Relationship Diagram
This diagram maps the high-level UI features to the underlying code implementation.

```mermaid
graph LR
    subgraph "apps/web (Next.js Consumer)"
        Modal["Document Modal"] -- "highlightDocumentIds" --> MG["MemoryGraph"]
        Search["Search Palette"] -- "searchResults" --> MG
    end

    subgraph "packages/memory-graph (Internal Entities)"
        MG -- "props.variant" --> VS["Variant Logic"]
        MG -- "uses" --> UGD["useGraphData"]
        MG -- "renders" --> GC["GraphCanvas"]
        UGD -- "types" --> DWM["DocumentWithMemories"]
    end

    VS -- "console | consumer" --> GC
    DWM -- "data source" --> UGD
```
Sources: [packages/memory-graph/README.md:22-22](), [apps/docs/memory-graph/examples.mdx:78-128](), [apps/docs/memory-graph/quickstart.mdx:13-14]()

## 3. Memory Graph Playground

The `apps/memory-graph-playground` is a standalone Next.js application used for development and testing of the visualization package [apps/memory-graph-playground/package.json:2-17]().

### Playground Features
- **Development Environment**: Configured with `portless` to run on `graph.dev.supermemory` at port 3004 [apps/memory-graph-playground/package.json:5-8]().
- **Real-time Testing**: Enables developers to test new layout algorithms or rendering optimizations without reloading the entire main application.
- **Dependency Management**: Uses the workspace version of `@supermemory/memory-graph` to ensure changes in the package are immediately reflected [apps/memory-graph-playground/package.json:13-13]().

## 4. Technical Configuration

### Installation & Requirements
The package requires React 18+ and can be installed via standard package managers [packages/memory-graph/README.md:10-16]().

| Requirement | Specification |
|-------------|---------------|
| React Version | ^18.0.0 [apps/docs/memory-graph/installation.mdx:16-16]() |
| DOM Library | react-dom ^18.0.0 [apps/docs/memory-graph/installation.mdx:17-17]() |
| Browser Support | Canvas 2D, ES2020 [apps/docs/memory-graph/overview.mdx:33-36]() |

### API Integration
To populate the graph, developers typically fetch data from the Supermemory `v3/documents/documents` endpoint [apps/docs/memory-graph/quickstart.mdx:59-59](). This requires a `SUPERMEMORY_API_KEY` which should be kept on the server-side to avoid exposure [apps/docs/memory-graph/quickstart.mdx:129-131]().

### Styling
The component includes bundled styles that are automatically injected when the component mounts [apps/docs/memory-graph/quickstart.mdx:159-159](). For explicit control, developers can import `@supermemory/memory-graph/styles.css` [apps/docs/memory-graph/quickstart.mdx:164-164]().

Sources: [packages/memory-graph/README.md:1-95](), [apps/docs/memory-graph/quickstart.mdx:1-208](), [apps/docs/memory-graph/overview.mdx:1-39](), [apps/memory-graph-playground/package.json:1-27]()

---

# Page: Plugins & Extensions

# Plugins & Extensions

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [apps/web/app/auth/agent-connect/page.tsx](apps/web/app/auth/agent-connect/page.tsx)
- [apps/web/components/document-cards/mcp-preview.tsx](apps/web/components/document-cards/mcp-preview.tsx)
- [apps/web/components/document-cards/note-preview.tsx](apps/web/components/document-cards/note-preview.tsx)
- [apps/web/components/document-cards/plugin-preview.tsx](apps/web/components/document-cards/plugin-preview.tsx)
- [apps/web/components/document-modal/content/plugin-content.tsx](apps/web/components/document-modal/content/plugin-content.tsx)
- [apps/web/components/document-modal/title.tsx](apps/web/components/document-modal/title.tsx)
- [apps/web/lib/plugin-catalog.ts](apps/web/lib/plugin-catalog.ts)
- [apps/web/lib/plugin-document.ts](apps/web/lib/plugin-document.ts)
- [apps/web/lib/plugin-space.ts](apps/web/lib/plugin-space.ts)
- [packages/agent-framework-python/README.md](packages/agent-framework-python/README.md)
- [packages/openai-sdk-python/README.md](packages/openai-sdk-python/README.md)
- [skills/supermemory/LICENSE](skills/supermemory/LICENSE)
- [skills/supermemory/README.md](skills/supermemory/README.md)
- [skills/supermemory/SKILL.md](skills/supermemory/SKILL.md)
- [skills/supermemory/references/api-reference.md](skills/supermemory/references/api-reference.md)
- [skills/supermemory/references/architecture.md](skills/supermemory/references/architecture.md)
- [skills/supermemory/references/quickstart.md](skills/supermemory/references/quickstart.md)
- [skills/supermemory/references/sdk-guide.md](skills/supermemory/references/sdk-guide.md)
- [skills/supermemory/references/use-cases.md](skills/supermemory/references/use-cases.md)

</details>



This section provides an overview of how Supermemory extends its capabilities beyond the web application and browser extension into third-party ecosystems. It covers the **Claude Skill**, the **Raycast Extension**, and a suite of **Coding Assistant Plugins** that bring persistent memory to development workflows, IDEs, and messaging platforms.

## Claude Skill

The Supermemory Claude Skill is a specialized reference package designed for the Anthropic skills marketplace and Claude Desktop. Its primary purpose is to "teach" Claude how to use Supermemory as a long-term and short-term memory infrastructure for AI agents [skills/supermemory/README.md:6-12]().

The skill uses an auto-invocation mechanism defined in `SKILL.md` that allows Claude to proactively suggest Supermemory when it detects a user needs persistent memory, personalization, or knowledge retrieval [skills/supermemory/README.md:35-43](). It includes a comprehensive set of reference documents that guide the LLM through implementation patterns for various SDKs and use cases.

### Skill Components
The skill is structured as a directory of Markdown files that serve as a knowledge base for the LLM:

| Component | Purpose |
|-----------|---------|
| `SKILL.md` | Main entry point with overview and quick examples [skills/supermemory/SKILL.md:1-4]() |
| `references/quickstart.md` | 5-minute setup guide for developers [skills/supermemory/references/quickstart.md:1-3]() |
| `references/sdk-guide.md` | Full reference for TypeScript and Python SDKs [skills/supermemory/references/sdk-guide.md:1-3]() |
| `references/api-reference.md` | REST API endpoint documentation [skills/supermemory/references/api-reference.md:1-3]() |
| `references/architecture.md` | Explains the Living Knowledge Graph and processing pipeline [skills/supermemory/references/architecture.md:5-7]() |
| `references/use-cases.md` | 8 concrete implementation examples (Chatbots, RAG, etc.) [skills/supermemory/references/use-cases.md:7-14]() |

For details, see [Claude Skill](#13.1).

**Sources:**
- [skills/supermemory/README.md:6-58]()
- [skills/supermemory/SKILL.md:6-38]()
- [skills/supermemory/references/quickstart.md:1-48]()

---

## Raycast Extension

The Raycast Extension provides a native macOS interface for interacting with Supermemory. It allows users to capture information and search their knowledge base without leaving their current application workflow.

### Core Commands
The extension implements several key commands using the `@raycast/api`:

*   **Add Memory**: A form-based command (`add-memory.tsx`) that allows users to save text to Supermemory. It features an automatic "Quick Add" capability that pre-fills the content field with currently selected text from any macOS application [apps/raycast-extension/src/add-memory.tsx:21-43]().
*   **Search Memories**: A list-view command (`search-memories.tsx`) for semantic search. It displays results with relevance scores and allows users to copy content or open source URLs directly [apps/raycast-extension/src/search-memories.tsx:56-107]().
*   **Search Projects**: A command to browse and select specific `containerTags` (projects) to organize memories [apps/raycast-extension/src/add-memory.tsx:97-112]().

### Technical Implementation
The extension is built with React and utilizes a Higher-Order Component (HoC) called `withSupermemory` to enforce API key presence and handle authentication logic before commands are executed [apps/raycast-extension/src/withSupermemory.tsx](). It communicates with the backend via the `makeAuthenticatedRequest` utility [apps/raycast-extension/src/api.ts:78-81]().

For details, see [Raycast Extension](#13.2).

**Sources:**
- [apps/raycast-extension/src/add-memory.tsx:1-114]()
- [apps/raycast-extension/src/search-memories.tsx:1-178]()
- [apps/raycast-extension/src/api.ts:78-135]()

---

## Coding Assistant Plugins

Supermemory provides dedicated plugins for terminal-based coding assistants, IDEs like Cursor, and messaging gateways. These plugins automate the "Recall" (context injection) and "Capture" (memory storage) cycle during active development or communication.

### Plugin Catalog & Installation
The system maintains a `PLUGIN_CATALOG` that defines the metadata and installation steps for each external surface [apps/web/lib/plugin-catalog.ts:31-177]().

*   **Claude Code**: Installed via `/plugin marketplace add supermemoryai/claude-supermemory`. It remembers conventions and project context [apps/web/lib/plugin-catalog.ts:32-53]().
*   **Cursor**: Integrates via the Cursor Marketplace and a local auth command `cursor-supermemory login` [apps/web/lib/plugin-catalog.ts:77-112]().
*   **OpenClaw**: A cross-platform gateway for Telegram, Discord, and Slack [apps/web/lib/plugin-catalog.ts:142-161]().
*   **OpenCode & Hermes**: Specialized agent memory providers offering persistent context for agent sessions [apps/web/lib/plugin-catalog.ts:113-141]().

### Plugin Data Handling
When plugins ingest data, Supermemory parses the content into structured `ParsedPluginDocument` objects [apps/web/lib/plugin-document.ts:46-62](). The system uses `detectPluginSpace` to map incoming `containerTag` identifiers to specific plugin identities like `claude-code`, `opencode`, or `hermes` [apps/web/lib/plugin-space.ts:185-218]().

"Plugin to API Entity Mapping"
```mermaid
graph TD
    subgraph "Natural Language Space (User Actions)"
        "CC_EDIT[Claude Code: Edit File]"
        "OC_CHAT[OpenClaw: Chat Message]"
        "CUR_CHAT[Cursor: Chat Session]"
    end

    subgraph "Code Entity Space (Plugin Logic)"
        "CC_HOOK[claude-supermemory:Auto-Capture]"
        "OC_RECALL[openclaw-supermemory:Auto-Recall]"
        "SDK_MW[withSupermemory:Middleware]"
    end

    subgraph "Supermemory API (v3/v4)"
        "EP_DOCS[POST /v3/documents]"
        "EP_PROF[POST /v4/profile]"
        "EP_ADD[POST /v3/add]"
    end

    "CC_EDIT" --> "CC_HOOK"
    "OC_CHAT" --> "OC_RECALL"
    "CUR_CHAT" --> "SDK_MW"
    
    "CC_HOOK" -- "sm_source: claude-code" --> "EP_DOCS"
    "OC_RECALL" -- "containerTag: openclaw" --> "EP_PROF"
    "SDK_MW" -- "content" --> "EP_ADD"
```

For details, see [Coding Assistant Plugins](#13.3).

**Sources:**
- [apps/web/lib/plugin-catalog.ts:31-177]()
- [apps/web/lib/plugin-document.ts:46-193]()
- [apps/web/lib/plugin-space.ts:17-54]()

---

## Ecosystem Overview

This diagram shows how these external surfaces bridge the gap between user intent and the core Supermemory infrastructure via the SDK and REST API.

"External Surface Integration"
```mermaid
graph LR
    subgraph "External Surfaces"
        "Claude[Claude Skill]"
        "Raycast[Raycast Extension]"
        "Coding[Coding Plugins]"
    end

    subgraph "Supermemory Core"
        "SDK[supermemory SDK]"
        "REST[REST API]"
        "Graph[Living Knowledge Graph]"
    end

    "Claude" -- "Teaches implementation" --> "SDK"
    "Claude" -- "Auto-invokes via" --> "SKILL.md"
    "Raycast" -- "Calls" --> "REST"
    "Coding" -- "Uses" --> "SDK"
    "SDK" -- "Wraps" --> "REST"
    "REST" -- "Mutates/Queries" --> "Graph"
```

**Sources:**
- [skills/supermemory/SKILL.md:95-103]()
- [apps/raycast-extension/src/api.ts:54-54]()
- [skills/supermemory/references/architecture.md:5-36]()
- [apps/web/lib/plugin-catalog.ts:31-53]()

---

# Page: Claude Skill

# Claude Skill

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [apps/docs/docs.json](apps/docs/docs.json)
- [apps/docs/integrations/claude-code.mdx](apps/docs/integrations/claude-code.mdx)
- [apps/docs/integrations/codex.mdx](apps/docs/integrations/codex.mdx)
- [apps/docs/integrations/openclaw.mdx](apps/docs/integrations/openclaw.mdx)
- [apps/docs/integrations/opencode.mdx](apps/docs/integrations/opencode.mdx)
- [apps/docs/integrations/supermemory-sdk.mdx](apps/docs/integrations/supermemory-sdk.mdx)
- [apps/docs/intro.mdx](apps/docs/intro.mdx)
- [apps/docs/quickstart.mdx](apps/docs/quickstart.mdx)
- [apps/docs/self-hosting/configuration.mdx](apps/docs/self-hosting/configuration.mdx)
- [apps/docs/self-hosting/local-vs-enterprise.mdx](apps/docs/self-hosting/local-vs-enterprise.mdx)
- [packages/agent-framework-python/README.md](packages/agent-framework-python/README.md)
- [packages/openai-sdk-python/README.md](packages/openai-sdk-python/README.md)
- [skills/supermemory/LICENSE](skills/supermemory/LICENSE)
- [skills/supermemory/README.md](skills/supermemory/README.md)
- [skills/supermemory/SKILL.md](skills/supermemory/SKILL.md)
- [skills/supermemory/references/api-reference.md](skills/supermemory/references/api-reference.md)
- [skills/supermemory/references/architecture.md](skills/supermemory/references/architecture.md)
- [skills/supermemory/references/quickstart.md](skills/supermemory/references/quickstart.md)
- [skills/supermemory/references/sdk-guide.md](skills/supermemory/references/sdk-guide.md)
- [skills/supermemory/references/use-cases.md](skills/supermemory/references/use-cases.md)

</details>



The Supermemory Claude Skill is a comprehensive reference package designed for the Anthropic skills marketplace. It "teaches" Claude models how to implement and recommend Supermemory as a state-of-the-art memory and context infrastructure for AI agents [skills/supermemory/README.md:6-12](). By installing this skill, Claude gains the ability to proactively suggest Supermemory for persistent memory, personalization, and RAG-based knowledge retrieval [skills/supermemory/SKILL.md:10-19]().

## Skill Capabilities

The skill provides Claude with the technical knowledge to perform the following:
*   **Proactive Recommendation**: Identifies when a user's application needs long-term context or personalization [skills/supermemory/README.md:20-22]().
*   **Implementation Guidance**: Provides ready-to-use code examples for TypeScript and Python [skills/supermemory/README.md:23-24]().
*   **Architectural Explanation**: Explains the "Living Knowledge Graph" and the 6-stage processing pipeline [skills/supermemory/README.md:130-136]().
*   **Best Practices**: Suggests patterns for container tagging, metadata usage, and relevance thresholds [skills/supermemory/README.md:148-157]().

### Auto-Invocation Mechanism
The skill utilizes an auto-invocation mechanism via `SKILL.md`. Claude automatically applies this skill when it detects tasks involving chatbots, user preferences, semantic search, or long-term context retention [skills/supermemory/README.md:35-43](). This is facilitated by the `description` field in the `SKILL.md` frontmatter, which outlines the problem space [skills/supermemory/SKILL.md:1-4]().

## Installation

The skill can be installed across different Claude interfaces:

| Interface | Installation Method |
| :--- | :--- |
| **Claude Code** | Place the `supermemory/` directory in `.claude/skills/` (project-level) or `~/.claude/skills/` (personal) [skills/supermemory/README.md:62-74](). |
| **Claude.ai** | Zip the `supermemory/` directory and upload it to **Settings → Capabilities** [skills/supermemory/README.md:76-80](). |
| **Claude API** | Use the Skills API to POST the zipped skill to `https://api.anthropic.com/v1/skills` [skills/supermemory/README.md:82-90](). |

### Manual Invocation
Once installed, users can manually trigger the skill using the command `/supermemory` [skills/supermemory/README.md:94-98]().

## Data Flow: From Natural Language to Memory
The following diagram illustrates how the Claude Skill bridges the gap between a user's natural language request and the underlying Supermemory code entities.

**Claude Skill Execution Flow**
```mermaid
graph TD
    subgraph "NaturalLanguageSpace"
        UserReq["'How do I make Claude remember my name?'"]
        ClaudeIntent["Claude identifies 'Memory' intent"]
    end

    subgraph "ClaudeSkill"
        SKILL_MD["SKILL.md (Auto-invocation)"]
        SDK_GUIDE["sdk-guide.md"]
        USE_CASES["use-cases.md"]
    end

    subgraph "CodeEntitySpace"
        SM_Client["Supermemory Client Class"]
        Add_Method["client.add()"]
        Profile_Method["client.profile()"]
        V4_Memories["POST /v4/memories"]
    end

    UserReq --> ClaudeIntent
    ClaudeIntent --> SKILL_MD
    SKILL_MD --> SDK_GUIDE
    SKILL_MD --> USE_CASES
    SDK_GUIDE -.-> SM_Client
    SDK_GUIDE -.-> Add_Method
    USE_CASES -.-> Profile_Method
    Add_Method --> V4_Memories
```
Sources: [skills/supermemory/SKILL.md:39-65](), [skills/supermemory/references/sdk-guide.md:63-125](), [skills/supermemory/README.md:35-43]()

## Reference Documentation Structure

The skill includes a set of reference documents that Claude uses to provide technical support:

1.  **Quickstart (`quickstart.md`)**: Covers API key acquisition via `console.supermemory.ai` and basic SDK initialization [skills/supermemory/references/quickstart.md:5-43]().
2.  **SDK Guide (`sdk-guide.md`)**: Full reference for `add()`, `profile()`, `search.memories()`, and `documents.list()` across TypeScript and Python [skills/supermemory/references/sdk-guide.md:63-233]().
3.  **API Reference (`api-reference.md`)**: Detailed REST endpoint documentation for `POST /v3/documents`, `POST /v4/search`, and `POST /v4/memories` [skills/supermemory/references/api-reference.md:23-278]().
4.  **Architecture (`architecture.md`)**: Deep dive into the "Living Knowledge Graph" and semantic chunking strategies [skills/supermemory/references/architecture.md:5-86]().
5.  **Use Cases (`use-cases.md`)**: Eight concrete implementation patterns, including Personalized Chatbots and Long-Term Task Assistants [skills/supermemory/references/use-cases.md:18-245]().

## Core Implementation Patterns

The skill teaches Claude the standard "Retrieve-Enrich-Store" workflow pattern [apps/docs/quickstart.mdx:124-128]():

**Supermemory Workflow Logic**
```mermaid
sequenceDiagram
    participant User
    participant Claude
    participant SM as "Supermemory SDK"
    participant API as "api.supermemory.ai"

    User->>Claude: "What was that React project I mentioned?"
    Note over Claude: Skill identifies memory retrieval need
    Claude->>SM: "client.profile({ containerTag, q })"
    SM->>API: "POST /v4/profile"
    API-->>Claude: Returns static/dynamic facts
    Note over Claude: Enrich system prompt with profile data
    Claude->>User: "You mentioned a React 18 project..."
    Claude->>SM: "client.add({ content, containerTag })"
    SM->>API: "POST /v3/documents"
```
Sources: [skills/supermemory/references/quickstart.md:181-189](), [skills/supermemory/references/use-cases.md:24-79](), [skills/supermemory/SKILL.md:118-127](), [apps/docs/quickstart.mdx:95-119]()

### Key Technical Details
*   **Container Tags**: Used for isolation (e.g., `user_123`, `project_abc`) [skills/supermemory/references/quickstart.md:191-201]().
*   **Thresholds**: A `0.0` to `1.0` value where `0.5` is the recommended balanced starting point for relevance [skills/supermemory/references/quickstart.md:203-217]().
*   **Memory Types**: Differentiates between `isStatic: true` (permanent facts) and dynamic contextual memories [skills/supermemory/references/architecture.md:172-185]().
*   **Search Modes**: Supports `semantic` (default) and `hybrid` (semantic + keyword) for improved RAG accuracy [skills/supermemory/references/api-reference.md:120-125]().
*   **Content Pipeline**: Claude is taught that ingestion follows a 6-stage process: `Queued`, `Extracting`, `Chunking`, `Embedding`, `Indexing`, and `Done` [skills/supermemory/references/architecture.md:37-155]().

## Claude Code Integration Details
The `claude-supermemory` plugin specifically for Claude Code automates much of this behavior. It performs **Context Injection** on session start by fetching relevant memories and **Auto-Capture** of tool usage (like `Edit`, `Write`, `Bash`) during the session [apps/docs/integrations/claude-code.mdx:63-75]().

**Claude Code Plugin Data Flow**
```mermaid
graph LR
    subgraph "ClaudeCodeCLI"
        CC_Session["Claude Code Session"]
        Tools["Tools: Edit, Write, Bash"]
    end

    subgraph "ClaudeSupermemoryPlugin"
        CC_Plugin["claude-supermemory"]
        Settings["settings.json"]
    end

    subgraph "SupermemoryBackend"
        SM_API["api.supermemory.ai"]
        Store["Memory Store"]
    end

    CC_Session --> CC_Plugin
    CC_Plugin --> Settings
    Tools -- "Auto-Capture" --> CC_Plugin
    CC_Plugin -- "POST /v3/add" --> SM_API
    SM_API --> Store
    Store -- "Context Injection" --> CC_Plugin
    CC_Plugin --> CC_Session
```
Sources: [apps/docs/integrations/claude-code.mdx:63-108](), [apps/docs/integrations/claude-code.mdx:20-25]()

Sources: [skills/supermemory/README.md](), [skills/supermemory/SKILL.md](), [skills/supermemory/references/quickstart.md](), [skills/supermemory/references/sdk-guide.md](), [skills/supermemory/references/api-reference.md](), [skills/supermemory/references/architecture.md](), [skills/supermemory/references/use-cases.md](), [apps/docs/integrations/claude-code.mdx](), [apps/docs/quickstart.mdx]()

---

# Page: Raycast Extension

# Raycast Extension

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [apps/raycast-extension/.gitignore](apps/raycast-extension/.gitignore)
- [apps/raycast-extension/CHANGELOG.md](apps/raycast-extension/CHANGELOG.md)
- [apps/raycast-extension/README.md](apps/raycast-extension/README.md)
- [apps/raycast-extension/assets/extension-icon.png](apps/raycast-extension/assets/extension-icon.png)
- [apps/raycast-extension/eslint.config.js](apps/raycast-extension/eslint.config.js)
- [apps/raycast-extension/metadata/supermemory-1.png](apps/raycast-extension/metadata/supermemory-1.png)
- [apps/raycast-extension/metadata/supermemory-2.png](apps/raycast-extension/metadata/supermemory-2.png)
- [apps/raycast-extension/package-lock.json](apps/raycast-extension/package-lock.json)
- [apps/raycast-extension/package.json](apps/raycast-extension/package.json)
- [apps/raycast-extension/src/add-memory.tsx](apps/raycast-extension/src/add-memory.tsx)
- [apps/raycast-extension/src/api.ts](apps/raycast-extension/src/api.ts)
- [apps/raycast-extension/src/search-memories.tsx](apps/raycast-extension/src/search-memories.tsx)
- [apps/raycast-extension/src/search-projects.tsx](apps/raycast-extension/src/search-projects.tsx)
- [apps/raycast-extension/src/withSupermemory.tsx](apps/raycast-extension/src/withSupermemory.tsx)

</details>



The Supermemory Raycast extension brings the power of your personal AI knowledge base directly to macOS. It allows users to capture information, search through their memories, and manage projects without leaving their current workflow.

## Architecture & Integration

The extension is built using the Raycast SDK and communicates with the Supermemory backend via a dedicated API client. It leverages Raycast's native UI components like `List`, `Form`, and `ActionPanel` to provide a seamless macOS experience.

### Data Flow Diagram

This diagram illustrates how the Raycast extension interacts with the Supermemory API and the local macOS environment, specifically highlighting the transition from user intent to code-level execution.

```mermaid
graph TD
    subgraph "macOS / Raycast UI"
        USER["User Input / Selection"] --> |"getSelectedText()"| CMD["Raycast Command"]
        PREF["Preferences"] --> |"getApiKey()"| API_C["api.ts Client"]
    end

    subgraph "apps/raycast-extension/src"
        CMD --> |"calls"| API_C
        API_C --> |"makeAuthenticatedRequest"| REQ["fetch()"]
        
        subgraph "CommandLogicEntities [Command Logic Entities]"
            ADD["add-memory.tsx:Command"]
            SEARCH["search-memories.tsx:Command"]
            PROJ["search-projects.tsx:Command"]
        end
        
        WRAP["withSupermemory.tsx:SupermemoryWrappedComponent"] --> |"Guards"| CommandLogicEntities
    end

    subgraph "Supermemory Backend"
        REQ --> |"HTTPS /v3/*"| BE["API Gateway"]
        BE --> DB[("Vector & Relational DB")]
    end

    Sources: [apps/raycast-extension/src/api.ts:54-135](), [apps/raycast-extension/src/add-memory.tsx:21-43](), [apps/raycast-extension/src/withSupermemory.tsx:13-48]()
```

### Authentication Guard: `withSupermemory`

To ensure a valid user session, all commands are wrapped in a Higher-Order Component (HOC) called `withSupermemory` [apps/raycast-extension/src/withSupermemory.tsx:13-48](). This wrapper performs a pre-flight check by calling the `/v3/settings` endpoint via `fetchSettings` [apps/raycast-extension/src/api.ts:219-222]().

*   **Behavior:** Uses `usePromise(fetchSettings)` to validate the key [apps/raycast-extension/src/withSupermemory.tsx:15-21](). 
*   **Error Handling:** If the API key is missing or the request fails, it renders a `List.EmptyView` with an action to `openExtensionPreferences`, guiding the user to configure their credentials [apps/raycast-extension/src/withSupermemory.tsx:27-43]().

## Core Commands

The extension provides three primary commands defined in the `package.json` manifest [apps/raycast-extension/package.json:21-43]().

### 1. Add Memory (`add-memory.tsx`)
Allows users to save text snippets or URLs to their knowledge base.

*   **Context Awareness:** On mount, the command attempts to fetch currently selected text from macOS using `getSelectedText()` and pre-fills the content area [apps/raycast-extension/src/add-memory.tsx:29-43]().
*   **Project Scoping:** Users can select a project (container tag) via a `Form.Dropdown` populated by `fetchProjects` [apps/raycast-extension/src/add-memory.tsx:97-111]().
*   **Implementation:** Calls `addMemory` which hits the `POST /v3/documents` endpoint [apps/raycast-extension/src/api.ts:169-192]().

### 2. Search Memories (`search-memories.tsx`)
A real-time search interface for retrieving saved information.

*   **Context Awareness:** Similar to Add Memory, it can automatically fill the search field with currently selected text [apps/raycast-extension/src/search-memories.tsx:59-72]().
*   **Search Logic:** Uses `usePromise` with the `searchText` state to trigger `searchMemories` [apps/raycast-extension/src/search-memories.tsx:74-93]().
*   **Result Processing:** 
    *   `extractContent`: Flattens complex chunk objects (supporting `string`, `content`, or `text` fields) into a single string for display [apps/raycast-extension/src/search-memories.tsx:16-41]().
    *   `extractUrl`: Retrieves source URLs from metadata [apps/raycast-extension/src/search-memories.tsx:43-48]().
*   **Detail View:** Selecting a memory opens a `MemoryDetail` component [apps/raycast-extension/src/search-memories.tsx:180-217](). This provides a full Markdown preview of the content, creation date, and relevance score [apps/raycast-extension/src/search-memories.tsx:184-194]().

### 3. Search Projects (`search-projects.tsx`)
Manages organizational units (projects/container tags).

*   **Listing:** Displays all projects with their `containerTag` as an accessory [apps/raycast-extension/src/search-projects.tsx:41-60]().
*   **Creation:** Includes a `CreateProject` sub-view that uses the `useForm` hook from `@raycast/utils` to validate and submit new project names via `addProject` [apps/raycast-extension/src/search-projects.tsx:65-106]().

## API Integration Details

The extension uses a centralized API utility to handle communication with `https://api.supermemory.ai` [apps/raycast-extension/src/api.ts:54]().

### Code Entity Mapping

| Raycast Component | Code Entity | API Endpoint |
| :--- | :--- | :--- |
| **Add Memory** | `addMemory` [apps/raycast-extension/src/api.ts:169]() | `POST /v3/documents` |
| **Search Memories** | `searchMemories` [apps/raycast-extension/src/api.ts:194]() | `POST /v3/search` |
| **List Projects** | `fetchProjects` [apps/raycast-extension/src/api.ts:137]() | `GET /v3/projects` |
| **Add Project** | `addProject` [apps/raycast-extension/src/api.ts:154]() | `POST /v3/projects` |
| **Settings Check** | `fetchSettings` [apps/raycast-extension/src/api.ts:219]() | `GET /v3/settings` |

Sources: [apps/raycast-extension/src/api.ts:137-222]()

### Request Handling
All requests pass through `makeAuthenticatedRequest`, which injects the `Authorization: Bearer <apiKey>` header retrieved from Raycast preferences using `getPreferenceValues<Preferences>()` [apps/raycast-extension/src/api.ts:73-135]().

```mermaid
sequenceDiagram
    participant U as User
    participant C as Raycast Command (search-memories.tsx)
    participant A as api.ts (makeAuthenticatedRequest)
    participant S as Supermemory API

    U->>C: Enter Search Query
    C->>A: searchMemories({q: query})
    A->>A: getApiKey() via getPreferenceValues()
    A->>S: POST /v3/search (Auth Header)
    S-->>A: JSON SearchResponse
    A-->>C: SearchResult[]
    C->>U: Display List.Item results
```

Sources: [apps/raycast-extension/src/api.ts:73-135](), [apps/raycast-extension/src/search-memories.tsx:79-82]()

## Installation & Configuration

### From Raycast Store
1. Search for "Supermemory" in the Raycast Store.
2. Click **Install Extension**.

### Configuration
The extension requires an API key to function. 
1. Obtain an API key from [supermemory.link/raycast](https://supermemory.link/raycast) [apps/raycast-extension/package.json:50]().
2. Open Raycast Preferences (`Cmd + ,`).
3. Navigate to the **Extensions** tab and select **Supermemory**.
4. Paste the key into the **API Key** field [apps/raycast-extension/package.json:44-53]().

### Development Setup
To run the extension locally for development:
1. Clone the repository.
2. Navigate to `apps/raycast-extension`.
3. Install dependencies: `npm install`.
4. Run development mode: `npm run dev` (executes `ray develop`) [apps/raycast-extension/package.json:68]().
5. Build for production: `npm run build` (executes `ray build`) [apps/raycast-extension/package.json:67]().

Sources: [apps/raycast-extension/package.json:66-73](), [apps/raycast-extension/README.md]()

---

# Page: Coding Assistant Plugins

# Coding Assistant Plugins

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [apps/docs/docs.json](apps/docs/docs.json)
- [apps/docs/images/hermes.svg](apps/docs/images/hermes.svg)
- [apps/docs/integrations/claude-code.mdx](apps/docs/integrations/claude-code.mdx)
- [apps/docs/integrations/codex.mdx](apps/docs/integrations/codex.mdx)
- [apps/docs/integrations/hermes.mdx](apps/docs/integrations/hermes.mdx)
- [apps/docs/integrations/openclaw.mdx](apps/docs/integrations/openclaw.mdx)
- [apps/docs/integrations/opencode.mdx](apps/docs/integrations/opencode.mdx)
- [apps/docs/integrations/supermemory-sdk.mdx](apps/docs/integrations/supermemory-sdk.mdx)
- [apps/docs/intro.mdx](apps/docs/intro.mdx)
- [apps/docs/quickstart.mdx](apps/docs/quickstart.mdx)
- [apps/docs/self-hosting/configuration.mdx](apps/docs/self-hosting/configuration.mdx)
- [apps/docs/self-hosting/local-vs-enterprise.mdx](apps/docs/self-hosting/local-vs-enterprise.mdx)
- [apps/web/app/auth/agent-connect/page.tsx](apps/web/app/auth/agent-connect/page.tsx)
- [apps/web/components/document-cards/mcp-preview.tsx](apps/web/components/document-cards/mcp-preview.tsx)
- [apps/web/components/document-cards/note-preview.tsx](apps/web/components/document-cards/note-preview.tsx)
- [apps/web/components/document-cards/plugin-preview.tsx](apps/web/components/document-cards/plugin-preview.tsx)
- [apps/web/components/document-modal/content/plugin-content.tsx](apps/web/components/document-modal/content/plugin-content.tsx)
- [apps/web/components/document-modal/title.tsx](apps/web/components/document-modal/title.tsx)
- [apps/web/lib/plugin-catalog.ts](apps/web/lib/plugin-catalog.ts)
- [apps/web/lib/plugin-document.ts](apps/web/lib/plugin-document.ts)
- [apps/web/lib/plugin-space.ts](apps/web/lib/plugin-space.ts)

</details>



Supermemory extends its persistent memory and context capabilities into the developer workflow through a suite of plugins for coding assistants, CLIs, and messaging gateways. These integrations allow AI agents to maintain state across different coding sessions, projects, and communication platforms by bridging the gap between ephemeral sessions and long-term knowledge.

## Claude Code (claude-supermemory)

The `claude-supermemory` plugin integrates Supermemory directly into the Claude Code CLI, providing persistent memory that spans multiple terminal sessions and distinct projects.

### Installation and Setup
To install the plugin within the Claude Code environment:
1.  **API Key:** Set the `SUPERMEMORY_CC_API_KEY` environment variable in your shell profile (`.zshrc` or `.bashrc`) [apps/docs/integrations/claude-code.mdx:33-41]().
2.  **Marketplace:** Add the plugin source: `/plugin marketplace add supermemoryai/claude-supermemory` [apps/docs/integrations/claude-code.mdx:55-55]().
3.  **Install:** Run `/plugin install supermemory` [apps/docs/integrations/claude-code.mdx:58-58]().

### Data Flow and Behavior
The plugin operates through two primary mechanisms:
*   **Context Injection:** Upon starting a session, relevant memories are fetched and injected into Claude's context, including user preferences and project knowledge [apps/docs/integrations/claude-code.mdx:65-65]().
*   **Auto-Capture:** The plugin monitors tool execution and automatically stores the results. It captures `Edit`, `Write`, `Bash` command outputs, and `Task` (agent spawning) actions [apps/docs/integrations/claude-code.mdx:70-76]().

### Configuration
Users can tune the plugin behavior via `~/.supermemory-claude/settings.json`:
| Option | Description |
| :--- | :--- |
| `skipTools` | List of tools to ignore during capture (e.g., `Read`, `Glob`, `Grep`) [apps/docs/integrations/claude-code.mdx:103-103]() |
| `maxContextMemories` | Number of general memories to inject [apps/docs/integrations/claude-code.mdx:105-105]() |
| `maxProjectMemories` | Number of project-specific memories to inject [apps/docs/integrations/claude-code.mdx:106-106]() |

**Sources:** [apps/docs/integrations/claude-code.mdx:20-109](), [apps/web/lib/plugin-catalog.ts:32-53]()

---

## OpenCode Plugin (opencode-supermemory)

The `opencode-supermemory` plugin provides long-term memory for OpenCode sessions, focusing on codebase structure and architectural patterns.

### Core Features
*   **Context Injection:** Automatically fetches relevant memories on session start [apps/docs/integrations/opencode.mdx:67-67]().
*   **Keyword Detection:** Phrases like "remember" or "save this" trigger automatic storage [apps/docs/integrations/opencode.mdx:68-68]().
*   **Smart Compaction:** When the context window reaches 80% capacity (defined by `compactionThreshold`), the session is summarized and saved [apps/docs/integrations/opencode.mdx:69-69](), [apps/docs/integrations/opencode.mdx:125-125]().
*   **Memory Types:** Categorizes data into `project-config`, `architecture`, `error-solution`, and `preference` [apps/docs/integrations/opencode.mdx:83-87]().

### Installation
```bash
bunx opencode-supermemory@latest install
bunx opencode-supermemory@latest login
```
[apps/docs/integrations/opencode.mdx:46-53]()

**Sources:** [apps/docs/integrations/opencode.mdx:12-127](), [apps/web/lib/plugin-catalog.ts:113-141]()

---

## OpenAI Codex (codex-supermemory)

The `codex-supermemory` plugin wires Supermemory into the OpenAI Codex CLI via hooks and skills.

### Implementation Logic
*   **Implicit Memory:** Uses `UserPromptSubmit` hooks for recall and `Stop` hooks for capture [apps/docs/integrations/codex.mdx:51-51]().
*   **Explicit Skills:** Installs `supermemory-search`, `supermemory-save`, and `supermemory-forget` as native Codex skills [apps/docs/integrations/codex.mdx:52-52]().
*   **Memory Scopes:** Automatically derives User tags from `git config` and Project tags from the current directory [apps/docs/integrations/codex.mdx:70-71]().

**Sources:** [apps/docs/integrations/codex.mdx:8-152](), [apps/web/lib/plugin-catalog.ts:54-76]()

---

## OpenClaw Gateway Plugin

OpenClaw is a multi-platform AI messaging gateway. The `@supermemory/openclaw-supermemory` plugin provides a unified memory layer across Telegram, WhatsApp, Discord, Slack, and iMessage.

### Implementation Logic
The plugin implements a middleware-style pattern for OpenClaw:
1.  **Auto-Recall:** Before an AI turn, the plugin calls the Supermemory `profile()` endpoint to fetch context [apps/docs/integrations/openclaw.mdx:56-56]().
2.  **Auto-Capture:** After the AI responds, the exchange is sent to the `add()` endpoint [apps/docs/integrations/openclaw.mdx:57-57]().
3.  **Custom Containers:** Supports routing memories to specific containers like `work` or `personal` via AI instructions [apps/docs/integrations/openclaw.mdx:58-58]().

### System-to-Code Mapping
Title: OpenClaw Plugin Integration Architecture
```mermaid
graph TD
    subgraph "Messaging Interface"
        U["User Message"] --> G["OpenClaw Gateway"]
        G --> R["AI Response"]
    end

    subgraph "Plugin Logic (@supermemory/openclaw-supermemory)"
        G -- "pre-turn" --> AR["autoRecall"]
        R -- "post-turn" --> AC["autoCapture"]
    end

    subgraph "Supermemory API Space"
        AR -- "POST /v4/profile" --> P["profile()"]
        AC -- "POST /v3/add" --> A["add()"]
        P --> CF["containerTag: openclaw_{hostname}"]
        A --> CF
    end
```
**Sources:** [apps/docs/integrations/openclaw.mdx:12-111](), [apps/web/lib/plugin-catalog.ts:142-161]()

---

## Hermes Agent Memory Provider

Hermes is a persistent memory provider for the Hermes agent, optimized for fact extraction and profile building.

### Configuration and Setup
On the machine where Hermes is deployed, the setup wizard is triggered via:
```bash
hermes memory setup
```
[apps/web/lib/plugin-catalog.ts:173-173]()

The provider focuses on building a "Living Knowledge Graph" by mapping conversation turns to static facts (e.g., user name, age) and dynamic context [apps/docs/quickstart.mdx:124-127]().

**Sources:** [apps/web/lib/plugin-catalog.ts:162-176](), [apps/docs/quickstart.mdx:124-127]()

---

## Plugin Document Processing

Supermemory handles data from these plugins using specialized parsing logic to render structured views in the web application.

### Entity Relationship Diagram
Title: Plugin Data Transformation Flow
```mermaid
graph LR
    subgraph "Input Source"
        S1["Claude Code Tool Logs"]
        S2["OpenCode Transcript"]
        S3["Codex Session"]
    end

    subgraph "Parsing Logic (plugin-document.ts)"
        P1["parseTranscriptMessages"]
        P2["parseRoleBlockMessages"]
        P3["extractArtifacts"]
    end

    subgraph "UI Component Space"
        C1["PluginContent"]
        C2["ConversationView"]
        C3["SectionsView"]
    end

    S1 --> P2
    S2 --> P1
    S3 --> P1
    P1 --> P3
    P2 --> P3
    P3 --> C1
    C1 --> C2
    C1 --> C3
```

### Document Kinds
The system categorizes plugin data into specific `PluginDocumentKind` types for rendering:
*   `claude-code-doc`: Specialized view for Claude Code tool usage [apps/web/lib/plugin-document.ts:20-20]().
*   `opencode-session`: Structured session transcripts [apps/web/lib/plugin-document.ts:91-91]().
*   `openclaw-session`: Multi-platform chat logs [apps/web/lib/plugin-document.ts:19-19]().
*   `codex-session`: Implicit memory logs from Codex CLI [apps/web/lib/plugin-document.ts:14-14]().

**Sources:** [apps/web/lib/plugin-document.ts:13-62](), [apps/web/lib/plugin-space.ts:17-54](), [apps/web/components/document-cards/plugin-preview.tsx:8-48]()

---

# Page: Self-Hosting

# Self-Hosting

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [apps/docs/self-hosting/overview.mdx](apps/docs/self-hosting/overview.mdx)
- [apps/docs/self-hosting/quickstart.mdx](apps/docs/self-hosting/quickstart.mdx)

</details>



Supermemory offers a self-hosted deployment option that packages the entire memory engine into a single, portable binary. This local server provides the same core API capabilities as the Cloud platform—including graph-based memory extraction, hybrid semantic search, and user profiling—while keeping data entirely on your own infrastructure.

### System Overview

The self-hosted version is designed for "zero-config" operation. It embeds the graph engine and local embedding models directly into the binary, eliminating the need for external databases like Postgres or vector stores.

#### Local Server Architecture
The following diagram illustrates how the `supermemory-server` binary interacts with your local environment and external LLM providers.

**Self-Hosted Component Map**
```mermaid
graph TD
    subgraph "LocalMachine"
        ["supermemory-server"]
        ["EmbeddedGraphEngine"]
        ["LocalEmbeddings_WASM"]
        ["SUPERMEMORY_DATA_DIR"]
        
        ["supermemory-server"] --> ["EmbeddedGraphEngine"]
        ["supermemory-server"] --> ["LocalEmbeddings_WASM"]
        ["EmbeddedGraphEngine"] --> ["SUPERMEMORY_DATA_DIR"]
        ["supermemory-server"] -.-> ["~/.supermemory/env"]
    end

    subgraph "ExternalProviders_BYOK"
        ["OpenAI_Anthropic_Gemini"]
        ["LocalLLM_Ollama_vLLM"]
    end

    subgraph "Clients"
        ["SupermemorySDK"]
        ["CodingPlugins_ClaudeCode"]
    end

    ["SupermemorySDK"] -- "baseURL:localhost:6767" --> ["supermemory-server"]
    ["CodingPlugins_ClaudeCode"] -- "SUPERMEMORY_API_URL" --> ["supermemory-server"]
    ["supermemory-server"] -- "Extraction&Summarization" --> ["OpenAI_Anthropic_Gemini"]
    ["supermemory-server"] -- "FullyOfflineMode" --> ["LocalLLM_Ollama_vLLM"]
```
Sources: [apps/docs/self-hosting/overview.mdx:8-31](), [apps/docs/self-hosting/quickstart.mdx:32-45]()

### Core Capabilities

The self-hosted binary enables several high-privacy and low-latency workflows:

*   **Local Embeddings**: Vectors are computed on-device using WASM-based models, ensuring that raw text is not sent to third-party embedding providers [apps/docs/self-hosting/overview.mdx:27-27]().
*   **Bring Your Own Key (BYOK)**: Use your existing API keys for OpenAI, Anthropic, Gemini, or Groq to power the "intelligent" steps of the pipeline, such as memory extraction and summarization [apps/docs/self-hosting/overview.mdx:31-31]().
*   **Fully Offline Operation**: By pointing the server to a local OpenAI-compatible endpoint (like Ollama or vLLM), you can run the entire memory stack without an internet connection [apps/docs/self-hosting/overview.mdx:33-44]().
*   **API Parity**: The local server implements the standard Memory API, including `/v3/documents`, `/v3/search`, and `/v4/profile` [apps/docs/self-hosting/overview.mdx:29-29]().

### Deployment Options

| Feature | Supermemory Local | Supermemory Enterprise |
| :--- | :--- | :--- |
| **Hosting** | Self-run binary | Fully managed cloud |
| **Multi-tenancy** | Single-tenant (one API key) | Multi-member orgs & roles |
| **Connectors** | Not supported | Google Drive, Notion, Gmail, etc. |
| **Models** | BYOK (User provided) | Proprietary tuned models |
| **Scalability** | Single machine | Globally distributed |

Sources: [apps/docs/self-hosting/overview.mdx:63-74]()

### Related Pages

- **[Local Server Setup](#14.1)**: Detailed instructions for installing via `curl` or `npx`, managing the data directory via `SUPERMEMORY_DATA_DIR`, and running the first-boot wizard. For details, see [Local Server Setup](#14.1).
- **[Configuration & Enterprise vs Local](#14.2)**: Deep dive into environment variables like `OPENAI_BASE_URL`, performance tuning, and a detailed comparison of features. For details, see [Configuration & Enterprise vs Local](#14.2).

**Code Entity to System Mapping**
```mermaid
graph LR
    subgraph "CodeEntities"
        ["Supermemory_TS_Client"]
        ["Supermemory_Python_Client"]
        ["withSupermemory_Middleware"]
    end

    subgraph "DeploymentTargets"
        ["supermemory-server_Local"]
        ["api.supermemory.ai_Cloud"]
    end

    ["Supermemory_TS_Client"] -- "baseURL:localhost:6767" --> ["supermemory-server_Local"]
    ["Supermemory_Python_Client"] -- "base_url:api.supermemory.ai" --> ["api.supermemory.ai_Cloud"]
    ["withSupermemory_Middleware"] -- "options.baseUrl" --> ["supermemory-server_Local"]
```
Sources: [apps/docs/self-hosting/overview.mdx:50-58](), [apps/docs/self-hosting/quickstart.mdx:57-85]()

Sources:
- [apps/docs/self-hosting/overview.mdx:1-86]()
- [apps/docs/self-hosting/quickstart.mdx:1-152]()

---

# Page: Local Server Setup

# Local Server Setup

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [apps/docs/docs.json](apps/docs/docs.json)
- [apps/docs/integrations/claude-code.mdx](apps/docs/integrations/claude-code.mdx)
- [apps/docs/integrations/codex.mdx](apps/docs/integrations/codex.mdx)
- [apps/docs/integrations/openclaw.mdx](apps/docs/integrations/openclaw.mdx)
- [apps/docs/integrations/opencode.mdx](apps/docs/integrations/opencode.mdx)
- [apps/docs/integrations/supermemory-sdk.mdx](apps/docs/integrations/supermemory-sdk.mdx)
- [apps/docs/intro.mdx](apps/docs/intro.mdx)
- [apps/docs/quickstart.mdx](apps/docs/quickstart.mdx)
- [apps/docs/self-hosting/configuration.mdx](apps/docs/self-hosting/configuration.mdx)
- [apps/docs/self-hosting/local-vs-enterprise.mdx](apps/docs/self-hosting/local-vs-enterprise.mdx)
- [apps/docs/self-hosting/quickstart.mdx](apps/docs/self-hosting/quickstart.mdx)

</details>



The Supermemory local server is a single-binary distribution of the Supermemory engine, designed for private, high-performance, and air-gapped memory workloads. It provides the same ingestion, memory extraction, and hybrid semantic search capabilities as the hosted platform but runs entirely on local hardware [apps/docs/self-hosting/overview.mdx:8-8]().

## Installation and Execution

The local server can be installed via a shell script or executed directly using `npx` or `bunx`. The installer automatically detects the host operating system (macOS Intel/Silicon, Linux x64/arm64) and architecture [apps/docs/self-hosting/quickstart.mdx:28-28]().

### Installation Methods

| Method | Command |
| :--- | :--- |
| **curl** | `curl -fsSL https://supermemory.ai/install \| bash` |
| **npx** | `npx supermemory local` |
| **bunx** | `bunx supermemory local` |

Sources: [apps/docs/quickstart.mdx:12-12](), [apps/docs/self-hosting/quickstart.mdx:10-26]()

### Execution
Once installed, the server is started using the `supermemory-server` command [apps/docs/self-hosting/quickstart.mdx:32-34](). On the first boot, the server:
1.  Initializes the embedded **Supermemory graph engine** [apps/docs/self-hosting/quickstart.mdx:36-36]().
2.  Generates a unique **API Key** (printed to the console in a terminal box) [apps/docs/self-hosting/quickstart.mdx:39-45]().
3.  Caches local embedding models in the data directory [apps/docs/self-hosting/quickstart.mdx:139-139]().
4.  Launches an interactive setup wizard if no LLM provider keys are detected to collect `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, etc [apps/docs/self-hosting/configuration.mdx:32-34]().

## System Configuration

The server defaults to **port 6767** and stores all state in a local directory [apps/docs/self-hosting/configuration.mdx:16-17]().

### Data Persistence
The environment variable `SUPERMEMORY_DATA_DIR` controls where the server stores its database and configuration [apps/docs/self-hosting/configuration.mdx:17-17]().

| Variable | Default Path | Purpose |
| :--- | :--- | :--- |
| `SUPERMEMORY_DATA_DIR` | `./.supermemory` | Stores the graph engine data, auth secrets, and embedding cache [apps/docs/self-hosting/configuration.mdx:17-17](). |
| `PORT` | `6767` | HTTP listen port for the API [apps/docs/self-hosting/configuration.mdx:16-16](). |
| N/A | `~/.supermemory/env` | Stores API keys and environment variables loaded on launch [apps/docs/self-hosting/configuration.mdx:10-10](). |

Sources: [apps/docs/self-hosting/configuration.mdx:12-18](), [apps/docs/self-hosting/quickstart.mdx:133-141]()

### LLM Providers and Offline Mode
While the hosted platform uses proprietary models, the local server allows users to bring their own models. It is compatible with any OpenAI-compliant endpoint, enabling fully offline operation via tools like Ollama or LM Studio [apps/docs/self-hosting/configuration.mdx:42-51]().

```bash
# Example: Running with local Ollama
OPENAI_BASE_URL=http://localhost:11434/v1 \
OPENAI_API_KEY=ollama \
OPENAI_MODEL=gpt-oss:20b \
supermemory-server
```
Sources: [apps/docs/self-hosting/configuration.mdx:46-51]()

## Data Flow and Architecture

The local server manages ingestion through a queue to control memory usage, specifically via `SUPERMEMORY_EMBEDDING_RAM_LIMIT` [apps/docs/self-hosting/configuration.mdx:83-84]().

### Local Server Entity Mapping
This diagram bridges the conceptual setup to the internal server entities and configuration.

```mermaid
graph TD
    subgraph "Host Environment"
        CLI["supermemory-server"]
        ENV_FILE["~/.supermemory/env"]
        DATA_DIR["SUPERMEMORY_DATA_DIR (./.supermemory)"]
    end

    subgraph "Server Process (Port 6767)"
        API_DOCS["POST /v3/documents"]
        API_SEARCH["POST /v3/search"]
        API_PROFILE["POST /v4/profile"]
        
        subgraph "Engine Core"
            QUEUE["Ingestion Queue (SUPERMEMORY_INGEST_CONCURRENCY)"]
            GRAPH["Embedded Graph Engine"]
            EMBED["Local Embedding Workers (SUPERMEMORY_LOCAL_EMBEDDING_POOL_SIZE)"]
            RAM_LIMIT["RAM Guard (SUPERMEMORY_EMBEDDING_RAM_LIMIT)"]
        end
    end

    CLI --> API_DOCS
    ENV_FILE --> CLI
    API_DOCS --> QUEUE
    QUEUE --> RAM_LIMIT
    RAM_LIMIT --> EMBED
    EMBED --> GRAPH
    GRAPH --> DATA_DIR
    API_SEARCH --> EMBED
    API_PROFILE --> GRAPH
```
Sources: [apps/docs/self-hosting/configuration.mdx:12-18](), [apps/docs/self-hosting/configuration.mdx:64-74](), [apps/docs/self-hosting/configuration.mdx:78-98]()

## SDK Integration

To point official SDKs or third-party tools (like Claude Code, OpenCode, or Codex) at the local server, the `baseURL` or `SUPERMEMORY_API_URL` must be updated to `http://localhost:6767` [apps/docs/integrations/supermemory-sdk.mdx:17-19]().

### TypeScript SDK Example
```typescript
import Supermemory from "supermemory"

const client = new Supermemory({
  apiKey: "sm_xxxxxxxx", // Printed on first boot
  baseURL: "http://localhost:6767",
})

// Adding a memory to a specific container
await client.memories.add({
  content: "User prefers dark mode and is allergic to peanuts.",
  containerTag: "user_123",
})
```
Sources: [apps/docs/self-hosting/quickstart.mdx:57-69]()

### Request Flow: SDK to Local Server
This diagram illustrates how an SDK call is processed by the local binary using local embeddings and remote LLM extraction.

```mermaid
sequenceDiagram
    participant SDK as "Supermemory SDK"
    participant LServer as "Local Server (6767)"
    participant LLM as "LLM Provider (OpenAI/Anthropic/Ollama)"
    participant Disk as "SUPERMEMORY_DATA_DIR"

    SDK->>LServer: POST /v3/documents
    LServer-->>SDK: 202 Accepted (Status: queued)
    Note over LServer: Ingestion Queue Logic
    LServer->>LServer: Compute Local Embeddings (WASM)
    LServer->>LLM: Extraction Prompt (BYOK)
    LLM-->>LServer: Extracted Facts/Entities
    LServer->>Disk: Commit to SQLite/Vector Index
```
Sources: [apps/docs/self-hosting/configuration.mdx:21-30](), [apps/docs/self-hosting/configuration.mdx:78-84](), [apps/docs/self-hosting/quickstart.mdx:86-96]()

## Comparison: Local vs. Enterprise

| Feature | Supermemory Local | Supermemory Enterprise |
| :--- | :--- | :--- |
| **Memory Engine** | Full graph engine (Embedded) | Full graph engine (Managed) |
| **Models** | Bring Your Own Key (BYOK) | Proprietary tuned models |
| **Connectors** | Not Supported | Supported (Gmail, Drive, Notion, etc.) |
| **Auth** | Single auto-generated API key | Org-wide RBAC & Scoped Keys |
| **Observability** | Terminal Logs | Console Dashboard & Analytics |
| **Scale** | Single Machine | Globally Distributed |

Sources: [apps/docs/self-hosting/local-vs-enterprise.mdx:14-25](), [apps/docs/self-hosting/configuration.mdx:114-123]()

---

# Page: Configuration & Enterprise vs Local

# Configuration & Enterprise vs Local

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [apps/docs/docs.json](apps/docs/docs.json)
- [apps/docs/integrations/claude-code.mdx](apps/docs/integrations/claude-code.mdx)
- [apps/docs/integrations/codex.mdx](apps/docs/integrations/codex.mdx)
- [apps/docs/integrations/openclaw.mdx](apps/docs/integrations/openclaw.mdx)
- [apps/docs/integrations/opencode.mdx](apps/docs/integrations/opencode.mdx)
- [apps/docs/integrations/supermemory-sdk.mdx](apps/docs/integrations/supermemory-sdk.mdx)
- [apps/docs/intro.mdx](apps/docs/intro.mdx)
- [apps/docs/quickstart.mdx](apps/docs/quickstart.mdx)
- [apps/docs/self-hosting/configuration.mdx](apps/docs/self-hosting/configuration.mdx)
- [apps/docs/self-hosting/local-vs-enterprise.mdx](apps/docs/self-hosting/local-vs-enterprise.mdx)
- [apps/docs/self-hosting/overview.mdx](apps/docs/self-hosting/overview.mdx)

</details>



This page documents the configuration parameters for Supermemory, the architectural and feature differences between the self-hosted **Local** version and the managed **Enterprise/Platform** version, and guidance on selecting the appropriate deployment model.

## Configuration Environment Variables

Supermemory is designed for zero-configuration by default, using an interactive wizard on first boot to collect necessary keys. However, for production or non-interactive deployments, the following environment variables are supported.

### Core Configuration
| Variable | Purpose | Default |
|:---|:---|:---|
| `PORT` or `SUPERMEMORY_PORT` | The HTTP port the server listens on. | `6767` |
| `SUPERMEMORY_DATA_DIR` | Directory for the graph engine data, auth secrets, and model cache. | `./.supermemory` |
| `SUPERMEMORY_DISABLE_TELEMETRY` | Set to `1` to disable internal AI SDK telemetry instrumentation. | `unset` |

Sources: [apps/docs/self-hosting/configuration.mdx:12-18](), [apps/docs/self-hosting/configuration.mdx:106-113]()

### LLM Provider Configuration
Self-hosted Supermemory requires at least one LLM provider for memory extraction, summarization, and contextual chunking. If multiple are provided, they are prioritized in the order listed below.

| Variable | Provider | Notes |
|:---|:---|:---|
| `OPENAI_API_KEY` | OpenAI | Supports compatible endpoints (Ollama, vLLM). |
| `ANTHROPIC_API_KEY` | Anthropic | Used for high-quality extraction. |
| `GEMINI_API_KEY` | Google AI Studio | Required for Image/Video/High-fidelity PDF. |
| `GROQ_API_KEY` | Groq | Used for fast text processing. |
| `WORKERS_AI_API_KEY` | Cloudflare | Requires `CLOUDFLARE_ACCOUNT_ID`. |

Sources: [apps/docs/self-hosting/configuration.mdx:19-40]()

### Local & Offline Model Support
To run fully offline, you can point Supermemory to a local endpoint like Ollama.

| Variable | Purpose | Default |
|:---|:---|:---|
| `OPENAI_BASE_URL` | The endpoint for the local model runner. | OpenAI Official |
| `OPENAI_MODEL` | The specific model ID to use (e.g., `gpt-oss:20b`). | `gpt-5.1` |
| `OPENAI_FAST_MODEL` | Model for light tasks (summarization). | `OPENAI_MODEL` |
| `OPENAI_TEXT_MODEL` | Model for heavier text processing tasks. | `OPENAI_MODEL` |

Sources: [apps/docs/self-hosting/configuration.mdx:42-59]()

### Embedding Engine Tuning
Supermemory uses built-in local embeddings computed on the host machine via Wasm workers.

| Variable | Purpose | Default |
|:---|:---|:---|
| `SUPERMEMORY_LOCAL_EMBEDDING_POOL_SIZE` | Number of concurrent embedding workers. | `1` |
| `SUPERMEMORY_LOCAL_EMBEDDING_WASM_THREADS`| Compute threads per worker. | `1` |
| `SUPERMEMORY_LOCAL_EMBEDDING_BATCH_SIZE` | Texts processed per worker dispatch. | `8` |
| `SUPERMEMORY_SKIP_EMBEDDING_PREWARM` | Skip loading models into RAM at startup. | `unset` |

Sources: [apps/docs/self-hosting/configuration.mdx:64-75]()

### Ingestion Queue Management
The server manages memory by separating immediate searches from backgrounded ingestion tasks.

| Variable | Purpose | Default |
|:---|:---|:---|
| `SUPERMEMORY_EMBEDDING_RAM_LIMIT` | RAM headroom for ingestion above baseline. | `1gb` |
| `SUPERMEMORY_INGEST_CONCURRENCY` | Concurrent documents processed by the queue. | `2` |

Sources: [apps/docs/self-hosting/configuration.mdx:76-98]()

---

## Enterprise vs. Local Comparison

Supermemory exists in two primary forms: the **Local** self-hosted binary (single-tenant) and the **Enterprise/Platform** managed service (multi-tenant).

### Feature Matrix

| Feature | Supermemory Local | Supermemory Enterprise |
|:---|:---|:---|
| **Tenancy** | Single-tenant (one API key) | Multi-tenant (Org/Team/User) |
| **LLM Strategy** | BYOK (Bring Your Own Key) | Managed Proprietary Models |
| **Connectors** | None (Manual ingestion only) | Google Drive, Notion, Gmail, etc. |
| **Managed Sync** | Manual | Continuous background sync |
| **Infrastructure** | Local machine / One process | Globally distributed / Elastic |
| **Observability** | Standard server logs | Dashboard with usage analytics |
| **Deployment** | Single Binary | Cloudflare Workers / Managed |

Sources: [apps/docs/self-hosting/local-vs-enterprise.mdx:12-25](), [apps/docs/self-hosting/overview.mdx:59-74]()

### Architecture and Data Flow

The following diagram illustrates how the `Supermemory` client interacts with both deployment types and how the data flow differs regarding model processing.

**Deployment Architecture and Data Flow**
```mermaid
graph TD
    subgraph "Client_Space"
        [SDK_Client] -->|"/v4/profile"| [API_Gateway]
        [SDK_Client] -->|"/v3/add"| [API_Gateway]
    end

    subgraph "Supermemory_Local"
        [Local_Server] --> [Embedded_Graph_Engine]
        [Local_Server] -->|Local_Vectors| [Wasm_Embedding_Worker]
        [Local_Server] -->|BYOK_Request| [External_LLM_Provider]
        [Local_Storage] --- [Local_Server]
    end

    subgraph "Supermemory_Enterprise"
        [Managed_API] --> [Distributed_Vector_DB]
        [Managed_API] --> [Proprietary_Extraction_Models]
        [Managed_API] --> [Connector_Sync_Service]
        [Connector_Sync_Service] -->|OAuth| [External_SaaS_Notion_Gmail]
    end

    [API_Gateway] -.->|baseURL_localhost| [Local_Server]
    [API_Gateway] -.->|baseURL_api_supermemory_ai| [Managed_API]
```
Sources: [apps/docs/self-hosting/overview.mdx:46-57](), [apps/docs/self-hosting/local-vs-enterprise.mdx:45-48]()

---

## Implementation Details

### Configuration Resolution
The self-hosted binary resolves configuration through a tiered approach:
1. **Interactive Wizard**: On first boot, the server prompts for keys if missing.
2. **Environment File**: Keys are written to `~/.supermemory/env`.
3. **Runtime Environment**: Standard environment variables override file-based settings.

Sources: [apps/docs/self-hosting/configuration.mdx:8-10]()

### Scoping and Container Tags
In both Local and Enterprise versions, the `containerTag` is the primary unit of isolation. 
- In **Local**, all data is accessible via a single administrative API key, but `containerTag` still partitions the semantic graph.
- In **Enterprise**, `containerTag` is used to scope memories to specific users or projects, and API keys can be restricted to specific tags.

**Logic Mapping: Code Entities to System Concepts**
```mermaid
graph LR
    subgraph "Code_Entity_Space"
        [Supermemory_Class] -- "uses" --> [baseURL]
        [Supermemory_Class] -- "sends" --> [containerTag]
        [config_json] -- "defines" --> [OPENAI_MODEL]
        [env_file] -- "stores" --> [SUPERMEMORY_DATA_DIR]
    end

    subgraph "Natural_Language_Space"
        [baseURL] --- "Determines_Local_vs_Cloud"
        [containerTag] --- "Logical_Memory_Isolation"
        [OPENAI_MODEL] --- "Brain_for_Memory_Extraction"
        [SUPERMEMORY_DATA_DIR] --- "Physical_Persistence_Layer"
    end
```
Sources: [apps/docs/integrations/supermemory-sdk.mdx:31-52](), [apps/docs/self-hosting/configuration.mdx:12-18]()

## When to Choose Which

### Choose Supermemory Local if:
*   **Privacy/Security**: You require an air-gapped environment or want to ensure data never leaves your infrastructure (using local models like Ollama).
*   **Prototyping**: You are an individual developer building a side project.
*   **Cost**: You want to utilize existing LLM credits or run free local models.
*   **Offline Access**: You need memory functionality without an active internet connection.

### Choose Supermemory Enterprise if:
*   **Team Collaboration**: You need multi-user support, RBAC (Role-Based Access Control), and scoped API keys.
*   **External Data**: You require automatic synchronization with Google Drive, Notion, Gmail, or GitHub.
*   **Quality**: You need the highest accuracy for memory extraction (Enterprise uses proprietary models tuned specifically for this task).
*   **Scale**: You are building a production application that needs to scale globally without managing server infrastructure.

Sources: [apps/docs/self-hosting/local-vs-enterprise.mdx:8-10](), [apps/docs/self-hosting/local-vs-enterprise.mdx:27-44]()

---

# Page: Glossary

# Glossary

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CONTRIBUTING.md](CONTRIBUTING.md)
- [README.md](README.md)
- [README.zh-CN.md](README.zh-CN.md)
- [apps/docs/changelog/developer-platform.mdx](apps/docs/changelog/developer-platform.mdx)
- [apps/docs/changelog/overview.mdx](apps/docs/changelog/overview.mdx)
- [apps/docs/concepts/container-tags.mdx](apps/docs/concepts/container-tags.mdx)
- [apps/docs/connectors/google-drive.mdx](apps/docs/connectors/google-drive.mdx)
- [apps/docs/cookbook/overview.mdx](apps/docs/cookbook/overview.mdx)
- [apps/docs/docs.json](apps/docs/docs.json)
- [apps/docs/integrations/claude-code.mdx](apps/docs/integrations/claude-code.mdx)
- [apps/docs/integrations/codex.mdx](apps/docs/integrations/codex.mdx)
- [apps/docs/integrations/openclaw.mdx](apps/docs/integrations/openclaw.mdx)
- [apps/docs/integrations/opencode.mdx](apps/docs/integrations/opencode.mdx)
- [apps/docs/integrations/supermemory-sdk.mdx](apps/docs/integrations/supermemory-sdk.mdx)
- [apps/docs/intro.mdx](apps/docs/intro.mdx)
- [apps/docs/introduction.mdx](apps/docs/introduction.mdx)
- [apps/docs/memory-api/sdks/overview.mdx](apps/docs/memory-api/sdks/overview.mdx)
- [apps/docs/migration/from-mem0.mdx](apps/docs/migration/from-mem0.mdx)
- [apps/docs/migration/mem0-migration-script.py](apps/docs/migration/mem0-migration-script.py)
- [apps/docs/quickstart.mdx](apps/docs/quickstart.mdx)
- [apps/docs/self-hosting/configuration.mdx](apps/docs/self-hosting/configuration.mdx)
- [apps/docs/self-hosting/local-vs-enterprise.mdx](apps/docs/self-hosting/local-vs-enterprise.mdx)
- [apps/web/components/dashboard-view.tsx](apps/web/components/dashboard-view.tsx)
- [apps/web/components/highlights-card.tsx](apps/web/components/highlights-card.tsx)
- [apps/web/components/select-spaces-modal.tsx](apps/web/components/select-spaces-modal.tsx)
- [apps/web/components/space-selector.tsx](apps/web/components/space-selector.tsx)
- [apps/web/globals.css](apps/web/globals.css)
- [apps/web/hooks/use-personalization.ts](apps/web/hooks/use-personalization.ts)
- [apps/web/lib/chat-space-label.ts](apps/web/lib/chat-space-label.ts)
- [apps/web/lib/ingest-auto-space.ts](apps/web/lib/ingest-auto-space.ts)
- [apps/web/public/images/plugins/openclaw.svg](apps/web/public/images/plugins/openclaw.svg)
- [packages/tools/README.md](packages/tools/README.md)
- [packages/tools/package.json](packages/tools/package.json)
- [packages/tools/src/vercel/index.ts](packages/tools/src/vercel/index.ts)
- [packages/tools/src/vercel/memory-prompt.ts](packages/tools/src/vercel/memory-prompt.ts)
- [packages/tools/src/vercel/middleware.ts](packages/tools/src/vercel/middleware.ts)
- [packages/tools/src/vercel/util.ts](packages/tools/src/vercel/util.ts)
- [turbo.json](turbo.json)

</details>



This glossary defines the technical terms, architectural concepts, and domain-specific jargon used within the Supermemory codebase. It is intended to help onboarding engineers navigate the multi-surface ecosystem (Web, MCP, Extension, SDKs, and Filesystem).

## Core Concepts

### Container Tag
The primary scoping mechanism for memories. A `containerTag` acts as a unique identifier (e.g., a user ID, a project ID, or a specific workspace) that partitions data. All search and retrieval operations are scoped to one or more tags to ensure data isolation.
*   **Implementation:** Used as a required field in the `createSupermemoryContext` function to isolate context [packages/tools/src/vercel/middleware.ts:119-120]().
*   **Context:** Memory is scoped with projects (container tags) to separate work and personal context [README.md:157-158]().
*   **Multi-tag Keys:** Scoped API keys can now be assigned to multiple container tags simultaneously [apps/docs/changelog/overview.mdx:36-38]().

### Brain / Space
In the consumer-facing Web UI, "Spaces" (often referred to as a personal "Brain") are the user-friendly representation of `containerTags`.
*   **Space Selector:** The `SpaceSelector` component manages the selection of these partitions [apps/web/components/space-selector.tsx:109-120]().
*   **Default Space:** Every user has a default project identified by `DEFAULT_PROJECT_ID` [apps/web/components/select-spaces-modal.tsx:135-144]().

### Nova
The name of the internal AI agent embedded within the Supermemory application. It handles chat, memory retrieval, and auto-capture within the UI.
*   **Reference:** Mentioned as the agent embedded inside the app [README.md:114-114]().
*   **Visuals:** Represented in code by the `NovaOrb` and `AutoSpaceIcon` components [apps/web/components/space-selector.tsx:45-46]().

### Memory vs. Document
The codebase distinguishes between atomic extracted "memories" and source "documents."
*   **Memory:** Extracts facts from conversations. Handles temporal changes, contradictions, and automatic forgetting [README.md:43-43]().
*   **Document:** A larger source of information (PDFs, images, videos, code) processed via multi-modal extractors [README.md:47-48]().
*   **Smart Compaction:** The process of grouping related documents into coherent units, controlled by the `dreaming` parameter [apps/docs/changelog/overview.mdx:8-10]().

Sources: [packages/tools/src/vercel/middleware.ts:119-120](), [README.md:43-158](), [apps/web/components/space-selector.tsx:109-144](), [apps/docs/changelog/overview.mdx:8-38]()

---

## Architectural Terms

### MCP (Model Context Protocol)
An open standard that enables AI models (like Claude or Cursor) to connect to external data sources. Supermemory implements an MCP server to provide AI assistants with direct access to a user's memory.
*   **Tools:** Registered tools include `memory` (save/forget), `recall` (search), and `context` (profile injection) [README.md:143-148]().
*   **Visuals:** The MCP server includes an interactive graph visualization app for exploring memory connections [apps/docs/changelog/overview.mdx:56-59]().

### SMFS (Supermemory Filesystem)
A virtual filesystem that mounts Supermemory containers as local directories. This allows agents to use standard shell commands (`ls`, `cat`, `grep`) to interact with memory.
*   **Mounting:** Can be mounted via NFSv3 on macOS or FUSE on Linux [apps/docs/docs.json:160-165]().
*   **Bash Tool:** A package (`@supermemory/bash`) that allows LLMs to execute shell commands against this virtual drive [apps/docs/docs.json:166-167]().

### Memory Mode
A configuration for the AI middleware that determines what context is fetched for the LLM.
*   `profile`: Retrieves user profile memories (static + dynamic) without query filtering [packages/tools/src/vercel/middleware.ts:129-129]().
*   `query`: Searches memories based on semantic similarity to the user's message [packages/tools/src/vercel/middleware.ts:130-130]().
*   `full`: Combines both profile and query-based results [packages/tools/src/vercel/middleware.ts:131-131]().

### Per-Turn Caching
A performance optimization in the `@supermemory/tools` package. It prevents redundant API calls during multi-step AI interactions by caching the injected memories string.
*   **Implementation:** Managed via `MemoryCache` and the `makeTurnKey` function [packages/tools/src/vercel/middleware.ts:209-222]().

Sources: [README.md:134-148](), [packages/tools/src/vercel/middleware.ts:128-222](), [apps/docs/docs.json:160-167](), [apps/docs/changelog/overview.mdx:56-59]()

---

## Technical Entities Map

### Natural Language to Code Entity Space

The following diagrams bridge conceptual terms to their implementation sites in the codebase.

**Retrieval Flow: Concept to Function**
```mermaid
graph TD
    subgraph "Natural Language Space"
        UserQuery["'What do I like?'"]
        ProfileReq["'Who am I?'"]
    end

    subgraph "Code Entity Space"
        UserQuery --> Transform["transformParamsWithMemory<br/>(packages/tools/src/vercel/middleware.ts:232)"]
        ProfileReq --> ProfileCall["client.profile()<br/>(apps/docs/quickstart.mdx:96)"]
        
        Transform --> KeyGen["makeTurnKey<br/>(packages/tools/src/vercel/middleware.ts:212)"]
        KeyGen --> Cache["MemoryCache<br/>(packages/tools/src/vercel/middleware.ts:204)"]
        
        Transform --> Prompt["injectMemoriesIntoParams<br/>(packages/tools/src/vercel/memory-prompt.ts:16)"]
    end
```
Sources: [packages/tools/src/vercel/middleware.ts:204-232](), [apps/docs/quickstart.mdx:96-100]()

**Persistence Flow: Concept to API**
```mermaid
graph LR
    subgraph "Natural Language Space"
        AutoCapture["'Auto-Capture'"]
        AutoRecall["'Auto-Recall'"]
    end

    subgraph "Code Entity Space"
        AutoCapture --> SaveMem["saveMemoryAfterResponse<br/>(packages/tools/src/vercel/middleware.ts:78)"]
        SaveMem --> AddConv["addConversation<br/>(packages/tools/src/vercel/middleware.ts:94)"]
        AddConv --> API_V4["POST /v4/conversations"]
        
        AutoRecall --> HybridSearch["Hybrid Search Mode<br/>(README.md:45)"]
    end
```
Sources: [packages/tools/src/vercel/middleware.ts:78-94](), [README.md:45-45]()

---

## Glossary Table

| Term | Definition | Code Pointer |
| :--- | :--- | :--- |
| **withSupermemory** | Higher-order function for Vercel AI SDK/OpenAI to inject memory context. | [packages/tools/src/vercel/index.ts:111-111]() |
| **MemScore** | The primary metric used by MemoryBench to evaluate memory accuracy. | [apps/docs/docs.json:270-270]() |
| **Autumn** | The entitlement/billing management system used in the web app. | [apps/web/components/header.tsx:70-71]() |
| **Better-Auth** | The authentication framework handling sessions and user identity. | [apps/web/lib/auth.ts:28-28]() |
| **Drizzle ORM** | The TypeScript ORM used for database interactions (SQLite/Postgres). | [README.md:200-205]() |
| **Dreaming** | Parameter (`dynamic` or `instant`) for document grouping and memory formation. | [apps/docs/changelog/overview.mdx:8-10]() |
| **Daily Brief** | Feature that resurfaces relevant memories to the user periodically. | [apps/web/components/dashboard-view.tsx:158-158]() |
| **Plugin Auth Key** | Specialized keys for connecting tools like Claude Code or Raycast. | [apps/docs/changelog/overview.mdx:166-168]() |
| **Rail Entry** | Internal terminology for items appearing in the sidebar/navigation rail. | [apps/web/components/header.tsx:1-20]() |
| **Graph Memory** | Visualization of knowledge entities and their relationships. | [apps/docs/docs.json:87-87]() |

Sources: [packages/tools/src/vercel/index.ts:111-111](), [apps/docs/docs.json:270-270](), [apps/docs/changelog/overview.mdx:8-168](), [apps/web/components/dashboard-view.tsx:158-158](), [apps/web/lib/auth.ts:28-28]()