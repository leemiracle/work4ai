# Page: Overview

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.prettierignore](.prettierignore)
- [.prettierrc.json](.prettierrc.json)
- [CLAUDE.md](CLAUDE.md)
- [README.md](README.md)
- [services/action-builder/scripts/login.ts](services/action-builder/scripts/login.ts)
- [services/action-builder/src/optimizer/SelectorOptimizer.ts](services/action-builder/src/optimizer/SelectorOptimizer.ts)
- [services/common/browser-profile/package.json](services/common/browser-profile/package.json)
- [services/common/browser-profile/src/BrowserProfileManager.ts](services/common/browser-profile/src/BrowserProfileManager.ts)

</details>



## Purpose and Scope

This document provides a high-level introduction to Actionbook, explaining what it is, its core value proposition, and the major architectural components that comprise the system. This overview is intended to orient new developers and users to the codebase structure before diving into specific subsystems.

For specific user-facing integration methods, see [User Interfaces](#2). For detailed service implementation, see [Core Services](#3). For browser automation specifics, see [Browser Automation Layer](#4).

**Sources:** [README.md:1-745](), [CLAUDE.md:1-209]()

## What is Actionbook

Actionbook is a platform that provides AI agents with verified, up-to-date action manuals for website interaction. Instead of agents repeatedly parsing full HTML pages to discover interactive elements, Actionbook pre-builds structured "action manuals" containing verified DOM selectors, allowed operations, and page metadata for websites.

The system operates on a simple principle: **crawl once, use many times**. Actionbook's build pipeline discovers and documents website capabilities, storing them in both a PostgreSQL database (for fast search and retrieval) and YAML files (for human-readable output). AI agents and automation scripts can then query this pre-built knowledge base to obtain reliable selectors without the overhead of page analysis.

**Key characteristics:**
- **Query-focused**: Agents query for action manuals; execution happens in agent's own browser
- **Multi-modal search**: Combines full-text and vector similarity for accurate retrieval
- **Versioned**: Supports Blue-Green deployment of action manual versions
- **Framework-agnostic**: Works with any LLM provider (OpenAI, Anthropic, Gemini, Bedrock)

**Sources:** [README.md:9-48](), [CLAUDE.md:8-11]()

## Core Value Proposition

Actionbook addresses four critical problems in browser automation:

| Problem | Without Actionbook | With Actionbook |
|---------|-------------------|-----------------|
| **Execution Speed** | Agents parse full HTML to find elements | 10x faster using pre-computed action manuals |
| **Token Cost** | Entire DOM trees sent to LLM | 100x token savings with concise JSON definitions |
| **Brittleness** | Hardcoded selectors break on UI updates | Resilient: manuals updated independently of agent code |
| **Hallucinations** | LLMs guess at complex, unstructured DOMs | Reduced: agents receive verified selectors |

The fundamental efficiency gain comes from separating **discovery** (expensive, done once) from **execution** (cheap, done many times). The build pipeline invests time using AI-powered browser automation to discover and validate selectors, then all subsequent agent runs can leverage this work instantly.

**Sources:** [README.md:29-48]()

## System Architecture

The following diagram shows the major architectural layers and how they interact:

### High-Level Component Architecture

```mermaid
graph TB
    subgraph "Layer 1: User Interfaces"
        CLI["CLI<br/>@actionbookdev/cli<br/>packages/cli"]
        MCP["MCP Server<br/>@actionbookdev/mcp<br/>packages/mcp"]
        SDK["JavaScript SDK<br/>@actionbookdev/sdk<br/>packages/js-sdk"]
    end
    
    subgraph "Layer 2: API Layer"
        APIService["API Service<br/>apps/api-service<br/>Express REST endpoints"]
    end
    
    subgraph "Layer 3: Core Services"
        ActionBuilder["Action Builder<br/>services/action-builder<br/>ActionRecorder, SelectorOptimizer"]
        PlaybookBuilder["Playbook Builder<br/>services/playbook-builder<br/>PlaybookTaskController"]
        KnowledgeBuilder["Knowledge Builder<br/>services/knowledge-builder<br/>Content extraction"]
    end
    
    subgraph "Layer 4: Task Orchestration"
        Coordinator["Coordinator<br/>services/action-builder/Coordinator"]
        BuildTaskRunner["BuildTaskRunner<br/>services/action-builder"]
        QueueWorker["QueueWorker<br/>services/action-builder"]
    end
    
    subgraph "Layer 5: Browser Automation"
        BrowserAdapter["BrowserAdapter<br/>interface<br/>packages/browser"]
        StagehandBrowser["StagehandBrowser<br/>Local Playwright<br/>packages/browser"]
        AgentCoreBrowser["AgentCoreBrowser<br/>AWS cloud<br/>packages/browser"]
        BrowserProfile["BrowserProfileManager<br/>services/common/browser-profile"]
    end
    
    subgraph "Layer 6: Data Layer"
        DB[("PostgreSQL<br/>sources, pages, elements<br/>chunks, build_tasks<br/>recording_tasks<br/>services/db")]
        YAML["YAML Files<br/>output/sites/<br/>Action manuals"]
    end
    
    CLI --> APIService
    MCP --> APIService
    SDK --> APIService
    
    APIService --> DB
    
    ActionBuilder --> BuildTaskRunner
    ActionBuilder --> QueueWorker
    PlaybookBuilder --> DB
    KnowledgeBuilder --> DB
    
    Coordinator --> BuildTaskRunner
    BuildTaskRunner --> QueueWorker
    
    QueueWorker --> BrowserAdapter
    ActionBuilder --> BrowserAdapter
    PlaybookBuilder --> BrowserAdapter
    
    BrowserAdapter --> StagehandBrowser
    BrowserAdapter --> AgentCoreBrowser
    StagehandBrowser --> BrowserProfile
    
    BrowserAdapter --> DB
    BrowserAdapter --> YAML
```

**Layer responsibilities:**
1. **User Interfaces**: Entry points for developers and AI agents
2. **API Layer**: REST endpoints for search and retrieval operations
3. **Core Services**: Build pipeline services for discovering and documenting websites
4. **Task Orchestration**: Concurrent build task management and execution
5. **Browser Automation**: Unified browser interface with local and cloud implementations
6. **Data Layer**: Persistent storage with hybrid search capabilities

**Sources:** [README.md:1-745](), [CLAUDE.md:29-56](), Diagram 1 from system architecture overview

## Domain Model Hierarchy

Actionbook organizes website information in a hierarchical structure:

```mermaid
graph LR
    Source["Source<br/>(sources table)<br/>Website domain<br/>e.g., airbnb.com"] --> SourceVersion["SourceVersion<br/>(source_versions table)<br/>Blue-Green versioning"]
    
    Source --> Document["Document<br/>(documents table)<br/>Crawled page HTML"]
    
    Document --> Chunk["Chunk<br/>(chunks table)<br/>Content segment<br/>+ embedding"]
    
    Source --> Page["Page<br/>(pages table)<br/>Page type<br/>e.g., home, search"]
    
    Page --> Element["Element<br/>(elements table)<br/>UI component<br/>Semantic ID"]
    
    Element --> Selectors["Selectors<br/>(SelectorItem[])<br/>css, xpath, dataTestId<br/>ariaLabel, id"]
    
    Source --> BuildTask["BuildTask<br/>(build_tasks table)<br/>Pipeline tracking"]
    
    BuildTask --> RecordingTask["RecordingTask<br/>(recording_tasks table)<br/>Task execution"]
```

**Key entities:**
- **Source**: Website domain with metadata, health score, tags [services/db]()
- **SourceVersion**: Version management for Blue-Green deployments [services/db]()
- **Page**: Functional page type (home, search, login) with URL patterns [services/db]()
- **Element**: Interactive UI component with semantic identifier [services/db]()
- **Selectors**: Multiple selector types with priority and confidence scores [services/db]()
- **Chunk**: Embedded content segments for vector search [services/db]()

**ActionId format**: `site/{domain}/page/{pageType}/element/{semanticId}`

Example: `site/airbnb.com/page/home/element/search-button`

**Sources:** [CLAUDE.md:14-26](), [CLAUDE.md:44-49](), Diagram 5 from system architecture overview

## Integration Methods

Actionbook provides three integration methods, each optimized for different use cases:

### Integration Method Comparison

| Method | Best For | Package | Entry Point |
|--------|----------|---------|-------------|
| **CLI** | AI agents, command-line automation, quick testing | `@actionbookdev/cli` | `actionbook` command |
| **MCP Server** | AI IDEs (Cursor, Claude Code, VS Code, etc.) | `@actionbookdev/mcp` | MCP protocol integration |
| **JavaScript SDK** | Custom agents, programmatic integration, LLM frameworks | `@actionbookdev/sdk` | `Actionbook` class |

### User Interaction Flow

```mermaid
graph LR
    subgraph "Entry Points"
        Dev["Developer"]
        Agent["AI Agent"]
        IDE["AI IDE"]
    end
    
    subgraph "Integration Layer"
        CLICmd["CLI Commands<br/>packages/cli/src/index.ts<br/>search, get, sources"]
        MCPTools["MCP Tools<br/>packages/mcp/src/index.ts<br/>search_actions<br/>get_action_by_id"]
        SDKMethods["SDK Methods<br/>packages/js-sdk/src/index.ts<br/>searchActions()<br/>getActionById()"]
    end
    
    subgraph "API Endpoints"
        SearchAPI["/actions/search<br/>apps/api-service<br/>GET endpoint"]
        GetAPI["/actions/:id<br/>apps/api-service<br/>GET endpoint"]
    end
    
    subgraph "Data Sources"
        ChunksTable["chunks table<br/>Full-text + vector search"]
        ElementsTable["elements table<br/>Verified selectors"]
    end
    
    Dev --> CLICmd
    Dev --> SDKMethods
    Agent --> MCPTools
    Agent --> SDKMethods
    IDE --> MCPTools
    
    CLICmd --> SearchAPI
    CLICmd --> GetAPI
    MCPTools --> SearchAPI
    MCPTools --> GetAPI
    SDKMethods --> SearchAPI
    SDKMethods --> GetAPI
    
    SearchAPI --> ChunksTable
    GetAPI --> ElementsTable
```

**Common workflow:**
1. Query for actions: `search_actions("airbnb search")`
2. Review results with descriptions and IDs
3. Get detailed action: `get_action_by_id("site/airbnb.com/page/home/element/search-button")`
4. Extract selectors: Use `css`, `dataTestId`, `ariaLabel`, or `xpath` from response
5. Execute in browser: Use selectors in Playwright, Puppeteer, Selenium, etc.

**Sources:** [README.md:84-661](), [CLAUDE.md:43-56](), Diagram 2 from system architecture overview

## Key Components Overview

### User-Facing Packages

**CLI (`@actionbookdev/cli`)**: Command-line interface providing search, retrieval, and browser automation commands. Wraps the API Service and includes an integrated browser automation tool. [packages/cli]()

**MCP Server (`@actionbookdev/mcp`)**: Model Context Protocol server enabling AI IDEs to access Actionbook via standardized tools. Exposes `search_actions` and `get_action_by_id` tools. [packages/mcp]()

**JavaScript SDK (`@actionbookdev/sdk`)**: Core TypeScript library with type definitions and API client. Provides methods with attached tool definitions for easy LLM framework integration. [packages/js-sdk]()

For detailed usage, see [User Interfaces](#2).

### Core Services

**API Service (`apps/api-service`)**: Express-based REST API providing search and retrieval endpoints. Implements hybrid search (full-text + vector similarity) using PostgreSQL indexes. [apps/api-service]()

**Action Builder (`services/action-builder`)**: Main recording service that discovers UI elements and generates action manuals. Uses AI-powered browser automation with multi-turn LLM loops. Includes `ActionRecorder`, `SelectorOptimizer`, `Coordinator`, `BuildTaskRunner`, and `QueueWorker`. [services/action-builder]()

**Playbook Builder (`services/playbook-builder`)**: Generates human-readable documentation for websites by discovering page types and capabilities. Operates alongside Action Builder. [services/playbook-builder]()

**Knowledge Builder (`services/knowledge-builder`)**: Crawls websites to extract and embed content for search. Generates the `chunks` table with embeddings for vector similarity search. [services/knowledge-builder]()

For detailed service architecture, see [Core Services](#3).

### Browser Automation

**BrowserAdapter Interface (`packages/browser`)**: Abstract interface defining unified browser operations. Implementations can be local (Playwright) or cloud-based (AWS). [packages/browser]()

**StagehandBrowser**: Local implementation using Playwright and Stagehand SDK. Supports multiple LLM providers (OpenRouter, OpenAI, Anthropic, Bedrock). [packages/browser]()

**AgentCoreBrowser**: Cloud implementation using AWS AgentCore and Bedrock Claude. [packages/browser]()

**BrowserProfileManager (`services/common/browser-profile`)**: Manages persistent browser profiles for login state. Enables "login once, reuse many times" workflow. [services/common/browser-profile/src/BrowserProfileManager.ts:1-239]()

For browser automation details, see [Browser Automation Layer](#4).

### Data Layer

**Database (`services/db`)**: PostgreSQL schema with Drizzle ORM. Includes specialized indexes:
- **GIN index** on `chunks.content` for full-text search
- **HNSW index** on `chunks.embedding` for vector similarity
- **Composite indexes** on foreign keys for efficient joins

**YAML Output (`output/sites/`)**: Human-readable action manuals in YAML format, organized by site and version. Provides offline access and version control.

For database details, see [Data Layer](#5).

**Sources:** [CLAUDE.md:29-40](), [README.md:702-729](), Diagram 6 from system architecture overview

## Build Pipeline Overview

The build pipeline operates in three stages to transform a website URL into searchable action manuals:

```mermaid
graph TB
    Input["Input<br/>Website URL + config"] --> Init["Stage: init<br/>Create build_task record"]
    
    Init --> KnowledgeStage["Stage: knowledge_build<br/>KnowledgeBuilder<br/>- Crawl pages<br/>- Extract content<br/>- Generate embeddings"]
    
    KnowledgeStage --> ActionStage["Stage: action_build<br/>Action Builder services"]
    
    subgraph "Action Building (Parallel)"
        ActionStage --> Coord["Coordinator<br/>Claims completed knowledge builds"]
        Coord --> BTR["BuildTaskRunner<br/>Per-build orchestration<br/>Generates 50-100+ recording_tasks"]
        BTR --> RT1["RecordingTask 1<br/>explore login page"]
        BTR --> RT2["RecordingTask 2<br/>explore search page"]
        BTR --> RTN["RecordingTask N<br/>explore checkout page"]
        
        RT1 --> QW["QueueWorker<br/>Global task consumer<br/>Claims and executes tasks"]
        RT2 --> QW
        RTN --> QW
        
        QW --> AR["ActionRecorder<br/>- Multi-turn LLM loop<br/>- observe_page<br/>- register_element"]
        
        AR --> SO["SelectorOptimizer<br/>LLM-based stability analysis"]
        
        SO --> Save["Save Results<br/>- elements table<br/>- YAML files"]
    end
    
    Save --> Complete["Stage: completed<br/>Publish version"]
```

**Stage progression:**
1. **init**: Create `build_task` record with pending status
2. **knowledge_build**: Crawl and document pages, generate embeddings
3. **action_build**: Discover and record UI elements with verified selectors
4. **completed**: Publish version, make available for queries

**Concurrency model:**
- **One Coordinator**: Polls database for completed knowledge builds, spawns BuildTaskRunners
- **Multiple BuildTaskRunners**: One per build, generates recording tasks
- **Global QueueWorker Pool**: Claims and executes recording tasks across all builds
- **Heartbeat monitoring**: 5-second intervals with 15-minute stale detection
- **Retry logic**: Max 3 attempts per recording task

For detailed pipeline mechanics, see [Task Execution Pipeline](#3.2.1).

**Sources:** [services/action-builder](), Diagram 3 from system architecture overview

## Technology Stack

### Core Technologies

| Category | Technology | Usage |
|----------|-----------|-------|
| **Language** | TypeScript 5.x | Entire codebase |
| **Runtime** | Node.js 18+ (20+ recommended) | All services |
| **Package Manager** | pnpm | Monorepo management |
| **Build System** | Turborepo | Parallel builds, caching |
| **Database** | PostgreSQL | Primary data store |
| **ORM** | Drizzle ORM | Type-safe database access |

### Browser Automation

| Technology | Usage |
|-----------|-------|
| **Playwright** | Local browser automation via StagehandBrowser |
| **Stagehand SDK** | AI-powered browser operations (`@browserbasehq/stagehand`) |
| **AWS AgentCore** | Cloud-based browser service |

### AI/LLM Integration

| Technology | Usage |
|-----------|-------|
| **Vercel AI SDK** | LLM framework abstraction (`ai`, `@ai-sdk/*`) |
| **OpenRouter** | Multi-model LLM gateway |
| **OpenAI** | GPT models (gpt-4o, gpt-4o-mini) |
| **Anthropic** | Claude models (claude-3-5-haiku, claude-sonnet) |
| **AWS Bedrock** | Claude models in AWS |

### API and Protocols

| Technology | Usage |
|-----------|-------|
| **Express** | REST API server (apps/api-service) |
| **MCP Protocol** | Model Context Protocol for AI IDE integration (`@modelcontextprotocol/sdk`) |
| **Zod** | Schema validation and type inference |

### Database Features

- **Full-text search**: PostgreSQL `ts_vector` with GIN indexes
- **Vector search**: pgvector extension with HNSW indexes
- **Hybrid search**: Combines full-text and vector similarity with RRF (Reciprocal Rank Fusion)
- **Serverless support**: Neon serverless PostgreSQL driver (`@neondatabase/serverless`)

**Sources:** [CLAUDE.md:59-65](), [README.md:702-729](), [package.json files in packages/]()

## Monorepo Structure

The codebase is organized as a pnpm workspace with Turborepo orchestration:

```
actionbook/
├── packages/              # Published npm packages
│   ├── js-sdk/           # @actionbookdev/sdk - Core types and API client
│   ├── mcp/              # @actionbookdev/mcp - MCP Server
│   ├── cli/              # @actionbookdev/cli - Command-line interface
│   ├── tools-ai-sdk/     # @actionbookdev/tools-ai-sdk - Vercel AI SDK integration
│   └── browser/          # @actionbookdev/browser - Browser adapter implementations
├── apps/
│   └── api-service/      # REST API server
├── services/
│   ├── action-builder/   # Action recording service
│   ├── playbook-builder/ # Documentation generation service
│   ├── knowledge-builder/# Content crawling and embedding service
│   ├── db/               # @actionbookdev/db - Database schema and migrations
│   └── common/
│       └── browser-profile/ # @actionbookdev/browser-profile - Login state management
├── playground/           # Example projects and demos
└── eval/                 # Evaluation framework
```

**Package dependency principle:** Published packages (`js-sdk`, `mcp`, `cli`) have no dependencies on internal services. Services depend on published packages and common libraries.

For detailed monorepo information, see [Development Guide](#8).

**Sources:** [CLAUDE.md:29-40](), [README.md:702-729]()

---

# Page: Getting Started

# Getting Started

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [LICENSE](LICENSE)
- [README.md](README.md)
- [packages/cli/package.json](packages/cli/package.json)
- [packages/js-sdk/package.json](packages/js-sdk/package.json)
- [packages/mcp/package.json](packages/mcp/package.json)

</details>



This guide covers the installation and initial setup of Actionbook, providing step-by-step instructions for all three integration methods: CLI, MCP Server, and JavaScript SDK. By the end of this guide, you will have Actionbook installed and will have executed your first action manual search.

For detailed information about individual installation methods and their features, see [User Interfaces](#2). For architecture details, see [Architecture Overview](#1.2).

---

## Prerequisites

Before installing Actionbook, ensure your environment meets the following requirements:

| Requirement | Minimum Version | Recommended | Verification Command |
|-------------|----------------|-------------|---------------------|
| Node.js | v18.0.0 | v20+ | `node --version` |
| npm | 9+ (included with Node.js) | 10+ | `npm --version` |
| pnpm | 8+ (optional, for SDK) | 10+ | `pnpm --version` |

**Current Status:** Actionbook is in open beta. No API key is required for any integration method.

**Sources:** [README.md:94-102]()

---

## Installation Method Selection

Actionbook provides three integration methods. Choose based on your use case:

```mermaid
graph TD
    Start["Choose Installation Method"]
    
    UseCase1{"Building an AI agent<br/>or using command line?"}
    UseCase2{"Using an MCP-compatible<br/>IDE (Cursor, Claude, etc.)?"}
    UseCase3{"Building custom<br/>programmatic integration?"}
    
    CLI["CLI Installation<br/>@actionbookdev/cli<br/>Global command-line tool"]
    MCP["MCP Server<br/>@actionbookdev/mcp<br/>IDE integration"]
    SDK["JavaScript SDK<br/>@actionbookdev/sdk<br/>Programmatic API"]
    
    Start --> UseCase1
    UseCase1 -->|Yes| CLI
    UseCase1 -->|No| UseCase2
    UseCase2 -->|Yes| MCP
    UseCase2 -->|No| UseCase3
    UseCase3 -->|Yes| SDK
    UseCase3 -->|No| CLI
    
    CLI --> CLIFeatures["• Browser automation<br/>• Direct CLI commands<br/>• Agent integration"]
    MCP --> MCPFeatures["• IDE tool integration<br/>• AI assistant access<br/>• No manual commands"]
    SDK --> SDKFeatures["• Full programmatic control<br/>• Custom LLM integration<br/>• TypeScript types"]
```

**Sources:** [README.md:86-93](), [README.md:106-661]()

---

## Option 1: CLI Installation

The CLI (`@actionbookdev/cli`) is the recommended method for most users and provides direct access to all Actionbook features.

### Installation Steps

**Step 1: Install the CLI globally**

```bash
npm install -g @actionbookdev/cli
```

**Step 2: Install Chromium for browser automation**

```bash
actionbook browser install
```

This command installs Chromium via the `agent-browser` dependency, enabling browser automation commands.

**Sources:** [README.md:106-115](), [packages/cli/package.json:27-30]()

### Core CLI Commands

The CLI provides the following command structure:

```mermaid
graph LR
    CLI["actionbook"]
    
    Search["search<br/>'query'"]
    Get["get<br/>'action-id'"]
    Sources["sources<br/>[list|get]"]
    Browser["browser<br/>[command]"]
    
    CLI --> Search
    CLI --> Get
    CLI --> Sources
    CLI --> Browser
    
    Search --> SearchResult["Returns: Array of<br/>matching actions"]
    Get --> GetResult["Returns: Detailed<br/>action with selectors"]
    Sources --> SourcesResult["Returns: Available<br/>website sources"]
    Browser --> BrowserResult["Executes: Browser<br/>automation command"]
    
    SearchResult --> API["/actions/search endpoint"]
    GetResult --> API2["/actions/:id endpoint"]
    SourcesResult --> API3["/sources endpoint"]
    BrowserResult --> AgentBrowser["agent-browser CLI"]
```

**Sources:** [README.md:117-130](), [packages/cli/package.json:27-30]()

### First Commands to Try

**1. Search for action manuals**

```bash
actionbook search "airbnb search"
```

Returns a list of action manuals matching the query. Each result includes an `id`, `title`, `description`, and relevance score.

**2. Get detailed action information**

```bash
actionbook get "site/airbnb.com/page/home/element/search-button"
```

Returns complete action details including:
- DOM selectors (`css`, `xpath`, `dataTestId`, `ariaLabel`)
- Element metadata (type, module, page context)
- Step-by-step instructions

**3. List available sources**

```bash
actionbook sources
```

Returns all indexed websites in the Actionbook database.

**Sources:** [README.md:117-130]()

---

## Option 2: MCP Server Installation

The MCP Server (`@actionbookdev/mcp`) integrates Actionbook into Model Context Protocol-compatible IDEs, allowing AI assistants to access action manuals as tools.

### Supported IDEs

| IDE | Configuration Method | Config File Location |
|-----|---------------------|---------------------|
| Cursor | Settings → MCP → Add global server | GUI configuration |
| Claude Desktop | Edit config file | `claude_desktop_config.json` |
| VS Code | Edit settings.json | `.vscode/settings.json` |
| Windsurf | Edit config file | `~/.codeium/windsurf/mcp_config.json` |
| Zed | Edit settings.json | Zed settings |

**Sources:** [README.md:134-424]()

### Standard Configuration Format

All MCP-compatible IDEs use this configuration structure:

```json
{
  "mcpServers": {
    "actionbook": {
      "command": "npx",
      "args": ["-y", "@actionbookdev/mcp@latest"]
    }
  }
}
```

The `-y` flag ensures `npx` automatically installs/updates the package without prompting.

**Alternative: Using Bun**

```json
{
  "mcpServers": {
    "actionbook": {
      "command": "bunx",
      "args": ["@actionbookdev/mcp@latest"]
    }
  }
}
```

**Sources:** [README.md:145-154](), [README.md:391-403]()

### MCP Tool Flow

```mermaid
graph TB
    IDE["AI IDE<br/>(Cursor/Claude/VS Code)"]
    
    Assistant["AI Assistant"]
    MCPServer["@actionbookdev/mcp<br/>MCP Server Process"]
    
    SearchTool["search_actions tool"]
    GetTool["get_action_by_id tool"]
    
    SDK["@actionbookdev/sdk<br/>Actionbook client"]
    
    API["API Service<br/>api.actionbook.dev"]
    
    IDE --> Assistant
    Assistant -->|Tool call request| MCPServer
    
    MCPServer --> SearchTool
    MCPServer --> GetTool
    
    SearchTool --> SDK
    GetTool --> SDK
    
    SDK -->|HTTP GET /actions/search| API
    SDK -->|HTTP GET /actions/:id| API
    
    API -->|Action results| SDK
    SDK -->|Tool response| MCPServer
    MCPServer -->|Structured data| Assistant
```

**Sources:** [packages/mcp/package.json:31-36](), [README.md:674-689]()

---

## Option 3: JavaScript SDK Installation

The JavaScript SDK (`@actionbookdev/sdk`) provides programmatic access to Actionbook for custom agent implementations.

### Installation

```bash
# npm
npm install @actionbookdev/sdk

# pnpm
pnpm add @actionbookdev/sdk

# yarn
yarn add @actionbookdev/sdk

# bun
bun add @actionbookdev/sdk
```

**Sources:** [README.md:433-446]()

### Basic Usage Pattern

```typescript
import { Actionbook } from '@actionbookdev/sdk'

// Initialize client (no API key required in open beta)
const actionbook = new Actionbook()

// Search for actions
const results = await actionbook.searchActions('airbnb search')
console.log(`Found ${results.length} actions`)

// Get specific action
const action = await actionbook.getActionById(results[0].id)

// Access selectors with fallback priority
const selector = action.selectors.css || 
                 action.selectors.dataTestId || 
                 action.selectors.ariaLabel

console.log('Selector:', selector)
```

**Sources:** [README.md:448-470]()

### SDK Method Structure

```mermaid
graph LR
    Actionbook["Actionbook class"]
    
    SearchMethod["searchActions(query)"]
    GetMethod["getActionById(id)"]
    SourcesMethod["listSources()"]
    SearchSourcesMethod["searchSources(query)"]
    
    Actionbook --> SearchMethod
    Actionbook --> GetMethod
    Actionbook --> SourcesMethod
    Actionbook --> SearchSourcesMethod
    
    SearchMethod --> SearchMeta["• description property<br/>• params.json (JSON Schema)<br/>• params.zod (Zod schema)"]
    GetMethod --> GetMeta["• description property<br/>• params.json (JSON Schema)<br/>• params.zod (Zod schema)"]
    
    SearchMeta --> Integration["LLM Framework<br/>Integration"]
    GetMeta --> Integration
    
    Integration --> VercelAI["Vercel AI SDK"]
    Integration --> OpenAISDK["OpenAI SDK"]
    Integration --> AnthropicSDK["Anthropic SDK"]
    Integration --> GeminiSDK["Google Gemini SDK"]
```

Each method exposes metadata for LLM tool integration. See [JavaScript SDK](#2.3) for complete integration examples.

**Sources:** [README.md:472-489](), [README.md:491-629]()

---

## Verification Steps

After installation, verify your setup with these commands:

### CLI Verification

```bash
# Check CLI version
actionbook --version

# Test search functionality
actionbook search "google login"

# Verify browser installation
actionbook browser --help
```

**Expected output for search:** JSON array of action manuals with `id`, `title`, `description`, and `score` fields.

### MCP Verification

1. Restart your IDE after adding the MCP configuration
2. Open a new chat with your AI assistant
3. Ask: "Use Actionbook to search for LinkedIn login actions"
4. The assistant should invoke the `search_actions` tool

**Expected behavior:** The IDE's tool execution panel should show the MCP server responding with action results.

### SDK Verification

Create a test script:

```typescript
import { Actionbook } from '@actionbookdev/sdk'

const actionbook = new Actionbook()
const results = await actionbook.searchActions('github search')
console.log('Connected! Found', results.length, 'actions')
```

Run with:
```bash
node --loader tsx test-actionbook.ts
# or
npx tsx test-actionbook.ts
```

**Expected output:** `Connected! Found [number] actions`

**Sources:** [README.md:117-130](), [README.md:448-470]()

---

## Common First Tasks

### Task 1: Find and Use a Specific Element Selector

**Use Case:** You need to automate clicking the "Sign In" button on GitHub.

**CLI Workflow:**

```bash
# Step 1: Search for the action
actionbook search "github sign in button"

# Step 2: Get the action details (use ID from search results)
actionbook get "site/github.com/page/home/element/signin-button"

# Step 3: Use the selector with browser automation
actionbook browser open github.com
actionbook browser click '[data-test-id="sign-in"]'
```

**SDK Workflow:**

```typescript
const actionbook = new Actionbook()

// Search for the action
const results = await actionbook.searchActions('github sign in button')

// Get detailed action info
const action = await actionbook.getActionById(results[0].id)

// Use with your browser automation library
await page.click(action.selectors.css)
```

**Sources:** [README.md:117-130](), [README.md:448-470]()

### Task 2: Explore Available Websites

```bash
# List all indexed sources
actionbook sources

# Search for a specific source
actionbook sources get airbnb.com
```

This returns metadata about the website including:
- Indexed pages
- Last update timestamp
- Available action count

**Sources:** [README.md:117-130]()

### Task 3: Integrate with AI Agent Frameworks

For Stagehand integration:

```typescript
import { Actionbook } from '@actionbookdev/sdk'
import { tool } from 'ai'

const actionbook = new Actionbook()

const agent = stagehand.agent({
  model: 'openai/gpt-4o',
  tools: {
    searchActions: tool({
      description: actionbook.searchActions.description,
      inputSchema: actionbook.searchActions.params.zod,
      execute: async ({ query }) => actionbook.searchActions(query),
    }),
    getActionById: tool({
      description: actionbook.getActionById.description,
      inputSchema: actionbook.getActionById.params.zod,
      execute: async ({ id }) => actionbook.getActionById(id),
    }),
  },
})
```

For detailed framework integrations, see [JavaScript SDK](#2.3).

**Sources:** [README.md:631-659]()

---

## Browser Automation Commands

The CLI includes `agent-browser` wrapper commands for direct browser automation. These commands operate on the currently open browser instance.

### Available Commands

| Command | Description | Example |
|---------|-------------|---------|
| `install` | Install Chromium browser | `actionbook browser install` |
| `open` | Open URL in browser | `actionbook browser open airbnb.com` |
| `click` | Click element by selector | `actionbook browser click '[data-test="btn"]'` |
| `fill` | Fill input field | `actionbook browser fill 'input[name="q"]' 'search term'` |
| `type` | Type text into element | `actionbook browser type 'textarea' 'message'` |
| `screenshot` | Capture screenshot | `actionbook browser screenshot` |
| `close` | Close browser | `actionbook browser close` |

**Complete Example:**

```bash
# Install browser
actionbook browser install

# Open Airbnb
actionbook browser open airbnb.com

# Search for a location
actionbook browser fill 'input[name="location"]' 'Tokyo'
actionbook browser click '[data-testid="search-button"]'

# Take screenshot
actionbook browser screenshot
```

For detailed browser automation documentation, see [Browser Automation Commands](#2.1.1).

**Sources:** [README.md:113-114](), [README.md:126-130](), [packages/cli/package.json:28]()

---

## Next Steps

After completing this guide, explore these resources:

1. **[CLI Reference](#2.1)** - Complete command documentation and options
2. **[MCP Server](#2.2)** - IDE-specific configuration and troubleshooting
3. **[JavaScript SDK](#2.3)** - Advanced integration patterns and TypeScript types
4. **[Architecture Overview](#1.2)** - Understand how Actionbook components interact
5. **[Available Tools](#2.4)** - Explore tool definitions and parameters

### Community Resources

- **GitHub Repository:** https://github.com/actionbook/actionbook
- **Discord Community:** https://discord.gg/7sKKp7XQ2d
- **X/Twitter:** https://x.com/ActionbookHQ
- **Website:** https://actionbook.dev

**Sources:** [README.md:690-700]()

---

## Troubleshooting Common Issues

### Issue: `actionbook: command not found` after global install

**Solution:** Ensure npm global bin directory is in your PATH:

```bash
# Check npm global bin path
npm config get prefix

# Add to PATH (example for bash/zsh)
export PATH="$(npm config get prefix)/bin:$PATH"
```

### Issue: Browser install fails

**Solution:** The browser installation uses Playwright's Chromium. Ensure you have sufficient disk space (~300MB) and run:

```bash
# Clear cache and reinstall
rm -rf ~/.cache/ms-playwright
actionbook browser install
```

### Issue: MCP server not appearing in IDE

**Solution:**
1. Verify JSON configuration syntax is correct
2. Restart the IDE completely (not just reload window)
3. Check IDE logs for MCP connection errors
4. Ensure Node.js >= 18 is in your system PATH

### Issue: SDK import errors

**Solution:** Ensure you're using ESM imports and have proper TypeScript configuration:

```json
// tsconfig.json
{
  "compilerOptions": {
    "module": "ESNext",
    "moduleResolution": "node"
  }
}
```

**Sources:** [README.md:94-102](), [packages/cli/package.json:38-40](), [packages/mcp/package.json:44-46]()

---

# Page: Architecture Overview

# Architecture Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitignore](.gitignore)
- [.prettierignore](.prettierignore)
- [.prettierrc.json](.prettierrc.json)
- [CLAUDE.md](CLAUDE.md)
- [README.md](README.md)
- [mcp-servers.json](mcp-servers.json)
- [package.json](package.json)
- [pnpm-lock.yaml](pnpm-lock.yaml)
- [pnpm-workspace.yaml](pnpm-workspace.yaml)
- [services/action-builder/.nvmrc](services/action-builder/.nvmrc)
- [services/action-builder/scripts/login.ts](services/action-builder/scripts/login.ts)
- [services/action-builder/src/optimizer/SelectorOptimizer.ts](services/action-builder/src/optimizer/SelectorOptimizer.ts)
- [services/common/browser-profile/package.json](services/common/browser-profile/package.json)
- [services/common/browser-profile/src/BrowserProfileManager.ts](services/common/browser-profile/src/BrowserProfileManager.ts)
- [turbo.json](turbo.json)

</details>



## Purpose and Scope

This document provides a high-level technical overview of the Actionbook system architecture, including its major components, their interactions, and the data flow between them. It explains the monorepo structure, published packages, internal services, and how different layers communicate.

For installation and basic usage, see [Getting Started](#1.1). For detailed information about each user interface (CLI, MCP Server, SDK), see [User Interfaces](#2). For implementation details of individual services, see [Core Services](#3).

## System Overview

Actionbook is a multi-layered system designed to provide AI agents with verified website action manuals. The architecture separates concerns into distinct layers: user-facing interfaces for consumption, core services for data generation, browser automation for discovery, task orchestration for pipeline management, and a hybrid data layer for storage and retrieval.

The system operates in two modes:

1. **Query Mode**: Users (AI agents, developers) query pre-built action manuals via CLI, MCP Server, or SDK
2. **Build Mode**: Background services crawl websites, discover capabilities, and generate action manuals

Sources: [README.md:1-48](), Diagram 1 from provided diagrams

## Monorepo Structure

Actionbook uses a pnpm workspace monorepo organized into four main categories:

| Category | Path | Purpose |
|----------|------|---------|
| Published Packages | `packages/*` | User-facing npm packages (CLI, SDK, MCP) |
| Services | `services/*` | Backend services and shared infrastructure |
| Playground | `playground/*` | Example integrations and demos |
| Evaluation | `eval/` | Testing and evaluation framework |

### Published Packages

```
packages/
├── cli/              # @actionbookdev/cli - Command-line interface
├── js-sdk/           # @actionbookdev/sdk - JavaScript SDK with tool definitions
├── mcp/              # @actionbookdev/mcp - MCP Server implementation
└── tools-ai-sdk/     # @actionbookdev/tools-ai-sdk - Vercel AI SDK integration
```

### Internal Packages

```
services/
├── common/
│   ├── browser/            # @actionbookdev/browser - Browser abstraction layer
│   └── browser-profile/    # @actionbookdev/browser-profile - Profile management
└── db/                     # @actionbookdev/db - Database schema and client
```

### Services

```
services/
├── action-builder/      # Action recording and element discovery
├── playbook-builder/    # Documentation and page discovery
├── knowledge-builder/   # Content extraction and embedding generation
└── api-service/         # REST API for queries (not shown in provided files)
```

Sources: [README.md:701-741](), [pnpm-workspace.yaml:1-7](), [CLAUDE.md:28-42]()

## Component Architecture

The following diagram shows the major components and their actual package/service names as they appear in the codebase:

```mermaid
graph TB
    subgraph "User Interfaces (packages/)"
        CLI["@actionbookdev/cli<br/>packages/cli"]
        MCP["@actionbookdev/mcp<br/>packages/mcp"]
        SDK["@actionbookdev/sdk<br/>packages/js-sdk"]
        ToolsAI["@actionbookdev/tools-ai-sdk<br/>packages/tools-ai-sdk"]
    end
    
    subgraph "Core Services (services/)"
        APIService["api-service<br/>REST endpoints"]
        ActionBuilder["action-builder<br/>ActionRecorder<br/>RecorderToolExecutor"]
        PlaybookBuilder["playbook-builder<br/>PlaybookTaskController"]
        KnowledgeBuilder["knowledge-builder<br/>Crawler & embeddings"]
    end
    
    subgraph "Browser Automation (services/common/browser)"
        BrowserAdapter["BrowserAdapter<br/>(interface)"]
        StagehandBrowser["StagehandBrowser<br/>Playwright + Stagehand"]
        AgentCoreBrowser["AgentCoreBrowser<br/>AWS AgentCore"]
    end
    
    subgraph "Task Orchestration (services/action-builder)"
        Coordinator["Coordinator<br/>Build manager"]
        BuildTaskRunner["BuildTaskRunner<br/>Per-build orchestrator"]
        QueueWorker["RecordingTaskQueueWorker<br/>Global task consumer"]
    end
    
    subgraph "Shared Infrastructure (services/)"
        DB["@actionbookdev/db<br/>Drizzle ORM + PostgreSQL"]
        BrowserProfile["@actionbookdev/browser-profile<br/>BrowserProfileManager"]
        AIClient["AIClient<br/>Multi-provider LLM client"]
        SelectorOptimizer["SelectorOptimizer<br/>LLM-based analysis"]
    end
    
    subgraph "Data Storage"
        PostgreSQL[("PostgreSQL<br/>sources, pages, elements<br/>build_tasks, recording_tasks<br/>chunks with embeddings")]
        YAMLFiles["YAML Files<br/>output/sites/"]
    end
    
    CLI --> SDK
    MCP --> SDK
    ToolsAI --> SDK
    SDK --> APIService
    CLI --> StagehandBrowser
    
    APIService --> DB
    
    ActionBuilder --> BuildTaskRunner
    ActionBuilder --> QueueWorker
    ActionBuilder --> AIClient
    ActionBuilder --> SelectorOptimizer
    
    PlaybookBuilder --> DB
    PlaybookBuilder --> AIClient
    
    KnowledgeBuilder --> DB
    KnowledgeBuilder --> BrowserProfile
    
    Coordinator --> BuildTaskRunner
    BuildTaskRunner --> QueueWorker
    
    QueueWorker --> BrowserAdapter
    BrowserAdapter <|-- StagehandBrowser
    BrowserAdapter <|-- AgentCoreBrowser
    
    StagehandBrowser --> BrowserProfile
    AgentCoreBrowser --> BrowserProfile
    
    DB --> PostgreSQL
    ActionBuilder --> YAMLFiles
    
    BuildTaskRunner --> DB
    QueueWorker --> DB
```

**Key Design Decisions:**

1. **Package Separation**: `@actionbookdev/sdk` is dependency-free and provides core types; other packages depend on it
2. **Browser Abstraction**: `BrowserAdapter` interface enables multiple implementations (local Playwright vs. cloud AWS)
3. **Task Orchestration Split**: `BuildTaskRunner` manages per-build coordination while `RecordingTaskQueueWorker` provides global task execution
4. **Dual Persistence**: Action manuals stored in both PostgreSQL (queryable) and YAML files (human-readable)

Sources: [README.md:87-93](), [CLAUDE.md:28-67](), Diagram 1 and Diagram 6 from provided diagrams

## Data Flow Architecture

### Query Flow (User → API → Database)

```mermaid
sequenceDiagram
    participant User as "AI Agent / Developer"
    participant Interface as "CLI / MCP / SDK"
    participant API as "APIService<br/>/actions/search<br/>/actions/:id"
    participant DB as "PostgreSQL<br/>chunks + elements tables"
    participant Index as "GIN + HNSW Indexes"
    
    User->>Interface: Search for actions
    Interface->>API: GET /actions/search?q=query
    API->>DB: Hybrid search query
    DB->>Index: Full-text + vector search
    Index->>DB: Matching chunk IDs
    DB->>API: Action metadata + selectors
    API->>Interface: JSON response
    Interface->>User: ElementCapability objects
    
    Note over User,Interface: User executes with selectors
```

### Build Flow (Service → Browser → Database)

```mermaid
sequenceDiagram
    participant Coord as "Coordinator"
    participant BTR as "BuildTaskRunner"
    participant QW as "RecordingTaskQueueWorker"
    participant Browser as "BrowserAdapter<br/>(Stagehand/AgentCore)"
    participant Tools as "RecorderToolExecutor<br/>navigate/observe/register"
    participant AI as "AIClient<br/>Multi-provider LLM"
    participant DB as "PostgreSQL<br/>build_tasks/recording_tasks"
    participant Opt as "SelectorOptimizer"
    
    Coord->>DB: Claim build_task
    Coord->>BTR: Spawn runner
    BTR->>DB: Generate recording_tasks
    
    loop For each recording task
        QW->>DB: Claim recording_task
        QW->>Browser: Initialize session
        QW->>Tools: Execute tools
        Tools->>Browser: navigate(), observe()
        Browser->>AI: LLM observation
        AI->>Tools: Discovered elements
        Tools->>DB: Register elements
    end
    
    BTR->>DB: Check task completion
    BTR->>Opt: Optimize selectors
    Opt->>AI: Batch analysis
    AI->>Opt: Stability scores
    BTR->>DB: Update with optimized selectors
    BTR->>DB: Publish version
```

Sources: Diagram 2 and Diagram 3 from provided diagrams

## Browser Automation Layer

The browser automation layer provides a unified interface for two different browser execution environments:

```mermaid
graph TB
    subgraph "Interface"
        BrowserAdapter["«interface» BrowserAdapter<br/>services/common/browser/src/BrowserAdapter.ts"]
    end
    
    subgraph "Local Implementation"
        StagehandBrowser["StagehandBrowser<br/>services/common/browser/src/StagehandBrowser.ts"]
        Playwright["Playwright Browser<br/>Local Chromium"]
        StagehandSDK["@browserbasehq/stagehand<br/>npm package"]
        ProfileMgr["BrowserProfileManager<br/>services/common/browser-profile"]
        
        StagehandBrowser --> Playwright
        StagehandBrowser --> StagehandSDK
        StagehandBrowser --> ProfileMgr
    end
    
    subgraph "Cloud Implementation"
        AgentCoreBrowser["AgentCoreBrowser<br/>services/common/browser/src/AgentCoreBrowser.ts"]
        AWSBrowser["AWS AgentCore<br/>bedrock-agentcore package"]
        BedrockClaude["AWS Bedrock<br/>Claude models"]
        
        AgentCoreBrowser --> AWSBrowser
        AgentCoreBrowser --> BedrockClaude
    end
    
    subgraph "LLM Providers"
        OpenRouter["OpenRouter"]
        OpenAI["OpenAI"]
        Anthropic["Anthropic"]
        Bedrock["AWS Bedrock"]
    end
    
    BrowserAdapter -.->|implements| StagehandBrowser
    BrowserAdapter -.->|implements| AgentCoreBrowser
    
    StagehandBrowser -.->|can use| OpenRouter
    StagehandBrowser -.->|can use| OpenAI
    StagehandBrowser -.->|can use| Anthropic
    StagehandBrowser -.->|can use| Bedrock
    
    AgentCoreBrowser -.->|uses| Bedrock
```

**Key Methods in BrowserAdapter:**

- `initialize()`: Setup browser session
- `navigate(url)`: Navigate to URL with validation
- `observe(instruction)`: AI-powered element discovery
- `act(action)`: Execute interactions (click, type, etc.)
- `getPageInfo()`: Extract page metadata
- `cleanup()`: Cleanup resources

**StagehandBrowser Features:**

- Local Playwright browser execution
- Multi-LLM provider support (OpenRouter, OpenAI, Anthropic, Bedrock)
- Persistent browser profiles via `BrowserProfileManager`
- Anti-detection arguments for stable automation

**AgentCoreBrowser Features:**

- AWS cloud-based browser service
- Bedrock Claude integration for vision
- No local Chromium installation required

Sources: [services/common/browser-profile/src/BrowserProfileManager.ts:1-239](), Diagram 4 from provided diagrams

## Task Orchestration Pipeline

The build pipeline uses a three-tier orchestration model:

```mermaid
graph TB
    subgraph "Tier 1: Build Management"
        Coordinator["Coordinator<br/>services/action-builder/src/coordinator/Coordinator.ts<br/>• Claims build_tasks<br/>• Spawns BuildTaskRunners<br/>• Monitors overall progress"]
    end
    
    subgraph "Tier 2: Per-Build Orchestration"
        BTR["BuildTaskRunner<br/>services/action-builder/src/coordinator/BuildTaskRunner.ts<br/>• Generates 50-100 recording_tasks<br/>• Polls task completion<br/>• Manages retries (max 3)<br/>• Publishes versions"]
    end
    
    subgraph "Tier 3: Global Task Execution"
        QW["RecordingTaskQueueWorker<br/>services/action-builder/src/coordinator/RecordingTaskQueueWorker.ts<br/>• Claims recording_tasks globally<br/>• Executes ActionRecorder<br/>• Updates heartbeat every 5s<br/>• Stale detection: 15 min"]
    end
    
    subgraph "Task Execution"
        ActionRecorder["ActionRecorder<br/>services/action-builder/src/recorder/ActionRecorder.ts<br/>• Multi-turn LLM loop (max 30 turns)<br/>• Tool execution<br/>• Element registration"]
        
        ToolExecutor["RecorderToolExecutor<br/>services/action-builder/src/recorder/RecorderToolExecutor.ts<br/>• navigate<br/>• observe_page<br/>• interact<br/>• register_element<br/>• set_page_context"]
    end
    
    subgraph "Database Tables"
        BuildTasks[("build_tasks<br/>stage: init/knowledge_build/action_build<br/>status: pending/in_progress/completed")]
        RecordingTasks[("recording_tasks<br/>status: pending/claimed/in_progress/completed/failed<br/>last_heartbeat_at")]
    end
    
    Coordinator --> BTR
    BTR --> QW
    QW --> ActionRecorder
    ActionRecorder --> ToolExecutor
    
    Coordinator --> BuildTasks
    BTR --> BuildTasks
    BTR --> RecordingTasks
    QW --> RecordingTasks
    ActionRecorder --> RecordingTasks
```

**Pipeline Stages:**

1. **Init**: Build task created, ready for knowledge building
2. **Knowledge Build**: `knowledge-builder` crawls pages and generates embeddings
3. **Action Build**: `action-builder` discovers elements and records actions

**Failure Handling:**

- **Heartbeat Monitoring**: Tasks update `last_heartbeat_at` every 5 seconds
- **Stale Detection**: Tasks with no heartbeat for 15 minutes are re-queued
- **Retry Logic**: Failed tasks retry up to 3 times before permanent failure
- **Idempotency**: Tasks can be safely retried without duplicating work

Sources: Diagram 3 from provided diagrams

## AI and LLM Integration

The system integrates with multiple LLM providers through a unified client:

```mermaid
graph TB
    subgraph "AI Components"
        AIClient["AIClient<br/>services/action-builder/src/ai/AIClient.ts<br/>• Multi-provider support<br/>• Proxy support<br/>• Metrics collection<br/>• Retry logic"]
        
        SelectorOpt["SelectorOptimizer<br/>services/action-builder/src/optimizer/SelectorOptimizer.ts<br/>• Batch selector analysis<br/>• Stability detection<br/>• Confidence scoring"]
    end
    
    subgraph "Configuration Resolution"
        EnvVars["Environment Variables<br/>OPENROUTER_API_KEY<br/>OPENAI_API_KEY<br/>ANTHROPIC_API_KEY<br/>AWS_ACCESS_KEY_ID"]
    end
    
    subgraph "Provider SDKs"
        OpenRouter["@openrouter/ai-sdk-provider<br/>createOpenRouter()"]
        OpenAI["@ai-sdk/openai<br/>createOpenAI()"]
        Anthropic["@ai-sdk/anthropic<br/>createAnthropic()"]
        Bedrock["@ai-sdk/amazon-bedrock<br/>createAmazonBedrock()"]
    end
    
    subgraph "Vercel AI SDK"
        AI["ai package<br/>generateText()<br/>streamText()<br/>tool definitions"]
    end
    
    EnvVars --> AIClient
    AIClient --> OpenRouter
    AIClient --> OpenAI
    AIClient --> Anthropic
    AIClient --> Bedrock
    
    OpenRouter --> AI
    OpenAI --> AI
    Anthropic --> AI
    Bedrock --> AI
    
    SelectorOpt --> AIClient
```

**AIClient Features:**

- **Multi-Provider Support**: Automatically selects provider based on available API keys
- **Proxy Support**: Uses `HTTPS_PROXY` environment variable for corporate networks
- **Fallback Chain**: OpenRouter → OpenAI → Anthropic → Bedrock
- **Message Conversion**: Converts between different provider message formats

**SelectorOptimizer Use Case:**

The `SelectorOptimizer` uses LLM to analyze CSS selectors and identify unstable patterns:

- **Unstable Patterns**: Dynamic counters, timestamps, hash-based CSS classes, framework-generated IDs
- **Stable Patterns**: `data-testid`, semantic `data-*` attributes, static `aria-label`, BEM classes
- **Output**: Reordered selectors with confidence scores and stability annotations

Sources: [services/action-builder/src/optimizer/SelectorOptimizer.ts:1-372](), Diagram 4 from provided diagrams

## Data Layer

The data layer uses a dual-persistence strategy combining PostgreSQL for queries and YAML files for human readability:

```mermaid
graph TB
    subgraph "Database Package"
        DB["@actionbookdev/db<br/>services/db"]
        Drizzle["Drizzle ORM<br/>Type-safe schema"]
        Schema["Schema Definitions<br/>services/db/src/schema/*"]
    end
    
    subgraph "Connection Management"
        GetDb["getDb() function<br/>services/db/src/index.ts<br/>• Environment detection<br/>• Connection pooling<br/>• Driver selection"]
        
        NodePg["node-postgres<br/>Local development"]
        NeonServerless["@neondatabase/serverless<br/>Serverless environments"]
    end
    
    subgraph "Core Tables"
        Sources[("sources<br/>Website metadata")]
        SourceVersions[("source_versions<br/>Blue-green versioning")]
        Documents[("documents<br/>Crawled pages")]
        Chunks[("chunks<br/>Content + embeddings")]
        Pages[("pages<br/>Page types")]
        Elements[("elements<br/>UI components + selectors")]
        BuildTasks[("build_tasks<br/>Pipeline tracking")]
        RecordingTasks[("recording_tasks<br/>Task execution")]
    end
    
    subgraph "Indexes"
        GIN["GIN Index<br/>Full-text search on chunks.content<br/>PostgreSQL ts_vector"]
        HNSW["HNSW Index<br/>Vector similarity on chunks.embedding<br/>Cosine distance"]
    end
    
    subgraph "YAML Output"
        YAMLFiles["output/sites/<domain>/<domain>.yml<br/>• Human-readable format<br/>• Version-controlled<br/>• Git-friendly"]
    end
    
    DB --> Drizzle
    Drizzle --> Schema
    DB --> GetDb
    
    GetDb --> NodePg
    GetDb --> NeonServerless
    
    Schema --> Sources
    Schema --> SourceVersions
    Schema --> Documents
    Schema --> Chunks
    Schema --> Pages
    Schema --> Elements
    Schema --> BuildTasks
    Schema --> RecordingTasks
    
    Chunks --> GIN
    Chunks --> HNSW
    
    Elements -.->|exported to| YAMLFiles
```

**Schema Relationships:**

- `sources` (1) → (N) `source_versions`: Blue-green deployment strategy
- `sources` (1) → (N) `documents`: Crawled pages per source
- `documents` (1) → (N) `chunks`: Content segments with embeddings
- `sources` (1) → (N) `pages`: Page types (home, search, profile, etc.)
- `pages` (1) → (N) `elements`: UI components with selectors
- `sources` (1) → (N) `build_tasks`: Build pipeline tracking
- `build_tasks` (1) → (N) `recording_tasks`: Task execution tracking

**Search Strategy:**

- **Full-Text Search**: GIN index on `chunks.content` using PostgreSQL `ts_vector`
- **Vector Search**: HNSW index on `chunks.embedding` using cosine distance
- **Hybrid Search**: Combines both strategies with weighted scoring

**Version Management:**

- `source_versions` table enables Blue-Green deployments
- Each version has status: `draft`, `published`, `archived`
- Only one version can be `published` per source at a time
- Failed builds remain in `draft` state without affecting production

Sources: Diagram 5 from provided diagrams

## Browser Profile Management

The `BrowserProfileManager` enables persistent login state across browser sessions:

```mermaid
graph LR
    subgraph "Profile Management"
        Manager["BrowserProfileManager<br/>services/common/browser-profile/src/BrowserProfileManager.ts"]
        
        Methods["Methods:<br/>• getProfilePath()<br/>• exists()<br/>• ensureDir()<br/>• clear()<br/>• cleanupStaleLocks()<br/>• getLaunchOptions()"]
    end
    
    subgraph "File System"
        ProfileDir[".browser-profile/<br/>Chromium user data<br/>• Cookies<br/>• LocalStorage<br/>• Session tokens"]
        
        LockFiles["Lock Files:<br/>• SingletonLock<br/>• SingletonSocket<br/>• SingletonCookie"]
    end
    
    subgraph "Browser Launch"
        LaunchOptions["Launch Options:<br/>userDataDir: .browser-profile<br/>preserveUserDataDir: true<br/>args: ANTI_DETECTION_ARGS<br/>ignoreDefaultArgs: IGNORE_DEFAULT_ARGS"]
        
        AntiDetection["Anti-Detection:<br/>--disable-blink-features=AutomationControlled<br/>--no-first-run"]
    end
    
    subgraph "Login Workflow"
        LoginScript["scripts/login.ts<br/>pnpm login command<br/>• Opens browser<br/>• User logs in manually<br/>• Profile saved on exit"]
    end
    
    Manager --> Methods
    Methods --> ProfileDir
    Methods --> LockFiles
    Manager --> LaunchOptions
    LaunchOptions --> AntiDetection
    LoginScript --> Manager
```

**Usage Pattern:**

1. **First Time**: Run `pnpm login` to open browser and complete login manually
2. **Subsequent Runs**: Browser reuses stored cookies and session tokens
3. **Multi-Site Support**: Can login to multiple websites in one session
4. **Lock File Cleanup**: Automatic cleanup of stale lock files from crashed browsers

**Integration:**

- Used by both `StagehandBrowser` and `AgentCoreBrowser`
- Shared across all recording tasks to maintain login state
- Profile directory excluded from git via `.gitignore`

Sources: [services/common/browser-profile/src/BrowserProfileManager.ts:1-239](), [services/action-builder/scripts/login.ts:1-149](), [.gitignore:73-75]()

## Build System

The monorepo uses Turborepo for task orchestration:

```mermaid
graph TB
    subgraph "Root Tasks"
        Root["package.json<br/>scripts:<br/>build, dev, test, lint, clean"]
    end
    
    subgraph "Turborepo Configuration"
        Turbo["turbo.json<br/>Task definitions<br/>Dependency graphs<br/>Cache configuration"]
    end
    
    subgraph "Workspace Tasks"
        Build["build:<br/>• Dependency-aware (^build)<br/>• Outputs: dist/**, .next/**<br/>• Cached"]
        
        Dev["dev:<br/>• No cache<br/>• Persistent tasks"]
        
        Test["test:<br/>• Depends on ^build<br/>• Cached"]
    end
    
    subgraph "Package Manager"
        PNPM["pnpm@10.24.0<br/>Workspace protocol<br/>Dependency hoisting"]
    end
    
    Root --> Turbo
    Turbo --> Build
    Turbo --> Dev
    Turbo --> Test
    Root --> PNPM
```

**Key Features:**

- **Dependency-Aware Builds**: `^build` means "build dependencies first"
- **Smart Caching**: Turborepo caches task outputs based on inputs
- **Parallel Execution**: Tasks run in parallel when dependencies allow
- **Filtered Builds**: `pnpm build --filter=@actionbookdev/sdk` builds only specified packages

**Build Order Example:**

```
1. @actionbookdev/db (no dependencies)
2. @actionbookdev/browser-profile (no dependencies)
3. @actionbookdev/browser (depends on browser-profile)
4. @actionbookdev/sdk (no internal dependencies)
5. @actionbookdev/mcp (depends on sdk)
6. @actionbookdev/cli (depends on sdk)
7. action-builder (depends on browser, browser-profile, db, mcp)
```

Sources: [turbo.json:1-23](), [package.json:1-25](), [pnpm-workspace.yaml:1-7]()

## Key Design Patterns

### Strategy Pattern: Browser Abstraction

The `BrowserAdapter` interface enables swapping between local (Playwright) and cloud (AWS AgentCore) implementations without changing consumer code.

### Producer-Consumer: Task Queue

`BuildTaskRunner` produces `recording_tasks` which are consumed by `RecordingTaskQueueWorker`. This decouples task generation from execution.

### Singleton: Database Connection

The `getDb()` function returns a singleton database connection per process, preventing connection pool exhaustion.

### Template Method: Recording Pipeline

`ActionRecorder` defines the high-level algorithm (navigate → observe → register) while `RecorderToolExecutor` implements specific tool execution logic.

### Facade: SDK Abstraction

The `@actionbookdev/sdk` package provides a simple facade over the complex API endpoints and data transformations.

Sources: Diagram 4 and Diagram 5 from provided diagrams

---

# Page: User Interfaces

# User Interfaces

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [LICENSE](LICENSE)
- [README.md](README.md)
- [packages/cli/package.json](packages/cli/package.json)
- [packages/js-sdk/package.json](packages/js-sdk/package.json)
- [packages/mcp/package.json](packages/mcp/package.json)

</details>



## Purpose and Scope

This document describes the three user-facing interfaces for consuming Actionbook data: the CLI (Command Line Interface), MCP Server (Model Context Protocol), and JavaScript SDK. These interfaces provide different ways to search action manuals, retrieve element selectors, and integrate with AI agents and automation frameworks.

For information about the backend API service that these interfaces consume, see [API Service](#3.1). For details on browser automation commands available through the CLI, see [Browser Automation Commands](#2.1.1). For SDK integration patterns with specific LLM frameworks, see [JavaScript SDK](#2.3).

## Overview

Actionbook provides three distinct interfaces that share a common backend but serve different use cases:

| Interface | Package | Primary Use Case | Target Users |
|-----------|---------|------------------|--------------|
| **CLI** | `@actionbookdev/cli` | Command-line automation, AI agent tool execution | Developers, AI agents using shell commands |
| **MCP Server** | `@actionbookdev/mcp` | IDE integration, AI assistant tools | Claude Code, Cursor, VS Code users |
| **JavaScript SDK** | `@actionbookdev/sdk` | Programmatic integration, custom agents | JavaScript/TypeScript developers |

All three interfaces communicate with the same REST API endpoints for action search and retrieval. The CLI also includes browser automation capabilities via the `agent-browser` package.

**Sources:** [README.md:86-93](), [packages/cli/package.json:1-10](), [packages/mcp/package.json:1-16](), [packages/js-sdk/package.json:1-12]()

## Interface Architecture

The following diagram illustrates how each interface connects to the underlying systems:

```mermaid
graph TB
    subgraph "User Space"
        Terminal["Terminal/Shell"]
        IDE["AI IDE<br/>(Cursor, Claude, VS Code)"]
        CustomAgent["Custom Agent Code"]
    end
    
    subgraph "CLI Package (@actionbookdev/cli)"
        CLIEntry["dist/index.js<br/>(bin: actionbook)"]
        CLICommands["Commands:<br/>search, get, sources, browser"]
        CLIBrowser["agent-browser wrapper"]
    end
    
    subgraph "MCP Package (@actionbookdev/mcp)"
        MCPEntry["dist/cli.js<br/>(bin: actionbook-mcp)"]
        MCPServer["MCP Server<br/>(@modelcontextprotocol/sdk)"]
        MCPTools["Tools:<br/>search_actions<br/>get_action_by_id"]
    end
    
    subgraph "SDK Package (@actionbookdev/sdk)"
        ActionbookClass["Actionbook class"]
        SDKMethods["Methods:<br/>searchActions()<br/>getActionById()"]
        ToolDefs["Tool Definitions<br/>with JSON Schema & Zod"]
    end
    
    subgraph "Shared Infrastructure"
        SDKAPI["SDK API Client<br/>(fetch-based)"]
        APIService["API Service<br/>/actions/search<br/>/actions/:id"]
    end
    
    Terminal --> CLIEntry
    CLIEntry --> CLICommands
    CLICommands --> SDKAPI
    CLICommands --> CLIBrowser
    CLIBrowser -.->|"Browser automation"| Chromium["Chromium"]
    
    IDE --> MCPEntry
    MCPEntry --> MCPServer
    MCPServer --> MCPTools
    MCPTools --> SDKAPI
    
    CustomAgent --> ActionbookClass
    ActionbookClass --> SDKMethods
    SDKMethods --> SDKAPI
    SDKMethods --> ToolDefs
    
    SDKAPI --> APIService
    
    style CLIEntry fill:#f9f9f9
    style MCPEntry fill:#f9f9f9
    style ActionbookClass fill:#f9f9f9
    style APIService fill:#e8e8e8
```

**Sources:** [README.md:86-93](), [packages/cli/package.json:9-11](), [packages/mcp/package.json:14-16](), [packages/js-sdk/package.json:6-12]()

## CLI (Command Line Interface)

The CLI is implemented in the `@actionbookdev/cli` package and provides command-line access to Actionbook functionality. The entry point is [packages/cli/dist/index.js](), which is exposed as the `actionbook` binary.

### Command Structure

```mermaid
graph LR
    actionbook["actionbook<br/>(main binary)"]
    
    search["search &lt;query&gt;<br/>Search action manuals"]
    get["get &lt;id&gt;<br/>Get action by ID"]
    sources["sources<br/>List available sources"]
    browser["browser &lt;command&gt;<br/>Browser automation"]
    
    browserOpen["open &lt;url&gt;"]
    browserClick["click &lt;selector&gt;"]
    browserFill["fill &lt;selector&gt; &lt;text&gt;"]
    browserInstall["install"]
    
    actionbook --> search
    actionbook --> get
    actionbook --> sources
    actionbook --> browser
    
    browser --> browserOpen
    browser --> browserClick
    browser --> browserFill
    browser --> browserInstall
```

**Sources:** [README.md:117-130](), [packages/cli/package.json:26-30]()

### Dependencies

The CLI package has three key dependencies:

| Dependency | Version | Purpose |
|------------|---------|---------|
| `@actionbookdev/sdk` | workspace:* | API client for search/get operations |
| `agent-browser` | ^0.8.3 | Browser automation via Chromium |
| `commander` | ^12.1.0 | Command-line argument parsing |
| `chalk` | ^5.3.0 | Terminal output formatting |

The CLI internally uses the SDK's `Actionbook` class to communicate with the API service. Browser commands are delegated to the `agent-browser` package, which provides a Chromium-based automation interface.

**Sources:** [packages/cli/package.json:26-31]()

## MCP Server

The MCP Server is implemented in the `@actionbookdev/mcp` package and exposes Actionbook functionality through the Model Context Protocol. The entry point is [packages/mcp/dist/cli.js](), exposed as the `actionbook-mcp` binary.

### Tool Definitions

The MCP server exposes two tools that AI assistants can invoke:

```mermaid
graph TB
    MCPServer["MCP Server<br/>(actionbook-mcp binary)"]
    
    searchTool["Tool: search_actions"]
    getTool["Tool: get_action_by_id"]
    
    searchParams["Parameters:<br/>- query: string (required)"]
    getParams["Parameters:<br/>- id: string (required)"]
    
    searchExec["Calls: actionbook.searchActions(query)"]
    getExec["Calls: actionbook.getActionById(id)"]
    
    APIEndpoint["API Endpoints:<br/>/actions/search<br/>/actions/:id"]
    
    MCPServer --> searchTool
    MCPServer --> getTool
    
    searchTool --> searchParams
    getTool --> getParams
    
    searchParams --> searchExec
    getParams --> getExec
    
    searchExec --> APIEndpoint
    getExec --> APIEndpoint
```

**Sources:** [README.md:677-688](), [packages/mcp/package.json:31-36]()

### IDE Integration Configuration

The MCP server is designed to be invoked via `npx` for zero-installation integration. The configuration format varies by IDE but follows a common pattern:

```json
{
  "mcpServers": {
    "actionbook": {
      "command": "npx",
      "args": ["-y", "@actionbookdev/mcp@latest"]
    }
  }
}
```

This configuration is compatible with:
- Cursor (`Settings` → `Cursor Settings` → `MCP`)
- Claude Desktop (`claude_desktop_config.json`)
- Windsurf (`~/.codeium/windsurf/mcp_config.json`)
- VS Code (settings JSON)
- Cline, Zed, JetBrains IDEs, and others

**Sources:** [README.md:138-260](), [packages/mcp/package.json:14-16]()

### MCP Protocol Integration

```mermaid
graph LR
    subgraph "AI IDE"
        Assistant["AI Assistant<br/>(Claude, GPT, etc.)"]
    end
    
    subgraph "MCP Transport Layer"
        StdioTransport["stdio transport<br/>(@modelcontextprotocol/sdk)"]
    end
    
    subgraph "MCP Server Process"
        MCPHandlers["Tool handlers:<br/>search_actions<br/>get_action_by_id"]
        SDKClient["Actionbook SDK client"]
    end
    
    subgraph "Backend"
        API["API Service<br/>actionbook.dev"]
    end
    
    Assistant -->|"JSON-RPC"| StdioTransport
    StdioTransport --> MCPHandlers
    MCPHandlers --> SDKClient
    SDKClient -->|"HTTP"| API
```

**Sources:** [packages/mcp/package.json:31-36]()

## JavaScript SDK

The JavaScript SDK is implemented in the `@actionbookdev/sdk` package and provides programmatic access to Actionbook functionality. It serves as the foundation for both the CLI and MCP server implementations.

### SDK Core API

The primary class is `Actionbook`, which exposes methods with attached metadata for LLM integration:

```typescript
class Actionbook {
  searchActions(query: string): Promise<ActionSearchResult[]>
  getActionById(id: string): Promise<Action>
  listSources(): Promise<Source[]>
  searchSources(query: string): Promise<Source[]>
}
```

Each method includes:
- `description`: String describing the tool's purpose
- `params.json`: JSON Schema for parameters
- `params.zod`: Zod schema for parameters

**Sources:** [README.md:450-489](), [packages/js-sdk/package.json:1-12]()

### Tool Definition Structure

```mermaid
graph TB
    subgraph "SDK Method Structure"
        Method["Method:<br/>searchActions(query: string)"]
        
        FunctionImpl["Function implementation<br/>(async HTTP call)"]
        Description["description property:<br/>'Search for action manuals'"]
        ParamsJSON["params.json property:<br/>JSON Schema object"]
        ParamsZod["params.zod property:<br/>Zod schema object"]
    end
    
    subgraph "Integration Points"
        VercelAI["Vercel AI SDK<br/>tool({ parameters: params.zod })"]
        OpenAI["OpenAI SDK<br/>function: { parameters: params.json }"]
        Anthropic["Anthropic SDK<br/>input_schema: params.json"]
        Gemini["Google Gemini<br/>parameters: params.json"]
    end
    
    Method --> FunctionImpl
    Method --> Description
    Method --> ParamsJSON
    Method --> ParamsZod
    
    ParamsZod --> VercelAI
    ParamsJSON --> OpenAI
    ParamsJSON --> Anthropic
    ParamsJSON --> Gemini
    Description --> VercelAI
    Description --> OpenAI
    Description --> Anthropic
    Description --> Gemini
```

**Sources:** [README.md:473-489](), [packages/js-sdk/package.json:27-29]()

### SDK Dependencies

The SDK has minimal dependencies to maintain broad compatibility:

| Dependency | Version | Purpose |
|------------|---------|---------|
| `zod` | ^3.25.6 | Schema validation and Zod parameter definitions |
| `zod-to-json-schema` | ^3.22.5 | Converting Zod schemas to JSON Schema format |

The SDK uses only standard `fetch` for HTTP requests, avoiding framework-specific clients.

**Sources:** [packages/js-sdk/package.json:27-29]()

### Framework Integration Patterns

The SDK is designed for integration with multiple LLM frameworks. The following table shows the mapping between SDK exports and framework-specific tool definitions:

| Framework | Tool Definition | Uses `description` | Uses `params.zod` | Uses `params.json` |
|-----------|----------------|-------------------|-------------------|-------------------|
| Vercel AI SDK | `tool()` | ✓ | ✓ | |
| OpenAI SDK | `ChatCompletionTool` | ✓ | | ✓ |
| Anthropic SDK | `Tool` | ✓ | | ✓ |
| Google Gemini | `FunctionDeclaration` | ✓ | | ✓ |
| Stagehand | `tool()` | ✓ | ✓ | |

**Sources:** [README.md:493-659]()

## Interface Communication Flow

The following diagram shows how data flows from user interaction through the interfaces to the API service:

```mermaid
sequenceDiagram
    participant User
    participant CLI as "CLI<br/>(actionbook binary)"
    participant MCP as "MCP Server<br/>(actionbook-mcp)"
    participant SDK as "SDK<br/>(Actionbook class)"
    participant API as "API Service<br/>(/actions/search)"
    
    Note over User,API: CLI Flow
    User->>CLI: actionbook search "airbnb"
    CLI->>SDK: new Actionbook().searchActions("airbnb")
    SDK->>API: GET /actions/search?q=airbnb
    API-->>SDK: [{ id, name, selectors, ... }]
    SDK-->>CLI: ActionSearchResult[]
    CLI-->>User: Formatted console output
    
    Note over User,API: MCP Flow
    User->>MCP: AI invokes search_actions tool
    MCP->>SDK: actionbook.searchActions("airbnb")
    SDK->>API: GET /actions/search?q=airbnb
    API-->>SDK: [{ id, name, selectors, ... }]
    SDK-->>MCP: ActionSearchResult[]
    MCP-->>User: MCP response (JSON-RPC)
    
    Note over User,API: SDK Direct Flow
    User->>SDK: actionbook.searchActions("airbnb")
    SDK->>API: GET /actions/search?q=airbnb
    API-->>SDK: [{ id, name, selectors, ... }]
    SDK-->>User: ActionSearchResult[]
```

**Sources:** [README.md:117-130](), [README.md:450-470](), [README.md:677-688]()

## Installation Methods

Each interface has a different installation and execution pattern:

### CLI Installation

```bash
# Global installation
npm install -g @actionbookdev/cli

# Direct execution (no installation)
npx @actionbookdev/cli search "query"

# Verify installation
actionbook --version
```

The CLI requires browser installation for automation features:
```bash
actionbook browser install
```

### MCP Server Installation

The MCP server is typically invoked via `npx` without explicit installation:

```bash
# Direct invocation
npx -y @actionbookdev/mcp@latest

# Via IDE configuration (automatic invocation)
# See IDE-specific configuration in [README.md:138-424]()
```

### SDK Installation

```bash
# npm
npm install @actionbookdev/sdk

# pnpm
pnpm add @actionbookdev/sdk

# yarn
yarn add @actionbookdev/sdk

# bun
bun add @actionbookdev/sdk
```

**Sources:** [README.md:106-116](), [README.md:134-424](), [README.md:429-446]()

## Common Type Definitions

All three interfaces work with the same type definitions, which are exported from the SDK package:

| Type | Purpose | Key Fields |
|------|---------|-----------|
| `ActionSearchResult` | Search result items | `id`, `name`, `description`, `site`, `score` |
| `Action` | Complete action details | `id`, `name`, `selectors`, `allowMethod`, `pageContext` |
| `Selectors` | Element selector collection | `css`, `xpath`, `id`, `dataTestId`, `ariaLabel` |
| `Source` | Website source information | `id`, `url`, `name`, `status` |

These types are defined in the SDK and shared across all interfaces. For detailed type definitions, see [Data Models and Types](#7).

**Sources:** [packages/js-sdk/package.json:6-12]()

## Environment Configuration

### CLI Environment Variables

The CLI reads the following environment variables:

```bash
ACTIONBOOK_API_URL=https://actionbook.dev  # API endpoint (optional)
```

### MCP Server Environment Variables

The MCP server supports the same environment variables as the CLI. These can be set in IDE configuration:

```json
{
  "mcpServers": {
    "actionbook": {
      "command": "npx",
      "args": ["-y", "@actionbookdev/mcp@latest"],
      "env": {
        "ACTIONBOOK_API_URL": "https://actionbook.dev"
      }
    }
  }
}
```

### SDK Configuration

The SDK `Actionbook` class accepts configuration in its constructor:

```typescript
const actionbook = new Actionbook({
  baseURL: 'https://actionbook.dev',  // Optional, defaults to public API
  apiKey: undefined                    // Optional, not required during open beta
})
```

**Sources:** [README.md:102](), [README.md:304-315]()

## Selecting the Right Interface

Use this decision tree to choose the appropriate interface:

```mermaid
graph TD
    Start["Choose Interface"]
    
    Start --> Q1{"Using an AI IDE?"}
    Q1 -->|Yes| Q2{"IDE supports MCP?"}
    Q1 -->|No| Q3{"Building custom agent?"}
    
    Q2 -->|Yes| MCP["Use MCP Server<br/>@actionbookdev/mcp"]
    Q2 -->|No| CLI1["Use CLI<br/>@actionbookdev/cli"]
    
    Q3 -->|Yes| Q4{"Using JavaScript/TypeScript?"}
    Q3 -->|No| CLI2["Use CLI<br/>@actionbookdev/cli"]
    
    Q4 -->|Yes| SDK["Use SDK<br/>@actionbookdev/sdk"]
    Q4 -->|No| CLI3["Use CLI<br/>@actionbookdev/cli"]
    
    style MCP fill:#e8e8e8
    style SDK fill:#e8e8e8
    style CLI1 fill:#e8e8e8
    style CLI2 fill:#e8e8e8
    style CLI3 fill:#e8e8e8
```

**Sources:** [README.md:86-93]()

---

# Page: CLI (Command Line Interface)

# CLI (Command Line Interface)

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [LICENSE](LICENSE)
- [packages/cli/README.md](packages/cli/README.md)
- [packages/cli/package.json](packages/cli/package.json)
- [packages/cli/src/commands/browser.ts](packages/cli/src/commands/browser.ts)
- [packages/cli/src/commands/get.ts](packages/cli/src/commands/get.ts)
- [packages/cli/src/commands/search.ts](packages/cli/src/commands/search.ts)
- [packages/cli/src/commands/sources.ts](packages/cli/src/commands/sources.ts)
- [packages/cli/src/index.ts](packages/cli/src/index.ts)
- [packages/cli/src/output.ts](packages/cli/src/output.ts)
- [packages/cli/src/utils/process.ts](packages/cli/src/utils/process.ts)
- [packages/cli/tsconfig.build.json](packages/cli/tsconfig.build.json)
- [packages/cli/tsconfig.json](packages/cli/tsconfig.json)
- [packages/js-sdk/package.json](packages/js-sdk/package.json)
- [packages/mcp/package.json](packages/mcp/package.json)

</details>



## Purpose and Scope

The CLI package (`@actionbookdev/cli`) provides a command-line interface for interacting with Actionbook's action manual database and browser automation capabilities. It serves as the primary tool for developers to search for verified website selectors, retrieve action details, manage sources, and execute browser automation commands.

This document covers the CLI's architecture, commands, and implementation. For programmatic access to the same functionality, see [JavaScript SDK](#2.3). For AI agent integration, see [MCP Server](#2.2). For details on the underlying browser automation commands, see [Browser Automation Commands](#2.1.1).

## Package Architecture

The CLI is published as `@actionbookdev/cli` and consists of a thin command-line wrapper around the core SDK with additional browser automation integration.

**Package Structure:**

```mermaid
graph TB
    EntryPoint["index.ts<br/>CLI entry point"]
    
    subgraph Commands
        SearchCmd["search.ts<br/>searchCommand"]
        GetCmd["get.ts<br/>getCommand"]
        SourcesCmd["sources.ts<br/>sourcesCommand"]
        BrowserCmd["browser.ts<br/>browserCommand"]
    end
    
    subgraph Utilities
        OutputUtils["output.ts<br/>getApiKey()<br/>handleError()<br/>outputResult()"]
        ProcessUtils["process.ts<br/>spawnCommand()<br/>spawnAgentBrowser()<br/>installAgentBrowser()"]
    end
    
    subgraph "External Dependencies"
        SDK["@actionbookdev/sdk<br/>Actionbook client"]
        Commander["commander<br/>Command parser"]
        AgentBrowser["agent-browser<br/>Browser automation"]
        Chalk["chalk<br/>Terminal colors"]
    end
    
    EntryPoint --> Commander
    EntryPoint --> SearchCmd
    EntryPoint --> GetCmd
    EntryPoint --> SourcesCmd
    EntryPoint --> BrowserCmd
    
    SearchCmd --> SDK
    SearchCmd --> OutputUtils
    GetCmd --> SDK
    GetCmd --> OutputUtils
    SourcesCmd --> SDK
    SourcesCmd --> OutputUtils
    
    BrowserCmd --> ProcessUtils
    ProcessUtils --> AgentBrowser
    
    OutputUtils --> Chalk
```

Sources: [packages/cli/src/index.ts:1-29](), [packages/cli/package.json:1-57]()

### Key Components

| Component | File | Purpose |
|-----------|------|---------|
| `index.ts` | [packages/cli/src/index.ts]() | Main entry point, command registration |
| `searchCommand` | [packages/cli/src/commands/search.ts]() | Search for action manuals |
| `getCommand` | [packages/cli/src/commands/get.ts]() | Retrieve action details by ID |
| `sourcesCommand` | [packages/cli/src/commands/sources.ts]() | List and search website sources |
| `browserCommand` | [packages/cli/src/commands/browser.ts]() | Forward commands to agent-browser |
| Output utilities | [packages/cli/src/output.ts]() | API key resolution, error handling, JSON output |
| Process utilities | [packages/cli/src/utils/process.ts]() | Command spawning, agent-browser integration |

Sources: [packages/cli/src/index.ts:1-29]()

## Installation and Setup

### Installation Methods

The CLI can be installed globally or used via npx:

```bash
# Global installation
npm install -g @actionbookdev/cli

# Use without installation
npx @actionbookdev/cli search "query"
```

The package is configured as a binary with the command name `actionbook` [packages/cli/package.json:9-11]().

### Authentication

The CLI requires an API key for accessing the Actionbook API. Authentication is handled through the `getApiKey()` function [packages/cli/src/output.ts:7-9](), which supports two methods:

1. **Environment variable** (recommended):
```bash
export ACTIONBOOK_API_KEY=your_api_key
```

2. **Command-line option**:
```bash
actionbook --api-key your_api_key search "query"
```

The global `--api-key` option is registered on the root program [packages/cli/src/index.ts:21]().

Sources: [packages/cli/src/output.ts:7-9](), [packages/cli/src/index.ts:16-22]()

## Command Architecture

### Command Registration Flow

```mermaid
graph LR
    Program["program<br/>Command()"]
    
    Program --> SearchCmd["searchCommand<br/>.alias('s')"]
    Program --> GetCmd["getCommand<br/>.alias('g')"]
    Program --> SourcesCmd["sourcesCommand"]
    Program --> BrowserCmd["browserCommand"]
    
    SourcesCmd --> SourcesSearch["sources search<br/>.alias('s')"]
    
    SearchCmd --> Action1["async action()<br/>Actionbook.searchActions()"]
    GetCmd --> Action2["async action()<br/>Actionbook.getActionById()"]
    SourcesCmd --> Action3["async action()<br/>Actionbook.listSources()"]
    SourcesSearch --> Action4["async action()<br/>Actionbook.searchSources()"]
    BrowserCmd --> Action5["async action()<br/>spawnAgentBrowser()"]
```

Sources: [packages/cli/src/index.ts:23-26]()

## Search Command

The `search` command searches the action manual database using hybrid, vector, or full-text search.

### Command Definition

```bash
actionbook search <query> [options]
# Alias: actionbook s
```

**Command Implementation:** [packages/cli/src/commands/search.ts:7-58]()

### Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `-t, --type <type>` | `'vector' \| 'fulltext' \| 'hybrid'` | `'hybrid'` | Search algorithm |
| `-l, --limit <number>` | `1-100` | `5` | Maximum results |
| `-s, --source-ids <ids>` | `string` | - | Comma-separated source IDs |
| `--min-score <score>` | `0-1` | - | Minimum similarity threshold |
| `-j, --json` | `boolean` | `false` | Output raw JSON |

### Implementation Details

**Client Initialization:**
```typescript
const apiKey = getApiKey(options)
const client = new Actionbook({ apiKey })
```
[packages/cli/src/commands/search.ts:18-19]()

**API Call:**
```typescript
const result = await client.searchActions({
  query,
  type: options.type as SearchType,
  limit: parseInt(options.limit, 10),
  sourceIds: options.sourceIds,
  minScore: options.minScore ? parseFloat(options.minScore) : undefined,
})
```
[packages/cli/src/commands/search.ts:21-27]()

**Output Formatting:**
- JSON mode: Calls `outputResult(result)` [packages/cli/src/commands/search.ts:30]()
- Formatted mode: Displays numbered results with score and truncated content [packages/cli/src/commands/search.ts:32-53]()

Sources: [packages/cli/src/commands/search.ts:1-64]()

## Get Command

The `get` command retrieves complete action details including metadata, content, and UI element selectors.

### Command Definition

```bash
actionbook get <id> [options]
# Alias: actionbook g
```

**Command Implementation:** [packages/cli/src/commands/get.ts:6-71]()

### Action ID Format

The command accepts flexible ID formats with fuzzy matching:
- Full URL: `https://www.airbnb.com/search`
- URL without protocol: `airbnb.com/search`
- Domain only: `releases.rs`

The ID is passed directly to `client.getActionById(id)` [packages/cli/src/commands/get.ts:16]().

### Formatted Output Structure

The formatted output displays:

1. **Heading/Title** [packages/cli/src/commands/get.ts:22]()
2. **Metadata section** showing:
   - Action ID
   - Document title
   - Document URL
   - Chunk index
   - Token count
   [packages/cli/src/commands/get.ts:24-31]()

3. **Content section** with full chunk text [packages/cli/src/commands/get.ts:33-36]()

4. **UI Elements section** (if present) parsing `result.elements` JSON and displaying:
   - Element name
   - CSS selector
   - XPath selector
   - Description
   - Element type
   - Allowed methods
   [packages/cli/src/commands/get.ts:38-66]()

Sources: [packages/cli/src/commands/get.ts:1-71]()

## Sources Command

The `sources` command manages website source queries with both listing and search capabilities.

### Base Command

```bash
actionbook sources [options]
```

**Options:**
- `-l, --limit <number>`: Maximum results (default: 50)
- `-j, --json`: Output raw JSON

**Implementation:** [packages/cli/src/commands/sources.ts:7-28]()

### Search Subcommand

```bash
actionbook sources search <query> [options]
# Alias: actionbook sources s
```

**Options:**
- `-l, --limit <number>`: Maximum results (default: 10)
- `-j, --json`: Output raw JSON

**Implementation:** [packages/cli/src/commands/sources.ts:31-62]()

### Source List Formatting

**Formatted Output Structure:**

```mermaid
graph TD
    FormatCall["formatSourceList()<br/>sources, count"]
    
    FormatCall --> Header["Table Header:<br/>ID | Name | URL"]
    Header --> Rows["For each source:"]
    Rows --> Row1["ID (yellow)"]
    Rows --> Row2["Name (white, max 30 chars)"]
    Rows --> Row3["URL (cyan)"]
    Rows --> Optional1["Optional: Description (dim)"]
    Rows --> Optional2["Optional: Tags (magenta)"]
    Rows --> Footer["Usage tip"]
```

**Column Width Calculation:**
- ID: Maximum source ID length, minimum 2 [packages/cli/src/commands/sources.ts:73]()
- Name: Maximum name length, capped at 30 [packages/cli/src/commands/sources.ts:74]()
- URL: No truncation

The `truncate()` helper function shortens strings with ellipsis [packages/cli/src/commands/sources.ts:114-117]().

Sources: [packages/cli/src/commands/sources.ts:1-118]()

## Browser Command

The `browser` command forwards all arguments to the `agent-browser` CLI, providing a unified interface for browser automation.

### Architecture

```mermaid
graph TB
    User["User: actionbook browser open example.com"]
    
    BrowserCmd["browserCommand<br/>.allowUnknownOption(true)<br/>.allowExcessArguments(true)<br/>.helpOption(false)"]
    
    User --> BrowserCmd
    
    BrowserCmd --> CheckArgs{"args.length === 0?"}
    
    CheckArgs -->|Yes| ShowHelp["spawnAgentBrowser(['--help'])"]
    CheckArgs -->|No| CheckInstall{"args[0] === 'install'?"}
    
    CheckInstall -->|Yes| Install["installAgentBrowser(args.slice(1))"]
    CheckInstall -->|No| Forward["spawnAgentBrowser(args)"]
    
    Install --> FindPlaywright["findPlaywrightCoreCli()<br/>Search node_modules"]
    FindPlaywright --> SpawnNode["spawn('node', [playwrightCliPath,<br/>'install', 'chromium'])"]
    
    Forward --> SpawnNpx["spawn('npx', ['agent-browser', ...args])<br/>cwd: cliPackageRoot"]
    ShowHelp --> SpawnNpx
    
    SpawnNpx --> Transform["Transform stdout/stderr:<br/>Replace 'agent-browser'<br/>with 'actionbook browser'"]
    Transform --> Output["process.stdout.write()"]
```

Sources: [packages/cli/src/commands/browser.ts:1-31](), [packages/cli/src/utils/process.ts:55-103]()

### Command Configuration

The command uses special Commander.js settings to forward all arguments:

```typescript
.allowUnknownOption(true)  // Allow any flags
.allowExcessArguments(true) // Allow any positional args
.helpOption(false)         // Don't intercept -h/--help
```
[packages/cli/src/commands/browser.ts:7-9]()

### Agent Browser Execution

**Function:** `spawnAgentBrowser(args: string[])`  
**File:** [packages/cli/src/utils/process.ts:55-103]()

**Execution Details:**
1. Determines CLI package root by traversing from current file [packages/cli/src/utils/process.ts:58-59]()
2. Spawns `npx agent-browser` with inherited stdin, piped stdout/stderr [packages/cli/src/utils/process.ts:61-66]()
3. Sets `cwd` to CLI package directory to ensure `agent-browser` is resolved from CLI's `node_modules` [packages/cli/src/utils/process.ts:65]()
4. Transforms output streams to replace "agent-browser" with "actionbook browser" for brand consistency [packages/cli/src/utils/process.ts:71-82]()

### Installation Command

**Function:** `installAgentBrowser(installArgs: string[])`  
**File:** [packages/cli/src/utils/process.ts:172-230]()

The `actionbook browser install` command downloads Chromium binaries using Playwright's CLI.

**Installation Flow:**

| Step | Implementation |
|------|----------------|
| 1. Locate playwright-core CLI | `findPlaywrightCoreCli()` searches multiple node_modules structures |
| 2. Check pnpm structure | Looks for `node_modules/.pnpm/playwright-core@*/node_modules/playwright-core/cli.js` |
| 3. Check npm flat structure | Looks for `node_modules/playwright-core/cli.js` |
| 4. Check npm nested | Looks for `node_modules/agent-browser/node_modules/playwright-core/cli.js` |
| 5. Execute install | Spawns `node [playwrightCliPath] install chromium [--with-deps]` |

**Node Modules Search:** [packages/cli/src/utils/process.ts:126-165]()

**Install Execution:** [packages/cli/src/utils/process.ts:188-219]()

### Error Handling

If `agent-browser` is not found (ENOENT error), the CLI displays installation instructions via `showAgentBrowserInstallation()` [packages/cli/src/utils/process.ts:108-120]():

```
agent-browser is not installed or not in PATH.

agent-browser is a fast browser automation CLI for AI agents.
To install it, run:

  npm install -g agent-browser

Learn more: https://github.com/vercel-labs/agent-browser
```

Sources: [packages/cli/src/utils/process.ts:55-230](), [packages/cli/src/commands/browser.ts:1-31]()

## Output Format System

### Output Mode Selection

All commands support two output modes controlled by the `-j, --json` flag:

```mermaid
graph LR
    Command["Command execution"]
    
    Command --> Check{"options.json?"}
    
    Check -->|true| JSON["outputResult(data)<br/>JSON.stringify(data, null, 2)"]
    Check -->|false| Formatted["Formatted output<br/>with chalk colors"]
    
    JSON --> Stdout["console.log()"]
    Formatted --> Stdout
```

**Output Function:** [packages/cli/src/output.ts:14-16]()

### Formatted Output Implementation

Formatted output uses the `chalk` library for terminal colors:

| Color | Usage | Example |
|-------|-------|---------|
| `chalk.cyan` | Headings, links | Section titles, URLs |
| `chalk.yellow` | IDs, warnings | Source IDs, "No results" |
| `chalk.white` | Primary text | Descriptions, content |
| `chalk.dim` | Secondary text | Separators, hints |
| `chalk.gray` | Labels | Field names |
| `chalk.red` | Errors | Error messages |
| `chalk.green` | Success | Installation complete |
| `chalk.magenta` | Tags | Source tags |

**Examples:**
- Search results heading: `chalk.bold.cyan()` [packages/cli/src/commands/search.ts:37]()
- Element names: `chalk.yellow()` [packages/cli/src/commands/get.ts:45]()
- Separators: `chalk.dim('─'.repeat(50))` [packages/cli/src/commands/get.ts:25]()

Sources: [packages/cli/src/output.ts:1-34](), [packages/cli/src/commands/search.ts:32-53]()

## Error Handling System

### Error Handler Function

**Function:** `handleError(error: unknown)`  
**File:** [packages/cli/src/output.ts:21-34]()

**Error Type Detection:**

```mermaid
graph TD
    HandleError["handleError(error)"]
    
    HandleError --> Check1{"isActionbookError(error)?"}
    
    Check1 -->|Yes| DisplaySDKError["Display error.code<br/>error.message<br/>error.suggestion"]
    Check1 -->|No| Check2{"error instanceof Error?"}
    
    Check2 -->|Yes| DisplayError["Display error.message"]
    Check2 -->|No| DisplayUnknown["Display 'Unknown error'"]
    
    DisplaySDKError --> Exit["process.exit(1)"]
    DisplayError --> Exit
    DisplayUnknown --> Exit
```

### SDK Error Format

The `isActionbookError()` type guard [packages/cli/src/output.ts:22]() checks for errors from `@actionbookdev/sdk` with the structure:

```typescript
{
  code: string,
  message: string,
  suggestion?: string
}
```

When an SDK error is detected, the output includes:
1. Red error code [packages/cli/src/output.ts:23]()
2. White error message [packages/cli/src/output.ts:24]()
3. Yellow suggestion if present [packages/cli/src/output.ts:25-27]()

### Exit Code Handling

The CLI uses standard POSIX exit codes:

| Code | Meaning | Source |
|------|---------|--------|
| 0 | Success | Normal completion |
| 1 | General error | Handled errors, failed operations |
| 127 | Command not found | ENOENT from spawn [packages/cli/src/utils/process.ts:41]() |
| 128 + N | Signal termination | e.g., 130 for SIGINT (Ctrl+C) [packages/cli/src/utils/process.ts:29]() |

Sources: [packages/cli/src/output.ts:21-34](), [packages/cli/src/utils/process.ts:25-47]()

## Dependencies

### Direct Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `@actionbookdev/sdk` | workspace:* | Core API client for search/get operations |
| `agent-browser` | ^0.8.3 | Browser automation CLI (forwarded by browser command) |
| `chalk` | ^5.3.0 | Terminal color formatting |
| `commander` | ^12.1.0 | Command-line parsing and routing |

**Dependency Declaration:** [packages/cli/package.json:26-30]()

### Build and Development Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `typescript` | ^5.6.3 | Type checking and compilation |
| `vitest` | ^1.6.0 | Testing framework |
| `rimraf` | ^5.0.5 | Cross-platform file deletion for clean task |
| `@types/node` | ^20.14.0 | Node.js type definitions |

**Dev Dependencies:** [packages/cli/package.json:32-36]()

### TypeScript Configuration

**Compiler Options:**
- Target: ES2022
- Module system: NodeNext (ESM)
- Output directory: `./dist`
- Root directory: `./src`

**Full Configuration:** [packages/cli/tsconfig.json:1-21]()

Sources: [packages/cli/package.json:26-36](), [packages/cli/tsconfig.json:1-21]()

## Build and Publishing

### Build Scripts

```mermaid
graph LR
    Build["pnpm build"]
    Build --> TSC["tsc -p tsconfig.build.json"]
    TSC --> Dist["Outputs to dist/"]
    
    Dev["pnpm dev"]
    Dev --> TSCWatch["tsc -p tsconfig.build.json --watch"]
    
    Publish["npm publish"]
    Publish --> PrePublish["prepublishOnly hook"]
    PrePublish --> Build
```

**Scripts Definition:** [packages/cli/package.json:18-24]()

### Package Distribution

**Published Files:**
- Only the `dist/` directory is included [packages/cli/package.json:12-14]()

**Binary Configuration:**
- Command name: `actionbook`
- Entry point: `dist/index.js`
- Shebang: `#!/usr/bin/env node` [packages/cli/src/index.ts:1]()

**NPM Configuration:**
- Scope: `@actionbookdev`
- Access: public [packages/cli/package.json:15-17]()
- Registry: npmjs.com
- Version: 0.2.3 [packages/cli/package.json:3]()

Sources: [packages/cli/package.json:1-57](), [packages/cli/src/index.ts:1]()

---

# Page: Browser Automation Commands

# Browser Automation Commands

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [packages/cli/README.md](packages/cli/README.md)
- [packages/cli/src/commands/browser.ts](packages/cli/src/commands/browser.ts)
- [packages/cli/src/commands/get.ts](packages/cli/src/commands/get.ts)
- [packages/cli/src/commands/search.ts](packages/cli/src/commands/search.ts)
- [packages/cli/src/commands/sources.ts](packages/cli/src/commands/sources.ts)
- [packages/cli/src/index.ts](packages/cli/src/index.ts)
- [packages/cli/src/output.ts](packages/cli/src/output.ts)
- [packages/cli/src/utils/process.ts](packages/cli/src/utils/process.ts)
- [packages/cli/tsconfig.build.json](packages/cli/tsconfig.build.json)
- [packages/cli/tsconfig.json](packages/cli/tsconfig.json)

</details>



## Purpose and Scope

This page documents the `actionbook browser` command suite, which provides browser automation capabilities within the Actionbook CLI. This command acts as a wrapper around the [`agent-browser`](https://github.com/vercel-labs/agent-browser) CLI tool, transparently forwarding commands while handling installation and providing consistent branding.

The browser automation commands are used for **executing** website interactions (opening pages, clicking, filling forms, etc.) using verified selectors. This is distinct from the action recording process covered in [Action Recording](#3.2.2), which is how Actionbook generates the action manuals that inform these automation tasks.

For general CLI usage beyond browser automation, see [CLI (Command Line Interface)](#2.1).

---

## Command Architecture

The browser command system implements a transparent forwarding pattern where the Actionbook CLI wraps `agent-browser` functionality while maintaining consistent user experience.

```mermaid
graph TB
    User["User Terminal"]
    BrowserCommand["browserCommand<br/>packages/cli/src/commands/browser.ts"]
    InstallCheck{"Command == 'install'?"}
    InstallFunc["installAgentBrowser()<br/>packages/cli/src/utils/process.ts:172"]
    SpawnFunc["spawnAgentBrowser()<br/>packages/cli/src/utils/process.ts:55"]
    FindCLI["findPlaywrightCoreCli()<br/>Locate playwright-core CLI"]
    NPX["npx agent-browser<br/>Executed from CLI package dir"]
    Transform["Output Transformation<br/>agent-browser → actionbook browser"]
    AgentBrowser["agent-browser CLI<br/>External dependency"]
    PlaywrightCLI["playwright-core/cli.js<br/>Browser binary installation"]
    
    User -->|"actionbook browser [args]"| BrowserCommand
    BrowserCommand --> InstallCheck
    InstallCheck -->|"Yes"| InstallFunc
    InstallCheck -->|"No"| SpawnFunc
    
    InstallFunc --> FindCLI
    FindCLI --> PlaywrightCLI
    PlaywrightCLI -->|"Installs Chromium"| User
    
    SpawnFunc --> NPX
    NPX --> AgentBrowser
    AgentBrowser --> Transform
    Transform --> User
```

**Sources:** [packages/cli/src/commands/browser.ts:1-32](), [packages/cli/src/utils/process.ts:55-103]()

### Command Registration

The `browserCommand` is registered in the main CLI program with specific configuration to enable transparent argument forwarding:

| Configuration Option | Purpose |
|---------------------|---------|
| `allowUnknownOption(true)` | Passes through all CLI flags without validation |
| `allowExcessArguments(true)` | Forwards any number of positional arguments |
| `helpOption(false)` | Disables built-in help; forwards to agent-browser |

This configuration ensures that all arguments after `browser` are captured and forwarded to the underlying `agent-browser` process without interpretation by Commander.js.

**Sources:** [packages/cli/src/commands/browser.ts:5-11](), [packages/cli/src/index.ts:26]()

---

## Installation Process

The `actionbook browser install` command sets up the Chromium browser binaries required for automation. This is handled separately from the normal command forwarding flow.

### Installation Flow

```mermaid
graph TB
    Install["actionbook browser install<br/>[--with-deps]"]
    InstallFunc["installAgentBrowser()"]
    GetRoot["Determine CLI package root<br/>dirname(import.meta.url)"]
    FindCLI["findPlaywrightCoreCli()"]
    
    subgraph "Search Locations"
        PnpmCheck["Check .pnpm/playwright-core@*"]
        NPMFlat["Check node_modules/playwright-core"]
        NPMNested["Check node_modules/agent-browser/node_modules/playwright-core"]
    end
    
    FoundCLI["playwright-core/cli.js"]
    SpawnNode["spawn('node', [cli.js, 'install', 'chromium', '--with-deps?'])"]
    Success["Chromium installed"]
    
    Install --> InstallFunc
    InstallFunc --> GetRoot
    GetRoot --> FindCLI
    FindCLI --> PnpmCheck
    PnpmCheck --> NPMFlat
    NPMFlat --> NPMNested
    NPMNested --> FoundCLI
    FoundCLI --> SpawnNode
    SpawnNode --> Success
```

**Sources:** [packages/cli/src/utils/process.ts:172-230](), [packages/cli/src/commands/browser.ts:22-26]()

### Playwright CLI Resolution

The `findPlaywrightCoreCli` function searches multiple node_modules structures to locate the `playwright-core/cli.js` binary:

1. **pnpm Structure**: Searches `.pnpm/playwright-core@*/node_modules/playwright-core/cli.js` for versioned installations
2. **npm Flat Structure**: Checks `node_modules/playwright-core/cli.js` for flat installations
3. **npm Nested Structure**: Checks `node_modules/agent-browser/node_modules/playwright-core/cli.js` for nested dependencies

The search checks both the CLI package directory and the workspace root (two levels up) to support both standalone and monorepo installations.

**Sources:** [packages/cli/src/utils/process.ts:126-165]()

### Installation Command Arguments

| Argument | Purpose |
|----------|---------|
| `install` | Playwright CLI install subcommand |
| `chromium` | Browser variant to install (Chrome/Chromium) |
| `--with-deps` | (Optional) Install system dependencies on Linux |

The `--with-deps` flag is only necessary on Linux systems that lack required system libraries for Chromium (e.g., libatk, libcups, etc.).

**Sources:** [packages/cli/src/utils/process.ts:188-191](), [packages/cli/README.md:126-129]()

---

## Command Execution and Forwarding

All non-install browser commands are forwarded to `agent-browser` via the `spawnAgentBrowser` function, which implements transparent process spawning with output transformation.

### Execution Flow

```mermaid
graph TB
    BrowserCmd["actionbook browser <command>"]
    GetArgs["Extract args after 'browser'"]
    EmptyCheck{"args.length == 0?"}
    ShowHelp["Forward '--help' to agent-browser"]
    InstallCheck{"args[0] == 'install'?"}
    CallInstall["installAgentBrowser(args.slice(1))"]
    Forward["spawnAgentBrowser(args)"]
    
    subgraph "spawnAgentBrowser Implementation"
        GetCLIRoot["Get CLI package root<br/>dirname(__dirname)"]
        SpawnNPX["spawn('npx', ['agent-browser', ...args])<br/>cwd: CLI package dir"]
        PipeSTDIO["stdio: ['inherit', 'pipe', 'pipe']"]
        TransformOut["Transform stdout/stderr<br/>agent-browser → actionbook browser"]
        WriteOut["Write to process.stdout/stderr"]
    end
    
    ExitCode["Return exit code to user"]
    
    BrowserCmd --> GetArgs
    GetArgs --> EmptyCheck
    EmptyCheck -->|"Yes"| ShowHelp
    EmptyCheck -->|"No"| InstallCheck
    InstallCheck -->|"Yes"| CallInstall
    InstallCheck -->|"No"| Forward
    
    Forward --> GetCLIRoot
    GetCLIRoot --> SpawnNPX
    SpawnNPX --> PipeSTDIO
    PipeSTDIO --> TransformOut
    TransformOut --> WriteOut
    WriteOut --> ExitCode
    
    ShowHelp --> ExitCode
    CallInstall --> ExitCode
```

**Sources:** [packages/cli/src/commands/browser.ts:10-31](), [packages/cli/src/utils/process.ts:55-103]()

### Output Transformation

The `spawnAgentBrowser` function pipes stdout and stderr to apply text replacement before writing to the terminal:

```typescript
// Transform stdout
child.stdout.on('data', (data: Buffer) => {
  const output = data.toString().replace(/agent-browser/g, 'actionbook browser')
  process.stdout.write(output)
})

// Transform stderr
child.stderr.on('data', (data: Buffer) => {
  const output = data.toString().replace(/agent-browser/g, 'actionbook browser')
  process.stderr.write(output)
})
```

This ensures all help text, error messages, and command feedback display `actionbook browser` instead of `agent-browser`, maintaining consistent branding throughout the user experience.

**Sources:** [packages/cli/src/utils/process.ts:68-82]()

### Working Directory Context

The spawned `npx` process executes with `cwd: cliPackageRoot`, ensuring that `agent-browser` is resolved from the CLI package's own `node_modules` rather than the user's global or project-local packages. This guarantees version consistency between the CLI and its browser automation dependency.

**Sources:** [packages/cli/src/utils/process.ts:58-65]()

---

## Available Commands

The following table lists common `agent-browser` commands that are forwarded through `actionbook browser`. For the complete command reference, run `actionbook browser --help`.

| Command | Purpose | Example |
|---------|---------|---------|
| `open <url>` | Navigate to a URL | `actionbook browser open example.com` |
| `snapshot -i` | Get interactive elements with references | `actionbook browser snapshot -i` |
| `click <selector>` | Click an element by selector or @ref | `actionbook browser click @e1` |
| `fill <selector> <text>` | Fill an input field | `actionbook browser fill @e3 "test@example.com"` |
| `type <selector> <text>` | Type text into an element | `actionbook browser type input[name="q"] "search"` |
| `wait <selector\|ms>` | Wait for element or time | `actionbook browser wait 2000` |
| `screenshot [path]` | Take a screenshot | `actionbook browser screenshot page.png` |
| `session` | Display current session info | `actionbook browser session` |
| `close` | Close the browser | `actionbook browser close` |

**Sources:** [packages/cli/README.md:132-141](), [README.md:100-130]()

### Selector Reference Syntax

`agent-browser` provides element references (e.g., `@e1`, `@e2`) when using `snapshot -i`, which can be used in subsequent commands instead of CSS selectors. This reference-based approach simplifies automation scripts:

```bash
# Get interactive snapshot
actionbook browser snapshot -i
# Output: @e1: button "Submit"
#         @e2: input[type="email"]

# Use references in subsequent commands
actionbook browser fill @e2 "user@example.com"
actionbook browser click @e1
```

**Sources:** [packages/cli/README.md:207-218](), [README.md:127-129]()

---

## Error Handling

The command execution system implements error handling for common failure scenarios.

### Command Not Found (ENOENT)

When `npx` is not available or `agent-browser` cannot be resolved, the system detects the `ENOENT` error code and displays appropriate guidance:

```typescript
child.on('error', (error: NodeJS.ErrnoException) => {
  if (error.code === 'ENOENT') {
    console.error(chalk.red('\nnpx command not found.'))
    console.error(chalk.white('Please ensure npm 5.2+ is installed.\n'))
    resolve(127) // Standard exit code for command not found
  } else {
    console.error(chalk.red(`Failed to execute agent-browser: ${error.message}`))
    resolve(1)
  }
})
```

**Sources:** [packages/cli/src/utils/process.ts:92-101]()

### Signal Handling

Process termination signals (e.g., SIGINT from Ctrl+C) are properly converted to standard exit codes:

```typescript
child.on('close', (code, signal) => {
  if (signal) {
    // Convert signal to exit code: 128 + signal number
    resolve(128 + (signal === 'SIGINT' ? 2 : 15))
  } else {
    resolve(code ?? 1)
  }
})
```

This ensures that interrupt signals propagate correctly to the parent shell environment.

**Sources:** [packages/cli/src/utils/process.ts:84-90]()

### Installation Failure Messages

If browser installation fails, the system provides clear feedback and suggests troubleshooting:

```typescript
if (exitCode === 0) {
  console.log(chalk.green('\n✓ Browser automation setup complete!\n'))
  console.log(chalk.white('You can now use: ') + chalk.cyan('actionbook browser <command>\n'))
} else {
  console.error(chalk.red('\nBrowser setup encountered an error.'))
  console.error(chalk.white('Please check the output above for details.\n'))
}
```

**Sources:** [packages/cli/src/utils/process.ts:221-227]()

---

## Integration with Actionbook Workflow

The browser automation commands complement the action retrieval workflow:

```mermaid
graph LR
    Search["actionbook search<br/>'github login'"]
    Get["actionbook get<br/>github.com/login"]
    Extract["Extract verified<br/>selectors"]
    BrowserOpen["actionbook browser open<br/>github.com/login"]
    BrowserSnap["actionbook browser snapshot -i"]
    BrowserFill["actionbook browser fill<br/>@e1 'username'"]
    BrowserClick["actionbook browser click<br/>@e3"]
    
    Search --> Get
    Get --> Extract
    Extract --> BrowserOpen
    BrowserOpen --> BrowserSnap
    BrowserSnap --> BrowserFill
    BrowserFill --> BrowserClick
```

This workflow allows users to:
1. **Discover** relevant actions via search
2. **Retrieve** verified selectors via get
3. **Execute** automation via browser commands

The browser commands operate independently of the Actionbook API, providing general-purpose browser automation capabilities that can be used with or without Actionbook's action manuals.

**Sources:** [packages/cli/README.md:206-218](), [README.md:119-130]()

---

# Page: MCP Server

# MCP Server

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.claude-plugin/marketplace.json](.claude-plugin/marketplace.json)
- [.claude-plugin/plugin.json](.claude-plugin/plugin.json)
- [LICENSE](LICENSE)
- [README.md](README.md)
- [commands/manual.md](commands/manual.md)
- [packages/cli/package.json](packages/cli/package.json)
- [packages/js-sdk/package.json](packages/js-sdk/package.json)
- [packages/mcp/package.json](packages/mcp/package.json)
- [skills/actionbook/SKILL.md](skills/actionbook/SKILL.md)

</details>



This document covers the Actionbook MCP (Model Context Protocol) Server, which enables AI IDEs and coding assistants to access Actionbook's action manuals through standardized tool calling. For command-line usage, see [CLI](#2.1). For programmatic integration in custom applications, see [JavaScript SDK](#2.3).

## Overview

The MCP Server provides a Model Context Protocol-compliant interface to Actionbook, allowing AI assistants in IDEs like Cursor, Claude Desktop, VS Code, and others to search and retrieve action manuals. The server exposes two primary tools that AI agents can call to understand and automate website interactions.

**Package**: `@actionbookdev/mcp`  
**Published Version**: 0.1.3  
**Protocol**: Model Context Protocol (MCP)  
**Execution Model**: Server runs as a subprocess managed by the IDE

The MCP Server wraps the [JavaScript SDK](#2.3) and translates between MCP's JSON-RPC protocol and Actionbook's REST API, providing a standardized interface for AI tools.

Sources: [packages/mcp/package.json:1-48](), [README.md:134-425]()

## Architecture

The MCP Server acts as a protocol adapter between MCP-compatible clients and Actionbook's API Service:

```mermaid
graph TB
    subgraph "IDE/AI Assistant"
        IDE["MCP Client<br/>(Cursor, Claude, VS Code)"]
    end
    
    subgraph "MCP Server Process"
        CLI["actionbook-mcp CLI<br/>packages/mcp/src/cli.ts"]
        Server["MCP Server<br/>@modelcontextprotocol/sdk"]
        ToolHandler["Tool Handler<br/>search_actions<br/>get_action_by_id"]
        SDK["Actionbook SDK<br/>@actionbookdev/sdk"]
    end
    
    subgraph "Backend"
        API["API Service<br/>REST endpoints"]
        DB[("PostgreSQL<br/>elements, chunks")]
    end
    
    IDE -->|"JSON-RPC over stdio"| CLI
    CLI --> Server
    Server --> ToolHandler
    ToolHandler --> SDK
    SDK -->|"HTTP requests"| API
    API --> DB
    
    CLI -.->|"Environment vars<br/>ACTIONBOOK_API_KEY"| ToolHandler
```

### Component Responsibilities

| Component | File/Package | Responsibility |
|-----------|-------------|----------------|
| `actionbook-mcp` CLI | [packages/mcp/src/cli.ts]() | Entry point for MCP server subprocess |
| MCP Server | `@modelcontextprotocol/sdk` | Handles JSON-RPC protocol, stdio transport |
| Tool Handler | [packages/mcp/src/index.ts]() | Implements tool schemas and execution logic |
| Actionbook SDK | `@actionbookdev/sdk` | Makes HTTP requests to API Service |

Sources: [packages/mcp/package.json:1-48](), [README.md:134-206]()

## Installation and Configuration

### NPM Package

The MCP Server is distributed as an npm package that can be executed directly via `npx`:

```bash
npx -y @actionbookdev/mcp@latest
```

The `-y` flag auto-accepts the package installation prompt. IDEs execute this command as a subprocess and communicate via stdio.

**Package Structure**:
- **Main Entry**: `dist/index.js` - MCP server implementation
- **Binary Entry**: `dist/cli.js` - Command-line wrapper (`actionbook-mcp`)
- **Dependencies**: `@actionbookdev/sdk`, `@modelcontextprotocol/sdk`, `zod`, `zod-to-json-schema`

Sources: [packages/mcp/package.json:1-48]()

### IDE Integration

The MCP Server can be configured in various MCP-compatible IDEs by adding a server configuration. The standard configuration format is:

```json
{
  "mcpServers": {
    "actionbook": {
      "command": "npx",
      "args": ["-y", "@actionbookdev/mcp@latest"]
    }
  }
}
```

#### Supported IDEs

| IDE/Client | Configuration Location | Notes |
|------------|----------------------|-------|
| **Cursor** | Settings → Cursor Settings → MCP | GUI-based configuration |
| **Claude Code** | Via `claude mcp add` command | CLI-based setup |
| **VS Code** | Settings JSON (`mcp.servers`) | Manual JSON editing |
| **Windsurf** | `~/.codeium/windsurf/mcp_config.json` | File-based config |
| **Claude Desktop** | `claude_desktop_config.json` | File-based config |
| **Cline** | Settings → MCP Servers | GUI-based configuration |
| **Zed** | Settings JSON (`context_servers`) | Uses `context_servers` key |
| **JetBrains IDEs** | Settings → Tools → AI Assistant → MCP | GUI-based configuration |
| **Amazon Q Developer CLI** | `~/.aws/amazonq/mcp.json` | File-based config |
| **Warp** | Settings → AI → Manage MCP servers | GUI with `start_on_launch` option |
| **Roo Code** | Settings → MCP Servers | GUI-based configuration |
| **Augment Code** | Settings → MCP Servers | GUI-based configuration |
| **Trae** | Settings → MCP Servers | GUI-based configuration |
| **Gemini CLI** | `~/.gemini/settings.json` | File-based config |

#### Alternative Runtime Configurations

**Using Bun**:
```json
{
  "mcpServers": {
    "actionbook": {
      "command": "bunx",
      "args": ["@actionbookdev/mcp@latest"]
    }
  }
}
```

**Using Deno**:
```json
{
  "mcpServers": {
    "actionbook": {
      "command": "deno",
      "args": ["run", "--allow-all", "npm:@actionbookdev/mcp"]
    }
  }
}
```

Sources: [README.md:134-425]()

### Environment Variables

The MCP Server supports configuration via environment variables:

| Variable | Purpose | Default |
|----------|---------|---------|
| `ACTIONBOOK_API_KEY` | API key for authentication | Not required (open beta) |
| `ACTIONBOOK_API_URL` | Custom API endpoint | `https://api.actionbook.dev` |

Some IDEs (like Warp) allow passing environment variables directly in the configuration:

```json
{
  "actionbook": {
    "command": "npx",
    "args": ["-y", "@actionbookdev/mcp@latest", "--api-key", "YOUR_API_KEY"],
    "env": {},
    "working_directory": null,
    "start_on_launch": true
  }
}
```

Sources: [README.md:298-316]()

## Available Tools

The MCP Server exposes two tools that AI assistants can call:

### Tool Execution Flow

```mermaid
sequenceDiagram
    participant IDE as "IDE/AI Assistant"
    participant MCP as "MCP Server"
    participant SDK as "Actionbook SDK"
    participant API as "API Service"
    
    IDE->>MCP: tool_call: search_actions<br/>{query: "airbnb search"}
    MCP->>SDK: searchActions("airbnb search")
    SDK->>API: GET /actions/search?q=airbnb+search
    API-->>SDK: [{id, title, description}]
    SDK-->>MCP: Action results
    MCP-->>IDE: Tool response with actions
    
    IDE->>MCP: tool_call: get_action_by_id<br/>{id: "site/airbnb.com/..."}
    MCP->>SDK: getActionById("site/airbnb.com/...")
    SDK->>API: GET /actions/site%2Fairbnb.com%2F...
    API-->>SDK: {id, selectors, instructions}
    SDK-->>MCP: Full action manual
    MCP-->>IDE: Tool response with manual
```

Sources: [README.md:674-689](), [skills/actionbook/SKILL.md:50-73]()

### `search_actions`

Searches for action manuals by keyword or task description.

**Tool Schema**:
```typescript
{
  name: "search_actions",
  description: "Search for action manuals by keyword",
  inputSchema: {
    type: "object",
    properties: {
      query: {
        type: "string",
        description: "Search query to find relevant action manuals"
      }
    },
    required: ["query"]
  }
}
```

**Example Queries**:
- `"airbnb search"` - Find actions related to searching on Airbnb
- `"linkedin send message"` - Find LinkedIn messaging actions
- `"google login"` - Find Google authentication actions
- `"twitter post tweet"` - Find Twitter posting actions

**Response Format**:
```typescript
{
  results: [
    {
      id: "site/airbnb.com/page/home/element/search-button",
      title: "Search button on Airbnb homepage",
      description: "Click to open search form",
      url: "https://airbnb.com",
      score: 0.95
    }
  ]
}
```

Sources: [README.md:678-683](), [skills/actionbook/SKILL.md:54-62]()

### `get_action_by_id`

Retrieves detailed information about a specific action, including verified selectors and step-by-step instructions.

**Tool Schema**:
```typescript
{
  name: "get_action_by_id",
  description: "Retrieve a specific action manual by its ID",
  inputSchema: {
    type: "object",
    properties: {
      id: {
        type: "string",
        description: "The unique identifier of the action manual"
      }
    },
    required: ["id"]
  }
}
```

**Response Format**:
```typescript
{
  id: "site/airbnb.com/page/home/element/search-button",
  type: "button",
  title: "Search button",
  description: "Opens the search form for finding listings",
  url: "https://airbnb.com",
  selectors: {
    css: "button[data-testid='structured-search-input-search-button']",
    xpath: "//button[@data-testid='structured-search-input-search-button']",
    dataTestId: "structured-search-input-search-button",
    ariaLabel: "Search"
  },
  allowedMethods: ["click"],
  instructions: [
    "Navigate to https://airbnb.com",
    "Click the search button using the selector",
    "Wait for search form to appear"
  ]
}
```

Sources: [README.md:684-689](), [skills/actionbook/SKILL.md:65-73]()

## Usage Patterns

### Basic Workflow in AI IDEs

When an AI assistant needs to automate a website task, it follows this pattern:

1. **Search Phase**: AI calls `search_actions` with a task description
2. **Selection Phase**: AI examines search results and selects relevant actions
3. **Retrieval Phase**: AI calls `get_action_by_id` to get detailed selectors
4. **Execution Phase**: AI uses the selectors with browser automation tools

**Example Session**:

```
User: "Help me automate sending a message on LinkedIn"

AI: [Calls search_actions({query: "linkedin send message"})]
    → Receives list of LinkedIn messaging actions

AI: [Calls get_action_by_id({id: "site/linkedin.com/page/profile/element/message-button"})]
    → Receives full manual with selectors

AI: "I found the LinkedIn message button. Here's the automation code:
     await page.click('[data-testid="message-button"]')"
```

Sources: [skills/actionbook/SKILL.md:1-112]()

### Integration with Browser Automation

The MCP Server is commonly used in conjunction with the [CLI's browser commands](#2.1.1) or direct browser automation frameworks:

**Pattern 1: Using CLI Browser Commands**
```bash
# AI assistant generates these commands based on MCP tool responses
actionbook browser open linkedin.com/in/username
actionbook browser click '[data-testid="message-button"]'
actionbook browser fill 'div[role="textbox"]' 'Hello!'
actionbook browser click 'button[type="submit"]'
```

**Pattern 2: Using Playwright/Puppeteer**
```javascript
// AI assistant generates automation code using retrieved selectors
await page.click('[data-testid="message-button"]')
await page.type('div[role="textbox"]', 'Hello!')
await page.click('button[type="submit"]')
```

Sources: [skills/actionbook/SKILL.md:78-105]()

### Skill System Integration

The MCP Server is also exposed through the Actionbook skill in the skill/plugin system (see [Skills and Plugins](#2.4)). The skill provides:

- Automatic activation when users mention browser automation tasks
- Guided workflow for search → retrieve → execute pattern
- Integration with both CLI and MCP methods

**Skill Definition**:
```yaml
name: actionbook
description: Browser automation, web scraping, UI testing, AI agents
```

The skill automatically activates for queries like:
- "Send a LinkedIn message"
- "Book an Airbnb"
- "How do I post a tweet?"

Sources: [skills/actionbook/SKILL.md:1-4](), [.claude-plugin/plugin.json:1-10]()

## Command Line Interface

While the MCP Server is typically run as a subprocess by IDEs, it can also be executed directly for testing or debugging:

```bash
# Run the MCP server directly
npx @actionbookdev/mcp

# Or if installed globally
npm install -g @actionbookdev/mcp
actionbook-mcp

# With custom API key
ACTIONBOOK_API_KEY=your-key npx @actionbookdev/mcp
```

The server communicates via stdio using JSON-RPC 2.0 protocol. When run directly, it expects MCP client messages on stdin and writes responses to stdout.

**Testing Tool Calls**:

To test the MCP server locally, you can use an MCP client or send JSON-RPC messages manually:

```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "search_actions",
    "arguments": {
      "query": "airbnb search"
    }
  },
  "id": 1
}
```

Sources: [packages/mcp/package.json:14-16]()

## Marketplace Distribution

The MCP Server is distributed through multiple channels:

| Channel | Purpose | Configuration |
|---------|---------|---------------|
| **NPM Registry** | Direct installation via `npx` | `@actionbookdev/mcp@latest` |
| **Claude Plugin Marketplace** | Discovery in Claude Code | [.claude-plugin/marketplace.json]() |
| **Skill System** | Integration with skill-based workflows | [.claude-plugin/plugin.json]() |

The marketplace listing includes:
- **Main plugin**: Actionbook MCP server for browser automation
- **Related plugins**: rust-learner, arxiv-viewer, actionbook-scraper (see [Skills and Plugins](#2.4))

Sources: [.claude-plugin/marketplace.json:1-32](), [.claude-plugin/plugin.json:1-10]()

## Implementation Details

### Dependencies

The MCP Server relies on a minimal set of dependencies:

| Dependency | Version | Purpose |
|------------|---------|---------|
| `@actionbookdev/sdk` | workspace:* | Core API client |
| `@modelcontextprotocol/sdk` | ^1.23.0 | MCP protocol implementation |
| `undici` | ^6.21.0 | HTTP client for API requests |
| `zod` | ^3.25.6 | Schema validation |
| `zod-to-json-schema` | ^3.22.5 | Convert Zod schemas to JSON Schema for MCP |

The SDK dependency ensures consistency between MCP, CLI, and direct SDK usage (see [JavaScript SDK](#2.3) for SDK details).

Sources: [packages/mcp/package.json:31-37]()

### Build Process

The MCP package is built from TypeScript source:

```bash
# Build command (defined in package.json)
tsc -p tsconfig.build.json

# Pre-build step ensures SDK is built first
pnpm --filter @actionbookdev/sdk build
```

**Output Structure**:
- `dist/index.js` - Main MCP server implementation
- `dist/cli.js` - Binary entry point for `actionbook-mcp`
- `dist/**/*.d.ts` - TypeScript type definitions

The build process must complete before publishing to ensure the `dist/` directory is included in the npm package.

Sources: [packages/mcp/package.json:23-29]()

---

**Related Pages**:
- [CLI (Command Line Interface)](#2.1) - Alternative interface for direct command-line usage
- [JavaScript SDK](#2.3) - Programmatic integration in custom applications
- [Skills and Plugins](#2.4) - Skill system that wraps MCP tools
- [API Service](#3.1) - Backend REST API that MCP Server communicates with

---

# Page: JavaScript SDK

# JavaScript SDK

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [packages/js-sdk/src/api-client.ts](packages/js-sdk/src/api-client.ts)
- [packages/js-sdk/src/client.ts](packages/js-sdk/src/client.ts)
- [packages/js-sdk/src/tool-defs.ts](packages/js-sdk/src/tool-defs.ts)
- [packages/js-sdk/src/types.ts](packages/js-sdk/src/types.ts)

</details>



## Purpose and Scope

The JavaScript SDK (`@actionbookdev/sdk`) provides programmatic access to the Actionbook API for building custom AI agents and browser automation tools. The SDK enables developers to search for action manuals, retrieve DOM selectors, and integrate Actionbook capabilities into any LLM framework.

This page covers SDK installation, client initialization, API methods, tool definitions, and integration patterns. For CLI usage, see [CLI](#2.1). For MCP Server integration, see [MCP Server](#2.2). For API endpoint specifications, see [API Service](#3.1).

**Sources:** [README.md:428-446](), [packages/js-sdk/src/client.ts:120-140]()

---

## Installation

The SDK is published as `@actionbookdev/sdk` on npm and supports all major package managers:

```bash
# npm
npm install @actionbookdev/sdk

# pnpm
pnpm add @actionbookdev/sdk

# yarn
yarn add @actionbookdev/sdk

# bun
bun add @actionbookdev/sdk
```

**Requirements:**
- Node.js >= 18.0.0
- TypeScript 5.0+ (for type definitions)

**Sources:** [README.md:434-446]()

---

## Client Architecture

The SDK consists of two primary classes: `Actionbook` (user-facing client) and `ApiClient` (internal HTTP client).

```mermaid
graph TB
    subgraph "User Code"
        UserAgent["User Agent Code"]
    end
    
    subgraph "@actionbookdev/sdk"
        Actionbook["Actionbook<br/>Client Class"]
        ApiClient["ApiClient<br/>HTTP Client"]
        
        subgraph "Tool Definitions"
            searchActionsSchema["searchActionsSchema"]
            getActionByIdSchema["getActionByIdSchema"]
            listSourcesSchema["listSourcesSchema"]
            searchSourcesSchema["searchSourcesSchema"]
        end
        
        subgraph "Types"
            ChunkSearchResult["ChunkSearchResult"]
            ChunkActionDetail["ChunkActionDetail"]
            SourceListResult["SourceListResult"]
            SourceSearchResult["SourceSearchResult"]
        end
    end
    
    subgraph "External Services"
        APIService["API Service<br/>api.actionbook.dev"]
    end
    
    UserAgent --> Actionbook
    Actionbook --> ApiClient
    Actionbook --> searchActionsSchema
    Actionbook --> getActionByIdSchema
    Actionbook --> listSourcesSchema
    Actionbook --> searchSourcesSchema
    
    ApiClient --> APIService
    
    ApiClient -.->|returns| ChunkSearchResult
    ApiClient -.->|returns| ChunkActionDetail
    ApiClient -.->|returns| SourceListResult
    ApiClient -.->|returns| SourceSearchResult
```

**Key Classes:**

| Class | Purpose | Location |
|-------|---------|----------|
| `Actionbook` | Main SDK client with tool-decorated methods | [packages/js-sdk/src/client.ts:141-235]() |
| `ApiClient` | HTTP client with retry logic and timeout handling | [packages/js-sdk/src/api-client.ts:53-188]() |

**Sources:** [packages/js-sdk/src/client.ts:141-235](), [packages/js-sdk/src/api-client.ts:53-175]()

---

## Client Initialization

The `Actionbook` class accepts optional configuration for API authentication, base URL, timeouts, and custom fetch implementations.

```typescript
import { Actionbook } from '@actionbookdev/sdk'

// Default configuration (no API key required during open beta)
const actionbook = new Actionbook()

// With custom options
const actionbook = new Actionbook({
  apiKey: 'YOUR_API_KEY',              // Optional, falls back to ACTIONBOOK_API_KEY env var
  baseUrl: 'https://api.actionbook.dev', // Optional, default shown
  timeoutMs: 30000,                     // Optional, default: 30 seconds
  fetch: customFetchFn,                 // Optional, for proxy support
})
```

**Configuration Options:**

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `apiKey` | `string` | `process.env.ACTIONBOOK_API_KEY` | API key for authentication |
| `baseUrl` | `string` | `https://api.actionbook.dev` | Base URL for API requests |
| `timeoutMs` | `number` | `30000` | Request timeout in milliseconds |
| `fetch` | `FetchFunction` | `globalThis.fetch` | Custom fetch implementation |

**Environment Variables:**
- `ACTIONBOOK_API_KEY` - Automatically used if `apiKey` option is not provided

**Sources:** [packages/js-sdk/src/client.ts:95-118](), [packages/js-sdk/src/client.ts:156-165](), [packages/js-sdk/src/api-client.ts:17-38]()

---

## API Methods

The SDK provides four primary methods, each with overloaded signatures for flexibility and attached tool definitions for LLM integration.

```mermaid
graph LR
    subgraph "Actionbook Methods"
        searchActions["searchActions()"]
        getActionById["getActionById()"]
        listSources["listSources()"]
        searchSources["searchSources()"]
    end
    
    subgraph "Tool Metadata Attached"
        description[".description<br/>string"]
        params[".params<br/>{json, zod}"]
    end
    
    subgraph "API Endpoints"
        SearchAPI["/api/actions/search"]
        GetAPI["/api/actions"]
        ListAPI["/api/sources"]
        SearchSourcesAPI["/api/sources/search"]
    end
    
    searchActions --> description
    searchActions --> params
    searchActions --> SearchAPI
    
    getActionById --> description
    getActionById --> params
    getActionById --> GetAPI
    
    listSources --> description
    listSources --> params
    listSources --> ListAPI
    
    searchSources --> description
    searchSources --> params
    searchSources --> SearchSourcesAPI
```

**Sources:** [packages/js-sdk/src/client.ts:144-154](), [packages/js-sdk/src/tool-defs.ts:60-237]()

### searchActions()

Searches for action manuals using hybrid search (full-text + vector similarity).

**Signatures:**
```typescript
// Simple string query
searchActions(query: string): Promise<ChunkSearchResult>

// Full options object
searchActions(options: SearchActionsInput): Promise<ChunkSearchResult>
```

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `query` | `string` | Yes | - | Search keyword (e.g., "airbnb search", "login button") |
| `type` | `"vector" \| "fulltext" \| "hybrid"` | No | `"hybrid"` | Search algorithm type |
| `limit` | `number` | No | `5` | Max results (1-100) |
| `sourceIds` | `string` | No | - | Comma-separated source IDs to filter |
| `minScore` | `number` | No | - | Minimum similarity score (0-1) |

**Return Type:** `ChunkSearchResult` containing action IDs, content previews, and relevance scores.

**Example:**
```typescript
// Simple query
const results = await actionbook.searchActions('airbnb search')

// With options
const results = await actionbook.searchActions({
  query: 'login button',
  type: 'hybrid',
  limit: 10,
  sourceIds: '1,2',
  minScore: 0.7
})
```

**Sources:** [packages/js-sdk/src/client.ts:42-51](), [packages/js-sdk/src/client.ts:168-189](), [packages/js-sdk/src/tool-defs.ts:64-112]()

### getActionById()

Retrieves complete action details including DOM selectors and element metadata.

**Signatures:**
```typescript
// ID string
getActionById(id: string): Promise<ChunkActionDetail>

// Options object
getActionById(options: GetActionByIdInput): Promise<ChunkActionDetail>
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | `string` | Yes | Action ID (full URL or fuzzy domain match) |

**Action ID Formats:**
- Full URL: `https://example.com/docs/page`
- Domain + path: `example.com/docs/page`
- Domain only: `releases.rs`
- With chunk: `https://example.com/page#chunk-1`

**Return Type:** `ChunkActionDetail` containing full content, parsed elements, selectors, and document metadata.

**Example:**
```typescript
// Full URL
const action = await actionbook.getActionById('https://docs.airbnb.com/search')

// Fuzzy match
const action = await actionbook.getActionById('docs.airbnb.com/search')

// Access selectors
const elements = JSON.parse(action.elements || '{}')
const selector = elements['search-button']?.css_selector
```

**Sources:** [packages/js-sdk/src/client.ts:56-65](), [packages/js-sdk/src/client.ts:192-203](), [packages/js-sdk/src/tool-defs.ts:118-154]()

### listSources()

Lists all available sources (websites) in the Actionbook database.

**Signatures:**
```typescript
// Default limit (50)
listSources(): Promise<SourceListResult>

// Custom limit
listSources(options: ListSourcesInput): Promise<SourceListResult>
```

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `limit` | `number` | No | `50` | Max sources (1-200) |

**Return Type:** `SourceListResult` containing source IDs, names, URLs, descriptions, and tags.

**Example:**
```typescript
// List all sources
const sources = await actionbook.listSources()

// Limited list
const sources = await actionbook.listSources({ limit: 100 })

// Access source data
sources.results.forEach(source => {
  console.log(`${source.name} (${source.domain})`)
})
```

**Sources:** [packages/js-sdk/src/client.ts:70-79](), [packages/js-sdk/src/client.ts:206-215](), [packages/js-sdk/src/tool-defs.ts:160-186]()

### searchSources()

Searches sources by keyword across name, description, domain, URL, and tags.

**Signatures:**
```typescript
// Simple string query
searchSources(query: string): Promise<SourceSearchResult>

// Full options object
searchSources(options: SearchSourcesInput): Promise<SourceSearchResult>
```

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `query` | `string` | Yes | - | Search keyword |
| `limit` | `number` | No | `10` | Max results (1-100) |

**Return Type:** `SourceSearchResult` containing matching sources.

**Example:**
```typescript
// Simple query
const sources = await actionbook.searchSources('airbnb')

// With limit
const sources = await actionbook.searchSources({
  query: 'e-commerce',
  limit: 20
})
```

**Sources:** [packages/js-sdk/src/client.ts:84-93](), [packages/js-sdk/src/client.ts:218-233](), [packages/js-sdk/src/tool-defs.ts:192-237]()

---

## Tool Definition System

Each SDK method has attached `.description` and `.params` properties for seamless LLM tool integration. This design eliminates boilerplate when connecting Actionbook to AI frameworks.

```mermaid
graph TB
    subgraph "SDK Method Structure"
        Method["searchActions()"]
        Description[".description<br/>string"]
        Params[".params"]
        
        ParamsJSON[".params.json<br/>JSON Schema"]
        ParamsZod[".params.zod<br/>Zod Schema"]
        
        Method --> Description
        Method --> Params
        Params --> ParamsJSON
        Params --> ParamsZod
    end
    
    subgraph "LLM Framework Usage"
        OpenAISDK["OpenAI SDK<br/>uses .params.json"]
        AnthropicSDK["Anthropic SDK<br/>uses .params.json"]
        VercelAI["Vercel AI SDK<br/>uses .params.zod"]
        GeminiSDK["Gemini SDK<br/>uses .params.json"]
    end
    
    Description --> OpenAISDK
    Description --> AnthropicSDK
    Description --> VercelAI
    Description --> GeminiSDK
    
    ParamsJSON --> OpenAISDK
    ParamsJSON --> AnthropicSDK
    ParamsJSON --> GeminiSDK
    
    ParamsZod --> VercelAI
```

**Tool Metadata Structure:**

| Property | Type | Purpose |
|----------|------|---------|
| `.description` | `string` | Human-readable description for LLM |
| `.params.json` | `Record<string, unknown>` | JSON Schema for OpenAI, Anthropic, Gemini |
| `.params.zod` | `z.ZodTypeAny` | Zod schema for Vercel AI SDK |

**Example:**
```typescript
import { Actionbook } from '@actionbookdev/sdk'

const actionbook = new Actionbook()

// Access tool metadata
console.log(actionbook.searchActions.description)
// "Search for action manuals by keyword..."

console.log(actionbook.searchActions.params.json)
// { type: "object", properties: { query: {...}, ... }, required: ["query"] }

console.log(actionbook.searchActions.params.zod)
// ZodObject { ... }
```

**Implementation Details:**

The tool definition system is implemented through:
1. `ToolParams<T>` interface providing dual schema formats [packages/js-sdk/src/tool-defs.ts:8-13]()
2. `createParams()` function generating both JSON Schema and Zod schemas [packages/js-sdk/src/tool-defs.ts:41-46]()
3. Method decoration in `Actionbook` constructor [packages/js-sdk/src/client.ts:186-189]()

**Sources:** [packages/js-sdk/src/tool-defs.ts:1-46](), [packages/js-sdk/src/client.ts:28-37](), [packages/js-sdk/src/client.ts:186-189]()

---

## LLM Framework Integration

The SDK integrates with all major LLM frameworks through its tool definition system. Examples below demonstrate integration patterns.

### Vercel AI SDK

Uses Zod schemas via `.params.zod`:

```typescript
import { Actionbook } from '@actionbookdev/sdk'
import { generateText, tool } from 'ai'
import { openai } from '@ai-sdk/openai'

const actionbook = new Actionbook()

const { text } = await generateText({
  model: openai('gpt-4o'),
  tools: {
    searchActions: tool({
      description: actionbook.searchActions.description,
      parameters: actionbook.searchActions.params.zod,
      execute: async ({ query }) => actionbook.searchActions(query),
    }),
    getActionById: tool({
      description: actionbook.getActionById.description,
      parameters: actionbook.getActionById.params.zod,
      execute: async ({ id }) => actionbook.getActionById(id),
    }),
  },
  maxSteps: 5,
  prompt: 'Search for LinkedIn message actions',
})
```

**Sources:** [README.md:496-520]()

### OpenAI SDK

Uses JSON Schema via `.params.json`:

```typescript
import { Actionbook } from '@actionbookdev/sdk'
import OpenAI from 'openai'

const actionbook = new Actionbook()
const openai = new OpenAI()

const tools: OpenAI.ChatCompletionTool[] = [
  {
    type: 'function',
    function: {
      name: 'searchActions',
      description: actionbook.searchActions.description,
      parameters: actionbook.searchActions.params.json,
    },
  },
  {
    type: 'function',
    function: {
      name: 'getActionById',
      description: actionbook.getActionById.description,
      parameters: actionbook.getActionById.params.json,
    },
  },
]

const completion = await openai.chat.completions.create({
  model: 'gpt-4o',
  tools,
  messages: [{ role: 'user', content: 'Search for Google login actions' }],
})
```

**Sources:** [README.md:525-558]()

### Anthropic Claude SDK

Uses JSON Schema via `.params.json` as `input_schema`:

```typescript
import { Actionbook } from '@actionbookdev/sdk'
import Anthropic from '@anthropic-ai/sdk'

const actionbook = new Actionbook()
const anthropic = new Anthropic()

const tools: Anthropic.Tool[] = [
  {
    name: 'searchActions',
    description: actionbook.searchActions.description,
    input_schema: actionbook.searchActions.params.json,
  },
  {
    name: 'getActionById',
    description: actionbook.getActionById.description,
    input_schema: actionbook.getActionById.params.json,
  },
]

const message = await anthropic.messages.create({
  model: 'claude-sonnet-4-20250514',
  max_tokens: 1024,
  tools,
  messages: [{ role: 'user', content: 'Search for Twitter post actions' }],
})
```

**Sources:** [README.md:563-591]()

### Google Gemini SDK

Uses JSON Schema via `.params.json` as `parameters`:

```typescript
import { Actionbook } from '@actionbookdev/sdk'
import { GoogleGenAI } from '@google/genai'

const actionbook = new Actionbook()
const genai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY })

const tools = [
  {
    functionDeclarations: [
      {
        name: 'searchActions',
        description: actionbook.searchActions.description,
        parameters: actionbook.searchActions.params.json,
      },
      {
        name: 'getActionById',
        description: actionbook.getActionById.description,
        parameters: actionbook.getActionById.params.json,
      },
    ],
  },
]

const response = await genai.models.generateContent({
  model: 'gemini-2.0-flash',
  contents: [{ role: 'user', parts: [{ text: 'Search for YouTube upload actions' }] }],
  config: { tools },
})
```

**Sources:** [README.md:596-627]()

---

## Type System

The SDK exports comprehensive TypeScript types for all request/response structures.

### Core Types

```mermaid
graph TB
    subgraph "Search Types"
        SearchType["SearchType<br/>'vector' | 'fulltext' | 'hybrid'"]
        ChunkSearchResult["ChunkSearchResult"]
        SearchActionsParams["SearchActionsParams"]
    end
    
    subgraph "Action Detail Types"
        ChunkActionDetail["ChunkActionDetail"]
        ParsedElements["ParsedElements"]
    end
    
    subgraph "Source Types"
        SourceItem["SourceItem"]
        SourceListResult["SourceListResult"]
        SourceSearchResult["SourceSearchResult"]
    end
    
    SearchActionsParams --> SearchType
    SearchActionsParams --> ChunkSearchResult
    
    ChunkActionDetail --> ParsedElements
    
    SourceListResult --> SourceItem
    SourceSearchResult --> SourceItem
```

**Key Type Definitions:**

| Type | Description | Location |
|------|-------------|----------|
| `SearchType` | Search algorithm: `"vector"`, `"fulltext"`, `"hybrid"` | [packages/js-sdk/src/types.ts:4]() |
| `ChunkSearchResult` | Search results with action IDs and scores | [packages/js-sdk/src/types.ts:9-21]() |
| `ChunkActionDetail` | Full action details with selectors | [packages/js-sdk/src/types.ts:26-37]() |
| `ParsedElements` | Structured element selector data | [packages/js-sdk/src/types.ts:42-51]() |
| `SourceItem` | Source metadata (name, URL, tags) | [packages/js-sdk/src/types.ts:56-66]() |
| `SourceListResult` | List of sources | [packages/js-sdk/src/types.ts:71-75]() |
| `SourceSearchResult` | Source search results | [packages/js-sdk/src/types.ts:80-85]() |

### ChunkSearchResult Structure

```typescript
interface ChunkSearchResult {
  success: boolean;
  query: string;
  results: Array<{
    action_id: string;    // URL-based action identifier
    content: string;      // Content preview
    score: number;        // Relevance score (0-1)
    createdAt: string;    // ISO timestamp
  }>;
  count: number;          // Number of results returned
  total: number;          // Total matching results
  hasMore: boolean;       // Whether more results exist
}
```

**Sources:** [packages/js-sdk/src/types.ts:9-21]()

### ChunkActionDetail Structure

```typescript
interface ChunkActionDetail {
  action_id: string;      // Unique action identifier
  content: string;        // Full action content
  elements: string | null; // JSON string of element selectors
  createdAt: string;      // ISO timestamp
  documentId: number;     // Parent document ID
  documentTitle: string;  // Document title
  documentUrl: string;    // Document URL
  chunkIndex: number;     // Chunk position in document
  heading: string | null; // Section heading
  tokenCount: number;     // Content token count
}
```

**Parsing Elements:**
```typescript
const action = await actionbook.getActionById('example.com/page')
const elements: ParsedElements = JSON.parse(action.elements || '{}')

// Access specific element
const searchButton = elements['search-button']
const selector = searchButton?.css_selector || searchButton?.xpath_selector
```

**Sources:** [packages/js-sdk/src/types.ts:26-37](), [packages/js-sdk/src/types.ts:42-51]()

### ParsedElements Structure

```typescript
interface ParsedElements {
  [key: string]: {
    css_selector?: string;     // CSS selector
    xpath_selector?: string;   // XPath selector
    description?: string;      // Element description
    element_type?: string;     // Type (button, input, link, etc.)
    allow_methods?: string[];  // Allowed actions (click, type, extract)
    depends_on?: string;       // Parent element key
  };
}
```

**Sources:** [packages/js-sdk/src/types.ts:42-51]()

---

## Error Handling

The SDK implements comprehensive error handling with retry logic and custom error types.

```mermaid
graph TB
    subgraph "Error Flow"
        Request["API Request"]
        Timeout["Timeout Check<br/>30s default"]
        HTTPError["HTTP Error<br/>Response"]
        Retry["Retry Logic<br/>Max 3 attempts"]
        ErrorCode["ActionbookError<br/>with ErrorCode"]
    end
    
    subgraph "Error Types"
        NOT_FOUND["NOT_FOUND<br/>404"]
        RATE_LIMITED["RATE_LIMITED<br/>429"]
        TIMEOUT["TIMEOUT<br/>AbortError"]
        API_ERROR["API_ERROR<br/>Other failures"]
        INTERNAL_ERROR["INTERNAL_ERROR<br/>Fatal"]
    end
    
    Request --> Timeout
    Request --> HTTPError
    
    Timeout -.->|abort| Retry
    HTTPError --> ErrorCode
    
    ErrorCode --> NOT_FOUND
    ErrorCode --> RATE_LIMITED
    ErrorCode --> TIMEOUT
    ErrorCode --> API_ERROR
    ErrorCode --> INTERNAL_ERROR
    
    Retry --> Request
```

### Error Types

The SDK throws `ActionbookError` instances with specific error codes:

| Error Code | HTTP Status | Description | Retryable |
|------------|-------------|-------------|-----------|
| `NOT_FOUND` | 404 | Action or resource not found | No |
| `RATE_LIMITED` | 429 | Rate limit exceeded | No |
| `TIMEOUT` | - | Request timeout or abort | Yes |
| `API_ERROR` | Other | General API failure | No |
| `INTERNAL_ERROR` | - | Internal SDK error | No |

**Error Handling Example:**
```typescript
import { Actionbook, ActionbookError, ErrorCodes } from '@actionbookdev/sdk'

const actionbook = new Actionbook()

try {
  const results = await actionbook.searchActions('query')
} catch (error) {
  if (error instanceof ActionbookError) {
    switch (error.code) {
      case ErrorCodes.NOT_FOUND:
        console.error('Resource not found')
        break
      case ErrorCodes.RATE_LIMITED:
        console.error('Rate limit exceeded')
        break
      case ErrorCodes.TIMEOUT:
        console.error('Request timed out')
        break
      default:
        console.error('API error:', error.message)
    }
  } else {
    console.error('Unknown error:', error)
  }
}
```

**Sources:** [packages/js-sdk/src/api-client.ts:131-174]()

### Retry Logic

The `ApiClient` implements automatic retry for transient failures:

**Retry Configuration:**
- **Max retries:** 3 (default)
- **Retry delay:** 1000ms (default)
- **Retryable errors:** Timeout/abort errors only

**Configuration:**
```typescript
const actionbook = new Actionbook({
  timeoutMs: 60000, // 60 second timeout
})
```

The retry configuration is hardcoded in `ApiClient` [packages/js-sdk/src/api-client.ts:64-67]() but can be extended in future versions.

**Sources:** [packages/js-sdk/src/api-client.ts:48-67](), [packages/js-sdk/src/api-client.ts:111-174]()

---

## Custom Fetch Implementation

The SDK supports custom fetch implementations for proxy support, custom headers, or alternative HTTP clients.

**Example with Proxy (undici):**
```typescript
import { Actionbook } from '@actionbookdev/sdk'
import { fetch as undiciFetch, ProxyAgent } from 'undici'

const proxyAgent = new ProxyAgent('http://proxy:8080')

const actionbook = new Actionbook({
  apiKey: 'YOUR_API_KEY',
  fetch: (url, init) => undiciFetch(url, { 
    ...init, 
    dispatcher: proxyAgent 
  }),
})

const results = await actionbook.searchActions('query')
```

**Example with Custom Headers:**
```typescript
import { Actionbook } from '@actionbookdev/sdk'

const actionbook = new Actionbook({
  fetch: (url, init) => fetch(url, {
    ...init,
    headers: {
      ...init?.headers,
      'X-Custom-Header': 'value',
    },
  }),
})
```

**Sources:** [packages/js-sdk/src/api-client.ts:22-37](), [packages/js-sdk/src/client.ts:102-117]()

---

## Complete Integration Example

This example demonstrates a full integration with Vercel AI SDK, including search, retrieval, and selector usage:

```typescript
import { Actionbook } from '@actionbookdev/sdk'
import { generateText, tool } from 'ai'
import { openai } from '@ai-sdk/openai'

const actionbook = new Actionbook({
  apiKey: process.env.ACTIONBOOK_API_KEY,
})

const { text, toolCalls, toolResults } = await generateText({
  model: openai('gpt-4o'),
  tools: {
    searchActions: tool({
      description: actionbook.searchActions.description,
      parameters: actionbook.searchActions.params.zod,
      execute: async ({ query, limit }) => {
        const results = await actionbook.searchActions({ query, limit })
        return JSON.stringify(results, null, 2)
      },
    }),
    getActionById: tool({
      description: actionbook.getActionById.description,
      parameters: actionbook.getActionById.params.zod,
      execute: async ({ id }) => {
        const action = await actionbook.getActionById(id)
        return JSON.stringify(action, null, 2)
      },
    }),
    listSources: tool({
      description: actionbook.listSources.description,
      parameters: actionbook.listSources.params.zod,
      execute: async ({ limit }) => {
        const sources = await actionbook.listSources({ limit })
        return JSON.stringify(sources, null, 2)
      },
    }),
    searchSources: tool({
      description: actionbook.searchSources.description,
      parameters: actionbook.searchSources.params.zod,
      execute: async ({ query, limit }) => {
        const sources = await actionbook.searchSources({ query, limit })
        return JSON.stringify(sources, null, 2)
      },
    }),
  },
  maxSteps: 10,
  prompt: `
    Find the Airbnb search functionality:
    1. Search for sources containing 'airbnb'
    2. Search for 'search' actions in that source
    3. Get full action details including selectors
  `,
})

console.log('Agent response:', text)
console.log('Tool calls made:', toolCalls.length)
```

**Sources:** [README.md:496-520](), [README.md:450-470]()

---

# Page: Skills and Plugins

# Skills and Plugins

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.claude-plugin/marketplace.json](.claude-plugin/marketplace.json)
- [.claude-plugin/plugin.json](.claude-plugin/plugin.json)
- [commands/manual.md](commands/manual.md)
- [skills/actionbook/SKILL.md](skills/actionbook/SKILL.md)

</details>



This page documents Actionbook's extensible plugin system that enables AI agents and IDEs to discover and use specialized capabilities. Plugins bundle **skills** (contextual activation patterns), **commands** (slash commands), and **MCP tools** (structured function calls) into distributable packages.

For information about using the MCP Server interface, see [MCP Server](#2.2). For details on the SDK's tool definitions, see [JavaScript SDK](#2.3).

---

## Plugin Architecture

Actionbook plugins follow a standardized directory structure defined by a `plugin.json` manifest. This manifest declares the plugin's metadata and points to its capabilities: skills, commands, and MCP server configurations.

### Plugin Manifest Structure

The plugin manifest defines the core plugin metadata and paths to capability directories:

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Unique plugin identifier |
| `description` | string | Brief description of plugin capabilities |
| `author` | object | Author metadata with `name` field |
| `skills` | string | Relative path to skills directory (optional) |
| `commands` | string | Relative path to commands directory (optional) |
| `mcpServers` | string | Relative path to MCP servers config (optional) |

**Example Plugin Manifest:**

```json
{
  "name": "actionbook",
  "description": "Actionbook MCP server for up-to-date browser automation",
  "author": { "name": "Actionbook" },
  "skills": "./skills/",
  "commands": "./commands/",
  "mcpServers": "./mcp-servers.json"
}
```

Sources: [.claude-plugin/plugin.json:1-10]()

### Plugin Component Diagram

```mermaid
graph TB
    subgraph Plugin["Plugin Package"]
        Manifest["plugin.json<br/>Metadata + Paths"]
        
        subgraph Skills["Skills Directory"]
            Skill1["skill1/SKILL.md<br/>Activation patterns"]
            Skill2["skill2/SKILL.md<br/>Context description"]
        end
        
        subgraph Commands["Commands Directory"]
            Cmd1["command1.md<br/>Slash command"]
            Cmd2["command2.md<br/>CLI wrapper"]
        end
        
        MCPConfig["mcp-servers.json<br/>MCP tool mappings"]
    end
    
    subgraph Runtime["Runtime Environment"]
        AIAgent["AI Agent<br/>Claude, GPT-4, etc."]
        IDE["IDE Integration<br/>Cursor, VS Code"]
        MCPClient["MCP Client<br/>Tool executor"]
    end
    
    Manifest --> Skills
    Manifest --> Commands
    Manifest --> MCPConfig
    
    Skills --> AIAgent
    Commands --> IDE
    MCPConfig --> MCPClient
    
    AIAgent -.->|"Activates based on<br/>skill description"| Skills
    IDE -.->|"Exposes as<br/>slash commands"| Commands
    MCPClient -.->|"Calls structured<br/>functions"| MCPConfig
```

Sources: [.claude-plugin/plugin.json:1-10]()

---

## Skills

Skills are markdown-based capability declarations that help AI agents understand **when** and **how** to use a plugin. Each skill includes activation patterns and usage guidance in natural language.

### Skill Definition Format

Skills are defined in markdown files named `SKILL.md` within the skills directory. The file structure consists of:

1. **YAML Frontmatter**: Metadata including `name` and `description`
2. **Markdown Body**: Detailed usage instructions, examples, and guidelines

**Frontmatter Fields:**

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Skill identifier (must match directory name) |
| `description` | Yes | Activation pattern describing when the skill should be used |

The `description` field is critical—it defines the semantic trigger conditions that cause an AI agent to activate this skill.

### Actionbook Core Skill

The primary Actionbook skill activates when users need browser automation capabilities:

```yaml
---
name: actionbook
description: This skill should be used when the user needs to automate multi-step website tasks. Activates for browser automation, web scraping, UI testing, or building AI agents. Provides complete action manuals with step-by-step instructions and verified selectors.
---
```

**Activation Triggers:**
- Multi-step website tasks ("Send a LinkedIn message")
- Website interaction queries ("How do I post a tweet?")
- Browser-based AI agent development
- E2E test writing for external websites

**What It Provides:**
1. Step-by-step instructions
2. Verified selectors (CSS/XPath)
3. Element metadata (type, allowed methods)

Sources: [skills/actionbook/SKILL.md:1-24]()

### Skill Usage Patterns

Skills guide agents through a standard workflow:

```mermaid
graph LR
    Trigger["User Request<br/>Multi-step task"]
    Activate["Skill Activates<br/>Pattern match"]
    Search["Step 1: Search<br/>actionbook search"]
    Retrieve["Step 2: Retrieve<br/>actionbook get"]
    Execute["Step 3: Execute<br/>actionbook browser<br/>or Playwright/Puppeteer"]
    
    Trigger --> Activate
    Activate --> Search
    Search --> Retrieve
    Retrieve --> Execute
    
    Search -.->|"Alternative"| MCPSearch["search_actions MCP"]
    Retrieve -.->|"Alternative"| MCPGet["get_action_by_id MCP"]
```

Sources: [skills/actionbook/SKILL.md:26-106]()

### Skill Guidelines

Skills provide best practices for agents:

- **Search by task**: Describe goals, not just elements (`"linkedin send message"` not `"linkedin message button"`)
- **Follow order**: Execute steps sequentially as provided
- **Trust selectors**: Actionbook selectors are verified and maintained

Sources: [skills/actionbook/SKILL.md:108-112]()

---

## Commands

Commands are slash-command interfaces that expose plugin functionality to IDEs and chat interfaces. Each command is defined by a markdown file with YAML frontmatter.

### Command Definition Format

Commands follow this structure:

**Frontmatter Fields:**

| Field | Required | Description |
|-------|----------|-------------|
| `description` | Yes | Brief command summary |
| `argument-hint` | No | Placeholder text for required arguments |

**Example Command Definition:**

```yaml
---
description: Get action manual for a website task
argument-hint: <task>
---

# /actionbook:manual

Fetches up-to-date action manuals with step-by-step instructions 
and verified selectors.

## Usage
/actionbook:manual <task>

## Examples
/actionbook:manual linkedin send message
/actionbook:manual airbnb book listing
```

Sources: [commands/manual.md:1-26]()

### Command Execution Flow

```mermaid
graph TB
    User["User Types Command<br/>/actionbook:manual linkedin send message"]
    Parse["IDE Parses Command<br/>Extract: task = 'linkedin send message'"]
    
    subgraph Execution["Command Execution"]
        SearchAPI["Call search_actions<br/>query: 'linkedin send message'"]
        Results["Parse Results<br/>Select best match"]
        GetAPI["Call get_action_by_id<br/>actionId: 'site/...'"]
        Format["Format Manual<br/>Steps + Selectors"]
    end
    
    Display["Display in IDE<br/>Formatted manual"]
    
    User --> Parse
    Parse --> SearchAPI
    SearchAPI --> Results
    Results --> GetAPI
    GetAPI --> Format
    Format --> Display
```

Sources: [commands/manual.md:28-36]()

---

## Plugin Marketplace

The marketplace configuration (`marketplace.json`) defines a registry of available plugins with metadata for discovery and installation.

### Marketplace Structure

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Marketplace identifier |
| `owner` | object | Marketplace owner metadata |
| `plugins` | array | List of available plugins |

**Plugin Entry Fields:**

| Field | Description |
|-------|-------------|
| `name` | Plugin identifier |
| `source` | Relative or absolute path to plugin directory |
| `description` | Plugin capabilities summary |
| `version` | Semantic version string |

Sources: [.claude-plugin/marketplace.json:1-7]()

### Available Plugins

The Actionbook marketplace includes four plugins:

#### 1. Actionbook (Core)

**Source:** `./`  
**Version:** 0.2.0  
**Purpose:** Core Actionbook functionality for browser automation with verified selectors.

#### 2. Rust Learner

**Source:** `./playground/rust-learner`  
**Version:** 0.1.0  
**Purpose:** Educational plugin demonstrating how to learn Rust language features and crate updates using Actionbook + agent-browser.

#### 3. ArXiv Viewer

**Source:** `./playground/arxiv-viewer`  
**Version:** 0.1.0  
**Purpose:** Academic paper research tool supporting:
- API queries for paper metadata
- Web scraping via Actionbook for paper discovery
- HTML paper reading via ar5iv

#### 4. Actionbook Scraper

**Source:** `./playground/actionbook-scraper`  
**Version:** 0.1.0  
**Purpose:** Web scraper code generation using verified selectors. Achieves 7.76x better data extraction accuracy compared to AI-guessed selectors.

Sources: [.claude-plugin/marketplace.json:6-31]()

### Plugin Distribution Diagram

```mermaid
graph TB
    subgraph Marketplace["Marketplace Registry<br/>marketplace.json"]
        CorePlugin["actionbook<br/>v0.2.0<br/>./"]
        RustPlugin["rust-learner<br/>v0.1.0<br/>./playground/rust-learner"]
        ArxivPlugin["arxiv-viewer<br/>v0.1.0<br/>./playground/arxiv-viewer"]
        ScraperPlugin["actionbook-scraper<br/>v0.1.0<br/>./playground/actionbook-scraper"]
    end
    
    subgraph CoreComponents["Core Plugin Components"]
        CoreSkills["skills/actionbook/<br/>SKILL.md"]
        CoreCommands["commands/<br/>manual.md"]
        CoreMCP["mcp-servers.json"]
    end
    
    subgraph PlaygroundComponents["Playground Plugin Components"]
        RustSkills["rust-learner skills"]
        ArxivSkills["arxiv-viewer skills"]
        ScraperSkills["scraper skills"]
    end
    
    CorePlugin --> CoreSkills
    CorePlugin --> CoreCommands
    CorePlugin --> CoreMCP
    
    RustPlugin --> RustSkills
    ArxivPlugin --> ArxivSkills
    ScraperPlugin --> ScraperSkills
    
    Marketplace --> CorePlugin
    Marketplace --> RustPlugin
    Marketplace --> ArxivPlugin
    Marketplace --> ScraperPlugin
```

Sources: [.claude-plugin/marketplace.json:1-32]()

---

## Integration Points

### Skills ↔ Commands ↔ MCP Tools

Plugins integrate three capability types that serve different consumption patterns:

| Capability | Consumer | Interface | Discovery Mechanism |
|------------|----------|-----------|---------------------|
| **Skills** | AI Agents | Natural language activation | Semantic pattern matching on `description` field |
| **Commands** | IDEs | Slash commands (`/plugin:command`) | Command palette registration |
| **MCP Tools** | MCP Clients | Structured function calls | Tool schema registration |

```mermaid
graph TB
    subgraph "Plugin Package"
        PluginJSON["plugin.json"]
        Skills["Skills<br/>Activation patterns"]
        Commands["Commands<br/>Slash syntax"]
        MCPTools["MCP Tools<br/>Function schemas"]
    end
    
    subgraph "Consumers"
        AIAgent["AI Agent<br/>Claude, GPT-4"]
        IDE["IDE<br/>Cursor, VS Code"]
        MCPClient["MCP Client<br/>Tool executor"]
    end
    
    subgraph "Underlying API"
        SearchAPI["searchActions()<br/>API endpoint"]
        GetAPI["getActionById()<br/>API endpoint"]
    end
    
    PluginJSON --> Skills
    PluginJSON --> Commands
    PluginJSON --> MCPTools
    
    Skills -->|"Natural language<br/>activation"| AIAgent
    Commands -->|"Slash command<br/>registration"| IDE
    MCPTools -->|"Function call<br/>schemas"| MCPClient
    
    AIAgent --> SearchAPI
    IDE --> SearchAPI
    MCPClient --> SearchAPI
    
    AIAgent --> GetAPI
    IDE --> GetAPI
    MCPClient --> GetAPI
```

Sources: [.claude-plugin/plugin.json:1-10](), [skills/actionbook/SKILL.md:26-73](), [commands/manual.md:1-36]()

---

## Implementation References

### File Paths for Plugin System

| Component | Path |
|-----------|------|
| Core plugin manifest | `.claude-plugin/plugin.json` |
| Marketplace registry | `.claude-plugin/marketplace.json` |
| Actionbook skill | `skills/actionbook/SKILL.md` |
| Manual command | `commands/manual.md` |
| MCP server config | `.claude-plugin/mcp-servers.json` (referenced) |

### Related Documentation

- For MCP server setup and tool definitions, see [MCP Server](#2.2)
- For SDK tool schemas (`ToolDefinition`), see [Tool Definitions](#7.3)
- For CLI command reference, see [CLI](#2.1)
- For browser automation commands exposed by plugins, see [Browser Automation Commands](#2.1.1)

Sources: [.claude-plugin/plugin.json:1-10](), [.claude-plugin/marketplace.json:1-32](), [skills/actionbook/SKILL.md:1-112](), [commands/manual.md:1-36]()

---

# Page: Core Services

# Core Services

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitignore](.gitignore)
- [README.md](README.md)
- [mcp-servers.json](mcp-servers.json)
- [package.json](package.json)
- [pnpm-lock.yaml](pnpm-lock.yaml)
- [pnpm-workspace.yaml](pnpm-workspace.yaml)
- [services/action-builder/.nvmrc](services/action-builder/.nvmrc)
- [turbo.json](turbo.json)

</details>



This page provides an overview of the four backend services that power Actionbook's automation and documentation capabilities. These services work together to discover website structures, record UI interactions, generate action manuals, and serve them through a REST API.

For information about the user-facing interfaces that consume these services, see [User Interfaces](#2). For detailed database schema and storage architecture, see [Data Layer](#5).

## Purpose and Scope

The Core Services layer consists of:

1. **API Service** - REST API for searching and retrieving action manuals
2. **Action Builder** - Browser automation service that discovers and records UI elements
3. **Playbook Builder** - Documentation generation service that crawls and catalogs pages
4. **Knowledge Builder** - Content extraction service that generates embeddings for semantic search

Each service operates independently but shares common infrastructure through the database and browser automation layers. This page covers the architecture and responsibilities of each service. Child pages provide detailed implementation information for specific services.

## Service Architecture

The following diagram shows how the four core services relate to each other and their primary responsibilities:

```mermaid
graph TB
    subgraph "Core Services"
        APIService["API Service<br/>apps/api-service<br/>REST endpoints"]
        ActionBuilder["Action Builder<br/>services/action-builder<br/>Element recording"]
        PlaybookBuilder["Playbook Builder<br/>services/playbook-builder<br/>Page discovery"]
        KnowledgeBuilder["Knowledge Builder<br/>services/knowledge-builder<br/>Content extraction"]
    end
    
    subgraph "Shared Infrastructure"
        DB[("PostgreSQL Database<br/>services/db<br/>sources, pages, elements,<br/>chunks, build_tasks")]
        BrowserLayer["Browser Automation<br/>services/common/browser<br/>StagehandBrowser,<br/>AgentCoreBrowser"]
    end
    
    subgraph "External Consumers"
        CLI["CLI<br/>@actionbookdev/cli"]
        MCP["MCP Server<br/>@actionbookdev/mcp"]
        SDK["JavaScript SDK<br/>@actionbookdev/sdk"]
    end
    
    CLI --> APIService
    MCP --> APIService
    SDK --> APIService
    
    APIService --> DB
    
    ActionBuilder --> DB
    ActionBuilder --> BrowserLayer
    
    PlaybookBuilder --> DB
    PlaybookBuilder --> BrowserLayer
    
    KnowledgeBuilder --> DB
    
    PlaybookBuilder -.->|"Triggers after completion"| ActionBuilder
```

**Sources:** README.md, architecture diagrams from system overview

## Service Responsibilities

| Service | Primary Function | Key Outputs | Dependencies |
|---------|-----------------|-------------|--------------|
| **API Service** | Query and retrieval | JSON responses via REST | `services/db` |
| **Action Builder** | UI element discovery | `elements` table records, YAML files | `services/db`, `services/common/browser` |
| **Playbook Builder** | Page structure documentation | `pages` table records, `documents` table | `services/db`, `services/common/browser` |
| **Knowledge Builder** | Content indexing | `chunks` table with embeddings | `services/db` |

**Sources:** Architecture diagrams, services directory structure

## API Service

The API Service provides a REST API for searching and retrieving action manuals. It is the primary interface between user-facing applications (CLI, MCP, SDK) and Actionbook's data layer.

**Location:** `apps/api-service` (not included in provided files)

**Key Endpoints:**
- `GET /actions/search` - Hybrid search combining full-text and vector similarity
- `GET /actions/:id` - Retrieve detailed action manual by ID
- `GET /sources` - List available websites
- `GET /sources/:id` - Get source details

The service implements hybrid search by combining PostgreSQL full-text search (GIN indexes on `chunks.content`) with vector similarity search (HNSW indexes on `chunks.embedding`).

For detailed API documentation including request/response formats and authentication, see [API Service](#3.1).

**Sources:** Architecture diagrams, README.md

## Action Builder Service

The Action Builder is responsible for discovering and recording UI elements on websites through browser automation. It orchestrates a multi-stage pipeline that generates recording tasks, executes them using AI-powered browser tools, and optimizes selectors for stability.

**Location:** `services/action-builder`

### Architecture Components

```mermaid
graph TB
    subgraph "Task Orchestration"
        Coordinator["Coordinator<br/>Claims build_tasks<br/>Spawns runners"]
        BTR["BuildTaskRunner<br/>Per-build orchestration<br/>Generates recording_tasks"]
        QW["RecordingTaskQueueWorker<br/>Global consumer<br/>Executes recordings"]
    end
    
    subgraph "Recording Execution"
        ActionRecorder["ActionRecorder<br/>Multi-turn LLM loop<br/>Element discovery"]
        ToolExecutor["RecorderToolExecutor<br/>Tool dispatcher<br/>navigate, observe,<br/>interact, register"]
        SelectorOptimizer["SelectorOptimizer<br/>LLM-based stability<br/>analysis"]
    end
    
    subgraph "Data Persistence"
        ElementsTable[("elements table<br/>UI components +<br/>verified selectors")]
        YAMLOutput["YAML files<br/>output/sites/"]
    end
    
    Coordinator --> BTR
    BTR --> QW
    QW --> ActionRecorder
    ActionRecorder --> ToolExecutor
    ToolExecutor --> SelectorOptimizer
    SelectorOptimizer --> ElementsTable
    SelectorOptimizer --> YAMLOutput
```

**Sources:** services/action-builder directory structure, Diagram 3 from system overview

### Key Classes and Files

| Component | Purpose | Key Methods |
|-----------|---------|-------------|
| `Coordinator` | Claims completed knowledge builds and spawns `BuildTaskRunner` instances | `claimTask()`, `spawnRunner()` |
| `BuildTaskRunner` | Generates recording tasks for a single build | `generateRecordingTasks()`, `pollTaskStatus()` |
| `RecordingTaskQueueWorker` | Global worker that executes recording tasks from queue | `claimTask()`, `executeTask()` |
| `ActionRecorder` | Orchestrates multi-turn LLM conversation for element discovery | `record()`, `executeToolLoop()` |
| `RecorderToolExecutor` | Dispatches tool calls to browser adapter | `executeTool()`, `navigate()`, `observe()`, `register()` |
| `SelectorOptimizer` | Uses LLM to analyze and filter unstable selectors | `optimizeSelectors()`, `detectUnstablePatterns()` |

The action-builder service processes builds in stages:
1. **Claim stage**: `Coordinator` claims `build_tasks` where `stage='knowledge_build'` and `stage_status='completed'`
2. **Generation stage**: `BuildTaskRunner` analyzes pages and creates 50-100+ `recording_tasks`
3. **Execution stage**: `RecordingTaskQueueWorker` claims tasks and uses `ActionRecorder` to discover elements
4. **Optimization stage**: `SelectorOptimizer` filters unstable selectors before persistence

For detailed information on the task pipeline, see [Task Execution Pipeline](#3.2.1). For recording mechanics, see [Action Recording](#3.2.2). For tool reference, see [Recording Tools Reference](#3.2.3).

**Sources:** Architecture diagrams, services/action-builder/.nvmrc indicates Node.js service

## Playbook Builder Service

The Playbook Builder discovers and documents the structure of websites, creating a foundation for subsequent action recording. It navigates through sites, identifies page types, and generates descriptive documentation.

**Location:** `services/playbook-builder`

### Core Functionality

The Playbook Builder operates independently from Action Builder but prepares the groundwork by:

1. **Page Discovery** - Crawls websites to identify distinct page types
2. **Structure Analysis** - Identifies navigation patterns and page relationships
3. **Documentation Generation** - Creates human-readable page descriptions
4. **Database Population** - Stores results in `pages` and `documents` tables

### Key Classes

| Component | Purpose |
|-----------|---------|
| `PlaybookTaskController` | Manages playbook generation lifecycle: polling, claiming, execution |
| Page discovery logic | Identifies unique page types through navigation patterns |
| Documentation generator | Creates structured descriptions of page capabilities |

The Playbook Builder uses the same browser automation layer as Action Builder (`services/common/browser`) but focuses on higher-level page structure rather than individual UI elements.

Upon completion, the Playbook Builder updates the `build_task` record to `stage='knowledge_build'` and `stage_status='completed'`, which triggers the Action Builder's `Coordinator` to begin element recording.

For detailed information on playbook task management, see [Playbook Task Controller](#3.3.1).

**Sources:** Architecture diagrams, services/playbook-builder directory structure

## Knowledge Builder Service

The Knowledge Builder extracts and indexes content from web pages for semantic search capabilities. It operates on crawled pages to generate embeddings that enable vector similarity search.

**Location:** `services/knowledge-builder`

### Core Functionality

1. **Content Extraction** - Parses HTML to extract meaningful text using readability algorithms
2. **Chunking** - Splits content into semantically coherent segments
3. **Embedding Generation** - Creates vector embeddings using OpenAI or compatible embedding models
4. **Index Population** - Stores chunks with embeddings in the `chunks` table

### Database Integration

The Knowledge Builder populates the following tables:

| Table | Records | Purpose |
|-------|---------|---------|
| `documents` | One per crawled page | Stores full page content and metadata |
| `chunks` | Multiple per document | Content segments with embeddings for search |

The `chunks` table includes:
- `content` (text) - Full-text indexed with GIN
- `embedding` (vector) - HNSW indexed for similarity search
- `document_id` (FK) - Links to source document
- `source_version_id` (FK) - Links to specific version

This enables the API Service to perform hybrid search combining keyword matching and semantic similarity.

**Sources:** Architecture diagrams, services/knowledge-builder directory structure

## Service Communication Flow

The following diagram shows how services interact during a typical build process:

```mermaid
sequenceDiagram
    participant User
    participant KnowledgeBuilder as "Knowledge Builder"
    participant DB as "Database<br/>(build_tasks table)"
    participant Coordinator as "Coordinator<br/>(Action Builder)"
    participant BTR as "BuildTaskRunner"
    participant QW as "QueueWorker"
    participant APIService as "API Service"
    
    User->>KnowledgeBuilder: Initialize build for website
    KnowledgeBuilder->>DB: Create build_task<br/>stage='init'
    KnowledgeBuilder->>DB: Crawl & extract content
    KnowledgeBuilder->>DB: Update to stage='knowledge_build'<br/>stage_status='completed'
    
    Coordinator->>DB: Poll for completed knowledge builds
    DB-->>Coordinator: Return build_task
    Coordinator->>BTR: Spawn BuildTaskRunner
    BTR->>DB: Generate recording_tasks (50-100+)
    BTR->>DB: Update build_task to stage='action_build'
    
    QW->>DB: Poll for pending recording_tasks
    DB-->>QW: Return recording_task
    QW->>QW: Execute ActionRecorder
    QW->>DB: Save elements + selectors
    QW->>DB: Update recording_task status
    
    BTR->>DB: Poll recording_tasks status
    BTR->>DB: All complete → Publish version
    
    User->>APIService: Search for actions
    APIService->>DB: Query chunks + elements
    APIService-->>User: Return action manuals
```

**Sources:** Architecture diagrams, build pipeline overview

### Stage Progression

The build pipeline follows this stage sequence in the `build_tasks` table:

1. `stage='init'` - Initial task creation
2. `stage='knowledge_build'`, `stage_status='in_progress'` - Knowledge extraction active
3. `stage='knowledge_build'`, `stage_status='completed'` - Ready for action building
4. `stage='action_build'`, `stage_status='in_progress'` - Recording tasks being executed
5. `stage='action_build'`, `stage_status='completed'` - Build complete, version published

Each stage transition is managed by the respective service, creating a loosely coupled architecture where services communicate primarily through database state.

**Sources:** Diagram 3 from system overview

## Shared Infrastructure

All core services depend on shared packages located in `services/common` and `services/db`:

### Database Package (`services/db`)

Provides:
- Drizzle ORM schema definitions
- Database connection management (`getDb()` singleton)
- Migration scripts
- Type-safe query builders

Used by all services for data persistence and retrieval.

### Browser Package (`services/common/browser`)

Provides:
- `BrowserAdapter` interface - Unified API for browser automation
- `StagehandBrowser` - Local Playwright implementation with multi-LLM support
- `AgentCoreBrowser` - AWS cloud-based implementation

Used by Action Builder and Playbook Builder for web automation.

For detailed browser architecture, see [Browser Automation Layer](#4).

### Browser Profile Package (`services/common/browser-profile`)

Provides:
- `BrowserProfileManager` - Manages persistent browser state
- User data directory handling
- Lock file cleanup
- Anti-detection browser arguments

Used by services requiring persistent login sessions.

For profile management details, see [Browser Profiles](#4.4).

**Sources:** Architecture diagrams, pnpm-workspace.yaml, services directory structure

## Deployment Architecture

Each service can be deployed independently:

```mermaid
graph LR
    subgraph "API Tier"
        API["API Service<br/>Stateless HTTP server<br/>Multiple instances"]
    end
    
    subgraph "Worker Tier"
        Coord["Coordinator Process<br/>Polls build_tasks<br/>Single instance"]
        Workers["QueueWorker Processes<br/>Execute recordings<br/>Multiple instances"]
    end
    
    subgraph "Batch Jobs"
        KB["Knowledge Builder<br/>CLI invoked<br/>On-demand"]
        PB["Playbook Builder<br/>CLI invoked<br/>On-demand"]
    end
    
    subgraph "Shared Data"
        DB[("PostgreSQL Database<br/>All tables")]
    end
    
    API --> DB
    Coord --> DB
    Workers --> DB
    KB --> DB
    PB --> DB
```

**Deployment Characteristics:**

| Service | Concurrency | State | Scaling Strategy |
|---------|-------------|-------|------------------|
| API Service | Multiple instances | Stateless | Horizontal (load balanced) |
| Coordinator | Single instance | Stateful (in-memory runner tracking) | Vertical or sequential |
| QueueWorker | Multiple instances | Stateless | Horizontal (task queue) |
| Knowledge Builder | One per build | Stateless | On-demand batch jobs |
| Playbook Builder | One per build | Stateless | On-demand batch jobs |

The architecture supports both centralized (all services on one host) and distributed (services across multiple hosts) deployments. Task coordination occurs through database polling rather than message queues, simplifying deployment at the cost of increased database load.

**Sources:** Architecture diagrams, build pipeline description

## Environment Configuration

Services share common environment variables defined in `.env` files at the service level:

**Common Variables:**
- Database connection: `DATABASE_URL`, `POSTGRES_URL`
- LLM providers: `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `OPENROUTER_API_KEY`
- Browser settings: Browser profile paths, userDataDir locations
- Proxy settings: `HTTP_PROXY`, `HTTPS_PROXY` for network routing

Each service package contains an `.env.example` file documenting required and optional configuration.

**Sources:** README.md:719-723

## Build and Development

All services are built using the Turborepo monorepo build system defined in `turbo.json`:

```bash
# Build all services
pnpm build

# Run all services in development mode
pnpm dev

# Run specific service
cd services/action-builder && pnpm dev
```

The build system automatically handles dependencies between packages through the `dependsOn` configuration in `turbo.json:4-7`.

For detailed development setup instructions, see [Local Development Setup](#8.3).

**Sources:** README.md:702-735, turbo.json, package.json:8-14

---

# Page: API Service

# API Service

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [services/db/migrations/0019_add_vector_indexes.sql](services/db/migrations/0019_add_vector_indexes.sql)
- [services/db/migrations/0020_add_chunks_fulltext_index.sql](services/db/migrations/0020_add_chunks_fulltext_index.sql)

</details>



## Purpose and Scope

The API Service is a REST API that provides programmatic access to Actionbook's indexed action manuals and website capabilities. It exposes endpoints for searching actions, retrieving detailed action information, and listing available sources. The service implements hybrid search combining full-text and vector similarity to deliver relevant results.

This document covers the REST API endpoints, request/response formats, and the hybrid search implementation. For information about the SDK that wraps these endpoints, see [JavaScript SDK](#2.3). For details on the data storage layer, see [Database Schema](#5.1) and [Search and Indexing](#5.3).

**Sources:** [README.md:1-745]()

---

## Architecture Overview

The API Service acts as the primary data access layer for all Actionbook user interfaces. It serves pre-built action manuals stored in PostgreSQL and provides efficient search capabilities through specialized database indexes.

```mermaid
graph TB
    subgraph "Client Interfaces"
        CLI["CLI<br/>@actionbookdev/cli"]
        MCP["MCP Server<br/>@actionbookdev/mcp"]
        SDK["SDK<br/>@actionbookdev/sdk"]
    end
    
    subgraph "API Service Layer"
        APIService["apps/api-service<br/>REST API Server"]
        SearchEndpoint["/actions/search<br/>Hybrid search handler"]
        GetEndpoint["/actions/:id<br/>Element lookup handler"]
        SourcesEndpoint["/sources<br/>List sources handler"]
    end
    
    subgraph "Database Layer"
        DB[("PostgreSQL Database")]
        ChunksTable["chunks table<br/>content + embeddings"]
        ElementsTable["elements table<br/>selectors + metadata"]
        SourcesTable["sources table<br/>website catalog"]
    end
    
    subgraph "Database Indexes"
        GINIndex["GIN Full-Text Index<br/>chunks_content_gin_idx"]
        HNSWIndex["HNSW Vector Index<br/>chunks_embedding_hnsw_idx"]
        CompositeIndex["Composite Indexes<br/>FK + version filters"]
    end
    
    CLI --> APIService
    MCP --> APIService
    SDK --> APIService
    
    APIService --> SearchEndpoint
    APIService --> GetEndpoint
    APIService --> SourcesEndpoint
    
    SearchEndpoint --> ChunksTable
    GetEndpoint --> ElementsTable
    SourcesEndpoint --> SourcesTable
    
    ChunksTable --> GINIndex
    ChunksTable --> HNSWIndex
    ChunksTable --> CompositeIndex
    ElementsTable --> CompositeIndex
```

**Sources:** [README.md:1-745](), Architecture Diagrams

---

## Endpoints

The API Service exposes three primary REST endpoints for querying action manuals and source information.

### Endpoint Summary

| Endpoint | Method | Purpose | Primary Table |
|----------|--------|---------|---------------|
| `/actions/search` | GET | Search for actions using hybrid search (full-text + vector) | `chunks` |
| `/actions/:id` | GET | Retrieve detailed action information by element ID | `elements` |
| `/sources` | GET | List available indexed websites | `sources` |

**Sources:** [README.md:1-745](), Architecture Diagrams

---

## Search Actions Endpoint

### Endpoint: `GET /actions/search`

Performs hybrid search across indexed action manuals, combining full-text search and vector similarity to return relevant results.

#### Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `q` or `query` | string | Yes | Search query (e.g., "airbnb search", "google login") |
| `type` | string | No | Search type: `hybrid` (default), `fulltext`, or `vector` |
| `limit` | number | No | Maximum number of results to return |

#### Response Format

Returns an array of search results with action details:

```typescript
{
  id: string              // Element ID (e.g., "site/airbnb.com/page/home/element/search-button")
  name: string            // Element name
  description: string     // What this action does
  selectors: {
    css?: string          // CSS selector
    xpath?: string        // XPath selector
    dataTestId?: string   // data-testid attribute
    ariaLabel?: string    // aria-label attribute
    // ... other selector types
  }
  page: {
    url: string           // Page URL pattern
    name: string          // Page name
  }
  source: {
    domain: string        // Website domain
    name: string          // Website name
  }
  relevance: number       // Search relevance score
}
```

#### Example Usage

```bash
# CLI
actionbook search "airbnb search"

# SDK
const results = await actionbook.searchActions('airbnb search')

# HTTP
GET /actions/search?q=airbnb+search&type=hybrid&limit=10
```

**Sources:** [README.md:119-130](), [README.md:449-470](), Architecture Diagrams

---

## Get Action by ID Endpoint

### Endpoint: `GET /actions/:id`

Retrieves complete details for a specific action element, including all available selectors and metadata.

#### Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string | Yes | Element ID (path parameter) |

#### Response Format

Returns detailed action information from the `elements` table:

```typescript
{
  id: string              // Full element ID path
  name: string            // Element name
  description: string     // Detailed description
  elementType: string     // Type: button, input, link, etc.
  selectors: {
    css?: string
    xpath?: string
    dataTestId?: string
    ariaLabel?: string
    id?: string
    // All available selectors with confidence scores
  }
  allowedMethods: string[] // Allowed interaction methods
  page: {
    id: string
    url: string
    name: string
    module: string         // Page module classification
  }
  source: {
    id: string
    domain: string
    name: string
    version: string        // Active version
  }
}
```

#### Example Usage

```bash
# CLI
actionbook get "site/airbnb.com/page/home/element/search-button"

# SDK
const action = await actionbook.getActionById(results[0].id)

# HTTP
GET /actions/site%2Fairbnb.com%2Fpage%2Fhome%2Felement%2Fsearch-button
```

**Sources:** [README.md:123-124](), [README.md:461-463](), Architecture Diagrams

---

## Sources Endpoints

### Endpoint: `GET /sources`

Returns a list of all indexed websites available in the Actionbook database.

#### Request Parameters

None required. Optional filtering parameters may include:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `domain` | string | No | Filter by specific domain |
| `active` | boolean | No | Filter by active status |

#### Response Format

```typescript
{
  sources: [
    {
      id: string
      domain: string        // e.g., "airbnb.com"
      name: string          // e.g., "Airbnb"
      activeVersion: string // Current version ID
      indexedAt: string     // ISO 8601 timestamp
      pageCount: number     // Number of indexed pages
      elementCount: number  // Number of indexed elements
    }
  ]
}
```

**Sources:** [README.md:1-745](), Architecture Diagrams

---

## Hybrid Search Implementation

The API Service implements a sophisticated hybrid search system that combines full-text search and vector similarity search to deliver relevant results. This approach leverages PostgreSQL's native full-text search capabilities and the pgvector extension for semantic similarity.

```mermaid
graph TB
    subgraph "Search Request Flow"
        Query["Search Query<br/>'airbnb search'"]
        QueryProcessor["Query Processor"]
        EmbedGen["Embedding Generator<br/>OpenAI API"]
    end
    
    subgraph "Parallel Search Paths"
        FullTextPath["Full-Text Search Path"]
        VectorPath["Vector Search Path"]
    end
    
    subgraph "Full-Text Search"
        TSVector["to_tsvector('english', content)"]
        GINLookup["GIN Index Scan<br/>chunks_content_gin_idx"]
        FTResults["Full-Text Results<br/>+ ts_rank scores"]
    end
    
    subgraph "Vector Search"
        QueryEmbed["Query Embedding<br/>1536 dimensions"]
        HNSWLookup["HNSW Index Scan<br/>chunks_embedding_hnsw_idx"]
        CosineCalc["Cosine Distance<br/>vector_cosine_ops"]
        VecResults["Vector Results<br/>+ similarity scores"]
    end
    
    subgraph "Result Combination"
        Merger["Result Merger"]
        Ranker["Hybrid Ranker<br/>weighted scoring"]
        FinalResults["Final Results<br/>sorted by relevance"]
    end
    
    Query --> QueryProcessor
    QueryProcessor --> EmbedGen
    QueryProcessor --> FullTextPath
    QueryProcessor --> VectorPath
    
    FullTextPath --> TSVector
    TSVector --> GINLookup
    GINLookup --> FTResults
    
    VectorPath --> EmbedGen
    EmbedGen --> QueryEmbed
    QueryEmbed --> HNSWLookup
    HNSWLookup --> CosineCalc
    CosineCalc --> VecResults
    
    FTResults --> Merger
    VecResults --> Merger
    Merger --> Ranker
    Ranker --> FinalResults
```

**Sources:** Architecture Diagrams, [services/db/migrations/0019_add_vector_indexes.sql:1-22](), [services/db/migrations/0020_add_chunks_fulltext_index.sql:1-19]()

---

## Full-Text Search Implementation

Full-text search uses PostgreSQL's native text search capabilities with GIN (Generalized Inverted Index) indexes for fast keyword matching.

### Database Index Structure

The `chunks` table uses two GIN indexes optimized for different query patterns:

```sql
-- Primary GIN index for all chunks
CREATE INDEX chunks_content_gin_idx
ON chunks
USING gin (to_tsvector('english', content));

-- Optimized partial index for active versions
CREATE INDEX chunks_content_gin_active_idx
ON chunks
USING gin (to_tsvector('english', content))
WHERE source_version_id IS NOT NULL;
```

### Performance Characteristics

| Metric | Without Index | With GIN Index |
|--------|---------------|----------------|
| Search Time | ~2000ms | ~200ms |
| Index Type | Sequential Scan | GIN Index Scan |
| Disk Impact | None | Additional storage for index |

### Full-Text Query Processing

The full-text search path:

1. **Text Tokenization**: Query is processed using PostgreSQL's `to_tsquery()` function with English language configuration
2. **Index Scan**: GIN index quickly identifies matching documents using inverted index structure
3. **Ranking**: Results are ranked using `ts_rank()` function based on term frequency and position
4. **Filtering**: Additional filters applied for `source_version_id` to return only active versions

### Supporting Indexes

Additional indexes improve JOIN and filter performance:

```sql
-- Fast JOIN on document relationships
CREATE INDEX chunks_document_id_idx
ON chunks (document_id);

-- Composite index for version filtering
CREATE INDEX chunks_version_embedding_idx
ON chunks (source_version_id)
WHERE embedding IS NOT NULL;
```

**Sources:** [services/db/migrations/0020_add_chunks_fulltext_index.sql:1-19]()

---

## Vector Search Implementation

Vector search uses the pgvector extension with HNSW (Hierarchical Navigable Small World) indexes for approximate nearest neighbor search based on semantic similarity.

### Vector Index Structure

The `chunks` table stores 1536-dimensional embeddings (OpenAI text-embedding-3-small format) and uses HNSW indexing:

```sql
-- HNSW index for fast approximate nearest neighbor search
CREATE INDEX chunks_embedding_hnsw_idx
ON chunks
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);
```

### HNSW Index Parameters

| Parameter | Value | Purpose |
|-----------|-------|---------|
| `m` | 16 | Number of bidirectional connections per layer. Higher values improve recall but slow down index construction and increase memory usage. |
| `ef_construction` | 64 | Size of dynamic candidate list during index construction. Higher values improve index quality but increase build time. |
| Distance Function | `vector_cosine_ops` | Uses cosine distance for similarity comparison, optimal for normalized embeddings. |

### Vector Search Query Flow

1. **Query Embedding Generation**: Search query is converted to a 1536-dimensional vector using the same embedding model (OpenAI)
2. **HNSW Traversal**: Index performs approximate nearest neighbor search by navigating the hierarchical graph structure
3. **Cosine Distance Calculation**: Similarity computed using cosine distance: `1 - cosine_similarity`
4. **Top-K Selection**: Returns K most similar chunks with similarity scores

### Performance Trade-offs

| Aspect | Exact Search | HNSW Approximate |
|--------|--------------|------------------|
| Accuracy | 100% | 95-99% |
| Query Time | O(n) linear | O(log n) approximate |
| Index Size | None | ~20% of vector data |
| Typical Latency | Seconds | <100ms |

### Supporting Indexes for Vector Search

```sql
-- Fast filtering by source version
CREATE INDEX chunks_source_version_id_idx
ON chunks (source_version_id)
WHERE source_version_id IS NOT NULL;

-- Composite index for common filter pattern
CREATE INDEX chunks_version_embedding_idx
ON chunks (source_version_id)
WHERE embedding IS NOT NULL;
```

**Sources:** [services/db/migrations/0019_add_vector_indexes.sql:1-22]()

---

## Hybrid Search Query Processing

The hybrid search combines full-text and vector search results using a weighted scoring algorithm to balance keyword relevance with semantic similarity.

### Search Flow Diagram

```mermaid
sequenceDiagram
    participant Client
    participant APIService as "API Service<br/>/actions/search"
    participant EmbedAPI as "OpenAI API<br/>Embeddings"
    participant DB as "PostgreSQL<br/>Database"
    
    Client->>APIService: GET /actions/search?q=airbnb+search&type=hybrid
    
    par Full-Text Search
        APIService->>DB: SELECT with ts_query('airbnb & search')
        Note over DB: GIN index scan on<br/>chunks_content_gin_idx
        DB->>APIService: Full-text results + ts_rank scores
    and Vector Search
        APIService->>EmbedAPI: Generate embedding for query
        EmbedAPI->>APIService: [0.123, -0.456, ...] (1536d)
        APIService->>DB: SELECT with cosine distance
        Note over DB: HNSW index scan on<br/>chunks_embedding_hnsw_idx
        DB->>APIService: Vector results + cosine distances
    end
    
    Note over APIService: Merge results:<br/>weighted_score = α×ft_score + β×vec_score
    Note over APIService: Deduplicate and sort by weighted_score
    
    APIService->>Client: Combined results ordered by relevance
```

### Result Combination Algorithm

The hybrid search merges results from both search paths:

1. **Score Normalization**: Both full-text rank and vector similarity scores are normalized to [0, 1] range
2. **Weighted Combination**: 
   - Default weights: α = 0.5 (full-text), β = 0.5 (vector)
   - Combined score: `score = α × normalized_ft_rank + β × (1 - cosine_distance)`
3. **Deduplication**: Same chunks appearing in both result sets are merged with combined scores
4. **Sorting**: Final results sorted by combined relevance score in descending order
5. **Limit Application**: Top N results returned based on request limit parameter

### Query Optimization Strategies

The API Service applies several optimizations:

| Strategy | Implementation | Benefit |
|----------|----------------|---------|
| **Partial Index Usage** | Queries filter `WHERE source_version_id IS NOT NULL` to use `chunks_content_gin_active_idx` | Smaller index, faster scans |
| **Composite Index Leverage** | Version filtering uses `chunks_version_embedding_idx` for both conditions | Single index scan instead of two |
| **Parallel Execution** | Full-text and vector searches execute concurrently | ~50% reduction in total latency |
| **Result Set Limiting** | LIMIT clause applied at database level | Reduces data transfer and processing |

**Sources:** [services/db/migrations/0019_add_vector_indexes.sql:1-22](), [services/db/migrations/0020_add_chunks_fulltext_index.sql:1-19](), Architecture Diagrams

---

## Authentication and Access Control

### Current State (Open Beta)

During the open beta period, the API Service does not require authentication:

- No API keys needed for any endpoints
- Rate limiting may be applied at the infrastructure level
- All indexed action manuals are publicly accessible

### Usage in Client Libraries

The SDK and CLI are designed to support future authentication:

```typescript
// SDK initialization (API key optional during beta)
const actionbook = new Actionbook({
  apiKey: process.env.ACTIONBOOK_API_KEY  // Optional
})

// CLI with environment variable
export ACTIONBOOK_API_KEY=your_key_here
actionbook search "query"
```

**Sources:** [README.md:94-103](), [README.md:450-454]()

---

## Database Queries and Performance

### Index Strategy Summary

The API Service relies on specialized PostgreSQL indexes for optimal performance:

| Index Name | Type | Column(s) | Purpose | Impact |
|------------|------|-----------|---------|--------|
| `chunks_content_gin_idx` | GIN | `to_tsvector('english', content)` | Full-text search on all chunks | 10x faster text search |
| `chunks_content_gin_active_idx` | GIN (partial) | `to_tsvector('english', content)` WHERE active | Full-text search on active versions only | Smaller, faster for common queries |
| `chunks_embedding_hnsw_idx` | HNSW | `embedding vector_cosine_ops` | Approximate nearest neighbor search | <100ms vector search |
| `chunks_document_id_idx` | B-tree | `document_id` | JOIN optimization | Faster element lookups |
| `chunks_source_version_id_idx` | B-tree | `source_version_id` | Version filtering | Faster active version queries |
| `chunks_version_embedding_idx` | B-tree (partial) | `source_version_id` WHERE embedded | Combined filter optimization | Single index scan |

### Query Pattern Examples

#### Hybrid Search Query Structure

```sql
-- Full-text component
SELECT 
  c.id,
  c.content,
  ts_rank(to_tsvector('english', c.content), to_tsquery('english', $1)) as ft_score
FROM chunks c
WHERE to_tsvector('english', c.content) @@ to_tsquery('english', $1)
  AND c.source_version_id IS NOT NULL
ORDER BY ft_score DESC
LIMIT 50;

-- Vector component
SELECT
  c.id,
  c.content,
  1 - (c.embedding <=> $1::vector) as similarity
FROM chunks c
WHERE c.embedding IS NOT NULL
  AND c.source_version_id IS NOT NULL
ORDER BY c.embedding <=> $1::vector
LIMIT 50;
```

#### Element Lookup Query

```sql
SELECT 
  e.id,
  e.name,
  e.description,
  e.selectors,
  p.url as page_url,
  s.domain as source_domain
FROM elements e
JOIN pages p ON e.page_id = p.id
JOIN sources s ON p.source_id = s.id
WHERE e.id = $1;
```

**Sources:** [services/db/migrations/0019_add_vector_indexes.sql:1-22](), [services/db/migrations/0020_add_chunks_fulltext_index.sql:1-19]()

---

## Integration with Client Libraries

The API Service is consumed by three primary client interfaces, each providing different usage patterns:

### Client Integration Matrix

| Client | Package | Use Case | Integration Method |
|--------|---------|----------|-------------------|
| **CLI** | `@actionbookdev/cli` | Command-line usage, AI agent automation | Direct HTTP requests |
| **MCP Server** | `@actionbookdev/mcp` | IDE integration (Cursor, VS Code, etc.) | HTTP requests wrapped in MCP tools |
| **SDK** | `@actionbookdev/sdk` | Programmatic integration, custom agents | HTTP client with TypeScript types |

### API Client Architecture

```mermaid
graph LR
    subgraph "Client Packages"
        CLI["@actionbookdev/cli<br/>Command handlers"]
        MCP["@actionbookdev/mcp<br/>MCP tool server"]
        SDK["@actionbookdev/sdk<br/>Actionbook class"]
    end
    
    subgraph "Shared HTTP Layer"
        HTTPClient["HTTP Client<br/>fetch/axios"]
        TypeDefs["Type Definitions<br/>ToolDefinition interface"]
    end
    
    subgraph "API Service"
        SearchRoute["/actions/search"]
        GetRoute["/actions/:id"]
        SourcesRoute["/sources"]
    end
    
    CLI --> HTTPClient
    MCP --> HTTPClient
    SDK --> HTTPClient
    
    HTTPClient --> TypeDefs
    
    HTTPClient --> SearchRoute
    HTTPClient --> GetRoute
    HTTPClient --> SourcesRoute
```

### Tool Definition Schema

All client libraries expose consistent tool definitions for LLM integration:

```typescript
// searchActions tool
{
  name: "searchActions",
  description: "Search for action manuals by keyword",
  params: {
    json: {
      type: "object",
      properties: {
        query: { type: "string", description: "Search query" }
      },
      required: ["query"]
    },
    zod: z.object({ query: z.string() })
  }
}

// getActionById tool
{
  name: "getActionById",
  description: "Retrieve detailed action manual by ID",
  params: {
    json: {
      type: "object",
      properties: {
        id: { type: "string", description: "Element ID" }
      },
      required: ["id"]
    },
    zod: z.object({ id: z.string() })
  }
}
```

**Sources:** [README.md:473-489](), [README.md:493-659]()

---

## Error Handling and Status Codes

The API Service uses standard HTTP status codes and returns consistent error response formats.

### HTTP Status Codes

| Status Code | Meaning | When Used |
|-------------|---------|-----------|
| `200 OK` | Success | Request completed successfully |
| `400 Bad Request` | Invalid input | Missing required parameters, invalid query format |
| `404 Not Found` | Resource not found | Element ID does not exist |
| `429 Too Many Requests` | Rate limit exceeded | Client exceeding request quota |
| `500 Internal Server Error` | Server error | Database connection failure, unexpected errors |
| `503 Service Unavailable` | Service down | Maintenance mode, database unavailable |

### Error Response Format

```typescript
{
  error: {
    code: string        // Error code (e.g., "INVALID_QUERY", "NOT_FOUND")
    message: string     // Human-readable error message
    details?: object    // Additional error context
  }
}
```

**Sources:** Architecture Diagrams

---

# Page: Action Builder Service

# Action Builder Service

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [services/action-builder/.env.example](services/action-builder/.env.example)
- [services/action-builder/.gitignore](services/action-builder/.gitignore)
- [services/action-builder/README.md](services/action-builder/README.md)
- [services/action-builder/package.json](services/action-builder/package.json)
- [services/action-builder/scripts/coordinator.ts](services/action-builder/scripts/coordinator.ts)
- [services/action-builder/scripts/crawl-playbook-batch.ts](services/action-builder/scripts/crawl-playbook-batch.ts)
- [services/action-builder/scripts/crawl-sites.txt.example](services/action-builder/scripts/crawl-sites.txt.example)
- [services/action-builder/scripts/import-playbook-batch.ts](services/action-builder/scripts/import-playbook-batch.ts)
- [services/action-builder/src/llm/AIClient.ts](services/action-builder/src/llm/AIClient.ts)
- [services/action-builder/src/utils/logger.ts](services/action-builder/src/utils/logger.ts)
- [services/action-builder/vitest.setup.ts](services/action-builder/vitest.setup.ts)
- [services/db/migrations/meta/0018_snapshot.json](services/db/migrations/meta/0018_snapshot.json)

</details>



The Action Builder Service is responsible for automatically discovering and recording UI capabilities of websites. It uses LLM-powered browser automation to explore web pages, identify interactive elements, extract stable CSS/XPath selectors, and persist them to both PostgreSQL database and YAML files. This service is the core of Actionbook's "recording" functionality that generates action manuals.

For information about the task execution pipeline internals, see [Task Execution Pipeline](#3.2.1). For details on how the recording process works with LLM tool loops, see [Action Recording](#3.2.2). For a complete reference of available recording tools, see [Recording Tools Reference](#3.2.3).

## Architecture Overview

The Action Builder Service implements a three-layer task orchestration architecture that enables concurrent processing of multiple websites while efficiently managing browser resources.

### Three-Layer Architecture

```mermaid
graph TB
    subgraph Layer1["Layer 1: Coordinator"]
        Coordinator["Coordinator<br/>(coordinator.ts)"]
    end
    
    subgraph Layer2["Layer 2: Per-Build Orchestration"]
        BTR1["BuildTaskRunner #1<br/>(build-task-runner.ts)"]
        BTR2["BuildTaskRunner #2<br/>(build-task-runner.ts)"]
        BTRn["BuildTaskRunner #N<br/>..."]
    end
    
    subgraph Layer3["Layer 3: Global Task Execution"]
        QW["RecordingTaskQueueWorker<br/>(recording-task-queue-worker.ts)"]
    end
    
    subgraph Database["PostgreSQL Database"]
        BuildTasks["build_tasks table<br/>stage, stage_status, updated_at"]
        RecordingTasks["recording_tasks table<br/>status, last_heartbeat, attempt_count"]
    end
    
    subgraph Execution["Task Execution"]
        TE1["TaskExecutor #1<br/>(task-executor.ts)"]
        TE2["TaskExecutor #2<br/>(task-executor.ts)"]
        TEn["TaskExecutor #M<br/>..."]
        
        AR1["ActionRecorder<br/>(ActionRecorder.ts)"]
        AR2["ActionRecorder"]
        ARn["ActionRecorder"]
        
        Browser1["BrowserAdapter<br/>StagehandBrowser"]
        Browser2["BrowserAdapter"]
        Browsern["BrowserAdapter"]
    end
    
    Coordinator -->|"Claims build_tasks<br/>(max N concurrent)"| BTR1
    Coordinator --> BTR2
    Coordinator --> BTRn
    
    BTR1 -->|"Generates & monitors<br/>recording_tasks"| RecordingTasks
    BTR2 --> RecordingTasks
    BTRn --> RecordingTasks
    
    BTR1 -.->|"Heartbeat (5s)<br/>updated_at"| BuildTasks
    
    QW -->|"Claims pending tasks<br/>(max M concurrent)"| RecordingTasks
    
    QW --> TE1
    QW --> TE2
    QW --> TEn
    
    TE1 --> AR1
    TE2 --> AR2
    TEn --> ARn
    
    AR1 --> Browser1
    AR2 --> Browser2
    ARn --> Browsern
    
    TE1 -.->|"Heartbeat (5s)<br/>last_heartbeat"| RecordingTasks
```

**Sources:** [services/action-builder/README.md:159-192](), [services/action-builder/scripts/coordinator.ts:1-82]()

### Layer Responsibilities

| Layer | Component | Concurrency | Responsibility |
|-------|-----------|-------------|----------------|
| 1 | `Coordinator` | N build_tasks | Claims `build_tasks` with `stage=knowledge_build` and `stage_status=completed`, spawns `BuildTaskRunner` instances |
| 2 | `BuildTaskRunner` | 1 per build_task | Generates `recording_tasks` for all chunks, polls status, retries failures, publishes version on completion |
| 3 | `RecordingTaskQueueWorker` | M recording_tasks | Global consumer that executes pending `recording_tasks` using `TaskExecutor` + `ActionRecorder` + `BrowserAdapter` |

**Sources:** [services/action-builder/README.md:159-192]()

### Key Design Patterns

**Separation of Orchestration and Execution**: `BuildTaskRunner` manages per-build task lifecycle (generation, monitoring, retry) but delegates actual execution to `RecordingTaskQueueWorker`. This allows efficient resource utilization where M browser instances can process tasks from N different builds concurrently.

**Database as Queue**: All state is stored in `build_tasks` and `recording_tasks` tables. No in-memory state means the system is fully stateless and recoverable after crashes.

**Heartbeat-Based Stale Detection**: Both layers use heartbeat mechanisms:
- `build_tasks.updated_at` updated every 5 seconds by `BuildTaskRunner`
- `recording_tasks.last_heartbeat` updated every 5 seconds by `TaskExecutor`

Stale tasks (no heartbeat for 15+ minutes) are automatically recovered by `Coordinator` or `RecordingTaskQueueWorker`.

**Sources:** [services/action-builder/README.md:319-335](), [services/action-builder/README.md:356-365]()

## Build Pipeline Flow

The Action Builder Service processes websites through a multi-stage pipeline that progresses from knowledge building to action building.

```mermaid
graph TB
    subgraph Input["Pipeline Input"]
        KBComplete["build_tasks<br/>stage=knowledge_build<br/>stage_status=completed"]
    end
    
    subgraph Stage1["Stage 1: Claim & Setup"]
        Claim["Coordinator.claimNextBuildTask()"]
        SpawnBTR["Spawn BuildTaskRunner"]
        UpdateStage["UPDATE build_tasks<br/>SET stage='action_build'<br/>stage_status='running'<br/>action_started_at=NOW()"]
    end
    
    subgraph Stage2["Stage 2: Generate Recording Tasks"]
        GenTasks["BuildTaskRunner.generateRecordingTasks()"]
        QueryChunks["SELECT chunks<br/>WHERE source_version_id=?<br/>ORDER BY chunk_index"]
        DetectType["ChunkTypeDetector<br/>task_driven vs exploratory"]
        InsertTasks["INSERT recording_tasks<br/>status='pending'<br/>attempt_count=0"]
    end
    
    subgraph Stage3["Stage 3: Execute Tasks"]
        QWClaim["QueueWorker.claimNextTask()"]
        Execute["TaskExecutor.execute()"]
        Recorder["ActionRecorder.record()"]
        SaveResults["Save to elements, pages<br/>+ YAML files"]
    end
    
    subgraph Stage4["Stage 4: Monitor & Retry"]
        Poll["BuildTaskRunner.pollTaskStatus()"]
        CheckComplete["All pending=0<br/>AND running=0<br/>AND retriedCount=0?"]
        Retry["Reset failed tasks<br/>WHERE attempt_count < max"]
    end
    
    subgraph Stage5["Stage 5: Publish"]
        Publish["BuildTaskRunner.publishVersion()"]
        UpdateVersion["UPDATE source_versions<br/>SET status='active'<br/>published_at=NOW()"]
        ArchivePrev["Archive previous version<br/>SET status='archived'"]
        UpdateBuildTask["UPDATE build_tasks<br/>SET stage_status='completed'<br/>action_completed_at=NOW()"]
    end
    
    KBComplete --> Claim
    Claim --> SpawnBTR
    SpawnBTR --> UpdateStage
    UpdateStage --> GenTasks
    
    GenTasks --> QueryChunks
    QueryChunks --> DetectType
    DetectType --> InsertTasks
    
    InsertTasks --> QWClaim
    QWClaim --> Execute
    Execute --> Recorder
    Recorder --> SaveResults
    
    SaveResults -.->|"Continuous"| Poll
    Poll --> CheckComplete
    CheckComplete -->|"No"| Retry
    Retry -.->|"Reset to pending"| QWClaim
    CheckComplete -->|"Yes"| Publish
    
    Publish --> UpdateVersion
    UpdateVersion --> ArchivePrev
    ArchivePrev --> UpdateBuildTask
```

**Sources:** [services/action-builder/README.md:379-399]()

### Stage Details

| Stage | Duration | Key Operations | Database Updates |
|-------|----------|----------------|------------------|
| Claim & Setup | <1s | Atomic `UPDATE ... WHERE` to claim next available `build_task` | `build_tasks.stage`, `stage_status`, `action_started_at` |
| Generate Tasks | 5-30s | Query all chunks, detect type (`task_driven`/`exploratory`), bulk insert | ~50-100 rows in `recording_tasks` |
| Execute Tasks | 5-60 min | LLM tool loop, element discovery, selector extraction | `recording_tasks.status`, `elements`, `pages`, YAML files |
| Monitor & Retry | Continuous | Poll every 5s, retry failed tasks (max 3 attempts) | `recording_tasks.status`, `attempt_count` |
| Publish | <5s | Blue-Green deployment: activate new version, archive old | `source_versions.status`, `build_tasks.stage_status` |

**Sources:** [services/action-builder/README.md:379-399]()

## Task Types

The Action Builder Service uses two distinct task types with different lifecycles and purposes.

### Build Tasks vs Recording Tasks

```mermaid
graph LR
    subgraph BuildTask["build_tasks (1 per website)"]
        BT_ID["id: serial"]
        BT_Stage["stage: varchar(20)<br/>'init' → 'knowledge_build' →<br/>'action_build'"]
        BT_Status["stage_status: varchar(20)<br/>'pending' → 'running' →<br/>'completed'"]
        BT_Source["source_id: integer<br/>source_version_id: integer"]
        BT_Updated["updated_at: timestamp<br/>(heartbeat field)"]
    end
    
    subgraph RecordingTask["recording_tasks (50-100 per build_task)"]
        RT_ID["id: serial"]
        RT_BuildTask["build_task_id: integer"]
        RT_Chunk["chunk_id: integer"]
        RT_Status["status: varchar(20)<br/>'pending' → 'running' →<br/>'completed' / 'failed'"]
        RT_Attempt["attempt_count: integer<br/>(increments on retry)"]
        RT_Heartbeat["last_heartbeat: timestamp<br/>(heartbeat field)"]
        RT_Type["config.chunk_type:<br/>'task_driven' | 'exploratory'"]
    end
    
    BuildTask -->|"1:N relationship"| RecordingTask
```

**Sources:** [services/action-builder/README.md:366-377](), [services/db/migrations/meta/0018_snapshot.json:97-290](), [services/db/migrations/meta/0018_snapshot.json:1079-1268]()

### Chunk Type Detection

Recording tasks are categorized based on chunk content to optimize LLM prompts:

```mermaid
graph TD
    Chunk["Chunk Content"]
    Analyze["ChunkTypeDetector.detect()"]
    
    TaskDriven["task_driven<br/>Action-oriented content"]
    Exploratory["exploratory<br/>Overview content"]
    
    Examples_TD["Examples:<br/>• 'How to search for articles'<br/>• 'Filtering results by date'<br/>• 'Submitting the form'"]
    
    Examples_EX["Examples:<br/>• 'Homepage overview'<br/>• 'Navigation menu structure'<br/>• 'Footer links'"]
    
    Focus_TD["Focus:<br/>• Pattern selectors<br/>• Repeating elements<br/>• Data extraction"]
    
    Focus_EX["Focus:<br/>• All interactive elements<br/>• Page structure<br/>• Global navigation"]
    
    Chunk --> Analyze
    Analyze -->|"Contains action verbs,<br/>step-by-step instructions"| TaskDriven
    Analyze -->|"Contains overview,<br/>general description"| Exploratory
    
    TaskDriven --> Examples_TD
    TaskDriven --> Focus_TD
    
    Exploratory --> Examples_EX
    Exploratory --> Focus_EX
```

**Sources:** [services/action-builder/README.md:413-421]()

### Task Lifecycle State Machine

```mermaid
stateDiagram-v2
    [*] --> pending: BuildTaskRunner generates task
    
    pending --> running: QueueWorker claims task<br/>attempt_count++
    
    running --> completed: TaskExecutor success<br/>elements/pages saved
    running --> failed: TaskExecutor error<br/>or timeout
    running --> pending: Stale detection<br/>(last_heartbeat > 15min)
    
    failed --> pending: BuildTaskRunner retry<br/>(if attempt_count < max)
    failed --> failed: Max attempts reached<br/>(no more retries)
    
    completed --> [*]: Task finished
    failed --> [*]: Task permanently failed
    
    note right of running
        Heartbeat every 5s
        last_heartbeat = NOW()
    end note
    
    note right of failed
        Max attempts = 3 (default)
        Permanent failures do NOT
        block build_task completion
    end note
```

**Sources:** [services/action-builder/README.md:337-355]()

## Configuration

The Action Builder Service is configured through environment variables that control concurrency, timeouts, retry behavior, and logging.

### Environment Variables Reference

| Variable | Default | Description | Used By |
|----------|---------|-------------|---------|
| **Coordinator Settings** | | | |
| `ACTION_BUILDER_BUILD_TASK_CONCURRENCY` | `5` | Max concurrent `build_tasks` (N) | `Coordinator` |
| `ACTION_BUILDER_BUILD_TASK_POLL_INTERVAL_SECONDS` | `5` | How often to check for new `build_tasks` | `Coordinator` |
| `ACTION_BUILDER_BUILD_TASK_STALE_TIMEOUT_MINUTES` | `15` | Stale timeout for `build_tasks` (crash recovery) | `Coordinator` |
| **BuildTaskRunner Settings** | | | |
| `ACTION_BUILDER_CHECK_INTERVAL_SECONDS` | `5` | How often to poll `recording_tasks` status | `BuildTaskRunner` |
| `ACTION_BUILDER_MAX_ATTEMPTS` | `3` | Max retry attempts for failed tasks | `BuildTaskRunner` |
| **QueueWorker Settings** | | | |
| `ACTION_BUILDER_RECORDING_TASK_CONCURRENCY` | `3` | Max concurrent `recording_tasks` (M) / browser instances | `RecordingTaskQueueWorker` |
| `ACTION_BUILDER_STALE_TIMEOUT_MINUTES` | `15` | Stale timeout for `recording_tasks` | `RecordingTaskQueueWorker` |
| `ACTION_BUILDER_TASK_TIMEOUT_MINUTES` | `10` | Single task execution timeout | `TaskExecutor` |
| **Recording Settings** | | | |
| `ACTION_BUILDER_HEADLESS` | `true` | Run browser in headless mode | `BrowserAdapter` |
| `ACTION_BUILDER_MAX_TURNS` | `30` | Max LLM conversation turns per task | `ActionRecorder` |
| `OUTPUT_DIR` | `./output` | Directory for YAML output files | `YamlWriter` |
| **Logging Settings** | | | |
| `ACTION_BUILDER_QUIET` | `true` | Quiet mode: only task-level logs to console | Logger |

**Sources:** [services/action-builder/README.md:215-231](), [services/action-builder/.env.example:91-142]()

### Concurrency Model

```mermaid
graph TB
    subgraph N_BuildTasks["N = BUILD_TASK_CONCURRENCY (default 5)"]
        BT1["BuildTaskRunner #1<br/>website A"]
        BT2["BuildTaskRunner #2<br/>website B"]
        BT3["BuildTaskRunner #3<br/>website C"]
        BTn["..."]
    end
    
    subgraph TaskQueue["Global recording_tasks Queue"]
        Q["pending tasks from all build_tasks<br/>(shared queue)"]
    end
    
    subgraph M_Workers["M = RECORDING_TASK_CONCURRENCY (default 3)"]
        W1["TaskExecutor #1<br/>Browser Instance"]
        W2["TaskExecutor #2<br/>Browser Instance"]
        W3["TaskExecutor #3<br/>Browser Instance"]
    end
    
    BT1 -->|"Generate 50 tasks"| Q
    BT2 -->|"Generate 75 tasks"| Q
    BT3 -->|"Generate 60 tasks"| Q
    BTn --> Q
    
    Q -->|"Claim next pending"| W1
    Q --> W2
    Q --> W3
    
    note1["Example: N=5, M=3<br/>• 5 websites processed concurrently<br/>• 3 browser instances shared<br/>• Total 185 tasks in queue"]
    
    style note1 fill:#f9f9f9,stroke:#333,stroke-width:1px
```

**Sources:** [services/action-builder/README.md:159-192]()

### Logging Modes

The service supports two logging modes controlled by `ACTION_BUILDER_QUIET`:

**Quiet Mode (default):**
- Console: Only task-level logs (`[Coordinator]`, `[BuildTaskRunner]`, `[QueueWorker]`, `[Metrics]`)
- File: All logs including `[ActionRecorder]` details (browser operations, LLM calls)
- Log files: `logs/action-builder_YYYYMMDDHHmmss.log`

**Verbose Mode (`ACTION_BUILDER_QUIET=false`):**
- Console: All logs (task-level + ActionRecorder details)
- File: Same as console

**Sources:** [services/action-builder/README.md:230-254](), [services/action-builder/src/utils/logger.ts:80-107]()

## Data Storage

The Action Builder Service persists data to both PostgreSQL database (for querying and versioning) and YAML files (for human readability and Git version control).

### Database Schema

```mermaid
erDiagram
    sources ||--o{ build_tasks : "has"
    sources ||--o{ source_versions : "has"
    sources ||--o{ pages : "has"
    sources ||--o{ recording_tasks : "has"
    
    source_versions ||--o{ build_tasks : "references"
    
    build_tasks ||--o{ recording_tasks : "has"
    
    chunks ||--o{ recording_tasks : "references"
    
    pages ||--o{ elements : "has"
    
    sources {
        serial id PK
        varchar name
        text base_url UK
        text domain
        integer current_version_id FK
    }
    
    source_versions {
        serial id PK
        integer source_id FK
        integer version_number
        varchar status "building,active,archived"
        timestamp published_at
    }
    
    build_tasks {
        serial id PK
        integer source_id FK
        integer source_version_id FK
        varchar stage "init,knowledge_build,action_build"
        varchar stage_status "pending,running,completed,failed"
        timestamp updated_at "heartbeat"
        timestamp action_started_at
        timestamp action_completed_at
    }
    
    recording_tasks {
        serial id PK
        integer source_id FK
        integer build_task_id FK
        integer chunk_id FK
        varchar status "pending,running,completed,failed"
        integer attempt_count
        timestamp last_heartbeat "heartbeat"
        jsonb config "chunk_type, etc"
    }
    
    pages {
        serial id PK
        integer source_id FK
        varchar page_type UK
        varchar name
        jsonb url_patterns
    }
    
    elements {
        serial id PK
        integer page_id FK
        varchar semantic_id UK
        varchar element_type
        jsonb selectors
        jsonb allow_methods
        varchar status
    }
```

**Sources:** [services/action-builder/README.md:366-377](), [services/db/migrations/meta/0018_snapshot.json:1346-1454](), [services/db/migrations/meta/0018_snapshot.json:1269-1345](), [services/db/migrations/meta/0018_snapshot.json:97-290](), [services/db/migrations/meta/0018_snapshot.json:1079-1268](), [services/db/migrations/meta/0018_snapshot.json:874-972](), [services/db/migrations/meta/0018_snapshot.json:731-873]()

### Key Indexes

| Table | Index | Purpose |
|-------|-------|---------|
| `build_tasks` | `idx_build_tasks_stage_status` | Fast lookup: `WHERE stage=? AND stage_status=?` |
| `build_tasks` | `idx_build_tasks_source_id` | Per-source queries |
| `recording_tasks` | Composite unique: `(chunk_id, build_task_id)` | Prevent duplicate task generation |

**Sources:** [services/db/migrations/meta/0018_snapshot.json:204-256]()

## Output Format

The Action Builder Service generates dual output: database records for querying and YAML files for human readability.

### YAML File Structure

```
output/
└── sites/
    └── {domain}/
        ├── site.yaml
        └── pages/
            └── {page_type}.yaml
```

**Example: `output/sites/www.example.com/pages/search_results.yaml`**

```yaml
page_type: search_results
name: Search Results
description: Page displaying search results with filters
url_patterns:
  - "^https://www\\.example\\.com/search\\?q=.*"
wait_for: "main ul li"

elements:
  search_result_card:
    id: search_result_card
    element_type: list_item
    description: Individual search result card
    selectors:
      - type: css
        value: "main ul li"
        priority: 1
        confidence: 0.85
      - type: xpath
        value: "//main//ul/li"
        priority: 2
        confidence: 0.80
    allow_methods:
      - click
      - extract
    is_repeating: true
    
  result_title_field:
    id: result_title_field
    element_type: data_field
    description: Title of the search result
    selectors:
      - type: css
        value: "main ul li h2"
        priority: 1
        confidence: 0.90
    allow_methods:
      - extract
    data_key: title
    is_repeating: true
```

**Sources:** [services/action-builder/README.md:422-478]()

### Element Properties

| Property | Type | Description | Example |
|----------|------|-------------|---------|
| `id` | string | Semantic identifier (snake_case) | `search_button`, `user_profile_menu` |
| `element_type` | enum | Type of UI element | `button`, `data_field`, `list_item`, `navigation` |
| `description` | string | Human-readable description | `"Submit search query"` |
| `selectors` | array | Ordered list of CSS/XPath selectors | See selector structure below |
| `allow_methods` | array | Allowed interaction methods | `["click"]`, `["click", "extract"]` |
| `is_repeating` | boolean | Whether element appears multiple times | `true` for list items |
| `depends_on` | string | Element ID that must be interacted with first | `"expand_button"` |
| `visibility_condition` | string | When element becomes visible | `"after_click:expand_button"` |

**Selector Structure:**

```yaml
selectors:
  - type: css               # css, xpath, id, dataTestId, ariaLabel
    value: "button.submit"  # Actual selector string
    priority: 1             # Lower = higher priority
    confidence: 0.85        # 0.0-1.0, from SelectorOptimizer
```

**Sources:** [services/action-builder/README.md:438-478]()

## Usage Modes

The Action Builder Service supports two operational modes: automated coordinator mode for production and manual CLI mode for development/testing.

### Mode 1: Automated Coordinator (Production)

```bash
# Start coordinator with default settings
pnpm coordinator

# Development mode with auto-reload
pnpm dev

# Verbose mode (all logs to console)
pnpm coordinator:verbose
```

**Behavior:**
1. `Coordinator` starts, polls for `build_tasks` with `stage=knowledge_build` and `stage_status=completed`
2. Spawns `BuildTaskRunner` for each claimed task (max N concurrent)
3. `RecordingTaskQueueWorker` consumes `recording_tasks` globally (max M concurrent)
4. Prints metrics every 30 seconds
5. Automatically recovers stale tasks after crash/restart

**Output Example:**

```
[Coordinator] Starting with maxConcurrentBuildTasks=5
[QueueWorker] Starting with concurrency=3
[Metrics] build_tasks=0/5, recording_tasks=0/3, elapsed=0.0s

[Coordinator] Starting BuildTaskRunner #123
[BuildTaskRunner #123] Generating recording tasks...
[BuildTaskRunner #123] Generated 50 recording tasks

[QueueWorker] Starting task #2001
[QueueWorker] Starting task #2002
[QueueWorker] Starting task #2003

[Metrics] build_tasks=1/5, recording_tasks=3/3, elapsed=30.0s
  #123 [arxiv.org] tasks=15+1/50 (32.0%) elapsed=1.5min

[BuildTaskRunner #123] All recording tasks finished
[BuildTaskRunner #123] Published version 2 (Blue-Green deployment)
```

**Sources:** [services/action-builder/README.md:14-27](), [services/action-builder/README.md:255-298](), [services/action-builder/scripts/coordinator.ts:1-82]()

### Mode 2: Manual Task CLI (Development)

```bash
# View task status for all sources
pnpm task:status

# View status for specific source
pnpm task:status 1

# Create 10 tasks for source 1
pnpm task:create 1 10

# Run 2 pending tasks manually
pnpm task:run 1 2

# Clear all tasks for source 1
pnpm task:clear 1
```

**Use Cases:**
- Testing on specific chunks
- Debugging task execution
- Running small batches
- Development without full coordinator

**Sources:** [services/action-builder/README.md:29-43](), [services/action-builder/README.md:91-131]()

### Batch Operations

For processing multiple websites:

```bash
# Crawl multiple sites (requires crawl-sites.txt)
pnpm crawl:batch

# Import crawled data into database
pnpm import:batch

# Retry failed imports
pnpm import:batch -- --retry-from output/batch/import_summary_xxx.json
```

**Configuration File:** `scripts/crawl-sites.txt`

```
# One URL per line
www.example.com
docs.python.org
github.com/actionbook/actionbook
```

**Sources:** [services/action-builder/scripts/crawl-playbook-batch.ts:1-360](), [services/action-builder/scripts/import-playbook-batch.ts:1-434](), [services/action-builder/scripts/crawl-sites.txt.example:1-7]()

## Integration Points

The Action Builder Service integrates with multiple components across the system:

```mermaid
graph TB
    subgraph ActionBuilder["Action Builder Service"]
        Coordinator["Coordinator"]
        BTR["BuildTaskRunner"]
        QW["RecordingTaskQueueWorker"]
        TE["TaskExecutor"]
        AR["ActionRecorder"]
    end
    
    subgraph Browser["Browser Automation (#4)"]
        BA["BrowserAdapter<br/>(interface)"]
        SB["StagehandBrowser<br/>(implementation)"]
        AC["AgentCoreBrowser<br/>(implementation)"]
    end
    
    subgraph AI["AI Integration (#6)"]
        AIC["AIClient<br/>(multi-provider)"]
        SO["SelectorOptimizer<br/>(LLM-based)"]
    end
    
    subgraph Data["Data Layer (#5)"]
        DB["PostgreSQL<br/>(build_tasks,<br/>recording_tasks,<br/>elements, pages)"]
        YAML["YAML Files<br/>(output/sites/)"]
    end
    
    subgraph Tools["Recording Tools (#3.2.3)"]
        RT["RecorderToolExecutor"]
        Nav["navigate"]
        Obs["observe_page"]
        Reg["register_element"]
    end
    
    Coordinator --> DB
    BTR --> DB
    QW --> DB
    
    TE --> AR
    AR --> RT
    AR --> AIC
    
    RT --> BA
    BA --> SB
    BA --> AC
    
    AR --> SO
    SO --> AIC
    
    AR --> DB
    AR --> YAML
```

**Sources:** [services/action-builder/package.json:40-58]()

### Component Dependencies

| Component | Dependencies | Purpose |
|-----------|-------------|---------|
| `Coordinator` | `@actionbookdev/db` | Query/update `build_tasks` |
| `BuildTaskRunner` | `@actionbookdev/db` | Generate/monitor `recording_tasks` |
| `TaskExecutor` | `ActionRecorder` | Execute single recording task |
| `ActionRecorder` | `@actionbookdev/browser`<br/>`AIClient`<br/>`SelectorOptimizer`<br/>`RecorderToolExecutor` | LLM tool loop, browser control, element discovery |
| `RecorderToolExecutor` | `BrowserAdapter` | Tool execution (navigate, observe, register) |

**Sources:** [services/action-builder/src/llm/AIClient.ts:1-544]()

## Error Handling and Recovery

The Action Builder Service implements robust error handling at multiple levels to ensure reliability.

### Failure Recovery Matrix

| Failure Type | Detection Method | Recovery Action | Max Attempts |
|--------------|------------------|-----------------|--------------|
| Task execution error | `TaskExecutor` catches exception | Mark `failed`, auto-retry if `attempt_count < max` | 3 (default) |
| Task timeout | `TaskExecutor` monitors elapsed time | Save partial results, mark `failed`, retry | 3 (default) |
| Stale task (no heartbeat) | `QueueWorker` checks `last_heartbeat` | Reset to `pending` if `attempt_count < max` | 3 (default) |
| Stale build_task | `Coordinator` checks `updated_at` | Re-claim task with priority | No limit |
| Process crash | Restart detection | All stale tasks recovered automatically | No limit |

**Sources:** [services/action-builder/README.md:337-355](), [services/action-builder/README.md:356-365]()

### Partial Success Policy

The Action Builder Service allows **partial success**: a `build_task` completes even if some `recording_tasks` permanently fail (exhaust retry attempts). This design choice ensures that one problematic chunk doesn't block the entire website from being published.

**Completion Condition:**

```
build_task completes when:
  pending_count = 0 AND
  running_count = 0 AND
  retried_count = 0
```

Permanent failures (status=`failed`, attempt_count >= max) do NOT block completion.

**Sources:** [services/action-builder/README.md:337-355]()

### Logging and Observability

All errors are logged to both console (errors/warnings always) and file:

```
logs/action-builder_YYYYMMDDHHmmss.log
```

**LLM Metrics Logging:**

```
[LLM] ✓ | openrouter/anthropic/claude-sonnet-4 | tokens: in=1234, out=567, total=1801 | perf: latency=2345ms, tps=45.2
[LLM] ✗ rate_limit | openrouter/anthropic/claude-sonnet-4 | tokens: in=0, out=0, total=0 | perf: latency=1234ms, tps=0
```

**Sources:** [services/action-builder/src/llm/AIClient.ts:445-471](), [services/action-builder/src/utils/logger.ts:1-155]()

---

# Page: Task Execution Pipeline

# Task Execution Pipeline

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [services/action-builder/.env.example](services/action-builder/.env.example)
- [services/action-builder/README.md](services/action-builder/README.md)
- [services/action-builder/scripts/coordinator.ts](services/action-builder/scripts/coordinator.ts)
- [services/action-builder/src/task-worker/build-task-runner.ts](services/action-builder/src/task-worker/build-task-runner.ts)
- [services/action-builder/src/task-worker/coordinator.ts](services/action-builder/src/task-worker/coordinator.ts)
- [services/action-builder/src/task-worker/recording-task-queue-worker.ts](services/action-builder/src/task-worker/recording-task-queue-worker.ts)
- [services/action-builder/test/coordinator.integration.it.test.ts](services/action-builder/test/coordinator.integration.it.test.ts)
- [services/action-builder/test/task-worker/integration/end-to-end.it.test.ts](services/action-builder/test/task-worker/integration/end-to-end.it.test.ts)

</details>



## Purpose and Scope

The Task Execution Pipeline is the core orchestration system in the Action Builder service that manages concurrent execution of website capability recording. It implements a 3-layer architecture with stateless recovery, automatic retry, and distributed task consumption.

This page covers the task orchestration components (`Coordinator`, `BuildTaskRunner`, `RecordingTaskQueueWorker`) and their lifecycle management. For details on how individual recording tasks discover and register UI elements, see [Action Recording](#3.2.2). For the tool definitions used during recording, see [Recording Tools Reference](#3.2.3).

**Sources:** [services/action-builder/README.md:153-191](), [services/action-builder/src/task-worker/coordinator.ts:1-10]()

---

## Architecture Overview

The Task Execution Pipeline implements a producer-consumer architecture with three distinct layers that coordinate through database state.

### Three-Layer Architecture

```mermaid
graph TB
    subgraph Layer1["Layer 1: Coordinator"]
        Coordinator["Coordinator<br/>(coordinator.ts)"]
    end
    
    subgraph Layer2["Layer 2: Build Task Orchestration"]
        BTR1["BuildTaskRunner #1<br/>(build-task-runner.ts)"]
        BTR2["BuildTaskRunner #2<br/>(build-task-runner.ts)"]
        BTRn["BuildTaskRunner #N<br/>(build-task-runner.ts)"]
    end
    
    subgraph Layer3["Layer 3: Recording Task Execution"]
        QW["RecordingTaskQueueWorker<br/>(recording-task-queue-worker.ts)"]
        TE1["TaskExecutor #1<br/>(task-executor.ts)"]
        TE2["TaskExecutor #2<br/>(task-executor.ts)"]
        TEm["TaskExecutor #M<br/>(task-executor.ts)"]
    end
    
    subgraph Database["Database (State Store)"]
        BuildTasksTable["build_tasks table<br/>(stage, stage_status, updated_at)"]
        RecordingTasksTable["recording_tasks table<br/>(status, last_heartbeat, attempt_count)"]
    end
    
    Coordinator -->|"Claims build_tasks<br/>Max N concurrent"| BuildTasksTable
    Coordinator -->|"Spawns & monitors"| BTR1
    Coordinator -->|"Spawns & monitors"| BTR2
    Coordinator -->|"Spawns & monitors"| BTRn
    
    BTR1 -->|"Generates recording_tasks<br/>Polls status"| RecordingTasksTable
    BTR2 -->|"Generates recording_tasks<br/>Polls status"| RecordingTasksTable
    BTRn -->|"Generates recording_tasks<br/>Polls status"| RecordingTasksTable
    
    QW -->|"Claims pending tasks<br/>Max M concurrent"| RecordingTasksTable
    QW -->|"Executes"| TE1
    QW -->|"Executes"| TE2
    QW -->|"Executes"| TEm
    
    TE1 -->|"Updates status<br/>heartbeat"| RecordingTasksTable
    TE2 -->|"Updates status<br/>heartbeat"| RecordingTasksTable
    TEm -->|"Updates status<br/>heartbeat"| RecordingTasksTable
    
    BTR1 -.->|"Heartbeat<br/>(updated_at)"| BuildTasksTable
    BTR2 -.->|"Heartbeat<br/>(updated_at)"| BuildTasksTable
    BTRn -.->|"Heartbeat<br/>(updated_at)"| BuildTasksTable
```

**Responsibilities by Layer:**

| Layer | Component | Responsibilities |
|-------|-----------|------------------|
| Layer 1 | `Coordinator` | Claims `build_tasks`, spawns `BuildTaskRunner` instances, enforces concurrency limit (max N build_tasks), monitors metrics |
| Layer 2 | `BuildTaskRunner` | Generates `recording_tasks` for one build, polls task status, retries failed tasks, updates build status, publishes versions |
| Layer 3 | `RecordingTaskQueueWorker` | Claims pending `recording_tasks` (global queue), spawns `TaskExecutor` instances, enforces concurrency limit (max M tasks), recovers stale tasks |

**Sources:** [services/action-builder/README.md:159-191](), [services/action-builder/src/task-worker/coordinator.ts:1-10](), [services/action-builder/src/task-worker/build-task-runner.ts:1-15](), [services/action-builder/src/task-worker/recording-task-queue-worker.ts:1-16]()

---

## Task Lifecycle

### Build Task State Transitions

The `build_tasks` table tracks the overall build pipeline with two-dimensional state (`stage` and `stage_status`):

```mermaid
stateDiagram-v2
    [*] --> knowledge_build_completed: "Created by<br/>knowledge-builder"
    
    knowledge_build_completed --> action_build_running: "Coordinator.claimBuildTask()<br/>(UPDATE + FOR UPDATE SKIP LOCKED)"
    
    action_build_running --> action_build_running: "BuildTaskRunner heartbeat<br/>(every 5s, updates updated_at)"
    
    action_build_running --> action_build_completed: "BuildTaskRunner.completeBuildTask()<br/>(all recording_tasks finished)"
    
    action_build_running --> action_build_error: "BuildTaskRunner.failBuildTask()<br/>(exception during execution)"
    
    action_build_running --> action_build_running: "Stale recovery<br/>(Coordinator detects updated_at timeout)"
    
    action_build_completed --> [*]: "Version published<br/>(Blue-Green deployment)"
    
    action_build_error --> [*]: "Manual intervention<br/>required"
    
    note right of knowledge_build_completed
        stage=knowledge_build
        stage_status=completed
    end note
    
    note right of action_build_running
        stage=action_build
        stage_status=running
        updated_at refreshed every 5s
    end note
    
    note right of action_build_completed
        stage=action_build
        stage_status=completed
        source_version.status = active
    end note
```

**Key Methods:**
- `Coordinator.claimBuildTask()` - Atomically claims a build_task using `FOR UPDATE SKIP LOCKED` [services/action-builder/src/task-worker/coordinator.ts:163-206]()
- `BuildTaskRunner.run()` - Main lifecycle execution [services/action-builder/src/task-worker/build-task-runner.ts:59-114]()
- `BuildTaskRunner.completeBuildTask()` - Marks build complete [services/action-builder/src/task-worker/build-task-runner.ts:376-386]()
- `BuildTaskRunner.publishVersion()` - Blue-Green version deployment [services/action-builder/src/task-worker/build-task-runner.ts:389-459]()

**Sources:** [services/action-builder/src/task-worker/coordinator.ts:159-206](), [services/action-builder/src/task-worker/build-task-runner.ts:59-114]()

### Recording Task State Transitions

The `recording_tasks` table tracks individual recording executions with status field and retry logic:

```mermaid
stateDiagram-v2
    [*] --> pending: "BuildTaskRunner.generateRecordingTasks()<br/>(bulk insert with ON CONFLICT)"
    
    pending --> running: "QueueWorker.claimTask()<br/>(UPDATE + FOR UPDATE SKIP LOCKED)"
    
    running --> running: "QueueWorker heartbeat<br/>(every 5s, updates last_heartbeat)"
    
    running --> completed: "TaskExecutor.execute() success<br/>(attempt_count++)"
    
    running --> failed: "TaskExecutor.execute() error<br/>(attempt_count++)"
    
    failed --> pending: "BuildTaskRunner.retryFailedTasks()<br/>(if attempt_count < max_attempts)"
    
    failed --> failed: "Retry exhausted<br/>(attempt_count >= max_attempts)"
    
    running --> pending: "Stale recovery<br/>(QueueWorker.recoverStaleTasks())<br/>if attempt_count < max"
    
    running --> failed: "Stale recovery<br/>(QueueWorker.recoverStaleTasks())<br/>if attempt_count >= max"
    
    completed --> [*]: "Success"
    
    failed --> [*]: "Permanent failure"
    
    note right of pending
        status=pending
        attempt_count=0
    end note
    
    note right of running
        status=running
        last_heartbeat updated every 5s
        started_at set on claim
    end note
    
    note right of completed
        status=completed
        completed_at set
        progress=100
    end note
    
    note right of failed
        status=failed
        error_message set
        May retry if attempts < max
    end note
```

**Key Methods:**
- `BuildTaskRunner.generateRecordingTasks()` - Creates tasks from chunks [services/action-builder/src/task-worker/build-task-runner.ts:154-226]()
- `RecordingTaskQueueWorker.claimTask()` - Atomically claims pending task [services/action-builder/src/task-worker/recording-task-queue-worker.ts:201-245]()
- `BuildTaskRunner.retryFailedTasks()` - Resets failed tasks to pending [services/action-builder/src/task-worker/build-task-runner.ts:298-336]()
- `RecordingTaskQueueWorker.recoverStaleTasks()` - Recovers tasks with stale heartbeat [services/action-builder/src/task-worker/recording-task-queue-worker.ts:304-352]()

**Sources:** [services/action-builder/src/task-worker/build-task-runner.ts:154-226](), [services/action-builder/src/task-worker/recording-task-queue-worker.ts:201-245](), [services/action-builder/src/task-worker/recording-task-queue-worker.ts:304-352]()

---

## Components

### Coordinator

The `Coordinator` class is the top-level orchestrator that manages the entire pipeline.

**Class Definition:**
```typescript
class Coordinator {
  constructor(db: Database, config: CoordinatorConfig)
  async start(): Promise<void>
  async stop(timeoutMs?: number): Promise<void>
  getStatus(): CoordinatorStatus
}
```

**Main Loop Execution Flow:**

```mermaid
sequenceDiagram
    participant Main as "Coordinator.mainLoop()"
    participant DB as "Database"
    participant BTR as "BuildTaskRunner"
    participant QW as "QueueWorker"
    
    Main->>QW: start() (background)
    Note over QW: Runs independently
    
    loop "Every buildTaskPollIntervalSeconds (default 5s)"
        Main->>Main: cleanupCompletedTasks()
        
        loop "While slots available (< maxConcurrentBuildTasks)"
            Main->>DB: claimBuildTask()
            Note over DB: FOR UPDATE SKIP LOCKED<br/>Prioritize stale tasks
            
            alt Build task available
                DB-->>Main: build_task (id, sourceId, etc)
                Main->>BTR: new BuildTaskRunner(buildTaskId)
                Main->>BTR: run() (non-blocking)
                Note over BTR: Runs independently
            else No tasks available
                DB-->>Main: null
                Main->>Main: break loop
            end
        end
        
        Main->>Main: sleep(pollInterval)
    end
```

**Configuration Options:**

| Parameter | Default | Description |
|-----------|---------|-------------|
| `maxConcurrentBuildTasks` | 5 | Max number of simultaneous build_tasks (different sources) |
| `buildTaskPollIntervalSeconds` | 5 | How often to check for new build_tasks |
| `buildTaskStaleTimeoutMinutes` | 15 | Stale threshold for `action_build/running` tasks (crash recovery) |
| `buildTaskRunner` | `{}` | Config passed to `BuildTaskRunner` instances |
| `queueWorker` | `{}` | Config for the global `RecordingTaskQueueWorker` |

**Graceful Shutdown:**
The `stop()` method implements graceful shutdown with timeout:
1. Stops accepting new build_tasks (`running = false`)
2. Stops `RecordingTaskQueueWorker` (waits for running tasks)
3. Waits for all `BuildTaskRunner` instances to complete
4. Enforces timeout to prevent indefinite waiting

**Sources:** [services/action-builder/src/task-worker/coordinator.ts:39-123](), [services/action-builder/src/task-worker/coordinator.ts:125-157](), [scripts/coordinator.ts:12-76]()

### BuildTaskRunner

The `BuildTaskRunner` class orchestrates a single build_task lifecycle.

**Class Definition:**
```typescript
class BuildTaskRunner {
  constructor(db: Database, buildTaskId: number, config: BuildTaskRunnerConfig)
  async run(): Promise<void>
  stop(): void
}
```

**Execution Flow:**

```mermaid
sequenceDiagram
    participant BTR as "BuildTaskRunner"
    participant DB as "Database"
    
    BTR->>DB: getBuildTask(buildTaskId)
    DB-->>BTR: BuildTaskInfo
    
    BTR->>DB: generateRecordingTasks()
    Note over DB: Bulk INSERT with<br/>ON CONFLICT DO UPDATE<br/>(idempotent)
    DB-->>BTR: tasksCreated count
    
    alt No tasks generated
        BTR->>DB: completeBuildTask()
        Note over BTR: Early exit
    end
    
    BTR->>BTR: startHeartbeat()
    Note over BTR: setInterval(5000ms)<br/>updates build_tasks.updated_at
    
    loop "Until all tasks finished"
        BTR->>DB: getRecordingTasksStatus()
        DB-->>BTR: {pending, running, completed, failed}
        
        BTR->>DB: retryFailedTasks()
        Note over DB: Reset failed tasks<br/>if attempt_count < max_attempts
        
        alt "pending=0 AND running=0 AND retriedCount=0"
            BTR->>BTR: break loop
        end
        
        BTR->>BTR: sleep(checkIntervalSeconds)
    end
    
    BTR->>BTR: stopHeartbeat()
    
    BTR->>DB: publishVersion()
    Note over DB: Blue-Green deployment:<br/>1. Archive current active<br/>2. Set new version active
    
    BTR->>DB: completeBuildTask()
    Note over DB: stage_status = completed<br/>action_completed_at = NOW()
```

**Recording Task Generation:**
The `generateRecordingTasks()` method uses an idempotent UPSERT pattern [services/action-builder/src/task-worker/build-task-runner.ts:154-226]():
- Queries all chunks for the `source_version_id`
- Creates one `recording_task` per chunk
- Uses `ON CONFLICT DO UPDATE` with target `(chunk_id, build_task_id)`
- Only resets tasks in `pending/running` state (preserves `completed/failed`)

**Polling and Retry:**
The polling loop [services/action-builder/src/task-worker/build-task-runner.ts:231-263]():
1. Queries task status counts grouped by status
2. Retries failed tasks (if `attempt_count < max_attempts`)
3. Waits until `pending=0 AND running=0 AND retriedCount=0`
4. **Important:** Permanent failures (`attempt_count >= max_attempts`) do NOT block completion

**Sources:** [services/action-builder/src/task-worker/build-task-runner.ts:39-114](), [services/action-builder/src/task-worker/build-task-runner.ts:154-226](), [services/action-builder/src/task-worker/build-task-runner.ts:231-263]()

### RecordingTaskQueueWorker

The `RecordingTaskQueueWorker` (also called `QueueWorker`) is the global consumer that executes recording_tasks from all build_tasks.

**Class Definition:**
```typescript
class RecordingTaskQueueWorker {
  constructor(db: Database, config: RecordingTaskQueueWorkerConfig)
  async start(): Promise<void>
  async stop(timeoutMs?: number): Promise<void>
  getStatus(): WorkerStatus
}
```

**Main Loop Execution:**

```mermaid
sequenceDiagram
    participant QW as "QueueWorker.mainLoop()"
    participant DB as "Database"
    participant TE as "TaskExecutor"
    
    QW->>DB: recoverStaleTasks()
    Note over DB: Find running tasks with<br/>last_heartbeat timeout<br/>Reset to pending or failed
    
    loop "While running"
        loop "Fill slots (< concurrency limit)"
            QW->>DB: claimTask()
            Note over DB: UPDATE recording_tasks<br/>SET status=running<br/>WHERE id = (<br/>  SELECT ... WHERE status=pending<br/>  ORDER BY updated_at DESC<br/>  FOR UPDATE SKIP LOCKED<br/>)
            
            alt Task claimed
                DB-->>QW: RecordingTask
                QW->>TE: new TaskExecutor()
                QW->>TE: execute(task) (non-blocking)
                Note over TE: ActionRecorder + Browser
                QW->>QW: setInterval(heartbeat, 5000ms)
            else No tasks available
                DB-->>QW: null
                QW->>QW: break loop
            end
        end
        
        alt "runningTasks.size === 0"
            QW->>QW: sleep(idleWaitMs)
        else
            QW->>QW: Promise.race(runningTasks)
            Note over QW: Wait for any task to complete
        end
        
        QW->>DB: recoverStaleTasks() (periodic)
    end
```

**Task Claiming:**
The `claimTask()` method implements atomic claiming [services/action-builder/src/task-worker/recording-task-queue-worker.ts:201-245]():
- Uses `FOR UPDATE SKIP LOCKED` to avoid contention
- Orders by `updated_at DESC` to prioritize recently retried tasks
- Atomically updates status to `running` and sets `started_at`, `last_heartbeat`

**Concurrency Control:**
- Maintains a `Map<taskId, RunningTask>` of executing tasks
- Each `RunningTask` includes: executor instance, heartbeat timer, promise
- Enforces max concurrent limit before claiming new tasks
- Uses `Promise.race()` to wait for any task completion

**Sources:** [services/action-builder/src/task-worker/recording-task-queue-worker.ts:44-86](), [services/action-builder/src/task-worker/recording-task-queue-worker.ts:154-195](), [services/action-builder/src/task-worker/recording-task-queue-worker.ts:201-245]()

### TaskExecutor

The `TaskExecutor` class wraps the execution of a single recording_task. It is responsible for:
- Initializing browser and ActionRecorder
- Executing the recording loop (see [Action Recording](#3.2.2))
- Updating task status and progress
- Handling errors and timeouts

**Note:** The actual implementation of `TaskExecutor` is not included in the provided files, but is referenced throughout the codebase. It serves as the bridge between task orchestration and action recording.

**Sources:** [services/action-builder/src/task-worker/recording-task-queue-worker.ts:250-285]()

---

## Concurrency Control

The pipeline implements concurrency control at two levels:

### Build Task Concurrency

| Parameter | Environment Variable | Default | Description |
|-----------|---------------------|---------|-------------|
| `maxConcurrentBuildTasks` | `ACTION_BUILDER_BUILD_TASK_CONCURRENCY` | 5 | Max number of different sources processed simultaneously |

**Mechanism:**
- `Coordinator` maintains `Map<buildTaskId, RunningBuildTask>`
- Before claiming new tasks, checks `runningBuildTasks.size < maxConcurrentBuildTasks`
- Each `BuildTaskRunner` runs independently in background

**Why Limit:** Different sources may have different characteristics (page count, complexity). Limiting concurrent builds prevents resource exhaustion.

### Recording Task Concurrency

| Parameter | Environment Variable | Default | Description |
|-----------|---------------------|---------|-------------|
| `concurrency` | `ACTION_BUILDER_RECORDING_TASK_CONCURRENCY` | 3 | Max number of browser instances running simultaneously (global queue) |

**Mechanism:**
- `RecordingTaskQueueWorker` maintains `Map<taskId, RunningTask>`
- Before claiming new tasks, checks `runningTasks.size < concurrency`
- Each `TaskExecutor` runs in a separate browser context

**Why Limit:** Each recording task launches a browser instance, which consumes significant CPU and memory. The global concurrency limit prevents system overload.

### Atomic Task Claiming

Both `build_tasks` and `recording_tasks` use PostgreSQL's `FOR UPDATE SKIP LOCKED` to enable concurrent claiming without conflicts:

```sql
UPDATE recording_tasks
SET status = 'running', started_at = NOW(), last_heartbeat = NOW()
WHERE id = (
  SELECT id FROM recording_tasks
  WHERE status = 'pending'
  ORDER BY updated_at DESC, id
  LIMIT 1
  FOR UPDATE SKIP LOCKED  -- Skip locked rows, prevents waiting
)
RETURNING *
```

This pattern ensures:
- Multiple workers can claim tasks concurrently
- No worker ever claims the same task twice
- No blocking waits (skip locked rows instead of waiting)

**Sources:** [services/action-builder/src/task-worker/coordinator.ts:163-206](), [services/action-builder/src/task-worker/recording-task-queue-worker.ts:201-245](), [services/action-builder/.env.example:93-116]()

---

## Heartbeat and Monitoring

### Heartbeat Mechanism

The system uses different heartbeat strategies for different task types:

| Task Type | Field | Update Interval | Timeout | Updated By |
|-----------|-------|-----------------|---------|------------|
| `build_tasks` | `updated_at` | 5 seconds | 15 minutes | `BuildTaskRunner.updateHeartbeat()` |
| `recording_tasks` | `last_heartbeat` | 5 seconds | 15 minutes | `RecordingTaskQueueWorker.updateTaskHeartbeat()` |

**Implementation:**

```typescript
// BuildTaskRunner heartbeat (services/action-builder/src/task-worker/build-task-runner.ts:341-372)
private startHeartbeat(): void {
  this.heartbeatTimer = setInterval(() => {
    this.updateHeartbeat().catch(console.error);
  }, this.config.heartbeatIntervalMs); // Default 5000ms
}

private async updateHeartbeat(): Promise<void> {
  await this.db
    .update(buildTasks)
    .set({ updatedAt: new Date() })
    .where(eq(buildTasks.id, this.buildTaskId));
}
```

```typescript
// QueueWorker heartbeat (services/action-builder/src/task-worker/recording-task-queue-worker.ts:250-298)
const heartbeatTimer = setInterval(() => {
  this.updateTaskHeartbeat(task.id).catch(console.error);
}, this.config.heartbeatIntervalMs); // Default 5000ms

private async updateTaskHeartbeat(taskId: number): Promise<void> {
  await this.db
    .update(recordingTasks)
    .set({ lastHeartbeat: new Date(), updatedAt: new Date() })
    .where(eq(recordingTasks.id, taskId));
}
```

### Metrics Output

The `Coordinator` outputs metrics every 30 seconds [services/action-builder/src/task-worker/coordinator.ts:250-316]():

```
[Metrics] build_tasks=2/5, recording_tasks=3/3, elapsed=30.0s
  #123 [arxiv.org] tasks=15+1/50 (32.0%) elapsed=1.5min
  #124 [github.com] tasks=8+0/25 (32.0%) elapsed=0.8min
```

**Metrics Format:**
- `build_tasks=X/Y`: X running builds out of Y max concurrent
- `recording_tasks=X/Y`: X running recordings out of Y concurrency limit
- Per build details:
  - `#123`: build_task ID
  - `[arxiv.org]`: source name
  - `tasks=15+1/50`: 15 completed + 1 failed / 50 total
  - `(32.0%)`: completion percentage
  - `elapsed=1.5min`: time since `action_started_at`

**Sources:** [services/action-builder/src/task-worker/build-task-runner.ts:341-372](), [services/action-builder/src/task-worker/recording-task-queue-worker.ts:250-298](), [services/action-builder/src/task-worker/coordinator.ts:250-316]()

---

## Failure Handling

### Retry Logic

The system implements multi-level retry with attempt counting:

**Recording Task Retry:**

```mermaid
graph TB
    Start["recording_task<br/>status=pending<br/>attempt_count=0"]
    
    Claim["QueueWorker.claimTask()<br/>status → running"]
    
    Execute["TaskExecutor.execute()"]
    
    Success["status → completed<br/>attempt_count++"]
    
    Failed["status → failed<br/>attempt_count++<br/>error_message set"]
    
    CheckAttempts{"attempt_count<br/>< max_attempts?"}
    
    Retry["BuildTaskRunner.retryFailedTasks()<br/>status → pending<br/>(no increment)"]
    
    Permanent["status = failed<br/>(permanent)"]
    
    Start --> Claim
    Claim --> Execute
    Execute -->|"Success"| Success
    Execute -->|"Error"| Failed
    Failed --> CheckAttempts
    CheckAttempts -->|"Yes"| Retry
    CheckAttempts -->|"No"| Permanent
    Retry --> Claim
    Success --> End["✓"]
    Permanent --> End
```

**Key Points:**
- `attempt_count` increments when `TaskExecutor` starts execution (whether success or failure)
- `BuildTaskRunner.retryFailedTasks()` resets `failed` → `pending` without incrementing attempts
- Only tasks with `attempt_count < max_attempts` are retriable
- Permanent failures do NOT block build_task completion

**Sources:** [services/action-builder/src/task-worker/build-task-runner.ts:298-336](), [services/action-builder/README.md:336-354]()

### Stale Detection and Recovery

Stale detection handles processes that crash or hang without updating heartbeat:

**Build Task Stale Recovery:**

Performed by `Coordinator.claimBuildTask()` [services/action-builder/src/task-worker/coordinator.ts:163-206]():

```sql
UPDATE build_tasks
SET stage = 'action_build', stage_status = 'running',
    action_started_at = COALESCE(action_started_at, NOW()),
    updated_at = NOW()
WHERE id = (
  SELECT id FROM build_tasks
  WHERE
    (stage = 'knowledge_build' AND stage_status = 'completed')  -- New tasks
    OR
    (stage = 'action_build' AND stage_status = 'running' AND updated_at < staleThreshold)  -- Stale tasks
  ORDER BY
    CASE WHEN stage = 'action_build' THEN 0 ELSE 1 END,  -- Prioritize stale recovery
    id
  LIMIT 1
  FOR UPDATE SKIP LOCKED
)
RETURNING id
```

**Recording Task Stale Recovery:**

Performed by `RecordingTaskQueueWorker.recoverStaleTasks()` [services/action-builder/src/task-worker/recording-task-queue-worker.ts:304-352]():

```sql
WITH stale_tasks AS (
  SELECT
    id,
    attempt_count,
    CASE
      WHEN attempt_count < max_attempts THEN 'pending'
      ELSE 'failed'
    END AS new_status
  FROM recording_tasks
  WHERE status = 'running' AND last_heartbeat < staleThreshold
)
UPDATE recording_tasks
SET
  status = stale_tasks.new_status,
  attempt_count = CASE
    WHEN stale_tasks.new_status = 'pending' THEN attempt_count + 1
    ELSE attempt_count
  END,
  error_message = CASE
    WHEN stale_tasks.new_status = 'failed' THEN 'Task stale: max attempts reached'
    ELSE NULL
  END
FROM stale_tasks
WHERE recording_tasks.id = stale_tasks.id
```

**Stale Recovery Flow:**

| Scenario | Detection | Action | Result |
|----------|-----------|--------|--------|
| `build_task` stale | `updated_at < threshold` (15min) | Re-claim with priority | `BuildTaskRunner` regenerates tasks (idempotent UPSERT) |
| `recording_task` stale (retriable) | `last_heartbeat < threshold` (15min) AND `attempt_count < max` | Reset to `pending`, increment `attempt_count` | Task re-queued for execution |
| `recording_task` stale (exhausted) | `last_heartbeat < threshold` AND `attempt_count >= max` | Mark as `failed` | Permanent failure, will not retry |

**Stateless Recovery After Crash:**

When the system crashes and restarts:
1. `Coordinator` starts and begins claiming build_tasks
2. Stale `action_build/running` tasks are detected and re-claimed (prioritized over new tasks)
3. `RecordingTaskQueueWorker` runs `recoverStaleTasks()` on startup
4. Stale `running` recording_tasks are reset to `pending` or `failed` based on attempt count
5. Normal execution resumes - no progress is lost

**Sources:** [services/action-builder/src/task-worker/coordinator.ts:163-206](), [services/action-builder/src/task-worker/recording-task-queue-worker.ts:304-352](), [services/action-builder/README.md:356-365]()

---

## Configuration

### Environment Variables

All configuration is controlled via environment variables with sensible defaults:

**Coordinator Configuration:**

| Variable | Default | Description |
|----------|---------|-------------|
| `ACTION_BUILDER_BUILD_TASK_CONCURRENCY` | `5` | Max concurrent build_tasks (different sources) |
| `ACTION_BUILDER_BUILD_TASK_POLL_INTERVAL_SECONDS` | `5` | Build task polling interval |
| `ACTION_BUILDER_BUILD_TASK_STALE_TIMEOUT_MINUTES` | `15` | Stale build_task timeout for crash recovery |

**BuildTaskRunner Configuration:**

| Variable | Default | Description |
|----------|---------|-------------|
| `ACTION_BUILDER_CHECK_INTERVAL_SECONDS` | `5` | Status check interval (how often to poll recording_tasks) |
| `ACTION_BUILDER_MAX_ATTEMPTS` | `3` | Max retry attempts for failed tasks |

**RecordingTaskQueueWorker Configuration:**

| Variable | Default | Description |
|----------|---------|-------------|
| `ACTION_BUILDER_RECORDING_TASK_CONCURRENCY` | `3` | Max concurrent recording_tasks (browser instances) |
| `ACTION_BUILDER_STALE_TIMEOUT_MINUTES` | `15` | Stale recording_task timeout |
| `ACTION_BUILDER_TASK_TIMEOUT_MINUTES` | `10` | Single task execution timeout |

**Recording Task Settings:**

| Variable | Default | Description |
|----------|---------|-------------|
| `ACTION_BUILDER_HEADLESS` | `true` | Run browser in headless mode |
| `ACTION_BUILDER_MAX_TURNS` | `30` | Maximum LLM turns per recording task |
| `OUTPUT_DIR` | `./output` | Output directory for generated YAML files |

**Logging:**

| Variable | Default | Description |
|----------|---------|-------------|
| `ACTION_BUILDER_QUIET` | `true` | Quiet mode: only task-level logs to console, detailed logs to file |

### Starting the Coordinator

**Command line:**
```bash
# Start with default settings
pnpm coordinator

# Development mode with auto-reload (quiet mode)
pnpm dev

# Verbose mode (all logs to console)
pnpm coordinator:verbose
pnpm dev:verbose
```

**Programmatic usage:**
```typescript
import { getDb } from '@actionbookdev/db';
import { Coordinator } from '@actionbookdev/action-builder/task-worker/coordinator';

const db = getDb();
const coordinator = new Coordinator(db, {
  maxConcurrentBuildTasks: 5,
  buildTaskPollIntervalSeconds: 5,
  buildTaskStaleTimeoutMinutes: 15,
  queueWorker: {
    concurrency: 3,
    staleTimeoutMinutes: 15,
    taskTimeoutMinutes: 10,
    databaseUrl: process.env.DATABASE_URL!,
    headless: true,
    outputDir: './output',
    maxAttempts: 3,
    maxTurns: 30,
  },
  buildTaskRunner: {
    checkIntervalSeconds: 5,
    maxAttempts: 3,
  },
});

// Start coordinator
await coordinator.start();

// Graceful shutdown
process.on('SIGINT', async () => {
  await coordinator.stop(60000); // 60 second timeout
  process.exit(0);
});
```

**Sources:** [services/action-builder/.env.example:93-142](), [services/action-builder/scripts/coordinator.ts:12-76](), [services/action-builder/README.md:205-232]()

---

## Summary

The Task Execution Pipeline provides robust, concurrent, stateless orchestration for website capability recording:

**Key Design Principles:**
1. **3-Layer Architecture** - Separation of concerns (coordination, per-build orchestration, execution)
2. **Database as State Store** - All state in database enables stateless recovery
3. **Atomic Operations** - `FOR UPDATE SKIP LOCKED` prevents conflicts
4. **Heartbeat Monitoring** - Detect and recover from crashes/hangs
5. **Graceful Degradation** - Partial failures don't block completion

**Fault Tolerance:**
- Automatic retry with attempt limiting
- Stale task detection and recovery
- Crash recovery without state loss
- Graceful shutdown with timeout

**Scalability:**
- Configurable concurrency at multiple levels
- Independent worker processes can be scaled horizontally
- Global task queue enables efficient resource utilization

For details on how recording tasks discover and register UI elements, see [Action Recording](#3.2.2).

**Sources:** [services/action-builder/README.md:153-203](), [services/action-builder/README.md:336-365]()

---

# Page: Action Recording

# Action Recording

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [services/action-builder/scripts/playbook-record.ts](services/action-builder/scripts/playbook-record.ts)
- [services/action-builder/src/ActionBuilder.ts](services/action-builder/src/ActionBuilder.ts)
- [services/action-builder/src/llm/prompts/capability-recorder.ts](services/action-builder/src/llm/prompts/capability-recorder.ts)
- [services/action-builder/src/recorder/ActionRecorder.ts](services/action-builder/src/recorder/ActionRecorder.ts)
- [services/action-builder/src/recorder/RecorderToolExecutor.ts](services/action-builder/src/recorder/RecorderToolExecutor.ts)
- [services/action-builder/src/task-worker/task-executor.ts](services/action-builder/src/task-worker/task-executor.ts)
- [services/action-builder/src/types/config.ts](services/action-builder/src/types/config.ts)
- [services/action-builder/src/validator/SelectorValidator.ts](services/action-builder/src/validator/SelectorValidator.ts)
- [services/action-builder/test/ActionBuilder.ut.test.ts](services/action-builder/test/ActionBuilder.ut.test.ts)
- [services/action-builder/test/browser/xpath-optimizer.ut.test.ts](services/action-builder/test/browser/xpath-optimizer.ut.test.ts)
- [services/action-builder/test/task-worker/task-executor.ut.test.ts](services/action-builder/test/task-worker/task-executor.ut.test.ts)
- [services/action-builder/test/validator/SelectorValidator.ut.test.ts](services/action-builder/test/validator/SelectorValidator.ut.test.ts)

</details>



## Purpose and Scope

This page documents how the **ActionRecorder** executes multi-turn LLM conversations to discover and register UI elements on web pages. It covers the recording loop architecture, tool execution flow, element discovery mechanisms, and multi-selector extraction strategies.

For information about the overall task execution pipeline (Coordinator, BuildTaskRunner, QueueWorker), see [Task Execution Pipeline](#3.2.1). For detailed documentation of individual recorder tools and their parameters, see [Recording Tools Reference](#3.2.3).

---

## Architecture Overview

The action recording system consists of four primary components that work together to discover and register UI capabilities:

**Component Interaction Diagram**

```mermaid
graph TB
    ActionRecorder["ActionRecorder"]
    RecorderToolExecutor["RecorderToolExecutor"]
    AIClient["AIClient"]
    Browser["BrowserAdapter"]
    YamlWriter["YamlWriter"]
    DbWriter["DbWriter"]
    SelectorOptimizer["SelectorOptimizer"]
    
    ActionRecorder --> RecorderToolExecutor
    ActionRecorder --> AIClient
    ActionRecorder --> YamlWriter
    ActionRecorder --> DbWriter
    ActionRecorder --> SelectorOptimizer
    
    RecorderToolExecutor --> Browser
    
    subgraph "State Management"
        ActionRecorder --> siteCapability["siteCapability: SiteCapability"]
        ActionRecorder --> discoveredElements["discoveredElements: Map"]
        ActionRecorder --> visitedUrls["visitedUrls: Set"]
        ActionRecorder --> currentPageType["currentPageType: string"]
    end
    
    subgraph "Recording Lifecycle"
        record["record(scenario, systemPrompt, userPrompt)"]
        multiTurnLoop["Multi-turn LLM Loop (max 30 turns)"]
        executeTool["executeToolWithRetry()"]
        registerElement["registerElement(element)"]
        optimize["optimizeAndUpdateSelectors()"]
        save["saveToYamlAndDb()"]
        
        record --> multiTurnLoop
        multiTurnLoop --> executeTool
        executeTool --> registerElement
        multiTurnLoop --> optimize
        optimize --> save
    end
```

**Sources:** [services/action-builder/src/recorder/ActionRecorder.ts:1-152](), [services/action-builder/src/recorder/RecorderToolExecutor.ts:1-68]()

### Core Classes

| Class | Location | Responsibility |
|-------|----------|----------------|
| `ActionRecorder` | [services/action-builder/src/recorder/ActionRecorder.ts:31-32]() | Orchestrates multi-turn LLM loop, manages recording state, coordinates tool execution |
| `RecorderToolExecutor` | [services/action-builder/src/recorder/RecorderToolExecutor.ts:49-67]() | Dispatches tool calls to browser operations, registers discovered elements |
| `AIClient` | [services/action-builder/src/llm/AIClient.ts]() | Manages LLM communication, handles tool calling, tracks token usage |
| `BrowserAdapter` | Interface in `@actionbookdev/browser` | Abstracts browser operations (navigate, observe, act) |

**Sources:** [services/action-builder/src/recorder/ActionRecorder.ts:31-77]()

---

## Recording Flow

The recording process follows a multi-turn conversational loop where the LLM uses tools to discover and register elements. Each turn represents one LLM response that may contain multiple tool calls.

**Multi-Turn Recording Loop**

```mermaid
sequenceDiagram
    participant AB as ActionBuilder
    participant AR as ActionRecorder
    participant AI as AIClient
    participant TE as RecorderToolExecutor
    participant Browser as BrowserAdapter
    participant DB as DbWriter

    AB->>AR: record(scenario, systemPrompt, userPrompt)
    AR->>AR: Initialize state (siteCapability, visitedUrls)
    AR->>AI: chat([systemPrompt, userPrompt], tools)
    
    loop Multi-turn (max 30 turns)
        AI->>AI: LLM generates response with tool_calls
        AI-->>AR: response with tool_calls[]
        
        loop For each tool_call
            AR->>AR: checkTermination()
            alt Termination condition met
                AR->>AR: Break loop
            end
            
            AR->>AR: executeToolWithRetry(toolName, args)
            AR->>TE: execute(toolName, args)
            
            alt Tool: navigate
                TE->>TE: onNavigate(url) - check external/visited
                alt URL is valid
                    TE->>Browser: navigate(url)
                    TE->>Browser: autoClosePopups()
                end
            else Tool: observe_page
                TE->>Browser: observe(focus, timeout)
                Browser-->>TE: ObserveResultItem[]
            else Tool: register_element
                TE->>Browser: getElementAttributesFromXPath(xpath)
                Browser-->>TE: {id, dataTestId, css, ariaLabel, ...}
                TE->>TE: extractMultipleSelectors()
                TE->>AR: registerElement(elementCapability)
                AR->>DB: Save to recording_tasks_steps
            else Tool: interact
                TE->>Browser: act(instruction)
                TE->>AR: registerElement(elementCapability)
            else Tool: set_page_context
                TE->>AR: Update currentPageType
            end
            
            TE-->>AR: {output, content}
            AR->>AR: recordStep(tool, input, output, status)
            AR->>AR: Emit StepEvent callback
        end
        
        AR->>AR: Build tool_results for next turn
        AR->>AI: chat([...messages, assistant, tool_results], tools)
    end
    
    AR->>AR: optimizeAndUpdateSelectors()
    AR->>AR: saveToYamlAndDb()
    AR-->>AB: RecordResult
```

**Sources:** [services/action-builder/src/recorder/ActionRecorder.ts:755-1100](), [services/action-builder/src/ActionBuilder.ts:410-483]()

### Recording Loop Details

The recording loop in `ActionRecorder.record()` follows these steps:

1. **Initialize Conversation**: Start with system prompt and user prompt, passing available tools
2. **LLM Response**: Receive response with tool calls (may contain 1-15+ tool calls per turn)
3. **Tool Execution**: Execute each tool call sequentially with retry logic
4. **State Updates**: Update `siteCapability`, `discoveredElements`, `visitedUrls`, `currentPageType`
5. **Step Recording**: Record each step to database for debugging and observability
6. **Termination Check**: Check termination conditions after each tool execution
7. **Next Turn**: Send tool results back to LLM for next decision

**Sources:** [services/action-builder/src/recorder/ActionRecorder.ts:755-942]()

---

## Tool Execution Flow

Tools are executed through `RecorderToolExecutor`, which dispatches to browser operations and manages state updates.

**Tool Execution Architecture**

```mermaid
graph TB
    subgraph "RecorderToolExecutor.execute()"
        dispatch["Tool Dispatcher"]
        navigate["navigate(url)"]
        observe["observe_page(focus)"]
        register["register_element(...)"]
        interact["interact(element_id, action)"]
        setContext["set_page_context(page_type)"]
        scroll["scroll/scroll_to_bottom"]
        wait["wait(seconds)"]
        goBack["go_back()"]
    end
    
    dispatch --> navigate
    dispatch --> observe
    dispatch --> register
    dispatch --> interact
    dispatch --> setContext
    dispatch --> scroll
    dispatch --> wait
    dispatch --> goBack
    
    navigate --> onNavigateCheck["onNavigate() - Check external/visited"]
    onNavigateCheck --> browserNavigate["browser.navigate(url)"]
    onNavigateCheck --> blocked["Blocked - Return error"]
    
    observe --> browserObserve["browser.observe(focus, timeout)"]
    browserObserve --> observeResults["ObserveResultItem[]"]
    
    register --> getAttrs["browser.getElementAttributesFromXPath()"]
    getAttrs --> extractSelectors["extractMultipleSelectors()"]
    extractSelectors --> registerHandler["handlers.registerElement()"]
    
    interact --> browserAct["browser.act(instruction)"]
    browserAct --> extractSelectors
```

**Sources:** [services/action-builder/src/recorder/RecorderToolExecutor.ts:69-552]()

### Tool Execution with Retry

Each tool execution includes retry logic for transient failures:

```typescript
// From ActionRecorder.executeToolWithRetry()
{
  maxAttempts: 3,
  baseDelayMs: 1000,
  exponentialBackoff: baseDelayMs * Math.pow(2, attempt - 1)
}
```

Retryable errors include browser timeouts, connection failures, and transient network issues. Non-retryable errors (e.g., element not found after retries) are marked as skipped.

**Sources:** [services/action-builder/src/recorder/ActionRecorder.ts:597-664]()

### Pre-Action Hooks

`observe_page` includes automatic pre-actions:

- **Auto-scroll**: If `config.autoScrollToBottom !== false`, scrolls to page bottom before observing to load lazy-loaded content
- **Scroll tracking**: `hasScrolledCurrentPage` flag prevents duplicate scrolling per page

**Sources:** [services/action-builder/src/recorder/ActionRecorder.ts:612-631]()

---

## Element Discovery

Elements are discovered through the `observe_page` tool, which uses AI-powered browser automation to identify interactive elements.

**Element Discovery Flow**

```mermaid
graph LR
    LLM["LLM calls observe_page"]
    focus["focus: 'search form elements'"]
    module["module: 'header'"]
    
    LLM --> focus
    LLM --> module
    
    focus --> browserObserve["browser.observe(focus, timeout)"]
    browserObserve --> stagehand["Stagehand SDK (AI vision)"]
    stagehand --> elements["ObserveResultItem[]"]
    
    elements --> item1["Item 1: {selector: 'xpath=...', description: '...', method: 'click'}"]
    elements --> item2["Item 2: {selector: 'xpath=...', description: '...', method: 'type'}"]
    elements --> itemN["Item N: ..."]
    
    item1 --> returned["Return to LLM: {elements_found: N, elements: [...]}"]
    item2 --> returned
    itemN --> returned
    
    returned --> llmRegister["LLM calls register_element for each discovered element"]
```

**Sources:** [services/action-builder/src/recorder/RecorderToolExecutor.ts:122-149]()

### Observe Result Format

Each observed element returns:

| Field | Type | Description |
|-------|------|-------------|
| `selector` | `string` | XPath selector (format: `xpath=//button[...]`) |
| `description` | `string` | Natural language description of element |
| `method` | `string` | Suggested interaction method (`click`, `type`, etc) |

**Sources:** [services/action-builder/src/types/index.ts]()

---

## Multi-Selector Extraction

When registering an element, multiple selectors are extracted with priority ordering for maximum stability.

**Selector Extraction Pipeline**

```mermaid
graph TB
    input["Input: element_id, xpath_selector, description"]
    
    subgraph "Auto-extraction via XPath"
        xpath["XPath from observe_page or LLM"]
        getAttrs["browser.getElementAttributesFromXPath(xpath)"]
        attrs["Extracted Attributes: {id, dataTestId, ariaLabel, placeholder, cssSelector, optimizedXPath}"]
        
        xpath --> getAttrs
        getAttrs --> attrs
    end
    
    subgraph "Selector Priority (extractMultipleSelectors)"
        p1["Priority 1: ID - createIdSelector(id) → '[id=\"value\"]'"]
        p2["Priority 2: data-testid → '[data-testid=\"value\"]'"]
        p3["Priority 3: aria-label → '[aria-label=\"value\"]'"]
        p4["Priority 4: data-* attributes → '[data-state--date-string=\"{{date}}\"]'"]
        p5["Priority 5: CSS selector"]
        p6["Priority 6: XPath (optimized or original)"]
        p7["Priority 7: placeholder → '[placeholder=\"value\"]'"]
        
        attrs --> p1
        attrs --> p2
        attrs --> p3
        attrs --> p4
        attrs --> p5
        attrs --> p6
        attrs --> p7
    end
    
    subgraph "Template Detection"
        p4 --> detectPattern["detectTemplatePattern(cssSelector)"]
        detectPattern --> datePattern["Date patterns: data-state--date-string='YYYY-MM-DD'"]
        datePattern --> template["Template: '[data-state--date-string=\"{{date}}\"]'"]
        template --> templateParams["templateParams: [{name: 'date', type: 'date', format: 'YYYY-MM-DD'}]"]
    end
    
    output["SelectorItem[] with priority, confidence, isTemplate"]
```

**Sources:** [services/action-builder/src/recorder/ActionRecorder.ts:263-397](), [services/action-builder/src/recorder/RecorderToolExecutor.ts:275-477]()

### Selector Types and Confidence Scores

| Selector Type | Priority | Confidence | Example |
|---------------|----------|------------|---------|
| `id` | 1 | 0.95 | `[id="submit-btn"]` |
| `data-testid` | 2 | 0.90 | `[data-testid="checkout-btn"]` |
| `aria-label` | 3 | 0.85 | `[aria-label="Close dialog"]` |
| `data-*` (stable) | 4 | 0.80 | `[data-component="header"]` |
| `css` | 5 | 0.75 | `.btn.primary` |
| `xpath` (optimized) | 6 | 0.80 | `//button[@name="submit"]` |
| `xpath` (absolute) | 6 | 0.60 | `/html[1]/body[1]/div[3]/button[1]` |
| `placeholder` | 7 | 0.65 | `[placeholder="Enter email"]` |

**Sources:** [services/action-builder/src/recorder/ActionRecorder.ts:278-394]()

### Template Pattern Detection

The system detects dynamic values that should be parameterized:

```typescript
// Example: Airbnb date selector
// Input:  button[data-state--date-string='2025-12-10']
// Output: button[data-state--date-string='{{date}}']
// Params: [{name: 'date', type: 'date', format: 'YYYY-MM-DD'}]
```

Supported patterns:
- Date attributes: `data-state--date-string`, `data-date`, `aria-label` with dates
- Format: `YYYY-MM-DD`, `MM/DD/YYYY`, `DD/MM/YYYY`

**Sources:** [services/action-builder/src/recorder/ActionRecorder.ts:209-261]()

---

## Recording Modes

ActionRecorder supports two distinct recording modes with different prompts and tool usage patterns.

**Recording Mode Comparison**

| Aspect | Exploratory Mode | Task-Driven Mode |
|--------|------------------|------------------|
| **Primary Tool** | `register_element` | `interact` |
| **Prompt Type** | `CAPABILITY_RECORDER_SYSTEM_PROMPT` | Custom system/user prompts |
| **Navigation** | Minimal (single page focus) | Task-driven (multi-page flows) |
| **Element Discovery** | Comprehensive module-by-module scan | Discover elements while executing task |
| **Use Case** | Document all elements on a page | Record task execution steps |
| **Output** | Complete page capability map | Task-specific action sequence |

**Sources:** [services/action-builder/src/llm/prompts/capability-recorder.ts:1-256](), [services/action-builder/src/task-worker/utils/prompt-builder.ts]()

### Exploratory Mode

Used by playbook-builder and default recording. Focuses on comprehensive element discovery:

```
System Prompt: CAPABILITY_RECORDER_SYSTEM_PROMPT
User Prompt: "Record all UI elements for this scenario... For EACH module, observe THEN IMMEDIATELY register..."

Tools Priority:
1. navigate(url)
2. set_page_context(page_type)
3. scroll_to_bottom() [if lazy loading]
4. observe_page(focus: "header elements", module: "header")
5. register_element() × N [batch registration]
6. observe_page(focus: "main content", module: "main")
7. register_element() × N
```

**Sources:** [services/action-builder/src/llm/prompts/capability-recorder.ts:4-135](), [scripts/playbook-record.ts:156-168]()

### Task-Driven Mode

Used by task-worker for executing specific scenarios while recording interactions:

```
System Prompt: "You are a web automation expert. Execute the given task while recording elements you interact with..."
User Prompt: "Task: Search for hotels in Tokyo\nSteps:\n1. Enter 'Tokyo' in search\n2. Click search button..."

Tools Priority:
1. navigate(url)
2. interact(element_id, action, instruction) [discovers + registers element]
3. wait/scroll as needed
4. observe_page [when need to find elements]
```

**Sources:** [services/action-builder/src/task-worker/utils/prompt-builder.ts:1-177](), [services/action-builder/src/task-worker/task-executor.ts:139-169]()

---

## Termination Strategy

Recording terminates when specific conditions are met to prevent runaway loops and optimize resource usage.

**Termination Conditions**

```mermaid
graph TB
    start["Every tool execution"]
    
    check1["1. Task timeout?\nelapsed >= taskTimeoutMs\n(default: 15 minutes)"]
    check2["2. Token limit?\ntotalTokens >= maxTokens\n(default: -1 = unlimited)"]
    check3["3. Element threshold?\ndiscoveredElements >= threshold\n(default: 80)"]
    check4["4. Low observe efficiency?\navgEfficiency < 3 && calls >= 3"]
    check5["5. Max pages visited?\nvisitedPagesCount >= maxPages\n(default: 5)"]
    check6["6. Max turns reached?\ncurrentTurn >= maxTurns\n(default: 30)"]
    
    start --> check1
    check1 -->|Yes| terminate["Terminate with reason"]
    check1 -->|No| check2
    check2 -->|Yes| terminate
    check2 -->|No| check3
    check3 -->|Yes| terminate
    check3 -->|No| check4
    check4 -->|Yes| terminate
    check4 -->|No| check5
    check5 -->|Yes| terminate
    check5 -->|No| check6
    check6 -->|Yes| terminate
    check6 -->|No| continue["Continue recording"]
    
    terminate --> result["RecordResult: {terminationReason, partialComplete: true}"]
```

**Sources:** [services/action-builder/src/recorder/ActionRecorder.ts:554-595]()

### Termination Configuration

Configurable via `RecorderConfig.terminationConfig`:

```typescript
{
  terminationConfig: {
    elementThreshold: 80,              // Stop after N elements
    minObserveEfficiency: 3,           // Stop if avg < 3 elements/observe
    minObserveCallsForCheck: 3,        // Min calls before efficiency check
  },
  taskTimeoutMs: 15 * 60 * 1000,       // Overall task timeout
  maxTokens: -1,                        // Token limit (-1 = unlimited)
  maxVisitedPages: 5,                   // Stop after N pages
  maxTurns: 30                          // Max LLM turns
}
```

**Sources:** [services/action-builder/src/types/config.ts:136-176]()

### Early Termination with Partial Results

When terminated early, the system saves discovered elements:

1. **Record Termination Reason**: Set `terminationReason` field in result
2. **Save Partial Results**: Call `saveToYamlAndDb()` with current `siteCapability`
3. **Return Success**: Mark as `partialComplete: true` to indicate incomplete but valid recording

**Sources:** [services/action-builder/src/recorder/ActionRecorder.ts:996-1054]()

---

## Selector Optimization

After recording completes, selectors are analyzed and optimized using LLM-based stability detection.

**Selector Optimization Pipeline**

```mermaid
graph LR
    input["discoveredElements: Map<string, ElementCapability>"]
    
    check["config.enableSelectorOptimization\n(default: true)"]
    input --> check
    
    check -->|false| skip["Skip optimization"]
    check -->|true| optimizer["SelectorOptimizer.optimizeSelectors()"]
    
    optimizer --> analyze["LLM analyzes all selectors"]
    analyze --> detect["Detect unstable patterns:\n- Dynamic counters\n- Hashes/UUIDs\n- Timestamps\n- Session IDs"]
    
    detect --> filter["Filter out unstable selectors"]
    filter --> reorder["Reorder by stability"]
    reorder --> adjustConf["Adjust confidence scores"]
    
    adjustConf --> update["Update siteCapability.pages[].elements[].selectors"]
    update --> save["Save to DB and YAML"]
```

**Sources:** [services/action-builder/src/recorder/ActionRecorder.ts:706-748](), [services/action-builder/src/optimizer/SelectorOptimizer.ts]()

### Optimization Benefits

- **Removes unstable selectors**: Dynamic IDs, timestamps, session tokens
- **Reorders by reliability**: Prioritizes stable attributes (id, data-testid, name)
- **Updates confidence scores**: Adjusts based on stability analysis
- **Batch processing**: Optimizes all elements in one LLM call for efficiency

**Sources:** [services/action-builder/src/recorder/ActionRecorder.ts:706-748]()

---

## Token and Statistics Tracking

Recording tracks comprehensive metrics for observability and cost monitoring.

**Token Tracking Architecture**

```mermaid
graph TB
    subgraph "Token Sources"
        planning["Planning Tokens\n(AIClient)"]
        browser["Browser Tokens\n(Stagehand)"]
    end
    
    planning --> inputPlanning["inputTokens"]
    planning --> outputPlanning["outputTokens"]
    
    browser --> inputBrowser["browser.getTokenStats().input"]
    browser --> outputBrowser["browser.getTokenStats().output"]
    
    subgraph "Combined Statistics"
        calc["calculateTokenStats()"]
        inputPlanning --> calc
        outputPlanning --> calc
        inputBrowser --> calc
        outputBrowser --> calc
        
        calc --> total["Total Tokens:\ninput + output"]
        calc --> breakdown["Breakdown:\n{planning: {...}, browser: {...}}"]
    end
    
    total --> result["RecordResult.tokens"]
    breakdown --> result
```

**Sources:** [services/action-builder/src/recorder/ActionRecorder.ts:666-700]()

### Statistics Output

`RecordResult` includes detailed metrics:

```typescript
{
  success: true,
  turns: 10,                          // LLM conversation turns
  steps: 25,                          // Total tool executions
  totalDuration: 45000,               // Milliseconds
  tokens: {
    input: 15000,                     // Total input tokens
    output: 8000,                     // Total output tokens
    total: 23000,                     // Combined total
    planning: {                       // AIClient usage
      input: 12000,
      output: 6000
    },
    browser: {                        // Stagehand usage
      input: 3000,
      output: 2000
    }
  },
  elementsDiscovered: 18,
  visitedPagesCount: 3,
  observeStats: {
    totalCalls: 5,
    totalElements: 18,
    avgEfficiency: 3.6               // Elements per observe call
  },
  terminationReason: 'completed'
}
```

**Sources:** [services/action-builder/src/types/config.ts:276-316]()

### Real-Time Step Events

`onStepFinish` callback provides real-time progress updates:

```typescript
{
  stepNumber: 5,
  totalTurns: 2,
  maxTurns: 30,
  toolName: 'register_element',
  toolArgs: { element_id: 'header_search_input', ... },
  toolResult: { success: true, ... },
  success: true,
  durationMs: 1200,
  pageType: 'home',
  timestamp: Date
}
```

**Sources:** [services/action-builder/src/types/config.ts:1-32](), [services/action-builder/src/recorder/ActionRecorder.ts:174-206]()

---

## Integration Points

ActionRecorder integrates with multiple system components:

| Component | Integration Point | Purpose |
|-----------|------------------|---------|
| **ActionBuilder** | `ActionBuilder.build()` calls `ActionRecorder.record()` | Main entry point for recording |
| **TaskExecutor** | Uses `ActionBuilder` with custom prompts | Task-driven recording mode |
| **YamlWriter** | `saveToYamlAndDb()` persists to YAML | Human-readable output format |
| **DbWriter** | `saveToYamlAndDb()` persists to database | Searchable element storage |
| **SelectorOptimizer** | `optimizeAndUpdateSelectors()` before save | LLM-based selector stability analysis |

**Sources:** [services/action-builder/src/ActionBuilder.ts:410-483](), [services/action-builder/src/task-worker/task-executor.ts:139-169](), [services/action-builder/src/recorder/ActionRecorder.ts:750-1100]()

---

# Page: Recording Tools Reference

# Recording Tools Reference

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [services/action-builder/scripts/playbook-record.ts](services/action-builder/scripts/playbook-record.ts)
- [services/action-builder/src/recorder/RecorderToolExecutor.ts](services/action-builder/src/recorder/RecorderToolExecutor.ts)
- [services/action-builder/src/recorder/RecorderTools.ts](services/action-builder/src/recorder/RecorderTools.ts)
- [services/action-builder/src/types/capability.ts](services/action-builder/src/types/capability.ts)
- [services/action-builder/src/utils/index.ts](services/action-builder/src/utils/index.ts)
- [services/action-builder/src/utils/url-matcher.ts](services/action-builder/src/utils/url-matcher.ts)
- [services/action-builder/src/validator/SelectorValidator.ts](services/action-builder/src/validator/SelectorValidator.ts)
- [services/action-builder/test/browser/xpath-optimizer.ut.test.ts](services/action-builder/test/browser/xpath-optimizer.ut.test.ts)
- [services/action-builder/test/recorder/RecorderTools.ut.test.ts](services/action-builder/test/recorder/RecorderTools.ut.test.ts)
- [services/action-builder/test/types/capability.ut.test.ts](services/action-builder/test/types/capability.ut.test.ts)
- [services/action-builder/test/utils/url-matcher.ut.test.ts](services/action-builder/test/utils/url-matcher.ut.test.ts)
- [services/action-builder/test/validator/SelectorValidator.ut.test.ts](services/action-builder/test/validator/SelectorValidator.ut.test.ts)

</details>



This page provides a complete reference for all recorder tools available during action recording sessions. These tools are invoked by the AI agent during multi-turn recording loops to discover, interact with, and register UI elements.

For information about how these tools are orchestrated in the recording process, see [Action Recording](#3.2.2). For details on the task execution pipeline that runs recordings, see [Task Execution Pipeline](#3.2.1).

## Overview

Recording tools are the primary interface between the AI agent and the browser during capability discovery. The `RecorderToolExecutor` dispatches tool calls from the LLM to the appropriate browser operations, element registration handlers, and page context management.

**Tool Categories:**

| Category | Tools | Purpose |
|----------|-------|---------|
| **Navigation** | `navigate`, `go_back` | URL navigation and browser history control |
| **Observation** | `observe_page` | AI-powered element discovery using vision models |
| **Interaction** | `interact` | Task-driven element interaction with automatic registration |
| **Registration** | `register_element`, `set_page_context` | Manual capability registration and page context setup |
| **Control Flow** | `wait`, `scroll`, `scroll_to_bottom` | Page state management and content loading |

Sources: [services/action-builder/src/recorder/RecorderTools.ts:3-216](), [services/action-builder/src/recorder/RecorderToolExecutor.ts:49-553]()

## Tool Execution Architecture

```mermaid
graph TB
    subgraph "AI Agent (LLM)"
        Agent["LLM Agent<br/>(Multi-turn loop)"]
    end
    
    subgraph "RecorderToolExecutor"
        Execute["execute()<br/>Tool dispatcher"]
        
        subgraph "Navigation Tools"
            Navigate["navigate<br/>URL + domain check"]
            GoBack["go_back<br/>Browser history"]
        end
        
        subgraph "Observation Tools"
            Observe["observe_page<br/>AI vision discovery"]
        end
        
        subgraph "Interaction Tools"
            Interact["interact<br/>Act + register"]
        end
        
        subgraph "Registration Tools"
            Register["register_element<br/>Multi-selector extraction"]
            SetContext["set_page_context<br/>Page metadata"]
        end
        
        subgraph "Control Tools"
            Wait["wait<br/>Time or text"]
            Scroll["scroll<br/>Up/down"]
            ScrollBottom["scroll_to_bottom<br/>Lazy loading"]
        end
    end
    
    subgraph "Handlers"
        OnNavigate["onNavigate()<br/>Visit tracking"]
        RegisterHandler["registerElement()<br/>Capability storage"]
        SetPageHandler["setPageContext()<br/>Page type setup"]
        ExtractSelectors["extractMultipleSelectors()<br/>Multi-format extraction"]
    end
    
    subgraph "Browser Automation"
        BrowserAdapter["BrowserAdapter<br/>(Stagehand/AgentCore)"]
        ObserveMethod["observe()<br/>AI element discovery"]
        ActMethod["act()<br/>Natural language action"]
        GetAttrs["getElementAttributesFromXPath()<br/>Attribute extraction"]
    end
    
    Agent -->|"Tool call"| Execute
    
    Execute --> Navigate
    Execute --> GoBack
    Execute --> Observe
    Execute --> Interact
    Execute --> Register
    Execute --> SetContext
    Execute --> Wait
    Execute --> Scroll
    Execute --> ScrollBottom
    
    Navigate --> OnNavigate
    Navigate --> BrowserAdapter
    
    Observe --> ObserveMethod
    
    Interact --> ObserveMethod
    Interact --> GetAttrs
    Interact --> ExtractSelectors
    Interact --> ActMethod
    Interact --> RegisterHandler
    
    Register --> ObserveMethod
    Register --> GetAttrs
    Register --> ExtractSelectors
    Register --> RegisterHandler
    
    SetContext --> SetPageHandler
    
    GoBack --> BrowserAdapter
    Scroll --> BrowserAdapter
    ScrollBottom --> BrowserAdapter
    Wait --> BrowserAdapter
```

**Execution Flow:**
1. LLM agent calls a tool via OpenAI function calling format
2. `RecorderToolExecutor.execute()` dispatches to the appropriate tool handler
3. Tool handler interacts with browser, extracts selectors, or updates state
4. Tool returns structured output to guide next LLM turn

Sources: [services/action-builder/src/recorder/RecorderToolExecutor.ts:49-67](), [services/action-builder/src/recorder/RecorderToolExecutor.ts:69-553]()

## Tool Reference

### navigate

Navigates the browser to a URL with domain validation and visit tracking.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `url` | string | Yes | Full URL to navigate to |

**Behavior:**

1. **Pre-navigation validation**: Checks if URL should be visited BEFORE loading the page to avoid:
   - External domain navigation (security)
   - Duplicate page loads (efficiency)
   - Unwanted side effects (form submissions, cart modifications)

2. **Domain checking**: Extracts hostname and validates against source domain via `onNavigate()` handler

3. **Visit tracking**: Maintains normalized URL history using sorted query parameters + hash for SPA support

4. **Auto-popup closing**: Calls `browser.autoClosePopups()` after successful navigation

**Output:**

```typescript
// Success
{ success: true, url: string }

// Already visited
{ 
  success: false, 
  url: string,
  message: string,
  already_visited: true,
  blocked: true 
}

// External domain
{ 
  success: false, 
  url: string,
  message: string,
  external_domain: true,
  blocked: true 
}
```

**Example Output:**

```json
{
  "success": false,
  "url": "https://example.com/search",
  "message": "Navigation to /search?q=test blocked: already visited. Please continue with other elements on the current page.",
  "already_visited": true,
  "blocked": true
}
```

Sources: [services/action-builder/src/recorder/RecorderToolExecutor.ts:76-120](), [services/action-builder/src/recorder/RecorderTools.ts:8-18]()

### observe_page

Discovers interactive elements on the current page using AI vision models.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `focus` | string | Yes | What to focus on (e.g., "search box and submit button") |
| `module` | string | No | Page module to observe: "header", "footer", "sidebar", "navibar", "main", "modal", "breadcrumb", "tab", "all" |
| `_timeoutMs` | number | No | Internal timeout parameter (not exposed to LLM) |

**Behavior:**

1. Calls `browser.observe()` with the focus instruction and optional timeout
2. AI vision model (via Stagehand/AgentCore) analyzes page and returns element descriptions with selectors
3. Results are filtered to elements with both description and selector
4. Limited to 20 elements in output to avoid token overflow

**Output:**

```typescript
{
  elements_found: number,
  elements: Array<{
    description: string,
    selector: string,      // CSS or XPath format
    method: string         // Default: "click"
  }>
}
```

**Module Classification:**

The `module` parameter helps focus observation on specific page regions:
- `header` - Top navigation, logos, user menu
- `footer` - Bottom links, copyright, social media
- `sidebar` - Side navigation or filters
- `navibar` - Navigation bars
- `main` - Primary content area
- `modal` - Dialog overlays
- `breadcrumb` - Breadcrumb navigation
- `tab` - Tab navigation
- `all` - Entire page (default)

**Example Output:**

```json
{
  "elements_found": 3,
  "elements": [
    {
      "description": "Search input field for entering query",
      "selector": "xpath=/html[1]/body[1]/div[1]/input[1]",
      "method": "click"
    },
    {
      "description": "Submit search button",
      "selector": "css=#search-btn",
      "method": "click"
    }
  ]
}
```

Sources: [services/action-builder/src/recorder/RecorderToolExecutor.ts:122-150](), [services/action-builder/src/recorder/RecorderTools.ts:19-42]()

### set_page_context

Sets metadata about the current page type for organizing recorded capabilities.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `page_type` | string | Yes | Page type identifier (e.g., "home", "search_results") |
| `page_name` | string | Yes | Human-readable page name |
| `page_description` | string | No | Optional detailed description |
| `url_pattern` | string | No | Optional regex pattern for this page type |

**Behavior:**

1. Extracts current URL from browser
2. Calls `setPageContext()` handler with page metadata
3. Handler associates subsequent element registrations with this page type

**Output:**

```typescript
{ success: true, page_type: string }
```

**Usage Pattern:**

Call `set_page_context` once at the start of recording on each new page type before registering elements:

```
1. navigate("https://example.com/search")
2. set_page_context(page_type="search_results", page_name="Search Results")
3. observe_page(focus="search filters")
4. register_element(...) // Elements belong to "search_results" page
```

Sources: [services/action-builder/src/recorder/RecorderToolExecutor.ts:479-502](), [services/action-builder/src/recorder/RecorderTools.ts:43-62]()

### register_element

Manually registers a UI element capability with multi-selector extraction and validation.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `element_id` | string | Yes | Unique identifier in snake_case (cannot be "undefined" or empty) |
| `description` | string | Yes | Human-readable element description |
| `element_type` | string | Yes | Element type: "button", "input", "link", "select", "checkbox", "radio", "text", "data_field", "container", "list", "list_item", "other" |
| `allow_methods` | string[] | Yes | Allowed methods: "click", "type", "clear", "scroll", "hover", "select", "extract" |
| `css_selector` | string | No | CSS selector (LLM-provided, may be inaccurate) |
| `xpath_selector` | string | No | XPath selector (preferred if available) |
| `aria_label` | string | No | ARIA label attribute |
| `placeholder` | string | No | Placeholder text (for inputs) |
| `leads_to` | string | No | Page type this element navigates to |
| `arguments` | object[] | No | Arguments for parameterized actions |
| `parent` | string | No | Parent element ID |
| `depends_on` | string | No | Element that must be interacted with first |
| `visibility_condition` | string | No | Visibility condition description |
| `is_repeating` | boolean | No | Whether element repeats in a list |
| `data_key` | string | No | Data extraction key for data_field type |
| `children` | string[] | No | Child element IDs |
| `module` | string | No | Page module: "header", "footer", "sidebar", "navibar", "main", "modal", "breadcrumb", "tab", "unknown" |
| `input_type` | string | No | Input type (text, email, password, number, etc.) |
| `input_name` | string | No | Name attribute for input elements |
| `input_value` | string | No | Default/placeholder value for inputs |
| `href` | string | No | Link href URL or pattern |

**Behavior:**

1. **Selector Validation**: Rejects elements with invalid IDs (undefined, null, empty string, "undefined")

2. **Automatic Selector Discovery**: If no valid XPath provided, calls `observe_page()` to find real selectors (LLM often provides made-up CSS selectors)

3. **Multi-Selector Extraction**: If XPath is provided, calls `getElementAttributesFromXPath()` to extract:
   - CSS selector (real from page, not LLM-provided)
   - ID attribute
   - data-testid attribute
   - aria-label attribute
   - placeholder attribute
   - Optimized attribute-based XPath

4. **Priority Ordering**: Builds selector array with priority order:
   - Priority 1: ID selector (confidence 0.95)
   - Priority 2: data-testid (confidence 0.9)
   - Priority 3: aria-label (confidence 0.85)
   - Priority 4: CSS (confidence 0.8 for templates, 0.75 for regular)
   - Priority 5: XPath (confidence 0.8 for optimized, 0.6 for absolute)
   - Priority 6: placeholder (confidence 0.65)

5. **Template Detection**: Checks CSS selectors for template patterns (e.g., dynamic IDs)

6. **Phantom Element Filtering**: Rejects elements with no valid selectors (element doesn't exist on current page)

**Output:**

```typescript
// Success
{ success: true, element_id: string }

// Invalid element_id
{ 
  error: "invalid_element_id",
  message: "element_id is required and cannot be empty or undefined"
}

// No selectors found
{
  error: "no_selectors_found",
  message: "Could not find element on current page. Skip this element.",
  element_id: string
}
```

**Multi-Selector Format:**

```typescript
interface SelectorItem {
  type: "css" | "xpath" | "id" | "data-testid" | "aria-label" | "placeholder"
  value: string
  priority: number       // Lower = higher priority
  confidence: number     // 0-1 scale
  isTemplate?: boolean
  templateParams?: Array<{
    name: string
    type: string
    description: string
  }>
}
```

**Example - ID with Special Characters:**

```json
{
  "element_id": "arxiv_category_cs_ai",
  "description": "Computer Science - Artificial Intelligence category link",
  "element_type": "link",
  "allow_methods": ["click"],
  "module": "main"
}

// Output includes optimized selectors:
{
  "success": true,
  "element_id": "arxiv_category_cs_ai",
  "selectors": [
    {
      "type": "id",
      "value": "[id=\"cs.AI\"]",  // Handles dots correctly
      "priority": 1,
      "confidence": 0.95
    },
    {
      "type": "xpath",
      "value": "//a[@id=\"cs.AI\"]",
      "priority": 2,
      "confidence": 0.8
    }
  ]
}
```

Sources: [services/action-builder/src/recorder/RecorderToolExecutor.ts:275-477](), [services/action-builder/src/recorder/RecorderTools.ts:63-135]()

### interact

Performs an interaction on an element and automatically registers it. Used in task-driven recording mode.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `element_id` | string | Yes | Unique element identifier |
| `action` | string | Yes | Action to perform (e.g., "click", "type") |
| `instruction` | string | Yes | Natural language instruction for locating element |
| `element_description` | string | Yes | Human-readable element description |
| `value` | string | No | Value to type (required for "type" action) |
| `css_selector` | string | No | Optional CSS selector hint |
| `xpath_selector` | string | No | Optional XPath selector hint |

**Behavior:**

1. **Selector Resolution**:
   - If LLM provides XPath or CSS, uses those
   - Otherwise, calls `observe_page()` with instruction to find element

2. **Attribute Extraction**: If XPath available, calls `getElementAttributesFromXPath()` to extract additional selectors (id, data-testid, aria-label, CSS, placeholder)

3. **Multi-Selector Building**: Constructs selector array using `extractMultipleSelectors()`

4. **Action Execution**: Calls `browser.act()` with natural language instruction:
   - For "type" action: appends value to instruction (e.g., "click search box and type 'query'")

5. **Element Inference**: Automatically infers `element_type` and `allow_methods` from action

6. **Auto Registration**: Creates and registers `ElementCapability` with discovered selectors

**Output:**

```typescript
{
  success: true,
  element_id: string,
  selectors: SelectorItem[],
  action_result: object  // Result from browser.act()
}
```

**Usage Pattern:**

Use `interact` for task-driven exploration where you want to both interact and register in one step:

```
interact(
  element_id="search_input",
  action="type",
  instruction="type into the search box",
  value="artificial intelligence",
  element_description="Main search input field"
)
```

Sources: [services/action-builder/src/recorder/RecorderToolExecutor.ts:152-273](), [services/action-builder/src/recorder/RecorderTools.ts:136-156]()

### wait

Pauses execution for a specified time or waits for text to appear.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `seconds` | number | No | Seconds to wait |
| `forText` | string | No | Text to wait for on page |

**Behavior:**

- If `seconds` provided: Waits for specified duration via `browser.wait()`
- If `forText` provided: Waits for text to appear via `browser.waitForText()`
- If neither provided: Returns immediately

**Output:**

```typescript
// Time-based wait
{ waited: number }

// Text-based wait
{ waitedFor: string }

// No-op
{ waited: 0 }
```

**Example Usage:**

```json
// Wait for loading
{ "seconds": 2 }

// Wait for confirmation message
{ "forText": "Successfully saved" }
```

Sources: [services/action-builder/src/recorder/RecorderToolExecutor.ts:504-516](), [services/action-builder/src/recorder/RecorderTools.ts:157-170]()

### scroll

Scrolls the page up or down by a specified amount.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `direction` | string | Yes | "up" or "down" |
| `amount` | number | No | Scroll distance in pixels (default: 300) |

**Behavior:**

Calls `browser.scroll(direction, amount)` to scroll the viewport.

**Output:**

```typescript
{ scrolled: "up" | "down", amount: number }
```

**Example Usage:**

```json
{
  "direction": "down",
  "amount": 500
}
```

Sources: [services/action-builder/src/recorder/RecorderToolExecutor.ts:518-524](), [services/action-builder/src/recorder/RecorderTools.ts:171-185]()

### scroll_to_bottom

Scrolls the page to the bottom to trigger lazy-loaded content.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `wait_after_scroll` | number | No | Time to wait after scrolling in milliseconds (default: 1000) |

**Behavior:**

1. Scrolls to page bottom via `browser.scrollToBottom()`
2. Waits for specified duration to allow lazy-loaded elements to render
3. Useful for infinite scroll pages, dynamically loaded lists, and footer content

**Output:**

```typescript
{ success: true, wait_after_scroll: number }
```

**Example Usage:**

```json
{
  "wait_after_scroll": 1500
}
```

**Use Cases:**
- Product listing pages with infinite scroll
- Social media feeds
- Search results with pagination
- Footer elements that load on scroll

Sources: [services/action-builder/src/recorder/RecorderToolExecutor.ts:526-532](), [services/action-builder/src/recorder/RecorderTools.ts:186-202](), [services/action-builder/scripts/playbook-record.ts:133-134]()

### go_back

Navigates back to the previous page in browser history.

**Parameters:**

None required.

**Behavior:**

1. Retrieves previous URL from visit history via `getPreviousUrl()`
2. Calls `browser.goBack()` to navigate back
3. Returns both previous and current URLs for tracking

**Output:**

```typescript
{
  success: true,
  previous_url: string | null,
  current_url: string | null
}
```

**Use Cases:**
- Return to listing page after viewing details
- Navigate back after exploring modal or overlay
- Undo navigation to unwanted page
- Control navigation flow during exploration

**Example Workflow:**

```
1. navigate("/products")
2. observe_page("product cards")
3. interact(element_id="product_1", action="click", ...)  // Goes to /products/1
4. observe_page("product details")
5. go_back()  // Returns to /products
6. interact(element_id="product_2", action="click", ...)  // Goes to /products/2
```

Sources: [services/action-builder/src/recorder/RecorderToolExecutor.ts:534-545](), [services/action-builder/src/recorder/RecorderTools.ts:203-214]()

## Tool Execution Flow

```mermaid
sequenceDiagram
    participant LLM as "LLM Agent"
    participant Executor as "RecorderToolExecutor"
    participant Browser as "BrowserAdapter"
    participant Handlers as "Registration Handlers"
    
    Note over LLM,Handlers: Multi-turn recording loop
    
    LLM->>Executor: navigate(url="https://example.com")
    Executor->>Handlers: onNavigate(url)
    Handlers-->>Executor: NavigateResult
    alt URL allowed
        Executor->>Browser: navigate(url)
        Executor->>Browser: autoClosePopups()
        Executor-->>LLM: {success: true}
    else URL blocked
        Executor-->>LLM: {success: false, blocked: true}
    end
    
    LLM->>Executor: set_page_context(page_type="home")
    Executor->>Handlers: setPageContext(...)
    Executor-->>LLM: {success: true}
    
    LLM->>Executor: observe_page(focus="search elements")
    Executor->>Browser: observe(focus)
    Browser-->>Executor: ObserveResult[]
    Executor-->>LLM: {elements_found: 3, elements: [...]}
    
    LLM->>Executor: register_element(element_id="search_input", ...)
    alt Has XPath
        Executor->>Browser: getElementAttributesFromXPath()
        Browser-->>Executor: {id, css, dataTestId, ...}
    else No XPath
        Executor->>Browser: observe(description)
        Browser-->>Executor: ObserveResult
    end
    Executor->>Handlers: extractMultipleSelectors()
    Handlers-->>Executor: SelectorItem[]
    Executor->>Handlers: registerElement(capability)
    Executor-->>LLM: {success: true, element_id: "search_input"}
    
    LLM->>Executor: scroll_to_bottom()
    Executor->>Browser: scrollToBottom(waitAfterScroll)
    Executor-->>LLM: {success: true}
    
    LLM->>Executor: go_back()
    Executor->>Browser: goBack()
    Executor->>Handlers: getCurrentUrl()
    Executor-->>LLM: {success: true, current_url: "..."}
```

**Key Points:**

1. **Pre-validation**: `navigate` checks URL validity before browser navigation
2. **Auto-extraction**: `register_element` automatically extracts multiple selector formats
3. **Fallback discovery**: Tools call `observe_page()` internally when selectors are missing
4. **Stateful tracking**: Handlers maintain visit history, page context, and registered elements
5. **Error handling**: Tools return structured errors instead of throwing exceptions

Sources: [services/action-builder/src/recorder/RecorderToolExecutor.ts:69-553]()

## Selector Extraction Strategy

```mermaid
graph TB
    subgraph "register_element Tool Call"
        Input["Tool Parameters<br/>element_id, description<br/>css_selector?, xpath_selector?"]
    end
    
    subgraph "Selector Discovery"
        HasXPath{"Has valid<br/>XPath?"}
        CallObserve["Call observe_page()<br/>to find real selector"]
        UseXPath["Use provided XPath"]
    end
    
    subgraph "Attribute Extraction"
        GetAttrs["getElementAttributesFromXPath()<br/>Extract all attributes"]
        Attributes["Extracted:<br/>• CSS selector (real)<br/>• id attribute<br/>• data-testid<br/>• aria-label<br/>• placeholder<br/>• optimized XPath"]
    end
    
    subgraph "Multi-Selector Building"
        Priority1["Priority 1<br/>ID selector<br/>confidence: 0.95"]
        Priority2["Priority 2<br/>data-testid<br/>confidence: 0.9"]
        Priority3["Priority 3<br/>aria-label<br/>confidence: 0.85"]
        Priority4["Priority 4<br/>CSS selector<br/>confidence: 0.75-0.8"]
        Priority5["Priority 5<br/>XPath<br/>confidence: 0.6-0.8"]
        Priority6["Priority 6<br/>placeholder<br/>confidence: 0.65"]
    end
    
    subgraph "Validation"
        CheckEmpty{"Any selectors<br/>found?"}
        Register["registerElement()<br/>Store capability"]
        Reject["Return error:<br/>no_selectors_found"]
    end
    
    Input --> HasXPath
    HasXPath -->|No| CallObserve
    HasXPath -->|Yes| UseXPath
    CallObserve --> GetAttrs
    UseXPath --> GetAttrs
    
    GetAttrs --> Attributes
    Attributes --> Priority1
    Priority1 --> Priority2
    Priority2 --> Priority3
    Priority3 --> Priority4
    Priority4 --> Priority5
    Priority5 --> Priority6
    
    Priority6 --> CheckEmpty
    CheckEmpty -->|Yes| Register
    CheckEmpty -->|No| Reject
```

**Selector Priority Rationale:**

| Priority | Selector Type | Confidence | Reasoning |
|----------|--------------|------------|-----------|
| 1 | ID | 0.95 | Most stable, unique identifier. Uses `createIdSelector()` to handle special characters like dots |
| 2 | data-testid | 0.9 | Designed for testing, intentionally stable |
| 3 | aria-label | 0.85 | Semantic, accessibility-focused, usually stable |
| 4 | CSS | 0.75-0.8 | Structure-dependent, may break with layout changes. Higher confidence for templates |
| 5 | XPath | 0.6-0.8 | Attribute-based XPath (0.8) is more stable than absolute paths (0.6) |
| 6 | placeholder | 0.65 | Input-specific, may change with content updates |

**Why This Matters:**

1. **Fallback Chain**: Browser automation tries selectors in priority order until one succeeds
2. **Stability**: Higher priority selectors are less likely to break during site updates
3. **Real Selectors**: Always extracts from actual page DOM, not LLM hallucinations
4. **Template Support**: Detects parameterized selectors for list items and dynamic content

Sources: [services/action-builder/src/recorder/RecorderToolExecutor.ts:275-477](), [services/action-builder/src/recorder/RecorderToolExecutor.ts:192-233](), [services/action-builder/src/recorder/RecorderToolExecutor.ts:330-435]()

## Tool Definition Schema

The tools are defined using OpenAI's function calling schema format for LLM consumption:

```mermaid
graph LR
    subgraph "getRecorderTools()"
        ToolArray["OpenAI.Chat.Completions<br/>.ChatCompletionTool[]"]
    end
    
    subgraph "Tool Definition"
        Type["type: 'function'"]
        Function["function: {<br/>  name: string<br/>  description: string<br/>  parameters: JSONSchema<br/>}"]
    end
    
    subgraph "Parameter Schema"
        Props["properties: {<br/>  param: { type, description, enum? }<br/>}"]
        Required["required: string[]"]
    end
    
    subgraph "Used By"
        ActionRecorder["ActionRecorder<br/>recording loop"]
        AIClient["AIClient<br/>LLM chat interface"]
    end
    
    ToolArray --> Type
    ToolArray --> Function
    Function --> Props
    Function --> Required
    
    ToolArray -.-> ActionRecorder
    ActionRecorder --> AIClient
```

**Example Tool Definition:**

```typescript
{
  type: "function",
  function: {
    name: "register_element",
    description: "Register a UI element capability with selectors...",
    parameters: {
      type: "object",
      properties: {
        element_id: { 
          type: "string", 
          description: "Unique element identifier (snake_case)" 
        },
        module: {
          type: "string",
          enum: ["header", "footer", "sidebar", "navibar", 
                 "main", "modal", "breadcrumb", "tab", "unknown"],
          description: "Page module location"
        }
        // ... more parameters
      },
      required: ["element_id", "description", "element_type", "allow_methods"]
    }
  }
}
```

Sources: [services/action-builder/src/recorder/RecorderTools.ts:3-216]()

## Common Usage Patterns

### Pattern 1: Exploratory Recording (observe + register)

Used for discovering all elements on a page without interaction:

```
1. navigate("https://example.com")
2. set_page_context(page_type="home", page_name="Home Page")
3. observe_page(focus="all interactive elements", module="header")
4. register_element(element_id="logo", ...) [from observe results]
5. register_element(element_id="search_input", ...) [from observe results]
6. observe_page(focus="main content area", module="main")
7. register_element(element_id="hero_cta", ...) [from observe results]
```

### Pattern 2: Task-Driven Recording (interact)

Used for recording through user workflows:

```
1. navigate("https://example.com")
2. set_page_context(page_type="home", page_name="Home Page")
3. interact(element_id="search_input", action="type", 
            value="product", instruction="type in search box")
4. interact(element_id="search_button", action="click",
            instruction="click search button")
5. set_page_context(page_type="search_results", page_name="Search Results")
6. observe_page(focus="search result cards")
```

### Pattern 3: Lazy-Loaded Content

Used for pages with dynamic content loading:

```
1. navigate("https://example.com/products")
2. set_page_context(page_type="product_listing", page_name="Products")
3. observe_page(focus="visible product cards")
4. scroll_to_bottom(wait_after_scroll=1500)
5. observe_page(focus="newly loaded product cards")
6. register_element(...) [additional elements]
```

### Pattern 4: Modal/Overlay Exploration

Used for recording elements in modals or overlays:

```
1. navigate("https://example.com")
2. observe_page(focus="main page elements")
3. interact(element_id="filters_button", action="click",
            instruction="click filters button")
4. wait(seconds=1)  // Wait for modal animation
5. observe_page(focus="filter options in modal", module="modal")
6. register_element(...) [modal elements]
7. go_back()  // Or close modal
```

### Pattern 5: Navigation Control

Used for exploring multiple pages systematically:

```
1. navigate("https://example.com/categories")
2. observe_page(focus="category cards")
3. interact(element_id="category_1", action="click", ...)
4. observe_page(focus="category detail page")
5. go_back()  // Return to categories
6. interact(element_id="category_2", action="click", ...)
7. observe_page(focus="category detail page")
```

Sources: [services/action-builder/scripts/playbook-record.ts:97-240]()

## Error Handling

Tools return structured error objects instead of throwing exceptions:

| Tool | Error Condition | Error Output |
|------|----------------|--------------|
| `navigate` | Already visited URL | `{success: false, already_visited: true, blocked: true, message: "..."}` |
| `navigate` | External domain | `{success: false, external_domain: true, blocked: true, message: "..."}` |
| `register_element` | Invalid element_id | `{error: "invalid_element_id", message: "element_id is required..."}` |
| `register_element` | No selectors found | `{error: "no_selectors_found", message: "Could not find element..."}` |

**Error Messages Guide LLM Behavior:**

- **`already_visited`**: Instructs LLM to continue with current page instead of navigating
- **`external_domain`**: Warns LLM not to record elements from external sites
- **`no_selectors_found`**: Suggests element may be on different page, skip it

Sources: [services/action-builder/src/recorder/RecorderToolExecutor.ts:92-111](), [services/action-builder/src/recorder/RecorderToolExecutor.ts:276-282](), [services/action-builder/src/recorder/RecorderToolExecutor.ts:438-446]()

## Implementation Notes

### URL Normalization

URLs are normalized for visit tracking to support SPAs:

```typescript
const urlObj = new URL(url);
const sortedParams = new URLSearchParams(urlObj.searchParams);
sortedParams.sort();
const urlKey = urlObj.pathname + 
               (sortedParams.toString() ? '?' + sortedParams.toString() : '') + 
               urlObj.hash;
```

- Query parameters are sorted alphabetically
- Hash fragments are preserved (important for SPAs)
- Enables accurate duplicate detection

Sources: [services/action-builder/src/recorder/RecorderToolExecutor.ts:86-89]()

### ID Selector Escaping

Special characters in IDs (like dots in "cs.AI") are handled via `createIdSelector()`:

```typescript
// Without escaping: #cs.AI (invalid, interprets as id="cs" class="AI")
// With escaping: [id="cs.AI"] (correct)
```

Sources: [services/action-builder/src/recorder/RecorderToolExecutor.ts:355-362]()

### Phantom Element Detection

Elements that the LLM thinks exist but aren't found on the page are filtered out:

```typescript
if (multiSelectors.length === 0) {
  log("warn", `Skipping element ${elementId} - no valid selectors found`);
  return { error: "no_selectors_found", message: "..." };
}
```

This prevents recording hallucinated elements and guides the LLM to focus on real UI.

Sources: [services/action-builder/src/recorder/RecorderToolExecutor.ts:438-446]()

---

# Page: Batch Crawling and Import

# Batch Crawling and Import

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [services/action-builder/.env.example](services/action-builder/.env.example)
- [services/action-builder/.gitignore](services/action-builder/.gitignore)
- [services/action-builder/README.md](services/action-builder/README.md)
- [services/action-builder/package.json](services/action-builder/package.json)
- [services/action-builder/scripts/coordinator.ts](services/action-builder/scripts/coordinator.ts)
- [services/action-builder/scripts/crawl-playbook-batch.ts](services/action-builder/scripts/crawl-playbook-batch.ts)
- [services/action-builder/scripts/crawl-sites.txt.example](services/action-builder/scripts/crawl-sites.txt.example)
- [services/action-builder/scripts/import-playbook-batch.ts](services/action-builder/scripts/import-playbook-batch.ts)
- [services/action-builder/src/llm/AIClient.ts](services/action-builder/src/llm/AIClient.ts)
- [services/action-builder/src/utils/logger.ts](services/action-builder/src/utils/logger.ts)
- [services/action-builder/vitest.setup.ts](services/action-builder/vitest.setup.ts)
- [services/db/migrations/meta/0018_snapshot.json](services/db/migrations/meta/0018_snapshot.json)

</details>



This page documents the batch crawling and import scripts for processing multiple websites sequentially. These utilities provide an alternative to the coordinator-based build pipeline for bulk operations on external sites.

For the coordinator-based task queue architecture that processes build tasks with parallel recording, see [3.2.1](#3.2.1). For action recording using LLM-driven browser automation, see [3.2.2](#3.2.2).

## Overview

The batch crawling system provides two sequential operations:

1. **Batch Crawling**: Crawls multiple websites in sequence using the playbook builder, generating JSON/YAML documentation for each site
2. **Batch Import**: Reads crawl results and imports them into the database, creating source records and associated data

This approach is useful for:
- Initial bulk ingestion of multiple websites
- Offline crawling operations that are later imported
- Testing and evaluation across multiple sites
- Separating crawl and import phases for resource management

```mermaid
graph TB
    SitesFile["crawl-sites.txt<br/>(one URL per line)"]
    
    subgraph "Phase 1: Batch Crawling"
        BatchCrawl["crawl-playbook-batch.ts"]
        CrawlScript["test/e2e/crawl-playbook.ts<br/>(spawned per site)"]
        CrawlOutput["output/sites/{domain}/crawl_playbooks/<br/>YAML + JSON files"]
        CrawlSummary["output/batch/<br/>crawl_playbook_batch_summary_*.json"]
    end
    
    subgraph "Phase 2: Batch Import"
        BatchImport["import-playbook-batch.ts"]
        ImportScript["test/e2e/import-playbook.ts<br/>(spawned per site)"]
        Database[("PostgreSQL<br/>sources, documents,<br/>chunks, etc.")]
        ImportSummary["output/batch/<br/>import_playbook_batch_summary_*.json"]
    end
    
    SitesFile --> BatchCrawl
    BatchCrawl --> CrawlScript
    CrawlScript --> CrawlOutput
    CrawlScript --> CrawlSummary
    
    CrawlSummary --> BatchImport
    CrawlOutput --> ImportScript
    BatchImport --> ImportScript
    ImportScript --> Database
    ImportScript --> ImportSummary

    style SitesFile fill:#f9f9f9
    style Database fill:#f9f9f9
```

**Sources**: [services/action-builder/scripts/crawl-playbook-batch.ts:1-360](), [services/action-builder/scripts/import-playbook-batch.ts:1-434]()

## Batch Crawling Workflow

### Configuration

Sites to crawl are listed in `scripts/crawl-sites.txt`, one URL per line:

```txt
# Crawl Sites Configuration
# Lines starting with # are comments
# Empty lines are ignored

www.example.com
www.anothersite.com
```

This file is gitignored by default. Copy from `scripts/crawl-sites.txt.example` to create it.

**Sources**: [services/action-builder/scripts/crawl-sites.txt.example:1-7](), [services/action-builder/.gitignore:41-42]()

### Execution Flow

```mermaid
graph TD
    Start["Start crawl-playbook-batch.ts"]
    LoadSites["loadSitesFromFile()<br/>Parse crawl-sites.txt"]
    InitVars["Initialize config:<br/>timeout, forwardArgs,<br/>summaryOutputPath"]
    
    LoopStart{"For each site"}
    SpawnChild["spawn() tsx<br/>test/e2e/crawl-playbook.ts"]
    Monitor["Monitor stdout/stderr<br/>Capture combined output"]
    Timeout{"Timeout?"}
    KillProcess["SIGTERM to child"]
    
    WaitComplete["Await child close"]
    ExtractPaths["extractSavedPaths()<br/>Parse 'YAML saved:' and<br/>'JSON saved:' lines"]
    
    CheckExit{"exitCode === 0?"}
    ReadJSON["Read JSON file<br/>Parse data"]
    RecordResult["Store SiteRunResult:<br/>status, paths, data,<br/>duration, error"]
    
    CheckContinue{"continueOnError?"}
    NextSite["Next site"]
    EarlyExit["Break loop"]
    
    WriteSummary["Write BatchSummary JSON:<br/>metadata + results[]"]
    End["End"]
    
    Start --> LoadSites
    LoadSites --> InitVars
    InitVars --> LoopStart
    
    LoopStart -->|Yes| SpawnChild
    SpawnChild --> Monitor
    Monitor --> Timeout
    
    Timeout -->|Yes| KillProcess
    Timeout -->|No| WaitComplete
    KillProcess --> WaitComplete
    
    WaitComplete --> ExtractPaths
    ExtractPaths --> CheckExit
    
    CheckExit -->|Yes| ReadJSON
    CheckExit -->|No| RecordResult
    ReadJSON --> RecordResult
    
    RecordResult --> CheckContinue
    CheckContinue -->|Error & stop-on-error| EarlyExit
    CheckContinue -->|Continue| NextSite
    
    NextSite --> LoopStart
    LoopStart -->|No more| WriteSummary
    EarlyExit --> WriteSummary
    WriteSummary --> End
```

**Sources**: [services/action-builder/scripts/crawl-playbook-batch.ts:225-359]()

### Command-Line Usage

```bash
# Basic usage (uses default timeout of 60 minutes per site)
pnpm crawl:batch

# Custom timeout per site
pnpm crawl:batch -- --site-timeout-minutes 30

# Forward args to crawl-playbook.ts
pnpm crawl:batch -- --max-pages 10 --max-depth 2 --concurrency 5

# Custom output directory and summary file
pnpm crawl:batch -- --output ./custom-output --summary-output ./results.json

# Stop on first error (default: continue on error)
pnpm crawl:batch -- --stop-on-error
```

**Command-line arguments:**

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `--site-timeout-minutes` | number | `60` | Per-site execution timeout |
| `--summary-output` | string | `output/batch/crawl_playbook_batch_summary_{timestamp}.json` | Path for batch summary JSON |
| `--stop-on-error` | flag | `false` | Stop on first site failure |
| `--output` | string | `./output` | Output directory (forwarded to crawl-playbook) |
| `--max-pages` | number | - | Max pages to crawl (forwarded) |
| `--max-depth` | number | - | Max crawl depth (forwarded) |
| `--concurrency` | number | - | Concurrent crawl operations (forwarded) |
| `--timeout` | number | - | Navigation timeout (forwarded) |
| `--html-limit` | number | - | HTML character limit (forwarded) |

**Sources**: [services/action-builder/scripts/crawl-playbook-batch.ts:225-266](), [services/action-builder/package.json:21-22]()

### Output Formats

#### Per-Site Output

Each crawl produces two files in `output/sites/{domain}/crawl_playbooks/`:

```
output/
└── sites/
    └── www.example.com/
        └── crawl_playbooks/
            ├── playbook_20260108_153000.yaml
            └── playbook_20260108_153000.json
```

**Sources**: [services/action-builder/scripts/crawl-playbook-batch.ts:103-113]()

#### Batch Summary JSON

```typescript
type BatchSummary = {
  metadata: {
    createdAt: string;          // ISO timestamp
    total: number;              // Total sites processed
    completed: number;          // Successfully completed
    failed: number;             // Failed sites
    timeout: number;            // Timed out sites
    batchArgs: string[];        // Command-line arguments
  };
  results: SiteRunResult[];
};

type SiteRunResult = {
  url: string;                  // Site URL
  status: 'completed' | 'failed' | 'timeout';
  startedAt: string;            // ISO timestamp
  finishedAt: string;           // ISO timestamp
  durationMs: number;           // Execution time
  exitCode: number | null;      // Child process exit code
  signal: NodeJS.Signals | null;
  yamlPath?: string;            // Absolute path to YAML output
  jsonPath?: string;            // Absolute path to JSON output
  error?: string;               // Error message (if failed/timeout)
  data?: unknown;               // Parsed JSON data (if completed)
};
```

**Sources**: [services/action-builder/scripts/crawl-playbook-batch.ts:22-48]()

## Batch Import Workflow

### Execution Flow

```mermaid
graph TD
    Start["Start import-playbook-batch.ts"]
    
    CheckMode{"Mode?"}
    
    subgraph "Mode A: Retry Failed"
        LoadPrevSummary["loadImportRunSummary()<br/>Read previous import summary"]
        FilterFailed["Filter results:<br/>status === 'failed' &&<br/>jsonPath exists"]
        RetryLoop{"For each<br/>failed item"}
        CheckFileA{"File exists?"}
        ImportRetry["runImportOne()<br/>spawn import-playbook.ts"]
        RecordRetry["Record result"]
        NextRetry["Next failed item"]
    end
    
    subgraph "Mode B: New Import"
        ResolveSummary["resolveSummaryPath()<br/>Auto-detect latest or<br/>use --summary arg"]
        LoadCrawlSummary["loadCrawlBatchSummary()<br/>Read crawl summary"]
        FilterCompleted["Filter candidates:<br/>status === 'completed' &&<br/>jsonPath exists"]
        ImportLoop{"For each<br/>candidate"}
        CheckFileB{"File exists?"}
        ImportNew["runImportOne()<br/>spawn import-playbook.ts"]
        RecordImport["Record result"]
        NextImport["Next candidate"]
    end
    
    WriteImportSummary["Write ImportBatchSummary JSON:<br/>metadata + results[]"]
    CheckFailures{"Any<br/>failures?"}
    Exit1["Exit code 1"]
    Exit0["Exit code 0"]
    
    Start --> CheckMode
    
    CheckMode -->|--retry-from| LoadPrevSummary
    LoadPrevSummary --> FilterFailed
    FilterFailed --> RetryLoop
    RetryLoop -->|Yes| CheckFileA
    CheckFileA -->|No| RecordRetry
    CheckFileA -->|Yes| ImportRetry
    ImportRetry --> RecordRetry
    RecordRetry --> NextRetry
    NextRetry --> RetryLoop
    RetryLoop -->|No more| WriteImportSummary
    
    CheckMode -->|Default| ResolveSummary
    ResolveSummary --> LoadCrawlSummary
    LoadCrawlSummary --> FilterCompleted
    FilterCompleted --> ImportLoop
    ImportLoop -->|Yes| CheckFileB
    CheckFileB -->|No| RecordImport
    CheckFileB -->|Yes| ImportNew
    ImportNew --> RecordImport
    RecordImport --> NextImport
    NextImport --> ImportLoop
    ImportLoop -->|No more| WriteImportSummary
    
    WriteImportSummary --> CheckFailures
    CheckFailures -->|Yes| Exit1
    CheckFailures -->|No| Exit0
```

**Sources**: [services/action-builder/scripts/import-playbook-batch.ts:223-428]()

### Command-Line Usage

```bash
# Import from latest crawl summary (auto-detected)
pnpm import:batch

# Import from specific crawl summary
pnpm import:batch -- --summary output/batch/crawl_playbook_batch_summary_xxx.json

# Dry run (validate without importing)
pnpm import:batch -- --dry-run

# Stop on first import failure
pnpm import:batch -- --stop-on-error

# Retry failed imports from previous run
pnpm import:batch -- --retry-from output/batch/import_playbook_batch_summary_xxx.json
```

**Command-line arguments:**

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `--summary` | string | Latest in `output/batch/` | Path to crawl batch summary JSON |
| `--retry-from` | string | - | Path to previous import summary (retry mode) |
| `--dry-run` | flag | `false` | Validate without executing imports |
| `--stop-on-error` | flag | `false` | Stop on first import failure |

**Sources**: [services/action-builder/scripts/import-playbook-batch.ts:223-230](), [services/action-builder/package.json:22]()

### Auto-Detection Logic

When `--summary` is not specified, the system auto-detects the latest crawl summary:

```typescript
// Path resolution logic
function resolveSummaryPath(actionBuilderRoot: string, summaryArg?: string): string {
  if (summaryArg) {
    return path.isAbsolute(summaryArg) ? summaryArg : path.resolve(actionBuilderRoot, summaryArg);
  }

  const batchDir = path.resolve(actionBuilderRoot, 'output', 'batch');
  const files = fs.readdirSync(batchDir)
    .filter((f) => f.startsWith('crawl_playbook_batch_summary_') && f.endsWith('.json'))
    .map((f) => path.join(batchDir, f));

  // Sort by modification time (newest first)
  files.sort((a, b) => fs.statSync(b).mtimeMs - fs.statSync(a).mtimeMs);
  
  return files[0]; // Return most recent
}
```

**Sources**: [services/action-builder/scripts/import-playbook-batch.ts:101-128]()

### Retry Failed Imports

When imports fail, use `--retry-from` to retry only the failed entries:

```bash
# Initial import (some fail)
pnpm import:batch
# Output: import_playbook_batch_summary_20260108153000.json
#   - imported: 45
#   - failed: 5

# Retry only the 5 failed entries
pnpm import:batch -- --retry-from output/batch/import_playbook_batch_summary_20260108153000.json
```

The retry mode:
1. Loads the previous import summary
2. Filters for `status === 'failed'` entries with `jsonPath`
3. Re-executes only those imports
4. Generates a new summary with retry results

**Sources**: [services/action-builder/scripts/import-playbook-batch.ts:243-326]()

### Output Format

#### Import Batch Summary JSON

```typescript
type ImportBatchSummary = {
  metadata: {
    createdAt: string;          // ISO timestamp
    sourceSummaryPath: string;  // Path to source crawl summary
    totalCandidates: number;    // Total items eligible for import
    imported: number;           // Successfully imported
    failed: number;             // Failed imports
    skipped: number;            // Skipped (not completed/no path)
    args: string[];             // Command-line arguments
  };
  results: ImportItemResult[];
};

type ImportItemResult = {
  url: string;                  // Site URL
  status: 'imported' | 'failed' | 'skipped';
  jsonPath?: string;            // Path to input JSON
  exitCode: number | null;      // Child process exit code
  signal: NodeJS.Signals | null;
  startedAt: string;            // ISO timestamp
  finishedAt: string;           // ISO timestamp
  durationMs: number;           // Execution time
  error?: string;               // Error message (if failed)
};
```

**Sources**: [services/action-builder/scripts/import-playbook-batch.ts:54-66]()

## Script Architecture

### Key Functions

#### Crawl Batch Functions

```mermaid
graph LR
    Main["main()"]
    LoadSites["loadSitesFromFile()"]
    ResolveTsx["resolveToxPath()"]
    RunOne["runOneSite()"]
    ExtractPaths["extractSavedPaths()"]
    
    Main --> LoadSites
    Main --> ResolveTsx
    Main --> RunOne
    RunOne --> ExtractPaths
```

| Function | Purpose | Location |
|----------|---------|----------|
| `loadSitesFromFile()` | Parse `crawl-sites.txt`, filter comments/empty lines | [crawl-playbook-batch.ts:54-66]() |
| `resolveToxPath()` | Locate local `tsx` binary or fallback to PATH | [crawl-playbook-batch.ts:95-101]() |
| `runOneSite()` | Spawn child process for single site, capture output | [crawl-playbook-batch.ts:115-223]() |
| `extractSavedPaths()` | Parse stdout for "YAML saved:" and "JSON saved:" lines | [crawl-playbook-batch.ts:103-113]() |

**Sources**: [services/action-builder/scripts/crawl-playbook-batch.ts:54-223]()

#### Import Batch Functions

```mermaid
graph LR
    Main["main()"]
    ResolveSummary["resolveSummaryPath()"]
    LoadCrawl["loadCrawlBatchSummary()"]
    LoadImport["loadImportRunSummary()"]
    ResolveTsx["resolveTsxPath()"]
    RunImport["runImportOne()"]
    
    Main --> ResolveSummary
    Main --> LoadCrawl
    Main --> LoadImport
    Main --> ResolveTsx
    Main --> RunImport
```

| Function | Purpose | Location |
|----------|---------|----------|
| `resolveSummaryPath()` | Auto-detect latest crawl summary or use `--summary` arg | [import-playbook-batch.ts:101-128]() |
| `loadCrawlBatchSummary()` | Parse crawl batch summary JSON, validate structure | [import-playbook-batch.ts:130-137]() |
| `loadImportRunSummary()` | Parse import summary JSON for retry mode | [import-playbook-batch.ts:152-159]() |
| `runImportOne()` | Spawn import-playbook.ts for single entry | [import-playbook-batch.ts:161-221]() |

**Sources**: [services/action-builder/scripts/import-playbook-batch.ts:101-221]()

## Integration with Database

### Data Flow Diagram

```mermaid
graph TD
    CrawlJSON["JSON from crawl-playbook.ts"]
    ImportScript["import-playbook.ts"]
    
    subgraph "Database Tables"
        Sources[("sources")]
        SourceVersions[("source_versions")]
        Documents[("documents")]
        Chunks[("chunks")]
        Pages[("pages")]
        Elements[("elements")]
    end
    
    CrawlJSON --> ImportScript
    ImportScript --> Sources
    ImportScript --> SourceVersions
    ImportScript --> Documents
    ImportScript --> Chunks
    
    Sources --> Pages
    Pages --> Elements
    
    SourceVersions -.references.-> Documents
    SourceVersions -.references.-> Chunks
```

The `import-playbook.ts` script (spawned by `import-playbook-batch.ts`) performs the following database operations:

1. Creates or updates `sources` record with base URL and metadata
2. Creates new `source_versions` record (version management)
3. Imports `documents` (crawled pages) with `source_version_id` foreign key
4. Imports `chunks` (content segments) with embeddings
5. Creates `pages` records for discovered page types
6. Imports `elements` records for discovered UI elements

**Sources**: [services/db/migrations/meta/0018_snapshot.json:96-1453]()

## Error Handling

### Crawl Failures

The batch crawler handles three failure modes:

| Status | Condition | Behavior |
|--------|-----------|----------|
| `timeout` | Execution exceeds `--site-timeout-minutes` | Child process killed with `SIGTERM`, status recorded |
| `failed` | Non-zero exit code from `crawl-playbook.ts` | Exit code and signal recorded, error message captured |
| `completed` | Exit code 0 and JSON file parseable | Data loaded, status set to `completed` |

**Stop-on-error behavior:**
- Default: Continue processing remaining sites even after failures
- With `--stop-on-error`: Break loop immediately on first non-completed status

**Sources**: [services/action-builder/scripts/crawl-playbook-batch.ts:178-223]()

### Import Failures

The batch importer handles failures with retry support:

```typescript
type ImportItemResult = {
  status: 'imported' | 'failed' | 'skipped';
  error?: string;  // Error details for failed/skipped
  // ...
};
```

**Failure scenarios:**

1. **File not found**: JSON path in crawl summary doesn't exist
   - Status: `failed`
   - Error: `"json file not found: {path}"`

2. **Import script failure**: `import-playbook.ts` exits with non-zero code
   - Status: `failed`
   - Error: `"import-playbook exited with code {code}"`

3. **Skipped entries**: Crawl status not `completed` or no `jsonPath`
   - Status: `skipped`
   - Error: `"skipped: crawl status={status}"` or `"skipped: jsonPath missing"`

**Retry logic:**
```bash
# Retry failed imports preserves attempt history
pnpm import:batch -- --retry-from output/batch/import_playbook_batch_summary_xxx.json
```

**Sources**: [services/action-builder/scripts/import-playbook-batch.ts:161-221](), [services/action-builder/scripts/import-playbook-batch.ts:243-326]()

## Comparison with Coordinator Pipeline

| Aspect | Batch Scripts | Coordinator Pipeline |
|--------|--------------|---------------------|
| **Execution Model** | Sequential (one site at a time) | Concurrent (max N build tasks, max M recordings) |
| **Target Use Case** | Bulk external site crawling | Continuous build pipeline for tracked sources |
| **Crawl vs Import** | Separate phases (can be offline) | Integrated (build_tasks → recording_tasks) |
| **Database Integration** | Manual import step required | Automatic via DbWriter |
| **Retry Mechanism** | Manual retry with `--retry-from` | Automatic retry up to `maxAttempts` |
| **Task Tracking** | JSON summary files | `build_tasks` and `recording_tasks` tables |
| **Failure Recovery** | Requires manual retry run | Automatic stale detection and recovery |
| **Resource Control** | Timeout per site | Concurrency limits + timeout per task |
| **Output Format** | YAML + JSON files | YAML files + database records |

The batch scripts are best suited for:
- Initial bulk ingestion of external sites
- One-time crawl operations
- Development and testing workflows
- Situations where crawl and import should be separated

The coordinator pipeline (see [3.2.1](#3.2.1)) is best suited for:
- Production build pipelines
- Continuous updates of tracked sources
- High-throughput parallel processing
- Automatic failure recovery

**Sources**: [services/action-builder/README.md:154-202](), [services/action-builder/scripts/crawl-playbook-batch.ts:1-360](), [services/action-builder/scripts/import-playbook-batch.ts:1-434]()

---

# Page: Playbook Builder Service

# Playbook Builder Service

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [services/action-builder/src/task-worker/utils/prompt-builder.ts](services/action-builder/src/task-worker/utils/prompt-builder.ts)
- [services/db/src/models/build-task.ts](services/db/src/models/build-task.ts)
- [services/playbook-builder/scripts/worker.ts](services/playbook-builder/scripts/worker.ts)
- [services/playbook-builder/src/analyzer/page-analyzer.ts](services/playbook-builder/src/analyzer/page-analyzer.ts)
- [services/playbook-builder/src/controller/playbook-task-controller.ts](services/playbook-builder/src/controller/playbook-task-controller.ts)
- [services/playbook-builder/src/discoverer/capabilities-discoverer.ts](services/playbook-builder/src/discoverer/capabilities-discoverer.ts)
- [services/playbook-builder/src/discoverer/page-discoverer.ts](services/playbook-builder/src/discoverer/page-discoverer.ts)
- [services/playbook-builder/src/playbook-builder.ts](services/playbook-builder/src/playbook-builder.ts)
- [services/playbook-builder/src/types/index.ts](services/playbook-builder/src/types/index.ts)

</details>



## Purpose and Scope

The Playbook Builder Service is responsible for generating comprehensive documentation ("playbooks") for websites by discovering pages through recursive navigation and producing structured markdown documents that describe each page's purpose, capabilities, and structure. This service operates during the `knowledge_build` stage of the build pipeline and produces content that is stored as `documents` and `chunks` in the database with embeddings for semantic search.

This page covers the playbook-builder service architecture, components, and how it integrates with the build pipeline. For information about recording UI element selectors, see [Action Builder Service](#3.2). For details about the task orchestration system that manages both services, see [Task Execution Pipeline](#3.2.1).

Sources: [services/playbook-builder/src/playbook-builder.ts:1-10]()

---

## Service Overview

The Playbook Builder Service generates documentation by:

1. **Page Discovery** - Starting from a base URL, recursively discovers navigable pages up to a configured depth using LLM vision analysis
2. **Playbook Generation** - For each discovered page, generates a 7-section "Playbook" document using LLM analysis of screenshots and HTML
3. **Storage** - Saves playbooks as `documents` with associated `chunks` in the database, generating embeddings for search

The service differs fundamentally from the Action Builder Service:

| Aspect | Playbook Builder | Action Builder |
|--------|------------------|----------------|
| **Goal** | Document what pages exist and what they do | Record UI element selectors for automation |
| **Output** | Markdown documentation (playbooks) | Element records with selectors |
| **Stage** | `knowledge_build` (first) | `action_build` (second) |
| **Depth** | Explores entire site structure | Processes individual chunks |
| **Database** | Creates `documents` and `chunks` | Creates `pages` and `elements` |

Sources: [services/playbook-builder/src/playbook-builder.ts:1-30](), [README.md:42-47]()

---

## Architecture

### Component Diagram

```mermaid
graph TB
    subgraph "Entry Point"
        Worker["PlaybookTaskController<br/>(worker.ts)"]
    end
    
    subgraph "Main Orchestrator"
        PlaybookBuilder["PlaybookBuilder<br/>(playbook-builder.ts)"]
    end
    
    subgraph "Discovery Components"
        PageDiscoverer["PageDiscoverer<br/>(page-discoverer.ts)"]
        CapabilitiesDiscoverer["CapabilitiesDiscoverer<br/>(capabilities-discoverer.ts)"]
    end
    
    subgraph "Infrastructure"
        BrowserAdapter["BrowserAdapter<br/>(StagehandBrowser or<br/>AgentCoreBrowser)"]
        AIClient["AIClient<br/>(brain/ai-client.ts)"]
        EmbeddingProvider["EmbeddingProvider<br/>(OpenAI embeddings)"]
        Storage["Storage<br/>(storage/index.ts)"]
    end
    
    subgraph "Database Tables"
        BuildTasks[("build_tasks")]
        Sources[("sources")]
        SourceVersions[("source_versions")]
        Documents[("documents")]
        Chunks[("chunks")]
    end
    
    Worker -->|"polls tasks<br/>stage=init or<br/>knowledge_build"| BuildTasks
    Worker -->|"creates and runs"| PlaybookBuilder
    
    PlaybookBuilder -->|"uses"| PageDiscoverer
    PlaybookBuilder -->|"uses"| CapabilitiesDiscoverer
    PlaybookBuilder -->|"navigates pages"| BrowserAdapter
    PlaybookBuilder -->|"saves results"| Storage
    
    PageDiscoverer -->|"analyzes screenshots"| AIClient
    CapabilitiesDiscoverer -->|"analyzes screenshots"| AIClient
    
    PlaybookBuilder -->|"generates embeddings"| EmbeddingProvider
    
    Storage -->|"writes to"| Documents
    Storage -->|"writes to"| Chunks
    Storage -->|"creates/updates"| SourceVersions
    Storage -->|"reads/writes"| Sources
    
    BuildTasks -.->|"references"| Sources
    BuildTasks -.->|"references"| SourceVersions
```

**Architecture Overview**: The service uses a worker pattern where `PlaybookTaskController` polls the `build_tasks` table for pending tasks, then instantiates and runs `PlaybookBuilder` for each task. The main orchestrator uses two discoverers (`PageDiscoverer` and `CapabilitiesDiscoverer`) which leverage browser automation and AI vision models to analyze pages. Results are persisted through the `Storage` layer to the database.

Sources: [services/playbook-builder/src/playbook-builder.ts:30-77](), [services/playbook-builder/src/controller/playbook-task-controller.ts:1-11]()

---

## Main Components

### PlaybookBuilder

The `PlaybookBuilder` class is the main orchestrator located at [services/playbook-builder/src/playbook-builder.ts:30-272]().

**Key Responsibilities:**
- Initialize browser and AI client based on environment
- Create or get source version
- Recursively discover pages using BFS (breadth-first search)
- Generate playbooks for each discovered page
- Generate embeddings and persist results

**Configuration Interface:**

```typescript
interface PlaybookBuilderConfig {
  sourceId: number;              // Source ID to build playbook for
  startUrl: string;              // Starting URL for exploration
  headless?: boolean;            // Browser headless mode
  maxPages?: number;             // Max pages to explore (default: 10)
  maxDepth?: number;             // Max depth for recursive discovery (default: 1)
  sourceVersionId?: number;      // Optional version ID
  llmProvider?: string;          // LLM provider (auto-detected if not specified)
  customPrompt?: string;         // Site-specific optimization instructions
}
```

**Main Method - build():**

The `build()` method at [services/playbook-builder/src/playbook-builder.ts:82-182]() orchestrates the entire process:

1. Initialize browser using `createBrowserAuto()` (auto-detects StagehandBrowser or AgentCoreBrowser)
2. Create or get `source_version` using `storage.createVersion()`
3. Discover pages recursively via `discoverPagesRecursively()`
4. For each discovered page:
   - Navigate using `browser.navigate()`
   - Capture screenshot with `browser.screenshot()`
   - Get page content with `browser.getContent()`
   - Generate playbook using `capabilitiesDiscoverer.discover()`
   - Generate embedding if `OPENAI_API_KEY` is available
   - Save as document+chunk using `storage.createPlaybook()`
5. Return `PlaybookBuildResult` with playbook count and IDs

Sources: [services/playbook-builder/src/playbook-builder.ts:30-182](), [services/playbook-builder/src/types/index.ts:8-33]()

### Page Discovery Process

The `discoverPagesRecursively()` method at [services/playbook-builder/src/playbook-builder.ts:188-271]() implements a BFS algorithm:

```mermaid
graph TB
    Start["Initialize<br/>visitedUrls = Set()<br/>allPages = []<br/>queue = [(startUrl, 0)]"]
    
    CheckQueue{"queue.length > 0<br/>AND<br/>allPages.length < maxPages?"}
    
    Dequeue["current = queue.shift()"]
    
    CheckDepth{"current.depth >= maxDepth?"}
    
    Navigate["browser.navigate(current.url)"]
    Screenshot["screenshot = browser.screenshot()"]
    GetContent["content = browser.getContent()"]
    
    DiscoverPages["discoveredPages =<br/>pageDiscoverer.discover(<br/>screenshot, content, url)"]
    
    ForEach["For each discovered page"]
    
    CheckVisited{"normalizeUrl in visitedUrls<br/>OR<br/>!isSameDomain?"}
    
    AddToQueue["visitedUrls.add(url)<br/>allPages.push(page)<br/>if depth+1 < maxDepth:<br/>  queue.push((url, depth+1))"]
    
    CheckMaxPages{"allPages.length >= maxPages?"}
    
    Return["return allPages"]
    
    Start --> CheckQueue
    CheckQueue -->|"yes"| Dequeue
    CheckQueue -->|"no"| Return
    
    Dequeue --> CheckDepth
    CheckDepth -->|"yes (skip)"| CheckQueue
    CheckDepth -->|"no"| Navigate
    
    Navigate --> Screenshot
    Screenshot --> GetContent
    GetContent --> DiscoverPages
    
    DiscoverPages --> ForEach
    ForEach --> CheckVisited
    CheckVisited -->|"yes (skip)"| ForEach
    CheckVisited -->|"no"| AddToQueue
    AddToQueue --> CheckMaxPages
    CheckMaxPages -->|"yes"| Return
    CheckMaxPages -->|"no"| ForEach
    ForEach -.->|"all pages processed"| CheckQueue
```

**Key Features:**
- BFS ensures pages at depth N are processed before depth N+1
- URL normalization using `normalizeUrl()` prevents duplicate visits
- Domain checking using `isSameDomain()` prevents external links
- Early termination when `maxPages` reached

Sources: [services/playbook-builder/src/playbook-builder.ts:188-271]()

### PageDiscoverer

The `PageDiscoverer` class at [services/playbook-builder/src/discoverer/page-discoverer.ts:77-191]() identifies navigable pages from the current page.

**Tool Definition:**

Uses the `register_discovered_pages` tool call with this schema at [services/playbook-builder/src/discoverer/page-discoverer.ts:31-72]():

```typescript
{
  name: 'register_discovered_pages',
  parameters: {
    pages: [{
      semanticId: string,    // e.g., 'home', 'search', 'listing_detail'
      name: string,          // Human-readable name
      description: string,   // Page purpose
      url: string,           // URL or pattern
      navigation: string     // How to reach this page
    }]
  }
}
```

**Process:**
1. Extract navigation HTML using `extractNavigationHtml()` - finds `<nav>`, `<header>`, `<footer>`, `<a>` tags
2. Send screenshot + simplified HTML to LLM with system prompt
3. Append custom prompt if provided via `config.playbookBuilderPrompt`
4. Parse tool call response to get discovered pages
5. Normalize URLs to absolute using base URL

Sources: [services/playbook-builder/src/discoverer/page-discoverer.ts:77-191]()

### CapabilitiesDiscoverer

The `CapabilitiesDiscoverer` class at [services/playbook-builder/src/discoverer/capabilities-discoverer.ts:84-245]() generates comprehensive 7-section playbooks for each page.

**7-Section Playbook Format:**

Defined in the system prompt at [services/playbook-builder/src/discoverer/capabilities-discoverer.ts:23-79]():

```
### 0. Page URL
- URL with query parameters and dynamic params

### 1. Page Overview
- Core business objective in one sentence

### 2. Page Function Summary
- Function list with brief descriptions

### 3. Page Structure Summary
- Layout modules with CSS selectors

### 4. DOM Structure Instance
- Pattern recognition for different states
- Simplified HTML snippets

### 5. Parsing & Processing Summary
- Data retrieval scenarios (direct/interaction/implicit)
- Compatible parsing logic

### 6. Operation Summary
- Interactive operations (input/click/hover)
- Target selectors and expected results
```

**Generation Process:**

The `discover()` method at [services/playbook-builder/src/discoverer/capabilities-discoverer.ts:97-165]():

1. Simplify HTML using `getSimplifiedHTML()` - removes scripts, styles, SVG, images, inline styles
2. Build user prompt with page URL, title, and HTML structure
3. Append custom prompt if provided via `config.playbookBuilderPrompt`
4. Send to LLM with vision (no tool calls - direct markdown response)
5. Extract description from Section 1 using `extractDescription()`
6. Extract capabilities from Section 2 using `extractCapabilities()`
7. Return `PageCapabilities` with full playbook markdown

**PageCapabilities Interface:**

```typescript
interface PageCapabilities {
  description: string;      // Extracted from Section 1: Page Overview
  capabilities: string[];   // Extracted from Section 2: Page Function Summary
  playbook?: string;        // Full 7-section markdown document
  // Legacy fields (deprecated):
  functionalAreas?: string[];
  scenarios?: UserScenario[];
  prerequisites?: string[];
}
```

Sources: [services/playbook-builder/src/discoverer/capabilities-discoverer.ts:84-245](), [services/playbook-builder/src/types/index.ts:85-129]()

---

## PlaybookTaskController

The `PlaybookTaskController` at [services/playbook-builder/src/controller/playbook-task-controller.ts:51-561]() implements the worker pattern for continuous task processing.

### Task Controller State Machine

```mermaid
stateDiagram-v2
    [*] --> idle
    idle --> polling: start()
    polling --> processing: claim task
    processing --> polling: task complete
    processing --> stopping: stop()
    polling --> stopping: stop()
    stopping --> stopped: cleanup
    stopped --> [*]
```

### Polling and Claiming

**Poll Query** at [services/playbook-builder/src/controller/playbook-task-controller.ts:174-203]():

Polls for tasks matching:
```sql
WHERE (
  (stage = 'init' AND stageStatus = 'pending')
  OR (stage = 'knowledge_build' AND stageStatus = 'pending')
)
ORDER BY createdAt
LIMIT 1
```

**Claim Task** at [services/playbook-builder/src/controller/playbook-task-controller.ts:309-330]():

Uses optimistic locking:
```sql
UPDATE build_tasks
SET 
  stage = 'knowledge_build',
  stageStatus = 'running',
  knowledgeStartedAt = NOW(),
  updatedAt = NOW()
WHERE id = ? AND stageStatus = 'pending'
RETURNING id
```

This prevents race conditions when multiple workers try to claim the same task.

Sources: [services/playbook-builder/src/controller/playbook-task-controller.ts:174-330]()

### Task Execution Flow

```mermaid
sequenceDiagram
    participant Controller as PlaybookTaskController
    participant DB as build_tasks table
    participant Source as sources table
    participant Builder as PlaybookBuilder
    participant Storage as Storage
    
    Controller->>DB: pollTask()
    DB-->>Controller: BuildTask (stage=init)
    
    Controller->>DB: claimTask() with optimistic lock
    DB-->>Controller: claimed=true
    
    Controller->>Source: findOrCreateSource()
    Source-->>Controller: sourceId
    
    Controller->>Builder: new PlaybookBuilder(config)
    Controller->>Builder: build()
    
    activate Builder
    Builder->>Builder: discoverPagesRecursively()
    Builder->>Builder: for each page: generate playbook
    Builder->>Storage: createPlaybook()
    Builder-->>Controller: PlaybookBuildResult
    deactivate Builder
    
    Controller->>DB: updateTaskSuccess()<br/>(stage=knowledge_build,<br/>stageStatus=completed)
    DB-->>Controller: updated
```

**Key Steps in executeTask()** at [services/playbook-builder/src/controller/playbook-task-controller.ts:209-303]():

1. **Claim task** - Optimistic lock to prevent duplicate execution
2. **Find or create source** - If `sourceId` is null, call `findOrCreateSource()` which:
   - Extracts domain from URL
   - Searches for existing source by `baseUrl`, `name`, or `domain`
   - Creates new source if not found
   - Updates task with `sourceId`
3. **Create PlaybookBuilder** - Extract config from `task.config`:
   - `playbookMaxPages` → `maxPages`
   - `playbookMaxDepth` → `maxDepth`
   - `playbookHeadless` → `headless`
   - `playbookBuilderPrompt` → `customPrompt`
4. **Execute build** - Call `builder.build()`
5. **Update task status** - Set to `knowledge_build/completed`
6. **Start heartbeat** - Update `updatedAt` every 60 seconds

Sources: [services/playbook-builder/src/controller/playbook-task-controller.ts:209-303](), [services/playbook-builder/src/controller/playbook-task-controller.ts:458-524]()

### Error Handling and Retry

At [services/playbook-builder/src/controller/playbook-task-controller.ts:349-376]():

```typescript
async handleTaskError(taskId, error, retryCount) {
  if (retryCount < maxRetries) {  // default: 3
    // Reset to pending for retry
    UPDATE build_tasks
    SET 
      stage = 'knowledge_build',
      stageStatus = 'pending',
      config = config || { _retryCount, _lastError }
  } else {
    // Permanent failure
    UPDATE build_tasks
    SET 
      stage = 'error',
      stageStatus = 'error',
      errorMessage = error.message
  }
}
```

Sources: [services/playbook-builder/src/controller/playbook-task-controller.ts:349-401]()

---

## Build Pipeline Integration

### Build Task Stage Progression

The Playbook Builder Service operates during the `knowledge_build` stage of the build pipeline:

```mermaid
graph LR
    Init["stage=init<br/>stageStatus=pending"]
    Knowledge["stage=knowledge_build<br/>stageStatus=running"]
    KnowledgeComplete["stage=knowledge_build<br/>stageStatus=completed"]
    Action["stage=action_build<br/>stageStatus=running"]
    Complete["stage=completed<br/>stageStatus=completed"]
    Error["stage=error<br/>stageStatus=error"]
    
    Init -->|"PlaybookTaskController<br/>claims task"| Knowledge
    Knowledge -->|"build() success"| KnowledgeComplete
    Knowledge -->|"error, retryCount<maxRetries"| Init
    Knowledge -->|"error, max retries exceeded"| Error
    
    KnowledgeComplete -->|"Coordinator<br/>spawns BuildTaskRunner"| Action
    Action -->|"all recording_tasks done"| Complete
```

**Stage Definitions** from [services/db/src/models/build-task.ts:112-117]():

| Stage | Description |
|-------|-------------|
| `init` | Initial state, waiting for knowledge build |
| `knowledge_build` | Playbook building in progress |
| `action_build` | Action builder recording in progress (next stage) |
| `completed` | All stages completed |
| `error` | Permanent error (max retries exceeded) |

Sources: [services/db/src/models/build-task.ts:18-117]()

### BuildTaskConfig for Playbook Builder

Configuration fields at [services/db/src/models/build-task.ts:141-162]():

```typescript
interface BuildTaskConfig {
  // Playbook Builder Config
  playbookMaxPages?: number;        // Max pages to process (default: 10)
  playbookMaxDepth?: number;        // Max depth for discovery (default: 1)
  playbookHeadless?: boolean;       // Run browser in headless mode
  playbookBuilderPrompt?: string;   // Site-specific optimization instructions
  
  // Action Builder Config (used by later stage)
  actionBuilderPrompt?: string;
  
  // Retry tracking (internal)
  _retryCount?: number;
  _lastError?: string;
  _errorAt?: string;
}
```

**Custom Prompt Usage:**

The `playbookBuilderPrompt` field is appended to LLM prompts in:
1. `PageDiscoverer` at [services/playbook-builder/src/discoverer/page-discoverer.ts:96-99]()
2. `CapabilitiesDiscoverer` at [services/playbook-builder/src/discoverer/capabilities-discoverer.ts:112-114]()

This allows site-specific instructions like:
```
"Focus on the main navigation menu and ignore promotional banners"
```

Sources: [services/db/src/models/build-task.ts:131-166](), [services/playbook-builder/src/discoverer/page-discoverer.ts:77-99](), [services/playbook-builder/src/discoverer/capabilities-discoverer.ts:97-114]()

---

## Storage and Data Flow

### Storage Operations

The `Storage` interface provides methods for persisting playbooks:

**createPlaybook()** creates both `document` and `chunk`:

```typescript
async createPlaybook({
  sourceId: number,
  sourceVersionId: number,
  url: string,
  title: string,
  description: string,
  chunkContent: string,      // Full playbook markdown
  embedding?: number[],      // 1536-dim vector from OpenAI
  embeddingModel?: string    // 'text-embedding-3-small'
})
```

**Database Schema Mapping:**

```mermaid
graph LR
    subgraph "Input Data"
        PlaybookResult["PlaybookBuildResult<br/>from build()"]
        PageData["Page Info<br/>(url, title, description)"]
        PlaybookMarkdown["7-section Playbook<br/>(markdown string)"]
        Embedding["Embedding Vector<br/>(number[1536])"]
    end
    
    subgraph "Storage Layer"
        CreatePlaybook["storage.createPlaybook()"]
    end
    
    subgraph "Database Tables"
        Documents["documents<br/>id, sourceId, sourceVersionId,<br/>url, title, description"]
        Chunks["chunks<br/>id, documentId, sourceVersionId,<br/>content, embedding,<br/>chunkType='playbook'"]
    end
    
    PlaybookResult --> CreatePlaybook
    PageData --> CreatePlaybook
    PlaybookMarkdown --> CreatePlaybook
    Embedding --> CreatePlaybook
    
    CreatePlaybook -->|"INSERT INTO<br/>documents"| Documents
    CreatePlaybook -->|"INSERT INTO<br/>chunks"| Chunks
    
    Documents -->|"documentId"| Chunks
```

**Chunk Type:**

Playbooks are stored with `chunkType = 'playbook'` to distinguish them from other content chunks. This enables filtering during search and retrieval.

Sources: [services/playbook-builder/src/playbook-builder.ts:146-157]()

### Embedding Generation

At [services/playbook-builder/src/playbook-builder.ts:62-72]():

```typescript
if (process.env.OPENAI_API_KEY) {
  this.embedding = createEmbeddingProvider({ provider: 'openai' });
  // Uses model: 'text-embedding-3-small'
}
```

Embeddings are generated for the full playbook content:
```typescript
const chunkContent = capabilities.playbook || buildChunkContent(...);
const result = await this.embedding.embed(chunkContent);
embedding = result.embedding;  // number[1536]
```

This enables semantic search over playbook documentation in the API service.

Sources: [services/playbook-builder/src/playbook-builder.ts:62-144]()

---

## Worker Process

### CLI Entry Point

The worker script at [services/playbook-builder/scripts/worker.ts:1-83]() provides the CLI entry point:

**Usage:**
```bash
cd services/playbook-builder
pnpm dev
```

**Startup Sequence:**
1. Load environment variables from `.env`
2. Create controller: `createPlaybookTaskController()`
3. Configure callbacks:
   - `onTaskStart` - Log task start
   - `onTaskComplete` - Log results (playbook count, duration)
   - `onTaskError` - Log error and retry count
4. Setup graceful shutdown handlers for SIGINT/SIGTERM
5. Start continuous polling: `controller.start(options)`

**Graceful Shutdown:**

When SIGINT/SIGTERM received:
1. Call `controller.stop(reason)`
2. Clear poll timer
3. If currently processing:
   - Update task to `stage=error, stageStatus=error`
   - Wait for current execution to finish
4. Clear heartbeat timer
5. Exit with code 0

Sources: [services/playbook-builder/scripts/worker.ts:1-83]()

### Controller Options

```typescript
interface ControllerOptions {
  pollInterval?: number;        // Default: 30000 (30s)
  taskTimeout?: number;         // Default: 0 (no timeout)
  heartbeatInterval?: number;   // Default: 60000 (1min)
  maxRetries?: number;          // Default: 3
  
  // Callbacks
  onProgress?: (taskId, progress) => void;
  onTaskStart?: (taskId) => void;
  onTaskComplete?: (taskId, result) => void;
  onTaskError?: (taskId, error, retryCount) => void;
}
```

Sources: [services/playbook-builder/src/controller/types.ts](), [services/playbook-builder/scripts/worker.ts:52-63]()

---

## Configuration

### Environment Variables

Required:
- `DATABASE_URL` - PostgreSQL connection string (or Neon serverless)
- LLM Provider (one of):
  - `OPENROUTER_API_KEY` - OpenRouter API key
  - `OPENAI_API_KEY` - OpenAI API key (also used for embeddings)
  - `ANTHROPIC_API_KEY` - Anthropic API key
  - `AWS_REGION`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` - For Bedrock

Optional:
- `LLM_PROVIDER` - Force specific provider: 'openrouter' | 'openai' | 'anthropic' | 'bedrock'
- `HEADLESS` - Run browser in headless mode (default: true in production)

**Provider Auto-Detection:**

At [services/playbook-builder/src/playbook-builder.ts:56-59]():

```typescript
const llmProvider = this.config.llmProvider ||
  (process.env.LLM_PROVIDER as 'openrouter' | 'openai' | 'anthropic' | 'bedrock' | undefined);
this.ai = new AIClient({ provider: llmProvider });
// AIClient auto-detects based on available API keys if provider not specified
```

**Browser Auto-Detection:**

At [services/playbook-builder/src/playbook-builder.ts:54]():

```typescript
this.browser = createBrowserAuto({ headless: this.config.headless });
// Returns AgentCoreBrowser in AWS Lambda, StagehandBrowser locally
```

Sources: [services/playbook-builder/src/playbook-builder.ts:41-60]()

### Build Task Configuration

Example configuration for a build task:

```typescript
const buildTask = {
  sourceUrl: 'https://example.com',
  sourceName: 'Example Site',
  sourceCategory: 'any',
  stage: 'init',
  stageStatus: 'pending',
  config: {
    // Playbook builder settings
    playbookMaxPages: 20,
    playbookMaxDepth: 2,
    playbookHeadless: true,
    playbookBuilderPrompt: 'Focus on documentation pages and ignore blog posts',
    
    // Action builder settings (used in next stage)
    actionBuilderPrompt: 'Prioritize form interactions',
  }
}
```

The controller extracts playbook-specific config at [services/playbook-builder/src/controller/playbook-task-controller.ts:246-254]():

```typescript
const config = task.config;
new PlaybookBuilder({
  sourceId: task.sourceId,
  startUrl: task.sourceUrl,
  headless: config.playbookHeadless ?? true,
  maxPages: config.playbookMaxPages ?? 10,
  maxDepth: config.playbookMaxDepth ?? 1,
  customPrompt: config.playbookBuilderPrompt,
});
```

Sources: [services/playbook-builder/src/controller/playbook-task-controller.ts:246-254](), [services/db/src/models/build-task.ts:131-166]()

---

## Comparison with Action Builder

### Architectural Differences

| Aspect | Playbook Builder | Action Builder |
|--------|------------------|----------------|
| **Entry Class** | `PlaybookBuilder` | `BuildTaskRunner` + `QueueWorker` |
| **Task Granularity** | One task = entire site | One build task → 50-100+ recording tasks |
| **Concurrency** | Single worker, sequential pages | Multiple workers, parallel recording tasks |
| **Browser Usage** | Navigate and screenshot each page | Multi-turn interaction loop per chunk |
| **LLM Interaction** | One-shot vision analysis | Multi-turn tool calling (max 30 turns) |
| **Output Format** | Markdown playbooks | Structured element records with selectors |
| **Database Tables** | `documents`, `chunks` | `pages`, `elements` |

### Prompt Differences

**Playbook Builder** at [services/playbook-builder/src/discoverer/capabilities-discoverer.ts:23-79]():
- Goal: "Generate a standardized Playbook document"
- No tool calls - direct markdown response
- Focuses on WHAT (business objective, functions, structure)
- Sections: Page URL, Overview, Functions, Structure, DOM, Parsing, Operations

**Action Builder** at [services/action-builder/src/task-worker/utils/prompt-builder.ts:19-163]():
- Goal: "Execute task steps while recording UI elements"
- Tool calls: `navigate`, `observe_page`, `interact`, `register_element`
- Focuses on HOW (selectors, interactions, element patterns)
- Safe Mode: distinguish navigation vs destructive actions

Sources: [services/playbook-builder/src/discoverer/capabilities-discoverer.ts:23-79](), [services/action-builder/src/task-worker/utils/prompt-builder.ts:19-163]()

---

## Data Flow Summary

```mermaid
graph TB
    subgraph "Input"
        BuildTask["build_tasks<br/>stage=init<br/>sourceUrl, config"]
    end
    
    subgraph "Playbook Builder Execution"
        Controller["PlaybookTaskController<br/>claims task"]
        Builder["PlaybookBuilder<br/>build()"]
        Discovery["Page Discovery<br/>(BFS, PageDiscoverer)"]
        Generation["Playbook Generation<br/>(CapabilitiesDiscoverer)"]
        Embedding["Embedding Generation<br/>(OpenAI)"]
    end
    
    subgraph "Output"
        Documents["documents table<br/>(url, title, description)"]
        Chunks["chunks table<br/>(content=playbook markdown,<br/>embedding, chunkType='playbook')"]
        TaskUpdated["build_tasks<br/>stage=knowledge_build<br/>stageStatus=completed"]
    end
    
    subgraph "Next Stage"
        Coordinator["Coordinator<br/>(action-builder)"]
        ActionBuild["Action Builder Pipeline<br/>creates recording_tasks"]
    end
    
    BuildTask --> Controller
    Controller --> Builder
    Builder --> Discovery
    Discovery --> Generation
    Generation --> Embedding
    Embedding --> Documents
    Embedding --> Chunks
    Embedding --> TaskUpdated
    
    TaskUpdated -.->|"triggers"| Coordinator
    Coordinator --> ActionBuild
```

**Key Points:**

1. **Task Polling** - Controller continuously polls for `stage=init` or `stage=knowledge_build, status=pending` tasks
2. **Page Discovery** - BFS traversal up to `maxDepth`, respecting domain boundaries
3. **Playbook Generation** - LLM vision analysis produces 7-section markdown documents
4. **Embedding** - OpenAI embeddings enable semantic search in API service
5. **Stage Transition** - Completion updates task to `knowledge_build/completed`, triggering action-builder coordinator
6. **Retry Logic** - Up to 3 retries on error before permanent failure

Sources: [services/playbook-builder/src/playbook-builder.ts:82-182](), [services/playbook-builder/src/controller/playbook-task-controller.ts:150-303]()

---

# Page: Playbook Task Controller

# Playbook Task Controller

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [services/action-builder/src/task-worker/utils/prompt-builder.ts](services/action-builder/src/task-worker/utils/prompt-builder.ts)
- [services/db/src/models/build-task.ts](services/db/src/models/build-task.ts)
- [services/playbook-builder/scripts/worker.ts](services/playbook-builder/scripts/worker.ts)
- [services/playbook-builder/src/analyzer/page-analyzer.ts](services/playbook-builder/src/analyzer/page-analyzer.ts)
- [services/playbook-builder/src/controller/playbook-task-controller.ts](services/playbook-builder/src/controller/playbook-task-controller.ts)
- [services/playbook-builder/src/discoverer/capabilities-discoverer.ts](services/playbook-builder/src/discoverer/capabilities-discoverer.ts)
- [services/playbook-builder/src/discoverer/page-discoverer.ts](services/playbook-builder/src/discoverer/page-discoverer.ts)
- [services/playbook-builder/src/playbook-builder.ts](services/playbook-builder/src/playbook-builder.ts)
- [services/playbook-builder/src/types/index.ts](services/playbook-builder/src/types/index.ts)

</details>



## Purpose and Scope

The `PlaybookTaskController` is responsible for orchestrating the execution of playbook generation tasks within the Playbook Builder service. It polls the database for pending build tasks, claims them using optimistic locking, executes the `PlaybookBuilder`, and manages the task lifecycle including success, failure, and retry scenarios.

For information about the overall Playbook Builder service architecture, see [Playbook Builder Service](#3.3). For details on the complete Task Execution Pipeline including action-builder coordination, see [Task Execution Pipeline](#3.2.1). For information about the PlaybookBuilder class that performs the actual playbook generation, see the main implementation at [services/playbook-builder/src/playbook-builder.ts:30-272]().

**Sources:** [services/playbook-builder/src/controller/playbook-task-controller.ts:1-562]()

---

## Architecture Overview

The `PlaybookTaskController` acts as a polling-based task orchestrator that bridges the database task queue and the `PlaybookBuilder` execution engine. It operates independently as a long-running worker process, continuously polling for tasks that require playbook generation.

### System Context Diagram

```mermaid
graph TB
    Database["PostgreSQL<br/>build_tasks table"]
    Controller["PlaybookTaskController"]
    Builder["PlaybookBuilder"]
    SourceTable["sources table"]
    
    Database -->|"poll tasks<br/>(stage=init OR<br/>stage=knowledge_build<br/>status=pending)"| Controller
    Controller -->|"claim task<br/>(optimistic lock)"| Database
    Controller -->|"create & execute"| Builder
    Controller -->|"find or create"| SourceTable
    Builder -->|"generate playbooks"| Database
    Controller -->|"update status<br/>(running/completed/error)"| Database
    Controller -->|"heartbeat<br/>(every 60s)"| Database
```

**Sources:** [services/playbook-builder/src/controller/playbook-task-controller.ts:1-562](), [services/db/src/models/build-task.ts:18-94]()

---

## Controller States

The `PlaybookTaskController` implements a state machine with five distinct states. The controller transitions between these states based on external commands and task processing outcomes.

### State Machine

```mermaid
stateDiagram-v2
    [*] --> idle
    idle --> polling: start()
    polling --> processing: "task claimed"
    processing --> polling: "task complete"
    polling --> stopping: stop()
    processing --> stopping: stop()
    stopping --> stopped: "cleanup complete"
    stopped --> [*]
    
    note right of polling
        Continuously polls for
        pending tasks every 30s
    end note
    
    note right of processing
        Executing PlaybookBuilder
        with heartbeat updates
    end note
```

The `ControllerState` type is defined in [services/playbook-builder/src/controller/types.ts]() with the following values:

| State | Description |
|-------|-------------|
| `idle` | Initial state, not yet started |
| `polling` | Actively polling database for pending tasks |
| `processing` | Currently executing a task |
| `stopping` | Graceful shutdown in progress |
| `stopped` | Controller has stopped |

**Sources:** [services/playbook-builder/src/controller/playbook-task-controller.ts:52-144]()

---

## Task Lifecycle

The controller manages build tasks through a multi-stage lifecycle, coordinating with the `build_tasks` table in PostgreSQL.

### Task Lifecycle Flow

```mermaid
graph TB
    Poll["pollTask()<br/>SELECT from build_tasks<br/>WHERE stage IN (init, knowledge_build)<br/>AND stageStatus = pending"]
    Claim["claimTask()<br/>UPDATE build_tasks<br/>SET stage=knowledge_build<br/>stageStatus=running<br/>WHERE stageStatus=pending"]
    FindSource["findOrCreateSource()<br/>Lookup or create in sources table"]
    Execute["executeTask()<br/>Create PlaybookBuilder<br/>Execute build()"]
    Success["updateTaskSuccess()<br/>SET stageStatus=completed<br/>knowledgeCompletedAt=now()"]
    Error["handleTaskError()<br/>Check retry count"]
    Retry["SET stageStatus=pending<br/>config._retryCount++"]
    Failed["updateTaskError()<br/>SET stage=error<br/>stageStatus=error"]
    
    Poll -->|"task found"| Claim
    Claim -->|"claimed successfully"| FindSource
    Claim -->|"already claimed"| Poll
    FindSource -->|"sourceId assigned"| Execute
    Execute -->|"success"| Success
    Execute -->|"error"| Error
    Error -->|"retries < maxRetries"| Retry
    Error -->|"retries >= maxRetries"| Failed
    Retry --> Poll
```

**Sources:** [services/playbook-builder/src/controller/playbook-task-controller.ts:173-303](), [services/playbook-builder/src/controller/playbook-task-controller.ts:309-420]()

### Build Task Stages

The controller specifically handles tasks in the knowledge building stage:

| Stage | Status | Controller Action |
|-------|--------|-------------------|
| `init` | `pending` | Claim and start execution |
| `knowledge_build` | `pending` | Retry execution (after previous failure) |
| `knowledge_build` | `running` | Currently processing (skip) |
| `knowledge_build` | `completed` | Pass to action-builder (not handled here) |
| `error` | `error` | Terminal failure (not handled here) |

**Sources:** [services/db/src/models/build-task.ts:110-127]()

---

## Optimistic Locking

The controller uses optimistic locking to prevent race conditions when multiple workers poll the same database. The `claimTask()` method performs an atomic compare-and-swap operation.

### Claim Task Implementation

The claim operation is implemented in [services/playbook-builder/src/controller/playbook-task-controller.ts:309-330]():

```typescript
// Pseudocode from claimTask()
UPDATE build_tasks
SET 
  stage = 'knowledge_build',
  stageStatus = 'running',
  knowledgeStartedAt = NOW()
WHERE 
  id = taskId 
  AND stageStatus = 'pending'  // ← Optimistic lock condition
RETURNING id
```

Only one worker will successfully update a row where `stageStatus = 'pending'`. Other workers attempting to claim the same task will receive 0 rows in the result set, indicating the task was already claimed.

**Sources:** [services/playbook-builder/src/controller/playbook-task-controller.ts:309-330]()

---

## Controller Configuration

The `PlaybookTaskControllerImpl` accepts configuration through the `ControllerOptions` interface.

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `pollInterval` | `number` | `30000` | Time between polls in milliseconds (30s) |
| `taskTimeout` | `number` | `0` | Task timeout (0 = no timeout) |
| `heartbeatInterval` | `number` | `60000` | Heartbeat update frequency (60s) |
| `maxRetries` | `number` | `3` | Maximum retry attempts before permanent failure |
| `onTaskStart` | `function` | - | Callback when task starts |
| `onTaskComplete` | `function` | - | Callback when task completes |
| `onTaskError` | `function` | - | Callback when task errors |
| `onProgress` | `function` | - | Callback for progress updates |

### Playbook Builder Configuration

The controller reads build configuration from the `build_tasks.config` JSONB field and passes it to `PlaybookBuilder`:

```typescript
// Mapped from build_tasks.config to PlaybookBuilderConfig
{
  sourceId: task.sourceId,              // From task.sourceId
  startUrl: task.sourceUrl,             // From task.sourceUrl
  headless: config.playbookHeadless,    // Default: true
  maxPages: config.playbookMaxPages,    // Default: 10
  maxDepth: config.playbookMaxDepth,    // Default: 1
  customPrompt: config.playbookBuilderPrompt
}
```

**Sources:** [services/playbook-builder/src/controller/playbook-task-controller.ts:34-46](), [services/playbook-builder/src/controller/playbook-task-controller.ts:244-254](), [services/db/src/models/build-task.ts:128-166]()

---

## Source Management

If a task does not have an associated `sourceId`, the controller attempts to find or create a matching source record before execution.

### Source Resolution Algorithm

```mermaid
graph TD
    Start["Task has no sourceId"]
    Extract["Extract domain from task.sourceUrl"]
    Query["Query sources table<br/>WHERE baseUrl = task.sourceUrl<br/>OR name = task.sourceName<br/>OR domain = extracted_domain"]
    Found{"Source found?"}
    Update1["UPDATE build_tasks<br/>SET sourceId = found.id"]
    Create["INSERT INTO sources<br/>name, baseUrl, domain, appUrl"]
    Update2["UPDATE build_tasks<br/>SET sourceId = new.id"]
    Success["Return sourceId"]
    Fail["Return null<br/>(task marked as error)"]
    
    Start --> Extract
    Extract --> Query
    Query --> Found
    Found -->|Yes| Update1
    Found -->|No| Create
    Update1 --> Success
    Create -->|Success| Update2
    Create -->|Error| Fail
    Update2 --> Success
```

This prevents duplicate sources and ensures tasks are properly linked to source records for version tracking.

**Sources:** [services/playbook-builder/src/controller/playbook-task-controller.ts:458-524]()

---

## Error Handling and Retry Logic

The controller implements automatic retry logic with exponential backoff through the `_retryCount` field stored in `build_tasks.config`.

### Retry Decision Flow

```mermaid
graph TD
    TaskError["Task execution throws error"]
    GetRetry["retryCount = config._retryCount + 1"]
    CheckMax{"retryCount < maxRetries?"}
    ResetPending["UPDATE build_tasks<br/>SET stageStatus = pending<br/>config._retryCount++<br/>config._lastError"]
    MarkError["UPDATE build_tasks<br/>SET stage = error<br/>stageStatus = error<br/>errorMessage"]
    
    TaskError --> GetRetry
    GetRetry --> CheckMax
    CheckMax -->|"Yes (retry)"| ResetPending
    CheckMax -->|"No (give up)"| MarkError
    
    ResetPending -.->|"Next poll cycle"| ResetPending
```

### Error State Persistence

Failed tasks store error information in multiple fields:

| Field | Purpose |
|-------|---------|
| `errorMessage` | Top-level error message (TEXT column) |
| `config._retryCount` | Current retry attempt count |
| `config._lastError` | Last error message (for debugging) |
| `config._errorAt` | ISO timestamp of error |

**Sources:** [services/playbook-builder/src/controller/playbook-task-controller.ts:349-401]()

---

## Heartbeat Mechanism

The controller maintains task liveness through periodic heartbeat updates. This allows monitoring systems to detect stale tasks.

### Heartbeat Implementation

The heartbeat runs on a separate timer while a task is processing:

```mermaid
sequenceDiagram
    participant Controller as PlaybookTaskController
    participant Timer as setInterval
    participant DB as build_tasks table
    
    Controller->>Timer: startHeartbeat(taskId)<br/>interval=60000ms
    loop Every 60 seconds
        Timer->>Controller: trigger heartbeat
        Controller->>DB: UPDATE build_tasks<br/>SET updatedAt = NOW()<br/>WHERE id = taskId
    end
    Controller->>Timer: clearHeartbeat()<br/>clearInterval()
```

The `updatedAt` timestamp is used by external monitoring to identify tasks that have not sent a heartbeat within the expected interval (typically 15 minutes in action-builder's stale detection).

**Sources:** [services/playbook-builder/src/controller/playbook-task-controller.ts:426-452]()

---

## Worker Entry Point

The controller is deployed as a long-running worker process through [services/playbook-builder/scripts/worker.ts:1-83]().

### Worker Process Lifecycle

```mermaid
graph LR
    Start["Process start"]
    Create["createPlaybookTaskController()"]
    Start_["controller.start(options)"]
    Poll["Continuous polling loop"]
    Signal["SIGINT/SIGTERM received"]
    Shutdown["controller.stop(reason)"]
    Exit["process.exit(0)"]
    
    Start --> Create
    Create --> Start_
    Start_ --> Poll
    Poll -.->|"graceful shutdown"| Signal
    Signal --> Shutdown
    Shutdown --> Exit
```

### Worker Initialization Code

The worker script sets up event handlers and callbacks:

```typescript
// From worker.ts:44-76
const controller = createPlaybookTaskController();

const controllerOptions = {
  onTaskStart: (taskId) => console.log(`Task #${taskId} started`),
  onTaskComplete: (taskId, result) => console.log(`Task #${taskId} completed`),
  onTaskError: (taskId, error, retryCount) => console.error(`Task #${taskId} error`)
};

// Graceful shutdown on SIGINT/SIGTERM
process.on('SIGINT', () => controller.stop('SIGINT'));
process.on('SIGTERM', () => controller.stop('SIGTERM'));

await controller.start(controllerOptions);
```

The worker can be run locally using `pnpm dev` in the playbook-builder service directory.

**Sources:** [services/playbook-builder/scripts/worker.ts:14-82]()

---

## Database Operations

The controller performs several key database operations on the `build_tasks` table.

### Database Operation Summary

| Operation | SQL Pattern | Method |
|-----------|-------------|--------|
| Poll tasks | `SELECT ... WHERE (stage='init' OR stage='knowledge_build') AND stageStatus='pending' ORDER BY createdAt LIMIT 1` | `pollTask()` |
| Claim task | `UPDATE ... SET stage='knowledge_build', stageStatus='running' WHERE id=? AND stageStatus='pending'` | `claimTask()` |
| Update success | `UPDATE ... SET stageStatus='completed', knowledgeCompletedAt=NOW()` | `updateTaskSuccess()` |
| Update error | `UPDATE ... SET stage='error', stageStatus='error', errorMessage=?` | `updateTaskError()` |
| Reset for retry | `UPDATE ... SET stageStatus='pending', config=config || {...}` | `handleTaskError()` |
| Heartbeat | `UPDATE ... SET updatedAt=NOW() WHERE id=?` | `sendHeartbeat()` |

### Task Status Query

The polling query uses a compound condition to find eligible tasks:

```sql
-- From pollTask()
SELECT * FROM build_tasks
WHERE (
  (stage = 'init' AND stageStatus = 'pending')
  OR 
  (stage = 'knowledge_build' AND stageStatus = 'pending')
)
ORDER BY createdAt
LIMIT 1
```

This retrieves both new tasks (`init`/`pending`) and retry tasks (`knowledge_build`/`pending`).

**Sources:** [services/playbook-builder/src/controller/playbook-task-controller.ts:174-203](), [services/playbook-builder/src/controller/playbook-task-controller.ts:309-420]()

---

## Integration with PlaybookBuilder

Once a task is claimed and source is resolved, the controller creates and executes a `PlaybookBuilder` instance.

### Execution Flow

```mermaid
sequenceDiagram
    participant Controller as PlaybookTaskController
    participant Builder as PlaybookBuilder
    participant Browser as BrowserAdapter
    participant AI as AIClient
    participant DB as Database
    
    Controller->>Builder: new PlaybookBuilder(config)
    Controller->>Builder: build()
    Builder->>Browser: initialize()
    Builder->>Browser: navigate(startUrl)
    Builder->>AI: discover pages (PageDiscoverer)
    Builder->>AI: generate playbook (CapabilitiesDiscoverer)
    Builder->>DB: createPlaybook()<br/>(document + chunk + embedding)
    Builder-->>Controller: PlaybookBuildResult
    Controller->>DB: updateTaskSuccess()
```

The `PlaybookBuilder.build()` method returns a `PlaybookBuildResult` containing:

```typescript
{
  playbookCount: number,      // Number of playbooks created
  sourceVersionId: number,    // Version ID for this build
  playbookIds: number[]       // Document IDs of created playbooks
}
```

This result is stored in the controller's `ProcessingResult` and can be accessed through the `onTaskComplete` callback.

**Sources:** [services/playbook-builder/src/controller/playbook-task-controller.ts:244-280](), [services/playbook-builder/src/playbook-builder.ts:82-182](), [services/playbook-builder/src/types/index.ts:132-142]()

---

## API Reference

### PlaybookTaskController Interface

```typescript
interface PlaybookTaskController {
  // Start the controller with optional configuration
  start(options?: ControllerOptions): Promise<void>;
  
  // Stop the controller gracefully
  stop(reason?: string): Promise<void>;
  
  // Check for and execute one task (non-polling mode)
  checkOnce(): Promise<boolean>;
  
  // Get current controller state
  getState(): ControllerState;
}
```

### Factory Function

```typescript
// Create a new controller instance
function createPlaybookTaskController(): PlaybookTaskController
```

The factory function is the recommended way to instantiate the controller, as it encapsulates the implementation class `PlaybookTaskControllerImpl`.

**Sources:** [services/playbook-builder/src/controller/types.ts](), [services/playbook-builder/src/controller/playbook-task-controller.ts:559-562]()

---

# Page: Browser Automation Layer

# Browser Automation Layer

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.prettierignore](.prettierignore)
- [.prettierrc.json](.prettierrc.json)
- [CLAUDE.md](CLAUDE.md)
- [services/action-builder/scripts/login.ts](services/action-builder/scripts/login.ts)
- [services/action-builder/src/index.ts](services/action-builder/src/index.ts)
- [services/action-builder/src/optimizer/SelectorOptimizer.ts](services/action-builder/src/optimizer/SelectorOptimizer.ts)
- [services/common/browser-profile/package.json](services/common/browser-profile/package.json)
- [services/common/browser-profile/src/BrowserProfileManager.ts](services/common/browser-profile/src/BrowserProfileManager.ts)
- [services/common/browser/package.json](services/common/browser/package.json)
- [services/common/browser/src/adapters/browser-adapter.ts](services/common/browser/src/adapters/browser-adapter.ts)
- [services/common/browser/src/adapters/index.ts](services/common/browser/src/adapters/index.ts)
- [services/common/browser/src/implementations/agent-core-browser.ts](services/common/browser/src/implementations/agent-core-browser.ts)
- [services/common/browser/src/implementations/stagehand-browser.ts](services/common/browser/src/implementations/stagehand-browser.ts)
- [services/common/browser/src/types/browser.ts](services/common/browser/src/types/browser.ts)
- [services/common/browser/test/e2e/stagehand-browser.e2e.test.ts](services/common/browser/test/e2e/stagehand-browser.e2e.test.ts)
- [services/common/browser/test/unit/agent-core-browser.ut.test.ts](services/common/browser/test/unit/agent-core-browser.ut.test.ts)

</details>



## Purpose and Scope

The Browser Automation Layer provides a unified interface for browser automation across multiple backend implementations. This layer abstracts the differences between local Playwright-based automation (via Stagehand) and cloud-based AWS AgentCore automation, allowing services like Action Builder and Playbook Builder to interact with browsers through a consistent API regardless of the underlying implementation.

For information about how the browser layer integrates with recording workflows, see [Action Recording](#3.2.2). For details on the tools that use this layer, see [Recording Tools Reference](#3.2.3).

**Sources:** [services/common/browser/package.json:1-74](), [services/common/browser/src/adapters/browser-adapter.ts:1-24]()

---

## Architecture Overview

The browser automation layer uses a strategy pattern with `BrowserAdapter` as the interface. Two implementations provide different execution environments: `StagehandBrowser` for local development and `AgentCoreBrowser` for cloud deployment.

```mermaid
graph TB
    subgraph "Interface Layer"
        BrowserAdapter["«interface» BrowserAdapter<br/>initialize()<br/>navigate()<br/>observe()<br/>act()<br/>close()"]
    end
    
    subgraph "Local Implementation"
        StagehandBrowser["StagehandBrowser"]
        Stagehand["@browserbasehq/stagehand<br/>Stagehand class"]
        Playwright["playwright<br/>Local Chromium"]
        AISdkClient["AISdkClient<br/>Multi-provider LLM"]
        ProfileMgr["BrowserProfileManager<br/>userDataDir persistence"]
        
        StagehandBrowser --> Stagehand
        StagehandBrowser --> ProfileMgr
        Stagehand --> Playwright
        Stagehand --> AISdkClient
    end
    
    subgraph "Cloud Implementation"
        AgentCoreBrowser["AgentCoreBrowser"]
        PlaywrightBrowser["bedrock-agentcore<br/>PlaywrightBrowser"]
        BedrockClient["@aws-sdk/client-bedrock-runtime<br/>BedrockRuntimeClient"]
        
        AgentCoreBrowser --> PlaywrightBrowser
        AgentCoreBrowser --> BedrockClient
    end
    
    subgraph "LLM Provider Support"
        OpenRouter["OpenRouter API"]
        OpenAI["OpenAI API"]
        Anthropic["Anthropic API"]
        Bedrock["AWS Bedrock"]
    end
    
    BrowserAdapter <|.. StagehandBrowser
    BrowserAdapter <|.. AgentCoreBrowser
    
    AISdkClient -.-> OpenRouter
    AISdkClient -.-> OpenAI
    AISdkClient -.-> Anthropic
    AISdkClient -.-> Bedrock
    BedrockClient -.-> Bedrock
```

**Implementation Selection**

| Implementation | Use Case | Environment | LLM Provider |
|---------------|----------|-------------|--------------|
| `StagehandBrowser` | Local development, testing | Developer machine | OpenRouter, OpenAI, Anthropic, Bedrock |
| `AgentCoreBrowser` | Cloud deployment, scalability | AWS Lambda/ECS | AWS Bedrock (Claude) |

**Sources:** [services/common/browser/src/adapters/browser-adapter.ts:1-254](), [services/common/browser/src/implementations/stagehand-browser.ts:1-112](), [services/common/browser/src/implementations/agent-core-browser.ts:1-69]()

---

## BrowserAdapter Interface

The `BrowserAdapter` interface defines the unified API for all browser automation operations. It combines lifecycle management, navigation, AI-powered element discovery, and direct automation methods.

### Lifecycle Methods

```typescript
interface BrowserAdapter {
  initialize(): Promise<void>;
  close(): Promise<void>;
}
```

**`initialize()`** must be called before any other operations. For `StagehandBrowser`, this creates a Stagehand instance and configures the LLM client. For `AgentCoreBrowser`, this creates the AWS AgentCore client and Bedrock client.

**`close()`** releases browser resources. For `StagehandBrowser`, this closes the Playwright browser. For `AgentCoreBrowser`, this calls `stopSession()` on the AgentCore client.

**Sources:** [services/common/browser/src/adapters/browser-adapter.ts:39-52](), [services/common/browser/src/implementations/stagehand-browser.ts:133-174](), [services/common/browser/src/implementations/agent-core-browser.ts:93-140]()

### Navigation and Page Information

```typescript
interface BrowserAdapter {
  navigate(url: string, options?: NavigateOptions): Promise<void>;
  goBack(): Promise<void>;
  getUrl(): string;
  getTitle(): Promise<string>;
  getContent(): Promise<string>;
}
```

| Method | Description | Implementation Notes |
|--------|-------------|----------------------|
| `navigate()` | Navigate to URL with timeout and waitUntil options | StagehandBrowser: [stagehand-browser.ts:180-197](). AgentCoreBrowser: [agent-core-browser.ts:146-163]() |
| `goBack()` | Navigate back in browser history | StagehandBrowser uses `page.goBack()`. AgentCoreBrowser uses `client.back()` |
| `getUrl()` | Get current page URL (synchronous) | StagehandBrowser: `page.url()`. AgentCoreBrowser: tracks `currentUrl` state |
| `getTitle()` | Get page title | Both use `page.title()` or `evaluate('document.title')` |
| `getContent()` | Get full page HTML | Both use `page.evaluate(() => document.documentElement.outerHTML)` |

**Sources:** [services/common/browser/src/adapters/browser-adapter.ts:54-88](), [services/common/browser/src/implementations/stagehand-browser.ts:180-220](), [services/common/browser/src/implementations/agent-core-browser.ts:146-199]()

### AI Capabilities

The AI capabilities are the core differentiator of this layer. Both implementations provide `observe()` and `act()` methods, but with different underlying mechanisms.

#### observe(instruction: string, timeoutMs?: number): Promise<ObserveResult[]>

Analyzes the page using AI vision to find elements matching the natural language instruction.

**StagehandBrowser Flow:**
1. Calls `stagehand.observe(instruction)` which uses the configured LLM provider
2. Stagehand captures a screenshot and sends it to the LLM with element markers
3. Returns array of `ObserveResult` with XPath selectors
4. Includes retry logic for rate limit errors (3 retries with exponential backoff)

**AgentCoreBrowser Flow:**
1. Takes screenshot using `client.screenshot()`
2. Builds a custom prompt for Bedrock Claude with vision capabilities
3. Sends screenshot + instruction to Bedrock using `InvokeModelCommand`
4. Parses JSON response containing selector, description, method

```mermaid
sequenceDiagram
    participant Client
    participant Browser as "StagehandBrowser / AgentCoreBrowser"
    participant LLM as "LLM Service"
    participant Page as "Browser Page"
    
    Client->>Browser: observe("find the submit button")
    Browser->>Page: screenshot()
    Page-->>Browser: image buffer
    Browser->>LLM: vision request + image + instruction
    LLM-->>Browser: [{selector, description, method}]
    Browser-->>Client: ObserveResult[]
```

**Sources:** [services/common/browser/src/adapters/browser-adapter.ts:146-161](), [services/common/browser/src/implementations/stagehand-browser.ts:334-396](), [services/common/browser/src/implementations/agent-core-browser.ts:396-475]()

#### act(instructionOrAction: string | ActionObject): Promise<unknown>

Executes an action using AI inference or direct selector.

**Natural Language Mode (string instruction):**
```typescript
await browser.act('click the submit button');
```
- Calls `observe()` to find the element
- Executes the suggested action

**Selector Mode (ActionObject):**
```typescript
await browser.act({
  selector: '#submit-btn',
  method: 'click',
  description: 'Submit button'
});
```
- Directly executes the action without AI inference
- Faster and more reliable when selector is known

**Supported Methods:** `click`, `type`, `fill`, `select`, `hover`, `press`, `scroll`, `wait`

**Sources:** [services/common/browser/src/adapters/browser-adapter.ts:163-195](), [services/common/browser/src/implementations/stagehand-browser.ts:407-502](), [services/common/browser/src/implementations/agent-core-browser.ts:482-584]()

### Element Inspection

#### getElementAttributesFromXPath(xpath: string): Promise<ElementAttributes | null>

Extracts comprehensive element metadata from an XPath selector for selector generation and validation.

**Extracted Attributes:**
- `tagName`: HTML tag name (lowercase)
- `id`, `className`: Standard attributes
- `dataTestId`: data-testid attribute
- `ariaLabel`: aria-label attribute
- `placeholder`, `name`: Form element attributes
- `textContent`: Truncated text content
- `dataAttributes`: All data-* attributes (filtered for state)
- `cssSelector`: Generated CSS selector (preferred over XPath)
- `optimizedXPath`: Simplified XPath without positional predicates

**Implementation Details:**

StagehandBrowser uses `page.evaluate()` to run JavaScript in the browser context. It handles iframe elements by detecting `iframe` in the XPath and iterating through `page.frames()`.

AgentCoreBrowser uses `client.evaluate()` to run a script that finds the element via `document.evaluate()`.

**Sources:** [services/common/browser/src/adapters/browser-adapter.ts:200-210](), [services/common/browser/src/implementations/stagehand-browser.ts:508-580](), [services/common/browser/src/implementations/agent-core-browser.ts:589-630]()

### Automation Helpers

```typescript
interface BrowserAdapter {
  wait(ms: number): Promise<void>;
  waitForSelector(selector: string, options?: WaitForSelectorOptions): Promise<void>;
  waitForText(text: string, timeout?: number): Promise<void>;
  scroll(direction: ScrollDirection, amount?: number): Promise<void>;
  scrollToBottom(waitAfterMs?: number): Promise<void>;
  screenshot(options?: ScreenshotOptions): Promise<Buffer>;
  autoClosePopups(): Promise<number>;
  getTokenStats?(): TokenStats | undefined;
}
```

**autoClosePopups()** attempts to detect and close common popup patterns (cookie banners, modals, overlays) using AI observation. Returns the number of popups closed.

**getTokenStats()** returns accumulated token usage for AI operations. Only implemented in `StagehandBrowser` (AgentCoreBrowser returns `undefined` since Bedrock billing is separate).

**Sources:** [services/common/browser/src/adapters/browser-adapter.ts:100-254](), [services/common/browser/src/implementations/stagehand-browser.ts:270-706](), [services/common/browser/src/implementations/agent-core-browser.ts:253-718]()

---

## StagehandBrowser Implementation

`StagehandBrowser` provides local Playwright-based automation with multi-provider LLM support via the Stagehand SDK. It's the primary implementation for development and testing.

### Class Structure

```typescript
export class StagehandBrowser implements BrowserAdapter {
  private stagehand: StagehandInstance | null = null;
  private page: Page | null = null;
  private config: BrowserConfig;
  private lastMetrics: StagehandMetricsSnapshot | null = null;
  private accumulatedInputTokens: number = 0;
  private accumulatedOutputTokens: number = 0;
}
```

**Sources:** [services/common/browser/src/implementations/stagehand-browser.ts:110-127]()

### LLM Provider Configuration

StagehandBrowser supports four LLM providers with automatic resolution based on environment variables:

```mermaid
graph LR
    Init["StagehandBrowser.initialize()"]
    CheckOR["OPENROUTER_API_KEY?"]
    CheckOAI["OPENAI_API_KEY?"]
    CheckBR["AWS credentials?"]
    CheckAnthropic["ANTHROPIC_API_KEY?"]
    Error["throw Error"]
    
    UseOR["Use OpenRouter<br/>modelName: STAGEHAND_MODEL || gpt-4o<br/>baseURL: openrouter.ai"]
    UseOAI["Use OpenAI<br/>modelName: STAGEHAND_MODEL || gpt-4o"]
    UseBR["Use Bedrock<br/>AISdkClient + createAmazonBedrock()<br/>modelName: AWS_BEDROCK_MODEL"]
    UseAnthropic["Use Anthropic<br/>modelName: STAGEHAND_MODEL || claude-sonnet-4"]
    
    Init --> CheckOR
    CheckOR -->|Yes| UseOR
    CheckOR -->|No| CheckOAI
    CheckOAI -->|Yes| UseOAI
    CheckOAI -->|No| CheckBR
    CheckBR -->|Yes| UseBR
    CheckBR -->|No| CheckAnthropic
    CheckAnthropic -->|Yes| UseAnthropic
    CheckAnthropic -->|No| Error
```

**Environment Variables:**

| Variable | Purpose | Default |
|----------|---------|---------|
| `OPENROUTER_API_KEY` | OpenRouter API key (highest priority) | - |
| `OPENAI_API_KEY` | OpenAI API key | - |
| `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` | AWS Bedrock credentials | - |
| `ANTHROPIC_API_KEY` | Anthropic API key | - |
| `STAGEHAND_MODEL` | Override default model name | Provider-specific default |
| `AWS_REGION` | AWS region for Bedrock | `us-east-1` |
| `AWS_BEDROCK_MODEL` | Bedrock model ID | `anthropic.claude-3-5-sonnet-20241022-v2:0` |

**Proxy Support:** If `HTTPS_PROXY` or `HTTP_PROXY` is set, StagehandBrowser creates a proxy-enabled fetch function using `undici.ProxyAgent` for all HTTP requests (OpenAI, OpenRouter, Bedrock).

**Sources:** [services/common/browser/src/implementations/stagehand-browser.ts:743-822](), [services/common/browser/src/implementations/stagehand-browser.ts:877-894]()

### Browser Launch Options

```typescript
private buildBrowserLaunchOptions(): LocalBrowserLaunchOptions {
  const options: LocalBrowserLaunchOptions = {
    headless: this.config.headless,
  };

  if (this.config.proxy) {
    options.proxy = { server: this.config.proxy };
  }

  if (this.config.profile?.enabled) {
    const profileManager = new BrowserProfileManager({ baseDir: profileDir });
    options.userDataDir = profileManager.getProfilePath();
    options.preserveUserDataDir = true;
    options.args = ['--disable-blink-features=AutomationControlled', '--no-first-run'];
    options.ignoreDefaultArgs = ['--enable-automation'];
  }

  return options;
}
```

**Anti-Detection:** When profile is enabled, StagehandBrowser applies anti-detection arguments to make the browser appear less like an automated instance. This is important for sites that block automation.

**Sources:** [services/common/browser/src/implementations/stagehand-browser.ts:824-854]()

### Token Metrics Tracking

StagehandBrowser tracks token usage for AI operations by maintaining a snapshot of Stagehand's metrics before and after each `observe()` or `act()` call.

**Metrics Captured:**
- `observePromptTokens`, `observeCompletionTokens`: Input/output tokens for observe operations
- `actPromptTokens`, `actCompletionTokens`: Input/output tokens for act operations
- `observeReasoningTokens`, `actReasoningTokens`: Reasoning tokens (for models like o1)
- `observeCachedInputTokens`, `actCachedInputTokens`: Prompt caching hits
- `observeInferenceTimeMs`, `actInferenceTimeMs`: LLM inference latency

**Log Format:**
```
[LLM] ✓ | stagehand/observe | tokens: in=1234, out=56, cache_read=890, total=2180 | perf: latency=1234ms, inference=890ms, tps=45.2
```

**Sources:** [services/common/browser/src/implementations/stagehand-browser.ts:939-1052](), [services/common/browser/src/implementations/stagehand-browser.ts:710-718]()

### Error Handling and Retry Logic

StagehandBrowser implements automatic retry for rate limit errors in both `observe()` and `act()` methods:

1. Max 3 retries (4 total attempts)
2. Exponential backoff: 1s, 2s, 4s (capped at 30s)
3. Detection via error message: "too many tokens", "rate limit", "429"
4. Other errors (element not found, timeout) throw immediately without retry

**Custom Error Types:**

```typescript
export class ElementNotFoundError extends Error {
  constructor(message: string, public readonly selector?: string) { }
}

export class ActionExecutionError extends Error {
  constructor(message: string, public readonly action?: string, 
              public readonly originalError?: Error) { }
}
```

**Sources:** [services/common/browser/src/implementations/stagehand-browser.ts:69-91](), [services/common/browser/src/implementations/stagehand-browser.ts:334-396](), [services/common/browser/src/implementations/stagehand-browser.ts:407-494]()

---

## AgentCoreBrowser Implementation

`AgentCoreBrowser` provides cloud-based browser automation using AWS AgentCore Browser Tool and Bedrock Claude for AI capabilities. It's designed for serverless and containerized deployments.

### Class Structure

```typescript
export class AgentCoreBrowser implements BrowserAdapter {
  private client: AgentCoreBrowserClient | null = null;
  private bedrockClient: BedrockRuntimeClient | null = null;
  private initialized: boolean = false;
  private config: AgentCoreBrowserConfig;
  private currentUrl: string = 'about:blank';
}
```

**Configuration Options:**

```typescript
export interface AgentCoreBrowserConfig extends BrowserConfig {
  sessionTimeoutMinutes?: number;  // Default: 15, max: 480 (8 hours)
  region?: string;                 // Default: us-east-1
  bedrockModelId?: string;         // Default: us.anthropic.claude-3-5-sonnet-20241022-v2:0
}
```

**Sources:** [services/common/browser/src/implementations/agent-core-browser.ts:56-87]()

### Initialization

```typescript
async initialize(): Promise<void> {
  this.client = new PlaywrightBrowser({
    region: this.config.region,
  });

  this.bedrockClient = new BedrockRuntimeClient({
    region: this.config.region,
  });

  this.initialized = true;
}
```

AgentCore sessions are created lazily on first navigation, not during initialization. The session timeout is configured when calling navigation methods.

**Sources:** [services/common/browser/src/implementations/agent-core-browser.ts:93-124]()

### Bedrock Vision Integration

AgentCoreBrowser implements `observe()` using Bedrock Claude's vision capabilities rather than delegating to a higher-level SDK:

```mermaid
sequenceDiagram
    participant Client
    participant ACB as "AgentCoreBrowser"
    participant ACClient as "PlaywrightBrowser"
    participant Bedrock as "BedrockRuntimeClient"
    
    Client->>ACB: observe("find login button")
    ACB->>ACClient: screenshot()
    ACClient-->>ACB: Buffer (base64)
    ACB->>ACB: buildObservePrompt(instruction)
    ACB->>Bedrock: InvokeModelCommand<br/>{model, image, prompt}
    Bedrock-->>ACB: JSON response
    ACB->>ACB: parseObserveResponse(content)
    ACB-->>Client: ObserveResult[]
```

**Prompt Template Highlights:**

```
You are helping the user automate the browser by finding elements...

CRITICAL RULES:
- ONLY return elements that actually exist and match the instruction
- If no matching elements exist (e.g., no popup, no cookie banner, no modal), return []
- Do NOT invent or guess elements that are not clearly visible

Response format (if elements found):
[{"selector": "xpath=//button[@id='close']", "description": "Close button", "method": "click"}]

Response format (if NO elements found):
[]
```

This prompt design is critical for preventing false positives, particularly for `autoClosePopups()` which should return `[]` when no popups exist rather than inventing non-existent elements.

**Sources:** [services/common/browser/src/implementations/agent-core-browser.ts:396-475](), [services/common/browser/src/implementations/agent-core-browser.ts:773-795]()

### Response Parsing

AgentCoreBrowser handles Claude's potentially markdown-wrapped responses:

```typescript
private parseObserveResponse(content: string): ObserveResult[] {
  let jsonStr = content.trim();
  
  // Remove markdown code blocks if present
  const jsonMatch = jsonStr.match(/```(?:json)?\s*([\s\S]*?)```/);
  if (jsonMatch) {
    jsonStr = jsonMatch[1].trim();
  }
  
  // Find JSON array
  const arrayMatch = jsonStr.match(/\[[\s\S]*\]/);
  if (!arrayMatch) {
    return [];
  }
  
  const parsed = JSON.parse(arrayMatch[0]);
  
  // Filter out invalid items
  return parsed
    .filter(item => !!item.selector && !!item.description)
    .map(item => ({
      selector: item.selector,
      description: item.description,
      method: item.method || 'click',
      arguments: item.arguments,
    }));
}
```

**Sources:** [services/common/browser/src/implementations/agent-core-browser.ts:800-847]()

### SDK Method Signatures

AWS AgentCore's `PlaywrightBrowser` uses object parameters for all methods rather than positional arguments:

| Playwright API | AgentCore API |
|---------------|---------------|
| `page.goto(url, {waitUntil, timeout})` | `client.navigate({url, waitUntil, timeout})` |
| `page.click(selector)` | `client.click({selector})` |
| `page.fill(selector, value)` | `client.fill({selector, value})` |
| `page.waitForSelector(selector, {timeout, state})` | `client.waitForSelector({selector, timeout, state})` |
| `page.evaluate(script)` | `client.evaluate({script})` |

This affects all method implementations in AgentCoreBrowser.

**Sources:** [services/common/browser/src/implementations/agent-core-browser.ts:146-370]()

### XPath Normalization and Escaping

Both implementations normalize XPath selectors by removing the `xpath=` prefix. AgentCoreBrowser uses `JSON.stringify()` to safely escape strings for JavaScript interpolation:

```typescript
private escapeForJs(str: string): string {
  return JSON.stringify(str);  // Properly escapes quotes, backslashes, special chars
}

private buildElementScript(selector: string, action: string): string {
  const cleanSelector = selector.replace(/^xpath=/, '');
  if (this.isXPathSelector(selector)) {
    return `(() => { 
      const el = document.evaluate(${this.escapeForJs(cleanSelector)}, 
        document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue; 
      ${action} 
    })()`;
  }
  return `(() => { 
    const el = document.querySelector(${this.escapeForJs(cleanSelector)}); 
    ${action} 
  })()`;
}
```

**Sources:** [services/common/browser/src/implementations/agent-core-browser.ts:744-766](), [services/common/browser/test/unit/agent-core-browser.ut.test.ts:479-517]()

---

## Browser Profile Management

`BrowserProfileManager` provides persistent browser profile storage for maintaining login state across sessions. This enables "login once, reuse many times" workflows.

### Purpose and Benefits

Browser profiles store:
- Cookies (authentication tokens, session data)
- localStorage and sessionStorage
- IndexedDB data
- Browser history and cache

Without profiles, each browser session starts fresh and requires re-authentication. With profiles enabled, users can log in once using `pnpm login` and reuse the authenticated state in all subsequent runs.

**Sources:** [services/common/browser-profile/src/BrowserProfileManager.ts:74-99]()

### Class API

```typescript
export class BrowserProfileManager {
  constructor(config?: ProfileConfig);
  
  getProfilePath(): string;
  exists(): boolean;
  ensureDir(): void;
  clear(): void;
  cleanupStaleLocks(): void;
  getInfo(): ProfileInfo;
  getLaunchOptions(options?: {headless?: boolean; proxy?: {server: string}}): Record<string, unknown>;
}
```

**Default Profile Directory:** `.browser-profile` (relative to process.cwd())

**Anti-Detection Constants:**
```typescript
export const ANTI_DETECTION_ARGS = [
  '--disable-blink-features=AutomationControlled',
  '--no-first-run',
];

export const IGNORE_DEFAULT_ARGS = ['--enable-automation'];
```

**Sources:** [services/common/browser-profile/src/BrowserProfileManager.ts:100-238]()

### Lock File Cleanup

Chrome creates lock files (`SingletonLock`, `SingletonSocket`, `SingletonCookie`) to prevent multiple instances from using the same profile. If Chrome crashes, these files may remain and prevent subsequent launches. `cleanupStaleLocks()` removes these files before each launch.

**Sources:** [services/common/browser-profile/src/BrowserProfileManager.ts:151-166]()

### Usage with StagehandBrowser

```typescript
const profileManager = new BrowserProfileManager({ baseDir: '.browser-profile' });

const browser = new StagehandBrowser({
  profile: {
    enabled: true,
    profileDir: '.browser-profile',
  },
});
```

Internally, StagehandBrowser uses the profile manager to configure launch options:

```typescript
if (this.config.profile?.enabled) {
  const profileManager = new BrowserProfileManager({ baseDir: profileDir });
  const profilePath = profileManager.getProfilePath();
  
  profileManager.ensureDir();
  profileManager.cleanupStaleLocks();
  
  options.userDataDir = profilePath;
  options.preserveUserDataDir = true;
  options.args = ANTI_DETECTION_ARGS;
  options.ignoreDefaultArgs = IGNORE_DEFAULT_ARGS;
}
```

**Sources:** [services/common/browser/src/implementations/stagehand-browser.ts:834-851]()

### Login Script

The `login.ts` script provides an interactive CLI for manual login:

```bash
pnpm login                           # Open browser for manual login
pnpm login --url https://airbnb.com  # Open specific URL
pnpm login --clear                   # Clear existing profile and re-login
```

**Workflow:**
1. Creates/clears profile directory
2. Launches browser with profile enabled (headless=false)
3. User manually logs into websites
4. User presses Enter when finished
5. Profile is automatically saved on browser close

**Sources:** [services/action-builder/scripts/login.ts:1-149]()

---

## Configuration and Initialization

### Configuration Objects

```typescript
// Base browser config (used by both implementations)
export interface BrowserConfig {
  headless?: boolean;              // Default: process.env.HEADLESS === 'true'
  proxy?: string;                  // Default: process.env.HTTPS_PROXY || process.env.HTTP_PROXY
  profileDir?: string;             // Default: undefined (no profile)
  timeout?: number;                // Default: 60000
  storageStatePath?: string;       // Default: undefined
  profile?: {
    enabled: boolean;
    profileDir?: string;
  };
}

// AgentCore-specific config
export interface AgentCoreBrowserConfig extends BrowserConfig {
  sessionTimeoutMinutes?: number;  // Default: 15
  region?: string;                 // Default: us-east-1
  bedrockModelId?: string;         // Default: us.anthropic.claude-3-5-sonnet-20241022-v2:0
}
```

**Sources:** [services/common/browser/src/types/browser.ts:9-28](), [services/common/browser/src/implementations/agent-core-browser.ts:56-64]()

### Initialization Patterns

**StagehandBrowser:**

```typescript
const browser = new StagehandBrowser({
  headless: true,
  proxy: 'http://proxy:8080',
  profile: { enabled: true, profileDir: '.browser-profile' },
});

await browser.initialize();  // Creates Stagehand, resolves LLM config
await browser.navigate('https://example.com');
// ... use browser
await browser.close();
```

**AgentCoreBrowser:**

```typescript
const browser = new AgentCoreBrowser({
  region: 'us-west-2',
  sessionTimeoutMinutes: 30,
  bedrockModelId: 'us.anthropic.claude-3-5-sonnet-20241022-v2:0',
});

await browser.initialize();  // Creates clients, but session starts on first navigate
await browser.navigate('https://example.com');
// ... use browser
await browser.close();  // Calls stopSession()
```

**Sources:** [services/common/browser/src/implementations/stagehand-browser.ts:120-174](), [services/common/browser/src/implementations/agent-core-browser.ts:76-140]()

### Environment Variable Precedence

```mermaid
graph TD
    Start["Browser Initialization"]
    
    subgraph "LLM Provider Selection StagehandBrowser"
        OR["OPENROUTER_API_KEY"]
        OAI["OPENAI_API_KEY"]
        BR["AWS_ACCESS_KEY_ID + AWS_SECRET_ACCESS_KEY"]
        ANT["ANTHROPIC_API_KEY"]
    end
    
    subgraph "AgentCore Configuration"
        Region["AWS_REGION || 'us-east-1'"]
        Model["AGENTCORE_BROWSER_MODEL_ID || default"]
    end
    
    subgraph "Common Configuration"
        Headless["HEADLESS === 'true'"]
        Proxy["HTTPS_PROXY || HTTP_PROXY"]
    end
    
    Start --> OR
    OR -->|Set| UseOR["OpenRouter + STAGEHAND_MODEL"]
    OR -->|Not Set| OAI
    OAI -->|Set| UseOAI["OpenAI + STAGEHAND_MODEL"]
    OAI -->|Not Set| BR
    BR -->|Set| UseBR["Bedrock + AWS_BEDROCK_MODEL"]
    BR -->|Not Set| ANT
    ANT -->|Set| UseANT["Anthropic + STAGEHAND_MODEL"]
    ANT -->|Not Set| Fail["throw Error"]
    
    Start --> Headless
    Start --> Proxy
    Start --> Region
    Start --> Model
```

**Sources:** [services/common/browser/src/implementations/stagehand-browser.ts:743-822](), [services/common/browser/src/implementations/agent-core-browser.ts:76-87]()

---

## Common Patterns and Usage

### Basic Navigation and Observation

```typescript
const browser = new StagehandBrowser({ headless: true });
await browser.initialize();

// Navigate
await browser.navigate('https://example.com');

// AI-powered observation
const elements = await browser.observe('find all navigation links');
console.log(elements[0].selector);  // "xpath=//nav//a[1]"

// Extract attributes
const attrs = await browser.getElementAttributesFromXPath(elements[0].selector);
console.log(attrs?.cssSelector);  // "nav a.nav-link"

await browser.close();
```

**Sources:** [services/common/browser/test/e2e/stagehand-browser.e2e.test.ts:63-91](), [services/common/browser/test/e2e/stagehand-browser.e2e.test.ts:179-193]()

### Direct Action Execution

```typescript
// Method 1: Natural language (uses AI)
await browser.act('click the submit button');

// Method 2: Direct selector (faster, no AI inference)
await browser.act({
  selector: '#submit-btn',
  method: 'click',
  description: 'Submit button',
});

// Method 3: Form filling
await browser.act({
  selector: 'input[name="email"]',
  method: 'fill',
  description: 'Email input',
  arguments: ['user@example.com'],
});
```

**Sources:** [services/common/browser/test/e2e/stagehand-browser.e2e.test.ts:295-318](), [services/common/browser/test/unit/agent-core-browser.ut.test.ts:347-411]()

### Error Handling

```typescript
import { ElementNotFoundError, ActionExecutionError } from '@actionbookdev/browser';

try {
  await browser.act('click the non-existent button');
} catch (error) {
  if (error instanceof ElementNotFoundError) {
    console.log(`Element not found: ${error.selector}`);
  } else if (error instanceof ActionExecutionError) {
    console.log(`Action failed: ${error.action}`, error.originalError);
  }
}
```

**Sources:** [services/common/browser/src/implementations/stagehand-browser.ts:69-91]()

### Token Usage Tracking

```typescript
// Only available in StagehandBrowser
const stats = browser.getTokenStats();
if (stats) {
  console.log(`Input tokens: ${stats.input}`);
  console.log(`Output tokens: ${stats.output}`);
  console.log(`Total tokens: ${stats.total}`);
}

// AgentCoreBrowser returns undefined (Bedrock billing is separate)
```

**Sources:** [services/common/browser/src/implementations/stagehand-browser.ts:710-718](), [services/common/browser/src/implementations/agent-core-browser.ts:716-718]()

### Popup Handling

```typescript
// Attempt to close common popups (cookie banners, modals, etc.)
const closedCount = await browser.autoClosePopups();
console.log(`Closed ${closedCount} popups`);

// Returns 0 if no popups found (not an error)
```

The `autoClosePopups()` method uses the same instructions for both implementations:
- "click the close button on any popup or modal"
- "click accept or dismiss on cookie consent banner"
- "click close on any overlay dialog"

**Sources:** [services/common/browser/src/implementations/stagehand-browser.ts:675-706](), [services/common/browser/src/implementations/agent-core-browser.ts:675-710]()

### Implementation Comparison Table

| Feature | StagehandBrowser | AgentCoreBrowser |
|---------|------------------|------------------|
| **Execution** | Local Playwright | AWS AgentCore cloud service |
| **LLM Provider** | OpenRouter, OpenAI, Anthropic, Bedrock | AWS Bedrock only |
| **Profile Support** | Yes (via BrowserProfileManager) | No (sessions are ephemeral) |
| **Token Tracking** | Yes (detailed metrics) | No (Bedrock billing separate) |
| **Proxy Support** | Yes (all providers) | No (cloud-managed) |
| **Rate Limit Retry** | Yes (3 retries, exponential backoff) | No (manual handling required) |
| **Session Timeout** | Indefinite (local) | 15-480 minutes (configurable) |
| **Page Access** | `Page` (Stagehand V3 API) | `Page` (full Playwright API, internal) |
| **Model Selection** | Any supported model | Claude variants only |

**Sources:** [services/common/browser/src/implementations/stagehand-browser.ts:1-1117](), [services/common/browser/src/implementations/agent-core-browser.ts:1-849]()

---

## Testing Strategy

The browser layer includes both unit tests and E2E tests:

### Unit Tests

Focus on internal logic, parameter validation, and response parsing without requiring real browser/LLM:
- Configuration resolution
- Screenshot format conversion
- waitForSelector state mapping
- Scroll direction calculation
- XPath normalization
- Response parsing (parseObserveResponse)
- Error handling

**Sources:** [services/common/browser/test/unit/agent-core-browser.ut.test.ts:1-727]()

### E2E Tests

Test against real browsers and LLM services:
- Browser lifecycle (initialize, close)
- Navigation and page information
- Screenshot capture
- Element inspection
- AI operations (observe, act) - requires LLM credentials
- Popup handling

**Test Conditions:**
- Skip AgentCore tests if `BROWSER_TYPE !== 'agentcore'`
- Skip AI tests if no LLM credentials present
- Use `example.com` as test target (simple, stable)

**Sources:** [services/common/browser/test/e2e/stagehand-browser.e2e.test.ts:1-402]()

---

# Page: BrowserAdapter Interface

# BrowserAdapter Interface

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [services/action-builder/src/index.ts](services/action-builder/src/index.ts)
- [services/common/browser/package.json](services/common/browser/package.json)
- [services/common/browser/src/adapters/browser-adapter.ts](services/common/browser/src/adapters/browser-adapter.ts)
- [services/common/browser/src/adapters/index.ts](services/common/browser/src/adapters/index.ts)
- [services/common/browser/src/implementations/agent-core-browser.ts](services/common/browser/src/implementations/agent-core-browser.ts)
- [services/common/browser/src/implementations/stagehand-browser.ts](services/common/browser/src/implementations/stagehand-browser.ts)
- [services/common/browser/src/types/browser.ts](services/common/browser/src/types/browser.ts)
- [services/common/browser/test/e2e/stagehand-browser.e2e.test.ts](services/common/browser/test/e2e/stagehand-browser.e2e.test.ts)
- [services/common/browser/test/unit/agent-core-browser.ut.test.ts](services/common/browser/test/unit/agent-core-browser.ut.test.ts)

</details>



## Purpose and Scope

The `BrowserAdapter` interface defines a unified contract for browser automation operations across different browser implementations in Actionbook. It provides a consistent API for both basic browser control (navigation, screenshots, waiting) and AI-powered capabilities (element observation, intelligent action execution).

This interface serves as an abstraction layer that allows the action-builder and playbook-builder services to work with multiple browser implementations without coupling to specific technologies. For details on specific implementations, see [StagehandBrowser Implementation](#4.2) and [AgentCoreBrowser Implementation](#4.3). For browser profile management, see [Browser Profiles](#4.4).

**Sources:** [services/common/browser/src/adapters/browser-adapter.ts:1-254]()

---

## Interface Structure

The `BrowserAdapter` interface is organized into nine logical groups of operations:

```mermaid
graph TB
    subgraph "BrowserAdapter Interface"
        Lifecycle["Lifecycle<br/>initialize(), close()"]
        Navigation["Navigation<br/>navigate(), goBack()"]
        PageInfo["Page Information<br/>getUrl(), getTitle(), getContent()"]
        Screenshot["Screenshot<br/>screenshot()"]
        Waiting["Waiting<br/>waitForSelector(), wait(), waitForText()"]
        Scrolling["Scrolling<br/>scroll(), scrollToBottom()"]
        AI["AI Capabilities<br/>observe(), act(), actWithSelector()"]
        Inspection["Element Inspection<br/>getElementAttributesFromXPath(), getPage()"]
        Helpers["Automation Helpers<br/>autoClosePopups()"]
        Metrics["Metrics (optional)<br/>getTokenStats()"]
    end
    
    Lifecycle -.-> Navigation
    Navigation -.-> PageInfo
    PageInfo -.-> Screenshot
    Screenshot -.-> Waiting
    Waiting -.-> Scrolling
    Scrolling -.-> AI
    AI -.-> Inspection
    Inspection -.-> Helpers
    Helpers -.-> Metrics
```

**Sources:** [services/common/browser/src/adapters/browser-adapter.ts:38-254]()

---

## Lifecycle Methods

The lifecycle methods manage browser instance initialization and cleanup:

| Method | Signature | Purpose |
|--------|-----------|---------|
| `initialize()` | `Promise<void>` | Initialize the browser instance. Must be called before any other operations. |
| `close()` | `Promise<void>` | Close the browser and release resources. |

### Usage Pattern

```typescript
const browser: BrowserAdapter = new StagehandBrowser();
await browser.initialize();
// ... perform operations
await browser.close();
```

**Implementation Notes:**
- `initialize()` should be idempotent - calling it multiple times should not create additional browser instances
- `close()` should gracefully handle being called multiple times
- All other methods should throw an error if called before `initialize()`

**Sources:** [services/common/browser/src/adapters/browser-adapter.ts:43-52](), [services/common/browser/src/implementations/stagehand-browser.ts:133-174](), [services/common/browser/src/implementations/agent-core-browser.ts:93-140]()

---

## Navigation Methods

Navigation methods control browser page transitions:

| Method | Signature | Purpose |
|--------|-----------|---------|
| `navigate(url, options?)` | `Promise<void>` | Navigate to a URL with optional wait conditions and timeout |
| `goBack()` | `Promise<void>` | Navigate back in browser history |

### NavigateOptions Type

```typescript
interface NavigateOptions {
  timeout?: number;  // Timeout in milliseconds
  waitUntil?: 'load' | 'domcontentloaded' | 'networkidle';
}
```

### Behavior

The `navigate()` method accepts a `NavigateOptions` object to control navigation behavior:
- `timeout`: Maximum time to wait for navigation (default varies by implementation)
- `waitUntil`: When to consider navigation complete (default: `'domcontentloaded'`)

**Sources:** [services/common/browser/src/adapters/browser-adapter.ts:54-68](), [services/common/browser/src/types/browser.ts:59-66](), [services/common/browser/src/implementations/stagehand-browser.ts:180-204](), [services/common/browser/src/implementations/agent-core-browser.ts:146-169]()

---

## Page Information Methods

Page information methods retrieve metadata about the current page state:

| Method | Signature | Return Type | Purpose |
|--------|-----------|-------------|---------|
| `getUrl()` | synchronous | `string` | Get the current page URL |
| `getTitle()` | `Promise<string>` | `string` | Get the current page title |
| `getContent()` | `Promise<string>` | `string` | Get the page HTML content |

### Implementation Details

- `getUrl()` is synchronous and returns the URL immediately
- `getTitle()` retrieves the value of the `<title>` tag
- `getContent()` returns the entire HTML content of `document.documentElement.outerHTML`

**Sources:** [services/common/browser/src/adapters/browser-adapter.ts:70-87](), [services/common/browser/src/implementations/stagehand-browser.ts:210-220](), [services/common/browser/src/implementations/agent-core-browser.ts:175-199]()

---

## Screenshot Capabilities

The screenshot method captures visual representations of the current page:

```typescript
screenshot(options?: ScreenshotOptions): Promise<Buffer>
```

### ScreenshotOptions Type

```typescript
interface ScreenshotOptions {
  fullPage?: boolean;        // Capture full scrollable page (default: false)
  format?: 'png' | 'jpeg' | 'webp';  // Image format (default: 'png')
  quality?: number;          // JPEG/WebP quality 0-100
}
```

### Return Value

Returns a `Buffer` containing the image data in the specified format. The buffer can be:
- Written to disk
- Converted to base64 for API transmission
- Passed directly to AI vision models

### Format Support

| Format | Magic Bytes | Support |
|--------|-------------|---------|
| PNG | `89 50 4E 47` | All implementations |
| JPEG | `FF D8 FF` | All implementations |
| WebP | N/A | StagehandBrowser converts to PNG; AgentCoreBrowser converts to PNG |

**Sources:** [services/common/browser/src/adapters/browser-adapter.ts:89-98](), [services/common/browser/src/types/browser.ts:48-56](), [services/common/browser/src/implementations/stagehand-browser.ts:226-234](), [services/common/browser/src/implementations/agent-core-browser.ts:205-227]()

---

## Waiting Operations

Waiting operations synchronize automation with page state changes:

| Method | Signature | Purpose |
|--------|-----------|---------|
| `waitForSelector(selector, options?)` | `Promise<void>` | Wait for a CSS or XPath selector to appear |
| `wait(ms)` | `Promise<void>` | Wait for a specified duration |
| `waitForText(text, timeout?)` | `Promise<void>` | Wait for text to appear on the page |

### WaitForSelectorOptions Type

```typescript
interface WaitForSelectorOptions {
  timeout?: number;   // Timeout in milliseconds (default: 30000)
  visible?: boolean;  // Wait for element to be visible
  hidden?: boolean;   // Wait for element to be hidden
}
```

### State Mapping

The `visible` and `hidden` options control the element state to wait for:
- Neither set: Wait for element to be attached to DOM
- `visible: true`: Wait for element to be visible (has dimensions)
- `hidden: true`: Wait for element to be hidden or removed

**Sources:** [services/common/browser/src/adapters/browser-adapter.ts:100-122](), [services/common/browser/src/types/browser.ts:69-78](), [services/common/browser/src/implementations/stagehand-browser.ts:240-272](), [services/common/browser/src/implementations/agent-core-browser.ts:233-256]()

---

## Scrolling Operations

Scrolling operations control viewport position for lazy-loaded content and navigation:

| Method | Signature | Purpose |
|--------|-----------|---------|
| `scroll(direction, amount?)` | `Promise<void>` | Scroll up or down by specified pixels |
| `scrollToBottom(waitAfterMs?)` | `Promise<void>` | Scroll to bottom of page, useful for lazy loading |

### scroll() Parameters

```typescript
type ScrollDirection = 'up' | 'down';
```

- `direction`: Direction to scroll ('up' or 'down')
- `amount`: Number of pixels to scroll (default: 300)

### scrollToBottom() Behavior

The `scrollToBottom()` method performs iterative scrolling:
1. Scrolls to bottom of page
2. Waits for potential lazy-loaded content
3. Checks if scroll height increased
4. Repeats up to 10 times until no more content loads
5. Waits for `waitAfterMs` (default: 1000ms) after final scroll

**Sources:** [services/common/browser/src/adapters/browser-adapter.ts:124-140](), [services/common/browser/src/types/browser.ts:80-83](), [services/common/browser/src/implementations/stagehand-browser.ts:278-322](), [services/common/browser/src/implementations/agent-core-browser.ts:262-310]()

---

## AI Capabilities

### AI Capabilities Overview

The AI capabilities enable intelligent element discovery and action execution using Large Language Models:

```mermaid
graph LR
    subgraph "AI Methods"
        observe["observe(instruction, timeoutMs?)"]
        act["act(instructionOrAction)"]
        actWithSelector["actWithSelector(action)"]
    end
    
    subgraph "Input Types"
        NLInstruction["Natural Language<br/>String"]
        ActionObj["ActionObject<br/>{selector, method, description}"]
    end
    
    subgraph "Return Types"
        ObserveResults["ObserveResult[]<br/>{selector, description, method, arguments}"]
        ActResult["unknown"]
    end
    
    NLInstruction --> observe
    observe --> ObserveResults
    
    NLInstruction --> act
    ActionObj --> act
    ActionObj --> actWithSelector
    
    act --> ActResult
    actWithSelector --> ActResult
```

**Sources:** [services/common/browser/src/adapters/browser-adapter.ts:142-195]()

---

### observe() Method

```typescript
observe(instruction: string, timeoutMs?: number): Promise<ObserveResult[]>
```

The `observe()` method uses AI to analyze the page and find elements matching a natural language instruction.

**Parameters:**
- `instruction`: Natural language description of what to find (e.g., "find the search button", "locate the login form")
- `timeoutMs`: Timeout in milliseconds (default: 30000)

**Return Type:**

```typescript
interface ObserveResult {
  selector?: string;      // Element selector (usually XPath)
  description?: string;   // Human-readable description
  method?: string;        // Suggested interaction method
  arguments?: unknown[];  // Suggested arguments
}
```

**Implementation Approaches:**
- **StagehandBrowser**: Uses Stagehand SDK's built-in `observe()` with LLM-powered element detection
- **AgentCoreBrowser**: Takes screenshot + calls Bedrock Claude with vision capabilities

**Sources:** [services/common/browser/src/adapters/browser-adapter.ts:146-161](), [services/common/browser/src/types/browser.ts:94-107](), [services/common/browser/src/implementations/stagehand-browser.ts:334-396](), [services/common/browser/src/implementations/agent-core-browser.ts:396-475]()

---

### act() Method

```typescript
act(instructionOrAction: string | ActionObject): Promise<unknown>
```

The `act()` method executes an action using either AI inference or a predefined selector.

**Input Modes:**

1. **Natural Language Mode** (AI inference):
```typescript
await browser.act('click the submit button');
```

2. **Selector Mode** (direct, faster):
```typescript
await browser.act({
  selector: '#submit-btn',
  method: 'click',
  description: 'Submit button'
});
```

**ActionObject Type:**

```typescript
interface ActionObject {
  selector: string;        // CSS or XPath selector
  description: string;     // Human-readable description
  method: ActionMethod;    // Interaction method
  arguments?: string[];    // Method arguments (e.g., text to type)
}

type ActionMethod = 
  | 'click' 
  | 'type' 
  | 'fill' 
  | 'select' 
  | 'hover' 
  | 'press' 
  | 'scroll' 
  | 'wait';
```

**Execution Flow:**
- String instruction → Calls `observe()` to find element → Executes action on first match
- ActionObject → Direct execution using selector (no AI inference)

**Sources:** [services/common/browser/src/adapters/browser-adapter.ts:163-184](), [services/common/browser/src/types/browser.ts:110-136](), [services/common/browser/src/implementations/stagehand-browser.ts:407-494](), [services/common/browser/src/implementations/agent-core-browser.ts:482-508]()

---

### actWithSelector() Method

```typescript
actWithSelector(action: ActionObject): Promise<unknown>
```

Convenience method for selector-based actions with clearer semantics than `act()` with `ActionObject`.

**Purpose:** Explicitly indicates direct selector-based execution without AI inference.

**Action Method Dispatch:**

| Method | Required Args | Behavior |
|--------|---------------|----------|
| `click` | None | Clicks the element |
| `type` | text (string) | Types text character by character |
| `fill` | text (string) | Fills input field (faster than type) |
| `select` | value (string) | Selects option in dropdown |
| `hover` | None | Triggers mouseover event |
| `press` | key (string) | Presses keyboard key |
| `scroll` | None | Scrolls by default amount |
| `wait` | ms (string, optional) | Waits specified milliseconds (default: 1000) |

**Sources:** [services/common/browser/src/adapters/browser-adapter.ts:186-195](), [services/common/browser/src/implementations/stagehand-browser.ts:496-502](), [services/common/browser/src/implementations/agent-core-browser.ts:510-584]()

---

## Element Inspection

Element inspection methods extract metadata for selector generation and validation:

### getElementAttributesFromXPath()

```typescript
getElementAttributesFromXPath(xpath: string): Promise<ElementAttributes | null>
```

Extracts comprehensive element metadata from an XPath selector.

**Return Type:**

```typescript
interface ElementAttributes {
  tagName: string;                    // HTML tag name (lowercase)
  id?: string;                        // Element id attribute
  className?: string;                 // Element class attribute
  dataTestId?: string;                // data-testid attribute
  ariaLabel?: string;                 // aria-label attribute
  placeholder?: string;               // placeholder attribute (inputs)
  name?: string;                      // name attribute (form elements)
  textContent?: string;               // Text content (truncated to 50-100 chars)
  cssSelector?: string;               // Generated CSS selector
  optimizedXPath?: string;            // Optimized XPath selector
  dataAttributes?: Record<string, string>; // All data-* attributes
}
```

**XPath Normalization:**
- Removes `xpath=` prefix if present
- Handles iframe elements by iterating through frames
- Filters state-related data attributes (e.g., `data-selected`, `data-active`)

**CSS Selector Generation Priority:**
1. `data-testid` attribute → `[data-testid="value"]`
2. Preferred data attributes (data-id, data-component, etc.)
3. ID attribute → `#id`
4. `aria-label` attribute → `[aria-label="value"]`
5. Fallback to tag + classes

**Sources:** [services/common/browser/src/adapters/browser-adapter.ts:197-210](), [services/common/browser/src/types/browser.ts:140-167](), [services/common/browser/src/implementations/stagehand-browser.ts:508-580](), [services/common/browser/src/implementations/agent-core-browser.ts:589-630]()

---

### getPage()

```typescript
getPage(): Promise<unknown>
```

Returns the underlying browser-specific Page instance for advanced operations.

**Return Types by Implementation:**
- **StagehandBrowser**: Returns Stagehand `Page` (limited Playwright-like API)
- **AgentCoreBrowser**: Returns Playwright `Page` (full API access)

**Usage Warning:** Prefer high-level `BrowserAdapter` methods when possible. Direct page access couples code to specific implementations.

**Sources:** [services/common/browser/src/adapters/browser-adapter.ts:212-223](), [services/common/browser/src/implementations/stagehand-browser.ts:585-587](), [services/common/browser/src/implementations/agent-core-browser.ts:636-645]()

---

## Automation Helpers

### autoClosePopups()

```typescript
autoClosePopups(): Promise<number>
```

Auto-detects and closes common popup patterns using AI:
- Cookie consent banners
- Newsletter signup modals
- Notification permission dialogs

**Process:**
1. Iterates through predefined popup instructions
2. Uses `observe()` to find popup elements
3. Executes close action if found
4. Returns count of popups closed

**Popup Instructions Used:**
```typescript
const popupInstructions = [
  'click the close button on any popup or modal',
  'click accept or dismiss on cookie consent banner',
  'click close on any overlay dialog',
];
```

**Return Value:** Number of popups successfully closed.

**Sources:** [services/common/browser/src/adapters/browser-adapter.ts:225-239](), [services/common/browser/src/implementations/stagehand-browser.ts:675-706](), [services/common/browser/src/implementations/agent-core-browser.ts:675-710]()

---

## Metrics

### getTokenStats()

```typescript
getTokenStats?(): TokenStats | undefined
```

Optional method that returns accumulated token usage statistics for AI operations.

**TokenStats Type:**

```typescript
interface TokenStats {
  input: number;   // Input tokens consumed
  output: number;  // Output tokens generated
  total: number;   // Total tokens (input + output)
}
```

**Implementation Status:**
- **StagehandBrowser**: Tracks tokens from `observe()` and `act()` calls using Stagehand's metrics API
- **AgentCoreBrowser**: Returns `undefined` (Bedrock billing is separate and tracked via AWS)

**Token Tracking (StagehandBrowser):**
- Captures deltas from Stagehand's internal metrics after each AI operation
- Accumulates input/output tokens across browser session
- Logs per-operation metrics with format: `[LLM] ✓ | stagehand/observe | tokens: in=X, out=Y, total=Z | perf: latency=Nms, inference=Nms, tps=N`

**Sources:** [services/common/browser/src/adapters/browser-adapter.ts:241-253](), [services/common/browser/src/types/browser.ts:173-183](), [services/common/browser/src/implementations/stagehand-browser.ts:712-718](), [services/common/browser/src/implementations/agent-core-browser.ts:716-718]()

---

## Implementations Overview

The `BrowserAdapter` interface has two production implementations:

```mermaid
graph TB
    subgraph "BrowserAdapter Interface"
        Interface["«interface» BrowserAdapter<br/>services/common/browser/src/adapters/browser-adapter.ts"]
    end
    
    subgraph "Local Implementation"
        StagehandBrowser["StagehandBrowser<br/>services/common/browser/src/implementations/stagehand-browser.ts"]
        Playwright["Playwright Browser<br/>Local Chrome/Chromium"]
        StagehandSDK["@browserbasehq/stagehand<br/>AI-powered observation"]
        BrowserProfile["BrowserProfileManager<br/>@actionbookdev/browser-profile"]
        
        StagehandBrowser --> Playwright
        StagehandBrowser --> StagehandSDK
        StagehandBrowser --> BrowserProfile
    end
    
    subgraph "Cloud Implementation"
        AgentCoreBrowser["AgentCoreBrowser<br/>services/common/browser/src/implementations/agent-core-browser.ts"]
        PlaywrightBrowserSDK["PlaywrightBrowser<br/>bedrock-agentcore/browser/playwright"]
        BedrockClient["BedrockRuntimeClient<br/>@aws-sdk/client-bedrock-runtime"]
        
        AgentCoreBrowser --> PlaywrightBrowserSDK
        AgentCoreBrowser --> BedrockClient
    end
    
    subgraph "LLM Providers"
        OpenRouter["OpenRouter"]
        OpenAI["OpenAI"]
        Anthropic["Anthropic"]
        Bedrock["AWS Bedrock"]
    end
    
    Interface -.implements.-> StagehandBrowser
    Interface -.implements.-> AgentCoreBrowser
    
    StagehandSDK -.uses.-> OpenRouter
    StagehandSDK -.uses.-> OpenAI
    StagehandSDK -.uses.-> Anthropic
    StagehandSDK -.uses.-> Bedrock
    
    BedrockClient -.uses.-> Bedrock
```

### Implementation Comparison

| Feature | StagehandBrowser | AgentCoreBrowser |
|---------|------------------|------------------|
| **Execution** | Local Playwright | AWS cloud service |
| **Installation** | Requires Playwright + Chromium | No local browser needed |
| **LLM Providers** | OpenRouter, OpenAI, Anthropic, Bedrock | Bedrock only |
| **Profile Support** | Yes (persistent login state) | No |
| **Token Tracking** | Yes (via Stagehand metrics) | No (Bedrock billing separate) |
| **Proxy Support** | Yes (HTTP/HTTPS proxies) | Via AWS networking |
| **observe() Implementation** | Stagehand SDK native | Screenshot + Bedrock Claude vision |
| **act() Implementation** | Stagehand SDK native | observe() + method dispatch |
| **Session Management** | Local process | AWS session (configurable timeout) |
| **Best For** | Development, custom LLM configs | Production, scalability, no local resources |

**Sources:** [services/common/browser/src/implementations/stagehand-browser.ts:1-1127](), [services/common/browser/src/implementations/agent-core-browser.ts:1-849](), [services/common/browser/package.json:1-75]()

---

## Usage in Action Builder

The action-builder service uses `BrowserAdapter` through the `RecorderToolExecutor` class:

```mermaid
graph LR
    subgraph "Action Recording Flow"
        RecorderToolExecutor["RecorderToolExecutor"]
        Browser["BrowserAdapter<br/>(StagehandBrowser or AgentCoreBrowser)"]
        
        navigate["navigate tool"]
        observe["observe_page tool"]
        interact["interact tool"]
        register["register_element tool"]
    end
    
    RecorderToolExecutor --> navigate
    RecorderToolExecutor --> observe
    RecorderToolExecutor --> interact
    RecorderToolExecutor --> register
    
    navigate --> Browser
    observe --> Browser
    interact --> Browser
    register --> Browser
```

**Key Operations:**
- `navigate` tool → `browser.navigate(url)`
- `observe_page` tool → `browser.observe(instruction)` + element attribute extraction
- `interact` tool → `browser.act(action)` or `browser.actWithSelector(action)`
- All tools use `browser.screenshot()` for debugging and logging

**Sources:** [services/action-builder/src/index.ts:1-50]()

---

## Error Handling

### Common Error Types

**StagehandBrowser-specific:**
```typescript
class ElementNotFoundError extends Error {
  constructor(message: string, selector?: string)
}

class ActionExecutionError extends Error {
  constructor(message: string, action?: string, originalError?: Error)
}
```

**Error Scenarios:**

| Scenario | Error Type | When Thrown |
|----------|------------|-------------|
| Element not found | `ElementNotFoundError` | `observe()` returns no results, `act()` selector not found |
| Action timeout | `ActionExecutionError` | Action exceeds timeout duration |
| Navigation timeout | Native Error | `navigate()` exceeds timeout |
| Rate limit hit | Native Error | LLM provider rate limit (with auto-retry) |
| Not initialized | Native Error | Methods called before `initialize()` |

**Rate Limit Retry:**
Both implementations implement exponential backoff retry for rate limit errors:
- Max retries: 3
- Delay: `min(1000 * 2^attempt, 30000)` milliseconds
- Applies to: `observe()` and `act()` methods

**Sources:** [services/common/browser/src/implementations/stagehand-browser.ts:69-91](), [services/common/browser/src/implementations/stagehand-browser.ts:334-396](), [services/common/browser/src/implementations/stagehand-browser.ts:407-494]()

---

# Page: StagehandBrowser Implementation

# StagehandBrowser Implementation

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [services/action-builder/src/index.ts](services/action-builder/src/index.ts)
- [services/common/browser/package.json](services/common/browser/package.json)
- [services/common/browser/src/adapters/browser-adapter.ts](services/common/browser/src/adapters/browser-adapter.ts)
- [services/common/browser/src/adapters/index.ts](services/common/browser/src/adapters/index.ts)
- [services/common/browser/src/implementations/agent-core-browser.ts](services/common/browser/src/implementations/agent-core-browser.ts)
- [services/common/browser/src/implementations/stagehand-browser.ts](services/common/browser/src/implementations/stagehand-browser.ts)
- [services/common/browser/src/types/browser.ts](services/common/browser/src/types/browser.ts)
- [services/common/browser/test/e2e/stagehand-browser.e2e.test.ts](services/common/browser/test/e2e/stagehand-browser.e2e.test.ts)
- [services/common/browser/test/unit/agent-core-browser.ut.test.ts](services/common/browser/test/unit/agent-core-browser.ut.test.ts)

</details>



## Purpose and Scope

`StagehandBrowser` is the local Playwright-based implementation of the `BrowserAdapter` interface ([services/common/browser/src/adapters/browser-adapter.ts:1-254]()). It combines Playwright browser automation with Stagehand AI capabilities for intelligent element observation and action execution. This implementation runs browsers locally and supports multiple LLM providers for AI operations.

For the unified browser interface specification, see [BrowserAdapter Interface](#4.1). For the cloud-based AWS implementation, see [AgentCoreBrowser Implementation](#4.3). For persistent login state management, see [Browser Profiles](#4.4).

**Sources:** [services/common/browser/src/implementations/stagehand-browser.ts:1-10]()

---

## Architecture Overview

`StagehandBrowser` implements `BrowserAdapter` by wrapping the Stagehand SDK, which itself wraps Playwright. The class maintains state for the Stagehand instance, Playwright page, configuration, and accumulated token metrics.

### Class Structure

```mermaid
classDiagram
    class BrowserAdapter {
        <<interface>>
        +initialize() Promise~void~
        +close() Promise~void~
        +navigate(url, options) Promise~void~
        +observe(instruction, timeout) Promise~ObserveResult[]~
        +act(instructionOrAction) Promise~unknown~
        +getTokenStats() TokenStats
    }
    
    class StagehandBrowser {
        -stagehand: StagehandInstance | null
        -page: Page | null
        -config: BrowserConfig
        -lastMetrics: StagehandMetricsSnapshot | null
        -accumulatedInputTokens: number
        -accumulatedOutputTokens: number
        +initialize() Promise~void~
        +close() Promise~void~
        +observe(instruction, timeoutMs) Promise~ObserveResult[]~
        +act(instructionOrAction) Promise~unknown~
        +getElementAttributesFromXPath(xpath) Promise~ElementAttributes~
        +getTokenStats() TokenStats
        -buildLLMConfig() Promise~config~
        -buildBrowserLaunchOptions() LocalBrowserLaunchOptions
        -logStagehandMetrics(operation, startTime) Promise~void~
        -isRateLimitError(error) boolean
    }
    
    class Stagehand {
        <<external>>
        +init() Promise~void~
        +observe(instruction) Promise~ObserveResult[]~
        +act(action) Promise~unknown~
        +context: V3Context
        +metrics: MetricsSnapshot
        +close() Promise~void~
    }
    
    class AISdkClient {
        <<external>>
        +model: LanguageModel
    }
    
    class BrowserProfileManager {
        <<external>>
        +getProfilePath() string
        +ensureDir() void
        +cleanupStaleLocks() void
    }
    
    BrowserAdapter <|.. StagehandBrowser
    StagehandBrowser --> Stagehand : wraps
    StagehandBrowser --> AISdkClient : optional
    StagehandBrowser --> BrowserProfileManager : uses
```

**Sources:** [services/common/browser/src/implementations/stagehand-browser.ts:112-127](), [services/common/browser/src/adapters/browser-adapter.ts:38-254]()

### Key Dependencies

| Dependency | Purpose | Configuration |
|------------|---------|---------------|
| `@browserbasehq/stagehand` | AI-powered browser automation | Peer dependency, optional |
| `playwright` | Browser engine | Peer dependency |
| `@ai-sdk/amazon-bedrock` | AWS Bedrock LLM integration | Dev dependency, loaded dynamically |
| `undici` | Proxy support for HTTP requests | Direct dependency |
| `@actionbookdev/browser-profile` | Persistent browser profiles | Workspace dependency |

**Sources:** [services/common/browser/package.json:38-62]()

---

## LLM Provider Configuration

`StagehandBrowser` supports four LLM providers through environment variables. The `buildLLMConfig()` method selects the provider based on available credentials and constructs appropriate configuration for Stagehand.

### Provider Selection Flow

```mermaid
flowchart TD
    Start["buildLLMConfig()"] --> CheckOR{OPENROUTER_API_KEY?}
    CheckOR -->|Yes| UseOR["Return ModelConfiguration<br/>baseURL: openrouter.ai/api/v1"]
    CheckOR -->|No| CheckOAI{OPENAI_API_KEY?}
    
    CheckOAI -->|Yes| CheckProxy{Has proxy?}
    CheckProxy -->|Yes| UseOAIProxy["Return ModelConfiguration<br/>with custom baseURL"]
    CheckProxy -->|No| UseOAI["Return model string<br/>(Stagehand default config)"]
    
    CheckOAI -->|No| CheckBedrock{AWS credentials?}
    CheckBedrock -->|Yes| CreateBedrock["createAmazonBedrock()<br/>with region, credentials"]
    CreateBedrock --> CreateClient["Return AISdkClient<br/>with Bedrock model"]
    
    CheckBedrock -->|No| CheckAnthropic{ANTHROPIC_API_KEY?}
    CheckAnthropic -->|Yes| CheckAnthropicProxy{Has proxy?}
    CheckAnthropicProxy -->|Yes| ThrowProxy["Throw: Anthropic SDK<br/>does not support proxy"]
    CheckAnthropicProxy -->|No| UseAnthropic["Return model string<br/>(Stagehand default)"]
    
    CheckAnthropic -->|No| ThrowNoKey["Throw: No LLM API key"]
```

**Sources:** [services/common/browser/src/implementations/stagehand-browser.ts:743-822]()

### Provider Configuration Details

| Provider | Environment Variables | Model Default | Proxy Support |
|----------|----------------------|---------------|---------------|
| OpenRouter | `OPENROUTER_API_KEY` | `gpt-4o` | Yes |
| OpenAI | `OPENAI_API_KEY`, `OPENAI_BASE_URL` | `gpt-4o` | Yes (via baseURL) |
| AWS Bedrock | `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_SESSION_TOKEN`, `AWS_REGION` | `anthropic.claude-3-5-sonnet-20241022-v2:0` | Yes (via undici ProxyAgent) |
| Anthropic | `ANTHROPIC_API_KEY` | `claude-sonnet-4-20250514` | No (throws error) |

Model selection can be overridden with `STAGEHAND_MODEL` environment variable.

**Sources:** [services/common/browser/src/implementations/stagehand-browser.ts:747-821]()

### Bedrock Proxy Configuration

For AWS Bedrock, proxy support is implemented using undici's `ProxyAgent`:

```mermaid
sequenceDiagram
    participant SB as StagehandBrowser
    participant CPF as createProxyFetchForBedrock()
    participant PA as ProxyAgent
    participant Bedrock as AWS Bedrock
    
    SB->>CPF: Check HTTPS_PROXY env
    CPF->>PA: Create ProxyAgent(proxyUrl)
    CPF->>SB: Return custom fetch function
    SB->>Bedrock: createAmazonBedrock({ fetch: proxyFetch })
    Note over Bedrock: All requests use proxy
```

**Sources:** [services/common/browser/src/implementations/stagehand-browser.ts:878-894](), [services/common/browser/src/implementations/stagehand-browser.ts:780-807]()

---

## Initialization and Lifecycle

### Initialization Process

The `initialize()` method sets up the Stagehand instance, configures the browser, and prepares metrics tracking:

```mermaid
sequenceDiagram
    participant Client
    participant SB as StagehandBrowser
    participant LLM as buildLLMConfig()
    participant BLO as buildBrowserLaunchOptions()
    participant SH as Stagehand
    participant SS as injectStorageState()
    participant M as initializeMetricsBaseline()
    
    Client->>SB: initialize()
    
    alt Already initialized
        SB-->>Client: Return early
    end
    
    SB->>LLM: Build LLM config
    LLM-->>SB: modelConfig or llmClient
    
    SB->>BLO: Build browser options
    BLO-->>SB: LocalBrowserLaunchOptions
    
    SB->>SH: new Stagehand(options)
    SB->>SH: stagehand.init()
    SH-->>SB: Context with Page
    
    SB->>SB: Extract page from context
    SB->>SS: Inject cookies/localStorage
    SB->>M: Initialize metrics baseline
    
    SB-->>Client: Complete
```

**Sources:** [services/common/browser/src/implementations/stagehand-browser.ts:133-165]()

### Browser Launch Options

The `buildBrowserLaunchOptions()` method configures Playwright launch settings:

| Option | Configuration | Source |
|--------|--------------|---------|
| `headless` | `config.headless` or `HEADLESS=true` env | [services/common/browser/src/implementations/stagehand-browser.ts:122-123]() |
| `proxy` | `config.proxy` or `HTTPS_PROXY`/`HTTP_PROXY` env | [services/common/browser/src/implementations/stagehand-browser.ts:123]() |
| `userDataDir` | Profile path from `BrowserProfileManager` | [services/common/browser/src/implementations/stagehand-browser.ts:835-842]() |
| `preserveUserDataDir` | `true` when using profiles | [services/common/browser/src/implementations/stagehand-browser.ts:843]() |
| `args` | Anti-detection args when using profiles | [services/common/browser/src/implementations/stagehand-browser.ts:844-847]() |

**Sources:** [services/common/browser/src/implementations/stagehand-browser.ts:824-854]()

### Storage State Injection

When `config.storageStatePath` is provided, `injectStorageState()` restores cookies and localStorage:

```mermaid
flowchart LR
    Load["Load storage state JSON"] --> Cookies{Has cookies?}
    Cookies -->|Yes| AddCookies["context.addCookies()"]
    Cookies -->|No| Origins{Has localStorage?}
    
    AddCookies --> Origins
    Origins -->|Yes| AddScript["context.addInitScript()<br/>Restore localStorage by origin"]
    Origins -->|No| Done["Complete"]
    AddScript --> Done
```

**Sources:** [services/common/browser/src/implementations/stagehand-browser.ts:896-937]()

### Cleanup

The `close()` method releases resources:

**Sources:** [services/common/browser/src/implementations/stagehand-browser.ts:167-174]()

---

## AI Capabilities

### observe() - Element Discovery

The `observe()` method uses Stagehand's AI to find elements matching a natural language instruction. It includes rate limit retry logic with exponential backoff.

```mermaid
sequenceDiagram
    participant Caller
    participant SB as StagehandBrowser
    participant RateLimit as isRateLimitError()
    participant SH as Stagehand
    participant Metrics as logStagehandMetrics()
    
    Caller->>SB: observe(instruction, timeoutMs)
    
    loop Retry up to 3 times
        SB->>SH: stagehand.observe(instruction)
        
        alt Success
            SH-->>SB: ObserveResult[]
            SB->>Metrics: Log tokens and performance
            SB-->>Caller: Return results
        else Rate Limit Error
            SH-->>SB: Error with "rate limit" or "429"
            SB->>RateLimit: Check error type
            RateLimit-->>SB: true
            SB->>SB: wait(exponential backoff)
            Note over SB: Retry with delay: 1s, 2s, 4s
        else Other Error
            SH-->>SB: Error
            SB-->>Caller: Throw error
        end
    end
    
    SB-->>Caller: Throw last error (max retries)
```

**Sources:** [services/common/browser/src/implementations/stagehand-browser.ts:334-396](), [services/common/browser/src/implementations/stagehand-browser.ts:734-741]()

### act() - Action Execution

The `act()` method supports both natural language instructions and explicit `ActionObject` selectors. It includes the same retry logic as `observe()`.

```mermaid
flowchart TD
    Start["act(instructionOrAction)"] --> CheckType{Type of input?}
    
    CheckType -->|string| NLMode["Natural language mode<br/>stagehand.act(instruction)"]
    CheckType -->|ActionObject| SelectorMode["Selector mode<br/>Convert to Stagehand Action format"]
    
    NLMode --> Execute[Execute with Stagehand]
    SelectorMode --> Execute
    
    Execute --> Success{Success?}
    Success -->|Yes| LogMetrics["logStagehandMetrics('act', startTime)"]
    LogMetrics --> Return[Return result]
    
    Success -->|No| CheckError{Error type?}
    CheckError -->|Rate Limit| Retry["Exponential backoff retry<br/>(max 3 attempts)"]
    CheckError -->|Element Not Found| ThrowENF["Throw ElementNotFoundError"]
    CheckError -->|Timeout| ThrowTimeout["Throw ActionExecutionError"]
    CheckError -->|Other| ThrowGeneric["Throw ActionExecutionError"]
    
    Retry --> Execute
```

**Sources:** [services/common/browser/src/implementations/stagehand-browser.ts:407-494]()

### Custom Error Types

| Error Class | Thrown When | Selector Captured |
|-------------|-------------|-------------------|
| `ElementNotFoundError` | "No object generated", "response did not match schema", "Could not find element" | Yes (if ActionObject) |
| `ActionExecutionError` | Timeout or other execution failures | No |

**Sources:** [services/common/browser/src/implementations/stagehand-browser.ts:69-91]()

### Token Tracking

`StagehandBrowser` accumulates token usage from both `observe()` and `act()` operations:

```mermaid
graph LR
    OM[observe() or act()] --> GetMetrics["stagehand.metrics<br/>Current snapshot"]
    GetMetrics --> CalcDelta["Calculate delta from<br/>lastMetrics snapshot"]
    CalcDelta --> AccumTokens["accumulatedInputTokens += delta.inputTokens<br/>accumulatedOutputTokens += delta.outputTokens"]
    AccumTokens --> UpdateLast["lastMetrics = current snapshot"]
    UpdateLast --> LogPerf["Log tokens, latency, TPS"]
```

**Sources:** [services/common/browser/src/implementations/stagehand-browser.ts:972-1052]()

The metrics snapshot structure:

```typescript
interface StagehandMetricsSnapshot {
  observePromptTokens: number;
  observeCompletionTokens: number;
  observeReasoningTokens: number;
  observeCachedInputTokens: number;
  observeInferenceTimeMs: number;
  actPromptTokens: number;
  actCompletionTokens: number;
  actReasoningTokens: number;
  actCachedInputTokens: number;
  actInferenceTimeMs: number;
}
```

**Sources:** [services/common/browser/src/implementations/stagehand-browser.ts:96-107]()

---

## Element Inspection

### getElementAttributesFromXPath()

This method extracts comprehensive element metadata for selector generation. It handles both regular elements and elements within iframes.

```mermaid
flowchart TD
    Start["getElementAttributesFromXPath(xpathSelector)"] --> CheckIframe{XPath contains<br/>iframe reference?}
    
    CheckIframe -->|Yes| ParseIframe["Parse iframe path and element path<br/>e.g., //iframe[1]/html[1]/body[1]//div"]
    CheckIframe -->|No| DirectEval["page.evaluate(extractElementAttributes)"]
    
    ParseIframe --> IterateFrames["Iterate through page.frames()"]
    IterateFrames --> TryFrame["Try frame[i].evaluate(extractElementAttributes)"]
    TryFrame --> Found{Found?}
    Found -->|Yes| ProcessAttrs["Process attributes"]
    Found -->|No| NextFrame["Try next frame"]
    NextFrame --> IterateFrames
    
    DirectEval --> CheckNull{attrs === null?}
    CheckNull -->|Yes| ReturnNull["return null"]
    CheckNull -->|No| ProcessAttrs
    
    ProcessAttrs --> FilterState["filterStateDataAttributes()"]
    FilterState --> BuildCSS["buildCssSelector()"]
    BuildCSS --> GenXPath["generateOptimizedXPath()"]
    GenXPath --> ReturnAttrs["Return ElementAttributes"]
```

**Sources:** [services/common/browser/src/implementations/stagehand-browser.ts:508-580]()

### Iframe Handling

The implementation detects iframe references using regex pattern and accesses the iframe content via Playwright's `frames()` API:

**Pattern:** `/^(.+?\/iframe\[\d+\])\/html\[\d+\]\/body\[\d+\](.*)$/i`

**Sources:** [services/common/browser/src/implementations/stagehand-browser.ts:513-545]()

### Selector Generation

The `buildCssSelector()` method prioritizes stable attributes:

1. `data-testid` → `[data-testid="value"]`
2. Preferred data attributes (`data-id`, `data-component`, etc.) → `[data-id="value"]`
3. `id` attribute → `#id` (filtered for dynamic patterns)
4. `aria-label` → `[aria-label="value"]`
5. `name` attribute → `[name="value"]`
6. Tag + class combination (filtered for utility classes)

**Sources:** [services/common/browser/src/implementations/stagehand-browser.ts:1088-1125]()

### Attribute Extraction Script

The `extractElementAttributes` function runs in the browser context to collect element metadata:

**Sources:** [services/common/browser/src/implementations/stagehand-browser.ts:1054-1086]()

---

## Navigation and Page Control

### navigate()

Navigation includes timeout handling with partial success detection:

```mermaid
sequenceDiagram
    participant Client
    participant SB as StagehandBrowser
    participant Page
    
    Client->>SB: navigate(url, options)
    SB->>Page: page.goto(url, { waitUntil, timeoutMs })
    
    alt Success
        Page-->>SB: Navigation complete
        SB->>SB: wait(3000)
        SB-->>Client: Complete
    else Timeout
        Page-->>SB: Timeout error
        SB->>SB: Check if hostname matches
        alt Hostname matches
            SB-->>Client: Log partial success, continue
        else Different page
            SB-->>Client: Throw error
        end
    end
```

**Sources:** [services/common/browser/src/implementations/stagehand-browser.ts:180-197]()

### Scrolling Operations

| Method | Implementation | Use Case |
|--------|---------------|----------|
| `scroll(direction, amount)` | `page.scroll(0, 0, 0, deltaY)` | Incremental scrolling |
| `scrollToBottom(waitAfterMs)` | Loop until `scrollHeight` stabilizes, max 10 attempts | Loading lazy content |

**Sources:** [services/common/browser/src/implementations/stagehand-browser.ts:278-322]()

---

## Automation Helpers

### autoClosePopups()

Automatically detects and closes common popup patterns using AI observation:

```mermaid
flowchart LR
    Start[autoClosePopups] --> Instr1["Observe: 'click close on popup'"]
    Instr1 --> Found1{Found?}
    Found1 -->|Yes| Act1["act(element)<br/>closedCount++"]
    Found1 -->|No| Instr2["Observe: 'accept/dismiss cookie banner'"]
    
    Act1 --> Instr2
    Instr2 --> Found2{Found?}
    Found2 -->|Yes| Act2["act(element)<br/>closedCount++"]
    Found2 -->|No| Instr3["Observe: 'close overlay dialog'"]
    
    Act2 --> Instr3
    Instr3 --> Found3{Found?}
    Found3 -->|Yes| Act3["act(element)<br/>closedCount++"]
    Found3 -->|No| Return[Return closedCount]
    
    Act3 --> Return
```

**Sources:** [services/common/browser/src/implementations/stagehand-browser.ts:675-706]()

---

## Metrics and Performance Logging

### Token Statistics

The `getTokenStats()` method returns accumulated usage:

```typescript
getTokenStats(): TokenStats {
  return {
    input: this.accumulatedInputTokens,
    output: this.accumulatedOutputTokens,
    total: this.accumulatedInputTokens + this.accumulatedOutputTokens,
  };
}
```

**Sources:** [services/common/browser/src/implementations/stagehand-browser.ts:712-718]()

### Performance Logging

The `logStagehandMetrics()` method logs detailed performance data after each AI operation:

**Log Format:**
```
[LLM] ✓ | stagehand/observe | tokens: in=1234, out=567, cache_read=890, total=1801 | perf: latency=2345ms, inference=1890ms, tps=30.0
```

**Components:**
- **Tokens:** Input, output, cached (prompt caching), reasoning tokens
- **Performance:** End-to-end latency, LLM inference time, tokens per second

**Sources:** [services/common/browser/src/implementations/stagehand-browser.ts:1028-1048]()

---

## Error Handling and Retry Logic

### Rate Limit Detection

The `isRateLimitError()` method identifies rate limit errors across providers:

**Detection Patterns:**
- Error message contains "too many tokens"
- Error message contains "rate limit"
- Error message contains "429"

**Sources:** [services/common/browser/src/implementations/stagehand-browser.ts:734-741]()

### Exponential Backoff

Both `observe()` and `act()` implement retry with exponential backoff:

| Attempt | Delay | Max Delay |
|---------|-------|-----------|
| 1 (initial) | 0ms | - |
| 2 | 1000ms (2^0 * 1000) | 30000ms |
| 3 | 2000ms (2^1 * 1000) | 30000ms |
| 4 | 4000ms (2^2 * 1000) | 30000ms |

**Formula:** `Math.min(1000 * Math.pow(2, attempt), 30000)`

**Sources:** [services/common/browser/src/implementations/stagehand-browser.ts:374-376](), [services/common/browser/src/implementations/stagehand-browser.ts:446-448]()

### Error Context

`ActionExecutionError` captures the action method and original error for debugging:

**Sources:** [services/common/browser/src/implementations/stagehand-browser.ts:82-91](), [services/common/browser/src/implementations/stagehand-browser.ts:480-487]()

---

## Usage Examples

### Basic Initialization

```typescript
import { StagehandBrowser } from '@actionbookdev/browser/stagehand';

const browser = new StagehandBrowser({
  headless: true,
  proxy: 'http://proxy:8080',  // Optional
  timeout: 60000,
});

await browser.initialize();
```

### Element Discovery and Action

```typescript
// Natural language observation
const elements = await browser.observe('find the search button');
console.log(elements[0].selector); // xpath=//button[@id='search']

// Direct action with selector
await browser.act({
  selector: '#search-input',
  method: 'type',
  description: 'Search input field',
  arguments: ['actionbook'],
});

// Natural language action
await browser.act('click the search button');
```

### Token Tracking

```typescript
await browser.observe('find navigation links');
await browser.act('click the first link');

const stats = browser.getTokenStats();
console.log(`Total tokens: ${stats.total}`);
// Total tokens: 4567 (input: 3210, output: 1357)
```

**Sources:** [services/common/browser/test/e2e/stagehand-browser.e2e.test.ts:36-40](), [services/common/browser/test/e2e/stagehand-browser.e2e.test.ts:269-318]()

---

## Configuration Reference

### BrowserConfig

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `headless` | `boolean` | `process.env.HEADLESS === 'true'` | Headless browser mode |
| `proxy` | `string` | `process.env.HTTPS_PROXY \|\| process.env.HTTP_PROXY` | Proxy server URL |
| `timeout` | `number` | `60000` | Default navigation timeout (ms) |
| `storageStatePath` | `string` | `undefined` | Path to cookies/localStorage JSON |
| `profile.enabled` | `boolean` | `false` | Enable persistent profile |
| `profile.profileDir` | `string` | `'.browser-profile'` | Profile directory path |

**Sources:** [services/common/browser/src/types/browser.ts:12-28](), [services/common/browser/src/implementations/stagehand-browser.ts:120-127]()

### Environment Variables

| Variable | Purpose | Used By |
|----------|---------|---------|
| `OPENROUTER_API_KEY` | OpenRouter API key | LLM provider selection |
| `OPENAI_API_KEY` | OpenAI API key | LLM provider selection |
| `OPENAI_BASE_URL` | Custom OpenAI endpoint | OpenAI with proxy |
| `ANTHROPIC_API_KEY` | Anthropic API key | LLM provider selection |
| `AWS_ACCESS_KEY_ID` | AWS credentials | Bedrock provider |
| `AWS_SECRET_ACCESS_KEY` | AWS credentials | Bedrock provider |
| `AWS_SESSION_TOKEN` | AWS session token | Bedrock provider (optional) |
| `AWS_REGION` | AWS region | Bedrock provider |
| `AWS_BEDROCK_MODEL` | Bedrock model override | Model selection |
| `STAGEHAND_MODEL` | Model name override | Any provider |
| `HEADLESS` | Headless mode flag | Browser launch |
| `HTTPS_PROXY` / `HTTP_PROXY` | Proxy URL | Proxy configuration |

**Sources:** [services/common/browser/src/implementations/stagehand-browser.ts:747-821]()

---

## Testing

### Unit Tests

Unit tests are not extensive for `StagehandBrowser` because it primarily wraps Stagehand SDK. Most testing is done at the E2E level.

### E2E Tests

E2E tests verify real browser automation with AI operations:

**Test Coverage:**
- Lifecycle (initialize, close)
- Navigation and page information
- Screenshots (PNG, JPEG, full page)
- Waiting operations
- Scrolling
- Element inspection
- AI observation and action
- Token tracking
- History navigation
- Auto-close popups

**Sources:** [services/common/browser/test/e2e/stagehand-browser.e2e.test.ts:1-402]()

**Test Execution:**
```bash
# Requires LLM credentials
pnpm test:e2e
```

---

# Page: AgentCoreBrowser Implementation

# AgentCoreBrowser Implementation

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [services/action-builder/src/index.ts](services/action-builder/src/index.ts)
- [services/common/browser/package.json](services/common/browser/package.json)
- [services/common/browser/src/adapters/browser-adapter.ts](services/common/browser/src/adapters/browser-adapter.ts)
- [services/common/browser/src/adapters/index.ts](services/common/browser/src/adapters/index.ts)
- [services/common/browser/src/implementations/agent-core-browser.ts](services/common/browser/src/implementations/agent-core-browser.ts)
- [services/common/browser/src/implementations/stagehand-browser.ts](services/common/browser/src/implementations/stagehand-browser.ts)
- [services/common/browser/src/types/browser.ts](services/common/browser/src/types/browser.ts)
- [services/common/browser/test/e2e/stagehand-browser.e2e.test.ts](services/common/browser/test/e2e/stagehand-browser.e2e.test.ts)
- [services/common/browser/test/unit/agent-core-browser.ut.test.ts](services/common/browser/test/unit/agent-core-browser.ut.test.ts)

</details>



## Purpose and Scope

This document details the `AgentCoreBrowser` class, an AWS cloud-based implementation of the `BrowserAdapter` interface ([4.1](#4.1)). AgentCoreBrowser provides browser automation capabilities through AWS Bedrock AgentCore Browser Tool and uses Bedrock Claude for AI-powered element observation. For the local Playwright-based implementation, see [StagehandBrowser](#4.2).

**Sources:** [services/common/browser/src/implementations/agent-core-browser.ts:1-12]()

---

## Architecture Overview

AgentCoreBrowser delegates browser automation to AWS AgentCore while implementing AI capabilities through direct Bedrock Claude invocation. This approach eliminates the need for local browser installations and provides enterprise-grade session isolation.

```mermaid
graph TB
    subgraph "AgentCoreBrowser Class"
        ACB[AgentCoreBrowser]
        Config[AgentCoreBrowserConfig]
        State["Private State:<br/>client: PlaywrightBrowser<br/>bedrockClient: BedrockRuntimeClient<br/>initialized: boolean<br/>currentUrl: string"]
    end
    
    subgraph "External Dependencies"
        PWB["PlaywrightBrowser<br/>(bedrock-agentcore/browser/playwright)"]
        BRC["BedrockRuntimeClient<br/>(@aws-sdk/client-bedrock-runtime)"]
        IMC["InvokeModelCommand<br/>(Bedrock API)"]
    end
    
    subgraph "BrowserAdapter Interface"
        BAI["BrowserAdapter<br/>Lifecycle, Navigation,<br/>AI, Element Inspection"]
    end
    
    ACB --|implements| BAI
    ACB --|uses| PWB
    ACB --|uses| BRC
    ACB --|uses| Config
    BRC --|sends| IMC
    
    Config -.->|sessionTimeoutMinutes| PWB
    Config -.->|bedrockModelId| BRC
    State -.->|stores| PWB
    State -.->|stores| BRC
```

**Key Components:**

| Component | Type | Purpose |
|-----------|------|---------|
| `PlaywrightBrowser` | External | AWS AgentCore browser client for page automation |
| `BedrockRuntimeClient` | External | AWS SDK client for invoking Bedrock models |
| `AgentCoreBrowserConfig` | Interface | Configuration including region, timeouts, model ID |
| `currentUrl` | State | Tracks navigation state (AgentCore doesn't expose URL directly) |

**Sources:** [services/common/browser/src/implementations/agent-core-browser.ts:34-87](), [services/common/browser/package.json:40-41]()

---

## Initialization and Lifecycle

### Constructor and Configuration

The `AgentCoreBrowser` constructor accepts an `AgentCoreBrowserConfig` object with defaults resolved from environment variables:

```mermaid
graph LR
    Constructor["new AgentCoreBrowser(config)"]
    Defaults["Default Resolution"]
    EnvVars["Environment Variables:<br/>AWS_REGION<br/>AGENTCORE_BROWSER_MODEL_ID"]
    ConfigStore["this.config"]
    
    Constructor --> Defaults
    Defaults -.->|fallback| EnvVars
    Defaults --> ConfigStore
```

**Configuration Fields:**

| Field | Default | Environment Variable | Description |
|-------|---------|---------------------|-------------|
| `sessionTimeoutMinutes` | 15 | - | Session duration (max 480 for 8 hours) |
| `region` | 'us-east-1' | `AWS_REGION` | AWS region for AgentCore |
| `timeout` | 60000 | - | Default navigation timeout (ms) |
| `bedrockModelId` | 'us.anthropic.claude-3-5-sonnet-20241022-v2:0' | `AGENTCORE_BROWSER_MODEL_ID` | Bedrock model for AI operations |

**Sources:** [services/common/browser/src/implementations/agent-core-browser.ts:56-87]()

### Initialization Flow

The `initialize()` method creates both the browser client and Bedrock client but defers session creation until first use:

```mermaid
sequenceDiagram
    participant Caller
    participant ACB as AgentCoreBrowser
    participant PWB as PlaywrightBrowser
    participant BRC as BedrockRuntimeClient
    
    Caller->>ACB: initialize()
    
    alt Already initialized
        ACB-->>Caller: return (no-op)
    end
    
    ACB->>PWB: new PlaywrightBrowser({ region })
    PWB-->>ACB: client instance
    
    ACB->>BRC: new BedrockRuntimeClient({ region })
    BRC-->>ACB: bedrock client
    
    ACB->>ACB: this.initialized = true
    
    Note over ACB: Session created later on first navigate()
    
    ACB-->>Caller: success
```

**Sources:** [services/common/browser/src/implementations/agent-core-browser.ts:93-124]()

### Session Lifecycle

Unlike local browsers, AgentCoreBrowser manages cloud-based sessions:

1. **Session Creation:** Implicit on first `navigate()` call
2. **Session Timeout:** Configured via `sessionTimeoutMinutes` (default 15 minutes, max 480)
3. **Session Termination:** Explicit via `close()` which calls `client.stopSession()`

**Sources:** [services/common/browser/src/implementations/agent-core-browser.ts:126-140]()

---

## Core Components

### PlaywrightBrowser Client

The `PlaywrightBrowser` class from `bedrock-agentcore` package provides the core browser automation API. All methods require object parameters:

```mermaid
graph TB
    subgraph "PlaywrightBrowser API"
        Navigate["navigate({ url, timeout?, waitUntil? })"]
        Click["click({ selector, timeout? })"]
        Fill["fill({ selector, value, timeout? })"]
        Type["type({ selector, text, delay? })"]
        Eval["evaluate({ script, args? })"]
        Wait["waitForSelector({ selector, timeout?, state? })"]
        Screen["screenshot({ fullPage?, type? })"]
        GetHTML["getHtml()"]
        GetText["getText({ selector })"]
        Back["back()"]
        PressKey["pressKey(key)"]
    end
    
    Navigate -.->|returns| Promise
    Click -.->|returns| Promise
    Fill -.->|returns| Promise
```

**Key Differences from Stagehand:**
- All methods require object parameters (not positional)
- `evaluate({ script })` takes JavaScript as string, not function
- Screenshot returns base64 string or Buffer
- No built-in AI observe/act (implemented separately via Bedrock)

**Sources:** [services/common/browser/src/implementations/agent-core-browser.ts:146-370]()

### BedrockRuntimeClient for AI

The `observe()` method uses `BedrockRuntimeClient` to invoke Claude with vision:

```mermaid
graph TB
    subgraph "observe() Implementation"
        Start["observe(instruction, timeout)"]
        Screenshot["this.screenshot()"]
        Base64["screenshot.toString('base64')"]
        BuildPrompt["buildObservePrompt(instruction)"]
        InvokeCmd["InvokeModelCommand"]
        Parse["parseObserveResponse(content)"]
        Results["ObserveResult[]"]
    end
    
    Start --> Screenshot
    Screenshot --> Base64
    Start --> BuildPrompt
    Base64 --> InvokeCmd
    BuildPrompt --> InvokeCmd
    
    InvokeCmd --|JSON body with<br/>anthropic_version,<br/>messages,<br/>image source| Parse
    Parse --> Results
    
    subgraph "JSON Request Body"
        Body["anthropic_version: 'bedrock-2023-05-31'<br/>max_tokens: 4096<br/>messages: [{ role: 'user', content: [...] }]<br/>content[0]: image (base64)<br/>content[1]: text (prompt)"]
    end
    
    InvokeCmd -.->|uses| Body
```

**Sources:** [services/common/browser/src/implementations/agent-core-browser.ts:112-116](), [services/common/browser/src/implementations/agent-core-browser.ts:396-475]()

---

## AI Capabilities Implementation

### observe() Method

The `observe()` method finds elements using AI vision analysis:

**Flow:**
1. Capture screenshot via `this.screenshot()`
2. Convert to base64 string
3. Build prompt with `buildObservePrompt(instruction)`
4. Invoke Bedrock Claude with screenshot + prompt
5. Parse response JSON with `parseObserveResponse(content)`
6. Return `ObserveResult[]` with selectors and descriptions

**Prompt Structure:**
```
You are helping the user automate the browser by finding elements...

Instruction: "{instruction}"

CRITICAL RULES:
- ONLY return elements that actually exist and match the instruction
- If no matching elements exist, return []
- Do NOT invent or guess elements that are not clearly visible
- Return ONLY a valid JSON array, no other text
```

**Sources:** [services/common/browser/src/implementations/agent-core-browser.ts:396-475](), [services/common/browser/src/implementations/agent-core-browser.ts:773-795]()

### Response Parsing

The `parseObserveResponse()` private method handles Claude's response with robust error handling:

```mermaid
graph TB
    Parse["parseObserveResponse(content)"]
    StripMarkdown["Strip markdown code blocks<br/>```json...```"]
    ExtractJSON["Extract JSON array<br/>regex: /\[[\s\S]*\]/"]
    ValidateArray["Validate array type"]
    FilterItems["Filter invalid items:<br/>- Missing selector<br/>- Missing description<br/>- Null items"]
    Normalize["Normalize:<br/>- Default method to 'click'<br/>- Include arguments if present"]
    Return["Return ObserveResult[]"]
    Empty["Return []"]
    
    Parse --> StripMarkdown
    StripMarkdown --> ExtractJSON
    ExtractJSON -->|no match| Empty
    ExtractJSON --> ValidateArray
    ValidateArray -->|not array| Empty
    ValidateArray --> FilterItems
    FilterItems --> Normalize
    Normalize --> Return
```

**Sources:** [services/common/browser/src/implementations/agent-core-browser.ts:800-847]()

### act() and actWithSelector()

The `act()` method routes requests based on input type:

| Input Type | Routing | Behavior |
|------------|---------|----------|
| `string` | `observe()` → `actWithSelector()` | Natural language → Find element → Execute action |
| `ActionObject` | `actWithSelector()` | Direct execution with selector |

**actWithSelector() Method Dispatch:**

```mermaid
graph TB
    ActWith["actWithSelector(action)"]
    Switch{"action.method"}
    
    Click["click({ selector })"]
    Fill["fill({ selector, value })"]
    Type["type({ selector, text })"]
    Hover["evaluate({ script })<br/>MouseOver event"]
    Select["evaluate({ script })<br/>Set value + change event"]
    Scroll["scroll('down', 300)"]
    Wait["wait(ms)"]
    Press["pressKey(key)"]
    Error["throw: Unsupported method"]
    
    ActWith --> Switch
    Switch -->|'click'| Click
    Switch -->|'fill'| Fill
    Switch -->|'type'| Type
    Switch -->|'hover'| Hover
    Switch -->|'select'| Select
    Switch -->|'scroll'| Scroll
    Switch -->|'wait'| Wait
    Switch -->|'press'| Press
    Switch -->|unknown| Error
    
    Fill -.->|requires| Args["arguments[0]"]
    Type -.->|requires| Args
    Select -.->|requires| Args
    Press -.->|requires| Args
```

**Sources:** [services/common/browser/src/implementations/agent-core-browser.ts:482-584]()

---

## Method Implementations

### Navigation Methods

**navigate(url, options?)**

Calls `client.navigate({ url, timeout, waitUntil })` and updates `currentUrl` state:

```typescript
// AgentCore SDK requires object parameter
await client.navigate({
  url,
  timeout: options?.timeout ?? this.config.timeout,
  waitUntil: options?.waitUntil ?? 'domcontentloaded',
});
this.currentUrl = url; // Track URL manually
```

**goBack()**

Simple wrapper: `await client.back()`

**Sources:** [services/common/browser/src/implementations/agent-core-browser.ts:146-169]()

### Page Information Methods

**getUrl()**

Returns `this.currentUrl` (tracked internally, not from AgentCore)

**getTitle()**

```typescript
const title = await client.evaluate({ script: 'document.title' });
return title || '';
```

**getContent()**

```typescript
const html = await client.getHtml();
return html || '';
```

**Sources:** [services/common/browser/src/implementations/agent-core-browser.ts:175-199]()

### Screenshot Method

Handles format conversion and base64-to-Buffer:

```mermaid
graph LR
    SS["screenshot(options?)"]
    Format["Format Mapping:<br/>webp → png<br/>jpeg → jpeg<br/>default → png"]
    SDK["client.screenshot({ fullPage, type })"]
    Convert["Base64 string → Buffer"]
    Return["Buffer"]
    
    SS --> Format
    Format --> SDK
    SDK --> Convert
    Convert --> Return
```

**Why webp → png:** AgentCore SDK only supports 'png' | 'jpeg', not 'webp'

**Sources:** [services/common/browser/src/implementations/agent-core-browser.ts:205-227]()

### Waiting Methods

**waitForSelector(selector, options?)**

Maps `BrowserAdapter` options to AgentCore state parameter:

| BrowserAdapter Option | AgentCore State |
|----------------------|-----------------|
| `hidden: true` | `'hidden'` |
| `visible: true` | `'visible'` |
| (default) | `'attached'` |

**wait(ms)**

Standard Promise-based delay: `new Promise(resolve => setTimeout(resolve, ms))`

**waitForText(text, timeout)**

Polls `getContent()` every 500ms until text found or timeout

**Sources:** [services/common/browser/src/implementations/agent-core-browser.ts:233-270](), [services/common/browser/src/implementations/agent-core-browser.ts:650-670]()

### Scrolling Methods

**scroll(direction, amount?)**

```typescript
const delta = direction === 'down' ? amount : -amount;
await client.evaluate({
  script: `window.scrollBy(0, ${delta})`,
});
```

**scrollToBottom(waitAfterMs?)**

Iteratively scrolls to bottom, checking `document.body.scrollHeight` until no change (max 10 attempts)

**Sources:** [services/common/browser/src/implementations/agent-core-browser.ts:262-310]()

---

## Element Inspection

### getElementAttributesFromXPath()

Extracts comprehensive element metadata via `evaluate()`:

```mermaid
graph TB
    GetAttrs["getElementAttributesFromXPath(xpath)"]
    Normalize["Remove 'xpath=' prefix"]
    Escape["escapeForJs(xpath)"]
    BuildScript["Build inline script:<br/>document.evaluate(...)<br/>Extract attributes"]
    Eval["client.evaluate({ script })"]
    Return["ElementAttributes | null"]
    
    GetAttrs --> Normalize
    Normalize --> Escape
    Escape --> BuildScript
    BuildScript --> Eval
    Eval --> Return
    
    subgraph "Extracted Attributes"
        Attrs["tagName, id, className,<br/>dataTestId, ariaLabel,<br/>placeholder, name,<br/>textContent, dataAttributes"]
    end
    
    Eval -.->|returns| Attrs
```

**Script Structure:**

```javascript
(() => {
  const el = document.evaluate(
    "//xpath/here",
    document,
    null,
    XPathResult.FIRST_ORDERED_NODE_TYPE,
    null
  ).singleNodeValue;
  
  if (!el) return null;
  
  // Collect data-* attributes
  const dataAttributes = {};
  for (const attr of el.attributes) {
    if (attr.name.startsWith('data-')) {
      dataAttributes[attr.name] = attr.value;
    }
  }
  
  return { tagName, id, className, ... };
})()
```

**Sources:** [services/common/browser/src/implementations/agent-core-browser.ts:589-630]()

### XPath and Selector Utilities

**isXPathSelector(selector)**

Checks if selector starts with `'xpath='`, `'/'`, or `'('`

**buildElementScript(selector, action)**

Generates JavaScript to find element (XPath or CSS) and execute action:

```typescript
if (isXPathSelector(selector)) {
  return `(() => { 
    const el = document.evaluate(${escapeForJs(cleanSelector)}, ...);
    ${action}
  })()`;
} else {
  return `(() => { 
    const el = document.querySelector(${escapeForJs(cleanSelector)});
    ${action}
  })()`;
}
```

**Sources:** [services/common/browser/src/implementations/agent-core-browser.ts:750-766]()

---

## Configuration and Environment

### Environment Variable Resolution

```mermaid
graph LR
    subgraph "Configuration Priority"
        Explicit["Explicit config parameter"]
        EnvVar["Environment variable"]
        Default["Hardcoded default"]
    end
    
    Explicit -->|highest| Priority
    EnvVar -->|medium| Priority
    Default -->|lowest| Priority
    
    subgraph "Environment Variables"
        AWSRegion["AWS_REGION"]
        ModelID["AGENTCORE_BROWSER_MODEL_ID"]
    end
    
    EnvVar -.->|maps to| AWSRegion
    EnvVar -.->|maps to| ModelID
```

**Configuration Example:**

```typescript
const browser = new AgentCoreBrowser({
  sessionTimeoutMinutes: 30,      // Override default
  region: 'us-west-2',            // Override env
  bedrockModelId: 'custom-model', // Override env
});
```

**Sources:** [services/common/browser/src/implementations/agent-core-browser.ts:76-86]()

### AWS Credentials

AgentCoreBrowser requires AWS credentials via standard AWS SDK resolution:
- Environment variables: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_SESSION_TOKEN`
- IAM role (when running on AWS)
- AWS credentials file (`~/.aws/credentials`)

**Required IAM Permissions:**
- `bedrock:InvokeModel` for AI observe operations
- AgentCore browser session management (specific permissions vary by AWS account setup)

**Sources:** [services/common/browser/src/implementations/agent-core-browser.ts:112-116]()

---

## Comparison with StagehandBrowser

### Key Differences

| Feature | AgentCoreBrowser | StagehandBrowser ([4.2](#4.2)) |
|---------|------------------|--------------------------------|
| **Execution** | AWS cloud-based | Local Playwright |
| **Installation** | No local browser needed | Requires Chromium/Chrome |
| **AI Provider** | Bedrock Claude (fixed) | OpenRouter/OpenAI/Anthropic/Bedrock |
| **Token Tracking** | Not tracked (Bedrock billing separate) | Tracked via Stagehand metrics |
| **Browser Profiles** | Not supported | Supported via `BrowserProfileManager` |
| **Session Management** | Cloud session with timeout | Local process |
| **Observe Implementation** | Screenshot + Bedrock InvokeModel | Stagehand SDK observe() |
| **Act Implementation** | Manual method dispatch | Stagehand SDK act() |
| **Proxy Support** | Via AWS VPC/networking | Via Playwright proxy config |

**Sources:** [services/common/browser/src/implementations/agent-core-browser.ts:1-849](), [services/common/browser/src/implementations/stagehand-browser.ts:1-1118]()

### When to Use AgentCoreBrowser

**Use AgentCoreBrowser when:**
- Running in AWS environment (Lambda, ECS, EC2)
- No local browser installation possible
- Need session recording/replay (AgentCore feature)
- Enterprise security requirements (VPC isolation)
- Automatic scaling needed

**Use StagehandBrowser when:**
- Local development
- Need multiple LLM provider options
- Require browser profile persistence
- Need detailed token usage metrics
- Proxy configuration required

**Sources:** [services/common/browser/src/implementations/agent-core-browser.ts:6-12]()

---

## Error Handling and Edge Cases

### Common Error Patterns

**Initialization State:**
```typescript
private ensureInitialized(): void {
  if (!this.client || !this.initialized) {
    throw new Error('Browser not initialized. Call initialize() first.');
  }
}
```

All major methods call `ensureInitialized()` or use `getClient()` which includes this check.

**Missing Arguments:**
```typescript
case 'fill':
case 'type':
  if (!args || args.length === 0) {
    throw new Error(`${method} action requires text argument`);
  }
```

**Element Not Found:**
```typescript
if (!selector) {
  throw new Error(`No elements found matching: ${instructionOrAction}`);
}
```

**Sources:** [services/common/browser/src/implementations/agent-core-browser.ts:724-738]()

### Response Parsing Robustness

The `parseObserveResponse()` handles various Claude response formats:

1. **Markdown code blocks:** Strips ` ```json ... ``` ` wrappers
2. **Plain JSON array:** Extracts `[...]` via regex
3. **Invalid JSON:** Returns empty array `[]`
4. **Non-array response:** Returns empty array `[]`
5. **Invalid items:** Filters out items missing required fields

**Sources:** [services/common/browser/src/implementations/agent-core-browser.ts:800-847]()

---

## Testing

### Unit Test Coverage

The unit tests mock external dependencies and verify internal logic:

```mermaid
graph TB
    subgraph "Test Categories"
        Config["Configuration Tests"]
        Init["Initialization State Tests"]
        Format["Format Conversion Tests"]
        State["State Mapping Tests"]
        Dispatch["Method Dispatch Tests"]
        Parse["Response Parsing Tests"]
        XPath["XPath Normalization Tests"]
    end
    
    subgraph "Mocked Dependencies"
        MockPWB["Mock PlaywrightBrowser"]
        MockBRC["Mock BedrockRuntimeClient"]
    end
    
    Config -.->|uses| MockPWB
    Init -.->|uses| MockPWB
    Format -.->|uses| MockPWB
    State -.->|uses| MockPWB
    Dispatch -.->|uses| MockPWB
    Parse -.->|pure logic| None["No mocks needed"]
    XPath -.->|uses| MockPWB
```

**Test File Structure:**

| Test Suite | Focus | Key Tests |
|------------|-------|-----------|
| Configuration | Config resolution | Default values, env vars, custom config |
| Initialization State | Lifecycle guards | Errors before init, double init |
| Screenshot Format Conversion | webp → png mapping | Format handling, base64 conversion |
| waitForSelector State Mapping | Option → state translation | hidden/visible/attached mapping |
| Scroll Direction | Delta calculation | up = negative, down = positive |
| act() Routing | Instruction vs ActionObject | String → observe, Object → actWithSelector |
| actWithSelector Method Dispatch | Switch statement logic | All action methods, error cases |
| XPath Normalization | Prefix handling | Remove 'xpath=' prefix |
| parseObserveResponse | JSON extraction | Markdown blocks, filtering, defaults |

**Sources:** [services/common/browser/test/unit/agent-core-browser.ut.test.ts:1-727]()

### E2E Test Considerations

E2E tests for AgentCoreBrowser require:
- AWS credentials with Bedrock access
- `AWS_AGENTCORE_RUNTIME=true` or `BROWSER_TYPE=agentcore`
- Tests are skipped when running in StagehandBrowser environment

**Example E2E test pattern:**
```typescript
const isAgentCoreEnv =
  process.env.AWS_AGENTCORE_RUNTIME === 'true' ||
  process.env.BROWSER_TYPE === 'agentcore';

const describeIfAgentCore = isAgentCoreEnv ? describe : describe.skip;

describeIfAgentCore('AgentCoreBrowser E2E', () => {
  // Tests run only in AgentCore environment
});
```

**Sources:** [services/common/browser/test/e2e/stagehand-browser.e2e.test.ts:17-30]()

---

## Integration with Action Builder

AgentCoreBrowser is used by the Action Builder service as one of the browser adapter options:

```mermaid
graph TB
    subgraph "Action Builder Service"
        AB["ActionBuilder"]
        BAI["BrowserAdapter Interface"]
    end
    
    subgraph "Browser Selection"
        EnvCheck{"AWS_AGENTCORE_RUNTIME<br/>or<br/>BROWSER_TYPE=agentcore"}
        CreateACB["new AgentCoreBrowser()"]
        CreateSHB["new StagehandBrowser()"]
    end
    
    subgraph "Recording Operations"
        Recorder["ActionRecorder"]
        Tools["RecorderToolExecutor"]
    end
    
    AB --> EnvCheck
    EnvCheck -->|true| CreateACB
    EnvCheck -->|false| CreateSHB
    CreateACB --> BAI
    CreateSHB --> BAI
    BAI --> Recorder
    Recorder --> Tools
```

The selection is typically based on execution environment (AWS Lambda/ECS for AgentCore, local for Stagehand).

**Sources:** [services/action-builder/src/index.ts:5-6]()

---

## Package Structure and Dependencies

### Package Configuration

AgentCoreBrowser is part of the `@actionbookdev/browser` package with conditional dependencies:

```json
{
  "name": "@actionbookdev/browser",
  "exports": {
    "./agentcore": {
      "types": "./dist/implementations/agent-core-browser.d.ts",
      "import": "./dist/implementations/agent-core-browser.js"
    }
  },
  "peerDependencies": {
    "bedrock-agentcore": ">=0.1.0"
  },
  "peerDependenciesMeta": {
    "bedrock-agentcore": {
      "optional": true
    }
  },
  "dependencies": {
    "@aws-sdk/client-bedrock-runtime": "^3.966.0"
  }
}
```

**Dependency Strategy:**
- `bedrock-agentcore` is a peer dependency (optional) to avoid installation when not needed
- `@aws-sdk/client-bedrock-runtime` is a regular dependency (always installed)
- Build system (tsup) marks both as external to avoid bundling

**Sources:** [services/common/browser/package.json:1-74]()

### Import Pattern

```typescript
// Static import for external dependency
import { PlaywrightBrowser } from 'bedrock-agentcore/browser/playwright';
import {
  BedrockRuntimeClient,
  InvokeModelCommand,
} from '@aws-sdk/client-bedrock-runtime';

// Implementation
export class AgentCoreBrowser implements BrowserAdapter {
  private client: InstanceType<typeof PlaywrightBrowser> | null = null;
  private bedrockClient: BedrockRuntimeClient | null = null;
  // ...
}
```

**Sources:** [services/common/browser/src/implementations/agent-core-browser.ts:14-39]()

---

# Page: Browser Profiles

# Browser Profiles

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.prettierignore](.prettierignore)
- [.prettierrc.json](.prettierrc.json)
- [CLAUDE.md](CLAUDE.md)
- [services/action-builder/scripts/login.ts](services/action-builder/scripts/login.ts)
- [services/action-builder/src/optimizer/SelectorOptimizer.ts](services/action-builder/src/optimizer/SelectorOptimizer.ts)
- [services/common/browser-profile/package.json](services/common/browser-profile/package.json)
- [services/common/browser-profile/src/BrowserProfileManager.ts](services/common/browser-profile/src/BrowserProfileManager.ts)

</details>



## Purpose and Scope

This document describes the browser profile management system that enables persistent login state across browser automation sessions. The `BrowserProfileManager` class provides a unified interface for managing Playwright's `userDataDir` feature, allowing "login once, reuse many times" workflows for recording and automation tasks.

For browser automation interfaces and implementations, see [BrowserAdapter Interface](#4.1), [StagehandBrowser Implementation](#4.2), and [AgentCoreBrowser Implementation](#4.3). For the broader browser automation architecture, see [Browser Automation Layer](#4).

## Overview

The browser profile system solves a critical problem in web automation: maintaining authenticated state across multiple sessions. Without persistent profiles, automation scripts must re-authenticate on every run, which is time-consuming, error-prone, and may trigger anti-bot detection.

The system is built around Playwright's `userDataDir` feature, which persists browser state (cookies, localStorage, sessionStorage, IndexedDB) to disk. The `BrowserProfileManager` class wraps this functionality with additional features:

- Lock file cleanup for crashed browser instances
- Anti-detection arguments to avoid automation detection
- Profile lifecycle management (create, clear, info)
- Proxy support configuration

**Sources:** [services/common/browser-profile/src/BrowserProfileManager.ts:1-239]()

## Architecture

```mermaid
graph TB
    subgraph "User Actions"
        LoginScript["login.ts<br/>pnpm login"]
        RecordingTask["Recording Task<br/>ActionRecorder"]
        PlaybookTask["Playbook Task<br/>PlaybookTaskController"]
    end
    
    subgraph "Profile Manager"
        BPM["BrowserProfileManager"]
        GetPath["getProfilePath()"]
        Exists["exists()"]
        CleanupLocks["cleanupStaleLocks()"]
        GetLaunchOpts["getLaunchOptions()"]
    end
    
    subgraph "File System"
        ProfileDir[".browser-profile/<br/>userDataDir"]
        Cookies["Cookies"]
        LocalStorage["Local Storage"]
        SessionStorage["Session Storage"]
        IndexedDB["IndexedDB"]
        LockFiles["SingletonLock<br/>SingletonSocket<br/>SingletonCookie"]
    end
    
    subgraph "Browser Implementations"
        StagehandBrowser["StagehandBrowser"]
        AgentCoreBrowser["AgentCoreBrowser"]
        Playwright["Playwright<br/>Browser Context"]
    end
    
    LoginScript --> BPM
    RecordingTask --> BPM
    PlaybookTask --> BPM
    
    BPM --> GetPath
    BPM --> Exists
    BPM --> CleanupLocks
    BPM --> GetLaunchOpts
    
    GetPath --> ProfileDir
    CleanupLocks --> LockFiles
    GetLaunchOpts --> StagehandBrowser
    GetLaunchOpts --> AgentCoreBrowser
    
    StagehandBrowser --> Playwright
    AgentCoreBrowser --> Playwright
    
    Playwright --> ProfileDir
    ProfileDir --> Cookies
    ProfileDir --> LocalStorage
    ProfileDir --> SessionStorage
    ProfileDir --> IndexedDB
```

**Sources:** [services/common/browser-profile/src/BrowserProfileManager.ts:74-99](), [services/action-builder/scripts/login.ts:1-149]()

## BrowserProfileManager Class

The `BrowserProfileManager` class is the core component for profile management, defined in [services/common/browser-profile/src/BrowserProfileManager.ts:100-239]().

### Constructor and Configuration

```typescript
interface ProfileConfig {
  baseDir?: string;      // Default: '.browser-profile'
  logger?: ProfileLogger;
}
```

The constructor accepts optional configuration:
- `baseDir`: Directory for profile storage, defaults to `DEFAULT_PROFILE_DIR` (`.browser-profile`)
- `logger`: Custom logging function for different log levels

**Sources:** [services/common/browser-profile/src/BrowserProfileManager.ts:37-107]()

### Core Methods

| Method | Return Type | Description |
|--------|-------------|-------------|
| `getProfilePath()` | `string` | Returns absolute path to profile directory |
| `exists()` | `boolean` | Checks if profile directory exists |
| `ensureDir()` | `void` | Creates profile directory if missing |
| `clear()` | `void` | Deletes all profile data |
| `cleanupStaleLocks()` | `void` | Removes stale Chromium lock files |
| `getInfo()` | `ProfileInfo` | Returns profile metadata (exists, path, size) |
| `getLaunchOptions()` | `Record<string, unknown>` | Returns browser launch options with profile config |

**Sources:** [services/common/browser-profile/src/BrowserProfileManager.ts:109-238]()

## Profile Storage Structure

The profile directory stores persistent browser state in Chromium's native format:

```mermaid
graph TB
    subgraph "File System Layout"
        Root[".browser-profile/"]
        
        Root --> Cookies["Cookies<br/>(SQLite)"]
        Root --> Prefs["Preferences<br/>(JSON)"]
        Root --> LocalState["Local State<br/>(JSON)"]
        Root --> DefaultDir["Default/"]
        
        DefaultDir --> History["History<br/>(SQLite)"]
        DefaultDir --> LS["Local Storage/<br/>(LevelDB)"]
        DefaultDir --> SS["Session Storage/<br/>(LevelDB)"]
        DefaultDir --> IDB["IndexedDB/"]
        
        Root --> LockFiles["Lock Files:<br/>SingletonLock<br/>SingletonSocket<br/>SingletonCookie"]
    end
    
    subgraph "Lock File Management"
        CleanupLocks["cleanupStaleLocks()"]
        LockFiles -.->|"Removes stale locks"| CleanupLocks
    end
```

### Lock File Cleanup

Chromium creates lock files (`SingletonLock`, `SingletonSocket`, `SingletonCookie`) to prevent multiple browser instances from using the same profile simultaneously. If a browser crashes, these files persist and prevent future launches. The `cleanupStaleLocks()` method removes these files before launching.

**Implementation:** [services/common/browser-profile/src/BrowserProfileManager.ts:148-166]()

```typescript
cleanupStaleLocks(): void {
  const profilePath = this.getProfilePath();
  const lockFiles = ["SingletonLock", "SingletonSocket", "SingletonCookie"];
  
  for (const lockFile of lockFiles) {
    const lockPath = path.join(profilePath, lockFile);
    if (fs.existsSync(lockPath)) {
      fs.unlinkSync(lockPath);
    }
  }
}
```

**Sources:** [services/common/browser-profile/src/BrowserProfileManager.ts:148-166]()

## Anti-Detection Configuration

The system provides anti-detection arguments to prevent websites from detecting automation:

### Constants

```typescript
// Defined at module level
export const ANTI_DETECTION_ARGS = [
  "--disable-blink-features=AutomationControlled",
  "--no-first-run",
];

export const IGNORE_DEFAULT_ARGS = ["--enable-automation"];
```

**Sources:** [services/common/browser-profile/src/BrowserProfileManager.ts:63-71]()

### Launch Options

The `getLaunchOptions()` method returns browser launch configuration with profile and anti-detection settings:

```mermaid
graph LR
    subgraph "Input Options"
        Headless["headless: boolean"]
        Proxy["proxy: {server}"]
    end
    
    subgraph "getLaunchOptions()"
        Method["getLaunchOptions()"]
    end
    
    subgraph "Output Configuration"
        UserDataDir["userDataDir: profilePath"]
        PreserveDir["preserveUserDataDir: true"]
        Args["args: ANTI_DETECTION_ARGS"]
        IgnoreArgs["ignoreDefaultArgs:<br/>IGNORE_DEFAULT_ARGS"]
        ProxyConfig["proxy: {server}"]
    end
    
    Headless --> Method
    Proxy --> Method
    
    Method --> UserDataDir
    Method --> PreserveDir
    Method --> Args
    Method --> IgnoreArgs
    Method --> ProxyConfig
```

**Implementation:** [services/common/browser-profile/src/BrowserProfileManager.ts:218-238]()

The method:
1. Calls `cleanupStaleLocks()` before launch
2. Sets `userDataDir` to profile path
3. Enables `preserveUserDataDir` to prevent cleanup on close
4. Applies anti-detection arguments
5. Optionally configures proxy from environment or parameters

**Sources:** [services/common/browser-profile/src/BrowserProfileManager.ts:218-238]()

## Login Workflow

The `pnpm login` command launches an interactive browser session for manual authentication:

```mermaid
sequenceDiagram
    participant User
    participant LoginScript as "login.ts"
    participant BPM as "BrowserProfileManager"
    participant Stagehand
    participant Browser as "Chromium Browser"
    participant FileSystem as "File System"
    
    User->>LoginScript: pnpm login [--url] [--clear]
    LoginScript->>BPM: getInfo()
    BPM->>FileSystem: Check profile exists
    FileSystem-->>BPM: Profile status
    BPM-->>LoginScript: ProfileInfo
    
    alt --clear flag
        LoginScript->>BPM: clear()
        BPM->>FileSystem: Delete profile directory
    end
    
    LoginScript->>BPM: ensureDir()
    BPM->>FileSystem: Create profile directory
    
    LoginScript->>BPM: getProfilePath()
    BPM-->>LoginScript: profilePath
    
    LoginScript->>Stagehand: new Stagehand({<br/>localBrowserLaunchOptions: {<br/>  userDataDir,<br/>  preserveUserDataDir,<br/>  args, ignoreDefaultArgs<br/>}})
    
    Stagehand->>Browser: Launch with profile
    Browser->>FileSystem: Load existing state
    
    opt URL provided
        LoginScript->>Browser: page.goto(url)
    end
    
    Browser-->>User: Display browser window
    User->>Browser: Manual login
    User->>LoginScript: Press ENTER
    
    LoginScript->>Stagehand: close()
    Stagehand->>Browser: Close browser
    Browser->>FileSystem: Save state to userDataDir
    FileSystem-->>LoginScript: Profile saved
```

### Command Line Arguments

| Argument | Description |
|----------|-------------|
| `--url <url>` | Navigate to specific URL on launch |
| `--clear` | Clear existing profile before login |
| `--help` or `-h` | Display help message |

**Sources:** [services/action-builder/scripts/login.ts:1-149]()

### Script Implementation Details

The login script [services/action-builder/scripts/login.ts:59-143]():

1. **Initialize Manager**: Creates `BrowserProfileManager` with default directory
2. **Display Info**: Shows current profile status (path, size)
3. **Clear Profile** (optional): Removes existing profile if `--clear` flag provided
4. **Ensure Directory**: Creates profile directory if missing
5. **Configure Browser**: Builds launch options with profile path and anti-detection args
6. **Proxy Support**: Automatically detects `HTTPS_PROXY` or `HTTP_PROXY` environment variables
7. **Launch Browser**: Initializes Stagehand with persistent profile
8. **Navigate** (optional): Opens specified URL if `--url` provided
9. **Wait for User**: Displays instructions and waits for ENTER key
10. **Save and Exit**: Closes browser, automatically persisting state to disk

**Sources:** [services/action-builder/scripts/login.ts:59-143]()

## Integration with Browser Adapters

Both `StagehandBrowser` and `AgentCoreBrowser` can use persistent profiles, though the implementation differs:

### StagehandBrowser Integration

`StagehandBrowser` runs locally with Playwright and supports full profile persistence:

```typescript
// StagehandBrowser initialization with profile
const profileManager = new BrowserProfileManager();
const launchOptions = profileManager.getLaunchOptions({
  headless: false,
  proxy: proxyConfig
});

const stagehand = new Stagehand({
  env: "LOCAL",
  localBrowserLaunchOptions: launchOptions,
});
```

The profile manager's launch options are directly compatible with Stagehand's `localBrowserLaunchOptions` parameter.

**Sources:** [services/action-builder/scripts/login.ts:92-112](), [services/common/browser-profile/src/BrowserProfileManager.ts:218-238]()

### Profile Usage Pattern

```mermaid
graph TB
    subgraph "Profile Check Pattern"
        Start[/"Start Recording Task"/]
        CheckProfile{"Profile<br/>Configured?"}
        ProfileExists{"profileManager.exists()"}
        UseProfile["Launch with<br/>profileManager.getLaunchOptions()"]
        NoProfile["Launch without profile<br/>(anonymous session)"]
        WarnUser["Log: Run 'pnpm login'<br/>for authenticated tasks"]
        Execute["Execute Recording"]
    end
    
    Start --> CheckProfile
    CheckProfile -->|Yes| ProfileExists
    CheckProfile -->|No| NoProfile
    ProfileExists -->|true| UseProfile
    ProfileExists -->|false| WarnUser
    WarnUser --> NoProfile
    UseProfile --> Execute
    NoProfile --> Execute
```

**Sources:** [services/common/browser-profile/src/BrowserProfileManager.ts:74-99](), [services/action-builder/scripts/login.ts:1-149]()

## Environment Variables and Proxy Support

The profile system respects standard proxy environment variables:

| Variable | Purpose |
|----------|---------|
| `HTTPS_PROXY` | HTTPS proxy URL (checked first) |
| `HTTP_PROXY` | HTTP proxy URL (fallback) |

When either variable is set, the profile manager automatically configures the browser to use the proxy. This is particularly useful in corporate environments or when routing traffic through debugging proxies.

**Implementation:** [services/action-builder/scripts/login.ts:86-105]()

**Sources:** [services/action-builder/scripts/login.ts:86-105](), [services/common/browser-profile/src/BrowserProfileManager.ts:218-238]()

## Package Structure

The browser profile functionality is packaged as an internal monorepo package:

```
services/common/browser-profile/
├── src/
│   ├── BrowserProfileManager.ts    # Main class
│   └── index.ts                     # Public exports
├── package.json                     # Package metadata
└── tsconfig.json                    # TypeScript config
```

**Package Name:** `@actionbookdev/browser-profile`

**Exports:**
- `BrowserProfileManager` - Main class
- `DEFAULT_PROFILE_DIR` - Default directory constant (`.browser-profile`)
- `ANTI_DETECTION_ARGS` - Browser arguments array
- `IGNORE_DEFAULT_ARGS` - Arguments to ignore array
- `ProfileConfig` - Configuration interface
- `ProfileInfo` - Info result interface
- `ProfileLogger` - Logger function type

**Sources:** [services/common/browser-profile/package.json:1-34](), [services/common/browser-profile/src/BrowserProfileManager.ts:1-239]()

## Best Practices

### When to Use Profiles

| Scenario | Use Profile? | Reason |
|----------|-------------|--------|
| Recording authenticated pages | Yes | Maintains login state across recordings |
| Batch crawling multiple sites | Yes | Avoids rate limiting, maintains sessions |
| Public pages only | No | Profile overhead unnecessary |
| CI/CD environments | Conditional | Use if login state can be pre-configured |
| Development testing | Yes | Faster iteration, consistent state |

### Profile Lifecycle Management

1. **Initial Setup**: Run `pnpm login` once per development environment
2. **Maintenance**: Clear profile (`pnpm login --clear`) if:
   - Login state becomes invalid
   - Testing different user accounts
   - Profile corruption suspected
3. **Cleanup**: Profile is preserved between sessions by default (`.browser-profile` in `.gitignore`)

### Anti-Detection Considerations

The anti-detection configuration helps avoid detection but is not foolproof:
- Disables `navigator.webdriver` property
- Removes automation indicators
- Preserves normal browser fingerprint

For sensitive automation tasks, consider additional measures:
- Random delays between actions
- Human-like mouse movements
- Viewport size variation
- User agent rotation

**Sources:** [services/common/browser-profile/src/BrowserProfileManager.ts:63-71](), [services/action-builder/scripts/login.ts:1-149]()

---

# Page: Data Layer

# Data Layer

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [services/db/migrations/0019_add_vector_indexes.sql](services/db/migrations/0019_add_vector_indexes.sql)
- [services/db/migrations/0020_add_chunks_fulltext_index.sql](services/db/migrations/0020_add_chunks_fulltext_index.sql)
- [services/db/src/connection.ts](services/db/src/connection.ts)

</details>



## Purpose and Scope

The Data Layer provides persistent storage for all Actionbook data, including discovered website capabilities, recorded UI elements, crawled documentation, and build pipeline state. This page covers the overall data storage architecture, including the PostgreSQL database, schema organization, version management, and the dual persistence strategy that maintains both structured database records and human-readable YAML files.

For detailed information on specific aspects of the data layer:
- Database schema tables, relationships, and fields: see [Database Schema](#5.1)
- Connection pooling, driver selection, and the `getDb()` singleton: see [Database Connection Management](#5.2)
- Full-text indexes, vector indexes, and hybrid search implementation: see [Search and Indexing](#5.3)

## Storage Architecture

Actionbook uses PostgreSQL as its primary data store with a dual persistence strategy:

| Storage Type | Purpose | Use Cases |
|--------------|---------|-----------|
| **PostgreSQL Database** | Structured querying, search, and transactional operations | API queries, task orchestration, version management, hybrid search |
| **YAML Files** | Human-readable action manuals | Direct file inspection, git version control, offline reference |

The database serves as the source of truth for all structured data, while YAML files in `output/sites/` provide portable, human-readable exports of discovered capabilities.

Sources: [Diagram 5 from architecture overview]

## Database Connection Management

### Connection Strategy

Actionbook uses different PostgreSQL drivers depending on the execution environment:

```mermaid
graph TB
    subgraph "Connection Resolution"
        getDb["getDb()"]
        createDb["createDb()"]
        shouldUsePg["shouldUsePgDriver()"]
    end
    
    subgraph "Environment Detection"
        nodeEnv["NODE_ENV !== 'production'"]
        agentCore["AWS_AGENTCORE_RUNTIME === 'true'"]
        vercel["process.env.VERCEL"]
    end
    
    subgraph "Driver Selection"
        pgDriver["node-postgres (pg)<br/>TCP connection"]
        neonDriver["@neondatabase/serverless<br/>WebSocket connection"]
    end
    
    subgraph "Connection Pools"
        pgPool["Pool<br/>max: 20 (local)<br/>max: 5 (serverless)"]
        neonPool["NeonPool<br/>WebSocket-based"]
    end
    
    subgraph "Drizzle ORM"
        drizzlePg["drizzlePg(pool, schema)"]
        drizzleNeon["drizzleNeon(pool, schema)"]
        dbType["Database<br/>(NodePgDatabase)"]
    end
    
    getDb --> createDb
    createDb --> shouldUsePg
    
    shouldUsePg --> nodeEnv
    shouldUsePg --> agentCore
    shouldUsePg --> vercel
    
    nodeEnv -->|"true"| pgDriver
    agentCore -->|"true"| pgDriver
    vercel -->|"false"| pgDriver
    vercel -->|"true"| neonDriver
    
    pgDriver --> pgPool
    neonDriver --> neonPool
    
    pgPool --> drizzlePg
    neonPool --> drizzleNeon
    
    drizzlePg --> dbType
    drizzleNeon --> dbType
```

Sources: [services/db/src/connection.ts:1-147]()

### Driver Selection Logic

The `shouldUsePgDriver()` function determines which driver to use:

| Condition | Driver Used | Reason |
|-----------|-------------|--------|
| `NODE_ENV !== 'production'` | **node-postgres** | Local development with TCP |
| `AWS_AGENTCORE_RUNTIME === 'true'` | **node-postgres** | Node.js runtime needs TCP, not WebSocket |
| `!process.env.VERCEL` | **node-postgres** | Non-Vercel production environments |
| `process.env.VERCEL` (production) | **Neon serverless** | Vercel edge/serverless with WebSocket support |

Sources: [services/db/src/connection.ts:25-40]()

### Connection Pool Configuration

Connection pool settings are optimized based on the execution environment:

```mermaid
graph LR
    subgraph "Pool Configuration"
        detect["Environment Detection"]
        
        subgraph "Serverless (Vercel/Lambda)"
            sMax["max: 5"]
            sMin["min: 0"]
            sIdle["idleTimeoutMillis: 30000"]
            sExit["allowExitOnIdle: true"]
        end
        
        subgraph "Traditional (Local/Long-running)"
            tMax["max: 20"]
            tMin["min: 2"]
            tIdle["idleTimeoutMillis: 30000"]
            tExit["allowExitOnIdle: false"]
        end
    end
    
    detect -->|"isServerless = true"| sMax
    detect -->|"isServerless = false"| tMax
```

**Key Parameters:**
- **max**: Maximum pool connections (20 for traditional, 5 for serverless)
- **min**: Minimum idle connections (2 for traditional, 0 for serverless)
- **idleTimeoutMillis**: Close idle connections after 30 seconds
- **connectionTimeoutMillis**: Timeout when acquiring connection (5 seconds)
- **allowExitOnIdle**: Allow process exit when no connections (serverless only)

Sources: [services/db/src/connection.ts:77-88]()

### Singleton Pattern

The `getDb()` function provides a singleton database instance:

```mermaid
graph TB
    app1["Service A"]
    app2["Service B"]
    app3["Service C"]
    
    getDb["getDb()"]
    singleton["_db: Database | null"]
    createDb["createDb()"]
    
    app1 --> getDb
    app2 --> getDb
    app3 --> getDb
    
    getDb --> singleton
    singleton -->|"null"| createDb
    singleton -->|"exists"| return["Return existing instance"]
    
    createDb --> pool["Connection Pool"]
    pool --> dbInstance["Database instance"]
```

The singleton pattern ensures all parts of an application share the same connection pool, avoiding connection exhaustion.

Sources: [services/db/src/connection.ts:140-147]()

## Schema Organization

The Actionbook database schema is organized into several logical groups:

```mermaid
graph TB
    subgraph "Source Management"
        sources["sources<br/>Websites tracked"]
        sourceVersions["source_versions<br/>Version snapshots"]
    end
    
    subgraph "Documentation Data"
        documents["documents<br/>Crawled pages"]
        chunks["chunks<br/>Content segments<br/>+ embeddings"]
    end
    
    subgraph "Capability Data"
        pages["pages<br/>Page types/modules"]
        elements["elements<br/>UI components<br/>+ selectors"]
    end
    
    subgraph "Build Pipeline"
        buildTasks["build_tasks<br/>Pipeline tracking"]
        recordingTasks["recording_tasks<br/>Task execution"]
    end
    
    sources --> sourceVersions
    sources --> documents
    sources --> pages
    sources --> buildTasks
    
    sourceVersions --> chunks
    
    documents --> chunks
    
    pages --> elements
    
    buildTasks --> recordingTasks
    
    style sources fill:#f0f0f0
    style chunks fill:#f0f0f0
    style elements fill:#f0f0f0
```

Sources: [Diagram 5 from architecture overview]

### Key Tables Overview

| Table | Primary Purpose | Key Fields |
|-------|----------------|------------|
| `sources` | Website tracking | `id`, `name`, `base_url`, `active_version_id` |
| `source_versions` | Version snapshots | `id`, `source_id`, `version`, `status`, `published_at` |
| `documents` | Crawled pages | `id`, `source_id`, `url`, `title`, `content` |
| `chunks` | Content segments | `id`, `document_id`, `source_version_id`, `content`, `embedding` |
| `pages` | Page types | `id`, `source_id`, `url`, `module`, `capabilities` |
| `elements` | UI capabilities | `id`, `page_id`, `action`, `selectors`, `element_type` |
| `build_tasks` | Build orchestration | `id`, `source_id`, `stage`, `stage_status`, `heartbeat_at` |
| `recording_tasks` | Recording execution | `id`, `build_task_id`, `chunk_id`, `status`, `retry_count` |

For detailed schema definitions, see [Database Schema](#5.1).

## Version Management

Actionbook implements Blue-Green deployment through the version management system:

```mermaid
graph TB
    subgraph "Version Lifecycle"
        create["New Version Created<br/>status = 'pending'"]
        build["Build Process<br/>status = 'building'"]
        complete["Build Complete<br/>status = 'completed'"]
        publish["Publish Version<br/>status = 'published'"]
    end
    
    subgraph "Active Version Tracking"
        sources["sources.active_version_id"]
        oldVersion["Old Version<br/>(unpublished)"]
        newVersion["New Version<br/>(published)"]
    end
    
    subgraph "Data References"
        chunks["chunks.source_version_id"]
        elements["elements<br/>(via pages)"]
    end
    
    create --> build
    build --> complete
    complete --> publish
    
    publish --> sources
    sources --> newVersion
    sources -.->|"previously pointed to"| oldVersion
    
    newVersion --> chunks
    newVersion --> elements
```

**Key Concepts:**

- **source_versions**: Each build creates a new version record with a unique version number
- **active_version_id**: The `sources.active_version_id` field points to the currently published version
- **Publishing**: Atomically switches `active_version_id` to the new version, enabling zero-downtime deployments
- **Rollback**: Simply revert `active_version_id` to a previous version

This design allows multiple versions to coexist in the database while only one is active for API queries.

Sources: [Diagram 5 from architecture overview, section on version management]

## Dual Persistence Strategy

Actionbook maintains data in both PostgreSQL and YAML files:

```mermaid
graph TB
    subgraph "Recording Process"
        recorder["ActionRecorder"]
        tools["RecorderToolExecutor"]
    end
    
    subgraph "Database Persistence"
        saveElement["Save to elements table"]
        savePage["Save to pages table"]
        saveChunk["Update chunks table"]
    end
    
    subgraph "YAML Persistence"
        yamlGen["Generate YAML"]
        yamlPath["output/sites/{source_name}/{page_path}.yaml"]
    end
    
    subgraph "Query Paths"
        apiQuery["API Queries<br/>GET /actions/search"]
        fileRead["Direct File Access"]
    end
    
    recorder --> tools
    tools --> saveElement
    tools --> savePage
    tools --> saveChunk
    
    tools --> yamlGen
    yamlGen --> yamlPath
    
    saveElement --> apiQuery
    savePage --> apiQuery
    saveChunk --> apiQuery
    
    yamlPath --> fileRead
```

### YAML File Structure

YAML files are organized by website and page path:

```
output/
└── sites/
    └── example.com/
        ├── index.yaml
        ├── login.yaml
        ├── dashboard/
        │   └── index.yaml
        └── settings/
            └── profile.yaml
```

Each YAML file contains:
- Page metadata (URL, title, module)
- Element capabilities (actions, selectors, descriptions)
- Human-readable formatting for manual inspection

### Benefits of Dual Persistence

| Aspect | Database | YAML Files |
|--------|----------|------------|
| **Querying** | Fast structured queries, indexes | File system traversal |
| **Search** | Hybrid search (full-text + vector) | Text search tools (grep, ripgrep) |
| **Versioning** | Built-in with `source_versions` | Git-friendly text format |
| **Portability** | Requires database connection | Self-contained files |
| **Human Readability** | Raw SQL/JSON | Formatted, documented |
| **Use Case** | Production API, automated tools | Development, debugging, documentation |

Sources: [Diagram 5 from architecture overview, Diagram 1 showing dual persistence]

## Search Infrastructure

Actionbook implements hybrid search combining full-text and vector similarity:

```mermaid
graph TB
    subgraph "Query Input"
        userQuery["User Query:<br/>'login button'"]
        embedding["Generate Embedding<br/>OpenAI/etc."]
    end
    
    subgraph "Full-Text Search"
        ginIndex["GIN Index<br/>chunks_content_gin_idx"]
        tsVector["to_tsvector('english', content)"]
        ftResults["Full-Text Results<br/>+ ts_rank scores"]
    end
    
    subgraph "Vector Search"
        hnswIndex["HNSW Index<br/>chunks_embedding_hnsw_idx"]
        cosineDist["vector_cosine_ops"]
        vecResults["Vector Results<br/>+ cosine distance"]
    end
    
    subgraph "Result Fusion"
        combine["Combine Results"]
        rerank["Re-rank by Hybrid Score"]
        topK["Return Top-K Results"]
    end
    
    userQuery --> embedding
    userQuery --> tsVector
    
    tsVector --> ginIndex
    ginIndex --> ftResults
    
    embedding --> cosineDist
    cosineDist --> hnswIndex
    hnswIndex --> vecResults
    
    ftResults --> combine
    vecResults --> combine
    combine --> rerank
    rerank --> topK
```

### Index Types

**GIN Index (Generalized Inverted Index)** - Full-Text Search
- Index name: `chunks_content_gin_idx`
- Accelerates `to_tsvector('english', content)` queries
- Improves full-text search from ~2s to ~200ms
- Partial index `chunks_content_gin_active_idx` for active versions only

**HNSW Index (Hierarchical Navigable Small World)** - Vector Similarity
- Index name: `chunks_embedding_hnsw_idx`
- Uses cosine distance (`vector_cosine_ops`)
- Parameters: `m=16`, `ef_construction=64`
- Enables fast approximate nearest neighbor search

Sources: [services/db/migrations/0020_add_chunks_fulltext_index.sql:1-19](), [services/db/migrations/0019_add_vector_indexes.sql:1-22]()

### Index Configuration

```mermaid
graph TB
    subgraph "Full-Text Indexes"
        gin1["chunks_content_gin_idx<br/>All chunks"]
        gin2["chunks_content_gin_active_idx<br/>Active versions only"]
    end
    
    subgraph "Vector Indexes"
        hnsw["chunks_embedding_hnsw_idx<br/>m=16, ef_construction=64"]
    end
    
    subgraph "Supporting Indexes"
        docIdx["chunks_document_id_idx<br/>JOIN optimization"]
        verIdx["chunks_source_version_id_idx<br/>Version filtering"]
        compIdx["chunks_version_embedding_idx<br/>Composite filter"]
    end
    
    chunks["chunks table"]
    
    chunks --> gin1
    chunks --> gin2
    chunks --> hnsw
    chunks --> docIdx
    chunks --> verIdx
    chunks --> compIdx
```

**Index Purposes:**

| Index | Purpose | Query Pattern |
|-------|---------|---------------|
| `chunks_content_gin_idx` | Full-text search on all chunks | `to_tsvector('english', content)` |
| `chunks_content_gin_active_idx` | Full-text search on active versions | Same, with `source_version_id IS NOT NULL` |
| `chunks_embedding_hnsw_idx` | Vector similarity search | `ORDER BY embedding <=> query_vector` |
| `chunks_document_id_idx` | JOIN with documents table | `JOIN documents ON chunks.document_id = documents.id` |
| `chunks_source_version_id_idx` | Filter by version | `WHERE source_version_id = ?` |
| `chunks_version_embedding_idx` | Combined version + embedding filter | `WHERE source_version_id = ? AND embedding IS NOT NULL` |

Sources: [services/db/migrations/0020_add_chunks_fulltext_index.sql:1-19](), [services/db/migrations/0019_add_vector_indexes.sql:1-22]()

### Hybrid Search Implementation

The API implements hybrid search by:

1. Executing full-text search with `ts_rank` scoring
2. Executing vector similarity search with cosine distance
3. Normalizing scores from both methods
4. Combining results with configurable weights
5. Re-ranking and returning top-K results

For implementation details, see [Search and Indexing](#5.3).

Sources: [Diagram 5 from architecture overview]

## Data Flow Summary

```mermaid
graph LR
    subgraph "Input Sources"
        crawler["Web Crawler"]
        recorder["Action Recorder"]
        embedder["Embedding Generator"]
    end
    
    subgraph "Database Tables"
        documents["documents"]
        chunks["chunks"]
        pages["pages"]
        elements["elements"]
    end
    
    subgraph "Indexes"
        ginIdx["GIN<br/>Full-text"]
        hnswIdx["HNSW<br/>Vector"]
    end
    
    subgraph "Output"
        api["API Endpoints"]
        yaml["YAML Files"]
    end
    
    crawler --> documents
    crawler --> chunks
    
    recorder --> pages
    recorder --> elements
    recorder --> yaml
    
    embedder --> chunks
    
    chunks --> ginIdx
    chunks --> hnswIdx
    
    ginIdx --> api
    hnswIdx --> api
    elements --> api
```

**Data Flow:**

1. **Web Crawler** (Playbook Builder) discovers pages and generates documentation content
2. **Content** is stored in `documents` and segmented into `chunks`
3. **Embedding Generator** produces vector embeddings for each chunk
4. **Action Recorder** discovers UI capabilities and stores them in `pages` and `elements`
5. **Indexes** (GIN and HNSW) are automatically maintained for fast search
6. **API Endpoints** query indexed data to serve search requests
7. **YAML Files** are generated alongside database records for portability

Sources: [Diagram 5 from architecture overview, Diagram 3 showing build pipeline data flow]

---

# Page: Database Schema

# Database Schema

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [services/action-builder/src/task-worker/build-task-runner.ts](services/action-builder/src/task-worker/build-task-runner.ts)
- [services/action-builder/src/task-worker/coordinator.ts](services/action-builder/src/task-worker/coordinator.ts)
- [services/action-builder/src/task-worker/recording-task-queue-worker.ts](services/action-builder/src/task-worker/recording-task-queue-worker.ts)
- [services/action-builder/test/coordinator.integration.it.test.ts](services/action-builder/test/coordinator.integration.it.test.ts)
- [services/action-builder/test/task-worker/integration/end-to-end.it.test.ts](services/action-builder/test/task-worker/integration/end-to-end.it.test.ts)
- [services/db/migrations/0019_add_vector_indexes.sql](services/db/migrations/0019_add_vector_indexes.sql)
- [services/db/migrations/0020_add_chunks_fulltext_index.sql](services/db/migrations/0020_add_chunks_fulltext_index.sql)

</details>



## Purpose and Scope

This document provides a complete reference for the Actionbook PostgreSQL database schema, including all tables, their relationships, key fields, indexes, and data lifecycle patterns. The schema supports both the knowledge building pipeline (crawling and documentation) and the action building pipeline (UI element discovery and recording).

For information about database connection management and pooling strategies, see [Database Connection Management](#5.2). For details on search implementation using these indexes, see [Search and Indexing](#5.3).

---

## Schema Overview

The Actionbook database organizes data into four functional groups: source management, content storage, UI discovery, and build pipeline tracking.

**Schema Organization Diagram**

```mermaid
graph TB
    subgraph "Source Management"
        sources["sources<br/>Website definitions"]
        sourceVersions["source_versions<br/>Blue-Green versioning"]
    end
    
    subgraph "Content Storage"
        documents["documents<br/>Crawled pages"]
        chunks["chunks<br/>Content segments<br/>+ embeddings"]
    end
    
    subgraph "UI Discovery"
        pages["pages<br/>Page types"]
        elements["elements<br/>UI components<br/>+ selectors"]
    end
    
    subgraph "Build Pipeline"
        buildTasks["build_tasks<br/>Build orchestration"]
        recordingTasks["recording_tasks<br/>Recording execution"]
    end
    
    sources --> sourceVersions
    sources --> documents
    sources --> pages
    sources --> buildTasks
    
    sourceVersions --> chunks
    documents --> chunks
    
    pages --> elements
    
    buildTasks --> recordingTasks
    buildTasks --> sourceVersions
    
    recordingTasks -.-> chunks
```

Sources: [services/action-builder/src/task-worker/build-task-runner.ts:19](), [services/db/migrations/0019_add_vector_indexes.sql:1-22](), [services/db/migrations/0020_add_chunks_fulltext_index.sql:1-19]()

---

## Core Tables

### Source Management Tables

#### `sources` Table

The `sources` table stores website definitions and serves as the root entity for all related data.

| Field | Type | Description |
|-------|------|-------------|
| `id` | `serial PRIMARY KEY` | Unique source identifier |
| `name` | `text NOT NULL` | Human-readable name |
| `base_url` | `text NOT NULL` | Root URL of the website |
| `domain` | `text NOT NULL` | Domain name for grouping |
| `description` | `text` | Optional description |
| `category` | `text` | Site category (e.g., 'help', 'docs') |
| `crawl_config` | `jsonb` | Crawler configuration |
| `created_at` | `timestamp` | Creation timestamp |
| `updated_at` | `timestamp` | Last update timestamp |

#### `source_versions` Table

The `source_versions` table implements Blue-Green deployment by maintaining multiple versions of source data.

| Field | Type | Description |
|-------|------|-------------|
| `id` | `serial PRIMARY KEY` | Version identifier |
| `source_id` | `integer REFERENCES sources(id)` | Parent source |
| `version_number` | `integer NOT NULL` | Monotonically increasing version |
| `status` | `text NOT NULL` | `building`, `active`, or `archived` |
| `commit_message` | `text` | Version description |
| `published_at` | `timestamp` | Activation timestamp |
| `created_at` | `timestamp` | Creation timestamp |

**Version Status Lifecycle:**
- `building` → Version being constructed by build pipeline
- `active` → Currently served version (only one per source)
- `archived` → Previously active version

Sources: [services/action-builder/src/task-worker/build-task-runner.ts:394-459]()

---

### Content Storage Tables

#### `documents` Table

The `documents` table stores crawled web pages with their metadata.

| Field | Type | Description |
|-------|------|-------------|
| `id` | `serial PRIMARY KEY` | Document identifier |
| `source_id` | `integer REFERENCES sources(id)` | Parent source |
| `source_version_id` | `integer REFERENCES source_versions(id)` | Associated version |
| `url` | `text NOT NULL` | Page URL |
| `url_hash` | `text NOT NULL` | Hash for deduplication |
| `title` | `text` | Page title |
| `content_text` | `text` | Extracted text content |
| `content_html` | `text` | Raw HTML content |
| `metadata` | `jsonb` | Additional page metadata |
| `created_at` | `timestamp` | Crawl timestamp |

#### `chunks` Table

The `chunks` table segments documents into searchable pieces with embeddings for vector similarity search.

| Field | Type | Description |
|-------|------|-------------|
| `id` | `serial PRIMARY KEY` | Chunk identifier |
| `document_id` | `integer REFERENCES documents(id)` | Parent document |
| `source_version_id` | `integer REFERENCES source_versions(id)` | Version association |
| `content` | `text NOT NULL` | Chunk text content |
| `content_hash` | `text NOT NULL` | Hash for deduplication |
| `chunk_index` | `integer NOT NULL` | Position within document |
| `start_char` | `integer` | Starting character offset |
| `end_char` | `integer` | Ending character offset |
| `token_count` | `integer` | Approximate token count |
| `embedding` | `vector(1536)` | OpenAI embedding vector |
| `metadata` | `jsonb` | Additional chunk metadata |
| `created_at` | `timestamp` | Creation timestamp |

**Key Indexes:**
- `chunks_content_gin_idx`: GIN index on `to_tsvector('english', content)` for full-text search
- `chunks_embedding_hnsw_idx`: HNSW index on `embedding` for vector similarity (cosine distance)
- `chunks_document_id_idx`: B-tree index for document joins
- `chunks_source_version_id_idx`: B-tree index for version filtering

Sources: [services/db/migrations/0019_add_vector_indexes.sql:1-22](), [services/db/migrations/0020_add_chunks_fulltext_index.sql:1-19](), [services/action-builder/src/task-worker/build-task-runner.ts:156-170]()

---

### UI Discovery Tables

#### `pages` Table

The `pages` table represents discovered page types with their capabilities.

| Field | Type | Description |
|-------|------|-------------|
| `id` | `serial PRIMARY KEY` | Page identifier |
| `source_id` | `integer REFERENCES sources(id)` | Parent source |
| `page_key` | `text NOT NULL` | Unique page identifier |
| `page_name` | `text NOT NULL` | Human-readable name |
| `url_pattern` | `text` | URL matching pattern |
| `description` | `text` | Page purpose description |
| `module` | `text` | Functional module grouping |
| `metadata` | `jsonb` | Additional page metadata |
| `created_at` | `timestamp` | Discovery timestamp |
| `updated_at` | `timestamp` | Last update timestamp |

#### `elements` Table

The `elements` table stores discovered UI components with verified selectors.

| Field | Type | Description |
|-------|------|-------------|
| `id` | `serial PRIMARY KEY` | Element identifier |
| `page_id` | `integer REFERENCES pages(id)` | Parent page |
| `element_key` | `text NOT NULL` | Unique element identifier |
| `element_type` | `text NOT NULL` | Type: `button`, `input`, `link`, etc. |
| `description` | `text` | Element purpose |
| `selectors` | `jsonb NOT NULL` | Array of selector objects |
| `allow_method` | `text` | Allowed interaction: `click`, `fill`, `navigate` |
| `required_context` | `jsonb` | Prerequisites for interaction |
| `validation_rules` | `jsonb` | Input validation rules |
| `metadata` | `jsonb` | Additional element metadata |
| `confidence` | `numeric` | Selector confidence score (0-100) |
| `last_verified_at` | `timestamp` | Last verification timestamp |
| `created_at` | `timestamp` | Discovery timestamp |
| `updated_at` | `timestamp` | Last update timestamp |

**Selector Structure** (stored in `selectors` JSONB field):
```json
[
  {
    "type": "css",
    "value": "#submit-button",
    "confidence": 95,
    "priority": 1
  },
  {
    "type": "xpath",
    "value": "//button[@id='submit-button']",
    "confidence": 90,
    "priority": 2
  }
]
```

For detailed information on selector types and structure, see [Selector Types](#7.2).

Sources: [services/action-builder/src/task-worker/build-task-runner.ts:1-493]()

---

### Build Pipeline Tables

#### `build_tasks` Table

The `build_tasks` table tracks the lifecycle of build pipeline executions.

| Field | Type | Description |
|-------|------|-------------|
| `id` | `serial PRIMARY KEY` | Build task identifier |
| `source_id` | `integer REFERENCES sources(id)` | Target source |
| `source_version_id` | `integer REFERENCES source_versions(id)` | Target version |
| `source_url` | `text NOT NULL` | Source URL |
| `source_name` | `text NOT NULL` | Source name |
| `source_category` | `text` | Source category |
| `stage` | `text NOT NULL` | Current stage (see below) |
| `stage_status` | `text NOT NULL` | Stage status (see below) |
| `config` | `jsonb` | Build configuration |
| `knowledge_started_at` | `timestamp` | Knowledge build start |
| `knowledge_completed_at` | `timestamp` | Knowledge build end |
| `action_started_at` | `timestamp` | Action build start |
| `action_completed_at` | `timestamp` | Action build end |
| `created_at` | `timestamp` | Creation timestamp |
| `updated_at` | `timestamp` | Last heartbeat timestamp |

**Build Stages:**
- `init` → Initial creation
- `knowledge_build` → Crawling and documentation phase
- `action_build` → UI element discovery phase

**Stage Status Values:**
- `pending` → Waiting to start
- `running` → Currently executing
- `completed` → Finished successfully
- `error` → Failed with error

Sources: [services/action-builder/src/task-worker/build-task-runner.ts:119-148](), [services/action-builder/src/task-worker/coordinator.ts:163-206]()

#### `recording_tasks` Table

The `recording_tasks` table manages individual recording task executions within a build.

| Field | Type | Description |
|-------|------|-------------|
| `id` | `serial PRIMARY KEY` | Recording task identifier |
| `source_id` | `integer REFERENCES sources(id)` | Parent source |
| `build_task_id` | `integer REFERENCES build_tasks(id)` | Parent build task |
| `chunk_id` | `integer REFERENCES chunks(id)` | Target chunk |
| `start_url` | `text NOT NULL` | Starting URL for recording |
| `status` | `text NOT NULL` | Task status (see below) |
| `progress` | `integer DEFAULT 0` | Completion percentage (0-100) |
| `attempt_count` | `integer DEFAULT 0` | Execution attempt count |
| `config` | `jsonb` | Task configuration |
| `error_message` | `text` | Failure error message |
| `started_at` | `timestamp` | Execution start time |
| `completed_at` | `timestamp` | Execution end time |
| `last_heartbeat` | `timestamp` | Last heartbeat for stale detection |
| `duration_ms` | `integer` | Total execution time |
| `tokens_used` | `integer` | LLM tokens consumed |
| `created_at` | `timestamp` | Creation timestamp |
| `updated_at` | `timestamp` | Last update timestamp |

**Task Status Values:**
- `pending` → Waiting for execution
- `running` → Currently executing
- `completed` → Finished successfully
- `failed` → Failed (may retry if `attempt_count` < max)

**Unique Constraint:** `(chunk_id, build_task_id)` prevents duplicate tasks

Sources: [services/action-builder/src/task-worker/recording-task-queue-worker.ts:201-244](), [services/action-builder/src/task-worker/build-task-runner.ts:154-226]()

---

## Entity Relationship Diagram

**Complete Database Relationships**

```mermaid
erDiagram
    sources ||--o{ source_versions : "has versions"
    sources ||--o{ documents : "contains"
    sources ||--o{ pages : "has pages"
    sources ||--o{ build_tasks : "tracks builds"
    
    source_versions ||--o{ chunks : "version of"
    source_versions ||--o| build_tasks : "built by"
    
    documents ||--o{ chunks : "split into"
    
    pages ||--o{ elements : "contains"
    
    build_tasks ||--o{ recording_tasks : "generates"
    recording_tasks }o--|| chunks : "targets"
    
    sources {
        serial id PK
        text name
        text base_url
        text domain
        jsonb crawl_config
    }
    
    source_versions {
        serial id PK
        integer source_id FK
        integer version_number
        text status
        timestamp published_at
    }
    
    documents {
        serial id PK
        integer source_id FK
        integer source_version_id FK
        text url
        text content_text
    }
    
    chunks {
        serial id PK
        integer document_id FK
        integer source_version_id FK
        text content
        vector_1536 embedding
    }
    
    pages {
        serial id PK
        integer source_id FK
        text page_key
        text page_name
        text url_pattern
    }
    
    elements {
        serial id PK
        integer page_id FK
        text element_key
        text element_type
        jsonb selectors
        text allow_method
    }
    
    build_tasks {
        serial id PK
        integer source_id FK
        integer source_version_id FK
        text stage
        text stage_status
        jsonb config
    }
    
    recording_tasks {
        serial id PK
        integer source_id FK
        integer build_task_id FK
        integer chunk_id FK
        text status
        integer attempt_count
        timestamp last_heartbeat
    }
```

Sources: [services/action-builder/src/task-worker/build-task-runner.ts:17-19](), [services/action-builder/src/task-worker/coordinator.ts:11-12]()

---

## Task Lifecycle and Status Transitions

**Build Task State Machine**

```mermaid
stateDiagram-v2
    [*] --> init : "Create build_task"
    
    init --> knowledge_build_running : "Start crawling"
    knowledge_build_running --> knowledge_build_completed : "Crawl finished"
    knowledge_build_running --> knowledge_build_error : "Crawl failed"
    
    knowledge_build_completed --> action_build_running : "Coordinator claims"
    action_build_running --> action_build_completed : "All tasks done"
    action_build_running --> action_build_error : "Build failed"
    
    action_build_completed --> [*] : "Publish version"
    
    note right of action_build_running
        BuildTaskRunner:
        - Generates recording_tasks
        - Polls task status
        - Retries failed tasks
        - Updates heartbeat
    end note
```

Sources: [services/action-builder/src/task-worker/coordinator.ts:163-206](), [services/action-builder/src/task-worker/build-task-runner.ts:59-114]()

**Recording Task State Machine**

```mermaid
stateDiagram-v2
    [*] --> pending : "BuildTaskRunner generates"
    
    pending --> running : "QueueWorker claims<br/>(FOR UPDATE SKIP LOCKED)"
    
    running --> completed : "Execution successful"
    running --> failed : "Execution failed"
    
    failed --> pending : "Retry (attemptCount < maxAttempts)"
    failed --> [*] : "Max attempts reached"
    
    running --> pending : "Stale recovery<br/>(heartbeat timeout)"
    
    completed --> [*]
    
    note right of running
        QueueWorker:
        - Updates heartbeat every 5s
        - Stale timeout: 15 minutes
        - Max attempts: 3
    end note
```

Sources: [services/action-builder/src/task-worker/recording-task-queue-worker.ts:201-244](), [services/action-builder/src/task-worker/recording-task-queue-worker.ts:304-352](), [services/action-builder/src/task-worker/build-task-runner.ts:298-336]()

---

## Recording Task Configuration

The `recording_tasks.config` JSONB field stores task-specific configuration:

| Field | Type | Description |
|-------|------|-------------|
| `chunk_type` | `string` | `task_driven` or `exploratory` |
| `actionBuilderPrompt` | `string` | Optional custom prompt override |

**Task Type Differences:**
- `task_driven`: Follows specific task instructions from chunk content
- `exploratory`: General page exploration and element discovery

Sources: [services/action-builder/src/task-worker/build-task-runner.ts:178-191](), [services/action-builder/test/task-worker/integration/end-to-end.it.test.ts:133-142]()

---

## Blue-Green Version Management

**Version Publishing Flow**

```mermaid
sequenceDiagram
    participant BTR as "BuildTaskRunner"
    participant DB as "Database"
    
    Note over BTR,DB: Build completes successfully
    
    BTR->>DB: SELECT source_versions<br/>WHERE source_id AND status='active'
    DB-->>BTR: Current active version (if any)
    
    BTR->>DB: UPDATE source_versions<br/>SET status='archived'<br/>WHERE id=current_active_id
    Note over DB: Old version archived
    
    BTR->>DB: UPDATE source_versions<br/>SET status='active', published_at=NOW()<br/>WHERE id=new_version_id
    Note over DB: New version activated
    
    Note over BTR,DB: Blue-Green swap complete
```

**Version Status Flow:**
1. `building` → New version created by build pipeline
2. `building` → `active` → Version published, becomes current
3. `active` → `archived` → Previous version superseded
4. Only one `active` version per source at any time

Sources: [services/action-builder/src/task-worker/build-task-runner.ts:394-459]()

---

## Concurrency and Safety Mechanisms

### Atomic Task Claiming

Both `Coordinator` (for `build_tasks`) and `RecordingTaskQueueWorker` (for `recording_tasks`) use PostgreSQL's `FOR UPDATE SKIP LOCKED` to prevent duplicate execution:

```sql
UPDATE build_tasks
SET stage = 'action_build', stage_status = 'running', updated_at = NOW()
WHERE id = (
  SELECT id FROM build_tasks
  WHERE stage = 'knowledge_build' AND stage_status = 'completed'
  ORDER BY id
  LIMIT 1
  FOR UPDATE SKIP LOCKED
)
RETURNING id
```

This ensures:
- Only one worker claims each task
- No blocking on locked rows
- Race-condition-free concurrent execution

Sources: [services/action-builder/src/task-worker/coordinator.ts:163-206](), [services/action-builder/src/task-worker/recording-task-queue-worker.ts:201-244]()

### Heartbeat Monitoring

Tasks track liveness via `last_heartbeat` field:
- **BuildTaskRunner**: Updates `build_tasks.updated_at` every 5 seconds
- **TaskExecutor**: Updates `recording_tasks.last_heartbeat` every 5 seconds
- **Stale Detection**: Tasks with heartbeat older than 15 minutes are recovered

Sources: [services/action-builder/src/task-worker/build-task-runner.ts:341-372](), [services/action-builder/src/task-worker/recording-task-queue-worker.ts:287-298](), [services/action-builder/src/task-worker/recording-task-queue-worker.ts:304-352]()

### Idempotent Task Generation

`BuildTaskRunner` uses `ON CONFLICT DO UPDATE` for idempotent recording task generation:

```sql
INSERT INTO recording_tasks (source_id, build_task_id, chunk_id, ...)
VALUES (...)
ON CONFLICT (chunk_id, build_task_id)
DO UPDATE SET
  status = CASE
    WHEN recording_tasks.status IN ('pending', 'running') THEN 'pending'
    ELSE recording_tasks.status
  END
```

This allows crash recovery without duplicating completed tasks.

Sources: [services/action-builder/src/task-worker/build-task-runner.ts:195-226]()

---

## Composite Indexes for Query Performance

The schema includes several composite indexes optimized for common query patterns:

### Full-Text Search Indexes

| Index Name | Type | Definition | Purpose |
|------------|------|------------|---------|
| `chunks_content_gin_idx` | GIN | `to_tsvector('english', content)` | Full-text search on chunk content |
| `chunks_content_gin_active_idx` | Partial GIN | `to_tsvector('english', content) WHERE source_version_id IS NOT NULL` | Optimized for active versions only |

### Vector Similarity Indexes

| Index Name | Type | Definition | Purpose |
|------------|------|------------|---------|
| `chunks_embedding_hnsw_idx` | HNSW | `embedding vector_cosine_ops (m=16, ef_construction=64)` | Approximate nearest neighbor search |
| `chunks_version_embedding_idx` | B-tree | `source_version_id WHERE embedding IS NOT NULL` | Filtered vector search |

### Relationship Indexes

| Index Name | Type | Definition | Purpose |
|------------|------|------------|---------|
| `chunks_document_id_idx` | B-tree | `document_id` | Document-to-chunks joins |
| `chunks_source_version_id_idx` | B-tree | `source_version_id` | Version-filtered queries |

Sources: [services/db/migrations/0019_add_vector_indexes.sql:1-22](), [services/db/migrations/0020_add_chunks_fulltext_index.sql:1-19]()

---

## Integration Test Coverage

The database schema is validated by comprehensive integration tests:

| Test | Coverage | Location |
|------|----------|----------|
| IT-01 | Multiple concurrent build_tasks (3 × 5 recording_tasks) | [coordinator.integration.it.test.ts:100-196]() |
| IT-02 | Task failure and automatic retry logic | [coordinator.integration.it.test.ts:198-296]() |
| IT-03 | Stale task recovery after simulated crash | [coordinator.integration.it.test.ts:298-404]() |
| IT-04 | Multi-worker concurrency safety (3 workers, 10 tasks) | [coordinator.integration.it.test.ts:406-508]() |
| IT-301 | End-to-end pipeline (TaskGenerator → TaskExecutor) | [end-to-end.it.test.ts:57-150]() |

Sources: [services/action-builder/test/coordinator.integration.it.test.ts:1-509](), [services/action-builder/test/task-worker/integration/end-to-end.it.test.ts:1-223]()

---

# Page: Database Connection Management

# Database Connection Management

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [services/db/src/connection.ts](services/db/src/connection.ts)

</details>



## Purpose and Scope

This document describes how Actionbook manages PostgreSQL database connections across different runtime environments. The system uses a dual-driver strategy to support both traditional Node.js environments (using `node-postgres`) and serverless platforms (using Neon's WebSocket-based driver). Topics covered include driver selection logic, connection pooling configurations, and the singleton pattern used for database access.

For details on the database schema and tables, see [Database Schema](#5.1). For information on search and indexing implementation, see [Search and Indexing](#5.3).

---

## Driver Selection Strategy

The system automatically selects between two PostgreSQL drivers based on the runtime environment:

- **node-postgres (`pg`)**: Used for local development, AgentCore runtime, and non-Vercel production environments
- **Neon serverless**: Used exclusively for Vercel deployments (edge/serverless functions with WebSocket support)

### Environment Detection Logic

The driver selection is determined by the `shouldUsePgDriver()` function, which evaluates environment variables in the following order:

```mermaid
graph TD
    Start["shouldUsePgDriver()"] --> CheckEnv["Check NODE_ENV"]
    CheckEnv -->|"!== 'production'"| UsePg["Return true<br/>(Use pg driver)"]
    CheckEnv -->|"=== 'production'"| CheckAgentCore["Check AWS_AGENTCORE_RUNTIME"]
    CheckAgentCore -->|"=== 'true'"| UsePg
    CheckAgentCore -->|"!== 'true'"| CheckVercel["Check VERCEL"]
    CheckVercel -->|"Not set"| UsePg
    CheckVercel -->|"Set"| UseNeon["Return false<br/>(Use Neon driver)"]
    
    UsePg --> PgDriver["node-postgres<br/>TCP connection"]
    UseNeon --> NeonDriver["@neondatabase/serverless<br/>WebSocket connection"]
```

**Sources:** [services/db/src/connection.ts:25-40]()

| Environment | `NODE_ENV` | `AWS_AGENTCORE_RUNTIME` | `VERCEL` | Driver Selected |
|-------------|------------|-------------------------|----------|-----------------|
| Local development | `!== 'production'` | N/A | N/A | `pg` (node-postgres) |
| AgentCore (AWS) | `production` | `'true'` | N/A | `pg` (node-postgres) |
| Vercel | `production` | N/A | Set | Neon serverless |
| Other production | `production` | N/A | Not set | `pg` (node-postgres) |

The rationale for this strategy:
- **AgentCore runtime** requires TCP connections because it runs in a Node.js environment without native WebSocket support
- **Vercel** requires WebSocket-based connections for edge and serverless functions
- **Local development** uses standard TCP for simplicity and compatibility with local PostgreSQL instances

**Sources:** [services/db/src/connection.ts:18-40]()

---

## Database Type Unification

Both drivers return compatible types through a unified `Database` type definition:

```typescript
export type Database = NodePgDatabase<typeof schema>;
```

This type alias allows the codebase to use a single interface regardless of the underlying driver. The Neon serverless driver's return type is cast to match:

```typescript
const db = drizzleNeon(pool, { schema }) as unknown as Database;
```

This ensures that all database operations use the same TypeScript types and Drizzle ORM methods, regardless of whether the connection uses TCP (node-postgres) or WebSocket (Neon).

**Sources:** [services/db/src/connection.ts:11](), [services/db/src/connection.ts:116]()

---

## Connection Creation

The `createDb()` function serves as the main entry point for establishing database connections:

```mermaid
graph TD
    CreateDb["createDb(databaseUrl?)"] --> GetUrl["Get database URL:<br/>1. databaseUrl param<br/>2. POSTGRES_URL env<br/>3. DATABASE_URL env"]
    GetUrl --> ValidateUrl{URL exists?}
    ValidateUrl -->|No| ThrowError["Throw Error:<br/>'Database URL not found'"]
    ValidateUrl -->|Yes| CheckDriver["shouldUsePgDriver()"]
    
    CheckDriver -->|true| CreatePg["createPgDb(url)"]
    CheckDriver -->|false| CreateNeon["createNeonDb(url)"]
    
    CreatePg --> PgPool["new Pool()<br/>from 'pg'"]
    CreateNeon --> NeonPool["new NeonPool()<br/>from '@neondatabase/serverless'"]
    
    PgPool --> DrizzlePg["drizzlePg(pool, {schema})"]
    NeonPool --> DrizzleNeon["drizzleNeon(pool, {schema})"]
    
    DrizzlePg --> StorePool["poolMap.set(db, pool)"]
    DrizzleNeon --> StorePool
    
    StorePool --> ReturnDb["Return Database instance"]
```

**Sources:** [services/db/src/connection.ts:49-64]()

### Node-Postgres Connection (`createPgDb`)

For traditional environments, the `createPgDb()` function creates a connection using the `pg` driver:

```mermaid
graph LR
    CreatePgDb["createPgDb(url)"] --> DetectSsl["Detect SSL requirement:<br/>!localhost OR<br/>url contains 'sslmode='"]
    DetectSsl --> DetectEnv["Detect serverless:<br/>VERCEL OR<br/>AWS_LAMBDA_FUNCTION_NAME"]
    DetectEnv --> CreatePool["new Pool({<br/>connectionString,<br/>ssl,<br/>max, min,<br/>idleTimeoutMillis,<br/>connectionTimeoutMillis,<br/>allowExitOnIdle<br/>})"]
    CreatePool --> ErrorHandler["pool.on('error', handler)"]
    ErrorHandler --> Drizzle["drizzlePg(pool, {schema})"]
    Drizzle --> Track["poolMap.set(db, pool)"]
```

**Sources:** [services/db/src/connection.ts:70-99]()

### Neon Serverless Connection (`createNeonDb`)

For Vercel deployments, the `createNeonDb()` function creates a WebSocket-based connection:

```mermaid
graph LR
    CreateNeonDb["createNeonDb(url)"] --> CreateNeonPool["new NeonPool({<br/>connectionString<br/>})"]
    CreateNeonPool --> ErrorHandler["pool.on('error', handler)"]
    ErrorHandler --> Drizzle["drizzleNeon(pool, {schema})"]
    Drizzle --> Cast["Cast to Database type"]
    Cast --> Track["poolMap.set(db, pool)"]
```

**Sources:** [services/db/src/connection.ts:106-119]()

---

## Connection Pooling Strategies

The system uses different pooling configurations based on the deployment environment to optimize resource usage:

### Pooling Parameters

| Parameter | Traditional Environment | Serverless Environment | Purpose |
|-----------|------------------------|------------------------|---------|
| `max` | 20 | 5 | Maximum number of connections in the pool |
| `min` | 2 | 0 | Minimum number of idle connections maintained |
| `idleTimeoutMillis` | 30000 | 30000 | Time before idle connections are closed (30 seconds) |
| `connectionTimeoutMillis` | 5000 | 5000 | Timeout when acquiring a connection (5 seconds) |
| `allowExitOnIdle` | false | true | Allow process to exit when all connections are idle |

**Sources:** [services/db/src/connection.ts:79-88]()

### Serverless Optimization

Serverless environments (Vercel, AWS Lambda) use more aggressive pooling settings:
- **Lower `max` (5)**: Reduces total connections since functions scale horizontally
- **Zero `min`**: Avoids maintaining idle connections that consume resources
- **`allowExitOnIdle: true`**: Allows the function to terminate when no work is pending

Traditional environments use higher limits:
- **Higher `max` (20)**: Supports more concurrent operations in long-running processes
- **Non-zero `min` (2)**: Keeps connections warm for better latency

```mermaid
graph TB
    subgraph "Traditional Environment"
        T1["Pool Config"]
        T2["max: 20<br/>min: 2<br/>allowExitOnIdle: false"]
        T3["Maintains 2+ connections<br/>at all times"]
        T1 --> T2 --> T3
    end
    
    subgraph "Serverless Environment"
        S1["Pool Config"]
        S2["max: 5<br/>min: 0<br/>allowExitOnIdle: true"]
        S3["No idle connections<br/>Process can terminate"]
        S1 --> S2 --> S3
    end
```

**Sources:** [services/db/src/connection.ts:76-88]()

### SSL Configuration

SSL is automatically enabled for non-localhost connections or when the URL contains `sslmode=`:

```mermaid
graph LR
    CheckUrl["Check URL"] --> IsLocalhost{"Contains localhost<br/>OR 127.0.0.1?"}
    IsLocalhost -->|Yes| CheckParam{"Contains<br/>'sslmode='?"}
    IsLocalhost -->|No| EnableSSL["ssl: {<br/>rejectUnauthorized: false<br/>}"]
    CheckParam -->|Yes| EnableSSL
    CheckParam -->|No| DisableSSL["ssl: false"]
```

**Sources:** [services/db/src/connection.ts:71-81]()

### Error Handling

Both drivers attach error handlers to prevent unhandled error events from crashing the process:

```typescript
pool.on('error', (err) => {
  console.error('[Database Pool Error]', err.message);
  // Don't throw - let individual query errors be handled by their callers
});
```

This pattern ensures that pool-level errors (e.g., network disconnections) are logged but don't terminate the application. Query-specific errors are still propagated to the calling code.

**Sources:** [services/db/src/connection.ts:91-94](), [services/db/src/connection.ts:110-113]()

---

## Singleton Pattern

The database connection is managed through a singleton pattern implemented by the `getDb()` function:

```mermaid
graph TD
    Call["getDb()"] --> CheckInstance{"_db exists?"}
    CheckInstance -->|No| CreateNew["_db = createDb()"]
    CheckInstance -->|Yes| ReturnExisting["Return _db"]
    CreateNew --> ReturnNew["Return _db"]
    
    subgraph "Lifecycle Management"
        CloseDb["closeDb(db)"] --> CheckMatch{"db === _db?"}
        CheckMatch -->|Yes| ClearGlobal["_db = null"]
        CheckMatch -->|No| Skip["Skip clearing"]
    end
```

**Sources:** [services/db/src/connection.ts:140-147](), [services/db/src/connection.ts:131-133]()

### Usage Pattern

The singleton is the recommended pattern for most services:

```typescript
import { getDb } from '@actionbookdev/db';

// Lazy initialization on first access
const db = getDb();
```

For scenarios requiring explicit connection management (e.g., testing, multiple databases), use `createDb()` directly:

```typescript
import { createDb, closeDb } from '@actionbookdev/db';

const db = createDb(customUrl);
try {
  // Use database
} finally {
  await closeDb(db);
}
```

**Sources:** [services/db/src/connection.ts:49-64](), [services/db/src/connection.ts:124-134]()

---

## Connection Lifecycle Management

### Pool Tracking

The system uses a `WeakMap` to associate each `Database` instance with its underlying connection pool:

```typescript
const poolMap = new WeakMap<Database, Pool | NeonPool>();
```

This allows the `closeDb()` function to access the correct pool for cleanup, while automatically allowing garbage collection when database instances are no longer referenced.

**Sources:** [services/db/src/connection.ts:14](), [services/db/src/connection.ts:97](), [services/db/src/connection.ts:117]()

### Cleanup Process

The `closeDb()` function performs proper cleanup:

```mermaid
graph TD
    CloseDb["closeDb(db)"] --> GetPool["poolMap.get(db)"]
    GetPool --> PoolExists{Pool exists?}
    PoolExists -->|Yes| EndPool["await pool.end()"]
    PoolExists -->|No| CheckGlobal
    EndPool --> DeleteEntry["poolMap.delete(db)"]
    DeleteEntry --> CheckGlobal["db === _db?"]
    CheckGlobal -->|Yes| ClearGlobal["_db = null"]
    CheckGlobal -->|No| Complete["Complete"]
    ClearGlobal --> Complete
```

**Sources:** [services/db/src/connection.ts:124-134]()

The cleanup process:
1. Retrieves the pool from `poolMap` using the `Database` instance
2. Calls `pool.end()` to close all connections in the pool
3. Removes the entry from `poolMap`
4. Clears the global singleton if the closed database matches `_db`

This ensures proper resource cleanup when shutting down services or in testing scenarios where multiple database instances are created and destroyed.

**Sources:** [services/db/src/connection.ts:124-134]()

---

## Integration with Services

The connection management system is consumed by all Actionbook services:

| Service | Connection Pattern | Notes |
|---------|-------------------|-------|
| API Service | Singleton (`getDb()`) | Long-running HTTP server |
| Action Builder | Singleton (`getDb()`) | Long-running worker process |
| Playbook Builder | Singleton (`getDb()`) | Long-running worker process |
| Knowledge Builder | Singleton (`getDb()`) | Long-running worker process |
| CLI | Explicit (`createDb()` + `closeDb()`) | Short-lived commands |

Services running in AWS AgentCore automatically use the `pg` driver due to the `AWS_AGENTCORE_RUNTIME` environment variable check, ensuring compatibility with the Node.js-based runtime.

**Sources:** [services/db/src/connection.ts:25-40](), [services/db/src/connection.ts:142-147]()

---

# Page: Search and Indexing

# Search and Indexing

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [services/db/migrations/0019_add_vector_indexes.sql](services/db/migrations/0019_add_vector_indexes.sql)
- [services/db/migrations/0020_add_chunks_fulltext_index.sql](services/db/migrations/0020_add_chunks_fulltext_index.sql)

</details>



This document covers the search and indexing implementation in Actionbook's data layer. It explains how the system enables fast retrieval of actions through full-text search, vector similarity search, and hybrid search that combines both approaches.

For information about the overall database schema, see [Database Schema](#5.1). For details on database connection management, see [Database Connection Management](#5.2). For information about how search is exposed through the API, see [API Service](#3.1).

## Purpose and Scope

The search and indexing system provides:

- **Full-text search** using PostgreSQL's GIN (Generalized Inverted Index) for keyword-based queries
- **Vector similarity search** using HNSW (Hierarchical Navigable Small World) indexes for semantic similarity
- **Hybrid search** combining both approaches for optimal relevance
- **Performance optimization** through specialized indexes and query patterns

All search operations target the `chunks` table, which contains text segments extracted from crawled pages along with their vector embeddings. Search results reference related `elements` (UI components with selectors) and `pages`.

## Search Architecture

The following diagram shows how search queries flow through the system and which indexes are used:

```mermaid
graph TB
    subgraph "Query Entry Points"
        SearchAPI["GET /actions/search<br/>Query: {q, type, sourceId}"]
        SDK["SDK: searchActions()"]
        CLI["CLI: actionbook search"]
        MCP["MCP: search_actions"]
    end
    
    subgraph "Search Layer"
        HybridSearch["Hybrid Search Logic<br/>Combines fulltext + vector"]
        FulltextSearch["Fulltext Search<br/>PostgreSQL ts_vector"]
        VectorSearch["Vector Search<br/>Cosine similarity"]
    end
    
    subgraph "Database Indexes"
        GIN_Full["chunks_content_gin_idx<br/>GIN on to_tsvector(content)"]
        GIN_Active["chunks_content_gin_active_idx<br/>Partial GIN for active chunks"]
        HNSW["chunks_embedding_hnsw_idx<br/>HNSW vector_cosine_ops"]
        Composite["chunks_version_embedding_idx<br/>source_version_id composite"]
    end
    
    subgraph "Data Tables"
        ChunksTable[("chunks table<br/>content + embedding")]
        DocumentsTable[("documents table<br/>page metadata")]
        ElementsTable[("elements table<br/>selectors")]
    end
    
    SearchAPI --> HybridSearch
    SDK --> HybridSearch
    CLI --> HybridSearch
    MCP --> HybridSearch
    
    HybridSearch --> FulltextSearch
    HybridSearch --> VectorSearch
    
    FulltextSearch --> GIN_Full
    FulltextSearch --> GIN_Active
    VectorSearch --> HNSW
    VectorSearch --> Composite
    
    GIN_Full --> ChunksTable
    GIN_Active --> ChunksTable
    HNSW --> ChunksTable
    Composite --> ChunksTable
    
    ChunksTable --> DocumentsTable
    ChunksTable --> ElementsTable
```

Sources: [services/db/migrations/0019_add_vector_indexes.sql:1-22](), [services/db/migrations/0020_add_chunks_fulltext_index.sql:1-19]()

## Index Types

The system uses three specialized index types on the `chunks` table:

| Index Name | Type | Purpose | Performance Impact |
|------------|------|---------|-------------------|
| `chunks_content_gin_idx` | GIN | Full-text search on all chunks | ~200ms queries (vs ~2s without) |
| `chunks_content_gin_active_idx` | Partial GIN | Full-text search on active chunks only | Faster than full index for common queries |
| `chunks_embedding_hnsw_idx` | HNSW | Vector similarity search | Approximate nearest neighbor in <100ms |
| `chunks_version_embedding_idx` | Composite B-tree | Filter by version with embedding | Speeds up hybrid queries |
| `chunks_source_version_id_idx` | B-tree | Join optimization | Faster version filtering |
| `chunks_document_id_idx` | B-tree | Join optimization | Faster document lookups |

Sources: [services/db/migrations/0019_add_vector_indexes.sql:1-22](), [services/db/migrations/0020_add_chunks_fulltext_index.sql:1-19]()

## Full-Text Search Implementation

Full-text search uses PostgreSQL's native text search capabilities with GIN indexes on `to_tsvector('english', content)`.

### GIN Indexes

Two GIN indexes are created for different query patterns:

**Full Index** - All chunks:
```sql
CREATE INDEX IF NOT EXISTS chunks_content_gin_idx
ON chunks
USING gin (to_tsvector('english', content));
```

**Partial Index** - Active chunks only (optimization):
```sql
CREATE INDEX IF NOT EXISTS chunks_content_gin_active_idx
ON chunks
USING gin (to_tsvector('english', content))
WHERE source_version_id IS NOT NULL;
```

The partial index is smaller and faster when queries filter by active source versions, which is the most common pattern.

Sources: [services/db/migrations/0020_add_chunks_fulltext_index.sql:5-14]()

### Performance Characteristics

- **Without index**: ~2 seconds per query
- **With GIN index**: ~200ms per query
- **With partial GIN index**: <100ms for active chunk queries (most common case)

The dramatic performance improvement comes from GIN's ability to index all lexemes (words) in the text, enabling rapid lookup without scanning every row.

Sources: [services/db/migrations/0020_add_chunks_fulltext_index.sql:2]()

## Vector Similarity Search

Vector search uses the pgvector extension with HNSW indexes for approximate nearest neighbor search on the `embedding` column.

### HNSW Index Configuration

```sql
CREATE INDEX IF NOT EXISTS chunks_embedding_hnsw_idx
ON chunks
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);
```

**Parameters**:
- `m = 16`: Number of connections per layer (default). Higher values improve recall but slow index building.
- `ef_construction = 64`: Size of dynamic candidate list during construction (default). Higher values improve index quality.
- `vector_cosine_ops`: Uses cosine distance metric for similarity comparison.

Sources: [services/db/migrations/0019_add_vector_indexes.sql:7-10]()

### HNSW Algorithm

HNSW (Hierarchical Navigable Small World) is an approximate nearest neighbor algorithm that:

1. Builds a multi-layer graph structure where each node represents a vector
2. Uses greedy search through the layers to find approximate neighbors
3. Provides fast queries (typically <100ms) with high recall (>90%)
4. Trades exact accuracy for speed - acceptable for semantic search

The cosine distance metric measures similarity between embeddings:
- Distance of 0: Identical vectors
- Distance of 1: Completely orthogonal vectors
- Distance of 2: Opposite vectors

## Composite Indexes for Filtering

Additional indexes optimize common filtering patterns:

### Version and Embedding Filter

```sql
CREATE INDEX IF NOT EXISTS chunks_version_embedding_idx
ON chunks (source_version_id)
WHERE embedding IS NOT NULL;
```

This composite index helps queries that:
- Filter by a specific source version
- Only consider chunks with embeddings

This pattern is common in hybrid search where the API filters by the active version before searching.

Sources: [services/db/migrations/0019_add_vector_indexes.sql:18-21]()

### Version Join Optimization

```sql
CREATE INDEX IF NOT EXISTS chunks_source_version_id_idx
ON chunks (source_version_id)
WHERE source_version_id IS NOT NULL;
```

Optimizes joins between `chunks` and `source_versions` tables when filtering by active versions.

Sources: [services/db/migrations/0019_add_vector_indexes.sql:12-15]()

## Hybrid Search Strategy

The following diagram shows how hybrid search combines full-text and vector results:

```mermaid
graph TB
    QueryInput["User Query<br/>{q: 'click login button', type: 'hybrid'}"]
    
    subgraph "Query Processing"
        ParseQuery["Parse query string<br/>Extract keywords"]
        GenerateEmbedding["Generate query embedding<br/>via OpenAI API"]
    end
    
    subgraph "Parallel Search Execution"
        FulltextQuery["Fulltext Query<br/>SELECT * FROM chunks<br/>WHERE to_tsvector(content)<br/>@@ to_tsquery(q)<br/>ORDER BY ts_rank DESC"]
        
        VectorQuery["Vector Query<br/>SELECT * FROM chunks<br/>ORDER BY embedding <=> $1<br/>LIMIT 50"]
    end
    
    subgraph "Index Utilization"
        UseGIN["Uses chunks_content_gin_active_idx<br/>for active chunks"]
        UseHNSW["Uses chunks_embedding_hnsw_idx<br/>for similarity"]
    end
    
    subgraph "Result Merging"
        DedupeResults["Deduplicate by chunk_id"]
        RankResults["Rank by combined score:<br/>fulltext_score * 0.5 +<br/>similarity_score * 0.5"]
        LimitResults["LIMIT to requested count"]
    end
    
    subgraph "Response Enrichment"
        JoinDocuments["JOIN documents<br/>for page context"]
        JoinElements["JOIN elements<br/>for selectors"]
        FormatResponse["Format as ActionResult[]"]
    end
    
    QueryInput --> ParseQuery
    QueryInput --> GenerateEmbedding
    
    ParseQuery --> FulltextQuery
    GenerateEmbedding --> VectorQuery
    
    FulltextQuery --> UseGIN
    VectorQuery --> UseHNSW
    
    UseGIN --> DedupeResults
    UseHNSW --> DedupeResults
    
    DedupeResults --> RankResults
    RankResults --> LimitResults
    LimitResults --> JoinDocuments
    JoinDocuments --> JoinElements
    JoinElements --> FormatResponse
```

Sources: [services/db/migrations/0019_add_vector_indexes.sql:1-22](), [services/db/migrations/0020_add_chunks_fulltext_index.sql:1-19]()

### Hybrid Search Algorithm

The hybrid search implementation performs these steps:

1. **Execute parallel queries**:
   - Full-text search using `to_tsvector` and `to_tsquery` with GIN index
   - Vector search using cosine distance `<=>` operator with HNSW index

2. **Score normalization**:
   - Full-text scores: Use `ts_rank()` or `ts_rank_cd()` (cover density)
   - Vector scores: Convert cosine distance to similarity (1 - distance)

3. **Result merging**:
   - Deduplicate chunks appearing in both result sets
   - Combine scores with configurable weights (typically 0.5 each)
   - Sort by combined score in descending order

4. **Enrichment**:
   - Join with `documents` to get page URLs and titles
   - Join with `elements` to get selectors and capabilities
   - Format as complete action results

### Search Type Selection

The API supports three search types:

| Type | Behavior | Use Case |
|------|----------|----------|
| `fulltext` | Only GIN-based text search | Exact keyword matching |
| `vector` | Only HNSW-based similarity | Semantic/conceptual search |
| `hybrid` | Combined approach (default) | Best general-purpose results |

## Query Optimization Patterns

### Active Version Filtering

Most queries filter by active source versions to avoid returning stale data:

```sql
WHERE source_version_id IN (
  SELECT id FROM source_versions 
  WHERE status = 'active'
)
```

The partial GIN index `chunks_content_gin_active_idx` specifically optimizes this pattern, reducing index size and improving query speed.

Sources: [services/db/migrations/0020_add_chunks_fulltext_index.sql:11-14]()

### Embedding Existence Check

When performing vector search, the query must filter out chunks without embeddings:

```sql
WHERE embedding IS NOT NULL
```

The composite index `chunks_version_embedding_idx` includes this condition in its WHERE clause, making it particularly efficient.

Sources: [services/db/migrations/0019_add_vector_indexes.sql:19-21]()

### Document Join Optimization

Search results often need page context from the `documents` table:

```sql
JOIN documents ON chunks.document_id = documents.id
```

The `chunks_document_id_idx` index accelerates this join operation.

Sources: [services/db/migrations/0020_add_chunks_fulltext_index.sql:17-18]()

## Index Maintenance

### Building Indexes

All indexes are created with `IF NOT EXISTS` to be idempotent across migrations:

```sql
CREATE INDEX IF NOT EXISTS index_name ON table_name ...
```

### Index Build Time

Index construction time varies by size:

| Index Type | Build Time (est.) | Notes |
|------------|------------------|-------|
| GIN (full) | 1-5 minutes | For ~100k chunks |
| GIN (partial) | 30 seconds - 2 minutes | Smaller subset |
| HNSW | 5-15 minutes | More expensive construction |
| B-tree | <1 minute | Fast for simple indexes |

HNSW construction is CPU-intensive due to graph building. The `ef_construction` parameter directly impacts build time.

### Index Storage

Approximate storage overhead:

- **GIN indexes**: 50-100% of indexed column size
- **HNSW indexes**: 30-60% of embedding column size (depends on `m` parameter)
- **B-tree indexes**: 10-30% of indexed column size

## Performance Monitoring

### Query Plan Analysis

Use `EXPLAIN ANALYZE` to verify index usage:

```sql
EXPLAIN ANALYZE
SELECT * FROM chunks
WHERE to_tsvector('english', content) @@ to_tsquery('login');
```

Expected output should show:
```
Bitmap Heap Scan on chunks
  -> Bitmap Index Scan on chunks_content_gin_idx
```

### Index Statistics

PostgreSQL tracks index usage in `pg_stat_user_indexes`:

```sql
SELECT 
  indexrelname,
  idx_scan,
  idx_tup_read,
  idx_tup_fetch
FROM pg_stat_user_indexes
WHERE tablename = 'chunks';
```

Key metrics:
- `idx_scan`: Number of index scans
- `idx_tup_read`: Number of index entries returned
- `idx_tup_fetch`: Number of rows fetched

Sources: [services/db/migrations/0019_add_vector_indexes.sql:1-22](), [services/db/migrations/0020_add_chunks_fulltext_index.sql:1-19]()

---

# Page: AI and LLM Integration

# AI and LLM Integration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.prettierignore](.prettierignore)
- [.prettierrc.json](.prettierrc.json)
- [CLAUDE.md](CLAUDE.md)
- [services/action-builder/.gitignore](services/action-builder/.gitignore)
- [services/action-builder/package.json](services/action-builder/package.json)
- [services/action-builder/scripts/crawl-playbook-batch.ts](services/action-builder/scripts/crawl-playbook-batch.ts)
- [services/action-builder/scripts/crawl-sites.txt.example](services/action-builder/scripts/crawl-sites.txt.example)
- [services/action-builder/scripts/import-playbook-batch.ts](services/action-builder/scripts/import-playbook-batch.ts)
- [services/action-builder/scripts/login.ts](services/action-builder/scripts/login.ts)
- [services/action-builder/src/llm/AIClient.ts](services/action-builder/src/llm/AIClient.ts)
- [services/action-builder/src/optimizer/SelectorOptimizer.ts](services/action-builder/src/optimizer/SelectorOptimizer.ts)
- [services/action-builder/src/utils/logger.ts](services/action-builder/src/utils/logger.ts)
- [services/action-builder/vitest.setup.ts](services/action-builder/vitest.setup.ts)
- [services/common/browser-profile/package.json](services/common/browser-profile/package.json)
- [services/common/browser-profile/src/BrowserProfileManager.ts](services/common/browser-profile/src/BrowserProfileManager.ts)
- [services/db/migrations/meta/0018_snapshot.json](services/db/migrations/meta/0018_snapshot.json)

</details>



This page documents the AI and Large Language Model (LLM) integration layer in Actionbook. It covers the multi-provider LLM client architecture, selector optimization using AI, and how LLMs power capability discovery throughout the system.

For browser automation details using AI-powered observation, see [Browser Automation Layer](#4). For action recording workflows that use LLM tool calling, see [Action Recording](#3.2.2). For capability discovery implementation, see [Capability Discovery](#6.3).

## Overview

Actionbook uses LLMs for three primary purposes:

1. **Action Recording** - Multi-turn LLM conversations with structured tools to discover and register UI capabilities
2. **Selector Optimization** - Batch analysis of discovered selectors to identify unstable patterns and rank selector reliability
3. **Capability Discovery** - AI-powered page observation to extract semantic element information and interactions

The system supports multiple LLM providers through a unified client interface, with automatic provider detection based on available API keys.

## Multi-Provider LLM Architecture

### AIClient Design

The `AIClient` class provides a unified interface to multiple LLM providers using the Vercel AI SDK. It handles provider auto-detection, message format conversion, proxy support, and metrics collection.

```mermaid
graph TB
    subgraph "Client Layer"
        AIClient["AIClient<br/>(services/action-builder/src/llm/AIClient.ts)"]
    end
    
    subgraph "Provider Abstraction"
        VercelAI["Vercel AI SDK<br/>generateText()<br/>LanguageModel interface"]
    end
    
    subgraph "Provider Implementations"
        OpenRouter["createOpenRouter()<br/>@openrouter/ai-sdk-provider"]
        OpenAI["createOpenAI()<br/>@ai-sdk/openai"]
        Anthropic["createAnthropic()<br/>@ai-sdk/anthropic"]
        Bedrock["createAmazonBedrock()<br/>@ai-sdk/amazon-bedrock"]
    end
    
    subgraph "Configuration"
        EnvVars["Environment Variables<br/>OPENROUTER_API_KEY<br/>OPENAI_API_KEY<br/>ANTHROPIC_API_KEY<br/>AWS_ACCESS_KEY_ID"]
        ProxyConfig["Proxy Support<br/>HTTPS_PROXY<br/>HTTP_PROXY"]
    end
    
    subgraph "Consumers"
        ActionRecorder["ActionRecorder<br/>(action recording loop)"]
        RecorderTools["RecorderToolExecutor<br/>(tool execution)"]
        SelectorOpt["SelectorOptimizer<br/>(batch optimization)"]
    end
    
    AIClient --> VercelAI
    VercelAI --> OpenRouter
    VercelAI --> OpenAI
    VercelAI --> Anthropic
    VercelAI --> Bedrock
    
    EnvVars --> AIClient
    ProxyConfig --> AIClient
    
    ActionRecorder --> AIClient
    RecorderTools --> AIClient
    SelectorOpt -.->|"similar pattern"| AIClient
```

**Sources:** [services/action-builder/src/llm/AIClient.ts:1-544]()

### Provider Detection and Priority

Provider selection follows automatic detection with priority ordering:

| Priority | Provider | Environment Variable | Default Model |
|----------|----------|---------------------|---------------|
| 1 | OpenRouter | `OPENROUTER_API_KEY` | `anthropic/claude-sonnet-4` |
| 2 | OpenAI | `OPENAI_API_KEY` | `gpt-4o` |
| 3 | Anthropic | `ANTHROPIC_API_KEY` | `claude-sonnet-4-5` |
| 4 | AWS Bedrock | `AWS_ACCESS_KEY_ID` + `AWS_SECRET_ACCESS_KEY` | `anthropic.claude-3-5-sonnet-20241022-v2:0` |

The `resolveConfig()` method implements this detection logic:

```mermaid
graph TD
    Start["resolveConfig()"] --> ExplicitProvider{"config.provider<br/>specified?"}
    ExplicitProvider -->|Yes| ValidateExplicit["Validate API key<br/>for provider"]
    ExplicitProvider -->|No| CheckOpenRouter{"OPENROUTER_API_KEY<br/>exists?"}
    
    CheckOpenRouter -->|Yes| UseOpenRouter["Return OpenRouter<br/>+ model config"]
    CheckOpenRouter -->|No| CheckOpenAI{"OPENAI_API_KEY<br/>exists?"}
    
    CheckOpenAI -->|Yes| UseOpenAI["Return OpenAI<br/>+ model config"]
    CheckOpenAI -->|No| CheckAnthropic{"ANTHROPIC_API_KEY<br/>exists?"}
    
    CheckAnthropic -->|Yes| UseAnthropic["Return Anthropic<br/>+ model config"]
    CheckAnthropic -->|No| CheckBedrock{"AWS credentials<br/>exist?"}
    
    CheckBedrock -->|Yes| UseBedrock["Return Bedrock<br/>+ model config"]
    CheckBedrock -->|No| ThrowError["throw Error:<br/>No API key found"]
    
    ValidateExplicit --> ReturnConfig["Return validated<br/>config"]
    UseOpenRouter --> ReturnConfig
    UseOpenAI --> ReturnConfig
    UseAnthropic --> ReturnConfig
    UseBedrock --> ReturnConfig
```

**Sources:** [services/action-builder/src/llm/AIClient.ts:97-171]()

### Message Format Conversion

The `AIClient` converts between OpenAI-compatible message formats (used internally) and Vercel AI SDK formats. This abstraction allows the codebase to use a consistent interface while supporting multiple providers.

**Key Conversions:**

1. **Tool Calls** - Assistant messages with `tool_calls` are converted to AI SDK's content array format with `type: 'tool-call'`
2. **Tool Results** - Tool messages become AI SDK tool results with structured output format (`{type: 'json' | 'text', value: any}`)
3. **Tool Call ID Mapping** - Maintains a map to associate tool results with their originating tool names

**Sources:** [services/action-builder/src/llm/AIClient.ts:222-312]()

### Proxy Support

The `createProxyFetch()` function enables HTTP/HTTPS proxy support for LLM API calls. It wraps `undici`'s fetch with a `ProxyAgent`:

```mermaid
graph LR
    AIClient --> ProxyCheck{"HTTPS_PROXY or<br/>HTTP_PROXY set?"}
    ProxyCheck -->|Yes| ProxyAgent["ProxyAgent<br/>(undici)"]
    ProxyCheck -->|No| DirectFetch["Standard fetch"]
    
    ProxyAgent --> CustomFetch["Custom fetch wrapper"]
    DirectFetch --> ProviderSDK["Provider SDK"]
    CustomFetch --> ProviderSDK
    
    ProviderSDK --> LLMEndpoint["LLM API<br/>Endpoint"]
```

**Sources:** [services/action-builder/src/llm/AIClient.ts:36-54](), [services/action-builder/src/optimizer/SelectorOptimizer.ts:72-93]()

### Metrics and Observability

The `AIClient` collects comprehensive metrics for each LLM call:

**Metric Structure (`LLMMetrics` interface):**

| Field | Type | Description |
|-------|------|-------------|
| `inputTokens` | number | Prompt tokens consumed |
| `outputTokens` | number | Completion tokens generated |
| `totalTokens` | number | Sum of input + output |
| `cacheCreationInputTokens` | number? | Tokens used to populate cache (Anthropic) |
| `cacheReadInputTokens` | number? | Tokens read from cache (Anthropic) |
| `reasoningTokens` | number? | Reasoning tokens (o1/o3 models) |
| `e2eLatencyMs` | number | End-to-end request latency |
| `tps` | number | Tokens per second (output / latency) |
| `provider` | string | Provider name |
| `model` | string | Model identifier |
| `success` | boolean | Request succeeded |
| `errorType` | string? | Error classification |

**Log Format:**
```
[LLM] ✓ | openrouter/anthropic/claude-sonnet-4 | tokens: in=1234, out=567, total=1801 | perf: latency=2450ms, tps=23.1
```

**Sources:** [services/action-builder/src/llm/AIClient.ts:11-31](), [services/action-builder/src/llm/AIClient.ts:443-471]()

### Retry Logic

The client uses Vercel AI SDK's built-in retry mechanism with exponential backoff:

- **Max Retries:** 5 (configurable)
- **Total Attempts:** 6 (1 initial + 5 retries)
- **Backoff Strategy:** Exponential with jitter (handled by SDK)
- **Rate Limit Handling:** Automatic retry with longer delays

**Sources:** [services/action-builder/src/llm/AIClient.ts:354-363]()

## Selector Optimization

The `SelectorOptimizer` uses LLM analysis to improve selector reliability by identifying unstable patterns and reordering selectors by stability.

```mermaid
graph TB
    subgraph "Input"
        Elements["Map<string, ElementCapability><br/>discovered elements<br/>with multiple selectors"]
    end
    
    subgraph "SelectorOptimizer"
        PrepInput["Prepare SelectorInput[]<br/>{elementId, description, selectors}"]
        LLMAnalysis["LLM Analysis<br/>Detect unstable patterns<br/>Rank selectors"]
        ApplyResults["Apply Results<br/>Mark unstable (confidence=0.1)<br/>Reorder by stability"]
    end
    
    subgraph "LLM Analysis Patterns"
        Unstable["UNSTABLE PATTERNS<br/>- Dynamic counters: '3 new'<br/>- Timestamps: '2m ago'<br/>- Framework IDs: :r0:, #ember123<br/>- Hash classes: .css-abc123<br/>- Session IDs"]
        Stable["STABLE PATTERNS<br/>- data-testid<br/>- data-* semantic attrs<br/>- Static aria-label<br/>- Semantic IDs<br/>- BEM classes"]
    end
    
    subgraph "Output"
        Optimized["OptimizationResult<br/>optimized selectors<br/>stability reasons<br/>token usage"]
    end
    
    Elements --> PrepInput
    PrepInput --> LLMAnalysis
    LLMAnalysis --> Unstable
    LLMAnalysis --> Stable
    Unstable --> ApplyResults
    Stable --> ApplyResults
    ApplyResults --> Optimized
```

**Sources:** [services/action-builder/src/optimizer/SelectorOptimizer.ts:1-372]()

### Unstable Selector Patterns

The optimizer prompt instructs the LLM to detect these unstable patterns:

**Dynamic Content:**
- Counters/notifications: `"0 条新通知"`, `"3 new messages"`, `"(5)"`, `"+99"`
- Timestamps: `"2 minutes ago"`, `"刚刚"`, `"Yesterday"`
- User-specific: Contains usernames, IDs like `"user-12345"`
- Session tokens: Random tokens, session IDs

**Framework-Generated IDs:**
- React: `:r0:`, `:r1:`, `#react-xxx`
- Ember: `#ember123`
- Angular: `.ng-c123`
- Radix: `#radix-123`

**Hash-Based CSS Classes:**
- CSS Modules: `.styles_button__x7y8z`, `.Component_name__hash`
- styled-components: `.sc-1a2b3c`, `.sc-aBcDeF`
- Emotion: `.css-1a2b3c`, `.css-xxxxxx`
- Generic patterns: Classes ending with `_[a-z0-9]{5,}`, `__[a-z0-9]{5,}`, or `-[a-z0-9]{6,}`

**Sources:** [services/action-builder/src/optimizer/SelectorOptimizer.ts:289-299]()

### Selector Priority Ranking

When all selectors are stable, the LLM uses this priority ordering:

1. `data-testid` (most stable, designed for testing)
2. Other semantic `data-*` attributes (`data-id`, `data-component`, `data-element`)
3. `id` selector (`#id`)
4. Static `aria-label`
5. Semantic CSS class (BEM naming)
6. XPath (least preferred)

**Sources:** [services/action-builder/src/optimizer/SelectorOptimizer.ts:308-314]()

### Batch Processing

The optimizer processes all elements in a single LLM call for efficiency:

```mermaid
graph LR
    Input["50-100 elements<br/>with 2-5 selectors each"] --> Batch["Single LLM Call<br/>generateText()"]
    Batch --> Parse["Parse JSON Array<br/>SelectorAnalysisResult[]"]
    Parse --> Apply["Apply to each element:<br/>1. Mark unstable selectors<br/>2. Reorder by stability<br/>3. Adjust confidence"]
    Apply --> Output["Optimized elements<br/>with ranked selectors"]
```

**Input Format:**
```typescript
interface SelectorInput {
  elementId: string
  description: string
  selectors: SelectorItem[]
}
```

**Output Format:**
```typescript
interface SelectorAnalysisResult {
  elementId: string
  bestSelectorIndex: number          // Index of best selector
  unstableSelectorIndices: number[]  // All unstable selectors
  reason: string                     // Explanation
  adjustedConfidence?: number        // 0.1-0.95
}
```

**Sources:** [services/action-builder/src/optimizer/SelectorOptimizer.ts:23-65](), [services/action-builder/src/optimizer/SelectorOptimizer.ts:157-278]()

### Model Configuration

The optimizer uses smaller/faster models to reduce costs:

| Provider | Default Model | Override Variable |
|----------|--------------|-------------------|
| OpenRouter | `gpt-4o-mini` | `SELECTOR_OPTIMIZER_MODEL` |
| OpenAI | `gpt-4o-mini` | `SELECTOR_OPTIMIZER_MODEL` |
| Anthropic | `claude-3-5-haiku-latest` | `SELECTOR_OPTIMIZER_MODEL` |
| Bedrock | `anthropic.claude-3-5-haiku-20241022-v1:0` | `SELECTOR_OPTIMIZER_MODEL` |

**Sources:** [services/action-builder/src/optimizer/SelectorOptimizer.ts:98-153]()

## Integration Points

### Action Recording Loop

The action recording system uses LLM-driven tool calling to discover and register UI capabilities. The `AIClient` powers the multi-turn conversation loop:

```mermaid
graph TB
    Start["Start Recording Task"] --> InitLLM["Initialize AIClient<br/>with system prompt"]
    InitLLM --> ToolLoop["Multi-turn Loop<br/>(max 30 turns)"]
    
    ToolLoop --> LLMCall["AIClient.chat()<br/>messages + tools"]
    LLMCall --> Response{"Response type?"}
    
    Response -->|"tool_calls"| ExecuteTools["Execute Tools:<br/>navigate, observe_page,<br/>interact, register_element"]
    Response -->|"stop"| Complete["Recording Complete"]
    
    ExecuteTools --> AddResult["Add tool result<br/>to messages"]
    AddResult --> ToolLoop
    
    ExecuteTools -.->|"observe_page"| BrowserObserve["Browser AI observe<br/>(StagehandBrowser or<br/>AgentCoreBrowser)"]
    BrowserObserve -.-> ExtractElements["Extract elements<br/>with selectors"]
    ExtractElements -.-> RegisterQueue["Queue for<br/>register_element"]
```

**Sources:** See [Action Recording](#3.2.2) for detailed workflow. The AIClient is used in [services/action-builder/src/recorder/ActionRecorder.ts]() for the recording loop.

### Browser Automation AI Operations

Browser adapters use LLM providers for AI-powered page observation:

**StagehandBrowser Integration:**
- Uses Stagehand SDK's built-in AI capabilities
- Supports all four providers (OpenRouter, OpenAI, Anthropic, Bedrock)
- Configuration: `STAGEHAND_PROVIDER`, `STAGEHAND_MODEL`
- Proxy support via `localBrowserLaunchOptions`

**AgentCoreBrowser Integration:**
- AWS cloud-based browser service
- Uses AWS Bedrock Claude exclusively
- Vision + inference for element detection

**Sources:** [services/common/browser/src/StagehandBrowser.ts](), [services/common/browser/src/AgentCoreBrowser.ts]()

### Capability Discovery

LLMs enable semantic understanding of UI elements during page observation:

1. **Visual Analysis** - AI models analyze screenshots to identify interactive elements
2. **Semantic Extraction** - Generate human-readable element descriptions and IDs
3. **Interaction Detection** - Infer allowed methods (click, type, etc.) from element type
4. **Relationship Mapping** - Detect navigation flows (leads_to)

**Sources:** See [Capability Discovery](#6.3) for implementation details.

## Configuration

### Environment Variables

**LLM Provider Configuration:**

| Variable | Purpose | Default |
|----------|---------|---------|
| `OPENROUTER_API_KEY` | OpenRouter API key | - |
| `OPENROUTER_MODEL` | OpenRouter model override | `anthropic/claude-sonnet-4` |
| `OPENAI_API_KEY` | OpenAI API key | - |
| `OPENAI_MODEL` | OpenAI model override | `gpt-4o` |
| `ANTHROPIC_API_KEY` | Anthropic API key | - |
| `ANTHROPIC_MODEL` | Anthropic model override | `claude-sonnet-4-5` |
| `AWS_ACCESS_KEY_ID` | AWS Bedrock access key | - |
| `AWS_SECRET_ACCESS_KEY` | AWS Bedrock secret key | - |
| `AWS_REGION` | AWS region | `us-east-1` |
| `AWS_BEDROCK_MODEL` | Bedrock model override | `anthropic.claude-3-5-sonnet-20241022-v2:0` |
| `SELECTOR_OPTIMIZER_MODEL` | Model for selector optimization | Provider-specific default |

**Proxy Configuration:**

| Variable | Purpose |
|----------|---------|
| `HTTPS_PROXY` | HTTPS proxy URL |
| `HTTP_PROXY` | HTTP proxy URL (fallback) |

**Stagehand-Specific:**

| Variable | Purpose |
|----------|---------|
| `STAGEHAND_PROVIDER` | Stagehand LLM provider (openai, anthropic, openrouter, bedrock) |
| `STAGEHAND_MODEL` | Stagehand model name |

**Sources:** [services/action-builder/src/llm/AIClient.ts:58-65](), [services/action-builder/src/optimizer/SelectorOptimizer.ts:117]()

### Explicit Provider Configuration

The `AIClient` constructor accepts an optional config object:

```typescript
interface AIClientConfig {
  provider?: 'openrouter' | 'openai' | 'anthropic' | 'bedrock'
  model?: string
  apiKey?: string
}

// Example: Force OpenAI with custom model
const client = new AIClient({
  provider: 'openai',
  model: 'gpt-4-turbo-preview',
  apiKey: process.env.CUSTOM_OPENAI_KEY
})
```

**Sources:** [services/action-builder/src/llm/AIClient.ts:56-71]()

## Error Handling and Reliability

### Error Classification

The `classifyError()` method categorizes failures for metrics:

| Error Type | Detection Pattern | Example |
|-----------|------------------|---------|
| `rate_limit` | Contains "429" or "rate limit" | HTTP 429, quota exceeded |
| `server_error` | Contains "5" and "00" | HTTP 500, 502, 503 |
| `timeout` | Contains "timeout" or "timed out" | Request timeout, connection timeout |
| `other` | All other errors | Network errors, invalid API key |

**Sources:** [services/action-builder/src/llm/AIClient.ts:422-440]()

### Retry Strategy

Failed requests are automatically retried with exponential backoff:

- **Initial Delay:** ~1 second (SDK-managed)
- **Backoff Multiplier:** 2x (SDK-managed)
- **Max Delay:** ~32 seconds (SDK-managed)
- **Jitter:** Random delay added to prevent thundering herd

**Sources:** [services/action-builder/src/llm/AIClient.ts:362]()

### Cost Optimization

**Token Usage Tracking:**
- All LLM calls log token consumption (input, output, cache hits)
- Metrics enable cost attribution per recording task
- Cache tokens (Anthropic) reduce repeated content costs

**Model Selection:**
- Action recording: Uses more capable models (Claude Sonnet, GPT-4o)
- Selector optimization: Uses smaller models (GPT-4o-mini, Haiku) for cost efficiency

**Sources:** [services/action-builder/src/llm/AIClient.ts:368-396](), [services/action-builder/src/optimizer/SelectorOptimizer.ts:118-128]()

## Dependencies

The AI integration layer relies on these npm packages:

| Package | Version | Purpose |
|---------|---------|---------|
| `ai` | ^5.0.113 | Vercel AI SDK core |
| `@ai-sdk/openai` | ^2.0.87 | OpenAI provider |
| `@ai-sdk/anthropic` | ^2.0.56 | Anthropic provider |
| `@openrouter/ai-sdk-provider` | ^1.5.4 | OpenRouter provider |
| `@ai-sdk/amazon-bedrock` | ^3.0.70 | AWS Bedrock provider |
| `openai` | ^4.77.0 | OpenAI SDK types |
| `undici` | ^6.22.0 | HTTP proxy support |
| `https-proxy-agent` | ^7.0.6 | Legacy proxy support |

**Sources:** [services/action-builder/package.json:45-56]()

---

# Page: AIClient

# AIClient

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.prettierignore](.prettierignore)
- [.prettierrc.json](.prettierrc.json)
- [CLAUDE.md](CLAUDE.md)
- [services/action-builder/.gitignore](services/action-builder/.gitignore)
- [services/action-builder/package.json](services/action-builder/package.json)
- [services/action-builder/scripts/crawl-playbook-batch.ts](services/action-builder/scripts/crawl-playbook-batch.ts)
- [services/action-builder/scripts/crawl-sites.txt.example](services/action-builder/scripts/crawl-sites.txt.example)
- [services/action-builder/scripts/import-playbook-batch.ts](services/action-builder/scripts/import-playbook-batch.ts)
- [services/action-builder/scripts/login.ts](services/action-builder/scripts/login.ts)
- [services/action-builder/src/llm/AIClient.ts](services/action-builder/src/llm/AIClient.ts)
- [services/action-builder/src/optimizer/SelectorOptimizer.ts](services/action-builder/src/optimizer/SelectorOptimizer.ts)
- [services/action-builder/src/utils/logger.ts](services/action-builder/src/utils/logger.ts)
- [services/action-builder/vitest.setup.ts](services/action-builder/vitest.setup.ts)
- [services/common/browser-profile/package.json](services/common/browser-profile/package.json)
- [services/common/browser-profile/src/BrowserProfileManager.ts](services/common/browser-profile/src/BrowserProfileManager.ts)
- [services/db/migrations/meta/0018_snapshot.json](services/db/migrations/meta/0018_snapshot.json)

</details>



## Purpose and Scope

`AIClient` is a multi-provider LLM client wrapper built on Vercel AI SDK that provides unified access to OpenRouter, OpenAI, Anthropic, and AWS Bedrock language models. It handles provider auto-detection, configuration resolution, message format conversion, metrics collection, and retry logic with exponential backoff. The client presents an OpenAI-compatible interface for backward compatibility while supporting multiple underlying providers.

For information about how `AIClient` is used in selector optimization workflows, see [Selector Optimizer](#6.2). For details on the recording tools that invoke `AIClient` for action discovery, see [Recording Tools Reference](#3.2.3).

**Sources:** [services/action-builder/src/llm/AIClient.ts:1-543]()

---

## Architecture and Provider Support

The `AIClient` class abstracts provider-specific differences behind a unified interface, supporting four LLM providers with automatic fallback detection.

### Provider Resolution Hierarchy

```mermaid
graph TB
    Start[AIClient Constructor]
    Start --> CheckConfig{Explicit provider<br/>in config?}
    
    CheckConfig -->|Yes| ValidateExplicit[Validate API key<br/>for provider]
    CheckConfig -->|No| AutoDetect[Auto-detect from<br/>environment]
    
    ValidateExplicit --> CreateModel[Create LanguageModel]
    
    AutoDetect --> CheckOR{OPENROUTER_API_KEY?}
    CheckOR -->|Yes| UseOR["provider='openrouter'<br/>model='anthropic/claude-sonnet-4'"]
    CheckOR -->|No| CheckOAI{OPENAI_API_KEY?}
    
    CheckOAI -->|Yes| UseOAI["provider='openai'<br/>model='gpt-4o'"]
    CheckOAI -->|No| CheckAnthropic{ANTHROPIC_API_KEY?}
    
    CheckAnthropic -->|Yes| UseAnthropic["provider='anthropic'<br/>model='claude-sonnet-4-5'"]
    CheckAnthropic -->|No| CheckBedrock{AWS credentials?}
    
    CheckBedrock -->|Yes| UseBedrock["provider='bedrock'<br/>model='anthropic.claude-3-5-sonnet'"]
    CheckBedrock -->|No| ThrowError[Throw Error:<br/>No API key found]
    
    UseOR --> CreateModel
    UseOAI --> CreateModel
    UseAnthropic --> CreateModel
    UseBedrock --> CreateModel
    
    CreateModel --> InitComplete[AIClient initialized]
```

**Sources:** [services/action-builder/src/llm/AIClient.ts:88-171]()

### Supported Providers

| Provider | Environment Variables | Default Model | SDK Package |
|----------|----------------------|---------------|-------------|
| **OpenRouter** | `OPENROUTER_API_KEY`, `OPENROUTER_MODEL` | `anthropic/claude-sonnet-4` | `@openrouter/ai-sdk-provider` |
| **OpenAI** | `OPENAI_API_KEY`, `OPENAI_MODEL` | `gpt-4o` | `@ai-sdk/openai` |
| **Anthropic** | `ANTHROPIC_API_KEY`, `ANTHROPIC_MODEL` | `claude-sonnet-4-5` | `@ai-sdk/anthropic` |
| **AWS Bedrock** | `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_BEDROCK_MODEL`, `AWS_REGION` | `anthropic.claude-3-5-sonnet-20241022-v2:0` | `@ai-sdk/amazon-bedrock` |

**Sources:** [services/action-builder/src/llm/AIClient.ts:56-180](), [services/action-builder/package.json:45-49]()

---

## Configuration Resolution

### AIClientConfig Interface

```typescript
interface AIClientConfig {
  provider?: LLMProvider;  // 'openrouter' | 'openai' | 'anthropic' | 'bedrock'
  model?: string;          // Model name override
  apiKey?: string;         // API key override
}
```

The `resolveConfig()` method implements the following resolution logic:

1. **Explicit Provider**: If `config.provider` is specified, use corresponding environment variable or `config.apiKey`
2. **Auto-detection**: Check environment variables in priority order: OpenRouter → OpenAI → Anthropic → Bedrock
3. **Model Override**: Use `config.model` if provided, otherwise use provider-specific environment variable (e.g., `OPENROUTER_MODEL`), falling back to default
4. **Bedrock Special Case**: Uses AWS credentials instead of API key

**Sources:** [services/action-builder/src/llm/AIClient.ts:58-71, 101-171]()

### Model Creation with Proxy Support

```mermaid
graph LR
    CreateModel["createModel()"]
    CreateModel --> CheckProxy{HTTPS_PROXY or<br/>HTTP_PROXY set?}
    
    CheckProxy -->|Yes| CreateProxyFetch["createProxyFetch()<br/>with undici ProxyAgent"]
    CheckProxy -->|No| NoProxy[proxyFetch = undefined]
    
    CreateProxyFetch --> CreateProvider
    NoProxy --> CreateProvider
    
    CreateProvider["Create provider SDK<br/>(OpenRouter/OpenAI/etc)"]
    CreateProvider --> PassFetch[Pass fetch: proxyFetch<br/>to provider config]
    PassFetch --> ReturnModel[Return LanguageModel]
```

**Sources:** [services/action-builder/src/llm/AIClient.ts:36-54, 183-220]()

---

## Message Format Conversion

`AIClient` accepts OpenAI-style messages and converts them to Vercel AI SDK format, handling tool calls, tool results, and multi-turn conversations.

### Message Conversion Flow

```mermaid
graph TB
    OpenAIMsgs["OpenAI.Chat.Completions<br/>.ChatCompletionMessageParam[]"]
    OpenAIMsgs --> BuildToolMap[Build toolCallId → toolName map<br/>from assistant tool_calls]
    
    BuildToolMap --> ConvertLoop[Iterate messages]
    
    ConvertLoop --> CheckRole{Message role?}
    
    CheckRole -->|system| SystemMsg["{ role: 'system',<br/>content: string }"]
    CheckRole -->|user| UserMsg["{ role: 'user',<br/>content: string }"]
    CheckRole -->|assistant| CheckToolCalls{Has tool_calls?}
    CheckRole -->|tool| ToolResult
    
    CheckToolCalls -->|Yes| AssistantWithTools["{ role: 'assistant',<br/>content: [<br/>  { type: 'text', text },<br/>  { type: 'tool-call',<br/>    toolCallId, toolName, input }<br/>]}"]
    CheckToolCalls -->|No| AssistantText["{ role: 'assistant',<br/>content: string }"]
    
    ToolResult --> ParseContent{Parse tool<br/>content as JSON?}
    ParseContent -->|Success| JSONOutput["{ role: 'tool',<br/>content: [<br/>  { type: 'tool-result',<br/>    toolCallId, toolName,<br/>    output: { type: 'json', value } }<br/>]}"]
    ParseContent -->|Fail| TextOutput["output: { type: 'text',<br/>value: string }"]
    
    SystemMsg --> VercelFormat
    UserMsg --> VercelFormat
    AssistantWithTools --> VercelFormat
    AssistantText --> VercelFormat
    JSONOutput --> VercelFormat
    TextOutput --> VercelFormat
    
    VercelFormat["Vercel AI SDK<br/>message format"]
```

**Sources:** [services/action-builder/src/llm/AIClient.ts:224-312]()

### Tool Call Conversion Details

The `convertMessages()` method handles special cases:

- **Tool Call Arguments**: Parses `tc.function.arguments` JSON string, defaults to `{}` on parse failure
- **AI SDK v5 Format**: Uses `input` field instead of `args` for tool calls
- **Tool Result Output**: Wraps in discriminated union with `{ type: 'json'|'text', value }` format
- **Tool Name Resolution**: Maps `tool_call_id` back to `toolName` using pre-built map from assistant messages

**Sources:** [services/action-builder/src/llm/AIClient.ts:258-307]()

---

## Tool Calling Support

`AIClient` supports OpenAI-style tool definitions, converting them to Vercel AI SDK format using direct JSON Schema passthrough.

### Tool Conversion Process

```typescript
// Input: OpenAI.Chat.Completions.ChatCompletionTool[]
// Output: Record<string, aiTool>

convertTools(tools) {
  for (const tool of tools) {
    if (tool.type === 'function') {
      result[tool.function.name] = aiTool({
        description: tool.function.description,
        inputSchema: jsonSchema(tool.function.parameters), // Direct JSON Schema
      });
    }
  }
}
```

**Key Design Decision**: Uses `jsonSchema()` from Vercel AI SDK for direct JSON Schema passthrough, avoiding Zod conversion issues with complex parameter schemas.

**Sources:** [services/action-builder/src/llm/AIClient.ts:318-337]()

### Tool Call Response Conversion

```mermaid
graph LR
    VercelResult["generateText() result"]
    VercelResult --> ExtractToolCalls["Extract toolCalls array<br/>(handle v5 property names)"]
    
    ExtractToolCalls --> MapToolCalls[Map to OpenAI format]
    
    MapToolCalls --> ToolCallObj["tool_calls: [{<br/>  id: toolCallId,<br/>  type: 'function',<br/>  function: {<br/>    name: toolName,<br/>    arguments: JSON.stringify(input)<br/>  }<br/>}]"]
    
    ToolCallObj --> BuildResponse[Build ChatCompletion]
    BuildResponse --> OpenAIResponse["OpenAI.Chat.Completions<br/>.ChatCompletion"]
```

**Sources:** [services/action-builder/src/llm/AIClient.ts:476-528]()

---

## Metrics Collection

`AIClient` tracks comprehensive metrics for each LLM call, enabling observability and performance monitoring.

### LLMMetrics Interface

```typescript
interface LLMMetrics {
  // Token statistics
  inputTokens: number;
  outputTokens: number;
  totalTokens: number;
  cacheCreationInputTokens?: number;    // Anthropic prompt caching
  cacheReadInputTokens?: number;        // Anthropic cache hits
  reasoningTokens?: number;             // o1/o3 models
  
  // Performance statistics
  e2eLatencyMs: number;                 // End-to-end latency
  tps: number;                          // Tokens per second
  
  // Request metadata
  provider: string;
  model: string;
  success: boolean;
  errorType?: string;                   // 'rate_limit' | 'server_error' | 'timeout' | 'other'
}
```

**Sources:** [services/action-builder/src/llm/AIClient.ts:13-31]()

### Metrics Collection and Logging

```mermaid
graph TB
    Start[Start LLM call]
    Start --> RecordStartTime["startTime = Date.now()"]
    
    RecordStartTime --> CallGenerateText["generateText({ model, messages, tools })"]
    
    CallGenerateText --> CheckSuccess{Success?}
    
    CheckSuccess -->|Yes| ExtractUsage["Extract usage from result:<br/>- inputTokens (promptTokens)<br/>- outputTokens (completionTokens)<br/>- cacheCreationInputTokens<br/>- cacheReadInputTokens<br/>- reasoningTokens"]
    
    ExtractUsage --> CalcMetrics["Calculate metrics:<br/>- e2eLatencyMs = now - startTime<br/>- tps = outputTokens / (latency/1000)<br/>- totalTokens = in + out"]
    
    CalcMetrics --> BuildSuccessMetrics["LLMMetrics { success: true, ... }"]
    
    CheckSuccess -->|No| ClassifyError["classifyError(error):<br/>- 'rate_limit': 429, 'rate limit'<br/>- 'server_error': '5xx'<br/>- 'timeout': 'timeout', 'timed out'<br/>- 'other': default"]
    
    ClassifyError --> BuildErrorMetrics["LLMMetrics {<br/>success: false,<br/>errorType,<br/>tokens: 0<br/>}"]
    
    BuildSuccessMetrics --> LogMetrics["logMetrics(metrics)"]
    BuildErrorMetrics --> LogMetrics
    
    LogMetrics --> FormatLog["Format:<br/>'[LLM] ✓|✗ | provider/model |<br/>tokens: in=X, out=Y, cache_read=Z, total=T |<br/>perf: latency=Xms, tps=Y'"]
    
    FormatLog --> WriteLog["log('info', formatted)"]
```

**Sources:** [services/action-builder/src/llm/AIClient.ts:343-421, 423-471]()

### Example Log Output

```
[LLM] ✓ | openrouter/anthropic/claude-sonnet-4 | tokens: in=2341, out=856, cache_read=1200, total=3197 | perf: latency=3240ms, tps=264.2
[LLM] ✗ rate_limit | openai/gpt-4o | tokens: in=0, out=0, total=0 | perf: latency=1250ms, tps=0
```

**Sources:** [services/action-builder/src/llm/AIClient.ts:445-471]()

---

## Error Handling and Retry Logic

### Built-in Retry Mechanism

`AIClient` leverages Vercel AI SDK's automatic retry with exponential backoff for transient failures:

```typescript
const result = await generateText({
  model: this.model,
  messages: modelMessages,
  tools: aiTools,
  maxOutputTokens: 4096,
  maxRetries: 5,  // 1 initial + 5 retries = 6 total attempts
});
```

**Retry Behavior**:
- Rate limit errors (`429`): Exponential backoff automatically applied
- Total attempts: 6 (1 initial + 5 retries)
- Errors are classified and logged with `errorType` metric

**Sources:** [services/action-builder/src/llm/AIClient.ts:357-363]()

### Error Classification

```mermaid
graph TD
    Error[Error caught]
    Error --> Extract[Extract error message]
    Extract --> CheckMsg{Check error message}
    
    CheckMsg -->|"'429' or<br/>'rate limit'"| RateLimit["errorType = 'rate_limit'"]
    CheckMsg -->|"'5' and '00'"| ServerError["errorType = 'server_error'"]
    CheckMsg -->|"'timeout' or<br/>'timed out'"| Timeout["errorType = 'timeout'"]
    CheckMsg -->|Other| Other["errorType = 'other'"]
    
    RateLimit --> Return[Return errorType]
    ServerError --> Return
    Timeout --> Return
    Other --> Return
```

**Sources:** [services/action-builder/src/llm/AIClient.ts:426-440]()

---

## Proxy Support

`AIClient` supports HTTP/HTTPS proxies via `HTTPS_PROXY` or `HTTP_PROXY` environment variables, using undici's `ProxyAgent`.

### Proxy Configuration Flow

```typescript
function createProxyFetch(): typeof fetch | undefined {
  const proxyUrl = process.env.HTTPS_PROXY || process.env.HTTP_PROXY;
  if (!proxyUrl) return undefined;
  
  const proxyAgent = new ProxyAgent(proxyUrl);
  
  return async (input: RequestInfo | URL, init?: RequestInit): Promise<Response> => {
    const url = typeof input === 'string' ? input : 
                input instanceof URL ? input.href : 
                input.url;
    const response = await undiciFetch(url, {
      ...init,
      dispatcher: proxyAgent,
    });
    return response as unknown as Response;
  };
}
```

**Usage**: Proxy fetch function is passed to each provider SDK during model creation:

```typescript
const openrouter = createOpenRouter({
  apiKey,
  fetch: proxyFetch,  // Custom fetch with proxy
});
```

**Sources:** [services/action-builder/src/llm/AIClient.ts:36-54, 189-192]()

---

## Usage in Action Builder

### Class Structure and Dependencies

```mermaid
graph TB
    AIClient["AIClient<br/>(llm/AIClient.ts)"]
    ActionRecorder["ActionRecorder<br/>(recorder/ActionRecorder.ts)"]
    SelectorOptimizer["SelectorOptimizer<br/>(optimizer/SelectorOptimizer.ts)"]
    RecorderToolExecutor["RecorderToolExecutor<br/>(tools/RecorderToolExecutor.ts)"]
    
    ActionRecorder -->|"chat(messages, tools)"| AIClient
    RecorderToolExecutor -->|Uses AIClient instance| ActionRecorder
    SelectorOptimizer -->|"Uses separate LLM instance<br/>(smaller model)"| VercelAISDK["Vercel AI SDK<br/>(generateText)"]
    
    AIClient -->|Wraps| OpenRouter["createOpenRouter()"]
    AIClient -->|Wraps| OpenAI["createOpenAI()"]
    AIClient -->|Wraps| Anthropic["createAnthropic()"]
    AIClient -->|Wraps| Bedrock["createAmazonBedrock()"]
    
    VercelAISDK --> OpenRouter
    VercelAISDK --> OpenAI
    VercelAISDK --> Anthropic
    VercelAISDK --> Bedrock
```

**Sources:** [services/action-builder/src/llm/AIClient.ts:1-10](), [services/action-builder/src/optimizer/SelectorOptimizer.ts:1-18]()

### ActionRecorder Integration Example

The `ActionRecorder` uses `AIClient` for multi-turn tool-calling loops:

```typescript
class ActionRecorder {
  private aiClient: AIClient;
  
  constructor() {
    this.aiClient = new AIClient();  // Auto-detects provider
  }
  
  async executeRecording() {
    const messages: OpenAI.Chat.Completions.ChatCompletionMessageParam[] = [
      { role: 'system', content: systemPrompt },
      { role: 'user', content: taskDescription },
    ];
    
    for (let turn = 0; turn < maxTurns; turn++) {
      const response = await this.aiClient.chat(messages, tools);
      
      // Handle tool calls...
      if (response.choices[0].message.tool_calls) {
        // Execute tools and append results to messages
      }
    }
  }
}
```

**Sources:** [services/action-builder/src/llm/AIClient.ts:343-421]()

---

## Configuration Examples

### OpenRouter (Recommended)

```bash
# Access to all models through single API key
export OPENROUTER_API_KEY="sk-or-..."
export OPENROUTER_MODEL="anthropic/claude-sonnet-4"  # Optional, uses default if not set
```

### OpenAI

```bash
export OPENAI_API_KEY="sk-..."
export OPENAI_MODEL="gpt-4o"  # Optional
```

### Anthropic

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
export ANTHROPIC_MODEL="claude-sonnet-4-5"  # Optional
```

### AWS Bedrock

```bash
export AWS_ACCESS_KEY_ID="AKIA..."
export AWS_SECRET_ACCESS_KEY="..."
export AWS_REGION="us-east-1"  # Optional, defaults to us-east-1
export AWS_BEDROCK_MODEL="anthropic.claude-3-5-sonnet-20241022-v2:0"  # Optional
```

### Proxy Configuration

```bash
# Applies to all providers
export HTTPS_PROXY="http://proxy.example.com:8080"
# or
export HTTP_PROXY="http://proxy.example.com:8080"
```

**Sources:** [services/action-builder/src/llm/AIClient.ts:101-171]()

---

## Related Components

`SelectorOptimizer` implements similar provider resolution logic but uses smaller/faster models (e.g., `gpt-4o-mini`, `claude-3-5-haiku-latest`) for cost efficiency. It also uses Vercel AI SDK directly rather than wrapping it in an OpenAI-compatible interface.

For usage of `AIClient` in the action recording workflow, see [Action Recording](#3.2.2).

**Sources:** [services/action-builder/src/optimizer/SelectorOptimizer.ts:95-153]()

---

# Page: Selector Optimizer

# Selector Optimizer

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.prettierignore](.prettierignore)
- [.prettierrc.json](.prettierrc.json)
- [CLAUDE.md](CLAUDE.md)
- [services/action-builder/scripts/login.ts](services/action-builder/scripts/login.ts)
- [services/action-builder/scripts/playbook-record.ts](services/action-builder/scripts/playbook-record.ts)
- [services/action-builder/src/optimizer/SelectorOptimizer.ts](services/action-builder/src/optimizer/SelectorOptimizer.ts)
- [services/action-builder/src/recorder/RecorderToolExecutor.ts](services/action-builder/src/recorder/RecorderToolExecutor.ts)
- [services/action-builder/src/validator/SelectorValidator.ts](services/action-builder/src/validator/SelectorValidator.ts)
- [services/action-builder/test/browser/xpath-optimizer.ut.test.ts](services/action-builder/test/browser/xpath-optimizer.ut.test.ts)
- [services/action-builder/test/validator/SelectorValidator.ut.test.ts](services/action-builder/test/validator/SelectorValidator.ut.test.ts)
- [services/common/browser-profile/package.json](services/common/browser-profile/package.json)
- [services/common/browser-profile/src/BrowserProfileManager.ts](services/common/browser-profile/src/BrowserProfileManager.ts)

</details>



## Purpose and Scope

The Selector Optimizer uses LLM-based analysis to improve the stability and reliability of discovered selectors. It identifies unstable patterns (dynamic counters, timestamps, framework-generated hashes) and reorders selectors based on their reliability. This page covers the optimization algorithm, stability analysis patterns, LLM integration, and batch processing workflow.

For information about how selectors are initially discovered and extracted, see [Action Recording](#3.2.2). For information about validating selectors after optimization, see [Selector Types](#7.2).

**Sources:** [services/action-builder/src/optimizer/SelectorOptimizer.ts:1-372]()

## Overview

The Selector Optimizer addresses a critical challenge in web automation: selectors that work initially but break over time due to dynamic content or framework-specific patterns. During element discovery, the system extracts multiple selectors per element ([services/action-builder/src/recorder/RecorderToolExecutor.ts:191-434]()), but not all selectors are equally reliable.

The optimizer performs three main functions:

1. **Stability Analysis**: Identifies selectors containing dynamic or unstable content
2. **Selector Ranking**: Reorders selectors by reliability, placing the most stable first
3. **Confidence Adjustment**: Updates confidence scores based on stability assessment

**Key Benefits:**
- Reduces selector brittleness across site updates
- Prioritizes semantic, test-friendly selectors (data-testid, aria-label)
- Detects framework-specific patterns that change on each build
- Batch processes multiple elements for efficiency

**Sources:** [services/action-builder/src/optimizer/SelectorOptimizer.ts:1-11]()

## Architecture

```mermaid
graph TB
    subgraph "Action Recording Phase"
        ElementDiscovery["Element Discovery<br/>(ActionRecorder)"]
        SelectorExtraction["Selector Extraction<br/>(extractMultipleSelectors)"]
    end
    
    subgraph "Selector Optimizer"
        SelectorOptimizer["SelectorOptimizer"]
        LLMProvider["LLM Provider<br/>(OpenRouter/OpenAI/Anthropic/Bedrock)"]
        StabilityAnalyzer["Stability Pattern Matching<br/>(System Prompt)"]
        ConfidenceAdjuster["Confidence Score Adjuster"]
    end
    
    subgraph "Output"
        OptimizedSelectors["OptimizedElement[]<br/>(reordered selectors)"]
        ConfidenceScores["Updated confidence scores"]
    end
    
    ElementDiscovery --> SelectorExtraction
    SelectorExtraction --> SelectorOptimizer
    
    SelectorOptimizer --> LLMProvider
    LLMProvider --> StabilityAnalyzer
    StabilityAnalyzer --> ConfidenceAdjuster
    ConfidenceAdjuster --> OptimizedSelectors
    ConfidenceAdjuster --> ConfidenceScores
    
    OptimizedSelectors --> ElementCapability["ElementCapability<br/>(stored in DB)"]
```

**Diagram: Selector Optimizer Architecture**

The optimizer is implemented as a standalone class that takes a batch of elements with their discovered selectors and returns optimized versions with adjusted priorities and confidence scores.

**Sources:** [services/action-builder/src/optimizer/SelectorOptimizer.ts:95-153](), [services/action-builder/src/optimizer/SelectorOptimizer.ts:158-278]()

## Selector Stability Patterns

The optimizer uses pattern-based analysis to classify selectors as stable or unstable. These patterns are encoded in the LLM system prompt and guide the analysis.

### Unstable Patterns

Selectors containing these patterns are marked with low confidence (0.1) as they change dynamically:

| Pattern Category | Examples | Detection Logic |
|-----------------|----------|-----------------|
| **Counters/Notifications** | `"0 条新通知"`, `"3 new messages"`, `"(5)"`, `"+99"` | Contains numeric badges or notification counts |
| **Timestamps** | `"2 minutes ago"`, `"刚刚"`, `"Yesterday"` | Contains relative time expressions |
| **User-specific IDs** | `"user-12345"`, `"profile-abc123"` | Contains user identifiers or session-specific values |
| **Framework-generated IDs** | `"#ember123"`, `"#react-xxx"`, `".ng-c123"`, `":r0:"`, `"#radix-123"` | React/Angular/Ember internal IDs |
| **CSS Module Hashes** | `".styles_button__x7y8z"`, `".Component_name__hash"` | CSS Modules pattern with hash suffix |
| **styled-components** | `".sc-1a2b3c"`, `".sc-aBcDeF"` | styled-components generated classes |
| **Emotion CSS** | `".css-1a2b3c"`, `".css-xxxxxx"` | Emotion CSS generated classes |
| **Generic Hash Patterns** | Classes ending with `_[a-z0-9]{5,}`, `__[a-z0-9]{5,}`, or `-[a-z0-9]{6,}` | Generic build-time hash suffixes |

**Sources:** [services/action-builder/src/optimizer/SelectorOptimizer.ts:283-316]()

### Stable Patterns

Selectors using these attributes are preferred for their reliability:

| Pattern Category | Examples | Priority | Confidence Range |
|-----------------|----------|----------|------------------|
| **data-testid** | `[data-testid="submit-btn"]` | 1 (Highest) | 0.90-0.95 |
| **Semantic data-*** | `[data-id="card-123"]`, `[data-component="header"]` | 2 | 0.85-0.90 |
| **ID selector** | `#main-nav`, `#search-button` | 3 | 0.85-0.95 |
| **Static aria-label** | `[aria-label="Submit"]`, `[aria-label="Close"]` | 4 | 0.80-0.85 |
| **BEM class names** | `.header__nav-item`, `.btn--primary` | 5 | 0.75-0.80 |
| **Semantic classes** | `.container`, `.navigation` | 6 | 0.70-0.75 |
| **XPath** | `//button[@name="email"]` | 7 (Lowest) | 0.60-0.70 |

**Selector Priority Logic:**
When all selectors are stable, the optimizer uses this priority order to determine which selector should be ranked first. `data-testid` is always preferred as it is explicitly designed for testing and rarely changes.

**Sources:** [services/action-builder/src/optimizer/SelectorOptimizer.ts:301-316]()

## LLM Provider Configuration

The optimizer supports multiple LLM providers with automatic provider detection based on available API keys.

```mermaid
graph LR
    ConfigResolver["resolveConfig()"]
    
    CheckOpenRouter["Check OPENROUTER_API_KEY"]
    CheckOpenAI["Check OPENAI_API_KEY"]
    CheckAnthropic["Check ANTHROPIC_API_KEY"]
    CheckBedrock["Check AWS credentials"]
    
    OpenRouterProvider["OpenRouter<br/>gpt-4o-mini"]
    OpenAIProvider["OpenAI<br/>gpt-4o-mini"]
    AnthropicProvider["Anthropic<br/>claude-3-5-haiku-latest"]
    BedrockProvider["Bedrock<br/>claude-3-5-haiku"]
    
    Error["Throw Error:<br/>No LLM API key found"]
    
    ConfigResolver --> CheckOpenRouter
    CheckOpenRouter -->|Found| OpenRouterProvider
    CheckOpenRouter -->|Not Found| CheckOpenAI
    CheckOpenAI -->|Found| OpenAIProvider
    CheckOpenAI -->|Not Found| CheckAnthropic
    CheckAnthropic -->|Found| AnthropicProvider
    CheckAnthropic -->|Not Found| CheckBedrock
    CheckBedrock -->|Found| BedrockProvider
    CheckBedrock -->|Not Found| Error
```

**Diagram: LLM Provider Resolution Order**

### Provider Priority

The configuration resolver checks for API keys in this order:

1. **OpenRouter** (`OPENROUTER_API_KEY`) - Default model: `gpt-4o-mini`
2. **OpenAI** (`OPENAI_API_KEY`) - Default model: `gpt-4o-mini`
3. **Anthropic** (`ANTHROPIC_API_KEY`) - Default model: `claude-3-5-haiku-latest`
4. **Bedrock** (`AWS_ACCESS_KEY_ID` + `AWS_SECRET_ACCESS_KEY`) - Default model: `anthropic.claude-3-5-haiku-20241022-v1:0`

**Model Override:**
Set `SELECTOR_OPTIMIZER_MODEL` environment variable to use a different model. The optimizer uses smaller/faster models by default since selector analysis doesn't require the most powerful models.

**Proxy Support:**
The optimizer automatically detects `HTTPS_PROXY` or `HTTP_PROXY` environment variables and routes LLM requests through the configured proxy using undici's `ProxyAgent`.

**Sources:** [services/action-builder/src/optimizer/SelectorOptimizer.ts:98-153](), [services/action-builder/src/optimizer/SelectorOptimizer.ts:71-93]()

## Input and Output Format

### SelectorInput

Input format for a single element to optimize:

```typescript
interface SelectorInput {
  elementId: string           // Element identifier
  description: string         // Human-readable element description
  selectors: SelectorItem[]   // Array of discovered selectors
}
```

Each `SelectorItem` contains:
- `type`: Selector type (css, xpath, id, data-testid, aria-label, placeholder)
- `value`: Selector string value
- `priority`: Current priority (1 = highest)
- `confidence`: Current confidence score (0.0-1.0)
- `isTemplate`: Whether selector uses template parameters
- `templateParams`: Template parameter definitions (if applicable)

**Sources:** [services/action-builder/src/optimizer/SelectorOptimizer.ts:23-28]()

### SelectorAnalysisResult

LLM output format for each element:

```typescript
interface SelectorAnalysisResult {
  elementId: string
  bestSelectorIndex: number          // Index of best selector (0-based)
  unstableSelectorIndices: number[]  // Indices of all unstable selectors
  reason: string                     // Explanation of choice
  adjustedConfidence?: number        // New confidence for best selector
}
```

**Example LLM Response:**
```json
[
  {
    "elementId": "search_button",
    "bestSelectorIndex": 1,
    "unstableSelectorIndices": [0, 3],
    "reason": "data-testid is most stable; CSS class contains hash; placeholder text is dynamic",
    "adjustedConfidence": 0.92
  }
]
```

**Sources:** [services/action-builder/src/optimizer/SelectorOptimizer.ts:32-39]()

### OptimizationResult

Final output from the optimizer:

```typescript
interface OptimizationResult {
  success: boolean
  optimizedCount: number
  totalElements: number
  elements: OptimizedElement[]
  tokensUsed: {
    input: number
    output: number
    total: number
  }
  error?: string
}
```

Each `OptimizedElement` contains:
- `elementId`: Element identifier
- `originalSelectors`: Pre-optimization selector array
- `optimizedSelectors`: Post-optimization selector array (reordered with updated confidence)
- `reason`: Explanation from LLM analysis

**Sources:** [services/action-builder/src/optimizer/SelectorOptimizer.ts:44-65]()

## Optimization Process

```mermaid
sequenceDiagram
    participant AR as "ActionRecorder"
    participant SO as "SelectorOptimizer"
    participant LLM as "LLM Provider"
    participant EC as "ElementCapability Map"
    
    AR->>EC: Store discovered elements<br/>(multiple selectors each)
    AR->>SO: optimizeSelectors(elements)
    
    Note over SO: Prepare batch input
    SO->>SO: Map elements to SelectorInput[]
    
    SO->>LLM: generateText()<br/>(system prompt + element data)
    Note over LLM: Analyze stability patterns<br/>Rank selectors<br/>Adjust confidence
    
    LLM-->>SO: SelectorAnalysisResult[]
    
    Note over SO: Apply optimizations
    loop For each analysis result
        SO->>SO: Mark unstable selectors<br/>(confidence = 0.1)
        SO->>SO: Move best selector to index 0
        SO->>SO: Update priorities (1, 2, 3...)
        SO->>SO: Adjust confidence score
    end
    
    SO->>EC: Update ElementCapability.selectors
    SO-->>AR: OptimizationResult
```

**Diagram: Optimization Sequence**

### Step-by-Step Process

1. **Batch Preparation** ([services/action-builder/src/optimizer/SelectorOptimizer.ts:178-183]())
   - Convert `Map<string, ElementCapability>` to `SelectorInput[]`
   - Include element ID, description, and all selectors

2. **LLM Analysis** ([services/action-builder/src/optimizer/SelectorOptimizer.ts:280-369]())
   - System prompt defines stability patterns and priority rules
   - User prompt provides element data in JSON format
   - Temperature set to 0.1 for consistent analysis
   - Response parsed from JSON (handles markdown code blocks)

3. **Unstable Marking** ([services/action-builder/src/optimizer/SelectorOptimizer.ts:199-209]())
   - For each index in `unstableSelectorIndices`, set `confidence = 0.1`
   - Logs warning for each unstable selector detected

4. **Selector Reordering** ([services/action-builder/src/optimizer/SelectorOptimizer.ts:212-241]())
   - Move `bestSelectorIndex` to position 0 (highest priority)
   - Update `priority` field: best=1, others=2,3,4...
   - Apply `adjustedConfidence` to best selector

5. **Result Collection** ([services/action-builder/src/optimizer/SelectorOptimizer.ts:243-248]())
   - Create `OptimizedElement` with before/after selectors
   - Include LLM's reasoning for audit trail

**Sources:** [services/action-builder/src/optimizer/SelectorOptimizer.ts:158-278]()

## Integration Points

### Action Recording Integration

The optimizer is called after element discovery completes in the ActionRecorder:

```mermaid
graph TB
    ObservePage["observe_page tool"]
    RegisterElement["register_element tool"]
    ElementMap["elements Map"]
    Optimizer["SelectorOptimizer.optimizeSelectors()"]
    SaveToDB["Save to database"]
    
    ObservePage --> RegisterElement
    RegisterElement --> ElementMap
    ElementMap --> Optimizer
    Optimizer --> SaveToDB
```

**Diagram: Action Recording Integration Flow**

The optimizer receives the complete set of discovered elements before they are persisted to the database, ensuring all stored selectors have been analyzed for stability.

**Sources:** [services/action-builder/src/recorder/RecorderToolExecutor.ts:191-434]()

### Database Persistence

After optimization, the reordered selectors are stored in the `elements` table with the following structure:

| Field | Description |
|-------|-------------|
| `selectors` | JSONB array of `SelectorItem[]` (post-optimization) |
| `element_type` | Element type inferred from interactions |
| `allow_methods` | Permitted interaction methods |
| `discovered_at` | Timestamp of discovery |

The optimized selector order persists through the API and is returned to consumers in priority order, ensuring clients try the most stable selector first.

**Sources:** [services/action-builder/src/optimizer/SelectorOptimizer.ts:158-278]()

## Error Handling

The optimizer includes comprehensive error handling:

| Error Condition | Behavior |
|----------------|----------|
| **No API keys configured** | Throws error during constructor: `"No LLM API key found for SelectorOptimizer"` |
| **LLM call failure** | Catches error, logs message, returns `OptimizationResult` with `success: false` |
| **JSON parse error** | Catches error, logs message, returns failed result |
| **Empty element list** | Returns success with `optimizedCount: 0` (no-op) |
| **Missing elementId in results** | Skips that element, continues processing others |
| **Invalid bestSelectorIndex** | Skips reordering, only marks unstable selectors |

The optimizer is designed to be non-blocking: if optimization fails, the action recording can still succeed with the original un-optimized selectors.

**Sources:** [services/action-builder/src/optimizer/SelectorOptimizer.ts:263-277](), [services/action-builder/src/optimizer/SelectorOptimizer.ts:150-153]()

## Performance Considerations

**Batch Processing:**
The optimizer processes all elements in a single LLM call rather than making individual requests per element. For a typical page with 20-30 elements, this reduces:
- API calls: from 20-30 to 1
- Total latency: from 20-60 seconds to 2-5 seconds
- Cost: proportional reduction in API charges

**Model Selection:**
Default models are optimized for speed and cost:
- `gpt-4o-mini`: Fast, inexpensive, sufficient for pattern matching
- `claude-3-5-haiku-latest`: Fast, good reasoning for selector analysis

Override with `SELECTOR_OPTIMIZER_MODEL` if more sophisticated analysis is needed.

**Latency Logging:**
The optimizer logs LLM call duration for monitoring: `[SelectorOptimizer] LLM call completed in {latencyMs}ms`

**Sources:** [services/action-builder/src/optimizer/SelectorOptimizer.ts:339-352](), [services/action-builder/src/optimizer/SelectorOptimizer.ts:118-149]()

---

# Page: Capability Discovery

# Capability Discovery

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [services/action-builder/scripts/playbook-record.ts](services/action-builder/scripts/playbook-record.ts)
- [services/action-builder/src/recorder/RecorderToolExecutor.ts](services/action-builder/src/recorder/RecorderToolExecutor.ts)
- [services/action-builder/src/task-worker/utils/prompt-builder.ts](services/action-builder/src/task-worker/utils/prompt-builder.ts)
- [services/action-builder/src/validator/SelectorValidator.ts](services/action-builder/src/validator/SelectorValidator.ts)
- [services/action-builder/test/browser/xpath-optimizer.ut.test.ts](services/action-builder/test/browser/xpath-optimizer.ut.test.ts)
- [services/action-builder/test/validator/SelectorValidator.ut.test.ts](services/action-builder/test/validator/SelectorValidator.ut.test.ts)
- [services/db/src/models/build-task.ts](services/db/src/models/build-task.ts)
- [services/playbook-builder/scripts/worker.ts](services/playbook-builder/scripts/worker.ts)
- [services/playbook-builder/src/analyzer/page-analyzer.ts](services/playbook-builder/src/analyzer/page-analyzer.ts)
- [services/playbook-builder/src/controller/playbook-task-controller.ts](services/playbook-builder/src/controller/playbook-task-controller.ts)
- [services/playbook-builder/src/discoverer/capabilities-discoverer.ts](services/playbook-builder/src/discoverer/capabilities-discoverer.ts)
- [services/playbook-builder/src/discoverer/page-discoverer.ts](services/playbook-builder/src/discoverer/page-discoverer.ts)
- [services/playbook-builder/src/playbook-builder.ts](services/playbook-builder/src/playbook-builder.ts)
- [services/playbook-builder/src/types/index.ts](services/playbook-builder/src/types/index.ts)

</details>



## Purpose and Scope

Capability Discovery is the AI-driven process of identifying interactive UI elements and page structures on websites. This page covers how Actionbook uses LLM vision models to discover elements, extract multiple stable selectors, and generate comprehensive page documentation.

For selector stability analysis and optimization after discovery, see [Selector Optimizer](#6.2). For the task execution pipeline that orchestrates capability discovery, see [Action Recording](#3.2.2).

---

## Discovery Architecture

Capability discovery operates at two levels: **element-level** (finding individual UI components) and **page-level** (understanding page structure and purpose). Both leverage LLM vision capabilities to analyze screenshots and HTML content.

### Discovery Flow Diagram

```mermaid
graph TB
    subgraph "Element Discovery Flow"
        ObserveTool["observe_page tool<br/>(RecorderToolExecutor)"]
        BrowserObserve["BrowserAdapter.observe()<br/>(Stagehand/AgentCore)"]
        LLMVision["LLM Vision Model<br/>(GPT-4V/Claude)"]
        ObserveResults["ObserveResultItem[]<br/>(selector + description)"]
        
        ObserveTool --> BrowserObserve
        BrowserObserve --> LLMVision
        LLMVision --> ObserveResults
    end
    
    subgraph "Element Registration Flow"
        RegisterTool["register_element tool<br/>(RecorderToolExecutor)"]
        ExtractSelectors["extractMultipleSelectors()<br/>(handlers)"]
        GetAttributes["getElementAttributesFromXPath()<br/>(BrowserAdapter)"]
        MultiSelectors["SelectorItem[]<br/>(id, data-testid, aria-label, css, xpath)"]
        TemplateDetect["detectTemplatePattern()<br/>(handlers)"]
        
        RegisterTool --> GetAttributes
        GetAttributes --> ExtractSelectors
        ExtractSelectors --> TemplateDetect
        TemplateDetect --> MultiSelectors
    end
    
    subgraph "Page Discovery Flow"
        PageDiscoverer["PageDiscoverer<br/>(playbook-builder)"]
        CapabilitiesDiscoverer["CapabilitiesDiscoverer<br/>(playbook-builder)"]
        PlaybookDoc["7-Section Playbook<br/>(Markdown)"]
        
        PageDiscoverer --> CapabilitiesDiscoverer
        CapabilitiesDiscoverer --> PlaybookDoc
    end
    
    ObserveResults --> RegisterTool
    MultiSelectors --> ElementCapability["ElementCapability<br/>(saved to DB)"]
    PlaybookDoc --> ChunksTable["chunks table<br/>(with embeddings)"]
```

**Sources:** [services/action-builder/src/recorder/RecorderToolExecutor.ts:122-150](), [services/playbook-builder/src/discoverer/page-discoverer.ts:1-192](), [services/playbook-builder/src/discoverer/capabilities-discoverer.ts:1-246]()

---

## Element Discovery with observe_page

The `observe_page` tool uses LLM vision capabilities to identify interactive elements on a webpage. The LLM analyzes screenshots and DOM structure to locate elements matching a given focus description.

### Tool Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `focus` | string | Natural language description of what to observe (e.g., "search bar and filters") |
| `_timeoutMs` | number (optional) | Timeout for observation operation |

### Execution Flow

```mermaid
sequenceDiagram
    participant LLM as "LLM Agent"
    participant RTE as "RecorderToolExecutor"
    participant BA as "BrowserAdapter"
    participant Vision as "Vision Model"
    
    LLM->>RTE: observe_page({focus: "search button"})
    RTE->>BA: observe("search button", timeout)
    BA->>Vision: Screenshot + HTML + focus
    Vision->>BA: Element matches with selectors
    BA->>RTE: ObserveResultItem[]
    Note over RTE: [{description, selector, method}]
    RTE->>LLM: {elements_found: N, elements: [...]}
```

### ObserveResultItem Structure

Each discovered element returns:
- `description`: Natural language description of the element
- `selector`: XPath or CSS selector (usually starts with `xpath=`)
- `method`: Suggested interaction method (e.g., `"click"`, `"type"`)

**Sources:** [services/action-builder/src/recorder/RecorderToolExecutor.ts:122-150](), [packages/browser/src/interfaces.ts]()

---

## Element Registration with register_element

The `register_element` tool records element capabilities with multiple stable selectors. It automatically extracts additional selectors beyond what the LLM provides, ensuring redundancy for robustness.

### Selector Priority Hierarchy

The system builds a multi-selector array with priority ordering:

| Priority | Selector Type | Confidence | Example |
|----------|--------------|------------|---------|
| 1 | `id` | 0.95 | `[id="submit-btn"]` |
| 2 | `data-testid` | 0.90 | `[data-testid="checkout"]` |
| 3 | `aria-label` | 0.85 | `[aria-label="Close"]` |
| 4 | `css` | 0.75 | `.btn.btn-primary` |
| 5 | `xpath` (optimized) | 0.80 | `//button[@name="submit"]` |
| 5 | `xpath` (absolute) | 0.60 | `/html[1]/body[1]/div[3]/button[1]` |
| 6 | `placeholder` | 0.65 | `[placeholder="Enter email"]` |

### Automatic Selector Extraction

When `register_element` is called, the system automatically extracts multiple selectors:

```mermaid
graph LR
    XPath["XPath from LLM/observe"]
    GetAttrs["getElementAttributesFromXPath()"]
    Extracted["Extracted Attributes:<br/>- id<br/>- data-testid<br/>- aria-label<br/>- placeholder<br/>- cssSelector<br/>- optimizedXPath"]
    BuildMulti["extractMultipleSelectors()"]
    SelectorArray["SelectorItem[]<br/>(priority ordered)"]
    
    XPath --> GetAttrs
    GetAttrs --> Extracted
    Extracted --> BuildMulti
    BuildMulti --> SelectorArray
```

**Key Implementation Details:**

1. **XPath Extraction** ([services/action-builder/src/recorder/RecorderToolExecutor.ts:330-348]()):
   - Calls `browser.getElementAttributesFromXPath()` to extract all available attributes
   - Retrieves `id`, `dataTestId`, `ariaLabel`, `placeholder`, `cssSelector`, and `optimizedXPath`

2. **Selector Building** ([services/action-builder/src/recorder/RecorderToolExecutor.ts:351-434]()):
   - ID selectors use `createIdSelector()` to handle special characters (e.g., dots in IDs)
   - data-testid formatted as `[data-testid="value"]`
   - aria-label formatted as `[aria-label="value"]`
   - CSS selectors checked for template patterns
   - XPath prefers optimized attribute-based over absolute path

3. **No-Selector Handling** ([services/action-builder/src/recorder/RecorderToolExecutor.ts:436-446]()):
   - If no selectors found, returns error message
   - Element is skipped with informative feedback to LLM
   - Prevents "phantom elements" (elements LLM thinks exist but don't)

**Sources:** [services/action-builder/src/recorder/RecorderToolExecutor.ts:275-476](), [packages/browser/src/StagehandBrowser.ts]()

---

## Multi-Selector Extraction Strategy

The `extractMultipleSelectors` handler function converts a single observed element into a redundant selector array. This provides fallback options when the primary selector fails due to DOM changes.

### Extraction Logic

```mermaid
graph TB
    Input["Input: ObserveResultItem<br/>+ additionalAttributes"]
    
    subgraph "Priority 1: ID Selectors"
        CheckID{"id attribute?"}
        CreateID["createIdSelector(id)<br/>(handles dots)"]
        IDSelector["SelectorItem<br/>(type: id, priority: 1)"]
    end
    
    subgraph "Priority 2: Test IDs"
        CheckTestID{"data-testid?"}
        TestIDSelector["SelectorItem<br/>(type: data-testid, priority: 2)"]
    end
    
    subgraph "Priority 3: Aria Labels"
        CheckAria{"aria-label?"}
        AriaSelector["SelectorItem<br/>(type: aria-label, priority: 3)"]
    end
    
    subgraph "Priority 4: CSS"
        CheckCSS{"cssSelector?"}
        TemplateCheck{"Template pattern?"}
        TemplateSel["SelectorItem<br/>(isTemplate: true)"]
        CSSSelector["SelectorItem<br/>(type: css, priority: 4)"]
    end
    
    subgraph "Priority 5: XPath"
        CheckXPath{"XPath?"}
        XPathSelector["SelectorItem<br/>(type: xpath, priority: 5)"]
    end
    
    subgraph "Priority 6: Placeholder"
        CheckPlaceholder{"placeholder?"}
        PlaceholderSel["SelectorItem<br/>(type: placeholder, priority: 6)"]
    end
    
    Input --> CheckID
    CheckID -->|Yes| CreateID --> IDSelector
    CheckID -->|No| CheckTestID
    CheckTestID -->|Yes| TestIDSelector
    CheckTestID -->|No| CheckAria
    CheckAria -->|Yes| AriaSelector
    CheckAria -->|No| CheckCSS
    CheckCSS -->|Yes| TemplateCheck
    TemplateCheck -->|Yes| TemplateSel
    TemplateCheck -->|No| CSSSelector
    CheckCSS -->|No| CheckXPath
    CheckXPath -->|Yes| XPathSelector
    CheckXPath -->|No| CheckPlaceholder
    CheckPlaceholder -->|Yes| PlaceholderSel
    
    IDSelector --> Output["SelectorItem[]"]
    TestIDSelector --> Output
    AriaSelector --> Output
    TemplateSel --> Output
    CSSSelector --> Output
    XPathSelector --> Output
    PlaceholderSel --> Output
```

### Special Handling: ID with Special Characters

IDs containing dots (e.g., `"cs.AI"`) require CSS attribute selector syntax:

```javascript
// Input: id = "cs.AI"
// Output: [id="cs.AI"]  (not #cs.AI which would fail)
```

Implementation: [services/action-builder/src/recorder/RecorderToolExecutor.ts:354-370]()

**Sources:** [services/action-builder/src/recorder/RecorderToolExecutor.ts:16-26](), [services/action-builder/src/utils/string.ts]()

---

## Template Pattern Detection

The `detectTemplatePattern` handler identifies CSS selectors with dynamic segments (e.g., `nth-child(3)`, `[data-id="123"]`) and converts them to parameterized templates for reusable patterns.

### Template Detection Algorithm

```mermaid
graph TB
    Input["CSS Selector<br/>(e.g., ul > li:nth-child(3))"]
    
    CheckNth{"Contains<br/>:nth-child?"}
    ExtractNth["Extract child index<br/>as {{index}} param"]
    
    CheckDataID{"Contains<br/>[data-id='value']?"}
    ExtractDataID["Extract value<br/>as {{id}} param"]
    
    CheckOther{"Other dynamic<br/>patterns?"}
    ExtractOther["Extract as<br/>template params"]
    
    NoTemplate["No template<br/>return null"]
    
    BuildTemplate["Build template:<br/>- Replace values with {{param}}<br/>- Create TemplateParam[]"]
    
    Output["Template Result:<br/>{template: string,<br/>params: TemplateParam[]}"]
    
    Input --> CheckNth
    CheckNth -->|Yes| ExtractNth --> BuildTemplate
    CheckNth -->|No| CheckDataID
    CheckDataID -->|Yes| ExtractDataID --> BuildTemplate
    CheckDataID -->|No| CheckOther
    CheckOther -->|Yes| ExtractOther --> BuildTemplate
    CheckOther -->|No| NoTemplate
    
    BuildTemplate --> Output
```

### Template Example

**Original CSS Selector:**
```
ul.items > li:nth-child(3) > a
```

**Template Conversion:**
```typescript
{
  template: "ul.items > li:nth-child({{index}}) > a",
  params: [{
    name: "index",
    type: "number",
    description: "List item index"
  }]
}
```

This allows the selector to match any list item by substituting the `{{index}}` parameter.

**Sources:** [services/action-builder/src/recorder/RecorderToolExecutor.ts:28-30](), [services/action-builder/src/types/index.ts]()

---

## Page Discovery (Playbook Builder)

The playbook-builder service uses two discoverers to understand website structure:

### Component Overview

| Component | Purpose | Input | Output |
|-----------|---------|-------|--------|
| `PageDiscoverer` | Find navigable pages | Screenshot + HTML + current URL | `DiscoveredPage[]` |
| `CapabilitiesDiscoverer` | Generate page playbook | Screenshot + HTML + page name | `PageCapabilities` (with 7-section Playbook) |

### PageDiscoverer Workflow

```mermaid
sequenceDiagram
    participant PB as "PlaybookBuilder"
    participant PD as "PageDiscoverer"
    participant AI as "AIClient"
    participant Tool as "register_discovered_pages"
    
    PB->>PD: discover(screenshot, html, currentUrl)
    PD->>PD: extractNavigationHtml(html)
    Note over PD: Extract nav, header, footer, links
    PD->>AI: chat(messages, [discoverPagesTool])
    Note over AI: System prompt:<br/>PAGE_DISCOVERY_SYSTEM_PROMPT
    AI->>Tool: register_discovered_pages({pages: [...]})
    Tool->>PD: DiscoveredPage[]
    PD->>PD: normalizeUrls(pages)
    PD->>PB: DiscoveredPage[]
```

### DiscoveredPage Structure

Each discovered page includes:
- `semanticId`: Snake_case identifier (e.g., `"search_results"`, `"listing_detail"`)
- `name`: Human-readable name
- `description`: Brief description of page purpose
- `url`: Absolute URL to the page
- `navigation`: Optional instructions on how to reach the page
- `depth`: Discovery depth (0 = start page, 1 = discovered from start, etc.)

**Sources:** [services/playbook-builder/src/discoverer/page-discoverer.ts:1-192](), [services/playbook-builder/src/types/index.ts:36-51]()

---

## Capabilities Discovery (7-Section Playbook)

The `CapabilitiesDiscoverer` generates comprehensive page documentation in a standardized 7-section format. This Playbook guides AI agents in understanding, parsing, and interacting with pages.

### Playbook Structure

| Section | Content | Purpose |
|---------|---------|---------|
| 0. Page URL | URL structure, query params, dynamic params | Understanding navigation |
| 1. Page Overview | Core business objective (1 sentence) | Quick purpose identification |
| 2. Page Function Summary | List of functions/capabilities | What users can DO |
| 3. Page Structure Summary | Layout modules (header, sidebar, main) + CSS selectors | DOM structure at macro level |
| 4. DOM Structure Instance | Pattern recognition, HTML snippets | Detailed DOM patterns |
| 5. Parsing & Processing Summary | Data retrieval scenarios (direct/interaction/implicit) | How to extract data |
| 6. Operation Summary | Interactive operations (input/click/hover) + selectors | How to interact |

### Playbook Generation Flow

```mermaid
graph TB
    Input["Input:<br/>- screenshot (Buffer)<br/>- htmlContent (string)<br/>- pageName (string)<br/>- pageUrl (optional)"]
    
    Simplify["getSimplifiedHTML()<br/>Remove scripts, styles,<br/>SVG, images"]
    
    BuildPrompt["Build user prompt:<br/>- URL context<br/>- Page title<br/>- Simplified HTML<br/>- Custom prompt (optional)"]
    
    LLMCall["AIClient.chat()<br/>System: PLAYBOOK_SYSTEM_PROMPT<br/>User: [image + text]<br/>Tools: [] (no tools)"]
    
    Parse["Parse response:<br/>- Extract Section 1 (description)<br/>- Extract Section 2 (capabilities)<br/>- Full playbook markdown"]
    
    Output["PageCapabilities:<br/>- description (string)<br/>- capabilities (string[])<br/>- playbook (markdown)"]
    
    Input --> Simplify
    Simplify --> BuildPrompt
    BuildPrompt --> LLMCall
    LLMCall --> Parse
    Parse --> Output
```

### Key Implementation Notes

1. **No Tool Calling** ([services/playbook-builder/src/discoverer/capabilities-discoverer.ts:136-138]()):
   - Uses direct LLM response (no function calls)
   - LLM generates markdown directly following the 7-section template

2. **HTML Simplification** ([services/playbook-builder/src/discoverer/capabilities-discoverer.ts:170-190]()):
   - Removes `<script>`, `<style>`, `<svg>`, `<img>`, `<iframe>`, `<video>`, `<audio>`
   - Removes inline styles
   - Removes data-* attributes except `data-testid`
   - Limits to ~20KB for token efficiency

3. **Content Extraction** ([services/playbook-builder/src/discoverer/capabilities-discoverer.ts:192-233]()):
   - Section 1 (Overview) extracted via regex matching `### 1. Page Overview`
   - Section 2 (Functions) extracted to populate `capabilities` array
   - Full playbook stored as markdown string

**Sources:** [services/playbook-builder/src/discoverer/capabilities-discoverer.ts:1-246](), [services/playbook-builder/src/playbook-builder.ts:123-145]()

---

## Integration with Action Recording

Capability discovery integrates with the action recording pipeline to enable efficient element registration during task execution.

### Task-Driven Discovery

In task-driven mode, the LLM executes navigation steps while discovering elements:

```mermaid
graph LR
    Navigate["navigate tool"]
    SetContext["set_page_context tool"]
    Observe["observe_page tool"]
    Register["register_element tool"]
    Interact["interact tool<br/>(for navigation only)"]
    
    Navigate --> SetContext
    SetContext --> Observe
    Observe --> Register
    Observe --> Interact
    Interact --> Observe
```

**Workflow:**
1. Navigate to page
2. Set page context (page type, name)
3. Observe specific areas (e.g., "search bar", "filters")
4. Register elements WITHOUT clicking (fast)
5. Use interact ONLY for navigation clicks
6. Repeat on new pages

### Exploratory Discovery

In exploratory mode, the LLM analyzes page content and records all interactive elements:

```mermaid
graph LR
    Navigate["navigate tool"]
    SetContext["set_page_context tool"]
    Batch["Batch observe_page<br/>(multiple focus areas)"]
    BatchRegister["Batch register_element<br/>(parallel tool calls)"]
    
    Navigate --> SetContext
    SetContext --> Batch
    Batch --> BatchRegister
```

**Optimization:**
- Focus on specific areas instead of "all interactive elements"
- Batch multiple tool calls in single turn
- Prioritize pattern registration for repeating elements

**Sources:** [services/action-builder/src/task-worker/utils/prompt-builder.ts:1-331](), [services/action-builder/scripts/playbook-record.ts:1-247]()

---

## Real-World Example: Multi-Step Discovery

This example demonstrates how capability discovery works for a search results page:

### Step 1: Initial Observation

```
Tool: observe_page
Args: { focus: "search filters and sorting controls" }

Result: {
  elements_found: 8,
  elements: [
    { description: "Price range filter", selector: "xpath=//div[@data-testid='price-filter']", method: "click" },
    { description: "Sort by dropdown", selector: "xpath=//select[@aria-label='Sort results']", method: "select" },
    { description: "Category filter checkbox", selector: "xpath=//input[@name='category']", method: "click" },
    ...
  ]
}
```

### Step 2: Multi-Selector Registration

```
Tool: register_element
Args: {
  element_id: "price_range_filter",
  description: "Price range filter control",
  xpath_selector: "//div[@data-testid='price-filter']",
  element_type: "filter",
  allow_methods: ["click", "select"]
}

Internal Processing:
1. getElementAttributesFromXPath("//div[@data-testid='price-filter']")
   → { dataTestId: "price-filter", cssSelector: "div.filter-price", id: "priceFilter" }

2. extractMultipleSelectors()
   → [
       { type: "id", value: "[id='priceFilter']", priority: 1, confidence: 0.95 },
       { type: "data-testid", value: "[data-testid='price-filter']", priority: 2, confidence: 0.90 },
       { type: "css", value: "div.filter-price", priority: 3, confidence: 0.75 },
       { type: "xpath", value: "//div[@data-testid='price-filter']", priority: 4, confidence: 0.80 }
     ]

3. Save to database with all selectors
```

### Step 3: Template Pattern Detection

```
Tool: register_element
Args: {
  element_id: "listing_card",
  description: "Property listing card",
  css_selector: "div.listings > div.card:nth-child(3)",
  is_repeating: true
}

Internal Processing:
1. detectTemplatePattern("div.listings > div.card:nth-child(3)")
   → { 
       template: "div.listings > div.card:nth-child({{index}})",
       params: [{ name: "index", type: "number", description: "Card position" }]
     }

2. Save with isTemplate: true and templateParams
```

**Sources:** [services/action-builder/src/recorder/RecorderToolExecutor.ts:122-476](), [services/action-builder/test/browser/xpath-optimizer.ut.test.ts:293-300]()

---

## Validation Integration

After capability discovery, the [SelectorValidator](#2.1) validates all discovered selectors to ensure they work correctly on the live page. The validator checks:

- **Existence**: Selector finds the element
- **Visibility**: Element is visible on page
- **Interactability**: Element is enabled and not obstructed

Validation results inform the [Selector Optimizer](#6.2), which uses LLM analysis to adjust confidence scores for unstable selectors.

**Validation Flow:**
```mermaid
graph LR
    Discovery["Capability Discovery"]
    Save["Save ElementCapability"]
    Validate["SelectorValidator.validate()"]
    Optimize["SelectorOptimizer.optimize()"]
    Final["Final confidence scores"]
    
    Discovery --> Save
    Save --> Validate
    Validate --> Optimize
    Optimize --> Final
```

**Sources:** [services/action-builder/src/validator/SelectorValidator.ts:273-309](), [services/action-builder/src/validator/SelectorValidator.ts:311-488]()

---

# Page: Data Models and Types

# Data Models and Types

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [packages/js-sdk/src/api-client.ts](packages/js-sdk/src/api-client.ts)
- [packages/js-sdk/src/client.ts](packages/js-sdk/src/client.ts)
- [packages/js-sdk/src/tool-defs.ts](packages/js-sdk/src/tool-defs.ts)
- [packages/js-sdk/src/types.ts](packages/js-sdk/src/types.ts)
- [services/action-builder/src/recorder/RecorderTools.ts](services/action-builder/src/recorder/RecorderTools.ts)
- [services/action-builder/src/types/capability.ts](services/action-builder/src/types/capability.ts)
- [services/action-builder/src/utils/index.ts](services/action-builder/src/utils/index.ts)
- [services/action-builder/src/utils/url-matcher.ts](services/action-builder/src/utils/url-matcher.ts)
- [services/action-builder/test/recorder/RecorderTools.ut.test.ts](services/action-builder/test/recorder/RecorderTools.ut.test.ts)
- [services/action-builder/test/types/capability.ut.test.ts](services/action-builder/test/types/capability.ut.test.ts)
- [services/action-builder/test/utils/url-matcher.ut.test.ts](services/action-builder/test/utils/url-matcher.ut.test.ts)

</details>



## Purpose and Scope

This document provides a comprehensive reference for the core type definitions used throughout the Actionbook system. These types form the foundation for:

- **Capability Models**: Hierarchical data structures representing website UI elements and pages
- **Selector System**: Multi-selector format with priority ordering and template support
- **Tool Definitions**: LLM-compatible tool schemas for SDK and MCP integration
- **API Types**: Request/response formats for the REST API

For information about how these types are used in the recording process, see [Action Recording](#3.2.2). For database schema details, see [Database Schema](#5.1). For tool implementation, see [Recording Tools Reference](#3.2.3).

---

## Capability Type Hierarchy

The capability system uses a three-level hierarchy to organize website UI information:

### Type Relationship Diagram

```mermaid
graph TB
    SiteCapability["SiteCapability"]
    PageCapability["PageCapability"]
    ElementCapability["ElementCapability"]
    SelectorItem["SelectorItem[]"]
    
    SiteCapability -->|"pages: Record<string, PageCapability>"| PageCapability
    SiteCapability -->|"global_elements: Record<string, ElementCapability>"| ElementCapability
    PageCapability -->|"elements: Record<string, ElementCapability>"| ElementCapability
    ElementCapability -->|"selectors: SelectorItem[]"| SelectorItem
    
    subgraph "Element Relationships"
        Parent["parent: string"]
        DependsOn["depends_on: string"]
        Children["children: string[]"]
    end
    
    ElementCapability -.->|"optional"| Parent
    ElementCapability -.->|"optional"| DependsOn
    ElementCapability -.->|"optional"| Children
```

**Sources:** [services/action-builder/src/types/capability.ts:1-156]()

### SiteCapability

The root aggregate representing an entire website's capabilities.

| Field | Type | Description |
|-------|------|-------------|
| `domain` | `string` | Website domain (e.g., "example.com") |
| `name` | `string` | Human-readable site name |
| `description` | `string` | Site description |
| `version` | `string` | Version identifier for the capability set |
| `recorded_at` | `string` | ISO timestamp of when capabilities were recorded |
| `scenario` | `string` | Recording scenario description |
| `health_score` | `number?` | Optional health score (0-100) |
| `global_elements` | `Record<string, ElementCapability>` | Elements present across all pages (e.g., header, footer) |
| `pages` | `Record<string, PageCapability>` | Page-specific capabilities indexed by page_type |

**Sources:** [services/action-builder/src/types/capability.ts:143-155]()

### PageCapability

Represents a specific page type within a website (e.g., search results, product detail).

| Field | Type | Description |
|-------|------|-------------|
| `page_type` | `string` | Page type identifier (e.g., "home", "search_results") |
| `name` | `string` | Human-readable page name |
| `description` | `string` | Page description |
| `url_patterns` | `string[]` | Regex patterns for matching URLs to this page type |
| `wait_for` | `string?` | Optional selector to wait for before considering page loaded |
| `elements` | `Record<string, ElementCapability>` | Elements specific to this page type |

**Sources:** [services/action-builder/src/types/capability.ts:130-140]()

### ElementCapability

The most granular level, representing a single UI element with its selectors and interaction methods.

| Field | Type | Description |
|-------|------|-------------|
| `id` | `string` | Unique element identifier (snake_case) |
| `selectors` | `SelectorItem[]` | Multi-selector array with priority ordering |
| `description` | `string` | Human-readable element description |
| `element_type` | `ElementType` | Element classification (button, input, link, etc.) |
| `allow_methods` | `AllowMethod[]` | Permitted interaction methods |
| `arguments` | `ArgumentDef[]?` | Optional arguments for parameterized actions |
| `leads_to` | `string?` | Page type this element navigates to |
| `wait_after` | `number?` | Milliseconds to wait after interaction |
| `confidence` | `number?` | Selector confidence score (0-1) |
| `discovered_at` | `string` | ISO timestamp of discovery |

**Additional Relationship Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `parent` | `string?` | Parent element ID (for hierarchical elements) |
| `depends_on` | `string?` | Element ID that must be interacted with first |
| `visibility_condition` | `string?` | Condition description for visibility |
| `is_repeating` | `boolean?` | True if element repeats in a list/table |
| `data_key` | `string?` | Data extraction key for data_field elements |
| `children` | `string[]?` | Child element IDs for containers |
| `module` | `PageModule?` | Page module location |

**Input-Specific Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `input_type` | `string?` | Input type (text, email, password, etc.) |
| `input_name` | `string?` | Name attribute |
| `input_value` | `string?` | Default/current value |

**Link-Specific Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `href` | `string?` | URL or pattern for link elements |

**Sources:** [services/action-builder/src/types/capability.ts:78-128]()

---

## Element Types and Enumerations

### ElementType Enum

Classification of UI elements by their semantic role:

```mermaid
graph LR
    subgraph "Interactive Types"
        button["button"]
        input["input"]
        link["link"]
        select["select"]
        checkbox["checkbox"]
        radio["radio"]
    end
    
    subgraph "Data Display Types"
        text["text"]
        data_field["data_field"]
        container["container"]
        list["list"]
        list_item["list_item"]
    end
    
    other["other"]
```

| Type | Purpose | Typical Allow Methods |
|------|---------|----------------------|
| `button` | Clickable action trigger | click, hover |
| `input` | Text input field | type, clear |
| `link` | Navigation link | click, hover |
| `select` | Dropdown selector | select, click |
| `checkbox` | Boolean toggle | click |
| `radio` | Single-choice option | click |
| `text` | Static text for reading | extract |
| `data_field` | Extractable data value | extract |
| `container` | Groups other elements | - |
| `list` | List container | scroll |
| `list_item` | Single list entry | click, extract |
| `other` | Uncategorized element | varies |

**Sources:** [services/action-builder/src/types/capability.ts:43-59]()

### AllowMethod Enum

Permitted interaction methods for elements:

| Method | Description | Typical Element Types |
|--------|-------------|----------------------|
| `click` | Mouse click interaction | button, link, checkbox, radio |
| `type` | Keyboard text input | input |
| `clear` | Clear input value | input |
| `scroll` | Scroll element into view | list, container |
| `hover` | Mouse hover | button, link |
| `select` | Select dropdown option | select |
| `extract` | Extract text/data | text, data_field, list_item |

**Sources:** [services/action-builder/src/types/capability.ts:62-71]()

### PageModule Enum

Categorizes elements by their page layout location:

```mermaid
graph TB
    subgraph "Page Structure"
        header["header<br/>(navigation, logo, search)"]
        navibar["navibar<br/>(primary navigation bar)"]
        breadcrumb["breadcrumb<br/>(navigation trail)"]
        sidebar["sidebar<br/>(secondary navigation)"]
        main["main<br/>(primary content area)"]
        tab["tab<br/>(tabbed navigation)"]
        modal["modal<br/>(overlay dialogs)"]
        footer["footer<br/>(bottom info, links)"]
    end
    
    unknown["unknown<br/>(unclassified location)"]
```

**Module Values:**
- `header`: Top navigation, logo, search bar
- `footer`: Bottom information, legal links
- `sidebar`: Side navigation or secondary content
- `navibar`: Primary navigation bar
- `main`: Primary content area
- `modal`: Overlay dialogs and popups
- `breadcrumb`: Navigation breadcrumb trail
- `tab`: Tabbed navigation interface
- `unknown`: Location not determined by LLM

**Sources:** [services/action-builder/src/types/capability.ts:28-40]()

---

## Selector System

### SelectorItem Structure

Multi-selector format with priority ordering and template support:

```mermaid
graph LR
    SelectorItem["SelectorItem"]
    type["type: SelectorType"]
    value["value: string"]
    priority["priority: number"]
    confidence["confidence: number"]
    template["template?: TemplateParam[]"]
    
    SelectorItem --> type
    SelectorItem --> value
    SelectorItem --> priority
    SelectorItem --> confidence
    SelectorItem --> template
    
    subgraph "SelectorType Options"
        css["css"]
        xpath["xpath"]
        id["id"]
        dataTestId["dataTestId"]
        ariaLabel["ariaLabel"]
    end
    
    type -.-> css
    type -.-> xpath
    type -.-> id
    type -.-> dataTestId
    type -.-> ariaLabel
```

**SelectorItem Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `type` | `SelectorType` | Selector strategy (css, xpath, id, etc.) |
| `value` | `string` | Selector value, may contain template placeholders |
| `priority` | `number` | Precedence order (1 = highest priority) |
| `confidence` | `number` | Stability confidence score (0-1) |
| `template` | `TemplateParam[]?` | Template parameter definitions if value contains placeholders |

**Sources:** [services/action-builder/src/types/capability.ts:2-6]()

### SelectorType Enum

| Type | Description | Example |
|------|-------------|---------|
| `css` | CSS selector | `.search-button` |
| `xpath` | XPath expression | `//button[@class='search']` |
| `id` | HTML id attribute | `#search-btn` |
| `dataTestId` | data-testid attribute | `[data-testid="search"]` |
| `ariaLabel` | aria-label attribute | `[aria-label="Search"]` |

**Priority Ordering Convention:**
1. Most stable/specific selectors (id, dataTestId)
2. CSS selectors (class-based)
3. XPath expressions
4. ARIA-based selectors

Lower priority numbers indicate higher precedence. The selector optimizer ([SelectorOptimizer](#6.2)) adjusts confidence scores based on LLM analysis of selector stability.

**Sources:** [services/action-builder/src/types/capability.ts:2-6]()

### Template Parameters

For selectors with dynamic values (e.g., list items), templates define parameterization:

```typescript
interface TemplateParam {
  name: string;        // Parameter name
  type: string;        // Parameter type (string, number, etc.)
  description: string; // Human-readable description
}
```

**Example:**
```javascript
{
  type: "css",
  value: ".product-item[data-id=\"{{product_id}}\"]",
  priority: 1,
  confidence: 0.85,
  template: [
    {
      name: "product_id",
      type: "string",
      description: "Product identifier"
    }
  ]
}
```

**Sources:** [services/action-builder/src/types/capability.ts:2-6]()

---

## Tool Definitions

The SDK exposes tools for LLM integration with dual schema formats (JSON Schema + Zod).

### Tool Definition Architecture

```mermaid
graph TB
    ToolDefinition["ToolDefinition&lt;T&gt;"]
    name["name: string"]
    description["description: string"]
    inputSchema["inputSchema: T (Zod)"]
    handler["handler: (input) => Promise&lt;string&gt;"]
    
    ToolDefinition --> name
    ToolDefinition --> description
    ToolDefinition --> inputSchema
    ToolDefinition --> handler
    
    ToolParams["ToolParams&lt;T&gt;"]
    json["json: Record&lt;string, unknown&gt;<br/>(JSON Schema)"]
    zod["zod: T<br/>(Zod Schema)"]
    
    ToolParams --> json
    ToolParams --> zod
    
    inputSchema -.->|"converted to"| ToolParams
    
    subgraph "SDK Methods"
        searchActions["searchActions()"]
        getActionById["getActionById()"]
        listSources["listSources()"]
        searchSources["searchSources()"]
    end
    
    searchActions -.->|"has attached"| ToolParams
    getActionById -.->|"has attached"| ToolParams
    listSources -.->|"has attached"| ToolParams
    searchSources -.->|"has attached"| ToolParams
```

**Sources:** [packages/js-sdk/src/tool-defs.ts:1-58]()

### ToolDefinition Interface

Generic interface for defining LLM-compatible tools:

```typescript
interface ToolDefinition<T extends z.ZodTypeAny> {
  name: string;              // Tool name (snake_case)
  description: string;       // Tool description for LLM
  inputSchema: T;            // Zod schema for validation
  handler: (input: z.infer<T>) => Promise<string>;
}
```

**Sources:** [packages/js-sdk/src/tool-defs.ts:15-27]()

### ToolParams Interface

Dual-format schema for multi-framework compatibility:

```typescript
interface ToolParams<T extends z.ZodTypeAny> {
  json: Record<string, unknown>;  // JSON Schema (OpenAI, Anthropic, Gemini)
  zod: T;                         // Zod schema (Vercel AI SDK)
}
```

**Framework Compatibility:**
- **JSON Schema format**: OpenAI SDK, Anthropic SDK, Google Gemini SDK
- **Zod format**: Vercel AI SDK (`@ai-sdk/openai`, `@ai-sdk/anthropic`, etc.)

**Sources:** [packages/js-sdk/src/tool-defs.ts:5-13]()

### SDK Tool Schemas

#### searchActions Tool

Search for action manuals by keyword.

```mermaid
graph LR
    searchActionsSchema["searchActionsSchema"]
    query["query: string<br/>(required, min=1, max=200)"]
    type["type?: enum<br/>(vector | fulltext | hybrid)"]
    limit["limit?: number<br/>(1-100, default=5)"]
    sourceIds["sourceIds?: string<br/>(comma-separated)"]
    minScore["minScore?: number<br/>(0-1)"]
    
    searchActionsSchema --> query
    searchActionsSchema --> type
    searchActionsSchema --> limit
    searchActionsSchema --> sourceIds
    searchActionsSchema --> minScore
```

**Schema Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `query` | `string` | Yes | Search keyword (1-200 chars) |
| `type` | `"vector" \| "fulltext" \| "hybrid"` | No | Search strategy (default: hybrid) |
| `limit` | `number` | No | Max results (1-100, default: 5) |
| `sourceIds` | `string` | No | Filter by source IDs (comma-separated) |
| `minScore` | `number` | No | Minimum similarity threshold (0-1) |

**Sources:** [packages/js-sdk/src/tool-defs.ts:64-112]()

#### getActionById Tool

Retrieve complete action details including selectors.

```mermaid
graph LR
    getActionByIdSchema["getActionByIdSchema"]
    id["id: string<br/>(required, min=1)"]
    
    getActionByIdSchema --> id
    
    subgraph "ID Format Examples"
        full["https://example.com/page"]
        partial["example.com/page"]
        domain["releases.rs"]
    end
    
    id -.-> full
    id -.-> partial
    id -.-> domain
```

**Schema Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | `string` | Yes | Action ID (full URL or fuzzy match) |

**ID Format Support:**
- Full URL: `https://example.com/docs/page`
- Domain + path: `example.com/docs/page`
- Domain only: `releases.rs` (matches `https://releases.rs/`)
- With chunk: `https://example.com/page#chunk-1`

**Sources:** [packages/js-sdk/src/tool-defs.ts:118-154]()

#### listSources Tool

List all available sources (websites) in the database.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `limit` | `number` | No | Max sources (1-200, default: 50) |

**Sources:** [packages/js-sdk/src/tool-defs.ts:160-186]()

#### searchSources Tool

Search for sources by keyword (name, description, domain, tags).

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `query` | `string` | Yes | Search keyword (1-200 chars) |
| `limit` | `number` | No | Max results (1-100, default: 10) |

**Sources:** [packages/js-sdk/src/tool-defs.ts:192-237]()

---

## Recorder Tool Definitions

Tools used by the AI recorder during element discovery and registration.

### Recorder Tool Overview

```mermaid
graph TB
    RecorderToolExecutor["RecorderToolExecutor"]
    
    navigate["navigate<br/>(url: string)"]
    observe["observe_page<br/>(focus: string, module?: PageModule)"]
    setContext["set_page_context<br/>(page_type, page_name, ...)"]
    register["register_element<br/>(element_id, selectors, ...)"]
    interact["interact<br/>(element_id, action, instruction)"]
    wait["wait<br/>(seconds?, forText?)"]
    scroll["scroll<br/>(direction, amount?)"]
    scrollToBottom["scroll_to_bottom<br/>(wait_after_scroll?)"]
    goBack["go_back<br/>()"]
    
    RecorderToolExecutor --> navigate
    RecorderToolExecutor --> observe
    RecorderToolExecutor --> setContext
    RecorderToolExecutor --> register
    RecorderToolExecutor --> interact
    RecorderToolExecutor --> wait
    RecorderToolExecutor --> scroll
    RecorderToolExecutor --> scrollToBottom
    RecorderToolExecutor --> goBack
```

**Sources:** [services/action-builder/src/recorder/RecorderTools.ts:1-216]()

### Core Recorder Tools

#### navigate

Navigate to a URL.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `url` | `string` | Yes | Target URL |

#### observe_page

Observe the current page to discover interactive elements.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `focus` | `string` | Yes | What to focus on (e.g., "search box and submit button") |
| `module` | `PageModule \| "all"` | No | Page module to observe (default: all) |

**Module Options:** `header`, `footer`, `sidebar`, `navibar`, `main`, `modal`, `breadcrumb`, `tab`, `all`

#### set_page_context

Set the current page context metadata.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `page_type` | `string` | Yes | Page type identifier |
| `page_name` | `string` | Yes | Human-readable name |
| `page_description` | `string` | No | Optional description |
| `url_pattern` | `string` | No | Optional URL regex pattern |

#### register_element

Register a UI element capability with selectors and metadata.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `element_id` | `string` | Yes | Unique identifier (snake_case) |
| `description` | `string` | Yes | Element description |
| `element_type` | `string` | Yes | Element type classification |
| `css_selector` | `string` | No | CSS selector |
| `xpath_selector` | `string` | No | XPath selector |
| `aria_label` | `string` | No | ARIA label |
| `placeholder` | `string` | No | Placeholder text (inputs) |
| `allow_methods` | `string[]` | Yes | Allowed interaction methods |
| `leads_to` | `string` | No | Page type navigation target |
| `arguments` | `ArgumentDef[]` | No | Parameterized arguments |
| `parent` | `string` | No | Parent element ID |
| `depends_on` | `string` | No | Dependency element ID |
| `visibility_condition` | `string` | No | Visibility condition |
| `is_repeating` | `boolean` | No | List item flag |
| `data_key` | `string` | No | Data extraction key |
| `children` | `string[]` | No | Child element IDs |
| `module` | `PageModule` | No | Page module location |
| `input_type` | `string` | No | Input type (for inputs) |
| `input_name` | `string` | No | Name attribute (for inputs) |
| `input_value` | `string` | No | Default value (for inputs) |
| `href` | `string` | No | URL pattern (for links) |

**Sources:** [services/action-builder/src/recorder/RecorderTools.ts:64-134]()

#### interact

Perform an interaction on a target element (task-driven mode).

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `element_id` | `string` | Yes | Unique identifier |
| `action` | `string` | Yes | Action to perform |
| `instruction` | `string` | Yes | Natural language instruction |
| `value` | `string` | No | Optional value (for type) |
| `element_description` | `string` | Yes | Element description |
| `css_selector` | `string` | No | Optional CSS selector |
| `xpath_selector` | `string` | No | Optional XPath selector |

**Sources:** [services/action-builder/src/recorder/RecorderTools.ts:136-155]()

### Navigation and Utility Tools

| Tool | Parameters | Description |
|------|-----------|-------------|
| `wait` | `seconds?: number, forText?: string` | Wait for time or text |
| `scroll` | `direction: "up"\|"down", amount?: number` | Scroll by pixels (default: 300px) |
| `scroll_to_bottom` | `wait_after_scroll?: number` | Scroll to bottom for lazy-load (default: 1000ms) |
| `go_back` | _(none)_ | Navigate back in browser history |

**Sources:** [services/action-builder/src/recorder/RecorderTools.ts:157-214]()

---

## API Response Types

### ChunkSearchResult

Response format for action search queries.

```typescript
interface ChunkSearchResult {
  success: boolean;
  query: string;
  results: Array<{
    action_id: string;    // URL-based action identifier
    content: string;      // Content preview
    score: number;        // Relevance score (0-1)
    createdAt: string;    // ISO timestamp
  }>;
  count: number;          // Number of results returned
  total: number;          // Total matching results
  hasMore: boolean;       // True if more results available
}
```

**Sources:** [packages/js-sdk/src/types.ts:6-21]()

### ChunkActionDetail

Complete action details with selectors and metadata.

```typescript
interface ChunkActionDetail {
  action_id: string;        // URL-based identifier
  content: string;          // Full action content/documentation
  elements: string | null;  // JSON-encoded ElementCapability objects
  createdAt: string;        // ISO timestamp
  documentId: number;       // Parent document ID
  documentTitle: string;    // Page title
  documentUrl: string;      // Page URL
  chunkIndex: number;       // Chunk position in document
  heading: string | null;   // Section heading
  tokenCount: number;       // Token count for content
}
```

**ParsedElements Structure:**

```typescript
interface ParsedElements {
  [key: string]: {
    css_selector?: string;
    xpath_selector?: string;
    description?: string;
    element_type?: string;
    allow_methods?: string[];
    depends_on?: string;
  };
}
```

**Sources:** [packages/js-sdk/src/types.ts:23-51]()

### SourceItem

Source (website) metadata.

```typescript
interface SourceItem {
  id: number;                      // Source ID
  name: string;                    // Source name
  baseUrl: string;                 // Base URL
  description: string | null;      // Optional description
  domain: string | null;           // Domain
  tags: string[];                  // Tag array
  healthScore: number | null;      // Health score (0-100)
  lastCrawledAt: string | null;    // Last crawl timestamp
  createdAt: string;               // Creation timestamp
}
```

**Sources:** [packages/js-sdk/src/types.ts:53-66]()

### SourceListResult and SourceSearchResult

```typescript
interface SourceListResult {
  success: boolean;
  results: SourceItem[];
  count: number;
}

interface SourceSearchResult {
  success: boolean;
  query: string;
  results: SourceItem[];
  count: number;
}
```

**Sources:** [packages/js-sdk/src/types.ts:68-85]()

---

## Type System Relationships

### Cross-System Type Flow

```mermaid
graph TB
    subgraph "Recording Layer"
        RecorderTools["RecorderTools<br/>(OpenAI tool format)"]
        RecorderToolExecutor["RecorderToolExecutor"]
    end
    
    subgraph "Capability Layer"
        ElementCapability["ElementCapability"]
        PageCapability["PageCapability"]
        SiteCapability["SiteCapability"]
        SelectorItem["SelectorItem[]"]
    end
    
    subgraph "Database Layer"
        elements["elements table"]
        pages["pages table"]
        chunks["chunks table"]
    end
    
    subgraph "API Layer"
        ChunkActionDetail["ChunkActionDetail"]
        ChunkSearchResult["ChunkSearchResult"]
        SourceItem["SourceItem"]
    end
    
    subgraph "SDK Layer"
        ToolDefinition["ToolDefinition&lt;T&gt;"]
        ToolParams["ToolParams&lt;T&gt;"]
        searchActionsSchema["searchActionsSchema"]
        getActionByIdSchema["getActionByIdSchema"]
    end
    
    RecorderTools --> RecorderToolExecutor
    RecorderToolExecutor -->|"creates"| ElementCapability
    ElementCapability -->|"contains"| SelectorItem
    ElementCapability -->|"aggregated in"| PageCapability
    PageCapability -->|"aggregated in"| SiteCapability
    
    ElementCapability -->|"persisted to"| elements
    PageCapability -->|"persisted to"| pages
    SiteCapability -->|"indexed in"| chunks
    
    elements -->|"queried as"| ChunkActionDetail
    chunks -->|"searched as"| ChunkSearchResult
    pages -->|"listed as"| SourceItem
    
    ChunkActionDetail -->|"returned by"| getActionByIdSchema
    ChunkSearchResult -->|"returned by"| searchActionsSchema
    
    searchActionsSchema -.->|"implements"| ToolDefinition
    getActionByIdSchema -.->|"implements"| ToolDefinition
    ToolDefinition -->|"has"| ToolParams
```

**Sources:** [services/action-builder/src/types/capability.ts:1-156](), [packages/js-sdk/src/tool-defs.ts:1-237](), [packages/js-sdk/src/types.ts:1-97]()

### Type Import Patterns

The codebase uses explicit type re-exports to maintain separation of concerns:

```typescript
// action-builder re-exports from db package
export type {
  SelectorType,
  SelectorItem,
  TemplateParam,
} from '@actionbookdev/db'

// action-builder re-exports from browser package
export type {
  ObserveResult,
  ActionObject,
  ActionMethod,
} from '@actionbookdev/browser'
```

This pattern ensures that capability types remain consistent across the recording layer, database layer, and SDK layer.

**Sources:** [services/action-builder/src/types/capability.ts:1-14]()

---

# Page: Capability Types

# Capability Types

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [services/action-builder/src/recorder/RecorderTools.ts](services/action-builder/src/recorder/RecorderTools.ts)
- [services/action-builder/src/types/capability.ts](services/action-builder/src/types/capability.ts)
- [services/action-builder/src/utils/index.ts](services/action-builder/src/utils/index.ts)
- [services/action-builder/src/utils/url-matcher.ts](services/action-builder/src/utils/url-matcher.ts)
- [services/action-builder/test/recorder/RecorderTools.ut.test.ts](services/action-builder/test/recorder/RecorderTools.ut.test.ts)
- [services/action-builder/test/types/capability.ut.test.ts](services/action-builder/test/types/capability.ut.test.ts)
- [services/action-builder/test/utils/url-matcher.ut.test.ts](services/action-builder/test/utils/url-matcher.ut.test.ts)

</details>



## Purpose and Scope

This page documents the core type definitions for representing website capabilities in Actionbook. These types form the data model for action manuals, defining the structure of UI elements, pages, and sites that are discovered and recorded during the build pipeline.

For information about the selector system used within capabilities, see [Selector Types](#7.2). For details on how capabilities are discovered and recorded, see [Action Recording](#3.2.2).

**Sources:** [services/action-builder/src/types/capability.ts:1-157]()

## Capability Hierarchy

Actionbook organizes website capabilities into a three-tier hierarchy that models the structure of websites:

```mermaid
graph TD
    SiteCapability["SiteCapability<br/>(Root Aggregate)"]
    GlobalElements["global_elements:<br/>Record&lt;string, ElementCapability&gt;"]
    Pages["pages:<br/>Record&lt;string, PageCapability&gt;"]
    PageElements["elements:<br/>Record&lt;string, ElementCapability&gt;"]
    
    SiteCapability --> GlobalElements
    SiteCapability --> Pages
    Pages --> PageElements
    
    GlobalElements -.->|"Shared across all pages"| ElementCapability1["ElementCapability"]
    PageElements -.->|"Page-specific elements"| ElementCapability2["ElementCapability"]
```

**Hierarchy Levels:**

| Level | Type | Purpose | Storage Location |
|-------|------|---------|------------------|
| Site | `SiteCapability` | Root container for an entire website | YAML file per site |
| Page | `PageCapability` | Represents a page type (e.g., search, product detail) | Nested in `SiteCapability.pages` |
| Element | `ElementCapability` | Individual UI component with selectors and interaction methods | Nested in page or global elements |

**Sources:** [services/action-builder/src/types/capability.ts:143-156](), [services/action-builder/src/types/capability.ts:131-141](), [services/action-builder/src/types/capability.ts:79-128]()

## SiteCapability

The root aggregate containing all capabilities for a website.

```typescript
interface SiteCapability {
  domain: string
  name: string
  description: string
  version: string
  recorded_at: string
  scenario: string
  health_score?: number
  global_elements: Record<string, ElementCapability>
  pages: Record<string, PageCapability>
}
```

| Field | Type | Description |
|-------|------|-------------|
| `domain` | `string` | Website domain (e.g., "github.com") |
| `name` | `string` | Human-readable site name |
| `description` | `string` | Site purpose and capabilities summary |
| `version` | `string` | Version identifier for the action manual |
| `recorded_at` | `string` | ISO timestamp of recording |
| `scenario` | `string` | Recording scenario context |
| `health_score` | `number?` | Optional quality metric (0-100) |
| `global_elements` | `Record<string, ElementCapability>` | Elements available across all pages (header, footer, etc.) |
| `pages` | `Record<string, PageCapability>` | Page type definitions keyed by page_type |

**Sources:** [services/action-builder/src/types/capability.ts:143-156]()

## PageCapability

Represents a specific page type within a site (e.g., homepage, search results, product detail).

```typescript
interface PageCapability {
  page_type: string
  name: string
  description: string
  url_patterns: string[]
  wait_for?: string
  elements: Record<string, ElementCapability>
}
```

| Field | Type | Description |
|-------|------|-------------|
| `page_type` | `string` | Unique identifier for page type (e.g., "search_results") |
| `name` | `string` | Human-readable page name |
| `description` | `string` | Page purpose and content description |
| `url_patterns` | `string[]` | Regex patterns matching URLs for this page type |
| `wait_for` | `string?` | Optional selector to wait for before page is ready |
| `elements` | `Record<string, ElementCapability>` | Page-specific elements keyed by element_id |

**Sources:** [services/action-builder/src/types/capability.ts:131-141]()

## ElementCapability

The core type representing a single UI element with its selectors, interaction methods, and metadata.

### Core Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | `string` | ✓ | Unique snake_case identifier (e.g., "search_button") |
| `selectors` | `SelectorItem[]` | ✓ | Multi-selector array with priority ordering (see [#7.2](#7.2)) |
| `description` | `string` | ✓ | Natural language description of element's purpose |
| `element_type` | `ElementType` | ✓ | Element classification (see [Element Types](#element-types)) |
| `allow_methods` | `AllowMethod[]` | ✓ | Permitted interaction methods (see [Interaction Methods](#interaction-methods)) |
| `discovered_at` | `string` | ✓ | ISO timestamp of element discovery |
| `arguments` | `ArgumentDef[]?` | - | Optional arguments for parameterized interactions |
| `leads_to` | `string?` | - | Page type this element navigates to |
| `wait_after` | `number?` | - | Milliseconds to wait after interaction |
| `confidence` | `number?` | - | Selector stability score (0.0-1.0) |

### Structural Relationships

| Field | Type | Description |
|-------|------|-------------|
| `parent` | `string?` | Parent element ID for hierarchical relationships |
| `children` | `string[]?` | Child element IDs (for containers and lists) |
| `depends_on` | `string?` | Element ID that must be interacted with first |
| `visibility_condition` | `string?` | Condition text for element visibility |
| `is_repeating` | `boolean?` | True if element repeats in a list/table pattern |
| `data_key` | `string?` | Key name for data extraction from this element |

### Page Location

| Field | Type | Description |
|-------|------|-------------|
| `module` | `PageModule?` | Location within page structure (see [Page Modules](#page-modules)) |

### Element-Specific Attributes

**Input Elements:**

| Field | Type | Description |
|-------|------|-------------|
| `input_type` | `string?` | HTML input type (text, email, password, number, etc.) |
| `input_name` | `string?` | HTML name attribute |
| `input_value` | `string?` | Default or placeholder value |

**Link Elements:**

| Field | Type | Description |
|-------|------|-------------|
| `href` | `string?` | URL or URL pattern for the link |

**Sources:** [services/action-builder/src/types/capability.ts:79-128]()

## Type Enumerations

### Element Types

The `ElementType` enumeration classifies UI elements by their semantic role.

| Type | Category | Description | Typical Allow Methods |
|------|----------|-------------|----------------------|
| `button` | Interactive | Clickable button elements | `click`, `hover` |
| `input` | Interactive | Text input fields | `type`, `clear` |
| `link` | Interactive | Navigation links | `click` |
| `select` | Interactive | Dropdown/select elements | `select`, `click` |
| `checkbox` | Interactive | Checkbox inputs | `click` |
| `radio` | Interactive | Radio button inputs | `click` |
| `text` | Display | Static text for reading | `extract` |
| `data_field` | Display | Extractable data field | `extract` |
| `container` | Structural | Groups related elements | `scroll` |
| `list` | Structural | Container with repeating items | `scroll` |
| `list_item` | Structural | Single item in a list | `click`, `extract` |
| `other` | Generic | Unclassified element type | Varies |

**Sources:** [services/action-builder/src/types/capability.ts:47-60]()

### Interaction Methods

The `AllowMethod` enumeration defines permitted interactions with elements.

| Method | Description | Applicable Element Types |
|--------|-------------|-------------------------|
| `click` | Click the element | `button`, `link`, `checkbox`, `radio`, `select` |
| `type` | Type text into element | `input` |
| `clear` | Clear element content | `input` |
| `scroll` | Scroll element into view or scroll within | `container`, `list` |
| `hover` | Hover over element | `button`, `link` |
| `select` | Select option from dropdown | `select` |
| `extract` | Extract text/data value | `text`, `data_field`, `list_item` |

**Sources:** [services/action-builder/src/types/capability.ts:64-72]()

### Page Modules

The `PageModule` enumeration categorizes elements by their location within the page structure. This helps organize elements and enables focused observation during recording.

| Module | Description | Typical Elements |
|--------|-------------|------------------|
| `header` | Top navigation area | Logo, navigation links, search bar, user menu |
| `footer` | Bottom page area | Copyright, links, social icons |
| `sidebar` | Side panel | Filters, navigation tree, quick links |
| `navibar` | Navigation bar | Primary navigation menu, breadcrumbs |
| `main` | Primary content area | Forms, content, data displays |
| `modal` | Overlay dialogs | Popups, confirmation dialogs, forms |
| `breadcrumb` | Breadcrumb navigation | Path indicators |
| `tab` | Tab interface | Tab buttons and panels |
| `unknown` | Unclassified location | Default when location unclear |

**Usage in Recording Tools:**

The `observe_page` tool accepts a `module` parameter to focus observation on specific page areas. The `register_element` tool uses `module` to categorize discovered elements.

**Sources:** [services/action-builder/src/types/capability.ts:31-41](), [services/action-builder/src/recorder/RecorderTools.ts:32-37](), [services/action-builder/src/recorder/RecorderTools.ts:108-112]()

## ArgumentDef

Defines arguments for parameterized element interactions. Arguments enable elements to accept dynamic values (e.g., search query text, form field values).

```typescript
interface ArgumentDef {
  name: string
  type: 'string' | 'number' | 'boolean' | 'enum'
  description: string
  required?: boolean
  enum_values?: string[]
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | `string` | ✓ | Argument identifier (snake_case) |
| `type` | `'string' \| 'number' \| 'boolean' \| 'enum'` | ✓ | Data type for the argument |
| `description` | `string` | ✓ | Natural language description of argument purpose |
| `required` | `boolean?` | - | Whether argument must be provided (default: false) |
| `enum_values` | `string[]?` | - | Valid values when type is 'enum' |

**Example Use Cases:**

```typescript
// Search input argument
{
  name: "query",
  type: "string",
  description: "Search query text",
  required: true
}

// Sort dropdown argument
{
  name: "sort_order",
  type: "enum",
  description: "Sort order for results",
  required: false,
  enum_values: ["newest", "oldest", "most_relevant"]
}
```

**Sources:** [services/action-builder/src/types/capability.ts:18-26]()

## Capability Type Flow

This diagram shows how capability types flow through the recording and storage systems:

```mermaid
graph LR
    subgraph "Recording Tools"
        RegisterElement["register_element tool"]
        SetPageContext["set_page_context tool"]
    end
    
    subgraph "ActionRecorder State"
        CurrentPage["currentPage:<br/>PageCapability"]
        Elements["elements:<br/>Map&lt;string, ElementCapability&gt;"]
    end
    
    subgraph "Database Layer"
        ElementsTable[("elements table")]
        PagesTable[("pages table")]
    end
    
    subgraph "YAML Output"
        SiteYAML["output/sites/{domain}.yaml<br/>SiteCapability"]
    end
    
    RegisterElement -->|"Creates"| ElementCapability["ElementCapability"]
    SetPageContext -->|"Creates"| PageCapability["PageCapability"]
    
    ElementCapability --> Elements
    PageCapability --> CurrentPage
    
    Elements --> ElementsTable
    CurrentPage --> PagesTable
    
    ElementsTable -->|"Aggregated"| SiteYAML
    PagesTable -->|"Aggregated"| SiteYAML
    
    SiteYAML -->|"Published as"| ActionManual["Action Manual"]
```

**Data Flow Description:**

1. **Recording Phase:** The LLM calls `register_element` and `set_page_context` tools during action recording
2. **In-Memory State:** `ActionRecorder` accumulates `ElementCapability` and `PageCapability` objects
3. **Persistence:** Recording results are saved to `elements` and `pages` database tables
4. **Aggregation:** Build completion triggers aggregation into `SiteCapability` structure
5. **Publication:** The final `SiteCapability` is written to YAML and made available via API

**Sources:** [services/action-builder/src/recorder/RecorderTools.ts:64-135](), [services/action-builder/src/types/capability.ts:1-157]()

## Tool Definition Integration

The recording tools expose capability types through their JSON Schema parameters:

```mermaid
graph TB
    subgraph "RecorderTools.ts"
        GetRecorderTools["getRecorderTools()"]
        RegisterElementTool["register_element function definition"]
        ObservePageTool["observe_page function definition"]
        SetPageContextTool["set_page_context function definition"]
    end
    
    subgraph "Type Constraints"
        ElementTypeEnum["element_type:<br/>button | input | link | select..."]
        AllowMethodsArray["allow_methods:<br/>click | type | extract..."]
        ModuleEnum["module:<br/>header | footer | sidebar..."]
        PageModuleEnum["module parameter:<br/>header | footer | all..."]
    end
    
    GetRecorderTools --> RegisterElementTool
    GetRecorderTools --> ObservePageTool
    GetRecorderTools --> SetPageContextTool
    
    RegisterElementTool --> ElementTypeEnum
    RegisterElementTool --> AllowMethodsArray
    RegisterElementTool --> ModuleEnum
    
    ObservePageTool --> PageModuleEnum
```

**Key Mappings:**

| Tool Parameter | Maps To Type | Validation |
|----------------|--------------|------------|
| `register_element.element_type` | `ElementType` | Enum constraint in tool schema |
| `register_element.allow_methods` | `AllowMethod[]` | Array of valid method strings |
| `register_element.module` | `PageModule` | Enum with 'unknown' default |
| `observe_page.module` | `PageModule` | Enum with 'all' option for observation |
| `register_element.arguments` | `ArgumentDef[]` | Object array matching ArgumentDef structure |

**Sources:** [services/action-builder/src/recorder/RecorderTools.ts:64-135](), [services/action-builder/src/recorder/RecorderTools.ts:19-42]()

## Type Re-exports and Dependencies

The capability types depend on and re-export types from other packages:

```mermaid
graph TD
    CapabilityTypes["services/action-builder/src/types/capability.ts"]
    DBPackage["@actionbookdev/db"]
    BrowserPackage["@actionbookdev/browser"]
    
    CapabilityTypes -->|"Re-exports"| SelectorType["SelectorType"]
    CapabilityTypes -->|"Re-exports"| SelectorItem["SelectorItem"]
    CapabilityTypes -->|"Re-exports"| TemplateParam["TemplateParam"]
    CapabilityTypes -->|"Re-exports"| ObserveResult["ObserveResult"]
    CapabilityTypes -->|"Re-exports"| ActionObject["ActionObject"]
    CapabilityTypes -->|"Re-exports"| ActionMethod["ActionMethod"]
    
    DBPackage --> SelectorType
    DBPackage --> SelectorItem
    DBPackage --> TemplateParam
    
    BrowserPackage --> ObserveResult
    BrowserPackage --> ActionObject
    BrowserPackage --> ActionMethod
```

**Type Sources:**

| Type | Source Package | Purpose |
|------|----------------|---------|
| `SelectorType` | `@actionbookdev/db` | Selector type enumeration (css, xpath, id, etc.) |
| `SelectorItem` | `@actionbookdev/db` | Individual selector with priority and confidence |
| `TemplateParam` | `@actionbookdev/db` | Template parameter definition for dynamic selectors |
| `ObserveResult` | `@actionbookdev/browser` | Browser observation result structure |
| `ActionObject` | `@actionbookdev/browser` | Browser action definition |
| `ActionMethod` | `@actionbookdev/browser` | Browser action method type |

**Sources:** [services/action-builder/src/types/capability.ts:1-14]()

---

# Page: Selector Types

# Selector Types

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [services/action-builder/scripts/playbook-record.ts](services/action-builder/scripts/playbook-record.ts)
- [services/action-builder/src/recorder/RecorderToolExecutor.ts](services/action-builder/src/recorder/RecorderToolExecutor.ts)
- [services/action-builder/src/recorder/RecorderTools.ts](services/action-builder/src/recorder/RecorderTools.ts)
- [services/action-builder/src/types/capability.ts](services/action-builder/src/types/capability.ts)
- [services/action-builder/src/utils/index.ts](services/action-builder/src/utils/index.ts)
- [services/action-builder/src/utils/url-matcher.ts](services/action-builder/src/utils/url-matcher.ts)
- [services/action-builder/src/validator/SelectorValidator.ts](services/action-builder/src/validator/SelectorValidator.ts)
- [services/action-builder/test/browser/xpath-optimizer.ut.test.ts](services/action-builder/test/browser/xpath-optimizer.ut.test.ts)
- [services/action-builder/test/recorder/RecorderTools.ut.test.ts](services/action-builder/test/recorder/RecorderTools.ut.test.ts)
- [services/action-builder/test/types/capability.ut.test.ts](services/action-builder/test/types/capability.ut.test.ts)
- [services/action-builder/test/utils/url-matcher.ut.test.ts](services/action-builder/test/utils/url-matcher.ut.test.ts)
- [services/action-builder/test/validator/SelectorValidator.ut.test.ts](services/action-builder/test/validator/SelectorValidator.ut.test.ts)

</details>



This page documents the selector system used throughout Actionbook to identify and interact with UI elements. The selector system supports multiple selector types with priority ordering, confidence scoring, and template parameterization for robust element targeting.

For information about how selectors are used in capability definitions, see [Capability Types](#7.1). For details about recording actions that use these selectors, see [Action Recording](#3.2.2).

## Overview

Actionbook uses a multi-selector strategy where each UI element is identified by an array of `SelectorItem` objects. Each selector item represents a different way to locate the same element (CSS, XPath, ID, data-testid, etc.), ordered by stability and reliability. When executing actions, the system tries selectors in priority order until one succeeds.

This approach provides resilience against page structure changes: if one selector breaks (e.g., a CSS class changes), other selectors (e.g., data-testid or aria-label) can still locate the element.

Sources: [services/action-builder/src/types/capability.ts:1-6](), [services/action-builder/src/recorder/RecorderToolExecutor.ts:1-26]()

## SelectorItem Data Structure

```mermaid
classDiagram
    class SelectorItem {
        +SelectorType type
        +string value
        +number priority
        +number confidence
        +boolean? isTemplate
        +TemplateParam[]? templateParams
    }
    
    class SelectorType {
        <<enumeration>>
        css
        xpath
        id
        data-testid
        aria-label
        placeholder
        text
    }
    
    class TemplateParam {
        +string name
        +string description
        +string? example
    }
    
    SelectorItem --> SelectorType
    SelectorItem --> TemplateParam
```

**SelectorItem Structure**

| Field | Type | Description |
|-------|------|-------------|
| `type` | `SelectorType` | The selector type (css, xpath, id, etc.) |
| `value` | `string` | The selector value or template string |
| `priority` | `number` | Execution order (lower = higher priority) |
| `confidence` | `number` | Stability score (0.0-1.0) |
| `isTemplate` | `boolean?` | Whether this selector contains template parameters |
| `templateParams` | `TemplateParam[]?` | Template parameter definitions |

Sources: [services/action-builder/src/types/capability.ts:1-6](), [services/action-builder/src/recorder/RecorderToolExecutor.ts:10-30]()

## Selector Types

The system supports seven distinct selector types, each with specific use cases and stability characteristics:

```mermaid
graph TB
    subgraph "Selector Type Hierarchy"
        ID["id<br/>#element-id or [id='value']"]
        DataTestId["data-testid<br/>[data-testid='value']"]
        AriaLabel["aria-label<br/>[aria-label='value']"]
        CSS["css<br/>.class or div > span"]
        XPath["xpath<br/>//div[@class='value']"]
        Placeholder["placeholder<br/>[placeholder='value']"]
        Text["text<br/>text=ButtonLabel"]
    end
    
    ID -.->|"highest stability"| DataTestId
    DataTestId -.-> AriaLabel
    AriaLabel -.-> CSS
    CSS -.-> XPath
    XPath -.-> Placeholder
    Placeholder -.->|"lowest stability"| Text
```

### Type Definitions

| Selector Type | Format | Example | Stability | Use Case |
|--------------|--------|---------|-----------|----------|
| `id` | `#id` or `[id="value"]` | `#submit-btn`, `[id="cs.AI"]` | Highest (0.95) | Elements with stable ID attributes |
| `data-testid` | `[data-testid="value"]` | `[data-testid="checkout-btn"]` | Very High (0.90) | Test-specific attributes |
| `aria-label` | `[aria-label="value"]` | `[aria-label="Close dialog"]` | High (0.85) | Accessible elements with semantic labels |
| `css` | Standard CSS selector | `.nav-item`, `button.primary` | Medium (0.75) | Class-based or structural selectors |
| `xpath` | XPath expression | `//button[@name="submit"]` | Low-Medium (0.60-0.80) | Complex hierarchical queries |
| `placeholder` | `[placeholder="value"]` | `[placeholder="Search..."]` | Low (0.65) | Input fields with placeholder text |
| `text` | `text=value` | `text=Submit` | Lowest | Buttons/links with visible text |

**Note**: The `id` selector type uses special handling for IDs containing special characters (e.g., dots). The system automatically converts `id: "cs.AI"` to `[id="cs.AI"]` instead of `#cs.AI` to avoid CSS selector parsing issues.

Sources: [services/action-builder/src/recorder/RecorderToolExecutor.ts:354-434](), [services/action-builder/test/browser/xpath-optimizer.ut.test.ts:26-120]()

## Priority Ordering System

```mermaid
graph LR
    subgraph "Priority Assignment in RecorderToolExecutor"
        Start["priority = 1"]
        
        Start --> CheckID["Has ID?"]
        CheckID -->|Yes| AddID["Add id selector<br/>priority=1, conf=0.95<br/>priority++"]
        CheckID -->|No| CheckDataTestId
        
        AddID --> CheckDataTestId["Has data-testid?"]
        CheckDataTestId -->|Yes| AddDataTestId["Add data-testid<br/>priority=2, conf=0.90<br/>priority++"]
        CheckDataTestId -->|No| CheckAria
        
        AddDataTestId --> CheckAria["Has aria-label?"]
        CheckAria -->|Yes| AddAria["Add aria-label<br/>priority=3, conf=0.85<br/>priority++"]
        CheckAria -->|No| CheckCSS
        
        AddAria --> CheckCSS["Has CSS selector?"]
        CheckCSS -->|Yes| AddCSS["Add css selector<br/>priority=4, conf=0.75-0.80<br/>priority++"]
        CheckCSS -->|No| CheckXPath
        
        AddCSS --> CheckXPath["Has XPath?"]
        CheckXPath -->|Yes| AddXPath["Add xpath selector<br/>priority=5, conf=0.60-0.80<br/>priority++"]
        CheckXPath -->|No| CheckPlaceholder
        
        AddXPath --> CheckPlaceholder["Has placeholder?"]
        CheckPlaceholder -->|Yes| AddPlaceholder["Add placeholder<br/>priority=6, conf=0.65<br/>priority++"]
        CheckPlaceholder -->|No| Done
        
        AddPlaceholder --> Done["Complete multi-selector array"]
    end
```

**Priority Assignment Logic**

The priority ordering is implemented in `RecorderToolExecutor.execute()` for the `register_element` tool:

1. **Priority 1**: ID selectors (including CSS ID selectors starting with `#` or `[id=`)
2. **Priority 2**: `data-testid` attributes
3. **Priority 3**: `aria-label` attributes
4. **Priority 4**: CSS selectors (with template detection)
5. **Priority 5**: XPath expressions (optimized attribute-based preferred over absolute paths)
6. **Priority 6**: Placeholder attributes (for input fields)

The priority number is assigned sequentially, so if an element has ID, data-testid, and CSS selectors, they receive priorities 1, 2, and 3 respectively.

Sources: [services/action-builder/src/recorder/RecorderToolExecutor.ts:350-434]()

## Confidence Scores

Confidence scores indicate selector stability and are used by the `SelectorOptimizer` to filter unreliable selectors. Higher confidence means the selector is less likely to break when the page changes.

### Confidence Score Table

| Selector Type | Base Confidence | Factors Affecting Score |
|---------------|----------------|-------------------------|
| `id` | 0.95 | Highest - IDs are unique and rarely change |
| `data-testid` | 0.90 | Very stable - explicitly added for testing |
| `aria-label` | 0.85 | Stable - accessibility attribute |
| `css` (template) | 0.80 | Moderately stable - parameterized pattern |
| `css` (standard) | 0.75 | Moderate - depends on class stability |
| `xpath` (optimized) | 0.80 | Moderately stable - attribute-based XPath |
| `xpath` (absolute) | 0.60 | Low - breaks with structural changes |
| `placeholder` | 0.65 | Low-moderate - text may change |

### Confidence Adjustment

The `SelectorOptimizer` can reduce confidence scores for selectors that contain unstable patterns:

- Dynamic counters (e.g., `item-123`, `post-456`)
- Hash-like patterns (e.g., `sc-xyz123`, `css-abc789`)
- Timestamp-based classes
- Generated IDs with random suffixes

Sources: [services/action-builder/src/recorder/RecorderToolExecutor.ts:354-434](), [services/action-builder/src/validator/SelectorValidator.ts:315-488]()

## Template Patterns

Template selectors support parameterization for dynamic elements. This enables recording reusable patterns that work across similar elements with different values.

```mermaid
graph TB
    subgraph "Template Selector Flow"
        Original["Original CSS Selector<br/>a[href='/category/123']"]
        
        Original --> Detect["detectTemplatePattern()<br/>Check for numeric/variable parts"]
        
        Detect -->|"Pattern found"| Create["Create Template<br/>value: 'a[href=\"/category/{{category_id}}\"]'<br/>isTemplate: true"]
        Detect -->|"No pattern"| Regular["Regular Selector<br/>value: 'a[href=\"/category/123\"]'<br/>isTemplate: false"]
        
        Create --> AddParams["Add templateParams<br/>[{name: 'category_id', description: '...'}]"]
        
        AddParams --> Store["Store in SelectorItem"]
        Regular --> Store
        
        Store --> Usage["At Runtime"]
        Usage --> Resolve["resolveSelectorValue()<br/>Replace {{category_id}} with actual value"]
    end
```

### Template Parameter Definition

```typescript
interface TemplateParam {
  name: string;           // Parameter name (e.g., "category_id")
  description: string;    // Human-readable description
  example?: string;       // Example value
}
```

### Template Usage Example

**Recording Phase**:
```json
{
  "type": "css",
  "value": "a[href=\"/search?q={{query}}\"]",
  "priority": 4,
  "confidence": 0.80,
  "isTemplate": true,
  "templateParams": [
    {
      "name": "query",
      "description": "Search query parameter",
      "example": "machine learning"
    }
  ]
}
```

**Validation Phase**:
```typescript
// Provide template parameters
const templateParams = { query: "artificial intelligence" };

// Resolved selector: a[href="/search?q=artificial intelligence"]
const resolved = resolveSelectorValue(selector, templateParams);
```

Sources: [services/action-builder/src/recorder/RecorderToolExecutor.ts:28-30](), [services/action-builder/src/recorder/RecorderToolExecutor.ts:392-412](), [services/action-builder/src/validator/SelectorValidator.ts:542-571]()

## Multi-Selector Extraction Process

```mermaid
sequenceDiagram
    participant LLM as "LLM / AI Client"
    participant Executor as "RecorderToolExecutor"
    participant Browser as "BrowserAdapter"
    participant Handler as "extractMultipleSelectors"
    
    LLM->>Executor: register_element tool call<br/>(element_id, xpath_selector, css_selector)
    
    alt XPath provided
        Executor->>Browser: getElementAttributesFromXPath(xpath)
        Browser-->>Executor: {id, dataTestId, cssSelector, ariaLabel, placeholder, optimizedXPath}
        Note over Executor: Auto-extracted attributes from page
    else No XPath
        Executor->>Browser: observe(description)
        Browser-->>Executor: observeResult with selector
        Note over Executor: Find real selector via AI vision
    end
    
    Executor->>Handler: extractMultipleSelectors(observeResult, cssSelector, additionalAttrs)
    
    Note over Handler: Build multi-selector array<br/>Priority ordering:
    Handler->>Handler: 1. Check for ID → add id selector
    Handler->>Handler: 2. Check for data-testid → add data-testid selector
    Handler->>Handler: 3. Check for aria-label → add aria-label selector
    Handler->>Handler: 4. Check for CSS → detectTemplatePattern() → add css selector
    Handler->>Handler: 5. Add XPath (prefer optimized over absolute)
    Handler->>Handler: 6. Check for placeholder → add placeholder selector
    
    Handler-->>Executor: SelectorItem[] array
    
    alt No selectors extracted
        Executor-->>LLM: Error: "no_selectors_found"
        Note over LLM: Element may not exist on page
    else Selectors found
        Executor->>Executor: registerElement(ElementCapability)
        Executor-->>LLM: Success with selectors array
    end
```

### Key Functions

| Function | Location | Purpose |
|----------|----------|---------|
| `extractMultipleSelectors` | Handler callback | Builds prioritized selector array from available attributes |
| `detectTemplatePattern` | Handler callback | Identifies parameterizable patterns in CSS selectors |
| `getElementAttributesFromXPath` | BrowserAdapter | Extracts all available attributes from an XPath-located element |
| `createIdSelector` | utils/string.js | Handles special characters in ID selectors (e.g., dots) |

Sources: [services/action-builder/src/recorder/RecorderToolExecutor.ts:192-233](), [services/action-builder/src/recorder/RecorderToolExecutor.ts:275-476]()

## Selector Validation

The `SelectorValidator` validates selector effectiveness by checking three states: **exists**, **visible**, and **interactable**.

```mermaid
graph TB
    subgraph "Selector Validation Process - validateSingleSelector"
        Input["SelectorItem + templateParams"]
        
        Input --> Resolve["resolveSelectorValue()<br/>Replace template params"]
        
        Resolve -->|Error| ReturnError["Return: valid=false, error='Missing param'"]
        Resolve -->|Success| CheckType["Check selector.type"]
        
        CheckType -->|xpath| XPathEval["evaluateXPathInBrowser(page, xpath)<br/>Use document.evaluate() directly"]
        CheckType -->|other| LocatorCount["page.locator(selector).count()"]
        
        XPathEval --> CountCheck
        LocatorCount --> CountCheck
        
        CountCheck{"count > 0?"}
        CountCheck -->|No| NotFound["Return: valid=false, error='Element not found'"]
        CountCheck -->|Yes| VisCheck["Check Visibility"]
        
        VisCheck -->|xpath| XPathVis["page.evaluate()<br/>getBoundingClientRect()<br/>getComputedStyle()"]
        VisCheck -->|other| LocatorVis["locator.isVisible()"]
        
        XPathVis --> InteractCheck
        LocatorVis --> InteractCheck
        
        InteractCheck{"visible?"}
        InteractCheck -->|No| ReturnHidden["Return: valid=true, visible=false, interactable=false"]
        InteractCheck -->|Yes| CheckInteract["Check Interactability"]
        
        CheckInteract --> PointerEvents["Check pointer-events !== 'none'"]
        CheckInteract --> Opacity["Check opacity > 0"]
        CheckInteract --> Enabled["Check not disabled"]
        CheckInteract --> Obstruction["Check not obstructed by other element"]
        
        PointerEvents --> Combine
        Opacity --> Combine
        Enabled --> Combine
        Obstruction --> Combine
        
        Combine["Combine all checks"] --> ReturnResult["Return: valid=true, visible=true, interactable=[true/false]"]
    end
```

### Validation States

| State | Meaning | Example Scenario |
|-------|---------|------------------|
| `valid: true, visible: true, interactable: true` | Fully functional | Active button ready for click |
| `valid: true, visible: true, interactable: false` | Element exists but disabled | Disabled submit button or obstructed element |
| `valid: true, visible: false, interactable: false` | Element exists but hidden | Display:none or zero-sized element |
| `valid: false` | Element not found | Selector no longer matches any element |

### XPath Validation Special Handling

The validator uses direct browser evaluation for XPath selectors via `evaluateXPathInBrowser()` instead of Playwright/Stagehand's locator API. This is necessary because:

1. Stagehand's `page.locator('xpath=...')` uses CDP (Chrome DevTools Protocol)
2. CDP has issues with relative XPath expressions (e.g., `//button[@id="submit"]`)
3. Absolute XPath paths work, but relative XPath returns `count=0` incorrectly
4. Direct `document.evaluate()` in browser context handles all XPath correctly

Sources: [services/action-builder/src/validator/SelectorValidator.ts:315-488](), [services/action-builder/src/validator/SelectorValidator.ts:507-540]()

## Selector Optimization

XPath selectors undergo optimization to prefer attribute-based expressions over absolute paths:

```mermaid
graph LR
    subgraph "XPath Optimization - generateOptimizedXPath"
        Absolute["Absolute XPath<br/>/html[1]/body[1]/div[3]/button[1]"]
        
        Absolute --> ExtractAttrs["Extract element attributes<br/>id, data-testid, name, aria-label, class, text"]
        
        ExtractAttrs --> Priority1{"Has id or<br/>data-testid?"}
        Priority1 -->|Yes| P1Result["//button[@id='submit']<br/>or<br/>//button[@data-testid='btn']"]
        
        Priority1 -->|No| Priority2{"Has name or<br/>aria-label?"}
        Priority2 -->|Yes| P2Result["//button[@name='submit']<br/>or<br/>//button[@aria-label='Submit']"]
        
        Priority2 -->|No| Priority3{"Has stable<br/>class?"}
        Priority3 -->|Yes| P3Result["//button[contains(@class, 'btn-primary')]"]
        
        Priority3 -->|No| Priority4{"Has short<br/>text content?"}
        Priority4 -->|Yes| P4Result["//button[normalize-space()='Submit']"]
        
        Priority4 -->|No| Fallback["Use original absolute path<br/>/html[1]/body[1]/div[3]/button[1]"]
        
        P1Result --> Assign["Assign confidence 0.80"]
        P2Result --> Assign
        P3Result --> Assign
        P4Result --> Assign
        Fallback --> AssignLow["Assign confidence 0.60"]
    end
```

**Optimization Priority**:
1. **ID-based**: `//tagName[@id="value"]` (confidence: 0.80)
2. **data-testid**: `//tagName[@data-testid="value"]` (confidence: 0.80)
3. **Name/aria-label**: `//tagName[@name="value"]` or `//tagName[@aria-label="value"]` (confidence: 0.80)
4. **Stable class**: `//tagName[contains(@class, "btn-primary")]` (confidence: 0.80)
5. **Text content**: `//tagName[normalize-space()="Text"]` (confidence: 0.80)
6. **Absolute path**: `/html[1]/body[1]/...` (confidence: 0.60 - fallback only)

Sources: [services/action-builder/src/recorder/RecorderToolExecutor.ts:330-348](), [services/action-builder/src/recorder/RecorderToolExecutor.ts:414-424](), [services/action-builder/test/browser/xpath-optimizer.ut.test.ts:12-120]()

## Common Selector Patterns

### Special Character Handling

```mermaid
graph TB
    subgraph "ID Selector with Special Characters"
        Input["element.id = 'cs.AI'"]
        
        Input --> Check["createIdSelector(id)"]
        
        Check --> HasDot{"Contains<br/>special chars?"}
        HasDot -->|Yes| Attribute["Use attribute selector<br/>[id='cs.AI']"]
        HasDot -->|No| Hash["Use hash selector<br/>#simpleId"]
        
        Attribute --> Result["SelectorItem<br/>type: 'id'<br/>value: '[id=\"cs.AI\"]'"]
        Hash --> Result2["SelectorItem<br/>type: 'id'<br/>value: '#simpleId'"]
    end
```

The `createIdSelector()` utility handles IDs with special characters (dots, colons, brackets) by using attribute selectors instead of hash selectors.

**Examples**:
- `cs.AI` → `[id="cs.AI"]` (not `#cs.AI` which would fail)
- `item:123` → `[id="item:123"]`
- `simple` → `#simple`

Sources: [services/action-builder/src/recorder/RecorderToolExecutor.ts:355-370](), [services/action-builder/test/browser/xpath-optimizer.ut.test.ts:293-300]()

### CSS Selector Template Detection

CSS selectors with numeric or variable parts are automatically detected and converted to templates:

```javascript
// Example: Dynamic category link
// Detected pattern: a[href="/category/123"]
// Becomes template: a[href="/category/{{category_id}}"]

const templateInfo = detectTemplatePattern(cssSelector);
if (templateInfo) {
  selector = {
    type: "css",
    value: templateInfo.template,  // a[href="/category/{{category_id}}"]
    isTemplate: true,
    templateParams: templateInfo.params,
    confidence: 0.8
  };
}
```

Sources: [services/action-builder/src/recorder/RecorderToolExecutor.ts:392-412]()

## Integration with Recording Tools

The recording tools expose selector types through the `register_element` tool schema:

```typescript
// From RecorderTools.ts
{
  name: "register_element",
  parameters: {
    element_id: string,      // Required: unique identifier
    description: string,     // Required: element description
    css_selector: string,    // Optional: CSS selector from LLM
    xpath_selector: string,  // Optional: XPath from observe_page
    aria_label: string,      // Optional: ARIA label
    placeholder: string,     // Optional: placeholder text
    // ... other fields
  }
}
```

When the LLM calls this tool, the `RecorderToolExecutor`:
1. Validates `element_id` is not empty/undefined
2. Attempts to find real selectors via `observe_page` if XPath is missing
3. Extracts all available attributes from the element
4. Builds prioritized multi-selector array
5. Creates `ElementCapability` with selectors array
6. Registers the element for storage

Sources: [services/action-builder/src/recorder/RecorderTools.ts:63-134](), [services/action-builder/src/recorder/RecorderToolExecutor.ts:275-476]()

---

# Page: Tool Definitions

# Tool Definitions

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [packages/js-sdk/src/api-client.ts](packages/js-sdk/src/api-client.ts)
- [packages/js-sdk/src/client.ts](packages/js-sdk/src/client.ts)
- [packages/js-sdk/src/tool-defs.ts](packages/js-sdk/src/tool-defs.ts)
- [packages/js-sdk/src/types.ts](packages/js-sdk/src/types.ts)

</details>



This document describes the tool definition system used by Actionbook's SDK for integrating with LLM frameworks and AI agents. Tool definitions provide structured schemas and descriptions that enable AI models to discover and invoke Actionbook's search and retrieval capabilities.

For information about capability types (ElementCapability, PageCapability), see [Capability Types](#7.1). For selector structures, see [Selector Types](#7.2).

## Purpose and Scope

Tool definitions serve as the bridge between Actionbook's API and AI frameworks that support function calling (OpenAI, Anthropic, Vercel AI SDK, etc.). Each tool definition includes:

- A descriptive name and purpose for LLM understanding
- Input schema in multiple formats (JSON Schema and Zod)
- Parameter validation and constraints
- Integration examples and usage patterns

The SDK exposes four primary tools: `searchActions`, `getActionById`, `listSources`, and `searchSources`.

**Sources:** [packages/js-sdk/src/tool-defs.ts:1-238]()

## Tool Schema Architecture

### Core Interfaces

The tool system defines two primary interfaces for describing tools to LLM frameworks:

```mermaid
classDiagram
    class ToolDefinition~T~ {
        +string name
        +string description
        +ZodType inputSchema
        +handler(input) Promise~string~
    }
    
    class ToolParams~T~ {
        +Record json
        +ZodType zod
    }
    
    class SearchActionsMethod {
        +description: string
        +params: ToolParams
        +(query: string) Promise~ChunkSearchResult~
        +(options: SearchActionsInput) Promise~ChunkSearchResult~
    }
    
    class GetActionByIdMethod {
        +description: string
        +params: ToolParams
        +(id: string) Promise~ChunkActionDetail~
        +(options: GetActionByIdInput) Promise~ChunkActionDetail~
    }
    
    ToolDefinition --> ToolParams : uses
    SearchActionsMethod --> ToolParams : has
    GetActionByIdMethod --> ToolParams : has
```

**`ToolDefinition<T>`** - Generic interface for defining tools with typed input schemas and handlers. Used primarily for MCP and custom integrations.

**`ToolParams<T>`** - Dual-format schema container that provides both JSON Schema (for OpenAI, Anthropic, Gemini SDKs) and Zod schema (for Vercel AI SDK) representations of the same input structure.

**Sources:** [packages/js-sdk/src/tool-defs.ts:5-36](), [packages/js-sdk/src/client.ts:29-93]()

### Schema Format Conversion

```mermaid
graph LR
    ZodSchema["Zod Schema<br/>(Runtime validation)"]
    JSONSchema["JSON Schema<br/>(LLM frameworks)"]
    ToolParams["ToolParams<br/>json + zod"]
    
    ZodSchema -->|"createParams()"| ToolParams
    ZodSchema -->|"zodToJsonSchema()"| JSONSchema
    JSONSchema --> ToolParams
    
    ToolParams -->|".zod"| VercelAI["Vercel AI SDK"]
    ToolParams -->|".json"| OpenAI["OpenAI SDK"]
    ToolParams -->|".json"| Anthropic["Anthropic SDK"]
    ToolParams -->|".json"| Gemini["Gemini SDK"]
```

The `createParams()` function converts a Zod schema into a `ToolParams` object containing both formats. For MCP compatibility, `createCleanParams()` provides additional JSON Schema cleaning.

**Sources:** [packages/js-sdk/src/tool-defs.ts:39-58]()

## Tool Reference

### searchActions

Searches for action manuals by keyword using hybrid search (full-text + vector similarity).

#### Schema Definition

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| `query` | string | Yes | 1-200 chars | Search keyword (e.g., 'airbnb search', 'login button') |
| `type` | enum | No | vector/fulltext/hybrid | Search algorithm (default: hybrid) |
| `limit` | number | No | 1-100 | Maximum results to return (default: 5) |
| `sourceIds` | string | No | - | Comma-separated source IDs (e.g., '1,2,3') |
| `minScore` | number | No | 0-1 | Minimum similarity threshold (e.g., 0.7) |

**Zod Schema:** [packages/js-sdk/src/tool-defs.ts:64-91]()

#### Tool Description

The LLM receives this description when deciding whether to use the tool:

> Search for action manuals by keyword. Use this tool to find website actions, page elements, and their selectors for browser automation.
>
> **Example queries:**
> - "airbnb search" → find Airbnb search-related actions
> - "google login" → find Google login actions
> - "linkedin message" → find LinkedIn messaging actions
>
> **Typical workflow:**
> 1. Search for actions: searchActions("airbnb search")
> 2. Get action_id from results (URL-based, e.g., "https://example.com/page")
> 3. Get full details: getActionById("https://example.com/page")
> 4. Use returned selectors with Playwright/browser automation
>
> Returns URL-based action IDs with content previews and relevance scores.

**Sources:** [packages/js-sdk/src/tool-defs.ts:95-110]()

#### Return Type

Returns a `ChunkSearchResult` with the following structure:

```typescript
{
  success: boolean
  query: string
  results: Array<{
    action_id: string      // URL-based identifier
    content: string        // Content preview
    score: number          // Relevance score (0-1)
    createdAt: string      // Timestamp
  }>
  count: number           // Results returned
  total: number           // Total matches
  hasMore: boolean        // Pagination indicator
}
```

**Sources:** [packages/js-sdk/src/types.ts:9-21]()

### getActionById

Retrieves complete action details including DOM selectors and step-by-step instructions.

#### Schema Definition

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| `id` | string | Yes | min 1 char | Action ID (full URL or fuzzy match) |

**Action ID Format:**
- Full URL: `https://example.com/docs/page`
- Domain + path: `example.com/docs/page` (auto-matches https://example.com/docs/page)
- Domain only: `releases.rs` (matches https://releases.rs/)
- With chunk: `https://example.com/page#chunk-1`

**Zod Schema:** [packages/js-sdk/src/tool-defs.ts:118-123]()

#### Tool Description

> Get complete action details by action ID, including DOM selectors and step-by-step instructions.
>
> **What you get:**
> - Full action content/documentation
> - Page element selectors (CSS, XPath)
> - Element types and allowed methods (click, type, extract, etc.)
> - Document metadata (title, URL)
>
> **Use returned selectors with browser automation:**
> ```javascript
> const selector = '.search-button';
> await page.locator(selector).click();
> ```
>
> **Typical workflow:**
> 1. Search for actions: searchActions("airbnb search")
> 2. Get action_id from results (e.g., "https://docs.airbnb.com/search")
> 3. Get full details: getActionById("docs.airbnb.com/search") // fuzzy match works!
> 4. Extract selectors and use in automation

**Sources:** [packages/js-sdk/src/tool-defs.ts:127-152]()

#### Return Type

Returns a `ChunkActionDetail` with complete action information:

```typescript
{
  action_id: string           // URL-based identifier
  content: string             // Full documentation
  elements: string | null     // JSON string of element selectors
  createdAt: string           // Timestamp
  documentId: number          // Source document reference
  documentTitle: string       // Page title
  documentUrl: string         // Original page URL
  chunkIndex: number          // Content chunk position
  heading: string | null      // Section heading
  tokenCount: number          // Content size
}
```

The `elements` field contains a JSON string that can be parsed into a `ParsedElements` structure:

```typescript
{
  [key: string]: {
    css_selector?: string
    xpath_selector?: string
    description?: string
    element_type?: string
    allow_methods?: string[]
    depends_on?: string
  }
}
```

**Sources:** [packages/js-sdk/src/types.ts:26-51]()

### listSources

Lists all available sources (websites) in the Actionbook database.

#### Schema Definition

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| `limit` | number | No | 1-200 | Maximum sources to return (default: 50) |

**Zod Schema:** [packages/js-sdk/src/tool-defs.ts:160-168]()

#### Tool Description

> List all available sources (websites) in the Actionbook database.
>
> Use this tool to:
> - Discover what websites/sources are available
> - Get source IDs for filtering search_actions
> - View source metadata (name, URL, description, tags)
>
> **Typical workflow:**
> 1. List sources: listSources()
> 2. Note the source ID you want to search
> 3. Search actions: searchActions({ query: "login", sourceIds: "1" })
>
> Returns source IDs, names, URLs, and metadata for each source.

**Sources:** [packages/js-sdk/src/tool-defs.ts:172-184]()

#### Return Type

Returns a `SourceListResult`:

```typescript
{
  success: boolean
  results: Array<{
    id: number
    name: string
    baseUrl: string
    description: string | null
    domain: string | null
    tags: string[]
    healthScore: number | null
    lastCrawledAt: string | null
    createdAt: string
  }>
  count: number
}
```

**Sources:** [packages/js-sdk/src/types.ts:56-75]()

### searchSources

Searches for sources (websites) by keyword across name, description, domain, URL, and tags.

#### Schema Definition

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| `query` | string | Yes | 1-200 chars | Search keyword for source metadata |
| `limit` | number | No | 1-100 | Maximum results (default: 10) |

**Zod Schema:** [packages/js-sdk/src/tool-defs.ts:192-207]()

#### Tool Description

> Search for sources (websites) by keyword.
>
> Use this tool to:
> - Find specific websites/sources by name or domain
> - Search by description or tags
> - Get source IDs for filtering search_actions
>
> **Search fields:**
> - Source name
> - Description
> - Domain
> - Base URL
> - Tags
>
> **Typical workflow:**
> 1. Search sources: searchSources({ query: "airbnb" })
> 2. Note the source ID from results
> 3. Search actions: searchActions({ query: "login", sourceIds: "1" })
>
> **Example queries:**
> - "airbnb" → find Airbnb source
> - "linkedin" → find LinkedIn source
> - "e-commerce" → find sources tagged with e-commerce
>
> Returns matching source IDs, names, URLs, and metadata.

**Sources:** [packages/js-sdk/src/tool-defs.ts:211-235]()

#### Return Type

Returns a `SourceSearchResult`:

```typescript
{
  success: boolean
  query: string
  results: Array<SourceItem>  // Same structure as listSources
  count: number
}
```

**Sources:** [packages/js-sdk/src/types.ts:80-85]()

## SDK Integration Architecture

```mermaid
graph TB
    subgraph "Tool Definitions Layer"
        searchActionsSchema["searchActionsSchema<br/>(Zod)"]
        getActionByIdSchema["getActionByIdSchema<br/>(Zod)"]
        listSourcesSchema["listSourcesSchema<br/>(Zod)"]
        searchSourcesSchema["searchSourcesSchema<br/>(Zod)"]
        
        createParams["createParams()<br/>Zod → ToolParams"]
    end
    
    subgraph "SDK Client Layer"
        ActionbookClient["Actionbook<br/>(client.ts)"]
        
        searchActionsMethod["searchActions()<br/>+ description<br/>+ params"]
        getActionByIdMethod["getActionById()<br/>+ description<br/>+ params"]
        listSourcesMethod["listSources()<br/>+ description<br/>+ params"]
        searchSourcesMethod["searchSources()<br/>+ description<br/>+ params"]
    end
    
    subgraph "API Client Layer"
        ApiClient["ApiClient<br/>(api-client.ts)"]
        
        searchActionsAPI["searchActions()<br/>/api/actions/search"]
        getActionByIdAPI["getActionById()<br/>/api/actions"]
        listSourcesAPI["listSources()<br/>/api/sources"]
        searchSourcesAPI["searchSources()<br/>/api/sources/search"]
    end
    
    searchActionsSchema --> createParams
    getActionByIdSchema --> createParams
    listSourcesSchema --> createParams
    searchSourcesSchema --> createParams
    
    createParams -->|"params.json<br/>params.zod"| searchActionsMethod
    createParams --> getActionByIdMethod
    createParams --> listSourcesMethod
    createParams --> searchSourcesMethod
    
    ActionbookClient --> searchActionsMethod
    ActionbookClient --> getActionByIdMethod
    ActionbookClient --> listSourcesMethod
    ActionbookClient --> searchSourcesMethod
    
    searchActionsMethod --> ApiClient
    getActionByIdMethod --> ApiClient
    listSourcesMethod --> ApiClient
    searchSourcesMethod --> ApiClient
    
    ApiClient --> searchActionsAPI
    ApiClient --> getActionByIdAPI
    ApiClient --> listSourcesAPI
    ApiClient --> searchSourcesAPI
```

The SDK implements a three-layer architecture:

1. **Tool Definitions Layer** - Defines Zod schemas and converts them to dual-format `ToolParams`
2. **SDK Client Layer** - Exposes methods with attached tool definitions (description + params)
3. **API Client Layer** - Handles HTTP requests, retries, and error handling

**Sources:** [packages/js-sdk/src/tool-defs.ts:1-238](), [packages/js-sdk/src/client.ts:1-236](), [packages/js-sdk/src/api-client.ts:1-188]()

## Method Attachment Pattern

Each SDK method has tool definition metadata attached as properties:

```mermaid
graph LR
    subgraph "Method Object"
        Function["Function<br/>(query) => Promise"]
        Description["description<br/>property"]
        Params["params<br/>property"]
    end
    
    Function -->|"callable"| APIClient["API Client"]
    Description -->|"for LLMs"| LLMFramework["LLM Framework"]
    Params -->|"for LLMs"| LLMFramework
    
    subgraph "ToolParams Structure"
        JSON["json: Record<br/>(JSON Schema)"]
        Zod["zod: ZodType<br/>(Zod schema)"]
    end
    
    Params --> JSON
    Params --> Zod
```

This pattern enables usage in multiple contexts:

**Direct Invocation:**
```typescript
const client = new Actionbook({ apiKey: 'xxx' })
const results = await client.searchActions('airbnb search')
```

**LLM Framework Integration:**
```typescript
// Access tool metadata
console.log(client.searchActions.description)  // String for LLM
console.log(client.searchActions.params.json)  // JSON Schema
console.log(client.searchActions.params.zod)   // Zod schema
```

**Sources:** [packages/js-sdk/src/client.ts:144-234]()

## LLM Framework Integration Examples

### Tool Definition Export Structure

```mermaid
graph TB
    subgraph "Method With Metadata"
        searchActions["searchActions()"]
        description["description: string"]
        params["params: ToolParams"]
    end
    
    subgraph "Framework Adapters"
        OpenAITools["OpenAI Tools<br/>tools: [{ type: 'function',<br/>function: { name, description,<br/>parameters } }]"]
        
        AnthropicTools["Anthropic Tools<br/>tools: [{ name, description,<br/>input_schema }]"]
        
        VercelAITools["Vercel AI Tools<br/>tools: { toolName: tool(params.zod,<br/>description, handler) }"]
        
        GeminiTools["Gemini Tools<br/>tools: [{ functionDeclarations:<br/>[{ name, description,<br/>parameters }] }]"]
    end
    
    description --> OpenAITools
    params -->|".json"| OpenAITools
    
    description --> AnthropicTools
    params -->|".json"| AnthropicTools
    
    description --> VercelAITools
    params -->|".zod"| VercelAITools
    
    description --> GeminiTools
    params -->|".json"| GeminiTools
```

**Vercel AI SDK Integration:**
```typescript
import { Actionbook } from '@actionbookdev/sdk'
import { tool } from 'ai'

const client = new Actionbook({ apiKey: 'xxx' })

const tools = {
  searchActions: tool(
    client.searchActions.params.zod,
    client.searchActions.description,
    async (input) => {
      const result = await client.searchActions(input)
      return JSON.stringify(result)
    }
  )
}
```

**OpenAI SDK Integration:**
```typescript
const tools = [{
  type: 'function',
  function: {
    name: 'searchActions',
    description: client.searchActions.description,
    parameters: client.searchActions.params.json
  }
}]
```

**Anthropic SDK Integration:**
```typescript
const tools = [{
  name: 'searchActions',
  description: client.searchActions.description,
  input_schema: client.searchActions.params.json
}]
```

**Sources:** [packages/js-sdk/src/client.ts:167-189](), [packages/js-sdk/src/tool-defs.ts:41-58]()

## Type Safety and Validation

```mermaid
graph LR
    UserInput["User Input<br/>(unknown)"]
    ZodValidation["Zod Schema<br/>Validation"]
    TypedInput["Typed Input<br/>(z.infer<T>)"]
    APICall["API Request"]
    TypedResponse["Typed Response"]
    
    UserInput --> ZodValidation
    ZodValidation -->|"Valid"| TypedInput
    ZodValidation -->|"Invalid"| Error["ZodError"]
    TypedInput --> APICall
    APICall --> TypedResponse
```

Tool schemas provide runtime validation through Zod and compile-time type safety through TypeScript inference:

**Runtime Validation:**
```typescript
// Zod validates at runtime
const input = searchActionsSchema.parse({
  query: 'airbnb search',
  limit: 10
})
// Throws ZodError if invalid
```

**Compile-Time Types:**
```typescript
// TypeScript infers types from Zod schema
type SearchActionsInput = z.infer<typeof searchActionsSchema>
// { query: string; type?: 'vector' | 'fulltext' | 'hybrid'; ... }
```

**Sources:** [packages/js-sdk/src/tool-defs.ts:64-91](), [packages/js-sdk/src/tool-defs.ts:93]()

## Tool Lifecycle and Error Handling

```mermaid
sequenceDiagram
    participant LLM as "LLM"
    participant SDK as "SDK Method"
    participant APIClient as "ApiClient"
    participant API as "API Service"
    
    LLM->>SDK: Call searchActions({ query: "login" })
    SDK->>SDK: Normalize input
    SDK->>APIClient: searchActions(params)
    
    loop Max 3 retries
        APIClient->>API: GET /api/actions/search?q=login
        alt Success
            API-->>APIClient: 200 OK + results
            APIClient-->>SDK: ChunkSearchResult
            SDK-->>LLM: JSON string
        else Rate Limited
            API-->>APIClient: 429 Too Many Requests
            APIClient->>APIClient: Wait + retry
        else Timeout
            API-->>APIClient: Timeout
            APIClient->>APIClient: Wait + retry
        else Not Found
            API-->>APIClient: 404 Not Found
            APIClient-->>SDK: ActionbookError
            SDK-->>LLM: Error message
        end
    end
```

The API client implements automatic retry logic with exponential backoff for transient failures (timeouts, rate limits) but fails fast for permanent errors (404, invalid input).

**Retry Configuration:**
- Max retries: 3 attempts
- Retry delay: 1000ms base (configurable)
- Timeout: 30000ms default (configurable)

**Sources:** [packages/js-sdk/src/api-client.ts:111-174]()

---

# Page: Development Guide

# Development Guide

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitignore](.gitignore)
- [LICENSE](LICENSE)
- [README.md](README.md)
- [mcp-servers.json](mcp-servers.json)
- [package.json](package.json)
- [packages/cli/package.json](packages/cli/package.json)
- [packages/js-sdk/package.json](packages/js-sdk/package.json)
- [packages/mcp/package.json](packages/mcp/package.json)
- [pnpm-lock.yaml](pnpm-lock.yaml)
- [pnpm-workspace.yaml](pnpm-workspace.yaml)
- [services/action-builder/.nvmrc](services/action-builder/.nvmrc)
- [turbo.json](turbo.json)

</details>



This document provides an overview of the Actionbook development environment, workspace structure, and common development workflows. It is intended for contributors who want to modify or extend the Actionbook codebase.

For detailed information on specific topics, see:
- [Monorepo Structure](#8.1) - Workspace organization and package categories
- [Build System](#8.2) - Turborepo configuration and task definitions
- [Local Development Setup](#8.3) - Step-by-step environment setup
- [Testing](#8.4) - Testing strategies and running tests

## Prerequisites

The Actionbook monorepo requires the following tools:

| Tool | Minimum Version | Recommended | Purpose |
|------|----------------|-------------|---------|
| **Node.js** | 18.0.0 | 20+ | JavaScript runtime |
| **pnpm** | 10.0.0 | 10.24.0 | Package manager |
| **PostgreSQL** | 14+ | 16+ | Database (local or hosted) |
| **Git** | 2.0+ | Latest | Version control |

The project uses pnpm workspaces for monorepo management and Turborepo for build orchestration. The package manager is enforced via the `packageManager` field in [package.json:7]().

Sources: [README.md:706-709](), [package.json:7](), [services/action-builder/.nvmrc:1]()

## Workspace Organization

The monorepo is organized into multiple workspace categories defined in [pnpm-workspace.yaml:1-6](). The following diagram shows the physical directory structure:

### Monorepo Directory Structure

```mermaid
graph TB
    root["actionbook/ (root)"]
    
    root --> packages["packages/"]
    root --> services["services/"]
    root --> playground["playground/"]
    root --> eval["eval/"]
    
    packages --> cli["cli/<br/>@actionbookdev/cli"]
    packages --> sdk["js-sdk/<br/>@actionbookdev/sdk"]
    packages --> mcp["mcp/<br/>@actionbookdev/mcp"]
    packages --> toolsAI["tools-ai-sdk/<br/>@actionbookdev/tools-ai-sdk"]
    
    services --> db["db/<br/>@actionbookdev/db"]
    services --> common["common/"]
    services --> actionBuilder["action-builder/"]
    services --> playbookBuilder["playbook-builder/"]
    services --> knowledgeBuilder["knowledge-builder/"]
    
    common --> browser["browser/<br/>@actionbookdev/browser"]
    common --> browserProfile["browser-profile/<br/>@actionbookdev/browser-profile"]
    
    playground --> stagehandAgent["stagehand-agent/"]
    playground --> generateScraper["generate-scraper-script/"]
    playground --> scrapers["actionbook-scraper/<br/>arxiv-viewer/<br/>rust-learner/<br/>lib-rs-scraper/"]
    
    eval --> evalTests["braintrust/<br/>eval tests"]
    
    style packages fill:#f9f9f9
    style services fill:#f9f9f9
    style playground fill:#f9f9f9
    style eval fill:#f9f9f9
```

The workspace configuration includes:
- `packages/*` - Published npm packages (CLI, SDK, MCP)
- `services/*` and `services/*/*` - Backend services and shared libraries
- `playground/*` - Example projects and integrations
- `eval` - Evaluation and testing harness

Sources: [pnpm-workspace.yaml:1-6](), [README.md:703]()

## Development Workflow

The typical development workflow involves installing dependencies, making code changes, running tests, and building packages. The following diagram shows the relationship between common development commands:

### Development Task Flow

```mermaid
graph LR
    install["pnpm install"]
    envSetup["Configure .env files"]
    migrate["cd services/db &&<br/>pnpm migrate"]
    
    dev["pnpm dev"]
    build["pnpm build"]
    test["pnpm test"]
    lint["pnpm lint"]
    clean["pnpm clean"]
    
    install --> envSetup
    envSetup --> migrate
    migrate --> dev
    migrate --> build
    
    build --> test
    build --> lint
    
    dev -.->|"Watch mode"| codeChange["Code changes"]
    codeChange -.->|"Auto-rebuild"| dev
    
    clean --> build
    
    style install fill:#f9f9f9
    style envSetup fill:#f9f9f9
    style migrate fill:#f9f9f9
```

All workspace scripts defined in [package.json:8-14]() use Turborepo to coordinate task execution across packages. Turborepo handles dependency ordering, parallel execution, and caching as configured in [turbo.json:1-22]().

Sources: [package.json:8-14](), [turbo.json:1-22](), [README.md:712-735]()

## Quick Start

To begin development, follow these high-level steps (detailed instructions in [Local Development Setup](#8.3)):

**1. Clone the repository:**
```bash
git clone https://github.com/actionbook/actionbook.git
cd actionbook
```

**2. Install dependencies:**
```bash
pnpm install
```

This installs all dependencies for all workspace packages. The pnpm workspace protocol (`workspace:*`) is used for internal package references as seen in [packages/cli/package.json:27]() and [packages/mcp/package.json:32]().

**3. Configure environment variables:**

Copy `.env.example` to `.env` in the following packages:
- `services/db` - Database connection (required)
- `apps/api-service` - API server configuration (optional)
- `services/action-builder` - Recording service (optional)
- `services/knowledge-builder` - Crawling service (optional)

**4. Run database migrations:**
```bash
cd services/db
pnpm migrate
```

**5. Start development servers:**
```bash
# From root directory
pnpm dev
```

This starts all services in watch mode with automatic rebuilding on file changes.

Sources: [README.md:712-735](), [package.json:8-14]()

## Common Development Commands

The root package defines Turborepo tasks that orchestrate operations across the monorepo:

| Command | Description | Turbo Configuration |
|---------|-------------|---------------------|
| `pnpm install` | Install all workspace dependencies | N/A |
| `pnpm build` | Build all packages in dependency order | [turbo.json:4-7]() |
| `pnpm dev` | Start all services in watch mode | [turbo.json:8-11]() |
| `pnpm test` | Run tests across all packages | [turbo.json:12-14]() |
| `pnpm lint` | Lint all packages | [turbo.json:15-17]() |
| `pnpm clean` | Remove build artifacts | [turbo.json:18-20]() |

Individual packages can be targeted using pnpm's `--filter` flag:
```bash
pnpm --filter @actionbookdev/cli build
pnpm --filter @actionbookdev/sdk test
```

Sources: [package.json:8-14](), [turbo.json:1-22]()

## Package Dependencies

The following diagram shows the dependency relationships between published packages and internal services:

### Internal Package Dependency Graph

```mermaid
graph TB
    subgraph Published["Published Packages"]
        cli["@actionbookdev/cli"]
        mcp["@actionbookdev/mcp"]
        sdk["@actionbookdev/sdk"]
        toolsAI["@actionbookdev/tools-ai-sdk"]
    end
    
    subgraph Internal["Internal Packages"]
        db["@actionbookdev/db"]
        browser["@actionbookdev/browser"]
        browserProfile["@actionbookdev/browser-profile"]
    end
    
    subgraph Services["Services"]
        actionBuilder["services/action-builder"]
        playbookBuilder["services/playbook-builder"]
        knowledgeBuilder["services/knowledge-builder"]
    end
    
    subgraph External["External Dependencies"]
        playwright["playwright"]
        stagehand["@browserbasehq/stagehand"]
        drizzle["drizzle-orm"]
        vercelAI["ai & @ai-sdk/*"]
        agentBrowser["agent-browser"]
    end
    
    cli --> sdk
    cli --> agentBrowser
    mcp --> sdk
    toolsAI --> sdk
    
    actionBuilder --> browser
    actionBuilder --> browserProfile
    actionBuilder --> db
    actionBuilder --> mcp
    actionBuilder --> vercelAI
    
    playbookBuilder --> browser
    playbookBuilder --> browserProfile
    playbookBuilder --> db
    playbookBuilder --> vercelAI
    
    knowledgeBuilder --> browserProfile
    knowledgeBuilder --> db
    
    browser --> playwright
    browser --> stagehand
    browser --> browserProfile
    
    db --> drizzle
    
    style Published fill:#f9f9f9
    style Internal fill:#f9f9f9
    style Services fill:#f9f9f9
```

Key dependency patterns:

- **Published packages** depend only on `@actionbookdev/sdk` to maintain clean separation
- **Services** depend on internal packages (`db`, `browser`, `browser-profile`) for shared functionality
- **Internal packages** abstract external dependencies (Playwright, Stagehand, Drizzle)
- The `@actionbookdev/sdk` package has no internal dependencies, making it suitable for standalone use

The `workspace:*` protocol in package.json files (e.g., [packages/cli/package.json:27](), [packages/mcp/package.json:32]()) ensures workspace packages always use the local version during development.

Sources: [packages/cli/package.json:26-30](), [packages/mcp/package.json:31-36](), [services/action-builder/package.json:194-202]()

## Build Output and Artifacts

Build artifacts are generated according to TypeScript configurations and Turborepo output patterns:

| Package Type | Build Command | Output Directory | Configured In |
|--------------|---------------|------------------|---------------|
| Published packages | `tsc -p tsconfig.build.json` | `dist/` | [packages/cli/package.json:19]() |
| Services | `tsc` or `tsup` | `dist/` | Individual package.json |
| CLI binaries | `tsc` | `dist/index.js` | [packages/cli/package.json:10]() |

Build outputs are cached by Turborepo based on input file hashes. The cache configuration in [turbo.json:4-7]() specifies `dist/**` and `.next/**` as cacheable outputs. The `.turbo` directory (ignored via [.gitignore:61]()) stores task logs and cache metadata.

Common build artifacts that should not be committed:
- `dist/` - Compiled TypeScript output
- `node_modules/` - Dependencies
- `.turbo/` - Turborepo cache
- `*.tsbuildinfo` - TypeScript incremental build info

Sources: [turbo.json:4-7](), [.gitignore:1-75](), [packages/cli/package.json:19]()

## Environment Configuration

Services require environment variables configured in `.env` files. The repository includes `.env.example` files but not actual `.env` files (excluded via [.gitignore:26-32]()). Required configuration packages:

1. **services/db** (required)
   - Database connection string
   - Migration configuration

2. **services/action-builder** (optional)
   - LLM API keys (OpenRouter, OpenAI, Anthropic, Bedrock)
   - Browser automation settings
   - Proxy configuration

3. **services/knowledge-builder** (optional)
   - Embedding API keys
   - Crawling configuration

The development workflow requires database setup before other services can run, as shown in [README.md:726-729]().

Sources: [README.md:719-724](), [.gitignore:26-32]()

## Git Hooks

The repository uses custom git hooks via `.githooks/` directory (configured in [package.json:14]()):

```bash
git config core.hooksPath .githooks
```

This is automatically configured when running `pnpm install` via the `prepare` script. The hooks directory itself is excluded from version control via [.gitignore:66]().

Sources: [package.json:14](), [.gitignore:66]()

## Next Steps

- Review [Monorepo Structure](#8.1) for detailed workspace organization
- Follow [Local Development Setup](#8.3) for complete environment configuration
- See [Build System](#8.2) for Turborepo task configuration
- Consult [Testing](#8.4) for running and writing tests

For contribution guidelines, see the Contributing section in [README.md:737-741]().

Sources: [README.md:701-741]()

---

# Page: Monorepo Structure

# Monorepo Structure

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitignore](.gitignore)
- [LICENSE](LICENSE)
- [mcp-servers.json](mcp-servers.json)
- [package.json](package.json)
- [packages/cli/package.json](packages/cli/package.json)
- [packages/js-sdk/package.json](packages/js-sdk/package.json)
- [packages/mcp/package.json](packages/mcp/package.json)
- [pnpm-lock.yaml](pnpm-lock.yaml)
- [pnpm-workspace.yaml](pnpm-workspace.yaml)
- [services/action-builder/.nvmrc](services/action-builder/.nvmrc)
- [turbo.json](turbo.json)

</details>



This document describes the organization of the Actionbook monorepo, including workspace configuration, package categories, dependency relationships, and directory structure. For information about the build system and task orchestration, see [Build System](#8.2). For local development setup instructions, see [Local Development Setup](#8.3).

## Workspace Organization

Actionbook uses a **pnpm workspace** monorepo managed by **Turborepo**. The workspace configuration defines six top-level package groups organized by purpose.

### Workspace Configuration

The workspace is defined in [pnpm-workspace.yaml:1-7]():

```yaml
packages:
  - packages/*
  - playground/*
  - eval
  - services/*
  - services/*/*
```

This configuration creates a flat workspace where all packages can reference each other using the `workspace:*` protocol. The root [package.json:1-24]() defines global scripts that delegate to Turborepo:

- `pnpm build` - Builds all packages in dependency order
- `pnpm dev` - Runs development mode for all packages
- `pnpm test` - Runs tests across the workspace
- `pnpm lint` - Lints all packages
- `pnpm clean` - Removes build artifacts

Sources: [pnpm-workspace.yaml:1-7](), [package.json:1-24](), [turbo.json:1-23]()

## Package Categories

The monorepo contains five distinct categories of packages, each serving a specific architectural role.

### Published Packages

Four packages are published to npm under the `@actionbookdev` scope and are intended for external consumption:

| Package | Version | Purpose | Entry Point |
|---------|---------|---------|-------------|
| `@actionbookdev/cli` | 0.2.3 | Command-line interface | `dist/index.js` |
| `@actionbookdev/sdk` | 0.2.2 | Core types and API client | `dist/index.js` |
| `@actionbookdev/mcp` | 0.1.3 | Model Context Protocol server | `dist/index.js` |
| `@actionbookdev/tools-ai-sdk` | (latest) | Vercel AI SDK integration | N/A |

All published packages have `"private": false` in their package.json and include `publishConfig.access: "public"` for npm registry publication.

**CLI Package** ([packages/cli/package.json:1-57]()):
- Binary: `actionbook` command installed to `node_modules/.bin/`
- Dependencies: `@actionbookdev/sdk`, `agent-browser`, `chalk`, `commander`
- Build: TypeScript compilation to `dist/`

**SDK Package** ([packages/js-sdk/package.json:1-41]()):
- Foundation package with **no internal dependencies**
- Core dependencies: `zod`, `zod-to-json-schema`
- Provides types, tool definitions, and API client
- Used by all other published packages

**MCP Package** ([packages/mcp/package.json:1-48]()):
- Binary: `actionbook-mcp` for IDE integration
- Dependencies: `@actionbookdev/sdk`, `@modelcontextprotocol/sdk`, `undici`
- Prebuild step: Ensures SDK is built first ([packages/mcp/package.json:24]())

**Tools AI SDK Package** ([pnpm-lock.yaml:127-150]()):
- Peer dependency on Vercel AI SDK (`ai`)
- Exports tool wrappers for LLM frameworks

Sources: [packages/cli/package.json:1-57](), [packages/js-sdk/package.json:1-41](), [packages/mcp/package.json:1-48](), [pnpm-lock.yaml:127-150]()

### Services

Four backend services implement the core platform functionality. These are **not published** to npm and run as standalone Node.js processes:

```mermaid
graph LR
    subgraph "Service Layer"
        AS["api-service<br/>apps/api-service"]
        AB["action-builder<br/>services/action-builder"]
        PB["playbook-builder<br/>services/playbook-builder"]
        KB["knowledge-builder<br/>services/knowledge-builder"]
    end
    
    AS --> DB["@actionbookdev/db"]
    AB --> DB
    AB --> BR["@actionbookdev/browser"]
    AB --> BP["@actionbookdev/browser-profile"]
    AB --> MCP["@actionbookdev/mcp"]
    PB --> DB
    PB --> BR
    PB --> BP
    KB --> DB
    KB --> BP
```

**API Service** (`apps/api-service`):
- REST API server for search and retrieval
- Dependencies: `@actionbookdev/db` only
- Exposes endpoints at `/actions/search`, `/actions/:id`, `/sources`

**Action Builder** (`services/action-builder`):
- Recording service that discovers UI capabilities
- Dependencies: `@actionbookdev/browser`, `@actionbookdev/browser-profile`, `@actionbookdev/db`, `@actionbookdev/mcp`
- External: `@browserbasehq/stagehand`, `playwright`, AI SDK packages
- Referenced in [pnpm-lock.yaml:192-269]()

**Playbook Builder** (`services/playbook-builder`):
- Documentation generation service
- Dependencies: `@actionbookdev/browser`, `@actionbookdev/browser-profile`, `@actionbookdev/db`
- External: Stagehand (older v1.14.0), Playwright, AI providers
- Referenced in [pnpm-lock.yaml:414-476]()

**Knowledge Builder** (`services/knowledge-builder`):
- Web crawling and content extraction service
- Dependencies: `@actionbookdev/browser-profile`, `@actionbookdev/db`
- External: `playwright`, `@mozilla/readability`, `cheerio`, `turndown`, `openai`
- Referenced in [pnpm-lock.yaml:354-410]()

Sources: [pnpm-lock.yaml:192-269](), [pnpm-lock.yaml:414-476](), [pnpm-lock.yaml:354-410]()

### Common Packages

Three internal packages provide shared infrastructure. These are referenced using `workspace:*` and are **not published**:

**@actionbookdev/browser** (`services/common/browser`):
- Defines `BrowserAdapter` interface
- Implements `StagehandBrowser` and `AgentCoreBrowser`
- Dependencies: `@actionbookdev/browser-profile`, Stagehand, Playwright, AWS Bedrock SDK
- Peer dependencies on Stagehand (>=1.0.0) and Playwright (>=1.40.0)
- Referenced in [pnpm-lock.yaml:271-306]()

**@actionbookdev/browser-profile** (`services/common/browser-profile`):
- Manages persistent browser profiles for login state
- Implements `BrowserProfileManager` class
- No external dependencies beyond TypeScript and build tools
- Referenced in [pnpm-lock.yaml:308-318]()

**@actionbookdev/db** (`services/db`):
- Database access layer using Drizzle ORM
- Core dependencies: `drizzle-orm`, `pg`, `@neondatabase/serverless`, `dotenv`
- Provides `getDb()` singleton and schema definitions
- Development: `drizzle-kit` for migrations
- Referenced in [pnpm-lock.yaml:320-352]()

Sources: [pnpm-lock.yaml:271-306](), [pnpm-lock.yaml:308-318](), [pnpm-lock.yaml:320-352]()

### Playground and Evaluation

Two additional workspace categories support experimentation and testing:

**Playground** (`playground/*`):
- Contains experimental and example projects
- `playground/stagehand-agent`: Example Stagehand integration with Actionbook SDK
- `playground/lib-rs-scraper`: Rust library scraper example
- Not part of core build pipeline
- Referenced in [pnpm-lock.yaml:152-191]()

**Evaluation** (`eval`):
- End-to-end testing and evaluation scripts
- Dependencies: `@actionbookdev/action-builder`, `braintrust`, `playwright`, `yaml`, `zod`
- Used for quality assurance and regression testing
- Referenced in [pnpm-lock.yaml:18-44]()

Sources: [pnpm-lock.yaml:152-191](), [pnpm-lock.yaml:18-44]()

## Dependency Graph

The following diagram shows the complete dependency relationships between internal packages. Note that `@actionbookdev/sdk` is the only published package with **no internal dependencies**, making it suitable for standalone use:

```mermaid
graph TB
    subgraph "Published Packages"
        CLI["@actionbookdev/cli"]
        SDK["@actionbookdev/sdk"]
        MCP["@actionbookdev/mcp"]
        ToolsAI["@actionbookdev/tools-ai-sdk"]
    end
    
    subgraph "Services"
        APIService["api-service"]
        ActionBuilder["action-builder"]
        PlaybookBuilder["playbook-builder"]
        KnowledgeBuilder["knowledge-builder"]
    end
    
    subgraph "Common Packages"
        Browser["@actionbookdev/browser"]
        BrowserProfile["@actionbookdev/browser-profile"]
        DB["@actionbookdev/db"]
    end
    
    subgraph "External Dependencies"
        Playwright["playwright"]
        Stagehand["@browserbasehq/stagehand"]
        DrizzleORM["drizzle-orm"]
        NeonDB["@neondatabase/serverless"]
        AISDK["ai & @ai-sdk/*"]
        AgentBrowser["agent-browser"]
    end
    
    CLI --> SDK
    CLI --> AgentBrowser
    MCP --> SDK
    ToolsAI --> SDK
    
    ActionBuilder --> Browser
    ActionBuilder --> BrowserProfile
    ActionBuilder --> DB
    ActionBuilder --> MCP
    ActionBuilder --> AISDK
    
    PlaybookBuilder --> Browser
    PlaybookBuilder --> BrowserProfile
    PlaybookBuilder --> DB
    PlaybookBuilder --> AISDK
    
    KnowledgeBuilder --> BrowserProfile
    KnowledgeBuilder --> DB
    
    APIService --> DB
    
    Browser --> BrowserProfile
    Browser --> Playwright
    Browser --> Stagehand
    
    DB --> DrizzleORM
    DB --> NeonDB
```

**Key Dependency Patterns:**

1. **SDK Independence**: `@actionbookdev/sdk` has zero workspace dependencies, only external `zod` and `zod-to-json-schema`
2. **Browser Isolation**: All browser automation flows through `@actionbookdev/browser` package
3. **Database Centralization**: All services access PostgreSQL through `@actionbookdev/db`
4. **Profile Sharing**: `@actionbookdev/browser-profile` is used by all services that need browser state persistence

Sources: [packages/cli/package.json:26-30](), [packages/js-sdk/package.json:27-29](), [packages/mcp/package.json:31-36](), [pnpm-lock.yaml:192-476]()

## File System Layout

The repository follows a structured layout optimized for logical grouping and build tooling:

```
actionbook/
├── packages/               # Published npm packages
│   ├── cli/               # @actionbookdev/cli
│   ├── js-sdk/            # @actionbookdev/sdk
│   ├── mcp/               # @actionbookdev/mcp
│   └── tools-ai-sdk/      # @actionbookdev/tools-ai-sdk
│
├── services/              # Backend services
│   ├── action-builder/    # Recording service
│   ├── playbook-builder/  # Documentation service
│   ├── knowledge-builder/ # Crawling service
│   ├── common/            # Shared packages
│   │   ├── browser/       # @actionbookdev/browser
│   │   └── browser-profile/ # @actionbookdev/browser-profile
│   └── db/                # @actionbookdev/db
│
├── apps/                  # Application services (not in workspace config)
│   └── api-service/       # REST API server
│
├── playground/            # Experimental projects
│   ├── stagehand-agent/   # Example integration
│   └── lib-rs-scraper/    # Rust scraper example
│
├── eval/                  # Evaluation and testing
│
├── output/                # Generated YAML files (gitignored)
│
├── .browser-profile/      # Persistent browser state (gitignored)
│
├── pnpm-workspace.yaml    # Workspace configuration
├── package.json           # Root package with global scripts
├── turbo.json             # Turborepo configuration
├── pnpm-lock.yaml         # Dependency lockfile
└── LICENSE                # Apache-2.0 license
```

**Important Directories:**

- **`packages/`**: User-facing packages published to npm. Each has `"private": false` and version numbers.
- **`services/`**: Backend services and shared infrastructure. Not published to npm.
- **`services/common/`**: Shared packages used by multiple services but not published externally.
- **`output/`**: Generated during builds, contains YAML action manuals ([.gitignore:68]())
- **`.browser-profile/`**: Contains Chromium user data directories with cookies and session state ([.gitignore:74]())

**Build Artifacts:**

Each TypeScript package builds to a `dist/` directory ([.gitignore:6]()), which is gitignored but included in npm packages via the `files` field in package.json. Build artifacts are coordinated by Turborepo caching ([turbo.json:4-7]()).

Sources: [pnpm-workspace.yaml:1-7](), [.gitignore:1-75](), [turbo.json:1-23]()

## Package Manager Configuration

The repository uses **pnpm 10.24.0** as specified in [package.json:7]() via the `packageManager` field. This enforces consistent dependency resolution across all contributors.

**pnpm Features Used:**

1. **Workspace Protocol**: Packages reference each other using `workspace:*` (e.g., [packages/cli/package.json:27]())
2. **Dependency Overrides**: Forces `@neondatabase/serverless` to `^0.10.4` ([package.json:20-22](), [pnpm-lock.yaml:7-8]())
3. **Nested Workspaces**: `services/*/*` pattern allows for `services/common/*` packages ([pnpm-workspace.yaml:6]())
4. **Peer Dependency Auto-install**: Enabled via [pnpm-lock.yaml:4]()

**Version Resolution:**

The lockfile ([pnpm-lock.yaml:1]()) uses lockfileVersion 9.0, which provides improved resolution and security. All workspace packages are linked using `link:` protocol in the lockfile, ensuring changes are immediately visible across packages during development.

Sources: [package.json:7](), [package.json:19-23](), [pnpm-lock.yaml:1-8](), [pnpm-workspace.yaml:1-7]()

## Development Workflow

The monorepo structure supports several development workflows:

**Building Individual Packages:**
```bash
# Build only the SDK
pnpm --filter @actionbookdev/sdk build

# Build SDK and all packages that depend on it
pnpm --filter @actionbookdev/sdk... build
```

**Running Services:**
```bash
# Run action-builder service
cd services/action-builder
pnpm dev
```

**Adding Dependencies:**
```bash
# Add to specific package
pnpm --filter @actionbookdev/cli add commander

# Add to workspace root
pnpm add -w turbo
```

**Turborepo Integration:**

The [turbo.json:1-23]() configuration defines task dependencies:
- `build` tasks run in topological order based on `dependsOn: ["^build"]`
- `dev` tasks run concurrently with caching disabled
- `test` and `lint` depend on upstream builds completing first

This ensures that changes to `@actionbookdev/sdk` trigger rebuilds of `@actionbookdev/cli`, `@actionbookdev/mcp`, and all services that depend on shared packages.

Sources: [turbo.json:1-23](), [packages/mcp/package.json:24]()

---

# Page: Build System

# Build System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitignore](.gitignore)
- [mcp-servers.json](mcp-servers.json)
- [package.json](package.json)
- [pnpm-lock.yaml](pnpm-lock.yaml)
- [pnpm-workspace.yaml](pnpm-workspace.yaml)
- [services/action-builder/.nvmrc](services/action-builder/.nvmrc)
- [turbo.json](turbo.json)

</details>



## Purpose and Scope

This document describes the build orchestration system used in the Actionbook monorepo. It covers the Turborepo configuration, task definitions, dependency management, caching strategy, and execution model for building, testing, and developing across multiple packages and services.

For information about the monorepo structure itself (package organization and dependencies), see [Monorepo Structure](#8.1). For local development setup procedures, see [Local Development Setup](#8.3).

**Sources:** [package.json:1-24](), [turbo.json:1-22](), [pnpm-workspace.yaml:1-7]()

## Overview

The Actionbook monorepo uses **Turborepo** as its build orchestration tool, combined with **pnpm workspaces** for package management. Turborepo provides intelligent task scheduling, caching, and parallel execution across all packages in the workspace.

The build system manages compilation, development servers, testing, and linting for:
- 4 published npm packages (`@actionbookdev/cli`, `@actionbookdev/sdk`, `@actionbookdev/mcp`, `@actionbookdev/tools-ai-sdk`)
- 3 internal packages (`@actionbookdev/browser`, `@actionbookdev/browser-profile`, `@actionbookdev/db`)
- 4 backend services (`api-service`, `action-builder`, `playbook-builder`, `knowledge-builder`)
- 2 playground projects
- 1 evaluation project

**Sources:** [package.json:1-24](), [pnpm-workspace.yaml:1-7]()

## Turborepo Configuration

### Task Dependency Graph

```mermaid
graph TB
    subgraph "Root Tasks"
        RootBuild["pnpm build"]
        RootDev["pnpm dev"]
        RootTest["pnpm test"]
        RootLint["pnpm lint"]
        RootClean["pnpm clean"]
    end
    
    subgraph "Turborepo Tasks"
        Build["turbo build"]
        Dev["turbo dev"]
        Test["turbo test"]
        Lint["turbo lint"]
        Clean["turbo clean"]
    end
    
    subgraph "Package-Level Execution"
        PkgBuild["package:build"]
        PkgDev["package:dev"]
        PkgTest["package:test"]
        PkgLint["package:lint"]
        PkgClean["package:clean"]
    end
    
    subgraph "Build Outputs"
        DistDir["dist/**"]
        NextDir[".next/**"]
    end
    
    RootBuild --> Build
    RootDev --> Dev
    RootTest --> Test
    RootLint --> Lint
    RootClean --> Clean
    
    Build --> PkgBuild
    Dev --> PkgDev
    Test --> PkgTest
    Lint --> PkgLint
    Clean --> PkgClean
    
    PkgBuild -.->|"dependsOn: ^build"| PkgBuild
    PkgTest -.->|"dependsOn: ^build"| PkgBuild
    PkgLint -.->|"dependsOn: ^build"| PkgBuild
    
    PkgBuild -->|"outputs"| DistDir
    PkgBuild -->|"outputs"| NextDir
```

**Diagram: Task dependency and execution flow in Turborepo**

The `^build` syntax in Turborepo means "wait for all dependencies to finish their `build` task before starting". This ensures packages are built in topological order.

**Sources:** [turbo.json:1-22](), [package.json:8-14]()

### Task Definitions

The Turborepo configuration in `turbo.json` defines five core tasks:

| Task | Cache | Persistent | Dependencies | Outputs |
|------|-------|------------|--------------|---------|
| `build` | ✅ | ❌ | `^build` | `dist/**`, `.next/**` |
| `dev` | ❌ | ✅ | none | none |
| `test` | ✅ | ❌ | `^build` | none |
| `lint` | ✅ | ❌ | `^build` | none |
| `clean` | ❌ | ❌ | none | none |

**Key properties:**

- **`dependsOn: ["^build"]`**: The `^` prefix indicates a topological dependency. When running `test`, `lint`, or `build`, Turborepo first builds all upstream dependencies.
- **`cache: false`**: Disables caching for `dev` and `clean` tasks since they have side effects or are inherently non-cacheable.
- **`persistent: true`**: Marks `dev` as a long-running process that shouldn't block other tasks.
- **`outputs`**: Defines which directories contain build artifacts for caching.

**Sources:** [turbo.json:3-21]()

## Workspace Organization

### Workspace Package Mapping

```mermaid
graph TB
    subgraph "Workspace Globs"
        PackagesGlob["packages/*"]
        PlaygroundGlob["playground/*"]
        EvalGlob["eval"]
        ServicesGlob1["services/*"]
        ServicesGlob2["services/*/*"]
    end
    
    subgraph "Published Packages"
        CLI["packages/cli"]
        SDK["packages/js-sdk"]
        MCP["packages/mcp"]
        ToolsAI["packages/tools-ai-sdk"]
    end
    
    subgraph "Internal Common Packages"
        Browser["services/common/browser"]
        BrowserProfile["services/common/browser-profile"]
        DB["services/db"]
    end
    
    subgraph "Backend Services"
        ActionBuilder["services/action-builder"]
        PlaybookBuilder["services/playbook-builder"]
        KnowledgeBuilder["services/knowledge-builder"]
    end
    
    subgraph "Development & Testing"
        Eval["eval"]
        StagehandAgent["playground/stagehand-agent"]
        LibRsScraper["playground/lib-rs-scraper"]
    end
    
    PackagesGlob --> CLI
    PackagesGlob --> SDK
    PackagesGlob --> MCP
    PackagesGlob --> ToolsAI
    
    ServicesGlob2 --> Browser
    ServicesGlob2 --> BrowserProfile
    ServicesGlob1 --> DB
    ServicesGlob1 --> ActionBuilder
    ServicesGlob1 --> PlaybookBuilder
    ServicesGlob1 --> KnowledgeBuilder
    
    PlaygroundGlob --> StagehandAgent
    PlaygroundGlob --> LibRsScraper
    EvalGlob --> Eval
```

**Diagram: pnpm workspace structure and package resolution**

The workspace configuration uses glob patterns to include packages at multiple directory levels. The `services/*/*` pattern specifically captures nested packages like `services/common/browser`.

**Sources:** [pnpm-workspace.yaml:1-7]()

## Build Task Execution

### Topological Build Order

```mermaid
graph LR
    subgraph "Layer 1: No Dependencies"
        SDK["@actionbookdev/sdk"]
        BrowserProfile["@actionbookdev/browser-profile"]
    end
    
    subgraph "Layer 2: Depends on Layer 1"
        Browser["@actionbookdev/browser"]
        DB["@actionbookdev/db"]
        CLI["@actionbookdev/cli"]
        MCP["@actionbookdev/mcp"]
        ToolsAI["@actionbookdev/tools-ai-sdk"]
    end
    
    subgraph "Layer 3: Depends on Layer 2"
        ActionBuilder["action-builder"]
        PlaybookBuilder["playbook-builder"]
        KnowledgeBuilder["knowledge-builder"]
    end
    
    subgraph "Layer 4: Applications"
        Eval["eval"]
        StagehandAgent["stagehand-agent"]
    end
    
    SDK --> CLI
    SDK --> MCP
    SDK --> ToolsAI
    BrowserProfile --> Browser
    
    Browser --> ActionBuilder
    Browser --> PlaybookBuilder
    BrowserProfile --> ActionBuilder
    BrowserProfile --> PlaybookBuilder
    BrowserProfile --> KnowledgeBuilder
    DB --> ActionBuilder
    DB --> PlaybookBuilder
    DB --> KnowledgeBuilder
    
    ActionBuilder --> Eval
    SDK --> StagehandAgent
```

**Diagram: Package dependency graph determining build order**

When running `pnpm build`, Turborepo analyzes this dependency graph and builds packages in topological order. Packages in the same layer can be built in parallel. The `^build` dependency in [turbo.json:5]() enforces this ordering.

**Sources:** [pnpm-lock.yaml:10-477]()

### Task Execution Lifecycle

```mermaid
graph TB
    Start["turbo build invoked"]
    
    subgraph "Analysis Phase"
        ParseConfig["Parse turbo.json"]
        BuildGraph["Build task graph"]
        CheckCache["Check cache for each task"]
    end
    
    subgraph "Execution Phase"
        ScheduleLayer1["Schedule Layer 1 tasks\n(parallel)"]
        RunLayer1["Execute Layer 1 builds"]
        ScheduleLayer2["Schedule Layer 2 tasks\n(parallel)"]
        RunLayer2["Execute Layer 2 builds"]
        ScheduleLayerN["Schedule Layer N tasks"]
        RunLayerN["Execute Layer N builds"]
    end
    
    subgraph "Output Phase"
        WriteCache["Write outputs to cache"]
        GenerateSummary["Generate task summary"]
    end
    
    Start --> ParseConfig
    ParseConfig --> BuildGraph
    BuildGraph --> CheckCache
    
    CheckCache -->|"No cache hit"| ScheduleLayer1
    CheckCache -->|"Cache hit"| WriteCache
    
    ScheduleLayer1 --> RunLayer1
    RunLayer1 --> ScheduleLayer2
    ScheduleLayer2 --> RunLayer2
    RunLayer2 --> ScheduleLayerN
    ScheduleLayerN --> RunLayerN
    
    RunLayer1 --> WriteCache
    RunLayer2 --> WriteCache
    RunLayerN --> WriteCache
    
    WriteCache --> GenerateSummary
```

**Diagram: Turborepo task execution lifecycle**

**Sources:** [turbo.json:1-22]()

## Caching Strategy

### Cache Behavior by Task

Turborepo caches task outputs based on:
1. **Task inputs**: Source files, dependencies, environment variables
2. **Task definition**: The task name and configuration
3. **Dependency outputs**: Results from upstream `^build` tasks

The caching behavior is configured per task:

**Cached Tasks (default):**
- `build`: Caches `dist/**` and `.next/**` directories
- `test`: Caches test results and coverage reports
- `lint`: Caches linting results

**Non-cached Tasks:**
- `dev`: Runs development servers with live reload ([turbo.json:9]())
- `clean`: Removes build artifacts ([turbo.json:18]())

### Cache Location

Turborepo stores its cache in the `.turbo` directory at the repository root. This directory is excluded from version control via [.gitignore:61]().

**Sources:** [turbo.json:4-21](), [.gitignore:60-61]()

## Package Manager Integration

### pnpm Configuration

The monorepo uses **pnpm 10.24.0** as specified in [package.json:7]():

```
"packageManager": "pnpm@10.24.0"
```

This ensures consistent behavior across development environments. The pnpm version is enforced when running any pnpm command.

### Dependency Overrides

Global dependency overrides are configured in [package.json:19-23]():

```json
"pnpm": {
  "overrides": {
    "@neondatabase/serverless": "^0.10.4"
  }
}
```

This ensures all packages in the workspace use the specified version of `@neondatabase/serverless`, regardless of what version individual packages request.

**Sources:** [package.json:7](), [package.json:19-23]()

## Running Tasks

### Root-Level Commands

All build system commands are executed from the repository root:

| Command | Purpose | Turbo Task |
|---------|---------|------------|
| `pnpm build` | Build all packages | `turbo build` |
| `pnpm dev` | Start development servers | `turbo dev` |
| `pnpm test` | Run all tests | `turbo test` |
| `pnpm lint` | Lint all packages | `turbo lint` |
| `pnpm clean` | Clean build artifacts | `turbo clean` |

These commands are defined as npm scripts in [package.json:8-14]() and delegate to Turborepo.

### Scoped Execution

To run tasks for specific packages:

```bash
# Build only the CLI package
pnpm --filter @actionbookdev/cli build

# Run tests for action-builder service
pnpm --filter action-builder test

# Start dev server for a single package
pnpm --filter @actionbookdev/sdk dev
```

The `--filter` flag uses pnpm's workspace filtering to select packages by name or pattern.

### Parallel Execution

Turborepo automatically parallelizes tasks that don't depend on each other. For example, when running `pnpm build`:

1. **Layer 1** (parallel): `@actionbookdev/sdk`, `@actionbookdev/browser-profile` build simultaneously
2. **Layer 2** (parallel): Once Layer 1 completes, `@actionbookdev/browser`, `@actionbookdev/db`, `@actionbookdev/cli`, `@actionbookdev/mcp` build in parallel
3. **Layer 3** (parallel): Services build after their dependencies are ready

This significantly reduces total build time compared to sequential execution.

**Sources:** [package.json:8-14](), [turbo.json:1-22]()

## Build Outputs

### Output Directory Structure

Build artifacts are generated in package-specific directories:

```
packages/cli/dist/              # CLI compiled output
packages/js-sdk/dist/           # SDK compiled output
packages/mcp/dist/              # MCP server compiled output
services/action-builder/dist/   # Action builder compiled output
services/db/dist/               # Database package compiled output
```

These directories are:
- Excluded from version control ([.gitignore:6-9]())
- Specified as Turborepo outputs ([turbo.json:6]())
- Included in npm packages for publication

### TypeScript Build Info

TypeScript generates `.tsbuildinfo` files for incremental compilation. These are excluded from version control ([.gitignore:35]()) but used by both TypeScript and Turborepo to optimize rebuilds.

**Sources:** [turbo.json:6](), [.gitignore:6-9](), [.gitignore:35]()

## Package-Specific Build Tools

### Build Tool by Package Type

Different packages use different build tools based on their requirements:

| Package Type | Build Tool | Config File |
|--------------|-----------|-------------|
| Published packages (CLI, SDK, MCP) | `tsc` (TypeScript) | `tsconfig.json` |
| Internal packages (browser, db) | `tsup` | `tsup.config.ts` |
| Services (action-builder, playbook-builder) | `tsup` | `tsup.config.ts` |

**tsup** is used for internal packages and services because it provides:
- Fast esbuild-based compilation
- Automatic CJS/ESM dual output
- Minimal configuration

The published packages use raw `tsc` to maintain full control over type definitions and build output structure.

**Sources:** [pnpm-lock.yaml:298-306](), [pnpm-lock.yaml:344-346]()

## Development Mode

### Persistent Development Tasks

The `dev` task is configured with `persistent: true` in [turbo.json:10](). This means:

1. Development servers run continuously
2. They don't block other tasks from starting
3. Multiple `dev` tasks can run simultaneously
4. Hot reload and file watching work as expected

When running `pnpm dev`, Turborepo starts all development servers in parallel without waiting for them to complete, allowing developers to work on multiple packages simultaneously.

### No Caching for Development

Development tasks have `cache: false` ([turbo.json:9]()) because:
- Dev servers have side effects (ports, file watching)
- Live reload requires reading from the actual file system
- Caching would prevent detecting file changes

**Sources:** [turbo.json:8-11]()

## Git Hooks Integration

The build system integrates with Git hooks via [package.json:14]():

```json
"prepare": "git config core.hooksPath .githooks"
```

This script runs after `pnpm install` and configures Git to use hooks from the `.githooks` directory. These hooks can run build system tasks (like linting) on commit or push.

**Sources:** [package.json:14]()

---

# Page: Local Development Setup

# Local Development Setup

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [services/db/src/connection.ts](services/db/src/connection.ts)

</details>



This guide provides step-by-step instructions for setting up a local Actionbook development environment. It covers prerequisites, initial setup, environment configuration, database initialization, and running services locally.

For information about the monorepo structure and package organization, see [Monorepo Structure](#8.1). For details on the build system and task orchestration, see [Build System](#8.2). For testing guidance, see [Testing](#8.4).

## Purpose and Scope

This page covers the complete local development setup process, from installing prerequisites to running the development server. It is targeted at contributors who want to modify Actionbook's codebase, run services locally, or develop new features. End users who only need to use the CLI, MCP Server, or SDK should refer to the installation instructions in the main README.

---

## Prerequisites

Before setting up the local environment, ensure the following tools are installed:

| Tool | Minimum Version | Recommended | Installation |
|------|----------------|-------------|--------------|
| **Node.js** | 18.0.0 | 20+ | [nodejs.org](https://nodejs.org) |
| **pnpm** | 10.0.0 | Latest | `npm install -g pnpm` |
| **PostgreSQL** | 14+ | 16+ | [postgresql.org](https://postgresql.org) or hosted (Neon/Supabase) |
| **Git** | Any | Latest | [git-scm.com](https://git-scm.com) |

**Optional but Recommended:**
- **Docker**: For running PostgreSQL locally via containers
- **VSCode**: Recommended IDE with TypeScript support

**Verify Prerequisites:**

```bash
node --version    # Should be >= v18.0.0
pnpm --version    # Should be >= 10.0.0
psql --version    # Should be >= 14
```

**Sources:** [README.md:706-709]()

---

## Setup Flow Overview

```mermaid
graph TB
    Start["Start: Clone Repository"]
    Install["pnpm install<br/>(Install dependencies)"]
    EnvConfig["Configure .env Files<br/>(services/db, apps/api-service, etc.)"]
    DbSetup["Database Setup<br/>(Create PostgreSQL database)"]
    Migrate["pnpm migrate<br/>(Run Drizzle migrations)"]
    BrowserSetup["actionbook browser install<br/>(Install Chromium)"]
    DevServer["pnpm dev<br/>(Start development server)"]
    Verify["Verify Services Running"]
    
    Start --> Install
    Install --> EnvConfig
    EnvConfig --> DbSetup
    DbSetup --> Migrate
    Migrate --> BrowserSetup
    BrowserSetup --> DevServer
    DevServer --> Verify
    
    style Start fill:#e1f5ff
    style Verify fill:#e1ffe1
```

**Sources:** [README.md:711-735]()

---

## Step 1: Clone Repository and Install Dependencies

**Clone the Repository:**

```bash
git clone https://github.com/actionbook/actionbook.git
cd actionbook
```

**Install Dependencies:**

The monorepo uses pnpm workspaces. Run the following command from the repository root to install all dependencies across all packages:

```bash
pnpm install
```

This installs dependencies for:
- Published packages: `@actionbookdev/cli`, `@actionbookdev/sdk`, `@actionbookdev/mcp`
- Services: `api-service`, `action-builder`, `playbook-builder`, `knowledge-builder`
- Internal packages: `@actionbookdev/browser`, `@actionbookdev/db`, `@actionbookdev/browser-profile`

**Sources:** [README.md:713-717]()

---

## Step 2: Database Setup

### Local PostgreSQL Setup

**Option 1: Docker (Recommended)**

```bash
docker run --name actionbook-postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=actionbook \
  -p 5432:5432 \
  -d postgres:16
```

**Option 2: Native Installation**

Create a database manually:

```bash
psql -U postgres
CREATE DATABASE actionbook;
\q
```

**Option 3: Hosted Database**

Use a hosted PostgreSQL provider:
- [Neon](https://neon.tech) (recommended for serverless)
- [Supabase](https://supabase.com)
- [Railway](https://railway.app)

For hosted databases, obtain the connection string (e.g., `postgresql://user:pass@host:5432/dbname`).

**Sources:** [README.md:709](), [services/db/src/connection.ts:49-64]()

---

## Step 3: Environment Configuration

### Database Connection Strategy

The connection strategy differs based on environment:

```mermaid
graph LR
    subgraph "Environment Detection"
        LocalDev["Local Development<br/>(NODE_ENV !== production)"]
        AgentCore["AgentCore Runtime<br/>(AWS_AGENTCORE_RUNTIME=true)"]
        NonVercel["Non-Vercel Production<br/>(!VERCEL)"]
        Vercel["Vercel Production<br/>(VERCEL=true)"]
    end
    
    subgraph "Driver Selection"
        PgDriver["node-postgres Driver<br/>(Pool with TCP)"]
        NeonDriver["Neon Serverless Driver<br/>(Pool with WebSocket)"]
    end
    
    LocalDev --> PgDriver
    AgentCore --> PgDriver
    NonVercel --> PgDriver
    Vercel --> NeonDriver
```

**Sources:** [services/db/src/connection.ts:25-40]()

### Required Environment Files

Copy `.env.example` to `.env` in the following directories:

| Package | Purpose | Required Variables |
|---------|---------|-------------------|
| `services/db` | Database connection | `DATABASE_URL` or `POSTGRES_URL` |
| `apps/api-service` | API server configuration | `DATABASE_URL`, `PORT` |
| `services/action-builder` | Action recording | `DATABASE_URL`, LLM provider keys |
| `services/knowledge-builder` | Knowledge extraction | `DATABASE_URL`, LLM provider keys |

### Environment Variable Reference

**services/db/.env:**

```bash
# Database URL (choose one format)
DATABASE_URL="postgresql://postgres:postgres@localhost:5432/actionbook"
# or
POSTGRES_URL="postgresql://postgres:postgres@localhost:5432/actionbook"

# For local development, SSL is auto-detected
# For production, sslmode=require is recommended
```

**apps/api-service/.env:**

```bash
# Database connection
DATABASE_URL="postgresql://postgres:postgres@localhost:5432/actionbook"

# Server configuration
PORT=3000
NODE_ENV=development

# CORS (optional)
ALLOWED_ORIGINS="http://localhost:3000,http://localhost:5173"
```

**services/action-builder/.env (optional):**

```bash
# Database connection
DATABASE_URL="postgresql://postgres:postgres@localhost:5432/actionbook"

# LLM Provider Configuration (choose one or more)
# OpenRouter (recommended)
OPENROUTER_API_KEY="sk-or-v1-..."

# OpenAI
OPENAI_API_KEY="sk-..."

# Anthropic
ANTHROPIC_API_KEY="sk-ant-..."

# AWS Bedrock
AWS_REGION="us-east-1"
AWS_ACCESS_KEY_ID="..."
AWS_SECRET_ACCESS_KEY="..."

# Browser configuration
BROWSER_TYPE="stagehand"  # or "agentcore"
```

**services/knowledge-builder/.env (optional):**

```bash
# Database connection
DATABASE_URL="postgresql://postgres:postgres@localhost:5432/actionbook"

# Embedding provider
OPENAI_API_KEY="sk-..."
```

### Connection Pool Configuration

The database connection logic in `createDb()` automatically adjusts pool settings based on environment:

| Environment | Max Connections | Min Connections | Idle Timeout | Allow Exit on Idle |
|-------------|----------------|-----------------|--------------|-------------------|
| **Local/Traditional** | 20 | 2 | 30s | false |
| **Serverless (Vercel/Lambda)** | 5 | 0 | 30s | true |

**Sources:** [services/db/src/connection.ts:70-98](), [README.md:719-723]()

---

## Step 4: Database Migrations

After configuring environment variables, run database migrations to create the schema:

```bash
cd services/db
pnpm migrate
```

This executes Drizzle ORM migrations that create the following tables:

```mermaid
erDiagram
    sources ||--o{ source_versions : "has"
    sources ||--o{ documents : "contains"
    sources ||--o{ pages : "contains"
    sources ||--o{ build_tasks : "has"
    source_versions ||--o{ chunks : "has"
    documents ||--o{ chunks : "split into"
    pages ||--o{ elements : "contains"
    build_tasks ||--o{ recording_tasks : "generates"
    
    sources {
        uuid id PK
        string name
        string url
        timestamp created_at
    }
    
    source_versions {
        uuid id PK
        uuid source_id FK
        string version
        enum status
        timestamp published_at
    }
    
    documents {
        uuid id PK
        uuid source_id FK
        string url
        text content
    }
    
    chunks {
        uuid id PK
        uuid document_id FK
        uuid source_version_id FK
        text content
        vector embedding
    }
    
    pages {
        uuid id PK
        uuid source_id FK
        string url
        string page_type
    }
    
    elements {
        uuid id PK
        uuid page_id FK
        string element_type
        jsonb selectors
        jsonb metadata
    }
    
    build_tasks {
        uuid id PK
        uuid source_id FK
        enum stage
        enum stage_status
    }
    
    recording_tasks {
        uuid id PK
        uuid build_task_id FK
        enum status
        text instructions
    }
```

For detailed schema information, see [Database Schema](#5.1).

**Verify Migration Success:**

```bash
psql $DATABASE_URL -c "\dt"
```

You should see tables: `sources`, `source_versions`, `documents`, `chunks`, `pages`, `elements`, `build_tasks`, `recording_tasks`, and others.

**Sources:** [README.md:726-729](), [services/db/src/connection.ts:1-5]()

---

## Step 5: Browser Setup

Actionbook uses Playwright for browser automation. Install Chromium:

```bash
# Build the CLI first
pnpm build

# Install Chromium
npx actionbook browser install
```

This downloads and installs Chromium to `~/.cache/ms-playwright/chromium-*` (or equivalent platform-specific location).

For more information on browser automation, see [Browser Automation Layer](#4) and [StagehandBrowser Implementation](#4.2).

**Sources:** [README.md:62-64](), [README.md:113-115]()

---

## Step 6: Running Services

### Development Server

Start all services in development mode:

```bash
# From repository root
pnpm dev
```

This uses Turborepo to run `dev` scripts for all packages in parallel, with the following services starting:

```mermaid
graph TB
    subgraph "Development Services"
        API["apps/api-service<br/>http://localhost:3000<br/>REST API server"]
        ActionBuilder["services/action-builder<br/>Recording service"]
        PlaybookBuilder["services/playbook-builder<br/>Documentation service"]
        KnowledgeBuilder["services/knowledge-builder<br/>Crawling service"]
    end
    
    subgraph "Supporting Processes"
        TypeWatch["TypeScript Watch Mode<br/>(tsc --watch)"]
        TurboCache["Turborepo Cache<br/>(Incremental builds)"]
    end
    
    subgraph "Database"
        DB[("PostgreSQL<br/>localhost:5432")]
    end
    
    API --> DB
    ActionBuilder --> DB
    PlaybookBuilder --> DB
    KnowledgeBuilder --> DB
    
    TypeWatch -.-> API
    TypeWatch -.-> ActionBuilder
    TypeWatch -.-> PlaybookBuilder
    TypeWatch -.-> KnowledgeBuilder
    
    TurboCache -.-> TypeWatch
```

### Individual Service Commands

Run services individually for targeted development:

```bash
# API Service only
cd apps/api-service
pnpm dev

# Action Builder only
cd services/action-builder
pnpm dev

# Playbook Builder only
cd services/playbook-builder
pnpm dev

# Knowledge Builder only
cd services/knowledge-builder
pnpm dev
```

### Building Packages

Build all packages:

```bash
pnpm build
```

Build specific package:

```bash
# CLI
cd packages/cli
pnpm build

# SDK
cd packages/sdk
pnpm build
```

For more information on the build system, see [Build System](#8.2).

**Sources:** [README.md:731-735]()

---

## Step 7: Verification

### Verify API Service

```bash
# Health check
curl http://localhost:3000/health

# Search actions
curl "http://localhost:3000/actions/search?q=airbnb"

# Get sources
curl http://localhost:3000/sources
```

Expected response from `/health`:
```json
{
  "status": "ok",
  "timestamp": "2025-01-15T12:00:00.000Z"
}
```

### Verify CLI

```bash
# Test CLI installation
actionbook --version

# Test search (requires populated database)
actionbook search "google login"

# Test browser commands
actionbook browser open https://example.com
```

### Verify Database Connection

Test the database connection using `getDb()`:

```typescript
import { getDb } from '@actionbookdev/db';

const db = getDb();
const sources = await db.query.sources.findMany();
console.log(`Found ${sources.length} sources`);
```

The `getDb()` function in [services/db/src/connection.ts:142-147]() returns a singleton Database instance that automatically selects the appropriate driver based on environment.

### Verify Services Status

```mermaid
graph LR
    Check1["API Service<br/>curl localhost:3000/health"]
    Check2["Database<br/>psql $DATABASE_URL -c 'SELECT 1'"]
    Check3["CLI<br/>actionbook --version"]
    Check4["Browser<br/>actionbook browser open example.com"]
    
    Check1 --> Success["✓ All Services Running"]
    Check2 --> Success
    Check3 --> Success
    Check4 --> Success
```

**Sources:** [services/db/src/connection.ts:142-147](), [README.md:119-130]()

---

## Common Development Tasks

### Resetting the Database

```bash
cd services/db
pnpm db:drop    # Drop all tables
pnpm migrate    # Recreate schema
```

### Clearing Browser Profiles

Browser profiles (for persistent login state) are stored in `~/.actionbook/profiles`. Clear them with:

```bash
rm -rf ~/.actionbook/profiles
```

For more information, see [Browser Profiles](#4.4).

### Running in Watch Mode

Watch mode automatically rebuilds on file changes:

```bash
# Watch all packages
pnpm dev

# Watch specific package
cd packages/cli
pnpm dev
```

### Inspecting the Database

```bash
# Connect to PostgreSQL
psql $DATABASE_URL

# List tables
\dt

# Query sources
SELECT id, name, url FROM sources;

# Query elements with selectors
SELECT e.id, e.element_type, e.selectors 
FROM elements e 
LIMIT 10;
```

**Sources:** [services/db/src/connection.ts:70-98]()

---

## Troubleshooting

### Database Connection Errors

**Error:** `Database URL not found`

**Solution:** Ensure `DATABASE_URL` or `POSTGRES_URL` is set in `services/db/.env`:

```bash
cd services/db
cat .env | grep DATABASE_URL
```

Reference: [services/db/src/connection.ts:54-57]()

---

**Error:** `Connection timeout`

**Solution:** Check PostgreSQL is running and accessible:

```bash
# Test connection
psql $DATABASE_URL -c "SELECT 1"

# For Docker
docker ps | grep postgres
```

---

**Error:** `SSL connection required`

**Solution:** For hosted databases (Neon, Supabase), append `?sslmode=require`:

```bash
DATABASE_URL="postgresql://user:pass@host:5432/db?sslmode=require"
```

The connection logic in [services/db/src/connection.ts:71-74]() automatically detects SSL requirements based on URL and hostname.

---

### Port Already in Use

**Error:** `Port 3000 already in use`

**Solution:** Change the port in `apps/api-service/.env`:

```bash
PORT=3001
```

Or kill the process using the port:

```bash
# Find process
lsof -i :3000

# Kill process
kill -9 <PID>
```

---

### Browser Installation Issues

**Error:** `Failed to install browser`

**Solution:** Install Playwright browsers manually:

```bash
npx playwright install chromium
```

Or specify a custom browser path in action-builder configuration.

---

### TypeScript Build Errors

**Error:** `Cannot find module '@actionbookdev/...'`

**Solution:** Build dependencies first:

```bash
pnpm build
```

The monorepo uses TypeScript project references. Packages must be built before dependent packages can compile.

---

### Migration Failures

**Error:** `Migration failed: relation already exists`

**Solution:** Reset the database:

```bash
cd services/db
pnpm db:drop
pnpm migrate
```

**Warning:** This deletes all data. Only use in development.

**Sources:** [services/db/src/connection.ts:79-88]()

---

## Next Steps

After completing local setup:

1. **Explore the codebase structure**: See [Monorepo Structure](#8.1)
2. **Understand the build system**: See [Build System](#8.2)  
3. **Run tests**: See [Testing](#8.4)
4. **Review core services**: See [Core Services](#3)
5. **Study the database schema**: See [Database Schema](#5.1)

For questions or issues, join the [Discord community](https://discord.gg/7sKKp7XQ2d) or open an issue on [GitHub](https://github.com/actionbook/actionbook/issues).

**Sources:** [README.md:696-700](), [README.md:703-735]()

---

# Page: Testing

# Testing

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitignore](.gitignore)
- [mcp-servers.json](mcp-servers.json)
- [package.json](package.json)
- [pnpm-lock.yaml](pnpm-lock.yaml)
- [pnpm-workspace.yaml](pnpm-workspace.yaml)
- [services/action-builder/.nvmrc](services/action-builder/.nvmrc)
- [services/action-builder/src/task-worker/build-task-runner.ts](services/action-builder/src/task-worker/build-task-runner.ts)
- [services/action-builder/src/task-worker/coordinator.ts](services/action-builder/src/task-worker/coordinator.ts)
- [services/action-builder/src/task-worker/recording-task-queue-worker.ts](services/action-builder/src/task-worker/recording-task-queue-worker.ts)
- [services/action-builder/test/coordinator.integration.it.test.ts](services/action-builder/test/coordinator.integration.it.test.ts)
- [services/action-builder/test/task-worker/integration/end-to-end.it.test.ts](services/action-builder/test/task-worker/integration/end-to-end.it.test.ts)
- [turbo.json](turbo.json)

</details>



This document describes the testing approach, tools, and patterns used in the Actionbook codebase. It covers test organization, running tests, writing new tests, and mocking strategies.

For information about setting up a local development environment before running tests, see [Local Development Setup](#8.3). For information about the build system that orchestrates test execution across the monorepo, see [Build System](#8.2).

---

## Testing Framework and Tools

Actionbook uses **Vitest** as its primary testing framework across all packages and services. Vitest is chosen for its speed, TypeScript support, and compatibility with the monorepo structure.

### Core Testing Stack

| Tool | Purpose | Location |
|------|---------|----------|
| Vitest | Test runner and assertion library | All packages and services |
| vi.mock() | Mocking framework (built into Vitest) | Test files |
| Playwright | Browser automation for E2E tests | Integration tests |
| PostgreSQL | Real database for integration tests | Test environment |

### Package-Level Test Configuration

Each package that includes tests has Vitest configured as a dev dependency:

- `packages/cli` - [pnpm-lock.yaml:70-72]()
- `packages/js-sdk` - [pnpm-lock.yaml:92-94]()
- `packages/mcp` - [pnpm-lock.yaml:123-125]()
- `services/action-builder` - [pnpm-lock.yaml:267-269]()
- `services/common/browser` - [pnpm-lock.yaml:304-306]()
- `services/playbook-builder` - [pnpm-lock.yaml:474-476]()

**Sources:** [pnpm-lock.yaml:1-477]()

---

## Test Types and Organization

### Test Naming Conventions

Tests follow a consistent naming pattern:

```
*.test.ts          - Unit tests
*.it.test.ts       - Integration tests
*.e2e.test.ts      - End-to-end tests (if applicable)
```

### Unit Tests

Unit tests focus on individual functions, classes, or modules in isolation. They use mocks for external dependencies and execute quickly.

**Characteristics:**
- Fast execution (< 100ms per test)
- No external dependencies (database, network, filesystem)
- Focus on single component behavior
- Heavy use of mocking

### Integration Tests

Integration tests verify that multiple components work together correctly. They may use real database connections and simulated external services.

**Example:** Coordinator integration tests verify the full task orchestration pipeline:

```mermaid
graph LR
    subgraph "Integration Test Scope"
        Coordinator["Coordinator"]
        BuildTaskRunner["BuildTaskRunner"]
        QueueWorker["RecordingTaskQueueWorker"]
        TaskExecutor["TaskExecutor (Mocked)"]
        DB[("PostgreSQL Database")]
    end
    
    Coordinator --> BuildTaskRunner
    Coordinator --> QueueWorker
    BuildTaskRunner --> DB
    QueueWorker --> TaskExecutor
    TaskExecutor --> DB
```

**Test IT-01: Multi-build concurrent execution** - [services/action-builder/test/coordinator.integration.it.test.ts:100-196]()

**Test IT-02: Task failure and retry** - [services/action-builder/test/coordinator.integration.it.test.ts:198-296]()

**Test IT-03: Stateless recovery** - [services/action-builder/test/coordinator.integration.it.test.ts:298-404]()

**Test IT-04: Multi-consumer concurrency safety** - [services/action-builder/test/coordinator.integration.it.test.ts:406-508]()

**Characteristics:**
- Slower execution (seconds to minutes)
- May use real database with test data
- Tests component interactions
- Longer timeouts (30-60 seconds)

**Sources:** [services/action-builder/test/coordinator.integration.it.test.ts:1-509]()

### End-to-End Tests

End-to-end tests verify complete user workflows through the entire system stack.

**Example:** TaskGenerator → TaskExecutor pipeline test:

```mermaid
graph LR
    subgraph "E2E Test: IT-301"
        Gen["TaskGenerator"]
        Tasks[("recording_tasks<br/>pending → running")]
        Exec["TaskExecutor"]
        Results[("recording_tasks<br/>completed")]
    end
    
    Gen -->|"generate()"| Tasks
    Tasks -->|"execute()"| Exec
    Exec -->|"update status"| Results
```

**Test IT-301: Complete pipeline** - [services/action-builder/test/task-worker/integration/end-to-end.it.test.ts:95-149]()

**Characteristics:**
- Slowest execution (minutes)
- Tests complete workflows
- Uses real or near-real dependencies
- Extended timeouts (60+ seconds)

**Sources:** [services/action-builder/test/task-worker/integration/end-to-end.it.test.ts:1-223]()

---

## Running Tests

### Running All Tests

From the monorepo root:

```bash
pnpm test
```

This executes the `test` task defined in `turbo.json`, which runs tests across all packages and services with proper dependency ordering.

### Running Tests for Specific Package

```bash
# From monorepo root
pnpm --filter @actionbookdev/cli test

# Or navigate to package directory
cd packages/cli
pnpm test
```

### Running Specific Test Files

```bash
# Run specific test file
pnpm vitest run path/to/test.test.ts

# Run tests matching pattern
pnpm vitest run --grep "coordinator"

# Run in watch mode
pnpm vitest watch
```

### Running Integration Tests Only

```bash
pnpm vitest run --grep "\.it\.test\.ts$"
```

**Sources:** [turbo.json:1-23](), [package.json:1-25]()

---

## Test Structure and Patterns

### Typical Test File Structure

```typescript
import { describe, test, expect, beforeAll, afterAll, beforeEach, vi } from 'vitest';
import { getDb } from '@actionbookdev/db';
import type { Database } from '@actionbookdev/db';

describe('Feature Name', () => {
  let db: Database;
  let testResourceIds: number[] = [];

  beforeAll(async () => {
    // One-time setup
    db = getDb();
  });

  afterAll(async () => {
    // One-time cleanup
    await cleanupTestData(db, testResourceIds);
  });

  beforeEach(async () => {
    // Reset before each test
    testResourceIds = [];
  });

  test('should verify behavior', async () => {
    // Arrange
    const testData = await createTestData();
    
    // Act
    const result = await performAction(testData);
    
    // Assert
    expect(result).toBeDefined();
  });
});
```

**Sources:** [services/action-builder/test/coordinator.integration.it.test.ts:69-99]()

### Lifecycle Hooks

| Hook | Purpose | Usage |
|------|---------|-------|
| `beforeAll()` | One-time setup before all tests | Database connection, test data creation |
| `afterAll()` | One-time cleanup after all tests | Remove test data, close connections |
| `beforeEach()` | Setup before each test | Reset state, clear arrays |
| `afterEach()` | Cleanup after each test | Remove test-specific resources |

### Test Timeout Configuration

Integration and E2E tests require longer timeouts:

```typescript
test('IT-01: Long-running integration test', async () => {
  // Test implementation
}, 60000); // 60 second timeout
```

Default Vitest timeout is 5 seconds. Integration tests typically use 30-60 seconds.

**Sources:** [services/action-builder/test/coordinator.integration.it.test.ts:100](), [services/action-builder/test/task-worker/integration/end-to-end.it.test.ts:149]()

---

## Mocking Strategies

### Mocking External Dependencies

Tests mock expensive or external dependencies like browsers, LLMs, and cloud services.

#### Example: Mocking TaskExecutor

```typescript
vi.mock('../src/task-worker/task-executor', async () => {
  const { recordingTasks } = await import('@actionbookdev/db');
  const { eq } = await import('drizzle-orm');

  return {
    TaskExecutor: class MockTaskExecutor {
      constructor(private db: any, private config: any) {}

      async execute(task: any) {
        // Simulate fast execution
        await new Promise((resolve) => setTimeout(resolve, 50));

        // Update database as real executor would
        await this.db
          .update(recordingTasks)
          .set({
            status: 'completed',
            progress: 100,
            completedAt: new Date(),
            attemptCount: task.attemptCount + 1,
            durationMs: 100,
            tokensUsed: 0,
            updatedAt: new Date(),
          })
          .where(eq(recordingTasks.id, task.id));

        return {
          success: true,
          actions_created: 5,
          duration_ms: 100,
        };
      }
    },
  };
});
```

**Sources:** [services/action-builder/test/coordinator.integration.it.test.ts:22-56]()

#### Example: Mocking ActionBuilder

```typescript
vi.mock('../../../src/ActionBuilder', () => ({
  ActionBuilder: vi.fn().mockImplementation(() => ({
    initialize: vi.fn().mockResolvedValue(undefined),
    build: vi.fn().mockResolvedValue({
      success: true,
      turns: 5,
      totalDuration: 10000,
      tokens: { input: 1000, output: 500, total: 1500 },
      savedPath: './output/test.yaml',
      siteCapability: {
        domain: 'example.com',
        pages: {
          home: {
            elements: {
              test_element: {},
            },
          },
        },
        global_elements: {},
      },
    }),
    close: vi.fn().mockResolvedValue(undefined),
  })),
}));
```

**Sources:** [services/action-builder/test/task-worker/integration/end-to-end.it.test.ts:32-55]()

### Mock Characteristics

Mocks should:
1. **Replicate real behavior** - Update database state as real components would
2. **Execute quickly** - Use short delays (50-100ms) instead of real execution times
3. **Return realistic data** - Provide valid response structures
4. **Maintain side effects** - Preserve database updates and other state changes

---

## Test Helpers and Utilities

### Common Test Helper Functions

Integration tests use shared helper functions for common operations:

```mermaid
graph TB
    subgraph "Test Helper Functions"
        Create["createTestSource()<br/>createTestDocument()<br/>createTestChunks()<br/>createTestBuildTask()"]
        Wait["waitForCondition()"]
        Cleanup["cleanupTestData()<br/>cleanupTestSource()"]
    end
    
    subgraph "Test Lifecycle"
        Setup["beforeAll()"]
        Test["test()"]
        Teardown["afterAll()"]
    end
    
    Setup --> Create
    Test --> Wait
    Teardown --> Cleanup
```

### Helper Function Patterns

#### Resource Creation

```typescript
async function createTestSource(
  db: Database, 
  name?: string
): Promise<number> {
  const result = await db.insert(sources).values({
    name: name || `test_${Date.now()}`,
    baseUrl: 'https://test.com',
    domain: 'test.com',
    // ...
  }).returning({ id: sources.id });
  
  return result[0].id;
}
```

#### Async Condition Polling

```typescript
async function waitForCondition(
  condition: () => Promise<boolean>,
  options: { timeout: number; interval: number }
): Promise<boolean> {
  const startTime = Date.now();
  
  while (Date.now() - startTime < options.timeout) {
    if (await condition()) {
      return true;
    }
    await sleep(options.interval);
  }
  
  return false;
}
```

**Usage Example:**

```typescript
// Wait for all tasks to reach completed status
const completed = await waitForCondition(
  async () => {
    const tasks = await db.select()
      .from(recordingTasks)
      .where(eq(recordingTasks.buildTaskId, buildTaskId));
    return tasks.every(t => t.status === 'completed');
  },
  { timeout: 30000, interval: 1000 }
);

expect(completed).toBe(true);
```

**Sources:** [services/action-builder/test/coordinator.integration.it.test.ts:60-67](), [services/action-builder/test/coordinator.integration.it.test.ts:162-172]()

#### Resource Cleanup

```typescript
async function cleanupTestData(
  db: Database, 
  buildTaskIds: number[]
): Promise<void> {
  // Delete recording_tasks (cascade)
  await db.delete(recordingTasks)
    .where(inArray(recordingTasks.buildTaskId, buildTaskIds));
  
  // Delete build_tasks
  await db.delete(buildTasks)
    .where(inArray(buildTasks.id, buildTaskIds));
}
```

---

## Writing New Tests

### Integration Test Template

When writing integration tests for the action-builder service:

```typescript
import { describe, test, expect, beforeAll, afterAll, vi } from 'vitest';
import { getDb } from '@actionbookdev/db';
import type { Database } from '@actionbookdev/db';
import { /* tables */ } from '@actionbookdev/db';

// Mock expensive dependencies
vi.mock('../src/expensive-component', () => ({
  ExpensiveComponent: class MockComponent {
    async execute() {
      // Fast mock implementation
    }
  }
}));

describe('Component Integration Tests', () => {
  let db: Database;
  let testResourceIds: number[] = [];

  beforeAll(async () => {
    db = getDb();
  });

  afterAll(async () => {
    await cleanupTestResources(db, testResourceIds);
  });

  test('IT-XX: should verify integrated behavior', async () => {
    // 1. Create test data
    const testData = await createTestData(db);
    testResourceIds.push(testData.id);
    
    // 2. Execute component under test
    const component = new ComponentUnderTest(db);
    await component.execute(testData);
    
    // 3. Wait for async completion
    const completed = await waitForCondition(
      async () => {
        const status = await checkStatus(db, testData.id);
        return status === 'completed';
      },
      { timeout: 30000, interval: 1000 }
    );
    
    // 4. Verify results
    expect(completed).toBe(true);
    const results = await fetchResults(db, testData.id);
    expect(results).toMatchObject({
      // Expected properties
    });
  }, 60000);
});
```

### Test Isolation Guidelines

1. **Use unique identifiers** - Timestamps or random IDs to avoid conflicts
2. **Clean up resources** - Always delete test data in `afterAll()`
3. **Avoid shared state** - Each test should be independent
4. **Mock external services** - Don't make real API calls or browser launches
5. **Use real database** - Integration tests should use actual PostgreSQL

### Database Test Data Pattern

```typescript
const testRunId = `test-${Date.now()}-${Math.floor(Math.random() * 10000)}`;
const testDomain = `${testRunId}.example.test`;

// Create test data with unique identifiers
const source = await createTestSource(db, testRunId);
const document = await createTestDocument(db, source.id, testDomain);
```

**Sources:** [services/action-builder/test/task-worker/integration/end-to-end.it.test.ts:63-64]()

---

## Test Coverage Areas

### Core Component Tests

| Component | Test Type | Key Scenarios |
|-----------|-----------|---------------|
| `Coordinator` | Integration | Multi-build concurrency, task claiming, heartbeat monitoring |
| `BuildTaskRunner` | Integration | Task generation, polling, retry logic, version publishing |
| `RecordingTaskQueueWorker` | Integration | Task claiming, concurrent execution, stale recovery |
| `TaskExecutor` | Unit + E2E | Task execution, status updates, error handling |
| `TaskGenerator` | Integration | Chunk-to-task conversion, dual-mode prompts |

### Integration Test Matrix

```mermaid
graph TB
    subgraph "Test IT-01: Concurrent Execution"
        BT1["build_task #1<br/>5 recording_tasks"]
        BT2["build_task #2<br/>5 recording_tasks"]
        BT3["build_task #3<br/>5 recording_tasks"]
        Coord["Coordinator<br/>maxConcurrent=2"]
        QW["QueueWorker<br/>concurrency=3"]
    end
    
    subgraph "Test IT-02: Retry Logic"
        Failed["Failed Task<br/>attemptCount=1"]
        Retry["BuildTaskRunner<br/>detects & retries"]
        Success["Task Completed<br/>attemptCount=2"]
    end
    
    subgraph "Test IT-03: Stale Recovery"
        Stale["Stale Task<br/>lastHeartbeat old"]
        Recover["QueueWorker<br/>recoverStaleTasks()"]
        Requeue["Task Pending<br/>attemptCount+1"]
    end
    
    subgraph "Test IT-04: Concurrency Safety"
        W1["Worker #1<br/>concurrency=2"]
        W2["Worker #2<br/>concurrency=2"]
        W3["Worker #3<br/>concurrency=2"]
        Tasks["10 Pending Tasks"]
        Lock["FOR UPDATE<br/>SKIP LOCKED"]
    end
    
    BT1 --> Coord
    BT2 --> Coord
    BT3 --> Coord
    Coord --> QW
    
    Failed --> Retry
    Retry --> Success
    
    Stale --> Recover
    Recover --> Requeue
    
    Tasks --> Lock
    Lock --> W1
    Lock --> W2
    Lock --> W3
```

**Sources:** [services/action-builder/test/coordinator.integration.it.test.ts:100-508]()

---

## Continuous Integration

### Turbo Task Configuration

Tests are integrated into the Turbo build pipeline:

```json
{
  "tasks": {
    "test": {
      "dependsOn": ["^build"]
    }
  }
}
```

This ensures:
1. Dependencies are built before running tests
2. Tests can run in parallel where possible
3. Results are cached based on file changes

**Sources:** [turbo.json:12-14]()

### Running Tests in CI

```bash
# Run all tests with proper dependency ordering
pnpm test

# Run specific test suites
pnpm --filter @actionbookdev/cli test
pnpm --filter @actionbookdev/action-builder test
```

---

## Best Practices

### Do's

✓ **Use descriptive test names** - `test('IT-01: Multi-build concurrent execution')`  
✓ **Mock expensive operations** - Browser launches, LLM calls, network requests  
✓ **Use real database for integration tests** - Validates actual data flow  
✓ **Clean up test data** - Always remove resources in `afterAll()`  
✓ **Set appropriate timeouts** - 30-60s for integration tests  
✓ **Use helper functions** - Reuse common setup/teardown logic  
✓ **Test error conditions** - Verify retry logic, stale recovery, failures  

### Don'ts

✗ **Don't share test data** - Each test should create its own resources  
✗ **Don't skip cleanup** - Leftover data causes future test failures  
✗ **Don't use hard-coded IDs** - Generate unique identifiers per test run  
✗ **Don't test external services** - Mock APIs, LLMs, and cloud services  
✗ **Don't use short timeouts** - Integration tests need time to complete  

**Sources:** [services/action-builder/test/coordinator.integration.it.test.ts:1-509](), [services/action-builder/test/task-worker/integration/end-to-end.it.test.ts:1-223]()